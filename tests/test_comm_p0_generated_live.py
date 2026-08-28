from __future__ import annotations

import json
import unittest
from dataclasses import replace
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_live as live
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical

ROOT = Path(__file__).resolve().parents[1]


class CommP0GeneratedLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = core.load_contract(ROOT)
        vault = core.GeneratedTargetVault(b"live-scorer-generated-secret-0001")
        cls.trials = core.generate_trial_plan(cls.contract, vault)
        cls.live_trials = tuple(
            row
            for row in cls.trials
            if row.cohort_id == live.LIVE_COHORT
            and row.phase == live.LIVE_PHASE
            and row.endpoint in core.ENDPOINTS
        )
        cls.targets = {
            row.item_id: numerical._fixture_command(row) for row in cls.live_trials
        }
        cls.predictions = cls._predictions()
        cls.freeze = core.build_prediction_freeze(
            (row.public_record() for row in cls.predictions),
            expected_rows=len(cls.predictions),
            expected_sets=21 * len(cls.contract["conditions"]) * len(core.ENDPOINTS),
        )
        cls.observations = cls._observations()
        cls.authorization = live.GeneratedLiveScoreAuthorization(
            prediction_freeze_green=True,
            target_delivery_count=1,
            prior_score_count=0,
        )

    @classmethod
    def _probabilities(
        cls, truth: int, condition: str, endpoint: str
    ) -> tuple[float, float, float, float]:
        if condition == "P_plus_residual_central_EEG":
            correct = 0.85
        elif condition == "cue_only" and endpoint == "prompted_intend":
            correct = 0.95
        else:
            wrong = (truth + 1) % 4
            return tuple(
                0.35 if index == truth else 0.45 if index == wrong else 0.10
                for index in range(4)
            )  # type: ignore[return-value]
        remainder = (1.0 - correct) / 3.0
        return tuple(correct if index == truth else remainder for index in range(4))  # type: ignore[return-value]

    @classmethod
    def _predictions(cls) -> tuple[numerical.CompactPrediction, ...]:
        rows = []
        for trial in cls.live_trials:
            truth = cls.targets[trial.item_id]
            for condition in cls.contract["conditions"]:
                rows.append(
                    numerical.CompactPrediction(
                        item_id=trial.item_id,
                        cohort_id=trial.cohort_id,
                        participant_id=trial.participant_id,
                        endpoint=str(trial.endpoint),
                        phase=trial.phase,
                        condition=condition,
                        probabilities=cls._probabilities(
                            truth, condition, str(trial.endpoint)
                        ),
                    )
                )
        return tuple(rows)

    @classmethod
    def _observations(cls) -> tuple[live.GeneratedLiveObservation, ...]:
        rows = []
        participants = sorted({trial.participant_id for trial in cls.live_trials})
        for trial in cls.live_trials:
            rows.append(
                live.GeneratedLiveObservation(
                    interval_id=trial.item_id,
                    cohort_id=trial.cohort_id,
                    participant_id=trial.participant_id,
                    endpoint=trial.endpoint,
                    phase=trial.phase,
                    active_intent=True,
                    inactive_surface=None,
                    duration_seconds=3.0,
                    stable_commit=True,
                    predicted_command_index=cls.targets[trial.item_id],
                    commit_count=1,
                    invalid_chunk_count=0,
                    total_chunk_count=10,
                    processed_frame_count=100,
                    total_frame_count=100,
                    first_output_latency_seconds=0.4,
                    stable_commit_latency_seconds=1.5,
                    capture_to_presentation_overhead_seconds=0.1,
                    clock_map_verified=True,
                )
            )
        for participant_id in participants:
            for surface in sorted(live.INACTIVE_SURFACES):
                rows.append(
                    live.GeneratedLiveObservation(
                        interval_id=f"{participant_id}-inactive-{surface}",
                        cohort_id=live.LIVE_COHORT,
                        participant_id=participant_id,
                        endpoint=None,
                        phase=live.LIVE_PHASE,
                        active_intent=False,
                        inactive_surface=surface,
                        duration_seconds=120.0,
                        stable_commit=False,
                        predicted_command_index=None,
                        commit_count=0,
                        invalid_chunk_count=0,
                        total_chunk_count=10,
                        processed_frame_count=100,
                        total_frame_count=100,
                        first_output_latency_seconds=None,
                        stable_commit_latency_seconds=None,
                        capture_to_presentation_overhead_seconds=None,
                        clock_map_verified=True,
                    )
                )
        return tuple(rows)

    def _score(
        self,
        *,
        observations: tuple[live.GeneratedLiveObservation, ...] | None = None,
        targets: dict[str, int] | None = None,
        authorization: live.GeneratedLiveScoreAuthorization | None = None,
    ) -> dict[str, object]:
        return live.score_generated_replication_live(
            self.predictions,
            self.trials,
            observations or self.observations,
            targets or self.targets,
            self.freeze,
            authorization or self.authorization,
            self.contract,
        )

    def test_live_score_is_split_aggregate_only_and_target_free(self) -> None:
        result = self._score()
        self.assertTrue(result["free_choice_live"]["passes"])
        self.assertTrue(result["prompted_live"]["passes"])
        self.assertTrue(result["router"]["live_gate_pass"])
        self.assertEqual(result["score_count"], 1)
        self.assertEqual(result["target_delivery_count"], 1)
        self.assertFalse(result["claim_boundary"]["end_to_end_latency_measured"])
        self.assertFalse(result["claim_boundary"]["scientific_claim_established"])
        core.assert_target_free(result)
        encoded = json.dumps(result, sort_keys=True)
        self.assertEqual(encoded.count('"inactive_null_metrics"'), 1)
        self.assertNotIn("participant_id", encoded)
        self.assertNotIn("item_id", encoded)
        self.assertNotIn("probabilities", encoded)

    def test_prompted_success_cannot_rescue_free_choice_failure(self) -> None:
        free_choice_ids = {
            trial.item_id
            for trial in self.live_trials
            if trial.endpoint == "free_choice_intend"
        }
        weakened = []
        for row in self.observations:
            if row.interval_id in free_choice_ids:
                weakened.append(
                    replace(
                        row,
                        stable_commit=False,
                        predicted_command_index=None,
                        commit_count=0,
                        first_output_latency_seconds=None,
                        stable_commit_latency_seconds=None,
                        capture_to_presentation_overhead_seconds=None,
                    )
                )
            else:
                weakened.append(row)
        result = self._score(observations=tuple(weakened))
        self.assertFalse(result["free_choice_live"]["passes"])
        self.assertTrue(result["prompted_live"]["passes"])
        self.assertFalse(result["router"]["live_gate_pass"])
        self.assertFalse(result["router"]["prompted_may_rescue_free_choice"])

    def test_inactive_interval_cannot_be_counted_twice(self) -> None:
        duplicated = self.observations + (self.observations[-1],)
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "false_commit_or_chatter_rate_above_maximum",
        ):
            self._score(observations=duplicated)

    def test_target_delivery_requires_exact_green_one_shot_order(self) -> None:
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "score_before_exact_green_freeze",
        ):
            self._score(
                authorization=live.GeneratedLiveScoreAuthorization(False, 1, 0)
            )
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "repeated_score_or_target_delivery",
        ):
            self._score(
                authorization=live.GeneratedLiveScoreAuthorization(True, 1, 1)
            )

    def test_target_inventory_must_match_live_active_manifest_exactly(self) -> None:
        missing = dict(self.targets)
        missing.pop(next(iter(missing)))
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "scorer_prediction_target_row_mismatch",
        ):
            self._score(targets=missing)


if __name__ == "__main__":
    unittest.main()
