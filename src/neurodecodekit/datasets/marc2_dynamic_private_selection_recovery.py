"""Proof-gated dynamic private structural selection for MARC2-VR7P."""

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
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_dynamic_live_selection as dynamic
from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import marc2_machine_readiness as readiness
from neurodecodekit.datasets import marc2_proof_record_recovery as proof_recovery


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR7P"
MODULE_NAME = (
    "neurodecodekit.datasets.marc2_dynamic_private_selection_recovery"
)
SUCCESS_ROUTE = "MARC2VR7P-R1"
REFUSAL_ROUTES = tuple(f"MARC2VR7P-F{index:02d}" for index in range(1, 11))

DECISION_COMMIT = "a318521cf9adb057617e839ead0003d89c3cab84"
DECISION_CI_RUN_ID = 31_979_669_507
DECISION_BASE_JOB_ID = 95_244_335_512
DECISION_OPTIONAL_JOB_ID = 95_244_335_508
DECISION_DOCUMENT_RELATIVE_PATH = Path(
    "docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_AUTHORIZATION_DECISION.md"
)
DECISION_DOCUMENT_SHA256 = (
    "851e23bebf97bc0fd4cabe433e6a97f92155e6135114c753176b45fd4e6ca9d7"
)
DECISION_REGISTRY_RELATIVE_PATH = Path(
    "registries/"
    "marc2_dynamic_private_selection_recovery_authorization_decision.v0.json"
)
DECISION_REGISTRY_SHA256 = (
    "9a281224237bb09d96480070fb08a9632206a31c83238885ece2e59974894bb5"
)
DECISION_TEST_RELATIVE_PATH = Path(
    "tests/test_marc2_dynamic_private_selection_recovery_authorization_decision.py"
)
DECISION_TEST_SHA256 = (
    "e724fb95425d45d9148d7949e35600ebce1bbe6c433f422cfb78841da42ab70d"
)
REQUEST_REGISTRY_RELATIVE_PATH = Path(
    "registries/"
    "marc2_dynamic_private_selection_recovery_authorization_request.v0.json"
)
REQUEST_REGISTRY_SHA256 = (
    "76fba4a69728436c900b74a5177a8d76215b4924e8354b8e916224489f572873"
)
IMPLEMENTATION_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_dynamic_private_selection_recovery_implementation.v0.json"
)
PROOF_RECORD_RELATIVE_PATH = Path(
    "registries/marc2_dynamic_private_selection_recovery_proof.v0.json"
)

READINESS_CERTIFICATE_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr7p/readiness.v0.json"
)
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_dynamic_private_selection_recovery/v0"
)
MARKER_NAME = "consumed_marker.v0.json"
PRIVATE_MANIFEST_NAME = "cohort_selection.private.v0.json"
AGGREGATE_REPORT_NAME = "cohort_selection.aggregate.v0.json"

PRIVATE_SOURCE_BYTES = 418_755
PRIVATE_SOURCE_SHA256 = (
    "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
)
EXPECTED_SOURCE_ROWS = 1_227
EXPECTED_SOURCE_FILES = 1_025
EXPECTED_SOURCE_DIRECTORIES = 202
EXPECTED_SOURCE_BUNDLES = 238
EXPECTED_ELIGIBLE_BUNDLES = 195
EXPECTED_INELIGIBLE_BUNDLES = 43

THREAD_ENVIRONMENT = readiness.THREAD_ENVIRONMENT
MAX_GENERATED_RUNTIME_SECONDS = 30.0
MAX_REAL_RUNTIME_SECONDS = 650.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_COMBINED_OUTPUT_BYTES = 4 * 1024**2
MAX_TRACKED_ARTIFACT_BYTES = 2 * 1024**2
MAX_PROOF_BYTES = 1024**2
READ_CHUNK_BYTES = 64 * 1024
READINESS_SCHEMA_NAME = (
    "neurodecodekit.marc2_dynamic_private_selection_recovery_readiness"
)
RESULT_SCHEMA_NAME = (
    "neurodecodekit.marc2_dynamic_private_selection_recovery_result"
)

FIXED_GREEN_ARTIFACTS = (
    (DECISION_DOCUMENT_RELATIVE_PATH, DECISION_DOCUMENT_SHA256),
    (DECISION_REGISTRY_RELATIVE_PATH, DECISION_REGISTRY_SHA256),
    (DECISION_TEST_RELATIVE_PATH, DECISION_TEST_SHA256),
    (REQUEST_REGISTRY_RELATIVE_PATH, REQUEST_REGISTRY_SHA256),
    (
        Path("registries/marc2_dynamic_live_selection_contract.v0.json"),
        dynamic.CONTRACT_SHA256,
    ),
    (
        Path("src/neurodecodekit/datasets/marc2_dynamic_live_selection.py"),
        "c3b0d056891f7708b87e8027d36ebd14830055cdeac8e652a681dd4592b4a104",
    ),
    (
        Path("registries/marc2_dynamic_live_selection_implementation.v0.json"),
        "0a08caa40d3bb46f6bea1ef8c32b6451d8066dab40935274b7ab1692dee78fdc",
    ),
    (
        Path("registries/marc2_dynamic_live_selection_result.v0.json"),
        "012af5ae838a00cdcefb49c02bcddfb2b454766d164613a87020bfacb1dc5e43",
    ),
    (
        Path("src/neurodecodekit/datasets/marc2_machine_readiness.py"),
        "7773b070dc0b819d7a680789fe6d998293ed17c94776af703034576e773dafa0",
    ),
    (
        Path("registries/marc2_machine_stable_structural_recovery_contract.v0.json"),
        readiness.CONTRACT_SHA256,
    ),
    (
        proof_recovery.MODULE_RELATIVE_PATH,
        "c22948ca9047f07908d3768a17caea56b96fa8219ccf0bb9895d766373903a2c",
    ),
    (
        proof_recovery.IMPLEMENTATION_REGISTRY_RELATIVE_PATH,
        "2b1ff6c9d41d7bae14686cbf16a2aa129d702842622ca990468a3263f68e66b6",
    ),
)

ZERO_FORBIDDEN_COUNTERS = {
    "network_requests": 0,
    "network_bytes": 0,
    "archive_member_or_payload_reads": 0,
    "signal_sample_reads": 0,
    "event_onset_channel_geometry_target_label_or_quality_reads": 0,
    "real_derivative_rows": 0,
    "training_or_parameter_update_fits": 0,
    "model_inference_or_prediction_sets": 0,
    "prediction_freezes_target_deliveries_or_scores": 0,
    "provider_or_language_model_calls": 0,
    "stream_device_or_hardware_operations": 0,
    "other_project_or_consumed_root_operations": 0,
    "release_publication_or_scientific_claim_upgrades": 0,
}
CLAIM_BOUNDARY = {
    "engineering_capability_added": (
        "A proof-gated machine-stable wrapper can freeze a dynamically measured "
        "real target-free structural cohort without opening an archive member."
    ),
    "scientific_claim_not_established": (
        "No archive neural payload target prediction or score is accessed, so "
        "this structural result establishes no neural effect decoding "
        "performance language decoding live decoding or thought-to-text capability."
    ),
}


class DynamicPrivateSelectionRecoveryRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR7P route."""

    def __init__(
        self,
        route: str,
        reason: str,
        *,
        upstream_route: str | None = None,
    ) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR7P refusal route")
        if upstream_route is not None and upstream_route not in dynamic.REFUSAL_ROUTES:
            raise ValueError("unknown allowlisted VR6 route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason
        self.upstream_route = upstream_route


@dataclass(frozen=True, slots=True)
class RegisteredFileIdentity:
    """One exact no-follow regular-file identity."""

    relative_path: Path
    mode: int
    bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    """Race-sensitive metadata captured before content open."""

    device: int
    inode: int
    mode: int
    size: int
    owner: int


@dataclass(frozen=True, slots=True)
class ExecutionProof:
    """Exact remote-green proof supplied to the fixed executor."""

    implementation_commit: str
    CI_run_id: int
    base_job_id: int
    optional_job_id: int
    proof_record_sha256: str
    proof_summary: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class SequenceOutcome:
    """One generated or real structural sequence."""

    aggregate_report: Mapping[str, Any]
    aggregate_bytes: bytes
    private_manifest_bytes: bytes
    marker_bytes: bytes
    certificate_bytes: bytes
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
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[7], "output JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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
        raise DynamicPrivateSelectionRecoveryRefusal(route, "JSON encoding differs")
    try:
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "strict JSON parse refused"
        ) from exc
    if not isinstance(value, dict):
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "JSON root is not an object"
        )
    return value


def _read_small_regular(path: Path, maximum_bytes: int, route: str) -> bytes:
    try:
        before = path.lstat()
    except OSError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "tracked artifact unavailable"
        ) from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "tracked artifact type differs"
        )
    if before.st_size > maximum_bytes:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "tracked artifact cap exceeded"
        )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    payload = bytearray()
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or opened.st_size != before.st_size
            ):
                raise DynamicPrivateSelectionRecoveryRefusal(
                    route, "tracked artifact identity changed"
                )
            while len(payload) <= maximum_bytes:
                chunk = os.read(
                    descriptor,
                    min(READ_CHUNK_BYTES, maximum_bytes + 1 - len(payload)),
                )
                if not chunk:
                    break
                payload.extend(chunk)
        finally:
            os.close(descriptor)
    except DynamicPrivateSelectionRecoveryRefusal:
        raise
    except OSError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "tracked artifact read refused"
        ) from exc
    if len(payload) != before.st_size or len(payload) > maximum_bytes:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "tracked artifact size changed"
        )
    return bytes(payload)


def _load_exact_json(
    root: Path,
    relative_path: Path,
    expected_sha256: str,
    *,
    maximum_bytes: int = MAX_TRACKED_ARTIFACT_BYTES,
) -> dict[str, Any]:
    payload = _read_small_regular(
        root / relative_path, maximum_bytes, REFUSAL_ROUTES[0]
    )
    if _sha256_bytes(payload) != expected_sha256:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact hash differs"
        )
    return _strict_json(payload, route=REFUSAL_ROUTES[0])


def _verify_green_inputs(root: Path) -> tuple[int, int]:
    total = 0
    for relative, expected_sha256 in FIXED_GREEN_ARTIFACTS:
        payload = _read_small_regular(
            root / relative, MAX_TRACKED_ARTIFACT_BYTES, REFUSAL_ROUTES[0]
        )
        if _sha256_bytes(payload) != expected_sha256:
            raise DynamicPrivateSelectionRecoveryRefusal(
                REFUSAL_ROUTES[0], "green artifact identity differs"
            )
        total += len(payload)
    decision = _load_exact_json(root, DECISION_REGISTRY_RELATIVE_PATH, DECISION_REGISTRY_SHA256)
    authorization = decision.get("authorization", {})
    if (
        decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "ecaa2aba82726b6c428facf917868b78e0340969"
        or decision.get("user_authorization", {}).get("actual_message_verbatim")
        != "continue"
        or decision.get("user_authorization", {}).get("actual_message_SHA256")
        != "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad"
        or decision.get("green_proof_closeout", {}).get("both_required_jobs_green")
        is not True
        or authorization.get("generated_mock_wrapper_implementation_after_decision_green")
        is not True
        or authorization.get("one_private_structural_manifest_read_after_wrapper_green")
        is not True
        or authorization.get("MARC2_FW2_or_CIL1_real_execution_authorized_now")
        is not False
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[0], "green decision semantics differ"
        )
    return len(FIXED_GREEN_ARTIFACTS), total


def load_implementation_registry(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load the exact generated qualification registry."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    payload = _read_small_regular(
        root / IMPLEMENTATION_REGISTRY_RELATIVE_PATH,
        MAX_TRACKED_ARTIFACT_BYTES,
        REFUSAL_ROUTES[0],
    )
    registry = _strict_json(payload, route=REFUSAL_ROUTES[0])
    proof = registry.get("green_authorization_decision", {})
    surface = registry.get("implementation_surface", {})
    state = registry.get("real_execution_state", {})
    if (
        registry.get("schema_name")
        != "neurodecodekit.marc2_dynamic_private_selection_recovery_implementation"
        or registry.get("schema_version") != SCHEMA_VERSION
        or registry.get("lane_id") != LANE_ID
        or registry.get("status")
        != "generated_mock_implementation_complete_real_sequence_not_executed"
        or proof.get("commit") != DECISION_COMMIT
        or proof.get("CI_run_id") != DECISION_CI_RUN_ID
        or proof.get("base_python_job_id") != DECISION_BASE_JOB_ID
        or proof.get("optional_neuro_job_id") != DECISION_OPTIONAL_JOB_ID
        or proof.get("both_required_jobs_green_before_implementation") is not True
        or surface.get("module") != MODULE_NAME
        or surface.get("commands") != ["plan", "qualify", "inspect", "execute"]
        or surface.get("generic_path_URL_retry_resume_or_fallback_argument") is not False
        or surface.get("consumed_executor_import_call_patch_or_reuse") is not False
        or state.get("registered_real_execution_limit") != 1
        or state.get("registered_real_execution_consumed") is not False
        or state.get("retry_rerun_resume_repair_or_fallback_limit") != 0
        or any(registry.get("implementation_access_counters", {}).values())
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
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
        raise DynamicPrivateSelectionRecoveryRefusal(
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
    """Bind one clean HEAD to the committed shared proof record."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_implementation_registry(root)
    proof_bytes = _read_small_regular(
        root / PROOF_RECORD_RELATIVE_PATH, MAX_PROOF_BYTES, REFUSAL_ROUTES[0]
    )
    proof_sha256 = _sha256_bytes(proof_bytes)
    head = _git_output(root, ["rev-parse", "HEAD"])
    status = _git_output(root, ["status", "--porcelain", "--untracked-files=no"])
    if head != implementation_commit or status:
        raise DynamicPrivateSelectionRecoveryRefusal(
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
        raise DynamicPrivateSelectionRecoveryRefusal(
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
        raise DynamicPrivateSelectionRecoveryRefusal(
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


def _absolute_directory(root: Path, route: str) -> Path:
    absolute = root.absolute()
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current = current / component
        try:
            info = current.lstat()
        except OSError as exc:
            raise DynamicPrivateSelectionRecoveryRefusal(
                route, "root path unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise DynamicPrivateSelectionRecoveryRefusal(
                route, "root path component differs"
            )
    return absolute


def _validate_parent_chain(root: Path, relative: Path, route: str) -> None:
    current = _absolute_directory(root, route)
    for component in relative.parts[:-1]:
        current = current / component
        try:
            info = current.lstat()
        except OSError as exc:
            raise DynamicPrivateSelectionRecoveryRefusal(
                route, "registered parent unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise DynamicPrivateSelectionRecoveryRefusal(
                route, "registered parent type differs"
            )


def _preflight_registered_file(
    root: Path,
    identity: RegisteredFileIdentity,
    route: str,
    *,
    owner_reader: Callable[[], int] = os.getuid,
) -> FileSnapshot:
    _validate_parent_chain(root, identity.relative_path, route)
    path = root / identity.relative_path
    try:
        info = path.lstat()
    except OSError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "registered file unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "registered file type differs"
        )
    if stat.S_IMODE(info.st_mode) != identity.mode:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "registered file mode differs"
        )
    if info.st_uid != owner_reader():
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "registered file owner differs"
        )
    if info.st_size != identity.bytes:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "registered file size differs"
        )
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
                raise DynamicPrivateSelectionRecoveryRefusal(
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
                raise DynamicPrivateSelectionRecoveryRefusal(
                    route, "registered file exceeds exact size"
                )
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except DynamicPrivateSelectionRecoveryRefusal:
        raise
    except OSError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "registered file content open refused"
        ) from exc
    if (
        len(payload) != identity.bytes
        or after.st_dev != snapshot.device
        or after.st_ino != snapshot.inode
        or after.st_size != snapshot.size
        or _sha256_bytes(payload) != identity.sha256
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "registered file content identity differs"
        )
    return bytes(payload)


def _ensure_parent_tree(root: Path, relative: Path, route: str) -> None:
    current = _absolute_directory(root, route)
    for component in relative.parts:
        current = current / component
        if current.exists() or current.is_symlink():
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise DynamicPrivateSelectionRecoveryRefusal(
                    route, "new parent tree differs"
                )
        else:
            try:
                current.mkdir(mode=0o700)
            except OSError as exc:
                raise DynamicPrivateSelectionRecoveryRefusal(
                    route, "new parent creation refused"
                ) from exc


def _write_exclusive(
    path: Path,
    payload: bytes,
    *,
    mode: int,
    route: str,
) -> None:
    if path.exists() or path.is_symlink():
        raise DynamicPrivateSelectionRecoveryRefusal(route, "output overwrite refused")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "exclusive output write refused"
        ) from exc
    info = path.lstat()
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != mode
        or info.st_size != len(payload)
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "written output shape differs"
        )


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


def _parse_utc(value: Any, route: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise DynamicPrivateSelectionRecoveryRefusal(route, "UTC value differs")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            route, "UTC value differs"
        ) from exc
    if parsed.tzinfo != timezone.utc:
        raise DynamicPrivateSelectionRecoveryRefusal(route, "UTC offset differs")
    return parsed


def _thread_values(environ: Mapping[str, str]) -> dict[str, str | None]:
    return {name: environ.get(name) for name in THREAD_ENVIRONMENT}


def _assess_samples(raw_samples: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    try:
        samples = [readiness._assess_raw_sample(row) for row in raw_samples]
        readiness._validate_sample_sequence(samples)
    except readiness.MachineReadinessRefusal as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "machine sample sequence refused"
        ) from exc
    return samples


def _build_readiness_certificate(
    raw_samples: Sequence[Mapping[str, Any]],
    *,
    implementation_commit: str,
    thread_environment: Mapping[str, str | None],
    certificate_path: str,
    proof_posture: str,
) -> dict[str, Any]:
    samples = _assess_samples(raw_samples)
    started = _parse_utc(samples[0]["observed_at_UTC"], REFUSAL_ROUTES[1])
    finished = _parse_utc(samples[-1]["observed_at_UTC"], REFUSAL_ROUTES[1])
    wait_seconds = float(samples[-1]["monotonic_seconds"]) - float(
        samples[0]["monotonic_seconds"]
    )
    tail = readiness._passing_tail(samples)
    threads_ok = thread_environment == {name: "1" for name in THREAD_ENVIRONMENT}
    ready = threads_ok and tail >= readiness.CONSECUTIVE_PASSING_SAMPLES
    certificate = {
        "schema_name": READINESS_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "ready" if ready else "not_ready",
        "ready": ready,
        "proof_posture": proof_posture,
        "certificate_path": certificate_path,
        "implementation_commit": implementation_commit,
        "machine_contract_sha256": readiness.CONTRACT_SHA256,
        "started_at_UTC": _format_utc(started),
        "finished_at_UTC": _format_utc(finished),
        "expires_at_UTC": _format_utc(
            finished + timedelta(seconds=readiness.CERTIFICATE_VALIDITY_SECONDS)
        ),
        "thresholds": copy.deepcopy(readiness.THRESHOLDS),
        "samples": samples,
        "measurements": {
            "sample_count": len(samples),
            "consecutive_passing_tail": tail,
            "wait_seconds": wait_seconds,
            "thread_environment": dict(thread_environment),
        },
        "access_counters": {
            "machine_readiness_checks": len(samples),
            "readiness_certificates": 1,
            **copy.deepcopy(readiness.ZERO_SCIENTIFIC_COUNTERS),
        },
        "claim_boundary": copy.deepcopy(readiness.CLAIM_BOUNDARY),
    }
    _validate_readiness_certificate(certificate, allow_not_ready=True)
    if len(_canonical_json_bytes(certificate)) > readiness.MAX_CERTIFICATE_BYTES:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness certificate cap exceeded"
        )
    return certificate


def _validate_readiness_certificate(
    certificate: Mapping[str, Any],
    *,
    allow_not_ready: bool = False,
    now_UTC: datetime | None = None,
) -> None:
    required = {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "ready",
        "proof_posture",
        "certificate_path",
        "implementation_commit",
        "machine_contract_sha256",
        "started_at_UTC",
        "finished_at_UTC",
        "expires_at_UTC",
        "thresholds",
        "samples",
        "measurements",
        "access_counters",
        "claim_boundary",
    }
    if set(certificate) != required:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness certificate fields differ"
        )
    commit = certificate.get("implementation_commit")
    posture = certificate.get("proof_posture")
    expected_path = (
        "<generated-fixture>"
        if posture == "generated_only_non_authoritative"
        else READINESS_CERTIFICATE_RELATIVE_PATH.as_posix()
    )
    if (
        certificate.get("schema_name") != READINESS_SCHEMA_NAME
        or certificate.get("schema_version") != SCHEMA_VERSION
        or certificate.get("lane_id") != LANE_ID
        or not isinstance(commit, str)
        or len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
        or posture not in {
            "generated_only_non_authoritative",
            "machine_only_non_scientific",
        }
        or certificate.get("certificate_path") != expected_path
        or certificate.get("machine_contract_sha256") != readiness.CONTRACT_SHA256
        or certificate.get("thresholds") != readiness.THRESHOLDS
        or certificate.get("claim_boundary") != readiness.CLAIM_BOUNDARY
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness certificate identity differs"
        )
    samples_raw = certificate.get("samples")
    if not isinstance(samples_raw, list):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness samples differ"
        )
    raw_keys = {
        "sequence",
        "observed_at_UTC",
        "monotonic_seconds",
        "logical_CPUs",
        "one_minute_load",
        "normalized_one_minute_load",
        "process_peak_RSS_bytes",
        "free_disk_bytes",
    }
    raw_samples = [
        {key: sample[key] for key in raw_keys}
        for sample in samples_raw
        if isinstance(sample, Mapping) and raw_keys.issubset(sample)
    ]
    if len(raw_samples) != len(samples_raw):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness sample shape differs"
        )
    samples = _assess_samples(raw_samples)
    if samples != samples_raw:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness sample values differ"
        )
    measurements = certificate.get("measurements")
    thread_values = (
        measurements.get("thread_environment")
        if isinstance(measurements, Mapping)
        else None
    )
    tail = readiness._passing_tail(samples)
    ready = (
        thread_values == {name: "1" for name in THREAD_ENVIRONMENT}
        and tail >= readiness.CONSECUTIVE_PASSING_SAMPLES
    )
    wait = float(samples[-1]["monotonic_seconds"]) - float(
        samples[0]["monotonic_seconds"]
    )
    started = _parse_utc(samples[0]["observed_at_UTC"], REFUSAL_ROUTES[1])
    finished = _parse_utc(samples[-1]["observed_at_UTC"], REFUSAL_ROUTES[1])
    expires = _parse_utc(certificate.get("expires_at_UTC"), REFUSAL_ROUTES[1])
    expected_counters = {
        "machine_readiness_checks": len(samples),
        "readiness_certificates": 1,
        **readiness.ZERO_SCIENTIFIC_COUNTERS,
    }
    if (
        not isinstance(measurements, Mapping)
        or measurements.get("sample_count") != len(samples)
        or measurements.get("consecutive_passing_tail") != tail
        or measurements.get("wait_seconds") != wait
        or certificate.get("started_at_UTC") != _format_utc(started)
        or certificate.get("finished_at_UTC") != _format_utc(finished)
        or expires != finished + timedelta(seconds=readiness.CERTIFICATE_VALIDITY_SECONDS)
        or certificate.get("ready") is not ready
        or certificate.get("status") != ("ready" if ready else "not_ready")
        or certificate.get("access_counters") != expected_counters
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness certificate measurements differ"
        )
    if not ready and not allow_not_ready:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "machine did not reach three passing samples"
        )
    if now_UTC is not None and now_UTC.astimezone(timezone.utc) > expires:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "readiness certificate expired"
        )


def _observe_machine(root: Path, sequence: int) -> dict[str, Any]:
    try:
        load = os.getloadavg()[0]
    except (AttributeError, OSError) as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "one-minute load unavailable"
        ) from exc
    logical_cpus = os.cpu_count()
    return {
        "sequence": sequence,
        "observed_at_UTC": _format_utc(datetime.now(timezone.utc)),
        "monotonic_seconds": time.monotonic(),
        "logical_CPUs": logical_cpus,
        "one_minute_load": load,
        "normalized_one_minute_load": (
            load / logical_cpus if logical_cpus else None
        ),
        "process_peak_RSS_bytes": _peak_rss_bytes(),
        "free_disk_bytes": shutil.disk_usage(root).free,
    }


def _write_readiness_certificate(
    root: Path, certificate: Mapping[str, Any]
) -> bytes:
    relative_parent = READINESS_CERTIFICATE_RELATIVE_PATH.parent
    destination_parent = root / relative_parent
    if destination_parent.exists() or destination_parent.is_symlink():
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "fresh readiness parent is not absent"
        )
    _ensure_parent_tree(root, relative_parent.parent, REFUSAL_ROUTES[1])
    try:
        destination_parent.mkdir(mode=0o700)
    except OSError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "fresh readiness parent creation refused"
        ) from exc
    payload = _canonical_json_bytes(certificate)
    if len(payload) > readiness.MAX_CERTIFICATE_BYTES:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "fresh readiness output cap exceeded"
        )
    _write_exclusive(
        root / READINESS_CERTIFICATE_RELATIVE_PATH,
        payload,
        mode=0o600,
        route=REFUSAL_ROUTES[1],
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
    raw_samples: list[Mapping[str, Any]] = []
    thread_values = _thread_values(environ)
    first_monotonic: float | None = None
    certificate: dict[str, Any] | None = None
    while len(raw_samples) < readiness.MAXIMUM_SAMPLES:
        sample = dict(sampler(root, len(raw_samples) + 1))
        raw_samples.append(sample)
        if first_monotonic is None:
            first_monotonic = float(sample["monotonic_seconds"])
        certificate = _build_readiness_certificate(
            raw_samples,
            implementation_commit=implementation_commit,
            thread_environment=thread_values,
            certificate_path=READINESS_CERTIFICATE_RELATIVE_PATH.as_posix(),
            proof_posture="machine_only_non_scientific",
        )
        if certificate["ready"]:
            break
        elapsed = float(sample["monotonic_seconds"]) - first_monotonic
        if (
            elapsed >= readiness.MAXIMUM_WAIT_SECONDS
            or thread_values != {name: "1" for name in THREAD_ENVIRONMENT}
        ):
            break
        sleeper(readiness.MINIMUM_SAMPLE_INTERVAL_SECONDS)
    if certificate is None or certificate.get("ready") is not True:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[1], "fresh readiness did not pass"
        )
    return certificate, _write_readiness_certificate(root, certificate)


def _pre_marker_machine_recheck(
    root: Path,
    *,
    environ: Mapping[str, str],
    rss_reader: Callable[[], int],
    disk_reader: Callable[[Path], int],
) -> dict[str, int | bool]:
    threads_ok = _thread_values(environ) == {
        name: "1" for name in THREAD_ENVIRONMENT
    }
    rss = rss_reader()
    free_disk = disk_reader(root)
    if (
        not threads_ok
        or isinstance(rss, bool)
        or not isinstance(rss, int)
        or rss < 0
        or rss >= MAX_PEAK_RSS_BYTES
        or isinstance(free_disk, bool)
        or not isinstance(free_disk, int)
        or free_disk < MINIMUM_FREE_DISK_BYTES
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[2], "pre-marker thread RSS or disk gate refused"
        )
    return {
        "thread_environment_all_one": threads_ok,
        "process_peak_RSS_bytes": rss,
        "free_disk_bytes": free_disk,
        "second_load_gate_performed": False,
    }


def _create_new_output_root(root: Path) -> Path:
    _ensure_parent_tree(root, OUTPUT_ROOT_RELATIVE_PATH.parent, REFUSAL_ROUTES[3])
    output_root = root / OUTPUT_ROOT_RELATIVE_PATH
    if output_root.exists() or output_root.is_symlink():
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[3], "registered output root is not absent"
        )
    try:
        output_root.mkdir(mode=0o700)
    except OSError as exc:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[3], "registered output root creation refused"
        ) from exc
    return output_root


def _contains_private_aggregate_value(value: Any) -> bool:
    forbidden_keys = {
        "subject_id",
        "selected_subject_ids",
        "participant_id",
        "member_name",
        "local_header_offset",
        "crc32",
        "private_manifest",
        "private_source_path",
        "private_output_path",
        "local_path",
        "rows",
    }
    if isinstance(value, Mapping):
        return any(
            str(key).lower() in forbidden_keys
            or _contains_private_aggregate_value(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_private_aggregate_value(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return (
            ".codex_work" in lowered
            or lowered.startswith("sub-")
            or "freewill_generated/" in lowered
            or "/users/" in lowered
        )
    return False


def validate_aggregate_report(report: Mapping[str, Any]) -> None:
    """Validate aggregate privacy, resources, counters, and claim ceiling."""

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
    measurements = report.get("measurements", {})
    if (
        set(report) != required
        or report.get("schema_name") != RESULT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
        or report.get("claim_boundary") != CLAIM_BOUNDARY
        or report.get("forbidden_counters") != ZERO_FORBIDDEN_COUNTERS
        or _contains_private_aggregate_value(report)
        or not isinstance(measurements, Mapping)
        or measurements.get("combined_output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1)
        > MAX_COMBINED_OUTPUT_BYTES
        or measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES)
        >= MAX_PEAK_RSS_BYTES
        or measurements.get("runtime_seconds", MAX_REAL_RUNTIME_SECONDS + 1)
        > MAX_REAL_RUNTIME_SECONDS
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[7], "aggregate privacy resource or claim boundary differs"
        )


def _operation_counters(
    *, real: bool, sample_count: int, source_input_bytes: int
) -> dict[str, int]:
    prefix = "real_" if real else "generated_fixture_"
    return {
        f"{prefix}fresh_machine_readiness_invocations": 1,
        f"{prefix}fresh_machine_readiness_samples": sample_count,
        f"{prefix}fresh_readiness_certificates": 1,
        f"{prefix}source_path_preflights": 1,
        f"{prefix}output_root_operations": 1,
        f"{prefix}consumed_markers": 1,
        f"{prefix}structural_content_opens": 1,
        f"{prefix}structural_input_bytes": source_input_bytes,
        f"{prefix}strict_JSON_parses": 1,
        f"{prefix}VR6_adapter_calls": 1,
        f"{prefix}cohort_freezes": 1,
    }


def _build_aggregate_report(
    *,
    proof: ExecutionProof,
    source_identity: RegisteredFileIdentity,
    selection: selector.SelectionResult,
    certificate: Mapping[str, Any],
    certificate_bytes: bytes,
    marker_bytes: bytes,
    private_bytes: bytes,
    runtime_seconds: float,
    peak_rss_bytes: int,
    real: bool,
) -> dict[str, Any]:
    selected_subjects = selection.cohort_summary["selected_subjects"]
    output_without_report = (
        len(certificate_bytes) + len(marker_bytes) + len(private_bytes)
    )
    report: dict[str, Any] = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_target_free_dynamic_structural_cohort_freeze",
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
            "structural_rows": EXPECTED_SOURCE_ROWS if real else None,
            "regular_entries": EXPECTED_SOURCE_FILES if real else None,
            "directory_entries": EXPECTED_SOURCE_DIRECTORIES if real else None,
            "complete_bundles": EXPECTED_SOURCE_BUNDLES,
            "eligible_bundles": EXPECTED_ELIGIBLE_BUNDLES,
            "valid_ineligible_bundles": EXPECTED_INELIGIBLE_BUNDLES,
            "content_opens": 1,
        },
        "cohort_summary": {
            "selected_subjects": selected_subjects,
            "selected_bundles": selection.split_summary["selected_run_bundles"],
            "selected_members": selection.split_summary["selected_core_members"],
            "selected_reservation_bytes": selection.byte_summary[
                "selected_reservation_bytes"
            ],
            "remaining_reservation_bytes": selection.byte_summary[
                "remaining_reservation_bytes"
            ],
            "reservation_cap_bytes": selector.RESERVATION_CAP_BYTES,
            "selected_bytes_are_reservation_metadata_only": True,
            "fit_heldout_overlap": selection.split_summary["fit_heldout_overlap"],
            "row_random_split_used": selection.split_summary[
                "row_random_split_used"
            ],
            "all_eligible_subjects_fit": selected_subjects == selector.MAXIMUM_SUBJECTS,
            "next_ranked_subject_does_not_fit": (
                selected_subjects < selector.MAXIMUM_SUBJECTS
            ),
            "archive_member_or_payload_bytes": 0,
        },
        "selection_hashes": dict(selection.selection_hashes),
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "fresh_readiness_samples": len(certificate["samples"]),
            "fresh_readiness_wait_seconds": certificate["measurements"][
                "wait_seconds"
            ],
            "fresh_readiness_certificate_bytes": len(certificate_bytes),
            "marker_bytes": len(marker_bytes),
            "private_manifest_bytes": len(private_bytes),
            "aggregate_report_bytes": 0,
            "combined_output_bytes": output_without_report,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "operation_counters": _operation_counters(
            real=real,
            sample_count=len(certificate["samples"]),
            source_input_bytes=source_identity.bytes,
        ),
        "forbidden_counters": copy.deepcopy(ZERO_FORBIDDEN_COUNTERS),
        "warnings": [
            "Selected bytes are reservation metadata, not downloaded payload bytes.",
            "No archive member neural value target prediction or score was read.",
            "A separate FW2 preregistration and Tier C decision remain required.",
        ],
        "unavailable_fields": [
            "archive_member_payload",
            "EEG_or_MEG_signal",
            "event_onset_channel_geometry_target_label_or_quality",
            "model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    for _ in range(8):
        report_bytes = _canonical_json_bytes(report)
        combined = output_without_report + len(report_bytes)
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
    source_identity: RegisteredFileIdentity,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
    sampler: Callable[[Path, int], Mapping[str, Any]],
    sleeper: Callable[[float], None],
    environ: Mapping[str, str],
    now_UTC: Callable[[], datetime],
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    disk_reader: Callable[[Path], int],
    real: bool,
) -> SequenceOutcome:
    started = clock()
    certificate, certificate_bytes = _run_fresh_readiness(
        root,
        implementation_commit=proof.implementation_commit,
        sampler=sampler,
        sleeper=sleeper,
        environ=environ,
    )
    _validate_readiness_certificate(certificate, now_UTC=now_UTC())
    _pre_marker_machine_recheck(
        root,
        environ=environ,
        rss_reader=rss_reader,
        disk_reader=disk_reader,
    )
    source_snapshot = _preflight_registered_file(
        root, source_identity, REFUSAL_ROUTES[2]
    )
    output_root = _create_new_output_root(root)
    marker = {
        "schema_name": (
            "neurodecodekit.marc2_dynamic_private_selection_recovery_marker"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_before_structural_content_open",
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
        route=REFUSAL_ROUTES[3],
    )
    source_payload = _read_exact_nofollow(
        root, source_identity, source_snapshot, REFUSAL_ROUTES[4]
    )
    source = _strict_json(source_payload, route=REFUSAL_ROUTES[5])
    source_before = _canonical_json_bytes(source)
    try:
        selection = dynamic.adapt_dynamic_live_source(
            source,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
    except dynamic.DynamicLiveSelectionRefusal as exc:
        upstream = exc.route if exc.route in dynamic.REFUSAL_ROUTES else None
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[6],
            "dynamic live selection refused",
            upstream_route=upstream,
        ) from None
    if _canonical_json_bytes(source) != source_before:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[6], "VR6 adapter mutated source"
        )
    private_bytes = _canonical_json_bytes(selection.private_manifest)
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    report = _build_aggregate_report(
        proof=proof,
        source_identity=source_identity,
        selection=selection,
        certificate=certificate,
        certificate_bytes=certificate_bytes,
        marker_bytes=marker_bytes,
        private_bytes=private_bytes,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        real=real,
    )
    aggregate_bytes = _canonical_json_bytes(report)
    combined = (
        len(certificate_bytes)
        + len(marker_bytes)
        + len(private_bytes)
        + len(aggregate_bytes)
    )
    maximum_runtime = MAX_REAL_RUNTIME_SECONDS if real else MAX_GENERATED_RUNTIME_SECONDS
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > maximum_runtime
        or peak_rss_bytes < 0
        or peak_rss_bytes >= MAX_PEAK_RSS_BYTES
        or combined > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
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
    expected = tuple(sorted((MARKER_NAME, PRIVATE_MANIFEST_NAME, AGGREGATE_REPORT_NAME)))
    if output_files != expected:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[8], "output inventory differs"
        )
    return SequenceOutcome(
        aggregate_report=report,
        aggregate_bytes=aggregate_bytes,
        private_manifest_bytes=private_bytes,
        marker_bytes=marker_bytes,
        certificate_bytes=certificate_bytes,
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
    """Run the sole fixed-path real structural pass after exact green proof."""

    root = _repo_root()
    proof = validate_execution_proof(
        implementation_commit=implementation_commit,
        CI_run_id=CI_run_id,
        base_job_id=base_job_id,
        optional_job_id=optional_job_id,
        repo_root=root,
    )
    _verify_green_inputs(root)
    return _run_structural_sequence(
        root=root,
        proof=proof,
        source_identity=RegisteredFileIdentity(
            PRIVATE_SOURCE_RELATIVE_PATH,
            0o600,
            PRIVATE_SOURCE_BYTES,
            PRIVATE_SOURCE_SHA256,
        ),
        vr2_contract=vr2.load_registered_contract(root),
        selector_contract=selector.load_registered_contract(root),
        sampler=_observe_machine,
        sleeper=time.sleep,
        environ=os.environ,
        now_UTC=lambda: datetime.now(timezone.utc),
        clock=time.perf_counter,
        rss_reader=_peak_rss_bytes,
        disk_reader=lambda path: shutil.disk_usage(path).free,
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


def _write_generated_fixture(
    root: Path, relative: Path, payload: bytes, mode: int
) -> None:
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    destination.chmod(mode)


def _generated_proof(root: Path) -> ExecutionProof:
    tracked = (
        proof_recovery.MODULE_RELATIVE_PATH,
        proof_recovery.CONTRACT_RELATIVE_PATH,
        Path("docs/MARC_2_PROOF_RECORD_RECOVERY_PREREGISTRATION.md"),
        Path("tests/test_marc2_proof_record_recovery_contract.py"),
    )
    record = proof_recovery.build_generated_candidate_record(
        root, tracked_artifacts=tracked
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
        repo_root=root,
        expected_proof=envelope,
        observed_proof=envelope,
    )
    return ExecutionProof(
        "a" * 40,
        1,
        2,
        3,
        _sha256_bytes(record_bytes),
        summary.to_mapping(),
    )


def _run_generated_fixture(
    repo_root: Path,
    profile: str,
    row_order: str,
) -> SequenceOutcome:
    vr2_contract = vr2.load_registered_contract(repo_root)
    selector_contract = selector.load_registered_contract(repo_root)
    source = dynamic.build_generated_profile(
        profile,
        row_order,
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    source_bytes = _canonical_json_bytes(source)
    samples = iter(
        _generated_raw_samples(datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc))
    )
    now_values = iter(
        (
            datetime(2026, 8, 16, 12, 1, tzinfo=timezone.utc),
            datetime(2026, 8, 16, 12, 1, 1, tzinfo=timezone.utc),
        )
    )
    clock_values = iter((10.0, 10.25))
    proof = _generated_proof(repo_root)
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir).resolve()
        _write_generated_fixture(
            root, PRIVATE_SOURCE_RELATIVE_PATH, source_bytes, 0o600
        )
        return _run_structural_sequence(
            root=root,
            proof=proof,
            source_identity=RegisteredFileIdentity(
                PRIVATE_SOURCE_RELATIVE_PATH,
                0o600,
                len(source_bytes),
                _sha256_bytes(source_bytes),
            ),
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
            sampler=lambda _root, _sequence: next(samples),
            sleeper=lambda _seconds: None,
            environ={name: "1" for name in THREAD_ENVIRONMENT},
            now_UTC=lambda: next(now_values),
            clock=lambda: next(clock_values),
            rss_reader=lambda: 40 * 1024**2,
            disk_reader=lambda _path: 20 * 1024**3,
            real=False,
        )


def _expect_refusal(
    name: str,
    callback: Callable[[], Any],
    *,
    expected_route: str | None = None,
) -> str:
    try:
        callback()
    except DynamicPrivateSelectionRecoveryRefusal as exc:
        if expected_route is not None and exc.route != expected_route:
            raise DynamicPrivateSelectionRecoveryRefusal(
                REFUSAL_ROUTES[9], f"mutation route differs: {name}"
            ) from exc
        return exc.route
    raise DynamicPrivateSelectionRecoveryRefusal(
        REFUSAL_ROUTES[9], f"mutation was accepted: {name}"
    )


def _certificate_mutations() -> dict[str, str]:
    base = _build_readiness_certificate(
        _generated_raw_samples(datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)),
        implementation_commit="a" * 40,
        thread_environment={name: "1" for name in THREAD_ENVIRONMENT},
        certificate_path="<generated-fixture>",
        proof_posture="generated_only_non_authoritative",
    )
    cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("certificate_schema", lambda value: value.__setitem__("schema_name", "wrong")),
        ("certificate_version", lambda value: value.__setitem__("schema_version", "9")),
        ("certificate_lane", lambda value: value.__setitem__("lane_id", "wrong")),
        ("certificate_commit", lambda value: value.__setitem__("implementation_commit", "x")),
        ("certificate_path", lambda value: value.__setitem__("certificate_path", "wrong")),
        ("certificate_contract", lambda value: value.__setitem__("machine_contract_sha256", "0" * 64)),
        ("certificate_threshold", lambda value: value["thresholds"].__setitem__("maximum_samples", 120)),
        ("certificate_thread", lambda value: value["measurements"]["thread_environment"].__setitem__(THREAD_ENVIRONMENT[0], "2")),
        ("certificate_counter", lambda value: value["access_counters"].__setitem__("network_requests", 1)),
        ("certificate_claim", lambda value: value["claim_boundary"].__setitem__("scientific_claim_not_established", "proven")),
        ("certificate_sample_sequence", lambda value: value["samples"][1].__setitem__("sequence", 4)),
        ("certificate_sample_interval", lambda value: value["samples"][1].__setitem__("monotonic_seconds", 101.0)),
    ]
    routes: dict[str, str] = {}
    for name, mutation in cases:
        changed = copy.deepcopy(base)
        mutation(changed)
        routes[name] = _expect_refusal(
            name,
            lambda item=changed: _validate_readiness_certificate(item),
            expected_route=REFUSAL_ROUTES[1],
        )
    expired = copy.deepcopy(base)
    routes["certificate_expired"] = _expect_refusal(
        "certificate_expired",
        lambda: _validate_readiness_certificate(
            expired,
            now_UTC=datetime(2026, 8, 16, 13, 0, tzinfo=timezone.utc),
        ),
        expected_route=REFUSAL_ROUTES[1],
    )
    return routes


def _aggregate_mutations(report: Mapping[str, Any]) -> dict[str, str]:
    cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("aggregate_schema", lambda value: value.__setitem__("schema_name", "wrong")),
        ("aggregate_version", lambda value: value.__setitem__("schema_version", "9")),
        ("aggregate_lane", lambda value: value.__setitem__("lane_id", "wrong")),
        ("aggregate_route", lambda value: value.__setitem__("route", "wrong")),
        ("aggregate_claim", lambda value: value["claim_boundary"].__setitem__("scientific_claim_not_established", "proven")),
        ("aggregate_counter", lambda value: value["forbidden_counters"].__setitem__("signal_sample_reads", 1)),
        ("aggregate_subject_leak", lambda value: value["source_summary"].__setitem__("subject_id", "sub-01")),
        ("aggregate_selected_ids_leak", lambda value: value["cohort_summary"].__setitem__("selected_subject_ids", ["sub-01"])),
        ("aggregate_participant_leak", lambda value: value["source_summary"].__setitem__("participant_id", "01")),
        ("aggregate_member_leak", lambda value: value["source_summary"].__setitem__("member_name", "private")),
        ("aggregate_path_leak", lambda value: value["source_summary"].__setitem__("local_path", ".codex_work/private")),
        ("aggregate_offset_leak", lambda value: value["source_summary"].__setitem__("local_header_offset", 1)),
        ("aggregate_rows_leak", lambda value: value["source_summary"].__setitem__("rows", [])),
        ("aggregate_output_cap", lambda value: value["measurements"].__setitem__("combined_output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1)),
        ("aggregate_RSS_cap", lambda value: value["measurements"].__setitem__("peak_RSS_bytes", MAX_PEAK_RSS_BYTES)),
        ("aggregate_runtime_cap", lambda value: value["measurements"].__setitem__("runtime_seconds", MAX_REAL_RUNTIME_SECONDS + 1)),
    ]
    routes: dict[str, str] = {}
    for name, mutation in cases:
        changed = copy.deepcopy(dict(report))
        mutation(changed)
        routes[name] = _expect_refusal(
            name,
            lambda item=changed: validate_aggregate_report(item),
            expected_route=REFUSAL_ROUTES[7],
        )
    missing = copy.deepcopy(dict(report))
    missing.pop("warnings")
    routes["aggregate_missing_field"] = _expect_refusal(
        "aggregate_missing_field",
        lambda: validate_aggregate_report(missing),
        expected_route=REFUSAL_ROUTES[7],
    )
    return routes


def _json_mutations() -> dict[str, str]:
    cases = {
        "JSON_duplicate_key": b'{"value":1,"value":2}\n',
        "JSON_root_array": b"[]\n",
        "JSON_BOM": b'\xef\xbb\xbf{"value":1}\n',
        "JSON_NUL": b'{"value":"\x00"}\n',
        "JSON_nonfinite": b'{"value":NaN}\n',
        "JSON_invalid_UTF8": b'{"value":"\xff"}\n',
        "JSON_syntax": b'{"value":}\n',
    }
    return {
        name: _expect_refusal(
            name,
            lambda payload=payload: _strict_json(
                payload, route=REFUSAL_ROUTES[5]
            ),
            expected_route=REFUSAL_ROUTES[5],
        )
        for name, payload in cases.items()
    }


def _file_mutations() -> dict[str, str]:
    routes: dict[str, str] = {}

    def run(kind: str) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            relative = Path("fixture/source.json")
            payload = b'{"value":1}\n'
            _write_generated_fixture(root, relative, payload, 0o600)
            path = root / relative
            identity = RegisteredFileIdentity(
                relative, 0o600, len(payload), _sha256_bytes(payload)
            )
            if kind == "missing":
                path.unlink()
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[2])
            elif kind == "mode":
                path.chmod(0o644)
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[2])
            elif kind == "size":
                path.write_bytes(payload + b"x")
                path.chmod(0o600)
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[2])
            elif kind == "owner":
                _preflight_registered_file(
                    root,
                    identity,
                    REFUSAL_ROUTES[2],
                    owner_reader=lambda: os.getuid() + 1,
                )
            elif kind == "symlink":
                target = root / "fixture/target.json"
                target.write_bytes(payload)
                target.chmod(0o600)
                path.unlink()
                path.symlink_to(target)
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[2])
            elif kind == "parent_symlink":
                path.unlink()
                (root / "fixture").rmdir()
                target = root / "target"
                target.mkdir()
                (target / "source.json").write_bytes(payload)
                (root / "fixture").symlink_to(target, target_is_directory=True)
                _preflight_registered_file(root, identity, REFUSAL_ROUTES[2])
            else:
                snapshot = _preflight_registered_file(
                    root, identity, REFUSAL_ROUTES[2]
                )
                if kind == "hash":
                    wrong = replace(identity, sha256="0" * 64)
                    _read_exact_nofollow(
                        root, wrong, snapshot, REFUSAL_ROUTES[4]
                    )
                elif kind == "race":
                    replacement = root / "fixture/replacement.json"
                    replacement.write_bytes(payload)
                    replacement.chmod(0o600)
                    os.replace(replacement, path)
                    _read_exact_nofollow(
                        root, identity, snapshot, REFUSAL_ROUTES[4]
                    )
                else:
                    raise ValueError("unknown file mutation")

    for kind, route in (
        ("missing", REFUSAL_ROUTES[2]),
        ("mode", REFUSAL_ROUTES[2]),
        ("size", REFUSAL_ROUTES[2]),
        ("owner", REFUSAL_ROUTES[2]),
        ("symlink", REFUSAL_ROUTES[2]),
        ("parent_symlink", REFUSAL_ROUTES[2]),
        ("hash", REFUSAL_ROUTES[4]),
        ("race", REFUSAL_ROUTES[4]),
    ):
        name = f"registered_file_{kind}"
        routes[name] = _expect_refusal(
            name, lambda value=kind: run(value), expected_route=route
        )
    return routes


def _state_mutations() -> dict[str, str]:
    routes: dict[str, str] = {}
    environment = {name: "1" for name in THREAD_ENVIRONMENT}
    routes["pre_marker_threads"] = _expect_refusal(
        "pre_marker_threads",
        lambda: _pre_marker_machine_recheck(
            Path("."),
            environ={**environment, THREAD_ENVIRONMENT[0]: "2"},
            rss_reader=lambda: 1,
            disk_reader=lambda _path: MINIMUM_FREE_DISK_BYTES,
        ),
        expected_route=REFUSAL_ROUTES[2],
    )
    routes["pre_marker_RSS"] = _expect_refusal(
        "pre_marker_RSS",
        lambda: _pre_marker_machine_recheck(
            Path("."),
            environ=environment,
            rss_reader=lambda: MAX_PEAK_RSS_BYTES,
            disk_reader=lambda _path: MINIMUM_FREE_DISK_BYTES,
        ),
        expected_route=REFUSAL_ROUTES[2],
    )
    routes["pre_marker_disk"] = _expect_refusal(
        "pre_marker_disk",
        lambda: _pre_marker_machine_recheck(
            Path("."),
            environ=environment,
            rss_reader=lambda: 1,
            disk_reader=lambda _path: MINIMUM_FREE_DISK_BYTES - 1,
        ),
        expected_route=REFUSAL_ROUTES[2],
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir).resolve()
        output = root / OUTPUT_ROOT_RELATIVE_PATH
        output.mkdir(parents=True)
        routes["output_root_exists"] = _expect_refusal(
            "output_root_exists",
            lambda: _create_new_output_root(root),
            expected_route=REFUSAL_ROUTES[3],
        )
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir).resolve()
        output = root / OUTPUT_ROOT_RELATIVE_PATH
        output.parent.mkdir(parents=True)
        target = root / "target"
        target.mkdir()
        output.symlink_to(target, target_is_directory=True)
        routes["output_root_symlink"] = _expect_refusal(
            "output_root_symlink",
            lambda: _create_new_output_root(root),
            expected_route=REFUSAL_ROUTES[3],
        )
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "output"
        path.write_bytes(b"old")
        routes["exclusive_write_collision"] = _expect_refusal(
            "exclusive_write_collision",
            lambda: _write_exclusive(
                path, b"new", mode=0o600, route=REFUSAL_ROUTES[3]
            ),
            expected_route=REFUSAL_ROUTES[3],
        )
    return routes


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    upstream_clock: Callable[[], float] = time.perf_counter,
    upstream_rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run ten dynamic fixture paths, replay, and at least 72 refusals."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    if _thread_values(os.environ) != {name: "1" for name in THREAD_ENVIRONMENT}:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[8], "one-thread environment is not explicit"
        )
    started = clock()
    fixed_reads, fixed_bytes = _verify_green_inputs(root)
    upstream = dynamic.qualify_generated(
        repo_root=root,
        clock=upstream_clock,
        rss_reader=upstream_rss_reader,
    )
    success_rows: list[dict[str, Any]] = []
    generated_input_bytes = 0
    generated_output_bytes = 0
    first_report: Mapping[str, Any] | None = None
    for profile, expected_count in dynamic.PROFILE_COUNTS.items():
        for row_order in ("canonical", "reversed"):
            first = _run_generated_fixture(root, profile, row_order)
            second = _run_generated_fixture(root, profile, row_order)
            if (
                first.aggregate_bytes != second.aggregate_bytes
                or first.private_manifest_bytes != second.private_manifest_bytes
                or first.marker_bytes != second.marker_bytes
                or first.certificate_bytes != second.certificate_bytes
            ):
                raise DynamicPrivateSelectionRecoveryRefusal(
                    REFUSAL_ROUTES[9], "generated replay differs"
                )
            selected = first.aggregate_report["cohort_summary"]["selected_subjects"]
            if selected != expected_count:
                raise DynamicPrivateSelectionRecoveryRefusal(
                    REFUSAL_ROUTES[9], "generated profile outcome differs"
                )
            generated_input_bytes += first.source_input_bytes
            generated_output_bytes += (
                len(first.certificate_bytes)
                + len(first.marker_bytes)
                + len(first.private_manifest_bytes)
                + len(first.aggregate_bytes)
            )
            success_rows.append(
                {
                    "profile": profile,
                    "row_order": row_order,
                    "selected_subjects": selected,
                    "selected_bundles": first.aggregate_report["cohort_summary"][
                        "selected_bundles"
                    ],
                    "selected_members": first.aggregate_report["cohort_summary"][
                        "selected_members"
                    ],
                    "selected_reservation_bytes": first.aggregate_report[
                        "cohort_summary"
                    ]["selected_reservation_bytes"],
                    "selection_identity_sha256": first.aggregate_report[
                        "selection_hashes"
                    ]["selection_identity_sha256"],
                }
            )
            if first_report is None:
                first_report = first.aggregate_report
    if first_report is None:
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[9], "generated success matrix is empty"
        )
    wrapper_mutations: dict[str, str] = {}
    for values in (
        _certificate_mutations(),
        _aggregate_mutations(first_report),
        _json_mutations(),
        _file_mutations(),
        _state_mutations(),
    ):
        overlap = set(wrapper_mutations) & set(values)
        if overlap:
            raise DynamicPrivateSelectionRecoveryRefusal(
                REFUSAL_ROUTES[9], "mutation names overlap"
            )
        wrapper_mutations.update(values)
    upstream_mutations = int(upstream["mutation_summary"]["direct_mutations_passed"])
    total_mutations = upstream_mutations + len(wrapper_mutations)
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    report: dict[str, Any] = {
        "schema_name": (
            "neurodecodekit.marc2_dynamic_private_selection_recovery_qualification"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_generated_mock_only",
        "route": SUCCESS_ROUTE,
        "proof_posture": "generated_fixture_only_no_scientific_value",
        "green_authorization_decision": {
            "commit": DECISION_COMMIT,
            "CI_run_id": DECISION_CI_RUN_ID,
            "base_python_job_id": DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
        },
        "success_matrix": success_rows,
        "replay": {
            "profiles": len(dynamic.PROFILE_COUNTS),
            "row_orders": 2,
            "success_paths": len(success_rows),
            "runs": len(success_rows) * 2,
            "all_outputs_byte_identical": True,
        },
        "mutation_summary": {
            "VR6_direct_mutations": upstream_mutations,
            "wrapper_direct_mutations": len(wrapper_mutations),
            "total_direct_mutations": total_mutations,
            "wrapper_names": list(wrapper_mutations),
            "wrapper_routes": wrapper_mutations,
        },
        "measurements": {
            "fixed_committed_artifact_reads": fixed_reads,
            "fixed_committed_input_bytes": fixed_bytes,
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes": generated_output_bytes,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "real_access_counters": {
            "real_readiness_or_certificate_operations": 0,
            "real_private_source_or_output_operations": 0,
            "real_structural_content_opens_or_bytes": 0,
            "real_VR6_adapter_calls_or_cohort_freezes": 0,
            "consumed_root_operations": 0,
            "archive_member_or_payload_reads": 0,
            "signal_event_target_label_quality_channel_or_geometry_reads": 0,
            "training_inference_prediction_freeze_delivery_or_score_operations": 0,
            "network_provider_stream_device_or_hardware_operations": 0,
            "other_project_operations": 0,
            "scientific_claim_upgrades": 0,
        },
        "acceptance_gates": {
            "green_decision_preceded_implementation": True,
            "fixed_artifact_hashes_passed": True,
            "shared_proof_validator_exercised": True,
            "five_dynamic_subject_boundaries_passed": True,
            "both_row_orders_passed": True,
            "ten_success_paths_passed": len(success_rows) == 10,
            "marker_immediately_precedes_source_open_in_sequence": True,
            "VR6_called_once_per_sequence": True,
            "minimum_72_direct_mutations_passed": total_mutations >= 72,
            "deterministic_replay_passed": True,
            "aggregate_privacy_and_target_firewall_passed": True,
            "one_thread_runtime_RSS_and_output_caps_passed": True,
            "temporary_generated_output_removed": True,
            "all_real_neural_target_model_score_counters_zero": True,
        },
        "warnings": [
            "All structural sources and outputs were generated in temporary roots.",
            "No real or consumed .codex_work path was inspected or changed.",
            "Generated selection behavior has no scientific value.",
        ],
        "unavailable_fields": [
            "real cohort identity",
            "archive member payload",
            "neural signal event target label channel or geometry",
            "model prediction score and live latency",
        ],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    payload = _canonical_json_bytes(report)
    if (
        runtime_seconds > MAX_GENERATED_RUNTIME_SECONDS
        or peak_rss_bytes >= MAX_PEAK_RSS_BYTES
        or len(payload) > MAX_COMBINED_OUTPUT_BYTES
        or any(report["real_access_counters"].values())
        or not all(report["acceptance_gates"].values())
    ):
        raise DynamicPrivateSelectionRecoveryRefusal(
            REFUSAL_ROUTES[9], "generated qualification cap or gate refused"
        )
    return report


def build_plan_summary() -> dict[str, Any]:
    """Describe the fixed command surface without touching ignored paths."""

    return {
        "schema_name": (
            "neurodecodekit.marc2_dynamic_private_selection_recovery_plan"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "commands": ["plan", "qualify", "inspect", "execute"],
        "fixed_paths": {
            "fresh_readiness_certificate": READINESS_CERTIFICATE_RELATIVE_PATH.as_posix(),
            "private_source": PRIVATE_SOURCE_RELATIVE_PATH.as_posix(),
            "new_output_root": OUTPUT_ROOT_RELATIVE_PATH.as_posix(),
        },
        "proof_order": [
            "green_decision",
            "generated_wrapper_qualification",
            "exact_implementation_remote_green",
            "fresh_readiness",
            "marker_then_one_structural_open",
        ],
        "dynamic_selected_subject_range": [
            selector.MINIMUM_SUBJECTS,
            selector.MAXIMUM_SUBJECTS,
        ],
        "generic_path_URL_retry_resume_or_fallback_argument": False,
        "network_or_archive_payload_bytes": 0,
        "FW2_neural_or_live_run_authorized": False,
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }


def build_inspection_summary() -> dict[str, Any]:
    """Inspect only committed implementation metadata."""

    registry = load_implementation_registry()
    return {
        "schema_name": (
            "neurodecodekit.marc2_dynamic_private_selection_recovery_inspection"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": registry["status"],
        "generated_qualification": registry["generated_qualification"],
        "real_execution_consumed": registry["real_execution_state"][
            "registered_real_execution_consumed"
        ],
        "private_or_consumed_path_inspected": False,
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("proof identifier must be positive")
    return parsed


def _commit(value: str) -> str:
    if len(value) != 40 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise argparse.ArgumentTypeError(
            "implementation commit must be 40 lowercase hex characters"
        )
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=f"python -m {MODULE_NAME}")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="show the fixed registered sequence")
    commands.add_parser("qualify", help="run generated/mock qualification only")
    commands.add_parser("inspect", help="inspect committed implementation metadata")
    execute = commands.add_parser(
        "execute", help="run the one fixed-path structural pass"
    )
    execute.add_argument("--implementation-commit", required=True, type=_commit)
    execute.add_argument("--ci-run-id", required=True, type=_positive_int)
    execute.add_argument("--base-job-id", required=True, type=_positive_int)
    execute.add_argument("--optional-job-id", required=True, type=_positive_int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _build_parser().parse_args(argv)
    try:
        if arguments.command == "plan":
            value = build_plan_summary()
        elif arguments.command == "qualify":
            value = qualify_generated()
        elif arguments.command == "inspect":
            value = build_inspection_summary()
        else:
            value = execute_registered(
                implementation_commit=arguments.implementation_commit,
                CI_run_id=arguments.ci_run_id,
                base_job_id=arguments.base_job_id,
                optional_job_id=arguments.optional_job_id,
            ).aggregate_report
    except DynamicPrivateSelectionRecoveryRefusal as exc:
        refusal = {
            "lane_id": LANE_ID,
            "status": "refused",
            "route": exc.route,
            "reason": exc.safe_reason,
            "retry_rerun_resume_limit": 0,
        }
        if exc.upstream_route is not None:
            refusal["upstream_VR6_route"] = exc.upstream_route
        print(json.dumps(refusal, sort_keys=True))
        return 2
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
