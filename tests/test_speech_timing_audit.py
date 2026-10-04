"""Generated timing-only inputs; no real recordings, models or targets."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "speech_timing_audit", Path(__file__).parents[1] / "scripts/audit_speech_reproduction_timing.py"
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("mne"),
                     "Optional NumPy/MNE not installed")
class TimingAuditTests(unittest.TestCase):
    def run_audit(self, n_samples, event_samples, edge_samples, *, change_identity=False):
        import numpy as np

        trigger = np.zeros(n_samples)
        trigger[edge_samples] = 1
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            signal = root / "generated_eeg.edf"
            events = root / "generated_events.tsv"
            signal.write_bytes(b"generated placeholder; EDF reader mocked")
            events.write_text("onset\tvalue\ttrial_type\n" + "".join(
                f"{sample / 256}\tNOT_A_LABEL\tDO_NOT_PARSE\n" for sample in event_samples
            ), encoding="utf-8")
            item = {"path": signal.name, "events_path": events.name,
                    "signal_bytes": signal.stat().st_size,
                    "signal_sha256": AUDIT.digest(signal),
                    "events_bytes": events.stat().st_size,
                    "events_git_blob_sha": AUDIT.digest(events, True)}
            if change_identity:
                item["signal_sha256"] = "0" * 64
            with patch("mne.io.read_raw_edf") as read:
                raw = read.return_value
                raw.ch_names, raw.info, raw.n_times = ["TRIGGER"], {"sfreq": 256}, n_samples
                raw.get_data.return_value = trigger[None, :]
                result = AUDIT.audit_recording(root, item)
                read.assert_called_once_with(str(signal), include=["TRIGGER"],
                                             preload=False, verbose=False)
                raw.close.assert_called_once()
            return result

    def test_retained_edges_do_not_define_concatenated_trial_identity(self):
        result = self.run_audit(5760, [0, 2880], [100, 700, 2900])
        self.assertEqual(result["source_supported_timing_route"], "source_npy_concatenation")
        self.assertTrue(result["current_reader_would_reject_retained_trigger_fallback"])
        self.assertTrue(result["all_original_buffers_in_bounds"])

    def test_continuous_uses_last_n_edges_and_original_buffers(self):
        result = self.run_audit(10000, [8003], [100, 8003])
        self.assertEqual(result["source_supported_timing_route"], "source_continuous_trigger_buffer")
        self.assertEqual(result["event_rise_matches"], 1)
        self.assertTrue(result["all_original_buffers_in_bounds"])

    def test_arbitrary_offset_is_unresolved(self):
        result = self.run_audit(10000, [8004], [8003])
        self.assertEqual(result["source_supported_timing_route"], "unresolved")
        self.assertFalse(result["all_original_buffers_in_bounds"])

    def test_padding_requires_whole_second_length_and_reports_trigger_only(self):
        result = self.run_audit(5888, [0, 2880], [100, 2900])
        self.assertEqual(result["trailing_edf_padding_samples"], 128)
        self.assertTrue(result["trigger_padding_is_edge_repetition"])
        invalid = self.run_audit(5800, [0, 2880], [100, 2900])
        self.assertEqual(invalid["source_supported_timing_route"], "unresolved")

    def test_incomplete_continuous_buffer_is_not_accepted(self):
        result = self.run_audit(2000, [1000], [1000])
        self.assertFalse(result["all_original_buffers_in_bounds"])

    def test_changed_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Pinned signal identity changed"):
            self.run_audit(5760, [0, 2880], [100], change_identity=True)

    def test_empty_onsets_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Empty or nonfinite"):
            self.run_audit(5760, [], [100])
