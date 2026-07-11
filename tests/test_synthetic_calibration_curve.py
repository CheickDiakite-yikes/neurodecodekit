import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.experiments.synthetic_calibration_curve import (
    run_synthetic_calibration_curve,
)


@unittest.skipUnless(importlib.util.find_spec("torch"), "Torch not installed")
@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SyntheticCalibrationCurveTests(unittest.TestCase):
    def test_curve_is_unpaired_multi_shift_holdout_safe_and_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "curve"
            report = run_synthetic_calibration_curve(
                out_dir=out_dir,
                sentences=48,
                calibration_sentences=16,
                calibration_sizes=(1, 2, 4, 8, 16),
                shift_seeds=(101, 211),
                epochs=20,
                bootstrap_iterations=100,
                max_output_mb=2.0,
            )
            disk_report = json.loads((out_dir / "report.json").read_text())

            self.assertTrue(report["decision"]["gate_passed"])
            self.assertFalse(report["decision"]["real_session_adapter_authorized"])
            self.assertFalse(report["protocol"]["real_source_test_rows_loaded"])
            self.assertFalse(report["protocol"]["real_session2_rows_loaded"])
            self.assertFalse(report["unpaired_calibration"]["source_text_overlap"])
            self.assertFalse(report["unpaired_calibration"]["labels_used_for_adapter_fit"])
            self.assertEqual(len(report["validation_curve"]), 3 * 2 * 5)
            self.assertEqual(len(report["holdout"]["rows"]), 3 * 2)
            self.assertEqual(report["protocol"]["decoder_training_runs"], 2)
            self.assertEqual(report["resources"]["new_cache_bytes"], 0)
            self.assertLess(report["resources"]["total_artifact_bytes"], 2 * 1024 * 1024)
            self.assertEqual(disk_report["decision"], report["decision"])
            self.assertTrue((out_dir / "validation_curve.csv").is_file())
            self.assertTrue((out_dir / "holdout_results.csv").is_file())

            with self.assertRaises(FileExistsError):
                run_synthetic_calibration_curve(
                    out_dir=out_dir,
                    sentences=48,
                    calibration_sentences=16,
                    calibration_sizes=(1, 2, 4, 8, 16),
                    shift_seeds=(101, 211),
                    epochs=1,
                    bootstrap_iterations=100,
                )


if __name__ == "__main__":
    unittest.main()
