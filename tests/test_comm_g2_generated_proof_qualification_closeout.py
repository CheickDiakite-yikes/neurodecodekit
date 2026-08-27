from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT = (
    ROOT
    / "registries"
    / "comm_g2_generated_proof_qualification_closeout.v0.json"
)
DOC = ROOT / "docs" / "COMM_G2_GENERATED_PROOF_QUALIFICATION_CLOSEOUT.md"
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"
INTENDED_RESULT = (
    ROOT / "registries" / "comm_g2_generated_proof_qualification_result.v0.json"
)


class CommG2GeneratedProofQualificationCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.closeout = json.loads(CLOSEOUT.read_text(encoding="utf-8"))

    def test_exact_green_implementation_is_bound(self) -> None:
        proof = self.closeout["implementation_green_proof"]
        self.assertEqual(
            proof["commit"], "83658976fb334a6b125a441af5dbc8cccf416e1f"
        )
        self.assertEqual(proof["CI_run_id"], 33056826167)
        self.assertEqual(proof["base_python_job_id"], 98465586781)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 98465586951)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_frozen_artifact_hashes_are_exact(self) -> None:
        for binding in self.closeout["frozen_bindings"].values():
            payload = (ROOT / binding["path"]).read_bytes()
            self.assertEqual(binding["bytes"], len(payload))
            self.assertEqual(binding["sha256"], hashlib.sha256(payload).hexdigest())

    def test_timeout_binds_R0_and_consumes_the_invocation(self) -> None:
        failure = self.closeout["observed_failure"]
        self.assertEqual(failure["refusal_id"], "G2-CHILD-TIMEOUT")
        self.assertEqual(failure["child_timeout_seconds"], 85)
        self.assertEqual(failure["completed_replay_records_returned_to_parent"], 0)
        self.assertFalse(failure["byte_equivalent_replay_proof_completed"])
        self.assertTrue(failure["cleanup_completed"])
        self.assertFalse(INTENDED_RESULT.exists())

        router = self.closeout["binding_router"]
        self.assertEqual(router["route"], "COMM-G2-R0")
        self.assertFalse(router["accepted_generated_score"])
        consumption = self.closeout["consumption"]
        self.assertEqual(consumption["official_invocations"], 1)
        self.assertTrue(consumption["consumed"])
        self.assertFalse(consumption["rerun_allowed"])
        self.assertFalse(consumption["repair_in_place_allowed"])

    def test_unknown_failure_metrics_are_not_fabricated_as_zero(self) -> None:
        values = self.closeout["unavailable_measurements"]
        for key, value in values.items():
            if key != "reason":
                self.assertIsNone(value)
        self.assertEqual(
            self.closeout["network_accounting"]["dataset_or_provider_payload_bytes"],
            0,
        )
        self.assertIsNone(
            self.closeout["network_accounting"]["remote_CI_proof_metadata_bytes"]
        )

    def test_real_counters_and_claims_remain_zero_or_false(self) -> None:
        self.assertTrue(all(value == 0 for value in self.closeout["access_counters"].values()))
        self.assertTrue(all(value is False for value in self.closeout["claim_boundary"].values()))
        gate = self.closeout["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(gate["all_authority_flags_false"])

    def test_document_is_plain_about_failure_and_no_rerun(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in (
            "G2-CHILD-TIMEOUT",
            "published no official qualification result",
            "COMM-G2-R0",
            "may not be rerun",
            "are therefore unavailable",
            "No real EEG or MEG was accessed",
        ):
            self.assertIn(phrase, normalized)

    def test_frontier_preserves_real_gate_and_closes_G2(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        successor = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["generated_proof_successor_preregistration"]
        self.assertEqual(successor["status"], "consumed_parked_COMM_G2_R0_no_rerun")
        self.assertEqual(successor["binding_closeout_route"], "COMM-G2-R0")
        self.assertFalse(successor["rerun_allowed"])
        self.assertEqual(frontier["active_lane_id"], "DREYER-C5R-1-HL")


if __name__ == "__main__":
    unittest.main()
