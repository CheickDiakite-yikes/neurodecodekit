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
class StreamingCTCGateTests(unittest.TestCase):
    def _fixture(self, root: Path) -> Path:
        from neurodecodekit.training.ctc_symbol_stream import (
            prepare_ctc_symbol_stream_fixture,
            registered_ctc_symbol_stream_protocol,
        )

        protocol = replace(
            registered_ctc_symbol_stream_protocol(),
            train_items=8,
            validation_items=3,
            test_items=3,
            train_seed=9831,
            validation_seed=9832,
            test_seed=9833,
        )
        prepare_ctc_symbol_stream_fixture(root, protocol=protocol)
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
        import neurodecodekit.experiments.streaming_ctc_gate as gate_module

        checkpoint = root / "checkpoint.npz"
        checkpoint.write_bytes(b"nonregistered-loop23-unit-test-checkpoint")
        producer = self._fake_producer()
        metadata = {
            "config_sha256": "b" * 64,
            "selected_epoch": 1,
        }
        with patch.object(
            gate_module,
            "load_tiny_causal_encoder_checkpoint",
            return_value=(producer, metadata),
        ):
            return gate_module.run_streaming_ctc_gate(
                fixture_manifest_path=manifest_path,
                checkpoint_path=checkpoint,
                out_json_path=root / "gate.json",
                out_markdown_path=root / "gate.md",
                require_registered_protocol=False,
                require_registered_checkpoint=False,
            )

    def test_mechanical_pass_opens_test_once_and_preserves_access_order(self):
        import neurodecodekit.experiments.streaming_ctc_gate as gate_module
        from neurodecodekit.training.ctc_symbol_stream import (
            load_ctc_symbol_stream_manifest,
            resolve_ctc_symbol_partition_path,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            manifest = load_ctc_symbol_stream_manifest(
                manifest_path, require_registered_protocol=False
            )
            test_path = resolve_ctc_symbol_partition_path(
                manifest_path, manifest, "test"
            ).resolve()
            real_read_bytes = Path.read_bytes
            real_validation_gate = gate_module._validation_gate
            real_test_gate = gate_module._test_gate
            test_file_reads = []

            def tracking_read_bytes(path):
                if path.resolve() == test_path:
                    test_file_reads.append(str(path))
                return real_read_bytes(path)

            def pass_validation(prefix, greedy, prior, zero, **kwargs):
                result = real_validation_gate(prefix, greedy, prior, zero, **kwargs)
                return {**result, "passed": True}

            def pass_test(prefix, greedy, prior, zero, bootstrap_prior, bootstrap_zero):
                result = real_test_gate(
                    prefix,
                    greedy,
                    prior,
                    zero,
                    bootstrap_prior,
                    bootstrap_zero,
                )
                return {**result, "passed": True}

            with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False), patch.object(
                Path, "read_bytes", tracking_read_bytes
            ), patch.object(
                gate_module, "_validation_gate", side_effect=pass_validation
            ), patch.object(gate_module, "_test_gate", side_effect=pass_test):
                report = self._run(root, manifest_path)
            persisted = json.loads((root / "gate.json").read_text(encoding="utf-8"))

        self.assertTrue(report["mechanical_gate_passed"])
        self.assertFalse(report["gate_passed"])
        self.assertEqual(
            report["decision"],
            "nonregistered_fixture_or_checkpoint_mechanics_only",
        )
        self.assertTrue(report["frozen_test"]["opened"])
        self.assertEqual(report["frozen_test"]["semantic_open_count"], 1)
        self.assertEqual(len(test_file_reads), 1)
        self.assertEqual(report["streaming_replay"]["schedules_passed"], 5)
        self.assertTrue(report["streaming_replay"]["passed"])
        self.assertTrue(report["access_audit"]["passed"])
        self.assertTrue(report["resources"]["resource_gate_passed"])
        self.assertTrue(report["artifacts"]["artifact_gate_passed"])
        self.assertEqual(persisted["decision"], report["decision"])
        stages = [event["stage"] for event in report["access_audit"]["events"]]
        self.assertLess(stages.index("decoder_config_freeze"), stages.index("frozen_test_open"))

    def test_validation_failure_keeps_test_physically_unopened(self):
        import neurodecodekit.experiments.streaming_ctc_gate as gate_module
        from neurodecodekit.training.ctc_symbol_stream import (
            load_ctc_symbol_stream_manifest,
            resolve_ctc_symbol_partition_path,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            manifest = load_ctc_symbol_stream_manifest(
                manifest_path, require_registered_protocol=False
            )
            test_path = resolve_ctc_symbol_partition_path(
                manifest_path, manifest, "test"
            ).resolve()
            real_read_bytes = Path.read_bytes
            real_validation_gate = gate_module._validation_gate
            test_file_reads = []

            def tracking_read_bytes(path):
                if path.resolve() == test_path:
                    test_file_reads.append(str(path))
                return real_read_bytes(path)

            def fail_validation(prefix, greedy, prior, zero, **kwargs):
                result = real_validation_gate(prefix, greedy, prior, zero, **kwargs)
                return {**result, "passed": False}

            with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False), patch.object(
                Path, "read_bytes", tracking_read_bytes
            ), patch.object(
                gate_module, "_validation_gate", side_effect=fail_validation
            ):
                report = self._run(root, manifest_path)

        self.assertFalse(report["validation"]["gate"]["passed"])
        self.assertFalse(report["frozen_test"]["opened"])
        self.assertEqual(report["frozen_test"]["semantic_open_count"], 0)
        self.assertEqual(test_file_reads, [])
        self.assertFalse(report["gate_passed"])
        self.assertEqual(report["decision"], "park_streaming_ctc_decoder_branch")
        self.assertTrue(report["access_audit"]["passed"])

    def test_missing_thread_contract_fails_before_manifest_access(self):
        from neurodecodekit.experiments.streaming_ctc_gate import (
            run_streaming_ctc_gate,
        )

        environment = dict(THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            with patch.dict(os.environ, environment, clear=False), self.assertRaisesRegex(
                RuntimeError, "one-thread numeric environment"
            ):
                run_streaming_ctc_gate(
                    fixture_manifest_path=manifest_path,
                    checkpoint_path=root / "missing.npz",
                    out_json_path=root / "gate.json",
                    require_registered_protocol=False,
                    require_registered_checkpoint=False,
                )
            self.assertFalse((root / "gate.json").exists())

    def test_cli_parser_exposes_strict_loop23_commands(self):
        from neurodecodekit.cli import build_parser

        parser = build_parser()
        fixture = parser.parse_args(
            ["make-ctc-symbol-stream-fixture", "--out-dir", "fixture"]
        )
        inspect = parser.parse_args(
            ["inspect-ctc-symbol-stream-fixture", "--manifest", "manifest.json"]
        )
        gate = parser.parse_args(
            [
                "streaming-ctc-gate",
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

        self.assertEqual(fixture.func.__name__, "_cmd_make_ctc_symbol_stream_fixture")
        self.assertEqual(
            inspect.func.__name__, "_cmd_inspect_ctc_symbol_stream_fixture"
        )
        self.assertEqual(gate.func.__name__, "_cmd_streaming_ctc_gate")


if __name__ == "__main__":
    unittest.main()
