"""D3 early-window diagnostic; late comparison reads public aggregates only."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[3]
BASE = REPO / ".codex_work/timesfm-words-r1"
SOURCE = REPO / ".codex_work/areeg-local-words-r0"
LATE = REPO / "registries/word_recording_balanced_result.v0.json"
spec = importlib.util.spec_from_file_location(
    "timing_balanced", Path(__file__).with_name("word_recording_balanced.py")
)
balanced = importlib.util.module_from_spec(spec)
spec.loader.exec_module(balanced)
d = balanced.engine
original_dump = d.dump
MANIFEST_SHA = "f202e0a47242e9faf4f578a4e5343cc060370e36119cb72cfe01cd03b77879eb"
SPLIT_SHA = "25bd162cab7c7e39e5c31e68e07c746681e9e104077ccbdfb215737a511ebd1f"
CHANNELS = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "OZ", "PO8"]


def word_events(marker_text, samples):
    """Original ordinal and full-4s eligibility; return zero-based early bounds."""
    rows, ordinal, dropped = [], 0, 0
    for line in marker_text.splitlines():
        if not re.match(r"Mk\d+=", line):
            continue
        parts = line.split("=", 1)[1].split(",")
        label = parts[1].lower()
        if label not in d.CLASSES:
            continue
        start, duration = int(parts[2]) - 1, int(parts[3])
        identity = str(ordinal)
        ordinal += 1
        if duration < 1000 or start < 0 or start + 1000 > samples:
            dropped += 1
            continue
        rows.append((identity, label, start, start + 500))
    return rows, dropped


def filtered_early(raw, start, scale, sos):
    import numpy as np
    from scipy.signal import sosfiltfilt

    x = raw[start : start + 500].T.astype(float) * scale
    if x.shape != (8, 500) or not np.isfinite(x).all():
        raise ValueError("Nonfinite/incomplete early window; matched comparison stops")
    return sosfiltfilt(sos, x, axis=-1).astype(np.float32)


def prepare(root, out):
    import numpy as np
    from scipy.signal import butter

    if d.sha(SOURCE / "manifest.json") != MANIFEST_SHA:
        raise ValueError("Original source manifest changed")
    manifest = d.read(SOURCE / "manifest.json")
    selected = [
        r
        for r in manifest["files"]
        if int(r["participant"]) in range(12) and int(r["session"]) in d.SESSIONS
    ]
    if len(selected) != 144:
        raise ValueError("Expected144 selected raw files")
    for row in selected:
        p = SOURCE / "raw" / row["path"]
        if p.stat().st_size != row["bytes"] or d.sha(p) != row["sha256"]:
            raise ValueError("Selected source identity differs")
    if d.sha(BASE / "prepared/calibration.json") != d.INPUT_SHA["calibration.json"]:
        raise ValueError("Canonical calibration changed")
    calibration = d.read(BASE / "prepared/calibration.json")
    windows, ids, labels, dropped = [], [], [], 0
    sos = butter(4, [1, 30], fs=250, btype="bandpass", output="sos")
    for person in range(12):
        for session in d.SESSIONS:
            stem = (
                SOURCE
                / "raw"
                / f"sub-{person}/ses-{session}/eeg/sub-{person}_ses-{session}_task-innerspeech_eeg"
            )
            header = stem.with_suffix(".vhdr").read_text(encoding="utf-8-sig")
            fields = dict(
                line.split("=", 1)
                for line in header.splitlines()
                if "=" in line and not line.startswith(";")
            )
            for key, expected in (
                ("DataOrientation", "MULTIPLEXED"),
                ("BinaryFormat", "IEEE_FLOAT_32"),
                ("NumberOfChannels", "8"),
            ):
                if fields.get(key) != expected:
                    raise ValueError("BrainVision format changed")
            channels = [line.split(",") for line in re.findall(r"^Ch\d+=(.*)$", header, re.M)]
            if (
                float(fields["SamplingInterval"]) != 4000
                or [c[0] for c in channels] != CHANNELS
                or any(c[3].strip() not in ("µV", "μV", "uV") for c in channels)
            ):
                raise ValueError("Sampling, channel order or units differ")
            scale = np.array([float(c[2]) * 1e-6 for c in channels])[:, None]
            raw = np.memmap(stem.with_suffix(".eeg"), dtype="<f4", mode="r").reshape(-1, 8)
            events, missing = word_events(
                stem.with_suffix(".vmrk").read_text(encoding="utf-8-sig"), len(raw)
            )
            dropped += missing
            for ordinal, label, start, stop in events:
                windows.append(filtered_early(raw, start, scale, sos))
                ids.append(
                    {"participant": str(person), "session": str(session), "trial_id": ordinal}
                )
                labels.append(label)
    if ids != calibration["identities"] or labels != calibration["labels"] or len(ids) != 1198:
        raise ValueError("Early identities/labels do not exactly match late development trials")
    np.save(out / "train.npy", np.stack(windows), allow_pickle=False)
    d.dump(
        out / "source_receipt.json",
        {
            "selected_files": len(selected),
            "verified_source_bytes": sum(r["bytes"] for r in selected),
            "trials": len(ids),
            "same_exclusions": dropped,
            "calibration_sha256": d.INPUT_SHA["calibration.json"],
            "early_array_sha256": d.sha(out / "train.npy"),
            "samples": 500,
            "window_seconds": [0, 2],
            "position_index_adjustment": -1,
        },
    )
    print("Prepared1,198 exactly matched early windows", flush=True)


def features(root, out):
    import numpy as np

    receipt = d.read(root / "prepare/source_receipt.json")
    if d.sha(root / "prepare/train.npy") != receipt["early_array_sha256"]:
        raise ValueError("Early array changed")
    f = d.load_module(
        REPO / "src/neurodecodekit/models/timesfm_word_features.py", "timing_features"
    )
    cov = d.load_module(REPO / "src/neurodecodekit/models/imagined_word_decoder.py", "timing_cov")
    x = f.resample_windows(np.load(root / "prepare/train.npy", allow_pickle=False))
    if x.shape != (1198, 8, 128) or d.sha(BASE / "checkpoint/model.safetensors") != d.WEIGHTS_SHA:
        raise ValueError("Early geometry or checkpoint differs")
    model = f.load_frozen_model(
        BASE / "vendor/timesfm-0df95ae62085a6ac0d0afd1ad40dee2e6c1356ab/src", BASE / "checkpoint"
    )
    chunks = []
    for i in range(0, len(x), 8):
        chunks.append(f.extract_features(model, x[i : i + 8], mode="joint_hidden"))
        if i % 128 == 0:
            print(f"Early TimesFM features: {i}/{len(x)}", flush=True)
    np.save(out / "joint_hidden.npy", np.concatenate(chunks), allow_pickle=False)
    np.save(out / "covariance.npy", cov.covariance_log_features(x), allow_pickle=False)
    np.save(out / "temporal.npy", x.reshape(len(x), -1) * 1e6, allow_pickle=False)


def configure(root):
    d.fit = balanced.balanced_fit

    def dump(path, value):
        if isinstance(value, dict) and value.get("experiment") == "WORD-RECORDING-D1":
            value = dict(value, experiment="WORD-TIMING-D3", window_seconds=[0, 2])
            if "input_sha256" in value:
                value["input_sha256"] = {
                    "calibration.json": d.INPUT_SHA["calibration.json"],
                    "early_train.npy": d.read(root / "prepare/source_receipt.json")[
                        "early_array_sha256"
                    ],
                }
        original_dump(path, value)

    d.dump = dump


def timing_comparison(root, out):
    import numpy as np

    early = d.read(out / "aggregate.json")
    late = d.read(LATE)
    if early["freeze"]["split_sha256"] != SPLIT_SHA or late["freeze"]["split_sha256"] != SPLIT_SHA:
        raise ValueError("Early and late splits differ")
    a = {p["participant"]: p["arms"] for p in early["people"]}
    b = {p["participant"]: p["arms"] for p in late["people"]}
    if set(a) != set(b) or len(a) != 12:
        raise ValueError("Participant populations differ")
    control_max_delta = 0.0
    for person in a:
        for condition in ("within", "cross"):
            for arm in ("uniform", "prior", "metadata", *(m + "_noise" for m in d.MODES)):
                key = f"{condition}/{arm}"
                for metric in ("log_loss", "balanced_accuracy"):
                    control_max_delta = max(
                        control_max_delta, abs(a[person][key][metric] - b[person][key][metric])
                    )
    if control_max_delta > 1e-10:
        raise ValueError("Unchanged control aggregates differ; timing interpretation stops")
    order = sorted(a, key=int)
    draws = np.random.default_rng(d.SEED).integers(0, 12, size=(4000, 12))
    contrasts = []
    for condition in ("within", "cross"):
        for mode in d.MODES:
            key = f"{condition}/{mode}"
            row = {"condition": condition, "mode": mode}
            for metric, sign in (("log_loss", -1), ("balanced_accuracy", 1)):
                gain = np.array([sign * (a[p][key][metric] - b[p][key][metric]) for p in order])
                sg = np.array(
                    [
                        sign * (a[p][key + "_shuffled"][metric] - b[p][key + "_shuffled"][metric])
                        for p in order
                    ]
                )
                for name, values in (
                    (metric + "_gain", gain),
                    (metric + "_gain_minus_shuffled_gain", gain - sg),
                ):
                    row[name] = {
                        "mean": float(values.mean()),
                        "positive_people": int((values > 0).sum()),
                        "ci95_descriptive": np.quantile(
                            values[draws].mean(axis=1), [0.025, 0.975]
                        ).tolist(),
                    }
            contrasts.append(row)
    # The early predictions are scored once above. These calculations use only
    # public participant summaries; late probabilities/targets remain closed.
    d.dump(
        out / "timing_aggregate.json",
        {
            "experiment": "WORD-TIMING-D3",
            "early": early,
            "late_aggregate_sha256": d.sha(LATE),
            "late_summary": late["summary"],
            "late_people": late["people"],
            "timing_contrasts": contrasts,
            "late_fit_or_score_operations": 0,
            "unchanged_control_max_absolute_delta": control_max_delta,
            "claim_scope": "Exploratory early/late prompted-task decoding; no separate cue/imagery onset.",
        },
    )


def permissions(role, root):
    reads, files = [], [BASE / "prepared/calibration.json"]
    if role == "prepare":
        files.append(SOURCE / "manifest.json")
        files += [
            SOURCE / "raw" / f"sub-{p}/ses-{s}/eeg/sub-{p}_ses-{s}_task-innerspeech_eeg.{e}"
            for p in range(12)
            for s in d.SESSIONS
            for e in ("eeg", "vhdr", "vmrk")
        ]
    elif role == "features":
        reads += [BASE / "vendor", BASE / "checkpoint"]
        files += [root / "prepare/train.npy", root / "prepare/source_receipt.json"]
    elif role == "predict":
        reads.append(root / "features")
        files.append(root / "prepare/source_receipt.json")
    elif role == "score":
        reads.append(root / "predict")
        files.append(LATE)
    else:
        raise ValueError("Unknown stage")
    return reads, files


def worker(role, root):
    out = root / role
    out.mkdir(parents=True, exist_ok=False)
    py = (REPO / ".venv/bin/python").resolve()
    site = REPO / ".venv/lib/python3.13/site-packages"

    def q(p):
        return json.dumps(str(Path(p).resolve()))

    reads, files = permissions(role, root)
    reads += [
        py.parent.parent,
        site,
        REPO / "src/neurodecodekit",
        "/System",
        "/usr/lib",
        "/usr/share",
        "/Library/Apple",
    ]
    files += [Path(p) for p in ("/dev/null", "/dev/urandom", "/dev/random")]
    profile = [
        "(version 1)",
        "(deny default)",
        '(import "dyld-support.sb")',
        "(allow sysctl-read)",
        "(allow process-info* (target self))",
        f"(allow process-exec (literal {q(py)}))",
    ]
    for p in reads:
        profile += [
            f"(allow file-read* file-map-executable (subpath {q(p)}))",
            f"(allow file-read-metadata (path-ancestors {q(p)}))",
        ]
    for p in files:
        profile += [
            f"(allow file-read* (literal {q(p)}))",
            f"(allow file-read-metadata (path-ancestors {q(p)}))",
        ]
    profile += [
        f"(allow file-read* file-write* (subpath {q(out)}))",
        f"(allow file-read-metadata (path-ancestors {q(out)}))",
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
    command = [
        "/usr/bin/sandbox-exec",
        "-p",
        "\n".join(profile),
        str(py),
        "-I",
        "-S",
        str(Path(__file__).resolve()),
        role,
        "--root",
        str(root),
        "--site",
        str(site),
        "--internal",
    ]
    started, peak = time.monotonic(), 0
    with (out / "worker.log").open("x") as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=out)
        try:
            while child.poll() is None:
                ps = subprocess.run(
                    ["/bin/ps", "-o", "rss=", "-p", str(child.pid)], capture_output=True, text=True
                )
                if ps.returncode and child.poll() is None:
                    raise RuntimeError("Cannot monitor memory")
                peak = max(peak, int(ps.stdout.strip() or "0") * 1024)
                size = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
                if (
                    peak > 4 * 2**30
                    or size > 256 * 2**20
                    or time.monotonic() - started > 900
                    or shutil.disk_usage(root).free < 20 * 2**30
                ):
                    raise RuntimeError("Resource bound reached")
                time.sleep(1)
        finally:
            if child.poll() is None:
                child.kill()
            child.wait()
    d.dump(
        out / "process.json",
        {
            "seconds": time.monotonic() - started,
            "sampled_peak_rss_bytes": peak,
            "returncode": child.returncode,
            "offline": True,
            "source_scope": "exact development whitelist",
        },
    )
    if child.returncode:
        raise RuntimeError(f"Worker failed: {out / 'worker.log'}")
    print((out / "process.json").read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("prepare", "features", "predict", "score"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--internal", action="store_true")
    parser.add_argument("--site")
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.internal:
        worker(args.role, root)
        return
    sys.path.insert(0, args.site)
    from threadpoolctl import threadpool_limits

    started = time.monotonic()
    configure(root)
    with threadpool_limits(limits=1):
        out = root / args.role
        if args.role == "prepare":
            prepare(root, out)
        elif args.role == "features":
            features(root, out)
        elif args.role == "predict":
            d.predict(BASE, root, out)
            if d.read(out / "freeze.json")["split_sha256"] != SPLIT_SHA:
                raise ValueError("D2 split matching failed")
        else:
            d.score(BASE, root, out)
            timing_comparison(root, out)
    d.dump(
        out / "measurement.json",
        {
            "seconds": time.monotonic() - started,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "threads": 1,
        },
    )


if __name__ == "__main__":
    main()
