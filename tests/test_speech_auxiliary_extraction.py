"""Generated-only checks for calibration auxiliary extraction; no source data."""

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.preprocess import speech_auxiliary as auxiliary


IDENTITY = "sub-1_ses-20230511_task-minimallyovert_acq-calibration_run-01"


def paths(identity=IDENTITY):
    root = Path("generated")
    return tuple(root / f"{identity}_{suffix}" for suffix in ("eeg.edf", "events.tsv", "channels.tsv"))


class PathBoundaryTests(unittest.TestCase):
    def test_import_keeps_numerical_dependencies_optional(self):
        result = subprocess.run(
            [sys.executable, "-c", "import sys; "
             "from neurodecodekit.preprocess import speech_auxiliary; "
             "assert not {'numpy','mne','scipy','torch','sklearn'} & set(sys.modules)"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_online_and_mismatched_paths_refused_before_any_open_or_mne_import(self):
        edf, events, channels = paths()
        cases = [paths(IDENTITY.replace("calibration", "online")),
                 (edf, Path(str(events).replace("calibration", "online")), channels),
                 (edf, events, Path(str(channels).replace("calibration", "online"))),
                 (edf, Path("another") / events.name, channels),
                 paths(IDENTITY.replace("20230511", "20230512"))]
        with mock.patch.object(auxiliary, "_dependencies", side_effect=AssertionError("No MNE open")), \
                mock.patch.object(Path, "open", side_effect=AssertionError("No file open")):
            for arguments in cases:
                with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                    auxiliary.extract_calibration_auxiliary(*arguments)


@unittest.skipUnless(importlib.util.find_spec("mne") and importlib.util.find_spec("numpy"),
                     "optional MNE and NumPy")
class AuxiliaryNumericsTests(unittest.TestCase):
    def test_features_equal_original_full_source_filter_on_generated_samples(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import source_filter

        rng = np.random.RandomState(20260921)
        eeg = rng.normal(0, 1e-5, (128, 1626))
        values = rng.normal(0, 2e-4, (5, 1626))
        _, original = source_filter(eeg, values)
        full = original[:, 25:1625].astype(np.float32)[None]
        expected = auxiliary.fixed_channel_features(auxiliary.average_repetitions(full),
                                                    full_trial=full)[0]
        actual = auxiliary.auxiliary_feature_row(values)
        self.assertEqual(actual.shape, (390,))
        np.testing.assert_array_equal(actual, expected)

    def _source_fixture(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import AUX_PAIRS, WORDS

        names = [f"EEG{index:03d}" for index in range(1, 129)]
        names += [name for pair in AUX_PAIRS for name in pair] + ["TRIGGER"]
        rows = []
        for name in names:
            kind = ("EEG" if name.startswith("EEG") else "TRIG" if name == "TRIGGER" else
                    "EOG" if name.startswith("EOG") else "EMG" if name.startswith("EMG") else "MISC")
            rows.append({"name": name, "type": kind, "sampling_frequency": "256",
                         "units": "V", "status": "good"})
        events = [{"onset": str(index * 11.25), "duration": "6.25", "value": str(index % 5),
                   "trial_type": WORDS[index % 5], "session_type": "calibration"}
                  for index in range(100)]

        class GeneratedRaw:
            ch_names = names
            info = {"sfreq": 256}
            n_times = 100 * 2880
            closed = False

            def __init__(self):
                self.reads = []

            def get_data(self, *, picks, start=0, stop=None):
                self.reads.append((list(picks), start, stop))
                if not set(picks).issubset(set(range(128, 139))):
                    raise AssertionError("EEG samples must not be requested")
                stop = self.n_times if stop is None else stop
                if picks == [138]:
                    return np.zeros((1, stop - start))
                return np.broadcast_to(np.asarray(picks, dtype=float)[:, None] * 1e-6,
                                       (len(picks), stop - start)).copy()

            def close(self):
                self.closed = True

        return GeneratedRaw(), rows, events

    def test_calibration_only_picks_timing_shape_and_progress(self):
        import numpy as np
        import mne

        raw, channel_rows, event_rows = self._source_fixture()
        progress = []

        def read_rows(path):
            return channel_rows if path.name.endswith("channels.tsv") else event_rows

        def generated_features(values):
            self.assertEqual(values.shape, (5, 1626))
            np.testing.assert_allclose(values, -1e-6, rtol=0, atol=1e-18)
            return np.arange(390, dtype=float)

        with mock.patch.object(mne.io, "read_raw_edf", return_value=raw), \
                mock.patch.object(auxiliary, "_read_tsv", side_effect=read_rows), \
                mock.patch.object(auxiliary, "auxiliary_feature_row", side_effect=generated_features):
            result = auxiliary.extract_calibration_auxiliary(*paths(),
                progress=lambda completed, total: progress.append((completed, total)))
        self.assertEqual(result["features"].shape, (100, 392))
        np.testing.assert_array_equal(result["features"][:, -2], np.arange(100))
        np.testing.assert_array_equal(result["features"][:, -1], (1279 + np.arange(100) * 2880) / 256)
        np.testing.assert_array_equal(result["calibration_labels"], np.arange(100) % 5)
        self.assertEqual(len(set(result["trial_ids"])), 100)
        self.assertEqual(progress, [(index, 100) for index in range(101)])
        self.assertTrue(raw.closed)
        self.assertTrue(result["timing_summary"]["action_windows_nonoverlapping"])
        self.assertFalse(result["timing_summary"]["eeg_samples_requested"])
        self.assertEqual(raw.reads[0][0], [138])
        self.assertTrue(all(picks == list(range(128, 138)) for picks, _, _ in raw.reads[1:]))

    def test_overlapping_original_action_windows_are_rejected(self):
        import numpy as np
        import mne

        raw, channel_rows, event_rows = self._source_fixture()
        bounds = {"action_starts": np.arange(100) * 1000}
        with mock.patch.object(mne.io, "read_raw_edf", return_value=raw), \
                mock.patch.object(auxiliary, "_read_tsv", side_effect=lambda path:
                    channel_rows if path.name.endswith("channels.tsv") else event_rows), \
                mock.patch.object(auxiliary, "trial_bounds", return_value=bounds):
            with self.assertRaisesRegex(ValueError, "overlap"):
                auxiliary.extract_calibration_auxiliary(*paths())
        self.assertTrue(raw.closed)
        self.assertEqual(len(raw.reads), 1)


if __name__ == "__main__":
    unittest.main()
