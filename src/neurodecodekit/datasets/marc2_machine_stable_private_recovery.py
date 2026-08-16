"""Proof-gated machine-stable structural cohort recovery for MARC2-VR4P."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import resource
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as adapter
from neurodecodekit.datasets import marc2_machine_readiness as readiness
from neurodecodekit.datasets import marc2_proof_record_recovery as proof_recovery


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR4P"
MODULE_NAME = (
    "neurodecodekit.datasets.marc2_machine_stable_private_recovery"
)
SUCCESS_ROUTE = "MARC2MSP-R1"
REFUSAL_ROUTES = tuple(f"MARC2MSP-F{index:02d}" for index in range(10))

DECISION_COMMIT = "eac37262dcf7cd4167475b7cc9145e3698d6dd9b"
DECISION_CI_RUN_ID = 31_969_063_955
DECISION_BASE_JOB_ID = 95_218_521_665
DECISION_OPTIONAL_JOB_ID = 95_218_521_647
DECISION_DOCUMENT_RELATIVE_PATH = Path(
    "docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_AUTHORIZATION_DECISION.md"
)
DECISION_DOCUMENT_SHA256 = (
    "5c87f87331b333d2548f8ffbe94d17280b236b723c44c0a5288292ae8d9ed89d"
)
DECISION_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_machine_stable_private_recovery_authorization_decision.v0.json"
)
DECISION_REGISTRY_SHA256 = (
    "d8db42baac8b7235f3b119a14241d46d40a280281920270be7979ea0280ade2d"
)
REQUEST_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_machine_stable_private_recovery_authorization_request.v0.json"
)
REQUEST_REGISTRY_SHA256 = (
    "cf10a7bcd40baa941c81f3966694aa63e80a173c1fc0c4e6e5c2d6c2bcce34a1"
)
IMPLEMENTATION_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_machine_stable_private_recovery_implementation.v0.json"
)
PROOF_CERTIFICATE_RELATIVE_PATH = Path(
    "registries/marc2_machine_stable_private_recovery_proof.v0.json"
)

EXPIRED_CERTIFICATE_RELATIVE_PATH = readiness.CERTIFICATE_RELATIVE_PATH
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_stable_private_recovery/v0"
)
MARKER_NAME = "consumed_marker.v0.json"
PRIVATE_MANIFEST_NAME = "cohort_selection.private.v0.json"
AGGREGATE_REPORT_NAME = "cohort_manifest.aggregate.v0.json"

EXPIRED_CERTIFICATE_BYTES = 4_551
EXPIRED_CERTIFICATE_SHA256 = (
    "5c268ffaefe6e557ace92214c6ec3bab6db29d0a89dee4c83ebd94dbf07b522e"
)
EXPIRED_CERTIFICATE_IMPLEMENTATION_COMMIT = (
    "9fdda316441fef4f245544c90dc0a373993140e0"
)
EXPIRED_CERTIFICATE_FINISHED_AT_UTC = "2026-08-16T19:21:01.928507Z"
EXPIRED_CERTIFICATE_EXPIRES_AT_UTC = "2026-08-16T19:26:01.928507Z"

PRIVATE_SOURCE_BYTES = 418_755
PRIVATE_SOURCE_SHA256 = (
    "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
)
EXPECTED_SOURCE_ROWS = 1_227
EXPECTED_SOURCE_BUNDLES = 238
EXPECTED_ELIGIBLE_BUNDLES = 195
EXPECTED_INELIGIBLE_BUNDLES = 43
EXPECTED_SELECTED_SUBJECTS = 16
EXPECTED_SELECTED_BUNDLES = 96
EXPECTED_SELECTED_MEMBERS = 384
EXPECTED_SELECTED_BYTES = 8_105_207_776

THREAD_ENVIRONMENT = readiness.THREAD_ENVIRONMENT
MAX_RUNTIME_SECONDS = 650.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_COMBINED_OUTPUT_BYTES = 4 * 1024**2
MAX_PROOF_BYTES = 1024**2
MAX_IMPLEMENTATION_REGISTRY_BYTES = 256 * 1024
READ_CHUNK_BYTES = 64 * 1024

ZERO_FORBIDDEN_COUNTERS = {
    "network_requests": 0,
    "network_bytes": 0,
    "archive_member_or_payload_reads": 0,
    "signal_sample_reads": 0,
    "event_onset_channel_geometry_target_or_label_reads": 0,
    "real_derivative_rows": 0,
    "training_or_parameter_update_fits": 0,
    "model_inference_or_prediction_sets": 0,
    "prediction_freezes_target_deliveries_or_scores": 0,
    "provider_or_language_model_calls": 0,
    "hardware_operations": 0,
    "other_file_project_or_consumed_root_deletions": 0,
    "release_or_publication_operations": 0,
    "scientific_claim_upgrades": 0,
}
CLAIM_BOUNDARY = {
    "engineering_capability_added": (
        "A proof-gated machine-stable wrapper can freeze a real target-free "
        "cohort identity from one exact structural manifest without opening "
        "an archive member."
    ),
    "scientific_claim_not_established": (
        "No archive payload neural value target prediction or score is accessed "
        "so this structural result establishes no neural effect decoding "
        "performance language decoding or thought-to-text capability."
    ),
}


class MachineStableRecoveryRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC2-VR4P route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR4P refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True, slots=True)
class RegisteredFileIdentity:
    """One exact no-follow regular-file identity."""

    relative_path: Path
    mode: int
    bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    """Race-detection fields captured without opening content."""

    device: int
    inode: int
    mode: int
    size: int
    owner: int


@dataclass(frozen=True, slots=True)
class ExecutionProof:
    """Remote-green identifiers supplied to the fixed real command."""

    implementation_commit: str
    CI_run_id: int
    base_job_id: int
    optional_job_id: int
    proof_record_sha256: str
    proof_summary: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class SequenceOutcome:
    """One generated or real structural sequence outcome."""

    aggregate_report: Mapping[str, Any]
    aggregate_bytes: bytes
    private_manifest_bytes: bytes
    marker_bytes: bytes
    certificate_bytes: bytes
    expired_input_bytes: int
    source_input_bytes: int
    output_files: tuple[str, ...]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[8], "output JSON is not canonical"
        ) from exc


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _strict_json(payload: bytes, *, route: str) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise MachineStableRecoveryRefusal(route, "JSON encoding differs")
    try:
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise MachineStableRecoveryRefusal(route, "JSON parse refused") from exc
    if not isinstance(value, dict):
        raise MachineStableRecoveryRefusal(route, "JSON root is not an object")
    return value


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _parse_utc(value: Any, *, route: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MachineStableRecoveryRefusal(route, "UTC timestamp is malformed")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise MachineStableRecoveryRefusal(
            route, "UTC timestamp is malformed"
        ) from exc
    if parsed.tzinfo != timezone.utc:
        raise MachineStableRecoveryRefusal(route, "UTC timestamp offset differs")
    return parsed


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


def _read_small_tracked_file(path: Path, maximum_bytes: int, route: str) -> bytes:
    try:
        info = path.lstat()
    except OSError as exc:
        raise MachineStableRecoveryRefusal(route, "tracked artifact unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise MachineStableRecoveryRefusal(route, "tracked artifact type differs")
    if info.st_size > maximum_bytes:
        raise MachineStableRecoveryRefusal(route, "tracked artifact cap exceeded")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != info.st_dev
                or opened.st_ino != info.st_ino
                or opened.st_size != info.st_size
            ):
                raise MachineStableRecoveryRefusal(
                    route, "tracked artifact identity changed"
                )
            payload = bytearray()
            while len(payload) <= maximum_bytes:
                chunk = os.read(descriptor, min(READ_CHUNK_BYTES, maximum_bytes + 1 - len(payload)))
                if not chunk:
                    break
                payload.extend(chunk)
        finally:
            os.close(descriptor)
    except MachineStableRecoveryRefusal:
        raise
    except OSError as exc:
        raise MachineStableRecoveryRefusal(route, "tracked artifact read refused") from exc
    if len(payload) != info.st_size or len(payload) > maximum_bytes:
        raise MachineStableRecoveryRefusal(route, "tracked artifact size changed")
    return bytes(payload)


def _load_exact_json_artifact(
    root: Path,
    relative_path: Path,
    expected_sha256: str,
    maximum_bytes: int,
    route: str,
) -> dict[str, Any]:
    payload = _read_small_tracked_file(root / relative_path, maximum_bytes, route)
    if _sha256_bytes(payload) != expected_sha256:
        raise MachineStableRecoveryRefusal(route, "tracked artifact hash differs")
    return _strict_json(payload, route=route)


def load_implementation_registry(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and semantically validate the native implementation registry."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _load_exact_json_artifact(
        root,
        DECISION_REGISTRY_RELATIVE_PATH,
        DECISION_REGISTRY_SHA256,
        MAX_IMPLEMENTATION_REGISTRY_BYTES,
        REFUSAL_ROUTES[0],
    )
    request = _load_exact_json_artifact(
        root,
        REQUEST_REGISTRY_RELATIVE_PATH,
        REQUEST_REGISTRY_SHA256,
        MAX_IMPLEMENTATION_REGISTRY_BYTES,
        REFUSAL_ROUTES[0],
    )
    payload = _read_small_tracked_file(
        root / IMPLEMENTATION_REGISTRY_RELATIVE_PATH,
        MAX_IMPLEMENTATION_REGISTRY_BYTES,
        REFUSAL_ROUTES[0],
    )
    registry = _strict_json(payload, route=REFUSAL_ROUTES[0])
    proof = registry.get("green_authorization_decision", {})
    paths = registry.get("fixed_paths", {})
    surface = registry.get("implementation_surface", {})
    execution = registry.get("real_execution_state", {})
    if (
        decision.get("authorization_parent_commit")
        != "a5b73d6859c71054a1f20ab6c1c500341539efea"
        or request.get("lane_id") != LANE_ID
        or registry.get("schema_name")
        != "neurodecodekit.marc2_machine_stable_private_recovery_implementation"
        or registry.get("schema_version") != SCHEMA_VERSION
        or registry.get("lane_id") != LANE_ID
        or registry.get("status")
        != "generated_mock_implementation_complete_real_sequence_not_executed"
        or proof
        != {
            "commit": DECISION_COMMIT,
            "CI_run_id": DECISION_CI_RUN_ID,
            "base_python_job_id": DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "decision_registry_sha256": DECISION_REGISTRY_SHA256,
        }
        or paths.get("expired_certificate")
        != EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix()
        or paths.get("private_source") != PRIVATE_SOURCE_RELATIVE_PATH.as_posix()
        or paths.get("new_output_root") != OUTPUT_ROOT_RELATIVE_PATH.as_posix()
        or surface.get("module") != MODULE_NAME
        or surface.get("commands") != ["plan", "qualify", "inspect", "execute"]
        or surface.get("standard_library_only") is not True
        or surface.get("generic_source_output_cleanup_or_project_override") is not False
        or surface.get("consumed_executor_import_call_copy_edit_or_alias") is not False
        or execution.get("registered_real_execution_limit") != 1
        or execution.get("registered_real_execution_consumed") is not False
        or execution.get("retry_rerun_resume_repair_or_fallback_limit") != 0
        or any(registry.get("implementation_access_counters", {}).values())
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[0], "implementation registry semantics differ"
        )
    return registry


def _git_output(root: Path, arguments: Sequence[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[0], "local Git proof refused"
        ) from exc
    return completed.stdout.strip()


def validate_execution_proof(
    *,
    implementation_commit: str,
    CI_run_id: int,
    base_job_id: int,
    optional_job_id: int,
    repo_root: str | Path | None = None,
) -> ExecutionProof:
    """Validate the exact committed proof record and supplied green identifiers."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_implementation_registry(root)
    proof_bytes = _read_small_tracked_file(
        root / PROOF_CERTIFICATE_RELATIVE_PATH,
        MAX_PROOF_BYTES,
        REFUSAL_ROUTES[0],
    )
    proof_sha256 = _sha256_bytes(proof_bytes)
    head = _git_output(root, ["rev-parse", "HEAD"])
    tracked_status = _git_output(root, ["status", "--porcelain", "--untracked-files=no"])
    if head != implementation_commit or tracked_status:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[0], "implementation HEAD or tracked worktree differs"
        )
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", DECISION_COMMIT, head],
            cwd=root,
            check=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[0], "green decision ancestry differs"
        ) from exc
    envelope = proof_recovery.ProofEnvelope(
        implementation_commit=implementation_commit,
        implementation_CI_run_id=CI_run_id,
        implementation_base_job_id=base_job_id,
        implementation_optional_job_id=optional_job_id,
        implementation_registry_sha256=proof_sha256,
        observed_HEAD=head,
        tracked_worktree_clean=True,
        green_decision_ancestor=True,
    )
    try:
        summary = proof_recovery.validate_implementation_record(
            proof_bytes,
            repo_root=root,
            expected_proof=envelope,
            observed_proof=envelope,
        )
    except proof_recovery.ProofRecordRefusal as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[0], "shared implementation proof refused"
        ) from exc
    return ExecutionProof(
        implementation_commit=implementation_commit,
        CI_run_id=CI_run_id,
        base_job_id=base_job_id,
        optional_job_id=optional_job_id,
        proof_record_sha256=proof_sha256,
        proof_summary=summary.to_mapping(),
    )


def _validate_absolute_directory_chain(root: Path, route: str) -> Path:
    absolute = root.absolute()
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current = current / component
        try:
            info = current.lstat()
        except OSError as exc:
            raise MachineStableRecoveryRefusal(route, "root path unavailable") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise MachineStableRecoveryRefusal(route, "root path component differs")
    return absolute


def _validate_parent_chain(root: Path, relative: Path, route: str) -> None:
    current = _validate_absolute_directory_chain(root, route)
    for component in relative.parts[:-1]:
        current = current / component
        try:
            info = current.lstat()
        except OSError as exc:
            raise MachineStableRecoveryRefusal(route, "path parent unavailable") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise MachineStableRecoveryRefusal(route, "path parent type differs")


def _preflight_registered_file(
    root: Path,
    identity: RegisteredFileIdentity,
    route: str,
) -> FileSnapshot:
    _validate_parent_chain(root, identity.relative_path, route)
    path = root / identity.relative_path
    try:
        info = path.lstat()
    except OSError as exc:
        raise MachineStableRecoveryRefusal(route, "registered file unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise MachineStableRecoveryRefusal(route, "registered file type differs")
    if stat.S_IMODE(info.st_mode) != identity.mode:
        raise MachineStableRecoveryRefusal(route, "registered file mode differs")
    if info.st_uid != os.getuid():
        raise MachineStableRecoveryRefusal(route, "registered file owner differs")
    if info.st_size != identity.bytes:
        raise MachineStableRecoveryRefusal(route, "registered file size differs")
    return FileSnapshot(
        device=info.st_dev,
        inode=info.st_ino,
        mode=stat.S_IMODE(info.st_mode),
        size=info.st_size,
        owner=info.st_uid,
    )


def _read_exact_nofollow(
    root: Path,
    identity: RegisteredFileIdentity,
    snapshot: FileSnapshot,
    route: str,
) -> bytes:
    path = root / identity.relative_path
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    payload = bytearray()
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != snapshot.device
                or opened.st_ino != snapshot.inode
                or stat.S_IMODE(opened.st_mode) != snapshot.mode
                or opened.st_size != snapshot.size
                or opened.st_uid != snapshot.owner
            ):
                raise MachineStableRecoveryRefusal(
                    route, "registered file identity changed before open"
                )
            while len(payload) < identity.bytes:
                chunk = os.read(
                    descriptor,
                    min(READ_CHUNK_BYTES, identity.bytes - len(payload)),
                )
                if not chunk:
                    break
                payload.extend(chunk)
            if os.read(descriptor, 1):
                raise MachineStableRecoveryRefusal(
                    route, "registered file exceeds exact byte count"
                )
        finally:
            os.close(descriptor)
    except MachineStableRecoveryRefusal:
        raise
    except OSError as exc:
        raise MachineStableRecoveryRefusal(route, "registered file open refused") from exc
    if len(payload) != identity.bytes:
        raise MachineStableRecoveryRefusal(route, "registered file read is short")
    if _sha256_bytes(payload) != identity.sha256:
        raise MachineStableRecoveryRefusal(route, "registered file hash differs")
    return bytes(payload)


def _validate_expired_certificate(
    payload: bytes,
    *,
    implementation_commit: str,
    finished_at_UTC: str,
    expires_at_UTC: str,
    now_UTC: datetime,
) -> dict[str, Any]:
    certificate = _strict_json(payload, route=REFUSAL_ROUTES[2])
    if _canonical_json_bytes(certificate) != payload:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[2], "expired certificate is not canonical"
        )
    try:
        readiness.validate_certificate(certificate)
    except readiness.MachineReadinessRefusal as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[2], "expired certificate semantics differ"
        ) from exc
    if (
        certificate.get("proof_posture") != "machine_only_non_scientific"
        or certificate.get("implementation_commit") != implementation_commit
        or certificate.get("finished_at_UTC") != finished_at_UTC
        or certificate.get("expires_at_UTC") != expires_at_UTC
        or certificate.get("certificate_path")
        != EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix()
        or now_UTC <= _parse_utc(expires_at_UTC, route=REFUSAL_ROUTES[2])
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[2], "expired certificate identity or state differs"
        )
    return certificate


def _unlink_exact_file(
    root: Path,
    identity: RegisteredFileIdentity,
    snapshot: FileSnapshot,
) -> None:
    path = root / identity.relative_path
    try:
        current = path.lstat()
    except OSError as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[2], "expired certificate disappeared"
        ) from exc
    if (
        current.st_dev != snapshot.device
        or current.st_ino != snapshot.inode
        or current.st_size != snapshot.size
        or stat.S_IMODE(current.st_mode) != snapshot.mode
        or current.st_uid != snapshot.owner
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[2], "expired certificate changed before unlink"
        )
    try:
        os.unlink(path)
    except OSError as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[2], "expired certificate unlink refused"
        ) from exc
    if path.exists() or path.is_symlink():
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[2], "expired certificate remains after unlink"
        )


def _thread_values(environ: Mapping[str, str]) -> dict[str, str | None]:
    return {name: environ.get(name) for name in THREAD_ENVIRONMENT}


def _observe_machine(root: Path, sequence: int) -> dict[str, Any]:
    try:
        load = os.getloadavg()[0]
    except (AttributeError, OSError) as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[3], "one-minute load unavailable"
        ) from exc
    logical_cpus = os.cpu_count()
    normalized = load / logical_cpus if logical_cpus else None
    return {
        "sequence": sequence,
        "observed_at_UTC": _format_utc(datetime.now(timezone.utc)),
        "monotonic_seconds": time.monotonic(),
        "logical_CPUs": logical_cpus,
        "one_minute_load": load,
        "normalized_one_minute_load": normalized,
        "process_peak_RSS_bytes": _peak_rss_bytes(),
        "free_disk_bytes": shutil.disk_usage(root).free,
    }


def _ensure_new_parent_tree(root: Path, relative_parent: Path, route: str) -> None:
    current = _validate_absolute_directory_chain(root, route)
    for component in relative_parent.parts:
        current = current / component
        if current.exists() or current.is_symlink():
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise MachineStableRecoveryRefusal(route, "output parent type differs")
        else:
            try:
                current.mkdir(mode=0o700)
            except OSError as exc:
                raise MachineStableRecoveryRefusal(
                    route, "output parent creation refused"
                ) from exc


def _write_exclusive(
    path: Path,
    payload: bytes,
    *,
    mode: int,
    route: str,
) -> None:
    if path.exists() or path.is_symlink():
        raise MachineStableRecoveryRefusal(route, "output overwrite refused")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise MachineStableRecoveryRefusal(route, "output write refused") from exc
    info = path.lstat()
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != mode
        or info.st_size != len(payload)
    ):
        raise MachineStableRecoveryRefusal(route, "written output shape differs")


def _write_fresh_certificate(root: Path, certificate: Mapping[str, Any]) -> bytes:
    payload = _canonical_json_bytes(certificate)
    if len(payload) > readiness.MAX_CERTIFICATE_BYTES:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[3], "fresh certificate cap exceeded"
        )
    _ensure_new_parent_tree(
        root, EXPIRED_CERTIFICATE_RELATIVE_PATH.parent, REFUSAL_ROUTES[3]
    )
    _write_exclusive(
        root / EXPIRED_CERTIFICATE_RELATIVE_PATH,
        payload,
        mode=0o600,
        route=REFUSAL_ROUTES[3],
    )
    return payload


def _run_fresh_readiness(
    root: Path,
    *,
    implementation_commit: str,
    sampler: Callable[[Path, int], Mapping[str, Any]],
    sleeper: Callable[[float], None],
    environ: Mapping[str, str],
) -> tuple[dict[str, Any], bytes]:
    thread_values = _thread_values(environ)
    raw_samples: list[Mapping[str, Any]] = []
    first_monotonic: float | None = None
    certificate: dict[str, Any] | None = None
    while len(raw_samples) < readiness.MAXIMUM_SAMPLES:
        sample = dict(sampler(root, len(raw_samples) + 1))
        raw_samples.append(sample)
        if first_monotonic is None:
            first_monotonic = float(sample["monotonic_seconds"])
        try:
            certificate = readiness.build_certificate(
                raw_samples,
                implementation_commit=implementation_commit,
                thread_environment=thread_values,
                proof_posture="machine_only_non_scientific",
                certificate_path=EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix(),
            )
        except readiness.MachineReadinessRefusal as exc:
            raise MachineStableRecoveryRefusal(
                REFUSAL_ROUTES[3], "fresh readiness sample refused"
            ) from exc
        if certificate["ready"]:
            break
        elapsed = float(sample["monotonic_seconds"]) - first_monotonic
        if (
            elapsed >= readiness.MAXIMUM_WAIT_SECONDS
            or thread_values != {name: "1" for name in THREAD_ENVIRONMENT}
        ):
            break
        sleeper(readiness.MINIMUM_SAMPLE_INTERVAL_SECONDS)
    if certificate is None:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[3], "fresh readiness produced no sample"
        )
    certificate_bytes = _write_fresh_certificate(root, certificate)
    if certificate.get("ready") is not True:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[3], "fresh readiness did not pass"
        )
    return certificate, certificate_bytes


def _pre_marker_machine_recheck(
    root: Path,
    *,
    environ: Mapping[str, str],
    rss_reader: Callable[[], int],
) -> dict[str, int | bool]:
    threads_ok = _thread_values(environ) == {
        name: "1" for name in THREAD_ENVIRONMENT
    }
    rss = rss_reader()
    free_disk = shutil.disk_usage(root).free
    if (
        not threads_ok
        or isinstance(rss, bool)
        or not isinstance(rss, int)
        or rss < 0
        or rss >= MAX_PEAK_RSS_BYTES
        or free_disk < MINIMUM_FREE_DISK_BYTES
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[4], "pre-marker thread RSS or disk gate refused"
        )
    return {
        "thread_environment_all_one": threads_ok,
        "process_peak_RSS_bytes": rss,
        "free_disk_bytes": free_disk,
        "second_load_gate_performed": False,
    }


def _create_new_output_root(root: Path) -> Path:
    relative_parent = OUTPUT_ROOT_RELATIVE_PATH.parent
    _ensure_new_parent_tree(root, relative_parent, REFUSAL_ROUTES[4])
    output_root = root / OUTPUT_ROOT_RELATIVE_PATH
    if output_root.exists() or output_root.is_symlink():
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[4], "registered output root is not absent"
        )
    try:
        output_root.mkdir(mode=0o700)
    except OSError as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[4], "registered output root creation refused"
        ) from exc
    return output_root


def _selection_invariants(adapted: adapter.AdaptedLiveDomain) -> None:
    counts = adapted.predicate_counts
    selection = adapted.selection
    if (
        sum(counts.values()) != EXPECTED_SOURCE_BUNDLES
        or counts.get(adapter.PREDICATE_CODES[0]) != EXPECTED_ELIGIBLE_BUNDLES
        or sum(counts.get(code, 0) for code in adapter.PREDICATE_CODES[1:])
        != EXPECTED_INELIGIBLE_BUNDLES
        or selection.cohort_summary.get("selected_subjects")
        != EXPECTED_SELECTED_SUBJECTS
        or selection.split_summary.get("selected_run_bundles")
        != EXPECTED_SELECTED_BUNDLES
        or selection.split_summary.get("selected_core_members")
        != EXPECTED_SELECTED_MEMBERS
        or selection.byte_summary.get("selected_reservation_bytes")
        != EXPECTED_SELECTED_BYTES
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[7], "structural cohort invariants differ"
        )


def _contains_forbidden_aggregate_key(value: Any) -> bool:
    forbidden = {
        "subject_id",
        "selected_subject_ids",
        "member_name",
        "local_header_offset",
        "CRC32",
        "private_source_path",
        "private_output_path",
        "local_path",
    }
    if isinstance(value, Mapping):
        return any(
            key in forbidden or _contains_forbidden_aggregate_key(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_aggregate_key(item) for item in value)
    if isinstance(value, str):
        return (
            ".codex_work/" in value
            or "Freewill_generated/" in value
            or "/Users/" in value
        )
    return False


def validate_aggregate_report(report: Mapping[str, Any]) -> None:
    """Validate the aggregate privacy, counter, and claim boundary."""

    required = {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "proof_posture",
        "implementation_proof",
        "source_summary",
        "cohort_summary",
        "selection_hashes",
        "measurements",
        "operation_counters",
        "forbidden_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    if set(report) != required:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[8], "aggregate report fields differ"
        )
    if (
        report.get("schema_name")
        != "neurodecodekit.marc2_machine_stable_private_recovery_result"
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
        or report.get("claim_boundary") != CLAIM_BOUNDARY
        or report.get("forbidden_counters") != ZERO_FORBIDDEN_COUNTERS
        or _contains_forbidden_aggregate_key(report)
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[8], "aggregate privacy or claim boundary differs"
        )
    measurements = report.get("measurements", {})
    if (
        not isinstance(measurements, Mapping)
        or measurements.get("combined_output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1)
        > MAX_COMBINED_OUTPUT_BYTES
        or measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES)
        >= MAX_PEAK_RSS_BYTES
        or measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1)
        > MAX_RUNTIME_SECONDS
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[8], "aggregate resource measurements differ"
        )


def _operation_counters(
    *,
    real: bool,
    sample_count: int,
    expired_input_bytes: int,
    source_input_bytes: int,
) -> dict[str, int]:
    values = {
        "expired_certificate_path_checks": 1,
        "expired_certificate_content_opens": 1,
        "expired_certificate_bytes_read": expired_input_bytes,
        "expired_certificate_unlinks": 1,
        "fresh_machine_readiness_invocations": 1,
        "fresh_machine_readiness_samples": sample_count,
        "fresh_readiness_certificates": 1,
        "private_source_path_operations": 1,
        "private_output_root_operations": 1,
        "private_consumed_markers": 1,
        "private_structural_content_opens": 1,
        "private_structural_input_bytes": source_input_bytes,
        "VR2_adapter_calls": 1,
        "real_cohort_freezes": 1,
    }
    if real:
        return values
    return {f"generated_fixture_{key}": value for key, value in values.items()}


def _build_aggregate_report(
    *,
    proof: ExecutionProof,
    source_identity: RegisteredFileIdentity,
    adapted: adapter.AdaptedLiveDomain,
    certificate: Mapping[str, Any],
    certificate_bytes: bytes,
    expired_input_bytes: int,
    marker_bytes: bytes,
    private_bytes: bytes,
    runtime_seconds: float,
    peak_rss_bytes: int,
    real: bool,
) -> dict[str, Any]:
    selection = adapted.selection
    output_bytes_without_report = (
        len(certificate_bytes) + len(marker_bytes) + len(private_bytes)
    )
    report: dict[str, Any] = {
        "schema_name": "neurodecodekit.marc2_machine_stable_private_recovery_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_target_free_structural_cohort_freeze",
        "route": SUCCESS_ROUTE,
        "proof_posture": (
            "real_private_structural_metadata_only"
            if real
            else "generated_fixture_only_no_scientific_value"
        ),
        "implementation_proof": {
            "commit": proof.implementation_commit,
            "CI_run_id": proof.CI_run_id,
            "base_python_job_id": proof.base_job_id,
            "optional_neuro_job_id": proof.optional_job_id,
            "proof_record_sha256": proof.proof_record_sha256,
        },
        "source_summary": {
            "input_bytes": source_identity.bytes,
            "input_sha256": source_identity.sha256,
            "rows": EXPECTED_SOURCE_ROWS,
            "complete_bundles": EXPECTED_SOURCE_BUNDLES,
            "eligible_bundles": EXPECTED_ELIGIBLE_BUNDLES,
            "valid_ineligible_bundles": EXPECTED_INELIGIBLE_BUNDLES,
            "content_opens": 1,
        },
        "cohort_summary": {
            "selected_subjects": EXPECTED_SELECTED_SUBJECTS,
            "selected_bundles": EXPECTED_SELECTED_BUNDLES,
            "selected_members": EXPECTED_SELECTED_MEMBERS,
            "selected_declared_bytes": EXPECTED_SELECTED_BYTES,
            "selected_bytes_are_reservation_metadata_only": True,
            "archive_member_or_payload_bytes": 0,
        },
        "selection_hashes": dict(selection.selection_hashes),
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "fresh_readiness_samples": len(certificate["samples"]),
            "fresh_readiness_wait_seconds": certificate["measurements"]["wait_seconds"],
            "fresh_readiness_maximum_normalized_load": max(
                sample["normalized_one_minute_load"]
                for sample in certificate["samples"]
            ),
            "fresh_readiness_minimum_free_disk_bytes": min(
                sample["free_disk_bytes"] for sample in certificate["samples"]
            ),
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
            "fresh_readiness_certificate_bytes": len(certificate_bytes),
            "marker_bytes": len(marker_bytes),
            "private_manifest_bytes": len(private_bytes),
            "aggregate_report_bytes": 0,
            "combined_output_bytes": output_bytes_without_report,
        },
        "operation_counters": _operation_counters(
            real=real,
            sample_count=len(certificate["samples"]),
            expired_input_bytes=expired_input_bytes,
            source_input_bytes=source_identity.bytes,
        ),
        "forbidden_counters": copy.deepcopy(ZERO_FORBIDDEN_COUNTERS),
        "warnings": [
            "Selected declared bytes are reservation metadata, not downloaded bytes.",
            "This pass opens no archive member and reads no neural value or target.",
            "A separate FW2 packet and decision are required before payload access.",
        ],
        "unavailable_fields": [
            "archive_member_payload",
            "EEG_or_MEG_signal",
            "event_or_target",
            "channel_or_geometry",
            "model_or_prediction",
            "scientific_score",
            "end_to_end_latency",
        ],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    for _ in range(8):
        report_bytes = _canonical_json_bytes(report)
        combined = output_bytes_without_report + len(report_bytes)
        measurements = report["measurements"]
        if (
            measurements["aggregate_report_bytes"] == len(report_bytes)
            and measurements["combined_output_bytes"] == combined
        ):
            break
        measurements["aggregate_report_bytes"] = len(report_bytes)
        measurements["combined_output_bytes"] = combined
    validate_aggregate_report(report)
    return report


def _run_structural_sequence(
    *,
    root: Path,
    proof: ExecutionProof,
    expired_identity: RegisteredFileIdentity,
    expired_implementation_commit: str,
    expired_finished_at_UTC: str,
    expired_expires_at_UTC: str,
    source_identity: RegisteredFileIdentity,
    adapter_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
    sampler: Callable[[Path, int], Mapping[str, Any]],
    sleeper: Callable[[float], None],
    environ: Mapping[str, str],
    now_UTC: Callable[[], datetime],
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    real: bool,
) -> SequenceOutcome:
    started = clock()
    expired_snapshot = _preflight_registered_file(
        root, expired_identity, REFUSAL_ROUTES[1]
    )
    expired_payload = _read_exact_nofollow(
        root, expired_identity, expired_snapshot, REFUSAL_ROUTES[2]
    )
    _validate_expired_certificate(
        expired_payload,
        implementation_commit=expired_implementation_commit,
        finished_at_UTC=expired_finished_at_UTC,
        expires_at_UTC=expired_expires_at_UTC,
        now_UTC=now_UTC(),
    )
    _unlink_exact_file(root, expired_identity, expired_snapshot)
    certificate, certificate_bytes = _run_fresh_readiness(
        root,
        implementation_commit=proof.implementation_commit,
        sampler=sampler,
        sleeper=sleeper,
        environ=environ,
    )
    try:
        readiness.validate_certificate(certificate, now_UTC=now_UTC())
    except readiness.MachineReadinessRefusal as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[3], "fresh certificate expired before private preflight"
        ) from exc
    _pre_marker_machine_recheck(root, environ=environ, rss_reader=rss_reader)
    source_snapshot = _preflight_registered_file(
        root, source_identity, REFUSAL_ROUTES[5]
    )
    output_root = _create_new_output_root(root)
    marker = {
        "schema_name": "neurodecodekit.marc2_machine_stable_private_recovery_marker",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_before_private_content_open",
        "recorded_at_UTC": _format_utc(now_UTC()),
        "implementation_commit": proof.implementation_commit,
        "proof_record_sha256": proof.proof_record_sha256,
        "registered_source_sha256": source_identity.sha256,
        "retry_rerun_resume_repair_or_fallback_limit": 0,
    }
    marker_bytes = _canonical_json_bytes(marker)
    _write_exclusive(
        output_root / MARKER_NAME,
        marker_bytes,
        mode=0o600,
        route=REFUSAL_ROUTES[6],
    )
    source_payload = _read_exact_nofollow(
        root, source_identity, source_snapshot, REFUSAL_ROUTES[6]
    )
    source = _strict_json(source_payload, route=REFUSAL_ROUTES[7])
    source_before = _canonical_json_bytes(source)
    try:
        adapted = adapter.adapt_live_domain_source(
            source,
            contract=adapter_contract,
            selector_contract=selector_contract,
        )
    except adapter.LiveDomainEligibilityRefusal as exc:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[7], "VR2 structural adapter refused"
        ) from exc
    if _canonical_json_bytes(source) != source_before:
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[7], "VR2 adapter mutated the source object"
        )
    _selection_invariants(adapted)
    private_bytes = _canonical_json_bytes(adapted.selection.private_manifest)
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    report = _build_aggregate_report(
        proof=proof,
        source_identity=source_identity,
        adapted=adapted,
        certificate=certificate,
        certificate_bytes=certificate_bytes,
        expired_input_bytes=expired_identity.bytes,
        marker_bytes=marker_bytes,
        private_bytes=private_bytes,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        real=real,
    )
    aggregate_bytes = _canonical_json_bytes(report)
    combined_output_bytes = (
        len(certificate_bytes)
        + len(marker_bytes)
        + len(private_bytes)
        + len(aggregate_bytes)
    )
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes < 0
        or peak_rss_bytes >= MAX_PEAK_RSS_BYTES
        or combined_output_bytes > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[8], "runtime RSS or output cap refused"
        )
    _write_exclusive(
        output_root / PRIVATE_MANIFEST_NAME,
        private_bytes,
        mode=0o600,
        route=REFUSAL_ROUTES[8],
    )
    _write_exclusive(
        output_root / AGGREGATE_REPORT_NAME,
        aggregate_bytes,
        mode=0o644,
        route=REFUSAL_ROUTES[8],
    )
    output_files = tuple(sorted(path.name for path in output_root.iterdir()))
    if output_files != tuple(
        sorted((MARKER_NAME, PRIVATE_MANIFEST_NAME, AGGREGATE_REPORT_NAME))
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[8], "output inventory differs"
        )
    return SequenceOutcome(
        aggregate_report=report,
        aggregate_bytes=aggregate_bytes,
        private_manifest_bytes=private_bytes,
        marker_bytes=marker_bytes,
        certificate_bytes=certificate_bytes,
        expired_input_bytes=expired_identity.bytes,
        source_input_bytes=source_identity.bytes,
        output_files=output_files,
    )


def execute_registered(
    *,
    implementation_commit: str,
    CI_run_id: int,
    base_job_id: int,
    optional_job_id: int,
) -> SequenceOutcome:
    """Run the sole fixed-path real structural sequence after remote proof."""

    root = _repo_root()
    proof = validate_execution_proof(
        implementation_commit=implementation_commit,
        CI_run_id=CI_run_id,
        base_job_id=base_job_id,
        optional_job_id=optional_job_id,
        repo_root=root,
    )
    adapter_contract = adapter.load_registered_contract(root)
    selector_contract = selector.load_registered_contract(root)
    return _run_structural_sequence(
        root=root,
        proof=proof,
        expired_identity=RegisteredFileIdentity(
            relative_path=EXPIRED_CERTIFICATE_RELATIVE_PATH,
            mode=0o600,
            bytes=EXPIRED_CERTIFICATE_BYTES,
            sha256=EXPIRED_CERTIFICATE_SHA256,
        ),
        expired_implementation_commit=EXPIRED_CERTIFICATE_IMPLEMENTATION_COMMIT,
        expired_finished_at_UTC=EXPIRED_CERTIFICATE_FINISHED_AT_UTC,
        expired_expires_at_UTC=EXPIRED_CERTIFICATE_EXPIRES_AT_UTC,
        source_identity=RegisteredFileIdentity(
            relative_path=PRIVATE_SOURCE_RELATIVE_PATH,
            mode=0o600,
            bytes=PRIVATE_SOURCE_BYTES,
            sha256=PRIVATE_SOURCE_SHA256,
        ),
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
        sampler=_observe_machine,
        sleeper=time.sleep,
        environ=os.environ,
        now_UTC=lambda: datetime.now(timezone.utc),
        clock=time.perf_counter,
        rss_reader=_peak_rss_bytes,
        real=True,
    )


def _generated_raw_samples(base: datetime) -> list[dict[str, Any]]:
    return [
        {
            "sequence": index + 1,
            "observed_at_UTC": _format_utc(base + timedelta(seconds=5 * index)),
            "monotonic_seconds": 100.0 + 5 * index,
            "logical_CPUs": 4,
            "one_minute_load": 0.5,
            "normalized_one_minute_load": 0.125,
            "process_peak_RSS_bytes": 32 * 1024**2,
            "free_disk_bytes": 20 * 1024**3,
        }
        for index in range(3)
    ]


def _write_generated_fixture_file(
    root: Path, relative: Path, payload: bytes, mode: int
) -> None:
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    destination.chmod(mode)


def _generated_proof(repo_root: Path) -> ExecutionProof:
    tracked = (
        proof_recovery.MODULE_RELATIVE_PATH,
        proof_recovery.CONTRACT_RELATIVE_PATH,
        Path("docs/MARC_2_PROOF_RECORD_RECOVERY_PREREGISTRATION.md"),
        Path("tests/test_marc2_proof_record_recovery_contract.py"),
    )
    record = proof_recovery.build_generated_candidate_record(
        repo_root, tracked_artifacts=tracked
    )
    record_bytes = (
        json.dumps(
            record,
            sort_keys=False,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")
    envelope = proof_recovery.ProofEnvelope(
        implementation_commit="a" * 40,
        implementation_CI_run_id=1,
        implementation_base_job_id=2,
        implementation_optional_job_id=3,
        implementation_registry_sha256=_sha256_bytes(record_bytes),
        observed_HEAD="a" * 40,
        tracked_worktree_clean=True,
        green_decision_ancestor=True,
    )
    summary = proof_recovery.validate_implementation_record(
        record_bytes,
        repo_root=repo_root,
        expected_proof=envelope,
        observed_proof=envelope,
    )
    return ExecutionProof(
        implementation_commit="a" * 40,
        CI_run_id=1,
        base_job_id=2,
        optional_job_id=3,
        proof_record_sha256=_sha256_bytes(record_bytes),
        proof_summary=summary.to_mapping(),
    )


def _run_generated_fixture(repo_root: Path) -> SequenceOutcome:
    adapter_contract = adapter.load_registered_contract(repo_root)
    selector_contract = selector.load_registered_contract(repo_root)
    source = adapter.build_generated_live_source(
        profile="A",
        contract=adapter_contract,
        selector_contract=selector_contract,
    )
    source_bytes = _canonical_json_bytes(source)
    old_base = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
    old_certificate = readiness.build_certificate(
        _generated_raw_samples(old_base),
        implementation_commit="b" * 40,
        thread_environment={name: "1" for name in THREAD_ENVIRONMENT},
        proof_posture="machine_only_non_scientific",
        certificate_path=EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix(),
    )
    old_certificate_bytes = _canonical_json_bytes(old_certificate)
    fresh_samples = iter(
        _generated_raw_samples(datetime(2026, 8, 16, 13, 0, tzinfo=timezone.utc))
    )
    now_values = iter(
        datetime(2026, 8, 16, 13, 1, tzinfo=timezone.utc)
        + timedelta(seconds=index)
        for index in range(5)
    )
    clock_values = iter((10.0, 10.25))
    proof = _generated_proof(repo_root)
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir).resolve()
        _write_generated_fixture_file(
            root,
            EXPIRED_CERTIFICATE_RELATIVE_PATH,
            old_certificate_bytes,
            0o600,
        )
        _write_generated_fixture_file(
            root, PRIVATE_SOURCE_RELATIVE_PATH, source_bytes, 0o600
        )
        outcome = _run_structural_sequence(
            root=root,
            proof=proof,
            expired_identity=RegisteredFileIdentity(
                EXPIRED_CERTIFICATE_RELATIVE_PATH,
                0o600,
                len(old_certificate_bytes),
                _sha256_bytes(old_certificate_bytes),
            ),
            expired_implementation_commit="b" * 40,
            expired_finished_at_UTC=old_certificate["finished_at_UTC"],
            expired_expires_at_UTC=old_certificate["expires_at_UTC"],
            source_identity=RegisteredFileIdentity(
                PRIVATE_SOURCE_RELATIVE_PATH,
                0o600,
                len(source_bytes),
                _sha256_bytes(source_bytes),
            ),
            adapter_contract=adapter_contract,
            selector_contract=selector_contract,
            sampler=lambda _root, _sequence: next(fresh_samples),
            sleeper=lambda _seconds: None,
            environ={name: "1" for name in THREAD_ENVIRONMENT},
            now_UTC=lambda: next(now_values),
            clock=lambda: next(clock_values),
            rss_reader=lambda: 40 * 1024**2,
            real=False,
        )
        return outcome


def _expect_refusal(name: str, callback: Callable[[], Any]) -> str:
    try:
        callback()
    except MachineStableRecoveryRefusal as exc:
        return exc.route
    raise MachineStableRecoveryRefusal(
        REFUSAL_ROUTES[9], f"generated mutation {name} was accepted"
    )


def _generated_mutations(repo_root: Path) -> dict[str, str]:
    certificate = readiness.build_certificate(
        _generated_raw_samples(datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)),
        implementation_commit="b" * 40,
        thread_environment={name: "1" for name in THREAD_ENVIRONMENT},
        proof_posture="machine_only_non_scientific",
        certificate_path=EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix(),
    )
    payload = _canonical_json_bytes(certificate)
    mutations: list[tuple[str, Callable[[], Any]]] = []

    def certificate_case(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        changed = copy.deepcopy(certificate)
        mutate(changed)
        changed_payload = _canonical_json_bytes(changed)
        mutations.append(
            (
                name,
                lambda value=changed_payload: _validate_expired_certificate(
                    value,
                    implementation_commit="b" * 40,
                    finished_at_UTC=certificate["finished_at_UTC"],
                    expires_at_UTC=certificate["expires_at_UTC"],
                    now_UTC=datetime(2026, 8, 16, 14, 0, tzinfo=timezone.utc),
                ),
            )
        )

    certificate_case("certificate_schema", lambda value: value.__setitem__("schema_name", "wrong"))
    certificate_case("certificate_commit", lambda value: value.__setitem__("implementation_commit", "c" * 40))
    certificate_case("certificate_path", lambda value: value.__setitem__("certificate_path", "wrong"))
    certificate_case("certificate_counter", lambda value: value["access_counters"].__setitem__("network_requests", 1))
    mutations.extend(
        [
            (
                "certificate_noncanonical",
                lambda: _validate_expired_certificate(
                    payload.rstrip(b"\n"),
                    implementation_commit="b" * 40,
                    finished_at_UTC=certificate["finished_at_UTC"],
                    expires_at_UTC=certificate["expires_at_UTC"],
                    now_UTC=datetime(2026, 8, 16, 14, 0, tzinfo=timezone.utc),
                ),
            ),
            (
                "certificate_not_expired",
                lambda: _validate_expired_certificate(
                    payload,
                    implementation_commit="b" * 40,
                    finished_at_UTC=certificate["finished_at_UTC"],
                    expires_at_UTC=certificate["expires_at_UTC"],
                    now_UTC=datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc),
                ),
            ),
            (
                "thread_environment",
                lambda: _pre_marker_machine_recheck(
                    repo_root,
                    environ={name: ("2" if index == 0 else "1") for index, name in enumerate(THREAD_ENVIRONMENT)},
                    rss_reader=lambda: 1,
                ),
            ),
            (
                "RSS_boundary",
                lambda: _pre_marker_machine_recheck(
                    repo_root,
                    environ={name: "1" for name in THREAD_ENVIRONMENT},
                    rss_reader=lambda: MAX_PEAK_RSS_BYTES,
                ),
            ),
        ]
    )

    def registered_file_case(kind: str) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            relative = Path("fixture/registered.json")
            fixture_payload = b'{"value":1}\n'
            _write_generated_fixture_file(root, relative, fixture_payload, 0o600)
            path = root / relative
            identity = RegisteredFileIdentity(
                relative,
                0o600,
                len(fixture_payload),
                _sha256_bytes(fixture_payload),
            )
            if kind == "mode":
                path.chmod(0o644)
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[5])
                return
            if kind == "size":
                path.write_bytes(fixture_payload + b"x")
                path.chmod(0o600)
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[5])
                return
            if kind == "symlink":
                target = root / "fixture/target.json"
                target.write_bytes(fixture_payload)
                target.chmod(0o600)
                path.unlink()
                path.symlink_to(target)
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[5])
                return
            snapshot = _preflight_registered_file(
                root, identity, REFUSAL_ROUTES[5]
            )
            if kind == "hash":
                wrong = RegisteredFileIdentity(
                    relative, 0o600, len(fixture_payload), "0" * 64
                )
                _read_exact_nofollow(
                    root, wrong, snapshot, REFUSAL_ROUTES[6]
                )
                return
            if kind == "race":
                replacement = root / "fixture/replacement.json"
                replacement.write_bytes(fixture_payload)
                replacement.chmod(0o600)
                os.replace(replacement, path)
                _read_exact_nofollow(
                    root, identity, snapshot, REFUSAL_ROUTES[6]
                )
                return
            raise ValueError("unknown generated registered-file case")

    def output_root_case(kind: str) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            parent = root / OUTPUT_ROOT_RELATIVE_PATH.parent
            parent.mkdir(parents=True)
            output = root / OUTPUT_ROOT_RELATIVE_PATH
            if kind == "exists":
                output.mkdir()
            elif kind == "symlink":
                target = root / "target"
                target.mkdir()
                output.symlink_to(target, target_is_directory=True)
            else:
                raise ValueError("unknown generated output-root case")
            _create_new_output_root(root)

    def readiness_refusal(kind: str) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            base = datetime(2026, 8, 16, 13, 0, tzinfo=timezone.utc)
            samples = _generated_raw_samples(base)
            for sample in samples:
                if kind == "load":
                    sample["one_minute_load"] = 8.0
                    sample["normalized_one_minute_load"] = 2.0
                elif kind == "disk":
                    sample["free_disk_bytes"] = MINIMUM_FREE_DISK_BYTES - 1
                else:
                    raise ValueError("unknown generated readiness case")
            samples[-1]["observed_at_UTC"] = _format_utc(
                base + timedelta(seconds=605)
            )
            samples[-1]["monotonic_seconds"] = 705.0
            iterator = iter(samples)
            _run_fresh_readiness(
                root,
                implementation_commit="a" * 40,
                sampler=lambda _root, _sequence: next(iterator),
                sleeper=lambda _seconds: None,
                environ={name: "1" for name in THREAD_ENVIRONMENT},
            )

    mutations.extend(
        [
            ("registered_file_mode", lambda: registered_file_case("mode")),
            ("registered_file_size", lambda: registered_file_case("size")),
            ("registered_file_symlink", lambda: registered_file_case("symlink")),
            ("registered_file_hash", lambda: registered_file_case("hash")),
            ("registered_file_race", lambda: registered_file_case("race")),
            ("output_root_exists", lambda: output_root_case("exists")),
            ("output_root_symlink", lambda: output_root_case("symlink")),
            (
                "source_duplicate_key",
                lambda: _strict_json(
                    b'{"value":1,"value":2}\n', route=REFUSAL_ROUTES[7]
                ),
            ),
            (
                "source_nonobject",
                lambda: _strict_json(b"[]\n", route=REFUSAL_ROUTES[7]),
            ),
            ("readiness_load", lambda: readiness_refusal("load")),
            ("readiness_disk", lambda: readiness_refusal("disk")),
        ]
    )
    base_report = {
        "schema_name": "neurodecodekit.marc2_machine_stable_private_recovery_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_target_free_structural_cohort_freeze",
        "route": SUCCESS_ROUTE,
        "proof_posture": "generated_fixture_only_no_scientific_value",
        "implementation_proof": {},
        "source_summary": {},
        "cohort_summary": {},
        "selection_hashes": {},
        "measurements": {
            "runtime_seconds": 0.1,
            "peak_RSS_bytes": 1,
            "combined_output_bytes": 1,
        },
        "operation_counters": {},
        "forbidden_counters": copy.deepcopy(ZERO_FORBIDDEN_COUNTERS),
        "warnings": [],
        "unavailable_fields": [],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    for name, key, value in (
        ("aggregate_subject_leak", "subject_id", "sub-01"),
        ("aggregate_member_leak", "member_name", "Freewill_generated/a"),
        ("aggregate_path_leak", "local_path", ".codex_work/private"),
    ):
        changed = copy.deepcopy(base_report)
        changed["source_summary"][key] = value
        mutations.append(
            (name, lambda item=changed: validate_aggregate_report(item))
        )
    changed = copy.deepcopy(base_report)
    changed["forbidden_counters"]["signal_sample_reads"] = 1
    mutations.append(
        ("aggregate_counter", lambda item=changed: validate_aggregate_report(item))
    )
    changed = copy.deepcopy(base_report)
    changed["claim_boundary"]["scientific_claim_not_established"] = "effect proven"
    mutations.append(
        ("aggregate_claim", lambda item=changed: validate_aggregate_report(item))
    )
    changed = copy.deepcopy(base_report)
    changed["measurements"]["combined_output_bytes"] = MAX_COMBINED_OUTPUT_BYTES + 1
    mutations.append(
        ("aggregate_output_cap", lambda item=changed: validate_aggregate_report(item))
    )
    changed = copy.deepcopy(base_report)
    changed["measurements"]["runtime_seconds"] = MAX_RUNTIME_SECONDS + 1
    mutations.append(
        ("aggregate_runtime_cap", lambda item=changed: validate_aggregate_report(item))
    )
    changed = copy.deepcopy(base_report)
    changed["measurements"]["peak_RSS_bytes"] = MAX_PEAK_RSS_BYTES
    mutations.append(
        ("aggregate_RSS_cap", lambda item=changed: validate_aggregate_report(item))
    )
    return {name: _expect_refusal(name, callback) for name, callback in mutations}


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run two generated replays and the direct refusal matrix."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    started = clock()
    load_implementation_registry(root)
    first = _run_generated_fixture(root)
    second = _run_generated_fixture(root)
    if (
        first.aggregate_bytes != second.aggregate_bytes
        or first.private_manifest_bytes != second.private_manifest_bytes
        or first.marker_bytes != second.marker_bytes
        or first.certificate_bytes != second.certificate_bytes
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[9], "generated replay differs"
        )
    mutations = _generated_mutations(root)
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    generated_input_bytes = first.expired_input_bytes + first.source_input_bytes
    generated_output_bytes = (
        len(first.certificate_bytes)
        + len(first.aggregate_bytes)
        + len(first.private_manifest_bytes)
        + len(first.marker_bytes)
    )
    report = {
        "schema_name": "neurodecodekit.marc2_machine_stable_private_recovery_qualification",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_generated_mock_only",
        "route": SUCCESS_ROUTE,
        "proof_posture": "generated_fixture_only_no_scientific_value",
        "replay": {
            "runs": 2,
            "aggregate_byte_identical": True,
            "private_manifest_byte_identical": True,
            "marker_byte_identical": True,
            "fresh_certificate_byte_identical": True,
        },
        "mutation_summary": {
            "count": len(mutations),
            "ordered_names": list(mutations),
            "routes": mutations,
        },
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes": generated_output_bytes,
            "retained_output_bytes": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "real_access_counters": {
            "expired_certificate_operations": 0,
            "private_source_operations": 0,
            "private_output_root_operations": 0,
            "archive_member_or_payload_reads": 0,
            "signal_event_target_or_label_reads": 0,
            "training_model_prediction_or_score_operations": 0,
            "network_or_provider_operations": 0,
            "hardware_operations": 0,
            "operations_on_other_projects": 0,
            "scientific_claim_upgrades": 0,
        },
        "acceptance_gates": {
            "decision_and_implementation_registry_valid": True,
            "shared_proof_validator_exercised": True,
            "exact_cleanup_state_machine_exercised_on_generated_fixture": True,
            "fresh_readiness_bound_to_supplied_proof_commit": True,
            "marker_immediately_before_one_generated_source_open": True,
            "VR2_adapter_called_once_per_generated_run": True,
            "cohort_invariants_replayed": True,
            "aggregate_privacy_firewall_passed": True,
            "all_mutations_refused": True,
            "deterministic_replay_passed": True,
            "runtime_RSS_input_output_and_retention_caps_passed": True,
            "real_private_archive_neural_target_model_score_counters_zero": True,
        },
        "warnings": [
            "Generated structural fixtures have no scientific value.",
            "The real expired certificate and retained manifest were not inspected.",
        ],
        "unavailable_fields": [
            "real_cohort_identity",
            "archive_payload",
            "neural_signal",
            "target",
            "prediction",
            "score",
        ],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    report_bytes = _canonical_json_bytes(report)
    if (
        runtime_seconds > 30.0
        or peak_rss_bytes >= MAX_PEAK_RSS_BYTES
        or generated_input_bytes > MAX_COMBINED_OUTPUT_BYTES
        or len(report_bytes) > MAX_COMBINED_OUTPUT_BYTES
        or any(value != 0 for value in report["real_access_counters"].values())
        or not all(report["acceptance_gates"].values())
    ):
        raise MachineStableRecoveryRefusal(
            REFUSAL_ROUTES[9], "generated qualification cap or gate refused"
        )
    return report


def build_plan_summary() -> dict[str, Any]:
    """Return the fixed command surface without touching a private path."""

    return {
        "schema_name": "neurodecodekit.marc2_machine_stable_private_recovery_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "commands": ["plan", "qualify", "inspect", "execute"],
        "fixed_paths": {
            "expired_certificate": EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix(),
            "private_source": PRIVATE_SOURCE_RELATIVE_PATH.as_posix(),
            "new_output_root": OUTPUT_ROOT_RELATIVE_PATH.as_posix(),
        },
        "proof_order": [
            "decision_remote_green",
            "exact_executor_remote_green",
            "expired_certificate_cleanup",
            "fresh_readiness",
            "marker_then_one_structural_open",
        ],
        "generic_path_or_root_override": False,
        "network_or_archive_payload_bytes": 0,
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }


def build_inspection_summary() -> dict[str, Any]:
    """Return implementation metadata without inspecting ignored paths."""

    registry = load_implementation_registry()
    return {
        "schema_name": "neurodecodekit.marc2_machine_stable_private_recovery_inspection",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": registry["status"],
        "generated_qualification": registry["generated_qualification"],
        "real_execution_consumed": registry["real_execution_state"][
            "registered_real_execution_consumed"
        ],
        "private_path_or_certificate_inspected": False,
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("proof identifier must be positive")
    return parsed


def _commit(value: str) -> str:
    if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise argparse.ArgumentTypeError("implementation commit must be 40 lowercase hex characters")
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_machine_stable_private_recovery"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="show the fixed registered sequence")
    commands.add_parser("qualify", help="run generated/mock qualification only")
    commands.add_parser("inspect", help="inspect committed implementation metadata")
    execute = commands.add_parser("execute", help="run the one fixed-path structural pass")
    execute.add_argument("--implementation-commit", required=True, type=_commit)
    execute.add_argument("--ci-run-id", required=True, type=_positive_int)
    execute.add_argument("--base-job-id", required=True, type=_positive_int)
    execute.add_argument("--optional-job-id", required=True, type=_positive_int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "plan":
            value = build_plan_summary()
        elif arguments.command == "qualify":
            value = qualify_generated()
        elif arguments.command == "inspect":
            value = build_inspection_summary()
        else:
            outcome = execute_registered(
                implementation_commit=arguments.implementation_commit,
                CI_run_id=arguments.ci_run_id,
                base_job_id=arguments.base_job_id,
                optional_job_id=arguments.optional_job_id,
            )
            value = outcome.aggregate_report
    except MachineStableRecoveryRefusal as exc:
        print(
            json.dumps(
                {
                    "lane_id": LANE_ID,
                    "status": "refused",
                    "route": exc.route,
                    "reason": exc.safe_reason,
                    "retry_rerun_resume_limit": 0,
                },
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
