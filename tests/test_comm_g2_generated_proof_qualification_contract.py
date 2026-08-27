from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries" / "comm_g2_generated_proof_qualification_contract.v0.json"
)
DOC_PATH = ROOT / "docs" / "COMM_G2_GENERATED_PROOF_QUALIFICATION_PREREGISTRATION.md"
FRONTIER_PATH = ROOT / "registries" / "current_research_frontier.v0.json"


class CommG2GeneratedProofQualificationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_parent_closeout_is_exact_green_consumed_R0(self) -> None:
        parent = self.contract["parent_closeout"]
        self.assertEqual(parent["binding_route"], "COMM-G1-R0")
        self.assertTrue(parent["consumed"])
        self.assertFalse(parent["rerun_allowed"])
        self.assertTrue(parent["both_required_jobs_green"])
        self.assertEqual(parent["commit"], "adc1b41be6e42a662ea465e21e5dd713cada0cd4")
        for artifact in parent["artifacts"]:
            path = ROOT / artifact["path"]
            payload = path.read_bytes()
            self.assertEqual(artifact["bytes"], len(payload))
            self.assertEqual(artifact["sha256"], hashlib.sha256(payload).hexdigest())

    def test_scientific_core_is_byte_bound_and_unchanged(self) -> None:
        core = self.contract["frozen_scientific_core"]
        for artifact in [core["module"], *core["bound_records"]]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(artifact["bytes"], len(payload))
            self.assertEqual(artifact["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertFalse(core["module"]["may_be_modified_by_COMM_G2"])
        self.assertFalse(
            core["features_residualizer_derangement_classifier_thresholds_and_seed_selection_changed"]
        )
        self.assertFalse(core["hyperparameter_or_model_selection"])

    def test_replay_digest_binds_every_failed_COMM_G1_surface(self) -> None:
        digest = self.contract["canonical_replay_digest"]
        required = {
            "cue_id",
            "timing_id",
            "source_sample_start",
            "source_sample_stop",
            "source_time_start_seconds",
            "source_time_stop_seconds",
            "source_sampling_rate_hz",
            "true_length",
            "padding_mask",
            "channel_names",
            "channel_roles",
            "channel_geometry",
            "signal",
            "synthetic_target",
        }
        self.assertTrue(required.issubset(set(digest["row_fields"])))
        self.assertEqual(
            digest["array_binding"], ["dtype", "byte_order", "shape", "C_contiguous_bytes"]
        )
        self.assertTrue(digest["two_isolated_replays_required"])

    def test_process_and_target_isolation_are_explicit(self) -> None:
        isolation = self.contract["process_isolation"]
        self.assertEqual(isolation["replays"], 2)
        self.assertTrue(isolation["separate_child_processes"])
        self.assertTrue(isolation["exclusive_clean_workdirs"])
        self.assertFalse(isolation["prediction_worker_can_open_target_vault"])
        self.assertFalse(isolation["scorer_can_update_model_or_transform"])
        firewall = self.contract["target_and_split_firewall"]
        self.assertEqual(firewall["held_out_target_fit_rows"], 0)
        self.assertTrue(firewall["aggregate_prediction_freeze_before_target_delivery"])
        self.assertEqual(firewall["post_target_updates"], 0)

    def test_schedule_duplicates_only_the_proof_replay(self) -> None:
        schedule = self.contract["schedule"]
        self.assertEqual(schedule["full_isolated_replays"], 2)
        self.assertEqual(schedule["parameter_updates_per_replay"], 60)
        self.assertEqual(schedule["total_parameter_updates"], 120)
        self.assertEqual(schedule["prediction_sets_per_replay"], 60)
        self.assertEqual(schedule["total_prediction_sets"], 120)
        self.assertEqual(schedule["total_prediction_rows"], 2880)
        self.assertEqual(schedule["post_target_updates"], 0)
        self.assertEqual(schedule["official_invocations"], 1)
        self.assertEqual(schedule["reruns"], 0)

    def test_filesystem_and_every_named_refusal_are_frozen(self) -> None:
        filesystem = self.contract["filesystem_contract"]
        self.assertTrue(filesystem["output_parent_no_follow_directory_capability"])
        self.assertEqual(filesystem["final_publication"], "non_replacing_same_directory")
        self.assertEqual(
            filesystem["cleanup_scope"], "invocation_owned_temporary_files_only"
        )
        adversarial = self.contract["adversarial_qualification"]
        families = set(adversarial["families"])
        self.assertTrue(adversarial["every_named_family_must_execute"])
        self.assertTrue(
            {
                "ancestor_symlink_escape",
                "leaf_symlink_escape",
                "publication_race",
                "resource_runtime_cap_breach",
                "resource_RSS_cap_breach",
                "resource_generated_input_cap_breach",
                "resource_private_output_cap_breach",
                "resource_public_output_cap_breach",
                "nondeterministic_prediction_replay",
            }.issubset(families)
        )
        self.assertGreaterEqual(len(families), adversarial["minimum_distinct_refusal_ids"])

    def test_caps_are_bounded_and_real_authority_is_all_false(self) -> None:
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["active_workers_maximum"], 1)
        self.assertLessEqual(caps["peak_process_tree_RSS_bytes"], 512 << 20)
        self.assertLessEqual(caps["generated_input_bytes_total_maximum"], 80 << 20)
        self.assertLessEqual(caps["temporary_disk_bytes_maximum"], 96 << 20)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["real_or_private_dataset_bytes"], 0)
        authorization = self.contract["authorization_state"]
        self.assertTrue(all(value is False for value in authorization.values()))
        counters = self.contract["operation_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_claims_and_active_Tier_C_gate_do_not_change(self) -> None:
        claims = self.contract["claim_boundary"]
        for key, value in claims.items():
            if key != "engineering_capability_proposed":
                self.assertFalse(value)
        gate = self.contract["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(gate["all_authority_flags_false"])
        self.assertFalse(gate["changed_by_this_contract"])

    def test_document_is_plain_about_scope_and_failure(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        for phrase in (
            "COMM-G1 is consumed at `COMM-G1-R0`",
            "does not repair, rerun, overwrite, or upgrade COMM-G1",
            "Two independent child processes",
            "No COMM-G2 route has scientific value",
            "This registration authorizes no current execution",
        ):
            self.assertIn(phrase, text)

    def test_frontier_preserves_registered_successor_and_active_gate(self) -> None:
        frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))
        source_gate = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]
        successor = source_gate["generated_proof_successor_preregistration"]
        self.assertEqual(successor["gate_id"], "COMM-G2_GENERATED_PROOF_QUALIFICATION")
        self.assertEqual(successor["status"], "consumed_parked_COMM_G2_R0_no_rerun")
        self.assertEqual(successor["binding_closeout_route"], "COMM-G2-R0")
        self.assertFalse(successor["rerun_allowed"])
        self.assertFalse(successor["generated_implementation_authorized_now"])
        self.assertFalse(successor["generated_qualification_authorized_now"])
        self.assertEqual(successor["real_or_private_operations"], 0)
        self.assertEqual(frontier["active_lane_id"], "DREYER-C5R-1-HL")


if __name__ == "__main__":
    unittest.main()
