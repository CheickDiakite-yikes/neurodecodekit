import importlib.util
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


HAS_NUMPY = importlib.util.find_spec("numpy") is not None
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


@unittest.skipUnless(HAS_NUMPY, "NumPy not installed")
class BlankInterceptGateTests(unittest.TestCase):
    def _fixture(self, root: Path) -> Path:
        from neurodecodekit.training.ctc_symbol_stream import (
            prepare_blank_calibration_fixture,
            registered_blank_calibration_protocol,
        )

        protocol = replace(
            registered_blank_calibration_protocol(),
            train_items=8,
            validation_items=3,
            test_items=3,
            train_seed=9871,
            validation_seed=9872,
            test_seed=9873,
        )
        prepare_blank_calibration_fixture(root, protocol=protocol)
        return root / "manifest.json"

    def _fake_producer(self):
        import numpy as np

        from neurodecodekit.cache.neurotoken_stream import CausalWindowTokenStream

        class Producer:
            n_channels = 5
            source_sampling_rate_hz = 100.0
            embedding_dim = 8
            kernel_size = 16
            stride = 4
            n_classes = 6
            token_dtype = "float32"
            parameter_payload_sha256 = "a" * 64
            trainable_parameter_count = 1130
            fixed_parameter_bytes = 1130 * 4 + 40
            mutable_state_bound_bytes = 300
            producer_right_context_samples = 0
            normalization_mean = np.zeros(5, dtype="float32")
            normalization_std = np.ones(5, dtype="float32")

            def new_stream(
                self,
                *,
                source_start_sec=0.0,
                max_chunk_samples=4096,
                max_total_samples=65536,
                max_total_tokens=4096,
            ):
                return CausalWindowTokenStream(
                    self,
                    source_start_sec=source_start_sec,
                    max_chunk_samples=max_chunk_samples,
                    max_total_samples=max_total_samples,
                    max_total_tokens=max_total_tokens,
                )

            def project_frame(self, frame):
                value = np.asarray(frame, dtype="float32").reshape(5, 16)
                embedding = np.zeros((1, 8), dtype="float32")
                embedding[0, :5] = np.abs(value).mean(axis=1)
                return embedding

            def probe_embedding(self, embedding):
                value = np.asarray(embedding, dtype="float32")
                logits = np.full((1, 6), -4.0, dtype="float32")
                channel = int(np.argmax(value[:5]))
                magnitude = float(value[channel])
                predicted = channel + 1 if magnitude >= 0.20 else 0
                logits[0, predicted] = 4.0
                return logits

        return Producer()

    def _run(self, root: Path, manifest_path: Path):
        import neurodecodekit.experiments.blank_intercept_gate as gate_module

        checkpoint = root / "checkpoint.npz"
        checkpoint.write_bytes(b"nonregistered-loop235-unit-test-checkpoint")
        producer = self._fake_producer()
        metadata = {"config_sha256": "b" * 64, "selected_epoch": 1}
        with patch.object(
            gate_module,
            "load_tiny_causal_encoder_checkpoint",
            return_value=(producer, metadata),
        ):
            return gate_module.run_blank_intercept_gate(
                fixture_manifest_path=manifest_path,
                checkpoint_path=checkpoint,
                out_json_path=root / "gate.json",
                out_markdown_path=root / "gate.md",
                require_registered_protocol=False,
                require_registered_checkpoint=False,
            )

    def test_mechanical_pass_uses_disjoint_train_views_and_opens_test_once(self):
        import neurodecodekit.experiments.blank_intercept_gate as gate_module
        from neurodecodekit.training.ctc_symbol_stream import (
            load_blank_calibration_manifest,
            resolve_ctc_symbol_partition_path,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            manifest = load_blank_calibration_manifest(
                manifest_path, require_registered_protocol=False
            )
            train_path = resolve_ctc_symbol_partition_path(
                manifest_path, manifest, "train"
            ).resolve()
            test_path = resolve_ctc_symbol_partition_path(
                manifest_path, manifest, "test"
            ).resolve()
            real_read_bytes = Path.read_bytes
            train_reads = []
            test_reads = []
            real_gate = gate_module._sequence_gate

            def tracking_read_bytes(path):
                if path.resolve() == train_path:
                    train_reads.append(str(path))
                if path.resolve() == test_path:
                    test_reads.append(str(path))
                return real_read_bytes(path)

            def pass_gate(**kwargs):
                result = real_gate(**kwargs)
                return {**result, "passed": True}

            with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False), patch.object(
                Path, "read_bytes", tracking_read_bytes
            ), patch.object(gate_module, "_sequence_gate", side_effect=pass_gate):
                report = self._run(root, manifest_path)
            persisted = json.loads((root / "gate.json").read_text(encoding="utf-8"))

        self.assertTrue(report["mechanical_gate_passed"])
        self.assertFalse(report["gate_passed"])
        self.assertEqual(
            report["decision"], "nonregistered_blank_calibration_mechanics_only"
        )
        self.assertEqual(len(train_reads), 2)
        self.assertEqual(len(test_reads), 1)
        self.assertEqual(report["access_audit"]["train_semantic_open_count"], 2)
        self.assertEqual(report["access_audit"]["test_semantic_open_count"], 1)
        self.assertTrue(report["access_audit"]["passed"])
        self.assertFalse(report["calibration"]["target_ids_opened_during_fit"])
        self.assertEqual(report["execution_counts"]["calibration_fits"], 1)
        self.assertEqual(report["streaming_replay"]["calibrated"]["schedules_passed"], 5)
        self.assertEqual(report["streaming_replay"]["unmodified"]["schedules_passed"], 5)
        self.assertTrue(report["resources"]["resource_gate_passed"])
        self.assertTrue(report["artifacts"]["artifact_gate_passed"])
        self.assertEqual(persisted["decision"], report["decision"])
        stages = [event["stage"] for event in report["access_audit"]["events"]]
        self.assertLess(stages.index("calibration_freeze"), stages.index("train_targets_open"))
        self.assertLess(stages.index("validation_decision"), stages.index("frozen_test_open"))

    def test_validation_failure_keeps_test_physically_unopened(self):
        import neurodecodekit.experiments.blank_intercept_gate as gate_module
        from neurodecodekit.training.ctc_symbol_stream import (
            load_blank_calibration_manifest,
            resolve_ctc_symbol_partition_path,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            manifest = load_blank_calibration_manifest(
                manifest_path, require_registered_protocol=False
            )
            test_path = resolve_ctc_symbol_partition_path(
                manifest_path, manifest, "test"
            ).resolve()
            real_read_bytes = Path.read_bytes
            test_reads = []
            real_gate = gate_module._sequence_gate

            def tracking_read_bytes(path):
                if path.resolve() == test_path:
                    test_reads.append(str(path))
                return real_read_bytes(path)

            def fail_gate(**kwargs):
                result = real_gate(**kwargs)
                return {**result, "passed": False}

            with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False), patch.object(
                Path, "read_bytes", tracking_read_bytes
            ), patch.object(gate_module, "_sequence_gate", side_effect=fail_gate):
                report = self._run(root, manifest_path)

        self.assertFalse(report["validation"]["gate"]["passed"])
        self.assertFalse(report["frozen_test"]["opened"])
        self.assertEqual(report["frozen_test"]["semantic_open_count"], 0)
        self.assertEqual(test_reads, [])
        self.assertEqual(report["decision"], "park_blank_intercept_calibration_branch")
        self.assertTrue(report["access_audit"]["passed"])

    def test_missing_thread_contract_fails_before_manifest_access(self):
        from neurodecodekit.experiments.blank_intercept_gate import (
            run_blank_intercept_gate,
        )

        environment = dict(THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            with patch.dict(os.environ, environment, clear=False), self.assertRaisesRegex(
                RuntimeError, "one-thread numeric environment"
            ):
                run_blank_intercept_gate(
                    fixture_manifest_path=manifest_path,
                    checkpoint_path=root / "missing.npz",
                    out_json_path=root / "gate.json",
                    require_registered_protocol=False,
                    require_registered_checkpoint=False,
                )
            self.assertFalse((root / "gate.json").exists())

    def test_fixture_cap_fails_before_checkpoint_or_output_access(self):
        from neurodecodekit.experiments.blank_intercept_gate import (
            registered_blank_intercept_gate_caps,
            run_blank_intercept_gate,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            checkpoint = root / "checkpoint.npz"
            checkpoint.write_bytes(b"must-not-be-opened")
            caps = replace(
                registered_blank_intercept_gate_caps(), max_fixture_bytes=1
            )
            with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False), patch.object(
                Path, "read_bytes", side_effect=AssertionError("checkpoint opened")
            ), self.assertRaisesRegex(ValueError, "fixture exceeds its byte cap"):
                run_blank_intercept_gate(
                    fixture_manifest_path=manifest_path,
                    checkpoint_path=checkpoint,
                    out_json_path=root / "gate.json",
                    require_registered_protocol=False,
                    require_registered_checkpoint=False,
                    caps=caps,
                )

            self.assertFalse((root / "gate.json").exists())

    def test_output_preflight_rejects_collisions_and_aliases(self):
        from neurodecodekit.experiments.blank_intercept_gate import _prepare_outputs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "existing.json"
            existing.write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "Refusing to replace"):
                _prepare_outputs([existing])
            with self.assertRaisesRegex(ValueError, "must be distinct"):
                _prepare_outputs([root / "same.json", root / "." / "same.json"])

            self.assertEqual(existing.read_text(encoding="utf-8"), "preserve")

    def test_sequence_gate_requires_correction_without_any_harm(self):
        from neurodecodekit.experiments.blank_intercept_gate import _sequence_gate

        metric = {
            "corpus_cer": 0.0,
            "exact_sequence_accuracy": 1.0,
            "repeated_pair_reconstruction_rate": 1.0,
        }
        unmodified = {"prefix_metrics": {**metric, "corpus_cer": 0.2, "exact_sequence_accuracy": 0.5}}
        calibrated = {"prefix_metrics": metric, "greedy_metrics": metric}
        control = {
            "corpus_cer": 0.8,
            "exact_sequence_accuracy": 0.0,
        }
        paired = {
            "corrected_items": 2,
            "new_error_items": 0,
            "items_with_worse_cer": 0,
            "tail_inserted_token_reduction": 2,
        }
        blank = {
            "before": {"negative_log_likelihood": 0.5, "brier_score": 0.2},
            "after": {"negative_log_likelihood": 0.2, "brier_score": 0.1},
        }
        passed = _sequence_gate(
            calibrated=calibrated,
            unmodified=unmodified,
            prior=control,
            zero_calibrated=control,
            paired=paired,
            blank_metrics=blank,
            replay_passed=True,
            resource_passed=True,
        )
        failed = _sequence_gate(
            calibrated=calibrated,
            unmodified=unmodified,
            prior=control,
            zero_calibrated=control,
            paired={**paired, "new_error_items": 1},
            blank_metrics=blank,
            replay_passed=True,
            resource_passed=True,
        )

        self.assertTrue(passed["passed"])
        self.assertFalse(failed["passed"])

    def test_cli_parser_exposes_strict_loop235_commands(self):
        from neurodecodekit.cli import build_parser

        parser = build_parser()
        fixture = parser.parse_args(
            ["make-blank-calibration-fixture", "--out-dir", "fixture"]
        )
        inspect = parser.parse_args(
            ["inspect-blank-calibration-fixture", "--manifest", "manifest.json"]
        )
        gate = parser.parse_args(
            [
                "blank-intercept-gate",
                "--fixture-manifest",
                "manifest.json",
                "--checkpoint",
                "checkpoint.npz",
                "--out-json",
                "gate.json",
                "--out-md",
                "gate.md",
            ]
        )

        self.assertEqual(fixture.func.__name__, "_cmd_make_blank_calibration_fixture")
        self.assertEqual(
            inspect.func.__name__, "_cmd_inspect_blank_calibration_fixture"
        )
        self.assertEqual(gate.func.__name__, "_cmd_blank_intercept_gate")


if __name__ == "__main__":
    unittest.main()
