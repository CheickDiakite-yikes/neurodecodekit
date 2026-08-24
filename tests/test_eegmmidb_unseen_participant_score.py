import copy
import hashlib
import json
import unittest

from neurodecodekit.evaluation import eegmmidb_unseen_participant_score as ug1


def _rows(*, imagery_passes=True):
    targets = []
    predictions = []
    controls = set(ug1.CONDITION_IDS) - {"primary_whole_head"}
    for task, run in ug1.TASK_RUNS.items():
        for participant_index, participant in enumerate(ug1.PARTICIPANTS):
            for ordinal in range(15):
                target = "T1" if ordinal % 2 == 0 else "T2"
                opaque = f"{task}-{participant}-{ordinal:02d}"
                cue_sample = 640 + ordinal * 320
                targets.append(
                    {
                        "schema_version": ug1.SCHEMA_VERSION,
                        "opaque_row_id": opaque,
                        "task": task,
                        "participant": participant,
                        "run": run,
                        "event_ordinal": ordinal,
                        "cue_sample": cue_sample,
                        "target": target,
                    }
                )
                for condition in ug1.CONDITION_IDS:
                    if condition in controls:
                        prediction = "T1"
                    elif task == "imagery" and not imagery_passes:
                        prediction = "T1"
                    else:
                        prediction = target
                    predictions.append(
                        {
                            "schema_version": ug1.SCHEMA_VERSION,
                            "opaque_row_id": opaque,
                            "task": task,
                            "participant": participant,
                            "run": run,
                            "event_ordinal": ordinal,
                            "cue_sample": cue_sample,
                            "condition": condition,
                            "prediction": prediction,
                        }
                    )
    targets.sort(
        key=lambda row: (row["task"], row["participant"], row["run"], row["event_ordinal"])
    )
    predictions.sort(
        key=lambda row: (
            row["task"],
            row["participant"],
            row["run"],
            row["event_ordinal"],
            row["condition"],
        )
    )
    return predictions, targets


def _fixture(*, imagery_passes=True):
    predictions, targets = _rows(imagery_passes=imagery_passes)
    prediction_payload = ug1.canonical_prediction_jsonl(predictions)
    target_payload = ug1.canonical_target_jsonl(targets)
    bindings = ug1.FreezeBindings(
        checkpoint_hashes={"execution_primary": "a" * 64, "imagery_primary": "b" * 64},
        configuration_hash="c" * 64,
        code_hash="d" * 64,
        sealed_target_payload_sha256=hashlib.sha256(target_payload).hexdigest(),
    )
    freeze = ug1.build_prediction_freeze(prediction_payload, bindings=bindings)
    return prediction_payload, target_payload, bindings, freeze


class UG1MetricTests(unittest.TestCase):
    def test_every_gate_threshold_has_inclusive_pass_and_first_fail_side(self):
        self.assertEqual(
            ug1.qualify_gate_threshold_boundaries(),
            {"inclusive_pass_cases": 2, "exclusive_fail_cases": 22},
        )

    def test_balanced_accuracy_is_exact_for_imbalanced_rows(self):
        self.assertEqual(
            ug1.balanced_accuracy(
                ["T1", "T1", "T1", "T2"],
                ["T1", "T1", "T2", "T2"],
            ),
            (2 / 3 + 1) / 2,
        )
        with self.assertRaises(ug1.UG1ScoreRefusal):
            ug1.balanced_accuracy(["T1"], ["T1"])

    def test_exact_sign_flip_enumerates_32768_and_retains_ties(self):
        self.assertEqual(ug1.exact_sign_flip_p([0.0] * 15), 1.0)
        self.assertEqual(ug1.exact_sign_flip_p([0.25] * 15), 1 / 32768)
        with self.assertRaises(ug1.UG1ScoreRefusal):
            ug1.exact_sign_flip_p([0.1] * 14)

    def test_router_orders_r0_through_r4(self):
        base = {
            "integrity_passed": True,
            "source_loso_execution_passed": True,
            "final_score_available": True,
            "execution_passed": True,
            "imagery_passed": True,
        }
        cases = (
            ({"integrity_passed": False}, "EEGMMIDBUG1-R0"),
            ({"source_loso_execution_passed": False}, "EEGMMIDBUG1-R1"),
            ({"final_score_available": False}, "EEGMMIDBUG1-R0"),
            ({"execution_passed": False}, "EEGMMIDBUG1-R2"),
            ({"imagery_passed": False}, "EEGMMIDBUG1-R3"),
            ({}, "EEGMMIDBUG1-R4"),
        )
        for changes, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(ug1.route_ug1(**(base | changes)), expected)


class UG1FreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prediction_payload, cls.target_payload, cls.bindings, cls.freeze = _fixture()

    def test_freeze_is_aggregate_canonical_and_replays(self):
        replay = ug1.build_prediction_freeze(self.prediction_payload, bindings=self.bindings)
        self.assertEqual(replay, self.freeze)
        self.assertEqual(self.freeze["private_prediction_rows"], 5_400)
        self.assertEqual(
            self.freeze["task_condition_counts"]["execution"]["primary_whole_head"],
            225,
        )
        encoded = json.dumps(self.freeze, sort_keys=True, separators=(",", ":"))
        self.assertNotIn('"participant"', encoded)
        self.assertNotIn('"prediction"', encoded)
        self.assertNotIn('"target"', encoded)

    def test_prediction_schema_forbids_target_leakage_and_free_form_fields(self):
        predictions, _targets = _rows()
        predictions[0]["target"] = "T1"
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "prediction row fields differ"):
            ug1.canonical_prediction_jsonl(predictions)
        predictions, _targets = _rows()
        predictions[0]["probability"] = 0.9
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "prediction row fields differ"):
            ug1.canonical_prediction_jsonl(predictions)

    def test_prediction_mutation_order_and_hash_refuse(self):
        mutated = bytearray(self.prediction_payload)
        offset = self.prediction_payload.index(b'"prediction":"T1"') + len(b'"prediction":"T')
        mutated[offset] = ord("2")
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "payload hash differs"):
            ug1.validate_prediction_freeze(self.freeze, bytes(mutated), bindings=self.bindings)

        lines = self.prediction_payload.splitlines(keepends=True)
        reordered = b"".join([lines[1], lines[0], *lines[2:]])
        rebound = ug1.build_prediction_freeze
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "canonically ordered"):
            rebound(reordered, bindings=self.bindings)

    def test_freeze_and_external_binding_mutations_refuse(self):
        mutated = copy.deepcopy(self.freeze)
        mutated["code_hash"] = "e" * 64
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "freeze record hash differs"):
            ug1.validate_prediction_freeze(mutated, self.prediction_payload, bindings=self.bindings)
        rebound = ug1.FreezeBindings(
            checkpoint_hashes=self.bindings.checkpoint_hashes,
            configuration_hash="e" * 64,
            code_hash=self.bindings.code_hash,
            sealed_target_payload_sha256=self.bindings.sealed_target_payload_sha256,
        )
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "configuration_hash differs"):
            ug1.validate_prediction_freeze(self.freeze, self.prediction_payload, bindings=rebound)

    def test_noncanonical_json_and_duplicate_key_refuse(self):
        rows, _targets = _rows()
        row = rows[0]
        noncanonical = json.dumps(row).encode() + b"\n"
        with self.assertRaises(ug1.UG1ScoreRefusal):
            ug1.build_prediction_freeze(noncanonical, bindings=self.bindings)
        duplicate = b'{"schema_version":"0.1.0","schema_version":"0.1.0"}\n'
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "duplicate JSON key"):
            ug1.build_prediction_freeze(duplicate, bindings=self.bindings)


class UG1ScorerTests(unittest.TestCase):
    def test_source_failure_routes_r1_without_loading_targets(self):
        prediction_payload, _target_payload, bindings, freeze = _fixture()
        calls = 0

        def forbidden_loader():
            nonlocal calls
            calls += 1
            raise AssertionError("target loader must stay closed")

        result = ug1.score_frozen_predictions(
            freeze=freeze,
            prediction_payload=prediction_payload,
            bindings=bindings,
            checkpoint_verifier=lambda: dict(bindings.checkpoint_hashes),
            sealed_target_loader=forbidden_loader,
            source_loso_execution_passed=False,
        )
        self.assertEqual(result["route"], "EEGMMIDBUG1-R1")
        self.assertEqual(calls, 0)
        self.assertEqual(result["scoring_events"], 0)

    def test_pre_target_prediction_failure_does_not_load_targets(self):
        prediction_payload, target_payload, bindings, freeze = _fixture()
        freeze = copy.deepcopy(freeze)
        freeze["prediction_set_hash"] = "0" * 64
        calls = 0

        def loader():
            nonlocal calls
            calls += 1
            return target_payload

        with self.assertRaises(ug1.UG1ScoreRefusal):
            ug1.score_frozen_predictions(
                freeze=freeze,
                prediction_payload=prediction_payload,
                bindings=bindings,
                checkpoint_verifier=lambda: dict(bindings.checkpoint_hashes),
                sealed_target_loader=loader,
                source_loso_execution_passed=True,
            )
        self.assertEqual(calls, 0)

    def test_checkpoint_mutation_refuses_before_target_delivery(self):
        prediction_payload, target_payload, bindings, freeze = _fixture()
        calls = 0

        def loader():
            nonlocal calls
            calls += 1
            return target_payload

        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "checkpoint hashes changed"):
            ug1.score_frozen_predictions(
                freeze=freeze,
                prediction_payload=prediction_payload,
                bindings=bindings,
                checkpoint_verifier=lambda: {"mutated": "0" * 64},
                sealed_target_loader=loader,
                source_loso_execution_passed=True,
            )
        self.assertEqual(calls, 0)

    def test_target_mutation_refuses_before_json_parse(self):
        prediction_payload, target_payload, bindings, freeze = _fixture()
        mutated = b"not-json\n" + target_payload
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "target payload hash differs"):
            ug1.score_frozen_predictions(
                freeze=freeze,
                prediction_payload=prediction_payload,
                bindings=bindings,
                checkpoint_verifier=lambda: dict(bindings.checkpoint_hashes),
                sealed_target_loader=lambda: mutated,
                source_loso_execution_passed=True,
            )

    def test_exact_r4_aggregate_score_has_no_participant_outcomes(self):
        prediction_payload, target_payload, bindings, freeze = _fixture()
        result = ug1.score_frozen_predictions(
            freeze=freeze,
            prediction_payload=prediction_payload,
            bindings=bindings,
            checkpoint_verifier=lambda: dict(bindings.checkpoint_hashes),
            sealed_target_loader=lambda: target_payload,
            source_loso_execution_passed=True,
        )
        self.assertEqual(result["route"], "EEGMMIDBUG1-R4")
        self.assertEqual(result["execution"]["primary_metrics"]["event_count"], 225)
        self.assertEqual(
            result["execution"]["primary_metrics"]["participant_macro_balanced_accuracy"],
            1.0,
        )
        self.assertEqual(result["execution"]["primary_metrics"]["pooled_balanced_accuracy"], 1.0)
        self.assertEqual(result["sealed_target_loads"], 1)
        encoded = json.dumps(result, sort_keys=True)
        for participant in ug1.PARTICIPANTS:
            self.assertNotIn(participant, encoded)

    def test_imagery_cannot_rescue_or_downgrade_execution_r3(self):
        prediction_payload, target_payload, bindings, freeze = _fixture(imagery_passes=False)
        result = ug1.score_frozen_predictions(
            freeze=freeze,
            prediction_payload=prediction_payload,
            bindings=bindings,
            checkpoint_verifier=lambda: dict(bindings.checkpoint_hashes),
            sealed_target_loader=lambda: target_payload,
            source_loso_execution_passed=True,
        )
        self.assertTrue(result["execution"]["passed"])
        self.assertFalse(result["imagery"]["passed"])
        self.assertEqual(result["route"], "EEGMMIDBUG1-R3")

    def test_execution_failure_routes_r2_even_when_imagery_passes(self):
        predictions, targets = _rows()
        for row in predictions:
            if row["task"] == "execution" and row["condition"] == "primary_whole_head":
                row["prediction"] = "T1"
        prediction_payload = ug1.canonical_prediction_jsonl(predictions)
        target_payload = ug1.canonical_target_jsonl(targets)
        bindings = ug1.FreezeBindings(
            checkpoint_hashes={"only": "a" * 64},
            configuration_hash="b" * 64,
            code_hash="c" * 64,
            sealed_target_payload_sha256=hashlib.sha256(target_payload).hexdigest(),
        )
        freeze = ug1.build_prediction_freeze(prediction_payload, bindings=bindings)
        result = ug1.score_frozen_predictions(
            freeze=freeze,
            prediction_payload=prediction_payload,
            bindings=bindings,
            checkpoint_verifier=lambda: dict(bindings.checkpoint_hashes),
            sealed_target_loader=lambda: target_payload,
            source_loso_execution_passed=True,
        )
        self.assertFalse(result["execution"]["passed"])
        self.assertTrue(result["imagery"]["passed"])
        self.assertEqual(result["route"], "EEGMMIDBUG1-R2")

    def test_target_identity_and_order_mutations_refuse(self):
        prediction_payload, _target_payload, bindings, freeze = _fixture()
        _predictions, targets = _rows()
        targets[0]["cue_sample"] += 1
        mutated_target = ug1.canonical_target_jsonl(targets)
        rebound = ug1.FreezeBindings(
            checkpoint_hashes=bindings.checkpoint_hashes,
            configuration_hash=bindings.configuration_hash,
            code_hash=bindings.code_hash,
            sealed_target_payload_sha256=hashlib.sha256(mutated_target).hexdigest(),
        )
        rebound_freeze = ug1.build_prediction_freeze(prediction_payload, bindings=rebound)
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "identities differ"):
            ug1.score_frozen_predictions(
                freeze=rebound_freeze,
                prediction_payload=prediction_payload,
                bindings=rebound,
                checkpoint_verifier=lambda: dict(rebound.checkpoint_hashes),
                sealed_target_loader=lambda: mutated_target,
                source_loso_execution_passed=True,
            )

        ordered_payload = ug1.canonical_target_jsonl(_rows()[1])
        lines = ordered_payload.splitlines(keepends=True)
        reordered_target = b"".join([lines[1], lines[0], *lines[2:]])
        order_bindings = ug1.FreezeBindings(
            checkpoint_hashes=bindings.checkpoint_hashes,
            configuration_hash=bindings.configuration_hash,
            code_hash=bindings.code_hash,
            sealed_target_payload_sha256=hashlib.sha256(reordered_target).hexdigest(),
        )
        order_freeze = ug1.build_prediction_freeze(prediction_payload, bindings=order_bindings)
        with self.assertRaisesRegex(ug1.UG1ScoreRefusal, "canonically ordered"):
            ug1.score_frozen_predictions(
                freeze=order_freeze,
                prediction_payload=prediction_payload,
                bindings=order_bindings,
                checkpoint_verifier=lambda: dict(order_bindings.checkpoint_hashes),
                sealed_target_loader=lambda: reordered_target,
                source_loso_execution_passed=True,
            )


if __name__ == "__main__":
    unittest.main()
