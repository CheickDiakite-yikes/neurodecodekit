import hashlib
import itertools
import json
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "local_precision_runtime_contract.v0.json"
RW3_CONTRACT_PATH = REPO_ROOT / "registries" / "replay_equivalence_contract.v0.json"
RW3_REQUEST_PATH = REPO_ROOT / "registries" / "rw3_stage_a_authorization_request.v0.json"


class LocalPrecisionRuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.rw3_contract = json.loads(RW3_CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.rw3_request = json.loads(RW3_REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_and_every_execution_authorization_are_frozen_false(self):
        contract = self.contract
        self.assertEqual(
            contract["schema_name"], "neurodecodekit.local_precision_runtime_contract"
        )
        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["contract_id"], "loop24-local-precision-runtime-v0")
        self.assertEqual(
            contract["status"], "preregistered_no_candidate_implementation_or_execution"
        )
        self.assertEqual(contract["preregistration_parent_commit"], "8190f86")
        authorization = contract["authorization"]
        self.assertTrue(authorization["preregistration_only"])
        self.assertTrue(authorization["implementation_requires_separate_user_authorization"])
        self.assertFalse(authorization["general_continuation_is_authorization"])
        self.assertTrue(
            all(
                value is False
                for key, value in authorization.items()
                if key.endswith("_authorized_now")
            )
        )
        self.assertIn("Do not authorize RW3 Stage A", authorization["authorization_sentence_exact"])
        contract_sha256 = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
        preregistration = (
            REPO_ROOT / "docs" / "LOOP_24_PRECISION_RUNTIME_PREREGISTRATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn(contract_sha256, preregistration)

    def test_reference_model_scalar_and_decoder_identities_are_exact(self):
        reference = self.contract["reference_pipeline"]
        self.assertEqual(reference["producer_name"], "TinyCausalWindowEncoder")
        self.assertEqual(reference["trainable_parameters"], 1130)
        self.assertEqual(reference["encoder_parameters"], 1076)
        self.assertEqual(reference["probe_parameters"], 54)
        self.assertEqual(reference["float32_parameter_bytes"], 4520)
        self.assertEqual(reference["float32_parameter_plus_normalization_bytes"], 4560)
        self.assertEqual(
            reference["checkpoint_file_sha256"],
            "75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1",
        )
        self.assertEqual(
            reference["parameter_payload_sha256"],
            "d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98",
        )
        self.assertEqual(reference["blank_intercept_value"], 5.130175197684084)
        self.assertEqual(reference["blank_intercept_dtype"], "float64")
        self.assertEqual(reference["decoder"]["beam_width"], 8)
        self.assertEqual(reference["decoder"]["log_softmax_dtype"], "float64")
        self.assertIsNone(reference["decoder"]["language_model"])
        self.assertFalse(reference["architecture_changes_allowed"])
        self.assertFalse(reference["retraining_allowed"])
        self.assertFalse(reference["recalibration_allowed"])

    def test_source_bindings_match_the_unchanged_parent_files(self):
        bindings = self.contract["source_bindings"]
        self.assertEqual(len(bindings), 5)
        self.assertEqual(len({row["path"] for row in bindings}), len(bindings))
        self.assertEqual(
            len({row["git_blob_sha1_at_parent"] for row in bindings}), len(bindings)
        )
        for row in bindings:
            path = REPO_ROOT / row["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["file_sha256_at_parent"])
            self.assertRegex(row["git_blob_sha1_at_parent"], r"^[0-9a-f]{40}$")

    def test_candidate_set_is_exact_explicit_and_has_no_fallback(self):
        candidates = self.contract["candidate_set"]
        self.assertEqual(
            [row["candidate_id"] for row in candidates],
            [
                "float32_eager_reference",
                "float16_eager_cpu",
                "dynamic_qint8_qnnpack",
            ],
        )
        self.assertFalse(candidates[0]["selectable_as_replacement"])
        self.assertTrue(candidates[1]["selectable_as_replacement"])
        self.assertTrue(candidates[2]["selectable_as_replacement"])
        self.assertTrue(all(not row["fallback_allowed"] for row in candidates))
        self.assertFalse(candidates[1]["autocast_allowed"])
        self.assertEqual(candidates[1]["linear_weight_dtype"], "float16")
        self.assertEqual(candidates[1]["hardware_accumulation_dtype_if_not_proven"], "unavailable")
        self.assertEqual(candidates[2]["quantized_engine"], "qnnpack")
        self.assertEqual(candidates[2]["packed_weight_dtype"], "qint8")
        self.assertEqual(
            candidates[2]["required_profiler_operator_contains"], "quantized::linear_dynamic"
        )
        self.assertFalse(candidates[2]["torchao_substitution_allowed"])
        self.assertIn("torchao", self.contract["excluded_candidates"])
        self.assertIn("torch_compile", self.contract["excluded_candidates"])

    def test_fixture_is_target_free_fresh_and_physically_split(self):
        fixture = self.contract["fixture_contract"]
        self.assertTrue(fixture["target_free"])
        self.assertEqual(
            fixture["members"], ["signals", "input_lengths", "item_ids", "metadata"]
        )
        forbidden = set(fixture["forbidden_members"])
        self.assertTrue(
            {"targets", "target_token_ids", "labels", "text", "predictions"}.issubset(
                forbidden
            )
        )
        self.assertEqual(fixture["selection"]["seed"], 2401)
        self.assertEqual(fixture["qualification"]["seed"], 2402)
        self.assertEqual(fixture["selection"]["items"], 48)
        self.assertEqual(fixture["qualification"]["items"], 48)
        self.assertEqual(len(fixture["waveform_families"]), 6)
        self.assertEqual(fixture["items_per_waveform_family_per_partition"], 8)
        self.assertFalse(fixture["generated_from_model_outputs"])
        self.assertTrue(fixture["physical_partition_files_required"])
        self.assertTrue(fixture["partition_item_ids_must_be_disjoint"])
        self.assertFalse(fixture["manifest_inspection_opens_array_members"])

    def test_correctness_and_access_sequence_protect_incremental_behavior(self):
        correctness = self.contract["correctness_gates"]
        exact = set(correctness["exact_for_every_candidate"])
        self.assertTrue(
            {
                "frame_start_samples",
                "frame_end_samples",
                "token_timestamps",
                "greedy_path_class_by_frame",
                "greedy_partial_hypothesis_by_frame",
                "prefix_top_hypothesis_by_frame",
                "prefix_final_hypothesis_by_item",
                "right_context_zero",
            }.issubset(exact)
        )
        self.assertEqual(correctness["reference_replay_repeats"], 3)
        self.assertTrue(correctness["tolerances_may_not_change_after_selection_open"])
        self.assertTrue(correctness["behavioral_exactness_is_primary_over_numeric_tolerance"])
        tolerances = correctness["numeric_tolerances"]
        self.assertEqual(tolerances["embedding_max_absolute_error"], 0.1)
        self.assertEqual(tolerances["logit_max_absolute_error"], 0.1)
        self.assertEqual(tolerances["blank_margin_max_absolute_error"], 0.15)
        self.assertEqual(tolerances["cosine_zero_norm_floor"], 1e-12)
        self.assertEqual(tolerances["cosine_one_zero_rule"], "zero")
        sequence = self.contract["partition_access_sequence"]
        self.assertEqual(len(sequence), 12)
        self.assertLess(
            sequence.index("freeze_selection_report_and_candidate_decision"),
            sequence.index(
                "open_qualification_input_only_partition_once_only_if_a_nonreference_replacement_candidate_was_selected"
            ),
        )

    def test_benchmark_orders_threads_and_energy_boundary_are_exact(self):
        benchmark = self.contract["benchmark_protocol"]
        candidate_ids = [row["candidate_id"] for row in self.contract["candidate_set"]]
        expected_permutations = set(itertools.permutations(candidate_ids))
        orders = [tuple(row) for row in benchmark["selection_candidate_orders"]]
        self.assertEqual(benchmark["selection_rounds"], 12)
        self.assertEqual(set(orders), expected_permutations)
        self.assertTrue(all(count == 2 for count in Counter(orders).values()))
        for position in range(3):
            self.assertEqual(
                Counter(order[position] for order in orders),
                Counter({candidate_id: 4 for candidate_id in candidate_ids}),
            )
        self.assertEqual(
            benchmark["steady_state_timer"],
            "torch.utils.benchmark.Timer.adaptive_autorange",
        )
        self.assertEqual(benchmark["timer_num_threads"], 1)
        self.assertEqual(benchmark["timer_max_run_time_sec"], 0.25)
        self.assertEqual(benchmark["torch_intraop_threads"], 1)
        self.assertEqual(benchmark["torch_interop_threads"], 1)
        self.assertEqual(benchmark["maximum_concurrent_workers"], 1)
        self.assertTrue(benchmark["torch_inference_mode_required"])
        self.assertFalse(benchmark["mps_cuda_xpu_allowed"])
        energy = self.contract["energy_proxy"]
        self.assertFalse(energy["required_for_gate"])
        self.assertFalse(energy["sudo_prompt_allowed"])
        self.assertTrue(energy["within_device_comparison_only"])
        self.assertFalse(energy["cross_device_comparison_allowed"])

    def test_selection_resources_refusals_and_sources_fail_closed(self):
        rules = self.contract["selection_rules"]
        replacement = rules["default_replacement_requires_all"]
        self.assertEqual(rules["default_before_gate"], "float32_eager_reference")
        self.assertEqual(replacement["model_path_median_latency_ratio_max"], 0.8)
        self.assertEqual(replacement["full_pipeline_median_latency_ratio_max"], 0.9)
        self.assertEqual(replacement["full_pipeline_p95_latency_ratio_max"], 0.95)
        self.assertFalse(rules["storage_only_candidate_replaces_default"])
        self.assertEqual(rules["qualification_failure_decision"], "retain_float32_and_reject_selected_candidate")
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["maximum_concurrent_workers"], 1)
        self.assertEqual(caps["maximum_generated_bytes_total"], 4 * 1024 * 1024)
        self.assertEqual(caps["maximum_internal_runtime_sec"], 60)
        for name in (
            "maximum_external_network_calls",
            "maximum_real_data_reads",
            "maximum_consumed_evidence_reads",
            "maximum_target_label_text_reads",
            "maximum_training_runs",
            "maximum_parameter_updates",
            "maximum_rw3_operations",
        ):
            self.assertEqual(caps[name], 0)
        refusals = self.contract["refusal_ids"]
        self.assertEqual(len(refusals), 30)
        self.assertEqual(len(refusals), len(set(refusals)))
        self.assertIn("candidate_silent_float32_or_backend_fallback", refusals)
        self.assertIn("consumed_seed_or_real_evidence_accessed", refusals)
        sources = self.contract["primary_sources"]
        self.assertGreaterEqual(len(sources), 15)
        self.assertEqual(len({row["id"] for row in sources}), len(sources))
        self.assertEqual(len({row["url"] for row in sources}), len(sources))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))

    def test_no_loop24_runtime_exists_and_rw3_remains_unauthorized(self):
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
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
        self.assertNotIn("torchao", pyproject)
        self.assertFalse(self.rw3_request["authorized_now"])
        self.assertTrue(self.rw3_contract["authorization"]["preregistration_only"])
        self.assertFalse(
            self.rw3_contract["authorization"]["source_chunk_implementation_authorized"]
        )
        self.assertTrue(
            all(
                not row["implementation_authorized_now"]
                for row in self.rw3_contract["adapter_stages"]
            )
        )


if __name__ == "__main__":
    unittest.main()
