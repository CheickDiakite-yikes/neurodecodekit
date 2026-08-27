from __future__ import annotations

import dataclasses
import importlib.util
import inspect
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit import comm_g1_cli  # noqa: E402
from neurodecodekit.experiments import comm_g1_generated as experiment  # noqa: E402

NUMERICAL_AVAILABLE = all(
    importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn")
)


def _fake_green_proof() -> dict[str, object]:
    commit = "a" * 40
    return {
        "branch": "codex/comm-g1-test",
        "head_sha": commit,
        "remote_head_sha": commit,
        "CI_run_id": 101,
        "CI_head_sha": commit,
        "CI_conclusion": "success",
        "base_python_job_id": 102,
        "base_python_job_name": "Base Python",
        "base_python_job_conclusion": "success",
        "optional_neuro_readers_job_id": 103,
        "optional_neuro_readers_job_name": "Optional Neuro Readers",
        "optional_neuro_readers_job_conclusion": "success",
    }


class CommG1GeneratedBaseTests(unittest.TestCase):
    def test_registration_and_amendment_hashes_are_bound(self) -> None:
        contract, amendment = experiment.load_registration(ROOT)
        self.assertEqual(tuple(contract["conditions"]), experiment.CONDITIONS)
        self.assertEqual(amendment["corrected_derangement"]["fixed_points"], 0)

    def test_plan_is_generated_only_and_exact(self) -> None:
        value = experiment.plan()
        self.assertTrue(value["generated_only"])
        self.assertEqual(value["participants"], 6)
        self.assertEqual(value["rows"], 144)
        self.assertEqual(value["parameter_update_fits"], 60)
        self.assertEqual(value["prediction_sets"], 60)
        self.assertEqual(value["prediction_rows"], 1440)
        self.assertEqual(value["real_or_private_operations"], 0)

    def test_cli_has_only_plan_qualify_and_inspect(self) -> None:
        parser = comm_g1_cli._parser()
        help_text = parser.format_help()
        for command in ("plan", "qualify", "inspect"):
            self.assertIn(command, help_text)
        for forbidden in (
            "download",
            "execute-real",
            "score-real",
            "provider",
            "device",
            "stream",
        ):
            self.assertNotIn(forbidden, help_text)

    def test_qualification_fails_closed_without_remote_green_proof(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaises(experiment.CommG1Refusal),
        ):
            experiment.run_generated_qualification(
                Path(directory) / "result.json",
                root=ROOT,
                remote_proof_collector=lambda _root: {},
            )


@unittest.skipUnless(NUMERICAL_AVAILABLE, "optional classical dependencies are not installed")
class CommG1GeneratedNumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.saved_environment = {
            name: os.environ.get(name) for name in experiment.THREAD_ENVIRONMENT
        }
        os.environ.update({name: "1" for name in experiment.THREAD_ENVIRONMENT})
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "comm-g1-result.json"
        cls.result = experiment.run_generated_qualification(
            cls.output,
            root=ROOT,
            remote_proof_collector=lambda _root: _fake_green_proof(),
            peak_rss_reader=lambda: 200_000_000,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()
        for name, value in cls.saved_environment.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_fixture_preserves_identity_timing_masks_and_roles(self) -> None:
        rows, targets, generated_bytes = experiment.generate_fixture()
        self.assertEqual(len(rows), 144)
        self.assertEqual(len(targets), 144)
        self.assertEqual(generated_bytes, 144 * 14 * 128 * 8)
        row = rows[0]
        self.assertEqual(row.sampling_rate_hz, 128)
        self.assertEqual(row.true_length, 128)
        self.assertFalse(any(row.padding_mask))
        self.assertEqual(row.source_sample_stop - row.source_sample_start, 128)
        self.assertEqual(row.source_time_stop_seconds - row.source_time_start_seconds, 1.0)
        self.assertEqual(row.channel_names, experiment.CHANNEL_NAMES)
        self.assertEqual(row.channel_roles, experiment.CHANNEL_ROLES)
        self.assertEqual(row.channel_geometry, experiment.CHANNEL_GEOMETRY)
        self.assertNotIn("target", {field.name for field in dataclasses.fields(row)})

    def test_feature_producer_cannot_accept_target_or_label(self) -> None:
        parameters = inspect.signature(
            experiment.causal_log_relative_band_features
        ).parameters
        self.assertNotIn("target", parameters)
        self.assertNotIn("label", parameters)
        rows, _targets, _bytes = experiment.generate_fixture(participants=("gsub-01",))
        with self.assertRaises(TypeError):
            experiment.causal_log_relative_band_features(
                rows[0].signal, target=0  # type: ignore[call-arg]
            )

    def test_fold_capability_excludes_held_out_targets(self) -> None:
        rows, targets, _bytes = experiment.generate_fixture()
        capability, held_targets = experiment.build_fold_capability(
            rows, targets, "gsub-01"
        )
        held_ids = {row.item_id for row in capability.held_out_rows}
        self.assertEqual(len(capability.source_rows), 120)
        self.assertEqual(len(capability.held_out_rows), 24)
        self.assertFalse(held_ids & set(capability.source_targets))
        self.assertEqual(held_ids, set(held_targets))
        self.assertNotIn("held_targets", capability.__dict__)

    def test_corrected_derangement_has_no_fixed_points_and_preserves_marginal(self) -> None:
        np = experiment._np()
        rows, targets, _bytes = experiment.generate_fixture(participants=("gsub-01",))
        values = np.arange(len(rows) * 3, dtype="float64").reshape(len(rows), 3)
        changed = experiment.corrected_source_derangement(rows, targets, values)
        self.assertEqual(sorted(map(tuple, changed)), sorted(map(tuple, values)))
        self.assertTrue(all(not np.array_equal(left, right) for left, right in zip(values, changed)))
        malformed_targets = dict(targets)
        malformed_targets.pop(rows[0].item_id)
        with self.assertRaises(experiment.CommG1Refusal):
            experiment.corrected_source_derangement(rows, malformed_targets, values)

    def test_positive_fixture_routes_R1_under_exact_schedule(self) -> None:
        case = self.result["cases"]["residual_EEG_increment"]
        self.assertEqual(case["route"], "COMM-G1-R1")
        self.assertGreaterEqual(case["candidate_delta_over_P"], 0.1)
        self.assertGreaterEqual(case["candidate_delta_over_deranged"], 0.1)
        self.assertEqual(case["positive_participants"], 6)
        schedule = self.result["positive_schedule"]
        self.assertEqual(schedule["residualizer_fits"], 6)
        self.assertEqual(schedule["classifier_or_prior_fits"], 54)
        self.assertEqual(schedule["total_parameter_update_fits"], 60)
        self.assertEqual(schedule["model_inference_runs"], 60)
        self.assertEqual(schedule["prediction_sets"], 60)
        self.assertEqual(schedule["prediction_rows"], 1440)
        self.assertEqual(schedule["post_target_updates"], 0)

    def test_shortcut_fixtures_are_structural_and_add_no_hidden_fits(self) -> None:
        expected = {
            "EOG_only": "eog",
            "oral_EMG_only": "oral",
            "posterior_only": "posterior",
            "cue_only": "cue_timing",
            "timing_only": "cue_timing",
            "mixed_without_increment": "eog",
        }
        for name in experiment.CASE_FAMILIES[1:]:
            case = self.result["cases"][name]
            self.assertEqual(
                case["status"], "passed_targeted_shortcut_fixture_without_model_fit"
            )
            self.assertNotIn("route", case)
            if name in expected:
                self.assertEqual(case["largest_class_spread_group"], expected[name])

    def test_firewall_freeze_and_delivery_refusals_are_exercised(self) -> None:
        refusals = self.result["firewall_refusals"]
        self.assertEqual(refusals["pre_freeze_target_delivery"], 1)
        self.assertEqual(refusals["repeated_target_delivery"], 1)
        self.assertEqual(refusals["prediction_tamper"], 1)
        adversarial = self.result["adversarial_qualification"]
        self.assertGreaterEqual(adversarial["refusal_count"], 30)
        self.assertEqual(
            adversarial["refusal_count"], len(set(adversarial["refusal_ids"]))
        )

    def test_result_is_bounded_target_free_and_aggregate_inspectable(self) -> None:
        payload = self.output.read_bytes()
        measurements = self.result["measurements"]
        self.assertEqual(measurements["public_output_bytes"], len(payload))
        self.assertLessEqual(len(payload), 1 << 20)
        self.assertLessEqual(measurements["generated_input_bytes"], 32 << 20)
        self.assertLessEqual(
            measurements["private_generated_prediction_bytes_maximum"], 32 << 20
        )
        self.assertTrue(measurements["producer_causal"])
        self.assertFalse(measurements["end_to_end_latency_measured"])
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))
        self.assertTrue(
            all(value is False for key, value in self.result["claim_boundary"].items() if key != "scientific_value")
        )
        summary = experiment.inspect_result(self.output)
        self.assertEqual(summary["positive_route"], "COMM-G1-R1")
        serialized = json.dumps(summary, sort_keys=True)
        for forbidden in ('"probabilities":', '"participant_id":', '"target":'):
            self.assertNotIn(forbidden, serialized)

    def test_output_no_clobber_and_caps_fail_closed(self) -> None:
        with self.assertRaises(experiment.CommG1Refusal):
            experiment.run_generated_qualification(
                self.output,
                root=ROOT,
                remote_proof_collector=lambda _root: _fake_green_proof(),
            )
        output = Path(self.temporary.name) / "rss-cap.json"
        with self.assertRaises(experiment.CommG1Refusal):
            experiment.run_generated_qualification(
                output,
                root=ROOT,
                remote_proof_collector=lambda _root: _fake_green_proof(),
                peak_rss_reader=lambda: experiment.CAPS[
                    "peak_process_tree_RSS_bytes"
                ]
                + 1,
            )
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
