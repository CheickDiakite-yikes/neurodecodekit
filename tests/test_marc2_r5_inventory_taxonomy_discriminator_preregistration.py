import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_r5_inventory_taxonomy_discriminator_contract.v0.json"
)
VR25A_PATH = (
    ROOT / "src/neurodecodekit/datasets/marc2_selection_boundary_firewall.py"
)


class Marc2R5InventoryTaxonomyDiscriminatorPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_result_proof_is_bound(self):
        proof = self.contract["result_proof"]
        self.assertEqual(
            proof["VR26P_result_commit"],
            "878148a7adaede8d871f181ad535a2c730a86f93",
        )
        self.assertEqual(proof["VR26P_result_CI_run_id"], 32_610_456_792)
        self.assertEqual(proof["VR26P_result_base_job_id"], 97_122_530_294)
        self.assertEqual(
            proof["VR26P_result_optional_neuro_job_id"], 97_122_530_346
        )
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["observed_route"], "MARC2VR26P-R5")
        self.assertFalse(proof["private_source_reinspected_by_registration"])

    def test_fixed_inputs_are_byte_exact(self):
        self.assertEqual(len(self.contract["fixed_inputs"]), 9)
        self.assertEqual(
            sum(item["bytes"] for item in self.contract["fixed_inputs"]),
            self.contract["fixed_input_bytes"],
        )
        for item in self.contract["fixed_inputs"]:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(payload), item["bytes"], item["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                item["sha256"],
                item["path"],
            )

    def test_ast_inventory_binds_one_r1_and_one_r2_site(self):
        tree = ast.parse(VR25A_PATH.read_text(encoding="utf-8"))
        counts = {"MARC2VR25A-R1": 0, "MARC2VR25A-R2": 0}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if (
                not isinstance(node.func, ast.Name)
                or node.func.id != "SelectionBoundaryFirewallRefusal"
                or not node.args
            ):
                continue
            route = node.args[0]
            if isinstance(route, ast.Constant) and route.value in counts:
                counts[route.value] += 1
        self.assertEqual(counts, {"MARC2VR25A-R1": 1, "MARC2VR25A-R2": 1})
        inventory = self.contract["ordered_route_inventory"]
        self.assertEqual(inventory["VR25A_R1"]["exact_call_sites"], 1)
        self.assertEqual(inventory["VR25A_R2"]["exact_call_sites"], 1)
        self.assertEqual(self.contract["exact_R1_R2_call_site_total"], 2)

    def test_matrix_and_routes_are_frozen(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(matrix["required_paths"], 20)
        self.assertEqual(matrix["required_VR25A_calls"], 20)
        self.assertEqual(
            matrix["expected_VR27A_route_counts"],
            {
                "MARC2VR27A-G1": 4,
                "MARC2VR27A-R1": 12,
                "MARC2VR27A-R2": 4,
            },
        )
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 50)
        self.assertEqual(
            [item["expected_VR25A_route"] for item in matrix["cases"]],
            [
                "MARC2VR25A-G1",
                "MARC2VR25A-R1",
                "MARC2VR25A-R1",
                "MARC2VR25A-R1",
                "MARC2VR25A-R2",
            ],
        )

    def test_registration_authorizes_no_private_or_scientific_work(self):
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["artifact_only_reads"])
        self.assertTrue(authorization["generated_fixture_creation"])
        for key, value in authorization.items():
            if key not in {"artifact_only_reads", "generated_fixture_creation"}:
                self.assertIn(value, (0, False), key)
        self.assertTrue(
            all(
                value == 0
                for value in self.contract[
                    "registration_operation_counters"
                ].values()
            )
        )
        claims = self.contract["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability_if_passed", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
