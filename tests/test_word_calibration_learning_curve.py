"""Generated checks of D4 isolation and nested calibration; no real inputs."""

from collections import Counter
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "calibration_d4",
    Path(__file__).parents[1] / "src/neurodecodekit/experiments/word_calibration_learning_curve.py",
)
d4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d4)


def fixture():
    ids, labels = [], []
    for s in d4.d.SESSIONS:
        for i in range(25):
            ids.append({"participant": "0", "session": str(s), "trial_id": str(i)})
            labels.append(d4.d.CLASSES[i % 5])
    return ids, labels


class CalibrationCurveTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy")
    def test_nested_balanced_disjoint_and_complete(self):
        ids, labels = fixture()
        plan = d4.nested_splits(ids, labels)
        self.assertEqual(plan, d4.nested_splits(ids, labels))
        self.assertEqual(len(plan), 4)
        for n in d4.SIZES:
            coverage = Counter(i for fold in plan for i in fold["test"])
            self.assertEqual(coverage, Counter(range(100)))
            for fold in plan:
                tr, te = fold["train"][str(n)], fold["test"]
                self.assertEqual(len(tr), n)
                self.assertEqual(len(set(tr)), n)
                self.assertFalse(set(tr) & set(te))
                self.assertTrue(all(ids[i]["session"] != fold["held_session"] for i in tr))
                cells = Counter((ids[i]["session"], labels[i]) for i in tr)
                self.assertEqual(len(cells), 15)
                self.assertEqual(set(cells.values()), {n // 15})
        for fold in plan:
            a, b, c = (set(fold["train"][str(n)]) for n in d4.SIZES)
            self.assertTrue(a < b < c)
        # Target labels must not change that fold's donor selection.
        changed = labels.copy()
        for i in plan[0]["test"]:
            changed[i] = d4.d.CLASSES[(d4.d.CLASSES.index(labels[i]) + 1) % 5]
        self.assertEqual(plan[0], d4.nested_splits(ids, changed)[0])

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy")
    def test_insufficient_pool_refuses_without_replacement(self):
        ids, labels = fixture()
        pairs = [
            (r, y)
            for r, y in zip(ids, labels)
            if not (r["session"] == "0" and r["trial_id"] in ("0", "5"))
        ]
        with self.assertRaisesRegex(ValueError, "four examples"):
            d4.nested_splits([r for r, _ in pairs], [y for _, y in pairs])

    def test_exact_stage_permissions(self):
        root = Path("/tmp/d4-generated")
        reads, files = d4.permissions("predict", root)
        self.assertEqual(reads, [])
        expected = {d4.BASE / "prepared/calibration.json", root / "design.json"}
        expected.update(p / (m + ".npy") for p in d4.FEATURE_ROOTS.values() for m in d4.d.MODES)
        self.assertEqual(set(files), expected)
        reads, files = d4.permissions("score", root)
        self.assertEqual(reads, [])
        self.assertEqual(
            set(files),
            {
                d4.BASE / "prepared/calibration.json",
                root / "design.json",
                *(
                    root / "predict" / n
                    for n in ("probabilities.npy", "freeze.json", "split_plan.json")
                ),
            },
        )
        with self.assertRaises(ValueError):
            d4.permissions("features", root)

    def test_freeze_rejects_axis_and_digest_drift(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "predict").mkdir()
            for p in ("predict/probabilities.npy", "predict/split_plan.json", "design.json"):
                (root / p).write_bytes(b"generated identity bytes")
            freeze = {
                "windows": list(d4.WINDOWS),
                "sizes": list(d4.SIZES),
                "arms": list(d4.d.ARMS),
                "classes": list(d4.d.CLASSES),
                "shape": [2, 3, len(d4.d.ARMS), 1198, 5],
                "predictions_sha256": d4.d.sha(root / "predict/probabilities.npy"),
                "split_sha256": d4.d.sha(root / "predict/split_plan.json"),
                "design_sha256": d4.d.sha(root / "design.json"),
            }
            import json

            path = root / "predict/freeze.json"
            path.write_text(json.dumps(freeze))
            self.assertEqual(d4.verify_freeze(root), freeze)
            path.write_text(json.dumps(dict(freeze, sizes=[60, 30, 15])))
            with self.assertRaisesRegex(ValueError, "axes"):
                d4.verify_freeze(root)
            path.write_text(json.dumps(freeze))
            (root / "predict/probabilities.npy").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "digest"):
                d4.verify_freeze(root)


if __name__ == "__main__":
    unittest.main()
