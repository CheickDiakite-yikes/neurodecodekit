"""Bounded calibration discovery: auxiliary carriers, power, or filter attribution.

Each fixed experiment has its own immutable output root and single invocation.
No online files are admitted. Explicit flags select separate fixed experiments;
omitting them retains the original, already-consumed auxiliary-only route.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_speech_reproduction as original

REPO = original.REPO
SOURCE = original.LOCAL / "source"
LOCAL = REPO / "data/speech_auxiliary_discovery_20260921"
PLAN = REPO / "registries/speech_auxiliary_discovery_plan.v0.json"
RESULT = REPO / "registries/speech_auxiliary_discovery_result.v0.json"
PRIOR_RESULT_SHA = "5ca61ce244d9d7ed65ba6a3cebd65b0af49a4782979a8b834008553329087d8c"
MAX_SECONDS, MAX_RSS, MAX_OUTPUT = 600, 1024**3, 32 * 1024**2
EXPERIMENT = "auxiliary"
PRIOR_AUXILIARY = REPO / "registries/speech_auxiliary_discovery_result.v0.json"
PRIOR_AUXILIARY_SHA = "794711f5f1731485c8d253ec48674a5ad35971dd9ede31876338c55bed4abda9"
PRIOR_POWER = REPO / "registries/speech_repetition_power_result.v0.json"
PRIOR_POWER_SHA = "daa18472b86d1348d33350e0862f5eec6b51ab4504c056376e98da3503bd0245"
PRIOR_ADAPTIVE = REPO / "registries/speech_adaptive_attribution_result.v0.json"
PRIOR_ADAPTIVE_SHA = "9e28a48e7fbb88eafee93b9955ee11a4184a5bf762801cf6cf9bccb51496826d"
PRIOR_TIME_FREQUENCY = REPO / "registries/speech_time_frequency_result.v0.json"
PRIOR_TIME_FREQUENCY_SHA = "127a1dd0ac98281d8a486c104847f701019f27c5cef8fc3062802eadb90a9553"


def configure_repetition_power():
    """Select one fixed discovery route before main; never alter old artifacts."""
    global EXPERIMENT, LOCAL, PLAN, RESULT
    EXPERIMENT = "repetition_power"
    LOCAL = REPO / "data/speech_repetition_power_20260921"
    PLAN = REPO / "registries/speech_repetition_power_plan.v0.json"
    RESULT = REPO / "registries/speech_repetition_power_result.v0.json"


def configure_adaptive_attribution():
    """Select the fixed sham-input falsifier without reopening previous routes."""
    global EXPERIMENT, LOCAL, PLAN, RESULT
    EXPERIMENT = "adaptive_attribution"
    LOCAL = REPO / "data/speech_adaptive_attribution_20260922"
    PLAN = REPO / "registries/speech_adaptive_attribution_plan.v0.json"
    RESULT = REPO / "registries/speech_adaptive_attribution_result.v0.json"


def configure_time_frequency():
    """Select the fixed auxiliary-independent EEG decomposition discovery."""
    global EXPERIMENT, LOCAL, PLAN, RESULT
    EXPERIMENT = "time_frequency"
    LOCAL = REPO / "data/speech_time_frequency_20260922"
    PLAN = REPO / "registries/speech_time_frequency_plan.v0.json"
    RESULT = REPO / "registries/speech_time_frequency_result.v0.json"


def configure_probability_calibration():
    """Select one nested confidence-scale diagnosis, not a new feature search."""
    global EXPERIMENT, LOCAL, PLAN, RESULT
    EXPERIMENT = "probability_calibration"
    LOCAL = REPO / "data/speech_probability_calibration_20260922"
    PLAN = REPO / "registries/speech_probability_calibration_plan.v0.json"
    RESULT = REPO / "registries/speech_probability_calibration_result.v0.json"


class Budget:
    def __init__(self):
        import psutil

        self.started = time.monotonic()
        self.process = psutil.Process()
        self.peak_rss = 0

    def check(self, *_):
        self.peak_rss = max(self.peak_rss, self.process.memory_info().rss)
        if time.monotonic() - self.started >= MAX_SECONDS:
            raise RuntimeError("Ten-minute discovery cap exceeded")
        if self.peak_rss > MAX_RSS:
            raise RuntimeError("One-GiB discovery RSS cap exceeded")

    def storage(self):
        output = sum(p.stat().st_size for p in LOCAL.rglob("*") if p.is_file())
        if RESULT.exists():
            output += RESULT.stat().st_size
        if output > MAX_OUTPUT or shutil.disk_usage(REPO).free < 20 * 1024**3:
            raise RuntimeError("Discovery output or free-space cap exceeded")
        self.check()
        return output


def failure(error, budget):
    marker = LOCAL / "execution_failed.json"
    if not marker.exists():
        original.write_json(marker, {"error_type": type(error).__name__, "message": str(error),
            "elapsed_seconds": time.monotonic() - budget.started,
            "online_files_opened": 0, "confirmation_reopened": False})


def watchdog(budget, finished):
    while not finished.wait(0.5):
        try:
            budget.check()
        except Exception as error:
            try:
                failure(error, budget)
                print("Discovery stopped at resource limit; preserve evidence, no automatic retry.",
                      flush=True)
            finally:
                os._exit(1)


def calibration_selection(manifest):
    selected = [item for item in manifest["files"] if "_acq-calibration_" in Path(item["path"]).name]
    pairs = [original.pair_key(item) for item in selected]
    if (manifest["source_commit"] != original.SOURCE_COMMIT or len(pairs) != 6
            or len(set(pairs)) != 6 or {(p, c) for p, _, c in pairs} != {
                (p, c) for p in ("sub-1", "sub-2", "sub-3") for c in ("minimallyovert", "covert")}):
        raise ValueError("Discovery must retain the exact six original calibration pairs")
    for item in selected:
        path, events = Path(item["path"]), Path(item["events_path"])
        if (path.is_absolute() or ".." in path.parts or "_acq-online_" in path.name
                or events.as_posix() != path.as_posix().removesuffix("_eeg.edf") + "_events.tsv"):
            raise ValueError("Only exact calibration source and sibling events are admitted")
    return selected


def verify_inputs(selected, freeze, budget):
    sidecars = {item["path"]: item for item in freeze["source_sidecars"]}
    receipts = []
    for item in selected:
        path = SOURCE / item["path"]
        if path.stat().st_size != item["signal_bytes"] or original.sha256(path) != item["signal_sha256"]:
            raise ValueError("Calibration signal identity changed")
        for relative in (item["events_path"], item["path"].replace("_eeg.edf", "_channels.tsv")):
            expected = sidecars[relative]
            payload = (SOURCE / relative).read_bytes()
            blob = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
            if (len(payload), blob) != (expected["bytes"], expected["git_blob_sha"]):
                raise ValueError("Calibration sidecar identity changed")
            if relative == item["events_path"] and (len(payload), blob) != (
                    item["events_bytes"], item["events_git_blob_sha"]):
                raise ValueError("Calibration event manifest identity differs")
        receipts.append({"path": item["path"], "signal_sha256": item["signal_sha256"],
                         "events_git_blob_sha": item["events_git_blob_sha"]})
        budget.check()
    return receipts


def verify_bound_metadata(started):
    for key, path in (("plan_sha256", PLAN), ("source_manifest_sha256", original.MANIFEST),
                      ("prediction_freeze_sha256", original.FREEZE)):
        if original.sha256(path) != started[key]:
            raise ValueError(f"Bound metadata changed: {key}")
    if original.sha256(original.RESULT) != PRIOR_RESULT_SHA:
        raise ValueError("Consumed confirmation aggregate changed")
    if EXPERIMENT in ("repetition_power", "adaptive_attribution", "time_frequency", "probability_calibration") and original.sha256(PRIOR_AUXILIARY) != PRIOR_AUXILIARY_SHA:
        raise ValueError("Previous auxiliary discovery aggregate changed")
    if EXPERIMENT in ("adaptive_attribution", "time_frequency", "probability_calibration") and original.sha256(PRIOR_POWER) != PRIOR_POWER_SHA:
        raise ValueError("Previous repetition-power aggregate changed")
    if EXPERIMENT in ("time_frequency", "probability_calibration") and original.sha256(PRIOR_ADAPTIVE) != PRIOR_ADAPTIVE_SHA:
        raise ValueError("Previous adaptive-attribution aggregate changed")
    if EXPERIMENT == "probability_calibration" and original.sha256(PRIOR_TIME_FREQUENCY) != PRIOR_TIME_FREQUENCY_SHA:
        raise ValueError("Previous time-frequency aggregate changed")


def run(budget, started):
    import numpy as np
    from neurodecodekit.experiments.speech_auxiliary_discovery import (
        preflight_calibration, run_pair_discovery,
    )
    from neurodecodekit.preprocess.speech_reproduction import _read_tsv, broker_event_rows
    probability_mode = EXPERIMENT == "probability_calibration"
    power_mode = EXPERIMENT in ("repetition_power", "adaptive_attribution", "time_frequency", "probability_calibration")
    mode_options = {"mode": EXPERIMENT} if EXPERIMENT in ("adaptive_attribution", "time_frequency") else {}
    if probability_mode:
        from neurodecodekit.experiments.speech_probability_calibration import (
            preflight_probability_calibration, run_pair_probability_calibration,
        )
        preflight_calibration = preflight_probability_calibration
        mode_options = {"mode": "time_frequency"}
    if power_mode:
        from neurodecodekit.experiments.speech_repetition_power import run_pair_power_discovery
        from neurodecodekit.preprocess.speech_repetition_power import extract_calibration_power
        extractor = extract_calibration_power
    else:
        from neurodecodekit.preprocess.speech_auxiliary import extract_calibration_auxiliary
        extractor = extract_calibration_auxiliary

    verify_bound_metadata(started)
    plan = json.loads(PLAN.read_text())
    selected = calibration_selection(json.loads(original.MANIFEST.read_text()))
    if plan["calibration_source_paths"] != [item["path"] for item in selected]:
        raise ValueError("Source selection differs from committed discovery plan")
    receipts = verify_inputs(selected, json.loads(original.FREEZE.read_text()), budget)
    eligibility = {}
    for item in selected:
        recording = Path(item["path"]).name.removesuffix("_eeg.edf")
        labels = broker_event_rows(_read_tsv(SOURCE / item["events_path"]), recording,
                                   "calibration")["calibration_labels"]
        eligibility[recording] = preflight_calibration(np.asarray(labels))
        budget.check()
    original.write_json(LOCAL / "preflight.json", eligibility)
    print("All six calibration sources and both split schemes passed; no online file opened.", flush=True)
    reports = []
    for item in selected:
        person, session, condition = original.pair_key(item)
        pair_id = "_".join((person, session, condition))
        extracted = extractor(SOURCE / item["path"],
            SOURCE / item["events_path"], SOURCE / item["path"].replace("_eeg.edf", "_channels.tsv"),
            progress=budget.check, **mode_options)
        budget.check()
        recording = Path(item["path"]).name.removesuffix("_eeg.edf")
        if preflight_calibration(np.asarray(extracted["calibration_labels"])) != eligibility[recording]:
            raise ValueError("Extracted calibration split differs from the all-six preflight")
        model_started = time.monotonic()
        if probability_mode:
            report, probabilities = run_pair_probability_calibration(extracted["auxiliary"],
                extracted["eeg_features"]["full_all"], np.asarray(extracted["calibration_labels"]),
                pair_id=pair_id, progress=budget.check)
            report["power_diagnostics"] = extracted["power_diagnostics"]
        elif power_mode:
            report, probabilities = run_pair_power_discovery(extracted["auxiliary"],
                extracted["eeg_features"], np.asarray(extracted["calibration_labels"]),
                pair_id=pair_id, progress=budget.check, **mode_options)
            report["power_diagnostics"] = extracted["power_diagnostics"]
        else:
            report, probabilities = run_pair_discovery(extracted["features"],
                np.asarray(extracted["calibration_labels"]), pair_id=pair_id, progress=budget.check)
        report.update({"participant": person, "condition": condition,
                       "extraction": extracted["timing_summary"],
                       "fitting_prediction_and_metrics_seconds": time.monotonic() - model_started})
        with (LOCAL / (pair_id + ".npz")).open("xb") as stream:
            np.savez_compressed(stream, **{f"{scheme}__{arm}": values
                for scheme, arms in probabilities.items() for arm, values in arms.items()})
        report["local_oof_sha256"] = original.sha256(LOCAL / (pair_id + ".npz"))
        original.write_json(LOCAL / (pair_id + ".json"), report)
        reports.append(report)
        budget.storage()
        print(f"Completed calibration discovery pair {len(reports)}/6: {pair_id}", flush=True)
        del extracted, probabilities
    verify_bound_metadata(started)
    result = {"experiment_id": LOCAL.name, "lane": "discovery",
        "status": "complete", "code_commit": started["code_commit"], "plan_sha256": started["plan_sha256"],
        "source_manifest_sha256": started["source_manifest_sha256"],
        "prediction_freeze_sha256": started["prediction_freeze_sha256"],
        "prior_confirmation_result_sha256": PRIOR_RESULT_SHA,
        "source_receipts": receipts, "pairs": reports,
        "online_files_opened": 0, "new_download_bytes": 0,
        "eeg_models_fitted": {"auxiliary": 0, "repetition_power": 1200,
                              "adaptive_attribution": 900, "time_frequency": 2700,
                              "probability_calibration": 1500}[EXPERIMENT],
        "ridge_models_fitted": {"auxiliary": 960, "repetition_power": 1320,
                                "adaptive_attribution": 1620, "time_frequency": 2940,
                                "probability_calibration": 2700}[EXPERIMENT],
        "deep_models_fitted": 0,
        "confirmation_reopened": False, "hyperparameter_searches": 0,
        "runtime_versions": {name: importlib.metadata.version(name) for name in
                             ("numpy", "scipy", "mne", "scikit-learn")},
        "runtime_seconds": time.monotonic() - budget.started,
        "peak_observed_rss_bytes": budget.peak_rss, "local_artifact_bytes": budget.storage(),
        "claim_ceiling": "Exploratory within-recording calibration prediction; not online confirmation, causal origin or utility"}
    if power_mode:
        result["prior_auxiliary_discovery_sha256"] = PRIOR_AUXILIARY_SHA
    if EXPERIMENT in ("adaptive_attribution", "time_frequency", "probability_calibration"):
        result["prior_repetition_power_sha256"] = PRIOR_POWER_SHA
    if EXPERIMENT == "adaptive_attribution":
        result["sham_feature_models_fitted"] = 600
    if EXPERIMENT in ("time_frequency", "probability_calibration"):
        result["prior_adaptive_attribution_sha256"] = PRIOR_ADAPTIVE_SHA
        result["auxiliary_only_models_fitted"] = 1200 if probability_mode else 240
    if probability_mode:
        result["prior_time_frequency_sha256"] = PRIOR_TIME_FREQUENCY_SHA
        result["training_only_temperature_parameters_fitted"] = 540
        result["feature_or_model_family_searches"] = 0
    budget.check()
    original.write_json(RESULT, result)
    budget.storage()
    print(f"Complete discovery aggregate: {RESULT.relative_to(REPO)}", flush=True)


def main():
    if LOCAL.exists() or RESULT.exists():
        raise FileExistsError("Discovery invocation already exists; no automatic rerun")
    if original.git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Commit the exact discovery implementation before execution")
    LOCAL.mkdir(exist_ok=False)
    budget = Budget()
    started = {"started_unix": time.time(), "code_commit": original.git("rev-parse", "HEAD"),
               "runtime_cap_seconds": MAX_SECONDS, "rss_cap_bytes": MAX_RSS,
               "output_cap_bytes": MAX_OUTPUT, "plan_sha256": original.sha256(PLAN),
               "source_manifest_sha256": original.sha256(original.MANIFEST),
               "prediction_freeze_sha256": original.sha256(original.FREEZE)}
    original.write_json(LOCAL / "started.json", started)
    finished = threading.Event()
    monitor = threading.Thread(target=watchdog, args=(budget, finished), daemon=True)
    monitor.start()
    try:
        budget.storage()
        run(budget, started)
    except Exception as error:
        failure(error, budget)
        raise
    finally:
        finished.set()
        monitor.join(timeout=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--repetition-power", action="store_true",
                       help="Select the separate, fixed EEG repetition-power discovery")
    modes.add_argument("--adaptive-attribution", action="store_true",
                       help="Select the separate, fixed normalization and sham-EEG falsifier")
    modes.add_argument("--time-frequency", action="store_true",
                       help="Select the fixed auxiliary-independent EEG decomposition discovery")
    modes.add_argument("--probability-calibration", action="store_true",
                       help="Select the fixed nested temperature diagnosis on unchanged features")
    arguments = parser.parse_args()
    if arguments.repetition_power:
        configure_repetition_power()
    elif arguments.adaptive_attribution:
        configure_adaptive_attribution()
    elif arguments.time_frequency:
        configure_time_frequency()
    elif arguments.probability_calibration:
        configure_probability_calibration()
    main()
