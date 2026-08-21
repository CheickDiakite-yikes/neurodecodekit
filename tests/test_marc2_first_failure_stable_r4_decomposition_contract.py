import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_first_failure_stable_r4_decomposition_contract.v0.json"
)


class Marc2FirstFailureStableR4DecompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_parked_predecessor_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR17C")
        proof = self.contract["predecessor_proof"]
        self.assertEqual(proof["parked_route"], "MARC2VR17B-P01")
        self.assertEqual(
            proof["commit"], "3d69d65424bba1c8cd48abca50b5337d97b688e0"
        )
        self.assertEqual(proof["CI_run_id"], 32_470_024_380)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["VR17B_amendment_retry_or_rerun_allowed"])

    def test_all_fixed_inputs_are_exact(self):
        fixed = self.contract["fixed_inputs"]
        self.assertEqual(len(fixed), self.contract["fixed_input_count"])
        self.assertEqual(sum(row["bytes"] for row in fixed), 139_348)
        for row in fixed:
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_equivalence_map_preserves_two_controls_and_four_repairs(self):
        mapping = self.contract["corrected_equivalence_map"]
        self.assertEqual(len(mapping["supported_controls"]), 2)
        self.assertEqual(len(mapping["extended_width_repairs"]), 4)
        self.assertTrue(
            all(row["VR15A_route"] == "MARC2VR15A-G1" for row in mapping["supported_controls"])
        )
        self.assertTrue(
            all(
                row["VR15A_route"] == "MARC2VR15A-R15"
                for row in mapping["extended_width_repairs"]
            )
        )

    def test_collision_witness_is_same_token_and_row_count_stable(self):
        witness = self.contract["collision_witness"]
        self.assertEqual(witness["source_row_count"], 1_227)
        self.assertEqual(witness["local_header_offset_delta"], 1)
        self.assertFalse(witness["run_token_changed"])
        self.assertFalse(witness["source_row_count_changed"])
        self.assertEqual(witness["expected_route"], "MARC2VR16A-F05")
        self.assertEqual(
            witness["expected_safe_reason"],
            "normalized run companion is duplicated",
        )
        self.assertTrue(witness["generated_development_check_passed"])

    def test_hypotheses_and_residual_routes_are_first_failure_stable(self):
        hypotheses = self.contract["composition_hypotheses"]
        self.assertEqual([row["id"] for row in hypotheses], [f"VR17C-H{i}" for i in range(1, 5)])
        self.assertTrue(all(row["must_be_generated_proven"] for row in hypotheses))
        residual = self.contract["residual_first_failure_classes"]
        self.assertEqual([row["route"] for row in residual], [f"MARC2VR17C-R{i}" for i in range(1, 5)])
        self.assertEqual(len({(row["VR16A_route"], row["safe_reason"]) for row in residual}), 4)
        self.assertEqual(residual[0]["safe_reason"], "core identity differs")

    def test_matrix_and_resources_are_bounded(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(matrix["equivalence_paths"], 24)
        self.assertEqual(matrix["residual_paths"], 20)
        self.assertEqual(matrix["total_VR15A_calls"], 24)
        self.assertEqual(matrix["total_VR16A_calls"], 44)
        caps = self.contract["resource_caps"]
        for key in ("CPU_threads", "workers", "numerical_jobs"):
            self.assertEqual(caps[key], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 40 * 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        verification = self.contract["registration_verification"]
        self.assertEqual(verification["focused_contract_tests_passed"], 8)
        self.assertEqual(verification["complete_dependency_light_tests_passed"], 4_564)
        self.assertEqual(verification["expected_skips"], 204)
        self.assertEqual(verification["registry_JSON_files_parsed"], 332)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["git_diff_check_passed"])

    def test_authority_and_operation_counters_fail_closed(self):
        self.assertTrue(all(value == 0 for value in self.contract["operation_counters"].values()))
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
