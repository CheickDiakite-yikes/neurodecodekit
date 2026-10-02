"""Approved observed-anchor successor; one decoder gate, one frozen score.

Reuse the existing local identity, budget, failure, freeze and scoring lifecycle.
Default is dry-run. No prior attempt can be resumed by this wrapper.
"""

import importlib.util
import json
from pathlib import Path
import time


def configured_runner():
    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("inner_speech_observed_runner",
                                                repo / "scripts/test_inner_speech.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.EXPERIMENT_ID = "INNER-SPEECH-OBSERVED-1"
    runner.LOCAL = runner.BASE / "inner_speech_observed_1_20261002"
    runner.PLAN = repo / "registries/inner_speech_observed_plan.v0.json"
    runner.FREEZE = repo / "registries/inner_speech_observed_prediction_freeze.v0.json"
    runner.RESULT = repo / "registries/inner_speech_observed_result.v0.json"
    runner.CODE_PATHS += (
        "scripts/test_inner_speech_observed.py",
        "src/neurodecodekit/datasets/inner_speech_observed.py",
        "src/neurodecodekit/datasets/inner_speech_reference_status.py",
        "registries/inner_speech_observed_plan.v0.json",
    )
    base_budget, base_publish = runner.Budget, runner.publish_result

    class ObservedBudget(base_budget):
        gate_active = False

        def check(self):
            super().check()
            if self.gate_active:
                runner.require(time.time() - self.started < 120, "decoder_gate_deadline")
                runner.require(self.peak_rss <= 256 * 1024**2, "decoder_gate_memory_cap")
                total = sum(p.stat().st_size for p in runner.LOCAL.rglob("*") if p.is_file())
                runner.require(total <= 1024**2 - 4096, "decoder_gate_output_cap")

    def prior_evidence():
        names = {
            "inner_speech_test_1_20260922": ("started.json", "execution_failed.json"),
            "inner_speech_test_1_mr1_20260929": ("started.json", "execution_failed.json"),
            "inner_speech_event_audit_20260929": ("started.json", "result.json"),
            "inner_speech_event_census_20260929": ("started.json", "result.json"),
        }
        return {f"{root}/{name}": runner.sha256(runner.BASE / root / name)
                for root, files in names.items() for name in files}

    def validate_pairs(pairs):
        expected = {(f"sub-{i:02d}", condition) for i in range(1, 11)
                    for condition, _ in runner.CONDITIONS}
        runner.require(len(pairs) == 30 and
                       {(p["participant"], p["condition"]) for p in pairs} == expected,
                       "exact_thirty_pair_roster")
        runner.require(all(type(p["trials"]) is int and
                       runner.expected_trials(p["participant"], p["condition"]) - 7 <= p["trials"] <=
                       runner.expected_trials(p["participant"], p["condition"]) for p in pairs),
                       "observed_pair_trial_count")
        runner.require(1993 <= sum(p["trials"] for p in pairs) <= 2000, "cohort_exclusion_cap")

    def timing_features(slots, index):
        import numpy as np
        slot = slots[index]
        runner.require(slot.eligible and slot.original_index == index, "eligible_original_slot")
        start_ok, rest_ok = slot.start is not None, slot.rest is not None
        gap_ok = start_ok and index > 0 and slots[index - 1].rest is not None
        return np.asarray([
            slot.start / 1024 if start_ok else 0.0, slot.run_ordinal, index % 40,
            (slot.cue - slot.start) / 1024 if start_ok else 0.0,
            (slot.action - slot.cue) / 1024, (slot.relax - slot.action) / 1024,
            (slot.rest - slot.relax) / 1024 if rest_ok else 0.0,
            (slot.start - slots[index - 1].rest) / 1024 if gap_ok else 0.0,
            float(rest_ok), float(gap_ok), float(start_ok),
        ], dtype=np.float64)

    def qualify_all(inventory, budget):
        import numpy as np
        from neurodecodekit.datasets.inner_speech import BDFReader
        from neurodecodekit.datasets.inner_speech_observed import parse_observed_slots
        from neurodecodekit.datasets.inner_speech_reference_status import reference_status_events
        from neurodecodekit.experiments.inner_speech import preflight_condition
        runner.require(tuple(p for p, _, _ in inventory) ==
                       tuple(f"sub-{i:02d}" for i in range(1, 11)), "complete_source_roster")
        qualified, summaries, agreements = [], [], []
        # No word values or sample positions are ever written into gate metadata.
        core_codes = {31, 32, 33, 34, 44, 45}
        protocol_codes = {11, 12, 13, 14, 15, 16, 21, 22, 23, 51}
        for person_index, (participant, path, digest) in enumerate(inventory):
            budget.participant, budget.stage = participant, "decoder_agreement"
            reader = BDFReader(path)
            events = reader.iter_status_events(budget.check, participant=participant)
            reference = reference_status_events(reader, participant=participant, check=budget.check)
            core_equal = ([e for e in events if e[1] in core_codes] ==
                          [e for e in reference if e[1] in core_codes])
            protocol_equal = ([e for e in events if e[1] in protocol_codes] ==
                              [e for e in reference if e[1] in protocol_codes])
            # Agreement on every event also protects nuisance timing/missingness.
            all_equal = events == reference
            agreements.append({"participant": participant, "core_agreement": core_equal,
                               "protocol_agreement": protocol_equal, "full_event_agreement": all_equal,
                               "frozen_events": len(events), "reference_events": len(reference)})
            if not (core_equal and protocol_equal and all_equal):
                runner.write_json(runner.LOCAL / "decoder_gate.json", {
                    "status": "refused", "participants_checked": agreements,
                    "physiological_windows_read": 0, "training_calls": 0, "scoring_calls": 0})
                runner.require(False, "decoder_disagreement")
            del reference
            budget.stage = "observed_slot_qualification"
            summary = {"participant": participant}
            slots = parse_observed_slots(events, participant=participant, summary=summary)
            del events
            for condition_index, (condition, code) in enumerate(runner.CONDITIONS):
                nominal = np.asarray([s.original_index for s in slots if s.condition == code])
                kept = [s for s in slots if s.condition == code and s.eligible]
                runner.require(len(nominal) == runner.expected_trials(participant, condition),
                               "nominal_condition_trial_count")
                preflight_condition(np.asarray([s.label for s in kept], dtype=np.int64),
                    np.asarray([s.original_index for s in kept], dtype=np.int64),
                    nominal_trial_indices=nominal, seed=20260922 + 16 * person_index + 4 * condition_index)
            summaries.append(summary)
            qualified.append((participant, reader, slots, digest))
            budget.check()
        runner.require(len(qualified) == 10 and sum(s["slots"] for s in summaries) == 2000,
                       "complete_slot_roster")
        excluded = sum(s["excluded"] for s in summaries)
        runner.require(excluded <= 7, "cohort_exclusion_cap")
        runner.write_json(runner.LOCAL / "decoder_gate.json", {
            "status": "passed", "participants_checked": agreements,
            "physiological_windows_read": 0, "training_calls": 0, "scoring_calls": 0})
        runner.write_json(runner.LOCAL / "qualification.json", {
            "participants": summaries, "nominal_trials": 2000, "trials": 2000 - excluded,
            "trials_excluded": excluded, "labels_imputed": 0,
            "decoder_gate_sha256": runner.sha256(runner.LOCAL / "decoder_gate.json")})
        budget.check()
        return qualified

    def participant_features(reader, slots, budget):
        import numpy as np
        from neurodecodekit.datasets.inner_speech import EEG_CHANNELS, EXG_CHANNELS
        from neurodecodekit.experiments.inner_speech import window_features
        features = {name: [] for name in ("P", "E_action", "E_cue", "E_late")}
        kept, picks = [], (*EEG_CHANNELS, *EXG_CHANNELS)
        for index, slot in enumerate(slots):
            if not slot.eligible:
                continue
            budget.check()
            runner.require(slot.relax - 2048 >= slot.action and slot.cue + 384 <= slot.action,
                           "window_crosses_event_boundary")
            action = reader.read_window(slot.relax - 2048, slot.relax, picks)
            primary = window_features(action[:128], action[128:])
            features["P"].append(np.concatenate((primary["P"], timing_features(slots, index))))
            features["E_action"].append(primary["E"])
            cue = reader.read_window(slot.cue, slot.cue + 384, picks)
            features["E_cue"].append(window_features(cue[:128], cue[128:])["E"])
            features["E_late"].append(window_features(action[:128, -384:], action[128:, -384:])["E"])
            kept.append(slot)
        return {name: np.stack(rows) for name, rows in features.items()}, kept

    def predict(budget, started):
        import numpy as np
        from neurodecodekit.experiments.inner_speech import run_condition
        budget.gate_active, budget.stage = True, "source_verification"
        before = prior_evidence()
        inventory = runner.source_inventory(budget)
        qualified = runner.qualify_all(inventory, budget)
        runner.require(before == prior_evidence(), "prior_evidence_changed")
        budget.check()
        budget.gate_active = False
        print("All ten passed decoder/slot/split qualification; starting fixed predictions.", flush=True)
        pairs = []
        for person_index, (participant, reader, slots, digest) in enumerate(qualified):
            budget.participant, budget.stage = participant, "feature_extraction"
            features, kept = runner.participant_features(reader, slots, budget)
            budget.stage = "nested_predictions"
            for condition_index, (condition, code) in enumerate(runner.CONDITIONS):
                rows = np.asarray([i for i, s in enumerate(kept) if s.condition == code])
                labels = np.asarray([kept[i].label for i in rows], dtype=np.int64)
                original = np.asarray([kept[i].original_index for i in rows])
                nominal = np.asarray([s.original_index for s in slots if s.condition == code])
                bundle = run_condition({k: v[rows] for k, v in features.items()}, labels, original,
                    seed=20260922 + 16 * person_index + 4 * condition_index, check=budget.check,
                    observed_anchors=True, nominal_trial_indices=nominal)
                name = f"{participant}_{condition}"
                predictions, targets, diagnostics = (runner.LOCAL / (name + suffix) for suffix in (
                    "_predictions.npz", "_targets.npy", "_diagnostics.json"))
                with predictions.open("xb") as stream:
                    np.savez_compressed(stream, **bundle["predictions"],
                        **{"raw_" + key: value for key, value in bundle["uncalibrated"].items()})
                with targets.open("xb") as stream:
                    np.save(stream, labels, allow_pickle=False)
                runner.write_json(diagnostics, bundle["fit_diagnostics"])
                pairs.append({"participant": participant, "condition": condition, "trials": len(labels),
                    **{key: path.name for key, path in zip(("predictions", "targets", "diagnostics"),
                                                          (predictions, targets, diagnostics))},
                    **{key + "_sha256": runner.sha256(path) for key, path in zip(
                        ("predictions", "targets", "diagnostics"), (predictions, targets, diagnostics))}})
                budget.storage()
            runner.require(runner.sha256(reader.path, budget.check) == digest, "source_changed_during_features")
            del features
            print(f"Completed participant {person_index + 1}/10; no held-out metrics computed.", flush=True)
        validate_pairs(pairs)
        runner.require(before == prior_evidence(), "prior_evidence_changed")
        runner.require(not (runner.LOCAL / "execution_failed.json").exists(), "failed_attempt")
        runner.write_json(runner.FREEZE, {"experiment_id": runner.EXPERIMENT_ID,
            "code_commit": started["code_commit"], "fingerprints": started["fingerprints"], "pairs": pairs,
            "qualification_sha256": runner.sha256(runner.LOCAL / "qualification.json"),
            "elapsed_seconds": time.time() - budget.started, "peak_rss_bytes": budget.peak_rss,
            "prior_evidence_unchanged": True, "held_out_metrics_computed": False, "scoring_invocations": 0})
        budget.storage()
        print("All predictions frozen. Commit/push ONLY the hash freeze before one score.", flush=True)

    def publish_result(output, budget):
        qualification = output["qualification"]
        runner.require(qualification["decoder_gate_sha256"] ==
                       runner.sha256(runner.LOCAL / "decoder_gate.json"), "decoder_gate_changed")
        output["trials_excluded"] = qualification["trials_excluded"]
        output["nominal_trials"] = qualification["nominal_trials"]
        output["eligible_trials"] = qualification["trials"]
        runner.require(sum(p["metrics"]["P"]["n_trials"] for p in output["pairs"]) ==
                       qualification["trials"], "scored_qualification_count")
        counts = {(p["participant"], condition): p["condition_counts_eligible"][str(code)]
                  for p in qualification["participants"] for condition, code in runner.CONDITIONS}
        runner.require(all(p["metrics"]["P"]["n_trials"] == counts[p["participant"], p["condition"]]
                           for p in output["pairs"]), "scored_pair_qualification_count")
        output["decoder_gate"] = json.loads((runner.LOCAL / "decoder_gate.json").read_text())
        base_publish(output, budget)

    runner.Budget, runner.predict = ObservedBudget, predict
    runner.validate_pairs, runner.qualify_all = validate_pairs, qualify_all
    runner.timing_features, runner.participant_features = timing_features, participant_features
    runner.publish_result = publish_result
    return runner


if __name__ == "__main__":
    raise SystemExit(configured_runner().main())
