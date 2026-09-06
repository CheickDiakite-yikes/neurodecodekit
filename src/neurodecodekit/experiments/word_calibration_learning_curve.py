"""D4: matched calibration-size learning curves on development-only features."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import resource
import sys
import time

spec = importlib.util.spec_from_file_location(
    "d4_worker", Path(__file__).with_name("word_timing_diagnostic.py")
)
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
d = t.d
REPO, BASE = t.REPO, t.BASE
WINDOWS = ("early", "late")
SIZES = (15, 30, 60)
COUNTS = (1, 2, 4)
FEATURE_ROOTS = {
    "early": REPO / ".codex_work/word-timing-d3/features",
    "late": REPO / ".codex_work/word-recording-d1/features",
}
HASHES = {
    "early": {
        "joint_hidden": "230c90385fefb454941d21ca67060625a49fa06050eb87b99a80b5506055c978",
        "covariance": "2441476ff05697a8e770deccbbace7cb6d79e7625365b23bb39b0105e45c6135",
        "temporal": "010d9a3648b4ac76b38da70a2bb8ac52496a1b526170bf39956a82e66a7e8ea5",
    },
    "late": {
        "joint_hidden": "9a966c187983008272a888cd2ceca6d7d31163b31bd6c075b739f3b931c853bd",
        "covariance": "062df046d438dd4a3ca91a068418fbc984c197aba36886507a7040a37f681597",
        "temporal": "1f244c6115b6f3d7fdcb44632aeab10a2ba60edffa61d28ecc70b655a9930e62",
    },
}
DIMS = {"joint_hidden": 10240, "covariance": 36, "temporal": 1024}
NULLS = ("uniform", "prior", "metadata", "shuffled", "noise")


def nested_splits(ids, labels):
    """Same three donors at every size; nested class-balanced subsets."""
    import numpy as np

    d.validate_development(ids, labels)
    plan = []
    for person in sorted({r["participant"] for r in ids}, key=int):
        for held in d.SESSIONS:
            test = [
                i
                for i, r in enumerate(ids)
                if r["participant"] == person and int(r["session"]) == held
            ]
            if not test:
                raise ValueError("Empty held recording")
            pools = []
            donors = [s for s in d.SESSIONS if s != held]
            for donor in donors:
                per_class = []
                for c, word in enumerate(d.CLASSES):
                    pool = [
                        i
                        for i, r in enumerate(ids)
                        if r["participant"] == person
                        and int(r["session"]) == donor
                        and labels[i] == word
                    ]
                    if len(pool) < 4:
                        raise ValueError("Every donor/class needs at least four examples")
                    rng = np.random.default_rng(
                        d.SEED + 10000 * int(person) + 1000 * held + 100 * donor + c
                    )
                    per_class.append(rng.permutation(pool).tolist())
                pools.append(per_class)
            selections = {
                str(n): [i for donor in pools for pool in donor for i in pool[:k]]
                for n, k in zip(SIZES, COUNTS)
            }
            plan.append(
                {
                    "participant": person,
                    "held_session": str(held),
                    "donors": donors,
                    "test": test,
                    "train": selections,
                }
            )
    return plan


def fit(train, labels, test):
    """Fixed PCA8; keep penalty strength on mean loss constant across N."""
    import warnings
    import numpy as np
    from sklearn.decomposition import PCA
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.exceptions import ConvergenceWarning

    n = len(train)
    if n not in SIZES or min(train.shape) <= 8:
        raise ValueError("Invalid training dimensions")
    if not np.isfinite(train).all() or not np.isfinite(test).all():
        raise ValueError("Nonfinite input")
    if any(sum(labels == c) != n // 5 for c in d.CLASSES):
        raise ValueError("Calibration classes must be balanced")
    model = make_pipeline(
        StandardScaler(),
        PCA(8, whiten=True, svd_solver="randomized", random_state=d.SEED),
        LogisticRegression(
            C=1.5 / n, max_iter=2000, tol=1e-8, solver="lbfgs", class_weight="balanced"
        ),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(train, labels)
    if not np.all(model.named_steps["pca"].explained_variance_ > 1e-12):
        raise ValueError("Training rank insufficient for PCA8")
    if model.classes_.tolist() != list(d.CLASSES):
        raise ValueError("Missing class")
    return model.predict_proba(test)


def load_metadata():
    path = BASE / "prepared/calibration.json"
    if d.sha(path) != d.INPUT_SHA["calibration.json"]:
        raise ValueError("Calibration changed")
    meta = d.read(path)
    if len(meta["identities"]) != 1198:
        raise ValueError("Unexpected development count")
    d.validate_development(meta["identities"], meta["labels"])
    return meta


def predict(root, out):
    import numpy as np

    meta = load_metadata()
    ids, labels = meta["identities"], np.array(meta["labels"])
    plan = nested_splits(ids, labels)
    if len(plan) != 48:
        raise ValueError("Expected 48 held-recording folds")
    xs = {}
    for window in WINDOWS:
        for mode in d.MODES:
            path = FEATURE_ROOTS[window] / (mode + ".npy")
            if d.sha(path) != HASHES[window][mode]:
                raise ValueError("Development feature identity changed")
            x = np.load(path, allow_pickle=False)
            if x.shape != (1198, DIMS[mode]) or not np.isfinite(x).all():
                raise ValueError("Invalid development features")
            xs[window, mode] = x
    rng = np.random.default_rng(d.SEED)
    noise = {m: rng.normal(size=(1198, DIMS[m])).astype(np.float32) for m in d.MODES}
    positions = np.array([int(r["trial_id"]) for r in ids])
    metadata = np.column_stack([positions / 24, (positions / 24) ** 2, np.eye(25)[positions]])
    p = np.full((2, 3, len(d.ARMS), len(ids), 5), np.nan)
    coverage = np.zeros((3, len(ids)), int)
    fits = 0
    for j, split in enumerate(plan):
        te = split["test"]
        for k, n in enumerate(SIZES):
            tr = split["train"][str(n)]
            yp = labels[tr]
            shuffled = yp.copy()
            shuffle_rng = np.random.default_rng(d.SEED + 100 * j + n)
            for donor in split["donors"]:
                ix = [i for i, row in enumerate(tr) if int(ids[row]["session"]) == donor]
                shuffled[ix] = yp[shuffle_rng.permutation(ix)]
            coverage[k, te] += 1
            counts = np.array([sum(yp == c) + 1 for c in d.CLASSES], float)
            shared = {
                "uniform": np.full((len(te), 5), 0.2),
                "prior": np.tile(counts / counts.sum(), (len(te), 1)),
                "metadata": fit(metadata[tr], yp, metadata[te]),
            }
            fits += 1
            for mode in d.MODES:
                shared[mode + "_noise"] = fit(noise[mode][tr], yp, noise[mode][te])
                fits += 1
                for w, window in enumerate(WINDOWS):
                    x = xs[window, mode]
                    for arm, y in ((mode, yp), (mode + "_shuffled", shuffled)):
                        p[w, k, d.ARMS.index(arm), te] = fit(x[tr], y, x[te])
                        fits += 1
            for arm, values in shared.items():
                for w in range(2):
                    p[w, k, d.ARMS.index(arm), te] = values
        if j % 8 == 7:
            print(f"Finished {j + 1}/48 held recordings, {fits} fits", flush=True)
    if not np.all(coverage == 1) or not np.isfinite(p).all():
        raise ValueError("Incomplete/repeated coverage")
    np.save(out / "probabilities.npy", p, allow_pickle=False)
    d.dump(out / "split_plan.json", plan)
    d.dump(
        out / "freeze.json",
        {
            "experiment": "WORD-CALIBRATION-D4",
            "windows": list(WINDOWS),
            "sizes": list(SIZES),
            "arms": list(d.ARMS),
            "classes": list(d.CLASSES),
            "shape": list(p.shape),
            "predictions_sha256": d.sha(out / "probabilities.npy"),
            "split_sha256": d.sha(out / "split_plan.json"),
            "feature_sha256": HASHES,
            "calibration_sha256": d.INPUT_SHA["calibration.json"],
            "design_sha256": d.sha(root / "design.json"),
            "fits": fits,
            "trials": len(ids),
            "folds": len(plan),
            "C_by_size": {str(n): 1.5 / n for n in SIZES},
        },
    )


def verify_freeze(root):
    freeze = d.read(root / "predict/freeze.json")
    for name, expected in (
        ("windows", list(WINDOWS)),
        ("sizes", list(SIZES)),
        ("arms", list(d.ARMS)),
        ("classes", list(d.CLASSES)),
        ("shape", [2, 3, len(d.ARMS), 1198, 5]),
    ):
        if freeze[name] != expected:
            raise ValueError("Frozen axes differ")
    for path, key in (
        ("predict/probabilities.npy", "predictions_sha256"),
        ("predict/split_plan.json", "split_sha256"),
        ("design.json", "design_sha256"),
    ):
        if d.sha(root / path) != freeze[key]:
            raise ValueError("Frozen digest differs")
    return freeze


def score(root, out):
    import numpy as np

    freeze = verify_freeze(root)
    meta = load_metadata()
    ids, y = meta["identities"], np.array([d.CLASSES.index(c) for c in meta["labels"]])
    p = np.load(root / "predict/probabilities.npy", allow_pickle=False)
    if list(p.shape) != freeze["shape"]:
        raise ValueError("Probability shape differs")
    for arm in ("uniform", "prior", "metadata", *(m + "_noise" for m in d.MODES)):
        if not np.array_equal(p[0, :, d.ARMS.index(arm)], p[1, :, d.ARMS.index(arm)]):
            raise ValueError("Input-independent controls differ across windows")
    if not np.array_equal(p[:, :, d.ARMS.index("uniform")], p[:, :, d.ARMS.index("prior")]):
        raise ValueError("Balanced prior differs from uniform")
    people = []
    for person in map(str, range(12)):
        arms = {}
        for w, window in enumerate(WINDOWS):
            for k, size in enumerate(SIZES):
                for a, arm in enumerate(d.ARMS):
                    recording_metrics = []
                    for session in d.SESSIONS:
                        ix = [
                            i
                            for i, r in enumerate(ids)
                            if r["participant"] == person and int(r["session"]) == session
                        ]
                        recording_metrics.append(d.metrics(p[w, k, a, ix], y[ix]))
                    arms[f"{window}/{size}/{arm}"] = {
                        key: float(np.mean([r[key] for r in recording_metrics]))
                        for key in ("log_loss", "balanced_accuracy")
                    }
        people.append({"participant": person, "arms": arms})
    summary = {
        arm: {
            key: float(np.mean([v["arms"][arm][key] for v in people]))
            for key in ("log_loss", "balanced_accuracy")
        }
        for arm in people[0]["arms"]
    }
    draws = np.random.default_rng(d.SEED).integers(0, 12, size=(4000, 12))

    def contrast(a, b, c=None, e=None):
        result = {}
        for metric, sign in (("log_loss", -1), ("balanced_accuracy", 1)):
            values = np.array(
                [sign * (v["arms"][a][metric] - v["arms"][b][metric]) for v in people]
            )
            if c is not None:
                values -= np.array(
                    [sign * (v["arms"][c][metric] - v["arms"][e][metric]) for v in people]
                )
            result[metric + "_gain"] = {
                "mean": float(values.mean()),
                "positive_people": int((values > 0).sum()),
                "ci95_descriptive": np.quantile(
                    values[draws].mean(axis=1), [0.025, 0.975]
                ).tolist(),
            }
        return result

    comparisons = []
    for window in WINDOWS:
        for mode in d.MODES:
            big, small = f"{window}/60/{mode}", f"{window}/15/{mode}"
            row = {
                "window": window,
                "mode": mode,
                "gain_15_to_60": contrast(big, small),
                "at_60_vs": {},
                "gain_minus_control_gain": {},
            }
            for null in NULLS:
                arm = mode + "_" + null if null in ("shuffled", "noise") else null
                nb, ns = f"{window}/60/{arm}", f"{window}/15/{arm}"
                row["at_60_vs"][null] = contrast(big, nb)
                row["gain_minus_control_gain"][null] = contrast(big, small, nb, ns)
            comparisons.append(row)
    d.dump(
        out / "aggregate.json",
        {
            "experiment": "WORD-CALIBRATION-D4",
            "lane": "reused-development learning curve",
            "participants": 12,
            "recordings": 48,
            "trials": 1198,
            "folds": 48,
            "sizes": list(SIZES),
            "primary": "late/joint_hidden, log_loss",
            "freeze": freeze,
            "summary": summary,
            "people": people,
            "comparisons": comparisons,
            "bootstrap": {
                "seed": d.SEED,
                "rng": "numpy.default_rng PCG64",
                "resamples": 4000,
                "unit": "person",
                "order": "numeric",
                "shared_draws": True,
                "quantile_method": "linear",
                "descriptive_unadjusted": True,
            },
            "identical_controls_across_windows": True,
            "prior_equals_uniform": True,
            "claim_scope": "Offline prompted-word conditions, known people, reused development; no neural or isolated inner-speech attribution.",
        },
    )


def permissions(role, root):
    files = [BASE / "prepared/calibration.json", root / "design.json"]
    if role == "predict":
        files += [p / (m + ".npy") for p in FEATURE_ROOTS.values() for m in d.MODES]
    elif role == "score":
        files += [
            root / "predict" / name
            for name in ("probabilities.npy", "freeze.json", "split_plan.json")
        ]
    else:
        raise ValueError("Unsupported stage")
    return [], files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("predict", "score"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--internal", action="store_true")
    parser.add_argument("--site")
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.internal:
        t.__file__ = __file__
        t.permissions = permissions
        t.worker(args.role, root)
        return
    sys.path.insert(0, args.site)
    from threadpoolctl import threadpool_limits

    started = time.monotonic()
    design = d.read(root / "design.json")
    for path, digest in design["code_sha256"].items():
        if d.sha(REPO / path) != digest:
            raise ValueError("Declared implementation changed")
    with threadpool_limits(limits=1):
        {"predict": predict, "score": score}[args.role](root, root / args.role)
    d.dump(
        root / args.role / "measurement.json",
        {
            "seconds": time.monotonic() - started,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "threads": 1,
        },
    )


if __name__ == "__main__":
    main()
