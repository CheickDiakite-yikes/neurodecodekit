"""One approved all-ten ses-02 Status audit; no trial parser, physiology or models."""

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import threading
import time
import os
from types import SimpleNamespace

from neurodecodekit.datasets.inner_speech import BDFReader, InnerSpeechRefusal
from neurodecodekit.datasets.inner_speech_reference_status import reference_status_events

REPO = Path(__file__).resolve().parents[1]
AUDIT_ID = "INNER-SPEECH-EVENT-AUDIT-S2"
AUDIT_NAME = "inner_speech_session2_event_audit_20261002"
MAX_SECONDS, MAX_RSS, MAX_OUTPUT = 120, 256 * 1024**2, 1024**2
PARTICIPANTS = tuple(f"sub-{i:02d}" for i in range(1, 11))
PLAN = "registries/inner_speech_session2_audit_plan.v0.json"
FAILURE = "registries/inner_speech_temporal_failure.v0.json"
EVENT_REFUSALS = frozenset(("event_count", "reference_transition_limit",
                           "reference_empty_status", "reference_orphan_offsets",
                           "reference_shortest_event"))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute():
    started = time.monotonic()
    frozen = load_script("test_inner_speech_temporal").configured_runner()
    analyze = load_script("inner_speech_session2_structure").analyze_structure
    import psutil

    frozen.LOCAL = frozen.BASE / AUDIT_NAME
    frozen.BASE, frozen.SOURCE, frozen.LOCAL = frozen.canonical_local_paths(
        frozen.BASE, frozen.SOURCE, frozen.LOCAL)
    root, output = frozen.BASE, frozen.LOCAL
    frozen.require(not output.exists(), "audit_already_used")
    frozen.require(not frozen.git("status", "--porcelain", "--untracked-files=no"), "clean_tracked_tree")
    code_paths = frozen.CODE_PATHS + ("scripts/audit_inner_speech_session2.py",
        "scripts/inner_speech_session2_structure.py", "scripts/audit_inner_speech_events.py", PLAN, FAILURE)
    code_hashes = {p: frozen.sha256(REPO / p) for p in code_paths}
    prior = dict(frozen.PRIOR_EVIDENCE)
    prior["inner_speech_temporal_dev_s2_20261002"] = ("started.json", "execution_failed.json")
    evidence = {f"{folder}/{name}": root / folder / name
                for folder, names in prior.items() for name in names}
    before = {name: frozen.sha256(path) for name, path in evidence.items()}
    failure = json.loads((REPO / FAILURE).read_text())
    frozen.require(before["inner_speech_temporal_dev_s2_20261002/started.json"] ==
                   failure["evidence_hashes"]["started_json_sha256"] and
                   before["inner_speech_temporal_dev_s2_20261002/execution_failed.json"] ==
                   failure["evidence_hashes"]["execution_failed_json_sha256"], "prior_failure_changed")
    frozen.require(shutil.disk_usage(root).free >= 20 * 1024**3, "free_disk_floor")
    process, peak = psutil.Process(), 0
    output.mkdir()  # Exclusive consumption before any recording access.
    frozen.write_json(output / "started.json", {"audit_id": AUDIT_ID,
        "started_unix": time.time(), "max_seconds": MAX_SECONDS,
        "max_rss_bytes": MAX_RSS, "max_generated_bytes": MAX_OUTPUT, "workers": 1,
        "approval_text": "approved continue", "code_commit": frozen.git("rev-parse", "HEAD"),
        "code_hashes": code_hashes, "prior_evidence_hashes": before,
        "retry_allowed": False})
    finished, publication = threading.Event(), threading.Lock()
    terminal, stage, participant = False, "source_identity", None

    def check():
        nonlocal peak
        peak = max(peak, process.memory_info().rss)
        frozen.require(time.monotonic() - started < MAX_SECONDS, "audit_deadline")
        frozen.require(peak <= MAX_RSS, "audit_memory_cap")
        frozen.require(shutil.disk_usage(root).free >= 20 * 1024**3, "free_disk_floor")

    def fail(code):
        nonlocal terminal
        if not terminal:
            frozen.write_json(output / "audit_failed.json", {"audit_id": AUDIT_ID,
                "status": "failed_no_retry", "stage": stage, "participant": participant,
                "error_code": code, "elapsed_seconds": time.monotonic() - started,
                "peak_rss_bytes": peak})
            terminal = True

    def watchdog():
        while not finished.wait(.25):
            with publication:
                if terminal:
                    return
                try:
                    check()
                except Exception:
                    try:
                        fail("resource_limit")
                    finally:
                        os._exit(1)

    watcher = threading.Thread(target=watchdog, daemon=True)
    watcher.start()
    try:
        inventory = frozen.source_inventory(SimpleNamespace(check=check))
        frozen.require(tuple(p for p, _, _ in inventory) == PARTICIPANTS, "complete_source_roster")
        rows = []
        for participant, path, digest in inventory:
            stage = "status_structure_audit"
            reader = BDFReader(path)
            outputs, decoded = {}, {}
            decoders = {
                "frozen": lambda: reader.iter_status_events(check, participant=participant, session="ses-02"),
                "independent": lambda: reference_status_events(reader, check=check,
                    participant=participant, session="ses-02"),
            }
            for name, decode in decoders.items():
                try:
                    decoded[name] = decode()
                except InnerSpeechRefusal as error:
                    code = str(error)
                    if code not in EVENT_REFUSALS:
                        raise  # Integrity, truncation and geometry failures are terminal.
                    outputs[name] = {"status": "decoder_refused",
                        "refusal_code": code}
            agreement = (decoded["frozen"] == decoded["independent"]
                         if len(decoded) == 2 else None)
            for name, events in decoded.items():
                # Do not choose a winner when decoders disagree; retain both aggregates.
                if name == "independent" and agreement:
                    outputs[name] = {"status": "decoded", "events": len(events),
                                     "structure_identical_to_frozen": True}
                else:
                    outputs[name] = {"status": "decoded", "structure": analyze(events, check=check)}
            del decoded
            stage = "source_post_hash"
            frozen.require(frozen.sha256(path, check) == digest, "source_changed_during_audit")
            rows.append({"participant": participant, "full_ordered_decoder_agreement": agreement,
                         "decoders": outputs, "source_hash_verified_before_and_after": True})
            check()
        stage = "immutable_evidence_check"
        frozen.require(tuple(r["participant"] for r in rows) == PARTICIPANTS, "complete_roster")
        frozen.require(all(frozen.sha256(path) == before[name] for name, path in evidence.items()) and
                       all(frozen.sha256(REPO / name) == digest for name, digest in code_hashes.items()),
                       "immutable_evidence_changed")
        result = {"schema_version": 1, "audit_id": AUDIT_ID, "status": "audit_completed",
            "dataset": "ds003626", "version": "2.1.2", "session": "ses-02",
            "code_commit": frozen.git("rev-parse", "HEAD"), "participants": rows,
            "participants_audited": len(rows), "decoder_agreement_participants": sum(
                r["full_ordered_decoder_agreement"] is True for r in rows),
            "physiological_windows_read": 0, "training_calls": 0, "scoring_calls": 0,
            "trial_parser_calls": 0, "events_changed": 0, "labels_or_times_inferred": 0,
            "direction_or_answer_identities_exported": 0,
            "prior_evidence_and_scientific_code_unchanged": True,
            "source_opaque_bytes_hashed": 2 * 6870116352,
            "code_hashes": code_hashes, "prior_evidence_hashes": before,
            "alignment_or_scientific_qualification_established": False,
            "elapsed_seconds": time.monotonic() - started, "peak_rss_bytes": peak}
        encoded = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        # Include the one later public aggregate copy and reserve failure metadata.
        existing = sum(p.stat().st_size for p in output.iterdir() if p.is_file())
        frozen.require(existing + 2 * len(encoded) + 4096 <= MAX_OUTPUT, "audit_output_cap")
        with publication:
            check()
            frozen.write_json(output / "result.json", result)
            terminal = True
        print(json.dumps({"status": "audit_completed", "participants": len(rows),
                          "decoder_agreement_participants": result["decoder_agreement_participants"]}), flush=True)
    except Exception as error:
        if terminal:
            return 0
        safe = {"complete_source_roster", "complete_roster", "source_changed_during_audit",
                "source_identity", "source_hash", "session_two_acquisition_identity",
                "acquisition_not_committed", "failed_acquisition", "complete_source_required",
                "immutable_evidence_changed", "audit_output_cap", "audit_deadline",
                "audit_memory_cap", "free_disk_floor", "local_source_containment",
                "file_changed", "body_truncated", "reference_status_truncated",
                "reference_geometry", "reference_incomplete_status"}
        with publication:
            fail(str(error) if str(error) in safe else "source_or_audit_error")
        print(json.dumps({"status": "failed_no_retry", "stage": stage, "participant": participant}), flush=True)
        return 1
    finally:
        finished.set()
        watcher.join(timeout=1)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-approved-audit", action="store_true")
    args = parser.parse_args(argv)
    if not args.execute_approved_audit:
        print(json.dumps({"audit_id": AUDIT_ID, "status": "dry_run_no_data_access",
            "participants": 10, "max_seconds": MAX_SECONDS, "max_rss_bytes": MAX_RSS,
            "max_output_bytes": MAX_OUTPUT, "physiology_training_scoring_allowed": False}))
        return 0
    return execute()


if __name__ == "__main__":
    raise SystemExit(main())
