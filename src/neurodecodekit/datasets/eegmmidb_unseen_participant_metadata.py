"""Body-blind Stage M metadata identity client for EEGMMIDB-UG1.

The public qualification surface is generated/mock only. The standard-library
live transport is present for the later proof-gated Stage M2 wrapper, but this
module exposes no command that can invoke it before that barrier is green.
"""

from __future__ import annotations

import copy
import email.utils
import hashlib
import io
import json
import os
import re
import resource
import shutil
import ssl
import stat
import time
import urllib.request
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping, Sequence
from urllib.parse import urlsplit

from neurodecodekit.datasets import eegmmidb_unseen_participant_acquisition as acquisition


SCHEMA_VERSION = "0.1.0"
LANE_ID = "EEGMMIDB-UG1-M"
GENERATED_ROUTE = "EEGMMIDBUG1M-G1"
DECISION_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_metadata_authorization_decision.v0.json"
)
DECISION_SHA256 = "9c1c9d214cc9b08845354f48c7e46002899815f773d9ed2a881f676efb1ebc65"
GREEN_DECISION_COMMIT = "021bf8a1f2f12a8e7388a561535328cd0dc0dba2"
GREEN_DECISION_CI_RUN_ID = 32_712_235_191
GREEN_DECISION_BASE_JOB_ID = 97_385_926_125
GREEN_DECISION_OPTIONAL_JOB_ID = 97_385_926_444
MAX_REQUESTS = 36
MAX_DECLARED_BYTES = 268_435_456
MAX_METADATA_BYTES = 2_097_152
MAX_OUTPUT_BYTES = 1_048_576
MAX_WALL_SECONDS = 300.0
MAX_PEAK_RSS_BYTES = 268_435_456
MINIMUM_FREE_DISK_BYTES = 2_147_483_648
REQUEST_TIMEOUT_SECONDS = 8.0
THREAD_ENV_KEYS = acquisition.THREAD_ENV_KEYS
DECIMAL_RE = re.compile(r"(?:0|[1-9][0-9]*)\Z")
ETAG_RE = re.compile(r'(?:W/)?"[\x21\x23-\x7e]*"\Z')
FORBIDDEN_OUTPUT_COMPONENTS = frozenset({".codex_work", "data"})
TARGET_LIKE_KEYS = frozenset(
    {"answer", "class", "condition", "event", "label", "response", "sentence", "target"}
)
QUALIFICATION_CASES = (
    "complete_validators",
    "optional_validators_unavailable",
    "deterministic_replay",
    "redirect",
    "status",
    "missing_content_length",
    "duplicate_content_length",
    "malformed_content_length",
    "malformed_etag",
    "malformed_last_modified",
    "malformed_accept_ranges",
    "observed_body_byte",
    "request_order",
    "missing_response",
    "declared_byte_cap",
    "output_collision",
    "thread_environment",
    "free_disk",
    "peak_rss",
    "wall_time",
)


class UG1MetadataRefusal(RuntimeError):
    """Refuse before a complete canonical metadata inventory exists."""


@dataclass(frozen=True)
class MetadataFact:
    repository_path: str
    partition: str
    participant: str
    run: str
    url: str
    size_bytes: int
    etag: str | None
    last_modified: str | None
    accept_ranges: str | None


@dataclass(frozen=True)
class MetadataCaps:
    requests: int = MAX_REQUESTS
    declared_bytes: int = MAX_DECLARED_BYTES
    metadata_bytes: int = MAX_METADATA_BYTES
    output_bytes: int = MAX_OUTPUT_BYTES
    wall_seconds: float = MAX_WALL_SECONDS
    peak_rss_bytes: int = MAX_PEAK_RSS_BYTES
    minimum_free_disk_bytes: int = MINIMUM_FREE_DISK_BYTES


@dataclass(frozen=True)
class MetadataOutcome:
    inventory: Mapping[str, Any]
    inventory_bytes: bytes
    receipt_bytes: bytes
    output_root: Path | None
    measurements: Mapping[str, Any]


class FixtureHeadResponse(io.BytesIO):
    """urllib-shaped response that records forbidden body reads."""

    def __init__(
        self,
        *,
        url: str,
        status: int = 200,
        headers: Sequence[tuple[str, str]] = (),
        observed_body_bytes: int = 0,
    ) -> None:
        super().__init__(b"x" * observed_body_bytes)
        self.status = status
        self.code = status
        self._url = url
        self.headers = Message()
        for key, value in headers:
            self.headers.add_header(key, value)
        self.observed_body_bytes = observed_body_bytes
        self.read_calls = 0

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status

    def read(self, size: int = -1) -> bytes:  # type: ignore[override]
        self.read_calls += 1
        return super().read(size)


@dataclass(frozen=True)
class FixtureExchange:
    url: str
    response: FixtureHeadResponse


class FixtureHeadOpener:
    """Strict sequential opener with no network capability."""

    def __init__(self, exchanges: Sequence[FixtureExchange]) -> None:
        self._exchanges = list(exchanges)
        self.calls: list[dict[str, Any]] = []

    def __call__(self, request: urllib.request.Request, timeout: float) -> BinaryIO:
        if not self._exchanges:
            raise UG1MetadataRefusal("unexpected metadata request")
        expected = self._exchanges.pop(0)
        observed = {
            "url": request.full_url,
            "method": request.get_method(),
            "timeout": timeout,
            "data": request.data,
            "headers": {key.lower(): value for key, value in request.header_items()},
        }
        self.calls.append(observed)
        if expected.url != request.full_url:
            raise UG1MetadataRefusal("metadata request order or URL differs")
        if (
            observed["method"] != "HEAD"
            or observed["data"] is not None
            or observed["timeout"] != REQUEST_TIMEOUT_SECONDS
            or observed["headers"]
            != {
                "accept": "*/*",
                "accept-encoding": "identity",
                "user-agent": "NeuroDecodeKit-EEGMMIDBUG1M/0.1",
            }
        ):
            raise UG1MetadataRefusal("metadata request semantics differ")
        return expected.response

    def assert_consumed(self) -> None:
        if self._exchanges:
            raise UG1MetadataRefusal("metadata response count is incomplete")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


class StandardLibraryHeadOpener:
    """TLS-verified, no-redirect standard-library opener for later Stage M2."""

    def __init__(self) -> None:
        context = ssl.create_default_context()
        self._opener = urllib.request.build_opener(
            _NoRedirect(),
            urllib.request.HTTPSHandler(context=context),
        )

    def __call__(self, request: urllib.request.Request, timeout: float) -> BinaryIO:
        return self._opener.open(request, timeout=timeout)


HeadOpener = Callable[[urllib.request.Request, float], BinaryIO]


def _canonical_json(value: Any) -> bytes:
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


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _peak_process_tree_rss_bytes() -> int:
    own = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    children = int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    multiplier = 1 if os.uname().sysname == "Darwin" else 1024
    return (own + children) * multiplier


def _read_locked_decision(repo_root: Path) -> dict[str, Any]:
    path = repo_root / DECISION_RELATIVE_PATH
    try:
        before = os.lstat(path)
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
            raise OSError("decision type differs")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            payload = os.read(descriptor, 128 * 1024)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise UG1MetadataRefusal("green Stage M decision is unavailable") from exc
    if len(payload) != before.st_size or _sha256(payload) != DECISION_SHA256:
        raise UG1MetadataRefusal("green Stage M decision identity differs")
    try:
        decision = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UG1MetadataRefusal("green Stage M decision JSON differs") from exc
    authorization = decision.get("authorization", {})
    if (
        decision.get("lane_id") != LANE_ID
        or decision.get("green_proof_closeout", {}).get("both_required_jobs_green") is not True
        or authorization.get(
            "stage_M1_generated_metadata_client_implementation_after_decision_green"
        )
        is not True
        or authorization.get("network_or_metadata_request_authorized_now") is not False
        or authorization.get("payload_download_or_acquisition_authorized_now") is not False
    ):
        raise UG1MetadataRefusal("green Stage M decision scope differs")
    return decision


def registered_metadata_plan(repo_root: str | Path) -> dict[str, Any]:
    """Return the exact Stage M plan without a transport or output operation."""

    _read_locked_decision(Path(repo_root))
    return {
        "schema_name": "neurodecodekit.eegmmidb_ug1_metadata_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "mode": "dry_run_no_network_no_URL_open_no_local_data_path",
        "files": [
            {
                "repository_path": row.repository_path,
                "partition": row.partition,
                "participant": row.participant,
                "run": row.run,
                "url": row.url,
            }
            for row in acquisition.EXPECTED_FILES
        ],
        "file_count": MAX_REQUESTS,
        "method": "HEAD",
        "redirects": 0,
        "retries": 0,
        "response_body_bytes": 0,
        "operation_counters": _zero_operation_counters(),
        "warnings": [
            "plan_only",
            "metadata_sizes_and_optional_validators_unavailable",
            "stage_M2_requires_a_separate_green_implementation_proof_barrier",
            "metadata_identity_is_not_neural_or_decoding_evidence",
        ],
    }


def _zero_operation_counters() -> dict[str, int]:
    return {
        "mock_HEAD_requests": 0,
        "real_HEAD_requests": 0,
        "redirects": 0,
        "retries": 0,
        "response_body_reads": 0,
        "response_body_bytes": 0,
        "local_real_data_path_operations": 0,
        "EDF_header_annotation_event_or_signal_reads": 0,
        "payload_download_bytes": 0,
        "target_or_label_reads": 0,
        "parameter_update_fits": 0,
        "model_inference_runs": 0,
        "scoring_events": 0,
        "scientific_claim_upgrades": 0,
    }


def _request(url: str) -> urllib.request.Request:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "physionet.org"
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith("/files/eegmmidb/1.0.0/")
    ):
        raise UG1MetadataRefusal("metadata URL differs from the frozen HTTPS allowlist")
    return urllib.request.Request(
        url,
        method="HEAD",
        headers={
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "User-Agent": "NeuroDecodeKit-EEGMMIDBUG1M/0.1",
        },
    )


def _single_header(headers: Message, name: str, *, required: bool) -> str | None:
    values = headers.get_all(name, failobj=[])
    if len(values) > 1 or (required and len(values) != 1):
        raise UG1MetadataRefusal(f"{name} header count differs")
    if not values:
        return None
    value = values[0]
    if not isinstance(value, str) or value != value.strip() or "\r" in value or "\n" in value:
        raise UG1MetadataRefusal(f"{name} header syntax differs")
    return value


def _content_length(headers: Message) -> int:
    value = _single_header(headers, "Content-Length", required=True)
    if value is None or DECIMAL_RE.fullmatch(value) is None:
        raise UG1MetadataRefusal("Content-Length must be one canonical decimal")
    result = int(value)
    if result > MAX_DECLARED_BYTES:
        raise UG1MetadataRefusal("declared payload bytes exceed the frozen cap")
    return result


def _optional_validators(headers: Message) -> tuple[str | None, str | None, str | None]:
    etag = _single_header(headers, "ETag", required=False)
    if etag is not None and (len(etag) > 256 or ETAG_RE.fullmatch(etag) is None):
        raise UG1MetadataRefusal("ETag syntax differs")
    modified = _single_header(headers, "Last-Modified", required=False)
    if modified is not None:
        try:
            parsed = email.utils.parsedate_to_datetime(modified)
        except (TypeError, ValueError) as exc:
            raise UG1MetadataRefusal("Last-Modified syntax differs") from exc
        if parsed.tzinfo is None or email.utils.format_datetime(parsed, usegmt=True) != modified:
            raise UG1MetadataRefusal("Last-Modified syntax differs")
    ranges = _single_header(headers, "Accept-Ranges", required=False)
    if ranges is not None:
        normalized = ranges.lower()
        if normalized not in {"bytes", "none"}:
            raise UG1MetadataRefusal("Accept-Ranges syntax differs")
        ranges = normalized
    return etag, modified, ranges


def _fetch_fact(
    planned: acquisition.PlannedFile,
    opener: HeadOpener,
    *,
    generated: bool,
    counters: dict[str, int],
) -> MetadataFact:
    request = _request(planned.url)
    counters["mock_HEAD_requests" if generated else "real_HEAD_requests"] += 1
    response = opener(request, REQUEST_TIMEOUT_SECONDS)
    try:
        final_url = response.geturl()
        status = response.getcode()
        headers = response.headers
        observed_body_bytes = int(getattr(response, "observed_body_bytes", 0))
        if final_url != planned.url:
            raise UG1MetadataRefusal("redirect or final URL change refused")
        if status != 200:
            raise UG1MetadataRefusal("metadata response status differs")
        if observed_body_bytes != 0:
            raise UG1MetadataRefusal("metadata response exposed body bytes")
        if not isinstance(headers, Message):
            raise UG1MetadataRefusal("metadata response headers differ")
        size = _content_length(headers)
        etag, modified, ranges = _optional_validators(headers)
        if int(getattr(response, "read_calls", 0)) != 0:
            raise UG1MetadataRefusal("response body read is forbidden")
    finally:
        response.close()
    return MetadataFact(
        repository_path=planned.repository_path,
        partition=planned.partition,
        participant=planned.participant,
        run=planned.run,
        url=planned.url,
        size_bytes=size,
        etag=etag,
        last_modified=modified,
        accept_ranges=ranges,
    )


def _fact_dict(fact: MetadataFact) -> dict[str, Any]:
    return {
        "repository_path": fact.repository_path,
        "partition": fact.partition,
        "participant": fact.participant,
        "run": fact.run,
        "url": fact.url,
        "size_bytes": fact.size_bytes,
        "etag": fact.etag,
        "last_modified": fact.last_modified,
        "accept_ranges": fact.accept_ranges,
    }


def _assert_target_free(value: Any, trail: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            lowered = str(key).lower()
            if lowered in TARGET_LIKE_KEYS:
                raise UG1MetadataRefusal(f"target-like public field refused: {'.'.join(trail + (lowered,))}")
            _assert_target_free(child, trail + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_target_free(child, trail + (str(index),))


def _receipt(inventory: Mapping[str, Any]) -> bytes:
    validators = inventory["validator_availability"]
    text = (
        "# EEGMMIDB-UG1 Stage M Metadata Receipt\n\n"
        f"- Files: {inventory['file_count']}\n"
        f"- Declared bytes: {inventory['declared_payload_bytes']}\n"
        f"- Method: {inventory['transport']['method']}\n"
        "- Redirects / retries / response-body bytes: 0 / 0 / 0\n"
        f"- ETag available: {validators['etag']}\n"
        f"- Last-Modified available: {validators['last_modified']}\n"
        f"- Accept-Ranges available: {validators['accept_ranges']}\n"
        "- EDF content opened: no\n"
        "- Scientific claim: none\n"
    )
    return text.encode("ascii")


def _assert_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(name) != "1" for name in THREAD_ENV_KEYS):
        raise UG1MetadataRefusal("one-thread environment is not exact")


def _safe_output_root(workspace_root: Path, output_relative: str) -> Path:
    relative = Path(output_relative)
    if (
        not output_relative
        or relative.is_absolute()
        or any(part in {"", ".", ".."} for part in relative.parts)
        or any(part in FORBIDDEN_OUTPUT_COMPONENTS for part in relative.parts)
    ):
        raise UG1MetadataRefusal("generated output path is unsafe")
    root = Path(os.path.abspath(workspace_root))
    observed = os.lstat(root)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise UG1MetadataRefusal("generated workspace root is unsafe")
    output = root / relative
    current = root
    for part in relative.parts[:-1]:
        current /= part
        try:
            state = os.lstat(current)
        except FileNotFoundError:
            os.mkdir(current, 0o700)
            continue
        if stat.S_ISLNK(state.st_mode) or not stat.S_ISDIR(state.st_mode):
            raise UG1MetadataRefusal("generated output crosses an unsafe path")
    if output.exists() or output.is_symlink():
        raise UG1MetadataRefusal("generated output already exists")
    return output


def _publish_output(root: Path, inventory: bytes, receipt: bytes) -> None:
    staging = root.with_name(f".{root.name}.tmp")
    if staging.exists() or staging.is_symlink():
        raise UG1MetadataRefusal("generated staging output already exists")
    os.mkdir(staging, 0o700)
    try:
        (staging / "inventory.v0.json").write_bytes(inventory)
        (staging / "receipt.md").write_bytes(receipt)
        acquisition._rename_noreplace(staging, root)
    except Exception:
        if staging.exists() and staging.is_dir() and not staging.is_symlink():
            shutil.rmtree(staging)
        raise


def run_metadata_pass(
    *,
    repo_root: str | Path,
    opener: HeadOpener,
    generated: bool,
    workspace_root: str | Path | None = None,
    output_relative: str | None = None,
    caps: MetadataCaps = MetadataCaps(),
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_process_tree_rss_bytes,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
) -> MetadataOutcome:
    """Run one exact metadata pass through an injected opener."""

    _read_locked_decision(Path(repo_root))
    environment = os.environ if environ is None else environ
    _assert_thread_environment(environment)
    if caps.requests != MAX_REQUESTS or caps.declared_bytes > MAX_DECLARED_BYTES:
        raise UG1MetadataRefusal("metadata request or declared-byte cap differs")
    output_root = None
    if (workspace_root is None) != (output_relative is None):
        raise UG1MetadataRefusal("workspace and output must be supplied together")
    if workspace_root is not None and output_relative is not None:
        output_root = _safe_output_root(Path(workspace_root), output_relative)
        if disk_usage_reader(Path(workspace_root)).free < caps.minimum_free_disk_bytes:
            raise UG1MetadataRefusal("free disk is below the frozen minimum")
    started = clock()
    counters = _zero_operation_counters()
    facts = [
        _fetch_fact(row, opener, generated=generated, counters=counters)
        for row in acquisition.EXPECTED_FILES
    ]
    if hasattr(opener, "assert_consumed"):
        opener.assert_consumed()  # type: ignore[attr-defined]
    if len(facts) != caps.requests:
        raise UG1MetadataRefusal("metadata fact count differs")
    declared = sum(fact.size_bytes for fact in facts)
    if declared > caps.declared_bytes:
        raise UG1MetadataRefusal("combined declared payload bytes exceed the frozen cap")
    validator_availability = {
        "etag": sum(fact.etag is not None for fact in facts),
        "last_modified": sum(fact.last_modified is not None for fact in facts),
        "accept_ranges": sum(fact.accept_ranges is not None for fact in facts),
    }
    unavailable = [
        name
        for name, count in validator_availability.items()
        if count != len(facts)
    ]
    runtime = clock() - started
    peak_rss = int(rss_reader())
    if runtime < 0 or runtime > caps.wall_seconds:
        raise UG1MetadataRefusal("metadata wall-time cap exceeded")
    if peak_rss < 0 or peak_rss > caps.peak_rss_bytes:
        raise UG1MetadataRefusal("metadata peak RSS cap exceeded")
    inventory: dict[str, Any] = {
        "schema_name": "neurodecodekit.eegmmidb_ug1_metadata_inventory",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "proof_posture": "generated_mock_only" if generated else "real_body_blind_metadata_only",
        "dataset": {
            "name": acquisition.DATASET_NAME,
            "version": acquisition.DATASET_VERSION,
            "doi": acquisition.DATASET_DOI,
        },
        "files": [_fact_dict(fact) for fact in facts],
        "file_count": len(facts),
        "source_file_count": 6,
        "fresh_file_count": 30,
        "declared_payload_bytes": declared,
        "validator_availability": validator_availability,
        "transport": {
            "method": "HEAD",
            "requests": len(facts),
            "redirects": 0,
            "retries": 0,
            "response_body_reads": 0,
            "response_body_bytes": 0,
        },
        "operation_counters": counters,
        "warnings": [
            "metadata_identity_only",
            "EDF_content_not_opened",
            "optional_validators_may_be_unavailable",
            "not_neural_or_decoding_evidence",
        ],
        "unavailable_fields": unavailable,
        "claim_boundary": {
            "scientific_claim_established": False,
            "real_EEG_accessed": False,
            "unseen_participant_generalization_established": False,
            "neural_or_decoding_advantage_established": False,
            "end_to_end_latency_measured": False,
        },
    }
    _assert_target_free(inventory)
    inventory_bytes = _canonical_json(inventory)
    receipt_bytes = _receipt(inventory)
    combined = len(inventory_bytes) + len(receipt_bytes)
    if len(inventory_bytes) > caps.metadata_bytes or combined > caps.output_bytes:
        raise UG1MetadataRefusal("metadata output exceeds the frozen cap")
    if output_root is not None:
        _publish_output(output_root, inventory_bytes, receipt_bytes)
    measurements = {
        "input_metadata_header_bytes": sum(
            len(str(value).encode("ascii"))
            for fact in facts
            for value in (fact.size_bytes, fact.etag, fact.last_modified, fact.accept_ranges)
            if value is not None
        ),
        "output_bytes": combined,
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": peak_rss,
        "mock_HEAD_requests": counters["mock_HEAD_requests"],
        "real_HEAD_requests": counters["real_HEAD_requests"],
        "response_body_reads": 0,
        "response_body_bytes": 0,
        "payload_download_bytes": 0,
        "local_real_data_path_operations": 0,
        "EDF_content_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "target_deliveries": 0,
        "scoring_events": 0,
        "producer_causal": None,
        "end_to_end_latency_measured": False,
    }
    return MetadataOutcome(
        inventory=inventory,
        inventory_bytes=inventory_bytes,
        receipt_bytes=receipt_bytes,
        output_root=output_root,
        measurements=measurements,
    )


def build_generated_exchanges(
    *,
    optional_validators: bool = True,
    declared_size: int = 1_000_000,
) -> tuple[FixtureExchange, ...]:
    """Build exact target-free HEAD response fixtures for all 36 paths."""

    rows = []
    for index, planned in enumerate(acquisition.EXPECTED_FILES):
        headers: list[tuple[str, str]] = [("Content-Length", str(declared_size + index))]
        if optional_validators:
            headers.extend(
                [
                    ("ETag", f'"ug1-generated-{index:02d}"'),
                    ("Last-Modified", "Mon, 24 Aug 2026 00:00:00 GMT"),
                    ("Accept-Ranges", "bytes"),
                ]
            )
        rows.append(
            FixtureExchange(
                url=planned.url,
                response=FixtureHeadResponse(url=planned.url, headers=headers),
            )
        )
    return tuple(rows)


def _mutated_exchanges(case: str) -> tuple[FixtureExchange, ...]:
    rows = list(build_generated_exchanges())
    first = rows[0]
    headers = list(first.response.headers.raw_items())
    if case == "redirect":
        response = FixtureHeadResponse(url=f"{first.url}?redirect", headers=headers)
    elif case == "status":
        response = FixtureHeadResponse(url=first.url, status=206, headers=headers)
    elif case == "missing_content_length":
        response = FixtureHeadResponse(url=first.url, headers=headers[1:])
    elif case == "duplicate_content_length":
        response = FixtureHeadResponse(
            url=first.url, headers=headers + [("Content-Length", "1000000")]
        )
    elif case == "malformed_content_length":
        response = FixtureHeadResponse(
            url=first.url,
            headers=[("Content-Length", "+1"), *headers[1:]],
        )
    elif case == "malformed_etag":
        response = FixtureHeadResponse(
            url=first.url,
            headers=[(key, "unquoted" if key.lower() == "etag" else value) for key, value in headers],
        )
    elif case == "malformed_last_modified":
        response = FixtureHeadResponse(
            url=first.url,
            headers=[
                (key, "yesterday" if key.lower() == "last-modified" else value)
                for key, value in headers
            ],
        )
    elif case == "malformed_accept_ranges":
        response = FixtureHeadResponse(
            url=first.url,
            headers=[
                (key, "bits" if key.lower() == "accept-ranges" else value)
                for key, value in headers
            ],
        )
    elif case == "observed_body_byte":
        response = FixtureHeadResponse(url=first.url, headers=headers, observed_body_bytes=1)
    elif case == "declared_byte_cap":
        response = FixtureHeadResponse(
            url=first.url,
            headers=[("Content-Length", str(MAX_DECLARED_BYTES)), *headers[1:]],
        )
    else:
        raise ValueError(f"unsupported mutation: {case}")
    rows[0] = FixtureExchange(first.url, response)
    return tuple(rows)


def run_generated_qualification(
    *,
    repo_root: str | Path,
    workspace_root: str | Path,
    environ: Mapping[str, str],
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_process_tree_rss_bytes,
) -> dict[str, Any]:
    """Run the sole bounded Stage M1 generated/mock qualification matrix."""

    started = clock()
    source = build_generated_exchanges()
    source_fingerprint = _sha256(
        _canonical_json(
            [
                {
                    "url": row.url,
                    "status": row.response.status,
                    "headers": list(row.response.headers.raw_items()),
                }
                for row in source
            ]
        )
    )
    passed: list[str] = []
    mock_requests = 0
    emitted_bytes = 0

    def execute(
        name: str,
        exchanges: Sequence[FixtureExchange],
        *,
        output: str | None = None,
        caps: MetadataCaps = MetadataCaps(),
        case_environ: Mapping[str, str] = environ,
        case_clock: Callable[[], float] = lambda: 10.0,
        case_rss: Callable[[], int] = lambda: 32 * 1024 * 1024,
        disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    ) -> MetadataOutcome:
        nonlocal mock_requests, emitted_bytes
        opener = FixtureHeadOpener(copy.deepcopy(tuple(exchanges)))
        outcome = run_metadata_pass(
            repo_root=repo_root,
            opener=opener,
            generated=True,
            workspace_root=workspace_root if output is not None else None,
            output_relative=output,
            caps=caps,
            environ=case_environ,
            clock=case_clock,
            rss_reader=case_rss,
            disk_usage_reader=disk_usage_reader,
        )
        mock_requests += len(opener.calls)
        emitted_bytes += outcome.measurements["output_bytes"]
        passed.append(name)
        return outcome

    complete = execute("complete_validators", source)
    optional = execute(
        "optional_validators_unavailable",
        build_generated_exchanges(optional_validators=False),
    )
    replay = execute("deterministic_replay", build_generated_exchanges())
    if complete.inventory_bytes != replay.inventory_bytes:
        raise UG1MetadataRefusal("generated metadata replay differs")
    if optional.inventory["unavailable_fields"] != ["etag", "last_modified", "accept_ranges"]:
        raise UG1MetadataRefusal("optional validator unavailability differs")

    for case in QUALIFICATION_CASES[3:12]:
        opener = FixtureHeadOpener(_mutated_exchanges(case))
        try:
            run_metadata_pass(
                repo_root=repo_root,
                opener=opener,
                generated=True,
                environ=environ,
                clock=lambda: 10.0,
                rss_reader=lambda: 32 * 1024 * 1024,
            )
        except UG1MetadataRefusal:
            mock_requests += len(opener.calls)
            passed.append(case)
        else:
            raise UG1MetadataRefusal(f"generated mutation unexpectedly passed: {case}")

    order_rows = list(build_generated_exchanges())
    order_rows[0], order_rows[1] = order_rows[1], order_rows[0]
    for case, exchanges in (
        ("request_order", order_rows),
        ("missing_response", build_generated_exchanges()[:-1]),
    ):
        opener = FixtureHeadOpener(exchanges)
        try:
            run_metadata_pass(
                repo_root=repo_root,
                opener=opener,
                generated=True,
                environ=environ,
                clock=lambda: 10.0,
                rss_reader=lambda: 32 * 1024 * 1024,
            )
        except UG1MetadataRefusal:
            mock_requests += len(opener.calls)
            passed.append(case)
        else:
            raise UG1MetadataRefusal(f"generated transport case unexpectedly passed: {case}")

    opener = FixtureHeadOpener(_mutated_exchanges("declared_byte_cap"))
    try:
        run_metadata_pass(
            repo_root=repo_root,
            opener=opener,
            generated=True,
            environ=environ,
            clock=lambda: 10.0,
            rss_reader=lambda: 32 * 1024 * 1024,
        )
    except UG1MetadataRefusal:
        mock_requests += len(opener.calls)
        passed.append("declared_byte_cap")
    else:
        raise UG1MetadataRefusal("generated declared-byte cap unexpectedly passed")

    execute("output_collision", build_generated_exchanges(), output="published")
    try:
        execute("second_output", build_generated_exchanges(), output="published")
    except UG1MetadataRefusal:
        passed[-1] = "output_collision"
    else:
        raise UG1MetadataRefusal("generated output collision unexpectedly passed")
    shutil.rmtree(Path(workspace_root) / "published")

    refusing = (
        (
            "thread_environment",
            {**environ, THREAD_ENV_KEYS[0]: "2"},
            MetadataCaps(),
            lambda: 10.0,
            lambda: 32 * 1024 * 1024,
            shutil.disk_usage,
        ),
        (
            "free_disk",
            environ,
            MetadataCaps(),
            lambda: 10.0,
            lambda: 32 * 1024 * 1024,
            lambda _path: type("Disk", (), {"free": 0})(),
        ),
        (
            "peak_rss",
            environ,
            MetadataCaps(),
            lambda: 10.0,
            lambda: MAX_PEAK_RSS_BYTES + 1,
            shutil.disk_usage,
        ),
        (
            "wall_time",
            environ,
            MetadataCaps(),
            iter((0.0, MAX_WALL_SECONDS + 1)).__next__,
            lambda: 32 * 1024 * 1024,
            shutil.disk_usage,
        ),
    )
    for case, case_env, caps, case_clock, case_rss, disk_reader in refusing:
        opener = FixtureHeadOpener(build_generated_exchanges())
        try:
            run_metadata_pass(
                repo_root=repo_root,
                opener=opener,
                generated=True,
                workspace_root=workspace_root,
                output_relative=f"refuse-{case}",
                caps=caps,
                environ=case_env,
                clock=case_clock,
                rss_reader=case_rss,
                disk_usage_reader=disk_reader,
            )
        except UG1MetadataRefusal:
            mock_requests += len(opener.calls)
            passed.append(case)
        else:
            raise UG1MetadataRefusal(f"generated resource case unexpectedly passed: {case}")

    if tuple(passed) != QUALIFICATION_CASES:
        raise UG1MetadataRefusal("generated qualification case order differs")
    current_source = build_generated_exchanges()
    current_fingerprint = _sha256(
        _canonical_json(
            [
                {
                    "url": row.url,
                    "status": row.response.status,
                    "headers": list(row.response.headers.raw_items()),
                }
                for row in current_source
            ]
        )
    )
    if current_fingerprint != source_fingerprint:
        raise UG1MetadataRefusal("generated fixture source mutated")
    runtime = clock() - started
    peak_rss = int(rss_reader())
    if runtime < 0 or runtime > MAX_WALL_SECONDS or peak_rss > MAX_PEAK_RSS_BYTES:
        raise UG1MetadataRefusal("generated qualification resource cap exceeded")
    summary = {
        "schema_name": "neurodecodekit.eegmmidb_ug1_metadata_stage_m1_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": GENERATED_ROUTE,
        "case_count": len(passed),
        "cases": passed,
        "mock_HEAD_requests": mock_requests,
        "real_HEAD_requests": 0,
        "response_body_reads": 0,
        "response_body_bytes": 0,
        "real_URL_or_local_data_path_operations": 0,
        "EDF_content_reads": 0,
        "payload_download_bytes": 0,
        "target_or_label_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "scoring_events": 0,
        "generated_metadata_bytes_emitted_across_success_cases": emitted_bytes,
        "retained_generated_output_bytes": 0,
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": peak_rss,
        "source_fixture_sha256": source_fingerprint,
        "deterministic_replay": True,
        "source_immutability_checks": 1,
        "warnings": [
            "generated_mock_only",
            "standard_library_live_transport_not_invoked",
            "not_neural_or_decoding_evidence",
        ],
        "claim_boundary": {
            "scientific_claim_established": False,
            "real_EEG_accessed": False,
            "unseen_participant_generalization_established": False,
        },
    }
    if len(_canonical_json(summary)) > MAX_OUTPUT_BYTES:
        raise UG1MetadataRefusal("generated qualification summary exceeds output cap")
    return summary


def write_generated_summary(path: str | Path, summary: Mapping[str, Any]) -> tuple[int, str]:
    """Atomically publish one bounded aggregate generated qualification summary."""

    destination = Path(path)
    if any(part in FORBIDDEN_OUTPUT_COMPONENTS for part in destination.parts):
        raise UG1MetadataRefusal("generated summary path uses a protected root")
    parent = destination.parent
    try:
        observed = os.lstat(parent)
    except OSError as exc:
        raise UG1MetadataRefusal("generated summary parent is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise UG1MetadataRefusal("generated summary parent is unsafe")
    payload = _canonical_json(dict(summary))
    if len(payload) > MAX_OUTPUT_BYTES:
        raise UG1MetadataRefusal("generated qualification summary exceeds output cap")
    acquisition._write_atomic(destination, payload)
    return len(payload), _sha256(payload)
