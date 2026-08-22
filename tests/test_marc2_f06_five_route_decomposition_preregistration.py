import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_f06_five_route_decomposition_contract.v0.json"
)


class Marc2F06FiveRouteDecompositionPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_fixed_inputs_are_exact(self):
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), 14)
        total = 0
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["role"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                row["sha256"],
                row["role"],
            )
            total += len(payload)
        self.assertEqual(total, 207_381)
        self.assertEqual(total, self.contract["fixed_input_bytes"])

    def test_green_result_anchor_and_consumed_route_are_exact(self):
        proof = self.contract["result_proof_anchor"]
        self.assertEqual(
            proof["commit"],
            "6920576a2bc9ad94cf854112c19712ee42bc0c94",
        )
        self.assertEqual(proof["CI_run_id"], 32_595_422_650)
        self.assertEqual(proof["base_job_id"], 97_085_435_130)
        self.assertEqual(proof["optional_neuro_job_id"], 97_085_434_967)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["observed_route"], "MARC2VR22P-R4")
        self.assertFalse(proof["private_source_reopened_by_registration"])

    def test_static_inventory_and_redundancy_proof_are_frozen(self):
        inventory = self.contract["static_inventory"]
        self.assertEqual(inventory["VR20A_F06_wrapper_call_site_count"], 2)
        self.assertEqual(inventory["VR2_bound_safe_reason_count"], 7)
        self.assertEqual(inventory["non_independent_defensive_reason_count"], 2)
        self.assertEqual(inventory["independently_reachable_F06_classes"], 5)
        self.assertEqual(
            inventory["non_independent_defensive_reasons"],
            [
                "bundle taxonomy is unclassified",
                "filtered eligible total differs",
            ],
        )

    def test_generated_matrix_has_six_routes_and_twenty_four_paths(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(matrix["case_count"], 6)
        self.assertEqual(matrix["paths"], 24)
        self.assertEqual(matrix["VR20A_calls"], 24)
        self.assertEqual(matrix["each_route_count"], 4)
        self.assertEqual(
            [row["expected_route"] for row in matrix["cases"]],
            ["MARC2VR23A-G1"]
            + [f"MARC2VR23A-R{index}" for index in range(1, 6)],
        )
        self.assertTrue(matrix["source_objects_must_remain_byte_identical"])
        self.assertTrue(matrix["diagnostic_and_VR20A_routes_must_agree"])

    def test_caps_and_authority_are_strict(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 24 * 1024**2)
        self.assertLess(caps["peak_RSS_bytes"], 257 * 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        self.assertTrue(
            all(
                value is False
                for value in self.contract["authorization_state"].values()
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )

    def test_scientific_ceiling_remains_none(self):
        claim = self.contract["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        for key, value in claim.items():
            if key not in {"engineering_capability_sought", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
