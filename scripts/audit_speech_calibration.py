"""Calibration-only class/fold compatibility audit; never open online targets."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_speech_reproduction as original

AUDIT = original.REPO / "registries/speech_reproduction_calibration_audit.v0.json"


def audit_calibrations(manifest, source_root, report_root):
    import numpy as np
    from neurodecodekit.models.speech_reference import calibration_folds
    from neurodecodekit.preprocess.speech_reproduction import WORDS, broker_event_rows

    if manifest["source_commit"] != original.SOURCE_COMMIT:
        raise ValueError("Calibration audit source commit differs")
    selected = [item for item in manifest["files"] if "_acq-calibration_" in item["path"]]
    keys = [original.pair_key(item) for item in selected]
    if len(keys) != 6 or len(set(keys)) != 6 or {(p, c) for p, _, c in keys} != {
        (p, c) for p in ("sub-1", "sub-2", "sub-3") for c in ("minimallyovert", "covert")
    }:
        raise ValueError("Audit requires the six original calibration pairs")
    reports = []
    for item in selected:
        # Both names must be calibration before any file open. Online rows are out of scope.
        name = item["events_path"]
        expected_name = item["path"].removesuffix("_eeg.edf") + "_events.tsv"
        if (name != expected_name or "_acq-calibration_" not in Path(name).name
                or "_acq-online_" in Path(name).name or Path(name).is_absolute()
                or ".." in Path(name).parts):
            raise ValueError("Only calibration event sidecars may be opened")
        payload = (source_root / name).read_bytes()
        digest = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
        if (len(payload), digest) != (item["events_bytes"], item["events_git_blob_sha"]):
            raise ValueError("Calibration source identity differs from the pinned manifest")
        rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8")), delimiter="\t"))
        recording = Path(name).name.removesuffix("_events.tsv")
        broker = broker_event_rows(rows, recording, "calibration")
        labels = np.asarray(broker["calibration_labels"], dtype=np.int64)
        if len(labels) != 100 or set(labels.tolist()) != set(range(5)):
            raise ValueError("Expected 100 calibration trials and all five fixed classes")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _, splits = calibration_folds(labels)
        if sorted(np.concatenate([v for _, v in splits]).tolist()) != list(range(len(labels))):
            raise ValueError("Calibration validation is not an exact partition")
        folds = []
        for index, (train, validation) in enumerate(splits):
            train_counts = np.bincount(labels[train], minlength=5).tolist()
            validation_counts = np.bincount(labels[validation], minlength=5).tolist()
            if min(train_counts) == 0 or len(validation) == 0 or set(train) & set(validation):
                raise ValueError("A calibration training fold loses a class or overlaps validation")
            folds.append({"fold": index, "training_class_counts": train_counts,
                          "validation_class_counts": validation_counts})
        pair_id = "_".join(original.pair_key(item))
        previous_path = report_root / (pair_id + ".json")
        matches = None
        if previous_path.exists():
            previous = json.loads(previous_path.read_text())["model"]["folds"]
            matches = len(previous) == 10 and all(
                p["validation_indices"] == validation.tolist()
                for p, (_, validation) in zip(previous, splits)
            )
            if not matches:
                raise ValueError("Source-compatible folds differ from previously trained folds")
        reports.append({"pair_id": pair_id, "events_path": name, "events_git_blob_sha": digest,
                        "calibration_trials": len(labels),
                        "class_counts": np.bincount(labels, minlength=5).tolist(),
                        "folds": folds, "split_warnings": sorted({str(w.message) for w in caught}),
                        "all_training_folds_have_all_five_classes": True,
                        "previous_fold_indices_match": matches})
    if sum(r["previous_fold_indices_match"] is True for r in reports) != 5:
        raise ValueError("Expected exactly five previously trained calibration pairs")
    return {"experiment_id": "SPEECH-REPRO-1", "source_commit": manifest["source_commit"],
            "author_commit": "0dca00584c528b288392684dcec0d496b6aa4951",
            "class_order": list(WORDS), "split": "StratifiedKFold(10, shuffle=False)",
            "pairs": reports, "all_six_eligible": True, "online_event_rows_read": 0,
            "private_targets_read": 0, "training_or_scoring_invocations": 0}


def main():
    manifest = json.loads(original.MANIFEST.read_text())
    report = audit_calibrations(manifest, original.LOCAL / "source", original.LOCAL / "pair_reports")
    original.write_json(AUDIT, report)
    print(json.dumps({"all_six_eligible": report["all_six_eligible"], "pairs": [
        {k: p[k] for k in ("pair_id", "class_counts", "previous_fold_indices_match", "split_warnings")}
        for p in report["pairs"]]}, indent=2))


if __name__ == "__main__":
    main()
