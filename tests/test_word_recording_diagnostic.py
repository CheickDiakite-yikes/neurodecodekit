"""Small generated checks for the real diagnostic's split and scoring semantics."""

import importlib.util
from pathlib import Path
import unittest

PATH = (
    Path(__file__).resolve().parents[1]
    / "src/neurodecodekit/experiments/word_recording_diagnostic.py"
)
spec = importlib.util.spec_from_file_location("word_diagnostic", PATH)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional numpy")
class DiagnosticTests(unittest.TestCase):
    def fixture(self):
        ids, labels = [], []
        for p in range(2):
            for s in d.SESSIONS:
                for t in range(25):
                    if (p, s, t) == (1, 0, 24):
                        continue
                    ids.append({"participant": str(p), "session": str(s), "trial_id": str(t)})
                    labels.append(d.CLASSES[t % 5])
        return ids, labels

    def test_matched_counts_guards_and_exactly_once_coverage(self):
        from collections import Counter

        ids, labels = self.fixture()
        plan = list(d.splits(ids, labels))
        self.assertEqual(plan, list(d.splits(ids, labels)))
        covered = Counter()
        for split in plan:
            a, b, te = split["within"], split["cross"], split["test"]
            self.assertEqual(Counter(labels[i] for i in a), Counter(labels[i] for i in b))
            self.assertTrue(set(a).isdisjoint(te) and set(b).isdisjoint(te))
            self.assertGreater(len(a), 8)
            self.assertTrue(all(ids[i]["participant"] == split["participant"] for i in a + b + te))
            self.assertTrue(all(ids[i]["session"] == split["donor"] for i in b))
            self.assertTrue(all(ids[i]["session"] == split["session"] for i in a + te))
            self.assertTrue(
                all(
                    abs(int(ids[i]["trial_id"]) - int(ids[j]["trial_id"])) > 1
                    for i in a
                    for j in te
                )
            )
            self.assertTrue(all(int(ids[i]["trial_id"]) // 5 == split["fold"] for i in te))
            covered.update(te)
        self.assertEqual(covered, Counter(range(len(ids))))

    def test_closed_sessions_and_duplicates_refused(self):
        ids, labels = self.fixture()
        for session in (2, 5, 6):
            bad = [dict(r) for r in ids]
            bad[0]["session"] = str(session)
            with self.assertRaises(ValueError):
                list(d.splits(bad, labels))
        with self.assertRaises(ValueError):
            d.validate_development(ids + [ids[0]], labels + [labels[0]])

    def test_class_macro_scoring_not_trial_micro_scoring(self):
        import numpy as np

        y = np.array([0] * 20 + [1, 2, 3, 4])
        p = np.tile([0.6, 0.1, 0.1, 0.1, 0.1], (24, 1))
        values = d.metrics(p, y)
        self.assertAlmostEqual(values["balanced_accuracy"], 0.2)
        self.assertAlmostEqual(values["log_loss"], -(np.log(0.6) + 4 * np.log(0.1)) / 5)
        with self.assertRaises(ValueError):
            d.metrics(p * 2, y)

    @unittest.skipUnless(importlib.util.find_spec("sklearn"), "optional sklearn")
    def test_readout_cannot_fit_evaluation_statistics(self):
        import numpy as np

        rng = np.random.default_rng(9)
        x = rng.normal(size=(20, 36))
        y = np.array(list(d.CLASSES) * 4)
        e = rng.normal(size=(3, 36))
        a = d.fit(x, y, e)
        b = d.fit(x, y, np.vstack([e, np.full((1, 36), 1e6)]))
        np.testing.assert_allclose(a, b[:3], rtol=1e-12, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
