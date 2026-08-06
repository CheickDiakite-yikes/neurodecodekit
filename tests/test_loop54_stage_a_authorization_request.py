import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop54_stage_a_vhdr_contract.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop54_stage_a_authorization_request.v0.json"
PACKET_PATH = REPO_ROOT / "docs" / "LOOP_54_STAGE_A_AUTHORIZATION_PACKET.md"
PREREG_PATH = REPO_ROOT / "docs" / "LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md"
INVARIANT_TEST_PATH = REPO_ROOT / "tests" / "test_loop54_stage_a_vhdr_contract.py"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


class Loop54StageAAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_identity_is_awaiting_exact_decision(self):
        request = self.request
        self.assertEqual(
            request["schema_name"],
            "neurodecodekit.loop54_stage_a_authorization_request",
        )
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["loop_id"], 54)
        self.assertEqual(request["stage_id"], "L54-A")
        self.assertIn("awaiting_exact_user_authorization", request["status"])
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])

    def test_registration_commit_local_evidence_and_remote_incident_are_explicit(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "c1146233a6178ca5e1153b92565915abad029719",
        )
        self.assertTrue(registration["commit_pushed"])
        self.assertEqual(registration["remote_ci_run_id"], 31127199848)
        self.assertEqual(registration["remote_ci_event"], "workflow_dispatch")
        self.assertIn("github_actions_incident", registration["remote_ci_status"])
        self.assertEqual(
            registration["remote_ci_conclusion"],
            "infrastructure_failure_zero_steps_started",
        )
        self.assertEqual(registration["local_complete_tests"], 1095)
        self.assertEqual(registration["local_complete_expected_skips"], 3)
        self.assertEqual(registration["focused_loop54_tests"], 20)
        self.assertTrue(registration["ruff_passed"])
        self.assertTrue(registration["compileall_passed"])
        verification = self.request["request_local_verification"]
        self.assertEqual(verification["complete_tests"], 1103)
        self.assertEqual(verification["complete_expected_skips"], 3)
        self.assertEqual(verification["focused_contract_request_roadmap_tests"], 39)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])

    def test_registration_artifact_hashes_are_exact(self):
        target = self.request["target"]
        for prefix, path in (
            ("contract", CONTRACT_PATH),
            ("preregistration", PREREG_PATH),
            ("invariant_test", INVARIANT_TEST_PATH),
        ):
            with self.subTest(path=path.name):
                self.assertEqual(target[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(target[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))
        self.assertEqual(target["contract_schema_version"], "0.1.0")
        self.assertTrue(target["registration_snapshot_must_remain_immutable"])

    def test_exact_sentence_appears_once_and_has_not_been_received(self):
        authorization = self.request["authorization"]
        sentence = authorization["exact_authorization_sentence"]
        self.assertEqual(self.packet.count(sentence), 1)
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])
        self.assertFalse(authorization["general_tier_a_b_autonomy_is_tier_c_authorization"])
        self.assertFalse(authorization["loop53_acquisition_authorization_is_loop54_authorization"])
        self.assertFalse(authorization["storage_allowance_is_content_access_authorization"])
        self.assertFalse(authorization["competitive_urgency_is_authorization"])
        actionability = self.request["actionability"]
        self.assertFalse(actionability["request_is_actionable_now"])
        self.assertFalse(actionability["draft_sentence_may_be_treated_as_user_authorization_now"])
        self.assertIn("remote_green_ci", actionability["blocking_condition"])

    def test_requested_scope_and_resources_match_contract(self):
        request = self.request
        scope = request["requested_scope"]
        registered = self.contract["registered_input"]
        self.assertEqual(scope["registered_real_executions"], 1)
        self.assertEqual(scope["registered_vhdr_content_opens"], 1)
        self.assertEqual(scope["registered_input_relative_path"], registered["vhdr_relative_path"])
        self.assertEqual(scope["registered_input_size_bytes"], registered["expected_size_bytes"])
        self.assertEqual(scope["registered_input_git_blob_sha1"], registered["source_identity"])
        self.assertTrue(scope["strict_allowlisted_parse"])
        resources = request["resource_caps"]
        contract_resources = self.contract["resource_caps"]
        for key in resources:
            self.assertEqual(resources[key], contract_resources[key], key)

    def test_all_forbidden_requested_and_current_counters_are_zero(self):
        scope = self.request["requested_scope"]
        for key in (
            "vmrk_stats_or_reads",
            "eeg_stats_or_signal_reads",
            "mat_stats_or_reads",
            "target_or_label_reads",
            "cache_or_split_operations",
            "model_or_checkpoint_loads",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "scoring_or_selection_runs",
            "network_or_download_operations",
            "language_model_runs",
            "rw3_stream_device_or_hardware_operations",
            "release_operations",
            "reruns",
        ):
            self.assertEqual(scope[key], 0, key)
        self.assertTrue(all(value == 0 for value in self.request["current_access_counters"].values()))

    def test_sequence_requires_two_green_milestones_before_one_execution(self):
        sequence = self.request["required_sequence_after_authorization"]
        decision_green = sequence.index("commit_push_and_obtain_remote_green_ci_for_decision")
        implementation = sequence.index(
            "implement_and_adversarially_test_with_synthetic_local_vhdr_fixtures_only"
        )
        implementation_green = sequence.index(
            "commit_push_and_obtain_remote_green_ci_for_implementation"
        )
        execution = sequence.index("execute_registered_vhdr_stage_once")
        stop = sequence.index("stop_before_loop54_stage_b")
        self.assertLess(decision_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, execution)
        self.assertLess(execution, stop)

    def test_packet_discloses_scope_caps_and_nonclaims(self):
        for phrase in (
            "11,705-byte BrainVision header",
            "may not resolve, stat, hash, or open those files",
            "256 MiB",
            "one registered execution",
            "cannot be repeated",
            "not actionable",
            "It would not establish EEG signal quality",
            "Every execution authorization remains false",
        ):
            self.assertIn(phrase.lower(), self.packet.lower())


if __name__ == "__main__":
    unittest.main()
