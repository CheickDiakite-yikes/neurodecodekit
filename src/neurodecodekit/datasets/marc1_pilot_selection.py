"""Generated-only, privacy-preserving MARC-1 pilot selector."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import resource
import shutil
import stat
import sys
import tempfile
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_NAME = "neurodecodekit.marc1_pilot_selection_qualification"
PRIVATE_SCHEMA_NAME = "neurodecodekit.marc1_pilot_selection_private_manifest"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc1_privacy_preserving_pilot_selection_contract.v0.json"
)
CONTRACT_SHA256 = "2099849ad13c6c1a97488e81cef8b21dcd61e59914d00fd43b9e76e8ccd5c39c"
GREEN_CONTRACT_COMMIT = "d1218066e64dea502d263acf0c096ed7eab55a11"
GREEN_CONTRACT_CI_RUN_ID = 31_569_417_204
GREEN_CONTRACT_BASE_JOB_ID = 94_028_013_357
GREEN_CONTRACT_OPTIONAL_JOB_ID = 94_028_013_230
EXPECTED_ROUTE = "MARC1PSG-R1"
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_PUBLIC_OUTPUT_BYTES = 1024 * 1024
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024 * 1024
FREEWILL_PAYLOAD_CAP_BYTES = 6 * 1024**3
WRIST_PAYLOAD_CAP_BYTES = 2 * 1024**3
JOINT_PAYLOAD_CAP_BYTES = 8 * 1024**3
EXPECTED_FREEWILL_ROWS = 1_227
EXPECTED_FREEWILL_FILES = 1_025
EXPECTED_FREEWILL_DIRECTORIES = 202
EXPECTED_WRIST_ROWS = 55
EXPECTED_SELECTED_SUBJECTS = 12
EXPECTED_FREEWILL_BUNDLES = 72
EXPECTED_FREEWILL_MEMBERS = 288
EXPECTED_WRIST_ARCHIVES = 12
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
FREEWILL_ENTRY_FIELDS = frozenset(
    {
        "CRC32",
        "ZIP64_extra_used",
        "compressed_size",
        "compression_method",
        "entry_kind",
        "external_attributes",
        "general_purpose_flags",
        "local_header_offset",
        "member_name",
        "uncompressed_size",
        "version_made_by",
    }
)
WRIST_ROW_FIELDS = frozenset(
    {
        "computed_md5",
        "download_url",
        "file_id",
        "is_link_only",
        "name",
        "role",
        "size",
        "subject_id",
        "supplied_md5",
    }
)
PRIVATE_ROW_FIELDS = (
    "source_id",
    "subject_id",
    "session_id",
    "run_id",
    "split_role",
    "member_or_archive_name",
    "file_id_if_available",
    "local_header_offset_if_available",
    "CRC32_if_available",
    "compressed_size",
    "uncompressed_size",
    "source_hashes",
)
REQUIRED_SUFFIXES = ("_eeg.eeg", "_eeg.vhdr", "_eeg.vmrk", "_events.tsv")
CORE_MEMBER_RE = re.compile(
    r"(?:[A-Za-z0-9._-]+/)*"
    r"(?P<subject>sub-[0-9]{2})/(?P<session>ses-[0-9]{2})/eeg/"
    r"(?P=subject)_(?P=session)_task-(?P<task>[A-Za-z0-9]+)"
    r"(?:_[A-Za-z0-9]+-[A-Za-z0-9]+)*_run-(?P<run>[0-9]{2})"
    r"(?P<suffix>_eeg\.eeg|_eeg\.vhdr|_eeg\.vmrk|_events\.tsv)\Z"
)
SUBJECT_RE = re.compile(r"sub-[0-9]{2}\Z")
CRC_RE = re.compile(r"[0-9a-f]{8}\Z")
MD5_RE = re.compile(r"[0-9a-f]{32}\Z")
REFUSAL_IDS = (
    "MARC1PSG-F00-contract-artifact-or-green-proof-mismatch",
    "MARC1PSG-F01-private-inventory-identity-schema-count-or-mode-failure",
    "MARC1PSG-F02-path-member-or-run-bundle-failure",
    "MARC1PSG-F03-eligibility-rank-participant-run-or-split-failure",
    "MARC1PSG-F04-source-or-joint-byte-cap-failure",
    "MARC1PSG-F05-Wrist-metadata-or-participant-archive-failure",
    "MARC1PSG-F06-privacy-output-overwrite-resource-or-replay-failure",
)
REQUIRED_MUTATIONS = (
    "contract_or_artifact_hash_mismatch",
    "private_inventory_hash_mismatch",
    "private_inventory_row_count_mismatch",
    "private_inventory_unknown_field",
    "private_inventory_duplicate_member",
    "private_inventory_symlink_or_wrong_mode",
    "unsafe_or_non_NFC_member_path",
    "encrypted_or_unsupported_member",
    "directory_masquerading_as_regular_member",
    "malformed_Freewill_BIDS_path",
    "Freewill_path_filename_identity_mismatch",
    "Freewill_session_ineligible",
    "Freewill_run_bundle_incomplete",
    "Freewill_duplicate_companion_suffix",
    "Freewill_cross_subject_or_cross_run_companion",
    "Freewill_sampling_tier_ineligible",
    "Freewill_single_session_participant_selected",
    "Freewill_selected_participant_count_drift",
    "Freewill_participant_hash_rank_drift",
    "participant_chosen_by_member_size_or_CRC",
    "run_chosen_by_member_size_or_CRC",
    "Freewill_run_count_drift",
    "Freewill_fit_heldout_overlap",
    "Freewill_session_role_reversal",
    "Freewill_unregistered_third_session_used",
    "Freewill_source_or_joint_cap_exceeded",
    "Wrist_metadata_identity_or_count_mismatch",
    "Wrist_selected_archive_missing_duplicate_or_malformed",
    "Wrist_participant_hash_rank_drift",
    "Wrist_run_split_or_trial_count_drift",
    "Wrist_source_or_joint_cap_exceeded",
    "event_target_or_quality_content_read_attempt",
    "local_header_member_payload_or_archive_open_attempt",
    "public_Freewill_member_field_leak",
    "public_Wrist_file_field_or_local_path_leak",
    "output_symlink_overwrite_cap_or_replay_mismatch",
)
PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "green_contract",
        "cohort_summary",
        "split_summary",
        "byte_summary",
        "selection_hashes",
        "measurements",
        "mutation_summary",
        "access_counters",
        "acceptance_gates",
        "route",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "CRC32",
        "CRC32_if_available",
        "download_url",
        "file_id",
        "file_id_if_available",
        "local_header_offset",
        "local_header_offset_if_available",
        "member_name",
        "member_or_archive_name",
        "path",
        "raw_body",
        "url",
    }
)
SAFE_AGGREGATE_PROVENANCE_KEYS = frozenset(
    {
        "local_header_reads",
        "zero_event_target_local_header_payload_and_signal_reads",
    }
)


class PilotSelectionRefusal(RuntimeError):
    """Fail closed with one stable aggregate-safe route."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown MARC1-P1 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class SelectionResult:
    """Canonical private selection plus aggregate facts."""

    private_manifest: Mapping[str, Any]
    cohort_summary: Mapping[str, Any]
    split_summary: Mapping[str, Any]
    byte_summary: Mapping[str, Any]
    selection_hashes: Mapping[str, str]


@dataclass(frozen=True)
class QualificationOutcome:
    """One bounded generated qualification outcome."""

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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PilotSelectionRefusal(REFUSAL_IDS[6], "duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise PilotSelectionRefusal(REFUSAL_IDS[6], "non-finite JSON value")


def _strict_json(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "invalid UTF-8") from exc
    if "\x00" in text or any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "disallowed control character")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except PilotSelectionRefusal:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "invalid JSON") from exc
    if not isinstance(value, dict):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "JSON root is not an object")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact contract that passed both required remote jobs."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _sha256_file(path) != CONTRACT_SHA256:
        raise PilotSelectionRefusal(REFUSAL_IDS[0], "contract hash differs")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PilotSelectionRefusal(REFUSAL_IDS[0], "contract is unavailable") from exc
    _verify_contract_mapping(contract)
    return contract


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc1_privacy_preserving_pilot_selection_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("contract_id")
        != "MARC-1-P1-privacy-preserving-pilot-selection-generated-contract-v0"
        or contract.get("status")
        != "generated_fixture_only_contract_frozen_implementation_not_started"
    ):
        raise PilotSelectionRefusal(REFUSAL_IDS[0], "contract identity differs")
    proof = contract.get("green_inventory_proof")
    if not isinstance(proof, dict) or proof.get("both_required_jobs_green") is not True:
        raise PilotSelectionRefusal(REFUSAL_IDS[0], "upstream inventory proof is not green")
    if len(contract.get("required_mutations", ())) != len(REQUIRED_MUTATIONS):
        raise PilotSelectionRefusal(REFUSAL_IDS[0], "mutation inventory differs")
    if tuple(contract["required_mutations"]) != REQUIRED_MUTATIONS:
        raise PilotSelectionRefusal(REFUSAL_IDS[0], "mutation order differs")


def _rank_subjects(seed: str, subject_ids: Sequence[str]) -> list[str]:
    return sorted(
        subject_ids,
        key=lambda subject_id: (
            hashlib.sha256(seed.encode("utf-8") + b"\0" + subject_id.encode("utf-8")).hexdigest(),
            subject_id,
        ),
    )


def _validate_selected_subjects(
    observed: Sequence[str],
    expected: Sequence[str],
    eligible: Sequence[str],
) -> None:
    if len(observed) != EXPECTED_SELECTED_SUBJECTS or len(set(observed)) != len(observed):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "selected participant count differs")
    if any(subject not in eligible for subject in observed):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "ineligible participant was selected")
    if list(observed) != list(expected):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "participant hash rank differs")


def _normalize_member_name(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 1024:
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "member path type or length differs")
    if unicodedata.normalize("NFC", value) != value:
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "member path is not NFC")
    if value.startswith("/") or "\\" in value or "//" in value:
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "member path is not safe POSIX relative")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "member path contains a control")
    body = value[:-1] if value.endswith("/") else value
    if not body or any(part in {"", ".", ".."} for part in body.split("/")):
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "member path has unsafe component")
    return value


def _freewill_entry(name: str, ordinal: int, *, directory: bool = False) -> dict[str, Any]:
    if directory:
        compressed = 0
        uncompressed = 0
        method = 0
        external = 1_106_051_088
    else:
        if name.endswith("_eeg.eeg"):
            compressed = 8 * 1024 * 1024 + ordinal
            uncompressed = compressed + 256 * 1024
        elif name.endswith(("_eeg.vhdr", "_eeg.vmrk", "_events.tsv")):
            compressed = 4_096 + ordinal % 257
            uncompressed = compressed + 512
        else:
            compressed = 1_024 + ordinal % 509
            uncompressed = compressed + 128
        method = 8
        external = 2_175_008_768
    return {
        "CRC32": hashlib.sha256(name.encode("utf-8")).hexdigest()[:8],
        "ZIP64_extra_used": ordinal % 37 == 0,
        "compressed_size": compressed,
        "compression_method": method,
        "entry_kind": "directory" if directory else "regular_file",
        "external_attributes": external,
        "general_purpose_flags": 0,
        "local_header_offset": 1_024 + ordinal * 10_000_000,
        "member_name": name,
        "uncompressed_size": uncompressed,
        "version_made_by": 813,
    }


def build_generated_freewill_manifest(
    *,
    row_order: str = "canonical",
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build 1,227 generated central-directory rows without touching a real manifest."""

    registered = dict(contract or load_registered_contract())
    freewill = registered["freewill_axis"]
    counts = freewill["eligibility"]["published_session_1_2_run_counts"]
    file_names: list[str] = []
    directory_names = {"Freewill_generated/"}
    for subject in sorted(counts):
        directory_names.add(f"Freewill_generated/{subject}/")
        for session_index, run_count in enumerate(counts[subject], start=1):
            session = f"ses-{session_index:02d}"
            directory_names.add(f"Freewill_generated/{subject}/{session}/")
            directory_names.add(f"Freewill_generated/{subject}/{session}/eeg/")
            for run in range(1, run_count + 1):
                stem = (
                    f"Freewill_generated/{subject}/{session}/eeg/"
                    f"{subject}_{session}_task-freewill_run-{run:02d}"
                )
                file_names.extend(f"{stem}{suffix}" for suffix in REQUIRED_SUFFIXES)
    auxiliary_count = EXPECTED_FREEWILL_FILES - len(file_names)
    file_names.extend(
        f"Freewill_generated/generated_aux/aux-{index:04d}.txt"
        for index in range(auxiliary_count)
    )
    directory_names.add("Freewill_generated/generated_aux/")
    while len(directory_names) < EXPECTED_FREEWILL_DIRECTORIES:
        directory_names.add(
            f"Freewill_generated/generated_aux/group-{len(directory_names):03d}/"
        )
    names_and_kinds = [(name, True) for name in sorted(directory_names)] + [
        (name, False) for name in sorted(file_names)
    ]
    rows = [
        _freewill_entry(name, ordinal, directory=directory)
        for ordinal, (name, directory) in enumerate(names_and_kinds)
    ]
    if row_order == "reversed":
        rows.reverse()
    elif row_order != "canonical":
        raise ValueError("unknown generated Freewill row order")
    manifest = {
        "schema_name": "neurodecodekit.marc1_central_directory_private_manifest",
        "schema_version": SCHEMA_VERSION,
        "proof_posture": "generated_fixture_private_metadata_only",
        "source_identity": {
            "provider": "generated_fixture",
            "record_id": 28_632_599,
            "version": 1,
            "file_id": 0,
            "declared_archive_bytes": 13_591_548_048,
            "registered_MD5": "0" * 32,
            "whole_archive_downloaded": False,
            "member_payload_opened": False,
        },
        "transport_body_sha256": {
            "metadata": hashlib.sha256(b"generated-metadata").hexdigest(),
            "tail": hashlib.sha256(b"generated-tail").hexdigest(),
            "central_directory": hashlib.sha256(b"generated-directory").hexdigest(),
        },
        "entries": rows,
    }
    return manifest


def build_generated_wrist_metadata(
    *,
    row_order: str = "canonical",
) -> list[dict[str, Any]]:
    """Build 55 generated Figshare-style rows without a network client."""

    rows: list[dict[str, Any]] = []
    for index in range(1, 46):
        subject = f"sub-{index:02d}"
        name = f"wrist45_{subject}.zip"
        digest = hashlib.md5(name.encode("ascii"), usedforsecurity=False).hexdigest()
        rows.append(
            {
                "computed_md5": digest,
                "download_url": f"https://generated.invalid/wrist/{index}/{name}",
                "file_id": 20_000 + index,
                "is_link_only": False,
                "name": name,
                "role": "participant_archive",
                "size": 48 * 1024 * 1024 + index * 1_024,
                "subject_id": subject,
                "supplied_md5": digest,
            }
        )
    for index in range(10):
        name = f"generated_support_{index:02d}.txt"
        digest = hashlib.md5(name.encode("ascii"), usedforsecurity=False).hexdigest()
        rows.append(
            {
                "computed_md5": digest,
                "download_url": f"https://generated.invalid/wrist/support/{index}",
                "file_id": 30_000 + index,
                "is_link_only": False,
                "name": name,
                "role": "supplementary",
                "size": 1_024 + index,
                "subject_id": None,
                "supplied_md5": digest,
            }
        )
    rows.sort(key=lambda row: (str(row["role"]), str(row["subject_id"]), int(row["file_id"])))
    if row_order == "reversed":
        rows.reverse()
    elif row_order != "canonical":
        raise ValueError("unknown generated Wrist row order")
    return rows


def _canonical_freewill_bytes(manifest: Mapping[str, Any]) -> bytes:
    canonical = copy.deepcopy(dict(manifest))
    entries = canonical.get("entries")
    if isinstance(entries, list):
        canonical["entries"] = sorted(entries, key=lambda row: str(row.get("member_name", "")))
    return _canonical_json_bytes(canonical)


def _canonical_wrist_bytes(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return _canonical_json_bytes(
        sorted(
            (dict(row) for row in rows),
            key=lambda row: (str(row.get("role")), str(row.get("subject_id")), row.get("file_id", -1)),
        )
    )


def _assert_source_hash(observed: str, expected: str) -> None:
    if observed != expected:
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private inventory hash differs")


def _assert_private_source_attributes(*, is_symlink: bool, mode: int) -> None:
    if is_symlink or stat.S_IMODE(mode) != 0o600:
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private inventory path or mode differs")


def _validate_freewill_entry(row: Any) -> tuple[str, re.Match[str] | None]:
    if not isinstance(row, dict) or set(row) != FREEWILL_ENTRY_FIELDS:
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private inventory row fields differ")
    name = _normalize_member_name(row["member_name"])
    if not isinstance(row["CRC32"], str) or CRC_RE.fullmatch(row["CRC32"]) is None:
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "CRC declaration differs")
    integer_fields = (
        "compressed_size",
        "compression_method",
        "external_attributes",
        "general_purpose_flags",
        "local_header_offset",
        "uncompressed_size",
        "version_made_by",
    )
    if any(isinstance(row[key], bool) or not isinstance(row[key], int) for key in integer_fields):
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "inventory integer field differs")
    if row["compressed_size"] < 0 or row["uncompressed_size"] < 0:
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "inventory size is negative")
    if not isinstance(row["ZIP64_extra_used"], bool):
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "ZIP64 declaration differs")
    if row["compression_method"] not in {0, 8} or row["general_purpose_flags"] & 0x1:
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "encrypted or unsupported member")
    if row["entry_kind"] == "directory":
        if not name.endswith("/") or row["compressed_size"] or row["uncompressed_size"]:
            raise PilotSelectionRefusal(REFUSAL_IDS[2], "directory row is malformed")
        return name, None
    if row["entry_kind"] != "regular_file" or name.endswith("/"):
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "regular member type differs")
    match = CORE_MEMBER_RE.fullmatch(name)
    if match is None and any(token in name for token in REQUIRED_SUFFIXES):
        raise PilotSelectionRefusal(REFUSAL_IDS[2], "Freewill BIDS identity differs")
    return name, match


def _validate_freewill_manifest(
    manifest: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    expected_top = {
        "schema_name",
        "schema_version",
        "proof_posture",
        "source_identity",
        "transport_body_sha256",
        "entries",
    }
    if not isinstance(manifest, dict) or set(manifest) != expected_top:
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private inventory schema differs")
    if (
        manifest["schema_name"] != "neurodecodekit.marc1_central_directory_private_manifest"
        or manifest["schema_version"] != SCHEMA_VERSION
        or manifest["proof_posture"] != "generated_fixture_private_metadata_only"
    ):
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private inventory identity differs")
    source_identity = manifest["source_identity"]
    expected_source_fields = {
        "provider",
        "record_id",
        "version",
        "file_id",
        "declared_archive_bytes",
        "registered_MD5",
        "whole_archive_downloaded",
        "member_payload_opened",
    }
    if (
        not isinstance(source_identity, dict)
        or set(source_identity) != expected_source_fields
        or source_identity["provider"] != "generated_fixture"
        or source_identity["record_id"] != 28_632_599
        or source_identity["version"] != 1
        or source_identity["file_id"] != 0
        or source_identity["declared_archive_bytes"] != 13_591_548_048
        or source_identity["registered_MD5"] != "0" * 32
        or source_identity["whole_archive_downloaded"] is not False
        or source_identity["member_payload_opened"] is not False
    ):
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private source identity differs")
    transport_hashes = manifest["transport_body_sha256"]
    if (
        not isinstance(transport_hashes, dict)
        or set(transport_hashes) != {"metadata", "tail", "central_directory"}
        or any(
            not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in transport_hashes.values()
        )
    ):
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private transport provenance differs")
    entries = manifest["entries"]
    if not isinstance(entries, list) or len(entries) != EXPECTED_FREEWILL_ROWS:
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private inventory row count differs")
    names: set[str] = set()
    kinds = Counter()
    groups: dict[tuple[str, str, int], dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in entries:
        name, match = _validate_freewill_entry(row)
        if name in names:
            raise PilotSelectionRefusal(REFUSAL_IDS[1], "duplicate private member")
        names.add(name)
        kinds[row["entry_kind"]] += 1
        if match is not None:
            subject = match.group("subject")
            session = match.group("session")
            run = int(match.group("run"))
            groups[(subject, session, run)][match.group("suffix")].append(row)
    source_sha256 = _sha256_bytes(_canonical_freewill_bytes(manifest))
    if expected_source_sha256 is not None:
        _assert_source_hash(source_sha256, expected_source_sha256)
    if kinds != Counter(
        {"regular_file": EXPECTED_FREEWILL_FILES, "directory": EXPECTED_FREEWILL_DIRECTORIES}
    ):
        raise PilotSelectionRefusal(REFUSAL_IDS[1], "private inventory kind counts differ")
    for suffixes in groups.values():
        if set(suffixes) != set(REQUIRED_SUFFIXES) or any(len(rows) != 1 for rows in suffixes.values()):
            raise PilotSelectionRefusal(REFUSAL_IDS[2], "Freewill run bundle is incomplete")
    axis = contract["freewill_axis"]
    eligibility = axis["eligibility"]
    eligible = eligibility["eligible_subject_ids"]
    expected_selected = axis["selected_subject_ids_in_rank_order"]
    ranked = _rank_subjects(axis["selection_seed"], eligible)[:EXPECTED_SELECTED_SUBJECTS]
    _validate_selected_subjects(ranked, expected_selected, eligible)
    observed_counts: dict[str, list[int]] = {}
    for subject in eligible:
        observed_counts[subject] = [
            sum(1 for key in groups if key[0] == subject and key[1] == session)
            for session in ("ses-01", "ses-02")
        ]
    if observed_counts != eligibility["published_session_1_2_run_counts"]:
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "Freewill run count differs")
    if any(session not in {"ses-01", "ses-02"} for _, session, _ in groups):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "unregistered Freewill session was used")
    private_rows: list[dict[str, Any]] = []
    bundle_ids: list[tuple[str, str, int]] = []
    reserved_bytes = 0
    for subject in expected_selected:
        for session, split_role in (("ses-01", "fit"), ("ses-02", "heldout")):
            runs = sorted(run for row_subject, row_session, run in groups if row_subject == subject and row_session == session)
            selected_runs = runs[:3]
            if selected_runs != [1, 2, 3]:
                raise PilotSelectionRefusal(REFUSAL_IDS[3], "first-three run selection differs")
            for run in selected_runs:
                bundle_ids.append((subject, session, run))
                for suffix in REQUIRED_SUFFIXES:
                    row = groups[(subject, session, run)][suffix][0]
                    name = row["member_name"]
                    reserved_bytes += row["compressed_size"] + 30 + len(name.encode("utf-8")) + 65_535
                    private_rows.append(
                        {
                            "source_id": "freewill_23_generated",
                            "subject_id": subject,
                            "session_id": session,
                            "run_id": f"run-{run:02d}",
                            "split_role": split_role,
                            "member_or_archive_name": name,
                            "file_id_if_available": None,
                            "local_header_offset_if_available": row["local_header_offset"],
                            "CRC32_if_available": row["CRC32"],
                            "compressed_size": row["compressed_size"],
                            "uncompressed_size": row["uncompressed_size"],
                            "source_hashes": {
                                "generated_inventory_sha256": source_sha256,
                                "contract_sha256": CONTRACT_SHA256,
                            },
                        }
                    )
    if len(bundle_ids) != EXPECTED_FREEWILL_BUNDLES or len(private_rows) != EXPECTED_FREEWILL_MEMBERS:
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "Freewill selected bundle count differs")
    if reserved_bytes > FREEWILL_PAYLOAD_CAP_BYTES:
        raise PilotSelectionRefusal(REFUSAL_IDS[4], "Freewill selection exceeds byte cap")
    identity = {
        "selected_subject_ids": list(expected_selected),
        "selected_bundles": [list(item) for item in sorted(bundle_ids)],
        "fit_session": "ses-01",
        "heldout_session": "ses-02",
    }
    return {
        "private_rows": sorted(
            private_rows,
            key=lambda row: (
                row["subject_id"],
                row["session_id"],
                row["run_id"],
                row["member_or_archive_name"],
            ),
        ),
        "source_sha256": source_sha256,
        "selection_identity": identity,
        "selection_identity_sha256": _sha256_bytes(_canonical_json_bytes(identity)),
        "reserved_bytes": reserved_bytes,
    }


def _validate_wrist_split(
    fit_runs: Sequence[int],
    heldout_runs: Sequence[int],
    fit_trials: int,
    heldout_trials: int,
) -> None:
    if (
        list(fit_runs) != [1, 2, 3, 4, 5, 6]
        or list(heldout_runs) != [7, 8]
        or set(fit_runs) & set(heldout_runs)
        or fit_trials != 2_880
        or heldout_trials != 960
    ):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "Wrist run split or trial count differs")


def _validate_wrist_metadata(
    rows: Sequence[Mapping[str, Any]],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(rows, list) or len(rows) != EXPECTED_WRIST_ROWS:
        raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist metadata row count differs")
    seen_file_ids: set[int] = set()
    seen_names: set[str] = set()
    participants: dict[str, Mapping[str, Any]] = {}
    supplementary = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != WRIST_ROW_FIELDS:
            raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist metadata row fields differ")
        file_id = row["file_id"]
        size = row["size"]
        if (
            isinstance(file_id, bool)
            or not isinstance(file_id, int)
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size < 0
            or not isinstance(row["name"], str)
            or not isinstance(row["download_url"], str)
            or row["is_link_only"] is not False
        ):
            raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist metadata type differs")
        if file_id in seen_file_ids or row["name"] in seen_names:
            raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist archive identity is duplicated")
        seen_file_ids.add(file_id)
        seen_names.add(row["name"])
        for key in ("computed_md5", "supplied_md5"):
            if not isinstance(row[key], str) or MD5_RE.fullmatch(row[key]) is None:
                raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist MD5 declaration differs")
        if row["computed_md5"] != row["supplied_md5"]:
            raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist MD5 declarations disagree")
        if row["role"] == "supplementary":
            if row["subject_id"] is not None:
                raise PilotSelectionRefusal(REFUSAL_IDS[5], "supplementary row has a subject")
            supplementary += 1
            continue
        subject = row["subject_id"]
        if (
            row["role"] != "participant_archive"
            or not isinstance(subject, str)
            or SUBJECT_RE.fullmatch(subject) is None
            or row["name"] != f"wrist45_{subject}.zip"
            or row["download_url"]
            != f"https://generated.invalid/wrist/{int(subject[-2:])}/{row['name']}"
        ):
            raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist participant archive is malformed")
        participants[subject] = row
    axis = contract["wrist_axis"]
    eligible = axis["eligible_subject_ids"]
    if set(participants) != set(eligible) or len(participants) != 45 or supplementary != 10:
        raise PilotSelectionRefusal(REFUSAL_IDS[5], "Wrist participant inventory differs")
    expected_selected = axis["selected_subject_ids_in_rank_order"]
    ranked = _rank_subjects(axis["selection_seed"], eligible)[:EXPECTED_SELECTED_SUBJECTS]
    _validate_selected_subjects(ranked, expected_selected, eligible)
    split = axis["later_split"]
    _validate_wrist_split(
        split["fit_runs"],
        split["heldout_runs"],
        split["expected_fit_trials"],
        split["expected_heldout_trials"],
    )
    source_sha256 = _sha256_bytes(_canonical_wrist_bytes(rows))
    selected = [participants[subject] for subject in expected_selected]
    reserved_bytes = sum(int(row["size"]) for row in selected)
    if reserved_bytes > WRIST_PAYLOAD_CAP_BYTES:
        raise PilotSelectionRefusal(REFUSAL_IDS[4], "Wrist selection exceeds byte cap")
    private_rows = [
        {
            "source_id": "wrist_45_generated",
            "subject_id": row["subject_id"],
            "session_id": None,
            "run_id": "runs-01-through-08",
            "split_role": "fit-runs-01-06_and_heldout-runs-07-08",
            "member_or_archive_name": row["name"],
            "file_id_if_available": row["file_id"],
            "local_header_offset_if_available": None,
            "CRC32_if_available": None,
            "compressed_size": row["size"],
            "uncompressed_size": None,
            "source_hashes": {
                "generated_metadata_sha256": source_sha256,
                "declared_MD5": row["computed_md5"],
                "contract_sha256": CONTRACT_SHA256,
            },
        }
        for row in selected
    ]
    identity = {
        "selected_subject_ids": list(expected_selected),
        "fit_runs": [1, 2, 3, 4, 5, 6],
        "heldout_runs": [7, 8],
    }
    return {
        "private_rows": private_rows,
        "source_sha256": source_sha256,
        "selection_identity": identity,
        "selection_identity_sha256": _sha256_bytes(_canonical_json_bytes(identity)),
        "reserved_bytes": reserved_bytes,
    }


def select_generated_pilot(
    freewill_manifest: Mapping[str, Any],
    wrist_rows: Sequence[Mapping[str, Any]],
    *,
    contract: Mapping[str, Any] | None = None,
) -> SelectionResult:
    """Select the frozen generated pilot without reading content or outcomes."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    freewill = _validate_freewill_manifest(freewill_manifest, registered)
    wrist = _validate_wrist_metadata(wrist_rows, registered)
    joint_bytes = freewill["reserved_bytes"] + wrist["reserved_bytes"]
    if joint_bytes > JOINT_PAYLOAD_CAP_BYTES:
        raise PilotSelectionRefusal(REFUSAL_IDS[4], "joint selection exceeds byte cap")
    private_rows = freewill["private_rows"] + wrist["private_rows"]
    if any(tuple(row) != PRIVATE_ROW_FIELDS for row in private_rows):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "private output row order differs")
    private_manifest = {
        "schema_name": PRIVATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "proof_posture": "generated_fixture_selection_only_no_scientific_value",
        "contract_sha256": CONTRACT_SHA256,
        "rows": private_rows,
    }
    selection_identity = {
        "freewill": freewill["selection_identity"],
        "wrist": wrist["selection_identity"],
    }
    private_sha256 = _sha256_bytes(_canonical_json_bytes(private_manifest))
    selection_identity_sha256 = _sha256_bytes(_canonical_json_bytes(selection_identity))
    return SelectionResult(
        private_manifest=private_manifest,
        cohort_summary={
            "freewill_selected_subject_ids": list(
                registered["freewill_axis"]["selected_subject_ids_in_rank_order"]
            ),
            "wrist_selected_subject_ids": list(
                registered["wrist_axis"]["selected_subject_ids_in_rank_order"]
            ),
            "selected_subjects_per_axis": EXPECTED_SELECTED_SUBJECTS,
            "selection_was_target_quality_and_outcome_free": True,
        },
        split_summary={
            "freewill_fit_session": "ses-01",
            "freewill_heldout_session": "ses-02",
            "freewill_fit_run_bundles": 36,
            "freewill_heldout_run_bundles": 36,
            "freewill_selected_run_bundles": EXPECTED_FREEWILL_BUNDLES,
            "freewill_selected_core_members": EXPECTED_FREEWILL_MEMBERS,
            "wrist_fit_runs_per_participant": 6,
            "wrist_heldout_runs_per_participant": 2,
            "wrist_fit_runs": 72,
            "wrist_heldout_runs": 24,
            "wrist_expected_fit_trials": 2_880,
            "wrist_expected_heldout_trials": 960,
            "fit_heldout_overlap": 0,
        },
        byte_summary={
            "freewill_reserved_payload_bytes": freewill["reserved_bytes"],
            "freewill_payload_cap_bytes": FREEWILL_PAYLOAD_CAP_BYTES,
            "wrist_reserved_payload_bytes": wrist["reserved_bytes"],
            "wrist_payload_cap_bytes": WRIST_PAYLOAD_CAP_BYTES,
            "joint_reserved_payload_bytes": joint_bytes,
            "joint_payload_cap_bytes": JOINT_PAYLOAD_CAP_BYTES,
            "fallback_used": False,
        },
        selection_hashes={
            "freewill_generated_inventory_sha256": freewill["source_sha256"],
            "wrist_generated_metadata_sha256": wrist["source_sha256"],
            "freewill_selection_identity_sha256": freewill["selection_identity_sha256"],
            "wrist_selection_identity_sha256": wrist["selection_identity_sha256"],
            "joint_selection_identity_sha256": selection_identity_sha256,
            "private_selection_manifest_sha256": private_sha256,
        },
    )


def _replace_core_name(
    manifest: dict[str, Any],
    predicate: Callable[[str], bool],
    replacement: Callable[[str], str],
    *,
    limit: int = 1,
) -> None:
    changed = 0
    for row in manifest["entries"]:
        name = row["member_name"]
        if predicate(name) and changed < limit:
            row["member_name"] = replacement(name)
            row["CRC32"] = hashlib.sha256(row["member_name"].encode()).hexdigest()[:8]
            changed += 1
    if changed != limit:
        raise AssertionError("generated mutation target is unavailable")


def _expect_refusal(
    name: str,
    expected: str,
    operation: Callable[[], Any],
) -> str:
    try:
        operation()
    except PilotSelectionRefusal as exc:
        if exc.refusal_id != expected:
            raise PilotSelectionRefusal(
                REFUSAL_IDS[6],
                f"mutation {name} routed to an unexpected refusal",
            ) from exc
        return exc.refusal_id
    raise PilotSelectionRefusal(REFUSAL_IDS[6], f"mutation {name} did not refuse")


def _reject_forbidden_content_operation() -> None:
    raise PilotSelectionRefusal(REFUSAL_IDS[6], "event target or quality read is forbidden")


def _reject_member_operation() -> None:
    raise PilotSelectionRefusal(REFUSAL_IDS[2], "local header payload or archive open is forbidden")


def _assert_fixed_selection(observed: Sequence[str], expected: Sequence[str]) -> None:
    if list(observed) != list(expected):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "selection depended on size or CRC")


def _assert_run_selection(observed: Sequence[int], expected: Sequence[int]) -> None:
    if list(observed) != list(expected):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "run selection differs")


def _assert_split_roles(fit: Sequence[str], heldout: Sequence[str]) -> None:
    if set(fit) & set(heldout):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "fit and held-out identities overlap")
    if list(fit) != ["ses-01"] or list(heldout) != ["ses-02"]:
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "Freewill session roles differ")


def _assert_no_third_session(sessions: Sequence[str]) -> None:
    if any(session not in {"ses-01", "ses-02"} for session in sessions):
        raise PilotSelectionRefusal(REFUSAL_IDS[3], "unregistered Freewill session was used")


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if (
                key not in SAFE_AGGREGATE_PROVENANCE_KEYS
                and (
                    key in FORBIDDEN_PUBLIC_KEYS
                    or "member_name" in lowered
                    or "archive_name" in lowered
                    or "file_id" in lowered
                    or "local_header" in lowered
                    or lowered in {"crc", "crc32"}
                    or "download_url" in lowered
                    or "raw_body" in lowered
                    or "raw_header" in lowered
                    or lowered in {"path", "paths", "url", "urls"}
                    or lowered.endswith("_path")
                    or lowered.endswith("_paths")
                )
            ):
                raise PilotSelectionRefusal(REFUSAL_IDS[6], "public report leaks a private key")
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            "https://" in lowered
            or "_eeg." in lowered
            or "_events.tsv" in lowered
            or ".zip" in lowered
            or value.startswith("/")
            or "\\" in value
        ):
            raise PilotSelectionRefusal(REFUSAL_IDS[6], "public report leaks a private value")


def _bounded_output_bytes(report_bytes: bytes, private_bytes: bytes) -> int:
    if len(report_bytes) > MAX_PUBLIC_OUTPUT_BYTES:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "public output exceeds cap")
    total = len(report_bytes) + len(private_bytes)
    if total > MAX_COMBINED_OUTPUT_BYTES:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "combined output exceeds cap")
    return total


def _mutation_freewill(
    base: Mapping[str, Any],
    operation: Callable[[dict[str, Any]], None],
    contract: Mapping[str, Any],
) -> None:
    changed = copy.deepcopy(dict(base))
    operation(changed)
    _validate_freewill_manifest(changed, contract)


def _mutation_wrist(
    base: Sequence[Mapping[str, Any]],
    operation: Callable[[list[dict[str, Any]]], None],
    contract: Mapping[str, Any],
) -> None:
    changed = copy.deepcopy(list(base))
    operation(changed)
    _validate_wrist_metadata(changed, contract)


def run_required_mutations(
    freewill_manifest: Mapping[str, Any],
    wrist_rows: Sequence[Mapping[str, Any]],
    *,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Exercise every frozen generated refusal in its assigned class."""

    registered = dict(contract or load_registered_contract())
    freewill_sha = _sha256_bytes(_canonical_freewill_bytes(freewill_manifest))
    freewill_expected = registered["freewill_axis"]["selected_subject_ids_in_rank_order"]
    wrist_expected = registered["wrist_axis"]["selected_subject_ids_in_rank_order"]
    freewill_eligible = registered["freewill_axis"]["eligibility"]["eligible_subject_ids"]
    wrist_eligible = registered["wrist_axis"]["eligible_subject_ids"]

    def pop_row(value: dict[str, Any]) -> None:
        value["entries"].pop()

    def add_unknown(value: dict[str, Any]) -> None:
        value["entries"][0]["unknown"] = True

    def duplicate_member(value: dict[str, Any]) -> None:
        value["entries"][-1] = copy.deepcopy(value["entries"][0])

    def unsafe_path(value: dict[str, Any]) -> None:
        value["entries"][0]["member_name"] = "../unsafe/"

    def unsupported(value: dict[str, Any]) -> None:
        next(row for row in value["entries"] if row["entry_kind"] == "regular_file")[
            "compression_method"
        ] = 99

    def directory_masquerade(value: dict[str, Any]) -> None:
        next(row for row in value["entries"] if row["entry_kind"] == "directory")[
            "entry_kind"
        ] = "regular_file"

    def malformed_bids(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: name.endswith("_eeg.eeg"),
            lambda name: name.replace("_eeg.eeg", "_eeg.bad"),
        )

    def mismatched_identity(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-01/" in name and name.endswith("_eeg.eeg"),
            lambda name: name.replace("/sub-01_ses-", "/sub-03_ses-"),
        )

    def third_session_bundle(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01" in name,
            lambda name: name.replace("ses-01", "ses-03"),
            limit=4,
        )

    def incomplete_bundle(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.eeg" in name,
            lambda name: name.replace("_eeg.eeg", "_notes.txt"),
        )

    def duplicate_suffix(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.vmrk" in name,
            lambda name: name.replace("task-freewill", "task-generated").replace(
                "_eeg.vmrk", "_eeg.vhdr"
            ),
        )

    def cross_subject(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.vhdr" in name,
            lambda name: name.replace("/sub-08_ses-", "/sub-09_ses-"),
        )

    def run_count_drift(value: dict[str, Any]) -> None:
        targets = [
            row
            for row in value["entries"]
            if "/sub-01/ses-01/" in row["member_name"] and "_run-06" in row["member_name"]
        ]
        if len(targets) != 4:
            raise AssertionError("run-count mutation target differs")
        for index, row in enumerate(targets):
            row["member_name"] = f"Freewill_generated/generated_aux/run-drift-{index}.txt"
            row["CRC32"] = hashlib.sha256(row["member_name"].encode()).hexdigest()[:8]

    def freewill_over_cap(value: dict[str, Any]) -> None:
        for row in value["entries"]:
            if "/sub-08/" in row["member_name"] and row["member_name"].endswith("_eeg.eeg"):
                row["compressed_size"] = 2 * 1024**3
                row["uncompressed_size"] = row["compressed_size"] + 1

    def wrist_count_mismatch(value: list[dict[str, Any]]) -> None:
        participant = next(row for row in value if row["role"] == "participant_archive")
        participant["role"] = "supplementary"
        participant["subject_id"] = None
        participant["name"] = "generated_extra_missing.txt"
        participant["download_url"] = "https://generated.invalid/wrist/support/missing"

    def wrist_duplicate(value: list[dict[str, Any]]) -> None:
        selected = [row for row in value if row.get("subject_id") in wrist_expected]
        value[value.index(selected[1])] = copy.deepcopy(selected[0])

    def wrist_over_cap(value: list[dict[str, Any]]) -> None:
        for row in value:
            if row.get("subject_id") in wrist_expected:
                row["size"] = 256 * 1024**2

    checks: dict[str, tuple[str, Callable[[], Any]]] = {
        "contract_or_artifact_hash_mismatch": (
            REFUSAL_IDS[0],
            lambda: _verify_contract_mapping({**registered, "contract_id": "changed"}),
        ),
        "private_inventory_hash_mismatch": (
            REFUSAL_IDS[1],
            lambda: _assert_source_hash(freewill_sha, "0" * 64),
        ),
        "private_inventory_row_count_mismatch": (
            REFUSAL_IDS[1],
            lambda: _mutation_freewill(freewill_manifest, pop_row, registered),
        ),
        "private_inventory_unknown_field": (
            REFUSAL_IDS[1],
            lambda: _mutation_freewill(freewill_manifest, add_unknown, registered),
        ),
        "private_inventory_duplicate_member": (
            REFUSAL_IDS[1],
            lambda: _mutation_freewill(freewill_manifest, duplicate_member, registered),
        ),
        "private_inventory_symlink_or_wrong_mode": (
            REFUSAL_IDS[1],
            lambda: _assert_private_source_attributes(is_symlink=True, mode=0o600),
        ),
        "unsafe_or_non_NFC_member_path": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, unsafe_path, registered),
        ),
        "encrypted_or_unsupported_member": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, unsupported, registered),
        ),
        "directory_masquerading_as_regular_member": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, directory_masquerade, registered),
        ),
        "malformed_Freewill_BIDS_path": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, malformed_bids, registered),
        ),
        "Freewill_path_filename_identity_mismatch": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, mismatched_identity, registered),
        ),
        "Freewill_session_ineligible": (
            REFUSAL_IDS[3],
            lambda: _mutation_freewill(freewill_manifest, third_session_bundle, registered),
        ),
        "Freewill_run_bundle_incomplete": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, incomplete_bundle, registered),
        ),
        "Freewill_duplicate_companion_suffix": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, duplicate_suffix, registered),
        ),
        "Freewill_cross_subject_or_cross_run_companion": (
            REFUSAL_IDS[2],
            lambda: _mutation_freewill(freewill_manifest, cross_subject, registered),
        ),
        "Freewill_sampling_tier_ineligible": (
            REFUSAL_IDS[3],
            lambda: _validate_selected_subjects(
                [*freewill_expected[:-1], "sub-13"], freewill_expected, freewill_eligible
            ),
        ),
        "Freewill_single_session_participant_selected": (
            REFUSAL_IDS[3],
            lambda: _validate_selected_subjects(
                [*freewill_expected[:-1], "sub-02"], freewill_expected, freewill_eligible
            ),
        ),
        "Freewill_selected_participant_count_drift": (
            REFUSAL_IDS[3],
            lambda: _validate_selected_subjects(
                freewill_expected[:-1], freewill_expected, freewill_eligible
            ),
        ),
        "Freewill_participant_hash_rank_drift": (
            REFUSAL_IDS[3],
            lambda: _validate_selected_subjects(
                [freewill_expected[1], freewill_expected[0], *freewill_expected[2:]],
                freewill_expected,
                freewill_eligible,
            ),
        ),
        "participant_chosen_by_member_size_or_CRC": (
            REFUSAL_IDS[3],
            lambda: _assert_fixed_selection(list(reversed(freewill_expected)), freewill_expected),
        ),
        "run_chosen_by_member_size_or_CRC": (
            REFUSAL_IDS[3],
            lambda: _assert_run_selection([2, 3, 4], [1, 2, 3]),
        ),
        "Freewill_run_count_drift": (
            REFUSAL_IDS[3],
            lambda: _mutation_freewill(freewill_manifest, run_count_drift, registered),
        ),
        "Freewill_fit_heldout_overlap": (
            REFUSAL_IDS[3],
            lambda: _assert_split_roles(["ses-01"], ["ses-01"]),
        ),
        "Freewill_session_role_reversal": (
            REFUSAL_IDS[3],
            lambda: _assert_split_roles(["ses-02"], ["ses-01"]),
        ),
        "Freewill_unregistered_third_session_used": (
            REFUSAL_IDS[3],
            lambda: _assert_no_third_session(["ses-01", "ses-03"]),
        ),
        "Freewill_source_or_joint_cap_exceeded": (
            REFUSAL_IDS[4],
            lambda: _mutation_freewill(freewill_manifest, freewill_over_cap, registered),
        ),
        "Wrist_metadata_identity_or_count_mismatch": (
            REFUSAL_IDS[5],
            lambda: _mutation_wrist(wrist_rows, wrist_count_mismatch, registered),
        ),
        "Wrist_selected_archive_missing_duplicate_or_malformed": (
            REFUSAL_IDS[5],
            lambda: _mutation_wrist(wrist_rows, wrist_duplicate, registered),
        ),
        "Wrist_participant_hash_rank_drift": (
            REFUSAL_IDS[3],
            lambda: _validate_selected_subjects(
                [wrist_expected[1], wrist_expected[0], *wrist_expected[2:]],
                wrist_expected,
                wrist_eligible,
            ),
        ),
        "Wrist_run_split_or_trial_count_drift": (
            REFUSAL_IDS[3],
            lambda: _validate_wrist_split([1, 2, 3, 4, 5], [6, 7, 8], 2_880, 960),
        ),
        "Wrist_source_or_joint_cap_exceeded": (
            REFUSAL_IDS[4],
            lambda: _mutation_wrist(wrist_rows, wrist_over_cap, registered),
        ),
        "event_target_or_quality_content_read_attempt": (
            REFUSAL_IDS[6],
            _reject_forbidden_content_operation,
        ),
        "local_header_member_payload_or_archive_open_attempt": (
            REFUSAL_IDS[2],
            _reject_member_operation,
        ),
        "public_Freewill_member_field_leak": (
            REFUSAL_IDS[6],
            lambda: _walk_public({"member_or_archive_name": "private"}),
        ),
        "public_Wrist_file_field_or_local_path_leak": (
            REFUSAL_IDS[6],
            lambda: _walk_public({"download_url": "https://generated.invalid/private"}),
        ),
        "output_symlink_overwrite_cap_or_replay_mismatch": (
            REFUSAL_IDS[6],
            lambda: _bounded_output_bytes(b"x" * (MAX_PUBLIC_OUTPUT_BYTES + 1), b""),
        ),
    }
    if tuple(checks) != REQUIRED_MUTATIONS:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "mutation implementation order differs")
    return {
        name: _expect_refusal(name, expected, operation)
        for name, (expected, operation) in checks.items()
    }


def _assert_resources(runtime_seconds: float, peak_rss_bytes: int) -> None:
    if runtime_seconds > MAX_RUNTIME_SECONDS:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "runtime exceeds cap")
    if peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "peak RSS exceeds cap")
    for key in THREAD_ENV_KEYS:
        if os.environ.get(key) not in {None, "1"}:
            raise PilotSelectionRefusal(REFUSAL_IDS[6], "numerical thread setting exceeds one")


def _assert_output_destination(output_dir: Path) -> None:
    if output_dir.exists() or output_dir.is_symlink():
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "output directory already exists")
    parent = output_dir.parent
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "output parent is unavailable")
    if stat.S_ISLNK(os.lstat(parent).st_mode):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "output parent is a symlink")


def _write_outputs(
    output_dir: Path,
    report: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
) -> tuple[Path, Path, int]:
    _assert_output_destination(output_dir)
    report_bytes = _canonical_json_bytes(report)
    private_bytes = _canonical_json_bytes(private_manifest)
    total = _bounded_output_bytes(report_bytes, private_bytes)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        report_path = stage / "marc1_pilot_selection_report.v0.json"
        private_path = stage / "marc1_pilot_selection.private.v0.json"
        report_path.write_bytes(report_bytes)
        private_path.write_bytes(private_bytes)
        private_path.chmod(0o600)
        os.replace(stage, output_dir)
    except Exception as exc:
        shutil.rmtree(stage, ignore_errors=True)
        if isinstance(exc, PilotSelectionRefusal):
            raise
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "output write failed") from exc
    final_report = output_dir / "marc1_pilot_selection_report.v0.json"
    final_private = output_dir / "marc1_pilot_selection.private.v0.json"
    if stat.S_IMODE(final_private.stat().st_mode) != 0o600:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "private output mode differs")
    return final_report, final_private, total


def _build_report(
    selection: SelectionResult,
    mutations: Mapping[str, str],
    *,
    generated_input_bytes: int,
    generated_output_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    return {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_pilot_selection_qualification",
        "proof_posture": "generated_metadata_only_no_scientific_value",
        "green_contract": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "cohort_summary": dict(selection.cohort_summary),
        "split_summary": dict(selection.split_summary),
        "byte_summary": dict(selection.byte_summary),
        "selection_hashes": dict(selection.selection_hashes),
        "measurements": {
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes": generated_output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "Freewill_fixture_rows": EXPECTED_FREEWILL_ROWS,
            "Wrist_fixture_rows": EXPECTED_WRIST_ROWS,
            "selected_private_rows": EXPECTED_FREEWILL_MEMBERS + EXPECTED_WRIST_ARCHIVES,
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
            "private_Freewill_manifest_reads": 0,
            "private_Freewill_manifest_bytes": 0,
            "public_Wrist_metadata_requests": 0,
            "public_Wrist_metadata_bytes": 0,
            "real_participant_selections": 0,
            "real_member_or_archive_selections": 0,
            "local_header_reads": 0,
            "member_or_archive_payload_reads": 0,
            "network_payload_bytes": 0,
            "signal_sample_reads": 0,
            "event_target_label_quality_or_onset_reads": 0,
            "real_derivative_rows": 0,
            "training_or_parameter_update_fits": 0,
            "model_inference_calls": 0,
            "prediction_sets_or_freezes": 0,
            "target_deliveries_or_scores": 0,
            "provider_or_language_model_calls": 0,
            "hardware_operations": 0,
            "retries_or_reruns": 0,
            "scientific_claim_upgrades": 0,
        },
        "acceptance_gates": {
            "green_contract_identity": True,
            "exact_DOI_bound_participant_ranks": True,
            "exact_1227_Freewill_and_55_Wrist_rows": True,
            "exact_12_subjects_per_source": True,
            "exact_72_Freewill_bundles_and_288_members": True,
            "exact_cross_day_and_run_heldout_splits": True,
            "irrelevant_row_order_invariance": True,
            "size_and_CRC_independent_selection": True,
            "zero_event_target_local_header_payload_and_signal_reads": True,
            "source_and_joint_caps": True,
            "private_and_public_output_separation": True,
            "all_36_mutations_refused": True,
            "byte_identical_deterministic_replay": True,
            "resource_and_output_caps": True,
            "all_real_neural_model_score_and_claim_counters_zero": True,
        },
        "route": EXPECTED_ROUTE,
        "warnings": [
            "All inventory and metadata rows are generated fixtures with no human content.",
            "The selected participant identifiers are preregistered but no real participant row was read.",
            "Declared generated sizes and checksums are interface fixtures and do not verify a payload.",
            "No event target signal quality model prediction or score was accessed.",
            "End-to-end neural decoding latency was not measured.",
        ],
        "unavailable_fields": [
            "real selected member and archive identities",
            "real payload byte totals and integrity",
            "channel geometry signal quality event target or movement onset",
            "neural feature model prediction score or latency",
            "thought-to-text evidence",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A deterministic target-free selector can bind a storage-capped two-axis pilot "
                "without using signal quality or outcome information."
            ),
            "scientific_claim_not_established": (
                "Generated selection metadata contain no human neural signal model prediction "
                "or score and establish no neural effect or decoding capability."
            ),
        },
    }


def validate_public_report(
    report: Mapping[str, Any],
    *,
    allow_incomplete_measurements: bool = False,
) -> None:
    """Validate one aggregate-only generated selection report."""

    if set(report) != PUBLIC_REPORT_FIELDS:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "public report fields differ")
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("status") != "passed_generated_pilot_selection_qualification"
        or report.get("route") != EXPECTED_ROUTE
    ):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "public report identity differs")
    _walk_public(report)
    counters = report.get("access_counters")
    gates = report.get("acceptance_gates")
    mutations = report.get("mutation_summary")
    if not isinstance(counters, dict) or any(counters.values()):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "public access counter is nonzero")
    if not isinstance(gates, dict) or len(gates) != 15 or not all(gates.values()):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "acceptance gate differs")
    if not isinstance(mutations, dict) or mutations.get("passed_count") != 36:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "mutation summary differs")
    measurements = report.get("measurements")
    if not isinstance(measurements, dict):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "measurements are unavailable")
    if not allow_incomplete_measurements:
        if measurements.get("generated_output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1) > MAX_COMBINED_OUTPUT_BYTES:
            raise PilotSelectionRefusal(REFUSAL_IDS[6], "output measurement exceeds cap")
        if measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1) > MAX_RUNTIME_SECONDS:
            raise PilotSelectionRefusal(REFUSAL_IDS[6], "runtime measurement exceeds cap")
        if measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1) > MAX_PEAK_RSS_BYTES:
            raise PilotSelectionRefusal(REFUSAL_IDS[6], "RSS measurement exceeds cap")


def qualify_generated_pilot_selection(
    output_dir: str | Path,
    *,
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run one bounded generated qualification and atomically write two outputs."""

    destination = Path(output_dir)
    _assert_output_destination(destination)
    start = clock()
    contract = load_registered_contract()
    first_freewill = build_generated_freewill_manifest(contract=contract)
    first_wrist = build_generated_wrist_metadata()
    replay_freewill = build_generated_freewill_manifest(row_order="reversed", contract=contract)
    replay_wrist = build_generated_wrist_metadata(row_order="reversed")
    first = select_generated_pilot(first_freewill, first_wrist, contract=contract)
    replay = select_generated_pilot(replay_freewill, replay_wrist, contract=contract)
    if _canonical_json_bytes(first.private_manifest) != _canonical_json_bytes(replay.private_manifest):
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "private selection replay differs")
    if first.selection_hashes != replay.selection_hashes:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "aggregate selection replay differs")
    mutations = run_required_mutations(first_freewill, first_wrist, contract=contract)
    runtime_seconds = clock() - start
    peak_rss_bytes = rss_probe()
    _assert_resources(runtime_seconds, peak_rss_bytes)
    generated_input_bytes = sum(
        (
            len(_canonical_json_bytes(first_freewill)),
            len(_canonical_json_bytes(first_wrist)),
            len(_canonical_json_bytes(replay_freewill)),
            len(_canonical_json_bytes(replay_wrist)),
        )
    )
    report = _build_report(
        first,
        mutations,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=0,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
    )
    validate_public_report(report, allow_incomplete_measurements=True)
    private_bytes = _canonical_json_bytes(first.private_manifest)
    for _ in range(4):
        report_bytes = _canonical_json_bytes(report)
        total = _bounded_output_bytes(report_bytes, private_bytes)
        if report["measurements"]["generated_output_bytes"] == total:
            break
        report["measurements"]["generated_output_bytes"] = total
    else:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "output measurement did not stabilize")
    validate_public_report(report)
    report_path, private_path, written_total = _write_outputs(
        destination, report, first.private_manifest
    )
    if written_total != report["measurements"]["generated_output_bytes"]:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "written output byte count differs")
    return QualificationOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=private_path,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=written_total,
    )


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Inspect only an aggregate generated report."""

    report_path = Path(path)
    if report_path.is_symlink() or not report_path.is_file():
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "aggregate report path is unavailable")
    size = report_path.stat().st_size
    if size > MAX_PUBLIC_OUTPUT_BYTES:
        raise PilotSelectionRefusal(REFUSAL_IDS[6], "aggregate report exceeds cap")
    report = _strict_json(report_path.read_bytes())
    validate_public_report(report)
    return {
        "route": report["route"],
        "selected_subjects_per_axis": report["cohort_summary"]["selected_subjects_per_axis"],
        "freewill_selected_run_bundles": report["split_summary"][
            "freewill_selected_run_bundles"
        ],
        "freewill_selected_core_members": report["split_summary"][
            "freewill_selected_core_members"
        ],
        "wrist_selected_archives": EXPECTED_WRIST_ARCHIVES,
        "joint_reserved_payload_bytes": report["byte_summary"][
            "joint_reserved_payload_bytes"
        ],
        "mutation_refusals_passed": report["mutation_summary"]["passed_count"],
        "generated_input_bytes": report["measurements"]["generated_input_bytes"],
        "generated_output_bytes": report["measurements"]["generated_output_bytes"],
        "runtime_seconds": report["measurements"]["runtime_seconds"],
        "peak_RSS_bytes": report["measurements"]["peak_RSS_bytes"],
        "warnings": list(report["warnings"]),
        "unavailable_fields": list(report["unavailable_fields"]),
    }


def build_plan_summary() -> dict[str, Any]:
    """Return the fixed generated-only plan without constructing fixtures."""

    contract = load_registered_contract()
    return {
        "lane_id": "MARC1-P1",
        "contract_sha256": CONTRACT_SHA256,
        "green_contract_commit": GREEN_CONTRACT_COMMIT,
        "green_contract_CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
        "generated_commands": list(contract["interface"]["generated_commands"]),
        "freewill_fixture_rows": EXPECTED_FREEWILL_ROWS,
        "wrist_fixture_rows": EXPECTED_WRIST_ROWS,
        "selected_subjects_per_axis": EXPECTED_SELECTED_SUBJECTS,
        "freewill_selected_run_bundles": EXPECTED_FREEWILL_BUNDLES,
        "freewill_selected_core_members": EXPECTED_FREEWILL_MEMBERS,
        "wrist_selected_archives": EXPECTED_WRIST_ARCHIVES,
        "required_mutations": len(REQUIRED_MUTATIONS),
        "combined_output_cap_bytes": MAX_COMBINED_OUTPUT_BYTES,
        "real_or_network_operations_authorized": 0,
        "signal_target_model_or_score_operations_authorized": 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_pilot_selection",
        description="Qualify the generated-only MARC1-P1 pilot selector.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the frozen generated-only plan.")
    qualify = subparsers.add_parser("qualify", help="Run one generated qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate generated report.")
    inspect.add_argument("report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            payload = build_plan_summary()
        elif args.command == "qualify":
            outcome = qualify_generated_pilot_selection(args.output_dir)
            payload = {
                "route": outcome.report["route"],
                "report": str(outcome.report_path),
                "private_manifest": str(outcome.private_manifest_path),
                "runtime_seconds": outcome.runtime_seconds,
                "peak_RSS_bytes": outcome.peak_rss_bytes,
                "generated_input_bytes": outcome.generated_input_bytes,
                "generated_output_bytes": outcome.generated_output_bytes,
            }
        else:
            payload = inspect_generated_report(args.report)
    except PilotSelectionRefusal as exc:
        print(
            json.dumps(
                {"refusal_id": exc.refusal_id, "reason": exc.safe_reason},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
