import unittest

from neurodecodekit.preprocess.ctc_text import (
    CTC_TOKEN_TO_ID,
    decode_ctc_target,
    encode_ctc_text,
    greedy_decode_ctc_ids,
    minimum_ctc_input_steps,
    normalize_ctc_text,
)


class CTCTextTests(unittest.TestCase):
    def test_roundtrip_and_normalization(self):
        encoded = encode_ctc_text("  Ab\tc  ")

        self.assertEqual(normalize_ctc_text("  Ab\tc  "), "AB C")
        self.assertEqual(decode_ctc_target(encoded), "AB C")
        self.assertNotIn(0, encoded)

    def test_greedy_decode_collapses_repeats_and_drops_blank(self):
        a = CTC_TOKEN_TO_ID["A"]
        b = CTC_TOKEN_TO_ID["B"]

        self.assertEqual(greedy_decode_ctc_ids([0, a, a, 0, a, b, b, 0]), "AAB")
        self.assertEqual(minimum_ctc_input_steps([a, a, b]), 4)

    def test_unsupported_target_character_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            encode_ctc_text("NINO!")


if __name__ == "__main__":
    unittest.main()
