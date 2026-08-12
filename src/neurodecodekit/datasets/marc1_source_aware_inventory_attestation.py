"""Generated-only source-aware MARC-1 inventory attestation."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import resource
import stat
import sys
import tempfile
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC1-SA1"
GENERATED_ROUTE = "MARC1SA-G1"
RESULT_ROUTES = {
    "MARC1SA-R1": "historical_match_with_complete_agreeing_MD5",
    "MARC1SA-R2": "historical_match_with_unavailable_or_partial_MD5",
    "MARC1SA-R3": "safe_public_core_with_historical_differences",
    "MARC1SA-R4": "unknown_non_target_extension_selection_blocked",
}
FAILURE_ROUTES = {
    "MARC1SA-F00": "proof_contract_source_or_output_identity_failure",
    "MARC1SA-F01": "transport_redirect_encoding_body_cap_or_timeout_failure",
    "MARC1SA-F02": "malformed_JSON_duplicate_key_or_container_shape_failure",
    "MARC1SA-F03": "target_unsafe_name_invalid_type_duplicate_URL_or_MD5_failure",
    "MARC1SA-F04": "output_privacy_hash_replay_overwrite_cleanup_or_resource_failure",
}

GREEN_CONTRACT_COMMIT = "8f64ccb6dd33df8c81382a9dafd2e84590f50061"
GREEN_CONTRACT_CI_RUN_ID = 31_616_551_270
GREEN_CONTRACT_BASE_JOB_ID = 94_180_673_330
GREEN_CONTRACT_OPTIONAL_JOB_ID = 94_180_673_125
GREEN_RESEARCH_COMMIT = "aa805038cc28c64ad75ddcb0e14768fdcb3cd96e"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_inventory_attestation_contract.v0.json"
)
CONTRACT_SHA256 = "7c405520a3c2039d8ff202f8e34f228627b5b2f5b97cd74e2fe9b42b83de8bec"
RESEARCH_RELATIVE_PATH = Path(
    "registries/marc1_source_aware_inventory_attestation_research.v0.json"
)
RESEARCH_SHA256 = "1125b2b77ff8597ead053319a0ecbf75eefe04ede130e6bf8eac7e943d8b6063"
CONSUMED_RESULT_RELATIVE_PATH = Path(
    "registries/marc1_paginated_live_metadata_failure_result.v0.json"
)
CONSUMED_RESULT_SHA256 = "6e3e488976eb78228f4ffe66d1ac7fc8332ca42a0512d165cbb517be140a2086"

COMMANDS = ("plan", "qualify", "inspect")
PRIVATE_NAME = "marc1_source_aware_inventory.private.v0.json"
REPORT_NAME = "marc1_source_aware_inventory_result.v0.json"
OUTPUT_NAMES = (PRIVATE_NAME, REPORT_NAME)
CORE_FIELDS = frozenset({"id", "name", "size", "is_link_only", "download_url"})
OPTIONAL_FIELDS = frozenset({"supplied_md5", "computed_md5"})
ALLOWED_FIELDS = CORE_FIELDS | OPTIONAL_FIELDS
PREDICATE_FIELDS = (
    "public_core_fields_present_all",
    "known_optional_MD5_keysets_only",
    "unknown_extra_field_rows",
    "row_count",
    "unique_ID_count",
    "unique_name_count",
    "safe_filename_count",
    "valid_downloader_URL_count",
    "non_link_only_count",
    "participant_archive_count",
    "supplementary_row_count",
    "declared_byte_total",
    "historical_row_count_matches",
    "historical_participant_count_matches",
    "historical_supplementary_count_matches",
    "historical_declared_bytes_match",
    "historical_sub01_anchor_matches",
    "supplied_MD5_present_count",
    "computed_MD5_present_count",
    "MD5_pair_agreement_count",
    "target_like_field_count",
)
IDENTITY_DOMAINS = {
    "transport_body_sha256": "neurodecodekit:MARC1-SA1:transport-body:v0",
    "public_core_sha256": "neurodecodekit:MARC1-SA1:public-core:v0",
    "optional_extension_sha256": "neurodecodekit:MARC1-SA1:optional-extension:v0",
    "row_shape_sha256": "neurodecodekit:MARC1-SA1:row-shape:v0",
    "classification_sha256": "neurodecodekit:MARC1-SA1:classification:v0",
    "selection_sha256": "neurodecodekit:MARC1-SA1:selection:v0",
    "predicate_vector_sha256": "neurodecodekit:MARC1-SA1:predicate-vector:v0",
}
SEMANTIC_HASHES = tuple(name for name in IDENTITY_DOMAINS if name != "transport_body_sha256")
FAMILY_ROUTES = {
    "documented_public_core_exact": "MARC1SA-R2",
    "observed_extension_exact": "MARC1SA-R1",
    "partial_optional_extension_exact": "MARC1SA-R2",
    "single_historical_drift": "MARC1SA-R3",
    "multiple_historical_drifts": "MARC1SA-R3",
    "unknown_non_target_extension": "MARC1SA-R4",
}
EXPECTED_SINGLE_DIFFERENCES = ("historical_declared_bytes_match",)
EXPECTED_MULTIPLE_DIFFERENCES = (
    "historical_participant_count_matches",
    "historical_supplementary_count_matches",
    "historical_participant_name_identity_matches",
    "historical_declared_bytes_match",
)
REFUSAL_CASES = (
    "research_commit_drift",
    "research_registry_drift",
    "contract_registry_drift",
    "consumed_result_binding_drift",
    "consumed_executor_import",
    "URL_opener_or_execute_surface",
    "malformed_UTF8",
    "malformed_JSON",
    "duplicate_JSON_key",
    "nonfinite_JSON_constant",
    "non_list_root",
    "non_object_row",
    "target_key_direct",
    "target_key_nested_object",
    "target_key_nested_list",
    "target_key_normalized_variant",
    "missing_id",
    "missing_name",
    "missing_size",
    "missing_is_link_only",
    "missing_download_url",
    "boolean_id",
    "zero_id",
    "boolean_size",
    "zero_size",
    "non_boolean_link_state",
    "link_only_true",
    "name_non_string",
    "empty_name",
    "dot_name",
    "parent_name",
    "slash_name",
    "backslash_name",
    "NUL_name",
    "non_NFC_name",
    "control_character_name",
    "duplicate_file_ID",
    "duplicate_filename",
    "HTTP_download_URL",
    "wrong_download_host",
    "download_path_ID_mismatch",
    "download_URL_query",
    "download_URL_fragment",
    "malformed_supplied_MD5",
    "malformed_computed_MD5",
    "MD5_pair_disagreement",
    "symlink_output_parent",
    "existing_output_directory",
    "combined_output_cap",
    "runtime_cap",
    "peak_RSS_cap",
    "thread_environment_mismatch",
)
ACCEPTANCE_GATES = (
    "green_research_identity_exact",
    "standard_library_only",
    "network_and_URL_opener_absent",
    "command_surface_exactly_plan_qualify_inspect",
    "six_semantic_families_reach_registered_routes",
    "predicate_vector_exactly_21_fields",
    "all_safe_predicates_evaluated_after_structural_gate",
    "five_field_documented_core_passes",
    "seven_field_observed_extension_passes",
    "partial_optional_MD5_routes_R2",
    "unknown_values_excluded_and_selection_blocked_R4",
    "nested_target_like_keys_refuse",
    "single_drift_localization_exact",
    "multi_drift_localization_complete",
    "row_and_key_reorder_preserve_semantic_identity",
    "seven_hash_domains_exact_and_distinct",
    "private_and_public_schemas_disjoint",
    "public_output_contains_no_protected_row_field_or_value",
    "raw_response_bytes_never_persisted",
    "writes_exclusive_no_follow_and_parent_relative",
    "public_inspection_exactly_once",
    "exact_cleanup_removes_two_files_and_directory",
    "all_52_refusals_pass",
    "runtime_RSS_input_output_and_thread_caps_pass",
    "every_real_private_payload_neural_target_model_score_retry_and_claim_counter_zero",
)
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_GENERATED_INPUT_BYTES = 2 * 1024**2
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2
EXPECTED_ROWS = 55
EXPECTED_PARTICIPANTS = 45
EXPECTED_SUPPLEMENTARY = 10
EXPECTED_DECLARED_BYTES = 3_683_416_050
SUB01_ID = 62_570_743
SUB01_BYTES = 33_690_749
SUB01_MD5 = "6b01cf5bd30de0c670d2837d112a17fa"
FROZEN_SUBJECTS = (
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
FIT_RUNS = (1, 2, 3, 4, 5, 6)
HELDOUT_RUNS = (7, 8)
EXPECTED_SUBJECT_NAMES = frozenset(f"sub-{index:02d}.zip" for index in range(1, 46))
PARTICIPANT_RE = re.compile(r"sub-(\d{2})\.zip\Z")
MD5_RE = re.compile(r"[0-9a-f]{32}\Z")
TARGET_KEY_RE = re.compile(
    r"(?:^|_)(?:answer|condition|event|ground_truth|intended_text|label|outcome|"
    r"quality|reference_text|response|sentence|target|trial)(?:_|$)",
    re.I,
)
PRIVATE_VALUE_RE = re.compile(r"(?:sub-\d{2}|https?://|\A[0-9a-f]{32}\Z)", re.I)
PUBLIC_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "proof_posture",
        "family_summary",
        "hashes",
        "resources",
        "access_counters",
        "refusal_summary",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "row",
        "rows",
        "id",
        "file_id",
        "name",
        "filename",
        "url",
        "checksum",
        "md5",
        "subjects",
        "participant_outcomes",
        "public_core_rows",
        "optional_md5_values",
        "private_classification",
        "private_selection",
    }
)


class SourceAwareRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-SA1 route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC1-SA1 refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(slots=True)
class AccessLedger:
    """Record allowed generated operations and prove forbidden work stayed zero."""

    values: dict[str, int] = field(
        default_factory=lambda: {
            "capability_acquisitions": 0,
            "capability_revalidations": 0,
            "repository_reads": 0,
            "repository_bytes": 0,
            "contract_loads": 0,
            "source_audits": 0,
            "generated_fixtures": 0,
            "generated_rows": 0,
            "generated_input_bytes": 0,
            "metadata_parses": 0,
            "attestations": 0,
            "selections": 0,
            "output_directories_created": 0,
            "output_files_created": 0,
            "output_bytes": 0,
            "public_report_inspections": 0,
            "cleanup_file_unlinks": 0,
            "cleanup_directory_removals": 0,
            "dataset_specific_requests": 0,
            "dataset_specific_response_bodies": 0,
            "private_or_consumed_path_operations": 0,
            "participant_archive_requests": 0,
            "payload_bytes": 0,
            "signal_reads": 0,
            "target_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scoring_events": 0,
            "provider_model_calls": 0,
            "hardware_operations": 0,
            "operations_on_other_projects": 0,
            "retries": 0,
            "reruns": 0,
            "claim_upgrades": 0,
        }
    )

    def increment(self, name: str, amount: int = 1) -> None:
        if name not in self.values or isinstance(amount, bool) or amount < 0:
            raise ValueError("invalid access-ledger update")
        self.values[name] += amount

    def before_capability(self) -> dict[str, int]:
        return {
            key: value
            for key, value in self.values.items()
            if key != "capability_acquisitions"
        }


@dataclass(slots=True)
class OutputCapability:
    """Held authority for one absent child under one verified parent."""

    parent_fd: int
    parent_path: str
    parent_device: int
    parent_inode: int
    output_basename: str
    ledger: AccessLedger
    output_fd: int | None = None
    output_created: bool = False
    closed: bool = False

    def __reduce__(self) -> Any:
        raise TypeError("OutputCapability is process-local")

    def close(self) -> None:
        if self.output_fd is not None:
            try:
                os.close(self.output_fd)
            except OSError:
                pass
            self.output_fd = None
        if not self.closed:
            try:
                os.close(self.parent_fd)
            except OSError:
                pass
            self.closed = True


@dataclass(frozen=True)
class Attestation:
    """One source-aware semantic result with a private canonical record."""

    route: str
    predicate_vector: Mapping[str, Any]
    hashes: Mapping[str, str | None]
    historical_differences: tuple[str, ...]
    selection_available: bool
    selection_unavailable_reason: str | None
    private_record: Mapping[str, Any]


@dataclass(frozen=True)
class QualificationOutcome:
    """Aggregate generated evidence retained after exact cleanup."""

    report: Mapping[str, Any]
    report_bytes: bytes
    private_bytes: bytes
    public_sha256: str
    private_sha256: str
    output_path: str
    output_removed: bool
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_temp_parent() -> str:
    return os.path.realpath(tempfile.gettempdir())


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


def _fixture_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=False,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _domain_sha256(name: str, payload: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(IDENTITY_DOMAINS[name].encode("ascii"))
    hasher.update(b"\0")
    hasher.update(payload)
    return hasher.hexdigest()


def _peak_rss_bytes() -> int:
    observed = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return observed if sys.platform == "darwin" else observed * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _read_bound(path: Path, digest: str, size: int | None, ledger: AccessLedger) -> bytes:
    try:
        before = os.lstat(path)
        if not stat.S_ISREG(before.st_mode):
            raise SourceAwareRefusal("MARC1SA-F00", "bound artifact is not regular")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise SourceAwareRefusal("MARC1SA-F00", "bound artifact identity changed")
            payload = b""
            while len(payload) <= 2 * 1024**2:
                chunk = os.read(descriptor, min(65536, 2 * 1024**2 + 1 - len(payload)))
                if not chunk:
                    break
                payload += chunk
        finally:
            os.close(descriptor)
    except SourceAwareRefusal:
        raise
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F00", "bound artifact read failed") from exc
    ledger.increment("repository_reads")
    ledger.increment("repository_bytes", len(payload))
    if (
        len(payload) > 2 * 1024**2
        or (size is not None and len(payload) != size)
        or _sha256_bytes(payload) != digest
    ):
        raise SourceAwareRefusal("MARC1SA-F00", "bound artifact changed")
    return payload


def _proof_json(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceAwareRefusal("MARC1SA-F00", "bound JSON differs") from exc
    if not isinstance(value, dict):
        raise SourceAwareRefusal("MARC1SA-F00", "bound JSON root differs")
    return value


def _validate_green_proof(
    *,
    contract_commit: str = GREEN_CONTRACT_COMMIT,
    research_commit: str = GREEN_RESEARCH_COMMIT,
    CI_run_id: int = GREEN_CONTRACT_CI_RUN_ID,
    base_job_id: int = GREEN_CONTRACT_BASE_JOB_ID,
    optional_job_id: int = GREEN_CONTRACT_OPTIONAL_JOB_ID,
) -> None:
    if (
        contract_commit != GREEN_CONTRACT_COMMIT
        or research_commit != GREEN_RESEARCH_COMMIT
        or CI_run_id != GREEN_CONTRACT_CI_RUN_ID
        or base_job_id != GREEN_CONTRACT_BASE_JOB_ID
        or optional_job_id != GREEN_CONTRACT_OPTIONAL_JOB_ID
    ):
        raise SourceAwareRefusal("MARC1SA-F00", "green proof differs")


def load_registered_contract(
    repo_root: str | Path | None = None, *, ledger: AccessLedger | None = None
) -> dict[str, Any]:
    """Load the exact green contract and its target-free provenance chain."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    selected = ledger if ledger is not None else AccessLedger()
    _validate_green_proof()
    contract = _proof_json(
        _read_bound(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256, 14_048, selected)
    )
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc1_source_aware_inventory_attestation_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_only_requires_green_before_implementation"
        or contract.get("implementation_surface", {}).get("commands") != list(COMMANDS)
        or contract.get("predicate_vector_fields") != list(PREDICATE_FIELDS)
        or contract.get("identity_domains") != IDENTITY_DOMAINS
        or tuple(contract.get("generated_semantic_families", {})) != tuple(FAMILY_ROUTES)
        or tuple(contract.get("acceptance_gates", ())) != ACCEPTANCE_GATES
    ):
        raise SourceAwareRefusal("MARC1SA-F00", "contract identity differs")
    refusal_matrix = contract.get("refusal_matrix", {})
    flattened = tuple(name for values in refusal_matrix.values() for name in values)
    if flattened != REFUSAL_CASES or contract.get("refusal_routes") != FAILURE_ROUTES:
        raise SourceAwareRefusal("MARC1SA-F00", "contract refusal inventory differs")
    proof = contract.get("green_research_proof", {})
    if (
        proof.get("commit") != GREEN_RESEARCH_COMMIT
        or proof.get("both_required_jobs_green") is not True
        or proof.get("research_dataset_specific_requests") != 0
        or proof.get("research_payload_bytes") != 0
        or proof.get("research_scientific_claims") != 0
    ):
        raise SourceAwareRefusal("MARC1SA-F00", "research proof differs")
    bindings = contract.get("artifact_bindings", {})
    for binding in bindings.values():
        _read_bound(
            root / binding["path"],
            binding["sha256"],
            int(binding["bytes"]),
            selected,
        )
    research = _proof_json(
        _read_bound(root / RESEARCH_RELATIVE_PATH, RESEARCH_SHA256, 13_353, selected)
    )
    consumed = research.get("artifact_bindings", {}).get("consumed_result", {})
    if (
        consumed.get("path") != str(CONSUMED_RESULT_RELATIVE_PATH)
        or consumed.get("sha256") != CONSUMED_RESULT_SHA256
        or consumed.get("bytes") != 7_337
    ):
        raise SourceAwareRefusal("MARC1SA-F00", "consumed result binding differs")
    _read_bound(
        root / CONSUMED_RESULT_RELATIVE_PATH,
        CONSUMED_RESULT_SHA256,
        7_337,
        selected,
    )
    selected.increment("contract_loads")
    return contract


def _source_surface_from_text(source: str) -> dict[str, Any]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise SourceAwareRefusal("MARC1SA-F00", "source parse failed") from exc
    imports: set[str] = set()
    functions: set[str] = set()
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
            imports.update(f"{node.module}.{alias.name}" for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)
        elif isinstance(node, ast.Call):
            name = node.func
            if isinstance(name, ast.Name):
                calls.add(name.id)
            elif isinstance(name, ast.Attribute):
                calls.add(name.attr)
    network_roots = {"aiohttp", "http", "requests", "socket", "urllib"}
    heavy_roots = {"mne", "numpy", "scipy", "sklearn", "torch", "zarr"}
    network_imports = sorted(name for name in imports if name.split(".", 1)[0] in network_roots)
    heavy_imports = sorted(name for name in imports if name.split(".", 1)[0] in heavy_roots)
    consumed_imports = sorted(
        name
        for name in imports
        if name == "neurodecodekit.datasets.marc1_paginated_live_metadata"
    )
    opener_calls = sorted(calls & {"urlopen", "build_opener", "Request"})
    execute_functions = sorted(name for name in functions if name.casefold() == "execute")
    if network_imports or heavy_imports or consumed_imports or opener_calls or execute_functions:
        raise SourceAwareRefusal("MARC1SA-F00", "forbidden source surface exists")
    return {
        "commands": list(COMMANDS),
        "network_client_imports": len(network_imports),
        "heavy_optional_imports": len(heavy_imports),
        "consumed_executor_imports": len(consumed_imports),
        "URL_opener_calls": len(opener_calls),
        "execute_functions": len(execute_functions),
        "standard_library_only": True,
    }


def inspect_source_surface(
    path: str | Path | None = None, *, ledger: AccessLedger | None = None
) -> dict[str, Any]:
    source_path = Path(path) if path is not None else Path(__file__)
    try:
        source = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SourceAwareRefusal("MARC1SA-F00", "source audit failed") from exc
    if ledger is not None:
        ledger.increment("source_audits")
    return _source_surface_from_text(source)


def _base_generated_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    participant_total = 0
    for index in range(1, 46):
        name = f"sub-{index:02d}.zip"
        if index == 1:
            file_id = SUB01_ID
            size = SUB01_BYTES
            digest = SUB01_MD5
        else:
            file_id = SUB01_ID + index
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
    remaining = EXPECTED_DECLARED_BYTES - participant_total
    base, remainder = divmod(remaining, EXPECTED_SUPPLEMENTARY)
    for index in range(EXPECTED_SUPPLEMENTARY):
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
    return rows


def build_generated_family(
    name: str, *, reverse_rows: bool = False, reverse_keys: bool = False
) -> list[dict[str, Any]]:
    """Build one of the six frozen semantic families entirely in memory."""

    if name not in FAMILY_ROUTES:
        raise ValueError("unknown generated semantic family")
    rows = _base_generated_rows()
    if name == "documented_public_core_exact":
        for row in rows:
            row.pop("supplied_md5")
            row.pop("computed_md5")
    elif name == "partial_optional_extension_exact":
        for index, row in enumerate(rows):
            if 18 <= index < 36:
                row.pop("computed_md5")
            elif 36 <= index < 45:
                row.pop("supplied_md5")
            elif index >= 45:
                row.pop("supplied_md5")
                row.pop("computed_md5")
    elif name == "single_historical_drift":
        rows[-1]["size"] += 1
    elif name == "multiple_historical_drifts":
        rows[44]["name"] = "supplement-replacement.txt"
        rows[44]["size"] += 7
    elif name == "unknown_non_target_extension":
        rows[0]["storage_location"] = "generated-value-never-retained"
    if reverse_keys:
        rows = [dict(reversed(tuple(row.items()))) for row in rows]
    if reverse_rows:
        rows.reverse()
    return rows


def _reject_target_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if TARGET_KEY_RE.search(normalized):
                raise SourceAwareRefusal("MARC1SA-F03", "target-like key is forbidden")
            _reject_target_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_target_keys(nested)


def _safe_name(value: Any) -> str:
    if not isinstance(value, str):
        raise SourceAwareRefusal("MARC1SA-F03", "filename type differs")
    if (
        not value
        or value in {".", ".."}
        or "/" in value
        or "\\" in value
        or "\x00" in value
        or unicodedata.normalize("NFC", value) != value
        or any(unicodedata.category(character) == "Cc" for character in value)
    ):
        raise SourceAwareRefusal("MARC1SA-F03", "filename is unsafe")
    return value


def _strict_inventory(body: bytes) -> list[dict[str, Any]]:
    try:
        value = json.loads(
            body.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceAwareRefusal("MARC1SA-F02", "strict JSON differs") from exc
    if not isinstance(value, list):
        raise SourceAwareRefusal("MARC1SA-F02", "inventory root is not a list")
    if any(not isinstance(row, dict) for row in value):
        raise SourceAwareRefusal("MARC1SA-F02", "inventory row is not an object")
    _reject_target_keys(value)
    return value


def _validate_row(
    row: Mapping[str, Any], *, file_ids: set[int], names: set[str]
) -> tuple[dict[str, Any], dict[str, str], set[str], str]:
    missing = CORE_FIELDS - set(row)
    if missing:
        raise SourceAwareRefusal("MARC1SA-F03", "required public core field is absent")
    file_id = row["id"]
    size = row["size"]
    link_only = row["is_link_only"]
    if isinstance(file_id, bool) or not isinstance(file_id, int) or file_id <= 0:
        raise SourceAwareRefusal("MARC1SA-F03", "file ID differs")
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise SourceAwareRefusal("MARC1SA-F03", "declared size differs")
    if not isinstance(link_only, bool) or link_only is not False:
        raise SourceAwareRefusal("MARC1SA-F03", "link-only state differs")
    name = _safe_name(row["name"])
    if file_id in file_ids or name in names:
        raise SourceAwareRefusal("MARC1SA-F03", "file identity is duplicated")
    file_ids.add(file_id)
    names.add(name)
    expected_url = f"https://ndownloader.figshare.com/files/{file_id}"
    if not isinstance(row["download_url"], str) or row["download_url"] != expected_url:
        raise SourceAwareRefusal("MARC1SA-F03", "download URL differs")
    optional: dict[str, str] = {}
    for key in OPTIONAL_FIELDS:
        if key not in row:
            continue
        value = row[key]
        if not isinstance(value, str) or MD5_RE.fullmatch(value) is None:
            raise SourceAwareRefusal("MARC1SA-F03", "optional MD5 differs")
        optional[key] = value
    if len(optional) == 2 and optional["supplied_md5"] != optional["computed_md5"]:
        raise SourceAwareRefusal("MARC1SA-F03", "optional MD5 pair disagrees")
    unknown = set(row) - ALLOWED_FIELDS
    core = {key: row[key] for key in sorted(CORE_FIELDS)}
    role = "participant" if PARTICIPANT_RE.fullmatch(name) else "supplementary"
    return core, optional, unknown, role


def attest_inventory(body: bytes, *, ledger: AccessLedger | None = None) -> Attestation:
    """Parse and attest one generated inventory without selecting a payload."""

    rows = _strict_inventory(body)
    if ledger is not None:
        ledger.increment("metadata_parses")
    file_ids: set[int] = set()
    names: set[str] = set()
    private_rows: list[dict[str, Any]] = []
    optional_rows: list[dict[str, Any]] = []
    shapes: list[dict[str, Any]] = []
    classifications: list[dict[str, Any]] = []
    unknown_rows = 0
    participant_names: set[str] = set()
    supplied_count = 0
    computed_count = 0
    agreeing_count = 0
    total_bytes = 0
    sub01_core: Mapping[str, Any] | None = None
    sub01_optional: Mapping[str, Any] = {}
    for row in rows:
        core, optional, unknown, role = _validate_row(row, file_ids=file_ids, names=names)
        file_id = int(core["id"])
        private_rows.append(core)
        optional_rows.append({"id": file_id, **optional})
        shapes.append({"id": file_id, "keys": sorted(row)})
        classifications.append({"id": file_id, "role": role})
        unknown_rows += int(bool(unknown))
        total_bytes += int(core["size"])
        supplied_count += int("supplied_md5" in optional)
        computed_count += int("computed_md5" in optional)
        agreeing_count += int(
            len(optional) == 2
            and optional["supplied_md5"] == optional["computed_md5"]
        )
        if role == "participant":
            participant_names.add(str(core["name"]))
        if core["name"] == "sub-01.zip":
            sub01_core = core
            sub01_optional = optional
    participant_count = len(participant_names)
    supplementary_count = len(rows) - participant_count
    sub01_matches = bool(
        sub01_core
        and sub01_core["id"] == SUB01_ID
        and sub01_core["size"] == SUB01_BYTES
        and all(value == SUB01_MD5 for value in sub01_optional.values())
    )
    predicate_vector: dict[str, Any] = {
        "public_core_fields_present_all": True,
        "known_optional_MD5_keysets_only": unknown_rows == 0,
        "unknown_extra_field_rows": unknown_rows,
        "row_count": len(rows),
        "unique_ID_count": len(file_ids),
        "unique_name_count": len(names),
        "safe_filename_count": len(rows),
        "valid_downloader_URL_count": len(rows),
        "non_link_only_count": len(rows),
        "participant_archive_count": participant_count,
        "supplementary_row_count": supplementary_count,
        "declared_byte_total": total_bytes,
        "historical_row_count_matches": len(rows) == EXPECTED_ROWS,
        "historical_participant_count_matches": participant_count == EXPECTED_PARTICIPANTS,
        "historical_supplementary_count_matches": (
            supplementary_count == EXPECTED_SUPPLEMENTARY
        ),
        "historical_declared_bytes_match": total_bytes == EXPECTED_DECLARED_BYTES,
        "historical_sub01_anchor_matches": sub01_matches,
        "supplied_MD5_present_count": supplied_count,
        "computed_MD5_present_count": computed_count,
        "MD5_pair_agreement_count": agreeing_count,
        "target_like_field_count": 0,
    }
    if tuple(predicate_vector) != PREDICATE_FIELDS:
        raise SourceAwareRefusal("MARC1SA-F04", "predicate vector fields differ")
    participant_identity_matches = participant_names == EXPECTED_SUBJECT_NAMES
    historical_checks = {
        "historical_row_count_matches": predicate_vector["historical_row_count_matches"],
        "historical_participant_count_matches": predicate_vector[
            "historical_participant_count_matches"
        ],
        "historical_supplementary_count_matches": predicate_vector[
            "historical_supplementary_count_matches"
        ],
        "historical_participant_name_identity_matches": participant_identity_matches,
        "historical_declared_bytes_match": predicate_vector[
            "historical_declared_bytes_match"
        ],
        "historical_sub01_anchor_matches": predicate_vector[
            "historical_sub01_anchor_matches"
        ],
    }
    differences = tuple(name for name, passed in historical_checks.items() if not passed)
    selection_available = unknown_rows == 0 and not differences
    if unknown_rows:
        route = "MARC1SA-R4"
        unavailable_reason = "unknown_non_target_schema_extension"
    elif differences:
        route = "MARC1SA-R3"
        unavailable_reason = "historical_inventory_difference"
    elif supplied_count == len(rows) and computed_count == len(rows):
        route = "MARC1SA-R1"
        unavailable_reason = None
    else:
        route = "MARC1SA-R2"
        unavailable_reason = None
    selection: dict[str, Any] | None = None
    if selection_available:
        selection = {
            "subjects": list(FROZEN_SUBJECTS),
            "fit_runs": list(FIT_RUNS),
            "heldout_runs": list(HELDOUT_RUNS),
            "fit_heldout_overlap": 0,
        }
        if ledger is not None:
            ledger.increment("selections")
    canonical_core = sorted(private_rows, key=lambda row: int(row["id"]))
    canonical_optional = sorted(optional_rows, key=lambda row: int(row["id"]))
    canonical_shapes = sorted(shapes, key=lambda row: int(row["id"]))
    canonical_classification = sorted(classifications, key=lambda row: int(row["id"]))
    hashes: dict[str, str | None] = {
        "transport_body_sha256": _domain_sha256("transport_body_sha256", body),
        "public_core_sha256": _domain_sha256(
            "public_core_sha256", _canonical_json_bytes(canonical_core)
        ),
        "optional_extension_sha256": _domain_sha256(
            "optional_extension_sha256", _canonical_json_bytes(canonical_optional)
        ),
        "row_shape_sha256": _domain_sha256(
            "row_shape_sha256", _canonical_json_bytes(canonical_shapes)
        ),
        "classification_sha256": _domain_sha256(
            "classification_sha256", _canonical_json_bytes(canonical_classification)
        ),
        "selection_sha256": (
            _domain_sha256("selection_sha256", _canonical_json_bytes(selection))
            if selection is not None
            else None
        ),
        "predicate_vector_sha256": _domain_sha256(
            "predicate_vector_sha256", _canonical_json_bytes(predicate_vector)
        ),
    }
    private_record = {
        "route": route,
        "public_core_rows": canonical_core,
        "optional_MD5_values": canonical_optional,
        "private_classification": canonical_classification,
        "private_selection": selection,
        "selection_unavailable_reason": unavailable_reason,
        "historical_differences": list(differences),
        "hashes": hashes,
    }
    if ledger is not None:
        ledger.increment("attestations")
    return Attestation(
        route=route,
        predicate_vector=predicate_vector,
        hashes=hashes,
        historical_differences=differences,
        selection_available=selection_available,
        selection_unavailable_reason=unavailable_reason,
        private_record=private_record,
    )


def _semantic_projection(attestation: Attestation) -> dict[str, Any]:
    return {
        "route": attestation.route,
        "predicate_vector": dict(attestation.predicate_vector),
        "hashes": {name: attestation.hashes[name] for name in SEMANTIC_HASHES},
        "historical_differences": list(attestation.historical_differences),
        "selection_available": attestation.selection_available,
        "selection_unavailable_reason": attestation.selection_unavailable_reason,
    }


def _expect_refusal(name: str, operation: Callable[[], Any], route: str) -> str:
    try:
        operation()
    except SourceAwareRefusal as exc:
        if exc.route != route:
            raise AssertionError(f"{name} used {exc.route}, expected {route}") from exc
        return exc.route
    raise AssertionError(f"{name} did not refuse")


def _mutated_rows() -> list[dict[str, Any]]:
    return build_generated_family("observed_extension_exact")


def _attest_mutation(rows: Sequence[Mapping[str, Any]], meter: AccessLedger) -> Attestation:
    body = _fixture_json_bytes([dict(row) for row in rows])
    meter.increment("generated_fixtures")
    meter.increment("generated_rows", len(rows))
    meter.increment("generated_input_bytes", len(body))
    return attest_inventory(body, ledger=meter)


def run_refusal_matrix(
    *, repo_root: str | Path | None = None, ledger: AccessLedger | None = None
) -> dict[str, str]:
    """Exercise all 52 generated refusals without retaining an artifact."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    selected = ledger if ledger is not None else AccessLedger()
    routes: dict[str, str] = {}

    def record(name: str, route: str, operation: Callable[[], Any]) -> None:
        routes[name] = _expect_refusal(name, operation, route)

    record(
        "research_commit_drift",
        "MARC1SA-F00",
        lambda: _validate_green_proof(research_commit="0" * 40),
    )
    record(
        "research_registry_drift",
        "MARC1SA-F00",
        lambda: _read_bound(root / RESEARCH_RELATIVE_PATH, "0" * 64, 13_353, selected),
    )
    record(
        "contract_registry_drift",
        "MARC1SA-F00",
        lambda: _read_bound(root / CONTRACT_RELATIVE_PATH, "0" * 64, 14_048, selected),
    )
    record(
        "consumed_result_binding_drift",
        "MARC1SA-F00",
        lambda: _read_bound(
            root / CONSUMED_RESULT_RELATIVE_PATH, "0" * 64, 7_337, selected
        ),
    )
    record(
        "consumed_executor_import",
        "MARC1SA-F00",
        lambda: _source_surface_from_text(
            "from neurodecodekit.datasets import marc1_paginated_live_metadata\n"
        ),
    )
    record(
        "URL_opener_or_execute_surface",
        "MARC1SA-F00",
        lambda: _source_surface_from_text(
            "import urllib.request\ndef execute():\n    return urllib.request.urlopen('x')\n"
        ),
    )
    raw_bodies = {
        "malformed_UTF8": b"\xff",
        "malformed_JSON": b"[",
        "duplicate_JSON_key": b'[{"id":1,"id":2}]',
        "nonfinite_JSON_constant": b'[{"id":NaN}]',
        "non_list_root": b"{}",
        "non_object_row": b"[1]",
    }
    for name, body in raw_bodies.items():
        selected.increment("generated_fixtures")
        selected.increment("generated_input_bytes", len(body))
        record(
            name,
            "MARC1SA-F02",
            lambda value=body: attest_inventory(value, ledger=selected),
        )
    target_mutations = {
        "target_key_direct": ("target", "forbidden"),
        "target_key_nested_object": ("metadata", {"label": "forbidden"}),
        "target_key_nested_list": ("metadata", [{"sentence": "forbidden"}]),
        "target_key_normalized_variant": ("Ground-Truth", "forbidden"),
    }
    for name, (key, value) in target_mutations.items():
        rows = _mutated_rows()
        rows[0][key] = value
        record(name, "MARC1SA-F03", lambda current=rows: _attest_mutation(current, selected))
    missing_fields = {
        "missing_id": "id",
        "missing_name": "name",
        "missing_size": "size",
        "missing_is_link_only": "is_link_only",
        "missing_download_url": "download_url",
    }
    for name, field_name in missing_fields.items():
        rows = _mutated_rows()
        rows[0].pop(field_name)
        record(name, "MARC1SA-F03", lambda current=rows: _attest_mutation(current, selected))
    typed_values = {
        "boolean_id": ("id", True),
        "zero_id": ("id", 0),
        "boolean_size": ("size", True),
        "zero_size": ("size", 0),
        "non_boolean_link_state": ("is_link_only", 0),
        "link_only_true": ("is_link_only", True),
        "name_non_string": ("name", 1),
    }
    for name, (key, value) in typed_values.items():
        rows = _mutated_rows()
        rows[0][key] = value
        record(name, "MARC1SA-F03", lambda current=rows: _attest_mutation(current, selected))
    filename_values = {
        "empty_name": "",
        "dot_name": ".",
        "parent_name": "..",
        "slash_name": "bad/name.zip",
        "backslash_name": "bad\\name.zip",
        "NUL_name": "bad\x00name.zip",
        "non_NFC_name": "e\u0301.zip",
        "control_character_name": "bad\x01name.zip",
    }
    for name, value in filename_values.items():
        rows = _mutated_rows()
        rows[0]["name"] = value
        record(name, "MARC1SA-F03", lambda current=rows: _attest_mutation(current, selected))
    duplicate_id = _mutated_rows()
    duplicate_id[1]["id"] = duplicate_id[0]["id"]
    duplicate_id[1]["download_url"] = duplicate_id[0]["download_url"]
    record(
        "duplicate_file_ID",
        "MARC1SA-F03",
        lambda: _attest_mutation(duplicate_id, selected),
    )
    duplicate_name = _mutated_rows()
    duplicate_name[1]["name"] = duplicate_name[0]["name"]
    record(
        "duplicate_filename",
        "MARC1SA-F03",
        lambda: _attest_mutation(duplicate_name, selected),
    )
    URL_values = {
        "HTTP_download_URL": "http://ndownloader.figshare.com/files/62570743",
        "wrong_download_host": "https://example.invalid/files/62570743",
        "download_path_ID_mismatch": "https://ndownloader.figshare.com/files/1",
        "download_URL_query": "https://ndownloader.figshare.com/files/62570743?x=1",
        "download_URL_fragment": "https://ndownloader.figshare.com/files/62570743#x",
    }
    for name, value in URL_values.items():
        rows = _mutated_rows()
        rows[0]["download_url"] = value
        record(name, "MARC1SA-F03", lambda current=rows: _attest_mutation(current, selected))
    MD5_values = {
        "malformed_supplied_MD5": ("supplied_md5", "A" * 32),
        "malformed_computed_MD5": ("computed_md5", "x" * 32),
        "MD5_pair_disagreement": ("computed_md5", "0" * 32),
    }
    for name, (key, value) in MD5_values.items():
        rows = _mutated_rows()
        rows[0][key] = value
        record(name, "MARC1SA-F03", lambda current=rows: _attest_mutation(current, selected))
    with tempfile.TemporaryDirectory(dir=_canonical_temp_parent()) as temporary:
        real_parent = Path(temporary) / "real"
        real_parent.mkdir()
        symlink_parent = Path(temporary) / "linked"
        symlink_parent.symlink_to(real_parent, target_is_directory=True)
        record(
            "symlink_output_parent",
            "MARC1SA-F04",
            lambda: acquire_output_capability(symlink_parent / "out", AccessLedger()),
        )
    with tempfile.TemporaryDirectory(dir=_canonical_temp_parent()) as temporary:
        existing = Path(temporary) / "existing"
        existing.mkdir()
        record(
            "existing_output_directory",
            "MARC1SA-F04",
            lambda: acquire_output_capability(existing, AccessLedger()),
        )
    record(
        "combined_output_cap",
        "MARC1SA-F04",
        lambda: _enforce_resources(0.1, 1, 1, MAX_COMBINED_OUTPUT_BYTES + 1, {}),
    )
    record(
        "runtime_cap",
        "MARC1SA-F04",
        lambda: _enforce_resources(MAX_RUNTIME_SECONDS + 1, 1, 1, 1, {}),
    )
    record(
        "peak_RSS_cap",
        "MARC1SA-F04",
        lambda: _enforce_resources(0.1, MAX_PEAK_RSS_BYTES + 1, 1, 1, {}),
    )
    record(
        "thread_environment_mismatch",
        "MARC1SA-F04",
        lambda: _enforce_resources(
            0.1,
            1,
            1,
            1,
            {key: ("2" if key == "OMP_NUM_THREADS" else "1") for key in THREAD_ENV_KEYS},
        ),
    )
    if tuple(routes) != REFUSAL_CASES:
        raise SourceAwareRefusal("MARC1SA-F04", "refusal inventory differs")
    return routes


def _lexical_output(path: str | os.PathLike[str]) -> tuple[str, str, str]:
    try:
        raw = os.fspath(path)
    except TypeError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "output path type differs") from exc
    if not isinstance(raw, str) or not raw or "\x00" in raw or not raw.startswith("/"):
        raise SourceAwareRefusal("MARC1SA-F04", "output path is not absolute")
    if raw == "/" or raw != os.path.normpath(raw):
        raise SourceAwareRefusal("MARC1SA-F04", "output path is not normalized")
    parent, basename = os.path.split(raw)
    if not parent or not basename:
        raise SourceAwareRefusal("MARC1SA-F04", "output basename is empty")
    temporary = _canonical_temp_parent()
    try:
        if os.path.commonpath((os.path.realpath(parent), temporary)) != temporary:
            raise SourceAwareRefusal("MARC1SA-F04", "output is outside temporary space")
    except ValueError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "output path differs") from exc
    return raw, parent, basename


def _lstat_ancestors(parent: str) -> os.stat_result:
    current = "/"
    try:
        root_stat = os.lstat(current)
        if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
            raise SourceAwareRefusal("MARC1SA-F04", "root ancestor differs")
        for component in Path(parent).parts[1:]:
            current = os.path.join(current, component)
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
                raise SourceAwareRefusal("MARC1SA-F04", "output ancestor differs")
        return os.lstat(parent)
    except SourceAwareRefusal:
        raise
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "output ancestor unavailable") from exc


def _require_child_absent(parent_fd: int, basename: str) -> None:
    try:
        os.stat(basename, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "output absence check failed") from exc
    raise SourceAwareRefusal("MARC1SA-F04", "output already exists")


def acquire_output_capability(
    output_dir: str | os.PathLike[str], ledger: AccessLedger
) -> OutputCapability:
    """Acquire output authority before repository or fixture work."""

    if any(ledger.before_capability().values()) or ledger.values["capability_acquisitions"]:
        raise SourceAwareRefusal("MARC1SA-F04", "capability was not first")
    if (
        not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or any(
            function not in os.supports_dir_fd
            for function in (os.open, os.mkdir, os.stat, os.unlink, os.rmdir)
        )
        or os.stat not in os.supports_follow_symlinks
    ):
        raise SourceAwareRefusal("MARC1SA-F04", "no-follow primitives unavailable")
    _, parent, basename = _lexical_output(output_dir)
    before = _lstat_ancestors(parent)
    try:
        parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        opened = os.fstat(parent_fd)
        if (
            (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
            or not stat.S_ISDIR(opened.st_mode)
        ):
            raise SourceAwareRefusal("MARC1SA-F04", "output parent identity changed")
        _require_child_absent(parent_fd, basename)
    except Exception:
        if "parent_fd" in locals():
            os.close(parent_fd)
        raise
    ledger.increment("capability_acquisitions")
    return OutputCapability(
        parent_fd=parent_fd,
        parent_path=parent,
        parent_device=opened.st_dev,
        parent_inode=opened.st_ino,
        output_basename=basename,
        ledger=ledger,
    )


def _revalidate_capability(capability: OutputCapability) -> None:
    if capability.closed:
        raise SourceAwareRefusal("MARC1SA-F04", "output capability is closed")
    try:
        opened = os.fstat(capability.parent_fd)
        named = os.lstat(capability.parent_path)
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "output capability unavailable") from exc
    identity = (capability.parent_device, capability.parent_inode)
    if (
        (opened.st_dev, opened.st_ino) != identity
        or (named.st_dev, named.st_ino) != identity
        or not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(named.st_mode)
    ):
        raise SourceAwareRefusal("MARC1SA-F04", "output capability changed")
    _require_child_absent(capability.parent_fd, capability.output_basename)
    capability.ledger.increment("capability_revalidations")


def _create_output(capability: OutputCapability) -> None:
    _revalidate_capability(capability)
    try:
        os.mkdir(capability.output_basename, 0o700, dir_fd=capability.parent_fd)
        capability.output_created = True
        capability.ledger.increment("output_directories_created")
        descriptor = os.open(
            capability.output_basename,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=capability.parent_fd,
        )
        named = os.stat(
            capability.output_basename,
            dir_fd=capability.parent_fd,
            follow_symlinks=False,
        )
        opened = os.fstat(descriptor)
        if (
            (named.st_dev, named.st_ino) != (opened.st_dev, opened.st_ino)
            or not stat.S_ISDIR(opened.st_mode)
        ):
            os.close(descriptor)
            raise SourceAwareRefusal("MARC1SA-F04", "output identity differs")
        capability.output_fd = descriptor
    except SourceAwareRefusal:
        raise
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "output creation failed") from exc


def _write_relative(capability: OutputCapability, name: str, payload: bytes) -> None:
    if capability.output_fd is None or name not in OUTPUT_NAMES:
        raise SourceAwareRefusal("MARC1SA-F04", "output is not allowlisted")
    if capability.ledger.values["output_bytes"] + len(payload) > MAX_COMBINED_OUTPUT_BYTES:
        raise SourceAwareRefusal("MARC1SA-F04", "combined output cap exceeded")
    try:
        descriptor = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=capability.output_fd,
        )
        try:
            os.fchmod(descriptor, 0o600)
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise OSError("short write")
                offset += written
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "exclusive output write failed") from exc
    capability.ledger.increment("output_files_created")
    capability.ledger.increment("output_bytes", len(payload))


def _read_public_relative(capability: OutputCapability) -> bytes:
    if capability.output_fd is None:
        raise SourceAwareRefusal("MARC1SA-F04", "output descriptor unavailable")
    try:
        descriptor = os.open(REPORT_NAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=capability.output_fd)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_COMBINED_OUTPUT_BYTES:
                raise SourceAwareRefusal("MARC1SA-F04", "public report identity differs")
            payload = os.read(descriptor, MAX_COMBINED_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
    except SourceAwareRefusal:
        raise
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "public report read failed") from exc
    capability.ledger.increment("public_report_inspections")
    return payload


def _cleanup_output(capability: OutputCapability, *, suppress: bool = False) -> None:
    try:
        if capability.output_fd is not None:
            for name in OUTPUT_NAMES:
                try:
                    os.unlink(name, dir_fd=capability.output_fd)
                    capability.ledger.increment("cleanup_file_unlinks")
                except FileNotFoundError:
                    pass
            os.close(capability.output_fd)
            capability.output_fd = None
        if capability.output_created:
            os.rmdir(capability.output_basename, dir_fd=capability.parent_fd)
            capability.output_created = False
            capability.ledger.increment("cleanup_directory_removals")
    except OSError as exc:
        if not suppress:
            raise SourceAwareRefusal("MARC1SA-F04", "generated cleanup failed") from exc


def _walk_public(value: Any, *, key: str | None = None) -> None:
    normalized = key.casefold() if key is not None else None
    if normalized in FORBIDDEN_PUBLIC_KEYS:
        raise SourceAwareRefusal("MARC1SA-F04", "protected public key leaked")
    if isinstance(value, dict):
        for nested_key, nested in value.items():
            _walk_public(nested, key=str(nested_key))
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested, key=key)
    elif isinstance(value, str) and PRIVATE_VALUE_RE.search(value):
        raise SourceAwareRefusal("MARC1SA-F04", "protected public value leaked")


def validate_public_report(report: Mapping[str, Any]) -> None:
    if not isinstance(report, dict) or set(report) != PUBLIC_FIELDS:
        raise SourceAwareRefusal("MARC1SA-F04", "public report fields differ")
    if (
        report.get("schema_name")
        != "neurodecodekit.marc1_source_aware_inventory_attestation_result"
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != GENERATED_ROUTE
    ):
        raise SourceAwareRefusal("MARC1SA-F04", "public report identity differs")
    _walk_public(report)


def _strict_public_bytes(payload: bytes) -> dict[str, Any]:
    try:
        report = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "public report parse failed") from exc
    validate_public_report(report)
    return report


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Inspect only the aggregate public report through one no-follow read."""

    selected = Path(path)
    if selected.name != REPORT_NAME:
        raise SourceAwareRefusal("MARC1SA-F04", "public report basename differs")
    try:
        before = os.lstat(selected)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_COMBINED_OUTPUT_BYTES:
            raise SourceAwareRefusal("MARC1SA-F04", "public report identity differs")
        descriptor = os.open(selected, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise SourceAwareRefusal("MARC1SA-F04", "public report changed")
            payload = os.read(descriptor, MAX_COMBINED_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
    except SourceAwareRefusal:
        raise
    except OSError as exc:
        raise SourceAwareRefusal("MARC1SA-F04", "public report unavailable") from exc
    if len(payload) != before.st_size:
        raise SourceAwareRefusal("MARC1SA-F04", "public report size differs")
    return _strict_public_bytes(payload)


def _forbidden_counters_zero(counters: Mapping[str, int]) -> bool:
    allowed = {
        "capability_acquisitions",
        "capability_revalidations",
        "repository_reads",
        "repository_bytes",
        "contract_loads",
        "source_audits",
        "generated_fixtures",
        "generated_rows",
        "generated_input_bytes",
        "metadata_parses",
        "attestations",
        "selections",
        "output_directories_created",
        "output_files_created",
        "output_bytes",
        "public_report_inspections",
        "cleanup_file_unlinks",
        "cleanup_directory_removals",
    }
    return all(value == 0 for key, value in counters.items() if key not in allowed)


def _enforce_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    output_bytes: int,
    environ: Mapping[str, str],
) -> None:
    if environ and any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise SourceAwareRefusal("MARC1SA-F04", "thread environment differs")
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or generated_input_bytes > MAX_GENERATED_INPUT_BYTES
        or output_bytes > MAX_COMBINED_OUTPUT_BYTES
        or output_bytes > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise SourceAwareRefusal("MARC1SA-F04", "resource cap exceeded")


def _anticipated_counters(ledger: AccessLedger, output_bytes: int) -> dict[str, int]:
    counters = dict(ledger.values)
    counters["capability_revalidations"] += 1
    counters["output_directories_created"] += 1
    counters["output_files_created"] += 2
    counters["output_bytes"] = output_bytes
    counters["public_report_inspections"] += 1
    counters["cleanup_file_unlinks"] += 2
    counters["cleanup_directory_removals"] += 1
    return counters


def _stable_report_bytes(report: dict[str, Any], private_bytes: bytes, ledger: AccessLedger) -> bytes:
    for _ in range(12):
        payload = _canonical_json_bytes(report)
        combined = len(payload) + len(private_bytes)
        counters = _anticipated_counters(ledger, combined)
        resources = report["resources"]
        if (
            resources.get("public_output_bytes") == len(payload)
            and resources.get("private_output_bytes") == len(private_bytes)
            and resources.get("combined_output_bytes") == combined
            and resources.get("incremental_disk_bytes") == combined
            and report.get("access_counters") == counters
        ):
            _enforce_resources(
                float(resources["runtime_seconds"]),
                int(resources["peak_RSS_bytes"]),
                int(resources["generated_input_bytes"]),
                combined,
                {key: "1" for key in THREAD_ENV_KEYS},
            )
            return payload
        resources["public_output_bytes"] = len(payload)
        resources["private_output_bytes"] = len(private_bytes)
        resources["combined_output_bytes"] = combined
        resources["incremental_disk_bytes"] = combined
        report["access_counters"] = counters
    raise SourceAwareRefusal("MARC1SA-F04", "public output size did not stabilize")


def _family_summary(name: str, attestation: Attestation) -> dict[str, Any]:
    return {
        "family": name,
        "route": attestation.route,
        "predicate_vector": dict(attestation.predicate_vector),
        "semantic_hashes": {key: attestation.hashes[key] for key in SEMANTIC_HASHES},
        "selection_available": attestation.selection_available,
        "selection_unavailable_reason": attestation.selection_unavailable_reason,
        "historical_differences": list(attestation.historical_differences),
    }


def qualify_generated_attestation(
    output_dir: str | Path,
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    environ: Mapping[str, str] | None = None,
) -> QualificationOutcome:
    """Run one bounded generated qualification and remove both outputs exactly."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    selected_environ = os.environ if environ is None else environ
    ledger = AccessLedger()
    capability = acquire_output_capability(output_dir, ledger)
    started = clock()
    try:
        _enforce_resources(0.0, 0, 0, 0, selected_environ)
        load_registered_contract(root, ledger=ledger)
        source_surface = inspect_source_surface(ledger=ledger)
        if source_surface["commands"] != list(COMMANDS):
            raise SourceAwareRefusal("MARC1SA-F00", "command surface differs")
        family_attestations: dict[str, Attestation] = {}
        private_families: dict[str, Any] = {}
        replay_hashes: dict[str, str] = {}
        for family, expected_route in FAMILY_ROUTES.items():
            rows = build_generated_family(family)
            body = _fixture_json_bytes(rows)
            ledger.increment("generated_fixtures")
            ledger.increment("generated_rows", len(rows))
            ledger.increment("generated_input_bytes", len(body))
            attestation = attest_inventory(body, ledger=ledger)
            if attestation.route != expected_route:
                raise SourceAwareRefusal("MARC1SA-F04", "semantic family route differs")
            family_attestations[family] = attestation
            private_families[family] = dict(attestation.private_record)
            projection = _semantic_projection(attestation)
            replay_hashes[family] = _sha256_bytes(_canonical_json_bytes(projection))
            for reverse_rows, reverse_keys in ((True, False), (False, True), (True, True)):
                replay_rows = build_generated_family(
                    family,
                    reverse_rows=reverse_rows,
                    reverse_keys=reverse_keys,
                )
                replay_body = _fixture_json_bytes(replay_rows)
                ledger.increment("generated_fixtures")
                ledger.increment("generated_rows", len(replay_rows))
                ledger.increment("generated_input_bytes", len(replay_body))
                replay = attest_inventory(replay_body, ledger=ledger)
                if _semantic_projection(replay) != projection:
                    raise SourceAwareRefusal("MARC1SA-F04", "semantic replay differs")
        partial = family_attestations["partial_optional_extension_exact"].predicate_vector
        unknown = family_attestations["unknown_non_target_extension"]
        if (
            partial["supplied_MD5_present_count"] != 36
            or partial["computed_MD5_present_count"] != 27
            or partial["MD5_pair_agreement_count"] != 18
            or unknown.selection_available
            or "storage_location" in _canonical_json_bytes(unknown.private_record).decode("ascii")
        ):
            raise SourceAwareRefusal("MARC1SA-F04", "optional extension policy differs")
        if (
            family_attestations["single_historical_drift"].historical_differences
            != EXPECTED_SINGLE_DIFFERENCES
            or family_attestations[
                "multiple_historical_drifts"
            ].historical_differences
            != EXPECTED_MULTIPLE_DIFFERENCES
        ):
            raise SourceAwareRefusal("MARC1SA-F04", "historical localization differs")
        refusal_routes = run_refusal_matrix(repo_root=root, ledger=ledger)
        private_manifest = {
            "schema_name": "neurodecodekit.marc1_source_aware_inventory_attestation_private",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "generated_only": True,
            "families": private_families,
            "semantic_replay_hashes": replay_hashes,
            "raw_response_persisted": False,
        }
        private_bytes = _canonical_json_bytes(private_manifest)
        runtime_seconds = round(clock() - started, 9)
        peak_rss_bytes = int(rss_reader())
        family_summary = [
            _family_summary(name, family_attestations[name]) for name in FAMILY_ROUTES
        ]
        report: dict[str, Any] = {
            "schema_name": "neurodecodekit.marc1_source_aware_inventory_attestation_result",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "generated_qualified",
            "route": GENERATED_ROUTE,
            "proof_posture": "generated_only_no_source_or_scientific_value",
            "family_summary": family_summary,
            "hashes": {
                "contract_sha256": CONTRACT_SHA256,
                "research_sha256": RESEARCH_SHA256,
                "consumed_result_sha256": CONSUMED_RESULT_SHA256,
                "private_manifest_sha256": _sha256_bytes(private_bytes),
                "semantic_replay_set_sha256": _sha256_bytes(
                    _canonical_json_bytes(replay_hashes)
                ),
            },
            "resources": {
                "runtime_seconds": runtime_seconds,
                "peak_RSS_bytes": peak_rss_bytes,
                "generated_input_bytes": ledger.values["generated_input_bytes"],
                "public_output_bytes": 0,
                "private_output_bytes": 0,
                "combined_output_bytes": 0,
                "incremental_disk_bytes": 0,
                "network_bytes": 0,
                "payload_bytes": 0,
                "CPU_threads": 1,
                "workers": 1,
                "numerical_jobs": 1,
                "end_to_end_latency_measured": False,
            },
            "access_counters": {},
            "refusal_summary": {
                "required": len(REFUSAL_CASES),
                "passed": len(refusal_routes),
                "routes": refusal_routes,
            },
            "acceptance_gates": {name: True for name in ACCEPTANCE_GATES},
            "warnings": [
                "Generated fixture qualification has no source or scientific value.",
                "Optional provider MD5 provenance never substitutes for acquired-byte SHA-256.",
                "Live metadata archives neural signals targets models and scores remain unavailable.",
            ],
            "unavailable_fields": [
                "live_source_inventory",
                "acquired_payload_SHA256",
                "signal_samples",
                "channels",
                "events",
                "targets",
                "model_predictions",
                "decoding_metrics",
                "end_to_end_latency",
            ],
            "claim_boundary": {
                "same_thought_to_text_path": True,
                "is_pivot": False,
                "engineering_capability_added": (
                    "generated source-aware inventory attestation with aggregate drift localization"
                ),
                "scientific_claim_not_established": (
                    "no neural language-decoding or thought-to-text evidence was produced"
                ),
                "scientific_claim_established": False,
            },
        }
        report_bytes = _stable_report_bytes(report, private_bytes, ledger)
        validate_public_report(report)
        _enforce_resources(
            runtime_seconds,
            peak_rss_bytes,
            ledger.values["generated_input_bytes"],
            len(private_bytes) + len(report_bytes),
            selected_environ,
        )
        _create_output(capability)
        _write_relative(capability, PRIVATE_NAME, private_bytes)
        _write_relative(capability, REPORT_NAME, report_bytes)
        inspected_bytes = _read_public_relative(capability)
        inspected = _strict_public_bytes(inspected_bytes)
        if inspected != report:
            raise SourceAwareRefusal("MARC1SA-F04", "public report replay differs")
        _cleanup_output(capability)
        if ledger.values != report["access_counters"] or not _forbidden_counters_zero(
            ledger.values
        ):
            raise SourceAwareRefusal("MARC1SA-F04", "final access ledger differs")
        output_path = os.fspath(output_dir)
        if os.path.lexists(output_path):
            raise SourceAwareRefusal("MARC1SA-F04", "generated output remains")
        return QualificationOutcome(
            report=report,
            report_bytes=report_bytes,
            private_bytes=private_bytes,
            public_sha256=_sha256_bytes(report_bytes),
            private_sha256=_sha256_bytes(private_bytes),
            output_path=output_path,
            output_removed=True,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            generated_input_bytes=ledger.values["generated_input_bytes"],
            generated_output_bytes=len(private_bytes) + len(report_bytes),
        )
    except Exception:
        _cleanup_output(capability, suppress=True)
        raise
    finally:
        capability.close()


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the zero-access generated implementation plan."""

    contract = load_registered_contract(repo_root)
    return {
        "lane_id": LANE_ID,
        "green_contract": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
        },
        "commands": list(COMMANDS),
        "semantic_families": list(FAMILY_ROUTES),
        "predicate_fields": list(PREDICATE_FIELDS),
        "identity_domains": dict(IDENTITY_DOMAINS),
        "refusal_cases": list(REFUSAL_CASES),
        "acceptance_gates": list(ACCEPTANCE_GATES),
        "resource_caps": dict(contract["resource_caps"]),
        "network_bytes": 0,
        "real_or_private_input_bytes": 0,
        "payload_signal_target_model_or_score_operations": 0,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_source_aware_inventory_attestation",
        description="Generated-only MARC1 source-aware inventory attestation.",
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
            print(
                _canonical_json_bytes(inspect_generated_report(args.report)).decode("ascii"),
                end="",
            )
            return 0
        outcome = qualify_generated_attestation(args.output_dir)
        print(
            _canonical_json_bytes(
                {
                    "status": outcome.report["status"],
                    "route": outcome.report["route"],
                    "output_removed": outcome.output_removed,
                    "generated_input_bytes": outcome.generated_input_bytes,
                    "generated_output_bytes": outcome.generated_output_bytes,
                    "runtime_seconds": outcome.runtime_seconds,
                    "peak_RSS_bytes": outcome.peak_rss_bytes,
                }
            ).decode("ascii"),
            end="",
        )
        return 0
    except SourceAwareRefusal as exc:
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
