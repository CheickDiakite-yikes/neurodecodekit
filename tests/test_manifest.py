import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets.manifest import (
    build_manifest_from_paths,
    infer_spanishbcbl_record,
    read_jsonl,
    summarize_manifest,
    write_jsonl,
)


class ManifestTests(unittest.TestCase):
    def test_infer_meg_fif_block(self):
        record = infer_spanishbcbl_record("pinet2024_public/MEG/FIF/S1/block1.fif")
        self.assertEqual(record.modality, "MEG")
        self.assertEqual(record.subject, "S1")
        self.assertEqual(record.block, "block1")
        self.assertEqual(record.kind, "raw")
        self.assertEqual(record.extension, ".fif")

    def test_infer_log_mat(self):
        record = infer_spanishbcbl_record("pinet2024_public/MEG/logs/S18_block2.mat")
        self.assertEqual(record.modality, "MEG")
        self.assertEqual(record.subject, "S18")
        self.assertEqual(record.block, "block2")
        self.assertEqual(record.kind, "log")

    def test_build_and_roundtrip(self):
        paths = [
            "pinet2024_public/MEG/FIF/S1/block1.fif",
            "pinet2024_public/MEG/logs/S1_block1.mat",
            "pinet2024_public/EEG/EEG/S2/eeg.vhdr",
        ]
        records = build_manifest_from_paths(paths)
        self.assertEqual(len(records), 3)
        summary = summarize_manifest(records)
        self.assertEqual(summary["by_modality"]["MEG"], 2)
        self.assertEqual(summary["by_modality"]["EEG"], 1)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "manifest.jsonl"
            write_jsonl(records, out)
            loaded = read_jsonl(out)
            self.assertEqual([r.path for r in loaded], paths)
            # Verify JSONL lines are valid JSON.
            for line in out.read_text().splitlines():
                json.loads(line)


if __name__ == "__main__":
    unittest.main()
