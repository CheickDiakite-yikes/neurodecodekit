import importlib.util
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_REGISTRY = REPO_ROOT / "registries/loop48_stage_c_synthetic_implementation.v0.json"
HAS_NUMPY = importlib.util.find_spec("numpy") is not None
HAS_TORCH = importlib.util.find_spec("torch") is not None


class Loop48StageCSyntheticDependencyLightTests(unittest.TestCase):
    def test_implementation_record_is_pre_execution_and_hash_bound(self):
        record = json.loads(IMPLEMENTATION_REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(
            record["status"],
            "preflight_refused_zero_update_fix_pending_remote_green",
        )
        self.assertEqual(
            record["research_milestone"]["commit"], "9579be93340d86f87f1b8c8f4ad7f987ebd765f0"
        )
        self.assertEqual(record["research_milestone"]["push_ci_run_id"], 29466218879)
        self.assertEqual(record["research_milestone"]["pull_request_ci_run_id"], 29466225955)
        for binding in record["source_bindings"].values():
            path = REPO_ROOT / binding["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), binding["sha256"])
        authorization = record["authorization"]
        self.assertTrue(authorization["implementation_authorized_and_completed_now"])
        self.assertFalse(authorization["synthetic_calibration_executed_now"])
        self.assertFalse(record["preflight_refusal"]["calibration_started"])
        self.assertEqual(record["preflight_refusal"]["optimizer_steps"], 0)
        for key, value in authorization.items():
            if (
                key.endswith("authorized_now")
                and key != "implementation_authorized_and_completed_now"
            ):
                self.assertFalse(value, key)

    def test_public_handoff_surfaces_name_the_implementation_boundary(self):
        paths = (
            REPO_ROOT / "README.md",
            REPO_ROOT / "START_HERE.md",
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "docs/NEXT_20_LOOPS_TRACKER.md",
            REPO_ROOT / "docs/LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
            REPO_ROOT / "docs/CODEX_HANDOFF.md",
            REPO_ROOT / "prompts/CODEX_START_PROMPT.md",
        )
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("LOOP_48_STAGE_C_SYNTHETIC_IMPLEMENTATION.md", text, path)
            self.assertIn("loop48_stage_c_synthetic_implementation.v0.json", text, path)

    def test_cli_help_exposes_only_synthetic_paths(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.cli",
                "loop48-stage-c-synthetic",
                "--help",
            ],
            cwd=REPO_ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        output = completed.stdout
        self.assertIn("--research-registry", output)
        self.assertIn("--out-dir", output)
        for forbidden in (
            "--cache",
            "--raw",
            "--target",
            "--subject",
            "--session",
            "--s24",
            "--s25",
        ):
            self.assertNotIn(forbidden, output)

    def test_gate_caps_cannot_expand(self):
        from neurodecodekit.experiments.temporal_representation_gate import (
            StageCSyntheticCaps,
            _validate_caps,
        )

        _validate_caps(StageCSyntheticCaps())
        with self.assertRaisesRegex(ValueError, "16 MiB"):
            _validate_caps(StageCSyntheticCaps(max_generated_artifact_bytes=16 * 1024**2 + 1))
        with self.assertRaisesRegex(ValueError, "one thread"):
            _validate_caps(StageCSyntheticCaps(cpu_threads=2))

    def test_gate_accepts_the_exact_frozen_research_registry(self):
        from neurodecodekit.experiments.temporal_representation_gate import (
            _load_and_validate_research_registry,
        )

        path = REPO_ROOT / "registries/loop48_stage_c_representation_repair_research.v0.json"
        payload = _load_and_validate_research_registry(path)
        self.assertEqual(payload["synthetic_calibration_plan"]["fixture_seed"], 4850)
        self.assertEqual(
            payload["synthetic_calibration_plan"]["partitions"],
            {"train": 24, "selection": 8, "final": 8},
        )

    def test_implementation_sources_have_no_protected_reader_import(self):
        paths = (
            REPO_ROOT / "src/neurodecodekit/models/tiny_causal_temporal_ctc.py",
            REPO_ROOT / "src/neurodecodekit/training/temporal_motif_sentences.py",
            REPO_ROOT / "src/neurodecodekit/experiments/temporal_representation_gate.py",
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        for forbidden in (
            "row_streaming_npz",
            "sentence_cache",
            "mne.io",
            "scipy.io",
            "huggingface_hub",
            "S21 session",
        ):
            self.assertNotIn(forbidden, combined)

    def test_malformed_result_is_rejected(self):
        from neurodecodekit.experiments.temporal_representation_gate import (
            load_stage_c_synthetic_result,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.json"
            path.write_text(json.dumps({"schema": {"name": "wrong", "version": 0}}))
            with self.assertRaisesRegex(ValueError, "unsupported"):
                load_stage_c_synthetic_result(path)


@unittest.skipUnless(HAS_NUMPY, "NumPy is optional")
class Loop48StageCFixtureTests(unittest.TestCase):
    def test_fixture_replay_identity_padding_and_split_binding(self):
        import numpy as np

        from neurodecodekit.training.temporal_motif_sentences import (
            generate_registered_temporal_motif_fixture,
            validate_temporal_motif_fixture,
        )

        first = generate_registered_temporal_motif_fixture()
        second = generate_registered_temporal_motif_fixture()
        first_summary = validate_temporal_motif_fixture(first)
        second_summary = validate_temporal_motif_fixture(second)
        self.assertEqual(first_summary["fixture_sha256"], second_summary["fixture_sha256"])
        self.assertEqual(first_summary["item_count"], 40)
        self.assertEqual(first_summary["array_bytes"], 1_699_920)
        self.assertEqual(first_summary["partitions"], {"train": 24, "selection": 8, "final": 8})
        all_ids = []
        for split in ("train", "selection", "final"):
            partition = first.partition(split)
            all_ids.extend(partition.item_ids.tolist())
            for row, length in zip(
                partition.signals,
                partition.input_lengths,
                strict=True,
            ):
                self.assertTrue(
                    np.array_equal(row[:, int(length) :], np.zeros_like(row[:, int(length) :]))
                )
                self.assertTrue(
                    np.array_equal(
                        row[:, : int(length) : 4], np.zeros_like(row[:, : int(length) : 4])
                    )
                )
        self.assertEqual(len(set(all_ids)), 40)

    def test_fixture_validator_rejects_padding_and_sampled_frame_leakage(self):
        from dataclasses import replace

        from neurodecodekit.training.temporal_motif_sentences import (
            generate_registered_temporal_motif_fixture,
            validate_temporal_motif_fixture,
        )

        fixture = generate_registered_temporal_motif_fixture()
        bad_signals = fixture.train.signals.copy()
        bad_signals[0, 0, 0] = 1.0
        bad_train = replace(fixture.train, signals=bad_signals)
        with self.assertRaisesRegex(ValueError, "sampled source frames"):
            validate_temporal_motif_fixture(replace(fixture, train=bad_train))


@unittest.skipUnless(HAS_NUMPY and HAS_TORCH, "NumPy and Torch are optional")
class Loop48StageCModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import torch

        torch.set_num_threads(1)
        torch.manual_seed(4850)

    def test_exact_parameter_counts_shapes_and_output_lengths(self):
        import torch

        from neurodecodekit.models.tiny_causal_temporal_ctc import (
            build_tiny_causal_temporal_ctc,
            registered_temporal_ctc_config,
        )

        values = torch.zeros((2, 102, 65), dtype=torch.float32)
        candidate = build_tiny_causal_temporal_ctc(
            registered_temporal_ctc_config("L48C-SYN-OPT0", architecture="candidate")
        )
        ablation = build_tiny_causal_temporal_ctc(
            registered_temporal_ctc_config("L48C-SYN-OPT0", architecture="ablation")
        )
        self.assertEqual(sum(value.numel() for value in candidate.parameters()), 7692)
        self.assertEqual(sum(value.numel() for value in ablation.parameters()), 7568)
        self.assertEqual(tuple(candidate(values).shape), (2, 17, 28))
        self.assertEqual(tuple(ablation(values).shape), (2, 17, 28))

    def test_candidate_has_zero_right_context(self):
        import torch

        from neurodecodekit.models.tiny_causal_temporal_ctc import (
            build_tiny_causal_temporal_ctc,
            registered_temporal_ctc_config,
        )

        torch.manual_seed(4850)
        model = build_tiny_causal_temporal_ctc(
            registered_temporal_ctc_config("L48C-SYN-OPT0", architecture="candidate")
        )
        values = torch.randn((2, 102, 80), dtype=torch.float32)
        mutated = values.clone()
        mutated[:, :, 33:] = mutated[:, :, 33:] * -3.0 + 2.0
        with torch.no_grad():
            baseline = model(values)
            changed = model(mutated)
        self.assertTrue(torch.equal(baseline[:, :9], changed[:, :9]))

    def test_ablation_cannot_observe_registered_motifs(self):
        import torch

        from neurodecodekit.models.tiny_causal_temporal_ctc import (
            build_tiny_causal_temporal_ctc,
            registered_temporal_ctc_config,
        )
        from neurodecodekit.training.temporal_motif_sentences import (
            generate_registered_temporal_motif_fixture,
        )

        fixture = generate_registered_temporal_motif_fixture()
        model = build_tiny_causal_temporal_ctc(
            registered_temporal_ctc_config("L48C-SYN-OPT0", architecture="ablation")
        )
        with torch.no_grad():
            logits = model(torch.from_numpy(fixture.selection.signals))
        for row in logits[1:]:
            self.assertTrue(torch.equal(logits[0], row))

    def test_numeric_checkpoint_replays_and_malformed_cache_is_rejected(self):
        import numpy as np
        import torch

        from neurodecodekit.models.tiny_causal_temporal_ctc import (
            build_tiny_causal_temporal_ctc,
            load_tiny_causal_temporal_checkpoint,
            registered_temporal_ctc_config,
            save_tiny_causal_temporal_checkpoint,
        )

        config = registered_temporal_ctc_config("L48C-SYN-OPT0", architecture="candidate")
        model = build_tiny_causal_temporal_ctc(config)
        values = torch.randn((2, 102, 65), dtype=torch.float32)
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint = Path(temp_dir) / "model.npz"
            save_tiny_causal_temporal_checkpoint(
                checkpoint,
                model=model,
                config=config,
                metadata={"qualification_only": True},
            )
            loaded, loaded_config, metadata = load_tiny_causal_temporal_checkpoint(checkpoint)
            self.assertEqual(loaded_config, config)
            self.assertTrue(metadata["qualification_only"])
            with torch.no_grad():
                self.assertTrue(torch.equal(model(values), loaded(values)))
            malformed = Path(temp_dir) / "malformed.npz"
            np.savez_compressed(malformed, weight=np.zeros(1, dtype="float32"))
            with self.assertRaisesRegex(ValueError, "lacks metadata"):
                load_tiny_causal_temporal_checkpoint(malformed)

    def test_prediction_rejects_nonzero_padding(self):
        import numpy as np

        from neurodecodekit.models.tiny_causal_temporal_ctc import (
            build_tiny_causal_temporal_ctc,
            predict_tiny_causal_temporal_ctc,
            registered_temporal_ctc_config,
        )

        model = build_tiny_causal_temporal_ctc(
            registered_temporal_ctc_config("L48C-SYN-OPT0", architecture="candidate")
        )
        values = np.zeros((1, 102, 20), dtype="float32")
        values[0, 0, 19] = 1.0
        with self.assertRaisesRegex(ValueError, "padding"):
            predict_tiny_causal_temporal_ctc(
                model,
                signals=values,
                input_lengths=np.asarray([16]),
            )


if __name__ == "__main__":
    unittest.main()
