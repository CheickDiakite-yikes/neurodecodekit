import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_r5_two_route_discriminator_contract.v0.json"
VR20A_PATH = ROOT / "src/neurodecodekit/datasets/marc2_published_task_selector_repair.py"


class Marc2R5TwoRouteDiscriminatorPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_result_proof_is_bound(self):
        proof = self.contract["result_proof"]
        self.assertEqual(
            proof["VR20P_result_commit"],
            "a7e2ccee7cd073844da52b7c11a603360aae7b88",
        )
        self.assertEqual(proof["VR20P_result_CI_run_id"], 32_558_830_891)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["observed_route"], "MARC2VR20P-R5")
        self.assertFalse(proof["private_source_reinspected_by_registration"])

    def test_fixed_inputs_are_byte_exact(self):
        self.assertEqual(len(self.contract["fixed_inputs"]), 11)
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

    def test_ast_inventory_binds_two_f06_and_nine_f07_sites(self):
        tree = ast.parse(VR20A_PATH.read_text(encoding="utf-8"))
        counts = {5: 0, 6: 0}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if (
                not isinstance(node.func, ast.Name)
                or node.func.id != "PublishedTaskSelectorRepairRefusal"
                or not node.args
            ):
                continue
            route = node.args[0]
            if (
                isinstance(route, ast.Subscript)
                and isinstance(route.value, ast.Name)
                and route.value.id == "REFUSAL_ROUTES"
                and isinstance(route.slice, ast.Constant)
                and route.slice.value in counts
            ):
                counts[route.slice.value] += 1
        self.assertEqual(counts, {5: 2, 6: 9})
        inventory = self.contract["ordered_route_inventory"]
        self.assertEqual(inventory["VR20A_F06"]["exact_call_sites"], 2)
        self.assertEqual(inventory["VR20A_F07"]["exact_call_sites"], 9)
        self.assertEqual(self.contract["exact_F06_F07_call_site_total"], 11)

    def test_matrix_and_routes_are_frozen(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(matrix["required_paths"], 12)
        self.assertEqual(matrix["required_VR20A_calls"], 12)
        self.assertEqual(matrix["route_count_each"], 4)
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 40)
        self.assertEqual(
            [item["expected_VR21A_route"] for item in matrix["cases"]],
            ["MARC2VR21A-G1", "MARC2VR21A-R1", "MARC2VR21A-R2"],
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
