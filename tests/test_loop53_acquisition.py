import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from neurodecodekit.cli import main
from neurodecodekit.datasets.loop53_acquisition import (
    AUTHORIZATION_COMMIT,
    CONTRACT_SHA256,
    DECISION_SHA256,
    EXPECTED_LICENSE,
    EXPECTED_REPO_ID,
    EXPECTED_REVISION,
    AcquisitionFailure,
    AcquisitionRefusal,
    ExecutionEvidence,
    _render_receipts,
    _verify_execution_evidence,
    run_acquisition,
)


THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}
EVIDENCE = ExecutionEvidence(
    implementation_commit="b" * 40,
    implementation_push_ci_run_id=101,
    implementation_pr_ci_run_id=102,
)


def git_blob_sha1(payload):
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def synthetic_fixture():
    payloads = {
        "EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr": b"\xff\xfeV\x00HDR",
        "EEG/EEG/020_DECOMEG_S2_11966_task2.eeg": b"\x80\x81\x00\xff" * 5,
        "EEG/EEG/020_DECOMEG_S2_11966_task2.vmrk": b"\xfe\xfdV\x00MRK",
        "EEG/logs/S20_session2_block2_list1.mat": b"\x89MAT\x00\xff\xfe",
    }
    selected = []
    roles = (
        "brainvision_header",
        "brainvision_signal",
        "brainvision_markers",
        "companion_log",
    )
    lfs_indexes = {1, 3}
    for index, (path, payload) in enumerate(payloads.items()):
        is_lfs = index in lfs_indexes
        selected.append(
            {
                "role": roles[index],
                "repository_path": path,
                "destination_relative_path": path,
                "size_bytes": len(payload),
                "repository_oid_algorithm": (
                    "git_lfs_pointer_sha1" if is_lfs else "git_blob_sha1"
                ),
                "repository_oid": (
                    hashlib.sha1(f"pointer-{index}".encode()).hexdigest()
                    if is_lfs
                    else git_blob_sha1(payload)
                ),
                "lfs_sha256": hashlib.sha256(payload).hexdigest() if is_lfs else None,
                "xet_hash": hashlib.sha256(f"xet-{index}".encode()).hexdigest()
                if is_lfs
                else None,
                "content_parse_allowed": False,
            }
        )
    total = sum(len(payload) for payload in payloads.values())
    contract = {
        "source_repository": {
            "repo_id": EXPECTED_REPO_ID,
            "revision": EXPECTED_REVISION,
            "license_id": EXPECTED_LICENSE,
        },
        "selected_files": selected,
        "storage_and_output": {
            "payload_root": "data/loop53_s20_eeg/SpanishBCBL",
            "temporary_root": ".codex_work/loop53_s20_eeg_acquisition/tmp",
            "receipt_root": ".codex_work/loop53_s20_eeg_acquisition/receipt",
            "expected_final_payload_bytes": total,
            "maximum_network_payload_bytes": total + 1024,
            "maximum_incremental_disk_bytes_including_temporary_files": 4 * 1024 * 1024,
            "minimum_free_disk_bytes_before_execution": 1,
            "maximum_generated_receipt_bytes": 1024 * 1024,
        },
        "resource_caps": {
            "cpu_threads": 1,
            "workers": 1,
            "wall_time_seconds": 600,
            "peak_rss_bytes": 512 * 1024 * 1024,
        },
        "receipt_contract": {
            "machine_manifest": "acquisition_manifest.json",
            "human_receipt": "acquisition_receipt.md",
        },
    }
    revision = {
        "sha": EXPECTED_REVISION,
        "private": False,
        "gated": False,
        "disabled": False,
        "cardData": {"license": EXPECTED_LICENSE},
        "tags": [f"license:{EXPECTED_LICENSE}"],
    }
    path_rows = []
    for row in selected:
        path_row = {
            "type": "file",
            "path": row["repository_path"],
            "size": row["size_bytes"],
            "oid": row["repository_oid"],
            "xetHash": row["xet_hash"],
        }
        if row["lfs_sha256"]:
            path_row["lfs"] = {
                "oid": row["lfs_sha256"],
                "size": row["size_bytes"],
                "pointerSize": 128,
            }
        path_rows.append(path_row)
    return contract, payloads, revision, path_rows


class FakeTransport:
    def __init__(self, payloads, revision, path_rows):
        self.payloads = dict(payloads)
        self.revision = copy.deepcopy(revision)
        self.path_rows = copy.deepcopy(path_rows)
        self.payload_calls = []

    def fetch_revision(self, repo_id, revision):
        self.assert_identity(repo_id, revision)
        return copy.deepcopy(self.revision), 137

    def fetch_paths(self, repo_id, revision, paths):
        self.assert_identity(repo_id, revision)
        if list(paths) != list(self.payloads):
            raise AssertionError("runner changed registered path order")
        return copy.deepcopy(self.path_rows), 401

    def open_payload(self, url, expected_size):
        marker = f"/resolve/{EXPECTED_REVISION}/"
        path = url.split(marker, 1)[1].split("?", 1)[0]
        self.payload_calls.append(path)
        payload = self.payloads[path]
        if len(payload) != expected_size:
            raise AssertionError("fake expected-size binding drifted")
        return io.BytesIO(payload)

    def assert_identity(self, repo_id, revision):
        if repo_id != EXPECTED_REPO_ID or revision != EXPECTED_REVISION:
            raise AssertionError("runner changed frozen source identity")


class Loop53AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.contract, self.payloads, self.revision, self.path_rows = synthetic_fixture()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_fixture(self, transport=None, contract=None, environ=None):
        transport = transport or FakeTransport(self.payloads, self.revision, self.path_rows)
        outcome = run_acquisition(
            contract=contract or self.contract,
            contract_sha256="1" * 64,
            decision_sha256="2" * 64,
            evidence=EVIDENCE,
            workspace_root=self.root,
            revision_fetcher=transport.fetch_revision,
            paths_fetcher=transport.fetch_paths,
            payload_opener=transport.open_payload,
            environ=environ or THREAD_ENV,
            clock=lambda: 100.0,
            utc_now=lambda: "2026-07-17T12:00:00Z",
            rss_reader=lambda: 16 * 1024 * 1024,
        )
        return outcome, transport

    def test_tiny_opaque_roundtrip_passes_without_decoding_invalid_utf8(self):
        outcome, transport = self.run_fixture()
        self.assertTrue(outcome.passed)
        self.assertEqual(outcome.status, "passed")
        self.assertEqual(transport.payload_calls, list(self.payloads))
        final_root = self.root / "data/loop53_s20_eeg/SpanishBCBL"
        for path, payload in self.payloads.items():
            self.assertEqual((final_root / path).read_bytes(), payload)
        self.assertFalse((self.root / ".codex_work/loop53_s20_eeg_acquisition/tmp").exists())
        self.assertTrue(outcome.manifest_path.is_file())
        self.assertTrue(outcome.receipt_path.is_file())

    def test_manifest_has_hashes_metrics_zero_forbidden_counters_and_claim_ceiling(self):
        outcome, _ = self.run_fixture()
        manifest = json.loads(outcome.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["file_paths_sizes_source_oids_and_content_sha256"]), 4)
        self.assertTrue(
            all(
                len(row["content_sha256"]) == 64
                for row in manifest["file_paths_sizes_source_oids_and_content_sha256"]
            )
        )
        counters = manifest["access_counters"]
        self.assertEqual(counters["metadata_calls"], 2)
        self.assertEqual(counters["payload_download_invocations"], 1)
        self.assertEqual(counters["payload_file_requests"], 4)
        self.assertEqual(counters["opaque_hash_reads"], 4)
        for key in (
            "header_reads",
            "marker_reads",
            "signal_reads",
            "mat_reads",
            "target_or_label_reads",
            "cache_reads_or_writes",
            "split_operations",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "scoring_runs",
        ):
            self.assertEqual(counters[key], 0, key)
        self.assertEqual(set(manifest["unavailable_fields"]), {
            "channel_count",
            "channel_names",
            "sampling_rate_hz",
            "reference_scheme",
            "sensor_geometry",
            "event_count",
            "trial_count",
            "target_text",
            "signal_quality",
            "neural_advantage",
            "decoding_accuracy",
            "end_to_end_latency",
        })
        self.assertIn("establishes no BrainVision readability", manifest["claim_boundary"]["scientific_claim_not_established"])
        self.assertTrue(all(manifest["acceptance_gate_results"].values()))
        generated = outcome.manifest_path.stat().st_size + outcome.receipt_path.stat().st_size
        self.assertEqual(manifest["measurements"]["generated_receipt_bytes"], generated)
        self.assertLessEqual(generated, 1024 * 1024)
        self.assertGreaterEqual(
            manifest["measurements"]["incremental_disk_peak_bytes"], generated
        )

    def test_metadata_mismatch_parks_before_any_payload_request(self):
        revision = copy.deepcopy(self.revision)
        revision["sha"] = "0" * 40
        transport = FakeTransport(self.payloads, revision, self.path_rows)
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.status, "parked")
        self.assertEqual(outcome.manifest["failure_stage"], "metadata")
        self.assertEqual(transport.payload_calls, [])
        self.assertEqual(outcome.manifest["access_counters"]["payload_download_invocations"], 0)
        self.assertFalse((self.root / "data/loop53_s20_eeg").exists())
        self.assertFalse((self.root / ".codex_work/loop53_s20_eeg_acquisition/tmp").exists())

    def test_paths_info_duplicate_or_identity_drift_parks_before_payload(self):
        rows = copy.deepcopy(self.path_rows)
        rows[1] = copy.deepcopy(rows[0])
        transport = FakeTransport(self.payloads, self.revision, rows)
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.status, "parked")
        self.assertEqual(outcome.manifest["failure_stage"], "metadata")
        self.assertEqual(transport.payload_calls, [])

    def test_payload_integrity_mismatch_cleans_only_invocation_temp_and_does_not_promote(self):
        changed = dict(self.payloads)
        signal_path = "EEG/EEG/020_DECOMEG_S2_11966_task2.eeg"
        changed[signal_path] = b"\x00" * len(changed[signal_path])
        transport = FakeTransport(changed, self.revision, self.path_rows)
        outcome, _ = self.run_fixture(transport)
        self.assertEqual(outcome.status, "parked")
        self.assertEqual(outcome.manifest["failure_stage"], "integrity")
        self.assertFalse((self.root / "data/loop53_s20_eeg").exists())
        self.assertFalse((self.root / ".codex_work/loop53_s20_eeg_acquisition/tmp").exists())
        self.assertTrue(outcome.manifest_path.exists())

    def test_network_cap_is_enforced_during_transfer(self):
        contract = copy.deepcopy(self.contract)
        contract["storage_and_output"]["maximum_network_payload_bytes"] = 8
        outcome, _ = self.run_fixture(contract=contract)
        self.assertEqual(outcome.status, "parked")
        self.assertEqual(outcome.manifest["failure_stage"], "resource")
        self.assertIn("network payload cap", outcome.manifest["failure_reason"])
        self.assertFalse((self.root / "data/loop53_s20_eeg").exists())

    def test_receipt_output_cap_is_strict(self):
        manifest = {
            "status": "parked",
            "source_revision": EXPECTED_REVISION,
            "license_id": EXPECTED_LICENSE,
            "failure_stage": "test",
            "measurements": {
                "final_file_count": 0,
                "final_payload_bytes": 0,
                "network_payload_bytes": 0,
                "runtime_seconds": 0,
                "peak_rss_bytes": 1,
                "incremental_disk_peak_bytes": 0,
                "generated_receipt_bytes": 0,
            },
            "warnings": ["bounded"],
            "claim_boundary": {
                "engineering_result": "parked",
                "scientific_claim_not_established": "none established",
            },
        }
        with self.assertRaisesRegex(AcquisitionFailure, "output cap"):
            _render_receipts(manifest, 64)

    def test_preexisting_destination_is_never_deleted_or_overwritten(self):
        marker_root = self.root / "data/loop53_s20_eeg"
        marker_root.mkdir()
        marker = marker_root / "user-owned.txt"
        marker.write_text("keep", encoding="utf-8")
        transport = FakeTransport(self.payloads, self.revision, self.path_rows)
        with self.assertRaisesRegex(AcquisitionRefusal, "must not already exist"):
            self.run_fixture(transport)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
        self.assertEqual(transport.payload_calls, [])

    def test_symlink_component_is_refused_without_following(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".codex_work").symlink_to(outside, target_is_directory=True)
        transport = FakeTransport(self.payloads, self.revision, self.path_rows)
        with self.assertRaisesRegex(AcquisitionRefusal, "symlink"):
            self.run_fixture(transport)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(transport.payload_calls, [])

    def test_one_thread_environment_is_mandatory(self):
        environ = dict(THREAD_ENV)
        environ["OPENBLAS_NUM_THREADS"] = "4"
        transport = FakeTransport(self.payloads, self.revision, self.path_rows)
        with self.assertRaisesRegex(AcquisitionRefusal, "one-thread"):
            self.run_fixture(transport, environ=environ)
        self.assertEqual(transport.payload_calls, [])

    def test_second_invocation_is_refused_by_existing_isolated_roots(self):
        first, _ = self.run_fixture()
        self.assertTrue(first.passed)
        second_transport = FakeTransport(self.payloads, self.revision, self.path_rows)
        with self.assertRaises(AcquisitionRefusal):
            self.run_fixture(second_transport)
        self.assertEqual(second_transport.payload_calls, [])

    def test_registered_hash_and_authorization_bindings_are_fixed(self):
        self.assertEqual(
            CONTRACT_SHA256,
            "bc7d86a1ce6ef3dc71dacca0af97cb5813df87620ac35d4f34ecd343f97e65ac",
        )
        self.assertEqual(
            DECISION_SHA256,
            "f5e75bb9f9315ced6f45812f3841973abedbef3c8a0890fa78737a7b5b478107",
        )
        self.assertEqual(AUTHORIZATION_COMMIT, "2a47bbc75eac0118c3f9de87363d7da02584d2fc")

    def test_execution_evidence_requires_current_clean_descendant_head(self):
        responses = [
            SimpleNamespace(returncode=0, stdout=f"{'b' * 40}\n"),
            SimpleNamespace(returncode=0, stdout=""),
            SimpleNamespace(returncode=0, stdout=""),
        ]
        with patch(
            "neurodecodekit.datasets.loop53_acquisition.subprocess.run",
            side_effect=responses,
        ) as run:
            _verify_execution_evidence(self.root, EVIDENCE)
        self.assertEqual(run.call_count, 3)

    def test_execution_evidence_refuses_head_mismatch_or_tracked_changes(self):
        with patch(
            "neurodecodekit.datasets.loop53_acquisition.subprocess.run",
            return_value=SimpleNamespace(returncode=0, stdout=f"{'c' * 40}\n"),
        ):
            with self.assertRaisesRegex(AcquisitionRefusal, "current HEAD"):
                _verify_execution_evidence(self.root, EVIDENCE)
        responses = [
            SimpleNamespace(returncode=0, stdout=f"{'b' * 40}\n"),
            SimpleNamespace(returncode=0, stdout=" M tracked.py\n"),
        ]
        with patch(
            "neurodecodekit.datasets.loop53_acquisition.subprocess.run",
            side_effect=responses,
        ):
            with self.assertRaisesRegex(AcquisitionRefusal, "tracked worktree"):
                _verify_execution_evidence(self.root, EVIDENCE)

    def test_no_heavy_neuro_or_array_dependency_is_imported(self):
        source_path = (
            Path(__file__).resolve().parents[1]
            / "src/neurodecodekit/datasets/loop53_acquisition.py"
        )
        source = source_path.read_text(encoding="utf-8")
        for forbidden in ("import mne", "import numpy", "import scipy", "import torch"):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("read_text", source)

    def test_cli_defaults_to_plan_without_registered_path_stat_or_network(self):
        stdout = io.StringIO()
        with (
            patch(
                "neurodecodekit.datasets.loop53_acquisition._lstat_optional",
                side_effect=AssertionError("dry-run must not stat registered paths"),
            ),
            patch("urllib.request.urlopen", side_effect=AssertionError("dry-run must not network")),
            redirect_stdout(stdout),
        ):
            code = main(["loop53-acquire-s20"])
        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn('"mode": "dry_run_no_path_stat_no_network"', output)
        self.assertIn('"expected_payload_bytes": 96090264', output)
        self.assertIn("No registered path stat or network access occurred", output)

    def test_cli_execute_requires_remote_green_implementation_evidence(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["loop53-acquire-s20", "--execute"])
        self.assertEqual(code, 2)
        self.assertIn("--implementation-commit", stderr.getvalue())
        self.assertIn("--implementation-push-ci-run-id", stderr.getvalue())
        self.assertIn("--implementation-pr-ci-run-id", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
