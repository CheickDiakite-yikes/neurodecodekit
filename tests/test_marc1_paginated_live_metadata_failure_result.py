from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc1_paginated_live_metadata_failure_result.v0.json"
DOCUMENT_PATH = ROOT / "docs/MARC_1_PAGINATED_LIVE_METADATA_RESULT.md"
RESULT_SHA256 = "6e3e488976eb78228f4ffe66d1ac7fc8332ca42a0512d165cbb517be140a2086"


class MARC1PaginatedLiveMetadataFailureResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result_bytes = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.result_bytes)

    def test_result_hash_identity_and_consumed_route_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.result_bytes).hexdigest(), RESULT_SHA256)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_paginated_live_metadata_failure_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC1-LM1")
        self.assertEqual(self.result["route"], "MARC1LM-F04")
        self.assertEqual(self.result["status"], "consumed_failed_real_metadata")

    def test_exact_green_implementation_preceded_execution(self) -> None:
        proof = self.result["proof_order"]
        self.assertEqual(
            proof["implementation_commit"],
            "f9a1eceb8ee432e57e19c6af2db355aadd53b1e3",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 31611639130)
        self.assertEqual(proof["implementation_base_python_job_id"], 94164152160)
        self.assertEqual(proof["implementation_optional_neuro_job_id"], 94164152302)
        self.assertTrue(proof["both_implementation_jobs_green_before_execution"])
        self.assertEqual(
            proof["implementation_registry_sha256"],
            "1943fbfdb90a2b8ae455db277e39434f38e0aa6bbc279c443c47355213a498a2",
        )

    def test_one_bounded_metadata_body_reached_inventory_validation(self) -> None:
        source = self.result["source_summary"]
        failure = self.result["failure_localization"]
        self.assertEqual(source["request_attempts"], 1)
        self.assertEqual(source["redirects"], 0)
        self.assertEqual(source["accepted_body_reads"], 1)
        self.assertEqual(source["accepted_body_bytes"], 15_652)
        self.assertEqual(source["metadata_parses"], 1)
        self.assertTrue(failure["strict_JSON_list_reached_inventory_validator"])
        self.assertEqual(failure["safe_reason"], "frozen inventory validation refused")

    def test_failure_is_not_overlocalized(self) -> None:
        failure = self.result["failure_localization"]
        self.assertFalse(failure["validated_inventory_available"])
        self.assertFalse(failure["actual_row_count_published"])
        self.assertFalse(failure["actual_rows_or_changed_fields_published"])
        self.assertFalse(failure["specific_inventory_predicate_inferred"])
        self.assertEqual(failure["selected_subjects"], 0)

    def test_resources_fit_registered_caps(self) -> None:
        measured = self.result["measurements"]
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["network_body_bytes"], 2 * 1024**2)
        self.assertLess(measured["combined_output_bytes"], 2 * 1024**2)
        self.assertLess(measured["incremental_disk_bytes"], 4 * 1024**2)
        self.assertGreaterEqual(measured["machine_gate"]["free_disk_bytes"], 10 * 1024**3)
        self.assertLessEqual(
            measured["machine_gate"]["one_minute_load_per_logical_CPU"], 1.0
        )
        self.assertEqual(
            (measured["CPU_threads"], measured["workers"], measured["numerical_jobs"]),
            (1, 1, 1),
        )

    def test_every_experiment_counter_remained_zero(self) -> None:
        counters = self.result["access_counters"]
        for key in (
            "participant_archive_requests",
            "payload_bytes",
            "selections",
            "signal_reads",
            "target_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "scoring_events",
            "provider_model_calls",
            "hardware_operations",
            "operations_on_other_projects",
            "claim_upgrades",
            "retries",
            "reruns",
        ):
            with self.subTest(key=key):
                self.assertEqual(counters[key], 0)

    def test_private_surface_was_not_reopened_or_committed(self) -> None:
        private = self.result["private_surface_posture"]
        self.assertEqual(private["aggregate_report_inspections"], 1)
        self.assertEqual(private["private_manifest_opens_after_execution"], 0)
        self.assertEqual(private["raw_response_or_row_publications"], 0)
        self.assertFalse(private["registered_output_committed"])
        self.assertFalse(private["registered_output_deleted_or_renamed"])

    def test_lane_is_consumed_and_payload_gate_stays_closed(self) -> None:
        gates = self.result["acceptance_gates"]
        disposition = self.result["disposition"]
        self.assertTrue(gates["exact_single_request_consumed"])
        self.assertFalse(gates["frozen_inventory_validation_passed"])
        self.assertFalse(gates["payload_gate_opened"])
        self.assertTrue(gates["no_retry_or_rerun_available"])
        self.assertTrue(disposition["lane_consumed"])
        self.assertFalse(disposition["retry_or_rerun_allowed"])
        self.assertFalse(disposition["payload_eligible"])

    def test_claim_boundary_keeps_the_same_path_without_overclaiming(self) -> None:
        claim = self.result["claim_boundary"]
        disposition = self.result["disposition"]
        self.assertTrue(disposition["same_thought_to_text_path"])
        self.assertFalse(disposition["is_pivot"])
        self.assertFalse(claim["scientific_claim_established"])
        self.assertFalse(claim["language_or_thought_to_text_established"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])

    def test_document_records_exact_result_and_uncertainty(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        normalized = " ".join(document.split())
        for phrase in (
            RESULT_SHA256,
            "f9a1eceb8ee432e57e19c6af2db355aadd53b1e3",
            "31611639130",
            "MARC1LM-F04",
            "15,652-byte",
            "actual row count",
            "There is no pivot.",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
