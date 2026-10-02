"""Approved session-two development test; one prediction freeze and one score."""

import importlib.util
import json
import math
from pathlib import Path


def configured_runner():
    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("temporal_observed_lifecycle",
        repo / "scripts/test_inner_speech_observed.py")
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    runner = wrapper.configured_runner()
    runner.EXPERIMENT_ID = "INNER-SPEECH-TEMPORAL-DEV-S2"
    runner.MODEL_MODULE = "neurodecodekit.experiments.inner_speech_temporal"
    runner.SOURCE_SESSION, runner.MAX_EXCLUSIONS = "ses-02", 20
    runner.EXPERIMENT_KWARGS = {}
    runner.SOURCE = runner.BASE / "ds003626_v2_1_2_ses02_20261002"
    runner.LOCAL = runner.BASE / "inner_speech_temporal_dev_s2_20261002"
    runner.MANIFEST = repo / "registries/inner_speech_session2_source_manifest.v0.json"
    runner.ACQUISITION = repo / "registries/inner_speech_session2_acquisition_result.v0.json"
    runner.PLAN = repo / "registries/inner_speech_temporal_plan.v0.json"
    runner.FREEZE = repo / "registries/inner_speech_temporal_prediction_freeze.v0.json"
    runner.RESULT = repo / "registries/inner_speech_temporal_result.v0.json"
    runner.CODE_PATHS = tuple(p for p in runner.CODE_PATHS if p not in (
        "registries/inner_speech_source_manifest.v0.json",
        "registries/inner_speech_acquisition_result.v0.json")) + (
        "scripts/test_inner_speech_temporal.py", "scripts/acquire_inner_speech.py",
        "scripts/acquire_inner_speech_session2.py",
        "src/neurodecodekit/experiments/inner_speech_temporal.py",
        "registries/inner_speech_session2_source_manifest.v0.json",
        "registries/inner_speech_session2_acquisition_result.v0.json",
        "registries/inner_speech_temporal_plan.v0.json",
    )
    runner.PRIOR_EVIDENCE["inner_speech_observed_1_20261002"] = (
        "started.json", "scoring_consumed.json", "completed_aggregate.json")

    def expected_trials(participant, condition):
        runner.require(participant in {f"sub-{i:02d}" for i in range(1, 11)} and
                       condition in dict(runner.CONDITIONS), "participant_condition_identity")
        return 40 if condition == "pronounced" else 80

    def validate_pairs(pairs):
        expected = {(f"sub-{i:02d}", c) for i in range(1, 11) for c, _ in runner.CONDITIONS}
        runner.require(len(pairs) == 30 and
                       {(p["participant"], p["condition"]) for p in pairs} == expected,
                       "exact_thirty_pair_roster")
        runner.require(all(type(p["trials"]) is int and
                       expected_trials(p["participant"], p["condition"]) - 2 <= p["trials"] <=
                       expected_trials(p["participant"], p["condition"]) for p in pairs),
                       "temporal_pair_trial_count")
        for participant in {p["participant"] for p in pairs}:
            runner.require(sum(p["trials"] for p in pairs if p["participant"] == participant) >= 198,
                           "person_exclusion_cap")
        runner.require(1980 <= sum(p["trials"] for p in pairs) <= 2000, "cohort_exclusion_cap")

    def source_inventory(budget):
        manifest = json.loads(runner.MANIFEST.read_text())
        acquisition = json.loads(runner.ACQUISITION.read_text())
        runner.require(acquisition == json.loads(runner.git("show", "HEAD:" +
                       runner.ACQUISITION.relative_to(repo).as_posix())), "acquisition_not_committed")
        runner.require(acquisition.get("acquisition_id") == "INNER-SPEECH-ACQ-S2" and
                       acquisition.get("status") == "complete" and
                       acquisition.get("payload_bytes") == 6870116352 and
                       acquisition.get("manifest_sha256") == runner.sha256(runner.MANIFEST) and
                       acquisition.get("sample_or_status_values_parsed") is False and
                       acquisition.get("targets_or_performance_outcomes_computed") is False,
                       "session_two_acquisition_identity")
        runner.require(not (runner.SOURCE / "acquisition_failure.json").exists(), "failed_acquisition")
        runner.require(len(acquisition["files"]) == len(manifest["files"]) == 10,
                       "complete_source_required")
        runner.require(runner.SOURCE.resolve() == runner.SOURCE.absolute() and
                       "onedrive" not in str(runner.SOURCE).lower(), "local_source_containment")
        output = []
        for index, (expected, acquired) in enumerate(zip(manifest["files"], acquisition["files"]), 1):
            participant = f"sub-{index:02d}"
            relative = f"{participant}/ses-02/eeg/{participant}_ses-02_task-innerspeech_eeg.bdf"
            path = runner.SOURCE / relative
            runner.require(expected["path"] == acquired["path"] == relative and
                           expected["md5"] == acquired["md5"] and
                           path.resolve().is_relative_to(runner.SOURCE.resolve()) and
                           path.stat().st_size == expected["size_bytes"] == acquired["bytes"],
                           "source_identity")
            runner.require(runner.sha256(path, budget.check) == acquired["sha256"], "source_hash")
            output.append((participant, path, acquired["sha256"]))
        return output

    def participant_features(reader, slots, budget):
        import numpy as np
        from neurodecodekit.datasets.inner_speech import EEG_CHANNELS, EXG_CHANNELS
        from neurodecodekit.experiments.inner_speech import window_features
        from neurodecodekit.experiments.inner_speech_temporal import temporal_window_features
        features = {key: [] for key in ("P", "E_action", "E_cue", "E_late", "E_spectral")}
        kept, picks = [], (*EEG_CHANNELS, *EXG_CHANNELS)
        for index, slot in enumerate(slots):
            if not slot.eligible:
                continue
            budget.check()
            runner.require(slot.relax - 2048 >= slot.action and slot.cue + 384 <= slot.action,
                           "window_crosses_event_boundary")
            action = reader.read_window(slot.relax - 2048, slot.relax, picks)
            spectral = window_features(action[:128], action[128:])
            temporal = temporal_window_features(action[:128], action[128:])
            features["P"].append(np.concatenate((spectral["P"], runner.timing_features(slots, index),
                                                 temporal["P_temporal"])))
            features["E_action"].append(temporal["E"])
            features["E_spectral"].append(spectral["E"])
            cue = reader.read_window(slot.cue, slot.cue + 384, picks)
            features["E_cue"].append(temporal_window_features(cue[:128], cue[128:])["E"])
            features["E_late"].append(temporal_window_features(action[:128, -384:], action[128:, -384:])["E"])
            kept.append(slot)
        return {key: np.stack(rows) for key, rows in features.items()}, kept

    def primary_decision(pairs):
        inner = [p for p in pairs if p["condition"] == "inner"]
        runner.require(len(inner) == 10 and {p["participant"] for p in inner} ==
                       {f"sub-{i:02d}" for i in range(1, 11)}, "primary_population")

        def contrast(gains):
            positive = sum(value > 0 for value in gains)
            return {"mean_gain_nats": sum(gains) / 10, "positive_participants": positive,
                    "one_sided_sign_p": sum(math.comb(10, k) for k in range(positive, 11)) / 1024}

        controls = ("P", "deranged_joint", "joint_shuffled", "uniform", "training_prior", "spectral_joint")
        contrasts = {c: contrast([p["primary_joint_nll_gains"][c] for p in inner]) for c in controls}
        passing = [p["participant"] for p in inner if
                   all(p["primary_joint_nll_gains"][c] > 0 for c in controls)]
        primary_pass = (len(passing) >= 9 and contrasts["P"]["mean_gain_nats"] >= .02 and
                        contrasts["spectral_joint"]["mean_gain_nats"] > 0)
        sensitivity_controls = {"own_shuffled": "cue_eeg_shuffled", "uniform": "uniform",
                                "training_prior": "training_prior"}
        sensitivity_contrasts = {c: contrast([p["eeg_sensitivity_nll_gains"]["cue_eeg"][key]
                                             for p in inner]) for c, key in sensitivity_controls.items()}
        sensitivity_passing = [p["participant"] for p in inner if
            all(p["eeg_sensitivity_nll_gains"]["cue_eeg"][key] > 0
                for key in sensitivity_controls.values())]
        sensitivity_pass = (len(sensitivity_passing) >= 9 and
                            sensitivity_contrasts["uniform"]["mean_gain_nats"] >= .02)
        return {"primary_pass": primary_pass, "same_people_passing_every_control": passing,
            "required_same_people": 9, "minimum_mean_gain_nats": .02, "contrasts": contrasts,
            "cue_sensitivity": {"pass": sensitivity_pass, "same_people_passing_every_control": sensitivity_passing,
                                "contrasts": sensitivity_contrasts},
            "progression_pass": primary_pass and sensitivity_pass,
            "progression_only_proposes_untouched_confirmation": True,
            "lane": "development", "ties_count_as_nonpositive": True,
            "secondary_results_cannot_rescue_primary": True}

    runner.expected_trials, runner.validate_pairs = expected_trials, validate_pairs
    runner.source_inventory, runner.participant_features = source_inventory, participant_features
    runner.primary_decision = primary_decision
    return runner


if __name__ == "__main__":
    raise SystemExit(configured_runner().main())
