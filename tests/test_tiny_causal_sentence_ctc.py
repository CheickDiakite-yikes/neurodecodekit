import importlib.util
import tempfile
import unittest
from pathlib import Path


ML_AVAILABLE = (
    importlib.util.find_spec("numpy") is not None and importlib.util.find_spec("torch") is not None
)


@unittest.skipUnless(ML_AVAILABLE, "NumPy/Torch not installed")
class TinyCausalSentenceCTCTests(unittest.TestCase):
    def test_exact_parameter_counts_output_lengths_and_future_invariance(self):
        import torch

        from neurodecodekit.models.tiny_causal_sentence_ctc import (
            build_causal_sentence_ctc,
            registered_candidate_config,
            registered_linear_config,
        )

        torch.manual_seed(2601)
        candidate = build_causal_sentence_ctc(registered_candidate_config())
        linear = build_causal_sentence_ctc(registered_linear_config())
        self.assertEqual(sum(value.numel() for value in candidate.parameters()), 2908)
        self.assertEqual(sum(value.numel() for value in linear.parameters()), 2884)
        source = torch.randn(1, 102, 12)
        changed = source.clone()
        changed[:, :, 8:] += 1000
        candidate.eval()
        with torch.no_grad():
            first = candidate(source)
            second = candidate(changed)
        self.assertEqual(tuple(first.shape), (1, 12, 28))
        torch.testing.assert_close(first[:, :8], second[:, :8], rtol=0, atol=0)
        self.assertFalse(torch.equal(first[:, 8:], second[:, 8:]))

    def test_fixed_step_training_replays_and_numeric_checkpoint_roundtrips(self):
        import numpy as np
        import torch

        from neurodecodekit.models.tiny_causal_sentence_ctc import (
            load_causal_sentence_ctc_checkpoint,
            predict_causal_sentence_ctc,
            registered_candidate_config,
            save_causal_sentence_ctc_checkpoint,
            train_causal_sentence_ctc,
        )

        rng = np.random.default_rng(7)
        signals = rng.normal(0, 0.1, size=(3, 102, 12)).astype("float32")
        signals[0, 0, :] += 1
        signals[1, 1, :] += 1
        signals[2, 2, :] += 1
        lengths = np.asarray([12, 12, 12], dtype="int32")
        target_ids = np.asarray([[1], [2], [3]], dtype="int16")
        target_lengths = np.asarray([1, 1, 1], dtype="int32")
        config = registered_candidate_config(seed=2601)
        first = train_causal_sentence_ctc(
            signals=signals,
            input_lengths=lengths,
            target_token_ids=target_ids,
            target_lengths=target_lengths,
            config=config,
        )
        second = train_causal_sentence_ctc(
            signals=signals,
            input_lengths=lengths,
            target_token_ids=target_ids,
            target_lengths=target_lengths,
            config=config,
        )
        self.assertEqual(first.optimizer_steps, 240)
        self.assertEqual(len(first.loss_history), 240)
        self.assertEqual(first.loss_history, second.loss_history)
        for name, value in first.model.state_dict().items():
            torch.testing.assert_close(value, second.model.state_dict()[name], rtol=0, atol=0)

        with tempfile.TemporaryDirectory() as tmp:
            checkpoint_path = Path(tmp) / "checkpoint.npz"
            descriptor = save_causal_sentence_ctc_checkpoint(
                checkpoint_path,
                training=first,
                metadata={"condition_id": "synthetic-test"},
            )
            loaded, metadata = load_causal_sentence_ctc_checkpoint(checkpoint_path)
            self.assertEqual(metadata["parameter_count"], 2908)
            self.assertLess(descriptor["bytes"], 4 * 1024 * 1024)
            original = predict_causal_sentence_ctc(
                first.model,
                signals=signals,
                input_lengths=lengths,
            )
            replay = predict_causal_sentence_ctc(
                loaded,
                signals=signals,
                input_lengths=lengths,
            )
            self.assertEqual(original["predictions"], replay["predictions"])
            self.assertEqual(original["blank_count"], replay["blank_count"])

    def test_refuses_config_drift_and_impossible_alignment(self):
        import numpy as np

        from neurodecodekit.models.tiny_causal_sentence_ctc import (
            CausalSentenceCTCConfig,
            build_causal_sentence_ctc,
            registered_candidate_config,
            train_causal_sentence_ctc,
        )

        with self.assertRaisesRegex(ValueError, "exactly 240"):
            build_causal_sentence_ctc(CausalSentenceCTCConfig(optimizer_steps=239))
        signals = np.zeros((1, 102, 2), dtype="float32")
        with self.assertRaisesRegex(RuntimeError, "non-finite"):
            train_causal_sentence_ctc(
                signals=signals,
                input_lengths=np.asarray([2]),
                target_token_ids=np.asarray([[1, 1]], dtype="int16"),
                target_lengths=np.asarray([2]),
                config=registered_candidate_config(),
            )


if __name__ == "__main__":
    unittest.main()
