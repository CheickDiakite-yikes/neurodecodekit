import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/marc2_selection_sufficiency_repair_contract.v0.json"
DOC = ROOT / "docs/MARC_2_SELECTION_SUFFICIENCY_REPAIR_PREREGISTRATION.md"


class SelectionSufficiencyRepairRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_green_predecessor_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR38A")
        proof = self.contract["green_predecessor_proof"]
        self.assertEqual(proof["commit"], "7de128053620514d067dbc1c99318a2b3bdb69e1")
        self.assertEqual(proof["CI_run_id"], 32_656_773_778)
        self.assertEqual(proof["base_python_job_id"], 97_236_607_433)
        self.assertEqual(proof["optional_neuro_job_id"], 97_236_607_490)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_fixed_inputs_are_byte_exact(self):
        total = 0
        for row in self.contract["fixed_inputs"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            total += len(payload)
        self.assertEqual(len(self.contract["fixed_inputs"]), 11)
        self.assertEqual(total, 252_686)
        self.assertEqual(total, self.contract["fixed_input_bytes"])

    def test_VR37P_is_proven_but_left_unexecuted(self):
        findings = self.contract["artifact_only_findings"]
        self.assertTrue(findings["VR37P_packet_remotely_proven"])
        self.assertFalse(findings["VR37P_packet_bound_decision_received"])
        self.assertFalse(findings["VR37P_private_execution_performed"])
        self.assertFalse(findings["VR37P_any_route_can_freeze_cohort"])
        self.assertTrue(findings["existing_selector_uses_first_three_sorted_runs"])
        self.assertTrue(findings["existing_selector_requires_runs_1_2_3"])

    def test_selection_rule_preserves_scientific_core(self):
        selection = self.contract["selection_contract"]
        self.assertEqual(selection["required_runs_per_session"], [1, 2, 3])
        self.assertEqual(selection["minimum_selected_subjects"], 12)
        self.assertEqual(selection["selected_bundles_per_subject"], 6)
        self.assertEqual(selection["selected_core_members_per_subject"], 24)
        self.assertFalse(selection["selected_run_above_3_allowed"])
        self.assertFalse(selection["non_target_or_ineligible_selected_row_allowed"])
        self.assertTrue(selection["optional_complete_run_above_3_may_be_ignored"])
        self.assertFalse(selection["global_eligible_total_equality_required_for_selection"])

    def test_routes_and_matrix_are_frozen(self):
        self.assertEqual(
            [row["route"] for row in self.contract["ordered_routes"]],
            [
                "MARC2VR38A-G1",
                "MARC2VR38A-G2",
                "MARC2VR38A-R1",
                "MARC2VR38A-R2",
                "MARC2VR38A-R3",
            ],
        )
        matrix = self.contract["generated_matrix"]
        self.assertEqual(len(matrix["cases"]), 10)
        self.assertEqual(matrix["required_paths"], 40)
        self.assertEqual(matrix["accepted_paths"], 20)
        self.assertEqual(sum(matrix["expected_route_counts"].values()), 40)
        self.assertEqual(matrix["accepted_semantic_selection_identities"], 1)
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 80)

    def test_private_and_scientific_surfaces_remain_closed(self):
        implementation = self.contract["implementation_contract"]
        self.assertEqual(implementation["commands"], ["plan", "qualify"])
        self.assertFalse(implementation["private_executor_allowed"])
        self.assertFalse(implementation["VR37P_wrapper_or_private_discriminator_call_allowed"])
        self.assertTrue(all(value == 0 for value in self.contract["forbidden_operations"].values()))
        gate = self.contract["terminal_next_gate"]
        self.assertTrue(
            gate["next_private_structural_request_must_freeze_a_cohort_or_park_Freewill"]
        )
        self.assertFalse(gate["topology_only_private_successor_allowed"])
        self.assertFalse(
            gate[
                "private_read_cohort_freeze_archive_neural_target_model_score_or_claim_authorized_now"
            ]
        )

    def test_human_registration_matches_the_machine_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Do not execute `MARC2-VR37P`", text)
        self.assertIn("implementation blocked until", text)
        self.assertIn("source-bound cohort of at least 12 participants", text)
        self.assertIn("Engineering capability proposed", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
