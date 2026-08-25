"""Proof-gated real Stage P controller for BNCI-C3C5-1."""

from __future__ import annotations

import hashlib
import hmac
import io
import json
import multiprocessing
import os
import secrets
import shutil
import stat
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import bnci_2014_001_stage_q as q_core
from neurodecodekit.datasets import bnci_2014_001_stage_q_live as q_live
from neurodecodekit.evaluation import bnci_2014_001_score as scorer
from neurodecodekit.experiments import bnci_2014_001_cross_participant_eeg_gain as model_core

LANE_ID = "BNCI-C3C5-1-P"
SCHEMA_VERSION = "0.1.0"
STAGE_Q_RESULT_RELATIVE_PATH = Path("registries/bnci_2014_001_stage_q_result.v0.json")
STAGE_Q_RESULT_SHA256 = "2c896e029627997e8e98ff7d99d41b376a69d85d8d1b7773387db44790c851ee"
STAGE_Q_RESULT_COMMIT = "9832ae5e60c42bf975ccfdd22740267ef802d191"
STAGE_Q_RESULT_CI_RUN_ID = 32_827_957_362
STAGE_Q_RESULT_BASE_JOB_ID = 97_740_061_957
STAGE_Q_RESULT_OPTIONAL_JOB_ID = 97_740_061_602
ACTIVATION_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_stage_p_implementation_activation.v0.json"
)
OUTPUT_RELATIVE_PATH = Path(".codex_work/bnci_c3c5/stage_p_v0")
MARKER_RELATIVE_PATH = Path(".codex_work/bnci_c3c5/stage_p_v0.consumed.json")
PUBLIC_FREEZE_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_stage_p_prediction_freeze.v0.json"
)
PRIVATE_MANIFEST_NAME = "manifest.private.v0.json"
PRIVATE_BINDING_KEY_NAME = "source_binding_key.sealed_until_T.private.v0.bin"
PARTICIPANTS = q_core.PARTICIPANTS
CONDITIONS = scorer.CONDITIONS
EXPECTED_FITS_PER_FOLD = 52
EXPECTED_PREDICTION_SETS_PER_FOLD = 55
EXPECTED_PREDICTION_ROWS_PER_FOLD = q_core.HELD_OUT_E_ROWS_PER_FOLD * len(CONDITIONS)
EXPECTED_TOTAL_FITS = len(PARTICIPANTS) * EXPECTED_FITS_PER_FOLD
EXPECTED_TOTAL_PREDICTION_SETS = len(PARTICIPANTS) * EXPECTED_PREDICTION_SETS_PER_FOLD
EXPECTED_TOTAL_PREDICTION_ROWS = len(PARTICIPANTS) * EXPECTED_PREDICTION_ROWS_PER_FOLD
MINIMUM_FREE_DISK_BYTES = 2 * 1024 * 1024 * 1024
PRIVATE_LAYOUT_BOUND_BYTES = 256 * 1024 * 1024
IMPLEMENTATION_ARTIFACTS = (
    "src/neurodecodekit/experiments/bnci_2014_001_stage_p_live.py",
    "src/neurodecodekit/evaluation/bnci_2014_001_stage_t_live.py",
    "src/neurodecodekit/bnci_c3c5_stage_p_t_cli.py",
    "tests/test_bnci_2014_001_stage_p_t_live.py",
    "docs/BNCI_2014_001_STAGE_P_T_IMPLEMENTATION.md",
    "registries/bnci_2014_001_stage_p_t_implementation.v0.json",
)


class BNCIStagePRefusal(RuntimeError):
    """Fail-closed Stage P refusal."""


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _is_commit(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )


def _direct_regular(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise BNCIStagePRefusal("Stage P input is not a single-link regular file")
    return info


def _read_direct(path: Path, *, expected_bytes: int | None = None, expected_sha256: str | None = None) -> bytes:
    info = _direct_regular(path)
    if expected_bytes is not None and info.st_size != expected_bytes:
        raise BNCIStagePRefusal("Stage P input size differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
    finally:
        os.close(descriptor)
    if len(payload) != info.st_size:
        raise BNCIStagePRefusal("Stage P input changed while reading")
    if expected_sha256 is not None and _sha256(payload) != expected_sha256:
        raise BNCIStagePRefusal("Stage P input hash differs")
    return payload


def _safe_child(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise BNCIStagePRefusal("Stage P private capability path is unsafe")
    resolved = root.joinpath(candidate)
    if resolved.parent != root and root not in resolved.parents:
        raise BNCIStagePRefusal("Stage P private capability escaped its root")
    return resolved


def _artifact_identity(root: Path, relative_path: str) -> dict[str, Any]:
    payload = (root / relative_path).read_bytes()
    return {"path": relative_path, "bytes": len(payload), "sha256": _sha256(payload)}


def validate_activation_document(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "lane_id",
        "status",
        "green_stage_q_result",
        "green_implementation",
        "implementation_artifacts",
        "authority",
    }:
        raise BNCIStagePRefusal("Stage P activation fields differ")
    if value.get("lane_id") != LANE_ID or value.get("status") != "remotely_green_stage_p_enabled":
        raise BNCIStagePRefusal("Stage P activation status differs")
    if value.get("green_stage_q_result") != {
        "commit": STAGE_Q_RESULT_COMMIT,
        "CI_run_id": STAGE_Q_RESULT_CI_RUN_ID,
        "base_python_job_id": STAGE_Q_RESULT_BASE_JOB_ID,
        "optional_neuro_readers_job_id": STAGE_Q_RESULT_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
    }:
        raise BNCIStagePRefusal("Stage P green Stage Q binding differs")
    green = value.get("green_implementation")
    if (
        not isinstance(green, dict)
        or set(green)
        != {
            "commit",
            "CI_run_id",
            "CI_head_sha",
            "CI_conclusion",
            "base_python_job_id",
            "base_python_job_name",
            "base_python_job_conclusion",
            "optional_neuro_readers_job_id",
            "optional_neuro_readers_job_name",
            "optional_neuro_readers_job_conclusion",
            "both_required_jobs_green",
        }
        or not _is_commit(green.get("commit"))
        or green.get("CI_head_sha") != green.get("commit")
        or green.get("CI_conclusion") != "success"
        or green.get("base_python_job_name") != "Base Python"
        or green.get("base_python_job_conclusion") != "success"
        or green.get("optional_neuro_readers_job_name") != "Optional Neuro Readers"
        or green.get("optional_neuro_readers_job_conclusion") != "success"
        or green.get("both_required_jobs_green") is not True
        or not all(
            isinstance(green.get(field), int) and green[field] > 0
            for field in ("CI_run_id", "base_python_job_id", "optional_neuro_readers_job_id")
        )
    ):
        raise BNCIStagePRefusal("Stage P implementation proof differs")
    artifacts = value.get("implementation_artifacts")
    if not isinstance(artifacts, list) or [row.get("path") for row in artifacts if isinstance(row, dict)] != list(IMPLEMENTATION_ARTIFACTS):
        raise BNCIStagePRefusal("Stage P implementation artifact inventory differs")
    if any(
        not isinstance(row, dict)
        or set(row) != {"path", "bytes", "sha256"}
        or not isinstance(row.get("bytes"), int)
        or row["bytes"] <= 0
        or not _is_sha256(row.get("sha256"))
        for row in artifacts
    ):
        raise BNCIStagePRefusal("Stage P implementation artifact identity differs")
    if value.get("authority") != {
        "one_real_Stage_P_execution": True,
        "parameter_update_fits_maximum": 540,
        "prediction_sets_maximum": 900,
        "held_out_E_target_delivery": False,
        "held_out_T_signal_or_target_delivery": False,
        "Stage_T": False,
        "reruns": 0,
        "post_target_updates": 0,
        "claim_upgrade": False,
    }:
        raise BNCIStagePRefusal("Stage P authority differs")
    return value


def read_green_activation(root: str | Path) -> dict[str, Any]:
    repo = Path(root).resolve()
    payload = (repo / ACTIVATION_RELATIVE_PATH).read_bytes()
    try:
        activation = validate_activation_document(json.loads(payload))
    except json.JSONDecodeError as exc:
        raise BNCIStagePRefusal("Stage P activation JSON is invalid") from exc
    green = activation["green_implementation"]
    for expected, row in zip(IMPLEMENTATION_ARTIFACTS, activation["implementation_artifacts"], strict=True):
        if row != _artifact_identity(repo, expected):
            raise BNCIStagePRefusal("Stage P implementation artifact changed")
        if q_core._git_output(repo, "show", f"{green['commit']}:{expected}") != (repo / expected).read_bytes():
            raise BNCIStagePRefusal("Stage P artifact differs from its green commit")
    if q_core._git_output(repo, "show", f"HEAD:{ACTIVATION_RELATIVE_PATH.as_posix()}") != payload:
        raise BNCIStagePRefusal("Stage P activation differs from HEAD")
    q_core._git_output(repo, "merge-base", "--is-ancestor", STAGE_Q_RESULT_COMMIT, "HEAD")
    q_core._git_output(repo, "merge-base", "--is-ancestor", green["commit"], "HEAD")
    branch = q_core._git_output(repo, "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    head = q_core._git_output(repo, "rev-parse", "HEAD").strip()
    remote = q_core._git_output(repo, "rev-parse", f"refs/remotes/origin/{branch}").strip()
    if not branch or branch == "HEAD" or head != remote:
        raise BNCIStagePRefusal("Stage P activation is not the pushed branch HEAD")
    subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=repo, check=True, timeout=30)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--"], cwd=repo, check=True, timeout=30)
    return activation


def _load_npz(payload: bytes) -> dict[str, Any]:
    np = q_core._np()
    try:
        with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
            return {name: archive[name] for name in archive.files}
    except Exception as exc:
        raise BNCIStagePRefusal("Stage P private NPZ is malformed") from exc


def _decode_row_id(value: Any) -> str:
    if isinstance(value, bytes):
        try:
            decoded = value.decode("ascii")
        except UnicodeDecodeError as exc:
            raise BNCIStagePRefusal("Stage P opaque identity is not ASCII") from exc
    else:
        decoded = str(value)
    if not _is_sha256(decoded):
        raise BNCIStagePRefusal("Stage P opaque identity is invalid")
    return decoded


def _expected_grid(participant: str, session: str) -> set[tuple[str, str, int, int]]:
    return {
        (participant, session, run, trial)
        for run in range(q_core.TASK_RUNS_PER_FILE)
        for trial in range(q_core.TRIALS_PER_RUN)
    }


def validate_exact_identity_grid(
    rows: Sequence[Mapping[str, Any]],
    *,
    participant_sessions: Sequence[tuple[str, str]],
) -> None:
    expected = set().union(*(_expected_grid(participant, session) for participant, session in participant_sessions))
    coordinates: set[tuple[str, str, int, int]] = set()
    row_ids: set[str] = set()
    for row in rows:
        coordinate = (
            str(row.get("participant")),
            str(row.get("session")),
            int(row.get("run_ordinal", -1)),
            int(row.get("trial_ordinal", -1)),
        )
        row_id = str(row.get("opaque_row_id"))
        if coordinate in coordinates or row_id in row_ids:
            raise BNCIStagePRefusal("Stage P identity grid is duplicated")
        coordinates.add(coordinate)
        row_ids.add(row_id)
    if coordinates != expected or len(rows) != len(expected):
        raise BNCIStagePRefusal("Stage P identity grid is incomplete")


def _rows_from_shard(payload: bytes, record: Mapping[str, Any]) -> list[dict[str, Any]]:
    np = q_core._np()
    arrays = _load_npz(payload)
    expected_fields = set(q_core.FEATURE_DIMENSIONS) | {
        "participant_index",
        "session_index",
        "run_ordinal",
        "trial_ordinal",
        "trial_start_sample",
        "opaque_row_id",
    }
    if set(arrays) != expected_fields:
        raise BNCIStagePRefusal("Stage P signal shard field inventory differs")
    participant = record.get("participant")
    session = record.get("session")
    if participant not in PARTICIPANTS or session not in q_core.SESSIONS:
        raise BNCIStagePRefusal("Stage P signal shard identity differs")
    rows_count = q_core.HELD_OUT_E_ROWS_PER_FOLD
    for name, dimension in q_core.FEATURE_DIMENSIONS.items():
        values = arrays[name]
        if values.shape != (rows_count, dimension) or values.dtype != np.dtype("float32") or not np.isfinite(values).all():
            raise BNCIStagePRefusal(f"Stage P signal feature differs: {name}")
    one_dimensional = {
        "participant_index": "uint8",
        "session_index": "uint8",
        "run_ordinal": "uint8",
        "trial_ordinal": "uint8",
        "trial_start_sample": "int32",
        "opaque_row_id": "S64",
    }
    for name, dtype in one_dimensional.items():
        if arrays[name].shape != (rows_count,) or arrays[name].dtype != np.dtype(dtype):
            raise BNCIStagePRefusal(f"Stage P signal identity array differs: {name}")
    participant_index = PARTICIPANTS.index(str(participant))
    session_index = q_core.SESSIONS.index(str(session))
    if not np.all(arrays["participant_index"] == participant_index) or not np.all(arrays["session_index"] == session_index):
        raise BNCIStagePRefusal("Stage P signal shard internal identity differs")
    rows = []
    for index in range(rows_count):
        row = {
            "participant": participant,
            "session": session,
            "run_ordinal": int(arrays["run_ordinal"][index]),
            "trial_ordinal": int(arrays["trial_ordinal"][index]),
            "trial_start_sample": int(arrays["trial_start_sample"][index]),
            "opaque_row_id": _decode_row_id(arrays["opaque_row_id"][index]),
        }
        row.update({name: arrays[name][index] for name in q_core.FEATURE_DIMENSIONS})
        rows.append(row)
    validate_exact_identity_grid(rows, participant_sessions=[(str(participant), str(session))])
    return rows


def _validate_delivery_manifest(value: Any, participant: str) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema_name") != "neurodecodekit.bnci_2014_001_stage_q_fold_delivery":
        raise BNCIStagePRefusal("Stage P delivery manifest schema differs")
    if value.get("fold") != participant or value.get("held_out_E_rows") != 288 or value.get("held_out_T_rows") != 288:
        raise BNCIStagePRefusal("Stage P delivery manifest fold differs")
    if value.get("held_out_T_rows_delivered") != 0 or value.get("future_delivery") != "exact_listed_bytes_only_no_repository_root_or_scoring_key_path":
        raise BNCIStagePRefusal("Stage P delivery manifest authority differs")
    shards = value.get("signal_shards")
    source = value.get("source_target_capability")
    if not isinstance(shards, list) or len(shards) != 17 or not isinstance(source, dict):
        raise BNCIStagePRefusal("Stage P delivery manifest inventory differs")
    if sum(row.get("delivery_role") == "source_signal" for row in shards if isinstance(row, dict)) != 16:
        raise BNCIStagePRefusal("Stage P source shard inventory differs")
    held = [row for row in shards if isinstance(row, dict) and row.get("delivery_role") == "held_out_E_signal"]
    if len(held) != 1 or held[0].get("participant") != participant or held[0].get("session") != "E":
        raise BNCIStagePRefusal("Stage P held-out signal delivery differs")
    return value


def load_fold_capability(stage_q_output: str | Path, participant: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str], dict[str, Any]]:
    """Load one exact fold without receiving a repository root or scoring-key path."""

    if participant not in PARTICIPANTS:
        raise BNCIStagePRefusal("Stage P participant differs")
    root = Path(stage_q_output).resolve()
    info = root.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise BNCIStagePRefusal("Stage P Stage Q output is not a direct directory")
    delivery_path = root / "fold_capabilities" / f"fold_{participant}.delivery.private.v0.json"
    delivery_payload = _read_direct(delivery_path)
    try:
        delivery = _validate_delivery_manifest(json.loads(delivery_payload), participant)
    except json.JSONDecodeError as exc:
        raise BNCIStagePRefusal("Stage P delivery manifest JSON is invalid") from exc
    source_rows: list[dict[str, Any]] = []
    held_rows: list[dict[str, Any]] = []
    shard_hashes: dict[str, str] = {}
    for record in delivery["signal_shards"]:
        if not isinstance(record, dict) or record.get("role") != "target_free_participant_session_signal_shard":
            raise BNCIStagePRefusal("Stage P signal shard record differs")
        shard_path = _safe_child(root, str(record.get("file")))
        payload = _read_direct(
            shard_path,
            expected_bytes=int(record.get("bytes", -1)),
            expected_sha256=str(record.get("sha256")),
        )
        rows = _rows_from_shard(payload, record)
        shard_hashes[f"{record['participant']}{record['session']}"] = str(record["sha256"])
        if record.get("delivery_role") == "source_signal":
            if record.get("participant") == participant:
                raise BNCIStagePRefusal("Stage P held-out participant reached source signal")
            source_rows.extend(rows)
        elif record.get("delivery_role") == "held_out_E_signal":
            held_rows.extend(rows)
        else:
            raise BNCIStagePRefusal("Stage P signal delivery role differs")
    expected_source_sessions = [
        (source, session)
        for source in PARTICIPANTS
        if source != participant
        for session in q_core.SESSIONS
    ]
    validate_exact_identity_grid(source_rows, participant_sessions=expected_source_sessions)
    validate_exact_identity_grid(held_rows, participant_sessions=[(participant, "E")])
    if len(source_rows) != q_core.SOURCE_ROWS_PER_FOLD or len(held_rows) != q_core.HELD_OUT_E_ROWS_PER_FOLD:
        raise BNCIStagePRefusal("Stage P fold row count differs")
    target_record = delivery["source_target_capability"]
    target_path = _safe_child(root, str(target_record.get("file")))
    target_payload = _read_direct(
        target_path,
        expected_bytes=int(target_record.get("bytes", -1)),
        expected_sha256=str(target_record.get("sha256")),
    )
    target_arrays = _load_npz(target_payload)
    if set(target_arrays) != {"opaque_row_id", "target_index"}:
        raise BNCIStagePRefusal("Stage P source target fields differ")
    if target_arrays["opaque_row_id"].shape != (q_core.SOURCE_ROWS_PER_FOLD,) or target_arrays["target_index"].shape != (q_core.SOURCE_ROWS_PER_FOLD,):
        raise BNCIStagePRefusal("Stage P source target shape differs")
    target_ids = [_decode_row_id(value) for value in target_arrays["opaque_row_id"]]
    target_values = [int(value) for value in target_arrays["target_index"]]
    if len(set(target_ids)) != len(target_ids) or any(value not in range(4) for value in target_values):
        raise BNCIStagePRefusal("Stage P source target capability is malformed")
    source_ids = {str(row["opaque_row_id"]) for row in source_rows}
    held_ids = {str(row["opaque_row_id"]) for row in held_rows}
    if set(target_ids) != source_ids or set(target_ids) & held_ids:
        raise BNCIStagePRefusal("Stage P target capability exceeds its source fold")
    source_targets = {
        row_id: model_core.CLASSES[value]
        for row_id, value in zip(target_ids, target_values, strict=True)
    }
    capability = {
        "delivery_manifest_sha256": _sha256(delivery_payload),
        "source_target_capability_sha256": _sha256(target_payload),
        "signal_shard_count": len(shard_hashes),
        "source_rows": len(source_rows),
        "held_out_E_rows": len(held_rows),
        "held_out_T_rows_delivered": 0,
    }
    return source_rows, held_rows, source_targets, capability


def validate_fold_predictions(participant: str, rows: Sequence[Mapping[str, Any]]) -> None:
    if len(rows) != EXPECTED_PREDICTION_ROWS_PER_FOLD:
        raise BNCIStagePRefusal("Stage P fold prediction count differs")
    identities: dict[tuple[str, str, int, int, str], set[str]] = {}
    coordinates: dict[tuple[str, str, int, int], str] = {}
    previous: tuple[Any, ...] | None = None
    for row in rows:
        if set(row) != scorer.PREDICTION_FIELDS:
            raise BNCIStagePRefusal("Stage P prediction fields differ")
        identity = scorer._identity(row)
        if identity[0] != participant or identity[1] != "E" or not 0 <= identity[3] < 48:
            raise BNCIStagePRefusal("Stage P fold prediction identity differs")
        condition = str(row.get("condition"))
        if condition not in CONDITIONS:
            raise BNCIStagePRefusal("Stage P prediction condition differs")
        scorer._validate_probabilities(row.get("probabilities"))
        key = scorer._prediction_sort_key(row)
        if previous is not None and key < previous:
            raise BNCIStagePRefusal("Stage P fold predictions are not ordered")
        previous = key
        identities.setdefault(identity, set()).add(condition)
        coordinate = identity[:4]
        if coordinate in coordinates and coordinates[coordinate] != identity[4]:
            raise BNCIStagePRefusal("Stage P coordinate has multiple opaque identities")
        coordinates[coordinate] = identity[4]
    if any(value != set(CONDITIONS) for value in identities.values()):
        raise BNCIStagePRefusal("Stage P prediction condition completeness differs")
    expected_coordinates = _expected_grid(participant, "E")
    if set(coordinates) != expected_coordinates or len(identities) != 288:
        raise BNCIStagePRefusal("Stage P fold prediction grid differs")


def _fold_worker(connection: Any, stage_q_output: str, participant: str) -> None:
    try:
        model_core.assert_single_thread_environment()
        model_core.assert_exact_versions()
        source, held, targets, capability = load_fold_capability(stage_q_output, participant)
        result = model_core._run_single_fold(participant, source, held, targets)
        validate_fold_predictions(participant, result["predictions"])
        result["capability"] = capability
        result["peak_process_RSS_bytes"] = model_core.peak_process_tree_rss_bytes()
        connection.send(("ok", result))
    except Exception as exc:  # noqa: BLE001  # pragma: no cover - child boundary
        connection.send(("error", type(exc).__name__, str(exc)))
    finally:
        connection.close()


def run_fold_isolated(stage_q_output: str | Path, participant: str, *, timeout_seconds: float) -> dict[str, Any]:
    if timeout_seconds <= 0.0:
        raise BNCIStagePRefusal("Stage P global deadline expired")
    context = multiprocessing.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(target=_fold_worker, args=(send, str(Path(stage_q_output).resolve()), participant))
    process.start()
    send.close()
    if not receive.poll(timeout_seconds):
        process.terminate()
        process.join(timeout=10.0)
        raise BNCIStagePRefusal(f"Stage P fold exceeded the global deadline: {participant}")
    message = receive.recv()
    receive.close()
    process.join(timeout=30.0)
    if process.is_alive():
        process.terminate()
        process.join(timeout=10.0)
        raise BNCIStagePRefusal(f"Stage P fold did not exit: {participant}")
    if process.exitcode != 0 or not isinstance(message, tuple) or not message:
        raise BNCIStagePRefusal(f"Stage P fold process failed: {participant}")
    if message[0] != "ok":
        raise BNCIStagePRefusal(
            f"Stage P fold refused: {participant}: {' : '.join(str(value) for value in message[1:])}"
        )
    result = message[1]
    if not isinstance(result, dict):
        raise BNCIStagePRefusal("Stage P fold result differs")
    return result


def _target_transport_inventory(stage_q_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    artifacts = stage_q_manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise BNCIStagePRefusal("Stage P Stage Q artifact inventory is absent")
    targets = [
        {"fold": row.get("fold"), "bytes": row.get("bytes"), "sha256": row.get("sha256")}
        for row in artifacts
        if isinstance(row, dict) and row.get("role") == "sealed_scoring_targets"
    ]
    if [row["fold"] for row in targets] != list(PARTICIPANTS) or any(
        not isinstance(row["bytes"], int) or row["bytes"] <= 0 or not _is_sha256(row["sha256"])
        for row in targets
    ):
        raise BNCIStagePRefusal("Stage P sealed target transport inventory differs")
    key_rows = [
        row
        for row in artifacts
        if isinstance(row, dict) and row.get("role") == "scoring_key_vault_sealed_until_T"
    ]
    if len(key_rows) != 1 or not _is_sha256(key_rows[0].get("sha256")):
        raise BNCIStagePRefusal("Stage P scoring-key commitment differs")
    return targets + [{"role": "scoring_key_vault", "bytes": key_rows[0]["bytes"], "sha256": key_rows[0]["sha256"]}]


def source_capability_commitment(stage_q_manifest_payload: bytes, binding_key: bytes) -> str:
    if len(binding_key) != 32:
        raise BNCIStagePRefusal("Stage P private binding-key length differs")
    return hmac.new(binding_key, b"NDK-P-SOURCE-v0\0" + stage_q_manifest_payload, hashlib.sha256).hexdigest()


def _implementation_code_hash(activation: Mapping[str, Any]) -> str:
    return _sha256(_canonical_bytes(activation["implementation_artifacts"]))


def build_public_freeze(
    *,
    activation: Mapping[str, Any],
    remote_proof: Mapping[str, Any],
    stage_q_manifest_payload: bytes,
    target_transport: Sequence[Mapping[str, Any]],
    binding_key: bytes,
    fold_records: Sequence[Mapping[str, Any]],
    prediction_payloads: Sequence[bytes],
    runtime_seconds: float,
    peak_rss_bytes: int,
    private_output_bytes: int,
    free_disk_before: int,
    free_disk_after: int,
) -> dict[str, Any]:
    if len(fold_records) != 9 or len(prediction_payloads) != 9:
        raise BNCIStagePRefusal("Stage P freeze fold inventory differs")
    digest = hashlib.sha256()
    condition_digests = {condition: hashlib.sha256() for condition in CONDITIONS}
    private_bytes = 0
    private_rows = 0
    for payload in prediction_payloads:
        digest.update(payload)
        private_bytes += len(payload)
        rows = scorer._parse_jsonl(payload, kind="Stage P private predictions")
        private_rows += len(rows)
        for row in rows:
            condition_digests[str(row["condition"])].update(scorer._canonical_bytes(row))
    fits = sum(int(row["fit_count"]) for row in fold_records)
    prediction_sets = sum(int(row["prediction_sets"]) for row in fold_records)
    inference_runs = sum(int(row["model_inference_runs"]) for row in fold_records)
    if (
        private_rows != EXPECTED_TOTAL_PREDICTION_ROWS
        or fits != EXPECTED_TOTAL_FITS
        or prediction_sets != EXPECTED_TOTAL_PREDICTION_SETS
        or inference_runs != EXPECTED_TOTAL_PREDICTION_SETS
    ):
        raise BNCIStagePRefusal("Stage P operation inventory differs")
    selected_counts = {family: sum(row["selected_family"] == family for row in fold_records) for family in ("E1", "E2")}
    freeze: dict[str, Any] = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_p_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "frozen_target_blind_predictions_targets_and_scoring_keys_still_sealed",
        "proof_posture": "aggregate_hash_only_no_individual_prediction_probability_target_or_participant_outcome",
        "green_stage_q_result": {
            "commit": STAGE_Q_RESULT_COMMIT,
            "CI_run_id": STAGE_Q_RESULT_CI_RUN_ID,
            "both_required_jobs_green": True,
        },
        "green_stage_p_control_plane": dict(remote_proof),
        "condition_ids": list(CONDITIONS),
        "folds": 9,
        "held_out_participants": 9,
        "held_out_E_rows_per_fold": 288,
        "held_out_T_rows_used": 0,
        "private_prediction_rows": private_rows,
        "private_prediction_bytes": private_bytes,
        "prediction_set_sha256": digest.hexdigest(),
        "condition_sha256": {name: value.hexdigest() for name, value in condition_digests.items()},
        "configuration_hash": q_core.CONTRACT_SHA256,
        "code_hash": _implementation_code_hash(activation),
        "split_protocol_hash": _sha256(_canonical_bytes({"participants": list(PARTICIPANTS), "source_sessions": ["T", "E"], "held_out_session": "E", "held_out_T_used": False, "trials_per_run": 48, "runs_per_session": 6})),
        "source_capability_HMAC_commitment": source_capability_commitment(stage_q_manifest_payload, binding_key),
        "sealed_target_transport_commitment_sha256": _sha256(_canonical_bytes(list(target_transport))),
        "operation_counters": {
            "parameter_update_fits": fits,
            "model_inference_runs": inference_runs,
            "prediction_sets": prediction_sets,
            "target_deliveries": 0,
            "scores": 0,
            "post_target_updates": 0,
            "reruns": 0,
        },
        "aggregate_model_selection": {
            "E1_selected_folds": selected_counts["E1"],
            "E2_selected_folds": selected_counts["E2"],
            "participant_level_selection_public": False,
        },
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_process_tree_RSS_bytes": peak_rss_bytes,
            "private_generated_bytes": private_output_bytes,
            "public_freeze_bytes": 0,
            "free_disk_bytes_before": free_disk_before,
            "free_disk_bytes_after": free_disk_after,
        },
        "registered_caps": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds_maximum": 3600.0,
            "peak_RSS_bytes_maximum": 1_073_741_824,
            "private_generated_bytes_maximum": 536_870_912,
            "public_output_bytes_maximum": 4_194_304,
            "parameter_update_fits_maximum": 540,
            "prediction_sets_maximum": 900,
            "network_bytes": 0,
        },
        "acceptance_gates": {
            "all_nine_folds_complete": True,
            "exact_9_by_6_by_48_held_out_identity_grid": True,
            "zero_held_out_person_calibration": True,
            "zero_held_out_T_signal_or_target_use": True,
            "held_out_E_targets_and_scoring_keys_remained_sealed": True,
            "all_predictions_frozen_before_target_delivery": True,
            "runtime_RSS_output_fit_and_prediction_caps_passed": True,
        },
        "warnings": [
            "this_is_a_target_blind_prediction_freeze_not_a_scientific_score",
            "individual_predictions_probabilities_targets_and_participant_outcomes_remain_private",
            "Stage_T_remains_closed_until_this_exact_freeze_is_committed_pushed_and_remotely_green",
        ],
        "next_gate": "commit_push_and_remotely_green_this_exact_prediction_freeze_before_one_Stage_T_target_delivery_and_score",
        "scientific_claim_established": False,
    }
    for _ in range(8):
        payload = _canonical_bytes(freeze)
        if freeze["measurements"]["public_freeze_bytes"] == len(payload):
            break
        freeze["measurements"]["public_freeze_bytes"] = len(payload)
    else:
        raise BNCIStagePRefusal("Stage P public freeze size did not stabilize")
    if len(payload) > q_core.PUBLIC_OUTPUT_CAP_BYTES:
        raise BNCIStagePRefusal("Stage P public freeze exceeds its cap")
    return freeze


def _collect_prediction_payloads(output: Path, fold_records: Sequence[Mapping[str, Any]]) -> list[bytes]:
    return [
        _read_direct(
            output / str(record["prediction_file"]),
            expected_bytes=int(record["prediction_bytes"]),
            expected_sha256=str(record["prediction_sha256"]),
        )
        for record in fold_records
    ]


def _assert_caps(*, started: float, peak_rss: int, private_bytes: int) -> None:
    if time.monotonic() - started > 3600.0:
        raise BNCIStagePRefusal("Stage P global runtime cap exceeded")
    if peak_rss > 1_073_741_824:
        raise BNCIStagePRefusal("Stage P peak RSS cap exceeded")
    if private_bytes > q_core.PRIVATE_OUTPUT_CAP_BYTES:
        raise BNCIStagePRefusal("Stage P private output cap exceeded")


def _execute_stage_p(
    root: str | Path,
    *,
    activation: Mapping[str, Any],
    remote_proof: Mapping[str, Any],
    environ: Mapping[str, str],
    fold_runner: Callable[..., dict[str, Any]],
    binding_key: bytes,
) -> dict[str, Any]:
    repo = Path(root).resolve()
    if repo != q_core._repo_root():
        raise BNCIStagePRefusal("Stage P repository root differs")
    q_core.assert_single_thread_environment(environ)
    versions = model_core.assert_exact_versions()
    stage_q_result = _read_direct(repo / STAGE_Q_RESULT_RELATIVE_PATH, expected_sha256=STAGE_Q_RESULT_SHA256)
    if json.loads(stage_q_result).get("execution", {}).get("complete_private_derivative_created") is not True:
        raise BNCIStagePRefusal("Stage P green Stage Q result is unavailable")
    output = repo / OUTPUT_RELATIVE_PATH
    marker = repo / MARKER_RELATIVE_PATH
    public_freeze_path = repo / PUBLIC_FREEZE_RELATIVE_PATH
    if any(path.exists() or path.is_symlink() for path in (output, marker, public_freeze_path)):
        raise BNCIStagePRefusal("Stage P is already consumed or has output")
    stage_q_output = repo / q_core.STAGE_Q_OUTPUT_RELATIVE_PATH
    stage_q_marker = repo / q_core.STAGE_Q_MARKER_RELATIVE_PATH
    if not stage_q_output.is_dir() or stage_q_output.is_symlink() or not stage_q_marker.exists():
        raise BNCIStagePRefusal("Stage P Stage Q private capability is unavailable")
    free_before = shutil.disk_usage(repo).free
    if free_before < MINIMUM_FREE_DISK_BYTES + PRIVATE_LAYOUT_BOUND_BYTES:
        raise BNCIStagePRefusal("Stage P free-disk preflight failed")
    temporary = output.with_name(output.name + f".tmp-{os.getpid()}")
    q_live._exclusive_directory(repo, temporary)
    marker_payload = _canonical_bytes({
        "schema_name": "neurodecodekit.bnci_2014_001_stage_p_consumed_marker",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_before_private_capability_or_model_open",
        "implementation_commit": activation["green_implementation"]["commit"],
        "rerun_allowed": False,
    })
    try:
        q_live._exclusive_write(repo, marker, marker_payload)
    except Exception:
        shutil.rmtree(temporary)
        raise
    started = time.monotonic()
    try:
        stage_q_manifest_path = stage_q_output / PRIVATE_MANIFEST_NAME
        stage_q_manifest_payload = _read_direct(stage_q_manifest_path)
        stage_q_manifest = json.loads(stage_q_manifest_payload)
        if (
            stage_q_manifest.get("schema_name") != "neurodecodekit.bnci_2014_001_stage_q_private_derivative_manifest"
            or stage_q_manifest.get("status") != "complete_encrypted_target_firewalled_capabilities"
            or stage_q_manifest.get("rows") != 5184
            or stage_q_manifest.get("folds") != 9
            or stage_q_manifest.get("held_out_T_rows_exposed_per_fold") != 0
        ):
            raise BNCIStagePRefusal("Stage P Stage Q private manifest differs")
        target_transport = _target_transport_inventory(stage_q_manifest)
        q_live._exclusive_write(repo, temporary / PRIVATE_BINDING_KEY_NAME, binding_key)
        fold_records: list[dict[str, Any]] = []
        child_peak = 0
        for participant in PARTICIPANTS:
            elapsed = time.monotonic() - started
            remaining = 3600.0 - elapsed
            result = fold_runner(stage_q_output, participant, timeout_seconds=remaining)
            predictions = result.get("predictions")
            if not isinstance(predictions, list):
                raise BNCIStagePRefusal("Stage P fold predictions are unavailable")
            validate_fold_predictions(participant, predictions)
            payload = b"".join(scorer._canonical_bytes(row) for row in predictions)
            prediction_name = f"fold_{participant}.predictions.private.v0.jsonl"
            q_live._exclusive_write(repo, temporary / prediction_name, payload)
            record = {
                "fold": participant,
                "prediction_file": prediction_name,
                "prediction_rows": len(predictions),
                "prediction_bytes": len(payload),
                "prediction_sha256": _sha256(payload),
                "selected_family": result.get("selected_family"),
                "fit_count": int(result.get("fit_count", -1)),
                "prediction_sets": int(result.get("prediction_sets", -1)),
                "model_inference_runs": int(result.get("model_inference_runs", -1)),
                "model_hashes": dict(result.get("model_hashes", {})),
                "capability": dict(result.get("capability", {})),
            }
            if (
                record["selected_family"] not in {"E1", "E2"}
                or record["fit_count"] != EXPECTED_FITS_PER_FOLD
                or record["prediction_sets"] != EXPECTED_PREDICTION_SETS_PER_FOLD
                or record["model_inference_runs"] != EXPECTED_PREDICTION_SETS_PER_FOLD
                or len(record["model_hashes"]) != 5
                or any(not _is_sha256(value) for value in record["model_hashes"].values())
            ):
                raise BNCIStagePRefusal("Stage P fold operation record differs")
            fold_records.append(record)
            child_peak = max(child_peak, int(result.get("peak_process_RSS_bytes", 0)))
            _assert_caps(
                started=started,
                peak_rss=max(child_peak, model_core.peak_process_tree_rss_bytes()),
                private_bytes=sum(path.stat().st_size for path in temporary.iterdir()),
            )
        prediction_payloads = _collect_prediction_payloads(temporary, fold_records)
        private_manifest = {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_p_private_manifest",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "complete_target_blind_predictions_targets_still_sealed",
            "stage_q_private_manifest_sha256": _sha256(stage_q_manifest_payload),
            "source_capability_HMAC_commitment": source_capability_commitment(stage_q_manifest_payload, binding_key),
            "sealed_target_transport_commitment_sha256": _sha256(_canonical_bytes(target_transport)),
            "folds": fold_records,
            "held_out_T_rows_used": 0,
            "target_deliveries": 0,
            "scores": 0,
        }
        private_manifest_payload = _canonical_bytes(private_manifest)
        q_live._exclusive_write(repo, temporary / PRIVATE_MANIFEST_NAME, private_manifest_payload)
        private_bytes = sum(path.stat().st_size for path in temporary.iterdir())
        peak_rss = max(child_peak, model_core.peak_process_tree_rss_bytes())
        _assert_caps(started=started, peak_rss=peak_rss, private_bytes=private_bytes)
        free_after = shutil.disk_usage(repo).free
        freeze = build_public_freeze(
            activation=activation,
            remote_proof=remote_proof,
            stage_q_manifest_payload=stage_q_manifest_payload,
            target_transport=target_transport,
            binding_key=binding_key,
            fold_records=fold_records,
            prediction_payloads=prediction_payloads,
            runtime_seconds=time.monotonic() - started,
            peak_rss_bytes=peak_rss,
            private_output_bytes=private_bytes,
            free_disk_before=free_before,
            free_disk_after=free_after,
        )
        freeze["software_versions"] = versions
        for _ in range(8):
            freeze_payload = _canonical_bytes(freeze)
            if freeze["measurements"]["public_freeze_bytes"] == len(freeze_payload):
                break
            freeze["measurements"]["public_freeze_bytes"] = len(freeze_payload)
        else:
            raise BNCIStagePRefusal("Stage P final public freeze size did not stabilize")
        if len(freeze_payload) > q_core.PUBLIC_OUTPUT_CAP_BYTES:
            raise BNCIStagePRefusal("Stage P public freeze exceeds cap")
        output_parent = output.parent
        q_live._ensure_direct_directory(repo, output_parent)
        temporary.rename(output)
        q_live._exclusive_write(repo, public_freeze_path, freeze_payload)
        return freeze
    except Exception:
        if temporary.exists() and temporary.is_dir() and not temporary.is_symlink():
            shutil.rmtree(temporary)
        raise


def execute_registered_stage_p(root: str | Path, *, environ: Mapping[str, str]) -> dict[str, Any]:
    """Execute the sole real Stage P run after fresh remote proof."""

    activation = read_green_activation(root)
    remote_proof = q_live.collect_remote_green_proof(root)
    return _execute_stage_p(
        root,
        activation=activation,
        remote_proof=remote_proof,
        environ=environ,
        fold_runner=run_fold_isolated,
        binding_key=secrets.token_bytes(32),
    )


def plan_stage_p() -> dict[str, Any]:
    return {
        "lane_id": LANE_ID,
        "stage_q_result_commit": STAGE_Q_RESULT_COMMIT,
        "folds": 9,
        "fits": EXPECTED_TOTAL_FITS,
        "prediction_sets": EXPECTED_TOTAL_PREDICTION_SETS,
        "private_prediction_rows": EXPECTED_TOTAL_PREDICTION_ROWS,
        "held_out_T_rows_used": 0,
        "target_deliveries": 0,
        "scores": 0,
        "runtime_seconds_maximum": 3600,
        "peak_RSS_bytes_maximum": 1_073_741_824,
        "next_gate": "activation_commit_must_be_pushed_and_remotely_green",
    }
