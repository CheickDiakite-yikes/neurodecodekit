"""Proof-gated selection-sufficiency MARC2 cohort confirmation."""

from __future__ import annotations

import argparse
import copy
import hashlib
import hmac
import json
import os
import resource
import secrets
import shutil
import stat
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_exact_count_readiness as vr33a
from neurodecodekit.datasets import marc2_selection_sufficiency_repair as vr38a

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR39P"
REQUEST_SCHEMA_NAME = (
    "neurodecodekit.marc2_selection_sufficiency_private_cohort_freeze_authorization_request"
)
DECISION_SCHEMA_NAME = (
    "neurodecodekit.marc2_selection_sufficiency_private_cohort_freeze_authorization_decision"
)
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_selection_sufficiency_private_cohort_freeze_implementation"
)
RESULT_SCHEMA_NAME = "neurodecodekit.marc2_selection_sufficiency_private_cohort_freeze_result"
PRIVATE_MANIFEST_SCHEMA_NAME = "neurodecodekit.marc2_selection_sufficiency_private_cohort_manifest"
REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_request.v0.json"
)
REQUEST_SHA256 = "313a1fe1a3cfb9002b636f1e992ce3981804c274fb6d486e84e3f143f7eb9a46"
DECISION_RELATIVE_PATH = Path(
    "registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_decision.v0.json"
)
DECISION_SHA256 = "3373365138be20ebf96c960d78b6e769dc3b22505c163a40eb2ac4a30d56e68e"
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_selection_sufficiency_private_cohort_freeze_implementation.v0.json"
)
PROOF_CLOSEOUT_RELATIVE_PATH = Path(
    "registries/marc2_selection_sufficiency_private_cohort_freeze_proof_closeout.v0.json"
)
PROOF_CLOSEOUT_SCHEMA_NAME = (
    "neurodecodekit.marc2_selection_sufficiency_private_cohort_freeze_proof_closeout"
)
GREEN_DECISION_COMMIT = "dbde5f84b3fac0ac0b23208afd56e00d678aff00"
GREEN_DECISION_CI_RUN_ID = 32_681_510_484
GREEN_DECISION_BASE_JOB_ID = 97_298_894_039
GREEN_DECISION_OPTIONAL_JOB_ID = 97_298_894_171
QUALIFICATION_ROUTE = "MARC2VR39P-G1"
PRIVATE_ROUTES = ("MARC2VR39P-R1", "MARC2VR39P-R2")
REFUSAL_ROUTES = tuple(f"MARC2VR39P-F{index:02d}" for index in range(1, 11))
CASES = (
    "selected_12_public_map_exact",
    "selected_12_optional_run_drift",
    "selected_13_public_map_exact",
    "selected_13_optional_run_drift",
    "selected_14_public_map_exact",
    "selected_14_optional_run_drift",
    "selected_15_public_map_exact",
    "selected_15_optional_run_drift",
    "selected_16_public_map_exact",
    "selected_16_optional_run_drift",
    "selected_17_public_map_exact",
    "selected_17_optional_run_drift",
    "selected_18_public_map_exact",
    "selected_18_optional_run_drift",
    "selected_19_public_map_exact",
    "selected_19_optional_run_drift",
    "required_fit_run_missing",
    "required_heldout_run_missing",
    "taxonomy_or_companion_refusal",
    "minimum_prefix_reservation_refusal",
    "uncompressed_payload_ceiling_exceeded",
)
ORDERS = vr38a.ORDERS
READINESS_PATTERNS = ("PPP", "FFF")
DIRECT_NONPASSING_PATTERNS = ("PFF", "FPF", "FFP", "PPF", "PFP", "FPP")
REPLAYS = 2
THREAD_ENVIRONMENT = dict(vr33a.THREAD_ENVIRONMENT)
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json"
)
READINESS_RELATIVE_PATH = Path(".codex_work/marc2_machine_readiness/vr39p/readiness.v0.json")
OUTPUT_ROOT_RELATIVE_PATH = Path(".codex_work/marc2_selection_sufficiency_private_cohort_freeze/v0")
MARKER_NAME = "consumed.marker.v0.json"
PRIVATE_MANIFEST_NAME = "cohort.private.v0.json"
REPORT_NAME = "report.aggregate.v0.json"
COMPLETION_NAME = "complete.marker.v0.json"
PRIVATE_SOURCE_BYTES = 418_755
PRIVATE_SOURCE_SHA256 = "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
PRIVATE_SOURCE_SCHEMA = "neurodecodekit.marc1_central_directory_private_manifest"
MAX_OUTPUT_BYTES = 2_097_152
MAX_RSS_BYTES = 268_435_456
MINIMUM_FREE_DISK_BYTES = 16_106_127_360
MAX_PRIVATE_RUNTIME_SECONDS = 30.0
MAX_GENERATED_RUNTIME_SECONDS = 120.0
MAX_MATERIALIZED_GENERATED_INPUT_BYTES = 67_108_864
MAX_COMPRESSED_BYTES = 8_589_934_592
MAX_SELECTED_UNCOMPRESSED_BYTES = 9_395_240_960
MAX_HARD_UNCOMPRESSED_BYTES = 10_737_418_240
DERIVATIVE_RESERVE_BYTES = 1_073_741_824
TEMPORARY_RESERVE_BYTES = 268_435_456
MAX_PEAK_INCREMENTAL_DISK_BYTES = 10_737_418_240
PRIVATE_NONCE_BYTES = 32
COMMITMENT_DOMAIN = b"NeuroDecodeKit:MARC2-VR39P:cohort:v0"
PUBLIC_FIELDS = {
    "schema_name",
    "schema_version",
    "lane_id",
    "route",
    "status",
    "proof_anchors",
    "commitment_scheme",
    "cohort_commitment_sha256",
    "warnings",
    "unavailable_fields",
    "claim_boundary",
}
FORBIDDEN_PUBLIC_KEYS = {
    "actual_count",
    "cohort",
    "difference",
    "eligible_count",
    "eligible_total",
    "exception",
    "label",
    "member_name",
    "observed_count",
    "participant",
    "participant_id",
    "path",
    "predicate",
    "private_hash",
    "private_manifest",
    "private_value",
    "probability",
    "reservation",
    "row",
    "selected_rows",
    "selection_identity",
    "session",
    "source_exact_name",
    "source_path",
    "subject",
    "subject_id",
    "target",
    "target_text",
    "target_value",
    "task_distribution",
    "value",
}


class SelectionSufficiencyPrivateCohortFreezeRefusal(RuntimeError):
    """Fail closed with an aggregate-safe VR39P refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR39P refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class SourceBinding:
    bytes: int
    sha256: str
    schema_name: str
    rows: int
    mode: int


@dataclass(frozen=True, slots=True)
class ExecutionPaths:
    source: Path
    readiness: Path
    output_root: Path

    @property
    def marker(self) -> Path:
        return self.output_root / MARKER_NAME

    @property
    def private_manifest(self) -> Path:
        return self.output_root / PRIVATE_MANIFEST_NAME

    @property
    def report(self) -> Path:
        return self.output_root / REPORT_NAME

    @property
    def completion(self) -> Path:
        return self.output_root / COMPLETION_NAME


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[3], "JSON value is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[3], "duplicate JSON key"
            )
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise SelectionSufficiencyPrivateCohortFreezeRefusal(REFUSAL_ROUTES[3], "non-finite JSON value")


def _strict_json(payload: bytes, *, canonical: bool = False) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[3], "UTF-8 BOM is forbidden"
        )
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[3], "invalid UTF-8"
        ) from exc
    if "\x00" in text or any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[3], "disallowed control character"
        )
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except SelectionSufficiencyPrivateCohortFreezeRefusal:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[3], "invalid JSON"
        ) from exc
    if not isinstance(value, dict):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[3], "JSON root is not an object"
        )
    if canonical and _canonical_json_bytes(value) != payload:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[3], "JSON bytes are not canonical"
        )
    return value


def _read_registered_json(
    relative_path: Path, expected_sha256: str, *, root: Path | None = None
) -> dict[str, Any]:
    base = root or _repo_root()
    try:
        payload = (base / relative_path).read_bytes()
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[0], "registered authority is unavailable"
        ) from exc
    if _sha256_bytes(payload) != expected_sha256:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[0], "registered authority hash differs"
        )
    return _strict_json(payload)


def load_registered_request(root: Path | None = None) -> dict[str, Any]:
    return _read_registered_json(REQUEST_RELATIVE_PATH, REQUEST_SHA256, root=root)


def load_registered_decision(root: Path | None = None) -> dict[str, Any]:
    return _read_registered_json(DECISION_RELATIVE_PATH, DECISION_SHA256, root=root)


def _verify_authority_mapping(request: Mapping[str, Any], decision: Mapping[str, Any]) -> None:
    registered_request = load_registered_request()
    registered_decision = load_registered_decision()
    authorization = registered_decision.get("authorization", {})
    requirements = registered_decision.get("generated_stage_requirements", {})
    if (
        not isinstance(request, dict)
        or request != registered_request
        or request.get("schema_name") != REQUEST_SCHEMA_NAME
        or request.get("lane_id") != LANE_ID
        or not isinstance(decision, dict)
        or decision != registered_decision
        or decision.get("schema_name") != DECISION_SCHEMA_NAME
        or decision.get("lane_id") != LANE_ID
        or decision.get("user_authorization", {}).get("actual_message_verbatim") != "continue"
        or authorization.get("generated_wrapper_implementation_after_decision_green") is not True
        or authorization.get("generated_wrapper_qualification_after_decision_green") is not True
        or requirements.get("case_count") != 21
        or requirements.get("required_paths") != 168
        or requirements.get("VR33A_calls") != 168
        or requirements.get("readiness_provider_calls") != 504
        or requirements.get("readiness_sleeper_calls") != 336
        or requirements.get("VR38A_calls") != 84
        or requirements.get("generated_cohort_writes") != 64
        or requirements.get("route_counts") != {PRIVATE_ROUTES[0]: 64, PRIVATE_ROUTES[1]: 104}
        or requirements.get("direct_refusal_minimum") != 200
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[0], "registered authority mapping differs"
        )


def _verify_decision_proof() -> None:
    if (
        GREEN_DECISION_COMMIT != "dbde5f84b3fac0ac0b23208afd56e00d678aff00"
        or GREEN_DECISION_CI_RUN_ID != 32_681_510_484
        or GREEN_DECISION_BASE_JOB_ID != 97_298_894_039
        or GREEN_DECISION_OPTIONAL_JOB_ID != 97_298_894_171
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[0], "decision proof differs"
        )


def _verify_fixed_inputs(
    request: Mapping[str, Any], decision: Mapping[str, Any], root: Path | None = None
) -> int:
    base = root or _repo_root()
    rows: list[Mapping[str, Any]] = []
    for group in (
        request.get("fixed_committed_artifacts"),
        decision.get("bound_packet_artifacts"),
        decision.get("decision_artifacts"),
    ):
        if not isinstance(group, list):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[0], "fixed input registry differs"
            )
        rows.extend(group)
    seen: set[str] = set()
    total = 0
    for row in rows:
        if not isinstance(row, Mapping) or not {
            "path",
            "bytes",
            "sha256",
        }.issubset(row):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        relative = str(row["path"])
        if relative in seen:
            continue
        seen.add(relative)
        try:
            payload = (base / relative).read_bytes()
        except OSError as exc:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row["bytes"] or _sha256_bytes(payload) != row["sha256"]:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if len(seen) != 28 or total != 374_043:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[9], "thread environment differs"
        )


def _require_green_implementation(root: Path | None = None) -> str:
    base = root or _repo_root()
    try:
        record = json.loads((base / IMPLEMENTATION_RELATIVE_PATH).read_text(encoding="utf-8"))
        closeout = json.loads((base / PROOF_CLOSEOUT_RELATIVE_PATH).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[1], "implementation proof is unavailable"
        ) from exc
    proof = record.get("remote_implementation_proof")
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("lane_id") != LANE_ID
        or not isinstance(proof, dict)
        or proof.get("both_required_jobs_green") is not True
        or proof.get("scope_changed_after_qualification") is not False
        or proof.get("qualification_route") != QUALIFICATION_ROUTE
        or proof.get("qualification_repeated_for_proof_closeout") is not False
        or proof.get("private_operations_during_proof_closeout") != 0
        or not isinstance(proof.get("commit"), str)
        or len(proof["commit"]) != 40
        or closeout.get("schema_name") != PROOF_CLOSEOUT_SCHEMA_NAME
        or closeout.get("lane_id") != LANE_ID
        or closeout.get("status") != "remotely_green_proof_only_closeout_private_stage_eligible"
        or closeout.get("implementation_commit") != proof["commit"]
        or closeout.get("qualification_route") != QUALIFICATION_ROUTE
        or closeout.get("qualification_repeated") is not False
        or closeout.get("private_operations") != 0
        or not isinstance(closeout.get("green_proof"), dict)
        or closeout["green_proof"].get("both_required_jobs_green") is not True
        or not isinstance(closeout["green_proof"].get("commit"), str)
        or len(closeout["green_proof"]["commit"]) != 40
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[1], "implementation proof is not remotely green"
        )
    artifact_blobs = closeout.get("implementation_artifact_git_blobs")
    artifacts = record.get("implementation_artifacts")
    if not isinstance(artifact_blobs, dict) or not isinstance(artifacts, list):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[1], "implementation artifact proof differs"
        )
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[1], "implementation artifact row differs"
            )
        role = artifact.get("role")
        relative = artifact.get("path")
        if not isinstance(role, str) or not isinstance(relative, str):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[1], "implementation artifact identity differs"
            )
        try:
            payload = (base / relative).read_bytes()
        except OSError as exc:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[1], "implementation artifact is unavailable"
            ) from exc
        git_blob = hashlib.sha1(
            f"blob {len(payload)}\0".encode("ascii") + payload,
            usedforsecurity=False,
        ).hexdigest()
        if (
            len(payload) != artifact.get("bytes")
            or _sha256_bytes(payload) != artifact.get("sha256")
            or artifact_blobs.get(role) != git_blob
        ):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[1], "implementation artifact binding differs"
            )
    return proof["commit"]


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                    REFUSAL_ROUTES[7], "aggregate report contains forbidden field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_aggregate_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    payload = _canonical_json_bytes(report)
    if len(payload) > MAX_OUTPUT_BYTES:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[7], "aggregate report exceeds output cap"
        )


def _open_directory_nofollow(path: Path) -> int:
    absolute = path.absolute()
    descriptor = os.open("/", os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for component in absolute.parts[1:]:
            child = os.open(component, directory_flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
    except OSError:
        os.close(descriptor)
        raise
    return descriptor


def _open_parent_nofollow(path: Path) -> int:
    return _open_directory_nofollow(path.absolute().parent)


def _ensure_directory_nofollow(
    path: Path,
    *,
    mode: int = 0o700,
    exclusive_leaf: bool = False,
) -> int:
    absolute = path.absolute()
    descriptor = os.open("/", os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        components = absolute.parts[1:]
        for index, component in enumerate(components):
            leaf = index == len(components) - 1
            created = False
            if exclusive_leaf and leaf:
                os.mkdir(component, mode=mode, dir_fd=descriptor)
                os.fsync(descriptor)
                created = True
            try:
                child = os.open(component, directory_flags, dir_fd=descriptor)
            except FileNotFoundError:
                os.mkdir(component, mode=mode, dir_fd=descriptor)
                os.fsync(descriptor)
                created = True
                child = os.open(component, directory_flags, dir_fd=descriptor)
            facts = os.fstat(child)
            if not stat.S_ISDIR(facts.st_mode) or (created and stat.S_IMODE(facts.st_mode) != mode):
                os.close(child)
                raise OSError("directory component is not a directory")
            os.close(descriptor)
            descriptor = child
    except OSError:
        os.close(descriptor)
        raise
    return descriptor


def _write_exclusive_at(
    parent_descriptor: int,
    name: str,
    payload: bytes,
    *,
    mode: int = 0o600,
    writer: Callable[[int, Any], int] = os.write,
) -> int:
    if not name or name in {".", ".."} or "/" in name:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[4], "output leaf name differs"
        )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, mode, dir_fd=parent_descriptor)
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[4], "exclusive output creation refused"
        ) from exc
    try:
        view = memoryview(payload)
        while view:
            written = writer(descriptor, view)
            if written <= 0 or written > len(view):
                raise OSError("short output write")
            view = view[written:]
        os.fsync(descriptor)
        opened = os.fstat(descriptor)
        if stat.S_IMODE(opened.st_mode) != mode or opened.st_size != len(payload):
            raise OSError("output identity differs")
        os.fsync(parent_descriptor)
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[4], "output write refused"
        ) from exc
    finally:
        os.close(descriptor)
    return len(payload)


def _write_exclusive(
    path: Path,
    payload: bytes,
    *,
    mode: int = 0o600,
    before_write: Callable[[Path], None] | None = None,
    writer: Callable[[int, Any], int] = os.write,
) -> int:
    if before_write is not None:
        before_write(path)
    parent_descriptor: int | None = None
    try:
        parent_descriptor = _ensure_directory_nofollow(path.parent)
        return _write_exclusive_at(
            parent_descriptor,
            path.name,
            payload,
            mode=mode,
            writer=writer,
        )
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[4], "exclusive output creation refused"
        ) from exc
    finally:
        if parent_descriptor is not None:
            os.close(parent_descriptor)


def _read_small_at(parent_descriptor: int, name: str, *, mode: int) -> bytes:
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_descriptor,
        )
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate artifact open refused"
        ) from exc
    try:
        facts = os.fstat(descriptor)
        if (
            not stat.S_ISREG(facts.st_mode)
            or facts.st_size > MAX_OUTPUT_BYTES
            or stat.S_IMODE(facts.st_mode) != mode
        ):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "aggregate artifact facts differ"
            )
        chunks: list[bytes] = []
        total = 0
        while total <= MAX_OUTPUT_BYTES:
            chunk = os.read(descriptor, min(65_536, MAX_OUTPUT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if len(payload) != facts.st_size or len(payload) > MAX_OUTPUT_BYTES:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate artifact content size differs"
        )
    return payload


@dataclass
class PinnedOutputRoot:
    path: Path
    descriptor: int
    device: int
    inode: int
    marker_payload: bytes

    def assert_path_identity(self) -> None:
        try:
            descriptor = _open_directory_nofollow(self.path)
        except OSError as exc:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[4], "output root identity is unavailable"
            ) from exc
        try:
            facts = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        if facts.st_dev != self.device or facts.st_ino != self.inode:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[4], "output root identity changed"
            )

    def write(self, name: str, payload: bytes, *, mode: int = 0o600) -> int:
        self.assert_path_identity()
        return _write_exclusive_at(self.descriptor, name, payload, mode=mode)

    def read(self, name: str, *, mode: int) -> bytes:
        self.assert_path_identity()
        return _read_small_at(self.descriptor, name, mode=mode)

    def size(self, name: str) -> int:
        self.assert_path_identity()
        facts = os.stat(name, dir_fd=self.descriptor, follow_symlinks=False)
        if not stat.S_ISREG(facts.st_mode):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "output artifact type differs"
            )
        return facts.st_size

    def close(self) -> None:
        os.close(self.descriptor)


def _read_small_nofollow(path: Path, *, mode: int) -> bytes:
    try:
        facts = os.lstat(path)
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate artifact is unavailable"
        ) from exc
    if (
        not stat.S_ISREG(facts.st_mode)
        or stat.S_ISLNK(facts.st_mode)
        or facts.st_size > MAX_OUTPUT_BYTES
        or stat.S_IMODE(facts.st_mode) != mode
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate artifact facts differ"
        )
    parent_descriptor: int | None = None
    try:
        parent_descriptor = _open_parent_nofollow(path)
        descriptor = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_descriptor,
        )
    except OSError as exc:
        if parent_descriptor is not None:
            os.close(parent_descriptor)
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate artifact open refused"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if (
            opened.st_dev != facts.st_dev
            or opened.st_ino != facts.st_ino
            or opened.st_size != facts.st_size
            or stat.S_IMODE(opened.st_mode) != mode
        ):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "aggregate artifact identity differs"
            )
        chunks: list[bytes] = []
        total = 0
        while total <= MAX_OUTPUT_BYTES:
            chunk = os.read(descriptor, min(65_536, MAX_OUTPUT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
    finally:
        os.close(descriptor)
        if parent_descriptor is not None:
            os.close(parent_descriptor)
    payload = b"".join(chunks)
    if len(payload) != facts.st_size or len(payload) > MAX_OUTPUT_BYTES:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate artifact content size differs"
        )
    return payload


def _preflight_bound_source(path: Path, binding: SourceBinding) -> os.stat_result:
    try:
        facts = os.lstat(path)
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[5], "source preflight refused"
        ) from exc
    if (
        not stat.S_ISREG(facts.st_mode)
        or stat.S_ISLNK(facts.st_mode)
        or facts.st_size != binding.bytes
        or stat.S_IMODE(facts.st_mode) != binding.mode
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[5], "source facts differ"
        )
    return facts


def _read_bound_source_once(
    path: Path, binding: SourceBinding, *, preflight: os.stat_result | None = None
) -> dict[str, Any]:
    facts = preflight or _preflight_bound_source(path, binding)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    parent_descriptor: int | None = None
    try:
        parent_descriptor = _open_parent_nofollow(path)
        descriptor = os.open(path.name, flags, dir_fd=parent_descriptor)
    except OSError as exc:
        if parent_descriptor is not None:
            os.close(parent_descriptor)
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[5], "source open refused"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_dev != facts.st_dev
            or opened.st_ino != facts.st_ino
            or opened.st_size != binding.bytes
            or stat.S_IMODE(opened.st_mode) != binding.mode
        ):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[5], "opened source identity differs"
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65_536, binding.bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > binding.bytes:
                raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                    REFUSAL_ROUTES[5], "source exceeds byte binding"
                )
    finally:
        os.close(descriptor)
        if parent_descriptor is not None:
            os.close(parent_descriptor)
    payload = b"".join(chunks)
    if len(payload) != binding.bytes or _sha256_bytes(payload) != binding.sha256:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[5], "source content binding differs"
        )
    source = _strict_json(payload)
    entries = source.get("entries")
    if (
        source.get("schema_name") != binding.schema_name
        or not isinstance(entries, list)
        or len(entries) != binding.rows
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[5], "source structural envelope differs"
        )
    return source


def _sample_payload(sequence: int, passing: bool) -> dict[str, Any]:
    return {
        "sequence": sequence,
        "passing": passing,
        "observed_at_seconds": float(sequence * 5),
        "available_bytes": MINIMUM_FREE_DISK_BYTES + sequence,
    }


def _collect_generated_readiness(
    pattern: str,
) -> tuple[vr33a.ReadinessResult, int, int, int]:
    if pattern not in (*READINESS_PATTERNS, *DIRECT_NONPASSING_PATTERNS):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[2], "generated readiness pattern differs"
        )
    samples = [
        _sample_payload(sequence, marker == "P") for sequence, marker in enumerate(pattern, start=1)
    ]
    provider_calls = 0
    sleeper_calls = 0
    input_bytes = 0

    def provider(sequence: int) -> Mapping[str, Any]:
        nonlocal provider_calls, input_bytes
        provider_calls += 1
        sample = samples[sequence - 1]
        input_bytes += len(_canonical_json_bytes(sample))
        return sample

    def sleeper(interval: float) -> None:
        nonlocal sleeper_calls
        if interval != vr33a.INTERVAL_SECONDS:
            raise ValueError("generated sleeper interval differs")
        sleeper_calls += 1

    result = vr33a.collect_exact_readiness(provider, sleeper)
    return result, provider_calls, sleeper_calls, input_bytes


def _readiness_certificate_bytes(readiness: vr33a.ReadinessResult, *, generated: bool) -> bytes:
    payload = {
        "schema_name": "neurodecodekit.marc2_selection_sufficiency_readiness_certificate",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "generated": generated,
        "ready": readiness.ready,
        "sample_count": len(readiness.samples),
        "samples": [
            {
                "sequence": sample.sequence,
                "passing": sample.passing,
                "observed_at_seconds": sample.observed_at_seconds,
                "available_bytes": sample.available_bytes,
            }
            for sample in readiness.samples
        ],
    }
    return _canonical_json_bytes(payload)


def _write_readiness_certificate(
    paths: ExecutionPaths,
    readiness: vr33a.ReadinessResult,
    *,
    generated: bool,
) -> int:
    return _write_exclusive(
        paths.readiness,
        _readiness_certificate_bytes(readiness, generated=generated),
    )


def _make_marker(paths: ExecutionPaths, *, generated: bool) -> PinnedOutputRoot:
    try:
        descriptor = _ensure_directory_nofollow(paths.output_root, exclusive_leaf=True)
    except OSError as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[4], "fresh output root precondition differs"
        ) from exc
    marker = {
        "schema_name": "neurodecodekit.marc2_selection_sufficiency_consumed_marker",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "generated": generated,
        "state": "consumed_no_retry_or_rerun",
    }
    marker_payload = _canonical_json_bytes(marker)
    try:
        facts = os.fstat(descriptor)
        if stat.S_IMODE(facts.st_mode) != 0o700:
            raise OSError("output root mode differs")
        _write_exclusive_at(descriptor, MARKER_NAME, marker_payload)
    except (OSError, SelectionSufficiencyPrivateCohortFreezeRefusal) as exc:
        os.close(descriptor)
        if isinstance(exc, SelectionSufficiencyPrivateCohortFreezeRefusal):
            raise
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[4], "consumed marker creation refused"
        ) from exc
    return PinnedOutputRoot(
        path=paths.output_root,
        descriptor=descriptor,
        device=facts.st_dev,
        inode=facts.st_ino,
        marker_payload=marker_payload,
    )


def _map_vr38a_route(route: str) -> str:
    if route in vr38a.SUCCESS_ROUTES:
        return PRIVATE_ROUTES[0]
    if route in (*vr38a.DIAGNOSTIC_ROUTES, *vr38a.REFUSAL_ROUTES):
        return PRIVATE_ROUTES[1]
    raise SelectionSufficiencyPrivateCohortFreezeRefusal(
        REFUSAL_ROUTES[6], "VR38A route is not allowlisted"
    )


def _selected_cardinality(case: str) -> int | None:
    if not case.startswith("selected_"):
        return None
    try:
        count = int(case.split("_", 2)[1])
    except (IndexError, ValueError) as exc:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[2], "generated cardinality differs"
        ) from exc
    if count not in range(12, 20):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[2], "generated cardinality is out of bounds"
        )
    return count


def _build_generated_source(case: str, order: str) -> dict[str, Any]:
    if case not in CASES or order not in ORDERS:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[2], "generated condition differs"
        )
    count = _selected_cardinality(case)
    if count is not None:
        upstream_case = (
            "single_cell_contiguous_optional_surplus"
            if case.endswith("optional_run_drift")
            else "public_map_exact_control"
        )
        source = vr38a.build_generated_case(upstream_case, "canonical")
        selector_contract = vr38a.selector.load_registered_contract(_repo_root())
        rank = vr38a.selector._validate_rank(selector_contract)
        vr38a._adjust_required_prefix_reservation(
            source,
            rank[:count],
            vr38a.selector.RESERVATION_CAP_BYTES - 1,
        )
    elif case == "required_fit_run_missing":
        source = vr38a.build_generated_case("required_fit_run_missing", "canonical")
    elif case == "required_heldout_run_missing":
        source = vr38a.build_generated_case("required_heldout_run_missing", "canonical")
    elif case == "taxonomy_or_companion_refusal":
        source = vr38a.build_generated_case("incomplete_companion_set", "canonical")
    elif case == "minimum_prefix_reservation_refusal":
        source = vr38a.build_generated_case("minimum_prefix_exceeds_cap", "canonical")
    else:
        source = _build_generated_source("selected_12_public_map_exact", "canonical")
        selected = set(
            vr38a.selector._validate_rank(vr38a.selector.load_registered_contract(_repo_root()))[
                :12
            ]
        )
        selected_rows = [
            row
            for row in source["entries"]
            if isinstance(row, dict)
            and isinstance(row.get("member_name"), str)
            and (match := vr38a.vr20a._core_match(row["member_name"])) is not None
            and match.group("subject") in selected
            and match.group("task") == vr38a.vr35a.PUBLISHED_TASK
            and match.group("session") in {"ses-01", "ses-02"}
            and vr38a.vr20a._semantic_run(match.group("run")) in {1, 2, 3}
        ]
        quotient, remainder = divmod(MAX_SELECTED_UNCOMPRESSED_BYTES + 1, len(selected_rows))
        for index, row in enumerate(sorted(selected_rows, key=lambda item: item["member_name"])):
            row["uncompressed_size"] = quotient + (1 if index < remainder else 0)
    source["entries"] = sorted(source["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        source["entries"].reverse()
    return source


def _apply_vr38a(
    source: Mapping[str, Any],
) -> tuple[str, vr38a.SelectionSufficiencyOutcome | None, str]:
    before = vr38a._source_bytes(source)
    outcome: vr38a.SelectionSufficiencyOutcome | None = None
    try:
        outcome = vr38a.select_generated_source(source)
        upstream = outcome.route
    except vr38a.SelectionSufficiencyRepairRefusal as exc:
        if exc.route not in (*vr38a.DIAGNOSTIC_ROUTES, *vr38a.REFUSAL_ROUTES):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[6], "VR38A refused outside the diagnostic map"
            ) from exc
        upstream = exc.route
    if vr38a._source_bytes(source) != before:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[6], "source changed during VR38A call"
        )
    return _map_vr38a_route(upstream), outcome, upstream


def _storage_totals(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    compressed = 0
    uncompressed = 0
    for row in rows:
        compressed_size = row.get("compressed_size")
        uncompressed_size = row.get("uncompressed_size")
        if (
            isinstance(compressed_size, bool)
            or not isinstance(compressed_size, int)
            or compressed_size < 0
            or isinstance(uncompressed_size, bool)
            or not isinstance(uncompressed_size, int)
            or uncompressed_size < 0
        ):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[6], "selected storage field differs"
            )
        compressed += compressed_size
        uncompressed += uncompressed_size
    peak = uncompressed + DERIVATIVE_RESERVE_BYTES + TEMPORARY_RESERVE_BYTES
    if (
        compressed > MAX_COMPRESSED_BYTES
        or uncompressed > MAX_SELECTED_UNCOMPRESSED_BYTES
        or uncompressed > MAX_HARD_UNCOMPRESSED_BYTES
        or peak > MAX_PEAK_INCREMENTAL_DISK_BYTES
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[6], "selected storage envelope refused"
        )
    return {
        "selected_compressed_bytes": compressed,
        "selected_uncompressed_bytes": uncompressed,
        "derivative_reserve_bytes": DERIVATIVE_RESERVE_BYTES,
        "temporary_reserve_bytes": TEMPORARY_RESERVE_BYTES,
        "peak_incremental_disk_bytes": peak,
    }


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


def _assert_no_generated_provenance(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if "generated" in str(key).casefold() or "fixture" in str(key).casefold():
                raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                    REFUSAL_ROUTES[6], "generated provenance key remained"
                )
            _assert_no_generated_provenance(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_generated_provenance(child)
    elif isinstance(value, str) and (
        "generated" in value.casefold() or "fixture" in value.casefold()
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[6], "generated provenance value remained"
        )


def _privateize_and_validate_rows(
    rows: list[Any],
    *,
    count: int,
    selected_subject_ids: Sequence[Any],
    raw_source_sha256: str,
    canonical_source_sha256: str,
) -> list[dict[str, Any]]:
    if not _is_sha256(raw_source_sha256) or not _is_sha256(canonical_source_sha256):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[6], "private source hash differs"
        )
    transformed: list[dict[str, Any]] = []
    bundles: dict[tuple[str, str, str], set[str]] = {}
    subjects: set[str] = set()
    for candidate in rows:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("source_hashes"), dict):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[6], "selected row provenance differs"
            )
        row = copy.deepcopy(candidate)
        member_name = row.get("member_name")
        source_id = row.get("source_id")
        if not isinstance(member_name, str) or not isinstance(source_id, str):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[6], "selected row source identity differs"
            )
        member_name = member_name.replace("Freewill_generated/", "Freewill_private_source/")
        source_id = source_id.removesuffix("_generated") + "_private_source"
        row["member_name"] = member_name
        row["source_id"] = source_id
        source_hashes = row["source_hashes"]
        contract_sha256 = source_hashes.get("contract_sha256")
        if not _is_sha256(contract_sha256):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[6], "selected row contract provenance differs"
            )
        row["source_hashes"] = {
            "contract_sha256": contract_sha256,
            "raw_source_file_sha256": raw_source_sha256,
            "canonical_private_inventory_sha256": canonical_source_sha256,
        }
        subject = row.get("subject_id")
        session = row.get("session_id")
        run = row.get("run_id")
        split_role = row.get("split_role")
        expected_role = "fit" if session == "ses-01" else "heldout"
        if (
            not isinstance(subject, str)
            or session not in {"ses-01", "ses-02"}
            or run not in {"run-01", "run-02", "run-03"}
            or split_role != expected_role
            or f"/{subject}/{session}/" not in member_name
            or "task-reachingandgrasping" not in member_name
            or f"run-{int(str(run).split('-')[1]):04d}" not in member_name
        ):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[6], "selected row split identity differs"
            )
        suffix = Path(member_name).suffix.casefold()
        if suffix not in {".eeg", ".vhdr", ".vmrk", ".tsv"}:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[6], "selected companion type differs"
            )
        bundle_key = (subject, str(session), str(run))
        bundles.setdefault(bundle_key, set()).add(suffix)
        subjects.add(subject)
        transformed.append(row)
    expected_companions = {".eeg", ".vhdr", ".vmrk", ".tsv"}
    if (
        len(subjects) != count
        or len(selected_subject_ids) != count
        or len(set(selected_subject_ids)) != count
        or set(selected_subject_ids) != subjects
        or len(bundles) != count * 6
        or any(companions != expected_companions for companions in bundles.values())
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[6], "selected cohort topology differs"
        )
    _assert_no_generated_provenance(transformed)
    return transformed


def _build_private_manifest(
    outcome: vr38a.SelectionSufficiencyOutcome,
    *,
    raw_source_sha256: str,
    nonce: bytes,
) -> tuple[dict[str, Any], str]:
    selection = outcome.selection
    rows = copy.deepcopy(selection.private_manifest.get("rows"))
    cohort = selection.cohort_summary
    split = selection.split_summary
    count = cohort.get("selected_subjects")
    if (
        outcome.route not in vr38a.SUCCESS_ROUTES
        or not isinstance(rows, list)
        or isinstance(count, bool)
        or not isinstance(count, int)
        or count not in range(12, 20)
        or len(rows) != count * 24
        or split.get("selected_run_bundles") != count * 6
        or split.get("fit_run_bundles") != count * 3
        or split.get("heldout_run_bundles") != count * 3
        or split.get("selected_core_members") != count * 24
        or split.get("fit_session") != "ses-01"
        or split.get("heldout_session") != "ses-02"
        or split.get("fit_heldout_overlap") != 0
        or split.get("row_random_split_used") is not False
        or cohort.get("selection_is_maximal_contiguous_rank_prefix") is not True
        or cohort.get("selection_was_target_quality_and_outcome_free") is not True
        or len(nonce) != PRIVATE_NONCE_BYTES
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[6], "cohort cardinality differs"
        )
    rows = _privateize_and_validate_rows(
        rows,
        count=count,
        selected_subject_ids=cohort.get("selected_subject_ids", []),
        raw_source_sha256=raw_source_sha256,
        canonical_source_sha256=outcome.source_sha256,
    )
    storage = _storage_totals(rows)
    selected_rows_sha256 = _sha256_bytes(_canonical_json_bytes(rows))
    split_protocol_sha256 = _sha256_bytes(_canonical_json_bytes(dict(split)))
    configuration_sha256 = _sha256_bytes(
        _canonical_json_bytes(
            {
                "VR38A_contract_sha256": vr38a.CONTRACT_SHA256,
                "request_sha256": REQUEST_SHA256,
                "decision_sha256": DECISION_SHA256,
            }
        )
    )
    manifest_without_nonce = {
        "schema_name": PRIVATE_MANIFEST_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "proof_posture": "target_free_private_structural_selection_no_neural_payload",
        "task": vr38a.vr35a.PUBLISHED_TASK,
        "hash_bindings": {
            "VR38A_contract_sha256": vr38a.CONTRACT_SHA256,
            "configuration_sha256": configuration_sha256,
            "raw_source_file_sha256": raw_source_sha256,
            "canonical_private_inventory_sha256": outcome.source_sha256,
            "selection_identity_sha256": selection.selection_hashes["selection_identity_sha256"],
            "semantic_selection_sha256": outcome.semantic_sha256,
            "selected_names_sha256": outcome.source_exact_selected_names_sha256,
            "selected_rows_sha256": selected_rows_sha256,
            "split_protocol_sha256": split_protocol_sha256,
        },
        "cohort_summary": dict(cohort),
        "split_summary": dict(split),
        "storage_feasibility": storage,
        "rows": rows,
    }
    message = COMMITMENT_DOMAIN + b"\x00" + _canonical_json_bytes(manifest_without_nonce)
    commitment = hmac.new(nonce, message, hashlib.sha256).hexdigest()
    manifest = dict(manifest_without_nonce)
    manifest["commitment"] = {
        "scheme": "HMAC-SHA256-v0",
        "domain_separator_utf8": COMMITMENT_DOMAIN.decode("ascii"),
        "private_nonce_hex": nonce.hex(),
        "cohort_commitment_sha256": commitment,
    }
    return manifest, commitment


def _verify_private_commitment(manifest: Mapping[str, Any], public_value: str) -> bool:
    candidate = copy.deepcopy(dict(manifest))
    commitment = candidate.pop("commitment", None)
    if not isinstance(commitment, dict):
        return False
    nonce_hex = commitment.get("private_nonce_hex")
    stored_value = commitment.get("cohort_commitment_sha256")
    if (
        set(commitment)
        != {
            "scheme",
            "domain_separator_utf8",
            "private_nonce_hex",
            "cohort_commitment_sha256",
        }
        or commitment.get("scheme") != "HMAC-SHA256-v0"
        or commitment.get("domain_separator_utf8") != COMMITMENT_DOMAIN.decode("ascii")
        or not isinstance(nonce_hex, str)
        or not _is_sha256(stored_value)
        or not _is_sha256(public_value)
        or nonce_hex != nonce_hex.lower()
        or len(nonce_hex) != PRIVATE_NONCE_BYTES * 2
    ):
        return False
    try:
        nonce = bytes.fromhex(nonce_hex)
    except ValueError:
        return False
    if len(nonce) != PRIVATE_NONCE_BYTES:
        return False
    expected = hmac.new(
        nonce,
        COMMITMENT_DOMAIN + b"\x00" + _canonical_json_bytes(candidate),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, stored_value) and hmac.compare_digest(
        stored_value, public_value
    )


def _require_private_commitment(manifest: Mapping[str, Any], public_value: str) -> None:
    if not _verify_private_commitment(manifest, public_value):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[6], "private commitment verification refused"
        )


def _case_report(
    *,
    route: str,
    commitment: str | None,
    generated: bool,
    implementation_commit: str | None = None,
) -> dict[str, Any]:
    if (
        route not in PRIVATE_ROUTES
        or (route == PRIVATE_ROUTES[0] and not _is_sha256(commitment))
        or (route == PRIVATE_ROUTES[1] and commitment is not None)
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[7], "public route and commitment differ"
        )
    proof_anchors: dict[str, Any] = {
        "decision_commit": GREEN_DECISION_COMMIT,
        "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
    }
    if implementation_commit is not None:
        proof_anchors["implementation_commit"] = implementation_commit
    report = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": route,
        "status": (
            "generated_target_free_structural_confirmation"
            if generated
            else "consumed_target_free_structural_confirmation"
        ),
        "proof_anchors": proof_anchors,
        "commitment_scheme": "HMAC-SHA256-v0",
        "cohort_commitment_sha256": commitment,
        "warnings": [
            "generated_only" if generated else "target_free_structural_only",
            "R1_only_makes_separate_FW2_preregistration_eligible",
            "no_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "selected_subject_count_identity_topology_rows_or_sizes",
            "readiness_failure_stage_runtime_RSS_or_operations",
            "archive_neural_target_model_prediction_or_score",
        ],
        "claim_boundary": {
            "engineering": "terminal target-free cohort freeze state machine",
            "scientific": "none",
        },
    }
    if set(report) != PUBLIC_FIELDS:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[7], "public report shape differs"
        )
    _assert_aggregate_safe(report)
    return report


def _validate_report_payload(payload: bytes, *, allow_generated: bool) -> dict[str, Any]:
    report = _strict_json(payload, canonical=True)
    _assert_aggregate_safe(report)
    if report.get("schema_name") != RESULT_SCHEMA_NAME or report.get("lane_id") != LANE_ID:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate report identity differs"
        )
    route = report.get("route")
    commitment = report.get("cohort_commitment_sha256")
    if route not in PRIVATE_ROUTES:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate report route differs"
        )
    implementation_commit = None
    if not allow_generated:
        proof_anchors = report.get("proof_anchors")
        if not isinstance(proof_anchors, dict):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "private proof anchors differ"
            )
        implementation_commit = proof_anchors.get("implementation_commit")
        if not isinstance(implementation_commit, str) or len(implementation_commit) != 40:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "private implementation proof differs"
            )
    expected = _case_report(
        route=str(route),
        commitment=commitment if isinstance(commitment, str) else None,
        generated=allow_generated,
        implementation_commit=implementation_commit,
    )
    if report != expected:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "aggregate report allowlist differs"
        )
    return report


def _inspect_report_file(path: Path, *, allow_generated: bool) -> dict[str, Any]:
    return _validate_report_payload(
        _read_small_nofollow(path, mode=0o644),
        allow_generated=allow_generated,
    )


def _completion_payload(
    *,
    route: str,
    marker_payload: bytes,
    readiness_payload: bytes,
    private_payload: bytes | None,
    report_payload: bytes,
) -> bytes:
    return _canonical_json_bytes(
        {
            "schema_name": "neurodecodekit.marc2_selection_sufficiency_completion",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "state": "complete",
            "route": route,
            "consumed_marker_sha256": _sha256_bytes(marker_payload),
            "readiness_certificate_sha256": _sha256_bytes(readiness_payload),
            "private_manifest_sha256": (
                _sha256_bytes(private_payload) if private_payload is not None else None
            ),
            "report_sha256": _sha256_bytes(report_payload),
        }
    )


def _require_output_cap(total_bytes: int) -> None:
    if total_bytes < 0 or total_bytes > MAX_OUTPUT_BYTES:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[9], "combined output cap exceeded"
        )


def _validate_pinned_completion(
    output: PinnedOutputRoot,
    *,
    readiness_path: Path,
    allow_generated: bool,
) -> dict[str, Any]:
    completion = _strict_json(output.read(COMPLETION_NAME, mode=0o600), canonical=True)
    if set(completion) != {
        "schema_name",
        "schema_version",
        "lane_id",
        "state",
        "route",
        "consumed_marker_sha256",
        "readiness_certificate_sha256",
        "private_manifest_sha256",
        "report_sha256",
    }:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "completion allowlist differs"
        )
    marker_payload = output.read(MARKER_NAME, mode=0o600)
    readiness_payload = _read_small_nofollow(readiness_path, mode=0o600)
    report_payload = output.read(REPORT_NAME, mode=0o644)
    report = _validate_report_payload(report_payload, allow_generated=allow_generated)
    route = report["route"]
    private_sha256 = completion.get("private_manifest_sha256")
    private_payload: bytes | None = None
    if route == PRIVATE_ROUTES[0]:
        private_payload = output.read(PRIVATE_MANIFEST_NAME, mode=0o600)
        if not _is_sha256(private_sha256):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "completion private manifest binding differs"
            )
    elif private_sha256 is not None:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "completion refusal manifest binding differs"
        )
    expected = _strict_json(
        _completion_payload(
            route=route,
            marker_payload=marker_payload,
            readiness_payload=readiness_payload,
            private_payload=private_payload,
            report_payload=report_payload,
        ),
        canonical=True,
    )
    if completion != expected:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "completion state binding differs"
        )
    return report


def _open_existing_output_root(path: Path) -> PinnedOutputRoot:
    try:
        descriptor = _open_directory_nofollow(path)
        facts = os.fstat(descriptor)
        if stat.S_IMODE(facts.st_mode) != 0o700:
            raise OSError("output root mode differs")
        marker_payload = _read_small_at(descriptor, MARKER_NAME, mode=0o600)
    except (OSError, SelectionSufficiencyPrivateCohortFreezeRefusal) as exc:
        if "descriptor" in locals():
            os.close(descriptor)
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "completed output root is unavailable"
        ) from exc
    return PinnedOutputRoot(
        path=path,
        descriptor=descriptor,
        device=facts.st_dev,
        inode=facts.st_ino,
        marker_payload=marker_payload,
    )


def _completion_is_valid(
    path: Path,
    *,
    readiness_path: Path | None = None,
    allow_generated: bool = True,
) -> bool:
    if path.name != COMPLETION_NAME:
        return False
    output: PinnedOutputRoot | None = None
    try:
        output = _open_existing_output_root(path.parent)
        _validate_pinned_completion(
            output,
            readiness_path=readiness_path or path.parent.parent / "readiness" / "readiness.json",
            allow_generated=allow_generated,
        )
    except SelectionSufficiencyPrivateCohortFreezeRefusal:
        return False
    finally:
        if output is not None:
            output.close()
    return True


def _generated_nonce(case: str, order: str) -> bytes:
    return hashlib.sha256(f"{case}:{order}".encode("ascii")).digest()


def _run_generated_case(
    *,
    pattern: str,
    case: str,
    order: str,
    root: Path,
    nonce_provider: Callable[[str, str], bytes] = _generated_nonce,
    selector: Callable[
        [Mapping[str, Any]],
        tuple[str, vr38a.SelectionSufficiencyOutcome | None, str],
    ] = _apply_vr38a,
    after_marker: Callable[[ExecutionPaths], None] | None = None,
) -> dict[str, Any]:
    if pattern not in READINESS_PATTERNS or case not in CASES or order not in ORDERS:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[2], "generated condition differs"
        )
    root = root.resolve(strict=True)
    paths = ExecutionPaths(
        source=root / "source.json",
        readiness=root / "readiness" / "readiness.json",
        output_root=root / "output",
    )
    output = _make_marker(paths, generated=True)
    try:
        if after_marker is not None:
            after_marker(paths)
        output.assert_path_identity()
        marker_preceded_source = output.read(MARKER_NAME, mode=0o600) == output.marker_payload
        readiness, provider_calls, sleeper_calls, readiness_input_bytes = (
            _collect_generated_readiness(pattern)
        )
        readiness_payload = _readiness_certificate_bytes(readiness, generated=True)
        source_constructions = 0
        source_opens = 0
        vr38a_calls = 0
        source_bytes = 0
        cohort_written = False
        nonce_calls = 0
        private_payload: bytes | None = None
        commitment: str | None = None
        source_unchanged = True
        upstream_route: str | None = None
        if readiness.ready:
            if not marker_preceded_source:
                raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                    REFUSAL_ROUTES[8], "consumed marker did not precede source"
                )
            source = _build_generated_source(case, order)
            source_constructions = 1
            payload = vr38a._source_bytes(source)
            source_before = payload
            source_bytes = len(payload)
            _write_exclusive(paths.source, payload)
            loaded = _read_bound_source_once(
                paths.source,
                SourceBinding(
                    bytes=len(payload),
                    sha256=_sha256_bytes(payload),
                    schema_name=str(source["schema_name"]),
                    rows=len(source["entries"]),
                    mode=0o600,
                ),
            )
            source_opens = 1
            route, outcome, upstream_route = selector(loaded)
            vr38a_calls = 1
            source_unchanged = vr38a._source_bytes(loaded) == source_before
            if not source_unchanged:
                route = PRIVATE_ROUTES[1]
                outcome = None
            if outcome is not None:
                nonce = nonce_provider(case, order)
                nonce_calls = 1
                try:
                    private_manifest, commitment = _build_private_manifest(
                        outcome,
                        raw_source_sha256=_sha256_bytes(payload),
                        nonce=nonce,
                    )
                    _require_private_commitment(private_manifest, commitment)
                except SelectionSufficiencyPrivateCohortFreezeRefusal:
                    route = PRIVATE_ROUTES[1]
                    commitment = None
                else:
                    private_payload = _canonical_json_bytes(private_manifest)
                    cohort_written = True
        else:
            route = PRIVATE_ROUTES[1]
        report = _case_report(route=route, commitment=commitment, generated=True)
        report_payload = _canonical_json_bytes(report)
        completion_payload = _completion_payload(
            route=route,
            marker_payload=output.marker_payload,
            readiness_payload=readiness_payload,
            private_payload=private_payload,
            report_payload=report_payload,
        )
        output_bytes = sum(
            (
                len(output.marker_payload),
                len(readiness_payload),
                len(private_payload or b""),
                len(report_payload),
                len(completion_payload),
            )
        )
        _require_output_cap(output_bytes)
        readiness_bytes = _write_exclusive(paths.readiness, readiness_payload)
        if private_payload is not None:
            output.write(PRIVATE_MANIFEST_NAME, private_payload)
        output.write(REPORT_NAME, report_payload, mode=0o644)
        output.write(COMPLETION_NAME, completion_payload)
        replayed = _validate_pinned_completion(
            output,
            readiness_path=paths.readiness,
            allow_generated=True,
        )
        if replayed != report:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "generated completion replay differs"
            )
        output_names = [MARKER_NAME, REPORT_NAME, COMPLETION_NAME]
        if cohort_written:
            output_names.append(PRIVATE_MANIFEST_NAME)
        peak_output_bytes = readiness_bytes + sum(output.size(name) for name in output_names)
        return {
            "route": route,
            "VR38A_route": upstream_route,
            "readiness_ready": readiness.ready,
            "VR33A_calls": 1,
            "readiness_provider_calls": provider_calls,
            "readiness_sleeper_calls": sleeper_calls,
            "source_constructions": source_constructions,
            "source_content_opens": source_opens,
            "VR38A_calls": vr38a_calls,
            "cohort_file_writes": int(cohort_written),
            "nonce_provider_calls": nonce_calls,
            "source_unchanged": source_unchanged,
            "marker_preceded_source": marker_preceded_source,
            "input_bytes": readiness_input_bytes + source_bytes,
            "materialized_generated_input_bytes": source_bytes,
            "output_bytes": output_bytes,
            "peak_incremental_output_bytes": peak_output_bytes,
            "peak_materialized_case_bytes": source_bytes + peak_output_bytes,
            "report_sha256": _sha256_bytes(report_payload),
            "completion_sha256": _sha256_bytes(completion_payload),
        }
    finally:
        output.close()


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except SelectionSufficiencyPrivateCohortFreezeRefusal as exc:
        return exc.route
    raise SelectionSufficiencyPrivateCohortFreezeRefusal(
        REFUSAL_ROUTES[8], "direct refusal unexpectedly passed"
    )


def _raise_injected_crash(_path: Path) -> None:
    raise SelectionSufficiencyPrivateCohortFreezeRefusal(
        REFUSAL_ROUTES[4], "injected pre-write crash"
    )


def _run_direct_refusals(request: Mapping[str, Any], decision: Mapping[str, Any]) -> Counter[str]:
    routes: list[str] = []
    request_mutations = [
        ("schema_name", "wrong"),
        ("lane_id", "wrong"),
        ("status", "wrong"),
    ]
    for key, value in request_mutations:
        mutated = copy.deepcopy(request)
        mutated[key] = value
        routes.append(_expect_refusal(lambda m=mutated: _verify_authority_mapping(m, decision)))
    decision_mutations = [
        ("schema_name", "wrong"),
        ("lane_id", "wrong"),
        ("status", "wrong"),
    ]
    for key, value in decision_mutations:
        mutated = copy.deepcopy(decision)
        mutated[key] = value
        routes.append(_expect_refusal(lambda m=mutated: _verify_authority_mapping(request, m)))
    for key in THREAD_ENVIRONMENT:
        missing = dict(THREAD_ENVIRONMENT)
        del missing[key]
        routes.append(_expect_refusal(lambda m=missing: _validate_thread_environment(m)))
        wrong = dict(THREAD_ENVIRONMENT)
        wrong[key] = "2"
        routes.append(_expect_refusal(lambda m=wrong: _validate_thread_environment(m)))
    for index in range(125):
        routes.append(
            _expect_refusal(
                lambda i=index: _strict_json(
                    f'{{"duplicate":{i},"duplicate":{i + 1}}}\n'.encode("ascii")
                )
            )
        )
    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        routes.append(_expect_refusal(lambda k=key: _assert_aggregate_safe({k: "x"})))
    for index in range(24):
        routes.append(
            _expect_refusal(
                lambda i=index: _run_generated_case(
                    pattern="PPP",
                    case=f"unknown-{i}",
                    order="canonical",
                    root=Path("unused"),
                )
            )
        )
    for index in range(24):
        routes.append(
            _expect_refusal(
                lambda i=index: _run_generated_case(
                    pattern="PPP",
                    case=CASES[0],
                    order=f"unknown-{i}",
                    root=Path("unused"),
                )
            )
        )
    for index in range(24):
        routes.append(
            _expect_refusal(
                lambda i=index: _run_generated_case(
                    pattern=f"X{i}",
                    case=CASES[0],
                    order="canonical",
                    root=Path("unused"),
                )
            )
        )
    for pattern in DIRECT_NONPASSING_PATTERNS:
        result, provider_calls, sleeper_calls, _ = _collect_generated_readiness(pattern)
        if result.ready or provider_calls != 3 or sleeper_calls != 2:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "nonpassing readiness witness differs"
            )
    for route in ("unknown", "MARC2VR38A-R9", "MARC2VR38A-G9"):
        routes.append(_expect_refusal(lambda r=route: _map_vr38a_route(r)))
    routes.append(
        _expect_refusal(
            lambda: _storage_totals(
                [
                    {
                        "compressed_size": MAX_COMPRESSED_BYTES + 1,
                        "uncompressed_size": 1,
                    }
                ]
            )
        )
    )
    with tempfile.TemporaryDirectory(prefix="marc2-vr39p-refusals-") as temp:
        temp_root = Path(temp).resolve()
        for name in (
            "source.json",
            MARKER_NAME,
            "readiness.v0.json",
            PRIVATE_MANIFEST_NAME,
            REPORT_NAME,
            COMPLETION_NAME,
        ):
            target = temp_root / name
            routes.append(
                _expect_refusal(
                    lambda p=target: _write_exclusive(
                        p,
                        b"{}\n",
                        before_write=_raise_injected_crash,
                    )
                )
            )
            if target.exists():
                raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                    REFUSAL_ROUTES[8], "crash witness retained output"
                )
        routes.append(
            _expect_refusal(
                lambda: _write_exclusive(
                    temp_root / "short-write.json",
                    b"{}\n",
                    writer=lambda _descriptor, _view: 0,
                )
            )
        )
        symlink_parent = temp_root / "symlink-parent"
        symlink_parent.symlink_to(temp_root, target_is_directory=True)
        routes.append(
            _expect_refusal(
                lambda: _write_exclusive(
                    symlink_parent / "refused.json",
                    b"{}\n",
                )
            )
        )
    counts = Counter(routes)
    if len(routes) < 200 or any(route not in REFUSAL_ROUTES for route in routes):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "direct refusal coverage differs"
        )
    return counts


def _run_critical_refusal_witnesses(
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> tuple[Counter[str], Counter[str]]:
    route_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()

    def record(label: str, action: Callable[[], Any]) -> None:
        route_counts[_expect_refusal(action)] += 1
        class_counts[label] += 1

    def require_r1(result: Mapping[str, Any]) -> None:
        if result.get("route") != PRIVATE_ROUTES[0]:
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "critical witness correctly refused R1"
            )

    def require_completion(path: Path) -> None:
        if not _completion_is_valid(path):
            raise SelectionSufficiencyPrivateCohortFreezeRefusal(
                REFUSAL_ROUTES[8], "missing completion correctly refused"
            )

    mutated_request = copy.deepcopy(request)
    mutated_request["lane_id"] = "wrong"
    record(
        "authority_drift",
        lambda: _verify_authority_mapping(mutated_request, decision),
    )
    record(
        "strict_JSON_duplicate_key",
        lambda: _strict_json(b'{"a":1,"a":2}\n'),
    )
    record(
        "public_allowlist_extra_field",
        lambda: _assert_aggregate_safe({"row": "forbidden"}),
    )
    record(
        "combined_output_cap",
        lambda: _require_output_cap(MAX_OUTPUT_BYTES + 1),
    )
    record(
        "selected_storage_cap",
        lambda: _storage_totals(
            [{"compressed_size": MAX_COMPRESSED_BYTES + 1, "uncompressed_size": 1}]
        ),
    )
    with tempfile.TemporaryDirectory(prefix="marc2-vr39p-critical-") as temp:
        root = Path(temp).resolve()
        source = _build_generated_source("selected_12_public_map_exact", "canonical")
        outcome = vr38a.select_generated_source(source)
        manifest, commitment = _build_private_manifest(
            outcome,
            raw_source_sha256=_sha256_bytes(vr38a._source_bytes(source)),
            nonce=b"x" * PRIVATE_NONCE_BYTES,
        )
        malformed = copy.deepcopy(manifest)
        malformed["commitment"]["scheme"] = "wrong"
        record(
            "HMAC_envelope_corruption",
            lambda: _require_private_commitment(malformed, commitment),
        )
        record(
            "missing_completion_marker",
            lambda: require_completion(root / "missing" / COMPLETION_NAME),
        )
        record(
            "short_write",
            lambda: _write_exclusive(
                root / "short.json",
                b"{}\n",
                writer=lambda _descriptor, _view: 0,
            ),
        )
        record(
            "crash_before_write",
            lambda: _write_exclusive(
                root / "crash.json",
                b"{}\n",
                before_write=_raise_injected_crash,
            ),
        )

        def mutating_selector(candidate: Mapping[str, Any]):
            result = _apply_vr38a(candidate)
            candidate["entries"].append(dict(candidate["entries"][0]))
            return result

        mutation_root = root / "mutation"
        mutation_root.mkdir(mode=0o700)
        mutation_result = _run_generated_case(
            pattern="PPP",
            case="selected_12_public_map_exact",
            order="canonical",
            root=mutation_root,
            selector=mutating_selector,
        )
        record("source_mutation", lambda: require_r1(mutation_result))

        def replace_output(paths: ExecutionPaths) -> None:
            moved = paths.output_root.with_name("moved-output")
            paths.output_root.rename(moved)
            paths.output_root.mkdir(mode=0o700)

        replacement_root = root / "replacement"
        replacement_root.mkdir(mode=0o700)
        record(
            "output_root_replacement",
            lambda: _run_generated_case(
                pattern="PPP",
                case="selected_12_public_map_exact",
                order="canonical",
                root=replacement_root,
                after_marker=replace_output,
            ),
        )
        proof_root = root / "proof"
        proof_root.mkdir(mode=0o700)
        record("proof_closeout_absent", lambda: _require_green_implementation(proof_root))
    if any(count != 1 for count in class_counts.values()) or len(class_counts) != 12:
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "critical refusal witness coverage differs"
        )
    return route_counts, class_counts


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _zero_counters() -> dict[str, int]:
    return {
        "repository_dot_codex_work_operations": 0,
        "private_structural_source_stats_resolves_hashes_opens_reads_or_parses": 0,
        "consumed_private_lane_path_or_output_operations": 0,
        "archive_header_or_member_payload_operations": 0,
        "signal_event_channel_geometry_target_or_label_operations": 0,
        "derivative_cache_feature_split_or_NeuroToken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_or_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "MARC2_FW2_or_CIL1_operations": 0,
        "retry_rerun_resume_repair_fallback_or_substitution_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _assert_generated_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    peak_incremental_output_bytes: int,
    generated_input_bytes: int = 0,
    peak_materialized_case_bytes: int = 0,
) -> None:
    if (
        runtime_seconds < 0
        or runtime_seconds > MAX_GENERATED_RUNTIME_SECONDS
        or peak_rss_bytes < 0
        or peak_rss_bytes >= MAX_RSS_BYTES
        or peak_incremental_output_bytes > MAX_OUTPUT_BYTES
        or generated_input_bytes > MAX_MATERIALIZED_GENERATED_INPUT_BYTES
        or peak_materialized_case_bytes > MAX_MATERIALIZED_GENERATED_INPUT_BYTES + MAX_OUTPUT_BYTES
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[9], "generated resource cap exceeded"
        )


def qualify_generated(
    *,
    request: Mapping[str, Any] | None = None,
    decision: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the sole registered 168-path generated qualification."""

    started = clock()
    registered_request = dict(request or load_registered_request())
    registered_decision = dict(decision or load_registered_decision())
    _verify_authority_mapping(registered_request, registered_decision)
    _verify_decision_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered_request, registered_decision)
    _validate_thread_environment(environment)
    refusal_counts = _run_direct_refusals(registered_request, registered_decision)
    critical_refusal_counts, critical_witness_classes = _run_critical_refusal_witnesses(
        registered_request,
        registered_decision,
    )
    refusal_counts.update(critical_refusal_counts)
    route_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    replay_signatures: list[list[tuple[Any, ...]]] = []
    provider_calls = 0
    sleeper_calls = 0
    vr33a_calls = 0
    source_constructions = 0
    source_opens = 0
    vr38a_calls = 0
    cohort_writes = 0
    nonce_calls = 0
    source_mutations = 0
    marker_order_successes = 0
    generated_input_bytes = 0
    generated_output_bytes = 0
    peak_incremental_output_bytes = 0
    peak_materialized_case_bytes = 0
    with tempfile.TemporaryDirectory(prefix="marc2-vr39p-generated-") as temp:
        temp_root = Path(temp).resolve()
        for replay in range(REPLAYS):
            signature: list[tuple[Any, ...]] = []
            for order in ORDERS:
                for case in CASES:
                    for pattern in READINESS_PATTERNS:
                        with tempfile.TemporaryDirectory(
                            prefix=f"r{replay}-{order}-{case}-{pattern}-",
                            dir=temp_root,
                        ) as case_temp:
                            result = _run_generated_case(
                                pattern=pattern,
                                case=case,
                                order=order,
                                root=Path(case_temp),
                                nonce_provider=_generated_nonce,
                            )
                        route_counts[result["route"]] += 1
                        if result["VR38A_route"] is not None:
                            upstream_counts[result["VR38A_route"]] += 1
                        provider_calls += result["readiness_provider_calls"]
                        sleeper_calls += result["readiness_sleeper_calls"]
                        vr33a_calls += result["VR33A_calls"]
                        source_constructions += result["source_constructions"]
                        source_opens += result["source_content_opens"]
                        vr38a_calls += result["VR38A_calls"]
                        cohort_writes += result["cohort_file_writes"]
                        nonce_calls += result["nonce_provider_calls"]
                        source_mutations += int(not result["source_unchanged"])
                        marker_order_successes += int(result["marker_preceded_source"])
                        generated_input_bytes += result["input_bytes"]
                        generated_output_bytes += result["output_bytes"]
                        peak_incremental_output_bytes = max(
                            peak_incremental_output_bytes,
                            result["peak_incremental_output_bytes"],
                        )
                        peak_materialized_case_bytes = max(
                            peak_materialized_case_bytes,
                            result["peak_materialized_case_bytes"],
                        )
                        signature.append(
                            (
                                order,
                                case,
                                pattern,
                                result["route"],
                                result["VR38A_route"],
                                result["cohort_file_writes"],
                                result["report_sha256"],
                            )
                        )
            replay_signatures.append(signature)
    expected_routes = Counter(
        {
            PRIVATE_ROUTES[0]: 64,
            PRIVATE_ROUTES[1]: 104,
        }
    )
    expected_upstream = Counter(
        {
            "MARC2VR38A-G1": 36,
            "MARC2VR38A-G2": 32,
            "MARC2VR38A-R1": 8,
            "MARC2VR38A-R2": 4,
            "MARC2VR38A-R3": 4,
        }
    )
    if (
        vr33a_calls != 168
        or provider_calls != 504
        or sleeper_calls != 336
        or source_constructions != 84
        or source_opens != 84
        or vr38a_calls != 84
        or cohort_writes != 64
        or nonce_calls != 68
        or source_mutations != 0
        or marker_order_successes != 168
        or route_counts != expected_routes
        or upstream_counts != expected_upstream
        or replay_signatures[0] != replay_signatures[1]
    ):
        raise SelectionSufficiencyPrivateCohortFreezeRefusal(
            REFUSAL_ROUTES[8], "generated replay or call distribution differs"
        )
    runtime = clock() - started
    rss = peak_rss()
    _assert_generated_resources(
        runtime,
        rss,
        peak_incremental_output_bytes,
        generated_input_bytes,
        peak_materialized_case_bytes,
    )
    report: dict[str, Any] = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": QUALIFICATION_ROUTE,
        "status": "generated_selection_sufficiency_fixed_path_wrapper_qualified",
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "decision_base_job_id": GREEN_DECISION_BASE_JOB_ID,
            "decision_optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "request_sha256": REQUEST_SHA256,
            "decision_sha256": DECISION_SHA256,
        },
        "matrix": {
            "fixture_cases": list(CASES),
            "readiness_patterns": list(READINESS_PATTERNS),
            "orders": list(ORDERS),
            "replays": REPLAYS,
            "paths": 168,
            "VR33A_calls": vr33a_calls,
            "readiness_provider_calls": provider_calls,
            "readiness_sleeper_calls": sleeper_calls,
            "source_constructions": source_constructions,
            "source_content_opens": source_opens,
            "VR38A_calls": vr38a_calls,
            "cohort_file_writes": cohort_writes,
            "nonce_provider_calls": nonce_calls,
            "VR39P_route_counts": dict(sorted(route_counts.items())),
            "VR38A_route_counts": dict(sorted(upstream_counts.items())),
            "nonpassing_readiness_source_constructions": 0,
            "nonpassing_readiness_VR38A_calls": 0,
            "additional_nonpassing_readiness_patterns_tested": list(DIRECT_NONPASSING_PATTERNS),
            "exact_replays_match": True,
            "source_mutations_after_call": source_mutations,
            "fixed_path_state_machine_qualified": True,
            "marker_preceded_every_source_construction_and_open": (marker_order_successes == 168),
            "direct_refusals_passed": sum(refusal_counts.values()),
            "direct_refusal_route_counts": dict(sorted(refusal_counts.items())),
            "critical_refusal_witness_class_counts": dict(sorted(critical_witness_classes.items())),
        },
        "measurements": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes_written": generated_output_bytes,
            "peak_incremental_output_bytes": peak_incremental_output_bytes,
            "peak_materialized_case_bytes": peak_materialized_case_bytes,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": _zero_counters(),
        "warnings": [
            "generated_only_qualification",
            "no_repository_private_or_consumed_path_was_touched",
            "private_execution_remains_proof_gated",
            "no_real_cohort_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "real_selection_sufficiency_route_or_cohort",
            "private_count_difference_task_distribution_identity_or_row",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "generated exact-readiness and selection-sufficiency fixed-path cohort-freeze "
                "state machine"
            ),
            "scientific_ceiling": "none",
            "real_or_private_data_accessed": False,
            "real_cohort_established": False,
            "archive_member_accessed": False,
            "neural_payload_accessed": False,
            "target_model_prediction_or_score_accessed": False,
            "neural_effect": False,
            "decoding_performance_established": False,
            "language_or_thought_decoding": False,
            "unseen_person_generalization": False,
            "live_decoding": False,
        },
    }
    output_bytes = -1
    while report["measurements"].get("aggregate_output_bytes") != output_bytes:
        report["measurements"]["aggregate_output_bytes"] = output_bytes
        output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_aggregate_safe(report)
    return report


def _current_machine_sample(sequence: int) -> dict[str, Any]:
    logical_cpus = os.cpu_count() or 0
    one_minute_load = os.getloadavg()[0]
    rss = _peak_rss_bytes()
    free_disk = shutil.disk_usage(_repo_root()).free
    normalized = one_minute_load / logical_cpus if logical_cpus else None
    passing = (
        logical_cpus >= 1
        and normalized is not None
        and normalized <= 1.0
        and rss < MAX_RSS_BYTES
        and free_disk >= MINIMUM_FREE_DISK_BYTES
    )
    return {
        "sequence": sequence,
        "passing": passing,
        "observed_at_seconds": time.monotonic(),
        "available_bytes": free_disk,
    }


def execute_fixed() -> dict[str, Any]:
    """Execute the one fixed private confirmation after proof activation."""

    started = time.monotonic()
    implementation_commit = _require_green_implementation()
    request = load_registered_request()
    decision = load_registered_decision()
    _verify_authority_mapping(request, decision)
    _verify_decision_proof()
    _verify_fixed_inputs(request, decision)
    _validate_thread_environment()
    root = _repo_root()
    paths = ExecutionPaths(
        source=root / PRIVATE_SOURCE_RELATIVE_PATH,
        readiness=root / READINESS_RELATIVE_PATH,
        output_root=root / OUTPUT_ROOT_RELATIVE_PATH,
    )
    output = _make_marker(paths, generated=False)
    try:
        try:
            readiness = vr33a.collect_exact_readiness(_current_machine_sample, time.sleep)
            readiness_payload = _readiness_certificate_bytes(readiness, generated=False)
            route = PRIVATE_ROUTES[1]
            private_payload: bytes | None = None
            commitment: str | None = None
            if readiness.ready:
                binding = SourceBinding(
                    bytes=PRIVATE_SOURCE_BYTES,
                    sha256=PRIVATE_SOURCE_SHA256,
                    schema_name=PRIVATE_SOURCE_SCHEMA,
                    rows=1227,
                    mode=0o600,
                )
                source = _read_bound_source_once(
                    paths.source,
                    binding,
                    preflight=_preflight_bound_source(paths.source, binding),
                )
                route, outcome, _upstream_route = _apply_vr38a(source)
                if outcome is not None:
                    nonce = secrets.token_bytes(PRIVATE_NONCE_BYTES)
                    manifest, commitment = _build_private_manifest(
                        outcome,
                        raw_source_sha256=PRIVATE_SOURCE_SHA256,
                        nonce=nonce,
                    )
                    _require_private_commitment(manifest, commitment)
                    private_payload = _canonical_json_bytes(manifest)
            runtime = time.monotonic() - started
            if runtime > MAX_PRIVATE_RUNTIME_SECONDS or _peak_rss_bytes() >= MAX_RSS_BYTES:
                route = PRIVATE_ROUTES[1]
                private_payload = None
                commitment = None
            report = _case_report(
                route=route,
                commitment=commitment,
                generated=False,
                implementation_commit=implementation_commit,
            )
            report_payload = _canonical_json_bytes(report)
            completion_payload = _completion_payload(
                route=route,
                marker_payload=output.marker_payload,
                readiness_payload=readiness_payload,
                private_payload=private_payload,
                report_payload=report_payload,
            )
            total_output = sum(
                (
                    len(output.marker_payload),
                    len(readiness_payload),
                    len(private_payload or b""),
                    len(report_payload),
                    len(completion_payload),
                )
            )
            _require_output_cap(total_output)
            _write_exclusive(paths.readiness, readiness_payload)
            if private_payload is not None:
                output.write(PRIVATE_MANIFEST_NAME, private_payload)
            output.write(REPORT_NAME, report_payload, mode=0o644)
            output.write(COMPLETION_NAME, completion_payload)
            return _validate_pinned_completion(
                output,
                readiness_path=paths.readiness,
                allow_generated=False,
            )
        except Exception:  # noqa: BLE001 - terminal failures must collapse without detail.
            return _case_report(
                route=PRIVATE_ROUTES[1],
                commitment=None,
                generated=False,
                implementation_commit=implementation_commit,
            )
    finally:
        output.close()


def inspect_fixed() -> dict[str, Any]:
    """Inspect only the fixed aggregate report after proof activation."""

    implementation_commit = _require_green_implementation()
    root = _repo_root()
    output: PinnedOutputRoot | None = None
    try:
        output = _open_existing_output_root(root / OUTPUT_ROOT_RELATIVE_PATH)
        return _validate_pinned_completion(
            output,
            readiness_path=root / READINESS_RELATIVE_PATH,
            allow_generated=False,
        )
    except SelectionSufficiencyPrivateCohortFreezeRefusal:
        return _case_report(
            route=PRIVATE_ROUTES[1],
            commitment=None,
            generated=False,
            implementation_commit=implementation_commit,
        )
    finally:
        if output is not None:
            output.close()


def build_plan() -> dict[str, Any]:
    request = load_registered_request()
    decision = load_registered_decision()
    _verify_authority_mapping(request, decision)
    _verify_decision_proof()
    return {
        "schema_name": "neurodecodekit.marc2_selection_sufficiency_private_cohort_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "decision_green_generated_stage_open_private_stage_proof_gated",
        "generated_cases": list(CASES),
        "successful_cardinalities": list(range(12, 20)),
        "readiness_patterns": list(READINESS_PATTERNS),
        "source_orders": list(ORDERS),
        "exact_replays": REPLAYS,
        "generated_paths": 168,
        "VR33A_calls": 168,
        "readiness_provider_calls": 504,
        "readiness_sleeper_calls": 336,
        "VR38A_calls": 84,
        "generated_cohort_writes": 64,
        "route_counts": {PRIVATE_ROUTES[0]: 64, PRIVATE_ROUTES[1]: 104},
        "minimum_direct_refusals": 200,
        "private_invocation_limit_after_proof": 1,
        "private_source_bytes_after_proof_if_ready": PRIVATE_SOURCE_BYTES,
        "neural_payload_bytes": 0,
        "target_bytes": 0,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proof-gated MARC2 selection-sufficiency cohort confirmation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "qualify", "inspect", "execute"):
        subparsers.add_parser(command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        result = build_plan()
    elif args.command == "qualify":
        result = qualify_generated()
    elif args.command == "inspect":
        result = inspect_fixed()
    else:
        result = execute_fixed()
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
