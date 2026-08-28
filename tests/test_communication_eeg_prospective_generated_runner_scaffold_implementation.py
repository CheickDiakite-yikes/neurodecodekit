from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_generated_runner_scaffold_implementation.v0.json"
)
DOCUMENT = ROOT / "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_RUNNER_SCAFFOLD_IMPLEMENTATION.md"
IMPLEMENTATION_COMMIT = "a961849761b4b734347ca1e83191008c69a7e897"
ARTIFACT_TABLE_SHA256 = "abd99ddbe8fe3b14da5c419ceda966534733c55464e509191ec83c6adb88d5cd"


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _historical_commit_is_available() -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{IMPLEMENTATION_COMMIT}^{{commit}}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


class CommunicationEEGProspectiveGeneratedRunnerScaffoldImplementationTest(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_prerequisite_and_exact_artifacts(self) -> None:
        green = self.record["green_prerequisite"]
        self.assertEqual(
            green["commit"], "c46064d19bd0ec74bc960d155ad9752989d9c54c"
        )
        self.assertEqual(green["CI_run_id"], 33_141_715_948)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertEqual(_canonical_sha256(self.record["artifacts"]), ARTIFACT_TABLE_SHA256)
        if not _historical_commit_is_available():
            return
        for artifact in self.record["artifacts"]:
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

    def test_reduced_measurement_is_bounded_and_nonofficial(self) -> None:
        measurement = self.record["development_measurement"]
        self.assertEqual(measurement["isolated_replays"], 2)
        self.assertEqual(measurement["structural_refusal_observations_total"], 140)
        self.assertEqual(measurement["post_target_updates"], 0)
        self.assertEqual(measurement["network_bytes"], 0)
        self.assertEqual(measurement["retained_generated_payload_bytes"], 0)
        self.assertLess(measurement["peak_process_tree_RSS_bytes"], 536_870_912)
        self.assertLess(measurement["private_generated_output_bytes"], 134_217_728)
        self.assertFalse(measurement["free_choice_primary_live_gate_passed"])
        self.assertFalse(measurement["prompted_may_rescue_free_choice"])

    def test_remaining_blockers_keep_official_path_closed(self) -> None:
        blockers = self.record["remaining_activation_blockers"]
        self.assertTrue(all(value is False for value in blockers.values()))
        official = self.record["official_qualification"]
        self.assertFalse(official["executed"])
        self.assertFalse(official["authorized_now"])
        self.assertFalse(official["activation_exists"])
        self.assertTrue(all(value is False for value in self.record["claim_boundary"].values()))

    def test_document_names_engineering_and_scientific_boundaries(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("scaffold, not the complete official coordinator", document)


if __name__ == "__main__":
    unittest.main()
