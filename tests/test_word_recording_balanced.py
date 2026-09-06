"""The balanced intervention must leave balanced-training behavior unchanged."""

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "balanced_adapter", ROOT / "src/neurodecodekit/experiments/word_recording_balanced.py"
)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


@unittest.skipUnless(importlib.util.find_spec("sklearn"), "optional sklearn")
class BalancedTests(unittest.TestCase):
    def test_no_change_when_training_labels_balanced(self):
        import numpy as np

        rng = np.random.default_rng(12)
        x, e = rng.normal(size=(20, 36)), rng.normal(size=(4, 36))
        y = np.array(list(b.engine.CLASSES) * 4)
        np.testing.assert_allclose(b.engine.fit(x, y, e), b.balanced_fit(x, y, e), atol=1e-12)


if __name__ == "__main__":
    unittest.main()
