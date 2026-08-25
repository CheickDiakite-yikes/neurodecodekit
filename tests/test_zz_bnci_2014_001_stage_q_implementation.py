from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit.datasets import bnci_2014_001_stage_q as stage_q  # noqa: E402


THREAD_ENV = {name: "1" for name in stage_q.THREAD_ENVIRONMENT}


class BNCIStageQImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.np = stage_q._np()
        _loadmat, savemat = stage_q._scipy_io()
        cls.savemat = staticmethod(savemat)

    def _task_run(self) -> dict[str, object]:
        starts = 1 + self.np.arange(48, dtype="float64") * 1500
        return {
            "X": self.np.zeros((72_000, 25), dtype="int8"),
            "trial": starts,
            "y": self.np.tile(self.np.arange(1, 5, dtype="float64"), 12),
            "fs": 250.0,
            "classes": list(stage_q.UPSTREAM_CLASSES),
            "artifacts": self.np.zeros(48, dtype="float64"),
        }

    def _payload(self, *, mutate=None, top_level=None) -> tuple[bytes, stage_q.PayloadMember]:
        runs = [self._task_run() for _ in range(6)]
        if mutate is not None:
            mutate(runs)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.mat"
            content = top_level if top_level is not None else {"data": self.np.asarray(runs, dtype=object)}
            self.savemat(path, content, do_compression=True)
            payload = path.read_bytes()
        return payload, stage_q.PayloadMember("fixture.mat", len(payload), stage_q._sha256(payload))

    def _parse_bounded(
        self, payload: bytes, member: stage_q.PayloadMember
    ) -> tuple[list[stage_q.TaskRun], int]:
        real_asarray = self.np.asarray

        def bounded_asarray(value, dtype=None, *args, **kwargs):
            observed = real_asarray(value, *args, **kwargs)
            if dtype == "float64" and observed.shape == (72_000, 25):
                return observed
            return real_asarray(observed, dtype=dtype)

        with mock.patch.object(self.np, "asarray", new=bounded_asarray):
            return stage_q.parse_verified_mat_payload(payload, member)

    def test_plan_is_public_and_has_zero_scientific_operations(self) -> None:
        plan = stage_q.registered_plan(ROOT)
        self.assertEqual(plan["MAT_files"], 18)
        self.assertEqual(plan["expected_trials"], 5_184)
        for field in ("network_bytes", "model_runs", "training_runs", "prediction_sets", "target_deliveries", "scores"):
            self.assertEqual(plan[field], 0)

    def test_parser_accepts_integral_matlab_floats_and_six_task_runs(self) -> None:
        payload, member = self._payload()
        runs, calibration = self._parse_bounded(payload, member)
        self.assertEqual((len(runs), calibration), (6, 0))
        self.assertEqual(runs[0].starts.dtype.name, "int64")
        self.assertEqual(runs[0].targets.dtype.name, "uint8")

    def test_parser_accepts_empty_calibration_structs_without_signal_use(self) -> None:
        empty = self._task_run()
        empty["X"] = self.np.full((1, 25), self.np.nan)
        empty["trial"] = self.np.empty(0)
        empty["y"] = self.np.empty(0)
        empty["artifacts"] = self.np.empty(0)
        runs = [empty, empty, empty] + [self._task_run() for _ in range(6)]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.mat"
            self.savemat(path, {"data": self.np.asarray(runs, dtype=object)}, do_compression=True)
            payload = path.read_bytes()
        member = stage_q.PayloadMember(path.name, len(payload), stage_q._sha256(payload))
        parsed, calibration = self._parse_bounded(payload, member)
        self.assertEqual((len(parsed), calibration), (6, 3))

    def test_parser_refuses_fractional_trial_indices(self) -> None:
        def mutate(runs):
            runs[0]["trial"][0] = 1.5

        payload, member = self._payload(mutate=mutate)
        with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "trial indices"):
            self._parse_bounded(payload, member)

    def test_parser_refuses_overlap_bad_balance_and_nonbinary_artifacts(self) -> None:
        mutations = [
            lambda runs: runs[0]["trial"].__setitem__(1, 1000),
            lambda runs: runs[0]["y"].__setitem__(0, 2),
            lambda runs: runs[0]["artifacts"].__setitem__(0, 2),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                payload, member = self._payload(mutate=mutate)
                with self.assertRaises(stage_q.BNCIStageQRefusal):
                    self._parse_bounded(payload, member)

    def test_parser_refuses_extra_top_level_variable_and_digest_change(self) -> None:
        runs = [self._task_run() for _ in range(6)]
        payload, member = self._payload(
            top_level={"data": self.np.asarray(runs, dtype=object), "extra": self.np.zeros(1)}
        )
        with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "top-level"):
            self._parse_bounded(payload, member)
        changed = stage_q.PayloadMember(member.relative_path, member.bytes, "0" * 64)
        with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "identity"):
            self._parse_bounded(payload, changed)

    def test_target_free_features_are_deterministic_and_target_invariant(self) -> None:
        rng = self.np.random.default_rng(42)
        signal = rng.normal(0.0, 0.05, size=(1_500, 25)).astype("float32")
        starts = self.np.zeros(48, dtype="int64")
        targets = self.np.tile(self.np.arange(1, 5, dtype="uint8"), 12)
        first = stage_q.extract_target_free_run_features(signal, starts)
        targets = self.np.roll(targets, 1)
        second = stage_q.extract_target_free_run_features(signal, starts)
        self.assertEqual(set(int(value) for value in targets), {1, 2, 3, 4})
        self.assertEqual(
            stage_q.deterministic_npz_bytes(first),
            stage_q.deterministic_npz_bytes(second),
        )
        self.assertEqual(set(first), set(stage_q.FEATURE_DIMENSIONS))

    def test_predictive_archive_has_no_target_or_artifact_array(self) -> None:
        arrays = {
            name: [self.np.zeros(dimension, dtype="float32")]
            for name, dimension in stage_q.FEATURE_DIMENSIONS.items()
        }
        payload = stage_q.deterministic_npz_bytes(arrays)
        with self.np.load(stage_q.io.BytesIO(payload), allow_pickle=False) as archive:
            names = set(archive.files)
        self.assertFalse(names.intersection({"target", "targets", "target_index", "y", "artifact", "artifacts", "artifact_flag"}))

    def test_output_refuses_overwrite_and_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            output.write_text("occupied", encoding="utf-8")
            with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "fixed output"):
                stage_q.run_generated_qualification(output, environ=THREAD_ENV)
            output.unlink()
            output.symlink_to(Path(temporary) / "missing")
            with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "fixed output"):
                stage_q.run_generated_qualification(output, environ=THREAD_ENV)

    def test_generated_qualification_and_original_live_entry_are_closed(self) -> None:
        with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "consumed"):
            stage_q.run_generated_qualification(
                ROOT / "registries/bnci_2014_001_stage_q_generated_result.v0.json",
                environ=THREAD_ENV,
            )
        with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "no live entry point"):
            stage_q.execute_registered_stage_q(ROOT, environ=THREAD_ENV)

    def test_execute_refuses_before_activation_without_private_access(self) -> None:
        with self.assertRaisesRegex(stage_q.BNCIStageQRefusal, "no live entry point"):
            stage_q.execute_registered_stage_q(ROOT, environ=THREAD_ENV)

    def test_cli_help_and_plan(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SRC)
        help_result = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.bnci_c3c5_stage_q_cli", "--help"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("target-firewalled", help_result.stdout)
        plan_result = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.bnci_c3c5_stage_q_cli", "plan", "--repo-root", str(ROOT)],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(plan_result.stdout)["status"], "public_plan_only_no_ignored_path_or_MAT_operation")


if __name__ == "__main__":
    unittest.main()
