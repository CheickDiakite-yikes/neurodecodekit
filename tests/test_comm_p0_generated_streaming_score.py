from __future__ import annotations

import copy
import unittest

from test_comm_p0_generated_score_worker import _fixture

from neurodecodekit.experiments import comm_p0_generated_score_only as score_only
from neurodecodekit.experiments import comm_p0_generated_streaming_score as streaming


class CommP0GeneratedStreamingScoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract, self.trials, self.predictions, self.observations, self.targets = _fixture()
        self.authorization = {
            "prediction_freeze_green": True,
            "replication_artifact_freeze_green": True,
            "one_shot": True,
            "target_delivery_count": 1,
            "prior_score_count": 0,
        }

    def _stream_score(self, predictions: list[dict[str, object]]) -> dict[str, object]:
        freeze = streaming.build_prediction_freeze_attestation(iter(predictions), self.contract)
        return streaming.score_records(
            contract=self.contract,
            trial_records=self.trials,
            prediction_pass_factory=lambda: iter(predictions),
            live_observation_records=self.observations,
            freeze_attestation=freeze,
            authorization=self.authorization,
            delivered_targets=self.targets,
        )

    def test_streaming_result_exactly_matches_existing_score(self) -> None:
        freeze = score_only.build_prediction_freeze_attestation(self.predictions, self.contract)
        expected = score_only.score_records(
            contract=self.contract,
            trial_records=self.trials,
            prediction_records=self.predictions,
            live_observation_records=self.observations,
            freeze_attestation=freeze,
            authorization=self.authorization,
            delivered_targets=self.targets,
        )
        self.assertEqual(self._stream_score(self.predictions), expected)

    def test_missing_and_invalid_rows_preserve_existing_penalties(self) -> None:
        changed = copy.deepcopy(self.predictions)
        changed.pop(3)
        changed[5]["probabilities"] = [float("nan"), 0.0, 0.0, 0.0]
        freeze = score_only.build_prediction_freeze_attestation(changed, self.contract)
        expected = score_only.score_records(
            contract=self.contract,
            trial_records=self.trials,
            prediction_records=changed,
            live_observation_records=self.observations,
            freeze_attestation=freeze,
            authorization=self.authorization,
            delivered_targets=self.targets,
        )
        self.assertEqual(self._stream_score(changed), expected)

    def test_second_pass_mutation_refuses_after_freeze(self) -> None:
        calls = 0

        def passes():
            nonlocal calls
            calls += 1
            records = copy.deepcopy(self.predictions)
            if calls == 2:
                records[0]["probabilities"] = [0.25, 0.25, 0.25, 0.25]
            return iter(records)

        freeze = streaming.build_prediction_freeze_attestation(
            iter(self.predictions), self.contract
        )
        with self.assertRaisesRegex(
            score_only.ScoreOnlyRefusal, "prediction_row_or_probability_tamper"
        ):
            streaming.score_records(
                contract=self.contract,
                trial_records=self.trials,
                prediction_pass_factory=passes,
                live_observation_records=self.observations,
                freeze_attestation=freeze,
                authorization=self.authorization,
                delivered_targets=self.targets,
            )

    def test_duplicate_and_metadata_mismatch_refuse(self) -> None:
        duplicated = copy.deepcopy(self.predictions)
        duplicated.append(copy.deepcopy(duplicated[0]))
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "prediction_inventory"):
            self._stream_score(duplicated)

        mismatched = copy.deepcopy(self.predictions)
        mismatched[0]["participant_id"] = "wrong"
        with self.assertRaisesRegex(score_only.ScoreOnlyRefusal, "prediction_inventory"):
            self._stream_score(mismatched)

    def test_capability_audit_binds_one_row_buffer_and_two_passes(self) -> None:
        audit = streaming.capability_audit()
        self.assertEqual(audit["prediction_passes"], 2)
        self.assertEqual(audit["maximum_prediction_rows_buffered"], 1)
        self.assertFalse(audit["complete_prediction_records_materialized"])
        self.assertFalse(audit["fit_or_model_capability"])
        self.assertFalse(audit["file_read_or_write_capability"])


if __name__ == "__main__":
    unittest.main()
