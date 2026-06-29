import unittest

from neurodecodekit.evaluation.metrics import (
    character_error_rate,
    levenshtein_distance,
    normalize_text,
    word_error_rate,
)


class MetricsTests(unittest.TestCase):
    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(levenshtein_distance("", "abc"), 3)
        self.assertEqual(levenshtein_distance("abc", "abc"), 0)

    def test_character_error_rate(self):
        self.assertAlmostEqual(character_error_rate("HOLA", "HOLA"), 0.0)
        self.assertAlmostEqual(character_error_rate("HOLA", "HALA"), 0.25)

    def test_word_error_rate(self):
        self.assertAlmostEqual(word_error_rate("HOLA MUNDO", "HOLA MUNDO"), 0.0)
        self.assertAlmostEqual(word_error_rate("HOLA MUNDO", "HOLA LUNA"), 0.5)

    def test_normalize_text(self):
        self.assertEqual(normalize_text("  hola   mundo "), "HOLA MUNDO")


if __name__ == "__main__":
    unittest.main()
