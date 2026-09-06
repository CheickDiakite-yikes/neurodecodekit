"""Development-only, matched within/cross recording diagnostic; no acquisition.

Heavy dependencies stay inside functions. Stages refuse existing outputs.
The historical TimesFM evaluation and mixed feature caches are never opened.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

SESSIONS = (0, 1, 3, 4)
CLASSES = ("down", "left", "right", "select", "up")
MODES = ("joint_hidden", "covariance", "temporal")
ARMS = tuple(a for m in MODES for a in (m, m + "_shuffled", m + "_noise")) + (
    "uniform",
    "prior",
    "metadata",
)
SEED = 20260906
INPUT_SHA = {
    "train.npy": "ee281590858b6eac2bed9a37ab90ffad2f599a396dfc43a3f0cc87f65cf58ac7",
    "calibration.json": "6240820e00627ed25819a314d3865abb8fabfc2a22cb1ef20f1187c841d7704a",
}
WEIGHTS_SHA = "a7592b0a8432baee54483254e5647856911ce69e09d09a9bb65904b2d98f17da"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def validate_development(ids, labels):
    if len(ids) != len(labels) or set(labels) != set(CLASSES):
        raise ValueError("Development vocabulary or row count differs")
    keys = [(r["participant"], r["session"], r["trial_id"]) for r in ids]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate trial identity")
    if any(int(s) not in SESSIONS or not 0 <= int(t) < 25 for _, s, t in keys):
        raise ValueError("Closed session or invalid trial")


def splits(ids, labels):
    """Deterministic group/guard separation and identical class counts."""
    import numpy as np

    validate_development(ids, labels)
    y = np.asarray(labels)
    for person in sorted({r["participant"] for r in ids}, key=int):
        for s in SESSIONS:
            donor = SESSIONS[(SESSIONS.index(s) + 1) % len(SESSIONS)]
            rec = [
                i
                for i, r in enumerate(ids)
                if r["participant"] == person and int(r["session"]) == s
            ]
            other = [
                i
                for i, r in enumerate(ids)
                if r["participant"] == person and int(r["session"]) == donor
            ]
            for fold in range(5):
                test = [i for i in rec if int(ids[i]["trial_id"]) // 5 == fold]
                if not test:
                    raise ValueError("Empty evaluation block")
                within = [
                    i
                    for i in rec
                    if all(abs(int(ids[i]["trial_id"]) - int(ids[j]["trial_id"])) > 1 for j in test)
                ]
                rng = np.random.default_rng(SEED + 100 * int(person) + 10 * s + fold)
                a, b, counts = [], [], []
                for c in CLASSES:
                    wa = [i for i in within if y[i] == c]
                    cb = [i for i in other if y[i] == c]
                    n = min(len(wa), len(cb), 4)
                    if n < 1:
                        raise ValueError("Training vocabulary incomplete")
                    a.extend(rng.choice(wa, n, replace=False).tolist())
                    b.extend(rng.choice(cb, n, replace=False).tolist())
                    counts.append(n)
                if len(a) <= 8:
                    raise ValueError("Insufficient training rows for PCA8")
                yield {
                    "participant": person,
                    "session": str(s),
                    "donor": str(donor),
                    "fold": fold,
                    "test": test,
                    "within": a,
                    "cross": b,
                    "class_counts": counts,
                }


def fit(train, labels, test):
    import warnings
    import numpy as np
    from sklearn.decomposition import PCA
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.exceptions import ConvergenceWarning

    if min(train.shape) <= 8 or not np.isfinite(train).all() or not np.isfinite(test).all():
        raise ValueError("Invalid PCA8 inputs")
    model = make_pipeline(
        StandardScaler(),
        PCA(8, whiten=True, svd_solver="randomized", random_state=SEED),
        LogisticRegression(C=0.1, max_iter=2000, tol=1e-8, solver="lbfgs"),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(train, labels)
    if not np.all(model.named_steps["pca"].explained_variance_ > 1e-12):
        raise ValueError("Training rank insufficient for PCA8")
    if model.classes_.tolist() != list(CLASSES):
        raise ValueError("Missing readout class")
    return model.predict_proba(test)


def features(old, out, code):
    import numpy as np

    for name, expected in INPUT_SHA.items():
        if sha(old / "prepared" / name) != expected:
            raise ValueError("Development input changed")
    meta = read(old / "prepared/calibration.json")
    validate_development(meta["identities"], meta["labels"])
    if len(meta["identities"]) != 1198:
        raise ValueError("Unexpected development size")
    if {r["participant"] for r in meta["identities"]} != {str(i) for i in range(12)}:
        raise ValueError("Unexpected participants")
    f = load_module(code / "models/timesfm_word_features.py", "dev_timesfm_features")
    cov = load_module(code / "models/imagined_word_decoder.py", "dev_covariance")
    x = f.resample_windows(np.load(old / "prepared/train.npy", allow_pickle=False))
    if len(x) != len(meta["identities"]):
        raise ValueError("Signal and identity mismatch")
    if sha(old / "checkpoint/model.safetensors") != WEIGHTS_SHA:
        raise ValueError("Checkpoint changed")
    model = f.load_frozen_model(
        old / "vendor/timesfm-0df95ae62085a6ac0d0afd1ad40dee2e6c1356ab/src",
        old / "checkpoint",
    )
    parts = []
    for start in range(0, len(x), 8):
        parts.append(f.extract_features(model, x[start : start + 8], mode="joint_hidden"))
        if start % 128 == 0:
            print(f"Development features: {start}/{len(x)}", flush=True)
    np.save(out / "joint_hidden.npy", np.concatenate(parts), allow_pickle=False)
    np.save(out / "covariance.npy", cov.covariance_log_features(x), allow_pickle=False)
    np.save(out / "temporal.npy", x.reshape(len(x), -1) * 1e6, allow_pickle=False)


def predict(old, root, out):
    import numpy as np

    meta = read(old / "prepared/calibration.json")
    ids, labels = meta["identities"], np.array(meta["labels"])
    plan = list(splits(ids, labels))
    xs = {m: np.load(root / "features" / (m + ".npy"), allow_pickle=False) for m in MODES}
    rng = np.random.default_rng(SEED)
    noise = {m: rng.normal(size=x.shape).astype(np.float32) for m, x in xs.items()}
    positions = np.array([int(r["trial_id"]) for r in ids])
    metadata = np.column_stack([positions / 24, (positions / 24) ** 2, np.eye(25)[positions]])
    predictions = np.full((2, len(ARMS), len(ids), 5), np.nan)
    coverage = np.zeros(len(ids), int)
    fits = 0
    for j, split in enumerate(plan):
        te = split["test"]
        coverage[te] += 1
        for k, condition in enumerate(("within", "cross")):
            tr = split[condition]
            yp = labels[tr]
            permutation = np.random.default_rng(SEED + j).permutation(len(tr))
            for m in MODES:
                for arm, x, y in (
                    (m, xs[m], yp),
                    (m + "_shuffled", xs[m], yp[permutation]),
                    (m + "_noise", noise[m], yp),
                ):
                    predictions[k, ARMS.index(arm), te] = fit(x[tr], y, x[te])
                    fits += 1
            counts = np.array([sum(yp == c) + 1 for c in CLASSES], float)
            predictions[k, ARMS.index("prior"), te] = counts / counts.sum()
            predictions[k, ARMS.index("uniform"), te] = 0.2
            predictions[k, ARMS.index("metadata"), te] = fit(metadata[tr], yp, metadata[te])
            fits += 1
        if j % 20 == 19:
            print(f"Finished {j + 1}/{len(plan)} matched folds", flush=True)
    if not np.all(coverage == 1) or not np.isfinite(predictions).all():
        raise ValueError("Incomplete or repeated evaluation coverage")
    np.save(out / "probabilities.npy", predictions, allow_pickle=False)
    dump(out / "split_plan.json", plan)
    dump(
        out / "freeze.json",
        {
            "experiment": "WORD-RECORDING-D1",
            "predictions_sha256": sha(out / "probabilities.npy"),
            "split_sha256": sha(out / "split_plan.json"),
            "arms": ARMS,
            "classes": CLASSES,
            "conditions": ["within", "cross"],
            "trials": len(ids),
            "folds": len(plan),
            "fits": fits,
            "input_sha256": INPUT_SHA,
        },
    )


def metrics(probabilities, targets):
    import numpy as np

    p, y = np.asarray(probabilities), np.asarray(targets)
    if p.shape != (len(y), 5) or not np.isfinite(p).all() or np.any(p < 0):
        raise ValueError("Invalid probabilities")
    if not np.allclose(p.sum(axis=1), 1) or set(y) != set(range(5)):
        raise ValueError("Incomplete vocabulary or probabilities do not sum to one")
    ll = -np.log(np.maximum(p[np.arange(len(y)), y], 1e-15))
    correct = p.argmax(axis=1) == y
    return {
        "log_loss": float(np.mean([ll[y == c].mean() for c in range(5)])),
        "balanced_accuracy": float(np.mean([correct[y == c].mean() for c in range(5)])),
    }


def score(old, root, out):
    import numpy as np

    freeze = read(root / "predict/freeze.json")
    if sha(root / "predict/probabilities.npy") != freeze["predictions_sha256"]:
        raise ValueError("Prediction digest differs")
    if sha(old / "prepared/calibration.json") != INPUT_SHA["calibration.json"]:
        raise ValueError("Development metadata differs")
    meta = read(old / "prepared/calibration.json")
    ids, y = meta["identities"], np.array([CLASSES.index(c) for c in meta["labels"]])
    p = np.load(root / "predict/probabilities.npy", allow_pickle=False)
    people = []
    for person in map(str, range(12)):
        arms = {}
        for k, condition in enumerate(("within", "cross")):
            for a, arm in enumerate(ARMS):
                per_recording = []
                for s in SESSIONS:
                    ix = [
                        i
                        for i, r in enumerate(ids)
                        if r["participant"] == person and int(r["session"]) == s
                    ]
                    per_recording.append(metrics(p[k, a, ix], y[ix]))
                arms[f"{condition}/{arm}"] = {
                    key: float(np.mean([v[key] for v in per_recording]))
                    for key in ("log_loss", "balanced_accuracy")
                }
        people.append({"participant": person, "arms": arms})
    summary = {
        arm: {
            key: float(np.mean([person["arms"][arm][key] for person in people]))
            for key in ("log_loss", "balanced_accuracy")
        }
        for arm in people[0]["arms"]
    }
    draws = np.random.default_rng(SEED).integers(0, 12, size=(4000, 12))
    comparisons = []
    for mode in MODES:
        for baseline in (
            f"cross/{mode}",
            "within/uniform",
            "within/prior",
            "within/metadata",
            f"within/{mode}_shuffled",
            f"within/{mode}_noise",
        ):
            treatment = f"within/{mode}"
            row = {"treatment": treatment, "baseline": baseline}
            for metric, sign in (("log_loss", -1), ("balanced_accuracy", 1)):
                gain = np.array(
                    [
                        sign * (v["arms"][treatment][metric] - v["arms"][baseline][metric])
                        for v in people
                    ]
                )
                row[metric + "_gain"] = {
                    "mean": float(gain.mean()),
                    "ci95_descriptive": np.quantile(
                        gain[draws].mean(axis=1), [0.025, 0.975]
                    ).tolist(),
                    "positive_people": int((gain > 0).sum()),
                }
            comparisons.append(row)
    plan = read(root / "predict/split_plan.json")
    counts = [len(s["within"]) for s in plan]
    result = {
        "experiment": "WORD-RECORDING-D1",
        "lane": "reused development diagnostic",
        "participants": 12,
        "recordings": 48,
        "trials": len(ids),
        "folds": len(plan),
        "training_count_range": [min(counts), max(counts)],
        "mean_training_count": float(np.mean(counts)),
        "freeze": freeze,
        "summary": summary,
        "people": people,
        "comparisons": comparisons,
        "interval_scope": "Unadjusted descriptive paired bootstrap across people; no significance declaration.",
    }
    dump(out / "aggregate.json", result)
    print(
        json.dumps({"summary": summary, "training_count_range": result["training_count_range"]}),
        flush=True,
    )


def run_worker(role, repo, root, old):
    out = root / role
    out.mkdir(parents=True, exist_ok=False)
    py = (repo / ".venv/bin/python").resolve()
    site = repo / ".venv/lib/python3.13/site-packages"
    code = repo / "src/neurodecodekit"

    def q(p):
        return json.dumps(str(Path(p).resolve()))

    profile = [
        "(version 1)",
        "(deny default)",
        '(import "dyld-support.sb")',
        "(allow sysctl-read)",
        "(allow process-info* (target self))",
        f"(allow process-exec (literal {q(py)}))",
    ]
    reads = [py.parent.parent, site, code, "/System", "/usr/lib", "/usr/share", "/Library/Apple"]
    files = ["/dev/null", "/dev/urandom", "/dev/random", old / "prepared/calibration.json"]
    if role == "features":
        reads += [old / "vendor", old / "checkpoint"]
        files.append(old / "prepared/train.npy")
    elif role == "predict":
        reads.append(root / "features")
    else:
        reads.append(root / "predict")
    for path in reads:
        profile += [
            f"(allow file-read* file-map-executable (subpath {q(path)}))",
            f"(allow file-read-metadata (path-ancestors {q(path)}))",
        ]
    for path in files:
        profile += [
            f"(allow file-read* (literal {q(path)}))",
            f"(allow file-read-metadata (path-ancestors {q(path)}))",
        ]
    profile += [
        f"(allow file-read* file-write* (subpath {q(out)}))",
        f"(allow file-read-metadata (path-ancestors {q(out)}))",
    ]
    args = [
        "/usr/bin/sandbox-exec",
        "-p",
        "\n".join(profile),
        str(py),
        "-I",
        "-S",
        str(Path(__file__).resolve()),
        role,
        "--internal",
        "--site",
        str(site),
        "--root",
        str(root),
        "--old",
        str(old),
    ]
    env = {
        "PATH": "/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "HF_HUB_OFFLINE": "1",
        "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
    }
    env.update(
        {
            n: "1"
            for n in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        }
    )
    start, peak = time.monotonic(), 0
    with (out / "worker.log").open("x") as log:
        child = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=out)
        try:
            while child.poll() is None:
                result = subprocess.run(
                    ["/bin/ps", "-o", "rss=", "-p", str(child.pid)], capture_output=True, text=True
                )
                if result.returncode and child.poll() is None:
                    raise RuntimeError("Cannot monitor worker memory")
                peak = max(peak, int(result.stdout.strip() or "0") * 1024)
                size = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
                if (
                    peak > 4 * 2**30
                    or time.monotonic() - start > 900
                    or size > 256 * 2**20
                    or shutil.disk_usage(root).free < 20 * 2**30
                ):
                    raise RuntimeError("Diagnostic resource cap reached")
                time.sleep(1)
        finally:
            if child.poll() is None:
                child.kill()
            child.wait()
    dump(
        out / "process.json",
        {
            "seconds": time.monotonic() - start,
            "sampled_peak_rss_bytes": peak,
            "returncode": child.returncode,
            "network_denied": True,
            "only_development_inputs_allowed": True,
        },
    )
    if child.returncode:
        raise RuntimeError(f"Worker failed; see {out / 'worker.log'}")
    print((out / "process.json").read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("features", "predict", "score"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--old", type=Path, required=True)
    parser.add_argument("--internal", action="store_true")
    parser.add_argument("--site")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    if not args.internal:
        run_worker(args.role, repo, args.root.resolve(), args.old.resolve())
        return
    sys.path.insert(0, args.site)
    from threadpoolctl import threadpool_limits

    start = time.monotonic()
    with threadpool_limits(limits=1):
        if args.role == "features":
            features(args.old, args.root / args.role, repo / "src/neurodecodekit")
        elif args.role == "predict":
            predict(args.old, args.root, args.root / args.role)
        else:
            score(args.old, args.root, args.root / args.role)
    dump(
        args.root / args.role / "measurement.json",
        {
            "seconds": time.monotonic() - start,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "threads": 1,
        },
    )


if __name__ == "__main__":
    main()
