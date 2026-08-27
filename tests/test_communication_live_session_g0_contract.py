from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries" / "communication_live_session_g0_contract.v0.json"
DOC = ROOT / "docs" / "COMMUNICATION_LIVE_SESSION_G0_PREREGISTRATION.md"
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommunicationLiveSessionG0ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_identity_and_state_machine_are_exact(self) -> None:
        self.assertEqual(self.contract["gate_id"], "COMM-LIVE-G0")
        self.assertEqual(self.contract["active_gate"]["gate_id"], "DREYER-C5R-1-HL")
        binding = self.contract["source_chunk_binding"]
        self.assertEqual(
            binding["contract"], "registries/replay_equivalence_contract.v0.json"
        )
        self.assertEqual(binding["schema_name"], "neurodecodekit.source_chunk")
        self.assertEqual(binding["schema_version"], "0.1.0")
        self.assertTrue(binding["RW3_owns_transport_envelope"])
        self.assertTrue(binding["LiveSession_accepts_only_strictly_validated_SourceChunk"])
        self.assertFalse(binding["alternate_or_duplicate_transport_schema_allowed"])
        self.assertFalse(binding["raw_array_input_allowed"])
        state = self.contract["state_machine"]
        self.assertTrue(state["exact_sequence_continuity"])
        self.assertTrue(state["exact_source_sample_continuity"])
        self.assertFalse(state["implicit_gap_allowed"])
        self.assertFalse(state["state_bridge_across_generation_allowed"])

    def test_targets_language_and_future_context_are_forbidden(self) -> None:
        forbidden = set(self.contract["forbidden_runtime_fields"])
        self.assertTrue({"targets", "intended_text", "reference_text"} <= forbidden)
        processor = self.contract["causal_processor"]
        self.assertEqual(processor["right_context_samples"], 0)
        self.assertFalse(processor["known_trial_end_allowed"])
        self.assertFalse(processor["future_chunk_allowed"])
        self.assertFalse(processor["target_or_reference_input_allowed"])
        self.assertFalse(processor["language_model_output_allowed"])

    def test_abstention_commit_and_clocks_are_frozen(self) -> None:
        policy = self.contract["commit_policy"]
        self.assertEqual(policy["minimum_confidence"], 0.8)
        self.assertEqual(policy["stable_updates_required"], 3)
        self.assertEqual(policy["warmup_chunks_per_generation"], 2)
        self.assertFalse(policy["repeat_commit_without_rearm_allowed"])
        self.assertEqual(len(self.contract["clock_order"]), 8)
        self.assertEqual(len(self.contract["latency_fields"]), 7)

    def test_generated_schedule_and_refusals_are_complete(self) -> None:
        qualification = self.contract["generated_qualification"]
        self.assertEqual(qualification["official_invocations_maximum"], 1)
        self.assertEqual(qualification["deterministic_replays"], 2)
        self.assertEqual(len(qualification["schedules"]), 3)
        self.assertFalse(qualification["rerun_allowed"])
        refusals = self.contract["required_adversarial_refusals"]
        self.assertEqual(len(refusals), 33)
        self.assertEqual(len(refusals), len(set(refusals)))
        for required in (
            "identical_duplicate_record",
            "partial_source_sample_overlap",
            "hidden_sample_gap",
            "arrival_monotonic_rollback",
            "snapshot_tamper",
            "stability_across_gap",
            "target_label_or_text_leakage",
        ):
            self.assertIn(required, refusals)

    def test_RW3_stage_A_review_is_narrow_and_delayed(self) -> None:
        review = self.contract["prior_RW3_stage_A_review"]
        self.assertTrue(
            review[
                "separate_review_requirement_satisfied_by_this_registration_after_own_remote_green"
            ]
        )
        changed = review["changed_authority_flags"]
        self.assertEqual(
            set(changed),
            {
                "source_chunk_implementation_authorized",
                "synthetic_fixture_generation_authorized",
            },
        )
        for decision in changed.values():
            self.assertFalse(decision["before"])
            self.assertTrue(decision["after_own_remote_green"])
        self.assertFalse(review["later_RW3_adapter_stage_authorized"])
        self.assertFalse(review["SourceChunk_schema_change_authorized"])
        forbidden = set(review["unchanged_forbidden_surfaces"])
        self.assertTrue(
            {
                "external_network",
                "live_hardware",
                "real_recording_or_cache_access",
                "target_label_or_prediction_access",
                "model_or_training",
            }
            <= forbidden
        )

    def test_resources_and_authority_remain_bounded(self) -> None:
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertTrue(caps["standard_library_base_implementation"])
        self.assertEqual(caps["serialized_SourceChunk_state_bytes_maximum"], 4096)
        self.assertEqual(caps["public_result_bytes_maximum"], 1_048_576)
        self.assertEqual(caps["wall_time_seconds_maximum"], 30)
        self.assertEqual(caps["analysis_network_bytes"], 0)
        authority = self.contract["authority"]
        allowed = {
            "RW3_stage_A_SourceChunk_implementation_after_registration_green",
            "RW3_stage_A_synthetic_fixture_generation_after_registration_green",
            "generated_implementation_after_registration_green",
            "generated_qualification_after_implementation_green",
        }
        for key in allowed:
            self.assertTrue(authority[key])
        for key, value in authority.items():
            if key not in allowed:
                self.assertFalse(value, key)

    def test_frontier_and_claims_remain_unchanged(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        live = frontier["parallel_tier_A_communication_program"][
            "generated_live_session_preregistration"
        ]
        self.assertEqual(live["gate_id"], "COMM-LIVE-G0")
        self.assertEqual(live["required_adversarial_refusals"], 33)
        self.assertEqual(frontier["active_lane_id"], "DREYER-C5R-1-HL")
        self.assertTrue(self.contract["active_gate"]["all_authority_flags_false"])
        self.assertTrue(all(value is False for value in self.contract["claim_boundary"].values()))

    def test_document_uses_honest_live_boundary(self) -> None:
        normalized = " ".join(DOC.read_text(encoding="utf-8").split())
        for phrase in (
            "does not yet have the session boundary required to call any future run live",
            "No later chunk is accepted until an explicit reconnect",
            "not a measurement of device or human latency",
            "Scientific claim not established",
            "DREYER-C5R-1-HL",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
