import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class Loop48StageBImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = (REPO_ROOT / "docs" / "LOOP_48_STAGE_B_IMPLEMENTATION.md").read_text(
            encoding="utf-8"
        )
        cls.evaluation = (
            REPO_ROOT
            / "src"
            / "neurodecodekit"
            / "evaluation"
            / "train_only_failure_discrimination.py"
        ).read_text(encoding="utf-8")
        cls.gate = (
            REPO_ROOT
            / "src"
            / "neurodecodekit"
            / "experiments"
            / "train_only_failure_discrimination_gate.py"
        ).read_text(encoding="utf-8")

    def test_implementation_files_and_staged_api_exist(self):
        self.assertIn("def diagnostic_split(", self.evaluation)
        self.assertIn("def validate_prediction_freeze_record(", self.evaluation)
        self.assertIn("def score_failure_discrimination(", self.evaluation)
        for function in (
            "run_static_stage_b_gate",
            "create_stage_b_derivatives",
            "run_target_blind_stage_b_gate",
            "score_frozen_stage_b",
        ):
            self.assertIn(f"def {function}(", self.gate)

    def test_doc_discloses_inventory_gates_resources_and_claim_ceiling(self):
        normalized = " ".join(self.doc.casefold().split())
        for phrase in (
            "implemented and synthetic-tested; protected execution has not started",
            "44/11",
            "20 parameterized + 5 priors",
            "41",
            "35",
            "4,800",
            "2^11 = 2,048",
            "20 gib",
            "32 mib",
            "all 55 rows were used by historical loop 26 fits",
            "upstream sentence cache is offline/noncausal",
            "scientific claim not established",
        ):
            self.assertIn(phrase, normalized)

    def test_doc_keeps_protected_execution_and_claims_closed(self):
        normalized = self.doc.casefold()
        self.assertIn("no registered cache", normalized)
        self.assertIn("check targets sealed", normalized)
        self.assertIn("not independent validation", normalized)
        self.assertIn("do not establish a stage b result", normalized)


if __name__ == "__main__":
    unittest.main()
