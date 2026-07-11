import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class SignalRepresentationTests(unittest.TestCase):
    def test_all_encodings_roundtrip_semantic_contract_and_exact_identity(self):
        import numpy as np

        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.cache.signal_representation import (
            SUPPORTED_SIGNAL_ENCODINGS,
            LoadedSignalRepresentation,
            load_sentence_cache_auto,
            load_signal_representation_cache,
            save_signal_representation_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "source.npz"
            _write_sentence_cache(source_path)
            source = load_sentence_npz_cache(source_path)

            for encoding in SUPPORTED_SIGNAL_ENCODINGS:
                with self.subTest(encoding=encoding):
                    path = root / f"{encoding}.npz"
                    sidecar = root / f"{encoding}.metadata.json"
                    summary = save_signal_representation_cache(
                        path,
                        source_cache=source,
                        encoding=encoding,
                        metadata_sidecar=sidecar,
                    )
                    loaded = load_signal_representation_cache(path)
                    automatic = load_sentence_cache_auto(path)

                    self.assertIsInstance(automatic, LoadedSignalRepresentation)
                    self.assertEqual(summary.encoding, encoding)
                    self.assertEqual(loaded.summary.signals_shape, source.summary.signals_shape)
                    self.assertEqual(str(loaded.signals.dtype), "float32")
                    self.assertEqual(loaded.metadata, source.metadata)
                    self.assertEqual(loaded.trial_indices.tolist(), [10, 11])
                    self.assertTrue(sidecar.exists())
                    for name in (
                        "input_lengths",
                        "target_token_ids",
                        "target_lengths",
                        "target_texts",
                        "reference_texts",
                        "mat_response_texts",
                        "trial_indices",
                        "sentence_start_sec",
                        "sentence_end_sec",
                        "channel_names",
                    ):
                        np.testing.assert_array_equal(
                            getattr(loaded, name), getattr(source, name)
                        )
                    if encoding == "float32":
                        np.testing.assert_array_equal(loaded.signals, source.signals)
                    else:
                        np.testing.assert_allclose(loaded.signals, source.signals, atol=0.04)

    def test_auto_loader_preserves_standard_sentence_cache(self):
        from neurodecodekit.cache.sentence_npz import LoadedSentenceCache
        from neurodecodekit.cache.signal_representation import load_sentence_cache_auto

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.npz"
            _write_sentence_cache(path)
            loaded = load_sentence_cache_auto(path)

        self.assertIsInstance(loaded, LoadedSentenceCache)
        self.assertEqual(loaded.target_texts.tolist(), ["AB", "BA"])

    def test_integer_encoding_refuses_implicit_clipping(self):
        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.cache.signal_representation import (
            load_signal_representation_cache,
            save_signal_representation_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "outside.npz"
            _write_sentence_cache(source_path, max_abs=6.0)
            source = load_sentence_npz_cache(source_path)

            with self.assertRaisesRegex(ValueError, "refusing implicit clipping"):
                save_signal_representation_cache(
                    root / "refused.npz",
                    source_cache=source,
                    encoding="qint8",
                    clip_abs=5.0,
                )
            self.assertFalse((root / "refused.npz").exists())

            save_signal_representation_cache(
                root / "allowed.npz",
                source_cache=source,
                encoding="qint8",
                clip_abs=5.0,
                allow_clipping=True,
            )
            loaded = load_signal_representation_cache(root / "allowed.npz")
            encoding = loaded.representation_metadata["storage"]["encoding"]
            self.assertGreater(encoding["source_values_outside_clip_count"], 0)
            self.assertLessEqual(float(abs(loaded.signals).max()), 5.0)

    def test_loader_rejects_payload_dtype_that_disagrees_with_metadata(self):
        import numpy as np

        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.cache.signal_representation import (
            SignalRepresentationSchemaError,
            load_signal_representation_cache,
            save_signal_representation_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "source.npz"
            path = root / "qint8.npz"
            _write_sentence_cache(source_path)
            save_signal_representation_cache(
                path,
                source_cache=load_sentence_npz_cache(source_path),
                encoding="qint8",
            )
            with np.load(path, allow_pickle=False) as data:
                arrays = {name: data[name].copy() for name in data.files}
            arrays["signal_payload"] = arrays["signal_payload"].astype("int16")
            np.savez_compressed(path, **arrays)

            with self.assertRaisesRegex(SignalRepresentationSchemaError, "dtype"):
                load_signal_representation_cache(path)

    def test_loader_rejects_wrong_representation_schema(self):
        import numpy as np

        from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
        from neurodecodekit.cache.signal_representation import (
            SignalRepresentationSchemaError,
            load_signal_representation_cache,
            save_signal_representation_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "source.npz"
            path = root / "float16.npz"
            _write_sentence_cache(source_path)
            save_signal_representation_cache(
                path,
                source_cache=load_sentence_npz_cache(source_path),
                encoding="float16",
            )
            with np.load(path, allow_pickle=False) as data:
                arrays = {name: data[name].copy() for name in data.files if name != "metadata"}
                metadata = json.loads(str(data["metadata"].item()))
            metadata["schema"]["name"] = "wrong"
            np.savez_compressed(path, **arrays, metadata=json.dumps(metadata))

            with self.assertRaisesRegex(SignalRepresentationSchemaError, "schema name"):
                load_signal_representation_cache(path)


def _write_sentence_cache(path: Path, *, max_abs: float = 5.0) -> None:
    import numpy as np

    from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
    from neurodecodekit.preprocess.ctc_text import encode_ctc_text

    input_lengths = np.asarray([20, 18], dtype="int32")
    signals = np.zeros((2, 3, 20), dtype="float32")
    for row_index, length in enumerate(input_lengths.tolist()):
        base = np.linspace(-max_abs, max_abs, length, dtype="float32")
        for channel_index in range(3):
            signals[row_index, channel_index, :length] = base / (channel_index + 1)
    texts = ["AB", "BA"]
    target_ids = np.asarray([encode_ctc_text(value) for value in texts], dtype="int16")
    save_sentence_npz_cache(
        path,
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_ids,
        target_lengths=np.asarray([2, 2], dtype="int32"),
        target_texts=np.asarray(texts, dtype="U"),
        reference_texts=np.asarray(texts, dtype="U"),
        mat_response_texts=np.asarray(texts, dtype="U"),
        trial_indices=np.asarray([10, 11], dtype="int32"),
        sentence_start_sec=np.asarray([1.0, 3.0], dtype="float64"),
        sentence_end_sec=np.asarray([1.2, 3.18], dtype="float64"),
        channel_names=np.asarray(["M1", "M2", "M3"], dtype="U"),
        metadata={
            "kind": "test_real_sentence_cache",
            "extraction_params": {"sfreq": 100.0, "clamp": 5.0},
            "source_files": {"raw": "fixture.fif", "events": "fixture.mat"},
            "warnings": ["test_only"],
        },
    )


if __name__ == "__main__":
    unittest.main()
