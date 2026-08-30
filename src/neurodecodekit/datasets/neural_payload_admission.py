"""Generated-only qualification for the NPA1 transport-admission boundary."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import resource
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

SCHEMA_NAME = "neurodecodekit.neural_payload_admission_generated_qualification"
SCHEMA_VERSION = "0.1.0"
PROTOCOL_ID = "NPA1-G-v0"
FRONTIER_RELATIVE_PATH = Path("registries/current_research_frontier.v7.json")
FRONTIER_SHA256 = "20fdc3cd9f2878c61984935c61ef05f7b0a4fbee79819778fbc795eb8cb3759c"
FRONTIER_BYTES = 5_245
FRONTIER_GIT_BLOB = "b6910f6e86036c034cec6a71b8716c953adc9822"
GREEN_FRONTIER_COMMIT = "d07eea0bc0ae2d6a218c06e08ef9ffa7e1592c35"
GREEN_FRONTIER_CI_RUN_ID = 33_281_704_903
GREEN_FRONTIER_BASE_JOB_ID = 99_177_847_778
GREEN_FRONTIER_OPTIONAL_JOB_ID = 99_177_847_631
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_GENERATED_BYTES = 8 * 1024 * 1024
MAX_REPORT_BYTES = 1024 * 1024
MAX_REDIRECTS = 2
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
SIGNED_QUERY_KEYS = ("cap", "issued", "ttl", "signature")
ALLOWED_HOSTS = ("source.example.org", "objects.example.net")
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
FROZEN_NOW_EPOCH_SECONDS = 1_700_000_300
MAX_CAPABILITY_TTL_SECONDS = 600
USER_AGENT = "NeuroDecodeKit-NPA1G/0.1"

REFUSAL_IDS = {
    "binding": "NPA1-G-F00-BINDING",
    "capability": "NPA1-G-F01-CAPABILITY",
    "route": "NPA1-G-F02-ROUTE",
    "redirect": "NPA1-G-F03-REDIRECT",
    "status": "NPA1-G-F04-STATUS",
    "header": "NPA1-G-F05-HEADER",
    "framing": "NPA1-G-F06-FRAMING",
    "range": "NPA1-G-F07-RANGE",
    "read": "NPA1-G-F08-READ",
    "length": "NPA1-G-F09-LENGTH",
    "identity": "NPA1-G-F10-IDENTITY",
    "close": "NPA1-G-F11-CLOSE",
    "open": "NPA1-G-F12-OPEN",
    "replay": "NPA1-G-F13-REPLAY",
    "resource": "NPA1-G-F14-RESOURCE",
    "output": "NPA1-G-F15-OUTPUT",
    "source": "NPA1-G-F16-SOURCE",
}

REQUIRED_MUTATIONS = (
    "non_https",
    "userinfo",
    "nondefault_port",
    "fragment",
    "host_drift",
    "private_resolution",
    "redirect_overflow",
    "redirect_body",
    "redirect_encoding",
    "redirect_missing_location",
    "redirect_loop",
    "automatic_redirect_drift",
    "status_mismatch",
    "duplicate_content_length",
    "malformed_content_length",
    "length_plus_transfer_encoding",
    "unsupported_transfer_encoding",
    "compressed_content_encoding",
    "body_underflow",
    "body_overflow",
    "nonbytes_body",
    "body_read_error",
    "close_failure",
    "invalid_range_profile",
    "missing_content_range",
    "mismatched_content_range",
    "body_hash_drift",
    "unexpected_second_open",
    "unused_transcript_response",
    "redirect_request_header_drift",
    "signed_query_drift",
    "signed_path_drift",
    "signed_expiry_invalid",
    "signed_expired",
    "signed_lifetime_excess",
    "signed_future_issued",
    "late_body_overflow",
)

ACCEPTED_PROFILE_IDS = (
    "direct_200",
    "direct_206",
    "metadata_chunked",
    "metadata_close",
    "metadata_fixed",
    "redirect_1",
    "redirect_2",
)
EXPECTED_STABLE_TRANSCRIPT_SHA256 = (
    "87fd828a07f5fa66253beb05d76b7620dfa34fbcc3a10159534732d063dd8d13"
)
EXPECTED_REFUSAL_ROUTES = (
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["route"],
    REFUSAL_IDS["redirect"],
    REFUSAL_IDS["length"],
    REFUSAL_IDS["header"],
    REFUSAL_IDS["redirect"],
    REFUSAL_IDS["redirect"],
    REFUSAL_IDS["redirect"],
    REFUSAL_IDS["status"],
    REFUSAL_IDS["header"],
    REFUSAL_IDS["framing"],
    REFUSAL_IDS["framing"],
    REFUSAL_IDS["framing"],
    REFUSAL_IDS["header"],
    REFUSAL_IDS["length"],
    REFUSAL_IDS["length"],
    REFUSAL_IDS["read"],
    REFUSAL_IDS["read"],
    REFUSAL_IDS["close"],
    REFUSAL_IDS["range"],
    REFUSAL_IDS["range"],
    REFUSAL_IDS["range"],
    REFUSAL_IDS["identity"],
    REFUSAL_IDS["open"],
    REFUSAL_IDS["open"],
    REFUSAL_IDS["open"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["capability"],
    REFUSAL_IDS["length"],
)
DETERMINISTIC_MEASUREMENTS = {
    "generated_input_bytes": 4_162,
    "response_opens": 44,
    "body_reads": 180,
    "response_closes": 44,
    "generated_resolver_calls": 55,
}
OPERATION_COUNTER_KEYS = (
    "network_requests",
    "network_bytes",
    "real_source_reads",
    "real_header_reads",
    "semantic_measurement_reads",
    "model_runs",
    "training_runs",
    "prediction_sets",
    "scores",
    "device_or_stream_runs",
    "scientific_claim_upgrades",
)
MEASUREMENT_KEYS = (
    "generated_input_bytes",
    "generated_output_bytes",
    "runtime_seconds",
    "peak_RSS_bytes",
    "response_opens",
    "body_reads",
    "response_closes",
    "generated_resolver_calls",
    "CPU_threads",
    "workers",
    "producer_is_causal",
    "end_to_end_latency_measured",
    "retained_generated_payload_bytes",
)
WARNINGS = (
    "generated_responses_are_not_neural_measurements",
    "signed_capabilities_are_ephemeral_and_not_scientific_identity",
    "no_live_network_opener_or_real_execution_command_exists",
)
UNAVAILABLE_FIELDS = (
    "live_transport_behavior",
    "real_object_identity",
    "sensor_semantics",
    "biological_effect",
    "end_to_end_latency",
)
CLAIM_BOUNDARY = {
    "engineering_capability_added": "A dependency-free generated validator now separates stable source identity, expiring transport capability, HTTP framing, bounded content identity, and later sensor semantics.",
    "scientific_claim_not_established": "Generated transport fixtures establish no neural information, unseen-person generalization, movement-intention decoding, language decoding, live operation, hardware result, or clinical value.",
}
GREEN_FRONTIER_EVIDENCE = {
    "commit": GREEN_FRONTIER_COMMIT,
    "CI_run_id": GREEN_FRONTIER_CI_RUN_ID,
    "base_python_job_id": GREEN_FRONTIER_BASE_JOB_ID,
    "optional_neuro_readers_job_id": GREEN_FRONTIER_OPTIONAL_JOB_ID,
    "both_required_jobs_green": True,
    "artifact_sha256": FRONTIER_SHA256,
    "artifact_bytes": FRONTIER_BYTES,
    "artifact_git_blob": FRONTIER_GIT_BLOB,
}


class NeuralPayloadAdmissionRefusal(RuntimeError):
    """Fail closed with a stable generated-only refusal identifier."""

    def __init__(self, route: str, reason: str):
        if route not in REFUSAL_IDS.values():
            raise ValueError("unknown NPA1-G refusal identifier")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class ScientificSourceIdentity:
    """Stable content identity, independent of an expiring delivery URL."""

    source_id: str
    revision: str
    object_key: str
    object_bytes: int
    object_sha256: str


@dataclass(frozen=True)
class TransportCapability:
    """Ephemeral permission to transport one stable generated object."""

    url: str
    allowed_hosts: tuple[str, ...]
    maximum_redirects: int


@dataclass(frozen=True)
class TerminalProfile:
    """Expected terminal response semantics for one generated object."""

    profile_id: str
    source: ScientificSourceIdentity
    status: int
    framing: str
    expected_body_bytes: int
    expected_body_sha256: str
    range_start: int | None = None
    range_end: int | None = None
    total_bytes: int | None = None


@dataclass(frozen=True)
class FixtureExchange:
    """One inert response in an injected HTTP transcript."""

    request_url: str
    status: int
    headers: tuple[tuple[str, str], ...]
    body: object
    expected_request_headers: tuple[tuple[str, str], ...]
    reported_url: str | None = None
    read_error: bool = False
    close_error: bool = False
    read_chunk_bytes: int | None = None


@dataclass
class FixtureMetrics:
    response_opens: int = 0
    body_reads: int = 0
    generated_body_bytes_read: int = 0
    resolver_calls: int = 0
    response_closes: int = 0


class FixtureResponse:
    """Minimal HTTPResponse-like generated fixture with auditable operations."""

    def __init__(self, exchange: FixtureExchange, metrics: FixtureMetrics) -> None:
        self.status = exchange.status
        self.headers = Message()
        for name, value in exchange.headers:
            self.headers[name] = value
        self._body = exchange.body
        self._reported_url = exchange.reported_url or exchange.request_url
        self._read_error = exchange.read_error
        self._close_error = exchange.close_error
        self._read_chunk_bytes = exchange.read_chunk_bytes
        self._offset = 0
        self._closed = False
        self._metrics = metrics

    def getcode(self) -> int:
        return self.status

    def geturl(self) -> str:
        return self._reported_url

    def read(self, size: int = -1) -> object:
        self._metrics.body_reads += 1
        if self._read_error:
            self._read_error = False
            raise OSError("generated read failure")
        if not isinstance(self._body, bytes):
            return self._body
        if self._offset >= len(self._body):
            return b""
        available = len(self._body) - self._offset
        requested = available if size < 0 else min(size, available)
        if self._read_chunk_bytes is not None:
            requested = min(requested, self._read_chunk_bytes)
        payload = self._body[self._offset : self._offset + requested]
        self._offset += len(payload)
        self._metrics.generated_body_bytes_read += len(payload)
        return payload

    def close(self) -> None:
        if self._closed:
            return
        if self._close_error:
            self._close_error = False
            raise OSError("generated close failure")
        self._closed = True
        self._metrics.response_closes += 1


class FixtureOpener:
    """Sequential injected opener; it contains no network implementation."""

    def __init__(self, exchanges: Sequence[FixtureExchange], metrics: FixtureMetrics):
        self._exchanges = tuple(exchanges)
        self._index = 0
        self._metrics = metrics

    @property
    def open_count(self) -> int:
        return self._index

    @property
    def remaining(self) -> int:
        return len(self._exchanges) - self._index

    def open(
        self, url: str, request_headers: tuple[tuple[str, str], ...]
    ) -> FixtureResponse:
        if self._index >= len(self._exchanges):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["open"], "response-open count exceeded transcript"
            )
        exchange = self._exchanges[self._index]
        self._index += 1
        if (
            url != exchange.request_url
            or request_headers != exchange.expected_request_headers
        ):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["open"], "request capability or headers differ"
            )
        self._metrics.response_opens += 1
        return FixtureResponse(exchange, self._metrics)


class FixtureResolver:
    """Inert resolver fixture with no socket or DNS implementation."""

    def __init__(self, addresses: Sequence[str] = ("8.8.8.8",)) -> None:
        self._addresses = tuple(addresses)

    def resolve(self, _hostname: str) -> tuple[str, ...]:
        return self._addresses


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


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _is_hex(value: object, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(
        character in "0123456789abcdef" for character in value
    )


def _validate_frontier(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / FRONTIER_RELATIVE_PATH
    if (
        not path.is_file()
        or path.is_symlink()
        or path.stat().st_size != FRONTIER_BYTES
        or _sha256_file(path) != FRONTIER_SHA256
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["binding"], "frontier artifact identity differs"
        )
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("status")
        != "NPA1_transport_admission_architecture_frozen_no_source_promoted"
        or value.get("selected_architecture", {}).get("next_stage")
        != "NPA1_G_generated_transport_qualification"
        or value.get("operation_authority", {}).get(
            "generated_fixture_only_NPA1_G_implementation_after_frontier_green"
        )
        is not True
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["binding"], "frontier authority differs"
        )
    return value


def _validate_source(source: ScientificSourceIdentity) -> None:
    if (
        not isinstance(source.source_id, str)
        or not source.source_id.isascii()
        or not source.source_id
        or not isinstance(source.revision, str)
        or not source.revision.isascii()
        or not source.revision
        or not isinstance(source.object_key, str)
        or not source.object_key.startswith("/")
        or ".." in source.object_key
        or "?" in source.object_key
        or "#" in source.object_key
        or type(source.object_bytes) is not int
        or source.object_bytes <= 0
        or not _is_hex(source.object_sha256, 64)
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["source"], "stable source identity is malformed"
        )


def _validate_capability_url(
    url: str,
    *,
    source: ScientificSourceIdentity,
    allowed_hosts: Sequence[str],
    resolver: FixtureResolver,
    metrics: FixtureMetrics,
    now_epoch_seconds: int,
) -> None:
    try:
        if not isinstance(url, str) or not url.isascii():
            raise ValueError("capability is not an ASCII string")
        parsed = urlsplit(url)
        port = parsed.port
    except (TypeError, ValueError) as exc:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["capability"], "capability URL is malformed"
        ) from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 443}
        or parsed.fragment
        or parsed.hostname not in allowed_hosts
        or parsed.path != source.object_key
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["capability"], "capability route differs"
        )
    try:
        pairs = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True)
    except ValueError as exc:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["capability"], "signed query is malformed"
        ) from exc
    if tuple(key for key, _value in pairs) != SIGNED_QUERY_KEYS:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["capability"], "signed query shape differs"
        )
    query = dict(pairs)
    try:
        issued = int(query["issued"])
        ttl = int(query["ttl"])
    except (KeyError, ValueError) as exc:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["capability"], "signed capability time differs"
        ) from exc
    if (
        query["cap"] != source.source_id
        or not _is_hex(query["signature"], 16)
        or str(issued) != query["issued"]
        or str(ttl) != query["ttl"]
        or ttl <= 0
        or ttl > MAX_CAPABILITY_TTL_SECONDS
        or now_epoch_seconds < issued
        or now_epoch_seconds > issued + ttl
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["capability"], "signed query value differs"
        )
    metrics.resolver_calls += 1
    try:
        addresses = resolver.resolve(parsed.hostname)
        if not addresses or any(
            not ipaddress.ip_address(address).is_global for address in addresses
        ):
            raise ValueError("non-global address")
    except (OSError, ValueError) as exc:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["route"], "capability host is not globally routable"
        ) from exc


def _strict_headers(response: FixtureResponse) -> dict[str, str]:
    critical = {
        "content-encoding",
        "content-length",
        "content-range",
        "location",
        "transfer-encoding",
    }
    result: dict[str, str] = {}
    for name, value in response.headers.raw_items():
        raw_key = str(name)
        raw_text = str(value)
        key = raw_key.strip().lower()
        text = raw_text.strip()
        if (
            not key
            or raw_key != raw_key.strip()
            or raw_text != text
            or "\r" in raw_key
            or "\n" in raw_key
            or "\r" in text
            or "\n" in text
        ):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["header"], "critical header is malformed"
            )
        if key not in critical:
            continue
        if key in result:
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["header"], "critical header is duplicated"
            )
        result[key] = text
    return result


def _strict_status(response: FixtureResponse) -> int:
    value = response.getcode()
    if type(value) is not int:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["status"], "response status is unavailable"
        )
    return value


def _read_once(response: FixtureResponse, maximum_bytes: int) -> bytes:
    chunks: list[bytes] = []
    observed = 0
    while True:
        try:
            value = response.read(min(64 * 1024, maximum_bytes - observed + 1))
        except Exception as exc:
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["read"], "response body read failed"
            ) from exc
        if not isinstance(value, bytes):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["read"], "response body is not bytes"
            )
        if not value:
            break
        chunks.append(value)
        observed += len(value)
        if observed > maximum_bytes:
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["length"], "response body exceeds cap"
            )
    return b"".join(chunks)


def _close_strict(response: FixtureResponse) -> None:
    try:
        response.close()
    except Exception as exc:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["close"], "response close failed"
        ) from exc


def _close_quietly(response: FixtureResponse) -> None:
    try:
        response.close()
    except OSError:
        pass


def _validate_identity_encoding(headers: Mapping[str, str]) -> str:
    value = headers.get("content-encoding")
    if value is None:
        return "absent"
    if value.casefold() != "identity":
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["header"], "content encoding is not identity"
        )
    return "identity"


def _parse_content_length(raw: str) -> int:
    if not raw or not raw.isascii() or not raw.isdigit():
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["framing"], "Content-Length is malformed"
        )
    return int(raw)


def _validate_profile(profile: TerminalProfile) -> None:
    if (
        not isinstance(profile.profile_id, str)
        or not profile.profile_id
        or profile.status not in {200, 206}
        or profile.framing not in {"fixed_length", "chunked", "close_delimited"}
        or type(profile.expected_body_bytes) is not int
        or profile.expected_body_bytes <= 0
        or not _is_hex(profile.expected_body_sha256, 64)
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["source"], "terminal profile is malformed"
        )
    if profile.status == 206:
        if (
            profile.framing != "fixed_length"
            or type(profile.range_start) is not int
            or type(profile.range_end) is not int
            or type(profile.total_bytes) is not int
            or profile.range_start < 0
            or profile.range_end < profile.range_start
            or profile.total_bytes != profile.source.object_bytes
            or profile.range_end >= profile.total_bytes
            or profile.range_end - profile.range_start + 1
            != profile.expected_body_bytes
        ):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["range"], "range profile is internally inconsistent"
            )
    elif (
        profile.range_start is not None
        or profile.range_end is not None
        or profile.total_bytes is not None
        or profile.expected_body_bytes != profile.source.object_bytes
        or profile.expected_body_sha256 != profile.source.object_sha256
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["range"], "full-object profile differs from source identity"
        )


def _request_headers(profile: TerminalProfile) -> tuple[tuple[str, str], ...]:
    headers = [
        ("Accept-Encoding", "identity"),
        ("User-Agent", USER_AGENT),
    ]
    if profile.status == 206:
        headers.append(("Range", f"bytes={profile.range_start}-{profile.range_end}"))
    return tuple(headers)


def _validate_terminal(
    response: FixtureResponse,
    *,
    profile: TerminalProfile,
) -> dict[str, Any]:
    if response.geturl() == "" or _strict_status(response) != profile.status:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["status"], "terminal response status differs"
        )
    headers = _strict_headers(response)
    encoding_state = _validate_identity_encoding(headers)
    content_length = headers.get("content-length")
    transfer_encoding = headers.get("transfer-encoding")
    if content_length is not None and transfer_encoding is not None:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["framing"], "length and transfer coding are ambiguous"
        )
    if profile.framing == "fixed_length":
        if (
            content_length is None
            or _parse_content_length(content_length) != profile.expected_body_bytes
        ):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["framing"], "fixed-length framing differs"
            )
        if transfer_encoding is not None:
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["framing"], "transfer coding is unexpected"
            )
    elif profile.framing == "chunked":
        if content_length is not None or transfer_encoding is None or transfer_encoding.casefold() != "chunked":
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["framing"], "chunked framing differs"
            )
    elif profile.framing == "close_delimited":
        if content_length is not None or transfer_encoding is not None:
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["framing"], "close-delimited framing differs"
            )
    else:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["framing"], "terminal framing profile is unknown"
        )
    if profile.status == 206:
        expected = (
            f"bytes {profile.range_start}-{profile.range_end}/{profile.total_bytes}"
        )
        if headers.get("content-range") != expected:
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["range"], "Content-Range differs"
            )
    elif "content-range" in headers:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["range"], "Content-Range is unexpected"
        )
    body = _read_once(response, profile.expected_body_bytes)
    if len(body) != profile.expected_body_bytes:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["length"], "observed body byte count differs"
        )
    body_sha256 = _sha256_bytes(body)
    if body_sha256 != profile.expected_body_sha256:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["identity"], "bounded content identity differs"
        )
    return {
        "profile_id": profile.profile_id,
        "terminal_status": profile.status,
        "framing_profile": profile.framing,
        "encoding_state": encoding_state,
        "accepted_bytes": len(body),
        "content_sha256": body_sha256,
        "stable_source_sha256": _sha256_bytes(
            _canonical_json_bytes(
                {
                    "source_id": profile.source.source_id,
                    "revision": profile.source.revision,
                    "object_key": profile.source.object_key,
                    "object_bytes": profile.source.object_bytes,
                    "object_sha256": profile.source.object_sha256,
                }
            )
        ),
        "range_validated": profile.status == 206,
    }


def admit_generated_transport(
    *,
    profile: TerminalProfile,
    capability: TransportCapability,
    opener: FixtureOpener,
    resolver: FixtureResolver,
    metrics: FixtureMetrics,
    now_epoch_seconds: int = FROZEN_NOW_EPOCH_SECONDS,
) -> dict[str, Any]:
    """Admit one injected transcript without exposing a live network surface."""

    if (
        type(profile) is not TerminalProfile
        or type(profile.source) is not ScientificSourceIdentity
        or type(capability) is not TransportCapability
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["source"], "generated transport type differs"
        )
    _validate_source(profile.source)
    _validate_profile(profile)
    if (
        type(opener) is not FixtureOpener
        or type(resolver) is not FixtureResolver
        or type(metrics) is not FixtureMetrics
        or type(now_epoch_seconds) is not int
        or tuple(capability.allowed_hosts) != ALLOWED_HOSTS
        or type(capability.maximum_redirects) is not int
        or not 0 <= capability.maximum_redirects <= MAX_REDIRECTS
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["capability"], "transport capability policy differs"
        )
    current_url = capability.url
    seen: set[str] = set()
    redirects = 0
    while True:
        if current_url in seen:
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["redirect"], "redirect loop detected"
            )
        seen.add(current_url)
        _validate_capability_url(
            current_url,
            source=profile.source,
            allowed_hosts=capability.allowed_hosts,
            resolver=resolver,
            metrics=metrics,
            now_epoch_seconds=now_epoch_seconds,
        )
        response = opener.open(current_url, _request_headers(profile))
        try:
            if response.geturl() != current_url:
                raise NeuralPayloadAdmissionRefusal(
                    REFUSAL_IDS["redirect"], "automatic redirect or URL drift"
                )
            status = _strict_status(response)
            headers = _strict_headers(response)
            if status in REDIRECT_STATUSES:
                if redirects >= capability.maximum_redirects:
                    raise NeuralPayloadAdmissionRefusal(
                        REFUSAL_IDS["redirect"], "redirect cap exceeded"
                    )
                if "transfer-encoding" in headers:
                    raise NeuralPayloadAdmissionRefusal(
                        REFUSAL_IDS["redirect"], "redirect transfer coding is forbidden"
                    )
                _validate_identity_encoding(headers)
                if headers.get("content-length") not in {None, "0"}:
                    raise NeuralPayloadAdmissionRefusal(
                        REFUSAL_IDS["redirect"], "redirect length differs"
                    )
                location = headers.get("location")
                if location is None:
                    raise NeuralPayloadAdmissionRefusal(
                        REFUSAL_IDS["redirect"], "redirect location is missing"
                    )
                if _read_once(response, 0):
                    raise NeuralPayloadAdmissionRefusal(
                        REFUSAL_IDS["redirect"], "redirect body is not empty"
                    )
                next_url = urljoin(current_url, location)
                _validate_capability_url(
                    next_url,
                    source=profile.source,
                    allowed_hosts=capability.allowed_hosts,
                    resolver=resolver,
                    metrics=metrics,
                    now_epoch_seconds=now_epoch_seconds,
                )
                _close_strict(response)
                current_url = next_url
                redirects += 1
                continue
            result = _validate_terminal(response, profile=profile)
            _close_strict(response)
            if opener.remaining != 0:
                raise NeuralPayloadAdmissionRefusal(
                    REFUSAL_IDS["open"], "transcript contains an unused response"
                )
            result["redirect_count"] = redirects
            result["response_opens"] = opener.open_count
            result["request_headers_validated"] = True
            return result
        except NeuralPayloadAdmissionRefusal:
            _close_quietly(response)
            raise


def _fixture_body(name: str, length: int) -> bytes:
    seed = hashlib.sha256(f"npa1-generated:{name}".encode("ascii")).digest()
    repeats = (length + len(seed) - 1) // len(seed)
    return (seed * repeats)[:length]


def _source(name: str, body: bytes, object_key: str) -> ScientificSourceIdentity:
    return ScientificSourceIdentity(
        source_id=f"npa1-{name}",
        revision="generated-r1",
        object_key=object_key,
        object_bytes=len(body),
        object_sha256=_sha256_bytes(body),
    )


def _signed_url(
    source: ScientificSourceIdentity,
    signature: str,
    host: str = ALLOWED_HOSTS[0],
    *,
    issued: int = 1_700_000_000,
    ttl: int = MAX_CAPABILITY_TTL_SECONDS,
) -> str:
    query = urlencode(
        (
            ("cap", source.source_id),
            ("issued", str(issued)),
            ("ttl", str(ttl)),
            ("signature", signature),
        )
    )
    return urlunsplit(("https", host, source.object_key, query, ""))


def _headers_for(profile: TerminalProfile) -> tuple[tuple[str, str], ...]:
    headers: list[tuple[str, str]] = [("Content-Encoding", "identity")]
    if profile.framing == "fixed_length":
        headers.append(("Content-Length", str(profile.expected_body_bytes)))
    elif profile.framing == "chunked":
        headers.append(("Transfer-Encoding", "chunked"))
    if profile.status == 206:
        headers.append(
            (
                "Content-Range",
                f"bytes {profile.range_start}-{profile.range_end}/{profile.total_bytes}",
            )
        )
    return tuple(headers)


def _acceptance_profiles() -> tuple[tuple[TerminalProfile, bytes], ...]:
    full = _fixture_body("full-object", 128)
    range_object = _fixture_body("range-object", 4_096)
    segment = range_object[:256]
    metadata = _fixture_body("metadata", 96)
    return (
        (
            TerminalProfile(
                "direct_200",
                _source("full", full, "/objects/full.bin"),
                200,
                "fixed_length",
                len(full),
                _sha256_bytes(full),
            ),
            full,
        ),
        (
            TerminalProfile(
                "direct_206",
                _source("range", range_object, "/objects/range.bin"),
                206,
                "fixed_length",
                len(segment),
                _sha256_bytes(segment),
                0,
                255,
                len(range_object),
            ),
            segment,
        ),
        (
            TerminalProfile(
                "metadata_fixed",
                _source("meta", metadata, "/metadata/source.json"),
                200,
                "fixed_length",
                len(metadata),
                _sha256_bytes(metadata),
            ),
            metadata,
        ),
        (
            TerminalProfile(
                "metadata_chunked",
                _source("meta", metadata, "/metadata/source.json"),
                200,
                "chunked",
                len(metadata),
                _sha256_bytes(metadata),
            ),
            metadata,
        ),
        (
            TerminalProfile(
                "metadata_close",
                _source("meta", metadata, "/metadata/source.json"),
                200,
                "close_delimited",
                len(metadata),
                _sha256_bytes(metadata),
            ),
            metadata,
        ),
    )


def _run_acceptance_replay(signature: str, metrics: FixtureMetrics) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    profiles = _acceptance_profiles()
    for profile, body in profiles:
        capability = TransportCapability(_signed_url(profile.source, signature), ALLOWED_HOSTS, 0)
        exchange = FixtureExchange(
            capability.url,
            profile.status,
            _headers_for(profile),
            body,
            _request_headers(profile),
            read_chunk_bytes=7 if profile.framing != "fixed_length" else 31,
        )
        rows.append(
            admit_generated_transport(
                profile=profile,
                capability=capability,
                opener=FixtureOpener((exchange,), metrics),
                resolver=FixtureResolver(),
                metrics=metrics,
            )
        )

    range_profile, range_body = profiles[1]
    initial = _signed_url(range_profile.source, signature)
    first_redirect = _signed_url(range_profile.source, signature, ALLOWED_HOSTS[1])
    for count in (1, 2):
        urls = (initial, first_redirect, initial) if count == 2 else (initial, first_redirect)
        if count == 2:
            middle_signature = hashlib.sha256(signature.encode("ascii")).hexdigest()[:16]
            final_signature = hashlib.sha256(
                f"{signature}:final".encode("ascii")
            ).hexdigest()[:16]
            urls = (
                initial,
                _signed_url(range_profile.source, middle_signature, ALLOWED_HOSTS[1]),
                _signed_url(range_profile.source, final_signature, ALLOWED_HOSTS[0]),
            )
        exchanges: list[FixtureExchange] = []
        for index in range(count):
            exchanges.append(
                FixtureExchange(
                    urls[index],
                    302,
                    (("Location", urls[index + 1]), ("Content-Length", "0")),
                    b"",
                    _request_headers(range_profile),
                )
            )
        exchanges.append(
            FixtureExchange(
                urls[-1],
                range_profile.status,
                _headers_for(range_profile),
                range_body,
                _request_headers(range_profile),
                read_chunk_bytes=29,
            )
        )
        row = admit_generated_transport(
            profile=range_profile,
            capability=TransportCapability(initial, ALLOWED_HOSTS, count),
            opener=FixtureOpener(exchanges, metrics),
            resolver=FixtureResolver(),
            metrics=metrics,
        )
        row["profile_id"] = f"redirect_{count}"
        rows.append(row)
    stable_rows = sorted(rows, key=lambda row: str(row["profile_id"]))
    return {
        "accepted_profiles": stable_rows,
        "stable_transcript_sha256": _sha256_bytes(_canonical_json_bytes(stable_rows)),
    }


def _base_range_case() -> tuple[TerminalProfile, bytes, str, FixtureExchange]:
    range_object = _fixture_body("mutation-object", 4_096)
    segment = range_object[:256]
    profile = TerminalProfile(
        "mutation_range",
        _source("mutation", range_object, "/objects/mutation.bin"),
        206,
        "fixed_length",
        len(segment),
        _sha256_bytes(segment),
        0,
        255,
        len(range_object),
    )
    url = _signed_url(profile.source, "0123456789abcdef")
    return profile, segment, url, FixtureExchange(
        url,
        206,
        _headers_for(profile),
        segment,
        _request_headers(profile),
    )


def _execute_case(
    profile: TerminalProfile,
    url: str,
    exchanges: Sequence[FixtureExchange],
    metrics: FixtureMetrics,
    *,
    redirects: int = 0,
    resolver: FixtureResolver | None = None,
) -> dict[str, Any]:
    return admit_generated_transport(
        profile=profile,
        capability=TransportCapability(url, ALLOWED_HOSTS, redirects),
        opener=FixtureOpener(exchanges, metrics),
        resolver=FixtureResolver() if resolver is None else resolver,
        metrics=metrics,
    )


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], object],
) -> dict[str, str]:
    try:
        operation()
    except NeuralPayloadAdmissionRefusal as exc:
        if exc.route != expected_route:
            raise AssertionError(f"{name} routed to {exc.route}, expected {expected_route}") from exc
        return {"mutation": name, "refusal_id": exc.route}
    raise AssertionError(f"{name} did not refuse")


def run_refusal_matrix(metrics: FixtureMetrics) -> list[dict[str, str]]:
    """Execute the frozen generated adversarial surface once."""

    profile, body, url, exchange = _base_range_case()
    parsed = urlsplit(url)

    def replace_url(*, scheme: str | None = None, netloc: str | None = None, path: str | None = None, query: str | None = None, fragment: str | None = None) -> str:
        return urlunsplit(
            (
                parsed.scheme if scheme is None else scheme,
                parsed.netloc if netloc is None else netloc,
                parsed.path if path is None else path,
                parsed.query if query is None else query,
                parsed.fragment if fragment is None else fragment,
            )
        )

    def terminal(
        *,
        request_url: str = url,
        status: int = 206,
        headers: tuple[tuple[str, str], ...] | None = None,
        payload: object = body,
        reported_url: str | None = None,
        read_error: bool = False,
        close_error: bool = False,
        read_chunk_bytes: int | None = None,
        expected_request_headers: tuple[tuple[str, str], ...] | None = None,
        resolver: FixtureResolver | None = None,
    ) -> object:
        item = FixtureExchange(
            request_url=request_url,
            status=status,
            headers=_headers_for(profile) if headers is None else headers,
            body=payload,
            expected_request_headers=(
                _request_headers(profile)
                if expected_request_headers is None
                else expected_request_headers
            ),
            reported_url=reported_url,
            read_error=read_error,
            close_error=close_error,
            read_chunk_bytes=read_chunk_bytes,
        )
        return _execute_case(profile, request_url, (item,), metrics, resolver=resolver)

    redirect_target = _signed_url(profile.source, "fedcba9876543210", ALLOWED_HOSTS[1])
    redirect = FixtureExchange(
        url,
        302,
        (("Location", redirect_target), ("Content-Length", "0")),
        b"",
        _request_headers(profile),
    )
    final = FixtureExchange(
        redirect_target,
        206,
        _headers_for(profile),
        body,
        _request_headers(profile),
    )
    base_headers = _headers_for(profile)
    query = urlencode(
        (
            ("cap", profile.source.source_id),
            ("issued", "1700000000"),
            ("ttl", "600"),
            ("extra", "1"),
            ("signature", "0123456789abcdef"),
        )
    )
    invalid_expiry = _signed_url(profile.source, "0123456789abcdef", ttl=0)
    expired = _signed_url(
        profile.source, "0123456789abcdef", issued=1_699_999_000
    )
    excessive_lifetime = _signed_url(
        profile.source, "0123456789abcdef", ttl=601
    )
    future_issued = _signed_url(
        profile.source, "0123456789abcdef", issued=1_700_000_301
    )
    invalid_range_profile = TerminalProfile(
        profile.profile_id,
        profile.source,
        profile.status,
        profile.framing,
        profile.expected_body_bytes,
        profile.expected_body_sha256,
        500,
        100,
        50,
    )

    cases: list[tuple[str, str, Callable[[], object]]] = [
        ("non_https", REFUSAL_IDS["capability"], lambda: terminal(request_url=replace_url(scheme="http"))),
        ("userinfo", REFUSAL_IDS["capability"], lambda: terminal(request_url=replace_url(netloc=f"user@{parsed.netloc}"))),
        ("nondefault_port", REFUSAL_IDS["capability"], lambda: terminal(request_url=replace_url(netloc=f"{parsed.netloc}:444"))),
        ("fragment", REFUSAL_IDS["capability"], lambda: terminal(request_url=replace_url(fragment="x"))),
        ("host_drift", REFUSAL_IDS["capability"], lambda: terminal(request_url=replace_url(netloc="other.example.org"))),
        ("private_resolution", REFUSAL_IDS["route"], lambda: terminal(resolver=FixtureResolver(("127.0.0.1",)))),
        ("redirect_overflow", REFUSAL_IDS["redirect"], lambda: _execute_case(profile, url, (redirect,), metrics, redirects=0)),
        ("redirect_body", REFUSAL_IDS["length"], lambda: _execute_case(profile, url, (FixtureExchange(url, 302, redirect.headers, b"x", _request_headers(profile)), final), metrics, redirects=1)),
        ("redirect_encoding", REFUSAL_IDS["header"], lambda: _execute_case(profile, url, (FixtureExchange(url, 302, redirect.headers + (("Content-Encoding", "gzip"),), b"", _request_headers(profile)), final), metrics, redirects=1)),
        ("redirect_missing_location", REFUSAL_IDS["redirect"], lambda: _execute_case(profile, url, (FixtureExchange(url, 302, (("Content-Length", "0"),), b"", _request_headers(profile)),), metrics, redirects=1)),
        ("redirect_loop", REFUSAL_IDS["redirect"], lambda: _execute_case(profile, url, (FixtureExchange(url, 302, (("Location", url), ("Content-Length", "0")), b"", _request_headers(profile)),), metrics, redirects=1)),
        ("automatic_redirect_drift", REFUSAL_IDS["redirect"], lambda: terminal(reported_url=redirect_target)),
        ("status_mismatch", REFUSAL_IDS["status"], lambda: terminal(status=200)),
        ("duplicate_content_length", REFUSAL_IDS["header"], lambda: terminal(headers=base_headers + (("Content-Length", "256"),))),
        ("malformed_content_length", REFUSAL_IDS["framing"], lambda: terminal(headers=tuple((key, "2x6" if key.lower() == "content-length" else value) for key, value in base_headers))),
        ("length_plus_transfer_encoding", REFUSAL_IDS["framing"], lambda: terminal(headers=base_headers + (("Transfer-Encoding", "chunked"),))),
        ("unsupported_transfer_encoding", REFUSAL_IDS["framing"], lambda: terminal(headers=(("Transfer-Encoding", "gzip"), ("Content-Encoding", "identity"), ("Content-Range", "bytes 0-255/4096")))),
        ("compressed_content_encoding", REFUSAL_IDS["header"], lambda: terminal(headers=tuple((key, "gzip" if key.lower() == "content-encoding" else value) for key, value in base_headers))),
        ("body_underflow", REFUSAL_IDS["length"], lambda: terminal(payload=body[:-1])),
        ("body_overflow", REFUSAL_IDS["length"], lambda: terminal(payload=body + b"x")),
        ("nonbytes_body", REFUSAL_IDS["read"], lambda: terminal(payload="not-bytes")),
        ("body_read_error", REFUSAL_IDS["read"], lambda: terminal(read_error=True)),
        ("close_failure", REFUSAL_IDS["close"], lambda: terminal(close_error=True)),
        ("invalid_range_profile", REFUSAL_IDS["range"], lambda: _execute_case(invalid_range_profile, url, (exchange,), metrics)),
        ("missing_content_range", REFUSAL_IDS["range"], lambda: terminal(headers=tuple((key, value) for key, value in base_headers if key.lower() != "content-range"))),
        ("mismatched_content_range", REFUSAL_IDS["range"], lambda: terminal(headers=tuple((key, "bytes 1-256/4096" if key.lower() == "content-range" else value) for key, value in base_headers))),
        ("body_hash_drift", REFUSAL_IDS["identity"], lambda: terminal(payload=b"x" + body[1:])),
        ("unexpected_second_open", REFUSAL_IDS["open"], lambda: _unexpected_second_open(profile, url, exchange, metrics)),
        ("unused_transcript_response", REFUSAL_IDS["open"], lambda: _execute_case(profile, url, (exchange, exchange), metrics)),
        ("redirect_request_header_drift", REFUSAL_IDS["open"], lambda: _execute_case(profile, url, (redirect, FixtureExchange(redirect_target, 206, _headers_for(profile), body, (("Accept-Encoding", "identity"),))), metrics, redirects=1)),
        ("signed_query_drift", REFUSAL_IDS["capability"], lambda: terminal(request_url=replace_url(query=query))),
        ("signed_path_drift", REFUSAL_IDS["capability"], lambda: terminal(request_url=replace_url(path="/objects/other.bin"))),
        ("signed_expiry_invalid", REFUSAL_IDS["capability"], lambda: terminal(request_url=invalid_expiry)),
        ("signed_expired", REFUSAL_IDS["capability"], lambda: terminal(request_url=expired)),
        ("signed_lifetime_excess", REFUSAL_IDS["capability"], lambda: terminal(request_url=excessive_lifetime)),
        ("signed_future_issued", REFUSAL_IDS["capability"], lambda: terminal(request_url=future_issued)),
        ("late_body_overflow", REFUSAL_IDS["length"], lambda: terminal(payload=body + b"x", read_chunk_bytes=17)),
    ]
    rows = [_expect_refusal(name, route, operation) for name, route, operation in cases]
    if tuple(row["mutation"] for row in rows) != REQUIRED_MUTATIONS:
        raise AssertionError("NPA1-G refusal matrix order differs")
    return rows


def _unexpected_second_open(
    profile: TerminalProfile,
    url: str,
    exchange: FixtureExchange,
    metrics: FixtureMetrics,
) -> object:
    opener = FixtureOpener((exchange,), metrics)
    first = _execute_case_with_opener(profile, url, opener, metrics)
    if first["accepted_bytes"] != profile.expected_body_bytes:
        raise AssertionError("first generated transport did not pass")
    return _execute_case_with_opener(profile, url, opener, metrics)


def _execute_case_with_opener(
    profile: TerminalProfile,
    url: str,
    opener: FixtureOpener,
    metrics: FixtureMetrics,
) -> dict[str, Any]:
    return admit_generated_transport(
        profile=profile,
        capability=TransportCapability(url, ALLOWED_HOSTS, 0),
        opener=opener,
        resolver=FixtureResolver(),
        metrics=metrics,
    )


def _validate_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["resource"], "thread environment is not fixed to one"
        )


def validate_public_report(report: Mapping[str, Any]) -> None:
    """Validate the aggregate generated-only qualification report."""

    expected_fields = {
        "schema_name",
        "schema_version",
        "protocol_id",
        "status",
        "green_frontier",
        "qualification",
        "measurements",
        "operation_counters",
        "warnings",
        "unavailable",
        "claim_boundary",
    }
    if not isinstance(report, Mapping) or set(report) != expected_fields:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "public report fields differ"
        )
    if (
        report.get("schema_name") != SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("protocol_id") != PROTOCOL_ID
        or report.get("status") != "accepted_generated_only_zero_network"
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "public report identity differs"
        )
    if report["green_frontier"] != GREEN_FRONTIER_EVIDENCE:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "green frontier evidence differs"
        )
    qualification = report["qualification"]
    qualification_fields = {
        "deterministic_replays",
        "accepted_profiles_per_replay",
        "accepted_profile_ids",
        "stable_transcript_sha256",
        "stable_transcript_digests_equal",
        "signed_capability_refresh_accepted",
        "named_adversarial_families",
        "distinct_refusal_ids",
        "refusals",
        "all_gates_passed",
    }
    if (
        not isinstance(qualification, Mapping)
        or set(qualification) != qualification_fields
        or qualification.get("deterministic_replays") != 2
        or qualification.get("accepted_profiles_per_replay")
        != len(ACCEPTED_PROFILE_IDS)
        or tuple(qualification.get("accepted_profile_ids", ()))
        != ACCEPTED_PROFILE_IDS
        or qualification.get("stable_transcript_sha256")
        != EXPECTED_STABLE_TRANSCRIPT_SHA256
        or qualification.get("named_adversarial_families") != len(REQUIRED_MUTATIONS)
        or qualification.get("stable_transcript_digests_equal") is not True
        or qualification.get("signed_capability_refresh_accepted") is not True
        or qualification.get("all_gates_passed") is not True
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "qualification summary differs"
        )
    refusals = qualification.get("refusals")
    if not isinstance(refusals, list) or len(refusals) != len(REQUIRED_MUTATIONS):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "refusal ledger differs"
        )
    for expected_name, expected_route, row in zip(
        REQUIRED_MUTATIONS, EXPECTED_REFUSAL_ROUTES, refusals, strict=True
    ):
        if (
            not isinstance(row, Mapping)
            or set(row) != {"mutation", "refusal_id"}
            or row.get("mutation") != expected_name
            or row.get("refusal_id") != expected_route
        ):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["output"], "refusal ledger differs"
            )
    if qualification.get("distinct_refusal_ids") != len(
        {row["refusal_id"] for row in refusals}
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "refusal summary differs"
        )
    counters = report["operation_counters"]
    if (
        not isinstance(counters, Mapping)
        or tuple(counters) != OPERATION_COUNTER_KEYS
        or any(type(value) is not int or value != 0 for value in counters.values())
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "forbidden operation counter is nonzero"
        )
    measurements = report["measurements"]
    if not isinstance(measurements, Mapping) or tuple(measurements) != MEASUREMENT_KEYS:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "measurement fields differ"
        )
    nonnegative_integer_fields = (
        "generated_input_bytes",
        "generated_output_bytes",
        "response_opens",
        "body_reads",
        "response_closes",
        "generated_resolver_calls",
        "retained_generated_payload_bytes",
    )
    if any(
        type(measurements[key]) is not int or measurements[key] < 0
        for key in nonnegative_integer_fields
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "measurement value differs"
        )
    runtime_seconds = measurements["runtime_seconds"]
    peak_rss_bytes = measurements["peak_RSS_bytes"]
    if (
        type(runtime_seconds) is not float
        or not 0 <= runtime_seconds <= MAX_RUNTIME_SECONDS
        or type(peak_rss_bytes) is not int
        or not 0 < peak_rss_bytes <= MAX_PEAK_RSS_BYTES
        or type(measurements["CPU_threads"]) is not int
        or measurements["CPU_threads"] != 1
        or type(measurements["workers"]) is not int
        or measurements["workers"] != 1
        or measurements["producer_is_causal"] is not None
        or measurements["end_to_end_latency_measured"] is not False
        or measurements["retained_generated_payload_bytes"] != 0
        or measurements["response_opens"] <= 0
        or measurements["body_reads"] <= 0
        or measurements["response_closes"] != measurements["response_opens"]
        or measurements["generated_resolver_calls"] <= 0
        or any(
            measurements[key] != expected
            for key, expected in DETERMINISTIC_MEASUREMENTS.items()
        )
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "measurement cap or invariant differs"
        )
    if not isinstance(report["warnings"], list) or tuple(report["warnings"]) != WARNINGS:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "warning inventory differs"
        )
    if (
        not isinstance(report["unavailable"], list)
        or tuple(report["unavailable"]) != UNAVAILABLE_FIELDS
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "unavailable-field inventory differs"
        )
    if (
        not isinstance(report["claim_boundary"], Mapping)
        or report["claim_boundary"] != CLAIM_BOUNDARY
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "claim boundary differs"
        )
    encoded = _canonical_json_bytes(report)
    if (
        len(encoded) > MAX_REPORT_BYTES
        or measurements["generated_output_bytes"] != len(encoded)
        or measurements["generated_input_bytes"] + len(encoded)
        > MAX_GENERATED_BYTES
    ):
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "public report size or cap differs"
        )

    def walk_public(value: object) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).casefold() in {
                    "url",
                    "path",
                    "query",
                    "signature",
                    "raw_headers",
                }:
                    raise NeuralPayloadAdmissionRefusal(
                        REFUSAL_IDS["output"], "ephemeral transport field escaped"
                    )
                walk_public(child)
        elif isinstance(value, list):
            for child in value:
                walk_public(child)
        elif isinstance(value, str) and value.startswith("https://"):
            raise NeuralPayloadAdmissionRefusal(
                REFUSAL_IDS["output"], "ephemeral transport value escaped"
            )

    walk_public(report)


def run_generated_qualification(
    repo_root: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the complete NPA1-G generated qualification exactly once per call."""

    _validate_frontier(repo_root)
    _validate_thread_environment(os.environ if environ is None else environ)
    started = clock()
    metrics = FixtureMetrics()
    first = _run_acceptance_replay("0123456789abcdef", metrics)
    second = _run_acceptance_replay("fedcba9876543210", metrics)
    if first != second:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["replay"], "stable transcript replay differs"
        )
    refusals = run_refusal_matrix(metrics)
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    if runtime_seconds < 0 or runtime_seconds > MAX_RUNTIME_SECONDS:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["resource"], "runtime cap failed"
        )
    if peak_rss_bytes <= 0 or peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["resource"], "RSS cap failed"
        )
    report: dict[str, Any] = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "accepted_generated_only_zero_network",
        "green_frontier": dict(GREEN_FRONTIER_EVIDENCE),
        "qualification": {
            "deterministic_replays": 2,
            "accepted_profiles_per_replay": len(first["accepted_profiles"]),
            "accepted_profile_ids": list(ACCEPTED_PROFILE_IDS),
            "stable_transcript_sha256": first["stable_transcript_sha256"],
            "stable_transcript_digests_equal": True,
            "signed_capability_refresh_accepted": True,
            "named_adversarial_families": len(refusals),
            "distinct_refusal_ids": len({row["refusal_id"] for row in refusals}),
            "refusals": refusals,
            "all_gates_passed": True,
        },
        "measurements": {
            "generated_input_bytes": metrics.generated_body_bytes_read,
            "generated_output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "response_opens": metrics.response_opens,
            "body_reads": metrics.body_reads,
            "response_closes": metrics.response_closes,
            "generated_resolver_calls": metrics.resolver_calls,
            "CPU_threads": 1,
            "workers": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
            "retained_generated_payload_bytes": 0,
        },
        "operation_counters": {key: 0 for key in OPERATION_COUNTER_KEYS},
        "warnings": list(WARNINGS),
        "unavailable": list(UNAVAILABLE_FIELDS),
        "claim_boundary": dict(CLAIM_BOUNDARY),
    }
    for _ in range(8):
        encoded = _canonical_json_bytes(report)
        size = len(encoded)
        if report["measurements"]["generated_output_bytes"] == size:
            break
        report["measurements"]["generated_output_bytes"] = size
    else:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["output"], "report size did not stabilize"
        )
    if metrics.generated_body_bytes_read + len(encoded) > MAX_GENERATED_BYTES:
        raise NeuralPayloadAdmissionRefusal(
            REFUSAL_IDS["resource"], "generated input plus output exceeds cap"
        )
    validate_public_report(report)
    return report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the generated-only NPA1-G plan after verifying its frontier."""

    _validate_frontier(repo_root)
    return {
        "protocol_id": PROTOCOL_ID,
        "status": "generated_only_ready",
        "deterministic_replays": 2,
        "minimum_named_adversarial_families": 24,
        "implemented_named_adversarial_families": len(REQUIRED_MUTATIONS),
        "maximum_runtime_seconds": MAX_RUNTIME_SECONDS,
        "maximum_peak_RSS_bytes": MAX_PEAK_RSS_BYTES,
        "maximum_generated_input_plus_output_bytes": MAX_GENERATED_BYTES,
        "CPU_threads": 1,
        "workers": 1,
        "network_client_present": False,
        "real_execution_command_present": False,
        "real_or_private_path_access_authorized": False,
        "scientific_claim_upgrade_authorized": False,
    }
