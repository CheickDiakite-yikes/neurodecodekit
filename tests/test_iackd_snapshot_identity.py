import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import iackd_snapshot_identity as identity


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


def _response_object(payload: bytes) -> dict:
    return json.loads(payload.decode("utf-8"))


def _payload(value: dict) -> bytes:
    return identity._canonical_json_bytes(value)


class IACKDSnapshotIdentityCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = identity.load_registered_contract(ROOT)
        cls.payload = identity.make_generated_response(cls.contract)

    def canonicalize(self, payload: bytes | None = None):
        return identity.canonicalize_generated_response(
            self.payload if payload is None else payload,
            contract=self.contract,
        )

    def test_registered_contract_and_green_proof_are_exact(self) -> None:
        self.assertEqual(
            self.contract["contract_id"],
            "IACKD-M1-snapshot-identity-contract-v0",
        )
        self.assertEqual(
            identity.CONTRACT_SHA256,
            "fa7bed69bb70022b3e61c6839b01a2fa7f3e4f77a40629dc62ab9b4873681e2a",
        )
        self.assertEqual(identity.GREEN_CONTRACT_COMMIT, "1667e302e262ad23695f204a88d5a0997ac38270")
        self.assertEqual(identity.GREEN_CONTRACT_CI_RUN_ID, 31481270697)
        self.assertEqual(identity.GREEN_CONTRACT_BASE_JOB_ID, 93746523491)
        self.assertEqual(identity.GREEN_CONTRACT_OPTIONAL_JOB_ID, 93746523322)

    def test_generated_fixture_matches_every_registered_aggregate(self) -> None:
        result = self.canonicalize()
        self.assertLessEqual(len(self.payload), identity.MAX_RESPONSE_BYTES)
        self.assertEqual(result.report["tree_summary"]["file_count"], 1679)
        self.assertEqual(result.report["tree_summary"]["total_bytes"], 7966799433)
        self.assertEqual(result.report["selected_summary"]["object_count"], 1340)
        self.assertEqual(result.report["selected_summary"]["payload_bytes"], 7249113684)
        self.assertEqual(result.report["selected_summary"]["participant_count"], 15)
        self.assertEqual(result.report["selected_summary"]["participant_hand_units"], 30)
        self.assertEqual(result.report["selected_summary"]["bids_run_count"], 128)
        self.assertEqual(
            result.report["selected_summary"]["role_summaries"],
            self.contract["selected_inventory_contract"]["role_summaries"],
        )

    def test_generated_selected_paths_equal_historical_inventory(self) -> None:
        historical = json.loads(
            (ROOT / "registries" / "iackd_openneuro_metadata_inventory.v0.json").read_text(
                encoding="utf-8"
            )
        )
        expected = {row["path"] for row in historical["selected_objects"]}
        generated = {
            path
            for path, _role, _size in identity._generated_selected_specs(self.contract)
        }
        self.assertEqual(generated, expected)

    def test_source_has_no_network_or_real_execution_surface(self) -> None:
        source = Path(identity.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "urllib.request",
            "requests.",
            "http.client",
            "socket.",
            'add_argument("--execute"',
            "iackd_role_aware_dual_reversal_stream_failure",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_canonical_replay_is_order_independent_and_byte_identical(self) -> None:
        left = self.canonicalize()
        changed = _response_object(self.payload)
        changed["data"]["snapshot"]["files"].reverse()
        right = self.canonicalize(_payload(changed))
        self.assertEqual(
            identity._canonical_json_bytes(left.private_manifest),
            identity._canonical_json_bytes(right.private_manifest),
        )
        self.assertEqual(
            left.report["tree_summary"]["canonical_sha256"],
            right.report["tree_summary"]["canonical_sha256"],
        )
        self.assertEqual(
            left.report["selected_summary"]["canonical_manifest_sha256"],
            right.report["selected_summary"]["canonical_manifest_sha256"],
        )

    def test_strict_json_rejects_duplicate_nonfinite_and_overflowed_numbers(self) -> None:
        cases = (
            b'{"data":{},"data":{}}',
            b'{"data":NaN}',
            b'{"data":1e400}',
            b"\xef\xbb\xbf{}",
            b'{"data":"\x00"}',
            b"\xff",
        )
        for payload in cases:
            with self.subTest(payload=payload):
                with self.assertRaises(identity.SnapshotIdentityRefusal):
                    self.canonicalize(payload)

    def test_anchor_description_path_size_and_url_mutations_refuse(self) -> None:
        mutations = []

        def mutate(path, value):
            candidate = _response_object(self.payload)
            target = candidate
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            mutations.append(_payload(candidate))

        snapshot = _response_object(self.payload)["data"]["snapshot"]
        first = snapshot["files"][0]
        mutate(("data", "snapshot", "id"), "ds000000:1.0.0")
        mutate(("data", "snapshot", "description", "License"), "unknown")
        mutate(("data", "snapshot", "files", 0, "filename"), "../escape")
        mutate(("data", "snapshot", "files", 0, "size"), 1.5)
        mutate(("data", "snapshot", "files", 0, "directory"), True)
        mutate(("data", "snapshot", "files", 0, "urls"), [])
        mutate(
            ("data", "snapshot", "files", 0, "urls"),
            [first["urls"][0] + "&other=1"],
        )
        for payload in mutations:
            with self.subTest(payload=identity._sha256_bytes(payload)):
                with self.assertRaises(identity.SnapshotIdentityRefusal):
                    self.canonicalize(payload)

    def test_all_registered_refusal_mutations_fail_closed(self) -> None:
        refusals = identity._run_required_mutations(self.payload, self.contract)
        self.assertEqual(tuple(refusals), identity.REQUIRED_MUTATIONS)
        self.assertEqual(len(refusals), 37)
        self.assertTrue(all(value in identity.REFUSAL_IDS for value in refusals.values()))

    def test_generated_body_reader_is_one_use(self) -> None:
        reader = identity.GeneratedBodyReader(self.payload)
        self.assertEqual(reader.read_once(identity.MAX_RESPONSE_BYTES + 1), self.payload)
        with self.assertRaises(identity.SnapshotIdentityRefusal):
            reader.read_once(identity.MAX_RESPONSE_BYTES + 1)

    def test_public_report_is_aggregate_and_private_manifest_is_separate(self) -> None:
        result = self.canonicalize()
        serialized = identity._canonical_json_bytes(result.report).decode("utf-8")
        self.assertNotIn("s3.amazonaws.com", serialized)
        self.assertNotRegex(serialized, r"sub-[0-9]{2}/")
        self.assertTrue(all(value == 0 for value in result.report["access_counters"].values()))
        self.assertEqual(len(result.private_manifest["rows"]), 1340)
        self.assertEqual(
            set(result.private_manifest["rows"][0]),
            {
                "filename",
                "git_object_id",
                "size_bytes",
                "annexed",
                "s3_key",
                "s3_version_id",
                "role",
            },
        )


class IACKDSnapshotIdentityQualificationTests(unittest.TestCase):
    @staticmethod
    def run_qualification(output_dir: Path):
        with (
            mock.patch.dict(os.environ, THREAD_ENV, clear=False),
            mock.patch.object(identity.time, "perf_counter", side_effect=(10.0, 10.25)),
            mock.patch.object(identity, "_peak_rss_bytes", return_value=32 * 1024 * 1024),
        ):
            return identity.qualify_generated_snapshot_identity(output_dir)

    def test_bounded_roundtrip_and_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            outcome = self.run_qualification(output)
            inspected = identity.inspect_snapshot_identity_report(outcome.report_path)
            self.assertEqual(inspected, outcome.report)
            self.assertEqual(outcome.runtime_seconds, 0.25)
            self.assertEqual(outcome.peak_rss_bytes, 32 * 1024 * 1024)
            self.assertEqual(outcome.input_bytes, 531067)
            self.assertLessEqual(outcome.generated_output_bytes, identity.MAX_OUTPUT_BYTES)
            self.assertEqual(outcome.report["measurements"]["deterministic_replays"], 2)
            self.assertEqual(outcome.report["measurements"]["refusal_mutations_passed"], 37)
            self.assertTrue(all(outcome.report["acceptance_gates"].values()))
            self.assertTrue(outcome.private_manifest_path.is_file())

    def test_fixed_monitors_produce_byte_identical_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = self.run_qualification(Path(directory) / "first")
            second = self.run_qualification(Path(directory) / "second")
            self.assertEqual(first.report_path.read_bytes(), second.report_path.read_bytes())
            self.assertEqual(
                first.private_manifest_path.read_bytes(),
                second.private_manifest_path.read_bytes(),
            )

    def test_thread_runtime_rss_output_cap_and_collision_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            with mock.patch.dict(os.environ, {**THREAD_ENV, "OMP_NUM_THREADS": "2"}, clear=False):
                with self.assertRaises(identity.SnapshotIdentityRefusal):
                    identity.qualify_generated_snapshot_identity(output)

            with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
                with self.assertRaises(identity.SnapshotIdentityRefusal):
                    identity._enforce_resources(identity.MAX_RUNTIME_SECONDS + 1, 1)
                with self.assertRaises(identity.SnapshotIdentityRefusal):
                    identity._enforce_resources(0, identity.MAX_PEAK_RSS_BYTES + 1)
                with self.assertRaises(identity.SnapshotIdentityRefusal):
                    identity._bounded_output_bytes(b"x" * (identity.MAX_OUTPUT_BYTES + 1), b"")

            self.run_qualification(output)
            with self.assertRaises(identity.SnapshotIdentityRefusal):
                self.run_qualification(output)

    def test_output_parent_and_report_symlinks_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real_parent = root / "real"
            real_parent.mkdir()
            parent_link = root / "parent-link"
            parent_link.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaises(identity.SnapshotIdentityRefusal):
                self.run_qualification(parent_link / "qualification")

            outcome = self.run_qualification(root / "qualification")
            report_link = root / "report-link.json"
            report_link.symlink_to(outcome.report_path)
            with self.assertRaises(identity.SnapshotIdentityRefusal):
                identity.inspect_snapshot_identity_report(report_link)

    def test_cli_help_qualify_and_inspect(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(identity.main([]), 0)
        self.assertIn("Generated-only", stdout.getvalue())

        with self.assertRaises(SystemExit) as help_exit:
            with contextlib.redirect_stdout(io.StringIO()):
                identity.main(["--help"])
        self.assertEqual(help_exit.exception.code, 0)

        with tempfile.TemporaryDirectory() as directory:
            outcome = self.run_qualification(Path(directory) / "qualification")
            with contextlib.redirect_stdout(io.StringIO()) as inspected:
                self.assertEqual(identity.main(["inspect", str(outcome.report_path)]), 0)
            self.assertIn('"selected_object_count": 1340', inspected.getvalue())

    def test_public_report_mutations_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.run_qualification(Path(directory) / "qualification")
            for mutation in (
                lambda value: value.update({"unknown": True}),
                lambda value: value["access_counters"].update({"signal_sample_reads": 1}),
                lambda value: value["tree_summary"].update({"path": "sub-01/eeg/private"}),
                lambda value: value["acceptance_gates"].update({"resource_caps": False}),
                lambda value: value["measurements"].update({"runtime_seconds": None}),
            ):
                with self.subTest(mutation=mutation):
                    candidate = copy.deepcopy(outcome.report)
                    mutation(candidate)
                    with self.assertRaises(identity.SnapshotIdentityRefusal):
                        identity.validate_public_report(candidate)


if __name__ == "__main__":
    unittest.main()
