import importlib.util
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.cli import build_parser


NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class LazyBackendGateTests(unittest.TestCase):
    def test_isolated_gate_preserves_rows_and_parks_unneeded_backend(self):
        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.cache.signal_representation import (
            save_signal_representation_cache,
        )
        from neurodecodekit.experiments.lazy_backend_gate import run_lazy_backend_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            packed = root / "source_qint8.npz"
            _write_sentence_cache(source)
            save_signal_representation_cache(
                packed,
                source_cache=load_sentence_npz_cache(source),
                encoding="qint8",
            )

            report = run_lazy_backend_gate(
                cache_paths=[source, packed],
                out_dir=root / "gate",
                row_counts=[1, 2],
                repetitions=2,
                max_full_load_ms=10_000,
                max_partial_load_ms=10_000,
                max_peak_rss_mb=4096,
                revisit_cache_mb=1024,
            )

            self.assertEqual(
                report["proof_posture"],
                "current_real_cache_npz_access_gate_no_zarr_install",
            )
            self.assertEqual(len(report["caches"]), 2)
            self.assertTrue(report["consistency"]["all_gate_checks_pass"])
            self.assertTrue(report["consistency"]["all_decoded_signal_hashes_exact"])
            self.assertEqual(
                report["decision"]["status"],
                "park_optional_zarr_npz_not_materially_limiting_current_caches",
            )
            self.assertEqual(report["resources"]["new_cache_or_backend_bytes"], 0)
            self.assertTrue((root / "gate" / "gate.json").exists())
            self.assertTrue((root / "gate" / "gate.md").exists())
            for cache in report["caches"]:
                self.assertTrue(cache["full_load"]["exact_decoded_signal_match"])
                self.assertTrue(
                    all(row["exact_decoded_signal_match"] for row in cache["partial_reads"])
                )

            with self.assertRaisesRegex(FileExistsError, "already exist"):
                run_lazy_backend_gate(
                    cache_paths=[source],
                    out_dir=root / "gate",
                    row_counts=[1],
                    repetitions=1,
                )

    def test_threshold_failure_justifies_comparison_without_installing_backend(self):
        from neurodecodekit.experiments.lazy_backend_gate import run_lazy_backend_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            _write_sentence_cache(source)

            report = run_lazy_backend_gate(
                cache_paths=[source],
                out_dir=root / "gate",
                row_counts=[1],
                repetitions=1,
                max_full_load_ms=1e-9,
                max_partial_load_ms=10_000,
                max_peak_rss_mb=4096,
                revisit_cache_mb=1024,
            )

            self.assertFalse(report["consistency"]["all_gate_checks_pass"])
            self.assertEqual(
                report["decision"]["status"], "bounded_zarr_comparison_justified"
            )
            self.assertEqual(
                report["decision"]["backend_action"],
                "benchmark_optional_zarr_before_implementation",
            )

    def test_validation_and_cli_contract(self):
        from neurodecodekit.experiments.lazy_backend_gate import (
            _normalize_row_counts,
        )

        self.assertEqual(_normalize_row_counts([8, 1]), [1, 8])
        for invalid in ([], [0, 1], [1, 1], [2, 8]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                _normalize_row_counts(invalid)

        args = build_parser().parse_args(
            [
                "lazy-backend-gate",
                "--cache",
                "base.npz",
                "base_qint8.npz",
                "--out-dir",
                "gate",
            ]
        )
        self.assertEqual(args.row_counts, [1, 8])
        self.assertEqual(args.repetitions, 5)
        self.assertEqual(args.max_full_load_ms, 250.0)
        self.assertEqual(args.max_partial_load_ms, 100.0)
        self.assertEqual(args.max_peak_rss_mb, 512.0)
        self.assertEqual(args.revisit_cache_mb, 128.0)


def _write_sentence_cache(path: Path) -> None:
    import numpy as np

    from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
    from neurodecodekit.preprocess.ctc_text import encode_ctc_text

    input_lengths = np.asarray([20, 18], dtype="int32")
    signals = np.zeros((2, 3, 20), dtype="float32")
    for row_index, length in enumerate(input_lengths.tolist()):
        base = np.linspace(-1.0, 1.0, length, dtype="float32")
        for channel_index in range(3):
            signals[row_index, channel_index, :length] = base * (channel_index + 1)
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
        trial_indices=np.asarray([30, 31], dtype="int32"),
        sentence_start_sec=np.asarray([1.0, 3.0], dtype="float64"),
        sentence_end_sec=np.asarray([1.2, 3.18], dtype="float64"),
        channel_names=np.asarray(["M1", "M2", "M3"], dtype="U"),
        metadata={
            "kind": "test_real_sentence_cache",
            "extraction_params": {"sfreq": 100.0, "clamp": 5.0},
            "source_files": {"raw": "fixture.fif", "events": "fixture.mat"},
            "warnings": ["test_only"],
        },
    )


if __name__ == "__main__":
    unittest.main()
