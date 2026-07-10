import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main
from neurodecodekit.datasets.manifest import build_manifest_from_paths
from neurodecodekit.datasets.selection import select_tiny_records, write_selection


class SelectionCliTests(unittest.TestCase):
    def test_download_selection_dry_run_prints_exact_plan(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif\t1024",
            "pinet2024_public/MEG/logs/S1_block1.mat\t256",
        ])
        selection = select_tiny_records(records, modality="MEG", subject="S1", blocks=1)

        with tempfile.TemporaryDirectory() as tmp:
            selection_path = Path(tmp) / "selection.json"
            write_selection(selection, selection_path)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main([
                    "download-selection",
                    "--selection",
                    str(selection_path),
                    "--local-dir",
                    str(Path(tmp) / "download"),
                ])

        output = stdout.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Download plan", output)
        self.assertIn("estimated size: 1.2 KB", output)
        self.assertIn("pinet2024_public/MEG/FIF/S1/block1.fif", output)
        self.assertIn("Safety default: dry-run", output)
        self.assertIn("revision: unpinned", output)
        self.assertIn("max_workers=1", output)

    def test_execute_requires_explicit_unknown_size_acknowledgement(self):
        records = build_manifest_from_paths([
            "pinet2024_public/MEG/FIF/S1/block1.fif",
            "pinet2024_public/MEG/logs/S1_block1.mat",
        ])
        selection = select_tiny_records(records, modality="MEG", subject="S1", blocks=1)

        with tempfile.TemporaryDirectory() as tmp:
            selection_path = Path(tmp) / "selection.json"
            write_selection(selection, selection_path)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main([
                    "download-selection",
                    "--selection",
                    str(selection_path),
                    "--local-dir",
                    str(Path(tmp) / "download"),
                    "--execute",
                ])

        self.assertEqual(code, 2)
        self.assertIn("--allow-unknown-size", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
