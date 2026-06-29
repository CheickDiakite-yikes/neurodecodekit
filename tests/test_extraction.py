import importlib.util
import unittest

from neurodecodekit.preprocess.fif_mat_extraction import (
    parse_mat_event_payload,
    require_neuro_dependencies,
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


class DependencyErrorTests(unittest.TestCase):
    def test_require_neuro_dependencies_has_actionable_message(self):
        def fake_import(_name):
            raise ImportError(_name)

        with self.assertRaisesRegex(RuntimeError, r"pip install -e '\.\[neuro\]'"):
            require_neuro_dependencies(import_module=fake_import)


if __name__ == "__main__":
    unittest.main()
