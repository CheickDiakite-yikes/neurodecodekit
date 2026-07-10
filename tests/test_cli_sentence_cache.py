import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SentenceCacheCliTests(unittest.TestCase):
    def test_make_and_inspect_synthetic_sentence_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "sentences.npz"
            sidecar = Path(tmp) / "sentences.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                make_code = main(
                    [
                        "make-synthetic-sentence-cache",
                        "--out",
                        str(cache),
                        "--sentences",
                        "16",
                        "--channels",
                        "5",
                    ]
                )
                inspect_code = main(
                    [
                        "inspect-sentence-cache",
                        "--cache",
                        str(cache),
                        "--metadata-out",
                        str(sidecar),
                    ]
                )
            payload = json.loads(sidecar.read_text(encoding="utf-8"))

        self.assertEqual(make_code, 0)
        self.assertEqual(inspect_code, 0)
        self.assertEqual(payload["summary"]["n_sentences"], 16)
        self.assertEqual(payload["summary"]["schema_name"], "b2q-sentence-cache")


@unittest.skipUnless(importlib.util.find_spec("torch"), "Torch not installed")
@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class TinyCTCCliTests(unittest.TestCase):
    def test_ctc_report_includes_no_brain_comparator(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cache = tmp_path / "sentences.npz"
            split_dir = tmp_path / "split"
            report_path = tmp_path / "report.json"
            with redirect_stdout(io.StringIO()):
                make_code = main(
                    [
                        "make-synthetic-sentence-cache",
                        "--out",
                        str(cache),
                        "--sentences",
                        "48",
                        "--channels",
                        "5",
                        "--seed",
                        "19",
                    ]
                )
                split_code = main(
                    [
                        "split-protocol",
                        "--cache",
                        str(cache),
                        "--out-dir",
                        str(split_dir),
                    ]
                )
                train_code = main(
                    [
                        "tiny-ctc-baseline",
                        "--cache",
                        str(cache),
                        "--split-report",
                        str(split_dir / "split.json"),
                        "--epochs",
                        "50",
                        "--seed",
                        "19",
                        "--num-threads",
                        "1",
                        "--out-json",
                        str(report_path),
                    ]
                )
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(make_code, 0)
        self.assertEqual(split_code, 0)
        self.assertEqual(train_code, 0)
        self.assertLess(report["summary"]["corpus_cer"], 0.25)
        self.assertIn("prior_only", report["comparators"])
        self.assertIn("tiny_ctc_vs_prior_only", report["comparisons"])
        self.assertEqual(report["baseline"]["kind"], "tiny-ctc-sentence")
        self.assertEqual(
            report["baseline"]["split_mode"],
            "split-protocol-v1-explicit-membership",
        )


if __name__ == "__main__":
    unittest.main()
