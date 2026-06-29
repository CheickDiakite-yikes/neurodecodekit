import unittest

from neurodecodekit.evaluation.keyboard import aligned_keyboard_distance, key_distance


class KeyboardTests(unittest.TestCase):
    def test_same_key_zero(self):
        self.assertEqual(key_distance("A", "A"), 0.0)
        self.assertEqual(key_distance("a", "A"), 0.0)

    def test_near_key_smaller_than_unknown(self):
        self.assertLess(key_distance("A", "S"), key_distance("A", "?"))

    def test_aligned_distance(self):
        self.assertEqual(aligned_keyboard_distance("ABC", "ABC"), 0.0)
        self.assertGreater(aligned_keyboard_distance("ABC", "AXC"), 0.0)


if __name__ == "__main__":
    unittest.main()
