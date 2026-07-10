import importlib.util
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.cli import build_parser


NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class PrecisionStorageSweepTests(unittest.TestCase):
    def test_runner_writes_five_variants_per_source_with_exact_identity(self):
        from neurodecodekit.cache.signal_representation import (
            load_signal_representation_cache,
        )
        from neurodecodekit.experiments.precision_storage_sweep import (
            run_precision_storage_sweep,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.npz"
            subset = root / "fps16.npz"
            _write_sentence_cache(base, channels=4)
            _write_sentence_cache(subset, channels=2)

            report = run_precision_storage_sweep(
                cache_paths=[base, subset],
                out_dir=root / "sweep",
                repetitions=2,
                max_output_mb=10,
            )

            self.assertEqual(
                report["proof_posture"],
                "single_block_multi_cache_representation_fidelity_study",
            )
            self.assertEqual(len(report["rows"]), 10)
            self.assertTrue(report["consistency"]["all_non_signal_arrays_exact"])
            self.assertTrue(report["consistency"]["all_semantic_metadata_exact"])
            self.assertTrue(report["consistency"]["all_padding_exact_zero"])
            self.assertEqual(
                report["consistency"]["integer_source_values_outside_clip_count"], 0
            )
            self.assertEqual(
                report["decision"]["status"],
                "retain_float32_default_carry_two_packed_candidates",
            )
            self.assertIn(
                report["decision"]["fidelity_candidate"],
                {"float16", "bfloat16", "qint16", "qint8"},
            )
            self.assertIn("no_decoder_was_trained_or_evaluated", report["warnings"])
            self.assertTrue((root / "sweep" / "sweep.json").exists())
            self.assertTrue((root / "sweep" / "sweep.md").exists())
            self.assertTrue(report["resources"]["total_artifacts_within_cap"])

            qint = load_signal_representation_cache(root / "sweep" / "base__qint8.npz")
            self.assertEqual(qint.representation_summary.encoding, "qint8")
            self.assertEqual(qint.trial_indices.tolist(), [20, 21])

            with self.assertRaisesRegex(FileExistsError, "already exist"):
                run_precision_storage_sweep(
                    cache_paths=[base, subset],
                    out_dir=root / "sweep",
                    repetitions=1,
                    max_output_mb=10,
                )

    def test_storage_cap_refuses_before_creating_output_directory(self):
        from neurodecodekit.experiments.precision_storage_sweep import (
            run_precision_storage_sweep,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            output = root / "too-large"
            _write_sentence_cache(source, channels=4)

            with self.assertRaisesRegex(ValueError, "Projected uncompressed"):
                run_precision_storage_sweep(
                    cache_paths=[source],
                    out_dir=output,
                    max_output_mb=0.0001,
                )

            self.assertFalse(output.exists())

    def test_reconstruction_metrics_exclude_padding_and_report_spectral_proxy(self):
        import numpy as np

        from neurodecodekit.experiments.precision_storage_sweep import (
            analyze_signal_reconstruction,
        )

        source = np.zeros((1, 1, 100), dtype="float32")
        source[0, 0, :80] = np.sin(2 * np.pi * 10 * np.arange(80) / 100)
        decoded = source.copy()
        decoded[0, 0, 20] += 0.1
        metrics = analyze_signal_reconstruction(
            source,
            decoded,
            np.asarray([80], dtype="int32"),
            channel_names=["M1"],
            sfreq=100.0,
        )

        self.assertEqual(metrics["valid_value_count"], 80)
        self.assertEqual(metrics["padding"]["value_count"], 20)
        self.assertEqual(metrics["padding"]["decoded_nonzero_count"], 0)
        self.assertGreater(metrics["rmse"], 0)
        self.assertGreater(
            metrics["spectral_bandpower"]["alpha_8_13"]["frequency_bin_observations"],
            0,
        )

    def test_variant_and_cli_contract(self):
        from neurodecodekit.experiments.precision_storage_sweep import normalize_variants

        self.assertEqual(
            normalize_variants(["float32", "qint8"]), ["float32", "qint8"]
        )
        with self.assertRaises(ValueError):
            normalize_variants([])
        with self.assertRaises(ValueError):
            normalize_variants(["float32", "float32"])
        with self.assertRaises(ValueError):
            normalize_variants(["unknown"])
        with self.assertRaises(ValueError):
            normalize_variants(["qint8"])
        with self.assertRaises(ValueError):
            normalize_variants(["float32"])

        args = build_parser().parse_args(
            [
                "precision-storage-sweep",
                "--cache",
                "base.npz",
                "fps16.npz",
                "variance16.npz",
                "--out-dir",
                "sweep",
            ]
        )
        self.assertEqual(args.cache, ["base.npz", "fps16.npz", "variance16.npz"])
        self.assertEqual(
            args.variants, ["float32", "float16", "bfloat16", "qint16", "qint8"]
        )
        self.assertEqual(args.repetitions, 3)
        self.assertEqual(args.max_output_mb, 96.0)
        self.assertFalse(args.allow_clipping)


def _write_sentence_cache(path: Path, *, channels: int) -> None:
    import numpy as np

    from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
    from neurodecodekit.preprocess.ctc_text import encode_ctc_text

    input_lengths = np.asarray([100, 90], dtype="int32")
    signals = np.zeros((2, channels, 100), dtype="float32")
    time_axis = np.arange(100, dtype="float32") / 100.0
    for row_index, length in enumerate(input_lengths.tolist()):
        for channel_index in range(channels):
            frequency = 3 + channel_index * 5
            signals[row_index, channel_index, :length] = (
                np.sin(2 * np.pi * frequency * time_axis[:length])
                * (1 + row_index * 0.1)
            )
    texts = ["AB", "BA"]
    target_ids = np.asarray([encode_ctc_text(value) for value in texts], dtype="int16")
    save_sentence_npz_cache(
        path,
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_ids,
        target_lengths=np.asarray([2, 2], dtype="int32"),
        target_texts=np.asarray(texts, dtype="U"),
        reference_texts=np.asarray(texts, dtype="U"),
        mat_response_texts=np.asarray(texts, dtype="U"),
        trial_indices=np.asarray([20, 21], dtype="int32"),
        sentence_start_sec=np.asarray([1.0, 3.0], dtype="float64"),
        sentence_end_sec=np.asarray([2.0, 3.9], dtype="float64"),
        channel_names=np.asarray([f"M{index}" for index in range(channels)], dtype="U"),
        metadata={
            "kind": "test_real_sentence_cache",
            "extraction_params": {"sfreq": 100.0, "clamp": 5.0},
            "source_files": {"raw": "fixture.fif", "events": "fixture.mat"},
            "warnings": ["test_only"],
        },
    )


if __name__ == "__main__":
    unittest.main()
