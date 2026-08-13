"""Proof-gated, source-aware MARC1 metadata wrapper.

The generated qualification path uses only in-memory fixtures and mocked
responses. The live path is fixed to one public metadata response and stops
before every participant archive or neural payload operation.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import re
import resource
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping, Sequence

from neurodecodekit.datasets import marc1_source_aware_inventory_attestation as attestor


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC1-SA1A"
GENERATED_ROUTE = "MARC1SAL-G1"
SUCCESS_ROUTE = "MARC1SAL-R1"
BLOCKED_ROUTE = "MARC1SAL-R2"
FAILURE_ROUTES = {
    "proof": "MARC1SAL-F00",
    "machine_or_output": "MARC1SAL-F01",
    "transport_or_json": "MARC1SAL-F02",
    "target_or_semantics": "MARC1SAL-F03",
    "privacy_or_resource": "MARC1SAL-F04",
}
SOURCE_ROUTE_MAP = {
    "MARC1SA-R1": SUCCESS_ROUTE,
    "MARC1SA-R2": SUCCESS_ROUTE,
    "MARC1SA-R3": BLOCKED_ROUTE,
    "MARC1SA-R4": BLOCKED_ROUTE,
}

GREEN_DECISION_COMMIT = "ef9ab91b38ad48ef5e832b993d4ca338d889bc04"
GREEN_DECISION_CI_RUN_ID = 31_670_457_497
GREEN_DECISION_BASE_JOB_ID = 94_353_799_568
GREEN_DECISION_OPTIONAL_JOB_ID = 94_353_799_602
DECISION_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_live_metadata_authorization_decision.v0.json"
)
DECISION_BYTES = 16_152
DECISION_SHA256 = "25c2e6b9e745ffb126644867e77e78558a8c3929bda12f0728a7ee776e3273c5"
DECISION_DOCUMENT_RELATIVE_PATH = Path(
    "docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_DECISION.md"
)
DECISION_DOCUMENT_BYTES = 7_964
DECISION_DOCUMENT_SHA256 = (
    "793a3c9fdeeb5990ad312a8fee8569bad085729e0044bc52912e213bce6111ed"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_live_metadata_authorization_request.v0.json"
)
REQUEST_BYTES = 16_974
REQUEST_SHA256 = "f5421681fe5ceb6a4b154de692bff81619c87338c832e4e04640bfcad9ca4659"
PACKET_RELATIVE_PATH = Path("docs/MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_PACKET.md")
PACKET_BYTES = 12_964
PACKET_SHA256 = "94a4c294db0177d0eb6b7320eb0f4874557e595dbfb26fe7b9a1022996b47162"
ATTESTOR_RESULT_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_inventory_attestation_result.v0.json"
)
ATTESTOR_RESULT_BYTES = 10_655
ATTESTOR_RESULT_SHA256 = (
    "4a8fff973f9943072ccd9b1aa4a9691b4b2a85e8d8fc1f832c583ee59f5ae80d"
)
ATTESTOR_CONTRACT_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_inventory_attestation_contract.v0.json"
)
ATTESTOR_CONTRACT_BYTES = 14_048
ATTESTOR_CONTRACT_SHA256 = (
    "7c405520a3c2039d8ff202f8e34f228627b5b2f5b97cd74e2fe9b42b83de8bec"
)
ATTESTOR_IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_inventory_attestation_implementation.v0.json"
)
ATTESTOR_IMPLEMENTATION_BYTES = 8_651
ATTESTOR_IMPLEMENTATION_SHA256 = (
    "61f55d7cae273eac431fa93fd26e978db3e35e3d04fc0a41b05323bc518d0d88"
)
ATTESTOR_SOURCE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc1_source_aware_inventory_attestation.py"
)
ATTESTOR_SOURCE_BYTES = 72_882
ATTESTOR_SOURCE_SHA256 = (
    "36a06958009f3ac42af6eb69d464a61db6f004bc51fa4f3b73420538cf29a482"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_live_metadata_implementation.v0.json"
)
SOURCE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc1_source_aware_live_metadata.py"
)

SOURCE_PROVIDER = "Figshare"
SOURCE_RECORD_ID = 29_666_735
SOURCE_VERSION = 3
SOURCE_DOI = "10.6084/m9.figshare.29666735.v3"
SOURCE_URL = (
    "https://api.figshare.com/v2/articles/29666735/versions/3/files"
    "?page=1&page_size=1000"
)
SOURCE_HOST = "api.figshare.com"
REQUEST_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "identity",
    "User-Agent": "NeuroDecodeKit-MARC1-SA1A/0.1",
}
REAL_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc1_source_aware_inventory/live_metadata_v0"
)
MARKER_NAME = "execution_consumed.v0.json"
PRIVATE_NAME = "marc1_source_aware_live_metadata.private.v0.json"
REPORT_NAME = "marc1_source_aware_live_metadata_result.v0.json"
OUTPUT_NAMES = (MARKER_NAME, PRIVATE_NAME, REPORT_NAME)

THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
MAX_RESPONSE_BYTES = 2 * 1024**2
MAX_REPORT_BYTES = 1024**2
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2
MINIMUM_FREE_DISK_BYTES = 10 * 1024**3
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_LOAD_PER_LOGICAL_CPU = 1.0
HTTP_TIMEOUT_SECONDS = 20.0
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
PRIVATE_STRING_RE = re.compile(r"(?:sub-\d{2}|https?://|\A[0-9a-f]{32}\Z)", re.I)

GENERATED_FAMILIES = tuple(attestor.FAMILY_ROUTES)
GENERATED_REFUSALS = (
    "registered_output_path",
    "capability_not_first",
    "existing_output",
    "wrong_request_method",
    "wrong_request_URL",
    "request_body",
    "authorization_header",
    "wrong_status",
    "final_URL_drift",
    "non_JSON_content_type",
    "gzip_content_encoding",
    "duplicate_content_encoding",
    "conflicting_framing",
    "malformed_content_length",
    "early_close",
    "body_overflow",
    "body_nonbytes",
    "body_read_failure",
    "malformed_UTF8",
    "malformed_JSON",
    "duplicate_JSON_key",
    "nonfinite_JSON_constant",
    "target_like_field",
    "missing_public_core",
    "MD5_disagreement",
    "public_private_leak",
    "runtime_cap",
    "peak_RSS_cap",
    "thread_environment_mismatch",
    "malformed_green_evidence",
    "second_invocation",
)
ACCEPTANCE_GATES = (
    "green_decision_identity_exact",
    "standard_library_only",
    "consumed_live_executor_absent",
    "output_capability_first",
    "fixed_request_identity",
    "one_response_cap",
    "three_HTTP_framing_forms",
    "strict_JSON_and_target_firewall",
    "all_source_aware_routes",
    "drift_blocks_selection",
    "private_public_separation",
    "three_allowlisted_outputs",
    "mode_0600_marker_and_private_manifest",
    "aggregate_report_inspection_once",
    "deterministic_semantic_replay",
    "all_refusals_pass",
    "resource_caps_pass",
    "generated_cleanup_exact",
    "real_network_zero",
    "payload_neural_target_model_score_zero",
)


class LiveMetadataRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-SA1A route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES.values():
            raise ValueError("unknown MARC1-SA1A refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class GreenWrapperEvidence:
    """Operator-supplied remote-green proof for the exact wrapper commit."""

    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    implementation_registry_sha256: str
    registered_execution_ordinal: int = 1


@dataclass(slots=True)
class AccessLedger:
    """Count wrapper operations and keep forbidden work explicit."""

    values: dict[str, int] = field(
        default_factory=lambda: {
            "capability_acquisitions": 0,
            "capability_revalidations": 0,
            "parent_directories_created": 0,
            "repository_reads": 0,
            "repository_bytes": 0,
            "proof_validations": 0,
            "generated_fixtures": 0,
            "generated_rows": 0,
            "generated_input_bytes": 0,
            "adversarial_cases": 0,
            "adversarial_mock_HTTP_calls": 0,
            "adversarial_response_reads": 0,
            "mock_HTTP_calls": 0,
            "public_HTTP_requests": 0,
            "accepted_response_bodies": 0,
            "response_body_bytes": 0,
            "metadata_parses": 0,
            "attestations": 0,
            "available_selections": 0,
            "output_directories_created": 0,
            "output_files_created": 0,
            "output_bytes": 0,
            "public_report_inspections": 0,
            "cleanup_file_unlinks": 0,
            "cleanup_directory_removals": 0,
            "participant_archive_requests": 0,
            "payload_requests": 0,
            "payload_bytes": 0,
            "signal_reads": 0,
            "target_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scoring_events": 0,
            "provider_model_calls": 0,
            "hardware_operations": 0,
            "operations_on_other_projects": 0,
            "retries": 0,
            "reruns": 0,
            "claim_upgrades": 0,
        }
    )

    def increment(self, name: str, amount: int = 1) -> None:
        if name not in self.values or isinstance(amount, bool) or amount < 0:
            raise ValueError("invalid wrapper ledger update")
        self.values[name] += amount

    def before_capability(self) -> dict[str, int]:
        return {
            name: value
            for name, value in self.values.items()
            if name != "capability_acquisitions"
        }


@dataclass(slots=True)
class OutputCapability:
    """Held no-follow authority for one absent output root."""

    parent_fd: int
    parent_path: str
    parent_device: int
    parent_inode: int
    output_basename: str
    ledger: AccessLedger
    output_fd: int | None = None
    output_created: bool = False
    closed: bool = False

    def __reduce__(self) -> Any:
        raise TypeError("OutputCapability is process-local")

    def close(self) -> None:
        if self.output_fd is not None:
            try:
                os.close(self.output_fd)
            except OSError:
                pass
            self.output_fd = None
        if not self.closed:
            try:
                os.close(self.parent_fd)
            except OSError:
                pass
            self.closed = True


@dataclass(frozen=True)
class TransportResult:
    """One bounded body and aggregate transport provenance."""

    body: bytes
    observed_bytes: int
    body_sha256: str
    framing: str
    content_encoding: str


@dataclass(frozen=True)
class WrapperResult:
    """One source-aware semantic result."""

    source_attestation: attestor.Attestation
    wrapper_route: str
    transport: TransportResult


@dataclass(frozen=True)
class WrapperOutcome:
    """One generated qualification or consumed metadata result."""

    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path | None
    marker_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    combined_output_bytes: int
    output_removed: bool
    marker_sha256: str
    private_manifest_sha256: str | None
    report_sha256: str


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        del req, fp, code, msg, headers, newurl
        return None


class _MemoryHeaders:
    def __init__(self, pairs: Sequence[tuple[str, str]]):
        self._pairs = list(pairs)

    def raw_items(self) -> list[tuple[str, str]]:
        return list(self._pairs)


class _MemoryResponse(io.BytesIO):
    def __init__(
        self,
        body: bytes,
        *,
        status: int = 200,
        url: str = SOURCE_URL,
        headers: Sequence[tuple[str, str]] | None = None,
        will_close: bool = True,
    ):
        super().__init__(body)
        self.status = status
        self._url = url
        self.headers = _MemoryHeaders(
            headers if headers is not None else [("Content-Type", "application/json")]
        )
        self.will_close = will_close

    def geturl(self) -> str:
        return self._url


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
    except (TypeError, ValueError) as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "canonical JSON differs"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(_value: str) -> None:
    raise ValueError("nonfinite JSON constant")


def _strict_json(payload: bytes, *, route: str) -> Any:
    try:
        return json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LiveMetadataRefusal(route, "strict JSON differs") from exc


def _read_bound(
    root: Path,
    relative: Path,
    *,
    expected_bytes: int | None,
    expected_sha256: str,
    ledger: AccessLedger,
) -> bytes:
    path = root / relative
    try:
        observed = path.lstat()
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
            raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "bound artifact type differs")
        payload = path.read_bytes()
    except LiveMetadataRefusal:
        raise
    except OSError as exc:
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "bound artifact unavailable") from exc
    ledger.increment("repository_reads")
    ledger.increment("repository_bytes", len(payload))
    if (
        (expected_bytes is not None and len(payload) != expected_bytes)
        or _sha256_bytes(payload) != expected_sha256
    ):
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "bound artifact differs")
    return payload


def load_green_decision(root: str | Path, ledger: AccessLedger) -> dict[str, Any]:
    """Replay the exact green decision and every immutable parent binding."""

    repo = Path(root)
    decision_payload = _read_bound(
        repo,
        DECISION_RELATIVE_PATH,
        expected_bytes=DECISION_BYTES,
        expected_sha256=DECISION_SHA256,
        ledger=ledger,
    )
    _read_bound(
        repo,
        DECISION_DOCUMENT_RELATIVE_PATH,
        expected_bytes=DECISION_DOCUMENT_BYTES,
        expected_sha256=DECISION_DOCUMENT_SHA256,
        ledger=ledger,
    )
    _read_bound(
        repo,
        REQUEST_RELATIVE_PATH,
        expected_bytes=REQUEST_BYTES,
        expected_sha256=REQUEST_SHA256,
        ledger=ledger,
    )
    _read_bound(
        repo,
        PACKET_RELATIVE_PATH,
        expected_bytes=PACKET_BYTES,
        expected_sha256=PACKET_SHA256,
        ledger=ledger,
    )
    _read_bound(
        repo,
        ATTESTOR_RESULT_RELATIVE_PATH,
        expected_bytes=ATTESTOR_RESULT_BYTES,
        expected_sha256=ATTESTOR_RESULT_SHA256,
        ledger=ledger,
    )
    _read_bound(
        repo,
        ATTESTOR_CONTRACT_RELATIVE_PATH,
        expected_bytes=ATTESTOR_CONTRACT_BYTES,
        expected_sha256=ATTESTOR_CONTRACT_SHA256,
        ledger=ledger,
    )
    _read_bound(
        repo,
        ATTESTOR_IMPLEMENTATION_RELATIVE_PATH,
        expected_bytes=ATTESTOR_IMPLEMENTATION_BYTES,
        expected_sha256=ATTESTOR_IMPLEMENTATION_SHA256,
        ledger=ledger,
    )
    _read_bound(
        repo,
        ATTESTOR_SOURCE_RELATIVE_PATH,
        expected_bytes=ATTESTOR_SOURCE_BYTES,
        expected_sha256=ATTESTOR_SOURCE_SHA256,
        ledger=ledger,
    )
    value = _strict_json(decision_payload, route=FAILURE_ROUTES["proof"])
    if not isinstance(value, dict):
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "decision record differs")
    green = value.get("green_request", {})
    user = value.get("user_authorization", {})
    if (
        value.get("schema_name")
        != "neurodecodekit.marc1_source_aware_live_metadata_authorization_decision"
        or value.get("lane_id") != LANE_ID
        or value.get("authorization_parent_commit")
        != "b0775501e8d7dc5b28b81692dbc7fb02d423be95"
        or green.get("CI_run_id") != 31_621_794_066
        or green.get("both_required_jobs_green") is not True
        or user.get("actual_message_SHA256")
        != "0c3c79426ed20b5720db1b09ca50280dff0033e75024297a394a92a8c1c66185"
        or user.get("later_unpacketized_steps_authorized_by_this_record") is not False
        or value.get("claim_boundary", {}).get("current_scientific_claim_upgrade")
        is not False
    ):
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "decision proof differs")
    ledger.increment("proof_validations")
    return value


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def load_implementation_record(
    root: str | Path,
    *,
    expected_sha256: str,
    ledger: AccessLedger,
) -> dict[str, Any]:
    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "implementation hash is malformed")
    repo = Path(root)
    path = repo / IMPLEMENTATION_RELATIVE_PATH
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["proof"], "implementation record unavailable"
        ) from exc
    ledger.increment("repository_reads")
    ledger.increment("repository_bytes", len(payload))
    if _sha256_bytes(payload) != expected_sha256:
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "implementation record differs")
    value = _strict_json(payload, route=FAILURE_ROUTES["proof"])
    if not isinstance(value, dict):
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "implementation record differs")
    source = value.get("implementation_source", {})
    execution = value.get("execution_state", {})
    if (
        value.get("schema_name")
        != "neurodecodekit.marc1_source_aware_live_metadata_implementation"
        or value.get("lane_id") != LANE_ID
        or value.get("green_parent_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or value.get("green_parent_decision", {}).get("CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or source.get("path") != SOURCE_RELATIVE_PATH.as_posix()
        or execution.get("public_execution_consumed") is not False
        or execution.get("network_requests") != 0
        or execution.get("payload_bytes") != 0
    ):
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "implementation proof differs")
    source_payload = _read_bound(
        repo,
        SOURCE_RELATIVE_PATH,
        expected_bytes=source.get("bytes"),
        expected_sha256=str(source.get("sha256")),
        ledger=ledger,
    )
    if not source_payload:
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "implementation source differs")
    ledger.increment("proof_validations")
    return value


def verify_green_wrapper_evidence(
    root: str | Path,
    evidence: GreenWrapperEvidence,
    ledger: AccessLedger,
) -> dict[str, Any]:
    """Bind a clean exact HEAD to externally observed green CI evidence."""

    repo = Path(root)
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or HEX64_RE.fullmatch(evidence.implementation_registry_sha256) is None
        or min(
            evidence.implementation_ci_run_id,
            evidence.implementation_base_job_id,
            evidence.implementation_optional_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "green wrapper evidence is malformed")
    head = _git(repo, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.implementation_commit:
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "HEAD differs from wrapper evidence")
    clean = _git(repo, "status", "--porcelain", "--untracked-files=no")
    if clean.returncode or clean.stdout.strip():
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "tracked worktree is not clean")
    ancestor = _git(repo, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, "HEAD")
    if ancestor.returncode:
        raise LiveMetadataRefusal(FAILURE_ROUTES["proof"], "green decision is not an ancestor")
    load_green_decision(repo, ledger)
    return load_implementation_record(
        repo,
        expected_sha256=evidence.implementation_registry_sha256,
        ledger=ledger,
    )


def _require_no_follow_support() -> None:
    if (
        not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or any(
            function not in os.supports_dir_fd
            for function in (os.open, os.mkdir, os.stat, os.unlink, os.rmdir)
        )
        or os.stat not in os.supports_follow_symlinks
    ):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "no-follow primitives unavailable"
        )


def _lstat_ancestors(parent: str) -> os.stat_result:
    current = "/"
    try:
        observed = os.lstat(current)
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["machine_or_output"], "root ancestor differs"
            )
        for component in Path(parent).parts[1:]:
            current = os.path.join(current, component)
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
                raise LiveMetadataRefusal(
                    FAILURE_ROUTES["machine_or_output"], "output ancestor differs"
                )
        return os.lstat(parent)
    except LiveMetadataRefusal:
        raise
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output ancestor unavailable"
        ) from exc


def _require_child_absent(parent_fd: int, basename: str) -> None:
    try:
        os.stat(basename, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output absence check failed"
        ) from exc
    raise LiveMetadataRefusal(FAILURE_ROUTES["machine_or_output"], "output already exists")


def acquire_generated_output_capability(
    output_dir: str | os.PathLike[str], ledger: AccessLedger
) -> OutputCapability:
    """Acquire generated output authority before proof or fixture work."""

    _require_no_follow_support()
    if any(ledger.before_capability().values()) or ledger.values["capability_acquisitions"]:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "capability was not first"
        )
    try:
        raw = os.fspath(output_dir)
    except TypeError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output path type differs"
        ) from exc
    if not isinstance(raw, str) or not raw or "\x00" in raw or not raw.startswith("/"):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output path is not absolute"
        )
    if raw == "/" or raw != os.path.normpath(raw):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output path is not normalized"
        )
    if tuple(Path(raw).parts[-len(REAL_ROOT_RELATIVE_PATH.parts) :]) == tuple(
        REAL_ROOT_RELATIVE_PATH.parts
    ):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "registered output is forbidden in qualification"
        )
    parent, basename = os.path.split(raw)
    temporary = os.path.realpath(tempfile.gettempdir())
    try:
        if os.path.commonpath((os.path.realpath(parent), temporary)) != temporary:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["machine_or_output"], "generated output is outside temporary space"
            )
    except ValueError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "generated output path differs"
        ) from exc
    before = _lstat_ancestors(parent)
    parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    opened = os.fstat(parent_fd)
    if (
        (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
        or not stat.S_ISDIR(opened.st_mode)
    ):
        os.close(parent_fd)
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output parent identity changed"
        )
    _require_child_absent(parent_fd, basename)
    ledger.increment("capability_acquisitions")
    return OutputCapability(
        parent_fd=parent_fd,
        parent_path=parent,
        parent_device=opened.st_dev,
        parent_inode=opened.st_ino,
        output_basename=basename,
        ledger=ledger,
    )


def _open_or_create_directory(parent_fd: int, name: str, ledger: AccessLedger) -> int:
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except FileNotFoundError:
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        except OSError as exc:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["machine_or_output"], "private parent creation failed"
            ) from exc
        ledger.increment("parent_directories_created")
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "private parent differs"
        ) from exc


def acquire_live_output_capability(root: str | Path, ledger: AccessLedger) -> OutputCapability:
    """Acquire the fixed repository-private output capability first."""

    _require_no_follow_support()
    if any(ledger.before_capability().values()) or ledger.values["capability_acquisitions"]:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "capability was not first"
        )
    repo = Path(root)
    raw = os.fspath(repo)
    if not repo.is_absolute() or raw != os.path.normpath(raw):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "repository root differs"
        )
    before = _lstat_ancestors(raw)
    root_fd = os.open(raw, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    opened = os.fstat(root_fd)
    if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
        os.close(root_fd)
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "repository capability changed"
        )
    work_fd: int | None = None
    inventory_fd: int | None = None
    try:
        work_fd = _open_or_create_directory(root_fd, ".codex_work", ledger)
        inventory_fd = _open_or_create_directory(
            work_fd, "marc1_source_aware_inventory", ledger
        )
        parent_stat = os.fstat(inventory_fd)
        _require_child_absent(inventory_fd, "live_metadata_v0")
        ledger.increment("capability_acquisitions")
        return OutputCapability(
            parent_fd=inventory_fd,
            parent_path=os.fspath(repo / REAL_ROOT_RELATIVE_PATH.parent),
            parent_device=parent_stat.st_dev,
            parent_inode=parent_stat.st_ino,
            output_basename="live_metadata_v0",
            ledger=ledger,
        )
    except Exception:
        if inventory_fd is not None:
            os.close(inventory_fd)
        raise
    finally:
        if work_fd is not None:
            os.close(work_fd)
        os.close(root_fd)


def _revalidate_capability(capability: OutputCapability) -> None:
    if capability.closed:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output capability is closed"
        )
    try:
        observed = os.fstat(capability.parent_fd)
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output capability unavailable"
        ) from exc
    if (
        (observed.st_dev, observed.st_ino)
        != (capability.parent_device, capability.parent_inode)
        or not stat.S_ISDIR(observed.st_mode)
    ):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output capability identity changed"
        )
    capability.ledger.increment("capability_revalidations")


def _create_output_root(capability: OutputCapability) -> None:
    _revalidate_capability(capability)
    _require_child_absent(capability.parent_fd, capability.output_basename)
    try:
        os.mkdir(capability.output_basename, mode=0o700, dir_fd=capability.parent_fd)
        output_fd = os.open(
            capability.output_basename,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=capability.parent_fd,
        )
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "output root creation failed"
        ) from exc
    capability.output_fd = output_fd
    capability.output_created = True
    capability.ledger.increment("output_directories_created")


def _write_relative(
    capability: OutputCapability, name: str, payload: bytes, *, mode: int
) -> None:
    if name not in OUTPUT_NAMES or capability.output_fd is None:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "output name or root differs"
        )
    _revalidate_capability(capability)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    try:
        fd = os.open(name, flags, mode, dir_fd=capability.output_fd)
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        observed = os.stat(name, dir_fd=capability.output_fd, follow_symlinks=False)
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "exclusive output write failed"
        ) from exc
    if not stat.S_ISREG(observed.st_mode) or stat.S_IMODE(observed.st_mode) != mode:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "output mode differs"
        )
    capability.ledger.increment("output_files_created")
    capability.ledger.increment("output_bytes", len(payload))


def _read_public_relative(capability: OutputCapability) -> bytes:
    if capability.output_fd is None:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "public report root unavailable"
        )
    try:
        fd = os.open(REPORT_NAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=capability.output_fd)
        with os.fdopen(fd, "rb", closefd=True) as handle:
            payload = handle.read(MAX_REPORT_BYTES + 1)
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "public report inspection failed"
        ) from exc
    if len(payload) > MAX_REPORT_BYTES:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "public report exceeds cap"
        )
    capability.ledger.increment("public_report_inspections")
    return payload


def _cleanup_generated_output(capability: OutputCapability, *, suppress: bool = False) -> None:
    if not capability.output_created or capability.output_fd is None:
        return
    try:
        for name in OUTPUT_NAMES:
            try:
                os.unlink(name, dir_fd=capability.output_fd)
                capability.ledger.increment("cleanup_file_unlinks")
            except FileNotFoundError:
                pass
        os.close(capability.output_fd)
        capability.output_fd = None
        os.rmdir(capability.output_basename, dir_fd=capability.parent_fd)
        capability.ledger.increment("cleanup_directory_removals")
        capability.output_created = False
    except OSError:
        if not suppress:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "generated cleanup failed"
            )


def build_registered_request() -> urllib.request.Request:
    request = urllib.request.Request(
        SOURCE_URL,
        data=None,
        headers=REQUEST_HEADERS,
        method="GET",
    )
    validate_registered_request(request)
    return request


def _normalized_request_headers(request: urllib.request.Request) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in request.header_items():
        lowered = key.strip().lower()
        text = value.strip()
        if not lowered or lowered in normalized or "\r" in text or "\n" in text:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "request header differs"
            )
        normalized[lowered] = text
    return normalized


def validate_registered_request(request: urllib.request.Request) -> None:
    if (
        request.full_url != SOURCE_URL
        or request.get_method() != "GET"
        or request.data is not None
        or _normalized_request_headers(request)
        != {name.lower(): value for name, value in REQUEST_HEADERS.items()}
    ):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "registered request differs"
        )


def _response_headers(response: BinaryIO) -> dict[str, str]:
    source = getattr(response, "headers", None)
    if source is None:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response headers unavailable"
        )
    items = source.raw_items() if hasattr(source, "raw_items") else source.items()
    critical = {
        "content-encoding",
        "content-length",
        "content-type",
        "location",
        "transfer-encoding",
    }
    normalized: dict[str, str] = {}
    for key, value in items:
        lowered = str(key).strip().lower()
        text = str(value).strip()
        if not lowered or "\r" in text or "\n" in text:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "response header differs"
            )
        if lowered not in critical:
            continue
        if lowered in normalized:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "response header is duplicated"
            )
        normalized[lowered] = text
    return normalized


def _response_status(response: BinaryIO) -> int:
    value = getattr(response, "status", None)
    if value is None and hasattr(response, "getcode"):
        value = response.getcode()
    if type(value) is not int:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response status unavailable"
        )
    return value


def _response_url(response: BinaryIO) -> str:
    if not hasattr(response, "geturl"):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response URL unavailable"
        )
    value = response.geturl()
    if not isinstance(value, str):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response URL differs"
        )
    return value


def _read_capped(response: BinaryIO, *, declared_length: int | None) -> bytes:
    try:
        payload = response.read(MAX_RESPONSE_BYTES + 1)
        trailing = response.read(1)
    except Exception as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response body read failed"
        ) from exc
    if not isinstance(payload, bytes) or not isinstance(trailing, bytes):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response body is not bytes"
        )
    if len(payload) > MAX_RESPONSE_BYTES or trailing:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response body exceeds cap"
        )
    if declared_length is not None and len(payload) != declared_length:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "declared response length differs"
        )
    return payload


def read_registered_response(response: BinaryIO) -> TransportResult:
    if _response_status(response) != 200:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "terminal response status differs"
        )
    if _response_url(response) != SOURCE_URL:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "final response URL differs"
        )
    headers = _response_headers(response)
    content_type = headers.get("content-type", "")
    media_parts = [part.strip().lower() for part in content_type.split(";")]
    if not media_parts or media_parts[0] != "application/json" or any(
        part not in {"charset=utf-8"} for part in media_parts[1:]
    ):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response content type differs"
        )
    encoding = headers.get("content-encoding")
    if encoding is None:
        normalized_encoding = "absent"
    elif encoding.lower() == "identity" and "," not in encoding:
        normalized_encoding = "identity"
    else:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response content encoding differs"
        )
    length = headers.get("content-length")
    transfer = headers.get("transfer-encoding")
    if length is not None and transfer is not None:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "response framing conflicts"
        )
    declared: int | None = None
    if length is not None:
        if not length.isascii() or not length.isdecimal() or str(int(length)) != length:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "Content-Length differs"
            )
        declared = int(length)
        if declared > MAX_RESPONSE_BYTES:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "Content-Length exceeds cap"
            )
        framing = "content_length"
    elif transfer is not None:
        if transfer.lower() != "chunked" or "," in transfer:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "Transfer-Encoding differs"
            )
        framing = "chunked"
    else:
        if getattr(response, "will_close", True) is not True:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "close-delimited framing differs"
            )
        framing = "close"
    body = _read_capped(response, declared_length=declared)
    return TransportResult(
        body=body,
        observed_bytes=len(body),
        body_sha256=_sha256_bytes(body),
        framing=framing,
        content_encoding=normalized_encoding,
    )


def _open_live_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)
    try:
        return opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        try:
            exc.close()
        finally:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["transport_or_json"], "terminal HTTP response refused"
            ) from exc
    except (OSError, urllib.error.URLError) as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["transport_or_json"], "public metadata request failed"
        ) from exc


def fetch_and_attest(
    *,
    opener: Callable[[urllib.request.Request, float], BinaryIO],
    ledger: AccessLedger,
    public_request: bool,
) -> WrapperResult:
    request = build_registered_request()
    if public_request:
        ledger.increment("public_HTTP_requests")
    else:
        ledger.increment("mock_HTTP_calls")
    response = opener(request, HTTP_TIMEOUT_SECONDS)
    try:
        transport = read_registered_response(response)
    finally:
        try:
            response.close()
        except Exception:
            pass
    ledger.increment("accepted_response_bodies")
    ledger.increment("response_body_bytes", transport.observed_bytes)
    try:
        source = attestor.attest_inventory(transport.body)
    except attestor.SourceAwareRefusal as exc:
        if exc.route == "MARC1SA-F02":
            route = FAILURE_ROUTES["transport_or_json"]
        elif exc.route == "MARC1SA-F03":
            route = FAILURE_ROUTES["target_or_semantics"]
        else:
            route = FAILURE_ROUTES["privacy_or_resource"]
        raise LiveMetadataRefusal(route, exc.safe_reason) from exc
    ledger.increment("metadata_parses")
    ledger.increment("attestations")
    if source.selection_available:
        ledger.increment("available_selections")
    return WrapperResult(
        source_attestation=source,
        wrapper_route=SOURCE_ROUTE_MAP[source.route],
        transport=transport,
    )


def preconsumption_machine_gate(
    root: str | Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "thread environment is not one"
        )
    try:
        free_bytes = int(disk_usage_reader(Path(root)).free)
        logical_cpus = cpu_count_reader()
        load_values = loadavg_reader()
        peak_rss = int(rss_reader())
    except Exception as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "machine metric unavailable"
        ) from exc
    if logical_cpus is None or logical_cpus <= 0 or not load_values:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "CPU or load metric unavailable"
        )
    load_one = float(load_values[0])
    normalized = load_one / logical_cpus
    if (
        free_bytes < MINIMUM_FREE_DISK_BYTES
        or not math.isfinite(load_one)
        or load_one < 0
        or normalized > MAX_LOAD_PER_LOGICAL_CPU
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["machine_or_output"], "machine resource cap failed"
        )
    return {
        "passed_before_consumed_marker": True,
        "free_disk_bytes": free_bytes,
        "logical_CPUs": logical_cpus,
        "one_minute_load": load_one,
        "one_minute_load_per_logical_CPU": normalized,
        "peak_RSS_bytes_before_consumption": peak_rss,
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
    }


def _source_summary(result: WrapperResult) -> dict[str, Any]:
    source = result.source_attestation
    predicates = source.predicate_vector
    return {
        "source_aware_route": source.route,
        "wrapper_route": result.wrapper_route,
        "selection_available": source.selection_available,
        "selection_unavailable_reason": source.selection_unavailable_reason,
        "historical_differences": list(source.historical_differences),
        "file_rows": predicates["row_count"],
        "participant_archives": predicates["participant_archive_count"],
        "supplementary_rows": predicates["supplementary_row_count"],
        "declared_record_bytes": predicates["declared_byte_total"],
        "unknown_extra_field_rows": predicates["unknown_extra_field_rows"],
        "supplied_MD5_present_count": predicates["supplied_MD5_present_count"],
        "computed_MD5_present_count": predicates["computed_MD5_present_count"],
        "MD5_pair_agreement_count": predicates["MD5_pair_agreement_count"],
        "hashes": dict(source.hashes),
    }


def _private_manifest(
    result: WrapperResult,
    *,
    generated: bool,
    proof: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.marc1_source_aware_live_metadata.private",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "generated": generated,
        "source": {
            "provider": SOURCE_PROVIDER,
            "record_id": SOURCE_RECORD_ID,
            "version": SOURCE_VERSION,
            "DOI": SOURCE_DOI,
        },
        "transport": {
            "observed_body_bytes": result.transport.observed_bytes,
            "raw_response_SHA256": result.transport.body_sha256,
            "framing": result.transport.framing,
            "content_encoding": result.transport.content_encoding,
        },
        "attestation": dict(result.source_attestation.private_record),
        "wrapper_route": result.wrapper_route,
        "proof": dict(proof),
        "payload_requests": 0,
        "payload_bytes": 0,
        "signal_reads": 0,
        "target_reads": 0,
        "model_runs": 0,
        "scoring_events": 0,
    }


def _walk_public(value: Any, *, key: str | None = None) -> None:
    if isinstance(value, dict):
        for nested_key, nested in value.items():
            _walk_public(nested, key=str(nested_key))
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested, key=key)
    elif isinstance(value, str) and PRIVATE_STRING_RE.search(value):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "public private-value pattern is forbidden"
        )


def validate_public_report(report: Mapping[str, Any]) -> None:
    allowed = {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "generated",
        "source",
        "transport",
        "source_aware_summary",
        "generated_family_routes",
        "deterministic_replay",
        "refusal_summary",
        "acceptance_gates",
        "proof",
        "resources",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    if set(report) != allowed:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "public report fields differ"
        )
    _walk_public(report)
    if report["source"] != {
        "provider": SOURCE_PROVIDER,
        "record_id": SOURCE_RECORD_ID,
        "version": SOURCE_VERSION,
        "DOI": SOURCE_DOI,
    }:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "public source identity differs"
        )
    if len(_canonical_json_bytes(report)) > MAX_REPORT_BYTES:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "public report exceeds cap"
        )


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    report_path = Path(path)
    if report_path.name != REPORT_NAME or report_path.is_symlink():
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "aggregate report path differs"
        )
    try:
        payload = report_path.read_bytes()
    except OSError as exc:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "aggregate report unavailable"
        ) from exc
    if len(payload) > MAX_REPORT_BYTES:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "aggregate report exceeds cap"
        )
    value = _strict_json(payload, route=FAILURE_ROUTES["privacy_or_resource"])
    if not isinstance(value, dict):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "aggregate report differs"
        )
    validate_public_report(value)
    return value


def _forbidden_counters_zero(counters: Mapping[str, int]) -> bool:
    forbidden = {
        "participant_archive_requests",
        "payload_requests",
        "payload_bytes",
        "signal_reads",
        "target_reads",
        "model_runs",
        "training_runs",
        "prediction_sets",
        "scoring_events",
        "provider_model_calls",
        "hardware_operations",
        "operations_on_other_projects",
        "retries",
        "reruns",
        "claim_upgrades",
    }
    return all(counters.get(name) == 0 for name in forbidden)


def _enforce_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    combined_output_bytes: int,
    report_bytes: int,
    environ: Mapping[str, str],
) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "thread environment differs"
        )
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes < 0
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or combined_output_bytes > MAX_COMBINED_OUTPUT_BYTES
        or combined_output_bytes > MAX_INCREMENTAL_DISK_BYTES
        or report_bytes > MAX_REPORT_BYTES
    ):
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "resource cap failed"
        )


def _build_report(
    result: WrapperResult,
    *,
    generated: bool,
    proof: Mapping[str, Any],
    machine: Mapping[str, Any],
    ledger: AccessLedger,
    runtime_seconds: float,
    peak_rss_bytes: int,
    combined_output_bytes: int,
    family_routes: Mapping[str, str] | None,
    deterministic_replay: bool,
    refusals: Sequence[str],
    anticipated_counters: Mapping[str, int],
    status: str = "complete",
    route: str | None = None,
) -> dict[str, Any]:
    report = {
        "schema_name": "neurodecodekit.marc1_source_aware_live_metadata_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": status,
        "route": route or (GENERATED_ROUTE if generated else result.wrapper_route),
        "generated": generated,
        "source": {
            "provider": SOURCE_PROVIDER,
            "record_id": SOURCE_RECORD_ID,
            "version": SOURCE_VERSION,
            "DOI": SOURCE_DOI,
        },
        "transport": {
            "request_attempts": ledger.values["mock_HTTP_calls"]
            + ledger.values["public_HTTP_requests"],
            "public_request_attempts": ledger.values["public_HTTP_requests"],
            "redirects": 0,
            "accepted_body_bytes": result.transport.observed_bytes,
            "raw_response_SHA256": result.transport.body_sha256,
            "framing": result.transport.framing,
            "content_encoding": result.transport.content_encoding,
        },
        "source_aware_summary": _source_summary(result),
        "generated_family_routes": dict(family_routes or {}),
        "deterministic_replay": deterministic_replay,
        "refusal_summary": {
            "required": len(GENERATED_REFUSALS) if generated else 0,
            "passed": len(refusals),
            "names": list(refusals),
        },
        "acceptance_gates": {
            name: True for name in ACCEPTANCE_GATES
        },
        "proof": dict(proof),
        "resources": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "combined_output_bytes": combined_output_bytes,
            "incremental_disk_bytes": combined_output_bytes,
            "minimum_free_disk_bytes": machine.get("free_disk_bytes"),
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "end_to_end_latency_measured": False,
        },
        "access_counters": dict(anticipated_counters),
        "warnings": [
            "Metadata identity is not neural or language evidence.",
            "Provider MD5 never substitutes for SHA-256 over acquired payload bytes.",
            "Participant archives payloads signals targets models and scores remain unavailable.",
        ],
        "unavailable_fields": [
            "participant_payloads",
            "acquired_payload_SHA256",
            "signal_samples",
            "channels",
            "events",
            "movement_onset",
            "EOG",
            "EMG",
            "targets",
            "model_predictions",
            "decoding_metrics",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "same_thought_to_text_path": True,
            "is_pivot": False,
            "engineering_capability": (
                "one bounded source-aware metadata response can yield a private cohort "
                "identity or aggregate drift diagnosis"
            ),
            "scientific_claim_not_established": (
                "no neural effect decoding accuracy language decoding or thought-to-text "
                "capability was established"
            ),
            "scientific_claim_established": False,
        },
    }
    validate_public_report(report)
    return report


def _stabilize_outputs(
    result: WrapperResult,
    *,
    marker: Mapping[str, Any],
    private: Mapping[str, Any] | None,
    generated: bool,
    proof: Mapping[str, Any],
    machine: Mapping[str, Any],
    ledger: AccessLedger,
    runtime_seconds: float,
    peak_rss_bytes: int,
    family_routes: Mapping[str, str] | None,
    deterministic_replay: bool,
    refusals: Sequence[str],
    status: str = "complete",
    route: str | None = None,
    output_file_count: int = 3,
    output_directory_count: int = 1,
    capability_revalidation_count: int | None = None,
    already_written_bytes: int = 0,
    inspection_count: int = 1,
    cleanup: bool = False,
) -> tuple[bytes, bytes | None, bytes, dict[str, Any]]:
    marker_bytes = _canonical_json_bytes(marker)
    private_bytes = _canonical_json_bytes(private) if private is not None else None
    report_bytes = b""
    report: dict[str, Any] = {}
    for _ in range(12):
        combined = len(marker_bytes) + len(report_bytes) + (
            len(private_bytes) if private_bytes is not None else 0
        )
        anticipated = dict(ledger.values)
        anticipated["capability_revalidations"] += (
            capability_revalidation_count
            if capability_revalidation_count is not None
            else output_file_count + output_directory_count
        )
        anticipated["output_directories_created"] += output_directory_count
        anticipated["output_files_created"] += output_file_count
        anticipated["output_bytes"] += combined - already_written_bytes
        anticipated["public_report_inspections"] += inspection_count
        if cleanup:
            anticipated["cleanup_file_unlinks"] += output_file_count
            anticipated["cleanup_directory_removals"] += 1
        report = _build_report(
            result,
            generated=generated,
            proof=proof,
            machine=machine,
            ledger=ledger,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            combined_output_bytes=combined,
            family_routes=family_routes,
            deterministic_replay=deterministic_replay,
            refusals=refusals,
            anticipated_counters=anticipated,
            status=status,
            route=route,
        )
        candidate = _canonical_json_bytes(report)
        if len(candidate) == len(report_bytes):
            report_bytes = candidate
            break
        report_bytes = candidate
    else:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "output size did not stabilize"
        )
    combined = len(marker_bytes) + len(report_bytes) + (
        len(private_bytes) if private_bytes is not None else 0
    )
    if report["resources"]["combined_output_bytes"] != combined:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "combined output accounting differs"
        )
    _enforce_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        combined_output_bytes=combined,
        report_bytes=len(report_bytes),
        environ={key: "1" for key in THREAD_ENV_KEYS},
    )
    return marker_bytes, private_bytes, report_bytes, report


def _expect_refusal(
    operation: Callable[[], Any],
    *,
    route: str,
) -> str:
    try:
        operation()
    except LiveMetadataRefusal as exc:
        if exc.route != route:
            raise AssertionError(f"refusal used {exc.route}, expected {route}") from exc
        return exc.route
    raise AssertionError("operation did not refuse")


def _family_body(name: str, *, reverse: bool = False) -> bytes:
    rows = attestor.build_generated_family(
        name,
        reverse_rows=reverse,
        reverse_keys=reverse,
    )
    return _canonical_json_bytes(rows)


def _memory_opener(
    body: bytes,
    *,
    headers: Sequence[tuple[str, str]] | None = None,
    status: int = 200,
    url: str = SOURCE_URL,
    response_type: type[_MemoryResponse] = _MemoryResponse,
) -> Callable[[urllib.request.Request, float], BinaryIO]:
    def open_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
        del timeout
        validate_registered_request(request)
        return response_type(body, status=status, url=url, headers=headers)

    return open_once


def _run_generated_refusals(
    *,
    base_body: bytes,
    output_dir: str | os.PathLike[str],
    audit_ledger: AccessLedger,
) -> tuple[str, ...]:
    routes: list[str] = []

    registered_like = Path(tempfile.gettempdir()) / REAL_ROOT_RELATIVE_PATH
    routes.append(
        _expect_refusal(
            lambda: acquire_generated_output_capability(registered_like, AccessLedger()),
            route=FAILURE_ROUTES["machine_or_output"],
        )
    )
    dirty = AccessLedger()
    dirty.increment("generated_fixtures")
    routes.append(
        _expect_refusal(
            lambda: acquire_generated_output_capability(output_dir, dirty),
            route=FAILURE_ROUTES["machine_or_output"],
        )
    )
    existing = Path(tempfile.gettempdir()) / "neurodecodekit-marc1sa-existing"
    existing.mkdir(exist_ok=True)
    try:
        routes.append(
            _expect_refusal(
                lambda: acquire_generated_output_capability(existing, AccessLedger()),
                route=FAILURE_ROUTES["machine_or_output"],
            )
        )
    finally:
        existing.rmdir()

    wrong_method = build_registered_request()
    wrong_method.method = "POST"
    routes.append(
        _expect_refusal(
            lambda: validate_registered_request(wrong_method),
            route=FAILURE_ROUTES["transport_or_json"],
        )
    )
    wrong_url = urllib.request.Request(
        SOURCE_URL + "&page=2", headers=REQUEST_HEADERS, method="GET"
    )
    routes.append(
        _expect_refusal(
            lambda: validate_registered_request(wrong_url),
            route=FAILURE_ROUTES["transport_or_json"],
        )
    )
    body_request = urllib.request.Request(
        SOURCE_URL, data=b"{}", headers=REQUEST_HEADERS, method="GET"
    )
    routes.append(
        _expect_refusal(
            lambda: validate_registered_request(body_request),
            route=FAILURE_ROUTES["transport_or_json"],
        )
    )
    auth_request = build_registered_request()
    auth_request.add_header("Authorization", "Bearer generated")
    routes.append(
        _expect_refusal(
            lambda: validate_registered_request(auth_request),
            route=FAILURE_ROUTES["transport_or_json"],
        )
    )

    response_cases: list[_MemoryResponse] = [
        _MemoryResponse(base_body, status=503),
        _MemoryResponse(base_body, url=SOURCE_URL + "&redirected=1"),
        _MemoryResponse(base_body, headers=[("Content-Type", "text/plain")]),
        _MemoryResponse(
            base_body,
            headers=[("Content-Type", "application/json"), ("Content-Encoding", "gzip")],
        ),
        _MemoryResponse(
            base_body,
            headers=[
                ("Content-Type", "application/json"),
                ("Content-Encoding", "identity"),
                ("Content-Encoding", "identity"),
            ],
        ),
        _MemoryResponse(
            base_body,
            headers=[
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(base_body))),
                ("Transfer-Encoding", "chunked"),
            ],
        ),
        _MemoryResponse(
            base_body,
            headers=[("Content-Type", "application/json"), ("Content-Length", "+1")],
        ),
        _MemoryResponse(
            base_body,
            headers=[
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(base_body) + 1)),
            ],
        ),
        _MemoryResponse(b"x" * (MAX_RESPONSE_BYTES + 1)),
    ]
    for response in response_cases:
        routes.append(
            _expect_refusal(
                lambda response=response: read_registered_response(response),
                route=FAILURE_ROUTES["transport_or_json"],
            )
        )

    class NonBytesResponse(_MemoryResponse):
        def read(self, size: int = -1) -> Any:
            del size
            return "not-bytes"

    class BrokenResponse(_MemoryResponse):
        def read(self, size: int = -1) -> bytes:
            del size
            raise OSError("generated read failure")

    for response in (
        NonBytesResponse(base_body),
        BrokenResponse(base_body),
    ):
        routes.append(
            _expect_refusal(
                lambda response=response: read_registered_response(response),
                route=FAILURE_ROUTES["transport_or_json"],
            )
        )

    malformed_bodies = (
        b"\xff",
        b"{",
        b'[{"id":1,"id":2}]',
        b'[{"id":NaN}]',
    )
    for body in malformed_bodies:
        routes.append(
            _expect_refusal(
                lambda body=body: fetch_and_attest(
                    opener=_memory_opener(body), ledger=AccessLedger(), public_request=False
                ),
                route=FAILURE_ROUTES["transport_or_json"],
            )
        )

    rows = attestor.build_generated_family("observed_extension_exact")
    rows[0]["target_text"] = "forbidden"
    routes.append(
        _expect_refusal(
            lambda: fetch_and_attest(
                opener=_memory_opener(_canonical_json_bytes(rows)),
                ledger=AccessLedger(),
                public_request=False,
            ),
            route=FAILURE_ROUTES["target_or_semantics"],
        )
    )
    rows = attestor.build_generated_family("observed_extension_exact")
    rows[0].pop("name")
    routes.append(
        _expect_refusal(
            lambda: fetch_and_attest(
                opener=_memory_opener(_canonical_json_bytes(rows)),
                ledger=AccessLedger(),
                public_request=False,
            ),
            route=FAILURE_ROUTES["target_or_semantics"],
        )
    )
    rows = attestor.build_generated_family("observed_extension_exact")
    rows[0]["computed_md5"] = "0" * 32
    routes.append(
        _expect_refusal(
            lambda: fetch_and_attest(
                opener=_memory_opener(_canonical_json_bytes(rows)),
                ledger=AccessLedger(),
                public_request=False,
            ),
            route=FAILURE_ROUTES["target_or_semantics"],
        )
    )

    leaked = {
        key: None
        for key in (
            "schema_name",
            "schema_version",
            "lane_id",
            "status",
            "route",
            "generated",
            "source",
            "transport",
            "source_aware_summary",
            "generated_family_routes",
            "deterministic_replay",
            "refusal_summary",
            "acceptance_gates",
            "proof",
            "resources",
            "access_counters",
            "warnings",
            "unavailable_fields",
            "claim_boundary",
        )
    }
    leaked["source"] = {
        "provider": SOURCE_PROVIDER,
        "record_id": SOURCE_RECORD_ID,
        "version": SOURCE_VERSION,
        "DOI": SOURCE_DOI,
    }
    leaked["warnings"] = ["sub-01"]
    routes.append(
        _expect_refusal(
            lambda: validate_public_report(leaked),
            route=FAILURE_ROUTES["privacy_or_resource"],
        )
    )
    for runtime, rss, environment in (
        (MAX_RUNTIME_SECONDS + 1, 1, {key: "1" for key in THREAD_ENV_KEYS}),
        (0.1, MAX_PEAK_RSS_BYTES + 1, {key: "1" for key in THREAD_ENV_KEYS}),
        (0.1, 1, {key: ("2" if key == THREAD_ENV_KEYS[0] else "1") for key in THREAD_ENV_KEYS}),
    ):
        routes.append(
            _expect_refusal(
                lambda runtime=runtime, rss=rss, environment=environment: _enforce_resources(
                    runtime_seconds=runtime,
                    peak_rss_bytes=rss,
                    combined_output_bytes=1,
                    report_bytes=1,
                    environ=environment,
                ),
                route=FAILURE_ROUTES["privacy_or_resource"],
            )
        )
    malformed_evidence = GreenWrapperEvidence("bad", 1, 1, 1, "bad")
    routes.append(
        _expect_refusal(
            lambda: verify_green_wrapper_evidence(_repo_root(), malformed_evidence, AccessLedger()),
            route=FAILURE_ROUTES["proof"],
        )
    )
    second = AccessLedger()
    second.increment("capability_acquisitions")
    routes.append(
        _expect_refusal(
            lambda: acquire_generated_output_capability(output_dir, second),
            route=FAILURE_ROUTES["machine_or_output"],
        )
    )
    if len(routes) != len(GENERATED_REFUSALS):
        raise AssertionError("generated refusal count differs")
    audit_ledger.increment("adversarial_cases", len(routes))
    audit_ledger.increment("adversarial_mock_HTTP_calls", 7)
    audit_ledger.increment("adversarial_response_reads", 18)
    return tuple(routes)


def qualify_generated_mock_wrapper(
    output_dir: str | os.PathLike[str],
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> WrapperOutcome:
    """Exercise the complete wrapper with generated bodies and mocked HTTP."""

    ledger = AccessLedger()
    capability = acquire_generated_output_capability(output_dir, ledger)
    started = clock()
    selected_environ = os.environ if environ is None else environ
    try:
        decision = load_green_decision(repo_root or _repo_root(), ledger)
        family_results: dict[str, WrapperResult] = {}
        family_routes: dict[str, str] = {}
        for index, name in enumerate(GENERATED_FAMILIES):
            body = _family_body(name)
            ledger.increment("generated_fixtures")
            ledger.increment("generated_rows", 55)
            ledger.increment("generated_input_bytes", len(body))
            if index % 3 == 0:
                headers = [("Content-Type", "application/json")]
            elif index % 3 == 1:
                headers = [
                    ("Content-Type", "application/json; charset=UTF-8"),
                    ("Content-Length", str(len(body))),
                ]
            else:
                headers = [
                    ("Content-Type", "application/json"),
                    ("Transfer-Encoding", "chunked"),
                ]
            result = fetch_and_attest(
                opener=_memory_opener(body, headers=headers),
                ledger=ledger,
                public_request=False,
            )
            if result.source_attestation.route != attestor.FAMILY_ROUTES[name]:
                raise LiveMetadataRefusal(
                    FAILURE_ROUTES["privacy_or_resource"], "generated family route differs"
                )
            family_results[name] = result
            family_routes[name] = result.source_attestation.route
        canonical = family_results["observed_extension_exact"]
        replay_body = _family_body("observed_extension_exact", reverse=True)
        ledger.increment("generated_fixtures")
        ledger.increment("generated_rows", 55)
        ledger.increment("generated_input_bytes", len(replay_body))
        replay = fetch_and_attest(
            opener=_memory_opener(replay_body),
            ledger=ledger,
            public_request=False,
        )
        deterministic = all(
            canonical.source_attestation.hashes[name]
            == replay.source_attestation.hashes[name]
            for name in attestor.SEMANTIC_HASHES
        )
        if not deterministic:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "semantic replay differs"
            )
        refusals = _run_generated_refusals(
            base_body=_family_body("observed_extension_exact"),
            output_dir=output_dir,
            audit_ledger=ledger,
        )
        runtime_seconds = clock() - started
        peak_rss_bytes = int(rss_reader())
        proof = {
            "green_decision_commit": GREEN_DECISION_COMMIT,
            "green_decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "green_decision_base_job_id": GREEN_DECISION_BASE_JOB_ID,
            "green_decision_optional_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "decision_registry_SHA256": DECISION_SHA256,
            "request_SHA256": REQUEST_SHA256,
            "attestor_source_SHA256": ATTESTOR_SOURCE_SHA256,
            "decision_scope_is_metadata_only": (
                decision["authorization"]["payload_acquisition_or_download_authorized_now"]
                is False
            ),
        }
        marker = {
            "schema_name": "neurodecodekit.marc1_source_aware_live_metadata.consumed",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "generated": True,
            "registered_execution_ordinal": 0,
            "network_requests": 0,
            "payload_bytes": 0,
        }
        private = _private_manifest(canonical, generated=True, proof=proof)
        machine = {
            "free_disk_bytes": None,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
        }
        marker_bytes, private_bytes, report_bytes, report = _stabilize_outputs(
            canonical,
            marker=marker,
            private=private,
            generated=True,
            proof=proof,
            machine=machine,
            ledger=ledger,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            family_routes=family_routes,
            deterministic_replay=deterministic,
            refusals=refusals,
            cleanup=True,
        )
        combined = len(marker_bytes) + len(private_bytes or b"") + len(report_bytes)
        _enforce_resources(
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            combined_output_bytes=combined,
            report_bytes=len(report_bytes),
            environ=selected_environ,
        )
        _create_output_root(capability)
        _write_relative(capability, MARKER_NAME, marker_bytes, mode=0o600)
        if private_bytes is None:
            raise AssertionError("generated private manifest is unavailable")
        _write_relative(capability, PRIVATE_NAME, private_bytes, mode=0o600)
        _write_relative(capability, REPORT_NAME, report_bytes, mode=0o644)
        inspected = _strict_json(
            _read_public_relative(capability),
            route=FAILURE_ROUTES["privacy_or_resource"],
        )
        if inspected != report:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "aggregate replay differs"
            )
        _cleanup_generated_output(capability)
        if ledger.values != report["access_counters"] or not _forbidden_counters_zero(
            ledger.values
        ):
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "final access ledger differs"
            )
        if os.path.lexists(os.fspath(output_dir)):
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "generated output remains"
            )
        return WrapperOutcome(
            report=report,
            report_path=Path(output_dir) / REPORT_NAME,
            private_manifest_path=Path(output_dir) / PRIVATE_NAME,
            marker_path=Path(output_dir) / MARKER_NAME,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            combined_output_bytes=combined,
            output_removed=True,
            marker_sha256=_sha256_bytes(marker_bytes),
            private_manifest_sha256=_sha256_bytes(private_bytes),
            report_sha256=_sha256_bytes(report_bytes),
        )
    except Exception:
        _cleanup_generated_output(capability, suppress=True)
        raise
    finally:
        capability.close()


def _failure_result(
    refusal: LiveMetadataRefusal,
    *,
    ledger: AccessLedger,
    runtime_seconds: float,
    peak_rss_bytes: int,
    marker_bytes: int,
    proof: Mapping[str, Any],
    machine: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    placeholder = WrapperResult(
        source_attestation=attestor.Attestation(
            route="MARC1SA-R4",
            predicate_vector={
                "row_count": 0,
                "participant_archive_count": 0,
                "supplementary_row_count": 0,
                "declared_byte_total": 0,
                "unknown_extra_field_rows": 0,
                "supplied_MD5_present_count": 0,
                "computed_MD5_present_count": 0,
                "MD5_pair_agreement_count": 0,
            },
            hashes={name: None for name in attestor.IDENTITY_DOMAINS},
            historical_differences=(),
            selection_available=False,
            selection_unavailable_reason="execution_failed_before_attestation",
            private_record={},
        ),
        wrapper_route=BLOCKED_ROUTE,
        transport=TransportResult(b"", 0, _sha256_bytes(b""), "unavailable", "unavailable"),
    )
    report_bytes = b""
    report: dict[str, Any] = {}
    for _ in range(12):
        combined = marker_bytes + len(report_bytes)
        anticipated = dict(ledger.values)
        anticipated["capability_revalidations"] += 1
        anticipated["output_files_created"] += 1
        anticipated["output_bytes"] += len(report_bytes)
        anticipated["public_report_inspections"] += 1
        report = _build_report(
            placeholder,
            generated=False,
            proof=proof,
            machine=machine,
            ledger=ledger,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            combined_output_bytes=combined,
            family_routes=None,
            deterministic_replay=False,
            refusals=(),
            anticipated_counters=anticipated,
            status="failed",
            route=refusal.route,
        )
        report["warnings"] = [
            f"Execution consumed and parked: {refusal.safe_reason}.",
            "No retry rerun resume fallback or payload continuation is available.",
            "No scientific claim was upgraded.",
        ]
        validate_public_report(report)
        candidate = _canonical_json_bytes(report)
        if len(candidate) == len(report_bytes):
            report_bytes = candidate
            break
        report_bytes = candidate
    else:
        raise LiveMetadataRefusal(
            FAILURE_ROUTES["privacy_or_resource"], "failure output did not stabilize"
        )
    combined = marker_bytes + len(report_bytes)
    report["resources"]["combined_output_bytes"] = combined
    report["resources"]["incremental_disk_bytes"] = combined
    report_bytes = _canonical_json_bytes(report)
    _enforce_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        combined_output_bytes=marker_bytes + len(report_bytes),
        report_bytes=len(report_bytes),
        environ={key: "1" for key in THREAD_ENV_KEYS},
    )
    return report_bytes, report


def execute_registered_metadata_check(
    root: str | Path,
    *,
    evidence: GreenWrapperEvidence,
    environ: Mapping[str, str] | None = None,
    opener: Callable[[urllib.request.Request, float], BinaryIO] = _open_live_once,
    proof_verifier: Callable[[str | Path, GreenWrapperEvidence, AccessLedger], Mapping[str, Any]] = verify_green_wrapper_evidence,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> WrapperOutcome:
    """Consume the one registered public metadata response and stop."""

    repo = Path(root)
    ledger = AccessLedger()
    capability = acquire_live_output_capability(repo, ledger)
    marker_written = False
    report_written = False
    marker_payload = b""
    proof: dict[str, Any] = {}
    machine: dict[str, Any] = {}
    started = clock()
    try:
        implementation = proof_verifier(repo, evidence, ledger)
        proof = {
            "green_decision_commit": GREEN_DECISION_COMMIT,
            "green_decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "implementation_commit": evidence.implementation_commit,
            "implementation_CI_run_id": evidence.implementation_ci_run_id,
            "implementation_base_job_id": evidence.implementation_base_job_id,
            "implementation_optional_job_id": evidence.implementation_optional_job_id,
            "implementation_registry_SHA256": evidence.implementation_registry_sha256,
            "implementation_preexecution_state": (
                implementation["execution_state"]["public_execution_consumed"] is False
            ),
        }
        selected_environ = os.environ if environ is None else environ
        machine = preconsumption_machine_gate(
            repo,
            environ=selected_environ,
            disk_usage_reader=disk_usage_reader,
            cpu_count_reader=cpu_count_reader,
            loadavg_reader=loadavg_reader,
            rss_reader=rss_reader,
        )
        _create_output_root(capability)
        marker = {
            "schema_name": "neurodecodekit.marc1_source_aware_live_metadata.consumed",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "generated": False,
            "registered_execution_ordinal": 1,
            "implementation_commit": evidence.implementation_commit,
            "implementation_CI_run_id": evidence.implementation_ci_run_id,
            "request_attempt_cap": 1,
            "retry_or_rerun_available": False,
        }
        marker_payload = _canonical_json_bytes(marker)
        _write_relative(capability, MARKER_NAME, marker_payload, mode=0o600)
        marker_written = True
        result = fetch_and_attest(opener=opener, ledger=ledger, public_request=True)
        runtime_seconds = clock() - started
        peak_rss_bytes = int(rss_reader())
        private = _private_manifest(result, generated=False, proof=proof)
        marker_bytes, private_bytes, report_bytes, report = _stabilize_outputs(
            result,
            marker=marker,
            private=private,
            generated=False,
            proof=proof,
            machine=machine,
            ledger=ledger,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            family_routes=None,
            deterministic_replay=False,
            refusals=(),
            cleanup=False,
            output_file_count=2,
            output_directory_count=0,
            capability_revalidation_count=2,
            already_written_bytes=len(marker_payload),
        )
        if marker_bytes != marker_payload or private_bytes is None:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "live output serialization differs"
            )
        combined = len(marker_bytes) + len(private_bytes) + len(report_bytes)
        _enforce_resources(
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            combined_output_bytes=combined,
            report_bytes=len(report_bytes),
            environ=selected_environ,
        )
        _write_relative(capability, PRIVATE_NAME, private_bytes, mode=0o600)
        _write_relative(capability, REPORT_NAME, report_bytes, mode=0o644)
        report_written = True
        inspected = _strict_json(
            _read_public_relative(capability),
            route=FAILURE_ROUTES["privacy_or_resource"],
        )
        if inspected != report or ledger.values != report["access_counters"]:
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "live aggregate replay differs"
            )
        if not _forbidden_counters_zero(ledger.values):
            raise LiveMetadataRefusal(
                FAILURE_ROUTES["privacy_or_resource"], "forbidden live counter differs"
            )
        output_root = repo / REAL_ROOT_RELATIVE_PATH
        return WrapperOutcome(
            report=report,
            report_path=output_root / REPORT_NAME,
            private_manifest_path=output_root / PRIVATE_NAME,
            marker_path=output_root / MARKER_NAME,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            combined_output_bytes=combined,
            output_removed=False,
            marker_sha256=_sha256_bytes(marker_bytes),
            private_manifest_sha256=_sha256_bytes(private_bytes),
            report_sha256=_sha256_bytes(report_bytes),
        )
    except LiveMetadataRefusal as exc:
        if marker_written and not report_written and capability.output_fd is not None:
            runtime_seconds = clock() - started
            peak_rss_bytes = int(rss_reader())
            try:
                failure_bytes, _ = _failure_result(
                    exc,
                    ledger=ledger,
                    runtime_seconds=runtime_seconds,
                    peak_rss_bytes=peak_rss_bytes,
                    marker_bytes=len(marker_payload),
                    proof=proof,
                    machine=machine,
                )
                _write_relative(capability, REPORT_NAME, failure_bytes, mode=0o644)
                persisted = _strict_json(
                    _read_public_relative(capability),
                    route=FAILURE_ROUTES["privacy_or_resource"],
                )
                if not isinstance(persisted, dict):
                    raise LiveMetadataRefusal(
                        FAILURE_ROUTES["privacy_or_resource"],
                        "failure aggregate differs",
                    )
                validate_public_report(persisted)
                if ledger.values != persisted["access_counters"]:
                    raise LiveMetadataRefusal(
                        FAILURE_ROUTES["privacy_or_resource"],
                        "failure access ledger differs",
                    )
            except Exception:
                pass
        raise
    finally:
        capability.close()


def registered_plan() -> dict[str, Any]:
    return {
        "lane_id": LANE_ID,
        "green_parent_decision": {
            "commit": GREEN_DECISION_COMMIT,
            "CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "base_python_job_id": GREEN_DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
        },
        "source": {
            "provider": SOURCE_PROVIDER,
            "record_id": SOURCE_RECORD_ID,
            "version": SOURCE_VERSION,
            "DOI": SOURCE_DOI,
            "request_attempts": 1,
            "response_cap_bytes": MAX_RESPONSE_BYTES,
        },
        "commands": ["plan", "qualify", "inspect", "execute"],
        "generated_families": list(GENERATED_FAMILIES),
        "generated_refusals": list(GENERATED_REFUSALS),
        "acceptance_gates": list(ACCEPTANCE_GATES),
        "payload_requests": 0,
        "payload_bytes": 0,
        "signal_target_model_score_operations": 0,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_source_aware_live_metadata",
        description="Proof-gated source-aware MARC1 metadata check.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the zero-network registered plan.")
    qualify = subparsers.add_parser("qualify", help="Run generated/mock qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect one aggregate report.")
    inspect.add_argument("report")
    execute = subparsers.add_parser("execute", help="Consume the one registered metadata check.")
    execute.add_argument("--implementation-commit", required=True)
    execute.add_argument("--implementation-ci-run-id", required=True, type=int)
    execute.add_argument("--implementation-base-job-id", required=True, type=int)
    execute.add_argument("--implementation-optional-job-id", required=True, type=int)
    execute.add_argument("--implementation-registry-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "plan":
            print(_canonical_json_bytes(registered_plan()).decode("ascii"), end="")
            return 0
        if args.command == "qualify":
            outcome = qualify_generated_mock_wrapper(args.output_dir)
        elif args.command == "inspect":
            print(
                _canonical_json_bytes(inspect_public_result(args.report)).decode("ascii"),
                end="",
            )
            return 0
        else:
            evidence = GreenWrapperEvidence(
                implementation_commit=args.implementation_commit,
                implementation_ci_run_id=args.implementation_ci_run_id,
                implementation_base_job_id=args.implementation_base_job_id,
                implementation_optional_job_id=args.implementation_optional_job_id,
                implementation_registry_sha256=args.implementation_registry_sha256,
            )
            outcome = execute_registered_metadata_check(
                _repo_root(),
                evidence=evidence,
            )
        print(
            _canonical_json_bytes(
                {
                    "status": outcome.report["status"],
                    "route": outcome.report["route"],
                    "report": str(outcome.report_path),
                    "runtime_seconds": outcome.runtime_seconds,
                    "peak_RSS_bytes": outcome.peak_rss_bytes,
                    "combined_output_bytes": outcome.combined_output_bytes,
                    "output_removed": outcome.output_removed,
                    "generated_input_bytes": outcome.report["access_counters"][
                        "generated_input_bytes"
                    ],
                    "mock_HTTP_calls": outcome.report["access_counters"][
                        "mock_HTTP_calls"
                    ],
                    "adversarial_cases": outcome.report["access_counters"][
                        "adversarial_cases"
                    ],
                    "public_HTTP_requests": outcome.report["access_counters"][
                        "public_HTTP_requests"
                    ],
                    "payload_bytes": outcome.report["access_counters"]["payload_bytes"],
                    "marker_sha256": outcome.marker_sha256,
                    "private_manifest_sha256": outcome.private_manifest_sha256,
                    "report_sha256": outcome.report_sha256,
                }
            ).decode("ascii"),
            end="",
        )
        return 0
    except LiveMetadataRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
