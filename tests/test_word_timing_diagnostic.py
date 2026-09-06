"""Generated timing/index and file-scope checks, without real data or weights."""

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "timing_test", ROOT / "src/neurodecodekit/experiments/word_timing_diagnostic.py"
)
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


class TimingTests(unittest.TestCase):
    def test_marker_origin_and_unchanged_full_window_exclusion(self):
        text = "\n".join(
            [
                "Mk1=Comment,Wait,1,100,0",
                "Mk2=Comment,up,101,1000,0",
                "Mk3=Comment,left,1201,999,0",
                "Mk4=Comment,down,2301,1000,0",
                "Mk5=Comment,right,3501,1000,0",
            ]
        )
        rows, dropped = t.word_events(text, 4300)
        self.assertEqual(rows, [("0", "up", 100, 600), ("2", "down", 2300, 2800)])
        self.assertEqual(dropped, 2)

    def test_precise_stage_inputs_exclude_completed_tests(self):
        root = ROOT / ".codex_work/generated-timing-test"
        reads, files = t.permissions("prepare", root)
        raw = [p for p in files if "raw" in p.parts]
        self.assertEqual(len(raw), 144)
        self.assertFalse(reads)
        self.assertEqual(
            {next(x for x in p.parts if x.startswith("ses-")) for p in raw},
            {"ses-0", "ses-1", "ses-3", "ses-4"},
        )
        for role in ("features", "predict", "score"):
            reads, files = t.permissions(role, root)
            self.assertFalse(any("raw" in p.parts for p in reads + files))
            self.assertFalse(
                any("targets.json" in str(p) or "test.npy" in str(p) for p in reads + files)
            )
        reads, files = t.permissions("score", root)
        self.assertIn(t.LATE, files)
        self.assertNotIn(t.BASE / "features", reads)

    @unittest.skipUnless(importlib.util.find_spec("scipy"), "optional scipy")
    def test_channel_scaling_and_no_late_to_early_filter_mixing(self):
        import numpy as np
        from scipy.signal import butter, sosfiltfilt

        rng = np.random.default_rng(7)
        raw = rng.normal(size=(1200, 8)).astype(np.float32)
        scale = np.arange(1, 9)[:, None] * 1e-6
        sos = butter(4, [1, 30], fs=250, btype="bandpass", output="sos")
        a = t.filtered_early(raw, 100, scale, sos)
        expected = sosfiltfilt(sos, raw[100:600].T.astype(float) * scale, axis=-1).astype(
            np.float32
        )
        np.testing.assert_array_equal(a, expected)
        raw[:100] = 1e10
        raw[600:] = -1e10
        np.testing.assert_array_equal(a, t.filtered_early(raw, 100, scale, sos))


if __name__ == "__main__":
    unittest.main()
