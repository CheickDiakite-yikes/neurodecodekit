"""Proof-gated two-layer MARC2 structural diagnostic.

The generated qualification composes exact parser/producer fixtures and keeps
all real and Git-ignored paths closed. The fixed execute surface becomes
eligible only after its exact implementation commit and both CI jobs are
supplied through the shared proof validator.
"""

from __future__ import annotations

import argparse
import ast
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
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.datasets import marc2_dynamic_live_selection as vr6
from neurodecodekit.datasets import marc2_generated_diagnostic_relay as relay
from neurodecodekit.datasets import marc2_machine_readiness as readiness
from neurodecodekit.datasets import marc2_proof_record_recovery as proof_recovery


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR9P"
MODULE_NAME = "neurodecodekit.datasets.marc2_two_layer_private_diagnostic"
QUALIFICATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_two_layer_private_diagnostic_qualification"
)
RESULT_SCHEMA_NAME = "neurodecodekit.marc2_two_layer_private_diagnostic_result"
READINESS_SCHEMA_NAME = (
    "neurodecodekit.marc2_two_layer_private_diagnostic_readiness"
)
MARKER_SCHEMA_NAME = "neurodecodekit.marc2_two_layer_private_diagnostic_marker"
GENERATED_ROUTE = "MARC2VR9P-G1"
F03_RESULT_ROUTE = "MARC2VR9P-R1"
F04_RESULT_ROUTE = "MARC2VR9P-R2"
REFUSAL_ROUTES = tuple(f"MARC2VR9P-F{index:02d}" for index in range(1, 13))

DECISION_COMMIT = "4cdd3d386b6c2c16b5187e0854b2bcb1f673b45a"
DECISION_CI_RUN_ID = 31_993_388_608
DECISION_BASE_JOB_ID = 95_280_728_093
DECISION_OPTIONAL_JOB_ID = 95_280_728_134
DECISION_DOCUMENT_RELATIVE_PATH = Path(
    "docs/MARC_2_TWO_LAYER_PRIVATE_DIAGNOSTIC_AUTHORIZATION_DECISION.md"
)
DECISION_DOCUMENT_SHA256 = (
    "def3ac16bbd7686b216f5c890b009fee3e0a41dc09a17f56d624b2cb9a8a638a"
)
DECISION_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_two_layer_private_diagnostic_authorization_decision.v0.json"
)
DECISION_REGISTRY_SHA256 = (
    "a62ee8463b384aefbe8b562da47a3c7e53644c2a2b066932bcbaff3e3db12571"
)
DECISION_TEST_RELATIVE_PATH = Path(
    "tests/test_marc2_two_layer_private_diagnostic_authorization_decision.py"
)
DECISION_TEST_SHA256 = (
    "d95c7e9432aafbe82471a470dba5444ca73aa50b38afe9f0651b0f8d81f0ac46"
)
REQUEST_PACKET_RELATIVE_PATH = Path(
    "docs/MARC_2_TWO_LAYER_PRIVATE_DIAGNOSTIC_AUTHORIZATION_PACKET.md"
)
REQUEST_PACKET_SHA256 = (
    "e89da84ee3f615ec9e2739220ac2bc2cf68b195be38dac1c605482cd020e9ba4"
)
REQUEST_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_two_layer_private_diagnostic_authorization_request.v0.json"
)
REQUEST_REGISTRY_SHA256 = (
    "c5a576e5340d271dc8efe4f5cb52761136620d89ff1b4c2dc08c5c302f31b964"
)
REQUEST_TEST_RELATIVE_PATH = Path(
    "tests/test_marc2_two_layer_private_diagnostic_authorization_request.py"
)
REQUEST_TEST_SHA256 = (
    "5f5ff1075c960a3ad3688e18e2b1d56bf87655d20ea13754e74ac58137db57d1"
)

IMPLEMENTATION_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_two_layer_private_diagnostic_implementation.v0.json"
)
PROOF_RECORD_RELATIVE_PATH = Path(
    "registries/marc2_two_layer_private_diagnostic_proof.v0.json"
)
READINESS_CERTIFICATE_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr9p/readiness.v0.json"
)
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_two_layer_private_diagnostic/v0"
)
MARKER_NAME = "consumed_marker.v0.json"
AGGREGATE_REPORT_NAME = "two_layer_diagnostic.aggregate.v0.json"

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
MAX_COMBINED_OUTPUT_BYTES = 1024**2
MAX_TRACKED_ARTIFACT_BYTES = 2 * 1024**2
MAX_PROOF_BYTES = 1024**2
MAX_GENERATED_INPUT_BYTES = 32 * 1024**2
READ_CHUNK_BYTES = 64 * 1024
ALLOWED_NESTED_ROUTES = ("MARC2VR2-F03", "MARC2VR2-F04")
CASES = ("F03", "F04")
ORDERS = ("canonical", "reversed")
EXACT_REPLAYS = 2

FIXED_GREEN_ARTIFACTS = (
    (DECISION_DOCUMENT_RELATIVE_PATH, DECISION_DOCUMENT_SHA256),
    (DECISION_REGISTRY_RELATIVE_PATH, DECISION_REGISTRY_SHA256),
    (DECISION_TEST_RELATIVE_PATH, DECISION_TEST_SHA256),
    (REQUEST_PACKET_RELATIVE_PATH, REQUEST_PACKET_SHA256),
    (REQUEST_REGISTRY_RELATIVE_PATH, REQUEST_REGISTRY_SHA256),
    (REQUEST_TEST_RELATIVE_PATH, REQUEST_TEST_SHA256),
    (
        Path("src/neurodecodekit/datasets/marc2_generated_diagnostic_relay.py"),
        "162c5b15b0a4583001520fd6d70ade9ec4c64421f8c0f46f28607129ae94cc77",
    ),
    (
        Path("registries/marc2_generated_diagnostic_relay_implementation.v0.json"),
        "a466109f7558f879b87eb77abafad1d2c2890d6d06cc24f859b91ab5b4ace12e",
    ),
    (
        Path("registries/marc2_generated_diagnostic_relay_result.v0.json"),
        "b0e39cb127c3f96d11e606370f807ab2d96fbef03a74e2fed8637a668f60795c",
    ),
    (
        Path("src/neurodecodekit/datasets/marc2_dynamic_live_selection.py"),
        "c3b0d056891f7708b87e8027d36ebd14830055cdeac8e652a681dd4592b4a104",
    ),
    (
        Path("registries/marc2_dynamic_live_selection_contract.v0.json"),
        vr6.CONTRACT_SHA256,
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

FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "aiohttp",
        "httpx",
        "mne",
        "numpy",
        "requests",
        "scipy",
        "sklearn",
        "torch",
        "urllib3",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "candidate",
        "cohort",
        "crc32",
        "exception",
        "failed_value",
        "local_header_offset",
        "local_path",
        "member_name",
        "participant_id",
        "path",
        "predicate",
        "private_hash",
        "private_manifest",
        "reason",
        "rows",
        "run_id",
        "selection",
        "session_id",
        "source_hash",
        "subject_id",
    }
)
ZERO_FORBIDDEN_COUNTERS = {
    "consumed_path_or_executor_operations": 0,
    "archive_local_header_or_member_payload_reads": 0,
    "signal_sample_reads": 0,
    "event_onset_channel_geometry_target_label_or_quality_reads": 0,
    "derivative_cache_feature_split_or_NeuroToken_operations": 0,
    "training_or_parameter_update_fits": 0,
    "model_inference_or_prediction_sets": 0,
    "prediction_freezes_target_deliveries_or_scores": 0,
    "network_requests": 0,
    "network_bytes": 0,
    "provider_or_language_model_calls": 0,
    "RW3_stream_device_or_hardware_operations": 0,
    "MARC2_FW2_or_CIL1_operations": 0,
    "other_project_operations": 0,
    "release_publication_or_scientific_claim_upgrades": 0,
    "retry_rerun_resume_repair_fallback_or_substitution_operations": 0,
}
CLAIM_BOUNDARY = {
    "engineering_ceiling": "target_free_two_layer_structural_route_diagnostic",
    "scientific_ceiling": "none",
    "neural_effect": False,
    "decoding_accuracy": False,
    "brain_specific_origin": False,
    "language_or_thought_decoding": False,
    "unseen_person_generalization": False,
    "real_time_portable_home_assistive_or_clinical_result": False,
}


class TwoLayerDiagnosticRefusal(RuntimeError):
    """Fail closed while exposing only an allowlisted diagnostic code."""

    def __init__(
        self,
        route: str,
        safe_reason: str,
        *,
        outer_route: str | None = None,
        nested_route: str | None = None,
    ) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR9P refusal route")
        if outer_route is not None and outer_route != "MARC2VR6-F02":
            raise ValueError("unknown outer diagnostic route")
        if nested_route is not None and nested_route not in ALLOWED_NESTED_ROUTES:
            raise ValueError("unknown nested diagnostic route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason
        self.outer_route = outer_route
        self.nested_route = nested_route


@dataclass(frozen=True, slots=True)
class RegisteredFileIdentity:
    relative_path: Path
    mode: int
    bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    device: int
    inode: int
    mode: int
    size: int
    owner: int


@dataclass(frozen=True, slots=True)
class ExecutionProof:
    implementation_commit: str
    CI_run_id: int
    base_job_id: int
    optional_job_id: int
    proof_record_sha256: str
    proof_summary: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class SequenceOutcome:
    aggregate_report: Mapping[str, Any]
    aggregate_bytes: bytes
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
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[7], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, nested in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = nested
    return value


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _strict_json(payload: bytes, *, route: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise TwoLayerDiagnosticRefusal(route, "strict JSON parse refused") from exc
    if not isinstance(value, dict):
        raise TwoLayerDiagnosticRefusal(route, "JSON root is not an object")
    return value


def _validate_relative_path(value: str, *, allow_codex_work: bool = False) -> Path:
    if not value or value.startswith(("/", "~")) or "\\" in value:
        raise TwoLayerDiagnosticRefusal(REFUSAL_ROUTES[0], "relative path differs")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or pure.as_posix() != value
        or any(part in {"", ".", ".."} for part in pure.parts)
        or (not allow_codex_work and ".codex_work" in pure.parts)
    ):
        raise TwoLayerDiagnosticRefusal(REFUSAL_ROUTES[0], "relative path differs")
    return Path(*pure.parts)


def _read_small_regular(path: Path, maximum_bytes: int, route: str) -> bytes:
    try:
        before = path.lstat()
    except OSError as exc:
        raise TwoLayerDiagnosticRefusal(route, "tracked artifact unavailable") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise TwoLayerDiagnosticRefusal(route, "tracked artifact type differs")
    if before.st_size > maximum_bytes:
        raise TwoLayerDiagnosticRefusal(route, "tracked artifact cap exceeded")
    payload = bytearray()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or opened.st_size != before.st_size
            ):
                raise TwoLayerDiagnosticRefusal(
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
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except TwoLayerDiagnosticRefusal:
        raise
    except OSError as exc:
        raise TwoLayerDiagnosticRefusal(route, "tracked artifact read refused") from exc
    if (
        len(payload) != before.st_size
        or len(payload) > maximum_bytes
        or after.st_dev != before.st_dev
        or after.st_ino != before.st_ino
        or after.st_size != before.st_size
    ):
        raise TwoLayerDiagnosticRefusal(route, "tracked artifact size changed")
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
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[0], "tracked artifact hash differs"
        )
    return _strict_json(payload, route=REFUSAL_ROUTES[0])


def _validate_decision_mapping(decision: Mapping[str, Any]) -> None:
    authority = decision.get("authorization", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc2_two_layer_private_diagnostic_authorization_decision"
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "ddc5e8529f86d05d9f3edefb4595106e3959477f"
        or decision.get("user_authorization", {}).get("actual_message_verbatim")
        != "continue"
        or decision.get("user_authorization", {}).get("actual_message_SHA256")
        != "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad"
        or decision.get("green_request", {}).get("both_required_jobs_green") is not True
        or decision.get("green_proof_closeout", {}).get("both_required_jobs_green")
        is not True
        or authority.get("generated_mock_wrapper_implementation_after_decision_green")
        is not True
        or authority.get("one_private_structural_manifest_read_after_wrapper_green")
        is not True
        or authority.get("one_VR6_call_and_two_layer_route_report_after_wrapper_green")
        is not True
        or authority.get("cohort_freeze_authorized_by_this_decision") is not False
        or authority.get("MARC2_FW2_or_CIL1_real_execution_authorized_now") is not False
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[0], "green decision semantics differ"
        )


def _verify_green_inputs(root: Path) -> tuple[int, int]:
    total = 0
    for relative, expected_sha256 in FIXED_GREEN_ARTIFACTS:
        payload = _read_small_regular(
            root / relative, MAX_TRACKED_ARTIFACT_BYTES, REFUSAL_ROUTES[0]
        )
        if _sha256_bytes(payload) != expected_sha256:
            raise TwoLayerDiagnosticRefusal(
                REFUSAL_ROUTES[0], "green artifact identity differs"
            )
        total += len(payload)
    decision = _load_exact_json(
        root, DECISION_REGISTRY_RELATIVE_PATH, DECISION_REGISTRY_SHA256
    )
    _validate_decision_mapping(decision)
    return len(FIXED_GREEN_ARTIFACTS), total


def _validate_implementation_mapping(registry: Mapping[str, Any]) -> None:
    proof = registry.get("green_authorization_decision", {})
    surface = registry.get("implementation_surface", {})
    state = registry.get("private_execution_state", {})
    if (
        registry.get("schema_name")
        != "neurodecodekit.marc2_two_layer_private_diagnostic_implementation"
        or registry.get("schema_version") != SCHEMA_VERSION
        or registry.get("lane_id") != LANE_ID
        or registry.get("status")
        != "generated_mock_implementation_complete_private_sequence_not_executed"
        or proof.get("commit") != DECISION_COMMIT
        or proof.get("CI_run_id") != DECISION_CI_RUN_ID
        or proof.get("base_python_job_id") != DECISION_BASE_JOB_ID
        or proof.get("optional_neuro_job_id") != DECISION_OPTIONAL_JOB_ID
        or proof.get("both_required_jobs_green_before_implementation") is not True
        or surface.get("module") != MODULE_NAME
        or surface.get("commands") != ["plan", "qualify", "inspect", "execute"]
        or surface.get("generic_path_URL_threshold_retry_resume_or_fallback_argument")
        is not False
        or surface.get("consumed_executor_import_call_patch_copy_or_reuse") is not False
        or surface.get("private_manifest_or_cohort_output") is not False
        or state.get("registered_private_execution_limit") != 1
        or state.get("registered_private_execution_consumed") is not False
        or state.get("retry_rerun_resume_repair_or_fallback_limit") != 0
        or any(registry.get("implementation_access_counters", {}).values())
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[0], "implementation registry semantics differ"
        )


def load_implementation_registry(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate committed generated qualification metadata."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    payload = _read_small_regular(
        root / IMPLEMENTATION_REGISTRY_RELATIVE_PATH,
        MAX_TRACKED_ARTIFACT_BYTES,
        REFUSAL_ROUTES[0],
    )
    registry = _strict_json(payload, route=REFUSAL_ROUTES[0])
    _validate_implementation_mapping(registry)
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
        raise TwoLayerDiagnosticRefusal(
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
    """Bind one clean implementation HEAD to the shared proof record."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_implementation_registry(root)
    proof_bytes = _read_small_regular(
        root / PROOF_RECORD_RELATIVE_PATH, MAX_PROOF_BYTES, REFUSAL_ROUTES[0]
    )
    proof_sha256 = _sha256_bytes(proof_bytes)
    head = _git_output(root, ["rev-parse", "HEAD"])
    status = _git_output(root, ["status", "--porcelain", "--untracked-files=no"])
    if head != implementation_commit or status:
        raise TwoLayerDiagnosticRefusal(
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
        raise TwoLayerDiagnosticRefusal(
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
        raise TwoLayerDiagnosticRefusal(
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
            raise TwoLayerDiagnosticRefusal(route, "root path unavailable") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise TwoLayerDiagnosticRefusal(route, "root path component differs")
    return absolute


def _validate_parent_chain(root: Path, relative: Path, route: str) -> None:
    current = _absolute_directory(root, route)
    for component in relative.parts[:-1]:
        current = current / component
        try:
            info = current.lstat()
        except OSError as exc:
            raise TwoLayerDiagnosticRefusal(
                route, "registered parent unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise TwoLayerDiagnosticRefusal(route, "registered parent type differs")


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
        raise TwoLayerDiagnosticRefusal(route, "registered file unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise TwoLayerDiagnosticRefusal(route, "registered file type differs")
    if stat.S_IMODE(info.st_mode) != identity.mode:
        raise TwoLayerDiagnosticRefusal(route, "registered file mode differs")
    if info.st_uid != owner_reader():
        raise TwoLayerDiagnosticRefusal(route, "registered file owner differs")
    if info.st_size != identity.bytes:
        raise TwoLayerDiagnosticRefusal(route, "registered file size differs")
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
    payload = bytearray()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
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
                raise TwoLayerDiagnosticRefusal(
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
                raise TwoLayerDiagnosticRefusal(
                    route, "registered file exceeds exact size"
                )
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except TwoLayerDiagnosticRefusal:
        raise
    except OSError as exc:
        raise TwoLayerDiagnosticRefusal(
            route, "registered file content open refused"
        ) from exc
    if (
        len(payload) != identity.bytes
        or after.st_dev != snapshot.device
        or after.st_ino != snapshot.inode
        or after.st_size != snapshot.size
        or _sha256_bytes(payload) != identity.sha256
    ):
        raise TwoLayerDiagnosticRefusal(
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
                raise TwoLayerDiagnosticRefusal(route, "new parent tree differs")
        else:
            try:
                current.mkdir(mode=0o700)
            except OSError as exc:
                raise TwoLayerDiagnosticRefusal(
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
        raise TwoLayerDiagnosticRefusal(route, "output overwrite refused")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise TwoLayerDiagnosticRefusal(route, "exclusive output write refused") from exc
    info = path.lstat()
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != mode
        or info.st_size != len(payload)
    ):
        raise TwoLayerDiagnosticRefusal(route, "written output shape differs")


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _parse_utc(value: Any, route: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise TwoLayerDiagnosticRefusal(route, "UTC value differs")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise TwoLayerDiagnosticRefusal(route, "UTC value differs") from exc
    if parsed.tzinfo != timezone.utc:
        raise TwoLayerDiagnosticRefusal(route, "UTC offset differs")
    return parsed


def _thread_values(environ: Mapping[str, str]) -> dict[str, str | None]:
    return {name: environ.get(name) for name in THREAD_ENVIRONMENT}


def _validate_thread_environment(environ: Mapping[str, str]) -> None:
    if _thread_values(environ) != {name: "1" for name in THREAD_ENVIRONMENT}:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "one-thread environment differs"
        )


def _assess_samples(raw_samples: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    try:
        samples = [readiness._assess_raw_sample(row) for row in raw_samples]
        readiness._validate_sample_sequence(samples)
    except readiness.MachineReadinessRefusal as exc:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "machine sample sequence refused"
        ) from exc
    return samples


def _build_readiness_certificate(
    raw_samples: Sequence[Mapping[str, Any]],
    *,
    implementation_commit: str,
    thread_environment: Mapping[str, str | None],
) -> dict[str, Any]:
    samples = _assess_samples(raw_samples)
    started = _parse_utc(samples[0]["observed_at_UTC"], REFUSAL_ROUTES[1])
    finished = _parse_utc(samples[-1]["observed_at_UTC"], REFUSAL_ROUTES[1])
    wait_seconds = float(samples[-1]["monotonic_seconds"]) - float(
        samples[0]["monotonic_seconds"]
    )
    passing_tail = readiness._passing_tail(samples)
    threads_ok = thread_environment == {name: "1" for name in THREAD_ENVIRONMENT}
    ready = threads_ok and passing_tail >= readiness.CONSECUTIVE_PASSING_SAMPLES
    certificate = {
        "schema_name": READINESS_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "ready" if ready else "not_ready",
        "ready": ready,
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
            "consecutive_passing_tail": passing_tail,
            "wait_seconds": wait_seconds,
            "thread_environment": dict(thread_environment),
        },
        "claim_boundary": copy.deepcopy(readiness.CLAIM_BOUNDARY),
    }
    _validate_readiness_certificate(certificate, allow_not_ready=True)
    if len(_canonical_json_bytes(certificate)) > readiness.MAX_CERTIFICATE_BYTES:
        raise TwoLayerDiagnosticRefusal(
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
        "implementation_commit",
        "machine_contract_sha256",
        "started_at_UTC",
        "finished_at_UTC",
        "expires_at_UTC",
        "thresholds",
        "samples",
        "measurements",
        "claim_boundary",
    }
    samples = certificate.get("samples")
    measurements = certificate.get("measurements", {})
    if (
        set(certificate) != required
        or certificate.get("schema_name") != READINESS_SCHEMA_NAME
        or certificate.get("schema_version") != SCHEMA_VERSION
        or certificate.get("lane_id") != LANE_ID
        or certificate.get("machine_contract_sha256") != readiness.CONTRACT_SHA256
        or certificate.get("thresholds") != readiness.THRESHOLDS
        or certificate.get("claim_boundary") != readiness.CLAIM_BOUNDARY
        or not isinstance(samples, list)
        or not isinstance(measurements, Mapping)
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "readiness certificate shape differs"
        )
    raw_fields = readiness.SAMPLE_FIELDS - {
        "thresholds",
        "checks",
        "passing",
        "refusal_reasons",
    }
    if any(set(sample) != readiness.SAMPLE_FIELDS for sample in samples):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "readiness sample fields differ"
        )
    assessed = _assess_samples(
        [{key: sample[key] for key in raw_fields} for sample in samples]
    )
    if assessed != samples:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "readiness assessment differs"
        )
    passing_tail = readiness._passing_tail(samples)
    thread_values = measurements.get("thread_environment")
    ready = (
        thread_values == {name: "1" for name in THREAD_ENVIRONMENT}
        and passing_tail >= readiness.CONSECUTIVE_PASSING_SAMPLES
    )
    if (
        certificate.get("ready") is not ready
        or certificate.get("status") != ("ready" if ready else "not_ready")
        or measurements.get("sample_count") != len(samples)
        or measurements.get("consecutive_passing_tail") != passing_tail
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "readiness certificate values differ"
        )
    started = _parse_utc(certificate.get("started_at_UTC"), REFUSAL_ROUTES[1])
    finished = _parse_utc(certificate.get("finished_at_UTC"), REFUSAL_ROUTES[1])
    expires = _parse_utc(certificate.get("expires_at_UTC"), REFUSAL_ROUTES[1])
    if (
        started > finished
        or expires
        != finished + timedelta(seconds=readiness.CERTIFICATE_VALIDITY_SECONDS)
        or measurements.get("wait_seconds")
        != float(samples[-1]["monotonic_seconds"])
        - float(samples[0]["monotonic_seconds"])
        or measurements.get("wait_seconds", readiness.MAXIMUM_WAIT_SECONDS + 1)
        > readiness.MAXIMUM_WAIT_SECONDS
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "readiness timing differs"
        )
    if not ready and not allow_not_ready:
        raise TwoLayerDiagnosticRefusal(REFUSAL_ROUTES[1], "machine is not ready")
    if now_UTC is not None and (now_UTC < finished or now_UTC > expires):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "readiness certificate is not current"
        )


def _observe_machine(root: Path, sequence: int) -> dict[str, Any]:
    return readiness._raw_machine_sample(
        sequence=sequence,
        observed_at=datetime.now(timezone.utc),
        monotonic_seconds=time.monotonic(),
        logical_cpus=os.cpu_count(),
        one_minute_load=os.getloadavg()[0],
        peak_rss_bytes=_peak_rss_bytes(),
        free_disk_bytes=shutil.disk_usage(root).free,
    )


def _run_fresh_readiness(
    root: Path,
    *,
    implementation_commit: str,
    sampler: Callable[[Path, int], Mapping[str, Any]],
    sleeper: Callable[[float], None],
    environ: Mapping[str, str],
) -> tuple[dict[str, Any], bytes]:
    _validate_thread_environment(environ)
    certificate_parent = root / READINESS_CERTIFICATE_RELATIVE_PATH.parent
    if certificate_parent.exists() or certificate_parent.is_symlink():
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "fresh readiness parent is not absent"
        )
    raw_samples: list[Mapping[str, Any]] = []
    started_monotonic: float | None = None
    for sequence in range(1, readiness.MAXIMUM_SAMPLES + 1):
        raw = dict(sampler(root, sequence))
        if started_monotonic is None:
            started_monotonic = float(raw["monotonic_seconds"])
        raw_samples.append(raw)
        assessed = _assess_samples(raw_samples)
        elapsed = float(raw["monotonic_seconds"]) - started_monotonic
        if readiness._passing_tail(assessed) >= readiness.CONSECUTIVE_PASSING_SAMPLES:
            break
        if elapsed >= readiness.MAXIMUM_WAIT_SECONDS:
            break
        sleeper(readiness.MINIMUM_SAMPLE_INTERVAL_SECONDS)
    certificate = _build_readiness_certificate(
        raw_samples,
        implementation_commit=implementation_commit,
        thread_environment=_thread_values(environ),
    )
    certificate_bytes = _canonical_json_bytes(certificate)
    _ensure_parent_tree(
        root, READINESS_CERTIFICATE_RELATIVE_PATH.parent, REFUSAL_ROUTES[1]
    )
    _write_exclusive(
        root / READINESS_CERTIFICATE_RELATIVE_PATH,
        certificate_bytes,
        mode=0o600,
        route=REFUSAL_ROUTES[1],
    )
    if certificate["ready"] is not True:
        raise TwoLayerDiagnosticRefusal(REFUSAL_ROUTES[1], "machine is not ready")
    return certificate, certificate_bytes


def _pre_marker_machine_recheck(
    root: Path,
    *,
    environ: Mapping[str, str],
    rss_reader: Callable[[], int],
    disk_reader: Callable[[Path], int],
) -> None:
    _validate_thread_environment(environ)
    rss = rss_reader()
    disk = disk_reader(root)
    if (
        isinstance(rss, bool)
        or not isinstance(rss, int)
        or rss < 0
        or rss >= MAX_PEAK_RSS_BYTES
        or isinstance(disk, bool)
        or not isinstance(disk, int)
        or disk < MINIMUM_FREE_DISK_BYTES
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[1], "pre-marker machine recheck refused"
        )


def _create_new_output_root(root: Path) -> Path:
    output_root = root / OUTPUT_ROOT_RELATIVE_PATH
    if output_root.exists() or output_root.is_symlink():
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[3], "registered output root is not absent"
        )
    _ensure_parent_tree(root, OUTPUT_ROOT_RELATIVE_PATH.parent, REFUSAL_ROUTES[3])
    try:
        output_root.mkdir(mode=0o700)
    except OSError as exc:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[3], "registered output root creation refused"
        ) from exc
    return output_root


def _relay_exception(exc: Any) -> tuple[str, str]:
    if (
        getattr(exc, "route", None) != "MARC2VR6-F02"
        or getattr(exc, "upstream_route", None) not in ALLOWED_NESTED_ROUTES
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[6], "two-layer route is outside the frozen allowlist"
        )
    return str(exc.route), str(exc.upstream_route)


def _diagnose_source(
    source: Mapping[str, Any],
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[str, str]:
    before = relay.vr2._canonical_source_bytes(source)
    try:
        vr6.adapt_dynamic_live_source(
            source,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
    except vr6.DynamicLiveSelectionRefusal as exc:
        if relay.vr2._canonical_source_bytes(source) != before:
            raise TwoLayerDiagnosticRefusal(
                REFUSAL_ROUTES[6], "VR6 mutated a refused source"
            ) from None
        return _relay_exception(exc)
    raise TwoLayerDiagnosticRefusal(
        REFUSAL_ROUTES[6], "VR6 success is forbidden for this diagnostic"
    )


def _contains_private_public_value(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key).lower() in FORBIDDEN_PUBLIC_KEYS
            or _contains_private_public_value(nested)
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return any(_contains_private_public_value(nested) for nested in value)
    if isinstance(value, str):
        lowered = value.lower()
        return (
            ".codex_work" in lowered
            or "/users/" in lowered
            or lowered.startswith("sub-")
            or "/sub-" in lowered
            or "task-freewill" in lowered
        )
    return False


def _result_route(nested_route: str) -> str:
    if nested_route == "MARC2VR2-F03":
        return F03_RESULT_ROUTE
    if nested_route == "MARC2VR2-F04":
        return F04_RESULT_ROUTE
    raise TwoLayerDiagnosticRefusal(
        REFUSAL_ROUTES[6], "nested route is outside the frozen allowlist"
    )


def _operation_counters(
    *,
    real: bool,
    sample_count: int,
    source_input_bytes: int,
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
        f"{prefix}aggregate_reports": 1,
        **copy.deepcopy(ZERO_FORBIDDEN_COUNTERS),
    }


def _build_aggregate_report(
    *,
    proof: ExecutionProof,
    outer_route: str,
    nested_route: str,
    source_input_bytes: int,
    certificate: Mapping[str, Any],
    certificate_bytes: bytes,
    marker_bytes: bytes,
    runtime_seconds: float,
    peak_rss_bytes: int,
    real: bool,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_target_free_two_layer_structural_diagnostic",
        "route": _result_route(nested_route),
        "outer_VR6_route": outer_route,
        "nested_VR2_route": nested_route,
        "proof_posture": (
            "real_private_structural_metadata_only"
            if real
            else "generated_fixture_only_no_scientific_value"
        ),
        "green_evidence": {
            "implementation_commit": proof.implementation_commit,
            "CI_run_id": proof.CI_run_id,
            "base_python_job_id": proof.base_job_id,
            "optional_neuro_job_id": proof.optional_job_id,
            "proof_record_sha256": proof.proof_record_sha256,
        },
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "fresh_readiness_samples": len(certificate["samples"]),
            "fresh_readiness_wait_seconds": certificate["measurements"][
                "wait_seconds"
            ],
            "fresh_readiness_certificate_bytes": len(certificate_bytes),
            "marker_bytes": len(marker_bytes),
            "source_input_bytes": source_input_bytes,
            "aggregate_report_bytes": 0,
            "combined_output_bytes": len(certificate_bytes) + len(marker_bytes),
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
        "access_counters": _operation_counters(
            real=real,
            sample_count=len(certificate["samples"]),
            source_input_bytes=source_input_bytes,
        ),
        "warnings": [
            "The route is an aggregate structural refusal class, not a neural result.",
            "No reason, row, path, identity, selection, or cohort was retained.",
            "A later repair requires a separate prospective design and authorization.",
        ],
        "unavailable_fields": [
            "upstream reason predicate and failed value",
            "source rows member names paths offsets CRCs and private hashes",
            "participant session run companion selection and cohort identities",
            "archive payload signals events targets predictions and scores",
        ],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    for _ in range(8):
        payload = _canonical_json_bytes(report)
        combined = len(certificate_bytes) + len(marker_bytes) + len(payload)
        measurements = report["measurements"]
        if (
            measurements["aggregate_report_bytes"] == len(payload)
            and measurements["combined_output_bytes"] == combined
        ):
            break
        measurements["aggregate_report_bytes"] = len(payload)
        measurements["combined_output_bytes"] = combined
    validate_aggregate_report(report)
    return report


def validate_aggregate_report(report: Mapping[str, Any]) -> None:
    """Validate the exact route-only aggregate firewall."""

    required = {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "outer_VR6_route",
        "nested_VR2_route",
        "proof_posture",
        "green_evidence",
        "measurements",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    nested = report.get("nested_VR2_route")
    measurements = report.get("measurements", {})
    counters = report.get("access_counters", {})
    if (
        set(report) != required
        or report.get("schema_name") != RESULT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("status")
        != "completed_target_free_two_layer_structural_diagnostic"
        or report.get("outer_VR6_route") != "MARC2VR6-F02"
        or nested not in ALLOWED_NESTED_ROUTES
        or report.get("route") != _result_route(str(nested))
        or report.get("claim_boundary") != CLAIM_BOUNDARY
        or _contains_private_public_value(report)
        or not isinstance(measurements, Mapping)
        or not isinstance(counters, Mapping)
        or any(counters.get(key) != 0 for key in ZERO_FORBIDDEN_COUNTERS)
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[7], "aggregate privacy or route boundary differs"
        )
    _assert_resources(
        runtime_seconds=measurements.get("runtime_seconds"),
        peak_rss_bytes=measurements.get("peak_RSS_bytes"),
        generated_input_bytes=0,
        aggregate_output_bytes=measurements.get("aggregate_report_bytes"),
        combined_output_bytes=measurements.get("combined_output_bytes"),
        retained_output_bytes=0,
        maximum_runtime=MAX_REAL_RUNTIME_SECONDS,
    )


def _assert_resources(
    *,
    runtime_seconds: Any,
    peak_rss_bytes: Any,
    generated_input_bytes: Any,
    aggregate_output_bytes: Any,
    combined_output_bytes: Any,
    retained_output_bytes: Any,
    maximum_runtime: float,
) -> None:
    values = (
        (runtime_seconds, maximum_runtime),
        (peak_rss_bytes, MAX_PEAK_RSS_BYTES - 1),
        (generated_input_bytes, MAX_GENERATED_INPUT_BYTES),
        (aggregate_output_bytes, MAX_COMBINED_OUTPUT_BYTES),
        (combined_output_bytes, MAX_COMBINED_OUTPUT_BYTES),
        (retained_output_bytes, 0),
    )
    for value, maximum in values:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or value < 0
            or value > maximum
        ):
            raise TwoLayerDiagnosticRefusal(
                REFUSAL_ROUTES[8], "runtime RSS input output or retention cap refused"
            )


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
        "schema_name": MARKER_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_before_structural_content_open",
        "recorded_at_UTC": _format_utc(now_UTC()),
        "implementation_commit": proof.implementation_commit,
        "proof_record_sha256": proof.proof_record_sha256,
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
    outer_route, nested_route = _diagnose_source(
        source,
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    report = _build_aggregate_report(
        proof=proof,
        outer_route=outer_route,
        nested_route=nested_route,
        source_input_bytes=source_identity.bytes,
        certificate=certificate,
        certificate_bytes=certificate_bytes,
        marker_bytes=marker_bytes,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        real=real,
    )
    aggregate_bytes = _canonical_json_bytes(report)
    combined = len(certificate_bytes) + len(marker_bytes) + len(aggregate_bytes)
    _assert_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=source_identity.bytes if not real else 0,
        aggregate_output_bytes=len(aggregate_bytes),
        combined_output_bytes=combined,
        retained_output_bytes=0,
        maximum_runtime=(
            MAX_REAL_RUNTIME_SECONDS if real else MAX_GENERATED_RUNTIME_SECONDS
        ),
    )
    _write_exclusive(
        output_root / AGGREGATE_REPORT_NAME,
        aggregate_bytes,
        mode=0o644,
        route=REFUSAL_ROUTES[9],
    )
    output_files = tuple(sorted(path.name for path in output_root.iterdir()))
    expected = tuple(sorted((MARKER_NAME, AGGREGATE_REPORT_NAME)))
    if output_files != expected:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[9], "output inventory differs"
        )
    return SequenceOutcome(
        aggregate_report=report,
        aggregate_bytes=aggregate_bytes,
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
    """Run the sole fixed-path target-free structural diagnostic."""

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
        vr2_contract=relay.vr2.load_registered_contract(root),
        selector_contract=relay.selector.load_registered_contract(root),
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
        readiness._raw_machine_sample(
            sequence=index + 1,
            observed_at=base + timedelta(seconds=index * 5),
            monotonic_seconds=100.0 + index * 5.0,
            logical_cpus=12,
            one_minute_load=1.2,
            peak_rss_bytes=32 * 1024**2,
            free_disk_bytes=32 * 1024**3,
        )
        for index in range(3)
    ]


def _generated_proof() -> ExecutionProof:
    return ExecutionProof(
        implementation_commit="a" * 40,
        CI_run_id=1,
        base_job_id=2,
        optional_job_id=3,
        proof_record_sha256="b" * 64,
        proof_summary={"generated": True},
    )


def _write_generated_source(root: Path, source: Mapping[str, Any]) -> RegisteredFileIdentity:
    relative = Path("generated/source.private.v0.json")
    _ensure_parent_tree(root, relative.parent, REFUSAL_ROUTES[10])
    payload = relay.vr2._canonical_source_bytes(source)
    _write_exclusive(
        root / relative,
        payload,
        mode=0o600,
        route=REFUSAL_ROUTES[10],
    )
    return RegisteredFileIdentity(relative, 0o600, len(payload), _sha256_bytes(payload))


def _run_generated_path(
    case: str,
    order: str,
    *,
    repo_root: Path,
) -> tuple[dict[str, Any], int, int]:
    vr2_contract = relay.vr2.load_registered_contract(repo_root)
    selector_contract = relay.selector.load_registered_contract(repo_root)
    composed = relay._compose_source(
        case,
        order,
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    base = datetime(2026, 8, 17, 0, 0, tzinfo=timezone.utc)
    samples = _generated_raw_samples(base)
    sample_iter = iter(samples)
    clock_values = iter((10.0, 14.0))
    generated_parent = Path(tempfile.gettempdir()).resolve(strict=True)
    with tempfile.TemporaryDirectory(
        prefix="ndk-vr9p-generated-", dir=generated_parent
    ) as temporary:
        root = Path(temporary)
        identity = _write_generated_source(root, composed.source)
        outcome = _run_structural_sequence(
            root=root,
            proof=_generated_proof(),
            source_identity=identity,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
            sampler=lambda _root, _sequence: next(sample_iter),
            sleeper=lambda _seconds: None,
            environ={name: "1" for name in THREAD_ENVIRONMENT},
            now_UTC=lambda: base + timedelta(seconds=10),
            clock=lambda: next(clock_values),
            rss_reader=lambda: 64 * 1024**2,
            disk_reader=lambda _path: 32 * 1024**3,
            real=False,
        )
        summary = {
            "case": case,
            "order": order,
            "route": outcome.aggregate_report["route"],
            "outer_VR6_route": outcome.aggregate_report["outer_VR6_route"],
            "nested_VR2_route": outcome.aggregate_report["nested_VR2_route"],
            "source_input_bytes": identity.bytes,
            "aggregate_output_bytes": len(outcome.aggregate_bytes),
            "output_files": list(outcome.output_files),
        }
        generated_output_bytes = (
            len(outcome.certificate_bytes)
            + len(outcome.marker_bytes)
            + len(outcome.aggregate_bytes)
        )
    return summary, identity.bytes, generated_output_bytes


def _validate_module_surface() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    if imported & FORBIDDEN_IMPORT_ROOTS:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[10], "network or heavy import surface is forbidden"
        )
    consumed_module = "marc2_dynamic_" + "private_selection_recovery"
    if consumed_module in source:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[10], "consumed executor surface is forbidden"
        )


def _expect_refusal(name: str, callback: Callable[[], Any]) -> tuple[str, str]:
    try:
        callback()
    except TwoLayerDiagnosticRefusal as exc:
        return name, exc.route
    raise TwoLayerDiagnosticRefusal(
        REFUSAL_ROUTES[11], "required direct mutation did not refuse"
    )


def _mutate_mapping(
    source: Mapping[str, Any], path: Sequence[str], value: Any
) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    cursor: dict[str, Any] = changed
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return changed


def _run_direct_refusals(
    *,
    decision: Mapping[str, Any],
    implementation: Mapping[str, Any],
    valid_report: Mapping[str, Any],
) -> dict[str, str]:
    mutations: list[tuple[str, Callable[[], Any]]] = []

    decision_mutations = (
        (("schema_name",), "wrong"),
        (("lane_id",), "wrong"),
        (("authorization_parent_commit",), "0" * 40),
        (("user_authorization", "actual_message_verbatim"), "approve"),
        (("user_authorization", "actual_message_SHA256"), "0" * 64),
        (("green_request", "both_required_jobs_green"), False),
        (("green_proof_closeout", "both_required_jobs_green"), False),
        (
            (
                "authorization",
                "generated_mock_wrapper_implementation_after_decision_green",
            ),
            False,
        ),
        (
            (
                "authorization",
                "one_private_structural_manifest_read_after_wrapper_green",
            ),
            False,
        ),
        (("authorization", "cohort_freeze_authorized_by_this_decision"), True),
    )
    for index, (path, value) in enumerate(decision_mutations, start=1):
        changed = _mutate_mapping(decision, path, value)
        mutations.append(
            (
                f"decision_{index:02d}",
                lambda changed=changed: _validate_decision_mapping(changed),
            )
        )

    implementation_mutations = (
        (("schema_name",), "wrong"),
        (("schema_version",), "9.9.9"),
        (("lane_id",), "wrong"),
        (("status",), "wrong"),
        (("green_authorization_decision", "commit"), "0" * 40),
        (("green_authorization_decision", "CI_run_id"), 1),
        (("green_authorization_decision", "base_python_job_id"), 1),
        (("green_authorization_decision", "optional_neuro_job_id"), 1),
        (("green_authorization_decision", "both_required_jobs_green_before_implementation"), False),
        (("implementation_surface", "module"), "wrong"),
        (("implementation_surface", "commands"), ["plan"]),
        (("implementation_surface", "generic_path_URL_threshold_retry_resume_or_fallback_argument"), True),
        (("implementation_surface", "consumed_executor_import_call_patch_copy_or_reuse"), True),
        (("implementation_surface", "private_manifest_or_cohort_output"), True),
        (("private_execution_state", "registered_private_execution_limit"), 2),
        (("private_execution_state", "registered_private_execution_consumed"), True),
        (("private_execution_state", "retry_rerun_resume_repair_or_fallback_limit"), 1),
    )
    for index, (path, value) in enumerate(implementation_mutations, start=1):
        changed = _mutate_mapping(implementation, path, value)
        mutations.append(
            (
                f"implementation_{index:02d}",
                lambda changed=changed: _validate_implementation_mapping(changed),
            )
        )
    nonzero = copy.deepcopy(dict(implementation))
    first_counter = next(iter(nonzero["implementation_access_counters"]))
    nonzero["implementation_access_counters"][first_counter] = 1
    mutations.append(
        ("implementation_18", lambda: _validate_implementation_mapping(nonzero))
    )

    report_mutations = (
        (("schema_name",), "wrong"),
        (("schema_version",), "9.9.9"),
        (("lane_id",), "wrong"),
        (("status",), "wrong"),
        (("route",), F04_RESULT_ROUTE),
        (("outer_VR6_route",), "wrong"),
        (("nested_VR2_route",), "MARC2VR2-F02"),
        (("claim_boundary", "neural_effect"), True),
    )
    for index, (path, value) in enumerate(report_mutations, start=1):
        changed = _mutate_mapping(valid_report, path, value)
        mutations.append(
            (
                f"aggregate_{index:02d}",
                lambda changed=changed: validate_aggregate_report(changed),
            )
        )
    for index, key in enumerate(
        ("reason", "path", "member_name", "participant_id", "candidate", "cohort"),
        start=9,
    ):
        changed = copy.deepcopy(dict(valid_report))
        changed[key] = "hidden"
        mutations.append(
            (
                f"aggregate_{index:02d}",
                lambda changed=changed: validate_aggregate_report(changed),
            )
        )
    path_leak = copy.deepcopy(dict(valid_report))
    path_leak["warnings"] = [".codex_work/hidden"]
    mutations.append(
        ("aggregate_15", lambda: validate_aggregate_report(path_leak))
    )
    counter_leak = copy.deepcopy(dict(valid_report))
    counter_leak["access_counters"]["network_requests"] = 1
    mutations.append(
        ("aggregate_16", lambda: validate_aggregate_report(counter_leak))
    )

    relay_values = (
        SimpleNamespace(route="MARC2VR6-F01", upstream_route="MARC2VR2-F03"),
        SimpleNamespace(route="MARC2VR6-F02", upstream_route="MARC2VR2-F01"),
        SimpleNamespace(route="MARC2VR6-F02", upstream_route="MARC2VR2-F02"),
        SimpleNamespace(route="MARC2VR6-F02", upstream_route="MARC2VR2-F05"),
        SimpleNamespace(route="MARC2VR6-F02", upstream_route=None),
        SimpleNamespace(route=None, upstream_route="MARC2VR2-F03"),
    )
    for index, value in enumerate(relay_values, start=1):
        mutations.append(
            (f"relay_{index:02d}", lambda value=value: _relay_exception(value))
        )

    json_payloads = (
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
        b"[]",
        b"null",
        b"{",
        b"\xff",
    )
    for index, payload in enumerate(json_payloads, start=1):
        mutations.append(
            (
                f"json_{index:02d}",
                lambda payload=payload: _strict_json(
                    payload, route=REFUSAL_ROUTES[5]
                ),
            )
        )

    resource_values = (
        {"runtime_seconds": 31.0},
        {"runtime_seconds": -1.0},
        {"runtime_seconds": float("nan")},
        {"peak_rss_bytes": MAX_PEAK_RSS_BYTES},
        {"generated_input_bytes": MAX_GENERATED_INPUT_BYTES + 1},
        {"aggregate_output_bytes": MAX_COMBINED_OUTPUT_BYTES + 1},
        {"combined_output_bytes": MAX_COMBINED_OUTPUT_BYTES + 1},
        {"retained_output_bytes": 1},
    )
    resource_base = {
        "runtime_seconds": 1.0,
        "peak_rss_bytes": 1,
        "generated_input_bytes": 1,
        "aggregate_output_bytes": 1,
        "combined_output_bytes": 1,
        "retained_output_bytes": 0,
        "maximum_runtime": MAX_GENERATED_RUNTIME_SECONDS,
    }
    for index, changed_value in enumerate(resource_values, start=1):
        values = {**resource_base, **changed_value}
        mutations.append(
            (
                f"resource_{index:02d}",
                lambda values=values: _assert_resources(**values),
            )
        )

    mutations.extend(
        (
            ("path_01", lambda: _validate_relative_path("/absolute")),
            ("path_02", lambda: _validate_relative_path("../escape")),
            ("path_03", lambda: _validate_relative_path("a\\b")),
            ("path_04", lambda: _validate_relative_path(".codex_work/private")),
            ("thread_01", lambda: _validate_thread_environment({})),
            (
                "thread_02",
                lambda: _validate_thread_environment(
                    {name: ("2" if index == 0 else "1") for index, name in enumerate(THREAD_ENVIRONMENT)}
                ),
            ),
        )
    )
    if len(mutations) != 70:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[11], "direct mutation inventory differs"
        )
    return dict(_expect_refusal(name, callback) for name, callback in mutations)


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run the bounded generated F03/F04 matrix and refusal qualification."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    started = clock()
    _validate_thread_environment(environment or os.environ)
    _validate_module_surface()
    fixed_count, fixed_bytes = _verify_green_inputs(root)
    decision = _load_exact_json(
        root, DECISION_REGISTRY_RELATIVE_PATH, DECISION_REGISTRY_SHA256
    )
    implementation = load_implementation_registry(root)
    replay_summaries: list[list[dict[str, Any]]] = []
    generated_input_bytes = 0
    generated_output_bytes = 0
    for _replay in range(EXACT_REPLAYS):
        rows: list[dict[str, Any]] = []
        for case in CASES:
            for order in ORDERS:
                summary, input_bytes, output_bytes = _run_generated_path(
                    case, order, repo_root=root
                )
                rows.append(summary)
                generated_input_bytes += input_bytes
                generated_output_bytes += output_bytes
        replay_summaries.append(rows)
    if replay_summaries[0] != replay_summaries[1]:
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[9], "generated replay differs"
        )
    route_matrix = replay_summaries[0]
    valid_report = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_target_free_two_layer_structural_diagnostic",
        "route": F03_RESULT_ROUTE,
        "outer_VR6_route": "MARC2VR6-F02",
        "nested_VR2_route": "MARC2VR2-F03",
        "proof_posture": "generated_fixture_only_no_scientific_value",
        "green_evidence": {
            "implementation_commit": "a" * 40,
            "CI_run_id": 1,
            "base_python_job_id": 2,
            "optional_neuro_job_id": 3,
            "proof_record_sha256": "b" * 64,
        },
        "measurements": {
            "runtime_seconds": 1.0,
            "peak_RSS_bytes": 64 * 1024**2,
            "fresh_readiness_samples": 3,
            "fresh_readiness_wait_seconds": 10.0,
            "fresh_readiness_certificate_bytes": 1,
            "marker_bytes": 1,
            "source_input_bytes": 1,
            "aggregate_report_bytes": 1,
            "combined_output_bytes": 3,
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
        "access_counters": _operation_counters(
            real=False, sample_count=3, source_input_bytes=1
        ),
        "warnings": ["generated only"],
        "unavailable_fields": ["neural data"],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    validate_aggregate_report(valid_report)
    direct_refusals = _run_direct_refusals(
        decision=decision,
        implementation=implementation,
        valid_report=valid_report,
    )
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    report: dict[str, Any] = {
        "schema_name": QUALIFICATION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_generated_mock_only",
        "route": GENERATED_ROUTE,
        "route_matrix": route_matrix,
        "mechanics": {
            "cases": list(CASES),
            "orders": list(ORDERS),
            "exact_replays": EXACT_REPLAYS,
            "paths_per_replay": len(CASES) * len(ORDERS),
            "VR6_calls_per_path": 1,
            "VR6_calls_total": len(CASES) * len(ORDERS) * EXACT_REPLAYS,
            "strict_JSON_parses_total": len(CASES) * len(ORDERS) * EXACT_REPLAYS,
            "private_manifest_or_cohort_outputs": 0,
            "temporary_generated_output_removed": True,
        },
        "direct_refusals": direct_refusals,
        "measurements": {
            "fixed_committed_artifact_reads": fixed_count,
            "fixed_committed_input_bytes": fixed_bytes,
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes": generated_output_bytes,
            "retained_output_bytes": 0,
            "aggregate_output_bytes": 0,
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
        "acceptance_gates": {
            "green_decision_bound": True,
            "generated_F03_and_F04_canonical_and_reversed": True,
            "two_exact_replays_byte_identical": True,
            "exactly_one_VR6_call_per_path": True,
            "at_least_64_direct_refusals": len(direct_refusals) >= 64,
            "route_only_aggregate_firewall": True,
            "no_private_manifest_or_cohort_output": True,
            "one_thread_and_zero_forbidden_operations": True,
            "consumed_executor_not_imported_called_copied_or_modified": True,
        },
        "access_counters": {
            "real_readiness_or_certificate_operations": 0,
            "real_private_source_path_operations": 0,
            "real_private_output_root_marker_or_report_operations": 0,
            "real_structural_content_opens_or_bytes": 0,
            "real_VR6_adapter_calls": 0,
            "private_manifest_or_cohort_outputs": 0,
            **copy.deepcopy(ZERO_FORBIDDEN_COUNTERS),
        },
        "warnings": [
            "Generated F03 and F04 fixtures prove interface behavior only.",
            "No real or Git-ignored path was inspected by this qualification.",
            "The private F03 versus F04 observation remains unavailable until exact implementation proof is green.",
        ],
        "unavailable_fields": [
            "real nested structural route",
            "private reason row path identity value selection or cohort",
            "archive neural target prediction and score data",
        ],
        "next_gate": {
            "exact_implementation_commit_push_and_both_jobs_green_required": True,
            "private_diagnostic_may_begin_before_green": False,
            "one_private_diagnostic_after_green": True,
            "FW2_CIL1_payload_model_target_or_score_work_authorized": False,
        },
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    for _ in range(8):
        payload = _canonical_json_bytes(report)
        if report["measurements"]["aggregate_output_bytes"] == len(payload):
            break
        report["measurements"]["aggregate_output_bytes"] = len(payload)
    _assert_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=generated_input_bytes,
        aggregate_output_bytes=report["measurements"]["aggregate_output_bytes"],
        combined_output_bytes=report["measurements"]["aggregate_output_bytes"],
        retained_output_bytes=0,
        maximum_runtime=MAX_GENERATED_RUNTIME_SECONDS,
    )
    if (
        not all(report["acceptance_gates"].values())
        or any(report["access_counters"].values())
        or _contains_private_public_value(report)
    ):
        raise TwoLayerDiagnosticRefusal(
            REFUSAL_ROUTES[11], "generated qualification gate refused"
        )
    return report


def build_plan_summary() -> dict[str, Any]:
    """Describe the fixed proof order without touching ignored paths."""

    return {
        "schema_name": "neurodecodekit.marc2_two_layer_private_diagnostic_plan",
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
            "one_F03_or_F04_aggregate_report",
        ],
        "allowed_nested_routes": list(ALLOWED_NESTED_ROUTES),
        "private_manifest_or_cohort_output": False,
        "generic_path_URL_threshold_retry_resume_or_fallback_argument": False,
        "network_archive_signal_target_or_model_bytes": 0,
        "FW2_CIL1_neural_or_live_run_authorized": False,
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }


def build_inspection_summary() -> dict[str, Any]:
    """Inspect only committed implementation metadata."""

    registry = load_implementation_registry()
    return {
        "schema_name": (
            "neurodecodekit.marc2_two_layer_private_diagnostic_inspection"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": registry["status"],
        "generated_qualification": registry["generated_qualification"],
        "private_execution_consumed": registry["private_execution_state"][
            "registered_private_execution_consumed"
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
        "execute", help="run the one fixed-path structural diagnostic"
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
    except TwoLayerDiagnosticRefusal as exc:
        refusal: dict[str, Any] = {
            "lane_id": LANE_ID,
            "status": "refused",
            "route": exc.route,
            "retry_rerun_resume_limit": 0,
        }
        if exc.outer_route is not None and exc.nested_route is not None:
            refusal["outer_VR6_route"] = exc.outer_route
            refusal["nested_VR2_route"] = exc.nested_route
        print(json.dumps(refusal, sort_keys=True))
        return 2
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
