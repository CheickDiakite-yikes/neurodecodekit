import json
import hashlib
import tempfile
import unittest
from pathlib import Path


try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:  # pragma: no cover
    NUMPY_AVAILABLE = False


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class SharedS21ValidationTests(unittest.TestCase):
    def test_prefix_and_control_transforms_are_deterministic_and_target_blind(self):
        from neurodecodekit.evaluation.shared_s21_validation import (
            apply_channel_derangement,
            apply_time_displacement,
            channel_derangement_indices,
            derange_train_targets,
            derange_validation_predictions,
            registered_prefix_order,
            timing_only_signals,
        )

        semantic = [f"semantic-{index}" for index in range(8)]
        performed = [f"performed-{index}" for index in range(8)]
        order = registered_prefix_order(semantic, performed)
        self.assertEqual(order, registered_prefix_order(semantic, performed))
        self.assertEqual(sorted(order), list(range(8)))

        channels = [f"M{index:03d}" for index in range(102)]
        mapping = channel_derangement_indices(channels)
        self.assertTrue(all(source != destination for destination, source in enumerate(mapping)))
        signals = np.arange(2 * 102 * 120, dtype="float32").reshape(2, 102, 120)
        deranged, returned_mapping = apply_channel_derangement(signals, channels)
        np.testing.assert_array_equal(deranged, signals[:, mapping, :])
        self.assertEqual(mapping, returned_mapping)

        delayed, report = apply_time_displacement(signals, [120, 110])
        self.assertTrue(np.all(delayed[:, :, :100] == 0))
        np.testing.assert_array_equal(delayed[0, :, 100:120], signals[0, :, :20])
        self.assertFalse(report["wrapping"])
        timing = timing_only_signals(signals, [120, 110])
        self.assertTrue(np.all(timing[:, 0, :110] == 1))
        self.assertTrue(np.all(timing[:, 2:, :] == 0))

        target_ids = np.arange(1, 9, dtype="int16")[:, None]
        lengths = np.ones(8, dtype="int32")
        texts = list("ABCDEFGH")
        moved_ids, moved_lengths, moved_texts, target_mapping = derange_train_targets(
            target_ids, lengths, texts, semantic
        )
        self.assertTrue(all(source != index for index, source in enumerate(target_mapping)))
        self.assertEqual(moved_ids.shape, target_ids.shape)
        self.assertEqual(moved_lengths.tolist(), lengths.tolist())
        self.assertEqual(moved_texts, [texts[index] for index in target_mapping])

        predictions, row_mapping = derange_validation_predictions(
            list("ABCDEF"), [f"item-{index}" for index in range(6)]
        )
        self.assertTrue(all(source != index for index, source in enumerate(row_mapping)))
        self.assertEqual(predictions, [list("ABCDEF")[index] for index in row_mapping])

    def test_freeze_requires_exact_inventory_and_contains_no_plaintext(self):
        from neurodecodekit.evaluation.shared_s21_validation import (
            build_prediction_freeze_record,
            expected_prediction_ids,
            validate_prediction_freeze_record,
        )

        rows = []
        for condition_id in expected_prediction_ids():
            rows.append(
                {
                    "condition_id": condition_id,
                    "configuration_sha256": "1" * 64,
                    "checkpoint_sha256_or_no_checkpoint_reason": "no_checkpoint",
                    "transform_sha256_or_identity": "identity",
                    "ordered_item_ids_sha256": "2" * 64,
                    "prediction_payload_sha256": "3" * 64,
                    "lengths_sha256": "4" * 64,
                    "runtime_sec": 0.01,
                    "peak_rss_bytes": 100,
                    "model_run_count": 1,
                    "warnings": [],
                    "private_payload_bytes": 10,
                    "private_payload_file_sha256": "5" * 64,
                }
            )
        record = build_prediction_freeze_record(
            contract_sha256="a" * 64,
            authorization_decision_sha256="b" * 64,
            implementation_commit="c" * 40,
            prediction_rows=rows,
            access_counters={"prediction_sets_frozen": 31},
            generated_artifact_bytes=1000,
            checkpoint_bytes=500,
            prediction_payload_bytes=310,
            parameter_update_runtime_sec=10,
            end_to_end_runtime_sec=12,
            peak_rss_bytes=1000,
            warnings=[],
        )
        validate_prediction_freeze_record(record)
        serialized = json.dumps(record)
        self.assertNotIn('"predictions"', serialized)
        self.assertNotIn('"targets"', serialized)
        broken = json.loads(serialized)
        broken["prediction_sets"].pop()
        with self.assertRaisesRegex(ValueError, "exactly 31"):
            validate_prediction_freeze_record(broken)

    def test_private_prediction_loader_binds_configuration_checkpoint_and_transform(self):
        from neurodecodekit.evaluation.shared_s21_validation import (
            load_prediction_payload,
            write_prediction_payload,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prediction.json"
            freeze_row = write_prediction_payload(
                path,
                condition_id="L31-E02",
                item_ids=[f"item-{index}" for index in range(6)],
                predictions=list("ABCDEF"),
                input_lengths=[10, 11, 12, 13, 14, 15],
                configuration={"model": "registered"},
                checkpoint_sha256_or_reason="checkpoint-identity",
                transform={"name": "exact_zero_valid_signal"},
                runtime_sec=0.1,
                peak_rss_bytes=100,
                model_run_count=1,
                blank_fraction=0.5,
                warnings=[],
            )
            self.assertEqual(load_prediction_payload(path, freeze_row)["condition_id"], "L31-E02")

            original = json.loads(path.read_text(encoding="utf-8"))
            for field, changed, expected_error in (
                ("configuration", {"model": "changed"}, "configuration"),
                ("checkpoint_sha256_or_reason", "changed", "checkpoint"),
                ("transform", {"name": "changed"}, "transform"),
            ):
                tampered = dict(original)
                tampered[field] = changed
                path.write_text(json.dumps(tampered, sort_keys=True), encoding="utf-8")
                bound = dict(freeze_row)
                bound["private_payload_file_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                with self.assertRaisesRegex(ValueError, expected_error):
                    load_prediction_payload(path, bound)

    def test_exact_scoring_and_bounded_scaling_gate_can_pass(self):
        from neurodecodekit.evaluation.shared_s21_validation import (
            ADDITIONAL_CONTROL_IDS,
            PREFIX_SIZES,
            SEEDS,
            candidate_prediction_id,
            expected_prediction_ids,
            prior_prediction_id,
            score_shared_validation,
        )

        targets = list("ABCDEF")
        ids = [f"item-{index}" for index in range(6)]
        payloads = {}
        correct_counts = {8: 0, 16: 0, 24: 2, 32: 3, 44: 5, 55: 6}
        for size in PREFIX_SIZES:
            count = correct_counts[size]
            predictions = targets[:count] + ["Z"] * (6 - count)
            for seed in SEEDS:
                payloads[candidate_prediction_id(size, seed)] = {
                    "item_ids": ids,
                    "predictions": predictions,
                    "blank_fraction": 0.2,
                }
            payloads[prior_prediction_id(size)] = {
                "item_ids": ids,
                "predictions": ["Z"] * 6,
                "blank_fraction": None,
            }
        for condition_id in ADDITIONAL_CONTROL_IDS:
            payloads[condition_id] = {
                "item_ids": ids,
                "predictions": ["Z"] * 6,
                "blank_fraction": 0.9,
            }
        self.assertEqual(set(payloads), set(expected_prediction_ids()))
        report = score_shared_validation(
            prediction_payloads=payloads,
            target_item_ids=ids,
            targets=targets,
        )
        self.assertEqual(report["status"], "passed")
        self.assertTrue(report["intersection_union_gate_passed"])
        primary = report["exact_comparisons"]["L31-E01"]
        self.assertEqual(primary["wins"], 6)
        self.assertEqual(primary["one_sided_greater_p"], 1 / 64)
        self.assertEqual(len(primary["null_statistics_binary_order"]), 64)
        self.assertTrue(report["scaling_gate"]["passed"])
        serialized = json.dumps(report)
        for target in targets:
            self.assertNotIn(f'"{target}"', serialized)

    def test_scorer_fails_closed_on_missing_condition(self):
        from neurodecodekit.evaluation.shared_s21_validation import score_shared_validation

        with self.assertRaisesRegex(ValueError, "all 31"):
            score_shared_validation(
                prediction_payloads={},
                target_item_ids=[f"item-{index}" for index in range(6)],
                targets=list("ABCDEF"),
            )


if __name__ == "__main__":
    unittest.main()
