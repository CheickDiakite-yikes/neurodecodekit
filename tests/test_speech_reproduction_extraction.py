"""Scientific integrity checks for the new speech reproduction extraction."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.preprocess.speech_reproduction import broker_event_rows


def event_rows(role):
    return [{"onset": "20.0", "duration": "6.25", "value": "2",
             "trial_type": "orange", "session_type": role}]


class TargetBrokerTests(unittest.TestCase):
    def test_online_targets_are_absent_from_return_and_written_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "private.json"
            result = broker_event_rows(event_rows("online"), "recording", "online", path)
            self.assertNotIn("labels", result)
            self.assertNotIn("calibration_labels", result)
            self.assertNotIn("orange", json.dumps(result))
            self.assertEqual(json.loads(path.read_text())["labels"], [2])
            with self.assertRaises(FileExistsError):
                broker_event_rows(event_rows("online"), "recording", "online", path)

    def test_online_refuses_missing_private_destination(self):
        with self.assertRaises(ValueError):
            broker_event_rows(event_rows("online"), "recording", "online")

    def test_calibration_targets_are_explicit(self):
        result = broker_event_rows(event_rows("calibration"), "recording", "calibration")
        self.assertEqual(result["calibration_labels"], [2])


class GeometryTests(unittest.TestCase):
    def test_named_geometry_and_coordinate_frame_requirements(self):
        from neurodecodekit.preprocess.speech_reproduction import validate_source_geometry
        frame = {"EEGCoordinateSystem": "Other", "EEGCoordinateUnits": "mm",
            "EEGCoordinateSystemDescription": "Subject head coordinate system from g.tec "
                "electrode digitization (electrodes_uhd.xml). 3D coordinates in the subject's "
                "head space."}
        rows = [f"EEG{i:03d}\t{i}.0\t1.0\t2.0" for i in range(1, 129)]
        with tempfile.TemporaryDirectory() as tmp:
            electrodes = Path(tmp) / "electrodes.tsv"
            coordinates = Path(tmp) / "coordsystem.json"
            coordinates.write_text(json.dumps(frame), encoding="utf-8")
            electrodes.write_text("name\tx\ty\tz\n" + "\n".join(rows), encoding="utf-8")
            self.assertEqual(validate_source_geometry(electrodes, coordinates)["eeg_electrodes"], 128)
            for invalid in (rows[:-1], [rows[0]] + rows[:-1],
                            ["EEG001\tnan\t1\t2"] + rows[1:]):
                electrodes.write_text("name\tx\ty\tz\n" + "\n".join(invalid), encoding="utf-8")
                with self.assertRaises(ValueError):
                    validate_source_geometry(electrodes, coordinates)
            electrodes.write_text("name\tx\ty\tz\n" + "\n".join(rows), encoding="utf-8")
            coordinates.write_text(json.dumps({**frame, "EEGCoordinateUnits": "m"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_source_geometry(electrodes, coordinates)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SpeechTimingTests(unittest.TestCase):
    def test_continuous_trigger_ends_source_buffer_not_starts_action(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import trial_bounds
        trigger = np.zeros(10000)
        trigger[8003:8005] = 1
        bounds = trial_bounds(trigger, [8003 / 256], len(trigger))
        self.assertEqual(bounds["buffer_starts"].tolist(), [5128])
        self.assertEqual(bounds["buffer_ends"].tolist(), [8008])
        self.assertEqual(bounds["action_starts"].tolist(), [6407])

    def test_wrong_timing_and_incomplete_trial_fail(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import trial_bounds
        trigger = np.zeros(10000)
        trigger[8003:8005] = 1
        with self.assertRaisesRegex(ValueError, "reconciled"):
            trial_bounds(trigger, [8004 / 256], len(trigger))
        trigger = np.zeros(2000)
        trigger[1000:1002] = 1
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            trial_bounds(trigger, [1000 / 256], len(trigger))

    def test_exact_source_concatenation_and_repetition_grouping(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import (
            average_repetitions, trial_bounds,
        )
        bounds = trial_bounds(np.zeros(5760), [0, 2880 / 256], 5760)
        self.assertEqual(bounds["action_starts"].tolist(), [1279, 4159])
        reps = np.repeat(np.arange(5), 320)[None, :]
        np.testing.assert_array_equal(average_repetitions(reps), np.full((1, 320), 2))
        with self.assertRaises(ValueError):
            trial_bounds(np.zeros(5800), [0, 2880 / 256], 5800)
        padded = trial_bounds(np.zeros(5888), [0, 2880 / 256], 5888)
        self.assertEqual(padded["buffer_ends"].tolist(), [2880, 5760])
        self.assertEqual(padded["trailing_edf_padding_samples"], 128)

    def test_concatenated_grid_selects_original_buffers_despite_retained_triggers(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import trial_bounds
        trigger = np.zeros(5888)
        trigger[2874:2878] = 1
        trigger[5753:5758] = 1
        bounds = trial_bounds(trigger, [0, 2880 / 256], len(trigger))
        self.assertEqual(bounds["route"], "source_npy_concatenation")
        self.assertEqual(bounds["buffer_starts"].tolist(), [0, 2880])
        self.assertEqual(bounds["buffer_ends"].tolist(), [2880, 5760])
        self.assertEqual(bounds["action_starts"].tolist(), [1279, 4159])
        self.assertEqual(bounds["retained_trigger_edges"], 2)
        self.assertEqual(bounds["trailing_edf_padding_samples"], 128)
        # Neither a near-grid onset nor an extra sample earns this route.
        with self.assertRaises(ValueError):
            trial_bounds(trigger, [1e-6, 2880 / 256], len(trigger))
        with self.assertRaises(ValueError):
            trial_bounds(trigger[:-1], [0, 2880 / 256], len(trigger) - 1)

    def test_strict_continuous_route_and_last_n_trimming_are_unchanged(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import trial_bounds
        trigger = np.zeros(15000)
        trigger[100:102] = 1
        trigger[8003:8005] = 1
        trigger[12001:12003] = 1
        bounds = trial_bounds(trigger, [8003 / 256, 12001 / 256], len(trigger))
        self.assertEqual(bounds["route"], "source_continuous_trigger_buffer")
        self.assertEqual(bounds["buffer_starts"].tolist(), [5128, 9128])
        self.assertEqual(bounds["buffer_ends"].tolist(), [8008, 12008])
        self.assertEqual(bounds["extra_leading_triggers"], 1)
        with self.assertRaisesRegex(ValueError, "reconciled"):
            trial_bounds(trigger, [8003 / 256, 12002 / 256], len(trigger))

    def test_adaptive_filter_state_resets_per_original_trial(self):
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import adaptive_residual
        rng = np.random.default_rng(8)
        x, noise = rng.normal(size=(128, 400)), rng.normal(size=(3, 400))
        first = adaptive_residual(x, noise)
        adaptive_residual(x * 100, noise * 5)
        np.testing.assert_array_equal(first, adaptive_residual(x, noise))


@unittest.skipUnless(importlib.util.find_spec("mne"), "MNE not installed")
class FullExtractionTests(unittest.TestCase):
    def test_preflight_does_not_decode_targets_or_read_neural_windows(self):
        import mne
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import (
            AUX_PAIRS, preflight_recording_timing,
        )
        names = [f"EEG{i:03d}" for i in range(1, 129)] + [
            name for pair in AUX_PAIRS for name in pair] + ["TRIGGER"]
        kinds = ["eeg"] * 128 + ["misc"] * 4 + ["eog"] * 2 + ["emg"] * 4 + ["stim"]
        data = np.zeros((139, 2880))
        data[-1, 2875:2878] = 1
        data = np.pad(data, ((0, 0), (0, 192)), mode="edge")
        raw = mne.io.RawArray(data, mne.create_info(names, 256, kinds), verbose=False)
        calls = []
        original_get_data = raw.get_data

        def limited_read(*, picks, start=0):
            calls.append((picks, start))
            if len(picks) > 1 and start != 2879:
                raise AssertionError("Preflight attempted to read original neural windows")
            return original_get_data(picks=picks, start=start)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            channels = root / "channels.tsv"
            rows = ["name\ttype\tunits\tsampling_frequency\tstatus"]
            for name, kind in zip(names, kinds):
                role = {"misc": "MISC", "stim": "TRIG"}.get(kind, kind.upper())
                rows.append(f"{name}\t{role}\t{'n/a' if kind == 'stim' else 'V'}\t256\tgood")
            channels.write_text("\n".join(rows), encoding="utf-8")
            events = root / "events.tsv"
            # Invalid UTF-8 target bytes establish that only onset is decoded.
            events.write_bytes(b"onset\tvalue\ttrial_type\n0\t\xff\xfe\t\xff\n")
            with patch("mne.io.read_raw_edf", return_value=raw), \
                    patch.object(raw, "get_data", side_effect=limited_read), \
                    patch("neurodecodekit.preprocess.speech_reproduction.broker_event_rows",
                          side_effect=AssertionError("Preflight invoked target broker")), \
                    patch("neurodecodekit.preprocess.speech_reproduction.source_filter",
                          side_effect=AssertionError("Preflight invoked feature preprocessing")):
                result = preflight_recording_timing(root / "generated.edf", events, channels)
        self.assertFalse(result["target_fields_read"])
        self.assertEqual(result["retained_trigger_edges"], 1)
        self.assertEqual(result["trailing_edf_padding_samples"], 192)
        self.assertEqual(calls[0], ([138], 0))
        self.assertEqual(len(calls), 2)

    def test_real_filter_path_keeps_preaction_independent_of_action(self):
        import mne
        import numpy as np
        from neurodecodekit.preprocess.speech_reproduction import (
            AUX_PAIRS, extract_recording,
        )
        names = [f"EEG{i:03d}" for i in range(1, 129)] + [
            name for pair in AUX_PAIRS for name in pair] + ["TRIGGER"]
        kinds = ["eeg"] * 128 + ["misc"] * 4 + ["eog"] * 2 + ["emg"] * 4 + ["stim"]
        info = mne.create_info(names, 256, kinds)
        data = np.random.default_rng(3).normal(0, 1e-5, (139, 2880))
        data[-1] = 0
        changed = data.copy()
        changed[0, 1300:1800] += 1e-3
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            channels = root / "channels.tsv"
            rows = ["name\ttype\tunits\tsampling_frequency\tstatus"]
            for name, kind in zip(names, kinds):
                role = {"misc": "MISC", "stim": "TRIG"}.get(kind, kind.upper())
                unit = "n/a" if kind == "stim" else "V"
                rows.append(f"{name}\t{role}\t{unit}\t256\tgood")
            channels.write_text("\n".join(rows), encoding="utf-8")
            events = root / "events.tsv"
            events.write_text("onset\tduration\tvalue\ttrial_type\tsession_type\n"
                              "0\t6.25\t2\torange\tcalibration\n", encoding="utf-8")
            outputs = []
            callbacks = []
            # EDF export pads a fractional final second using edge values.
            for signal in (np.pad(data, ((0, 0), (0, 192)), mode="edge"),
                           np.pad(changed, ((0, 0), (0, 192)), mode="edge")):
                raw = mne.io.RawArray(signal, info, verbose=False)
                with patch("mne.io.read_raw_edf", return_value=raw):
                    outputs.append(extract_recording(root / "generated.edf", events, channels,
                        recording_id="generated", role="calibration",
                        progress=lambda done, total: callbacks.append((done, total))))
            malformed = np.pad(data, ((0, 0), (0, 192)), mode="edge")
            malformed[1, -1] += 1e-5
            with patch("mne.io.read_raw_edf",
                       return_value=mne.io.RawArray(malformed, info, verbose=False)):
                with self.assertRaisesRegex(ValueError, "padding"):
                    extract_recording(root / "generated.edf", events, channels,
                                      recording_id="generated", role="calibration")
        np.testing.assert_array_equal(outputs[0]["eeg_preaction"], outputs[1]["eeg_preaction"])
        self.assertFalse(np.array_equal(outputs[0]["eeg_adaptive"], outputs[1]["eeg_adaptive"]))
        self.assertEqual(outputs[0]["adaptive_trials"].shape, (1, 128, 1626))
        self.assertEqual(outputs[0]["nuisance_full"].shape, (1, 5, 1600))
        self.assertEqual(callbacks, [(0, 1), (1, 1), (0, 1), (1, 1)])


if __name__ == "__main__":
    unittest.main()
