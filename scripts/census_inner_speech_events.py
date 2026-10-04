"""One approved all-ten Status-only census; no repair, physiology or scoring.

Default is a no-data dry run. Structural blocks are not qualified trials.
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

from neurodecodekit.datasets.inner_speech import BDFReader

REPO = Path(__file__).resolve().parents[1]
CENSUS_ID = "INNER-SPEECH-EVENT-CENSUS-1"
CENSUS_NAME = "inner_speech_event_census_20260929"
MAX_SECONDS, MAX_RSS, MAX_OUTPUT = 120, 256 * 1024**2, 1024**2
PARTICIPANTS = tuple(f"sub-{i:02d}" for i in range(1, 11))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


family = load_script("audit_inner_speech_events").family


def inventory(events):
    """Inspect every observed event without repair or emitting ordered event rows.

    Only collapsed family names, counts and timing-range categories leave here.
    Run blocks require exactly one start followed by one end, without nesting.
    Start blocks end at the next start or run boundary, even when malformed.
    """
    families = [family(code) for _, code in events]
    totals = Counter(families)
    transitions = Counter(zip(families, families[1:]))
    boundaries = [(i, f) for i, f in enumerate(families) if f in {"run_start", "run_end"}]
    runs, covered = [], set()
    depth, start, nested = 0, None, False
    for i, name in boundaries:
        if name == "run_start":
            if depth == 0:
                start, nested = i, False
            else:
                nested = True
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0 and not nested:
                runs.append(dict(sorted(Counter(families[start:i + 1]).items())))
                covered.update(range(start, i + 1))

    blocks = Counter()
    stops = {"trial_start", "run_start", "run_end"}
    for i, name in enumerate(families):
        if name != "trial_start":
            continue
        end = i + 1
        while end < len(families) and families[end] not in stops:
            end += 1
        block = families[i:end]
        counts = Counter(block)
        signature = tuple("zero" if counts[f] == 0 else "one" if counts[f] == 1 else "multiple"
                          for f in ("direction_cue", "action", "relax", "rest"))
        prefix = block[:4] == ["trial_start", "direction_cue", "action", "relax"]
        successor = families[end] if end < len(families) else "end_of_events"
        blocks[(signature, prefix, successor)] += 1

    cue_context, cue_core = Counter(), Counter()
    intervals = {name: Counter() for name in ("start_to_cue", "cue_to_action",
                                             "action_to_relax", "relax_to_rest")}
    pairs = {("trial_start", "direction_cue"): ("start_to_cue", 1, 5 * 1024),
             ("direction_cue", "action"): ("cue_to_action", 384, 3 * 1024),
             ("action", "relax"): ("action_to_relax", 2 * 1024, 4 * 1024),
             ("relax", "rest"): ("relax_to_rest", 1, 3 * 1024)}
    for i, name in enumerate(families):
        if name == "direction_cue":
            cue_context[families[i - 1] if i else "beginning_of_events"] += 1
            cue_core["contiguous_cue_action_relax" if families[i:i + 3] ==
                     ["direction_cue", "action", "relax"] else "incomplete_or_interrupted"] += 1
        if i + 1 < len(families) and (name, families[i + 1]) in pairs:
            interval, lower, upper = pairs[name, families[i + 1]]
            delta = events[i + 1][0] - events[i][0]
            intervals[interval]["within_range" if lower <= delta <= upper else "outside_range"] += 1

    return {
        "events": len(events), "event_family_counts": dict(sorted(totals.items())),
        "nonincreasing_sample_pairs": sum(a[0] >= b[0] for a, b in zip(events, events[1:])),
        "adjacent_family_transitions": [
            {"from": a, "to": b, "count": n} for (a, b), n in sorted(transitions.items())],
        "unambiguously_bounded_runs": runs,
        "unassigned_run_boundary_markers": len(boundaries) - 2 * len(runs),
        "events_outside_unambiguous_runs": dict(sorted(Counter(
            f for i, f in enumerate(families) if i not in covered).items())),
        "trial_start_anchor_block_patterns": [
            {"cue_count": sig[0], "action_count": sig[1], "relax_count": sig[2],
             "rest_count": sig[3], "ordered_core_prefix": prefix,
             "ending_boundary_family": successor, "blocks": count}
            for (sig, prefix, successor), count in sorted(blocks.items())],
        "cue_preceding_families": dict(sorted(cue_context.items())),
        "cue_core_patterns": dict(sorted(cue_core.items())),
        "adjacent_interval_checks": {k: {"within_range": v["within_range"],
                                          "outside_range": v["outside_range"]}
                                     for k, v in intervals.items()},
        "alignment_or_scientific_qualification_established": False,
    }


def execute():
    # Reuse admitted identity/path/hash/write helpers. Never call a model runner.
    frozen = load_script("test_inner_speech_missing_rest").configured_runner()
    import psutil

    root, source, failed = frozen.canonical_local_paths(frozen.BASE, frozen.SOURCE, frozen.LOCAL)
    output = root / CENSUS_NAME
    frozen.require(output.resolve() == output and not output.exists(), "census_already_used_or_redirected")
    frozen.require(not frozen.git("status", "--porcelain", "--untracked-files=no"), "clean_tracked_tree")
    code_paths = frozen.CODE_PATHS + ("scripts/census_inner_speech_events.py",)
    code_hashes = {p: frozen.sha256(REPO / p) for p in code_paths}
    evidence = [root / "inner_speech_test_1_20260922" / name
                for name in ("started.json", "execution_failed.json")]
    evidence += [failed / name for name in ("started.json", "execution_failed.json")]
    evidence += [root / "inner_speech_event_audit_20260929" / name
                 for name in ("started.json", "result.json")]
    before = {p: frozen.sha256(p) for p in evidence}
    frozen.require(shutil.disk_usage(root).free >= 20 * 1024**3, "free_disk_floor")
    output.mkdir()  # Exclusive and consumed even if any later step fails.
    started, process, peak = time.monotonic(), psutil.Process(), 0
    frozen.write_json(output / "started.json", {
        "census_id": CENSUS_ID, "started_unix": time.time(), "max_seconds": MAX_SECONDS,
        "max_rss_bytes": MAX_RSS, "max_output_bytes": MAX_OUTPUT, "workers": 1})
    finished, publication = threading.Event(), threading.Lock()
    terminal, stage, participant = False, "source_identity", None

    def check():
        nonlocal peak
        peak = max(peak, process.memory_info().rss)
        frozen.require(time.monotonic() - started < MAX_SECONDS, "census_deadline")
        frozen.require(peak <= MAX_RSS, "census_memory_cap")
        frozen.require(shutil.disk_usage(root).free >= 20 * 1024**3, "free_disk_floor")

    def fail(code):
        nonlocal terminal
        if not terminal:
            frozen.write_json(output / "census_failed.json", {
                "census_id": CENSUS_ID, "status": "failed_no_retry", "stage": stage,
                "participant": participant, "error_code": code,
                "elapsed_seconds": time.monotonic() - started, "peak_rss_bytes": peak})
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
        frozen.require(frozen.sha256(frozen.ACQUISITION) ==
                       "35caa3bea6e782a67ef982d185eb0781e7938cfe4bccc7b93c89fb86d57b54bb",
                       "acquisition_receipt_changed")
        manifest = json.loads(frozen.MANIFEST.read_text())["files"]
        acquired = json.loads(frozen.ACQUISITION.read_text())["files"]
        frozen.require(len(manifest) == len(acquired) == 10, "complete_source_required")
        rows = []
        for participant, expected, copied in zip(PARTICIPANTS, manifest, acquired):
            relative = f"{participant}/ses-01/eeg/{participant}_ses-01_task-innerspeech_eeg.bdf"
            path = source / relative
            stage = "source_identity"
            frozen.require(expected["path"] == copied["path"] == relative and
                           path.resolve().is_relative_to(source) and
                           path.stat().st_size == expected["size_bytes"], "source_identity")
            frozen.require(frozen.sha256(path, check) == copied["sha256"], "source_hash")
            stage = "status_structure_census"
            reader = BDFReader(path)
            events = reader.iter_status_events(check, participant=participant)
            row = inventory(events)
            del events
            row.update(participant=participant, status_summary=reader.status_summary,
                       source_sha256_verified=True)
            rows.append(row)
            check()
        frozen.require(tuple(row["participant"] for row in rows) == PARTICIPANTS, "complete_roster")
        stage = "immutable_evidence_check"
        frozen.require(all(frozen.sha256(p) == digest for p, digest in before.items()) and
                       all(frozen.sha256(REPO / p) == digest for p, digest in code_hashes.items()),
                       "immutable_evidence_changed")
        result = {"schema_version": 1, "census_id": CENSUS_ID, "status": "census_completed",
                  "dataset": "ds003626", "version": "2.1.2", "session": "ses-01",
                  "code_commit": frozen.git("rev-parse", "HEAD"), "participants": rows,
                  "prior_evidence_and_scientific_code_unchanged": True,
                  "physiological_windows_read": 0, "training_calls": 0, "scoring_calls": 0,
                  "events_changed": 0, "labels_inferred": 0, "parser_calls": 0,
                  "direction_or_answer_identities_exported": 0,
                  "elapsed_seconds": time.monotonic() - started, "peak_rss_bytes": peak}
        encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False).encode()
        frozen.require(len(encoded) + 4096 < MAX_OUTPUT, "census_output_cap")
        with publication:
            check()
            frozen.write_json(output / "result.json", result)
            terminal = True
        print(json.dumps({"status": "census_completed", "participants": len(rows)}))
    except Exception as error:
        if terminal:
            return 0
        safe = {"source_identity", "source_hash", "complete_source_required", "complete_roster",
                "acquisition_receipt_changed", "immutable_evidence_changed", "census_output_cap",
                "census_deadline", "census_memory_cap", "free_disk_floor"}
        with publication:
            fail(str(error) if str(error) in safe else "source_or_census_error")
        print(json.dumps({"status": "failed_no_retry", "stage": stage, "participant": participant}))
        return 1
    finally:
        finished.set()
        watcher.join(timeout=1)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-approved-census", action="store_true")
    args = parser.parse_args()
    if not args.execute_approved_census:
        print(json.dumps({"status": "dry_run_no_data_access", "participants": 10,
                          "max_seconds": MAX_SECONDS, "max_rss_bytes": MAX_RSS,
                          "max_output_bytes": MAX_OUTPUT, "training_and_scoring_allowed": False}))
        return 0
    return execute()


if __name__ == "__main__":
    raise SystemExit(main())
