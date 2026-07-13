import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "registries" / "loop25_authorization_decision.v1.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop25_authorization_request.v1.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v1.json"
RW3_REQUEST_PATH = REPO_ROOT / "registries" / "rw3_stage_a_authorization_request.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_25_AUTHORIZATION_DECISION_V1.md"


class Loop25AuthorizationDecisionV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.rw3_request = json.loads(RW3_REQUEST_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_hash_bindings_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.loop25_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(decision["status"], "authorized_no_implementation_yet")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "6174b37b24a408a6b953538d85d43d3b30d36f26",
        )
        self.assertTrue(
            decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"
            ]
        )
        binding = decision["authorized_contract"]
        self.assertEqual(binding["contract_id"], self.contract["contract_id"])
        self.assertEqual(binding["amendment_commit"][:7], "b6b92d8")
        self.assertEqual(
            binding["contract_sha256"],
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        )
        request = decision["authorization_request"]
        self.assertEqual(
            request["request_sha256"],
            hashlib.sha256(REQUEST_PATH.read_bytes()).hexdigest(),
        )
        self.assertTrue(binding["contract_remains_immutable_preregistration_snapshot"])
        self.assertTrue(request["request_remains_immutable_and_unauthorized"])

    def test_broad_delegation_is_recorded_with_conservative_scope(self):
        user = self.decision["user_authorization"]
        self.assertTrue(user["explicit_loop25_authorization_intent"])
        self.assertTrue(user["delegated_research_decision_authority"])
        self.assertFalse(user["matches_packet_exact_sentence"])
        self.assertTrue(user["treated_as_conservative_frozen_scope_decision"])
        self.assertIn("I also authorize real or consumed data", user["broad_statement_verbatim"])
        self.assertIn("co-researcher", user["delegation_statement_verbatim"])
        self.assertIn("target-free", user["conservative_scope_interpretation"])
        self.assertTrue(
            user["computer_storage_and_other_project_safety_is_governing_operational_constraint"]
        )

    def test_only_seven_registered_loop25_surfaces_are_authorized(self):
        authorization = self.decision["authorization"]
        expected_true = {
            "loop25_implementation_authorized_now",
            "target_free_fixture_generation_authorized_now",
            "registered_filter_design_authorized_now",
            "registered_numeric_preprocessing_authorized_now",
            "development_partition_open_authorized_now",
            "conditional_qualification_partition_open_authorized_now",
            "report_and_cli_implementation_authorized_now",
        }
        expected_false = set(authorization) - expected_true
        self.assertEqual(len(expected_true), 7)
        self.assertTrue(all(authorization[key] is True for key in expected_true))
        self.assertTrue(all(authorization[key] is False for key in expected_false))
        for forbidden in [
            "real_or_consumed_data_access_authorized_now",
            "target_label_text_or_prediction_access_authorized_now",
            "checkpoint_or_model_inference_authorized_now",
            "training_or_parameter_updates_authorized_now",
            "rw3_stage_a_or_source_chunk_authorized_now",
            "stream_socket_board_device_hardware_authorized_now",
            "loop26_or_later_authorized_now",
        ]:
            self.assertIn(forbidden, expected_false)

    def test_preregistration_request_contract_and_rw3_remain_false(self):
        for payload in [self.request, self.contract]:
            flags = []

            def collect(value):
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key.endswith("_authorized_now"):
                            flags.append(child)
                        collect(child)
                elif isinstance(value, list):
                    for child in value:
                        collect(child)

            collect(payload)
            self.assertTrue(flags)
            self.assertTrue(all(value is False for value in flags))
        self.assertIsNone(self.request["authorization_record_commit"])
        self.assertFalse(self.rw3_request["authorized_now"])
        self.assertIsNone(self.rw3_request["user_decision"])
        self.assertIsNone(self.rw3_request["authorization_record_commit"])
        self.assertEqual(
            self.rw3_request["status"],
            "awaiting_explicit_user_authorization",
        )

    def test_access_order_and_partition_conditions_fail_closed(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(
            order[:3],
            [
                "test_this_authorization_record_and_all_existing_contract_invariants",
                "commit_and_push_authorization_only_changes_before_implementation",
                "confirm_the_pushed_authorization_commit_and_both_ci_jobs_are_green",
            ],
        )
        self.assertLess(
            order.index("pass_the_complete_static_filter_gate_before_any_fixture_array_open"),
            order.index(
                "open_seed_2501_once_and_freeze_the_development_report_if_static_passes"
            ),
        )
        self.assertLess(
            order.index(
                "open_seed_2501_once_and_freeze_the_development_report_if_static_passes"
            ),
            order.index("open_seed_2502_once_only_if_every_development_gate_passes"),
        )
        rules = self.decision["conditional_access_rules"]
        self.assertTrue(rules["static_filter_gate_must_pass_before_seed_2501_opens"])
        self.assertTrue(rules["development_report_must_be_frozen_before_seed_2502_opens"])
        self.assertFalse(rules["post_result_tuning_or_rerun_allowed"])

    def test_resources_and_authorization_only_measurements_are_bounded(self):
        resources = self.decision["resource_boundary"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["worker_processes"], 1)
        self.assertEqual(resources["maximum_fixture_bytes_total"], 4 * 1024 * 1024)
        self.assertEqual(
            resources["maximum_materialized_working_array_bytes"], 16 * 1024 * 1024
        )
        self.assertEqual(resources["maximum_generated_bytes_total"], 8 * 1024 * 1024)
        self.assertEqual(resources["maximum_internal_runtime_sec"], 45)
        self.assertEqual(resources["maximum_peak_rss_bytes"], 1024**3)
        for key, value in resources.items():
            if key.endswith("_reads") or key.endswith("_runs") or key.endswith("_operations"):
                self.assertEqual(value, 0, key)
        measurements = self.decision["authorization_only_measurements"]
        for key, value in measurements.items():
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_authorization_record_froze_zero_work_before_current_implementation(self):
        planned = self.contract["planned_implementation"]
        self.assertFalse(planned["files_exist_now"])
        self.assertFalse(planned["cli_exists_now"])
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["filter_coefficients_generated"], 0)
        self.assertEqual(measurements["fixture_items_generated"], 0)
        self.assertEqual(measurements["partition_arrays_opened"], 0)
        self.assertEqual(measurements["numeric_preprocessing_runs"], 0)
        for relative in planned["files"]:
            self.assertTrue((REPO_ROOT / relative).exists(), relative)
        cli_source = (REPO_ROOT / "src" / "neurodecodekit" / "cli.py").read_text(
            encoding="utf-8"
        )
        for command in planned["cli_commands"]:
            self.assertIn(command, cli_source)

    def test_human_decision_matches_machine_scope_and_claim_ceiling(self):
        for term in [
            "Authorized after this record is tested, committed, pushed",
            "seed 2501",
            "seed 2502",
            "<= 8 MiB",
            "real or consumed data:                  not used or authorized in Loop 25",
            "end-to-end latency measured:           false",
            self.decision["authorized_contract"]["contract_sha256"],
            self.decision["authorization_parent_commit"],
        ]:
            self.assertIn(term, self.doc)
        claims = " ".join(self.decision["claim_boundary"])
        for term in [
            "neural information",
            "decoding accuracy",
            "end-to-end latency",
            "unseen-person generalization",
            "device portability",
            "clinical utility",
        ]:
            self.assertIn(term, claims)


if __name__ == "__main__":
    unittest.main()
