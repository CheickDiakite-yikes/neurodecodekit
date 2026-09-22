"""Generated-only streaming tests; never read a real source or online file."""

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.preprocess import speech_repetition_power as repetition


IDENTITY = "sub-1_ses-20230511_task-minimallyovert_acq-calibration_run-01"


def source_paths(identity=IDENTITY):
    return tuple(Path("generated") / f"{identity}_{suffix}"
                 for suffix in ("eeg.edf", "events.tsv", "channels.tsv"))


class CalibrationPathTests(unittest.TestCase):
    def test_import_does_not_load_optional_numerical_dependencies(self):
        result = subprocess.run(
            [sys.executable, "-c", "import sys; "
             "from neurodecodekit.preprocess import speech_repetition_power; "
             "assert not {'mne','numpy','scipy','torch','sklearn'} & set(sys.modules)"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_online_foreign_and_mismatched_paths_refuse_before_open(self):
        edf, events, channels = source_paths()
        cases = [source_paths(IDENTITY.replace("calibration", "online")),
                 source_paths(IDENTITY.replace("20230511", "20230611")),
                 (edf, Path(str(events).replace("calibration", "online")), channels),
                 (edf, events, Path("elsewhere") / channels.name)]
        with mock.patch.object(repetition, "_dependencies", side_effect=AssertionError("No import")), \
                mock.patch.object(Path, "open", side_effect=AssertionError("No open")):
            for arguments in cases:
                with self.subTest(paths=arguments), self.assertRaises(ValueError):
                    repetition.extract_calibration_power(*arguments)


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("mne"),
                     "optional NumPy and MNE")
class StreamedPowerTests(unittest.TestCase):
    def _fixture(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import AUX_PAIRS, WORDS

        names = [f"EEG{index:03d}" for index in range(1, 129)]
        names += [name for pair in AUX_PAIRS for name in pair] + ["TRIGGER"]
        rows = []
        for name in names:
            kind = ("EEG" if name.startswith("EEG") else "TRIG" if name == "TRIGGER" else
                    "EOG" if name.startswith("EOG") else "EMG" if name.startswith("EMG") else "MISC")
            rows.append({"name": name, "type": kind, "sampling_frequency": "256", "units": "V",
                         "status": "bad" if name == "EEG017" else "good"})
        events = [{"onset": str(index * 11.25), "duration": "6.25", "value": str(index % 5),
                   "trial_type": WORDS[index % 5], "session_type": "calibration"}
                  for index in range(100)]
        template = np.random.RandomState(33).normal(0, 1e-5, (138, 1626))

        class GeneratedRaw:
            ch_names = names
            info = {"sfreq": 256}
            n_times = 288000
            closed = False

            def __init__(self):
                self.reads = []

            def get_data(self, *, picks, start=0, stop=None):
                self.reads.append((list(picks), start, stop))
                if picks == [138]:
                    return np.zeros((1, self.n_times))
                if stop - start != 1626:
                    raise AssertionError("One original 1626-sample window at a time")
                return template[np.asarray(picks)].copy()

            def close(self):
                self.closed = True

        return GeneratedRaw, rows, events, template

    def test_one_trial_matches_original_filter_adaptive_crop_and_auxiliary(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_auxiliary import auxiliary_feature_row
        from neurodecodekit.preprocess.speech_reproduction import source_filter, adaptive_residual

        _, _, _, template = self._fixture()
        eeg, auxiliary = template[:128], template[128::2] - template[129::2]
        expected_eeg, expected_auxiliary = source_filter(eeg, auxiliary)
        expected_residual = adaptive_residual(expected_eeg, expected_auxiliary[2:], seed=20260906)
        seen = []

        def capture(values):
            self.assertEqual(values.shape, (1, 128, 1600))
            self.assertEqual(values.dtype, np.float32)
            seen.append(values.copy())
            return {"evoked": np.zeros((1, 768)), "repetition": np.ones((1, 768)),
                    "diagnostics": {"generated": True}}

        with mock.patch("neurodecodekit.experiments.speech_repetition_power.paired_power_features",
                        side_effect=capture), \
                mock.patch.object(repetition, "source_filter", wraps=source_filter) as filtered, \
                mock.patch.object(repetition, "adaptive_residual", wraps=adaptive_residual) as adapted:
            nuisance, powers, _ = repetition._trial_features(eeg, auxiliary)
        self.assertEqual(filtered.call_count, 1)
        self.assertEqual(adapted.call_count, 1)
        self.assertEqual(adapted.call_args.kwargs, {"seed": 20260906})
        np.testing.assert_array_equal(seen[0], expected_eeg[:, 25:1625].astype(np.float32)[None])
        np.testing.assert_array_equal(seen[1], expected_residual[:, 25:1625].astype(np.float32)[None])
        np.testing.assert_array_equal(adapted.call_args.args[1], expected_auxiliary[2:])
        np.testing.assert_array_equal(nuisance, auxiliary_feature_row(auxiliary))
        self.assertEqual(set(powers), set(repetition.EEG_ARMS))

    def test_streamed_rows_retain_all_channels_repetitions_and_original_auxiliary_matrix(self):
        import mne
        import numpy as np
        from neurodecodekit.preprocess import speech_auxiliary

        raw_class, rows, events, template = self._fixture()
        raw, auxiliary_raw = raw_class(), raw_class()
        progress, allocations = [], []
        transformed_count = 0
        original_empty = np.empty
        nuisance = speech_auxiliary.auxiliary_feature_row(template[128::2] - template[129::2])

        def empty(shape, *args, **kwargs):
            allocations.append(shape)
            return original_empty(shape, *args, **kwargs)

        def read_rows(path):
            return rows if path.name.endswith("channels.tsv") else events

        def one_trial(eeg, auxiliary):
            nonlocal transformed_count
            transformed_count += 1
            np.testing.assert_array_equal(eeg, template[:128])
            np.testing.assert_array_equal(auxiliary, template[128::2] - template[129::2])
            diagnostic = {**repetition._empty_diagnostic(), "n_trials": 1,
                          "coherent_band_power_sum": [1.0] * 6,
                          "total_band_power_sum": [2.0] * 6}
            return nuisance, {arm: np.arange(768, dtype=float) for arm in repetition.EEG_ARMS}, \
                {name: diagnostic for name in ("raw", "filtered")}

        with mock.patch.object(mne.io, "read_raw_edf", return_value=raw), \
                mock.patch.object(repetition, "_read_tsv", side_effect=read_rows), \
                mock.patch.object(repetition, "_trial_features", new=one_trial), \
                mock.patch.object(np, "empty", side_effect=empty):
            result = repetition.extract_calibration_power(*source_paths(),
                progress=lambda complete, total: progress.append((complete, total)))
        with mock.patch.object(mne.io, "read_raw_edf", return_value=auxiliary_raw), \
                mock.patch.object(speech_auxiliary, "_read_tsv", side_effect=read_rows), \
                mock.patch.object(speech_auxiliary, "auxiliary_feature_row", return_value=nuisance):
            original = speech_auxiliary.extract_calibration_auxiliary(*source_paths())
        np.testing.assert_array_equal(result["auxiliary"], original["features"])
        self.assertEqual(transformed_count, 100)
        self.assertEqual(result["auxiliary"].shape, (100, 392))
        self.assertTrue(all(matrix.shape == (100, 768) for matrix in result["eeg_features"].values()))
        self.assertEqual(len(result["trial_ids"]), 100)
        self.assertEqual(progress, [(index, 100) for index in range(101)])
        self.assertEqual(allocations.count((100, 768)), 4)
        self.assertFalse(any(isinstance(shape, tuple) and len(shape) == 3 and shape[0] == 100
                             for shape in allocations))
        self.assertTrue(all(picks == list(range(138)) for picks, _, _ in raw.reads[1:]))
        self.assertEqual(result["timing_summary"]["retained_eeg_channels"], 128)
        self.assertEqual(result["timing_summary"]["retained_bad_eeg_channels"], 1)
        self.assertFalse(result["timing_summary"]["waveform_cache_retained"])
        for diagnostic in result["power_diagnostics"].values():
            self.assertEqual(diagnostic["n_trials"], 100)
            self.assertEqual(diagnostic["coherent_band_power_sum"], [100.0] * 6)
            self.assertEqual(diagnostic["total_band_power_sum"], [200.0] * 6)
            self.assertEqual(diagnostic["coherent_to_total_band_power_ratio"], [.5] * 6)
        self.assertTrue(raw.closed and auxiliary_raw.closed)

    def test_padding_validator_keeps_every_channel_and_overlap_refuses(self):
        import mne
        import numpy as np

        raw_class, rows, events, _ = self._fixture()
        raw = raw_class()
        bounds = {"action_starts": np.arange(100) * 1600,
                  "buffer_ends": np.arange(100) * 2880 + 2880}

        def stop_after_layout(_raw, layout, _bounds):
            self.assertEqual(layout["eeg"], list(range(128)))
            self.assertEqual(layout["aux_pairs"], [[i, i + 1] for i in range(128, 138, 2)])
            self.assertEqual(layout["trigger"], 138)
            raise RuntimeError("generated padding stop")

        with mock.patch.object(mne.io, "read_raw_edf", return_value=raw), \
                mock.patch.object(repetition, "_read_tsv", side_effect=lambda path:
                    rows if path.name.endswith("channels.tsv") else events), \
                mock.patch.object(repetition, "trial_bounds", return_value=bounds), \
                mock.patch.object(repetition, "_validate_edf_padding", side_effect=stop_after_layout):
            with self.assertRaisesRegex(RuntimeError, "generated padding stop"):
                repetition.extract_calibration_power(*source_paths())
            bounds["action_starts"][1] = 1599
            with self.assertRaisesRegex(ValueError, "overlap"):
                repetition.extract_calibration_power(*source_paths())
        self.assertTrue(raw.closed)

    def test_diagnostic_ratios_use_summed_power_not_mean_trial_ratios(self):
        aggregate = repetition._empty_diagnostic()
        for index in range(100):
            coherent, total = (1.0, 1.0) if index < 50 else (0.0, 9.0)
            repetition._merge_diagnostic(aggregate, {
                **repetition._empty_diagnostic(), "n_trials": 1,
                "coherent_band_power_sum": [coherent] * 6, "total_band_power_sum": [total] * 6,
            })
        self.assertEqual(repetition._finish_diagnostic(aggregate)[
            "coherent_to_total_band_power_ratio"], [.1] * 6)


if __name__ == "__main__":
    unittest.main()
