import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_variable_width_run_index_repair as vr16a

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_f04_task_implication_contract.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_F04_TASK_IMPLICATION_PREREGISTRATION.md"
SOURCE_PATH = (
    ROOT / "src/neurodecodekit/datasets/marc2_variable_width_run_index_repair.py"
)


def _f04_references_in_validator() -> list[ast.Subscript]:
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_validate_variable_entry"
    )
    return [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "REFUSAL_ROUTES"
        and isinstance(node.slice, ast.Constant)
        and node.slice.value == 3
    ]


def _mutate_generated(case: str) -> dict:
    source = vr16a.build_generated_variant("three_digit", "canonical")
    if case.startswith("task_"):
        token = case.removeprefix("task_")
        for row in source["entries"]:
            name = row.get("member_name") if isinstance(row, dict) else None
            if isinstance(name, str):
                row["member_name"] = name.replace(
                    "_task-freewill_", f"_task-{token}_"
                )
        return source
    target = next(
        row
        for row in source["entries"]
        if isinstance(row, dict)
        and vr16a._variable_core_match(row.get("member_name", "")) is not None
    )
    if case == "subject_repeat_mismatch":
        target["member_name"] = target["member_name"].replace(
            "/eeg/sub-", "/eeg/sub-99", 1
        )
    elif case == "session_repeat_mismatch":
        target["member_name"] = target["member_name"].replace(
            "_ses-01_task-", "_ses-99_task-", 1
        )
    elif case == "subject_width_mismatch":
        target["member_name"] = target["member_name"].replace("sub-01", "sub-1", 1)
    else:
        raise ValueError("unknown generated case")
    return source


class Marc2F04TaskImplicationPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_predecessor_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR19A")
        proof = self.contract["predecessor_proof"]
        self.assertEqual(proof["consumed_route"], "MARC2VR18P-R4")
        self.assertEqual(
            proof["commit"], "7123bb2a00706de46e276f07e05ab3a619719226"
        )
        self.assertEqual(proof["CI_run_id"], 32_479_345_476)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["private_cohort_frozen"])

    def test_fixed_inputs_are_byte_exact(self):
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), self.contract["fixed_input_count"])
        self.assertEqual(
            sum(row["bytes"] for row in rows), self.contract["fixed_input_bytes"]
        )
        for row in rows:
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_ast_inventory_has_exactly_two_f04_validator_references(self):
        self.assertEqual(len(_f04_references_in_validator()), 2)
        inventory = self.contract["static_producer_inventory"]
        self.assertEqual(inventory["F04_producer_reference_count"], 2)
        self.assertTrue(
            inventory["exact_R4_pair_implies_nonfreewill_task_under_bound_source"]
        )

    def test_both_f04_references_are_task_inequality_guarded(self):
        source = SOURCE_PATH.read_text(encoding="utf-8")
        self.assertIn(
            'REFUSAL_ROUTES[3] if match.group("task") != "freewill"', source
        )
        self.assertIn('if match.group("task") != "freewill":', source)
        self.assertIn('REFUSAL_ROUTES[3], "Freewill task differs"', source)

    def test_generated_development_witnesses_have_frozen_evidence(self):
        expected = {
            "task_motor": ("MARC2VR16A-F04", "core identity differs"),
            "task_rest": ("MARC2VR16A-F04", "core identity differs"),
            "task_Freewill": ("MARC2VR16A-F04", "core identity differs"),
            "task_freewill2": ("MARC2VR16A-F04", "core identity differs"),
            "subject_repeat_mismatch": (
                "MARC2VR16A-F03",
                "suffix-bearing identity differs",
            ),
            "session_repeat_mismatch": (
                "MARC2VR16A-F03",
                "suffix-bearing identity differs",
            ),
            "subject_width_mismatch": (
                "MARC2VR16A-F03",
                "suffix-bearing identity differs",
            ),
        }
        for case, evidence in expected.items():
            source = _mutate_generated(case)
            before = copy.deepcopy(source)
            with self.subTest(case=case), self.assertRaises(
                vr16a.VariableWidthRunIndexRepairRefusal
            ) as caught:
                vr16a.adapt_variable_width_source(source)
            self.assertEqual((caught.exception.route, caught.exception.safe_reason), evidence)
            self.assertEqual(source, before)

    def test_generated_matrix_and_caps_are_exact(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(matrix["cases"], 8)
        self.assertEqual(matrix["paths"], 32)
        self.assertEqual(matrix["VR16A_calls"], 32)
        self.assertEqual(sum(matrix["expected_route_counts"].values()), 32)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 32 * 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)

    def test_authority_and_operation_counters_are_closed(self):
        authority = self.contract["authority"]
        self.assertTrue(authority["registration_only"])
        for key, value in authority.items():
            if key != "registration_only" and key != (
                "generated_implementation_allowed_after_exact_registration_remote_green"
            ):
                self.assertFalse(value, key)
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )
        self.assertIsNone(self.contract["remote_registration_proof"])

    def test_document_preserves_private_and_scientific_ceiling(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("non-`freewill` task class", text)
        self.assertIn("not guesses about the private source", text)
        self.assertIn("no neural payload", text)
        boundary = self.contract["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        self.assertFalse(boundary["private_task_value_known"])
        self.assertFalse(boundary["decoding_accuracy"])


if __name__ == "__main__":
    unittest.main()
