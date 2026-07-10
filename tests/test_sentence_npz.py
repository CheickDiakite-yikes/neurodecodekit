import importlib.util
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SentenceCacheTests(unittest.TestCase):
    def _arrays(self):
        import numpy as np

        from neurodecodekit.preprocess.ctc_text import encode_ctc_text

        texts = ["AB", "AA"]
        encoded = [encode_ctc_text(text) for text in texts]
        signals = np.zeros((2, 2, 6), dtype="float32")
        signals[0, :, :5] = 1
        signals[1, :, :4] = 2
        target_ids = np.zeros((2, 2), dtype="int16")
        for index, values in enumerate(encoded):
            target_ids[index, : len(values)] = values
        return {
            "signals": signals,
            "input_lengths": np.array([5, 4], dtype="int32"),
            "target_token_ids": target_ids,
            "target_lengths": np.array([2, 2], dtype="int32"),
            "target_texts": np.array(texts, dtype="U"),
            "reference_texts": np.array(["PROMPT AB", "PROMPT AA"], dtype="U"),
            "mat_response_texts": np.array(texts, dtype="U"),
            "trial_indices": np.array([7, 8], dtype="int32"),
            "sentence_start_sec": np.array([1.0, 2.0]),
            "sentence_end_sec": np.array([1.5, 2.4]),
            "channel_names": np.array(["M1", "M2"], dtype="U"),
        }

    def test_roundtrip_reports_variable_length_storage(self):
        from neurodecodekit.cache.sentence_npz import (
            load_sentence_npz_cache,
            save_sentence_npz_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sentences.npz"
            save_sentence_npz_cache(
                path,
                **self._arrays(),
                metadata={"kind": "test_sentences", "warnings": ["test_only"]},
            )
            loaded = load_sentence_npz_cache(path)

        self.assertEqual(loaded.summary.signals_shape, (2, 2, 6))
        self.assertEqual(loaded.summary.total_valid_timepoints, 9)
        self.assertAlmostEqual(loaded.summary.padding_fraction, 0.25)
        self.assertEqual(loaded.target_texts.tolist(), ["AB", "AA"])
        self.assertEqual(loaded.metadata["ctc_vocabulary"]["blank_id"], 0)

    def test_rejects_nonzero_signal_padding(self):
        from neurodecodekit.cache.sentence_npz import (
            SentenceCacheSchemaError,
            save_sentence_npz_cache,
        )

        arrays = self._arrays()
        arrays["signals"][0, 0, 5] = 1
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(
            SentenceCacheSchemaError, "signal padding"
        ):
            save_sentence_npz_cache(
                Path(tmp) / "bad.npz",
                **arrays,
                metadata={"kind": "test"},
            )

    def test_rejects_text_token_disagreement(self):
        from neurodecodekit.cache.sentence_npz import (
            SentenceCacheSchemaError,
            save_sentence_npz_cache,
        )

        arrays = self._arrays()
        arrays["target_texts"][0] = "BA"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(
            SentenceCacheSchemaError, "does not match"
        ):
            save_sentence_npz_cache(
                Path(tmp) / "bad.npz",
                **arrays,
                metadata={"kind": "test"},
            )

    def test_loader_rejects_wrong_schema_name(self):
        import json

        import numpy as np

        from neurodecodekit.cache.sentence_npz import (
            SentenceCacheSchemaError,
            load_sentence_npz_cache,
            save_sentence_npz_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong-schema.npz"
            save_sentence_npz_cache(path, **self._arrays(), metadata={"kind": "test"})
            with np.load(path, allow_pickle=False) as data:
                arrays = {name: data[name].copy() for name in data.files if name != "metadata"}
                metadata = json.loads(str(data["metadata"].item()))
            metadata["schema"]["name"] = "not-a-sentence-cache"
            np.savez_compressed(path, **arrays, metadata=json.dumps(metadata))

            with self.assertRaisesRegex(SentenceCacheSchemaError, "schema name"):
                load_sentence_npz_cache(path)


if __name__ == "__main__":
    unittest.main()
