from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_QUALIFICATION_AMENDMENT_2.md"
)
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_qualification_amendment_2.v0.json"
)


class CommunicationEEGProspectiveGeneratedQualificationAmendment2Tests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_parent_artifact_hashes_are_exact(self) -> None:
        for artifact in self.record["bound_parent_artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_proof_order_is_possible_without_network(self) -> None:
        defect = self.record["defect"]
        self.assertEqual(defect["generated_invocation_network_bytes_maximum"], 0)
        self.assertFalse(defect["same_invocation_remote_green_transition_possible"])
        correction = self.record["correction"]
        self.assertTrue(correction["activation_remotely_green_before_invocation"])
        self.assertTrue(
            correction[
                "generated_prediction_freeze_cryptographically_attested_before_target_descriptor_open"
            ]
        )
        self.assertFalse(
            correction["network_or_git_operation_inside_generated_invocation_allowed"]
        )
        self.assertTrue(
            correction["future_real_prediction_freeze_remotely_green_before_target_delivery"]
        )

    def test_all_seven_shortcut_fixtures_are_frozen(self) -> None:
        fixtures = self.record["shortcut_fixtures"]
        self.assertEqual(fixtures["executions_required"], 7)
        self.assertEqual(fixtures["positive"], ["residual_central_EEG"])
        self.assertEqual(
            fixtures["negative"],
            ["EOG", "oral_EMG", "microphone", "cue", "timing", "language"],
        )
        self.assertTrue(fixtures["negative_routes_must_fail_neural_evidence_gate"])
        self.assertFalse(fixtures["scientific_value"])

    def test_authority_and_claims_remain_closed(self) -> None:
        effect = self.record["effect"]
        self.assertTrue(
            effect[
                "generated_implementation_may_continue_after_this_amendment_is_remotely_green"
            ]
        )
        for key, value in effect.items():
            if key != "generated_implementation_may_continue_after_this_amendment_is_remotely_green":
                self.assertFalse(value, key)
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )
        claims = self.record["claim_boundary"]
        self.assertTrue(claims["generated_proof_order_ambiguity_resolved_prospectively"])
        for key, value in claims.items():
            if key != "generated_proof_order_ambiguity_resolved_prospectively":
                self.assertFalse(value, key)
        self.assertEqual(self.record["active_gate"]["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(self.record["active_gate"]["all_authority_flags_false"])

    def test_human_document_preserves_real_study_remote_green_rule(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("future real or human study", document)
        self.assertIn("separately committed, pushed, and remotely", document)
        self.assertIn("no scientific value", document)


if __name__ == "__main__":
    unittest.main()
