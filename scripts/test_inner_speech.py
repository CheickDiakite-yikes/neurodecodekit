"""One fixed fresh-cohort prediction pass and a separately frozen one-shot score.

Default is dry-run. Real execution requires the user's explicit study approval;
--approval-text records that decision, it does not itself grant permission.
No source data, event rows or per-trial outputs may enter Git or OneDrive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

REPO = Path(__file__).resolve().parents[1]
BASE = Path(r"C:\Users\80714\AppData\Local\NeuroDecodeKit")
SOURCE = BASE / "ds003626_v2_1_2_ses01_20260922"
LOCAL = BASE / "inner_speech_test_1_20260922"
PLAN = REPO / "registries/inner_speech_test_plan.v0.json"
MANIFEST = REPO / "registries/inner_speech_source_manifest.v0.json"
ACQUISITION = REPO / "registries/inner_speech_acquisition_result.v0.json"
FREEZE = REPO / "registries/inner_speech_prediction_freeze.v0.json"
RESULT = REPO / "registries/inner_speech_result.v0.json"
CONDITIONS = (("pronounced", 21), ("inner", 22), ("visualization", 23))
MAX_SECONDS, MAX_RSS, MAX_OUTPUT = 1200, 1024**3, 32 * 1024**2
CODE_PATHS = (
    "scripts/test_inner_speech.py",
    "src/neurodecodekit/datasets/inner_speech.py",
    "src/neurodecodekit/experiments/inner_speech.py",
    "src/neurodecodekit/evaluation/speech_reproduction.py",
    "src/neurodecodekit/experiments/speech_probability_calibration.py",
    "registries/inner_speech_test_plan.v0.json",
    "registries/inner_speech_source_manifest.v0.json",
    "registries/inner_speech_acquisition_result.v0.json",
)


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def write_json(path, payload):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def sha256(path, check=None):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024**2), b""):
            digest.update(chunk)
            if check:
                check()
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", *args],
                                   cwd=REPO, text=True, encoding="utf-8").strip()


def fingerprints():
    return {name: sha256(REPO / name) for name in CODE_PATHS}


class Budget:
    def __init__(self, started):
        import psutil
        self.started = started["started_unix"]
        self.process = psutil.Process()
        self.peak_rss = 0
        self.stage, self.participant = "initialization", None
        self.publication_lock = threading.Lock()
        self.completed = False

    def check(self):
        self.peak_rss = max(self.peak_rss, self.process.memory_info().rss)
        require(time.time() - self.started <= MAX_SECONDS, "twenty_minute_deadline")
        require(self.peak_rss <= MAX_RSS, "one_gib_rss")
        require(shutil.disk_usage(BASE).free >= 20 * 1024**3, "free_disk_floor")

    def storage(self, additional=0):
        total = sum(p.stat().st_size for p in LOCAL.rglob("*") if p.is_file())
        total += sum(p.stat().st_size for p in (FREEZE, RESULT) if p.exists())
        require(total + additional <= MAX_OUTPUT - 4096, "generated_output_budget")
        self.check()
        return total


def failure(error, budget):
    path = LOCAL / "execution_failed.json"
    if not path.exists():
        code = str(error)
        write_json(path, {"experiment_id": "INNER-SPEECH-TEST-1", "status": "failed",
            "stage": budget.stage, "participant": budget.participant,
            "error_type": type(error).__name__,
            "error_code": code if re.fullmatch("[a-z_]+", code) else type(error).__name__,
            "elapsed_seconds": time.time() - budget.started,
            "peak_rss_bytes": budget.peak_rss, "retry_or_partial_score_allowed": False})


def watchdog(budget, finished):
    while not finished.wait(0.5):
        with budget.publication_lock:
            if budget.completed:
                return
            try:
                budget.check()
            except Exception as error:
                try:
                    failure(error, budget)
                finally:
                    os._exit(1)


def expected_trials(participant, condition):
    require(participant in {f"sub-{i:02d}" for i in range(1, 11)} and
            condition in dict(CONDITIONS), "participant_condition_identity")
    if condition == "pronounced" or (participant == "sub-03" and condition == "inner"):
        return 40
    return 120 if participant == "sub-03" else 80


def validate_pairs(pairs):
    expected = {(f"sub-{i:02d}", condition) for i in range(1, 11) for condition, _ in CONDITIONS}
    require(len(pairs) == 30 and {(p["participant"], p["condition"]) for p in pairs} == expected,
            "exact_thirty_pair_roster")
    require(all(p["trials"] == expected_trials(p["participant"], p["condition"]) for p in pairs),
            "exact_per_pair_trial_count")


def source_inventory(budget):
    require(sha256(ACQUISITION) ==
            "35caa3bea6e782a67ef982d185eb0781e7938cfe4bccc7b93c89fb86d57b54bb",
            "acquisition_receipt_changed")
    manifest = json.loads(MANIFEST.read_text())
    acquisition = json.loads(ACQUISITION.read_text())
    require(len(acquisition["files"]) == len(manifest["files"]) == 10, "complete_source_required")
    require(SOURCE.resolve() == SOURCE.absolute() and "onedrive" not in str(SOURCE).lower(),
            "local_source_containment")
    output = []
    for expected, acquired in zip(manifest["files"], acquisition["files"]):
        path = SOURCE / expected["path"]
        require(path.resolve().is_relative_to(SOURCE.resolve()) and
                expected["path"] == acquired["path"] and path.stat().st_size == expected["size_bytes"],
                "source_identity")
        require(sha256(path, budget.check) == acquired["sha256"], "source_hash")
        output.append((expected["path"].split("/")[0], path, acquired["sha256"]))
    return output


def qualify_all(inventory, budget):
    import numpy as np
    from neurodecodekit.datasets.inner_speech import BDFReader, parse_trials
    from neurodecodekit.experiments.inner_speech import preflight_condition
    qualified, summaries = [], []
    for person_index, (participant, path, digest) in enumerate(inventory):
        budget.participant = participant
        reader, summary = BDFReader(path), {"participant": participant}
        events = reader.iter_status_events(budget.check, participant=participant)
        trials = parse_trials(events, participant=participant, summary=summary)
        summary["status"] = reader.status_summary
        summary["condition_counts"] = {}
        for condition_index, (condition, code) in enumerate(CONDITIONS):
            selected = np.asarray([i for i, trial in enumerate(trials) if trial.condition == code])
            labels = np.asarray([trials[i].label for i in selected], dtype=np.int64)
            expected = expected_trials(participant, condition)
            require(len(selected) == expected, "condition_trial_count")
            preflight_condition(labels, selected, seed=20260922 + 16 * person_index + 4 * condition_index)
            summary["condition_counts"][condition] = len(selected)
        qualified.append((participant, reader, trials, digest))
        summaries.append(summary)
        budget.check()
    require(sum(x["trials"] for x in summaries) == 2000, "all_two_thousand_trials_required")
    write_json(LOCAL / "qualification.json", {"participants": summaries, "trials": 2000,
                                             "labels_imputed": 0, "trials_excluded": 0})
    return qualified


def participant_features(reader, trials, budget):
    import numpy as np
    from neurodecodekit.datasets.inner_speech import EEG_CHANNELS, EXG_CHANNELS
    from neurodecodekit.experiments.inner_speech import window_features
    features = {name: [] for name in ("P", "E_action", "E_cue", "E_late")}
    picks = (*EEG_CHANNELS, *EXG_CHANNELS)
    for index, trial in enumerate(trials):
        budget.check()
        require(trial.relax - 2048 >= trial.action and trial.cue + 384 <= trial.action,
                "window_crosses_event_boundary")
        action = reader.read_window(trial.relax - 2048, trial.relax, picks)
        primary = window_features(action[:128], action[128:])
        timing = np.asarray([trial.start / 1024, trial.run_ordinal, index % 40,
            (trial.cue - trial.start) / 1024, (trial.action - trial.cue) / 1024,
            (trial.relax - trial.action) / 1024, (trial.rest - trial.relax) / 1024,
            0.0 if index == 0 else (trial.start - trials[index-1].rest) / 1024])
        features["P"].append(np.concatenate((primary["P"], timing)))
        features["E_action"].append(primary["E"])
        cue = reader.read_window(trial.cue, trial.cue + 384, picks)
        features["E_cue"].append(window_features(cue[:128], cue[128:])["E"])
        features["E_late"].append(window_features(action[:128, -384:], action[128:, -384:])["E"])
    return {name: np.stack(rows) for name, rows in features.items()}


def predict(budget, started):
    import numpy as np
    from neurodecodekit.experiments.inner_speech import run_condition
    budget.stage = "source_verification"
    inventory = source_inventory(budget)
    budget.stage = "all_participant_event_qualification"
    qualified = qualify_all(inventory, budget)
    print("All ten participants qualified; no trials excluded or labels inferred.", flush=True)
    pairs = []
    for person_index, (participant, reader, trials, digest) in enumerate(qualified):
        budget.participant, budget.stage = participant, "feature_extraction"
        features = participant_features(reader, trials, budget)
        budget.stage = "nested_predictions"
        for condition_index, (condition, code) in enumerate(CONDITIONS):
            indices = np.asarray([i for i, trial in enumerate(trials) if trial.condition == code])
            labels = np.asarray([trials[i].label for i in indices], dtype=np.int64)
            bundle = run_condition({k: v[indices] for k, v in features.items()}, labels, indices,
                seed=20260922 + 16 * person_index + 4 * condition_index, check=budget.check)
            name = f"{participant}_{condition}"
            predictions, targets, diagnostics = (LOCAL / (name + suffix) for suffix in (
                "_predictions.npz", "_targets.npy", "_diagnostics.json"))
            with predictions.open("xb") as stream:
                np.savez_compressed(stream, **bundle["predictions"],
                    **{"raw_" + key: value for key, value in bundle["uncalibrated"].items()})
            with targets.open("xb") as stream:
                np.save(stream, labels, allow_pickle=False)
            write_json(diagnostics, bundle["fit_diagnostics"])
            pairs.append({"participant": participant, "condition": condition, "trials": len(labels),
                "predictions": predictions.name, "predictions_sha256": sha256(predictions),
                "targets": targets.name, "targets_sha256": sha256(targets),
                "diagnostics": diagnostics.name, "diagnostics_sha256": sha256(diagnostics)})
            budget.storage()
        require(sha256(reader.path, budget.check) == digest, "source_changed_during_features")
        del features
        print(f"Completed participant {person_index+1}/10; held-out metrics not computed.", flush=True)
    validate_pairs(pairs)
    require(not (LOCAL / "execution_failed.json").exists(), "failed_attempt")
    write_json(FREEZE, {"experiment_id": "INNER-SPEECH-TEST-1",
        "code_commit": started["code_commit"], "fingerprints": started["fingerprints"],
        "pairs": pairs, "qualification_sha256": sha256(LOCAL / "qualification.json"),
        "elapsed_seconds": time.time() - budget.started, "peak_rss_bytes": budget.peak_rss,
        "held_out_metrics_computed": False, "scoring_invocations": 0})
    budget.storage()
    print("All predictions frozen. Commit/push ONLY the hash freeze before one score.", flush=True)


def primary_decision(pairs):
    controls = ("P", "deranged_joint", "joint_shuffled", "uniform", "training_prior")
    inner = [pair for pair in pairs if pair["condition"] == "inner"]
    require(len(inner) == 10 and {p["participant"] for p in inner} ==
            {f"sub-{i:02d}" for i in range(1, 11)}, "primary_population")
    passing = [p["participant"] for p in inner if
               all(p["primary_joint_nll_gains"][control] > 0 for control in controls)]
    contrasts = {}
    for control in controls:
        gains = [p["primary_joint_nll_gains"][control] for p in inner]
        positive = sum(gain > 0 for gain in gains)
        contrasts[control] = {"mean_gain_nats": sum(gains) / 10, "positive_participants": positive,
            "one_sided_sign_p": sum(math.comb(10, k) for k in range(positive, 11)) / 1024}
    return {"primary_pass": len(passing) >= 9 and contrasts["P"]["mean_gain_nats"] >= 0.02,
        "same_people_passing_every_control": passing, "required_same_people": 9,
        "minimum_mean_gain_nats": 0.02, "contrasts": contrasts,
        "ties_count_as_nonpositive": True, "secondary_results_cannot_rescue_primary": True}


def publish_result(output, budget):
    staged = LOCAL / "completed_aggregate.json"
    write_json(staged, output)
    # Check encoded size before exclusive publication; no failure can be written
    # by the monitor after this terminal point. Both locations are on C:.
    with budget.publication_lock:
        budget.storage(additional=staged.stat().st_size)
        require(not (LOCAL / "execution_failed.json").exists(), "failed_attempt")
        os.link(staged, RESULT)
        budget.completed = True


def score(freeze_commit, budget, started):
    import numpy as np
    from neurodecodekit.experiments.inner_speech import ARMS, LEARNED_ARMS, score_condition
    require(re.fullmatch("[a-f0-9]{40}", freeze_commit) is not None, "exact_freeze_commit")
    freeze_path = FREEZE.relative_to(REPO).as_posix()
    require(git("rev-parse", "HEAD") == freeze_commit, "freeze_must_be_head")
    require(not git("status", "--porcelain", "--untracked-files=no"), "clean_scoring_tree")
    require(git("diff", "--name-only", started["code_commit"], "HEAD").splitlines() == [freeze_path],
            "only_prediction_freeze_may_change")
    require(git("ls-remote", "origin", "refs/heads/main").split()[0] == freeze_commit,
            "freeze_not_verified_on_remote_main")
    frozen = json.loads(git("show", f"{freeze_commit}:{freeze_path}"))
    require(frozen == json.loads(FREEZE.read_text()) and frozen["fingerprints"] == fingerprints(),
            "freeze_or_code_changed")
    validate_pairs(frozen["pairs"])
    require(sha256(LOCAL / "qualification.json") == frozen["qualification_sha256"], "qualification_changed")
    for pair in frozen["pairs"]:
        for kind in ("predictions", "targets", "diagnostics"):
            path = LOCAL / pair[kind]
            require(path.parent == LOCAL and path.name == pair[kind], "artifact_path")
            require(sha256(path) == pair[kind + "_sha256"], "frozen_artifact_changed")
    budget.stage = "one_shot_scoring"
    budget.storage()
    write_json(LOCAL / "scoring_consumed.json", {"freeze_commit": freeze_commit,
                                               "started_unix": time.time()})
    results = []
    for pair in frozen["pairs"]:
        budget.participant = pair["participant"]
        with np.load(LOCAL / pair["predictions"], allow_pickle=False) as arrays:
            bundle = {"predictions": {arm: arrays[arm] for arm in ARMS},
                      "uncalibrated": {arm: arrays["raw_" + arm] for arm in LEARNED_ARMS}}
            labels = np.load(LOCAL / pair["targets"], allow_pickle=False)
            require(labels.shape == (pair["trials"],), "scored_trial_count")
            result = score_condition(bundle, labels)
        diagnostics = json.loads((LOCAL / pair["diagnostics"]).read_text())
        result.update(participant=pair["participant"], condition=pair["condition"],
                      fit_diagnostics=diagnostics)
        results.append(result)
        budget.check()
    output = {"experiment_id": "INNER-SPEECH-TEST-1", "status": "complete",
        "code_commit": started["code_commit"], "freeze_commit": freeze_commit,
        "pairs": results, "primary": primary_decision(results),
        "qualification": json.loads((LOCAL / "qualification.json").read_text()),
        "elapsed_seconds": time.time() - budget.started,
        "peak_rss_bytes": max(budget.peak_rss, frozen["peak_rss_bytes"]),
        "scoring_invocations": 1, "trials_excluded": 0, "labels_imputed": 0,
        "claim_boundary": json.loads(PLAN.read_text())["interpretation"]}
    publish_result(output, budget)
    print(json.dumps({"status": "complete", "primary": output["primary"]}, indent=2), flush=True)


def main(argv=None):
    invoked_at = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", nargs="?", default="dry-run", choices=("dry-run", "predict", "score"))
    parser.add_argument("--approval-text")
    parser.add_argument("--freeze-commit")
    args = parser.parse_args(argv)
    if args.phase == "dry-run":
        print(json.dumps({"experiment_id": "INNER-SPEECH-TEST-1", "mode": "dry_run",
            "participant_files_opened": 0, "trials_expected": 2000,
            "execution_requires_explicit_study_approval": True}, indent=2))
        return 0
    require(os.name == "nt" and LOCAL.resolve() == LOCAL.absolute() and
            "onedrive" not in str(LOCAL).lower(), "fixed_local_windows_output")
    if args.phase == "predict":
        require(bool(args.approval_text and args.approval_text.strip()), "explicit_approval_record_required")
        require(not LOCAL.exists() and not FREEZE.exists() and not RESULT.exists(), "attempt_already_exists")
        require(not git("status", "--porcelain", "--untracked-files=no"), "commit_before_prediction")
        started = {"experiment_id": "INNER-SPEECH-TEST-1", "started_unix": invoked_at,
            "deadline_unix": invoked_at + MAX_SECONDS, "code_commit": git("rev-parse", "HEAD"),
            "fingerprints": fingerprints(), "approval_text": args.approval_text,
            "approval_field_is_audit_not_authority": True}
        LOCAL.mkdir(parents=False, exist_ok=False)
        write_json(LOCAL / "started.json", started)
    else:
        require(bool(args.freeze_commit), "pushed_freeze_commit_required")
        require(not (LOCAL / "execution_failed.json").exists() and
                not (LOCAL / "scoring_consumed.json").exists() and not RESULT.exists(), "consumed_or_failed")
        started = json.loads((LOCAL / "started.json").read_text())
    require(started["fingerprints"] == fingerprints(), "scientific_code_changed")
    budget = Budget(started)
    finished = threading.Event()
    monitor = threading.Thread(target=watchdog, args=(budget, finished), daemon=True)
    monitor.start()
    try:
        budget.storage()
        if args.phase == "predict":
            predict(budget, started)
        else:
            score(args.freeze_commit, budget, started)
    except Exception as error:
        if budget.completed:
            return 0  # e.g. stdout closed after the scientific result was published
        failure(error, budget)
        print("Study stopped; preserve local failure evidence. No retry or partial score.", flush=True)
        return 1
    finally:
        finished.set()
        monitor.join(timeout=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
