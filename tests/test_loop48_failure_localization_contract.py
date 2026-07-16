import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_failure_localization_contract.v0.json"
CONTRACT_SHA256 = "ecd226f8ae8892e40ecd65c25d59e000384289e9c434886db71dabcfde9e31b1"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_48_PRIMARY_SOURCE_RESEARCH.md"
RESULT_PATH = REPO_ROOT / "registries" / "loop26_shared_validation_result.v0.json"
SCIENTIFIC_ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
)


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


class Loop48FailureLocalizationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.roadmap = json.loads(SCIENTIFIC_ROADMAP_PATH.read_text(encoding="utf-8"))

    def test_contract_is_post_outcome_and_every_authorization_is_false(self):
        self.assertEqual(hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(), CONTRACT_SHA256)
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.loop48_failure_localization_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["status"], "preregistered_authorization_pending")
        self.assertIn("post_outcome", self.contract["contract_kind"])
        flags = authorization_flags(self.contract)
        self.assertEqual(len(flags), 18)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(self.contract["authorization"]["authorization_request_prepared"])
        self.assertFalse(self.contract["authorization"]["authorization_sentence_exists"])

    def test_exact_committed_artifact_hashes_and_sizes_match(self):
        for artifact in self.contract["committed_input_artifacts"]:
            path = REPO_ROOT / artifact["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), artifact["bytes"], artifact["artifact_id"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                artifact["sha256"],
                artifact["artifact_id"],
            )
            self.assertFalse(artifact["contains_plaintext_targets_or_predictions"])

    def test_observed_snapshot_replays_public_result_without_targets(self):
        snapshot = self.contract["observed_aggregate_snapshot"]
        candidate = self.result["condition_metrics"][snapshot["primary_candidate_id"]]
        prior = self.result["condition_metrics"][snapshot["train_only_prior_id"]]
        self.assertAlmostEqual(
            candidate["macro_sentence_cer"],
            snapshot["primary_candidate_macro_sentence_cer"],
        )
        self.assertAlmostEqual(
            candidate["blank_fraction"], snapshot["primary_candidate_blank_fraction"]
        )
        self.assertAlmostEqual(
            prior["macro_sentence_cer"], snapshot["train_only_prior_macro_sentence_cer"]
        )
        self.assertFalse(snapshot["snapshot_is_independent_loop48_evidence"])
        self.assertFalse(self.result["plaintext_targets_or_predictions_present"])

    def test_seed_instability_and_prior_dominance_values_are_exact(self):
        snapshot = self.contract["observed_aggregate_snapshot"]
        blank_fractions = [
            self.result["condition_metrics"][condition_id]["blank_fraction"]
            for condition_id in snapshot["size55_seed_ids"]
        ]
        cers = [
            self.result["condition_metrics"][condition_id]["macro_sentence_cer"]
            for condition_id in snapshot["size55_seed_ids"]
        ]
        prior = snapshot["train_only_prior_macro_sentence_cer"]
        self.assertEqual(blank_fractions, snapshot["size55_blank_fractions"])
        self.assertAlmostEqual(max(blank_fractions) - min(blank_fractions), 0.4732980024459845)
        self.assertEqual(cers, snapshot["size55_macro_sentence_cers"])
        self.assertTrue(all(value > prior for value in cers))
        self.assertTrue(snapshot["size55_every_seed_worse_than_prior"])

    def test_all_six_prefix_groups_cross_the_descriptive_instability_rule(self):
        snapshot = self.contract["observed_aggregate_snapshot"]
        ranges = snapshot["prefix_blank_ranges"]
        self.assertEqual(set(ranges), {"8", "16", "24", "32", "44", "55"})
        self.assertTrue(all(value >= 0.25 for value in ranges.values()))
        self.assertEqual(snapshot["prefix_groups_with_blank_range_at_least_0_25"], 6)
        self.assertEqual(snapshot["prefix_group_count"], 6)

    def test_failure_taxonomy_is_ordered_unique_and_root_cause_safe(self):
        classes = self.contract["ordered_failure_classes"]
        self.assertEqual([row["order"] for row in classes], list(range(1, 9)))
        ids = [row["class_id"] for row in classes]
        self.assertEqual(ids, ["F1", "F2", "F5", "F3", "F4", "F6", "F7", "U0"])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(not row["root_cause_claim_allowed"] for row in classes))
        leading = self.contract["leading_observed_diagnosis"]
        self.assertEqual(leading["failure_class_id"], "F5")
        self.assertFalse(leading["root_cause_established"])
        self.assertFalse(leading["loop48_acceptance_gate_satisfied_now"])

    def test_stage_a_is_artifact_only_bounded_and_not_authorized(self):
        stage = self.contract["future_artifact_only_stage_a"]
        self.assertEqual(stage["status"], "preregistered_not_authorized_or_implemented")
        self.assertEqual(len(stage["allowed_input_artifact_ids"]), 4)
        self.assertEqual(stage["expected_primary_class_if_bound_artifacts_remain_exact"], "F5")
        self.assertFalse(stage["expected_class_is_new_independent_evidence"])
        self.assertFalse(stage["output_may_contain_plaintext_targets_or_predictions"])
        self.assertFalse(stage["output_may_recommend_a_larger_architecture"])
        self.assertFalse(stage["output_may_select_a_seed"])
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["future_stage_a_cpu_threads"], 1)
        self.assertEqual(caps["future_stage_a_workers"], 1)
        self.assertEqual(caps["future_stage_a_runtime_sec"], 30)
        self.assertEqual(caps["future_stage_a_peak_rss_bytes"], 256 * 1024**2)
        self.assertEqual(caps["future_stage_a_generated_bytes"], 1024**2)
        self.assertLess(caps["current_generated_planning_bytes"], 8 * 1024**2)

    def test_future_train_only_stage_remains_unregistered_and_target_free(self):
        self.assertEqual(len(self.contract["unavailable_root_cause_fields"]), 17)
        stage = self.contract["future_train_only_stage"]
        self.assertEqual(stage["status"], "not_preregistered_not_authorized")
        self.assertEqual(len(stage["minimum_diagnostic_families"]), 7)
        self.assertFalse(stage["validation_targets_allowed"])
        self.assertFalse(stage["source_test_allowed"])
        self.assertFalse(stage["session2_allowed"])
        self.assertFalse(stage["s25_allowed"])
        self.assertFalse(stage["model_run_inventory_frozen"])
        self.assertFalse(stage["stop_rules_frozen"])

    def test_planning_access_counters_are_zero_for_protected_operations(self):
        counters = self.contract["planning_access_counters"]
        self.assertEqual(counters["committed_aggregate_json_reads"], 4)
        protected = {
            key: value for key, value in counters.items() if key != "committed_aggregate_json_reads"
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_refusals_sources_and_claim_boundary_are_complete(self):
        refusals = self.contract["refusal_ids"]
        self.assertEqual(len(refusals), 30)
        self.assertEqual(len(refusals), len(set(refusals)))
        sources = self.contract["source_bindings"]
        self.assertEqual(len(sources), 5)
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        claim = self.contract["claim_boundary"]
        self.assertIn("artifact-only", claim["maximum_future_stage_a_claim"])
        self.assertIn("No root cause", claim["scientific_claim_not_established"])

    def test_living_status_docs_preserve_the_contract_and_claim_boundary(self):
        for path in PUBLIC_STATUS_PATHS:
            content = path.read_text(encoding="utf-8")
            self.assertIn("Loop 48", content, path)
        combined = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS)
        self.assertIn("not a proven root cause", combined.lower())
        self.assertIn("no rerun", combined.lower())

    def test_human_research_note_explains_the_exact_boundary(self):
        for phrase in (
            "99.3477%",
            "0.002446",
            "0.999592",
            "F5",
            "failure phenotype",
            "post-outcome",
            "not a proven root cause",
            "does not prove",
            "not specified or authorized",
        ):
            self.assertIn(phrase, self.research)

    def test_scientific_roadmap_marks_stage_a_consumed_without_a_rerun(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 48)
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["status"], "Complete; Stage A F5 And Stage B H4 Diagnostic")
        self.assertIn("Stage A has no rerun authorized", row["authorization_boundary"])
        self.assertIn("no rerun", row["authorization_boundary"])

    def test_registration_snapshot_records_no_runtime_or_authorization(self):
        self.assertEqual(self.contract["status"], "preregistered_authorization_pending")
        self.assertEqual(
            self.contract["future_artifact_only_stage_a"]["status"],
            "preregistered_not_authorized_or_implemented",
        )
        flags = authorization_flags(self.contract)
        self.assertTrue(flags)
        self.assertTrue(all(value is False for _, value in flags), flags)
        counters = self.contract["planning_access_counters"]
        protected = {
            key: value for key, value in counters.items() if key != "committed_aggregate_json_reads"
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)


if __name__ == "__main__":
    unittest.main()
