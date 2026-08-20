import ast
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_r4_residual_decomposition_contract.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_R4_RESIDUAL_DECOMPOSITION_PREREGISTRATION.md"
REPAIR_PATH = ROOT / "src/neurodecodekit/datasets/marc2_p15_run_index_repair.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _f01_f06_refusal_inventory() -> dict[int, set[str]]:
    tree = ast.parse(REPAIR_PATH.read_text(encoding="utf-8"))
    selected_functions = {
        "_registered_contract_bytes",
        "load_registered_contract",
        "_verify_contract_mapping",
        "_verify_registration_proof",
        "_validate_repaired_entry",
        "_group_repaired_rows",
        "_validate_and_filter",
    }
    inventory = {index: set() for index in range(6)}
    for function in (
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in selected_functions
    ):
        for node in ast.walk(function):
            if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
                continue
            call = node.exc
            if not isinstance(call.func, ast.Name) or call.func.id != "P15RunIndexRepairRefusal":
                continue
            if len(call.args) < 2 or not isinstance(call.args[0], ast.Subscript):
                continue
            route = call.args[0]
            if not isinstance(route.value, ast.Name) or route.value.id != "REFUSAL_ROUTES":
                continue
            index_node = route.slice
            reason_node = call.args[1]
            if not isinstance(index_node, ast.Constant) or not isinstance(index_node.value, int):
                continue
            if not isinstance(reason_node, ast.Constant) or not isinstance(reason_node.value, str):
                continue
            if index_node.value in inventory:
                inventory[index_node.value].add(reason_node.value)
    return inventory


class Marc2R4ResidualDecompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_identity_and_scope_are_exact(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_r4_residual_decomposition_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR13A")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )

    def test_every_fixed_input_is_exact(self):
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), self.contract["fixed_input_count"])
        self.assertEqual(sum(row["bytes"] for row in rows), self.contract["fixed_input_bytes"])
        self.assertEqual(len({row["path"] for row in rows}), len(rows))
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertNotIn(".codex_work", row["path"])

    def test_consumed_route_and_same_registered_source_are_bound_without_access(self):
        observed = self.contract["observed_route_binding"]
        self.assertEqual(observed["VR11P_route"], "MARC2VR11P-R2")
        self.assertEqual(observed["VR12P_route"], "MARC2VR12P-R4")
        self.assertTrue(observed["same_registered_source_identity"])
        self.assertEqual(observed["registered_source_bytes"], 418_755)
        self.assertFalse(observed["private_source_opened_by_registration"])
        self.assertFalse(observed["private_failure_value_available"])

    def test_static_AST_inventory_matches_all_23_f01_f06_call_sites(self):
        expected = {
            int(key.removeprefix("F")) - 1: set(value)
            for key, value in self.contract["F01_F06_safe_reason_inventory"].items()
        }
        observed = _f01_f06_refusal_inventory()
        self.assertEqual(observed, expected)
        self.assertEqual(sum(len(values) for values in observed.values()), 23)

    def test_partition_keeps_exactly_seven_ordered_residual_classes(self):
        partition = self.contract["residual_first_failure_classes"]
        self.assertEqual(len(partition), 7)
        self.assertEqual(
            [row["route"] for row in partition],
            [f"MARC2VR13A-R{index}" for index in range(1, 8)],
        )
        self.assertTrue(all(row["private_observation"] is False for row in partition))
        excluded = self.contract["excluded_classes"]
        self.assertEqual([row["VR12A_route"] for row in excluded[:2]], ["F01", "F02"])
        self.assertTrue(all(row["private_observation"] is False for row in excluded))

    def test_generated_matrix_is_complete_ordered_and_replayed(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(len(matrix["cases"]), 8)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 32)
        self.assertEqual(matrix["required_VR12A_calls"], 32)
        self.assertEqual(matrix["route_count_each"], 4)
        self.assertEqual(
            [row["expected_VR13A_route"] for row in matrix["cases"]],
            ["MARC2VR13A-G1"]
            + [f"MARC2VR13A-R{index}" for index in range(1, 8)],
        )

    def test_resources_and_direct_refusal_floor_are_bounded(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertLessEqual(caps["runtime_seconds"], 30)
        self.assertLessEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(caps["generated_input_bytes"], 24 * 1024**2)
        self.assertLessEqual(caps["aggregate_output_bytes"], 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        self.assertEqual(caps["private_or_Git_ignored_bytes"], 0)
        self.assertGreaterEqual(self.contract["direct_refusal_minimum"], 50)

    def test_authority_and_operation_counters_remain_closed(self):
        self.assertTrue(
            all(value is False for value in self.contract["authorization_state"].values())
        )
        self.assertTrue(all(value == 0 for value in self.contract["operation_counters"].values()))
        gate = self.contract["next_gate"]
        self.assertTrue(gate["generated_implementation_allowed_after_registration_green"])
        self.assertFalse(gate["private_read_or_real_executor_allowed"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_allowed"])

    def test_registration_artifacts_are_hash_bound(self):
        artifacts = self.contract["registration_artifacts"]
        self.assertEqual(_sha256(ROOT / artifacts["document_path"]), artifacts["document_sha256"])
        self.assertEqual(_sha256(ROOT / artifacts["test_path"]), artifacts["test_sha256"])

    def test_human_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability sought:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("MARC2VR12P-R4", text)
        self.assertIn("no private access", text.lower())
        self.assertIn("new Tier C decision", text)


if __name__ == "__main__":
    unittest.main()
