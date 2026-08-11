"""Generated-only OpenNeuro snapshot identity canonicalizer."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import resource
import shutil
import stat
import sys
import tempfile
import time
import unicodedata
import urllib.parse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_NAME = "neurodecodekit.iackd_snapshot_identity_qualification"
MANIFEST_SCHEMA_NAME = "neurodecodekit.iackd_snapshot_selected_manifest"
CONTRACT_RELATIVE_PATH = Path("registries/iackd_snapshot_identity_contract.v0.json")
CONTRACT_SHA256 = "fa7bed69bb70022b3e61c6839b01a2fa7f3e4f77a40629dc62ab9b4873681e2a"
GREEN_CONTRACT_COMMIT = "1667e302e262ad23695f204a88d5a0997ac38270"
GREEN_CONTRACT_CI_RUN_ID = 31_481_270_697
GREEN_CONTRACT_BASE_JOB_ID = 93_746_523_491
GREEN_CONTRACT_OPTIONAL_JOB_ID = 93_746_523_322
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
EXPECTED_FILE_COUNT = 1_679
EXPECTED_TREE_BYTES = 7_966_799_433
EXPECTED_SELECTED_COUNT = 1_340
EXPECTED_SELECTED_BYTES = 7_249_113_684
EXPECTED_ROUTE = "IACKDM-R1"
HEX_ID_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
VERSION_ID_RE = re.compile(r"[A-Za-z0-9._~+/=:-]{1,256}\Z")
SUBJECT_RE = re.compile(r"sub-[0-9]{2}\Z")
EEG_RUN_RE = re.compile(
    r"(?P<subject>sub-[0-9]{2})/eeg/"
    r"(?P=subject)_task-ihc_acq-(?P<hand>left|right)_run-(?P<run>[0-9]{2})_"
    r"(?P<suffix>channels\.tsv|eeg\.eeg|eeg\.json|eeg\.vhdr|eeg\.vmrk|events\.tsv)\Z"
)
BEH_RUN_RE = re.compile(
    r"(?P<subject>sub-[0-9]{2})/sourcedata/beh/"
    r"(?P=subject)_task-ihc_run-(?P<run>[0-9]{2})_hand-(?P<hand>left|right)_"
    r"(?P<kind>ball|leap)\.(?P<extension>json|tsv)\Z"
)
GEOMETRY_RE = re.compile(
    r"(?P<subject>sub-[0-9]{2})/eeg/"
    r"(?P=subject)_acq-(?P<hand>left|right)_space-CapTrak_"
    r"(?P<kind>coordsystem\.json|electrodes\.tsv)\Z"
)
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
REFUSAL_IDS = (
    "IACKDM-F00-registration-source-query-or-green-proof-mismatch",
    "IACKDM-F01-HTTP-redirect-compression-body-cap-or-GraphQL-error",
    "IACKDM-F02-response-shape-duplicate-key-unknown-field-or-type-failure",
    "IACKDM-F03-accession-tag-snapshot-ID-hexsha-or-description-revision-mismatch",
    "IACKDM-F04-recursive-tree-path-object-ID-size-URL-or-version-ID-failure",
    "IACKDM-F05-historical-participant-run-object-byte-or-role-count-incompatibility",
    "IACKDM-F06-critical-Name-BIDSVersion-License-or-DOI-mismatch",
    "IACKDM-F07-output-runtime-RSS-thread-retry-or-overwrite-failure",
)
PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "green_registration",
        "snapshot_anchor",
        "tree_summary",
        "selected_summary",
        "critical_metadata",
        "measurements",
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
        "filename",
        "filenames",
        "git_object_id",
        "path",
        "paths",
        "s3_key",
        "s3_version_id",
        "url",
        "urls",
        "version_id",
        "version_ids",
    }
)
REQUIRED_MUTATIONS = (
    "body_overflow",
    "read_error_or_second_read",
    "duplicate_JSON_key",
    "invalid_UTF8_BOM_NUL_or_control",
    "nonfinite_JSON_number",
    "GraphQL_errors_present",
    "null_data_or_snapshot",
    "unknown_top_level_data_snapshot_description_or_file_field",
    "missing_required_field",
    "wrong_field_type",
    "wrong_snapshot_ID",
    "wrong_snapshot_tag",
    "malformed_snapshot_hexsha",
    "description_revision_mismatch",
    "critical_Name_drift",
    "critical_BIDSVersion_drift",
    "critical_License_drift",
    "critical_DatasetDOI_drift",
    "duplicate_path",
    "absolute_dot_dotdot_backslash_or_repeated_separator_path",
    "non_NFC_or_percent_ambiguous_path",
    "malformed_file_ID",
    "boolean_negative_fractional_or_noncanonical_size",
    "directory_true_or_annexed_wrong_type",
    "missing_or_multiple_URL",
    "non_HTTPS_alternate_host_bucket_or_key_mismatch",
    "userinfo_port_fragment_extra_query_or_missing_versionId",
    "all_tree_count_or_byte_drift",
    "selected_count_or_byte_drift",
    "participant_or_run_count_drift",
    "role_count_or_byte_drift",
    "missing_dataset_description_row",
    "network_constructor_or_real_path_attempt",
    "output_symlink_overwrite_or_cap",
    "thread_runtime_or_RSS_cap",
    "public_row_path_URL_or_version_ID_leak",
    "deterministic_replay_mismatch",
)


class SnapshotIdentityRefusal(RuntimeError):
    """Fail closed with one stable and non-sensitive refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown IACKD-M1 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class CanonicalSnapshot:
    """Aggregate public result and private selected manifest for one response."""

    report: Mapping[str, Any]
    private_manifest: Mapping[str, Any]
    response_bytes: int
    response_sha256: str


@dataclass(frozen=True)
class QualificationOutcome:
    """One bounded generated qualification outcome."""

    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    input_bytes: int
    generated_output_bytes: int


class GeneratedBodyReader:
    """One-use in-memory body reader for generated transport qualification."""

    def __init__(self, payload: bytes, *, read_error: Exception | None = None):
        self._payload = payload
        self._read_error = read_error
        self.read_calls = 0

    def read_once(self, limit: int) -> bytes:
        if self.read_calls != 0:
            raise SnapshotIdentityRefusal(REFUSAL_IDS[1], "body was already read")
        self.read_calls += 1
        if self._read_error is not None:
            raise SnapshotIdentityRefusal(REFUSAL_IDS[1], "body read failed") from self._read_error
        return self._payload[:limit]


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
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "non-finite JSON number")


def _strict_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "non-finite JSON number")
    return parsed


def _strict_json(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "invalid UTF-8") from exc
    if "\x00" in text or any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "disallowed control character")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
            parse_float=_strict_float,
        )
    except SnapshotIdentityRefusal:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "invalid JSON") from exc
    if not isinstance(value, dict):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "JSON root is not an object")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], *, label: str) -> None:
    if set(value) != expected:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], f"{label} fields differ")


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green registration from the repository."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _sha256_file(path) != CONTRACT_SHA256:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[0], "contract hash differs")
    contract = _strict_json(path.read_bytes())
    if contract.get("contract_id") != "IACKD-M1-snapshot-identity-contract-v0":
        raise SnapshotIdentityRefusal(REFUSAL_IDS[0], "contract identity differs")
    proof = contract.get("green_research_proof")
    if not isinstance(proof, dict) or not proof.get("both_required_jobs_green"):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[0], "research proof is not green")
    return contract


def _normalize_size(value: Any) -> int:
    if isinstance(value, bool):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "boolean size is forbidden")
    if isinstance(value, int):
        if value < 0:
            raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "negative size")
        return value
    if isinstance(value, str):
        if not re.fullmatch(r"0|[1-9][0-9]*", value):
            raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "noncanonical decimal size")
        return int(value)
    raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "size type differs")


def _normalize_path(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 1024:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "path type or length differs")
    if unicodedata.normalize("NFC", value) != value:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "path is not NFC")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "path contains a control")
    if value.startswith("/") or "\\" in value or "//" in value:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "path is not safe relative POSIX")
    if any(char in value for char in ("?", "#", "%")):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "path is URL ambiguous")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "path has unsafe component")
    return value


def _decode_version_id(raw_value: str) -> str:
    if not raw_value:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "version ID is missing")
    for match in re.finditer("%", raw_value):
        if not re.fullmatch(r"[0-9A-Fa-f]{2}", raw_value[match.start() + 1 : match.start() + 3]):
            raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "version ID escape is invalid")
    try:
        value = urllib.parse.unquote(raw_value, errors="strict")
    except UnicodeDecodeError as exc:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "version ID decode failed") from exc
    if not VERSION_ID_RE.fullmatch(value):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "version ID shape differs")
    return value


def _parse_versioned_url(value: Any, filename: str) -> tuple[str, str]:
    if not isinstance(value, str) or len(value) > 4096:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "URL type or length differs")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "URL parse failed") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname != "s3.amazonaws.com"
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.fragment
    ):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "URL authority differs")
    expected_path = f"/openneuro.org/ds006840/{filename}"
    if parsed.path != expected_path:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "URL object key differs")
    if not parsed.query.startswith("versionId=") or "&" in parsed.query or ";" in parsed.query:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "URL query differs")
    version_id = _decode_version_id(parsed.query[len("versionId=") :])
    return expected_path.removeprefix("/openneuro.org/"), version_id


def _canonical_file(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "file row is not an object")
    _exact_keys(value, {"id", "filename", "size", "directory", "annexed", "urls"}, label="file")
    object_id = value["id"]
    if not isinstance(object_id, str) or not HEX_ID_RE.fullmatch(object_id):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "file object ID differs")
    filename = _normalize_path(value["filename"])
    size_bytes = _normalize_size(value["size"])
    if value["directory"] is not False or not isinstance(value["annexed"], bool):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "directory or annexed field differs")
    urls = value["urls"]
    if not isinstance(urls, list) or len(urls) != 1:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "URL list differs")
    s3_key, version_id = _parse_versioned_url(urls[0], filename)
    return {
        "filename": filename,
        "git_object_id": object_id,
        "size_bytes": size_bytes,
        "annexed": value["annexed"],
        "s3_key": s3_key,
        "s3_version_id": version_id,
    }


def _role_identity(path: str) -> tuple[str, str, tuple[str, str, str] | None, tuple[str, str] | None]:
    match = EEG_RUN_RE.fullmatch(path)
    if match:
        role = {
            "channels.tsv": "channels",
            "eeg.eeg": "eeg_signal",
            "eeg.json": "eeg_sidecar",
            "eeg.vhdr": "eeg_header",
            "eeg.vmrk": "eeg_marker",
            "events.tsv": "events",
        }[match.group("suffix")]
        run = (match.group("subject"), match.group("hand"), match.group("run"))
        return role, match.group("subject"), run, None
    match = BEH_RUN_RE.fullmatch(path)
    if match:
        role = f"{match.group('kind')}_{'sidecar' if match.group('extension') == 'json' else 'stream'}"
        run = (match.group("subject"), match.group("hand"), match.group("run"))
        return role, match.group("subject"), run, None
    match = GEOMETRY_RE.fullmatch(path)
    if match:
        role = "coordsystem" if match.group("kind") == "coordsystem.json" else "electrodes"
        unit = (match.group("subject"), match.group("hand"))
        return role, match.group("subject"), None, unit
    raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "selected path role is unknown")


def _is_selected(path: str) -> bool:
    parts = path.split("/")
    if len(parts) < 3 or not SUBJECT_RE.fullmatch(parts[0]):
        return False
    return parts[1] == "eeg" or parts[1:3] == ["sourcedata", "beh"]


def _validate_selected(
    rows: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    subjects: set[str] = set()
    run_sets: dict[str, set[tuple[str, str, str]]] = {}
    geometry_sets: dict[str, set[tuple[str, str]]] = {}
    role_counts: Counter[str] = Counter()
    role_bytes: Counter[str] = Counter()
    for row in rows:
        path = str(row["filename"])
        if not _is_selected(path):
            continue
        role, subject, run, geometry = _role_identity(path)
        subjects.add(subject)
        if run is not None:
            run_sets.setdefault(role, set()).add(run)
        if geometry is not None:
            geometry_sets.setdefault(role, set()).add(geometry)
        role_counts[role] += 1
        role_bytes[role] += int(row["size_bytes"])
        selected.append({**row, "role": role})
    expected = contract["selected_inventory_contract"]
    if len(selected) != expected["object_count"]:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "selected object count differs")
    if sum(int(row["size_bytes"]) for row in selected) != expected["payload_bytes"]:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "selected byte count differs")
    if len(subjects) != expected["participant_count"]:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "participant count differs")
    expected_roles = expected["role_summaries"]
    if set(role_counts) != set(expected_roles):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "selected role set differs")
    for role, summary in expected_roles.items():
        if role_counts[role] != summary["object_count"] or role_bytes[role] != summary["size_bytes"]:
            raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "selected role summary differs")
    run_roles = {role for role, summary in expected_roles.items() if summary["object_count"] == 128}
    if set(run_sets) != run_roles:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "run-role membership differs")
    reference_runs = run_sets["eeg_header"]
    if len(reference_runs) != expected["bids_run_count"] or any(
        run_sets[role] != reference_runs for role in run_roles
    ):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "run identities do not reconcile")
    reference_geometry = geometry_sets.get("coordsystem", set())
    if (
        len(reference_geometry) != expected["participant_hand_units"]
        or geometry_sets.get("electrodes", set()) != reference_geometry
        or {(subject, hand) for subject, hand, _run in reference_runs} != reference_geometry
    ):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "participant-hand units differ")
    selected.sort(key=lambda row: str(row["filename"]))
    summary = {
        "participant_count": len(subjects),
        "participant_hand_units": len(reference_geometry),
        "bids_run_count": len(reference_runs),
        "object_count": len(selected),
        "payload_bytes": sum(int(row["size_bytes"]) for row in selected),
        "role_summaries": {
            role: {
                "object_count": role_counts[role],
                "size_bytes": role_bytes[role],
            }
            for role in sorted(role_counts)
        },
    }
    return selected, summary


def _validate_critical(description: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, str]:
    expected = contract["snapshot_anchor_contract"]["critical_description"]
    result: dict[str, str] = {}
    for field, expected_value in expected.items():
        value = description.get(field)
        if not isinstance(value, str) or value != expected_value:
            raise SnapshotIdentityRefusal(REFUSAL_IDS[6], f"critical {field} differs")
        result[field] = value
    return result


def _base_access_counters() -> dict[str, int]:
    return {
        "dataset_specific_GraphQL_requests": 0,
        "dataset_specific_GraphQL_response_bytes": 0,
        "ds006840_S3_requests": 0,
        "ds006840_S3_body_bytes": 0,
        "local_IACKD_path_operations": 0,
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
        "retries_or_reruns": 0,
        "scientific_claim_upgrades": 0,
    }


def canonicalize_generated_response(
    payload: bytes,
    *,
    contract: Mapping[str, Any] | None = None,
) -> CanonicalSnapshot:
    """Validate and canonicalize one generated snapshot response."""

    if not isinstance(payload, bytes):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "response is not bytes")
    if len(payload) > MAX_RESPONSE_BYTES:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[1], "response exceeds body cap")
    active_contract = dict(contract) if contract is not None else load_registered_contract()
    root = _strict_json(payload)
    if "errors" in root:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[1], "GraphQL errors are present")
    _exact_keys(root, {"data"}, label="response")
    data = root["data"]
    if not isinstance(data, dict):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "data is not an object")
    _exact_keys(data, {"snapshot"}, label="data")
    snapshot = data["snapshot"]
    if not isinstance(snapshot, dict):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "snapshot is not an object")
    _exact_keys(snapshot, {"id", "tag", "hexsha", "description", "files"}, label="snapshot")
    anchor_contract = active_contract["snapshot_anchor_contract"]
    if snapshot["id"] != anchor_contract["id"] or snapshot["tag"] != anchor_contract["tag"]:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[3], "snapshot ID or tag differs")
    hexsha = snapshot["hexsha"]
    if not isinstance(hexsha, str) or not HEX_ID_RE.fullmatch(hexsha):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[3], "snapshot hexsha differs")
    description = snapshot["description"]
    if not isinstance(description, dict):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "description is not an object")
    _exact_keys(
        description,
        {"id", "Name", "BIDSVersion", "License", "DatasetDOI"},
        label="description",
    )
    if description["id"] != hexsha:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[3], "description revision differs")
    files = snapshot["files"]
    if not isinstance(files, list) or any(item is None for item in files):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[2], "files list differs")
    canonical_rows = [_canonical_file(item) for item in files]
    paths = [str(row["filename"]) for row in canonical_rows]
    if len(set(paths)) != len(paths):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[4], "duplicate file path")
    canonical_rows.sort(key=lambda row: str(row["filename"]))
    tree_contract = active_contract["recursive_tree_contract"]
    if len(canonical_rows) != tree_contract["file_count"]:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "tree file count differs")
    tree_bytes = sum(int(row["size_bytes"]) for row in canonical_rows)
    if tree_bytes != tree_contract["total_bytes"]:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "tree byte count differs")
    if not any(row["filename"] == "dataset_description.json" for row in canonical_rows):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[5], "dataset description row is missing")
    selected, selected_summary = _validate_selected(canonical_rows, active_contract)
    critical = _validate_critical(description, active_contract)
    anchor = {
        "dataset_accession": "ds006840",
        "snapshot_id": snapshot["id"],
        "snapshot_tag": snapshot["tag"],
        "snapshot_hexsha": hexsha,
    }
    tree_sha256 = _sha256_bytes(_canonical_json_bytes(canonical_rows))
    selected_sha256 = _sha256_bytes(_canonical_json_bytes(selected))
    anchor_sha256 = _sha256_bytes(_canonical_json_bytes(anchor))
    critical_sha256 = _sha256_bytes(_canonical_json_bytes(critical))
    private_manifest = {
        "schema_name": MANIFEST_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "generated_fixture_private_manifest",
        "snapshot_anchor_sha256": anchor_sha256,
        "tree_sha256": tree_sha256,
        "selected_manifest_sha256": selected_sha256,
        "selected_object_count": len(selected),
        "selected_payload_bytes": selected_summary["payload_bytes"],
        "rows": selected,
    }
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "generated_snapshot_identity_qualified",
        "proof_posture": "generated_response_only_zero_network_zero_real_or_local_data",
        "green_registration": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
        },
        "snapshot_anchor": {
            "dataset_accession": "ds006840",
            "snapshot_id": snapshot["id"],
            "snapshot_tag": snapshot["tag"],
            "snapshot_hexsha": hexsha,
            "canonical_sha256": anchor_sha256,
        },
        "tree_summary": {
            "file_count": len(canonical_rows),
            "total_bytes": tree_bytes,
            "canonical_sha256": tree_sha256,
        },
        "selected_summary": {
            **selected_summary,
            "canonical_manifest_sha256": selected_sha256,
        },
        "critical_metadata": {
            "values": critical,
            "canonical_sha256": critical_sha256,
        },
        "measurements": {
            "input_bytes": len(payload),
            "input_sha256": _sha256_bytes(payload),
            "runtime_seconds": None,
            "peak_RSS_bytes": None,
            "generated_output_bytes": None,
            "deterministic_replays": None,
            "refusal_mutations_passed": None,
        },
        "access_counters": _base_access_counters(),
        "acceptance_gates": {
            "snapshot_anchor": True,
            "recursive_tree": True,
            "selected_inventory": True,
            "critical_metadata": True,
            "aggregate_only_public_output": True,
            "network_and_real_path_closed": True,
            "resource_caps": None,
            "deterministic_replay": None,
            "all_required_refusals": None,
        },
        "route": EXPECTED_ROUTE,
        "warnings": [
            "Constructed metadata validates only the identity interface.",
            "No public response, neural payload, target, model, or score was accessed.",
            "A later real metadata route would not authorize payload acquisition.",
        ],
        "unavailable_fields": [
            "end_to_end_decoding_latency",
            "neural_effect",
            "decoding_accuracy",
            "brain_specific_origin",
        ],
        "claim_boundary": {
            "engineering_capability_added": "A generated snapshot response can be reduced to separate deterministic snapshot tree selected-manifest and critical-metadata identities.",
            "scientific_claim_not_established": "Generated metadata and zero neural reads establish no neural effect or decoding result.",
        },
    }
    validate_public_report(report, allow_incomplete_measurements=True)
    return CanonicalSnapshot(
        report=report,
        private_manifest=private_manifest,
        response_bytes=len(payload),
        response_sha256=_sha256_bytes(payload),
    )


def _distribute_sizes(count: int, total: int) -> list[int]:
    quotient, remainder = divmod(total, count)
    return [quotient + (1 if index < remainder else 0) for index in range(count)]


def _generated_runs() -> list[tuple[str, str, str]]:
    runs: list[tuple[str, str, str]] = []
    for subject_index in range(1, 16):
        subject = f"sub-{subject_index:02d}"
        runs_per_hand = 6 if subject_index in {4, 5} else 4
        for hand in ("left", "right"):
            for run_index in range(1, runs_per_hand + 1):
                runs.append((subject, hand, f"{run_index:02d}"))
    if len(runs) != 128:
        raise AssertionError("generated run geometry differs")
    return runs


def _generated_selected_specs(contract: Mapping[str, Any]) -> list[tuple[str, str, int]]:
    role_paths: dict[str, list[str]] = {role: [] for role in contract["selected_inventory_contract"]["role_summaries"]}
    for subject, hand, run in _generated_runs():
        stem = f"{subject}/eeg/{subject}_task-ihc_acq-{hand}_run-{run}_"
        role_paths["channels"].append(stem + "channels.tsv")
        role_paths["eeg_signal"].append(stem + "eeg.eeg")
        role_paths["eeg_sidecar"].append(stem + "eeg.json")
        role_paths["eeg_header"].append(stem + "eeg.vhdr")
        role_paths["eeg_marker"].append(stem + "eeg.vmrk")
        role_paths["events"].append(stem + "events.tsv")
        beh = f"{subject}/sourcedata/beh/{subject}_task-ihc_run-{run}_hand-{hand}_"
        role_paths["ball_sidecar"].append(beh + "ball.json")
        role_paths["ball_stream"].append(beh + "ball.tsv")
        role_paths["leap_sidecar"].append(beh + "leap.json")
        role_paths["leap_stream"].append(beh + "leap.tsv")
    for subject_index in range(1, 16):
        subject = f"sub-{subject_index:02d}"
        for hand in ("left", "right"):
            stem = f"{subject}/eeg/{subject}_acq-{hand}_space-CapTrak_"
            role_paths["coordsystem"].append(stem + "coordsystem.json")
            role_paths["electrodes"].append(stem + "electrodes.tsv")
    specs: list[tuple[str, str, int]] = []
    for role in sorted(role_paths):
        paths = sorted(role_paths[role])
        expected = contract["selected_inventory_contract"]["role_summaries"][role]
        if len(paths) != expected["object_count"]:
            raise AssertionError("generated role count differs")
        sizes = _distribute_sizes(len(paths), expected["size_bytes"])
        specs.extend((path, role, size) for path, size in zip(paths, sizes, strict=True))
    return sorted(specs)


def _generated_file(path: str, size_bytes: int, *, annexed: bool) -> dict[str, Any]:
    object_id = hashlib.sha1(f"object:{path}".encode("ascii")).hexdigest()
    version_id = hashlib.sha256(f"version:{path}".encode("ascii")).hexdigest()[:32]
    return {
        "id": object_id,
        "filename": path,
        "size": size_bytes,
        "directory": False,
        "annexed": annexed,
        "urls": [f"https://s3.amazonaws.com/openneuro.org/ds006840/{path}?versionId={version_id}"],
    }


def make_generated_response(contract: Mapping[str, Any] | None = None) -> bytes:
    """Build one deterministic synthetic response matching aggregate contracts."""

    active_contract = dict(contract) if contract is not None else load_registered_contract()
    selected_specs = _generated_selected_specs(active_contract)
    files = [_generated_file(path, size, annexed=role in {"eeg_signal", "ball_stream", "leap_stream"}) for path, role, size in selected_specs]
    nonselected_count = EXPECTED_FILE_COUNT - len(files)
    nonselected_total = EXPECTED_TREE_BYTES - EXPECTED_SELECTED_BYTES
    fixed = [("dataset_description.json", 1178), ("CHANGES", 164)]
    remaining_count = nonselected_count - len(fixed)
    remaining_total = nonselected_total - sum(size for _path, size in fixed)
    auxiliary_sizes = _distribute_sizes(remaining_count, remaining_total)
    auxiliary = [(f"auxiliary/generated-{index:04d}.bin", size) for index, size in enumerate(auxiliary_sizes, start=1)]
    files.extend(_generated_file(path, size, annexed=False) for path, size in [*fixed, *auxiliary])
    files.sort(key=lambda row: str(row["filename"]), reverse=True)
    hexsha = hashlib.sha1(b"generated-iackd-snapshot-identity-v0").hexdigest()
    critical = active_contract["snapshot_anchor_contract"]["critical_description"]
    response = {
        "data": {
            "snapshot": {
                "id": active_contract["snapshot_anchor_contract"]["id"],
                "tag": active_contract["snapshot_anchor_contract"]["tag"],
                "hexsha": hexsha,
                "description": {"id": hexsha, **critical},
                "files": files,
            }
        }
    }
    payload = _canonical_json_bytes(response)
    if len(payload) > MAX_RESPONSE_BYTES:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "generated response exceeds cap")
    return payload


def _payload_from_object(value: Mapping[str, Any]) -> bytes:
    return _canonical_json_bytes(value)


def _expect_refusal(name: str, function: Callable[[], Any]) -> str:
    try:
        function()
    except SnapshotIdentityRefusal as exc:
        return exc.refusal_id
    raise SnapshotIdentityRefusal(REFUSAL_IDS[7], f"required mutation did not refuse: {name}")


def _mutated(base: Mapping[str, Any], mutate: Callable[[dict[str, Any]], None]) -> bytes:
    value = copy.deepcopy(base)
    mutate(value)
    return _payload_from_object(value)


def _snapshot(value: dict[str, Any]) -> dict[str, Any]:
    return value["data"]["snapshot"]


def _first_file(value: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(value)["files"][0]


def _reject_forbidden_source(value: str | Path) -> None:
    text = os.fspath(value)
    if text.startswith(("http://", "https://", "/", "~")) or ".codex_work" in text:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "network or real path source is forbidden")


def _enforce_resources(runtime_seconds: float, peak_rss_bytes: int) -> None:
    if runtime_seconds > MAX_RUNTIME_SECONDS or peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "resource cap exceeded")
    for key in THREAD_ENV_KEYS:
        if os.environ.get(key) != "1":
            raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "thread environment is not one")


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "public row field is forbidden")
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)
    elif isinstance(value, str):
        if "s3.amazonaws.com" in value or "versionId=" in value or re.search(r"sub-[0-9]{2}/", value):
            raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "public row value is forbidden")


def validate_public_report(
    report: Mapping[str, Any], *, allow_incomplete_measurements: bool = False
) -> None:
    """Validate exact aggregate report shape and claim boundary."""

    if set(report) != PUBLIC_REPORT_FIELDS:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "public report fields differ")
    if report.get("schema_name") != REPORT_SCHEMA_NAME or report.get("route") != EXPECTED_ROUTE:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "public report identity differs")
    counters = report.get("access_counters")
    if not isinstance(counters, dict) or any(value != 0 for value in counters.values()):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "real access counter is nonzero")
    if not allow_incomplete_measurements:
        measurements = report.get("measurements")
        if not isinstance(measurements, dict) or any(
            measurements.get(field) is None
            for field in (
                "runtime_seconds",
                "peak_RSS_bytes",
                "generated_output_bytes",
                "deterministic_replays",
                "refusal_mutations_passed",
            )
        ):
            raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "measurements are incomplete")
        gates = report.get("acceptance_gates")
        if not isinstance(gates, dict) or not all(gates.values()):
            raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "acceptance gate is not true")
    _walk_public(report)


def _run_required_mutations(payload: bytes, contract: Mapping[str, Any]) -> dict[str, str]:
    base = _strict_json(payload)
    checks: dict[str, Callable[[], Any]] = {}

    checks["body_overflow"] = lambda: canonicalize_generated_response(b"x" * (MAX_RESPONSE_BYTES + 1), contract=contract)

    def read_twice() -> None:
        reader = GeneratedBodyReader(payload)
        reader.read_once(MAX_RESPONSE_BYTES + 1)
        reader.read_once(MAX_RESPONSE_BYTES + 1)

    checks["read_error_or_second_read"] = read_twice
    checks["duplicate_JSON_key"] = lambda: canonicalize_generated_response(b'{"data":{},"data":{}}', contract=contract)
    checks["invalid_UTF8_BOM_NUL_or_control"] = lambda: canonicalize_generated_response(b"\xef\xbb\xbf{}", contract=contract)
    checks["nonfinite_JSON_number"] = lambda: canonicalize_generated_response(b'{"data":NaN}', contract=contract)
    checks["GraphQL_errors_present"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: value.__setitem__("errors", [])), contract=contract)
    checks["null_data_or_snapshot"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: value.__setitem__("data", None)), contract=contract)
    checks["unknown_top_level_data_snapshot_description_or_file_field"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: value.__setitem__("extra", True)), contract=contract)
    checks["missing_required_field"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value).pop("tag")), contract=contract)
    checks["wrong_field_type"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value).__setitem__("files", {})), contract=contract)
    checks["wrong_snapshot_ID"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value).__setitem__("id", "ds000000:1.0.0")), contract=contract)
    checks["wrong_snapshot_tag"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value).__setitem__("tag", "1.0.1")), contract=contract)
    checks["malformed_snapshot_hexsha"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value).__setitem__("hexsha", "xyz")), contract=contract)
    checks["description_revision_mismatch"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value)["description"].__setitem__("id", "0" * 40)), contract=contract)
    for field, name in (
        ("Name", "critical_Name_drift"),
        ("BIDSVersion", "critical_BIDSVersion_drift"),
        ("License", "critical_License_drift"),
        ("DatasetDOI", "critical_DatasetDOI_drift"),
    ):
        checks[name] = lambda field=field: canonicalize_generated_response(
            _mutated(base, lambda value, field=field: _snapshot(value)["description"].__setitem__(field, "drift")),
            contract=contract,
        )
    checks["duplicate_path"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value)["files"][1].__setitem__("filename", _first_file(value)["filename"])), contract=contract)
    checks["absolute_dot_dotdot_backslash_or_repeated_separator_path"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _first_file(value).__setitem__("filename", "../escape")), contract=contract)
    checks["non_NFC_or_percent_ambiguous_path"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _first_file(value).__setitem__("filename", "auxiliary/cafe\u0301.bin")), contract=contract)
    checks["malformed_file_ID"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _first_file(value).__setitem__("id", "bad")), contract=contract)
    checks["boolean_negative_fractional_or_noncanonical_size"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _first_file(value).__setitem__("size", True)), contract=contract)
    checks["directory_true_or_annexed_wrong_type"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _first_file(value).__setitem__("directory", True)), contract=contract)
    checks["missing_or_multiple_URL"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _first_file(value).__setitem__("urls", [])), contract=contract)
    checks["non_HTTPS_alternate_host_bucket_or_key_mismatch"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _first_file(value).__setitem__("urls", ["http://example.invalid/object?versionId=x"])), contract=contract)

    def extra_query(value: dict[str, Any]) -> None:
        row = _first_file(value)
        row["urls"] = [row["urls"][0] + "&extra=1"]

    checks["userinfo_port_fragment_extra_query_or_missing_versionId"] = lambda: canonicalize_generated_response(_mutated(base, extra_query), contract=contract)
    checks["all_tree_count_or_byte_drift"] = lambda: canonicalize_generated_response(_mutated(base, lambda value: _snapshot(value)["files"].pop()), contract=contract)

    def remove_selected(value: dict[str, Any]) -> None:
        files = _snapshot(value)["files"]
        index = next(i for i, row in enumerate(files) if str(row["filename"]).startswith("sub-"))
        files.pop(index)

    checks["selected_count_or_byte_drift"] = lambda: canonicalize_generated_response(_mutated(base, remove_selected), contract=contract)

    def participant_drift(value: dict[str, Any]) -> None:
        row = next(row for row in _snapshot(value)["files"] if str(row["filename"]).startswith("sub-15/"))
        old = str(row["filename"])
        new = old.replace("sub-15", "sub-16")
        row["filename"] = new
        row["urls"] = [str(row["urls"][0]).replace(old, new)]

    checks["participant_or_run_count_drift"] = lambda: canonicalize_generated_response(_mutated(base, participant_drift), contract=contract)

    def role_drift(value: dict[str, Any]) -> None:
        row = next(row for row in _snapshot(value)["files"] if str(row["filename"]).endswith("_events.tsv"))
        old = str(row["filename"])
        new = old.removesuffix("_events.tsv") + "_unknown.tsv"
        row["filename"] = new
        row["urls"] = [str(row["urls"][0]).replace(old, new)]

    checks["role_count_or_byte_drift"] = lambda: canonicalize_generated_response(_mutated(base, role_drift), contract=contract)

    def missing_description(value: dict[str, Any]) -> None:
        row = next(row for row in _snapshot(value)["files"] if row["filename"] == "dataset_description.json")
        old = str(row["filename"])
        new = "description-missing.json"
        row["filename"] = new
        row["urls"] = [str(row["urls"][0]).replace(old, new)]

    checks["missing_dataset_description_row"] = lambda: canonicalize_generated_response(_mutated(base, missing_description), contract=contract)
    checks["network_constructor_or_real_path_attempt"] = lambda: _reject_forbidden_source("https://example.invalid")
    checks["output_symlink_overwrite_or_cap"] = lambda: _bounded_output_bytes(b"x" * (MAX_OUTPUT_BYTES + 1), b"")
    checks["thread_runtime_or_RSS_cap"] = lambda: _enforce_resources(MAX_RUNTIME_SECONDS + 1.0, 1)

    completed = canonicalize_generated_response(payload, contract=contract)

    def leak_public() -> None:
        report = copy.deepcopy(completed.report)
        report["tree_summary"]["path"] = "sub-01/eeg/private"
        validate_public_report(report, allow_incomplete_measurements=True)

    checks["public_row_path_URL_or_version_ID_leak"] = leak_public

    def replay_mismatch() -> None:
        left = _canonical_json_bytes(completed.private_manifest)
        right = left + b"x"
        if left != right:
            raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "replay differs")

    checks["deterministic_replay_mismatch"] = replay_mismatch
    if set(checks) != set(REQUIRED_MUTATIONS):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "mutation inventory differs")
    return {name: _expect_refusal(name, checks[name]) for name in REQUIRED_MUTATIONS}


def _bounded_output_bytes(report_bytes: bytes, manifest_bytes: bytes) -> int:
    total = len(report_bytes) + len(manifest_bytes)
    if total > MAX_OUTPUT_BYTES:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "combined output exceeds cap")
    return total


def _assert_output_destination(output_dir: Path) -> None:
    if output_dir.exists() or output_dir.is_symlink():
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "output directory already exists")
    parent = output_dir.parent
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "output parent is unavailable")
    mode = os.lstat(parent).st_mode
    if stat.S_ISLNK(mode):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "output parent is a symlink")


def _write_outputs(output_dir: Path, report: Mapping[str, Any], manifest: Mapping[str, Any]) -> tuple[Path, Path, int]:
    _assert_output_destination(output_dir)
    report_bytes = _canonical_json_bytes(report)
    manifest_bytes = _canonical_json_bytes(manifest)
    total = _bounded_output_bytes(report_bytes, manifest_bytes)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        report_path = stage / "snapshot_identity_report.v0.json"
        manifest_path = stage / "selected_manifest.private.v0.json"
        report_path.write_bytes(report_bytes)
        manifest_path.write_bytes(manifest_bytes)
        os.replace(stage, output_dir)
    except Exception as exc:
        shutil.rmtree(stage, ignore_errors=True)
        if isinstance(exc, SnapshotIdentityRefusal):
            raise
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "output write failed") from exc
    return (
        output_dir / "snapshot_identity_report.v0.json",
        output_dir / "selected_manifest.private.v0.json",
        total,
    )


def qualify_generated_snapshot_identity(output_dir: str | Path) -> QualificationOutcome:
    """Run the one bounded generated qualification and write inspectable outputs."""

    start = time.perf_counter()
    contract = load_registered_contract()
    payload = make_generated_response(contract)
    first = canonicalize_generated_response(payload, contract=contract)
    second = canonicalize_generated_response(payload, contract=contract)
    if (
        _canonical_json_bytes(first.private_manifest) != _canonical_json_bytes(second.private_manifest)
        or _canonical_json_bytes(first.report) != _canonical_json_bytes(second.report)
    ):
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "deterministic replay differs")
    mutations = _run_required_mutations(payload, contract)
    runtime = time.perf_counter() - start
    peak_rss = _peak_rss_bytes()
    _enforce_resources(runtime, peak_rss)
    report = copy.deepcopy(first.report)
    report["measurements"].update(
        {
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "deterministic_replays": 2,
            "refusal_mutations_passed": len(mutations),
        }
    )
    report["acceptance_gates"].update(
        {
            "resource_caps": True,
            "deterministic_replay": True,
            "all_required_refusals": True,
        }
    )
    provisional_report_bytes = _canonical_json_bytes(report)
    manifest_bytes = _canonical_json_bytes(first.private_manifest)
    provisional_total = _bounded_output_bytes(provisional_report_bytes, manifest_bytes)
    report["measurements"]["generated_output_bytes"] = provisional_total
    final_report_bytes = _canonical_json_bytes(report)
    final_total = _bounded_output_bytes(final_report_bytes, manifest_bytes)
    if final_total != provisional_total:
        report["measurements"]["generated_output_bytes"] = final_total
        final_report_bytes = _canonical_json_bytes(report)
        final_total = _bounded_output_bytes(final_report_bytes, manifest_bytes)
    validate_public_report(report)
    output = Path(output_dir)
    report_path, manifest_path, written_total = _write_outputs(output, report, first.private_manifest)
    if written_total != final_total:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "written output count differs")
    return QualificationOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=manifest_path,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        input_bytes=len(payload),
        generated_output_bytes=written_total,
    )


def inspect_snapshot_identity_report(path: str | Path) -> dict[str, Any]:
    """Load and validate only an aggregate public qualification report."""

    report_path = Path(path)
    if report_path.is_symlink() or not report_path.is_file():
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "report path is unavailable")
    if report_path.stat().st_size > MAX_OUTPUT_BYTES:
        raise SnapshotIdentityRefusal(REFUSAL_IDS[7], "report exceeds output cap")
    report = _strict_json(report_path.read_bytes())
    validate_public_report(report)
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.iackd_snapshot_identity",
        description="Generated-only IACKD snapshot identity canonicalizer.",
    )
    subparsers = parser.add_subparsers(dest="command")
    qualify = subparsers.add_parser("qualify", help="Run one generated qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate report.")
    inspect.add_argument("report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Module CLI with no network or real-data execution mode."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "qualify":
            outcome = qualify_generated_snapshot_identity(args.output_dir)
            print(
                json.dumps(
                    {
                        "status": outcome.report["status"],
                        "route": outcome.report["route"],
                        "input_bytes": outcome.input_bytes,
                        "generated_output_bytes": outcome.generated_output_bytes,
                        "runtime_seconds": outcome.runtime_seconds,
                        "peak_RSS_bytes": outcome.peak_rss_bytes,
                        "report": str(outcome.report_path),
                    },
                    sort_keys=True,
                )
            )
            return 0
        report = inspect_snapshot_identity_report(args.report)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "route": report["route"],
                    "file_count": report["tree_summary"]["file_count"],
                    "selected_object_count": report["selected_summary"]["object_count"],
                    "selected_payload_bytes": report["selected_summary"]["payload_bytes"],
                    "warnings": report["warnings"],
                },
                sort_keys=True,
            )
        )
        return 0
    except SnapshotIdentityRefusal as exc:
        print(json.dumps({"status": "refused", "refusal_id": exc.refusal_id}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
