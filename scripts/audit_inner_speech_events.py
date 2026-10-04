"""One approved Status-only diagnosis; never repair or rerun the experiment.

Default is a no-data dry run. Only collapsed structural facts may leave memory.
The frozen parser is called exactly once, with its original, unfiltered events.
"""

import argparse
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import shutil
import threading
import time

from neurodecodekit.datasets.inner_speech import BDFReader, InnerSpeechRefusal, parse_trials

REPO = Path(__file__).resolve().parents[1]
AUDIT_NAME = "inner_speech_event_audit_20260929"
MAX_SECONDS, MAX_RSS, MAX_OUTPUT = 120, 256 * 1024**2, 64 * 1024
_PARSER_CODE = parse_trials.__code__


def family(code):
    """Never reveal direction/answer identity or unknown numeric status words."""
    if code is None:
        return "end_of_events"
    if code in (31, 32, 33, 34):
        return "direction_cue"
    if code in (61, 62, 63, 64):
        return "attention_answer"
    if code in (21, 22, 23):
        return "condition_marker"
    return {11: "experiment_start", 12: "experiment_end", 13: "baseline_start",
            14: "baseline_end", 15: "run_start", 16: "run_end", 17: "attention_question",
            42: "trial_start", 44: "action", 45: "relax", 46: "rest",
            51: "inter_run_rest"}.get(code, "unrecognized_status_word")


def project_parser_refusal(error, *, audit_context=False):
    """Sanitize an existing parser traceback; never read a file or parse again."""
    frame, take = None, None
    trace = error.__traceback__
    while trace is not None:
        if trace.tb_frame.f_code is _PARSER_CODE:
            frame = trace.tb_frame
        elif (trace.tb_frame.f_code.co_name == "take" and
              trace.tb_frame.f_code.co_filename == _PARSER_CODE.co_filename):
            take = trace.tb_frame
        trace = trace.tb_next
    known = {"event_count", "event_format", "event_order", "event_grammar",
             "baseline_end_missing", "trial_timing", "trailing_events", "condition_layout"}
    result = {"parser_status": "refused", "error_code": str(error) if str(error) in known else
              "other_parser_refusal", "completed_trials": None, "first_mismatch": None}
    if frame is not None:
        state = frame.f_locals
        result["completed_trials"] = len(state.get("trials", []))
        position, events = state.get("position"), state["events"]
        if take is not None and type(position) is int:
            present = position < len(events)
            result["first_mismatch"] = {
                "expected_families": sorted({family(c) for c in take.f_locals["allowed"]}),
                "observed_family": family(events[position][1] if present else None),
            }
            if audit_context:
                result["first_mismatch"].update({
                    "is_first_retained_event": position == 0,
                    "is_recording_initial_sample": present and events[position][0] == 0,
                    "completed_run_end_markers": sum(c == 16 for _, c in events[:position]),
                })
    # Only primitive allowlisted facts leave this function, never private frame state.
    return result


def diagnose(events):
    """Project only allowlisted structural fields from one unchanged parse."""
    result = {"event_family_counts": dict(sorted(Counter(family(c) for _, c in events).items()))}
    try:
        trials = parse_trials(events, participant="sub-01")
        result.update(parser_status="passed", completed_trials=len(trials), first_mismatch=None)
    except InnerSpeechRefusal as error:
        result.update(project_parser_refusal(error, audit_context=True))
    return result


def execute():
    # Reuse the already qualified path and receipt checks, not a second reader.
    spec = importlib.util.spec_from_file_location("frozen_inner_runner", REPO / "scripts/test_inner_speech.py")
    frozen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(frozen)
    import psutil

    root, source, failed = frozen.canonical_local_paths(frozen.BASE, frozen.SOURCE, frozen.LOCAL)
    audit = root / AUDIT_NAME
    frozen.require(audit.resolve() == audit and not audit.exists(), "audit_already_used_or_redirected")
    frozen.require((failed / "execution_failed.json").is_file(), "prior_failure_required")
    frozen.require(not frozen.git("diff", "HEAD", "--", *frozen.CODE_PATHS), "frozen_code_modified")
    original = {str(p): frozen.sha256(p) for p in
                (failed / "started.json", failed / "execution_failed.json")}
    fingerprints = frozen.fingerprints()
    frozen.require(frozen.sha256(frozen.ACQUISITION) ==
                   "35caa3bea6e782a67ef982d185eb0781e7938cfe4bccc7b93c89fb86d57b54bb",
                   "acquisition_receipt_changed")
    expected = json.loads(frozen.MANIFEST.read_text())["files"][0]
    acquired = json.loads(frozen.ACQUISITION.read_text())["files"][0]
    relative = "sub-01/ses-01/eeg/sub-01_ses-01_task-innerspeech_eeg.bdf"
    frozen.require(expected["path"] == acquired["path"] == relative, "fixed_audit_recording")
    path = source / relative
    frozen.require(path.resolve().is_relative_to(source) and
                   path.stat().st_size == expected["size_bytes"], "source_identity")
    frozen.require(shutil.disk_usage(root).free >= 20 * 1024**3, "free_disk_floor")
    audit.mkdir()  # Exclusive: any initialized audit requires a new decision before retry.
    started, process, peak = time.monotonic(), psutil.Process(), 0
    frozen.write_json(audit / "started.json", {"audit_id": "INNER-SPEECH-EVENT-AUDIT-1",
                      "started_unix": time.time(), "max_seconds": MAX_SECONDS,
                      "max_rss_bytes": MAX_RSS, "max_output_bytes": MAX_OUTPUT})
    finished, publication = threading.Event(), threading.Lock()
    terminal = False

    def check():
        nonlocal peak
        peak = max(peak, process.memory_info().rss)
        frozen.require(time.monotonic() - started < MAX_SECONDS, "audit_deadline")
        frozen.require(peak <= MAX_RSS, "audit_memory_cap")
        frozen.require(shutil.disk_usage(root).free >= 20 * 1024**3, "free_disk_floor")

    def watchdog():
        while not finished.wait(.25):
            with publication:
                if terminal:
                    return
                try:
                    check()
                except Exception:
                    # No exception text or source values may enter the failure marker.
                    frozen.write_json(audit / "audit_failed.json", {"status": "resource_limit"})
                    os._exit(1)

    watcher = threading.Thread(target=watchdog, daemon=True)
    watcher.start()
    try:
        frozen.require(frozen.sha256(path, check) == acquired["sha256"], "source_hash")
        reader = BDFReader(path)
        events = reader.iter_status_events(check, participant="sub-01")
        result = diagnose(events)
        del events
        check()
        frozen.require(all(frozen.sha256(Path(p)) == digest for p, digest in original.items()) and
                       frozen.fingerprints() == fingerprints, "immutable_evidence_changed")
        result.update(schema_version=1, audit_id="INNER-SPEECH-EVENT-AUDIT-1",
                      participant="sub-01", session="ses-01", dataset="ds003626", version="2.1.2",
                      code_commit=frozen.git("rev-parse", "HEAD"), status="audit_completed",
                      status_summary=reader.status_summary, source_sha256_verified=True,
                      failed_attempt_and_frozen_code_unchanged=True, parser_calls=1,
                      physiological_windows_read=0, training_calls=0, scoring_calls=0,
                      events_changed=0, direction_or_answer_identities_exported=0,
                      elapsed_seconds=time.monotonic() - started, peak_rss_bytes=peak)
        frozen.require(len(json.dumps(result).encode()) + 4096 < MAX_OUTPUT, "audit_output_cap")
        with publication:
            check()
            frozen.write_json(audit / "result.json", result)
            terminal = True
        print(json.dumps({"status": "audit_completed", "parser_status": result["parser_status"]}))
    except Exception:
        if terminal:
            return 0  # A closed console cannot invalidate a completed private result.
        with publication:
            failure = audit / "audit_failed.json"
            if not failure.exists():
                frozen.write_json(failure, {"status": "audit_failed_no_retry"})
            terminal = True
        print(json.dumps({"status": "audit_failed_no_retry"}))
        return 1
    finally:
        finished.set()
        watcher.join(timeout=1)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-approved-audit", action="store_true")
    args = parser.parse_args()
    if not args.execute_approved_audit:
        print(json.dumps({"status": "dry_run_no_data_access", "participants": 1,
                          "scope": "Status only; original parser once; aggregate families only",
                          "max_seconds": MAX_SECONDS, "training_and_scoring_allowed": False}))
        return 0
    return execute()


if __name__ == "__main__":
    raise SystemExit(main())
