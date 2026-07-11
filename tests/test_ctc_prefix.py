import math
import unittest


class CTCPrefixDecoderTests(unittest.TestCase):
    def test_collapse_and_greedy_preserve_blank_separated_repeats(self):
        from neurodecodekit.decoding.ctc_prefix import (
            GreedyCTCDecoder,
            ctc_collapse,
        )

        path = (1, 1, 0, 1, 2, 2, 0, 2)
        self.assertEqual(ctc_collapse(path), (1, 1, 2, 2))
        decoder = GreedyCTCDecoder(max_output_length=8)
        hypotheses = []
        for selected in path:
            frame = [-8.0, -8.0, -8.0]
            frame[selected] = 0.0
            hypotheses.append(decoder.push(frame).hypothesis)

        self.assertEqual(decoder.flush(), (1, 1, 2, 2))
        self.assertEqual(hypotheses[1], (1,))
        self.assertEqual(hypotheses[3], (1, 1))

    def test_wide_prefix_beam_matches_exhaustive_path_sums(self):
        from neurodecodekit.decoding.ctc_prefix import (
            PrefixBeamCTCDecoder,
            exhaustive_ctc_distribution,
        )

        probabilities = (
            (0.20, 0.70, 0.10),
            (0.55, 0.35, 0.10),
            (0.20, 0.65, 0.15),
            (0.45, 0.10, 0.45),
        )
        frames = tuple(
            tuple(math.log(value) for value in frame) for frame in probabilities
        )
        exhaustive = exhaustive_ctc_distribution(frames)
        decoder = PrefixBeamCTCDecoder(beam_width=128, max_prefix_length=4)
        for frame in frames:
            decoder.push(frame)
        beam_scores = decoder.beam_scores()

        self.assertEqual(set(beam_scores), set(exhaustive))
        for prefix, expected in exhaustive.items():
            self.assertAlmostEqual(beam_scores[prefix], expected, places=12)
        expected_top = min(
            exhaustive,
            key=lambda prefix: (-exhaustive[prefix], prefix),
        )
        self.assertEqual(decoder.flush(), expected_top)

    def test_prefix_beam_reconstructs_adjacent_duplicate_through_blank(self):
        from neurodecodekit.decoding.ctc_prefix import PrefixBeamCTCDecoder

        probabilities = (
            (0.05, 0.90, 0.05),
            (0.90, 0.05, 0.05),
            (0.05, 0.90, 0.05),
        )
        decoder = PrefixBeamCTCDecoder(beam_width=8, max_prefix_length=4)
        for frame in probabilities:
            decoder.push(tuple(math.log(value) for value in frame))

        self.assertEqual(decoder.flush(), (1, 1))
        self.assertLessEqual(decoder.max_state_payload_bytes, 4 * 1024)

    def test_frame_order_not_transport_grouping_controls_partial_trace(self):
        from neurodecodekit.decoding.ctc_prefix import PrefixBeamCTCDecoder

        probabilities = (
            (0.10, 0.80, 0.10),
            (0.70, 0.20, 0.10),
            (0.10, 0.20, 0.70),
            (0.80, 0.10, 0.10),
        )
        frames = [tuple(math.log(value) for value in frame) for frame in probabilities]

        def decode(groups):
            decoder = PrefixBeamCTCDecoder(beam_width=8, max_prefix_length=4)
            trace = []
            for group in groups:
                for frame in group:
                    trace.append(decoder.push(frame).top_prefix)
            return trace, decoder.flush()

        single_trace, single_final = decode([[frame] for frame in frames])
        grouped_trace, grouped_final = decode([frames[:3], frames[3:]])
        self.assertEqual(grouped_trace, single_trace)
        self.assertEqual(grouped_final, single_final)

    def test_caps_ties_and_closed_state_fail_deterministically(self):
        from neurodecodekit.decoding.ctc_prefix import (
            GreedyCTCDecoder,
            PrefixBeamCTCDecoder,
            exhaustive_ctc_distribution,
        )

        greedy = GreedyCTCDecoder(max_output_length=1)
        self.assertEqual(greedy.push((-1.0, -1.0, -2.0)).path_class, 0)
        greedy.flush()
        with self.assertRaisesRegex(RuntimeError, "already closed"):
            greedy.push((0.0, -1.0))

        prefix = PrefixBeamCTCDecoder(beam_width=2, max_prefix_length=1)
        prefix.push((-1.0, -1.0, -2.0))
        prefix.flush()
        with self.assertRaisesRegex(RuntimeError, "already closed"):
            prefix.push((0.0, -1.0, -2.0))
        with self.assertRaisesRegex(ValueError, "exceeding"):
            exhaustive_ctc_distribution(
                ((-1.0, -1.0, -1.0),) * 5,
                max_paths=100,
            )


if __name__ == "__main__":
    unittest.main()
