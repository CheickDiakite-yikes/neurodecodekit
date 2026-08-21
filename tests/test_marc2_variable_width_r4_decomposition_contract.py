import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_variable_width_r4_decomposition_contract.v0.json"
)


class Marc2VariableWidthR4DecompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_consumed_result_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR17A")
        observed = self.contract["observed_route_binding"]
        self.assertEqual(observed["VR15P_route"], "MARC2VR15P-R15")
        self.assertEqual(observed["VR16P_route"], "MARC2VR16P-R4")
        self.assertEqual(
            observed["VR16P_result_commit"],
            "a180b4646cfe5b301ce57677c40103842574d18e",
        )
        self.assertEqual(observed["VR16P_result_CI_run_id"], 32_466_008_062)
        self.assertTrue(observed["both_required_result_jobs_green"])

    def test_all_fixed_inputs_are_exact(self):
        fixed = self.contract["fixed_inputs"]
        self.assertEqual(len(fixed), self.contract["fixed_input_count"])
        self.assertEqual(sum(row["bytes"] for row in fixed), 204_240)
        for row in fixed:
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_static_F03_F05_inventory_matches_exact_module_calls(self):
        path = ROOT / "src/neurodecodekit/datasets/marc2_variable_width_run_index_repair.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = {
            "_canonical_run_token",
            "_validate_variable_entry",
            "_group_variable_rows",
        }
        observed = []
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or node.name not in functions:
                continue
            for child in ast.walk(node):
                if not isinstance(child, ast.Raise) or not isinstance(child.exc, ast.Call):
                    continue
                if getattr(child.exc.func, "id", None) != "VariableWidthRunIndexRepairRefusal":
                    continue
                observed.append(
                    {
                        "function": node.name,
                        "route_expression": ast.unparse(child.exc.args[0]),
                        "reason": ast.literal_eval(child.exc.args[1]),
                    }
                )
        expected = self.contract["F03_F05_static_call_sites"]
        self.assertEqual(len(observed), self.contract["static_call_site_count"])
        self.assertCountEqual(observed, expected)

    def test_composition_hypotheses_are_explicitly_unproven_at_registration(self):
        hypotheses = self.contract["composition_hypotheses"]
        self.assertEqual([row["id"] for row in hypotheses], [f"VR17A-H{i}" for i in range(1, 5)])
        self.assertTrue(all(row["must_be_generated_proven"] for row in hypotheses))
        self.assertIn("hypothesis", self.contract["warnings"][1].casefold())

    def test_four_residual_classes_and_matrix_are_frozen(self):
        residual = self.contract["residual_first_failure_classes"]
        self.assertEqual(
            [row["route"] for row in residual],
            [f"MARC2VR17A-R{i}" for i in range(1, 5)],
        )
        matrix = self.contract["generated_matrix"]
        self.assertEqual(matrix["equivalence_paths"], 24)
        self.assertEqual(matrix["residual_paths"], 20)
        self.assertEqual(matrix["total_VR15A_calls"], 24)
        self.assertEqual(matrix["total_VR16A_calls"], 44)
        self.assertEqual(matrix["residual_route_count_each"], 4)
        self.assertEqual(matrix["retained_generated_output_bytes"], 0)

    def test_resources_and_authority_fail_closed(self):
        caps = self.contract["resource_caps"]
        for key in ("CPU_threads", "workers", "numerical_jobs"):
            self.assertEqual(caps[key], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 40 * 1024**2)
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
