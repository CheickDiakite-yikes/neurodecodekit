import inspect
import unittest
from pathlib import Path


class Loop26SharedValidationImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.doc = (cls.root / "docs" / "LOOP_26_SHARED_VALIDATION_IMPLEMENTATION.md").read_text(
            encoding="utf-8"
        )
        cls.gate_source = (
            cls.root / "src" / "neurodecodekit" / "experiments" / "shared_s21_validation_gate.py"
        ).read_text(encoding="utf-8")

    def test_document_preserves_pre_access_and_claim_boundaries(self):
        normalized = " ".join(self.doc.split()).casefold()
        for phrase in (
            "protected access must wait",
            "No real cache stat, hash, member, signal, or target value was read",
            "Scientific claim not established",
            "no neural advantage",
            "source-test rows, session 2",
        ):
            self.assertIn(phrase.casefold(), normalized)

    def test_gate_does_not_use_legacy_full_array_loader(self):
        self.assertNotIn("load_sentence_npz_cache", self.gate_source)
        self.assertNotIn("np.load(cache_path", self.gate_source)

    def test_target_blind_signature_cannot_receive_validation_targets(self):
        from neurodecodekit.experiments.shared_s21_validation_gate import (
            run_target_blind_shared_s21_gate,
        )

        parameters = inspect.signature(run_target_blind_shared_s21_gate).parameters
        self.assertNotIn("targets", parameters)
        self.assertNotIn("validation_targets", parameters)

    def test_required_stages_and_exact_inventory_are_implemented(self):
        for name in (
            "run_static_shared_s21_gate",
            "create_shared_s21_derivatives",
            "run_target_blind_shared_s21_gate",
            "score_frozen_shared_s21_validation",
            "EXACT_TARGET_BLIND_COUNTERS",
        ):
            self.assertIn(name, self.gate_source)
        for value in ("5040", "31", "24", "21"):
            self.assertIn(value, self.gate_source)

    def test_heavy_imports_are_function_local(self):
        top_level = self.gate_source.split("def _environment_versions", 1)[0]
        self.assertNotIn("\nimport numpy", top_level)
        self.assertNotIn("\nimport scipy", top_level)
        self.assertNotIn("\nimport torch", top_level)


if __name__ == "__main__":
    unittest.main()
