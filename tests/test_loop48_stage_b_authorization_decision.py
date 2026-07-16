import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "registries" / "loop48_stage_b_authorization_decision.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop48_stage_b_authorization_request.v0.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_train_only_discrimination_contract.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md"
PUBLIC_PATHS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop48StageBAuthorizationDecisionTests(unittest.TestCase):
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
            "neurodecodekit.loop48_stage_b_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(decision["status"], "authorized_no_implementation_or_execution_yet")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "54bbbdf6d052b4f273db13819e6dac77c29c4ba3",
        )
        self.assertTrue(
            decision["effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"]
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

    def test_exact_user_sentence_matches_request_and_human_decision(self):
        user = self.decision["user_authorization"]
        sentence = user["exact_sentence_verbatim"]
        self.assertEqual(sentence, self.request["authorization"]["exact_authorization_sentence"])
        self.assertEqual(self.doc.count(sentence), 1)
        self.assertTrue(user["matches_request_exact_sentence"])
        self.assertTrue(user["one_registered_execution_only"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])
        self.assertTrue(user["research_autonomy_charter_is_not_substitute_authorization"])

    def test_contract_and_request_remain_immutable_unauthorized_snapshots(self):
        for payload in (self.contract, self.request):
            flags = authorization_flags(payload)
            self.assertTrue(flags)
            self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertEqual(
            self.contract["status"],
            "preregistered_not_authorized_no_protected_execution",
        )
        self.assertEqual(self.request["status"], "awaiting_exact_user_authorization")
        self.assertTrue(
            self.decision["authorized_contract"]["remains_immutable_preregistration_snapshot"]
        )
        self.assertTrue(
            self.decision["authorization_request"]["remains_immutable_and_unauthorized_snapshot"]
        )

    def test_only_exact_registered_surfaces_are_authorized(self):
        expected_true = {
            "stage_b_implementation_authorized_now",
            "one_source_cache_sha256_pass_authorized_now",
            "target_free_split_metadata_read_authorized_now",
            "opaque_deflated_member_traversal_authorized_now",
            "fit_and_check_derivative_creation_authorized_now",
            "forty_four_fit_signal_target_row_delivery_authorized_now",
            "eleven_check_signal_row_pre_freeze_delivery_authorized_now",
            "twenty_parameter_update_runs_authorized_now",
            "thirty_five_target_blind_inference_runs_authorized_now",
            "five_train_only_prior_fits_authorized_now",
            "forty_one_prediction_sets_authorized_now",
            "conditional_eleven_check_target_post_green_delivery_authorized_now",
            "one_check_scoring_event_authorized_now",
            "one_registered_stage_b_execution_authorized_now",
        }
        flags = dict(authorization_flags(self.decision["authorization"]))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 26)

    def test_registered_operation_counts_match_the_frozen_request(self):
        run = self.decision["registered_execution"]
        requested = self.request["requested_scope"]
        shared = (
            "source_cache_bytes",
            "source_cache_sha256",
            "source_cache_sha256_passes",
            "source_partition_rows",
            "fit_signal_rows_delivered",
            "fit_target_rows_delivered",
            "check_signal_rows_delivered",
            "check_target_rows_delivered_before_green_freeze",
            "check_target_rows_delivered_after_green_freeze",
            "check_target_delivery_events",
            "parameter_update_runs",
            "optimizer_steps",
            "target_blind_model_inference_runs",
            "train_only_no_signal_prior_fits",
            "prediction_sets",
            "check_scoring_events",
            "validation_rows_delivered",
            "source_test_rows_delivered",
            "session2_rows_delivered",
            "raw_fif_or_mat_reads",
            "new_download_bytes",
            "reruns_after_check_scoring",
        )
        for key in shared:
            self.assertEqual(run[key], requested[key], key)

    def test_order_requires_three_distinct_green_gates(self):
        order = self.decision["required_execution_order"]
        authorization_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_authorization_record"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_implementation"
        )
        protected_read = order.index("one_source_cache_sha256_pass")
        freeze_green = order.index(
            "commit_push_and_obtain_green_ci_for_plaintext_free_prediction_freeze"
        )
        target_delivery = order.index("deliver_exactly_11_check_targets_once")
        self.assertLess(authorization_green, implementation_green)
        self.assertLess(implementation_green, protected_read)
        self.assertLess(protected_read, freeze_green)
        self.assertLess(freeze_green, target_delivery)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(
            rules["protected_inputs_may_be_read_during_implementation_or_synthetic_tests"]
        )
        self.assertFalse(
            rules["check_targets_may_be_read_before_prediction_freeze_commit_is_green"]
        )
        self.assertTrue(rules["check_targets_may_be_read_after_prediction_freeze_commit_is_green"])
        self.assertFalse(rules["stage_b_may_run_more_than_once"])

    def test_resource_caps_match_the_frozen_request(self):
        resources = self.decision["resource_boundary"]
        requested = self.request["resource_caps"]
        self.assertEqual(resources, requested)
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["peak_rss_bytes"], 1024**3)
        self.assertEqual(resources["total_generated_artifact_bytes"], 32 * 1024**2)
        self.assertEqual(resources["minimum_free_disk_bytes_before_execution"], 20 * 1024**3)

    def test_authorization_only_measurements_are_zero(self):
        for key, value in self.decision["authorization_only_measurements"].items():
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_ceiling_and_public_status_preserve_history_and_result(self):
        claim = self.decision["claim_boundary"]
        self.assertEqual(claim["maximum_evidence_level"], "E2_pipeline_discriminative")
        unavailable = claim["scientific_claim_not_established"]
        for term in (
            "independent validation",
            "neural advantage",
            "brain-specific",
            "unseen-person",
            "real-time",
            "portable-device",
            "clinical",
        ):
            self.assertIn(term, unavailable)

        self.assertIn(
            "no implementation",
            " ".join(DOC_PATH.read_text(encoding="utf-8").lower().split()),
        )
        for path in PUBLIC_PATHS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn("LOOP_48_STAGE_B_AUTHORIZATION_DECISION.md", content)
                self.assertIn("loop48_train_only_discrimination_result.v0.json", content)
                self.assertIn("no rerun", " ".join(content.lower().split()))


if __name__ == "__main__":
    unittest.main()
