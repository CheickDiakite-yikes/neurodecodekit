from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import iackd_cue_action_acquisition as acquisition
from neurodecodekit.experiments import iackd_cue_action_dissociation as iackd


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in iackd.THREAD_ENV_KEYS}


def _has_exact_stack() -> bool:
    try:
        iackd.dependency_versions()
    except (Exception, SystemExit):
        return False
    return True


HAS_EXACT_STACK = _has_exact_stack()


class IACKDBaseTests(unittest.TestCase):
    def test_registered_plans_are_target_free_and_exact(self):
        acquisition_plan = acquisition.registered_plan(ROOT)
        analysis_plan = iackd.registered_plan(ROOT)
        self.assertEqual(acquisition_plan["object_count"], 1_340)
        self.assertEqual(acquisition_plan["payload_bytes"], 7_249_113_684)
        self.assertEqual(analysis_plan["parameter_update_fits"], 300)
        self.assertEqual(analysis_plan["prediction_sets"], 420)
        self.assertIn("no_local_IACKD", analysis_plan["mode"])

    def test_registered_inventory_forms_exact_128_run_groups(self):
        groups = iackd._run_groups(acquisition.load_registered_inventory(ROOT))
        self.assertEqual(len(groups), 128)
        self.assertEqual(groups[0]["subject"], "sub-01")
        self.assertEqual(groups[0]["hand"], "left")
        self.assertEqual(groups[0]["run"], "01")
        self.assertEqual(groups[-1]["subject"], "sub-15")
        self.assertEqual(groups[-1]["hand"], "right")
        self.assertEqual(groups[-1]["run"], "04")

    def test_incongruent_condition_cannot_alias_to_congruent(self):
        self.assertEqual(iackd._condition("incongruent"), "yellow")
        self.assertEqual(iackd._condition("yellow incongruent"), "yellow")
        self.assertEqual(iackd._condition("congruent"), "red")
        self.assertEqual(iackd._condition("red congruent"), "red")

    def test_event_parser_requires_order_and_preserves_condition(self):
        text = (
            "onset\tvalue\ttrial_id\tcondition\n"
            "1.0\tStimulus/S 55\ttrial-1\tincongruent\n"
            "2.0\tStimulus/S 14\ttrial-1\tincongruent\n"
            "3.0\tResponse/R 66\ttrial-1\tincongruent\n"
        )
        rows = iackd.parse_events_tsv(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].condition, "yellow")
        self.assertEqual(rows[0].trial_id, "trial-1")
        with self.assertRaisesRegex(iackd.IACKDFailure, "outside a unique trial"):
            iackd.parse_events_tsv("onset\tvalue\n1.0\t14\n")

    def test_real_analysis_marks_consumed_before_bundle_inspection(self):
        contract = iackd.load_registered_contract(ROOT)
        inventory = acquisition.load_registered_inventory(ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = iackd.ImplementationEvidence("a" * 40, 1, 2, 3)
            with (
                mock.patch.object(iackd, "load_registered_contract", return_value=contract),
                mock.patch.object(iackd, "load_registered_decision", return_value={}),
                mock.patch.object(
                    acquisition, "load_registered_inventory", return_value=inventory
                ),
                mock.patch.object(
                    acquisition,
                    "_validate_implementation_registry",
                    return_value={"tracked_file_hashes": []},
                ),
                mock.patch.object(iackd, "dependency_versions", return_value={}),
            ):
                with self.assertRaises(FileNotFoundError):
                    iackd.run_registered_prediction_execution(
                        repo_root=root,
                        evidence=evidence,
                        environ=THREAD_ENV,
                    )
            consumed = root / iackd.EXECUTION_ROOT_RELATIVE_PATH / iackd.EXECUTION_CONSUMED_NAME
            self.assertTrue(consumed.is_file())

    def test_public_freeze_rejects_unregistered_field_before_hash_check(self):
        with self.assertRaisesRegex(iackd.IACKDFailure, "strict schema"):
            iackd.validate_public_freeze(
                {
                    "schema_name": "neurodecodekit.iackd_prediction_freeze",
                    "unexpected_target_alias": [0, 1],
                }
            )


@unittest.skipUnless(HAS_EXACT_STACK, "requires the frozen optional IACKD stack")
class IACKDExactStackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.first = cls.root / "first"
        cls.summary = iackd.run_synthetic_qualification(cls.first)
        cls.freeze = json.loads(
            (cls.first / "synthetic_prediction_freeze.v0.json").read_text(encoding="utf-8")
        )
        cls.private = json.loads(
            (cls.first / iackd.PRIVATE_PREDICTIONS_NAME).read_text(encoding="utf-8")
        )
        cls.final = iackd._load_npz(
            cls.first / iackd.FINAL_DERIVATIVE_NAME,
            target_free=True,
        )
        cls.sealed = iackd._load_npz(cls.first / iackd.SEALED_TARGET_NAME)
        cls.physiology = iackd._load_npz(
            cls.first / iackd.PHYSIOLOGY_SUMMARY_NAME,
            target_free=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_full_synthetic_inventory_and_target_firewall(self):
        self.assertEqual(self.summary["synthetic_runs"], 128)
        self.assertEqual(self.summary["synthetic_trials"], 2_048)
        self.assertEqual(self.summary["fit_rows"], 1_568)
        self.assertEqual(self.summary["final_rows"], 480)
        self.assertEqual(self.summary["parameter_update_fits"], 300)
        self.assertEqual(self.summary["participant_condition_prediction_sets"], 420)
        self.assertEqual(self.summary["final_target_rows_available_to_model_stage"], 0)
        forbidden = ("target", "label", "direction", "signed", "prediction", "probability")
        self.assertFalse(
            [key for key in self.final if any(token in key.lower() for token in forbidden)]
        )
        self.assertEqual(
            self.physiology["readiness_mean_C3_C4_Cz"].shape,
            (30, 3, 1024),
        )

    def test_deterministic_replay_of_arrays_and_predictions(self):
        second = self.root / "second"
        second_summary = iackd.run_synthetic_qualification(second)
        deterministic_files = (
            iackd.FIT_DERIVATIVE_NAME,
            iackd.FINAL_DERIVATIVE_NAME,
            iackd.SEALED_TARGET_NAME,
            iackd.PHYSIOLOGY_SUMMARY_NAME,
            iackd.PRIVATE_PREDICTIONS_NAME,
        )
        for name in deterministic_files:
            self.assertEqual(
                hashlib.sha256((self.first / name).read_bytes()).hexdigest(),
                hashlib.sha256((second / name).read_bytes()).hexdigest(),
                name,
            )
        second_freeze = json.loads(
            (second / "synthetic_prediction_freeze.v0.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.freeze["prediction_set_sha256"], second_freeze["prediction_set_sha256"])
        for root, summary in ((self.first, self.summary), (second, second_summary)):
            self.assertEqual(
                summary["generated_bytes"],
                sum(path.stat().st_size for path in root.iterdir() if path.is_file()),
            )
            self.assertLess(summary["generated_bytes"], 512 * 1024 * 1024)

    def test_stream_join_and_target_failure_firewall(self):
        self.assertEqual(
            iackd._stream_scales(
                {
                    "timestamp": {"Units": "milliseconds"},
                    "palm_position": {"Units": "meters"},
                },
                kind="leap",
            ),
            (1e-3, 1000.0),
        )
        events = iackd.parse_events_tsv(
            "onset\tvalue\ttrial_id\tcondition\n"
            "1.0\t55\ttrial-1\tred\n"
            "2.0\t14\ttrial-1\tred\n"
            "3.0\t66\ttrial-1\tred\n"
        )
        samples = [1.5 + 0.2 * index for index in range(9)]
        ball = "trial_id\ttimestamp\tx\tcondition\tmove_direct\n" + "".join(
            f"trial-1\t{value}\t{10 * index}\tred\tright\n"
            for index, value in enumerate(samples)
        )
        leap = "trial_id\ttimestamp\tx\ty\tz\tcondition\n" + "".join(
            f"trial-1\t{value}\t{10 * index}\t0\t0\tred\n"
            for index, value in enumerate(samples)
        )
        joined = iackd.reconcile_trials(
            events,
            iackd._stream_groups(ball, kind="ball"),
            iackd._stream_groups(leap, kind="leap"),
        )
        self.assertEqual(len(joined), 1)
        record = iackd.build_synthetic_run_record("sub-01", "left", "01")
        bad_trial = replace(record.trials[0], ball_move_direct="invalid")
        bad_record = replace(record, trials=(bad_trial, *record.trials[1:]))
        with self.assertRaisesRegex(iackd.IACKDFailure, "move_direct") as raised:
            iackd.extract_run_features(bad_record)
        self.assertEqual(raised.exception.stage, "target")

    def test_malformed_cache_and_output_cap_fail_closed(self):
        np = iackd._np()
        leak_path = self.root / "leak.npz"
        iackd._write_npz_exclusive(
            leak_path,
            {"actual_direction": np.asarray([0, 1], dtype="int8")},
            1024 * 1024,
        )
        with self.assertRaisesRegex(iackd.IACKDFailure, "leaks keys"):
            iackd._load_npz(leak_path, target_free=True)
        with self.assertRaisesRegex(iackd.IACKDFailure, "exceeds output cap"):
            iackd._write_npz_exclusive(
                self.root / "too-small.npz",
                {"values": np.zeros(8, dtype="float32")},
                1,
            )
        self.assertFalse((self.root / "too-small.npz").exists())

    def _chance(self, targets):
        np = iackd._np()
        original = np.asarray(targets, dtype="int8")
        values = original.copy()
        for label in (0, 1):
            positions = np.flatnonzero(original == label)
            values[positions[len(positions) // 2 :]] = 1 - label
        return values.tolist()

    def _route_inputs(self, route: str):
        private = copy.deepcopy(self.private)
        predictions = {condition: {} for condition in iackd.CONDITION_IDS}
        for unit, event_ids in private["unit_event_ids"].items():
            subject, hand = unit.split("|", 1)
            mask = (self.final["subjects"] == subject) & (self.final["hands"] == hand)
            actual = self.sealed["actual_hand_directions"][mask].astype("int8")
            visual = self.sealed["visual_target_directions"][mask].astype("int8")
            chance = self._chance(actual)
            self.assertEqual(len(event_ids), len(actual))
            for condition in iackd.CONDITION_IDS:
                predictions[condition][unit] = list(chance)
            if route == "IACKD-R1":
                predictions["whole_head_primary"][unit] = visual.tolist()
            elif route in {"IACKD-R2", "IACKD-R3", "IACKD-R4"}:
                predictions["whole_head_primary"][unit] = actual.tolist()
                predictions["fit_only_EOG_orthogonalized_whole_head"][unit] = actual.tolist()
                if route == "IACKD-R2":
                    predictions["HEOG_VEOG_only"][unit] = actual.tolist()
                if route == "IACKD-R4":
                    predictions["central_C3_C4_Cz"][unit] = actual.tolist()
        private["predictions"] = predictions
        unhashed = dict(private)
        unhashed.pop("canonical_prediction_sha256", None)
        private["canonical_prediction_sha256"] = iackd._canonical_sha256(unhashed)
        freeze = copy.deepcopy(self.freeze)
        freeze["prediction_set_sha256"] = {
            condition: {
                unit: iackd._prediction_sha256(values)
                for unit, values in unit_predictions.items()
            }
            for condition, unit_predictions in predictions.items()
        }
        freeze["canonical_private_prediction_sha256"] = private[
            "canonical_prediction_sha256"
        ]
        unhashed_freeze = dict(freeze)
        unhashed_freeze.pop("freeze_record_sha256", None)
        freeze["freeze_record_sha256"] = iackd._canonical_sha256(unhashed_freeze)
        return freeze, private

    def test_all_five_registered_routes_are_reachable_without_tuning(self):
        for expected in ("IACKD-R1", "IACKD-R0", "IACKD-R2", "IACKD-R3", "IACKD-R4"):
            with self.subTest(expected=expected):
                freeze, private = self._route_inputs(expected)
                result = iackd.score_private_predictions(
                    freeze=freeze,
                    private_predictions=private,
                    sealed=self.sealed,
                    final=self.final,
                    physiology=self.physiology,
                )
                self.assertEqual(result["verdict"], expected)
                self.assertFalse(result["individual_participant_metrics_published"])


if __name__ == "__main__":
    unittest.main()
