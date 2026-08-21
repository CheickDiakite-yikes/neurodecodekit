import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_variable_width_r4_decomposition_result.v0.json"


class Marc2VariableWidthR4DecompositionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_green_registration_preceded_preflight(self):
        proof = self.result["registration_proof"]
        self.assertEqual(proof["commit"], "e1c9366627e26a4a81c6eff152a8779eba5aa109")
        self.assertEqual(proof["CI_run_id"], 32_467_147_580)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_H3_failure_parks_without_full_matrix(self):
        failure = self.result["failed_gate"]
        self.assertEqual(failure["hypothesis_id"], "VR17A-H3")
        self.assertFalse(failure["full_registered_matrix_run"])
        self.assertTrue(failure["lane_parked_without_amendment"])
        self.assertEqual(self.result["disposition_code"], "MARC2VR17A-P01")

    def test_exact_two_control_four_repair_partition(self):
        measured = self.result["generated_preflight"]
        self.assertEqual(measured["VR15A_calls"], 6)
        self.assertEqual(measured["VR16A_calls"], 6)
        self.assertEqual(measured["VR15A_G1_count"], 2)
        self.assertEqual(measured["VR15A_R15_count"], 4)
        self.assertEqual(measured["VR16A_G1_count"], 6)
        self.assertEqual(measured["semantic_digest_count"], 1)
        self.assertEqual(
            measured["semantic_sha256"],
            "254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba",
        )

    def test_resources_and_private_counters_are_bounded(self):
        measured = self.result["generated_preflight"]
        self.assertEqual(measured["generated_input_bytes"], 2_651_670)
        self.assertEqual(measured["runtime_seconds"], 0.6208636660012417)
        self.assertEqual(measured["peak_RSS_bytes"], 33_390_592)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(measured["retained_output_bytes"], 0)
        self.assertTrue(all(value == 0 for value in self.result["operation_counters"].values()))

    def test_no_scientific_or_private_claim_upgrade(self):
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_insight", "scientific_ceiling"}:
                self.assertFalse(value, key)
        self.assertFalse(self.result["next_gate"]["private_discriminator_authorized"])

    def test_verification_is_recorded(self):
        verification = self.result["verification"]
        self.assertEqual(verification["focused_tests_passed"], 6)
        self.assertEqual(verification["complete_dependency_light_tests_passed"], 4_541)
        self.assertEqual(verification["complete_dependency_light_tests_skipped"], 204)
        self.assertTrue(verification["ruff_passed"])
        self.assertEqual(verification["registry_JSON_files_parsed"], 329)
        self.assertTrue(verification["git_diff_check_passed"])


if __name__ == "__main__":
    unittest.main()
