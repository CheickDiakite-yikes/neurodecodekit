from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc1_source_aware_live_metadata as live


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc1_source_aware_live_metadata_implementation.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_IMPLEMENTATION.md"
REGISTRY_SHA256 = "b909800fa0c3c3a004e2a08b311b33c4447dea1a389df94ee202f14dc4fe76d5"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
    ).hexdigest()


class MARC1SourceAwareLiveMetadataImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_bytes = REGISTRY_PATH.read_bytes()
        cls.record = json.loads(cls.registry_bytes)

    def test_registry_identity_status_and_lane_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.registry_bytes).hexdigest(), REGISTRY_SHA256)
        self.assertEqual(len(self.registry_bytes), 14_090)
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_source_aware_live_metadata_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-SA1A")
        self.assertEqual(self.record["created_at_local"], "2026-08-13")
        self.assertIn("both_remote_CI_jobs_required", self.record["status"])

    def test_green_parent_decision_precedes_implementation(self) -> None:
        green = self.record["green_parent_decision"]
        self.assertEqual(green["commit"], live.GREEN_DECISION_COMMIT)
        self.assertEqual(green["CI_run_id"], live.GREEN_DECISION_CI_RUN_ID)
        self.assertEqual(green["base_python_job_id"], live.GREEN_DECISION_BASE_JOB_ID)
        self.assertEqual(
            green["optional_neuro_job_id"], live.GREEN_DECISION_OPTIONAL_JOB_ID
        )
        self.assertTrue(green["both_required_jobs_green"])
        self.assertEqual(green["decision_registry_SHA256"], live.DECISION_SHA256)

    def test_implementation_source_and_behavior_test_bindings_match(self) -> None:
        for key in ("implementation_source", "behavior_test"):
            binding = self.record[key]
            with self.subTest(key=key, path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])
                self.assertEqual(_git_blob_sha1(path), binding["git_blob_sha1"])

    def test_loader_replays_record_and_bound_source(self) -> None:
        ledger = live.AccessLedger()
        observed = live.load_implementation_record(
            ROOT,
            expected_sha256=hashlib.sha256(self.registry_bytes).hexdigest(),
            ledger=ledger,
        )
        self.assertEqual(observed, self.record)
        self.assertEqual(ledger.values["repository_reads"], 2)
        self.assertEqual(ledger.values["proof_validations"], 1)

    def test_surface_is_additive_dependency_light_and_payload_free(self) -> None:
        architecture = self.record["architecture"]
        self.assertTrue(architecture["standard_library_only_except_green_attestor"])
        self.assertEqual(architecture["base_dependency_delta"], 0)
        self.assertEqual(
            architecture["commands"], ["plan", "qualify", "inspect", "execute"]
        )
        self.assertTrue(architecture["imports_green_attestor"])
        self.assertFalse(
            architecture[
                "imports_calls_modifies_probes_or_exposes_consumed_live_executor"
            ]
        )
        self.assertFalse(architecture["participant_archive_or_payload_interface_exists"])
        self.assertFalse(
            architecture["signal_event_target_quality_model_or_score_interface_exists"]
        )

    def test_request_and_transport_are_one_shot_and_bounded(self) -> None:
        source = self.record["source_identity"]
        transport = self.record["transport_contract"]
        self.assertEqual((source["record_id"], source["version"]), (29_666_735, 3))
        self.assertEqual(source["query"], "page=1&page_size=1000")
        self.assertEqual((source["request_attempts"], source["redirects"]), (1, 0))
        self.assertEqual(source["accepted_body_count"], 1)
        self.assertEqual(source["accepted_body_cap_bytes"], 2 * 1024**2)
        self.assertEqual((source["payload_requests"], source["payload_bytes"]), (0, 0))
        self.assertTrue(transport["exact_Content_Length_chunked_or_clean_close_framing"])
        self.assertTrue(transport["duplicate_or_conflicting_framing_refused"])
        self.assertEqual(transport["content_decoding_or_decompression_operations"], 0)
        self.assertEqual((transport["retries"], transport["reruns"]), (0, 0))

    def test_semantics_and_route_router_preserve_the_frozen_split(self) -> None:
        semantic = self.record["semantic_contract"]
        routes = self.record["route_contract"]
        self.assertEqual(
            (
                semantic["historical_file_rows"],
                semantic["historical_participant_archives"],
                semantic["historical_supplementary_rows"],
            ),
            (55, 45, 10),
        )
        self.assertEqual(semantic["historical_declared_record_bytes"], 3_683_416_050)
        self.assertEqual(semantic["frozen_selected_subjects_only_if_complete_historical_match"], 12)
        self.assertEqual(semantic["fit_runs_if_eligible"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(semantic["heldout_runs_if_eligible"], [7, 8])
        self.assertEqual(semantic["fit_heldout_overlap"], 0)
        for route in ("MARC1SA-R1", "MARC1SA-R2"):
            self.assertEqual(routes[route]["wrapper_route"], live.SUCCESS_ROUTE)
            self.assertTrue(routes[route]["selection_available"])
        for route in ("MARC1SA-R3", "MARC1SA-R4"):
            self.assertEqual(routes[route]["wrapper_route"], live.BLOCKED_ROUTE)
            self.assertFalse(routes[route]["selection_available"])
        self.assertTrue(routes["every_live_result_or_failure_consumes_lane"])

    def test_output_capability_and_resource_limits_are_exact(self) -> None:
        output = self.record["output_contract"]
        caps = self.record["resource_caps"]
        self.assertEqual(output["registered_root_relative_path"], live.REAL_ROOT_RELATIVE_PATH.as_posix())
        self.assertEqual(output["maximum_files"], 3)
        self.assertEqual(output["allowlisted_files"], list(live.OUTPUT_NAMES))
        self.assertEqual((output["marker_mode"], output["private_manifest_mode"]), ("0600", "0600"))
        self.assertFalse(output["preexisting_path_overwrite_move_delete_or_rename"])
        self.assertFalse(output["success_authorizes_payload_access"])
        self.assertEqual(caps["minimum_free_disk_bytes"], 10 * 1024**3)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["network_body_cap_bytes"], 2 * 1024**2)
        self.assertEqual(caps["incremental_disk_cap_bytes"], 4 * 1024**2)
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )

    def test_generated_qualification_passes_every_exact_gate(self) -> None:
        qualification = self.record["generated_qualification"]
        self.assertEqual(qualification["status"], "passed")
        self.assertEqual(qualification["route"], live.GENERATED_ROUTE)
        self.assertEqual(qualification["semantic_families"], 6)
        self.assertEqual(qualification["generated_fixtures"], 7)
        self.assertEqual(qualification["generated_rows"], 385)
        self.assertEqual(qualification["generated_input_bytes"], 84_422)
        self.assertEqual(qualification["mock_HTTP_calls"], 7)
        self.assertEqual(qualification["adversarial_cases"], 31)
        self.assertEqual(qualification["acceptance_gates_passed"], 20)
        self.assertEqual(
            sorted(qualification["accepted_framing_forms"]),
            ["chunked", "close", "content_length"],
        )
        self.assertTrue(qualification["deterministic_semantic_replay"])
        self.assertTrue(qualification["output_root_removed"])

    def test_generated_measurements_fit_every_cap(self) -> None:
        qualification = self.record["generated_qualification"]
        caps = self.record["resource_caps"]
        self.assertLess(
            qualification["runtime_seconds"], caps["generated_qualification_wall_time_seconds"]
        )
        self.assertLess(
            qualification["external_wall_seconds"],
            caps["generated_qualification_wall_time_seconds"],
        )
        self.assertLess(qualification["reported_peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLess(qualification["external_maximum_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLess(qualification["combined_output_bytes"], caps["combined_output_cap_bytes"])
        self.assertEqual(
            qualification["marker_SHA256"],
            "9d130c565b9e918768a84387c411cb8614c90b054827e658c00664974056c010",
        )
        self.assertEqual(
            qualification["private_manifest_SHA256"],
            "28098678a903a362aa24507dc99ebdfde0ae3b5f8568369077b573e33cedaeb6",
        )

    def test_real_execution_and_every_forbidden_operation_remain_zero(self) -> None:
        qualification = self.record["generated_qualification"]
        for key in (
            "real_public_requests",
            "real_or_private_input_bytes",
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
                self.assertEqual(qualification[key], 0)
        state = self.record["execution_state"]
        self.assertIsNone(state["exact_implementation_commit"])
        self.assertFalse(state["both_required_jobs_green"])
        self.assertFalse(state["public_execution_eligible_now"])
        self.assertFalse(state["public_execution_consumed"])

    def test_next_gate_and_claim_boundary_are_explicit(self) -> None:
        gate = self.record["next_gate"]
        claim = self.record["claim_boundary"]
        self.assertTrue(gate["implementation_commit_required"])
        self.assertTrue(gate["implementation_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["live_request_may_begin_before_green"])
        self.assertTrue(gate["one_live_request_may_begin_after_exact_green_proof"])
        self.assertFalse(gate["payload_or_selective_acquisition_may_begin"])
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["metadata_is_scientific_or_language_evidence"])
        self.assertFalse(claim["current_scientific_claim_upgrade"])

    def test_document_preserves_engineering_and_scientific_boundaries(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "Same Research Path",
            "Every live result or post-marker failure consumes the lane.",
            "Engineering capability added:",
            "Scientific claim not established:",
            "one registered live invocation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
