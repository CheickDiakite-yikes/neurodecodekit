import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_corrected_variable_width_r4_decomposition_result.v0.json"
)


class Marc2CorrectedVariableWidthR4DecompositionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_green_registration_preceded_preflight(self):
        proof = self.result["registration_proof"]
        self.assertEqual(
            proof["commit"], "cde85696de8ed998d15c79630265059264ba1f2c"
        )
        self.assertEqual(proof["CI_run_id"], 32_469_173_279)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_exactly_two_frozen_expectations_failed(self):
        cases = {row["case"]: row for row in self.result["case_results"]}
        self.assertEqual(len(cases), 5)
        self.assertFalse(cases["wrong_task_token"]["matched"])
        self.assertEqual(cases["wrong_task_token"]["observed_reason"], "core identity differs")
        collision = cases["duplicate_normalized_run_companion"]
        self.assertFalse(collision["matched"])
        self.assertEqual(collision["observed_reason"], "companion run spelling differs")
        self.assertEqual(sum(not row["matched"] for row in cases.values()), 2)

    def test_matching_cases_and_semantic_control_are_exact(self):
        cases = {row["case"]: row for row in self.result["case_results"]}
        for name in (
            "control_success",
            "mixed_lexical_tokens_within_bundle",
            "incomplete_companion_set",
        ):
            self.assertTrue(cases[name]["matched"], name)
        self.assertEqual(
            cases["control_success"]["semantic_sha256"],
            "254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba",
        )

    def test_lane_parks_before_full_matrix(self):
        preflight = self.result["generated_preflight"]
        self.assertEqual(preflight["VR16A_calls"], 5)
        self.assertEqual(preflight["VR15A_calls"], 0)
        self.assertFalse(preflight["full_equivalence_matrix_run"])
        self.assertFalse(preflight["full_residual_matrix_run"])
        self.assertFalse(preflight["direct_refusal_suite_run"])
        self.assertEqual(self.result["disposition_code"], "MARC2VR17B-P01")
        self.assertFalse(
            self.result["next_gate"]["VR17B_amendment_retry_or_rerun_allowed"]
        )

    def test_unavailable_measurements_and_zero_operations_are_explicit(self):
        preflight = self.result["generated_preflight"]
        self.assertIsNone(preflight["generated_input_bytes"])
        self.assertIsNone(preflight["peak_RSS_bytes"])
        self.assertEqual(preflight["retained_output_bytes"], 0)
        self.assertTrue(all(value == 0 for value in self.result["operation_counters"].values()))
        verification = self.result["verification"]
        self.assertEqual(verification["focused_contract_and_result_tests_passed"], 14)
        self.assertEqual(verification["complete_dependency_light_tests_passed"], 4_556)
        self.assertEqual(verification["complete_dependency_light_tests_skipped"], 204)
        self.assertEqual(verification["registry_JSON_files_parsed"], 331)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["git_diff_check_passed"])

    def test_no_scientific_or_private_claim_upgrade(self):
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_insight", "scientific_ceiling"}:
                self.assertFalse(value, key)
        self.assertFalse(self.result["next_gate"]["private_discriminator_authorized"])


if __name__ == "__main__":
    unittest.main()
