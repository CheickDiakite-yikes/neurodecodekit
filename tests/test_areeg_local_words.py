"""Generated ArEEG runner checks; no HTTP, EEG payloads, or model fitting."""

import contextlib
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.experiments import areeg_local_words as runner


def _source_paths():
    return [
        f"sub-{p}/ses-{s}/eeg/sub-{p}_ses-{s}_task-innerspeech_eeg.{suffix}"
        for p in range(12) for s in range(6) for suffix in ("eeg", "vhdr", "vmrk")
    ]


def _metadata_transport(paths):
    def write_generated_archive(url, destination, size_cap):
        if runner.REVISION not in url or size_cap != 2 * 2**20:
            raise AssertionError("unexpected metadata transport arguments")
        with tarfile.open(destination, "w:gz") as archive:
            for path in paths:
                member = tarfile.TarInfo("generated-release/" + path)
                member.type = tarfile.SYMTYPE
                member.linkname = (
                    "../../annex/objects/SHA256E-s100--" + "a" * 64 + Path(path).suffix
                )
                archive.addfile(member)
    return write_generated_archive


class ManifestTests(unittest.TestCase):
    def test_exact_generated_slice_has_unique_files_and_consistent_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "new-invocation"
            with mock.patch.object(runner, "curl", side_effect=_metadata_transport(_source_paths())):
                with contextlib.redirect_stdout(io.StringIO()):
                    runner.manifest(root)
            manifest = json.loads((root / "manifest.json").read_text())
            self.assertEqual(manifest["revision"], runner.REVISION)
            self.assertEqual(len(manifest["files"]), 216)
            self.assertEqual({row["path"] for row in manifest["files"]}, set(_source_paths()))
            self.assertEqual(manifest["total_bytes"], 21600)
            self.assertTrue(all(row["sha256"] == "a" * 64 for row in manifest["files"]))

    def test_duplicate_cannot_replace_a_required_source_file(self):
        paths = _source_paths()
        paths[-1] = paths[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "new-invocation"
            with mock.patch.object(runner, "curl", side_effect=_metadata_transport(paths)):
                with self.assertRaises(RuntimeError):
                    runner.manifest(root)
            self.assertFalse((root / "manifest.json").exists())

    def test_missing_file_is_rejected_before_manifest_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "new-invocation"
            with mock.patch.object(runner, "curl", side_effect=_metadata_transport(_source_paths()[:-1])):
                with self.assertRaises(RuntimeError):
                    runner.manifest(root)
            self.assertFalse((root / "manifest.json").exists())


class SandboxProfileTests(unittest.TestCase):
    def test_predictor_profile_reads_only_named_inputs_and_own_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            repo, prepared, output = root / "repo", root / "prepared", root / "predicted"
            names = ("train.npy", "train_cue.npy", "test.npy", "test_cue.npy",
                     "calibration.json", "test_ids.json")
            model = repo / "src/neurodecodekit/models/imagined_word_decoder.py"
            inputs = [prepared / name for name in names] + [model]
            command = runner.sandbox(repo, "predictor", inputs, output, [])
            profile = command[command.index("-p") + 1]
            self.assertIn("(deny default)", profile)
            self.assertIn("-I", command)
            self.assertIn("-S", command)
            for path in inputs:
                self.assertIn(f"(allow file-read* (literal {json.dumps(str(path))}))", profile)
            self.assertNotIn("targets.json", profile)
            self.assertNotIn(".vmrk", profile)
            for forbidden_root in (root, repo, prepared, root / "raw"):
                self.assertNotIn(f"(subpath {json.dumps(str(forbidden_root))})", profile)
            self.assertIn(
                f"(allow file-read* file-write* (subpath {json.dumps(str(output))}))", profile,
            )
            self.assertNotIn("(allow network", profile)
            self.assertNotIn("(allow process-fork", profile)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class DerangementTests(unittest.TestCase):
    def test_noncontiguous_groups_preserve_sessions_without_fixed_points(self):
        import numpy as np

        values = np.arange(12).reshape(12, 1, 1)
        original = values.copy()
        ids = [
            {"participant": str(i % 2), "session": str((i // 2) % 2), "trial_id": str(i)}
            for i in range(12)
        ]
        output = runner.derange_by_session(values, ids, 7)
        self.assertTrue(np.all(output[:, 0, 0] != values[:, 0, 0]))
        np.testing.assert_array_equal(values, original)
        np.testing.assert_array_equal(output, runner.derange_by_session(values, ids, 7))
        for participant in ("0", "1"):
            for session in ("0", "1"):
                indices = [i for i, row in enumerate(ids)
                           if row["participant"] == participant and row["session"] == session]
                self.assertEqual(set(output[indices, 0, 0]), set(values[indices, 0, 0]))

    def test_singleton_group_is_refused(self):
        import numpy as np

        with self.assertRaisesRegex(RuntimeError, "fixed point"):
            runner.derange_by_session(np.ones((1, 2, 4)),
                                      [{"participant": "0", "session": "0"}], 7)


if __name__ == "__main__":
    unittest.main()
