"""Dependency-free identifiability checks for the prospective communication task."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

SCHEMA_NAME = "neurodecodekit.communication_task_identifiability_result"
SCHEMA_VERSION = "0.1.0"
COMMANDS = ("yes", "no", "help", "stop")
PROFILE_LEVELS = (0, 1, 2, 3)


class TaskIdentifiabilityError(ValueError):
    """Raised when the prospective contract cannot support the design audit."""


@dataclass(frozen=True)
class SyntheticTrial:
    """One generated design row; profiles are abstractions, not physiology."""

    target: str
    cue_content: str
    cue_side: int
    eog_profile: int
    oral_emg_profile: int
    timing_phase: int


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TaskIdentifiabilityError(f"{label} must be an object")
    return value


def _require_int(value: Any, label: str, *, minimum: int = 1) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise TaskIdentifiabilityError(f"{label} must be an integer >= {minimum}")
    return value


def _gf4_multiply(left: int, right: int) -> int:
    """Multiply two GF(4) elements encoded as two polynomial bits."""

    product = 0
    for bit in range(2):
        if (right >> bit) & 1:
            product ^= left << bit
    if product & 0b1000:
        product ^= 0b1110
    if product & 0b0100:
        product ^= 0b0111
    return product & 0b0011


def _orthogonal_profiles() -> tuple[tuple[int, int, int, int], ...]:
    """Return a 16-row, four-level pairwise-orthogonal nuisance schedule."""

    rows = []
    for left in PROFILE_LEVELS:
        for right in PROFILE_LEVELS:
            rows.append(
                (
                    left,
                    right,
                    left ^ right,
                    left ^ _gf4_multiply(2, right),
                )
            )
    return tuple(rows)


def build_endpoint_schedule(endpoint: str) -> tuple[SyntheticTrial, ...]:
    """Build the exact 64-row prompted or free-choice generated schedule."""

    if endpoint not in {"prompted", "free_choice"}:
        raise TaskIdentifiabilityError("endpoint must be prompted or free_choice")
    rows: list[SyntheticTrial] = []
    for target in COMMANDS:
        for cue_side, eog_profile, oral_emg_profile, timing_phase in _orthogonal_profiles():
            rows.append(
                SyntheticTrial(
                    target=target,
                    cue_content=target if endpoint == "prompted" else "neutral_go",
                    cue_side=cue_side,
                    eog_profile=eog_profile,
                    oral_emg_profile=oral_emg_profile,
                    timing_phase=timing_phase,
                )
            )
    return tuple(rows)


def _entropy(values: Sequence[Any]) -> float:
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * math.log(count / total) for count in counts.values())


def _mutual_information(targets: Sequence[str], features: Sequence[Any]) -> float:
    if len(targets) != len(features) or not targets:
        raise TaskIdentifiabilityError("mutual-information inputs must be nonempty and aligned")
    target_counts = Counter(targets)
    feature_counts = Counter(features)
    joint_counts = Counter(zip(targets, features, strict=True))
    total = len(targets)
    information = 0.0
    for (target, feature), count in joint_counts.items():
        joint = count / total
        information += joint * math.log(
            joint / ((target_counts[target] / total) * (feature_counts[feature] / total))
        )
    return information


def _bayes_accuracy(targets: Sequence[str], features: Sequence[Any]) -> float:
    grouped: dict[Any, Counter[str]] = defaultdict(Counter)
    for target, feature in zip(targets, features, strict=True):
        grouped[feature][target] += 1
    return sum(max(counts.values()) for counts in grouped.values()) / len(targets)


def _matrix_rank(rows: Sequence[Sequence[float]], *, tolerance: float = 1e-10) -> int:
    if not rows:
        return 0
    matrix = [list(map(float, row)) for row in rows]
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise TaskIdentifiabilityError("rank matrix rows must have equal width")
    rank = 0
    for column in range(column_count):
        pivot = max(range(rank, len(matrix)), key=lambda index: abs(matrix[index][column]))
        if abs(matrix[pivot][column]) <= tolerance:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        divisor = matrix[rank][column]
        matrix[rank] = [value / divisor for value in matrix[rank]]
        for row_index in range(len(matrix)):
            if row_index == rank:
                continue
            scale = matrix[row_index][column]
            if abs(scale) <= tolerance:
                continue
            matrix[row_index] = [
                value - scale * pivot_value
                for value, pivot_value in zip(
                    matrix[row_index], matrix[rank], strict=True
                )
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def _design_matrix(
    rows: Sequence[SyntheticTrial],
    *,
    include_target: bool,
) -> list[list[float]]:
    cue_levels = ("neutral_go",) + COMMANDS
    fields: tuple[tuple[str, Sequence[Any]], ...] = (
        ("cue_content", cue_levels),
        ("cue_side", PROFILE_LEVELS),
        ("eog_profile", PROFILE_LEVELS),
        ("oral_emg_profile", PROFILE_LEVELS),
        ("timing_phase", PROFILE_LEVELS),
    )
    matrix: list[list[float]] = []
    for row in rows:
        encoded = [1.0]
        for field, levels in fields:
            value = getattr(row, field)
            encoded.extend(float(value == level) for level in levels[1:])
        if include_target:
            encoded.extend(float(row.target == target) for target in COMMANDS[1:])
        matrix.append(encoded)
    return matrix


def summarize_endpoint(rows: Sequence[SyntheticTrial]) -> dict[str, Any]:
    """Summarize target leakage and target degrees of freedom for one endpoint."""

    targets = [row.target for row in rows]
    nuisance = [
        (
            row.cue_content,
            row.cue_side,
            row.eog_profile,
            row.oral_emg_profile,
            row.timing_phase,
        )
        for row in rows
    ]
    nuisance_rank = _matrix_rank(_design_matrix(rows, include_target=False))
    augmented_rank = _matrix_rank(_design_matrix(rows, include_target=True))
    pairwise_information = {
        field: _mutual_information(targets, [getattr(row, field) for row in rows])
        for field in (
            "cue_content",
            "cue_side",
            "eog_profile",
            "oral_emg_profile",
            "timing_phase",
        )
    }
    information = _mutual_information(targets, nuisance)
    bayes_accuracy = _bayes_accuracy(targets, nuisance)
    target_incremental_df = augmented_rank - nuisance_rank
    return {
        "rows": len(rows),
        "target_classes": len(set(targets)),
        "target_entropy_nats": _entropy(targets),
        "nuisance_mutual_information_nats": information,
        "nuisance_bayes_accuracy": bayes_accuracy,
        "pairwise_target_information_nats": pairwise_information,
        "nuisance_design_rank": nuisance_rank,
        "augmented_design_rank": augmented_rank,
        "target_incremental_degrees_of_freedom": target_incremental_df,
        "target_separable_from_scheduled_nuisance": (
            target_incremental_df == len(COMMANDS) - 1
            and information <= 1e-12
            and bayes_accuracy <= (1 / len(COMMANDS)) + 1e-12
        ),
    }


def exact_binomial_tail(n: int, minimum_successes: int, probability: float) -> float:
    """Return P[X >= minimum_successes] for X ~ Binomial(n, probability)."""

    _require_int(n, "n")
    _require_int(minimum_successes, "minimum_successes", minimum=0)
    if minimum_successes > n:
        return 0.0
    if not 0.0 <= probability <= 1.0:
        raise TaskIdentifiabilityError("probability must be between zero and one")
    return sum(
        math.comb(n, successes)
        * probability**successes
        * (1.0 - probability) ** (n - successes)
        for successes in range(minimum_successes, n + 1)
    )


def sign_test_sensitivity(
    participants: int,
    *,
    alpha: float = 0.05,
    positive_probabilities: Sequence[float] = (0.6, 0.7, 0.8, 0.804, 0.9),
) -> dict[str, Any]:
    """Compute exact one- and two-cohort sensitivity for participant consistency."""

    _require_int(participants, "participants")
    critical = next(
        successes
        for successes in range(participants + 1)
        if exact_binomial_tail(participants, successes, 0.5) <= alpha
    )
    rows = []
    for probability in positive_probabilities:
        one_cohort = exact_binomial_tail(participants, critical, probability)
        rows.append(
            {
                "true_positive_participant_probability": probability,
                "one_cohort_power": one_cohort,
                "two_independent_cohorts_joint_power": one_cohort**2,
            }
        )
    return {
        "participants_per_cohort": participants,
        "alpha_one_sided": alpha,
        "minimum_positive_participants": critical,
        "null_tail_probability": exact_binomial_tail(participants, critical, 0.5),
        "power_curve": rows,
        "interpretation": (
            "The 21-person design has high two-cohort power only when the true "
            "positive-participant probability is near 0.80, not merely at the 0.70 "
            "acceptance boundary."
        ),
    }


def _storage_and_device_summary(contract: Mapping[str, Any]) -> dict[str, Any]:
    cohorts = _require_mapping(contract.get("cohorts"), "cohorts")
    acquisition = _require_mapping(contract.get("acquisition"), "acquisition")
    channels = _require_mapping(acquisition.get("biosignal_channels"), "biosignal_channels")
    storage = _require_mapping(contract.get("storage_budget"), "storage_budget")
    total_participants = _require_int(
        cohorts.get("maximum_total_enrolled_participants"),
        "maximum_total_enrolled_participants",
    )
    total_channels = _require_int(channels.get("total"), "biosignal_channels.total")
    seconds = _require_int(
        acquisition.get("maximum_recording_seconds_per_participant"),
        "maximum_recording_seconds_per_participant",
    )
    biosignal_bytes = (
        total_participants
        * total_channels
        * _require_int(acquisition.get("biosignal_sampling_rate_hz"), "biosignal_sampling_rate_hz")
        * _require_int(
            acquisition.get("biosignal_storage_bytes_per_sample"),
            "biosignal_storage_bytes_per_sample",
        )
        * seconds
    )
    audio_bytes = (
        total_participants
        * _require_int(acquisition.get("audio_sampling_rate_hz"), "audio_sampling_rate_hz")
        * _require_int(acquisition.get("audio_channels"), "audio_channels")
        * _require_int(
            acquisition.get("audio_storage_bytes_per_sample"),
            "audio_storage_bytes_per_sample",
        )
        * seconds
    )
    raw_total = biosignal_bytes + audio_bytes
    declared_total = _require_int(storage.get("raw_total_worst_case_bytes"), "raw total")
    if raw_total != declared_total:
        raise TaskIdentifiabilityError("recomputed raw storage differs from the frozen contract")
    raw_cap = _require_int(storage.get("raw_payload_cap_bytes"), "raw payload cap")
    return {
        "maximum_enrolled_participants": total_participants,
        "maximum_recording_minutes_per_participant": seconds / 60.0,
        "biosignal_channels": dict(channels),
        "biosignal_sampling_rate_hz": acquisition["biosignal_sampling_rate_hz"],
        "microphone_required": acquisition.get("microphone_required") is True,
        "hardware_trigger_required": acquisition.get("hardware_trigger_required") is True,
        "photodiode_required": acquisition.get("photodiode_display_onset_required") is True,
        "raw_biosignal_worst_case_bytes": biosignal_bytes,
        "raw_audio_worst_case_bytes": audio_bytes,
        "raw_total_worst_case_bytes": raw_total,
        "raw_payload_cap_bytes": raw_cap,
        "raw_cap_headroom_bytes": raw_cap - raw_total,
        "fits_frozen_raw_cap": raw_total <= raw_cap,
        "consent_and_hardware_boundary": (
            "No human recording is authorized; consent, approved hardware, privacy, "
            "and a fresh Tier C decision remain mandatory before acquisition."
        ),
    }


def run_task_identifiability_audit(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Run the generated task, power, storage, and device audit."""

    contract = _require_mapping(contract, "contract")
    task = _require_mapping(contract.get("task"), "task")
    if task.get("command_inventory_semantics") != list(COMMANDS):
        raise TaskIdentifiabilityError("command inventory differs from the four frozen commands")
    if task.get("prompted_intend_trials_per_participant") != 64:
        raise TaskIdentifiabilityError("prompted trial count differs from 64")
    if task.get("free_choice_intend_trials_per_participant") != 64:
        raise TaskIdentifiabilityError("free-choice trial count differs from 64")
    cohorts = _require_mapping(contract.get("cohorts"), "cohorts")
    discovery = _require_mapping(cohorts.get("discovery"), "cohorts.discovery")
    participants = _require_int(
        discovery.get("minimum_complete_participants"),
        "minimum complete discovery participants",
    )
    prompted = summarize_endpoint(build_endpoint_schedule("prompted"))
    free_choice = summarize_endpoint(build_endpoint_schedule("free_choice"))
    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_design_audit_no_scientific_signal",
        "scientific_question": (
            "Can the frozen task separate intended command identity from scheduled cue, "
            "eye, oral-muscle, and timing profiles?"
        ),
        "endpoint_results": {
            "prompted": prompted,
            "free_choice": free_choice,
        },
        "belief_update": (
            "Prompted trials cannot identify intention beyond cue content, while the "
            "free-choice precommitment endpoint is structurally separable from the "
            "generated nuisance schedule and must remain the non-rescuable primary endpoint."
        ),
        "power_sensitivity": sign_test_sensitivity(participants),
        "storage_and_device": _storage_and_device_summary(contract),
        "operation_counters": {
            "real_or_private_reads": 0,
            "network_bytes": 0,
            "human_participants": 0,
            "device_runs": 0,
            "model_fits": 0,
            "model_inference_runs": 0,
            "target_deliveries": 0,
            "scientific_scores": 0,
        },
        "warnings": [
            "Generated profile independence is not evidence that EEG contains command information.",
            "Recorded EOG and oral EMG do not exclude unmeasured peripheral contamination.",
            "Prompted cue content reveals the target and cannot establish intent-specific decoding.",
            "Free-choice validity still requires blinded target precommitment and a target firewall.",
            "No recruitment, consent, hardware, private data, or claim operation occurred.",
        ],
        "claim_boundary": {
            "task_schedule_identifiability_checked": True,
            "scientific_neural_effect_established": False,
            "communication_decoding_established": False,
            "EEG_beyond_peripheral_established": False,
            "unseen_person_generalization_established": False,
            "live_decoding_established": False,
        },
    }
