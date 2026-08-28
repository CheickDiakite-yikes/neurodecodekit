"""Generated-only COMM-P0-G prospective communication qualification core.

This module represents the frozen prospective protocol without touching a person,
device, network, or real/private path.  The official two-replay qualification is
deliberately activation-locked; the reusable validators and deterministic fixture
builders are available for bounded implementation tests.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Any

from neurodecodekit.streaming.source_chunk import SourceBindings

CONTRACT_PATH = Path(
    "registries/communication_eeg_prospective_generated_qualification_contract.v0.json"
)
CONTRACT_SHA256 = "a3f7ddbe763186e0618cf7e4d1f9b34ec87204fb91ac7c25db160a9d716f2910"
ACTIVATION_PATH = Path(
    "registries/communication_eeg_prospective_generated_qualification_activation.v0.json"
)
GATE_ID = "COMM-P0-G-v0"
SCHEMA_VERSION = "0.1.0"
COMMANDS = ("yes", "no", "help", "stop")
COHORTS = ("discovery", "independent_replication")
ENDPOINTS = ("prompted_intend", "free_choice_intend")
TRIAL_ROLE_COUNTS = {
    "prompted_intend": 64,
    "prompted_no_intent": 32,
    "free_choice_intend": 64,
    "free_choice_no_intent": 32,
    "rest": 32,
    "peripheral_calibration": 32,
}
FORBIDDEN_TARGET_KEYS = frozenset(
    {
        "answer",
        "class_label",
        "intended_command",
        "intended_text",
        "label",
        "reference_text",
        "target",
        "target_key",
        "target_value",
    }
)


class CommP0GeneratedRefusal(RuntimeError):
    """Fail-closed generated qualification refusal with an exact family id."""

    def __init__(self, family: str, detail: str = "") -> None:
        self.family = family
        message = f"COMM-P0-G:{family}"
        if detail:
            message = f"{message}:{detail}"
        super().__init__(message)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def canonical_json_bytes(value: Any) -> bytes:
    """Return the registered compact canonical JSON encoding."""

    try:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CommP0GeneratedRefusal(
            "nondeterministic_fixture_prediction_or_freeze_replay", str(exc)
        ) from exc
    return (payload + "\n").encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_contract(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    path = repository / CONTRACT_PATH
    if _file_sha256(path) != CONTRACT_SHA256:
        raise CommP0GeneratedRefusal("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("gate_id") != GATE_ID:
        raise CommP0GeneratedRefusal("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    return value


def assert_target_free(value: Any, path: str = "$") -> None:
    """Reject recursively target-bearing decoder capability surfaces."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_TARGET_KEYS or normalized.endswith("_target"):
                raise CommP0GeneratedRefusal(
                    "recursive_target_label_reference_key_leakage", f"{path}.{key}"
                )
            assert_target_free(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            assert_target_free(child, f"{path}[{index}]")


@dataclass(frozen=True, slots=True)
class ParticipantPlan:
    cohort_id: str
    participant_id: str
    enrolled_index: int
    complete: bool
    exclusion_reason: str | None


@dataclass(frozen=True, slots=True)
class TrialPlan:
    item_id: str
    cohort_id: str
    participant_id: str
    session_id: str
    trial_index: int
    role: str
    endpoint: str | None
    phase: str
    cue_code: int | None
    washout_seconds: int
    duration_seconds: int
    segment_index: int
    intention_window_start_seconds: float
    intention_window_stop_seconds: float
    target_commitment_sha256: str | None

    def public_record(self) -> dict[str, Any]:
        value = asdict(self)
        assert_target_free(value)
        return value


def participant_plans(contract: Mapping[str, Any]) -> tuple[ParticipantPlan, ...]:
    spec = contract["fictional_cohorts"]
    enrolled = int(spec["enrolled_participants_per_cohort"])
    plans: list[ParticipantPlan] = []
    for cohort_index, cohort in enumerate(COHORTS):
        for index in range(enrolled):
            complete = index < int(spec["complete_participants_per_cohort"])
            participant_id = f"P0-{cohort_index + 1}-{index + 1:02d}"
            plans.append(
                ParticipantPlan(
                    cohort_id=cohort,
                    participant_id=participant_id,
                    enrolled_index=index,
                    complete=complete,
                    exclusion_reason=None if complete else "generated_hardware_exclusion",
                )
            )
    if len(plans) != int(spec["enrolled_participants_total"]):
        raise CommP0GeneratedRefusal("cohort_cardinality_or_replacement_rule_violation")
    identities = [plan.participant_id for plan in plans]
    if len(identities) != len(set(identities)):
        raise CommP0GeneratedRefusal("participant_identity_collision")
    return tuple(plans)


class GeneratedTargetVault:
    """Fixed-size generated target commitments with one delivery per cohort."""

    def __init__(self, secret: bytes) -> None:
        if len(secret) < 32:
            raise CommP0GeneratedRefusal("target_vault_key_capability_escape")
        self.__secret = bytes(secret)
        self.__targets: dict[str, dict[str, int]] = defaultdict(dict)
        self.__commitments: dict[str, str] = {}
        self.__delivered: set[str] = set()

    def precommit(self, cohort_id: str, item_id: str, command_index: int) -> str:
        if cohort_id not in COHORTS or command_index not in range(len(COMMANDS)):
            raise CommP0GeneratedRefusal("free_choice_target_before_precommit")
        if item_id in self.__commitments:
            raise CommP0GeneratedRefusal("free_choice_target_before_precommit")
        message = f"{cohort_id}\0{item_id}\0{command_index}".encode()
        commitment = hmac.new(self.__secret, message, hashlib.sha256).hexdigest()
        self.__targets[cohort_id][item_id] = command_index
        self.__commitments[item_id] = commitment
        return commitment

    def commitment(self, item_id: str) -> str:
        try:
            return self.__commitments[item_id]
        except KeyError as exc:
            raise CommP0GeneratedRefusal("free_choice_target_before_precommit") from exc

    def source_targets(self, cohort_id: str, allowed_item_ids: Iterable[str]) -> dict[str, int]:
        """Deliver only explicitly capability-bound source targets."""

        source = self.__targets.get(cohort_id, {})
        requested = tuple(allowed_item_ids)
        if any(item_id not in source for item_id in requested):
            raise CommP0GeneratedRefusal("scorer_prediction_target_row_mismatch")
        return {item_id: source[item_id] for item_id in requested}

    def deliver_for_score(
        self,
        cohort_id: str,
        *,
        prediction_freeze_green: bool,
        replication_artifact_freeze_green: bool,
    ) -> dict[str, int]:
        if not prediction_freeze_green:
            raise CommP0GeneratedRefusal("pre_freeze_target_delivery")
        if cohort_id == "independent_replication" and not replication_artifact_freeze_green:
            raise CommP0GeneratedRefusal("replication_prediction_freeze_not_green_before_delivery")
        if cohort_id in self.__delivered:
            raise CommP0GeneratedRefusal("repeated_score_or_target_delivery")
        self.__delivered.add(cohort_id)
        return dict(self.__targets[cohort_id])

    def public_summary(self) -> dict[str, Any]:
        value = {
            "cohorts": list(COHORTS),
            "commitment_count": len(self.__commitments),
            "fixed_commitment_hex_characters": 64,
            "commitment_set_sha256": sha256_json(sorted(self.__commitments.values())),
            "target_values_exposed": False,
            "deliveries": len(self.__delivered),
        }
        assert_target_free(value)
        return value


def _role_sequence() -> tuple[str, ...]:
    remaining = Counter(TRIAL_ROLE_COUNTS)
    ordered_roles = sorted(
        remaining,
        key=lambda role: hashlib.sha256(f"20260827:{role}".encode()).digest(),
    )
    roles: list[str] = []
    while remaining:
        for role in ordered_roles:
            if remaining.get(role, 0):
                roles.append(role)
                remaining[role] -= 1
                if remaining[role] == 0:
                    del remaining[role]
    return tuple(roles)


def _command_for(participant_id: str, trial_index: int, role: str) -> int:
    payload = f"{participant_id}:{trial_index}:{role}:20260827".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big") % len(COMMANDS)


def _phase_for(role: str, role_index: int) -> str:
    if role == "peripheral_calibration":
        return "calibration"
    return "shadow" if role_index % 2 == 0 else "live"


def generate_trial_plan(
    contract: Mapping[str, Any], vault: GeneratedTargetVault
) -> tuple[TrialPlan, ...]:
    """Generate the complete target-firewalled 42-person structural plan."""

    grammar = contract["trial_grammar"]
    schedule = grammar["timing_schedule"]
    complete = [plan for plan in participant_plans(contract) if plan.complete]
    washouts: list[int] = []
    for seconds, count in schedule["free_choice_washout_seconds_counts"].items():
        washouts.extend([int(seconds)] * int(count))
    rows: list[TrialPlan] = []
    role_template = _role_sequence()
    for participant in complete:
        role_seen: Counter[str] = Counter()
        free_choice_seen = 0
        elapsed = 0.0
        padding_remaining = float(schedule["fixed_sync_warmup_and_segment_padding_seconds"])
        for trial_index, role in enumerate(role_template):
            role_index = role_seen[role]
            role_seen[role] += 1
            endpoint = role if role in ENDPOINTS else None
            command_index = _command_for(participant.participant_id, trial_index, role)
            phase = _phase_for(role, role_index)
            if role.startswith("free_choice"):
                washout = washouts[free_choice_seen]
                free_choice_seen += 1
            else:
                washout = 0
            if role.startswith("free_choice"):
                duration = washout + int(
                    schedule["free_choice_post_washout_intention_and_ITI_seconds"]
                )
            elif role.startswith("prompted"):
                duration = int(schedule["prompted_row_seconds"])
            elif role == "rest":
                duration = int(schedule["rest_row_seconds"])
            else:
                duration = int(schedule["peripheral_calibration_row_seconds"])
            item_id = f"{participant.participant_id}-trial-{trial_index:03d}"
            commitment = None
            if role.startswith("free_choice"):
                commitment = vault.precommit(participant.cohort_id, item_id, command_index)
            cue_code = command_index if role.startswith("prompted") else None
            intention_start = elapsed + washout
            intention_stop = elapsed + duration
            if endpoint is not None:
                segment_stop = (math.floor(intention_start / 120.0) + 1.0) * 120.0
                if intention_stop > segment_stop and segment_stop < 1650.0:
                    inserted_padding = segment_stop - elapsed
                    if inserted_padding < 0.0 or inserted_padding > padding_remaining:
                        raise CommP0GeneratedRefusal("active_trial_may_cross_segment_boundary")
                    elapsed += inserted_padding
                    padding_remaining -= inserted_padding
                    intention_start = elapsed + washout
                    intention_stop = elapsed + duration
            segment_index = min(int(intention_start // 120), 13)
            rows.append(
                TrialPlan(
                    item_id=item_id,
                    cohort_id=participant.cohort_id,
                    participant_id=participant.participant_id,
                    session_id=f"{participant.cohort_id}-session-1",
                    trial_index=trial_index,
                    role=role,
                    endpoint=endpoint,
                    phase=phase,
                    cue_code=cue_code,
                    washout_seconds=washout,
                    duration_seconds=duration,
                    segment_index=segment_index,
                    intention_window_start_seconds=intention_start,
                    intention_window_stop_seconds=intention_stop,
                    target_commitment_sha256=commitment,
                )
            )
            elapsed += duration
        if role_seen != Counter(TRIAL_ROLE_COUNTS):
            raise CommP0GeneratedRefusal(
                "required_control_condition_missing_duplicated_or_substituted"
            )
        elapsed += padding_remaining
        if not math.isclose(elapsed, float(schedule["total_session_seconds"])):
            raise CommP0GeneratedRefusal("trial_or_block_boundary_oracle_use")
    validate_trial_plan(rows, contract)
    return tuple(rows)


def validate_trial_plan(rows: Sequence[TrialPlan], contract: Mapping[str, Any]) -> None:
    expected = int(contract["trial_grammar"]["complete_structural_rows_per_replay"])
    if len(rows) != expected:
        raise CommP0GeneratedRefusal("cohort_cardinality_or_replacement_rule_violation")
    item_ids = [row.item_id for row in rows]
    if len(item_ids) != len(set(item_ids)):
        raise CommP0GeneratedRefusal("participant_identity_collision")
    by_participant: dict[str, list[TrialPlan]] = defaultdict(list)
    for row in rows:
        assert_target_free(row.public_record())
        if row.washout_seconds and row.washout_seconds not in range(6, 11):
            raise CommP0GeneratedRefusal("post_washout_context_limit_breach")
        if row.intention_window_stop_seconds <= row.intention_window_start_seconds:
            raise CommP0GeneratedRefusal("source_timestamp_nonfinite_regression_or_clock_reset")
        if row.endpoint is not None:
            first_segment = int(row.intention_window_start_seconds // 120)
            final_segment = int((row.intention_window_stop_seconds - 1e-12) // 120)
            if first_segment != final_segment:
                raise CommP0GeneratedRefusal("active_trial_may_cross_segment_boundary")
        by_participant[row.participant_id].append(row)
    for participant_rows in by_participant.values():
        counts = Counter(row.role for row in participant_rows)
        if counts != Counter(TRIAL_ROLE_COUNTS):
            raise CommP0GeneratedRefusal(
                "required_control_condition_missing_duplicated_or_substituted"
            )


def _eeg_roles(contract: Mapping[str, Any]) -> tuple[str, ...]:
    adapter = contract["synchronized_sensor_adapter"]
    frozen = list(adapter["central_EEG_roles"]) + list(adapter["posterior_EEG_roles"])
    reserved = set(frozen)
    for index in range(1, 65):
        candidate = f"EEG_{index:02d}"
        if candidate not in reserved:
            frozen.append(candidate)
        if len(frozen) == 64:
            break
    if len(frozen) != 64 or len(set(frozen)) != 64:
        raise CommP0GeneratedRefusal("channel_count_name_or_order_drift")
    return tuple(frozen)


def build_sensor_bundle(
    contract: Mapping[str, Any], participant: ParticipantPlan, segment_index: int
) -> dict[str, Any]:
    adapter = contract["synchronized_sensor_adapter"]
    if segment_index not in range(int(adapter["segments_per_participant"])):
        raise CommP0GeneratedRefusal("source_sample_overlap_reorder_or_hidden_gap")
    eeg_roles = _eeg_roles(contract)
    peripheral = (
        "EOG_L",
        "EOG_R",
        "EOG_U",
        "EOG_D",
        "EMG_LL",
        "EMG_LR",
        "EMG_RL",
        "EMG_RR",
        "PHOTODIODE",
    )
    roles_by_shard = (eeg_roles[:32], eeg_roles[32:], peripheral)
    shard_ids = ("EEG_A", "EEG_B", "PERIPHERAL")
    sample_count = 120 * 512 if segment_index < 13 else 90 * 512
    sample_axis = {
        "sampling_rate_hz": 512,
        "first_source_sample_index": segment_index * 120 * 512,
        "sample_count": sample_count,
        "reconnect_generation": 0,
    }
    sample_axis_sha256 = sha256_json(sample_axis)
    geometry_sha256 = sha256_json(
        {role: [index, index % 9, (index * 7) % 13] for index, role in enumerate(eeg_roles)}
    )
    clock_ledger_sha256 = sha256_json(
        {"mapping": "generated_identity", "uncertainty_p99_seconds": 0.0005}
    )
    gap_ledger_sha256 = sha256_json({"gaps": [], "reconnects": []})
    shards = []
    for shard_id, roles in zip(shard_ids, roles_by_shard, strict=True):
        types = tuple("EEG" if shard_id.startswith("EEG") else role.split("_")[0] for role in roles)
        bindings = SourceBindings.generated(
            channel_names=roles,
            channel_types=types,
            channel_units=tuple("uV" for _ in roles),
            nominal_sampling_rate_hz=512.0,
            seed=f"{participant.participant_id}:{segment_index}:{shard_id}",
            modality="synthetic_eeg" if shard_id.startswith("EEG") else "synthetic_peripheral",
            device_type="generated_synchronized_fixture",
        )
        shards.append(
            {
                "shard_id": shard_id,
                "channel_names": list(roles),
                "bindings_sha256": bindings.sha256,
                "sample_axis_sha256": sample_axis_sha256,
                "geometry_sha256": geometry_sha256,
                "clock_ledger_sha256": clock_ledger_sha256,
                "gap_reconnect_ledger_sha256": gap_ledger_sha256,
            }
        )
    identity = {
        "cohort_id": participant.cohort_id,
        "participant_id": participant.participant_id,
        "session_id": f"{participant.cohort_id}-session-1",
        "segment_index": segment_index,
        "reconnect_generation": 0,
    }
    bundle = {
        **identity,
        "bundle_id": sha256_json(identity)[:24],
        "channel_role_map_sha256": sha256_json([list(row) for row in roles_by_shard]),
        "geometry_sha256": geometry_sha256,
        "sample_axis_sha256": sample_axis_sha256,
        "clock_ledger_sha256": clock_ledger_sha256,
        "gap_reconnect_ledger_sha256": gap_ledger_sha256,
        "shards": shards,
        "microphone": {
            "schema": "mono_PCM16_16000_Hz_shared_clock_map_required",
            "clock_ledger_sha256": clock_ledger_sha256,
        },
        "hardware_trigger": {
            "schema": "integer_hardware_trigger_timestamped_on_shared_clock_map",
            "clock_ledger_sha256": clock_ledger_sha256,
        },
        "LSL_clock_uncertainty_p99_seconds": 0.0005,
        "hardware_residual_p99_samples": 1,
    }
    bundle["bundle_sha256"] = sha256_json(bundle)
    validate_sensor_bundle(bundle, contract)
    return bundle


def validate_sensor_bundle(bundle: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    adapter = contract["synchronized_sensor_adapter"]
    atomic = adapter["atomic_bundle"]
    required = set(atomic["required_identity_fields"] + atomic["required_hash_fields"])
    if not required.issubset(bundle):
        raise CommP0GeneratedRefusal("microphone_trigger_or_photodiode_binding_missing")
    shards = bundle.get("shards")
    if not isinstance(shards, list) or [row.get("shard_id") for row in shards] != [
        "EEG_A",
        "EEG_B",
        "PERIPHERAL",
    ]:
        raise CommP0GeneratedRefusal("channel_count_name_or_order_drift")
    expected_counts = [32, 32, 9]
    if [len(row.get("channel_names", ())) for row in shards] != expected_counts:
        raise CommP0GeneratedRefusal("channel_count_name_or_order_drift")
    for field in (
        "sample_axis_sha256",
        "geometry_sha256",
        "clock_ledger_sha256",
        "gap_reconnect_ledger_sha256",
    ):
        if any(row.get(field) != bundle.get(field) for row in shards):
            raise CommP0GeneratedRefusal("correction_ledger_tamper")
    if bundle.get("microphone", {}).get("clock_ledger_sha256") != bundle.get("clock_ledger_sha256"):
        raise CommP0GeneratedRefusal("cross_clock_mapping_missing_or_unverified")
    if bundle.get("hardware_trigger", {}).get("clock_ledger_sha256") != bundle.get(
        "clock_ledger_sha256"
    ):
        raise CommP0GeneratedRefusal("cross_clock_mapping_missing_or_unverified")
    if float(bundle.get("LSL_clock_uncertainty_p99_seconds", math.inf)) > float(
        atomic["LSL_clock_uncertainty_p99_seconds_maximum"]
    ):
        raise CommP0GeneratedRefusal("LSL_clock_uncertainty_cap_breach")
    if int(bundle.get("hardware_residual_p99_samples", 10**9)) > int(
        atomic["hardware_residual_p99_samples_maximum"]
    ):
        raise CommP0GeneratedRefusal("hardware_residual_cap_breach")
    supplied_hash = bundle.get("bundle_sha256")
    unhashed = dict(bundle)
    unhashed.pop("bundle_sha256", None)
    if supplied_hash != sha256_json(unhashed):
        raise CommP0GeneratedRefusal("correction_ledger_tamper")


def validate_probability_vector(probabilities: Sequence[float]) -> tuple[float, ...]:
    if len(probabilities) != len(COMMANDS):
        raise CommP0GeneratedRefusal("prediction_probability_nonfinite_or_sum_mismatch")
    values = tuple(float(value) for value in probabilities)
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise CommP0GeneratedRefusal("prediction_probability_nonfinite_or_sum_mismatch")
    if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise CommP0GeneratedRefusal("prediction_probability_nonfinite_or_sum_mismatch")
    return values


def build_prediction_freeze(
    rows: Iterable[Mapping[str, Any]], *, expected_rows: int, expected_sets: int
) -> dict[str, Any]:
    digest = hashlib.sha256()
    seen: set[tuple[str, str, str]] = set()
    count = 0
    participants: set[str] = set()
    conditions: set[str] = set()
    endpoints: set[str] = set()
    for row in rows:
        assert_target_free(row)
        item_id = str(row.get("item_id", ""))
        condition = str(row.get("condition", ""))
        endpoint = str(row.get("endpoint", ""))
        key = (item_id, condition, endpoint)
        if not item_id or not condition or endpoint not in ENDPOINTS or key in seen:
            raise CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
        seen.add(key)
        validate_probability_vector(row.get("probabilities", ()))
        participants.add(str(row.get("participant_id", "")))
        conditions.add(condition)
        endpoints.add(endpoint)
        digest.update(canonical_json_bytes(dict(row)))
        count += 1
    if count != expected_rows:
        raise CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
    if len(participants) * len(conditions) * len(endpoints) != expected_sets:
        raise CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "prediction_rows": count,
        "prediction_sets": expected_sets,
        "private_prediction_stream_sha256": digest.hexdigest(),
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
    }


def _percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return math.inf
    ordered = sorted(float(value) for value in values)
    rank = max(0, math.ceil(quantile * len(ordered)) - 1)
    return ordered[rank]


def summarize_live_records(
    records: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> dict[str, Any]:
    live = contract["live_metrics"]
    active = [row for row in records if row.get("active_intent") is True]
    inactive = [row for row in records if row.get("active_intent") is False]
    if not active:
        raise CommP0GeneratedRefusal("live_required_metric_missing")
    participant_ids = sorted({str(row["participant_id"]) for row in active})
    per_participant = []
    per_command: dict[str, list[bool]] = defaultdict(list)
    latencies: list[float] = []
    overheads: list[float] = []
    deadlines = 0
    drops = 0
    for participant_id in participant_ids:
        rows = [row for row in active if row["participant_id"] == participant_id]
        committed = [
            bool(row.get("stable_commit")) and not bool(row.get("invalid")) for row in rows
        ]
        per_participant.append(sum(committed) / len(rows))
    for row in active:
        committed = bool(row.get("stable_commit")) and not bool(row.get("invalid"))
        per_command[str(row["command"])].append(committed)
        drops += int(bool(row.get("invalid")))
        deadlines += int(bool(row.get("processed_before_deadline")))
        if committed:
            if row.get("clock_map_verified") is not True:
                raise CommP0GeneratedRefusal(
                    "capture_to_presentation_overhead_or_clock_map_failure"
                )
            latencies.append(float(row["stable_commit_latency_seconds"]))
            overheads.append(float(row["capture_to_presentation_overhead_seconds"]))
    inactive_seconds = sum(float(row.get("duration_seconds", 0.0)) for row in inactive)
    false_commits = sum(int(row.get("commit_count", 0)) for row in inactive)
    summary = {
        "participant_macro_coverage": sum(per_participant) / len(per_participant),
        "per_command_coverage": {
            command: sum(values) / len(values) for command, values in sorted(per_command.items())
        },
        "false_commits_per_inactive_minute": (
            false_commits / (inactive_seconds / 60.0) if inactive_seconds else math.inf
        ),
        "dropped_or_invalid_chunk_fraction": drops / len(active),
        "frames_processed_before_next_deadline_fraction": deadlines / len(active),
        "stable_commit_latency_median_seconds": median(latencies) if latencies else math.inf,
        "stable_commit_latency_p95_seconds": _percentile(latencies, 0.95),
        "capture_to_presentation_processing_overhead_p95_seconds": _percentile(overheads, 0.95),
        "noncommits_retained": sum(not bool(row.get("stable_commit")) for row in active),
    }
    if summary["participant_macro_coverage"] < live["stable_commit_coverage_fraction_minimum"]:
        raise CommP0GeneratedRefusal("stable_commit_or_per_command_coverage_below_minimum")
    if any(
        value < live["per_command_coverage_fraction_minimum"]
        for value in summary["per_command_coverage"].values()
    ):
        raise CommP0GeneratedRefusal("stable_commit_or_per_command_coverage_below_minimum")
    if (
        summary["false_commits_per_inactive_minute"]
        > live["false_commits_per_inactive_minute_maximum"]
    ):
        raise CommP0GeneratedRefusal("false_commit_or_chatter_rate_above_maximum")
    if (
        summary["dropped_or_invalid_chunk_fraction"]
        > live["dropped_or_invalid_chunk_fraction_maximum"]
        or summary["frames_processed_before_next_deadline_fraction"]
        < live["frames_processed_before_next_deadline_fraction_minimum"]
    ):
        raise CommP0GeneratedRefusal("dropped_invalid_or_deadline_gate_failure")
    if (
        summary["stable_commit_latency_median_seconds"]
        > live["stable_commit_latency_median_seconds_maximum"]
        or summary["stable_commit_latency_p95_seconds"]
        > live["stable_commit_latency_p95_seconds_maximum"]
    ):
        raise CommP0GeneratedRefusal("stable_commit_latency_median_or_p95_above_maximum")
    if (
        summary["capture_to_presentation_processing_overhead_p95_seconds"]
        > live["capture_to_presentation_processing_overhead_p95_seconds_maximum"]
    ):
        raise CommP0GeneratedRefusal("capture_to_presentation_overhead_or_clock_map_failure")
    return summary


def exact_one_sided_sign_flip(values: Sequence[float]) -> tuple[float, int]:
    """Exhaustively enumerate signs in O(2**n) using Gray-code updates."""

    rounded = [round(float(value), 12) for value in values]
    if not rounded or len(rounded) > 21:
        raise CommP0GeneratedRefusal("pooled_result_or_other_cohort_rescues_failed_cohort")
    observed = sum(rounded) / len(rounded)
    signed_sum = -sum(rounded)
    extreme = int(signed_sum / len(rounded) >= observed - 1e-12)
    previous_gray = 0
    assignments = 1 << len(rounded)
    for assignment in range(1, assignments):
        gray = assignment ^ (assignment >> 1)
        changed = gray ^ previous_gray
        bit = changed.bit_length() - 1
        if gray & changed:
            signed_sum += 2.0 * rounded[bit]
        else:
            signed_sum -= 2.0 * rounded[bit]
        extreme += int(signed_sum / len(rounded) >= observed - 1e-12)
        previous_gray = gray
    return extreme / assignments, assignments


def participant_first_summary(
    participant_metrics: Mapping[str, Mapping[str, float]], contract: Mapping[str, Any]
) -> dict[str, Any]:
    spec = contract["participant_first_scoring"]
    if len(participant_metrics) != spec["complete_participants_denominator"]:
        raise CommP0GeneratedRefusal("cohort_cardinality_or_replacement_rule_violation")
    margins = []
    accuracy_margins = []
    for participant_id in sorted(participant_metrics):
        row = participant_metrics[participant_id]
        margin = min(
            float(row["LL_P"]) - float(row["LL_P_plus_EEG"]),
            float(row["LL_P_plus_deranged_EEG"]) - float(row["LL_P_plus_EEG"]),
        )
        margins.append(round(margin, int(spec["participant_metric_decimal_places"])))
        accuracy_margins.append(float(row["BA_P_plus_EEG"]) - float(row["BA_best_control"]))
    p_value, assignments = exact_one_sided_sign_flip(margins)
    summary = {
        "participant_count": len(margins),
        "mean_margin_nats_per_item": sum(margins) / len(margins),
        "positive_participants": sum(value > 0.0 for value in margins),
        "exact_one_sided_sign_flip_p": p_value,
        "sign_flip_assignments_evaluated": assignments,
        "mean_balanced_accuracy_margin": sum(accuracy_margins) / len(accuracy_margins),
    }
    summary["passes"] = bool(
        summary["mean_margin_nats_per_item"] >= spec["mean_margin_nats_per_item_minimum"]
        and summary["positive_participants"] >= spec["positive_participants_minimum"]
        and summary["exact_one_sided_sign_flip_p"] <= spec["exact_one_sided_sign_flip_p_maximum"]
        and summary["mean_balanced_accuracy_margin"] >= spec["balanced_accuracy_margin_minimum"]
    )
    return summary


def _transaction_state() -> dict[str, Any]:
    return {
        "fit_count": 0,
        "prediction_count": 0,
        "target_delivery_count": 0,
        "score_count": 0,
        "published": False,
        "temporary_paths": [],
    }


def exercise_refusal_families(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Exercise every exact refusal wrapper without mutating transaction state."""

    families = [
        family
        for rows in contract["adversarial_qualification"]["refusal_families"].values()
        for family in rows
    ]
    observations = []
    for family in families:
        state = _transaction_state()
        before = sha256_json(state)
        try:
            raise CommP0GeneratedRefusal(family)
        except CommP0GeneratedRefusal as exc:
            if exc.family != family or str(exc) != f"COMM-P0-G:{family}":
                raise CommP0GeneratedRefusal(
                    "nondeterministic_fixture_prediction_or_freeze_replay"
                ) from exc
            after = sha256_json(state)
            if after != before:
                raise CommP0GeneratedRefusal("post_score_mutation_repeat_or_output_replacement")
            observations.append(
                {
                    "family": family,
                    "wrapper": str(exc),
                    "pre_state_sha256": before,
                    "post_state_sha256": after,
                    "state_unchanged": True,
                }
            )
    if len(observations) != contract["adversarial_qualification"]["registered_refusal_families"]:
        raise CommP0GeneratedRefusal("required_control_condition_missing_duplicated_or_substituted")
    return observations


def canonical_replay_digest(surface: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    replay = contract["adversarial_qualification"]["canonical_replay_equivalence"]
    expected = set(replay["digest_fields"])
    if set(surface) != expected or any(
        not isinstance(surface[field], str) or len(surface[field]) != 64 for field in expected
    ):
        raise CommP0GeneratedRefusal("nondeterministic_fixture_prediction_or_freeze_replay")
    return sha256_json(dict(surface))


def plan(root: str | Path | None = None) -> dict[str, Any]:
    contract = load_contract(root)
    schedule = contract["numerical_schedule_per_replay"]
    adversarial = contract["adversarial_qualification"]
    resources = contract["resource_caps"]
    return {
        "gate_id": GATE_ID,
        "mode": "generated_engineering_only",
        "official_qualification_authorized_now": False,
        "real_or_private_data_allowed": False,
        "human_or_device_operation_allowed": False,
        "replays": adversarial["isolated_child_process_replays"],
        "complete_fictional_participants": contract["fictional_cohorts"][
            "complete_participants_total"
        ],
        "structural_rows_per_replay": contract["trial_grammar"][
            "complete_structural_rows_per_replay"
        ],
        "prediction_sets_per_replay": schedule["prediction_sets"],
        "prediction_rows_per_replay": schedule["prediction_rows"],
        "refusal_families_per_replay": adversarial["registered_refusal_families"],
        "CPU_threads": resources["CPU_threads"],
        "wall_time_seconds": resources["wall_time_seconds"],
        "peak_process_tree_RSS_bytes": resources["peak_process_tree_RSS_bytes"],
        "network_bytes": resources["network_bytes"],
        "claim_boundary": contract["claim_boundary"],
        "warnings": [
            "fictional procedural signals only",
            "not an official qualification result",
            "not scientific evidence",
            "official execution requires a separate exact green activation",
        ],
    }


def run_generated_qualification(
    output: str | Path, *, root: str | Path | None = None
) -> dict[str, Any]:
    """Fail closed until a future exact implementation activation is green."""

    repository = Path(root) if root is not None else _repo_root()
    load_contract(repository)
    if not (repository / ACTIVATION_PATH).is_file():
        raise CommP0GeneratedRefusal("score_before_exact_green_freeze")
    raise CommP0GeneratedRefusal(
        "protocol_model_threshold_vocabulary_prior_or_code_hash_drift",
        "activation schema is not implemented in this milestone",
    )


def inspect_result(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file():
        raise CommP0GeneratedRefusal("filesystem_capability_publication_or_cleanup_escape")
    payload = candidate.read_bytes()
    value = json.loads(payload)
    assert_target_free(value)
    return {
        "path_name": candidate.name,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "schema_name": value.get("schema_name"),
        "gate_id": value.get("gate_id"),
        "claim_boundary": value.get("claim_boundary"),
        "warnings": value.get("warnings", []),
    }
