"""Focused checks of TimesFM integration boundaries; no checkpoint or real data."""

import unittest
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


f = load("src/neurodecodekit/models/timesfm_word_features.py", "feature_test")
r = load("src/neurodecodekit/experiments/timesfm_words.py", "runner_test")
report = load("src/neurodecodekit/evaluation/imagined_word_report.py", "report_test")


class ContractTests(unittest.TestCase):
    def test_all_17_arms_accepted_without_changing_old_scorer(self):
        aliases = [r.ALIASES.get(a, a) for a in r.ARMS]
        controls = ["prior", "metadata", "shuffled", "noise"]
        diagnostics = [a for a in aliases if a not in ["joint_hidden", *controls]]
        rows = [
            {
                "participant": "0",
                "session": "6",
                "trial_id": str(i),
                "probabilities": {a: [0.2] * 5 for a in aliases},
            }
            for i in range(5)
        ]
        targets = [
            {"participant": "0", "session": "6", "trial_id": str(i), "target": c}
            for i, c in enumerate(r.CLASSES)
        ]
        result = report.score_predictions(
            rows,
            targets,
            class_labels=r.CLASSES,
            primary_arm="joint_hidden",
            control_arms=controls,
            diagnostic_arms=diagnostics,
            expected_participants=["0"],
            heldout_session="6",
            bootstrap_samples=100,
        )
        self.assertEqual(len(result["summary_by_arm"]), 17)
        self.assertEqual(r.SESSIONS, (0, 1, 3, 4))
        self.assertEqual(r.TEST_SESSION, 6)


@unittest.skipUnless(
    importlib.util.find_spec("torch") and importlib.util.find_spec("scipy"),
    "optional numerical libraries",
)
class FeatureTests(unittest.TestCase):
    def test_channel_identity_and_all_target_mask(self):
        import numpy as np
        import torch

        calls = []

        class Fake:
            def forward(self, inputs, **kw):
                calls.append(inputs)
                self_output = inputs["values"][..., :1].repeat(1, 1, 1, 1280)
                return {"__call__:transformer_output": self_output}

        x = np.arange(2 * 8 * 128, dtype="float32").reshape(2, 8, 128) * 1e-6
        joint = f.extract_features(Fake(), x, mode="joint_hidden")
        independent = f.extract_features(Fake(), x, mode="independent_hidden")
        np.testing.assert_array_equal(joint, independent)
        self.assertEqual(joint.shape, (2, 10240))
        self.assertEqual(tuple(calls[0]["values"].shape), (2, 8, 4, 32))
        self.assertEqual(tuple(calls[1]["values"].shape), (16, 1, 4, 32))
        self.assertTrue(all(torch.all(c["patch_is_target"]) for c in calls))
        self.assertTrue(all(not torch.any(c["masks"]) for c in calls))

    def test_forecast_cannot_receive_observed_tail(self):
        import numpy as np
        import torch

        seen = []

        class Fake:
            quantiles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

            def decode(self, *, target, horizon):
                seen.append(target.clone())
                return torch.zeros((*target.shape[:2], horizon, 9))

        x = np.ones((1, 8, 128), dtype="float32") * 1e-6
        a = f.extract_features(Fake(), x, mode="forecast_residual")
        x[..., 64:] *= 3
        b = f.extract_features(Fake(), x, mode="forecast_residual")
        np.testing.assert_array_equal(seen[0].numpy(), seen[1].numpy())
        np.testing.assert_allclose(b, a * 3)
        self.assertEqual(a.shape, (1, 512))

    def test_resampling_rejects_wrong_geometry_and_nonfinite(self):
        import numpy as np

        for x in [np.zeros((1, 8, 499)), np.full((1, 8, 500), np.nan)]:
            with self.assertRaises(ValueError):
                f.resample_windows(x)
        self.assertEqual(f.resample_windows(np.zeros((2, 8, 500))).shape, (2, 8, 128))

    @unittest.skipUnless(importlib.util.find_spec("sklearn"), "optional sklearn")
    def test_other_test_rows_cannot_change_first_prediction(self):
        import numpy as np

        rng = np.random.default_rng(2)
        x = rng.normal(size=(60, 36))
        y = np.array(r.CLASSES * 12)
        test = rng.normal(size=(2, 36))
        a, labels = f.fit_readout(x, y, test)
        test[1] *= 1000
        b, _ = f.fit_readout(x, y, test)
        self.assertEqual(labels, r.CLASSES)
        np.testing.assert_allclose(a[0], b[0], atol=1e-12)


if __name__ == "__main__":
    unittest.main()
