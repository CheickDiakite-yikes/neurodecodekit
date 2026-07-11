import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

if importlib.util.find_spec("numpy") is None:
    raise unittest.SkipTest("NumPy not installed")

import numpy as np

from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
from neurodecodekit.cli import build_parser
from neurodecodekit.experiments.sampling_rate_sweep import (
    build_sampling_rate_report,
    normalize_sampling_rates,
    run_sampling_rate_sweep,
    temporal_conv_output_length,
)
from neurodecodekit.preprocess.ctc_text import encode_ctc_text


class SamplingRateSweepTests(unittest.TestCase):
    def test_runner_orders_rates_writes_reports_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "block1.fif"
            events = root / "logs.mat"
            raw.touch()
            events.touch()
            calls = []

            def fake_worker(*, rate_hz, cache_path, summary_path, log_path, options):
                calls.append(rate_hz)
                _write_sentence_cache(
                    cache_path,
                    rate_hz=rate_hz,
                    raw_path=options["raw_path"],
                    events_path=options["events_path"],
                )
                summary = {
                    "sfreq": rate_hz,
                    "runtime_sec": rate_hz / 100.0,
                    "peak_rss_bytes": int(rate_hz * 1024),
                }
                summary_path.write_text(json.dumps(summary), encoding="utf-8")
                log_path.write_text("fake isolated worker\n", encoding="utf-8")
                return summary

            report = run_sampling_rate_sweep(
                raw_path=raw,
                events_path=events,
                out_dir=root / "sweep",
                rates_hz=[25, 100, 50],
                extraction_worker=fake_worker,
            )

            self.assertEqual(calls, [100.0, 50.0, 25.0])
            self.assertEqual([row["rate_hz"] for row in report["rates"]], calls)
            self.assertTrue(report["consistency"]["all_identity_fields_match"])
            self.assertEqual(
                [row["ctc_infeasible_rows_stride_1"] for row in report["rates"]],
                [0, 0, 0],
            )
            self.assertAlmostEqual(
                report["rates"][1]["valid_timepoint_retention_vs_reference"],
                0.5,
            )
            self.assertAlmostEqual(
                report["rates"][2]["valid_timepoint_retention_vs_reference"],
                0.25,
                delta=0.002,
            )
            self.assertEqual(
                report["decision"]["status"],
                "resource_characterized_no_rate_selected",
            )
            self.assertEqual(
                report["rates"][0]["official_v2_ctc_feasible_rows"],
                2,
            )
            self.assertTrue((root / "sweep" / "sweep.json").exists())
            markdown = (root / "sweep" / "sweep.md").read_text(encoding="utf-8")
            self.assertIn("no model training", markdown)
            self.assertIn("100 Hz", markdown)
            self.assertTrue((root / "sweep" / "sentence_25hz.metadata.json").exists())
            with self.assertRaises(FileExistsError):
                run_sampling_rate_sweep(
                    raw_path=raw,
                    events_path=events,
                    out_dir=root / "sweep",
                    extraction_worker=fake_worker,
                )

    def test_report_flags_text_identity_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifacts = {}
            summaries = {}
            for rate, targets in ((100.0, ["AB", "BA"]), (50.0, ["AB", "CA"])):
                cache = root / f"{rate:g}.npz"
                _write_sentence_cache(
                    cache,
                    rate_hz=rate,
                    raw_path=root / "block1.fif",
                    events_path=root / "logs.mat",
                    target_texts=targets,
                )
                artifacts[rate] = {
                    "cache": cache,
                    "summary": root / f"{rate:g}.json",
                    "metadata": root / f"{rate:g}.metadata.json",
                    "log": root / f"{rate:g}.log",
                }
                summaries[rate] = {
                    "sfreq": rate,
                    "runtime_sec": 1.0,
                    "peak_rss_bytes": 1024,
                }

            report = build_sampling_rate_report(
                raw_path=root / "block1.fif",
                events_path=root / "logs.mat",
                rates_hz=[100, 50],
                artifacts=artifacts,
                extraction_summaries=summaries,
                total_runtime_sec=2.0,
                configured_h_freq=45.0,
            )

            self.assertFalse(report["consistency"]["exact_identity"]["typed_targets"])
            self.assertFalse(report["consistency"]["all_identity_fields_match"])
            self.assertIn(
                "rate_caches_do_not_share_exact_trial_text_channel_identity",
                report["warnings"],
            )

    def test_rate_validation_and_cli_contract(self):
        self.assertEqual(normalize_sampling_rates([25, 100, 50]), [100.0, 50.0, 25.0])
        for invalid in ([100], [100, 100], [100, 0], [100, float("nan")]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                normalize_sampling_rates(invalid)

        parser = build_parser()
        extract = parser.parse_args(
            [
                "extract-sentence-cache",
                "--raw",
                "raw.fif",
                "--events",
                "events.mat",
                "--out",
                "cache.npz",
                "--summary-json",
                "summary.json",
            ]
        )
        self.assertEqual(extract.summary_json, "summary.json")
        sweep = parser.parse_args(
            [
                "sampling-rate-sweep",
                "--raw",
                "raw.fif",
                "--events",
                "events.mat",
                "--out-dir",
                "sweep",
            ]
        )
        self.assertEqual(sweep.rates, [100.0, 50.0, 25.0])

        self.assertEqual(
            temporal_conv_output_length(329, kernel_size=16, stride=4),
            79,
        )
        self.assertEqual(
            temporal_conv_output_length(83, kernel_size=16, stride=4),
            17,
        )
        self.assertEqual(
            temporal_conv_output_length(10, kernel_size=16, stride=4),
            0,
        )
        with self.assertRaises(ValueError):
            temporal_conv_output_length(0, kernel_size=16, stride=4)

    def test_runner_rejects_preprocessing_options_it_cannot_replay_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "block1.fif"
            events = root / "logs.mat"
            raw.touch()
            events.touch()
            with self.assertRaisesRegex(ValueError, "explicit max_channels"):
                run_sampling_rate_sweep(
                    raw_path=raw,
                    events_path=events,
                    out_dir=root / "uncapped",
                    max_channels=None,
                )
            with self.assertRaisesRegex(ValueError, "explicit numeric preprocessing"):
                run_sampling_rate_sweep(
                    raw_path=raw,
                    events_path=events,
                    out_dir=root / "no_lowpass",
                    h_freq=None,
                )


def _write_sentence_cache(
    path: Path,
    *,
    rate_hz: float,
    raw_path: Path,
    events_path: Path,
    target_texts=None,
):
    target_texts = list(target_texts or ["AB", "BA"])
    durations = [2.0, 1.5]
    input_lengths = np.asarray([round(rate_hz * value) for value in durations], dtype="int32")
    signals = np.zeros((2, 2, int(input_lengths.max())), dtype="float32")
    for row_index, length in enumerate(input_lengths.tolist()):
        values = np.linspace(-1.0, 1.0, 2 * length, dtype="float32").reshape(2, length)
        signals[row_index, :, :length] = values
    encoded = [encode_ctc_text(text) for text in target_texts]
    target_lengths = np.asarray([len(values) for values in encoded], dtype="int32")
    target_ids = np.zeros((2, int(target_lengths.max())), dtype="int16")
    for row_index, values in enumerate(encoded):
        target_ids[row_index, : len(values)] = values
    starts = np.asarray([0.0, 3.0], dtype="float64")
    ends = starts + np.asarray(durations, dtype="float64")
    save_sentence_npz_cache(
        path,
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_ids,
        target_lengths=target_lengths,
        target_texts=np.asarray(target_texts, dtype="U"),
        reference_texts=np.asarray(target_texts, dtype="U"),
        mat_response_texts=np.asarray(target_texts, dtype="U"),
        trial_indices=np.asarray([0, 1], dtype="int32"),
        sentence_start_sec=starts,
        sentence_end_sec=ends,
        channel_names=np.asarray(["MEG001", "MEG002"], dtype="U"),
        metadata={
            "kind": "real_fif_mat_continuous_sentences",
            "source_files": {"raw": str(raw_path), "events": str(events_path)},
            "extraction_params": {"sfreq": rate_hz, "h_freq": 45.0, "clamp": 5.0},
            "warnings": ["test_fixture"],
        },
    )


if __name__ == "__main__":
    unittest.main()
