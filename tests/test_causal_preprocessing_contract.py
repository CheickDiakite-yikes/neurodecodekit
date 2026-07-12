import hashlib
import json
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v0.json"
PREREGISTRATION_PATH = (
    REPO_ROOT / "docs" / "LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md"
)
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_25_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
LOOP24_AUTHORIZATION_PATH = (
    REPO_ROOT / "registries" / "loop24_authorization_decision.v0.json"
)
RW3_REQUEST_PATH = (
    REPO_ROOT / "registries" / "rw3_stage_a_authorization_request.v0.json"
)


class CausalPreprocessingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.preregistration = PREREGISTRATION_PATH.read_text(encoding="utf-8")
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.loop24_authorization = json.loads(
            LOOP24_AUTHORIZATION_PATH.read_text(encoding="utf-8")
        )
        cls.rw3_request = json.loads(RW3_REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_hash_and_every_execution_authorization_are_frozen(self):
        contract = self.contract
        self.assertEqual(
            contract["schema_name"],
            "neurodecodekit.causal_preprocessing_contract",
        )
        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["contract_id"], "loop25-causal-preprocessing-v0")
        self.assertEqual(
            contract["status"], "preregistered_no_implementation_or_execution"
        )
        self.assertEqual(contract["preregistration_parent_commit"], "3ae7d97")
        authorization = contract["authorization"]
        self.assertTrue(authorization["preregistration_only"])
        self.assertTrue(
            authorization["implementation_requires_separate_user_authorization"]
        )
        self.assertFalse(authorization["general_continuation_is_authorization"])
        self.assertFalse(authorization["roadmap_approval_is_authorization"])
        self.assertFalse(authorization["loop24_authorization_carries_forward"])
        self.assertTrue(
            all(
                value is False
                for key, value in authorization.items()
                if key.endswith("_authorized_now")
            )
        )
        self.assertIn(
            "Do not authorize real or consumed data",
            authorization["authorization_sentence_exact"],
        )
        contract_sha256 = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
        self.assertIn(contract_sha256, self.preregistration)

    def test_official_and_local_offline_audits_keep_async_separate_from_causal(self):
        upstream = self.contract["official_upstream_audit"]
        self.assertEqual(
            upstream["commit"], "3bf5a4099ca0d23bbe994b2287905760236e56e0"
        )
        self.assertTrue(upstream["paper_preprocessing_declared_offline"])
        self.assertEqual(upstream["paper_bandpass_hz"], [0.5, 45.0])
        self.assertEqual(upstream["paper_notch_hz"], 50.0)
        self.assertEqual(upstream["paper_output_sampling_rate_hz"], 100.0)
        self.assertTrue(upstream["asynchronous_is_not_treated_as_causal_proof"])
        self.assertFalse(upstream["public_model_file_exposes_streaming_state"])
        self.assertFalse(upstream["public_model_file_exposes_causal_attention_mask"])
        self.assertEqual(len(upstream["source_files"]), 4)
        self.assertTrue(
            all(len(row["git_blob_sha1"]) == 40 for row in upstream["source_files"])
        )

        local = self.contract["local_offline_pipeline_audit"]
        self.assertFalse(local["sentence_notch"]["causal"])
        self.assertFalse(local["sentence_bandpass"]["causal"])
        self.assertEqual(local["sentence_resample"]["method"], "fft")
        self.assertTrue(local["recording_robust_scaler_fit"]["future_dependent"])
        self.assertFalse(
            local["train_robust_scaler_application"]["fit_allowed_in_loop25_runtime"]
        )
        self.assertFalse(local["sentence_zero_padding"]["allowed_in_loop25_stream"])
        self.assertTrue(local["legacy_files_must_not_be_mutated_by_loop25"])

    def test_parent_source_bindings_match_without_mutating_legacy_paths(self):
        bindings = self.contract["source_bindings"]
        self.assertEqual(len(bindings), 5)
        self.assertEqual(len({row["path"] for row in bindings}), 5)
        for row in bindings:
            with self.subTest(path=row["path"]):
                path = REPO_ROOT / row["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    row["file_sha256_at_parent"],
                )
                self.assertRegex(row["git_blob_sha1_at_parent"], r"^[0-9a-f]{40}$")

    def test_pipeline_filter_decimation_normalization_and_timing_are_exact(self):
        pipeline = self.contract["planned_pipeline"]
        self.assertEqual(pipeline["input_layout"], "channels,time")
        self.assertEqual(pipeline["input_dtype"], "float32")
        self.assertEqual(pipeline["channels"], 5)
        self.assertEqual(pipeline["source_sampling_rate_hz"], 1000.0)
        self.assertEqual(pipeline["output_sampling_rate_hz"], 100.0)
        self.assertEqual(pipeline["integer_decimation_factor"], 10)
        self.assertEqual(pipeline["notch"]["quality_factor"], 30.0)
        self.assertEqual(pipeline["bandpass"]["order"], 4)
        self.assertEqual(
            pipeline["bandpass"]["critical_frequencies_hz"], [0.5, 45.0]
        )
        application = pipeline["filter_application"]
        self.assertEqual(application["api"], "scipy.signal.sosfilt")
        self.assertEqual(application["computation_dtype"], "float64")
        self.assertFalse(application["zero_phase_or_backward_pass_allowed"])
        self.assertFalse(application["future_samples_allowed"])
        self.assertFalse(application["silent_state_reset_allowed"])
        decimation = pipeline["decimation"]
        self.assertEqual(decimation["kept_global_source_indices"], "0,10,20,...")
        self.assertFalse(decimation["general_rational_resampling_allowed"])
        self.assertFalse(decimation["padding_allowed"])
        normalization = pipeline["normalization"]
        self.assertFalse(normalization["fit_during_loop25_allowed"])
        self.assertEqual(normalization["center_float64"], [-0.25, -0.125, 0, 0.125, 0.25])
        self.assertEqual(normalization["scale_float64"], [0.75, 0.875, 1, 1.125, 1.25])
        self.assertEqual(normalization["clamp_inclusive"], [-5, 5])
        self.assertEqual(pipeline["output"]["right_context_samples"], 0)
        self.assertFalse(pipeline["output"]["end_to_end_latency_measured"])
        self.assertFalse(pipeline["official_offline_path_is_reference_for_numeric_identity"])

    def test_fixture_is_fresh_target_free_bounded_and_physically_split(self):
        fixture = self.contract["fixture_contract"]
        self.assertTrue(fixture["target_free"])
        self.assertEqual(
            fixture["members"],
            [
                "signals",
                "input_lengths",
                "item_ids",
                "source_start_samples",
                "metadata",
            ],
        )
        forbidden = set(fixture["forbidden_members"])
        self.assertTrue(
            {
                "targets",
                "labels",
                "text",
                "predictions",
                "participant_id",
                "model_output",
                "checkpoint",
            }.issubset(forbidden)
        )
        self.assertEqual(fixture["development"]["seed"], 2501)
        self.assertEqual(fixture["qualification"]["seed"], 2502)
        self.assertEqual(fixture["development"]["items"], 12)
        self.assertEqual(fixture["qualification"]["items"], 12)
        self.assertEqual(len(fixture["item_lengths_exact"]), 12)
        self.assertEqual(len(fixture["signal_families"]), 6)
        self.assertEqual(fixture["items_per_family_per_partition"], 2)
        self.assertFalse(fixture["generated_from_model_outputs"])
        self.assertFalse(
            fixture["generated_from_targets_labels_text_or_predictions"]
        )
        self.assertTrue(fixture["physical_partition_files_required"])
        self.assertTrue(fixture["partition_item_ids_must_be_disjoint"])
        self.assertFalse(fixture["manifest_inspection_opens_signal_arrays"])

    def test_seven_schedules_ten_resumes_and_future_mutations_are_frozen(self):
        schedules = self.contract["registered_chunk_schedules"]
        self.assertEqual(
            [row["schedule_id"] for row in schedules],
            [
                "whole_item",
                "single_sample",
                "fixed_seven",
                "decimation_boundaries",
                "frame_boundaries",
                "powers_of_two",
                "seeded_irregular",
            ],
        )
        self.assertEqual(len({row["rule"] for row in schedules}), 7)
        self.assertEqual(
            self.contract["registered_resume_cut_source_samples"],
            [1, 9, 10, 15, 16, 159, 160, 161, 511, 997],
        )
        self.assertEqual(
            self.contract["registered_future_mutation_cut_source_samples"],
            [160, 512, 1000],
        )
        state = self.contract["state_contract"]
        self.assertTrue(state["deterministic_semantic_hash_required"])
        self.assertTrue(state["resume_must_match_uninterrupted"])
        self.assertFalse(state["silent_reset_allowed"])
        self.assertEqual(state["mutable_state_max_bytes"], 4096)
        sequence = self.contract["partition_access_sequence"]
        self.assertEqual(len(sequence), 12)
        self.assertLess(
            sequence.index("freeze_and_hash_development_report_before_qualification"),
            sequence.index(
                "open_qualification_target_free_partition_once_only_if_every_development_gate_passed"
            ),
        )

    def test_acceptance_gates_are_conjunctive_and_do_not_hide_filter_delay(self):
        gates = self.contract["acceptance_gates"]
        self.assertEqual(gates["causality"]["declared_right_context_source_samples"], 0)
        self.assertTrue(
            gates["causality"]["future_mutation_earlier_output_bitwise_identity_required"]
        )
        self.assertTrue(
            gates["schedule_equivalence"]["same_host_output_float32_bitwise_identity"]
        )
        self.assertEqual(
            gates["schedule_equivalence"]["cross_environment_output_absolute_tolerance"],
            1e-6,
        )
        frequency = gates["frequency_response"]
        self.assertEqual(frequency["dc_gain_db_max"], -20.0)
        self.assertEqual(frequency["passband_probe_frequencies_hz"], [5, 10, 20, 35])
        self.assertEqual(frequency["notch_probe_hz"], 50.0)
        self.assertEqual(frequency["notch_gain_db_max"], -20.0)
        self.assertTrue(frequency["frequency_dependent_phase_delay_report_required"])
        self.assertTrue(frequency["frequency_delay_is_not_end_to_end_latency"])
        self.assertEqual(
            gates["timing"]["expected_output_count_formula"],
            "floor((input_length-1)/10)+1",
        )
        self.assertEqual(gates["timing"]["timestamp_absolute_tolerance_sec"], 1e-12)
        self.assertEqual(gates["normalization"]["statistics_fit_counter_required_zero"], True)
        self.assertEqual(gates["normalization"]["padding_values_emitted"], 0)
        self.assertEqual(gates["flush"]["invented_source_samples"], 0)
        self.assertEqual(gates["flush"]["invented_output_samples"], 0)
        self.assertFalse(gates["decision"]["post_result_tuning_or_rerun_allowed"])

    def test_resources_access_counters_refusals_and_sources_fail_closed(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["maximum_concurrent_workers"], 1)
        self.assertEqual(caps["maximum_fixture_bytes_total"], 4 * 1024 * 1024)
        self.assertEqual(caps["maximum_generated_bytes_total"], 8 * 1024 * 1024)
        self.assertEqual(caps["maximum_internal_runtime_sec"], 45)
        self.assertEqual(caps["maximum_mutable_state_bytes"], 4096)
        for name in (
            "maximum_external_network_calls",
            "maximum_real_data_reads",
            "maximum_real_cache_reads",
            "maximum_consumed_evidence_reads",
            "maximum_target_label_text_prediction_reads",
            "maximum_checkpoint_reads",
            "maximum_model_runs",
            "maximum_training_runs",
            "maximum_parameter_updates",
            "maximum_rw3_operations",
            "maximum_stream_socket_board_device_hardware_operations",
        ):
            self.assertEqual(caps[name], 0)
        counters = self.contract["required_access_counters"]
        self.assertEqual(len(counters), 21)
        self.assertEqual(len(counters), len(set(counters)))
        refusals = self.contract["refusal_ids"]
        self.assertEqual(len(refusals), 40)
        self.assertEqual(len(refusals), len(set(refusals)))
        self.assertIn("zero_phase_backward_or_centered_filter_requested", refusals)
        self.assertIn("future_mutation_changed_earlier_output_or_state", refusals)
        self.assertIn("real_consumed_target_model_training_network_rw3_or_hardware_access", refusals)
        sources = self.contract["primary_sources"]
        self.assertEqual(len(sources), 12)
        self.assertEqual(len({row["id"] for row in sources}), 12)
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))

    def test_no_runtime_fixture_cli_or_dependency_exists_before_authorization(self):
        planned = self.contract["planned_implementation"]
        self.assertFalse(planned["files_exist_now"])
        self.assertFalse(planned["cli_exists_now"])
        self.assertEqual(planned["base_dependencies_added"], [])
        self.assertEqual(planned["optional_dependencies_added"], [])
        for relative in planned["files"]:
            self.assertFalse((REPO_ROOT / relative).exists(), relative)
        cli_text = (REPO_ROOT / "src" / "neurodecodekit" / "cli.py").read_text(
            encoding="utf-8"
        )
        for command in planned["cli_commands"]:
            self.assertNotIn(command, cli_text)
        project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(project["project"]["dependencies"], [])
        self.assertIn("scipy>=1.11", project["project"]["optional-dependencies"]["neuro"])

    def test_human_docs_roadmap_and_independent_boundaries_agree(self):
        loop25 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 25)
        self.assertEqual(loop25["title"], "Causal Preprocessing Audit")
        self.assertFalse(loop25["execution_authorized"])
        boundary = loop25["authorization_boundary"].lower()
        self.assertIn("separate", boundary)
        self.assertIn("authorization", boundary)
        for phrase in (
            "seven schedules",
            "ten resume",
            "40 refusal",
            "seed 2501",
            "seed 2502",
            "no implementation or execution authorized",
        ):
            self.assertIn(phrase.lower(), self.preregistration.lower())
        self.assertIn("preprocessed offline", self.research)
        self.assertIn("zero-phase", self.research)
        self.assertIn("not a causal preprocessing path", self.research)
        loop24_flags = self.loop24_authorization["authorization"]
        self.assertTrue(loop24_flags["loop24_implementation_authorized_now"])
        self.assertFalse(loop24_flags["real_data_access_authorized_now"])
        self.assertFalse(loop24_flags["consumed_evidence_access_authorized_now"])
        self.assertFalse(loop24_flags["training_or_parameter_updates_authorized_now"])
        self.assertFalse(loop24_flags["loop25_through_44_execution_authorized_now"])
        self.assertFalse(self.rw3_request["authorized_now"])
        claims = " ".join(self.contract["claim_boundaries"]["must_not_claim"])
        self.assertIn("official Brain2Qwerty v2", claims)
        self.assertIn("end-to-end", claims)
        self.assertIn("portable-device", claims)


if __name__ == "__main__":
    unittest.main()
