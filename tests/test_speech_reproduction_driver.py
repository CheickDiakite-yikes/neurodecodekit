"""No neural data or network: verify the experiment's acquisition boundary."""

import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location("speech_repro_driver",
    Path(__file__).resolve().parents[1] / "scripts" / "run_speech_reproduction.py")
DRIVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIVER)


class SpeechReproductionDriverTests(unittest.TestCase):
    def test_download_checks_git_blob_identity_and_commits_only_complete_file(self):
        payload = b"source sidecar fixture\n"
        digest = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.tsv"
            with patch.object(DRIVER, "request", return_value=io.BytesIO(payload)):
                DRIVER.download("https://example.invalid/fixture", path, len(payload), digest,
                                Mock(), git_blob=True)
            self.assertEqual(path.read_bytes(), payload)
            self.assertFalse(path.with_suffix(".tsv.partial").exists())

    def test_wrong_identity_never_promotes_source_file(self):
        payload = b"wrong source"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.edf"
            with patch.object(DRIVER, "request", return_value=io.BytesIO(payload)):
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    DRIVER.download("https://example.invalid/fixture", path, len(payload),
                                    "0" * 64, Mock())
            self.assertFalse(path.exists())

    def test_existing_source_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.edf"
            path.touch()
            with patch.object(DRIVER, "request") as request:
                with self.assertRaises(FileExistsError):
                    DRIVER.download("https://example.invalid/fixture", path, 0, "", Mock())
            request.assert_not_called()

    def test_trial_pair_uses_person_session_condition_not_target(self):
        item = {"path": "sub-2/ses-20230512/eeg/"
                        "sub-2_ses-20230512_task-minimallyovert_acq-online_run-01_eeg.edf"}
        self.assertEqual(DRIVER.pair_key(item), ("sub-2", "ses-20230512", "minimallyovert"))


if __name__ == "__main__":
    unittest.main()
