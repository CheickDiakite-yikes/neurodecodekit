"""Execute the single registered SPEECH-REPRO-1 experiment, then score once.

Run with PYTHONPATH=src and the optional neuro/ML dependencies. Raw source,
scorer targets, weights and predictions stay under ignored data/. Only the
hash freeze and aggregate result are written into registries/. No target values
are printed. See docs/SPEECH_REPRODUCTION_RESEARCH_DECISION.md.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request

# Set before NumPy, MNE or Torch imports. No parallel numerical workers.
for _variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                  "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_variable] = "1"

REPO = Path(__file__).resolve().parents[1]
LOCAL = REPO / "data" / "speech_repro_1_20260921"
MANIFEST = REPO / "registries" / "speech_reproduction_source_manifest.v0.json"
FREEZE = REPO / "registries" / "speech_reproduction_prediction_freeze.v0.json"
RESULT = REPO / "registries" / "speech_reproduction_result.v0.json"
SOURCE_COMMIT = "034af61aba855c58450977bf1c1916085c586cd6"
GITHUB = f"https://raw.githubusercontent.com/OpenNeuroDatasets/ds007591/{SOURCE_COMMIT}/"
S3 = "https://s3.amazonaws.com/openneuro.org/ds007591/"
SEED = 20260906
GIB = 1024**3


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=REPO,
                                   text=True, encoding="utf-8").strip()


class Budget:
    def __init__(self):
        import psutil

        self.started = time.monotonic()
        self.deadline = self.started + 21600
        self.process = psutil.Process()
        self.peak_rss = 0

    def check(self, stage_started=None):
        now = time.monotonic()
        self.peak_rss = max(self.peak_rss, self.process.memory_info().rss)
        if now > self.deadline:
            raise RuntimeError("Six-hour execution budget exceeded; do not score partial predictions")
        if stage_started is not None and now - stage_started > 900:
            raise RuntimeError("Fifteen-minute stage limit exceeded")
        if self.peak_rss > 4 * GIB:
            raise RuntimeError("Four-GiB RSS budget exceeded")

    def storage(self):
        retained = sum(p.stat().st_size for p in LOCAL.rglob("*") if p.is_file())
        if retained > 1.5 * GIB or shutil.disk_usage(REPO).free < 20 * GIB:
            raise RuntimeError("Registered storage budget or free-space floor exceeded")
        self.check()
        return retained


def request(url):
    return urllib.request.urlopen(urllib.request.Request(
        url, headers={"User-Agent": "NeuroDecodeKit-SPEECH-REPRO-1"}), timeout=60)


def download(url, destination, expected_bytes, expected_hash, budget, *, git_blob=False):
    """One streamed object; never overwrite existing payloads or accept new identity."""
    start = time.monotonic()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".partial")
    digest = hashlib.sha1() if git_blob else hashlib.sha256()
    if git_blob:
        digest.update(f"blob {expected_bytes}\0".encode())
    size = 0
    if destination.exists():
        raise FileExistsError("Source destination already exists; no implicit experiment rerun")
    with request(url) as source, temporary.open("xb") as output:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            size += len(chunk)
            if size > expected_bytes:
                raise ValueError("Source object exceeds pinned size")
            output.write(chunk)
            digest.update(chunk)
            budget.check(start)
    if size != expected_bytes or digest.hexdigest() != expected_hash:
        raise ValueError("Source size/hash mismatch; refusing replacement")
    temporary.rename(destination)
    budget.storage()


def acquire(manifest, budget):
    """Fetch only the thirteen selected signals and their pinned sidecars."""
    with request("https://api.github.com/repos/OpenNeuroDatasets/ds007591/git/trees/"
                 + SOURCE_COMMIT + "?recursive=1") as response:
        tree = json.load(response)
    if tree.get("truncated") or tree["sha"] != SOURCE_COMMIT:
        raise ValueError("Incomplete or mismatched pinned source tree")
    entries = {entry["path"]: entry for entry in tree["tree"] if entry["type"] == "blob"}
    sidecars = {"README", "dataset_description.json", "events.json"}
    for item in manifest["files"]:
        stem = item["path"].removesuffix("_eeg.edf")
        session = "/".join(item["path"].split("/")[:2])
        session_stem = "_".join(item["path"].split("/")[:2])
        sidecars.update(stem + suffix for suffix in (
            "_events.tsv", "_channels.tsv", "_eeg.json", "_bad_channels.json"))
        sidecars.update(f"{session}/eeg/{session_stem}{suffix}" for suffix in (
            "_electrodes.tsv", "_coordsystem.json"))
        event = entries[item["events_path"]]
        if (event["sha"], event["size"]) != (item["events_git_blob_sha"], item["events_bytes"]):
            raise ValueError("Pinned event identity does not match preregistration")
    receipts = []
    for path in sorted(sidecars):
        entry = entries[path]
        download(GITHUB + path, LOCAL / "source" / path, entry["size"], entry["sha"],
                 budget, git_blob=True)
        receipts.append({"path": path, "bytes": entry["size"], "git_blob_sha": entry["sha"]})
    description = json.loads((LOCAL / "source/dataset_description.json").read_text())
    if description.get("License") != "CC0":
        raise ValueError("Source license differs from selected CC0 release")
    for index, item in enumerate(manifest["files"]):
        sidecar = json.loads((LOCAL / "source" / item["path"].replace(
            "_eeg.edf", "_eeg.json")).read_text())
        if sidecar.get("SamplingFrequency") != 256 or sidecar.get("EEGChannelCount") != 128:
            raise ValueError("Source EEG sample rate or montage differs from proposal")
        download(S3 + item["path"], LOCAL / "source" / item["path"], item["signal_bytes"],
                 item["signal_sha256"], budget)
        print(f"Verified signal {index + 1}/13: {item['path']}", flush=True)
    return receipts


def pair_key(item):
    parts = item["path"].split("/")
    condition = parts[-1].split("_task-")[1].split("_")[0]
    return parts[0], parts[1], condition


def compact_features(extracted):
    import numpy as np
    from neurodecodekit.evaluation.speech_reproduction import fixed_channel_features

    auxiliary = np.concatenate((fixed_channel_features(extracted["nuisance_averaged"],
        full_trial=extracted["nuisance_full"]), extracted["timing"]), axis=1)
    eeg = {name: fixed_channel_features(extracted[key]) for name, key in (
        ("raw", "eeg_raw"), ("filtered", "eeg_adaptive"), ("preaction", "eeg_preaction"))}
    return auxiliary, eeg


def predict():
    import numpy as np
    from neurodecodekit.evaluation.speech_reproduction import COMPACT_ARMS, predict_compact_arms
    from neurodecodekit.models.speech_reference import train_predict
    from neurodecodekit.preprocess.speech_reproduction import (
        extract_recording, validate_source_geometry,
    )

    if LOCAL.exists() or FREEZE.exists() or RESULT.exists():
        raise FileExistsError("This experiment invocation already exists; no implicit rerun")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Commit the exact implementation before execution")
    manifest = json.loads(MANIFEST.read_text())
    if manifest["source_commit"] != SOURCE_COMMIT or len(manifest["files"]) != 13:
        raise ValueError("Unexpected source manifest")
    if shutil.disk_usage(REPO).free < 20 * GIB:
        raise RuntimeError("Insufficient free space")
    # Existing local roots contain only the previously identified synthetic work;
    # count sizes without opening historical payload contents.
    existing = sum(p.stat().st_size for folder in ("data", "cache", ".codex_work")
                   for p in (REPO / folder).rglob("*") if p.is_file())
    if existing + 1.5 * GIB + 3 * GIB > 20 * GIB:
        raise RuntimeError("Research ceiling would consume the untouched reserve")
    budget = Budget()
    write_json(LOCAL / "started.json", {"started_unix": time.time(), "code_commit": git("rev-parse", "HEAD"),
        "existing_research_bytes": existing, "deadline_seconds": 21600})
    try:
        receipts = acquire(manifest, budget)
        pair_reports, trial_ids, people, conditions, records = [], [], [], [], []
        all_predictions = {arm: [] for arm in (*COMPACT_ARMS, "eegnet_reference")}
        for key in dict.fromkeys(pair_key(item) for item in manifest["files"]):
            person, session, condition = key
            pair_id = "_".join(key)
            geometry_base = LOCAL / "source" / person / session / "eeg"
            validate_source_geometry(geometry_base / f"{person}_{session}_electrodes.tsv",
                                     geometry_base / f"{person}_{session}_coordsystem.json")
            selected = [item for item in manifest["files"] if pair_key(item) == key]
            calibrations = [item for item in selected if "_acq-calibration_" in item["path"]]
            online = [item for item in selected if "_acq-online_" in item["path"]]
            if len(calibrations) != 1 or not online:
                raise ValueError("Missing or ambiguous calibration-to-online pairing")
            extracts, extraction_metadata = [], []
            for item in [*calibrations, *online]:
                stage = time.monotonic()
                recording = Path(item["path"]).name.removesuffix("_eeg.edf")
                role = "calibration" if item in calibrations else "online"
                print(f"Extracting {recording}", flush=True)
                extracted = extract_recording(LOCAL / "source" / item["path"],
                    LOCAL / "source" / item["events_path"],
                    LOCAL / "source" / item["path"].replace("_eeg.edf", "_channels.tsv"),
                    recording_id=recording, role=role,
                    private_target_path=LOCAL / "private_targets" / (recording + ".json"),
                    seed=SEED, progress=lambda _completed, _total: budget.check(stage))
                budget.check(stage)
                extracts.append(extracted)
                extraction_metadata.append({"recording_id": recording, **extracted["timing_summary"],
                    "private_targets_sha256": extracted.get("private_targets_sha256")})
            calibration, evaluations = extracts[0], extracts[1:]
            train_aux, train_eeg = compact_features(calibration)
            eval_blocks = [compact_features(item) for item in evaluations]
            eval_aux = np.concatenate([item[0] for item in eval_blocks])
            eval_eeg = {name: np.concatenate([item[1][name] for item in eval_blocks])
                        for name in train_eeg}
            eval_records = [meta["recording_id"] for meta, item in zip(extraction_metadata[1:], evaluations)
                            for _ in item["trial_ids"]]
            probabilities = predict_compact_arms(calibration["calibration_labels"], train_aux, eval_aux,
                train_eeg, eval_eeg, eval_recordings=eval_records, seed=SEED)
            eval_windows = np.concatenate([item["eeg_adaptive"] for item in evaluations])

            def progress(message):
                budget.check()
                print(f"{pair_id}: {json.dumps(message, sort_keys=True)}", flush=True)

            probabilities["eegnet_reference"], model_metadata = train_predict(
                calibration["adaptive_trials"], np.asarray(calibration["calibration_labels"]),
                eval_windows, deadline=budget.deadline, progress=progress,
                checkpoint_dir=LOCAL / "checkpoints" / pair_id)
            ids = [trial for item in evaluations for trial in item["trial_ids"]]
            trial_ids.extend(ids)
            people.extend([person] * len(ids))
            conditions.extend([condition] * len(ids))
            records.extend(eval_records)
            for arm, probability in probabilities.items():
                all_predictions[arm].append(probability)
            pair_reports.append({"pair_id": pair_id, "calibration_trials": len(train_aux),
                "evaluation_trials": len(ids), "extraction": extraction_metadata,
                "model": model_metadata, "elapsed_seconds": time.monotonic() - budget.started})
            write_json(LOCAL / "pair_reports" / (pair_id + ".json"), pair_reports[-1])
            del extracts, calibration, evaluations, extracted, eval_blocks, train_aux, train_eeg
            del eval_aux, eval_eeg, eval_windows
            gc.collect()
            budget.storage()
        payload = LOCAL / "predictions.npz"
        np.savez_compressed(payload, trial_ids=np.asarray(trial_ids), participants=np.asarray(people),
            conditions=np.asarray(conditions), recordings=np.asarray(records),
            **{name: np.concatenate(values) for name, values in all_predictions.items()})
        budget.check()
        freeze = {"experiment_id": "SPEECH-REPRO-1", "status": "predictions_locked_unscored",
            "code_commit": git("rev-parse", "HEAD"), "source_commit": SOURCE_COMMIT,
            "source_manifest_sha256": sha256(MANIFEST), "predictions_sha256": sha256(payload),
            "predictions_relative_path": str(payload.relative_to(REPO)).replace("\\", "/"),
            "n_evaluation_trials": len(trial_ids), "arms": list(all_predictions), "seed": SEED,
            "protocol": "docs/SPEECH_REPRODUCTION_RESEARCH_DECISION.md",
            "execution_amendment": "docs/SPEECH_REPRODUCTION_EXECUTION.md",
            "maximum_total_seconds": 21600,
            "compact_settings": {"time_bins": 64, "bands_hz": [[2, 4], [4, 8], [8, 13],
                [13, 30], [30, 60], [60, 118]], "ridge_penalty": 1.0, "intercept_penalized": False,
                "eeg_features": 8960, "auxiliary_features_including_timing": 392},
            "runtime_versions": {name: importlib.metadata.version(name) for name in
                ("numpy", "scipy", "mne", "scikit-learn", "torch")},
            "source_sidecars": receipts, "pairs": pair_reports,
            "execution_seconds": time.monotonic() - budget.started,
            "peak_observed_rss_bytes": budget.peak_rss, "retained_bytes": budget.storage(),
            "online_labels_released_to_scorer": False}
        write_json(FREEZE, freeze)
        print("Complete predictions locked. Commit and push the hash freeze before scoring.", flush=True)
    except Exception as error:
        write_json(LOCAL / "execution_failed.json", {"error_type": type(error).__name__,
            "message": str(error), "elapsed_seconds": time.monotonic() - budget.started,
            "online_labels_released_to_scorer": False})
        raise


def score(freeze_commit):
    import numpy as np
    from neurodecodekit.evaluation.speech_reproduction import COMPACT_ARMS, score_speech_predictions

    frozen_text = git("show", f"{freeze_commit}:registries/speech_reproduction_prediction_freeze.v0.json")
    freeze = json.loads(frozen_text)
    started = json.loads((LOCAL / "started.json").read_text())
    if time.time() - started["started_unix"] > started["deadline_seconds"]:
        raise RuntimeError("Execution deadline expired before scoring; do not score")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Scoring requires a clean committed implementation and freeze")
    if freeze != json.loads(FREEZE.read_text()) or freeze["status"] != "predictions_locked_unscored":
        raise ValueError("Working freeze differs from the committed unscored freeze")
    # Local remote-tracking ref must contain the freeze; caller verifies push first.
    subprocess.run(["git", "merge-base", "--is-ancestor", freeze_commit, "origin/main"],
                   cwd=REPO, check=True, capture_output=True)
    payload = LOCAL / "predictions.npz"
    if sha256(payload) != freeze["predictions_sha256"] or RESULT.exists():
        raise ValueError("Predictions changed or aggregate result already exists")
    with np.load(payload, allow_pickle=False) as arrays:
        targets, target_ids = [], []
        # Consume once before opening any private target values.
        write_json(LOCAL / "scoring_consumed.json", {"freeze_commit": freeze_commit,
            "started_unix": time.time(), "predictions_sha256": freeze["predictions_sha256"]})
        for pair in freeze["pairs"]:
            for recording in pair["extraction"]:
                if recording["private_targets_sha256"] is None:
                    continue
                path = LOCAL / "private_targets" / (recording["recording_id"] + ".json")
                if sha256(path) != recording["private_targets_sha256"]:
                    raise ValueError("Private target file changed since extraction")
                private = json.loads(path.read_text())
                targets.extend(private["labels"])
                target_ids.extend(private["trial_ids"])
        if target_ids != arrays["trial_ids"].tolist():
            raise ValueError("Scorer target/prediction trial IDs differ")
        result = score_speech_predictions({name: arrays[name] for name in (*COMPACT_ARMS, "eegnet_reference")},
            np.asarray(targets), arrays["participants"], arrays["conditions"])
    result.update({"freeze_commit": freeze_commit, "predictions_sha256": freeze["predictions_sha256"],
        "source_commit": SOURCE_COMMIT, "code_commit": freeze["code_commit"],
        "scoring_invocations": 1})
    write_json(RESULT, result)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("predict", "score"))
    parser.add_argument("--freeze-commit", help="Pushed commit containing the complete prediction freeze")
    args = parser.parse_args()
    if args.phase == "predict":
        predict()
    elif not args.freeze_commit:
        parser.error("score requires --freeze-commit")
    else:
        score(args.freeze_commit)


if __name__ == "__main__":
    main()
