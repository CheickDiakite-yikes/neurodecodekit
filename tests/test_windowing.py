import unittest

from neurodecodekit.preprocess.windowing import WindowSpec, event_sample_indices


class WindowingTests(unittest.TestCase):
    def test_event_sample_indices(self):
        self.assertEqual(event_sample_indices([0.0, 0.5, 1.0], 100), [0, 50, 100])

    def test_window_spec_n_times(self):
        self.assertEqual(WindowSpec(sfreq=50, tmin=-0.2, tmax=0.3).n_times, 25)


if __name__ == "__main__":
    unittest.main()
