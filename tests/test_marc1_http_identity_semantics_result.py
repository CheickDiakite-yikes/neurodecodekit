import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries" / "marc1_http_identity_semantics_result.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1HTTPIdentitySemanticsResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_result_identity_route_and_consumed_status(self) -> None:
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_http_identity_semantics_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC1-HT1")
        self.assertEqual(self.result["route"], "MARC1HT-G1")
        self.assertEqual(
            self.result["status"],
            "passed_registered_generated_closeout_consumed_no_rerun",
        )

    def test_green_implementation_proof_preceded_closeout(self) -> None:
        proof = self.result["green_implementation_proof"]
        self.assertEqual(proof["commit"], "b2cb48cc1c630cf2d22186732e8258619db0a930")
        self.assertEqual(proof["CI_run_id"], 31_583_931_303)
        self.assertEqual(proof["base_python_job_id"], 94_073_234_688)
        self.assertEqual(proof["optional_neuro_job_id"], 94_073_234_607)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_every_committed_artifact_binding_is_current(self) -> None:
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_all_registered_transport_and_acceptance_gates_passed(self) -> None:
        execution = self.result["registered_execution"]
        self.assertEqual(execution["accepted_response_cases"], 4)
        self.assertEqual(execution["accepted_response_cases_passed"], 4)
        self.assertEqual(execution["refusal_cases"], 20)
        self.assertEqual(execution["refusal_cases_passed"], 20)
        self.assertEqual(execution["acceptance_gates"], 16)
        self.assertEqual(execution["acceptance_gates_passed"], 16)
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_selection_and_split_replay_are_exact(self) -> None:
        selection = self.result["selection_summary"]
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_run_bundles"], 72)
        self.assertEqual(selection["Freewill_core_members"], 288)
        self.assertEqual(selection["Wrist_archives"], 12)
        self.assertEqual(selection["private_rows"], 300)
        self.assertEqual(selection["fit_heldout_overlap"], 0)
        self.assertTrue(selection["row_order_replay_exact"])
        self.assertTrue(selection["target_quality_size_CRC_and_outcome_free"])

    def test_output_hashes_sizes_modes_and_removal_are_exact(self) -> None:
        output = self.result["output_receipt"]
        self.assertEqual(output["aggregate_report_bytes"], 7_063)
        self.assertEqual(output["private_manifest_bytes"], 175_618)
        self.assertEqual(output["combined_output_bytes"], 182_681)
        self.assertEqual(output["incremental_disk_bytes"], 182_681)
        self.assertEqual(output["private_manifest_mode"], "0600")
        self.assertEqual(output["aggregate_report_mode"], "0644")
        self.assertEqual(
            output["aggregate_report_sha256"],
            "865e69d4b263dd311c48ad301e29dadc2050962f871bf87405193aa77c394299",
        )
        self.assertEqual(
            output["private_manifest_sha256"],
            "e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831",
        )
        self.assertEqual(output["aggregate_report_inspections"], 1)
        self.assertTrue(output["temporary_outputs_removed"])
        self.assertFalse(output["generated_outputs_committed"])

    def test_runtime_memory_and_storage_caps_passed(self) -> None:
        measurements = self.result["measurements"]
        self.assertEqual(measurements["generated_input_bytes"], 923_052)
        self.assertLess(measurements["runtime_seconds"], 30)
        self.assertLess(measurements["reported_peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(measurements["external_maximum_RSS_bytes"], 33_095_680)
        self.assertEqual(
            (measurements["CPU_threads"], measurements["workers"], measurements["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(measurements["network_bytes"], 0)
        self.assertEqual(measurements["real_or_private_input_bytes"], 0)

    def test_every_real_neural_model_score_and_claim_counter_is_zero(self) -> None:
        counters = self.result["access_counters"]
        self.assertTrue(counters)
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_closeout_is_consumed_and_real_work_remains_closed(self) -> None:
        closeout = self.result["consumption_and_next_gate"]
        self.assertTrue(closeout["registered_generated_closeout_consumed"])
        self.assertEqual(closeout["retries"], 0)
        self.assertEqual(closeout["reruns"], 0)
        self.assertFalse(closeout["real_metadata_wrapper_may_be_implemented"])
        self.assertFalse(closeout["private_or_public_metadata_may_be_read"])
        self.assertFalse(closeout["payload_acquisition_or_analysis_may_begin"])
        self.assertTrue(closeout["result_must_be_remotely_green_before_Tier_C_request"])

    def test_verification_counts_add_exactly_eleven_result_tests(self) -> None:
        tests = self.result["qualification_tests"]
        self.assertEqual(tests["result_tests"], 11)
        self.assertEqual(tests["final_MARC1_tests"], 400)
        self.assertEqual(tests["dependency_light_tests"], 2_539)
        self.assertEqual(tests["dependency_light_expected_skips"], 204)
        self.assertEqual(tests["optional_neuro_tests"], 2_610)
        self.assertEqual(tests["optional_neuro_expected_skips"], 35)
        self.assertEqual(tests["test_delta"], 11)
        self.assertEqual(tests["additional_skips"], 0)
        for key in (
            "ruff_passed",
            "compile_passed",
            "JSON_validation_passed",
            "git_diff_check_passed",
        ):
            with self.subTest(key=key):
                self.assertTrue(tests[key])

    def test_human_result_preserves_same_path_and_claim_boundary(self) -> None:
        document = (
            ROOT / "docs" / "MARC_1_HTTP_IDENTITY_SEMANTICS_RESULT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("not a pivot away from thought-to-text", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("closeout is consumed", document)
        self.assertIn("retry or rerun", document)


if __name__ == "__main__":
    unittest.main()
