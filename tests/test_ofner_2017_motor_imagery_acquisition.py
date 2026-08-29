import io
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.datasets.ofner_2017_motor_imagery_acquisition import (
    EXPECTED_FILE_COUNT,
    THREAD_ENV_KEYS,
    AcquisitionCaps,
    OfnerAcquisitionRefusal,
    _canonical_json_bytes,
    _generated_fixture,
    acquire_selected_members,
    canonicalize_manifest,
    registered_plan,
    run_generated_qualification,
    select_manifest,
    write_generated_qualification_result,
)
from neurodecodekit.ofner_mi_acquisition_cli import main as ofner_cli_main


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {key: "1" for key in THREAD_ENV_KEYS}


class OfnerMotorImageryAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.policy, self.raw, self.payloads = _generated_fixture(signature_digit="1")
        self.members = select_manifest(self.raw, self.policy)

    def mutated(self, mutator):
        value = json.loads(self.raw)
        mutator(value)
        return _canonical_json_bytes(value)

    def test_registered_plan_is_explicitly_generated_or_dry_run_only(self):
        plan = registered_plan(ROOT)
        self.assertEqual(plan["expected_file_count"], 150)
        self.assertEqual(plan["expected_payload_bytes"], 13_748_417_608)
        self.assertFalse(plan["live_network_client_present"])
        self.assertFalse(plan["real_payload_execution_present"])
        self.assertFalse(plan["header_or_signal_parser_present"])

    def test_signed_url_refresh_does_not_change_canonical_identity(self):
        second_policy, second_raw, _ = _generated_fixture(signature_digit="2")
        self.assertEqual(self.policy, second_policy)
        self.assertNotEqual(self.raw, second_raw)
        self.assertEqual(canonicalize_manifest(self.raw), canonicalize_manifest(second_raw))
        first = select_manifest(self.raw, self.policy)
        second = select_manifest(second_raw, self.policy)
        self.assertEqual(
            [(row.path, row.size_bytes, row.sha256, row.bytes_url) for row in first],
            [(row.path, row.size_bytes, row.sha256, row.bytes_url) for row in second],
        )
        self.assertNotEqual(first[0].signed_url, second[0].signed_url)

    def test_selector_requires_complete_unique_participant_run_matrix(self):
        self.assertEqual(len(self.members), EXPECTED_FILE_COUNT)
        self.assertEqual(
            {(member.participant, member.run) for member in self.members},
            {(subject, run) for subject in range(1, 16) for run in range(1, 11)},
        )
        self.assertEqual(len({member.sha256 for member in self.members}), EXPECTED_FILE_COUNT)
        with self.assertRaises(OfnerAcquisitionRefusal):
            select_manifest(self.mutated(lambda value: value["files"].pop()), self.policy)
        with self.assertRaises(OfnerAcquisitionRefusal):
            select_manifest(
                self.mutated(lambda value: value["files"].append(value["files"][0])),
                self.policy,
            )

    def test_selector_refuses_target_like_fields_before_any_payload(self):
        for field in ("target", "label", "event", "annotation"):
            with self.subTest(field=field), self.assertRaises(OfnerAcquisitionRefusal):
                select_manifest(
                    self.mutated(lambda value, field=field: value["files"][0].update({field: 1})),
                    self.policy,
                )

    def test_selector_refuses_identity_and_transport_drift(self):
        mutations = (
            lambda value: value["files"][0].update(bytes=1),
            lambda value: value["files"][0].update(sha256="0" * 64),
            lambda value: value["files"][0].update(
                bytes_url=value["files"][0]["bytes_url"].replace(
                    "data.nemar.org", "example.invalid"
                )
            ),
            lambda value: value["files"][0].update(
                url=value["files"][0]["url"].replace(
                    "nemar.s3.us-east-2.amazonaws.com", "example.invalid"
                )
            ),
            lambda value: value["files"][0].update(
                url=value["files"][0]["url"] + "&unexpected=1"
            ),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), self.assertRaises(OfnerAcquisitionRefusal):
                select_manifest(self.mutated(mutate), self.policy)

    def test_selector_refuses_duplicate_keys_and_nonfinite_json(self):
        for malformed in (
            b'{"files":[],"files":[]}',
            b'{"files":[],"value":NaN}',
            b"not-json",
            b"\xef\xbb\xbf{}",
        ):
            with self.subTest(payload=malformed), self.assertRaises(OfnerAcquisitionRefusal):
                select_manifest(malformed, self.policy)

    def test_opaque_writer_roundtrip_preserves_every_generated_byte(self):
        by_url = {member.signed_url: self.payloads[member.path] for member in self.members}
        total = sum(map(len, self.payloads.values()))
        with tempfile.TemporaryDirectory() as temporary:
            receipt = acquire_selected_members(
                self.members,
                workspace_root=temporary,
                destination_relative="bundle",
                payload_opener=lambda url, _size: io.BytesIO(by_url[url]),
                caps=AcquisitionCaps(network_bytes=total, incremental_disk_bytes=total),
                environ=THREAD_ENV,
            )
            self.assertEqual(receipt["measurements"]["file_count"], EXPECTED_FILE_COUNT)
            self.assertEqual(receipt["measurements"]["final_payload_bytes"], total)
            for member in self.members:
                self.assertEqual(
                    (Path(temporary) / "bundle" / member.path).read_bytes(),
                    self.payloads[member.path],
                )
            counters = receipt["operation_counters"]
            for key in (
                "GDF_header_reads",
                "event_or_annotation_reads",
                "target_or_label_reads",
                "signal_sample_reads",
                "model_runs",
                "training_runs",
                "prediction_sets",
                "scientific_scores",
            ):
                self.assertEqual(counters[key], 0, key)

    def test_opaque_writer_refuses_corruption_cap_and_existing_output(self):
        member = self.members[0]
        expected = self.payloads[member.path]
        cases = (
            (expected[:-1], len(expected)),
            (expected + b"x", len(expected) + 1),
            (b"x" * len(expected), len(expected)),
            (expected, len(expected) - 1),
        )
        for payload, cap in cases:
            with self.subTest(length=len(payload), cap=cap), tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(OfnerAcquisitionRefusal):
                    acquire_selected_members(
                        (member,),
                        workspace_root=temp,
                        destination_relative="bundle",
                        payload_opener=lambda _url, _size, payload=payload: io.BytesIO(payload),
                        caps=AcquisitionCaps(
                            network_bytes=cap,
                            incremental_disk_bytes=len(payload) + 1,
                        ),
                        environ=THREAD_ENV,
                    )
                self.assertFalse((Path(temp) / "bundle.partial-ofner").exists())
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "bundle").mkdir()
            with self.assertRaises(OfnerAcquisitionRefusal):
                acquire_selected_members(
                    (member,),
                    workspace_root=temp,
                    destination_relative="bundle",
                    payload_opener=lambda _url, _size: io.BytesIO(expected),
                    caps=AcquisitionCaps(
                        network_bytes=len(expected), incremental_disk_bytes=len(expected)
                    ),
                    environ=THREAD_ENV,
                )

    def test_writer_refuses_wrong_thread_environment_and_symlink_escape(self):
        member = self.members[0]
        payload = self.payloads[member.path]
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(OfnerAcquisitionRefusal):
                acquire_selected_members(
                    (member,),
                    workspace_root=temp,
                    destination_relative="bundle",
                    payload_opener=lambda _url, _size: io.BytesIO(payload),
                    caps=AcquisitionCaps(
                        network_bytes=len(payload), incremental_disk_bytes=len(payload)
                    ),
                    environ={**THREAD_ENV, "OMP_NUM_THREADS": "2"},
                )
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            (Path(temp) / "escape").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(OfnerAcquisitionRefusal):
                acquire_selected_members(
                    (member,),
                    workspace_root=temp,
                    destination_relative="escape/bundle",
                    payload_opener=lambda _url, _size: io.BytesIO(payload),
                    caps=AcquisitionCaps(
                        network_bytes=len(payload), incremental_disk_bytes=len(payload)
                    ),
                    environ=THREAD_ENV,
                )

    def test_generated_qualification_replays_and_refusal_matrix_pass(self):
        result = run_generated_qualification(ROOT)
        self.assertEqual(result["status"], "accepted_generated_only")
        self.assertEqual(result["measurements"]["manifest_replays"], 2)
        self.assertEqual(result["measurements"]["acquisition_replays"], 2)
        self.assertEqual(result["measurements"]["selected_files_per_replay"], 150)
        self.assertEqual(result["measurements"]["adversarial_refusals"], 20)
        self.assertEqual(result["measurements"]["network_bytes"], 0)
        self.assertTrue(all(result["determinism"].values()))
        self.assertFalse(result["capabilities"]["live_network_client_present"])
        self.assertFalse(result["capabilities"]["real_payload_execution_present"])
        self.assertTrue(all(value == 0 for value in result["operation_counters"].values()))

    def test_committed_generated_result_binds_exact_implementation(self):
        result_path = (
            ROOT
            / "registries/ofner_2017_motor_imagery_acquisition_generated_qualification.v0.json"
        )
        result = json.loads(result_path.read_text(encoding="utf-8"))
        artifact = result["implementation_artifact"]
        observed = hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest()
        self.assertEqual(observed, artifact["sha256"])
        self.assertEqual(result["status"], "accepted_generated_only")
        self.assertEqual(result["measurements"]["adversarial_refusals"], 20)
        self.assertEqual(result["measurements"]["network_bytes"], 0)
        self.assertEqual(result["measurements"]["retained_generated_payload_bytes"], 0)
        self.assertFalse(result["capabilities"]["live_network_client_present"])
        self.assertFalse(result["capabilities"]["real_payload_execution_present"])

    def test_result_writer_is_non_replacing_and_bounded(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            result = write_generated_qualification_result(ROOT, output)
            self.assertEqual(json.loads(output.read_text()), result)
            self.assertLess(output.stat().st_size, 1024 * 1024)
            with self.assertRaises(OfnerAcquisitionRefusal):
                write_generated_qualification_result(ROOT, output)

    def test_cli_has_no_real_execute_mode(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = ofner_cli_main(["plan", "--repo-root", str(ROOT)])
        self.assertEqual(code, 0)
        value = stdout.getvalue()
        self.assertIn('"live_network_client_present": false', value)
        self.assertIn("no network, real payload, header", value)
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit):
            ofner_cli_main(["execute"])
        self.assertIn("invalid choice: 'execute'", stderr.getvalue())

    def test_cli_generated_qualification_writes_one_new_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "qualification.json"
            with redirect_stdout(io.StringIO()):
                code = ofner_cli_main(
                    [
                        "qualify-generated",
                        "--repo-root",
                        str(ROOT),
                        "--out",
                        str(output),
                    ]
                )
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.read_text())["status"], "accepted_generated_only")


if __name__ == "__main__":
    unittest.main()
