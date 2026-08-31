"""Generated-only core for the FMSR1 source-identity witness.

This module intentionally has no network opener. It validates the frozen root
plan, opaque pagination controls, transport transcripts, CI fixtures, and the
page/root/profile/global hash tree that a separately authorized live adapter
may later use.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import re
import resource
import time
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

SCHEMA_NAME = "neurodecodekit.fresh_motor_source_identity_witness_generated"
SCHEMA_VERSION = "0.1.0"
PACKET_ID = "FMSR1-R1-W-v0"
IMPLEMENTATION_ID = "FMSR1-R1-W-I0"

GREEN_DECISION_COMMIT = "e158e8cef2bc0267e5161e947b35409081ea37d7"
GREEN_DECISION_CI_RUN_ID = 33_358_495_852
GREEN_DECISION_BASE_JOB_ID = 99_385_124_402
GREEN_DECISION_OPTIONAL_JOB_ID = 99_385_124_488
DECISION_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_identity_witness_implementation_decision.v0.json"
)
DECISION_BYTES = 5_866
DECISION_SHA256 = "8aa3acd13d705501755e76d0be74feb9c70e9c4c452839944e69498eefe0243f"
PACKET_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_identity_witness_authorization_request.v0.json"
)
PACKET_BYTES = 48_747
PACKET_SHA256 = "e805ffc8b2a963055c075fe002c83b6c4e6e2348f865dc07f41051dd7968d3f6"

MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_GENERATED_INPUT_BYTES = 4 * 1024**2
MAX_REPORT_BYTES = 1024**2
MAX_PAGE_BYTES = 8 * 1024**2
MAX_JSON_DEPTH = 32
MAX_CONTROL_STRING_BYTES = 4_096
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
)
PROFILE_ORDER = (
    "OPENNEURO_CRN",
    "NEMAR",
    "PHYSIONET",
    "GIGADB",
    "BNCI_HORIZON_2020",
)
EXACT_QUERIES = (
    '"motor imagery" EEG EOG EMG',
    '"movement intention" EEG EOG EMG',
    '"motor execution" EEG EOG EMG',
    '"hand movement" EEG EOG EMG',
)
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
HEX_64 = re.compile(r"[0-9a-f]{64}\Z")
INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z")

REFUSAL_ROUTES = (
    "CONTRACT_REFUSE",
    "DECISION_REFUSE",
    "SCHEMA_REFUSE",
    "PLAN_REFUSE",
    "REQUEST_REFUSE",
    "PAGINATION_REFUSE",
    "URL_REFUSE",
    "TRANSPORT_REFUSE",
    "HASH_TREE_REFUSE",
    "CI_REFUSE",
    "TARGET_FIREWALL_REFUSE",
    "RESOURCE_REFUSE",
    "OUTPUT_REFUSE",
)
WARNINGS = (
    "Generated fixtures only; no GitHub API or official index was contacted.",
    "Candidate entities were opaque byte ranges and were neither extracted nor retained.",
    "The generated witness is not authority for a live source transaction.",
)
UNAVAILABLE_FIELDS = (
    "official source identity",
    "candidate metadata or source eligibility",
    "EEG EOG EMG signal or geometry",
    "target label event annotation or trial",
    "model prediction score or neural advantage",
    "end-to-end live latency",
)
CLAIM_BOUNDARY = {
    "scientific_claim_established": False,
    "source_identity_established": False,
    "source_selected": False,
    "real_EEG_accessed": False,
    "neural_information_established": False,
    "unseen_person_generalization_established": False,
    "EEG_beyond_joint_nuisance_established": False,
    "movement_intention_or_motor_cortex_established": False,
    "thought_or_language_decoding_established": False,
    "causal_live_decoding_established": False,
    "hardware_or_clinical_value_established": False,
}


class WitnessRefusal(RuntimeError):
    """Fail-closed generated witness refusal."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError(f"unknown witness refusal route: {route}")
        self.route = route
        self.reason = reason
        super().__init__(f"{route}:{reason}")


@dataclass(frozen=True, slots=True)
class RootRequest:
    root_ordinal: int
    index_id: str
    query_or_category_id: str
    url: str
    method: str
    body: bytes


@dataclass(frozen=True, slots=True)
class FixtureExchange:
    request_identity_sha256: str
    media_type: str
    response_body: bytes
    response_headers: tuple[tuple[str, str], ...]
    redirects: tuple[Mapping[str, object], ...] = ()


def _refuse(route: str, reason: str) -> None:
    raise WitnessRefusal(route, reason)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: object, *, newline: bool = False) -> bytes:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    return payload + (b"\n" if newline else b"")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _refuse("SCHEMA_REFUSE", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_float(_value: str) -> object:
    _refuse("SCHEMA_REFUSE", "floating-point JSON value")


def _reject_constant(_value: str) -> object:
    _refuse("SCHEMA_REFUSE", "non-finite JSON value")


def _walk_json(value: object, *, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        _refuse("SCHEMA_REFUSE", "JSON depth cap exceeded")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                _refuse("SCHEMA_REFUSE", "non-string JSON key")
            _walk_json(child, depth=depth + 1)
    elif isinstance(value, list):
        for child in value:
            _walk_json(child, depth=depth + 1)
    elif value is not None and not isinstance(value, (bool, int, str)):
        _refuse("SCHEMA_REFUSE", "unsupported JSON scalar")


def strict_json_loads(payload: bytes) -> object:
    if payload.startswith(b"\xef\xbb\xbf"):
        _refuse("SCHEMA_REFUSE", "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WitnessRefusal("SCHEMA_REFUSE", "malformed strict JSON") from exc
    _walk_json(value)
    return value


def _mapping(value: object, route: str = "SCHEMA_REFUSE") -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _refuse(route, "expected object")
    return value


def _read_exact_json(path: Path, expected_bytes: int, expected_sha256: str) -> Mapping[str, object]:
    payload = path.read_bytes()
    if len(payload) != expected_bytes or _sha256(payload) != expected_sha256:
        _refuse("CONTRACT_REFUSE", f"artifact identity differs: {path.as_posix()}")
    return _mapping(strict_json_loads(payload))


def load_green_decision(repo_root: str | Path | None = None) -> Mapping[str, object]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    decision = _read_exact_json(root / DECISION_RELATIVE_PATH, DECISION_BYTES, DECISION_SHA256)
    if (
        decision.get("decision_id") != "FMSR1-R1-W-I0-D0"
        or decision.get("packet_id") != PACKET_ID
        or decision.get("effective_only_after_decision_commit_pushed_and_both_CI_jobs_green")
        is not True
    ):
        _refuse("DECISION_REFUSE", "decision identity or ordering differs")
    proof = _mapping(decision.get("green_packet_proof"), "DECISION_REFUSE")
    if (
        proof.get("commit") != "d4ae388d883b8fb04fc75546e6a30aec2fbfa6f2"
        or proof.get("both_required_jobs_green") is not True
        or proof.get("on_GitHub_main") is not True
    ):
        _refuse("DECISION_REFUSE", "packet proof differs")
    authority = _mapping(
        decision.get("authorization_after_decision_green"), "DECISION_REFUSE"
    )
    if (
        authority.get("additive_standard_library_witness_implementation") is not True
        or authority.get("generated_fixture_only_qualification") is not True
        or authority.get("GitHub_API_or_official_index_network") is not False
        or authority.get("live_source_identity_witness") is not False
        or authority.get("model_checkpoint_training_inference_prediction_or_score") is not False
    ):
        _refuse("DECISION_REFUSE", "decision authority differs")
    return decision


def load_packet(repo_root: str | Path | None = None) -> Mapping[str, object]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    packet = _read_exact_json(root / PACKET_RELATIVE_PATH, PACKET_BYTES, PACKET_SHA256)
    if packet.get("packet_id") != PACKET_ID:
        _refuse("CONTRACT_REFUSE", "packet identity differs")
    authority = _mapping(packet.get("operation_authority_now"), "CONTRACT_REFUSE")
    if any(value is not False for value in authority.values()):
        _refuse("CONTRACT_REFUSE", "all-false packet authority differs")
    return packet


def _openneuro_body(
    query: str,
    cursor: str | None = None,
    *,
    root_request: bool = False,
) -> bytes:
    value = {
        "operationName": "FMSR1DatasetSearch",
        "query": (
            "query FMSR1DatasetSearch($query:String!,$first:Int!,$after:String){"
            "datasets(query:$query,first:$first,after:$after){edges{node{id name}}"
            "pageInfo{hasNextPage endCursor}}}"
        ),
        "variables": {"after": cursor, "first": 100, "query": query},
    }
    return canonical_json_bytes(value, newline=root_request)


def build_root_plan(repo_root: str | Path | None = None) -> tuple[RootRequest, ...]:
    packet = load_packet(repo_root)
    frozen = _mapping(packet["frozen_discovery_plan"], "PLAN_REFUSE")
    frozen_rows = frozen.get("root_request_identities")
    if not isinstance(frozen_rows, list) or len(frozen_rows) != 17:
        _refuse("PLAN_REFUSE", "frozen root inventory differs")
    roots: list[RootRequest] = []
    for ordinal, raw_row in enumerate(frozen_rows):
        row = _mapping(raw_row, "PLAN_REFUSE")
        index_id = str(row.get("index_id"))
        query_id = str(row.get("query_or_category_id"))
        method = str(row.get("method"))
        url = str(row.get("url"))
        if index_id == "OPENNEURO":
            try:
                query_index = int(query_id.removeprefix("query_")) - 1
                body = _openneuro_body(EXACT_QUERIES[query_index], root_request=True)
            except (ValueError, IndexError) as exc:
                raise WitnessRefusal("PLAN_REFUSE", "OpenNeuro query identity differs") from exc
        else:
            body = b""
        if _sha256(body) != row.get("body_sha256"):
            _refuse("PLAN_REFUSE", f"root body identity differs: {ordinal}")
        roots.append(RootRequest(ordinal, index_id, query_id, url, method, body))
    if [root.root_ordinal for root in roots] != list(range(17)):
        _refuse("PLAN_REFUSE", "root ordinals differ")
    return tuple(roots)


def _profile_id(root_index_id: str) -> str:
    return "OPENNEURO_CRN" if root_index_id == "OPENNEURO" else root_index_id


def _profile(packet: Mapping[str, object], index_id: str) -> Mapping[str, object]:
    profiles = packet.get("index_profiles")
    if not isinstance(profiles, list):
        _refuse("CONTRACT_REFUSE", "profile inventory differs")
    matches = [row for row in profiles if isinstance(row, Mapping) and row.get("index_id") == index_id]
    if len(matches) != 1:
        _refuse("CONTRACT_REFUSE", f"profile identity differs: {index_id}")
    return matches[0]


def _request_headers(packet: Mapping[str, object], root: RootRequest) -> tuple[tuple[str, str], ...]:
    profile = _mapping(packet["exact_source_HTTP_profile"], "REQUEST_REFUSE")
    raw = profile.get("application_headers_in_order")
    if not isinstance(raw, list):
        _refuse("REQUEST_REFUSE", "application headers differ")
    headers = [(str(row[0]), str(row[1])) for row in raw]
    if root.method == "POST":
        appended = profile.get("OpenNeuro_application_header_appended")
        if not isinstance(appended, list) or len(appended) != 2:
            _refuse("REQUEST_REFUSE", "OpenNeuro content type differs")
        headers.append((str(appended[0]), str(appended[1])))
    host = urlsplit(root.url).hostname
    if host is None:
        _refuse("REQUEST_REFUSE", "request host is absent")
    headers.append(("Host", host.lower()))
    if root.method == "POST":
        headers.append(("Content-Length", str(len(root.body))))
    return tuple(headers)


def request_identity(
    packet: Mapping[str, object],
    root: RootRequest,
    *,
    url: str | None = None,
    body: bytes | None = None,
) -> tuple[str, tuple[tuple[str, str], ...]]:
    active_url = root.url if url is None else url
    active_body = root.body if body is None else body
    active = RootRequest(
        root.root_ordinal,
        root.index_id,
        root.query_or_category_id,
        active_url,
        root.method,
        active_body,
    )
    headers = _request_headers(packet, active)
    prefix = canonical_json_bytes(
        {
            "method": active.method,
            "url": active.url,
            "headers": [list(row) for row in headers],
            "body_bytes": len(active.body),
        },
        newline=True,
    )
    return _sha256(prefix + active.body), headers


def _skip_ws(text: str, offset: int) -> int:
    while offset < len(text) and text[offset] in " \t\r\n":
        offset += 1
    return offset


def _scan_string_end(text: str, offset: int) -> int:
    if offset >= len(text) or text[offset] != '"':
        _refuse("PAGINATION_REFUSE", "JSON string expected")
    offset += 1
    while offset < len(text):
        character = text[offset]
        if character == '"':
            return offset + 1
        if ord(character) < 0x20:
            _refuse("PAGINATION_REFUSE", "JSON control character")
        if character == "\\":
            offset += 1
            if offset >= len(text) or text[offset] not in '"\\/bfnrtu':
                _refuse("PAGINATION_REFUSE", "invalid JSON escape")
            if text[offset] == "u":
                token = text[offset + 1 : offset + 5]
                if len(token) != 4 or any(ch not in "0123456789abcdefABCDEF" for ch in token):
                    _refuse("PAGINATION_REFUSE", "invalid Unicode escape")
                offset += 4
        offset += 1
    _refuse("PAGINATION_REFUSE", "unterminated JSON string")


def _raw_value_end(text: str, offset: int) -> int:
    offset = _skip_ws(text, offset)
    if offset >= len(text):
        _refuse("PAGINATION_REFUSE", "JSON value is absent")
    if text[offset] == '"':
        return _scan_string_end(text, offset)
    if text[offset] in "[{":
        stack = [text[offset]]
        offset += 1
        while offset < len(text) and stack:
            character = text[offset]
            if character == '"':
                offset = _scan_string_end(text, offset)
                continue
            if character in "[{":
                stack.append(character)
            elif character in "]}":
                opener = stack.pop()
                if (opener, character) not in (("[", "]"), ("{", "}")):
                    _refuse("PAGINATION_REFUSE", "mismatched JSON container")
            offset += 1
        if stack:
            _refuse("PAGINATION_REFUSE", "unterminated JSON container")
        return offset
    end = offset
    while end < len(text) and text[end] not in ",]} \t\r\n":
        end += 1
    token = text[offset:end]
    if token not in {"true", "false", "null"} and NUMBER.fullmatch(token) is None:
        _refuse("PAGINATION_REFUSE", "invalid JSON scalar")
    return end


def _decode_json_string(raw: str) -> str:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise WitnessRefusal("PAGINATION_REFUSE", "invalid control string") from exc
    if not isinstance(value, str):
        _refuse("PAGINATION_REFUSE", "control value is not a string")
    if not value or len(value.encode("utf-8")) > MAX_CONTROL_STRING_BYTES:
        _refuse("PAGINATION_REFUSE", "control string length differs")
    if unicodedata.normalize("NFC", value) != value or any(ord(ch) < 0x20 for ch in value):
        _refuse("PAGINATION_REFUSE", "control string normalization differs")
    return value


def _object_members(raw: str) -> list[tuple[str, str]]:
    offset = _skip_ws(raw, 0)
    if offset >= len(raw) or raw[offset] != "{":
        _refuse("PAGINATION_REFUSE", "JSON control parent is not an object")
    offset += 1
    members: list[tuple[str, str]] = []
    seen: set[str] = set()
    while True:
        offset = _skip_ws(raw, offset)
        if offset < len(raw) and raw[offset] == "}":
            offset = _skip_ws(raw, offset + 1)
            if offset != len(raw):
                _refuse("PAGINATION_REFUSE", "trailing JSON control bytes")
            return members
        key_end = _scan_string_end(raw, offset)
        key = _decode_json_string(raw[offset:key_end])
        if key in seen:
            _refuse("PAGINATION_REFUSE", f"duplicate control key: {key}")
        seen.add(key)
        offset = _skip_ws(raw, key_end)
        if offset >= len(raw) or raw[offset] != ":":
            _refuse("PAGINATION_REFUSE", "JSON member colon is absent")
        value_start = _skip_ws(raw, offset + 1)
        value_end = _raw_value_end(raw, value_start)
        members.append((key, raw[value_start:value_end]))
        offset = _skip_ws(raw, value_end)
        if offset < len(raw) and raw[offset] == ",":
            offset += 1
            continue
        if offset < len(raw) and raw[offset] == "}":
            continue
        _refuse("PAGINATION_REFUSE", "JSON object separator differs")


def _member_object(raw: str, name: str) -> str:
    rows = [value for key, value in _object_members(raw) if key == name]
    if len(rows) != 1 or not rows[0].lstrip().startswith("{"):
        _refuse("PAGINATION_REFUSE", f"required object differs: {name}")
    return rows[0]


def _parse_scalar(raw: str) -> object:
    raw = raw.strip()
    if raw == "null":
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw.startswith('"'):
        return _decode_json_string(raw)
    _refuse("PAGINATION_REFUSE", "routing scalar type differs")


def extract_openneuro_control(payload: bytes) -> tuple[str | None, Mapping[str, object]]:
    if payload.startswith(b"\xef\xbb\xbf"):
        _refuse("PAGINATION_REFUSE", "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise WitnessRefusal("PAGINATION_REFUSE", "response is not strict UTF-8") from exc
    page_info = _member_object(_member_object(_member_object(text, "data"), "datasets"), "pageInfo")
    controls = {key: _parse_scalar(value) for key, value in _object_members(page_info)}
    if set(controls) != {"hasNextPage", "endCursor"}:
        _refuse("PAGINATION_REFUSE", "OpenNeuro pageInfo controls differ")
    has_next = controls["hasNextPage"]
    cursor = controls["endCursor"]
    if has_next is True and isinstance(cursor, str):
        return cursor, {"variant": "OPENNEURO_CONTINUE", "cursor_sha256": _sha256(cursor.encode())}
    if has_next is False and cursor is None:
        return None, {"variant": "OPENNEURO_TERMINAL"}
    _refuse("PAGINATION_REFUSE", "OpenNeuro control values differ")


def extract_generic_json_control(payload: bytes) -> tuple[str | None, Mapping[str, object]]:
    if payload.startswith(b"\xef\xbb\xbf"):
        _refuse("PAGINATION_REFUSE", "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise WitnessRefusal("PAGINATION_REFUSE", "response is not strict UTF-8") from exc
    members = dict(_object_members(text))
    top_present = "next" in members
    pagination_present = "pagination" in members
    if top_present == pagination_present:
        _refuse("PAGINATION_REFUSE", "exactly one JSON control variant is required")
    if top_present:
        value = _parse_scalar(members["next"])
        if value is None:
            return None, {"variant": "TOP_LEVEL_NEXT", "terminal": True}
        if isinstance(value, str):
            return value, {"variant": "TOP_LEVEL_NEXT", "terminal": False}
        _refuse("PAGINATION_REFUSE", "top-level next type differs")
    pagination = dict(_object_members(members["pagination"]))
    if "next" in pagination and "has_next" not in pagination:
        value = _parse_scalar(pagination["next"])
        if value is None:
            return None, {"variant": "PAGINATION_NEXT", "terminal": True}
        if isinstance(value, str):
            return value, {"variant": "PAGINATION_NEXT", "terminal": False}
    if set(pagination) == {"has_next"} and _parse_scalar(pagination["has_next"]) is False:
        return None, {"variant": "PAGINATION_HAS_NEXT_FALSE", "terminal": True}
    _refuse("PAGINATION_REFUSE", "pagination control differs")


class _PaginationHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.container_depth: int | None = None
        self.container_count = 0
        self.next_values: list[str] = []
        self.terminal_count = 0

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return {token.casefold() for token in value.split() if token}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.depth += 1
        values = {key.casefold(): value or "" for key, value in attrs}
        classes = self._tokens(values.get("class", ""))
        matches = (
            (tag.casefold() == "nav" and values.get("aria-label", "").strip().casefold() == "pagination")
            or (
                values.get("role", "").strip().casefold() == "navigation"
                and values.get("aria-label", "").strip().casefold() == "pagination"
            )
            or bool(classes & {"pagination", "pager"})
            or values.get("id", "").strip().casefold() in {"pagination", "pager"}
        )
        if matches:
            self.container_count += 1
            if self.container_depth is None:
                self.container_depth = self.depth
        if self.container_depth is None or self.depth <= self.container_depth or tag.casefold() != "a":
            return
        rel = self._tokens(values.get("rel", ""))
        if "next" in rel:
            href = values.get("href", "")
            if href:
                self.next_values.append(href)
            elif values.get("aria-disabled", "").strip().casefold() == "true":
                self.terminal_count += 1
        elif {"next", "disabled"}.issubset(classes) and not values.get("href"):
            self.terminal_count += 1

    def handle_endtag(self, _tag: str) -> None:
        if self.container_depth == self.depth:
            self.container_depth = None
        self.depth = max(0, self.depth - 1)


def extract_generic_html_control(payload: bytes) -> tuple[str | None, Mapping[str, object]]:
    if payload.startswith(b"\xef\xbb\xbf"):
        _refuse("PAGINATION_REFUSE", "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise WitnessRefusal("PAGINATION_REFUSE", "response is not strict UTF-8") from exc
    parser = _PaginationHTMLParser()
    parser.feed(text)
    parser.close()
    if parser.container_count != 1:
        _refuse("PAGINATION_REFUSE", "HTML pagination container count differs")
    if len(parser.next_values) == 1 and parser.terminal_count == 0:
        value = parser.next_values[0]
        if len(value.encode("utf-8")) > MAX_CONTROL_STRING_BYTES:
            _refuse("PAGINATION_REFUSE", "HTML next href cap exceeded")
        return value, {"variant": "HTML_NEXT", "terminal": False}
    if not parser.next_values and parser.terminal_count == 1:
        return None, {"variant": "HTML_TERMINAL", "terminal": True}
    _refuse("PAGINATION_REFUSE", "HTML next or terminal control differs")


def _contains_control(value: str) -> bool:
    return any(ord(character) < 0x20 or ord(character) == 0x7F for character in value)


def canonicalize_continuation_url(
    packet: Mapping[str, object],
    root: RootRequest,
    current_url: str,
    reference: str,
) -> str:
    if not reference or len(reference.encode("utf-8")) > MAX_CONTROL_STRING_BYTES:
        _refuse("URL_REFUSE", "continuation reference length differs")
    resolved = urljoin(current_url, reference)
    try:
        parsed = urlsplit(resolved)
        port = parsed.port
    except ValueError as exc:
        raise WitnessRefusal("URL_REFUSE", "continuation URL is malformed") from exc
    profile = _profile(packet, _profile_id(root.index_id))
    host = parsed.hostname
    if host is None:
        _refuse("URL_REFUSE", "continuation host is absent")
    if not host.isascii():
        _refuse("URL_REFUSE", "continuation host must be frozen ASCII")
    host_ascii = host.lower()
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port is not None
        or host_ascii not in profile["allowed_hosts"]
    ):
        _refuse("URL_REFUSE", "continuation origin differs")
    path = parsed.path or "/"
    if path != profile["allowed_path"] or not path.startswith("/") or not path.isascii():
        _refuse("URL_REFUSE", "continuation path differs")
    try:
        pairs = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True)
        root_pairs = parse_qsl(urlsplit(root.url).query, keep_blank_values=True, strict_parsing=True)
    except (UnicodeDecodeError, ValueError) as exc:
        raise WitnessRefusal("URL_REFUSE", "continuation query is malformed") from exc
    keys = [key for key, _value in pairs]
    if len(keys) != len(set(keys)) or any(not key or not value for key, value in pairs):
        _refuse("URL_REFUSE", "duplicate or empty query component")
    if any(
        unicodedata.normalize("NFC", part) != part or _contains_control(part)
        for pair in pairs
        for part in pair
    ):
        _refuse("URL_REFUSE", "query normalization differs")
    allowed = set(profile["allowed_query_keys"])
    if any(key not in allowed for key in keys):
        _refuse("URL_REFUSE", "query key is not allowlisted")
    grammar_rows = packet.get("pagination_grammars")
    if not isinstance(grammar_rows, list):
        _refuse("CONTRACT_REFUSE", "pagination grammar inventory differs")
    grammar_matches = [
        row for row in grammar_rows if isinstance(row, Mapping) and row.get("index_id") == _profile_id(root.index_id)
    ]
    if len(grammar_matches) != 1:
        _refuse("CONTRACT_REFUSE", "pagination grammar identity differs")
    grammar = grammar_matches[0]
    fixed_key = grammar.get("fixed_root_query_key")
    root_map = dict(root_pairs)
    next_map = dict(pairs)
    if fixed_key is not None and next_map.get(fixed_key) != root_map.get(fixed_key):
        _refuse("URL_REFUSE", "frozen root query changed")
    optional = list(grammar.get("unchanged_optional_keys_in_canonical_order", []))
    for key in optional:
        if next_map.get(key) != root_map.get(key):
            _refuse("URL_REFUSE", "optional query changed")
    continuation_keys = list(grammar.get("allowed_continuation_keys", []))
    active = [key for key in continuation_keys if key in next_map]
    if len(active) != 1:
        _refuse("URL_REFUSE", "exactly one continuation key is required")
    key = active[0]
    value = next_map[key]
    if key == "page" and (INTEGER.fullmatch(value) is None or int(value) <= 0):
        _refuse("URL_REFUSE", "page value differs")
    if key == "offset" and (INTEGER.fullmatch(value) is None or int(value) < 0):
        _refuse("URL_REFUSE", "offset value differs")
    if key == "cursor" and not value:
        _refuse("URL_REFUSE", "cursor value differs")
    ordered_keys = ([fixed_key] if fixed_key is not None else []) + optional + [key]
    expected_pairs = [(name, next_map[name]) for name in ordered_keys if name in next_map]
    canonical_query = urlencode(expected_pairs)
    canonical = urlunsplit(("https", host_ascii, path, canonical_query, ""))
    if resolved != canonical:
        _refuse("URL_REFUSE", "continuation URL is noncanonical")
    return canonical


def _parse_control(
    packet: Mapping[str, object],
    root: RootRequest,
    current_url: str,
    current_body: bytes,
    media_type: str,
    payload: bytes,
) -> tuple[str | None, bytes | None, Mapping[str, object]]:
    if len(payload) > MAX_PAGE_BYTES:
        _refuse("RESOURCE_REFUSE", "page byte cap exceeded")
    profile_id = _profile_id(root.index_id)
    if profile_id == "OPENNEURO_CRN":
        if media_type != "application/json":
            _refuse("PAGINATION_REFUSE", "OpenNeuro media type differs")
        cursor, control = extract_openneuro_control(payload)
        if cursor is None:
            return None, None, control
        query_index = int(root.query_or_category_id.removeprefix("query_")) - 1
        next_body = _openneuro_body(EXACT_QUERIES[query_index], cursor)
        if next_body == current_body:
            _refuse("PAGINATION_REFUSE", "OpenNeuro cursor did not advance")
        return root.url, next_body, control
    if media_type == "application/json":
        reference, control = extract_generic_json_control(payload)
    elif media_type in {"text/html", "application/xhtml+xml"}:
        reference, control = extract_generic_html_control(payload)
    else:
        _refuse("TRANSPORT_REFUSE", "normalized media type differs")
    if reference is None:
        return None, None, control
    return canonicalize_continuation_url(packet, root, current_url, reference), b"", control


def _transport_evidence(
    root: RootRequest,
    url: str,
    headers: Sequence[tuple[str, str]],
    body: bytes,
    exchange: FixtureExchange,
    global_ordinal: int,
) -> dict[str, object]:
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    response_header_bytes = canonical_json_bytes([list(row) for row in exchange.response_headers])
    return {
        "global_request_ordinal": global_ordinal,
        "method": root.method,
        "scheme": "https",
        "host_ascii": host,
        "port": 443,
        "path_and_query_sha256": _sha256(
            ((parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")).encode()
        ),
        "request_headers_sha256": _sha256(canonical_json_bytes([list(row) for row in headers])),
        "request_body_bytes": len(body),
        "request_body_sha256": _sha256(body),
        "DNS_answer_set_sha256": _sha256(f"generated-DNS:{host}".encode()),
        "selected_peer_sha256": _sha256(f"generated-peer:{host}".encode()),
        "post_connect_peer_sha256": _sha256(f"generated-peer:{host}".encode()),
        "selected_and_post_connect_peer_equal_and_global": True,
        "TLS_hostname": host,
        "TLS_SNI": host,
        "TLS_version": "TLSv1.3",
        "system_CA_verification_succeeded": True,
        "HTTP_status": 200,
        "response_headers_sha256": _sha256(response_header_bytes),
        "normalized_media_type": exchange.media_type,
        "charset": "utf-8",
        "content_encoding": "identity",
        "transfer_framing": "content_length",
        "wire_bytes": len(exchange.response_body),
        "entity_body_bytes": len(exchange.response_body),
        "request_elapsed_nanoseconds": 1_000 + global_ordinal,
        "whole_invocation_elapsed_nanoseconds": 10_000 + global_ordinal,
    }


def validate_transport_evidence(packet: Mapping[str, object], value: object) -> None:
    row = _mapping(value, "TRANSPORT_REFUSE")
    contract = _mapping(packet["opaque_snapshot_ledger_contract"], "CONTRACT_REFUSE")
    required = contract["required_transport_evidence_fields"]
    if not isinstance(required, list) or set(row) != set(required):
        _refuse("TRANSPORT_REFUSE", "transport evidence fields differ")
    digest_fields = (
        "path_and_query_sha256",
        "request_headers_sha256",
        "request_body_sha256",
        "DNS_answer_set_sha256",
        "selected_peer_sha256",
        "post_connect_peer_sha256",
        "response_headers_sha256",
    )
    if any(not isinstance(row[name], str) or HEX_64.fullmatch(row[name]) is None for name in digest_fields):
        _refuse("TRANSPORT_REFUSE", "transport digest differs")
    if row["selected_and_post_connect_peer_equal_and_global"] is not True:
        _refuse("TRANSPORT_REFUSE", "peer binding differs")
    if row["system_CA_verification_succeeded"] is not True:
        _refuse("TRANSPORT_REFUSE", "CA verification differs")
    if row["TLS_version"] not in {"TLSv1.2", "TLSv1.3"} or row["HTTP_status"] != 200:
        _refuse("TRANSPORT_REFUSE", "TLS or HTTP status differs")
    if row["content_encoding"] not in {"", "identity"}:
        _refuse("TRANSPORT_REFUSE", "content encoding differs")


def validate_redirect_transcript(packet: Mapping[str, object], value: object) -> None:
    if not isinstance(value, list):
        _refuse("TRANSPORT_REFUSE", "redirect transcript is not an array")
    contract = _mapping(packet["redirect_hop_contract"], "CONTRACT_REFUSE")
    required = contract["required_fields_in_canonical_order"]
    if len(value) > int(contract["maximum_items"]):
        _refuse("TRANSPORT_REFUSE", "redirect cap exceeded")
    for ordinal, raw_row in enumerate(value):
        row = _mapping(raw_row, "TRANSPORT_REFUSE")
        if set(row) != set(required) or row.get("hop_ordinal") != ordinal:
            _refuse("TRANSPORT_REFUSE", "redirect fields or order differ")
        if row.get("selected_and_post_connect_peer_equal_and_global") is not True:
            _refuse("TRANSPORT_REFUSE", "redirect peer binding differs")
        if row.get("system_CA_verification_succeeded") is not True:
            _refuse("TRANSPORT_REFUSE", "redirect CA verification differs")
        if row.get("normalized_next_scheme") != "https" or row.get("normalized_next_port") != 443:
            _refuse("TRANSPORT_REFUSE", "redirect target differs")


def _hash_fields(value: Mapping[str, object], fields: Sequence[str]) -> str:
    if any(field not in value for field in fields):
        _refuse("HASH_TREE_REFUSE", "hash preimage field is absent")
    return _sha256(canonical_json_bytes({field: value[field] for field in fields}, newline=True))


def _assert_sorted_unique_ascii(values: object) -> None:
    if (
        not isinstance(values, list)
        or values != sorted(set(values))
        or any(not isinstance(value, str) or not value.isascii() for value in values)
    ):
        _refuse("HASH_TREE_REFUSE", "warning or unavailable-field array differs")


def validate_ledger(packet: Mapping[str, object], ledger: object) -> Mapping[str, object]:
    outer = _mapping(ledger, "HASH_TREE_REFUSE")
    contract = _mapping(packet["opaque_snapshot_ledger_contract"], "CONTRACT_REFUSE")
    if set(outer) != set(contract["required_outer_fields"]):
        _refuse("HASH_TREE_REFUSE", "outer ledger fields differ")
    profiles = outer.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 5:
        _refuse("HASH_TREE_REFUSE", "profile inventory differs")
    if [row.get("index_id") for row in profiles if isinstance(row, Mapping)] != list(PROFILE_ORDER):
        _refuse("HASH_TREE_REFUSE", "profile order differs")
    expected_profile_hashes: list[str] = []
    expected_global_root_hashes: list[str] = []
    total_pages = total_wire = total_entity = 0
    membership = _mapping(contract["profile_root_membership"], "CONTRACT_REFUSE")
    hash_contract = _mapping(contract["canonical_hash_contract"], "CONTRACT_REFUSE")
    for profile_ordinal, raw_profile in enumerate(profiles):
        profile = _mapping(raw_profile, "HASH_TREE_REFUSE")
        if set(profile) != set(contract["required_profile_fields"]):
            _refuse("HASH_TREE_REFUSE", "profile fields differ")
        index_id = str(profile["index_id"])
        expected_ordinals = membership[index_id]
        if profile["profile_ordinal"] != profile_ordinal or profile["root_ordinals"] != expected_ordinals:
            _refuse("HASH_TREE_REFUSE", "profile ordinal membership differs")
        roots = profile["roots"]
        if not isinstance(roots, list) or [row.get("root_ordinal") for row in roots] != expected_ordinals:
            _refuse("HASH_TREE_REFUSE", "root membership differs")
        root_hashes: list[str] = []
        profile_pages = profile_wire = profile_entity = terminal_roots = 0
        for raw_root in roots:
            root = _mapping(raw_root, "HASH_TREE_REFUSE")
            if set(root) != set(contract["required_root_fields"]):
                _refuse("HASH_TREE_REFUSE", "root fields differ")
            pages = root["pages"]
            if not isinstance(pages, list) or not pages:
                _refuse("HASH_TREE_REFUSE", "root page inventory differs")
            page_hashes: list[str] = []
            request_chain: list[str] = []
            terminal_count = 0
            for page_ordinal, raw_page in enumerate(pages):
                page = _mapping(raw_page, "HASH_TREE_REFUSE")
                if set(page) != set(contract["required_page_fields"]):
                    _refuse("HASH_TREE_REFUSE", "page fields differ")
                if page["page_ordinal"] != page_ordinal:
                    _refuse("HASH_TREE_REFUSE", "page ordinal gap")
                validate_redirect_transcript(packet, page["redirect_transcript"])
                validate_transport_evidence(packet, page["transport_evidence"])
                if request_chain and page["request_identity_sha256"] != request_chain[-1]:
                    _refuse("HASH_TREE_REFUSE", "request chain differs")
                next_identity = page["next_request_identity_sha256"]
                if page["terminal_state"] == "TERMINAL":
                    terminal_count += 1
                    if next_identity is not None or page_ordinal != len(pages) - 1:
                        _refuse("HASH_TREE_REFUSE", "terminal page differs")
                elif page["terminal_state"] == "CONTINUE":
                    if not isinstance(next_identity, str) or HEX_64.fullmatch(next_identity) is None:
                        _refuse("HASH_TREE_REFUSE", "continuation identity differs")
                    request_chain.append(next_identity)
                else:
                    _refuse("HASH_TREE_REFUSE", "terminal state differs")
                expected_page_hash = _hash_fields(page, hash_contract["page_preimage_fields"])
                if page["canonical_page_ledger_sha256"] != expected_page_hash:
                    _refuse("HASH_TREE_REFUSE", "page hash differs")
                page_hashes.append(expected_page_hash)
                transport = page["transport_evidence"]
                profile_wire += int(transport["wire_bytes"])
                profile_entity += int(transport["entity_body_bytes"])
            if terminal_count != 1 or root["terminal_page_count"] != 1 or root["complete"] is not True:
                _refuse("HASH_TREE_REFUSE", "root completion differs")
            if root["page_count"] != len(pages) or root["page_sha256_values"] != page_hashes:
                _refuse("HASH_TREE_REFUSE", "root page reconciliation differs")
            expected_root_hash = _hash_fields(root, hash_contract["root_preimage_fields"])
            if root["canonical_root_ledger_sha256"] != expected_root_hash:
                _refuse("HASH_TREE_REFUSE", "root hash differs")
            root_hashes.append(expected_root_hash)
            expected_global_root_hashes.append(expected_root_hash)
            profile_pages += len(pages)
            terminal_roots += 1
        if profile["root_sha256_values"] != root_hashes:
            _refuse("HASH_TREE_REFUSE", "profile root reconciliation differs")
        if (
            profile["complete"] is not True
            or profile["page_count"] != profile_pages
            or profile["terminal_root_count"] != terminal_roots
            or profile["wire_bytes"] != profile_wire
            or profile["entity_body_bytes"] != profile_entity
        ):
            _refuse("HASH_TREE_REFUSE", "profile aggregate differs")
        _assert_sorted_unique_ascii(profile["warnings"])
        _assert_sorted_unique_ascii(profile["unavailable_fields"])
        expected_profile_hash = _hash_fields(profile, hash_contract["profile_preimage_fields"])
        if profile["canonical_profile_ledger_sha256"] != expected_profile_hash:
            _refuse("HASH_TREE_REFUSE", "profile hash differs")
        expected_profile_hashes.append(expected_profile_hash)
        total_pages += profile_pages
        total_wire += profile_wire
        total_entity += profile_entity
    if outer["profile_sha256_values"] != expected_profile_hashes:
        _refuse("HASH_TREE_REFUSE", "outer profile reconciliation differs")
    if outer["global_root_sha256_values"] != expected_global_root_hashes:
        _refuse("HASH_TREE_REFUSE", "outer root reconciliation differs")
    if (
        outer["total_root_count"] != 17
        or outer["total_page_count"] != total_pages
        or outer["total_wire_bytes"] != total_wire
        or outer["total_entity_body_bytes"] != total_entity
    ):
        _refuse("HASH_TREE_REFUSE", "outer aggregate differs")
    expected_global_hash = _hash_fields(outer, hash_contract["global_preimage_fields"])
    if outer["canonical_global_ledger_sha256"] != expected_global_hash:
        _refuse("HASH_TREE_REFUSE", "global hash differs")
    return outer


def _next_url(root: RootRequest) -> str:
    parsed = urlsplit(root.url)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    pairs.append(("page", "2"))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(pairs), ""))


def _generated_response(root: RootRequest, page_ordinal: int) -> tuple[str, bytes]:
    poison = f"REFERENCE_TARGET_DO_NOT_RETAIN_{root.root_ordinal}"
    if root.index_id == "OPENNEURO":
        value = {
            "data": {
                "datasets": {
                    "edges": [{"node": {"id": poison, "name": poison}}],
                    "pageInfo": {
                        "endCursor": f"cursor-{root.root_ordinal}" if page_ordinal == 0 else None,
                        "hasNextPage": page_ordinal == 0,
                    },
                }
            }
        }
        return "application/json", canonical_json_bytes(value)
    next_url = _next_url(root)
    variant = root.root_ordinal % 3
    if variant == 0:
        value = {
            "items": [{"reference_text": poison}],
            "next": next_url if page_ordinal == 0 else None,
        }
        return "application/json", canonical_json_bytes(value)
    if variant == 1:
        pagination = {"next": next_url} if page_ordinal == 0 else {"has_next": False}
        value = {"pagination": pagination, "results": [{"target": poison}]}
        return "application/json", canonical_json_bytes(value)
    if page_ordinal == 0:
        html = (
            '<html><body><div class="candidate">'
            + poison
            + '</div><nav aria-label="pagination"><a rel="next" href="'
            + next_url
            + '">next</a></nav></body></html>'
        )
    else:
        html = (
            '<html><body><div class="candidate">'
            + poison
            + '</div><nav aria-label="pagination">'
            '<a rel="next" aria-disabled="true">next</a></nav></body></html>'
        )
    return "text/html", html.encode("utf-8")


def build_generated_fixture(repo_root: str | Path | None = None) -> dict[str, object]:
    packet = load_packet(repo_root)
    roots = build_root_plan(repo_root)
    exchanges: list[FixtureExchange] = []
    for root in roots:
        current_url = root.url
        current_body = root.body
        for page_ordinal in range(2):
            identity, _headers = request_identity(packet, root, url=current_url, body=current_body)
            media_type, response_body = _generated_response(root, page_ordinal)
            headers = (
                ("Content-Type", f"{media_type}; charset=utf-8"),
                ("Content-Encoding", "identity"),
                ("Content-Length", str(len(response_body))),
            )
            exchanges.append(FixtureExchange(identity, media_type, response_body, headers))
            next_url, next_body, _control = _parse_control(
                packet,
                root,
                current_url,
                current_body,
                media_type,
                response_body,
            )
            if page_ordinal == 0:
                if next_url is None or next_body is None:
                    _refuse("PLAN_REFUSE", "generated continuation is absent")
                current_url, current_body = next_url, next_body
            elif next_url is not None or next_body is not None:
                _refuse("PLAN_REFUSE", "generated terminal control differs")
    return {
        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_fixture",
        "schema_version": "0.1.0",
        "packet_id": PACKET_ID,
        "exchanges": exchanges,
    }


def _build_ledger(
    packet: Mapping[str, object],
    roots: Sequence[RootRequest],
    exchanges: Sequence[FixtureExchange],
) -> dict[str, object]:
    contract = _mapping(packet["opaque_snapshot_ledger_contract"], "CONTRACT_REFUSE")
    hash_contract = _mapping(contract["canonical_hash_contract"], "CONTRACT_REFUSE")
    exchange_offset = 0
    global_ordinal = 0
    roots_by_profile: dict[str, list[dict[str, object]]] = {name: [] for name in PROFILE_ORDER}
    for root in roots:
        current_url = root.url
        current_body = root.body
        initial_identity, _initial_headers = request_identity(packet, root)
        pages: list[dict[str, object]] = []
        for page_ordinal in range(2):
            if exchange_offset >= len(exchanges):
                _refuse("PLAN_REFUSE", "fixture exchange is missing")
            exchange = exchanges[exchange_offset]
            exchange_offset += 1
            identity, headers = request_identity(packet, root, url=current_url, body=current_body)
            if exchange.request_identity_sha256 != identity:
                _refuse("REQUEST_REFUSE", "fixture request identity differs")
            next_url, next_body, control = _parse_control(
                packet,
                root,
                current_url,
                current_body,
                exchange.media_type,
                exchange.response_body,
            )
            next_identity = None
            if next_url is not None and next_body is not None:
                next_identity, _next_headers = request_identity(
                    packet, root, url=next_url, body=next_body
                )
            page = {
                "page_ordinal": page_ordinal,
                "request_identity_sha256": identity,
                "request_body_sha256": _sha256(current_body),
                "redirect_transcript": [dict(row) for row in exchange.redirects],
                "pagination_identity_sha256": _sha256(canonical_json_bytes(control, newline=True)),
                "response_body_bytes": len(exchange.response_body),
                "response_body_sha256": _sha256(exchange.response_body),
                "next_request_identity_sha256": next_identity,
                "terminal_state": "TERMINAL" if next_identity is None else "CONTINUE",
                "transport_evidence": _transport_evidence(
                    root,
                    current_url,
                    headers,
                    current_body,
                    exchange,
                    global_ordinal,
                ),
            }
            page["canonical_page_ledger_sha256"] = _hash_fields(
                page, hash_contract["page_preimage_fields"]
            )
            pages.append(page)
            global_ordinal += 1
            if next_url is not None and next_body is not None:
                current_url, current_body = next_url, next_body
        page_hashes = [str(page["canonical_page_ledger_sha256"]) for page in pages]
        root_row = {
            "root_ordinal": root.root_ordinal,
            "index_id": _profile_id(root.index_id),
            "query_or_category_id": root.query_or_category_id,
            "initial_request_identity_sha256": initial_identity,
            "complete": True,
            "page_count": len(pages),
            "terminal_page_count": 1,
            "pages": pages,
            "page_sha256_values": page_hashes,
        }
        root_row["canonical_root_ledger_sha256"] = _hash_fields(
            root_row, hash_contract["root_preimage_fields"]
        )
        roots_by_profile[_profile_id(root.index_id)].append(root_row)
    if exchange_offset != len(exchanges):
        _refuse("PLAN_REFUSE", "fixture exchange inventory has trailing rows")
    profiles: list[dict[str, object]] = []
    for profile_ordinal, index_id in enumerate(PROFILE_ORDER):
        profile_roots = roots_by_profile[index_id]
        root_hashes = [str(row["canonical_root_ledger_sha256"]) for row in profile_roots]
        profile_row = {
            "profile_ordinal": profile_ordinal,
            "index_id": index_id,
            "mode": "OPAQUE_COMPLETE_SNAPSHOT_REPLAY",
            "root_ordinals": [int(row["root_ordinal"]) for row in profile_roots],
            "roots": profile_roots,
            "root_sha256_values": root_hashes,
            "complete": True,
            "page_count": sum(int(row["page_count"]) for row in profile_roots),
            "terminal_root_count": len(profile_roots),
            "wire_bytes": sum(
                int(page["transport_evidence"]["wire_bytes"])
                for row in profile_roots
                for page in row["pages"]
            ),
            "entity_body_bytes": sum(
                int(page["transport_evidence"]["entity_body_bytes"])
                for row in profile_roots
                for page in row["pages"]
            ),
            "warnings": sorted(set(WARNINGS)),
            "unavailable_fields": sorted(set(UNAVAILABLE_FIELDS)),
        }
        profile_row["canonical_profile_ledger_sha256"] = _hash_fields(
            profile_row, hash_contract["profile_preimage_fields"]
        )
        profiles.append(profile_row)
    ledger = {
        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_ledger",
        "schema_version": "0.1.0",
        "packet_id": PACKET_ID,
        "profiles": profiles,
        "profile_sha256_values": [
            str(profile["canonical_profile_ledger_sha256"]) for profile in profiles
        ],
        "global_root_sha256_values": [
            str(root["canonical_root_ledger_sha256"])
            for profile in profiles
            for root in profile["roots"]
        ],
        "total_root_count": 17,
        "total_page_count": sum(int(profile["page_count"]) for profile in profiles),
        "total_wire_bytes": sum(int(profile["wire_bytes"]) for profile in profiles),
        "total_entity_body_bytes": sum(
            int(profile["entity_body_bytes"]) for profile in profiles
        ),
    }
    ledger["canonical_global_ledger_sha256"] = _hash_fields(
        ledger, hash_contract["global_preimage_fields"]
    )
    return ledger


def run_generated_replay(
    repo_root: str | Path | None = None,
    *,
    fixture: Mapping[str, object] | None = None,
) -> dict[str, object]:
    packet = load_packet(repo_root)
    load_green_decision(repo_root)
    active_fixture = build_generated_fixture(repo_root) if fixture is None else fixture
    exchanges = active_fixture.get("exchanges")
    if not isinstance(exchanges, (list, tuple)) or any(
        not isinstance(exchange, FixtureExchange) for exchange in exchanges
    ):
        _refuse("SCHEMA_REFUSE", "fixture exchange inventory differs")
    ledger = _build_ledger(packet, build_root_plan(repo_root), exchanges)
    validate_ledger(packet, ledger)
    return ledger


def build_generated_CI_fixture(repo_root: str | Path | None = None) -> dict[str, bytes]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    workflow = (root / ".github/workflows/ci.yml").read_bytes()
    head = "a" * 40
    main_ref = canonical_json_bytes({"object": {"sha": head}})
    check_runs = canonical_json_bytes(
        {
            "total_count": 2,
            "check_runs": [
                {
                    "id": 101,
                    "name": "Base Python",
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": head,
                    "app": {"slug": "github-actions"},
                },
                {
                    "id": 102,
                    "name": "Optional Neuro Readers",
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": head,
                    "app": {"slug": "github-actions"},
                },
            ],
        }
    )
    workflow_blob = canonical_json_bytes(
        {
            "sha": "4246b7c7f6f8570df53b1b89705b496b30e38a78",
            "encoding": "base64",
            "size": len(workflow),
            "content": base64.b64encode(workflow).decode("ascii"),
        }
    )
    return {"head": head.encode(), "main_ref": main_ref, "check_runs": check_runs, "workflow_blob": workflow_blob}


def validate_generated_CI_fixture(
    packet: Mapping[str, object],
    fixture: Mapping[str, bytes],
) -> dict[str, object]:
    head = fixture.get("head", b"").decode("ascii", errors="strict")
    if len(head) != 40 or any(character not in "0123456789abcdef" for character in head):
        _refuse("CI_REFUSE", "local HEAD fixture differs")
    main_ref = _mapping(strict_json_loads(fixture.get("main_ref", b"")), "CI_REFUSE")
    main_object = _mapping(main_ref.get("object"), "CI_REFUSE")
    if main_object.get("sha") != head:
        _refuse("CI_REFUSE", "remote main fixture differs")
    checks = _mapping(strict_json_loads(fixture.get("check_runs", b"")), "CI_REFUSE")
    rows = checks.get("check_runs")
    if checks.get("total_count") != 2 or not isinstance(rows, list) or len(rows) != 2:
        _refuse("CI_REFUSE", "check-run cardinality differs")
    expected_names = ["Base Python", "Optional Neuro Readers"]
    if sorted(row.get("name") for row in rows if isinstance(row, Mapping)) != expected_names:
        _refuse("CI_REFUSE", "check-run names differ")
    for row in rows:
        item = _mapping(row, "CI_REFUSE")
        app = _mapping(item.get("app"), "CI_REFUSE")
        if (
            item.get("head_sha") != head
            or item.get("status") != "completed"
            or item.get("conclusion") != "success"
            or app.get("slug") != "github-actions"
        ):
            _refuse("CI_REFUSE", "check-run identity differs")
    blob = _mapping(strict_json_loads(fixture.get("workflow_blob", b"")), "CI_REFUSE")
    if blob.get("encoding") != "base64" or blob.get("sha") != "4246b7c7f6f8570df53b1b89705b496b30e38a78":
        _refuse("CI_REFUSE", "workflow blob identity differs")
    try:
        decoded = base64.b64decode(str(blob.get("content", "")), validate=True)
    except ValueError as exc:
        raise WitnessRefusal("CI_REFUSE", "workflow blob base64 differs") from exc
    ci = _mapping(packet["CI_W0_contract"], "CONTRACT_REFUSE")
    if len(decoded) != blob.get("size") or _sha256(decoded) != ci["workflow_blob_content_SHA256"]:
        _refuse("CI_REFUSE", "workflow blob content differs")
    return {
        "local_HEAD_sha256": _sha256(head.encode()),
        "main_ref_response_sha256": _sha256(fixture["main_ref"]),
        "check_runs_response_sha256": _sha256(fixture["check_runs"]),
        "workflow_blob_response_sha256": _sha256(fixture["workflow_blob"]),
        "Base_Python_check_run_id": 101,
        "Optional_Neuro_Readers_check_run_id": 102,
    }


def validate_state_transcript(value: object) -> None:
    packet = load_packet()
    firewall = _mapping(packet["attempt_and_transport_firewall"], "CONTRACT_REFUSE")
    expected = firewall["state_machine"]
    if value != expected:
        _refuse("TRANSPORT_REFUSE", "attempt state ordering differs")


def _walk_public(value: object, *, path: tuple[str, ...] = ()) -> None:
    forbidden_keys = {"candidate", "candidates", "target", "targets", "label", "labels", "reference_text"}
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key.casefold() in forbidden_keys:
                _refuse("TARGET_FIREWALL_REFUSE", f"forbidden public key: {'.'.join(path + (key,))}")
            _walk_public(child, path=path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_public(child, path=path + (str(index),))
    elif isinstance(value, str) and "REFERENCE_TARGET_DO_NOT_RETAIN" in value:
        _refuse("TARGET_FIREWALL_REFUSE", "poison candidate escaped")


def validate_public_report(report: Mapping[str, object]) -> None:
    _walk_public(report)
    if report.get("route") != "GENERATED_WITNESS_QUALIFIED":
        _refuse("OUTPUT_REFUSE", "generated report route differs")
    counters = _mapping(report.get("operation_counters"), "OUTPUT_REFUSE")
    protected = (
        "network_requests",
        "network_bytes",
        "official_index_requests",
        "candidate_semantic_operations",
        "source_selections",
        "payload_or_neural_reads",
        "target_or_label_reads",
        "model_runs",
        "training_runs",
        "prediction_sets",
        "scoring_events",
        "scientific_claim_upgrades",
    )
    if any(counters.get(name) != 0 for name in protected):
        _refuse("OUTPUT_REFUSE", "protected operation counter is nonzero")
    if report.get("claim_boundary") != CLAIM_BOUNDARY:
        _refuse("OUTPUT_REFUSE", "claim boundary differs")
    if len(canonical_json_bytes(report, newline=True)) > MAX_REPORT_BYTES:
        _refuse("OUTPUT_REFUSE", "report byte cap exceeded")


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], object],
) -> dict[str, str]:
    try:
        operation()
    except WitnessRefusal as exc:
        if exc.route != expected_route:
            raise WitnessRefusal("SCHEMA_REFUSE", f"wrong refusal route for {name}: {exc.route}") from exc
        return {"name": name, "route": exc.route}
    _refuse("SCHEMA_REFUSE", f"mutation accepted: {name}")


def run_refusal_matrix(
    repo_root: str | Path | None = None,
    *,
    baseline_ledger: Mapping[str, object] | None = None,
) -> list[dict[str, str]]:
    packet = load_packet(repo_root)
    ledger = run_generated_replay(repo_root) if baseline_ledger is None else baseline_ledger
    fixture = build_generated_fixture(repo_root)
    ci_fixture = build_generated_CI_fixture(repo_root)
    observations: list[dict[str, str]] = []

    def mutated_ledger(mutator: Callable[[dict[str, object]], None]) -> None:
        value = copy.deepcopy(ledger)
        mutator(value)
        validate_ledger(packet, value)

    ledger_cases: tuple[tuple[str, Callable[[dict[str, object]], None]], ...] = (
        ("outer_count", lambda value: value.__setitem__("total_root_count", 16)),
        ("profile_order", lambda value: value["profiles"].reverse()),
        ("profile_hash", lambda value: value["profile_sha256_values"].__setitem__(0, "0" * 64)),
        ("root_membership", lambda value: value["profiles"][0]["root_ordinals"].__setitem__(0, 1)),
        ("root_hash", lambda value: value["profiles"][0]["root_sha256_values"].__setitem__(0, "0" * 64)),
        ("page_gap", lambda value: value["profiles"][0]["roots"][0]["pages"][1].__setitem__("page_ordinal", 2)),
        ("page_hash", lambda value: value["profiles"][0]["roots"][0]["pages"][0].__setitem__("canonical_page_ledger_sha256", "0" * 64)),
        ("terminal_next", lambda value: value["profiles"][0]["roots"][0]["pages"][1].__setitem__("next_request_identity_sha256", "1" * 64)),
        ("peer_binding", lambda value: value["profiles"][0]["roots"][0]["pages"][0]["transport_evidence"].__setitem__("selected_and_post_connect_peer_equal_and_global", False)),
        ("encoding", lambda value: value["profiles"][0]["roots"][0]["pages"][0]["transport_evidence"].__setitem__("content_encoding", "gzip")),
    )
    for name, mutator in ledger_cases:
        observations.append(
            _expect_refusal(name, "HASH_TREE_REFUSE" if name not in {"peer_binding", "encoding"} else "TRANSPORT_REFUSE", lambda mutator=mutator: mutated_ledger(mutator))
        )

    first = fixture["exchanges"][0]
    if not isinstance(first, FixtureExchange):
        _refuse("SCHEMA_REFUSE", "fixture row differs")
    bad_exchange = FixtureExchange("0" * 64, first.media_type, first.response_body, first.response_headers)
    bad_fixture = {**fixture, "exchanges": [bad_exchange, *fixture["exchanges"][1:]]}
    observations.append(
        _expect_refusal(
            "request_identity",
            "REQUEST_REFUSE",
            lambda: run_generated_replay(repo_root, fixture=bad_fixture),
        )
    )
    observations.extend(
        (
            _expect_refusal(
                "generic_ambiguous",
                "PAGINATION_REFUSE",
                lambda: extract_generic_json_control(b'{"next":null,"pagination":{"has_next":false}}'),
            ),
            _expect_refusal(
                "generic_missing",
                "PAGINATION_REFUSE",
                lambda: extract_generic_json_control(b'{"items":[]}'),
            ),
            _expect_refusal(
                "openneuro_mistyped",
                "PAGINATION_REFUSE",
                lambda: extract_openneuro_control(b'{"data":{"datasets":{"pageInfo":{"hasNextPage":"yes","endCursor":null}}}}'),
            ),
            _expect_refusal(
                "HTML_multiple_containers",
                "PAGINATION_REFUSE",
                lambda: extract_generic_html_control(b'<nav aria-label="pagination"></nav><div class="pager"></div>'),
            ),
        )
    )
    generic_root = build_root_plan(repo_root)[4]
    observations.extend(
        (
            _expect_refusal(
                "URL_scheme",
                "URL_REFUSE",
                lambda: canonicalize_continuation_url(packet, generic_root, generic_root.url, "http://nemar.org/search?q=x&page=2"),
            ),
            _expect_refusal(
                "URL_unknown_key",
                "URL_REFUSE",
                lambda: canonicalize_continuation_url(packet, generic_root, generic_root.url, "https://nemar.org/search?q=%22motor+imagery%22+EEG+EOG+EMG&token=x&page=2"),
            ),
            _expect_refusal(
                "URL_mixed_pagination",
                "URL_REFUSE",
                lambda: canonicalize_continuation_url(packet, generic_root, generic_root.url, _next_url(generic_root) + "&offset=2"),
            ),
        )
    )
    bad_ci = dict(ci_fixture)
    bad_ci["main_ref"] = canonical_json_bytes({"object": {"sha": "b" * 40}})
    observations.append(
        _expect_refusal(
            "CI_main",
            "CI_REFUSE",
            lambda: validate_generated_CI_fixture(packet, bad_ci),
        )
    )
    bad_checks = dict(ci_fixture)
    bad_checks["check_runs"] = canonical_json_bytes({"total_count": 0, "check_runs": []})
    observations.append(
        _expect_refusal(
            "CI_checks",
            "CI_REFUSE",
            lambda: validate_generated_CI_fixture(packet, bad_checks),
        )
    )
    observations.append(
        _expect_refusal(
            "state_order",
            "TRANSPORT_REFUSE",
            lambda: validate_state_transcript(["CLOSED", "ARMED_CONSUMED"]),
        )
    )
    poisoned_report = {
        "route": "GENERATED_WITNESS_QUALIFIED",
        "target": "REFERENCE_TARGET_DO_NOT_RETAIN",
        "operation_counters": {},
        "claim_boundary": CLAIM_BOUNDARY,
    }
    observations.append(
        _expect_refusal(
            "target_firewall",
            "TARGET_FIREWALL_REFUSE",
            lambda: validate_public_report(poisoned_report),
        )
    )
    return observations


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if os.uname().sysname == "Darwin" else value * 1024)


def _validate_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        _refuse("RESOURCE_REFUSE", "one-thread environment differs")


def registered_plan(repo_root: str | Path | None = None) -> dict[str, object]:
    packet = load_packet(repo_root)
    decision = load_green_decision(repo_root)
    roots = build_root_plan(repo_root)
    return {
        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_plan",
        "schema_version": "0.1.0",
        "packet_id": PACKET_ID,
        "implementation_id": IMPLEMENTATION_ID,
        "green_decision_id": decision["decision_id"],
        "green_decision_commit": GREEN_DECISION_COMMIT,
        "official_index_profiles": len(packet["index_profiles"]),
        "root_request_count": len(roots),
        "root_plan_sha256": _sha256(
            canonical_json_bytes(
                [
                    {
                        "root_ordinal": root.root_ordinal,
                        "index_id": root.index_id,
                        "query_or_category_id": root.query_or_category_id,
                        "url": root.url,
                        "method": root.method,
                        "body_sha256": _sha256(root.body),
                    }
                    for root in roots
                ],
                newline=True,
            )
        ),
        "commands": ["plan", "inspect-generated", "qualify-generated"],
        "live_or_execute_command_present": False,
        "network_import_or_opener_present": False,
        "candidate_parser_or_selector_present": False,
        "network_authorized": False,
        "scientific_claim_established": False,
    }


def inspect_generated(repo_root: str | Path | None = None) -> dict[str, object]:
    ledger = run_generated_replay(repo_root)
    return {
        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_inspection",
        "schema_version": "0.1.0",
        "packet_id": PACKET_ID,
        "route": "GENERATED_WITNESS_INSPECTED",
        "profile_count": len(ledger["profiles"]),
        "root_count": ledger["total_root_count"],
        "page_count": ledger["total_page_count"],
        "generated_entity_body_bytes": ledger["total_entity_body_bytes"],
        "global_ledger_sha256": ledger["canonical_global_ledger_sha256"],
        "network_requests": 0,
        "candidate_semantic_operations": 0,
        "payload_or_neural_reads": 0,
        "model_or_score_operations": 0,
        "scientific_claim_established": False,
    }


def run_generated_qualification(
    repo_root: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, object]:
    started = time.monotonic()
    active_environ = os.environ if environ is None else environ
    _validate_thread_environment(active_environ)
    packet = load_packet(repo_root)
    load_green_decision(repo_root)
    validate_state_transcript(packet["attempt_and_transport_firewall"]["state_machine"])
    ci_receipt = validate_generated_CI_fixture(packet, build_generated_CI_fixture(repo_root))
    first = run_generated_replay(repo_root)
    second = run_generated_replay(repo_root)
    if first != second:
        _refuse("HASH_TREE_REFUSE", "generated replay differs")
    refusals = run_refusal_matrix(repo_root, baseline_ledger=first)
    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    fixture = build_generated_fixture(repo_root)
    generated_input_bytes = sum(
        len(exchange.response_body) for exchange in fixture["exchanges"]
    )
    if runtime > MAX_RUNTIME_SECONDS or peak_rss > MAX_PEAK_RSS_BYTES:
        _refuse("RESOURCE_REFUSE", "runtime or peak RSS cap exceeded")
    if generated_input_bytes > MAX_GENERATED_INPUT_BYTES:
        _refuse("RESOURCE_REFUSE", "generated input cap exceeded")
    report = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "implementation_id": IMPLEMENTATION_ID,
        "route": "GENERATED_WITNESS_QUALIFIED",
        "replay_count": 2,
        "replay_ledger_sha256": first["canonical_global_ledger_sha256"],
        "profile_count": len(first["profiles"]),
        "root_count": first["total_root_count"],
        "page_count": first["total_page_count"],
        "generated_input_bytes": generated_input_bytes,
        "generated_entity_body_bytes": first["total_entity_body_bytes"],
        "refusal_observations": len(refusals),
        "refusal_routes": sorted({row["route"] for row in refusals}),
        "CI_fixture_receipt_sha256": _sha256(canonical_json_bytes(ci_receipt, newline=True)),
        "runtime_seconds": runtime,
        "peak_RSS_bytes": peak_rss,
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
        "producer_is_causal": "not_applicable_source_identity_only",
        "end_to_end_latency_measured": False,
        "warnings": list(WARNINGS),
        "unavailable_fields": list(UNAVAILABLE_FIELDS),
        "operation_counters": {
            "generated_fixture_exchanges": len(fixture["exchanges"]),
            "generated_replays": 2,
            "generated_CI_fixture_validations": 1,
            "network_requests": 0,
            "network_bytes": 0,
            "official_index_requests": 0,
            "candidate_semantic_operations": 0,
            "source_selections": 0,
            "payload_or_neural_reads": 0,
            "target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scoring_events": 0,
            "scientific_claim_upgrades": 0,
        },
        "claim_boundary": dict(CLAIM_BOUNDARY),
    }
    validate_public_report(report)
    report["report_bytes"] = len(canonical_json_bytes(report, newline=True))
    if report["report_bytes"] > MAX_REPORT_BYTES:
        _refuse("OUTPUT_REFUSE", "report byte cap exceeded")
    return report
