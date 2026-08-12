"""Capability-first MARC1 paginated metadata qualification and one-shot executor."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
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


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC1-LM1"
GENERATED_ROUTE = "MARC1LM-G1"
SUCCESS_ROUTE = "MARC1LM-R1"
FAILURE_ROUTES = {
    "MARC1LM-F00": "proof_source_or_green_evidence_mismatch",
    "MARC1LM-F01": "output_capability_or_machine_gate_failure",
    "MARC1LM-F02": "request_identity_or_network_open_failure",
    "MARC1LM-F03": "response_status_URL_header_framing_or_body_failure",
    "MARC1LM-F04": "JSON_schema_target_firewall_or_inventory_failure",
    "MARC1LM-F05": "cohort_split_or_private_manifest_failure",
    "MARC1LM-F06": "output_privacy_replay_or_resource_failure",
    "MARC1LM-F07": "consumption_retry_rerun_fallback_or_amendment_failure",
}

GREEN_DECISION_COMMIT = "060a365a24e75da4297a5c4a3422ff730467ec36"
GREEN_DECISION_CI_RUN_ID = 31_604_608_307
GREEN_DECISION_BASE_JOB_ID = 94_140_250_333
GREEN_DECISION_OPTIONAL_JOB_ID = 94_140_250_412
DECISION_RELATIVE_PATH = Path(
    "registries/marc1_paginated_live_metadata_authorization_decision.v0.json"
)
DECISION_SHA256 = "f66a79adb60656de8a09ef40b56ae5389ac1fbb664a515fe424333c6fecdf366"
REQUEST_RELATIVE_PATH = Path(
    "registries/marc1_paginated_live_metadata_authorization_request.v0.json"
)
REQUEST_SHA256 = "798d05a52e86891467b54a6807475602d9f3530468bd5a4005768e9f966dac9d"
PAGINATION_SOURCE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc1_versioned_pagination.py"
)
PAGINATION_SOURCE_SHA256 = (
    "3dc5f4fdf5792040f153797d708cf27cd8ece8e4dc40b3a0eeaba86071724228"
)
OUTPUT_SOURCE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc1_output_capability_recovery.py"
)
OUTPUT_SOURCE_SHA256 = (
    "40a2d8520102b6502fcad82e1f262613a647335bbad92ef1529204bb5a9166b4"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc1_paginated_live_metadata_implementation.v0.json"
)

REQUEST_PATH = "/v2/articles/29666735/versions/3/files"
REQUEST_QUERY = "page=1&page_size=1000"
REQUEST_URL = f"https://api.figshare.com{REQUEST_PATH}?{REQUEST_QUERY}"
REGISTERED_OUTPUT_PATH = (
    "/private/tmp/neurodecodekit-marc1lm1-live-metadata-20260812"
)
REPORT_NAME = "marc1_paginated_live_metadata_result.v0.json"
PRIVATE_NAME = "marc1_paginated_live_metadata.private.v0.json"
MARKER_NAME = "execution_consumed.v0.json"
OUTPUT_NAMES = (MARKER_NAME, PRIVATE_NAME, REPORT_NAME)

MAX_BODY_BYTES = 2 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 10 * 1024**3
MAX_LOAD_PER_LOGICAL_CPU = 1.0
MAX_TIMEOUT_SECONDS = 20.0
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
EXPECTED_ROWS = 55
EXPECTED_PARTICIPANTS = 45
EXPECTED_SUPPLEMENTARY = 10
EXPECTED_DECLARED_BYTES = 3_683_416_050
FROZEN_SUBJECTS = (
    "sub-08",
    "sub-11",
    "sub-09",
    "sub-23",
    "sub-20",
    "sub-16",
    "sub-42",
    "sub-38",
    "sub-36",
    "sub-30",
    "sub-45",
    "sub-21",
)
FIT_RUNS = (1, 2, 3, 4, 5, 6)
HELDOUT_RUNS = (7, 8)
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
PRIVATE_VALUE_RE = re.compile(r"(?:sub-\d{2}|https?://|\A[0-9a-f]{32}\Z)", re.I)
TARGET_KEY_RE = re.compile(
    r"(?:^|_)(?:answer|condition|event|ground_truth|intended_text|label|outcome|"
    r"quality|reference_text|response|sentence|target|trial)(?:_|$)",
    re.I,
)
PUBLIC_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "proof_posture",
        "source_summary",
        "inventory_summary",
        "cohort_summary",
        "split_summary",
        "transport_summary",
        "hashes",
        "measurements",
        "access_counters",
        "mutation_summary",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
REQUIRED_MUTATIONS = (
    "wrong_decision_hash",
    "wrong_request_query",
    "request_body_present",
    "redirect_status",
    "final_URL_drift",
    "non_200_status",
    "non_JSON_content_type",
    "gzip_content_encoding",
    "duplicate_content_encoding",
    "content_encoding_list",
    "content_length_and_chunked",
    "transfer_encoding_list",
    "malformed_content_length",
    "content_length_mismatch",
    "body_overflow",
    "malformed_JSON",
    "duplicate_JSON_key",
    "non_array_root",
    "non_object_row",
    "target_like_field",
    "fifty_four_rows",
    "fifty_six_rows",
    "row_field_drift",
    "duplicate_file_id",
    "duplicate_filename",
    "download_URL_drift",
    "MD5_disagreement",
    "sub01_anchor_drift",
    "declared_byte_total_drift",
    "cohort_order_drift",
    "split_drift",
    "public_private_leak",
    "output_appears_after_capability",
    "resource_cap_breach",
    "retry_nonzero",
    "second_execution_ordinal",
)
ACCEPTANCE_GATES = (
    "green_decision_and_request_hashes",
    "pagination_and_output_source_hashes",
    "capability_is_first_operation",
    "all_ancestors_no_follow_and_parent_identity_bound",
    "exact_request_serialization",
    "four_transport_cases_accepted",
    "all_accepted_cases_share_semantic_hash",
    "all_required_mutations_refuse",
    "strict_duplicate_key_and_target_firewall",
    "exact_55_45_10_inventory_and_declared_bytes",
    "exact_target_free_12_subject_selection",
    "exact_fit_heldout_split_and_zero_overlap",
    "consumed_executors_not_imported_called_or_modified",
    "three_parent_relative_exclusive_writes",
    "private_public_separation",
    "deterministic_private_manifest_replay",
    "bounded_runtime_RSS_input_output_and_disk",
    "zero_real_network_payload_neural_target_model_score_counters",
    "public_report_inspected_once",
    "generated_outputs_removed_exactly",
)


class PaginatedMetadataRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-LM1 route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC1-LM1 route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(slots=True)
class AccessLedger:
    """Counters for operation order and forbidden-surface auditing."""

    values: dict[str, int] = field(
        default_factory=lambda: {
            "capability_acquisitions": 0,
            "capability_revalidations": 0,
            "repository_reads": 0,
            "decision_loads": 0,
            "deferred_pagination_imports": 0,
            "generated_fixtures": 0,
            "mock_HTTP_calls": 0,
            "real_network_requests": 0,
            "response_body_reads": 0,
            "response_body_bytes": 0,
            "metadata_parses": 0,
            "selections": 0,
            "output_directories_created": 0,
            "output_files_created": 0,
            "output_bytes": 0,
            "public_report_inspections": 0,
            "cleanup_file_unlinks": 0,
            "cleanup_directory_removals": 0,
            "participant_archive_requests": 0,
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
            "claim_upgrades": 0,
            "retries": 0,
            "reruns": 0,
        }
    )

    def increment(self, name: str, amount: int = 1) -> None:
        if name not in self.values or amount < 0:
            raise ValueError("invalid access-ledger update")
        self.values[name] += amount

    def early_snapshot(self) -> dict[str, int]:
        names = (
            "repository_reads",
            "decision_loads",
            "deferred_pagination_imports",
            "generated_fixtures",
            "mock_HTTP_calls",
            "real_network_requests",
            "response_body_reads",
            "metadata_parses",
            "selections",
            "output_bytes",
        )
        return {name: self.values[name] for name in names}


@dataclass(slots=True)
class OutputCapability:
    """Held authority for one absent child under one verified real parent."""

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
class GreenImplementationEvidence:
    """Operator-supplied remote-green proof for the exact implementation."""

    implementation_commit: str
    implementation_registry_sha256: str
    CI_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class FixtureResponse:
    """In-memory response with explicit raw header rows."""

    body: bytes
    status: int = 200
    reported_url: str = REQUEST_URL
    headers: tuple[tuple[str, str], ...] = (
        ("Content-Type", "application/json"),
    )

    def read(self, maximum: int = -1) -> bytes:
        if maximum < 0:
            return self.body
        return self.body[:maximum]

    def geturl(self) -> str:
        return self.reported_url

    def close(self) -> None:
        return None

    def __enter__(self) -> FixtureResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


@dataclass(slots=True)
class FixtureOpener:
    """One-shot mocked opener that records the request without networking."""

    response: FixtureResponse
    calls: int = 0
    observed_request: urllib.request.Request | None = None

    def open(self, request: urllib.request.Request, timeout: float) -> FixtureResponse:
        if timeout <= 0 or self.calls:
            raise PaginatedMetadataRefusal("MARC1LM-F07", "mock opener reused")
        self.calls += 1
        self.observed_request = request
        return self.response


@dataclass(frozen=True)
class QualificationOutcome:
    """Aggregate generated result retained after exact cleanup."""

    report: Mapping[str, Any]
    report_bytes: bytes
    private_sha256: str
    public_sha256: str
    output_path: str
    output_removed: bool
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args: Any, **_kwargs: Any) -> None:
        return None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_temp_parent() -> str:
    return os.path.realpath(tempfile.gettempdir())


def _canonical_json_bytes(value: Any) -> bytes:
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


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _domain_sha256(domain: str, payload: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(domain.encode("ascii"))
    hasher.update(b"\0")
    hasher.update(payload)
    return hasher.hexdigest()


def _peak_rss_bytes() -> int:
    observed = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return observed if sys.platform == "darwin" else observed * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _lexical_output(path: str | os.PathLike[str]) -> tuple[str, str, str]:
    try:
        raw = os.fspath(path)
    except TypeError as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F01", "output path type differs") from exc
    if not isinstance(raw, str) or not raw or "\x00" in raw or not raw.startswith("/"):
        raise PaginatedMetadataRefusal("MARC1LM-F01", "output path is not absolute")
    if raw == "/" or raw != os.path.normpath(raw) or any(
        component in {".", ".."} for component in raw.split("/")
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F01", "output path differs")
    parent, basename = os.path.split(raw)
    if not parent or not basename:
        raise PaginatedMetadataRefusal("MARC1LM-F01", "output basename is empty")
    return raw, parent, basename


def _lstat_ancestors(parent: str) -> os.stat_result:
    current = "/"
    try:
        root_stat = os.lstat(current)
        if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
            raise PaginatedMetadataRefusal("MARC1LM-F01", "root ancestor differs")
        for component in Path(parent).parts[1:]:
            current = os.path.join(current, component)
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
                raise PaginatedMetadataRefusal(
                    "MARC1LM-F01", "output ancestor is not a real directory"
                )
        return os.lstat(parent)
    except PaginatedMetadataRefusal:
        raise
    except OSError as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F01", "output ancestor is unavailable"
        ) from exc


def _require_child_absent(parent_fd: int, basename: str) -> None:
    try:
        os.stat(basename, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F01", "output absence check failed"
        ) from exc
    raise PaginatedMetadataRefusal("MARC1LM-F01", "output already exists")


def acquire_output_capability(
    output_dir: str | os.PathLike[str], *, ledger: AccessLedger
) -> OutputCapability:
    """Acquire output authority before every experiment operation."""

    if any(ledger.early_snapshot().values()):
        raise PaginatedMetadataRefusal("MARC1LM-F01", "capability was not first")
    if (
        not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or any(
            function not in os.supports_dir_fd
            for function in (os.open, os.mkdir, os.stat, os.unlink, os.rmdir)
        )
        or os.stat not in os.supports_follow_symlinks
    ):
        raise PaginatedMetadataRefusal(
            "MARC1LM-F01", "required no-follow primitives unavailable"
        )
    _, parent, basename = _lexical_output(output_dir)
    before = _lstat_ancestors(parent)
    try:
        parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        opened = os.fstat(parent_fd)
        if (
            (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
            or not stat.S_ISDIR(opened.st_mode)
        ):
            raise PaginatedMetadataRefusal(
                "MARC1LM-F01", "parent identity changed during acquisition"
            )
        _require_child_absent(parent_fd, basename)
    except Exception:
        if "parent_fd" in locals():
            os.close(parent_fd)
        raise
    ledger.increment("capability_acquisitions")
    return OutputCapability(
        parent_fd=parent_fd,
        parent_path=parent,
        parent_device=opened.st_dev,
        parent_inode=opened.st_ino,
        output_basename=basename,
        ledger=ledger,
    )


def _revalidate_capability(capability: OutputCapability) -> None:
    if capability.closed:
        raise PaginatedMetadataRefusal("MARC1LM-F01", "capability is closed")
    try:
        opened = os.fstat(capability.parent_fd)
        named = os.lstat(capability.parent_path)
    except OSError as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F01", "capability cannot be revalidated"
        ) from exc
    identity = (capability.parent_device, capability.parent_inode)
    if (
        (opened.st_dev, opened.st_ino) != identity
        or (named.st_dev, named.st_ino) != identity
        or not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(named.st_mode)
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F01", "parent identity changed")
    _require_child_absent(capability.parent_fd, capability.output_basename)
    capability.ledger.increment("capability_revalidations")


def _create_output(capability: OutputCapability) -> None:
    _revalidate_capability(capability)
    try:
        os.mkdir(capability.output_basename, 0o700, dir_fd=capability.parent_fd)
        capability.output_created = True
        capability.ledger.increment("output_directories_created")
        output_fd = os.open(
            capability.output_basename,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=capability.parent_fd,
        )
        named = os.stat(
            capability.output_basename,
            dir_fd=capability.parent_fd,
            follow_symlinks=False,
        )
        opened = os.fstat(output_fd)
        if (
            (named.st_dev, named.st_ino) != (opened.st_dev, opened.st_ino)
            or not stat.S_ISDIR(opened.st_mode)
        ):
            os.close(output_fd)
            raise PaginatedMetadataRefusal("MARC1LM-F01", "output identity differs")
        capability.output_fd = output_fd
    except PaginatedMetadataRefusal:
        raise
    except OSError as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F01", "output creation failed"
        ) from exc


def _write_relative(
    capability: OutputCapability, filename: str, payload: bytes, *, mode: int
) -> None:
    if capability.output_fd is None or filename not in OUTPUT_NAMES:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "output is not allowlisted")
    if capability.ledger.values["output_bytes"] + len(payload) > MAX_COMBINED_OUTPUT_BYTES:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "combined output cap exceeded")
    try:
        descriptor = os.open(
            filename,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            mode,
            dir_fd=capability.output_fd,
        )
        try:
            os.fchmod(descriptor, mode)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise OSError("short write")
                offset += written
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F06", "exclusive relative write failed"
        ) from exc
    capability.ledger.increment("output_files_created")
    capability.ledger.increment("output_bytes", len(payload))


def _read_public(capability: OutputCapability) -> bytes:
    if capability.output_fd is None:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "output descriptor unavailable")
    try:
        descriptor = os.open(
            REPORT_NAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=capability.output_fd
        )
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_PUBLIC_OUTPUT_BYTES:
                raise PaginatedMetadataRefusal(
                    "MARC1LM-F06", "public report identity differs"
                )
            payload = os.read(descriptor, MAX_PUBLIC_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
    except PaginatedMetadataRefusal:
        raise
    except OSError as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F06", "public report inspection failed"
        ) from exc
    capability.ledger.increment("public_report_inspections")
    return payload


def _cleanup_generated_output(capability: OutputCapability) -> None:
    try:
        if capability.output_fd is not None:
            for filename in OUTPUT_NAMES:
                try:
                    os.unlink(filename, dir_fd=capability.output_fd)
                    capability.ledger.increment("cleanup_file_unlinks")
                except FileNotFoundError:
                    pass
            os.close(capability.output_fd)
            capability.output_fd = None
        if capability.output_created:
            os.rmdir(capability.output_basename, dir_fd=capability.parent_fd)
            capability.output_created = False
            capability.ledger.increment("cleanup_directory_removals")
    except OSError as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "generated cleanup failed") from exc


def _read_bound(path: Path, expected_sha256: str, ledger: AccessLedger) -> bytes:
    try:
        before = os.lstat(path)
        if not stat.S_ISREG(before.st_mode):
            raise PaginatedMetadataRefusal("MARC1LM-F00", "bound artifact differs")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise PaginatedMetadataRefusal(
                    "MARC1LM-F00", "bound artifact identity changed"
                )
            payload = b""
            while len(payload) <= 2 * 1024**2:
                chunk = os.read(descriptor, min(65536, 2 * 1024**2 + 1 - len(payload)))
                if not chunk:
                    break
                payload += chunk
        finally:
            os.close(descriptor)
    except PaginatedMetadataRefusal:
        raise
    except OSError as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F00", "bound artifact read failed") from exc
    ledger.increment("repository_reads")
    if len(payload) > 2 * 1024**2 or _sha256_bytes(payload) != expected_sha256:
        raise PaginatedMetadataRefusal("MARC1LM-F00", "bound artifact hash differs")
    return payload


def _strict_json(payload: bytes, route: str) -> Any:
    try:
        return json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PaginatedMetadataRefusal(route, "strict JSON differs") from exc


def load_green_decision(
    repo_root: str | Path | None = None, *, ledger: AccessLedger | None = None
) -> dict[str, Any]:
    """Load and validate the exact remotely green packet-bound decision."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    selected = ledger if ledger is not None else AccessLedger()
    decision = _strict_json(
        _read_bound(root / DECISION_RELATIVE_PATH, DECISION_SHA256, selected),
        "MARC1LM-F00",
    )
    request = _strict_json(
        _read_bound(root / REQUEST_RELATIVE_PATH, REQUEST_SHA256, selected),
        "MARC1LM-F00",
    )
    selected.increment("decision_loads")
    source = decision.get("registered_sequence", {}).get("Wrist_public_metadata", {})
    authorization = decision.get("authorization", {})
    if (
        not isinstance(decision, dict)
        or decision.get("schema_name")
        != "neurodecodekit.marc1_paginated_live_metadata_authorization_decision"
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "4d3eb19690676d48ce42ed16c5c00cc041d8bb4b"
        or decision.get("green_request", {}).get("both_required_jobs_green") is not True
        or decision.get("green_request", {}).get("CI_run_id") != 31_603_530_015
        or decision.get("user_authorization", {}).get("actual_message_SHA256")
        != "aedb564a57be18493fc20376676ef404794ca169d02985228aa8424cd7f7e6e8"
        or authorization.get("wrapper_implementation_after_decision_green") is not True
        or authorization.get("one_live_metadata_request_after_wrapper_green") is not True
        or authorization.get("participant_archive_or_payload_access_authorized_now")
        is not False
        or authorization.get(
            "derivative_model_training_inference_prediction_freeze_or_score_authorized_now"
        )
        is not False
        or source.get("full_URL") != REQUEST_URL
        or source.get("query") != REQUEST_QUERY
        or source.get("request_attempts") != 1
        or source.get("redirects") != 0
        or source.get("accepted_body_cap_bytes") != MAX_BODY_BYTES
        or source.get("expected_file_rows") != EXPECTED_ROWS
        or source.get("payload_requests") != 0
        or request.get("authorized_now") is not False
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F00", "authorization proof differs")
    for path, digest in (
        (PAGINATION_SOURCE_RELATIVE_PATH, PAGINATION_SOURCE_SHA256),
        (OUTPUT_SOURCE_RELATIVE_PATH, OUTPUT_SOURCE_SHA256),
    ):
        _read_bound(root / path, digest, selected)
    return decision


def _deferred_pagination(root: Path, ledger: AccessLedger) -> Any:
    _read_bound(root / PAGINATION_SOURCE_RELATIVE_PATH, PAGINATION_SOURCE_SHA256, ledger)
    module = importlib.import_module(
        "neurodecodekit.datasets.marc1_versioned_pagination"
    )
    ledger.increment("deferred_pagination_imports")
    return module


def inspect_source_surface(
    path: Path | None = None, *, ledger: AccessLedger | None = None
) -> dict[str, Any]:
    """Audit imports and CLI commands without invoking an executor."""

    source_path = path if path is not None else Path(__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    if ledger is not None:
        ledger.increment("repository_reads")
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = {
        "neurodecodekit.datasets.marc1_http_identity_live",
        "neurodecodekit.datasets.marc1_pilot_selection_live",
        "mne",
        "numpy",
        "scipy",
        "torch",
    }
    return {
        "forbidden_imports": sorted(imported & forbidden),
        "standard_library_only_at_module_scope": not bool(imported & forbidden),
        "payload_or_model_command": False,
        "commands": ["plan", "qualify", "inspect", "execute"],
    }


def _request() -> urllib.request.Request:
    return urllib.request.Request(
        REQUEST_URL,
        method="GET",
        headers={"Accept": "application/json", "Accept-Encoding": "identity"},
    )


def validate_request(request: urllib.request.Request) -> dict[str, Any]:
    headers = {key.casefold(): value for key, value in request.header_items()}
    if (
        request.full_url != REQUEST_URL
        or request.get_method() != "GET"
        or request.data not in (None, b"")
        or headers != {"accept": "application/json", "accept-encoding": "identity"}
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F02", "request identity differs")
    canonical = (
        f"GET {REQUEST_PATH}?{REQUEST_QUERY} HTTP/1.1\r\n"
        "Host: api.figshare.com\r\n"
        "Accept: application/json\r\n"
        "Accept-Encoding: identity\r\n\r\n"
    ).encode("ascii")
    return {
        "method": "GET",
        "query": REQUEST_QUERY,
        "canonical_request_bytes": len(canonical),
        "canonical_request_sha256": _domain_sha256(
            "neurodecodekit:MARC1-LM1:request:v0", canonical
        ),
    }


def _header_rows(response: BinaryIO) -> tuple[tuple[str, str], ...]:
    headers = getattr(response, "headers", ())
    if hasattr(headers, "raw_items"):
        rows = tuple((str(key), str(value)) for key, value in headers.raw_items())
    else:
        rows = tuple((str(key), str(value)) for key, value in headers)
    return rows


def _critical_headers(response: BinaryIO) -> dict[str, str]:
    result: dict[str, str] = {}
    allowed = {
        "content-encoding",
        "content-length",
        "content-type",
        "transfer-encoding",
    }
    for raw_key, raw_value in _header_rows(response):
        key = raw_key.strip().casefold()
        value = raw_value.strip()
        if "\r" in value or "\n" in value:
            raise PaginatedMetadataRefusal("MARC1LM-F03", "response header differs")
        if key not in allowed:
            continue
        if key in result:
            raise PaginatedMetadataRefusal(
                "MARC1LM-F03", "critical response header is duplicated"
            )
        result[key] = value
    return result


def _validate_headers(headers: Mapping[str, str]) -> dict[str, Any]:
    content_type = headers.get("content-type", "").split(";", 1)[0].strip().casefold()
    if content_type != "application/json":
        raise PaginatedMetadataRefusal("MARC1LM-F03", "content type differs")
    encoding = headers.get("content-encoding")
    if encoding is None:
        encoding_state = "absent"
    elif encoding and encoding.casefold() == "identity" and "," not in encoding:
        encoding_state = "identity"
    else:
        raise PaginatedMetadataRefusal("MARC1LM-F03", "content encoding differs")
    length = headers.get("content-length")
    transfer = headers.get("transfer-encoding")
    if length is not None and transfer is not None:
        raise PaginatedMetadataRefusal("MARC1LM-F03", "response framing conflicts")
    declared_length: int | None = None
    if length is not None:
        if (
            not length
            or any(character not in "0123456789" for character in length)
            or (len(length) > 1 and length.startswith("0"))
        ):
            raise PaginatedMetadataRefusal("MARC1LM-F03", "content length differs")
        declared_length = int(length)
        if declared_length > MAX_BODY_BYTES:
            raise PaginatedMetadataRefusal("MARC1LM-F03", "declared body exceeds cap")
        framing = "content-length"
    elif transfer is not None:
        if transfer.casefold() != "chunked" or "," in transfer or ";" in transfer:
            raise PaginatedMetadataRefusal("MARC1LM-F03", "transfer coding differs")
        framing = "chunked"
    else:
        framing = "connection-close"
    return {
        "content_encoding_state": encoding_state,
        "framing": framing,
        "declared_length": declared_length,
    }


def _response_status(response: BinaryIO) -> int:
    value = getattr(response, "status", None)
    if isinstance(value, bool) or not isinstance(value, int):
        try:
            value = int(response.getcode())  # type: ignore[attr-defined]
        except Exception as exc:
            raise PaginatedMetadataRefusal(
                "MARC1LM-F03", "response status unavailable"
            ) from exc
    return value


def _response_url(response: BinaryIO) -> str:
    try:
        value = response.geturl()  # type: ignore[attr-defined]
    except Exception as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F03", "response URL unavailable"
        ) from exc
    if not isinstance(value, str):
        raise PaginatedMetadataRefusal("MARC1LM-F03", "response URL differs")
    return value


def _read_response(response: BinaryIO, framing: Mapping[str, Any]) -> bytes:
    try:
        body = response.read(MAX_BODY_BYTES + 1)
    except Exception as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F03", "response read failed") from exc
    if not isinstance(body, bytes) or len(body) > MAX_BODY_BYTES:
        raise PaginatedMetadataRefusal("MARC1LM-F03", "response body exceeds cap")
    declared = framing["declared_length"]
    if declared is not None and declared != len(body):
        raise PaginatedMetadataRefusal("MARC1LM-F03", "content length mismatches body")
    return body


def _reject_target_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if TARGET_KEY_RE.search(normalized):
                raise PaginatedMetadataRefusal(
                    "MARC1LM-F04", "target-like field is forbidden"
                )
            _reject_target_fields(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_target_fields(nested)


def parse_inventory(
    body: bytes, pagination: Any, *, ledger: AccessLedger
) -> dict[str, Any]:
    value = _strict_json(body, "MARC1LM-F04")
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise PaginatedMetadataRefusal("MARC1LM-F04", "inventory root or row differs")
    _reject_target_fields(value)
    ledger.increment("metadata_parses")
    try:
        inventory = pagination.validate_wrist_rows(value)
    except Exception as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F04", "frozen inventory validation refused"
        ) from exc
    if (
        inventory.get("participant_archives") != EXPECTED_PARTICIPANTS
        or inventory.get("supplementary_rows") != EXPECTED_SUPPLEMENTARY
        or inventory.get("declared_bytes") != EXPECTED_DECLARED_BYTES
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F04", "inventory identity differs")
    inventory["bound_inventory_sha256"] = _domain_sha256(
        "neurodecodekit:MARC1-LM1:inventory:v0",
        _canonical_json_bytes(inventory["rows"]),
    )
    return inventory


def select_frozen_cohort(
    inventory: Mapping[str, Any], *, ledger: AccessLedger,
    subjects: Sequence[str] = FROZEN_SUBJECTS,
    fit_runs: Sequence[int] = FIT_RUNS,
    heldout_runs: Sequence[int] = HELDOUT_RUNS,
) -> dict[str, Any]:
    if tuple(subjects) != FROZEN_SUBJECTS:
        raise PaginatedMetadataRefusal("MARC1LM-F05", "cohort identity differs")
    if tuple(fit_runs) != FIT_RUNS or tuple(heldout_runs) != HELDOUT_RUNS:
        raise PaginatedMetadataRefusal("MARC1LM-F05", "split identity differs")
    if set(fit_runs) & set(heldout_runs):
        raise PaginatedMetadataRefusal("MARC1LM-F05", "split overlap differs")
    participants = inventory.get("participants")
    rows = inventory.get("rows")
    if not isinstance(participants, dict) or not isinstance(rows, list):
        raise PaginatedMetadataRefusal("MARC1LM-F05", "inventory selection surface differs")
    try:
        selected = [participants[subject] for subject in subjects]
    except KeyError as exc:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F05", "selected participant is unavailable"
        ) from exc
    canonical_rows = sorted((dict(row) for row in rows), key=lambda row: row["id"])
    selection_identity = {
        "subjects": list(subjects),
        "fit_runs": list(fit_runs),
        "heldout_runs": list(heldout_runs),
    }
    manifest = {
        "schema_name": "neurodecodekit.marc1_paginated_live_metadata_private",
        "schema_version": SCHEMA_VERSION,
        "source": {
            "provider": "Figshare",
            "record_id": 29_666_735,
            "version": 3,
            "DOI": "10.6084/m9.figshare.29666735.v3",
            "license": "CC BY 4.0",
            "request_query": REQUEST_QUERY,
            "inventory_identity_sha256": inventory["bound_inventory_sha256"],
        },
        "rows": canonical_rows,
        "selection": selection_identity,
    }
    ledger.increment("selections")
    return {
        "private_manifest": manifest,
        "private_bytes": _canonical_json_bytes(manifest),
        "selected_count": len(selected),
        "selected_declared_bytes": sum(int(row["size"]) for row in selected),
        "selection_sha256": _domain_sha256(
            "neurodecodekit:MARC1-LM1:selection:v0",
            _canonical_json_bytes(selection_identity),
        ),
        "fit_runs": list(fit_runs),
        "heldout_runs": list(heldout_runs),
        "fit_heldout_overlap": 0,
    }


def fetch_and_validate(
    *,
    opener: Any,
    pagination: Any,
    ledger: AccessLedger,
    real_network: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    request = _request()
    request_summary = validate_request(request)
    if real_network:
        ledger.increment("real_network_requests")
    else:
        ledger.increment("mock_HTTP_calls")
    try:
        response = opener.open(request, timeout=MAX_TIMEOUT_SECONDS)
    except urllib.error.HTTPError as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F03", "terminal status differs") from exc
    except PaginatedMetadataRefusal:
        raise
    except Exception as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F02", "network open failed") from exc
    with response:
        if _response_status(response) != 200:
            raise PaginatedMetadataRefusal("MARC1LM-F03", "terminal status differs")
        if _response_url(response) != REQUEST_URL:
            raise PaginatedMetadataRefusal("MARC1LM-F03", "terminal URL differs")
        framing = _validate_headers(_critical_headers(response))
        body = _read_response(response, framing)
    ledger.increment("response_body_reads")
    ledger.increment("response_body_bytes", len(body))
    inventory = parse_inventory(body, pagination, ledger=ledger)
    selection = select_frozen_cohort(inventory, ledger=ledger)
    transport = {
        **request_summary,
        **framing,
        "body_bytes": len(body),
        "body_sha256": _domain_sha256(
            "neurodecodekit:MARC1-LM1:response-body:v0", body
        ),
        "request_attempts": 1,
        "redirects": 0,
        "content_decoding_or_decompression_operations": 0,
    }
    return inventory, selection, transport


def _fixture_response(
    body: bytes,
    *,
    case: str = "content_length",
    status: int = 200,
    url: str = REQUEST_URL,
    extra_headers: Sequence[tuple[str, str]] = (),
) -> FixtureResponse:
    headers: list[tuple[str, str]] = [("Content-Type", "application/json")]
    if case == "content_length":
        headers.append(("Content-Length", str(len(body))))
    elif case == "identity_length":
        headers.extend(
            (("Content-Encoding", "IdEnTiTy"), ("Content-Length", str(len(body))))
        )
    elif case == "chunked":
        headers.append(("Transfer-Encoding", "chunked"))
    elif case != "close":
        raise ValueError("unknown fixture response case")
    headers.extend(extra_headers)
    return FixtureResponse(body=body, status=status, reported_url=url, headers=tuple(headers))


def _expect_refusal(
    name: str,
    operation: Callable[[], Any],
    *,
    routes: Sequence[str] = tuple(FAILURE_ROUTES),
) -> str:
    try:
        operation()
    except PaginatedMetadataRefusal as exc:
        if exc.route not in routes:
            raise AssertionError(f"{name} used unexpected route {exc.route}") from exc
        return exc.route
    raise AssertionError(f"{name} did not refuse")


def _mutated_body(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return _canonical_json_bytes([dict(row) for row in rows])


def run_required_mutations(
    pagination: Any,
    canonical_body: bytes,
    *,
    repo_root: Path,
    ledger: AccessLedger,
) -> dict[str, str]:
    """Exercise every frozen generated refusal without a real operation."""

    rows = pagination.build_generated_wrist_rows()
    routes: dict[str, str] = {}

    def parse_response(response: FixtureResponse) -> Any:
        return fetch_and_validate(
            opener=FixtureOpener(response),
            pagination=pagination,
            ledger=ledger,
            real_network=False,
        )

    routes["wrong_decision_hash"] = _expect_refusal(
        "wrong_decision_hash",
        lambda: _read_bound(repo_root / DECISION_RELATIVE_PATH, "0" * 64, ledger),
        routes=("MARC1LM-F00",),
    )
    bad_request = urllib.request.Request(
        REQUEST_URL.replace("page=1", "page=2"),
        method="GET",
        headers={"Accept": "application/json", "Accept-Encoding": "identity"},
    )
    routes["wrong_request_query"] = _expect_refusal(
        "wrong_request_query", lambda: validate_request(bad_request), routes=("MARC1LM-F02",)
    )
    body_request = urllib.request.Request(
        REQUEST_URL,
        data=b"x",
        method="GET",
        headers={"Accept": "application/json", "Accept-Encoding": "identity"},
    )
    routes["request_body_present"] = _expect_refusal(
        "request_body_present", lambda: validate_request(body_request), routes=("MARC1LM-F02",)
    )
    routes["redirect_status"] = _expect_refusal(
        "redirect_status",
        lambda: parse_response(_fixture_response(canonical_body, status=302)),
        routes=("MARC1LM-F03",),
    )
    routes["final_URL_drift"] = _expect_refusal(
        "final_URL_drift",
        lambda: parse_response(_fixture_response(canonical_body, url=REQUEST_URL + "&x=1")),
        routes=("MARC1LM-F03",),
    )
    routes["non_200_status"] = _expect_refusal(
        "non_200_status",
        lambda: parse_response(_fixture_response(canonical_body, status=204)),
        routes=("MARC1LM-F03",),
    )
    routes["non_JSON_content_type"] = _expect_refusal(
        "non_JSON_content_type",
        lambda: parse_response(
            FixtureResponse(canonical_body, headers=(("Content-Type", "text/plain"),))
        ),
        routes=("MARC1LM-F03",),
    )
    for name, header_rows in (
        ("gzip_content_encoding", (("Content-Encoding", "gzip"),)),
        (
            "duplicate_content_encoding",
            (("Content-Encoding", "identity"), ("Content-Encoding", "identity")),
        ),
        ("content_encoding_list", (("Content-Encoding", "identity, gzip"),)),
        (
            "content_length_and_chunked",
            (("Content-Length", str(len(canonical_body))), ("Transfer-Encoding", "chunked")),
        ),
        ("transfer_encoding_list", (("Transfer-Encoding", "gzip, chunked"),)),
        ("malformed_content_length", (("Content-Length", "01"),)),
        ("content_length_mismatch", (("Content-Length", str(len(canonical_body) + 1)),)),
    ):
        routes[name] = _expect_refusal(
            name,
            lambda values=header_rows: parse_response(
                FixtureResponse(
                    canonical_body,
                    headers=(("Content-Type", "application/json"), *values),
                )
            ),
            routes=("MARC1LM-F03",),
        )
    routes["body_overflow"] = _expect_refusal(
        "body_overflow",
        lambda: parse_response(_fixture_response(b"x" * (MAX_BODY_BYTES + 1), case="close")),
        routes=("MARC1LM-F03",),
    )
    for name, body in (
        ("malformed_JSON", b"["),
        ("duplicate_JSON_key", b'[{"id":1,"id":2}]'),
        ("non_array_root", b"{}"),
        ("non_object_row", b"[1]"),
    ):
        routes[name] = _expect_refusal(
            name,
            lambda value=body: parse_response(_fixture_response(value)),
            routes=("MARC1LM-F04",),
        )
    target_rows = [dict(row) for row in rows]
    target_rows[0]["target"] = "forbidden"
    routes["target_like_field"] = _expect_refusal(
        "target_like_field",
        lambda: parse_response(_fixture_response(_mutated_body(target_rows))),
        routes=("MARC1LM-F04",),
    )
    row_mutations: dict[str, list[dict[str, Any]]] = {}
    row_mutations["fifty_four_rows"] = [dict(row) for row in rows[:-1]]
    row_mutations["fifty_six_rows"] = [dict(row) for row in rows] + [dict(rows[-1])]
    drift = [dict(row) for row in rows]
    drift[0]["extra"] = 1
    row_mutations["row_field_drift"] = drift
    duplicate_id = [dict(row) for row in rows]
    duplicate_id[1]["id"] = duplicate_id[0]["id"]
    row_mutations["duplicate_file_id"] = duplicate_id
    duplicate_name = [dict(row) for row in rows]
    duplicate_name[1]["name"] = duplicate_name[0]["name"]
    row_mutations["duplicate_filename"] = duplicate_name
    URL_drift = [dict(row) for row in rows]
    URL_drift[0]["download_url"] += "?x=1"
    row_mutations["download_URL_drift"] = URL_drift
    MD5_drift = [dict(row) for row in rows]
    MD5_drift[0]["computed_md5"] = "0" * 32
    row_mutations["MD5_disagreement"] = MD5_drift
    anchor_drift = [dict(row) for row in rows]
    anchor_drift[0]["size"] += 1
    anchor_drift[-1]["size"] -= 1
    row_mutations["sub01_anchor_drift"] = anchor_drift
    total_drift = [dict(row) for row in rows]
    total_drift[-1]["size"] += 1
    row_mutations["declared_byte_total_drift"] = total_drift
    for name, mutated in row_mutations.items():
        routes[name] = _expect_refusal(
            name,
            lambda value=mutated: parse_response(_fixture_response(_mutated_body(value))),
            routes=("MARC1LM-F04",),
        )
    inventory = parse_inventory(canonical_body, pagination, ledger=ledger)
    routes["cohort_order_drift"] = _expect_refusal(
        "cohort_order_drift",
        lambda: select_frozen_cohort(
            inventory, ledger=ledger, subjects=tuple(reversed(FROZEN_SUBJECTS))
        ),
        routes=("MARC1LM-F05",),
    )
    routes["split_drift"] = _expect_refusal(
        "split_drift",
        lambda: select_frozen_cohort(
            inventory, ledger=ledger, fit_runs=(1, 2), heldout_runs=(3,)
        ),
        routes=("MARC1LM-F05",),
    )
    routes["public_private_leak"] = _expect_refusal(
        "public_private_leak",
        lambda: validate_public_report(
            {
                "schema_name": "x",
                "schema_version": SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "status": "x",
                "route": GENERATED_ROUTE,
                "proof_posture": "x",
                "source_summary": {"url": REQUEST_URL},
                "inventory_summary": {},
                "cohort_summary": {},
                "split_summary": {},
                "transport_summary": {},
                "hashes": {},
                "measurements": {},
                "access_counters": {},
                "mutation_summary": {},
                "acceptance_gates": [],
                "warnings": [],
                "unavailable_fields": [],
                "claim_boundary": {},
            }
        ),
        routes=("MARC1LM-F06",),
    )
    with tempfile.TemporaryDirectory(dir=_canonical_temp_parent()) as temporary:
        ledger = AccessLedger()
        capability = acquire_output_capability(Path(temporary) / "race", ledger=ledger)
        try:
            (Path(temporary) / "race").mkdir()
            routes["output_appears_after_capability"] = _expect_refusal(
                "output_appears_after_capability",
                lambda: _create_output(capability),
                routes=("MARC1LM-F01",),
            )
        finally:
            capability.close()
    routes["resource_cap_breach"] = _expect_refusal(
        "resource_cap_breach",
        lambda: _enforce_resources(MAX_RUNTIME_SECONDS + 1, 0, 0),
        routes=("MARC1LM-F06",),
    )
    routes["retry_nonzero"] = _expect_refusal(
        "retry_nonzero", lambda: _require_single_execution(1, retry_count=1),
        routes=("MARC1LM-F07",),
    )
    routes["second_execution_ordinal"] = _expect_refusal(
        "second_execution_ordinal", lambda: _require_single_execution(2, retry_count=0),
        routes=("MARC1LM-F07",),
    )
    if tuple(routes) != REQUIRED_MUTATIONS:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "mutation inventory differs")
    return routes


def _require_single_execution(ordinal: int, *, retry_count: int) -> None:
    if ordinal != 1 or retry_count != 0:
        raise PaginatedMetadataRefusal("MARC1LM-F07", "retry or rerun is forbidden")


def _walk_public(value: Any, *, key: str | None = None) -> None:
    normalized_key = key.casefold() if key is not None else None
    if normalized_key == "rows" and (
        isinstance(value, bool) or not isinstance(value, int)
    ):
        raise PaginatedMetadataRefusal(
            "MARC1LM-F06", "private public key leaked (rows)"
        )
    if normalized_key in {
        "url",
        "file_id",
        "filename",
        "subjects",
        "checksum",
        "md5",
        "path",
    }:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F06", f"private public key leaked ({normalized_key})"
        )
    if isinstance(value, dict):
        for nested_key, nested in value.items():
            _walk_public(nested, key=str(nested_key))
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested, key=key)
    elif isinstance(value, str) and PRIVATE_VALUE_RE.search(value):
        raise PaginatedMetadataRefusal("MARC1LM-F06", "private public value leaked")


def validate_public_report(report: Mapping[str, Any]) -> None:
    if not isinstance(report, dict) or set(report) != PUBLIC_FIELDS:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "public report fields differ")
    if report.get("lane_id") != LANE_ID or report.get("route") not in {
        GENERATED_ROUTE,
        SUCCESS_ROUTE,
        *FAILURE_ROUTES,
    }:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "public report identity differs")
    _walk_public(report)


def _anticipated_final_counters(
    ledger: AccessLedger,
    *,
    files_to_write: int,
    inspect_public: bool,
    generated_cleanup_files: int = 0,
    generated_cleanup_directory: bool = False,
    create_output_directory: bool = False,
) -> dict[str, int]:
    counters = dict(ledger.values)
    if create_output_directory:
        counters["capability_revalidations"] += 1
        counters["output_directories_created"] += 1
    counters["output_files_created"] += files_to_write
    if inspect_public:
        counters["public_report_inspections"] += 1
    counters["cleanup_file_unlinks"] += generated_cleanup_files
    if generated_cleanup_directory:
        counters["cleanup_directory_removals"] += 1
    return counters


def _stable_report_bytes(report: dict[str, Any], private_bytes: bytes, marker: bytes) -> bytes:
    for _ in range(12):
        payload = _canonical_json_bytes(report)
        combined = len(payload) + len(private_bytes) + len(marker)
        if (
            report["measurements"].get("public_output_bytes") == len(payload)
            and report["measurements"].get("combined_output_bytes") == combined
            and report["measurements"].get("incremental_disk_bytes") == combined
            and report["access_counters"].get("output_bytes") == combined
        ):
            if len(payload) > MAX_PUBLIC_OUTPUT_BYTES or combined > min(
                MAX_COMBINED_OUTPUT_BYTES, MAX_INCREMENTAL_DISK_BYTES
            ):
                raise PaginatedMetadataRefusal("MARC1LM-F06", "output cap exceeded")
            return payload
        report["measurements"]["public_output_bytes"] = len(payload)
        report["measurements"]["combined_output_bytes"] = combined
        report["measurements"]["incremental_disk_bytes"] = combined
        report["access_counters"]["output_bytes"] = combined
    raise PaginatedMetadataRefusal("MARC1LM-F06", "public output size did not stabilize")


def _base_report(
    *,
    route: str,
    proof_posture: str,
    inventory: Mapping[str, Any],
    selection: Mapping[str, Any],
    transport: Mapping[str, Any],
    ledger: AccessLedger,
    mutations: Mapping[str, str],
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    private_sha256: str,
    marker_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.marc1_paginated_live_metadata_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_qualified" if route == GENERATED_ROUTE else "real_metadata_validated",
        "route": route,
        "proof_posture": proof_posture,
        "source_summary": {
            "provider": "Figshare",
            "record_id": 29_666_735,
            "version": 3,
            "query": REQUEST_QUERY,
            "metadata_only": True,
        },
        "inventory_summary": {
            "rows": EXPECTED_ROWS,
            "participant_archives": inventory["participant_archives"],
            "supplementary_rows": inventory["supplementary_rows"],
            "declared_bytes": inventory["declared_bytes"],
        },
        "cohort_summary": {
            "selected_subjects": selection["selected_count"],
            "selection_target_quality_checksum_outcome_free": True,
            "selected_declared_bytes": selection["selected_declared_bytes"],
        },
        "split_summary": {
            "fit_run_count": len(selection["fit_runs"]),
            "heldout_run_count": len(selection["heldout_runs"]),
            "fit_heldout_overlap": selection["fit_heldout_overlap"],
        },
        "transport_summary": {
            "request_attempts": transport["request_attempts"],
            "redirects": transport["redirects"],
            "framing": transport["framing"],
            "content_encoding_state": transport["content_encoding_state"],
            "body_bytes": transport["body_bytes"],
            "content_decoding_or_decompression_operations": 0,
        },
        "hashes": {
            "inventory_identity_sha256": inventory["bound_inventory_sha256"],
            "selection_identity_sha256": selection["selection_sha256"],
            "response_body_identity_sha256": transport["body_sha256"],
            "private_manifest_sha256": private_sha256,
            "consumed_marker_sha256": marker_sha256,
        },
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "generated_input_bytes": generated_input_bytes,
            "network_body_bytes": transport["body_bytes"] if route == SUCCESS_ROUTE else 0,
            "public_output_bytes": 0,
            "private_output_bytes": len(selection["private_bytes"]),
            "combined_output_bytes": 0,
            "incremental_disk_bytes": 0,
            "end_to_end_latency_measured": False,
        },
        "access_counters": dict(ledger.values),
        "mutation_summary": {
            "required": len(REQUIRED_MUTATIONS),
            "passed": len(mutations),
            "routes": dict(mutations),
        },
        "acceptance_gates": list(ACCEPTANCE_GATES),
        "warnings": [
            "Generated qualification has no source or scientific value."
            if route == GENERATED_ROUTE
            else "Metadata validation alone is not neural or language evidence.",
            "Participant payloads signals targets models and scores remain unavailable.",
        ],
        "unavailable_fields": [
            "signal_samples",
            "channels",
            "events",
            "targets",
            "model_predictions",
            "decoding_metrics",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "same_thought_to_text_path": True,
            "is_pivot": False,
            "engineering_capability": "complete target-free Wrist inventory bound without payload access",
            "scientific_claim_established": False,
            "language_or_thought_to_text_established": False,
        },
    }


def _failure_report(
    refusal: PaginatedMetadataRefusal,
    *,
    stage: str,
    ledger: AccessLedger,
    machine: Mapping[str, Any],
    runtime_seconds: float,
    peak_rss_bytes: int,
    marker: bytes,
) -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.marc1_paginated_live_metadata_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_failed_real_metadata",
        "route": refusal.route,
        "proof_posture": "aggregate_failure_after_consumed_marker_no_retry_or_rerun",
        "source_summary": {
            "provider": "Figshare",
            "record_id": 29_666_735,
            "version": 3,
            "query": REQUEST_QUERY,
            "metadata_only": True,
        },
        "inventory_summary": {
            "available": False,
            "expected_rows": EXPECTED_ROWS,
            "expected_participant_archives": EXPECTED_PARTICIPANTS,
            "expected_supplementary_rows": EXPECTED_SUPPLEMENTARY,
        },
        "cohort_summary": {"available": False, "selected_subjects": 0},
        "split_summary": {"available": False, "fit_heldout_overlap": None},
        "transport_summary": {
            "request_attempts": ledger.values["real_network_requests"],
            "redirects": 0,
            "accepted_body_reads": ledger.values["response_body_reads"],
            "accepted_body_bytes": ledger.values["response_body_bytes"],
            "content_decoding_or_decompression_operations": 0,
        },
        "hashes": {
            "inventory_identity_sha256": None,
            "selection_identity_sha256": None,
            "response_body_identity_sha256": None,
            "private_manifest_sha256": None,
            "consumed_marker_sha256": _domain_sha256(
                "neurodecodekit:MARC1-LM1:consumed-marker:v0", marker
            ),
        },
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "generated_input_bytes": 0,
            "network_body_bytes": ledger.values["response_body_bytes"],
            "public_output_bytes": 0,
            "private_output_bytes": 0,
            "combined_output_bytes": 0,
            "incremental_disk_bytes": 0,
            "end_to_end_latency_measured": False,
            "machine_gate": dict(machine),
        },
        "access_counters": _anticipated_final_counters(
            ledger,
            files_to_write=1,
            inspect_public=True,
        ),
        "mutation_summary": {
            "required": len(REQUIRED_MUTATIONS),
            "passed": 0,
            "routes": {},
        },
        "acceptance_gates": {
            "required": list(ACCEPTANCE_GATES),
            "completed": False,
            "failed_stage": stage,
            "no_retry_or_rerun_available": True,
        },
        "warnings": [
            "The one registered metadata invocation is consumed and cannot be retried or rerun.",
            "The aggregate route reports a failure class without publishing raw headers rows or bodies.",
            "No participant archive signal target model prediction or score was accessed.",
        ],
        "unavailable_fields": [
            "validated_inventory",
            "frozen_cohort",
            "signal_samples",
            "channels",
            "events",
            "targets",
            "model_predictions",
            "decoding_metrics",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "same_thought_to_text_path": True,
            "is_pivot": False,
            "engineering_capability": "aggregate failure localization after one consumed metadata attempt",
            "scientific_claim_established": False,
            "language_or_thought_to_text_established": False,
        },
    }


def _marker_bytes(*, generated: bool, implementation_commit: str | None = None) -> bytes:
    return _canonical_json_bytes(
        {
            "schema_name": "neurodecodekit.marc1_paginated_live_metadata_consumed",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "execution_ordinal": 1,
            "generated": generated,
            "implementation_commit": implementation_commit,
            "retry_or_rerun_available": False,
        }
    )


def _enforce_resources(runtime_seconds: float, peak_rss_bytes: int, output_bytes: int) -> None:
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or output_bytes > MAX_COMBINED_OUTPUT_BYTES
        or output_bytes > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F06", "resource cap exceeded")


def preconsumption_machine_gate(
    parent: str | Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise PaginatedMetadataRefusal("MARC1LM-F01", "thread environment differs")
    try:
        free_bytes = int(disk_usage_reader(Path(parent)).free)
        logical_cpus = cpu_count_reader()
        loads = loadavg_reader()
        peak_rss = int(rss_reader())
    except Exception as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F01", "machine metric unavailable") from exc
    if logical_cpus is None or logical_cpus <= 0 or not loads:
        raise PaginatedMetadataRefusal("MARC1LM-F01", "CPU or load unavailable")
    one_minute = float(loads[0])
    normalized = one_minute / logical_cpus
    if (
        free_bytes < MINIMUM_FREE_DISK_BYTES
        or not math.isfinite(one_minute)
        or one_minute < 0
        or normalized > MAX_LOAD_PER_LOGICAL_CPU
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F01", "machine resource gate failed")
    return {
        "free_disk_bytes": free_bytes,
        "logical_CPUs": logical_cpus,
        "one_minute_load": one_minute,
        "one_minute_load_per_logical_CPU": normalized,
        "peak_RSS_bytes": peak_rss,
        "threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
    }


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args), cwd=root, check=False, capture_output=True, text=True
    )


def load_implementation_record(
    repo_root: str | Path, *, expected_sha256: str, ledger: AccessLedger
) -> dict[str, Any]:
    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise PaginatedMetadataRefusal("MARC1LM-F00", "implementation hash malformed")
    root = Path(repo_root)
    record = _strict_json(
        _read_bound(root / IMPLEMENTATION_RELATIVE_PATH, expected_sha256, ledger),
        "MARC1LM-F00",
    )
    if (
        not isinstance(record, dict)
        or record.get("schema_name")
        != "neurodecodekit.marc1_paginated_live_metadata_implementation"
        or record.get("lane_id") != LANE_ID
        or record.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or record.get("generated_qualification", {}).get("route") != GENERATED_ROUTE
        or record.get("generated_qualification", {}).get("all_gates_passed") is not True
        or record.get("execution_state", {}).get("real_execution_consumed") is not False
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F00", "implementation record differs")
    for binding in record.get("tracked_file_hashes", ()):
        path = str(binding.get("path", ""))
        digest = str(binding.get("sha256", ""))
        if (
            not path
            or path.startswith(("/", "~"))
            or ".." in Path(path).parts
            or HEX64_RE.fullmatch(digest) is None
        ):
            raise PaginatedMetadataRefusal("MARC1LM-F00", "implementation binding differs")
        _read_bound(root / path, digest, ledger)
    return record


def verify_green_implementation(
    repo_root: str | Path,
    evidence: GreenImplementationEvidence,
    *,
    ledger: AccessLedger,
) -> dict[str, Any]:
    root = Path(repo_root)
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or HEX64_RE.fullmatch(evidence.implementation_registry_sha256) is None
        or min(
            evidence.CI_run_id,
            evidence.base_python_job_id,
            evidence.optional_neuro_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F00", "green evidence malformed")
    head = _git(root, "rev-parse", "HEAD")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    ancestor = _git(root, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, "HEAD")
    if (
        head.returncode
        or head.stdout.strip() != evidence.implementation_commit
        or clean.returncode
        or clean.stdout.strip()
        or ancestor.returncode
    ):
        raise PaginatedMetadataRefusal("MARC1LM-F00", "green implementation proof differs")
    load_green_decision(root, ledger=ledger)
    return load_implementation_record(
        root, expected_sha256=evidence.implementation_registry_sha256, ledger=ledger
    )


def qualify_generated(
    output_dir: str | os.PathLike[str],
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run the complete generated/mock qualification after capability acquisition."""

    if os.fspath(output_dir) == REGISTERED_OUTPUT_PATH:
        raise PaginatedMetadataRefusal(
            "MARC1LM-F01", "generated qualification cannot use registered output"
        )
    ledger = AccessLedger()
    capability = acquire_output_capability(output_dir, ledger=ledger)
    started = clock()
    root = Path(repo_root) if repo_root is not None else _repo_root()
    try:
        load_green_decision(root, ledger=ledger)
        pagination = _deferred_pagination(root, ledger)
        source_surface = inspect_source_surface(ledger=ledger)
        if source_surface["forbidden_imports"]:
            raise PaginatedMetadataRefusal("MARC1LM-F00", "forbidden import surface")
        rows = pagination.build_generated_wrist_rows()
        ledger.increment("generated_fixtures")
        body = _canonical_json_bytes(rows)
        accepted: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
        for case in ("close", "content_length", "identity_length", "chunked"):
            accepted.append(
                fetch_and_validate(
                    opener=FixtureOpener(_fixture_response(body, case=case)),
                    pagination=pagination,
                    ledger=ledger,
                    real_network=False,
                )
            )
        semantic_hashes = {item[0]["bound_inventory_sha256"] for item in accepted}
        selection_hashes = {item[1]["selection_sha256"] for item in accepted}
        if len(semantic_hashes) != 1 or len(selection_hashes) != 1:
            raise PaginatedMetadataRefusal("MARC1LM-F06", "accepted replay differs")
        mutations = run_required_mutations(
            pagination,
            body,
            repo_root=root,
            ledger=ledger,
        )
        inventory, selection, transport = accepted[0]
        replay = select_frozen_cohort(inventory, ledger=ledger)
        if replay["private_bytes"] != selection["private_bytes"]:
            raise PaginatedMetadataRefusal("MARC1LM-F06", "private replay differs")
        marker = _marker_bytes(generated=True)
        private_bytes = selection["private_bytes"]
        marker_sha = _domain_sha256(
            "neurodecodekit:MARC1-LM1:consumed-marker:v0", marker
        )
        private_sha = _domain_sha256(
            "neurodecodekit:MARC1-LM1:private-manifest:v0", private_bytes
        )
        generated_input = ledger.values["response_body_bytes"]
        runtime = clock() - started
        peak_rss = int(rss_reader())
        report = _base_report(
            route=GENERATED_ROUTE,
            proof_posture="generated_mock_only_no_source_or_scientific_value",
            inventory=inventory,
            selection=selection,
            transport=transport,
            ledger=ledger,
            mutations=mutations,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            generated_input_bytes=generated_input,
            private_sha256=private_sha,
            marker_sha256=marker_sha,
        )
        report["access_counters"] = _anticipated_final_counters(
            ledger,
            files_to_write=3,
            inspect_public=True,
            generated_cleanup_files=3,
            generated_cleanup_directory=True,
            create_output_directory=True,
        )
        report_bytes = _stable_report_bytes(report, private_bytes, marker)
        validate_public_report(report)
        _enforce_resources(runtime, peak_rss, len(report_bytes) + len(private_bytes) + len(marker))
        _create_output(capability)
        _write_relative(capability, MARKER_NAME, marker, mode=0o600)
        _write_relative(capability, PRIVATE_NAME, private_bytes, mode=0o600)
        _write_relative(capability, REPORT_NAME, report_bytes, mode=0o644)
        observed_public = _read_public(capability)
        if observed_public != report_bytes:
            raise PaginatedMetadataRefusal("MARC1LM-F06", "public output replay differs")
        validate_public_report(_strict_json(observed_public, "MARC1LM-F06"))
        _cleanup_generated_output(capability)
        if ledger.values != report["access_counters"]:
            raise PaginatedMetadataRefusal("MARC1LM-F06", "final access counters differ")
        output_removed = True
        public_sha = _domain_sha256(
            "neurodecodekit:MARC1-LM1:public-report:v0", report_bytes
        )
        return QualificationOutcome(
            report=report,
            report_bytes=report_bytes,
            private_sha256=private_sha,
            public_sha256=public_sha,
            output_path=os.fspath(output_dir),
            output_removed=output_removed,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            generated_input_bytes=generated_input,
            generated_output_bytes=len(report_bytes) + len(private_bytes) + len(marker),
        )
    finally:
        if capability.output_created:
            _cleanup_generated_output(capability)
        capability.close()


def _real_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())


def _write_consumed_failure_report(
    capability: OutputCapability,
    refusal: PaginatedMetadataRefusal,
    *,
    stage: str,
    ledger: AccessLedger,
    machine: Mapping[str, Any],
    started: float,
    marker: bytes,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    runtime = clock() - started
    peak_rss = int(rss_reader())
    report = _failure_report(
        refusal,
        stage=stage,
        ledger=ledger,
        machine=machine,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        marker=marker,
    )
    report_bytes = _stable_report_bytes(report, b"", marker)
    validate_public_report(report)
    _enforce_resources(runtime, peak_rss, len(report_bytes) + len(marker))
    _write_relative(capability, REPORT_NAME, report_bytes, mode=0o644)
    observed = _read_public(capability)
    if observed != report_bytes:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "failure report replay differs")
    validate_public_report(_strict_json(observed, "MARC1LM-F06"))
    if ledger.values != report["access_counters"]:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "failure counters differ")
    return report


def execute_registered(
    *,
    repo_root: str | Path,
    output_dir: str | os.PathLike[str],
    evidence: GreenImplementationEvidence,
    environ: Mapping[str, str] | None = None,
    opener: Any | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Consume the one registered metadata response after every green gate."""

    ledger = AccessLedger()
    capability = acquire_output_capability(output_dir, ledger=ledger)
    started = clock()
    root = Path(repo_root)
    machine: Mapping[str, Any] = {}
    marker: bytes | None = None
    report_written = False
    stage = "preconsumption_proof"
    try:
        if os.fspath(output_dir) != REGISTERED_OUTPUT_PATH:
            raise PaginatedMetadataRefusal("MARC1LM-F01", "registered output path differs")
        _require_single_execution(
            evidence.registered_execution_ordinal, retry_count=ledger.values["retries"]
        )
        verify_green_implementation(root, evidence, ledger=ledger)
        stage = "machine_gate"
        machine = preconsumption_machine_gate(
            capability.parent_path,
            environ=os.environ if environ is None else environ,
            rss_reader=rss_reader,
        )
        stage = "bound_pagination_import"
        pagination = _deferred_pagination(root, ledger)
        stage = "consumed_marker"
        _create_output(capability)
        marker = _marker_bytes(
            generated=False, implementation_commit=evidence.implementation_commit
        )
        _write_relative(capability, MARKER_NAME, marker, mode=0o600)
        stage = "public_metadata_transport"
        selected_opener = _real_opener() if opener is None else opener
        inventory, selection, transport = fetch_and_validate(
            opener=selected_opener,
            pagination=pagination,
            ledger=ledger,
            real_network=opener is None,
        )
        stage = "private_manifest_and_aggregate_report"
        private_bytes = selection["private_bytes"]
        runtime = clock() - started
        peak_rss = int(rss_reader())
        report = _base_report(
            route=SUCCESS_ROUTE,
            proof_posture="one_registered_public_metadata_response_no_payload",
            inventory=inventory,
            selection=selection,
            transport=transport,
            ledger=ledger,
            mutations={},
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            generated_input_bytes=0,
            private_sha256=_domain_sha256(
                "neurodecodekit:MARC1-LM1:private-manifest:v0", private_bytes
            ),
            marker_sha256=_domain_sha256(
                "neurodecodekit:MARC1-LM1:consumed-marker:v0", marker
            ),
        )
        report["measurements"]["machine_gate"] = machine
        report["access_counters"] = _anticipated_final_counters(
            ledger,
            files_to_write=2,
            inspect_public=True,
        )
        report_bytes = _stable_report_bytes(report, private_bytes, marker)
        validate_public_report(report)
        _enforce_resources(runtime, peak_rss, len(report_bytes) + len(private_bytes) + len(marker))
        _write_relative(capability, PRIVATE_NAME, private_bytes, mode=0o600)
        _write_relative(capability, REPORT_NAME, report_bytes, mode=0o644)
        report_written = True
        observed = _read_public(capability)
        if observed != report_bytes:
            raise PaginatedMetadataRefusal("MARC1LM-F06", "public output replay differs")
        validate_public_report(_strict_json(observed, "MARC1LM-F06"))
        if ledger.values != report["access_counters"]:
            raise PaginatedMetadataRefusal("MARC1LM-F06", "final access counters differ")
        return report
    except PaginatedMetadataRefusal as refusal:
        if marker is not None and not report_written:
            _write_consumed_failure_report(
                capability,
                refusal,
                stage=stage,
                ledger=ledger,
                machine=machine,
                started=started,
                marker=marker,
                clock=clock,
                rss_reader=rss_reader,
            )
        raise
    except Exception as exc:
        refusal = PaginatedMetadataRefusal(
            "MARC1LM-F06", "unexpected post-proof implementation failure"
        )
        if marker is not None and not report_written:
            _write_consumed_failure_report(
                capability,
                refusal,
                stage=stage,
                ledger=ledger,
                machine=machine,
                started=started,
                marker=marker,
                clock=clock,
                rss_reader=rss_reader,
            )
        raise refusal from exc
    finally:
        capability.close()


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    """Inspect one aggregate report with no sibling access."""

    selected = Path(path)
    if selected.name != REPORT_NAME:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "only aggregate report inspection is allowed")
    try:
        before = os.lstat(selected)
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
            raise PaginatedMetadataRefusal("MARC1LM-F06", "public result differs")
        if before.st_size > MAX_PUBLIC_OUTPUT_BYTES:
            raise PaginatedMetadataRefusal("MARC1LM-F06", "public result exceeds cap")
        descriptor = os.open(selected, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise PaginatedMetadataRefusal("MARC1LM-F06", "public result identity changed")
            payload = os.read(descriptor, MAX_PUBLIC_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
    except PaginatedMetadataRefusal:
        raise
    except OSError as exc:
        raise PaginatedMetadataRefusal("MARC1LM-F06", "public result read failed") from exc
    value = _strict_json(payload, "MARC1LM-F06")
    validate_public_report(value)
    return value


def registered_plan() -> dict[str, Any]:
    return {
        "lane_id": LANE_ID,
        "decision_commit": GREEN_DECISION_COMMIT,
        "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
        "registered_output_path": REGISTERED_OUTPUT_PATH,
        "request_query": REQUEST_QUERY,
        "request_attempts": 1,
        "redirects": 0,
        "body_cap_bytes": MAX_BODY_BYTES,
        "payload_requests": 0,
        "scientific_claim_established": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="print the frozen zero-access plan")
    qualify = subparsers.add_parser("qualify", help="run generated/mock qualification")
    qualify.add_argument("--output", required=True)
    qualify.add_argument("--repo-root", default=str(_repo_root()))
    inspect = subparsers.add_parser("inspect", help="inspect one aggregate report")
    inspect.add_argument("path")
    execute = subparsers.add_parser("execute", help="run the one proof-gated metadata request")
    execute.add_argument("--repo-root", default=str(_repo_root()))
    execute.add_argument("--output", required=True)
    execute.add_argument("--implementation-commit", required=True)
    execute.add_argument("--implementation-registry-sha256", required=True)
    execute.add_argument("--ci-run-id", required=True, type=int)
    execute.add_argument("--base-job-id", required=True, type=int)
    execute.add_argument("--optional-job-id", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            value = registered_plan()
        elif args.command == "qualify":
            outcome = qualify_generated(args.output, repo_root=args.repo_root)
            value = {
                **dict(outcome.report),
                "output_removed": outcome.output_removed,
                "public_report_sha256": outcome.public_sha256,
                "private_manifest_sha256": outcome.private_sha256,
            }
        elif args.command == "inspect":
            value = inspect_public_result(args.path)
        else:
            evidence = GreenImplementationEvidence(
                implementation_commit=args.implementation_commit,
                implementation_registry_sha256=args.implementation_registry_sha256,
                CI_run_id=args.ci_run_id,
                base_python_job_id=args.base_job_id,
                optional_neuro_job_id=args.optional_job_id,
            )
            value = execute_registered(
                repo_root=args.repo_root,
                output_dir=args.output,
                evidence=evidence,
            )
        print(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True))
        return 0
    except PaginatedMetadataRefusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "reason": exc.safe_reason},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
