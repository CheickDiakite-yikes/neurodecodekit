import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = (
    ROOT
    / "src"
    / "neurodecodekit"
    / "datasets"
    / "marc2_selection_sufficiency_private_cohort_freeze.py"
)


class SelectionSufficiencyPrivateCohortFreezeSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_import_surface_is_standard_library_plus_two_bound_modules(self):
        allowed_roots = {
            "__future__",
            "argparse",
            "collections",
            "copy",
            "dataclasses",
            "hashlib",
            "hmac",
            "json",
            "neurodecodekit",
            "os",
            "pathlib",
            "resource",
            "secrets",
            "shutil",
            "stat",
            "sys",
            "tempfile",
            "time",
            "typing",
        }
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertLessEqual(imported, allowed_roots)

    def test_no_network_process_provider_or_model_surface(self):
        forbidden_roots = {
            "httpx",
            "requests",
            "socket",
            "subprocess",
            "torch",
            "transformers",
            "urllib",
        }
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertFalse(imports & forbidden_roots)
        self.assertNotIn("OPENAI_API_KEY", self.source)
        self.assertNotIn("huggingface", self.source.casefold())

    def test_fixed_paths_and_parameter_free_commands_are_exact(self):
        self.assertIn(
            ".codex_work/marc2_selection_sufficiency_private_cohort_freeze/v0",
            self.source,
        )
        self.assertIn('for command in ("plan", "qualify", "inspect", "execute")', self.source)
        self.assertNotIn('add_argument("--', self.source)
        self.assertNotIn("http://", self.source)
        self.assertNotIn("https://", self.source)
        self.assertNotIn("/Users/", self.source)

    def test_only_vr33a_and_vr38a_are_direct_dataset_imports(self):
        imports = {
            alias.asname
            for node in ast.walk(self.tree)
            if isinstance(node, ast.ImportFrom) and node.module == "neurodecodekit.datasets"
            for alias in node.names
        }
        self.assertEqual(imports, {"vr33a", "vr38a"})


if __name__ == "__main__":
    unittest.main()
