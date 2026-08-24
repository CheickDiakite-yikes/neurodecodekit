import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_research.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_PRIMARY_SOURCE_RESEARCH.md"


class BNCI2014001CrossParticipantEEGGainResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_pinned_source_and_original_payload_are_exact(self):
        source = self.record["source_snapshot"]
        self.assertEqual(source["nemar_version"], "v1.0.2")
        self.assertEqual(source["peeled_commit"], "15cf4f87975f4b5ee2ac39f703b9ac85b0ff97dc")
        self.assertEqual(source["participants"], 9)
        self.assertEqual(source["EEG_channels"], 22)
        self.assertEqual(source["EOG_channels"], 3)

        payload = self.record["selected_original_payload"]
        self.assertEqual(payload["files"], 18)
        self.assertEqual(len(payload["members"]), 18)
        self.assertEqual(sum(member["bytes"] for member in payload["members"]), 779_873_919)
        self.assertEqual(
            {Path(member["path"]).name for member in payload["members"]},
            {f"A{subject:02d}{session}.mat" for subject in range(1, 10) for session in "ET"},
        )
        self.assertTrue(all(len(member["sha256"]) == 64 for member in payload["members"]))
        self.assertTrue(payload["exclude_duplicate_representations"])

    def test_outer_folds_are_strictly_zero_calibration(self):
        protocol = self.record["outer_protocol"]
        self.assertEqual(protocol["folds"], 9)
        self.assertEqual(protocol["inference_unit"], "participant")
        self.assertEqual(protocol["source_participants_per_fold"], 8)
        self.assertEqual(protocol["held_out_participants_per_fold"], 1)
        self.assertTrue(protocol["four_class_primary"])
        self.assertTrue(
            all(
                value is False
                for key, value in protocol.items()
                if key
                in {
                    "held_out_person_signal_for_fit",
                    "held_out_person_target_for_fit",
                    "held_out_person_calibration",
                    "held_out_person_normalization_fit",
                    "held_out_person_alignment_fit",
                    "held_out_person_threshold_fit",
                    "post_target_update",
                }
            )
        )

    def test_conditional_fusion_and_controls_target_C3_and_partial_C5(self):
        architecture = self.record["architecture"]
        self.assertEqual(
            architecture["name"], "source_cross_fitted_conditional_EOG_EEG_logit_fusion"
        )
        self.assertFalse(architecture["deep_network"])
        self.assertFalse(architecture["foundation_or_language_model"])
        controls = set(self.record["required_conditions"])
        self.assertTrue(
            {
                "equal_prior_no_signal",
                "timing_and_trial_order_only",
                "EOG_only_P",
                "fused_P_plus_E",
                "size_matched_P_plus_D_E",
                "fixed_nonwrapping_EEG_trial_displacement_within_run",
                "early_cue",
            }.issubset(controls)
        )
        endpoints = self.record["recommended_endpoints"]
        self.assertEqual(endpoints["paired_inference_unit"], "participant")
        self.assertTrue(endpoints["pooled_trial_only_inference_forbidden"])

    def test_research_used_metadata_only_and_authorized_nothing(self):
        operations = self.record["research_operations"]
        self.assertGreater(operations["measured_direct_metadata_body_bytes"], 0)
        forbidden_operation_keys = (
            "neural_payload_GETs",
            "MAT_body_GETs",
            "BDF_body_GETs",
            "event_table_reads",
            "row_target_or_per_trial_label_reads",
            "signal_sample_reads",
            "model_fits",
            "prediction_sets",
            "scoring_events",
            "retained_download_bytes",
            "operations_on_consumed_or_ignored_state",
            "operations_on_other_projects",
            "scientific_claim_upgrades",
        )
        self.assertTrue(all(operations[key] == 0 for key in forbidden_operation_keys))
        self.assertTrue(all(value is False for value in self.record["authorization_state"].values()))

    def test_resource_and_claim_boundaries_are_honest(self):
        envelope = self.record["resource_envelope"]
        self.assertLess(envelope["future_payload_bytes"], 1_000_000_000)
        self.assertLessEqual(
            envelope["future_incremental_disk_bytes_maximum"],
            envelope["maintainer_current_data_ceiling_bytes"],
        )
        boundary = self.record["claim_boundary"]
        self.assertTrue(
            all(
                value is False
                for key, value in boundary.items()
                if key != "maximum_future_claim"
            )
        )
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("## Conditional Fusion Architecture", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("not a repair, retry, resume, fallback, or", document)


if __name__ == "__main__":
    unittest.main()
