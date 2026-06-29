import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets.manifest import build_manifest_from_paths, write_jsonl
from neurodecodekit.datasets.selection import read_selection, select_tiny_records, write_selection


class SelectionTests(unittest.TestCase):
    def test_selects_one_meg_block_plus_matching_log(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif",
            "pinet2024_public/MEG/FIF/S1/block2.fif",
            "pinet2024_public/MEG/logs/S1_block1.mat",
            "pinet2024_public/MEG/logs/S1_block2.mat",
            "pinet2024_public/MEG/FIF/S2/block1.fif",
        ])
        selection = select_tiny_records(records, modality="MEG", subject="S1", blocks=1)
        paths = selection.allow_patterns
        self.assertIn("pinet2024_public/MEG/FIF/S1/block1.fif", paths)
        self.assertIn("pinet2024_public/MEG/logs/S1_block1.mat", paths)
        self.assertNotIn("pinet2024_public/MEG/FIF/S1/block2.fif", paths)
        self.assertNotIn("pinet2024_public/MEG/logs/S1_block2.mat", paths)

    def test_selection_roundtrip(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif",
            "pinet2024_public/MEG/logs/S1_block1.mat",
        ])
        selection = select_tiny_records(records)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "selection.json"
            write_selection(selection, path)
            loaded = read_selection(path)
            self.assertEqual(loaded.repo_id, selection.repo_id)
            self.assertEqual(loaded.allow_patterns, selection.allow_patterns)

    def test_manifest_to_selection_cli_input_shape(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S3/block1.fif",
            "pinet2024_public/MEG/logs/S3_block1.mat",
        ])
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.jsonl"
            write_jsonl(records, manifest)
            self.assertTrue(manifest.exists())


if __name__ == "__main__":
    unittest.main()
