import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets.hf_access import HubFileRecord, write_file_record_list


class HuggingFaceAccessTests(unittest.TestCase):
    def test_metadata_writer_is_manifest_compatible_jsonl(self):
        records = [
            HubFileRecord(path="EEG/EEG/002_task1.vhdr", size_bytes=123),
            HubFileRecord(path="EEG/EEG/002_task1.eeg", size_bytes=456),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "files.jsonl"
            write_file_record_list(records, output)
            rows = [json.loads(line) for line in output.read_text().splitlines()]

        self.assertEqual(rows[0]["path"], records[0].path)
        self.assertEqual(rows[0]["size_bytes"], 123)
        self.assertEqual(rows[1]["size_bytes"], 456)


if __name__ == "__main__":
    unittest.main()
