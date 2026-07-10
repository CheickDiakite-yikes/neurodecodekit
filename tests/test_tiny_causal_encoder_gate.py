import importlib.util
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


HAS_ML = bool(
    importlib.util.find_spec("numpy") and importlib.util.find_spec("torch")
)
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


@unittest.skipUnless(HAS_ML, "NumPy/Torch not installed")
class TinyCausalEncoderGateTests(unittest.TestCase):
    def _fixture(
        self,
        root: Path,
        *,
        train_items: int = 16,
        validation_items: int = 4,
        test_items: int = 4,
        seed_base: int = 9940,
    ) -> Path:
        from neurodecodekit.training.causal_motifs import (
            prepare_causal_motif_fixture,
            registered_causal_motif_protocol,
        )

        protocol = replace(
            registered_causal_motif_protocol(),
            train_items=train_items,
            validation_items=validation_items,
            test_items=test_items,
            train_seed=seed_base + 1,
            validation_seed=seed_base + 2,
            test_seed=seed_base + 3,
        )
        prepare_causal_motif_fixture(root, protocol=protocol)
        return root / "manifest.json"

    def _run(self, root: Path, manifest_path: Path):
        from neurodecodekit.experiments.tiny_causal_encoder_gate import (
            run_tiny_causal_encoder_gate,
        )

        return run_tiny_causal_encoder_gate(
            fixture_manifest_path=manifest_path,
            checkpoint_out_path=root / "checkpoint.npz",
            out_json_path=root / "gate.json",
            out_markdown_path=root / "gate.md",
            require_registered_protocol=False,
        )

    def test_nonregistered_rehearsal_passes_mechanics_and_opens_test_once(self):
        from neurodecodekit.training.causal_motifs import (
            load_causal_motif_manifest,
            resolve_manifest_partition_path,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            manifest = load_causal_motif_manifest(
                manifest_path, require_registered_protocol=False
            )
            test_path = resolve_manifest_partition_path(
                manifest_path, manifest, "test"
            ).resolve()
            real_read_bytes = Path.read_bytes
            test_file_reads = []

            def tracking_read_bytes(path):
                if path.resolve() == test_path:
                    test_file_reads.append(str(path))
                return real_read_bytes(path)

            with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False), patch.object(
                Path, "read_bytes", tracking_read_bytes
            ):
                report = self._run(root, manifest_path)
            persisted = json.loads((root / "gate.json").read_text(encoding="utf-8"))

        self.assertTrue(report["mechanical_gate_passed"])
        self.assertFalse(report["gate_passed"])
        self.assertEqual(report["decision"], "nonregistered_fixture_mechanics_only")
        self.assertTrue(report["selection"]["validation_gate"]["passed"])
        self.assertTrue(report["frozen_test"]["gate"]["passed"])
        self.assertEqual(report["frozen_test"]["semantic_open_count"], 1)
        self.assertEqual(len(test_file_reads), 1)
        self.assertEqual(report["streaming_replay"]["schedules_passed"], 5)
        self.assertTrue(report["streaming_replay"]["schedule_bits_invariant"])
        self.assertEqual(report["model"]["trainable_parameters"], 1130)
        self.assertEqual(report["resources"]["thread_environment"], THREAD_ENVIRONMENT)
        self.assertTrue(report["resources"]["resource_gate_passed"])
        self.assertTrue(report["artifacts"]["artifact_gate_passed"])
        self.assertEqual(persisted["decision"], report["decision"])
        stages = [event["stage"] for event in report["access_audit"]["events"]]
        self.assertLess(stages.index("validation_selection"), stages.index("checkpoint_freeze"))
        self.assertLess(stages.index("checkpoint_freeze"), stages.index("frozen_test_open"))

    def test_forced_validation_failure_keeps_test_physically_unopened(self):
        import neurodecodekit.experiments.tiny_causal_encoder_gate as gate_module

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(
                root / "fixture",
                train_items=8,
                validation_items=3,
                test_items=3,
                seed_base=9950,
            )
            manifest = gate_module.load_causal_motif_manifest(
                manifest_path, require_registered_protocol=False
            )
            test_path = gate_module.resolve_manifest_partition_path(
                manifest_path, manifest, "test"
            ).resolve()
            real_read_bytes = Path.read_bytes
            test_file_reads = []
            real_validation_gate = gate_module._validation_gate

            def tracking_read_bytes(path):
                if path.resolve() == test_path:
                    test_file_reads.append(str(path))
                return real_read_bytes(path)

            def force_failure(learned, prior):
                result = real_validation_gate(learned, prior)
                return {**result, "passed": False}

            with patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False), patch.object(
                Path, "read_bytes", tracking_read_bytes
            ), patch.object(gate_module, "_validation_gate", side_effect=force_failure):
                report = self._run(root, manifest_path)

        self.assertFalse(report["selection"]["validation_gate"]["passed"])
        self.assertFalse(report["frozen_test"]["opened"])
        self.assertEqual(report["frozen_test"]["semantic_open_count"], 0)
        self.assertEqual(test_file_reads, [])
        self.assertFalse(report["gate_passed"])
        self.assertEqual(report["decision"], "park_tiny_causal_encoder_branch")
        self.assertTrue(report["access_audit"]["passed"])

    def test_missing_thread_contract_fails_before_manifest_access(self):
        from neurodecodekit.experiments.tiny_causal_encoder_gate import (
            run_tiny_causal_encoder_gate,
        )

        environment = dict(THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture", seed_base=9960)
            with patch.dict(os.environ, environment, clear=False), self.assertRaisesRegex(
                RuntimeError, "one-thread numeric environment"
            ):
                run_tiny_causal_encoder_gate(
                    fixture_manifest_path=manifest_path,
                    checkpoint_out_path=root / "checkpoint.npz",
                    out_json_path=root / "gate.json",
                    require_registered_protocol=False,
                )
            self.assertFalse((root / "checkpoint.npz").exists())
            self.assertFalse((root / "gate.json").exists())

    def test_cli_parser_exposes_strict_loop22_commands(self):
        from neurodecodekit.cli import build_parser

        parser = build_parser()
        fixture = parser.parse_args(
            ["make-causal-motif-fixture", "--out-dir", "fixture"]
        )
        inspect = parser.parse_args(
            ["inspect-causal-motif-fixture", "--manifest", "manifest.json"]
        )
        gate = parser.parse_args(
            [
                "tiny-causal-encoder-gate",
                "--fixture-manifest",
                "manifest.json",
                "--checkpoint-out",
                "checkpoint.npz",
                "--out-json",
                "gate.json",
                "--out-md",
                "gate.md",
            ]
        )

        self.assertEqual(fixture.func.__name__, "_cmd_make_causal_motif_fixture")
        self.assertEqual(inspect.func.__name__, "_cmd_inspect_causal_motif_fixture")
        self.assertEqual(gate.func.__name__, "_cmd_tiny_causal_encoder_gate")


if __name__ == "__main__":
    unittest.main()
