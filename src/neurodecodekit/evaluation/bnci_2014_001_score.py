"""Hash-bound aggregate scorer for BNCI-C3C5-1."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence


LANE_ID = "BNCI-C3C5-1"
SCHEMA_VERSION = "0.1.0"
PARTICIPANTS = tuple(f"A{index:02d}" for index in range(1, 10))
CLASSES = ("left_hand", "right_hand", "feet", "tongue")
CONDITIONS = (
    "equal_prior_no_signal",
    "source_empirical_prior",
    "timing_only",
    "selected_E",
    "P",
    "P_plus_E",
    "P_plus_D_E",
    "exact_zero_EEG",
    "channel_rotation_EEG",
    "trial_displacement_EEG",
    "source_label_rotation_EEG",
    "pre_cue_EEG",
    "early_cue_EEG",
    "central_EEG",
    "frontal_EEG",
    "posterior_EEG",
)
PREDICTION_FIELDS = {
    "participant",
    "session",
    "run_ordinal",
    "trial_ordinal",
    "opaque_row_id",
    "condition",
    "probabilities",
}
TARGET_FIELDS = {
    "participant",
    "session",
    "run_ordinal",
    "trial_ordinal",
    "opaque_row_id",
    "target",
}


class BNCIScoreRefusal(ValueError):
    """Fail-closed scoring refusal."""


@dataclass(frozen=True)
class FreezeBindings:
    configuration_hash: str
    code_hash: str
    source_cache_hashes: Mapping[str, str]
    split_protocol_hash: str
    sealed_target_payload_sha256: str


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _reject_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BNCIScoreRefusal(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_jsonl(payload: bytes, *, kind: str) -> list[dict[str, Any]]:
    if not isinstance(payload, bytes) or not payload.endswith(b"\n"):
        raise BNCIScoreRefusal(f"{kind} is not newline-terminated bytes")
    rows: list[dict[str, Any]] = []
    for line in payload.splitlines():
        try:
            row = json.loads(line, object_pairs_hook=_reject_duplicate_object)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BNCIScoreRefusal(f"{kind} is malformed JSONL") from exc
        if not isinstance(row, dict) or _canonical_bytes(row).rstrip(b"\n") != line:
            raise BNCIScoreRefusal(f"{kind} is not canonical JSONL")
        rows.append(row)
    if not rows:
        raise BNCIScoreRefusal(f"{kind} is empty")
    return rows


def _identity(row: Mapping[str, Any]) -> tuple[str, str, int, int, str]:
    participant = row.get("participant")
    session = row.get("session")
    run = row.get("run_ordinal")
    trial = row.get("trial_ordinal")
    row_id = row.get("opaque_row_id")
    if participant not in PARTICIPANTS or session != "E":
        raise BNCIScoreRefusal("prediction identity is outside held-out E")
    if type(run) is not int or not 0 <= run < 6:
        raise BNCIScoreRefusal("run ordinal is invalid")
    if type(trial) is not int or trial < 0:
        raise BNCIScoreRefusal("trial ordinal is invalid")
    if not isinstance(row_id, str) or not _is_sha256(row_id):
        raise BNCIScoreRefusal("opaque row identity is invalid")
    return participant, session, run, trial, row_id


def _validate_probabilities(value: Any) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise BNCIScoreRefusal("probability vector shape differs")
    probabilities = tuple(float(item) for item in value)
    if any(not math.isfinite(item) or item < 0.0 or item > 1.0 for item in probabilities):
        raise BNCIScoreRefusal("probability vector contains an invalid value")
    if abs(math.fsum(probabilities) - 1.0) > 1e-9:
        raise BNCIScoreRefusal("probability vector does not sum to one")
    return probabilities  # type: ignore[return-value]


def _prediction_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    identity = _identity(row)
    condition = row.get("condition")
    if condition not in CONDITIONS:
        raise BNCIScoreRefusal("prediction condition is unavailable")
    return (*identity[:4], CONDITIONS.index(str(condition)))


def _target_sort_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return _identity(row)[:4]


def canonical_prediction_jsonl(rows: Sequence[Mapping[str, Any]]) -> bytes:
    normalized = [dict(row) for row in rows]
    _validate_prediction_rows(normalized)
    return b"".join(_canonical_bytes(row) for row in normalized)


def canonical_target_jsonl(rows: Sequence[Mapping[str, Any]]) -> bytes:
    normalized = [dict(row) for row in rows]
    _validate_target_rows(normalized)
    return b"".join(_canonical_bytes(row) for row in normalized)


def _validate_prediction_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    if any(set(row) != PREDICTION_FIELDS for row in rows):
        raise BNCIScoreRefusal("prediction row fields differ")
    if list(rows) != sorted(rows, key=_prediction_sort_key):
        raise BNCIScoreRefusal("prediction rows are not canonically ordered")
    identities: set[tuple[str, str, int, int, str, str]] = set()
    counts: dict[tuple[str, str], int] = {}
    row_conditions: dict[tuple[str, str, int, int, str], set[str]] = {}
    for row in rows:
        identity = _identity(row)
        condition = str(row["condition"])
        _validate_probabilities(row["probabilities"])
        full = (*identity, condition)
        if full in identities:
            raise BNCIScoreRefusal("prediction row is duplicated")
        identities.add(full)
        counts[(identity[0], condition)] = counts.get((identity[0], condition), 0) + 1
        row_conditions.setdefault(identity, set()).add(condition)
    expected_conditions = set(CONDITIONS)
    if any(value != expected_conditions for value in row_conditions.values()):
        raise BNCIScoreRefusal("prediction condition inventory differs by row")
    participant_counts = {
        participant: {counts[(participant, condition)] for condition in CONDITIONS}
        for participant in PARTICIPANTS
    }
    if any(len(values) != 1 or next(iter(values), 0) <= 0 for values in participant_counts.values()):
        raise BNCIScoreRefusal("participant prediction completeness differs")
    if len({next(iter(values)) for values in participant_counts.values()}) != 1:
        raise BNCIScoreRefusal("participant prediction row counts differ")


def _validate_target_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    if any(set(row) != TARGET_FIELDS for row in rows):
        raise BNCIScoreRefusal("sealed target row fields differ")
    if list(rows) != sorted(rows, key=_target_sort_key):
        raise BNCIScoreRefusal("sealed target rows are not canonically ordered")
    identities: set[tuple[str, str, int, int, str]] = set()
    participant_counts: dict[str, int] = {participant: 0 for participant in PARTICIPANTS}
    participant_targets: dict[str, set[str]] = {
        participant: set() for participant in PARTICIPANTS
    }
    for row in rows:
        identity = _identity(row)
        if identity in identities:
            raise BNCIScoreRefusal("sealed target row is duplicated")
        identities.add(identity)
        target = row.get("target")
        if target not in CLASSES:
            raise BNCIScoreRefusal("sealed target is outside four classes")
        participant_counts[identity[0]] += 1
        participant_targets[identity[0]].add(str(target))
    if len(set(participant_counts.values())) != 1 or min(participant_counts.values()) <= 0:
        raise BNCIScoreRefusal("sealed participant target counts differ")
    if any(targets != set(CLASSES) for targets in participant_targets.values()):
        raise BNCIScoreRefusal("sealed participant lacks a class")


def _validate_bindings(bindings: FreezeBindings) -> None:
    if not isinstance(bindings, FreezeBindings):
        raise BNCIScoreRefusal("freeze bindings type differs")
    for field in (
        bindings.configuration_hash,
        bindings.code_hash,
        bindings.split_protocol_hash,
        bindings.sealed_target_payload_sha256,
    ):
        if not _is_sha256(field):
            raise BNCIScoreRefusal("freeze binding hash is invalid")
    if not bindings.source_cache_hashes or any(
        not isinstance(key, str) or not _is_sha256(value)
        for key, value in bindings.source_cache_hashes.items()
    ):
        raise BNCIScoreRefusal("source cache hash inventory is invalid")


def build_prediction_freeze(
    prediction_payload: bytes, *, bindings: FreezeBindings
) -> dict[str, Any]:
    _validate_bindings(bindings)
    rows = _parse_jsonl(prediction_payload, kind="predictions")
    _validate_prediction_rows(rows)
    condition_hashes = {
        condition: _sha256(
            b"".join(_canonical_bytes(row) for row in rows if row["condition"] == condition)
        )
        for condition in CONDITIONS
    }
    freeze: dict[str, Any] = {
        "schema_name": "neurodecodekit.bnci_2014_001_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "frozen_target_blind_predictions_targets_sealed",
        "condition_ids": list(CONDITIONS),
        "prediction_set_sha256": _sha256(prediction_payload),
        "private_prediction_bytes": len(prediction_payload),
        "private_prediction_rows": len(rows),
        "condition_sha256": condition_hashes,
        "configuration_hash": bindings.configuration_hash,
        "code_hash": bindings.code_hash,
        "source_cache_hashes": dict(sorted(bindings.source_cache_hashes.items())),
        "split_protocol_hash": bindings.split_protocol_hash,
        "sealed_target_payload_sha256": bindings.sealed_target_payload_sha256,
    }
    freeze["freeze_record_sha256"] = _sha256(_canonical_bytes(freeze))
    return freeze


def validate_prediction_freeze(
    freeze: Mapping[str, Any], prediction_payload: bytes, *, bindings: FreezeBindings
) -> list[dict[str, Any]]:
    expected = build_prediction_freeze(prediction_payload, bindings=bindings)
    if dict(freeze) != expected:
        raise BNCIScoreRefusal("prediction freeze or immutable binding differs")
    return _parse_jsonl(prediction_payload, kind="predictions")


def balanced_accuracy(targets: Sequence[str], predictions: Sequence[str]) -> float:
    if len(targets) != len(predictions) or not targets:
        raise BNCIScoreRefusal("balanced-accuracy row count differs")
    recalls = []
    for target_class in CLASSES:
        indices = [index for index, value in enumerate(targets) if value == target_class]
        if not indices:
            raise BNCIScoreRefusal("balanced accuracy requires all four classes")
        recalls.append(
            math.fsum(predictions[index] == target_class for index in indices) / len(indices)
        )
    return math.fsum(recalls) / 4.0


def multiclass_log_loss(
    targets: Sequence[str], probabilities: Sequence[Sequence[float]]
) -> float:
    if len(targets) != len(probabilities) or not targets:
        raise BNCIScoreRefusal("log-loss row count differs")
    losses = []
    for target, row in zip(targets, probabilities, strict=True):
        values = _validate_probabilities(list(row))
        losses.append(-math.log(max(values[CLASSES.index(target)], 1e-15)))
    return math.fsum(losses) / len(losses)


def exact_sign_flip_p(values: Sequence[float]) -> float:
    if len(values) != 9 or any(not math.isfinite(value) for value in values):
        raise BNCIScoreRefusal("exact sign-flip test requires nine finite values")
    observed = math.fsum(values)
    tail = 0
    for mask in range(1 << 9):
        permuted = math.fsum(
            value if mask & (1 << index) else -value for index, value in enumerate(values)
        )
        if permuted >= observed - 1e-15:
            tail += 1
    return tail / float(1 << 9)


def route_result(*, integrity: bool, C3: bool, C5_partial: bool) -> str:
    if not integrity:
        return "BNCIC3C5-R0"
    if C3 and C5_partial:
        return "BNCIC3C5-R5"
    if C3:
        return "BNCIC3C5-R3"
    if C5_partial:
        return "BNCIC3C5-R4"
    return "BNCIC3C5-R2"


def _argmax(values: Sequence[float]) -> str:
    return CLASSES[max(range(4), key=lambda index: (values[index], -index))]


def _score_rows(
    prediction_rows: Sequence[Mapping[str, Any]], target_rows: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    target_map = {_identity(row): str(row["target"]) for row in target_rows}
    prediction_map = {
        (*_identity(row), str(row["condition"])): tuple(row["probabilities"])
        for row in prediction_rows
    }
    participant_ba: dict[str, dict[str, float]] = {}
    participant_loss: dict[str, dict[str, float]] = {}
    for participant in PARTICIPANTS:
        identities = sorted(identity for identity in target_map if identity[0] == participant)
        targets = [target_map[identity] for identity in identities]
        participant_ba[participant] = {}
        participant_loss[participant] = {}
        for condition in CONDITIONS:
            probabilities = [prediction_map[(*identity, condition)] for identity in identities]
            participant_ba[participant][condition] = balanced_accuracy(
                targets, [_argmax(row) for row in probabilities]
            )
            participant_loss[participant][condition] = multiclass_log_loss(
                targets, probabilities
            )

    def macro(values: Sequence[float]) -> float:
        return math.fsum(values) / 9.0

    ba_macro = {
        condition: macro([participant_ba[p][condition] for p in PARTICIPANTS])
        for condition in CONDITIONS
    }
    loss_macro = {
        condition: macro([participant_loss[p][condition] for p in PARTICIPANTS])
        for condition in CONDITIONS
    }
    no_signal_conditions = ("equal_prior_no_signal", "timing_only")
    control_conditions = (
        "channel_rotation_EEG",
        "trial_displacement_EEG",
        "source_label_rotation_EEG",
        "pre_cue_EEG",
        "early_cue_EEG",
        "central_EEG",
        "frontal_EEG",
        "posterior_EEG",
    )
    participant_primary_margins = [
        participant_ba[p]["selected_E"]
        - max(participant_ba[p][condition] for condition in no_signal_conditions)
        for p in PARTICIPANTS
    ]
    macro_no_signal_margin = ba_macro["selected_E"] - max(
        ba_macro[condition] for condition in no_signal_conditions
    )
    macro_control_margin = ba_macro["selected_E"] - max(
        ba_macro[condition] for condition in control_conditions
    )
    c3_components = {
        "macro_balanced_accuracy_at_least_0_35": ba_macro["selected_E"] >= 0.35 - 1e-12,
        "macro_no_signal_timing_margin_at_least_0_08": macro_no_signal_margin
        >= 0.08 - 1e-12,
        "macro_control_margin_at_least_0_02": macro_control_margin >= 0.02 - 1e-12,
        "positive_participant_primary_margins_at_least_8": sum(
            value > 0.0 for value in participant_primary_margins
        )
        >= 8,
        "exact_one_sided_sign_flip_p_at_most_0_05": exact_sign_flip_p(
            participant_primary_margins
        )
        <= 0.05 + 1e-12,
    }
    delta_eog = [
        participant_loss[p]["P"] - participant_loss[p]["P_plus_E"]
        for p in PARTICIPANTS
    ]
    delta_deranged = [
        participant_loss[p]["P_plus_D_E"] - participant_loss[p]["P_plus_E"]
        for p in PARTICIPANTS
    ]
    c5_components = {
        "macro_P_minus_P_plus_E_at_least_0_03": macro(delta_eog) >= 0.03 - 1e-12,
        "macro_P_plus_D_E_minus_P_plus_E_at_least_0_03": macro(delta_deranged)
        >= 0.03 - 1e-12,
        "positive_participant_EOG_deltas_at_least_8": sum(value > 0.0 for value in delta_eog)
        >= 8,
        "positive_participant_deranged_deltas_at_least_8": sum(
            value > 0.0 for value in delta_deranged
        )
        >= 8,
        "exact_EOG_delta_sign_flip_p_at_most_0_05": exact_sign_flip_p(delta_eog)
        <= 0.05 + 1e-12,
        "exact_deranged_delta_sign_flip_p_at_most_0_05": exact_sign_flip_p(delta_deranged)
        <= 0.05 + 1e-12,
    }
    c3_passed = all(c3_components.values())
    c5_passed = all(c5_components.values())
    return {
        "route": route_result(integrity=True, C3=c3_passed, C5_partial=c5_passed),
        "participant_count": 9,
        "held_out_session": "E",
        "C3_passed": c3_passed,
        "C5_partial_passed": c5_passed,
        "C3_components": c3_components,
        "C5_partial_components": c5_components,
        "participant_macro_balanced_accuracy": ba_macro,
        "participant_macro_log_loss": loss_macro,
        "C3_macro_no_signal_timing_margin": macro_no_signal_margin,
        "C3_macro_control_margin": macro_control_margin,
        "C3_positive_participant_margins": sum(
            value > 0.0 for value in participant_primary_margins
        ),
        "C3_exact_one_sided_sign_flip_p": exact_sign_flip_p(
            participant_primary_margins
        ),
        "C5_macro_EOG_delta": macro(delta_eog),
        "C5_macro_deranged_delta": macro(delta_deranged),
        "C5_positive_EOG_deltas": sum(value > 0.0 for value in delta_eog),
        "C5_positive_deranged_deltas": sum(value > 0.0 for value in delta_deranged),
        "C5_exact_EOG_delta_sign_flip_p": exact_sign_flip_p(delta_eog),
        "C5_exact_deranged_delta_sign_flip_p": exact_sign_flip_p(delta_deranged),
    }


def score_frozen_predictions(
    *,
    freeze: Mapping[str, Any],
    prediction_payload: bytes,
    bindings: FreezeBindings,
    checkpoint_verifier: Callable[[], bool],
    sealed_target_loader: Callable[[], bytes],
) -> dict[str, Any]:
    """Verify prediction commitments, deliver targets once, and score aggregates."""

    if not callable(checkpoint_verifier) or not checkpoint_verifier():
        raise BNCIScoreRefusal("checkpoint verification failed before target delivery")
    prediction_rows = validate_prediction_freeze(
        freeze, prediction_payload, bindings=bindings
    )
    if not callable(sealed_target_loader):
        raise BNCIScoreRefusal("sealed target loader is unavailable")
    try:
        target_payload = sealed_target_loader()
    except Exception as exc:
        raise BNCIScoreRefusal("sealed target delivery failed") from exc
    if not isinstance(target_payload, bytes):
        raise BNCIScoreRefusal("sealed target loader did not return bytes")
    if _sha256(target_payload) != bindings.sealed_target_payload_sha256:
        raise BNCIScoreRefusal("sealed target payload hash differs")
    target_rows = _parse_jsonl(target_payload, kind="sealed targets")
    _validate_target_rows(target_rows)
    prediction_identities = {_identity(row) for row in prediction_rows}
    target_identities = {_identity(row) for row in target_rows}
    if prediction_identities != target_identities:
        raise BNCIScoreRefusal("prediction and target identity inventories differ")
    score = _score_rows(prediction_rows, target_rows)
    return {
        "schema_name": "neurodecodekit.bnci_2014_001_aggregate_score",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "scored_once_frozen_router_applied",
        **score,
        "sealed_target_rows": len(target_rows),
        "sealed_target_loads": 1,
        "target_deliveries": 1,
        "scoring_events": 1,
        "post_target_updates": 0,
        "individual_predictions_targets_or_participant_outcomes_public": False,
    }


def generated_passing_rows(
    identities: Sequence[Mapping[str, Any]], targets: Sequence[str]
) -> list[dict[str, Any]]:
    """Build deterministic synthetic probabilities for scorer qualification only."""

    rows: list[dict[str, Any]] = []
    for identity, target in zip(identities, targets, strict=True):
        target_index = CLASSES.index(target)
        for condition in CONDITIONS:
            if condition in {"selected_E", "P_plus_E"}:
                confidence = 0.94 if condition == "P_plus_E" else 0.90
                probabilities = [(1.0 - confidence) / 3.0] * 4
                probabilities[target_index] = confidence
            elif condition in {"P", "P_plus_D_E"}:
                confidence = 0.50 if condition == "P" else 0.45
                probabilities = [(1.0 - confidence) / 3.0] * 4
                probabilities[target_index] = confidence
            else:
                probabilities = [0.25] * 4
            rows.append(
                {
                    **identity,
                    "condition": condition,
                    "probabilities": probabilities,
                }
            )
    return sorted(rows, key=_prediction_sort_key)
