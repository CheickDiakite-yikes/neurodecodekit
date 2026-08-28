"""Generated-only COMM-P0 two-child full-scale rehearsal wrapper."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import signal
import stat
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_qualification as qualification


GATE_ID = "COMM-P0-G-FS2-v0"
RUN_ID = "COMM-P0-G-FS2-R0"
SCHEMA_VERSION = "0.1.0"
CONTRACT_PATH = Path(
    "registries/communication_eeg_prospective_generated_two_child_"
    "full_scale_rehearsal_contract.v0.json"
)
CONTRACT_SHA256 = "ce533db97ace7b1d8c1423f48227119699f66e454252b78b9acd80b65a8f0a7a"
PROOF_PATH = Path(
    "registries/communication_eeg_prospective_generated_two_child_"
    "rehearsal_implementation_proof.v0.json"
)
PROOF_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_two_child_"
    "rehearsal_implementation_proof"
)
RECEIPT_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_two_child_"
    "rehearsal_receipt"
)
RESULT_SCHEMA = (
    "neurodecodekit.communication_eeg_prospective_generated_two_child_"
    "full_scale_rehearsal_result"
)
IMPLEMENTATION_ARTIFACT_ALLOWLIST = (
    "src/neurodecodekit/experiments/comm_p0_generated_two_child_rehearsal.py",
    "src/neurodecodekit/comm_p0_rehearsal_cli.py",
    "tests/test_comm_p0_generated_two_child_rehearsal.py",
    "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_TWO_CHILD_REHEARSAL_IMPLEMENTATION.md",
    "registries/communication_eeg_prospective_generated_two_child_rehearsal_implementation.v0.json",
)
PROOF_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "gate_id",
        "run_id",
        "contract_sha256",
        "registration_commit",
        "implementation_commit",
        "implementation_CI_run_id",
        "implementation_base_python_job_id",
        "implementation_optional_neuro_readers_job_id",
        "registration_remotely_green_on_GitHub_main",
        "implementation_remotely_green_on_GitHub_main",
        "both_required_implementation_jobs_green",
        "rehearsal_execution_authorized_under_Tier_B",
        "official_qualification_activated",
        "official_marker_operations_authorized",
        "real_private_network_device_or_release_authorized",
        "full_scale_rehearsal_attempts_before_proof",
        "implementation_artifacts",
        "implementation_artifact_set_sha256",
        "proof_sha256",
    }
)
HEX_40 = frozenset("0123456789abcdef")
RESERVATION_CHUNK_BYTES = 8 * 1024 * 1024
PUBLIC_FAILURE_FAMILIES = frozenset(
    {
        "FS2-parent_hash_or_green_proof_drift",
        "FS2-duplicate_or_missing_rehearsal_receipt",
        "FS2-official_capability_or_marker_access",
        "FS2-wrong_cohort_or_replay_cardinality",
        "FS2-concurrent_or_same_PID_children",
        "FS2-canonical_replay_mismatch",
        "FS2-schedule_or_counter_drift",
        "FS2-resource_or_monitor_failure",
        "FS2-forbidden_operation_nonzero",
        "FS2-publication_collision_partial_write_or_cleanup_escape",
        "FS2-claim_boundary_violation",
    }
)
RECEIPT_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "gate_id",
        "run_id",
        "attempt_status",
        "contract_sha256",
        "implementation_proof_sha256",
        "started_at_unix_ns",
        "failure_timeout_or_refusal_consumes_attempt",
        "official_marker_schema",
    }
)
RESULT_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "gate_id",
        "run_id",
        "route",
        "mode",
        "official_qualification",
        "attempt_consumed",
        "contract_sha256",
        "implementation_proof_sha256",
        "rehearsal_receipt_sha256",
        "completed_replay_children",
        "expected_replay_children",
        "distinct_replay_worker_PIDs",
        "canonical_replay_equivalent",
        "canonical_replay_sha256",
        "registered_totals",
        "observed_generated_counters",
        "runtime_seconds",
        "peak_process_tree_RSS_bytes",
        "mandatory_process_monitor_samples",
        "observed_free_disk_bytes_before_reservation",
        "observed_free_disk_bytes_after_reservation",
        "failure_family",
        "post_target_updates",
        "official_activation_reads",
        "official_marker_operations",
        "real_or_private_path_operations",
        "real_signal_reads",
        "real_target_or_label_reads",
        "real_data_training_or_inference_runs",
        "human_operations",
        "device_stream_microphone_operations",
        "provider_or_network_operations",
        "network_bytes",
        "release_operations",
        "end_to_end_device_latency_measured",
        "retained_generated_payload_bytes",
        "scientific_claim_established",
        "warnings",
    }
)
SOCKET_GUARD = """\
import os
import socket

def _blocked(*args, **kwargs):
    raise RuntimeError("COMM-P0-G:FS2-forbidden_operation_nonzero:network")

class _BlockedSocket(socket.socket):
    def connect(self, *args, **kwargs):
        return _blocked(*args, **kwargs)
    def connect_ex(self, *args, **kwargs):
        return _blocked(*args, **kwargs)

socket.socket = _BlockedSocket
socket.create_connection = _blocked
socket.getaddrinfo = _blocked

from neurodecodekit.experiments import comm_p0_generated_qualification as _qualification
_original_environment = _qualification._sanitized_child_environment

def _guarded_environment(temp_root, repository):
    value = _original_environment(temp_root, repository)
    guard = os.environ["NDK_FS2_GUARD_DIR"]
    value["NDK_FS2_GUARD_DIR"] = guard
    value["PYTHONPATH"] = guard + os.pathsep + value["PYTHONPATH"]
    return value

_qualification._sanitized_child_environment = _guarded_environment
"""


def _refuse(family: str, detail: str = "") -> None:
    raise core.CommP0GeneratedRefusal(f"FS2-{family}", detail)


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else core._repo_root()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_commit(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and set(value) <= HEX_40


def _read_json_no_follow(path: Path, *, byte_cap: int) -> tuple[dict[str, Any], str]:
    identity, payload = qualification.read_no_follow(path, byte_cap=byte_cap)
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-parent_hash_or_green_proof_drift"
        ) from exc
    if not isinstance(value, Mapping):
        _refuse("parent_hash_or_green_proof_drift")
    return dict(value), identity.sha256


def load_contract(root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green FS2 contract and verify its parents."""

    repository = _repo_root(root)
    contract, observed_sha = _read_json_no_follow(
        repository / CONTRACT_PATH, byte_cap=1_048_576
    )
    if (
        observed_sha != CONTRACT_SHA256
        or contract.get("gate_id") != GATE_ID
        or contract.get("run_id") != RUN_ID
        or contract.get("schema_version") != SCHEMA_VERSION
    ):
        _refuse("parent_hash_or_green_proof_drift")
    parents = contract.get("bound_parents")
    if not isinstance(parents, list) or len(parents) != 4:
        _refuse("parent_hash_or_green_proof_drift")
    for row in parents:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"}:
            _refuse("parent_hash_or_green_proof_drift")
        source = repository / str(row["path"])
        identity, _ = qualification.read_no_follow(source, byte_cap=8 * 1024 * 1024)
        if identity.size_bytes != row["bytes"] or identity.sha256 != row["sha256"]:
            _refuse("parent_hash_or_green_proof_drift")
    return contract


def validate_implementation_proof(
    proof: Mapping[str, Any], *, root: str | Path | None = None
) -> dict[str, Any]:
    """Validate a future remotely green proof without Git or network access."""

    repository = _repo_root(root)
    if set(proof) != PROOF_KEYS:
        _refuse("parent_hash_or_green_proof_drift")
    required_true = (
        "registration_remotely_green_on_GitHub_main",
        "implementation_remotely_green_on_GitHub_main",
        "both_required_implementation_jobs_green",
        "rehearsal_execution_authorized_under_Tier_B",
    )
    required_false = (
        "official_qualification_activated",
        "official_marker_operations_authorized",
        "real_private_network_device_or_release_authorized",
    )
    if (
        proof.get("schema_name") != PROOF_SCHEMA
        or proof.get("schema_version") != SCHEMA_VERSION
        or proof.get("gate_id") != GATE_ID
        or proof.get("run_id") != RUN_ID
        or proof.get("contract_sha256") != CONTRACT_SHA256
        or proof.get("full_scale_rehearsal_attempts_before_proof") != 0
        or any(proof.get(key) is not True for key in required_true)
        or any(proof.get(key) is not False for key in required_false)
        or not _is_commit(proof.get("registration_commit"))
        or not _is_commit(proof.get("implementation_commit"))
        or any(
            not isinstance(proof.get(key), int) or proof[key] <= 0
            for key in (
                "implementation_CI_run_id",
                "implementation_base_python_job_id",
                "implementation_optional_neuro_readers_job_id",
            )
        )
    ):
        _refuse("parent_hash_or_green_proof_drift")
    rows = proof.get("implementation_artifacts")
    if not isinstance(rows, list) or [row.get("path") for row in rows] != list(
        IMPLEMENTATION_ARTIFACT_ALLOWLIST
    ):
        _refuse("parent_hash_or_green_proof_drift")
    for row in rows:
        if set(row) != {"path", "bytes", "sha256"}:
            _refuse("parent_hash_or_green_proof_drift")
        identity, _ = qualification.read_no_follow(
            repository / row["path"], byte_cap=8 * 1024 * 1024
        )
        if identity.size_bytes != row["bytes"] or identity.sha256 != row["sha256"]:
            _refuse("parent_hash_or_green_proof_drift")
    if proof.get("implementation_artifact_set_sha256") != core.sha256_json(rows):
        _refuse("parent_hash_or_green_proof_drift")
    canonical = dict(proof)
    supplied = canonical.pop("proof_sha256")
    if supplied != core.sha256_json(canonical):
        _refuse("parent_hash_or_green_proof_drift")
    return dict(proof)


def load_implementation_proof(root: str | Path | None = None) -> dict[str, Any]:
    repository = _repo_root(root)
    path = repository / PROOF_PATH
    if not path.exists():
        _refuse("parent_hash_or_green_proof_drift", "implementation_proof_absent")
    proof, _ = _read_json_no_follow(path, byte_cap=1_048_576)
    return validate_implementation_proof(proof, root=repository)


def plan(root: str | Path | None = None) -> dict[str, Any]:
    contract = load_contract(root)
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_fs2_plan",
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "run_id": RUN_ID,
        "mode": "generated_only_nonofficial_two_child_resource_rehearsal",
        "implementation_proof_present": (_repo_root(root) / PROOF_PATH).is_file(),
        "registration_authorizes_execution_now": False,
        "registered_attempts_maximum": 1,
        "schedule_per_replay": contract["schedule_per_replay"],
        "two_replay_totals": contract["two_replay_totals"],
        "resource_caps": contract["resource_caps"],
        "official_qualification_activated": False,
        "real_or_private_operations_authorized": False,
        "scientific_claim_established": False,
        "warnings": [
            "fictional generated records only",
            "the official qualification is separate and remains inactive",
            "generated runtime is not end-to-end device latency",
            "not scientific evidence",
        ],
    }


def _normalize_destinations(
    output: Path, receipt: Path, *, repository: Path
) -> tuple[Path, Path, Path]:
    output = qualification._absolute_without_resolution(output)
    receipt = qualification._absolute_without_resolution(receipt)
    if output == receipt or output.parent != receipt.parent:
        _refuse("publication_collision_partial_write_or_cleanup_escape")
    activation_path = qualification._absolute_without_resolution(
        repository / core.ACTIVATION_PATH
    )
    if output == activation_path or receipt == activation_path:
        _refuse("official_capability_or_marker_access")
    try:
        directory_fd = qualification._open_directory_no_follow(output.parent)
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-publication_collision_partial_write_or_cleanup_escape"
        ) from exc
    else:
        os.close(directory_fd)
    if os.path.lexists(output) or os.path.lexists(receipt):
        _refuse("duplicate_or_missing_rehearsal_receipt")
    return output, receipt, output.parent


def _create_receipt(
    path: Path, *, proof_sha256: str, started_at_unix_ns: int
) -> qualification.FileIdentity:
    record = {
        "schema_name": RECEIPT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "run_id": RUN_ID,
        "attempt_status": "consumed_before_child_1",
        "contract_sha256": CONTRACT_SHA256,
        "implementation_proof_sha256": proof_sha256,
        "started_at_unix_ns": started_at_unix_ns,
        "failure_timeout_or_refusal_consumes_attempt": True,
        "official_marker_schema": False,
    }
    if set(record) != RECEIPT_KEYS:
        _refuse("claim_boundary_violation")
    core.assert_target_free(record)
    return qualification.create_no_replace_file(
        path, core.canonical_json_bytes(record), byte_cap=4096
    )


def _create_disk_reservation(path: Path, size_bytes: int) -> None:
    """Allocate a bounded non-sparse file and fsync it before child work."""

    directory_fd = qualification._open_directory_no_follow(path.parent)
    descriptor = -1
    try:
        descriptor = os.open(
            path.name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        remaining = size_bytes
        block = secrets.token_bytes(min(RESERVATION_CHUNK_BYTES, size_bytes))
        while remaining:
            payload = block[: min(len(block), remaining)]
            qualification._write_all(descriptor, payload)
            remaining -= len(payload)
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_size != size_bytes
        ):
            _refuse("resource_or_monitor_failure", "disk_reservation_invalid")
        os.close(descriptor)
        descriptor = -1
        os.fsync(directory_fd)
    except FileExistsError as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-publication_collision_partial_write_or_cleanup_escape"
        ) from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(directory_fd)


def _resize_disk_reservation(path: Path, size_bytes: int) -> None:
    directory_fd = qualification._open_directory_no_follow(path.parent)
    descriptor = -1
    try:
        descriptor = os.open(
            path.name,
            os.O_RDWR | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            _refuse("publication_collision_partial_write_or_cleanup_escape")
        os.ftruncate(descriptor, size_bytes)
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        if after.st_size != size_bytes or after.st_nlink != 1:
            _refuse("resource_or_monitor_failure", "disk_reservation_resize")
        os.close(descriptor)
        descriptor = -1
        os.fsync(directory_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(directory_fd)


def _create_owned_directory(parent: Path, name: str) -> Path:
    directory_fd = qualification._open_directory_no_follow(parent)
    try:
        os.mkdir(name, mode=0o700, dir_fd=directory_fd)
        os.fsync(directory_fd)
    except FileExistsError as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-publication_collision_partial_write_or_cleanup_escape"
        ) from exc
    finally:
        os.close(directory_fd)
    return parent / name


def _clear_directory_fd(directory_fd: int) -> None:
    for entry in list(os.scandir(directory_fd)):
        info = os.stat(entry.name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            child_fd = os.open(
                entry.name,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory_fd,
            )
            try:
                _clear_directory_fd(child_fd)
            finally:
                os.close(child_fd)
            os.rmdir(entry.name, dir_fd=directory_fd)
        elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
            os.unlink(entry.name, dir_fd=directory_fd)
        else:
            _refuse("publication_collision_partial_write_or_cleanup_escape")
    os.fsync(directory_fd)


def _remove_owned_tree(path: Path) -> None:
    parent_fd = qualification._open_directory_no_follow(path.parent)
    directory_fd = -1
    try:
        directory_fd = os.open(
            path.name,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        _clear_directory_fd(directory_fd)
        os.close(directory_fd)
        directory_fd = -1
        os.rmdir(path.name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        if directory_fd >= 0:
            os.close(directory_fd)
        os.close(parent_fd)


def _write_socket_guard(replay_root: Path) -> Path:
    guard_root = _create_owned_directory(replay_root, "network-guard")
    qualification.create_no_replace_file(
        guard_root / "sitecustomize.py",
        SOCKET_GUARD.encode("ascii"),
        byte_cap=16_384,
    )
    return guard_root


def _process_rows() -> dict[int, tuple[int, int, int]]:
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,rss=,pgid="],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-resource_or_monitor_failure", "process_monitor_failed"
        ) from exc
    rows: dict[int, tuple[int, int, int]] = {}
    try:
        for line in completed.stdout.splitlines():
            pid, parent, rss_kib, process_group = (int(value) for value in line.split())
            rows[pid] = (parent, rss_kib * 1024, process_group)
    except (TypeError, ValueError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-resource_or_monitor_failure", "process_monitor_malformed"
        ) from exc
    return rows


def _descendants(rows: Mapping[int, tuple[int, int, int]], root_pid: int) -> set[int]:
    found = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, (parent, _, _) in rows.items():
            if parent in found and pid not in found:
                found.add(pid)
                changed = True
    return found


def _terminate_captured_processes(
    process: subprocess.Popen[bytes], captured_pids: set[int], captured_groups: set[int]
) -> None:
    own_group = os.getpgrp()
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for group in sorted(captured_groups, reverse=True):
            if group <= 0 or group == own_group:
                continue
            try:
                os.killpg(group, sig)
            except ProcessLookupError:
                pass
        for pid in sorted(captured_pids, reverse=True):
            if pid == os.getpid():
                continue
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            continue
        break
    rows = _process_rows()
    survivors = {pid for pid in captured_pids if pid in rows}
    if survivors:
        _refuse("resource_or_monitor_failure", "descendant_termination_failed")


def _run_monitored_tree_command(
    command: Sequence[str],
    *,
    pass_fds: Sequence[int],
    environment: Mapping[str, str],
    cwd: Path,
    deadline_monotonic: float,
    rss_cap_bytes: int,
) -> qualification.ProcessMeasurement:
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            tuple(command),
            cwd=cwd,
            env=dict(environment),
            pass_fds=tuple(pass_fds),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-publication_collision_partial_write_or_cleanup_escape",
            "child_start_failed",
        ) from exc
    captured_pids = {process.pid}
    captured_groups = {process.pid}
    peak = 0
    samples = 0
    try:
        while process.poll() is None:
            rows = _process_rows()
            current = _descendants(rows, process.pid)
            captured_pids.update(current)
            captured_groups.update(
                rows[pid][2] for pid in current if pid in rows and rows[pid][2] > 0
            )
            whole_tree = _descendants(rows, os.getpid())
            peak = max(peak, sum(rows[pid][1] for pid in whole_tree if pid in rows))
            samples += 1
            if time.monotonic() >= deadline_monotonic:
                _terminate_captured_processes(process, captured_pids, captured_groups)
                _refuse("resource_or_monitor_failure", "absolute_deadline")
            if peak > rss_cap_bytes:
                _terminate_captured_processes(process, captured_pids, captured_groups)
                _refuse("resource_or_monitor_failure", "RSS")
            time.sleep(0.1)
        rows = _process_rows()
        alive = {pid for pid in captured_pids if pid != process.pid and pid in rows}
        if alive:
            _terminate_captured_processes(process, captured_pids, captured_groups)
            _refuse("resource_or_monitor_failure", "orphan_descendant")
        if process.returncode != 0:
            _refuse("resource_or_monitor_failure", "child_failure")
        if samples == 0:
            _refuse("resource_or_monitor_failure", "zero_monitor_samples")
    finally:
        if process.poll() is None:
            _terminate_captured_processes(process, captured_pids, captured_groups)
    return qualification.ProcessMeasurement(
        runtime_seconds=time.monotonic() - started,
        peak_process_tree_RSS_bytes=peak,
        monitor_samples=samples,
    )


def _execute_replay_child_fs2(
    *,
    repository: Path,
    replay_root: Path,
    participants_per_cohort: int,
    absolute_deadline: float,
    vault_key: bytes,
    opaque_key: bytes,
    freeze_key: bytes,
    invocation_nonce: str,
    rss_cap_bytes: int,
) -> dict[str, Any]:
    guard_root = _write_socket_guard(replay_root)
    control_path = replay_root / "replay-control.json"
    output_path = replay_root / "replay-result.json"
    control = {
        "repository": str(repository),
        "temporary_root": str(replay_root),
        "participants_per_cohort": participants_per_cohort,
        "absolute_deadline": absolute_deadline,
        "vault_key_hex": vault_key.hex(),
        "opaque_key_hex": opaque_key.hex(),
        "freeze_key_hex": freeze_key.hex(),
        "invocation_nonce": invocation_nonce,
    }
    qualification.create_no_replace_file(
        control_path, core.canonical_json_bytes(control), byte_cap=16_384
    )
    qualification.create_no_replace_file(output_path, b"", byte_cap=1)
    control_fd = os.open(control_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    output_fd = os.open(output_path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))
    environment = qualification._sanitized_child_environment(replay_root, repository)
    environment["NDK_FS2_GUARD_DIR"] = str(guard_root)
    environment["PYTHONPATH"] = str(guard_root) + os.pathsep + environment["PYTHONPATH"]
    try:
        measurement = _run_monitored_tree_command(
            (
                sys.executable,
                "-m",
                "neurodecodekit.experiments.comm_p0_generated_replay_worker",
                "--control-fd",
                str(control_fd),
                "--output-fd",
                str(output_fd),
            ),
            pass_fds=(control_fd, output_fd),
            environment=environment,
            cwd=repository,
            deadline_monotonic=absolute_deadline,
            rss_cap_bytes=rss_cap_bytes,
        )
    finally:
        os.close(control_fd)
        os.close(output_fd)
    _, payload = qualification.read_no_follow(output_path, byte_cap=1_048_576)
    try:
        result = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-schedule_or_counter_drift", "child_output"
        ) from exc
    if not isinstance(result, Mapping):
        _refuse("schedule_or_counter_drift")
    core.assert_target_free(result)
    value = dict(result)
    value["outer_process_tree_RSS_bytes"] = measurement.peak_process_tree_RSS_bytes
    value["outer_monitor_samples"] = measurement.monitor_samples
    return value


def _validate_replay(
    replay: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, Any]:
    core.assert_target_free(replay)
    expected = contract["schedule_per_replay"]
    inventory = replay.get("prediction_inventory")
    shortcut = replay.get("shortcut_counters")
    ledger = replay.get("ledger")
    if not all(isinstance(value, Mapping) for value in (inventory, shortcut, ledger)):
        _refuse("schedule_or_counter_drift")
    model_keys = (
        "prior_fits",
        "residualizer_fits",
        "classifier_fits",
        "temperature_calibration_fits",
        "model_inference_runs",
        "prediction_sets",
        "prediction_rows",
        "post_target_updates",
    )
    if any(ledger.get(key) != expected[key] for key in model_keys):
        _refuse("schedule_or_counter_drift")
    if (
        inventory.get("rows") != expected["prediction_rows"]
        or inventory.get("sets") != expected["prediction_sets"]
        or replay.get("shortcut_fixture_executions")
        != expected["numerical_shortcut_fixture_executions"]
        or replay.get("refusal_observations") != expected["refusal_observations"]
        or replay.get("target_deliveries") != expected["cohort_target_deliveries"]
        or replay.get("scores") != expected["cohort_scores"]
        or shortcut.get("target_deliveries") != expected["shortcut_target_deliveries"]
        or shortcut.get("scores") != expected["shortcut_scores"]
        or shortcut.get("prediction_rows") != expected["prediction_rows"]
        or replay.get("post_target_updates") != 0
        or replay.get("maximum_prediction_rows_buffered", 257)
        > expected["maximum_prediction_rows_buffered"]
        or replay.get("complete_prediction_records_materialized") is not False
    ):
        _refuse("schedule_or_counter_drift")
    caps = contract["resource_caps"]
    peak_rss = max(
        int(replay.get("peak_process_tree_RSS_bytes", 0)),
        int(replay.get("outer_process_tree_RSS_bytes", 0)),
    )
    monitor_samples = int(replay.get("monitor_samples", 0)) + int(
        replay.get("outer_monitor_samples", 0)
    )
    if (
        peak_rss <= 0
        or peak_rss > caps["peak_process_tree_RSS_bytes"]
        or monitor_samples <= 0
        or replay.get("generated_input_bytes_written", caps["generated_input_bytes_maximum_per_replay"] + 1)
        > caps["generated_input_bytes_maximum_per_replay"]
        or replay.get("private_output_bytes_written", caps["private_generated_output_bytes_maximum_per_replay"] + 1)
        > caps["private_generated_output_bytes_maximum_per_replay"]
        or replay.get("temporary_disk_peak_bytes", caps["temporary_disk_peak_bytes"] + 1)
        > caps["temporary_disk_peak_bytes"]
    ):
        _refuse("resource_or_monitor_failure")
    if not isinstance(replay.get("isolated_replay_worker_pid"), int):
        _refuse("concurrent_or_same_PID_children")
    if not isinstance(replay.get("canonical_surface"), Mapping) or not isinstance(
        replay.get("canonical_replay_sha256"), str
    ):
        _refuse("canonical_replay_mismatch")
    return dict(replay)


def _aggregate_result(
    *,
    route: str,
    contract: Mapping[str, Any],
    proof_sha256: str,
    receipt_sha256: str,
    runtime_seconds: float,
    observed_free_before: int,
    observed_free_after_reservation: int | None,
    peak_rss_bytes: int,
    monitor_samples: int,
    replay_sha256: str | None,
    failure_family: str | None,
    completed_replays: int,
    retained_generated_payload_bytes: int | None,
) -> dict[str, Any]:
    totals = contract["two_replay_totals"]
    if failure_family is not None and failure_family not in PUBLIC_FAILURE_FAMILIES:
        _refuse("claim_boundary_violation", "unregistered_failure_family")
    observed_generated_counters = None
    if route == "FS2_PASS":
        observed_generated_counters = {
            "cohort_target_deliveries": totals["cohort_target_deliveries"],
            "cohort_scores": totals["cohort_scores"],
            "shortcut_target_deliveries": totals["shortcut_target_deliveries"],
            "shortcut_scores": totals["shortcut_scores"],
            "model_inference_runs": totals["model_inference_runs"],
            "prediction_sets": totals["prediction_sets"],
            "prediction_rows": totals["prediction_rows"],
            "post_target_updates": 0,
        }
    result = {
        "schema_name": RESULT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "run_id": RUN_ID,
        "route": route,
        "mode": "generated_only_nonofficial_two_child_resource_rehearsal",
        "official_qualification": False,
        "attempt_consumed": True,
        "contract_sha256": CONTRACT_SHA256,
        "implementation_proof_sha256": proof_sha256,
        "rehearsal_receipt_sha256": receipt_sha256,
        "completed_replay_children": completed_replays,
        "expected_replay_children": 2,
        "distinct_replay_worker_PIDs": True if route == "FS2_PASS" else None,
        "canonical_replay_equivalent": True if route == "FS2_PASS" else None,
        "canonical_replay_sha256": replay_sha256,
        "registered_totals": totals,
        "observed_generated_counters": observed_generated_counters,
        "runtime_seconds": runtime_seconds,
        "peak_process_tree_RSS_bytes": peak_rss_bytes or None,
        "mandatory_process_monitor_samples": monitor_samples or None,
        "observed_free_disk_bytes_before_reservation": observed_free_before,
        "observed_free_disk_bytes_after_reservation": observed_free_after_reservation,
        "failure_family": failure_family,
        "post_target_updates": 0,
        "official_activation_reads": 0,
        "official_marker_operations": 0,
        "real_or_private_path_operations": 0,
        "real_signal_reads": 0,
        "real_target_or_label_reads": 0,
        "real_data_training_or_inference_runs": 0,
        "human_operations": 0,
        "device_stream_microphone_operations": 0,
        "provider_or_network_operations": 0,
        "network_bytes": 0,
        "release_operations": 0,
        "end_to_end_device_latency_measured": False,
        "retained_generated_payload_bytes": retained_generated_payload_bytes,
        "scientific_claim_established": False,
        "warnings": [
            "fictional generated records only",
            "this is not the official generated qualification",
            "generated runtime is not end-to-end device latency",
            "not scientific evidence",
        ],
    }
    if set(result) != RESULT_KEYS:
        _refuse("claim_boundary_violation", "public_result_schema")
    core.assert_target_free(result)
    return result


def _public_failure_family(exc: BaseException) -> str:
    if isinstance(exc, core.CommP0GeneratedRefusal):
        family = exc.family
        if family in PUBLIC_FAILURE_FAMILIES:
            return family
        lowered = str(exc).lower()
        if any(token in lowered for token in ("deadline", "rss", "monitor", "space")):
            return "FS2-resource_or_monitor_failure"
        if any(token in lowered for token in ("filesystem", "publication", "replace")):
            return "FS2-publication_collision_partial_write_or_cleanup_escape"
        if any(token in lowered for token in ("target", "network", "provider", "device")):
            return "FS2-forbidden_operation_nonzero"
        if any(token in lowered for token in ("replay", "nondeterministic")):
            return "FS2-canonical_replay_mismatch"
    return "FS2-resource_or_monitor_failure"


def _free_disk_bytes(path: Path) -> int:
    info = os.statvfs(path)
    return int(info.f_bavail * info.f_frsize)


def _run_with_dependencies(
    output: Path,
    receipt: Path,
    *,
    root: str | Path | None,
    proof: Mapping[str, Any],
    execute_replay: Callable[..., dict[str, Any]],
    free_disk_bytes: Callable[[Path], int],
    reserve_disk: Callable[[Path, int], None],
    resize_reservation: Callable[[Path, int], None],
    monotonic: Callable[[], float],
    time_ns: Callable[[], int],
) -> dict[str, Any]:
    repository = _repo_root(root)
    contract = load_contract(repository)
    validated_proof = validate_implementation_proof(proof, root=repository)
    proof_sha256 = str(validated_proof["proof_sha256"])
    output, receipt, destination_root = _normalize_destinations(
        output, receipt, repository=repository
    )
    caps = contract["resource_caps"]
    observed_before = free_disk_bytes(destination_root)
    if observed_before < caps["free_bytes_required_before_reservation"]:
        _refuse("resource_or_monitor_failure", "free_space_preflight")
    started = monotonic()
    absolute_deadline = started + float(caps["wall_time_seconds"])
    receipt_identity = _create_receipt(
        receipt,
        proof_sha256=proof_sha256,
        started_at_unix_ns=time_ns(),
    )
    replays: list[dict[str, Any]] = []
    observed_after_reservation: int | None = None
    failure_family: str | None = None
    peak_rss = 0
    monitor_samples = 0
    replay_sha256: str | None = None
    retained_generated_payload_bytes: int | None = None
    temporary_root: Path | None = None
    try:
        temporary_root = _create_owned_directory(
            destination_root, f".comm-p0-g-fs2-{secrets.token_hex(16)}"
        )
        reservation_path = temporary_root / "disk-reservation.bin"
        reserve_disk(reservation_path, int(caps["aggregate_incremental_disk_bytes"]))
        observed_after_reservation = free_disk_bytes(destination_root)
        if observed_after_reservation < caps["free_bytes_required_after_reservation"]:
            _refuse("resource_or_monitor_failure", "free_space_after_reservation")
        if qualification._temporary_tree_bytes(temporary_root) > caps[
            "aggregate_incremental_disk_bytes"
        ]:
            _refuse("resource_or_monitor_failure", "reservation_cap")
        resize_reservation(
            reservation_path,
            int(
                caps["aggregate_incremental_disk_bytes"]
                - caps["temporary_disk_peak_bytes"]
            ),
        )
        vault_key = secrets.token_bytes(32)
        opaque_key = secrets.token_bytes(32)
        freeze_key = secrets.token_bytes(32)
        invocation_nonce = secrets.token_hex(32)
        for index in range(2):
            if monotonic() >= absolute_deadline:
                _refuse("resource_or_monitor_failure", "absolute_deadline")
            replay_root = _create_owned_directory(temporary_root, f"replay-{index + 1}")
            replay = execute_replay(
                repository=repository,
                replay_root=replay_root,
                participants_per_cohort=21,
                absolute_deadline=absolute_deadline,
                vault_key=vault_key,
                opaque_key=opaque_key,
                freeze_key=freeze_key,
                invocation_nonce=invocation_nonce,
                rss_cap_bytes=int(caps["peak_process_tree_RSS_bytes"]),
            )
            replay = _validate_replay(replay, contract)
            replays.append(replay)
            peak_rss = max(
                peak_rss,
                int(replay["peak_process_tree_RSS_bytes"]),
                int(replay.get("outer_process_tree_RSS_bytes", 0)),
            )
            monitor_samples += int(replay["monitor_samples"]) + int(
                replay.get("outer_monitor_samples", 0)
            )
            if qualification._temporary_tree_bytes(temporary_root) > caps[
                "aggregate_incremental_disk_bytes"
            ]:
                _refuse("resource_or_monitor_failure", "aggregate_disk_cap")
            _remove_owned_tree(replay_root)
            if index == 0:
                resize_reservation(
                    reservation_path, int(caps["public_target_free_result_bytes"])
                )
        first, second = replays
        if first["isolated_replay_worker_pid"] == second["isolated_replay_worker_pid"]:
            _refuse("concurrent_or_same_PID_children")
        if (
            first["canonical_surface"] != second["canonical_surface"]
            or first["canonical_replay_sha256"] != second["canonical_replay_sha256"]
        ):
            _refuse("canonical_replay_mismatch")
        replay_sha256 = first["canonical_replay_sha256"]
        resize_reservation(reservation_path, 0)
        qualification._unlink_invocation_file(
            reservation_path, invocation_root=temporary_root
        )
    except Exception as exc:
        failure_family = _public_failure_family(exc)
    finally:
        if temporary_root is not None:
            try:
                _remove_owned_tree(temporary_root)
            except Exception:
                failure_family = (
                    "FS2-publication_collision_partial_write_or_cleanup_escape"
                )
                retained_generated_payload_bytes = None
            else:
                retained_generated_payload_bytes = 0
    runtime = monotonic() - started
    if runtime > float(caps["wall_time_seconds"]):
        failure_family = "FS2-resource_or_monitor_failure"
    route = (
        "FS2_PASS"
        if failure_family is None
        and len(replays) == 2
        and retained_generated_payload_bytes == 0
        else "FS2_PARK"
    )
    result = _aggregate_result(
        route=route,
        contract=contract,
        proof_sha256=proof_sha256,
        receipt_sha256=receipt_identity.sha256,
        runtime_seconds=runtime,
        observed_free_before=observed_before,
        observed_free_after_reservation=observed_after_reservation,
        peak_rss_bytes=peak_rss,
        monitor_samples=monitor_samples,
        replay_sha256=replay_sha256 if route == "FS2_PASS" else None,
        failure_family=failure_family,
        completed_replays=len(replays),
        retained_generated_payload_bytes=retained_generated_payload_bytes,
    )
    payload = core.canonical_json_bytes(result)
    if len(payload) > caps["public_target_free_result_bytes"]:
        _refuse("publication_collision_partial_write_or_cleanup_escape", "output_cap")
    qualification.publish_atomic_no_replace(
        output, payload, byte_cap=int(caps["public_target_free_result_bytes"])
    )
    return result


def run_registered_rehearsal(
    output: str | Path,
    *,
    receipt: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Run the sole FS2 attempt only after its fixed implementation proof exists."""

    proof = load_implementation_proof(root)
    return _run_with_dependencies(
        Path(output),
        Path(receipt),
        root=root,
        proof=proof,
        execute_replay=_execute_replay_child_fs2,
        free_disk_bytes=_free_disk_bytes,
        reserve_disk=_create_disk_reservation,
        resize_reservation=_resize_disk_reservation,
        monotonic=time.monotonic,
        time_ns=time.time_ns,
    )


def inspect_result(path: str | Path) -> dict[str, Any]:
    _, payload = qualification.read_no_follow(path, byte_cap=1_048_576)
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "FS2-publication_collision_partial_write_or_cleanup_escape"
        ) from exc
    if (
        not isinstance(value, Mapping)
        or value.get("schema_name") != RESULT_SCHEMA
        or set(value) != RESULT_KEYS
        or value.get("route") not in {"FS2_PASS", "FS2_PARK"}
        or (
            value.get("failure_family") is not None
            and value.get("failure_family") not in PUBLIC_FAILURE_FAMILIES
        )
    ):
        _refuse("publication_collision_partial_write_or_cleanup_escape")
    core.assert_target_free(value)
    return dict(value)
