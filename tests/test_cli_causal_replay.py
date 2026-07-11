import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class CausalReplayCliTests(unittest.TestCase):
    def test_causal_replay_gate_writes_bounded_reports_and_refuses_collision(self):
        from neurodecodekit.training.synthetic_sentences import save_synthetic_sentence_npz

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            out_json = root / "gate.json"
            out_md = root / "gate.md"
            save_synthetic_sentence_npz(
                source,
                sentences=16,
                channels=5,
                letter_classes=4,
                sfreq=100,
                seed=31,
            )
            args = [
                "causal-replay-gate",
                "--source-cache",
                str(source),
                "--out-json",
                str(out_json),
                "--out-md",
                str(out_md),
                "--max-items",
                "32",
                "--max-source-mb",
                "1",
                "--max-samples-per-item",
                "128",
                "--max-chunk-samples",
                "128",
                "--max-tokens-per-item",
                "128",
                "--max-state-kib",
                "1",
                "--max-report-mb",
                "1",
            ]
            with redirect_stdout(io.StringIO()):
                code = main(args)
            report = json.loads(out_json.read_text(encoding="utf-8"))
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                collision_code = main(args)

        self.assertEqual(
            code,
            0,
            {
                "failed_gate_checks": report["failed_gate_checks"],
                "max_offline_absolute_error": report["summary"][
                    "max_offline_absolute_error"
                ],
                "runtime_sec": report["resources"]["runtime_sec"],
                "peak_rss_bytes": report["resources"]["peak_rss_bytes"],
            },
        )
        self.assertEqual(collision_code, 2)
        self.assertTrue(report["gate_passed"])
        self.assertEqual(report["proof_posture"], "synthetic_causal_frame_replay_only_no_decoder")
        self.assertEqual(report["summary"]["schedules_passed"], 5)
        self.assertEqual(report["summary"]["decoder_runs"], 0)
        self.assertIn("Refusing to replace", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
