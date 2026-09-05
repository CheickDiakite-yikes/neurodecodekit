"""Generated numerical fixtures only; no recordings or external inputs."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.models.imagined_word_decoder import (
    ImaginedWordDecoder,
    covariance_log_features,
)


_NUMERICAL = all(importlib.util.find_spec(name) for name in (
    "numpy", "scipy", "sklearn", "threadpoolctl",
))


def _fixture(seed, repeats=12, n_classes=5):
    import numpy as np

    rng = np.random.default_rng(seed)
    labels = np.tile(np.arange(n_classes), repeats)
    epochs = rng.normal(size=(len(labels), 8, 96)) * 1e-6
    for epoch, label in zip(epochs, labels):
        epoch[label] *= 5.0
    return epochs, np.asarray([f"word-{label}" for label in labels])


class ConfigurationTests(unittest.TestCase):
    def test_invalid_parameters_and_unfitted_prediction(self):
        for value in (0, -1, 1.1, float("nan")):
            with self.assertRaises(ValueError):
                ImaginedWordDecoder(shrinkage=value)
        with self.assertRaises(ValueError):
            ImaginedWordDecoder(C=float("inf"))
        with self.assertRaisesRegex(RuntimeError, "fitted"):
            ImaginedWordDecoder().predict_proba([])


@unittest.skipUnless(_NUMERICAL, "optional numerical dependencies not installed")
class ImaginedWordDecoderTests(unittest.TestCase):
    def test_matrix_log_matches_analytic_diagonal_and_rotation(self):
        import numpy as np

        epoch = np.asarray([[1, -1, 1, -1], [2, 2, -2, -2]], dtype=float)
        diagonal = np.log([26 / 15, 74 / 15])
        np.testing.assert_allclose(
            covariance_log_features(epoch[None], shrinkage=0.2)[0],
            [diagonal[0], 0, diagonal[1]], atol=1e-12,
        )
        rotation = np.asarray([[0.8, -0.6], [0.6, 0.8]])
        expected = rotation @ np.diag(diagonal) @ rotation.T
        actual = covariance_log_features((rotation @ epoch)[None], shrinkage=0.2)[0]
        np.testing.assert_allclose(
            actual, [expected[0, 0], 2**0.5 * expected[0, 1], expected[1, 1]],
            atol=1e-12,
        )
        self.assertAlmostEqual(float(actual @ actual), float((expected**2).sum()))

    def test_demeaning_scale_and_rank_deficiency(self):
        import numpy as np

        epoch = np.asarray([[1, -1, 1, -1], [1, -1, 1, -1]], dtype=float)
        original = covariance_log_features(epoch[None])
        shifted = covariance_log_features((epoch + np.asarray([[30], [-40]]))[None])
        np.testing.assert_allclose(original, shifted, atol=1e-12)
        tiny = covariance_log_features((epoch * 1e-6)[None])
        np.testing.assert_allclose(
            tiny - original, [[2 * np.log(1e-6), 0, 2 * np.log(1e-6)]], atol=1e-12,
        )
        with self.assertRaisesRegex(ValueError, "variance"):
            covariance_log_features(np.ones((1, 2, 4)))

    def test_five_class_fit_inference_is_independent_of_prediction_batch(self):
        import numpy as np

        train, labels = _fixture(101)
        test, expected = _fixture(202, repeats=3)
        model = ImaginedWordDecoder().fit(train, labels)
        original_mean, original_scale = model.mean_.copy(), model.scale_.copy()
        probabilities = model.predict_proba(test)
        self.assertEqual(probabilities.shape, (15, 5))
        self.assertEqual(model.training_summary_["n_features"], 36)
        np.testing.assert_allclose(probabilities.sum(axis=1), 1.0, atol=1e-14)
        self.assertGreaterEqual(float(np.mean(model.predict(test) == expected)), 0.9)
        separate = np.vstack([model.predict_proba(row[None]) for row in test])
        np.testing.assert_allclose(probabilities, separate, atol=1e-14)
        model.predict_proba(test * 1000)
        np.testing.assert_array_equal(model.mean_, original_mean)
        np.testing.assert_array_equal(model.scale_, original_scale)
        expected_features = covariance_log_features(train)
        np.testing.assert_allclose(model.mean_, expected_features.mean(axis=0))
        with self.assertRaisesRegex(RuntimeError, "already fitted"):
            model.fit(train, labels)

    def test_binary_and_multiclass_round_trip_without_pickle(self):
        import numpy as np

        for n_classes in (2, 5):
            train, labels = _fixture(10, n_classes=n_classes)
            test, _ = _fixture(11, repeats=2, n_classes=n_classes)
            model = ImaginedWordDecoder().fit(train, labels)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "model.npz"
                model.save(path)
                with np.load(path, allow_pickle=False) as archive:
                    self.assertTrue(all(archive[key].dtype.kind != "O" for key in archive.files))
                loaded = ImaginedWordDecoder.load(path)
                np.testing.assert_array_equal(loaded.classes_, model.classes_)
                np.testing.assert_allclose(loaded.predict_proba(test), model.predict_proba(test))
                with self.assertRaises(FileExistsError):
                    model.save(path)

    def test_malformed_shapes_and_nonfinite_inputs_are_rejected(self):
        import numpy as np

        train, labels = _fixture(7)
        model = ImaginedWordDecoder().fit(train, labels)
        for value in (train[:, :7], train[:, :, :90], np.full_like(train, np.nan)):
            with self.assertRaises(ValueError):
                model.predict_proba(value)
        with self.assertRaisesRegex(ValueError, "one label"):
            ImaginedWordDecoder().fit(train, labels[:-1])
        with self.assertRaisesRegex(ValueError, "two nonempty"):
            ImaginedWordDecoder().fit(train, ["only"] * len(train))

    def test_load_rejects_nonpositive_scale(self):
        import numpy as np

        train, labels = _fixture(6)
        model = ImaginedWordDecoder().fit(train, labels)
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp) / "good.npz", Path(tmp) / "bad.npz"
            model.save(good)
            with np.load(good, allow_pickle=False) as archive:
                arrays = {key: archive[key] for key in archive.files}
            arrays["scale"][0] = 0.0
            np.savez_compressed(bad, **arrays)
            with self.assertRaisesRegex(ValueError, "scale"):
                ImaginedWordDecoder.load(bad)


if __name__ == "__main__":
    unittest.main()
