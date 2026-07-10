import importlib.util
import unittest

from neurodecodekit.preprocess.fif_mat_extraction import (
    _pick_and_load_raw,
    parse_mat_event_payload,
    require_neuro_dependencies,
    stim_key_event_rows,
    stim_letter_event_rows,
)
from neurodecodekit.preprocess.windowing import (
    WindowSpec,
    extract_windows_from_array_with_report,
    window_bounds_for_events,
)


class WindowExtractionEdgeTests(unittest.TestCase):
    def test_window_bounds_report_edge_drops(self):
        spec = WindowSpec(sfreq=100, tmin=-0.1, tmax=0.1)
        kept, dropped = window_bounds_for_events([0.05, 0.5, 0.95], spec, n_samples=100)

        self.assertEqual([bound.event_index for bound in kept], [1])
        self.assertEqual([drop.reason for drop in dropped], ["before_start", "after_end"])

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
    def test_extract_windows_from_synthetic_array_with_report(self):
        import numpy as np

        spec = WindowSpec(sfreq=100, tmin=-0.1, tmax=0.1)
        data = np.arange(2 * 100, dtype="float32").reshape(2, 100)
        result = extract_windows_from_array_with_report(data, [0.5, 0.01, 0.99], spec)

        self.assertEqual(result.windows.shape, (1, 2, 20))
        self.assertEqual(result.kept_event_indices, [0])
        self.assertEqual(result.dropped_by_reason, {"before_start": 1, "after_end": 1})
        np.testing.assert_array_equal(result.windows[0], data[:, 40:60])


class MatEventParserTests(unittest.TestCase):
    def test_parse_parallel_time_and_label_arrays(self):
        payload = {"log": {"key_times": [0.25, 0.5], "keys": ["A", "B"]}}

        parsed = parse_mat_event_payload(payload, source_sfreq=100)

        self.assertEqual([row.time_sec for row in parsed.rows], [0.25, 0.5])
        self.assertEqual([row.label for row in parsed.rows], ["A", "B"])
        self.assertEqual(parsed.source_fields, ["mat.log.key_times + mat.log.keys"])

    def test_parse_event_matrix_with_sample_indices(self):
        payload = {"events": [[50, 0, 65], [100, 0, 66]]}

        parsed = parse_mat_event_payload(
            payload,
            source_sfreq=100,
            raw_duration_sec=1.2,
            raw_n_times=120,
        )

        self.assertEqual([row.time_sec for row in parsed.rows], [0.5, 1.0])
        self.assertEqual([row.label for row in parsed.rows], ["65", "66"])

    def test_warns_when_no_event_table_found(self):
        parsed = parse_mat_event_payload({"notes": "no timing here"})

        self.assertEqual(parsed.rows, [])
        self.assertIn("No confident event timestamp table", parsed.warnings[0])

    def test_duplicate_parser_warnings_are_collapsed(self):
        payload = {
            "events": [
                {"Time": 500, "Keycode": 65},
                {"Time": 600, "Keycode": 66},
            ]
        }

        parsed = parse_mat_event_payload(
            payload,
            source_sfreq=100,
            raw_duration_sec=1.0,
            raw_n_times=1000,
        )

        self.assertEqual(len(parsed.warnings), len(set(parsed.warnings)))

    def test_stim_letter_event_rows_keep_only_unambiguous_uppercase_ascii(self):
        rows = stim_letter_event_rows(
            [
                [100, 0, 1],
                [200, 0, 65],
                [300, 0, 32],
                [400, 0, 90],
            ],
            sfreq=100,
            stim_channel="STI101",
            source_path="raw.fif",
        )

        self.assertEqual([row.time_sec for row in rows], [2.0, 4.0])
        self.assertEqual([row.label for row in rows], ["A", "Z"])
        self.assertEqual([row.confidence for row in rows], ["raw_stim_letter", "raw_stim_letter"])

    def test_stim_rows_subtract_nonzero_raw_first_sample(self):
        letter_rows = stim_letter_event_rows(
            [[150, 0, 65]],
            sfreq=100,
            stim_channel="STI101",
            source_path="raw.fif",
            first_samp=50,
        )
        key_rows = stim_key_event_rows(
            [[150, 0, 65]],
            sfreq=100,
            stim_channel="STI101",
            source_path="raw.fif",
            first_samp=50,
        )

        self.assertEqual(letter_rows[0].time_sec, 1.0)
        self.assertEqual(key_rows.rows[0].time_sec, 1.0)

    def test_stim_key_event_rows_include_space_enter_and_drop_initial_sweep(self):
        ascii_sweep = [[index * 10, 0, value] for index, value in enumerate([13, 32, *range(65, 91)])]
        typed_keys = [
            [1000, 0, 65],
            [1100, 0, 32],
            [1200, 0, 66],
            [1300, 0, 13],
            [1400, 0, 1],
        ]

        parsed = stim_key_event_rows(
            [*ascii_sweep, *typed_keys],
            sfreq=100,
            stim_channel="STI101",
            source_path="raw.fif",
            segment_gap_sec=5.0,
        )

        self.assertEqual(parsed.n_candidate_events, 32)
        self.assertEqual(parsed.n_dropped_initial_ascii_sweep, 28)
        self.assertEqual(parsed.warnings, ["initial_ascii_sweep_dropped:28"])
        self.assertEqual([row.time_sec for row in parsed.rows], [10.0, 11.0, 12.0, 13.0])
        self.assertEqual([row.label for row in parsed.rows], ["A", "SPACE", "B", "ENTER"])
        self.assertEqual({row.confidence for row in parsed.rows}, {"raw_stim_key"})


class DependencyErrorTests(unittest.TestCase):
    def test_require_neuro_dependencies_has_actionable_message(self):
        def fake_import(_name):
            raise ImportError(_name)

        with self.assertRaisesRegex(RuntimeError, r"pip install -e '\.\[neuro\]'"):
            require_neuro_dependencies(import_module=fake_import)


class ResourceBoundedExtractionTests(unittest.TestCase):
    def test_channel_cap_is_applied_before_signal_data_is_loaded(self):
        class FakeRaw:
            def __init__(self):
                self.ch_names = ["MEG001", "MEG002", "MEG003"]
                self.calls = []

            def pick(self, picks):
                self.calls.append(("pick", list(picks)))
                self.ch_names = list(picks)

            def load_data(self):
                self.calls.append(("load_data",))

        raw = FakeRaw()

        _pick_and_load_raw(raw, picks=None, max_channels=2)

        self.assertEqual(
            raw.calls,
            [("pick", ["MEG001", "MEG002"]), ("load_data",)],
        )


if __name__ == "__main__":
    unittest.main()
