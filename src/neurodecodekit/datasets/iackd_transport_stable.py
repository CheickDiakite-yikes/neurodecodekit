"""Zero-network qualification for transport-stable IACKD response identity."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import resource
import stat
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping


SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_NAME = "neurodecodekit.iackd_transport_stable_qualification"
CONTRACT_RELATIVE_PATH = Path(
    "registries/iackd_transport_stable_recovery_contract.v0.json"
)
CONTRACT_SHA256 = "d2208ea8a7aca1a3c2788ec00e9a892c1cc4b630e25b2a911f822530a80624e4"
GREEN_REGISTRATION_COMMIT = "ee0f62adf74afd390052694142090ccc0395c539"
GREEN_REGISTRATION_CI_RUN_ID = 31_472_269_070
GREEN_REGISTRATION_BASE_JOB_ID = 93_717_995_481
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 93_717_995_427
MAX_REPORT_BYTES = 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
FORBIDDEN_GENERATED_TERMS = frozenset(
    {
        "intended_text",
        "label",
        "labels",
        "participant",
        "prediction",
        "predictions",
        "reference_text",
        "sentence",
        "sentences",
        "target",
        "targets",
        "trajectory",
    }
)
REFUSAL_IDS = (
    "IACKDT-F00-contract-or-green-registration-mismatch",
    "IACKDT-F01-mode-spec-or-field-malformed",
    "IACKDT-F02-status-final-URL-or-redirect-failure",
    "IACKDT-F03-framing-ambiguity-or-invalid-field",
    "IACKDT-F04-content-encoding-failure",
    "IACKDT-F05-declared-length-or-read-cap-failure",
    "IACKDT-F06-body-read-underflow-overflow-or-error",
    "IACKDT-F07-body-SHA256-mismatch",
    "IACKDT-F08-payload-ETag-mismatch",
    "IACKDT-F09-read-hash-or-parse-order-violation",
    "IACKDT-F10-semantic-parse-failure",
    "IACKDT-F11-output-path-overwrite-or-cap",
    "IACKDT-F12-thread-runtime-or-RSS-cap",
    "IACKDT-F13-network-real-path-or-forbidden-fixture-field",
    "IACKDT-F14-deterministic-replay-mismatch",
)
REQUIRED_REFUSAL_MUTATIONS = (
    "non_200_status",
    "changed_final_URL",
    "redirect",
    "malformed_Content_Length",
    "negative_Content_Length",
    "comma_joined_Content_Length",
    "over_cap_Content_Length",
    "Content_Length_plus_Transfer_Encoding",
    "unsupported_Transfer_Encoding",
    "compressed_Content_Encoding",
    "body_underflow",
    "body_overflow",
    "body_read_error",
    "body_SHA256_drift",
    "second_read",
    "second_hash",
    "parse_before_identity",
    "payload_missing_or_different_Content_Length",
    "payload_missing_or_different_ETag",
    "unknown_mode_or_field",
    "network_or_real_path_attempt",
    "output_overwrite_or_cap",
)
REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "green_registration",
        "fixture_qualification",
        "measurements",
        "access_counters",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)


class TransportStableRefusal(RuntimeError):
    """Fail closed with one stable, non-sensitive refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown IACKD-T1 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class ResponseSpec:
    """Expected identity for one generated or future registered response."""

    url: str
    expected_bytes: int
    expected_sha256: str | None
    expected_etag: str | None = None


@dataclass(frozen=True)
class ResponseValidation:
    """Aggregate-safe outcome from one accepted response."""

    mode: str
    framing_profile: str
    content_length_state: str
    observed_bytes: int
    body_sha256: str
    etag_state: str
    read_calls: int
    hash_calls: int
    parse_calls: int
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class QualificationOutcome:
    """One bounded generated-fixture qualification outcome."""

    report: Mapping[str, Any]
    report_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_output_bytes: int


class GeneratedResponse(io.BytesIO):
    """Small response fixture with an HTTPResponse-like interface."""

    def __init__(
        self,
        body: bytes,
        *,
        url: str,
        headers: Mapping[str, str] | None = None,
        status: int = 200,
        redirected: bool = False,
        read_error: Exception | None = None,
    ) -> None:
        super().__init__(body)
        self.status = status
        self.headers = dict(headers or {})
        self.redirected = redirected
        self._url = url
        self._read_error = read_error

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status

    def read(self, size: int = -1) -> bytes:
        if self._read_error is not None:
            raise self._read_error
        return super().read(size)


class AuditedResponse:
    """One-use response wrapper enforcing read, hash, and parse ordering."""

    def __init__(self, response: BinaryIO):
        self.response = response
        self.read_calls = 0
        self.hash_calls = 0
        self.parse_calls = 0

    def read_once(self, limit: int) -> bytes:
        if self.read_calls != 0:
            raise TransportStableRefusal(REFUSAL_IDS[9], "response was already read")
        self.read_calls += 1
        try:
            body = self.response.read(limit)
        except Exception as exc:  # noqa: BLE001 - stable safe boundary
            raise TransportStableRefusal(REFUSAL_IDS[6], "response body read failed") from exc
        if not isinstance(body, bytes):
            raise TransportStableRefusal(REFUSAL_IDS[6], "response body is not bytes")
        return body

    def hash_once(self, body: bytes) -> str:
        if self.read_calls != 1 or self.hash_calls != 0 or self.parse_calls != 0:
            raise TransportStableRefusal(REFUSAL_IDS[9], "body hash order differs")
        self.hash_calls += 1
        return hashlib.sha256(body).hexdigest()

    def parse_once(self, parser: Callable[[bytes], Any], body: bytes) -> Any:
        if self.read_calls != 1 or self.hash_calls != 1 or self.parse_calls != 0:
            raise TransportStableRefusal(REFUSAL_IDS[9], "semantic parse order differs")
        self.parse_calls += 1
        try:
            return parser(body)
        except TransportStableRefusal:
            raise
        except Exception as exc:  # noqa: BLE001 - stable safe boundary
            raise TransportStableRefusal(REFUSAL_IDS[10], "semantic parse failed") from exc


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
    ).encode("utf-8")


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


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _load_json_object(payload: bytes) -> dict[str, Any]:
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_json_object,
        parse_constant=_reject_json_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact green registration without touching a dataset path."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _sha256_file(path) != CONTRACT_SHA256:
        raise TransportStableRefusal(REFUSAL_IDS[0], "contract hash differs")
    try:
        contract = _load_json_object(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise TransportStableRefusal(REFUSAL_IDS[0], "contract is malformed") from exc
    if (
        contract.get("contract_id")
        != "IACKD-T1-transport-stable-recovery-contract-v0"
        or contract.get("allowed_semantic_delta")
        != ["small_metadata_response_framing_policy"]
        or contract.get("authorization_state", {}).get("public_metadata_request") is not False
        or contract.get("authorization_state", {}).get("public_payload_request") is not False
    ):
        raise TransportStableRefusal(REFUSAL_IDS[0], "contract state differs")
    return contract


def response_spec_from_mapping(value: Mapping[str, Any]) -> ResponseSpec:
    """Construct a strict response spec while refusing unknown fields."""

    allowed = {"url", "expected_bytes", "expected_sha256", "expected_etag"}
    if set(value) != allowed:
        raise TransportStableRefusal(REFUSAL_IDS[1], "response spec fields differ")
    url = value["url"]
    expected_bytes = value["expected_bytes"]
    expected_sha256 = value["expected_sha256"]
    expected_etag = value["expected_etag"]
    if not isinstance(url, str) or not url.startswith("fixture://"):
        raise TransportStableRefusal(REFUSAL_IDS[13], "only generated fixture URLs are allowed")
    if not isinstance(expected_bytes, int) or isinstance(expected_bytes, bool) or expected_bytes <= 0:
        raise TransportStableRefusal(REFUSAL_IDS[1], "expected byte count is invalid")
    if expected_sha256 is not None and not _is_hex64(expected_sha256):
        raise TransportStableRefusal(REFUSAL_IDS[1], "expected SHA256 is invalid")
    if expected_etag is not None and (
        not isinstance(expected_etag, str) or not expected_etag
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "expected ETag is invalid")
    return ResponseSpec(url, expected_bytes, expected_sha256, expected_etag)


def _is_hex64(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _header(response: BinaryIO, name: str) -> str | None:
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    getter = getattr(headers, "get", None)
    if callable(getter):
        direct = getter(name)
        if direct is not None:
            return str(direct)
    if isinstance(headers, Mapping):
        matches = [value for key, value in headers.items() if str(key).casefold() == name.casefold()]
        if len(matches) > 1:
            return ", ".join(str(value) for value in matches)
        if matches:
            return str(matches[0])
    return None


def _status(response: BinaryIO) -> int | None:
    status = getattr(response, "status", None)
    if status is not None:
        return int(status)
    getter = getattr(response, "getcode", None)
    return int(getter()) if callable(getter) else None


def _final_url(response: BinaryIO) -> str | None:
    getter = getattr(response, "geturl", None)
    return str(getter()) if callable(getter) else None


def _parse_content_length(raw: str) -> int:
    if raw != raw.strip() or not raw or not raw.isascii() or any(
        character not in "0123456789" for character in raw
    ):
        raise TransportStableRefusal(REFUSAL_IDS[3], "Content-Length is malformed")
    return int(raw)


def _normalize_etag(raw: str) -> str:
    if raw != raw.strip() or not raw or raw.startswith("W/"):
        raise TransportStableRefusal(REFUSAL_IDS[8], "payload ETag is malformed")
    if raw.startswith('"') or raw.endswith('"'):
        if len(raw) < 2 or not (raw.startswith('"') and raw.endswith('"')):
            raise TransportStableRefusal(REFUSAL_IDS[8], "payload ETag quoting differs")
        raw = raw[1:-1]
    if not raw or '"' in raw:
        raise TransportStableRefusal(REFUSAL_IDS[8], "payload ETag is malformed")
    return raw


def _framing_profile(
    response: BinaryIO,
    *,
    mode: str,
    expected_bytes: int,
    read_limit: int,
) -> tuple[str, str]:
    content_length_raw = _header(response, "Content-Length")
    transfer_encoding_raw = _header(response, "Transfer-Encoding")
    if content_length_raw is not None and transfer_encoding_raw is not None:
        raise TransportStableRefusal(REFUSAL_IDS[3], "length and transfer coding are ambiguous")
    if transfer_encoding_raw is not None:
        if (
            transfer_encoding_raw != transfer_encoding_raw.strip()
            or transfer_encoding_raw.casefold() != "chunked"
        ):
            raise TransportStableRefusal(REFUSAL_IDS[3], "transfer coding is unsupported")
        if mode == "payload":
            raise TransportStableRefusal(REFUSAL_IDS[3], "payload transfer coding is forbidden")
        return "chunked", "unavailable"
    if content_length_raw is None:
        if mode == "payload":
            raise TransportStableRefusal(REFUSAL_IDS[5], "payload Content-Length is required")
        return "close_delimited", "unavailable"
    declared = _parse_content_length(content_length_raw)
    if declared > read_limit:
        raise TransportStableRefusal(REFUSAL_IDS[5], "declared length exceeds the read cap")
    if mode == "payload" and declared != expected_bytes:
        raise TransportStableRefusal(REFUSAL_IDS[5], "payload Content-Length differs")
    state = "exact" if declared == expected_bytes else "different"
    return "fixed_length", state


def validate_and_parse_response(
    audited: AuditedResponse,
    *,
    spec: ResponseSpec,
    mode: str,
    parser: Callable[[bytes], Any],
) -> tuple[ResponseValidation, Any]:
    """Validate one response and parse it only after body identity passes."""

    if mode not in {"metadata", "payload"}:
        raise TransportStableRefusal(REFUSAL_IDS[1], "response mode is unknown")
    if audited.read_calls or audited.hash_calls or audited.parse_calls:
        raise TransportStableRefusal(REFUSAL_IDS[9], "response wrapper is not fresh")
    if (
        not isinstance(spec.url, str)
        or not spec.url.startswith("fixture://")
        or not isinstance(spec.expected_bytes, int)
        or isinstance(spec.expected_bytes, bool)
        or spec.expected_bytes <= 0
        or (spec.expected_sha256 is not None and not _is_hex64(spec.expected_sha256))
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "response spec is malformed")

    response = audited.response
    if (
        _status(response) != 200
        or _final_url(response) != spec.url
        or bool(getattr(response, "redirected", False))
    ):
        raise TransportStableRefusal(REFUSAL_IDS[2], "status final URL or redirect differs")

    content_encoding = _header(response, "Content-Encoding")
    if content_encoding not in {None, ""} and (
        content_encoding != content_encoding.strip()
        or content_encoding.casefold() != "identity"
    ):
        raise TransportStableRefusal(REFUSAL_IDS[4], "content encoding is not identity")

    read_limit = spec.expected_bytes + 1
    framing_profile, content_length_state = _framing_profile(
        response,
        mode=mode,
        expected_bytes=spec.expected_bytes,
        read_limit=read_limit,
    )
    body = audited.read_once(read_limit)
    if len(body) != spec.expected_bytes:
        raise TransportStableRefusal(REFUSAL_IDS[6], "observed body byte count differs")
    body_sha256 = audited.hash_once(body)
    if spec.expected_sha256 is not None and body_sha256 != spec.expected_sha256:
        raise TransportStableRefusal(REFUSAL_IDS[7], "body SHA256 differs")

    etag_state = "not_applicable"
    if mode == "payload":
        if spec.expected_etag is None:
            raise TransportStableRefusal(REFUSAL_IDS[1], "payload expected ETag is missing")
        observed_etag = _header(response, "ETag")
        if observed_etag is None or _normalize_etag(observed_etag) != spec.expected_etag:
            raise TransportStableRefusal(REFUSAL_IDS[8], "payload ETag differs")
        etag_state = "exact"

    parsed = audited.parse_once(parser, body)
    warnings: list[str] = []
    if mode == "metadata" and content_length_state == "different":
        warnings.append("metadata_Content_Length_differs_content_identity_passed")
    if mode == "metadata" and content_length_state == "unavailable":
        warnings.append("metadata_Content_Length_unavailable_content_identity_passed")
    return (
        ResponseValidation(
            mode=mode,
            framing_profile=framing_profile,
            content_length_state=content_length_state,
            observed_bytes=len(body),
            body_sha256=body_sha256,
            etag_state=etag_state,
            read_calls=audited.read_calls,
            hash_calls=audited.hash_calls,
            parse_calls=audited.parse_calls,
            warnings=tuple(warnings),
        ),
        parsed,
    )


def assert_generated_source(source_kind: str) -> None:
    """Refuse any source category other than generated in this module."""

    if source_kind != "generated":
        raise TransportStableRefusal(REFUSAL_IDS[13], "only generated sources are allowed")


def _fixture_body(case: str) -> bytes:
    if case.casefold() in FORBIDDEN_GENERATED_TERMS:
        raise TransportStableRefusal(REFUSAL_IDS[13], "fixture case contains a forbidden term")
    return _canonical_json_bytes(
        {
            "case": case,
            "fixture": "iackd-t1-generated-transport",
            "revision": 1,
        }
    )


def _fixture_parser(body: bytes) -> dict[str, Any]:
    value = _load_json_object(body)
    if set(value) != {"case", "fixture", "revision"}:
        raise ValueError("fixture semantic fields differ")
    if value["fixture"] != "iackd-t1-generated-transport" or value["revision"] != 1:
        raise ValueError("fixture semantic identity differs")
    text = json.dumps(value, sort_keys=True).casefold()
    if any(term in text for term in FORBIDDEN_GENERATED_TERMS):
        raise TransportStableRefusal(REFUSAL_IDS[13], "fixture contains forbidden content")
    return value


def _acceptance_case(case: str) -> tuple[ResponseValidation, dict[str, Any]]:
    body = _fixture_body(case)
    url = f"fixture://iackd-t1/{case}"
    headers: dict[str, str] = {}
    mode = "metadata"
    expected_etag: str | None = None
    if case == "fixed_length_exact":
        headers["Content-Length"] = str(len(body))
    elif case == "fixed_length_valid_different":
        headers["Content-Length"] = str(len(body) + 1)
    elif case == "chunked":
        headers["Transfer-Encoding"] = "chunked"
    elif case == "close_delimited":
        pass
    elif case == "payload_fixed_length_exact":
        mode = "payload"
        expected_etag = "fixture-etag-001"
        headers["Content-Length"] = str(len(body))
        headers["ETag"] = f'"{expected_etag}"'
    else:
        raise ValueError("unknown generated acceptance case")
    spec = ResponseSpec(
        url=url,
        expected_bytes=len(body),
        expected_sha256=_sha256_bytes(body),
        expected_etag=expected_etag,
    )
    validation, parsed = validate_and_parse_response(
        AuditedResponse(GeneratedResponse(body, url=url, headers=headers)),
        spec=spec,
        mode=mode,
        parser=_fixture_parser,
    )
    return validation, parsed


def run_acceptance_matrix() -> dict[str, Any]:
    """Run all generated acceptance cases once and return stable summaries."""

    assert_generated_source("generated")
    cases = (
        "fixed_length_exact",
        "fixed_length_valid_different",
        "chunked",
        "close_delimited",
        "payload_fixed_length_exact",
    )
    rows = []
    for case in cases:
        validation, parsed = _acceptance_case(case)
        rows.append(
            {
                "case": case,
                "mode": validation.mode,
                "framing_profile": validation.framing_profile,
                "content_length_state": validation.content_length_state,
                "observed_bytes": validation.observed_bytes,
                "body_sha256": validation.body_sha256,
                "etag_state": validation.etag_state,
                "read_calls": validation.read_calls,
                "hash_calls": validation.hash_calls,
                "parse_calls": validation.parse_calls,
                "warnings": list(validation.warnings),
                "parsed_fixture": parsed["fixture"],
            }
        )
    return {"cases": rows, "canonical_sha256": _sha256_bytes(_canonical_json_bytes(rows))}


def _base_fixture() -> tuple[bytes, str, ResponseSpec]:
    body = _fixture_body("mutation-base")
    url = "fixture://iackd-t1/mutation-base"
    return body, url, ResponseSpec(url, len(body), _sha256_bytes(body))


def _expect_refusal(name: str, expected_id: str, operation: Callable[[], Any]) -> dict[str, str]:
    try:
        operation()
    except TransportStableRefusal as exc:
        if exc.refusal_id != expected_id:
            raise AssertionError(
                f"{name} produced {exc.refusal_id}, expected {expected_id}"
            ) from exc
        return {"mutation": name, "refusal_id": exc.refusal_id}
    raise AssertionError(f"{name} did not refuse")


def run_refusal_matrix() -> list[dict[str, str]]:
    """Exercise the 22 frozen aggregate-safe refusal mutations."""

    body, url, spec = _base_fixture()

    def validate(
        *,
        candidate_body: bytes = body,
        headers: Mapping[str, str] | None = None,
        status: int = 200,
        final_url: str = url,
        redirected: bool = False,
        read_error: Exception | None = None,
        candidate_spec: ResponseSpec = spec,
        mode: str = "metadata",
        prepare: Callable[[AuditedResponse], None] | None = None,
    ) -> Any:
        audited = AuditedResponse(
            GeneratedResponse(
                candidate_body,
                url=final_url,
                headers=headers,
                status=status,
                redirected=redirected,
                read_error=read_error,
            )
        )
        if prepare is not None:
            prepare(audited)
        return validate_and_parse_response(
            audited,
            spec=candidate_spec,
            mode=mode,
            parser=_fixture_parser,
        )

    over_cap = str(len(body) + 2)
    wrong_hash = "0" * 64 if spec.expected_sha256 != "0" * 64 else "1" * 64
    payload_spec = ResponseSpec(url, len(body), _sha256_bytes(body), "fixture-etag-001")

    def mark_read(audited: AuditedResponse) -> None:
        audited.read_calls = 1

    def mark_hash(audited: AuditedResponse) -> None:
        audited.hash_calls = 1

    def mark_parse(audited: AuditedResponse) -> None:
        audited.parse_calls = 1

    cases: tuple[tuple[str, str, Callable[[], Any]], ...] = (
        ("non_200_status", REFUSAL_IDS[2], lambda: validate(status=206)),
        ("changed_final_URL", REFUSAL_IDS[2], lambda: validate(final_url=f"{url}-other")),
        ("redirect", REFUSAL_IDS[2], lambda: validate(redirected=True)),
        ("malformed_Content_Length", REFUSAL_IDS[3], lambda: validate(headers={"Content-Length": "abc"})),
        ("negative_Content_Length", REFUSAL_IDS[3], lambda: validate(headers={"Content-Length": "-1"})),
        ("comma_joined_Content_Length", REFUSAL_IDS[3], lambda: validate(headers={"Content-Length": "4, 4"})),
        ("over_cap_Content_Length", REFUSAL_IDS[5], lambda: validate(headers={"Content-Length": over_cap})),
        (
            "Content_Length_plus_Transfer_Encoding",
            REFUSAL_IDS[3],
            lambda: validate(headers={"Content-Length": str(len(body)), "Transfer-Encoding": "chunked"}),
        ),
        ("unsupported_Transfer_Encoding", REFUSAL_IDS[3], lambda: validate(headers={"Transfer-Encoding": "gzip"})),
        ("compressed_Content_Encoding", REFUSAL_IDS[4], lambda: validate(headers={"Content-Encoding": "gzip"})),
        ("body_underflow", REFUSAL_IDS[6], lambda: validate(candidate_body=body[:-1])),
        ("body_overflow", REFUSAL_IDS[6], lambda: validate(candidate_body=body + b"x")),
        ("body_read_error", REFUSAL_IDS[6], lambda: validate(read_error=OSError("generated"))),
        (
            "body_SHA256_drift",
            REFUSAL_IDS[7],
            lambda: validate(candidate_spec=ResponseSpec(url, len(body), wrong_hash)),
        ),
        ("second_read", REFUSAL_IDS[9], lambda: validate(prepare=mark_read)),
        ("second_hash", REFUSAL_IDS[9], lambda: validate(prepare=mark_hash)),
        ("parse_before_identity", REFUSAL_IDS[9], lambda: validate(prepare=mark_parse)),
        (
            "payload_missing_or_different_Content_Length",
            REFUSAL_IDS[5],
            lambda: validate(candidate_spec=payload_spec, mode="payload", headers={"ETag": '"fixture-etag-001"'}),
        ),
        (
            "payload_missing_or_different_ETag",
            REFUSAL_IDS[8],
            lambda: validate(candidate_spec=payload_spec, mode="payload", headers={"Content-Length": str(len(body))}),
        ),
        ("unknown_mode_or_field", REFUSAL_IDS[1], lambda: validate(mode="unknown")),
        ("network_or_real_path_attempt", REFUSAL_IDS[13], lambda: assert_generated_source("public_url")),
        (
            "output_overwrite_or_cap",
            REFUSAL_IDS[11],
            lambda: _write_exclusive(Path(tempfile.gettempdir()) / "unused-iackdt.json", b"xx", 1),
        ),
    )
    return [_expect_refusal(name, refusal_id, operation) for name, refusal_id, operation in cases]


def _thread_environment() -> dict[str, str]:
    environ = dict(os.environ)
    for key in THREAD_ENV_KEYS:
        environ[key] = "1"
    return environ


def _validate_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise TransportStableRefusal(REFUSAL_IDS[12], "thread environment is not one")


def _write_exclusive(path: Path, payload: bytes, maximum_bytes: int) -> int:
    if maximum_bytes <= 0 or maximum_bytes > MAX_REPORT_BYTES or len(payload) > maximum_bytes:
        raise TransportStableRefusal(REFUSAL_IDS[11], "output exceeds the frozen cap")
    if path.exists() or path.is_symlink():
        raise TransportStableRefusal(REFUSAL_IDS[11], "output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise TransportStableRefusal(REFUSAL_IDS[11], "output creation failed") from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return len(payload)


def _report_bytes(report: dict[str, Any]) -> bytes:
    measurements = report["measurements"]
    prior = -1
    for _ in range(8):
        payload = _canonical_json_bytes(report)
        current = len(payload)
        measurements["generated_output_bytes"] = current
        if current == prior:
            return payload
        prior = current
    raise TransportStableRefusal(REFUSAL_IDS[11], "output size did not stabilize")


def _zero_access_counters() -> dict[str, int]:
    return {
        "ds006840_metadata_requests": 0,
        "ds006840_payload_requests": 0,
        "network_bytes": 0,
        "real_or_public_body_reads": 0,
        "local_IACKD_path_operations": 0,
        "old_invocation_root_operations": 0,
        "old_retained_bundle_operations": 0,
        "signal_sample_reads": 0,
        "event_or_trajectory_reads": 0,
        "target_or_label_reads": 0,
        "parameter_update_fits": 0,
        "model_inference_calls": 0,
        "prediction_sets": 0,
        "prediction_freezes": 0,
        "target_deliveries": 0,
        "scores": 0,
        "scientific_claim_upgrades": 0,
    }


def run_synthetic_qualification(
    output_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    maximum_output_bytes: int = MAX_REPORT_BYTES,
) -> QualificationOutcome:
    """Run one bounded final qualification over generated responses only."""

    contract = load_registered_contract(repo_root)
    _validate_thread_environment(os.environ if environ is None else environ)
    assert_generated_source("generated")
    started = clock()
    first = run_acceptance_matrix()
    second = run_acceptance_matrix()
    if first != second:
        raise TransportStableRefusal(REFUSAL_IDS[14], "acceptance replay differs")
    refusals = run_refusal_matrix()
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    caps = contract["resource_caps"]["generated_qualification"]
    if runtime_seconds < 0 or runtime_seconds > min(
        float(caps["wall_time_seconds"]), MAX_RUNTIME_SECONDS
    ):
        raise TransportStableRefusal(REFUSAL_IDS[12], "runtime cap failed")
    if peak_rss_bytes <= 0 or peak_rss_bytes > min(
        int(caps["peak_RSS_bytes"]), MAX_PEAK_RSS_BYTES
    ):
        raise TransportStableRefusal(REFUSAL_IDS[12], "RSS cap failed")
    if maximum_output_bytes > int(caps["generated_output_bytes"]):
        raise TransportStableRefusal(REFUSAL_IDS[11], "output cap exceeds contract")

    cases = first["cases"]
    input_bytes = 2 * sum(int(row["observed_bytes"]) for row in cases)
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "generated_fixture_qualification_passed_zero_network",
        "proof_posture": "generated_responses_and_mocked_streams_only_no_scientific_value",
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "push_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "fixture_qualification": {
            "accepted_case_count_per_replay": len(cases),
            "accepted_case_count_total": 2 * len(cases),
            "metadata_framing_profiles": [
                "fixed_length",
                "chunked",
                "close_delimited",
            ],
            "valid_different_metadata_Content_Length_accepted_with_exact_content": True,
            "payload_exact_length_and_ETag_accepted": True,
            "deterministic_replays": 2,
            "deterministic_acceptance_sha256": first["canonical_sha256"],
            "refusal_mutation_count": len(refusals),
            "distinct_refusal_ids": len({row["refusal_id"] for row in refusals}),
            "refusal_mutations": refusals,
            "read_calls": 2 * sum(int(row["read_calls"]) for row in cases),
            "body_SHA256_passes": 2 * sum(int(row["hash_calls"]) for row in cases),
            "semantic_parse_passes": 2 * sum(int(row["parse_calls"]) for row in cases),
            "all_gates_passed": True,
        },
        "measurements": {
            "generated_input_bytes": input_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "generated_output_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "access_counters": _zero_access_counters(),
        "acceptance_gates": [
            {"gate": "green_registration_hash", "passed": True},
            {"gate": "three_metadata_framing_profiles", "passed": True},
            {"gate": "exact_observed_bytes", "passed": True},
            {"gate": "exact_registered_SHA256", "passed": True},
            {"gate": "one_read_hash_parse_order", "passed": True},
            {"gate": "valid_different_length_is_advisory", "passed": True},
            {"gate": "payload_length_and_ETag_remain_strict", "passed": True},
            {"gate": "twenty_two_refusal_mutations", "passed": True},
            {"gate": "deterministic_replay", "passed": True},
            {"gate": "aggregate_only_output", "passed": True},
            {"gate": "zero_network_and_real_paths", "passed": True},
            {"gate": "zero_models_targets_and_scores", "passed": True},
            {"gate": "runtime_RSS_and_output_caps", "passed": True},
        ],
        "warnings": [
            "Generated response bodies are interface fixtures and contain no scientific evidence.",
            "Content-Length remains mandatory and exact for the future large-object mode.",
            "No public URL opener or real-path executor exists in this module.",
        ],
        "unavailable_fields": [
            "real_HTTP_framing_profile",
            "real_response_headers",
            "real_body_identity",
            "real_signal_or_target_identity",
            "producer_causality_for_real_derivative",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": "A dependency-free validator now separates HTTP framing from exact body identity and retains strict payload length and ETag checks.",
            "scientific_claim_not_established": "Generated responses establish no neural effect action decoding brain-specific origin language or thought decoding real-time operation hardware capability assistive benefit home use or clinical use.",
        },
    }
    validate_qualification_report(report)
    payload = _report_bytes(report)
    if len(payload) > maximum_output_bytes:
        raise TransportStableRefusal(REFUSAL_IDS[11], "qualification report exceeds cap")
    _write_exclusive(Path(output_path), payload, maximum_output_bytes)
    loaded = load_qualification_report(output_path, maximum_bytes=maximum_output_bytes)
    if loaded != report:
        raise TransportStableRefusal(REFUSAL_IDS[14], "written qualification replay differs")
    return QualificationOutcome(
        report=report,
        report_path=Path(output_path),
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_output_bytes=len(payload),
    )


def validate_qualification_report(report: Mapping[str, Any]) -> None:
    """Validate the aggregate report without opening any source artifact."""

    if set(report) != REPORT_FIELDS:
        raise TransportStableRefusal(REFUSAL_IDS[1], "qualification report fields differ")
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("status") != "generated_fixture_qualification_passed_zero_network"
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "qualification report identity differs")
    green = report["green_registration"]
    if (
        green.get("commit") != GREEN_REGISTRATION_COMMIT
        or green.get("push_CI_run_id") != GREEN_REGISTRATION_CI_RUN_ID
        or green.get("contract_sha256") != CONTRACT_SHA256
        or green.get("both_required_jobs_green") is not True
    ):
        raise TransportStableRefusal(REFUSAL_IDS[0], "green registration proof differs")
    fixture = report["fixture_qualification"]
    fixture_fields = {
        "accepted_case_count_per_replay",
        "accepted_case_count_total",
        "metadata_framing_profiles",
        "valid_different_metadata_Content_Length_accepted_with_exact_content",
        "payload_exact_length_and_ETag_accepted",
        "deterministic_replays",
        "deterministic_acceptance_sha256",
        "refusal_mutation_count",
        "distinct_refusal_ids",
        "refusal_mutations",
        "read_calls",
        "body_SHA256_passes",
        "semantic_parse_passes",
        "all_gates_passed",
    }
    refusal_rows = fixture.get("refusal_mutations")
    if (
        set(fixture) != fixture_fields
        or fixture.get("accepted_case_count_per_replay") != 5
        or fixture.get("accepted_case_count_total") != 10
        or fixture.get("metadata_framing_profiles")
        != ["fixed_length", "chunked", "close_delimited"]
        or fixture.get(
            "valid_different_metadata_Content_Length_accepted_with_exact_content"
        )
        is not True
        or fixture.get("payload_exact_length_and_ETag_accepted") is not True
        or fixture.get("deterministic_replays") != 2
        or fixture.get("refusal_mutation_count") != 22
        or fixture.get("read_calls") != 10
        or fixture.get("body_SHA256_passes") != 10
        or fixture.get("semantic_parse_passes") != 10
        or fixture.get("all_gates_passed") is not True
        or not _is_hex64(fixture.get("deterministic_acceptance_sha256"))
        or not isinstance(refusal_rows, list)
        or len(refusal_rows) != len(REQUIRED_REFUSAL_MUTATIONS)
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "fixture qualification differs")
    if any(
        not isinstance(row, Mapping)
        or set(row) != {"mutation", "refusal_id"}
        or row.get("refusal_id") not in REFUSAL_IDS
        for row in refusal_rows
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "refusal row is malformed")
    if [row["mutation"] for row in refusal_rows] != list(REQUIRED_REFUSAL_MUTATIONS):
        raise TransportStableRefusal(REFUSAL_IDS[1], "refusal mutation order differs")
    if fixture.get("distinct_refusal_ids") != len(
        {row["refusal_id"] for row in refusal_rows}
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "refusal count differs")

    counters = report["access_counters"]
    expected_counters = _zero_access_counters()
    if set(counters) != set(expected_counters) or not all(
        isinstance(value, int) and not isinstance(value, bool) and value == 0
        for value in counters.values()
    ):
        raise TransportStableRefusal(REFUSAL_IDS[13], "forbidden access counter is nonzero")

    measurements = report["measurements"]
    measurement_fields = {
        "generated_input_bytes",
        "runtime_seconds",
        "peak_RSS_bytes",
        "generated_output_bytes",
        "CPU_threads",
        "workers",
        "numerical_jobs",
        "producer_is_causal",
        "end_to_end_latency_measured",
    }
    runtime = measurements.get("runtime_seconds")
    peak_rss = measurements.get("peak_RSS_bytes")
    output_bytes = measurements.get("generated_output_bytes")
    if (
        set(measurements) != measurement_fields
        or measurements.get("generated_input_bytes") != 848
        or not isinstance(runtime, (int, float))
        or isinstance(runtime, bool)
        or runtime < 0
        or runtime > MAX_RUNTIME_SECONDS
        or not isinstance(peak_rss, int)
        or isinstance(peak_rss, bool)
        or peak_rss <= 0
        or peak_rss > MAX_PEAK_RSS_BYTES
        or not isinstance(output_bytes, int)
        or isinstance(output_bytes, bool)
        or output_bytes < 0
        or output_bytes > MAX_REPORT_BYTES
        or (
            measurements.get("CPU_threads"),
            measurements.get("workers"),
            measurements.get("numerical_jobs"),
        )
        != (1, 1, 1)
        or measurements.get("producer_is_causal") is not None
        or measurements.get("end_to_end_latency_measured") is not False
    ):
        raise TransportStableRefusal(REFUSAL_IDS[12], "report resource values differ")

    if not report["acceptance_gates"] or not all(
        isinstance(row, Mapping)
        and set(row) == {"gate", "passed"}
        and isinstance(row.get("gate"), str)
        and row.get("passed") is True
        for row in report["acceptance_gates"]
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "acceptance gate failed")
    if (
        not isinstance(report["warnings"], list)
        or not report["warnings"]
        or not all(isinstance(value, str) and value for value in report["warnings"])
        or not isinstance(report["unavailable_fields"], list)
        or not all(
            isinstance(value, str) and value for value in report["unavailable_fields"]
        )
        or set(report["claim_boundary"])
        != {"engineering_capability_added", "scientific_claim_not_established"}
    ):
        raise TransportStableRefusal(REFUSAL_IDS[1], "aggregate report boundary differs")
    serialized = json.dumps(report, sort_keys=True).casefold()
    if any(f'"{term}"' in serialized for term in FORBIDDEN_GENERATED_TERMS):
        raise TransportStableRefusal(REFUSAL_IDS[13], "report contains forbidden field")


def load_qualification_report(
    path: str | Path,
    *,
    maximum_bytes: int = MAX_REPORT_BYTES,
) -> dict[str, Any]:
    """Load one bounded regular-file report without source access."""

    candidate = Path(path)
    try:
        info = candidate.lstat()
    except OSError as exc:
        raise TransportStableRefusal(REFUSAL_IDS[11], "report is unavailable") from exc
    if not stat.S_ISREG(info.st_mode) or candidate.is_symlink():
        raise TransportStableRefusal(REFUSAL_IDS[11], "report must be a regular file")
    if info.st_size <= 0 or info.st_size > maximum_bytes or maximum_bytes > MAX_REPORT_BYTES:
        raise TransportStableRefusal(REFUSAL_IDS[11], "report size exceeds cap")
    try:
        report = _load_json_object(candidate.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise TransportStableRefusal(REFUSAL_IDS[1], "report is malformed") from exc
    validate_qualification_report(report)
    return report


def summarize_qualification(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact aggregate-only inspection surface."""

    validate_qualification_report(report)
    fixture = report["fixture_qualification"]
    measurements = report["measurements"]
    return {
        "status": report["status"],
        "metadata_framing_profiles": fixture["metadata_framing_profiles"],
        "accepted_case_count_total": fixture["accepted_case_count_total"],
        "refusal_mutation_count": fixture["refusal_mutation_count"],
        "deterministic_replays": fixture["deterministic_replays"],
        "generated_input_bytes": measurements["generated_input_bytes"],
        "generated_output_bytes": measurements["generated_output_bytes"],
        "runtime_seconds": measurements["runtime_seconds"],
        "peak_RSS_bytes": measurements["peak_RSS_bytes"],
        "producer_is_causal": measurements["producer_is_causal"],
        "end_to_end_latency_measured": measurements["end_to_end_latency_measured"],
        "warnings": report["warnings"],
        "unavailable_fields": report["unavailable_fields"],
        "claim_boundary": report["claim_boundary"],
    }


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the frozen zero-network plan."""

    contract = load_registered_contract(repo_root)
    return {
        "schema_name": "neurodecodekit.iackd_transport_stable_plan",
        "schema_version": SCHEMA_VERSION,
        "status": "generated_fixture_implementation_only",
        "lane": "IACKD-T1",
        "accepted_metadata_framing_profiles": contract["metadata_contract"][
            "accepted_framing_profiles"
        ],
        "metadata_documents": contract["metadata_contract"]["request_count"],
        "metadata_registered_body_bytes": contract["metadata_contract"][
            "registered_body_bytes"
        ],
        "payload_objects_future_only": contract["payload_contract"]["object_count"],
        "network_requests_made": 0,
        "network_bytes_read": 0,
        "local_IACKD_path_operations": 0,
        "real_executor_available": False,
        "public_execution_authorized": False,
        "next_gate": "green_exact_generated_implementation_then_all_false_Tier_C_request",
        "claim_ceiling": "transport_interface_mechanics_only",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.iackd_transport_stable",
        description=(
            "Plan, generated-fixture qualify, or inspect the zero-network IACKD-T1 "
            "transport validator. No public URL or real-path executor exists here."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true", help="Run generated responses only.")
    mode.add_argument("--inspect", metavar="REPORT", help="Inspect one bounded report.")
    parser.add_argument("--out", help="New JSON output path for --fixture.")
    parser.add_argument("--max-input-mib", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.inspect:
            maximum_bytes = int(args.max_input_mib * 1024 * 1024)
            report = load_qualification_report(args.inspect, maximum_bytes=maximum_bytes)
            print(json.dumps(summarize_qualification(report), indent=2, sort_keys=True))
            return 0
        if args.fixture:
            if not args.out:
                raise ValueError("--fixture requires --out")
            outcome = run_synthetic_qualification(
                args.out,
                environ=_thread_environment(),
            )
            print(json.dumps(summarize_qualification(outcome.report), indent=2, sort_keys=True))
            return 0
        if args.out:
            raise ValueError("--out requires --fixture")
        print(json.dumps(registered_plan(), indent=2, sort_keys=True))
        print("Safety default: zero network requests and zero local IACKD path operations.")
        return 0
    except Exception as exc:  # noqa: BLE001 - friendly CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
