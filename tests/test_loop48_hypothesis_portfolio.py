import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "loop48_hypothesis_portfolio.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_48_TRAIN_ONLY_HYPOTHESIS_PORTFOLIO.md"


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


class Loop48HypothesisPortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_design_is_not_preregistered_or_authorized(self):
        self.assertEqual(
            self.registry["status"], "design_research_only_not_preregistered_or_authorized"
        )
        flags = authorization_flags(self.registry)
        self.assertEqual(len(flags), 11)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_five_hypotheses_are_unique_and_may_coexist(self):
        hypotheses = self.registry["hypotheses"]
        self.assertEqual(
            [row["hypothesis_id"] for row in hypotheses], ["H1", "H2", "H3", "H4", "H5"]
        )
        self.assertTrue(all(row["causal_status_now"] == "unresolved" for row in hypotheses))
        principles = self.registry["design_principles"]
        self.assertTrue(principles["hypotheses_may_coexist"])
        self.assertFalse(principles["forced_single_root_cause"])

    def test_parallel_science_is_sequential_compute(self):
        principles = self.registry["design_principles"]
        resources = self.registry["future_resource_boundary"]
        self.assertEqual(resources["current_portfolio_artifact_bytes"], 20377)
        self.assertTrue(principles["parallel_means_scientific_comparison_not_concurrent_compute"])
        self.assertTrue(principles["physical_compute_is_sequential"])
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["concurrent_numerical_jobs"], 1)

    def test_shared_measurements_cover_all_hypothesis_families(self):
        families = self.registry["shared_measurement_families"]
        self.assertEqual(len(families), 10)
        measurements = {
            value for row in self.registry["hypotheses"] for value in row["shared_measurements"]
        }
        for required in (
            "ctc_length_feasibility",
            "loss_trajectory",
            "line_noise_burden",
            "event_timing_residual",
            "simple_aligned_probe_metrics",
            "train_only_prior_metrics",
        ):
            self.assertIn(required, measurements)

    def test_future_split_is_train_only_and_exact_inventory_stays_unfrozen(self):
        split = self.registry["future_split_boundary"]
        self.assertIn("55", split["source_membership"])
        self.assertTrue(split["fit_and_check_rows_must_be_disjoint"])
        self.assertFalse(split["exact_counts_frozen"])
        self.assertFalse(split["exact_model_inventory_frozen"])
        for key in (
            "validation_rows_allowed",
            "source_test_rows_allowed",
            "session2_rows_allowed",
            "s7_s20_s25_allowed",
        ):
            self.assertFalse(split[key])

    def test_current_access_counters_are_zero(self):
        counters = self.registry["current_access_counters"]
        self.assertEqual(len(counters), 12)
        self.assertTrue(all(value == 0 for value in counters.values()), counters)

    def test_sources_and_claim_boundary_are_explicit(self):
        sources = self.registry["source_bindings"]
        self.assertEqual(len(sources), 5)
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        claim = self.registry["claim_boundary"]
        self.assertIn("shared train-only", claim["engineering_capability_proposed"])
        self.assertIn("No hypothesis", claim["scientific_claim_not_established"])

    def test_human_doc_preserves_multi_cause_and_authorization_boundaries(self):
        for phrase in (
            "parallel hypothesis portfolio",
            "not mean running workloads concurrently",
            "not mutually exclusive",
            "one-worker",
            "No validation targets",
            "authorizes nothing",
            "Stage B cannot inherit",
        ):
            self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
