import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "marc1_http_identity_semantics_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1HTTPIdentitySemanticsImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_http_identity_semantics_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-HT1")
        self.assertEqual(
            self.record["status"],
            "generated_only_implementation_qualified_registered_closeout_not_executed",
        )

    def test_every_artifact_binding_is_current(self) -> None:
        for binding in self.record["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_contract_proof_is_exact(self) -> None:
        proof = self.record["green_contract_proof"]
        self.assertEqual(proof["commit"], "1f99d0a8c5609dae992fa0e245f179c2f417038f")
        self.assertEqual(proof["CI_run_id"], 31_581_395_690)
        self.assertEqual(proof["base_python_job_id"], 94_065_047_494)
        self.assertEqual(proof["optional_neuro_job_id"], 94_065_047_277)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["contract_sha256"],
            "a8b86c56b2ea540715dc09a4a34e0de93f969e3e30dd0ea2d055d366d0c5e73d",
        )

    def test_surface_is_additive_dependency_free_and_closed(self) -> None:
        surface = self.record["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertTrue(surface["python_S_compatible"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        for key in (
            "execute_command",
            "network_client",
            "DNS_resolver",
            "decompressor_or_decoder",
            "private_or_consumed_input_path",
            "signal_event_target_model_or_score_interface",
            "retry_rerun_resume_fallback_or_substitution_interface",
        ):
            with self.subTest(key=key):
                self.assertFalse(surface[key])

    def test_transport_matrix_and_routes_are_exact(self) -> None:
        transport = self.record["transport_qualification"]
        self.assertEqual(transport["accepted_cases"], 4)
        self.assertEqual(transport["accepted_cases_passed"], 4)
        self.assertEqual(transport["refusal_cases"], 20)
        self.assertEqual(transport["refusal_cases_passed"], 20)
        self.assertEqual(
            transport["route_counts"],
            {
                "MARC1HT-F01": 0,
                "MARC1HT-F02": 10,
                "MARC1HT-F03": 8,
                "MARC1HT-F04": 1,
                "MARC1HT-F05": 1,
            },
        )
        self.assertEqual(transport["decompression_or_decoding_operations"], 0)

    def test_selection_privacy_and_replay_are_exact(self) -> None:
        selection = self.record["generated_selection"]
        self.assertEqual(selection["Freewill_rows"], 1_227)
        self.assertEqual(selection["Wrist_rows"], 55)
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_run_bundles"], 72)
        self.assertEqual(selection["Freewill_core_members"], 288)
        self.assertEqual(selection["Wrist_archives"], 12)
        self.assertEqual(selection["private_rows"], 300)
        self.assertTrue(selection["target_quality_size_CRC_and_outcome_free"])
        self.assertTrue(selection["row_order_replay_exact"])
        self.assertTrue(selection["fixed_measurement_output_replay_byte_identical"])

    def test_development_measurements_and_hashes_are_bound(self) -> None:
        result = self.record["development_qualification"]
        self.assertEqual(result["route"], "MARC1HT-G1")
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["acceptance_gates_passed"], 16)
        self.assertEqual(result["generated_input_bytes"], 923_052)
        self.assertEqual(result["aggregate_report_bytes"], 7_064)
        self.assertEqual(result["private_manifest_bytes"], 175_618)
        self.assertEqual(result["combined_output_bytes"], 182_682)
        self.assertLess(result["runtime_seconds"], 30)
        self.assertLess(result["reported_peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(result["external_maximum_RSS_bytes"], 32_669_696)
        self.assertEqual(
            result["aggregate_report_sha256"],
            "adbe2ffd269edbaaaf82113924df361de0e62f45e9fb4a481ecbae7bb0e39beb",
        )
        self.assertEqual(
            result["private_manifest_sha256"],
            "e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831",
        )
        self.assertTrue(result["aggregate_inspect_passed"])
        self.assertTrue(result["temporary_outputs_removed"])
        self.assertFalse(result["generated_artifacts_committed"])

    def test_resource_caps_and_access_counters_are_closed(self) -> None:
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

    def test_verification_counts_add_exactly_twenty_nine_tests(self) -> None:
        tests = self.record["qualification_tests"]
        self.assertEqual(tests["focused_implementation_tests"], 18)
        self.assertEqual(tests["implementation_record_tests"], 11)
        self.assertEqual(tests["final_MARC1_tests"], 389)
        self.assertEqual(tests["dependency_light_tests"], 2_528)
        self.assertEqual(tests["dependency_light_expected_skips"], 204)
        self.assertEqual(tests["optional_neuro_tests"], 2_599)
        self.assertEqual(tests["optional_neuro_expected_skips"], 35)
        self.assertEqual(tests["test_delta"], 29)
        self.assertEqual(tests["additional_skips"], 0)
        for key in (
            "ruff_passed",
            "compile_passed",
            "JSON_validation_passed",
            "CLI_help_and_roundtrip_passed",
            "git_diff_check_passed",
        ):
            with self.subTest(key=key):
                self.assertTrue(tests[key])

    def test_registered_closeout_and_real_inputs_remain_closed(self) -> None:
        gate = self.record["next_gate"]
        self.assertTrue(gate["exact_implementation_must_be_remotely_green"])
        self.assertFalse(gate["registered_generated_closeout_executed"])
        self.assertFalse(gate["real_or_private_metadata_may_be_read"])
        self.assertFalse(gate["public_metadata_may_be_requested"])
        self.assertFalse(gate["payload_acquisition_or_analysis_may_begin"])
        self.assertTrue(gate["later_real_attempt_requires_new_Tier_C_packet"])
        self.assertTrue(gate["later_real_attempt_requires_fresh_packet_bound_decision"])

    def test_human_record_preserves_same_path_and_claim_boundary(self) -> None:
        document = (
            ROOT / "docs" / "MARC_1_HTTP_IDENTITY_SEMANTICS_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("MARC1-HT1 is not a pivot away from thought-to-text", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("registered generated closeout not executed", document)


if __name__ == "__main__":
    unittest.main()
