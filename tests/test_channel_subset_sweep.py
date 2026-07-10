import importlib.util
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.cli import build_parser


NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class ChannelSubsetSweepTests(unittest.TestCase):
    def test_spatial_order_is_deterministic_and_nested(self):
        import numpy as np

        from neurodecodekit.experiments.channel_subset_sweep import (
            spatial_farthest_point_order,
        )

        positions = np.asarray(
            [
                [-1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, -1.0, 0.0],
            ]
        )
        order = spatial_farthest_point_order(positions, ["A", "B", "C", "D"])

        self.assertEqual(order, [0, 1, 2, 3])
        self.assertEqual(set(order[:2]), {0, 1})
        self.assertTrue(set(order[:2]).issubset(order[:3]))

    def test_selection_metrics_preserve_colocated_zero_distance(self):
        import numpy as np

        from neurodecodekit.experiments.channel_subset_sweep import analyze_selection

        result = analyze_selection(
            positions=np.asarray([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
            variances=np.asarray([1.0, 1.0, 1.0]),
            selected_indices=[0, 1],
        )

        self.assertEqual(result["selected_min_pairwise_distance_m"], 0.0)

    def test_runner_writes_valid_subsets_and_exact_identity(self):
        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.experiments.channel_subset_sweep import (
            run_channel_subset_sweep,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "base.npz"
            _write_geometry_cache(source_path)

            report = run_channel_subset_sweep(
                cache_path=source_path,
                out_dir=root / "sweep",
                channel_counts=[4, 2],
                strategies=["spatial-fps", "variance", "random", "first"],
                seed=5,
                max_output_mb=10,
            )

            self.assertEqual(report["proof_posture"], "single_block_real_data_resource_and_proxy_study")
            self.assertEqual(len(report["rows"]), 8)
            self.assertTrue(report["consistency"]["all_written_identity_arrays_match_base"])
            self.assertTrue(
                report["consistency"]["all_written_signal_values_match_base_subsets"]
            )
            self.assertEqual(
                report["decision"]["status"],
                "carry_two_candidates_to_future_accuracy_test",
            )
            self.assertIn("no_decoder_was_trained_or_evaluated", report["warnings"])
            self.assertTrue((root / "sweep" / "sweep.json").exists())
            self.assertTrue((root / "sweep" / "sweep.md").exists())

            subset = load_sentence_npz_cache(root / "sweep" / "subset_variance_2ch.npz")
            self.assertEqual(subset.summary.n_channels, 2)
            self.assertEqual(subset.channel_names.tolist(), ["M4", "M5"])
            self.assertEqual(subset.trial_indices.tolist(), [10, 11])
            self.assertEqual(subset.metadata["channel_subset"]["strategy"], "variance")

    def test_storage_cap_refuses_before_creating_output_directory(self):
        from neurodecodekit.experiments.channel_subset_sweep import (
            run_channel_subset_sweep,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "base.npz"
            _write_geometry_cache(source_path)
            output_dir = root / "too-large"

            with self.assertRaisesRegex(ValueError, "Projected uncompressed"):
                run_channel_subset_sweep(
                    cache_path=source_path,
                    out_dir=output_dir,
                    channel_counts=[4, 2],
                    max_output_mb=0.0001,
                )

            self.assertFalse(output_dir.exists())

    def test_missing_geometry_is_rejected_with_reextract_instruction(self):
        from neurodecodekit.experiments.channel_subset_sweep import (
            run_channel_subset_sweep,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "base.npz"
            _write_geometry_cache(source_path, include_geometry=False)

            with self.assertRaisesRegex(ValueError, "Re-extract"):
                run_channel_subset_sweep(
                    cache_path=source_path,
                    out_dir=root / "sweep",
                    channel_counts=[2],
                )

    def test_validation_and_cli_contract(self):
        from neurodecodekit.experiments.channel_subset_sweep import (
            normalize_channel_counts,
            normalize_strategies,
        )

        self.assertEqual(normalize_channel_counts([2, 4], 6), [4, 2])
        self.assertEqual(normalize_strategies(["variance", "first"]), ["variance", "first"])
        for invalid in ([0], [6], [2, 2], []):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                normalize_channel_counts(invalid, 6)
        with self.assertRaises(ValueError):
            normalize_strategies(["unknown"])

        args = build_parser().parse_args(
            [
                "channel-subset-sweep",
                "--cache",
                "base.npz",
                "--out-dir",
                "sweep",
            ]
        )
        self.assertEqual(args.counts, [76, 51, 25, 16, 8])
        self.assertEqual(args.max_output_mb, 128.0)


def _write_geometry_cache(path: Path, *, include_geometry: bool = True) -> None:
    import numpy as np

    from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
    from neurodecodekit.preprocess.ctc_text import encode_ctc_text

    names = [f"M{index}" for index in range(6)]
    positions = [
        [1.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, -1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, -1.0],
    ]
    input_lengths = np.asarray([10, 8], dtype="int32")
    signals = np.zeros((2, 6, 10), dtype="float32")
    for row_index, length in enumerate(input_lengths.tolist()):
        base = np.linspace(-1.0, 1.0, length, dtype="float32")
        for channel_index in range(6):
            signals[row_index, channel_index, :length] = base * (channel_index + 1)
    targets = ["AB", "BA"]
    encoded = [encode_ctc_text(value) for value in targets]
    target_ids = np.asarray(encoded, dtype="int16")
    metadata = {
        "kind": "test_real_geometry_cache",
        "source_files": {"raw": "fixture.fif", "events": "fixture.mat"},
        "extraction_params": {"sfreq": 100.0, "picks": "mag", "max_channels": 6},
        "channels": {
            "n_channels": 6,
            "names": names,
            "position_units": "m",
        },
        "warnings": ["test_only"],
    }
    if include_geometry:
        metadata["channels"]["geometry"] = [
            {
                "name": name,
                "type": "mag",
                "position_m": position,
                "coord_frame": 1,
                "coil_type": 3024,
                "unit": 112,
            }
            for name, position in zip(names, positions, strict=True)
        ]
    save_sentence_npz_cache(
        path,
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_ids,
        target_lengths=np.asarray([2, 2], dtype="int32"),
        target_texts=np.asarray(targets, dtype="U"),
        reference_texts=np.asarray(targets, dtype="U"),
        mat_response_texts=np.asarray(targets, dtype="U"),
        trial_indices=np.asarray([10, 11], dtype="int32"),
        sentence_start_sec=np.asarray([1.0, 3.0], dtype="float64"),
        sentence_end_sec=np.asarray([2.0, 3.8], dtype="float64"),
        channel_names=np.asarray(names, dtype="U"),
        metadata=metadata,
    )


if __name__ == "__main__":
    unittest.main()
