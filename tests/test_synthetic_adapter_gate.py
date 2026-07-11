import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.experiments.synthetic_adapter_gate import run_synthetic_adapter_gate


@unittest.skipUnless(importlib.util.find_spec("torch"), "Torch not installed")
@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SyntheticAdapterGateTests(unittest.TestCase):
    def test_gate_selects_adapter_without_real_data_and_stays_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "gate"
            report = run_synthetic_adapter_gate(
                out_dir=out_dir,
                sentences=48,
                channels=5,
                letter_classes=4,
                seed=23,
                epochs=40,
                bootstrap_iterations=100,
                max_output_mb=1.0,
            )
            disk_report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))

            self.assertTrue(report["decision"]["gate_passed"])
            self.assertEqual(
                report["protocol"]["selected_adapter_before_holdout"],
                "robust_channel_affine",
            )
            self.assertFalse(report["protocol"]["real_session2_rows_loaded"])
            self.assertFalse(report["protocol"]["real_source_test_rows_loaded"])
            self.assertFalse(report["adapter"]["target_labels_used"])
            self.assertLess(
                report["holdout"]["robust_channel_affine"]["corpus_cer"],
                report["holdout"]["identity"]["corpus_cer"],
            )
            self.assertEqual(report["resources"]["new_cache_bytes"], 0)
            self.assertLess(report["resources"]["total_artifact_bytes"], 1024 * 1024)
            self.assertEqual(disk_report["decision"], report["decision"])

            with self.assertRaises(FileExistsError):
                run_synthetic_adapter_gate(
                    out_dir=out_dir,
                    sentences=48,
                    channels=5,
                    letter_classes=4,
                    epochs=1,
                    bootstrap_iterations=100,
                )


if __name__ == "__main__":
    unittest.main()
