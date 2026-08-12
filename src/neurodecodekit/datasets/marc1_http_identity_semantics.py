"""Generated-only qualification for MARC1 HTTP identity semantics."""

from __future__ import annotations

import argparse
import ast
import hashlib
import ipaddress
import json
import math
import os
import resource
import stat
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlsplit

from neurodecodekit.datasets import marc1_pilot_selection as selector


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC1-HT1"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc1_http_identity_semantics_recovery_contract.v0.json"
)
CONTRACT_SHA256 = "a8b86c56b2ea540715dc09a4a34e0de93f969e3e30dd0ea2d055d366d0c5e73d"
POLICY_SHA256 = "ac1b98eed57af7e545b925f1529ebf38de72b4277ea54a473ae1d6f7fe0cd3a6"
GREEN_CONTRACT_COMMIT = "1f99d0a8c5609dae992fa0e245f179c2f417038f"
GREEN_CONTRACT_CI_RUN_ID = 31581395690
GREEN_CONTRACT_BASE_JOB_ID = 94065047494
GREEN_CONTRACT_OPTIONAL_JOB_ID = 94065047277

MOCK_ENDPOINT = "https://generated.invalid/marc1-ht1/files"
MAX_BODY_BYTES = 2 * 1024 * 1024
MAX_PUBLIC_OUTPUT_BYTES = 1024 * 1024
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024 * 1024
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_GENERATED_INPUT_BYTES = 2 * 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)

REPORT_NAME = "marc1_http_identity_semantics_qualification.v0.json"
PRIVATE_NAME = "marc1_http_identity_semantics.generated.private.v0.json"
ACCEPTED_CASES = (
    "Content_Encoding_absent",
    "Content_Encoding_identity_lowercase",
    "Content_Encoding_IDENTITY_uppercase",
    "Content_Encoding_IdEnTiTy_mixed_case",
)
REFUSAL_CASES = (
    "Content_Encoding_present_empty",
    "Content_Encoding_whitespace_only",
    "Content_Encoding_gzip",
    "Content_Encoding_br",
    "Content_Encoding_deflate",
    "Content_Encoding_compress",
    "Content_Encoding_unknown_token",
    "Content_Encoding_identity_plus_gzip",
    "Content_Encoding_parameterized_identity",
    "duplicate_Content_Encoding",
    "Transfer_Encoding_present",
    "non_JSON_Content_Type",
    "malformed_Content_Length",
    "body_overflow",
    "automatic_redirect",
    "private_or_nonglobal_redirect",
    "alternate_endpoint",
    "target_like_public_field",
    "output_cap",
    "second_invocation",
)
FAILURE_ROUTES = {
    "MARC1HT-F01": "proof_or_contract_identity",
    "MARC1HT-F02": "content_encoding_semantics",
    "MARC1HT-F03": "unchanged_HTTP_envelope_or_source_schema",
    "MARC1HT-F04": "resource_output_privacy_or_replay_boundary",
    "MARC1HT-F05": "forbidden_operation_or_second_invocation",
}
ACCEPTANCE_GATES = (
    "green_research_proof_identity",
    "exact_contract_identity",
    "exact_candidate_policy_hash",
    "all_four_accepted_forms_pass",
    "accepted_forms_have_identical_body_and_selection_hashes",
    "all_twenty_mutations_refuse_under_registered_routes",
    "row_order_replay_exact",
    "exact_12_plus_12_participant_identities",
    "exact_72_bundle_288_member_12_archive_selection",
    "exact_split_binding_and_zero_overlap",
    "target_quality_size_CRC_and_outcome_free_selection",
    "private_public_output_separation",
    "source_has_no_network_decoder_real_executor_or_neural_interface",
    "all_real_payload_neural_target_model_score_and_claim_counters_zero",
    "resource_and_output_caps",
    "deterministic_aggregate_and_private_output_hashes",
)
PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "proof_posture",
        "green_contract_proof",
        "accepted_response_summary",
        "refusal_summary",
        "cohort_summary",
        "split_summary",
        "byte_summary",
        "selection_hashes",
        "source_surface",
        "replay_summary",
        "access_counters",
        "measurements",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
EXPECTED_FREEWILL_SUBJECTS = (
    "sub-08",
    "sub-10",
    "sub-07",
    "sub-22",
    "sub-19",
    "sub-16",
    "sub-14",
    "sub-04",
    "sub-05",
    "sub-03",
    "sub-09",
    "sub-11",
)
EXPECTED_WRIST_SUBJECTS = (
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
TARGET_LIKE_KEYS = {
    "answer",
    "event",
    "ground_truth",
    "intended_text",
    "label",
    "outcome",
    "quality",
    "reference_text",
    "response",
    "sentence",
    "target",
    "trial_label",
}


class HTTPIdentityRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-HT1 route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC1-HT1 failure route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class MockResponse:
    """In-memory response fixture with no network behavior."""

    status: int
    reported_url: str
    headers: tuple[tuple[str, str], ...]
    body: bytes


@dataclass(frozen=True)
class QualificationOutcome:
    """One generated qualification outcome."""

    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


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
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise HTTPIdentityRefusal("MARC1HT-F01", "bound artifact is unavailable") from exc
    if not stat.S_ISREG(observed.st_mode):
        raise HTTPIdentityRefusal("MARC1HT-F01", "bound artifact is not a regular file")
    digest = hashlib.sha256()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != observed.st_dev
                or opened.st_ino != observed.st_ino
                or opened.st_size != observed.st_size
            ):
                raise HTTPIdentityRefusal("MARC1HT-F01", "bound artifact changed during open")
            while chunk := os.read(descriptor, 64 * 1024):
                digest.update(chunk)
        finally:
            os.close(descriptor)
    except HTTPIdentityRefusal:
        raise
    except OSError as exc:
        raise HTTPIdentityRefusal("MARC1HT-F01", "bound artifact read failed") from exc
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _canonical_policy_hash(policy: Mapping[str, Any]) -> str:
    return _sha256_bytes(
        json.dumps(
            policy,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    )


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact generated-only contract after its remote-green proof."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _sha256_file(path) != CONTRACT_SHA256:
        raise HTTPIdentityRefusal("MARC1HT-F01", "contract hash differs")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPIdentityRefusal("MARC1HT-F01", "contract is unavailable") from exc
    _verify_contract(contract, root)
    return contract


def _verify_contract(contract: Mapping[str, Any], root: Path) -> None:
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc1_http_identity_semantics_recovery_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("contract_id")
        != "MARC1-HT1-generated-http-identity-semantics-v0"
        or contract.get("status")
        != "frozen_generated_mock_contract_real_inputs_and_execution_unauthorized"
        or contract.get("acceptance_route") != "MARC1HT-G1"
    ):
        raise HTTPIdentityRefusal("MARC1HT-F01", "contract identity differs")
    proof = contract.get("green_research_anchor")
    if (
        not isinstance(proof, dict)
        or proof.get("both_required_jobs_green") is not True
        or proof.get("commit") != "f515b36cfdd2b297bcbba9885af92e59ead066a7"
        or proof.get("CI_run_id") != 31580575669
        or proof.get("base_python_job_id") != 94062432262
        or proof.get("optional_neuro_job_id") != 94062432241
    ):
        raise HTTPIdentityRefusal("MARC1HT-F01", "research proof differs")
    if (
        tuple(contract.get("accepted_response_cases", ())) != ACCEPTED_CASES
        or tuple(contract.get("refusal_cases", ())) != REFUSAL_CASES
        or tuple(contract.get("acceptance_gates", ())) != ACCEPTANCE_GATES
        or contract.get("failure_routes") != FAILURE_ROUTES
    ):
        raise HTTPIdentityRefusal("MARC1HT-F01", "contract matrix differs")
    if _canonical_policy_hash(contract.get("candidate_transport_policy", {})) != POLICY_SHA256:
        raise HTTPIdentityRefusal("MARC1HT-F01", "policy hash differs")
    bindings = (
        proof.get("research_document"),
        proof.get("research_registry"),
        contract.get("frozen_source_bindings", {}).get("consumed_live_result"),
        contract.get("frozen_source_bindings", {}).get("generated_selector"),
    )
    for binding in bindings:
        if (
            not isinstance(binding, dict)
            or "path" not in binding
            or not isinstance(binding.get("path"), str)
        ):
            raise HTTPIdentityRefusal("MARC1HT-F01", "artifact binding differs")
        expected = binding.get("SHA256", binding.get("sha256"))
        if not isinstance(expected, str) or _sha256_file(root / binding["path"]) != expected:
            raise HTTPIdentityRefusal("MARC1HT-F01", "artifact hash differs")
    if any(contract.get("authorization_flags", {}).values()) or any(
        contract.get("current_access_counters", {}).values()
    ):
        raise HTTPIdentityRefusal("MARC1HT-F01", "contract is not zero-access")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise HTTPIdentityRefusal("MARC1HT-F03", "duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise HTTPIdentityRefusal("MARC1HT-F03", "non-finite JSON value")


def _parse_rows(payload: bytes) -> list[dict[str, Any]]:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise HTTPIdentityRefusal("MARC1HT-F03", "JSON encoding differs")
    try:
        text = payload.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except HTTPIdentityRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise HTTPIdentityRefusal("MARC1HT-F03", "JSON body differs") from exc
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise HTTPIdentityRefusal("MARC1HT-F03", "metadata row root differs")
    _reject_target_like_fields(value)
    return value


def _normalize_key(value: str) -> str:
    return "_".join(value.lower().replace("-", "_").split())


def _reject_target_like_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if _normalize_key(str(key)) in TARGET_LIKE_KEYS:
                raise HTTPIdentityRefusal("MARC1HT-F03", "target-like field is forbidden")
            _reject_target_like_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_target_like_fields(child)


def _critical_headers(
    headers: Sequence[tuple[str, str]],
) -> dict[str, str]:
    critical = {
        "content-encoding",
        "transfer-encoding",
        "content-type",
        "content-length",
        "location",
    }
    result: dict[str, str] = {}
    for name, value in headers:
        if not isinstance(name, str) or not isinstance(value, str):
            raise HTTPIdentityRefusal("MARC1HT-F03", "header type differs")
        lowered = name.lower()
        if not lowered or "\r" in name or "\n" in name or "\r" in value or "\n" in value:
            raise HTTPIdentityRefusal("MARC1HT-F03", "header syntax differs")
        if lowered not in critical:
            continue
        if lowered in result:
            route = "MARC1HT-F02" if lowered == "content-encoding" else "MARC1HT-F03"
            raise HTTPIdentityRefusal(route, "critical header is duplicated")
        result[lowered] = value
    return result


def _validate_content_encoding(headers: Mapping[str, str]) -> str:
    if "content-encoding" not in headers:
        return "absent"
    value = headers["content-encoding"].strip()
    if not value:
        raise HTTPIdentityRefusal("MARC1HT-F02", "content encoding is empty")
    if value.casefold() != "identity":
        raise HTTPIdentityRefusal("MARC1HT-F02", "content coding is not identity")
    return "identity"


def validate_mock_terminal_response(
    response: MockResponse,
    *,
    expected_url: str = MOCK_ENDPOINT,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate one in-memory terminal response without decoding content."""

    if type(response.status) is not int or response.status != 200:
        raise HTTPIdentityRefusal("MARC1HT-F03", "terminal status differs")
    if response.reported_url != expected_url or expected_url != MOCK_ENDPOINT:
        raise HTTPIdentityRefusal("MARC1HT-F03", "terminal endpoint differs")
    headers = _critical_headers(response.headers)
    if "transfer-encoding" in headers:
        raise HTTPIdentityRefusal("MARC1HT-F03", "transfer encoding is forbidden")
    encoding_state = _validate_content_encoding(headers)
    content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        raise HTTPIdentityRefusal("MARC1HT-F03", "content type differs")
    declared = headers.get("content-length")
    if declared is not None:
        if not declared or any(character not in "0123456789" for character in declared):
            raise HTTPIdentityRefusal("MARC1HT-F03", "content length differs")
        if int(declared) > MAX_BODY_BYTES:
            raise HTTPIdentityRefusal("MARC1HT-F03", "content length differs")
        if int(declared) != len(response.body):
            raise HTTPIdentityRefusal("MARC1HT-F03", "content length does not match body")
    if len(response.body) > MAX_BODY_BYTES:
        raise HTTPIdentityRefusal("MARC1HT-F03", "body exceeds cap")
    rows = _parse_rows(response.body)
    return rows, {
        "content_encoding_state": encoding_state,
        "body_bytes": len(response.body),
        "body_sha256": _sha256_bytes(response.body),
        "content_length_present": declared is not None,
        "decompression_or_decoding_operations": 0,
        "raw_header_published": False,
        "raw_body_persisted": False,
        "URL_published": False,
    }


def validate_mock_redirect_target(
    target: str,
    addresses: Sequence[str],
) -> None:
    """Validate caller-supplied mock redirect facts without resolving a host."""

    parsed = urlsplit(target)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in {None, 443}
        or parsed.fragment
    ):
        raise HTTPIdentityRefusal("MARC1HT-F03", "redirect target differs")
    try:
        if not addresses or any(not ipaddress.ip_address(value).is_global for value in addresses):
            raise ValueError("non-global address")
    except ValueError as exc:
        raise HTTPIdentityRefusal("MARC1HT-F03", "redirect address is not global") from exc


def _response_for_case(
    payload: bytes,
    case_name: str,
    *,
    row_headers: Sequence[tuple[str, str]] = (),
    reported_url: str = MOCK_ENDPOINT,
) -> MockResponse:
    headers: list[tuple[str, str]] = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(payload))),
    ]
    values = {
        "Content_Encoding_absent": None,
        "Content_Encoding_identity_lowercase": "identity",
        "Content_Encoding_IDENTITY_uppercase": "IDENTITY",
        "Content_Encoding_IdEnTiTy_mixed_case": "IdEnTiTy",
    }
    if case_name not in values:
        raise ValueError("unknown accepted response case")
    if values[case_name] is not None:
        headers.append(("Content-Encoding", str(values[case_name])))
    headers.extend(row_headers)
    return MockResponse(200, reported_url, tuple(headers), payload)


def _selection_signature(result: selector.SelectionResult) -> dict[str, Any]:
    return {
        "cohort_summary": result.cohort_summary,
        "split_summary": result.split_summary,
        "byte_summary": result.byte_summary,
        "selection_hashes": result.selection_hashes,
    }


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], Any],
) -> tuple[str, str]:
    try:
        operation()
    except HTTPIdentityRefusal as exc:
        if exc.route != expected_route:
            raise HTTPIdentityRefusal(
                "MARC1HT-F04",
                f"mutation {name} used an unexpected route",
            ) from exc
        return name, exc.route
    raise HTTPIdentityRefusal("MARC1HT-F04", f"mutation {name} did not refuse")


def _replace_header(
    response: MockResponse,
    name: str,
    value: str,
    *,
    keep_existing: bool = False,
) -> MockResponse:
    lowered = name.lower()
    headers = list(response.headers)
    if not keep_existing:
        headers = [(key, item) for key, item in headers if key.lower() != lowered]
    headers.append((name, value))
    return MockResponse(response.status, response.reported_url, tuple(headers), response.body)


def _check_output_caps(public_bytes: bytes, private_bytes: bytes) -> None:
    if (
        len(public_bytes) > MAX_PUBLIC_OUTPUT_BYTES
        or len(public_bytes) + len(private_bytes) > MAX_COMBINED_OUTPUT_BYTES
        or len(public_bytes) + len(private_bytes) > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "output cap failed")


def _assert_new_output_directory(path: Path) -> None:
    if path.exists() or path.is_symlink():
        raise HTTPIdentityRefusal("MARC1HT-F05", "generated invocation already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise HTTPIdentityRefusal("MARC1HT-F04", "output parent differs")


def run_refusal_matrix(
    base_response: MockResponse,
    output_dir: Path,
) -> dict[str, str]:
    """Exercise every frozen refusal without real inputs or side effects."""

    target_rows = json.loads(base_response.body.decode("utf-8"))
    target_rows[0]["target"] = "forbidden"
    target_body = _canonical_json_bytes(target_rows)
    target_response = _response_for_case(target_body, "Content_Encoding_absent")
    cases: list[tuple[str, str, Callable[[], Any]]] = [
        (
            "Content_Encoding_present_empty",
            "MARC1HT-F02",
            lambda: validate_mock_terminal_response(
                _replace_header(base_response, "Content-Encoding", "")
            ),
        ),
        (
            "Content_Encoding_whitespace_only",
            "MARC1HT-F02",
            lambda: validate_mock_terminal_response(
                _replace_header(base_response, "Content-Encoding", "   ")
            ),
        ),
    ]
    for name, value in (
        ("Content_Encoding_gzip", "gzip"),
        ("Content_Encoding_br", "br"),
        ("Content_Encoding_deflate", "deflate"),
        ("Content_Encoding_compress", "compress"),
        ("Content_Encoding_unknown_token", "x-generated"),
        ("Content_Encoding_identity_plus_gzip", "identity, gzip"),
        ("Content_Encoding_parameterized_identity", "identity;q=1"),
    ):
        cases.append(
            (
                name,
                "MARC1HT-F02",
                lambda value=value: validate_mock_terminal_response(
                    _replace_header(base_response, "Content-Encoding", value)
                ),
            )
        )
    duplicate = _replace_header(base_response, "Content-Encoding", "identity")
    duplicate = _replace_header(
        duplicate,
        "Content-Encoding",
        "identity",
        keep_existing=True,
    )
    cases.extend(
        [
            (
                "duplicate_Content_Encoding",
                "MARC1HT-F02",
                lambda: validate_mock_terminal_response(duplicate),
            ),
            (
                "Transfer_Encoding_present",
                "MARC1HT-F03",
                lambda: validate_mock_terminal_response(
                    _replace_header(base_response, "Transfer-Encoding", "chunked")
                ),
            ),
            (
                "non_JSON_Content_Type",
                "MARC1HT-F03",
                lambda: validate_mock_terminal_response(
                    _replace_header(base_response, "Content-Type", "text/plain")
                ),
            ),
            (
                "malformed_Content_Length",
                "MARC1HT-F03",
                lambda: validate_mock_terminal_response(
                    _replace_header(base_response, "Content-Length", "not-a-number")
                ),
            ),
            (
                "body_overflow",
                "MARC1HT-F03",
                lambda: validate_mock_terminal_response(
                    _replace_header(base_response, "Content-Length", str(MAX_BODY_BYTES + 1))
                ),
            ),
            (
                "automatic_redirect",
                "MARC1HT-F03",
                lambda: validate_mock_terminal_response(
                    MockResponse(
                        base_response.status,
                        "https://redirected.generated.invalid/files",
                        base_response.headers,
                        base_response.body,
                    )
                ),
            ),
            (
                "private_or_nonglobal_redirect",
                "MARC1HT-F03",
                lambda: validate_mock_redirect_target(
                    "https://private.generated.invalid/files",
                    ("127.0.0.1",),
                ),
            ),
            (
                "alternate_endpoint",
                "MARC1HT-F03",
                lambda: validate_mock_terminal_response(
                    base_response,
                    expected_url="https://alternate.generated.invalid/files",
                ),
            ),
            (
                "target_like_public_field",
                "MARC1HT-F03",
                lambda: validate_mock_terminal_response(target_response),
            ),
            (
                "output_cap",
                "MARC1HT-F04",
                lambda: _check_output_caps(b"x" * (MAX_PUBLIC_OUTPUT_BYTES + 1), b""),
            ),
            (
                "second_invocation",
                "MARC1HT-F05",
                lambda: _assert_new_output_directory(output_dir),
            ),
        ]
    )
    if tuple(name for name, _, _ in cases) != REFUSAL_CASES:
        raise HTTPIdentityRefusal("MARC1HT-F01", "refusal implementation order differs")
    return dict(_expect_refusal(name, route, operation) for name, route, operation in cases)


def inspect_source_surface(path: Path | None = None) -> dict[str, Any]:
    """Inspect imports, calls, and commands without reading any external source."""

    source_path = path or Path(__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    calls: set[str] = set()
    functions: set[str] = set()
    commands: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
                if (
                    node.func.attr == "add_parser"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    commands.add(node.args[0].value)
    allowed_imports = {
        "__future__",
        "argparse",
        "ast",
        "dataclasses",
        "hashlib",
        "ipaddress",
        "json",
        "math",
        "neurodecodekit.datasets",
        "os",
        "pathlib",
        "resource",
        "stat",
        "sys",
        "time",
        "typing",
        "urllib.parse",
    }
    forbidden_calls = {
        "decompress",
        "execv",
        "execve",
        "fork",
        "getaddrinfo",
        "popen",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
        "system",
        "urlopen",
    }
    bad_imports = sorted(name for name in imports if name not in allowed_imports)
    bad_calls = sorted(calls & forbidden_calls)
    if bad_imports or bad_calls or "execute" in functions or commands != {
        "inspect",
        "plan",
        "qualify",
    }:
        raise HTTPIdentityRefusal("MARC1HT-F05", "source surface is forbidden")
    return {
        "source_sha256": _sha256_file(source_path),
        "network_client_imports": 0,
        "DNS_resolver_imports": 0,
        "decompressor_or_decoder_imports": 0,
        "forbidden_calls": 0,
        "execute_functions": 0,
        "allowed_commands": ["plan", "qualify", "inspect"],
    }


def _base_access_counters() -> dict[str, int]:
    return {
        "generated_fixture_runs": 1,
        "generated_mock_response_validations": 25,
        "generated_selection_runs": 5,
        "private_Freewill_manifest_reads": 0,
        "public_Wrist_metadata_requests": 0,
        "DNS_queries": 0,
        "network_body_bytes": 0,
        "real_participant_selections": 0,
        "payload_requests": 0,
        "payload_bytes": 0,
        "signal_sample_reads": 0,
        "event_or_quality_reads": 0,
        "target_reads": 0,
        "cache_split_epoch_window_or_feature_operations": 0,
        "model_runs": 0,
        "training_runs": 0,
        "prediction_sets": 0,
        "scoring_events": 0,
        "provider_or_language_model_calls": 0,
        "hardware_operations": 0,
        "retry_or_rerun_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _forbidden_counters_zero(counters: Mapping[str, int]) -> bool:
    permitted = {
        "generated_fixture_runs",
        "generated_mock_response_validations",
        "generated_selection_runs",
    }
    return all(value == 0 for key, value in counters.items() if key not in permitted)


def _private_public_outputs(
    selection: selector.SelectionResult,
    report: Mapping[str, Any],
) -> tuple[bytes, bytes]:
    private_bytes = _canonical_json_bytes(selection.private_manifest)
    report_bytes = _canonical_json_bytes(report)
    _check_output_caps(report_bytes, private_bytes)
    return report_bytes, private_bytes


def _write_exclusive(path: Path, payload: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            os.fchmod(descriptor, mode)
            offset = 0
            while offset < len(payload):
                offset += os.write(descriptor, payload[offset:])
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise HTTPIdentityRefusal("MARC1HT-F04", "exclusive output write failed") from exc


def _write_outputs(
    output_dir: Path,
    report_bytes: bytes,
    private_bytes: bytes,
) -> tuple[Path, Path]:
    _assert_new_output_directory(output_dir)
    created = False
    private_path = output_dir / PRIVATE_NAME
    report_path = output_dir / REPORT_NAME
    try:
        os.mkdir(output_dir, 0o700)
        created = True
        os.chmod(output_dir, 0o700)
        _write_exclusive(private_path, private_bytes, 0o600)
        _write_exclusive(report_path, report_bytes, 0o644)
    except Exception as exc:
        if created:
            for path in (report_path, private_path):
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
            try:
                output_dir.rmdir()
            except OSError:
                pass
        if isinstance(exc, HTTPIdentityRefusal):
            raise
        raise HTTPIdentityRefusal("MARC1HT-F04", "bounded output write failed") from exc
    if (
        stat.S_IMODE(private_path.stat().st_mode) != 0o600
        or stat.S_IMODE(report_path.stat().st_mode) != 0o644
        or private_path.stat().st_size != len(private_bytes)
        or report_path.stat().st_size != len(report_bytes)
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "written output differs")
    return report_path, private_path


def _walk_public_report(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if (
                "member_name" in lowered
                or "archive_name" in lowered
                or "local_header" in lowered
                or "download_url" in lowered
                or "raw_header" in lowered
                or "raw_body" in lowered
                or lowered in {"crc", "crc32", "file_id", "path", "paths", "url", "urls"}
                or lowered.endswith("_path")
                or lowered.endswith("_paths")
            ):
                raise HTTPIdentityRefusal("MARC1HT-F04", "public report leaks a private key")
            _walk_public_report(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public_report(child)
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            "https://" in lowered
            or ".codex_work" in lowered
            or "_eeg." in lowered
            or "_events.tsv" in lowered
            or lowered.endswith(".zip")
            or value.startswith("/")
            or "\\" in value
        ):
            raise HTTPIdentityRefusal("MARC1HT-F04", "public report leaks a private value")


def _is_nonnegative_int(value: Any) -> bool:
    return type(value) is int and value >= 0


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if set(report) != PUBLIC_REPORT_FIELDS:
        raise HTTPIdentityRefusal("MARC1HT-F04", "public report fields differ")
    if (
        report.get("schema_name")
        != "neurodecodekit.marc1_http_identity_semantics_qualification"
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != "MARC1HT-G1"
        or report.get("status") != "passed_generated_http_identity_semantics"
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "public report identity differs")
    _walk_public_report(report)
    gates = report.get("acceptance_gates")
    if (
        not isinstance(gates, dict)
        or set(gates) != set(ACCEPTANCE_GATES)
        or any(value is not True for value in gates.values())
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "acceptance gates differ")
    counters = report.get("access_counters")
    if counters != _base_access_counters() or not _forbidden_counters_zero(counters):
        raise HTTPIdentityRefusal("MARC1HT-F04", "forbidden counter is nonzero")
    proof = report.get("green_contract_proof")
    if not isinstance(proof, dict) or proof != {
        "commit": GREEN_CONTRACT_COMMIT,
        "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
        "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
        "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
        "contract_sha256": CONTRACT_SHA256,
        "policy_sha256": POLICY_SHA256,
    }:
        raise HTTPIdentityRefusal("MARC1HT-F04", "green contract proof differs")
    accepted = report.get("accepted_response_summary")
    expected_states = {
        "Content_Encoding_absent": "absent",
        "Content_Encoding_identity_lowercase": "identity",
        "Content_Encoding_IDENTITY_uppercase": "identity",
        "Content_Encoding_IdEnTiTy_mixed_case": "identity",
    }
    if (
        not isinstance(accepted, dict)
        or accepted.get("case_names") != list(ACCEPTED_CASES)
        or accepted.get("passed_count") != len(ACCEPTED_CASES)
        or accepted.get("all_body_hashes_identical") is not True
        or accepted.get("encoding_states") != expected_states
        or accepted.get("decompression_or_decoding_operations") != 0
        or not _is_sha256(accepted.get("canonical_body_sha256"))
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "accepted response summary differs")
    refusals = report.get("refusal_summary")
    if (
        not isinstance(refusals, dict)
        or refusals.get("case_names") != list(REFUSAL_CASES)
        or refusals.get("passed_count") != len(REFUSAL_CASES)
        or refusals.get("route_counts")
        != {
            "MARC1HT-F01": 0,
            "MARC1HT-F02": 10,
            "MARC1HT-F03": 8,
            "MARC1HT-F04": 1,
            "MARC1HT-F05": 1,
        }
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "refusal summary differs")
    replay = report.get("replay_summary")
    if (
        not isinstance(replay, dict)
        or replay.get("row_order_replay_exact") is not True
        or replay.get("selection_signature_identical") is not True
        or not _is_sha256(replay.get("replay_body_sha256"))
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "replay summary differs")
    cohort = report.get("cohort_summary")
    if (
        not isinstance(cohort, dict)
        or set(cohort)
        != {
            "freewill_selected_subject_ids",
            "wrist_selected_subject_ids",
            "selected_subjects_per_axis",
            "selection_was_target_quality_and_outcome_free",
        }
        or cohort.get("selected_subjects_per_axis") != 12
        or tuple(cohort.get("freewill_selected_subject_ids", ()))
        != EXPECTED_FREEWILL_SUBJECTS
        or tuple(cohort.get("wrist_selected_subject_ids", ())) != EXPECTED_WRIST_SUBJECTS
        or cohort.get("selection_was_target_quality_and_outcome_free") is not True
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "cohort summary differs")
    split = report.get("split_summary")
    expected_split = {
        "fit_heldout_overlap": 0,
        "freewill_fit_run_bundles": 36,
        "freewill_fit_session": "ses-01",
        "freewill_heldout_run_bundles": 36,
        "freewill_heldout_session": "ses-02",
        "freewill_selected_core_members": 288,
        "freewill_selected_run_bundles": 72,
        "wrist_expected_fit_trials": 2880,
        "wrist_expected_heldout_trials": 960,
        "wrist_fit_runs": 72,
        "wrist_fit_runs_per_participant": 6,
        "wrist_heldout_runs": 24,
        "wrist_heldout_runs_per_participant": 2,
    }
    if split != expected_split:
        raise HTTPIdentityRefusal("MARC1HT-F04", "split summary differs")
    hashes = report.get("selection_hashes")
    if (
        not isinstance(hashes, dict)
        or set(hashes)
        != {
            "aggregate_selection_identity_sha256",
            "freewill_generated_inventory_sha256",
            "freewill_selection_identity_sha256",
            "joint_selection_identity_sha256",
            "private_selection_manifest_sha256",
            "wrist_generated_metadata_sha256",
            "wrist_selection_identity_sha256",
        }
        or any(not _is_sha256(value) for value in hashes.values())
        or hashes.get("wrist_generated_metadata_sha256")
        != accepted.get("canonical_body_sha256")
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "selection hashes differ")
    byte_summary = report.get("byte_summary")
    if byte_summary != {
        "fallback_used": False,
        "freewill_payload_cap_bytes": 6 * 1024**3,
        "freewill_reserved_payload_bytes": 623853450,
        "joint_payload_cap_bytes": 8 * 1024**3,
        "joint_reserved_payload_bytes": 1228139402,
        "wrist_payload_cap_bytes": 2 * 1024**3,
        "wrist_reserved_payload_bytes": 604285952,
    }:
        raise HTTPIdentityRefusal("MARC1HT-F04", "byte summary differs")
    source_surface = report.get("source_surface")
    if (
        not isinstance(source_surface, dict)
        or source_surface.get("allowed_commands") != ["plan", "qualify", "inspect"]
        or any(
            source_surface.get(key) != 0
            for key in (
                "network_client_imports",
                "DNS_resolver_imports",
                "decompressor_or_decoder_imports",
                "forbidden_calls",
                "execute_functions",
            )
        )
        or not _is_sha256(source_surface.get("source_sha256"))
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "source surface differs")
    measurements = report.get("measurements")
    if not isinstance(measurements, dict):
        raise HTTPIdentityRefusal("MARC1HT-F04", "measurements differ")
    required_zero = (
        "network_bytes",
        "real_or_private_input_bytes",
        "raw_data_reads",
        "real_cache_reads",
        "model_runs",
        "training_runs",
    )
    integers = (
        "generated_input_bytes",
        "public_output_bytes",
        "private_output_bytes",
        "combined_output_bytes",
        "incremental_disk_bytes",
        "peak_RSS_bytes",
        *required_zero,
    )
    if any(not _is_nonnegative_int(measurements.get(key)) for key in integers):
        raise HTTPIdentityRefusal("MARC1HT-F04", "measurement type differs")
    runtime = measurements.get("runtime_seconds")
    if (
        type(runtime) not in {int, float}
        or not math.isfinite(runtime)
        or runtime < 0
        or runtime > MAX_RUNTIME_SECONDS
        or measurements["peak_RSS_bytes"] > MAX_PEAK_RSS_BYTES
        or measurements["generated_input_bytes"] > MAX_GENERATED_INPUT_BYTES
        or measurements["public_output_bytes"] > MAX_PUBLIC_OUTPUT_BYTES
        or measurements["combined_output_bytes"] > MAX_COMBINED_OUTPUT_BYTES
        or measurements["incremental_disk_bytes"] > MAX_INCREMENTAL_DISK_BYTES
        or measurements["combined_output_bytes"]
        != measurements["public_output_bytes"] + measurements["private_output_bytes"]
        or measurements["incremental_disk_bytes"] != measurements["combined_output_bytes"]
        or any(measurements[key] != 0 for key in required_zero)
        or (
            measurements.get("CPU_threads"),
            measurements.get("workers"),
            measurements.get("numerical_jobs"),
        )
        != (1, 1, 1)
        or measurements.get("producer_is_causal")
        != "not_applicable_metadata_transport_only"
        or measurements.get("end_to_end_latency_measured") is not False
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "resource measurement differs")


def _assert_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
) -> None:
    if (
        type(runtime_seconds) not in {int, float}
        or not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or not _is_nonnegative_int(peak_rss_bytes)
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or not _is_nonnegative_int(generated_input_bytes)
        or generated_input_bytes > MAX_GENERATED_INPUT_BYTES
    ):
        raise HTTPIdentityRefusal("MARC1HT-F04", "resource cap failed")
    if any(os.environ.get(key) not in {None, "1"} for key in THREAD_ENV_KEYS):
        raise HTTPIdentityRefusal("MARC1HT-F04", "numerical thread setting exceeds one")


def qualify_generated_identity_semantics(
    output_dir: str | Path,
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run one generated/mock qualification and write two bounded outputs."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    output = Path(output_dir)
    _assert_new_output_directory(output)
    started = clock()
    load_registered_contract(root)
    generated_contract = selector.load_registered_contract(root)
    source_surface = inspect_source_surface()

    freewill = selector.build_generated_freewill_manifest(contract=generated_contract)
    freewill_reversed = selector.build_generated_freewill_manifest(
        row_order="reversed",
        contract=generated_contract,
    )
    wrist = selector.build_generated_wrist_metadata()
    wrist_reversed = selector.build_generated_wrist_metadata(row_order="reversed")
    wrist_body = _canonical_json_bytes(wrist)
    wrist_reversed_body = _canonical_json_bytes(wrist_reversed)

    accepted: dict[str, dict[str, Any]] = {}
    first_selection: selector.SelectionResult | None = None
    first_signature: dict[str, Any] | None = None
    for case_name in ACCEPTED_CASES:
        response = _response_for_case(wrist_body, case_name)
        rows, transport = validate_mock_terminal_response(response)
        selected = selector.select_generated_pilot(
            freewill,
            rows,
            contract=generated_contract,
        )
        signature = _selection_signature(selected)
        if first_selection is None:
            first_selection = selected
            first_signature = signature
        elif signature != first_signature:
            raise HTTPIdentityRefusal("MARC1HT-F04", "accepted form selection differs")
        accepted[case_name] = transport
    if first_selection is None or first_signature is None:
        raise AssertionError("accepted qualification result is unavailable")

    reversed_rows, reversed_transport = validate_mock_terminal_response(
        _response_for_case(wrist_reversed_body, "Content_Encoding_absent")
    )
    replay = selector.select_generated_pilot(
        freewill_reversed,
        reversed_rows,
        contract=generated_contract,
    )
    if _selection_signature(replay) != first_signature:
        raise HTTPIdentityRefusal("MARC1HT-F04", "row-order replay differs")

    base_response = _response_for_case(wrist_body, "Content_Encoding_absent")
    refusals = run_refusal_matrix(base_response, output.parent)
    runtime = clock() - started
    peak_rss = int(rss_reader())
    generated_input_bytes = sum(
        (
            len(_canonical_json_bytes(freewill)),
            len(_canonical_json_bytes(freewill_reversed)),
            len(wrist_body) * len(ACCEPTED_CASES),
            len(wrist_reversed_body),
        )
    )
    _assert_resources(runtime, peak_rss, generated_input_bytes)
    counters = _base_access_counters()
    selection = first_selection
    aggregate_identity = {
        "accepted_body_sha256": _sha256_bytes(wrist_body),
        "cohort_summary": selection.cohort_summary,
        "split_summary": selection.split_summary,
        "selection_hashes": selection.selection_hashes,
    }
    report: dict[str, Any] = {
        "schema_name": "neurodecodekit.marc1_http_identity_semantics_qualification",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "passed_generated_http_identity_semantics",
        "route": "MARC1HT-G1",
        "proof_posture": "generated_metadata_and_mock_responses_only_no_scientific_value",
        "green_contract_proof": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "contract_sha256": CONTRACT_SHA256,
            "policy_sha256": POLICY_SHA256,
        },
        "accepted_response_summary": {
            "case_names": list(ACCEPTED_CASES),
            "passed_count": len(accepted),
            "canonical_body_sha256": _sha256_bytes(wrist_body),
            "all_body_hashes_identical": len(
                {value["body_sha256"] for value in accepted.values()}
            )
            == 1,
            "encoding_states": {
                name: value["content_encoding_state"] for name, value in accepted.items()
            },
            "decompression_or_decoding_operations": 0,
        },
        "refusal_summary": {
            "case_names": list(REFUSAL_CASES),
            "passed_count": len(refusals),
            "route_counts": {
                route: list(refusals.values()).count(route) for route in FAILURE_ROUTES
            },
        },
        "cohort_summary": selection.cohort_summary,
        "split_summary": selection.split_summary,
        "byte_summary": selection.byte_summary,
        "selection_hashes": {
            **selection.selection_hashes,
            "aggregate_selection_identity_sha256": _sha256_bytes(
                _canonical_json_bytes(aggregate_identity)
            ),
        },
        "source_surface": source_surface,
        "replay_summary": {
            "row_order_replay_exact": True,
            "replay_body_sha256": reversed_transport["body_sha256"],
            "selection_signature_identical": True,
        },
        "access_counters": counters,
        "measurements": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "generated_input_bytes": generated_input_bytes,
            "public_output_bytes": 0,
            "private_output_bytes": 0,
            "combined_output_bytes": 0,
            "incremental_disk_bytes": 0,
            "network_bytes": 0,
            "real_or_private_input_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_transport_only",
            "end_to_end_latency_measured": False,
        },
        "acceptance_gates": {name: True for name in ACCEPTANCE_GATES},
        "warnings": [
            "All metadata rows and HTTP responses were generated locally.",
            "The consumed live header remains unavailable and was not inferred.",
            "No network private input payload signal target model prediction or score was accessed.",
            "Generated MARC1HT-G1 has no source or scientific value.",
            "A future real metadata attempt remains a separate Tier C action.",
        ],
        "unavailable_fields": [
            "live response acceptance",
            "completed real pilot selection",
            "selected payload integrity",
            "neural signal target prediction and score",
            "language decoding and thought-to-text evidence",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A generated harness validates standards-aligned unencoded response semantics "
                "without changing frozen cohort selection or safety boundaries."
            ),
            "scientific_claim_not_established": (
                "Generated transport qualification establishes no neural effect language "
                "decoding or thought-to-text capability."
            ),
        },
    }
    private_bytes = _canonical_json_bytes(selection.private_manifest)
    for _ in range(8):
        report_bytes, private_bytes = _private_public_outputs(selection, report)
        total = len(report_bytes) + len(private_bytes)
        desired = {
            "public_output_bytes": len(report_bytes),
            "private_output_bytes": len(private_bytes),
            "combined_output_bytes": total,
            "incremental_disk_bytes": total,
        }
        if all(report["measurements"][key] == value for key, value in desired.items()):
            break
        report["measurements"].update(desired)
    else:
        raise HTTPIdentityRefusal("MARC1HT-F04", "output byte measurement did not stabilize")
    _validate_public_report(report)
    report_path, private_path = _write_outputs(output, report_bytes, private_bytes)
    return QualificationOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=private_path,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=len(report_bytes) + len(private_bytes),
    )


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Inspect one bounded aggregate generated result."""

    report_path = Path(path)
    if "private" in report_path.name.lower():
        raise HTTPIdentityRefusal("MARC1HT-F04", "private report inspection is forbidden")
    try:
        observed = os.lstat(report_path)
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
            raise OSError("not a regular file")
        if observed.st_size > MAX_PUBLIC_OUTPUT_BYTES:
            raise HTTPIdentityRefusal("MARC1HT-F04", "public report exceeds cap")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(report_path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != observed.st_dev
                or opened.st_ino != observed.st_ino
                or opened.st_size != observed.st_size
            ):
                raise OSError("report changed during open")
            payload = b""
            while chunk := os.read(descriptor, 64 * 1024):
                payload += chunk
                if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
                    raise HTTPIdentityRefusal("MARC1HT-F04", "public report exceeds cap")
        finally:
            os.close(descriptor)
        report = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except HTTPIdentityRefusal as exc:
        if exc.route == "MARC1HT-F04":
            raise
        raise HTTPIdentityRefusal("MARC1HT-F04", "public report is malformed") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPIdentityRefusal("MARC1HT-F04", "public report is unavailable") from exc
    if not isinstance(report, dict):
        raise HTTPIdentityRefusal("MARC1HT-F04", "public report root differs")
    _validate_public_report(report)
    if report["measurements"]["public_output_bytes"] != observed.st_size:
        raise HTTPIdentityRefusal("MARC1HT-F04", "public output byte measurement differs")
    return report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact zero-access generated qualification plan."""

    contract = load_registered_contract(repo_root)
    return {
        "lane_id": LANE_ID,
        "accepted_response_cases": list(ACCEPTED_CASES),
        "refusal_cases": list(REFUSAL_CASES),
        "acceptance_gates": list(ACCEPTANCE_GATES),
        "candidate_transport_policy_SHA256": POLICY_SHA256,
        "commands": list(contract["implementation_surface"]["commands"]),
        "network_bytes": 0,
        "real_or_private_input_bytes": 0,
        "payload_signal_target_model_or_score_operations": 0,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_http_identity_semantics",
        description="Generated-only MARC1 HTTP identity-semantics qualification.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the zero-access registered plan.")
    qualify = subparsers.add_parser("qualify", help="Run generated/mock qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate generated report.")
    inspect.add_argument("report")
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
        if args.command == "inspect":
            report = inspect_generated_report(args.report)
            print(_canonical_json_bytes(report).decode("ascii"), end="")
            return 0
        outcome = qualify_generated_identity_semantics(args.output_dir)
        print(
            _canonical_json_bytes(
                {
                    "status": outcome.report["status"],
                    "route": outcome.report["route"],
                    "report": str(outcome.report_path),
                    "generated_input_bytes": outcome.generated_input_bytes,
                    "generated_output_bytes": outcome.generated_output_bytes,
                    "runtime_seconds": outcome.runtime_seconds,
                    "peak_RSS_bytes": outcome.peak_rss_bytes,
                }
            ).decode("ascii"),
            end="",
        )
        return 0
    except HTTPIdentityRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
