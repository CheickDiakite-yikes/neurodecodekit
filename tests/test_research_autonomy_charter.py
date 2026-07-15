import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHARTER_PATH = REPO_ROOT / "docs" / "RESEARCH_AUTONOMY_CHARTER_DRAFT.md"


class ResearchAutonomyCharterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.charter = CHARTER_PATH.read_text(encoding="utf-8")
        cls.normalized = " ".join(cls.charter.split())

    def test_charter_is_explicitly_inactive(self):
        self.assertIn(
            "Draft for maintainer approval; this document grants no authorization",
            self.charter,
        )
        self.assertIn("becomes active only", self.charter)

    def test_three_tiers_separate_reversible_and_irreversible_work(self):
        for heading in (
            "Tier A - Autonomous Routine Work",
            "Tier B - Autonomous Bounded Development Experiments",
            "Tier C - Explicit One-Time Permission Still Required",
        ):
            self.assertIn(heading, self.charter)
        self.assertIn("A file can be restored; a held-out target cannot", self.normalized)

    def test_default_machine_envelope_is_conservative(self):
        for phrase in (
            "one CPU thread, one worker, and one numerical job at a time",
            "at most 1 GiB peak RSS",
            "at most 32 MiB of generated artifacts per loop",
            "no new real-data download",
            "free disk space would fall below 20 GiB",
        ):
            self.assertIn(phrase, self.charter)

    def test_irreversible_stops_cover_evidence_hardware_and_release(self):
        for phrase in (
            "first access to a new real participant signal",
            "held-out, final-only, source-test, or unseen-person evaluation",
            "reusing a consumed evaluation",
            "connecting hardware",
            "deleting data, rewriting history, merging, tagging, releasing",
        ):
            self.assertIn(phrase, self.charter)

    def test_approval_is_exact_and_nonretroactive(self):
        self.assertIn(
            "Authorize the NeuroDecodeKit Research Autonomy Charter dated 2026-07-15",
            self.charter,
        )
        for closed_scope in ("Loop 48 Stage B", "RW3", "S25"):
            self.assertIn(closed_scope, self.charter)


if __name__ == "__main__":
    unittest.main()
