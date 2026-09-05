"""Small generated checks for the exact SMR-D1 runner; never contact a source."""

import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest

from neurodecodekit.experiments import eegmmidb_smr_d1 as smr


NUMERICAL = all(importlib.util.find_spec(name) for name in ("numpy", "scipy", "mne"))


def generated_edf(path, flip=False):
    """A 112-second, 64-channel EDF+C with fourteen balanced task events."""
    import numpy as np
    channels = [name for pair in smr.PAIRS for name in pair] + [f"X{i}" for i in range(52)]
    n = 65

    def field(value, width):
        return str(value).encode("ascii").ljust(width, b" ")

    header = b"".join(field(value, width) for value, width in (
        (0, 8), ("generated", 80), ("generated", 80), ("01.01.00", 8), ("00.00.00", 8),
        (256+256*n, 8), ("EDF+C", 44), (112, 8), (1, 8), (n, 4)))
    for values, width in ((channels+["EDF Annotations"], 16), ([""]*n, 80),
                          (["uV"]*64+[""], 8), ([-100]*n, 8), ([100]*n, 8),
                          ([-32768]*n, 8), ([32767]*n, 8), ([""]*n, 80),
                          ([160]*64+[64], 8), ([""]*n, 32)):
        header += b"".join(field(value, width) for value in values)
    with Path(path).open("wb") as stream:
        stream.write(header)
        for second in range(112):
            t = np.arange(160)/160+second
            for channel in range(64):
                uv = (10+channel/10)*np.sin(2*np.pi*10*t+channel/5)
                digital = np.rint((uv+100)*65535/200-32768).astype("<i2")
                stream.write(digital.tobytes())
            annotations = f"+{second}\x14\x14\x00".encode()
            if second >= 4 and (second-4) % 8 == 0:
                label = ((second-4)//8) % 2
                label = 1-label if flip else label
                annotations += f"+{second}\x154\x14T{label+1}\x14\x00".encode()
            stream.write(annotations.ljust(128, b"\x00"))


class SMRContractTests(unittest.TestCase):
    def test_sattolo_has_no_fixed_points(self):
        order = smr.sattolo(14)
        self.assertEqual(sorted(order), list(range(14)))
        self.assertTrue(all(i != j for i, j in enumerate(order)))
        self.assertEqual(sum(math.comb(20, k) for k in range(15, 21))/2**20,
                         0.020694732666015625)

    def test_zero_body_budget_refuses_before_transfer(self):
        state = {}
        with self.assertRaisesRegex(smr.Park, "BODY_CAP_EXHAUSTED"):
            smr.curl_request(None, "META", "https://invalid.invalid", None, 0, state)
        self.assertEqual(state, {})


@unittest.skipUnless(NUMERICAL, "optional numpy/scipy/mne are not installed")
class SMRNumericalTests(unittest.TestCase):
    def test_si_power_and_class_macro_metrics(self):
        import numpy as np
        t = np.arange(320)/160
        x = np.tile(2e-6*np.sin(2*np.pi*10*t), (3, 1))
        power = np.exp(smr.spectral_features(x).reshape(3, 3))
        np.testing.assert_allclose(power[:, 0], 2e-12, rtol=1e-12)
        np.testing.assert_allclose(power[:, 1:], 1e-24, rtol=1e-12)
        y = np.array([0, 0, 0, 1])
        p = np.array([[.8, .2]]*3+[[.2, .8]])
        np.testing.assert_allclose(smr.metrics(y, p), [1, -math.log(.8), .04])
        with self.assertRaisesRegex(smr.Park, "INVALID_PROBABILITY"):
            smr.metrics(y, np.ones((4, 2)))

    def test_training_weights_equalize_people_and_classes(self):
        import numpy as np
        y = np.array([0]*4+[1]*8+[0]*12+[1]*4)
        groups = np.array([0]*12+[1]*16)
        w = smr.weights(y, groups)
        for person in (0, 1):
            for label in (0, 1):
                self.assertAlmostEqual(float(w[(groups == person) & (y == label)].sum()), 7)

    def test_edf_units_and_mask_are_invariant_to_labels(self):
        import numpy as np
        with tempfile.TemporaryDirectory(prefix="smr-generated-edf-") as directory:
            a, b = Path(directory)/"a.edf", Path(directory)/"b.edf"
            generated_edf(a)
            generated_edf(b, flip=True)
            x, y, permutation, kept, total = smr.extract_run(a)
            other, flipped, second_permutation, second_kept, second_total = smr.extract_run(b)
            self.assertEqual((len(y), total, second_total), (14, 14, 14))
            np.testing.assert_array_equal(flipped, 1-y)
            np.testing.assert_array_equal(permutation, second_permutation)
            np.testing.assert_array_equal(kept, second_kept)
            for arm in smr.ARMS:
                np.testing.assert_array_equal(x[arm], other[arm])
                self.assertTrue(np.isfinite(x[arm]).all())
                self.assertEqual(x[arm].shape, (14, 2 if arm == "metadata" else 11))
            # Known microvolt signals cannot produce log power near unscaled units.
            self.assertTrue((x["central"][:, 2:] < -20).all())
            np.testing.assert_array_equal(x["central"][:, :2], x["deranged"][:, :2])
            np.testing.assert_array_equal(x["central"][permutation, 2:], x["deranged"][:, 2:])

    def test_generated_score_has_all_edges_and_actual_delivery_counts(self):
        import numpy as np
        with tempfile.TemporaryDirectory(prefix="smr-generated-score-") as directory:
            root = Path(directory)
            y = np.tile([0, 1], 140)
            groups = np.repeat(np.arange(20), 14)
            rows = np.arange(280)
            p = np.column_stack([np.where(y == 0, .8, .2), np.where(y == 1, .8, .2)])
            controls = {arm: np.full((280, 2), .5) for arm in smr.ALL_ARMS if arm != "central"}
            np.savez(root/"p.npz", central=p, groups=groups, rows=rows, **controls)
            mapping = np.concatenate([np.array(smr.sattolo(14))+i*14 for i in range(20)])
            np.savez(root/"y.npz", y=y, groups=groups, rows=rows, derange_index=mapping)
            smr.numerical_worker("score", [root/"p.npz", root/"y.npz"], root)
            result = smr.read_json(root/"scientific_result.json")
            self.assertEqual(len(result["edges"]), 7)
            self.assertTrue(result["conjunction_passed"])
            for edge in result["edges"].values():
                self.assertEqual(edge["wins_above_002"], 20)
                self.assertAlmostEqual(edge["mean_increment"], math.log(1.6))
            self.assertEqual(smr.read_json(root/"score_counts.json"),
                             {"target_read_started": 1, "target_deliveries": 1, "scores_completed": 1})

    @unittest.skipUnless(sys.platform == "darwin" and os.environ.get("SMR_OS_FIXTURE") == "1",
                         "explicit local generated OS broker smoke only")
    def test_os_broker_emits_label_free_confirmation_features(self):
        import numpy as np
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="smr-generated-broker-") as directory:
            root = Path(directory).resolve()
            for name in ("raw", "features", "sealed", "tmp"):
                (root/name).mkdir()
            generated_edf(root/"raw/S041R11.edf")
            shutil.copyfile(smr.__file__, root/"runner.py")
            smr.write_json(root/"manifest.json", [{"partition": "confirmation", "participant": "S041",
                                                   "run": 11, "path": "S041/S041R11.edf"}])
            state = {"_root": str(root), "numerical_seconds": 0., "started_unix": time.time(),
                     "peak_process_tree_rss_bytes": 0, "peak_incremental_disk_bytes": 0,
                     "fit_calls_started": 0, "fits_completed": 0}
            smr.launch_worker(repo, root, "broker_confirmation", [root, root/"manifest.json"], state)
            with np.load(root/"features/confirmation.npz", allow_pickle=False) as data:
                self.assertNotIn("y", data.files)
                self.assertEqual(data["central"].shape, (14, 11))
            self.assertTrue((root/"sealed/targets.npz").is_file())
            print("GENERATED_BROKER_MEASUREMENTS " + json.dumps(state))


if __name__ == "__main__":
    unittest.main()
