"""Generated-only qualification for the frozen COMM-R0 replication protocol."""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import multiprocessing
import os
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_g1_generated as g1
from neurodecodekit.experiments import comm_g2_generated_proof as g2

LANE_ID = "COMM-R0-G"
REGISTRATION_ID = "COMM-R0-REPLICATION-v0"
SOURCE_ID = "generated-full-control-fixture-v0"
CONTRACT_PATH = Path("registries/communication_eeg_independent_replication_contract.v0.json")
CONTRACT_SHA256 = "2f04ff2d6ea427c490807460a79baaa1d4f5a30f27d88ce90519806eed53d579"
PROOF_PATH = Path("registries/communication_eeg_independent_replication_proof.v0.json")
PROOF_SHA256 = "63a64cde8f3cee9662a5a63390e7b7ceaccc673da27b9370dc86ab3226cbf32e"
ACTIVATION_PATH = Path(
    "registries/communication_eeg_independent_replication_generated_activation.v0.json"
)
ACTIVATION_PROOF_PATH = Path(
    "registries/communication_eeg_independent_replication_generated_activation_proof.v0.json"
)
RESULT_PATH = Path(
    "registries/communication_eeg_independent_replication_generated_result.v0.json"
)

PARTICIPANTS = tuple(f"rsub-{index:02d}" for index in range(1, 13))
NEURAL_CONDITIONS = (
    "equal_prior",
    "source_class_prior",
    "cue_only",
    "timing_only",
    "EOG_only",
    "oral_EMG_only",
    "peripheral_context_P",
    "selected_central_EEG_only",
    "posterior_EEG_only",
    "P_plus_residual_EEG",
    "P_plus_class_destroyed_residual_EEG",
)
LANGUAGE_CONDITIONS = (
    "language_only",
    "neural_only",
    "neural_plus_language",
    "item_deranged_neural_plus_language",
)
ALL_CONDITIONS = (*NEURAL_CONDITIONS, *LANGUAGE_CONDITIONS)
REQUIRED_REFUSALS = (
    "identity_mismatch",
    "split_leak",
    "target_leak",
    "future_sample_use",
    "channel_role_mismatch",
    "missing_required_control",
    "derangement_scope_mismatch",
    "prediction_tamper",
    "pre_freeze_target_delivery",
    "repeated_target_delivery",
    "output_clobber",
    "symlink_escape",
    "nondeterministic_replay",
    "output_cap_breach",
    "RSS_cap_breach",
    "timeout",
)
CAPS = {
    "wall_time_seconds": 300,
    "peak_process_tree_RSS_bytes": 805_306_368,
    "generated_input_bytes": 33_554_432,
    "private_output_bytes": 67_108_864,
    "temporary_disk_bytes": 134_217_728,
    "public_output_bytes": 1_048_576,
}


class CommR0GeneratedRefusal(RuntimeError):
    """A COMM-R0 generated qualification invariant failed closed."""


@dataclass(frozen=True)
class FoldCapability:
    held_out_participant: str
    source_rows: tuple[g1.GeneratedRow, ...]
    source_targets: Mapping[str, int]
    held_out_rows: tuple[g1.GeneratedRow, ...]


@dataclass
class OperationLedger:
    residualizer_fits: int = 0
    classifier_or_prior_fits: int = 0
    model_inference_runs: int = 0
    prediction_sets: int = 0
    prediction_rows: int = 0
    synthetic_target_deliveries: int = 0
    synthetic_scores: int = 0
    post_target_updates: int = 0
    provider_calls: int = 0


class SealedSyntheticTargetVault:
    """Hold generated held-out targets outside every prediction capability."""

    def __init__(self, targets: Mapping[str, int]) -> None:
        self.__targets = dict(targets)
        self.__committed_freeze: CommittedPredictionFreeze | None = None
        self.deliveries = 0

    def arm(
        self,
        predictions: Sequence[Mapping[str, Any]],
        freeze: Mapping[str, Any],
        neural_freeze: Mapping[str, Any],
    ) -> CommittedPredictionFreeze:
        if self.__committed_freeze is not None:
            raise CommR0GeneratedRefusal("R0G-REPEATED-FREEZE-ARM")
        if {str(row["item_id"]) for row in predictions} != set(self.__targets):
            raise CommR0GeneratedRefusal("R0G-FREEZE-TARGET-INVENTORY")
        committed = _commit_prediction_freeze(predictions, freeze, neural_freeze)
        self.__committed_freeze = committed
        return committed

    def deliver(self, freeze: CommittedPredictionFreeze | None) -> dict[str, int]:
        if freeze is None or freeze is not self.__committed_freeze:
            raise CommR0GeneratedRefusal("R0G-PRE-FREEZE-TARGET-DELIVERY")
        if self.deliveries:
            raise CommR0GeneratedRefusal("R0G-REPEATED-TARGET-DELIVERY")
        self.deliveries = 1
        return dict(self.__targets)

    def score_once(
        self,
        predictions: Sequence[Mapping[str, Any]],
        freeze: Mapping[str, Any],
        neural_freeze: Mapping[str, Any],
    ) -> dict[str, Any]:
        committed = self.arm(predictions, freeze, neural_freeze)
        targets = self.deliver(committed)
        return _score_predictions(predictions, targets, committed)


@dataclass(frozen=True)
class CommittedPredictionFreeze:
    payload: Mapping[str, Any]
    canonical_sha256: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_registration(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    contract_payload = (repository / CONTRACT_PATH).read_bytes()
    proof_payload = (repository / PROOF_PATH).read_bytes()
    if _sha256(contract_payload) != CONTRACT_SHA256:
        raise CommR0GeneratedRefusal("R0G-CONTRACT-HASH")
    if _sha256(proof_payload) != PROOF_SHA256:
        raise CommR0GeneratedRefusal("R0G-PROOF-HASH")
    contract = json.loads(contract_payload)
    proof = json.loads(proof_payload)
    if contract.get("registration_id") != REGISTRATION_ID:
        raise CommR0GeneratedRefusal("R0G-CONTRACT-ID")
    if not proof.get("green_registration_commit", {}).get("both_required_jobs_green"):
        raise CommR0GeneratedRefusal("R0G-PARENT-NOT-GREEN")
    if tuple(contract.get("conditions_full_control", ())) != NEURAL_CONDITIONS:
        raise CommR0GeneratedRefusal("R0G-CONDITION-INVENTORY")
    if tuple(contract.get("language_control_arms", ())) != LANGUAGE_CONDITIONS:
        raise CommR0GeneratedRefusal("R0G-LANGUAGE-INVENTORY")
    if tuple(contract.get("generated_qualification_required_refusals", ())) != REQUIRED_REFUSALS:
        raise CommR0GeneratedRefusal("R0G-REFUSAL-INVENTORY")
    if contract.get("authorization_state", {}).get("generated_implementation_or_qualification"):
        raise CommR0GeneratedRefusal("R0G-PARENT-AUTHORITY-MUTATED")
    return contract


def load_activation(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    path = repository / ACTIVATION_PATH
    if not path.is_file() or path.is_symlink():
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-ABSENT")
    activation = json.loads(path.read_bytes())
    if activation.get("schema_name") != (
        "neurodecodekit.communication_eeg_independent_replication_generated_activation"
    ):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-SCHEMA")
    authority = activation.get("authority", {})
    if authority.get("generated_qualification_invocations_maximum") != 1:
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-AUTHORITY")
    if not authority.get("generated_qualification"):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-AUTHORITY")
    forbidden = (
        "real_or_private_data",
        "network",
        "real_training_or_inference",
        "real_target_delivery_or_score",
        "provider",
        "stream_or_device",
        "release",
        "scientific_claim_upgrade",
    )
    if any(authority.get(key) is not False for key in forbidden):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-SCOPE")
    if activation.get("result_path") != RESULT_PATH.as_posix():
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-RESULT-PATH")
    implementation_commit = activation.get("implementation_commit")
    if not isinstance(implementation_commit, str) or len(implementation_commit) != 40:
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-COMMIT")
    for artifact in activation.get("implementation_artifacts", ()):
        artifact_path = repository / str(artifact.get("path", ""))
        if not artifact_path.is_file() or artifact_path.is_symlink():
            raise CommR0GeneratedRefusal("R0G-ACTIVATION-ARTIFACT")
        if artifact_path.stat().st_size != artifact.get("bytes"):
            raise CommR0GeneratedRefusal("R0G-ACTIVATION-ARTIFACT")
        if _file_sha256(artifact_path) != artifact.get("sha256"):
            raise CommR0GeneratedRefusal("R0G-ACTIVATION-ARTIFACT")
    if len(activation.get("implementation_artifacts", ())) < 4:
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-ARTIFACT")
    if not activation.get("delayed_effect", {}).get("activation_commit_must_be_remotely_green"):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-DELAY")
    return activation


def load_activation_proof(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    activation = load_activation(repository)
    path = repository / ACTIVATION_PROOF_PATH
    if not path.is_file() or path.is_symlink():
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-PROOF-ABSENT")
    proof = json.loads(path.read_bytes())
    if proof.get("schema_name") != (
        "neurodecodekit.communication_eeg_independent_replication_generated_activation_proof"
    ):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-PROOF-SCHEMA")
    green = proof.get("green_activation_commit", {})
    if green.get("commit") != proof.get("activation_commit"):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-PROOF-COMMIT")
    if not green.get("both_required_jobs_green"):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-PROOF-NOT-GREEN")
    if proof.get("implementation_commit") != activation.get("implementation_commit"):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-PROOF-IMPLEMENTATION")
    activation_payload = (repository / ACTIVATION_PATH).read_bytes()
    if proof.get("activation_sha256") != _sha256(activation_payload):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-PROOF-HASH")
    counters = proof.get("operation_counters", {})
    if any(value != 0 for value in counters.values()):
        raise CommR0GeneratedRefusal("R0G-ACTIVATION-PROOF-OPERATIONS")
    return proof


def assert_single_thread_environment() -> None:
    changed = [name for name in g1.THREAD_ENVIRONMENT if os.environ.get(name) != "1"]
    if changed:
        raise CommR0GeneratedRefusal(f"R0G-THREAD-ENV:{','.join(changed)}")


def _run_isolated(
    operation: Callable[..., Any],
    *args: Any,
    timeout_seconds: float,
    child_tempdir: str | Path,
) -> tuple[Any, dict[str, Any]]:
    """Run one clean child with parent-enforced timeout and bounded join."""

    context = multiprocessing.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    child_environment = g2._sanitized_child_environment()
    temporary_directory = Path(child_tempdir).absolute()
    descriptor = g2._assert_directory_capability(temporary_directory)
    os.close(descriptor)
    child_environment["TMPDIR"] = str(temporary_directory)
    process = context.Process(
        target=g2._child_entry,
        args=(send, operation, args, child_environment, True),
    )
    original_environment = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(child_environment)
        process.start()
    finally:
        os.environ.clear()
        os.environ.update(original_environment)
    send.close()
    started = time.monotonic()
    try:
        while not receive.poll(0.1):
            if time.monotonic() - started > timeout_seconds:
                g2._terminate_child(process, process_group=True)
                raise CommR0GeneratedRefusal("R0G-CHILD-TIMEOUT")
            if not process.is_alive() and not receive.poll():
                raise CommR0GeneratedRefusal("R0G-CHILD-EOF")
        message = receive.recv()
    except EOFError as exc:
        raise CommR0GeneratedRefusal("R0G-CHILD-EOF") from exc
    finally:
        receive.close()
    process.join(15)
    if process.is_alive():
        g2._terminate_child(process, process_group=True)
        raise CommR0GeneratedRefusal("R0G-CHILD-JOIN")
    if process.exitcode != 0 or not message.get("ok"):
        raise CommR0GeneratedRefusal(
            f"R0G-CHILD-FAILED:{message.get('error', process.exitcode)}"
        )
    return message["value"], {
        "runtime_seconds": time.monotonic() - started,
        "process_id": process.pid,
        "timeout_seconds": timeout_seconds,
    }


def _rename_generated_participants(
    rows: Sequence[g1.GeneratedRow], targets: Mapping[str, int]
) -> tuple[list[g1.GeneratedRow], dict[str, int]]:
    renamed_rows: list[g1.GeneratedRow] = []
    renamed_targets: dict[str, int] = {}
    participant_map = {
        source: destination
        for source, destination in zip(
            sorted({row.participant_id for row in rows}), PARTICIPANTS, strict=True
        )
    }
    for row in rows:
        participant = participant_map[row.participant_id]
        suffix = row.item_id.split("-", 2)[-1]
        item_id = f"{participant}-{suffix}"
        renamed_rows.append(
            replace(row, item_id=item_id, participant_id=participant, outer_fold_id=participant)
        )
        renamed_targets[item_id] = targets[row.item_id]
    return renamed_rows, renamed_targets


def generate_fixture(
    case_family: str = "residual_EEG_increment",
    *,
    participants: Sequence[str] = PARTICIPANTS,
) -> tuple[list[g1.GeneratedRow], dict[str, int], int]:
    if len(participants) < 2 or len(set(participants)) != len(participants):
        raise CommR0GeneratedRefusal("R0G-FIXTURE-PARTICIPANTS")
    source_ids = tuple(f"gsub-{index:02d}" for index in range(1, len(participants) + 1))
    rows, targets, input_bytes = g1.generate_fixture(case_family, participants=source_ids)
    if tuple(participants) == PARTICIPANTS:
        return (*_rename_generated_participants(rows, targets), input_bytes)
    renamed: list[g1.GeneratedRow] = []
    renamed_targets: dict[str, int] = {}
    mapping = dict(zip(source_ids, participants, strict=True))
    for row in rows:
        participant = mapping[row.participant_id]
        item_id = row.item_id.replace(row.participant_id, participant, 1)
        renamed.append(
            replace(row, item_id=item_id, participant_id=participant, outer_fold_id=participant)
        )
        renamed_targets[item_id] = targets[row.item_id]
    return renamed, renamed_targets, input_bytes


def validate_fixture(rows: Sequence[g1.GeneratedRow], *, expected_participants: int = 12) -> None:
    g1.validate_rows(rows)
    participants = sorted({row.participant_id for row in rows})
    if len(participants) != expected_participants:
        raise CommR0GeneratedRefusal("R0G-PARTICIPANT-COUNT")
    if len(rows) != expected_participants * 24:
        raise CommR0GeneratedRefusal("R0G-ROW-COUNT")
    expected_grid = {
        (participant, f"ses-{session}", repeat, target)
        for participant in participants
        for session in range(1, 4)
        for repeat in range(2)
        for target in range(4)
    }
    observed_grid = set()
    for row in rows:
        fields = row.trial_id.split("-")
        if len(fields) != 3:
            raise CommR0GeneratedRefusal("R0G-TRIAL-ID")
        observed_grid.add(
            (row.participant_id, row.session_id, row.repeat_index, int(fields[-1]))
        )
        if row.source_sample_stop > row.source_sample_start + row.true_length:
            raise CommR0GeneratedRefusal("R0G-FUTURE-SAMPLE")
    if observed_grid != expected_grid:
        raise CommR0GeneratedRefusal("R0G-GRID")


def causal_timing_record(row: g1.GeneratedRow) -> dict[str, Any]:
    """Make the offline oracle and sample-availability boundary explicit."""

    record = {
        "event_onset_seconds": row.source_time_start_seconds,
        "frozen_event_offset_seconds": 1.0,
        "decision_timestamp_seconds": row.source_time_stop_seconds,
        "feature_availability_timestamp_seconds": row.source_time_stop_seconds,
        "source_sample_start": row.source_sample_start,
        "source_sample_stop_exclusive": row.source_sample_stop,
        "required_left_context_seconds": 1.0,
        "right_context_seconds": 0.0,
        "trial_boundary_oracle_used": True,
        "continuous_or_live_claim_allowed": False,
    }
    if not math.isclose(
        record["decision_timestamp_seconds"],
        record["event_onset_seconds"] + record["frozen_event_offset_seconds"],
        abs_tol=1e-12,
    ):
        raise CommR0GeneratedRefusal("R0G-CAUSAL-OFFSET")
    if record["feature_availability_timestamp_seconds"] > record["decision_timestamp_seconds"]:
        raise CommR0GeneratedRefusal("R0G-FUTURE-SAMPLE")
    return record


def route_condition_inventory(
    *,
    has_eog: bool,
    has_oral_emg: bool,
) -> dict[str, Any]:
    """Return explicit route availability; missing sensors are never zero-filled."""

    if has_eog and has_oral_emg:
        return {
            "route": "full_control",
            "conditions": list(NEURAL_CONDITIONS),
            "unavailable_conditions": [],
            "available_nuisance_predictors": [
                "EOG",
                "bilateral_oral_EMG",
                "posterior_EEG",
                "cue",
                "timing",
            ],
            "full_peripheral_adjusted_claim_allowed": True,
        }
    unavailable = []
    available = ["posterior_EEG", "cue", "timing"]
    if not has_eog:
        unavailable.append("EOG_only")
    else:
        available.append("EOG")
    if not has_oral_emg:
        unavailable.append("oral_EMG_only")
    else:
        available.append("bilateral_oral_EMG")
    return {
        "route": "partial_control",
        "conditions": [
            condition for condition in NEURAL_CONDITIONS if condition not in set(unavailable)
        ],
        "unavailable_conditions": sorted(set(unavailable)),
        "available_nuisance_predictors": available,
        "full_peripheral_adjusted_claim_allowed": False,
    }


def qualify_route_contracts() -> list[dict[str, Any]]:
    cases = (
        ("full", True, True),
        ("missing_EOG", False, True),
        ("missing_oral_EMG", True, False),
        ("missing_EOG_and_oral_EMG", False, False),
    )
    results = []
    for case_id, has_eog, has_oral_emg in cases:
        route = route_condition_inventory(has_eog=has_eog, has_oral_emg=has_oral_emg)
        if route["route"] == "full_control":
            if route["conditions"] != list(NEURAL_CONDITIONS):
                raise CommR0GeneratedRefusal("R0G-FULL-ROUTE-INVENTORY")
        else:
            if route["full_peripheral_adjusted_claim_allowed"]:
                raise CommR0GeneratedRefusal("R0G-PARTIAL-CLAIM-UPGRADE")
            if any(
                condition in route["conditions"]
                for condition in route["unavailable_conditions"]
            ):
                raise CommR0GeneratedRefusal("R0G-PARTIAL-UNAVAILABLE-EMITTED")
            for required in (
                "peripheral_context_P",
                "P_plus_residual_EEG",
                "P_plus_class_destroyed_residual_EEG",
            ):
                if required not in route["conditions"]:
                    raise CommR0GeneratedRefusal("R0G-PARTIAL-CANDIDATE-ABSENT")
        results.append({"case_id": case_id, **route})
    return results


def canonical_fixture_digest(
    rows: Sequence[g1.GeneratedRow], targets: Mapping[str, int]
) -> str:
    validate_fixture(rows, expected_participants=len({row.participant_id for row in rows}))
    if set(targets) != {row.item_id for row in rows}:
        raise CommR0GeneratedRefusal("R0G-TARGET-INVENTORY")
    np = g1._np()
    digest = hashlib.sha256()
    for row in rows:
        metadata = {
            "item_id": row.item_id,
            "participant_id": row.participant_id,
            "session_id": row.session_id,
            "trial_id": row.trial_id,
            "repeat_index": row.repeat_index,
            "outer_fold_id": row.outer_fold_id,
            "source_sample_start": row.source_sample_start,
            "source_sample_stop": row.source_sample_stop,
            "source_time_start_seconds": row.source_time_start_seconds,
            "source_time_stop_seconds": row.source_time_stop_seconds,
            "sampling_rate_hz": row.sampling_rate_hz,
            "channel_names": row.channel_names,
            "channel_roles": row.channel_roles,
            "channel_geometry": row.channel_geometry,
            "true_length": row.true_length,
            "padding_mask": row.padding_mask,
            "cue": row.cue,
            "timing": row.timing,
            "target": targets[row.item_id],
        }
        digest.update(_canonical_bytes(metadata))
        values = np.asarray(row.signal)
        digest.update(_canonical_bytes({"dtype": values.dtype.str, "shape": values.shape}))
        digest.update(values.astype("<f8", copy=False).tobytes(order="C"))
    return digest.hexdigest()


def prepare_fold_capabilities(
    rows: Sequence[g1.GeneratedRow], targets: Mapping[str, int]
) -> tuple[tuple[FoldCapability, ...], SealedSyntheticTargetVault]:
    validate_fixture(rows)
    if set(targets) != {row.item_id for row in rows}:
        raise CommR0GeneratedRefusal("R0G-TARGET-INVENTORY")
    capabilities = []
    held_target_inventory: dict[str, int] = {}
    for held_out in PARTICIPANTS:
        source_rows = tuple(row for row in rows if row.participant_id != held_out)
        held_rows = tuple(row for row in rows if row.participant_id == held_out)
        source_targets = {row.item_id: targets[row.item_id] for row in source_rows}
        held_targets = {row.item_id: targets[row.item_id] for row in held_rows}
        if set(source_targets) & set(held_targets):
            raise CommR0GeneratedRefusal("R0G-SPLIT-LEAK")
        capabilities.append(FoldCapability(held_out, source_rows, source_targets, held_rows))
        held_target_inventory.update(held_targets)
    return tuple(capabilities), SealedSyntheticTargetVault(held_target_inventory)


def assert_target_free_payload(value: Any) -> None:
    forbidden = {"target", "targets", "label", "labels", "reference_text", "intended_text"}
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in forbidden or lowered.endswith(("_target", "_targets", "_label", "_labels")):
                raise CommR0GeneratedRefusal("R0G-TARGET-LEAK")
            assert_target_free_payload(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            assert_target_free_payload(nested)


def cyclic_source_derangement(
    source_rows: Sequence[g1.GeneratedRow],
    source_targets: Mapping[str, int],
    residuals: Any,
    *,
    shift: int,
    class_count: int = 4,
) -> Any:
    np = g1._np()
    values = np.asarray(residuals, dtype="float64")
    if shift not in range(1, class_count):
        raise CommR0GeneratedRefusal("R0G-DERANGEMENT-SHIFT")
    if values.ndim != 2 or values.shape[0] != len(source_rows):
        raise CommR0GeneratedRefusal("R0G-DERANGEMENT-SHAPE")
    by_group: dict[tuple[str, str, int], list[int]] = defaultdict(list)
    for index, row in enumerate(source_rows):
        if row.item_id not in source_targets:
            raise CommR0GeneratedRefusal("R0G-DERANGEMENT-SCOPE")
        by_group[(row.participant_id, row.session_id, row.repeat_index)].append(index)
    result = np.empty_like(values)
    for indices in by_group.values():
        by_class = {source_targets[source_rows[index].item_id]: index for index in indices}
        if sorted(by_class) != list(range(class_count)) or len(indices) != class_count:
            raise CommR0GeneratedRefusal("R0G-DERANGEMENT-SCOPE")
        for target_class, destination in by_class.items():
            result[destination] = values[by_class[(target_class + shift) % class_count]]
    if sorted(map(tuple, result.tolist())) != sorted(map(tuple, values.tolist())):
        raise CommR0GeneratedRefusal("R0G-DERANGEMENT-MARGINAL")
    return result


def _condition_features(
    condition: str, views: Sequence[Mapping[str, Any]], residuals: Any
) -> Any:
    np = g1._np()
    arrays = {
        "cue_only": [view["cue"] for view in views],
        "timing_only": [view["timing"] for view in views],
        "EOG_only": [view["eog"] for view in views],
        "oral_EMG_only": [view["oral"] for view in views],
        "peripheral_context_P": [view["context"] for view in views],
        "selected_central_EEG_only": [view["central"] for view in views],
        "posterior_EEG_only": [view["posterior"] for view in views],
    }
    if condition in arrays:
        return np.stack(arrays[condition])
    if condition in {
        "P_plus_residual_EEG",
        "P_plus_class_destroyed_residual_EEG",
    }:
        context = np.stack([view["context"] for view in views])
        return np.concatenate((context, residuals), axis=1)
    raise CommR0GeneratedRefusal("R0G-CONDITION")


def _feature_view(row: g1.GeneratedRow) -> dict[str, Any]:
    np = g1._np()
    base = g1.feature_views(row)
    return {
        **base,
        "cue": np.asarray(row.cue, dtype="float64"),
        "timing": np.asarray(row.timing, dtype="float64"),
    }


def _normalized(probabilities: Any) -> Any:
    np = g1._np()
    values = np.clip(np.asarray(probabilities, dtype="float64"), 1e-6, 0.999999)
    return values / values.sum(axis=1, keepdims=True)


def _prediction_rows(
    rows: Sequence[g1.GeneratedRow], condition: str, probabilities: Any
) -> list[dict[str, Any]]:
    return [
        {
            "item_id": row.item_id,
            "participant_id": row.participant_id,
            "session_id": row.session_id,
            "condition": condition,
            "probabilities": probability.tolist(),
        }
        for row, probability in zip(rows, _normalized(probabilities), strict=True)
    ]


def _derive_language_arms(
    held_rows: Sequence[g1.GeneratedRow],
    source_prior: Any,
    candidate: Any,
) -> dict[str, Any]:
    np = g1._np()
    prior = _normalized(source_prior)
    neural = _normalized(candidate)
    combined = _normalized(prior * neural)
    by_session: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(held_rows):
        by_session[row.session_id].append(index)
    deranged = np.empty_like(neural)
    for session_id, indices in by_session.items():
        ordered = sorted(
            indices,
            key=lambda index: (
                hashlib.sha256(
                    (
                        f"{REGISTRATION_ID}|item-derangement|{SOURCE_ID}|"
                        f"{session_id}|{held_rows[index].item_id}"
                    ).encode("utf-8")
                ).digest(),
                held_rows[index].item_id.encode("utf-8"),
            ),
        )
        if len(ordered) < 2:
            raise CommR0GeneratedRefusal("R0G-ITEM-DERANGEMENT-GROUP")
        for destination, source in zip(ordered, ordered[1:] + ordered[:1], strict=True):
            deranged[destination] = neural[source]
    return {
        "language_only": prior,
        "neural_only": neural,
        "neural_plus_language": combined,
        "item_deranged_neural_plus_language": _normalized(prior * deranged),
    }


def predict_capabilities(
    capabilities: Sequence[FoldCapability],
) -> tuple[list[dict[str, Any]], OperationLedger]:
    """Fit source-only transforms and emit neural/control predictions only."""

    np = g1._np()
    if tuple(inspect.signature(predict_capabilities).parameters) != ("capabilities",):
        raise CommR0GeneratedRefusal("R0G-PREDICTOR-SIGNATURE")
    predictions: list[dict[str, Any]] = []
    ledger = OperationLedger()
    for capability in capabilities:
        if any(row.participant_id == capability.held_out_participant for row in capability.source_rows):
            raise CommR0GeneratedRefusal("R0G-SPLIT-LEAK")
        if any(row.participant_id != capability.held_out_participant for row in capability.held_out_rows):
            raise CommR0GeneratedRefusal("R0G-CAPABILITY-ESCAPE")
        assert_target_free_payload(
            {
                "held_out_rows": [row.item_id for row in capability.held_out_rows],
                "held_out_participant": capability.held_out_participant,
            }
        )
        source_views = [_feature_view(row) for row in capability.source_rows]
        held_views = [_feature_view(row) for row in capability.held_out_rows]
        source_context = np.stack([view["context"] for view in source_views])
        held_context = np.stack([view["context"] for view in held_views])
        source_central = np.stack([view["central"] for view in source_views])
        held_central = np.stack([view["central"] for view in held_views])
        source_y = np.asarray(
            [capability.source_targets[row.item_id] for row in capability.source_rows]
        )
        residualizer = g1._fit_residualizer(source_context, source_central)
        ledger.residualizer_fits += 1
        source_residual = g1._residualize(residualizer, source_context, source_central)
        held_residual = g1._residualize(residualizer, held_context, held_central)
        counts = Counter(source_y.tolist())
        prior_vector = np.asarray([counts[index] for index in range(4)], dtype="float64")
        prior_vector /= prior_vector.sum()
        equal = np.full((len(capability.held_out_rows), 4), 0.25)
        prior = np.tile(prior_vector, (len(capability.held_out_rows), 1))
        condition_probabilities: dict[str, Any] = {
            "equal_prior": equal,
            "source_class_prior": prior,
        }
        ledger.classifier_or_prior_fits += 1
        ledger.model_inference_runs += 1
        for condition in NEURAL_CONDITIONS[2:-1]:
            source_x = _condition_features(condition, source_views, source_residual)
            held_x = _condition_features(condition, held_views, held_residual)
            scaler, model = g1._fit_classifier(source_x, source_y)
            condition_probabilities[condition] = model.predict_proba(
                scaler.transform(held_x)
            )
            ledger.classifier_or_prior_fits += 1
            ledger.model_inference_runs += 1
        deranged_probabilities = []
        for shift in range(1, 4):
            deranged_source = cyclic_source_derangement(
                capability.source_rows,
                capability.source_targets,
                source_residual,
                shift=shift,
            )
            source_x = _condition_features(
                "P_plus_class_destroyed_residual_EEG",
                source_views,
                deranged_source,
            )
            held_x = _condition_features(
                "P_plus_class_destroyed_residual_EEG",
                held_views,
                held_residual,
            )
            scaler, model = g1._fit_classifier(source_x, source_y)
            deranged_probabilities.append(model.predict_proba(scaler.transform(held_x)))
            ledger.classifier_or_prior_fits += 1
            ledger.model_inference_runs += 1
        condition_probabilities["P_plus_class_destroyed_residual_EEG"] = np.mean(
            np.stack(deranged_probabilities), axis=0
        )
        for condition in NEURAL_CONDITIONS:
            predictions.extend(
                _prediction_rows(
                    capability.held_out_rows,
                    condition,
                    condition_probabilities[condition],
                )
            )
            ledger.prediction_sets += 1
    ledger.prediction_rows = len(predictions)
    expected_sets = len(PARTICIPANTS) * len(NEURAL_CONDITIONS)
    expected_rows = len(PARTICIPANTS) * 24 * len(NEURAL_CONDITIONS)
    if ledger.residualizer_fits != 12 or ledger.classifier_or_prior_fits != 144:
        raise CommR0GeneratedRefusal("R0G-FIT-SCHEDULE")
    if ledger.model_inference_runs != 144:
        raise CommR0GeneratedRefusal("R0G-INFERENCE-SCHEDULE")
    if ledger.prediction_sets != expected_sets or ledger.prediction_rows != expected_rows:
        raise CommR0GeneratedRefusal("R0G-PREDICTION-SCHEDULE")
    validate_prediction_inventory(predictions, conditions=NEURAL_CONDITIONS)
    return predictions, ledger


def validate_prediction_inventory(
    predictions: Sequence[Mapping[str, Any]],
    *,
    conditions: Sequence[str] = ALL_CONDITIONS,
) -> None:
    expected_rows = len(PARTICIPANTS) * 24 * len(conditions)
    if len(predictions) != expected_rows:
        raise CommR0GeneratedRefusal("R0G-PREDICTION-COUNT")
    keys: set[tuple[str, str]] = set()
    for prediction in predictions:
        if set(prediction) != {
            "item_id",
            "participant_id",
            "session_id",
            "condition",
            "probabilities",
        }:
            raise CommR0GeneratedRefusal("R0G-PREDICTION-FIELDS")
        key = (str(prediction["item_id"]), str(prediction["condition"]))
        if key in keys:
            raise CommR0GeneratedRefusal("R0G-PREDICTION-DUPLICATE")
        keys.add(key)
        if prediction["condition"] not in conditions:
            raise CommR0GeneratedRefusal("R0G-PREDICTION-CONDITION")
        probabilities = prediction["probabilities"]
        if not isinstance(probabilities, list) or len(probabilities) != 4:
            raise CommR0GeneratedRefusal("R0G-PREDICTION-DIMENSION")
        if any(not math.isfinite(float(value)) for value in probabilities):
            raise CommR0GeneratedRefusal("R0G-PREDICTION-NONFINITE")
        if not math.isclose(sum(map(float, probabilities)), 1.0, abs_tol=1e-12):
            raise CommR0GeneratedRefusal("R0G-PREDICTION-SUM")


def build_neural_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    validate_prediction_inventory(predictions, conditions=NEURAL_CONDITIONS)
    return {
        "schema_name": "neurodecodekit.comm_r0_generated_neural_prediction_freeze",
        "schema_version": "0.1.0",
        "registration_id": REGISTRATION_ID,
        "participants": len(PARTICIPANTS),
        "conditions": list(NEURAL_CONDITIONS),
        "prediction_sets": len(PARTICIPANTS) * len(NEURAL_CONDITIONS),
        "prediction_rows": len(predictions),
        "private_prediction_payload_sha256": _sha256(_canonical_bytes(list(predictions))),
        "contains_individual_prediction_probability_target_participant_outcome_or_private_path": False,
    }


def verify_neural_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]], freeze: Mapping[str, Any]
) -> None:
    if dict(freeze) != build_neural_prediction_freeze(predictions):
        raise CommR0GeneratedRefusal("R0G-NEURAL-PREDICTION-TAMPER")


def derive_language_predictions(
    neural_predictions: Sequence[Mapping[str, Any]],
    capabilities: Sequence[FoldCapability],
    neural_freeze: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Derive provider-free language arms only after the neural freeze verifies."""

    np = g1._np()
    verify_neural_prediction_freeze(neural_predictions, neural_freeze)
    by_key = {
        (str(row["item_id"]), str(row["condition"])): row
        for row in neural_predictions
    }
    language_predictions: list[dict[str, Any]] = []
    for capability in capabilities:
        held_rows = capability.held_out_rows
        prior = np.asarray(
            [
                by_key[(row.item_id, "source_class_prior")]["probabilities"]
                for row in held_rows
            ],
            dtype="float64",
        )
        candidate = np.asarray(
            [
                by_key[(row.item_id, "P_plus_residual_EEG")]["probabilities"]
                for row in held_rows
            ],
            dtype="float64",
        )
        language = _derive_language_arms(held_rows, prior, candidate)
        for condition in LANGUAGE_CONDITIONS:
            language_predictions.extend(
                _prediction_rows(held_rows, condition, language[condition])
            )
    validate_prediction_inventory(language_predictions, conditions=LANGUAGE_CONDITIONS)
    return language_predictions


def build_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]],
    neural_freeze: Mapping[str, Any],
) -> dict[str, Any]:
    validate_prediction_inventory(predictions)
    neural_predictions = [
        row for row in predictions if str(row["condition"]) in NEURAL_CONDITIONS
    ]
    verify_neural_prediction_freeze(neural_predictions, neural_freeze)
    return {
        "schema_name": "neurodecodekit.comm_r0_generated_prediction_freeze",
        "schema_version": "0.1.0",
        "registration_id": REGISTRATION_ID,
        "participants": len(PARTICIPANTS),
        "conditions": list(ALL_CONDITIONS),
        "prediction_sets": len(PARTICIPANTS) * len(ALL_CONDITIONS),
        "prediction_rows": len(predictions),
        "private_prediction_payload_sha256": _sha256(_canonical_bytes(list(predictions))),
        "neural_prediction_freeze_sha256": _sha256(
            _canonical_bytes(dict(neural_freeze))
        ),
        "neural_prediction_freeze_preceded_language_arms": True,
        "contains_individual_prediction_probability_target_participant_outcome_or_private_path": False,
    }


def verify_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]],
    freeze: Mapping[str, Any],
    neural_freeze: Mapping[str, Any],
) -> None:
    if dict(freeze) != build_prediction_freeze(predictions, neural_freeze):
        raise CommR0GeneratedRefusal("R0G-PREDICTION-TAMPER")


def _commit_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]],
    freeze: Mapping[str, Any],
    neural_freeze: Mapping[str, Any],
) -> CommittedPredictionFreeze:
    verify_prediction_freeze(predictions, freeze, neural_freeze)
    payload = dict(freeze)
    return CommittedPredictionFreeze(payload, _sha256(_canonical_bytes(payload)))


def _balanced_accuracy(targets: Sequence[int], predictions: Sequence[int]) -> float:
    recalls = []
    for target_class in range(4):
        indices = [index for index, target in enumerate(targets) if target == target_class]
        if not indices:
            raise CommR0GeneratedRefusal("R0G-SCORER-CLASS")
        recalls.append(
            sum(predictions[index] == target_class for index in indices) / len(indices)
        )
    return sum(recalls) / len(recalls)


def exact_one_sided_sign_flip(values: Sequence[float]) -> float:
    if not values or len(values) > 20:
        raise CommR0GeneratedRefusal("R0G-SIGN-FLIP-SIZE")
    observed = sum(values) / len(values)
    at_least = 0
    total = 1 << len(values)
    for mask in range(total):
        statistic = sum(
            value if mask & (1 << index) else -value
            for index, value in enumerate(values)
        ) / len(values)
        if statistic >= observed - 1e-15:
            at_least += 1
    return at_least / total


def one_sided_sign_flip(
    values: Sequence[float],
    *,
    source_id: str = SOURCE_ID,
    monte_carlo_draws: int = 1_000_000,
) -> float:
    """Execute the registered exact or deterministic SHA-256 sign schedule."""

    if len(values) <= 20:
        return exact_one_sided_sign_flip(values)
    if monte_carlo_draws <= 0:
        raise CommR0GeneratedRefusal("R0G-SIGN-FLIP-DRAWS")
    observed = sum(values) / len(values)
    at_least = 0
    for draw in range(monte_carlo_draws):
        signed = 0.0
        for rank, value in enumerate(values):
            digest = hashlib.sha256(
                (
                    f"{REGISTRATION_ID}|sign-flip|{source_id}|{draw}|{rank}"
                ).encode("ascii")
            ).digest()
            signed += value if digest[-1] & 1 else -value
        if signed / len(values) >= observed - 1e-15:
            at_least += 1
    return (1 + at_least) / (monte_carlo_draws + 1)


def holm_two_adjusted_p_values(p_values: Mapping[str, float]) -> dict[str, float]:
    if len(p_values) != 2 or any(not 0.0 <= value <= 1.0 for value in p_values.values()):
        raise CommR0GeneratedRefusal("R0G-HOLM-INPUT")
    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0].encode("utf-8")))
    first_name, first_value = ordered[0]
    second_name, second_value = ordered[1]
    first_adjusted = min(1.0, 2.0 * first_value)
    second_adjusted = min(1.0, max(first_adjusted, second_value))
    return {first_name: first_adjusted, second_name: second_adjusted}


def qualify_generalized_statistics_and_derangement(
    template: g1.GeneratedRow,
) -> dict[str, Any]:
    np = g1._np()
    derangement_hashes: dict[str, list[str]] = {}
    for class_count in (3, 4, 5):
        rows = tuple(
            replace(
                template,
                item_id=f"mechanics-k{class_count}-c{target}",
                trial_id=f"trial-0-{target}",
            )
            for target in range(class_count)
        )
        targets = {row.item_id: target for target, row in enumerate(rows)}
        residuals = np.arange(class_count * 3, dtype="float64").reshape(class_count, 3)
        hashes = [
            _sha256(
                cyclic_source_derangement(
                    rows,
                    targets,
                    residuals,
                    shift=shift,
                    class_count=class_count,
                ).astype("<f8", copy=False).tobytes(order="C")
            )
            for shift in range(1, class_count)
        ]
        if len(set(hashes)) != class_count - 1:
            raise CommR0GeneratedRefusal("R0G-DYNAMIC-K-DERANGEMENT")
        derangement_hashes[str(class_count)] = hashes
    values = [0.1 if index % 2 else -0.02 for index in range(21)]
    first_p = one_sided_sign_flip(values, monte_carlo_draws=256)
    second_p = one_sided_sign_flip(values, monte_carlo_draws=256)
    if first_p != second_p:
        raise CommR0GeneratedRefusal("R0G-MONTE-CARLO-NONDETERMINISTIC")
    return {
        "derangement_mechanics_K": [3, 4, 5],
        "derangement_hashes": derangement_hashes,
        "n_above_20_test_participants": 21,
        "n_above_20_qualification_draws": 256,
        "n_above_20_default_registered_draws": 1_000_000,
        "n_above_20_replay_p": first_p,
        "Holm_two_route_adjusted_p": holm_two_adjusted_p_values(
            {"partial-route-a": 0.01, "partial-route-b": 0.04}
        ),
        "full_numerical_model_fixture_K": 4,
        "source_specific_dynamic_model_adapter_status": "pending_exact_source_lock",
    }


def _score_predictions(
    predictions: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    freeze: CommittedPredictionFreeze,
) -> dict[str, Any]:
    if not isinstance(freeze, CommittedPredictionFreeze):
        raise CommR0GeneratedRefusal("R0G-SCORER-UNCOMMITTED-FREEZE")
    if freeze.canonical_sha256 != _sha256(_canonical_bytes(dict(freeze.payload))):
        raise CommR0GeneratedRefusal("R0G-SCORER-FREEZE-TAMPER")
    neural_freeze_sha256 = freeze.payload.get("neural_prediction_freeze_sha256")
    if not isinstance(neural_freeze_sha256, str) or len(neural_freeze_sha256) != 64:
        raise CommR0GeneratedRefusal("R0G-SCORER-NEURAL-FREEZE")
    if set(targets) != {str(row["item_id"]) for row in predictions}:
        raise CommR0GeneratedRefusal("R0G-SCORER-INVENTORY")
    losses: dict[tuple[str, str], list[float]] = defaultdict(list)
    truth: dict[tuple[str, str], list[int]] = defaultdict(list)
    guesses: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in predictions:
        participant = str(row["participant_id"])
        condition = str(row["condition"])
        target = targets[str(row["item_id"])]
        probabilities = [float(value) for value in row["probabilities"]]
        losses[(participant, condition)].append(-math.log(max(probabilities[target], 1e-6)))
        truth[(participant, condition)].append(target)
        guesses[(participant, condition)].append(max(range(4), key=probabilities.__getitem__))
    participant_metrics: dict[str, dict[str, Any]] = {}
    primary_values = []
    component_positive = 0
    for participant in PARTICIPANTS:
        condition_loss = {
            condition: sum(losses[(participant, condition)])
            / len(losses[(participant, condition)])
            for condition in ALL_CONDITIONS
        }
        condition_ba = {
            condition: _balanced_accuracy(
                truth[(participant, condition)], guesses[(participant, condition)]
            )
            for condition in ALL_CONDITIONS
        }
        candidate = condition_loss["P_plus_residual_EEG"]
        margin_p = condition_loss["peripheral_context_P"] - candidate
        margin_deranged = (
            condition_loss["P_plus_class_destroyed_residual_EEG"] - candidate
        )
        primary = min(margin_p, margin_deranged)
        primary_values.append(primary)
        if margin_p > 0.0 and margin_deranged > 0.0:
            component_positive += 1
        participant_metrics[participant] = {
            "primary_minimum_margin": primary,
            "margin_over_P": margin_p,
            "margin_over_deranged": margin_deranged,
            "candidate_balanced_accuracy": condition_ba["P_plus_residual_EEG"],
        }
    aggregate_loss = {
        condition: sum(
            sum(losses[(participant, condition)]) / len(losses[(participant, condition)])
            for participant in PARTICIPANTS
        )
        / len(PARTICIPANTS)
        for condition in ALL_CONDITIONS
    }
    aggregate_ba = {
        condition: sum(
            _balanced_accuracy(
                truth[(participant, condition)], guesses[(participant, condition)]
            )
            for participant in PARTICIPANTS
        )
        / len(PARTICIPANTS)
        for condition in ALL_CONDITIONS
    }
    primary_mean = sum(primary_values) / len(primary_values)
    positive_fraction = component_positive / len(PARTICIPANTS)
    p_value = one_sided_sign_flip(primary_values)
    comparator_ba = max(
        aggregate_ba[condition]
        for condition in (
            "equal_prior",
            "source_class_prior",
            "cue_only",
            "timing_only",
            "posterior_EEG_only",
        )
    )
    ba_margin = aggregate_ba["P_plus_residual_EEG"] - comparator_ba
    gates = {
        "primary_margin_at_least_0_03": primary_mean >= 0.03,
        "both_components_positive_fraction_at_least_0_70": positive_fraction >= 0.70,
        "one_sided_sign_flip_p_at_most_0_05": p_value <= 0.05,
        "balanced_accuracy_margin_at_least_0_05": ba_margin >= 0.05,
        "candidate_log_loss_better_than_equal_prior": (
            aggregate_loss["P_plus_residual_EEG"] < aggregate_loss["equal_prior"]
        ),
    }
    if all(gates.values()):
        route = "COMM-R0-G-R1"
    elif primary_mean > 0.0:
        route = "COMM-R0-G-R2"
    else:
        route = "COMM-R0-G-R3"
    return {
        "route": route,
        "primary_mean_nats_per_item": primary_mean,
        "both_component_positive_participant_fraction": positive_fraction,
        "exact_one_sided_sign_flip_p": p_value,
        "candidate_balanced_accuracy": aggregate_ba["P_plus_residual_EEG"],
        "best_fixed_noncandidate_balanced_accuracy": comparator_ba,
        "balanced_accuracy_margin": ba_margin,
        "condition_log_loss": aggregate_loss,
        "condition_balanced_accuracy": aggregate_ba,
        "participant_metrics": participant_metrics,
        "gates": gates,
        "language_arms_change_neural_router": False,
        "scientific_value": "none_generated_engineering_only",
    }


def enforce_resource_caps(measurements: Mapping[str, int | float]) -> None:
    fields = {
        "runtime_seconds": "wall_time_seconds",
        "peak_process_tree_RSS_bytes": "peak_process_tree_RSS_bytes",
        "generated_input_bytes": "generated_input_bytes",
        "private_output_bytes": "private_output_bytes",
        "temporary_disk_bytes": "temporary_disk_bytes",
        "public_output_bytes": "public_output_bytes",
    }
    for field, cap_name in fields.items():
        value = measurements.get(field)
        if not isinstance(value, (int, float)) or value < 0:
            raise CommR0GeneratedRefusal("R0G-RESOURCE-MEASUREMENT")
        if value > CAPS[cap_name]:
            raise CommR0GeneratedRefusal(f"R0G-{field.upper()}-CAP")


def _expect_refusal(name: str, operation: Callable[[], Any], expected: str) -> str:
    try:
        operation()
    except (CommR0GeneratedRefusal, g1.CommG1Refusal, g2.CommG2Refusal) as exc:
        if expected not in str(exc):
            raise CommR0GeneratedRefusal(f"R0G-WRONG-REFUSAL:{name}") from exc
        return name
    raise CommR0GeneratedRefusal(f"R0G-ACCEPTED-MALFORMED:{name}")


def exercise_required_refusals(
    rows: Sequence[g1.GeneratedRow],
    targets: Mapping[str, int],
    capabilities: Sequence[FoldCapability],
    predictions: Sequence[Mapping[str, Any]],
    neural_freeze: Mapping[str, Any],
    freeze: Mapping[str, Any],
    workdir: Path,
) -> list[str]:
    np = g1._np()
    first = rows[0]
    malformed_identity = replace(first, outer_fold_id="wrong")
    malformed_future = replace(first, source_sample_stop=first.source_sample_stop + 1)
    malformed_role = replace(first, channel_roles=("unknown",) * len(first.channel_roles))
    missing_control = replace(
        first,
        channel_roles=tuple(
            "unknown" if role == "oral_EMG" else role for role in first.channel_roles
        ),
    )
    leaked = replace(
        capabilities[0], source_rows=(*capabilities[0].source_rows, capabilities[0].held_out_rows[0])
    )
    tampered = [dict(row) for row in predictions]
    tampered[0] = {**tampered[0], "probabilities": [0.7, 0.1, 0.1, 0.1]}
    existing = workdir / "existing.json"
    existing.write_bytes(b"keep")
    symlink_target = workdir / "target"
    symlink_target.mkdir()
    symlink = workdir / "link"
    symlink.symlink_to(symlink_target, target_is_directory=True)
    fresh_vault = SealedSyntheticTargetVault(targets)
    delivered_vault = SealedSyntheticTargetVault(targets)
    committed = delivered_vault.arm(predictions, freeze, neural_freeze)
    delivered_vault.deliver(committed)
    base_measurements = {
        "runtime_seconds": 0,
        "peak_process_tree_RSS_bytes": 0,
        "generated_input_bytes": 0,
        "private_output_bytes": 0,
        "temporary_disk_bytes": 0,
        "public_output_bytes": 0,
    }
    cases = {
        "identity_mismatch": (
            lambda: g1.validate_rows((malformed_identity,)),
            "SPLIT-IDENTITY",
        ),
        "split_leak": (lambda: predict_capabilities((leaked,)), "SPLIT-LEAK"),
        "target_leak": (
            lambda: assert_target_free_payload({"held_out_targets": {"x": 1}}),
            "TARGET-LEAK",
        ),
        "future_sample_use": (
            lambda: validate_fixture((malformed_future,), expected_participants=1),
            "SAMPLE-TIMESTAMP",
        ),
        "channel_role_mismatch": (
            lambda: g1.validate_rows((malformed_role,)),
            "CHANNEL-ROLE",
        ),
        "missing_required_control": (
            lambda: g1.validate_rows((missing_control,)),
            "CHANNEL-ROLE",
        ),
        "derangement_scope_mismatch": (
            lambda: cyclic_source_derangement(
                capabilities[0].source_rows[:-1],
                capabilities[0].source_targets,
                np.zeros((len(capabilities[0].source_rows) - 1, 4)),
                shift=1,
            ),
            "DERANGEMENT-SCOPE",
        ),
        "prediction_tamper": (
            lambda: verify_prediction_freeze(tampered, freeze, neural_freeze),
            "PREDICTION-TAMPER",
        ),
        "pre_freeze_target_delivery": (
            lambda: fresh_vault.deliver(None),
            "PRE-FREEZE",
        ),
        "repeated_target_delivery": (
            lambda: delivered_vault.deliver(committed),
            "REPEATED",
        ),
        "output_clobber": (
            lambda: g2._publish_no_replace(existing, b"replace"),
            "OUTPUT-CLOBBER",
        ),
        "symlink_escape": (
            lambda: g2._publish_no_replace(symlink / "escape.json", b"x"),
            "DIRECTORY-CAPABILITY",
        ),
        "nondeterministic_replay": (
            lambda: _assert_equal_digest("a" * 64, "b" * 64),
            "NONDETERMINISTIC",
        ),
        "output_cap_breach": (
            lambda: enforce_resource_caps(
                {**base_measurements, "public_output_bytes": CAPS["public_output_bytes"] + 1}
            ),
            "PUBLIC_OUTPUT_BYTES-CAP",
        ),
        "RSS_cap_breach": (
            lambda: enforce_resource_caps(
                {
                    **base_measurements,
                    "peak_process_tree_RSS_bytes": CAPS["peak_process_tree_RSS_bytes"] + 1,
                }
            ),
            "PEAK_PROCESS_TREE_RSS_BYTES-CAP",
        ),
        "timeout": (
            lambda: _run_isolated(
                time.sleep,
                0.1,
                timeout_seconds=0.01,
                child_tempdir=workdir,
            ),
            "CHILD-TIMEOUT",
        ),
    }
    refusals = [_expect_refusal(name, *cases[name]) for name in REQUIRED_REFUSALS]
    if tuple(refusals) != REQUIRED_REFUSALS:
        raise CommR0GeneratedRefusal("R0G-REFUSAL-COMPLETENESS")
    return refusals


def _assert_equal_digest(first: str, second: str) -> None:
    if first != second:
        raise CommR0GeneratedRefusal("R0G-NONDETERMINISTIC-REPLAY")


def _run_replay(
    replay_id: str = "development-replay",
    workdir_text: str | None = None,
) -> dict[str, Any]:
    workdir_identity: tuple[int, int] | None = None
    if workdir_text is not None:
        workdir = Path(workdir_text).absolute()
        descriptor = g2._assert_directory_capability(workdir)
        os.close(descriptor)
        info = workdir.stat()
        workdir_identity = (info.st_dev, info.st_ino)
    rows, targets, input_bytes = generate_fixture()
    fixture_digest = canonical_fixture_digest(rows, targets)
    causal_records = [causal_timing_record(row) for row in rows]
    causal_timing_sha256 = _sha256(_canonical_bytes(causal_records))
    capabilities, vault = prepare_fold_capabilities(rows, targets)
    neural_predictions, ledger = predict_capabilities(capabilities)
    neural_freeze = build_neural_prediction_freeze(neural_predictions)
    language_predictions = derive_language_predictions(
        neural_predictions, capabilities, neural_freeze
    )
    predictions = [*neural_predictions, *language_predictions]
    ledger.prediction_sets += len(PARTICIPANTS) * len(LANGUAGE_CONDITIONS)
    ledger.prediction_rows = len(predictions)
    freeze = build_prediction_freeze(predictions, neural_freeze)
    score = vault.score_once(predictions, freeze, neural_freeze)
    ledger.synthetic_target_deliveries += 1
    ledger.synthetic_scores += 1
    public_score = {key: value for key, value in score.items() if key != "participant_metrics"}
    return {
        "fixture_digest": fixture_digest,
        "causal_timing_sha256": causal_timing_sha256,
        "input_bytes": input_bytes,
        "private_prediction_bytes": len(_canonical_bytes(predictions)),
        "freeze": freeze,
        "neural_freeze": neural_freeze,
        "score": public_score,
        "ledger": ledger.__dict__,
        "rows": rows,
        "targets": targets,
        "capabilities": capabilities,
        "predictions": predictions,
        "replay_id": replay_id,
        "process_id": os.getpid(),
        "workdir_identity": workdir_identity,
        "peak_process_tree_RSS_bytes": g1.peak_process_tree_rss_bytes(),
    }


def _replay_equivalence_surface(replay: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fixture_digest": replay["fixture_digest"],
        "causal_timing_sha256": replay["causal_timing_sha256"],
        "neural_freeze": replay["neural_freeze"],
        "freeze": replay["freeze"],
        "score": replay["score"],
        "ledger": replay["ledger"],
    }


def _result_payload(result: dict[str, Any]) -> bytes:
    prior = -1
    for _ in range(8):
        payload = _canonical_bytes(result)
        result["measurements"]["public_output_bytes"] = len(payload)
        if len(payload) == prior:
            return _canonical_bytes(result)
        prior = len(payload)
    raise CommR0GeneratedRefusal("R0G-PUBLIC-BYTE-ACCOUNTING")


def plan() -> dict[str, Any]:
    return {
        "lane_id": LANE_ID,
        "registration_id": REGISTRATION_ID,
        "generated_only": True,
        "participants": 12,
        "rows_per_replay": 288,
        "replays": 2,
        "neural_conditions": list(NEURAL_CONDITIONS),
        "language_conditions": list(LANGUAGE_CONDITIONS),
        "cyclic_derangements_per_fold": 3,
        "parameter_update_fits_per_replay": 156,
        "model_inference_runs_per_replay": 144,
        "prediction_sets_per_replay": 180,
        "prediction_rows_per_replay": 4320,
        "real_or_private_operations": 0,
        "scientific_value": "none_generated_engineering_only",
    }


def _run_deterministic_replay_pair(
    replay_directories: Sequence[Path],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
    """Execute the exact isolated replay pair used by the qualification."""

    if len(replay_directories) != 2:
        raise CommR0GeneratedRefusal("R0G-REPLAY-DIRECTORY-COUNT")
    first, first_monitor = _run_isolated(
        _run_replay,
        "replay-1",
        str(replay_directories[0]),
        timeout_seconds=120.0,
        child_tempdir=replay_directories[0],
    )
    if first["peak_process_tree_RSS_bytes"] > CAPS["peak_process_tree_RSS_bytes"]:
        raise CommR0GeneratedRefusal("R0G-PEAK_PROCESS_TREE_RSS_BYTES-CAP")
    second, second_monitor = _run_isolated(
        _run_replay,
        "replay-2",
        str(replay_directories[1]),
        timeout_seconds=120.0,
        child_tempdir=replay_directories[1],
    )
    if second["peak_process_tree_RSS_bytes"] > CAPS["peak_process_tree_RSS_bytes"]:
        raise CommR0GeneratedRefusal("R0G-PEAK_PROCESS_TREE_RSS_BYTES-CAP")
    if first["process_id"] == second["process_id"]:
        raise CommR0GeneratedRefusal("R0G-REPLAY-PROCESS-ISOLATION")
    if first["workdir_identity"] == second["workdir_identity"]:
        raise CommR0GeneratedRefusal("R0G-REPLAY-WORKDIR-ISOLATION")
    first_digest = _sha256(_canonical_bytes(_replay_equivalence_surface(first)))
    second_digest = _sha256(_canonical_bytes(_replay_equivalence_surface(second)))
    _assert_equal_digest(first_digest, second_digest)
    return first, first_monitor, second, second_monitor, first_digest


def run_generated_qualification(
    output_path: str | Path,
    *,
    root: str | Path | None = None,
    peak_rss_reader: Callable[[], int] = g1.peak_process_tree_rss_bytes,
) -> dict[str, Any]:
    """Run the one activated generated qualification; no real-data path exists."""

    assert_single_thread_environment()
    repository = Path(root) if root is not None else _repo_root()
    load_registration(repository)
    activation = load_activation(repository)
    activation_proof = load_activation_proof(repository)
    output = Path(output_path).expanduser().absolute()
    expected_output = (repository / RESULT_PATH).absolute()
    if output != expected_output:
        raise CommR0GeneratedRefusal("R0G-OUTPUT-PATH")
    g2._require_output_within_repository(output, repository)
    if output.exists() or output.is_symlink():
        raise CommR0GeneratedRefusal("R0G-OUTPUT-CLOBBER")
    started = time.monotonic()
    preflight_rss = peak_rss_reader()
    if not isinstance(preflight_rss, int) or preflight_rss < 0:
        raise CommR0GeneratedRefusal("R0G-RSS-MEASUREMENT")
    workdir = output.parent / f".comm-r0-g-{os.getpid()}-{time.monotonic_ns()}"
    workdir.mkdir(mode=0o700)
    workdir_info = workdir.stat()
    workdir_identity = (workdir_info.st_dev, workdir_info.st_ino)
    replay_directories = []
    try:
        for name in ("replay-1", "replay-2", "adversarial"):
            directory = workdir / name
            directory.mkdir(mode=0o700)
            replay_directories.append(directory)
        first, first_monitor, second, second_monitor, equivalence_sha256 = (
            _run_deterministic_replay_pair(replay_directories[:2])
        )
        if first["score"]["route"] != "COMM-R0-G-R1":
            raise CommR0GeneratedRefusal("R0G-POSITIVE-CONTROL")
        route_qualification = qualify_route_contracts()
        generalized_mechanics = qualify_generalized_statistics_and_derangement(
            first["rows"][0]
        )
        shortcut_results = {}
        generated_input_bytes = first["input_bytes"] + second["input_bytes"]
        for case_family in g1.CASE_FAMILIES[1:]:
            case_rows, case_targets, case_bytes = generate_fixture(
                case_family, participants=("shortcut-a", "shortcut-b")
            )
            replay_rows, replay_targets, replay_bytes = generate_fixture(
                case_family, participants=("shortcut-a", "shortcut-b")
            )
            first_digest = canonical_fixture_digest(case_rows, case_targets)
            second_digest = canonical_fixture_digest(replay_rows, replay_targets)
            _assert_equal_digest(first_digest, second_digest)
            shortcut_results[case_family] = {
                **g1.validate_shortcut_fixture(case_family, case_rows, case_targets),
                "fixture_sha256": first_digest,
            }
            generated_input_bytes += case_bytes + replay_bytes
        refusal_ids = exercise_required_refusals(
            first["rows"],
            first["targets"],
            first["capabilities"],
            first["predictions"],
            first["neural_freeze"],
            first["freeze"],
            replay_directories[2],
        )
        temporary_disk_bytes = g2._measure_tree_bytes(workdir)
    finally:
        g2._secure_remove_tree(workdir, workdir_identity)
    runtime = time.monotonic() - started
    peak_rss = max(
        peak_rss_reader(),
        first["peak_process_tree_RSS_bytes"],
        second["peak_process_tree_RSS_bytes"],
    )
    private_output_bytes = first["private_prediction_bytes"] + second["private_prediction_bytes"]
    result = {
        "schema_name": "neurodecodekit.communication_eeg_independent_replication_generated_result",
        "schema_version": "0.1.0",
        "lane_id": LANE_ID,
        "registration_id": REGISTRATION_ID,
        "status": "passed_generated_only_no_scientific_value",
        "implementation_proof": activation_proof["green_activation_commit"],
        "activation": {
            "implementation_commit": activation["implementation_commit"],
            "activation_commit": activation_proof["activation_commit"],
            "activation_proof_commit": activation_proof["proof_closeout_commit"],
        },
        "deterministic_replays": {
            "count": 2,
            "separate_child_processes": True,
            "separate_inode_bound_workdirs": True,
            "equivalence_sha256": equivalence_sha256,
            "causal_timing_sha256": first["causal_timing_sha256"],
        },
        "positive_control": first["score"],
        "route_qualification": route_qualification,
        "generalized_mechanics": generalized_mechanics,
        "shortcut_controls": shortcut_results,
        "adversarial_qualification": {
            "required": list(REQUIRED_REFUSALS),
            "observed": refusal_ids,
            "all_required_refused": tuple(refusal_ids) == REQUIRED_REFUSALS,
        },
        "schedule": {
            "replays": 2,
            "residualizer_fits": 24,
            "classifier_or_prior_fits": 288,
            "total_parameter_update_fits": 312,
            "model_inference_runs": 288,
            "prediction_sets": 360,
            "prediction_rows": 8640,
            "synthetic_target_deliveries": 2,
            "synthetic_scores": 2,
            "post_target_updates": 0,
            "provider_calls": 0,
        },
        "measurements": {
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": peak_rss,
            "replay_runtime_seconds": [
                first_monitor["runtime_seconds"],
                second_monitor["runtime_seconds"],
            ],
            "replay_peak_process_tree_RSS_bytes": [
                first["peak_process_tree_RSS_bytes"],
                second["peak_process_tree_RSS_bytes"],
            ],
            "generated_input_bytes": generated_input_bytes,
            "private_output_bytes": private_output_bytes,
            "temporary_disk_bytes": temporary_disk_bytes,
            "public_output_bytes": 0,
            "producer_causal": True,
            "required_context_seconds": 1.0,
            "right_context_seconds": 0.0,
            "trial_boundary_oracle_used": True,
            "end_to_end_latency_measured": False,
        },
        "access_counters": {
            "real_or_private_path_reads": 0,
            "network_bytes": 0,
            "real_signal_samples": 0,
            "real_targets_or_labels": 0,
            "real_training_runs": 0,
            "real_model_inference_runs": 0,
            "real_prediction_sets": 0,
            "real_target_deliveries": 0,
            "real_scores": 0,
            "provider_calls": 0,
            "stream_or_device_operations": 0,
            "release_operations": 0,
            "scientific_claim_upgrades": 0,
        },
        "warnings": [
            "generated arrays and synthetic labels only",
            "positive control is constructed and has no scientific value",
            "offline event-locked trial-boundary oracle remains in use",
            "no dataset-specific source identity has been qualified",
            "no external or generative language model was called",
        ],
        "claim_boundary": {
            "engineering_capability": "generated_full_control_replication_firewall_and_router",
            "real_EEG_accessed": False,
            "communication_decoding_established": False,
            "EEG_beyond_peripheral_controls_established": False,
            "unseen_person_generalization_established": False,
            "independent_replication_established": False,
            "causal_continuous_decoding_established": False,
            "live_neural_decoding_established": False,
        },
    }
    payload = _result_payload(result)
    result["measurements"]["public_output_bytes"] = len(payload)
    enforce_resource_caps(result["measurements"])
    g2._publish_no_replace(output, payload)
    return result


def inspect_result(*, root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    path = (repository / RESULT_PATH).absolute()
    g2._require_output_within_repository(path, repository)
    value = json.loads(g2._read_regular_no_follow(path))
    if value.get("schema_name") != (
        "neurodecodekit.communication_eeg_independent_replication_generated_result"
    ):
        raise CommR0GeneratedRefusal("R0G-INSPECT-SCHEMA")
    return {
        "lane_id": value["lane_id"],
        "status": value["status"],
        "positive_control_route": value["positive_control"]["route"],
        "schedule": value["schedule"],
        "measurements": value["measurements"],
        "warnings": value["warnings"],
        "claim_boundary": value["claim_boundary"],
    }
