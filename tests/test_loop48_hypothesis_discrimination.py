import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "loop48_hypothesis_discrimination.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_48_HYPOTHESIS_DISCRIMINATION_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop48HypothesisDiscriminationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_design_remains_unpreregistered_and_unauthorized(self):
        self.assertEqual(
            self.registry["status"],
            "design_research_only_not_preregistered_or_authorized",
        )
        flags = authorization_flags(self.registry)
        self.assertEqual(len(flags), 15)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_green_inputs_are_hash_bound_without_mutation(self):
        binding = self.registry["additive_to_green_portfolio"]
        for path_key, hash_key in (
            ("portfolio_path", "portfolio_sha256"),
            ("portfolio_doc_path", "portfolio_doc_sha256"),
            ("stage_a_contract_path", "stage_a_contract_sha256"),
        ):
            payload = (REPO_ROOT / binding[path_key]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), binding[hash_key])
        self.assertFalse(binding["mutates_stage_a_request"])
        self.assertFalse(binding["authorizes_stage_a_or_stage_b"])

    def test_six_hypotheses_are_unique_coexisting_and_unresolved(self):
        rows = self.registry["hypotheses"]
        self.assertEqual(
            [row["hypothesis_id"] for row in rows],
            ["H1", "H2", "H3", "H4", "H5", "H6"],
        )
        self.assertTrue(all(row["causal_status_now"] == "unresolved" for row in rows))
        self.assertTrue(self.registry["design_corrections"]["hypotheses_may_coexist"])
        self.assertFalse(self.registry["design_corrections"]["forced_single_winner"])

    def test_h1_and_h6_fix_the_two_scientific_ambiguities(self):
        rows = {row["hypothesis_id"]: row for row in self.registry["hypotheses"]}
        self.assertIn("fixed_tiny_ctc_recipe", rows["H1"]["label"])
        self.assertIn("not that CTC is unsuitable", rows["H1"]["maximum_claim"])
        self.assertIn("sentence_diversity", rows["H6"]["label"])
        self.assertIn("55-row", rows["H6"]["maximum_claim"])
        self.assertIn("unique-sentence", rows["H6"]["smallest_falsifier"])

    def test_evidence_ladder_caps_stage_b_below_brain_origin(self):
        levels = [row["level"] for row in self.registry["evidence_levels"]]
        self.assertEqual(levels, ["E0", "E1", "E2", "E3", "E4"])
        self.assertEqual(self.registry["current_evidence_ceiling"], "E1")
        self.assertEqual(self.registry["future_stage_b_ceiling"], "E3")
        e3 = self.registry["evidence_levels"][3]["maximum_wording"]
        self.assertIn("preregistered practical margin", e3)
        self.assertIn("paired uncertainty gate", e3)
        threat = self.registry["orthogonal_claim_threat"]
        self.assertEqual(threat["threat_id"], "T1")
        self.assertEqual(threat["route"], "Loop_35_peripheral_confound_firewall")
        self.assertFalse(threat["stage_b_can_clear_threat"])
        self.assertFalse(threat["brain_specific_claim_allowed"])

    def test_sequential_stage_map_reuses_shared_evidence(self):
        stages = self.registry["future_discrimination_stages"]
        self.assertEqual([row["stage_id"] for row in stages], ["D0", "D1", "D2", "D3", "D4", "D5"])
        self.assertEqual(stages[0]["status"], "stage_a_requested_not_authorized")
        self.assertTrue(all(row["status"] == "not_preregistered" for row in stages[1:]))
        corrections = self.registry["design_corrections"]
        self.assertFalse(corrections["parallel_science_means_concurrent_compute"])
        self.assertEqual(corrections["cpu_threads"], 1)
        self.assertEqual(corrections["workers"], 1)
        self.assertEqual(corrections["concurrent_numerical_jobs"], 1)
        self.assertEqual(len(self.registry["shared_evidence_families"]), 12)

    def test_non_identifiability_and_unfrozen_fields_are_explicit(self):
        self.assertEqual(len(self.registry["non_identifiability_rules"]), 5)
        self.assertEqual(len(self.registry["future_unfrozen_fields"]), 7)
        joined = " ".join(self.registry["non_identifiability_rules"])
        self.assertIn("blank_dominance_alone", joined)
        self.assertIn("brain_specific_origin", joined)

    def test_only_public_research_activity_is_nonzero(self):
        counters = self.registry["current_activity_counters"]
        self.assertEqual(counters["public_primary_source_documents_consulted"], 5)
        self.assertEqual(counters["public_source_research_passes"], 1)
        protected = {
            key: value
            for key, value in counters.items()
            if key
            not in {
                "public_primary_source_documents_consulted",
                "public_source_research_passes",
            }
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_primary_sources_and_human_claim_boundaries_are_complete(self):
        sources = self.registry["source_bindings"]
        self.assertEqual(len(sources), 5)
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        for phrase in (
            "six coexisting failure hypotheses",
            "Why `H6` Must Be Separate",
            "one-threaded",
            "Non-Identifiability Rules",
            "Orthogonal Claim Threat `T1`",
            "authorizes nothing",
            "Stage A authorization cannot",
            "Scientific claim not established",
        ):
            self.assertIn(phrase, self.doc)

    def test_scientific_roadmap_points_to_additive_design_without_authorizing_it(self):
        roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        loop48 = next(row for row in roadmap["loops"] if row["loop_id"] == 48)
        self.assertFalse(loop48["execution_authorized"])
        self.assertIn(
            "loop48_hypothesis_discrimination.v0.json",
            loop48["build_deliverable"],
        )
        self.assertIn(
            "unable to inherit Stage A authorization",
            loop48["authorization_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
