from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc1_paginated_live_metadata as live


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc1_paginated_live_metadata_implementation.v0.json"
DOCUMENT_PATH = ROOT / "docs/MARC_1_PAGINATED_LIVE_METADATA_IMPLEMENTATION.md"
REGISTRY_SHA256 = "083fe060ccd466380dd990e5478594408ad55a97fcb5417851e9ee2f671291f6"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1PaginatedLiveMetadataImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_bytes = REGISTRY_PATH.read_bytes()
        cls.record = json.loads(cls.registry_bytes)

    def test_registry_identity_hash_and_status_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.registry_bytes).hexdigest(), REGISTRY_SHA256)
        self.assertEqual(len(self.registry_bytes), 12265)
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_paginated_live_metadata_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-LM1")
        self.assertIn("requires_remote_green", self.record["status"])

    def test_all_tracked_file_bindings_match(self) -> None:
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_loader_replays_the_exact_record_and_bindings(self) -> None:
        ledger = live.AccessLedger()
        observed = live.load_implementation_record(
            ROOT,
            expected_sha256=REGISTRY_SHA256,
            ledger=ledger,
        )
        self.assertEqual(observed, self.record)
        self.assertEqual(
            ledger.values["repository_reads"],
            1 + len(self.record["tracked_file_hashes"]),
        )

    def test_green_decision_precedes_implementation(self) -> None:
        green = self.record["green_decision"]
        self.assertEqual(green["commit"], live.GREEN_DECISION_COMMIT)
        self.assertEqual(green["CI_run_id"], live.GREEN_DECISION_CI_RUN_ID)
        self.assertEqual(green["base_python_job_id"], live.GREEN_DECISION_BASE_JOB_ID)
        self.assertEqual(
            green["optional_neuro_job_id"], live.GREEN_DECISION_OPTIONAL_JOB_ID
        )
        self.assertTrue(green["both_required_jobs_green_before_implementation"])
        self.assertFalse(green["scope_expanded"])

    def test_surface_is_additive_dependency_free_and_narrow(self) -> None:
        surface = self.record["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(surface["capability_acquisition_before_repository_fixture_parser_or_network_work"])
        self.assertTrue(surface["registered_path_refused_without_stat_or_open_during_generated_qualification"])
        self.assertEqual(surface["consumed_qualifier_calls"], 0)
        self.assertEqual(surface["consumed_live_executor_imports_or_calls"], 0)
        self.assertFalse(surface["payload_archive_decoder_or_signal_interface"])
        self.assertFalse(surface["target_label_model_prediction_or_score_interface"])

    def test_request_transport_and_inventory_identity_are_frozen(self) -> None:
        transport = self.record["request_and_transport"]
        self.assertEqual(transport["query"], "page=1&page_size=1000")
        self.assertEqual(transport["request_attempts"], 1)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["response_body_cap_bytes"], 2 * 1024**2)
        self.assertEqual(len(transport["accepted_framing"]), 4)
        identity = self.record["semantic_and_selection_identity"]
        self.assertEqual(identity["file_rows"], 55)
        self.assertEqual(identity["participant_archives"], 45)
        self.assertEqual(identity["supplementary_rows"], 10)
        self.assertEqual(identity["declared_record_bytes"], 3_683_416_050)
        self.assertEqual(identity["selected_subjects"], 12)
        self.assertEqual(identity["fit_heldout_overlap"], 0)
        self.assertTrue(identity["selection_target_label_quality_size_checksum_and_outcome_free"])

    def test_output_capability_and_failure_receipt_are_exact(self) -> None:
        output = self.record["output_capability"]
        self.assertTrue(output["process_local_nonserializable"])
        self.assertTrue(output["all_ancestors_no_follow"])
        self.assertTrue(output["parent_relative_exclusive_no_follow_writes"])
        self.assertEqual(output["maximum_files"], 3)
        self.assertEqual(output["consumed_marker_mode"], "0600")
        self.assertEqual(output["private_manifest_mode"], "0600")
        self.assertTrue(output["aggregate_failure_receipt_after_marker"])
        self.assertFalse(output["real_output_cleanup_interface"])

    def test_generated_qualification_passes_every_frozen_case(self) -> None:
        qualification = self.record["generated_qualification"]
        self.assertEqual(qualification["route"], "MARC1LM-G1")
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(qualification["accepted_transport_cases_passed"], 4)
        self.assertEqual(qualification["acceptance_gates_passed"], 20)
        self.assertEqual(qualification["mutations_passed"], 36)
        self.assertEqual(tuple(qualification["mutation_routes"]), live.REQUIRED_MUTATIONS)
        self.assertTrue(
            all(route in live.FAILURE_ROUTES for route in qualification["mutation_routes"].values())
        )

    def test_measurements_fit_every_registered_resource_cap(self) -> None:
        measured = self.record["generated_qualification"]["measurements"]
        caps = self.record["resource_caps"]
        self.assertLess(measured["reported_runtime_seconds"], caps["runtime_seconds"])
        self.assertLess(measured["external_wall_seconds"], caps["runtime_seconds"])
        self.assertLess(measured["reported_peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLess(measured["external_peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLess(measured["combined_output_bytes"], caps["combined_output_bytes"])
        self.assertLess(measured["incremental_disk_bytes"], caps["incremental_disk_bytes"])
        self.assertTrue(measured["temporary_output_removed"])
        verification = self.record["qualification_tests"]
        self.assertEqual(verification["MARC_tests"], 658)
        self.assertEqual(verification["dependency_light_tests"], 2797)
        self.assertEqual(verification["canonical_optional_tests"], 2868)
        self.assertEqual(verification["test_delta"], 33)
        self.assertEqual(verification["skip_delta"], 0)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compile_passed"])

    def test_access_ledger_matches_measured_output_and_forbidden_zeroes(self) -> None:
        qualification = self.record["generated_qualification"]
        ledger = qualification["final_access_counters"]
        self.assertEqual(ledger["output_files_created"], 3)
        self.assertEqual(ledger["output_bytes"], qualification["measurements"]["combined_output_bytes"])
        self.assertEqual(ledger["public_report_inspections"], 1)
        self.assertEqual(ledger["cleanup_file_unlinks"], 3)
        self.assertEqual(ledger["cleanup_directory_removals"], 1)
        self.assertTrue(all(value == 0 for value in self.record["implementation_access_counters"].values()))

    def test_real_execution_remains_closed_until_exact_remote_green(self) -> None:
        state = self.record["execution_state"]
        self.assertTrue(all(value is False for value in state.values()))
        gate = self.record["next_gate"]
        self.assertTrue(gate["commit_push_and_green_this_exact_implementation"])
        self.assertTrue(gate["then_one_registered_metadata_invocation"])
        self.assertTrue(gate["failure_after_marker_consumes_and_parks"])
        self.assertTrue(gate["success_stops_before_payload"])

    def test_document_states_same_path_and_scientific_boundary(self) -> None:
        claim = self.record["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["scientific_claim_established"])
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "It is not a pivot",
            "Engineering capability added:",
            "Scientific claim not established:",
            "Any post-marker failure parks the lane",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
