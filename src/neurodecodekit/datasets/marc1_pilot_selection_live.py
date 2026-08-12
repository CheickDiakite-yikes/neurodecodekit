"""Proof-gated real-metadata wrapper for the MARC1-P1 pilot selector."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import ipaddress
import json
import math
import os
import re
import resource
import shutil
import socket
import stat
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping, Sequence
from urllib.parse import urljoin, urlsplit

from neurodecodekit.datasets import marc1_pilot_selection as selector


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC1-P1A"
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.marc1_privacy_preserving_pilot_selection_live_implementation"
)
RESULT_SCHEMA_NAME = "neurodecodekit.marc1_pilot_selection_live_result"
PRIVATE_SCHEMA_NAME = "neurodecodekit.marc1_pilot_selection_private_manifest"
GENERATED_ROUTE = "MARC1PSL-G1"
SUCCESS_ROUTE = "MARC1PS-R1"
FAILURE_ROUTES = tuple(f"MARC1PS-F{index:02d}" for index in range(7))

DECISION_RELATIVE_PATH = Path(
    "registries/marc1_privacy_preserving_pilot_selection_authorization_decision.v0.json"
)
DECISION_SHA256 = "fb97887d332749bc50e1dcdc69418b7f63b631a166032e6823565442c5c3fb39"
GREEN_DECISION_COMMIT = "9726d07ab08e9c2815dbe68398659f454693be5e"
GREEN_DECISION_CI_RUN_ID = 31_574_870_204
GREEN_DECISION_BASE_JOB_ID = 94_044_627_592
GREEN_DECISION_OPTIONAL_JOB_ID = 94_044_627_647
REQUEST_RELATIVE_PATH = Path(
    "registries/marc1_privacy_preserving_pilot_selection_authorization_request.v0.json"
)
REQUEST_SHA256 = "8eebf5f34294bc266e81552d31ff376cb81240d2ee18b2fc6857600fbd3aba85"
GENERATED_IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc1_privacy_preserving_pilot_selection_implementation.v0.json"
)
GENERATED_IMPLEMENTATION_SHA256 = (
    "09f3c559ba83b2eec47a36b8772a8904c4b2783e1e443f8999bf2c2371e6a4d1"
)
GENERATED_RESULT_RELATIVE_PATH = Path(
    "registries/marc1_privacy_preserving_pilot_selection_result.v0.json"
)
GENERATED_RESULT_SHA256 = "e795bed7effbf7f69f80804a1ac770c1d18bafe597d55f1627984c9dae878add"
FREEWILL_RESULT_RELATIVE_PATH = Path(
    "registries/marc1_freewill_central_directory_live_result.v0.json"
)
FREEWILL_RESULT_SHA256 = "fee969818b4e3e2ef7aee86096ad676c9bd70f80d19f2fd6dbe0e8069175257b"
GENERATED_SELECTOR_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc1_pilot_selection.py"
)
GENERATED_SELECTOR_SHA256 = (
    "072b9877bff0496ed10b10e4dbccc6751f357ec072390ce406342cc038359374"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc1_privacy_preserving_pilot_selection_live_implementation.v0.json"
)

FREEWILL_PRIVATE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
FREEWILL_PRIVATE_BYTES = 418_755
FREEWILL_PRIVATE_SHA256 = (
    "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
)
FREEWILL_INVENTORY_SHA256 = (
    "da0270a2d8f86106fe25e2246c1b969be448084b1a40c492c885580992c48d69"
)
FREEWILL_ARCHIVE_BYTES = 13_591_548_048
FREEWILL_ARCHIVE_MD5 = "3b7c3039c5c9fb6abf1429a830301711"
FREEWILL_FILE_ID = 57_518_986

WRIST_METADATA_URL = "https://api.figshare.com/v2/articles/29666735/versions/3/files"
WRIST_RECORD_ID = 29_666_735
WRIST_VERSION = 3
WRIST_DOI = "10.6084/m9.figshare.29666735.v3"
WRIST_EXPECTED_ROWS = 55
WRIST_EXPECTED_PARTICIPANTS = 45
WRIST_EXPECTED_SUPPLEMENTARY = 10
WRIST_EXPECTED_BYTES = 3_683_416_050
WRIST_SUB01_FILE_ID = 62_570_743
WRIST_SUB01_BYTES = 33_690_749
WRIST_SUB01_MD5 = "6b01cf5bd30de0c670d2837d112a17fa"
WRIST_RAW_FIELDS = frozenset(
    {
        "id",
        "name",
        "size",
        "is_link_only",
        "download_url",
        "supplied_md5",
        "computed_md5",
    }
)
WRIST_PARTICIPANT_RE = re.compile(r"(?P<subject>sub-(?:0[1-9]|[1-3][0-9]|4[0-5]))\.zip\Z")
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
MD5_RE = re.compile(r"[0-9a-f]{32}\Z")

PRIVATE_ROOT_RELATIVE_PATH = Path(".codex_work/marc1_pilot_selection/live_selection_v0")
PRIVATE_PARENT_RELATIVE_PATH = PRIVATE_ROOT_RELATIVE_PATH.parent
CONSUMED_MARKER_NAME = "execution_consumed.v0.json"
PRIVATE_SELECTION_NAME = "marc1_pilot_selection.private.v0.json"
PUBLIC_RESULT_RELATIVE_PATH = Path(
    "registries/marc1_privacy_preserving_pilot_selection_live_result.v0.json"
)

MINIMUM_FREE_DISK_BYTES = 12 * 1024**3
MAX_LOAD_PER_LOGICAL_CPU = 1.0
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_NETWORK_BODY_BYTES = 2 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2
MAX_HTTP_ATTEMPTS = 3
MAX_REDIRECTS = 2
MAX_TIMEOUT_SECONDS = 20.0
THREAD_ENV_KEYS = selector.THREAD_ENV_KEYS
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
TARGET_LEAK_KEYS = frozenset(
    {
        "answer",
        "class",
        "condition",
        "event",
        "label",
        "movement_direction",
        "outcome",
        "response",
        "sentence",
        "target",
        "trial",
    }
)
PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "proof_posture",
        "route",
        "green_evidence",
        "source_summary",
        "cohort_summary",
        "split_summary",
        "byte_summary",
        "selection_hashes",
        "transport_summary",
        "measurements",
        "mutation_summary",
        "access_counters",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "CRC32",
        "CRC32_if_available",
        "download_url",
        "entries",
        "file_id",
        "file_id_if_available",
        "local_header_offset",
        "local_header_offset_if_available",
        "member_name",
        "member_or_archive_name",
        "path",
        "raw_body",
        "raw_headers",
        "response_body",
        "url",
    }
)
REQUIRED_MUTATIONS = (
    "private_hash_mismatch",
    "private_mode_mismatch",
    "private_symlink",
    "freewill_source_identity",
    "freewill_row_count",
    "freewill_unknown_row_field",
    "freewill_duplicate_member",
    "freewill_unsafe_path",
    "freewill_incomplete_bundle",
    "wrist_root_shape",
    "wrist_target_leak_field",
    "wrist_row_count",
    "wrist_duplicate_file_id",
    "wrist_duplicate_name",
    "wrist_participant_name",
    "wrist_download_URL",
    "wrist_MD5_mismatch",
    "wrist_sub01_anchor",
    "wrist_record_byte_total",
    "wrist_selected_byte_cap",
    "transport_overflow",
    "transport_duplicate_header",
    "transport_transfer_encoding",
    "transport_private_redirect",
    "public_private_field_leak",
    "forbidden_target_operation",
)


class LivePilotRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-P1A route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC1-P1A refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class GreenWrapperEvidence:
    """Operator-supplied proof for the exact remotely green wrapper."""

    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    implementation_registry_sha256: str
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class HTTPFixtureExchange:
    url: str
    response: "FixtureHTTPResponse"


@dataclass(frozen=True)
class PilotOutcome:
    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path | None
    runtime_seconds: float
    peak_rss_bytes: int
    combined_output_bytes: int


class FixtureHTTPResponse(io.BytesIO):
    """Minimal urllib-shaped response for generated and mocked qualification."""

    def __init__(
        self,
        body: bytes,
        *,
        status: int,
        url: str,
        headers: Mapping[str, str],
        duplicate_headers: Sequence[tuple[str, str]] = (),
        nonbytes_body: bool = False,
    ) -> None:
        super().__init__(body)
        self.status = status
        self.code = status
        self._url = url
        self.headers = Message()
        for key, value in headers.items():
            self.headers.add_header(key, value)
        for key, value in duplicate_headers:
            self.headers.add_header(key, value)
        self.nonbytes_body = nonbytes_body
        self.read_calls = 0
        self.close_calls = 0

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status

    def read(self, size: int = -1) -> bytes:  # type: ignore[override]
        self.read_calls += 1
        value = super().read(size)
        if self.nonbytes_body:
            return "not-bytes"  # type: ignore[return-value]
        return value

    def close(self) -> None:
        self.close_calls += 1
        super().close()


class FixtureOpener:
    """Strict sequential opener with no network operation."""

    def __init__(self, exchanges: Sequence[HTTPFixtureExchange]) -> None:
        self._exchanges = list(exchanges)
        self.calls = 0

    def __call__(self, request: urllib.request.Request, timeout: float) -> BinaryIO:
        self.calls += 1
        if not self._exchanges:
            raise LivePilotRefusal(FAILURE_ROUTES[3], "unexpected HTTP attempt")
        expected = self._exchanges.pop(0)
        observed_headers = _request_headers(request)
        if (
            request.full_url != expected.url
            or request.get_method() != "GET"
            or request.data is not None
            or timeout != MAX_TIMEOUT_SECONDS
            or observed_headers
            != {
                "accept": "application/json",
                "accept-encoding": "identity",
                "user-agent": "NeuroDecodeKit-MARC1PS/0.1",
            }
        ):
            raise LivePilotRefusal(FAILURE_ROUTES[3], "mock request differs")
        return expected.response

    def assert_consumed(self) -> None:
        if self._exchanges:
            raise LivePilotRefusal(FAILURE_ROUTES[3], "expected HTTP attempt is missing")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON number")


def _strict_json_value(payload: bytes) -> Any:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    text = payload.decode("utf-8", errors="strict")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise ValueError("JSON control character differs")
    return json.loads(
        text,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )


def _read_tracked_object(
    path: Path,
    *,
    expected_sha256: str,
    maximum_bytes: int = MAX_COMBINED_OUTPUT_BYTES,
) -> dict[str, Any]:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "tracked proof is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise LivePilotRefusal(FAILURE_ROUTES[0], "tracked proof type differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            payload = os.read(descriptor, maximum_bytes + 1)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "tracked proof open failed") from exc
    if len(payload) > maximum_bytes or _sha256_bytes(payload) != expected_sha256:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "tracked proof identity differs")
    try:
        value = _strict_json_value(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "tracked proof JSON differs") from exc
    if not isinstance(value, dict):
        raise LivePilotRefusal(FAILURE_ROUTES[0], "tracked proof root differs")
    return value


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact decision that passed both required remote jobs."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _read_tracked_object(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=DECISION_SHA256,
    )
    request = _read_tracked_object(
        root / REQUEST_RELATIVE_PATH,
        expected_sha256=REQUEST_SHA256,
    )
    sequence = decision.get("registered_sequence", {})
    authorization = decision.get("authorization", {})
    wrist = sequence.get("Wrist_public_metadata", {})
    freewill = sequence.get("Freewill_private_inventory", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc1_privacy_preserving_pilot_selection_authorization_decision"
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "7f1ba0936e4e0266c0210648aa641feab63cd0eb"
        or decision.get("user_authorization", {}).get("actual_message_SHA256")
        != "aedb564a57be18493fc20376676ef404794ca169d02985228aa8424cd7f7e6e8"
        or authorization.get("real_selector_implementation_authorized_after_decision_green")
        is not True
        or authorization.get("one_private_and_one_public_metadata_selection_authorized_after_wrapper_green")
        is not True
        or authorization.get("payload_acquisition_or_download_authorized_now") is not False
        or authorization.get(
            "derivative_model_training_inference_prediction_freeze_or_score_authorized_now"
        )
        is not False
        or freewill.get("relative_path") != str(FREEWILL_PRIVATE_RELATIVE_PATH)
        or freewill.get("bytes") != FREEWILL_PRIVATE_BYTES
        or freewill.get("mode") != "0600"
        or freewill.get("sha256") != FREEWILL_PRIVATE_SHA256
        or freewill.get("content_opens") != 1
        or wrist.get("metadata_endpoint") != WRIST_METADATA_URL
        or wrist.get("accepted_body_count") != 1
        or wrist.get("accepted_body_cap_bytes") != MAX_NETWORK_BODY_BYTES
        or wrist.get("expected_file_rows") != WRIST_EXPECTED_ROWS
        or wrist.get("expected_participant_archives") != WRIST_EXPECTED_PARTICIPANTS
        or wrist.get("expected_supplementary_rows") != WRIST_EXPECTED_SUPPLEMENTARY
        or wrist.get("expected_record_bytes") != WRIST_EXPECTED_BYTES
        or sequence.get("payload_requests") != 0
        or sequence.get("signal_reads") != 0
        or sequence.get("target_reads") != 0
        or sequence.get("model_runs") != 0
        or sequence.get("scoring_runs") != 0
        or sequence.get("retries") != 0
        or sequence.get("reruns") != 0
        or request.get("authorized_now") is not False
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[0], "authorization proof differs")
    frozen = (
        (GENERATED_IMPLEMENTATION_RELATIVE_PATH, GENERATED_IMPLEMENTATION_SHA256),
        (GENERATED_RESULT_RELATIVE_PATH, GENERATED_RESULT_SHA256),
        (FREEWILL_RESULT_RELATIVE_PATH, FREEWILL_RESULT_SHA256),
        (GENERATED_SELECTOR_RELATIVE_PATH, GENERATED_SELECTOR_SHA256),
    )
    if any(_sha256_file(root / path) != digest for path, digest in frozen):
        raise LivePilotRefusal(FAILURE_ROUTES[0], "frozen upstream artifact differs")
    selector.load_registered_contract(root)
    return decision


def load_implementation_record(
    repo_root: str | Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    """Validate the generated-qualified live-wrapper record and file bindings."""

    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "implementation proof is malformed")
    root = Path(repo_root)
    record = _read_tracked_object(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256=expected_sha256,
    )
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("lane_id") != LANE_ID
        or record.get("status")
        != "generated_mock_live_selector_qualified_requires_remote_green_before_real_metadata"
        or record.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or record.get("green_decision", {}).get("push_CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or record.get("generated_qualification", {}).get("all_gates_passed") is not True
        or record.get("execution_state", {}).get("real_metadata_execution_consumed")
        is not False
        or tuple(record.get("generated_qualification", {}).get("mutation_routes", {}))
        != REQUIRED_MUTATIONS
        or any(
            route not in FAILURE_ROUTES
            for route in record.get("generated_qualification", {})
            .get("mutation_routes", {})
            .values()
        )
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[0], "implementation record differs")
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
            raise LivePilotRefusal(FAILURE_ROUTES[0], "implementation file hash differs")
    return record


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def verify_green_wrapper_evidence(
    repo_root: str | Path,
    evidence: GreenWrapperEvidence,
) -> dict[str, Any]:
    """Require the exact clean HEAD and externally observed green job identifiers."""

    root = Path(repo_root)
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
        raise LivePilotRefusal(FAILURE_ROUTES[0], "green wrapper evidence is malformed")
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.implementation_commit:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "HEAD differs from wrapper evidence")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    if clean.returncode or clean.stdout.strip():
        raise LivePilotRefusal(FAILURE_ROUTES[0], "tracked worktree is not clean")
    ancestor = _git(root, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, "HEAD")
    if ancestor.returncode:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "green decision is not an ancestor")
    load_green_decision(root)
    return load_implementation_record(
        root,
        expected_sha256=evidence.implementation_registry_sha256,
    )


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def preconsumption_machine_gate(
    root: str | Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Measure every computer-protection condition before a consumed marker."""

    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise LivePilotRefusal(FAILURE_ROUTES[6], "thread environment is not one")
    try:
        free_bytes = int(disk_usage_reader(Path(root)).free)
        logical_cpus = cpu_count_reader()
        load_values = loadavg_reader()
        peak_rss = int(rss_reader())
    except Exception as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[6], "machine metric is unavailable") from exc
    if logical_cpus is None or logical_cpus <= 0 or not load_values:
        raise LivePilotRefusal(FAILURE_ROUTES[6], "CPU or load metric is unavailable")
    one_minute_load = float(load_values[0])
    normalized_load = one_minute_load / logical_cpus
    if (
        free_bytes < MINIMUM_FREE_DISK_BYTES
        or not math.isfinite(one_minute_load)
        or one_minute_load < 0
        or normalized_load > MAX_LOAD_PER_LOGICAL_CPU
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[6], "machine resource cap failed")
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


def _base_access_counters() -> dict[str, int]:
    return {
        "private_Freewill_manifest_path_operations": 0,
        "private_Freewill_manifest_content_opens": 0,
        "private_Freewill_manifest_body_reads": 0,
        "private_Freewill_manifest_bytes": 0,
        "private_Freewill_manifest_hashes": 0,
        "private_Freewill_manifest_parses": 0,
        "public_Wrist_metadata_requests": 0,
        "public_Wrist_metadata_response_opens": 0,
        "public_Wrist_metadata_body_reads": 0,
        "public_Wrist_metadata_body_bytes": 0,
        "public_Wrist_metadata_hashes": 0,
        "public_Wrist_metadata_parses": 0,
        "DNS_queries": 0,
        "network_redirects": 0,
        "network_body_bytes": 0,
        "real_participant_selections": 0,
        "real_member_or_archive_selections": 0,
        "private_consumed_markers": 0,
        "private_selection_manifests": 0,
        "public_aggregate_reports": 0,
        "local_header_requests": 0,
        "member_or_archive_payload_requests": 0,
        "member_or_archive_payload_bytes": 0,
        "signal_sample_reads": 0,
        "channel_geometry_event_onset_or_quality_reads": 0,
        "target_label_response_sentence_key_or_trial_reads": 0,
        "derivative_cache_split_epoch_window_or_feature_operations": 0,
        "training_or_parameter_update_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "prediction_freezes": 0,
        "target_deliveries": 0,
        "scoring_events": 0,
        "dependency_installs": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "temporary_cleanup_operations": 0,
        "retries_or_reruns": 0,
        "post_result_updates": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
        "end_to_end_latency_measurements": 0,
        "operations_on_other_projects": 0,
    }


def read_locked_freewill_manifest(
    path: Path,
    *,
    expected_bytes: int,
    expected_sha256: str,
    counters: dict[str, int] | None,
) -> tuple[dict[str, Any], bytes]:
    """Perform one no-follow path validation, content open, read, hash, and parse."""

    if expected_bytes <= 0 or HEX64_RE.fullmatch(expected_sha256) is None:
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private source contract differs")
    if counters is not None:
        counters["private_Freewill_manifest_path_operations"] += 1
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest is unavailable") from exc
    if (
        stat.S_ISLNK(before.st_mode)
        or not stat.S_ISREG(before.st_mode)
        or stat.S_IMODE(before.st_mode) != 0o600
        or before.st_size != expected_bytes
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest path size or mode differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest no-follow open failed") from exc
    if counters is not None:
        counters["private_Freewill_manifest_content_opens"] += 1
    try:
        after = os.fstat(descriptor)
        if (
            after.st_dev != before.st_dev
            or after.st_ino != before.st_ino
            or not stat.S_ISREG(after.st_mode)
            or stat.S_IMODE(after.st_mode) != 0o600
            or after.st_size != expected_bytes
        ):
            raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest changed during open")
        payload = os.read(descriptor, expected_bytes + 1)
    finally:
        os.close(descriptor)
    if counters is not None:
        counters["private_Freewill_manifest_body_reads"] += 1
        counters["private_Freewill_manifest_bytes"] += len(payload)
    if len(payload) != expected_bytes:
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest byte count differs")
    observed_sha256 = _sha256_bytes(payload)
    if counters is not None:
        counters["private_Freewill_manifest_hashes"] += 1
    if observed_sha256 != expected_sha256:
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest SHA-256 differs")
    try:
        value = _strict_json_value(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest JSON differs") from exc
    if counters is not None:
        counters["private_Freewill_manifest_parses"] += 1
    if not isinstance(value, dict):
        raise LivePilotRefusal(FAILURE_ROUTES[1], "private manifest root differs")
    return value, payload


def _canonical_freewill_input(manifest: Mapping[str, Any]) -> bytes:
    value = copy.deepcopy(dict(manifest))
    entries = value.get("entries")
    if isinstance(entries, list):
        value["entries"] = sorted(entries, key=lambda row: str(row.get("member_name", "")))
    return _canonical_json_bytes(value)


def _validate_real_freewill_manifest(
    manifest: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    expected_top = {
        "schema_name",
        "schema_version",
        "proof_posture",
        "source_identity",
        "transport_body_sha256",
        "entries",
    }
    source = manifest.get("source_identity") if isinstance(manifest, dict) else None
    transport = manifest.get("transport_body_sha256") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or set(manifest) != expected_top
        or manifest.get("schema_name")
        != "neurodecodekit.marc1_central_directory_private_manifest"
        or manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("proof_posture")
        != "live_archive_private_central_directory_metadata_only"
        or not isinstance(source, dict)
        or source
        != {
            "provider": "Figshare",
            "record_id": 28_632_599,
            "version": 1,
            "file_id": FREEWILL_FILE_ID,
            "declared_archive_bytes": FREEWILL_ARCHIVE_BYTES,
            "registered_MD5": FREEWILL_ARCHIVE_MD5,
            "whole_archive_downloaded": False,
            "member_payload_opened": False,
        }
        or not isinstance(transport, dict)
        or set(transport) != {"metadata", "tail", "central_directory"}
        or any(not isinstance(value, str) or HEX64_RE.fullmatch(value) is None for value in transport.values())
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[2], "Freewill source identity differs")

    # Reuse the frozen generated selector's row, bundle, rank, split, and cap logic.
    adapted = copy.deepcopy(dict(manifest))
    adapted["proof_posture"] = "generated_fixture_private_metadata_only"
    adapted["source_identity"] = {
        "provider": "generated_fixture",
        "record_id": 28_632_599,
        "version": 1,
        "file_id": 0,
        "declared_archive_bytes": FREEWILL_ARCHIVE_BYTES,
        "registered_MD5": "0" * 32,
        "whole_archive_downloaded": False,
        "member_payload_opened": False,
    }
    try:
        result = selector._validate_freewill_manifest(adapted, contract)
    except selector.PilotSelectionRefusal as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[2], "frozen Freewill selector refused") from exc
    canonical_sha256 = _sha256_bytes(_canonical_freewill_input(manifest))
    return {
        **result,
        "canonical_source_sha256": canonical_sha256,
    }


def _safe_public_filename(value: Any) -> str:
    if not isinstance(value, str) or not value or unicodedata.normalize("NFC", value) != value:
        raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist filename differs")
    if value in {".", ".."} or "/" in value or "\\" in value or "\x00" in value:
        raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist filename is unsafe")
    return value


def _canonical_wrist_rows(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return _canonical_json_bytes(sorted((dict(row) for row in rows), key=lambda row: row["id"]))


def parse_wrist_metadata(payload: bytes, *, counters: dict[str, int] | None) -> dict[str, Any]:
    """Parse exactly the frozen Figshare file-list schema without target fields."""

    try:
        value = _strict_json_value(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist metadata JSON differs") from exc
    if counters is not None:
        counters["public_Wrist_metadata_parses"] += 1
    if not isinstance(value, list) or len(value) != WRIST_EXPECTED_ROWS:
        raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist metadata row count differs")
    file_ids: set[int] = set()
    names: set[str] = set()
    participants: dict[str, dict[str, Any]] = {}
    supplementary = 0
    total_bytes = 0
    for row in value:
        if not isinstance(row, dict) or set(row) != WRIST_RAW_FIELDS:
            if isinstance(row, dict) and set(row) & TARGET_LEAK_KEYS:
                raise LivePilotRefusal(FAILURE_ROUTES[4], "target-like metadata field is forbidden")
            raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist metadata fields differ")
        file_id = row["id"]
        size = row["size"]
        name = _safe_public_filename(row["name"])
        if (
            isinstance(file_id, bool)
            or not isinstance(file_id, int)
            or file_id <= 0
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size <= 0
            or row["is_link_only"] is not False
            or not isinstance(row["download_url"], str)
            or row["download_url"] != f"https://ndownloader.figshare.com/files/{file_id}"
        ):
            raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist metadata type or URL differs")
        if file_id in file_ids or name in names:
            raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist file identity is duplicated")
        file_ids.add(file_id)
        names.add(name)
        for key in ("supplied_md5", "computed_md5"):
            if not isinstance(row[key], str) or MD5_RE.fullmatch(row[key]) is None:
                raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist MD5 declaration differs")
        if row["supplied_md5"] != row["computed_md5"]:
            raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist MD5 declarations disagree")
        total_bytes += size
        match = WRIST_PARTICIPANT_RE.fullmatch(name)
        if match is None:
            supplementary += 1
            continue
        subject = match.group("subject")
        participants[subject] = dict(row)
    expected_subjects = {f"sub-{index:02d}" for index in range(1, 46)}
    if (
        set(participants) != expected_subjects
        or len(participants) != WRIST_EXPECTED_PARTICIPANTS
        or supplementary != WRIST_EXPECTED_SUPPLEMENTARY
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist participant inventory differs")
    sub01 = participants["sub-01"]
    if (
        sub01["id"] != WRIST_SUB01_FILE_ID
        or sub01["size"] != WRIST_SUB01_BYTES
        or sub01["computed_md5"] != WRIST_SUB01_MD5
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist sub-01 identity anchor differs")
    if total_bytes != WRIST_EXPECTED_BYTES:
        raise LivePilotRefusal(FAILURE_ROUTES[4], "Wrist record byte total differs")
    return {
        "rows": value,
        "participants": participants,
        "supplementary_rows": supplementary,
        "declared_bytes": total_bytes,
        "canonical_source_sha256": _sha256_bytes(_canonical_wrist_rows(value)),
    }


def _select_real_metadata(
    freewill_manifest: Mapping[str, Any],
    wrist: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    generated: bool,
) -> selector.SelectionResult:
    freewill = _validate_real_freewill_manifest(freewill_manifest, contract)
    axis = contract["wrist_axis"]
    expected_selected = axis["selected_subject_ids_in_rank_order"]
    ranked = selector._rank_subjects(axis["selection_seed"], axis["eligible_subject_ids"])[
        : selector.EXPECTED_SELECTED_SUBJECTS
    ]
    try:
        selector._validate_selected_subjects(
            ranked,
            expected_selected,
            axis["eligible_subject_ids"],
        )
        split = axis["later_split"]
        selector._validate_wrist_split(
            split["fit_runs"],
            split["heldout_runs"],
            split["expected_fit_trials"],
            split["expected_heldout_trials"],
        )
    except selector.PilotSelectionRefusal as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[5], "frozen Wrist selector refused") from exc
    participants = wrist["participants"]
    selected = [participants[subject] for subject in expected_selected]
    wrist_reserved_bytes = sum(row["size"] for row in selected)
    if wrist_reserved_bytes > selector.WRIST_PAYLOAD_CAP_BYTES:
        raise LivePilotRefusal(FAILURE_ROUTES[5], "Wrist selection exceeds byte cap")
    joint_reserved_bytes = freewill["reserved_bytes"] + wrist_reserved_bytes
    if joint_reserved_bytes > selector.JOINT_PAYLOAD_CAP_BYTES:
        raise LivePilotRefusal(FAILURE_ROUTES[5], "joint selection exceeds byte cap")

    freewill_source_id = "freewill_23_generated_live_shape" if generated else "freewill_23_figshare_v1"
    wrist_source_id = "wrist_45_generated_live_shape" if generated else "wrist_45_figshare_v3"
    freewill_rows: list[dict[str, Any]] = []
    for row in freewill["private_rows"]:
        rewritten = dict(row)
        rewritten["source_id"] = freewill_source_id
        rewritten["source_hashes"] = {
            "canonical_metadata_sha256": freewill["canonical_source_sha256"],
            "registered_inventory_sha256": FREEWILL_INVENTORY_SHA256,
            "contract_sha256": selector.CONTRACT_SHA256,
        }
        freewill_rows.append(rewritten)
    wrist_rows = [
        {
            "source_id": wrist_source_id,
            "subject_id": subject,
            "session_id": None,
            "run_id": "runs-01-through-08",
            "split_role": "fit-runs-01-06_and_heldout-runs-07-08",
            "member_or_archive_name": participants[subject]["name"],
            "file_id_if_available": participants[subject]["id"],
            "local_header_offset_if_available": None,
            "CRC32_if_available": None,
            "compressed_size": participants[subject]["size"],
            "uncompressed_size": None,
            "source_hashes": {
                "canonical_metadata_sha256": wrist["canonical_source_sha256"],
                "declared_MD5": participants[subject]["computed_md5"],
                "contract_sha256": selector.CONTRACT_SHA256,
            },
        }
        for subject in expected_selected
    ]
    private_rows = freewill_rows + wrist_rows
    if len(private_rows) != 300 or any(
        tuple(row) != selector.PRIVATE_ROW_FIELDS for row in private_rows
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "private selection row shape differs")
    private_manifest = {
        "schema_name": PRIVATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "proof_posture": (
            "generated_live_shape_selection_only_no_scientific_value"
            if generated
            else "real_metadata_selection_only_no_payload_or_scientific_result"
        ),
        "contract_sha256": selector.CONTRACT_SHA256,
        "rows": private_rows,
    }
    freewill_identity = freewill["selection_identity"]
    wrist_identity = {
        "selected_subject_ids": list(expected_selected),
        "fit_runs": [1, 2, 3, 4, 5, 6],
        "heldout_runs": [7, 8],
    }
    joint_identity = {"freewill": freewill_identity, "wrist": wrist_identity}
    return selector.SelectionResult(
        private_manifest=private_manifest,
        cohort_summary={
            "freewill_selected_subject_ids": list(
                contract["freewill_axis"]["selected_subject_ids_in_rank_order"]
            ),
            "wrist_selected_subject_ids": list(expected_selected),
            "selected_subjects_per_axis": 12,
            "selection_was_target_quality_and_outcome_free": True,
        },
        split_summary={
            "freewill_fit_session": "ses-01",
            "freewill_heldout_session": "ses-02",
            "freewill_fit_run_bundles": 36,
            "freewill_heldout_run_bundles": 36,
            "freewill_selected_run_bundles": 72,
            "freewill_selected_core_members": 288,
            "wrist_fit_runs_per_participant": 6,
            "wrist_heldout_runs_per_participant": 2,
            "wrist_fit_runs": 72,
            "wrist_heldout_runs": 24,
            "wrist_expected_fit_trials": 2_880,
            "wrist_expected_heldout_trials": 960,
            "fit_heldout_overlap": 0,
        },
        byte_summary={
            "freewill_reserved_payload_bytes": freewill["reserved_bytes"],
            "freewill_payload_cap_bytes": selector.FREEWILL_PAYLOAD_CAP_BYTES,
            "wrist_reserved_payload_bytes": wrist_reserved_bytes,
            "wrist_payload_cap_bytes": selector.WRIST_PAYLOAD_CAP_BYTES,
            "joint_reserved_payload_bytes": joint_reserved_bytes,
            "joint_payload_cap_bytes": selector.JOINT_PAYLOAD_CAP_BYTES,
            "fallback_used": False,
        },
        selection_hashes={
            "freewill_canonical_metadata_sha256": freewill["canonical_source_sha256"],
            "wrist_canonical_metadata_sha256": wrist["canonical_source_sha256"],
            "freewill_selection_identity_sha256": _sha256_bytes(
                _canonical_json_bytes(freewill_identity)
            ),
            "wrist_selection_identity_sha256": _sha256_bytes(
                _canonical_json_bytes(wrist_identity)
            ),
            "joint_selection_identity_sha256": _sha256_bytes(
                _canonical_json_bytes(joint_identity)
            ),
            "private_selection_manifest_sha256": _sha256_bytes(
                _canonical_json_bytes(private_manifest)
            ),
        },
    )


def _request_headers(request: urllib.request.Request) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in request.header_items():
        lowered = key.strip().lower()
        if not lowered or lowered in result or "\r" in value or "\n" in value:
            raise LivePilotRefusal(FAILURE_ROUTES[3], "request header differs")
        result[lowered] = value.strip()
    return result


def _response_headers(response: BinaryIO) -> dict[str, str]:
    source = getattr(response, "headers", None)
    if source is None:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "response headers are unavailable")
    items = source.raw_items() if hasattr(source, "raw_items") else source.items()
    critical = {
        "content-encoding",
        "content-length",
        "content-type",
        "location",
        "transfer-encoding",
    }
    result: dict[str, str] = {}
    for key, value in items:
        lowered = str(key).strip().lower()
        text = str(value).strip()
        if not lowered or "\r" in text or "\n" in text:
            raise LivePilotRefusal(FAILURE_ROUTES[3], "response header differs")
        if lowered not in critical:
            continue
        if lowered in result:
            raise LivePilotRefusal(FAILURE_ROUTES[3], "critical response header is duplicated")
        result[lowered] = text
    return result


def _response_status(response: BinaryIO) -> int:
    status_code = getattr(response, "status", None)
    if status_code is None and hasattr(response, "getcode"):
        status_code = response.getcode()
    if type(status_code) is not int:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "response status is unavailable")
    return status_code


def _response_url(response: BinaryIO) -> str:
    if not hasattr(response, "geturl"):
        raise LivePilotRefusal(FAILURE_ROUTES[3], "response URL is unavailable")
    value = response.geturl()
    if not isinstance(value, str):
        raise LivePilotRefusal(FAILURE_ROUTES[3], "response URL differs")
    return value


def _read_once(response: BinaryIO, maximum_bytes: int) -> bytes:
    try:
        payload = response.read(maximum_bytes + 1)
    except Exception as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "response body read failed") from exc
    if not isinstance(payload, bytes):
        raise LivePilotRefusal(FAILURE_ROUTES[3], "response body is not bytes")
    if len(payload) > maximum_bytes:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "response body exceeds cap")
    return payload


def _open_live_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)
    try:
        return opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        return exc
    except Exception as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "public request failed") from exc


def _resolve_global_addresses(hostname: str) -> tuple[str, ...]:
    try:
        values = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect DNS lookup failed") from exc
    addresses = tuple(sorted({str(value[4][0]) for value in values}))
    if not addresses:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect DNS result is empty")
    return addresses


def _validate_redirect_target(
    current_url: str,
    location: str,
    *,
    resolver: Callable[[str], Sequence[str]],
    counters: dict[str, int] | None,
) -> str:
    target = urljoin(current_url, location)
    parsed = urlsplit(target)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in {None, 443}
        or parsed.fragment
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect target differs")
    if counters is not None:
        counters["DNS_queries"] += 1
    try:
        addresses = resolver(parsed.hostname)
        if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
            raise ValueError("non-global address")
    except (ValueError, OSError) as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect destination is not global") from exc
    return target


def fetch_wrist_metadata(
    opener: Callable[[urllib.request.Request, float], BinaryIO],
    *,
    resolver: Callable[[str], Sequence[str]],
    counters: dict[str, int] | None,
) -> tuple[bytes, dict[str, Any]]:
    """Fetch one terminal bounded JSON body with manual bodyless redirects."""

    current = WRIST_METADATA_URL
    seen = {current}
    redirects = 0
    attempts = 0
    while True:
        if attempts >= MAX_HTTP_ATTEMPTS:
            raise LivePilotRefusal(FAILURE_ROUTES[3], "HTTP attempt cap exceeded")
        request = urllib.request.Request(
            current,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "identity",
                "User-Agent": "NeuroDecodeKit-MARC1PS/0.1",
            },
            method="GET",
        )
        attempts += 1
        if counters is not None:
            counters["public_Wrist_metadata_requests"] += 1
        try:
            response = opener(request, MAX_TIMEOUT_SECONDS)
        except LivePilotRefusal:
            raise
        except Exception as exc:
            raise LivePilotRefusal(FAILURE_ROUTES[3], "HTTP opener failed") from exc
        if counters is not None:
            counters["public_Wrist_metadata_response_opens"] += 1
        try:
            status_code = _response_status(response)
            if _response_url(response) != current:
                raise LivePilotRefusal(FAILURE_ROUTES[3], "automatic redirect or URL drift")
            headers = _response_headers(response)
            if "transfer-encoding" in headers:
                raise LivePilotRefusal(FAILURE_ROUTES[3], "transfer encoding is forbidden")
            if status_code in REDIRECT_STATUSES:
                if (
                    "content-encoding" in headers
                    and headers["content-encoding"].lower() != "identity"
                ):
                    raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect encoding differs")
                if redirects >= MAX_REDIRECTS or "location" not in headers:
                    raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect contract differs")
                if _read_once(response, 0):
                    raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect body is not empty")
                target = _validate_redirect_target(
                    current,
                    headers["location"],
                    resolver=resolver,
                    counters=counters,
                )
                if target in seen:
                    raise LivePilotRefusal(FAILURE_ROUTES[3], "redirect loop detected")
                seen.add(target)
                current = target
                redirects += 1
                if counters is not None:
                    counters["network_redirects"] += 1
                continue
            if status_code != 200:
                raise LivePilotRefusal(FAILURE_ROUTES[3], "terminal HTTP status differs")
            if headers.get("content-encoding", "").lower() != "identity":
                raise LivePilotRefusal(FAILURE_ROUTES[3], "terminal content encoding differs")
            content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if content_type != "application/json":
                raise LivePilotRefusal(FAILURE_ROUTES[3], "terminal content type differs")
            declared_length = headers.get("content-length")
            if declared_length is not None:
                if not declared_length.isdigit() or int(declared_length) > MAX_NETWORK_BODY_BYTES:
                    raise LivePilotRefusal(FAILURE_ROUTES[3], "content length differs")
            payload = _read_once(response, MAX_NETWORK_BODY_BYTES)
            if declared_length is not None and int(declared_length) != len(payload):
                raise LivePilotRefusal(FAILURE_ROUTES[3], "content length does not match body")
            if counters is not None:
                counters["public_Wrist_metadata_body_reads"] += 1
                counters["public_Wrist_metadata_body_bytes"] += len(payload)
                counters["public_Wrist_metadata_hashes"] += 1
                counters["network_body_bytes"] += len(payload)
            return payload, {
                "HTTP_request_attempts": attempts,
                "network_redirects": redirects,
                "accepted_response_bodies": 1,
                "accepted_response_body_bytes": len(payload),
                "raw_response_sha256": _sha256_bytes(payload),
                "terminal_host_sha256": _sha256_bytes(
                    (urlsplit(current).hostname or "").encode("ascii")
                ),
                "content_length_present": declared_length is not None,
                "raw_headers_published": False,
                "raw_body_persisted": False,
                "terminal_URL_published": False,
            }
        finally:
            try:
                response.close()
            except Exception:
                pass


def build_generated_real_freewill_manifest(
    *,
    reverse_rows: bool = False,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a real-schema Freewill manifest using only generated rows."""

    value = selector.build_generated_freewill_manifest(
        row_order="reversed" if reverse_rows else "canonical",
        contract=contract,
    )
    value["proof_posture"] = "live_archive_private_central_directory_metadata_only"
    value["source_identity"] = {
        "provider": "Figshare",
        "record_id": 28_632_599,
        "version": 1,
        "file_id": FREEWILL_FILE_ID,
        "declared_archive_bytes": FREEWILL_ARCHIVE_BYTES,
        "registered_MD5": FREEWILL_ARCHIVE_MD5,
        "whole_archive_downloaded": False,
        "member_payload_opened": False,
    }
    return value


def build_generated_wrist_response(*, reverse_rows: bool = False) -> bytes:
    """Build the frozen seven-field Figshare schema without network access."""

    rows: list[dict[str, Any]] = []
    participant_total = 0
    for index in range(1, 46):
        name = f"sub-{index:02d}.zip"
        if index == 1:
            file_id = WRIST_SUB01_FILE_ID
            size = WRIST_SUB01_BYTES
            digest = WRIST_SUB01_MD5
        else:
            file_id = WRIST_SUB01_FILE_ID + index
            size = 50_000_000 + index
            digest = hashlib.md5(name.encode("ascii"), usedforsecurity=False).hexdigest()
        participant_total += size
        rows.append(
            {
                "id": file_id,
                "name": name,
                "size": size,
                "is_link_only": False,
                "download_url": f"https://ndownloader.figshare.com/files/{file_id}",
                "supplied_md5": digest,
                "computed_md5": digest,
            }
        )
    remaining = WRIST_EXPECTED_BYTES - participant_total
    base, remainder = divmod(remaining, WRIST_EXPECTED_SUPPLEMENTARY)
    for index in range(WRIST_EXPECTED_SUPPLEMENTARY):
        name = f"supplement-{index:02d}.txt"
        file_id = 70_000_000 + index
        digest = hashlib.md5(name.encode("ascii"), usedforsecurity=False).hexdigest()
        rows.append(
            {
                "id": file_id,
                "name": name,
                "size": base + (1 if index < remainder else 0),
                "is_link_only": False,
                "download_url": f"https://ndownloader.figshare.com/files/{file_id}",
                "supplied_md5": digest,
                "computed_md5": digest,
            }
        )
    if reverse_rows:
        rows.reverse()
    return _canonical_json_bytes(rows)


def generated_http_fixture(
    payload: bytes,
    *,
    redirects: int,
) -> tuple[FixtureOpener, Callable[[str], Sequence[str]]]:
    """Create a strict direct or two-redirect generated exchange sequence."""

    if redirects not in {0, 2}:
        raise ValueError("generated redirect count must be zero or two")
    exchanges: list[HTTPFixtureExchange] = []
    current = WRIST_METADATA_URL
    if redirects:
        targets = (
            "https://cdn-a.example.net/wrist/files",
            "https://cdn-b.example.net/wrist/files",
        )
        for target in targets:
            exchanges.append(
                HTTPFixtureExchange(
                    current,
                    FixtureHTTPResponse(
                        b"",
                        status=302,
                        url=current,
                        headers={"Content-Length": "0", "Location": target},
                    ),
                )
            )
            current = target
    exchanges.append(
        HTTPFixtureExchange(
            current,
            FixtureHTTPResponse(
                payload,
                status=200,
                url=current,
                headers={
                    "Content-Encoding": "identity",
                    "Content-Length": str(len(payload)),
                    "Content-Type": "application/json; charset=utf-8",
                },
            ),
        )
    )

    def resolver(hostname: str) -> Sequence[str]:
        return {
            "cdn-a.example.net": ("8.8.8.8",),
            "cdn-b.example.net": ("1.1.1.1",),
        }.get(hostname, ("8.8.4.4",))

    return FixtureOpener(exchanges), resolver


def _expect_refusal(name: str, operation: Callable[[], Any]) -> str:
    try:
        operation()
    except LivePilotRefusal as exc:
        return exc.route
    raise LivePilotRefusal(
        FAILURE_ROUTES[6],
        f"required generated mutation did not refuse: {name}",
    )


def _forbidden_target_operation() -> None:
    raise LivePilotRefusal(FAILURE_ROUTES[4], "target operation is forbidden")


def run_required_mutations(
    freewill: Mapping[str, Any],
    wrist_payload: bytes,
    *,
    contract: Mapping[str, Any],
) -> dict[str, str]:
    """Exercise all frozen failure classes using generated values only."""

    wrist_rows = _strict_json_value(wrist_payload)

    def freewill_mutation(change: Callable[[dict[str, Any]], None]) -> Callable[[], Any]:
        def operation() -> Any:
            value = copy.deepcopy(dict(freewill))
            change(value)
            return _validate_real_freewill_manifest(value, contract)

        return operation

    def wrist_mutation(change: Callable[[list[dict[str, Any]]], None]) -> Callable[[], Any]:
        def operation() -> Any:
            value = copy.deepcopy(wrist_rows)
            change(value)
            return parse_wrist_metadata(_canonical_json_bytes(value), counters=None)

        return operation

    def selected_cap(rows: list[dict[str, Any]]) -> None:
        selected = contract["wrist_axis"]["selected_subject_ids_in_rank_order"]
        selected_names = {f"{subject}.zip" for subject in selected}
        target = next(row for row in rows if row["name"] in selected_names)
        selected_total = sum(row["size"] for row in rows if row["name"] in selected_names)
        remaining = selector.WRIST_PAYLOAD_CAP_BYTES - selected_total + 1
        target["size"] += remaining
        for row in rows:
            if row["name"] in selected_names or row["name"] == "sub-01.zip":
                continue
            reduction = min(remaining, row["size"] - 1)
            row["size"] -= reduction
            remaining -= reduction
            if remaining == 0:
                return
        raise AssertionError("generated nonselected bytes cannot preserve total")

    def remove_first_core_member(value: dict[str, Any]) -> None:
        for row in value["entries"]:
            if selector.CORE_MEMBER_RE.fullmatch(row["member_name"]):
                row["member_name"] = "generated_removed_core_member.txt"
                return
        raise AssertionError("generated core member is unavailable")

    def select_after_wrist(change: Callable[[list[dict[str, Any]]], None]) -> Any:
        value = copy.deepcopy(wrist_rows)
        change(value)
        parsed = parse_wrist_metadata(_canonical_json_bytes(value), counters=None)
        return _select_real_metadata(freewill, parsed, contract=contract, generated=True)

    def bad_private_hash() -> Any:
        with _temporary_private_manifest(freewill) as path:
            return read_locked_freewill_manifest(
                path,
                expected_bytes=path.stat().st_size,
                expected_sha256="0" * 64,
                counters=None,
            )

    def bad_private_mode() -> Any:
        with _temporary_private_manifest(freewill, mode=0o644) as path:
            return read_locked_freewill_manifest(
                path,
                expected_bytes=path.stat().st_size,
                expected_sha256=_sha256_file(path),
                counters=None,
            )

    def bad_private_symlink() -> Any:
        with _temporary_private_manifest(freewill, symlink=True) as path:
            target = path.resolve()
            return read_locked_freewill_manifest(
                path,
                expected_bytes=target.stat().st_size,
                expected_sha256=_sha256_file(target),
                counters=None,
            )

    def bad_transport(response: FixtureHTTPResponse, resolver=None) -> Any:  # noqa: ANN001
        opener = FixtureOpener([HTTPFixtureExchange(WRIST_METADATA_URL, response)])
        return fetch_wrist_metadata(
            opener,
            resolver=resolver or (lambda _hostname: ("8.8.8.8",)),
            counters=None,
        )

    def private_redirect() -> Any:
        response = FixtureHTTPResponse(
            b"",
            status=302,
            url=WRIST_METADATA_URL,
            headers={"Content-Length": "0", "Location": "https://private.example/files"},
        )
        return bad_transport(response, resolver=lambda _hostname: ("127.0.0.1",))

    checks: dict[str, Callable[[], Any]] = {
        "private_hash_mismatch": bad_private_hash,
        "private_mode_mismatch": bad_private_mode,
        "private_symlink": bad_private_symlink,
        "freewill_source_identity": freewill_mutation(
            lambda value: value["source_identity"].__setitem__("file_id", 1)
        ),
        "freewill_row_count": freewill_mutation(lambda value: value["entries"].pop()),
        "freewill_unknown_row_field": freewill_mutation(
            lambda value: value["entries"][0].__setitem__("target", "forbidden")
        ),
        "freewill_duplicate_member": freewill_mutation(
            lambda value: value["entries"].__setitem__(1, copy.deepcopy(value["entries"][0]))
        ),
        "freewill_unsafe_path": freewill_mutation(
            lambda value: value["entries"][202].__setitem__("member_name", "../unsafe_eeg.eeg")
        ),
        "freewill_incomplete_bundle": freewill_mutation(remove_first_core_member),
        "wrist_root_shape": lambda: parse_wrist_metadata(b"{}\n", counters=None),
        "wrist_target_leak_field": wrist_mutation(
            lambda rows: rows[0].__setitem__("target", "left")
        ),
        "wrist_row_count": wrist_mutation(lambda rows: rows.pop()),
        "wrist_duplicate_file_id": wrist_mutation(
            lambda rows: rows[1].__setitem__("id", rows[0]["id"])
        ),
        "wrist_duplicate_name": wrist_mutation(
            lambda rows: rows[1].__setitem__("name", rows[0]["name"])
        ),
        "wrist_participant_name": wrist_mutation(
            lambda rows: rows[1].__setitem__("name", "participant-02.zip")
        ),
        "wrist_download_URL": wrist_mutation(
            lambda rows: rows[1].__setitem__("download_url", "https://example.invalid/file")
        ),
        "wrist_MD5_mismatch": wrist_mutation(
            lambda rows: rows[1].__setitem__("computed_md5", "0" * 32)
        ),
        "wrist_sub01_anchor": wrist_mutation(
            lambda rows: rows[0].__setitem__("size", rows[0]["size"] + 1)
        ),
        "wrist_record_byte_total": wrist_mutation(
            lambda rows: rows[-1].__setitem__("size", rows[-1]["size"] + 1)
        ),
        "wrist_selected_byte_cap": lambda: select_after_wrist(selected_cap),
        "transport_overflow": lambda: bad_transport(
            FixtureHTTPResponse(
                b"x" * (MAX_NETWORK_BODY_BYTES + 1),
                status=200,
                url=WRIST_METADATA_URL,
                headers={"Content-Type": "application/json"},
            )
        ),
        "transport_duplicate_header": lambda: bad_transport(
            FixtureHTTPResponse(
                wrist_payload,
                status=200,
                url=WRIST_METADATA_URL,
                headers={"Content-Type": "application/json"},
                duplicate_headers=(("Content-Type", "application/json"),),
            )
        ),
        "transport_transfer_encoding": lambda: bad_transport(
            FixtureHTTPResponse(
                wrist_payload,
                status=200,
                url=WRIST_METADATA_URL,
                headers={"Content-Type": "application/json", "Transfer-Encoding": "chunked"},
            )
        ),
        "transport_private_redirect": private_redirect,
        "public_private_field_leak": lambda: _walk_public({"file_id": 1}),
        "forbidden_target_operation": _forbidden_target_operation,
    }
    result = {name: _expect_refusal(name, operation) for name, operation in checks.items()}
    if tuple(result) != REQUIRED_MUTATIONS:
        raise LivePilotRefusal(FAILURE_ROUTES[6], "mutation order differs")
    return result


class _temporary_private_manifest:
    """Small generated-file context used only by local qualification."""

    def __init__(
        self,
        value: Mapping[str, Any],
        *,
        mode: int = 0o600,
        symlink: bool = False,
    ) -> None:
        import tempfile

        self._temp = tempfile.TemporaryDirectory()
        root = Path(self._temp.name)
        self._target = root / "target.json"
        self._target.write_bytes(_canonical_json_bytes(value))
        self._target.chmod(mode)
        self.path = root / "manifest.json"
        if symlink:
            self.path.symlink_to(self._target)
        else:
            os.replace(self._target, self.path)

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type, exc, traceback) -> None:  # noqa: ANN001
        self._temp.cleanup()


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_PUBLIC_KEYS or key.lower() in TARGET_LEAK_KEYS:
                raise LivePilotRefusal(FAILURE_ROUTES[5], "public report leaks private data")
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)
    elif isinstance(value, str) and ("://" in value or "/files/" in value):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "public report leaks a URL")


def _green_evidence(
    evidence: GreenWrapperEvidence | None,
    implementation_registry_sha256: str | None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "decision_commit": GREEN_DECISION_COMMIT,
        "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
        "decision_base_job_id": GREEN_DECISION_BASE_JOB_ID,
        "decision_optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
        "decision_registry_sha256": DECISION_SHA256,
        "both_decision_jobs_green": True,
    }
    if evidence is None:
        value.update(
            {
                "wrapper_commit": "uncommitted_generated_qualification",
                "wrapper_CI_run_id": None,
                "wrapper_base_job_id": None,
                "wrapper_optional_neuro_job_id": None,
                "implementation_registry_sha256": implementation_registry_sha256,
                "both_wrapper_jobs_green": False,
            }
        )
    else:
        value.update(
            {
                "wrapper_commit": evidence.implementation_commit,
                "wrapper_CI_run_id": evidence.implementation_ci_run_id,
                "wrapper_base_job_id": evidence.implementation_base_job_id,
                "wrapper_optional_neuro_job_id": evidence.implementation_optional_job_id,
                "implementation_registry_sha256": implementation_registry_sha256,
                "both_wrapper_jobs_green": True,
            }
        )
    return value


def _build_success_report(
    selection: selector.SelectionResult,
    *,
    generated: bool,
    evidence: GreenWrapperEvidence | None,
    implementation_registry_sha256: str | None,
    machine: Mapping[str, Any],
    transport_summary: Mapping[str, Any],
    counters: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
    input_bytes: int,
    output_bytes: int,
    mutation_routes: Mapping[str, str],
) -> dict[str, Any]:
    return {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": (
            "passed_generated_mock_live_selector_qualification"
            if generated
            else "passed_real_metadata_pilot_selection"
        ),
        "proof_posture": (
            "generated_metadata_and_mock_transport_only_no_scientific_value"
            if generated
            else "real_target_free_metadata_selection_no_payload_or_scientific_result"
        ),
        "route": GENERATED_ROUTE if generated else SUCCESS_ROUTE,
        "green_evidence": _green_evidence(evidence, implementation_registry_sha256),
        "source_summary": {
            "Freewill_provider": "generated_fixture" if generated else "Figshare",
            "Freewill_record_id": 28_632_599,
            "Freewill_version": 1,
            "Freewill_inventory_rows": selector.EXPECTED_FREEWILL_ROWS,
            "Wrist_provider": "generated_fixture" if generated else "Figshare",
            "Wrist_record_id": WRIST_RECORD_ID,
            "Wrist_version": WRIST_VERSION,
            "Wrist_DOI": WRIST_DOI,
            "Wrist_file_rows": WRIST_EXPECTED_ROWS,
            "Wrist_participant_archives": WRIST_EXPECTED_PARTICIPANTS,
            "Wrist_supplementary_rows": WRIST_EXPECTED_SUPPLEMENTARY,
            "Wrist_declared_record_bytes": WRIST_EXPECTED_BYTES,
            "payload_opened": False,
        },
        "cohort_summary": dict(selection.cohort_summary),
        "split_summary": dict(selection.split_summary),
        "byte_summary": dict(selection.byte_summary),
        "selection_hashes": dict(selection.selection_hashes),
        "transport_summary": dict(transport_summary),
        "measurements": {
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "selected_private_rows": 300,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "machine_gate": dict(machine),
        },
        "mutation_summary": {
            "required_count": len(REQUIRED_MUTATIONS),
            "passed_count": len(mutation_routes),
            "mutation_names": list(REQUIRED_MUTATIONS),
            "route_counts": dict(sorted(Counter(mutation_routes.values()).items())),
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "green_decision_identity": True,
            "green_wrapper_identity_or_generated_only_state": True,
            "preconsumption_machine_gate": True,
            "exact_Freewill_private_schema_or_generated_equivalent": True,
            "exact_Wrist_public_schema_or_generated_equivalent": True,
            "frozen_participant_name_rule_and_sub01_anchor": True,
            "exact_12_subjects_per_axis": True,
            "exact_72_Freewill_bundles_288_members_and_12_Wrist_archives": True,
            "exact_fit_and_heldout_split_binding": True,
            "target_quality_and_outcome_free_selection": True,
            "source_and_joint_payload_caps": True,
            "deterministic_replay": True,
            "private_and_public_output_separation": True,
            "resource_and_output_caps": True,
            "all_forbidden_payload_neural_model_score_and_claim_counters_zero": True,
        },
        "warnings": [
            (
                "All source rows and HTTP responses were generated locally."
                if generated
                else "Only source metadata were read; no archive member or payload was opened."
            ),
            "Selected payload byte totals are declarations and do not verify payload integrity.",
            "No signal channel geometry event target quality model prediction or score was accessed.",
            "Participant selection cannot establish a neural effect or language decoding.",
            "End-to-end neural decoding latency was not measured.",
        ],
        "unavailable_fields": [
            "selected payload integrity",
            "channel geometry signal quality event target and movement onset",
            "control-adjusted neural effect",
            "model prediction score and latency",
            "language decoding and thought-to-text evidence",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A proof-gated target-free selector can bind a storage-capped real two-axis "
                "pilot from bounded source metadata without opening a neural payload."
            ),
            "scientific_claim_not_established": (
                "Metadata selection contains no neural signal model prediction or score and "
                "establishes no neural effect language decoding or thought-to-text capability."
            ),
        },
    }


def _build_failure_report(
    refusal: LivePilotRefusal,
    *,
    stage: str,
    evidence: GreenWrapperEvidence,
    implementation_registry_sha256: str,
    machine: Mapping[str, Any],
    counters: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
    marker_bytes: int,
    transport_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_failed_real_metadata_pilot_selection",
        "proof_posture": "aggregate_failure_after_private_consumed_marker",
        "route": refusal.route,
        "green_evidence": _green_evidence(evidence, implementation_registry_sha256),
        "source_summary": {
            "Freewill_provider": "Figshare",
            "Freewill_record_id": 28_632_599,
            "Wrist_provider": "Figshare",
            "Wrist_record_id": WRIST_RECORD_ID,
            "payload_opened": False,
            "selection_completed": False,
            "failure_stage": stage,
        },
        "cohort_summary": {"selection_available": False},
        "split_summary": {"selection_available": False},
        "byte_summary": {"payload_bytes_opened": 0},
        "selection_hashes": {"selection_available": False},
        "transport_summary": dict(transport_summary),
        "measurements": {
            "input_bytes": counters.get("private_Freewill_manifest_bytes", 0)
            + counters.get("public_Wrist_metadata_body_bytes", 0),
            "output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "selected_private_rows": 0,
            "incremental_disk_bytes": marker_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "machine_gate": dict(machine),
        },
        "mutation_summary": {
            "required_count": len(REQUIRED_MUTATIONS),
            "passed_count": 0,
            "mutation_names": [],
            "route_counts": {},
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "green_decision_identity": True,
            "green_wrapper_identity": True,
            "preconsumption_machine_gate": True,
            "real_metadata_selection_completed": False,
            "no_retry_or_rerun_available": True,
            "zero_payload_signal_target_model_score_and_claim_operations": all(
                counters.get(key, 0) == 0
                for key in (
                    "local_header_requests",
                    "member_or_archive_payload_requests",
                    "signal_sample_reads",
                    "target_label_response_sentence_key_or_trial_reads",
                    "model_inference_runs",
                    "scoring_events",
                    "scientific_claim_upgrades",
                )
            ),
        },
        "warnings": [
            "The one registered metadata invocation is consumed and cannot be retried or rerun.",
            "The aggregate route reports a failure class without publishing private rows or raw bodies.",
            "No archive payload signal target model prediction or score was accessed.",
        ],
        "unavailable_fields": [
            "completed real pilot selection",
            "selected payload integrity",
            "neural signal target model prediction and score",
            "language decoding and thought-to-text evidence",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "The one-shot selector failed closed and retained an aggregate consumed result."
            ),
            "scientific_claim_not_established": (
                "A metadata selection failure establishes no neural effect language decoding "
                "or thought-to-text capability."
            ),
        },
    }


def validate_public_report(report: Mapping[str, Any]) -> None:
    """Validate one generated, real, or consumed aggregate-only result."""

    if set(report) != PUBLIC_REPORT_FIELDS:
        raise LivePilotRefusal(FAILURE_ROUTES[5], "public report fields differ")
    if (
        report.get("schema_name") != RESULT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") not in {GENERATED_ROUTE, SUCCESS_ROUTE, *FAILURE_ROUTES}
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "public report identity differs")
    _walk_public(report)
    counters = report.get("access_counters")
    if not isinstance(counters, dict):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "public counters differ")
    for key in (
        "local_header_requests",
        "member_or_archive_payload_requests",
        "member_or_archive_payload_bytes",
        "signal_sample_reads",
        "target_label_response_sentence_key_or_trial_reads",
        "model_inference_runs",
        "scoring_events",
        "scientific_claim_upgrades",
        "operations_on_other_projects",
    ):
        if counters.get(key) != 0:
            raise LivePilotRefusal(FAILURE_ROUTES[5], "forbidden public counter is nonzero")
    if report.get("route") == GENERATED_ROUTE and any(counters.values()):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "generated report used real access")
    if report.get("route") == SUCCESS_ROUTE:
        if (
            counters.get("private_Freewill_manifest_content_opens") != 1
            or counters.get("private_Freewill_manifest_body_reads") != 1
            or counters.get("private_Freewill_manifest_bytes") != FREEWILL_PRIVATE_BYTES
            or counters.get("public_Wrist_metadata_body_reads") != 1
            or counters.get("real_participant_selections") != 24
            or counters.get("real_member_or_archive_selections") != 300
            or not all(report.get("acceptance_gates", {}).values())
        ):
            raise LivePilotRefusal(FAILURE_ROUTES[5], "real success counter differs")


def _serialize_outputs(
    report: dict[str, Any],
    private_manifest: Mapping[str, Any] | None,
    *,
    marker_bytes: int,
) -> tuple[bytes, bytes | None, int, int]:
    private_bytes = (
        None if private_manifest is None else _canonical_json_bytes(private_manifest)
    )
    report["measurements"]["output_bytes"] = 0
    report["measurements"]["incremental_disk_bytes"] = marker_bytes + (
        0 if private_bytes is None else len(private_bytes)
    )
    report_bytes = _canonical_json_bytes(report)
    for _ in range(4):
        combined = len(report_bytes) + (0 if private_bytes is None else len(private_bytes))
        incremental = combined + marker_bytes
        report["measurements"]["output_bytes"] = combined
        report["measurements"]["incremental_disk_bytes"] = incremental
        updated = _canonical_json_bytes(report)
        if updated == report_bytes:
            break
        report_bytes = updated
    combined = len(report_bytes) + (0 if private_bytes is None else len(private_bytes))
    incremental = combined + marker_bytes
    if (
        len(report_bytes) > MAX_PUBLIC_OUTPUT_BYTES
        or combined > MAX_COMBINED_OUTPUT_BYTES
        or incremental > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "output cap failed")
    validate_public_report(report)
    return report_bytes, private_bytes, combined, incremental


def _write_exclusive(path: Path, payload: bytes, *, mode: int) -> None:
    if path.exists() or path.is_symlink():
        raise LivePilotRefusal(FAILURE_ROUTES[5], "output already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise LivePilotRefusal(FAILURE_ROUTES[5], "output parent is unavailable")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            offset = 0
            while offset < len(payload):
                offset += os.write(descriptor, payload[offset:])
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[5], "exclusive output write failed") from exc


def _make_exclusive_directory(path: Path, *, route: str = FAILURE_ROUTES[5]) -> None:
    if path.exists() or path.is_symlink():
        raise LivePilotRefusal(route, "output directory already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise LivePilotRefusal(route, "output parent is unavailable")
    try:
        os.mkdir(path, 0o700)
    except OSError as exc:
        raise LivePilotRefusal(route, "output directory creation failed") from exc


def _ensure_private_parent(root: Path) -> Path:
    codex_work = root / ".codex_work"
    if not codex_work.is_dir() or codex_work.is_symlink():
        raise LivePilotRefusal(FAILURE_ROUTES[6], "workspace private root is unavailable")
    parent = root / PRIVATE_PARENT_RELATIVE_PATH
    if parent.exists() or parent.is_symlink():
        if not parent.is_dir() or parent.is_symlink():
            raise LivePilotRefusal(FAILURE_ROUTES[6], "private selector parent differs")
    else:
        try:
            os.mkdir(parent, 0o700)
        except OSError as exc:
            raise LivePilotRefusal(FAILURE_ROUTES[6], "private selector parent creation failed") from exc
    return parent


def _write_consumed_marker(
    private_root: Path,
    evidence: GreenWrapperEvidence,
) -> tuple[Path, int]:
    marker = {
        "schema_name": "neurodecodekit.marc1_pilot_selection_live_execution_consumed",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "implementation_commit": evidence.implementation_commit,
        "implementation_registry_sha256": evidence.implementation_registry_sha256,
        "registered_execution_ordinal": 1,
        "retry_allowed": False,
        "rerun_allowed": False,
        "payload_access_allowed": False,
        "signal_target_model_or_score_access_allowed": False,
    }
    payload = _canonical_json_bytes(marker)
    path = private_root / CONSUMED_MARKER_NAME
    _write_exclusive(path, payload, mode=0o600)
    return path, len(payload)


def _enforce_resources(runtime_seconds: float, peak_rss_bytes: int) -> None:
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[6], "runtime or RSS cap failed")


def qualify_generated_mock_selector(
    output_dir: str | Path,
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> PilotOutcome:
    """Qualify the exact reader, transport, selector, privacy, and output path."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    output = Path(output_dir)
    load_green_decision(root)
    machine = preconsumption_machine_gate(
        output.parent,
        environ=os.environ if environ is None else environ,
        disk_usage_reader=disk_usage_reader,
        cpu_count_reader=cpu_count_reader,
        loadavg_reader=loadavg_reader,
        rss_reader=rss_reader,
    )
    _make_exclusive_directory(output)
    started = clock()
    contract = selector.load_registered_contract(root)
    first_freewill = build_generated_real_freewill_manifest(contract=contract)
    replay_freewill = build_generated_real_freewill_manifest(
        reverse_rows=True,
        contract=contract,
    )
    first_wrist_payload = build_generated_wrist_response()
    replay_wrist_payload = build_generated_wrist_response(reverse_rows=True)

    direct_opener, direct_resolver = generated_http_fixture(first_wrist_payload, redirects=0)
    direct_payload, direct_transport = fetch_wrist_metadata(
        direct_opener,
        resolver=direct_resolver,
        counters=None,
    )
    direct_opener.assert_consumed()
    redirect_opener, redirect_resolver = generated_http_fixture(
        replay_wrist_payload,
        redirects=2,
    )
    redirect_payload, _ = fetch_wrist_metadata(
        redirect_opener,
        resolver=redirect_resolver,
        counters=None,
    )
    redirect_opener.assert_consumed()
    first_wrist = parse_wrist_metadata(direct_payload, counters=None)
    replay_wrist = parse_wrist_metadata(redirect_payload, counters=None)
    first = _select_real_metadata(
        first_freewill,
        first_wrist,
        contract=contract,
        generated=True,
    )
    replay = _select_real_metadata(
        replay_freewill,
        replay_wrist,
        contract=contract,
        generated=True,
    )
    if (
        _canonical_json_bytes(first.private_manifest)
        != _canonical_json_bytes(replay.private_manifest)
        or first.selection_hashes != replay.selection_hashes
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "generated replay differs")
    mutations = run_required_mutations(
        first_freewill,
        first_wrist_payload,
        contract=contract,
    )
    runtime = clock() - started
    peak_rss = int(rss_reader())
    _enforce_resources(runtime, peak_rss)
    generated_input_bytes = sum(
        (
            len(_canonical_json_bytes(first_freewill)),
            len(_canonical_json_bytes(replay_freewill)),
            len(first_wrist_payload),
            len(replay_wrist_payload),
        )
    )
    counters = _base_access_counters()
    report = _build_success_report(
        first,
        generated=True,
        evidence=None,
        implementation_registry_sha256=None,
        machine=machine,
        transport_summary=direct_transport,
        counters=counters,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        input_bytes=generated_input_bytes,
        output_bytes=0,
        mutation_routes=mutations,
    )
    report_bytes, private_bytes, combined, _ = _serialize_outputs(
        report,
        first.private_manifest,
        marker_bytes=0,
    )
    if private_bytes is None:
        raise AssertionError("generated private manifest is unavailable")
    private_path = output / "marc1_pilot_selection.generated.private.v0.json"
    report_path = output / "marc1_pilot_selection_live_qualification.v0.json"
    _write_exclusive(private_path, private_bytes, mode=0o600)
    _write_exclusive(report_path, report_bytes, mode=0o644)
    return PilotOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=private_path,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        combined_output_bytes=combined,
    )


def _write_consumed_failure_report(
    path: Path,
    *,
    refusal: LivePilotRefusal,
    stage: str,
    evidence: GreenWrapperEvidence,
    implementation_registry_sha256: str,
    machine: Mapping[str, Any],
    counters: Mapping[str, int],
    started: float,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    marker_bytes: int,
    transport_summary: Mapping[str, Any],
) -> None:
    failure_counters = dict(counters)
    failure_counters["public_aggregate_reports"] = 1
    report = _build_failure_report(
        refusal,
        stage=stage,
        evidence=evidence,
        implementation_registry_sha256=implementation_registry_sha256,
        machine=machine,
        counters=failure_counters,
        runtime_seconds=clock() - started,
        peak_rss_bytes=int(rss_reader()),
        marker_bytes=marker_bytes,
        transport_summary=transport_summary,
    )
    report_bytes, _, _, _ = _serialize_outputs(report, None, marker_bytes=marker_bytes)
    _write_exclusive(path, report_bytes, mode=0o644)


def execute_registered_metadata_selection(
    repo_root: str | Path,
    *,
    evidence: GreenWrapperEvidence,
    environ: Mapping[str, str] | None = None,
    opener: Callable[[urllib.request.Request, float], BinaryIO] = _open_live_once,
    resolver: Callable[[str], Sequence[str]] = _resolve_global_addresses,
    proof_verifier: Callable[[str | Path, GreenWrapperEvidence], Mapping[str, Any]] = (
        verify_green_wrapper_evidence
    ),
    private_reader: Callable[..., tuple[dict[str, Any], bytes]] = (
        read_locked_freewill_manifest
    ),
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> PilotOutcome:
    """Consume the one registered private/public target-free metadata selection."""

    root = Path(repo_root)
    implementation = proof_verifier(root, evidence)
    if implementation.get("execution_state", {}).get("real_metadata_execution_consumed") is not False:
        raise LivePilotRefusal(FAILURE_ROUTES[0], "implementation is not pre-execution")
    machine = preconsumption_machine_gate(
        root,
        environ=os.environ if environ is None else environ,
        disk_usage_reader=disk_usage_reader,
        cpu_count_reader=cpu_count_reader,
        loadavg_reader=loadavg_reader,
        rss_reader=rss_reader,
    )
    private_root = root / PRIVATE_ROOT_RELATIVE_PATH
    public_result_path = root / PUBLIC_RESULT_RELATIVE_PATH
    if (
        private_root.exists()
        or private_root.is_symlink()
        or public_result_path.exists()
        or public_result_path.is_symlink()
    ):
        raise LivePilotRefusal(FAILURE_ROUTES[6], "registered execution is already consumed")
    _ensure_private_parent(root)
    _make_exclusive_directory(private_root, route=FAILURE_ROUTES[6])
    marker_path, marker_bytes = _write_consumed_marker(private_root, evidence)
    if not marker_path.is_file():
        raise LivePilotRefusal(FAILURE_ROUTES[6], "consumed marker was not created")
    counters = _base_access_counters()
    counters["private_consumed_markers"] = 1
    started = clock()
    stage = "private_Freewill_manifest"
    transport_summary: dict[str, Any] = {
        "HTTP_request_attempts": 0,
        "network_redirects": 0,
        "accepted_response_bodies": 0,
        "accepted_response_body_bytes": 0,
        "raw_headers_published": False,
        "raw_body_persisted": False,
        "terminal_URL_published": False,
    }
    try:
        freewill_manifest, freewill_payload = private_reader(
            root / FREEWILL_PRIVATE_RELATIVE_PATH,
            expected_bytes=FREEWILL_PRIVATE_BYTES,
            expected_sha256=FREEWILL_PRIVATE_SHA256,
            counters=counters,
        )
        stage = "public_Wrist_metadata_transport"
        wrist_payload, transport_summary = fetch_wrist_metadata(
            opener,
            resolver=resolver,
            counters=counters,
        )
        stage = "target_free_metadata_parse_and_selection"
        wrist = parse_wrist_metadata(wrist_payload, counters=counters)
        contract = selector.load_registered_contract(root)
        selection = _select_real_metadata(
            freewill_manifest,
            wrist,
            contract=contract,
            generated=False,
        )
        counters["real_participant_selections"] = 24
        counters["real_member_or_archive_selections"] = 300
        runtime = clock() - started
        peak_rss = int(rss_reader())
        _enforce_resources(runtime, peak_rss)
        counters["private_selection_manifests"] = 1
        counters["public_aggregate_reports"] = 1
        report = _build_success_report(
            selection,
            generated=False,
            evidence=evidence,
            implementation_registry_sha256=evidence.implementation_registry_sha256,
            machine=machine,
            transport_summary=transport_summary,
            counters=counters,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            input_bytes=len(freewill_payload) + len(wrist_payload),
            output_bytes=0,
            mutation_routes=implementation["generated_qualification"]["mutation_routes"],
        )
        report_bytes, private_bytes, combined, _ = _serialize_outputs(
            report,
            selection.private_manifest,
            marker_bytes=marker_bytes,
        )
        if private_bytes is None:
            raise AssertionError("real private selection is unavailable")
        private_path = private_root / PRIVATE_SELECTION_NAME
        _write_exclusive(private_path, private_bytes, mode=0o600)
        _write_exclusive(public_result_path, report_bytes, mode=0o644)
        return PilotOutcome(
            report=report,
            report_path=public_result_path,
            private_manifest_path=private_path,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            combined_output_bytes=combined,
        )
    except LivePilotRefusal as refusal:
        if not public_result_path.exists() and not public_result_path.is_symlink():
            _write_consumed_failure_report(
                public_result_path,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                implementation_registry_sha256=evidence.implementation_registry_sha256,
                machine=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_reader=rss_reader,
                marker_bytes=marker_bytes,
                transport_summary=transport_summary,
            )
        raise
    except Exception as exc:
        refusal = LivePilotRefusal(
            FAILURE_ROUTES[6],
            "unexpected post-consumption implementation failure",
        )
        if not public_result_path.exists() and not public_result_path.is_symlink():
            _write_consumed_failure_report(
                public_result_path,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                implementation_registry_sha256=evidence.implementation_registry_sha256,
                machine=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_reader=rss_reader,
                marker_bytes=marker_bytes,
                transport_summary=transport_summary,
            )
        raise refusal from exc


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    """Inspect only an aggregate generated or consumed result."""

    report_path = Path(path)
    if "private" in report_path.name.lower():
        raise LivePilotRefusal(FAILURE_ROUTES[5], "private manifest inspection is forbidden")
    try:
        observed = os.lstat(report_path)
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
            raise OSError("not a regular file")
        if observed.st_size > MAX_PUBLIC_OUTPUT_BYTES:
            raise LivePilotRefusal(FAILURE_ROUTES[5], "aggregate result exceeds cap")
        payload = report_path.read_bytes()
        report = _strict_json_value(payload)
    except LivePilotRefusal:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LivePilotRefusal(FAILURE_ROUTES[5], "aggregate result is unavailable") from exc
    if not isinstance(report, dict):
        raise LivePilotRefusal(FAILURE_ROUTES[5], "aggregate result root differs")
    validate_public_report(report)
    return report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the fixed zero-access plan and closed payload boundary."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(root)
    return {
        "lane_id": LANE_ID,
        "Freewill_private_manifest_bytes": FREEWILL_PRIVATE_BYTES,
        "Freewill_private_manifest_content_opens": 1,
        "Wrist_record_id": WRIST_RECORD_ID,
        "Wrist_version": WRIST_VERSION,
        "Wrist_metadata_body_cap_bytes": MAX_NETWORK_BODY_BYTES,
        "Wrist_expected_file_rows": WRIST_EXPECTED_ROWS,
        "selected_subjects_per_axis": 12,
        "selected_private_rows": 300,
        "HTTP_request_attempt_cap": MAX_HTTP_ATTEMPTS,
        "bodyless_redirect_cap": MAX_REDIRECTS,
        "public_or_private_inputs_accessed": 0,
        "payload_requests": 0,
        "signal_target_model_or_score_operations": 0,
        "execution_requires_exact_green_wrapper_evidence": True,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_pilot_selection_live",
        description="Proof-gated MARC1-P1A real-metadata pilot selector.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the zero-access registered plan.")
    qualify = subparsers.add_parser("qualify", help="Run generated/mock qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate result.")
    inspect.add_argument("report")
    execute = subparsers.add_parser("execute", help="Consume the one real metadata selection.")
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
            outcome = qualify_generated_mock_selector(args.output_dir)
        elif args.command == "inspect":
            report = inspect_public_result(args.report)
            print(_canonical_json_bytes(report).decode("ascii"), end="")
            return 0
        else:
            evidence = GreenWrapperEvidence(
                implementation_commit=args.implementation_commit,
                implementation_ci_run_id=args.implementation_ci_run_id,
                implementation_base_job_id=args.implementation_base_job_id,
                implementation_optional_job_id=args.implementation_optional_job_id,
                implementation_registry_sha256=args.implementation_registry_sha256,
            )
            outcome = execute_registered_metadata_selection(_repo_root(), evidence=evidence)
        print(
            _canonical_json_bytes(
                {
                    "status": outcome.report["status"],
                    "route": outcome.report["route"],
                    "report": str(outcome.report_path),
                    "combined_output_bytes": outcome.combined_output_bytes,
                    "runtime_seconds": outcome.runtime_seconds,
                    "peak_RSS_bytes": outcome.peak_rss_bytes,
                }
            ).decode("ascii"),
            end="",
        )
        return 0
    except LivePilotRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
