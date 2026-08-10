import dataclasses
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from neurodecodekit.cli import main
from neurodecodekit.experiments import (
    physionet_low_frequency_cohort_confirmation as wo9r,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}

try:
    import numpy as np
    import scipy  # noqa: F401

    HAS_ARRAYS = True
except ImportError:
    np = None
    HAS_ARRAYS = False

try:
    import mne  # noqa: F401
    import pyriemann  # noqa: F401
    import sklearn  # noqa: F401

    HAS_CLASSICAL = HAS_ARRAYS
except ImportError:
    HAS_CLASSICAL = False


def aggregate_fixture():
    contract = wo9r.load_registered_contract(ROOT)
    participants = contract["dataset_binding"]["participants"]
    channels = contract["reader_and_derivative_contract"]["standardized_channel_names"]
    event_ids = []
    subjects = []
    runs = []
    labels = []
    for participant in participants:
        for run in ("11", "12"):
            for index in range(15):
                event_ids.append(f"{participant}-{run}-E{index:02d}")
                subjects.append(participant)
                runs.append(run)
                labels.append(index % 2)
    labels_array = np.asarray(labels, dtype="int8")
    run11_by_participant = {
        participant: [index % 2 for index in range(15)] for participant in participants
    }
    run12_by_participant = {
        participant: [index % 2 for index in range(15)] for participant in participants
    }
    perfect_conditions = {
        "execution_native_primary",
        "imagery_native",
        "execution_central_sensorimotor",
    }
    predictions = {}
    for condition_id in wo9r.CONDITION_IDS:
        source = run12_by_participant if condition_id in {
            "imagery_native",
            "execution_to_imagery",
            "imagery_no_signal_prior",
        } else run11_by_participant
        predictions[condition_id] = {
            participant: list(source[participant])
            if condition_id in perfect_conditions
            else [0] * 15
            for participant in participants
        }
    prediction_hashes = {
        condition_id: {
            participant: wo9r.wo9._prediction_set_sha256(values)
            for participant, values in rows.items()
        }
        for condition_id, rows in predictions.items()
    }
    counters = {
        "parameter_update_fits": 144,
        "target_blind_model_inference_runs": 216,
        "participant_condition_prediction_sets": 216,
        "individual_predictions": 3240,
        "final_target_rows_available_to_model_stage": 0,
        "scoring_events": 0,
    }
    freeze = {
        "schema_name": "neurodecodekit.physionet_low_frequency_prediction_freeze",
        "schema_version": wo9r.SCHEMA_VERSION,
        "contract_sha256": wo9r.CONTRACT_SHA256,
        "authorization_decision_sha256": wo9r.DECISION_SHA256,
        "source_kind": "generated_synthetic_fixture",
        "condition_ids": list(wo9r.CONDITION_IDS),
        "participant_condition_prediction_sets": 216,
        "prediction_set_sha256": prediction_hashes,
        "operation_counters": counters,
        "target_firewall": {"final_target_rows_available_to_model_stage": 0},
    }
    freeze["freeze_record_sha256"] = wo9r._canonical_sha256(freeze)
    private = {
        "schema_name": "neurodecodekit.physionet_low_frequency_private_predictions",
        "schema_version": wo9r.SCHEMA_VERSION,
        "contract_sha256": wo9r.CONTRACT_SHA256,
        "source_kind": "generated_synthetic_fixture",
        "event_ids": event_ids,
        "participant_ids": subjects,
        "run_ids": runs,
        "predictions": predictions,
        "operation_counters": counters,
    }
    private["canonical_prediction_sha256"] = wo9r._canonical_sha256(private)
    physiology = np.zeros((360, 64), dtype="float32")
    left = [channels.index(name) for name in contract["channel_sets"]["sensorimotor_left"]]
    right = [channels.index(name) for name in contract["channel_sets"]["sensorimotor_right"]]
    for row, (run, label) in enumerate(zip(runs, labels, strict=True)):
        if run == "11":
            physiology[row, right if label == 0 else left] = -1.0
    final = {
        "event_ids": np.asarray(event_ids),
        "subjects": np.asarray(subjects),
        "runs": np.asarray(runs),
        "physiology_deltas": physiology,
        "channel_names": np.asarray(channels),
    }
    sealed = {
        "event_ids": np.asarray(event_ids),
        "subjects": np.asarray(subjects),
        "runs": np.asarray(runs),
        "targets": labels_array,
    }
    return freeze, private, sealed, final


class PhysioNetLowFrequencyBaseTests(unittest.TestCase):
    def test_registered_plan_is_exact_and_target_free(self):
        plan = wo9r.registered_plan(ROOT)
        self.assertEqual(
            plan["mode"],
            "dry_run_no_local_physionet_stat_open_hash_parse_or_target_read",
        )
        self.assertEqual(plan["participants"], [f"S{index:03d}" for index in range(4, 16)])
        self.assertEqual(plan["file_count"], 72)
        self.assertEqual(plan["fit_rows"], 720)
        self.assertEqual(plan["sealed_final_rows"], 360)
        self.assertEqual(plan["parameter_update_fits"], 144)
        self.assertEqual(plan["target_blind_inference_runs"], 216)

    def test_contract_and_short_form_decision_are_hash_locked(self):
        contract = wo9r.load_registered_contract(ROOT)
        decision = wo9r.load_registered_decision(ROOT)
        self.assertEqual(contract["dataset_binding"]["exact_payload_bytes"], 184_252_032)
        self.assertEqual(decision["authorized_contract"]["sha256"], wo9r.CONTRACT_SHA256)
        self.assertEqual(decision["user_authorization"]["actual_message_sha256"], (
            "6d3ed4ff57af0f8574feb8d5b8952ee366182db82f215413c72fd3f062169c67"
        ))

    def test_target_like_cache_keys_and_public_outputs_fail_closed(self):
        for key in ("label", "targets", "reference_text", "participant_outcomes"):
            with self.subTest(key=key):
                with self.assertRaises(wo9r.WO9RFailure):
                    wo9r._validate_prediction_keys(["features", key])

    def test_output_cap_refuses_before_synthetic_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            with self.assertRaisesRegex(wo9r.WO9RRefusal, "within 1 to 64 MiB"):
                wo9r.run_synthetic_qualification(output, maximum_output_bytes=0)
            self.assertFalse(output.exists())

    def test_all_three_cli_surfaces_default_to_dry_run(self):
        for command, expected in (
            ("physionet-low-frequency-acquire", "no registered path stat"),
            ("physionet-low-frequency-cohort", "no local PhysioNet path"),
            ("score-physionet-low-frequency-cohort", "sealed final targets were not opened"),
        ):
            with self.subTest(command=command):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main([command])
                self.assertEqual(code, 0)
                self.assertIn(expected, stdout.getvalue())

    def test_real_analysis_marks_consumed_before_first_bundle_inspection(self):
        contract = wo9r.load_registered_contract(ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def assert_consumed(_bundle):
                marker = root / wo9r.EXECUTION_ROOT_RELATIVE_PATH / wo9r.EXECUTION_CONSUMED_NAME
                self.assertTrue(marker.is_file())
                raise wo9r.WO9RFailure("sentinel", "stop before bundle access")

            with (
                patch.object(wo9r, "load_registered_contract", return_value=contract),
                patch.object(wo9r, "load_registered_decision", return_value={}),
                patch.object(wo9r.acquisition, "_validate_implementation_registry", return_value={}),
                patch.object(wo9r, "_assert_directory", side_effect=assert_consumed),
                self.assertRaisesRegex(wo9r.WO9RFailure, "stop before bundle access"),
            ):
                wo9r.run_registered_prediction_execution(
                    repo_root=root,
                    evidence=wo9r.ImplementationEvidence("a" * 40, 1, 2, 3),
                    environ=THREAD_ENV,
                )


@unittest.skipUnless(HAS_ARRAYS, "NumPy and SciPy are optional")
class PhysioNetLowFrequencyArrayTests(unittest.TestCase):
    def test_one_and_two_second_feature_contracts_are_explicit_and_deterministic(self):
        rng = np.random.default_rng(5909)
        for samples in (160, 320):
            values = rng.normal(size=(64, samples))
            first = wo9r._feature_rows(values)
            second = wo9r._feature_rows(values)
            self.assertEqual(first.shape, (64, 5))
            self.assertTrue(np.array_equal(first, second))
        with self.assertRaisesRegex(wo9r.WO9RFailure, "160 or 320"):
            wo9r._feature_rows(np.zeros((64, 159)))

    def test_malformed_run_records_fail_closed(self):
        record = wo9r.build_synthetic_run_record("S004", "03")
        mutations = (
            dataclasses.replace(record, sampling_rate_hz=159.0),
            dataclasses.replace(record, channel_names=tuple(reversed(record.channel_names))),
            dataclasses.replace(record, annotations=record.annotations[:-1]),
            dataclasses.replace(
                record,
                annotations=record.annotations
                + (wo9r.Annotation(record.annotations[-1].onset_seconds + 4.0, "BAD"),),
            ),
            dataclasses.replace(
                record,
                signal_volts=np.where(
                    np.arange(record.signal_volts.size).reshape(record.signal_volts.shape) == 0,
                    np.nan,
                    record.signal_volts,
                ),
            ),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                with self.assertRaises(wo9r.WO9RFailure):
                    wo9r.extract_run_features(mutation)

    def test_aggregate_scorer_can_reach_R4_without_publishing_participant_outcomes(self):
        freeze, private, sealed, final = aggregate_fixture()
        result = wo9r.score_private_predictions(
            freeze=freeze,
            private_predictions=private,
            sealed=sealed,
            final=final,
        )
        self.assertEqual(result["verdict"], "WO9R-R4")
        self.assertTrue(result["H1_execution_native_passed"])
        self.assertTrue(result["H2_imagery_native_passed"])
        self.assertTrue(result["H3_motor_compatible_localization_passed"])
        self.assertTrue(result["mandatory_controls_passed"])
        self.assertFalse(result["individual_participant_metrics_published"])
        serialized = json.dumps(result, sort_keys=True)
        for participant in (f"S{index:03d}" for index in range(4, 16)):
            self.assertNotIn(participant, serialized)

    def test_scorer_rejects_prediction_hash_and_identity_tampering(self):
        freeze, private, sealed, final = aggregate_fixture()
        private["predictions"][wo9r.CONDITION_IDS[0]]["S004"][0] = 1
        private["canonical_prediction_sha256"] = wo9r._canonical_sha256(
            {key: value for key, value in private.items() if key != "canonical_prediction_sha256"}
        )
        with self.assertRaisesRegex(wo9r.WO9RFailure, "hash or values mismatch"):
            wo9r.score_private_predictions(
                freeze=freeze,
                private_predictions=private,
                sealed=sealed,
                final=final,
            )
        freeze, private, sealed, final = aggregate_fixture()
        sealed["event_ids"][0] = "wrong"
        with self.assertRaisesRegex(wo9r.WO9RFailure, "identities do not align"):
            wo9r.score_private_predictions(
                freeze=freeze,
                private_predictions=private,
                sealed=sealed,
                final=final,
            )

    def test_public_freeze_rejects_tampering_and_individual_predictions(self):
        freeze, _, _, _ = aggregate_fixture()
        wo9r.validate_public_freeze(freeze)
        freeze["predictions"] = [0]
        freeze["freeze_record_sha256"] = wo9r._canonical_sha256(
            {key: value for key, value in freeze.items() if key != "freeze_record_sha256"}
        )
        with self.assertRaisesRegex(wo9r.WO9RFailure, "individual-output"):
            wo9r.validate_public_freeze(freeze)

    def test_real_scorer_marks_consumed_before_first_private_or_target_hash(self):
        freeze, _, _, _ = aggregate_fixture()
        freeze["source_kind"] = "real_physionet"
        freeze["implementation_commit"] = "a" * 40
        freeze["freeze_record_sha256"] = wo9r._canonical_sha256(
            {key: value for key, value in freeze.items() if key != "freeze_record_sha256"}
        )
        contract = wo9r.load_registered_contract(ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            freeze_path = root / wo9r.FREEZE_RELATIVE_PATH
            freeze_path.parent.mkdir(parents=True)
            freeze_path.write_text(json.dumps(freeze), encoding="utf-8")
            output = root / wo9r.EXECUTION_ROOT_RELATIVE_PATH
            output.mkdir(parents=True)

            def assert_consumed(_path):
                self.assertTrue((output / wo9r.SCORING_CONSUMED_NAME).is_file())
                raise wo9r.WO9RFailure("sentinel", "stop before private target hash")

            completed = SimpleNamespace(stdout="", returncode=0)
            with (
                patch.object(wo9r, "load_registered_contract", return_value=contract),
                patch.object(wo9r, "load_registered_decision", return_value={}),
                patch.object(wo9r, "_git_head", return_value="b" * 40),
                patch.object(wo9r.subprocess, "run", return_value=completed),
                patch.object(wo9r, "_file_sha256", side_effect=assert_consumed),
                self.assertRaisesRegex(wo9r.WO9RFailure, "stop before private target hash"),
            ):
                wo9r.score_registered_execution(
                    repo_root=root,
                    evidence=wo9r.FreezeEvidence("b" * 40, 1, 2, 3),
                    environ=THREAD_ENV,
                )


@unittest.skipUnless(HAS_CLASSICAL, "classical EEG environment is optional")
class PhysioNetLowFrequencyClassicalTests(unittest.TestCase):
    def test_dependency_versions_are_exact(self):
        self.assertEqual(
            wo9r.dependency_versions(),
            {
                "numpy": "2.5.2",
                "scipy": "1.18.0",
                "mne": "1.12.1",
                "scikit_learn": "1.9.0",
                "pyriemann": "0.12",
            },
        )

    def test_participant_model_predictions_replay_exactly(self):
        contract = wo9r.load_registered_contract(ROOT)
        records = [
            wo9r.extract_run_features(wo9r.build_synthetic_run_record("S004", run))
            for run in ("03", "04", "07", "08", "11", "12")
        ]
        fit = wo9r._concatenate(records[:4], include_labels=True)
        final = wo9r._concatenate(records[4:], include_labels=False)
        first = wo9r._participant_predictions(fit, final, "S004", contract)
        second = wo9r._participant_predictions(fit, final, "S004", contract)
        self.assertEqual(first, second)
        self.assertEqual(tuple(first), wo9r.CONDITION_IDS)
        self.assertTrue(all(len(values) == 15 for values in first.values()))

    def test_complete_generated_fixture_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            summary = wo9r.run_synthetic_qualification(output)
            self.assertTrue(summary["all_gates_passed"])
            self.assertEqual(summary["synthetic_runs"], 72)
            self.assertEqual(summary["synthetic_events"], 1080)
            self.assertEqual(summary["parameter_update_fits"], 144)
            self.assertEqual(summary["target_blind_model_inference_runs"], 216)
            self.assertEqual(summary["participant_condition_prediction_sets"], 216)
            self.assertEqual(summary["real_data_reads"], 0)
            self.assertEqual(summary["real_target_reads"], 0)
            self.assertLessEqual(summary["generated_bytes"], 64 * 1024**2)
            final = wo9r._load_npz(
                output / wo9r.PREDICTION_DERIVATIVE_NAME,
                target_free=True,
            )
            self.assertEqual(final["features"].shape, (360, 64, 5))
            self.assertFalse(any("target" in key or "label" in key for key in final))
            freeze = json.loads(
                (output / "synthetic_prediction_freeze.v0.json").read_text(encoding="utf-8")
            )
            wo9r.validate_public_freeze(freeze)


if __name__ == "__main__":
    unittest.main()
