from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc1_http_identity_live as live


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc1_http_identity_live_result.v0.json"
RESULT_SHA256 = "50a1bd4e97e6149db91d528aa0fce79e6aa5d3cedf79acdb12f03bf4a2d041f2"
DOCUMENT_PATH = ROOT / "docs/MARC_1_HTTP_IDENTITY_LIVE_RESULT.md"


class MARC1HTTPIdentityLiveResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_hash_identity_and_consumed_route_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(RESULT_PATH.read_bytes()).hexdigest(), RESULT_SHA256)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_http_identity_live_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC1-HT1A")
        self.assertEqual(self.result["route"], "MARC1HTL-F04")
        self.assertEqual(
            self.result["status"],
            "consumed_failed_real_metadata_HTTP_identity_selection",
        )

    def test_exact_green_wrapper_preceded_execution(self) -> None:
        proof = self.result["green_evidence"]
        self.assertEqual(
            proof["wrapper_commit"],
            "68ade0d4f6a58c19dbaae954a608080bdc6f128a",
        )
        self.assertEqual(proof["wrapper_CI_run_id"], 31588920988)
        self.assertEqual(proof["wrapper_base_job_id"], 94089099869)
        self.assertEqual(proof["wrapper_optional_neuro_job_id"], 94089099850)
        self.assertEqual(
            proof["implementation_registry_sha256"],
            "30a0728590c1990c7f4d3c68356397fda29e4d5f2158108803d93b21e4ef48af",
        )
        self.assertTrue(proof["both_decision_jobs_green"])
        self.assertTrue(proof["both_wrapper_jobs_green"])

    def test_private_inventory_was_read_once(self) -> None:
        counters = self.result["access_counters"]
        self.assertEqual(counters["private_Freewill_manifest_path_operations"], 1)
        self.assertEqual(counters["private_Freewill_manifest_content_opens"], 1)
        self.assertEqual(counters["private_Freewill_manifest_body_reads"], 1)
        self.assertEqual(counters["private_Freewill_manifest_bytes"], 418_755)
        self.assertEqual(counters["private_Freewill_manifest_hashes"], 1)
        self.assertEqual(counters["private_Freewill_manifest_parses"], 1)
        self.assertEqual(counters["private_consumed_markers"], 1)

    def test_corrected_transport_accepted_one_uncoded_body(self) -> None:
        counters = self.result["access_counters"]
        transport = self.result["transport_summary"]
        self.assertEqual(counters["public_Wrist_metadata_requests"], 1)
        self.assertEqual(counters["public_Wrist_metadata_response_opens"], 1)
        self.assertEqual(counters["public_Wrist_metadata_body_reads"], 1)
        self.assertEqual(counters["public_Wrist_metadata_body_bytes"], 2_917)
        self.assertEqual(counters["public_Wrist_metadata_hashes"], 1)
        self.assertEqual(counters["public_Wrist_metadata_parses"], 1)
        self.assertEqual(transport["HTTP_request_attempts"], 1)
        self.assertEqual(transport["accepted_response_bodies"], 1)
        self.assertEqual(transport["accepted_response_body_bytes"], 2_917)
        self.assertEqual(transport["content_encoding_state"], "absent")
        self.assertTrue(transport["content_length_present"])
        self.assertEqual(transport["decompression_or_decoding_operations"], 0)
        self.assertEqual(
            transport["raw_response_sha256"],
            "4fee5117731a4c8f66efb7b48acb847ac3f0fafcd2b60b2017fb47115c37474c",
        )
        self.assertFalse(transport["raw_headers_published"])
        self.assertFalse(transport["raw_body_persisted"])
        self.assertFalse(transport["terminal_URL_published"])

    def test_semantic_row_count_failure_prevented_selection(self) -> None:
        counters = self.result["access_counters"]
        self.assertEqual(
            self.result["source_summary"]["failure_stage"],
            "target_free_metadata_parse_and_selection",
        )
        self.assertFalse(self.result["acceptance_gates"]["real_metadata_selection_completed"])
        self.assertFalse(self.result["source_summary"]["selection_completed"])
        self.assertFalse(self.result["source_summary"]["payload_opened"])
        self.assertEqual(counters["real_participant_selections"], 0)
        self.assertEqual(counters["real_member_or_archive_selections"], 0)
        self.assertEqual(counters["private_selection_manifests"], 0)

    def test_resources_and_outputs_are_bounded(self) -> None:
        measurements = self.result["measurements"]
        self.assertLess(measurements["runtime_seconds"], 30)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(measurements["input_bytes"], 421_672)
        self.assertEqual(measurements["output_bytes"], 5_006)
        self.assertEqual(measurements["incremental_disk_bytes"], 5_458)
        self.assertEqual(
            (
                measurements["CPU_threads"],
                measurements["workers"],
                measurements["numerical_jobs"],
            ),
            (1, 1, 1),
        )
        machine = measurements["machine_gate"]
        self.assertTrue(machine["passed_before_consumed_marker"])
        self.assertGreaterEqual(machine["free_disk_bytes"], 12 * 1024**3)
        self.assertLessEqual(machine["one_minute_load_per_logical_CPU"], 1.0)

    def test_every_forbidden_counter_remained_zero(self) -> None:
        counters = self.result["access_counters"]
        forbidden = (
            "local_header_requests",
            "member_or_archive_payload_requests",
            "member_or_archive_payload_bytes",
            "signal_sample_reads",
            "channel_geometry_event_onset_or_quality_reads",
            "target_label_response_sentence_key_or_trial_reads",
            "derivative_cache_split_epoch_window_or_feature_operations",
            "training_or_parameter_update_runs",
            "model_inference_runs",
            "prediction_sets",
            "prediction_freezes",
            "target_deliveries",
            "scoring_events",
            "dependency_installs",
            "provider_or_language_model_calls",
            "stream_device_or_hardware_operations",
            "temporary_cleanup_operations",
            "retries_or_reruns",
            "post_result_updates",
            "release_operations",
            "scientific_claim_upgrades",
            "operations_on_other_projects",
        )
        for key in forbidden:
            with self.subTest(key=key):
                self.assertEqual(counters[key], 0)

    def test_public_result_passes_privacy_validator(self) -> None:
        live.validate_public_report(self.result)
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("member_name", serialized)
        self.assertNotIn("download_url", serialized.lower())
        self.assertNotIn("https://", serialized)
        self.assertNotIn(".codex_work", serialized)

    def test_no_rerun_and_claim_boundary_are_explicit(self) -> None:
        gates = self.result["acceptance_gates"]
        self.assertTrue(gates["green_decision_identity"])
        self.assertTrue(gates["green_wrapper_identity"])
        self.assertTrue(gates["preconsumption_machine_gate"])
        self.assertTrue(gates["no_retry_or_rerun_available"])
        self.assertTrue(gates["zero_payload_signal_target_model_score_and_claim_operations"])
        self.assertFalse(gates["real_metadata_selection_completed"])
        self.assertIn(
            "thought-to-text",
            self.result["claim_boundary"]["scientific_claim_not_established"],
        )

    def test_document_is_exact_about_deeper_failure_and_same_path(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for value in (
            RESULT_SHA256,
            "68ade0d4f6a58c19dbaae954a608080bdc6f128a",
            "31588920988",
            "MARC1HTL-F04",
            "no retry or rerun",
            "same research path",
            "actual row count",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(value, document)


if __name__ == "__main__":
    unittest.main()
