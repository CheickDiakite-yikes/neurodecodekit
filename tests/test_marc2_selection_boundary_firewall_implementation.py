import ast
import hashlib
import inspect
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_selection_boundary_firewall as firewall


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "src/neurodecodekit/datasets/marc2_selection_boundary_firewall.py"
)
CONTRACT_PATH = (
    ROOT / "registries/marc2_selection_boundary_firewall_contract.v0.json"
)


class Marc2SelectionBoundaryFirewallImplementationTests(unittest.TestCase):
    def test_contract_hash_and_green_registration_are_exact(self):
        self.assertEqual(
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
            firewall.CONTRACT_SHA256,
        )
        self.assertEqual(
            firewall.GREEN_REGISTRATION_COMMIT,
            "ad8be2197e58d4d3e0e1fe4f344de1c608930f73",
        )
        self.assertEqual(firewall.GREEN_REGISTRATION_CI_RUN_ID, 32_603_540_967)
        self.assertEqual(firewall.GREEN_REGISTRATION_BASE_JOB_ID, 97_105_227_375)
        self.assertEqual(
            firewall.GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            97_105_227_440,
        )

    def test_module_has_no_private_or_execution_surface(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        function_names = {
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        self.assertNotIn("execute", function_names)
        self.assertNotIn("_execute", function_names)
        self.assertNotIn("private", function_names)
        self.assertNotIn("download", function_names)
        parser_source = inspect.getsource(firewall._parser)
        self.assertIn('choices=("plan", "qualify", "inspect")', parser_source)
        self.assertNotIn("--source", parser_source)
        self.assertNotIn("--output", parser_source)
        self.assertNotIn("--url", parser_source.casefold())

    def test_frozen_upstream_modules_are_only_imported(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn("vr20a._group_rows", source)
        self.assertIn("vr2._filter_and_validate_eligible", source)
        self.assertIn("repair._select_from_filtered", source)
        self.assertIn("vr20a._validate_selection", source)

    def test_cli_refuses_generic_source_argument(self):
        with self.assertRaises(SystemExit):
            firewall.main(["plan", "--source", "/tmp/other"])

    def test_zero_counters_are_preserved(self):
        contract = firewall.load_registered_contract()
        self.assertTrue(all(value == 0 for value in contract["operation_counters"].values()))
        self.assertTrue(
            all(value is False for value in contract["authorization_state"].values())
        )


if __name__ == "__main__":
    unittest.main()
