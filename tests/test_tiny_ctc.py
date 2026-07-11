import importlib.util
import unittest

from neurodecodekit.models.tiny_ctc import (
    deterministic_text_holdout_indices,
    greedy_decode_token_rows,
)
from neurodecodekit.preprocess.ctc_text import CTC_TOKEN_TO_ID


class TinyCTCHelperTests(unittest.TestCase):
    def test_text_hash_split_prevents_duplicate_text_leakage(self):
        texts = ["AA", "BB", "AA", "CC", "DD", "BB"]
        train, eval_ = deterministic_text_holdout_indices(texts, train_fraction=0.5)

        self.assertTrue(train)
        self.assertTrue(eval_)
        self.assertFalse({texts[index] for index in train} & {texts[index] for index in eval_})

    def test_greedy_decode_respects_valid_lengths(self):
        a = CTC_TOKEN_TO_ID["A"]
        b = CTC_TOKEN_TO_ID["B"]
        rows = [[0, a, a, 0, b, b], [b, b, 0, a, a, a]]

        self.assertEqual(greedy_decode_token_rows(rows, [5, 3]), ["AB", "B"])

    def test_parameter_validation_precedes_optional_import(self):
        from neurodecodekit.models.tiny_ctc import run_tiny_ctc_baseline

        with self.assertRaisesRegex(ValueError, "epochs"):
            run_tiny_ctc_baseline(
                signals=[],
                input_lengths=[],
                target_token_ids=[],
                target_lengths=[],
                target_texts=[],
                epochs=0,
            )

    def test_explicit_partition_contract_requires_exact_coverage(self):
        from neurodecodekit.models.tiny_ctc import _normalize_partition_indices

        normalized = _normalize_partition_indices(
            {"train": [0, 1], "val": [2], "test": [3]},
            n_rows=4,
            eval_partition="test",
        )
        self.assertEqual(normalized["train"], [0, 1])
        self.assertEqual(normalized["test"], [3])

        with self.assertRaisesRegex(ValueError, "overlap"):
            _normalize_partition_indices(
                {"train": [0, 1], "test": [1, 2, 3]},
                n_rows=4,
                eval_partition="test",
            )
        with self.assertRaisesRegex(ValueError, "cover every"):
            _normalize_partition_indices(
                {"train": [0], "test": [2]},
                n_rows=4,
                eval_partition="test",
            )


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
@unittest.skipIf(importlib.util.find_spec("torch"), "Torch installed")
class TinyCTCMissingDependencyTests(unittest.TestCase):
    def test_missing_torch_error_points_to_ml_extra(self):
        import numpy as np

        from neurodecodekit.models.tiny_ctc import run_tiny_ctc_baseline

        with self.assertRaisesRegex(RuntimeError, r"pip install -e '.\[ml\]'"):
            run_tiny_ctc_baseline(
                signals=np.zeros((2, 2, 4), dtype="float32"),
                input_lengths=np.array([4, 4]),
                target_token_ids=np.array([[1], [2]]),
                target_lengths=np.array([1, 1]),
                target_texts=["A", "B"],
            )


@unittest.skipUnless(importlib.util.find_spec("torch"), "Torch not installed")
@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class TinyCTCTrainingTests(unittest.TestCase):
    def test_cross_session_multi_view_trains_once_and_scores_named_views(self):
        import numpy as np

        from neurodecodekit.models.tiny_ctc import run_tiny_ctc_cross_session_views
        from neurodecodekit.training.synthetic_sentences import (
            make_synthetic_sentence_arrays,
        )

        source, _ = make_synthetic_sentence_arrays(
            sentences=16,
            channels=5,
            letter_classes=4,
            seed=51,
        )
        evaluation, _ = make_synthetic_sentence_arrays(
            sentences=8,
            channels=5,
            letter_classes=4,
            seed=52,
        )
        partitions = {
            "train": list(range(12)),
            "val": [12, 13],
            "test": [14, 15],
        }
        result = run_tiny_ctc_cross_session_views(
            train_signals=source["signals"],
            train_input_lengths=source["input_lengths"],
            train_target_token_ids=source["target_token_ids"],
            train_target_lengths=source["target_lengths"],
            train_target_texts=source["target_texts"],
            eval_signal_views={
                "identity": evaluation["signals"],
                "scaled": np.asarray(evaluation["signals"]) * 0.5,
            },
            eval_input_lengths=evaluation["input_lengths"],
            eval_target_token_ids=evaluation["target_token_ids"],
            eval_target_lengths=evaluation["target_lengths"],
            eval_target_texts=evaluation["target_texts"],
            source_partitions=partitions,
            epochs=2,
            num_threads=1,
            max_restarts=1,
        )

        self.assertEqual(result.n_eval_views, 2)
        self.assertEqual(set(result.predictions_by_view), {"identity", "scaled"})
        self.assertEqual(set(result.eval_cer_by_view), {"identity", "scaled"})
        self.assertEqual(len(result.loss_history), 2)
        self.assertEqual(result.n_eval_rows, 8)
        self.assertIn(
            "multiple_target_views_share_one_frozen_source_trained_model",
            result.warnings,
        )

    def test_cross_session_path_reserves_source_holdouts_and_evaluates_all_eval_rows(self):
        from neurodecodekit.models.tiny_ctc import run_tiny_ctc_cross_session
        from neurodecodekit.training.synthetic_sentences import (
            make_synthetic_sentence_arrays,
        )

        source, _ = make_synthetic_sentence_arrays(
            sentences=16,
            channels=5,
            letter_classes=4,
            seed=31,
        )
        evaluation, _ = make_synthetic_sentence_arrays(
            sentences=8,
            channels=5,
            letter_classes=4,
            seed=32,
        )
        partitions = {
            "train": list(range(12)),
            "val": [12, 13],
            "test": [14, 15],
        }

        result = run_tiny_ctc_cross_session(
            train_signals=source["signals"],
            train_input_lengths=source["input_lengths"],
            train_target_token_ids=source["target_token_ids"],
            train_target_lengths=source["target_lengths"],
            train_target_texts=source["target_texts"],
            eval_signals=evaluation["signals"],
            eval_input_lengths=evaluation["input_lengths"],
            eval_target_token_ids=evaluation["target_token_ids"],
            eval_target_lengths=evaluation["target_lengths"],
            eval_target_texts=evaluation["target_texts"],
            source_partitions=partitions,
            split_metadata={"semantic_membership_sha256": "membership"},
            epochs=2,
            num_threads=1,
            max_restarts=1,
        )

        self.assertEqual(
            result.split_mode,
            "strict-source-train-to-independent-session-eval",
        )
        self.assertEqual(result.train_indices, partitions["train"])
        self.assertEqual(result.reserved_validation_indices, partitions["val"])
        self.assertEqual(result.reserved_test_indices, partitions["test"])
        self.assertEqual(result.eval_indices, list(range(8)))
        self.assertEqual(result.n_eval_rows, 8)
        self.assertEqual(result.semantic_membership_sha256, "membership")

    def test_tiny_ctc_consumes_explicit_split_protocol_membership(self):
        from neurodecodekit.evaluation.split_protocol import (
            build_sentence_text_membership,
        )
        from neurodecodekit.models.tiny_ctc import run_tiny_ctc_baseline
        from neurodecodekit.training.synthetic_sentences import make_synthetic_sentence_arrays

        arrays, _metadata = make_synthetic_sentence_arrays(
            sentences=24,
            channels=5,
            letter_classes=4,
            seed=23,
        )
        membership = build_sentence_text_membership(
            arrays["reference_texts"].tolist(),
            trial_indices=arrays["trial_indices"].tolist(),
            ratios={"train": 0.7, "val": 0.1, "test": 0.2},
        )
        partitions = {
            name: [row["source_row_index"] for row in membership["rows"] if row["split"] == name]
            for name in ("train", "val", "test")
        }
        result = run_tiny_ctc_baseline(
            signals=arrays["signals"],
            input_lengths=arrays["input_lengths"],
            target_token_ids=arrays["target_token_ids"],
            target_lengths=arrays["target_lengths"],
            target_texts=arrays["target_texts"],
            seed=23,
            epochs=2,
            num_threads=1,
            max_restarts=1,
            partition_indices=partitions,
            eval_partition="test",
            split_metadata=membership,
        )

        self.assertEqual(result.split_mode, "split-protocol-v1-explicit-membership")
        self.assertEqual(result.train_indices, partitions["train"])
        self.assertEqual(result.validation_indices, partitions["val"])
        self.assertEqual(result.test_indices, partitions["test"])
        self.assertEqual(
            result.semantic_membership_sha256,
            membership["semantic_membership_sha256"],
        )

    def test_tiny_ctc_learns_synthetic_token_motifs(self):
        from neurodecodekit.models.tiny_ctc import run_tiny_ctc_baseline
        from neurodecodekit.training.synthetic_sentences import make_synthetic_sentence_arrays

        arrays, _metadata = make_synthetic_sentence_arrays(
            sentences=48,
            channels=5,
            letter_classes=4,
            seed=13,
        )
        result = run_tiny_ctc_baseline(
            signals=arrays["signals"],
            input_lengths=arrays["input_lengths"],
            target_token_ids=arrays["target_token_ids"],
            target_lengths=arrays["target_lengths"],
            target_texts=arrays["target_texts"],
            seed=13,
            epochs=50,
            num_threads=1,
        )

        self.assertLess(result.eval_cer, 0.25)
        self.assertLess(result.loss_history[-1], result.loss_history[0])
        self.assertEqual(result.output_stride, 1)
        self.assertFalse(result.causal)

    def test_degenerate_seed_restarts_using_training_fit_only(self):
        from neurodecodekit.models.tiny_ctc import run_tiny_ctc_baseline
        from neurodecodekit.training.synthetic_sentences import make_synthetic_sentence_arrays

        arrays, _metadata = make_synthetic_sentence_arrays(
            sentences=48,
            channels=5,
            letter_classes=4,
            seed=4,
        )
        result = run_tiny_ctc_baseline(
            signals=arrays["signals"],
            input_lengths=arrays["input_lengths"],
            target_token_ids=arrays["target_token_ids"],
            target_lengths=arrays["target_lengths"],
            target_texts=arrays["target_texts"],
            seed=4,
            epochs=60,
            num_threads=1,
            max_restarts=3,
        )

        self.assertLess(result.eval_cer, 0.25)
        self.assertGreater(result.restart_count, 1)
        self.assertIn("tiny_ctc_restarted_after_degenerate_training_fit", result.warnings)


if __name__ == "__main__":
    unittest.main()
