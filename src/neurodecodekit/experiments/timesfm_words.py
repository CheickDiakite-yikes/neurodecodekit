"""One bounded, local TimesFM word comparison; no automatic acquisition or score.

Run `python .../timesfm_words.py --help`. Numerical dependencies are optional.
Workers use OS file whitelists and disabled network; targets are broker/scorer only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tarfile
import time

SESSIONS = (0, 1, 3, 4)
TEST_SESSION = 6
REVISION = "4ba1bb516d6cc98917143b0dfca23947935c7b15"
WEIGHTS_SHA = "a7592b0a8432baee54483254e5647856911ce69e09d09a9bb65904b2d98f17da"
CLASSES = ["down", "left", "right", "select", "up"]
MODES = ["joint_hidden", "independent_hidden", "forecast_residual", "covariance", "temporal"]
ARMS = [name for m in MODES for name in (m, m + "_shuffled", m + "_noise")] + ["prior", "metadata"]
ALIASES = {"joint_hidden_shuffled": "shuffled", "joint_hidden_noise": "noise"}
CHANNELS = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "OZ", "PO8"]


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(2**20), b""):
            h.update(b)
    return h.hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def budget(root):
    used = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    if used > 2 * 2**30 or shutil.disk_usage(root).free < 20 * 2**30:
        raise RuntimeError("Invocation 2 GiB or free-disk 20 GiB limit reached")
    return used


def fetch(url, path, cap):
    subprocess.run(
        [
            "/usr/bin/curl",
            "--fail",
            "--silent",
            "--show-error",
            "--location",
            "--proto",
            "=https",
            "--proto-redir",
            "=https",
            "--max-time",
            "90",
            "--max-filesize",
            str(cap),
            "--output",
            str(path),
            url,
        ],
        check=True,
    )
    if path.stat().st_size > cap:
        raise RuntimeError("Download exceeds bound")


def acquire(root):
    if (root / "acquired.json").exists():
        raise RuntimeError("Acquisition already completed")
    started = time.monotonic()
    archive = root / "source_metadata.tar.gz"
    fetch(
        f"https://codeload.github.com/OpenNeuroDatasets/ds005262/tar.gz/{REVISION}", archive, 2**20
    )
    rows = []
    with tarfile.open(archive) as tar:
        for member in tar:
            path = member.name.split("/", 1)[-1]
            match = re.fullmatch(
                r"sub-(\d+)/ses-6/eeg/sub-\1_ses-6_task-innerspeech_eeg\.(eeg|vhdr|vmrk)", path
            )
            if not match or int(match[1]) >= 12:
                continue
            key = re.search(r"SHA256E-s(\d+)--([a-f0-9]{64})\.", member.linkname)
            if not member.issym() or not key:
                raise RuntimeError("Expected annex identity")
            rows.append({"path": path, "bytes": int(key[1]), "sha256": key[2]})
    expected = {
        f"sub-{p}/ses-6/eeg/sub-{p}_ses-6_task-innerspeech_eeg.{e}"
        for p in range(12)
        for e in ("eeg", "vhdr", "vmrk")
    }
    if (
        {r["path"] for r in rows} != expected
        or len(rows) != 36
        or sum(r["bytes"] for r in rows) != 45969075
    ):
        raise RuntimeError("Fresh slice metadata changed")
    manifest = {"revision": REVISION, "files": sorted(rows, key=lambda r: r["path"])}
    if (root / "source_manifest.json").exists():
        if read(root / "source_manifest.json") != manifest:
            raise RuntimeError("Manifest differs")
    else:
        dump(root / "source_manifest.json", manifest)
    for row in rows:
        out = root / "raw" / row["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        if not (out.exists() and out.stat().st_size == row["bytes"] and sha(out) == row["sha256"]):
            fetch(
                "https://s3.amazonaws.com/openneuro.org/ds005262/" + row["path"], out, row["bytes"]
            )
        if out.stat().st_size != row["bytes"] or sha(out) != row["sha256"]:
            raise RuntimeError("Source hash mismatch")
        budget(root)
    dump(
        root / "acquired.json",
        {"files": 36, "bytes": 45969075, "seconds": time.monotonic() - started},
    )
    print("Verified all 36 fresh session-6 files", flush=True)


def extract_recording(stem, participant, session):
    import numpy as np
    from scipy.signal import butter, sosfiltfilt

    header = stem.with_suffix(".vhdr").read_text(encoding="utf-8-sig")
    fields = dict(
        line.split("=", 1)
        for line in header.splitlines()
        if "=" in line and not line.startswith(";")
    )
    if any(
        fields.get(k) != v
        for k, v in [
            ("DataOrientation", "MULTIPLEXED"),
            ("BinaryFormat", "IEEE_FLOAT_32"),
            ("NumberOfChannels", "8"),
        ]
    ):
        raise RuntimeError("Unexpected BrainVision format")
    if float(fields.get("SamplingInterval", "nan")) != 4000:
        raise RuntimeError("Unexpected sample rate")
    ch = [line.split(",") for line in re.findall(r"^Ch\d+=(.*)$", header, re.M)]
    if [line[0] for line in ch] != CHANNELS or any(
        line[3].strip() not in ("µV", "μV", "uV") for line in ch
    ):
        raise RuntimeError("Unexpected sensors or units")
    scale = np.array([float(line[2]) * 1e-6 for line in ch])[:, None]
    signal = np.memmap(stem.with_suffix(".eeg"), mode="r", dtype="<f4").reshape(-1, 8)
    sos = butter(4, [1, 30], fs=250, btype="bandpass", output="sos")
    windows, labels, ids = [], [], []
    n = dropped = 0
    for line in stem.with_suffix(".vmrk").read_text(encoding="utf-8-sig").splitlines():
        if not re.match(r"Mk\d+=", line):
            continue
        parts = line.split("=", 1)[1].split(",")
        label = parts[1].lower()
        if label not in CLASSES:
            continue
        start, duration = int(parts[2]) - 1, int(parts[3])
        identity = {"participant": str(participant), "session": str(session), "trial_id": str(n)}
        n += 1
        if duration < 1000 or start < 0 or start + 1000 > len(signal):
            dropped += 1
            continue
        x = signal[start + 500 : start + 1000].T.astype(float) * scale
        if not np.isfinite(x).all():
            raise RuntimeError("Nonfinite signal")
        windows.append(sosfiltfilt(sos, x, axis=-1).astype(np.float32))
        labels.append(label)
        ids.append(identity)
    return (
        windows,
        labels,
        ids,
        {
            "participant": participant,
            "session": session,
            "events": n,
            "incomplete_dropped": dropped,
            "retained": len(windows),
        },
    )


def prepare(root, old, output):
    import numpy as np

    started = time.monotonic()
    old_manifest = {r["path"]: r for r in read(old / "manifest.json")["files"]}
    train, test, ytrain, targets, train_ids, test_ids, counts = [], [], [], [], [], [], []
    for p in range(12):
        for s in (*SESSIONS, TEST_SESSION):
            parent = root if s == TEST_SESSION else old
            stem = parent / "raw" / f"sub-{p}/ses-{s}/eeg/sub-{p}_ses-{s}_task-innerspeech_eeg"
            if s in SESSIONS:
                for extension in ("eeg", "vhdr", "vmrk"):
                    path = stem.with_suffix("." + extension)
                    identity = old_manifest[str(path.relative_to(old / "raw"))]
                    if path.stat().st_size != identity["bytes"] or sha(path) != identity["sha256"]:
                        raise RuntimeError("Previously acquired calibration file changed")
            x, y, ids, count = extract_recording(stem, p, s)
            if not x:
                raise RuntimeError(
                    f"No complete events participant {p} session {s}; no replacement"
                )
            counts.append(count)
            if s == TEST_SESSION:
                test.extend(x)
                test_ids.extend(ids)
                targets.extend({**i, "target": label} for i, label in zip(ids, y))
            else:
                train.extend(x)
                ytrain.extend(y)
                train_ids.extend(ids)
    np.save(output / "train.npy", np.stack(train), allow_pickle=False)
    np.save(output / "test.npy", np.stack(test), allow_pickle=False)
    dump(output / "calibration.json", {"identities": train_ids, "labels": ytrain})
    dump(output / "test_ids.json", test_ids)
    dump(output / "targets.json", {"records": targets})
    dump(
        output / "prepared.json",
        {
            "train_trials": len(train),
            "test_trials": len(test),
            "recordings": counts,
            "seconds": time.monotonic() - started,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    )
    print(
        json.dumps(
            {
                "train_trials": len(train),
                "test_trials": len(test),
                "dropped_incomplete": sum(c["incomplete_dropped"] for c in counts),
            }
        ),
        flush=True,
    )


def features(root, output, code):
    import numpy as np

    f = module(code / "models/timesfm_word_features.py", "timesfm_features")
    cov = module(code / "models/imagined_word_decoder.py", "cov_features")
    started = time.monotonic()
    if sha(root / "checkpoint/model.safetensors") != WEIGHTS_SHA:
        raise RuntimeError("TimesFM checkpoint hash mismatch")
    prepared = root / "prepared"
    for denied in (
        prepared / "targets.json",
        root / "raw/sub-0/ses-6/eeg/sub-0_ses-6_task-innerspeech_eeg.vmrk",
    ):
        try:
            with denied.open("rb"):
                pass
        except PermissionError:
            continue
        raise RuntimeError("Target firewall not active")
    train = f.resample_windows(np.load(prepared / "train.npy", allow_pickle=False))
    test = f.resample_windows(np.load(prepared / "test.npy", allow_pickle=False))
    train_ids = read(prepared / "calibration.json")["identities"]
    test_ids = read(prepared / "test_ids.json")
    rng = np.random.default_rng(20260906)
    noise_train, noise_test = np.empty_like(train), np.empty_like(test)
    for p in range(12):
        it = np.array([i for i, row in enumerate(train_ids) if row["participant"] == str(p)])
        ie = np.array([i for i, row in enumerate(test_ids) if row["participant"] == str(p)])
        scale = train[it].std(axis=(0, 2), keepdims=True)
        noise_train[it] = rng.normal(size=train[it].shape) * scale
        noise_test[ie] = rng.normal(size=test[ie].shape) * scale
    model = f.load_frozen_model(
        next((root / "vendor").glob("timesfm-*")) / "src", root / "checkpoint"
    )
    measurements = []
    for condition, a, b in (("actual", train, test), ("noise", noise_train, noise_test)):
        all_x = np.concatenate([a, b])
        for mode in MODES:
            t = time.monotonic()
            if mode == "covariance":
                values = cov.covariance_log_features(all_x).astype(np.float32)
            elif mode == "temporal":
                values = all_x.reshape(len(all_x), -1) * 1e6
            else:
                parts = []
                for i in range(0, len(all_x), 8):
                    parts.append(f.extract_features(model, all_x[i : i + 8], mode=mode))
                    if i % 128 == 0:
                        print(f"{condition} {mode}: {i}/{len(all_x)} windows", flush=True)
                values = np.concatenate(parts)
            np.save(output / f"{condition}-{mode}.npy", values, allow_pickle=False)
            measurements.append(
                {
                    "condition": condition,
                    "mode": mode,
                    "shape": list(values.shape),
                    "seconds": time.monotonic() - t,
                }
            )
            print(json.dumps(measurements[-1]), flush=True)
    dump(
        output / "measurements.json",
        {
            "modes": measurements,
            "seconds": time.monotonic() - started,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "torch_threads": 1,
            "weights_sha256": WEIGHTS_SHA,
            "target_and_raw_read_denied": True,
        },
    )


def metadata_features(ids):
    import numpy as np

    positions = np.array([int(row["trial_id"]) for row in ids])
    scaled = positions / 24
    return np.column_stack([scaled, scaled**2, np.eye(26)[np.minimum(positions, 25)]])


def predict(root, output, code):
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    f = module(code / "models/timesfm_word_features.py", "timesfm_features")
    start = time.monotonic()
    calibration = read(root / "prepared/calibration.json")
    ids, labels = calibration["identities"], np.array(calibration["labels"])
    test_ids = read(root / "prepared/test_ids.json")
    if set(int(i["session"]) for i in ids) != set(SESSIONS) or any(
        i["session"] != "6" for i in test_ids
    ):
        raise RuntimeError("Unexpected recording split")
    yshuffle = labels.copy()
    rng = np.random.default_rng(20260905)
    for p in range(12):
        for s in SESSIONS:
            ix = np.array(
                [
                    i
                    for i, r in enumerate(ids)
                    if r["participant"] == str(p) and r["session"] == str(s)
                ]
            )
            yshuffle[ix] = labels[rng.permutation(ix)]
    rows = [{**i, "probabilities": {}} for i in test_ids]
    fits = 0
    for p in range(12):
        it = np.array([i for i, r in enumerate(ids) if r["participant"] == str(p)])
        ie = np.array([i for i, r in enumerate(test_ids) if r["participant"] == str(p)])
        for mode in MODES:
            x = np.load(root / f"features/actual-{mode}.npy", mmap_mode="r")
            xn = np.load(root / f"features/noise-{mode}.npy", mmap_mode="r")
            for arm, source, y in (
                (mode, x, labels),
                (mode + "_shuffled", x, yshuffle),
                (mode + "_noise", xn, labels),
            ):
                probs, classes = f.fit_readout(source[it], y[it], source[len(ids) + ie])
                if classes != CLASSES:
                    raise RuntimeError("Training vocabulary incomplete")
                for index, prob in zip(ie, probs):
                    rows[index]["probabilities"][arm] = prob.tolist()
                fits += 1
        prior = np.array([np.sum(labels[it] == c) + 1 for c in CLASSES], dtype=float)
        prior /= prior.sum()
        meta = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000, tol=1e-8))
        meta.fit(metadata_features([ids[i] for i in it]), labels[it])
        meta_prob = meta.predict_proba(metadata_features([test_ids[i] for i in ie]))
        if meta.classes_.tolist() != CLASSES:
            raise RuntimeError("Metadata classes differ")
        for index, prob in zip(ie, meta_prob):
            rows[index]["probabilities"].update(prior=prior.tolist(), metadata=prob.tolist())
        print(f"Completed participant {p}: all 17 arms", flush=True)
    for row in rows:
        row["probabilities"] = {ALIASES.get(k, k): v for k, v in row["probabilities"].items()}
    envelope = {
        "class_labels": CLASSES,
        "primary_arm": "joint_hidden",
        "control_arms": ["prior", "metadata", "shuffled", "noise"],
        "diagnostic_arms": [
            a
            for a in ARMS
            if a
            not in (
                "joint_hidden",
                "joint_hidden_shuffled",
                "joint_hidden_noise",
                "prior",
                "metadata",
            )
        ],
        "expected_participants": [str(p) for p in range(12)],
        "heldout_session": "6",
        "records": rows,
    }
    dump(output / "predictions.json", envelope)
    dump(
        output / "measurements.json",
        {
            "seconds": time.monotonic() - start,
            "numerical_fits": fits + 12,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    )


def score(root, output, code, digest):
    import numpy as np

    start = time.monotonic()
    report = module(code / "evaluation/imagined_word_report.py", "word_report")
    result = report.score_frozen_files(
        root / "predicted/predictions.json",
        root / "prepared/targets.json",
        expected_prediction_sha256=digest,
    )
    # These comparisons are computed within this sole score transaction, never
    # by reopening targets or fitting after outcomes are visible.
    rng = np.random.default_rng(20260905)
    people = result["participants"]
    indices = rng.integers(0, len(people), size=(4000, len(people)))
    signs = np.array(list(itertools.product([-1, 1], repeat=len(people))))
    comparisons = []
    for mode in MODES[:3]:
        for control in (
            "covariance",
            "temporal",
            "prior",
            "metadata",
            mode + "_shuffled",
            mode + "_noise",
        ):
            control = ALIASES.get(control, control)
            gains = np.array(
                [
                    p["arms"][control]["macro_log_loss"] - p["arms"][mode]["macro_log_loss"]
                    for p in people
                ]
            )
            observed = gains.mean()
            pvalue = float(np.mean((signs @ gains / len(gains)) >= observed - 1e-12))
            comparisons.append(
                {
                    "mode": mode,
                    "control": control,
                    "mean_log_loss_gain": float(observed),
                    "ci95": np.quantile(gains[indices].mean(axis=1), [0.025, 0.975]).tolist(),
                    "positive_people": int((gains > 0).sum()),
                    "one_sided_sign_flip_p": pvalue,
                }
            )
    running = 0.0
    for rank, index in enumerate(
        sorted(range(len(comparisons)), key=lambda i: comparisons[i]["one_sided_sign_flip_p"])
    ):
        running = max(
            running,
            min(1.0, comparisons[index]["one_sided_sign_flip_p"] * (len(comparisons) - rank)),
        )
        comparisons[index]["holm_p_18"] = running
    result["timesfm_comparisons"] = comparisons
    result["sign_flip_assumption"] = (
        "Conditional on symmetric/exchangeable participant gain signs; this is not an "
        "assumption-free mean-improvement test or independent confirmation."
    )
    result["score_seconds"] = time.monotonic() - start
    result["claim_scope"] = (
        "Exploratory prompted-word transfer to a new recording of calibrated people; no neural attribution or thought-to-text claim."
    )
    dump(output / "result.json", result)
    public = {k: v for k, v in result.items() if k != "prediction_rows"}
    dump(output / "aggregate.json", public)
    print(
        json.dumps(
            {
                a: {m: v["participant_mean"] for m, v in row.items()}
                for a, row in result["summary_by_arm"].items()
            }
        ),
        flush=True,
    )


def worker(root, old, role, repo, digest=None):
    out = (
        root
        / {
            "prepare": "prepared",
            "features": "features",
            "predict": "predicted",
            "score": "scored",
        }[role]
    )
    out.mkdir(exist_ok=False)
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
    reads = [
        py.parent.parent,
        site,
        "/System",
        "/usr/lib",
        "/usr/share",
        "/Library/Apple",
        "/dev/null",
        "/dev/urandom",
        "/dev/random",
        code,
    ]
    files = []
    if role == "prepare":
        reads.append(root / "raw")
        files.append(old / "manifest.json")
        for p in range(12):
            for s in SESSIONS:
                for e in ("eeg", "vhdr", "vmrk"):
                    files.append(
                        old
                        / "raw"
                        / f"sub-{p}/ses-{s}/eeg/sub-{p}_ses-{s}_task-innerspeech_eeg.{e}"
                    )
    elif role in ("features", "predict"):
        files += [
            root / "prepared" / n
            for n in ("train.npy", "test.npy", "calibration.json", "test_ids.json")
        ]
        reads += (
            [root / "vendor", root / "checkpoint"] if role == "features" else [root / "features"]
        )
    else:
        files += [root / "predicted/predictions.json", root / "prepared/targets.json"]
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
        "--site",
        str(site),
        "--root",
        str(root),
        "--old",
        str(old),
        "--output",
        str(out),
        "--internal",
        role,
    ]
    if digest:
        args += ["--digest", digest]
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
    with (out / "worker.log").open("w") as log:
        child = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=out)
        try:
            limit = {"features": 3300, "predict": 300, "prepare": 300, "score": 120}[role]
            while child.poll() is None:
                ps = subprocess.run(
                    ["/bin/ps", "-o", "rss=", "-p", str(child.pid)], capture_output=True, text=True
                )
                peak = max(peak, int(ps.stdout.strip() or "0") * 1024)
                if peak > 4 * 2**30 or time.monotonic() - start > limit:
                    dump(out / "blocked.json", {"reason": "RSS or runtime cap", "peak_rss": peak})
                    raise RuntimeError("Worker resource limit")
                budget(root)
                time.sleep(1)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
    dump(
        out / "process.json",
        {
            "returncode": child.returncode,
            "seconds": time.monotonic() - start,
            "sampled_peak_rss_bytes": peak,
            "network_denied": True,
            "os_file_whitelist": True,
        },
    )
    if child.returncode:
        raise RuntimeError(f"Worker failed: {out / 'worker.log'}")
    print((out / "process.json").read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("acquire", "prepare", "features", "predict", "score"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--old", type=Path, default=Path(".codex_work/areeg-local-words-r0"))
    parser.add_argument("--site")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--internal", action="store_true")
    parser.add_argument("--digest")
    args = parser.parse_args()
    if args.site:
        sys.path.insert(0, args.site)
    root, old = args.root.resolve(), args.old.resolve()
    repo = Path(__file__).resolve().parents[3]
    if args.role == "acquire":
        acquire(root)
    elif args.internal:
        code = repo / "src/neurodecodekit"
        if args.role == "prepare":
            prepare(root, old, args.output)
        elif args.role == "features":
            features(root, args.output, code)
        elif args.role == "predict":
            predict(root, args.output, code)
        else:
            score(root, args.output, code, args.digest)
    else:
        worker(root, old, args.role, repo, args.digest)


if __name__ == "__main__":
    main()
