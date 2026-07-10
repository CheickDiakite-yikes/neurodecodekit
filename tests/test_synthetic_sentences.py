import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SyntheticSentenceTests(unittest.TestCase):
    def test_generation_is_deterministic_and_variable_length(self):
        from neurodecodekit.training.synthetic_sentences import make_synthetic_sentence_arrays

        first, metadata = make_synthetic_sentence_arrays(
            sentences=24,
            channels=5,
            letter_classes=4,
            seed=11,
        )
        second, _ = make_synthetic_sentence_arrays(
            sentences=24,
            channels=5,
            letter_classes=4,
            seed=11,
        )

        self.assertEqual(first["signals"].shape[0:2], (24, 5))
        self.assertGreater(len(set(first["input_lengths"].tolist())), 1)
        self.assertEqual(len(set(first["target_texts"].tolist())), 24)
        self.assertTrue((first["signals"] == second["signals"]).all())
        self.assertIn("not_real_neural_data", metadata["warnings"][0])


if __name__ == "__main__":
    unittest.main()
