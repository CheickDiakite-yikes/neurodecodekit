import unittest

from neurodecodekit.preprocess.sequence_alignment import (
    KeySequence,
    MatTrialIndexMap,
    TargetSequence,
    TrialMappingUnavailableError,
    align_key_sequences_by_trial_map,
    align_key_sequences_to_targets,
    build_mat_trial_index_map,
    build_sequence_alignment_report,
    extract_response_sequences_from_payload,
    extract_mat_key_trigger_time_sequences_from_payload,
    extract_target_sequences_from_payload,
    group_key_event_times_into_sequences,
    group_key_labels_into_sequences,
    summarize_alignments,
    summarize_key_trigger_timing,
)


class SequenceGroupingTests(unittest.TestCase):
    def test_groups_key_labels_by_enter_without_loading_windows(self):
        sequences = group_key_labels_into_sequences(
            ["A", "SPACE", "B", "ENTER", "C", "ENTER"],
            event_times=[1.0, 1.1, 1.2, 1.3, 2.0, 2.1],
        )

        self.assertEqual([sequence.text for sequence in sequences], ["A B", "C"])
        self.assertEqual([sequence.ended_by for sequence in sequences], ["ENTER", "ENTER"])
        self.assertEqual(sequences[0].start_event_index, 0)
        self.assertEqual(sequences[0].end_event_index, 3)
        self.assertEqual(sequences[0].start_sec, 1.0)
        self.assertEqual(sequences[0].end_sec, 1.3)

    def test_trailing_sequence_is_kept_with_explicit_boundary(self):
        sequences = group_key_labels_into_sequences(["A", "SPACE", "B"])

        self.assertEqual(len(sequences), 1)
        self.assertEqual(sequences[0].text, "A B")
        self.assertEqual(sequences[0].ended_by, "end_of_cache")

    def test_groups_key_event_times_and_keeps_enter_timestamp(self):
        sequences = group_key_event_times_into_sequences(
            ["A", "ENTER", "B", "SPACE", "C", "ENTER"],
            [1.0, 1.1, 2.0, 2.1, 2.2, 2.3],
        )

        self.assertEqual(sequences, [[1.0, 1.1], [2.0, 2.1, 2.2, 2.3]])


class TrialMappingTests(unittest.TestCase):
    @staticmethod
    def _key(index: int) -> KeySequence:
        return KeySequence(index, f"K{index}", f"K{index}", 0, 1, 1.0, 2.0, 2, "ENTER")

    @staticmethod
    def _target(index: int, source: str = "mat.pr_trials.sequence") -> TargetSequence:
        return TargetSequence(index, f"T{index}", f"T{index}", source)

    def test_maps_raw_rows_to_nonempty_key_trigger_slots(self):
        mapping = build_mat_trial_index_map(
            [self._key(0), self._key(1), self._key(2)],
            [self._target(index) for index in range(5)],
            [
                self._target(0, "mat.pr_trials.key"),
                self._target(2, "mat.pr_trials.key"),
                self._target(4, "mat.pr_trials.key"),
            ],
            [[1.0], [], [2.0], [], [3.0]],
        )

        self.assertEqual(mapping.strategy, "nonempty_mat_keyTrig_trial_order")
        self.assertEqual(mapping.raw_to_mat_trial_indices, (0, 2, 4))
        self.assertEqual(mapping.skipped_mat_trial_indices, (1, 3))
        self.assertTrue(mapping.response_indices_match_performed_trials)

    def test_rejects_unreconciled_raw_and_performed_counts(self):
        with self.assertRaisesRegex(
            TrialMappingUnavailableError, "nonempty MAT keyTrig trial slots"
        ):
            build_mat_trial_index_map(
                [self._key(0), self._key(1)],
                [self._target(index) for index in range(3)],
                [],
                [[1.0], [], []],
            )


class TargetExtractionTests(unittest.TestCase):
    def test_prefers_pr_trials_sequence_over_sequence_pool(self):
        targets, warnings = extract_target_sequences_from_payload(
            {
                "sequences": ["TOP LEVEL TARGET"],
                "pr_trials": {
                    "sequence": ["training target", "chronological target"],
                    "sequences": [
                        "la fuerza atrae el electron primero   ",
                        "la fuerza atrae el electron primero   ",
                        "las calles marcan las lineas imaginarias   ",
                    ],
                },
            }
        )

        self.assertEqual(
            [target.normalized_text for target in targets],
            [
                "TRAINING TARGET",
                "CHRONOLOGICAL TARGET",
            ],
        )
        self.assertEqual({target.source_path for target in targets}, {"mat.pr_trials.sequence"})
        self.assertTrue(
            warnings[0].startswith("target_sequence_source_selected:mat.pr_trials.sequence")
        )

    def test_extracts_mat_recorded_key_responses_with_backspace(self):
        class Event:
            def __init__(self, code):
                self.Pressed = 1
                self.CookedKey = code
                self.Keycode = code

        responses, warnings = extract_response_sequences_from_payload(
            {
                "pr_trials": {
                    "key": [
                        [Event(ord("A")), Event(ord("X")), Event(8), Event(ord("B")), Event(13)],
                    ]
                }
            }
        )

        self.assertEqual(warnings, [])
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0].text, "AB")
        self.assertEqual(responses[0].source_path, "mat.pr_trials.key")

    def test_extracts_trial_aligned_mat_key_trigger_times(self):
        sequences, warnings = extract_mat_key_trigger_time_sequences_from_payload(
            {"pr_trials": {"keyTrig": [[10.0, 10.1], [20.0]]}}
        )

        self.assertEqual(sequences, [[10.0, 10.1], [20.0]])
        self.assertEqual(warnings, [])


class SequenceAlignmentTests(unittest.TestCase):
    def test_summarizes_run_specific_key_trigger_clock_offset(self):
        summary = summarize_key_trigger_timing(
            [[1.0, 1.1], [2.0, 2.1]],
            [[11.0, 11.1], [12.0, 12.1]],
        )

        self.assertEqual(summary["n_exact_length_trials"], 2)
        self.assertEqual(summary["n_keypress_pairs"], 4)
        self.assertEqual(summary["length_mismatch_trial_indices"], [])
        self.assertAlmostEqual(summary["clock_offset_sec"], 10.0)
        self.assertAlmostEqual(summary["max_abs_residual_ms"], 0.0)

    def test_key_trigger_timing_excludes_length_mismatched_trials(self):
        summary = summarize_key_trigger_timing(
            [[1.0, 1.1], [2.0]],
            [[11.0, 11.1], [12.0, 12.1]],
        )

        self.assertEqual(summary["n_exact_length_trials"], 1)
        self.assertEqual(summary["n_keypress_pairs"], 2)
        self.assertEqual(summary["length_mismatch_trial_indices"], [1])

    def test_aligns_each_typed_sequence_to_best_target(self):
        key_sequences = group_key_labels_into_sequences(
            [
                "L",
                "A",
                "SPACE",
                "F",
                "U",
                "E",
                "R",
                "Z",
                "A",
                "ENTER",
                "L",
                "A",
                "SPACE",
                "C",
                "O",
                "M",
                "P",
                "A",
                "I",
                "A",
                "ENTER",
            ]
        )
        targets, _ = extract_target_sequences_from_payload(
            {
                "pr_trials": {
                    "sequences": [
                        "la fuerza",
                        "la compañia",
                    ]
                }
            }
        )

        alignments = align_key_sequences_to_targets(
            key_sequences,
            targets,
            high_confidence_cer=0.05,
            moderate_confidence_cer=0.35,
        )
        summary = summarize_alignments(
            key_sequences=key_sequences,
            target_sequences=targets,
            alignments=alignments,
        )

        self.assertEqual([alignment.target_index for alignment in alignments], [0, 1])
        self.assertEqual([alignment.confidence for alignment in alignments], ["high", "moderate"])
        self.assertEqual(summary["confidence_counts"], {"high": 1, "moderate": 1})
        self.assertEqual(summary["matched_target_indices"], [0, 1])
        self.assertTrue(summary["target_index_mapping_is_identity"])
        self.assertEqual(summary["target_index_duplicate_count"], 0)
        self.assertEqual(summary["target_indices_in_key_order"], [0, 1])
        self.assertTrue(summary["target_index_order_is_monotonic"])

    def test_trial_map_controls_assignment_instead_of_fuzzy_text(self):
        key_sequences = group_key_labels_into_sequences(
            ["C", "ENTER", "A", "ENTER"]
        )
        targets = [
            TargetSequence(0, "A", "A", "mat.pr_trials.sequence"),
            TargetSequence(1, "B", "B", "mat.pr_trials.sequence"),
            TargetSequence(2, "C", "C", "mat.pr_trials.sequence"),
        ]

        fuzzy = align_key_sequences_to_targets(key_sequences, targets)
        strict = align_key_sequences_by_trial_map(key_sequences, targets, [0, 2])

        self.assertEqual([row.target_index for row in fuzzy], [2, 0])
        self.assertEqual([row.target_index for row in strict], [0, 2])

    def test_report_embeds_strict_trial_assignment_evidence(self):
        key_sequences = group_key_labels_into_sequences(
            ["A", "ENTER", "C", "ENTER"]
        )
        targets = [
            TargetSequence(index, value, value, "mat.pr_trials.sequence")
            for index, value in enumerate(["A", "B", "C"])
        ]
        mapping = MatTrialIndexMap(
            strategy="nonempty_mat_keyTrig_trial_order",
            raw_to_mat_trial_indices=(0, 2),
            skipped_mat_trial_indices=(1,),
            response_indices_match_performed_trials=True,
            warnings=("empty_mat_keyTrig_trials_skipped:1",),
        )
        alignments = align_key_sequences_by_trial_map(
            key_sequences,
            targets,
            mapping.raw_to_mat_trial_indices,
        )

        report = build_sequence_alignment_report(
            cache_path="cache/example.npz",
            events_path="events/example.mat",
            key_sequences=key_sequences,
            target_sequences=targets,
            alignments=alignments,
            trial_index_map=mapping,
            runtime_sec=0.125,
        )

        self.assertEqual(report["schema"]["version"], 3)
        self.assertEqual(
            report["assignment"]["strategy"], "nonempty_mat_keyTrig_trial_order"
        )
        self.assertTrue(report["assignment"]["uses_mat_trial_order"])
        self.assertTrue(report["assignment"]["has_mat_key_trigger_evidence"])
        self.assertFalse(report["assignment"]["uses_text_similarity_for_assignment"])
        self.assertEqual(report["trial_index_map"]["raw_to_mat_trial_indices"], [0, 2])
        self.assertEqual(report["resources"]["runtime_sec"], 0.125)
        self.assertNotIn(
            "assignment_uses_best_text_similarity_without_mat_trial_map",
            report["warnings"],
        )

    def test_report_warns_when_best_matches_jump_backward_in_trial_order(self):
        key_sequences = group_key_labels_into_sequences(["B", "ENTER", "A", "ENTER"])
        targets, _ = extract_target_sequences_from_payload(
            {
                "pr_trials": {
                    "sequence": ["A", "B"],
                }
            }
        )
        alignments = align_key_sequences_to_targets(key_sequences, targets)

        report = build_sequence_alignment_report(
            cache_path="cache/example.npz",
            events_path="events/example.mat",
            key_sequences=key_sequences,
            target_sequences=targets,
            alignments=alignments,
        )

        self.assertEqual(report["summary"]["target_indices_in_key_order"], [1, 0])
        self.assertFalse(report["summary"]["target_index_order_is_monotonic"])
        self.assertFalse(report["summary"]["target_index_mapping_is_identity"])
        self.assertEqual(report["summary"]["target_index_backtrack_count"], 1)
        self.assertIn(
            "best_mat_target_matches_are_not_monotonic_in_trial_order", report["warnings"]
        )
        self.assertIn(
            "assignment_uses_best_text_similarity_without_mat_trial_map", report["warnings"]
        )


if __name__ == "__main__":
    unittest.main()
