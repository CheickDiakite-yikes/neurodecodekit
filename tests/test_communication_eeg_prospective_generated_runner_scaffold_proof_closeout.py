from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_generated_runner_scaffold_proof_closeout.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_RUNNER_SCAFFOLD_PROOF_CLOSEOUT.md"
)
IMPLEMENTATION_COMMIT = "a961849761b4b734347ca1e83191008c69a7e897"


class CommunicationEEGProspectiveGeneratedRunnerScaffoldProofCloseoutTest(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_commit_and_jobs(self) -> None:
        green = self.record["green_implementation"]
        self.assertEqual(
            green["commit"], "a961849761b4b734347ca1e83191008c69a7e897"
        )
        self.assertEqual(green["CI_run_id"], 33_144_492_190)
        self.assertEqual(green["base_python_job_id"], 98_762_447_110)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98_762_446_873)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_bound_artifacts_are_exact(self) -> None:
        for artifact in self.record["bound_artifacts"]:
            payload = subprocess.check_output(
                ["git", "show", f"{IMPLEMENTATION_COMMIT}:{artifact['path']}"],
                cwd=ROOT,
            )
            self.assertEqual(len(payload), artifact["bytes"], artifact["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                artifact["sha256"],
                artifact["path"],
            )

    def test_closeout_performed_no_operation_or_claim_upgrade(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        self.assertTrue(all(value is False for value in self.record["official_qualification"].values()))
        self.assertTrue(all(value is False for value in self.record["claim_boundary"].values()))

    def test_document_preserves_both_boundaries(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("complete 42-person", document)


if __name__ == "__main__":
    unittest.main()
