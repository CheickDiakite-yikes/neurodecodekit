import copy
import unittest
from pathlib import Path

from neurodecodekit.research.knowledge import (
    CLAIM_STATES,
    COORDINATE_FIELDS,
    KnowledgeLedgerError,
    build_research_update,
    load_scientific_ledger,
    summarize_scientific_ledger,
    validate_scientific_ledger,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/scientific_knowledge_ledger.v0.json"


class ScientificKnowledgeLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = load_scientific_ledger(REGISTRY, repository_root=ROOT)

    def test_identity_and_flagship_are_exact(self):
        self.assertEqual(
            self.ledger["schema_name"],
            "neurodecodekit.scientific_knowledge_ledger",
        )
        self.assertEqual(self.ledger["schema_version"], "0.1.0")
        self.assertEqual(self.ledger["flagship"]["experiment_id"], "EXP-DREYER-C5R-1")
        self.assertIn("fixed header", self.ledger["flagship"]["first_empirical_checkpoint"])

    def test_claims_have_valid_states_and_full_coordinates(self):
        for claim in self.ledger["claims"]:
            self.assertIn(claim["state"], CLAIM_STATES)
            self.assertEqual(set(claim["coordinates"]), set(COORDINATE_FIELDS))
            self.assertTrue(claim["unsupported"])

    def test_summary_keeps_science_and_authority_explicit(self):
        summary = summarize_scientific_ledger(self.ledger)
        self.assertEqual(summary["flagship_experiment_id"], "EXP-DREYER-C5R-1")
        self.assertEqual(summary["active_tier_c_packet"], "DREYER-C5R-1-HL")
        self.assertTrue(summary["all_authority_flags_false"])
        self.assertIn(
            "CLAIM-DREYER-NUISANCE-CONTROLLED-EEG",
            summary["unresolved_claim_ids"],
        )

    def test_operation_boundary_records_no_new_empirical_work(self):
        boundary = self.ledger["operation_boundary"]
        self.assertTrue(boundary["all_authority_flags_false"])
        for key, value in boundary.items():
            if key not in {"active_tier_c_packet", "all_authority_flags_false"}:
                self.assertEqual(value, 0, key)

    def test_two_scoreboards_remain_separate(self):
        scoreboards = self.ledger["scoreboards"]
        self.assertEqual(
            set(scoreboards),
            {"scientific_attribution", "functional_utility"},
        )
        attribution = {row["measure"] for row in scoreboards["scientific_attribution"]}
        utility = {row["measure"] for row in scoreboards["functional_utility"]}
        self.assertFalse(attribution & utility)

    def test_cycle_update_has_only_constitution_fields(self):
        update = build_research_update(self.ledger)
        self.assertEqual(
            set(update),
            {
                "scientific_question",
                "evidence_produced",
                "belief_changed",
                "uncertainty_remaining",
                "next_decisive_experiment",
                "infrastructure_created_and_why",
            },
        )
        self.assertIn("sub-01 R1 EDF", update["next_decisive_experiment"])

    def test_malformed_state_is_rejected(self):
        malformed = copy.deepcopy(self.ledger)
        malformed["claims"][0]["state"] = "GREAT_RESULT"
        with self.assertRaisesRegex(KnowledgeLedgerError, "state is unsupported"):
            validate_scientific_ledger(malformed)

    def test_dangling_evidence_is_rejected(self):
        malformed = copy.deepcopy(self.ledger)
        malformed["claims"][0]["evidence_ids"] = ["EVID-MISSING"]
        with self.assertRaisesRegex(KnowledgeLedgerError, "dangling evidence"):
            validate_scientific_ledger(malformed)

    def test_unsafe_or_nonpublic_evidence_path_is_rejected(self):
        unsafe = copy.deepcopy(self.ledger)
        unsafe["evidence"][0]["paths"] = ["../private/result.json"]
        with self.assertRaisesRegex(KnowledgeLedgerError, "repository-relative safe path"):
            validate_scientific_ledger(unsafe)

        nonpublic = copy.deepcopy(self.ledger)
        nonpublic["evidence"][0]["paths"] = ["private/result.json"]
        with self.assertRaisesRegex(KnowledgeLedgerError, "public evidence"):
            validate_scientific_ledger(nonpublic)

    def test_unknown_top_level_field_is_rejected(self):
        malformed = copy.deepcopy(self.ledger)
        malformed["narrative_escape_hatch"] = True
        with self.assertRaisesRegex(KnowledgeLedgerError, "unsupported fields"):
            validate_scientific_ledger(malformed)


if __name__ == "__main__":
    unittest.main()
