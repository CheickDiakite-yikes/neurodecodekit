import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "registries" / "loop48_failure_localization_result.v0.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_failure_localization_contract.v0.json"
DECISION_PATH = REPO_ROOT / "registries" / "loop48_authorization_decision.v0.json"
CLOSEOUT_PATH = REPO_ROOT / "docs" / "LOOP_48_FAILURE_LOCALIZATION_RESULT.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
RESULT_SHA256 = "dbfb4c7cc6163ff31fa216c1b33e7510a87b0b843ef714754037d37275924659"


class Loop48FailureLocalizationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.closeout = CLOSEOUT_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))

    def test_result_identity_hash_and_consumed_status_are_exact(self):
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), RESULT_SHA256)
        self.assertEqual(len(self.payload), 10643)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.loop48_failure_localization_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["status"], "completed_descriptive_f5_no_root_cause")
        self.assertEqual(self.result["generated_bytes"], len(self.payload))
        self.assertIn("post_outcome", self.result["proof_posture"])

    def test_authorization_and_implementation_were_remote_green_first(self):
        authorization = self.result["authorization"]
        implementation = self.result["implementation"]
        self.assertEqual(
            authorization["authorization_commit"],
            "5bae88092525206b1d3cf3add055c75665943f14",
        )
        self.assertEqual(
            (
                authorization["authorization_push_ci_run_id"],
                authorization["authorization_pr_ci_run_id"],
            ),
            (29442914090, 29442916230),
        )
        self.assertEqual(
            implementation["commit"],
            "ca21539cb25949650e1b5a79ccba8fa586e88ccf",
        )
        self.assertEqual(
            (implementation["push_ci_run_id"], implementation["pr_ci_run_id"]),
            (29444008688, 29444012075),
        )
        self.assertTrue(implementation["operator_confirmed_both_runs_green_before_stage_a"])
        self.assertEqual(
            self.result["contract_sha256"],
            self.decision["authorized_contract"]["contract_sha256"],
        )

    def test_four_input_identities_and_total_bytes_match_the_contract(self):
        measured = self.result["input_artifact_hashes"]
        frozen = self.contract["committed_input_artifacts"]
        self.assertEqual(len(measured), 4)
        self.assertEqual(
            [(row["artifact_id"], row["path"], row["bytes"], row["sha256"]) for row in measured],
            [(row["artifact_id"], row["path"], row["bytes"], row["sha256"]) for row in frozen],
        )
        self.assertTrue(all(row["sha256_verified"] for row in measured))
        self.assertTrue(
            all(not row["plaintext_targets_or_predictions_present"] for row in measured)
        )
        self.assertEqual(self.result["input_bytes"], 155545)

    def test_recomputed_aggregate_evidence_is_exact(self):
        evidence = self.result["aggregate_evidence"]
        self.assertEqual(evidence["primary_candidate_id"], "L33-N55-S2601")
        self.assertAlmostEqual(evidence["primary_candidate_macro_sentence_cer"], 0.9381765674382471)
        self.assertAlmostEqual(evidence["train_only_prior_macro_sentence_cer"], 0.7512350583540796)
        self.assertAlmostEqual(
            evidence["primary_prior_minus_candidate_margin"], -0.1869415090841675
        )
        self.assertAlmostEqual(evidence["primary_candidate_blank_fraction"], 0.9934773746432939)
        self.assertEqual(evidence["primary_candidate_exact_sentences"], 0)
        self.assertEqual(evidence["primary_wins_ties_losses"], [0, 1, 5])
        self.assertEqual(evidence["primary_one_sided_exact_p"], 1.0)
        self.assertTrue(evidence["size55_every_seed_worse_than_prior"])
        self.assertEqual(evidence["trained_scaling_condition_count"], 18)
        self.assertEqual(evidence["prefix_groups_with_blank_range_at_least_0_25"], 6)
        self.assertEqual(evidence["prefix_group_count"], 6)
        self.assertFalse(evidence["source_cache_preprocessing_is_causal"])

    def test_ordered_tree_selects_f5_without_claiming_root_cause(self):
        trace = self.result["decision_trace"]
        self.assertEqual(
            [row["class_id"] for row in trace], ["F1", "F2", "F5", "F3", "F4", "F6", "F7", "U0"]
        )
        self.assertEqual(trace[0]["state"], "not_triggered")
        self.assertEqual(trace[1]["state"], "unavailable")
        self.assertEqual(trace[2]["state"], "triggered")
        self.assertTrue(all(trace[2]["checks"].values()))
        primary = self.result["primary_failure_class"]
        self.assertEqual(primary["class_id"], "F5")
        self.assertTrue(primary["descriptive_failure_phenotype_only"])
        self.assertFalse(primary["root_cause_established"])
        self.assertEqual(
            self.result["secondary_unresolved_classes"],
            ["F2", "F3", "F4", "F6", "F7", "U0"],
        )

    def test_access_and_resource_gates_all_passed(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["runtime_committed_json_reads"], 4)
        self.assertEqual(counters["input_sha256_verifications"], 4)
        self.assertEqual(counters["generated_diagnostic_reports"], 1)
        allowed_nonzero = {
            "governance_json_reads",
            "runtime_committed_json_reads",
            "input_sha256_verifications",
            "generated_diagnostic_reports",
        }
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in allowed_nonzero)
        )
        self.assertLessEqual(self.result["runtime_sec"], 30)
        self.assertLessEqual(self.result["peak_rss_bytes"], 256 * 1024**2)
        self.assertLessEqual(self.result["generated_bytes"], 1024**2)
        self.assertTrue(self.result["resource_checks"]["all_caps_passed"])
        self.assertTrue(all(self.result["resource_checks"].values()))
        self.assertFalse(self.result["producer"]["end_to_end_latency_measured"])

    def test_report_contains_no_plaintext_or_per_item_metrics(self):
        serialized = json.dumps(self.result, sort_keys=True)
        for forbidden in ('"targets"', '"predictions"', '"target_texts"', '"per_item"'):
            self.assertNotIn(forbidden, serialized)
        self.assertFalse(self.result["plaintext_targets_or_predictions_present"])
        self.assertFalse(self.result["per_item_target_conditioned_metrics_present"])

    def test_closeout_and_roadmap_preserve_the_claim_ceiling(self):
        for phrase in (
            "Complete at the one-shot artifact-only Stage A boundary",
            "no rerun authorized",
            "not a causal root cause",
            "0.016568875",
            "23,429,120",
            "10,643",
            RESULT_SHA256,
        ):
            self.assertIn(phrase, self.closeout)
        loop48 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 48)
        self.assertEqual(loop48["status"], "Complete A/B; Stage C Preflight Fix Pending Green")
        self.assertFalse(loop48["execution_authorized"])
        self.assertIn("consumed", loop48["authorization_boundary"])
        self.assertIn("no rerun", loop48["authorization_boundary"])


if __name__ == "__main__":
    unittest.main()
