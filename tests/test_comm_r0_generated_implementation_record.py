from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_independent_replication_generated_implementation.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_INDEPENDENT_REPLICATION_GENERATED_IMPLEMENTATION.md"
)


class CommR0GeneratedImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.document = DOCUMENT.read_text(encoding="utf-8")

    def test_schema_parent_and_artifact_hashes(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.communication_eeg_independent_replication_generated_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "COMM-R0-G")
        self.assertEqual(self.record["registration_id"], "COMM-R0-REPLICATION-v0")
        self.assertTrue(self.record["parent_proof"]["both_required_jobs_green"])
        for group in ("implementation_artifacts", "bound_reused_generated_utilities"):
            for artifact in self.record[group]:
                payload = (ROOT / artifact["path"]).read_bytes()
                self.assertEqual(len(payload), artifact["bytes"], artifact["path"])
                self.assertEqual(
                    hashlib.sha256(payload).hexdigest(),
                    artifact["sha256"],
                    artifact["path"],
                )

    def test_two_stage_freeze_and_schedule_are_exact(self) -> None:
        firewall = self.record["firewall"]
        self.assertFalse(firewall["held_out_targets_in_predictor_signature"])
        self.assertTrue(firewall["neural_prediction_freeze_before_language_arms"])
        self.assertTrue(firewall["complete_prediction_freeze_before_target_delivery"])
        self.assertTrue(
            firewall["vault_delivery_requires_identity_bound_committed_freeze_capability"]
        )
        schedule = self.record["schedule_per_replay"]
        self.assertEqual(schedule["total_parameter_update_fits"], 156)
        self.assertEqual(schedule["prediction_sets"], 180)
        self.assertEqual(schedule["prediction_rows"], 4320)
        official = self.record["official_qualification_schedule"]
        self.assertEqual(official["deterministic_full_replays"], 2)
        self.assertEqual(official["total_parameter_update_fits"], 312)
        self.assertEqual(official["prediction_rows"], 8640)
        self.assertEqual(official["post_target_updates"], 0)
        self.assertEqual(official["official_invocations_maximum"], 1)

    def test_controls_causality_and_partial_ceiling_are_preserved(self) -> None:
        fixture = self.record["generated_fixture"]
        self.assertEqual(fixture["participants"], 12)
        self.assertTrue(fixture["causal_timing_record_complete"])
        self.assertTrue(fixture["offline_trial_boundary_oracle_explicit"])
        self.assertTrue(
            fixture[
                "partial_route_missing_sensors_are_unavailable_not_zero_filled_or_proxied"
            ]
        )
        derangement = self.record["derangement"]
        self.assertTrue(derangement["all_K_minus_1_cyclic_shifts"])
        self.assertEqual(derangement["generated_shifts"], [1, 2, 3])
        self.assertFalse(derangement["held_out_rows_or_targets_permuted"])
        language = self.record["language_controls"]
        self.assertTrue(language["provider_free"])
        self.assertFalse(language["participant_identity_in_item_derangement_digest"])
        self.assertFalse(language["language_arms_can_change_neural_router"])

    def test_every_parent_refusal_and_resource_cap_is_bound(self) -> None:
        parent = json.loads(
            (
                ROOT
                / "registries"
                / "communication_eeg_independent_replication_contract.v0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            self.record["adversarial_qualification"]["families"],
            parent["generated_qualification_required_refusals"],
        )
        resources = self.record["resource_caps"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertEqual(resources["analysis_network_bytes"], 0)
        self.assertFalse(resources["write_outside_NeuroDecodeKit"])

    def test_activation_and_every_real_surface_remain_closed(self) -> None:
        activation = self.record["activation_sequence"]
        self.assertIsNone(activation["implementation_commit"])
        self.assertFalse(activation["both_required_jobs_green"])
        self.assertTrue(activation["separate_activation_required"])
        self.assertTrue(activation["separate_activation_proof_closeout_required"])
        self.assertFalse(activation["runtime_green_proof_network_request"])
        authority = self.record["authority"]
        self.assertTrue(authority["development_replay"])
        self.assertFalse(authority["official_generated_qualification"])
        for key, value in authority.items():
            if key != "development_replay":
                self.assertFalse(value, key)
        for key, value in self.record["operation_counters"].items():
            self.assertEqual(value, 0, key)
        for key, value in self.record["claim_boundary"].items():
            if key != "engineering_capability_added":
                self.assertFalse(value, key)

    def test_document_is_explicit_about_nonclaim(self) -> None:
        self.assertIn("identity-bound committed-freeze capability", self.document)
        self.assertIn("performs no GitHub", self.document)
        self.assertIn("or other network request during analysis", self.document)
        self.assertIn("cannot prove continuous endpointing", self.document)
        self.assertIn("Scientific claim not established", self.document)


if __name__ == "__main__":
    unittest.main()
