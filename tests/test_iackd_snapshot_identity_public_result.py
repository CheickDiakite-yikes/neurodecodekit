import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import iackd_snapshot_identity_public as public


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries" / "iackd_snapshot_identity_public_result.v0.json"
RESULT_SHA256 = "79273525d3c598a97399401cfe16b1ba7e437e2ba41c53a53219df3f48b989fe"


class IACKDSnapshotIdentityPublicResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_is_exact_consumed_semantic_refusal(self) -> None:
        self.assertEqual(hashlib.sha256(RESULT_PATH.read_bytes()).hexdigest(), RESULT_SHA256)
        self.assertEqual(
            self.result["status"],
            "public_snapshot_audit_consumed_and_parked",
        )
        self.assertEqual(self.result["route"], public.REFUSAL_IDS[5])
        self.assertEqual(
            self.result["transport"]["failure_stage"],
            "semantic_canonicalization",
        )
        self.assertFalse(self.result["acceptance_gates"]["snapshot_metadata_compatible"])

    def test_exact_green_decision_and_wrapper_are_bound(self) -> None:
        decision = self.result["green_evidence"]["decision"]
        wrapper = self.result["green_evidence"]["wrapper"]
        self.assertEqual(decision["commit"], public.GREEN_DECISION_COMMIT)
        self.assertEqual(decision["push_CI_run_id"], public.GREEN_DECISION_CI_RUN_ID)
        self.assertEqual(
            wrapper["commit"],
            "406bff8bbcfce7b635b0ee4d95096a24288a13e2",
        )
        self.assertEqual(wrapper["push_CI_run_id"], 31487183289)
        self.assertEqual(wrapper["base_python_job_id"], 93765145883)
        self.assertEqual(wrapper["optional_neuro_job_id"], 93765145952)

    def test_one_request_read_and_hash_are_consumed(self) -> None:
        counters = self.result["access_counters"]
        self.assertEqual(counters["public_GraphQL_requests"], 1)
        self.assertEqual(counters["public_response_opens"], 1)
        self.assertEqual(counters["public_response_body_reads"], 1)
        self.assertEqual(counters["public_response_body_bytes"], 595082)
        self.assertEqual(counters["public_response_hashes"], 1)
        self.assertEqual(counters["public_response_semantic_parses"], 0)
        self.assertEqual(counters["private_consumed_markers"], 1)
        self.assertEqual(counters["private_selected_manifests"], 0)
        self.assertEqual(counters["public_aggregate_reports"], 1)

    def test_resource_and_output_measurements_are_bounded(self) -> None:
        measurements = self.result["measurements"]
        self.assertEqual(measurements["request_body_bytes"], 355)
        self.assertEqual(measurements["response_body_bytes"], 595082)
        self.assertEqual(measurements["network_body_bytes"], 595437)
        self.assertEqual(measurements["combined_output_bytes"], 4352)
        self.assertEqual(measurements["incremental_disk_bytes"], 4726)
        self.assertLess(measurements["runtime_seconds_at_final_serialization"], 30)
        self.assertLess(
            measurements["peak_RSS_bytes_at_final_serialization"],
            256 * 1024 * 1024,
        )
        self.assertGreaterEqual(
            measurements["free_disk_bytes_before_consumption"],
            2 * 1024 * 1024 * 1024,
        )
        self.assertLessEqual(measurements["one_minute_load_per_logical_CPU"], 1.0)

    def test_payload_neural_target_model_and_score_counters_are_zero(self) -> None:
        counters = self.result["access_counters"]
        for key in (
            "S3_payload_requests",
            "S3_payload_bytes",
            "local_IACKD_path_operations",
            "old_consumed_root_operations",
            "signal_sample_reads",
            "channel_geometry_event_or_trajectory_reads",
            "target_label_or_trial_reads",
            "training_or_parameter_update_runs",
            "model_inference_runs",
            "prediction_sets",
            "prediction_freezes",
            "target_deliveries",
            "scoring_events",
            "retries_or_reruns",
            "scientific_claim_upgrades",
        ):
            with self.subTest(key=key):
                self.assertEqual(counters[key], 0)

    def test_no_identity_or_private_manifest_claim_survived(self) -> None:
        self.assertIsNone(self.result["snapshot_anchor"])
        self.assertIsNone(self.result["tree_summary"])
        self.assertIsNone(self.result["selected_summary"])
        self.assertIsNone(self.result["critical_metadata"])
        self.assertIn(
            "No public snapshot compatibility result",
            self.result["claim_boundary"]["maximum_result"],
        )
        public.validate_public_result(self.result)

    def test_human_result_records_missing_provenance_and_CLI_defect(self) -> None:
        document = (
            ROOT / "docs" / "IACKD_SNAPSHOT_IDENTITY_PUBLIC_RESULT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("response SHA-256", document)
        self.assertIn("now unavailable", document)
        self.assertIn("CLI Reporting Defect", document)
        self.assertIn("no post-result patch or", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
