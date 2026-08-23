import ast
import hashlib
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    marc2_r1_eligible_total_direction_discriminator as subject,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE = (
    ROOT
    / "src/neurodecodekit/datasets/marc2_r1_eligible_total_direction_discriminator.py"
)
CONTRACT = (
    ROOT
    / "registries/marc2_r1_eligible_total_direction_discriminator_contract.v0.json"
)


class Marc2R1EligibleTotalDirectionDiscriminatorImplementationTests(
    unittest.TestCase
):
    def test_registration_proof_and_contract_hash_are_exact(self):
        self.assertEqual(
            subject.GREEN_REGISTRATION_COMMIT,
            "eeab6785b8eadc6d65199fa1ac519173f9c160c7",
        )
        self.assertEqual(subject.GREEN_REGISTRATION_CI_RUN_ID, 32_626_878_097)
        self.assertEqual(subject.GREEN_REGISTRATION_BASE_JOB_ID, 97_163_443_088)
        self.assertEqual(
            subject.GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            97_163_443_152,
        )
        self.assertEqual(
            hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            subject.CONTRACT_SHA256,
        )

    def test_module_uses_only_standard_library_and_local_helpers(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        allowed = {
            "__future__",
            "argparse",
            "ast",
            "collections",
            "copy",
            "hashlib",
            "json",
            "neurodecodekit",
            "os",
            "pathlib",
            "resource",
            "sys",
            "time",
            "typing",
        }
        self.assertLessEqual(roots, allowed)

    def test_module_has_no_private_executor_or_override_surface(self):
        source = MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        self.assertNotIn("execute", functions)
        self.assertNotIn("execute_fixed", functions)
        self.assertNotIn("inspect", functions)
        self.assertNotIn(".codex_work", source)
        parser_source = ast.get_source_segment(
            source,
            next(
                node
                for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == "_parser"
            ),
        )
        self.assertIn('choices=("plan", "qualify")', parser_source)
        for forbidden in (
            "--source",
            "--output",
            "--threshold",
            "--retry",
            "--url",
        ):
            self.assertNotIn(forbidden, parser_source)

    def test_direction_function_returns_routes_only(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_direction_from_generated_source"
        )
        returned_names = {
            node.value.id
            for node in ast.walk(function)
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Name)
        }
        self.assertEqual(
            returned_names,
            {"BELOW_EXPECTED_ROUTE", "ABOVE_EXPECTED_ROUTE"},
        )

    def test_plan_preserves_scientific_ceiling(self):
        plan = subject.build_plan()
        self.assertFalse(plan["private_executor_available"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])
        self.assertEqual(plan["scientific_ceiling"], "none")


if __name__ == "__main__":
    unittest.main()
