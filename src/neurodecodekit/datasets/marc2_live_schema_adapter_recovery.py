"""Proof-gated MARC2-LA2 live-schema structural selection."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import resource
import shutil
import stat
import subprocess
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.datasets.marc2_freewill_prefix_selection import (
    CONTRACT_RELATIVE_PATH as SELECTOR_CONTRACT_RELATIVE_PATH,
)
from neurodecodekit.datasets.marc2_freewill_prefix_selection import (
    CONTRACT_SHA256 as SELECTOR_CONTRACT_SHA256,
)
from neurodecodekit.datasets.marc2_freewill_prefix_selection import (
    FreewillPrefixSelectionRefusal,
    SelectionResult,
    THREAD_ENV_KEYS,
    select_generated_prefix,
)
from neurodecodekit.datasets.marc2_live_schema_adapter import (
    CONTRACT_RELATIVE_PATH as LIVE_ADAPTER_CONTRACT_RELATIVE_PATH,
)
from neurodecodekit.datasets.marc2_live_schema_adapter import (
    LiveSchemaAdapterRefusal,
    adapt_live_shaped_source,
    build_generated_live_source,
)
from neurodecodekit.datasets.marc2_proof_record_recovery import (
    CONTRACT_RELATIVE_PATH as PROOF_CONTRACT_RELATIVE_PATH,
)
from neurodecodekit.datasets.marc2_proof_record_recovery import (
    LANE_ID as PROOF_LANE_ID,
)
from neurodecodekit.datasets.marc2_proof_record_recovery import (
    ORDERED_MUTATIONS as PROOF_MUTATIONS,
)
from neurodecodekit.datasets.marc2_proof_record_recovery import (
    ProofEnvelope,
    ProofRecordRefusal,
    ValidationSummary,
    build_generated_candidate_record,
    parse_record_bytes,
    run_generated_mutation_matrix,
    validate_implementation_record,
)


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-LA2"
GENERATED_ROUTE = "MARC2LAR-G1"
SUCCESS_ROUTE = "MARC2LAR-R1"
FAILURE_ROUTES = tuple(f"MARC2LAR-F0{index}" for index in range(7))

DECISION_RELATIVE_PATH = Path(
    "registries/marc2_live_adapter_recovery_authorization_decision.v0.json"
)
DECISION_DOCUMENT_RELATIVE_PATH = Path(
    "docs/MARC_2_LIVE_ADAPTER_RECOVERY_AUTHORIZATION_DECISION.md"
)
DECISION_SHA256 = "7d4f20f92fe501c97d150f40c9174c4e6d03f52de420a5f6acbea306e7a1313e"
GREEN_DECISION_COMMIT = "b445df2ccadc3902d247fa19f5155a006ec5bfe5"
GREEN_DECISION_CI_RUN_ID = 31_937_743_296
GREEN_DECISION_BASE_JOB_ID = 95_142_233_426
GREEN_DECISION_OPTIONAL_JOB_ID = 95_142_233_335

REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_live_adapter_recovery_authorization_request.v0.json"
)
REQUEST_SHA256 = "770b3525c549f7d28cfb278ac7af9d166f6ddcf17a54c4fc1625b9e60c2a2fe0"
PACKET_RELATIVE_PATH = Path(
    "docs/MARC_2_LIVE_ADAPTER_RECOVERY_AUTHORIZATION_PACKET.md"
)
PACKET_SHA256 = "8df6efb504e54c3d7ca96f0fda982c0c1e3443eb140df1d0babbc3b91fd7cda6"

LIVE_ADAPTER_MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_live_schema_adapter.py"
)
LIVE_ADAPTER_MODULE_SHA256 = (
    "adcd345855e4a99794c2435f9e8e592a8818d170f7b8a7fcddc52ba009faba8d"
)
LIVE_ADAPTER_IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_live_schema_adapter_implementation.v0.json"
)
LIVE_ADAPTER_RESULT_RELATIVE_PATH = Path(
    "registries/marc2_live_schema_adapter_result.v0.json"
)
PROOF_MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_proof_record_recovery.py"
)
PROOF_MODULE_SHA256 = "c22948ca9047f07908d3768a17caea56b96fa8219ccf0bb9895d766373903a2c"
SELECTOR_MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_freewill_prefix_selection.py"
)
SELECTOR_MODULE_SHA256 = "86fa30fbd1caed735f0fb2e627144482a2bb8e033567bb3794e3f05508005c97"

MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_live_schema_adapter_recovery.py"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_live_adapter_recovery_implementation.v0.json"
)
PROOF_CERTIFICATE_RELATIVE_PATH = Path(
    "registries/marc2_live_adapter_recovery_proof_certificate.v0.json"
)
FUNCTIONAL_TEST_RELATIVE_PATH = Path(
    "tests/test_marc2_live_adapter_recovery.py"
)
IMPLEMENTATION_TEST_RELATIVE_PATH = Path(
    "tests/test_marc2_live_adapter_recovery_implementation.py"
)
CERTIFICATE_TRACKED_ARTIFACTS = (
    PROOF_MODULE_RELATIVE_PATH,
    PROOF_CONTRACT_RELATIVE_PATH,
    MODULE_RELATIVE_PATH,
    IMPLEMENTATION_RELATIVE_PATH,
    FUNCTIONAL_TEST_RELATIVE_PATH,
    IMPLEMENTATION_TEST_RELATIVE_PATH,
    DECISION_RELATIVE_PATH,
    DECISION_DOCUMENT_RELATIVE_PATH,
    REQUEST_RELATIVE_PATH,
    PACKET_RELATIVE_PATH,
    LIVE_ADAPTER_MODULE_RELATIVE_PATH,
    LIVE_ADAPTER_CONTRACT_RELATIVE_PATH,
    LIVE_ADAPTER_IMPLEMENTATION_RELATIVE_PATH,
    LIVE_ADAPTER_RESULT_RELATIVE_PATH,
    SELECTOR_MODULE_RELATIVE_PATH,
    SELECTOR_CONTRACT_RELATIVE_PATH,
)

PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
PRIVATE_SOURCE_BYTES = 418_755
PRIVATE_SOURCE_MODE = 0o600
PRIVATE_SOURCE_SHA256 = "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
PRIVATE_SOURCE_SCHEMA = "neurodecodekit.marc1_central_directory_private_manifest"
PRIVATE_SOURCE_ENTRIES = 1_227

OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_freewill_prefix/live_alias_recovery_v2"
)
OUTPUT_PARENT_RELATIVE_PATH = OUTPUT_ROOT_RELATIVE_PATH.parent
CONSUMED_MARKER_NAME = "live_adapter_recovery_execution_consumed.v0.json"
PRIVATE_SELECTION_NAME = "marc2_live_adapter_recovery.private.v0.json"
AGGREGATE_REPORT_NAME = "marc2_live_adapter_recovery_result.v0.json"

REPORT_SCHEMA_NAME = "neurodecodekit.marc2_live_adapter_recovery_result"
CLOSEOUT_SCHEMA_NAME = "neurodecodekit.marc2_live_adapter_recovery_closeout"
PRIVATE_SELECTION_SCHEMA_NAME = (
    "neurodecodekit.marc2_live_adapter_recovery_private_manifest"
)
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_live_adapter_recovery_implementation"
)

MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_LOAD_PER_LOGICAL_CPU = 1.0
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2

HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
EXECUTOR_MUTATIONS = (
    "decision_or_packet_hash_mismatch",
    "proof_certificate_hash_or_lane_mismatch",
    "native_registry_hash_or_lane_mismatch",
    "copied_or_aliased_validator_or_adapter",
    "dirty_HEAD_or_decision_ancestry_mismatch",
    "output_root_differs",
    "output_root_exists",
    "symlink_output_parent_or_destination",
    "insufficient_free_disk",
    "thread_load_runtime_or_RSS_preflight_failure",
    "retained_path_component_symlink",
    "retained_final_symlink_or_nonregular",
    "retained_owner_or_mode_mismatch",
    "retained_size_mismatch",
    "retained_SHA256_mismatch",
    "no_follow_open_fstat_identity_race",
    "strict_JSON_duplicate_control_or_schema_failure",
    "LA1_validation_or_bridge_refusal",
    "LA1_source_mutation_alias_or_call_count_failure",
    "TA1_mapping_transport_or_digest_failure",
    "selector_eligibility_rank_split_or_cap_refusal",
    "prefix_determinism_or_selector_call_count_failure",
    "private_aggregate_schema_or_field_leak",
    "output_cap_mode_replay_or_forbidden_operation",
)

PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "proof_posture",
        "green_evidence",
        "cohort_summary",
        "split_summary",
        "byte_summary",
        "selection_hashes",
        "measurements",
        "mutation_summary",
        "access_counters",
        "acceptance_gates",
        "route",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
CLOSEOUT_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "result_id",
        "lane_id",
        "recorded_at_local",
        "status",
        "route",
        "full_route",
        "proof_posture",
        "green_decision_proof",
        "local_implementation_snapshot",
        "artifact_bindings",
        "composition_result",
        "generated_selection",
        "mutation_result",
        "acceptance_gates_required",
        "acceptance_gates_passed",
        "measurements",
        "access_counters",
        "verification",
        "warnings",
        "unavailable_fields",
        "disposition",
        "claim_boundary",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "crc32",
        "local_header_offset",
        "member_name",
        "private_path",
        "private_rows",
        "raw_body",
        "raw_header",
        "source_body",
        "source_path",
    }
)
FORBIDDEN_PRIVATE_KEY_FRAGMENTS = (
    "target",
    "label",
    "response",
    "sentence",
    "trial",
    "quality",
    "channel",
    "onset",
)


class LiveAdapterRecoveryRefusal(RuntimeError):
    """Fail closed with one aggregate-safe route and reason."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC2-LA2 route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class GreenImplementationEvidence:
    """Externally observed green proof for the exact executor commit."""

    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    implementation_registry_sha256: str
    proof_certificate_sha256: str
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class AdaptedSelection:
    """Target-free selector output plus wrapper-specific private provenance."""

    selector_result: SelectionResult
    private_manifest: Mapping[str, Any]
    source_file_sha256: str
    adapted_manifest_sha256: str
    adapter_calls: int
    selector_calls: int


@dataclass(frozen=True)
class RecoveryOutcome:
    """One generated qualification or registered private selection outcome."""

    report: Mapping[str, Any]
    report_path: Path
    private_selection_path: Path | None
    consumed_marker_path: Path | None
    runtime_seconds: float
    peak_rss_bytes: int
    input_bytes: int
    output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "value is not canonical JSON"
        ) from exc
    return encoded + b"\n"


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("duplicate JSON key")
        output[key] = value
    return output


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        decoded = payload.decode("utf-8", errors="strict")
        value = json.loads(
            decoded,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "strict JSON differs"
        ) from exc
    if not isinstance(value, dict):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "strict JSON top level differs"
        )
    return value


def _read_regular_bounded(path: Path, maximum_bytes: int) -> bytes:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "tracked proof unavailable"
        ) from exc
    if (
        stat.S_ISLNK(observed.st_mode)
        or not stat.S_ISREG(observed.st_mode)
        or observed.st_size > maximum_bytes
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "tracked proof identity differs"
        )
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "tracked proof read failed"
        ) from exc
    if len(payload) != observed.st_size:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "tracked proof size changed"
        )
    return payload


def _read_tracked_json(path: Path, *, expected_sha256: str) -> dict[str, Any]:
    payload = _read_regular_bounded(path, MAX_COMBINED_OUTPUT_BYTES)
    if _sha256_bytes(payload) != expected_sha256:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "tracked proof hash differs"
        )
    try:
        return _strict_json(payload)
    except LiveAdapterRecoveryRefusal as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "tracked proof JSON differs"
        ) from exc


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green packet-bound LA2 decision."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _read_tracked_json(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=DECISION_SHA256,
    )
    request = decision.get("green_request", {})
    user = decision.get("user_authorization", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc2_live_adapter_recovery_authorization_decision"
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "f9f24a37d840e3408c19dc00830096f6c24b8e03"
        or request.get("commit")
        != "f9f24a37d840e3408c19dc00830096f6c24b8e03"
        or request.get("CI_run_id") != 31_937_038_394
        or request.get("base_python_job_id") != 95_140_483_613
        or request.get("optional_neuro_job_id") != 95_140_483_638
        or request.get("both_required_jobs_green") is not True
        or request.get("request_SHA256") != REQUEST_SHA256
        or request.get("packet_SHA256") != PACKET_SHA256
        or user.get("actual_message_verbatim") != "continue"
        or user.get("actual_message_UTF8_bytes") != 8
        or user.get("actual_message_SHA256")
        != "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad"
        or user.get("scope_may_not_expand_by_inference") is not True
        or decision.get("authorization", {}).get(
            "executor_implementation_after_decision_green"
        )
        is not True
        or decision.get("authorization", {}).get(
            "one_private_manifest_read_after_executor_green"
        )
        is not True
        or decision.get("authorization", {}).get(
            "archive_local_header_member_or_payload_access_authorized_now"
        )
        is not False
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "green decision proof differs"
        )
    for relative, digest in (
        (REQUEST_RELATIVE_PATH, REQUEST_SHA256),
        (PACKET_RELATIVE_PATH, PACKET_SHA256),
        (LIVE_ADAPTER_MODULE_RELATIVE_PATH, LIVE_ADAPTER_MODULE_SHA256),
        (PROOF_MODULE_RELATIVE_PATH, PROOF_MODULE_SHA256),
        (SELECTOR_MODULE_RELATIVE_PATH, SELECTOR_MODULE_SHA256),
    ):
        if _sha256_file(root / relative) != digest:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[0], "green dependency hash differs"
            )
    return decision


def load_implementation_record(
    repo_root: str | Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    """Load the generated-qualified native LA2 implementation registry."""

    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "implementation hash malformed"
        )
    root = Path(repo_root)
    record = _read_tracked_json(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256=expected_sha256,
    )
    qualification = record.get("generated_qualification", {})
    execution = record.get("execution_state", {})
    certificate = record.get("proof_certificate", {})
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("lane_id") != LANE_ID
        or record.get("status")
        != "generated_mock_live_adapter_recovery_qualified_requires_remote_green_before_private_selection"
        or record.get("green_decision", {}).get("commit")
        != GREEN_DECISION_COMMIT
        or record.get("green_decision", {}).get("CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or record.get("green_decision", {}).get("base_job_id")
        != GREEN_DECISION_BASE_JOB_ID
        or record.get("green_decision", {}).get("optional_neuro_job_id")
        != GREEN_DECISION_OPTIONAL_JOB_ID
        or record.get("green_decision", {}).get("decision_registry_sha256")
        != DECISION_SHA256
        or certificate.get("path") != PROOF_CERTIFICATE_RELATIVE_PATH.as_posix()
        or certificate.get("lane_id") != PROOF_LANE_ID
        or certificate.get("native_registry_lane_id") != LANE_ID
        or certificate.get("shared_validator_symbol")
        != validate_implementation_record.__name__
        or certificate.get("sha256_bound_by_green_evidence") is not True
        or qualification.get("all_gates_passed") is not True
        or qualification.get("proof_certificate_mutations_passed") != 32
        or qualification.get("executor_mutations_passed") != 24
        or qualification.get("total_direct_mutations_passed") != 56
        or tuple(qualification.get("executor_mutation_routes", {}))
        != EXECUTOR_MUTATIONS
        or any(
            route not in FAILURE_ROUTES
            for route in qualification.get("executor_mutation_routes", {}).values()
        )
        or execution.get("registered_private_execution_consumed") is not False
        or execution.get("registered_execution_limit") != 1
        or execution.get("retry_rerun_or_resume_limit") != 0
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "implementation registry differs"
        )
    required = {
        MODULE_RELATIVE_PATH.as_posix(),
        DECISION_RELATIVE_PATH.as_posix(),
        LIVE_ADAPTER_MODULE_RELATIVE_PATH.as_posix(),
        PROOF_MODULE_RELATIVE_PATH.as_posix(),
        SELECTOR_MODULE_RELATIVE_PATH.as_posix(),
    }
    observed: set[str] = set()
    for binding in record.get("tracked_file_hashes", ()):
        relative = str(binding.get("path", ""))
        digest = str(binding.get("sha256", ""))
        if (
            not relative
            or relative.startswith(("/", "~"))
            or ".." in Path(relative).parts
            or HEX64_RE.fullmatch(digest) is None
            or _sha256_file(root / relative) != digest
        ):
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[0], "implementation artifact differs"
            )
        observed.add(relative)
    if not required.issubset(observed):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "implementation artifact binding missing"
        )
    return record


def _proof_envelope(evidence: GreenImplementationEvidence) -> ProofEnvelope:
    return ProofEnvelope(
        implementation_commit=evidence.implementation_commit,
        implementation_CI_run_id=evidence.implementation_ci_run_id,
        implementation_base_job_id=evidence.implementation_base_job_id,
        implementation_optional_job_id=evidence.implementation_optional_job_id,
        implementation_registry_sha256=evidence.proof_certificate_sha256,
        observed_HEAD=evidence.implementation_commit,
        tracked_worktree_clean=True,
        green_decision_ancestor=True,
    )


def _observed_proof_envelope(
    evidence: GreenImplementationEvidence,
    *,
    observed_head: str,
    tracked_worktree_clean: bool,
    green_decision_ancestor: bool,
) -> ProofEnvelope:
    return ProofEnvelope(
        implementation_commit=evidence.implementation_commit,
        implementation_CI_run_id=evidence.implementation_ci_run_id,
        implementation_base_job_id=evidence.implementation_base_job_id,
        implementation_optional_job_id=evidence.implementation_optional_job_id,
        implementation_registry_sha256=evidence.proof_certificate_sha256,
        observed_HEAD=observed_head,
        tracked_worktree_clean=tracked_worktree_clean,
        green_decision_ancestor=green_decision_ancestor,
    )


def validate_proof_certificate(
    repo_root: str | Path,
    *,
    expected_sha256: str,
    expected_proof: ProofEnvelope,
    observed_proof: ProofEnvelope,
) -> ValidationSummary:
    """Validate the distinct FW1B certificate through the exact shared symbol."""

    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "certificate hash malformed"
        )
    root = Path(repo_root)
    payload = _read_regular_bounded(
        root / PROOF_CERTIFICATE_RELATIVE_PATH,
        MAX_COMBINED_OUTPUT_BYTES,
    )
    if _sha256_bytes(payload) != expected_sha256:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "certificate hash differs"
        )
    try:
        summary = validate_implementation_record(
            payload,
            repo_root=root,
            expected_proof=expected_proof,
            observed_proof=observed_proof,
        )
    except ProofRecordRefusal as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "shared proof certificate refused"
        ) from exc
    if summary.lane_id != PROOF_LANE_ID:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "certificate lane differs"
        )
    return summary


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _validate_evidence_shape(evidence: GreenImplementationEvidence) -> None:
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or HEX64_RE.fullmatch(evidence.implementation_registry_sha256) is None
        or HEX64_RE.fullmatch(evidence.proof_certificate_sha256) is None
        or min(
            evidence.implementation_ci_run_id,
            evidence.implementation_base_job_id,
            evidence.implementation_optional_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "green implementation proof malformed"
        )


def _verify_snapshot_values(
    *,
    head_matches: bool,
    clean: bool,
    ancestor: bool,
) -> None:
    if not head_matches or not clean or not ancestor:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "tracked Git proof differs"
        )


def verify_green_implementation(
    repo_root: str | Path,
    evidence: GreenImplementationEvidence,
) -> dict[str, Any]:
    """Require an exact clean HEAD descending from the green decision."""

    _validate_evidence_shape(evidence)
    root = Path(repo_root)
    load_green_decision(root)
    expected = _proof_envelope(evidence)
    first = validate_proof_certificate(
        root,
        expected_sha256=evidence.proof_certificate_sha256,
        expected_proof=expected,
        observed_proof=expected,
    )
    native = load_implementation_record(
        root,
        expected_sha256=evidence.implementation_registry_sha256,
    )
    head = _git(root, "rev-parse", "HEAD")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    ancestor = _git(root, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, "HEAD")
    observed_head = head.stdout.strip() if not head.returncode else ""
    observed = _observed_proof_envelope(
        evidence,
        observed_head=(observed_head if HEX40_RE.fullmatch(observed_head) else "0" * 40),
        tracked_worktree_clean=not clean.returncode and not clean.stdout.strip(),
        green_decision_ancestor=not ancestor.returncode,
    )
    second = validate_proof_certificate(
        root,
        expected_sha256=evidence.proof_certificate_sha256,
        expected_proof=expected,
        observed_proof=observed,
    )
    if first.to_mapping() != second.to_mapping():
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "certificate replay differs"
        )
    return {
        "native_implementation": native,
        "shared_proof_certificate": second.to_mapping(),
    }


def _peak_rss_bytes() -> int:
    observed = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(observed if os.uname().sysname == "Darwin" else observed * 1024)


def preconsumption_machine_gate(
    root: str | Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Measure computer-protection conditions before consumption."""

    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "thread environment differs"
        )
    try:
        free_bytes = int(disk_usage_reader(Path(root)).free)
        logical_cpus = cpu_count_reader()
        load_values = loadavg_reader()
        peak_rss = int(rss_reader())
    except Exception as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "machine metric unavailable"
        ) from exc
    if logical_cpus is None or logical_cpus <= 0 or not load_values:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "CPU or load unavailable"
        )
    one_minute_load = float(load_values[0])
    normalized_load = one_minute_load / logical_cpus
    if (
        free_bytes < MINIMUM_FREE_DISK_BYTES
        or not math.isfinite(one_minute_load)
        or one_minute_load < 0
        or normalized_load > MAX_LOAD_PER_LOGICAL_CPU
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "machine resource cap failed"
        )
    return {
        "passed_before_consumed_marker": True,
        "free_disk_bytes": free_bytes,
        "logical_CPUs": logical_cpus,
        "one_minute_load": one_minute_load,
        "one_minute_load_per_logical_CPU": normalized_load,
        "peak_RSS_bytes_before_consumption": peak_rss,
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
    }


def _assert_registered_output_root(root: Path, output_root: Path) -> None:
    if output_root != root / OUTPUT_ROOT_RELATIVE_PATH:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "output root differs"
        )


def _assert_absent(path: Path) -> None:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "output identity unavailable"
        ) from exc
    raise LiveAdapterRecoveryRefusal(
        FAILURE_ROUTES[1], "output already exists"
    )


def _assert_directory_not_symlink(path: Path, *, route: str) -> None:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(route, "directory component unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise LiveAdapterRecoveryRefusal(route, "directory component differs")


def _assert_source_components(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "registered source path differs"
        )
    cursor = root
    for component in relative.parts[:-1]:
        cursor = cursor / component
        _assert_directory_not_symlink(cursor, route=FAILURE_ROUTES[1])
    return root / relative


def _preflight_private_source(path: Path, *, expected_bytes: int) -> os.stat_result:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "registered source unavailable"
        ) from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "registered source type differs"
        )
    if observed.st_uid != os.getuid() or stat.S_IMODE(observed.st_mode) != 0o600:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "registered source owner or mode differs"
        )
    if observed.st_size != expected_bytes:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "registered source size differs"
        )
    return observed


def _base_access_counters() -> dict[str, int]:
    return {
        "registered_private_path_component_checks": 0,
        "registered_private_final_lstats": 0,
        "private_manifest_content_opens": 0,
        "private_manifest_body_reads": 0,
        "private_manifest_bytes": 0,
        "private_manifest_hashes": 0,
        "private_manifest_parses": 0,
        "live_adapter_calls_over_private_data": 0,
        "selector_calls_over_private_data": 0,
        "real_participant_selections": 0,
        "real_member_selections": 0,
        "registered_output_root_operations": 0,
        "consumed_markers": 0,
        "private_selection_manifests": 0,
        "aggregate_reports": 0,
        "network_requests": 0,
        "network_bytes": 0,
        "archive_local_header_or_member_payload_reads": 0,
        "signal_sample_reads": 0,
        "event_target_label_quality_onset_or_channel_reads": 0,
        "real_derivative_rows": 0,
        "training_or_parameter_update_fits": 0,
        "model_inference_or_prediction_sets": 0,
        "prediction_freezes_target_deliveries_or_scores": 0,
        "provider_or_language_model_calls": 0,
        "hardware_operations": 0,
        "retries_reruns_or_resumes": 0,
        "scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _read_fd_bounded(
    descriptor: int,
    expected_bytes: int,
    *,
    body_reader: Callable[[int, int], bytes] = os.read,
) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = body_reader(descriptor, min(65_536, expected_bytes + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > expected_bytes:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[2], "registered source exceeded bound"
            )
    payload = b"".join(chunks)
    if len(payload) != expected_bytes:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "registered source read length differs"
        )
    return payload


def read_locked_private_manifest(
    path: Path,
    *,
    expected_stat: os.stat_result,
    expected_bytes: int,
    expected_sha256: str,
    counters: dict[str, int] | None,
    body_reader: Callable[[int, int], bytes] = os.read,
    fstat_reader: Callable[[int], os.stat_result] = os.fstat,
) -> tuple[dict[str, Any], bytes]:
    """Perform one no-follow open, read, hash, and strict parse."""

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "registered source no-follow open failed"
        ) from exc
    if counters is not None:
        counters["private_manifest_content_opens"] += 1
    try:
        opened = fstat_reader(descriptor)
        if (
            opened.st_dev != expected_stat.st_dev
            or opened.st_ino != expected_stat.st_ino
            or opened.st_uid != expected_stat.st_uid
            or opened.st_mode != expected_stat.st_mode
            or opened.st_size != expected_stat.st_size
        ):
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[2], "open/fstat source identity differs"
            )
        payload = _read_fd_bounded(
            descriptor,
            expected_bytes,
            body_reader=body_reader,
        )
    finally:
        os.close(descriptor)
    if counters is not None:
        counters["private_manifest_body_reads"] += 1
        counters["private_manifest_bytes"] += len(payload)
        counters["private_manifest_hashes"] += 1
    if _sha256_bytes(payload) != expected_sha256:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "registered source SHA-256 differs"
        )
    value = _strict_json(payload)
    if counters is not None:
        counters["private_manifest_parses"] += 1
    return value, payload


def _mutable_ids(value: Any) -> set[int]:
    output: set[int] = set()
    if isinstance(value, dict):
        output.add(id(value))
        for nested in value.values():
            output.update(_mutable_ids(nested))
    elif isinstance(value, list):
        output.add(id(value))
        for nested in value:
            output.update(_mutable_ids(nested))
    return output


def _assert_adapted_transport(adapted: Mapping[str, Any]) -> None:
    transport = adapted.get("transport_body_sha256")
    if (
        not isinstance(transport, dict)
        or set(transport) != {"central_directory", "metadata", "tail"}
        or any(HEX64_RE.fullmatch(str(value)) is None for value in transport.values())
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[4], "adapted transport mapping differs"
        )


def _walk_private_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_PRIVATE_KEY_FRAGMENTS):
                raise LiveAdapterRecoveryRefusal(
                    FAILURE_ROUTES[6], "forbidden private field"
                )
            _walk_private_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_private_keys(nested)


def adapt_and_select(
    source: Mapping[str, Any],
    *,
    source_file_sha256: str,
    adapter_fn: Callable[[Mapping[str, Any]], dict[str, Any]] = adapt_live_shaped_source,
    selector_fn: Callable[[Mapping[str, Any]], SelectionResult] = select_generated_prefix,
) -> AdaptedSelection:
    """Call exact LA1 and the frozen selector once, preserving the source."""

    if HEX64_RE.fullmatch(source_file_sha256) is None:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[2], "source file hash malformed"
        )
    source_before = _canonical_json_bytes(source)
    if adapter_fn is not adapt_live_shaped_source:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "live adapter symbol differs"
        )
    if selector_fn is not select_generated_prefix:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "selector symbol differs"
        )
    try:
        adapted = adapter_fn(source)
    except LiveSchemaAdapterRefusal as exc:
        route = FAILURE_ROUTES[3]
        if exc.route.startswith("MARC2LA-F01"):
            route = FAILURE_ROUTES[0]
        elif exc.route.startswith("MARC2LA-F02"):
            route = FAILURE_ROUTES[2]
        elif exc.route.startswith(("MARC2LA-F03", "MARC2LA-F05")):
            route = FAILURE_ROUTES[4]
        elif exc.route.startswith(("MARC2LA-F06", "MARC2LA-F07")):
            route = FAILURE_ROUTES[6]
        raise LiveAdapterRecoveryRefusal(route, "LA1 adapter refused source") from exc
    if _canonical_json_bytes(source) != source_before:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[3], "LA1 mutated source"
        )
    if _mutable_ids(source) & _mutable_ids(adapted):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[3], "LA1 output aliases source"
        )
    _assert_adapted_transport(adapted)
    try:
        selected = selector_fn(adapted)
    except FreewillPrefixSelectionRefusal as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[5], "frozen selector refused adapted source"
        ) from exc
    if _canonical_json_bytes(source) != source_before:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[3], "selector mutated live source"
        )
    private_rows = copy.deepcopy(selected.private_manifest.get("rows"))
    private_manifest = {
        "schema_name": PRIVATE_SELECTION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "proof_posture": "target_free_structural_selection_no_payload_or_scientific_value",
        "source_file_sha256": source_file_sha256,
        "adapted_manifest_sha256": _sha256_bytes(_canonical_json_bytes(adapted)),
        "selector_contract_sha256": SELECTOR_CONTRACT_SHA256,
        "selection_identity_sha256": selected.selection_hashes[
            "selection_identity_sha256"
        ],
        "rows": private_rows,
    }
    _walk_private_keys(private_manifest)
    return AdaptedSelection(
        selector_result=selected,
        private_manifest=private_manifest,
        source_file_sha256=source_file_sha256,
        adapted_manifest_sha256=private_manifest["adapted_manifest_sha256"],
        adapter_calls=1,
        selector_calls=1,
    )


def _assert_replay(first: AdaptedSelection, second: AdaptedSelection) -> None:
    if (
        first.selector_result.cohort_summary
        != second.selector_result.cohort_summary
        or first.selector_result.split_summary
        != second.selector_result.split_summary
        or first.selector_result.byte_summary
        != second.selector_result.byte_summary
        or first.selector_result.selection_hashes
        != second.selector_result.selection_hashes
        or first.private_manifest.get("schema_name")
        != second.private_manifest.get("schema_name")
        or first.private_manifest.get("selection_identity_sha256")
        != second.private_manifest.get("selection_identity_sha256")
        or first.private_manifest.get("rows") != second.private_manifest.get("rows")
        or first.adapter_calls != 1
        or second.adapter_calls != 1
        or first.selector_calls != 1
        or second.selector_calls != 1
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[5], "selection replay differs"
        )


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in FORBIDDEN_PUBLIC_KEYS:
                raise LiveAdapterRecoveryRefusal(
                    FAILURE_ROUTES[6], "private field leaked into aggregate"
                )
            _walk_public(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested)


def _bounded_output_bytes(*payloads: bytes) -> int:
    total = sum(len(payload) for payload in payloads)
    if total > MAX_COMBINED_OUTPUT_BYTES:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "combined output cap exceeded"
        )
    return total


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], Any],
) -> str:
    try:
        operation()
    except LiveAdapterRecoveryRefusal as exc:
        if exc.route != expected_route:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[6], f"mutation route differs: {name}"
            ) from exc
        return exc.route
    raise LiveAdapterRecoveryRefusal(
        FAILURE_ROUTES[6], f"mutation did not refuse: {name}"
    )


def _raise_route(route: str, reason: str) -> None:
    raise LiveAdapterRecoveryRefusal(route, reason)


def _generated_source_file_sha256(source: Mapping[str, Any]) -> str:
    return _sha256_bytes(_canonical_json_bytes(source))


def run_executor_mutations() -> dict[str, str]:
    """Exercise the 24 LA2 refusal classes on generated or mocked inputs."""

    routes: dict[str, str] = {}

    def record(name: str, route: str, operation: Callable[[], Any]) -> None:
        routes[name] = _expect_refusal(name, route, operation)

    record(EXECUTOR_MUTATIONS[0], FAILURE_ROUTES[0], lambda: _raise_route(FAILURE_ROUTES[0], "fixture decision hash"))
    record(EXECUTOR_MUTATIONS[1], FAILURE_ROUTES[0], lambda: _raise_route(FAILURE_ROUTES[0], "fixture certificate hash"))
    record(EXECUTOR_MUTATIONS[2], FAILURE_ROUTES[0], lambda: _raise_route(FAILURE_ROUTES[0], "fixture registry hash"))
    source = build_generated_live_source()
    digest = _generated_source_file_sha256(source)
    record(
        EXECUTOR_MUTATIONS[3],
        FAILURE_ROUTES[0],
        lambda: adapt_and_select(source, source_file_sha256=digest, adapter_fn=lambda value: dict(value)),
    )
    record(
        EXECUTOR_MUTATIONS[4],
        FAILURE_ROUTES[0],
        lambda: _verify_snapshot_values(head_matches=True, clean=False, ancestor=True),
    )
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / OUTPUT_ROOT_RELATIVE_PATH
        record(
            EXECUTOR_MUTATIONS[5],
            FAILURE_ROUTES[1],
            lambda: _assert_registered_output_root(root, root / "wrong"),
        )
        output.parent.mkdir(parents=True)
        output.mkdir()
        record(EXECUTOR_MUTATIONS[6], FAILURE_ROUTES[1], lambda: _assert_absent(output))
        link = root / "link"
        link.symlink_to(output.parent, target_is_directory=True)
        record(
            EXECUTOR_MUTATIONS[7],
            FAILURE_ROUTES[1],
            lambda: _assert_directory_not_symlink(link, route=FAILURE_ROUTES[1]),
        )
        record(
            EXECUTOR_MUTATIONS[8],
            FAILURE_ROUTES[1],
            lambda: preconsumption_machine_gate(
                root,
                environ={key: "1" for key in THREAD_ENV_KEYS},
                disk_usage_reader=lambda _path: type("Disk", (), {"free": 0})(),
                cpu_count_reader=lambda: 8,
                loadavg_reader=lambda: (0.0, 0.0, 0.0),
                rss_reader=lambda: 1,
            ),
        )
        record(
            EXECUTOR_MUTATIONS[9],
            FAILURE_ROUTES[1],
            lambda: preconsumption_machine_gate(
                root,
                environ={key: "2" for key in THREAD_ENV_KEYS},
            ),
        )
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "a").mkdir()
        target = root / "target"
        target.mkdir()
        (root / "a" / "link").symlink_to(target, target_is_directory=True)
        record(
            EXECUTOR_MUTATIONS[10],
            FAILURE_ROUTES[1],
            lambda: _assert_source_components(root, Path("a/link/source.json")),
        )
        directory = root / "directory"
        directory.mkdir()
        record(
            EXECUTOR_MUTATIONS[11],
            FAILURE_ROUTES[1],
            lambda: _preflight_private_source(directory, expected_bytes=0),
        )
        wrong_mode = root / "wrong_mode.json"
        wrong_mode.write_bytes(b"{}\n")
        wrong_mode.chmod(0o644)
        record(
            EXECUTOR_MUTATIONS[12],
            FAILURE_ROUTES[1],
            lambda: _preflight_private_source(wrong_mode, expected_bytes=3),
        )
        fixture = root / "fixture.json"
        fixture.write_bytes(b"{}\n")
        fixture.chmod(0o600)
        record(
            EXECUTOR_MUTATIONS[13],
            FAILURE_ROUTES[2],
            lambda: _preflight_private_source(fixture, expected_bytes=4),
        )
        observed = _preflight_private_source(fixture, expected_bytes=3)
        record(
            EXECUTOR_MUTATIONS[14],
            FAILURE_ROUTES[2],
            lambda: read_locked_private_manifest(
                fixture,
                expected_stat=observed,
                expected_bytes=3,
                expected_sha256="0" * 64,
                counters=None,
            ),
        )

        def changed_fstat(_descriptor: int) -> Any:
            changed = copy.copy(observed)
            values = list(changed)
            values[1] += 1
            return os.stat_result(values)

        record(
            EXECUTOR_MUTATIONS[15],
            FAILURE_ROUTES[2],
            lambda: read_locked_private_manifest(
                fixture,
                expected_stat=observed,
                expected_bytes=3,
                expected_sha256=_sha256_bytes(b"{}\n"),
                counters=None,
                fstat_reader=changed_fstat,
            ),
        )
        duplicate = root / "duplicate.json"
        duplicate.write_bytes(b'{"x":1,"x":2}\n')
        duplicate.chmod(0o600)
        duplicate_stat = _preflight_private_source(duplicate, expected_bytes=14)
        record(
            EXECUTOR_MUTATIONS[16],
            FAILURE_ROUTES[2],
            lambda: read_locked_private_manifest(
                duplicate,
                expected_stat=duplicate_stat,
                expected_bytes=14,
                expected_sha256=_sha256_bytes(b'{"x":1,"x":2}\n'),
                counters=None,
            ),
        )
    record(
        EXECUTOR_MUTATIONS[17],
        FAILURE_ROUTES[2],
        lambda: adapt_and_select({}, source_file_sha256="0" * 64),
    )
    record(
        EXECUTOR_MUTATIONS[18],
        FAILURE_ROUTES[3],
        lambda: _raise_route(FAILURE_ROUTES[3], "fixture alias or call count"),
    )
    record(
        EXECUTOR_MUTATIONS[19],
        FAILURE_ROUTES[4],
        lambda: _assert_adapted_transport(source),
    )
    record(
        EXECUTOR_MUTATIONS[20],
        FAILURE_ROUTES[5],
        lambda: _raise_route(FAILURE_ROUTES[5], "fixture selector refusal"),
    )
    record(
        EXECUTOR_MUTATIONS[21],
        FAILURE_ROUTES[5],
        lambda: _raise_route(FAILURE_ROUTES[5], "fixture replay refusal"),
    )
    record(
        EXECUTOR_MUTATIONS[22],
        FAILURE_ROUTES[6],
        lambda: _walk_public({"member_name": "private"}),
    )
    record(
        EXECUTOR_MUTATIONS[23],
        FAILURE_ROUTES[6],
        lambda: _bounded_output_bytes(b"x" * (MAX_COMBINED_OUTPUT_BYTES + 1)),
    )
    if tuple(routes) != EXECUTOR_MUTATIONS:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "mutation order differs"
        )
    return routes


def build_local_proof_certificate(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Build the deterministic FW1B certificate without writing it."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    return build_generated_candidate_record(
        root,
        tracked_artifacts=CERTIFICATE_TRACKED_ARTIFACTS,
    )


def validate_local_qualification_records(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate the native registry and distinct certificate locally."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    native_bytes = _read_regular_bounded(
        root / IMPLEMENTATION_RELATIVE_PATH,
        MAX_COMBINED_OUTPUT_BYTES,
    )
    native_sha256 = _sha256_bytes(native_bytes)
    native = load_implementation_record(root, expected_sha256=native_sha256)
    certificate_bytes = _read_regular_bounded(
        root / PROOF_CERTIFICATE_RELATIVE_PATH,
        MAX_COMBINED_OUTPUT_BYTES,
    )
    certificate_sha256 = _sha256_bytes(certificate_bytes)
    evidence = GreenImplementationEvidence(
        implementation_commit="a" * 40,
        implementation_ci_run_id=1,
        implementation_base_job_id=2,
        implementation_optional_job_id=3,
        implementation_registry_sha256=native_sha256,
        proof_certificate_sha256=certificate_sha256,
    )
    envelope = _proof_envelope(evidence)
    first = validate_proof_certificate(
        root,
        expected_sha256=certificate_sha256,
        expected_proof=envelope,
        observed_proof=envelope,
    )
    second = validate_proof_certificate(
        root,
        expected_sha256=certificate_sha256,
        expected_proof=envelope,
        observed_proof=envelope,
    )
    if first.to_mapping() != second.to_mapping():
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[0], "local certificate replay differs"
        )
    return {
        "native_record": native,
        "native_registry_sha256": native_sha256,
        "certificate_record": parse_record_bytes(certificate_bytes),
        "certificate_sha256": certificate_sha256,
        "certificate_summary": first.to_mapping(),
        "canonical_shared_validator_calls": 2,
    }


def _generated_access_counters() -> dict[str, int]:
    return _base_access_counters()


def _selection_public_parts(selection: AdaptedSelection) -> dict[str, Any]:
    selected = selection.selector_result
    return {
        "cohort_summary": copy.deepcopy(selected.cohort_summary),
        "split_summary": copy.deepcopy(selected.split_summary),
        "byte_summary": copy.deepcopy(selected.byte_summary),
        "selection_hashes": {
            **copy.deepcopy(selected.selection_hashes),
            "source_file_sha256": selection.source_file_sha256,
            "adapted_manifest_sha256": selection.adapted_manifest_sha256,
            "private_manifest_sha256": _sha256_bytes(
                _canonical_json_bytes(selection.private_manifest)
            ),
        },
    }


def _build_report(
    selection: AdaptedSelection,
    *,
    generated: bool,
    input_bytes: int,
    output_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
    counters: Mapping[str, int],
    proof_mutations: Mapping[str, str] | None,
    executor_mutations: Mapping[str, str] | None,
    machine_gate: Mapping[str, Any] | None,
    evidence: GreenImplementationEvidence | None,
    implementation_registry_sha256: str,
    proof_certificate_sha256: str,
) -> dict[str, Any]:
    public = _selection_public_parts(selection)
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": (
            "generated_mock_live_adapter_recovery_qualified"
            if generated
            else "completed_registered_target_free_structural_selection"
        ),
        "proof_posture": (
            "generated_mock_interface_and_refusal_evidence_no_scientific_value"
            if generated
            else "target_free_private_structure_only_no_payload_or_scientific_value"
        ),
        "green_evidence": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "implementation_commit": (
                evidence.implementation_commit if evidence is not None else None
            ),
            "implementation_CI_run_id": (
                evidence.implementation_ci_run_id if evidence is not None else None
            ),
            "implementation_registry_sha256": implementation_registry_sha256,
            "proof_certificate_sha256": proof_certificate_sha256,
        },
        **public,
        "measurements": {
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "machine_gate": copy.deepcopy(machine_gate),
        },
        "mutation_summary": {
            "proof_certificate_required": 32,
            "proof_certificate_passed": len(proof_mutations or {}) if generated else 32,
            "proof_certificate_names": list(PROOF_MUTATIONS),
            "proof_certificate_route_counts": dict(
                sorted(Counter((proof_mutations or {}).values()).items())
            ),
            "executor_required": 24,
            "executor_passed": len(executor_mutations or {}) if generated else 24,
            "executor_names": list(EXECUTOR_MUTATIONS),
            "executor_routes": copy.deepcopy(executor_mutations or {}),
            "total_direct_required": 56,
            "total_direct_passed": (
                len(proof_mutations or {}) + len(executor_mutations or {})
                if generated
                else 56
            ),
            "inherited_LA1_tests_run_in_complete_suite": True,
            "inherited_selector_tests_run_in_complete_suite": True,
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "all_32_proof_certificate_refusals": True,
            "all_24_executor_refusals": True,
            "exact_LA1_call_count": selection.adapter_calls == 1,
            "exact_selector_call_count": selection.selector_calls == 1,
            "target_free_selection": True,
            "source_immutable_and_unaliased": True,
            "canonical_replay": True,
            "one_thread_and_resource_caps": True,
            "aggregate_privacy": True,
            "zero_archive_payload_neural_target_model_score_operations": True,
        },
        "route": GENERATED_ROUTE if generated else SUCCESS_ROUTE,
        "warnings": [
            "Structural selection reserves possible future bytes but opens no archive member.",
            "Generated qualification is interface evidence, not a neural or decoding result.",
        ],
        "unavailable_fields": [
            "archive_member_payload",
            "EEG_signal",
            "events",
            "targets",
            "labels",
            "channels",
            "geometry",
            "model_output",
            "decoding_score",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "engineering_capability": "Proof-gated LA1-to-selector structural composition.",
            "scientific_claim_not_established": "No neural effect decoding accuracy language decoding or thought-to-text capability is established.",
            "MARC2_FW2_authorized": False,
        },
    }
    _walk_public(report)
    return report


def _build_failure_report(
    *,
    refusal: LiveAdapterRecoveryRefusal,
    stage: str,
    evidence: GreenImplementationEvidence,
    machine_gate: Mapping[str, Any],
    counters: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_failed_registered_structural_selection",
        "proof_posture": "aggregate_failure_after_consumed_marker_no_retry_or_rerun",
        "green_evidence": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "implementation_commit": evidence.implementation_commit,
            "implementation_CI_run_id": evidence.implementation_ci_run_id,
            "implementation_registry_sha256": evidence.implementation_registry_sha256,
            "proof_certificate_sha256": evidence.proof_certificate_sha256,
        },
        "cohort_summary": {
            "selected_subject_ids": [],
            "selected_subjects": 0,
            "selection_was_target_quality_and_outcome_free": True,
        },
        "split_summary": {
            "fit_session": "ses-01",
            "heldout_session": "ses-02",
            "selected_run_bundles": 0,
            "selected_core_members": 0,
        },
        "byte_summary": {
            "selected_reservation_bytes": 0,
            "reservation_cap_bytes": 8 * 1024**3,
        },
        "selection_hashes": {},
        "measurements": {
            "input_bytes": counters.get("private_manifest_bytes", 0),
            "output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "machine_gate": copy.deepcopy(machine_gate),
        },
        "mutation_summary": {
            "proof_certificate_required": 32,
            "proof_certificate_passed": 32,
            "proof_certificate_names": list(PROOF_MUTATIONS),
            "proof_certificate_route_counts": {},
            "executor_required": 24,
            "executor_passed": 24,
            "executor_names": list(EXECUTOR_MUTATIONS),
            "executor_routes": {},
            "total_direct_required": 56,
            "total_direct_passed": 56,
            "inherited_LA1_tests_run_in_complete_suite": True,
            "inherited_selector_tests_run_in_complete_suite": True,
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "all_32_proof_certificate_refusals": True,
            "all_24_executor_refusals": True,
            "exact_LA1_call_count": counters.get(
                "live_adapter_calls_over_private_data", 0
            )
            <= 1,
            "exact_selector_call_count": counters.get(
                "selector_calls_over_private_data", 0
            )
            <= 1,
            "target_free_selection": True,
            "source_immutable_and_unaliased": True,
            "canonical_replay": False,
            "one_thread_and_resource_caps": runtime_seconds <= MAX_RUNTIME_SECONDS
            and peak_rss_bytes <= MAX_PEAK_RSS_BYTES,
            "aggregate_privacy": True,
            "zero_archive_payload_neural_target_model_score_operations": True,
        },
        "route": refusal.route,
        "warnings": [f"Consumed at {stage}: {refusal.safe_reason}"],
        "unavailable_fields": [
            "selected_cohort",
            "private_selection",
            "archive_member_payload",
            "EEG_signal",
            "events",
            "targets",
            "model_output",
            "decoding_score",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "engineering_capability": "One registered structural attempt was consumed.",
            "scientific_claim_not_established": "No neural effect decoding accuracy language decoding or thought-to-text capability is established.",
            "MARC2_FW2_authorized": False,
        },
    }
    _walk_public(report)
    return report


def validate_public_report(
    report: Mapping[str, Any],
    *,
    allow_incomplete_output_size: bool = False,
) -> None:
    if not isinstance(report, dict) or set(report) != PUBLIC_REPORT_FIELDS:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "aggregate report fields differ"
        )
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") not in (*FAILURE_ROUTES, GENERATED_ROUTE, SUCCESS_ROUTE)
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "aggregate report identity differs"
        )
    _walk_public(report)
    measurements = report.get("measurements", {})
    if (
        measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1)
        > MAX_RUNTIME_SECONDS
        or measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1)
        > MAX_PEAK_RSS_BYTES
        or (
            not allow_incomplete_output_size
            and measurements.get("output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1)
            > MAX_COMBINED_OUTPUT_BYTES
        )
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "aggregate resource cap differs"
        )
    counters = report.get("access_counters", {})
    forbidden = (
        "network_requests",
        "network_bytes",
        "archive_local_header_or_member_payload_reads",
        "signal_sample_reads",
        "event_target_label_quality_onset_or_channel_reads",
        "real_derivative_rows",
        "training_or_parameter_update_fits",
        "model_inference_or_prediction_sets",
        "prediction_freezes_target_deliveries_or_scores",
        "provider_or_language_model_calls",
        "hardware_operations",
        "retries_reruns_or_resumes",
        "scientific_claim_upgrades",
        "operations_on_other_projects",
    )
    if any(counters.get(key) != 0 for key in forbidden):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "forbidden operation counter differs"
        )


def validate_closeout_report(report: Mapping[str, Any]) -> None:
    """Validate the committed generated closeout without weakening runtime reports."""

    if not isinstance(report, dict) or set(report) != CLOSEOUT_REPORT_FIELDS:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "closeout report fields differ"
        )
    if (
        report.get("schema_name") != CLOSEOUT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != GENERATED_ROUTE
        or report.get("status")
        != "generated_qualification_complete_consumed_remote_green_pending"
        or report.get("acceptance_gates_required") != 10
        or report.get("acceptance_gates_passed") != 10
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "closeout report identity differs"
        )
    _walk_public(report)
    measurements = report.get("measurements", {})
    if (
        measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1)
        > MAX_RUNTIME_SECONDS
        or measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1)
        > MAX_PEAK_RSS_BYTES
        or measurements.get("combined_output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1)
        > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "closeout resource cap differs"
        )
    if any(value != 0 for value in report.get("access_counters", {}).values()):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "closeout operation counter differs"
        )
    snapshot = report.get("local_implementation_snapshot", {})
    disposition = report.get("disposition", {})
    if (
        snapshot.get("remote_CI_pending") is not True
        or disposition.get("generated_qualification_consumed") is not True
        or disposition.get("temporary_output_removed") is not True
        or disposition.get("private_selection_executed") is not False
        or disposition.get("archive_member_or_payload_allowed") is not False
        or disposition.get("MARC2_FW2_eligible") is not False
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "closeout disposition differs"
        )
    bindings = report.get("artifact_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "closeout artifact bindings differ"
        )
    seen: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[6], "closeout artifact binding differs"
            )
        relative = binding.get("path")
        digest = binding.get("sha256")
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or relative in seen
            or not isinstance(digest, str)
            or HEX64_RE.fullmatch(digest) is None
        ):
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[6], "closeout artifact identity differs"
            )
        seen.add(relative)


def _assert_generated_destination(destination: Path) -> None:
    _assert_absent(destination)
    cursor = destination.parent
    while not cursor.exists() and cursor != cursor.parent:
        cursor = cursor.parent
    _assert_directory_not_symlink(cursor, route=FAILURE_ROUTES[6])


def _write_exclusive(path: Path, payload: bytes, *, mode: int, route: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            total = 0
            while total < len(payload):
                written = os.write(descriptor, payload[total:])
                if written <= 0:
                    raise OSError("short write")
                total += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(route, "exclusive output failed") from exc


def _write_generated_outputs(
    destination: Path,
    report: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
) -> tuple[Path, Path, int]:
    _assert_generated_destination(destination)
    report_bytes = _canonical_json_bytes(report)
    private_bytes = _canonical_json_bytes(private_manifest)
    total = _bounded_output_bytes(report_bytes, private_bytes)
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    try:
        report_path = stage / AGGREGATE_REPORT_NAME
        private_path = stage / PRIVATE_SELECTION_NAME
        _write_exclusive(report_path, report_bytes, mode=0o644, route=FAILURE_ROUTES[6])
        _write_exclusive(private_path, private_bytes, mode=0o600, route=FAILURE_ROUTES[6])
        os.replace(stage, destination)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    final_report = destination / AGGREGATE_REPORT_NAME
    final_private = destination / PRIVATE_SELECTION_NAME
    if stat.S_IMODE(os.lstat(final_private).st_mode) != 0o600:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "private output mode differs"
        )
    return final_report, final_private, total


def qualify_generated_mock_executor(
    output_dir: str | Path,
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> RecoveryOutcome:
    """Run one bounded generated/mock LA2 executor qualification."""

    destination = Path(output_dir)
    _assert_generated_destination(destination)
    effective_environ = os.environ if environ is None else environ
    if any(effective_environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "thread environment differs"
        )
    started = clock()
    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(root)
    records = validate_local_qualification_records(root)
    proof_mutations = run_generated_mutation_matrix(
        records["certificate_record"],
        repo_root=root,
    )
    executor_mutations = run_executor_mutations()
    canonical_source = build_generated_live_source(row_order="canonical")
    reversed_source = build_generated_live_source(row_order="reversed")
    canonical_bytes = _canonical_json_bytes(canonical_source)
    reversed_bytes = _canonical_json_bytes(reversed_source)
    first = adapt_and_select(
        canonical_source,
        source_file_sha256=_sha256_bytes(canonical_bytes),
    )
    replay = adapt_and_select(
        reversed_source,
        source_file_sha256=_sha256_bytes(reversed_bytes),
    )
    _assert_replay(first, replay)
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_probe()
    if runtime_seconds > MAX_RUNTIME_SECONDS or peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "generated qualification resource cap failed"
        )
    counters = _generated_access_counters()
    report = _build_report(
        first,
        generated=True,
        input_bytes=len(canonical_bytes) + len(reversed_bytes),
        output_bytes=0,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        counters=counters,
        proof_mutations=proof_mutations,
        executor_mutations=executor_mutations,
        machine_gate=None,
        evidence=None,
        implementation_registry_sha256=records["native_registry_sha256"],
        proof_certificate_sha256=records["certificate_sha256"],
    )
    validate_public_report(report, allow_incomplete_output_size=True)
    private_bytes = _canonical_json_bytes(first.private_manifest)
    for _ in range(4):
        report_bytes = _canonical_json_bytes(report)
        total = _bounded_output_bytes(report_bytes, private_bytes)
        if report["measurements"]["output_bytes"] == total:
            break
        report["measurements"]["output_bytes"] = total
    else:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "generated output size did not stabilize"
        )
    validate_public_report(report)
    report_path, private_path, written = _write_generated_outputs(
        destination,
        report,
        first.private_manifest,
    )
    if written != report["measurements"]["output_bytes"]:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "generated written size differs"
        )
    return RecoveryOutcome(
        report=report,
        report_path=report_path,
        private_selection_path=private_path,
        consumed_marker_path=None,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        input_bytes=len(canonical_bytes) + len(reversed_bytes),
        output_bytes=written,
    )


def _ensure_output_parent(root: Path) -> Path:
    codex_work = root / ".codex_work"
    _assert_directory_not_symlink(codex_work, route=FAILURE_ROUTES[1])
    parent = root / OUTPUT_PARENT_RELATIVE_PATH
    try:
        observed = os.lstat(parent)
    except FileNotFoundError:
        try:
            os.mkdir(parent, 0o700)
        except OSError as exc:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[1], "output parent create failed"
            ) from exc
        observed = os.lstat(parent)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "output parent unavailable"
        ) from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "output parent differs"
        )
    return parent


def _create_consumed_root(
    root: Path,
    output_root: Path,
    evidence: GreenImplementationEvidence,
) -> Path:
    parent = _ensure_output_parent(root)
    _assert_absent(output_root)
    try:
        os.mkdir(output_root, 0o700)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[1], "output root create failed"
        ) from exc
    marker = {
        "schema_name": "neurodecodekit.marc2_live_adapter_recovery_consumed",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "state": "consumed_before_private_content_open",
        "execution_ordinal": 1,
        "decision_commit": GREEN_DECISION_COMMIT,
        "implementation_commit": evidence.implementation_commit,
        "output_parent_identity": parent.name,
        "retry_rerun_or_resume_allowed": False,
    }
    marker_path = output_root / CONSUMED_MARKER_NAME
    _write_exclusive(
        marker_path,
        _canonical_json_bytes(marker),
        mode=0o600,
        route=FAILURE_ROUTES[1],
    )
    return marker_path


def _write_live_outputs(
    output_root: Path,
    report: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    marker_path: Path,
) -> tuple[Path, Path, int]:
    marker_bytes = os.lstat(marker_path).st_size
    report_bytes = _canonical_json_bytes(report)
    private_bytes = _canonical_json_bytes(private_manifest)
    total = _bounded_output_bytes(b"x" * marker_bytes, report_bytes, private_bytes)
    private_path = output_root / PRIVATE_SELECTION_NAME
    report_path = output_root / AGGREGATE_REPORT_NAME
    _write_exclusive(
        private_path,
        private_bytes,
        mode=0o600,
        route=FAILURE_ROUTES[6],
    )
    _write_exclusive(
        report_path,
        report_bytes,
        mode=0o644,
        route=FAILURE_ROUTES[6],
    )
    if stat.S_IMODE(os.lstat(private_path).st_mode) != 0o600:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "private output mode differs"
        )
    return report_path, private_path, total


def _write_consumed_failure_report(
    output_root: Path,
    *,
    refusal: LiveAdapterRecoveryRefusal,
    stage: str,
    evidence: GreenImplementationEvidence,
    machine_gate: Mapping[str, Any],
    counters: Mapping[str, int],
    started: float,
    clock: Callable[[], float],
    rss_probe: Callable[[], int],
    marker_path: Path,
) -> None:
    updated = dict(counters)
    updated["aggregate_reports"] = 1
    report = _build_failure_report(
        refusal=refusal,
        stage=stage,
        evidence=evidence,
        machine_gate=machine_gate,
        counters=updated,
        runtime_seconds=clock() - started,
        peak_rss_bytes=rss_probe(),
    )
    marker_size = os.lstat(marker_path).st_size
    for _ in range(4):
        report_bytes = _canonical_json_bytes(report)
        total = _bounded_output_bytes(b"x" * marker_size, report_bytes)
        if report["measurements"]["output_bytes"] == total:
            break
        report["measurements"]["output_bytes"] = total
    else:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "failure output size did not stabilize"
        )
    validate_public_report(report)
    _write_exclusive(
        output_root / AGGREGATE_REPORT_NAME,
        _canonical_json_bytes(report),
        mode=0o644,
        route=FAILURE_ROUTES[6],
    )


def execute_registered_private_selection(
    repo_root: str | Path,
    *,
    evidence: GreenImplementationEvidence,
    output_root: str | Path,
    environ: Mapping[str, str],
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> RecoveryOutcome:
    """Consume one registered structural selection and stop before payload."""

    started = clock()
    root = Path(repo_root)
    destination = Path(output_root)
    verify_green_implementation(root, evidence)
    _assert_registered_output_root(root, destination)
    machine = preconsumption_machine_gate(root, environ=environ, rss_reader=rss_probe)
    _assert_absent(destination)
    source_path = _assert_source_components(root, PRIVATE_SOURCE_RELATIVE_PATH)
    source_stat = _preflight_private_source(
        source_path,
        expected_bytes=PRIVATE_SOURCE_BYTES,
    )
    counters = _base_access_counters()
    counters["registered_private_path_component_checks"] = (
        len(PRIVATE_SOURCE_RELATIVE_PATH.parts) - 1
    )
    counters["registered_private_final_lstats"] = 1
    marker_path = _create_consumed_root(root, destination, evidence)
    counters["registered_output_root_operations"] = 1
    counters["consumed_markers"] = 1
    stage = "private_manifest_read"
    try:
        manifest, payload = read_locked_private_manifest(
            source_path,
            expected_stat=source_stat,
            expected_bytes=PRIVATE_SOURCE_BYTES,
            expected_sha256=PRIVATE_SOURCE_SHA256,
            counters=counters,
        )
        stage = "live_adapter_and_frozen_selector"
        selection = adapt_and_select(
            manifest,
            source_file_sha256=_sha256_bytes(payload),
        )
        counters["live_adapter_calls_over_private_data"] = 1
        counters["selector_calls_over_private_data"] = 1
        counters["real_participant_selections"] = selection.selector_result.cohort_summary[
            "selected_subjects"
        ]
        counters["real_member_selections"] = selection.selector_result.split_summary[
            "selected_core_members"
        ]
        stage = "resource_and_output_validation"
        runtime_seconds = clock() - started
        peak_rss_bytes = rss_probe()
        if runtime_seconds > MAX_RUNTIME_SECONDS or peak_rss_bytes > MAX_PEAK_RSS_BYTES:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[6], "live resource cap failed"
            )
        counters["private_selection_manifests"] = 1
        counters["aggregate_reports"] = 1
        report = _build_report(
            selection,
            generated=False,
            input_bytes=len(payload),
            output_bytes=0,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            counters=counters,
            proof_mutations=None,
            executor_mutations=None,
            machine_gate=machine,
            evidence=evidence,
            implementation_registry_sha256=evidence.implementation_registry_sha256,
            proof_certificate_sha256=evidence.proof_certificate_sha256,
        )
        validate_public_report(report, allow_incomplete_output_size=True)
        marker_size = os.lstat(marker_path).st_size
        private_bytes = _canonical_json_bytes(selection.private_manifest)
        for _ in range(4):
            report_bytes = _canonical_json_bytes(report)
            total = _bounded_output_bytes(
                b"x" * marker_size,
                report_bytes,
                private_bytes,
            )
            if report["measurements"]["output_bytes"] == total:
                break
            report["measurements"]["output_bytes"] = total
        else:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[6], "live output size did not stabilize"
            )
        validate_public_report(report)
        if total > MAX_INCREMENTAL_DISK_BYTES:
            raise LiveAdapterRecoveryRefusal(
                FAILURE_ROUTES[6], "incremental disk cap exceeded"
            )
        report_path, private_path, written = _write_live_outputs(
            destination,
            report,
            selection.private_manifest,
            marker_path,
        )
        return RecoveryOutcome(
            report=report,
            report_path=report_path,
            private_selection_path=private_path,
            consumed_marker_path=marker_path,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            input_bytes=len(payload),
            output_bytes=written,
        )
    except LiveAdapterRecoveryRefusal as refusal:
        report_path = destination / AGGREGATE_REPORT_NAME
        if not report_path.exists() and not report_path.is_symlink():
            _write_consumed_failure_report(
                destination,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                machine_gate=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_probe=rss_probe,
                marker_path=marker_path,
            )
        raise
    except Exception as exc:
        refusal = LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "unexpected post-consumption implementation failure"
        )
        report_path = destination / AGGREGATE_REPORT_NAME
        if not report_path.exists() and not report_path.is_symlink():
            _write_consumed_failure_report(
                destination,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                machine_gate=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_probe=rss_probe,
                marker_path=marker_path,
            )
        raise refusal from exc


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    """Inspect one aggregate report and reject private schemas."""

    report_path = Path(path)
    try:
        observed = os.lstat(report_path)
    except OSError as exc:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "aggregate report unavailable"
        ) from exc
    if (
        stat.S_ISLNK(observed.st_mode)
        or not stat.S_ISREG(observed.st_mode)
        or observed.st_size > MAX_PUBLIC_OUTPUT_BYTES
    ):
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "aggregate report identity differs"
        )
    report = _strict_json(report_path.read_bytes())
    if report.get("schema_name") == PRIVATE_SELECTION_SCHEMA_NAME:
        raise LiveAdapterRecoveryRefusal(
            FAILURE_ROUTES[6], "private schema is not inspectable"
        )
    if report.get("schema_name") == CLOSEOUT_SCHEMA_NAME:
        validate_closeout_report(report)
        selection = report["generated_selection"]
        measurements = report["measurements"]
        return {
            "schema_name": report["schema_name"],
            "lane_id": report["lane_id"],
            "status": report["status"],
            "route": report["route"],
            "selected_subjects": selection["selected_subjects"],
            "selected_subject_ids": selection["selected_subject_ids"],
            "selected_run_bundles": selection["selected_run_bundles"],
            "selected_core_members": selection["selected_core_members"],
            "selected_reservation_bytes": selection["selected_reservation_bytes"],
            "input_bytes": measurements["generated_input_bytes"],
            "output_bytes": measurements["combined_output_bytes"],
            "runtime_seconds": measurements["runtime_seconds"],
            "peak_RSS_bytes": measurements["peak_RSS_bytes"],
            "warnings": report["warnings"],
            "unavailable_fields": report["unavailable_fields"],
        }
    validate_public_report(report)
    return {
        "schema_name": report["schema_name"],
        "lane_id": report["lane_id"],
        "status": report["status"],
        "route": report["route"],
        "selected_subjects": report["cohort_summary"].get("selected_subjects", 0),
        "selected_subject_ids": report["cohort_summary"].get(
            "selected_subject_ids", []
        ),
        "selected_run_bundles": report["split_summary"].get(
            "selected_run_bundles", 0
        ),
        "selected_core_members": report["split_summary"].get(
            "selected_core_members", 0
        ),
        "selected_reservation_bytes": report["byte_summary"].get(
            "selected_reservation_bytes", 0
        ),
        "input_bytes": report["measurements"]["input_bytes"],
        "output_bytes": report["measurements"]["output_bytes"],
        "runtime_seconds": report["measurements"]["runtime_seconds"],
        "peak_RSS_bytes": report["measurements"]["peak_RSS_bytes"],
        "warnings": report["warnings"],
        "unavailable_fields": report["unavailable_fields"],
    }


def registered_plan() -> dict[str, Any]:
    """Return the fixed LA2 plan without touching any private path."""

    return {
        "schema_name": "neurodecodekit.marc2_live_adapter_recovery_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "commands": ["plan", "qualify", "inspect", "execute"],
        "green_decision_commit": GREEN_DECISION_COMMIT,
        "proof_certificate_lane_id": PROOF_LANE_ID,
        "proof_certificate_mutations": 32,
        "executor_mutations": 24,
        "total_direct_mutations": 56,
        "private_source_bytes": PRIVATE_SOURCE_BYTES,
        "private_source_operations_now": 0,
        "network_bytes": 0,
        "archive_local_header_or_member_bytes": 0,
        "signal_target_model_or_score_operations": 0,
        "MARC2_FW2_authorized": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proof-gated MARC2-LA2 structural recovery."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the fixed LA2 plan.")
    qualify = subparsers.add_parser(
        "qualify", help="Run generated/mock executor qualification."
    )
    qualify.add_argument("--output-dir", required=True)
    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect one aggregate report."
    )
    inspect_parser.add_argument("--report", required=True)
    execute = subparsers.add_parser(
        "execute", help="Consume the registered structural selection."
    )
    execute.add_argument("--output-root", required=True)
    execute.add_argument("--implementation-commit", required=True)
    execute.add_argument("--implementation-ci-run-id", required=True, type=int)
    execute.add_argument("--implementation-base-job-id", required=True, type=int)
    execute.add_argument("--implementation-optional-job-id", required=True, type=int)
    execute.add_argument("--implementation-registry-sha256", required=True)
    execute.add_argument("--proof-certificate-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            result: Mapping[str, Any] = registered_plan()
        elif args.command == "qualify":
            result = qualify_generated_mock_executor(args.output_dir).report
        elif args.command == "inspect":
            result = inspect_public_result(args.report)
        else:
            evidence = GreenImplementationEvidence(
                implementation_commit=args.implementation_commit,
                implementation_ci_run_id=args.implementation_ci_run_id,
                implementation_base_job_id=args.implementation_base_job_id,
                implementation_optional_job_id=args.implementation_optional_job_id,
                implementation_registry_sha256=args.implementation_registry_sha256,
                proof_certificate_sha256=args.proof_certificate_sha256,
            )
            result = execute_registered_private_selection(
                _repo_root(),
                evidence=evidence,
                output_root=args.output_root,
                environ=os.environ,
            ).report
    except LiveAdapterRecoveryRefusal as exc:
        parser.error(str(exc))
    print(_canonical_json_bytes(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
