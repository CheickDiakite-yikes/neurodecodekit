import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "physionet_motor_positive_control_authorization_decision.v0.json"
)
REQUEST_PATH = (
    ROOT / "registries/physionet_motor_positive_control_authorization_request.v0.json"
)
CONTRACT_PATH = ROOT / "registries/physionet_motor_positive_control_contract.v0.json"
PACKET_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_PACKET.md"
DOC_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_DECISION.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if "authorized_" in key:
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class PhysioNetMotorPositiveControlAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_hash_bindings_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.physionet_motor_positive_control_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["status"],
            "authorized_after_remote_green_no_implementation_or_execution_yet",
        )
        self.assertEqual(
            decision["authorization_parent_commit"],
            "c62b10a6e9dae8d92e5ff54d17403e1054a0ac76",
        )
        self.assertTrue(
            decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"
            ]
        )
        self.assertEqual(decision["authorized_contract"]["sha256"], sha256(CONTRACT_PATH))
        self.assertEqual(
            decision["authorized_contract"]["git_blob_sha1"],
            git_blob_sha1(CONTRACT_PATH),
        )
        self.assertEqual(decision["authorization_request"]["sha256"], sha256(REQUEST_PATH))
        self.assertEqual(
            decision["authorization_request"]["git_blob_sha1"],
            git_blob_sha1(REQUEST_PATH),
        )
        self.assertEqual(decision["authorization_packet"]["sha256"], sha256(PACKET_PATH))

    def test_green_request_commit_and_both_jobs_are_exact(self):
        green = self.decision["green_request"]
        self.assertEqual(green["commit"], "c62b10a6e9dae8d92e5ff54d17403e1054a0ac76")
        self.assertEqual(green["push_ci_run_id"], 31347209691)
        self.assertEqual(green["base_python_job_id"], 93331241434)
        self.assertEqual(green["optional_neuro_job_id"], 93331241411)
        self.assertEqual(green["push_ci_conclusion"], "success")
        self.assertEqual(green["base_python_job_conclusion"], "success")
        self.assertEqual(green["optional_neuro_job_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])

    def test_exact_user_sentence_matches_request_and_human_decision(self):
        user = self.decision["user_authorization"]
        sentence = user["exact_sentence_verbatim"]
        self.assertEqual(sentence, self.request["authorization"]["exact_authorization_sentence"])
        self.assertEqual(self.doc.count(sentence), 1)
        self.assertTrue(user["matches_request_exact_sentence"])
        self.assertTrue(user["one_registered_execution_only"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_contract_and_request_remain_immutable_pending_snapshots(self):
        self.assertEqual(
            self.contract["status"],
            "preregistered_tier_c_not_authorized_not_implemented_not_executed",
        )
        self.assertEqual(self.request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(self.request["authorized_now"])
        self.assertFalse(self.request["authorization"]["exact_sentence_received_from_user"])
        self.assertTrue(
            self.decision["authorized_contract"][
                "remains_immutable_preregistration_snapshot"
            ]
        )
        self.assertTrue(
            self.decision["authorization_request"][
                "remains_immutable_and_unauthorized_snapshot"
            ]
        )

    def test_authorization_is_exact_and_every_expansion_remains_false(self):
        authorization = self.decision["authorization"]
        expected_true = {
            "fixture_only_implementation_authorized_after_decision_green",
            "narrow_optional_classical_extra_authorized_after_decision_green",
            "isolated_dependency_environment_authorized_after_decision_green",
            "registered_local_manifest_verification_authorized_after_implementation_green",
            "nine_edf_size_sha256_and_semantic_parse_authorized_after_implementation_green",
            "registered_header_annotation_signal_geometry_reads_authorized_after_implementation_green",
            "target_firewalled_derivative_creation_authorized_after_implementation_green",
            "bounded_classical_training_and_inference_authorized_after_implementation_green",
            "hash_only_prediction_freeze_authorized_after_implementation_green",
            "one_final_target_delivery_and_score_authorized_after_freeze_green",
            "invocation_created_temporary_cleanup_authorized_now",
        }
        flags = dict(authorization_flags(authorization))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 24)

    def test_registered_scope_matches_frozen_contract(self):
        run = self.decision["registered_execution"]
        binding = self.contract["dataset_binding"]
        self.assertEqual(run["provider"], binding["provider"])
        self.assertEqual(run["dataset_id"], binding["dataset_id"])
        self.assertEqual(run["dataset_version"], binding["version"])
        self.assertEqual(run["subjects"], binding["subjects"])
        self.assertEqual(run["fit_and_selection_runs"], binding["fit_and_selection_runs"])
        self.assertEqual(run["sealed_final_run"], binding["sealed_final_run"])
        self.assertEqual(run["file_count"], 9)
        self.assertEqual(run["payload_bytes"], 23_248_224)
        self.assertEqual(run["expected_task_events"], 135)
        self.assertEqual(run["sealed_final_events"], 45)
        self.assertEqual(run["maximum_verdict"], "WO9-V3")
        self.assertEqual(run["retries"], 0)
        self.assertEqual(run["reruns"], 0)

    def test_order_requires_three_remote_green_milestones_before_score(self):
        order = self.decision["required_execution_order"]
        decision_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_authorization_record"
        )
        implementation = order.index(
            "implement_and_fixture_test_without_local_physionet_operation"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_exact_implementation"
        )
        real_parse = order.index(
            "make_one_size_sha256_pass_and_one_semantic_parse_per_registered_edf"
        )
        freeze_green = order.index(
            "commit_push_and_obtain_green_ci_for_prediction_freeze"
        )
        score = order.index("deliver_and_score_same_45_run11_targets_once")
        self.assertLess(decision_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, real_parse)
        self.assertLess(real_parse, freeze_green)
        self.assertLess(freeze_green, score)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(rules["implementation_may_begin_before_authorization_commit_is_green"])
        self.assertFalse(
            rules["local_physionet_operation_may_begin_before_implementation_commit_is_green"]
        )
        self.assertFalse(
            rules["run11_targets_may_open_before_prediction_freeze_commit_is_green"]
        )
        self.assertFalse(rules["registered_execution_may_run_more_than_once"])
        self.assertFalse(rules["post_target_update_or_tuning_may_occur"])

    def test_resource_caps_match_frozen_contract_and_request(self):
        real = self.decision["resource_boundary"]["real_execution"]
        contract = self.contract["resource_caps"]
        for key in (
            "registered_executions",
            "cpu_threads",
            "workers",
            "concurrent_numerical_jobs",
            "wall_time_seconds",
            "peak_rss_bytes",
            "network_bytes",
            "new_payload_bytes",
            "edf_sha256_passes",
            "edf_semantic_parses",
            "final_target_deliveries",
            "final_scoring_events",
            "retries",
            "reruns",
        ):
            self.assertEqual(real[key], contract[key], key)
        self.assertEqual(real["maximum_generated_private_output_bytes"], 64 * 1024 * 1024)
        self.assertEqual(real["maximum_classical_fits"], 40)
        self.assertEqual(real["maximum_prediction_sets"], 64)

        install = self.decision["resource_boundary"]["optional_environment_installation"]
        request_install = self.request["resource_caps"][
            "optional_environment_installation"
        ]
        self.assertEqual(install, {key: request_install[key] for key in install})
        self.assertFalse(install["base_dependency_change"])

    def test_authorization_only_measurements_preserve_zero_real_operations(self):
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["github_ci_verification_calls"], 1)
        for key, value in measurements.items():
            if key == "github_ci_verification_calls":
                continue
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_ceiling_remains_narrow(self):
        claim = self.decision["claim_boundary"]
        self.assertIn("three-person", claim["maximum_after_clean_WO9_V3"])
        unavailable = claim["scientific_claim_not_established"]
        for term in (
            "brain-specific",
            "unseen-person",
            "typing",
            "thought decoding",
            "real-time",
            "portable hardware",
            "clinical",
        ):
            self.assertIn(term, unavailable)
        normalized_doc = " ".join(self.doc.split()).lower()
        self.assertIn("no dependency installation, implementation", normalized_doc)


if __name__ == "__main__":
    unittest.main()
