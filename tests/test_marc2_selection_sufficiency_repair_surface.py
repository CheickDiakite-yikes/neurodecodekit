import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "neurodecodekit" / "datasets" / "marc2_selection_sufficiency_repair.py"


class Marc2SelectionSufficiencyRepairSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_import_surface_is_standard_library_plus_bound_local_modules(self):
        allowed_roots = {
            "argparse",
            "collections",
            "copy",
            "dataclasses",
            "hashlib",
            "json",
            "os",
            "pathlib",
            "resource",
            "sys",
            "time",
            "typing",
            "__future__",
            "neurodecodekit",
        }
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertLessEqual(imported, allowed_roots)

    def test_no_discovery_write_network_or_process_surface(self):
        forbidden_calls = {
            "glob",
            "rglob",
            "iterdir",
            "walk",
            "unlink",
            "rename",
            "replace",
            "write_bytes",
            "write_text",
            "open",
            "remove",
            "rmdir",
            "system",
            "popen",
        }
        observed = {
            node.func.attr
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertFalse(observed & forbidden_calls)

    def test_no_private_path_or_executor_constant(self):
        constants = {
            node.value
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        joined = "\n".join(constants)
        self.assertNotIn(".codex_work", joined)
        self.assertNotIn("/Users/", joined)
        self.assertNotIn("file://", joined)
        function_names = {
            node.name for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)
        }
        self.assertFalse(any("private" in name and "execute" in name for name in function_names))

    def test_only_parameter_free_plan_and_qualify_commands_exist(self):
        self.assertIn('choices=("plan", "qualify")', self.source)
        self.assertNotIn('choices=("plan", "qualify", "execute")', self.source)
        self.assertNotIn('add_argument("--', self.source)


if __name__ == "__main__":
    unittest.main()
