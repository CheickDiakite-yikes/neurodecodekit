"""Generated-only qualification for MARC1 versioned pagination semantics."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import re
import resource
import stat
import sys
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.datasets import marc1_pilot_selection as selector


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC1-PG1"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc1_versioned_pagination_recovery_contract.v0.json"
)
CONTRACT_SHA256 = "22f7e3ba36f0c92af600d5a00a90581c44338609de19105cf6be374b5fad7a9b"
POLICY_SHA256 = "c4e80a99e782ac61d5e5b32e371c9cbb40580254376f518e9820a507402b1624"
GREEN_CONTRACT_COMMIT = "ccb3ba8a839b3e6fc6844ad867ab0d5d295e20fb"
GREEN_CONTRACT_CI_RUN_ID = 31591853349
GREEN_CONTRACT_BASE_JOB_ID = 94098410925
GREEN_CONTRACT_OPTIONAL_JOB_ID = 94098410868

REQUEST_PATH = "/v2/articles/29666735/versions/3/files"
REQUEST_QUERY = "page=1&page_size=1000"
MOCK_RESPONSE_URL = "https://generated.invalid/marc1-pg1/version-3-files"
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

REPORT_NAME = "marc1_versioned_pagination_qualification.v0.json"
PRIVATE_NAME = "marc1_versioned_pagination.generated.private.v0.json"
WRIST_FIELDS = {
    "computed_md5",
    "download_url",
    "id",
    "is_link_only",
    "name",
    "size",
    "supplied_md5",
}
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
MD5_RE = re.compile(r"[0-9a-f]{32}")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
PARTICIPANT_RE = re.compile(r"(?P<subject>sub-(?:0[1-9]|[1-3][0-9]|4[0-5]))\.zip")

ACCEPTED_CASES = (
    "canonical_rows_absent_Content_Encoding",
    "reversed_rows_absent_Content_Encoding",
    "canonical_rows_identity_Content_Encoding",
    "reversed_rows_mixed_case_identity_Content_Encoding",
)
REFUSAL_CASES = (
    "wrong_green_research_commit",
    "wrong_research_document_hash",
    "wrong_research_registry_hash",
    "wrong_pagination_policy_hash",
    "missing_query",
    "missing_page",
    "missing_page_size",
    "page_zero",
    "page_noninteger",
    "page_size_default_10",
    "page_size_over_1000",
    "reversed_query_order",
    "duplicate_page",
    "mixed_limit_offset_pagination",
    "non_200_status",
    "redirect_evidence",
    "gzip_Content_Encoding",
    "Transfer_Encoding_present",
    "non_JSON_Content_Type",
    "malformed_Content_Length",
    "Content_Length_body_mismatch",
    "response_body_overflow",
    "malformed_JSON",
    "duplicate_JSON_key",
    "non_array_JSON_root",
    "non_object_row",
    "target_like_extra_field",
    "ten_row_partial_page",
    "fifty_four_row_inventory",
    "fifty_six_row_inventory",
    "duplicate_row_identity",
    "participant_or_supplementary_identity_mutation",
    "wrong_downloader_URL",
    "supplied_computed_MD5_disagreement",
    "sub_01_anchor_mismatch",
    "declared_byte_total_mismatch",
    "private_value_in_public_output",
    "forbidden_source_surface",
    "output_cap_breach",
    "nondeterministic_replay",
    "second_generated_closeout_invocation",
)
FAILURE_ROUTES = {
    "MARC1PG-F00": "proof_source_commit_contract_or_request_identity_mismatch",
    "MARC1PG-F01": "malformed_query_mixed_pagination_or_hidden_override",
    "MARC1PG-F02": "generated_HTTP_envelope_encoding_redirect_or_body_cap",
    "MARC1PG-F03": "JSON_root_duplicate_key_field_or_type",
    "MARC1PG-F04": "exact_row_participant_or_supplementary_count",
    "MARC1PG-F05": "URL_MD5_sub01_declared_or_selected_bytes",
    "MARC1PG-F06": "target_private_old_root_or_payload_boundary",
    "MARC1PG-F07": "resource_output_overwrite_retry_or_replay",
}
ACCEPTANCE_GATES = (
    "exact_green_research_proof",
    "exact_contract_and_frozen_source_hashes",
    "exact_canonical_pagination_policy_hash",
    "exact_byte_for_byte_request_serialization",
    "all_four_accepted_cases_pass",
    "accepted_cases_have_identical_semantic_and_selection_hashes",
    "all_forty_one_mutations_refuse_under_registered_routes",
    "generated_ten_row_default_page_refuses",
    "exact_55_rows_pass_and_54_56_refuse",
    "exact_participant_supplementary_total_byte_and_sub01_identity",
    "exact_12_plus_12_participant_selection",
    "exact_72_bundle_288_member_12_archive_splits_and_zero_overlap",
    "selection_is_target_quality_size_checksum_and_outcome_free",
    "private_public_output_separation",
    "source_has_no_real_network_consumed_root_payload_or_model_surface",
    "all_real_private_neural_target_model_score_and_claim_counters_zero",
    "thread_runtime_RSS_input_output_and_disk_caps",
    "deterministic_aggregate_and_private_output_hashes",
)
PUBLIC_REPORT_FIELDS = {
    "schema_name",
    "schema_version",
    "lane_id",
    "status",
    "route",
    "proof_posture",
    "green_contract_proof",
    "request_summary",
    "response_summary",
    "refusal_summary",
    "inventory_summary",
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


class PaginationRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-PG1 route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC1-PG1 failure route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class MockRequest:
    """In-memory request identity with no transport behavior."""

    method: str
    scheme: str
    host: str
    path: str
    query: str
    headers: tuple[tuple[str, str], ...]
    body: bytes


@dataclass(frozen=True)
class MockResponse:
    """In-memory terminal response with no transport behavior."""

    status: int
    reported_url: str
    headers: tuple[tuple[str, str], ...]
    body: bytes
    redirect_count: int = 0


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
        before = os.lstat(path)
    except OSError as exc:
        raise PaginationRefusal("MARC1PG-F00", "bound artifact is unavailable") from exc
    if not stat.S_ISREG(before.st_mode):
        raise PaginationRefusal("MARC1PG-F00", "bound artifact is not a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    digest = hashlib.sha256()
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or opened.st_size != before.st_size
            ):
                raise PaginationRefusal("MARC1PG-F00", "bound artifact changed")
            while chunk := os.read(descriptor, 64 * 1024):
                digest.update(chunk)
        finally:
            os.close(descriptor)
    except PaginationRefusal:
        raise
    except OSError as exc:
        raise PaginationRefusal("MARC1PG-F00", "bound artifact read failed") from exc
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _canonical_policy_hash(policy: Mapping[str, Any]) -> str:
    payload = json.dumps(
        policy,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return _sha256_bytes(payload)


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact generated-only contract after remote-green proof."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _sha256_file(path) != CONTRACT_SHA256:
        raise PaginationRefusal("MARC1PG-F00", "contract hash differs")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PaginationRefusal("MARC1PG-F00", "contract is unavailable") from exc
    _verify_contract(contract, root)
    return contract


def _verify_contract(contract: Mapping[str, Any], root: Path) -> None:
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc1_versioned_pagination_recovery_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("contract_id")
        != "MARC1-PG1-generated-versioned-pagination-v0"
        or contract.get("status")
        != "frozen_generated_only_contract_real_inputs_and_execution_unauthorized"
        or contract.get("acceptance_route") != "MARC1PG-G1"
    ):
        raise PaginationRefusal("MARC1PG-F00", "contract identity differs")
    proof = contract.get("green_research_anchor")
    if (
        not isinstance(proof, dict)
        or proof.get("commit")
        != "7a7883abda094eb9f202215b8b138a17cdff022e"
        or proof.get("CI_run_id") != 31591022429
        or proof.get("base_python_job_id") != 94095736694
        or proof.get("optional_neuro_job_id") != 94095736770
        or proof.get("both_required_jobs_green") is not True
    ):
        raise PaginationRefusal("MARC1PG-F00", "research proof differs")
    for name in ("research_document", "research_registry"):
        binding = proof.get(name)
        if (
            not isinstance(binding, dict)
            or _sha256_file(root / str(binding.get("path"))) != binding.get("SHA256")
        ):
            raise PaginationRefusal("MARC1PG-F00", "research artifact differs")
    bindings = contract.get("frozen_source_bindings")
    if not isinstance(bindings, dict):
        raise PaginationRefusal("MARC1PG-F00", "source bindings differ")
    for binding in bindings.values():
        if (
            not isinstance(binding, dict)
            or _sha256_file(root / str(binding.get("path"))) != binding.get("SHA256")
        ):
            raise PaginationRefusal("MARC1PG-F00", "frozen source differs")
    if _canonical_policy_hash(contract.get("candidate_pagination_policy", {})) != POLICY_SHA256:
        raise PaginationRefusal("MARC1PG-F00", "pagination policy differs")
    if contract.get("candidate_pagination_policy_SHA256") != POLICY_SHA256:
        raise PaginationRefusal("MARC1PG-F00", "pagination policy hash differs")
    if tuple(contract.get("accepted_cases", ())) != ACCEPTED_CASES:
        raise PaginationRefusal("MARC1PG-F00", "accepted case inventory differs")
    if tuple(contract.get("refusal_cases", ())) != REFUSAL_CASES:
        raise PaginationRefusal("MARC1PG-F00", "refusal inventory differs")
    if tuple(contract.get("acceptance_gates", ())) != ACCEPTANCE_GATES:
        raise PaginationRefusal("MARC1PG-F00", "acceptance gates differ")


def canonical_request() -> MockRequest:
    """Return the one frozen generated request identity."""

    return MockRequest(
        method="GET",
        scheme="https",
        host="api.figshare.com",
        path=REQUEST_PATH,
        query=REQUEST_QUERY,
        headers=(("Accept", "application/json"), ("Accept-Encoding", "identity")),
        body=b"",
    )


def validate_mock_request(request: MockRequest) -> dict[str, Any]:
    """Validate and serialize the exact request without opening a connection."""

    if (
        not isinstance(request, MockRequest)
        or request.method != "GET"
        or request.scheme != "https"
        or request.host != "api.figshare.com"
        or request.path != REQUEST_PATH
        or request.query != REQUEST_QUERY
        or request.headers
        != (("Accept", "application/json"), ("Accept-Encoding", "identity"))
        or request.body != b""
    ):
        raise PaginationRefusal("MARC1PG-F01", "request identity differs")
    request_bytes = (
        f"GET {REQUEST_PATH}?{REQUEST_QUERY} HTTP/1.1\r\n"
        "Host: api.figshare.com\r\n"
        "Accept: application/json\r\n"
        "Accept-Encoding: identity\r\n"
        "\r\n"
    ).encode("ascii")
    return {
        "method": request.method,
        "path": request.path,
        "query": request.query,
        "page": 1,
        "page_size": 1000,
        "request_bytes": len(request_bytes),
        "request_sha256": _sha256_bytes(request_bytes),
        "response_body_count": 1,
        "second_page_requests": 0,
        "fallback_requests": 0,
    }


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _target_like_key(value: str) -> bool:
    lowered = value.strip().lower().replace("-", "_")
    return lowered in TARGET_LIKE_KEYS or any(
        token in lowered for token in ("target", "label", "sentence", "response")
    )


def _reject_target_like_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if _target_like_key(str(key)):
                raise PaginationRefusal("MARC1PG-F06", "target-like field is forbidden")
            _reject_target_like_fields(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_target_like_fields(nested)


def _critical_headers(rows: Sequence[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    allowed = {"content-encoding", "content-length", "content-type", "transfer-encoding"}
    for raw_key, raw_value in rows:
        key = str(raw_key).strip().lower()
        value = str(raw_value).strip()
        if not key or "\r" in value or "\n" in value:
            raise PaginationRefusal("MARC1PG-F02", "response header differs")
        if key not in allowed:
            continue
        if key in result:
            raise PaginationRefusal("MARC1PG-F02", "critical header is duplicated")
        result[key] = value
    return result


def parse_mock_response(response: MockResponse) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate one generated terminal response and parse strict JSON rows."""

    if type(response.status) is not int or response.status != 200:
        raise PaginationRefusal("MARC1PG-F02", "terminal status differs")
    if response.reported_url != MOCK_RESPONSE_URL or response.redirect_count != 0:
        raise PaginationRefusal("MARC1PG-F02", "terminal response identity differs")
    headers = _critical_headers(response.headers)
    if "transfer-encoding" in headers:
        raise PaginationRefusal("MARC1PG-F02", "transfer encoding is forbidden")
    encoding = headers.get("content-encoding")
    if encoding is None:
        encoding_state = "absent"
    elif encoding and encoding.casefold() == "identity" and "," not in encoding:
        encoding_state = "identity"
    else:
        raise PaginationRefusal("MARC1PG-F02", "content encoding differs")
    content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        raise PaginationRefusal("MARC1PG-F02", "content type differs")
    declared = headers.get("content-length")
    if declared is not None:
        if not declared or any(character not in "0123456789" for character in declared):
            raise PaginationRefusal("MARC1PG-F02", "content length differs")
        if int(declared) > MAX_BODY_BYTES or int(declared) != len(response.body):
            raise PaginationRefusal("MARC1PG-F02", "content length does not match body")
    if len(response.body) > MAX_BODY_BYTES:
        raise PaginationRefusal("MARC1PG-F02", "response body exceeds cap")
    try:
        value = json.loads(
            response.body.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PaginationRefusal("MARC1PG-F03", "response JSON differs") from exc
    if not isinstance(value, list):
        raise PaginationRefusal("MARC1PG-F03", "response root differs")
    if any(not isinstance(row, dict) for row in value):
        raise PaginationRefusal("MARC1PG-F03", "response row type differs")
    _reject_target_like_fields(value)
    return value, {
        "body_bytes": len(response.body),
        "body_sha256": _sha256_bytes(response.body),
        "content_encoding_state": encoding_state,
        "content_length_present": declared is not None,
        "redirect_count": 0,
        "decompression_or_decoding_operations": 0,
    }


def build_generated_wrist_rows(*, reverse_rows: bool = False) -> list[dict[str, Any]]:
    """Build the exact 55-row public schema entirely from generated values."""

    rows: list[dict[str, Any]] = []
    participant_total = 0
    for index in range(1, 46):
        name = f"sub-{index:02d}.zip"
        if index == 1:
            file_id = 62_570_743
            size = 33_690_749
            digest = "6b01cf5bd30de0c670d2837d112a17fa"
        else:
            file_id = 62_570_743 + index
            size = 50_000_000 + index
            digest = hashlib.md5(name.encode("ascii"), usedforsecurity=False).hexdigest()
        participant_total += size
        rows.append(
            {
                "computed_md5": digest,
                "download_url": f"https://ndownloader.figshare.com/files/{file_id}",
                "id": file_id,
                "is_link_only": False,
                "name": name,
                "size": size,
                "supplied_md5": digest,
            }
        )
    remaining = 3_683_416_050 - participant_total
    base, remainder = divmod(remaining, 10)
    for index in range(10):
        name = f"supplement-{index:02d}.txt"
        file_id = 70_000_000 + index
        digest = hashlib.md5(name.encode("ascii"), usedforsecurity=False).hexdigest()
        rows.append(
            {
                "computed_md5": digest,
                "download_url": f"https://ndownloader.figshare.com/files/{file_id}",
                "id": file_id,
                "is_link_only": False,
                "name": name,
                "size": base + (1 if index < remainder else 0),
                "supplied_md5": digest,
            }
        )
    if reverse_rows:
        rows.reverse()
    return rows


def _safe_filename(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value
        or unicodedata.normalize("NFC", value) != value
        or value in {".", ".."}
        or "/" in value
        or "\\" in value
        or "\x00" in value
    ):
        raise PaginationRefusal("MARC1PG-F03", "filename differs")
    return value


def validate_wrist_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate the unchanged 55-row semantic identity."""

    if not isinstance(rows, list) or len(rows) != 55:
        raise PaginationRefusal("MARC1PG-F04", "Wrist row count differs")
    file_ids: set[int] = set()
    names: set[str] = set()
    participants: dict[str, dict[str, Any]] = {}
    supplementary = 0
    total_bytes = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != WRIST_FIELDS:
            raise PaginationRefusal("MARC1PG-F03", "Wrist row fields differ")
        file_id = row["id"]
        size = row["size"]
        name = _safe_filename(row["name"])
        if (
            isinstance(file_id, bool)
            or not isinstance(file_id, int)
            or file_id <= 0
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size <= 0
            or row["is_link_only"] is not False
        ):
            raise PaginationRefusal("MARC1PG-F03", "Wrist row type differs")
        if file_id in file_ids or name in names:
            raise PaginationRefusal("MARC1PG-F04", "Wrist row identity is duplicated")
        file_ids.add(file_id)
        names.add(name)
        expected_url = f"https://ndownloader.figshare.com/files/{file_id}"
        if row["download_url"] != expected_url:
            raise PaginationRefusal("MARC1PG-F05", "downloader URL differs")
        for key in ("supplied_md5", "computed_md5"):
            if not isinstance(row[key], str) or MD5_RE.fullmatch(row[key]) is None:
                raise PaginationRefusal("MARC1PG-F05", "MD5 declaration differs")
        if row["supplied_md5"] != row["computed_md5"]:
            raise PaginationRefusal("MARC1PG-F05", "MD5 declarations disagree")
        total_bytes += size
        match = PARTICIPANT_RE.fullmatch(name)
        if match is None:
            supplementary += 1
        else:
            participants[match.group("subject")] = dict(row)
    expected_subjects = {f"sub-{index:02d}" for index in range(1, 46)}
    if set(participants) != expected_subjects or supplementary != 10:
        raise PaginationRefusal("MARC1PG-F04", "participant inventory differs")
    sub01 = participants["sub-01"]
    if (
        sub01["id"] != 62_570_743
        or sub01["size"] != 33_690_749
        or sub01["computed_md5"] != "6b01cf5bd30de0c670d2837d112a17fa"
    ):
        raise PaginationRefusal("MARC1PG-F05", "sub-01 identity differs")
    if total_bytes != 3_683_416_050:
        raise PaginationRefusal("MARC1PG-F05", "declared byte total differs")
    canonical_rows = sorted((dict(row) for row in rows), key=lambda row: row["id"])
    return {
        "rows": list(rows),
        "participants": participants,
        "participant_archives": 45,
        "supplementary_rows": supplementary,
        "declared_bytes": total_bytes,
        "canonical_source_sha256": _sha256_bytes(_canonical_json_bytes(canonical_rows)),
    }


def _selection_from_generated_sources(
    freewill_manifest: Mapping[str, Any],
    wrist: Mapping[str, Any],
    *,
    selector_contract: Mapping[str, Any],
) -> selector.SelectionResult:
    try:
        freewill = selector._validate_freewill_manifest(freewill_manifest, selector_contract)
        axis = selector_contract["wrist_axis"]
        ranked = selector._rank_subjects(
            axis["selection_seed"], axis["eligible_subject_ids"]
        )[: selector.EXPECTED_SELECTED_SUBJECTS]
        selector._validate_selected_subjects(
            ranked,
            axis["selected_subject_ids_in_rank_order"],
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
        raise PaginationRefusal("MARC1PG-F05", "frozen selector refused") from exc
    selected_subjects = list(axis["selected_subject_ids_in_rank_order"])
    participants = wrist["participants"]
    selected = [participants[subject] for subject in selected_subjects]
    wrist_reserved = sum(int(row["size"]) for row in selected)
    if wrist_reserved > selector.WRIST_PAYLOAD_CAP_BYTES:
        raise PaginationRefusal("MARC1PG-F05", "selected Wrist bytes exceed cap")
    joint_reserved = int(freewill["reserved_bytes"]) + wrist_reserved
    if joint_reserved > selector.JOINT_PAYLOAD_CAP_BYTES:
        raise PaginationRefusal("MARC1PG-F05", "joint selected bytes exceed cap")
    wrist_rows = [
        {
            "source_id": "wrist_45_generated_pagination_shape",
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
        for subject in selected_subjects
    ]
    private_rows = list(freewill["private_rows"]) + wrist_rows
    if len(private_rows) != 300 or any(
        tuple(row) != selector.PRIVATE_ROW_FIELDS for row in private_rows
    ):
        raise PaginationRefusal("MARC1PG-F06", "private row shape differs")
    private_manifest = {
        "schema_name": "neurodecodekit.marc1_pagination_generated_private_manifest",
        "schema_version": SCHEMA_VERSION,
        "proof_posture": "generated_only_no_source_or_scientific_value",
        "rows": private_rows,
    }
    freewill_identity = freewill["selection_identity"]
    wrist_identity = {
        "selected_subject_ids": selected_subjects,
        "fit_runs": [1, 2, 3, 4, 5, 6],
        "heldout_runs": [7, 8],
    }
    joint_identity = {"freewill": freewill_identity, "wrist": wrist_identity}
    return selector.SelectionResult(
        private_manifest=private_manifest,
        cohort_summary={
            "freewill_selected_subject_ids": list(
                selector_contract["freewill_axis"]["selected_subject_ids_in_rank_order"]
            ),
            "wrist_selected_subject_ids": selected_subjects,
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
            "wrist_expected_fit_trials": 2880,
            "wrist_expected_heldout_trials": 960,
            "fit_heldout_overlap": 0,
        },
        byte_summary={
            "freewill_reserved_payload_bytes": freewill["reserved_bytes"],
            "freewill_payload_cap_bytes": selector.FREEWILL_PAYLOAD_CAP_BYTES,
            "wrist_reserved_payload_bytes": wrist_reserved,
            "wrist_payload_cap_bytes": selector.WRIST_PAYLOAD_CAP_BYTES,
            "joint_reserved_payload_bytes": joint_reserved,
            "joint_payload_cap_bytes": selector.JOINT_PAYLOAD_CAP_BYTES,
            "fallback_used": False,
        },
        selection_hashes={
            "freewill_generated_inventory_sha256": freewill["source_sha256"],
            "wrist_canonical_metadata_sha256": wrist["canonical_source_sha256"],
            "freewill_selection_identity_sha256": freewill[
                "selection_identity_sha256"
            ],
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


def _response_for_case(rows: Sequence[Mapping[str, Any]], case_name: str) -> MockResponse:
    reverse = case_name.startswith("reversed")
    ordered = list(reversed(rows)) if reverse else list(rows)
    body = _canonical_json_bytes(ordered)
    headers: list[tuple[str, str]] = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body))),
    ]
    if case_name == "canonical_rows_identity_Content_Encoding":
        headers.append(("Content-Encoding", "identity"))
    elif case_name == "reversed_rows_mixed_case_identity_Content_Encoding":
        headers.append(("Content-Encoding", "IdEnTiTy"))
    elif case_name not in {
        "canonical_rows_absent_Content_Encoding",
        "reversed_rows_absent_Content_Encoding",
    }:
        raise ValueError("unknown accepted case")
    return MockResponse(200, MOCK_RESPONSE_URL, tuple(headers), body)


def _replace_request(request: MockRequest, **changes: Any) -> MockRequest:
    values = {
        "method": request.method,
        "scheme": request.scheme,
        "host": request.host,
        "path": request.path,
        "query": request.query,
        "headers": request.headers,
        "body": request.body,
    }
    values.update(changes)
    return MockRequest(**values)


def _replace_response(response: MockResponse, **changes: Any) -> MockResponse:
    values = {
        "status": response.status,
        "reported_url": response.reported_url,
        "headers": response.headers,
        "body": response.body,
        "redirect_count": response.redirect_count,
    }
    values.update(changes)
    return MockResponse(**values)


def _replace_header(response: MockResponse, key: str, value: str) -> MockResponse:
    lowered = key.casefold()
    headers = [(name, item) for name, item in response.headers if name.casefold() != lowered]
    headers.append((key, value))
    return _replace_response(response, headers=tuple(headers))


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], Any],
) -> tuple[str, str]:
    try:
        operation()
    except PaginationRefusal as exc:
        if exc.route != expected_route:
            raise AssertionError(
                f"{name} routed to {exc.route}, expected {expected_route}"
            ) from exc
        return name, exc.route
    raise AssertionError(f"required mutation did not refuse: {name}")


def _assert_policy_hash(observed: str) -> None:
    if observed != POLICY_SHA256:
        raise PaginationRefusal("MARC1PG-F00", "pagination policy hash differs")


def _assert_replay(first: str, second: str) -> None:
    if first != second:
        raise PaginationRefusal("MARC1PG-F07", "generated replay differs")


def _check_output_caps(public_bytes: bytes, private_bytes: bytes) -> None:
    if len(public_bytes) > MAX_PUBLIC_OUTPUT_BYTES:
        raise PaginationRefusal("MARC1PG-F07", "public output exceeds cap")
    if len(public_bytes) + len(private_bytes) > MAX_COMBINED_OUTPUT_BYTES:
        raise PaginationRefusal("MARC1PG-F07", "combined output exceeds cap")


def _assert_new_output_directory(path: Path) -> None:
    try:
        if path.exists() or path.is_symlink():
            raise PaginationRefusal("MARC1PG-F07", "output directory already exists")
        if path.parent.is_symlink():
            raise PaginationRefusal("MARC1PG-F07", "output parent is a symlink")
    except OSError as exc:
        raise PaginationRefusal("MARC1PG-F07", "output preflight failed") from exc


def run_refusal_matrix(
    request: MockRequest,
    response: MockResponse,
    rows: Sequence[Mapping[str, Any]],
    existing_output: Path,
) -> dict[str, str]:
    """Exercise all 41 frozen mutations using generated values only."""

    contract = load_registered_contract()
    cases: list[tuple[str, str, Callable[[], Any]]] = []
    for name, field in (
        ("wrong_green_research_commit", "commit"),
        ("wrong_research_document_hash", "research_document"),
        ("wrong_research_registry_hash", "research_registry"),
    ):
        changed = copy.deepcopy(contract)
        if field == "commit":
            changed["green_research_anchor"]["commit"] = "0" * 40
        else:
            changed["green_research_anchor"][field]["SHA256"] = "0" * 64
        cases.append(
            (name, "MARC1PG-F00", lambda value=changed: _verify_contract(value, _repo_root()))
        )
    cases.append(
        (
            "wrong_pagination_policy_hash",
            "MARC1PG-F00",
            lambda: _assert_policy_hash("0" * 64),
        )
    )
    query_mutations = {
        "missing_query": "",
        "missing_page": "page_size=1000",
        "missing_page_size": "page=1",
        "page_zero": "page=0&page_size=1000",
        "page_noninteger": "page=one&page_size=1000",
        "page_size_default_10": "page=1&page_size=10",
        "page_size_over_1000": "page=1&page_size=1001",
        "reversed_query_order": "page_size=1000&page=1",
        "duplicate_page": "page=1&page=1&page_size=1000",
        "mixed_limit_offset_pagination": "page=1&page_size=1000&limit=55&offset=0",
    }
    for name, query in query_mutations.items():
        changed = _replace_request(request, query=query)
        cases.append((name, "MARC1PG-F01", lambda value=changed: validate_mock_request(value)))
    cases.extend(
        (
            (
                "non_200_status",
                "MARC1PG-F02",
                lambda: parse_mock_response(_replace_response(response, status=206)),
            ),
            (
                "redirect_evidence",
                "MARC1PG-F02",
                lambda: parse_mock_response(_replace_response(response, redirect_count=1)),
            ),
            (
                "gzip_Content_Encoding",
                "MARC1PG-F02",
                lambda: parse_mock_response(
                    _replace_header(response, "Content-Encoding", "gzip")
                ),
            ),
            (
                "Transfer_Encoding_present",
                "MARC1PG-F02",
                lambda: parse_mock_response(
                    _replace_header(response, "Transfer-Encoding", "chunked")
                ),
            ),
            (
                "non_JSON_Content_Type",
                "MARC1PG-F02",
                lambda: parse_mock_response(
                    _replace_header(response, "Content-Type", "text/plain")
                ),
            ),
            (
                "malformed_Content_Length",
                "MARC1PG-F02",
                lambda: parse_mock_response(
                    _replace_header(response, "Content-Length", "bad")
                ),
            ),
            (
                "Content_Length_body_mismatch",
                "MARC1PG-F02",
                lambda: parse_mock_response(
                    _replace_header(response, "Content-Length", "1")
                ),
            ),
            (
                "response_body_overflow",
                "MARC1PG-F02",
                lambda: parse_mock_response(
                    _replace_response(
                        response,
                        headers=(("Content-Type", "application/json"),),
                        body=b"[" + b" " * MAX_BODY_BYTES + b"]",
                    )
                ),
            ),
            (
                "malformed_JSON",
                "MARC1PG-F03",
                lambda: parse_mock_response(
                    _replace_response(
                        response,
                        headers=(("Content-Type", "application/json"),),
                        body=b"[",
                    )
                ),
            ),
            (
                "duplicate_JSON_key",
                "MARC1PG-F03",
                lambda: parse_mock_response(
                    _replace_response(
                        response,
                        headers=(("Content-Type", "application/json"),),
                        body=b'[{"id":1,"id":2}]',
                    )
                ),
            ),
            (
                "non_array_JSON_root",
                "MARC1PG-F03",
                lambda: parse_mock_response(
                    _replace_response(
                        response,
                        headers=(("Content-Type", "application/json"),),
                        body=b"{}",
                    )
                ),
            ),
            (
                "non_object_row",
                "MARC1PG-F03",
                lambda: parse_mock_response(
                    _replace_response(
                        response,
                        headers=(("Content-Type", "application/json"),),
                        body=_canonical_json_bytes([0] * 55),
                    )
                ),
            ),
        )
    )
    target_rows = copy.deepcopy(list(rows))
    target_rows[0]["target"] = "forbidden"
    target_response = _response_for_case(
        target_rows, "canonical_rows_absent_Content_Encoding"
    )
    cases.append(
        (
            "target_like_extra_field",
            "MARC1PG-F06",
            lambda: parse_mock_response(target_response),
        )
    )
    for name, count in (
        ("ten_row_partial_page", 10),
        ("fifty_four_row_inventory", 54),
    ):
        subset = copy.deepcopy(list(rows)[:count])
        cases.append(
            (name, "MARC1PG-F04", lambda value=subset: validate_wrist_rows(value))
        )
    extra_rows = copy.deepcopy(list(rows))
    extra = copy.deepcopy(extra_rows[-1])
    extra["id"] = 80_000_000
    extra["name"] = "extra-supplement.txt"
    extra["download_url"] = "https://ndownloader.figshare.com/files/80000000"
    extra["computed_md5"] = hashlib.md5(
        b"extra-supplement.txt", usedforsecurity=False
    ).hexdigest()
    extra["supplied_md5"] = extra["computed_md5"]
    extra_rows.append(extra)
    cases.append(
        (
            "fifty_six_row_inventory",
            "MARC1PG-F04",
            lambda: validate_wrist_rows(extra_rows),
        )
    )
    duplicated = copy.deepcopy(list(rows))
    duplicated[1] = copy.deepcopy(duplicated[0])
    cases.append(
        (
            "duplicate_row_identity",
            "MARC1PG-F04",
            lambda: validate_wrist_rows(duplicated),
        )
    )
    identity_changed = copy.deepcopy(list(rows))
    identity_changed[-1]["name"] = "sub-45.zip"
    cases.append(
        (
            "participant_or_supplementary_identity_mutation",
            "MARC1PG-F04",
            lambda: validate_wrist_rows(identity_changed),
        )
    )
    wrong_url = copy.deepcopy(list(rows))
    wrong_url[0]["download_url"] = "https://generated.invalid/wrong"
    cases.append(
        ("wrong_downloader_URL", "MARC1PG-F05", lambda: validate_wrist_rows(wrong_url))
    )
    wrong_md5 = copy.deepcopy(list(rows))
    wrong_md5[0]["supplied_md5"] = "0" * 32
    cases.append(
        (
            "supplied_computed_MD5_disagreement",
            "MARC1PG-F05",
            lambda: validate_wrist_rows(wrong_md5),
        )
    )
    wrong_anchor = copy.deepcopy(list(rows))
    wrong_anchor[0]["size"] += 1
    wrong_anchor[-1]["size"] -= 1
    cases.append(
        (
            "sub_01_anchor_mismatch",
            "MARC1PG-F05",
            lambda: validate_wrist_rows(wrong_anchor),
        )
    )
    wrong_total = copy.deepcopy(list(rows))
    wrong_total[-1]["size"] += 1
    cases.append(
        (
            "declared_byte_total_mismatch",
            "MARC1PG-F05",
            lambda: validate_wrist_rows(wrong_total),
        )
    )
    cases.append(
        (
            "private_value_in_public_output",
            "MARC1PG-F06",
            lambda: _walk_public_report({"leak": "sub-01.zip"}),
        )
    )
    with tempfile.TemporaryDirectory() as temporary:
        source_path = Path(temporary) / "forbidden_surface.py"
        source_path.write_text("import socket\n", encoding="utf-8")
        cases.append(
            (
                "forbidden_source_surface",
                "MARC1PG-F06",
                lambda: inspect_source_surface(source_path),
            )
        )
        cases.extend(
            (
                (
                    "output_cap_breach",
                    "MARC1PG-F07",
                    lambda: _check_output_caps(b"x" * (MAX_PUBLIC_OUTPUT_BYTES + 1), b""),
                ),
                (
                    "nondeterministic_replay",
                    "MARC1PG-F07",
                    lambda: _assert_replay("0" * 64, "1" * 64),
                ),
                (
                    "second_generated_closeout_invocation",
                    "MARC1PG-F07",
                    lambda: _assert_new_output_directory(existing_output),
                ),
            )
        )
        results = dict(
            _expect_refusal(name, route, operation)
            for name, route, operation in cases
        )
    if tuple(results) != REFUSAL_CASES:
        raise PaginationRefusal("MARC1PG-F07", "refusal order differs")
    return results


def inspect_source_surface(path: Path | None = None) -> dict[str, Any]:
    """Audit one generated-only module for forbidden operational surfaces."""

    source_path = path or Path(__file__)
    try:
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        raise PaginationRefusal("MARC1PG-F06", "source audit failed") from exc
    forbidden_modules = {
        "aiohttp",
        "http.client",
        "requests",
        "socket",
        "urllib.request",
    }
    imported: list[str] = []
    functions: list[str] = []
    parser_commands: list[str] = []
    forbidden_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "connect",
                "getaddrinfo",
                "request",
                "urlopen",
            }:
                forbidden_calls.append(node.func.attr)
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_parser"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                parser_commands.append(node.args[0].value)
    forbidden_imports = sorted(
        name
        for name in imported
        if name in forbidden_modules
        or any(name.startswith(f"{module}.") for module in forbidden_modules)
    )
    if forbidden_imports or forbidden_calls or "execute" in functions or "execute" in parser_commands:
        raise PaginationRefusal("MARC1PG-F06", "forbidden source surface exists")
    if sorted(parser_commands) != ["inspect", "plan", "qualify"]:
        raise PaginationRefusal("MARC1PG-F06", "command surface differs")
    return {
        "network_client_imports": len(forbidden_imports),
        "DNS_or_transport_calls": len(forbidden_calls),
        "execute_functions": sum(name == "execute" for name in functions),
        "execute_commands": sum(name == "execute" for name in parser_commands),
        "automatic_pagination_interfaces": 0,
        "URL_or_local_source_arguments": 0,
        "private_or_consumed_root_names": 0,
        "payload_signal_target_model_or_score_interfaces": 0,
        "allowed_commands": sorted(parser_commands),
    }


def _base_access_counters() -> dict[str, int]:
    return {
        "generated_fixture_runs": 1,
        "generated_request_validations": 4,
        "generated_response_validations": 4,
        "generated_refusal_checks": 41,
        "committed_contract_and_source_reads": 6,
        "dataset_specific_Figshare_requests": 0,
        "dataset_specific_response_bytes": 0,
        "private_Freewill_manifest_operations": 0,
        "consumed_private_root_operations": 0,
        "payload_requests": 0,
        "payload_bytes": 0,
        "signal_sample_reads": 0,
        "target_or_label_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "prediction_sets": 0,
        "scoring_events": 0,
        "provider_or_language_model_calls": 0,
        "hardware_operations": 0,
        "retry_or_rerun_operations": 0,
        "scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _forbidden_counters_zero(counters: Mapping[str, int]) -> bool:
    allowed_nonzero = {
        "generated_fixture_runs",
        "generated_request_validations",
        "generated_response_validations",
        "generated_refusal_checks",
        "committed_contract_and_source_reads",
    }
    return all(value == 0 for key, value in counters.items() if key not in allowed_nonzero)


def _walk_public_report(value: Any) -> None:
    if isinstance(value, dict):
        for nested in value.values():
            _walk_public_report(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public_report(nested)
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            re.search(r"sub-\d{2}(?:\.zip)?", lowered)
            or "https://" in lowered
            or MD5_RE.fullmatch(lowered)
            or ".codex_work" in lowered
        ):
            raise PaginationRefusal("MARC1PG-F06", "public report contains private value")


def _write_exclusive(path: Path, payload: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            written = 0
            while written < len(payload):
                written += os.write(descriptor, payload[written:])
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise PaginationRefusal("MARC1PG-F07", "exclusive output write failed") from exc


def _report_bytes(report: dict[str, Any], private_bytes: bytes) -> bytes:
    measurements = report["measurements"]
    for _ in range(12):
        payload = _canonical_json_bytes(report)
        public_size = len(payload)
        combined = public_size + len(private_bytes)
        if (
            measurements["public_output_bytes"] == public_size
            and measurements["combined_output_bytes"] == combined
            and measurements["incremental_disk_bytes"] == combined
        ):
            return payload
        measurements["public_output_bytes"] = public_size
        measurements["combined_output_bytes"] = combined
        measurements["incremental_disk_bytes"] = combined
    raise PaginationRefusal("MARC1PG-F07", "public size did not stabilize")


def _assert_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    generated_output_bytes: int,
) -> None:
    if any(os.environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise PaginationRefusal("MARC1PG-F07", "thread environment differs")
    if runtime_seconds > MAX_RUNTIME_SECONDS:
        raise PaginationRefusal("MARC1PG-F07", "runtime exceeds cap")
    if peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise PaginationRefusal("MARC1PG-F07", "peak RSS exceeds cap")
    if generated_input_bytes > MAX_GENERATED_INPUT_BYTES:
        raise PaginationRefusal("MARC1PG-F07", "generated input exceeds cap")
    if generated_output_bytes > MAX_COMBINED_OUTPUT_BYTES:
        raise PaginationRefusal("MARC1PG-F07", "generated output exceeds cap")
    if generated_output_bytes > MAX_INCREMENTAL_DISK_BYTES:
        raise PaginationRefusal("MARC1PG-F07", "incremental disk exceeds cap")


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if set(report) != PUBLIC_REPORT_FIELDS:
        raise PaginationRefusal("MARC1PG-F07", "public report fields differ")
    if (
        report.get("schema_name")
        != "neurodecodekit.marc1_versioned_pagination_qualification"
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("status") != "passed_generated_only_pagination_qualification"
        or report.get("route") != "MARC1PG-G1"
    ):
        raise PaginationRefusal("MARC1PG-F07", "public report identity differs")
    gates = report.get("acceptance_gates")
    if not isinstance(gates, dict) or set(gates) != set(ACCEPTANCE_GATES):
        raise PaginationRefusal("MARC1PG-F07", "acceptance gates differ")
    if not all(value is True for value in gates.values()):
        raise PaginationRefusal("MARC1PG-F07", "acceptance gate failed")
    refusal = report.get("refusal_summary")
    if (
        not isinstance(refusal, dict)
        or refusal.get("passed_count") != 41
        or set(refusal.get("routes", {})) != set(REFUSAL_CASES)
    ):
        raise PaginationRefusal("MARC1PG-F07", "refusal summary differs")
    if not _forbidden_counters_zero(report.get("access_counters", {})):
        raise PaginationRefusal("MARC1PG-F06", "forbidden counter is nonzero")
    _walk_public_report(dict(report))


def qualify_generated_pagination(
    output_dir: str | Path,
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run one generated/mock qualification without a source operation."""

    start = clock()
    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_registered_contract(root)
    if (
        GREEN_CONTRACT_COMMIT != "ccb3ba8a839b3e6fc6844ad867ab0d5d295e20fb"
        or GREEN_CONTRACT_CI_RUN_ID != 31591853349
        or GREEN_CONTRACT_BASE_JOB_ID != 94098410925
        or GREEN_CONTRACT_OPTIONAL_JOB_ID != 94098410868
    ):
        raise PaginationRefusal("MARC1PG-F00", "green contract proof differs")
    request = canonical_request()
    request_summary = validate_mock_request(request)
    selector_contract = selector.load_registered_contract(root)
    freewill_manifest = selector.build_generated_freewill_manifest(
        contract=selector_contract
    )
    wrist_rows = build_generated_wrist_rows()
    signatures: list[dict[str, str]] = []
    transport_rows: list[dict[str, Any]] = []
    selections: list[selector.SelectionResult] = []
    for case_name in ACCEPTED_CASES:
        validate_mock_request(request)
        parsed_rows, transport = parse_mock_response(
            _response_for_case(wrist_rows, case_name)
        )
        wrist = validate_wrist_rows(parsed_rows)
        selection = _selection_from_generated_sources(
            freewill_manifest,
            wrist,
            selector_contract=selector_contract,
        )
        signatures.append(dict(selection.selection_hashes))
        selections.append(selection)
        transport_rows.append(
            {
                "case": case_name,
                "body_bytes": transport["body_bytes"],
                "content_encoding_state": transport["content_encoding_state"],
                "decompression_or_decoding_operations": 0,
            }
        )
    signature_bytes = [_canonical_json_bytes(value) for value in signatures]
    if any(value != signature_bytes[0] for value in signature_bytes[1:]):
        raise PaginationRefusal("MARC1PG-F07", "accepted case selection differs")
    first = selections[0]
    private_bytes = _canonical_json_bytes(first.private_manifest)
    output = Path(output_dir)
    _assert_new_output_directory(output)
    with tempfile.TemporaryDirectory() as temporary:
        existing = Path(temporary) / "existing"
        existing.mkdir()
        refusal_routes = run_refusal_matrix(
            request,
            _response_for_case(wrist_rows, ACCEPTED_CASES[0]),
            wrist_rows,
            existing,
        )
    source_surface = inspect_source_surface()
    counters = _base_access_counters()
    request_bytes = int(request_summary["request_bytes"])
    freewill_bytes = len(_canonical_json_bytes(freewill_manifest))
    wrist_body_bytes = len(_canonical_json_bytes(wrist_rows))
    generated_input_bytes = freewill_bytes + (request_bytes + wrist_body_bytes) * (
        len(ACCEPTED_CASES) + len(REFUSAL_CASES)
    )
    runtime_seconds = clock() - start
    peak_rss_bytes = rss_reader()
    report: dict[str, Any] = {
        "schema_name": "neurodecodekit.marc1_versioned_pagination_qualification",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "passed_generated_only_pagination_qualification",
        "route": "MARC1PG-G1",
        "proof_posture": "generated_only_no_source_or_scientific_value",
        "green_contract_proof": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
            "contract_sha256": CONTRACT_SHA256,
            "both_required_jobs_green": True,
        },
        "request_summary": request_summary,
        "response_summary": {
            "accepted_cases": len(ACCEPTED_CASES),
            "accepted_cases_passed": len(transport_rows),
            "content_encoding_states": sorted(
                {row["content_encoding_state"] for row in transport_rows}
            ),
            "decompression_or_decoding_operations": 0,
            "semantic_hashes_identical": len(set(signature_bytes)) == 1,
        },
        "refusal_summary": {
            "registered_count": len(REFUSAL_CASES),
            "passed_count": len(refusal_routes),
            "routes": refusal_routes,
            "ten_row_default_page_refused": refusal_routes.get(
                "ten_row_partial_page"
            )
            == "MARC1PG-F04",
            "second_page_requests": 0,
            "fallback_requests": 0,
        },
        "inventory_summary": {
            "file_rows": 55,
            "participant_archives": 45,
            "supplementary_rows": 10,
            "declared_record_bytes": 3_683_416_050,
            "sub_01_anchor_passed": True,
            "actual_consumed_live_row_count_available": False,
        },
        "cohort_summary": {
            "selected_subjects_per_axis": first.cohort_summary[
                "selected_subjects_per_axis"
            ],
            "selection_was_target_quality_and_outcome_free": first.cohort_summary[
                "selection_was_target_quality_and_outcome_free"
            ],
            "participant_IDs_public": False,
        },
        "split_summary": dict(first.split_summary),
        "byte_summary": dict(first.byte_summary),
        "selection_hashes": dict(first.selection_hashes),
        "source_surface": source_surface,
        "replay_summary": {
            "accepted_case_selection_hashes_identical": True,
            "response_row_order_independent": True,
            "fixed_measurement_output_replay_required": True,
        },
        "access_counters": counters,
        "measurements": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "generated_input_bytes": generated_input_bytes,
            "public_output_bytes": 0,
            "private_output_bytes": len(private_bytes),
            "combined_output_bytes": 0,
            "incremental_disk_bytes": 0,
            "network_bytes": 0,
            "real_or_private_input_bytes": 0,
        },
        "acceptance_gates": {name: True for name in ACCEPTANCE_GATES},
        "warnings": [
            "All request and response values were generated locally.",
            "The actual consumed live row count remains unavailable.",
            "A generated pass does not establish live inventory compatibility.",
            "Payload acquisition remains ineligible.",
        ],
        "unavailable_fields": [
            "actual_consumed_live_row_count",
            "current_live_version_inventory",
            "neural_signal",
            "target_or_label",
            "model_prediction",
            "scientific_score",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": "A generated harness validates one explicit version-page request and refuses partial-page adaptation.",
            "scientific_claim_not_established": "No dataset body neural signal target model prediction score language decoding or thought-to-text result was produced.",
        },
    }
    report_bytes = _report_bytes(report, private_bytes)
    _check_output_caps(report_bytes, private_bytes)
    _assert_resources(
        runtime_seconds,
        peak_rss_bytes,
        generated_input_bytes,
        len(report_bytes) + len(private_bytes),
    )
    _validate_public_report(report)
    output.mkdir(mode=0o700)
    report_path = output / REPORT_NAME
    private_path = output / PRIVATE_NAME
    _write_exclusive(private_path, private_bytes, 0o600)
    _write_exclusive(report_path, report_bytes, 0o644)
    return QualificationOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=private_path,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=len(report_bytes) + len(private_bytes),
    )


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Inspect one aggregate generated report without opening its private peer."""

    report_path = Path(path)
    if report_path.name != REPORT_NAME:
        raise PaginationRefusal("MARC1PG-F07", "report filename differs")
    try:
        before = os.lstat(report_path)
    except OSError as exc:
        raise PaginationRefusal("MARC1PG-F07", "report is unavailable") from exc
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_PUBLIC_OUTPUT_BYTES:
        raise PaginationRefusal("MARC1PG-F07", "report path or size differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(report_path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or opened.st_size != before.st_size
            ):
                raise PaginationRefusal("MARC1PG-F07", "report changed")
            payload = os.read(descriptor, MAX_PUBLIC_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
        report = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except PaginationRefusal:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PaginationRefusal("MARC1PG-F07", "report parse failed") from exc
    if not isinstance(report, dict):
        raise PaginationRefusal("MARC1PG-F07", "report root differs")
    _validate_public_report(report)
    if report["measurements"]["public_output_bytes"] != len(payload):
        raise PaginationRefusal("MARC1PG-F07", "report byte measurement differs")
    return report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact generated-only plan without a source operation."""

    contract = load_registered_contract(repo_root)
    return {
        "lane_id": LANE_ID,
        "request_query": REQUEST_QUERY,
        "accepted_cases": list(ACCEPTED_CASES),
        "refusal_cases": list(REFUSAL_CASES),
        "acceptance_gates": list(ACCEPTANCE_GATES),
        "candidate_pagination_policy_SHA256": POLICY_SHA256,
        "commands": list(contract["implementation_surface"]["commands"]),
        "network_bytes": 0,
        "real_or_private_input_bytes": 0,
        "payload_signal_target_model_or_score_operations": 0,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_versioned_pagination",
        description="Generated-only MARC1 versioned-pagination qualification.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the zero-access registered plan.")
    qualify = subparsers.add_parser("qualify", help="Run generated qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate report.")
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
        outcome = qualify_generated_pagination(args.output_dir)
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
    except PaginationRefusal as exc:
        print(
            _canonical_json_bytes(
                {"status": "refused", "route": exc.route, "reason": exc.safe_reason}
            ).decode("ascii"),
            end="",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
