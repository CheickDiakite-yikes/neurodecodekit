import copy
import tempfile
import unittest
from pathlib import Path


try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:  # pragma: no cover
    NUMPY_AVAILABLE = False


from neurodecodekit.evaluation.train_only_failure_discrimination import (
    FIT_PREFIX_SIZES,
    SEEDS,
    apply_channel_derangement,
    apply_nonwrapping_shift,
    build_prediction_freeze_record,
    candidate_condition_id,
    derange_check_predictions,
    diagnostic_split,
    expected_fit_ids,
    expected_prediction_ids,
    fine_shift_condition_id,
    linear_condition_id,
    load_prediction_payload,
    prior_condition_id,
    score_failure_discrimination,
    sha256_json,
    timing_only_signals,
    validate_prediction_freeze_record,
    write_prediction_payload,
)


def _membership_rows():
    return [
        {
            "source_row_index": index,
            "row_uid_sha256": f"row-{index:02d}",
            "semantic_row_uid_sha256": f"semantic-{index:02d}",
        }
        for index in range(55)
    ]


def _prediction_rows():
    item_hash = sha256_json([f"item-{index}" for index in range(11)])
    return [
        {
            "condition_id": condition_id,
            "configuration_sha256": "a" * 64,
            "checkpoint_sha256_or_no_checkpoint_reason": "b" * 64,
            "transform_sha256_or_identity": "identity",
            "ordered_check_item_ids_sha256": item_hash,
            "prediction_payload_sha256": "d" * 64,
            "lengths_sha256": "e" * 64,
            "runtime_sec": 0.01,
            "peak_rss_bytes": 1024,
            "model_run_count": (
                0
                if condition_id.startswith("prior_") or condition_id == "check_row_derangement"
                else 1
            ),
            "warnings": [],
        }
        for condition_id in expected_prediction_ids()
    ]


def _fit_rows():
    rows = []
    for condition_id in expected_fit_ids():
        seed = next((seed for seed in SEEDS if condition_id.endswith(str(seed))), 4801)
        prefix = next(
            (size for size in FIT_PREFIX_SIZES if f"size{size}_" in condition_id),
            44,
        )
        rows.append(
            {
                "condition_id": condition_id,
                "seed": seed,
                "prefix_size": prefix,
                "configuration_sha256": "f" * 64,
                "checkpoint_sha256": "1" * 64,
                "telemetry_sha256": "2" * 64,
                "optimizer_steps": 240,
                "runtime_sec": 0.1,
                "peak_rss_bytes": 2048,
                "warnings": [],
                "telemetry_finite": True,
                "fit_cer_gain_over_prior": 0.1,
                "fit_blank_fraction": 0.2,
            }
        )
    return rows


def _counters():
    return {
        "source_cache_stat_reads": 1,
        "source_cache_hash_passes": 1,
        "split_report_metadata_reads": 1,
        "archive_header_reads": 14,
        "archive_row_member_streams": 7,
        "fit_signal_rows_delivered": 44,
        "fit_target_rows_delivered": 44,
        "check_signal_rows_delivered": 11,
        "candidate_training_runs": 15,
        "linear_training_runs": 3,
        "control_training_runs": 2,
        "optimizer_steps": 4800,
        "checkpoint_writes": 20,
        "checkpoint_reads": 0,
        "target_blind_model_inference_runs": 35,
        "no_signal_prior_fits": 5,
        "prediction_sets_frozen": 41,
        "check_target_rows_delivered_before_green_freeze": 0,
        "check_target_rows_delivered_after_green_freeze": 0,
        "check_scoring_runs": 0,
        "validation_signal_rows_delivered": 0,
        "validation_target_rows_delivered": 0,
        "source_test_signal_rows_delivered": 0,
        "source_test_target_rows_delivered": 0,
        "session2_rows_delivered": 0,
        "raw_fif_or_mat_reads": 0,
        "network_calls": 0,
        "new_download_bytes": 0,
        "language_model_or_neurotoken_runs": 0,
        "rw3_stream_device_or_hardware_operations": 0,
        "post_check_parameter_updates": 0,
        "post_check_configuration_changes": 0,
        "reruns": 0,
    }


def _freeze():
    return build_prediction_freeze_record(
        contract_sha256="3" * 64,
        authorization_decision_sha256="4" * 64,
        implementation_commit="5" * 40,
        prediction_rows=_prediction_rows(),
        fit_rows=_fit_rows(),
        static_audit={"infeasible_row_count": 0, "gross_defect": False},
        access_counters=_counters(),
        resources={
            "generated_artifact_bytes_before_freeze": 4096,
            "checkpoint_bytes": 1024,
            "prediction_payload_bytes": 2048,
            "working_array_bytes_upper_bound": 8192,
            "parameter_update_runtime_sec": 1.0,
            "cumulative_execution_runtime_sec": 2.0,
            "peak_rss_bytes": 16384,
            "producer_is_causal": True,
            "upstream_cache_is_causal": False,
            "end_to_end_latency_measured": False,
        },
        environment={"cpu_threads": 1},
        warnings=["synthetic_test_only"],
    )


class TrainOnlyFailureDiscriminationTests(unittest.TestCase):
    def test_inventory_is_exact_and_named(self):
        self.assertEqual(len(expected_fit_ids()), 20)
        self.assertEqual(len(set(expected_fit_ids())), 20)
        self.assertEqual(len(expected_prediction_ids()), 41)
        self.assertEqual(len(set(expected_prediction_ids())), 41)
        self.assertIn(candidate_condition_id(44, 4801), expected_prediction_ids())
        self.assertIn(prior_condition_id(44), expected_prediction_ids())
        self.assertIn(linear_condition_id(4803), expected_prediction_ids())
        self.assertIn(fine_shift_condition_id(-50, 4802), expected_prediction_ids())

    def test_diagnostic_split_is_deterministic_target_independent_and_strict(self):
        rows = _membership_rows()
        forward = diagnostic_split(rows)
        reverse = diagnostic_split(list(reversed(rows)))
        self.assertEqual(forward, reverse)
        self.assertEqual((forward["fit_rows"], forward["check_rows"]), (44, 11))
        self.assertTrue(
            set(forward["fit_source_row_indices"]).isdisjoint(forward["check_source_row_indices"])
        )
        with self.assertRaisesRegex(ValueError, "semantic IDs must be unique"):
            duplicate = copy.deepcopy(rows)
            duplicate[-1]["semantic_row_uid_sha256"] = duplicate[0]["semantic_row_uid_sha256"]
            diagnostic_split(duplicate)
        leaked = copy.deepcopy(rows)
        for row in leaked:
            row["target_text"] = "MUST NOT AFFECT ORDER"
        self.assertEqual(
            diagnostic_split(leaked)["assignment_sha256"],
            forward["assignment_sha256"],
        )

    def test_freeze_rejects_plaintext_malformed_inventory_and_target_access(self):
        freeze = _freeze()
        validate_prediction_freeze_record(freeze)
        leaked = copy.deepcopy(freeze)
        leaked["prediction_sets"][0]["predictions"] = ["SECRET"]
        with self.assertRaisesRegex(ValueError, "plaintext"):
            validate_prediction_freeze_record(leaked)
        missing = copy.deepcopy(freeze)
        missing["prediction_sets"].pop()
        with self.assertRaisesRegex(ValueError, "41"):
            validate_prediction_freeze_record(missing)
        target_access = copy.deepcopy(freeze)
        target_access["access_counters"]["check_target_rows_delivered_before_green_freeze"] = 11
        with self.assertRaisesRegex(ValueError, "counters mismatch"):
            validate_prediction_freeze_record(target_access)
        over_cap = copy.deepcopy(freeze)
        over_cap["resources"]["prediction_payload_bytes"] = 4 * 1024 * 1024 + 1
        with self.assertRaisesRegex(ValueError, "resources exceed caps"):
            validate_prediction_freeze_record(over_cap)

    def test_prediction_payload_roundtrip_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prediction.json"
            row = write_prediction_payload(
                path,
                condition_id="candidate_size44_seed4801",
                item_ids=[f"item-{index}" for index in range(11)],
                predictions=[f"PREDICTION {index}" for index in range(11)],
                input_lengths=[20 + index for index in range(11)],
                configuration={"seed": 4801},
                checkpoint_sha256_or_reason="a" * 64,
                transform={"name": "identity"},
                runtime_sec=0.1,
                peak_rss_bytes=1024,
                model_run_count=1,
                blank_fraction=0.5,
                warnings=[],
            )
            payload = load_prediction_payload(path, row)
            self.assertEqual(payload["condition_id"], "candidate_size44_seed4801")
            path.write_text(path.read_text().replace("PREDICTION 0", "TAMPERED"))
            with self.assertRaisesRegex(ValueError, "file hash"):
                load_prediction_payload(path, row)

    def test_exact_scoring_uses_all_2048_assignments_and_has_no_plaintext(self):
        ids = [f"item-{index}" for index in range(11)]
        targets = [chr(ord("A") + index) for index in range(11)]
        predictions = {}
        for condition_id in expected_prediction_ids():
            values = [""] * 11
            if condition_id.startswith("candidate_"):
                values = list(targets)
            predictions[condition_id] = {
                "item_ids": ids,
                "predictions": values,
                "input_lengths": [8] * 11,
                "blank_fraction": 0.0 if values == targets else 1.0,
            }
        report = score_failure_discrimination(
            prediction_payloads=predictions,
            target_item_ids=ids,
            targets=targets,
            freeze_record=_freeze(),
        )
        self.assertEqual(report["condition_count"], 41)
        self.assertEqual(report["check_items"], 11)
        self.assertTrue(report["intact_signal_conjunction_passed"])
        self.assertEqual(
            report["primary_comparisons"]["prior_size44"]["null_assignments"],
            2048,
        )
        self.assertFalse(report["plaintext_targets_or_predictions_present"])
        self.assertEqual(len(report["hypothesis_support_vector"]), 6)


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class TrainOnlyFailureDiscriminationArrayTests(unittest.TestCase):
    def test_nonwrapping_shifts_preserve_padding_and_direction(self):
        signals = np.zeros((1, 2, 8), dtype="float32")
        signals[0, 0, :5] = np.arange(1, 6)
        delayed, delayed_report = apply_nonwrapping_shift(
            signals, np.asarray([5]), offset_samples=2
        )
        advanced, advanced_report = apply_nonwrapping_shift(
            signals, np.asarray([5]), offset_samples=-2
        )
        self.assertEqual(delayed[0, 0].tolist(), [0, 0, 1, 2, 3, 0, 0, 0])
        self.assertEqual(advanced[0, 0].tolist(), [3, 4, 5, 0, 0, 0, 0, 0])
        self.assertFalse(delayed_report["offline_noncausal_diagnostic_only"])
        self.assertTrue(advanced_report["offline_noncausal_diagnostic_only"])

    def test_channel_and_row_cycles_have_no_fixed_points(self):
        signals = np.arange(2 * 4 * 3, dtype="float32").reshape(2, 4, 3)
        _, channel_mapping = apply_channel_derangement(signals, ["M000", "M001", "M002", "M003"])
        self.assertTrue(all(source != index for index, source in enumerate(channel_mapping)))
        predictions, row_mapping = derange_check_predictions(
            [f"P{index}" for index in range(11)],
            [f"I{index}" for index in range(11)],
        )
        self.assertEqual(len(predictions), 11)
        self.assertTrue(all(source != index for index, source in enumerate(row_mapping)))

    def test_timing_only_uses_no_signal_values_and_respects_lengths(self):
        signal_a = np.ones((2, 102, 6), dtype="float32")
        signal_b = np.full((2, 102, 6), 99.0, dtype="float32")
        lengths = np.asarray([4, 2])
        timing_a = timing_only_signals(signal_a, lengths)
        timing_b = timing_only_signals(signal_b, lengths)
        np.testing.assert_array_equal(timing_a, timing_b)
        self.assertTrue((timing_a[0, :, 4:] == 0).all())
        self.assertEqual(timing_a[0, 0, :4].tolist(), [1, 1, 1, 1])
        np.testing.assert_allclose(timing_a[0, 1, :4], [0, 1 / 3, 2 / 3, 1])


if __name__ == "__main__":
    unittest.main()
