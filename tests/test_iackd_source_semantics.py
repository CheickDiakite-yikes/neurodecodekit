import copy
import io
import json
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.preprocess import iackd_source_semantics as semantics
from neurodecodekit.preprocess.iackd_source_semantics import (
    POLICY_SHA256,
    REFUSAL_IDS,
    SourceSemanticsRefusal,
    count_field_for_bids_version,
    load_qualification_report,
    load_registered_policy,
    main,
    make_generated_fixture,
    run_generated_mutation_suite,
    run_synthetic_qualification,
    summarize_qualification,
    validate_generated_fixture,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


class IACKDSourceSemanticsPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded = load_registered_policy(ROOT)
        cls.policy = cls.loaded["policy"]

    def fixture(self, optional=False):
        return make_generated_fixture(
            include_optional_references=optional,
            policy=self.policy,
        )

    def refusal(self, fixture, refusal_id):
        with self.assertRaises(SourceSemanticsRefusal) as raised:
            validate_generated_fixture(fixture, self.policy)
        self.assertEqual(raised.exception.refusal_id, refusal_id)

    def test_green_policy_registry_and_canonical_hash_are_exact(self):
        self.assertEqual(self.loaded["policy_sha256"], POLICY_SHA256)
        self.assertEqual(self.policy["dataset_BIDS_version"], "1.7.0")
        self.assertEqual(self.policy["version_specific_misc_count_field"], "MiscChannelCount")
        self.assertEqual(self.policy["current_BIDS_migration_field"], "MISCChannelCount")

    def test_version_specific_count_field_spelling_is_explicit(self):
        self.assertEqual(count_field_for_bids_version("1.7.0"), "MiscChannelCount")
        self.assertEqual(count_field_for_bids_version("1.11.1"), "MISCChannelCount")
        with self.assertRaises(SourceSemanticsRefusal) as raised:
            count_field_for_bids_version("latest")
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[1])

    def test_generated_29_and_31_row_signatures_preserve_source_counts(self):
        summaries = [
            validate_generated_fixture(self.fixture(optional), self.policy)
            for optional in (False, True)
        ]
        self.assertEqual([row["row_count"] for row in summaries], [29, 31])
        self.assertEqual(
            [row["source_counts"]["EEGChannelCount"] for row in summaries],
            [26, 28],
        )
        self.assertEqual(
            [row["source_counts"]["MiscChannelCount"] for row in summaries],
            [3, 3],
        )
        self.assertEqual([row["predictive_EEG_count"] for row in summaries], [26, 26])

    def test_roles_source_types_and_model_mask_are_separate(self):
        summary = validate_generated_fixture(self.fixture(), self.policy)
        self.assertEqual(
            summary["functional_role_counts"],
            {"ocular_control": 2, "predictive_eeg": 26, "trigger_control": 1},
        )
        self.assertEqual(len(summary["predictive_output_order"]), 26)
        self.assertEqual(
            set(summary["bindings"]),
            set(semantics.EXPECTED_BINDING_FIELDS),
        )

    def test_optional_references_are_finite_nonpredictive_EEG(self):
        fixture = self.fixture(optional=True)
        references = [row for row in fixture["channels"] if row["name"] in {"M1", "M2"}]
        self.assertEqual([row["type"] for row in references], ["EEG", "EEG"])
        self.assertTrue(all(row["geometry_m"] is not None for row in references))
        summary = validate_generated_fixture(fixture, self.policy)
        self.assertEqual(summary["functional_role_counts"]["optional_reference_eeg"], 2)
        self.assertEqual(summary["predictive_EEG_count"], 26)

    def test_controls_remain_misc_and_geometry_unavailable(self):
        fixture = self.fixture()
        controls = [row for row in fixture["channels"] if row["name"] in {"HEOG", "VEOG", "Trigger"}]
        self.assertEqual([row["type"] for row in controls], ["MISC", "MISC", "MISC"])
        self.assertTrue(all(row["geometry_m"] is None for row in controls))
        self.assertEqual(fixture["eeg_sidecar"]["MiscChannelCount"], 3)
        self.assertEqual(fixture["eeg_sidecar"]["EOGChannelCount"], 0)
        self.assertEqual(fixture["eeg_sidecar"]["TriggerChannelCount"], 0)

    def test_normalized_matching_preserves_display_spelling_in_hash(self):
        fixture = self.fixture()
        fixture["channels"][0]["name"] = " fp1 "
        projected = validate_generated_fixture(fixture, self.policy, check_bindings=False)
        fixture["expected_bindings"] = projected["bindings"]
        accepted = validate_generated_fixture(fixture, self.policy)
        self.assertEqual(accepted["predictive_output_order"][0], "Fp1")
        self.assertNotEqual(
            accepted["bindings"]["source_order_sha256"],
            self.fixture()["expected_bindings"]["source_order_sha256"],
        )

    def test_source_order_mutation_refuses_even_if_indices_are_rewritten(self):
        fixture = self.fixture()
        fixture["channels"][0], fixture["channels"][1] = (
            fixture["channels"][1],
            fixture["channels"][0],
        )
        for index, row in enumerate(fixture["channels"]):
            row["source_index"] = index
        self.refusal(fixture, REFUSAL_IDS[11])

    def test_wrong_BIDS_version_and_newer_count_spelling_refuse(self):
        version = self.fixture()
        version["dataset"]["BIDSVersion"] = "1.11.1"
        self.refusal(version, REFUSAL_IDS[1])
        spelling = self.fixture()
        spelling["eeg_sidecar"]["MISCChannelCount"] = spelling["eeg_sidecar"].pop(
            "MiscChannelCount"
        )
        self.refusal(spelling, REFUSAL_IDS[1])

    def test_unknown_duplicate_missing_and_wrong_type_channels_refuse(self):
        unknown = self.fixture()
        unknown["channels"][0]["name"] = "Unknown"
        self.refusal(unknown, REFUSAL_IDS[4])
        duplicate = self.fixture()
        duplicate["channels"][1]["name"] = duplicate["channels"][0]["name"]
        self.refusal(duplicate, REFUSAL_IDS[4])
        wrong_type = self.fixture()
        next(row for row in wrong_type["channels"] if row["name"] == "HEOG")[
            "type"
        ] = "HEOG"
        self.refusal(wrong_type, REFUSAL_IDS[5])

    def test_count_sampling_and_reference_drift_refuse(self):
        count = self.fixture()
        count["eeg_sidecar"]["MiscChannelCount"] = 2
        self.refusal(count, REFUSAL_IDS[6])
        sampling = self.fixture()
        sampling["eeg_sidecar"]["SamplingFrequency"] = 512
        self.refusal(sampling, REFUSAL_IDS[7])
        reference = self.fixture()
        reference["eeg_sidecar"]["EEGReference"] = "Cz"
        self.refusal(reference, REFUSAL_IDS[7])

    def test_required_and_optional_geometry_fail_closed(self):
        predictive = self.fixture()
        predictive["channels"][0]["geometry_m"] = None
        self.refusal(predictive, REFUSAL_IDS[10])
        optional = self.fixture(optional=True)
        next(row for row in optional["channels"] if row["name"] == "M1")[
            "geometry_m"
        ] = None
        self.refusal(optional, REFUSAL_IDS[10])
        nonfinite = self.fixture()
        nonfinite["channels"][0]["geometry_m"] = [0.0, float("nan"), 0.5]
        self.refusal(nonfinite, REFUSAL_IDS[10])

    def test_target_firewall_scans_nested_keys_before_semantics(self):
        for key in ("target", "labels", "reference_text", "predictions", "scores"):
            with self.subTest(key=key):
                fixture = self.fixture()
                fixture["dataset"][key] = "forbidden"
                self.refusal(fixture, REFUSAL_IDS[12])

    def test_all_thirteen_mutations_cover_twelve_distinct_refusal_classes(self):
        observed = run_generated_mutation_suite(self.fixture(), self.policy)
        self.assertEqual(len(observed), 13)
        self.assertEqual(len({row["refusal_id"] for row in observed}), 12)
        self.assertEqual(
            {row["mutation"] for row in observed if row["refusal_id"] == REFUSAL_IDS[1]},
            {"BIDS_version", "count_spelling"},
        )

    def test_policy_overlap_model_mask_and_hash_drift_refuse(self):
        overlap = copy.deepcopy(self.policy)
        overlap["role_rules"][1]["source_names"].append("Fp1")
        with self.assertRaises(SourceSemanticsRefusal) as role:
            semantics._compile_policy(overlap, expected_hash=None)
        self.assertEqual(role.exception.refusal_id, REFUSAL_IDS[8])
        model = copy.deepcopy(self.policy)
        model["role_rules"][0]["model_inclusion"] = False
        with self.assertRaises(SourceSemanticsRefusal) as mask:
            semantics._compile_policy(model, expected_hash=None)
        self.assertEqual(mask.exception.refusal_id, REFUSAL_IDS[9])
        drift = copy.deepcopy(self.policy)
        drift["policy_version"] = "0.1.1"
        with self.assertRaises(SourceSemanticsRefusal) as hashed:
            semantics._compile_policy(drift, expected_hash=POLICY_SHA256)
        self.assertEqual(hashed.exception.refusal_id, REFUSAL_IDS[0])


class IACKDSourceSemanticsQualificationTests(unittest.TestCase):
    def run_fixture(self, output, **kwargs):
        return run_synthetic_qualification(
            output,
            repo_root=ROOT,
            environ=THREAD_ENV,
            rss_reader=lambda: 24 * 1024 * 1024,
            **kwargs,
        )

    def test_bounded_roundtrip_summary_and_measurements(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            outcome = self.run_fixture(output)
            loaded = load_qualification_report(output)
            summary = summarize_qualification(loaded)
        self.assertEqual(outcome.report, loaded)
        self.assertEqual(summary["fixture_row_counts"], [29, 31])
        self.assertEqual(summary["predictive_EEG_counts"], [26, 26])
        self.assertEqual(summary["distinct_refusal_classes"], 12)
        self.assertLess(summary["generated_output_bytes"], 2 * 1024 * 1024)
        self.assertLess(summary["runtime_seconds"], 30)
        self.assertIsNone(summary["producer_is_causal"])
        self.assertFalse(summary["end_to_end_latency_measured"])

    def test_report_replay_is_byte_identical_under_fixed_monitors(self):
        def clock_factory():
            values = iter((0.0, 0.1, 0.2))
            return lambda: next(values)

        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            self.run_fixture(first, clock=clock_factory())
            self.run_fixture(second, clock=clock_factory())
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_wrong_thread_environment_output_collision_and_small_cap_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            with self.assertRaises(SourceSemanticsRefusal) as thread:
                run_synthetic_qualification(
                    output,
                    repo_root=ROOT,
                    environ={**THREAD_ENV, "OMP_NUM_THREADS": "2"},
                )
            self.assertEqual(thread.exception.refusal_id, REFUSAL_IDS[14])
            output.write_text("occupied", encoding="utf-8")
            with self.assertRaises(SourceSemanticsRefusal) as collision:
                self.run_fixture(output)
            self.assertEqual(collision.exception.refusal_id, REFUSAL_IDS[14])
            output.unlink()
            with self.assertRaises(SourceSemanticsRefusal) as cap:
                self.run_fixture(output, maximum_output_bytes=100)
            self.assertEqual(cap.exception.refusal_id, REFUSAL_IDS[14])

    def test_malformed_report_and_forbidden_counter_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            report = copy.deepcopy(self.run_fixture(output).report)
            output.unlink()
            report["access_counters"]["target_or_label_reads"] = 1
            output.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(SourceSemanticsRefusal) as raised:
                load_qualification_report(output)
        self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[13])

    def test_new_heavy_import_refuses_and_is_cleaned_up(self):
        module_name = next(
            name for name in semantics.HEAVY_MODULE_ROOTS if name not in sys.modules
        )
        original = semantics.run_generated_mutation_suite

        def importing_suite(*args, **kwargs):
            sys.modules[module_name] = types.ModuleType(module_name)
            return original(*args, **kwargs)

        try:
            with tempfile.TemporaryDirectory() as directory:
                with patch.object(
                    semantics,
                    "run_generated_mutation_suite",
                    side_effect=importing_suite,
                ):
                    with self.assertRaises(SourceSemanticsRefusal) as raised:
                        self.run_fixture(Path(directory) / "qualification.json")
            self.assertEqual(raised.exception.refusal_id, REFUSAL_IDS[13])
        finally:
            sys.modules.pop(module_name, None)

    def test_report_contains_aggregate_bindings_not_raw_fixture_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            report = self.run_fixture(Path(directory) / "qualification.json").report
        self.assertNotIn("channels", report)
        self.assertNotIn("geometry_m", json.dumps(report))
        self.assertEqual(report["access_counters"]["real_or_public_metadata_requests"], 0)
        self.assertEqual(report["access_counters"]["target_or_label_reads"], 0)
        self.assertEqual(report["access_counters"]["model_inference_runs"], 0)


class IACKDSourceSemanticsCLITests(unittest.TestCase):
    def test_default_plan_is_dry_run_and_has_no_execute_surface(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main([])
        plan = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(plan["generated_fixture_row_counts"], [29, 31])
        self.assertFalse(plan["real_or_public_data_authorized"])
        self.assertNotIn("execute", semantics.build_parser().format_help())

    def test_fixture_and_inspection_CLI_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            create_stdout = io.StringIO()
            with patch.dict(os.environ, THREAD_ENV):
                with patch.object(semantics, "_peak_rss_bytes", return_value=24 * 1024 * 1024):
                    with redirect_stdout(create_stdout):
                        create_code = main(["--fixture", "--out", str(output)])
            inspect_stdout = io.StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_code = main(["--inspect", str(output)])
            created = json.loads(create_stdout.getvalue())
            inspected = json.loads(inspect_stdout.getvalue())
        self.assertEqual((create_code, inspect_code), (0, 0))
        self.assertEqual(created, inspected)

    def test_fixture_refusal_is_safe_and_nonzero(self):
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            with patch.dict(os.environ, {**THREAD_ENV, "OMP_NUM_THREADS": "2"}):
                with redirect_stderr(stderr):
                    code = main(["--fixture", "--out", str(output)])
        self.assertEqual(code, 2)
        self.assertIn(REFUSAL_IDS[14], stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
