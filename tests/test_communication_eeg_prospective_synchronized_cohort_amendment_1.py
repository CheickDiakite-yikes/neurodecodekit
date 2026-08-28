from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARENT_DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_SYNCHRONIZED_COHORT_PREREGISTRATION.md"
)
PARENT_CONTRACT = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_synchronized_cohort_contract.v0.json"
)
AMENDMENT_DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_SYNCHRONIZED_COHORT_AMENDMENT_1.md"
)
AMENDMENT = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_synchronized_cohort_amendment_1.v0.json"
)


class CommunicationEEGProspectiveSynchronizedCohortAmendment1Tests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))
        cls.parent = json.loads(PARENT_CONTRACT.read_text(encoding="utf-8"))

    def test_defect_and_authoritative_correction_are_exact(self) -> None:
        defect = self.amendment["defect"]
        self.assertEqual(defect["human_document_value"], 0.60)
        self.assertEqual(defect["machine_contract_value"], 0.70)
        self.assertEqual(defect["contract_test_value"], 0.70)
        correction = self.amendment["correction"]
        self.assertEqual(
            correction["authoritative_stable_commit_coverage_fraction_minimum"],
            0.70,
        )
        self.assertFalse(correction["post_result_threshold_selection_allowed"])

    def test_parent_machine_contract_already_uses_seventy_percent(self) -> None:
        self.assertEqual(
            self.parent["live_endpoint"][
                "stable_commit_coverage_fraction_minimum"
            ],
            0.70,
        )
        human = PARENT_DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Stable-commit coverage must reach 60%", human)
        amendment = AMENDMENT_DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("authoritative minimum is **70%**", amendment)

    def test_scope_is_one_field_and_every_operation_remains_closed(self) -> None:
        correction = self.amendment["correction"]
        self.assertTrue(
            correction["parent_human_60_percent_sentence_superseded_for_this_field_only"]
        )
        self.assertTrue(correction["all_other_parent_fields_unchanged"])
        effect = self.amendment["effect"]
        self.assertTrue(
            effect[
                "generated_qualification_design_paused_until_amendment_and_proof_closeout_green"
            ]
        )
        self.assertTrue(
            all(
                value is False
                for key, value in effect.items()
                if key
                != "generated_qualification_design_paused_until_amendment_and_proof_closeout_green"
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.amendment["operation_counters"].values())
        )

    def test_claim_boundary_and_active_gate_are_honest(self) -> None:
        claims = self.amendment["claim_boundary"]
        self.assertTrue(claims["engineering_threshold_ambiguity_resolved_prospectively"])
        for key, value in claims.items():
            if key != "engineering_threshold_ambiguity_resolved_prospectively":
                self.assertFalse(value, key)
        self.assertEqual(self.amendment["active_gate"]["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(self.amendment["active_gate"]["all_authority_flags_false"])


if __name__ == "__main__":
    unittest.main()
