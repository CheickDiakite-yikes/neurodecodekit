import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class CausalReplayGateTests(unittest.TestCase):
    def _source(self, root: Path) -> Path:
        from neurodecodekit.training.synthetic_sentences import save_synthetic_sentence_npz

        source = root / "source.npz"
        save_synthetic_sentence_npz(
            source,
            sentences=16,
            channels=5,
            letter_classes=4,
            sfreq=100,
            seed=31,
        )
        return source

    def test_registered_schedules_pass_with_bounded_state_and_no_target_reads(self):
        import numpy as np

        from neurodecodekit.experiments.causal_replay_gate import (
            REGISTERED_SCHEDULES,
            TARGET_MEMBERS_NOT_OPENED,
            run_causal_replay_gate,
        )

        accessed = []
        real_load = np.load

        class TrackingNpz:
            def __init__(self, wrapped):
                self.wrapped = wrapped
                self.files = wrapped.files

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                self.wrapped.close()

            def __getitem__(self, name):
                accessed.append(name)
                return self.wrapped[name]

        def tracking_load(*args, **kwargs):
            return TrackingNpz(real_load(*args, **kwargs))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._source(root)
            out_json = root / "gate.json"
            out_md = root / "gate.md"
            with (
                patch("numpy.load", side_effect=tracking_load),
                patch(
                    "neurodecodekit.experiments.causal_replay_gate._peak_rss_bytes",
                    return_value=128 * 1024 * 1024,
                ),
            ):
                report = run_causal_replay_gate(
                    source_cache_path=source,
                    out_json_path=out_json,
                    out_markdown_path=out_md,
                    max_items=32,
                    max_source_mb=1,
                    max_samples_per_item=128,
                    max_chunk_samples=128,
                    max_tokens_per_item=128,
                    max_state_kib=1,
                    max_report_mb=1,
                )
            saved = json.loads(out_json.read_text(encoding="utf-8"))
            json_bytes = out_json.stat().st_size

        self.assertTrue(
            report["gate_passed"],
            {
                "failed_gate_checks": report["failed_gate_checks"],
                "max_offline_absolute_error": report["summary"][
                    "max_offline_absolute_error"
                ],
                "runtime_sec": report["resources"]["runtime_sec"],
                "peak_rss_bytes": report["resources"]["peak_rss_bytes"],
            },
        )
        self.assertTrue(all(report["gate_checks"].values()))
        self.assertEqual(report["failed_gate_checks"], [])
        self.assertEqual(report["summary"]["schedules_passed"], len(REGISTERED_SCHEDULES))
        self.assertTrue(report["summary"]["stream_schedule_bits_invariant"])
        self.assertLessEqual(report["summary"]["max_offline_absolute_error"], 2e-6)
        self.assertTrue(report["summary"]["timestamps_bitwise_equal"])
        self.assertTrue(report["summary"]["frame_grid_exact"])
        self.assertEqual(report["summary"]["producer_right_context_samples"], 0)
        self.assertLessEqual(
            report["summary"]["max_mutable_state_bytes"],
            report["summary"]["mutable_state_bound_bytes"],
        )
        self.assertEqual(report["summary"]["decoder_runs"], 0)
        self.assertEqual(report["summary"]["model_runs"], 0)
        self.assertEqual(report["summary"]["training_runs"], 0)
        self.assertEqual(report["summary"]["real_data_reads"], 0)
        self.assertEqual(report["summary"]["target_array_reads"], 0)
        self.assertTrue(set(TARGET_MEMBERS_NOT_OPENED).isdisjoint(accessed))
        self.assertEqual(set(accessed), {"metadata", "signals", "input_lengths", "sentence_start_sec"})
        by_name = {row["name"]: row for row in report["schedules"]}
        self.assertEqual(by_name["single-sample"]["schedule_delay_sec"]["max"], 0)
        self.assertEqual(by_name["stride-aligned"]["schedule_delay_sec"]["max"], 0)
        self.assertGreater(by_name["jittered"]["schedule_delay_sec"]["max"], 0)
        self.assertGreater(by_name["whole-item"]["schedule_delay_sec"]["max"], 0)
        self.assertEqual(saved["artifacts"]["json_bytes"], json_bytes)

    def test_canonical_payload_replays_and_outputs_refuse_collision(self):
        from neurodecodekit.experiments.causal_replay_gate import run_causal_replay_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._source(root)
            first = run_causal_replay_gate(
                source_cache_path=source,
                out_json_path=root / "first.json",
                max_items=32,
                max_source_mb=1,
                max_samples_per_item=128,
                max_chunk_samples=128,
                max_tokens_per_item=128,
            )
            second = run_causal_replay_gate(
                source_cache_path=source,
                out_json_path=root / "second.json",
                max_items=32,
                max_source_mb=1,
                max_samples_per_item=128,
                max_chunk_samples=128,
                max_tokens_per_item=128,
            )
            with self.assertRaisesRegex(FileExistsError, "Refusing to replace"):
                run_causal_replay_gate(
                    source_cache_path=source,
                    out_json_path=root / "first.json",
                    max_items=32,
                )
            with self.assertRaisesRegex(ValueError, "paths must be distinct"):
                run_causal_replay_gate(
                    source_cache_path=source,
                    out_json_path=root / "same-report",
                    out_markdown_path=root / "same-report",
                    max_items=32,
                )

        self.assertEqual(
            first["summary"]["canonical_stream_payload_sha256"],
            second["summary"]["canonical_stream_payload_sha256"],
        )

    def test_refuses_source_and_report_caps(self):
        from neurodecodekit.experiments.causal_replay_gate import run_causal_replay_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._source(root)
            with self.assertRaisesRegex(ValueError, "source cache"):
                run_causal_replay_gate(
                    source_cache_path=source,
                    out_json_path=root / "source-cap.json",
                    max_source_mb=0.00001,
                )
            with self.assertRaisesRegex(ValueError, "JSON report"):
                run_causal_replay_gate(
                    source_cache_path=source,
                    out_json_path=root / "report-cap.json",
                    max_items=32,
                    max_source_mb=1,
                    max_samples_per_item=128,
                    max_chunk_samples=128,
                    max_tokens_per_item=128,
                    max_report_mb=0.001,
                )
            self.assertFalse((root / "report-cap.json").exists())
            with patch(
                "neurodecodekit.experiments.causal_replay_gate._peak_rss_bytes",
                return_value=257 * 1024 * 1024,
            ):
                rss_report = run_causal_replay_gate(
                    source_cache_path=source,
                    out_json_path=root / "rss-cap.json",
                    max_items=32,
                    max_source_mb=1,
                    max_samples_per_item=128,
                    max_chunk_samples=128,
                    max_tokens_per_item=128,
                    max_peak_rss_mb=256,
                )
            self.assertFalse(rss_report["gate_passed"])
            self.assertIn(
                "peak_rss_within_cap_or_unavailable",
                rss_report["failed_gate_checks"],
            )

    def test_refuses_fractional_input_lengths(self):
        import numpy as np

        from neurodecodekit.experiments.causal_replay_gate import run_causal_replay_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._source(root)
            with np.load(source, allow_pickle=False) as data:
                payload = {name: data[name].copy() for name in data.files}
            payload["input_lengths"] = payload["input_lengths"].astype("float32") + 0.5
            malformed = root / "fractional-lengths.npz"
            np.savez_compressed(malformed, **payload)

            with self.assertRaisesRegex(ValueError, "integer dtype"):
                run_causal_replay_gate(
                    source_cache_path=malformed,
                    out_json_path=root / "gate.json",
                    max_items=32,
                    max_source_mb=1,
                    max_samples_per_item=128,
                    max_chunk_samples=128,
                    max_tokens_per_item=128,
                )


if __name__ == "__main__":
    unittest.main()
