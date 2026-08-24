"""Generated-only UG1 prediction firewall and aggregate scoring helpers.

This module intentionally uses only the Python standard library. It validates
the target-blind prediction bytes and their public commitments before invoking
the sealed-target loader, then exposes aggregate task metrics only.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


SCHEMA_VERSION = "0.1.0"
LANE_ID = "EEGMMIDB-UG1"
PARTICIPANTS = tuple(f"S{index:03d}" for index in range(16, 31))
TASK_RUNS = {"execution": 11, "imagery": 12}
CONDITION_IDS = (
    "primary_whole_head",
    "equal_prior_no_signal",
    "timing_only",
    "exact_zero",
    "fixed_channel_permutation",
    "nonwrapping_event_displacement",
    "fixed_source_label_derangement",
    "pre_cue",
    "early_cue",
    "central_view",
    "frontal_view",
    "occipital_view",
)
PREDICTION_FIELDS = frozenset(
    {
        "schema_version",
        "opaque_row_id",
        "task",
        "participant",
        "run",
        "event_ordinal",
        "cue_sample",
        "condition",
        "prediction",
    }
)
TARGET_FIELDS = frozenset(
    {
        "schema_version",
        "opaque_row_id",
        "task",
        "participant",
        "run",
        "event_ordinal",
        "cue_sample",
        "target",
    }
)
FREEZE_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "condition_ids",
        "task_condition_counts",
        "task_condition_sha256",
        "checkpoint_hashes",
        "configuration_hash",
        "code_hash",
        "prediction_set_hash",
        "canonical_row_order_hash",
        "sealed_target_payload_sha256",
        "private_prediction_bytes",
        "private_prediction_rows",
        "freeze_record_sha256",
    }
)
SHA256_HEX = frozenset("0123456789abcdef")
COMPARISON_TOLERANCE = 1e-12


class UG1ScoreRefusal(ValueError):
    """Fail-closed UG1 scorer refusal, always routed to R0."""

    route = "EEGMMIDBUG1-R0"

    def __init__(self, reason: str, detail: str):
        self.reason = reason
        self.detail = detail
        super().__init__(f"{self.route} {reason}: {detail}")


@dataclass(frozen=True)
class FreezeBindings:
    """External immutable bindings the public freeze cannot self-authenticate."""

    checkpoint_hashes: Mapping[str, str]
    configuration_hash: str
    code_hash: str
    sealed_target_payload_sha256: str


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise UG1ScoreRefusal("canonical_json", "value is not canonical JSON") from exc


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value).issubset(SHA256_HEX)


def _require_sha256(value: Any, field: str) -> str:
    if not _is_sha256(value):
        raise UG1ScoreRefusal("hash", f"{field} is not a lowercase SHA-256")
    return value


def _reject_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise UG1ScoreRefusal("json_schema", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_canonical_jsonl(payload: bytes, *, kind: str) -> list[dict[str, Any]]:
    if not isinstance(payload, bytes) or not payload or not payload.endswith(b"\n"):
        raise UG1ScoreRefusal("canonical_jsonl", f"{kind} must be nonempty LF-terminated bytes")
    if b"\r" in payload or b"\x00" in payload:
        raise UG1ScoreRefusal("canonical_jsonl", f"{kind} contains a forbidden byte")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise UG1ScoreRefusal("canonical_jsonl", f"{kind} is not UTF-8") from exc
    lines = text.splitlines()
    if not lines or any(not line for line in lines):
        raise UG1ScoreRefusal("canonical_jsonl", f"{kind} contains a blank row")
    rows: list[dict[str, Any]] = []
    for line in lines:
        try:
            row = json.loads(line, object_pairs_hook=_reject_duplicate_object)
        except UG1ScoreRefusal:
            raise
        except (json.JSONDecodeError, TypeError) as exc:
            raise UG1ScoreRefusal("canonical_jsonl", f"{kind} contains invalid JSON") from exc
        if not isinstance(row, dict):
            raise UG1ScoreRefusal("json_schema", f"{kind} row is not an object")
        rows.append(row)
    rebuilt = b"".join(_canonical_json_bytes(row) + b"\n" for row in rows)
    if rebuilt != payload:
        raise UG1ScoreRefusal("canonical_jsonl", f"{kind} bytes are not canonical")
    return rows


def canonical_prediction_jsonl(rows: Sequence[Mapping[str, Any]]) -> bytes:
    """Serialize already ordered generated prediction rows canonically."""

    normalized = [dict(row) for row in rows]
    payload = b"".join(_canonical_json_bytes(row) + b"\n" for row in normalized)
    _validate_prediction_rows(_parse_canonical_jsonl(payload, kind="predictions"))
    return payload


def canonical_target_jsonl(rows: Sequence[Mapping[str, Any]]) -> bytes:
    """Serialize sealed generated target rows canonically for scorer tests."""

    normalized = [dict(row) for row in rows]
    payload = b"".join(_canonical_json_bytes(row) + b"\n" for row in normalized)
    _validate_target_rows(_parse_canonical_jsonl(payload, kind="sealed targets"))
    return payload


def _require_exact_int(value: Any, field: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise UG1ScoreRefusal("row_schema", f"{field} is not a valid integer")
    return value


def _identity_key(row: Mapping[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(row["task"]),
        str(row["participant"]),
        int(row["run"]),
        int(row["event_ordinal"]),
    )


def _prediction_sort_key(row: Mapping[str, Any]) -> tuple[str, str, int, int, str]:
    return (*_identity_key(row), str(row["condition"]))


def _validate_common_identity(row: Mapping[str, Any]) -> None:
    task = row.get("task")
    participant = row.get("participant")
    if task not in TASK_RUNS:
        raise UG1ScoreRefusal("row_schema", "task is outside execution/imagery")
    if participant not in PARTICIPANTS:
        raise UG1ScoreRefusal("row_schema", "participant is outside S016-S030")
    run = _require_exact_int(row.get("run"), "run")
    if run != TASK_RUNS[task]:
        raise UG1ScoreRefusal("row_schema", "task and run do not match")
    ordinal = _require_exact_int(row.get("event_ordinal"), "event_ordinal")
    if ordinal > 14:
        raise UG1ScoreRefusal("row_schema", "event ordinal is outside zero through 14")
    _require_exact_int(row.get("cue_sample"), "cue_sample")
    opaque = row.get("opaque_row_id")
    if not isinstance(opaque, str) or not opaque or len(opaque.encode("utf-8")) > 256:
        raise UG1ScoreRefusal("row_schema", "opaque row ID is invalid")
    if row.get("schema_version") != SCHEMA_VERSION:
        raise UG1ScoreRefusal("row_schema", "row schema version differs")


def _validate_prediction_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    expected_rows = len(TASK_RUNS) * len(PARTICIPANTS) * 15 * len(CONDITION_IDS)
    if len(rows) != expected_rows:
        raise UG1ScoreRefusal("prediction_completeness", "prediction row count differs")
    observed_keys: set[tuple[str, str, int, int, str]] = set()
    identity_metadata: dict[tuple[str, str, int, int], tuple[str, int]] = {}
    for row in rows:
        if set(row) != PREDICTION_FIELDS:
            raise UG1ScoreRefusal("prediction_firewall", "prediction row fields differ")
        _validate_common_identity(row)
        condition = row.get("condition")
        prediction = row.get("prediction")
        if condition not in CONDITION_IDS or prediction not in {"T1", "T2"}:
            raise UG1ScoreRefusal("prediction_firewall", "condition or prediction differs")
        key = _prediction_sort_key(row)
        if key in observed_keys:
            raise UG1ScoreRefusal("prediction_completeness", "duplicate prediction row")
        observed_keys.add(key)
        identity = _identity_key(row)
        metadata = (str(row["opaque_row_id"]), int(row["cue_sample"]))
        previous = identity_metadata.setdefault(identity, metadata)
        if previous != metadata:
            raise UG1ScoreRefusal("prediction_identity", "identity metadata differs by condition")
    keys = [_prediction_sort_key(row) for row in rows]
    if keys != sorted(keys):
        raise UG1ScoreRefusal("prediction_order", "prediction rows are not canonically ordered")
    opaque_ids = {opaque for opaque, _cue_sample in identity_metadata.values()}
    if len(identity_metadata) != 450 or len(opaque_ids) != 450:
        raise UG1ScoreRefusal("prediction_identity", "opaque identities are incomplete or collide")
    for task in TASK_RUNS:
        for participant in PARTICIPANTS:
            cue_samples = {
                cue_sample
                for (row_task, row_participant, _run, _ordinal), (_opaque, cue_sample) in (
                    identity_metadata.items()
                )
                if row_task == task and row_participant == participant
            }
            if len(cue_samples) != 15:
                raise UG1ScoreRefusal("prediction_identity", "duplicate cue sample")


def _validate_target_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    if len(rows) != 450:
        raise UG1ScoreRefusal("target_completeness", "sealed target row count differs")
    identities: set[tuple[str, str, int, int]] = set()
    opaque_ids: set[str] = set()
    for row in rows:
        if set(row) != TARGET_FIELDS:
            raise UG1ScoreRefusal("target_firewall", "sealed target row fields differ")
        _validate_common_identity(row)
        if row.get("target") not in {"T1", "T2"}:
            raise UG1ScoreRefusal("target_schema", "sealed target is outside T1/T2")
        identity = _identity_key(row)
        if identity in identities or row["opaque_row_id"] in opaque_ids:
            raise UG1ScoreRefusal("target_completeness", "sealed target identity is duplicated")
        identities.add(identity)
        opaque_ids.add(str(row["opaque_row_id"]))
    keys = [_identity_key(row) for row in rows]
    if keys != sorted(keys):
        raise UG1ScoreRefusal("target_order", "sealed targets are not canonically ordered")
    for task, run in TASK_RUNS.items():
        task_rows = [row for row in rows if row["task"] == task and row["run"] == run]
        if len(task_rows) != 225:
            raise UG1ScoreRefusal("target_completeness", f"{task} target count differs")
        for participant in PARTICIPANTS:
            participant_rows = [row for row in task_rows if row["participant"] == participant]
            if len(participant_rows) != 15:
                raise UG1ScoreRefusal(
                    "target_completeness", f"{task} participant target count differs"
                )
            if {row["target"] for row in participant_rows} != {"T1", "T2"}:
                raise UG1ScoreRefusal(
                    "target_completeness", f"{task} participant lacks both classes"
                )
            if len({row["cue_sample"] for row in participant_rows}) != 15:
                raise UG1ScoreRefusal(
                    "target_completeness", f"{task} participant has duplicate cue samples"
                )


def _canonical_order_hash(rows: Sequence[Mapping[str, Any]]) -> str:
    order = [
        {
            "task": row["task"],
            "participant": row["participant"],
            "run": row["run"],
            "event_ordinal": row["event_ordinal"],
            "condition": row["condition"],
        }
        for row in rows
    ]
    return _sha256(_canonical_json_bytes(order))


def _condition_commitments(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, str]]]:
    counts: dict[str, dict[str, int]] = {}
    hashes: dict[str, dict[str, str]] = {}
    for task in TASK_RUNS:
        counts[task] = {}
        hashes[task] = {}
        for condition in CONDITION_IDS:
            selected = [
                row for row in rows if row["task"] == task and row["condition"] == condition
            ]
            subset = b"".join(_canonical_json_bytes(row) + b"\n" for row in selected)
            counts[task][condition] = len(selected)
            hashes[task][condition] = _sha256(subset)
    return counts, hashes


def _validate_bindings(bindings: FreezeBindings) -> dict[str, str]:
    if not isinstance(bindings, FreezeBindings):
        raise UG1ScoreRefusal("freeze_binding", "freeze bindings type differs")
    checkpoint_hashes = dict(bindings.checkpoint_hashes)
    if not checkpoint_hashes or any(
        not isinstance(key, str) or not key or not _is_sha256(value)
        for key, value in checkpoint_hashes.items()
    ):
        raise UG1ScoreRefusal("freeze_binding", "checkpoint hash inventory differs")
    _require_sha256(bindings.configuration_hash, "configuration_hash")
    _require_sha256(bindings.code_hash, "code_hash")
    _require_sha256(bindings.sealed_target_payload_sha256, "sealed_target_payload_sha256")
    return checkpoint_hashes


def build_prediction_freeze(
    prediction_payload: bytes,
    *,
    bindings: FreezeBindings,
) -> dict[str, Any]:
    """Build an aggregate public freeze from canonical target-free prediction bytes."""

    checkpoint_hashes = _validate_bindings(bindings)
    rows = _parse_canonical_jsonl(prediction_payload, kind="predictions")
    _validate_prediction_rows(rows)
    counts, hashes = _condition_commitments(rows)
    freeze: dict[str, Any] = {
        "schema_name": "neurodecodekit.eegmmidb_unseen_participant_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "frozen_target_blind_predictions_targets_sealed",
        "condition_ids": list(CONDITION_IDS),
        "task_condition_counts": counts,
        "task_condition_sha256": hashes,
        "checkpoint_hashes": checkpoint_hashes,
        "configuration_hash": bindings.configuration_hash,
        "code_hash": bindings.code_hash,
        "prediction_set_hash": _sha256(prediction_payload),
        "canonical_row_order_hash": _canonical_order_hash(rows),
        "sealed_target_payload_sha256": bindings.sealed_target_payload_sha256,
        "private_prediction_bytes": len(prediction_payload),
        "private_prediction_rows": len(rows),
    }
    freeze["freeze_record_sha256"] = _sha256(_canonical_json_bytes(freeze))
    return freeze


def validate_prediction_freeze(
    freeze: Mapping[str, Any],
    prediction_payload: bytes,
    *,
    bindings: FreezeBindings,
) -> list[dict[str, Any]]:
    """Rehash a public freeze and exact private prediction payload."""

    checkpoint_hashes = _validate_bindings(bindings)
    if not isinstance(freeze, Mapping) or set(freeze) != FREEZE_FIELDS:
        raise UG1ScoreRefusal("freeze_schema", "public freeze fields differ")
    if freeze.get("schema_name") != (
        "neurodecodekit.eegmmidb_unseen_participant_prediction_freeze"
    ):
        raise UG1ScoreRefusal("freeze_schema", "public freeze schema differs")
    if freeze.get("schema_version") != SCHEMA_VERSION or freeze.get("lane_id") != LANE_ID:
        raise UG1ScoreRefusal("freeze_schema", "public freeze version or lane differs")
    if freeze.get("status") != "frozen_target_blind_predictions_targets_sealed":
        raise UG1ScoreRefusal("freeze_schema", "public freeze status differs")
    if freeze.get("condition_ids") != list(CONDITION_IDS):
        raise UG1ScoreRefusal("freeze_schema", "condition inventory differs")
    unsigned = dict(freeze)
    observed_record_hash = unsigned.pop("freeze_record_sha256", None)
    if observed_record_hash != _sha256(_canonical_json_bytes(unsigned)):
        raise UG1ScoreRefusal("freeze_hash", "freeze record hash differs")
    if freeze.get("checkpoint_hashes") != checkpoint_hashes:
        raise UG1ScoreRefusal("freeze_binding", "checkpoint hashes differ")
    for field, expected in (
        ("configuration_hash", bindings.configuration_hash),
        ("code_hash", bindings.code_hash),
        ("sealed_target_payload_sha256", bindings.sealed_target_payload_sha256),
    ):
        if freeze.get(field) != expected:
            raise UG1ScoreRefusal("freeze_binding", f"{field} differs")
    if freeze.get("prediction_set_hash") != _sha256(prediction_payload):
        raise UG1ScoreRefusal("prediction_hash", "private prediction payload hash differs")
    if freeze.get("private_prediction_bytes") != len(prediction_payload):
        raise UG1ScoreRefusal("prediction_hash", "private prediction byte count differs")
    rows = _parse_canonical_jsonl(prediction_payload, kind="predictions")
    _validate_prediction_rows(rows)
    if freeze.get("private_prediction_rows") != len(rows):
        raise UG1ScoreRefusal("prediction_completeness", "private prediction rows differ")
    counts, hashes = _condition_commitments(rows)
    if freeze.get("task_condition_counts") != counts:
        raise UG1ScoreRefusal("prediction_hash", "task-condition counts differ")
    if freeze.get("task_condition_sha256") != hashes:
        raise UG1ScoreRefusal("prediction_hash", "task-condition hashes differ")
    if freeze.get("canonical_row_order_hash") != _canonical_order_hash(rows):
        raise UG1ScoreRefusal("prediction_order", "canonical row-order hash differs")
    return rows


def balanced_accuracy(targets: Sequence[str], predictions: Sequence[str]) -> float:
    """Compute exact two-class T1/T2 balanced accuracy."""

    target_values = list(targets)
    prediction_values = list(predictions)
    if len(target_values) != len(prediction_values) or not target_values:
        raise UG1ScoreRefusal("score_shape", "balanced-accuracy rows differ")
    if not set(target_values).issubset({"T1", "T2"}) or not set(prediction_values).issubset(
        {"T1", "T2"}
    ):
        raise UG1ScoreRefusal("score_value", "balanced-accuracy values differ")
    recalls = []
    for target_class in ("T1", "T2"):
        indices = [index for index, value in enumerate(target_values) if value == target_class]
        if not indices:
            raise UG1ScoreRefusal("score_class", "balanced accuracy requires both classes")
        recalls.append(
            math.fsum(prediction_values[index] == target_class for index in indices) / len(indices)
        )
    return math.fsum(recalls) / 2.0


def exact_sign_flip_p(values: Sequence[float]) -> float:
    """Enumerate the frozen one-sided 15-unit sign-flip test, retaining ties."""

    observed_values = [float(value) for value in values]
    if len(observed_values) != 15 or not all(math.isfinite(value) for value in observed_values):
        raise UG1ScoreRefusal("sign_flip", "exactly 15 finite participant values are required")
    observed = math.fsum(observed_values) / 15.0
    tail_count = 0
    assignments = 1 << 15
    for mask in range(assignments):
        statistic = (
            math.fsum(
                value if mask & (1 << index) else -value
                for index, value in enumerate(observed_values)
            )
            / 15.0
        )
        if statistic >= observed - COMPARISON_TOLERANCE:
            tail_count += 1
    return tail_count / assignments


def route_ug1(
    *,
    integrity_passed: bool,
    source_loso_execution_passed: bool,
    final_score_available: bool,
    execution_passed: bool,
    imagery_passed: bool,
) -> str:
    """Apply the frozen R0-R4 ordering without skipping an earlier gate."""

    values = (
        integrity_passed,
        source_loso_execution_passed,
        final_score_available,
        execution_passed,
        imagery_passed,
    )
    if any(type(value) is not bool for value in values):
        raise UG1ScoreRefusal("router", "router inputs must be exact booleans")
    if not integrity_passed:
        return "EEGMMIDBUG1-R0"
    if not source_loso_execution_passed:
        return "EEGMMIDBUG1-R1"
    if not final_score_available:
        return "EEGMMIDBUG1-R0"
    if not execution_passed:
        return "EEGMMIDBUG1-R2"
    if imagery_passed:
        return "EEGMMIDBUG1-R4"
    return "EEGMMIDBUG1-R3"


def _condition_metrics(
    *,
    targets_by_identity: Mapping[tuple[str, str, int, int], str],
    prediction_rows: Sequence[Mapping[str, Any]],
    task: str,
    condition: str,
) -> tuple[dict[str, Any], list[float]]:
    selected = [
        row for row in prediction_rows if row["task"] == task and row["condition"] == condition
    ]
    pooled_targets: list[str] = []
    pooled_predictions: list[str] = []
    participant_scores: list[float] = []
    for participant in PARTICIPANTS:
        participant_rows = [row for row in selected if row["participant"] == participant]
        targets = [targets_by_identity[_identity_key(row)] for row in participant_rows]
        predictions = [str(row["prediction"]) for row in participant_rows]
        participant_scores.append(balanced_accuracy(targets, predictions))
        pooled_targets.extend(targets)
        pooled_predictions.extend(predictions)
    return (
        {
            "event_count": len(pooled_targets),
            "pooled_balanced_accuracy": balanced_accuracy(pooled_targets, pooled_predictions),
            "participant_macro_balanced_accuracy": math.fsum(participant_scores) / 15.0,
            "ordinary_pooled_accuracy": math.fsum(
                target == prediction
                for target, prediction in zip(pooled_targets, pooled_predictions, strict=True)
            )
            / len(pooled_targets),
            "participants_strictly_above_chance": sum(score > 0.5 for score in participant_scores),
            "exact_one_sided_sign_flip_p_against_chance": exact_sign_flip_p(
                [score - 0.5 for score in participant_scores]
            ),
        },
        participant_scores,
    )


def _paired_control_summary(
    primary: Sequence[float],
    controls: Sequence[Sequence[float]],
) -> dict[str, float]:
    strongest = [max(values) for values in zip(*controls, strict=True)]
    differences = [
        primary_score - control_score
        for primary_score, control_score in zip(primary, strongest, strict=True)
    ]
    return {
        "participant_macro_margin": math.fsum(differences) / 15.0,
        "exact_one_sided_paired_sign_flip_p": exact_sign_flip_p(differences),
    }


def _gate_components(
    task: str,
    primary: Mapping[str, Any],
    b_summary: Mapping[str, float],
    c_summary: Mapping[str, float],
    a_summary: Mapping[str, float],
) -> dict[str, bool]:
    chance_ceiling = 0.01 if task == "execution" else 0.05
    return {
        "event_count_exact": primary["event_count"] == 225,
        "pooled_balanced_accuracy_at_least_0_60": (
            primary["pooled_balanced_accuracy"] >= 0.60 - COMPARISON_TOLERANCE
        ),
        "participant_macro_balanced_accuracy_at_least_0_60": (
            primary["participant_macro_balanced_accuracy"] >= 0.60 - COMPARISON_TOLERANCE
        ),
        "participants_strictly_above_chance_at_least_11": (
            primary["participants_strictly_above_chance"] >= 11
        ),
        "chance_sign_flip_p_at_most_frozen_ceiling": (
            primary["exact_one_sided_sign_flip_p_against_chance"]
            <= chance_ceiling + COMPARISON_TOLERANCE
        ),
        "macro_margin_over_B_i_at_least_0_10": (
            b_summary["participant_macro_margin"] >= 0.10 - COMPARISON_TOLERANCE
        ),
        "paired_sign_flip_p_against_B_i_at_most_0_05": (
            b_summary["exact_one_sided_paired_sign_flip_p"] <= 0.05 + COMPARISON_TOLERANCE
        ),
        "macro_margin_over_C_i_at_least_0_02": (
            c_summary["participant_macro_margin"] >= 0.02 - COMPARISON_TOLERANCE
        ),
        "paired_sign_flip_p_against_C_i_at_most_0_05": (
            c_summary["exact_one_sided_paired_sign_flip_p"] <= 0.05 + COMPARISON_TOLERANCE
        ),
        "macro_margin_over_A_i_at_least_0_02": (
            a_summary["participant_macro_margin"] >= 0.02 - COMPARISON_TOLERANCE
        ),
        "paired_sign_flip_p_against_A_i_at_most_0_05": (
            a_summary["exact_one_sided_paired_sign_flip_p"] <= 0.05 + COMPARISON_TOLERANCE
        ),
    }


def qualify_gate_threshold_boundaries() -> dict[str, int]:
    """Exercise every inclusive gate at its pass and first fail-side boundary."""

    failure_cases = 0
    for task in ("execution", "imagery"):
        primary = {
            "event_count": 225,
            "pooled_balanced_accuracy": 0.60,
            "participant_macro_balanced_accuracy": 0.60,
            "participants_strictly_above_chance": 11,
            "exact_one_sided_sign_flip_p_against_chance": 0.01 if task == "execution" else 0.05,
        }
        b_summary = {
            "participant_macro_margin": 0.10,
            "exact_one_sided_paired_sign_flip_p": 0.05,
        }
        c_summary = {
            "participant_macro_margin": 0.02,
            "exact_one_sided_paired_sign_flip_p": 0.05,
        }
        a_summary = dict(c_summary)
        if not all(_gate_components(task, primary, b_summary, c_summary, a_summary).values()):
            raise UG1ScoreRefusal("threshold", "inclusive gate boundary did not pass")
        mutations = (
            (primary, "event_count", 224),
            (primary, "pooled_balanced_accuracy", 0.60 - 2e-12),
            (primary, "participant_macro_balanced_accuracy", 0.60 - 2e-12),
            (primary, "participants_strictly_above_chance", 10),
            (
                primary,
                "exact_one_sided_sign_flip_p_against_chance",
                (0.01 if task == "execution" else 0.05) + 2e-12,
            ),
            (b_summary, "participant_macro_margin", 0.10 - 2e-12),
            (b_summary, "exact_one_sided_paired_sign_flip_p", 0.05 + 2e-12),
            (c_summary, "participant_macro_margin", 0.02 - 2e-12),
            (c_summary, "exact_one_sided_paired_sign_flip_p", 0.05 + 2e-12),
            (a_summary, "participant_macro_margin", 0.02 - 2e-12),
            (a_summary, "exact_one_sided_paired_sign_flip_p", 0.05 + 2e-12),
        )
        for mapping, field, value in mutations:
            original = mapping[field]
            mapping[field] = value
            if all(_gate_components(task, primary, b_summary, c_summary, a_summary).values()):
                raise UG1ScoreRefusal("threshold", f"fail-side boundary passed: {task}/{field}")
            mapping[field] = original
            failure_cases += 1
    return {"inclusive_pass_cases": 2, "exclusive_fail_cases": failure_cases}


def _task_score(
    task: str,
    *,
    targets_by_identity: Mapping[tuple[str, str, int, int], str],
    prediction_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    metrics: dict[str, dict[str, Any]] = {}
    participant_scores: dict[str, list[float]] = {}
    for condition in CONDITION_IDS:
        metric, scores = _condition_metrics(
            targets_by_identity=targets_by_identity,
            prediction_rows=prediction_rows,
            task=task,
            condition=condition,
        )
        metrics[condition] = metric
        participant_scores[condition] = scores
    primary_scores = participant_scores["primary_whole_head"]
    b_summary = _paired_control_summary(
        primary_scores,
        [
            participant_scores["equal_prior_no_signal"],
            participant_scores["timing_only"],
        ],
    )
    c_summary = _paired_control_summary(
        primary_scores,
        [
            participant_scores["exact_zero"],
            participant_scores["fixed_channel_permutation"],
            participant_scores["nonwrapping_event_displacement"],
            participant_scores["fixed_source_label_derangement"],
        ],
    )
    a_summary = _paired_control_summary(
        primary_scores,
        [
            participant_scores["pre_cue"],
            participant_scores["early_cue"],
            participant_scores["central_view"],
            participant_scores["frontal_view"],
            participant_scores["occipital_view"],
        ],
    )
    primary = metrics["primary_whole_head"]
    components = _gate_components(task, primary, b_summary, c_summary, a_summary)
    return {
        "passed": all(components.values()),
        "gate_components": components,
        "primary_metrics": primary,
        "B_i_comparison": b_summary,
        "C_i_comparison": c_summary,
        "A_i_comparison": a_summary,
        "condition_metrics": metrics,
    }


def score_frozen_predictions(
    *,
    freeze: Mapping[str, Any],
    prediction_payload: bytes,
    bindings: FreezeBindings,
    checkpoint_verifier: Callable[[], Mapping[str, str]],
    sealed_target_loader: Callable[[], bytes],
    source_loso_execution_passed: bool,
) -> dict[str, Any]:
    """Verify frozen predictions, load sealed targets once, and score aggregates."""

    if type(source_loso_execution_passed) is not bool:
        raise UG1ScoreRefusal("source_gate", "source gate must be an exact boolean")
    if not source_loso_execution_passed:
        return {
            "schema_name": "neurodecodekit.eegmmidb_unseen_participant_aggregate_score",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "route": "EEGMMIDBUG1-R1",
            "source_loso_execution_passed": False,
            "sealed_target_loads": 0,
            "scoring_events": 0,
            "individual_participant_metrics_published": False,
        }
    if not callable(sealed_target_loader):
        raise UG1ScoreRefusal("target_firewall", "sealed target loader is not callable")
    if not callable(checkpoint_verifier):
        raise UG1ScoreRefusal("checkpoint_binding", "checkpoint verifier is not callable")

    prediction_rows = validate_prediction_freeze(
        freeze,
        prediction_payload,
        bindings=bindings,
    )
    try:
        observed_checkpoint_hashes = dict(checkpoint_verifier())
    except Exception as exc:
        raise UG1ScoreRefusal("checkpoint_binding", "checkpoint verification failed") from exc
    if observed_checkpoint_hashes != dict(bindings.checkpoint_hashes):
        raise UG1ScoreRefusal("checkpoint_binding", "checkpoint hashes changed")
    try:
        target_payload = sealed_target_loader()
    except Exception as exc:
        raise UG1ScoreRefusal("target_delivery", "sealed target loader failed") from exc
    if not isinstance(target_payload, bytes):
        raise UG1ScoreRefusal("target_delivery", "sealed target loader did not return bytes")
    if _sha256(target_payload) != bindings.sealed_target_payload_sha256:
        raise UG1ScoreRefusal("target_hash", "sealed target payload hash differs")
    target_rows = _parse_canonical_jsonl(target_payload, kind="sealed targets")
    _validate_target_rows(target_rows)

    prediction_identity_metadata: dict[tuple[str, str, int, int], tuple[str, int]] = {}
    for row in prediction_rows:
        prediction_identity_metadata.setdefault(
            _identity_key(row), (str(row["opaque_row_id"]), int(row["cue_sample"]))
        )
    targets_by_identity: dict[tuple[str, str, int, int], str] = {}
    for row in target_rows:
        identity = _identity_key(row)
        if prediction_identity_metadata.get(identity) != (
            str(row["opaque_row_id"]),
            int(row["cue_sample"]),
        ):
            raise UG1ScoreRefusal("target_identity", "target and prediction identities differ")
        targets_by_identity[identity] = str(row["target"])
    if set(targets_by_identity) != set(prediction_identity_metadata):
        raise UG1ScoreRefusal("target_identity", "target identity inventory differs")

    execution = _task_score(
        "execution",
        targets_by_identity=targets_by_identity,
        prediction_rows=prediction_rows,
    )
    imagery = _task_score(
        "imagery",
        targets_by_identity=targets_by_identity,
        prediction_rows=prediction_rows,
    )
    route = route_ug1(
        integrity_passed=True,
        source_loso_execution_passed=True,
        final_score_available=True,
        execution_passed=bool(execution["passed"]),
        imagery_passed=bool(imagery["passed"]),
    )
    return {
        "schema_name": "neurodecodekit.eegmmidb_unseen_participant_aggregate_score",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "scored_once_frozen_router_applied",
        "route": route,
        "source_loso_execution_passed": True,
        "execution": execution,
        "imagery": imagery,
        "sealed_target_rows": 450,
        "sealed_target_loads": 1,
        "scoring_events": 1,
        "post_target_updates": 0,
        "individual_participant_metrics_published": False,
        "warnings": [
            "visual_cue_and_ocular_compatibility_remain",
            "no_EOG_comparator_is_available",
            "movement_intention_and_motor_cortex_origin_are_not_established",
            "language_live_hardware_and_clinical_claims_are_not_established",
        ],
    }
