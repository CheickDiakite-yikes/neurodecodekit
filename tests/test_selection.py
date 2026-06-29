import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets.manifest import build_manifest_from_paths, write_jsonl
from neurodecodekit.datasets.selection import SelectionError, read_selection, select_tiny_records, write_selection


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
            self.assertEqual(loaded.safety_warnings, selection.safety_warnings)

    def test_prefers_smallest_known_meg_block_with_exact_log(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif\t2000",
            "pinet2024_public/MEG/logs/S1_block1.mat\t10",
            "pinet2024_public/MEG/FIF/S1/block2.fif\t100",
            "pinet2024_public/MEG/logs/S1_block2.mat\t10",
        ])

        selection = select_tiny_records(records, modality="MEG", subject="S1", blocks=1)

        self.assertIn("pinet2024_public/MEG/FIF/S1/block2.fif", selection.allow_patterns)
        self.assertIn("pinet2024_public/MEG/logs/S1_block2.mat", selection.allow_patterns)
        self.assertEqual(selection.estimated_bytes, 110)

    def test_rejects_selection_exceeding_max_files(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif\t100",
            "pinet2024_public/MEG/logs/S1_block1_a.mat\t10",
            "pinet2024_public/MEG/logs/S1_block1_b.mat\t10",
        ])

        with self.assertRaisesRegex(SelectionError, "exceeding max_files"):
            select_tiny_records(records, modality="MEG", subject="S1", blocks=1, max_files=2)

    def test_rejects_selection_exceeding_max_total_bytes(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif\t1000",
            "pinet2024_public/MEG/logs/S1_block1.mat\t100",
        ])

        with self.assertRaisesRegex(SelectionError, "exceeding max_total_bytes"):
            select_tiny_records(records, modality="MEG", subject="S1", blocks=1, max_total_bytes=500)

    def test_unknown_sizes_are_warned_but_allowed_for_dry_run_planning(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif",
            "pinet2024_public/MEG/logs/S1_block1.mat",
        ])

        selection = select_tiny_records(records, modality="MEG", subject="S1", blocks=1)

        self.assertIsNone(selection.estimated_bytes)
        self.assertEqual(selection.missing_size_count, 2)
        self.assertIn("size_unknown_for_2_files", selection.safety_warnings)

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
