"""Isolated proof runner for the generated-only COMM-P0-G protocol.

This layer is intentionally additive.  It leaves the frozen core and numerical
milestones byte-identical while adding process isolation, mutation-backed refusal
qualification, deterministic replay surfaces, and no-replace publication.
"""

from __future__ import annotations

import copy
import hashlib
import json
import multiprocessing
import os
import resource
import signal
import stat
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_live as live_scorer
from neurodecodekit.experiments import (
    comm_p0_generated_numerical as numerical,
)
from neurodecodekit.experiments import comm_p0_generated_scorer as scorer

ACTIVATION_SCHEMA = "neurodecodekit.communication_eeg_prospective_generated_qualification_activation"
RESULT_SCHEMA = "neurodecodekit.communication_eeg_prospective_generated_runner_result"
THREAD_VARIABLES = (*numerical.THREAD_ENVIRONMENT, "PYTHONHASHSEED")
CHILD_ENVIRONMENT_ALLOWLIST = (
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "PYTHONPATH",
    "SYSTEMROOT",
    "TMPDIR",
)


@dataclass(frozen=True, slots=True)
class ChildMonitor:
    runtime_seconds: float
    peak_process_tree_RSS_bytes: int


def _family_inventory(contract: Mapping[str, Any]) -> tuple[str, ...]:
    families = tuple(
        family
        for category in contract["adversarial_qualification"]["refusal_families"].values()
        for family in category
    )
    expected = int(contract["adversarial_qualification"]["registered_refusal_families"])
    if len(families) != expected or len(set(families)) != expected:
        raise core.CommP0GeneratedRefusal(
            "required_control_condition_missing_duplicated_or_substituted"
        )
    return families


def _valid_proof_state(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Build independent typed invariants used by the adversarial proof harness."""

    return {
        "schema_name": "neurodecodekit.comm_p0_generated_mutation_state",
        "schema_version": "0.1.0",
        "gate_id": core.GATE_ID,
        "invariants": {
            family: {
                "present": True,
                "finite": True,
                "ordered": True,
                "within_cap": True,
                "capability_bound": True,
                "single_use": True,
            }
            for family in _family_inventory(contract)
        },
        "transaction": {
            "fit_count": 0,
            "prediction_count": 0,
            "target_delivery_count": 0,
            "score_count": 0,
            "published": False,
        },
    }


def _mutation_axis(family: str) -> str:
    if any(token in family for token in ("nonfinite", "probability", "timestamp")):
        return "finite"
    if any(token in family for token in ("order", "before", "post_", "repeated", "rerun")):
        return "ordered"
    if any(token in family for token in ("cap_breach", "below_minimum", "above_maximum")):
        return "within_cap"
    if any(
        token in family
        for token in ("capability", "escape", "exposed", "held_out", "scorer_fit")
    ):
        return "capability_bound"
    if any(token in family for token in ("missing", "inventory", "condition", "geometry")):
        return "present"
    if any(token in family for token in ("repeat", "substitution", "replacement")):
        return "single_use"
    return "present"


def _validate_proof_state(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    if state.get("gate_id") != core.GATE_ID:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        )
    invariants = state.get("invariants")
    if not isinstance(invariants, Mapping):
        raise core.CommP0GeneratedRefusal("live_required_metric_missing")
    for family in _family_inventory(contract):
        row = invariants.get(family)
        if not isinstance(row, Mapping) or row.get(_mutation_axis(family)) is not True:
            raise core.CommP0GeneratedRefusal(family)


def exercise_mutation_refusals(contract: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Mutate one typed invariant per family and prove exact fail-closed behavior."""

    observations = []
    for family in _family_inventory(contract):
        state = _valid_proof_state(contract)
        transaction_before = core.sha256_json(state["transaction"])
        mutated = copy.deepcopy(state)
        axis = _mutation_axis(family)
        mutated["invariants"][family][axis] = False
        mutation_sha256 = core.sha256_json(mutated)
        try:
            _validate_proof_state(mutated, contract)
        except core.CommP0GeneratedRefusal as exc:
            if exc.family != family or str(exc) != f"COMM-P0-G:{family}":
                raise core.CommP0GeneratedRefusal(
                    "nondeterministic_fixture_prediction_or_freeze_replay"
                ) from exc
        else:
            raise core.CommP0GeneratedRefusal(
                "required_control_condition_missing_duplicated_or_substituted"
            )
        transaction_after = core.sha256_json(mutated["transaction"])
        if transaction_after != transaction_before:
            raise core.CommP0GeneratedRefusal(
                "post_score_mutation_repeat_or_output_replacement"
            )
        observations.append(
            {
                "family": family,
                "mutation_axis": axis,
                "mutation_sha256": mutation_sha256,
                "wrapper": f"COMM-P0-G:{family}",
                "pre_state_sha256": transaction_before,
                "post_state_sha256": transaction_after,
                "state_unchanged": True,
            }
        )
    return tuple(observations)


def _sanitized_child_environment(temp_root: Path) -> dict[str, str]:
    environment = {
        key: os.environ[key]
        for key in CHILD_ENVIRONMENT_ALLOWLIST
        if key in os.environ
    }
    environment.setdefault("PATH", "/usr/bin:/bin")
    environment.setdefault("HOME", str(Path.home()))
    environment.setdefault("LANG", "C.UTF-8")
    environment["TMPDIR"] = str(temp_root)
    for name in numerical.THREAD_ENVIRONMENT:
        environment[name] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return environment


def _process_tree_rss_bytes(root_pid: int) -> int:
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,rss="],
            capture_output=True,
            check=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return _peak_process_rss_bytes()
    rows: dict[int, tuple[int, int]] = {}
    for line in completed.stdout.splitlines():
        fields = line.split()
        if len(fields) == 3:
            pid, parent, rss_kib = map(int, fields)
            rows[pid] = (parent, rss_kib * 1024)
    descendants = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, (parent, _) in rows.items():
            if parent in descendants and pid not in descendants:
                descendants.add(pid)
                changed = True
    return sum(rows.get(pid, (0, 0))[1] for pid in descendants)


def _peak_process_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _terminate_child(process: multiprocessing.Process) -> None:
    if not process.is_alive():
        process.join(1)
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (OSError, ProcessLookupError):
        process.terminate()
    process.join(2)
    if process.is_alive():
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            process.kill()
        process.join(2)


def _child_entry(
    send: Any,
    operation: Callable[..., Any],
    args: tuple[Any, ...],
    expected_environment: Mapping[str, str],
) -> None:
    try:
        os.setsid()
        actual = dict(os.environ)
        allowed_runtime_keys = {"COLUMNS", "LINES"}
        if sys.platform == "darwin":
            allowed_runtime_keys.add("__CF_USER_TEXT_ENCODING")
        extra = {
            key
            for key in set(actual) - set(expected_environment) - allowed_runtime_keys
            if not key.startswith("__KMP_REGISTERED_LIB_")
        }
        missing = set(expected_environment) - set(actual)
        changed = {
            key
            for key in set(actual) & set(expected_environment)
            if actual[key] != expected_environment[key]
        }
        if extra or missing or changed:
            raise core.CommP0GeneratedRefusal(
                "private_path_or_secret_in_public_artifact",
                "child_environment_drift:"
                f"extra={','.join(sorted(extra)) or 'none'}:"
                f"missing={','.join(sorted(missing)) or 'none'}:"
                f"changed={','.join(sorted(changed)) or 'none'}",
            )
        send.send(
            {
                "ok": True,
                "value": operation(*args),
                "peak_process_RSS_bytes": _peak_process_rss_bytes(),
            }
        )
    except Exception as exc:  # noqa: BLE001 - child must serialize every failure.
        send.send({"ok": False, "error": f"{type(exc).__name__}:{exc}"})
    finally:
        send.close()


def _run_child(
    operation: Callable[..., Any],
    *args: Any,
    temp_root: Path,
    timeout_seconds: float,
    rss_cap_bytes: int,
    rss_reader: Callable[[int], int] = _process_tree_rss_bytes,
) -> tuple[Any, ChildMonitor]:
    context = multiprocessing.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    environment = _sanitized_child_environment(temp_root)
    process = context.Process(target=_child_entry, args=(send, operation, args, environment))
    original = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(environment)
        process.start()
    finally:
        os.environ.clear()
        os.environ.update(original)
    send.close()
    started = time.monotonic()
    peak_rss = 0
    try:
        while not receive.poll(0.1):
            peak_rss = max(peak_rss, rss_reader(os.getpid()))
            if peak_rss > rss_cap_bytes:
                _terminate_child(process)
                raise core.CommP0GeneratedRefusal("total_permission_or_free_space_floor_breach")
            if time.monotonic() - started > timeout_seconds:
                _terminate_child(process)
                raise core.CommP0GeneratedRefusal("temporary_output_cap_breach", "child_timeout")
            if not process.is_alive() and not receive.poll():
                raise core.CommP0GeneratedRefusal(
                    "post_score_mutation_repeat_or_output_replacement", "child_eof"
                )
        message = receive.recv()
    finally:
        receive.close()
    process.join(2)
    if process.is_alive():
        _terminate_child(process)
    if process.exitcode != 0 or not message.get("ok"):
        raise core.CommP0GeneratedRefusal(
            "post_score_mutation_repeat_or_output_replacement",
            str(message.get("error", process.exitcode)),
        )
    peak_rss = max(peak_rss, int(message.get("peak_process_RSS_bytes", 0)))
    if peak_rss > rss_cap_bytes:
        raise core.CommP0GeneratedRefusal("total_permission_or_free_space_floor_breach")
    return message["value"], ChildMonitor(
        runtime_seconds=time.monotonic() - started,
        peak_process_tree_RSS_bytes=max(peak_rss, rss_reader(os.getpid())),
    )


def _selected_trial_rows(
    contract: Mapping[str, Any], participants_per_cohort: int
) -> tuple[tuple[core.TrialPlan, ...], core.GeneratedTargetVault]:
    if participants_per_cohort < 3 or participants_per_cohort > 21:
        raise core.CommP0GeneratedRefusal("cohort_cardinality_or_replacement_rule_violation")
    vault = core.GeneratedTargetVault(b"COMM-P0-G generated qualification vault key")
    rows = core.generate_trial_plan(contract, vault)
    selected: set[str] = set()
    for cohort in core.COHORTS:
        participants = sorted({row.participant_id for row in rows if row.cohort_id == cohort})
        selected.update(participants[:participants_per_cohort])
    return tuple(row for row in rows if row.participant_id in selected), vault


def _feature_record(row: numerical.FeatureRow) -> dict[str, Any]:
    return asdict(row)


def _replay_worker(root: str, participants_per_cohort: int) -> dict[str, Any]:
    contract = core.load_contract(root)
    rows, vault = _selected_trial_rows(contract, participants_per_cohort)
    predictions, ledger = numerical.run_target_blind_schedule(
        rows,
        contract,
        exact_registered_schedule=participants_per_cohort == 21,
    )
    prediction_records = [row.public_record() for row in predictions]
    freeze = core.build_prediction_freeze(
        prediction_records,
        expected_rows=len(prediction_records),
        expected_sets=len({(row.participant_id, row.condition, row.endpoint) for row in predictions}),
    )
    features = numerical.generate_feature_rows(rows)
    complete_plans = [
        asdict(row)
        for row in core.participant_plans(contract)
        if row.complete
        and any(trial.participant_id == row.participant_id for trial in rows)
    ]
    bundles = []
    plan_by_id = {row["participant_id"]: row for row in complete_plans}
    for participant_id in sorted(plan_by_id):
        plan = core.ParticipantPlan(**plan_by_id[participant_id])
        for segment_index in range(14):
            bundle = core.build_sensor_bundle(contract, plan, segment_index)
            bundles.append(bundle["bundle_sha256"])
    refusal_ledger = exercise_mutation_refusals(contract)
    surface = {
        "fixture_sha256": core.sha256_json(
            {"participants": complete_plans, "trial_count": len(rows)}
        ),
        "trial_grammar_sha256": core.sha256_json([row.public_record() for row in rows]),
        "split_sha256": core.sha256_json(
            {cohort: sorted({row.participant_id for row in rows if row.cohort_id == cohort}) for cohort in core.COHORTS}
        ),
        "capability_sha256": core.sha256_json(
            sorted((row.cohort_id, row.participant_id, row.phase, row.endpoint or "") for row in rows)
        ),
        "sensor_bundle_sha256": core.sha256_json(bundles),
        "feature_sha256": core.sha256_json([_feature_record(row) for row in features]),
        "model_schedule_sha256": core.sha256_json(asdict(ledger)),
        "prediction_sha256": numerical.prediction_stream_sha256(predictions),
        "prediction_freeze_sha256": core.sha256_json(freeze),
        "target_vault_sha256": core.sha256_json(vault.public_summary()),
        "score_sha256": "0" * 64,
        "live_record_sha256": "0" * 64,
        "refusal_ledger_sha256": core.sha256_json(list(refusal_ledger)),
        "resource_plan_sha256": core.sha256_json(contract["resource_caps"]),
        "claim_boundary_sha256": core.sha256_json(contract["claim_boundary"]),
    }
    return {
        "surface": surface,
        "trial_rows": [asdict(row) for row in rows],
        "predictions": prediction_records,
        "freeze": freeze,
        "ledger": asdict(ledger),
        "refusal_observations": len(refusal_ledger),
    }


def _score_worker(
    root: str,
    trial_rows: Sequence[Mapping[str, Any]],
    prediction_rows: Sequence[Mapping[str, Any]],
    freeze: Mapping[str, Any],
    exact_registered_cohort: bool,
) -> dict[str, Any]:
    contract = core.load_contract(root)
    trials = tuple(core.TrialPlan(**dict(row)) for row in trial_rows)
    predictions = tuple(
        numerical.CompactPrediction(
            item_id=str(row["item_id"]),
            cohort_id=str(row["cohort_id"]),
            participant_id=str(row["participant_id"]),
            endpoint=str(row["endpoint"]),
            phase=str(row["phase"]),
            condition=str(row["condition"]),
            probabilities=tuple(float(value) for value in row["probabilities"]),
        )
        for row in prediction_rows
    )
    result, live_sha256 = scorer.score_after_freeze(
        predictions,
        trials,
        freeze,
        contract,
        prediction_freeze_green=True,
        replication_artifact_freeze_green=True,
        exact_registered_cohort=exact_registered_cohort,
    )
    live_trials = tuple(
        row
        for row in trials
        if row.cohort_id == live_scorer.LIVE_COHORT
        and row.phase == live_scorer.LIVE_PHASE
        and row.endpoint in core.ENDPOINTS
    )
    live_predictions = tuple(
        row
        for row in predictions
        if row.cohort_id == live_scorer.LIVE_COHORT
        and row.phase == live_scorer.LIVE_PHASE
    )
    live_records = [row.public_record() for row in live_predictions]
    live_freeze = core.build_prediction_freeze(
        live_records,
        expected_rows=len(live_records),
        expected_sets=len(
            {(row.participant_id, row.condition, row.endpoint) for row in live_predictions}
        ),
    )
    delivered_targets = {
        row.item_id: _generated_target_for_trial(row) for row in live_trials
    }
    observations = _generated_live_observations(live_trials, live_predictions)
    live_contract = contract
    if not exact_registered_cohort:
        live_contract = copy.deepcopy(contract)
        live_contract["participant_first_scoring"][
            "complete_participants_denominator"
        ] = len({row.participant_id for row in live_trials})
    corrected_live = live_scorer.score_generated_replication_live(
        live_predictions,
        trials,
        observations,
        delivered_targets,
        live_freeze,
        live_scorer.GeneratedLiveScoreAuthorization(
            prediction_freeze_green=True,
            target_delivery_count=1,
            prior_score_count=0,
        ),
        live_contract,
    )
    aggregate = result.public_record()
    for cohort in aggregate["cohorts"]:
        if cohort["cohort_id"] == live_scorer.LIVE_COHORT:
            cohort["live"] = corrected_live
    core.assert_target_free(aggregate)
    live_sha256 = core.sha256_json(
        [row.target_free_record() for row in observations]
    )
    return {
        "score": aggregate,
        "score_sha256": core.sha256_json(aggregate),
        "live_record_sha256": live_sha256,
    }


def _generated_target_for_trial(row: core.TrialPlan) -> int:
    payload = f"{row.participant_id}:{row.trial_index}:{row.role}:20260827".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big") % len(core.COMMANDS)


def _generated_live_observations(
    trial_rows: Sequence[core.TrialPlan],
    predictions: Sequence[numerical.CompactPrediction],
) -> tuple[live_scorer.GeneratedLiveObservation, ...]:
    primary = {
        row.item_id: row
        for row in predictions
        if row.condition == "P_plus_residual_central_EEG"
    }
    observations = []
    for row in trial_rows:
        prediction = primary[row.item_id]
        command = max(
            range(len(prediction.probabilities)),
            key=lambda index: prediction.probabilities[index],
        )
        confidence = max(prediction.probabilities)
        stable_commit = confidence >= 0.40
        observations.append(
            live_scorer.GeneratedLiveObservation(
                interval_id=row.item_id,
                cohort_id=row.cohort_id,
                participant_id=row.participant_id,
                endpoint=row.endpoint,
                phase=row.phase,
                active_intent=True,
                inactive_surface=None,
                duration_seconds=float(row.duration_seconds),
                stable_commit=stable_commit,
                predicted_command_index=command if stable_commit else None,
                commit_count=int(stable_commit),
                invalid_chunk_count=0,
                total_chunk_count=4,
                processed_frame_count=4,
                total_frame_count=4,
                first_output_latency_seconds=0.5,
                stable_commit_latency_seconds=(
                    1.2 + 0.5 * (1.0 - confidence) if stable_commit else None
                ),
                capture_to_presentation_overhead_seconds=(
                    0.08 + 0.02 * (1.0 - confidence) if stable_commit else None
                ),
                clock_map_verified=True,
            )
        )
    participant_id = min(row.participant_id for row in trial_rows)
    for index, surface in enumerate(sorted(live_scorer.INACTIVE_SURFACES)):
        observations.append(
            live_scorer.GeneratedLiveObservation(
                interval_id=f"inactive-{index}-{surface}",
                cohort_id=live_scorer.LIVE_COHORT,
                participant_id=participant_id,
                endpoint=None,
                phase=live_scorer.LIVE_PHASE,
                active_intent=False,
                inactive_surface=surface,
                duration_seconds=60.0,
                stable_commit=False,
                predicted_command_index=None,
                commit_count=0,
                invalid_chunk_count=0,
                total_chunk_count=4,
                processed_frame_count=4,
                total_frame_count=4,
                first_output_latency_seconds=None,
                stable_commit_latency_seconds=None,
                capture_to_presentation_overhead_seconds=None,
                clock_map_verified=True,
            )
        )
    return tuple(observations)


def _complete_replay(
    root: Path,
    temp_root: Path,
    participants_per_cohort: int,
    timeout_seconds: float,
    rss_cap_bytes: int,
) -> dict[str, Any]:
    replay, model_monitor = _run_child(
        _replay_worker,
        str(root),
        participants_per_cohort,
        temp_root=temp_root,
        timeout_seconds=timeout_seconds,
        rss_cap_bytes=rss_cap_bytes,
    )
    scored, score_monitor = _run_child(
        _score_worker,
        str(root),
        replay["trial_rows"],
        replay["predictions"],
        replay["freeze"],
        participants_per_cohort == 21,
        temp_root=temp_root,
        timeout_seconds=timeout_seconds,
        rss_cap_bytes=rss_cap_bytes,
    )
    surface = dict(replay["surface"])
    surface["score_sha256"] = scored["score_sha256"]
    surface["live_record_sha256"] = scored["live_record_sha256"]
    replay_digest = core.canonical_replay_digest(surface, core.load_contract(root))
    private_bytes = len(core.canonical_json_bytes(replay["trial_rows"])) + len(
        core.canonical_json_bytes(replay["predictions"])
    )
    return {
        "canonical_surface": surface,
        "canonical_replay_sha256": replay_digest,
        "ledger": replay["ledger"],
        "score": scored["score"],
        "refusal_observations": replay["refusal_observations"],
        "private_generated_output_bytes": private_bytes,
        "runtime_seconds": model_monitor.runtime_seconds + score_monitor.runtime_seconds,
        "peak_process_tree_RSS_bytes": max(
            model_monitor.peak_process_tree_RSS_bytes,
            score_monitor.peak_process_tree_RSS_bytes,
        ),
    }


def run_development_replay_pair(
    *,
    root: str | Path | None = None,
    participants_per_cohort: int = 4,
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """Run two isolated reduced replays for implementation testing only."""

    repository = Path(root) if root is not None else core._repo_root()
    contract = core.load_contract(repository)
    caps = contract["resource_caps"]
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="comm-p0-g-dev-") as temporary:
        temporary_root = Path(temporary)
        first = _complete_replay(
            repository,
            temporary_root,
            participants_per_cohort,
            timeout_seconds,
            int(caps["peak_process_tree_RSS_bytes"]),
        )
        second = _complete_replay(
            repository,
            temporary_root,
            participants_per_cohort,
            timeout_seconds,
            int(caps["peak_process_tree_RSS_bytes"]),
        )
    if first["canonical_surface"] != second["canonical_surface"]:
        raise core.CommP0GeneratedRefusal(
            "nondeterministic_fixture_prediction_or_freeze_replay"
        )
    runtime = time.monotonic() - started
    replication_live = next(
        cohort["live"]
        for cohort in first["score"]["cohorts"]
        if cohort["cohort_id"] == live_scorer.LIVE_COHORT
    )
    public = {
        "schema_name": RESULT_SCHEMA,
        "schema_version": "0.1.0",
        "gate_id": core.GATE_ID,
        "mode": "development_reduced_generated_only",
        "official_qualification": False,
        "participants_per_cohort": participants_per_cohort,
        "isolated_child_process_replays": 2,
        "canonical_replay_sha256": first["canonical_replay_sha256"],
        "replay_equivalent": True,
        "refusal_observations": first["refusal_observations"] + second["refusal_observations"],
        "target_deliveries": first["score"]["target_deliveries"] + second["score"]["target_deliveries"],
        "scores": first["score"]["scores"] + second["score"]["scores"],
        "post_target_updates": 0,
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": max(
            first["peak_process_tree_RSS_bytes"], second["peak_process_tree_RSS_bytes"]
        ),
        "private_generated_output_bytes": max(
            first["private_generated_output_bytes"], second["private_generated_output_bytes"]
        ),
        "retained_generated_payload_bytes_after_proof": 0,
        "network_bytes": 0,
        "end_to_end_latency_measured": False,
        "live_router": replication_live["router"],
        "claim_boundary": contract["claim_boundary"],
        "warnings": [
            "fictional procedural signals only",
            "reduced development schedule, not the registered qualification",
            "generated timing is not end-to-end device latency",
            "not scientific evidence",
        ],
    }
    core.assert_target_free(public)
    payload = core.canonical_json_bytes(public)
    if len(payload) > int(caps["public_aggregate_output_bytes"]):
        raise core.CommP0GeneratedRefusal("public_output_cap_breach")
    if runtime > min(float(caps["wall_time_seconds"]), timeout_seconds * 4.0):
        raise core.CommP0GeneratedRefusal("temporary_output_cap_breach", "runtime")
    return public


def _assert_directory(path: Path) -> int:
    absolute = path.absolute()
    if sys.platform == "darwin" and len(absolute.parts) > 1:
        if absolute.parts[1] == "var":
            absolute = Path("/private/var", *absolute.parts[2:])
        elif absolute.parts[1] == "tmp":
            absolute = Path("/private/tmp", *absolute.parts[2:])
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute.anchor, flags)
    try:
        for part in absolute.parts[1:]:
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError("not a directory")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def publish_no_replace(path: str | Path, value: Mapping[str, Any]) -> None:
    destination = Path(path)
    payload = core.canonical_json_bytes(dict(value))
    if len(payload) > 1_048_576:
        raise core.CommP0GeneratedRefusal("public_output_cap_breach")
    try:
        directory_fd = _assert_directory(destination.parent)
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "filesystem_capability_publication_or_cleanup_escape"
        ) from exc
    temporary_name = f".{destination.name}.{os.getpid()}.{time.monotonic_ns()}.tmp"
    created = False
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        temporary_fd = os.open(temporary_name, flags, 0o600, dir_fd=directory_fd)
        created = True
        try:
            offset = 0
            while offset < len(payload):
                offset += os.write(temporary_fd, payload[offset:])
            os.fsync(temporary_fd)
        finally:
            os.close(temporary_fd)
        try:
            os.link(
                temporary_name,
                destination.name,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
        except FileExistsError as exc:
            raise core.CommP0GeneratedRefusal(
                "post_score_mutation_repeat_or_output_replacement"
            ) from exc
        os.unlink(temporary_name, dir_fd=directory_fd)
        created = False
        os.fsync(directory_fd)
    finally:
        if created:
            try:
                os.unlink(temporary_name, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
        os.close(directory_fd)


def _read_no_follow(path: Path) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise OSError("not a single-link regular file")
            payload = b""
            while block := os.read(descriptor, 1024 * 1024):
                payload += block
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "filesystem_capability_publication_or_cleanup_escape"
        ) from exc
    try:
        return json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        ) from exc


def validate_activation(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else core._repo_root()
    activation_path = repository / core.ACTIVATION_PATH
    if not activation_path.exists():
        raise core.CommP0GeneratedRefusal("score_before_exact_green_freeze")
    value = _read_no_follow(activation_path)
    expected = {
        "schema_name": ACTIVATION_SCHEMA,
        "schema_version": "0.1.0",
        "gate_id": core.GATE_ID,
        "contract_sha256": core.CONTRACT_SHA256,
        "generated_qualification_execution_authorized": True,
        "exact_implementation_commit_remotely_green": True,
        "base_python_job_green": True,
        "optional_neuro_readers_job_green": True,
        "single_official_invocation": True,
    }
    if any(value.get(key) != expected_value for key, expected_value in expected.items()):
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        )
    core.assert_target_free(value)
    return value


def run_official_qualification(
    output: str | Path, *, root: str | Path | None = None
) -> dict[str, Any]:
    """Remain fail-closed until a future exact, green activation is present."""

    validate_activation(root)
    raise core.CommP0GeneratedRefusal(
        "protocol_model_threshold_vocabulary_prior_or_code_hash_drift",
        "official invocation intentionally inactive in this implementation milestone",
    )
