import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h
from neurodecodekit.datasets import dreyer_c5r_1_stage_h_l2 as hl2


ROOT = Path(__file__).resolve().parents[1]


def _activation() -> dict:
    return {
        "schema_name": (
            "neurodecodekit.dreyer_c5r_1_stage_h_l2_fixed_header_activation"
        ),
        "schema_version": "0.1.0",
        "activation_id": "DREYER-C5R-1-HL2-ACT0",
        "request_id": hl2.REQUEST_ID,
        "decision_id": hl2.DECISION_ID,
        "decision_commit": hl2.GREEN_DECISION_COMMIT,
        "status": "no_authority_record_effective_only_after_own_remote_green",
        "exact_member": {
            "path": stage_h.PREFLIGHT_PATH,
            "url": stage_h.PREFLIGHT_URL,
            "bytes": stage_h.PREFLIGHT_BYTES,
            "sha256": stage_h.PREFLIGHT_SHA256,
        },
        "ordered_execution_after_remote_green": {
            "registered_invocations_maximum": 1,
            "marker_before_opener_or_request": True,
            "real_HTTP_GET_requests_exact": 1,
            "fixed_header_semantic_parses_maximum": 1,
            "retries": 0,
            "reruns": 0,
        },
        "bound_implementation_artifacts": [],
    }


def _evidence() -> hl2.ActivationEvidence:
    return hl2.ActivationEvidence(
        activation_sha256="0" * 64,
        activation_commit="1" * 40,
        activation_ci_run_id=1,
        activation_base_job_id=1,
        activation_optional_job_id=1,
    )


class DreyerStageHL2FixedHeaderImplementationTests(unittest.TestCase):
    def test_green_decision_and_recovery_artifacts_are_exact(self):
        decision = hl2.load_green_decision(ROOT)
        self.assertEqual(decision["decision_id"], hl2.DECISION_ID)
        self.assertEqual(hl2.GREEN_DECISION_CI_RUN_ID, 33_257_975_186)
        self.assertEqual(hl2.GREEN_DECISION_BASE_JOB_ID, 99_114_895_023)
        self.assertEqual(hl2.GREEN_DECISION_OPTIONAL_JOB_ID, 99_114_895_128)
        hl2.verify_frozen_recovery(ROOT)

    def test_activation_contract_is_strict_and_still_generated_only(self):
        activation = _activation()
        hl2.validate_activation(
            activation,
            _evidence(),
            repo_root=ROOT,
            verify_artifacts=False,
        )
        for key, value in (
            ("activation_id", "wrong"),
            ("decision_commit", "0" * 40),
            ("status", "active_without_green"),
        ):
            changed = {**activation, key: value}
            with self.assertRaises(hl2.HL2Refusal) as caught:
                hl2.validate_activation(
                    changed,
                    _evidence(),
                    repo_root=ROOT,
                    verify_artifacts=False,
                )
            self.assertEqual(caught.exception.code, "HL2-PROOF")

    def test_generated_h1_is_marker_first_deterministic_and_target_free(self):
        reports = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as directory:
                result = hl2.run_generated_case(directory)
                reports.append(result.report)
                self.assertEqual(result.report["route"], "DREYER-H1")
                self.assertEqual(result.events[0:2], ("marker_durable", "transaction_entered"))
                self.assertLess(
                    result.events.index("marker_durable"),
                    result.events.index("opener_constructed"),
                )
                self.assertEqual(result.opener_constructions, 1)
                self.assertEqual(result.requests, 1)
                self.assertTrue(result.response_closed)
                self.assertTrue(result.marker_path.is_file())
                self.assertTrue(result.final_payload_path.is_file())
                inspected = hl2.inspect_public_result(result.output_path)
                self.assertEqual(inspected["sensor_contract"]["EEG_channel_count"], 27)
                self.assertEqual(inspected["sensor_contract"]["EOG_channel_count"], 3)
                self.assertEqual(inspected["sensor_contract"]["EMG_channel_count"], 2)
                counters = inspected["operation_counters"]
                self.assertTrue(all(value == 0 for value in counters.values()))
                self.assertTrue(
                    all(value is False for value in inspected["claim_boundary"].values())
                )
        for key in (
            "route",
            "refusal_code",
            "exact_member",
            "sensor_contract",
            "transport",
            "operation_counters",
            "warnings",
            "claim_boundary",
        ):
            self.assertEqual(reports[0][key], reports[1][key], key)

    def test_preconsumption_refusals_create_no_new_marker_or_request(self):
        cases = (
            "missing_thread_cap",
            "low_free_disk",
            "preexisting_public_result",
            "preexisting_consumed_marker",
            "occupied_staging_name",
            "preexisting_final_payload",
            "consumed_rerun",
            "RSS_cap",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaises(hl2.HL2Refusal):
                    hl2.run_generated_case(root, case=case)
                private = root / hl2.PRIVATE_ROOT_RELATIVE_PATH
                marker = private / hl2.CONSUMED_MARKER_NAME
                if case not in {"preexisting_consumed_marker", "consumed_rerun"}:
                    self.assertFalse(marker.exists())

    def test_postmarker_refusals_publish_H0_and_remove_unaccepted_payload(self):
        cases = (
            "staging_create_refusal",
            "opener_factory_refusal",
            "request_factory_refusal",
            "response_open_refusal",
            "HTTP_status_drift",
            "final_URL_drift",
            "transfer_encoding",
            "duplicate_content_length",
            "content_encoding",
            "short_body",
            "oversized_body",
            "nonbytes_body",
            "wrong_payload_hash",
            "malformed_fixed_header",
            "wrong_sensor_roster",
            "wrong_sampling_rate",
            "header_payload_geometry",
            "runtime_cap",
            "incremental_disk_cap",
            "response_close_failure",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                result = hl2.run_generated_case(directory, case=case)
                self.assertEqual(result.report["route"], "DREYER-H0")
                self.assertIn(result.report["refusal_code"], hl2.REFUSAL_CODES)
                self.assertTrue(result.marker_path.is_file())
                self.assertFalse(result.final_payload_path.exists())
                self.assertFalse(
                    (Path(directory) / hl2.PRIVATE_ROOT_RELATIVE_PATH / hl2.STAGING_DIRECTORY_NAME).exists()
                )
                self.assertTrue(result.response_closed or result.requests == 0)
                self.assertTrue(
                    all(
                        value == 0
                        for value in result.report["operation_counters"].values()
                    )
                )

    def test_no_replace_and_publication_failures_never_retain_accepted_payload(self):
        for case in (
            "promotion_destination_race",
            "publication_destination_race",
            "public_output_cap",
        ):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                if case == "promotion_destination_race":
                    result = hl2.run_generated_case(root, case=case)
                    self.assertEqual(result.report["route"], "DREYER-H0")
                    self.assertEqual(result.final_payload_path.read_bytes(), b"foreign")
                else:
                    with self.assertRaises(hl2.HL2Refusal):
                        hl2.run_generated_case(root, case=case)
                    final = root / hl2.PRIVATE_ROOT_RELATIVE_PATH / hl2.PRIVATE_PAYLOAD_NAME
                    self.assertFalse(final.exists())

    def test_complete_generated_qualification_is_bounded_and_deterministic(self):
        environment = {
            **os.environ,
            "PYTHONPATH": str(ROOT / "src"),
            **{key: "1" for key in hl2.THREAD_ENV_KEYS},
        }
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.dreyer_c5r_1_stage_h_l2_cli",
                "qualify-generated",
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        qualification = json.loads(completed.stdout)
        self.assertEqual(qualification["transaction_case_count"], 32)
        self.assertEqual(qualification["attempt_count"], 33)
        self.assertEqual(qualification["accepted_H1_count"], 2)
        self.assertEqual(qualification["aggregate_H0_count"], 21)
        self.assertEqual(qualification["raised_refusal_count"], 10)
        self.assertEqual(qualification["refusal_observation_count"], 31)
        self.assertEqual(qualification["retained_generated_payload_bytes"], 0)
        self.assertEqual(qualification["network_bytes"], 0)
        self.assertFalse(qualification["scientific_claim_established"])

    def test_plan_and_cli_expose_no_current_execution_authority(self):
        plan = hl2.registered_plan(ROOT)
        self.assertFalse(plan["registered_execution_authority_now"])
        self.assertFalse(plan["real_EDF_access_authority_now"])
        self.assertIsInstance(plan["activation_present"], bool)
        environment = {
            **os.environ,
            "PYTHONPATH": str(ROOT / "src"),
        }
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.dreyer_c5r_1_stage_h_l2_cli",
                "plan",
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["registered_execution_authority_now"])
        refused = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.dreyer_c5r_1_stage_h_l2_cli",
                "execute",
                "--activation-sha256",
                "0" * 64,
                "--activation-commit",
                "1" * 40,
                "--activation-ci-run-id",
                "1",
                "--activation-base-job-id",
                "1",
                "--activation-optional-job-id",
                "1",
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertEqual(json.loads(refused.stdout)["refusal_code"], "HL2-PROOF")


if __name__ == "__main__":
    unittest.main()
