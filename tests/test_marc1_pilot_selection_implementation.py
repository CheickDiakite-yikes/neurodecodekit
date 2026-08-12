import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc1_privacy_preserving_pilot_selection_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1PilotSelectionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_privacy_preserving_pilot_selection_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-P1")
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
        self.assertEqual(
            proof["commit"],
            "d1218066e64dea502d263acf0c096ed7eab55a11",
        )
        self.assertEqual(proof["CI_run_id"], 31_569_417_204)
        self.assertEqual(proof["base_job_id"], 94_028_013_357)
        self.assertEqual(proof["optional_neuro_job_id"], 94_028_013_230)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["contract_sha256"],
            "2099849ad13c6c1a97488e81cef8b21dcd61e59914d00fd43b9e76e8ccd5c39c",
        )

    def test_interface_is_dependency_free_generated_only_and_closed(self) -> None:
        interface = self.record["implementation_surface"]
        self.assertTrue(interface["standard_library_only"])
        self.assertTrue(interface["python_S_compatible"])
        self.assertEqual(interface["base_dependency_delta"], 0)
        self.assertEqual(interface["commands"], ["plan", "qualify", "inspect"])
        for key in (
            "execute_command",
            "network_client",
            "real_inventory_or_metadata_path_argument",
            "participant_seed_size_or_split_override",
            "archive_local_header_or_payload_reader",
            "event_signal_target_quality_model_or_score_interface",
            "retry_rerun_or_fallback_interface",
        ):
            with self.subTest(key=key):
                self.assertFalse(interface[key])

    def test_generated_fixtures_and_selection_are_exact(self) -> None:
        fixtures = self.record["generated_fixtures"]
        self.assertEqual(fixtures["Freewill_rows"], 1_227)
        self.assertEqual(fixtures["Freewill_regular_files"], 1_025)
        self.assertEqual(fixtures["Freewill_directories"], 202)
        self.assertEqual(fixtures["Wrist_rows"], 55)
        self.assertEqual(fixtures["Wrist_participant_archives"], 45)
        self.assertEqual(fixtures["Wrist_supplementary_rows"], 10)
        selection = self.record["selection_contract"]
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_run_bundles"], 72)
        self.assertEqual(selection["Freewill_core_members"], 288)
        self.assertEqual(selection["Wrist_selected_archives"], 12)
        self.assertEqual(selection["private_selection_rows"], 300)
        self.assertTrue(selection["row_order_invariant"])
        self.assertTrue(selection["size_and_CRC_independent_identity"])

    def test_caps_and_firewall_are_exact(self) -> None:
        caps = self.record["resource_caps"]
        self.assertEqual(caps["Freewill_payload_bytes"], 6 * 1024**3)
        self.assertEqual(caps["Wrist_payload_bytes"], 2 * 1024**3)
        self.assertEqual(caps["joint_payload_bytes"], 8 * 1024**3)
        self.assertEqual(caps["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        firewall = self.record["target_firewall"]
        self.assertTrue(firewall["selection_is_target_free"])
        self.assertEqual(firewall["forbidden_selection_fields"], 9)
        self.assertEqual(firewall["content_reader_count"], 0)
        self.assertEqual(firewall["model_or_scorer_count"], 0)

    def test_all_mutations_and_development_measurements_are_bound(self) -> None:
        mutations = self.record["mutation_qualification"]
        self.assertEqual(mutations["required"], 36)
        self.assertEqual(mutations["passed"], 36)
        self.assertEqual(sum(mutations["route_counts"].values()), 36)
        result = self.record["development_qualification"]
        self.assertEqual(result["route"], "MARC1PSG-R1")
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["generated_input_bytes"], 873_348)
        self.assertEqual(result["generated_output_bytes"], 182_563)
        self.assertEqual(result["aggregate_report_bytes"], 6_945)
        self.assertEqual(result["private_manifest_bytes"], 175_618)
        self.assertEqual(result["selected_private_rows"], 300)
        self.assertLess(result["runtime_seconds"], 30)
        self.assertLess(result["reported_peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(result["external_maximum_RSS_bytes"], 32_915_456)
        self.assertTrue(result["temporary_outputs_removed"])
        self.assertFalse(result["scientific_value"])

    def test_output_hashes_and_private_mode_are_bound(self) -> None:
        result = self.record["development_qualification"]
        self.assertEqual(
            result["aggregate_report_SHA256"],
            "c9613c308fc4ce3cbb2901297e3c3a6de39ba7ceebb41c58524369ca60bc9c39",
        )
        self.assertEqual(
            result["private_manifest_SHA256"],
            "e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831",
        )
        self.assertEqual(result["private_manifest_mode"], "0600")
        self.assertTrue(result["aggregate_inspect_passed"])
        self.assertFalse(result["generated_artifacts_committed"])

    def test_all_access_and_authorization_flags_remain_zero_or_false(self) -> None:
        self.assertTrue(self.record["implementation_access_counters"])
        self.assertTrue(
            all(value == 0 for value in self.record["implementation_access_counters"].values())
        )
        self.assertTrue(self.record["authorization_flags"])
        self.assertTrue(all(value is False for value in self.record["authorization_flags"].values()))
        tests = self.record["qualification_tests"]
        self.assertEqual(tests["focused_implementation_tests"], 26)
        self.assertEqual(tests["implementation_record_tests"], 11)
        self.assertEqual(tests["final_MARC1_tests"], 263)
        self.assertEqual(tests["dependency_light_tests"], 2_402)
        self.assertEqual(tests["dependency_light_expected_skips"], 204)
        self.assertEqual(tests["optional_neuro_tests"], 2_473)
        self.assertEqual(tests["optional_neuro_expected_skips"], 35)
        self.assertEqual(tests["test_delta"], 37)
        self.assertEqual(tests["additional_skips"], 0)
        self.assertTrue(tests["ruff_passed"])
        self.assertTrue(tests["compile_passed"])
        self.assertTrue(tests["JSON_validation_passed"])
        self.assertTrue(tests["CLI_help_and_roundtrip_passed"])
        self.assertTrue(tests["git_diff_check_passed"])

    def test_closeout_and_real_selection_remain_closed(self) -> None:
        gate = self.record["next_gate"]
        self.assertTrue(gate["exact_implementation_must_be_remotely_green"])
        self.assertFalse(gate["registered_generated_closeout_executed"])
        self.assertFalse(gate["private_Freewill_manifest_read_may_begin"])
        self.assertFalse(gate["Wrist_metadata_request_may_begin"])
        self.assertFalse(gate["payload_acquisition_or_analysis_may_begin"])
        self.assertTrue(gate["later_real_selection_requires_new_Tier_C_packet"])
        self.assertTrue(gate["later_real_selection_requires_fresh_packet_bound_decision"])

    def test_human_record_preserves_same_path_and_claim_boundary(self) -> None:
        document = (
            ROOT
            / "docs"
            / "MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("MARC1-P1 is not a pivot away from thought-to-text", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("one registered generated closeout not executed", document)


if __name__ == "__main__":
    unittest.main()
