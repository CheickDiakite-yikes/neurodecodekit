"""Bounded, sibling-blind IACKD BrainVision header inventory audit."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
LEDGER_SCHEMA_NAME = "neurodecodekit.iackd_channel_inventory_ledger"
IMPLEMENTATION_SCHEMA_NAME = "neurodecodekit.iackd_channel_inventory_implementation"
DECISION_SCHEMA_NAME = "neurodecodekit.iackd_channel_inventory_authorization_decision"
CONTRACT_RELATIVE_PATH = Path("registries/iackd_channel_inventory_contract.v0.json")
INVENTORY_RELATIVE_PATH = Path("registries/iackd_openneuro_metadata_inventory.v0.json")
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/iackd_channel_inventory_implementation.v0.json"
)
DECISION_RELATIVE_PATH = Path(
    "registries/iackd_channel_inventory_authorization_decision.v0.json"
)
REAL_OUTPUT_RELATIVE_PATH = Path(
    ".codex_work/iackd_channel_inventory/public/iackd_channel_inventory_ledger.v0.json"
)
REAL_CONSUMED_RELATIVE_PATH = Path(
    ".codex_work/iackd_channel_inventory/private/execution_consumed.v0.json"
)
CONTRACT_SHA256 = "d85ff8ca05c69ce707a52e44d503fc7ec6e5d2a05d1d191203f07820442647fd"
CONTRACT_BYTES = 13_287
INVENTORY_SHA256 = "aeaa4928192cca9086fcb0abf4711147c68a68ef5c5aacda2ebc67d162a1ef19"
REGISTRATION_COMMIT = "0e52278aaa1d15e70f4baab7b21ab1c96eb37f67"
REGISTRATION_CI_RUN_ID = 31_412_667_060
REGISTRATION_BASE_JOB_ID = 93_534_203_368
REGISTRATION_OPTIONAL_JOB_ID = 93_534_203_385
MAX_LOCKED_JSON_BYTES = 2 * 1024 * 1024
MAX_VHDR_BYTES = 4096
MINIMUM_PLAUSIBLE_LEDGER_BYTES = 2048
FORMAT_PREAMBLE = "Brain Vision Data Exchange Header File Version 1.0"
REQUIRED_SECTIONS = ("Common Infos", "Binary Infos", "Channel Infos")
REQUIRED_COMMON_KEYS = (
    "DataFile",
    "MarkerFile",
    "DataFormat",
    "DataOrientation",
    "NumberOfChannels",
    "SamplingInterval",
)
REQUIRED_BINARY_KEYS = ("BinaryFormat",)
PUBLIC_NAME_ALLOWLIST = ("M1", "M2", "HEOG", "VEOG", "HEO", "VEO", "TRIGGER")
CANONICAL_GATE_NAMES = ("M1", "M2", "HEOG", "VEOG")
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
HEAVY_MODULE_ROOTS = frozenset(
    {
        "braindecode",
        "huggingface_hub",
        "mne",
        "moabb",
        "numpy",
        "pyriemann",
        "scipy",
        "sklearn",
        "torch",
        "zarr",
    }
)
REFUSAL_IDS = (
    "IACKDH-F01_missing_exact_real_content_decision",
    "IACKDH-F02_registration_implementation_inventory_or_green_proof_mismatch",
    "IACKDH-F03_wrong_object_set_order_URL_or_source_version",
    "IACKDH-F04_redirect_retry_substitution_or_rerun",
    "IACKDH-F05_response_status_length_ETag_compression_or_size_mismatch",
    "IACKDH-F06_decode_codepage_preamble_section_or_key_failure",
    "IACKDH-F07_channel_count_index_name_or_uniqueness_failure",
    "IACKDH-F08_unsafe_sibling_reference_or_attempted_sibling_resolution",
    "IACKDH-F09_raw_comment_unallowlisted_name_path_or_protected_output",
    "IACKDH-F10_local_bundle_companion_sample_event_trajectory_or_target_access",
    "IACKDH-F11_cache_split_feature_model_inference_training_or_scoring_operation",
    "IACKDH-F12_dependency_provider_language_model_stream_device_or_hardware_operation",
    "IACKDH-F13_malformed_or_nondeterministic_signature_aggregation",
    "IACKDH-F14_resource_thread_network_disk_or_output_cap_breach",
    "IACKDH-F15_overwrite_retained_raw_payload_deletion_move_upload_or_release",
    "IACKDH-F16_scientific_decoding_realtime_portable_assistive_or_clinical_overclaim",
)
CHANNEL_KEY_RE = re.compile(r"Ch([1-9][0-9]*)\Z", re.IGNORECASE)
SECTION_RE = re.compile(r"\[([^\r\n]+)\]\Z")
HEX32_RE = re.compile(r"[0-9a-f]{32}\Z")
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
PUBLIC_LEDGER_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "provenance",
        "measurements",
        "signature_groups",
        "first_header_diagnosis",
        "all_headers_identical",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "acceptance_gate_results",
        "diagnostic_route",
        "claim_boundary",
    }
)


class HeaderAuditRefusal(RuntimeError):
    """Fail closed with one stable, non-sensitive refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown IACKD-H1 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class RealExecutionEvidence:
    """Immutable green evidence required by the future one-shot real stage."""

    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    authorization_commit: str
    authorization_ci_run_id: int
    authorization_base_job_id: int
    authorization_optional_job_id: int
    authorization_decision_sha256: str
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class HeaderAuditOutcome:
    """One completed synthetic or authorized real header audit."""

    ledger: Mapping[str, Any]
    ledger_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_output_bytes: int


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise HeaderAuditRefusal(REFUSAL_IDS[3], "redirect is forbidden")


class FixtureResponse(io.BytesIO):
    """Small urllib-like response used only by generated fixtures."""

    def __init__(
        self,
        payload: bytes,
        *,
        url: str,
        etag: str,
        status: int = 200,
        content_encoding: str | None = None,
        transfer_encoding: str | None = None,
    ) -> None:
        super().__init__(payload)
        self._url = url
        self.status = status
        self.headers = {
            "Content-Length": str(len(payload)),
            "ETag": f'"{etag}"',
        }
        if content_encoding is not None:
            self.headers["Content-Encoding"] = content_encoding
        if transfer_encoding is not None:
            self.headers["Transfer-Encoding"] = transfer_encoding

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status


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
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_locked_json(
    path: Path,
    *,
    expected_sha256: str | None,
    maximum_bytes: int = MAX_LOCKED_JSON_BYTES,
) -> tuple[dict[str, Any], str, int]:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "locked JSON is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "locked JSON is not a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "locked JSON no-follow open failed") from exc
    try:
        payload = b""
        while len(payload) <= maximum_bytes:
            chunk = os.read(descriptor, min(64 * 1024, maximum_bytes + 1 - len(payload)))
            if not chunk:
                break
            payload += chunk
    finally:
        os.close(descriptor)
    if len(payload) > maximum_bytes:
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "locked JSON exceeds its byte cap")
    observed_hash = _sha256_bytes(payload)
    if expected_sha256 is not None and observed_hash != expected_sha256:
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "locked JSON identity mismatch")
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_strict_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "locked JSON is malformed") from exc
    if not isinstance(value, dict):
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "locked JSON root is not an object")
    return value, observed_hash, len(payload)


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely-green IACKD-H1 contract."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract, _, observed_bytes = _read_locked_json(
        root / CONTRACT_RELATIVE_PATH,
        expected_sha256=CONTRACT_SHA256,
    )
    if observed_bytes != CONTRACT_BYTES:
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "registered contract byte count mismatch")
    if (
        contract.get("schema_name") != "neurodecodekit.iackd_channel_inventory_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("contract_id") != "IACKD-H1-header-inventory-audit-v0"
        or tuple(contract.get("public_name_allowlist", ())) != PUBLIC_NAME_ALLOWLIST
        or tuple(contract.get("refusal_ids", ())) != REFUSAL_IDS
        or contract.get("ordered_stages", {}).get("stage_R", {}).get("currently_authorized")
        is not False
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "registered contract structure mismatch")
    return contract


def load_registered_inventory(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load only the committed metadata inventory; no payload path is consulted."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    inventory, _, _ = _read_locked_json(
        root / INVENTORY_RELATIVE_PATH,
        expected_sha256=INVENTORY_SHA256,
    )
    if (
        inventory.get("schema_name") != "neurodecodekit.iackd_openneuro_metadata_inventory"
        or inventory.get("dataset", {}).get("accession") != "ds006840"
        or inventory.get("dataset", {}).get("version") != "1.0.0"
        or inventory.get("access_boundary", {}).get("payload_url_gets") != 0
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "registered inventory structure mismatch")
    return inventory


def _safe_relative_object_path(value: str) -> str:
    path = Path(value)
    if (
        not value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in value
        or "\x00" in value
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[2], "object path is not a safe relative path")
    return value


def registered_header_rows(
    contract: Mapping[str, Any], inventory: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Reconstruct the exact 128-header surface from committed metadata."""

    rows = sorted(
        (
            {
                "path": _safe_relative_object_path(str(row.get("path", ""))),
                "size_bytes": int(row.get("size_bytes", -1)),
                "etag": str(row.get("etag", "")).lower(),
                "last_modified": str(row.get("last_modified", "")),
            }
            for row in inventory.get("selected_objects", ())
            if str(row.get("path", "")).endswith(".vhdr")
        ),
        key=lambda row: row["path"],
    )
    source = contract["source"]
    if (
        len(rows) != int(source["expected_object_count"])
        or sum(row["size_bytes"] for row in rows) != int(source["expected_total_body_bytes"])
        or min(row["size_bytes"] for row in rows) != int(source["minimum_object_bytes"])
        or max(row["size_bytes"] for row in rows) != int(source["maximum_object_bytes"])
        or sorted({row["size_bytes"] for row in rows}) != source["unique_object_sizes"]
        or rows[0] != source["first_deterministic_object"]
        or len({row["path"] for row in rows}) != len(rows)
        or any(HEX32_RE.fullmatch(row["etag"]) is None for row in rows)
        or any(row["size_bytes"] <= 0 or row["size_bytes"] > MAX_VHDR_BYTES for row in rows)
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[2], "registered header inventory mismatch")
    return rows


def _ascii_codepage_declarations(payload: bytes) -> tuple[str, ...]:
    declarations: list[str] = []
    current_section: bytes | None = None
    for raw_line in payload.splitlines():
        candidate = raw_line[3:] if raw_line.startswith(b"\xef\xbb\xbf") else raw_line
        stripped = candidate.strip(b" \t")
        if stripped.startswith(b"[") and stripped.endswith(b"]"):
            try:
                current_section = stripped[1:-1].strip().lower()
            except UnicodeError as exc:
                raise HeaderAuditRefusal(
                    REFUSAL_IDS[5], "section declaration is not ASCII-safe"
                ) from exc
            continue
        if current_section != b"common infos":
            continue
        if not stripped.lower().startswith(b"codepage"):
            continue
        if any(byte < 0x20 or byte > 0x7E for byte in stripped) or stripped.count(b"=") != 1:
            raise HeaderAuditRefusal(REFUSAL_IDS[5], "Codepage declaration is malformed")
        key, value = (part.strip() for part in stripped.split(b"=", 1))
        if key.lower() != b"codepage" or not value:
            raise HeaderAuditRefusal(REFUSAL_IDS[5], "Codepage declaration is malformed")
        declarations.append(value.decode("ascii"))
    return tuple(declarations)


def _decode_vhdr(payload: bytes) -> tuple[str, str]:
    if not isinstance(payload, bytes) or not payload:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "VHDR body is empty or not bytes")
    declarations = _ascii_codepage_declarations(payload)
    normalized = {value.casefold().replace("_", "-") for value in declarations}
    if len(normalized) > 1:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "Codepage declarations conflict")
    declared = next(iter(normalized), None)
    has_bom = payload.startswith(b"\xef\xbb\xbf")
    if declared not in {None, "utf-8", "utf8", "windows-1252", "cp1252"}:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "Codepage is unsupported")
    if has_bom and declared in {"windows-1252", "cp1252"}:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "UTF-8 BOM conflicts with Codepage")
    if declared in {"windows-1252", "cp1252"}:
        codec, canonical = "cp1252", "windows-1252"
    elif has_bom:
        codec, canonical = "utf-8-sig", "UTF-8-BOM"
    else:
        codec, canonical = "utf-8", "UTF-8"
    try:
        text = payload.decode(codec, errors="strict")
    except UnicodeDecodeError as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "strict VHDR decoding failed") from exc
    if "\ufffd" in text:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "replacement decoding is forbidden")
    for character in text:
        if character in "\r\n\t":
            continue
        if unicodedata.category(character).startswith("C"):
            raise HeaderAuditRefusal(REFUSAL_IDS[5], "decoded control character is forbidden")
    return text, canonical


def _parse_required_sections(text: str) -> dict[str, dict[str, str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != FORMAT_PREAMBLE:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "exact VHDR preamble is missing")
    sections: dict[str, dict[str, str]] = {}
    required_by_fold = {name.casefold(): name for name in REQUIRED_SECTIONS}
    seen_required: set[str] = set()
    current_required: str | None = None
    inside_section = False
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(";"):
            continue
        match = SECTION_RE.fullmatch(stripped)
        if match:
            inside_section = True
            folded = match.group(1).strip().casefold()
            current_required = required_by_fold.get(folded)
            if current_required is not None:
                if current_required in seen_required:
                    raise HeaderAuditRefusal(REFUSAL_IDS[5], "duplicate required section")
                seen_required.add(current_required)
                sections[current_required] = {}
            continue
        if not inside_section:
            raise HeaderAuditRefusal(REFUSAL_IDS[5], "content appeared before a VHDR section")
        if current_required is None:
            continue
        if stripped.count("=") != 1:
            raise HeaderAuditRefusal(REFUSAL_IDS[5], "required-section row is malformed")
        key, value = (part.strip() for part in stripped.split("=", 1))
        if not key or any(existing.casefold() == key.casefold() for existing in sections[current_required]):
            raise HeaderAuditRefusal(REFUSAL_IDS[5], "required-section key is empty or duplicate")
        sections[current_required][key] = value
    if set(sections) != set(REQUIRED_SECTIONS):
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "required VHDR section is missing")
    return sections


def _casefold_lookup(values: Mapping[str, str], key: str) -> str:
    matches = [value for candidate, value in values.items() if candidate.casefold() == key.casefold()]
    if len(matches) != 1 or not matches[0]:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "required VHDR key is missing or empty")
    return matches[0]


def _assert_inert_basename(value: str) -> None:
    if (
        not value
        or value in {".", ".."}
        or value.startswith(("/", "~"))
        or "/" in value
        or "\\" in value
        or "\x00" in value
        or "://" in value
        or re.match(r"[A-Za-z]:", value)
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[7], "sibling reference is not an inert basename")


def _canonical_decimal(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _parse_channel_names(values: Mapping[str, str], declared_count: int) -> list[str]:
    rows: dict[int, str] = {}
    for key, value in values.items():
        match = CHANNEL_KEY_RE.fullmatch(key)
        if match is None:
            raise HeaderAuditRefusal(REFUSAL_IDS[6], "unexpected Channel Infos key")
        index = int(match.group(1))
        if index in rows:
            raise HeaderAuditRefusal(REFUSAL_IDS[6], "duplicate channel index")
        fields = value.split(",")
        if len(fields) != 4:
            raise HeaderAuditRefusal(REFUSAL_IDS[6], "channel declaration must have four fields")
        name = unicodedata.normalize("NFC", fields[0].replace(r"\1", ",").strip())
        if not name or any(unicodedata.category(char).startswith("C") for char in name):
            raise HeaderAuditRefusal(REFUSAL_IDS[6], "channel name is empty or unsafe")
        rows[index] = name
    expected = list(range(1, declared_count + 1))
    if sorted(rows) != expected:
        raise HeaderAuditRefusal(REFUSAL_IDS[6], "channel table is missing or noncontiguous")
    ordered = [rows[index] for index in expected]
    if len(set(ordered)) != len(ordered):
        raise HeaderAuditRefusal(REFUSAL_IDS[6], "normalized channel names are not unique")
    return ordered


def parse_vhdr_bytes(payload: bytes) -> dict[str, Any]:
    """Parse only declarations needed for the registered aggregate signature."""

    text, codepage = _decode_vhdr(payload)
    sections = _parse_required_sections(text)
    common = sections["Common Infos"]
    binary = sections["Binary Infos"]
    for key in REQUIRED_COMMON_KEYS:
        _casefold_lookup(common, key)
    for key in REQUIRED_BINARY_KEYS:
        _casefold_lookup(binary, key)
    _assert_inert_basename(_casefold_lookup(common, "DataFile"))
    _assert_inert_basename(_casefold_lookup(common, "MarkerFile"))
    for key in ("DataFormat", "DataOrientation"):
        if not _casefold_lookup(common, key).strip():
            raise HeaderAuditRefusal(REFUSAL_IDS[5], "required declaration is empty")
    if not _casefold_lookup(binary, "BinaryFormat").strip():
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "required binary declaration is empty")
    try:
        declared_count = int(_casefold_lookup(common, "NumberOfChannels"), 10)
    except ValueError as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[6], "declared channel count is malformed") from exc
    if declared_count <= 0:
        raise HeaderAuditRefusal(REFUSAL_IDS[6], "declared channel count must be positive")
    try:
        interval = Decimal(_casefold_lookup(common, "SamplingInterval"))
    except InvalidOperation as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "sampling interval is malformed") from exc
    if not interval.is_finite() or interval <= 0:
        raise HeaderAuditRefusal(REFUSAL_IDS[5], "sampling interval must be finite and positive")
    with localcontext() as context:
        context.prec = 28
        sampling_rate = Decimal(1_000_000) / interval
    names = _parse_channel_names(sections["Channel Infos"], declared_count)
    return {
        "strict_codepage": codepage,
        "declared_channel_count": declared_count,
        "sampling_interval_microseconds": _canonical_decimal(interval),
        "sampling_rate_hz": _canonical_decimal(sampling_rate),
        "normalized_channel_names": names,
    }


def build_channel_signature(parsed: Mapping[str, Any]) -> dict[str, Any]:
    """Create the public-safe signature for one parsed header."""

    names = list(parsed["normalized_channel_names"])
    folded = {name.casefold() for name in names}
    fields = {
        "declared_channel_count": int(parsed["declared_channel_count"]),
        "ordered_normalized_channel_names_sha256": _sha256_bytes(
            _canonical_json_bytes(names)
        ),
        "sampling_interval_microseconds": str(parsed["sampling_interval_microseconds"]),
        "sampling_rate_hz": str(parsed["sampling_rate_hz"]),
        "allowlisted_name_presence": {
            name: name.casefold() in folded for name in PUBLIC_NAME_ALLOWLIST
        },
    }
    return {"signature_id": _sha256_bytes(_canonical_json_bytes(fields)), **fields}


def route_signatures(signatures: Sequence[Mapping[str, Any]], *, failed: bool = False) -> str:
    """Apply the frozen IACKD-H1 diagnostic router in exact order."""

    if failed or not signatures:
        return "IACKDH-R0"
    if len(signatures) > 1:
        return "IACKDH-R5"
    first = signatures[0]
    count_ok = int(first["declared_channel_count"]) == 36
    presence = first["allowlisted_name_presence"]
    names_ok = all(bool(presence[name]) for name in CANONICAL_GATE_NAMES)
    if count_ok and names_ok:
        return "IACKDH-R1"
    if not count_ok and not names_ok:
        return "IACKDH-R4"
    if not count_ok:
        return "IACKDH-R2"
    return "IACKDH-R3"


def _normalize_etag(value: str) -> str:
    normalized = value.strip().strip('"').lower()
    if HEX32_RE.fullmatch(normalized) is None:
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "response ETag is malformed")
    return normalized


def _response_header(stream: BinaryIO, name: str) -> str | None:
    headers = getattr(stream, "headers", None)
    return None if headers is None else headers.get(name)


def _response_url(stream: BinaryIO) -> str | None:
    getter = getattr(stream, "geturl", None)
    return None if getter is None else str(getter())


def _response_status(stream: BinaryIO) -> int | None:
    value = getattr(stream, "status", None)
    if value is None:
        getter = getattr(stream, "getcode", None)
        value = None if getter is None else getter()
    return None if value is None else int(value)


@contextmanager
def _managed_stream(stream: BinaryIO) -> Iterator[BinaryIO]:
    try:
        yield stream
    finally:
        stream.close()


def _validate_response(stream: BinaryIO, *, url: str, row: Mapping[str, Any]) -> None:
    if _response_status(stream) != 200:
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "response status is not 200")
    if _response_url(stream) != url:
        raise HeaderAuditRefusal(REFUSAL_IDS[3], "response URL differs from request URL")
    length = _response_header(stream, "Content-Length")
    try:
        parsed_length = int(length) if length is not None else -1
    except ValueError as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "Content-Length is malformed") from exc
    if parsed_length != int(row["size_bytes"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "Content-Length mismatch")
    etag = _response_header(stream, "ETag")
    if etag is None or _normalize_etag(etag) != row["etag"]:
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "response ETag mismatch")
    content_encoding = (_response_header(stream, "Content-Encoding") or "identity").casefold()
    transfer_encoding = (_response_header(stream, "Transfer-Encoding") or "identity").casefold()
    if content_encoding != "identity" or transfer_encoding != "identity":
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "response transformation is forbidden")


def _read_exact_body(stream: BinaryIO, expected_bytes: int, maximum_bytes: int) -> bytes:
    if expected_bytes > maximum_bytes:
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "registered body exceeds read cap")
    payload = stream.read(expected_bytes + 1)
    if len(payload) != expected_bytes:
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "response body length mismatch")
    return payload


def _peak_rss_bytes() -> int:
    import resource

    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "one-thread environment is required")


def _base_access_counters(*, synthetic: bool) -> dict[str, int]:
    return {
        "synthetic_VHDR_requests": 0,
        "real_VHDR_requests": 0,
        "real_VHDR_body_bytes": 0,
        "real_header_parses": 0,
        "local_IACKD_path_stats_or_opens": 0,
        "sibling_resolutions_stats_hashes_or_opens": 0,
        "signal_sample_reads": 0,
        "marker_or_event_reads": 0,
        "trajectory_reads": 0,
        "target_or_label_reads": 0,
        "cache_or_split_operations": 0,
        "feature_extraction_runs": 0,
        "model_or_checkpoint_loads": 0,
        "training_or_parameter_update_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "scoring_runs": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
        "synthetic_mode": int(synthetic),
    }


def _assert_forbidden_counters_zero(counters: Mapping[str, int], *, synthetic: bool) -> None:
    permitted = {"synthetic_mode", "synthetic_VHDR_requests"}
    if not synthetic:
        permitted |= {"real_VHDR_requests", "real_VHDR_body_bytes", "real_header_parses"}
    for name, value in counters.items():
        if name not in permitted and value != 0:
            if name in {"local_IACKD_path_stats_or_opens", "sibling_resolutions_stats_hashes_or_opens"}:
                refusal = REFUSAL_IDS[9] if name.startswith("local") else REFUSAL_IDS[7]
            elif name in {
                "cache_or_split_operations",
                "feature_extraction_runs",
                "model_or_checkpoint_loads",
                "training_or_parameter_update_runs",
                "model_inference_runs",
                "prediction_sets",
                "scoring_runs",
            }:
                refusal = REFUSAL_IDS[10]
            else:
                refusal = REFUSAL_IDS[11]
            raise HeaderAuditRefusal(refusal, "forbidden access counter is nonzero")


def _iter_string_values(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from _iter_string_values(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested in value:
            yield from _iter_string_values(nested)


def validate_public_ledger(
    ledger: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    forbidden_private_values: Sequence[str] = (),
) -> None:
    """Validate schema, router replay, leakage boundaries, and claim ceiling."""

    if set(ledger) != PUBLIC_LEDGER_FIELDS:
        raise HeaderAuditRefusal(REFUSAL_IDS[8], "public ledger field set mismatch")
    if (
        ledger.get("schema_name") != LEDGER_SCHEMA_NAME
        or ledger.get("schema_version") != SCHEMA_VERSION
        or ledger.get("status") != "passed"
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[12], "public ledger identity mismatch")
    groups = ledger.get("signature_groups")
    if not isinstance(groups, list) or not groups:
        raise HeaderAuditRefusal(REFUSAL_IDS[12], "signature groups are missing")
    if groups != sorted(groups, key=lambda row: row["signature_id"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[12], "signature groups are not canonical")
    signatures = [
        {key: value for key, value in row.items() if key != "occurrence_count"}
        for row in groups
    ]
    for signature in signatures:
        signature_id = signature.pop("signature_id", None)
        if signature_id != _sha256_bytes(_canonical_json_bytes(signature)):
            raise HeaderAuditRefusal(REFUSAL_IDS[12], "signature identifier mismatch")
        signature["signature_id"] = signature_id
    if ledger.get("diagnostic_route") != route_signatures(signatures):
        raise HeaderAuditRefusal(REFUSAL_IDS[12], "diagnostic route does not replay")
    if sum(int(row["occurrence_count"]) for row in groups) != int(
        ledger["measurements"]["input_objects"]
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[12], "signature occurrence count mismatch")
    if ledger.get("all_headers_identical") is not (len(groups) == 1):
        raise HeaderAuditRefusal(REFUSAL_IDS[12], "header-identity flag mismatch")
    first = ledger.get("first_header_diagnosis", {})
    if first.get("signature_id") not in {row["signature_id"] for row in groups}:
        raise HeaderAuditRefusal(REFUSAL_IDS[12], "first-header signature is unknown")
    forbidden_keys = {name.casefold() for name in contract["forbidden_public_fields"]}

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                if str(key).casefold() in forbidden_keys:
                    raise HeaderAuditRefusal(REFUSAL_IDS[8], "forbidden public field present")
                visit(nested)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for nested in value:
                visit(nested)

    visit(ledger)
    public_strings = set(_iter_string_values(ledger))
    if any(value and value in public_strings for value in forbidden_private_values):
        raise HeaderAuditRefusal(REFUSAL_IDS[8], "private source value escaped into output")
    if ledger.get("warnings") != contract["warnings"]:
        raise HeaderAuditRefusal(REFUSAL_IDS[15], "registered warnings changed")
    if ledger.get("unavailable_fields") != contract["unavailable_by_design"]:
        raise HeaderAuditRefusal(REFUSAL_IDS[15], "unavailable-field boundary changed")
    if ledger.get("claim_boundary") != contract["claim_boundary"]:
        raise HeaderAuditRefusal(REFUSAL_IDS[15], "claim boundary changed")
    if set(ledger.get("acceptance_gate_results", {})) != set(contract["acceptance_gates"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[15], "acceptance-gate set changed")
    gate_results = ledger["acceptance_gate_results"]
    if ledger["proof_posture"] == "generated_fixture_and_mocked_transport_only":
        real_only = {
            "registration_and_implementation_remote_green_before_real_access",
            "separate_exact_Tier_C_decision_remote_green_before_real_access",
            "all_paths_URLs_sizes_ETags_and_response_policies_match",
        }
        if any(gate_results[name] for name in real_only) or not all(
            value for name, value in gate_results.items() if name not in real_only
        ):
            raise HeaderAuditRefusal(
                REFUSAL_IDS[15], "synthetic and real acceptance gates are conflated"
            )
    elif not all(gate_results.values()):
        raise HeaderAuditRefusal(REFUSAL_IDS[15], "a real success-ledger gate is false")


def _ensure_output_preflight(path: Path, *, maximum_output_bytes: int) -> None:
    if maximum_output_bytes < MINIMUM_PLAUSIBLE_LEDGER_BYTES:
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "output cap is too small for the schema")
    if path.exists() or path.is_symlink():
        raise HeaderAuditRefusal(REFUSAL_IDS[14], "output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    observed = os.lstat(path.parent)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise HeaderAuditRefusal(REFUSAL_IDS[14], "output parent is not a regular directory")


def _assert_rooted_output_path(root: Path, path: Path) -> None:
    """Reject a real output path that escapes or crosses a symlink."""

    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[14], "real output escapes repository root") from exc
    current = root
    for part in relative.parts[:-1]:
        current /= part
        try:
            observed = os.lstat(current)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise HeaderAuditRefusal(
                REFUSAL_IDS[14], "real output ancestry could not be inspected"
            ) from exc
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
            raise HeaderAuditRefusal(REFUSAL_IDS[14], "real output ancestry is unsafe")


def _write_atomic_exclusive(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temporary.exists() or temporary.is_symlink():
        raise HeaderAuditRefusal(REFUSAL_IDS[14], "invocation temporary output exists")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError:
            raise HeaderAuditRefusal(REFUSAL_IDS[14], "output appeared during commit") from None
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _build_ledger(
    *,
    contract: Mapping[str, Any],
    groups: Sequence[Mapping[str, Any]],
    first_signature: Mapping[str, Any],
    body_hash_set_sha256: str,
    object_count: int,
    input_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
    counters: Mapping[str, int],
    synthetic: bool,
    implementation_binding: Mapping[str, Any] | None,
) -> dict[str, Any]:
    presence = first_signature["allowlisted_name_presence"]
    count_ok = int(first_signature["declared_channel_count"]) == 36
    names_ok = all(bool(presence[name]) for name in CANONICAL_GATE_NAMES)
    route = route_signatures(groups)
    return {
        "schema_name": LEDGER_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "proof_posture": (
            "generated_fixture_and_mocked_transport_only"
            if synthetic
            else "authorized_public_VHDR_metadata_compatibility_audit"
        ),
        "provenance": {
            "contract_sha256": CONTRACT_SHA256,
            "inventory_sha256": INVENTORY_SHA256 if not synthetic else "synthetic_fixture",
            "registration_commit": REGISTRATION_COMMIT,
            "registration_push_CI_run_id": REGISTRATION_CI_RUN_ID,
            "registration_base_python_job_id": REGISTRATION_BASE_JOB_ID,
            "registration_optional_neuro_job_id": REGISTRATION_OPTIONAL_JOB_ID,
            "implementation": implementation_binding,
            "body_hash_set_sha256": body_hash_set_sha256,
        },
        "measurements": {
            "input_objects": object_count,
            "input_bytes": input_bytes,
            "network_body_bytes": 0 if synthetic else input_bytes,
            "body_SHA256_passes": object_count,
            "semantic_parse_passes": object_count,
            "runtime_seconds_through_output_finalization": round(runtime_seconds, 9),
            "peak_RSS_bytes_through_output_finalization": peak_rss_bytes,
            "generated_output_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "signature_groups": list(groups),
        "first_header_diagnosis": {
            "signature_id": first_signature["signature_id"],
            "declared_channel_count": first_signature["declared_channel_count"],
            "canonical_32_plus_4_count_gate_passed": count_ok,
            "canonical_name_presence": {
                name: bool(presence[name]) for name in CANONICAL_GATE_NAMES
            },
            "canonical_name_gate_passed": names_ok,
            "combined_gate_passed": count_ok and names_ok,
        },
        "all_headers_identical": len(groups) == 1,
        "access_counters": dict(counters),
        "warnings": list(contract["warnings"]),
        "unavailable_fields": list(contract["unavailable_by_design"]),
        "acceptance_gate_results": {
            name: not (
                synthetic
                and name
                in {
                    "registration_and_implementation_remote_green_before_real_access",
                    "separate_exact_Tier_C_decision_remote_green_before_real_access",
                    "all_paths_URLs_sizes_ETags_and_response_policies_match",
                }
            )
            for name in contract["acceptance_gates"]
        },
        "diagnostic_route": route,
        "claim_boundary": dict(contract["claim_boundary"]),
    }


def run_header_audit(
    *,
    contract: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    opener: Callable[[str, int], BinaryIO],
    output_path: str | Path,
    environ: Mapping[str, str],
    synthetic: bool,
    implementation_binding: Mapping[str, Any] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> HeaderAuditOutcome:
    """Run the bounded audit core over generated or separately authorized responses."""

    _check_thread_environment(environ)
    caps = contract["resource_caps"]
    maximum_output = int(caps["public_generated_output_bytes"])
    destination = Path(output_path)
    _ensure_output_preflight(destination, maximum_output_bytes=maximum_output)
    if shutil.disk_usage(destination.parent).free < int(caps["minimum_free_disk_bytes"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "free disk is below the registered minimum")
    if len(rows) != int(caps["VHDR_requests"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[2], "header request count mismatch")
    if sum(int(row["size_bytes"]) for row in rows) != int(caps["expected_VHDR_body_bytes"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[2], "header byte total mismatch")
    if [str(row["path"]) for row in rows] != sorted(str(row["path"]) for row in rows):
        raise HeaderAuditRefusal(REFUSAL_IDS[2], "header rows are not in canonical order")
    base_url = str(contract["source"]["object_base_url"])
    if synthetic:
        if not base_url.startswith("fixture://"):
            raise HeaderAuditRefusal(REFUSAL_IDS[2], "synthetic audit requires fixture URLs")
    elif not base_url.startswith("https://"):
        raise HeaderAuditRefusal(REFUSAL_IDS[2], "real audit requires HTTPS")
    started = clock()
    peak_rss = rss_reader()
    if peak_rss > int(caps["peak_RSS_bytes"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "initial peak RSS exceeds cap")
    heavy_before = HEAVY_MODULE_ROOTS.intersection(sys.modules)
    counters = _base_access_counters(synthetic=synthetic)
    group_counts: dict[str, dict[str, Any]] = {}
    first_signature: dict[str, Any] | None = None
    body_rows: list[dict[str, Any]] = []
    private_values: list[str] = []
    input_bytes = 0
    maximum_body = int(caps["maximum_bytes_read_per_VHDR"])
    for row in rows:
        path = _safe_relative_object_path(str(row["path"]))
        size = int(row["size_bytes"])
        etag = str(row["etag"]).lower()
        if size <= 0 or size > maximum_body or HEX32_RE.fullmatch(etag) is None:
            raise HeaderAuditRefusal(REFUSAL_IDS[2], "header row identity is malformed")
        quoted = urllib.parse.quote(path, safe="/._-")
        url = f"{base_url.rstrip('/')}/{quoted}"
        with _managed_stream(opener(url, maximum_body)) as stream:
            _validate_response(stream, url=url, row=row)
            payload = _read_exact_body(stream, size, maximum_body)
        body_sha256 = _sha256_bytes(payload)
        parsed = parse_vhdr_bytes(payload)
        signature = build_channel_signature(parsed)
        if first_signature is None:
            first_signature = signature
        signature_id = signature["signature_id"]
        if signature_id not in group_counts:
            group_counts[signature_id] = {**signature, "occurrence_count": 0}
        group_counts[signature_id]["occurrence_count"] += 1
        body_rows.append(
            {
                "path": path,
                "size_bytes": size,
                "etag": etag,
                "body_sha256": body_sha256,
            }
        )
        private_values.extend(parsed["normalized_channel_names"])
        input_bytes += size
        if synthetic:
            counters["synthetic_VHDR_requests"] += 1
        else:
            counters["real_VHDR_requests"] += 1
            counters["real_VHDR_body_bytes"] += size
            counters["real_header_parses"] += 1
        elapsed = clock() - started
        peak_rss = max(peak_rss, rss_reader())
        if elapsed > float(caps["wall_time_seconds"]) or peak_rss > int(caps["peak_RSS_bytes"]):
            raise HeaderAuditRefusal(REFUSAL_IDS[13], "runtime or peak RSS cap exceeded")
    if first_signature is None or input_bytes != int(caps["expected_VHDR_body_bytes"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[2], "header audit is incomplete")
    if HEAVY_MODULE_ROOTS.intersection(sys.modules) != heavy_before:
        raise HeaderAuditRefusal(REFUSAL_IDS[11], "a heavy dependency was imported")
    _assert_forbidden_counters_zero(counters, synthetic=synthetic)
    groups = sorted(group_counts.values(), key=lambda row: row["signature_id"])
    body_hash_set = _sha256_bytes(_canonical_json_bytes(body_rows))
    ledger = _build_ledger(
        contract=contract,
        groups=groups,
        first_signature=first_signature,
        body_hash_set_sha256=body_hash_set,
        object_count=len(rows),
        input_bytes=input_bytes,
        runtime_seconds=clock() - started,
        peak_rss_bytes=max(peak_rss, rss_reader()),
        counters=counters,
        synthetic=synthetic,
        implementation_binding=implementation_binding,
    )
    for _ in range(8):
        payload = _canonical_json_bytes(ledger)
        if ledger["measurements"]["generated_output_bytes"] == len(payload):
            break
        ledger["measurements"]["generated_output_bytes"] = len(payload)
    else:
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "output byte accounting did not converge")
    payload = _canonical_json_bytes(ledger)
    if len(payload) > maximum_output:
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "public output exceeds cap")
    allowlisted = {name.casefold() for name in PUBLIC_NAME_ALLOWLIST}
    private_unallowlisted = [name for name in private_values if name.casefold() not in allowlisted]
    validate_public_ledger(
        ledger,
        contract=contract,
        forbidden_private_values=[*private_unallowlisted, *(row["path"] for row in body_rows)],
    )
    _write_atomic_exclusive(destination, payload)
    runtime = clock() - started
    peak_rss = max(int(ledger["measurements"]["peak_RSS_bytes_through_output_finalization"]), rss_reader())
    if runtime > float(caps["wall_time_seconds"]) or peak_rss > int(caps["peak_RSS_bytes"]):
        raise HeaderAuditRefusal(REFUSAL_IDS[13], "post-write resource cap exceeded")
    return HeaderAuditOutcome(ledger, destination, runtime, peak_rss, len(payload))


def make_synthetic_vhdr(
    channel_names: Sequence[str],
    *,
    sampling_interval: str = "976.5625",
    codepage: str | None = "UTF-8",
    include_bom: bool = False,
    total_bytes: int | None = None,
) -> bytes:
    """Create deterministic target-free VHDR bytes for adversarial qualification."""

    lines = [
        FORMAT_PREAMBLE,
        "; generated fixture content must never appear in public output",
        "[Common Infos]",
    ]
    if codepage is not None:
        lines.append(f"Codepage={codepage}")
    lines.extend(
        [
            "DataFile=fixture.eeg",
            "MarkerFile=fixture.vmrk",
            "DataFormat=BINARY",
            "DataOrientation=MULTIPLEXED",
            f"NumberOfChannels={len(channel_names)}",
            f"SamplingInterval={sampling_interval}",
            "[Binary Infos]",
            "BinaryFormat=IEEE_FLOAT_32",
            "[Channel Infos]",
        ]
    )
    lines.extend(
        f"Ch{index}={name},,0.1,uV" for index, name in enumerate(channel_names, start=1)
    )
    lines.extend(["[Comment]", "PrivateFixtureToken=must_not_escape"])
    text = "\r\n".join(lines) + "\r\n"
    normalized = None if codepage is None else codepage.casefold().replace("_", "-")
    encoding = "cp1252" if normalized in {"windows-1252", "cp1252"} else "utf-8"
    payload = text.encode(encoding)
    if include_bom:
        payload = b"\xef\xbb\xbf" + payload
    if total_bytes is not None:
        padding = total_bytes - len(payload)
        if padding < 3:
            raise ValueError("requested synthetic VHDR byte count is too small")
        payload += b";" + (b"x" * (padding - 3)) + b"\r\n"
    return payload


def fixture_opener(
    payloads: Mapping[str, bytes], etags: Mapping[str, str]
) -> Callable[[str, int], BinaryIO]:
    """Return a one-open, no-network transport over generated bytes."""

    calls: list[str] = []

    def open_fixture(url: str, maximum_bytes: int) -> BinaryIO:
        if url not in payloads or url in calls:
            raise HeaderAuditRefusal(REFUSAL_IDS[3], "fixture URL is unexpected or repeated")
        if len(payloads[url]) > maximum_bytes:
            raise HeaderAuditRefusal(REFUSAL_IDS[13], "fixture body exceeds read cap")
        calls.append(url)
        return FixtureResponse(payloads[url], url=url, etag=etags[url])

    open_fixture.calls = calls  # type: ignore[attr-defined]
    return open_fixture


def _synthetic_contract_and_rows(
    contract: Mapping[str, Any], inventory: Mapping[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, bytes], dict[str, str]]:
    import copy

    registered = registered_header_rows(contract, inventory)
    names = [f"EEG{index:02d}" for index in range(1, 33)] + list(CANONICAL_GATE_NAMES)
    synthetic_contract = copy.deepcopy(contract)
    synthetic_contract["source"]["object_base_url"] = "fixture://iackd"
    rows: list[dict[str, Any]] = []
    payloads: dict[str, bytes] = {}
    etags: dict[str, str] = {}
    for index, registered_row in enumerate(registered):
        path = f"headers/fixture-{index:03d}.vhdr"
        payload = make_synthetic_vhdr(names, total_bytes=int(registered_row["size_bytes"]))
        etag = _sha256_bytes(payload)[:32]
        url = f"fixture://iackd/{path}"
        rows.append(
            {
                "path": path,
                "size_bytes": len(payload),
                "etag": etag,
                "last_modified": "synthetic",
            }
        )
        payloads[url] = payload
        etags[url] = etag
    return synthetic_contract, rows, payloads, etags


def run_synthetic_qualification(
    output_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> HeaderAuditOutcome:
    """Exercise all 128 registered sizes with generated bytes and mocked transport."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    inventory = load_registered_inventory(root)
    fixture_contract, rows, payloads, etags = _synthetic_contract_and_rows(contract, inventory)
    return run_header_audit(
        contract=fixture_contract,
        rows=rows,
        opener=fixture_opener(payloads, etags),
        output_path=output_path,
        environ=os.environ if environ is None else environ,
        synthetic=True,
        clock=clock,
        rss_reader=rss_reader,
    )


def _open_url_once(url: str, maximum_bytes: int) -> BinaryIO:
    request = urllib.request.Request(
        url,
        headers={"Accept-Encoding": "identity", "User-Agent": "NeuroDecodeKit-IACKDH/0.1"},
        method="GET",
    )
    try:
        response = urllib.request.build_opener(_RejectRedirect).open(request, timeout=30)
    except HeaderAuditRefusal:
        raise
    except Exception as exc:
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "single HTTPS request failed") from exc
    length = response.headers.get("Content-Length")
    try:
        too_large = length is not None and int(length) > maximum_bytes
    except ValueError:
        too_large = True
    if too_large:
        response.close()
        raise HeaderAuditRefusal(REFUSAL_IDS[4], "response Content-Length exceeds cap")
    return response


def load_implementation_record(repo_root: str | Path | None = None) -> tuple[dict[str, Any], str]:
    """Validate the future implementation manifest and its tracked source hashes."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    record, record_hash, _ = _read_locked_json(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256=None,
    )
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("status")
        != "fixture_qualified_exact_implementation_requires_remote_green_before_real_access"
        or record.get("contract_sha256") != CONTRACT_SHA256
        or record.get("green_registration", {}).get("commit") != REGISTRATION_COMMIT
        or record.get("fixture_qualification", {}).get("all_gates_passed") is not True
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "implementation record mismatch")
    for binding in record.get("tracked_file_hashes", ()):
        relative = _safe_relative_object_path(str(binding.get("path", "")))
        expected = str(binding.get("sha256", ""))
        if HEX64_RE.fullmatch(expected) is None or _sha256_file(root / relative) != expected:
            raise HeaderAuditRefusal(REFUSAL_IDS[1], "implementation source hash mismatch")
    return record, record_hash


def _load_authorization_decision(
    root: Path, evidence: RealExecutionEvidence, implementation_record_sha256: str
) -> dict[str, Any]:
    decision, observed_hash, _ = _read_locked_json(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=evidence.authorization_decision_sha256,
    )
    implementation = decision.get("green_implementation", {})
    authorization = decision.get("authorization", {})
    if (
        observed_hash != evidence.authorization_decision_sha256
        or decision.get("schema_name") != DECISION_SCHEMA_NAME
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("contract_sha256") != CONTRACT_SHA256
        or decision.get("effective_only_after_decision_commit_pushed_and_both_CI_jobs_green")
        is not True
        or implementation.get("commit") != evidence.implementation_commit
        or implementation.get("push_CI_run_id") != evidence.implementation_ci_run_id
        or implementation.get("base_python_job_id") != evidence.implementation_base_job_id
        or implementation.get("optional_neuro_job_id")
        != evidence.implementation_optional_job_id
        or implementation.get("implementation_registry_sha256")
        != implementation_record_sha256
        or authorization.get("one_registered_real_header_audit") is not True
        or authorization.get("real_VHDR_requests") != 128
        or authorization.get("real_VHDR_body_bytes") != 161_792
        or authorization.get("retries") != 0
        or authorization.get("reruns") != 0
        or not isinstance(decision.get("maintainer_words"), str)
        or not decision["maintainer_words"].strip()
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[0], "exact real-content decision mismatch")
    return decision


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args), cwd=root, check=False, capture_output=True, text=True
    )


def _verify_real_evidence(root: Path, evidence: RealExecutionEvidence) -> None:
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or HEX40_RE.fullmatch(evidence.authorization_commit) is None
        or HEX64_RE.fullmatch(evidence.authorization_decision_sha256) is None
        or min(
            evidence.implementation_ci_run_id,
            evidence.implementation_base_job_id,
            evidence.implementation_optional_job_id,
            evidence.authorization_ci_run_id,
            evidence.authorization_base_job_id,
            evidence.authorization_optional_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise HeaderAuditRefusal(REFUSAL_IDS[3], "green or one-shot evidence is malformed")
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.authorization_commit:
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "HEAD differs from authorization evidence")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    if clean.returncode or clean.stdout.strip():
        raise HeaderAuditRefusal(REFUSAL_IDS[1], "tracked worktree must be clean")
    for ancestor in (REGISTRATION_COMMIT, evidence.implementation_commit):
        if _git(root, "merge-base", "--is-ancestor", ancestor, "HEAD").returncode:
            raise HeaderAuditRefusal(REFUSAL_IDS[1], "required green commit is not an ancestor")


def _write_consumed_marker(path: Path, evidence: RealExecutionEvidence) -> None:
    _ensure_output_preflight(path, maximum_output_bytes=64 * 1024)
    marker = {
        "schema_name": "neurodecodekit.iackd_channel_inventory_execution_consumed",
        "schema_version": SCHEMA_VERSION,
        "authorization_commit": evidence.authorization_commit,
        "registered_execution_ordinal": 1,
        "retry_allowed": False,
        "rerun_allowed": False,
    }
    _write_atomic_exclusive(path, _canonical_json_bytes(marker))


def execute_registered_audit(
    repo_root: str | Path,
    *,
    evidence: RealExecutionEvidence,
    environ: Mapping[str, str] | None = None,
    opener: Callable[[str, int], BinaryIO] = _open_url_once,
) -> HeaderAuditOutcome:
    """Consume the future one-shot real audit after every exact green gate."""

    root = Path(repo_root)
    contract = load_registered_contract(root)
    inventory = load_registered_inventory(root)
    rows = registered_header_rows(contract, inventory)
    _verify_real_evidence(root, evidence)
    implementation, implementation_hash = load_implementation_record(root)
    _load_authorization_decision(root, evidence, implementation_hash)
    if implementation.get("execution_state", {}).get("real_execution_consumed") is not False:
        raise HeaderAuditRefusal(REFUSAL_IDS[3], "implementation record is not pre-execution")
    consumed_path = root / REAL_CONSUMED_RELATIVE_PATH
    output_path = root / REAL_OUTPUT_RELATIVE_PATH
    _assert_rooted_output_path(root, consumed_path)
    _assert_rooted_output_path(root, output_path)
    if output_path.exists() or output_path.is_symlink():
        raise HeaderAuditRefusal(REFUSAL_IDS[14], "registered output already exists")
    _write_consumed_marker(consumed_path, evidence)
    binding = {
        "commit": evidence.implementation_commit,
        "push_CI_run_id": evidence.implementation_ci_run_id,
        "base_python_job_id": evidence.implementation_base_job_id,
        "optional_neuro_job_id": evidence.implementation_optional_job_id,
        "implementation_registry_sha256": implementation_hash,
        "authorization_commit": evidence.authorization_commit,
        "authorization_push_CI_run_id": evidence.authorization_ci_run_id,
        "authorization_base_python_job_id": evidence.authorization_base_job_id,
        "authorization_optional_neuro_job_id": evidence.authorization_optional_job_id,
        "authorization_decision_sha256": evidence.authorization_decision_sha256,
    }
    return run_header_audit(
        contract=contract,
        rows=rows,
        opener=opener,
        output_path=output_path,
        environ=os.environ if environ is None else environ,
        synthetic=False,
        implementation_binding=binding,
    )


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the frozen no-network plan without inspecting a local data bundle."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    inventory = load_registered_inventory(root)
    rows = registered_header_rows(contract, inventory)
    return {
        "schema_name": "neurodecodekit.iackd_channel_inventory_plan",
        "schema_version": SCHEMA_VERSION,
        "status": "dry_run_real_header_access_unauthorized",
        "lane": "IACKD-H1",
        "registered_objects": len(rows),
        "registered_body_bytes": sum(row["size_bytes"] for row in rows),
        "network_requests_made": 0,
        "network_bytes_read": 0,
        "local_IACKD_path_stats_or_opens": 0,
        "sibling_resolutions_stats_hashes_or_opens": 0,
        "real_header_parses": 0,
        "real_execution_authorized": False,
        "next_gate": "exact_implementation_remote_green_then_separate_Tier_C_decision",
        "claim_ceiling": "metadata_compatibility_only",
    }


def load_public_ledger(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
    maximum_bytes: int = 1024 * 1024,
) -> dict[str, Any]:
    """Load and validate one bounded public ledger without source access."""

    if maximum_bytes <= 0 or maximum_bytes > 1024 * 1024:
        raise ValueError("ledger input cap must be in (0, 1 MiB]")
    ledger, _, _ = _read_locked_json(
        Path(path), expected_sha256=None, maximum_bytes=maximum_bytes
    )
    contract = load_registered_contract(repo_root)
    validate_public_ledger(ledger, contract=contract)
    return ledger


def summarize_public_ledger(ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact, target-free inspection surface."""

    measurements = ledger["measurements"]
    return {
        "status": ledger["status"],
        "proof_posture": ledger["proof_posture"],
        "diagnostic_route": ledger["diagnostic_route"],
        "input_objects": measurements["input_objects"],
        "input_bytes": measurements["input_bytes"],
        "unique_signature_count": len(ledger["signature_groups"]),
        "all_headers_identical": ledger["all_headers_identical"],
        "first_header_diagnosis": ledger["first_header_diagnosis"],
        "runtime_seconds": measurements["runtime_seconds_through_output_finalization"],
        "peak_RSS_bytes": measurements["peak_RSS_bytes_through_output_finalization"],
        "generated_output_bytes": measurements["generated_output_bytes"],
        "producer_is_causal": measurements["producer_is_causal"],
        "end_to_end_latency_measured": measurements["end_to_end_latency_measured"],
        "warnings": ledger["warnings"],
        "unavailable_fields": ledger["unavailable_fields"],
        "claim_boundary": ledger["claim_boundary"],
    }


def _thread_environment() -> dict[str, str]:
    environ = dict(os.environ)
    for key in THREAD_ENV_KEYS:
        environ[key] = "1"
    return environ


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.preprocess.iackd_header_inventory",
        description=(
            "Dry-run, fixture-qualify, inspect, or separately authorize the bounded "
            "IACKD-H1 VHDR inventory audit. The default makes no network request."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true", help="Run generated fixtures only.")
    mode.add_argument("--inspect", metavar="LEDGER", help="Inspect one bounded public ledger.")
    mode.add_argument("--execute", action="store_true", help="Consume the future authorized run.")
    parser.add_argument("--out", help="New JSON output path for --fixture.")
    parser.add_argument("--implementation-commit")
    parser.add_argument("--implementation-ci-run-id", type=int)
    parser.add_argument("--implementation-base-job-id", type=int)
    parser.add_argument("--implementation-optional-job-id", type=int)
    parser.add_argument("--authorization-commit")
    parser.add_argument("--authorization-ci-run-id", type=int)
    parser.add_argument("--authorization-base-job-id", type=int)
    parser.add_argument("--authorization-optional-job-id", type=int)
    parser.add_argument("--authorization-decision-sha256")
    parser.add_argument("--max-input-mib", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.inspect:
            ledger = load_public_ledger(
                args.inspect,
                maximum_bytes=int(args.max_input_mib * 1024 * 1024),
            )
            print(json.dumps(summarize_public_ledger(ledger), indent=2, sort_keys=True))
            return 0
        if args.fixture:
            if not args.out:
                raise ValueError("--fixture requires --out")
            outcome = run_synthetic_qualification(args.out, environ=_thread_environment())
            print(json.dumps(summarize_public_ledger(outcome.ledger), indent=2, sort_keys=True))
            return 0
        if not args.execute:
            print(json.dumps(registered_plan(), indent=2, sort_keys=True))
            print("Safety default: zero network requests and zero local IACKD bundle access.")
            return 0
        names = (
            "implementation_commit",
            "implementation_ci_run_id",
            "implementation_base_job_id",
            "implementation_optional_job_id",
            "authorization_commit",
            "authorization_ci_run_id",
            "authorization_base_job_id",
            "authorization_optional_job_id",
            "authorization_decision_sha256",
        )
        missing = [f"--{name.replace('_', '-')}" for name in names if getattr(args, name) is None]
        if missing:
            raise ValueError(f"--execute requires: {', '.join(missing)}")
        evidence = RealExecutionEvidence(**{name: getattr(args, name) for name in names})
        outcome = execute_registered_audit(
            _repo_root(), evidence=evidence, environ=_thread_environment()
        )
        print(json.dumps(summarize_public_ledger(outcome.ledger), indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # noqa: BLE001 - friendly CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
