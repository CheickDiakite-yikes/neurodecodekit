"""One approved, corrected two-hour SPEECH-REPRO-1 attempt; score only once.

Both failed invocations are read-only evidence, never resumed or overwritten.
Reuse its exact source and 50 checkpoints; only the final ten EEGNet fits are
new. Targets, weights and probabilities remain local. No automatic retry.
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
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_speech_reproduction as original

REPO = original.REPO
OLD = original.LOCAL
FAILED_RECOVERY = REPO / "data/speech_repro_1_recovery_20260921"
LOCAL = REPO / "data/speech_repro_1_corrected_20260921"
FAILURE_SHA = "cc260c268518fe2764132a57f83bf4b519ba07003c04192f036be45648fc33b6"
IMPLEMENTATION = "479c1c3964823e43bafc995b11a48242980a532b"
FAILED_RECOVERY_SHA = "acb4394ead52bbe084e547b192e9a92012841bd0bdeddd8dc08daa7645cc8dc5"
FAILED_RECOVERY_IMPLEMENTATION = "059b75bd7c6a1b00098e65f583abfb53a5088138"
CALIBRATION_AUDIT = REPO / "registries/speech_reproduction_calibration_audit.v0.json"
MANIFEST, FREEZE, RESULT = original.MANIFEST, original.FREEZE, original.RESULT
SEED, GIB = original.SEED, original.GIB
write_json, sha256, git = original.write_json, original.sha256, original.git
MAX_SECONDS = 7200


class RecoveryBudget(original.Budget):
    def __init__(self, started_unix=None):
        super().__init__()
        self.started_unix = time.time() if started_unix is None else started_unix
        self.deadline = self.started + MAX_SECONDS - (time.time() - self.started_unix)
        self.stage_started = None

    def check(self, stage_started=None):
        if time.monotonic() >= self.deadline or time.time() - self.started_unix >= MAX_SECONDS:
            raise RuntimeError("Two-hour recovery deadline exceeded; no partial scoring")
        super().check(self.stage_started if stage_started is None else stage_started)

    def storage(self):
        retained = sum(p.stat().st_size for root in (OLD, FAILED_RECOVERY, LOCAL)
                       for p in root.rglob("*") if p.is_file())
        if retained > 1.5 * GIB or shutil.disk_usage(REPO).free < 20 * GIB:
            raise RuntimeError("Combined original/recovery storage budget exceeded")
        self.check()
        return retained


def failure(error, budget):
    marker = LOCAL / "execution_failed.json"
    if not marker.exists():
        write_json(marker, {"error_type": type(error).__name__, "message": str(error),
            "elapsed_seconds": time.time() - budget.started_unix,
            "online_labels_released_to_scorer": (LOCAL / "scoring_consumed.json").exists()})


def watchdog(budget, finished):
    # Enforce total/RSS/stage limits even if a numerical/library call stalls.
    while not finished.wait(1):
        try:
            budget.check()
        except Exception as error:
            try:
                failure(error, budget)
                print("Recovery stopped at its resource limit; no retry or partial score.", flush=True)
            finally:
                os._exit(1)


def verify_original():
    if sha256(OLD / "execution_failed.json") != FAILURE_SHA:
        raise ValueError("Original failed invocation differs from approved recovery lineage")
    started = json.loads((OLD / "started.json").read_text())
    if started["code_commit"] != IMPLEMENTATION:
        raise ValueError("Original implementation identity differs")
    for name in ("scoring_consumed.json", "predictions.npz"):
        if (OLD / name).exists():
            raise ValueError("Original invocation has unexpected predictions or scoring state")


def verify_failed_recovery():
    if sha256(FAILED_RECOVERY / "execution_failed.json") != FAILED_RECOVERY_SHA:
        raise ValueError("Previous recovery failure differs from approved successor lineage")
    started = json.loads((FAILED_RECOVERY / "started.json").read_text())
    if (started["code_commit"] != FAILED_RECOVERY_IMPLEMENTATION
            or started["original_failure_sha256"] != FAILURE_SHA):
        raise ValueError("Previous recovery implementation or original lineage differs")
    for name in ("scoring_consumed.json", "predictions.npz"):
        if (FAILED_RECOVERY / name).exists():
            raise ValueError("Previous recovery has unexpected predictions or scoring state")


def failed_recovery_inventory():
    """Preserve the previous attempt's sealed files without parsing target values."""
    verify_failed_recovery()
    reports = sorted((FAILED_RECOVERY / "pair_reports").glob("*.json"))
    weights = sorted((FAILED_RECOVERY / "checkpoints").glob("*/fold-*.pt"))
    targets = sorted((FAILED_RECOVERY / "private_targets").glob("*.json"))
    if (len(reports), len(weights), len(targets)) != (5, 0, 7):
        raise ValueError("Previous recovery needs five reports, zero checkpoints and seven sealed files")
    paths = [FAILED_RECOVERY / name for name in (
        "started.json", "execution_failed.json", "preflight.json")]
    return {path.relative_to(FAILED_RECOVERY).as_posix(): sha256(path)
            for path in [*paths, *reports, *targets]}


def verify_failed_inventory(expected):
    if failed_recovery_inventory() != expected:
        raise ValueError("Previous failed recovery artifacts changed")


def original_inventory():
    """Hash artifacts opaquely, including sealed files; never parse target values."""
    verify_original()
    reports = sorted((OLD / "pair_reports").glob("*.json"))
    weights = sorted((OLD / "checkpoints").glob("*/fold-*.pt"))
    targets = sorted((OLD / "private_targets").glob("*.json"))
    if (len(reports), len(weights), len(targets)) != (5, 50, 6):
        raise ValueError("Expected exactly five pairs, fifty checkpoints and six sealed target files")
    paths = [OLD / "started.json", OLD / "execution_failed.json", *reports, *weights, *targets]
    return {path.relative_to(OLD).as_posix(): sha256(path) for path in paths}


def verify_inventory(expected):
    if original_inventory() != expected:
        raise ValueError("Original artifacts changed during recovery")


def verify_sources(manifest, budget):
    """No raw download: verify existing source against the same pinned public tree."""
    if manifest["source_commit"] != original.SOURCE_COMMIT or len(manifest["files"]) != 13:
        raise ValueError("Unexpected recovery source selection")
    with original.request("https://api.github.com/repos/OpenNeuroDatasets/ds007591/git/trees/"
                          + original.SOURCE_COMMIT + "?recursive=1") as response:
        tree = json.load(response)
    if tree.get("truncated") or tree["sha"] != original.SOURCE_COMMIT:
        raise ValueError("Pinned source tree identity mismatch")
    entries = {item["path"]: item for item in tree["tree"] if item["type"] == "blob"}
    sidecars = {"README", "dataset_description.json", "events.json"}
    for item in manifest["files"]:
        path = OLD / "source" / item["path"]
        if path.stat().st_size != item["signal_bytes"] or sha256(path) != item["signal_sha256"]:
            raise ValueError("Original signal no longer matches pinned manifest")
        stem = item["path"].removesuffix("_eeg.edf")
        session = "/".join(item["path"].split("/")[:2])
        session_stem = "_".join(item["path"].split("/")[:2])
        sidecars.update(stem + suffix for suffix in (
            "_events.tsv", "_channels.tsv", "_eeg.json", "_bad_channels.json"))
        sidecars.update(f"{session}/eeg/{session_stem}{suffix}" for suffix in (
            "_electrodes.tsv", "_coordsystem.json"))
        event = entries[item["events_path"]]
        if (event["sha"], event["size"]) != (item["events_git_blob_sha"], item["events_bytes"]):
            raise ValueError("Pinned event identity mismatch")
        budget.check()
    receipts = []
    for name in sorted(sidecars):
        path, entry = OLD / "source" / name, entries[name]
        digest = hashlib.sha1(f"blob {path.stat().st_size}\0".encode())
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                budget.check()
        if path.stat().st_size != entry["size"] or digest.hexdigest() != entry["sha"]:
            raise ValueError("Original sidecar no longer matches pinned source")
        receipts.append({"path": name, "bytes": entry["size"], "git_blob_sha": entry["sha"]})
    description = json.loads((OLD / "source/dataset_description.json").read_text())
    if description.get("License") != "CC0":
        raise ValueError("Source license differs")
    return receipts


def expected_pairs(manifest):
    pairs = list(dict.fromkeys(original.pair_key(item) for item in manifest["files"]))
    if len(pairs) != 6 or {(p, c) for p, _, c in pairs} != {
        (p, c) for p in ("sub-1", "sub-2", "sub-3") for c in ("minimallyovert", "covert")
    }:
        raise ValueError("Recovery requires all three people and both conditions")
    return pairs


def validate_complete(freeze, manifest):
    from neurodecodekit.evaluation.speech_reproduction import COMPACT_ARMS

    pairs = expected_pairs(manifest)
    reports = freeze["pairs"]
    if [r["pair_id"] for r in reports] != ["_".join(p) for p in pairs]:
        raise ValueError("Incomplete or reordered pair freeze")
    expected_records = [Path(i["path"]).name.removesuffix("_eeg.edf") for i in manifest["files"]]
    if [e["recording_id"] for r in reports for e in r["extraction"]] != expected_records:
        raise ValueError("Incomplete or reordered recording freeze")
    if freeze["arms"] != [*COMPACT_ARMS, "eegnet_reference"]:
        raise ValueError("Missing registered comparator")
    if (freeze["n_evaluation_trials"] != 341 or sum(r["calibration_trials"] for r in reports) != 600
            or sum(r["evaluation_trials"] for r in reports) != 341):
        raise ValueError("Incomplete original trial selection")
    for report in reports:
        model = report["model"]
        if len(model["folds"]) != 10 or any(f["epochs"] != 100 for f in model["folds"]):
            raise ValueError("Incomplete reference training")
    if (sum(r["checkpoint_reuse"]["reused_fits"] for r in reports) != 50
            or sum(r["new_reference_fits"] for r in reports) != 10):
        raise ValueError("Recovery did not preserve the approved fifty-plus-ten fit allocation")


def predict_body(manifest, budget, started):
    import numpy as np
    from audit_speech_calibration import audit_calibrations
    from neurodecodekit.evaluation.speech_reproduction import COMPACT_ARMS, predict_compact_arms
    from neurodecodekit.models.speech_reference import predict_from_checkpoints, train_predict
    from neurodecodekit.preprocess.speech_reproduction import (
        extract_recording, preflight_recording_timing, validate_source_geometry,
    )

    budget.stage_started = time.monotonic()
    inventory = original_inventory()
    failed_inventory = failed_recovery_inventory()
    receipts = verify_sources(manifest, budget)
    pairs = expected_pairs(manifest)
    if sha256(CALIBRATION_AUDIT) != started["calibration_audit_sha256"]:
        raise ValueError("Committed calibration audit changed since invocation")
    expected_audit = json.loads(CALIBRATION_AUDIT.read_text())
    actual_audit = audit_calibrations(manifest, OLD / "source", OLD / "pair_reports")
    if actual_audit != expected_audit:
        raise ValueError("Calibration preflight differs from committed six-pair audit")
    budget.check()
    preflight = []
    for item in manifest["files"]:
        budget.stage_started = time.monotonic()
        preflight.append({"recording_id": Path(item["path"]).name.removesuffix("_eeg.edf"),
            **preflight_recording_timing(OLD / "source" / item["path"],
                OLD / "source" / item["events_path"],
                OLD / "source" / item["path"].replace("_eeg.edf", "_channels.tsv"))})
        budget.check()
    write_json(LOCAL / "preflight.json", {"recordings": preflight,
        "original_artifacts_sha256": inventory, "source_sidecars": receipts,
        "failed_recovery_artifacts_sha256": failed_inventory,
        "calibration_audit_sha256": started["calibration_audit_sha256"],
        "elapsed_seconds": time.time() - budget.started_unix})
    print("All six calibration and thirteen timing/padding preflights passed.", flush=True)
    pair_reports, trial_ids, people, conditions, records = [], [], [], [], []
    all_predictions = {arm: [] for arm in (*COMPACT_ARMS, "eegnet_reference")}
    for key in pairs:
        person, session, condition = key
        pair_id = "_".join(key)
        geometry_base = OLD / "source" / person / session / "eeg"
        validate_source_geometry(geometry_base / f"{person}_{session}_electrodes.tsv",
                                 geometry_base / f"{person}_{session}_coordsystem.json")
        selected = [item for item in manifest["files"] if original.pair_key(item) == key]
        calibrations = [item for item in selected if "_acq-calibration_" in item["path"]]
        online = [item for item in selected if "_acq-online_" in item["path"]]
        if len(calibrations) != 1 or not online:
            raise ValueError("Missing or ambiguous calibration-to-online pairing")
        old_path = OLD / "pair_reports" / (pair_id + ".json")
        old_report = json.loads(old_path.read_text()) if old_path.exists() else None
        if (old_report is None) != (key == pairs[-1]):
            raise ValueError("Unexpected completed-pair inventory")
        extracts, extraction_metadata = [], []
        for item in [*calibrations, *online]:
            budget.stage_started = time.monotonic()
            recording = Path(item["path"]).name.removesuffix("_eeg.edf")
            role = "calibration" if item in calibrations else "online"
            print(f"Extracting {recording}", flush=True)
            extracted = extract_recording(OLD / "source" / item["path"],
                OLD / "source" / item["events_path"],
                OLD / "source" / item["path"].replace("_eeg.edf", "_channels.tsv"),
                recording_id=recording, role=role,
                private_target_path=LOCAL / "private_targets" / (recording + ".json"),
                seed=SEED, progress=lambda _completed, _total: budget.check())
            budget.check()
            extracts.append(extracted)
            extraction_metadata.append({"recording_id": recording, **extracted["timing_summary"],
                "private_targets_sha256": extracted.get("private_targets_sha256")})
            if role == "online" and old_report is not None:
                if sha256(OLD / "private_targets" / (recording + ".json")) != extracted[
                    "private_targets_sha256"]:
                    raise ValueError("Reconstructed sealed targets differ from original")
            if role == "online" and sha256(
                    FAILED_RECOVERY / "private_targets" / (recording + ".json")) != extracted[
                        "private_targets_sha256"]:
                raise ValueError("Reconstructed sealed targets differ from previous recovery")
        if old_report is not None and extraction_metadata != old_report["extraction"]:
            raise ValueError("Completed pair extraction identity changed")
        budget.stage_started = time.monotonic()
        calibration, evaluations = extracts[0], extracts[1:]
        train_aux, train_eeg = original.compact_features(calibration)
        eval_blocks = [original.compact_features(item) for item in evaluations]
        eval_aux = np.concatenate([item[0] for item in eval_blocks])
        eval_eeg = {name: np.concatenate([item[1][name] for item in eval_blocks]) for name in train_eeg}
        eval_records = [meta["recording_id"] for meta, item in zip(extraction_metadata[1:], evaluations)
                        for _ in item["trial_ids"]]
        probabilities = predict_compact_arms(calibration["calibration_labels"], train_aux, eval_aux,
            train_eeg, eval_eeg, eval_recordings=eval_records, seed=SEED)
        eval_windows = np.concatenate([item["eeg_adaptive"] for item in evaluations])
        budget.check()
        budget.stage_started = None  # Each new reference fold enforces its own 900s deadline.

        def progress(message):
            budget.check()
            if message["event"] in ("reference_fold_start", "reference_fold_complete"):
                budget.stage_started = time.monotonic()
                print(f"{pair_id}: {message['event']} fold {message['fold']}", flush=True)

        if old_report is not None:
            budget.stage_started = time.monotonic()
            model_metadata = old_report["model"]
            probabilities["eegnet_reference"], reuse = predict_from_checkpoints(
                eval_windows, model_metadata, OLD / "checkpoints" / pair_id,
                cal_labels=np.asarray(calibration["calibration_labels"]),
                deadline=budget.deadline, progress=progress)
            reuse = {**reuse, "reused_fits": 10, "original_pair_report_sha256": sha256(old_path)}
            new_fits = 0
        else:
            probabilities["eegnet_reference"], model_metadata = train_predict(
                calibration["adaptive_trials"], np.asarray(calibration["calibration_labels"]),
                eval_windows, deadline=budget.deadline, progress=progress,
                checkpoint_dir=LOCAL / "checkpoints" / pair_id)
            reuse, new_fits = {"reused_fits": 0}, 10
        ids = [trial for item in evaluations for trial in item["trial_ids"]]
        trial_ids.extend(ids)
        people.extend([person] * len(ids))
        conditions.extend([condition] * len(ids))
        records.extend(eval_records)
        for arm, probability in probabilities.items():
            all_predictions[arm].append(probability)
        pair_reports.append({"pair_id": pair_id, "calibration_trials": len(train_aux),
            "evaluation_trials": len(ids), "extraction": extraction_metadata,
            "model": model_metadata, "checkpoint_reuse": reuse, "new_reference_fits": new_fits,
            "elapsed_seconds": time.time() - budget.started_unix})
        write_json(LOCAL / "pair_reports" / (pair_id + ".json"), pair_reports[-1])
        print(f"Completed recovery pair {len(pair_reports)}/6; still unscored.", flush=True)
        del extracts, calibration, evaluations, extracted, eval_blocks, train_aux, train_eeg
        del eval_aux, eval_eeg, eval_windows
        gc.collect()
        budget.storage()
    budget.stage_started = time.monotonic()
    verify_inventory(inventory)
    verify_failed_inventory(failed_inventory)
    if sha256(CALIBRATION_AUDIT) != started["calibration_audit_sha256"]:
        raise ValueError("Calibration audit changed before freeze")
    payload = LOCAL / "predictions.npz"
    with payload.open("xb") as stream:
        np.savez_compressed(stream, trial_ids=np.asarray(trial_ids), participants=np.asarray(people),
            conditions=np.asarray(conditions), recordings=np.asarray(records),
            **{name: np.concatenate(values) for name, values in all_predictions.items()})
    freeze = {"experiment_id": "SPEECH-REPRO-1", "status": "predictions_locked_unscored",
        "code_commit": started["code_commit"], "source_commit": original.SOURCE_COMMIT,
        "source_manifest_sha256": sha256(MANIFEST), "predictions_sha256": sha256(payload),
        "predictions_relative_path": payload.relative_to(REPO).as_posix(),
        "execution_root": LOCAL.relative_to(REPO).as_posix(),
        "started_sha256": sha256(LOCAL / "started.json"), "original_failure_sha256": FAILURE_SHA,
        "original_artifacts_sha256": inventory, "preflight_sha256": sha256(LOCAL / "preflight.json"),
        "failed_recovery_failure_sha256": FAILED_RECOVERY_SHA,
        "failed_recovery_artifacts_sha256": failed_inventory,
        "calibration_audit_sha256": started["calibration_audit_sha256"],
        "n_evaluation_trials": len(trial_ids), "arms": list(all_predictions), "seed": SEED,
        "protocol": "docs/SPEECH_REPRODUCTION_RESEARCH_DECISION.md",
        "execution_amendment": "docs/SPEECH_REPRODUCTION_CALIBRATION_CORRECTION.md",
        "maximum_total_seconds": MAX_SECONDS,
        "compact_settings": {"time_bins": 64, "bands_hz": [[2, 4], [4, 8], [8, 13],
            [13, 30], [30, 60], [60, 118]], "ridge_penalty": 1.0, "intercept_penalized": False,
            "eeg_features": 8960, "auxiliary_features_including_timing": 392},
        "runtime_versions": {name: importlib.metadata.version(name) for name in
            ("numpy", "scipy", "mne", "scikit-learn", "torch")},
        "source_sidecars": receipts, "pairs": pair_reports,
        "execution_seconds": time.time() - budget.started_unix,
        "peak_observed_rss_bytes": budget.peak_rss, "retained_bytes": budget.storage(),
        "online_labels_released_to_scorer": False}
    validate_complete(freeze, manifest)
    budget.check()
    write_json(FREEZE, freeze)
    print("All six pairs complete. Push the prediction hash freeze before one scoring call.", flush=True)


def validate_score_ready(freeze, started):
    if (LOCAL / "execution_failed.json").exists() or (LOCAL / "scoring_consumed.json").exists():
        raise RuntimeError("Recovery failed or scoring already consumed; no retry")
    verify_original()
    verify_failed_recovery()
    if (freeze["execution_root"] != LOCAL.relative_to(REPO).as_posix()
            or freeze["predictions_relative_path"] != (LOCAL / "predictions.npz").relative_to(REPO).as_posix()
            or freeze["original_failure_sha256"] != FAILURE_SHA
            or freeze["failed_recovery_failure_sha256"] != FAILED_RECOVERY_SHA
            or started["original_failure_sha256"] != FAILURE_SHA
            or started["failed_recovery_failure_sha256"] != FAILED_RECOVERY_SHA):
        raise ValueError("Freeze execution root or failed-run lineage differs")
    if (started["deadline_seconds"] != MAX_SECONDS or freeze["maximum_total_seconds"] != MAX_SECONDS
            or time.time() - started["started_unix"] >= MAX_SECONDS):
        raise RuntimeError("Approved recovery deadline expired or changed")
    if (freeze["started_sha256"] != sha256(LOCAL / "started.json")
            or freeze["source_manifest_sha256"] != sha256(MANIFEST)
            or freeze["preflight_sha256"] != sha256(LOCAL / "preflight.json")
            or freeze["calibration_audit_sha256"] != sha256(CALIBRATION_AUDIT)
            or freeze["calibration_audit_sha256"] != started["calibration_audit_sha256"]
            or freeze["code_commit"] != started["code_commit"]):
        raise ValueError("Recovery provenance changed")
    if freeze["status"] != "predictions_locked_unscored" or RESULT.exists():
        raise ValueError("Scoring state is not fresh")
    validate_complete(freeze, json.loads(MANIFEST.read_text()))
    verify_inventory(freeze["original_artifacts_sha256"])
    verify_failed_inventory(freeze["failed_recovery_artifacts_sha256"])


def score_body(freeze_commit, budget, started):
    budget.stage_started = time.monotonic()
    import numpy as np
    from neurodecodekit.evaluation.speech_reproduction import COMPACT_ARMS, score_speech_predictions

    frozen_path = FREEZE.relative_to(REPO).as_posix()
    freeze = json.loads(git("show", f"{freeze_commit}:{frozen_path}"))
    validate_score_ready(freeze, started)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Scoring requires clean committed code and freeze")
    if freeze != json.loads(FREEZE.read_text()):
        raise ValueError("Working freeze differs from committed freeze")
    if git("diff", "--name-only", started["code_commit"], "HEAD").splitlines() != [frozen_path]:
        raise ValueError("Code changed between recovery execution and frozen scoring")
    subprocess.run(["git", "merge-base", "--is-ancestor", freeze_commit, "origin/main"],
                   cwd=REPO, check=True, capture_output=True)
    payload = LOCAL / "predictions.npz"
    if sha256(payload) != freeze["predictions_sha256"]:
        raise ValueError("Predictions changed since freeze")
    budget.storage()
    with np.load(payload, allow_pickle=False) as arrays:
        targets, target_ids = [], []
        budget.check()
        write_json(LOCAL / "scoring_consumed.json", {"freeze_commit": freeze_commit,
            "started_unix": time.time(), "predictions_sha256": freeze["predictions_sha256"]})
        for pair in freeze["pairs"]:
            for recording in pair["extraction"]:
                if recording["private_targets_sha256"] is None:
                    continue
                path = LOCAL / "private_targets" / (recording["recording_id"] + ".json")
                if sha256(path) != recording["private_targets_sha256"]:
                    raise ValueError("Sealed target file changed since extraction")
                private = json.loads(path.read_text())
                targets.extend(private["labels"])
                target_ids.extend(private["trial_ids"])
        if target_ids != arrays["trial_ids"].tolist():
            raise ValueError("Scorer target/prediction trial IDs differ")
        result = score_speech_predictions({name: arrays[name] for name in (*COMPACT_ARMS, "eegnet_reference")},
            np.asarray(targets), arrays["participants"], arrays["conditions"])
    result.update({"freeze_commit": freeze_commit, "predictions_sha256": freeze["predictions_sha256"],
        "source_commit": original.SOURCE_COMMIT, "code_commit": freeze["code_commit"],
        "execution_amendment": freeze["execution_amendment"], "scoring_invocations": 1,
        "original_failure_sha256": FAILURE_SHA,
        "failed_recovery_failure_sha256": FAILED_RECOVERY_SHA,
        "calibration_audit_sha256": freeze["calibration_audit_sha256"],
        "reused_reference_fits": 50, "new_reference_fits": 10,
        "total_recovery_seconds": time.time() - budget.started_unix})
    budget.check()
    if (LOCAL / "execution_failed.json").exists():
        raise RuntimeError("Resource failure before result publication")
    write_json(RESULT, result)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)


def main():
    invoked_at = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("predict", "score"))
    parser.add_argument("--freeze-commit")
    args = parser.parse_args()
    if args.phase == "score" and not args.freeze_commit:
        parser.error("score requires the pushed --freeze-commit")
    if args.phase == "predict":
        verify_original()
        verify_failed_recovery()
        if LOCAL.exists() or FREEZE.exists() or RESULT.exists():
            raise FileExistsError("Recovery already exists; no automatic retry")
        if git("status", "--porcelain", "--untracked-files=no"):
            raise RuntimeError("Commit exact recovery implementation before execution")
        LOCAL.mkdir(parents=False, exist_ok=False)
        started = {"started_unix": invoked_at, "deadline_seconds": MAX_SECONDS,
                   "code_commit": git("rev-parse", "HEAD"), "original_failure_sha256": FAILURE_SHA,
                   "failed_recovery_failure_sha256": FAILED_RECOVERY_SHA,
                   "calibration_audit_sha256": sha256(CALIBRATION_AUDIT),
                   "authorization": "User approved one corrected complete two-hour successor run"}
        write_json(LOCAL / "started.json", started)
    else:
        if (LOCAL / "execution_failed.json").exists() or (LOCAL / "scoring_consumed.json").exists():
            raise RuntimeError("Recovery failed or score consumed; preserve evidence, no retry")
        started = json.loads((LOCAL / "started.json").read_text())
    budget = RecoveryBudget(started["started_unix"])
    finished = threading.Event()
    monitor = threading.Thread(target=watchdog, args=(budget, finished), daemon=True)
    monitor.start()
    try:
        budget.storage()
        if args.phase == "predict":
            predict_body(json.loads(MANIFEST.read_text()), budget, started)
        else:
            score_body(args.freeze_commit, budget, started)
    except Exception as error:
        failure(error, budget)
        raise
    finally:
        finished.set()
        monitor.join(timeout=2)


if __name__ == "__main__":
    main()
