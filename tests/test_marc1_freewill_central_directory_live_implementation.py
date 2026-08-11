import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc1_freewill_central_directory_live_implementation.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1CentralDirectoryLiveImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_freewill_central_directory_live_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-CD1A")
        self.assertEqual(
            self.record["status"],
            "generated_mock_live_wrapper_qualified_requires_remote_green_before_public_access",
        )

    def test_green_decision_proof_is_bound(self) -> None:
        proof = self.record["green_decision"]
        self.assertEqual(
            proof["commit"],
            "624cc4e99a4aa600b68a333c1bcd84e6cebb9dcd",
        )
        self.assertEqual(proof["push_CI_run_id"], 31519016891)
        self.assertEqual(proof["base_python_job_id"], 93871192638)
        self.assertEqual(proof["optional_neuro_job_id"], 93871192713)
        self.assertEqual(proof["base_python_job_conclusion"], "success")
        self.assertEqual(proof["optional_neuro_job_conclusion"], "success")
        self.assertTrue(proof["both_required_jobs_green"])

    def test_every_tracked_hash_matches(self) -> None:
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_wrapper_is_additive_dependency_free_and_has_no_payload_interface(self) -> None:
        surface = self.record["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertTrue(surface["green_parser_imported_without_modification"])
        self.assertEqual(surface["base_install_dependency_delta"], 0)
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        for key in (
            "user_selected_endpoint_record_version_file_range_or_path_arguments",
            "credential_or_API_key_interface",
            "whole_archive_download_interface",
            "ZIP_extraction_interface",
            "member_local_header_interface",
            "member_payload_interface",
            "participant_signal_target_model_or_score_interface",
            "retry_rerun_resume_or_fallback_interface",
        ):
            with self.subTest(key=key):
                self.assertFalse(surface[key])

    def test_transport_contract_is_three_body_and_no_whole_download(self) -> None:
        transport = self.record["transport_contract"]
        self.assertEqual(transport["declared_archive_bytes"], 13_591_548_048)
        self.assertEqual(transport["tail_bytes"], 128 * 1024)
        self.assertEqual(transport["central_directory_cap_bytes"], 16 * 1024 * 1024)
        self.assertEqual(transport["accepted_response_body_count"], 3)
        self.assertEqual(transport["accepted_response_body_cap_bytes"], 17_039_360)
        self.assertEqual(transport["HTTP_request_attempt_cap"], 5)
        self.assertEqual(transport["bodyless_tail_redirect_cap"], 2)
        self.assertEqual(transport["directory_redirect_cap"], 0)
        self.assertTrue(transport["automatic_redirects_disabled"])
        self.assertTrue(transport["all_redirect_addresses_must_be_globally_routable"])
        self.assertEqual(transport["whole_archive_downloads"], 0)
        self.assertEqual(transport["member_payload_requests"], 0)
        self.assertEqual((transport["retries"], transport["reruns"]), (0, 0))

    def test_machine_and_output_caps_match_decision(self) -> None:
        resources = self.record["resource_caps"]
        self.assertEqual(resources["minimum_free_disk_bytes"], 12 * 1024**3)
        self.assertEqual(resources["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["live_execution_wall_time_seconds"], 120)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["aggregate_public_output_cap_bytes"], 1024 * 1024)
        self.assertEqual(resources["combined_output_cap_bytes"], 8 * 1024 * 1024)
        self.assertEqual(resources["incremental_disk_cap_bytes"], 32 * 1024 * 1024)

    def test_generated_qualification_measurements_are_exact(self) -> None:
        result = self.record["generated_qualification"]
        self.assertEqual(result["route"], "MARC1CDL-G1")
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(
            (result["acceptance_gates_passed"], result["acceptance_gate_count"]),
            (14, 14),
        )
        self.assertEqual(result["generated_input_bytes"], 280_249)
        self.assertEqual(result["entry_count"], 18)
        self.assertEqual(result["central_directory_bytes"], 148_910)
        self.assertEqual(result["inherited_parser_mutations_passed"], 32)
        self.assertEqual(result["wrapper_mutations_passed"], 8)
        self.assertLess(result["runtime_seconds"], 30)
        self.assertLess(result["reported_peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(result["combined_output_bytes"], 12_182)
        self.assertEqual(result["network_client_calls"], 0)
        self.assertEqual(result["public_or_forbidden_counter_sum"], 0)
        self.assertTrue(result["temporary_outputs_removed"])
        self.assertFalse(result["generated_artifacts_committed"])
        self.assertFalse(result["scientific_value"])

    def test_generated_output_hashes_and_byte_counts_are_bound(self) -> None:
        result = self.record["generated_qualification"]
        self.assertEqual(result["aggregate_report_bytes"], 5_995)
        self.assertEqual(
            result["aggregate_report_SHA256"],
            "149eec28f847d072495f1212d8281a63d5b881e821ada57f2668cf5c77195939",
        )
        self.assertEqual(result["private_manifest_bytes"], 6_187)
        self.assertEqual(
            result["private_manifest_SHA256"],
            "94124a9dbbc67099fb0ccfa1cffa5d3c62db4e97d9b6de289e156c9089306ded",
        )
        self.assertEqual(
            result["aggregate_report_bytes"] + result["private_manifest_bytes"],
            result["combined_output_bytes"],
        )

    def test_all_implementation_access_counters_are_zero(self) -> None:
        self.assertTrue(self.record["implementation_access_counters"])
        for key, value in self.record["implementation_access_counters"].items():
            with self.subTest(key=key):
                self.assertEqual(value, 0)

        tests = self.record["qualification_tests"]
        self.assertEqual(tests["final_MARC1_tests"], 198)
        self.assertEqual(tests["dependency_light_tests"], 2337)
        self.assertEqual(tests["dependency_light_expected_skips"], 204)
        self.assertEqual(tests["optional_neuro_tests"], 2408)
        self.assertEqual(tests["optional_neuro_expected_skips"], 35)
        self.assertEqual(tests["optional_neuro_prechange_tests"], 2378)
        self.assertEqual(tests["optional_neuro_prechange_expected_skips"], 35)
        self.assertEqual(tests["test_delta"], 30)
        self.assertEqual(tests["additional_skips"], 0)
        self.assertTrue(tests["ruff_passed"])
        self.assertTrue(tests["compile_passed"])
        self.assertTrue(tests["JSON_validation_passed"])
        self.assertTrue(tests["CLI_help_passed"])
        self.assertTrue(tests["git_diff_check_passed"])

    def test_execution_remains_closed_until_exact_wrapper_is_green(self) -> None:
        state = self.record["execution_state"]
        self.assertFalse(state["implementation_commit_created"])
        self.assertFalse(state["implementation_pushed"])
        self.assertFalse(state["implementation_base_CI_green"])
        self.assertFalse(state["implementation_optional_neuro_CI_green"])
        self.assertFalse(state["public_execution_consumed"])
        self.assertFalse(state["public_execution_may_begin_before_exact_green_wrapper"])
        self.assertFalse(state["retry_available"])
        self.assertFalse(state["rerun_available"])
        gate = self.record["next_gate"]
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["public_request_may_begin_now"])
        self.assertFalse(gate["whole_archive_or_member_acquisition_may_begin"])

    def test_human_record_has_two_sentence_claim_boundary(self) -> None:
        document = (
            ROOT / "docs" / "MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("The implementation never turns", document)
        self.assertIn("whole-file transfer", document)


if __name__ == "__main__":
    unittest.main()
