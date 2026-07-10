import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class FrozenScalerTests(unittest.TestCase):
    @staticmethod
    def _arrays(channel_names=("M1", "M2")):
        import numpy as np

        from neurodecodekit.preprocess.ctc_text import encode_ctc_text

        signals = np.zeros((2, 2, 4), dtype="float32")
        signals[0, :, :3] = [[1.0, 3.0, 5.0], [10.0, 15.0, 20.0]]
        signals[1, :, :2] = [[-1.0, 1.0], [5.0, 10.0]]
        texts = ["AB", "BA"]
        target_ids = np.asarray([encode_ctc_text(text) for text in texts], dtype="int16")
        return {
            "signals": signals,
            "input_lengths": np.asarray([3, 2], dtype="int32"),
            "target_token_ids": target_ids,
            "target_lengths": np.asarray([2, 2], dtype="int32"),
            "target_texts": np.asarray(texts, dtype="U"),
            "reference_texts": np.asarray(["PROMPT A", "PROMPT B"], dtype="U"),
            "mat_response_texts": np.asarray(texts, dtype="U"),
            "trial_indices": np.asarray([0, 1], dtype="int32"),
            "sentence_start_sec": np.asarray([1.0, 2.0]),
            "sentence_end_sec": np.asarray([1.3, 2.2]),
            "channel_names": np.asarray(channel_names, dtype="U"),
        }

    @staticmethod
    def _extraction_params():
        return {
            "sfreq": 100.0,
            "pre_context_sec": 0.4,
            "post_context_sec": 0.45,
            "picks": "mag",
            "max_channels": 2,
            "stim_channel": "STI101",
            "l_freq": 0.5,
            "h_freq": 45.0,
            "notch_freq": 50.0,
        }

    def _write_source(self, path: Path, *, channel_names=("M1", "M2")) -> None:
        from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache

        save_sentence_npz_cache(
            path,
            **self._arrays(channel_names),
            metadata={
                "kind": "test_unscaled",
                "extraction_params": self._extraction_params(),
                "transformations": [
                    {
                        "name": "per_channel_robust_scaler",
                        "params": {"enabled": False},
                    }
                ],
            },
        )

    def _write_fit(self, path: Path) -> None:
        import numpy as np

        from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
        from neurodecodekit.preprocess.sentence_extraction import scaler_array_sha256

        center = np.asarray([1.0, 10.0], dtype="float32")
        scale = np.asarray([2.0, 5.0], dtype="float32")
        save_sentence_npz_cache(
            path,
            **self._arrays(),
            metadata={
                "kind": "test_train_scaled",
                "extraction_params": self._extraction_params(),
                "transformations": [
                    {
                        "name": "per_channel_robust_scaler",
                        "params": {
                            "enabled": True,
                            "clamp": 5.0,
                            "fit_split": "train",
                            "fit_scope": "valid_train_sentence_timepoints",
                            "split_protocol_config_sha256": "protocol-hash",
                            "semantic_membership_sha256": "membership-hash",
                            "statistics": {
                                "center": center.tolist(),
                                "scale": scale.tolist(),
                                "center_sha256": scaler_array_sha256(center),
                                "scale_sha256": scaler_array_sha256(scale),
                                "n_fit_rows": 1,
                            },
                        },
                    }
                ],
            },
        )

    def test_applies_verified_fit_cache_scaler_and_preserves_padding(self):
        import numpy as np

        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.preprocess.frozen_scaler import (
            apply_frozen_train_scaler_to_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            fit = root / "fit.npz"
            output = root / "scaled.npz"
            self._write_source(source)
            self._write_fit(fit)

            summary = apply_frozen_train_scaler_to_cache(
                source_cache_path=source,
                fit_cache_path=fit,
                output_path=output,
            )
            loaded = load_sentence_npz_cache(output)
            fit_loaded = load_sentence_npz_cache(fit)
            from neurodecodekit.cache.signal_representation import file_sha256
            from neurodecodekit.evaluation.cross_session import (
                validate_cross_session_contract,
            )

            contract = validate_cross_session_contract(
                train_cache=fit_loaded,
                eval_cache=loaded,
                partitions=SimpleNamespace(
                    source_cache_sha256=file_sha256(fit),
                    protocol_config_sha256="protocol-hash",
                    group_assignment_sha256="group-hash",
                    semantic_membership_sha256="membership-hash",
                    report_path="split.json",
                    train_indices=[0],
                    validation_indices=[],
                    test_indices=[1],
                ),
            )

        np.testing.assert_allclose(loaded.signals[0, 0, :3], [0.0, 1.0, 2.0])
        np.testing.assert_allclose(loaded.signals[0, 1, :3], [0.0, 1.0, 2.0])
        np.testing.assert_allclose(loaded.signals[1, 0, :2], [-1.0, 0.0])
        np.testing.assert_allclose(loaded.signals[1, 1, :2], [-1.0, 0.0])
        self.assertTrue((loaded.signals[0, :, 3:] == 0).all())
        self.assertTrue((loaded.signals[1, :, 2:] == 0).all())
        self.assertEqual(summary.signals_shape, (2, 2, 4))
        self.assertEqual(
            loaded.metadata["frozen_scaler"]["fit_scope"],
            "valid_train_sentence_timepoints",
        )
        self.assertTrue(contract["channel_names_identical"])
        self.assertTrue(contract["unscaled_eval_source_cache_hash_verified"])

    def test_rejects_channel_order_mismatch(self):
        from neurodecodekit.preprocess.frozen_scaler import (
            apply_frozen_train_scaler_to_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            fit = root / "fit.npz"
            self._write_source(source, channel_names=("M1", "M3"))
            self._write_fit(fit)

            with self.assertRaisesRegex(ValueError, "identical channel names and order"):
                apply_frozen_train_scaler_to_cache(
                    source_cache_path=source,
                    fit_cache_path=fit,
                    output_path=root / "scaled.npz",
                )


if __name__ == "__main__":
    unittest.main()
