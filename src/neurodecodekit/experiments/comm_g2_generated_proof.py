"""Isolated generated proof qualification around the frozen COMM-G1 core."""

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing
import os
import signal
import stat
import subprocess
import tempfile
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_g1_generated as g1


LANE_ID = "COMM-G2"
CONTRACT_PATH = "registries/comm_g2_generated_proof_qualification_contract.v0.json"
CONTRACT_SHA256 = "9ab5b7ef9d90df06abec363301c19cb3821a7b1a308856fdac7813a9eada677b"
FROZEN_G1_MODULE_SHA256 = "99178d463558c27dcfe8c4346d6f47c207cb8dc60b6d45cd6ad3dab4b08fb3f4"
FROZEN_G1_MODULE_PATH = "src/neurodecodekit/experiments/comm_g1_generated.py"
IMPLEMENTATION_RECORD_PATH = "registries/comm_g2_generated_proof_implementation.v0.json"

CAPS = {
    "wall_time_seconds": 180,
    "peak_process_tree_RSS_bytes": 536_870_912,
    "generated_input_bytes_total_maximum": 83_886_080,
    "private_generated_output_bytes_total_maximum": 67_108_864,
    "public_output_bytes_maximum": 1_048_576,
    "temporary_disk_bytes_maximum": 100_663_296,
}

CHILD_ENVIRONMENT_KEYS = (
    "__CF_USER_TEXT_ENCODING",
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "PYTHONHASHSEED",
    "PYTHONPATH",
    "TMPDIR",
    *g1.THREAD_ENVIRONMENT,
)

ADVERSARIAL_FAMILIES = (
    "participant_collision",
    "session_collision",
    "split_leak",
    "capability_escape",
    "row_reorder",
    "role_mismatch",
    "channel_mismatch",
    "mask_mismatch",
    "timestamp_mismatch",
    "geometry_mismatch",
    "sampling_rate_mismatch",
    "held_out_state_fit",
    "residualizer_target_leak",
    "derangement_scope_mismatch",
    "prediction_tamper",
    "prediction_duplicate",
    "prediction_missing",
    "probability_nonfinite",
    "probability_sum_mismatch",
    "pre_freeze_target_delivery",
    "repeated_target_delivery",
    "scorer_row_mismatch",
    "output_clobber",
    "ancestor_symlink_escape",
    "leaf_symlink_escape",
    "publication_race",
    "nonregular_output",
    "cross_workdir_traversal",
    "resource_runtime_cap_breach",
    "resource_RSS_cap_breach",
    "resource_generated_input_cap_breach",
    "resource_private_output_cap_breach",
    "resource_public_output_cap_breach",
    "nondeterministic_fixture_replay",
    "nondeterministic_prediction_replay",
)


class CommG2Refusal(RuntimeError):
    """Fail-closed COMM-G2 generated proof refusal."""


@dataclass(frozen=True)
class FoldJob:
    held_out_participant: str
    source_rows: tuple[g1.GeneratedRow, ...]
    source_targets: Mapping[str, int]
    held_out_rows: tuple[g1.GeneratedRow, ...]


class SealedSyntheticTargetVault:
    def __init__(self, targets: Mapping[str, int]) -> None:
        self.__targets = dict(targets)
        self.deliveries = 0

    def deliver(self, *, freeze_green: bool) -> dict[str, int]:
        if not freeze_green:
            raise CommG2Refusal("G2-TARGET-PRE-FREEZE")
        if self.deliveries:
            raise CommG2Refusal("G2-TARGET-REPEATED-DELIVERY")
        self.deliveries = 1
        return dict(self.__targets)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CommG2Refusal("G2-CANONICAL-JSON") from exc
    return (text + "\n").encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _hash_values(values: Any) -> str:
    return _sha256(_canonical_bytes(values))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_registration(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    contract_path = repository / CONTRACT_PATH
    payload = contract_path.read_bytes()
    if _sha256(payload) != CONTRACT_SHA256:
        raise CommG2Refusal("G2-REGISTRATION-HASH")
    contract = json.loads(payload)
    if contract.get("contract_id") != "COMM-G2-generated-proof-qualification-contract-v0":
        raise CommG2Refusal("G2-REGISTRATION-SCHEMA")
    module_path = repository / FROZEN_G1_MODULE_PATH
    if _file_sha256(module_path) != FROZEN_G1_MODULE_SHA256:
        raise CommG2Refusal("G2-FROZEN-SCIENTIFIC-MODULE-HASH")
    for artifact in contract["parent_closeout"]["artifacts"]:
        path = repository / artifact["path"]
        content = path.read_bytes()
        if len(content) != artifact["bytes"] or _sha256(content) != artifact["sha256"]:
            raise CommG2Refusal("G2-PARENT-CLOSEOUT-HASH")
    return contract


def load_implementation_record(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    path = repository / IMPLEMENTATION_RECORD_PATH
    try:
        record = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise CommG2Refusal("G2-IMPLEMENTATION-RECORD") from exc
    if record.get("schema_name") != "neurodecodekit.comm_g2_generated_proof_implementation":
        raise CommG2Refusal("G2-IMPLEMENTATION-RECORD")
    for artifact in record.get("artifacts", ()):
        artifact_path = repository / artifact["path"]
        payload = artifact_path.read_bytes()
        if len(payload) != artifact["bytes"] or _sha256(payload) != artifact["sha256"]:
            raise CommG2Refusal("G2-IMPLEMENTATION-ARTIFACT-HASH")
    return record


def canonical_fixture_digest(
    rows: Sequence[g1.GeneratedRow], targets: Mapping[str, int]
) -> str:
    """Bind every generated row field and array byte in sequence order."""

    np = g1._np()
    _validate_fixture(rows, targets)
    digest = hashlib.sha256()
    for row_index, row in enumerate(rows):
        signal = np.ascontiguousarray(np.asarray(row.signal))
        byte_order = signal.dtype.byteorder
        if byte_order == "=":
            byte_order = "little" if np.little_endian else "big"
        elif byte_order == "<":
            byte_order = "little"
        elif byte_order == ">":
            byte_order = "big"
        elif byte_order == "|":
            byte_order = "not_applicable"
        metadata = {
            "row_index": row_index,
            "item_id": row.item_id,
            "participant_id": row.participant_id,
            "session_id": row.session_id,
            "trial_id": row.trial_id,
            "repeat_id": row.repeat_index,
            "outer_fold_id": row.outer_fold_id,
            "cue_id": list(row.cue),
            "timing_id": list(row.timing),
            "source_sample_start": row.source_sample_start,
            "source_sample_stop": row.source_sample_stop,
            "source_time_start_seconds": row.source_time_start_seconds,
            "source_time_stop_seconds": row.source_time_stop_seconds,
            "source_sampling_rate_hz": row.sampling_rate_hz,
            "true_length": row.true_length,
            "padding_mask": list(row.padding_mask),
            "channel_names": list(row.channel_names),
            "channel_roles": list(row.channel_roles),
            "channel_geometry": [list(value) if value is not None else None for value in row.channel_geometry],
            "signal": {
                "dtype": signal.dtype.str,
                "byte_order": byte_order,
                "shape": list(signal.shape),
            },
            "synthetic_target": targets[row.item_id],
        }
        metadata_bytes = _canonical_bytes(metadata)
        signal_bytes = signal.tobytes(order="C")
        digest.update(len(metadata_bytes).to_bytes(8, "big"))
        digest.update(metadata_bytes)
        digest.update(len(signal_bytes).to_bytes(8, "big"))
        digest.update(signal_bytes)
    return digest.hexdigest()


def _validate_fixture(
    rows: Sequence[g1.GeneratedRow], targets: Mapping[str, int]
) -> None:
    g1.validate_rows(rows)
    if len(rows) != 144 or set(targets) != {row.item_id for row in rows}:
        raise CommG2Refusal("G2-FIXTURE-COMPLETENESS")
    expected_order = []
    for participant in g1.PARTICIPANTS:
        for session in range(1, 4):
            for repeat_index in range(2):
                for target in range(4):
                    expected_order.append(
                        f"{participant}-s{session}-r{repeat_index}-c{target}"
                    )
    if [row.item_id for row in rows] != expected_order:
        raise CommG2Refusal("G2-FIXTURE-ROW-ORDER")
    groups: dict[tuple[str, str, int], list[int]] = defaultdict(list)
    for row in rows:
        target = targets.get(row.item_id)
        if type(target) is not int or target not in range(4):
            raise CommG2Refusal("G2-FIXTURE-TARGET")
        groups[(row.participant_id, row.session_id, row.repeat_index)].append(target)
    if len(groups) != 36 or any(sorted(values) != [0, 1, 2, 3] for values in groups.values()):
        raise CommG2Refusal("G2-FIXTURE-GRID")


def _validate_fold_job(job: FoldJob) -> None:
    source_ids = {row.item_id for row in job.source_rows}
    held_ids = {row.item_id for row in job.held_out_rows}
    if source_ids & held_ids:
        raise CommG2Refusal("G2-CAPABILITY-COLLISION")
    rows = (*job.source_rows, *job.held_out_rows)
    g1.validate_rows(rows)
    if set(job.source_targets) != source_ids:
        raise CommG2Refusal("G2-SOURCE-TARGET-INVENTORY")
    if any(row.participant_id == job.held_out_participant for row in job.source_rows):
        raise CommG2Refusal("G2-HELD-OUT-STATE-FIT")
    if not job.held_out_rows or any(
        row.participant_id != job.held_out_participant for row in job.held_out_rows
    ):
        raise CommG2Refusal("G2-HELD-OUT-SIGNAL-INVENTORY")
    if any(item_id in held_ids for item_id in job.source_targets):
        raise CommG2Refusal("G2-RESIDUALIZER-TARGET-LEAK")


def _fold_manifest(job: FoldJob) -> dict[str, Any]:
    source_ids = sorted(row.item_id for row in job.source_rows)
    held_ids = sorted(row.item_id for row in job.held_out_rows)
    source_fit_rows = [
        [row.item_id, job.source_targets[row.item_id]] for row in job.source_rows
    ]
    return {
        "held_out_participant": job.held_out_participant,
        "source_participants": sorted({row.participant_id for row in job.source_rows}),
        "source_item_ids": source_ids,
        "held_out_item_ids": held_ids,
        "source_item_ids_sha256": _hash_values(source_ids),
        "held_out_item_ids_sha256": _hash_values(held_ids),
        "source_fit_rows_sha256": _hash_values(source_fit_rows),
        "source_rows": len(source_ids),
        "held_out_rows": len(held_ids),
        "held_out_target_rows_delivered_to_predictor": 0,
    }


def _predict_fold(job: FoldJob) -> dict[str, Any]:
    """Run one held-out fold without possessing any held-out target."""

    np = g1._np()
    _validate_fold_job(job)
    source_views = [g1.feature_views(row) for row in job.source_rows]
    held_views = [g1.feature_views(row) for row in job.held_out_rows]
    source_context = np.stack([view["context"] for view in source_views])
    held_context = np.stack([view["context"] for view in held_views])
    source_central = np.stack([view["central"] for view in source_views])
    held_central = np.stack([view["central"] for view in held_views])
    source_y = np.asarray([job.source_targets[row.item_id] for row in job.source_rows])
    residualizer = g1._fit_residualizer(source_context, source_central)
    source_residual = g1._residualize(residualizer, source_context, source_central)
    held_residual = g1._residualize(residualizer, held_context, held_central)
    deranged = g1.corrected_source_derangement(
        job.source_rows, job.source_targets, source_residual
    )
    counts = Counter(source_y.tolist())
    predictions: list[dict[str, Any]] = []
    classifier_or_prior_fits = 0
    for condition in g1.CONDITIONS:
        if condition == "equal_prior":
            probabilities = np.full((len(job.held_out_rows), 4), 0.25)
        elif condition == "source_class_prior":
            classifier_or_prior_fits += 1
            prior = np.asarray([counts[index] for index in range(4)], dtype="float64")
            prior /= prior.sum()
            probabilities = np.tile(prior, (len(job.held_out_rows), 1))
        else:
            source_condition_residual = (
                deranged if condition == "P_plus_deranged_residual_EEG" else source_residual
            )
            source_x = g1._condition_features(
                condition, source_views, source_condition_residual
            )
            held_x = g1._condition_features(condition, held_views, held_residual)
            scaler, model = g1._fit_classifier(source_x, source_y)
            classifier_or_prior_fits += 1
            probabilities = model.predict_proba(scaler.transform(held_x))
        probabilities = np.clip(probabilities, 1e-6, 0.999999)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        for row, probability in zip(job.held_out_rows, probabilities, strict=True):
            predictions.append(
                {
                    "item_id": row.item_id,
                    "participant_id": row.participant_id,
                    "condition": condition,
                    "probabilities": probability.tolist(),
                }
            )
    if classifier_or_prior_fits != 9 or len(predictions) != 240:
        raise CommG2Refusal("G2-FOLD-SCHEDULE")
    return {
        "predictions": predictions,
        "manifest": _fold_manifest(job),
        "schedule": {
            "residualizer_fits": 1,
            "classifier_or_prior_fits": 9,
            "model_inference_runs": 10,
            "prediction_sets": 10,
            "prediction_rows": 240,
        },
    }


def _sanitized_child_environment() -> dict[str, str]:
    environment: dict[str, str] = {}
    for key in CHILD_ENVIRONMENT_KEYS:
        if key in g1.THREAD_ENVIRONMENT:
            environment[key] = "1"
        elif key == "PYTHONHASHSEED":
            environment[key] = "0"
        elif key in os.environ:
            environment[key] = os.environ[key]
    environment.setdefault("PATH", "/usr/bin:/bin")
    environment.setdefault("HOME", str(Path.home()))
    environment.setdefault("TMPDIR", tempfile.gettempdir())
    environment.setdefault("LANG", "C.UTF-8")
    return environment


def _environment_snapshot() -> dict[str, str]:
    return dict(os.environ)


def _process_tree_rss_bytes(root_pid: int) -> int:
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,rss="],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CommG2Refusal("G2-RSS-MONITOR") from exc
    rows: dict[int, tuple[int, int]] = {}
    for line in completed.stdout.splitlines():
        fields = line.split()
        if len(fields) != 3:
            continue
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


def _zero_rss_reader(_root_pid: int) -> int:
    return 0


def _terminate_child(process: Any, *, process_group: bool) -> None:
    if not process.is_alive():
        process.join(1)
        return
    try:
        if process_group:
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
    except (OSError, ProcessLookupError):
        process.terminate()
    process.join(2)
    if process.is_alive():
        try:
            if process_group:
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
        except (OSError, ProcessLookupError):
            process.kill()
        process.join(2)


def _child_entry(
    send: Any,
    operation: Callable[..., Any],
    args: tuple[Any, ...],
    expected_environment: Mapping[str, str],
    create_process_group: bool,
) -> None:
    try:
        if create_process_group:
            os.setsid()
        if dict(os.environ) != dict(expected_environment):
            actual_keys = set(os.environ)
            expected_keys = set(expected_environment)
            extra = ",".join(sorted(actual_keys - expected_keys)) or "none"
            missing = ",".join(sorted(expected_keys - actual_keys)) or "none"
            changed = ",".join(
                sorted(
                    key
                    for key in actual_keys & expected_keys
                    if os.environ[key] != expected_environment[key]
                )
            ) or "none"
            raise CommG2Refusal(
                f"G2-CHILD-ENVIRONMENT:extra={extra}:missing={missing}:changed={changed}"
            )
        send.send({"ok": True, "value": operation(*args)})
    except BaseException as exc:
        send.send({"ok": False, "error": f"{type(exc).__name__}:{exc}"})
    finally:
        send.close()


def _run_child(
    operation: Callable[..., Any],
    *args: Any,
    timeout_seconds: float = 60.0,
    create_process_group: bool = True,
    return_monitor: bool = False,
    rss_cap_bytes: int = CAPS["peak_process_tree_RSS_bytes"],
    rss_reader: Callable[[int], int] = _process_tree_rss_bytes,
    child_tempdir: str | Path | None = None,
) -> Any:
    context = multiprocessing.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    child_environment = _sanitized_child_environment()
    if child_tempdir is not None:
        temporary_directory = Path(child_tempdir).absolute()
        descriptor = _assert_directory_capability(temporary_directory)
        os.close(descriptor)
        child_environment["TMPDIR"] = str(temporary_directory)
    process = context.Process(
        target=_child_entry,
        args=(send, operation, args, child_environment, create_process_group),
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
    peak_RSS = 0
    try:
        while not receive.poll(0.25):
            elapsed = time.monotonic() - started
            peak_RSS = max(peak_RSS, rss_reader(os.getpid()))
            if peak_RSS > rss_cap_bytes:
                _terminate_child(process, process_group=create_process_group)
                raise CommG2Refusal("G2-RSS-CAP")
            if elapsed > timeout_seconds:
                _terminate_child(process, process_group=create_process_group)
                raise CommG2Refusal("G2-CHILD-TIMEOUT")
            if not process.is_alive() and not receive.poll():
                raise CommG2Refusal("G2-CHILD-EOF")
        message = receive.recv()
    except CommG2Refusal:
        _terminate_child(process, process_group=create_process_group)
        raise
    except EOFError as exc:
        raise CommG2Refusal("G2-CHILD-EOF") from exc
    finally:
        receive.close()
    process.join(2)
    if process.is_alive():
        _terminate_child(process, process_group=create_process_group)
        raise CommG2Refusal("G2-CHILD-JOIN")
    if process.exitcode != 0 or not message.get("ok"):
        raise CommG2Refusal(f"G2-CHILD-FAILED:{message.get('error', process.exitcode)}")
    monitor = {
        "runtime_seconds": time.monotonic() - started,
        "peak_process_tree_RSS_bytes": max(
            peak_RSS, rss_reader(os.getpid())
        ),
    }
    if return_monitor:
        return message["value"], monitor
    return message["value"]


def validate_prediction_inventory(
    predictions: Sequence[Mapping[str, Any]],
    fold_manifests: Sequence[Mapping[str, Any]] | None = None,
) -> None:
    if len(predictions) != 1440:
        raise CommG2Refusal("G2-PREDICTION-ROW-COUNT")
    keys: set[tuple[str, str, str]] = set()
    conditions = set(g1.CONDITIONS)
    expected: set[tuple[str, str, str]] | None = None
    if fold_manifests is not None:
        if len(fold_manifests) != 6:
            raise CommG2Refusal("G2-FOLD-MANIFEST-COUNT")
        expected = set()
        for manifest in fold_manifests:
            participant = str(manifest.get("held_out_participant", ""))
            item_ids = manifest.get("held_out_item_ids")
            if participant not in g1.PARTICIPANTS or not isinstance(item_ids, list):
                raise CommG2Refusal("G2-FOLD-MANIFEST-INVENTORY")
            if len(item_ids) != 24 or len(set(item_ids)) != 24:
                raise CommG2Refusal("G2-FOLD-MANIFEST-INVENTORY")
            for item_id in item_ids:
                expected.update(
                    (participant, str(item_id), condition) for condition in g1.CONDITIONS
                )
    for row in predictions:
        if set(row) != {"item_id", "participant_id", "condition", "probabilities"}:
            raise CommG2Refusal("G2-PREDICTION-FIELD-INVENTORY")
        key = (str(row["participant_id"]), str(row["item_id"]), str(row["condition"]))
        if key in keys:
            raise CommG2Refusal("G2-PREDICTION-DUPLICATE")
        keys.add(key)
        if row["condition"] not in conditions:
            raise CommG2Refusal("G2-PREDICTION-CONDITION")
        probabilities = row["probabilities"]
        if not isinstance(probabilities, list) or len(probabilities) != 4:
            raise CommG2Refusal("G2-PREDICTION-DIMENSION")
        values = [float(value) for value in probabilities]
        if any(not math.isfinite(value) for value in values):
            raise CommG2Refusal("G2-PREDICTION-NONFINITE")
        if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise CommG2Refusal("G2-PREDICTION-PROBABILITY-SUM")
    if len(keys) != 1440 or (expected is not None and keys != expected):
        raise CommG2Refusal("G2-PREDICTION-COMPLETENESS")


def build_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]], fold_manifests: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    validate_prediction_inventory(predictions, fold_manifests)
    if len(fold_manifests) != 6:
        raise CommG2Refusal("G2-FOLD-MANIFEST-COUNT")
    return {
        "schema_name": "neurodecodekit.comm_g2_prediction_freeze",
        "schema_version": "0.1.0",
        "contract_sha256": CONTRACT_SHA256,
        "prediction_rows": 1440,
        "prediction_sets": 60,
        "participants": 6,
        "conditions": list(g1.CONDITIONS),
        "private_prediction_payload_sha256": _hash_values(list(predictions)),
        "fold_manifests_sha256": _hash_values(list(fold_manifests)),
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
    }


def verify_prediction_freeze(
    predictions: Sequence[Mapping[str, Any]],
    fold_manifests: Sequence[Mapping[str, Any]],
    freeze: Mapping[str, Any],
) -> None:
    if dict(freeze) != build_prediction_freeze(predictions, fold_manifests):
        raise CommG2Refusal("G2-PREDICTION-FREEZE-TAMPER")


def _score_after_freeze(
    predictions: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    freeze: Mapping[str, Any],
    fold_manifests: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    verify_prediction_freeze(predictions, fold_manifests, freeze)
    if set(targets) != {str(row["item_id"]) for row in predictions}:
        raise CommG2Refusal("G2-SCORER-ROW-MISMATCH")
    g1_freeze = g1.build_prediction_freeze(predictions)
    score = g1.score_predictions(predictions, targets, g1_freeze)
    route = {
        "COMM-G1-R1": "COMM-G2-R1",
        "COMM-G1-R2": "COMM-G2-R2",
        "COMM-G1-R3": "COMM-G2-R3",
    }[score["route"]]
    return {**score, "route": route}


def _assert_directory_capability(path: Path) -> int:
    absolute = path.absolute()
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute.anchor, flags)
        for part in absolute.parts[1:]:
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
    except OSError as exc:
        if "descriptor" in locals():
            os.close(descriptor)
        raise CommG2Refusal("G2-DIRECTORY-CAPABILITY") from exc
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise CommG2Refusal("G2-DIRECTORY-CAPABILITY")
    return descriptor


def _secure_remove_tree(path: Path, expected_identity: tuple[int, int]) -> None:
    """Remove only the still-bound invocation directory using directory fds."""

    parent_fd = _assert_directory_capability(path.parent.absolute())
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        root_fd = os.open(path.name, flags, dir_fd=parent_fd)
        root_info = os.fstat(root_fd)
        if (root_info.st_dev, root_info.st_ino) != expected_identity:
            os.close(root_fd)
            raise CommG2Refusal("G2-CLEANUP-IDENTITY")

        def remove_contents(directory_fd: int) -> None:
            with os.scandir(directory_fd) as entries:
                names = [entry.name for entry in entries]
            for name in names:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    child_fd = os.open(name, flags, dir_fd=directory_fd)
                    try:
                        remove_contents(child_fd)
                    finally:
                        os.close(child_fd)
                    os.rmdir(name, dir_fd=directory_fd)
                else:
                    os.unlink(name, dir_fd=directory_fd)
            os.fsync(directory_fd)

        try:
            remove_contents(root_fd)
        finally:
            os.close(root_fd)
        current = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != expected_identity:
            raise CommG2Refusal("G2-CLEANUP-IDENTITY")
        os.rmdir(path.name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def _publish_no_replace(
    path: Path,
    payload: bytes,
    *,
    before_link: Callable[[], None] | None = None,
) -> None:
    parent = path.parent.absolute()
    directory_fd = _assert_directory_capability(parent)
    temporary_name = f".{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp"
    temporary_created = False
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        temporary_fd = os.open(temporary_name, flags, 0o600, dir_fd=directory_fd)
        temporary_created = True
        try:
            offset = 0
            while offset < len(payload):
                offset += os.write(temporary_fd, payload[offset:])
            os.fsync(temporary_fd)
        finally:
            os.close(temporary_fd)
        if before_link is not None:
            before_link()
        try:
            os.link(
                temporary_name,
                path.name,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
        except FileExistsError as exc:
            raise CommG2Refusal("G2-OUTPUT-CLOBBER") from exc
        except OSError as exc:
            raise CommG2Refusal("G2-OUTPUT-PUBLICATION") from exc
        os.unlink(temporary_name, dir_fd=directory_fd)
        temporary_created = False
        os.fsync(directory_fd)
        final_fd = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        try:
            info = os.fstat(final_fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size != len(payload) or info.st_nlink != 1:
                raise CommG2Refusal("G2-OUTPUT-READBACK")
        finally:
            os.close(final_fd)
    finally:
        if temporary_created:
            try:
                os.unlink(temporary_name, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
        os.close(directory_fd)


def _read_regular_no_follow(path: Path) -> bytes:
    parent_fd = _assert_directory_capability(path.parent.absolute())
    try:
        descriptor = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise CommG2Refusal("G2-OUTPUT-FILE-TYPE")
            chunks = []
            while chunk := os.read(descriptor, 1024 * 1024):
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise CommG2Refusal("G2-OUTPUT-FILE-TYPE") from exc
    finally:
        os.close(parent_fd)


def _measure_tree_bytes(path: Path) -> int:
    total = 0
    for root, directories, files in os.walk(path, followlinks=False):
        root_path = Path(root)
        for name in (*directories, *files):
            item = root_path / name
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise CommG2Refusal("G2-TEMPORARY-SYMLINK")
            if stat.S_ISREG(info.st_mode):
                total += info.st_size
    return total


def enforce_resource_caps(measurements: Mapping[str, int | float]) -> None:
    checks = (
        ("runtime_seconds", "wall_time_seconds", "G2-RUNTIME-CAP"),
        ("peak_process_tree_RSS_bytes", "peak_process_tree_RSS_bytes", "G2-RSS-CAP"),
        (
            "generated_input_bytes",
            "generated_input_bytes_total_maximum",
            "G2-GENERATED-INPUT-CAP",
        ),
        (
            "private_generated_output_bytes",
            "private_generated_output_bytes_total_maximum",
            "G2-PRIVATE-OUTPUT-CAP",
        ),
        ("public_output_bytes", "public_output_bytes_maximum", "G2-PUBLIC-OUTPUT-CAP"),
        ("temporary_disk_bytes", "temporary_disk_bytes_maximum", "G2-TEMPORARY-DISK-CAP"),
    )
    for field, cap, refusal in checks:
        value = measurements.get(field)
        if not isinstance(value, (int, float)) or value < 0:
            raise CommG2Refusal("G2-RESOURCE-MEASUREMENT")
        if value > CAPS[cap]:
            raise CommG2Refusal(refusal)


def _expect_refusal(family: str, operation: Callable[[], Any], expected: str) -> str:
    try:
        operation()
    except (CommG2Refusal, g1.CommG1Refusal) as exc:
        if expected not in str(exc):
            raise CommG2Refusal(f"G2-ADVERSARIAL-WRONG-REFUSAL:{family}") from exc
        return f"G2-{family}"
    raise CommG2Refusal(f"G2-ADVERSARIAL-ACCEPTED:{family}")


def _assert_replay_equivalence(first: Mapping[str, Any], second: Mapping[str, Any]) -> None:
    if _canonical_bytes(first) != _canonical_bytes(second):
        raise CommG2Refusal("G2-NONDETERMINISTIC-REPLAY")


def exercise_adversarial_refusals(
    rows: Sequence[g1.GeneratedRow],
    targets: Mapping[str, int],
    predictions: Sequence[Mapping[str, Any]],
    fold_manifests: Sequence[Mapping[str, Any]],
    freeze: Mapping[str, Any],
    workdir: Path,
) -> list[str]:
    """Execute every registered malformed generated family exactly once."""

    np = g1._np()
    row = rows[0]
    source_rows = tuple(value for value in rows if value.participant_id != g1.PARTICIPANTS[0])
    held_rows = tuple(value for value in rows if value.participant_id == g1.PARTICIPANTS[0])
    source_targets = {value.item_id: targets[value.item_id] for value in source_rows}
    good_job = FoldJob(g1.PARTICIPANTS[0], source_rows, source_targets, held_rows)
    refusals: list[str] = []
    sandbox = workdir / "adversarial"
    sandbox.mkdir()
    sandbox_info = sandbox.stat()
    sandbox_identity = (sandbox_info.st_dev, sandbox_info.st_ino)

    malformed_participant = replace(rows[1], item_id=rows[0].item_id)
    refusals.append(_expect_refusal("participant_collision", lambda: g1.validate_rows((row, malformed_participant)), "ITEM-COLLISION"))
    malformed_session = list(rows)
    malformed_session[24] = replace(malformed_session[24], session_id="ses-2")
    refusals.append(_expect_refusal("session_collision", lambda: _validate_fixture(malformed_session, targets), "FIXTURE-GRID"))
    leaked_row = good_job.held_out_rows[0]
    leak_job = replace(
        good_job,
        source_rows=(*good_job.source_rows, leaked_row),
        source_targets={**good_job.source_targets, leaked_row.item_id: targets[leaked_row.item_id]},
    )
    refusals.append(_expect_refusal("split_leak", lambda: _validate_fold_job(leak_job), "CAPABILITY"))
    escape_job = replace(good_job, held_out_rows=(*good_job.held_out_rows, good_job.source_rows[0]))
    refusals.append(_expect_refusal("capability_escape", lambda: _validate_fold_job(escape_job), "CAPABILITY"))
    reordered = [rows[1], rows[0], *rows[2:]]
    refusals.append(_expect_refusal("row_reorder", lambda: _validate_fixture(reordered, targets), "ROW-ORDER"))
    refusals.append(_expect_refusal("role_mismatch", lambda: g1.validate_rows((replace(row, channel_roles=("bad",) * 14),)), "CHANNEL-ROLE"))
    refusals.append(_expect_refusal("channel_mismatch", lambda: g1.validate_rows((replace(row, channel_names=("bad",) * 14),)), "CHANNEL-ROLE"))
    refusals.append(_expect_refusal("mask_mismatch", lambda: g1.validate_rows((replace(row, padding_mask=(True,) + row.padding_mask[1:]),)), "MASK-LENGTH"))
    refusals.append(_expect_refusal("timestamp_mismatch", lambda: g1.validate_rows((replace(row, source_sample_stop=row.source_sample_stop + 1),)), "SAMPLE-TIMESTAMP"))
    refusals.append(_expect_refusal("geometry_mismatch", lambda: g1.validate_rows((replace(row, channel_geometry=(None,) * 14),)), "CHANNEL-GEOMETRY"))
    refusals.append(_expect_refusal("sampling_rate_mismatch", lambda: g1.validate_rows((replace(row, sampling_rate_hz=127),)), "SAMPLING-RATE"))
    held_state_job = replace(
        good_job,
        source_rows=(*good_job.source_rows, leaked_row),
        source_targets={**good_job.source_targets, leaked_row.item_id: targets[leaked_row.item_id]},
        held_out_rows=good_job.held_out_rows[1:],
    )
    refusals.append(_expect_refusal("held_out_state_fit", lambda: _validate_fold_job(held_state_job), "HELD-OUT-STATE-FIT"))
    target_leak = replace(good_job, source_targets={**good_job.source_targets, held_rows[0].item_id: targets[held_rows[0].item_id]})
    refusals.append(_expect_refusal("residualizer_target_leak", lambda: _validate_fold_job(target_leak), "SOURCE-TARGET-INVENTORY"))
    refusals.append(_expect_refusal("derangement_scope_mismatch", lambda: g1.corrected_source_derangement(source_rows[:-1], source_targets, np.zeros((len(source_rows) - 1, 16))), "INCOMPLETE-GROUP"))
    tampered = [dict(value) for value in predictions]
    tampered[0] = {**tampered[0], "probabilities": [0.7, 0.1, 0.1, 0.1]}
    refusals.append(_expect_refusal("prediction_tamper", lambda: verify_prediction_freeze(tampered, fold_manifests, freeze), "FREEZE-TAMPER"))
    refusals.append(_expect_refusal("prediction_duplicate", lambda: validate_prediction_inventory([*predictions[:-1], predictions[0]], fold_manifests), "DUPLICATE"))
    refusals.append(_expect_refusal("prediction_missing", lambda: validate_prediction_inventory(predictions[:-1], fold_manifests), "ROW-COUNT"))
    nonfinite = [dict(value) for value in predictions]
    nonfinite[0] = {**nonfinite[0], "probabilities": [float("nan"), 0.3, 0.3, 0.4]}
    refusals.append(_expect_refusal("probability_nonfinite", lambda: validate_prediction_inventory(nonfinite, fold_manifests), "NONFINITE"))
    bad_sum = [dict(value) for value in predictions]
    bad_sum[0] = {**bad_sum[0], "probabilities": [0.4, 0.3, 0.2, 0.2]}
    refusals.append(_expect_refusal("probability_sum_mismatch", lambda: validate_prediction_inventory(bad_sum, fold_manifests), "PROBABILITY-SUM"))
    vault = SealedSyntheticTargetVault(targets)
    refusals.append(_expect_refusal("pre_freeze_target_delivery", lambda: vault.deliver(freeze_green=False), "PRE-FREEZE"))
    vault.deliver(freeze_green=True)
    refusals.append(_expect_refusal("repeated_target_delivery", lambda: vault.deliver(freeze_green=True), "REPEATED"))
    missing_targets = dict(targets)
    missing_targets.pop(next(iter(missing_targets)))
    refusals.append(_expect_refusal("scorer_row_mismatch", lambda: _score_after_freeze(predictions, missing_targets, freeze, fold_manifests), "SCORER-ROW-MISMATCH"))

    existing = sandbox / "existing.json"
    existing.write_bytes(b"x")
    refusals.append(_expect_refusal("output_clobber", lambda: _publish_no_replace(existing, b"y"), "OUTPUT-CLOBBER"))
    real_parent = sandbox / "real-parent"
    real_parent.mkdir()
    ancestor_link = sandbox / "ancestor-link"
    ancestor_link.symlink_to(real_parent, target_is_directory=True)
    refusals.append(_expect_refusal("ancestor_symlink_escape", lambda: _publish_no_replace(ancestor_link / "x", b"x"), "DIRECTORY-CAPABILITY"))
    leaf_link = sandbox / "leaf-link"
    leaf_target = sandbox / "leaf-target"
    leaf_target.write_bytes(b"x")
    leaf_link.symlink_to(leaf_target)
    refusals.append(_expect_refusal("leaf_symlink_escape", lambda: _publish_no_replace(leaf_link, b"x"), "OUTPUT-CLOBBER"))
    race = sandbox / "race.json"
    refusals.append(
        _expect_refusal(
            "publication_race",
            lambda: _publish_no_replace(
                race,
                b"x",
                before_link=lambda: race.write_bytes(b"racer"),
            ),
            "OUTPUT-CLOBBER",
        )
    )
    directory_output = sandbox / "directory-output"
    directory_output.mkdir()
    refusals.append(_expect_refusal("nonregular_output", lambda: _read_regular_no_follow(directory_output), "OUTPUT-FILE-TYPE"))
    outside = workdir.parent / "outside.json"
    refusals.append(_expect_refusal("cross_workdir_traversal", lambda: _require_within_workdir(outside, workdir), "WORKDIR-ESCAPE"))

    zero = {
        "runtime_seconds": 0,
        "peak_process_tree_RSS_bytes": 0,
        "generated_input_bytes": 0,
        "private_generated_output_bytes": 0,
        "public_output_bytes": 0,
        "temporary_disk_bytes": 0,
    }
    resource_cases = (
        ("resource_runtime_cap_breach", "runtime_seconds", CAPS["wall_time_seconds"] + 1, "RUNTIME-CAP"),
        ("resource_RSS_cap_breach", "peak_process_tree_RSS_bytes", CAPS["peak_process_tree_RSS_bytes"] + 1, "RSS-CAP"),
        ("resource_generated_input_cap_breach", "generated_input_bytes", CAPS["generated_input_bytes_total_maximum"] + 1, "GENERATED-INPUT-CAP"),
        ("resource_private_output_cap_breach", "private_generated_output_bytes", CAPS["private_generated_output_bytes_total_maximum"] + 1, "PRIVATE-OUTPUT-CAP"),
        ("resource_public_output_cap_breach", "public_output_bytes", CAPS["public_output_bytes_maximum"] + 1, "PUBLIC-OUTPUT-CAP"),
    )
    for family, field, value, expected in resource_cases:
        measurements = {**zero, field: value}
        refusals.append(_expect_refusal(family, lambda measurements=measurements: enforce_resource_caps(measurements), expected))
    refusals.append(_expect_refusal("nondeterministic_fixture_replay", lambda: _assert_replay_equivalence({"fixture": "a"}, {"fixture": "b"}), "NONDETERMINISTIC-REPLAY"))
    refusals.append(_expect_refusal("nondeterministic_prediction_replay", lambda: _assert_replay_equivalence({"prediction": "a"}, {"prediction": "b"}), "NONDETERMINISTIC-REPLAY"))
    if tuple(value.removeprefix("G2-") for value in refusals) != ADVERSARIAL_FAMILIES:
        raise CommG2Refusal("G2-ADVERSARIAL-COMPLETENESS")
    _secure_remove_tree(sandbox, sandbox_identity)
    return refusals


def _require_within_workdir(path: Path, workdir: Path) -> None:
    try:
        path.absolute().relative_to(workdir.absolute())
    except ValueError as exc:
        raise CommG2Refusal("G2-WORKDIR-ESCAPE") from exc


def _require_output_within_repository(output: Path, repository: Path) -> None:
    try:
        output.absolute().relative_to(repository.absolute())
    except ValueError as exc:
        raise CommG2Refusal("G2-OUTPUT-OUTSIDE-REPOSITORY") from exc


def _run_replay(replay_id: str, workdir_text: str) -> dict[str, Any]:
    started = time.monotonic()
    workdir = Path(workdir_text)
    descriptor = _assert_directory_capability(workdir)
    os.close(descriptor)
    if any(workdir.iterdir()):
        raise CommG2Refusal("G2-WORKDIR-NOT-CLEAN")
    identity = workdir.stat()
    fixture_digests: dict[str, str] = {}
    shortcut_results: dict[str, Any] = {}
    generated_input_bytes = 0
    positive_rows: list[g1.GeneratedRow] | None = None
    positive_targets: dict[str, int] | None = None
    for case_family in g1.CASE_FAMILIES:
        rows, targets, input_bytes = g1.generate_fixture(case_family)
        fixture_digests[case_family] = canonical_fixture_digest(rows, targets)
        generated_input_bytes += input_bytes
        if case_family == "residual_EEG_increment":
            positive_rows = rows
            positive_targets = targets
        else:
            shortcut_results[case_family] = g1.validate_shortcut_fixture(
                case_family, rows, targets
            )
    assert positive_rows is not None
    assert positive_targets is not None
    vault = SealedSyntheticTargetVault(positive_targets)
    predictions: list[dict[str, Any]] = []
    fold_manifests: list[dict[str, Any]] = []
    schedule = {
        "residualizer_fits": 0,
        "classifier_or_prior_fits": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "prediction_rows": 0,
    }
    worker_peak_RSS = 0
    for held_out in g1.PARTICIPANTS:
        capability, _ = g1.build_fold_capability(
            positive_rows, positive_targets, held_out
        )
        job = FoldJob(
            held_out_participant=held_out,
            source_rows=capability.source_rows,
            source_targets=capability.source_targets,
            held_out_rows=capability.held_out_rows,
        )
        fold_result = _run_child(
            _predict_fold_with_peak,
            job,
            timeout_seconds=45,
            create_process_group=False,
            rss_reader=_zero_rss_reader,
        )
        predictions.extend(fold_result["predictions"])
        fold_manifests.append(fold_result["manifest"])
        worker_peak_RSS = max(worker_peak_RSS, fold_result["peak_process_RSS_bytes"])
        for field in schedule:
            schedule[field] += fold_result["schedule"][field]
    expected_schedule = {
        "residualizer_fits": 6,
        "classifier_or_prior_fits": 54,
        "model_inference_runs": 60,
        "prediction_sets": 60,
        "prediction_rows": 1440,
    }
    if schedule != expected_schedule:
        raise CommG2Refusal("G2-REPLAY-SCHEDULE")
    freeze = build_prediction_freeze(predictions, fold_manifests)
    delivered_targets = vault.deliver(freeze_green=True)
    score = _run_child(
        _score_after_freeze,
        predictions,
        delivered_targets,
        freeze,
        fold_manifests,
        timeout_seconds=20,
        create_process_group=False,
        rss_reader=_zero_rss_reader,
    )
    refusal_ids = exercise_adversarial_refusals(
        positive_rows,
        positive_targets,
        predictions,
        fold_manifests,
        freeze,
        workdir,
    )
    deterministic = {
        "fixture_digests": fixture_digests,
        "shortcut_results": shortcut_results,
        "fold_manifests": fold_manifests,
        "schedule": schedule,
        "prediction_freeze": freeze,
        "score": score,
        "router_outcome": score["route"],
        "adversarial_refusal_ids": refusal_ids,
    }
    replay_payload = _canonical_bytes(deterministic)
    replay_record = workdir / "replay-proof.json"
    _publish_no_replace(replay_record, replay_payload)
    if _read_regular_no_follow(replay_record) != replay_payload:
        raise CommG2Refusal("G2-REPLAY-READBACK")
    runtime = time.monotonic() - started
    replay_peak_RSS = max(worker_peak_RSS, g1.peak_process_tree_rss_bytes())
    return {
        "replay_id": replay_id,
        "process_id": os.getpid(),
        "workdir_identity": [identity.st_dev, identity.st_ino],
        "deterministic": deterministic,
        "deterministic_sha256": _sha256(replay_payload),
        "measurements": {
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": replay_peak_RSS,
            "generated_input_bytes": generated_input_bytes,
            "private_generated_output_bytes": len(_canonical_bytes(predictions)),
            "temporary_disk_bytes": _measure_tree_bytes(workdir),
        },
    }


def _predict_fold_with_peak(job: FoldJob) -> dict[str, Any]:
    result = _predict_fold(job)
    result["peak_process_RSS_bytes"] = g1.peak_process_tree_rss_bytes()
    return result


def _result_payload(result: dict[str, Any]) -> bytes:
    previous = -1
    for _ in range(8):
        payload = _canonical_bytes(result)
        result["measurements"]["public_output_bytes"] = len(payload)
        if len(payload) == previous:
            return _canonical_bytes(result)
        previous = len(payload)
    raise CommG2Refusal("G2-PUBLIC-BYTE-ACCOUNTING")


def plan() -> dict[str, Any]:
    return {
        "lane_id": LANE_ID,
        "generated_only": True,
        "full_isolated_replays": 2,
        "parameter_updates_per_replay": 60,
        "total_parameter_updates": 120,
        "total_prediction_sets": 120,
        "total_prediction_rows": 2880,
        "minimum_distinct_refusal_ids": 35,
        "real_or_private_operations": 0,
        "scientific_value": "none_generated_engineering_only",
    }


def run_generated_qualification(
    output_path: str | Path,
    *,
    root: str | Path | None = None,
    remote_proof_collector: Callable[[str | Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run one proof-gated, two-replay generated qualification."""

    g1.assert_single_thread_environment()
    repository = (Path(root) if root is not None else _repo_root()).absolute()
    repository_fd = _assert_directory_capability(repository)
    os.close(repository_fd)
    load_registration(repository)
    load_implementation_record(repository)
    output_argument = Path(output_path)
    if ".." in output_argument.parts:
        raise CommG2Refusal("G2-OUTPUT-PATH")
    output = output_argument.expanduser().absolute()
    _require_output_within_repository(output, repository)
    if output.exists() or output.is_symlink():
        raise CommG2Refusal("G2-OUTPUT-CLOBBER")
    if not output.parent.exists():
        raise CommG2Refusal("G2-OUTPUT-PARENT-MISSING")
    lowered = {part.lower() for part in output.parts}
    if lowered.intersection({"data", ".codex_work"}):
        raise CommG2Refusal("G2-PROTECTED-OUTPUT-ROOT")
    parent_fd = _assert_directory_capability(output.parent)
    os.close(parent_fd)

    from neurodecodekit.experiments import dreyer_c5r_1 as proof_tools

    collector = remote_proof_collector or proof_tools.collect_remote_green_proof
    try:
        proof = proof_tools.validate_remote_green_proof(dict(collector(repository)))
    except (proof_tools.DreyerExperimentRefusal, KeyError, TypeError) as exc:
        raise CommG2Refusal("G2-REMOTE-GREEN-PROOF-FAILED") from exc

    started = time.monotonic()
    temporary_root = Path(
        tempfile.mkdtemp(prefix=".comm-g2-", dir=str(output.parent))
    )
    temporary_info = temporary_root.stat()
    temporary_identity = (temporary_info.st_dev, temporary_info.st_ino)
    try:
        expected_generated_input = 2 * len(g1.CASE_FAMILIES) * 144 * 14 * 128 * 8
        if expected_generated_input > CAPS["generated_input_bytes_total_maximum"]:
            raise CommG2Refusal("G2-GENERATED-INPUT-PREFLIGHT")
        replay_results = []
        for index in range(2):
            workdir = temporary_root / f"replay-{index + 1}"
            workdir.mkdir(mode=0o700)
            runtime_temp = temporary_root / f"runtime-{index + 1}"
            runtime_temp.mkdir(mode=0o700)
            replay_result, replay_monitor = _run_child(
                    _run_replay,
                    f"replay-{index + 1}",
                    str(workdir),
                    timeout_seconds=85,
                    return_monitor=True,
                    child_tempdir=runtime_temp,
                )
            replay_result["monitor"] = replay_monitor
            replay_results.append(replay_result)
            enforce_resource_caps(
                {
                    "runtime_seconds": time.monotonic() - started,
                    "peak_process_tree_RSS_bytes": max(
                        value["monitor"]["peak_process_tree_RSS_bytes"]
                        for value in replay_results
                    ),
                    "generated_input_bytes": sum(
                        value["measurements"]["generated_input_bytes"]
                        for value in replay_results
                    ),
                    "private_generated_output_bytes": sum(
                        value["measurements"]["private_generated_output_bytes"]
                        for value in replay_results
                    ),
                    "public_output_bytes": 0,
                    "temporary_disk_bytes": _measure_tree_bytes(temporary_root),
                }
            )
        first, second = replay_results
        if first["process_id"] == second["process_id"]:
            raise CommG2Refusal("G2-REPLAY-PROCESS-ISOLATION")
        if first["workdir_identity"] == second["workdir_identity"]:
            raise CommG2Refusal("G2-REPLAY-WORKDIR-ISOLATION")
        _assert_replay_equivalence(first["deterministic"], second["deterministic"])
        runtime = time.monotonic() - started
        measurements = {
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": max(
                first["measurements"]["peak_process_tree_RSS_bytes"],
                second["measurements"]["peak_process_tree_RSS_bytes"],
                first["monitor"]["peak_process_tree_RSS_bytes"],
                second["monitor"]["peak_process_tree_RSS_bytes"],
                g1.peak_process_tree_rss_bytes(),
            ),
            "generated_input_bytes": sum(
                value["measurements"]["generated_input_bytes"]
                for value in replay_results
            ),
            "private_generated_output_bytes": sum(
                value["measurements"]["private_generated_output_bytes"]
                for value in replay_results
            ),
            "temporary_disk_bytes": _measure_tree_bytes(temporary_root),
            "public_output_bytes": 0,
            "producer_causal": True,
            "required_context_seconds": 1.0,
            "right_context_seconds": 0.0,
            "end_to_end_latency_measured": False,
        }
        deterministic = first["deterministic"]
        result = {
            "schema_name": "neurodecodekit.comm_g2_generated_proof_qualification_result",
            "schema_version": "0.1.0",
            "lane_id": LANE_ID,
            "status": "completed_generated_only_no_scientific_value",
            "binding_route": deterministic["router_outcome"],
            "registration": {
                "contract_sha256": CONTRACT_SHA256,
                "frozen_COMM_G1_module_sha256": FROZEN_G1_MODULE_SHA256,
            },
            "implementation_proof": proof,
            "replay_equivalence": {
                "separate_processes": True,
                "separate_clean_workdirs": True,
                "deterministic_sha256": first["deterministic_sha256"],
                "byte_equivalent": True,
            },
            "aggregate_proof": {
                "fixture_digests": deterministic["fixture_digests"],
                "fold_manifests_sha256": _hash_values(deterministic["fold_manifests"]),
                "prediction_freeze": deterministic["prediction_freeze"],
                "score": {
                    "route": deterministic["score"]["route"],
                    "candidate_delta_over_P": deterministic["score"]["candidate_delta_over_P"],
                    "candidate_delta_over_deranged": deterministic["score"]["candidate_delta_over_deranged"],
                    "positive_participants": deterministic["score"]["positive_participants"],
                    "scientific_value": "none_generated_engineering_only",
                },
            },
            "schedule": {
                "full_isolated_replays": 2,
                "parameter_updates_per_replay": 60,
                "total_parameter_updates": 120,
                "prediction_sets_per_replay": 60,
                "total_prediction_sets": 120,
                "prediction_rows_per_replay": 1440,
                "total_prediction_rows": 2880,
                "synthetic_target_deliveries": 2,
                "synthetic_scores": 2,
                "post_target_updates": 0,
            },
            "adversarial_qualification": {
                "refusal_count": len(deterministic["adversarial_refusal_ids"]),
                "refusal_ids": deterministic["adversarial_refusal_ids"],
                "every_named_family_executed": True,
            },
            "measurements": measurements,
            "access_counters": {
                "real_or_private_path_reads": 0,
                "network_bytes": 0,
                "real_signal_samples": 0,
                "real_targets_or_labels": 0,
                "real_training_runs": 0,
                "real_model_inference_runs": 0,
                "provider_calls": 0,
                "stream_or_device_operations": 0,
                "release_operations": 0,
                "scientific_claim_upgrades": 0,
            },
            "claim_boundary": {
                "scientific_value": "none_generated_engineering_only",
                "real_EEG_accessed": False,
                "communication_decoding_established": False,
                "EEG_beyond_peripheral_controls_established": False,
                "unseen_person_generalization_established": False,
                "live_neural_decoding_established": False,
            },
        }
        payload = _result_payload(result)
        measurements["public_output_bytes"] = len(payload)
        enforce_resource_caps(measurements)
        _publish_no_replace(output, payload)
        return result
    finally:
        _secure_remove_tree(temporary_root, temporary_identity)


def inspect_result(path: str | Path) -> dict[str, Any]:
    value = json.loads(_read_regular_no_follow(Path(path).absolute()))
    if value.get("schema_name") != "neurodecodekit.comm_g2_generated_proof_qualification_result":
        raise CommG2Refusal("G2-INSPECT-SCHEMA")
    return {
        "lane_id": value["lane_id"],
        "status": value["status"],
        "binding_route": value["binding_route"],
        "replay_equivalence": value["replay_equivalence"],
        "schedule": value["schedule"],
        "adversarial_qualification": value["adversarial_qualification"],
        "measurements": value["measurements"],
        "claim_boundary": value["claim_boundary"],
    }
