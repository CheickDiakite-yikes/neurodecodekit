"""One frozen EEGMMIDB-SMR-D1 experiment; optional numerical imports are local."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import html
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import re
import resource
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
import warnings


ARMS = ("central", "metadata", "posterior", "earlier", "cue", "shifted", "deranged")
ALL_ARMS = (*ARMS, "prior")
PAIRS = (("C3", "FC3"), ("CZ", "FCZ"), ("C4", "FC4"),
         ("P3", "PO3"), ("PZ", "POZ"), ("P4", "PO4"))
WINDOWS = {"central": (320, 640), "earlier": (-320, 0),
           "cue": (0, 320), "shifted": (-640, -320)}
REQUEST_SHA = "2a5260fe9d3697941450306fad94b473abfba3aa9c74900a2fcf287824ff5bdd"
DECISION_COMMIT = "d129e16ccc636279878a3c03aebdecf0692d7c21"
LIMIT = 512 * 2**20
RSS_LIMIT = 2**30


class Park(RuntimeError):
    """An explicit protocol refusal, never an instruction to retry."""


def require(condition, code):
    if not condition:
        raise Park(code)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value, *, exclusive=False):
    path = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW
    flags |= os.O_EXCL if exclusive else os.O_TRUNC
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read_json(path):
    with Path(path).open() as stream:
        return json.load(stream)


def environment():
    # Do not inherit credentials, editable-project paths, or numerical threading.
    env = {"PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0",
           "PYTHONDONTWRITEBYTECODE": "1", "MNE_DONTWRITE_HOME": "true"}
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[name] = "1"
    return env


def runtime(repo):
    site = repo / ".venv/lib/python3.13/site-packages"
    python = (repo / ".venv/bin/python").resolve(strict=True)
    return python, site.resolve(strict=True)


def sandbox_profile(python, site, script, inputs, output, extra_writes=()):
    def quote(path):
        return json.dumps(str(Path(path).resolve()))
    reads = [python.parent.parent, site, Path("/System"), Path("/usr/lib"),
             Path("/usr/share"), Path("/Library/Apple"), Path("/dev/null"),
             Path("/dev/urandom"), Path("/dev/random")]
    clauses = ["(version 1)", "(deny default)", '(import "dyld-support.sb")',
               "(allow sysctl-read)",
               f"(allow process-exec (literal {quote(python)}))",
               "(allow process-info* (target self))"]
    clauses += [f"(allow file-read* file-map-executable (subpath {quote(p)}))"
                for p in reads]
    clauses += [f"(allow file-read* (literal {quote(p)}))" for p in [script, *inputs]]
    clauses += [f"(allow file-read-metadata (path-ancestors {quote(p)}))"
                for p in [script, *inputs, output, *extra_writes]]
    clauses += [f"(allow file-read* file-write* (subpath {quote(p)}))"
                for p in (output, *extra_writes)]
    # process-fork, other executables, network and task ports remain denied.
    return "\n".join(clauses)


def sandbox_command(repo, script, role, inputs, output, extra=(), extra_writes=()):
    python, site = runtime(repo)
    profile = sandbox_profile(python, site, script, inputs, output, extra_writes)
    return ["/usr/bin/sandbox-exec", "-p", profile, str(python), "-I", "-S",
            str(script), "--site", str(site), role, *map(str, extra)]


def canary_worker(allowed, forbidden, output, parent_pid, port):
    import numpy
    import scipy
    import sklearn

    require(Path(allowed).read_text() == "allowed fixture", "CANARY_ALLOWED_READ")
    denied = []
    for path in forbidden:
        try:
            Path(path).read_bytes()
        except PermissionError:
            denied.append("file")
        else:
            raise Park("CANARY_FORBIDDEN_READ")
    try:
        subprocess.run(["/usr/bin/true"], check=True)
    except PermissionError:
        denied.append("child")
    else:
        raise Park("CANARY_CHILD_EXECUTION")
    with socket.socket() as connection:
        try:
            connection.connect(("127.0.0.1", port))
        except PermissionError:
            denied.append("network")
        else:
            raise Park("CANARY_NETWORK")
    library = ctypes.CDLL(None)
    task = ctypes.c_uint()
    result = library.task_for_pid(library.mach_task_self(), parent_pid, ctypes.byref(task))
    require(result != 0, "CANARY_BROKER_TASK_PORT")
    denied.append("broker_task_port")
    write_json(Path(output) / "canary.json", {
        "passed": True, "denial_count": len(denied), "file_denials": len(forbidden),
        "numpy": numpy.__version__, "scipy": scipy.__version__,
        "sklearn": sklearn.__version__, "official_source_requests": 0})


def preflight(repo):
    """Small generated OS-denial checks; no scientific source or data access."""
    require(sys.platform == "darwin", "MACOS_ISOLATION_REQUIRED")
    python, site = runtime(repo)
    fixture = Path(tempfile.mkdtemp(prefix="neurodecodekit-smr-canary-")).resolve()
    try:
        script = fixture / "runner.py"
        shutil.copyfile(__file__, script)
        allowed = fixture / "allowed.txt"
        allowed.write_text("allowed fixture")
        forbidden = []
        for name in ("raw.edf", "sealed-targets.bin", "old-evidence.bin", "other-checkout.py"):
            path = fixture / name
            path.write_text("generated forbidden canary")
            forbidden.append(path)
        output = fixture / "out"
        output.mkdir()
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            cmd = sandbox_command(repo, script, "canary", [allowed], output,
                                  [allowed, output, os.getpid(), listener.getsockname()[1],
                                   *forbidden])
            started = time.monotonic()
            with (output / "stdout").open("wb") as stdout, (output / "stderr").open("wb") as stderr:
                completed = subprocess.run(cmd, env=environment(), cwd=output, stdout=stdout,
                                           stderr=stderr, timeout=60)
        if completed.returncode:
            # Generated-only diagnostics contain no real data or target values.
            raise Park(f"OS_CANARY_FAILED exit={completed.returncode}: "
                       + (output / "stderr").read_text(errors="replace")[-2000:])
        result = read_json(output / "canary.json")
        result.update(runtime_seconds=time.monotonic()-started,
                      script_sha256=digest(script), python=str(python), site=str(site))
        return result
    finally:
        # Only this freshly-created generated fixture root is removed.
        shutil.rmtree(fixture)


def weights(y, groups):
    import numpy as np
    people = np.unique(groups)
    result = np.zeros(len(y), dtype=float)
    for person in people:
        for label in (0, 1):
            mask = (groups == person) & (y == label)
            require(mask.sum() >= 4, "TRAIN_CLASS_COUNT")
            result[mask] = len(y) / (2 * len(people) * mask.sum())
    require(np.isclose(result.sum(), len(y)), "TRAIN_WEIGHTS")
    return result


def fit_model(x, y, groups):
    import numpy as np
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    w = weights(y, groups)
    mean = np.average(x, axis=0, weights=w)
    sd = np.sqrt(np.average((x-mean)**2, axis=0, weights=w))
    sd[sd == 0] = 1
    model = LogisticRegression(C=0.1, l1_ratio=0.0, solver="lbfgs",
                               fit_intercept=True, max_iter=1000, tol=1e-8,
                               class_weight=None, random_state=0, warm_start=False)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        try:
            model.fit((x-mean)/sd, y, sample_weight=w)
        except ConvergenceWarning as exc:
            raise Park("MODEL_NONCONVERGENCE") from exc
    require(np.array_equal(model.classes_, [0, 1]), "MODEL_CLASS_ORDER")
    require(int(model.n_iter_.max()) < 1000, "MODEL_NONCONVERGENCE")
    require(np.isfinite(model.coef_).all() and np.isfinite(model.intercept_).all(),
            "MODEL_NONFINITE")
    return {"mean": mean.tolist(), "sd": sd.tolist(), "coef": model.coef_[0].tolist(),
            "intercept": float(model.intercept_[0]), "prior": float(np.average(y, weights=w))}


def predict(model, x):
    import numpy as np
    from scipy.special import expit
    p = expit(((x-np.array(model["mean"]))/np.array(model["sd"]))
              @ np.array(model["coef"]) + model["intercept"])
    return np.column_stack([1-p, p])


def metrics(y, p):
    import numpy as np
    require(p.shape == (len(y), 2), "PROBABILITY_SHAPE")
    require(np.isfinite(p).all() and (p >= 0).all() and (p <= 1).all()
            and np.allclose(p.sum(axis=1), 1, rtol=0, atol=1e-12), "INVALID_PROBABILITY")
    require(np.array_equal(np.unique(y), [0, 1]), "SCORE_CLASSES")
    predicted = p.argmax(axis=1)
    correct = predicted == y
    loss = -np.log(np.clip(p[np.arange(len(y)), y], 1e-6, 1-1e-6))
    brier = (p[:, 1]-y)**2
    return np.array([np.mean([correct[y == c].mean() for c in (0, 1)]),
                     np.mean([loss[y == c].mean() for c in (0, 1)]),
                     np.mean([brier[y == c].mean() for c in (0, 1)])])


def sattolo(n):
    order = list(range(n))
    rng = random.Random(0)
    for i in range(n-1, 0, -1):
        j = rng.randrange(i)
        order[i], order[j] = order[j], order[i]
    return order


def spectral_features(data):
    import numpy as np
    from scipy.signal import welch, windows
    require(data.shape[-1] == 320, "WINDOW_LENGTH")
    f, psd = welch(data, fs=160, window=windows.hann(160, sym=False),
                   nperseg=160, noverlap=80, nfft=160, detrend="constant",
                   return_onesided=True, scaling="density", axis=-1, average="mean")
    bands = ((f >= 8) & (f < 12), (f >= 12) & (f < 20), (f >= 20) & (f <= 30))
    return np.log(np.maximum(np.stack([psd[:, band].sum(axis=1) for band in bands],
                                      axis=1), 1e-24)).reshape(-1)


def numerical_worker(role, inputs, output):
    if role.startswith("broker_"):
        root = Path(inputs[0])
        tempfile.tempdir = str(root / "tmp")
        result = broker_partition(root, read_json(inputs[1]), role.removeprefix("broker_"))
        write_json(Path(output)/"missingness.json", result)
        return
    import numpy as np
    output = Path(output)
    counters = {"started": 0, "completed": 0}

    def counted_fit(x, y, groups):
        counters["started"] += 1
        write_json(output/"fit_counts.json", counters)
        model = fit_model(x, y, groups)
        counters["completed"] += 1
        write_json(output/"fit_counts.json", counters)
        return model
    if role in ("development", "fit"):
        with np.load(inputs[0], allow_pickle=False) as bundle:
            data = {k: bundle[k] for k in bundle.files}
        y, groups = data["y"], data["groups"]
        if role == "development":
            scores = []
            for person in range(10):
                train = (groups == person) & (data["runs"] == 0)
                test = (groups == person) & (data["runs"] == 1)
                require(train.sum() >= 12 and test.sum() >= 12, "DEVELOPMENT_ROWS")
                require(min(np.bincount(y[test], minlength=2)) >= 4, "DEVELOPMENT_CLASSES")
                model = counted_fit(data["central"][train], y[train], groups[train])
                actual = metrics(y[test], predict(model, data["central"][test]))
                prior = metrics(y[test], np.tile([1-model["prior"], model["prior"]], (test.sum(), 1)))
                scores.append([*actual.tolist(), float(prior[1]-actual[1])])
            scores = np.array(scores)
            result = {"people": 10, "fits": 10, "mean_balanced_accuracy": float(scores[:, 0].mean()),
                      "mean_macro_log_loss": float(scores[:, 1].mean()),
                      "mean_binary_macro_brier": float(scores[:, 2].mean()),
                      "mean_log_loss_increment": float(scores[:, 3].mean()),
                      "people_increment_above_002": int((scores[:, 3] > .020).sum())}
            result["passed"] = (result["mean_balanced_accuracy"] >= .55
                                and result["people_increment_above_002"] >= 6)
            write_json(output / "development_result.json", result)
            write_json(output / "development_people.private.json", scores.tolist())
        else:
            require(len(np.unique(groups)) == 10, "FIT_PEOPLE")
            models = {arm: counted_fit(data[arm], y, groups) for arm in ARMS}
            write_json(output / "models.json", models)
        return
    if role == "predict":
        models = read_json(inputs[0])
        with np.load(inputs[1], allow_pickle=False) as bundle:
            require("y" not in bundle.files, "PREDICTOR_TARGET_COLUMN")
            predictions = {arm: predict(models[arm], bundle[arm]) for arm in ARMS}
            prior = models["central"]["prior"]
            predictions["prior"] = np.tile([1-prior, prior], (len(bundle["groups"]), 1))
            predictions["rows"] = bundle["rows"]
            predictions["groups"] = bundle["groups"]
            require(len(np.unique(bundle["groups"])) == 20, "PREDICTION_PEOPLE")
        np.savez_compressed(output / "predictions.npz", **predictions)
        return
    require(role == "score", "WORKER_ROLE")
    with np.load(inputs[0], allow_pickle=False) as bundle:
        probabilities = {k: bundle[k] for k in bundle.files}
    scoring = {"target_read_started": 1, "target_deliveries": 0, "scores_completed": 0}
    write_json(output/"score_counts.json", scoring)
    with np.load(inputs[1], allow_pickle=False) as bundle:
        targets = {k: bundle[k] for k in bundle.files}
    scoring["target_deliveries"] = 1
    write_json(output/"score_counts.json", scoring)
    require(np.array_equal(probabilities["rows"], targets["rows"])
            and np.array_equal(probabilities["groups"], targets["groups"]), "SCORE_ROW_IDENTITY")
    y, groups = targets["y"], targets["groups"]
    require(np.array_equal(np.unique(groups), np.arange(20)), "SCORE_PEOPLE")
    class_counts = [np.bincount(y[groups == person], minlength=2).tolist() for person in range(20)]
    write_json(output/"class_counts.private.json", class_counts)
    insufficient = sum(sum(count) < 12 or len(count) != 2 or min(count) < 4 for count in class_counts)
    if insufficient:
        write_json(output/"scientific_result.json", {
            "status": "incomplete_class_counts", "people": 20, "people_excluded": 0,
            "people_with_insufficient_class_counts": insufficient, "retained_trials": int(len(y)),
            "conjunction_passed": False, "primary_metrics_computed": False})
        scoring["scores_completed"] = 1
        write_json(output/"score_counts.json", scoring)
        return
    person_metrics = []
    preservation = []
    for person in range(20):
        mask = groups == person
        require(mask.sum() >= 12 and min(np.bincount(y[mask], minlength=2)) >= 4,
                "CONFIRMATION_CLASS_INCOMPLETE")
        person_metrics.append([metrics(y[mask], probabilities[arm][mask]) for arm in ALL_ARMS])
        preservation.append(float(np.mean(y[mask] == y[targets["derange_index"][mask]])))
    values = np.array(person_metrics)  # person, arm, BA/loss/binary Brier
    rng = random.Random(0)
    indices = np.array([[rng.randrange(20) for _ in range(20)] for _ in range(10000)])
    result = {"people": 20, "retained_trials": int(len(y)), "arms": {}, "edges": {},
              "mean_derangement_label_preservation": float(np.mean(preservation)),
              "bootstrap_replicates": 10000, "bootstrap_percentile_method": "linear",
              "claim_ceiling": "unseen-person cued task-condition information; no peripheral attribution"}
    for a, arm in enumerate(ALL_ARMS):
        ci = np.percentile(values[indices, a].mean(axis=1), [2.5, 97.5], axis=0, method="linear")
        summary = {name: {"mean": float(values[:, a, j].mean()), "ci95": ci[:, j].tolist()}
                   for j, name in enumerate(("balanced_accuracy", "macro_log_loss", "binary_macro_brier"))}
        bins = []
        p1 = probabilities[arm][:, 1]
        for b in range(5):
            mask = (p1 >= b/5) & ((p1 < (b+1)/5) if b < 4 else (p1 <= 1))
            bins.append({"count": int(mask.sum()), "mean_probability": float(p1[mask].mean()) if mask.any() else None,
                         "class1_fraction": float(y[mask].mean()) if mask.any() else None})
        summary["reliability_bins"] = bins
        result["arms"][arm] = summary
        if a:
            d = values[:, a, 1]-values[:, 0, 1]
            wins = int((d > .020).sum())
            result["edges"][arm] = {"mean_increment": float(d.mean()), "median_increment": float(np.median(d)),
                "mean_ci95": np.percentile(d[indices].mean(axis=1), [2.5, 97.5], method="linear").tolist(),
                "median_ci95": np.percentile(np.median(d[indices], axis=1), [2.5, 97.5], method="linear").tolist(),
                "wins_above_002": wins, "exact_sign_p": sum(math.comb(20, k) for k in range(wins, 21))/2**20,
                "passed": wins >= 15}
    valid = result["mean_derangement_label_preservation"] < .75
    result["derangement_effective"] = valid
    result["conjunction_passed"] = valid and all(e["passed"] for e in result["edges"].values())
    result["status"] = ("inconclusive_control" if not valid else
                        "preliminary_task_condition_increment" if result["conjunction_passed"] else
                        "conjunction_not_supported")
    write_json(output / "participant_metrics.private.json", {
        "metrics": values.tolist(), "derangement_label_preservation": preservation})
    write_json(output / "scientific_result.json", result)
    scoring["scores_completed"] = 1
    write_json(output/"score_counts.json", scoring)


def selected_header(path):
    """Read only this invocation's authorized EDF header, inside the broker."""
    with Path(path).open("rb") as stream:
        fixed = stream.read(256)
        require(len(fixed) == 256 and fixed[:8].strip() == b"0", "EDF_FORMAT")
        header_bytes = int(fixed[184:192])
        count = int(fixed[252:256])
        duration = float(fixed[244:252])
        require(1 <= count <= 128 and header_bytes == 256+256*count and duration > 0,
                "EDF_HEADER_LAYOUT")
        rest = stream.read(256*count)
    require(len(rest) == 256*count, "EDF_HEADER_LENGTH")
    fields, offset = [], 0
    for width in (16, 80, 8, 8, 8, 8, 8, 80, 8, 32):
        fields.append([rest[offset+i*width:offset+(i+1)*width].decode("latin1").strip()
                       for i in range(count)])
        offset += width*count
    names = [name.upper().rstrip(". \t\r\n") for name in fields[0]]
    required = [name for pair in PAIRS for name in pair]
    require(all(names.count(name) == 1 for name in required), "EDF_REQUIRED_CHANNEL")
    for name in required:
        i = names.index(name)
        require(fields[2][i] in ("V", "mV", "uV", "µV", "μV"), "EDF_EXPLICIT_UNITS")
        require(int(fields[8][i])/duration == 160, "EDF_CHANNEL_RATE")
        require(float(fields[4][i]) > float(fields[3][i])
                and int(fields[6][i]) > int(fields[5][i]), "EDF_CALIBRATION")
    return required


def extract_run(path):
    import numpy as np
    import mne
    required = selected_header(path)
    raw = mne.io.read_raw_edf(path, preload=False, verbose="ERROR")
    try:
        names = [name.upper().rstrip(". \t\r\n") for name in raw.ch_names]
        require(len(names) == 64 and raw.info["sfreq"] == 160, "EDF_SENSOR_COUNT_RATE")
        picks = [names.index(name) for name in required]
        events = [(math.floor(float(onset)*160+.5), float(onset), float(duration), int(label[1])-1)
                  for onset, duration, label in zip(raw.annotations.onset, raw.annotations.duration,
                                                     raw.annotations.description)
                  if label in ("T1", "T2")]
        require(bool(events), "EDF_NO_TASK_EVENTS")
        onsets = [event[0] for event in events]
        features = {arm: [] for arm in ("central", "posterior", "earlier", "cue", "shifted")}
        labels, kept, times = [], [], []
        for row, (sample, onset, duration, label) in enumerate(events):
            windows = {arm: (sample+a, sample+b) for arm, (a, b) in WINDOWS.items()}
            if duration < 4 or any(a < 0 or b > raw.n_times for a, b in windows.values()):
                continue
            if any(a < other < b for a, b in windows.values()
                   for j, other in enumerate(onsets) if j != row):
                continue
            signal = {arm: raw.get_data(picks=picks, start=a, stop=b, units=None,
                                       reject_by_annotation=None, verbose="ERROR")
                      for arm, (a, b) in windows.items()}
            if not all(np.isfinite(value).all() for value in signal.values()):
                continue
            for arm, value in signal.items():
                bipolar = value[::2]-value[1::2]
                features[arm].append(spectral_features(bipolar[:3]))
                if arm == "central":
                    features["posterior"].append(spectral_features(bipolar[3:]))
            kept.append(row)
            labels.append(label)
            times.append(onset/(raw.n_times/160))
        n = len(labels)
        require(n >= 12, "COMMON_MASK_TOO_FEW_ROWS")
        metadata = np.column_stack([times, np.arange(n)/max(1, n-1)])
        permutation = np.array(sattolo(n), dtype=int)
        result = {arm: np.column_stack([metadata, np.array(value)]) for arm, value in features.items()}
        result["metadata"] = metadata
        result["deranged"] = np.column_stack([metadata, np.array(features["central"])[permutation]])
        return result, np.array(labels, dtype=np.int64), permutation, np.array(kept), len(events)
    finally:
        raw.close()


def broker_partition(root, files, partition):
    import numpy as np
    bundles = {arm: [] for arm in ARMS}
    groups, runs, rows, labels, derangement = [], [], [], [], []
    before = after = 0
    for spec in files:
        if spec["partition"] != partition:
            continue
        features, y, mapping, kept, original = extract_run(root / "raw" / Path(spec["path"]).name)
        group = int(spec["participant"][1:]) - (31 if partition == "development" else 41)
        run = 0 if spec["run"] == 3 else 1
        n = len(y)
        for arm in ARMS:
            bundles[arm].append(features[arm])
        groups.extend([group]*n)
        runs.extend([run]*n)
        rows.extend([hashlib.sha256(f"{partition}:{group}:{run}:{r}".encode()).hexdigest() for r in kept])
        labels.extend(y.tolist())
        derangement.extend((mapping+after).tolist())
        before += original
        after += n
    data = {arm: np.concatenate(value) for arm, value in bundles.items()}
    data.update(groups=np.array(groups), rows=np.array(rows), runs=np.array(runs))
    if partition == "development":
        data["y"] = np.array(labels, dtype=np.int64)
    else:
        np.savez_compressed(root / "sealed" / "targets.npz", y=np.array(labels, dtype=np.int64),
                            groups=data["groups"], rows=data["rows"], derange_index=np.array(derangement))
    np.savez_compressed(root / "features" / f"{partition}.npz", **data)
    return {"original_trials": before, "retained_trials": after, "excluded_trials": before-after}


def tree_rss():
    table = subprocess.check_output(["/bin/ps", "-A", "-o", "pid=,ppid=,rss="], text=True)
    records = [tuple(map(int, line.split())) for line in table.splitlines() if line.strip()]
    children = {os.getpid()}
    while True:
        larger = children | {pid for pid, parent, _ in records if parent in children}
        if larger == children:
            break
        children = larger
    return sum(rss*1024 for pid, _, rss in records if pid in children)


def own_allocation(root):
    total = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in [*dirs, *files]:
            item = os.lstat(Path(directory)/name)
            require(not stat.S_ISLNK(item.st_mode), "INVOCATION_SYMLINK")
            total += item.st_blocks*512
    return total


def check_partitions(root, *, enforce=True):
    """Account only freshly-created invocation entries, never older evidence."""
    totals = {"raw": 0, "metadata": 0, "tmp": 0, "derived": 0, "runtime": 0}
    for directory, _, files in os.walk(root, followlinks=False):
        for name in files:
            path = Path(directory)/name
            info = path.lstat()
            require(not stat.S_ISLNK(info.st_mode), "INVOCATION_SYMLINK")
            top = path.relative_to(root).parts[0]
            bucket = top if top in ("raw", "metadata", "tmp") else (
                "derived" if path.suffix == ".npz" or name == "models.json"
                or name.endswith(".private.json") else "runtime")
            totals[bucket] += info.st_blocks*512
    for bucket, cap in (("raw", 256), ("metadata", 4), ("tmp", 128),
                        ("derived", 32), ("runtime", 32)):
        if enforce:
            require(totals[bucket] <= cap*2**20, "DISK_PARTITION_"+bucket.upper())
    return totals


def monitor_command(cmd, cwd, stdout_path, stderr_path, state, timeout, *, env=None):
    started = time.monotonic()
    with Path(stdout_path).open("wb") as out, Path(stderr_path).open("wb") as err:
        process = subprocess.Popen(cmd, cwd=cwd, env=env or environment(), stdout=out, stderr=err)
        try:
            while process.poll() is None:
                state["peak_process_tree_rss_bytes"] = max(state["peak_process_tree_rss_bytes"], tree_rss())
                require(state["peak_process_tree_rss_bytes"] <= RSS_LIMIT, "RSS_LIMIT")
                if "_root" in state:
                    size = own_allocation(Path(state["_root"]))
                    state["peak_incremental_disk_bytes"] = max(state["peak_incremental_disk_bytes"], size)
                    require(size <= LIMIT, "INCREMENTAL_DISK_LIMIT")
                    check_partitions(Path(state["_root"]))
                require(time.monotonic()-started <= timeout, "PHASE_RUNTIME_LIMIT")
                time.sleep(.1)
            high_water = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            high_water += resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            if sys.platform != "darwin":
                high_water *= 1024
            state["peak_process_tree_rss_bytes"] = max(state["peak_process_tree_rss_bytes"], high_water)
            require(high_water <= RSS_LIMIT, "RSS_HIGH_WATER_LIMIT")
            require(time.monotonic()-started <= timeout, "PHASE_RUNTIME_LIMIT")
            if "_root" in state:
                check_partitions(Path(state["_root"]))
            return process.returncode, time.monotonic()-started
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()


def launch_worker(repo, root, role, inputs, state):
    output = root / role
    output.mkdir()
    script = root / "runner.py"
    allowed = list(inputs)
    writes = ()
    if role.startswith("broker_"):
        allowed = [root/"manifest.json"] + [root/"raw"/Path(item["path"]).name
                   for item in read_json(root/"manifest.json")
                   if item["partition"] == role.removeprefix("broker_")]
        writes = (root/"features", root/"sealed", root/"tmp")
    cmd = sandbox_command(repo, script, "worker", allowed, output,
                          [role, output, *inputs], writes)
    remaining = min(1800-state["numerical_seconds"], 14400-(time.time()-state["started_unix"]))
    require(remaining > 0, "NUMERICAL_OR_END_TO_END_RUNTIME")
    started = time.monotonic()
    try:
        code, _ = monitor_command(cmd, output, output/"stdout", output/"stderr", state, remaining)
    finally:
        state["numerical_seconds"] += time.monotonic()-started
        if (output/"fit_counts.json").exists():
            counts = read_json(output/"fit_counts.json")
            state["fit_calls_started"] += counts["started"]
            state["fits_completed"] += counts["completed"]
        if (output/"score_counts.json").exists():
            counts = read_json(output/"score_counts.json")
            state["confirmation_target_read_started"] = counts["target_read_started"]
            state["confirmation_target_deliveries"] = counts["target_deliveries"]
            state["final_scores"] = counts["scores_completed"]
    require(state["fit_calls_started"] <= 17, "FIT_COUNT_LIMIT")
    if code:
        failure = read_json(output/"failure.json") if (output/"failure.json").exists() else {}
        raise Park(failure.get("code", "NUMERICAL_"+role.upper()+"_FAILED"))
    return output


def curl_request(root, method, url, destination, cap, state):
    require(cap > 0, "BODY_CAP_EXHAUSTED")
    remaining = min(95, 1800-state["acquisition_seconds"],
                    14400-(time.time()-state["started_unix"]))
    require(remaining > 0, "ACQUISITION_OR_END_TO_END_RUNTIME")
    index = state["source_requests"]
    state["source_requests"] += 1
    state["metadata_gets" if method == "META" else "edf_heads" if method == "HEAD" else "edf_gets"] += 1
    header = root / "transport" / f"headers-{index}.txt"
    output = root / "transport" / f"status-{index}.txt"
    error = root / "transport" / f"error-{index}.txt"
    cmd = ["/usr/bin/curl", "-q", "--silent", "--show-error", "--fail", "--proto", "=https",
           "--max-redirs", "0", "--retry", "0", "--connect-timeout", "20", "--max-time", "90",
           "--header", "Accept-Encoding: identity", "--max-filesize", str(cap),
           "--dump-header", str(header), "--write-out", "%{http_code}"]
    if method == "HEAD":
        cmd += ["--head", "--output", "/dev/null"]
    else:
        cmd += ["--output", str(destination)]
    cmd.append(url)
    started = time.monotonic()
    try:
        code, _ = monitor_command(cmd, root, output, error, state, remaining)
    finally:
        state["acquisition_seconds"] += time.monotonic()-started
    body_bytes = destination.stat().st_size if destination.exists() else 0
    if method != "HEAD":
        state["metadata_body_bytes" if method == "META" else "edf_body_bytes"] += body_bytes
    require(state["acquisition_seconds"] <= 1800, "ACQUISITION_RUNTIME")
    require(code == 0, f"TRANSPORT_EXIT_{code}")
    require(output.read_text() == "200", "HTTP_STATUS")
    require(body_bytes <= cap, "BODY_CAP")
    headers = header.read_text(errors="replace")
    final = re.split(r"HTTP/\S+ \d{3}[^\n]*\n", headers)[-1]
    fields = {}
    for line in final.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields.setdefault(key.strip().lower(), []).append(value.strip())
    require(fields.get("content-encoding", ["identity"]) == ["identity"], "CONTENT_ENCODING")
    require("content-range" not in fields, "UNREQUESTED_RANGE")
    return fields


def source_manifest(root, request, state):
    landing = root / "metadata" / "landing.html"
    checksums = root / "metadata" / "SHA256SUMS.txt"
    curl_request(root, "META", request["source"]["landing_url"], landing, 4*2**20, state)
    text = " ".join(html.unescape(re.sub(r"<[^>]*>", " ", landing.read_text())).split()).casefold()
    for expected in ("EEG Motor Movement/Imagery Dataset", "1.0.0", "10.13026/C28G6P",
                     "Open Data Commons Attribution License v1.0"):
        require(expected.casefold() in text, "SOURCE_IDENTITY_OR_LICENSE")
    curl_request(root, "META", request["source"]["checksum_url"], checksums,
                 4*2**20-state["metadata_body_bytes"], state)
    wanted = {item["path"] for item in request["files"]}
    found = {}
    for line in checksums.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)", line)
        if match:
            path = match[2].removeprefix("./")
            if path in wanted:
                require(path not in found, "DUPLICATE_CHECKSUM")
                found[path] = match[1].lower()
    require(set(found) == wanted, "REQUIRED_CHECKSUM_ABSENT")
    manifest = []
    for item in request["files"]:
        header = curl_request(root, "HEAD", request["source"]["file_base_url"]+item["path"],
                               root/"transport"/"head-no-body", 8*2**20, state)
        length = header.get("content-length", [])
        require(len(length) == 1 and length[0].isdigit(), "HEAD_SIZE_ABSENT")
        size = int(length[0])
        require(256 < size <= 8*2**20, "SINGLE_EDF_CAP")
        manifest.append({**item, "bytes": size, "sha256": found[item["path"]]})
    require(sum(item["bytes"] for item in manifest) <= 256*2**20, "EDF_BUNDLE_CAP")
    write_json(root/"manifest.json", manifest)
    return manifest


def acquire_partition(root, request, manifest, partition, state):
    for item in manifest:
        if item["partition"] != partition:
            continue
        path = root / "raw" / Path(item["path"]).name
        cap = min(8*2**20, 256*2**20-state["edf_body_bytes"])
        curl_request(root, "GET", request["source"]["file_base_url"]+item["path"], path, cap, state)
        require(path.stat().st_size == item["bytes"] and digest(path) == item["sha256"],
                "EDF_SIZE_OR_HASH")


def verify_ci(repo, commit, deadline=None):
    gh = shutil.which("gh")
    require(gh is not None, "GITHUB_CLI_UNAVAILABLE")
    common = [gh, "--repo", "CheickDiakite-yikes/neurodecodekit", "run"]
    def budget():
        remaining = 60 if deadline is None else min(60, deadline-time.time())
        require(remaining > 0, "END_TO_END_RUNTIME")
        return remaining
    runs = json.loads(subprocess.check_output(common + ["list", "--commit", commit,
        "--limit", "3", "--json", "databaseId,headSha,status,conclusion"],
        cwd=repo, text=True, timeout=budget()))
    require(bool(runs) and runs[0]["headSha"] == commit
            and runs[0]["conclusion"] == "success", "REQUIRED_CI_NOT_GREEN")
    detail = json.loads(subprocess.check_output(common + ["view", str(runs[0]["databaseId"]),
        "--json", "headSha,status,conclusion,jobs"], cwd=repo, text=True, timeout=budget()))
    jobs = {job["name"]: job for job in detail["jobs"]}
    require(detail["headSha"] == commit and detail["conclusion"] == "success"
            and all(jobs.get(name, {}).get("conclusion") == "success"
                    for name in ("Base Python", "Optional Neuro Readers")), "REQUIRED_CI_JOBS")
    return {"commit": commit, "run": runs[0]["databaseId"], "jobs": {
        name: jobs[name]["databaseId"] for name in ("Base Python", "Optional Neuro Readers")}}


def pre_execution(repo):
    request_path = repo/"registries/eegmmidb_smr_d1_request.v0.json"
    require(digest(request_path) == REQUEST_SHA, "REQUEST_IDENTITY")
    request = read_json(request_path)
    require(digest(repo/request["packet_path"]) == request["packet_sha256"], "PACKET_IDENTITY")
    decision = read_json(repo/"registries/eegmmidb_smr_d1_decision.v0.json")
    require(decision["actual_maintainer_words"] == "continue"
            and decision["request_sha256"] == REQUEST_SHA, "DECISION_IDENTITY")
    decision_ci = verify_ci(repo, DECISION_COMMIT)
    decision_bytes = subprocess.check_output(["git", "show",
        f"{DECISION_COMMIT}:registries/eegmmidb_smr_d1_decision.v0.json"], cwd=repo)
    require(hashlib.sha256(decision_bytes).hexdigest()
            == digest(repo/"registries/eegmmidb_smr_d1_decision.v0.json"), "DECISION_DIRTY")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    implementation_ci = verify_ci(repo, commit)
    relative = "src/neurodecodekit/experiments/eegmmidb_smr_d1.py"
    frozen = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=repo)
    require(hashlib.sha256(frozen).hexdigest() == digest(__file__), "IMPLEMENTATION_DIRTY")
    versions = request["execution_versions"]
    require(sys.version.split()[0] == versions["python"], "PYTHON_VERSION")
    for name in ("numpy", "scipy", "mne", "scikit-learn"):
        require(importlib.metadata.version(name) == versions[name], "DEPENDENCY_VERSION")
    curl_version = subprocess.check_output(["/usr/bin/curl", "--version"], text=True)
    require(curl_version.startswith("curl 8.7.1 ") and "SecureTransport" in curl_version,
            "TRANSPORT_RUNTIME_VERSION")
    require(shutil.disk_usage(repo).free >= 20*2**30, "FILESYSTEM_FREE_FLOOR")
    # Actual earlier same-task aggregate, recovered from completed command
    # exec-cd0c337d-b2e3-4972-acdf-c265a0d88591; no closed root is restatted.
    existing = 15618984*1024
    subsequent_write_allowance = 2**30
    require(existing+subsequent_write_allowance+LIMIT+3*2**30 <= 20*2**30,
            "GLOBAL_ALLOCATION_BOUND")
    isolation = preflight(repo)
    return request, {"decision_ci": decision_ci, "implementation_ci": implementation_ci,
                     "implementation_sha256": digest(__file__), "isolation": isolation,
                     "existing_allocation_measurement_bytes": existing,
                     "subsequent_write_allowance_bytes": subsequent_write_allowance}


def public_state(state):
    return {key: value for key, value in state.items() if not key.startswith("_")}


def persist_state(root, state):
    state["elapsed_seconds"] = time.time()-state["started_unix"]
    state["retained_allocated_bytes"] = own_allocation(root)
    state["disk_partition_bytes"] = check_partitions(root, enforce=False)
    state["edf_body_bytes"] = sum(p.stat().st_size for p in (root/"raw").glob("*.edf"))
    state["metadata_body_bytes"] = sum(p.stat().st_size for p in (root/"metadata").glob("*") if p.is_file())
    state["peak_incremental_disk_bytes"] = max(state["peak_incremental_disk_bytes"],
                                              state["retained_allocated_bytes"])
    write_json(root/"state.json", state)


def cleanup_temporary(root, state):
    temporary = root/"tmp"
    entries = sorted(temporary.rglob("*"), key=lambda p: len(p.parts), reverse=True)
    write_json(root/"temporary_manifest.json", [str(p.relative_to(root)) for p in entries])
    for path in entries:
        require(not path.is_symlink(), "TEMPORARY_SYMLINK")
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()
    state["temporary_entries_cleaned"] = len(entries)
    state["retained_temporary_bytes"] = own_allocation(temporary)


def execute(repo):
    request, preparation = pre_execution(repo)
    # Exclusively new child only; never inspect or resume an existing attempt.
    parent = repo/"outputs"
    parent.mkdir(exist_ok=True)
    require(parent.resolve().parent == repo.resolve(), "OUTPUT_PARENT_IDENTITY")
    root = parent/"eegmmidb-smr-d1-r0"
    root.mkdir(mode=0o700)
    state = {"attempt": "EEGMMIDB-SMR-D1-R0", "phase": "armed", "started_unix": time.time(),
             "_root": str(root), "source_requests": 0, "metadata_gets": 0, "edf_heads": 0,
             "edf_gets": 0, "metadata_body_bytes": 0, "edf_body_bytes": 0,
             "acquisition_seconds": 0., "numerical_seconds": 0., "peak_process_tree_rss_bytes": 0,
             "peak_incremental_disk_bytes": 0, "fit_invocations_reserved": 0,
             "fit_calls_started": 0, "fits_completed": 0, "final_scores": 0,
             "rss_measurement": "100ms tree samples and conservative parent-plus-largest-child high-water bound",
             "confirmation_target_deliveries": 0, "confirmation_target_read_started": 0,
             "score_invocation_reserved": False, "preparation": preparation}
    write_json(root/"consumed.json", {"attempt": state["attempt"], "request_sha256": REQUEST_SHA,
        "decision_commit": DECISION_COMMIT, "implementation": preparation["implementation_ci"],
        "started_unix": state["started_unix"]}, exclusive=True)
    # Persist the newly created root's ancestry before source contact.
    for directory in (root, parent, repo):
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    try:
        for directory in ("metadata", "raw", "transport", "features", "sealed", "tmp"):
            (root/directory).mkdir(mode=0o700)
        shutil.copyfile(__file__, root/"runner.py")
        write_json(root/"request.json", request)
        manifest = source_manifest(root, request, state)
        acquire_partition(root, request, manifest, "development", state)
        broker = launch_worker(repo, root, "broker_development", [root, root/"manifest.json"], state)
        state["development_missingness"] = read_json(broker/"missingness.json")
        state["fit_invocations_reserved"] = 10
        stage = launch_worker(repo, root, "development", [root/"features/development.npz"], state)
        result = read_json(stage/"development_result.json")
        state["development_result"] = result
        if not result["passed"]:
            state["phase"] = "terminal_development_check_failed"
            cleanup_temporary(root, state)
            persist_state(root, state)
            return public_state(state)
        state["fit_invocations_reserved"] = 17
        fit = launch_worker(repo, root, "fit", [root/"features/development.npz"], state)
        acquire_partition(root, request, manifest, "confirmation", state)
        broker = launch_worker(repo, root, "broker_confirmation", [root, root/"manifest.json"], state)
        state["confirmation_missingness"] = read_json(broker/"missingness.json")
        prediction = launch_worker(repo, root, "predict", [fit/"models.json", root/"features/confirmation.npz"], state)
        state["phase"] = "predictions_frozen"
        frozen_files = ["runner.py", "manifest.json", "features/development.npz",
                        "features/confirmation.npz", "sealed/targets.npz", "fit/models.json",
                        "predict/predictions.npz"]
        freeze = {"attempt": state["attempt"], "request_sha256": REQUEST_SHA,
                  "implementation_commit": preparation["implementation_ci"]["commit"],
                  "files": {name: digest(root/name) for name in frozen_files},
                  "confirmation_people": 20, "arms": list(ALL_ARMS), "fits": 17,
                  "target_deliveries": 0, "final_scores": 0}
        require((prediction/"predictions.npz").exists(), "PREDICTION_FILE")
        write_json(root/"freeze.json", freeze, exclusive=True)
        persist_state(root, state)
        return public_state(state)
    except Exception as exc:
        state["phase"] = "terminal_blocker"
        state["blocker"] = str(exc) if isinstance(exc, Park) else type(exc).__name__
        if (root/"tmp").exists():
            cleanup_temporary(root, state)
        persist_state(root, state)
        return public_state(state)


def final_score(repo, freeze_commit):
    root = repo/"outputs/eegmmidb-smr-d1-r0"
    state = read_json(root/"state.json")
    require(state["phase"] == "predictions_frozen", "ATTEMPT_NOT_SCORE_READY")
    try:
        write_json(root/"score-consumed.json", {"freeze_commit": freeze_commit}, exclusive=True)
        state["score_invocation_reserved"] = True
        require(time.time()-state["started_unix"] <= 14400, "END_TO_END_RUNTIME")
        verify_ci(repo, freeze_commit, state["started_unix"]+14400)
        require(time.time()-state["started_unix"] <= 14400, "END_TO_END_RUNTIME")
        published = subprocess.check_output(["git", "show",
            f"{freeze_commit}:registries/eegmmidb_smr_d1_prediction_freeze.v0.json"], cwd=repo)
        freeze = read_json(root/"freeze.json")
        require(json.loads(published) == freeze, "PUBLISHED_FREEZE_IDENTITY")
        require(digest(__file__) == freeze["files"]["runner.py"], "SCORER_CODE_IDENTITY")
        for name, expected in freeze["files"].items():
            require(digest(root/name) == expected, "FROZEN_FILE_DRIFT")
        stage = launch_worker(repo, root, "score", [root/"predict/predictions.npz", root/"sealed/targets.npz"], state)
        state["scientific_result"] = read_json(stage/"scientific_result.json")
        state["phase"] = "terminal_scored"
    except Exception as exc:
        state["phase"] = "terminal_score_blocker"
        state["blocker"] = str(exc) if isinstance(exc, Park) else type(exc).__name__
    cleanup_temporary(root, state)
    persist_state(root, state)
    return public_state(state)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site")
    commands = parser.add_subparsers(dest="role", required=True)
    command = commands.add_parser("preflight")
    command.add_argument("repo", type=Path)
    command = commands.add_parser("canary")
    command.add_argument("allowed")
    command.add_argument("output")
    command.add_argument("parent_pid", type=int)
    command.add_argument("port", type=int)
    command.add_argument("forbidden", nargs="+")
    command = commands.add_parser("worker")
    command.add_argument("operation", choices=["development", "fit", "predict", "score",
                                               "broker_development", "broker_confirmation"])
    command.add_argument("output")
    command.add_argument("inputs", nargs="+")
    command = commands.add_parser("execute")
    command.add_argument("repo", type=Path)
    command = commands.add_parser("score")
    command.add_argument("repo", type=Path)
    command.add_argument("freeze_commit")
    args = parser.parse_args()
    for name, value in environment().items():
        if name != "PATH":
            os.environ[name] = value
    if args.site:
        sys.path.insert(0, args.site)
    elif hasattr(args, "repo"):
        sys.path.insert(0, str(runtime(args.repo)[1]))
    if args.role == "preflight":
        print(json.dumps(preflight(args.repo)))
    elif args.role == "canary":
        canary_worker(args.allowed, args.forbidden, args.output, args.parent_pid, args.port)
    elif args.role == "worker":
        try:
            numerical_worker(args.operation, args.inputs, args.output)
        except Exception as exc:
            code = str(exc) if isinstance(exc, Park) else type(exc).__name__
            write_json(Path(args.output)/"failure.json", {"code": code})
            raise SystemExit(1) from None
    elif args.role == "execute":
        print(json.dumps(execute(args.repo)))
    elif args.role == "score":
        print(json.dumps(final_score(args.repo, args.freeze_commit)))


if __name__ == "__main__":
    main()
