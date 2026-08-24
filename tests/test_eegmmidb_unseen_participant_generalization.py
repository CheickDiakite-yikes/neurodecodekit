from __future__ import annotations

import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from neurodecodekit import eegmmidb_ug1_cli
from neurodecodekit.experiments import eegmmidb_unseen_participant_generalization as ug1


HAS_CLASSICAL = all(
    importlib.util.find_spec(name) is not None for name in ("numpy", "scipy", "sklearn")
)
RUN_NUMERICAL = HAS_CLASSICAL and os.environ.get("NEURODECODEKIT_UG1_NUMERICAL_TESTS") == "1"


class UG1BaseTests(unittest.TestCase):
    def test_sidecar_cli_preserves_central_cli_hash_and_defaults_to_plan(self) -> None:
        with mock.patch("builtins.print") as printer:
            self.assertEqual(eegmmidb_ug1_cli.main([]), 0)
        rendered = "\n".join(str(call.args[0]) for call in printer.call_args_list)
        self.assertIn('"file_count": 36', rendered)
        self.assertIn("no output path", rendered)

    def test_registered_artifacts_load(self) -> None:
        self.assertEqual(ug1.load_contract()["contract_id"], "EEGMMIDB-UG1")
        self.assertEqual(ug1.load_amendment()["amendment_id"], "EEGMMIDB-UG1-A1")

    def test_forbidden_run_refuses(self) -> None:
        with self.assertRaises(ug1.UG1Refusal):
            ug1.task_for_run("10")

    def test_balanced_accuracy(self) -> None:
        self.assertEqual(ug1.balanced_accuracy(["T1", "T1", "T2", "T2"], ["T1"] * 4), 0.5)

    def test_sign_flip_retains_ties(self) -> None:
        self.assertEqual(ug1._exact_sign_flip([0.0] * 15), 1.0)

    def test_thread_environment_refuses_drift(self) -> None:
        previous = os.environ.get("OMP_NUM_THREADS")
        try:
            for name in ug1.THREAD_ENVIRONMENT:
                os.environ[name] = "1"
            ug1.assert_single_thread_environment()
            os.environ["OMP_NUM_THREADS"] = "2"
            with self.assertRaises(ug1.UG1Refusal):
                ug1.assert_single_thread_environment()
        finally:
            if previous is None:
                os.environ.pop("OMP_NUM_THREADS", None)
            else:
                os.environ["OMP_NUM_THREADS"] = previous

    def test_output_path_is_absolute_and_protected_roots_refuse(self) -> None:
        temporary_root = "/private/tmp" if Path("/private/tmp").is_dir() else None
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                prepared = ug1._prepare_output_path("generated/result.json")
                self.assertTrue(prepared.is_absolute())
                self.assertEqual(prepared, Path(directory) / "generated/result.json")
                with self.assertRaises(ug1.UG1Refusal):
                    ug1._prepare_output_path("data/result.json")
                with self.assertRaises(ug1.UG1Refusal):
                    ug1._prepare_output_path(".codex_work/result.json")
                with self.assertRaisesRegex(ug1.UG1Refusal, "traversal"):
                    ug1._prepare_output_path("../result.json")
                with self.assertRaises(ug1.UG1Refusal):
                    ug1._prepare_output_path("DATA/result.json")
            finally:
                os.chdir(previous)

    def test_atomic_publish_refuses_a_destination_race(self) -> None:
        temporary_root = "/private/tmp" if Path("/private/tmp").is_dir() else None
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            destination = Path(directory) / "result.json"

            def race() -> None:
                destination.write_bytes(b"race\n")

            with self.assertRaisesRegex(ug1.UG1Refusal, "appeared"):
                ug1._atomic_write_bytes(destination, b"result\n", _before_rename=race)
            self.assertEqual(destination.read_bytes(), b"race\n")
            self.assertEqual(list(Path(directory).glob(".result.json.*")), [])

    def test_incremental_output_and_free_disk_caps_refuse(self) -> None:
        with self.assertRaisesRegex(ug1.UG1Refusal, "incremental"):
            ug1._assert_resource_limits(
                started=0.0,
                peak_rss_bytes=1,
                output_bytes=1,
                incremental_output_bytes=2,
                wall_cap_seconds=float("inf"),
                incremental_output_cap_bytes=1,
            )
        with self.assertRaisesRegex(ug1.UG1Refusal, "free-disk"):
            ug1._assert_minimum_free_disk(Path.cwd(), observed_free_bytes=1)

    def test_joint_source_fresh_overlap_and_payload_alias_refuse(self) -> None:
        source = {"execution": [{"participant": "S001", "opaque_row_id": "a"}], "imagery": []}
        fresh = {"execution": [{"participant": "S016", "opaque_row_id": "b"}], "imagery": []}
        ug1.validate_source_fresh_isolation(
            source,
            fresh,
            source_payload_identities=["source"],
            fresh_payload_identities=["fresh"],
        )
        with self.assertRaises(ug1.UG1Refusal):
            ug1.validate_source_fresh_isolation(
                source,
                {"execution": [{"participant": "S016", "opaque_row_id": "a"}], "imagery": []},
                source_payload_identities=["source"],
                fresh_payload_identities=["fresh"],
            )
        with self.assertRaises(ug1.UG1Refusal):
            ug1.validate_source_fresh_isolation(
                source,
                fresh,
                source_payload_identities=["shared"],
                fresh_payload_identities=["shared"],
            )

    def test_literal_derangement_is_identity_free_and_exact(self) -> None:
        targets = ["T1" if index % 2 == 0 else "T2" for index in range(15)]
        indices = ug1.load_amendment()["control_contract"]["source_label_derangement_indices"]
        self.assertEqual(ug1.derange_target_group(targets), [targets[index] for index in indices])
        with self.assertRaises(ug1.UG1Refusal):
            ug1.derange_target_group(targets[:-1])


@unittest.skipUnless(
    RUN_NUMERICAL,
    "UG1 numerical tests require the classical extra and explicit isolated opt-in",
)
class UG1NumericalTests(unittest.TestCase):
    def test_causal_chunk_replay_and_future_impulse(self) -> None:
        import numpy as np

        rng = np.random.default_rng(4)
        signal = rng.normal(size=(64, 1000)).astype("float64")
        referenced = ug1.common_average_reference(signal)
        full = ug1.causal_filter(referenced)
        chunked = ug1.causal_filter(referenced, chunk_sizes=(211, 307, 482))
        np.testing.assert_allclose(full, chunked, rtol=0.0, atol=1e-12)
        impulse = referenced.copy()
        impulse[:, 800] += 1.0
        changed = ug1.causal_filter(impulse)
        np.testing.assert_array_equal(full[:, :800], changed[:, :800])

    def test_window_dimensions(self) -> None:
        import numpy as np

        signal = np.arange(64 * 320, dtype="float64").reshape(64, 320)
        self.assertEqual(ug1.window_features(signal, 0, 320).shape, (320,))
        self.assertEqual(ug1.window_features(signal[:18], 0, 320).shape, (90,))

    def test_source_feature_cohort_is_complete_and_target_free(self) -> None:
        rows, targets, byte_count = ug1.build_synthetic_feature_cohort(partition="source")
        ug1.validate_partition(rows, targets, partition="source")
        self.assertGreater(byte_count, 0)
        self.assertFalse(any("target" in row for task_rows in rows.values() for row in task_rows))
        original_hash = ug1._feature_partition_sha256(rows)
        changed = {task: [dict(row) for row in task_rows] for task, task_rows in rows.items()}
        changed["execution"][0]["timing_only"] = changed["execution"][0]["timing_only"].copy()
        changed["execution"][0]["timing_only"][0] += 1.0
        self.assertNotEqual(original_hash, ug1._feature_partition_sha256(changed))
        target_hash = ug1._target_partition_sha256(targets)
        changed_targets = {task: list(values) for task, values in targets.items()}
        changed_targets["execution"][0] = "T2" if changed_targets["execution"][0] == "T1" else "T1"
        self.assertNotEqual(target_hash, ug1._target_partition_sha256(changed_targets))

    def test_montage_identity_drift_refuses(self) -> None:
        record = ug1.build_synthetic_run_record()
        with self.assertRaisesRegex(ug1.UG1Refusal, "montage"):
            ug1.extract_run(replace(record, montage_identity="unknown"))

    def test_predictive_view_excludes_identity_and_refuses_targets(self) -> None:
        import numpy as np

        rows, _targets, _ = ug1.build_synthetic_feature_cohort(partition="fresh")
        task_rows = rows["execution"][:2]
        view = ug1._predictive_feature_rows(task_rows)
        self.assertEqual(set(view[0]), set(ug1.PREDICTIVE_FEATURE_DIMENSIONS))
        self.assertNotIn("participant", view[0])
        relabeled = [{**row, "participant": "opaque-relabel"} for row in task_rows]
        for original, changed in zip(view, ug1._predictive_feature_rows(relabeled), strict=True):
            for name in ug1.PREDICTIVE_FEATURE_DIMENSIONS:
                np.testing.assert_array_equal(original[name], changed[name])
        target_bearing = [dict(row) for row in task_rows]
        target_bearing[0]["target"] = "T1"
        with self.assertRaisesRegex(ug1.UG1Refusal, "target-bearing"):
            ug1._predictive_feature_rows(target_bearing)

        def model(dimension):
            return ug1.FrozenLDA(
                mean=np.zeros(dimension),
                scale=np.ones(dimension),
                classes=("T1", "T2"),
                coef=np.ones((1, dimension)),
                intercept=np.zeros(1),
            )

        task_models = {
            condition: model(ug1.MODEL_DIMENSIONS[condition]) for condition in ug1.FITTED_CONDITIONS
        }
        self.assertEqual(
            ug1._predict_task_values(task_models, view),
            ug1._predict_task_values(task_models, ug1._predictive_feature_rows(relabeled)),
        )
        with self.assertRaisesRegex(ug1.UG1Refusal, "identity"):
            ug1._predict_task_values(task_models, task_rows)

    def test_frozen_lda_replay_and_tie(self) -> None:
        import numpy as np

        features = np.asarray([[-2.0], [-1.0], [1.0], [2.0]], dtype="float64")
        model = ug1.fit_frozen_lda(features, ["T1", "T1", "T2", "T2"])
        self.assertEqual(ug1.predict_frozen_lda(model, features), ["T1", "T1", "T2", "T2"])
        tie = ug1.FrozenLDA(
            mean=np.zeros(1),
            scale=np.ones(1),
            classes=("T1", "T2"),
            coef=np.zeros((1, 1)),
            intercept=np.zeros(1),
        )
        self.assertEqual(ug1.predict_frozen_lda(tie, np.zeros((2, 1))), ["T1", "T1"])

    def test_exact_fit_and_prediction_schedule_with_lightweight_fit_double(self) -> None:
        import numpy as np

        source_rows, source_targets, _ = ug1.build_synthetic_feature_cohort(partition="source")
        fit_calls = 0

        def fake_fit(features, targets):
            nonlocal fit_calls
            fit_calls += 1
            values = np.asarray(features, dtype="float64")
            signs = np.asarray([1.0 if target == "T2" else -1.0 for target in targets])
            coefficient = np.zeros(values.shape[1], dtype="float64")
            if values.shape[1] != 3:
                coefficient = values.T @ signs
            return ug1.FrozenLDA(
                mean=np.zeros(values.shape[1]),
                scale=np.ones(values.shape[1]),
                classes=("T1", "T2"),
                coef=coefficient.reshape(1, -1),
                intercept=np.zeros(1),
            )

        with mock.patch.object(ug1, "fit_frozen_lda", side_effect=fake_fit):
            models, report = ug1.run_source_loso_and_fit(source_rows, source_targets)
        self.assertEqual(fit_calls, 61)
        self.assertEqual(report["fit_count"], 61)
        self.assertEqual(report["prediction_set_count"], 60)
        fresh_rows, _fresh_targets, _ = ug1.build_synthetic_feature_cohort(partition="fresh")
        predictions, fresh_sets = ug1.predict_fresh_rows(models, fresh_rows)
        self.assertEqual(fresh_sets, 360)
        self.assertEqual(len(predictions), 5_400)

    def test_checkpoint_rejects_member_mutation(self) -> None:
        import numpy as np

        def model(dimension):
            return ug1.FrozenLDA(
                mean=np.zeros(dimension),
                scale=np.ones(dimension),
                classes=("T1", "T2"),
                coef=np.ones((1, dimension)),
                intercept=np.zeros(1),
            )

        models = {
            task: {
                condition: model(ug1.MODEL_DIMENSIONS[condition])
                for condition in ug1.FITTED_CONDITIONS
            }
            for task in ("execution", "imagery")
        }
        source_hashes = {"fixture": "0" * 64}
        versions = ug1.load_amendment()["model_contract"]["required_versions"]
        bindings = {
            "expected_code_hash": "1" * 64,
            "expected_configuration_hash": "2" * 64,
            "expected_source_payload_hashes": source_hashes,
            "expected_package_versions": versions,
        }
        temporary_root = "/private/tmp" if Path("/private/tmp").is_dir() else None
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            destination = Path(directory) / "checkpoint"
            ug1.save_checkpoint(
                models,
                destination,
                source_payload_hashes=source_hashes,
                code_hash="1" * 64,
                configuration_hash="2" * 64,
                package_versions=versions,
            )
            loaded, _ = ug1.load_checkpoint(destination, **bindings)
            self.assertIn("primary_whole_head", loaded["execution"])
            with self.assertRaises(ug1.UG1Refusal):
                ug1.load_checkpoint(
                    destination,
                    **{**bindings, "expected_code_hash": "3" * 64},
                )
            with self.assertRaises(ug1.UG1Refusal):
                ug1.load_checkpoint(
                    destination,
                    **{**bindings, "expected_configuration_hash": "4" * 64},
                )
            manifest_mutation = Path(directory) / "manifest-mutation"
            shutil.copytree(destination, manifest_mutation)
            manifest_path = manifest_mutation / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["channel_order"] = list(reversed(manifest["channel_order"]))
            unsigned = {key: value for key, value in manifest.items() if key != "manifest_hash"}
            manifest["manifest_hash"] = ug1._sha256_bytes(ug1._canonical_bytes(unsigned))
            manifest_path.write_bytes(ug1._canonical_bytes(manifest))
            with self.assertRaises(ug1.UG1Refusal):
                ug1.load_checkpoint(manifest_mutation, **bindings)
            source_mutation = Path(directory) / "source-mutation"
            shutil.copytree(destination, source_mutation)
            source_manifest_path = source_mutation / "manifest.json"
            source_manifest = json.loads(source_manifest_path.read_text())
            source_manifest["source_payload_hashes"] = {"fixture": "5" * 64}
            unsigned = {
                key: value for key, value in source_manifest.items() if key != "manifest_hash"
            }
            source_manifest["manifest_hash"] = ug1._sha256_bytes(ug1._canonical_bytes(unsigned))
            source_manifest_path.write_bytes(ug1._canonical_bytes(source_manifest))
            with self.assertRaises(ug1.UG1Refusal):
                ug1.load_checkpoint(source_mutation, **bindings)
            whitespace_mutation = Path(directory) / "whitespace-mutation"
            shutil.copytree(destination, whitespace_mutation)
            whitespace_manifest = whitespace_mutation / "manifest.json"
            whitespace_manifest.write_bytes(
                whitespace_manifest.read_bytes().replace(b"{", b"{ ", 1)
            )
            with self.assertRaisesRegex(ug1.UG1Refusal, "canonical"):
                ug1.load_checkpoint(whitespace_mutation, **bindings)
            duplicate_mutation = Path(directory) / "duplicate-mutation"
            shutil.copytree(destination, duplicate_mutation)
            duplicate_manifest = duplicate_mutation / "manifest.json"
            duplicate_manifest.write_bytes(
                duplicate_manifest.read_bytes().replace(b"{", b'{"schema_name":"duplicate",', 1)
            )
            with self.assertRaisesRegex(ug1.UG1Refusal, "duplicate"):
                ug1.load_checkpoint(duplicate_mutation, **bindings)
            extra_mutation = Path(directory) / "extra-mutation"
            shutil.copytree(destination, extra_mutation)
            extra_manifest_path = extra_mutation / "manifest.json"
            extra_manifest = json.loads(extra_manifest_path.read_text())
            extra_manifest["unexpected"] = False
            unsigned = {
                key: value for key, value in extra_manifest.items() if key != "manifest_hash"
            }
            extra_manifest["manifest_hash"] = ug1._sha256_bytes(ug1._canonical_bytes(unsigned))
            extra_manifest_path.write_bytes(ug1._canonical_bytes(extra_manifest))
            with self.assertRaisesRegex(ug1.UG1Refusal, "field inventory"):
                ug1.load_checkpoint(extra_mutation, **bindings)
            member = next(destination.glob("*.mean.npy"))
            member.write_bytes(member.read_bytes() + b"x")
            with self.assertRaises(ug1.UG1Refusal):
                ug1.load_checkpoint(destination, **bindings)


if __name__ == "__main__":
    unittest.main()
