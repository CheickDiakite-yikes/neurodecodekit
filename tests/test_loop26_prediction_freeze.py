import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "registries" / "loop26_prediction_freeze.v0.json"
DOC_PATH = ROOT / "docs" / "LOOP_26_PREDICTION_FREEZE.md"


class Loop26PredictionFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze_bytes = FREEZE_PATH.read_bytes()
        cls.freeze = json.loads(cls.freeze_bytes)
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_and_exact_inventory_are_frozen(self):
        self.assertEqual(
            hashlib.sha256(self.freeze_bytes).hexdigest(),
            "10191558a68a8c646e32c4ab0516f84ee99d127b9e6a2ea277c432c6c28b2348",
        )
        self.assertEqual(self.freeze["schema_name"], "neurodecodekit.loop26_prediction_freeze")
        self.assertEqual(self.freeze["schema_version"], "0.1.0")
        self.assertEqual(self.freeze["status"], "predictions_frozen_targets_unavailable")
        self.assertEqual(self.freeze["prediction_set_count"], 31)
        self.assertEqual(len(self.freeze["prediction_sets"]), 31)
        self.assertEqual(
            self.freeze["implementation_commit"],
            "4015677d468e428d5bc03f866d98faabfe6379c3",
        )

    def test_exact_access_counters_preserve_target_firewall(self):
        counters = self.freeze["access_counters"]
        expected = {
            "source_cache_stat_reads": 1,
            "source_cache_hash_passes": 1,
            "archive_header_reads": 20,
            "archive_row_member_streams": 8,
            "train_signal_rows_delivered": 55,
            "train_target_rows_delivered": 55,
            "validation_signal_rows_delivered": 6,
            "candidate_training_runs": 18,
            "control_training_runs": 3,
            "optimizer_steps": 5040,
            "checkpoint_writes": 21,
            "checkpoint_reads": 0,
            "target_blind_model_inference_runs": 24,
            "no_signal_prior_fits": 6,
            "prediction_sets_frozen": 31,
        }
        for name, value in expected.items():
            self.assertEqual(counters[name], value, name)
        for name in (
            "validation_target_rows_delivered_before_prediction_freeze",
            "validation_target_rows_delivered_after_prediction_freeze",
            "validation_scoring_runs",
            "source_test_rows_delivered",
            "source_test_scoring_runs",
            "session2_rows_delivered",
            "session2_scoring_runs",
            "raw_fif_or_mat_reads",
            "post_target_parameter_updates",
            "post_target_configuration_changes",
            "external_network_calls",
            "new_downloads",
            "language_model_or_neurotoken_runs",
            "rw3_stream_device_or_hardware_operations",
        ):
            self.assertEqual(counters[name], 0, name)

    def test_record_has_hashes_but_no_plaintext_predictions_or_targets(self):
        self.assertFalse(self.freeze["plaintext_predictions_committed"])
        self.assertEqual(self.freeze["validation_target_rows_delivered"], 0)
        self.assertEqual(self.freeze["validation_scoring_runs"], 0)
        serialized = json.dumps(self.freeze, sort_keys=True)
        for forbidden in ('"predictions"', '"targets"', '"target_texts"'):
            self.assertNotIn(forbidden, serialized)
        required = {
            "condition_id",
            "configuration_sha256",
            "checkpoint_sha256_or_no_checkpoint_reason",
            "transform_sha256_or_identity",
            "ordered_item_ids_sha256",
            "prediction_payload_sha256",
            "lengths_sha256",
            "private_payload_file_sha256",
        }
        self.assertTrue(all(required <= set(row) for row in self.freeze["prediction_sets"]))

    def test_resources_are_within_registered_caps(self):
        resources = self.freeze["resources"]
        self.assertLessEqual(resources["parameter_update_runtime_sec"], 1200)
        self.assertLessEqual(resources["end_to_end_runtime_sec"], 1500)
        self.assertLessEqual(resources["peak_rss_bytes"], 1024**3)
        self.assertLessEqual(resources["checkpoint_bytes"], 4 * 1024**2)
        self.assertLessEqual(resources["prediction_payload_bytes"], 2 * 1024**2)
        self.assertLessEqual(resources["generated_artifact_bytes"], 32 * 1024**2)

    def test_handoff_requires_green_commit_before_target_delivery(self):
        normalized = " ".join(self.doc.split()).casefold()
        self.assertIn("require both remote ci jobs", normalized)
        self.assertIn("targets remain unopened", normalized)
        self.assertIn("no rerun is authorized", normalized)


if __name__ == "__main__":
    unittest.main()
