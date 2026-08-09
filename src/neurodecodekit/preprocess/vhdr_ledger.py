"""Strict, sibling-blind BrainVision VHDR compatibility ledger support."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any, Callable, Mapping


SCHEMA_VERSION = "0.1.0"
LEDGER_SCHEMA_NAME = "neurodecodekit.loop54_stage_a_vhdr_ledger"
IMPLEMENTATION_SCHEMA_NAME = "neurodecodekit.loop54_stage_a_vhdr_implementation"
CONTRACT_RELATIVE_PATH = Path("registries/loop54_stage_a_vhdr_contract.v0.json")
DECISION_RELATIVE_PATH = Path(
    "registries/loop54_stage_a_recovery_authorization_decision.v1.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/loop54_stage_a_vhdr_implementation.v0.json"
)
CONTRACT_SHA256 = "a0a466d845bff79e9461646f76791a3583fe7c567aeb532b6e951e570411124e"
CONTRACT_BYTES = 13_216
DECISION_SHA256 = "a0bdc88afd5e7205bd2c1410b1361e690174c593466e14ce0d3807be892c2d44"
DECISION_BYTES = 10_718
AUTHORIZATION_COMMIT = "2177b36f56464361bc51b2656406da7575ff1a1f"
AUTHORIZATION_PUSH_CI_RUN_ID = 31_286_428_489
AUTHORIZATION_BASE_PYTHON_JOB_ID = 93_176_025_548
AUTHORIZATION_OPTIONAL_NEURO_JOB_ID = 93_176_025_560
MAX_COMMITTED_ARTIFACT_BYTES = 1024 * 1024
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
REFUSAL_IDS = (
    "L54A-F01_missing_exact_authorization",
    "L54A-F02_dependency_or_source_identity_mismatch",
    "L54A-F03_authorization_or_implementation_not_remote_green",
    "L54A-F04_unexpected_missing_nonregular_or_symlinked_input",
    "L54A-F05_input_size_or_git_blob_mismatch",
    "L54A-F06_preexisting_output",
    "L54A-F07_extra_file_resolution_stat_or_open",
    "L54A-F08_mne_or_heavy_dependency_import",
    "L54A-F09_unsupported_ambiguous_or_conflicting_codepage",
    "L54A-F10_decode_replacement_or_control_character",
    "L54A-F11_missing_duplicate_or_malformed_required_section_or_key",
    "L54A-F12_data_or_marker_reference_not_exact_basename",
    "L54A-F13_channel_count_index_name_or_uniqueness_failure",
    "L54A-F14_resolution_unit_reference_or_sampling_guess",
    "L54A-F15_raw_comment_unknown_path_or_protected_value_output",
    "L54A-F16_vmrk_eeg_mat_target_or_other_participant_access",
    "L54A-F17_cache_split_model_inference_training_scoring_or_selection",
    "L54A-F18_network_download_language_model_rw3_stream_device_or_hardware_operation",
    "L54A-F19_resource_or_output_cap_breach",
    "L54A-F20_overwrite_delete_rename_or_preexisting_path_follow",
    "L54A-F21_rerun_substitution_or_post_result_amendment",
    "L54A-F22_scientific_decoding_realtime_portable_home_or_clinical_overclaim",
)
FORBIDDEN_COUNTER_GROUPS = {
    REFUSAL_IDS[6]: (
        "sibling_path_resolutions",
        "sibling_path_stats",
        "sibling_hash_reads",
        "sibling_content_opens",
    ),
    REFUSAL_IDS[15]: (
        "vmrk_stats_hashes_or_reads",
        "eeg_stats_hashes_or_signal_reads",
        "mat_stats_hashes_or_reads",
        "other_sibling_or_participant_accesses",
        "signal_marker_event_trial_or_target_reads",
    ),
    REFUSAL_IDS[16]: (
        "cache_or_split_operations",
        "feature_extraction_runs",
        "model_or_checkpoint_loads",
        "model_inference_runs",
        "training_or_parameter_update_runs",
        "scoring_or_selection_runs",
    ),
    REFUSAL_IDS[17]: (
        "network_calls",
        "download_operations",
        "language_model_runs",
        "rw3_stream_device_or_hardware_operations",
        "release_operations",
    ),
}
FORMAT_PREAMBLE = "Brain Vision Data Exchange Header File Version "
CHANNEL_KEY_RE = re.compile(r"Ch([1-9][0-9]*)\Z", re.IGNORECASE)
SECTION_RE = re.compile(r"\[([^\r\n]+)\]\Z")
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
LEDGER_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "loop_id",
        "stage_id",
        "status",
        "proof_posture",
        "provenance",
        "declared_header",
        "measurements",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "acceptance_gate_results",
        "claim_boundary",
    }
)
PROVENANCE_FIELDS = frozenset(
    {
        "contract_sha256",
        "authorization_decision_sha256",
        "authorization_commit",
        "authorization_push_CI_run_id",
        "implementation_record_sha256",
        "implementation_commit",
        "implementation_push_CI_run_id",
        "implementation_base_python_job_id",
        "implementation_optional_neuro_readers_job_id",
        "source_identity_algorithm",
        "source_git_blob_sha1",
    }
)
HEADER_FIELDS = frozenset(
    {
        "format_version",
        "strict_codepage",
        "data_file_basename",
        "marker_file_basename",
        "data_format",
        "data_orientation",
        "binary_format",
        "declared_channel_count",
        "sampling_interval_microseconds",
        "sampling_rate_hz",
        "channels",
        "impedance_section_available",
        "filter_declaration_available",
    }
)
CHANNEL_FIELDS = frozenset(
    {
        "source_index",
        "source_name",
        "declared_reference",
        "declared_resolution",
        "declared_unit",
    }
)
MEASUREMENT_FIELDS = frozenset(
    {
        "input_bytes",
        "generated_output_bytes",
        "runtime_seconds_through_output_finalization",
        "peak_RSS_bytes_through_output_finalization",
        "CPU_threads",
        "workers",
        "end_to_end_latency_measured",
    }
)
CLAIM_FIELDS = frozenset(
    {
        "claim_ceiling",
        "engineering_capability",
        "scientific_claim_not_established",
    }
)


class VHDRRefusal(RuntimeError):
    """Fail-closed refusal with a stable, non-sensitive reason identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown Loop 54-A refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class ExecutionEvidence:
    """Offline evidence supplied only after the exact implementation is green."""

    implementation_commit: str
    implementation_push_ci_run_id: int
    implementation_base_python_job_id: int
    implementation_optional_neuro_job_id: int
    registered_execution_ordinal: int = 1
    post_result_amendment: bool = False


@dataclass(frozen=True)
class VHDROutcome:
    """One completed registered or synthetic compatibility-ledger execution."""

    ledger: Mapping[str, Any]
    ledger_path: Path
    summary_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _read_bounded(path: Path, *, expected_sha256: str, expected_bytes: int) -> bytes:
    with path.open("rb") as handle:
        payload = handle.read(MAX_COMMITTED_ARTIFACT_BYTES + 1)
    if len(payload) > MAX_COMMITTED_ARTIFACT_BYTES:
        raise VHDRRefusal(REFUSAL_IDS[1], "committed dependency exceeds its byte cap")
    if len(payload) != expected_bytes or hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise VHDRRefusal(REFUSAL_IDS[1], "committed dependency identity mismatch")
    return payload


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the immutable Loop 54-A preregistration contract."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    payload = _read_bounded(
        root / CONTRACT_RELATIVE_PATH,
        expected_sha256=CONTRACT_SHA256,
        expected_bytes=CONTRACT_BYTES,
    )
    contract = json.loads(payload.decode("utf-8"))
    if (
        contract.get("schema_name") != "neurodecodekit.loop54_stage_a_vhdr_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("stage_id") != "L54-A"
        or contract.get("status") != "preregistered_authorization_pending"
        or tuple(contract.get("refusal_ids", ())) != REFUSAL_IDS
    ):
        raise VHDRRefusal(REFUSAL_IDS[1], "registered contract structure mismatch")
    registered = contract.get("registered_input", {})
    if (
        registered.get("expected_size_bytes") != 11_705
        or registered.get("maximum_read_bytes") != 16_384
        or registered.get("source_identity")
        != "9ab325a0f8523b675ecab1c97e16169143f1f341"
    ):
        raise VHDRRefusal(REFUSAL_IDS[1], "registered source identity mismatch")
    return contract


def load_authorization_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact authorization record without touching the registered data path."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    payload = _read_bounded(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=DECISION_SHA256,
        expected_bytes=DECISION_BYTES,
    )
    decision = json.loads(payload.decode("utf-8"))
    _validate_authorization_decision(decision)
    return decision


def _validate_authorization_decision(decision: Mapping[str, Any]) -> None:
    allowed = decision.get("authorization_after_decision_green", {})
    conditional = decision.get("conditional_registered_real_execution", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.loop54_stage_a_recovery_authorization_decision"
        or not decision.get("effective_only_after_this_record_is_tested_committed_pushed_and_ci_green")
        or not allowed.get("standard_library_parser_implementation_authorized_now")
        or not allowed.get("synthetic_adversarial_qualification_authorized_now")
        or not conditional.get("authorized_by_this_exact_decision")
        or not conditional.get(
            "eligible_only_after_exact_implementation_commit_is_pushed_and_both_CI_jobs_are_green"
        )
        or conditional.get("registered_real_executions") != 1
        or conditional.get("registered_VHDR_content_opens") != 1
        or conditional.get("post_result_rerun_or_amendment") is not False
    ):
        raise VHDRRefusal(REFUSAL_IDS[0], "exact authorization record mismatch")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_implementation_record(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Validate the committed implementation manifest and every source binding."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / IMPLEMENTATION_RELATIVE_PATH
    with path.open("rb") as handle:
        payload = handle.read(MAX_COMMITTED_ARTIFACT_BYTES + 1)
    if len(payload) > MAX_COMMITTED_ARTIFACT_BYTES:
        raise VHDRRefusal(REFUSAL_IDS[1], "implementation record exceeds its byte cap")
    record = json.loads(payload.decode("utf-8"))
    decision = record.get("authorization_binding", {})
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("status")
        != "implemented_synthetic_qualified_pending_exact_commit_remote_green"
        or record.get("contract_binding", {}).get("sha256") != CONTRACT_SHA256
        or decision.get("commit") != AUTHORIZATION_COMMIT
        or decision.get("sha256") != DECISION_SHA256
        or decision.get("push_CI_run_id") != AUTHORIZATION_PUSH_CI_RUN_ID
        or decision.get("base_python_job_id") != AUTHORIZATION_BASE_PYTHON_JOB_ID
        or decision.get("optional_neuro_readers_job_id")
        != AUTHORIZATION_OPTIONAL_NEURO_JOB_ID
    ):
        raise VHDRRefusal(REFUSAL_IDS[1], "implementation record binding mismatch")
    bindings = record.get("implementation_binding")
    if not isinstance(bindings, Mapping) or not bindings:
        raise VHDRRefusal(REFUSAL_IDS[1], "implementation source bindings are missing")
    for binding in bindings.values():
        if not isinstance(binding, Mapping):
            raise VHDRRefusal(REFUSAL_IDS[1], "implementation source binding is malformed")
        relative = binding.get("path")
        expected = binding.get("sha256")
        if (
            not isinstance(relative, str)
            or not isinstance(expected, str)
            or HEX64_RE.fullmatch(expected) is None
        ):
            raise VHDRRefusal(REFUSAL_IDS[1], "implementation source binding is malformed")
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise VHDRRefusal(REFUSAL_IDS[1], "implementation source path is unsafe")
        if _sha256_file(root / candidate) != expected:
            raise VHDRRefusal(REFUSAL_IDS[1], "implementation source hash mismatch")
    return record


def _ascii_codepage_declarations(payload: bytes) -> tuple[str, ...]:
    declarations: list[str] = []
    for raw_line in payload.splitlines():
        candidate = raw_line[3:] if raw_line.startswith(b"\xef\xbb\xbf") else raw_line
        stripped = candidate.strip(b" \t")
        if not stripped.lower().startswith(b"codepage"):
            continue
        if any(byte < 0x20 or byte > 0x7E for byte in stripped):
            raise VHDRRefusal(REFUSAL_IDS[8], "Codepage declaration is not ASCII-safe")
        if stripped.count(b"=") != 1:
            raise VHDRRefusal(REFUSAL_IDS[8], "Codepage declaration is malformed")
        key, value = (part.strip() for part in stripped.split(b"=", 1))
        if key.lower() != b"codepage" or not value:
            raise VHDRRefusal(REFUSAL_IDS[8], "Codepage declaration is malformed")
        declarations.append(value.decode("ascii"))
    return tuple(declarations)


def _detect_and_decode(payload: bytes) -> tuple[str, str, bool]:
    declarations = _ascii_codepage_declarations(payload)
    normalized = {value.casefold().replace("_", "-") for value in declarations}
    if len(normalized) > 1:
        raise VHDRRefusal(REFUSAL_IDS[8], "Codepage declarations conflict")
    has_bom = payload.startswith(b"\xef\xbb\xbf")
    declared = next(iter(normalized), None)
    utf8_values = {"utf-8", "utf8"}
    windows_values = {"windows-1252", "cp1252"}
    if has_bom:
        if declared is not None and declared not in utf8_values:
            raise VHDRRefusal(REFUSAL_IDS[8], "UTF-8 BOM conflicts with Codepage declaration")
        codec = "utf-8-sig"
        canonical = "UTF-8"
    elif declared in utf8_values:
        codec = "utf-8"
        canonical = "UTF-8"
    elif declared in windows_values:
        codec = "cp1252"
        canonical = "windows-1252"
    else:
        raise VHDRRefusal(REFUSAL_IDS[8], "Codepage is missing or unsupported")
    try:
        text = payload.decode(codec, errors="strict")
    except UnicodeDecodeError as exc:
        raise VHDRRefusal(REFUSAL_IDS[9], "strict VHDR decoding failed") from exc
    if "\ufffd" in text:
        raise VHDRRefusal(REFUSAL_IDS[9], "replacement decoding is forbidden")
    for character in text:
        if character in "\r\n":
            continue
        if unicodedata.category(character).startswith("C"):
            raise VHDRRefusal(REFUSAL_IDS[9], "decoded control character is forbidden")
    return text, canonical, has_bom


def _parse_sections(text: str) -> tuple[str, dict[str, dict[str, str]], set[str]]:
    sections: dict[str, dict[str, str]] = {}
    canonical_names: dict[str, str] = {}
    availability_sections: set[str] = set()
    current: str | None = None
    format_version: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(";"):
            continue
        if format_version is None:
            if not stripped.startswith(FORMAT_PREAMBLE):
                raise VHDRRefusal(REFUSAL_IDS[10], "VHDR format preamble is missing")
            version = stripped[len(FORMAT_PREAMBLE) :].strip()
            if not version or any(character.isspace() for character in version):
                raise VHDRRefusal(REFUSAL_IDS[10], "VHDR format version is malformed")
            format_version = version
            continue
        match = SECTION_RE.fullmatch(stripped)
        if match:
            name = match.group(1).strip()
            folded = name.casefold()
            if folded in canonical_names:
                raise VHDRRefusal(REFUSAL_IDS[10], "duplicate VHDR section")
            canonical_names[folded] = name
            sections[name] = {}
            availability_sections.add(folded)
            current = name
            continue
        if current is None:
            raise VHDRRefusal(REFUSAL_IDS[10], "content appeared outside a VHDR section")
        required = next(
            (name for name in REQUIRED_SECTIONS if current.casefold() == name.casefold()),
            None,
        )
        if required is None:
            continue
        if stripped.count("=") != 1:
            raise VHDRRefusal(REFUSAL_IDS[10], "required-section declaration is malformed")
        key, value = (part.strip() for part in stripped.split("=", 1))
        if not key:
            raise VHDRRefusal(REFUSAL_IDS[10], "required-section key is empty")
        folded_keys = {existing.casefold() for existing in sections[current]}
        if key.casefold() in folded_keys:
            raise VHDRRefusal(REFUSAL_IDS[10], "duplicate VHDR key")
        sections[current][key] = value
    if format_version is None:
        raise VHDRRefusal(REFUSAL_IDS[10], "VHDR format preamble is missing")
    for required in REQUIRED_SECTIONS:
        matches = [name for name in sections if name.casefold() == required.casefold()]
        if len(matches) != 1:
            raise VHDRRefusal(REFUSAL_IDS[10], "required VHDR section is missing")
    normalized_sections = {
        required: sections[
            next(name for name in sections if name.casefold() == required.casefold())
        ]
        for required in REQUIRED_SECTIONS
    }
    return format_version, normalized_sections, availability_sections


def _casefold_lookup(values: Mapping[str, str], key: str) -> str:
    matches = [value for candidate, value in values.items() if candidate.casefold() == key.casefold()]
    if len(matches) != 1 or not matches[0]:
        raise VHDRRefusal(REFUSAL_IDS[10], "required VHDR key is missing or empty")
    return matches[0]


def _decode_brainvision_escape(value: str) -> str:
    """Decode the BrainVision ``\\1`` escape used for literal commas."""

    return value.replace(r"\1", ",")


def _safe_declared_field(value: str, *, allow_empty: bool) -> str:
    if not value and not allow_empty:
        raise VHDRRefusal(REFUSAL_IDS[12], "required declared field is empty")
    if (
        value.startswith(("/", "~"))
        or re.match(r"[A-Za-z]:[\\/]", value)
        or "file://" in value.casefold()
    ):
        raise VHDRRefusal(REFUSAL_IDS[14], "absolute or local path value is forbidden")
    return value


def _exact_inert_basename(value: str, expected: str) -> str:
    if (
        value != expected
        or value in {".", ".."}
        or "/" in value
        or "\\" in value
        or "\x00" in value
    ):
        raise VHDRRefusal(REFUSAL_IDS[11], "referenced file is not the exact inert basename")
    return value


def _canonical_decimal(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _parse_channels(values: Mapping[str, str], declared_count: int) -> list[dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for key, value in values.items():
        match = CHANNEL_KEY_RE.fullmatch(key)
        if match is None:
            continue
        index = int(match.group(1))
        if index in rows:
            raise VHDRRefusal(REFUSAL_IDS[12], "duplicate channel index")
        fields = value.split(",")
        if len(fields) != 4:
            raise VHDRRefusal(REFUSAL_IDS[12], "channel declaration must have four fields")
        name, reference, resolution, unit = (
            _decode_brainvision_escape(field.strip()) for field in fields
        )
        name = _safe_declared_field(name, allow_empty=False)
        reference = _safe_declared_field(reference, allow_empty=True)
        resolution = _safe_declared_field(resolution, allow_empty=True)
        unit = _safe_declared_field(unit, allow_empty=True)
        rows[index] = {
            "source_index": index,
            "source_name": name,
            "declared_reference": reference,
            "declared_resolution": resolution,
            "declared_unit": unit,
        }
    expected_indices = list(range(1, declared_count + 1))
    if sorted(rows) != expected_indices:
        raise VHDRRefusal(REFUSAL_IDS[12], "channel table is missing or noncontiguous")
    ordered = [rows[index] for index in expected_indices]
    names = [row["source_name"] for row in ordered]
    if len(set(names)) != len(names):
        raise VHDRRefusal(REFUSAL_IDS[12], "decoded channel names are not unique")
    return ordered


def parse_vhdr_bytes(
    payload: bytes,
    *,
    expected_data_basename: str,
    expected_marker_basename: str,
) -> dict[str, Any]:
    """Strictly parse allowlisted VHDR declarations from one in-memory payload."""

    if not isinstance(payload, bytes) or not payload:
        raise VHDRRefusal(REFUSAL_IDS[10], "VHDR payload is empty or not bytes")
    text, codepage, has_bom = _detect_and_decode(payload)
    format_version, sections, available_sections = _parse_sections(text)
    common = sections["Common Infos"]
    binary = sections["Binary Infos"]
    for key in REQUIRED_COMMON_KEYS:
        _casefold_lookup(common, key)
    for key in REQUIRED_BINARY_KEYS:
        _casefold_lookup(binary, key)
    common_codepages = [
        value for key, value in common.items() if key.casefold() == "codepage"
    ]
    if not has_bom and len(common_codepages) != 1:
        raise VHDRRefusal(REFUSAL_IDS[8], "Codepage must be declared in Common Infos")
    if common_codepages:
        normalized = common_codepages[0].casefold().replace("_", "-")
        expected_values = {"utf-8", "utf8"} if codepage == "UTF-8" else {
            "windows-1252",
            "cp1252",
        }
        if normalized not in expected_values:
            raise VHDRRefusal(REFUSAL_IDS[8], "Common Infos Codepage conflicts")

    data_basename = _exact_inert_basename(
        _casefold_lookup(common, "DataFile"), expected_data_basename
    )
    marker_basename = _exact_inert_basename(
        _casefold_lookup(common, "MarkerFile"), expected_marker_basename
    )
    try:
        declared_count = int(_casefold_lookup(common, "NumberOfChannels"), 10)
    except ValueError as exc:
        raise VHDRRefusal(REFUSAL_IDS[12], "declared channel count is malformed") from exc
    if declared_count <= 0:
        raise VHDRRefusal(REFUSAL_IDS[12], "declared channel count must be positive")
    try:
        sampling_interval = Decimal(_casefold_lookup(common, "SamplingInterval"))
    except InvalidOperation as exc:
        raise VHDRRefusal(REFUSAL_IDS[13], "sampling interval is malformed") from exc
    if not sampling_interval.is_finite() or sampling_interval <= 0:
        raise VHDRRefusal(REFUSAL_IDS[13], "sampling interval must be finite and positive")
    with localcontext() as context:
        context.prec = 28
        sampling_rate = Decimal(1_000_000) / sampling_interval
    channels = _parse_channels(sections["Channel Infos"], declared_count)
    return {
        "format_version": format_version,
        "strict_codepage": codepage,
        "data_file_basename": data_basename,
        "marker_file_basename": marker_basename,
        "data_format": _safe_declared_field(
            _casefold_lookup(common, "DataFormat"), allow_empty=False
        ),
        "data_orientation": _safe_declared_field(
            _casefold_lookup(common, "DataOrientation"), allow_empty=False
        ),
        "binary_format": _safe_declared_field(
            _casefold_lookup(binary, "BinaryFormat"), allow_empty=False
        ),
        "declared_channel_count": declared_count,
        "sampling_interval_microseconds": _canonical_decimal(sampling_interval),
        "sampling_rate_hz": _canonical_decimal(sampling_rate),
        "channels": channels,
        "impedance_section_available": any(
            "impedance" in name for name in available_sections
        ),
        "filter_declaration_available": any("filter" in name for name in available_sections),
    }


def make_synthetic_vhdr(
    *,
    codepage: str = "UTF-8",
    data_basename: str = "synthetic.eeg",
    marker_basename: str = "synthetic.vmrk",
    include_bom: bool = False,
) -> bytes:
    """Build a deterministic target-free VHDR fixture for parser qualification."""

    lines = [
        "Brain Vision Data Exchange Header File Version 1.0",
        "; synthetic comment that must never appear in output",
        "[Common Infos]",
        f"Codepage={codepage}",
        f"DataFile={data_basename}",
        f"MarkerFile={marker_basename}",
        "DataFormat=BINARY",
        "DataOrientation=MULTIPLEXED",
        "NumberOfChannels=4",
        "SamplingInterval=2000",
        "[Binary Infos]",
        "BinaryFormat=IEEE_FLOAT_32",
        "[Channel Infos]",
        "Ch1=Fz,,0.1,\N{MICRO SIGN}V",
        "Ch2=C\\1mid,REF,0.1,\N{MICRO SIGN}V",
        "Ch3=Pz,,0.1,\N{MICRO SIGN}V",
        "Ch4=Oz,,0.1,\N{MICRO SIGN}V",
        "[Comment]",
        "ProtectedSyntheticValue=must-not-emit",
        "[Impedance [kOhm]]",
        "Ch1=5",
    ]
    text = "\r\n".join(lines) + "\r\n"
    normalized = codepage.casefold().replace("_", "-")
    encoding = "cp1252" if normalized in {"windows-1252", "cp1252"} else "utf-8"
    payload = text.encode(encoding)
    return b"\xef\xbb\xbf" + payload if include_bom else payload


def git_blob_sha1(payload: bytes) -> str:
    """Return the Git blob object identifier for one byte payload."""

    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


def _peak_rss_bytes() -> int:
    import resource

    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise VHDRRefusal(REFUSAL_IDS[18], "one-thread environment is required")


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise VHDRRefusal(REFUSAL_IDS[1], "registered relative path is unsafe")
    return path


def _lstat_optional(
    path: Path,
    *,
    refusal_id: str = REFUSAL_IDS[3],
) -> os.stat_result | None:
    try:
        return os.lstat(path)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise VHDRRefusal(refusal_id, "filesystem metadata validation failed") from exc


def _assert_no_symlink_components(root: Path, path: Path, *, require_leaf: bool) -> os.stat_result | None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise VHDRRefusal(REFUSAL_IDS[3], "registered path escapes the workspace") from exc
    root_stat = _lstat_optional(root)
    if root_stat is None or stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise VHDRRefusal(REFUSAL_IDS[3], "workspace root is missing or unsafe")
    current = root
    last_stat: os.stat_result | None = root_stat
    for index, part in enumerate(relative.parts):
        current = current / part
        last_stat = _lstat_optional(current)
        is_leaf = index == len(relative.parts) - 1
        if last_stat is None:
            if require_leaf or not is_leaf:
                raise VHDRRefusal(REFUSAL_IDS[3], "registered path component is missing")
            return None
        if stat.S_ISLNK(last_stat.st_mode):
            raise VHDRRefusal(REFUSAL_IDS[3], "registered path component is symlinked")
        if not is_leaf and not stat.S_ISDIR(last_stat.st_mode):
            raise VHDRRefusal(REFUSAL_IDS[3], "registered parent is not a directory")
    return last_stat


def _preflight_output(root: Path, output_root: Path) -> None:
    try:
        relative = output_root.relative_to(root)
    except ValueError as exc:
        raise VHDRRefusal(REFUSAL_IDS[19], "output path escapes the workspace") from exc
    current = root
    root_stat = _lstat_optional(root, refusal_id=REFUSAL_IDS[19])
    if root_stat is None or stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise VHDRRefusal(REFUSAL_IDS[19], "workspace root is unsafe")
    for index, part in enumerate(relative.parts):
        current = current / part
        observed = _lstat_optional(current, refusal_id=REFUSAL_IDS[19])
        if observed is None:
            return
        if stat.S_ISLNK(observed.st_mode):
            raise VHDRRefusal(REFUSAL_IDS[19], "output path component is symlinked")
        if index == len(relative.parts) - 1:
            raise VHDRRefusal(REFUSAL_IDS[5], "registered output already exists")
        if not stat.S_ISDIR(observed.st_mode):
            raise VHDRRefusal(REFUSAL_IDS[19], "output parent is not a directory")


def _mkdir_missing_output_components(root: Path, output_root: Path) -> None:
    current = root
    for part in output_root.relative_to(root).parts:
        current = current / part
        observed = _lstat_optional(current, refusal_id=REFUSAL_IDS[19])
        if observed is None:
            try:
                os.mkdir(current, mode=0o700)
            except OSError as exc:
                raise VHDRRefusal(
                    REFUSAL_IDS[19], "exclusive output directory creation failed"
                ) from exc
            continue
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
            raise VHDRRefusal(REFUSAL_IDS[19], "output directory creation was unsafe")


def _exclusive_write(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise VHDRRefusal(REFUSAL_IDS[5], "registered output already exists") from exc
    except OSError as exc:
        raise VHDRRefusal(REFUSAL_IDS[19], "exclusive output creation failed") from exc
    try:
        try:
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise OSError("exclusive output write made no progress")
                offset += written
            os.fsync(descriptor)
        except OSError as exc:
            raise VHDRRefusal(REFUSAL_IDS[19], "exclusive output commit failed") from exc
    finally:
        os.close(descriptor)


def _base_access_counters() -> dict[str, int]:
    return {
        "registered_real_executions": 1,
        "local_S20_registered_path_validations": 1,
        "vhdr_content_opens": 1,
        "vhdr_hash_reads": 1,
        "vhdr_parse_runs": 1,
        "output_ledger_writes": 1,
        "output_summary_writes": 1,
        "sibling_path_resolutions": 0,
        "sibling_path_stats": 0,
        "sibling_hash_reads": 0,
        "sibling_content_opens": 0,
        "vmrk_stats_hashes_or_reads": 0,
        "eeg_stats_hashes_or_signal_reads": 0,
        "mat_stats_hashes_or_reads": 0,
        "other_sibling_or_participant_accesses": 0,
        "signal_marker_event_trial_or_target_reads": 0,
        "cache_or_split_operations": 0,
        "feature_extraction_runs": 0,
        "model_or_checkpoint_loads": 0,
        "model_inference_runs": 0,
        "training_or_parameter_update_runs": 0,
        "scoring_or_selection_runs": 0,
        "network_calls": 0,
        "download_operations": 0,
        "language_model_runs": 0,
        "rw3_stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "reruns": 0,
        "source_test_or_session_2_signal_reads": 0,
    }


def _assert_forbidden_counters_zero(counters: Mapping[str, int]) -> None:
    for refusal_id, keys in FORBIDDEN_COUNTER_GROUPS.items():
        if any(counters.get(key) != 0 for key in keys):
            raise VHDRRefusal(refusal_id, "a forbidden access or operation counter is nonzero")


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, nested in pairs:
        if key in value:
            raise ValueError("duplicate JSON key is forbidden")
        value[key] = nested
    return value


def _render_summary(ledger: Mapping[str, Any]) -> bytes:
    header = ledger["declared_header"]
    measurements = ledger["measurements"]
    lines = [
        "# Loop 54-A VHDR compatibility ledger",
        "",
        f"- Status: `{ledger['status']}`",
        f"- Claim ceiling: `{ledger['claim_boundary']['claim_ceiling']}`",
        f"- Strict codepage: `{header['strict_codepage']}`",
        f"- Declared channels: `{header['declared_channel_count']}`",
        f"- Declared sampling rate: `{header['sampling_rate_hz']} Hz`",
        f"- Input bytes: `{measurements['input_bytes']}`",
        f"- Generated output bytes: `{measurements['generated_output_bytes']}`",
        f"- Runtime through finalization: `{measurements['runtime_seconds_through_output_finalization']}` seconds",
        f"- Peak RSS through finalization: `{measurements['peak_RSS_bytes_through_output_finalization']}` bytes",
        "- Sibling path stats/opens: `0/0`",
        "- Signal, marker, target, model, training, inference, and scoring runs: `0`",
        "",
        "This result establishes only strict declared-header compatibility under L54-Q2.",
        "It does not establish signal quality, trial validity, neural advantage, or decoding accuracy.",
        "",
    ]
    return "\n".join(lines).encode("ascii")


def _finalize_output_bytes(ledger: dict[str, Any]) -> tuple[bytes, bytes]:
    previous = -1
    for _ in range(8):
        json_bytes = _canonical_json_bytes(ledger)
        summary_bytes = _render_summary(ledger)
        combined = len(json_bytes) + len(summary_bytes)
        ledger["measurements"]["generated_output_bytes"] = combined
        if combined == previous:
            return json_bytes, summary_bytes
        previous = combined
    raise VHDRRefusal(REFUSAL_IDS[18], "output byte accounting did not converge")


def _build_ledger(
    *,
    parsed: Mapping[str, Any],
    contract: Mapping[str, Any],
    contract_sha256: str,
    decision_sha256: str,
    implementation_record_sha256: str,
    implementation_commit: str,
    evidence: ExecutionEvidence,
    source_sha1: str,
    input_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
    counters: Mapping[str, int],
) -> dict[str, Any]:
    gates = {name: True for name in contract["acceptance_gates"]}
    return {
        "schema_name": LEDGER_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "loop_id": 54,
        "stage_id": "L54-A",
        "status": "passed",
        "proof_posture": "target_free_strict_declared_header_compatibility_only",
        "provenance": {
            "contract_sha256": contract_sha256,
            "authorization_decision_sha256": decision_sha256,
            "authorization_commit": AUTHORIZATION_COMMIT,
            "authorization_push_CI_run_id": AUTHORIZATION_PUSH_CI_RUN_ID,
            "implementation_record_sha256": implementation_record_sha256,
            "implementation_commit": implementation_commit,
            "implementation_push_CI_run_id": evidence.implementation_push_ci_run_id,
            "implementation_base_python_job_id": evidence.implementation_base_python_job_id,
            "implementation_optional_neuro_readers_job_id": (
                evidence.implementation_optional_neuro_job_id
            ),
            "source_identity_algorithm": "git_blob_sha1",
            "source_git_blob_sha1": source_sha1,
        },
        "declared_header": dict(parsed),
        "measurements": {
            "input_bytes": input_bytes,
            "generated_output_bytes": 0,
            "runtime_seconds_through_output_finalization": runtime_seconds,
            "peak_RSS_bytes_through_output_finalization": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "end_to_end_latency_measured": False,
        },
        "access_counters": dict(counters),
        "warnings": list(contract["warnings"]),
        "unavailable_fields": list(contract["forced_unavailable_fields"]),
        "acceptance_gate_results": gates,
        "claim_boundary": {
            "claim_ceiling": "L54-Q2_declared_header_compatibility",
            "engineering_capability": (
                "The exact registered VHDR was strictly decoded and its allowlisted declared "
                "recording and channel fields were validated without sibling access."
            ),
            "scientific_claim_not_established": (
                "No EEG signal quality, event or trial validity, target correctness, neural "
                "advantage, decoding accuracy, generalization, end-to-end latency, portable "
                "hardware, home-use, or clinical result was established."
            ),
        },
    }


def _validate_safe_ledger(ledger: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    def exact_keys(value: Any, expected: frozenset[str], label: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping) or set(value) != expected:
            raise VHDRRefusal(REFUSAL_IDS[14], f"ledger {label} fields changed")
        return value

    exact_keys(ledger, LEDGER_FIELDS, "top-level")
    if ledger.get("schema_name") != LEDGER_SCHEMA_NAME or ledger.get("status") != "passed":
        raise VHDRRefusal(REFUSAL_IDS[14], "ledger schema or status mismatch")
    if (
        ledger.get("schema_version") != SCHEMA_VERSION
        or ledger.get("loop_id") != 54
        or ledger.get("stage_id") != "L54-A"
        or ledger.get("proof_posture")
        != "target_free_strict_declared_header_compatibility_only"
    ):
        raise VHDRRefusal(REFUSAL_IDS[14], "ledger identity changed")
    provenance = exact_keys(ledger.get("provenance"), PROVENANCE_FIELDS, "provenance")
    registered = contract["registered_input"]
    if (
        provenance.get("contract_sha256") != CONTRACT_SHA256
        or provenance.get("authorization_decision_sha256") != DECISION_SHA256
        or provenance.get("authorization_commit") != AUTHORIZATION_COMMIT
        or provenance.get("authorization_push_CI_run_id") != AUTHORIZATION_PUSH_CI_RUN_ID
        or provenance.get("source_identity_algorithm") != "git_blob_sha1"
        or provenance.get("source_git_blob_sha1") != registered["source_identity"]
        or HEX64_RE.fullmatch(str(provenance.get("implementation_record_sha256"))) is None
        or HEX40_RE.fullmatch(str(provenance.get("implementation_commit"))) is None
    ):
        raise VHDRRefusal(REFUSAL_IDS[1], "ledger provenance identity changed")
    for key in (
        "implementation_push_CI_run_id",
        "implementation_base_python_job_id",
        "implementation_optional_neuro_readers_job_id",
    ):
        if not isinstance(provenance.get(key), int) or provenance[key] <= 0:
            raise VHDRRefusal(REFUSAL_IDS[2], "ledger green evidence is malformed")

    header = exact_keys(ledger.get("declared_header"), HEADER_FIELDS, "header")
    if (
        header.get("strict_codepage") not in {"UTF-8", "windows-1252"}
        or header.get("data_file_basename") != registered["expected_data_basename"]
        or header.get("marker_file_basename") != registered["expected_marker_basename"]
        or not isinstance(header.get("declared_channel_count"), int)
        or header["declared_channel_count"] <= 0
        or not isinstance(header.get("impedance_section_available"), bool)
        or not isinstance(header.get("filter_declaration_available"), bool)
    ):
        raise VHDRRefusal(REFUSAL_IDS[14], "ledger declared-header identity changed")
    for key in ("format_version", "data_format", "data_orientation", "binary_format"):
        if not isinstance(header.get(key), str):
            raise VHDRRefusal(REFUSAL_IDS[14], "ledger declared-header type changed")
        _safe_declared_field(header[key], allow_empty=False)
    channels = header.get("channels")
    if not isinstance(channels, list) or len(channels) != header["declared_channel_count"]:
        raise VHDRRefusal(REFUSAL_IDS[12], "ledger channel count changed")
    for expected_index, row in enumerate(channels, start=1):
        channel = exact_keys(row, CHANNEL_FIELDS, "channel")
        if channel.get("source_index") != expected_index or not channel.get("source_name"):
            raise VHDRRefusal(REFUSAL_IDS[12], "ledger channel identity changed")
        for key in CHANNEL_FIELDS - {"source_index"}:
            if not isinstance(channel.get(key), str):
                raise VHDRRefusal(REFUSAL_IDS[14], "ledger channel value type changed")
            _safe_declared_field(channel[key], allow_empty=key != "source_name")
    if len({row["source_name"] for row in channels}) != len(channels):
        raise VHDRRefusal(REFUSAL_IDS[12], "ledger channel names are not unique")
    try:
        interval = Decimal(str(header["sampling_interval_microseconds"]))
        rate = Decimal(str(header["sampling_rate_hz"]))
    except InvalidOperation as exc:
        raise VHDRRefusal(REFUSAL_IDS[13], "ledger sampling values are malformed") from exc
    if not interval.is_finite() or interval <= 0 or not rate.is_finite() or rate <= 0:
        raise VHDRRefusal(REFUSAL_IDS[13], "ledger sampling values are invalid")
    with localcontext() as context:
        context.prec = 28
        if rate != Decimal(1_000_000) / interval:
            raise VHDRRefusal(REFUSAL_IDS[13], "ledger sampling derivation changed")

    measurements = exact_keys(
        ledger.get("measurements"), MEASUREMENT_FIELDS, "measurements"
    )
    if (
        measurements.get("input_bytes") != registered["expected_size_bytes"]
        or not isinstance(measurements.get("generated_output_bytes"), int)
        or measurements["generated_output_bytes"] <= 0
        or measurements["generated_output_bytes"]
        > contract["output_contract"]["maximum_combined_generated_output_bytes"]
        or measurements.get("CPU_threads") != 1
        or measurements.get("workers") != 1
        or measurements.get("end_to_end_latency_measured") is not False
        or not isinstance(
            measurements.get("runtime_seconds_through_output_finalization"), (int, float)
        )
        or not math.isfinite(measurements["runtime_seconds_through_output_finalization"])
        or measurements["runtime_seconds_through_output_finalization"] < 0
        or not isinstance(
            measurements.get("peak_RSS_bytes_through_output_finalization"), int
        )
        or measurements["peak_RSS_bytes_through_output_finalization"] < 0
    ):
        raise VHDRRefusal(REFUSAL_IDS[18], "ledger measurements changed")
    counters = exact_keys(
        ledger.get("access_counters"), frozenset(_base_access_counters()), "access counters"
    )
    if any(not isinstance(value, int) or value < 0 for value in counters.values()):
        raise VHDRRefusal(REFUSAL_IDS[14], "ledger access counter type changed")
    exact_keys(ledger.get("claim_boundary"), CLAIM_FIELDS, "claim boundary")
    encoded = _canonical_json_bytes(ledger)
    lowered = encoded.lower()
    for forbidden in (
        b"raw_vhdr",
        b"raw_header",
        b"comment_content",
        b"target_text_value",
        b"marker_description_value",
        b"absolute_local_path",
    ):
        if forbidden in lowered:
            raise VHDRRefusal(REFUSAL_IDS[14], "ledger contains a forbidden field")
    if ledger.get("unavailable_fields") != contract.get("forced_unavailable_fields"):
        raise VHDRRefusal(REFUSAL_IDS[13], "forced-unavailable fields changed")
    if ledger.get("warnings") != contract.get("warnings"):
        raise VHDRRefusal(REFUSAL_IDS[14], "registered warnings changed")
    if set(ledger.get("acceptance_gate_results", {})) != set(contract["acceptance_gates"]):
        raise VHDRRefusal(REFUSAL_IDS[21], "acceptance-gate set changed")
    if not all(ledger["acceptance_gate_results"].values()):
        raise VHDRRefusal(REFUSAL_IDS[21], "an acceptance gate is false")
    if ledger.get("claim_boundary", {}).get("claim_ceiling") != (
        "L54-Q2_declared_header_compatibility"
    ):
        raise VHDRRefusal(REFUSAL_IDS[21], "claim ceiling exceeds L54-Q2")
    _assert_forbidden_counters_zero(ledger["access_counters"])


def _verify_execution_evidence(root: Path, evidence: ExecutionEvidence) -> None:
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or min(
            evidence.implementation_push_ci_run_id,
            evidence.implementation_base_python_job_id,
            evidence.implementation_optional_neuro_job_id,
        )
        <= 0
    ):
        raise VHDRRefusal(REFUSAL_IDS[2], "implementation green evidence is malformed")

    def git(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    head = git("rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.implementation_commit:
        raise VHDRRefusal(REFUSAL_IDS[2], "current HEAD does not match implementation evidence")
    tracked = git("status", "--porcelain", "--untracked-files=no")
    if tracked.returncode or tracked.stdout.strip():
        raise VHDRRefusal(REFUSAL_IDS[2], "tracked worktree must be clean during execution")
    ancestor = git("merge-base", "--is-ancestor", AUTHORIZATION_COMMIT, "HEAD")
    if ancestor.returncode:
        raise VHDRRefusal(REFUSAL_IDS[0], "authorization commit is not an ancestor")


def _verify_one_shot_evidence(evidence: ExecutionEvidence) -> None:
    if evidence.registered_execution_ordinal != 1 or evidence.post_result_amendment:
        raise VHDRRefusal(REFUSAL_IDS[20], "rerun or post-result amendment is forbidden")


def run_vhdr_ledger(
    *,
    contract: Mapping[str, Any],
    contract_sha256: str,
    decision_sha256: str,
    implementation_record_sha256: str,
    evidence: ExecutionEvidence,
    workspace_root: str | Path,
    environ: Mapping[str, str],
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    verify_evidence: Callable[[Path, ExecutionEvidence], None] | None = None,
) -> VHDROutcome:
    """Run one bounded VHDR ledger pass against a supplied frozen contract."""

    root = Path(workspace_root)
    _verify_one_shot_evidence(evidence)
    if verify_evidence is not None:
        verify_evidence(root, evidence)
    _check_thread_environment(environ)
    started = clock()
    initial_rss = rss_reader()
    caps = contract["resource_caps"]
    if initial_rss > int(caps["peak_rss_bytes"]):
        raise VHDRRefusal(REFUSAL_IDS[18], "initial peak RSS exceeds the cap")
    heavy_before = HEAVY_MODULE_ROOTS.intersection(sys.modules)
    registered = contract["registered_input"]
    output = contract["output_contract"]
    output_root = root / _safe_relative_path(output["output_root"])
    _preflight_output(root, output_root)

    input_root = root / _safe_relative_path(registered["payload_root_relative_path"])
    input_path = input_root / _safe_relative_path(registered["vhdr_relative_path"])
    observed = _assert_no_symlink_components(root, input_path, require_leaf=True)
    if observed is None or not stat.S_ISREG(observed.st_mode):
        raise VHDRRefusal(REFUSAL_IDS[3], "registered VHDR is not a regular file")
    if observed.st_size != int(registered["expected_size_bytes"]):
        raise VHDRRefusal(REFUSAL_IDS[4], "registered VHDR size mismatch")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(input_path, flags)
    except OSError as exc:
        raise VHDRRefusal(REFUSAL_IDS[3], "registered VHDR no-follow open failed") from exc
    try:
        descriptor_stat = os.fstat(descriptor)
        if (
            not stat.S_ISREG(descriptor_stat.st_mode)
            or descriptor_stat.st_size != int(registered["expected_size_bytes"])
            or descriptor_stat.st_dev != observed.st_dev
            or descriptor_stat.st_ino != observed.st_ino
        ):
            raise VHDRRefusal(REFUSAL_IDS[3], "registered VHDR changed during no-follow open")
        maximum_read = int(registered["maximum_read_bytes"])
        chunks: list[bytes] = []
        bytes_read = 0
        while bytes_read <= maximum_read:
            chunk = os.read(descriptor, min(4096, maximum_read + 1 - bytes_read))
            if not chunk:
                break
            chunks.append(chunk)
            bytes_read += len(chunk)
        payload = b"".join(chunks)
    finally:
        os.close(descriptor)
    if len(payload) != int(registered["expected_size_bytes"]) or len(payload) > maximum_read:
        raise VHDRRefusal(REFUSAL_IDS[4], "registered VHDR read size mismatch")
    source_sha1 = git_blob_sha1(payload)
    if source_sha1 != registered["source_identity"]:
        raise VHDRRefusal(REFUSAL_IDS[4], "registered VHDR Git blob identity mismatch")

    parsed = parse_vhdr_bytes(
        payload,
        expected_data_basename=registered["expected_data_basename"],
        expected_marker_basename=registered["expected_marker_basename"],
    )
    if HEAVY_MODULE_ROOTS.intersection(sys.modules) != heavy_before:
        raise VHDRRefusal(REFUSAL_IDS[7], "a heavy dependency was imported")
    counters = _base_access_counters()
    _assert_forbidden_counters_zero(counters)
    runtime = clock() - started
    peak_rss = max(initial_rss, rss_reader())
    if runtime > float(caps["wall_time_seconds"]) or peak_rss > int(caps["peak_rss_bytes"]):
        raise VHDRRefusal(REFUSAL_IDS[18], "runtime or peak RSS cap exceeded")

    ledger = _build_ledger(
        parsed=parsed,
        contract=contract,
        contract_sha256=contract_sha256,
        decision_sha256=decision_sha256,
        implementation_record_sha256=implementation_record_sha256,
        implementation_commit=evidence.implementation_commit,
        evidence=evidence,
        source_sha1=source_sha1,
        input_bytes=len(payload),
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        counters=counters,
    )
    json_bytes, summary_bytes = _finalize_output_bytes(ledger)
    runtime = clock() - started
    peak_rss = max(peak_rss, rss_reader())
    ledger["measurements"]["runtime_seconds_through_output_finalization"] = runtime
    ledger["measurements"]["peak_RSS_bytes_through_output_finalization"] = peak_rss
    json_bytes, summary_bytes = _finalize_output_bytes(ledger)
    generated = len(json_bytes) + len(summary_bytes)
    if generated != ledger["measurements"]["generated_output_bytes"]:
        raise VHDRRefusal(REFUSAL_IDS[18], "generated-output accounting mismatch")
    if generated > int(output["maximum_combined_generated_output_bytes"]):
        raise VHDRRefusal(REFUSAL_IDS[18], "generated-output cap exceeded")
    if (
        runtime > float(caps["wall_time_seconds"]) - 0.25
        or peak_rss > int(caps["peak_rss_bytes"]) - 1024 * 1024
    ):
        raise VHDRRefusal(REFUSAL_IDS[18], "insufficient resource headroom for output commit")
    _validate_safe_ledger(ledger, contract)

    _mkdir_missing_output_components(root, output_root)
    ledger_path = output_root / output["canonical_json_name"]
    summary_path = output_root / output["human_summary_name"]
    # The ledger is the commit marker: it is created only after the summary is complete.
    _exclusive_write(summary_path, summary_bytes)
    _exclusive_write(ledger_path, json_bytes)
    final_runtime = clock() - started
    final_rss = max(peak_rss, rss_reader())
    if final_runtime > float(caps["wall_time_seconds"]) or final_rss > int(caps["peak_rss_bytes"]):
        raise VHDRRefusal(REFUSAL_IDS[18], "post-write runtime or peak RSS cap exceeded")
    return VHDROutcome(
        ledger=ledger,
        ledger_path=ledger_path,
        summary_path=summary_path,
        runtime_seconds=final_runtime,
        peak_rss_bytes=final_rss,
        generated_output_bytes=generated,
    )


def execute_registered_vhdr(
    workspace_root: str | Path,
    *,
    evidence: ExecutionEvidence,
    environ: Mapping[str, str] | None = None,
) -> VHDROutcome:
    """Consume the single registered execution after all offline green checks."""

    root = Path(workspace_root)
    contract = load_registered_contract(root)
    load_authorization_decision(root)
    load_implementation_record(root)
    implementation_path = root / IMPLEMENTATION_RELATIVE_PATH
    implementation_sha256 = _sha256_file(implementation_path)
    return run_vhdr_ledger(
        contract=contract,
        contract_sha256=CONTRACT_SHA256,
        decision_sha256=DECISION_SHA256,
        implementation_record_sha256=implementation_sha256,
        evidence=evidence,
        workspace_root=root,
        environ=os.environ if environ is None else environ,
        verify_evidence=_verify_execution_evidence,
    )


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact dry-run plan without statting the registered data path."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    load_authorization_decision(root)
    registered = contract["registered_input"]
    return {
        "schema_name": "neurodecodekit.loop54_stage_a_vhdr_plan",
        "schema_version": SCHEMA_VERSION,
        "status": "dry_run_no_registered_path_stat_or_content_access",
        "stage_id": "L54-A",
        "expected_input_basename": registered["expected_basename"],
        "expected_input_bytes": registered["expected_size_bytes"],
        "maximum_read_bytes": registered["maximum_read_bytes"],
        "output_root": contract["output_contract"]["output_root"],
        "registered_real_executions": 1,
        "registered_VHDR_content_opens": 1,
        "siblings_resolved_statted_hashed_or_opened": 0,
        "network_bytes": 0,
        "claim_ceiling": "L54-Q2_declared_header_compatibility",
    }


def load_vhdr_ledger(
    path: str | Path,
    *,
    maximum_bytes: int = 1024 * 1024,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Load one bounded ledger for metadata-only inspection."""

    if maximum_bytes <= 0 or maximum_bytes > 1024 * 1024:
        raise ValueError("ledger inspection cap must be within 1 MiB")
    source = Path(path)
    with source.open("rb") as handle:
        payload = handle.read(maximum_bytes + 1)
    if len(payload) > maximum_bytes:
        raise ValueError("VHDR ledger exceeds the inspection cap")
    ledger = json.loads(payload.decode("ascii"), object_pairs_hook=_strict_json_object)
    if ledger.get("schema_name") != LEDGER_SCHEMA_NAME or ledger.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("VHDR ledger schema mismatch")
    try:
        bound_contract = load_registered_contract() if contract is None else contract
        _validate_safe_ledger(ledger, bound_contract)
        if contract is None:
            expected_implementation = _sha256_file(_repo_root() / IMPLEMENTATION_RELATIVE_PATH)
            if ledger["provenance"]["implementation_record_sha256"] != expected_implementation:
                raise VHDRRefusal(REFUSAL_IDS[1], "implementation record identity changed")
    except VHDRRefusal as exc:
        raise ValueError("VHDR ledger validation failed") from exc
    return ledger


def summarize_vhdr_ledger(ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Return a concise, target-free inspection summary."""

    header = ledger["declared_header"]
    measurements = ledger["measurements"]
    counters = ledger["access_counters"]
    return {
        "schema_name": ledger["schema_name"],
        "status": ledger["status"],
        "stage_id": ledger["stage_id"],
        "strict_codepage": header["strict_codepage"],
        "declared_channel_count": header["declared_channel_count"],
        "sampling_rate_hz": header["sampling_rate_hz"],
        "input_bytes": measurements["input_bytes"],
        "generated_output_bytes": measurements["generated_output_bytes"],
        "runtime_seconds_through_output_finalization": measurements[
            "runtime_seconds_through_output_finalization"
        ],
        "peak_RSS_bytes_through_output_finalization": measurements[
            "peak_RSS_bytes_through_output_finalization"
        ],
        "vhdr_content_opens": counters["vhdr_content_opens"],
        "sibling_path_stats": counters["sibling_path_stats"],
        "sibling_content_opens": counters["sibling_content_opens"],
        "warnings": list(ledger["warnings"]),
        "unavailable_fields": list(ledger["unavailable_fields"]),
        "claim_boundary": dict(ledger["claim_boundary"]),
    }
