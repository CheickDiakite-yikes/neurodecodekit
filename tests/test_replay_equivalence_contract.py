import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "replay_equivalence_contract.v0.json"
AUTHORIZATION_REQUEST_PATH = (
    REPO_ROOT / "registries" / "rw3_stage_a_authorization_request.v0.json"
)


class ReplayEquivalenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.authorization_request = json.loads(
            AUTHORIZATION_REQUEST_PATH.read_text(encoding="utf-8")
        )

    def test_registration_identity_and_authorization_are_preregistration_only(self):
        contract = self.contract
        self.assertEqual(
            contract["schema_name"], "neurodecodekit.replay_equivalence_contract"
        )
        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(
            contract["contract_id"], "rw3-offline-replay-live-source-equivalence-v0"
        )
        self.assertEqual(contract["status"], "preregistered_no_adapter_implementation")
        authorization = contract["authorization"]
        self.assertTrue(authorization["preregistration_only"])
        self.assertTrue(authorization["implementation_requires_separate_review"])
        authorized_actions = [
            key
            for key, value in authorization.items()
            if key.endswith("_authorized") and value is True
        ]
        self.assertEqual(authorized_actions, [])
        self.assertFalse(contract["target_compatibility"]["level_6_live_source_qualified"])

    def test_optional_dependency_and_adapter_stages_are_frozen_without_imports(self):
        dependencies = self.contract["dependencies"]
        self.assertEqual(dependencies["base_dependencies_added"], [])
        self.assertEqual(dependencies["installed_during_preregistration"], [])
        self.assertEqual(
            dependencies["future_exact_versions"],
            {
                "brainflow": "5.22.2",
                "pylsl": "1.18.2",
                "liblsl": "1.17.7",
                "pyxdf": "1.17.5",
            },
        )
        stages = self.contract["adapter_stages"]
        self.assertEqual([row["stage"] for row in stages], ["A", "B", "C", "D"])
        self.assertTrue(all(not row["implementation_authorized_now"] for row in stages))
        self.assertEqual(stages[0]["adapter_id"], "pure_python_synthetic_replay")
        self.assertEqual(stages[1]["forbidden_board_ids"][-1], "every_physical_board")
        self.assertEqual(stages[2]["network_allowed"], "loopback_only_after_separate_approval")
        self.assertFalse(stages[3]["hardware_allowed"])

        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
        for dependency in ("brainflow", "pylsl", "pyxdf"):
            self.assertNotIn(dependency, pyproject)

    def test_source_chunk_schema_preserves_identity_payload_time_and_anomalies(self):
        schema = self.contract["source_chunk_schema"]
        self.assertEqual(schema["schema_name"], "neurodecodekit.source_chunk")
        self.assertEqual(schema["layout"], "channels,samples")
        self.assertEqual(schema["allowed_payload_dtypes"], ["float32", "float64"])
        self.assertEqual(
            schema["record_kinds"],
            [
                "stream_start",
                "data",
                "gap",
                "reconnect",
                "stream_end",
                "source_error",
            ],
        )
        required = set(schema["required_top_level_fields"])
        self.assertTrue(
            {
                "identity",
                "channels",
                "payload",
                "sample_axis",
                "timestamps",
                "packet_accounting",
                "anomalies",
                "causality",
                "provenance",
                "hashes",
            }.issubset(required)
        )
        self.assertIn("padding_mask", schema["payload_required_fields"])
        self.assertIn("source_sample_indices", schema["sample_axis_required_fields"])
        self.assertIn("source_timestamps_sec", schema["timestamp_required_fields"])
        self.assertIn("corrected_timestamps_sec", schema["timestamp_required_fields"])
        self.assertIn("arrival_monotonic_start_ns", schema["timestamp_required_fields"])
        self.assertIn("interpolation_performed", schema["anomaly_required_fields"])
        self.assertFalse(self.contract["architecture_boundary"]["target_or_text_members_allowed"])

    def test_raw_corrected_and_arrival_clocks_cannot_be_collapsed(self):
        clocks = self.contract["clock_contract"]
        self.assertEqual(
            clocks["three_view_rule"],
            [
                "source_timestamp_preserved_bitwise",
                "corrected_timestamp_separate_and_reversible_from_ledger",
                "local_arrival_time_measured_with_monotonic_ns",
            ],
        )
        self.assertEqual(clocks["lsl_primary_processing_flags"], "proc_none")
        self.assertFalse(clocks["lsl_automatic_postprocessing_primary_path"])
        self.assertEqual(
            clocks["xdf_raw_import_arguments"],
            {"synchronize_clocks": False, "dejitter_timestamps": False},
        )
        self.assertTrue(clocks["xdf_derived_import_arguments"]["synchronize_clocks"])
        self.assertTrue(clocks["xdf_derived_import_arguments"]["handle_clock_resets"])
        self.assertTrue(clocks["xdf_derived_import_arguments"]["dejitter_timestamps"])
        self.assertEqual(
            clocks["brainflow_playback_timestamp_mode_primary"], "old_timestamps"
        )

    def test_schedules_fixtures_and_tolerances_are_exact_and_bounded(self):
        schedules = self.contract["registered_schedules"]
        self.assertEqual(
            [row["id"] for row in schedules],
            [
                "single_sample",
                "fixed_20ms",
                "native_packet",
                "deterministic_jitter_5_to_30ms",
                "whole_source",
            ],
        )
        fixtures = self.contract["synthetic_fixture_families"]
        self.assertEqual(len(fixtures), 18)
        self.assertEqual(len(fixtures), len(set(fixtures)))
        self.assertTrue(
            {
                "proven_sample_gap",
                "duplicate_packet",
                "out_of_order_packet",
                "packet_counter_wrap",
                "clock_reset_and_reconnect",
                "ambiguous_stream_identity",
                "resource_cap_violation",
            }.issubset(fixtures)
        )
        tolerances = self.contract["numeric_tolerances"]
        self.assertEqual(tolerances["payload_after_declared_dtype_conversion"], "bitwise_exact")
        self.assertEqual(tolerances["semantic_stream_hash_across_schedules"], "exact")
        self.assertEqual(tolerances["local_lsl_time_correction_uncertainty_max_sec"], 0.005)
        self.assertIsNone(tolerances["generic_wireless_transport_latency_pass_threshold"])
        self.assertIsNone(tolerances["end_to_end_text_latency_threshold"])

    def test_resources_access_refusals_and_decisions_fail_closed(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["worker_processes"], 1)
        self.assertEqual(
            caps["max_total_channel_sample_values"] * 8,
            caps["max_materialized_payload_bytes"],
        )
        self.assertLessEqual(
            caps["max_complete_fixture_and_report_bytes"],
            caps["hard_generated_artifact_cap_bytes"],
        )
        self.assertEqual(caps["hard_generated_artifact_cap_bytes"], 32 * 1024 * 1024)
        for name in (
            "max_external_network_calls",
            "max_real_data_reads",
            "max_consumed_cache_reads",
            "max_target_label_reads",
            "max_model_runs",
            "max_training_runs",
        ):
            self.assertEqual(caps[name], 0)

        counters = set(self.contract["access_counters"])
        self.assertTrue(
            {
                "brainflow_destructive_get_board_data_calls",
                "brainflow_nondestructive_get_current_board_data_calls",
                "lsl_resolve_calls",
                "lsl_time_correction_calls",
                "loopback_socket_calls",
                "external_network_calls",
                "real_data_reads",
                "target_label_reads",
                "model_runs",
                "training_runs",
                "decoder_runs",
            }.issubset(counters)
        )
        refusals = self.contract["refusal_ids"]
        self.assertEqual(len(refusals), 30)
        self.assertEqual(len(refusals), len(set(refusals)))
        self.assertIn("external_network_not_authorized", refusals)
        self.assertIn("live_hardware_not_authorized", refusals)
        self.assertIn("source_timestamp_overwritten_or_destroyed", refusals)
        self.assertEqual(
            self.contract["decision_rules"]["after_registration"],
            "request_separate_authorization_for_stage_A_only",
        )

    def test_privacy_hashes_claims_and_primary_sources_are_explicit(self):
        privacy = self.contract["privacy"]
        self.assertTrue(privacy["local_only"])
        self.assertIn("waveform_values", privacy["report_forbidden_fields"])
        self.assertIn("target_text", privacy["report_forbidden_fields"])
        self.assertIn("hostname_or_ip_address", privacy["report_forbidden_fields"])
        hashes = self.contract["semantic_hash_contract"]
        self.assertTrue(hashes["chunk_hash_boundary_sensitive"])
        self.assertTrue(hashes["semantic_stream_hash_boundary_invariant"])
        self.assertIn("wall_clock_values", hashes["excludes"])
        self.assertIn("source_timestamp_bits", hashes["includes"])
        self.assertTrue(self.contract["claim_boundary"])
        self.assertIn("no runtime result", self.contract["claim_boundary"][0])

        sources = self.contract["primary_sources"]
        self.assertGreaterEqual(len(sources), 12)
        self.assertEqual(len({row["id"] for row in sources}), len(sources))
        self.assertEqual(len({row["url"] for row in sources}), len(sources))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))

    def test_stage_a_request_is_bound_but_not_authorized(self):
        request = self.authorization_request
        self.assertEqual(
            request["schema_name"], "neurodecodekit.stage_authorization_request"
        )
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["status"], "awaiting_explicit_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        self.assertIsNone(request["authorization_record_commit"])
        self.assertFalse(request["decision"]["silence_or_general_continuation_is_authorization"])
        self.assertFalse(request["decision"]["authorization_is_transitive_to_later_stages"])

        contract_sha256 = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
        self.assertEqual(request["target"]["contract_sha256"], contract_sha256)
        self.assertEqual(request["target"]["contract_id"], self.contract["contract_id"])
        self.assertEqual(request["target"]["stage"], "A")
        self.assertEqual(request["target"]["adapter_id"], "pure_python_synthetic_replay")
        self.assertEqual(request["target"]["registration_commit"], "c3d1f01")

    def test_stage_a_request_matches_frozen_cases_refusals_and_caps(self):
        request = self.authorization_request
        matrix = request["case_matrix"]
        self.assertEqual(matrix["registered_schedule_count"], 5)
        self.assertEqual(matrix["registered_fixture_family_count"], 18)
        self.assertEqual(matrix["schedule_by_fixture_case_count"], 90)
        self.assertEqual(
            matrix["schedule_by_fixture_case_count"],
            len(self.contract["registered_schedules"])
            * len(self.contract["synthetic_fixture_families"]),
        )
        self.assertEqual(
            request["registered_refusal_ids"], self.contract["refusal_ids"]
        )
        self.assertEqual(request["resource_caps"], self.contract["resource_caps"])
        self.assertEqual(
            request["acceptance"]["registered_refusal_ids"],
            "30_of_30_reachable_by_deterministic_negative_tests",
        )

    def test_stage_a_request_keeps_optional_data_model_and_later_stages_forbidden(self):
        request = self.authorization_request
        self.assertEqual(request["stage_a_scope"]["base_dependencies_added"], [])
        self.assertEqual(
            request["stage_a_scope"]["optional_dependencies_installed_or_imported"], []
        )
        self.assertEqual(len(request["stage_a_scope"]["cli_surface"]), 4)
        forbidden = request["forbidden_even_if_stage_a_is_authorized"]
        self.assertTrue(forbidden)
        self.assertTrue(all(forbidden.values()))
        self.assertTrue(forbidden["stage_B_C_or_D_implementation"])
        self.assertTrue(forbidden["real_recording_or_cache_access"])
        self.assertTrue(forbidden["target_label_prediction_or_text_access"])
        self.assertTrue(forbidden["model_decoder_or_training_run"])

        contract_authorization = self.contract["authorization"]
        self.assertTrue(contract_authorization["preregistration_only"])
        self.assertFalse(contract_authorization["source_chunk_implementation_authorized"])
        self.assertFalse(contract_authorization["synthetic_fixture_generation_authorized"])
        self.assertTrue(
            all(
                not stage["implementation_authorized_now"]
                for stage in self.contract["adapter_stages"]
            )
        )


if __name__ == "__main__":
    unittest.main()
