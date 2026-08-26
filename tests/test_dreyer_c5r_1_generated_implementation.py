from __future__ import annotations

import hashlib
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

from neurodecodekit.datasets.dreyer_c5r_1 import (  # noqa: E402
    DreyerDataRefusal,
    build_generated_edf_header,
    log_relative_band_features,
    parse_edf_fixed_header,
)
from neurodecodekit.evaluation import dreyer_c5r_1_score as scorer  # noqa: E402
from neurodecodekit.experiments import dreyer_c5r_1 as experiment  # noqa: E402
from neurodecodekit import dreyer_c5r_1_cli  # noqa: E402


NUMERICAL_AVAILABLE = all(
    importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn")
)
CONTRACT_PATH = ROOT / experiment.CONTRACT_RELATIVE_PATH


class DreyerC5R1GeneratedBaseTests(unittest.TestCase):
    def test_contract_hash_condition_inventory_and_real_schedule_are_exact(self) -> None:
        payload = CONTRACT_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), experiment.CONTRACT_SHA256)
        contract = json.loads(payload)
        self.assertEqual(tuple(contract["conditions"]), scorer.CONDITIONS)
        self.assertEqual(
            experiment.plan_real_schedule(),
            {
                "outer_folds": 60,
                "inner_folds": 5,
                "parameter_update_fits": 4_740,
                "model_inference_runs": 3_660,
                "held_out_prediction_sets": 1_020,
                "held_out_prediction_rows": 81_600,
            },
        )

    def test_strict_generated_edf_header_parser_exposes_only_allowlisted_facts(self) -> None:
        labels = ("C3", "C4", "EOG-V", "EMG-L", "EDF Annotations")
        payload = build_generated_edf_header(labels)
        summary = parse_edf_fixed_header(payload)
        self.assertEqual(summary.labels, labels)
        self.assertEqual(summary.signal_count, 5)
        self.assertEqual(summary.header_bytes, 1_536)
        self.assertEqual(summary.sampling_rates_hz, (512.0,) * 5)
        self.assertFalse(hasattr(summary, "patient"))
        self.assertFalse(hasattr(summary, "recording"))
        self.assertNotIn("GENERATED-PATIENT", repr(summary))

    def test_edf_parser_refuses_truncation_duplicate_and_non_ascii_labels(self) -> None:
        payload = build_generated_edf_header(("C3", "C4", "EOG-V"))
        malformed = (
            payload[:-1],
            payload[:256] + payload[256:272] + payload[256:272] + payload[288:],
            payload[:256] + b"\xff" + payload[257:],
        )
        for candidate in malformed:
            with self.subTest(length=len(candidate)):
                with self.assertRaises(DreyerDataRefusal):
                    parse_edf_fixed_header(candidate)

    def test_feature_producer_has_no_target_or_label_input(self) -> None:
        parameters = inspect.signature(log_relative_band_features).parameters
        self.assertNotIn("target", parameters)
        self.assertNotIn("label", parameters)
        with self.assertRaises(TypeError):
            log_relative_band_features([[0.0] * 512], target=1)  # type: ignore[call-arg]

    def test_cli_is_generated_only_and_has_no_real_execute_or_score_command(self) -> None:
        help_text = dreyer_c5r_1_cli._parser().format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertIn("inspect", help_text)
        for forbidden in ("execute-real", "download", "score-real", "acquire"):
            self.assertNotIn(forbidden, help_text)


@unittest.skipUnless(NUMERICAL_AVAILABLE, "optional classical dependencies are not installed")
class DreyerC5R1GeneratedNumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.saved_environment = {
            name: os.environ.get(name) for name in experiment.THREAD_ENVIRONMENT
        }
        os.environ.update({name: "1" for name in experiment.THREAD_ENVIRONMENT})
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output_path = Path(cls.temporary.name) / "qualification.json"
        cls.result = experiment.run_generated_qualification(cls.output_path, root=ROOT)
        cls.output_bytes = cls.output_path.read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()
        for name, value in cls.saved_environment.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_generated_qualification_passes_positive_router_and_exact_schedule(self) -> None:
        self.assertEqual(
            self.result["status"], "passed_generated_only_no_real_or_private_data"
        )
        self.assertEqual(self.result["synthetic_router"]["route"], "DREYERC5R-R1")
        self.assertTrue(self.result["synthetic_router"]["primary_gate_passed"])
        self.assertEqual(self.result["schedule"]["parameter_update_fits"], 330)
        self.assertEqual(self.result["schedule"]["model_inference_runs"], 258)
        self.assertEqual(self.result["schedule"]["held_out_prediction_sets"], 102)
        self.assertEqual(self.result["schedule"]["prediction_rows"], 2_040)
        self.assertEqual(self.result["schedule"]["post_target_updates"], 0)

    def test_generated_result_is_bounded_and_has_zero_real_access(self) -> None:
        measurements = self.result["measurements"]
        self.assertEqual(measurements["public_output_bytes"], len(self.output_bytes))
        self.assertLessEqual(len(self.output_bytes), 1 << 20)
        self.assertLessEqual(measurements["generated_input_bytes"], 32 << 20)
        self.assertLessEqual(measurements["private_temporary_prediction_bytes"], 32 << 20)
        self.assertTrue(measurements["producer_causal"])
        self.assertFalse(measurements["end_to_end_latency_measured"])
        counters = self.result["access_counters"]
        for key, value in counters.items():
            self.assertEqual(value, 0, key)

    def test_firewall_freeze_tamper_and_delivery_cases_all_passed(self) -> None:
        cases = self.result["cases"]
        self.assertEqual(cases["target_delivery_before_freeze_refusals"], 1)
        self.assertEqual(cases["target_repeat_delivery_refusals"], 1)
        self.assertEqual(cases["prediction_tamper_refusals"], 1)
        freeze = self.result["prediction_freeze"]
        self.assertFalse(freeze["contains_individual_prediction_probability_target_or_outcome"])
        serialized = json.dumps(freeze, sort_keys=True)
        for forbidden in ('"probabilities"', '"target"', '"participant":"', "/Users/"):
            self.assertNotIn(forbidden, serialized)

    def test_fixture_replay_and_spectral_localization_are_stable(self) -> None:
        self.assertTrue(self.result["cases"]["deterministic_feature_replay"])
        self.assertEqual(
            self.result["cases"]["causal_spectral_feature"]["sha256"],
            "f712325a77aeb129f1bdb4e3072edaf1671d2a00056f17196b69cec0e1052bfd",
        )
        first = experiment.generate_feature_fixture()
        second = experiment.generate_feature_fixture()
        self.assertEqual(experiment._canonical_bytes(first[0]), experiment._canonical_bytes(second[0]))
        self.assertEqual(first[1:], second[1:])

    def test_capability_contains_source_targets_but_no_held_out_target(self) -> None:
        rows, targets, _bytes = experiment.generate_feature_fixture(participants=4)
        capability, held_targets = experiment.build_fold_capability(
            rows, targets, "g-01", inner_folds=3
        )
        held_ids = {row["row_id"] for row in capability.held_out_rows}
        self.assertFalse(held_ids & set(capability.source_targets))
        self.assertEqual(held_ids, set(held_targets))
        self.assertNotIn("target", capability.__dict__)
        self.assertNotIn("held_targets", capability.__dict__)

    def test_output_is_no_clobber_and_inspection_is_summary_only(self) -> None:
        with self.assertRaises(experiment.DreyerExperimentRefusal):
            experiment.run_generated_qualification(self.output_path, root=ROOT)
        summary = experiment.inspect_generated_result(self.output_path)
        self.assertEqual(summary["synthetic_route"], "DREYERC5R-R1")
        self.assertNotIn("prediction_freeze", summary)
        self.assertNotIn("generated_fixture", summary)

    def test_scorer_routes_null_predictions_to_R3(self) -> None:
        rows, targets = _constant_prediction_fixture(probability_margin=0.0)
        freeze = scorer.build_prediction_freeze(
            rows,
            expected_participants=4,
            expected_rows_per_participant=8,
            contract_sha256=experiment.CONTRACT_SHA256,
        )
        score = scorer.score_frozen_predictions(
            rows,
            targets,
            freeze,
            expected_participants=4,
            expected_rows_per_participant=8,
            contract_sha256=experiment.CONTRACT_SHA256,
            positive_participants_minimum=3,
        )
        self.assertEqual(score["route"], "DREYERC5R-R3")
        self.assertFalse(score["primary_gate_passed"])

    def test_scorer_routes_subthreshold_candidate_to_R2(self) -> None:
        rows, targets = _constant_prediction_fixture(probability_margin=0.005)
        freeze = scorer.build_prediction_freeze(
            rows,
            expected_participants=4,
            expected_rows_per_participant=8,
            contract_sha256=experiment.CONTRACT_SHA256,
        )
        score = scorer.score_frozen_predictions(
            rows,
            targets,
            freeze,
            expected_participants=4,
            expected_rows_per_participant=8,
            contract_sha256=experiment.CONTRACT_SHA256,
            positive_participants_minimum=3,
        )
        self.assertEqual(score["route"], "DREYERC5R-R2")
        self.assertFalse(score["primary_gate_passed"])


def _constant_prediction_fixture(
    *, probability_margin: float
) -> tuple[list[dict[str, object]], dict[str, int]]:
    rows: list[dict[str, object]] = []
    targets: dict[str, int] = {}
    for participant in range(1, 5):
        for run in (1, 2):
            for trial in range(4):
                target = (run + trial) % 2
                row_id = f"p-{participant:02d}-r{run}-t{trial}"
                targets[row_id] = target
                for condition in scorer.CONDITIONS:
                    probability = 0.5
                    if condition == "late_N_plus_R" and probability_margin:
                        probability += probability_margin if target else -probability_margin
                    rows.append(
                        {
                            "participant": f"p-{participant:02d}",
                            "run": run,
                            "trial": trial,
                            "row_id": row_id,
                            "condition": condition,
                            "probabilities": [1.0 - probability, probability],
                        }
                    )
    return rows, targets


if __name__ == "__main__":
    unittest.main()
