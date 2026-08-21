import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_variable_width_run_index_repair_contract.v0.json"
)
RESEARCH_PATH = ROOT / "docs/MARC_2_VARIABLE_WIDTH_RUN_INDEX_PRIMARY_SOURCE_RESEARCH.md"
PREREG_PATH = ROOT / "docs/MARC_2_VARIABLE_WIDTH_RUN_INDEX_REPAIR_PREREGISTRATION.md"


class Marc2VariableWidthRunIndexRepairContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_real_route_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR16A")
        observed = self.contract["observed_route_binding"]
        self.assertEqual(observed["VR15P_route"], "MARC2VR15P-R15")
        self.assertEqual(
            observed["frozen_class"],
            "run_token_width_outside_one_or_two_ASCII_digits",
        )
        for key, value in observed.items():
            if key not in {"VR15P_route", "frozen_class"}:
                self.assertFalse(value, key)

    def test_fixed_inputs_match_size_and_sha256(self):
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(row["bytes"] for row in rows), 121_238)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_standards_basis_and_repair_are_narrow(self):
        standards = self.contract["standards_basis"]
        self.assertEqual(standards["BIDS_version"], "1.11.1")
        self.assertEqual(
            standards["index_semantics"],
            "nonnegative_integer_with_arbitrary_leading_zeroes",
        )
        self.assertEqual(len(standards["references"]), 3)

        repair = self.contract["frozen_repair"]
        self.assertEqual(repair["accepted_run_token_regex"], "[0-9]+")
        self.assertIsNone(repair["separate_run_width_ceiling"])
        self.assertEqual(repair["member_name_UTF8_bytes_maximum"], 1_024)
        self.assertEqual(repair["allowed_semantic_run_values"], [1, 2, 3])
        self.assertTrue(repair["canonical_identity_checked_before_integer_conversion"])
        self.assertTrue(repair["normalized_duplicate_companions_refuse"])
        self.assertTrue(repair["selected_member_names_remain_source_exact"])
        self.assertFalse(repair["subject_session_task_suffix_entity_order_or_prefix_broadening"])

    def test_generated_matrix_and_resources_are_bounded(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(len(matrix["success_variants"]), 6)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_success_paths"], 24)
        self.assertGreaterEqual(len(matrix["required_refusal_witnesses"]), 14)
        self.assertEqual(self.contract["direct_refusal_minimum"], 48)

        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(caps["temporary_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)

    def test_authority_and_claim_boundary_are_empty(self):
        self.assertTrue(
            all(value is False for value in self.contract["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )
        gate = self.contract["implementation_gate"]
        self.assertTrue(gate["this_registration_commit_push_and_both_jobs_green_required"])
        self.assertFalse(gate["private_or_neural_execution_authorized"])
        claims = self.contract["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability_sought", "scientific_ceiling"}:
                self.assertFalse(value, key)

    def test_documents_preserve_scope_and_claim_boundary(self):
        research = RESEARCH_PATH.read_text(encoding="utf-8")
        prereg = PREREG_PATH.read_text(encoding="utf-8")
        self.assertIn("arbitrary number of zeroes", research)
        self.assertIn("No private", research)
        self.assertIn("24 success paths", prereg)
        self.assertIn("Scientific claim not established", prereg)
        self.assertIn("Do not open or list `.codex_work`", prereg)


if __name__ == "__main__":
    unittest.main()
