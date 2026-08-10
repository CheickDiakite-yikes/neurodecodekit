import dataclasses
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.experiments import physionet_motor_positive_control as wo9


try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

try:
    import mne  # noqa: F401
    import pyriemann  # noqa: F401
    import sklearn  # noqa: F401

    HAS_CLASSICAL = HAS_NUMPY
except ImportError:
    HAS_CLASSICAL = False


ROOT = Path(__file__).resolve().parents[1]


def fixture_freeze(predictions=None):
    if predictions is None:
        predictions = {condition: [0] * 45 for condition in wo9.CONDITION_IDS}
    prediction_hashes = {
        condition: wo9._prediction_set_sha256(predictions[condition])
        for condition in wo9.CONDITION_IDS
    }
    contract = wo9.load_registered_contract(ROOT)
    value = {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_prediction_freeze",
        "schema_version": "0.1.0",
        "status": "predictions_frozen_run11_sealed_target_file_unopened_by_model_stage",
        "contract_sha256": wo9.CONTRACT_SHA256,
        "authorization_decision_sha256": wo9.DECISION_SHA256,
        "source_kind": "generated_synthetic_fixture",
        "prediction_set_ids": list(wo9.CONDITION_IDS),
        "prediction_set_count": 12,
        "prediction_set_sha256": prediction_hashes,
        "configuration_sha256": wo9._canonical_sha256(
            {
                "candidate_families": contract["candidate_families"],
                "fixed_comparator": contract["fixed_comparator"],
                "causal_preprocessing": contract["causal_preprocessing"],
                "channel_sets": contract["channel_sets"],
                "determinism": contract["determinism"],
            }
        ),
        "split_protocol_sha256": wo9._canonical_sha256(
            {
                "dataset_binding": contract["dataset_binding"],
                "split_and_selection": contract["split_and_selection"],
            }
        ),
        "selected_family": "fixed_8_to_30_hz_csp_lda",
        "target_firewall": {
            "run11_target_rows_available_to_model_stage": 0,
            "prediction_derivative_contains_targets": False,
            "individual_outputs_committed": False,
        },
        "determinism_checks": {
            "zero_signal_prediction_set_complete": True,
            "no_signal_prediction_set_complete": True,
            "zero_signal_prediction_sha256": prediction_hashes["all_zero_final_signal"],
            "no_signal_prediction_sha256": prediction_hashes[
                "train_only_no_signal_prior"
            ],
        },
    }
    value["freeze_record_sha256"] = wo9._canonical_sha256(value)
    return value


class PhysioNetMotorPositiveControlBaseTests(unittest.TestCase):
    def test_registered_plan_is_no_stat_and_exact(self):
        plan = wo9.registered_plan(ROOT)
        self.assertEqual(plan["mode"], "dry_run_no_local_physionet_stat_open_hash_or_parse")
        self.assertEqual(plan["subjects"], ["S001", "S002", "S003"])
        self.assertEqual(plan["fit_and_selection_runs"], ["03", "07"])
        self.assertEqual(plan["sealed_final_run"], "11")
        self.assertEqual(plan["file_count"], 9)
        self.assertEqual(plan["payload_bytes"], 23_248_224)
        self.assertEqual(plan["prediction_set_count"], 12)
        self.assertEqual(plan["maximum_fits"], 40)
        self.assertEqual(plan["registered_executions"], 1)
        self.assertEqual(plan["retries"], 0)
        self.assertEqual(plan["reruns"], 0)

    def test_contract_and_decision_are_hash_locked(self):
        contract = wo9.load_registered_contract(ROOT)
        decision = wo9.load_registered_decision(ROOT)
        self.assertEqual(contract["dataset_binding"]["file_count"], 9)
        self.assertEqual(tuple(contract["mandatory_final_prediction_sets"]), wo9.CONDITION_IDS)
        self.assertEqual(decision["authorized_contract"]["sha256"], wo9.CONTRACT_SHA256)
        self.assertTrue(decision["green_request"]["both_required_jobs_green"])

    def test_public_freeze_rejects_individual_outputs_and_tampering(self):
        freeze = fixture_freeze()
        wo9.validate_public_freeze_ledger(freeze)
        leaked = json.loads(json.dumps(freeze))
        leaked["predictions"] = [0] * 45
        leaked["freeze_record_sha256"] = wo9._canonical_sha256(
            {key: value for key, value in leaked.items() if key != "freeze_record_sha256"}
        )
        with self.assertRaisesRegex(wo9.WO9Failure, "individual-output"):
            wo9.validate_public_freeze_ledger(leaked)
        tampered = json.loads(json.dumps(freeze))
        tampered["selected_family"] = "regularized_riemannian_mdm"
        with self.assertRaisesRegex(wo9.WO9Failure, "canonical SHA-256"):
            wo9.validate_public_freeze_ledger(tampered)
        missing_hash = fixture_freeze()
        del missing_hash["prediction_set_sha256"][wo9.CONDITION_IDS[-1]]
        missing_hash["freeze_record_sha256"] = wo9._canonical_sha256(
            {
                key: value
                for key, value in missing_hash.items()
                if key != "freeze_record_sha256"
            }
        )
        with self.assertRaisesRegex(wo9.WO9Failure, "hash inventory mismatch"):
            wo9.validate_public_freeze_ledger(missing_hash)

    def test_prediction_derivative_forbids_target_like_keys(self):
        for key in (
            "labels",
            "targets",
            "reference_text",
            "intended_outcome",
        ):
            with self.subTest(key=key):
                with self.assertRaisesRegex(wo9.WO9Failure, "forbidden key"):
                    wo9._validate_prediction_derivative_keys(["primary", key])

    def test_fixture_output_cap_refuses_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            with self.assertRaisesRegex(wo9.WO9Refusal, "at most 64 MiB"):
                wo9.run_synthetic_qualification(output, maximum_output_bytes=65 * 1024**2)
            self.assertFalse(output.exists())

    def test_optional_extra_is_narrow_and_base_remains_empty(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("dependencies = []", text)
        for requirement in (
            '"numpy>=1.26"',
            '"scipy>=1.11"',
            '"mne>=1.12,<1.13"',
            '"scikit-learn>=1.4,<2"',
            '"pyriemann==0.12"',
        ):
            self.assertIn(requirement, text)
        for forbidden in ("braindecode", "moabb"):
            self.assertNotIn(forbidden, text.lower())


@unittest.skipUnless(HAS_NUMPY, "NumPy is optional")
class PhysioNetMotorPositiveControlArrayTests(unittest.TestCase):
    def test_malformed_run_records_fail_closed(self):
        record = wo9.build_synthetic_run_record("S001", "03")
        mutations = (
            dataclasses.replace(record, sampling_rate_hz=159.0),
            dataclasses.replace(
                record,
                channel_names=tuple(reversed(record.channel_names)),
            ),
            dataclasses.replace(record, annotations=record.annotations[:-1]),
            dataclasses.replace(
                record,
                annotations=record.annotations
                + (wo9.Annotation(record.annotations[-1].onset_seconds + 4.0, "BAD"),),
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
                with self.assertRaises(wo9.WO9Failure):
                    wo9.extract_run_features(mutation)

    def test_aggregate_scorer_publishes_no_individual_participant_metrics(self):
        event_ids = [
            f"{subject}-11-E{index:02d}"
            for subject in ("S001", "S002", "S003")
            for index in range(15)
        ]
        participants = [subject for subject in ("S001", "S002", "S003") for _ in range(15)]
        labels = np.asarray([index % 2 for _ in range(3) for index in range(15)], dtype="int8")
        predictions = {
            condition: labels.tolist() if condition == wo9.CONDITION_IDS[0] else [0] * 45
            for condition in wo9.CONDITION_IDS
        }
        physiology = np.zeros((45, 2, 2, 64), dtype="float32")
        contract = wo9.load_registered_contract(ROOT)
        left = [wo9.REGISTERED_CHANNEL_NAMES.index(name) for name in contract["channel_sets"][
            "sensorimotor_left"
        ]]
        right = [wo9.REGISTERED_CHANNEL_NAMES.index(name) for name in contract["channel_sets"][
            "sensorimotor_right"
        ]]
        for row, label in enumerate(labels):
            physiology[row, :, 1, right if label == 0 else left] = -2.0
        result = wo9.score_private_predictions(
            freeze=fixture_freeze(predictions),
            private_predictions={
                "event_ids": event_ids,
                "participant_ids": participants,
                "predictions": predictions,
            },
            sealed={"event_ids": np.asarray(event_ids), "targets": labels},
            prediction_derivative={
                "physiology_log_power": physiology,
                "channel_names": np.asarray(wo9.REGISTERED_CHANNEL_NAMES),
            },
            permutation_draws=7,
        )
        self.assertEqual(result["scored_final_events"], 45)
        self.assertFalse(result["individual_participant_metrics_published"])
        serialized = json.dumps(result, sort_keys=True)
        for subject in ("S001", "S002", "S003"):
            self.assertNotIn(subject, serialized)

    def test_scorer_rejects_private_prediction_hash_mismatch(self):
        labels = np.asarray([index % 2 for index in range(45)], dtype="int8")
        predictions = {condition: labels.tolist() for condition in wo9.CONDITION_IDS}
        freeze = fixture_freeze(predictions)
        predictions[wo9.CONDITION_IDS[0]][0] = 1 - predictions[wo9.CONDITION_IDS[0]][0]
        event_ids = [f"event-{index:02d}" for index in range(45)]
        participants = [subject for subject in ("S001", "S002", "S003") for _ in range(15)]
        with self.assertRaisesRegex(wo9.WO9Failure, "private prediction hash mismatch"):
            wo9.score_private_predictions(
                freeze=freeze,
                private_predictions={
                    "event_ids": event_ids,
                    "participant_ids": participants,
                    "predictions": predictions,
                },
                sealed={"event_ids": np.asarray(event_ids), "targets": labels},
                prediction_derivative={
                    "physiology_log_power": np.zeros((45, 2, 2, 64)),
                    "channel_names": np.asarray(wo9.REGISTERED_CHANNEL_NAMES),
                },
                permutation_draws=7,
            )


@unittest.skipUnless(HAS_CLASSICAL, "classical EEG dependencies are optional")
class PhysioNetMotorPositiveControlClassicalTests(unittest.TestCase):
    def test_both_registered_families_fit_and_replay(self):
        rng = np.random.default_rng(5509)
        values = rng.normal(size=(16, 8, 320))
        labels = np.asarray([0, 1] * 8, dtype="int8")
        values[labels == 0, 0, :] += 1.5 * np.sin(np.linspace(0.0, 20.0, 320))
        values[labels == 1, 1, :] += 1.5 * np.sin(np.linspace(0.0, 20.0, 320))
        for family in (
            "fixed_8_to_30_hz_csp_lda",
            "regularized_riemannian_mdm",
        ):
            with self.subTest(family=family):
                model = wo9.fit_registered_family(family, values, labels)
                first = model.predict(values)
                second = model.predict(values)
                self.assertTrue(np.array_equal(first, second))
                self.assertEqual(first.shape, (16,))

    def test_complete_generated_fixture_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            summary = wo9.run_synthetic_qualification(
                output,
                maximum_output_bytes=64 * 1024**2,
                permutation_draws=31,
            )
            self.assertEqual(summary["status"], "passed_generated_fixture_only")
            self.assertEqual(summary["synthetic_runs"], 9)
            self.assertEqual(summary["synthetic_events"], 135)
            self.assertEqual(summary["prediction_sets"], 12)
            self.assertEqual(summary["classical_parameter_update_fits"], 33)
            self.assertEqual(summary["target_blind_model_inference_runs"], 45)
            self.assertEqual(summary["real_data_reads"], 0)
            self.assertEqual(summary["real_target_reads"], 0)
            self.assertLessEqual(summary["generated_bytes"], 64 * 1024**2)
            prediction = wo9._load_npz(
                output / wo9.PREDICTION_DERIVATIVE_NAME,
                prediction_derivative=True,
            )
            self.assertNotIn("labels", prediction)
            self.assertNotIn("targets", prediction)


if __name__ == "__main__":
    unittest.main()
