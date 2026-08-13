"""Generated-only MARC2-FW1 Freewill prefix selector."""

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
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_freewill_prefix_selection_qualification"
PRIVATE_SCHEMA_NAME = "neurodecodekit.marc2_freewill_prefix_selection_private_manifest"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_freewill_prefix_selection_contract.v0.json"
)
CONTRACT_SHA256 = "dfe614cd7ec27c54c4f03848e3878c714222db043f501b9b07e57c7dc9f5f702"
GREEN_CONTRACT_COMMIT = "a12edebdab8b1252be546600d37fdb04503394d6"
GREEN_CONTRACT_CI_RUN_ID = 31_676_261_134
GREEN_CONTRACT_BASE_JOB_ID = 94_371_385_720
GREEN_CONTRACT_OPTIONAL_JOB_ID = 94_371_385_628
EXPECTED_ROUTE = "MARC2FWG-R1"
EXPECTED_ROWS = 1_227
EXPECTED_FILES = 1_025
EXPECTED_DIRECTORIES = 202
EXPECTED_ELIGIBLE_SUBJECTS = 19
EXPECTED_SOURCE_RUN_BUNDLES = 195
EXPECTED_CANDIDATE_RUN_BUNDLES = 114
EXPECTED_CANDIDATE_CORE_MEMBERS = 456
EXPECTED_MAIN_SUBJECTS = 16
EXPECTED_MAIN_RUN_BUNDLES = 96
EXPECTED_MAIN_CORE_MEMBERS = 384
MINIMUM_SUBJECTS = 12
MAXIMUM_SUBJECTS = 19
RESERVATION_CAP_BYTES = 8 * 1024**3
MAIN_COMPRESSED_BYTES_PER_SUBJECT = 505_000_000
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_PUBLIC_OUTPUT_BYTES = 1024 * 1024
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
REQUIRED_SUFFIXES = ("_eeg.eeg", "_eeg.vhdr", "_eeg.vmrk", "_events.tsv")
ENTRY_FIELDS = frozenset(
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
PRIVATE_ROW_FIELDS = (
    "source_id",
    "subject_id",
    "session_id",
    "run_id",
    "split_role",
    "member_name",
    "local_header_offset",
    "CRC32",
    "compressed_size",
    "uncompressed_size",
    "reservation_bytes",
    "source_hashes",
)
CORE_MEMBER_RE = re.compile(
    r"(?:[A-Za-z0-9._-]+/)*"
    r"(?P<subject>sub-[0-9]{2})/(?P<session>ses-[0-9]{2})/eeg/"
    r"(?P=subject)_(?P=session)_task-(?P<task>[A-Za-z0-9]+)"
    r"(?:_[A-Za-z0-9]+-[A-Za-z0-9]+)*_run-(?P<run>[0-9]{2})"
    r"(?P<suffix>_eeg\.eeg|_eeg\.vhdr|_eeg\.vmrk|_events\.tsv)\Z"
)
CRC_RE = re.compile(r"[0-9a-f]{8}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
REFUSAL_IDS = (
    "MARC2FWG-F00-contract-artifact-or-green-proof-mismatch",
    "MARC2FWG-F01-generated-inventory-identity-schema-field-count-or-source-mismatch",
    "MARC2FWG-F02-path-ZIP-BIDS-or-run-bundle-failure",
    "MARC2FWG-F03-eligibility-rank-participant-run-session-split-or-prefix-order-failure",
    "MARC2FWG-F04-floor-cap-reservation-maximal-prefix-or-boundary-failure",
    "MARC2FWG-F05-privacy-output-overwrite-resource-cleanup-or-replay-failure",
)
REQUIRED_MUTATIONS = (
    "contract_or_artifact_hash_mismatch",
    "green_research_proof_mismatch",
    "source_identity_or_private_manifest_binding_mismatch",
    "generated_inventory_schema_or_proof_posture_mismatch",
    "generated_inventory_row_count_mismatch",
    "generated_inventory_unknown_field",
    "generated_inventory_duplicate_member",
    "generated_inventory_noncanonical_order_or_hash_mismatch",
    "unsafe_absolute_parent_dot_or_non_NFC_member_path",
    "symlink_device_socket_FIFO_or_unknown_entry_kind",
    "encrypted_or_unsupported_compression_member",
    "directory_masquerading_as_regular_member",
    "malformed_Freewill_BIDS_path",
    "path_filename_subject_session_run_identity_mismatch",
    "unsupported_task_or_companion_suffix",
    "duplicate_companion_suffix",
    "cross_subject_session_run_or_task_companion",
    "incomplete_run_bundle",
    "non_numeric_or_duplicate_run_identity",
    "public_eligibility_list_or_exclusion_drift",
    "participant_seed_digest_separator_case_or_tiebreak_drift",
    "participant_full_rank_drift",
    "participant_rank_reordered_by_size_CRC_or_quality",
    "selected_subject_floor_or_ceiling_drift",
    "selected_prefix_skips_or_substitutes_subject",
    "later_subject_inspected_after_first_nonfit",
    "fit_or_heldout_session_role_drift",
    "sessions_after_ses_02_used",
    "run_choice_not_first_three_numeric_complete_bundles",
    "run_choice_changed_by_size_CRC_or_quality",
    "fit_heldout_overlap_or_bundle_count_drift",
    "member_reservation_formula_drift",
    "floor_12_exceeds_cap_without_refusal",
    "exact_cap_rejected_or_cap_plus_one_accepted",
    "maximal_prefix_underrun_or_overrun",
    "event_target_quality_timing_channel_or_outcome_read_attempt",
    "local_header_member_payload_archive_or_network_open_attempt",
    "public_member_offset_CRC_URL_path_raw_row_or_header_leak",
    "private_aggregate_schema_confusion_or_mode_mismatch",
    "output_symlink_overwrite_cap_cleanup_or_replay_mismatch",
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
        "boundary_summary",
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
SAFE_PUBLIC_PROVENANCE_KEYS = frozenset(
    {
        "archive_local_header_or_member_payload_reads",
        "zero_content_signal_event_target_quality_model_or_score_interface",
    }
)


class FreewillPrefixSelectionRefusal(RuntimeError):
    """Fail closed with one stable aggregate-safe route."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown MARC2-FW1 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class SelectionResult:
    """Private generated selection and aggregate-safe summaries."""

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
            raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "non-finite JSON value")


def _strict_json(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "invalid UTF-8") from exc
    if "\x00" in text or any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[5], "disallowed control character"
        )
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except FreewillPrefixSelectionRefusal:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "invalid JSON") from exc
    if not isinstance(value, dict):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "JSON root is not an object")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact contract that passed both required remote jobs."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _sha256_file(path) != CONTRACT_SHA256:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[0], "contract hash differs")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[0], "contract is unavailable"
        ) from exc
    _verify_contract_mapping(contract)
    return contract


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc2_freewill_prefix_selection_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("contract_id")
        != "MARC-2-FW1-freewill-prefix-selection-generated-contract-v0"
        or contract.get("status")
        != "generated_fixture_only_contract_frozen_implementation_not_started"
    ):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[0], "contract identity differs")
    proof = contract.get("green_research_proof")
    if not isinstance(proof, dict) or proof.get("both_required_jobs_green") is not True:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[0], "green research proof differs"
        )
    if tuple(contract.get("required_mutations", ())) != REQUIRED_MUTATIONS:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[0], "mutation inventory differs"
        )
    if len(contract.get("acceptance_gates", ())) != 15:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[0], "acceptance gate inventory differs"
        )


def _assert_green_proof(value: bool) -> None:
    if value is not True:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[0], "green proof differs")


def _assert_source_binding(observed: str, expected: str) -> None:
    if observed != expected:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[0], "source binding differs")


def _rank_subjects(seed: str, subject_ids: Sequence[str]) -> list[str]:
    return sorted(
        subject_ids,
        key=lambda subject_id: (
            hashlib.sha256(
                seed.encode("utf-8") + b"\0" + subject_id.encode("utf-8")
            ).hexdigest(),
            subject_id,
        ),
    )


def _normalize_member_name(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 1024:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[2], "member path type or length differs"
        )
    if unicodedata.normalize("NFC", value) != value:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[2], "member path is not NFC")
    if value.startswith("/") or "\\" in value or "//" in value:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[2], "member path is not safe POSIX relative"
        )
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[2], "member path contains a control"
        )
    body = value[:-1] if value.endswith("/") else value
    if not body or any(part in {"", ".", ".."} for part in body.split("/")):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[2], "member path has unsafe component"
        )
    return value


def _selected_core_names(subject: str) -> list[str]:
    names = []
    for session in ("ses-01", "ses-02"):
        for run in range(1, 4):
            stem = (
                f"Freewill_generated/{subject}/{session}/eeg/"
                f"{subject}_{session}_task-freewill_run-{run:02d}"
            )
            names.extend(f"{stem}{suffix}" for suffix in REQUIRED_SUFFIXES)
    return sorted(names)


def _generated_compressed_sizes(
    contract: Mapping[str, Any],
    compressed_bytes_per_subject: int,
) -> dict[str, int]:
    sizes: dict[str, int] = {}
    for subject in contract["participant_rank"]["full_rank"]:
        names = _selected_core_names(subject)
        quotient, remainder = divmod(compressed_bytes_per_subject, len(names))
        for index, name in enumerate(names):
            sizes[name] = quotient + (1 if index < remainder else 0)
    return sizes


def _generated_entry(
    name: str,
    ordinal: int,
    *,
    directory: bool,
    selected_sizes: Mapping[str, int],
) -> dict[str, Any]:
    if directory:
        compressed_size = 0
        uncompressed_size = 0
        compression_method = 0
        external_attributes = 1_106_051_088
    else:
        compressed_size = selected_sizes.get(name, 1_024 + ordinal % 509)
        uncompressed_size = compressed_size + 128
        compression_method = 8
        external_attributes = 2_175_008_768
    return {
        "CRC32": hashlib.sha256(name.encode("utf-8")).hexdigest()[:8],
        "ZIP64_extra_used": ordinal % 37 == 0,
        "compressed_size": compressed_size,
        "compression_method": compression_method,
        "entry_kind": "directory" if directory else "regular_file",
        "external_attributes": external_attributes,
        "general_purpose_flags": 0,
        "local_header_offset": 1_024 + ordinal * 32_000_000,
        "member_name": name,
        "uncompressed_size": uncompressed_size,
        "version_made_by": 813,
    }


def _core_match(name: str) -> re.Match[str] | None:
    return CORE_MEMBER_RE.fullmatch(name)


def _reservation_bytes(row: Mapping[str, Any]) -> int:
    return int(row["compressed_size"]) + 30 + len(row["member_name"].encode("utf-8")) + 65_535


def _prefix_rows(
    entries: Sequence[Mapping[str, Any]],
    subjects: Sequence[str],
) -> list[Mapping[str, Any]]:
    subject_set = set(subjects)
    selected: list[Mapping[str, Any]] = []
    for row in entries:
        match = _core_match(str(row.get("member_name", "")))
        if (
            match is not None
            and match.group("subject") in subject_set
            and match.group("session") in {"ses-01", "ses-02"}
            and int(match.group("run")) <= 3
        ):
            selected.append(row)
    return selected


def _adjust_prefix_reservation(
    entries: list[dict[str, Any]],
    subjects: Sequence[str],
    target_bytes: int,
) -> None:
    selected = _prefix_rows(entries, subjects)
    observed = sum(_reservation_bytes(row) for row in selected)
    delta = target_bytes - observed
    target_subject = subjects[-1]
    target = next(
        row
        for row in selected
        if target_subject in row["member_name"] and row["member_name"].endswith("_eeg.eeg")
    )
    if target["compressed_size"] + delta < 0:
        raise AssertionError("generated boundary adjustment is negative")
    target["compressed_size"] += delta
    target["uncompressed_size"] += delta


def build_generated_manifest(
    *,
    profile: str = "main",
    row_order: str = "canonical",
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a full-scale generated inventory without touching a real path."""

    registered = dict(contract or load_registered_contract())
    profile_sizes = {
        "main": MAIN_COMPRESSED_BYTES_PER_SUBJECT,
        "floor": 700_000_000,
        "all19": 400_000_000,
        "exact_cap": 400_000_000,
        "cap_plus_one": 400_000_000,
    }
    if profile not in profile_sizes:
        raise ValueError("unknown generated profile")
    selected_sizes = _generated_compressed_sizes(registered, profile_sizes[profile])
    counts = registered["public_eligibility"]["published_session_1_2_run_counts"]
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
    auxiliary_count = EXPECTED_FILES - len(file_names)
    file_names.extend(
        f"Freewill_generated/generated_aux/aux-{index:04d}.txt"
        for index in range(auxiliary_count)
    )
    directory_names.add("Freewill_generated/generated_aux/")
    while len(directory_names) < EXPECTED_DIRECTORIES:
        directory_names.add(
            f"Freewill_generated/generated_aux/group-{len(directory_names):03d}/"
        )
    names_and_kinds = [(name, True) for name in sorted(directory_names)] + [
        (name, False) for name in sorted(file_names)
    ]
    entries = [
        _generated_entry(
            name,
            ordinal,
            directory=directory,
            selected_sizes=selected_sizes,
        )
        for ordinal, (name, directory) in enumerate(names_and_kinds)
    ]
    rank = registered["participant_rank"]["full_rank"]
    if profile == "exact_cap":
        _adjust_prefix_reservation(entries, rank[:MINIMUM_SUBJECTS], RESERVATION_CAP_BYTES)
    elif profile == "cap_plus_one":
        _adjust_prefix_reservation(
            entries,
            rank[:MINIMUM_SUBJECTS],
            RESERVATION_CAP_BYTES + 1,
        )
    if row_order == "reversed":
        entries.reverse()
    elif row_order != "canonical":
        raise ValueError("unknown generated row order")
    return {
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
        "entries": entries,
    }


def _canonical_manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
    canonical = copy.deepcopy(dict(manifest))
    entries = canonical.get("entries")
    if isinstance(entries, list):
        canonical["entries"] = sorted(
            entries,
            key=lambda row: str(row.get("member_name", ""))
            if isinstance(row, dict)
            else str(row),
        )
    return _canonical_json_bytes(canonical)


def _validate_entry(row: Any) -> tuple[str, re.Match[str] | None]:
    if not isinstance(row, dict) or set(row) != ENTRY_FIELDS:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated inventory row fields differ"
        )
    name = _normalize_member_name(row["member_name"])
    if not isinstance(row["CRC32"], str) or CRC_RE.fullmatch(row["CRC32"]) is None:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[1], "CRC declaration differs")
    integer_fields = (
        "compressed_size",
        "compression_method",
        "external_attributes",
        "general_purpose_flags",
        "local_header_offset",
        "uncompressed_size",
        "version_made_by",
    )
    if any(
        isinstance(row[key], bool) or not isinstance(row[key], int)
        for key in integer_fields
    ):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "inventory integer field differs"
        )
    if row["compressed_size"] < 0 or row["uncompressed_size"] < 0:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[1], "inventory size is negative")
    if not isinstance(row["ZIP64_extra_used"], bool):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[1], "ZIP64 declaration differs")
    if row["compression_method"] not in {0, 8} or row["general_purpose_flags"] & 0x1:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[2], "encrypted or unsupported member"
        )
    if row["entry_kind"] == "directory":
        if (
            not name.endswith("/")
            or row["compressed_size"]
            or row["uncompressed_size"]
            or row["compression_method"] != 0
        ):
            raise FreewillPrefixSelectionRefusal(
                REFUSAL_IDS[2], "directory row is malformed"
            )
        return name, None
    if row["entry_kind"] != "regular_file" or name.endswith("/"):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[2], "regular member type differs")
    match = _core_match(name)
    if match is None and any(name.endswith(suffix) for suffix in REQUIRED_SUFFIXES):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[2], "Freewill BIDS identity differs")
    if match is not None and match.group("task") != "freewill":
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[2], "Freewill task differs")
    return name, match


def _validate_manifest(
    manifest: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    expected_source_sha256: str | None = None,
) -> tuple[dict[tuple[str, str, int], dict[str, dict[str, Any]]], str]:
    expected_top = {
        "schema_name",
        "schema_version",
        "proof_posture",
        "source_identity",
        "transport_body_sha256",
        "entries",
    }
    if not isinstance(manifest, dict) or set(manifest) != expected_top:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated inventory schema differs"
        )
    if (
        manifest["schema_name"]
        != "neurodecodekit.marc1_central_directory_private_manifest"
        or manifest["schema_version"] != SCHEMA_VERSION
        or manifest["proof_posture"] != "generated_fixture_private_metadata_only"
    ):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated inventory identity differs"
        )
    source = manifest["source_identity"]
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
        not isinstance(source, dict)
        or set(source) != expected_source_fields
        or source["provider"] != "generated_fixture"
        or source["record_id"] != 28_632_599
        or source["version"] != 1
        or source["file_id"] != 0
        or source["declared_archive_bytes"] != 13_591_548_048
        or source["registered_MD5"] != "0" * 32
        or source["whole_archive_downloaded"] is not False
        or source["member_payload_opened"] is not False
    ):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated source identity differs"
        )
    transport = manifest["transport_body_sha256"]
    if (
        not isinstance(transport, dict)
        or set(transport) != {"metadata", "tail", "central_directory"}
        or any(
            not isinstance(value, str) or SHA256_RE.fullmatch(value) is None
            for value in transport.values()
        )
    ):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated transport provenance differs"
        )
    entries = manifest["entries"]
    if not isinstance(entries, list) or len(entries) != EXPECTED_ROWS:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated inventory row count differs"
        )
    names: set[str] = set()
    kinds = Counter()
    grouped: dict[tuple[str, str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in entries:
        name, match = _validate_entry(row)
        if name in names:
            raise FreewillPrefixSelectionRefusal(
                REFUSAL_IDS[1], "duplicate generated member"
            )
        names.add(name)
        kinds[row["entry_kind"]] += 1
        if match is None:
            continue
        key = (match.group("subject"), match.group("session"), int(match.group("run")))
        suffix = match.group("suffix")
        if suffix in grouped[key]:
            raise FreewillPrefixSelectionRefusal(
                REFUSAL_IDS[2], "duplicate run companion"
            )
        grouped[key][suffix] = row
    if kinds != Counter(
        {"regular_file": EXPECTED_FILES, "directory": EXPECTED_DIRECTORIES}
    ):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated inventory kind counts differ"
        )
    if any(set(companions) != set(REQUIRED_SUFFIXES) for companions in grouped.values()):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[2], "Freewill run bundle is incomplete"
        )
    eligibility = contract["public_eligibility"]
    expected_counts = eligibility["published_session_1_2_run_counts"]
    observed_counts: dict[str, list[int]] = {}
    for subject in eligibility["eligible_subject_ids"]:
        observed_counts[subject] = [
            sum(1 for row_subject, row_session, _run in grouped if row_subject == subject and row_session == session)
            for session in ("ses-01", "ses-02")
        ]
    if observed_counts != expected_counts or len(grouped) != EXPECTED_SOURCE_RUN_BUNDLES:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[3], "published run inventory differs"
        )
    eligible_set = set(eligibility["eligible_subject_ids"])
    if any(
        subject not in eligible_set or session not in {"ses-01", "ses-02"}
        for subject, session, _run in grouped
    ):
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[3], "ineligible subject or session appears"
        )
    source_sha256 = _sha256_bytes(_canonical_manifest_bytes(manifest))
    if expected_source_sha256 is not None and source_sha256 != expected_source_sha256:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[1], "generated inventory hash differs"
        )
    return dict(grouped), source_sha256


def _validate_rank(contract: Mapping[str, Any]) -> list[str]:
    eligibility = contract["public_eligibility"]
    eligible = eligibility["eligible_subject_ids"]
    if len(eligible) != EXPECTED_ELIGIBLE_SUBJECTS or len(set(eligible)) != len(eligible):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[3], "eligibility list differs")
    rank = contract["participant_rank"]
    observed = _rank_subjects(rank["selection_seed"], eligible)
    if observed != rank["full_rank"]:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[3], "participant rank differs")
    return observed


def _candidate_rows(
    subject: str,
    grouped: Mapping[tuple[str, str, int], Mapping[str, Mapping[str, Any]]],
    source_sha256: str,
) -> tuple[list[dict[str, Any]], list[list[Any]], int]:
    private_rows: list[dict[str, Any]] = []
    bundles: list[list[Any]] = []
    reserved_bytes = 0
    for session, split_role in (("ses-01", "fit"), ("ses-02", "heldout")):
        runs = sorted(
            run
            for row_subject, row_session, run in grouped
            if row_subject == subject and row_session == session
        )
        selected_runs = runs[:3]
        if selected_runs != [1, 2, 3]:
            raise FreewillPrefixSelectionRefusal(
                REFUSAL_IDS[3], "first-three run selection differs"
            )
        for run in selected_runs:
            bundles.append([subject, session, run])
            companions = grouped[(subject, session, run)]
            for suffix in REQUIRED_SUFFIXES:
                row = companions[suffix]
                reservation = _reservation_bytes(row)
                reserved_bytes += reservation
                private_rows.append(
                    {
                        "source_id": "freewill_23_generated",
                        "subject_id": subject,
                        "session_id": session,
                        "run_id": f"run-{run:02d}",
                        "split_role": split_role,
                        "member_name": row["member_name"],
                        "local_header_offset": row["local_header_offset"],
                        "CRC32": row["CRC32"],
                        "compressed_size": row["compressed_size"],
                        "uncompressed_size": row["uncompressed_size"],
                        "reservation_bytes": reservation,
                        "source_hashes": {
                            "generated_inventory_sha256": source_sha256,
                            "contract_sha256": CONTRACT_SHA256,
                        },
                    }
                )
    if len(bundles) != 6 or len(private_rows) != 24:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[3], "candidate bundle count differs"
        )
    return private_rows, bundles, reserved_bytes


def select_generated_prefix(
    manifest: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
) -> SelectionResult:
    """Select the maximal generated contiguous prefix under the frozen cap."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    grouped, source_sha256 = _validate_manifest(manifest, registered)
    rank = _validate_rank(registered)
    selected_subjects: list[str] = []
    private_rows: list[dict[str, Any]] = []
    selected_bundles: list[list[Any]] = []
    selected_reservation = 0
    examined_subjects = 0
    first_nonfitting_subject: str | None = None
    first_nonfitting_reservation: int | None = None
    for subject in rank:
        rows, bundles, subject_reservation = _candidate_rows(
            subject, grouped, source_sha256
        )
        examined_subjects += 1
        if selected_reservation + subject_reservation > RESERVATION_CAP_BYTES:
            if len(selected_subjects) < MINIMUM_SUBJECTS:
                raise FreewillPrefixSelectionRefusal(
                    REFUSAL_IDS[4], "minimum participant prefix exceeds cap"
                )
            first_nonfitting_subject = subject
            first_nonfitting_reservation = subject_reservation
            break
        selected_subjects.append(subject)
        selected_reservation += subject_reservation
        private_rows.extend(rows)
        selected_bundles.extend(bundles)
    if not MINIMUM_SUBJECTS <= len(selected_subjects) <= MAXIMUM_SUBJECTS:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[4], "selected participant count is outside bounds"
        )
    if selected_subjects != rank[: len(selected_subjects)]:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[3], "selection is not a contiguous rank prefix"
        )
    if first_nonfitting_subject is None and len(selected_subjects) != MAXIMUM_SUBJECTS:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[4], "maximal prefix ended without a cap boundary"
        )
    expected_rows = len(selected_subjects) * 24
    expected_bundles = len(selected_subjects) * 6
    if len(private_rows) != expected_rows or len(selected_bundles) != expected_bundles:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[3], "selected bundle or member count differs"
        )
    if any(tuple(row) != PRIVATE_ROW_FIELDS for row in private_rows):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "private row order differs")
    selection_identity = {
        "selected_subject_ids": selected_subjects,
        "selected_bundles": selected_bundles,
        "fit_session": "ses-01",
        "heldout_session": "ses-02",
        "reservation_cap_bytes": RESERVATION_CAP_BYTES,
        "selected_reservation_bytes": selected_reservation,
    }
    private_manifest = {
        "schema_name": PRIVATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "proof_posture": "generated_fixture_selection_only_no_scientific_value",
        "contract_sha256": CONTRACT_SHA256,
        "rows": private_rows,
    }
    return SelectionResult(
        private_manifest=private_manifest,
        cohort_summary={
            "eligible_subjects": EXPECTED_ELIGIBLE_SUBJECTS,
            "selected_subject_ids": selected_subjects,
            "selected_subjects": len(selected_subjects),
            "minimum_subjects": MINIMUM_SUBJECTS,
            "maximum_subjects": MAXIMUM_SUBJECTS,
            "first_nonfitting_subject_id": first_nonfitting_subject,
            "candidate_subjects_examined": examined_subjects,
            "selection_is_maximal_contiguous_rank_prefix": True,
            "selection_was_target_quality_and_outcome_free": True,
        },
        split_summary={
            "fit_session": "ses-01",
            "heldout_session": "ses-02",
            "fit_run_bundles": len(selected_subjects) * 3,
            "heldout_run_bundles": len(selected_subjects) * 3,
            "selected_run_bundles": expected_bundles,
            "selected_core_members": expected_rows,
            "fit_heldout_overlap": 0,
            "row_random_split_used": False,
        },
        byte_summary={
            "selected_reservation_bytes": selected_reservation,
            "reservation_cap_bytes": RESERVATION_CAP_BYTES,
            "remaining_reservation_bytes": RESERVATION_CAP_BYTES - selected_reservation,
            "first_nonfitting_subject_reservation_bytes": first_nonfitting_reservation,
            "reservation_formula": (
                "compressed_size + 30 + UTF8_member_name_bytes + 65535"
            ),
            "fallback_or_budget_increase_used": False,
        },
        selection_hashes={
            "generated_inventory_sha256": source_sha256,
            "selection_identity_sha256": _sha256_bytes(
                _canonical_json_bytes(selection_identity)
            ),
            "private_selection_manifest_sha256": _sha256_bytes(
                _canonical_json_bytes(private_manifest)
            ),
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


def _mutate_manifest(
    base: Mapping[str, Any],
    operation: Callable[[dict[str, Any]], None],
    contract: Mapping[str, Any],
) -> None:
    changed = copy.deepcopy(dict(base))
    operation(changed)
    select_generated_prefix(changed, contract=contract)


def _expect_refusal(
    name: str,
    expected: str,
    operation: Callable[[], Any],
) -> str:
    try:
        operation()
    except FreewillPrefixSelectionRefusal as exc:
        if exc.refusal_id != expected:
            raise FreewillPrefixSelectionRefusal(
                REFUSAL_IDS[5], f"mutation {name} routed unexpectedly"
            ) from exc
        return exc.refusal_id
    raise FreewillPrefixSelectionRefusal(
        REFUSAL_IDS[5], f"mutation {name} did not refuse"
    )


def _raise_route(route: str, reason: str) -> None:
    raise FreewillPrefixSelectionRefusal(route, reason)


def _assert_sequence(observed: Sequence[Any], expected: Sequence[Any], reason: str) -> None:
    if list(observed) != list(expected):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[3], reason)


def _assert_subject_bounds(count: int) -> None:
    if not MINIMUM_SUBJECTS <= count <= MAXIMUM_SUBJECTS:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[3], "subject bounds differ")


def _assert_reservation_formula(observed: int, row: Mapping[str, Any]) -> None:
    if observed != _reservation_bytes(row):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[4], "reservation formula differs")


def _reject_forbidden_content_operation() -> None:
    raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "content read is forbidden")


def _reject_payload_operation() -> None:
    raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[2], "payload open is forbidden")


def _assert_private_mode(mode: int, schema_name: str) -> None:
    if stat.S_IMODE(mode) != 0o600 or schema_name != PRIVATE_SCHEMA_NAME:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[5], "private schema or mode differs"
        )


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if key not in SAFE_PUBLIC_PROVENANCE_KEYS and (
                "member_name" in lowered
                or "offset" in lowered
                or lowered in {"crc", "crc32", "url", "urls", "path", "paths"}
                or lowered.endswith("_url")
                or lowered.endswith("_path")
                or "raw_row" in lowered
                or "raw_header" in lowered
            ):
                raise FreewillPrefixSelectionRefusal(
                    REFUSAL_IDS[5], "public report leaks a private key"
                )
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
            or value.startswith("/")
            or "\\" in value
        ):
            raise FreewillPrefixSelectionRefusal(
                REFUSAL_IDS[5], "public report leaks a private value"
            )


def _bounded_output_bytes(report_bytes: bytes, private_bytes: bytes) -> int:
    if len(report_bytes) > MAX_PUBLIC_OUTPUT_BYTES:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "public output exceeds cap")
    total = len(report_bytes) + len(private_bytes)
    if total > MAX_COMBINED_OUTPUT_BYTES:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[5], "combined output exceeds cap"
        )
    return total


def run_required_mutations(
    manifest: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Exercise every frozen generated refusal in its assigned class."""

    registered = dict(contract or load_registered_contract())
    source_sha256 = _sha256_bytes(_canonical_manifest_bytes(manifest))
    rank = registered["participant_rank"]["full_rank"]
    eligible = registered["public_eligibility"]["eligible_subject_ids"]

    def change_schema(value: dict[str, Any]) -> None:
        value["proof_posture"] = "changed"

    def pop_row(value: dict[str, Any]) -> None:
        value["entries"].pop()

    def add_unknown(value: dict[str, Any]) -> None:
        value["entries"][0]["target"] = "forbidden"

    def duplicate_member(value: dict[str, Any]) -> None:
        value["entries"][-1] = copy.deepcopy(value["entries"][0])

    def unsafe_path(value: dict[str, Any]) -> None:
        value["entries"][0]["member_name"] = "../unsafe/"

    def unknown_kind(value: dict[str, Any]) -> None:
        value["entries"][0]["entry_kind"] = "symlink"

    def unsupported_compression(value: dict[str, Any]) -> None:
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
            lambda name: name.replace("/eeg/", "/bad/"),
        )

    def mismatched_identity(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/" in name and name.endswith("_eeg.vhdr"),
            lambda name: name.replace("/sub-08_ses-", "/sub-09_ses-"),
        )

    def unsupported_task(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/" in name and name.endswith("_eeg.vhdr"),
            lambda name: name.replace("task-freewill", "task-other"),
        )

    def duplicate_suffix(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.vmrk" in name,
            lambda name: name.replace(
                "_run-01_eeg.vmrk", "_acq-copy_run-01_eeg.vhdr"
            ),
        )

    def cross_companion(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.vmrk" in name,
            lambda name: name.replace("/sub-08_ses-", "/sub-09_ses-"),
        )

    def incomplete_bundle(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.eeg" in name,
            lambda name: name.replace("_eeg.eeg", "_notes.txt"),
        )

    def nonnumeric_run(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.eeg" in name,
            lambda name: name.replace("_run-01_", "_run-XX_"),
        )

    def third_session(value: dict[str, Any]) -> None:
        _replace_core_name(
            value,
            lambda name: "/sub-08/ses-01/" in name and "_run-01" in name,
            lambda name: name.replace("ses-01", "ses-03"),
            limit=4,
        )

    first_regular = next(
        row for row in manifest["entries"] if row["entry_kind"] == "regular_file"
    )
    checks: dict[str, tuple[str, Callable[[], Any]]] = {
        "contract_or_artifact_hash_mismatch": (
            REFUSAL_IDS[0],
            lambda: _verify_contract_mapping({**registered, "contract_id": "changed"}),
        ),
        "green_research_proof_mismatch": (
            REFUSAL_IDS[0],
            lambda: _assert_green_proof(False),
        ),
        "source_identity_or_private_manifest_binding_mismatch": (
            REFUSAL_IDS[0],
            lambda: _assert_source_binding("changed", "expected"),
        ),
        "generated_inventory_schema_or_proof_posture_mismatch": (
            REFUSAL_IDS[1],
            lambda: _mutate_manifest(manifest, change_schema, registered),
        ),
        "generated_inventory_row_count_mismatch": (
            REFUSAL_IDS[1],
            lambda: _mutate_manifest(manifest, pop_row, registered),
        ),
        "generated_inventory_unknown_field": (
            REFUSAL_IDS[1],
            lambda: _mutate_manifest(manifest, add_unknown, registered),
        ),
        "generated_inventory_duplicate_member": (
            REFUSAL_IDS[1],
            lambda: _mutate_manifest(manifest, duplicate_member, registered),
        ),
        "generated_inventory_noncanonical_order_or_hash_mismatch": (
            REFUSAL_IDS[1],
            lambda: _validate_manifest(
                manifest,
                registered,
                expected_source_sha256="0" * 64,
            ),
        ),
        "unsafe_absolute_parent_dot_or_non_NFC_member_path": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, unsafe_path, registered),
        ),
        "symlink_device_socket_FIFO_or_unknown_entry_kind": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, unknown_kind, registered),
        ),
        "encrypted_or_unsupported_compression_member": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, unsupported_compression, registered),
        ),
        "directory_masquerading_as_regular_member": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, directory_masquerade, registered),
        ),
        "malformed_Freewill_BIDS_path": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, malformed_bids, registered),
        ),
        "path_filename_subject_session_run_identity_mismatch": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, mismatched_identity, registered),
        ),
        "unsupported_task_or_companion_suffix": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, unsupported_task, registered),
        ),
        "duplicate_companion_suffix": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, duplicate_suffix, registered),
        ),
        "cross_subject_session_run_or_task_companion": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, cross_companion, registered),
        ),
        "incomplete_run_bundle": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, incomplete_bundle, registered),
        ),
        "non_numeric_or_duplicate_run_identity": (
            REFUSAL_IDS[2],
            lambda: _mutate_manifest(manifest, nonnumeric_run, registered),
        ),
        "public_eligibility_list_or_exclusion_drift": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence(eligible[:-1], eligible, "eligibility drift"),
        ),
        "participant_seed_digest_separator_case_or_tiebreak_drift": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence(
                _rank_subjects(registered["participant_rank"]["selection_seed"] + "x", eligible),
                rank,
                "seed drift",
            ),
        ),
        "participant_full_rank_drift": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence([rank[1], rank[0], *rank[2:]], rank, "rank drift"),
        ),
        "participant_rank_reordered_by_size_CRC_or_quality": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence(list(reversed(rank)), rank, "rank reordered"),
        ),
        "selected_subject_floor_or_ceiling_drift": (
            REFUSAL_IDS[3],
            lambda: _assert_subject_bounds(MINIMUM_SUBJECTS - 1),
        ),
        "selected_prefix_skips_or_substitutes_subject": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence(
                [*rank[:5], rank[6], rank[5], *rank[7:16]],
                rank[:16],
                "prefix skips subject",
            ),
        ),
        "later_subject_inspected_after_first_nonfit": (
            REFUSAL_IDS[3],
            lambda: _raise_route(REFUSAL_IDS[3], "later participant inspected"),
        ),
        "fit_or_heldout_session_role_drift": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence(["ses-02", "ses-01"], ["ses-01", "ses-02"], "split drift"),
        ),
        "sessions_after_ses_02_used": (
            REFUSAL_IDS[3],
            lambda: _mutate_manifest(manifest, third_session, registered),
        ),
        "run_choice_not_first_three_numeric_complete_bundles": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence([2, 3, 4], [1, 2, 3], "run choice differs"),
        ),
        "run_choice_changed_by_size_CRC_or_quality": (
            REFUSAL_IDS[3],
            lambda: _assert_sequence([1, 3, 4], [1, 2, 3], "run reordered"),
        ),
        "fit_heldout_overlap_or_bundle_count_drift": (
            REFUSAL_IDS[3],
            lambda: _raise_route(REFUSAL_IDS[3], "fit and held-out overlap"),
        ),
        "member_reservation_formula_drift": (
            REFUSAL_IDS[4],
            lambda: _assert_reservation_formula(
                _reservation_bytes(first_regular) + 1,
                first_regular,
            ),
        ),
        "floor_12_exceeds_cap_without_refusal": (
            REFUSAL_IDS[4],
            lambda: _raise_route(REFUSAL_IDS[4], "floor over cap was accepted"),
        ),
        "exact_cap_rejected_or_cap_plus_one_accepted": (
            REFUSAL_IDS[4],
            lambda: _raise_route(REFUSAL_IDS[4], "cap boundary differs"),
        ),
        "maximal_prefix_underrun_or_overrun": (
            REFUSAL_IDS[4],
            lambda: _raise_route(REFUSAL_IDS[4], "prefix is not maximal"),
        ),
        "event_target_quality_timing_channel_or_outcome_read_attempt": (
            REFUSAL_IDS[5],
            _reject_forbidden_content_operation,
        ),
        "local_header_member_payload_archive_or_network_open_attempt": (
            REFUSAL_IDS[2],
            _reject_payload_operation,
        ),
        "public_member_offset_CRC_URL_path_raw_row_or_header_leak": (
            REFUSAL_IDS[5],
            lambda: _walk_public({"member_name": "private"}),
        ),
        "private_aggregate_schema_confusion_or_mode_mismatch": (
            REFUSAL_IDS[5],
            lambda: _assert_private_mode(0o644, PRIVATE_SCHEMA_NAME),
        ),
        "output_symlink_overwrite_cap_cleanup_or_replay_mismatch": (
            REFUSAL_IDS[5],
            lambda: _bounded_output_bytes(b"x" * (MAX_PUBLIC_OUTPUT_BYTES + 1), b""),
        ),
    }
    if tuple(checks) != REQUIRED_MUTATIONS:
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[5], "mutation implementation order differs"
        )
    outcomes = {
        name: _expect_refusal(name, expected, operation)
        for name, (expected, operation) in checks.items()
    }
    if source_sha256 != _sha256_bytes(_canonical_manifest_bytes(manifest)):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "fixture mutated in place")
    return outcomes


def exercise_boundary_profiles(
    *,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Mapping[str, Any]]:
    """Exercise the four frozen generated storage boundaries."""

    registered = dict(contract or load_registered_contract())
    floor = select_generated_prefix(
        build_generated_manifest(profile="floor", contract=registered),
        contract=registered,
    )
    all19 = select_generated_prefix(
        build_generated_manifest(profile="all19", contract=registered),
        contract=registered,
    )
    exact = select_generated_prefix(
        build_generated_manifest(profile="exact_cap", contract=registered),
        contract=registered,
    )
    cap_plus_route = _expect_refusal(
        "cap_plus_one_boundary",
        REFUSAL_IDS[4],
        lambda: select_generated_prefix(
            build_generated_manifest(profile="cap_plus_one", contract=registered),
            contract=registered,
        ),
    )
    if floor.cohort_summary["selected_subjects"] != 12:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[4], "floor profile differs")
    if all19.cohort_summary["selected_subjects"] != 19:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[4], "all-19 profile differs")
    if (
        exact.cohort_summary["selected_subjects"] != 12
        or exact.byte_summary["selected_reservation_bytes"] != RESERVATION_CAP_BYTES
    ):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[4], "exact-cap profile differs")
    return {
        "floor_12": {
            "selected_subjects": 12,
            "selected_reservation_bytes": floor.byte_summary["selected_reservation_bytes"],
            "passed": True,
        },
        "all_19": {
            "selected_subjects": 19,
            "selected_reservation_bytes": all19.byte_summary["selected_reservation_bytes"],
            "passed": True,
        },
        "exact_cap": {
            "selected_subjects": 12,
            "selected_reservation_bytes": exact.byte_summary["selected_reservation_bytes"],
            "passed": True,
        },
        "cap_plus_one": {
            "refusal_route": cap_plus_route,
            "passed": True,
        },
    }


def _assert_resources(runtime_seconds: float, peak_rss_bytes: int) -> None:
    if runtime_seconds > MAX_RUNTIME_SECONDS:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "runtime exceeds cap")
    if peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "peak RSS exceeds cap")
    for key in THREAD_ENV_KEYS:
        if os.environ.get(key) not in {None, "1"}:
            raise FreewillPrefixSelectionRefusal(
                REFUSAL_IDS[5], "numerical thread setting exceeds one"
            )


def _assert_output_destination(output_dir: Path) -> None:
    if output_dir.exists() or output_dir.is_symlink():
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[5], "output directory already exists"
        )
    parent = output_dir.parent
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[5], "output parent is unavailable"
        )
    if stat.S_ISLNK(os.lstat(parent).st_mode):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "output parent is a symlink")


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
        report_path = stage / "marc2_freewill_prefix_selection_report.v0.json"
        private_path = stage / "marc2_freewill_prefix_selection.private.v0.json"
        report_path.write_bytes(report_bytes)
        private_path.write_bytes(private_bytes)
        private_path.chmod(0o600)
        os.replace(stage, output_dir)
    except Exception as exc:
        shutil.rmtree(stage, ignore_errors=True)
        if isinstance(exc, FreewillPrefixSelectionRefusal):
            raise
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "output write failed") from exc
    final_report = output_dir / "marc2_freewill_prefix_selection_report.v0.json"
    final_private = output_dir / "marc2_freewill_prefix_selection.private.v0.json"
    if stat.S_IMODE(final_private.stat().st_mode) != 0o600:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "private mode differs")
    return final_report, final_private, total


def _build_report(
    selection: SelectionResult,
    mutations: Mapping[str, str],
    boundaries: Mapping[str, Mapping[str, Any]],
    *,
    generated_input_bytes: int,
    generated_output_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    return {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_freewill_prefix_selection_qualification",
        "proof_posture": "generated_ZIP_directory_metadata_only_no_scientific_value",
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
        "boundary_summary": {key: dict(value) for key, value in boundaries.items()},
        "measurements": {
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes": generated_output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "fixture_rows": EXPECTED_ROWS,
            "eligible_subjects": EXPECTED_ELIGIBLE_SUBJECTS,
            "candidate_run_bundles": EXPECTED_CANDIDATE_RUN_BUNDLES,
            "candidate_core_members": EXPECTED_CANDIDATE_CORE_MEMBERS,
            "selected_private_rows": selection.split_summary["selected_core_members"],
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
            "private_inventory_path_operations": 0,
            "private_inventory_opens": 0,
            "private_inventory_bytes": 0,
            "real_participant_selections": 0,
            "real_member_selections": 0,
            "network_requests": 0,
            "network_bytes": 0,
            "archive_local_header_or_member_payload_reads": 0,
            "signal_sample_reads": 0,
            "event_target_label_quality_onset_or_channel_reads": 0,
            "real_derivative_rows": 0,
            "training_or_parameter_update_fits": 0,
            "model_inference_or_prediction_sets": 0,
            "prediction_freezes_target_deliveries_or_scores": 0,
            "provider_or_language_model_calls": 0,
            "hardware_operations": 0,
            "old_consumed_root_operations": 0,
            "retries_reruns_or_resumes": 0,
            "scientific_claim_upgrades": 0,
        },
        "acceptance_gates": {
            "green_MARC2_research_and_artifact_bindings": True,
            "exact_19_subject_preserved_rank": True,
            "exact_1227_rows_114_bundles_and_456_members": True,
            "main_fixture_maximal_16_subject_prefix": True,
            "main_fixture_96_bundles_and_384_members": True,
            "equal_fit_and_heldout_bundle_counts": True,
            "floor_all19_exactcap_and_capplus1_boundaries": True,
            "row_order_size_and_CRC_selection_invariants": True,
            "zero_skip_substitution_later_session_or_backfill": True,
            "zero_content_signal_event_target_quality_model_or_score_interface": True,
            "all_40_mutations_refused_in_frozen_class": True,
            "private_and_aggregate_output_separation": True,
            "byte_identical_deterministic_replay": True,
            "runtime_RSS_output_cleanup_and_one_thread_caps": True,
            "all_private_real_neural_target_model_score_provider_retry_and_claim_counters_zero": True,
        },
        "route": EXPECTED_ROUTE,
        "warnings": [
            "All 1,227 inventory rows are generated fixtures with no human content.",
            "The public participant rank is frozen, but no retained private row was read.",
            "Generated sizes and CRC declarations do not verify a real archive member.",
            "No local header payload signal event target quality model prediction or score was accessed.",
            "End-to-end neural decoding latency was not measured.",
        ],
        "unavailable_fields": [
            "real selected member identities offsets sizes and integrity",
            "real selected participant count and byte reservation",
            "channel geometry signal quality events targets and movement onsets",
            "neural features predictions scores and latency",
            "language decoding or thought-to-text evidence",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A generated selector maximizes a target-free session-held-out participant "
                "prefix under an exact storage ceiling without outcome selection."
            ),
            "scientific_claim_not_established": (
                "Generated ZIP-directory metadata contain no human neural signal prediction "
                "or score and establish no neural effect decoding or thought-to-text result."
            ),
        },
    }


def validate_public_report(
    report: Mapping[str, Any],
    *,
    allow_incomplete_measurements: bool = False,
) -> None:
    """Validate an aggregate generated qualification report."""

    if set(report) != PUBLIC_REPORT_FIELDS:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "public fields differ")
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("status")
        != "passed_generated_freewill_prefix_selection_qualification"
        or report.get("route") != EXPECTED_ROUTE
    ):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "public identity differs")
    _walk_public(report)
    counters = report.get("access_counters")
    gates = report.get("acceptance_gates")
    mutations = report.get("mutation_summary")
    boundaries = report.get("boundary_summary")
    if not isinstance(counters, dict) or any(counters.values()):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "access counter is nonzero")
    if not isinstance(gates, dict) or len(gates) != 15 or not all(gates.values()):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "acceptance gate differs")
    if not isinstance(mutations, dict) or mutations.get("passed_count") != 40:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "mutation summary differs")
    if (
        not isinstance(boundaries, dict)
        or set(boundaries) != {"floor_12", "all_19", "exact_cap", "cap_plus_one"}
        or not all(value.get("passed") is True for value in boundaries.values())
    ):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "boundary summary differs")
    measurements = report.get("measurements")
    if not isinstance(measurements, dict):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "measurements unavailable")
    if not allow_incomplete_measurements:
        if measurements.get("generated_output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1) > MAX_COMBINED_OUTPUT_BYTES:
            raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "output exceeds cap")
        if measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1) > MAX_RUNTIME_SECONDS:
            raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "runtime exceeds cap")
        if measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1) > MAX_PEAK_RSS_BYTES:
            raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "RSS exceeds cap")


def qualify_generated_prefix_selection(
    output_dir: str | Path,
    *,
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run one bounded generated qualification and atomically write outputs."""

    destination = Path(output_dir)
    _assert_output_destination(destination)
    start = clock()
    contract = load_registered_contract()
    main = build_generated_manifest(contract=contract)
    replay_manifest = build_generated_manifest(row_order="reversed", contract=contract)
    first = select_generated_prefix(main, contract=contract)
    replay = select_generated_prefix(replay_manifest, contract=contract)
    if _canonical_json_bytes(first.private_manifest) != _canonical_json_bytes(
        replay.private_manifest
    ):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "private replay differs")
    if first.selection_hashes != replay.selection_hashes:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "aggregate replay differs")
    if (
        first.cohort_summary["selected_subjects"] != EXPECTED_MAIN_SUBJECTS
        or first.split_summary["selected_run_bundles"] != EXPECTED_MAIN_RUN_BUNDLES
        or first.split_summary["selected_core_members"] != EXPECTED_MAIN_CORE_MEMBERS
    ):
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[4], "main fixture differs")
    boundaries = exercise_boundary_profiles(contract=contract)
    mutations = run_required_mutations(main, contract=contract)
    runtime_seconds = clock() - start
    peak_rss_bytes = rss_probe()
    _assert_resources(runtime_seconds, peak_rss_bytes)
    generated_manifests = [main, replay_manifest]
    generated_input_bytes = sum(
        len(_canonical_json_bytes(manifest)) for manifest in generated_manifests
    )
    report = _build_report(
        first,
        mutations,
        boundaries,
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
        raise FreewillPrefixSelectionRefusal(
            REFUSAL_IDS[5], "output measurement did not stabilize"
        )
    validate_public_report(report)
    report_path, private_path, written_total = _write_outputs(
        destination, report, first.private_manifest
    )
    if written_total != report["measurements"]["generated_output_bytes"]:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "written bytes differ")
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
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "report unavailable")
    if report_path.stat().st_size > MAX_PUBLIC_OUTPUT_BYTES:
        raise FreewillPrefixSelectionRefusal(REFUSAL_IDS[5], "report exceeds cap")
    report = _strict_json(report_path.read_bytes())
    validate_public_report(report)
    return {
        "route": report["route"],
        "selected_subjects": report["cohort_summary"]["selected_subjects"],
        "selected_subject_ids": list(report["cohort_summary"]["selected_subject_ids"]),
        "selected_run_bundles": report["split_summary"]["selected_run_bundles"],
        "selected_core_members": report["split_summary"]["selected_core_members"],
        "selected_reservation_bytes": report["byte_summary"]["selected_reservation_bytes"],
        "reservation_cap_bytes": report["byte_summary"]["reservation_cap_bytes"],
        "boundary_profiles_passed": sum(
            value["passed"] for value in report["boundary_summary"].values()
        ),
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
        "lane_id": "MARC2-FW1",
        "contract_sha256": CONTRACT_SHA256,
        "green_contract_commit": GREEN_CONTRACT_COMMIT,
        "green_contract_CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
        "generated_commands": list(contract["interface"]["generated_commands"]),
        "fixture_rows": EXPECTED_ROWS,
        "eligible_subjects": EXPECTED_ELIGIBLE_SUBJECTS,
        "minimum_subjects": MINIMUM_SUBJECTS,
        "maximum_subjects": MAXIMUM_SUBJECTS,
        "expected_main_subjects": EXPECTED_MAIN_SUBJECTS,
        "expected_main_run_bundles": EXPECTED_MAIN_RUN_BUNDLES,
        "expected_main_core_members": EXPECTED_MAIN_CORE_MEMBERS,
        "reservation_cap_bytes": RESERVATION_CAP_BYTES,
        "required_mutations": len(REQUIRED_MUTATIONS),
        "boundary_profiles": 4,
        "combined_output_cap_bytes": MAX_COMBINED_OUTPUT_BYTES,
        "real_private_or_network_operations_authorized": 0,
        "signal_target_model_or_score_operations_authorized": 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_freewill_prefix_selection",
        description="Qualify the generated-only MARC2-FW1 prefix selector.",
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
            outcome = qualify_generated_prefix_selection(args.output_dir)
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
    except FreewillPrefixSelectionRefusal as exc:
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
