import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets.manifest import (
    build_manifest_from_paths,
    infer_spanishbcbl_record,
    pair_raw_records_to_logs,
    parse_manifest_input_line,
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
        self.assertEqual(record.family, "meg_log_mat")

    def test_infer_eeg_brainvision_family(self):
        record = infer_spanishbcbl_record("pinet2024_public/EEG/EEG/S2/eeg.vhdr")
        self.assertEqual(record.modality, "EEG")
        self.assertEqual(record.subject, "S2")
        self.assertEqual(record.kind, "raw")
        self.assertEqual(record.family, "eeg_brainvision_vhdr")

    def test_unknown_rows_are_explicit(self):
        record = infer_spanishbcbl_record("pinet2024_public/misc/readme.txt")
        self.assertEqual(record.family, "unknown")
        self.assertIn("unknown_modality", record.warnings)
        self.assertIn("unknown_kind", record.warnings)
        self.assertIn("unknown_file_family", record.warnings)

    def test_parse_manifest_input_line_with_sizes(self):
        json_record = parse_manifest_input_line(
            '{"path":"pinet2024_public/MEG/FIF/S1/block1.fif","size_bytes":12345}'
        )
        self.assertIsNotNone(json_record)
        self.assertEqual(json_record.path, "pinet2024_public/MEG/FIF/S1/block1.fif")
        self.assertEqual(json_record.size_bytes, 12345)

        tsv_record = parse_manifest_input_line(
            "pinet2024_public/MEG/logs/S1_block1.mat\t678"
        )
        self.assertIsNotNone(tsv_record)
        self.assertEqual(tsv_record.path, "pinet2024_public/MEG/logs/S1_block1.mat")
        self.assertEqual(tsv_record.size_bytes, 678)

        bom_record = parse_manifest_input_line(
            "\ufeffpinet2024_public/MEG/FIF/S2/block2.fif\t999"
        )
        self.assertIsNotNone(bom_record)
        self.assertEqual(bom_record.path, "pinet2024_public/MEG/FIF/S2/block2.fif")
        self.assertEqual(bom_record.size_bytes, 999)

    def test_pair_raw_records_to_logs_reports_exact_missing_and_ambiguous(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif",
            "pinet2024_public/MEG/logs/S1_block1.mat",
            "pinet2024_public/MEG/FIF/S2/block1.fif",
            "pinet2024_public/MEG/FIF/S3/block1.fif",
            "pinet2024_public/MEG/logs/S3_block1_a.mat",
            "pinet2024_public/MEG/logs/S3_block1_b.mat",
        ])

        pairs = {pair.raw_path: pair for pair in pair_raw_records_to_logs(records)}

        self.assertEqual(
            pairs["pinet2024_public/MEG/FIF/S1/block1.fif"].candidate_log_paths,
            ("pinet2024_public/MEG/logs/S1_block1.mat",),
        )
        self.assertEqual(pairs["pinet2024_public/MEG/FIF/S1/block1.fif"].status, "exact")
        self.assertEqual(pairs["pinet2024_public/MEG/FIF/S2/block1.fif"].status, "missing_log")
        self.assertEqual(pairs["pinet2024_public/MEG/FIF/S3/block1.fif"].status, "ambiguous")

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
        self.assertEqual(summary["by_family"]["meg_fif_raw"], 1)
        self.assertEqual(summary["raw_log_pairing"]["by_status"]["exact"], 1)

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
