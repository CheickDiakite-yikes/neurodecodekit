"""Generated-only HTTP range and ZIP64 qualification for MARC1-CD1."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import io
import ipaddress
import json
import os
import re
import resource
import shutil
import stat
import struct
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urljoin, urlsplit


SCHEMA_VERSION = "0.1.0"
IMPLEMENTATION_STATUS = (
    "generated_mock_implementation_complete_registered_closeout_not_executed"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc1_central_directory_generated_result"
PRIVATE_SCHEMA_NAME = (
    "neurodecodekit.marc1_central_directory_generated_private_manifest"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc1_freewill_central_directory_contract.v0.json"
)
CONTRACT_SHA256 = "900417812d978030b7b92ad04befa4a7ce7f9e54fe479cd8c2c43ccfab1b8d69"
GREEN_CONTRACT_COMMIT = "cf6304385f61fc7713ae7fd4526d86e45e4c03e5"
GREEN_CONTRACT_CI_RUN_ID = 31_508_903_399
GREEN_CONTRACT_BASE_JOB_ID = 93_837_415_016
GREEN_CONTRACT_OPTIONAL_JOB_ID = 93_837_415_174

VIRTUAL_ARCHIVE_BYTES = 13_591_548_048
TAIL_BYTES = 128 * 1024
TAIL_START = VIRTUAL_ARCHIVE_BYTES - TAIL_BYTES
TAIL_END = VIRTUAL_ARCHIVE_BYTES - 1
MAX_DIRECTORY_BYTES = 16 * 1024 * 1024
MAX_DIRECTORY_ENTRIES = 250_000
MAX_METADATA_BYTES = 128 * 1024
MAX_MOCK_BODY_BYTES_PER_PATH = 17_039_360
MAX_MOCK_REQUESTS_PER_PATH = 5
MAX_GENERATED_FIXTURE_BYTES = 2 * 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024

METADATA_URL = "https://api.figshare.com/v2/articles/28632599/versions/1/files"
DOWNLOAD_URL = "https://ndownloader.figshare.com/files/57518986"
ARCHIVE_NAME = "Freewill_EEG_Reaching_Grasping.zip"
ARCHIVE_MD5 = "3b7c3039c5c9fb6abf1429a830301711"
FILE_ID = 57_518_986

EOCD_SIGNATURE = b"PK\x05\x06"
ZIP64_EOCD_SIGNATURE = b"PK\x06\x06"
ZIP64_LOCATOR_SIGNATURE = b"PK\x06\x07"
CENTRAL_ENTRY_SIGNATURE = b"PK\x01\x02"
ZIP64_EXTRA_ID = 0x0001

THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)

REFUSAL_IDS = (
    "MARC1CDG-F00-contract-artifact-or-green-proof-failure",
    "MARC1CDG-F01-machine-output-runtime-RSS-or-resource-failure",
    "MARC1CDG-F02-metadata-identity-shape-or-download-URL-failure",
    "MARC1CDG-F03-redirect-request-status-range-framing-encoding-or-byte-count-failure",
    "MARC1CDG-F04-EOCD-ZIP64-disk-offset-size-or-directory-bound-failure",
    "MARC1CDG-F05-central-entry-path-flag-method-kind-ZIP64-extra-or-duplicate-failure",
    "MARC1CDG-F06-privacy-deterministic-replay-hash-or-output-failure",
)
EXPECTED_ROUTE = "MARC1CDG-R1"

REQUIRED_MUTATIONS = (
    "contract_or_artifact_hash_mismatch",
    "metadata_status_or_JSON_shape",
    "metadata_missing_or_duplicate_selected_row",
    "metadata_name_size_or_MD5_drift",
    "metadata_link_only_or_download_URL",
    "redirect_loop_limit_or_order",
    "redirect_body_or_unsafe_destination",
    "unexpected_method_URL_header_or_extra_request",
    "archive_status_200_416_or_multipart",
    "archive_content_encoding_or_Content_Range",
    "archive_Content_Length_short_or_overlong_body",
    "tail_range_or_virtual_total_mismatch",
    "EOCD_missing_truncated_or_comment_mismatch",
    "EOCD_decoy_or_ambiguous_candidate",
    "ZIP64_locator_missing_misplaced_or_truncated",
    "ZIP64_record_outside_tail_or_wrong_end",
    "ZIP64_record_size_or_extensible_sector",
    "ZIP64_multidisk_or_classic_disagreement",
    "central_directory_zero_entry_or_size_cap",
    "central_directory_offset_overlap_or_bounds",
    "central_directory_status_range_or_length",
    "central_entry_signature_count_or_trailing_bytes",
    "duplicate_normalized_member_name",
    "unsafe_absolute_parent_or_separator_path",
    "invalid_UTF8_CP437_NFC_or_control_name",
    "encrypted_patched_strong_or_masked_entry",
    "unsupported_compression_or_flag",
    "symlink_device_socket_FIFO_or_kind",
    "invalid_directory_entry",
    "ZIP64_extra_missing_duplicate_truncated_or_surplus",
    "aggregate_privacy_leak_or_private_inspect",
    "output_symlink_overwrite_cap_or_replay_mismatch",
)

_CENTRAL_STRUCT = struct.Struct("<4s6H3I5H2I")
_EOCD_STRUCT = struct.Struct("<4s4H2IH")
_ZIP64_LOCATOR_STRUCT = struct.Struct("<4sIQI")
_ZIP64_EOCD_STRUCT = struct.Struct("<4sQ2H2I4Q")
_CONTENT_RANGE_RE = re.compile(r"bytes ([0-9]+)-([0-9]+)/([0-9]+)\Z")
_DECIMAL_RE = re.compile(r"(?:0|[1-9][0-9]*)\Z")
_MD5_RE = re.compile(r"[0-9a-f]{32}\Z")


class Marc1CentralDirectoryRefusal(RuntimeError):
    """Fail closed with one aggregate-safe route."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown MARC1-CD1 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class EntrySpec:
    name: str
    kind: str
    method: int
    compressed_size: int
    uncompressed_size: int
    local_header_offset: int
    flags: int = 0
    force_zip64: bool = False
    raw_name: bytes | None = None
    extra_override: bytes | None = None
    comment_bytes: int = 8192


@dataclass(frozen=True)
class GeneratedFixture:
    metadata_body: bytes
    tail_body: bytes
    central_directory_body: bytes
    entries: tuple[EntrySpec, ...]
    central_directory_offset: int
    zip64_eocd_offset: int
    zip64_position_in_tail: int
    locator_position_in_tail: int
    eocd_position_in_tail: int

    @property
    def materialized_bytes(self) -> int:
        return len(self.metadata_body) + len(self.tail_body) + len(
            self.central_directory_body
        )


@dataclass(frozen=True)
class TrailerInfo:
    entry_count: int
    central_directory_size: int
    central_directory_offset: int
    zip64_eocd_offset: int
    archive_comment_bytes: int

    @property
    def range_start(self) -> int:
        return self.central_directory_offset

    @property
    def range_end(self) -> int:
        return self.central_directory_offset + self.central_directory_size - 1


@dataclass(frozen=True)
class ParsedInventory:
    private_manifest: Mapping[str, Any]
    aggregate_summary: Mapping[str, Any]
    canonical_inventory_bytes: bytes


@dataclass(frozen=True)
class MockRequest:
    method: str
    url: str
    headers: Mapping[str, str]


class MockResponse(io.BytesIO):
    """Small response object used only by the injected generated transport."""

    def __init__(
        self,
        body: bytes,
        *,
        status: int,
        url: str,
        headers: Mapping[str, str],
    ) -> None:
        super().__init__(body)
        self.status = status
        self.url = url
        self.headers = dict(headers)
        self.body_length = len(body)
        self.read_calls = 0

    def read(self, size: int = -1) -> bytes:  # type: ignore[override]
        self.read_calls += 1
        return super().read(size)


@dataclass(frozen=True)
class ExpectedExchange:
    request: MockRequest
    response: MockResponse


class GeneratedTransport:
    """Exact request queue with no socket or live opener."""

    def __init__(self, exchanges: Sequence[ExpectedExchange]) -> None:
        self._exchanges = list(exchanges)
        self.requests: list[MockRequest] = []
        self.responses: list[MockResponse] = []

    def request(self, method: str, url: str, headers: Mapping[str, str]) -> MockResponse:
        request = MockRequest(method, url, _normalized_headers(headers))
        if not self._exchanges:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "unexpected extra request")
        expected = self._exchanges.pop(0)
        if request != expected.request:
            raise Marc1CentralDirectoryRefusal(
                REFUSAL_IDS[3], "method URL header or request order differs"
            )
        self.requests.append(request)
        self.responses.append(expected.response)
        return expected.response

    def assert_consumed(self) -> None:
        if self._exchanges:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "expected request missing")

    @property
    def body_read_calls(self) -> int:
        return sum(response.read_calls for response in self.responses)

    @property
    def returned_body_bytes(self) -> int:
        return sum(response.body_length for response in self.responses if response.read_calls)


@dataclass(frozen=True)
class PathResult:
    inventory: ParsedInventory
    request_count: int
    redirect_count: int
    body_response_count: int
    body_bytes: int
    body_read_calls: int


@dataclass(frozen=True)
class QualificationOutcome:
    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


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


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON value")


def _strict_json(payload: bytes, refusal_id: str) -> Any:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise Marc1CentralDirectoryRefusal(refusal_id, "JSON encoding differs")
    try:
        return json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise Marc1CentralDirectoryRefusal(refusal_id, "JSON is malformed") from exc


def load_registered_contract() -> dict[str, Any]:
    """Load and verify the exact remotely green generated-only contract."""

    path = _repo_root() / CONTRACT_RELATIVE_PATH
    if path.is_symlink() or not path.is_file():
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "contract is unavailable")
    if _sha256_file(path) != CONTRACT_SHA256:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "contract hash differs")
    value = _strict_json(path.read_bytes(), REFUSAL_IDS[0])
    if not isinstance(value, dict):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "contract root differs")
    expected = {
        "schema_name": "neurodecodekit.marc1_freewill_central_directory_contract",
        "schema_version": "0.1.0",
        "contract_id": "MARC-1-freewill-central-directory-generated-contract-v0",
        "status": "generated_mock_only_contract_frozen_implementation_not_started",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], f"contract {key} differs")
    interface = value.get("interface")
    if not isinstance(interface, dict) or interface.get("commands") != [
        "plan",
        "qualify",
        "inspect",
    ]:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "contract interface differs")
    if any(
        interface.get(key)
        for key in (
            "execute_command_available",
            "URL_or_host_argument_available",
            "HTTP_header_argument_available",
            "real_archive_path_argument_available",
            "participant_or_member_argument_available",
            "target_model_or_provider_argument_available",
            "network_opener_available",
        )
    ):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "live interface is enabled")
    flags = value.get("authorization_flags")
    counters = value.get("access_counters")
    if not isinstance(flags, dict) or any(flags.values()):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "authorization flag is true")
    if not isinstance(counters, dict) or any(counters.values()):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "access counter is nonzero")
    if value.get("required_mutations") != list(REQUIRED_MUTATIONS):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "mutation inventory differs")
    return value


def _generated_entries() -> tuple[EntrySpec, ...]:
    def directory(name: str, offset: int) -> EntrySpec:
        return EntrySpec(name, "directory", 0, 0, 0, offset)

    def regular(
        name: str,
        method: int,
        compressed: int,
        uncompressed: int,
        offset: int,
        **kwargs: Any,
    ) -> EntrySpec:
        return EntrySpec(
            name,
            "regular_file",
            method,
            compressed,
            uncompressed,
            offset,
            **kwargs,
        )
    return (
        directory("dataset/", 1_024),
        directory("dataset/sub-01/", 2_048),
        directory("dataset/sub-02/", 3_072),
        directory("dataset/derivatives/", 4_096),
        regular("dataset/README", 0, 1_024, 1_024, 1_000_000),
        regular("dataset/dataset_description.json", 8, 2_048, 4_096, 3_000_000),
        regular("dataset/participants.tsv", 8, 4_096, 8_192, 5_000_000, flags=1 << 3),
        regular("dataset/notes_\u00e9.txt", 8, 2_048, 3_072, 7_000_000, flags=1 << 11),
        regular("dataset/sub-01/sub-01_task-freewill_eeg.eeg", 8, 500_000, 750_000, 20_000_000),
        regular("dataset/sub-01/sub-01_task-freewill_eeg.vhdr", 8, 4_000, 8_000, 22_000_000),
        regular("dataset/sub-01/sub-01_task-freewill_eeg.vmrk", 8, 8_000, 16_000, 24_000_000),
        regular("dataset/sub-01/sub-01_task-freewill_events.tsv", 8, 12_000, 24_000, 26_000_000),
        regular("dataset/sub-01/sub-01_task-freewill_channels.tsv", 8, 6_000, 12_000, 28_000_000),
        regular(
            "dataset/sub-02/sub-02_task-freewill_eeg.eeg",
            8,
            4_300_000_000,
            5_000_000_000,
            5_500_000_000,
            force_zip64=True,
        ),
        regular("dataset/sub-02/sub-02_task-freewill_eeg.vhdr", 8, 4_000, 8_000, 40_000_000),
        regular("dataset/sub-02/sub-02_task-freewill_eeg.vmrk", 8, 8_000, 16_000, 42_000_000),
        regular("dataset/sub-02/sub-02_task-freewill_events.tsv", 8, 12_000, 24_000, 44_000_000),
        regular("dataset/sub-02/sub-02_task-freewill_channels.tsv", 8, 6_000, 12_000, 46_000_000),
    )


def _external_attributes(kind: str) -> int:
    if kind == "directory":
        return (stat.S_IFDIR | 0o755) << 16 | 0x10
    if kind == "regular_file":
        return (stat.S_IFREG | 0o644) << 16
    if kind == "symlink":
        return (stat.S_IFLNK | 0o777) << 16
    if kind == "device":
        return (stat.S_IFCHR | 0o600) << 16
    raise ValueError("unknown generated entry kind")


def _encode_entry(spec: EntrySpec) -> bytes:
    name = spec.raw_name
    if name is None:
        codec = "utf-8" if spec.flags & (1 << 11) else "cp437"
        name = spec.name.encode(codec)
    extra = b""
    compressed_32 = spec.compressed_size
    uncompressed_32 = spec.uncompressed_size
    offset_32 = spec.local_header_offset
    needed = 20
    if spec.force_zip64:
        compressed_32 = 0xFFFFFFFF
        uncompressed_32 = 0xFFFFFFFF
        offset_32 = 0xFFFFFFFF
        payload = struct.pack(
            "<QQQ",
            spec.uncompressed_size,
            spec.compressed_size,
            spec.local_header_offset,
        )
        extra = struct.pack("<HH", ZIP64_EXTRA_ID, len(payload)) + payload
        needed = 45
    if spec.extra_override is not None:
        extra = spec.extra_override
    comment = b"m" * spec.comment_bytes
    crc32 = binascii.crc32(name) & 0xFFFFFFFF
    fixed = _CENTRAL_STRUCT.pack(
        CENTRAL_ENTRY_SIGNATURE,
        (3 << 8) | 45,
        needed,
        spec.flags,
        spec.method,
        0,
        0,
        crc32,
        compressed_32,
        uncompressed_32,
        len(name),
        len(extra),
        len(comment),
        0,
        0,
        _external_attributes(spec.kind),
        offset_32,
    )
    return fixed + name + extra + comment


def _build_central_directory(entries: Sequence[EntrySpec]) -> bytes:
    return b"".join(_encode_entry(entry) for entry in entries)


def build_generated_fixture(entries: Sequence[EntrySpec] | None = None) -> GeneratedFixture:
    """Build small metadata ranges for the exact virtual archive identity."""

    specs = tuple(entries or _generated_entries())
    central = _build_central_directory(specs)
    comment = b"MARC1CDG-PK\x05\x06-decoy-comment"
    eocd = _EOCD_STRUCT.pack(
        EOCD_SIGNATURE,
        0,
        0,
        0xFFFF,
        0xFFFF,
        0xFFFFFFFF,
        0xFFFFFFFF,
        len(comment),
    ) + comment
    zip64_offset = VIRTUAL_ARCHIVE_BYTES - len(eocd) - _ZIP64_LOCATOR_STRUCT.size - _ZIP64_EOCD_STRUCT.size
    central_offset = zip64_offset - len(central)
    zip64 = _ZIP64_EOCD_STRUCT.pack(
        ZIP64_EOCD_SIGNATURE,
        44,
        (3 << 8) | 45,
        45,
        0,
        0,
        len(specs),
        len(specs),
        len(central),
        central_offset,
    )
    locator = _ZIP64_LOCATOR_STRUCT.pack(ZIP64_LOCATOR_SIGNATURE, 0, zip64_offset, 1)
    tail = bytearray(TAIL_BYTES)
    overlap_start = max(TAIL_START, central_offset)
    overlap_end = min(VIRTUAL_ARCHIVE_BYTES, central_offset + len(central))
    if overlap_start < overlap_end:
        source_start = overlap_start - central_offset
        target_start = overlap_start - TAIL_START
        tail[target_start : target_start + overlap_end - overlap_start] = central[
            source_start : source_start + overlap_end - overlap_start
        ]
    zip64_position = zip64_offset - TAIL_START
    locator_position = zip64_position + len(zip64)
    eocd_position = locator_position + len(locator)
    tail[zip64_position:locator_position] = zip64
    tail[locator_position:eocd_position] = locator
    tail[eocd_position : eocd_position + len(eocd)] = eocd
    metadata = _canonical_json_bytes(
        [
            {
                "computed_md5": ARCHIVE_MD5,
                "download_url": DOWNLOAD_URL,
                "id": FILE_ID,
                "is_link_only": False,
                "name": ARCHIVE_NAME,
                "size": VIRTUAL_ARCHIVE_BYTES,
                "supplied_md5": ARCHIVE_MD5,
            }
        ]
    )
    fixture = GeneratedFixture(
        metadata_body=metadata,
        tail_body=bytes(tail),
        central_directory_body=central,
        entries=specs,
        central_directory_offset=central_offset,
        zip64_eocd_offset=zip64_offset,
        zip64_position_in_tail=zip64_position,
        locator_position_in_tail=locator_position,
        eocd_position_in_tail=eocd_position,
    )
    if fixture.materialized_bytes > MAX_GENERATED_FIXTURE_BYTES:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "generated fixture exceeds cap")
    if not central_offset < TAIL_START:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "directory fixture is not range separated")
    return fixture


def _normalized_headers(headers: Mapping[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in headers.items():
        lowered = key.strip().lower()
        if not lowered or lowered in normalized or "\n" in value or "\r" in value:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "request header differs")
        normalized[lowered] = value.strip()
    return normalized


def _response_headers(headers: Mapping[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in headers.items():
        lowered = key.strip().lower()
        if not lowered or lowered in normalized or "\n" in value or "\r" in value:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "response header differs")
        normalized[lowered] = value.strip()
    return normalized


def _read_bounded_body(
    response: MockResponse,
    *,
    cap: int,
    expected_bytes: int | None,
    refusal_id: str,
) -> bytes:
    headers = _response_headers(response.headers)
    content_length = headers.get("content-length")
    if content_length is None or not _DECIMAL_RE.fullmatch(content_length):
        raise Marc1CentralDirectoryRefusal(refusal_id, "Content-Length is unavailable")
    declared = int(content_length)
    if declared > cap or (expected_bytes is not None and declared != expected_bytes):
        raise Marc1CentralDirectoryRefusal(refusal_id, "Content-Length differs")
    payload = bytearray()
    while len(payload) <= cap:
        chunk = response.read(min(64 * 1024, cap + 1 - len(payload)))
        if not chunk:
            break
        if not isinstance(chunk, bytes):
            raise Marc1CentralDirectoryRefusal(refusal_id, "response body is not bytes")
        payload.extend(chunk)
    if len(payload) > cap or len(payload) != declared:
        raise Marc1CentralDirectoryRefusal(refusal_id, "response byte count differs")
    if expected_bytes is not None and len(payload) != expected_bytes:
        raise Marc1CentralDirectoryRefusal(refusal_id, "exact response length differs")
    return bytes(payload)


def _validate_metadata_body(payload: bytes) -> str:
    value = _strict_json(payload, REFUSAL_IDS[2])
    if not isinstance(value, list):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "metadata root is not an array")
    rows = [row for row in value if isinstance(row, dict) and row.get("id") == FILE_ID]
    if len(rows) != 1:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "selected file row count differs")
    row = rows[0]
    required = {
        "id",
        "name",
        "size",
        "is_link_only",
        "download_url",
        "supplied_md5",
        "computed_md5",
    }
    if not required.issubset(row):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "metadata field is unavailable")
    if type(row["id"]) is not int or row["id"] != FILE_ID:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "file id differs")
    if row["name"] != ARCHIVE_NAME or type(row["size"]) is not int:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "name or size differs")
    if row["size"] != VIRTUAL_ARCHIVE_BYTES:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "archive size differs")
    if row["is_link_only"] is not False:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "selected file is link-only")
    for key in ("supplied_md5", "computed_md5"):
        if not isinstance(row[key], str) or not _MD5_RE.fullmatch(row[key]):
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "MD5 field differs")
        if row[key] != ARCHIVE_MD5:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "archive MD5 differs")
    if row["download_url"] != DOWNLOAD_URL:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "download URL differs")
    parsed = urlsplit(row["download_url"])
    if (
        parsed.scheme != "https"
        or parsed.hostname != "ndownloader.figshare.com"
        or parsed.path != "/files/57518986"
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "download URL is unsafe")
    return row["download_url"]


def _read_metadata_response(response: MockResponse) -> str:
    if response.status != 200:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "metadata status differs")
    headers = _response_headers(response.headers)
    encoding = headers.get("content-encoding")
    if encoding not in {None, "identity"}:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[2], "metadata encoding differs")
    payload = _read_bounded_body(
        response,
        cap=MAX_METADATA_BYTES,
        expected_bytes=None,
        refusal_id=REFUSAL_IDS[2],
    )
    return _validate_metadata_body(payload)


def _validate_redirect_destination(
    current_url: str,
    location: str,
    *,
    seen: set[str],
    resolver: Callable[[str], Sequence[str]],
) -> str:
    destination = urljoin(current_url, location)
    parsed = urlsplit(destination)
    try:
        port = parsed.port
    except ValueError as exc:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect port differs") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
        or port not in {None, 443}
    ):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect destination is unsafe")
    if destination in seen:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect loop detected")
    addresses = tuple(resolver(parsed.hostname))
    if not addresses:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect address unavailable")
    try:
        if not all(ipaddress.ip_address(address).is_global for address in addresses):
            raise Marc1CentralDirectoryRefusal(
                REFUSAL_IDS[3], "redirect address is not globally routable"
            )
    except ValueError as exc:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect address differs") from exc
    return destination


def _validate_redirect_response(response: MockResponse) -> str:
    headers = _response_headers(response.headers)
    if response.status not in {301, 302, 303, 307, 308}:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect status differs")
    if response.body_length != 0 or headers.get("content-length") not in {None, "0"}:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect body is not empty")
    if "transfer-encoding" in headers:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect framing differs")
    location = headers.get("location")
    if not location:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect Location is unavailable")
    return location


def _read_range_response(
    response: MockResponse,
    *,
    expected_start: int,
    expected_end: int,
) -> bytes:
    if response.status != 206:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "archive status is not 206")
    headers = _response_headers(response.headers)
    content_type = headers.get("content-type", "")
    if content_type.lower().startswith("multipart/"):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "multipart response is forbidden")
    if "transfer-encoding" in headers:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "archive framing differs")
    if headers.get("content-encoding") not in {None, "identity"}:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "archive encoding differs")
    raw_range = headers.get("content-range")
    match = _CONTENT_RANGE_RE.fullmatch(raw_range or "")
    if not match:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "Content-Range differs")
    start, end, total = (int(value) for value in match.groups())
    if (start, end, total) != (expected_start, expected_end, VIRTUAL_ARCHIVE_BYTES):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "Content-Range identity differs")
    expected_bytes = expected_end - expected_start + 1
    return _read_bounded_body(
        response,
        cap=expected_bytes,
        expected_bytes=expected_bytes,
        refusal_id=REFUSAL_IDS[3],
    )


def _fetch_range(
    transport: GeneratedTransport,
    *,
    initial_url: str,
    range_start: int,
    range_end: int,
    resolver: Callable[[str], Sequence[str]],
    maximum_redirects: int = 2,
) -> tuple[bytes, str, int]:
    headers = {
        "accept-encoding": "identity",
        "range": f"bytes={range_start}-{range_end}",
    }
    current = initial_url
    seen = {current}
    redirects = 0
    while True:
        response = transport.request("GET", current, headers)
        if response.status in {301, 302, 303, 307, 308}:
            if redirects >= maximum_redirects:
                raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "redirect limit exceeded")
            location = _validate_redirect_response(response)
            current = _validate_redirect_destination(
                current,
                location,
                seen=seen,
                resolver=resolver,
            )
            seen.add(current)
            redirects += 1
            continue
        return (
            _read_range_response(
                response,
                expected_start=range_start,
                expected_end=range_end,
            ),
            current,
            redirects,
        )


def _find_eocd(tail: bytes) -> tuple[int, tuple[Any, ...]]:
    candidates: list[tuple[int, tuple[Any, ...]]] = []
    position = len(tail)
    while True:
        position = tail.rfind(EOCD_SIGNATURE, 0, position)
        if position < 0:
            break
        if position + _EOCD_STRUCT.size <= len(tail):
            fields = _EOCD_STRUCT.unpack_from(tail, position)
            comment_length = fields[-1]
            if position + _EOCD_STRUCT.size + comment_length == len(tail):
                candidates.append((position, fields))
        if position == 0:
            break
    if len(candidates) != 1:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "EOCD candidate count differs")
    return candidates[0]


def parse_zip64_trailer(tail: bytes, *, tail_start: int = TAIL_START) -> TrailerInfo:
    """Parse the fixed generated archive tail without a full ZIP."""

    if len(tail) != TAIL_BYTES or tail_start != TAIL_START:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "tail range differs")
    eocd_position, eocd = _find_eocd(tail)
    (
        signature,
        disk_number,
        directory_disk,
        classic_entries_disk,
        classic_entries_total,
        classic_directory_size,
        classic_directory_offset,
        comment_bytes,
    ) = eocd
    if signature != EOCD_SIGNATURE or disk_number != 0 or directory_disk != 0:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "classic EOCD disk differs")
    locator_position = eocd_position - _ZIP64_LOCATOR_STRUCT.size
    if locator_position < 0:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 locator is unavailable")
    locator = _ZIP64_LOCATOR_STRUCT.unpack_from(tail, locator_position)
    locator_signature, zip64_disk, zip64_offset, total_disks = locator
    if locator_signature != ZIP64_LOCATOR_SIGNATURE:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 locator differs")
    if zip64_disk != 0 or total_disks != 1:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 archive is not single-disk")
    if zip64_offset < tail_start:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 record starts before tail")
    zip64_position = zip64_offset - tail_start
    if zip64_position < 0 or zip64_position + _ZIP64_EOCD_STRUCT.size > len(tail):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 record is outside tail")
    zip64 = _ZIP64_EOCD_STRUCT.unpack_from(tail, zip64_position)
    (
        zip64_signature,
        zip64_remaining_size,
        _version_made,
        _version_needed,
        current_disk,
        start_disk,
        entries_disk,
        entries_total,
        directory_size,
        directory_offset,
    ) = zip64
    if zip64_signature != ZIP64_EOCD_SIGNATURE or zip64_remaining_size != 44:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 record size differs")
    if zip64_position + 12 + zip64_remaining_size != locator_position:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 record end differs")
    if current_disk != 0 or start_disk != 0 or entries_disk != entries_total:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "ZIP64 disk or entry count differs")
    if not 1 <= entries_total <= MAX_DIRECTORY_ENTRIES:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "directory entry count exceeds cap")
    if not 46 <= directory_size <= MAX_DIRECTORY_BYTES:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "directory size exceeds cap")
    if directory_size // entries_total < 46:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "directory bytes per entry differ")
    if directory_offset < 0 or directory_offset + directory_size > zip64_offset:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "directory bounds differ")
    comparisons = (
        (classic_entries_disk, entries_disk, 0xFFFF),
        (classic_entries_total, entries_total, 0xFFFF),
        (classic_directory_size, directory_size, 0xFFFFFFFF),
        (classic_directory_offset, directory_offset, 0xFFFFFFFF),
    )
    if any(classic != sentinel and classic != actual for classic, actual, sentinel in comparisons):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[4], "classic and ZIP64 values differ")
    return TrailerInfo(
        entry_count=entries_total,
        central_directory_size=directory_size,
        central_directory_offset=directory_offset,
        zip64_eocd_offset=zip64_offset,
        archive_comment_bytes=comment_bytes,
    )


def _parse_extra_fields(extra: bytes) -> dict[int, bytes]:
    fields: dict[int, bytes] = {}
    position = 0
    while position < len(extra):
        if position + 4 > len(extra):
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "extra field is truncated")
        field_id, size = struct.unpack_from("<HH", extra, position)
        position += 4
        if position + size > len(extra) or field_id in fields:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "extra field differs")
        fields[field_id] = extra[position : position + size]
        position += size
    return fields


def _resolve_zip64_values(
    *,
    compressed_32: int,
    uncompressed_32: int,
    offset_32: int,
    disk_16: int,
    extra: bytes,
) -> tuple[int, int, int, int, bool]:
    needs = (
        uncompressed_32 == 0xFFFFFFFF,
        compressed_32 == 0xFFFFFFFF,
        offset_32 == 0xFFFFFFFF,
        disk_16 == 0xFFFF,
    )
    fields = _parse_extra_fields(extra)
    payload = fields.get(ZIP64_EXTRA_ID)
    if not any(needs):
        if payload is not None:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "surplus ZIP64 extra")
        return compressed_32, uncompressed_32, offset_32, disk_16, False
    if payload is None:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "ZIP64 extra is unavailable")
    position = 0

    def take(size: int) -> int:
        nonlocal position
        if position + size > len(payload):
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "ZIP64 extra is truncated")
        format_code = "<Q" if size == 8 else "<I"
        value = struct.unpack_from(format_code, payload, position)[0]
        position += size
        return value

    uncompressed = take(8) if needs[0] else uncompressed_32
    compressed = take(8) if needs[1] else compressed_32
    local_offset = take(8) if needs[2] else offset_32
    disk = take(4) if needs[3] else disk_16
    if position != len(payload):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "ZIP64 extra has surplus bytes")
    return compressed, uncompressed, local_offset, disk, True


def _validate_member_name(name: str) -> None:
    if not name or name != unicodedata.normalize("NFC", name):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member name is not NFC")
    if (
        "\x00" in name
        or "\\" in name
        or any(unicodedata.category(character) == "Cc" for character in name)
    ):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member name contains unsafe text")
    if re.match(r"^[A-Za-z]:", name) or name.startswith("/") or "//" in name:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member path is absolute or repeated")
    raw_path = name[:-1] if name.endswith("/") else name
    raw_parts = raw_path.split("/")
    parts = PurePosixPath(raw_path).parts
    if (
        not raw_parts
        or any(part in {"", ".", ".."} for part in raw_parts)
        or tuple(raw_parts) != parts
    ):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member path component is unsafe")


def _classify_entry(version_made: int, external_attributes: int, name: str) -> str:
    host = version_made >> 8
    if host == 3:
        mode = (external_attributes >> 16) & 0xFFFF
        if stat.S_ISREG(mode):
            return "regular_file"
        if stat.S_ISDIR(mode):
            return "directory"
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member kind is unsupported")
    if external_attributes & 0x10 or name.endswith("/"):
        return "directory"
    return "regular_file"


def parse_central_directory(body: bytes, trailer: TrailerInfo) -> ParsedInventory:
    """Parse only central-directory metadata and return private/aggregate views."""

    if len(body) != trailer.central_directory_size:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "directory body length differs")
    records: list[dict[str, Any]] = []
    names: set[str] = set()
    intervals: list[tuple[int, int]] = []
    position = 0
    for _index in range(trailer.entry_count):
        if position + _CENTRAL_STRUCT.size > len(body):
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "central entry is truncated")
        fields = _CENTRAL_STRUCT.unpack_from(body, position)
        (
            signature,
            version_made,
            _version_needed,
            flags,
            method,
            _modified_time,
            _modified_date,
            crc32,
            compressed_32,
            uncompressed_32,
            name_length,
            extra_length,
            comment_length,
            disk_start,
            _internal_attributes,
            external_attributes,
            local_offset_32,
        ) = fields
        if signature != CENTRAL_ENTRY_SIGNATURE:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "central entry signature differs")
        variable_start = position + _CENTRAL_STRUCT.size
        variable_end = variable_start + name_length + extra_length + comment_length
        if variable_end > len(body) or name_length == 0:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "central variable fields differ")
        name_bytes = body[variable_start : variable_start + name_length]
        extra_start = variable_start + name_length
        extra = body[extra_start : extra_start + extra_length]
        codec = "utf-8" if flags & (1 << 11) else "cp437"
        try:
            name = name_bytes.decode(codec, errors="strict")
        except UnicodeDecodeError as exc:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member name decoding failed") from exc
        _validate_member_name(name)
        if name in names:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "normalized member name repeats")
        names.add(name)
        forbidden_bits = flags & ~((1 << 3) | (1 << 11))
        if forbidden_bits or flags & ((1 << 0) | (1 << 5) | (1 << 6) | (1 << 13)):
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member flags are unsupported")
        if method not in {0, 8}:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "compression method is unsupported")
        compressed, uncompressed, local_offset, resolved_disk, used_zip64 = (
            _resolve_zip64_values(
                compressed_32=compressed_32,
                uncompressed_32=uncompressed_32,
                offset_32=local_offset_32,
                disk_16=disk_start,
                extra=extra,
            )
        )
        if resolved_disk != 0:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member disk differs")
        kind = _classify_entry(version_made, external_attributes, name)
        if kind == "directory":
            if not name.endswith("/") or compressed != 0 or uncompressed != 0 or method != 0:
                raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "directory entry differs")
        elif name.endswith("/"):
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "regular member ends in slash")
        if local_offset < 0 or local_offset + compressed > trailer.central_directory_offset:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member interval exceeds directory")
        if compressed:
            intervals.append((local_offset, local_offset + compressed))
        records.append(
            {
                "CRC32": f"{crc32:08x}",
                "ZIP64_extra_used": used_zip64,
                "compressed_size": compressed,
                "compression_method": method,
                "entry_kind": kind,
                "external_attributes": external_attributes,
                "general_purpose_flags": flags,
                "local_header_offset": local_offset,
                "member_name": name,
                "uncompressed_size": uncompressed,
                "version_made_by": version_made,
            }
        )
        position = variable_end
    if position != len(body):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "directory has trailing bytes")
    for previous, current in zip(sorted(intervals), sorted(intervals)[1:]):
        if previous[1] > current[0]:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[5], "member intervals overlap")
    canonical_rows = []
    for record in records:
        row = dict(record)
        name = row.pop("member_name")
        row["member_name_sha256"] = _sha256_bytes(
            b"neurodecodekit.marc1cd.member-name.v0\0" + name.encode("utf-8")
        )
        canonical_rows.append(row)
    canonical_bytes = _canonical_json_bytes(canonical_rows)
    manifest = {
        "schema_name": PRIVATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "proof_posture": "generated_private_fixture_only",
        "entries": records,
    }
    kinds = Counter(record["entry_kind"] for record in records)
    methods = Counter(str(record["compression_method"]) for record in records)
    summary = {
        "archive_comment_bytes": trailer.archive_comment_bytes,
        "central_directory_bytes": trailer.central_directory_size,
        "directory_entries": kinds.get("directory", 0),
        "entry_count": len(records),
        "inventory_sha256": _sha256_bytes(canonical_bytes),
        "method_counts": dict(sorted(methods.items())),
        "private_manifest_sha256": _sha256_bytes(_canonical_json_bytes(manifest)),
        "regular_file_entries": kinds.get("regular_file", 0),
        "total_compressed_member_bytes": sum(record["compressed_size"] for record in records),
        "total_uncompressed_member_bytes": sum(
            record["uncompressed_size"] for record in records
        ),
        "virtual_archive_bytes": VIRTUAL_ARCHIVE_BYTES,
        "whole_archive_materialized_bytes": 0,
        "ZIP64_member_entries": sum(record["ZIP64_extra_used"] for record in records),
    }
    return ParsedInventory(
        private_manifest=manifest,
        aggregate_summary=summary,
        canonical_inventory_bytes=canonical_bytes,
    )


def _range_headers(start: int, end: int, total: int = VIRTUAL_ARCHIVE_BYTES) -> dict[str, str]:
    return {
        "Content-Encoding": "identity",
        "Content-Length": str(end - start + 1),
        "Content-Range": f"bytes {start}-{end}/{total}",
        "Content-Type": "application/zip",
    }


def _request(method: str, url: str, headers: Mapping[str, str]) -> MockRequest:
    return MockRequest(method, url, _normalized_headers(headers))


def build_generated_transport(
    fixture: GeneratedFixture,
    *,
    redirect_count: int,
) -> tuple[GeneratedTransport, Callable[[str], Sequence[str]]]:
    """Build an exact direct or two-bodyless-redirect fixture path."""

    if redirect_count not in {0, 2}:
        raise ValueError("generated redirect count must be zero or two")
    exchanges: list[ExpectedExchange] = [
        ExpectedExchange(
            _request(
                "GET",
                METADATA_URL,
                {"accept": "application/json", "accept-encoding": "identity"},
            ),
            MockResponse(
                fixture.metadata_body,
                status=200,
                url=METADATA_URL,
                headers={
                    "Content-Encoding": "identity",
                    "Content-Length": str(len(fixture.metadata_body)),
                    "Content-Type": "application/json",
                },
            ),
        )
    ]
    range_request_headers = {
        "accept-encoding": "identity",
        "range": f"bytes={TAIL_START}-{TAIL_END}",
    }
    terminal_url = DOWNLOAD_URL
    if redirect_count:
        first = "https://cdn-a.example.net/freewill/57518986"
        second = "https://cdn-b.example.net/freewill/57518986"
        exchanges.extend(
            [
                ExpectedExchange(
                    _request("GET", DOWNLOAD_URL, range_request_headers),
                    MockResponse(
                        b"",
                        status=302,
                        url=DOWNLOAD_URL,
                        headers={"Content-Length": "0", "Location": first},
                    ),
                ),
                ExpectedExchange(
                    _request("GET", first, range_request_headers),
                    MockResponse(
                        b"",
                        status=307,
                        url=first,
                        headers={"Content-Length": "0", "Location": second},
                    ),
                ),
            ]
        )
        terminal_url = second
    exchanges.append(
        ExpectedExchange(
            _request("GET", terminal_url, range_request_headers),
            MockResponse(
                fixture.tail_body,
                status=206,
                url=terminal_url,
                headers=_range_headers(TAIL_START, TAIL_END),
            ),
        )
    )
    directory_start = fixture.central_directory_offset
    directory_end = directory_start + len(fixture.central_directory_body) - 1
    exchanges.append(
        ExpectedExchange(
            _request(
                "GET",
                terminal_url,
                {
                    "accept-encoding": "identity",
                    "range": f"bytes={directory_start}-{directory_end}",
                },
            ),
            MockResponse(
                fixture.central_directory_body,
                status=206,
                url=terminal_url,
                headers=_range_headers(directory_start, directory_end),
            ),
        )
    )

    def resolver(hostname: str) -> Sequence[str]:
        values = {
            "cdn-a.example.net": ("8.8.8.8",),
            "cdn-b.example.net": ("1.1.1.1",),
        }
        return values.get(hostname, ("8.8.4.4",))

    return GeneratedTransport(exchanges), resolver


def run_generated_path(fixture: GeneratedFixture, *, redirect_count: int) -> PathResult:
    transport, resolver = build_generated_transport(fixture, redirect_count=redirect_count)
    metadata_response = transport.request(
        "GET",
        METADATA_URL,
        {"accept": "application/json", "accept-encoding": "identity"},
    )
    download_url = _read_metadata_response(metadata_response)
    tail, terminal_url, redirects = _fetch_range(
        transport,
        initial_url=download_url,
        range_start=TAIL_START,
        range_end=TAIL_END,
        resolver=resolver,
    )
    trailer = parse_zip64_trailer(tail)
    directory, directory_terminal_url, directory_redirects = _fetch_range(
        transport,
        initial_url=terminal_url,
        range_start=trailer.range_start,
        range_end=trailer.range_end,
        resolver=resolver,
        maximum_redirects=0,
    )
    if directory_terminal_url != terminal_url or directory_redirects:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[3], "directory endpoint drifted")
    inventory = parse_central_directory(directory, trailer)
    transport.assert_consumed()
    if len(transport.requests) > MAX_MOCK_REQUESTS_PER_PATH:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "mock request cap exceeded")
    if transport.returned_body_bytes > MAX_MOCK_BODY_BYTES_PER_PATH:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "mock body cap exceeded")
    return PathResult(
        inventory=inventory,
        request_count=len(transport.requests),
        redirect_count=redirects,
        body_response_count=sum(response.read_calls > 0 for response in transport.responses),
        body_bytes=transport.returned_body_bytes,
        body_read_calls=transport.body_read_calls,
    )


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], Any],
) -> str:
    try:
        operation()
    except Marc1CentralDirectoryRefusal as exc:
        if exc.refusal_id != expected_route:
            raise Marc1CentralDirectoryRefusal(
                REFUSAL_IDS[6], f"mutation {name} used the wrong route"
            ) from exc
        return exc.refusal_id
    raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], f"mutation {name} did not refuse")


def _metadata_response(body: bytes, *, status: int = 200) -> MockResponse:
    return MockResponse(
        body,
        status=status,
        url=METADATA_URL,
        headers={"Content-Encoding": "identity", "Content-Length": str(len(body))},
    )


def _mutated_metadata(**updates: Any) -> bytes:
    row = {
        "computed_md5": ARCHIVE_MD5,
        "download_url": DOWNLOAD_URL,
        "id": FILE_ID,
        "is_link_only": False,
        "name": ARCHIVE_NAME,
        "size": VIRTUAL_ARCHIVE_BYTES,
        "supplied_md5": ARCHIVE_MD5,
    }
    row.update(updates)
    return _canonical_json_bytes([row])


def _mutate_zip64_field(fixture: GeneratedFixture, field_offset: int, value: int, fmt: str) -> bytes:
    tail = bytearray(fixture.tail_body)
    struct.pack_into(fmt, tail, fixture.zip64_position_in_tail + field_offset, value)
    return bytes(tail)


def _validate_contract_mapping(value: Mapping[str, Any]) -> None:
    if value.get("contract_id") != "MARC-1-freewill-central-directory-generated-contract-v0":
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[0], "contract mapping differs")


def _bounded_output_bytes(report_bytes: bytes, manifest_bytes: bytes) -> int:
    total = len(report_bytes) + len(manifest_bytes)
    if total > MAX_OUTPUT_BYTES:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "combined output exceeds cap")
    return total


def _walk_public(value: Any) -> None:
    forbidden_keys = {
        "member_name",
        "local_header_offset",
        "download_url",
        "redirect_url",
        "query_string",
        "response_header_value",
        "per_member_crc32",
        "entries",
    }
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in forbidden_keys:
                raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "aggregate key leaks private data")
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)
    elif isinstance(value, str) and ("://" in value or "dataset/" in value):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "aggregate string leaks private data")


def validate_public_report(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    expected_keys = {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "green_contract",
        "archive_summary",
        "transport_summary",
        "measurements",
        "mutation_summary",
        "access_counters",
        "acceptance_gates",
        "route",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    if set(report) != expected_keys:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "aggregate field set differs")
    if report.get("schema_name") != REPORT_SCHEMA_NAME or report.get("route") != EXPECTED_ROUTE:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "aggregate identity differs")
    counters = report.get("access_counters")
    gates = report.get("acceptance_gates")
    mutations = report.get("mutation_summary")
    if not isinstance(counters, dict) or any(counters.values()):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "aggregate counter is nonzero")
    if not isinstance(gates, dict) or not gates or not all(gates.values()):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "acceptance gate failed")
    if not isinstance(mutations, dict) or mutations.get("passed_count") != 32:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "mutation count differs")


def run_required_mutations(fixture: GeneratedFixture) -> dict[str, str]:
    """Exercise every frozen generated refusal without hostile allocations."""

    routes: dict[str, str] = {}

    def record(name: str, route: str, operation: Callable[[], Any]) -> None:
        routes[name] = _expect_refusal(name, route, operation)

    record(
        REQUIRED_MUTATIONS[0],
        REFUSAL_IDS[0],
        lambda: _validate_contract_mapping({"contract_id": "wrong"}),
    )
    record(
        REQUIRED_MUTATIONS[1],
        REFUSAL_IDS[2],
        lambda: _read_metadata_response(_metadata_response(b"{}", status=500)),
    )
    record(
        REQUIRED_MUTATIONS[2],
        REFUSAL_IDS[2],
        lambda: _validate_metadata_body(_canonical_json_bytes([])),
    )
    record(
        REQUIRED_MUTATIONS[3],
        REFUSAL_IDS[2],
        lambda: _validate_metadata_body(_mutated_metadata(size=VIRTUAL_ARCHIVE_BYTES - 1)),
    )
    record(
        REQUIRED_MUTATIONS[4],
        REFUSAL_IDS[2],
        lambda: _validate_metadata_body(_mutated_metadata(is_link_only=True)),
    )
    record(
        REQUIRED_MUTATIONS[5],
        REFUSAL_IDS[3],
        lambda: _validate_redirect_destination(
            DOWNLOAD_URL,
            DOWNLOAD_URL,
            seen={DOWNLOAD_URL},
            resolver=lambda _host: ("8.8.8.8",),
        ),
    )
    record(
        REQUIRED_MUTATIONS[6],
        REFUSAL_IDS[3],
        lambda: _validate_redirect_response(
            MockResponse(
                b"x",
                status=302,
                url=DOWNLOAD_URL,
                headers={"Content-Length": "1", "Location": "http://127.0.0.1/x"},
            )
        ),
    )
    transport, _resolver = build_generated_transport(fixture, redirect_count=0)
    record(
        REQUIRED_MUTATIONS[7],
        REFUSAL_IDS[3],
        lambda: transport.request("POST", METADATA_URL, {}),
    )
    record(
        REQUIRED_MUTATIONS[8],
        REFUSAL_IDS[3],
        lambda: _read_range_response(
            MockResponse(
                b"",
                status=200,
                url=DOWNLOAD_URL,
                headers={"Content-Length": "0"},
            ),
            expected_start=TAIL_START,
            expected_end=TAIL_END,
        ),
    )
    record(
        REQUIRED_MUTATIONS[9],
        REFUSAL_IDS[3],
        lambda: _read_range_response(
            MockResponse(
                fixture.tail_body,
                status=206,
                url=DOWNLOAD_URL,
                headers={
                    **_range_headers(TAIL_START, TAIL_END),
                    "Content-Encoding": "gzip",
                },
            ),
            expected_start=TAIL_START,
            expected_end=TAIL_END,
        ),
    )
    short_headers = _range_headers(TAIL_START, TAIL_END)
    short_headers["Content-Length"] = str(TAIL_BYTES - 1)
    record(
        REQUIRED_MUTATIONS[10],
        REFUSAL_IDS[3],
        lambda: _read_range_response(
            MockResponse(
                fixture.tail_body[:-1],
                status=206,
                url=DOWNLOAD_URL,
                headers=short_headers,
            ),
            expected_start=TAIL_START,
            expected_end=TAIL_END,
        ),
    )
    wrong_total = _range_headers(TAIL_START, TAIL_END, VIRTUAL_ARCHIVE_BYTES + 1)
    record(
        REQUIRED_MUTATIONS[11],
        REFUSAL_IDS[3],
        lambda: _read_range_response(
            MockResponse(
                fixture.tail_body,
                status=206,
                url=DOWNLOAD_URL,
                headers=wrong_total,
            ),
            expected_start=TAIL_START,
            expected_end=TAIL_END,
        ),
    )
    missing_eocd = bytearray(fixture.tail_body)
    missing_eocd[fixture.eocd_position_in_tail : fixture.eocd_position_in_tail + 4] = b"NOPE"
    record(
        REQUIRED_MUTATIONS[12],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(bytes(missing_eocd)),
    )
    ambiguous = bytearray(fixture.tail_body)
    decoy_position = fixture.eocd_position_in_tail - 64
    decoy_comment = len(ambiguous) - decoy_position - _EOCD_STRUCT.size
    ambiguous[decoy_position : decoy_position + _EOCD_STRUCT.size] = _EOCD_STRUCT.pack(
        EOCD_SIGNATURE,
        0,
        0,
        0xFFFF,
        0xFFFF,
        0xFFFFFFFF,
        0xFFFFFFFF,
        decoy_comment,
    )
    record(
        REQUIRED_MUTATIONS[13],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(bytes(ambiguous)),
    )
    missing_locator = bytearray(fixture.tail_body)
    missing_locator[fixture.locator_position_in_tail : fixture.locator_position_in_tail + 4] = b"NOPE"
    record(
        REQUIRED_MUTATIONS[14],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(bytes(missing_locator)),
    )
    outside_zip64 = bytearray(fixture.tail_body)
    struct.pack_into(
        "<Q",
        outside_zip64,
        fixture.locator_position_in_tail + 8,
        TAIL_START - 1,
    )
    record(
        REQUIRED_MUTATIONS[15],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(bytes(outside_zip64)),
    )
    record(
        REQUIRED_MUTATIONS[16],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(_mutate_zip64_field(fixture, 4, 45, "<Q")),
    )
    record(
        REQUIRED_MUTATIONS[17],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(_mutate_zip64_field(fixture, 16, 1, "<I")),
    )
    record(
        REQUIRED_MUTATIONS[18],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(_mutate_zip64_field(fixture, 24, 0, "<Q")),
    )
    record(
        REQUIRED_MUTATIONS[19],
        REFUSAL_IDS[4],
        lambda: parse_zip64_trailer(
            _mutate_zip64_field(fixture, 48, fixture.zip64_eocd_offset, "<Q")
        ),
    )
    directory_end = fixture.central_directory_offset + len(fixture.central_directory_body) - 1
    bad_directory_headers = _range_headers(fixture.central_directory_offset, directory_end)
    bad_directory_headers["Content-Range"] = (
        f"bytes {fixture.central_directory_offset + 1}-{directory_end}/{VIRTUAL_ARCHIVE_BYTES}"
    )
    record(
        REQUIRED_MUTATIONS[20],
        REFUSAL_IDS[3],
        lambda: _read_range_response(
            MockResponse(
                fixture.central_directory_body,
                status=206,
                url=DOWNLOAD_URL,
                headers=bad_directory_headers,
            ),
            expected_start=fixture.central_directory_offset,
            expected_end=directory_end,
        ),
    )
    trailer = parse_zip64_trailer(fixture.tail_body)
    bad_signature = bytearray(fixture.central_directory_body)
    bad_signature[:4] = b"NOPE"
    record(
        REQUIRED_MUTATIONS[21],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(bytes(bad_signature), trailer),
    )
    duplicate_entries = list(fixture.entries)
    duplicate_entries[1] = replace(duplicate_entries[1], name=duplicate_entries[0].name)
    duplicate_body = _build_central_directory(duplicate_entries)
    record(
        REQUIRED_MUTATIONS[22],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            duplicate_body,
            replace(trailer, central_directory_size=len(duplicate_body)),
        ),
    )
    unsafe_entries = list(fixture.entries)
    unsafe_entries[4] = replace(unsafe_entries[4], name="../escape")
    unsafe_body = _build_central_directory(unsafe_entries)
    record(
        REQUIRED_MUTATIONS[23],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            unsafe_body,
            replace(trailer, central_directory_size=len(unsafe_body)),
        ),
    )
    invalid_name_entries = list(fixture.entries)
    invalid_name_entries[4] = replace(
        invalid_name_entries[4], raw_name=b"bad-\xff", flags=1 << 11
    )
    invalid_name_body = _build_central_directory(invalid_name_entries)
    record(
        REQUIRED_MUTATIONS[24],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            invalid_name_body,
            replace(trailer, central_directory_size=len(invalid_name_body)),
        ),
    )
    encrypted_entries = list(fixture.entries)
    encrypted_entries[4] = replace(encrypted_entries[4], flags=1)
    encrypted_body = _build_central_directory(encrypted_entries)
    record(
        REQUIRED_MUTATIONS[25],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            encrypted_body,
            replace(trailer, central_directory_size=len(encrypted_body)),
        ),
    )
    unsupported_entries = list(fixture.entries)
    unsupported_entries[4] = replace(unsupported_entries[4], method=99)
    unsupported_body = _build_central_directory(unsupported_entries)
    record(
        REQUIRED_MUTATIONS[26],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            unsupported_body,
            replace(trailer, central_directory_size=len(unsupported_body)),
        ),
    )
    symlink_entries = list(fixture.entries)
    symlink_entries[4] = replace(symlink_entries[4], kind="symlink")
    symlink_body = _build_central_directory(symlink_entries)
    record(
        REQUIRED_MUTATIONS[27],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            symlink_body,
            replace(trailer, central_directory_size=len(symlink_body)),
        ),
    )
    invalid_directory_entries = list(fixture.entries)
    invalid_directory_entries[0] = replace(invalid_directory_entries[0], name="dataset")
    invalid_directory_body = _build_central_directory(invalid_directory_entries)
    record(
        REQUIRED_MUTATIONS[28],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            invalid_directory_body,
            replace(trailer, central_directory_size=len(invalid_directory_body)),
        ),
    )
    bad_zip64_entries = list(fixture.entries)
    bad_zip64_entries[13] = replace(bad_zip64_entries[13], extra_override=b"")
    bad_zip64_body = _build_central_directory(bad_zip64_entries)
    record(
        REQUIRED_MUTATIONS[29],
        REFUSAL_IDS[5],
        lambda: parse_central_directory(
            bad_zip64_body,
            replace(trailer, central_directory_size=len(bad_zip64_body)),
        ),
    )
    record(
        REQUIRED_MUTATIONS[30],
        REFUSAL_IDS[6],
        lambda: _walk_public({"member_name": "private"}),
    )
    record(
        REQUIRED_MUTATIONS[31],
        REFUSAL_IDS[6],
        lambda: _bounded_output_bytes(b"x" * (MAX_OUTPUT_BYTES + 1), b""),
    )
    if tuple(routes) != REQUIRED_MUTATIONS:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "mutation execution order differs")
    return routes


def _assert_output_destination(output_dir: Path) -> None:
    if output_dir.exists() or output_dir.is_symlink():
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "output directory exists")
    parent = output_dir.parent
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "output parent is unavailable")
    if stat.S_ISLNK(os.lstat(parent).st_mode):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "output parent is a symlink")


def _assert_resources(runtime_seconds: float, peak_rss_bytes: int) -> None:
    if runtime_seconds > MAX_RUNTIME_SECONDS:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "runtime exceeds cap")
    if peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "peak RSS exceeds cap")
    for key in THREAD_ENV_KEYS:
        if os.environ.get(key) not in {None, "1"}:
            raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "thread setting exceeds one")


def _write_outputs(
    output_dir: Path,
    report: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> tuple[Path, Path, int]:
    _assert_output_destination(output_dir)
    report_bytes = _canonical_json_bytes(report)
    manifest_bytes = _canonical_json_bytes(manifest)
    total = _bounded_output_bytes(report_bytes, manifest_bytes)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        report_path = stage / "marc1_central_directory_generated_report.v0.json"
        manifest_path = stage / "marc1_central_directory_generated_private_manifest.v0.json"
        report_path.write_bytes(report_bytes)
        manifest_path.write_bytes(manifest_bytes)
        os.replace(stage, output_dir)
    except Exception as exc:
        shutil.rmtree(stage, ignore_errors=True)
        if isinstance(exc, Marc1CentralDirectoryRefusal):
            raise
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[1], "output write failed") from exc
    return (
        output_dir / "marc1_central_directory_generated_report.v0.json",
        output_dir / "marc1_central_directory_generated_private_manifest.v0.json",
        total,
    )


def _build_report(
    direct: PathResult,
    redirected: PathResult,
    mutations: Mapping[str, str],
    *,
    generated_input_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    return {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_mock_qualification",
        "proof_posture": "generated_mock_metadata_only_no_scientific_value",
        "green_contract": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "archive_summary": dict(direct.inventory.aggregate_summary),
        "transport_summary": {
            "direct_path_body_bytes": direct.body_bytes,
            "direct_path_body_read_calls": direct.body_read_calls,
            "direct_path_requests": direct.request_count,
            "direct_path_redirects": direct.redirect_count,
            "metadata_response_bodies_per_path": 1,
            "mock_only": True,
            "range_response_bodies_per_path": 2,
            "redirected_path_body_bytes": redirected.body_bytes,
            "redirected_path_body_read_calls": redirected.body_read_calls,
            "redirected_path_requests": redirected.request_count,
            "redirected_path_redirects": redirected.redirect_count,
            "terminal_status": 206,
        },
        "measurements": {
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes": 0,
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
        },
        "mutation_summary": {
            "required_count": len(REQUIRED_MUTATIONS),
            "passed_count": len(mutations),
            "mutation_names": list(REQUIRED_MUTATIONS),
            "route_counts": dict(sorted(Counter(mutations.values()).items())),
        },
        "access_counters": {
            "live_metadata_requests": 0,
            "live_metadata_bytes": 0,
            "archive_HEAD_requests": 0,
            "archive_range_requests": 0,
            "archive_range_bytes": 0,
            "network_redirects": 0,
            "whole_archive_downloads": 0,
            "real_archive_path_operations": 0,
            "member_local_header_reads": 0,
            "member_payload_reads": 0,
            "member_payload_bytes": 0,
            "signal_sample_reads": 0,
            "event_or_onset_reads": 0,
            "target_or_label_reads": 0,
            "real_derivative_rows": 0,
            "parameter_update_fits": 0,
            "model_inference_calls": 0,
            "prediction_sets": 0,
            "prediction_freezes": 0,
            "target_deliveries": 0,
            "scores": 0,
            "scientific_claim_upgrades": 0,
        },
        "acceptance_gates": {
            "exact_generated_metadata_identity": True,
            "valid_direct_and_two_redirect_paths": True,
            "exact_tail_and_virtual_total": True,
            "decoy_resistant_EOCD": True,
            "complete_in_tail_ZIP64": True,
            "directory_range_derived_before_response": True,
            "exact_18_entry_inventory": True,
            "safe_supported_member_classification": True,
            "zero_local_header_and_member_content_reads": True,
            "aggregate_private_output_separation": True,
            "all_32_mutations_refused": True,
            "deterministic_replay_and_manifest_hashes": True,
            "resource_and_output_caps": True,
            "all_live_real_model_score_and_claim_counters_zero": True,
        },
        "route": EXPECTED_ROUTE,
        "warnings": [
            "Generated and mocked ranges contain no public or human data.",
            "Live range support and final transport identity remain unavailable.",
            "Whole-archive MD5 member CRC local headers and payload integrity remain unavailable.",
            "End-to-end latency was not measured.",
            "MARC1CDG-R1 cannot authorize a live request member acquisition or scientific claim.",
        ],
        "unavailable_fields": [
            "live range support",
            "live final host",
            "live ETag and Last-Modified",
            "real entry count and central-directory size",
            "real member inventory",
            "whole-archive MD5 verification",
            "member CRC32 verification",
            "local-header consistency",
            "member payload integrity",
            "human signal event target or model result",
            "end-to-end latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A dependency-free generated and mocked executor validates exact HTTP range and "
                "ZIP64 central-directory mechanics for a virtual 13.59 GB archive with zero "
                "member-content access."
            ),
            "scientific_claim_not_established": (
                "Generated transport and archive metadata contain no human neural signal event "
                "target or model result and establish no neural effect or decoding capability."
            ),
        },
    }


def qualify_generated_central_directory(
    output_dir: str | Path,
    *,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run one bounded generated/mock qualification and write two outputs."""

    start = time.perf_counter()
    output = Path(output_dir)
    _assert_output_destination(output)
    load_registered_contract()
    first_fixture = build_generated_fixture()
    second_fixture = build_generated_fixture()
    direct = run_generated_path(first_fixture, redirect_count=0)
    redirected = run_generated_path(first_fixture, redirect_count=2)
    replay = run_generated_path(second_fixture, redirect_count=0)
    replay_redirected = run_generated_path(second_fixture, redirect_count=2)
    if (
        first_fixture != second_fixture
        or direct.inventory.canonical_inventory_bytes
        != redirected.inventory.canonical_inventory_bytes
        or direct.inventory.canonical_inventory_bytes
        != replay.inventory.canonical_inventory_bytes
        or direct.inventory.canonical_inventory_bytes
        != replay_redirected.inventory.canonical_inventory_bytes
        or _canonical_json_bytes(direct.inventory.private_manifest)
        != _canonical_json_bytes(replay.inventory.private_manifest)
    ):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "generated replay differs")
    mutations = run_required_mutations(first_fixture)
    deterministic_first = _build_report(
        direct,
        redirected,
        mutations,
        generated_input_bytes=first_fixture.materialized_bytes,
        runtime_seconds=0.0,
        peak_rss_bytes=0,
    )
    deterministic_second = _build_report(
        replay,
        replay_redirected,
        mutations,
        generated_input_bytes=second_fixture.materialized_bytes,
        runtime_seconds=0.0,
        peak_rss_bytes=0,
    )
    if _canonical_json_bytes(deterministic_first) != _canonical_json_bytes(
        deterministic_second
    ):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "canonical report replay differs")
    runtime = time.perf_counter() - start
    peak_rss = rss_probe()
    _assert_resources(runtime, peak_rss)
    generated_input_bytes = first_fixture.materialized_bytes
    report = _build_report(
        direct,
        redirected,
        mutations,
        generated_input_bytes=generated_input_bytes,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
    )
    manifest_bytes = _canonical_json_bytes(direct.inventory.private_manifest)
    provisional = _bounded_output_bytes(_canonical_json_bytes(report), manifest_bytes)
    report["measurements"]["generated_output_bytes"] = provisional
    final_total = _bounded_output_bytes(_canonical_json_bytes(report), manifest_bytes)
    if final_total != provisional:
        report["measurements"]["generated_output_bytes"] = final_total
        final_total = _bounded_output_bytes(_canonical_json_bytes(report), manifest_bytes)
    validate_public_report(report)
    report_path, manifest_path, written_total = _write_outputs(
        output,
        report,
        direct.inventory.private_manifest,
    )
    if written_total != final_total:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "written output count differs")
    return QualificationOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=manifest_path,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=written_total,
    )


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Load and validate only an aggregate MARC1-CD1 generated report."""

    report_path = Path(path)
    if report_path.is_symlink() or not report_path.is_file():
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "report path is unavailable")
    if report_path.stat().st_size > MAX_OUTPUT_BYTES:
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "report exceeds cap")
    value = _strict_json(report_path.read_bytes(), REFUSAL_IDS[6])
    if not isinstance(value, dict):
        raise Marc1CentralDirectoryRefusal(REFUSAL_IDS[6], "report root differs")
    validate_public_report(value)
    return value


def build_plan_summary() -> dict[str, Any]:
    """Return the frozen generated/mock plan without creating range bytes."""

    contract = load_registered_contract()
    return {
        "contract_id": contract["contract_id"],
        "contract_status": contract["status"],
        "status": IMPLEMENTATION_STATUS,
        "commands": contract["interface"]["commands"],
        "virtual_archive_bytes": VIRTUAL_ARCHIVE_BYTES,
        "generated_entry_count": contract["generated_virtual_archive"]["entry_count"],
        "mutation_count": len(REQUIRED_MUTATIONS),
        "network_requests": 0,
        "real_archive_bytes": 0,
        "member_payload_bytes": 0,
        "scientific_claim": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_central_directory_audit",
        description="Generated-only MARC1-CD1 HTTP range and ZIP64 qualification.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the frozen generated/mock plan.")
    qualify = subparsers.add_parser("qualify", help="Run one generated/mock qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate generated report.")
    inspect.add_argument("report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "plan":
            print(_canonical_json_bytes(build_plan_summary()).decode("ascii"), end="")
            return 0
        if arguments.command == "qualify":
            outcome = qualify_generated_central_directory(arguments.output_dir)
            print(_canonical_json_bytes(outcome.report).decode("ascii"), end="")
            return 0
        if arguments.command == "inspect":
            report = inspect_generated_report(arguments.report)
            print(_canonical_json_bytes(report).decode("ascii"), end="")
            return 0
        parser.print_help()
        return 0
    except Marc1CentralDirectoryRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
