"""Bounded ArEEG acquisition, separated prediction/scoring and local replay.

Run directly with the project's optional-neuro Python. No numerical imports at
module import; no download or fitting without an explicit CLI action.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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

REVISION = "4ba1bb516d6cc98917143b0dfca23947935c7b15"
CLASSES = ["down", "left", "right", "select", "up"]
ARMS = ["eeg", "prior", "metadata", "shuffled", "noise", "cue"]
LIMIT = 512 * 2**20


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def dump(path, value, exclusive=False):
    with Path(path).open("x" if exclusive else "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def read(path):
    return json.loads(Path(path).read_text())


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_budget(root):
    # Only this invocation's new directory is inventoried.
    used = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    if used > LIMIT or shutil.disk_usage(root).free < 20 * 2**30:
        raise RuntimeError("New invocation disk budget or free-space floor exceeded")
    return used


def curl(url, path, size_cap):
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
            str(size_cap),
            "--output",
            str(path),
            url,
        ],
        check=True,
    )
    if path.stat().st_size > size_cap:
        raise RuntimeError("Source exceeded byte cap")


def manifest(root):
    root.mkdir(parents=False, exist_ok=False)
    archive = root / "metadata.tar.gz"
    curl(
        f"https://codeload.github.com/OpenNeuroDatasets/ds005262/tar.gz/{REVISION}",
        archive,
        2 * 2**20,
    )
    rows = []
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            path = member.name.split("/", 1)[-1]
            match = re.fullmatch(
                r"sub-(\d+)/ses-(\d+)/eeg/sub-\1_ses-\2_task-innerspeech_eeg\.(eeg|vhdr|vmrk)", path
            )
            if not match or int(match[1]) >= 12 or int(match[2]) >= 6:
                continue
            if not member.issym():
                raise RuntimeError("Expected release metadata annex link")
            key = re.search(r"SHA256E-s(\d+)--([a-f0-9]{64})\.", member.linkname)
            if not key:
                raise RuntimeError("Missing release content hash")
            rows.append(
                {
                    "path": path,
                    "participant": int(match[1]),
                    "session": int(match[2]),
                    "bytes": int(key[1]),
                    "sha256": key[2],
                    "url": "https://s3.amazonaws.com/openneuro.org/ds005262/" + path,
                }
            )
    rows.sort(key=lambda x: (x["participant"], x["session"], x["path"]))
    total = sum(x["bytes"] for x in rows)
    expected_paths = {
        f"sub-{p}/ses-{s}/eeg/sub-{p}_ses-{s}_task-innerspeech_eeg.{ext}"
        for p in range(12)
        for s in range(6)
        for ext in ("eeg", "vhdr", "vmrk")
    }
    if len(rows) != 216 or {row["path"] for row in rows} != expected_paths or total > 320 * 2**20:
        raise RuntimeError(f"Unexpected selected slice: {len(rows)} files, {total} bytes")
    result = {
        "revision": REVISION,
        "license": "CC0",
        "files": rows,
        "total_bytes": total,
        "metadata_archive_sha256": sha(archive),
    }
    dump(root / "manifest.json", result, exclusive=True)
    print(json.dumps({"files": len(rows), "bytes": total, "revision": REVISION}))


def acquire(root):
    if (root / "acquired.json").exists():
        raise RuntimeError("Acquisition already completed")
    started = time.monotonic()
    rows = read(root / "manifest.json")["files"]
    fetched = 0
    for i, row in enumerate(rows):
        destination = root / "raw" / row["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Transport recovery is permitted before prediction/scoring. Existing
        # exact complete files are verified, never downloaded again.
        if not (
            destination.exists()
            and destination.stat().st_size == row["bytes"]
            and sha(destination) == row["sha256"]
        ):
            curl(row["url"], destination, row["bytes"])
            fetched += row["bytes"]
        if destination.stat().st_size != row["bytes"] or sha(destination) != row["sha256"]:
            raise RuntimeError("Payload differs from frozen release")
        check_budget(root)
        if (i + 1) % 18 == 0:
            print(f"Verified {i + 1}/{len(rows)} selected files", flush=True)
    dump(
        root / "acquired.json",
        {
            "verified_bytes": sum(x["bytes"] for x in rows),
            "fetched_bytes_this_invocation": fetched,
            "seconds": time.monotonic() - started,
        },
    )


def env():
    result = {
        "PATH": "/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "MNE_DONTWRITE_HOME": "true",
    }
    for name in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        result[name] = "1"
    return result


def sandbox(repo, role, inputs, output, args):
    python = (repo / ".venv/bin/python").resolve()
    site = (repo / ".venv/lib/python3.13/site-packages").resolve()
    script = Path(__file__).resolve()

    def q(p):
        return json.dumps(str(Path(p).resolve()))

    profile = [
        "(version 1)",
        "(deny default)",
        '(import "dyld-support.sb")',
        "(allow sysctl-read)",
        "(allow process-info* (target self))",
        f"(allow process-exec (literal {q(python)}))",
    ]
    for path in [
        python.parent.parent,
        site,
        "/System",
        "/usr/lib",
        "/usr/share",
        "/Library/Apple",
        "/dev/null",
        "/dev/urandom",
        "/dev/random",
    ]:
        profile.append(f"(allow file-read* file-map-executable (subpath {q(path)}))")
    for path in [script, *inputs]:
        profile += [
            f"(allow file-read* (literal {q(path)}))",
            f"(allow file-read-metadata (path-ancestors {q(path)}))",
        ]
    profile += [
        f"(allow file-read* file-write* (subpath {q(output)}))",
        f"(allow file-read-metadata (path-ancestors {q(output)}))",
    ]
    return [
        "/usr/bin/sandbox-exec",
        "-p",
        "\n".join(profile),
        str(python),
        "-I",
        "-S",
        str(script),
        "--site",
        str(site),
        role,
        *map(str, args),
    ]


def broker(root, output):
    import numpy as np
    from scipy.signal import butter, sosfiltfilt

    # Minimal verified BrainVision reader: the frozen source is float32,
    # multiplexed, 8ch, 250Hz. Annotations are read only in this broker.
    xtrain, xcue, xtest, qtest, ytrain, targets, train_ids, test_ids = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    recording_counts = []
    channels_expected = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "OZ", "PO8"]
    sos = butter(4, [1, 30], btype="bandpass", fs=250, output="sos")
    for p in range(12):
        for s in range(6):
            stem = root / "raw" / f"sub-{p}/ses-{s}/eeg/sub-{p}_ses-{s}_task-innerspeech_eeg"
            header = stem.with_suffix(".vhdr").read_text(encoding="utf-8-sig")
            header_fields = dict(
                line.split("=", 1)
                for line in header.splitlines()
                if "=" in line and not line.startswith(";")
            )
            for key, value in (
                ("DataOrientation", "MULTIPLEXED"),
                ("BinaryFormat", "IEEE_FLOAT_32"),
                ("NumberOfChannels", "8"),
            ):
                if header_fields.get(key) != value:
                    raise RuntimeError("Unexpected source geometry")
            if float(header_fields.get("SamplingInterval", "nan")) != 4000.0:
                raise RuntimeError("Unexpected source sample rate")
            channel_lines = re.findall(r"^Ch\d+=(.*)$", header, re.M)
            channels = [line.split(",")[0] for line in channel_lines]
            if channels != channels_expected:
                raise RuntimeError("Unexpected electrode ordering")
            resolutions = np.array([float(line.split(",")[2]) for line in channel_lines]) * 1e-6
            if any(line.strip().split(",")[3] not in ("µV", "μV", "uV") for line in channel_lines):
                raise RuntimeError("Unexpected source units")
            raw = np.memmap(stem.with_suffix(".eeg"), dtype="<f4", mode="r").reshape(-1, 8)
            markers = stem.with_suffix(".vmrk").read_text(encoding="utf-8-sig")
            n, dropped = 0, 0
            for line in markers.splitlines():
                if not re.match(r"Mk\d+=", line):
                    continue
                parts = line.split("=", 1)[1].split(",")
                label = parts[1].lower()
                if label not in CLASSES:
                    continue
                start, duration = int(parts[2]) - 1, int(parts[3])
                identity = {"participant": str(p), "session": str(s), "trial_id": str(n)}
                n += 1
                if duration < 1000 or start < 0 or start + 1000 > len(raw):
                    dropped += 1
                    continue
                late = raw[start + 500 : start + 1000].T.astype(float) * resolutions[:, None]
                early = raw[start : start + 500].T.astype(float) * resolutions[:, None]
                if not np.isfinite(late).all() or not np.isfinite(early).all():
                    raise RuntimeError("Nonfinite event")
                late = sosfiltfilt(sos, late, axis=-1).astype("float32")
                early = sosfiltfilt(sos, early, axis=-1).astype("float32")
                if s < 5:
                    xtrain.append(late)
                    xcue.append(early)
                    ytrain.append(label)
                    train_ids.append(identity)
                else:
                    xtest.append(late)
                    qtest.append(early)
                    test_ids.append(identity)
                    targets.append({**identity, "target": label})
            if n - dropped < 2 and not (s == 5 and n == 0):
                raise RuntimeError(
                    f"Insufficient complete word events: participant={p}, session={s}, events={n}, incomplete={dropped}"
                )
            recording_counts.append(
                {
                    "participant": p,
                    "session": s,
                    "word_events": n,
                    "incomplete_dropped": dropped,
                    "retained": n - dropped,
                }
            )
            del raw
    for name, array in (
        ("train", xtrain),
        ("train_cue", xcue),
        ("test", xtest),
        ("test_cue", qtest),
    ):
        np.save(output / f"{name}.npy", np.stack(array), allow_pickle=False)
    dump(output / "calibration.json", {"labels": ytrain, "identities": train_ids})
    dump(output / "test_ids.json", test_ids)
    dump(output / "targets.json", {"records": targets}, exclusive=True)
    dump(
        output / "prepared.json",
        {
            "train_trials": len(xtrain),
            "test_trials": len(xtest),
            "participants": 12,
            "channels": channels_expected,
            "samples_per_window": 500,
            "recording_counts": recording_counts,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    )


def derange_by_session(x, ids, seed):
    import numpy as np

    rng = np.random.default_rng(seed)
    out = np.empty_like(x)
    for key in sorted({(r["participant"], r["session"]) for r in ids}):
        idx = np.array([i for i, r in enumerate(ids) if (r["participant"], r["session"]) == key])
        order = np.arange(len(idx))
        for i in range(len(order) - 1, 0, -1):
            j = int(rng.integers(0, i))
            order[i], order[j] = order[j], order[i]
        if (order == np.arange(len(idx))).any():
            raise RuntimeError("Derangement fixed point")
        out[idx] = x[idx[order]]
    return out


def predictor(prepared, output, model_path):
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from threadpoolctl import threadpool_limits

    threadpool_limits(limits=1)
    model_module = load_module(model_path, "local_word_model")
    # Active denial proof before fitting. The raw/target namespace is excluded
    # from the OS profile, not merely omitted from function arguments.
    denied = []
    for path in (
        prepared / "targets.json",
        prepared.parent / "raw/sub-0/ses-5/eeg/sub-0_ses-5_task-innerspeech_eeg.vmrk",
    ):
        try:
            with path.open("rb") as f:
                f.read(1)
        except PermissionError:
            denied.append(str(path.name))
        else:
            raise RuntimeError("Target firewall failed")
    train = np.load(prepared / "train.npy", allow_pickle=False)
    cue = np.load(prepared / "train_cue.npy", allow_pickle=False)
    test = np.load(prepared / "test.npy", allow_pickle=False)
    test_cue = np.load(prepared / "test_cue.npy", allow_pickle=False)
    calibration = read(prepared / "calibration.json")
    ids = calibration["identities"]
    test_ids = read(prepared / "test_ids.json")
    labels = np.array(calibration["labels"])
    shuffled_train = derange_by_session(train, ids, 20260905)
    shuffled_test = derange_by_session(test, test_ids, 20260906)
    records = []
    started = time.monotonic()
    for p in range(12):
        it = np.array([i for i, r in enumerate(ids) if r["participant"] == str(p)])
        ie = np.array([i for i, r in enumerate(test_ids) if r["participant"] == str(p)])
        if len(ie) == 0:
            continue
        y = labels[it]
        if sorted(set(y)) != CLASSES:
            raise RuntimeError("Calibration vocabulary incomplete")
        scale = np.std(train[it], axis=(0, 2), keepdims=True)
        rng = np.random.default_rng(1200 + p)
        noise_train = rng.normal(size=train[it].shape) * scale
        noise_test = rng.normal(size=test[ie].shape) * scale
        predictions = {}
        for arm, a, b in (
            ("eeg", train[it], test[ie]),
            ("cue", cue[it], test_cue[ie]),
            ("shuffled", shuffled_train[it], shuffled_test[ie]),
            ("noise", noise_train, noise_test),
        ):
            model = model_module.ImaginedWordDecoder(shrinkage=0.1, C=1.0).fit(a, y)
            if list(model.classes_) != CLASSES:
                raise RuntimeError("Model vocabulary order drift")
            predictions[arm] = model.predict_proba(b)
            if arm == "eeg":
                model.save(output / f"participant-{p}.npz")

        def positions(selected):
            position = np.array([int(r["trial_id"]) for r in selected])
            return np.column_stack(
                [position / 24, (position / 24) ** 2, np.eye(26)[np.minimum(position, 25)]]
            )

        metadata = LogisticRegression(C=1.0, solver="lbfgs", max_iter=500).fit(
            positions([ids[i] for i in it]), y
        )
        predictions["metadata"] = metadata.predict_proba(positions([test_ids[i] for i in ie]))
        prior = np.array([(y == c).sum() + 1 for c in CLASSES], dtype=float)
        prior /= prior.sum()
        predictions["prior"] = np.tile(prior, (len(ie), 1))
        for j, i in enumerate(ie):
            records.append(
                {
                    **test_ids[i],
                    "probabilities": {arm: predictions[arm][j].tolist() for arm in ARMS},
                }
            )
        print(f"Predictions frozen in memory for participant {p + 1}/12", flush=True)
    dump(
        output / "predictions.json",
        {
            "class_labels": CLASSES,
            "primary_arm": "eeg",
            "control_arms": ["prior", "metadata", "shuffled", "noise"],
            "diagnostic_arms": ["cue"],
            "expected_participants": sorted({r["participant"] for r in test_ids}),
            "heldout_session": "5",
            "records": records,
        },
        exclusive=True,
    )
    dump(
        output / "prediction_measurements.json",
        {
            "seconds": time.monotonic() - started,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "fit_count": 5 * len({r["participant"] for r in test_ids}),
            "fitted_calibration_trials": sum(
                r["participant"] in {t["participant"] for t in test_ids} for r in ids
            ),
            "prediction_rows": len(records),
            "target_access_denials": denied,
            "classes": CLASSES,
            "model_feature_count": 36,
        },
    )


def run_child(repo, root, role):
    prepared = root / "prepared"
    if role == "broker":
        output = prepared
        inputs = [root / "raw" / row["path"] for row in read(root / "manifest.json")["files"]]
        args = ["--root", root, "--output", output]
    else:
        output = root / "predicted"
        model = repo / "src/neurodecodekit/models/imagined_word_decoder.py"
        inputs = [
            prepared / name
            for name in (
                "train.npy",
                "train_cue.npy",
                "test.npy",
                "test_cue.npy",
                "calibration.json",
                "test_ids.json",
            )
        ] + [model]
        args = ["--root", prepared, "--output", output, "--model", model]
    output.mkdir(exist_ok=True)
    if any(output.iterdir()):
        raise RuntimeError("Worker output already exists; completed work cannot be repeated")
    started = time.monotonic()
    peak_rss = 0
    with (root / f"{role}.log").open("w") as log:
        process = subprocess.Popen(
            sandbox(repo, role, inputs, output, args),
            env=env(),
            cwd=output,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        while process.poll() is None:
            sampled = subprocess.run(
                ["/bin/ps", "-o", "rss=", "-p", str(process.pid)],
                capture_output=True,
                text=True,
                check=False,
            )
            rss = int(sampled.stdout.strip() or "0") * 1024
            peak_rss = max(peak_rss, rss)
            if rss > 2**30 or time.monotonic() - started > 600:
                process.kill()
                process.wait()
                raise RuntimeError("Numerical resource cap exceeded")
            time.sleep(0.5)
        if process.returncode:
            raise RuntimeError(f"{role} exited {process.returncode}; see its local log")
    dump(
        root / f"{role}_execution.json",
        {
            "seconds": time.monotonic() - started,
            "new_disk_bytes": check_budget(root),
            "os_sandbox": True,
            "sampled_peak_rss_bytes": peak_rss,
        },
    )
    result = read(
        output / ("prepared.json" if role == "broker" else "prediction_measurements.json")
    )
    print(json.dumps({k: v for k, v in result.items() if k != "recording_counts"}))


def freeze(repo, root):
    prediction = root / "predicted/predictions.json"
    record = {
        "experiment": "ArEEG-local-words-r0",
        "revision": REVISION,
        "prediction_sha256": sha(prediction),
        "prediction_bytes": prediction.stat().st_size,
        "manifest_sha256": sha(root / "manifest.json"),
        "model_sha256": {
            p: sha(root / f"predicted/participant-{p}.npz")
            for p in read(prediction)["expected_participants"]
        },
        "measurements": read(root / "predicted/prediction_measurements.json"),
        "claim": "Calibrated prompted word classification across held-out recordings.",
    }
    path = repo / "registries/areeg_local_words_prediction_freeze.v0.json"
    dump(path, record, exclusive=True)
    print(json.dumps({"prediction_sha256": record["prediction_sha256"], "freeze": str(path)}))


def score_worker(root, output, report_path, digest):
    report = load_module(report_path, "local_word_report")
    result = report.score_frozen_files(
        root / "predicted/predictions.json",
        root / "prepared/targets.json",
        expected_prediction_sha256=digest,
    )
    dump(output / "result.json", result, exclusive=True)
    report.write_html_report(result, output / "report.html")
    dump(output / "aggregate.json", {k: v for k, v in result.items() if k != "prediction_rows"})


def score(repo, root, commit):
    relative = "registries/areeg_local_words_prediction_freeze.v0.json"
    committed = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    record = json.loads(committed)
    digest = record["prediction_sha256"]
    if sha(root / "predicted/predictions.json") != digest:
        raise RuntimeError("Predictions differ from committed freeze")
    output = root / "scored"
    output.mkdir(exist_ok=False)
    dump(
        root / "score_started.json",
        {"freeze_commit": commit, "prediction_sha256": digest},
        exclusive=True,
    )
    module = repo / "src/neurodecodekit/evaluation/imagined_word_report.py"
    inputs = [module, root / "predicted/predictions.json", root / "prepared/targets.json"]
    args = ["--root", root, "--output", output, "--model", module, "--digest", digest]
    started = time.monotonic()
    with (root / "score.log").open("w") as log:
        subprocess.run(
            sandbox(repo, "scorer", inputs, output, args),
            cwd=output,
            env=env(),
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=60,
        )
    dump(
        root / "scoring_execution.json",
        {
            "seconds": time.monotonic() - started,
            "new_disk_bytes": check_budget(root),
            "score_operations": 1,
        },
    )
    result = read(output / "aggregate.json")
    print(
        json.dumps(
            {
                "n_participants": result["n_participants"],
                "n_trials": result["n_trials"],
                "summary_by_arm": result["summary_by_arm"],
                "comparisons": result["comparisons"],
            }
        )
    )


def replay(root, participant, trial):
    """Display a frozen, target-free prediction; never retrain or rescore."""
    rows = read(root / "predicted/predictions.json")["records"]
    row = next(r for r in rows if r["participant"] == participant and r["trial_id"] == trial)
    p = row["probabilities"]["eeg"]
    i = max(range(len(p)), key=lambda k: p[k])
    print(
        json.dumps(
            {
                "mode": "frozen prediction replay",
                "word": CLASSES[i],
                "model_probability": p[i],
                "probabilities": dict(zip(CLASSES, p)),
                "note": "A prompted five-word recording, not unrestricted thought decoding.",
            },
            indent=2,
        )
    )


def infer(repo, model_path, window_path, index):
    """Run a saved model on preprocessed EEG, without labels or scoring."""
    import numpy as np

    module = load_module(
        repo / "src/neurodecodekit/models/imagined_word_decoder.py", "local_word_model"
    )
    model = module.ImaginedWordDecoder.load(model_path)
    windows = np.load(window_path, mmap_mode="r", allow_pickle=False)
    if windows.ndim == 2:
        if index != 0:
            raise ValueError("A single window only has index 0")
        window = windows[None, ...]
    elif windows.ndim == 3 and 0 <= index < len(windows):
        window = windows[index : index + 1]
    else:
        raise ValueError("Expected preprocessed [8,500] or [trials,8,500] EEG and a valid index")
    started = time.monotonic()
    probabilities = model.predict_proba(window)[0]
    i = int(np.argmax(probabilities))
    print(
        json.dumps(
            {
                "mode": "saved-model inference, no scoring",
                "word": str(model.classes_[i]),
                "probabilities": dict(zip(model.classes_.tolist(), probabilities.tolist())),
                "inference_seconds": time.monotonic() - started,
                "note": "Experimental probabilities; useful word decoding has not been established.",
            },
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site")
    parser.add_argument(
        "action",
        choices=[
            "manifest",
            "acquire",
            "prepare",
            "predict",
            "freeze",
            "score",
            "replay",
            "infer",
            "broker",
            "predictor",
            "scorer",
        ],
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--freeze-commit")
    parser.add_argument("--digest")
    parser.add_argument("--participant", default="0")
    parser.add_argument("--trial", default="0")
    parser.add_argument(
        "--window", type=Path, help="Already filtered, two-second EEG windows in volts; no labels"
    )
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()
    args.root = args.root.resolve()
    args.repo = args.repo.resolve()
    if args.site:
        sys.path.insert(0, args.site)
    if args.action == "manifest":
        manifest(args.root)
    elif args.action == "acquire":
        acquire(args.root)
    elif args.action == "prepare":
        run_child(args.repo, args.root, "broker")
    elif args.action == "predict":
        run_child(args.repo, args.root, "predictor")
    elif args.action == "freeze":
        freeze(args.repo, args.root)
    elif args.action == "score":
        if not args.freeze_commit:
            parser.error("score requires the prior --freeze-commit")
        score(args.repo, args.root, args.freeze_commit)
    elif args.action == "replay":
        replay(args.root, args.participant, args.trial)
    elif args.action == "infer":
        if not args.model or not args.window:
            parser.error("infer requires --model and --window")
        infer(args.repo, args.model, args.window, args.index)
    elif args.action == "broker":
        broker(args.root, args.output)
    elif args.action == "predictor":
        predictor(args.root, args.output, args.model)
    elif args.action == "scorer":
        score_worker(args.root, args.output, args.model, args.digest)


if __name__ == "__main__":
    main()
