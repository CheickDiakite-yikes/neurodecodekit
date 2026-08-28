from __future__ import annotations

import ast
import copy
import json
import math
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated_score_only as score_only

ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict[str, object]:
    conditions = [
        "equal_prior",
        "cue_only",
        "all_recorded_peripheral_P",
        "P_plus_residual_central_EEG",
        "P_plus_class_destroyed_residual_central_EEG",
    ]
    return {
        "schema_version": "0.1.0",
        "gate_id": "COMM-P0-G-v0",
        "conditions": conditions,
        "trial_grammar": {"commands": ["yes", "no", "help", "stop"]},
        "participant_first_scoring": {
            "primary_condition": "P_plus_residual_central_EEG",
            "primary_log_loss_comparators": [
                "all_recorded_peripheral_P",
                "P_plus_class_destroyed_residual_central_EEG",
            ],
            "balanced_accuracy_comparator_inventory": [
                "equal_prior",
                "cue_only",
                "all_recorded_peripheral_P",
            ],
            "mean_margin_nats_per_item_minimum": 0.03,
            "positive_participants_minimum": 2,
            "complete_participants_denominator": 2,
            "exact_one_sided_sign_flip_p_maximum": 0.25,
            "balanced_accuracy_margin_minimum": 0.05,
            "probability_floor": 0.000001,
            "maximum_frozen_log_loss": 13.815510557964274,
            "participant_metric_decimal_places": 12,
        },
        "live_metrics": {
            "stable_commit_coverage_fraction_minimum": 0.70,
            "per_command_coverage_fraction_minimum": 0.50,
            "false_commits_per_inactive_minute_maximum": 0.10,
            "dropped_or_invalid_chunk_fraction_maximum": 0.01,
            "frames_processed_before_next_deadline_fraction_minimum": 0.99,
            "stable_commit_latency_median_seconds_maximum": 2.5,
            "stable_commit_latency_p95_seconds_maximum": 5.0,
            "capture_to_presentation_processing_overhead_p95_seconds_maximum": 0.5,
        },
    }


def _fixture() -> tuple[
    dict[str, object],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, int],
]:
    contract = _contract()
    trials: list[dict[str, object]] = []
    targets: dict[str, int] = {}
    for cohort_index, cohort in enumerate(score_only.COHORTS):
        for participant_index in range(2):
            participant = f"P-{cohort_index + 1}-{participant_index + 1:02d}"
            for phase in ["shadow", "live"] if cohort == "independent_replication" else ["shadow"]:
                for endpoint in score_only.ENDPOINTS:
                    for command in range(4):
                        item_id = f"{participant}-{phase}-{endpoint}-{command}"
                        trials.append(
                            {
                                "item_id": item_id,
                                "cohort_id": cohort,
                                "participant_id": participant,
                                "phase": phase,
                                "endpoint": endpoint,
                                "role": endpoint,
                            }
                        )
                        targets[item_id] = command

    predictions: list[dict[str, object]] = []
    for trial in trials:
        if trial["endpoint"] not in score_only.ENDPOINTS:
            continue
        truth = targets[str(trial["item_id"])]
        for condition in contract["conditions"]:
            if condition == "P_plus_residual_central_EEG":
                probabilities = [0.05, 0.05, 0.05, 0.05]
                probabilities[truth] = 0.85
            elif condition == "cue_only" and trial["endpoint"] == "prompted_intend":
                probabilities = [0.05, 0.05, 0.05, 0.05]
                probabilities[truth] = 0.85
            else:
                probabilities = [0.10, 0.10, 0.10, 0.10]
                probabilities[(truth + 1) % 4] = 0.70
            predictions.append(
                {
                    "item_id": trial["item_id"],
                    "cohort_id": trial["cohort_id"],
                    "participant_id": trial["participant_id"],
                    "endpoint": trial["endpoint"],
                    "phase": trial["phase"],
                    "condition": condition,
                    "probabilities": probabilities,
                }
            )

    observations: list[dict[str, object]] = []
    live_trials = [
        trial
        for trial in trials
        if trial["cohort_id"] == "independent_replication" and trial["phase"] == "live"
    ]
    participants = sorted({str(trial["participant_id"]) for trial in live_trials})
    for trial in live_trials:
        observations.append(
            {
                "interval_id": trial["item_id"],
                "cohort_id": trial["cohort_id"],
                "participant_id": trial["participant_id"],
                "endpoint": trial["endpoint"],
                "phase": trial["phase"],
                "active_intent": True,
                "inactive_surface": None,
                "duration_seconds": 3.0,
                "stable_commit": True,
                "predicted_command_index": targets[str(trial["item_id"])],
                "commit_count": 1,
                "invalid_chunk_count": 0,
                "total_chunk_count": 10,
                "processed_frame_count": 100,
                "total_frame_count": 100,
                "first_output_latency_seconds": 0.4,
                "stable_commit_latency_seconds": 1.5,
                "capture_to_presentation_overhead_seconds": 0.1,
                "clock_map_verified": True,
            }
        )
    for participant in participants:
        for surface in sorted(score_only.INACTIVE_SURFACES):
            observations.append(
                {
                    "interval_id": f"{participant}-inactive-{surface}",
                    "cohort_id": "independent_replication",
                    "participant_id": participant,
                    "endpoint": None,
                    "phase": "live",
                    "active_intent": False,
                    "inactive_surface": surface,
                    "duration_seconds": 120.0,
                    "stable_commit": False,
                    "predicted_command_index": None,
                    "commit_count": 0,
                    "invalid_chunk_count": 0,
                    "total_chunk_count": 10,
                    "processed_frame_count": 100,
                    "total_frame_count": 100,
                    "first_output_latency_seconds": None,
                    "stable_commit_latency_seconds": None,
                    "capture_to_presentation_overhead_seconds": None,
                    "clock_map_verified": True,
                }
            )
    return contract, trials, predictions, observations, targets


class CommP0GeneratedScoreOnlyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract, self.trials, self.predictions, self.observations, self.targets = _fixture()
        self.freeze = score_only.build_prediction_freeze_attestation(
            self.predictions, self.contract
        )
        self.authorization = {
            "prediction_freeze_green": True,
            "replication_artifact_freeze_green": True,
            "one_shot": True,
            "target_delivery_count": 1,
            "prior_score_count": 0,
        }

    def _score(
        self,
        *,
        worker: score_only.ScoreOnlyWorker | None = None,
        predictions: list[dict[str, object]] | None = None,
        observations: list[dict[str, object]] | None = None,
        freeze: dict[str, object] | None = None,
    ) -> dict[str, object]:
        used_predictions = predictions if predictions is not None else self.predictions
        used_freeze = freeze or score_only.build_prediction_freeze_attestation(
            used_predictions, self.contract
        )
        return (worker or score_only.ScoreOnlyWorker(self.contract)).score(
            trial_records=self.trials,
            prediction_records=used_predictions,
            live_observation_records=observations
            if observations is not None
            else self.observations,
            freeze_attestation=used_freeze,
            authorization=self.authorization,
            delivered_targets=self.targets,
        )

    def test_module_has_no_forbidden_import_or_capability(self) -> None:
        module_path = ROOT / "src/neurodecodekit/experiments/comm_p0_generated_score_only.py"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        self.assertFalse(imported.intersection(score_only.FORBIDDEN_IMPORT_ROOTS))
        self.assertNotIn("neurodecodekit", imported)
        audit = score_only.import_capability_audit()
        self.assertTrue(audit["standard_library_only"])
        self.assertEqual(audit["forbidden_import_roots_present"], [])
        self.assertFalse(audit["fit_or_model_capability"])
        self.assertFalse(audit["network_capability"])
        self.assertFalse(audit["real_or_private_data_capability"])

    def test_tampered_freeze_is_refused_before_target_delivery(self) -> None:
        tampered = dict(self.freeze)
        tampered["private_prediction_stream_sha256"] = "0" * 64
        worker = score_only.ScoreOnlyWorker(self.contract)
        with self.assertRaisesRegex(
            score_only.ScoreOnlyRefusal, "prediction_freeze_attestation_mismatch"
        ):
            self._score(worker=worker, freeze=tampered)
        self.assertFalse(worker.consumed)

    def test_repeated_delivery_or_score_is_refused(self) -> None:
        worker = score_only.ScoreOnlyWorker(self.contract)
        self._score(worker=worker)
        self.assertTrue(worker.consumed)
        with self.assertRaisesRegex(
            score_only.ScoreOnlyRefusal, "repeated_score_or_target_delivery"
        ):
            self._score(worker=worker)

    def test_missing_and_nonfinite_predictions_are_retained_as_failures(self) -> None:
        damaged = copy.deepcopy(self.predictions)
        damaged.pop(0)
        damaged[0]["probabilities"] = [math.nan, 0.0, 0.0, 1.0]
        result = self._score(predictions=damaged)
        quality = result["prediction_quality"]
        self.assertEqual(quality["missing_prediction_rows_retained"], 1)
        self.assertEqual(quality["invalid_prediction_rows_retained"], 1)
        self.assertEqual(quality["rows_dropped"], 0)
        assigned = sum(
            cohort["free_choice_shadow"]["assigned_active_episodes"]
            + cohort["prompted_shadow_directional"]["assigned_active_episodes"]
            for cohort in result["cohorts"]
        )
        self.assertEqual(assigned, 32)
        self.assertIn("maximum-loss zero-accuracy", " ".join(result["warnings"]))

    def test_aggregate_output_contains_no_private_rows(self) -> None:
        result = self._score()
        encoded = json.dumps(result, sort_keys=True, allow_nan=False)
        for forbidden in (
            '"item_id"',
            '"participant_id"',
            '"probabilities"',
            '"predicted_command_index"',
            '"target"',
            '"targets"',
        ):
            self.assertNotIn(forbidden, encoded)
        self.assertFalse(
            result["contains_individual_prediction_probability_target_or_participant_outcome"]
        )
        self.assertEqual(result["target_delivery_count"], 1)
        self.assertEqual(result["score_count"], 1)
        self.assertEqual(result["post_target_updates"], 0)

    def test_prompted_endpoint_cannot_rescue_failed_free_choice_live(self) -> None:
        weakened = copy.deepcopy(self.observations)
        for row in weakened:
            if row.get("endpoint") == "free_choice_intend":
                row.update(
                    {
                        "stable_commit": False,
                        "predicted_command_index": None,
                        "commit_count": 0,
                        "first_output_latency_seconds": None,
                        "stable_commit_latency_seconds": None,
                        "capture_to_presentation_overhead_seconds": None,
                    }
                )
        result = self._score(observations=weakened)
        live = result["replication_live"]
        self.assertFalse(live["free_choice_live"]["passes"])
        self.assertTrue(live["prompted_live"]["passes"])
        self.assertEqual(live["router"]["primary_endpoint"], "free_choice_intend")
        self.assertFalse(live["router"]["prompted_may_rescue_free_choice"])
        self.assertFalse(live["router"]["live_gate_pass"])


if __name__ == "__main__":
    unittest.main()
