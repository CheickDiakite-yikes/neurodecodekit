from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc1_versioned_pagination_implementation.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/MARC_1_VERSIONED_PAGINATION_IMPLEMENTATION.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1VersionedPaginationImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_versioned_pagination_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-PG1")
        self.assertEqual(
            self.record["status"],
            "generated_only_implementation_qualified_registered_closeout_not_executed",
        )

    def test_every_artifact_binding_is_current(self) -> None:
        for binding in self.record["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_green_contract_proof_is_exact(self) -> None:
        proof = self.record["green_contract_proof"]
        self.assertEqual(
            proof["commit"],
            "ccb3ba8a839b3e6fc6844ad867ab0d5d295e20fb",
        )
        self.assertEqual(proof["CI_run_id"], 31591853349)
        self.assertEqual(proof["base_python_job_id"], 94098410925)
        self.assertEqual(proof["optional_neuro_job_id"], 94098410868)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["contract_sha256"],
            "22f7e3ba36f0c92af600d5a00a90581c44338609de19105cf6be374b5fad7a9b",
        )

    def test_surface_is_dependency_free_and_operationally_closed(self) -> None:
        surface = self.record["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertTrue(surface["python_S_compatible"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        for key, value in surface.items():
            if key not in {
                "standard_library_only",
                "python_S_compatible",
                "base_dependency_delta",
                "commands",
            }:
                with self.subTest(key=key):
                    self.assertFalse(value)

    def test_request_and_response_boundary_is_exact(self) -> None:
        request = self.record["request_qualification"]
        self.assertEqual(request["query"], "page=1&page_size=1000")
        self.assertEqual((request["page"], request["page_size"]), (1, 1000))
        self.assertEqual(request["serialized_bytes"], 154)
        self.assertEqual(
            request["serialized_sha256"],
            "95b490f61ee3f563b39344ac09414ff83b06b61339426a4260693c5c567b3b45",
        )
        self.assertEqual(request["response_body_count"], 1)
        self.assertEqual(request["second_page_requests"], 0)
        self.assertEqual(request["fallback_requests"], 0)

    def test_all_cases_gates_and_routes_are_qualified(self) -> None:
        result = self.record["generated_qualification"]
        self.assertEqual((result["accepted_cases"], result["accepted_cases_passed"]), (4, 4))
        self.assertEqual((result["refusal_cases"], result["refusal_cases_passed"]), (41, 41))
        self.assertEqual(
            (result["acceptance_gates"], result["acceptance_gates_passed"]),
            (18, 18),
        )
        self.assertEqual(result["route"], "MARC1PG-G1")
        self.assertEqual(sum(result["route_counts"].values()), 41)
        self.assertEqual(
            set(result["route_counts"]),
            {f"MARC1PG-F0{index}" for index in range(8)},
        )
        self.assertTrue(result["semantic_hashes_identical"])
        self.assertTrue(result["ten_row_default_page_refused"])

    def test_selection_identity_and_privacy_are_exact(self) -> None:
        identity = self.record["semantic_and_selection_identity"]
        self.assertEqual(identity["Wrist_rows"], 55)
        self.assertEqual(identity["Wrist_participant_archives"], 45)
        self.assertEqual(identity["Wrist_supplementary_rows"], 10)
        self.assertEqual(identity["Wrist_declared_record_bytes"], 3683416050)
        self.assertEqual(identity["selected_subjects_per_axis"], 12)
        self.assertEqual(identity["Freewill_run_bundles"], 72)
        self.assertEqual(identity["Freewill_core_members"], 288)
        self.assertEqual(identity["private_selection_rows"], 300)
        self.assertEqual(identity["fit_heldout_overlap"], 0)
        self.assertFalse(identity["participant_IDs_public"])
        self.assertFalse(identity["partial_page_or_cohort_accepted"])

    def test_development_measurements_hashes_and_cleanup_are_bound(self) -> None:
        result = self.record["development_qualification"]
        self.assertEqual(result["route"], "MARC1PG-G1")
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["generated_input_bytes"], 1019776)
        self.assertEqual(result["aggregate_report_bytes"], 7681)
        self.assertEqual(result["private_manifest_bytes"], 175674)
        self.assertEqual(result["combined_output_bytes"], 183355)
        self.assertLess(result["runtime_seconds"], 30)
        self.assertLess(result["reported_peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(result["external_maximum_RSS_bytes"], 40108032)
        self.assertEqual(
            result["aggregate_report_sha256"],
            "7895ffa73b94ccf1ac7fc979469092c9657b48feab9ba6fbef2b8c784392c369",
        )
        self.assertEqual(
            result["private_manifest_sha256"],
            "e835e41a2494268c7795ca72e2e6ef9f01d0494767c9c70b4e76c382c6e609b4",
        )
        self.assertTrue(result["aggregate_inspect_passed"])
        self.assertTrue(result["temporary_outputs_removed"])
        self.assertFalse(result["generated_artifacts_committed"])

    def test_resources_and_forbidden_access_counters_are_closed(self) -> None:
        caps = self.record["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["generated_input_bytes"], 2 * 1024**2)
        self.assertEqual(caps["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["incremental_disk_bytes"], 4 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertTrue(self.record["implementation_access_counters"])
        self.assertTrue(
            all(value == 0 for value in self.record["implementation_access_counters"].values())
        )

    def test_verification_counts_add_exactly_29_tests(self) -> None:
        tests = self.record["qualification_tests"]
        self.assertEqual(tests["focused_behavior_tests"], 18)
        self.assertEqual(tests["implementation_record_tests"], 11)
        self.assertEqual(tests["final_MARC1_tests"], 518)
        self.assertEqual(tests["dependency_light_tests"], 2657)
        self.assertEqual(tests["dependency_light_expected_skips"], 204)
        self.assertEqual(tests["optional_neuro_tests"], 2728)
        self.assertEqual(tests["optional_neuro_expected_skips"], 35)
        self.assertEqual(tests["test_delta"], 29)
        self.assertEqual(tests["additional_skips"], 0)
        for key in (
            "ruff_passed",
            "compile_passed",
            "JSON_validation_passed",
            "CLI_help_plan_qualify_inspect_passed",
            "git_diff_check_passed",
        ):
            with self.subTest(key=key):
                self.assertTrue(tests[key])

    def test_next_gate_and_human_claim_boundary_are_explicit(self) -> None:
        gate = self.record["next_gate"]
        self.assertTrue(gate["exact_implementation_must_be_remotely_green"])
        self.assertFalse(gate["registered_generated_closeout_executed"])
        self.assertFalse(gate["real_or_private_metadata_may_be_read"])
        self.assertFalse(gate["dataset_specific_metadata_may_be_requested"])
        self.assertFalse(gate["payload_acquisition_or_analysis_may_begin"])
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("registered generated\ncloseout not executed", document)
        self.assertIn("not a pivot away from thought-to-text", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
