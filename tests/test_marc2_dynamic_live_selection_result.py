import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_dynamic_live_selection_result.v0.json"


class Marc2DynamicLiveSelectionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_route_and_registration_proof_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR6")
        self.assertEqual(self.result["route"], "MARC2VR6-G1")
        self.assertEqual(
            self.result["status"],
            "completed_generated_only_dynamic_selection_qualification_remotely_green",
        )
        proof = self.result["green_registration_proof"]
        self.assertEqual(
            proof["commit"], "71d7cec63ff3c57122aec1ffa02fbec02de5f9dd"
        )
        self.assertEqual(proof["CI_run_id"], 31974405202)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])
        implementation = self.result["green_implementation_proof"]
        self.assertEqual(
            implementation["commit"],
            "482dad55e91e2abf48b6a59a417ebca191c0cd68",
        )
        self.assertEqual(implementation["CI_run_id"], 31975600088)
        self.assertEqual(implementation["base_python_job_id"], 95234487830)
        self.assertEqual(implementation["optional_neuro_job_id"], 95234487789)
        self.assertTrue(implementation["both_required_jobs_green"])

    def test_every_bound_artifact_hash_matches(self):
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(".codex_work", binding["path"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    binding["sha256"],
                )

    def test_dynamic_profiles_cover_all_registered_boundaries(self):
        profiles = self.result["profile_results"]
        self.assertEqual(
            [row["selected_subjects"] for row in profiles],
            [12, 14, 16, 18, 19],
        )
        self.assertEqual(
            [row["selected_run_bundles"] for row in profiles],
            [72, 84, 96, 108, 114],
        )
        self.assertEqual(
            [row["selected_core_members"] for row in profiles],
            [288, 336, 384, 432, 456],
        )
        self.assertEqual(len({row["selection_identity_sha256"] for row in profiles}), 5)
        self.assertTrue(all(row["next_ranked_subject_does_not_fit"] for row in profiles[:4]))
        self.assertTrue(profiles[-1]["all_eligible_subjects_fit"])

    def test_fixture_identity_was_replaced_by_measured_invariants(self):
        policy = self.result["dynamic_policy"]
        self.assertTrue(policy["source_validation_precedes_selection"])
        self.assertFalse(policy["VR2_exact_generated_assertion_called"])
        self.assertTrue(
            policy["selected_count_reservation_and_hash_are_measured_outputs"]
        )
        self.assertTrue(policy["row_reservation_formula_and_sum_recomputed"])
        self.assertTrue(policy["rank_prefix_must_be_contiguous_and_maximal"])

    def test_live_semantics_and_route_boundary_are_exact(self):
        semantics = self.result["source_and_route_semantics"]
        self.assertEqual(
            semantics["live_row_source_id"],
            "freewill_23_live_central_directory",
        )
        self.assertFalse(semantics["generated_inventory_hash_key_retained"])
        self.assertTrue(semantics["selection_identity_recomputed"])
        self.assertTrue(semantics["private_manifest_hash_recomputed"])
        self.assertTrue(semantics["allowlisted_upstream_route_code_only"])
        self.assertFalse(semantics["upstream_reason_or_private_value_retained"])

    def test_replay_mutations_measurements_and_counters_are_bounded(self):
        self.assertEqual(self.result["replay_summary"]["success_paths"], 10)
        mutation = self.result["mutation_summary"]
        self.assertEqual(mutation["direct_mutations_passed"], 34)
        self.assertEqual(
            set(mutation["route_counts"]),
            {f"MARC2VR6-F{index:02d}" for index in range(1, 9)},
        )
        measured = self.result["measurements"]
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))
        self.assertTrue(all(self.result["acceptance_gates"].values()))
        verification = self.result["verification"]
        self.assertEqual(verification["focused_tests"], 29)
        self.assertEqual(verification["focused_subtests"], 19)
        self.assertEqual(verification["complete_suite_primary_passes"], 3894)
        self.assertEqual(verification["complete_suite_skips"], 35)
        self.assertEqual(
            verification["complete_suite_known_process_state_failures"], 3
        )
        self.assertEqual(verification["new_failures_vs_pre_change_baseline"], 0)
        self.assertTrue(
            verification["ruff_compile_registry_JSON_CLI_and_diff_hygiene_passed"]
        )
        self.assertFalse(verification["remote_CI_pending"])
        self.assertTrue(verification["remote_CI_passed"])

    def test_claim_and_next_gate_remain_closed(self):
        claim = self.result["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["real_cohort_frozen"])
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])
        gate = self.result["next_gate"]
        self.assertTrue(
            gate["exact_implementation_commit_is_pushed_and_remotely_green"]
        )
        self.assertTrue(gate["Tier_A_or_B_private_wrapper_specification_eligible"])
        self.assertFalse(gate["private_read_authorized"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])
        self.assertTrue(
            gate["future_private_read_requires_new_Tier_C_packet_and_decision"]
        )


if __name__ == "__main__":
    unittest.main()
