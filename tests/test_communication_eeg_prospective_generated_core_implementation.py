from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/communication_eeg_prospective_generated_core_implementation.v0.json"
DOCUMENT = ROOT / "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_CORE_IMPLEMENTATION.md"
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CommunicationEEGProspectiveGeneratedCoreImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_proof_barrier_and_artifact_hashes_are_exact(self) -> None:
        proof = self.record["green_registration_proof"]
        self.assertEqual(proof["commit"], "eafe1dfbcc300643c7638d0f01131f3bad2a1885")
        self.assertEqual(proof["CI_run_id"], 33_137_998_642)
        self.assertTrue(proof["both_required_jobs_green"])
        for artifact in self.record["artifacts"]:
            path = ROOT / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["bytes"], artifact["path"])
            self.assertEqual(_sha256(path), artifact["sha256"], artifact["path"])

    def test_core_is_present_but_full_runner_and_execution_remain_false(self) -> None:
        implemented = self.record["implemented_capabilities"]
        self.assertEqual(implemented["deterministic_structural_rows"], 10_752)
        self.assertEqual(implemented["synchronized_biosignal_roles"], 73)
        self.assertEqual(implemented["exact_refusal_families"], 70)
        self.assertTrue(implemented["activation_locked_official_qualify"])
        self.assertTrue(all(self.record["pending_full_implementation"].values()))
        official = self.record["official_qualification"]
        self.assertFalse(official["executed"])
        self.assertFalse(official["authorized_now"])
        self.assertEqual(official["invocations"], 0)

    def test_claim_and_operation_boundaries_remain_closed(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        self.assertTrue(all(value is False for value in self.record["claim_boundary"].values()))
        self.assertTrue(self.record["active_gate"]["sole_active_Tier_C_packet"])
        self.assertTrue(self.record["active_gate"]["all_authority_flags_false"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("does not yet contain the full 630-classifier", document)
        self.assertIn("Scientific claim not established", document)

    def test_frontier_routes_to_core_then_full_coordinator(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        generated = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["prospective_synchronized_cohort_preregistration"]["generated_qualification_registration"]
        # The parent field is an immutable historical registration snapshot.
        self.assertFalse(generated["implementation_authorized_now"])
        self.assertFalse(generated["execution_authorized_now"])
        core = generated["core_implementation"]
        self.assertFalse(core["full_compact_model_schedule_implemented"])
        self.assertFalse(core["two_isolated_registered_replays_implemented"])


if __name__ == "__main__":
    unittest.main()
