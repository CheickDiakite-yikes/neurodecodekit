from __future__ import annotations

import hashlib
import inspect
import json
import os
import tempfile
import unittest
from pathlib import Path

from neurodecodekit import dreyer_c5r_1_stage_h_cli as cli
from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / stage_h.CONTRACT_RELATIVE_PATH


def _fake_remote_proof() -> dict[str, object]:
    commit = "a" * 40
    return {
        "branch": "codex/stage-h-generated-test",
        "head_sha": commit,
        "remote_head_sha": commit,
        "CI_run_id": 201,
        "CI_head_sha": commit,
        "CI_conclusion": "success",
        "base_python_job_id": 202,
        "base_python_job_name": "Base Python",
        "base_python_job_conclusion": "success",
        "optional_neuro_readers_job_id": 203,
        "optional_neuro_readers_job_name": "Optional Neuro Readers",
        "optional_neuro_readers_job_conclusion": "success",
    }


class DreyerC5R1StageHContractTests(unittest.TestCase):
    def test_contract_identity_bindings_and_authority_are_exact(self) -> None:
        payload = CONTRACT_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), stage_h.CONTRACT_SHA256)
        contract = json.loads(payload)
        self.assertEqual(contract["lane_id"], "DREYER-C5R-1-H")
        self.assertEqual(contract["parent_lane_id"], "DREYER-C5R-1")
        self.assertEqual(contract["status"], "generated_qualification_only")
        self.assertEqual(
            contract["bindings"]["generated_stage_G_result_commit"],
            "8f102541a9dd968b5f6574697ddbf7377b0a7372",
        )
        self.assertFalse(contract["authority"]["real_HTTP_request"])
        self.assertFalse(contract["authority"]["real_EDF_header_read"])
        self.assertFalse(contract["authority"]["real_annotation_signal_target_model_training_prediction_or_score_access"])

    def test_registered_member_and_sensor_roster_are_exact(self) -> None:
        contract = stage_h.load_contract(ROOT)
        self.assertEqual(stage_h.REGISTERED_SPEC.bytes, 14_805_604)
        self.assertEqual(
            stage_h.REGISTERED_SPEC.sha256,
            "a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185",
        )
        self.assertEqual(len(stage_h.EXPECTED_EEG_LABELS), 27)
        self.assertEqual(
            tuple(contract["sensor_contract"]["expected_EEG_labels"]),
            stage_h.EXPECTED_EEG_LABELS,
        )
        self.assertEqual(contract["preflight"]["url"], stage_h.REGISTERED_SPEC.url)

    def test_preflight_has_no_target_label_model_or_live_network_argument(self) -> None:
        parameters = inspect.signature(stage_h.stream_verified_preflight).parameters
        for forbidden in ("target", "label", "model", "annotation", "url_opener"):
            self.assertNotIn(forbidden, parameters)
        source = inspect.getsource(stage_h)
        self.assertNotIn("urlopen(", source)
        self.assertNotIn("requests.get(", source)

    def test_cli_is_generated_only(self) -> None:
        help_text = cli._parser().format_help()
        for present in ("plan", "qualify", "inspect"):
            self.assertIn(present, help_text)
        for forbidden in ("execute", "download", "acquire", "score", "live"):
            self.assertNotIn(forbidden, help_text.casefold())


class DreyerC5R1StageHStreamingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.body = stage_h._fixture_body(stage_h._valid_labels())
        self.spec = stage_h._fixture_spec(self.body)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_chunked_stream_retains_exact_payload_and_allowlisted_summary(self) -> None:
        destination = self.root / "valid.edf"
        result = stage_h.stream_verified_preflight(
            stage_h.FixtureResponse(
                self.body,
                url=self.spec.url,
                maximum_read_bytes=73,
            ),
            self.spec,
            destination,
        )
        self.assertEqual(destination.read_bytes(), self.body)
        self.assertEqual(result["payload_sha256"], hashlib.sha256(self.body).hexdigest())
        sensor = result["sensor_contract"]
        self.assertEqual(sensor["EEG_channel_count"], 27)
        self.assertEqual(sensor["EOG_labels"], ["EOG-VU", "EOG-VD", "EOG-H"])
        self.assertEqual(sensor["EMG_labels"], ["EMG-LH", "EMG-RH"])
        self.assertEqual(sensor["annotation_channel_count"], 1)
        serialized = json.dumps(result, sort_keys=True)
        for forbidden in (
            "GENERATED-PATIENT",
            "GENERATED-RECORDING",
            "annotation_records",
            "signal_samples",
            "target",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_header_failure_removes_only_invocation_temporary_file(self) -> None:
        protected = self.root / "protected.txt"
        protected.write_bytes(b"unchanged")
        malformed = b"1" + self.body[1:]
        destination = self.root / "refused.edf"
        with self.assertRaises(stage_h.StageHRefusal):
            stage_h.stream_verified_preflight(
                stage_h.FixtureResponse(malformed, url=self.spec.url),
                stage_h.PreflightSpec(
                    self.spec.url,
                    self.spec.relative_path,
                    len(malformed),
                    hashlib.sha256(malformed).hexdigest(),
                ),
                destination,
            )
        self.assertFalse(destination.exists())
        self.assertEqual(protected.read_bytes(), b"unchanged")
        self.assertEqual(list(self.root.glob("*.stage-h.tmp")), [])

    def test_digest_short_long_and_transfer_contract_fail_closed(self) -> None:
        candidates = (
            (
                stage_h.FixtureResponse(self.body, url=self.spec.url),
                stage_h.PreflightSpec(
                    self.spec.url,
                    self.spec.relative_path,
                    self.spec.bytes,
                    "0" * 64,
                ),
            ),
            (
                stage_h.FixtureResponse(
                    self.body[:-1],
                    url=self.spec.url,
                    headers={"Content-Length": str(len(self.body))},
                ),
                self.spec,
            ),
            (
                stage_h.FixtureResponse(
                    self.body + b"x",
                    url=self.spec.url,
                    headers={"Content-Length": str(len(self.body))},
                ),
                self.spec,
            ),
            (
                stage_h.FixtureResponse(
                    self.body,
                    url=self.spec.url,
                    headers={
                        "Content-Length": str(len(self.body)),
                        "Content-Encoding": "gzip",
                    },
                ),
                self.spec,
            ),
        )
        for index, (response, spec) in enumerate(candidates):
            destination = self.root / f"refused-{index}.edf"
            with self.subTest(index=index):
                with self.assertRaises(stage_h.StageHRefusal):
                    stage_h.stream_verified_preflight(response, spec, destination)
                self.assertFalse(destination.exists())

    def test_roster_and_sampling_ambiguity_fail_closed(self) -> None:
        labels = stage_h._valid_labels()
        candidates = (
            stage_h._fixture_body(labels[:-1] + ("MYSTERY",)),
            stage_h._fixture_body(labels, sampling_rate_hz=511),
            stage_h._fixture_body(
                stage_h.EXPECTED_EEG_LABELS
                + ("EOG-1", "EOG-2", "EMG-1", "EMG-2", "EDF Annotations")
            ),
        )
        for index, body in enumerate(candidates):
            spec = stage_h._fixture_spec(body)
            destination = self.root / f"roster-refused-{index}.edf"
            with self.subTest(index=index):
                with self.assertRaises(stage_h.StageHRefusal):
                    stage_h.stream_verified_preflight(
                        stage_h.FixtureResponse(body, url=spec.url), spec, destination
                    )
                self.assertFalse(destination.exists())

    def test_existing_or_symlink_destination_is_never_changed(self) -> None:
        occupied = self.root / "occupied.edf"
        occupied.write_bytes(b"preserve")
        with self.assertRaises(stage_h.StageHRefusal):
            stage_h.stream_verified_preflight(
                stage_h.FixtureResponse(self.body, url=self.spec.url),
                self.spec,
                occupied,
            )
        self.assertEqual(occupied.read_bytes(), b"preserve")

        target = self.root / "target.edf"
        target.write_bytes(b"target")
        link = self.root / "link.edf"
        link.symlink_to(target)
        with self.assertRaises(stage_h.StageHRefusal):
            stage_h.stream_verified_preflight(
                stage_h.FixtureResponse(self.body, url=self.spec.url), self.spec, link
            )
        self.assertEqual(target.read_bytes(), b"target")


class DreyerC5R1StageHGeneratedQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.saved_environment = {
            name: os.environ.get(name) for name in stage_h.parent.THREAD_ENVIRONMENT
        }
        os.environ.update({name: "1" for name in stage_h.parent.THREAD_ENVIRONMENT})
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "stage-h-result.json"
        cls.result = stage_h.run_generated_qualification(
            cls.output,
            root=ROOT,
            remote_proof_collector=lambda _root: _fake_remote_proof(),
            peak_rss_reader=lambda: 80_000_000,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()
        for name, value in cls.saved_environment.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_generated_qualification_exercises_exact_case_families(self) -> None:
        self.assertEqual(
            self.result["status"], "passed_generated_mock_only_no_real_data_or_network"
        )
        cases = self.result["cases"]
        self.assertEqual(cases["valid_cases_passed"], 2)
        self.assertEqual(cases["adversarial_cases_refused"], 18)
        self.assertTrue(cases["deterministic_replay"])
        self.assertIn("digest_mismatch", cases["adversarial_case_names"])
        self.assertIn("wrong_sampling_rate", cases["adversarial_case_names"])
        self.assertIn("no_clobber", cases["adversarial_case_names"])

    def test_result_is_bounded_and_every_real_counter_is_zero(self) -> None:
        measurements = self.result["measurements"]
        self.assertEqual(measurements["public_output_bytes"], self.output.stat().st_size)
        self.assertLessEqual(
            measurements["generated_input_bytes"],
            stage_h.GENERATED_CAPS["generated_input_bytes_maximum"],
        )
        self.assertLessEqual(
            measurements["private_temporary_bytes"],
            stage_h.GENERATED_CAPS["private_temporary_bytes_maximum"],
        )
        self.assertFalse(measurements["producer_causal"])
        self.assertIsNone(measurements["required_context_seconds"])
        self.assertFalse(measurements["end_to_end_latency_measured"])
        counters = self.result["access_counters"]
        self.assertEqual(counters["pre_qualification_Git_remote_metadata_calls"], 1)
        self.assertEqual(counters["pre_qualification_GitHub_Actions_metadata_calls"], 2)
        for key, value in counters.items():
            if key not in {
                "pre_qualification_Git_remote_metadata_calls",
                "pre_qualification_GitHub_Actions_metadata_calls",
            }:
                self.assertEqual(value, 0, key)

    def test_public_result_contains_no_real_sensor_observation(self) -> None:
        serialized = self.output.read_text(encoding="utf-8")
        self.assertIn("real_source_EDF_sensor_roster_remains_unverified", serialized)
        self.assertIn('"real_authority": false', serialized)
        self.assertNotIn("/Users/", serialized)
        self.assertNotIn("GENERATED-PATIENT", serialized)

    def test_no_clobber_refuses_before_remote_proof(self) -> None:
        proof_calls = 0

        def unexpected_proof(_root: str | Path) -> dict[str, object]:
            nonlocal proof_calls
            proof_calls += 1
            raise AssertionError("proof must not run when result already exists")

        with self.assertRaises(stage_h.parent.DreyerExperimentRefusal):
            stage_h.run_generated_qualification(
                self.output,
                root=ROOT,
                remote_proof_collector=unexpected_proof,
            )
        self.assertEqual(proof_calls, 0)

    def test_inspection_is_summary_only(self) -> None:
        summary = stage_h.inspect_generated_result(self.output)
        self.assertEqual(
            summary["status"], "passed_generated_mock_only_no_real_data_or_network"
        )
        self.assertNotIn("implementation_proof", summary)
        self.assertNotIn("planned_real_preflight", summary)

    def test_invalid_RSS_measurement_refuses_without_output(self) -> None:
        for index, value in enumerate(
            (
                stage_h.GENERATED_CAPS["peak_process_tree_RSS_bytes_maximum"] + 1,
                -1,
                True,
            )
        ):
            destination = Path(self.temporary.name) / f"rss-refusal-{index}.json"
            with self.subTest(value=value):
                with self.assertRaises(stage_h.StageHRefusal):
                    stage_h.run_generated_qualification(
                        destination,
                        root=ROOT,
                        remote_proof_collector=lambda _root: _fake_remote_proof(),
                        peak_rss_reader=lambda value=value: value,
                    )
                self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
