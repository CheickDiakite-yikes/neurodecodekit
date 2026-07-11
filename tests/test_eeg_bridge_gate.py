import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets.manifest import build_manifest_from_paths, write_jsonl
from neurodecodekit.experiments.eeg_bridge_gate import run_eeg_bridge_gate


REVISION = "a" * 40
NEURO_AVAILABLE = all(
    importlib.util.find_spec(name) is not None for name in ("mne", "numpy", "scipy")
)


@unittest.skipUnless(NEURO_AVAILABLE, "MNE/NumPy/SciPy not installed")
class EEGBridgeGateTests(unittest.TestCase):
    def _write_manifest(self, root: Path) -> Path:
        records = build_manifest_from_paths([
            "EEG/EEG/002_DECOMEG_S1_9696_task1.vhdr\t11703",
            "EEG/EEG/002_DECOMEG_S1_9696_task1.eeg\t127482880",
            "EEG/EEG/002_DECOMEG_S1_9696_task1.vmrk\t89765",
            "EEG/logs/S2_session1_block1_list1.mat\t202313",
        ])
        manifest = root / "manifest.jsonl"
        write_jsonl(records, manifest)
        return manifest

    def test_gate_writes_bounded_dry_run_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._write_manifest(root)
            result = run_eeg_bridge_gate(
                manifest_path=manifest,
                out_dir=root / "out",
                revision=REVISION,
            )
            report = json.loads((root / "out" / "report.json").read_text())
            selection = json.loads((root / "out" / "selection.json").read_text())

        self.assertTrue(result["report"]["gate_passed"])
        self.assertEqual(report["selected_bundle"]["n_files"], 4)
        self.assertEqual(selection["estimated_bytes"], 127_786_661)
        self.assertEqual(result["audit"]["data_downloads"], 0)
        self.assertEqual(result["audit"]["raw_signal_reads"], 0)
        self.assertEqual(result["audit"]["new_cache_bytes"], 0)

    def test_gate_rejects_bundle_over_download_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._write_manifest(root)
            with self.assertRaisesRegex(ValueError, "exceeding max_total_bytes"):
                run_eeg_bridge_gate(
                    manifest_path=manifest,
                    out_dir=root / "out",
                    revision=REVISION,
                    max_download_mb=64,
                )

    def test_gate_rejects_mutable_or_short_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._write_manifest(root)
            with self.assertRaisesRegex(ValueError, "40-character"):
                run_eeg_bridge_gate(
                    manifest_path=manifest,
                    out_dir=root / "out",
                    revision="main",
                )

    def test_gate_refuses_nonempty_output_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._write_manifest(root)
            output = root / "out"
            output.mkdir()
            (output / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_eeg_bridge_gate(
                    manifest_path=manifest,
                    out_dir=output,
                    revision=REVISION,
                )
            self.assertEqual((output / "keep.txt").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
