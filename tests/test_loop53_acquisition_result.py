import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "registries/loop53_acquisition_result.v0.json"
DOC_PATH = REPO_ROOT / "docs/LOOP_53_ACQUISITION_RESULT.md"


class Loop53AcquisitionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_result_is_consumed_passed_and_hash_bound_to_green_milestones(self):
        result = self.result
        self.assertEqual(result["schema_name"], "neurodecodekit.loop53_acquisition_result")
        self.assertEqual(result["schema_version"], "0.1.0")
        self.assertEqual(result["status"], "consumed_passed_no_rerun_stop_before_loop54")
        milestones = result["authorization_and_implementation"]
        self.assertEqual(
            milestones["implementation_commit"],
            "8ec5b1b978e2401f77638f59d9262f34accf17ec",
        )
        self.assertEqual(milestones["implementation_push_ci_run_id"], 29591387642)
        self.assertEqual(milestones["implementation_pull_request_ci_run_id"], 29591391286)
        self.assertTrue(milestones["both_implementation_workflows_green_before_execution"])

    def test_exact_source_identity_and_acquisition_bytes_passed(self):
        source = self.result["source_identity"]
        measurements = self.result["measurements"]
        self.assertEqual(source["repository"], "bcbl190626/SpanishBCBL")
        self.assertEqual(source["revision"], "88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684")
        self.assertEqual(source["license_id"], "cc-by-nc-4.0")
        self.assertEqual(source["registered_file_count"], 4)
        self.assertEqual(source["registered_payload_bytes"], 96090264)
        self.assertTrue(source["all_registered_path_size_git_lfs_and_xet_identities_matched"])
        self.assertFalse(source["substitution_used"])
        self.assertEqual(measurements["network_payload_bytes"], 96090264)
        self.assertEqual(measurements["final_payload_bytes"], 96090264)
        self.assertEqual(measurements["final_file_count"], 4)

    def test_resources_and_private_receipts_are_within_frozen_caps(self):
        measurements = self.result["measurements"]
        private = self.result["private_artifact_bindings"]
        self.assertLessEqual(measurements["runtime_seconds"], 600)
        self.assertLessEqual(measurements["peak_rss_bytes"], 512 * 1024 * 1024)
        self.assertLessEqual(measurements["network_payload_bytes"], 128 * 1024 * 1024)
        self.assertLessEqual(measurements["incremental_disk_peak_bytes"], 256 * 1024 * 1024)
        self.assertGreaterEqual(measurements["free_disk_before_bytes"], 2 * 1024 * 1024 * 1024)
        self.assertEqual(measurements["cpu_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertFalse(measurements["end_to_end_latency_measured"])
        self.assertIsNone(measurements["producer_causal"])
        self.assertEqual(private["combined_receipt_bytes"], 8265)
        self.assertEqual(
            private["machine_manifest_bytes"] + private["human_receipt_bytes"],
            private["combined_receipt_bytes"],
        )
        self.assertLessEqual(private["combined_receipt_bytes"], 1024 * 1024)
        self.assertFalse(private["payload_committed"])
        self.assertFalse(private["private_receipts_committed"])

    def test_all_frozen_gates_pass_and_forbidden_counters_are_zero(self):
        self.assertEqual(len(self.result["acceptance_gate_results"]), 10)
        self.assertTrue(all(self.result["acceptance_gate_results"].values()))
        counters = self.result["access_counters"]
        self.assertEqual(counters["registered_acquisition_invocations"], 1)
        self.assertEqual(counters["metadata_calls"], 2)
        self.assertEqual(counters["payload_download_invocations"], 1)
        self.assertEqual(counters["payload_file_requests"], 4)
        self.assertEqual(counters["opaque_hash_reads"], 4)
        for key in (
            "header_reads",
            "marker_reads",
            "signal_reads",
            "mat_reads",
            "target_or_label_reads",
            "cache_reads_or_writes",
            "split_operations",
            "model_or_checkpoint_loads",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "scoring_runs",
            "language_model_runs",
            "rw3_stream_device_or_hardware_operations",
            "additional_file_requests",
            "additional_participant_operations",
            "reruns",
        ):
            self.assertEqual(counters[key], 0, key)

    def test_public_result_excludes_private_per_file_content_hashes(self):
        source = RESULT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("content_sha256", source)
        self.assertFalse(
            self.result["private_artifact_bindings"][
                "per_file_local_content_hashes_publicly_repeated"
            ]
        )
        for key in ("machine_manifest_sha256", "human_receipt_sha256"):
            value = self.result["private_artifact_bindings"][key]
            self.assertEqual(len(value), 64)
            int(value, 16)

    def test_unavailable_fields_claim_ceiling_and_loop54_stop_are_explicit(self):
        unavailable = set(self.result["unavailable_fields"])
        self.assertTrue(
            {
                "channel_count",
                "sampling_rate_hz",
                "event_count",
                "trial_count",
                "target_text",
                "signal_quality",
                "neural_advantage",
                "decoding_accuracy",
                "end_to_end_latency",
            }.issubset(unavailable)
        )
        next_gate = self.result["next_gate"]
        self.assertFalse(next_gate["loop54_authorized_now"])
        self.assertTrue(next_gate["stop_before_loop54"])
        self.assertIn("no evidence", self.result["claim_boundary"]["scientific_claim_not_established"])
        normalized = " ".join(self.doc.split()).lower()
        self.assertIn("consumed; acquisition passed; no rerun; stop before loop 54", normalized)
        self.assertIn("no parser was called", normalized)
        self.assertIn("scientific claim not established", normalized)


if __name__ == "__main__":
    unittest.main()
