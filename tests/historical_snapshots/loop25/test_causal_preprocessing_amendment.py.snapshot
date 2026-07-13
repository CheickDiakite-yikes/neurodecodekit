import hashlib
import json
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
V0_CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v0.json"
V0_REQUEST_PATH = REPO_ROOT / "registries" / "loop25_authorization_request.v0.json"
V0_PREREGISTRATION_PATH = (
    REPO_ROOT / "docs" / "LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md"
)
V0_RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_25_PRIMARY_SOURCE_RESEARCH.md"
V0_TEST_PATH = REPO_ROOT / "tests" / "test_causal_preprocessing_contract.py"
CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v1.json"
AMENDMENT_PATH = (
    REPO_ROOT / "docs" / "LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md"
)
AUDIT_PATH = REPO_ROOT / "docs" / "LOOP_25_ANTI_ALIAS_AUDIT.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class CausalPreprocessingAmendmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.amendment = AMENDMENT_PATH.read_text(encoding="utf-8")
        cls.audit = AUDIT_PATH.read_text(encoding="utf-8")

    def test_v0_registration_and_request_remain_byte_identical(self):
        expected = {
            V0_CONTRACT_PATH: "42781526225c556d0df54d1b6924fd5d9ecf95578a84c3e3922b6d5c7035050e",
            V0_REQUEST_PATH: "3d103a0a18bd1d9ea8b320cde9515f891e41646c51132ad9c7adea35838f04b4",
            V0_PREREGISTRATION_PATH: "c681be25a633705f14ae5e2850908c4d911762d380ee2342fb7f2a587a3ebe7c",
            V0_RESEARCH_PATH: "6e2b6c1ff584fc186926e6c631b2e1397117f13564de13fd276d64497b874ed4",
            V0_TEST_PATH: "e0e37d54f0d83103cddab5b7782b30722a52cb21ba8c9ae823421132684c2916",
        }
        for path, digest in expected.items():
            with self.subTest(path=path.name):
                self.assertEqual(sha256(path), digest)

    def test_v1_identity_hash_supersession_and_authorization_are_frozen(self):
        contract = self.contract
        self.assertEqual(contract["schema_version"], "0.2.0")
        self.assertEqual(contract["contract_id"], "loop25-causal-preprocessing-v1")
        self.assertEqual(
            contract["status"],
            "superseding_amendment_no_implementation_or_execution",
        )
        self.assertEqual(
            contract["amendment_parent_commit"],
            "2e7607b7b56298a9f21899c4465232c5313d2ed3",
        )
        self.assertIn(sha256(CONTRACT_PATH), self.amendment)
        flags = authorization_flags(contract)
        self.assertEqual(len(flags), 14)
        self.assertTrue(all(value is False for _, value in flags), flags)
        supersession = contract["supersession"]
        self.assertFalse(supersession["superseded_request_was_authorized"])
        self.assertFalse(supersession["superseded_development_seed_was_opened"])
        self.assertFalse(supersession["superseded_qualification_seed_was_opened"])
        self.assertTrue(
            supersession["superseded_authorization_sentence_is_no_longer_actionable"]
        )

    def test_pinned_upstream_proves_resampling_is_separate_from_bandpass(self):
        upstream = self.contract["official_upstream_audit"]
        dependencies = upstream["dependency_manifest"]
        self.assertEqual(dependencies["neuralset_version"], "0.2.2")
        self.assertEqual(dependencies["mne_version"], "1.11.0")
        self.assertEqual(dependencies["scipy_version"], "1.14.1")
        neuralset = upstream["pinned_neuralset_extractor"]
        self.assertEqual(
            neuralset["commit"], "02bd64b93d5b1cfc785e6fd576b40fad27556765"
        )
        self.assertEqual(
            neuralset["preprocessing_order"],
            ["notch_filter", "bandpass_filter", "resample", "scaler"],
        )
        self.assertTrue(neuralset["resample_is_separate_from_bandpass"])
        mne = upstream["pinned_mne_resampler"]
        self.assertEqual(mne["default_method"], "fft")
        self.assertTrue(mne["default_applies_anti_aliasing"])
        self.assertTrue(mne["default_operates_on_complete_signal"])
        self.assertFalse(mne["default_is_allowed_in_causal_runtime"])
        self.assertIn("separate `raw.resample(...)`", self.audit)

    def test_dedicated_antialias_design_and_stage_order_are_exact(self):
        pipeline = self.contract["planned_pipeline"]
        self.assertEqual(
            pipeline["pipeline_id"],
            "causal_sos_filter_dedicated_elliptic_antialias_phase_locked_decimate_frozen_scale_v1",
        )
        stages = pipeline["stage_order"]
        self.assertLess(
            stages.index("stateful_0_5_to_45_hz_bandpass_sos"),
            stages.index("stateful_dedicated_45_to_50_hz_elliptic_antialias_sos"),
        )
        self.assertLess(
            stages.index("stateful_dedicated_45_to_50_hz_elliptic_antialias_sos"),
            stages.index("phase_locked_keep_global_source_indices_divisible_by_10"),
        )
        design = pipeline["dedicated_antialias"]
        self.assertEqual(design["design_api"], "scipy.signal.iirdesign")
        self.assertEqual(design["passband_edge_hz"], 45.0)
        self.assertEqual(design["stopband_edge_hz"], 50.0)
        self.assertEqual(design["maximum_passband_loss_db"], 1.0)
        self.assertEqual(design["minimum_stopband_attenuation_db"], 60.0)
        self.assertEqual(design["filter_type"], "ellip")
        self.assertEqual(design["output"], "sos")
        self.assertTrue(design["coefficient_generation_occurs_before_fixture_array_open"])

    def test_dense_folding_band_and_alias_map_replace_one_weak_probe(self):
        frequency = self.contract["acceptance_gates"]["frequency_response"]
        self.assertEqual(frequency["dense_grid_start_hz"], 0.0)
        self.assertEqual(frequency["dense_grid_stop_hz"], 500.0)
        self.assertEqual(frequency["dense_grid_points_inclusive"], 65537)
        self.assertEqual(frequency["dedicated_antialias_stopband_hz"], [50.0, 500.0])
        self.assertEqual(
            frequency["dedicated_antialias_dense_stopband_gain_db_max"], -59.5
        )
        self.assertEqual(
            frequency["combined_chain_dense_folding_band_gain_db_max"], -59.5
        )
        probes = frequency["registered_alias_source_probe_frequencies_hz"]
        self.assertEqual(len(probes), 23)
        self.assertEqual(probes[0], 50.0)
        self.assertEqual(probes[-1], 500.0)
        self.assertTrue(all(50.0 <= value <= 500.0 for value in probes))
        self.assertEqual(
            frequency["alias_destination_formula_hz"],
            "abs(((source_frequency_hz+50)%100)-50)",
        )
        self.assertTrue(
            frequency["full_folding_band_gate_is_required_before_development_partition_open"]
        )
        self.assertNotIn("stopband_probe_hz", frequency)

    def test_static_design_must_pass_before_manifest_or_partition_access(self):
        sequence = self.contract["partition_access_sequence"]
        design = sequence.index(
            "construct_registered_filter_coefficients_exactly_once_before_any_fixture_array_open"
        )
        static = sequence.index(
            "run_static_pole_dense_frequency_alias_fold_map_impulse_and_step_design_gates"
        )
        manifest = sequence.index(
            "validate_fixture_manifest_without_opening_partition_arrays"
        )
        development = sequence.index("open_development_target_free_partition_once")
        qualification = sequence.index(
            "open_qualification_target_free_partition_once_only_if_every_development_gate_passed"
        )
        self.assertLess(design, static)
        self.assertLess(static, manifest)
        self.assertLess(manifest, development)
        self.assertLess(development, qualification)
        self.assertIn(
            "park_with_development_and_qualification_unopened_if_any_static_design_gate_fails",
            sequence,
        )

    def test_fresh_partitions_schedules_and_protected_evidence_are_unchanged(self):
        fixture = self.contract["fixture_contract"]
        self.assertTrue(fixture["target_free"])
        self.assertEqual(fixture["development"]["seed"], 2501)
        self.assertEqual(fixture["qualification"]["seed"], 2502)
        self.assertEqual(fixture["development"]["items"], 12)
        self.assertEqual(fixture["qualification"]["items"], 12)
        self.assertEqual(len(fixture["signal_families"]), 6)
        self.assertEqual(len(self.contract["registered_chunk_schedules"]), 7)
        self.assertEqual(len(self.contract["registered_resume_cut_source_samples"]), 10)
        self.assertEqual(
            len(self.contract["registered_future_mutation_cut_source_samples"]), 3
        )
        self.assertEqual(
            self.contract["protected_evidence"]["unopened_synthetic_seeds"],
            [2402, 2501, 2502],
        )

    def test_state_resources_access_and_refusal_surfaces_remain_bounded(self):
        state = self.contract["state_contract"]
        self.assertEqual(state["maximum_total_sos_sections"], 17)
        self.assertEqual(state["maximum_filter_state_array_bytes"], 1360)
        self.assertEqual(state["mutable_state_max_bytes"], 4096)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["maximum_concurrent_workers"], 1)
        self.assertEqual(caps["maximum_generated_bytes_total"], 8 * 1024 * 1024)
        self.assertEqual(caps["maximum_internal_runtime_sec"], 45)
        counters = self.contract["required_access_counters"]
        self.assertEqual(len(counters), 23)
        self.assertEqual(len(counters), len(set(counters)))
        refusals = self.contract["refusal_ids"]
        self.assertEqual(len(refusals), 45)
        self.assertEqual(len(refusals), len(set(refusals)))
        for refusal in (
            "superseded_contract_or_request_selected",
            "dedicated_antialias_stage_missing_reordered_or_spec_mismatch",
            "full_folding_band_attenuation_failed",
            "alias_fold_map_failed",
        ):
            self.assertIn(refusal, refusals)
        for name, value in caps.items():
            if any(
                term in name
                for term in (
                    "network",
                    "real_",
                    "consumed",
                    "target_",
                    "checkpoint",
                    "model_",
                    "training",
                    "parameter",
                    "rw3",
                    "stream_",
                )
            ):
                self.assertEqual(value, 0, name)

    def test_time_semantics_separate_grid_availability_delay_and_latency(self):
        output = self.contract["planned_pipeline"]["output"]
        self.assertEqual(
            output["sample_grid_timestamp_reference"],
            "kept_source_sample_before_frequency_dependent_filter_delay",
        )
        self.assertEqual(
            output["effective_signal_timestamp"],
            "unavailable_because_group_delay_is_frequency_dependent",
        )
        self.assertEqual(output["right_context_samples"], 0)
        self.assertFalse(output["delay_compensation_allowed"])
        self.assertFalse(output["end_to_end_latency_measured"])
        warnings = self.contract["claim_boundaries"]["warnings_required"]
        self.assertIn(
            "45_to_50_hz_is_a_transition_band_without_a_passband_claim", warnings
        )
        self.assertIn(
            "frequency_dependent_filter_delay_is_not_end_to_end_latency", warnings
        )

    def test_no_runtime_cli_dependency_or_numeric_artifact_exists(self):
        planned = self.contract["planned_implementation"]
        self.assertFalse(planned["files_exist_now"])
        self.assertFalse(planned["cli_exists_now"])
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
        self.assertIn("Filter design or coefficient generation | 0", self.audit)
        self.assertIn("Every `authorized_now` field", self.amendment)

    def test_primary_sources_are_unique_and_claim_boundary_stays_narrow(self):
        sources = self.contract["primary_sources"]
        self.assertEqual(len(sources), 19)
        self.assertEqual(len({row["id"] for row in sources}), 19)
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        must_not_claim = " ".join(
            self.contract["claim_boundaries"]["must_not_claim"]
        )
        self.assertIn("official Brain2Qwerty v2", must_not_claim)
        self.assertIn("decoding accuracy", must_not_claim)
        self.assertIn("end-to-end", must_not_claim)
        self.assertIn("portable-device", must_not_claim)
        self.assertIn("stronger, source-audited protocol", self.amendment)


if __name__ == "__main__":
    unittest.main()
