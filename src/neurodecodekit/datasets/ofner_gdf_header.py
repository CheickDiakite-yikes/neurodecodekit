"""Generated-only GDF header parser and range firewall for Ofner 2017.

The module contains no network client and no real-data execution path. It can
parse only a complete, header-only GDF 2.x byte string and validate injected
HTTP range transcripts produced by generated fixtures.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import resource
import struct
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

CONTRACT_RELATIVE_PATH = (
    "registries/ofner_2017_motor_imagery_fixed_header_contract.v0.json"
)
CONTRACT_SHA256 = "c556049ddabdefe3f4de06d451954b8df99508c17ac950850bb8cf83e55fdae5"
FIXED_HEADER_BYTES = 256
HEADER_BLOCK_BYTES = 256
MAXIMUM_HEADER_BYTES = 65_536
EXPECTED_SIGNALS = 96
THREAD_ENV_NAMES = (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
_VERSION_RE = re.compile(r"GDF 2\.\d{2}\Z")
_CONTENT_RANGE_RE = re.compile(r"bytes (0|[1-9]\d*)-(0|[1-9]\d*)/(0|[1-9]\d*)\Z")
_NORMALIZE_SEPARATORS_RE = re.compile(r"[\s_]+")


class OfnerGDFHeaderRefusal(RuntimeError):
    """A GDF header or injected transport transcript failed closed."""


@dataclass(frozen=True)
class FixedHeaderDescriptor:
    """Allowlisted structural fields from the mandatory 256-byte header."""

    version: str
    header_length_blocks: int
    header_bytes: int
    record_duration_numerator: int
    record_duration_denominator: int
    number_of_signals: int


@dataclass(frozen=True)
class ParsedHeader:
    """Target-free measurement summary from a complete header-only payload."""

    version: str
    header_bytes: int
    number_of_signals: int
    sampling_rate_hz: int
    EEG_channels: int
    EOG_channels: int
    glove_channels: int
    arm_channels: int
    unique_normalized_labels: int
    finite_nonzero_EEG_geometry_channels: int
    complete_header_sha256: str


@dataclass(frozen=True)
class RangeResponse:
    """Injected, inert representation of one HTTP range response."""

    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes
    redirects: int = 0


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_json_object(payload: bytes) -> dict[str, object]:
    if not payload or len(payload) > 1024 * 1024 or payload.startswith(b"\xef\xbb\xbf"):
        raise OfnerGDFHeaderRefusal("contract bytes are absent, encoded differently, or too large")

    def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, child in pairs:
            if key in value:
                raise OfnerGDFHeaderRefusal("contract JSON key is duplicated")
            value[key] = child
        return value

    try:
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=strict_object,
            parse_constant=lambda _value: (_ for _ in ()).throw(
                OfnerGDFHeaderRefusal("contract JSON constant is non-finite")
            ),
        )
    except OfnerGDFHeaderRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise OfnerGDFHeaderRefusal("contract JSON is invalid") from exc
    if not isinstance(value, dict):
        raise OfnerGDFHeaderRefusal("contract JSON is not an object")
    return value


def load_registered_contract(repo_root: str | Path) -> dict[str, object]:
    """Load the exact remotely registered contract without network access."""

    path = Path(repo_root) / CONTRACT_RELATIVE_PATH
    payload = path.read_bytes()
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise OfnerGDFHeaderRefusal("registered header contract hash differs")
    contract = _strict_json_object(payload)
    if contract.get("protocol_id") != "OFNER-C6R-1-HG0":
        raise OfnerGDFHeaderRefusal("registered header protocol differs")
    green = contract.get("green_basis")
    if not isinstance(green, dict) or green.get("both_proof_closeout_jobs_green") is not True:
        raise OfnerGDFHeaderRefusal("registered header basis is not remotely green")
    return contract


def registered_plan(repo_root: str | Path) -> dict[str, object]:
    """Return the generated-only plan and explicit absent capabilities."""

    contract = load_registered_contract(repo_root)
    exact_member = contract["exact_member"]
    generated = contract["generated_qualification_plan"]
    envelope = contract["resource_envelope"]
    assert isinstance(exact_member, dict)
    assert isinstance(generated, dict)
    assert isinstance(envelope, dict)
    return {
        "schema_name": "neurodecodekit.ofner_gdf_header_plan",
        "schema_version": "0.1.0",
        "protocol_id": contract["protocol_id"],
        "mode": "generated_only",
        "exact_future_member_path": exact_member["path"],
        "future_combined_GDF_body_bytes_maximum": 65_536,
        "generated_replays": generated["generated_replays"],
        "minimum_named_refusal_cases": generated["minimum_named_refusal_cases"],
        "runtime_seconds_maximum": envelope["runtime_seconds_maximum"],
        "peak_RSS_bytes_maximum": envelope["peak_process_tree_RSS_bytes_maximum"],
        "network_client_present": False,
        "real_execution_command_present": False,
        "event_parser_present": False,
        "signal_parser_present": False,
        "model_or_scorer_present": False,
        "warnings": [
            "generated_header_bytes_are_not_EEG",
            "real_header_access_requires_a_separate_Tier_C_packet_and_decision",
            "no_scientific_claim",
        ],
    }


def _require_header_bytes(payload: bytes, expected: int, message: str) -> None:
    if not isinstance(payload, bytes) or len(payload) != expected:
        raise OfnerGDFHeaderRefusal(message)


def parse_fixed_header(payload: bytes) -> FixedHeaderDescriptor:
    """Parse only allowlisted structural fields from exactly 256 bytes."""

    _require_header_bytes(payload, FIXED_HEADER_BYTES, "fixed header must be exactly 256 bytes")
    try:
        version = payload[0:8].decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise OfnerGDFHeaderRefusal("GDF version is not ASCII") from exc
    if _VERSION_RE.fullmatch(version) is None:
        raise OfnerGDFHeaderRefusal("only an exact GDF 2.x version is accepted")

    header_length_blocks = struct.unpack_from("<H", payload, 184)[0]
    duration_numerator = struct.unpack_from("<I", payload, 244)[0]
    duration_denominator = struct.unpack_from("<I", payload, 248)[0]
    number_of_signals = struct.unpack_from("<H", payload, 252)[0]
    if number_of_signals != EXPECTED_SIGNALS:
        raise OfnerGDFHeaderRefusal("GDF signal count differs from 96")
    if duration_numerator == 0 or duration_denominator == 0:
        raise OfnerGDFHeaderRefusal("GDF record duration is zero")

    header_bytes = header_length_blocks * HEADER_BLOCK_BYTES
    minimum_header_bytes = (number_of_signals + 1) * HEADER_BLOCK_BYTES
    if header_bytes < minimum_header_bytes:
        raise OfnerGDFHeaderRefusal("GDF header is shorter than fixed plus channel headers")
    if header_bytes > MAXIMUM_HEADER_BYTES:
        raise OfnerGDFHeaderRefusal("GDF header exceeds the frozen byte cap")
    return FixedHeaderDescriptor(
        version=version,
        header_length_blocks=header_length_blocks,
        header_bytes=header_bytes,
        record_duration_numerator=duration_numerator,
        record_duration_denominator=duration_denominator,
        number_of_signals=number_of_signals,
    )


def _normalize_label(raw: bytes) -> str:
    trimmed = raw.rstrip(b"\x00 ")
    if not trimmed or b"\x00" in trimmed:
        raise OfnerGDFHeaderRefusal("channel label is empty or internally NUL-padded")
    try:
        text = trimmed.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise OfnerGDFHeaderRefusal("channel label is not ASCII") from exc
    if any(ord(character) < 32 or ord(character) == 127 for character in text):
        raise OfnerGDFHeaderRefusal("channel label contains a control character")
    normalized = _NORMALIZE_SEPARATORS_RE.sub("-", text.strip().lower())
    if not normalized or len(normalized) > 32:
        raise OfnerGDFHeaderRefusal("normalized channel label is invalid")
    return normalized


def _expected_groups(contract: Mapping[str, object]) -> tuple[tuple[str, ...], ...]:
    expected = contract.get("expected_measurement_contract")
    if not isinstance(expected, dict):
        raise OfnerGDFHeaderRefusal("expected measurement contract is absent")
    groups: list[tuple[str, ...]] = []
    for key, count in (
        ("EEG_labels", 61),
        ("EOG_labels", 3),
        ("glove_labels", 19),
        ("arm_labels", 13),
    ):
        values = expected.get(key)
        if (
            not isinstance(values, list)
            or len(values) != count
            or not all(isinstance(value, str) and value for value in values)
        ):
            raise OfnerGDFHeaderRefusal(f"registered {key} roster is invalid")
        group = tuple(values)
        if len(set(group)) != len(group):
            raise OfnerGDFHeaderRefusal(f"registered {key} roster is duplicated")
        groups.append(group)
    flattened = tuple(label for group in groups for label in group)
    if len(flattened) != EXPECTED_SIGNALS or len(set(flattened)) != EXPECTED_SIGNALS:
        raise OfnerGDFHeaderRefusal("registered channel roster is not globally unique")
    return tuple(groups)


def parse_complete_header(payload: bytes, contract: Mapping[str, object]) -> ParsedHeader:
    """Parse and validate one complete header with no trailing data bytes."""

    if not isinstance(payload, bytes) or len(payload) < FIXED_HEADER_BYTES:
        raise OfnerGDFHeaderRefusal("complete header is absent or truncated")
    fixed = parse_fixed_header(payload[:FIXED_HEADER_BYTES])
    if len(payload) != fixed.header_bytes:
        raise OfnerGDFHeaderRefusal("complete header length differs or contains trailing bytes")

    signal_count = fixed.number_of_signals
    label_start = FIXED_HEADER_BYTES
    labels = tuple(
        _normalize_label(payload[label_start + index * 16 : label_start + (index + 1) * 16])
        for index in range(signal_count)
    )
    if len(set(labels)) != signal_count:
        raise OfnerGDFHeaderRefusal("normalized channel labels are not unique")

    expected_groups = _expected_groups(contract)
    boundaries = (0, 61, 64, 83, 96)
    for index, expected_group in enumerate(expected_groups):
        observed = labels[boundaries[index] : boundaries[index + 1]]
        if set(observed) != set(expected_group):
            raise OfnerGDFHeaderRefusal("channel role roster differs from the frozen contract")

    samples_offset = FIXED_HEADER_BYTES + 216 * signal_count
    positions_offset = FIXED_HEADER_BYTES + 224 * signal_count
    samples = struct.unpack_from(f"<{signal_count}I", payload, samples_offset)
    expected_rate = 512
    for value in samples:
        if value == 0 or (
            value * fixed.record_duration_denominator
            != expected_rate * fixed.record_duration_numerator
        ):
            raise OfnerGDFHeaderRefusal("channel sampling rate differs from 512 Hz")

    coordinates = struct.unpack_from(f"<{signal_count * 3}f", payload, positions_offset)
    if not all(math.isfinite(value) for value in coordinates):
        raise OfnerGDFHeaderRefusal("sensor geometry contains a non-finite value")
    finite_nonzero_EEG_geometry = 0
    for channel in range(61):
        xyz = coordinates[channel * 3 : channel * 3 + 3]
        if any(value != 0.0 for value in xyz):
            finite_nonzero_EEG_geometry += 1

    return ParsedHeader(
        version=fixed.version,
        header_bytes=fixed.header_bytes,
        number_of_signals=signal_count,
        sampling_rate_hz=expected_rate,
        EEG_channels=61,
        EOG_channels=3,
        glove_channels=19,
        arm_channels=13,
        unique_normalized_labels=len(set(labels)),
        finite_nonzero_EEG_geometry_channels=finite_nonzero_EEG_geometry,
        complete_header_sha256=_sha256_bytes(payload),
    )


def _strict_headers(pairs: Sequence[tuple[str, str]]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for raw_name, raw_value in pairs:
        if not isinstance(raw_name, str) or not isinstance(raw_value, str):
            raise OfnerGDFHeaderRefusal("range response header is not text")
        name = raw_name.strip().lower()
        value = raw_value.strip()
        if not name or name in headers or "\r" in value or "\n" in value:
            raise OfnerGDFHeaderRefusal("range response headers are duplicated or malformed")
        headers[name] = value
    return headers


def validate_range_response(
    response: RangeResponse,
    *,
    expected_start: int,
    expected_end: int,
    expected_total: int,
) -> bytes:
    """Validate an injected HTTP 206 transcript without performing I/O."""

    if response.status != 206:
        raise OfnerGDFHeaderRefusal("range response status is not 206")
    if response.redirects != 0:
        raise OfnerGDFHeaderRefusal("range response followed a redirect")
    if not 0 <= expected_start <= expected_end < expected_total:
        raise OfnerGDFHeaderRefusal("expected range is invalid")
    headers = _strict_headers(response.headers)
    if "transfer-encoding" in headers:
        raise OfnerGDFHeaderRefusal("range response uses transfer encoding")
    if headers.get("content-encoding", "identity").lower() != "identity":
        raise OfnerGDFHeaderRefusal("range response is encoded")
    raw_range = headers.get("content-range")
    if raw_range is None:
        raise OfnerGDFHeaderRefusal("range response lacks Content-Range")
    match = _CONTENT_RANGE_RE.fullmatch(raw_range)
    if match is None:
        raise OfnerGDFHeaderRefusal("range response Content-Range is malformed")
    observed_start, observed_end, observed_total = (int(value) for value in match.groups())
    if (observed_start, observed_end, observed_total) != (
        expected_start,
        expected_end,
        expected_total,
    ):
        raise OfnerGDFHeaderRefusal("range response Content-Range differs")
    raw_length = headers.get("content-length")
    if raw_length is None or not raw_length.isascii() or not raw_length.isdigit():
        raise OfnerGDFHeaderRefusal("range response Content-Length is absent or malformed")
    expected_length = expected_end - expected_start + 1
    if int(raw_length) != expected_length or len(response.body) != expected_length:
        raise OfnerGDFHeaderRefusal("range response body length differs")
    return response.body


def assemble_two_range_header(
    first: RangeResponse,
    second: RangeResponse,
    *,
    expected_total: int,
) -> bytes:
    """Validate and assemble the exact two non-overlapping header ranges."""

    fixed_bytes = validate_range_response(
        first,
        expected_start=0,
        expected_end=FIXED_HEADER_BYTES - 1,
        expected_total=expected_total,
    )
    descriptor = parse_fixed_header(fixed_bytes)
    if descriptor.header_bytes <= FIXED_HEADER_BYTES:
        raise OfnerGDFHeaderRefusal("complete variable header range is absent")
    variable_bytes = validate_range_response(
        second,
        expected_start=FIXED_HEADER_BYTES,
        expected_end=descriptor.header_bytes - 1,
        expected_total=expected_total,
    )
    header = fixed_bytes + variable_bytes
    if len(header) != descriptor.header_bytes:
        raise OfnerGDFHeaderRefusal("assembled header length differs")
    return header


def _fixture_labels(contract: Mapping[str, object]) -> tuple[str, ...]:
    return tuple(label for group in _expected_groups(contract) for label in group)


def build_generated_header(contract: Mapping[str, object]) -> bytes:
    """Build a deterministic header-only GDF 2.x fixture with no data section."""

    header_blocks = EXPECTED_SIGNALS + 1
    payload = bytearray(header_blocks * HEADER_BLOCK_BYTES)
    payload[0:8] = b"GDF 2.20"
    struct.pack_into("<H", payload, 184, header_blocks)
    struct.pack_into("<I", payload, 244, 1)
    struct.pack_into("<I", payload, 248, 1)
    struct.pack_into("<H", payload, 252, EXPECTED_SIGNALS)

    for index, label in enumerate(_fixture_labels(contract)):
        encoded = label.encode("ascii")
        if len(encoded) > 16:
            raise OfnerGDFHeaderRefusal("generated channel label exceeds GDF width")
        offset = FIXED_HEADER_BYTES + index * 16
        payload[offset : offset + len(encoded)] = encoded

    samples_offset = FIXED_HEADER_BYTES + 216 * EXPECTED_SIGNALS
    positions_offset = FIXED_HEADER_BYTES + 224 * EXPECTED_SIGNALS
    for index in range(EXPECTED_SIGNALS):
        struct.pack_into("<I", payload, samples_offset + index * 4, 512)
        if index < 61:
            struct.pack_into(
                "<fff",
                payload,
                positions_offset + index * 12,
                (index % 11 - 5) / 10.0,
                (index // 11 - 2) / 10.0,
                0.5 + index / 1000.0,
            )
    return bytes(payload)


def _range_response(
    body: bytes,
    *,
    start: int,
    total: int,
    status: int = 206,
    redirects: int = 0,
    extra_headers: Sequence[tuple[str, str]] = (),
    replace_headers: Mapping[str, str | None] | None = None,
) -> RangeResponse:
    end = start + len(body) - 1
    headers: list[tuple[str, str]] = [
        ("Content-Range", f"bytes {start}-{end}/{total}"),
        ("Content-Length", str(len(body))),
        ("Content-Encoding", "identity"),
    ]
    if replace_headers:
        replacements = {key.lower(): value for key, value in replace_headers.items()}
        headers = [
            (name, replacements.get(name.lower(), value))
            for name, value in headers
            if replacements.get(name.lower(), value) is not None
        ]
        existing = {name.lower() for name, _value in headers}
        for name, value in replace_headers.items():
            if value is not None and name.lower() not in existing:
                headers.append((name, value))
    headers.extend(extra_headers)
    return RangeResponse(
        status=status,
        headers=tuple((name, str(value)) for name, value in headers),
        body=body,
        redirects=redirects,
    )


def _replace_bytes(payload: bytes, offset: int, replacement: bytes) -> bytes:
    result = bytearray(payload)
    result[offset : offset + len(replacement)] = replacement
    return bytes(result)


def _set_label(payload: bytes, index: int, label: bytes) -> bytes:
    if len(label) > 16:
        raise AssertionError("test label exceeds GDF width")
    result = bytearray(payload)
    offset = FIXED_HEADER_BYTES + index * 16
    result[offset : offset + 16] = b"\x00" * 16
    result[offset : offset + len(label)] = label
    return bytes(result)


def _expect_refusal(name: str, operation: Callable[[], object]) -> str:
    try:
        operation()
    except OfnerGDFHeaderRefusal:
        return name
    raise AssertionError(f"generated refusal case unexpectedly passed: {name}")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _assert_thread_boundary() -> None:
    for name in THREAD_ENV_NAMES:
        value = os.environ.get(name)
        if value not in {None, "1"}:
            raise OfnerGDFHeaderRefusal(f"{name} must be unset or 1")


def run_generated_qualification(repo_root: str | Path) -> dict[str, object]:
    """Run the one bounded generated qualification defined by HG0."""

    _assert_thread_boundary()
    started = time.perf_counter()
    contract = load_registered_contract(repo_root)
    fixture = build_generated_header(contract)
    total = int(contract["exact_member"]["declared_payload_bytes"])  # type: ignore[index]

    replay_summaries: list[dict[str, object]] = []
    transcript_digests: list[str] = []
    for _replay in range(2):
        first = _range_response(fixture[:256], start=0, total=total)
        second = _range_response(fixture[256:], start=256, total=total)
        assembled = assemble_two_range_header(first, second, expected_total=total)
        parsed = parse_complete_header(assembled, contract)
        replay_summaries.append(asdict(parsed))
        transcript_digests.append(
            _sha256_bytes(
                json.dumps(
                    {
                        "first": _sha256_bytes(first.body),
                        "second": _sha256_bytes(second.body),
                        "summary": asdict(parsed),
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("ascii")
            )
        )
    if replay_summaries[0] != replay_summaries[1] or len(set(transcript_digests)) != 1:
        raise OfnerGDFHeaderRefusal("generated header replays differ")

    fixed = fixture[:256]
    first = _range_response(fixed, start=0, total=total)
    second = _range_response(fixture[256:], start=256, total=total)
    samples_offset = FIXED_HEADER_BYTES + 216 * EXPECTED_SIGNALS
    positions_offset = FIXED_HEADER_BYTES + 224 * EXPECTED_SIGNALS
    malformed: list[tuple[str, Callable[[], object]]] = [
        ("fixed_short", lambda: parse_fixed_header(fixed[:-1])),
        ("fixed_long", lambda: parse_fixed_header(fixed + b"0")),
        ("version_prefix_wrong", lambda: parse_fixed_header(_replace_bytes(fixed, 0, b"EDF 2.20"))),
        ("version_non_ascii", lambda: parse_fixed_header(_replace_bytes(fixed, 0, b"GDF 2.\xff0"))),
        ("version_1x", lambda: parse_fixed_header(_replace_bytes(fixed, 0, b"GDF 1.25"))),
        ("header_blocks_zero", lambda: parse_fixed_header(_replace_bytes(fixed, 184, b"\x00\x00"))),
        ("header_blocks_short", lambda: parse_fixed_header(_replace_bytes(fixed, 184, b"`\x00"))),
        ("header_blocks_over_cap", lambda: parse_fixed_header(_replace_bytes(fixed, 184, b"\x01\x01"))),
        ("duration_numerator_zero", lambda: parse_fixed_header(_replace_bytes(fixed, 244, b"\x00" * 4))),
        ("duration_denominator_zero", lambda: parse_fixed_header(_replace_bytes(fixed, 248, b"\x00" * 4))),
        ("signals_zero", lambda: parse_fixed_header(_replace_bytes(fixed, 252, b"\x00\x00"))),
        ("signals_95", lambda: parse_fixed_header(_replace_bytes(fixed, 252, b"_\x00"))),
        ("complete_truncated", lambda: parse_complete_header(fixture[:-1], contract)),
        ("complete_trailing", lambda: parse_complete_header(fixture + b"\x00", contract)),
        ("label_duplicate", lambda: parse_complete_header(_set_label(fixture, 1, b"c1"), contract)),
        ("label_empty", lambda: parse_complete_header(_set_label(fixture, 0, b""), contract)),
        ("label_non_ascii", lambda: parse_complete_header(_set_label(fixture, 0, b"c\xff"), contract)),
        ("label_control", lambda: parse_complete_header(_set_label(fixture, 0, b"c\x01"), contract)),
        ("EEG_roster_wrong", lambda: parse_complete_header(_set_label(fixture, 0, b"not-eeg"), contract)),
        ("EOG_roster_wrong", lambda: parse_complete_header(_set_label(fixture, 61, b"not-eog"), contract)),
        ("glove_roster_wrong", lambda: parse_complete_header(_set_label(fixture, 64, b"not-glove"), contract)),
        ("arm_roster_wrong", lambda: parse_complete_header(_set_label(fixture, 83, b"not-arm"), contract)),
        ("sampling_zero", lambda: parse_complete_header(_replace_bytes(fixture, samples_offset, b"\x00" * 4), contract)),
        ("sampling_511", lambda: parse_complete_header(_replace_bytes(fixture, samples_offset, struct.pack("<I", 511)), contract)),
        ("geometry_nan", lambda: parse_complete_header(_replace_bytes(fixture, positions_offset, struct.pack("<f", math.nan)), contract)),
        ("range_status_200", lambda: validate_range_response(_range_response(fixed, start=0, total=total, status=200), expected_start=0, expected_end=255, expected_total=total)),
        ("range_redirect", lambda: validate_range_response(_range_response(fixed, start=0, total=total, redirects=1), expected_start=0, expected_end=255, expected_total=total)),
        ("range_duplicate_header", lambda: validate_range_response(_range_response(fixed, start=0, total=total, extra_headers=(("content-length", "256"),)), expected_start=0, expected_end=255, expected_total=total)),
        ("range_missing_content_range", lambda: validate_range_response(_range_response(fixed, start=0, total=total, replace_headers={"content-range": None}), expected_start=0, expected_end=255, expected_total=total)),
        ("range_malformed_content_range", lambda: validate_range_response(_range_response(fixed, start=0, total=total, replace_headers={"content-range": "bytes nope"}), expected_start=0, expected_end=255, expected_total=total)),
        ("range_wrong_start", lambda: validate_range_response(_range_response(fixed, start=1, total=total), expected_start=0, expected_end=255, expected_total=total)),
        ("range_wrong_total", lambda: validate_range_response(_range_response(fixed, start=0, total=total + 1), expected_start=0, expected_end=255, expected_total=total)),
        ("range_missing_length", lambda: validate_range_response(_range_response(fixed, start=0, total=total, replace_headers={"content-length": None}), expected_start=0, expected_end=255, expected_total=total)),
        ("range_bad_length", lambda: validate_range_response(_range_response(fixed, start=0, total=total, replace_headers={"content-length": "255"}), expected_start=0, expected_end=255, expected_total=total)),
        ("range_gzip", lambda: validate_range_response(_range_response(fixed, start=0, total=total, replace_headers={"content-encoding": "gzip"}), expected_start=0, expected_end=255, expected_total=total)),
        ("range_transfer_encoding", lambda: validate_range_response(_range_response(fixed, start=0, total=total, extra_headers=(("transfer-encoding", "chunked"),)), expected_start=0, expected_end=255, expected_total=total)),
        ("range_body_short", lambda: validate_range_response(_range_response(fixed[:-1], start=0, total=total), expected_start=0, expected_end=255, expected_total=total)),
        ("second_range_gap", lambda: assemble_two_range_header(first, _range_response(fixture[256:], start=257, total=total), expected_total=total)),
        ("second_range_overlap", lambda: assemble_two_range_header(first, _range_response(fixture[256:], start=255, total=total), expected_total=total)),
        ("second_range_trailing", lambda: assemble_two_range_header(first, _range_response(fixture[256:] + b"0", start=256, total=total), expected_total=total)),
        ("first_total_wrong", lambda: assemble_two_range_header(_range_response(fixed, start=0, total=total + 1), second, expected_total=total)),
    ]
    refusal_ids = [_expect_refusal(name, operation) for name, operation in malformed]
    if len(refusal_ids) < 30 or len(set(refusal_ids)) != len(refusal_ids):
        raise AssertionError("generated refusal ledger is incomplete or duplicated")

    runtime_seconds = time.perf_counter() - started
    if runtime_seconds > 30:
        raise OfnerGDFHeaderRefusal("generated qualification exceeded runtime cap")
    peak_rss_bytes = _peak_rss_bytes()
    if peak_rss_bytes > 268_435_456:
        raise OfnerGDFHeaderRefusal("generated qualification exceeded RSS cap")
    result = {
        "schema_name": "neurodecodekit.ofner_gdf_header_generated_qualification",
        "schema_version": "0.1.0",
        "protocol_id": "OFNER-C6R-1-HG0",
        "status": "accepted_generated_only",
        "contract": {
            "path": CONTRACT_RELATIVE_PATH,
            "sha256": CONTRACT_SHA256,
        },
        "measurements": {
            "generated_replays": 2,
            "generated_header_bytes_per_replay": len(fixture),
            "range_transcripts_per_replay": 2,
            "combined_range_body_bytes_per_replay": len(fixture),
            "named_adversarial_refusals": len(refusal_ids),
            "runtime_seconds": runtime_seconds,
            "peak_rss_bytes": peak_rss_bytes,
            "network_bytes": 0,
            "retained_generated_payload_bytes": 0,
        },
        "determinism": {
            "replay_summaries_equal": True,
            "transcript_digests_equal": True,
            "transcript_sha256": transcript_digests[0],
        },
        "parsed_header": replay_summaries[0],
        "refusal_ids": refusal_ids,
        "capabilities": {
            "GDF_2x_header_parser_present": True,
            "two_range_firewall_present": True,
            "network_client_present": False,
            "real_execution_command_present": False,
            "event_parser_present": False,
            "signal_parser_present": False,
            "model_or_scorer_present": False,
        },
        "operation_counters": {
            "real_manifest_requests": 0,
            "real_GDF_requests": 0,
            "real_GDF_bytes": 0,
            "real_header_reads": 0,
            "event_or_annotation_reads": 0,
            "signal_sample_reads": 0,
            "target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scores": 0,
        },
        "warnings": [
            "generated_header_bytes_are_not_EEG",
            "no_real_measurement_contract_verified",
            "no_neural_advantage_or_unseen_person_result",
            "no_scientific_claim",
        ],
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("ascii")
    if len(encoded) > 1024 * 1024:
        raise OfnerGDFHeaderRefusal("generated qualification output exceeds cap")
    return result
