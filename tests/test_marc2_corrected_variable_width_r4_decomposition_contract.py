import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "registries/marc2_corrected_variable_width_r4_decomposition_contract.v0.json"
)


class Marc2CorrectedVariableWidthR4DecompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_parked_predecessor_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR17B")
        proof = self.contract["predecessor_proof"]
        self.assertEqual(proof["parked_lane"], "MARC2-VR17A")
        self.assertEqual(proof["parked_route"], "MARC2VR17A-P01")
        self.assertEqual(
            proof["commit"], "48775bb35c9ff624293c6914425ca2119b0a131a"
        )
        self.assertEqual(proof["CI_run_id"], 32_468_221_097)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["VR17A_full_matrix_ran"])
        self.assertFalse(proof["VR17A_amendment_or_rerun_allowed"])

    def test_all_fixed_inputs_are_exact(self):
        fixed = self.contract["fixed_inputs"]
        self.assertEqual(len(fixed), self.contract["fixed_input_count"])
        self.assertEqual(sum(row["bytes"] for row in fixed), 152_527)
        for row in fixed:
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_corrected_two_control_four_repair_map_is_exact(self):
        mapping = self.contract["corrected_equivalence_map"]
        controls = mapping["supported_controls"]
        repairs = mapping["extended_width_repairs"]
        self.assertEqual([row["variant"] for row in controls], ["unpadded", "two_digit_control"])
        self.assertTrue(
            all(
                row["VR15A_route"] == "MARC2VR15A-G1"
                and row["VR16A_route"] == "MARC2VR16A-G1"
                for row in controls
            )
        )
        self.assertEqual(len(repairs), 4)
        self.assertTrue(
            all(
                row["VR15A_route"] == "MARC2VR15A-R15"
                and row["VR16A_route"] == "MARC2VR16A-G1"
                for row in repairs
            )
        )
        self.assertEqual(mapping["semantic_digest_count"], 1)

    def test_hypotheses_bind_corrected_H3_and_fail_closed(self):
        hypotheses = self.contract["composition_hypotheses"]
        self.assertEqual([row["id"] for row in hypotheses], [f"VR17B-H{i}" for i in range(1, 5)])
        self.assertTrue(all(row["must_be_generated_proven"] for row in hypotheses))
        self.assertIn("Two supported controls", hypotheses[2]["statement"])
        self.assertNotIn("All six width-only sources classify as VR15A R15", hypotheses[2]["statement"])
        self.assertEqual(self.contract["park_route"], "MARC2VR17B-P01")

    def test_four_residual_classes_and_matrix_are_frozen(self):
        residual = self.contract["residual_first_failure_classes"]
        self.assertEqual(
            [row["route"] for row in residual],
            [f"MARC2VR17B-R{i}" for i in range(1, 5)],
        )
        self.assertEqual(len({(row["VR16A_route"], row["safe_reason"]) for row in residual}), 4)
        matrix = self.contract["generated_matrix"]
        self.assertEqual(matrix["equivalence_paths"], 24)
        self.assertEqual(matrix["residual_paths"], 20)
        self.assertEqual(matrix["total_VR15A_calls"], 24)
        self.assertEqual(matrix["total_VR16A_calls"], 44)
        self.assertEqual(matrix["residual_route_count_each"], 4)

    def test_resources_and_operation_counters_are_bounded(self):
        caps = self.contract["resource_caps"]
        for key in ("CPU_threads", "workers", "numerical_jobs"):
            self.assertEqual(caps[key], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 40 * 1024**2)
        self.assertLessEqual(caps["aggregate_output_bytes"], 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        self.assertTrue(all(value == 0 for value in self.contract["operation_counters"].values()))
        verification = self.contract["registration_verification"]
        self.assertEqual(verification["focused_contract_tests_passed"], 8)
        self.assertEqual(verification["complete_dependency_light_tests_passed"], 4_550)
        self.assertEqual(verification["expected_skips"], 204)
        self.assertEqual(verification["registry_JSON_files_parsed"], 330)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["git_diff_check_passed"])

    def test_authority_remains_generated_only_after_remote_green(self):
        authority = self.contract["authority"]
        self.assertTrue(authority["registration_only"])
        self.assertTrue(
            authority[
                "generated_implementation_allowed_after_exact_registration_remote_green"
            ]
        )
        for key, value in authority.items():
            if key not in {
                "registration_only",
                "generated_implementation_allowed_after_exact_registration_remote_green",
            }:
                self.assertFalse(value, key)
        self.assertIsNone(self.contract["remote_registration_proof"])

    def test_claim_boundary_remains_non_neural(self):
        claims = self.contract["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability_sought", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
