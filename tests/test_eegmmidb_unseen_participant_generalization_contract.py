import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries/eegmmidb_unseen_participant_generalization_contract.v0.json"
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_GENERALIZATION_PREREGISTRATION.md"


class EEGMMIDBUnseenParticipantGeneralizationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_all_current_authority_is_false(self):
        self.assertEqual(self.contract["status"], "preregistered_all_authority_false")
        self.assertTrue(all(value is False for value in self.contract["authority_now"].values()))

    def test_split_binding_is_strict_and_zero_calibration(self):
        source = self.contract["source_partition"]
        fresh = self.contract["fresh_partition"]
        self.assertEqual(source["participants"], [f"S{i:03d}" for i in range(1, 16)])
        self.assertEqual(fresh["participants"], [f"S{i:03d}" for i in range(16, 31)])
        self.assertEqual(source["execution_runs"], [3, 7])
        self.assertEqual(source["imagery_runs"], [4, 8])
        self.assertEqual(source["forbidden_runs"], [11, 12])
        self.assertEqual(fresh["execution_run"], 11)
        self.assertEqual(fresh["imagery_run"], 12)
        self.assertEqual(fresh["calibration_rows"], 0)
        self.assertEqual(fresh["normalization_fit_rows"], 0)
        self.assertEqual(fresh["threshold_or_selection_rows"], 0)

    def test_stages_and_barriers_are_ordered(self):
        self.assertEqual(
            self.contract["ordered_stages"],
            [
                "G_generated_and_mocked_implementation_qualification",
                "M_metadata_only_exact_inventory_freeze",
                "S_six_source_file_acquisition_source_LOSO_and_checkpoint_freeze",
                "F_thirty_fresh_file_acquisition_target_blind_prediction_freeze",
                "T_one_combined_target_delivery_and_score",
            ],
        )
        self.assertTrue(all(self.contract["freeze_barriers"].values()))

    def test_model_controls_and_gates_are_fixed(self):
        model = self.contract["model"]
        self.assertEqual(model["feature_dimension"], 320)
        self.assertEqual(model["model_candidates"], 1)
        self.assertEqual(model["hyperparameter_searches"], 0)
        self.assertFalse(model["test_time_adaptation"])
        self.assertEqual(len(self.contract["conditions"]), 12)
        self.assertEqual(
            self.contract["fresh_execution_gate"]["macro_margin_over_max_no_signal_timing_minimum"],
            0.10,
        )

    def test_resources_are_bounded_and_one_shot(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertLessEqual(caps["payload_network_bytes_maximum"], 256 << 20)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 512 << 20)
        self.assertLessEqual(caps["peak_RSS_bytes_maximum"], 1 << 30)
        self.assertEqual(caps["final_target_deliveries"], 1)
        self.assertEqual(caps["final_scoring_events"], 1)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertEqual(caps["post_target_updates"], 0)

    def test_preregistration_preserves_claim_boundary(self):
        boundary = self.contract["claim_boundary"]
        self.assertEqual(boundary["maximum_route"], "EEGMMIDBUG1-R4")
        self.assertFalse(boundary["motor_cortex_or_movement_intention"])
        self.assertFalse(boundary["EEG_beyond_eyes_or_peripheral_signals"])
        self.assertFalse(boundary["language_or_thought_decoding"])
        self.assertFalse(boundary["live_decoding"])
        self.assertIn(
            "This preregistration authorizes nothing", DOCUMENT.read_text(encoding="utf-8")
        )


if __name__ == "__main__":
    unittest.main()
