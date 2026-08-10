import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/iackd_cue_action_dissociation_result.v0.json"
DOCUMENT_PATH = ROOT / "docs/IACKD_CUE_ACTION_DISSOCIATION_RESULT.md"
FREEZE_PATH = (
    ROOT / "registries/iackd_cue_action_dissociation_prediction_freeze.v0.json"
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDCueActionDissociationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_lane_is_consumed_and_parked_at_registered_failure(self):
        self.assertEqual(
            self.result["status"],
            "acquisition_passed_analysis_consumed_parked_IACKD_F10_no_rerun",
        )
        analysis = self.result["analysis_result"]
        self.assertEqual(
            analysis["failure_id"],
            "IACKD-F10-channel_sampling_or_geometry_failure",
        )
        self.assertEqual(
            analysis["public_error"],
            "BrainVision channel inventory is not 32+4",
        )
        self.assertTrue(analysis["registered_execution_consumed"])
        self.assertFalse(analysis["retry_allowed"])
        self.assertFalse(analysis["rerun_allowed"])

    def test_green_implementation_preceded_every_real_operation(self):
        self.assertEqual(
            self.result["green_implementation"],
            {
                "commit": "f5c36baffefc3889c006a515d06bc42cd2b5cb78",
                "push_ci_run_id": 31409141349,
                "base_python_job_id": 93522699446,
                "optional_neuro_job_id": 93522699599,
                "both_required_jobs_green": True,
            },
        )

    def test_acquisition_measurements_are_exact_and_bounded(self):
        acquisition = self.result["acquisition_result"]
        self.assertEqual(acquisition["selected_objects"], 1340)
        self.assertEqual(acquisition["payload_requests"], 1340)
        self.assertEqual(acquisition["payload_bytes"], 7_249_113_684)
        self.assertEqual(acquisition["stream_hash_passes"], 1340)
        self.assertEqual(acquisition["payload_content_parses"], 0)
        self.assertEqual(acquisition["post_write_content_opens"], 0)
        self.assertEqual(acquisition["retries"], 0)
        self.assertEqual(acquisition["reruns"], 0)
        self.assertLess(acquisition["peak_rss_bytes"], 512 * 1024 * 1024)
        self.assertLess(acquisition["peak_incremental_disk_upper_bound_bytes"], 9 * 1024**3)

    def test_failure_preceded_samples_targets_models_and_freeze(self):
        counters = self.result["analysis_access_counters"]
        self.assertEqual(counters["real_object_hash_passes"], 1340)
        self.assertEqual(counters["brainvision_reader_calls"], 1)
        for name in (
            "signal_sample_materializations",
            "channels_TSV_parses",
            "geometry_parses",
            "events_TSV_parses",
            "ball_stream_parses",
            "leap_stream_parses",
            "target_or_label_rows_delivered_to_model",
            "parameter_update_fits",
            "model_inference_calls",
            "prediction_sets",
            "prediction_freezes",
            "final_target_deliveries",
            "scoring_events",
            "post_target_updates",
            "retries",
            "reruns",
        ):
            self.assertEqual(counters[name], 0, name)
        self.assertFalse(FREEZE_PATH.exists())

    def test_unavailable_values_and_claim_boundary_are_explicit(self):
        unavailable = self.result["unavailable_fields"]
        self.assertIn("observed_channel_count", unavailable)
        self.assertIn("observed_channel_names", unavailable)
        self.assertIn("analysis_peak_rss_bytes", unavailable)
        self.assertEqual(self.result["scientific_route"], "not_reached_before_prediction")
        self.assertFalse(self.result["scientific_claim_upgrade"])

    def test_public_artifact_hashes_and_wording_are_current(self):
        bindings = self.result["public_artifact_bindings"]
        self.assertEqual(bindings["document_sha256"], sha256(DOCUMENT_PATH))
        self.assertEqual(bindings["invariant_test_sha256"], sha256(Path(__file__)))
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("integrity-gate result", document)
        self.assertIn("null neural result.", document)


if __name__ == "__main__":
    unittest.main()
