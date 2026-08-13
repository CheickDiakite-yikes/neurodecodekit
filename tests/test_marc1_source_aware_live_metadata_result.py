from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries" / "marc1_source_aware_live_metadata_result.v0.json"
)
DOCUMENT_PATH = ROOT / "docs" / "MARC_1_SOURCE_AWARE_LIVE_METADATA_RESULT.md"
RESULT_SHA256 = "c5412aa6018006f0bc8c05642ce8f04dce4c0379599f3426cf694f3da34a1662"


class MARC1SourceAwareLiveMetadataResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result_bytes = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.result_bytes)

    def test_result_hash_identity_status_and_route_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.result_bytes).hexdigest(), RESULT_SHA256)
        self.assertEqual(len(self.result_bytes), 8_573)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_source_aware_live_metadata_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC1-SA1A")
        self.assertEqual(self.result["status"], "consumed_complete_selection_blocked")
        self.assertEqual(self.result["route"], "MARC1SAL-R2")

    def test_exact_green_implementation_preceded_execution(self) -> None:
        proof = self.result["proof_order"]
        self.assertEqual(
            proof["implementation_commit"],
            "74aff21bde6495436066c1538e229eb7be5059cc",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 31_672_761_644)
        self.assertEqual(proof["implementation_base_python_job_id"], 94_360_721_568)
        self.assertEqual(proof["implementation_optional_neuro_job_id"], 94_360_722_170)
        self.assertTrue(proof["both_implementation_jobs_green_before_execution"])
        self.assertTrue(proof["tracked_worktree_clean_before_execution"])
        self.assertEqual(
            proof["implementation_registry_sha256"],
            "b909800fa0c3c3a004e2a08b311b33c4447dea1a389df94ee202f14dc4fe76d5",
        )

    def test_one_bounded_metadata_response_and_zero_payload_are_exact(self) -> None:
        source = self.result["source_summary"]
        self.assertEqual((source["record_id"], source["version"]), (29_666_735, 3))
        self.assertEqual(source["query"], "page=1&page_size=1000")
        self.assertEqual((source["request_attempts"], source["redirects"]), (1, 0))
        self.assertEqual(source["accepted_body_count"], 1)
        self.assertEqual(source["accepted_body_cap_bytes"], 2 * 1024**2)
        self.assertIsNone(source["accepted_body_bytes"])
        self.assertEqual(source["participant_archive_requests"], 0)
        self.assertEqual(source["payload_bytes"], 0)

    def test_blocked_route_is_not_overlocalized(self) -> None:
        route = self.result["route_result"]
        self.assertEqual(route["wrapper_route"], "MARC1SAL-R2")
        self.assertIsNone(route["source_aware_route"])
        self.assertEqual(
            route["source_aware_route_candidates"], ["MARC1SA-R3", "MARC1SA-R4"]
        )
        self.assertFalse(route["selection_available"])
        self.assertTrue(route["selection_blocked"])
        self.assertFalse(route["frozen_cohort_available"])
        self.assertEqual(route["selected_subjects"], 0)
        self.assertIsNone(route["historical_differences"])
        self.assertIsNone(route["unknown_extension_status"])
        self.assertFalse(route["specific_difference_inferred"])

    def test_retained_hashes_and_post_execution_privacy_are_exact(self) -> None:
        output = self.result["output_summary"]
        self.assertEqual(output["files_created"], 3)
        self.assertEqual(output["combined_output_bytes"], 23_112)
        self.assertFalse(output["output_removed"])
        for key in (
            "consumed_marker_sha256",
            "private_manifest_sha256",
            "aggregate_report_sha256",
        ):
            with self.subTest(key=key):
                self.assertRegex(output[key], r"\A[0-9a-f]{64}\Z")
        self.assertEqual(output["aggregate_report_inspections"], 1)
        self.assertEqual(output["private_manifest_opens_after_execution"], 0)
        self.assertEqual(output["registered_output_content_opens_after_execution"], 0)
        self.assertEqual(output["registered_output_stat_or_probe_after_execution"], 0)
        self.assertFalse(output["registered_output_committed"])
        self.assertFalse(output["registered_output_deleted_renamed_or_overwritten"])

    def test_resources_fit_every_registered_cap(self) -> None:
        measured = self.result["measurements"]
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["combined_output_bytes"], 2 * 1024**2)
        self.assertLess(measured["incremental_disk_bytes"], 4 * 1024**2)
        self.assertEqual(
            (measured["CPU_threads"], measured["workers"], measured["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertTrue(measured["machine_gate_passed_before_consumed_marker"])
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_every_experiment_or_claim_counter_is_zero(self) -> None:
        counters = self.result["known_access_counters"]
        self.assertEqual(counters["public_HTTP_requests"], 1)
        self.assertEqual(counters["accepted_response_bodies"], 1)
        self.assertEqual(counters["metadata_parses"], 1)
        self.assertEqual(counters["attestations"], 1)
        self.assertEqual(counters["available_selections"], 0)
        for key in (
            "participant_archive_requests",
            "payload_requests",
            "payload_bytes",
            "signal_reads",
            "target_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "scoring_events",
            "provider_model_calls",
            "hardware_operations",
            "operations_on_other_projects",
            "retries",
            "reruns",
            "claim_upgrades",
        ):
            with self.subTest(key=key):
                self.assertEqual(counters[key], 0)

    def test_lane_is_consumed_and_acquisition_stays_closed(self) -> None:
        gates = self.result["acceptance_gates"]
        disposition = self.result["disposition"]
        self.assertTrue(gates["exact_single_request_consumed"])
        self.assertFalse(gates["source_aware_selection_gate_passed"])
        self.assertFalse(gates["payload_gate_opened"])
        self.assertTrue(gates["no_retry_or_rerun_available"])
        self.assertTrue(disposition["lane_consumed"])
        self.assertFalse(disposition["retry_or_rerun_allowed"])
        self.assertFalse(disposition["post_result_parser_or_expectation_amendment_allowed"])
        self.assertFalse(disposition["cohort_selection_eligible"])
        self.assertFalse(disposition["selective_acquisition_eligible"])
        self.assertFalse(disposition["payload_eligible"])

    def test_claim_boundary_keeps_same_path_without_scientific_upgrade(self) -> None:
        claim = self.result["claim_boundary"]
        disposition = self.result["disposition"]
        self.assertTrue(disposition["same_thought_to_text_path"])
        self.assertFalse(disposition["is_pivot"])
        self.assertFalse(claim["scientific_claim_established"])
        self.assertFalse(claim["language_or_thought_to_text_established"])
        self.assertIn("No neural payload", claim["scientific_claim_not_established"])

    def test_document_records_exact_result_uncertainty_and_stop(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        normalized = " ".join(document.split())
        for phrase in (
            RESULT_SHA256,
            "74aff21bde6495436066c1538e229eb7be5059cc",
            "31672761644",
            "MARC1SAL-R2",
            "R3 historical drift or R4 unknown extension",
            "23,112 bytes",
            "Do not retry, rerun, resume",
            "There is no pivot and no manufactured positive result.",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
