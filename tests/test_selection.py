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
        selection = select_tiny_records(records, revision="abc123")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "selection.json"
            write_selection(selection, path)
            loaded = read_selection(path)
            self.assertEqual(loaded.repo_id, selection.repo_id)
            self.assertEqual(loaded.revision, "abc123")
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

    def test_current_hf_selection_includes_primary_fif_and_split_continuation(self):
        records = build_manifest_from_paths([
            "MEG/FIF/07_10038/230503/block2-1.fif\t52452283",
            "MEG/FIF/07_10038/230503/block2.fif\t1903891995",
            "MEG/logs/S7-session1_block2_list2.mat\t294169",
        ])

        selection = select_tiny_records(records, modality="MEG", subject="S7", blocks=1)

        self.assertIn("MEG/FIF/07_10038/230503/block2.fif", selection.allow_patterns)
        self.assertIn("MEG/FIF/07_10038/230503/block2-1.fif", selection.allow_patterns)
        self.assertIn("MEG/logs/S7-session1_block2_list2.mat", selection.allow_patterns)
        self.assertEqual(selection.estimated_bytes, 1_956_638_447)

    def test_s21_block2_selection_matches_official_block2_2_override(self):
        records = build_manifest_from_paths([
            "MEG/FIF/21_3660/231204/block2.fif\t621506838",
            "MEG/FIF/21_3660/231204/block2_1.fif\t1812162350",
            "MEG/FIF/21_3660/231204/block2_2.fif\t1903915362",
            "MEG/FIF/21_3660/231204/block2_2-1.fif\t312688098",
            "MEG/logs/S21-session1_block2_list2.mat\t280082",
        ])

        selection = select_tiny_records(records, modality="MEG", subject="S21", blocks=1)

        self.assertIn("MEG/FIF/21_3660/231204/block2_2.fif", selection.allow_patterns)
        self.assertIn("MEG/FIF/21_3660/231204/block2_2-1.fif", selection.allow_patterns)
        self.assertIn("MEG/logs/S21-session1_block2_list2.mat", selection.allow_patterns)
        self.assertNotIn("MEG/FIF/21_3660/231204/block2.fif", selection.allow_patterns)
        self.assertNotIn("MEG/FIF/21_3660/231204/block2_1.fif", selection.allow_patterns)

    def test_session_filter_selects_complete_s21_session2_fiff_set(self):
        records = build_manifest_from_paths([
            "MEG/FIF/21_3660/231204/block1.fif\t1812164730",
            "MEG/logs/S21-session1_block1_list1.mat\t215888",
            "MEG/FIF/21_3660/231213/block1.fif\t1903910570",
            "MEG/FIF/21_3660/231213/block1-1.fif\t612208426",
            "MEG/logs/S21-session2_block1_list2.mat\t265769",
        ])

        selection = select_tiny_records(
            records,
            modality="MEG",
            subject="S21",
            session="2",
            blocks=1,
            max_files=3,
            max_total_bytes=3 * 1024**3,
        )

        self.assertEqual(
            selection.allow_patterns,
            [
                "MEG/FIF/21_3660/231213/block1.fif",
                "MEG/FIF/21_3660/231213/block1-1.fif",
                "MEG/logs/S21-session2_block1_list2.mat",
            ],
        )
        self.assertEqual(selection.estimated_bytes, 2_516_384_765)

    def test_eeg_selection_requires_complete_triplet_and_exact_log(self):
        records = build_manifest_from_paths([
            "EEG/EEG/002_DECOMEG_S1_9696_task1.vhdr\t11703",
            "EEG/EEG/002_DECOMEG_S1_9696_task1.eeg\t127482880",
            "EEG/EEG/002_DECOMEG_S1_9696_task1.vmrk\t89765",
            "EEG/logs/S2_session1_block1_list1.mat\t202313",
            "EEG/EEG/002_DECOMEG_S1_9696_task2.vhdr\t11703",
            "EEG/EEG/002_DECOMEG_S1_9696_task2.eeg\t138053120",
            "EEG/EEG/002_DECOMEG_S1_9696_task2.vmrk\t119430",
            "EEG/logs/S2_session1_block2_list2.mat\t267376",
        ])

        selection = select_tiny_records(
            records,
            modality="EEG",
            subject="S2",
            session="1",
            blocks=1,
            max_files=4,
            max_total_bytes=256 * 1024**2,
        )

        self.assertEqual(
            selection.allow_patterns,
            [
                "EEG/EEG/002_DECOMEG_S1_9696_task1.vhdr",
                "EEG/EEG/002_DECOMEG_S1_9696_task1.eeg",
                "EEG/EEG/002_DECOMEG_S1_9696_task1.vmrk",
                "EEG/logs/S2_session1_block1_list1.mat",
            ],
        )
        self.assertEqual(selection.estimated_bytes, 127_786_661)

    def test_eeg_selection_rejects_incomplete_triplet(self):
        records = build_manifest_from_paths([
            "EEG/EEG/002_DECOMEG_S1_9696_task1.vhdr\t11703",
            "EEG/EEG/002_DECOMEG_S1_9696_task1.eeg\t127482880",
            "EEG/logs/S2_session1_block1_list1.mat\t202313",
        ])

        with self.assertRaisesRegex(SelectionError, "complete EEG BrainVision triplet"):
            select_tiny_records(records, modality="EEG", subject="S2")

    def test_eeg_selection_excludes_official_known_bad_recording(self):
        records = build_manifest_from_paths([
            "EEG/EEG/003_DECOMEG_S1_9337_task1.vhdr\t11703",
            "EEG/EEG/003_DECOMEG_S1_9337_task1.eeg\t100",
            "EEG/EEG/003_DECOMEG_S1_9337_task1.vmrk\t100",
            "EEG/logs/S3_session1_block1_list1.mat\t100",
        ])

        with self.assertRaisesRegex(SelectionError, "No raw EEG candidates"):
            select_tiny_records(records, modality="EEG", subject="S3")

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
