import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "registries" / "loop24_authorization_decision.v0.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "local_precision_runtime_contract.v0.json"
RW3_CONTRACT_PATH = REPO_ROOT / "registries" / "replay_equivalence_contract.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_24_AUTHORIZATION_DECISION.md"


class Loop24AuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.rw3_contract = json.loads(RW3_CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_contract_binding_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"], "neurodecodekit.loop24_authorization_decision"
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["status"], "authorized_no_implementation_yet"
        )
        self.assertEqual(
            decision["authorization_parent_commit"],
            "4050b8590507e079eccb961668706eaa0ae6f228",
        )
        binding = decision["authorized_contract"]
        self.assertEqual(binding["contract_id"], self.contract["contract_id"])
        self.assertEqual(binding["contract_schema_version"], self.contract["schema_version"])
        self.assertEqual(binding["preregistration_commit"], "186bb6f")
        self.assertEqual(
            binding["contract_sha256"],
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        )
        self.assertTrue(binding["contract_remains_immutable_preregistration_snapshot"])
        self.assertTrue(
            decision["effective_only_after_this_record_is_tested_committed_and_pushed"]
        )

    def test_user_statement_is_recorded_as_a_conservative_scope_amendment(self):
        user = self.decision["user_authorization"]
        self.assertTrue(user["explicit_loop24_authorization_intent"])
        self.assertFalse(user["matches_original_exact_sentence"])
        self.assertTrue(user["treated_as_scope_amendment_request"])
        self.assertIn("loop 24 real data / training", user["statement_verbatim"])
        self.assertIn("target-free synthetic", user["conservative_scope_interpretation"])
        self.assertTrue(user["fresh_real_data_and_training_intent_recorded_for_later_gates"])

    def test_only_registered_target_free_loop24_execution_is_authorized(self):
        authorization = self.decision["authorization"]
        expected_true = {
            "loop24_implementation_authorized_now",
            "target_free_fixture_generation_authorized_now",
            "frozen_checkpoint_validation_and_open_authorized_now",
            "registered_candidate_conversion_authorized_now",
            "registered_model_inference_authorized_now",
            "registered_selection_authorized_now",
            "conditional_one_time_qualification_authorized_now",
            "report_and_cli_implementation_authorized_now",
        }
        expected_false = set(authorization) - expected_true
        self.assertTrue(all(authorization[key] is True for key in expected_true))
        self.assertTrue(all(authorization[key] is False for key in expected_false))
        self.assertIn("real_data_access_authorized_now", expected_false)
        self.assertIn("training_or_parameter_updates_authorized_now", expected_false)
        self.assertIn("rw3_stage_a_authorized_now", expected_false)
        self.assertIn("device_or_hardware_authorized_now", expected_false)

    def test_preregistration_and_rw3_snapshots_remain_unchanged_and_false(self):
        self.assertTrue(
            all(
                value is False
                for key, value in self.contract["authorization"].items()
                if key.endswith("_authorized_now")
            )
        )
        self.assertTrue(
            all(
                value is False
                for key, value in self.rw3_contract["authorization"].items()
                if key.endswith("_authorized_now")
            )
        )
        self.assertFalse(
            self.decision["authorization"]["rw3_stage_a_authorized_now"]
        )

    def test_execution_order_resources_and_protected_evidence_fail_closed(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(
            order[:3],
            [
                "test_this_authorization_record_and_all_existing_contract_invariants",
                "commit_and_push_authorization_only_changes_before_implementation",
                "confirm_the_pushed_authorization_commit_and_ci",
            ],
        )
        self.assertLess(
            order.index("freeze_selection_report_and_candidate_decision"),
            order.index(
                "open_seed_2402_qualification_once_only_if_a_nonreference_replacement_candidate_qualifies"
            ),
        )
        resources = self.decision["resource_boundary"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["worker_processes"], 1)
        self.assertEqual(resources["max_generated_artifact_bytes"], 4 * 1024 * 1024)
        self.assertEqual(resources["max_materialized_array_bytes"], 32 * 1024 * 1024)
        self.assertEqual(resources["energy_measurement"], "not_authorized_for_this_execution")
        protected = self.decision["protected_evidence"]
        self.assertEqual(protected["consumed_synthetic_seeds"], [2203, 2303, 2353])
        self.assertEqual(protected["fresh_loop24_seeds"], {"selection": 2401, "qualification": 2402})
        self.assertTrue(any("session-2" in row for row in protected["real_cohorts"]))
        self.assertTrue(any("S7 EEG" in row for row in protected["real_cohorts"]))

    def test_real_data_training_and_eeg_are_routed_without_claim_upgrade(self):
        routing = self.decision["scope_routing"]
        self.assertIn("Loop 27", routing["real_data"])
        self.assertIn("separate authorization", routing["real_data"])
        self.assertIn("Loop 26", routing["real_training"])
        self.assertIn("Loop 25", routing["real_training"])
        self.assertIn("Do not reopen", routing["real_training"])
        self.assertIn("negative consumed evaluation", routing["eeg"])
        claims = " ".join(self.decision["claim_boundary"])
        for term in [
            "neural information",
            "real-data accuracy",
            "unseen-person transfer",
            "end-to-end latency",
            "portable hardware",
            "clinical utility",
        ]:
            self.assertIn(term, claims)

    def test_human_decision_matches_machine_scope_and_zero_runtime_boundary(self):
        for term in [
            "Authorized after this record is tested, committed, and pushed",
            "real or consumed data access:      not authorized under Loop 24",
            "training or parameter updates:     not authorized under Loop 24",
            "seed 2401",
            "seed 2402",
            "<= 4 MiB",
            "end-to-end latency measured:         false",
        ]:
            self.assertIn(term, self.doc)
        self.assertIn(self.decision["authorized_contract"]["contract_sha256"], self.doc)
        self.assertIn(self.decision["authorization_parent_commit"], self.doc)


if __name__ == "__main__":
    unittest.main()
