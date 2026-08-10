"""Strict, aggregate-only IACKD BIDS channel-role and geometry audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import stat
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
LEDGER_SCHEMA_NAME = "neurodecodekit.iackd_channel_role_geometry_ledger"
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.iackd_channel_role_geometry_implementation"
)
DECISION_SCHEMA_NAME = (
    "neurodecodekit.iackd_channel_role_geometry_authorization_decision"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/iackd_channel_role_geometry_contract.v0.json"
)
INVENTORY_RELATIVE_PATH = Path("registries/iackd_openneuro_metadata_inventory.v0.json")
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/iackd_channel_role_geometry_implementation.v0.json"
)
DECISION_RELATIVE_PATH = Path(
    "registries/iackd_channel_role_geometry_authorization_decision.v0.json"
)
REAL_OUTPUT_RELATIVE_PATH = Path(
    ".codex_work/iackd_channel_role_geometry/public/"
    "iackd_channel_role_geometry_ledger.v0.json"
)
REAL_CONSUMED_RELATIVE_PATH = Path(
    ".codex_work/iackd_channel_role_geometry/private/execution_consumed.v0.json"
)
CONTRACT_SHA256 = "a5c1e18cf77c25a656b31bbcd30c65e2ad3b7076ea747ec7c7137a3ff919612b"
CONTRACT_BYTES = 20_425
INVENTORY_SHA256 = "aeaa4928192cca9086fcb0abf4711147c68a68ef5c5aacda2ebc67d162a1ef19"
REGISTRATION_COMMIT = "228ccd03f5e0b5d02ba104e13b77b04f2032df78"
REGISTRATION_CI_RUN_ID = 31_427_931_578
REGISTRATION_BASE_JOB_ID = 93_583_989_913
REGISTRATION_OPTIONAL_JOB_ID = 93_583_989_996
MAX_LOCKED_JSON_BYTES = 2 * 1024 * 1024
MINIMUM_PLAUSIBLE_LEDGER_BYTES = 4096
HEX32_RE = re.compile(r"[0-9a-f]{32}\Z")
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
RUN_PATH_RE = re.compile(
    r"(?P<subject>sub-[0-9]{2})/eeg/"
    r"(?P=subject)_task-ihc_acq-(?P<hand>left|right)_run-(?P<run>[0-9]{2})_"
    r"(?P<suffix>channels\.tsv|eeg\.json)\Z"
)
GEOMETRY_PATH_RE = re.compile(
    r"(?P<subject>sub-[0-9]{2})/eeg/"
    r"(?P=subject)_acq-(?P<hand>left|right)_space-CapTrak_"
    r"(?P<suffix>electrodes\.tsv|coordsystem\.json)\Z"
)
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
CORE_EEG_NAMES = (
    "Fp1",
    "Fp2",
    "F7",
    "F3",
    "Fz",
    "F4",
    "F8",
    "FC3",
    "FCz",
    "FC4",
    "T7",
    "C3",
    "Cz",
    "C4",
    "T8",
    "CP3",
    "CPz",
    "CP4",
    "P7",
    "P3",
    "Pz",
    "P4",
    "P8",
    "O1",
    "Oz",
    "O2",
)
CONTROL_NAMES = ("HEOG", "VEOG", "TRIGGER")
OPTIONAL_REFERENCE_NAMES = ("M1", "M2")
COUNT_FIELDS = (
    "EEGChannelCount",
    "EOGChannelCount",
    "ECGChannelCount",
    "EMGChannelCount",
    "MiscChannelCount",
    "TriggerChannelCount",
)
REFUSAL_IDS = (
    "IACKDR-F00-registration-or-evidence-not-green",
    "IACKDR-F01-real-decision-missing-or-mismatched",
    "IACKDR-F02-execution-already-consumed",
    "IACKDR-F03-inventory-or-version-drift",
    "IACKDR-F04-path-URL-size-ETag-or-encoding-mismatch",
    "IACKDR-F05-redirect-retry-or-concurrency",
    "IACKDR-F06-body-size-or-resource-cap",
    "IACKDR-F07-text-or-JSON-decode-failure",
    "IACKDR-F08-TSV-schema-row-or-name-failure",
    "IACKDR-F09-channel-type-unit-status-or-number-failure",
    "IACKDR-F10-sidecar-required-field-or-number-failure",
    "IACKDR-F11-electrode-or-coordinate-schema-failure",
    "IACKDR-F12-geometry-pair-or-membership-failure",
    "IACKDR-F13-forbidden-public-field",
    "IACKDR-F14-output-exists-or-write-failure",
    "IACKDR-F15-local-bundle-VHDR-sibling-signal-event-trajectory-target-model-or-score-access",
    "IACKDR-F16-second-execution-retry-or-rerun",
)
PUBLIC_LEDGER_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "provenance",
        "measurements",
        "body_hash_set_SHA256",
        "channel_schema_groups",
        "aggregate_status_counts",
        "sidecar_groups",
        "role_map_candidate",
        "geometry_groups",
        "H1_reconciliation",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "acceptance_gate_results",
        "diagnostic_route",
        "claim_boundary",
    }
)


class RoleAuditRefusal(RuntimeError):
    """Fail closed with one stable, non-sensitive refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown IACKD-H2 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class RealExecutionEvidence:
    """Immutable green evidence required by the future one-shot real stage."""

    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    authorization_commit: str
    authorization_ci_run_id: int
    authorization_base_job_id: int
    authorization_optional_job_id: int
    authorization_decision_sha256: str
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class RoleAuditOutcome:
    """One completed synthetic or separately authorized metadata audit."""

    ledger: Mapping[str, Any]
    ledger_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_output_bytes: int


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise RoleAuditRefusal(REFUSAL_IDS[5], "redirect is forbidden")


class FixtureResponse(io.BytesIO):
    """Small urllib-like response used only by generated fixtures."""

    def __init__(
        self,
        payload: bytes,
        *,
        url: str,
        etag: str,
        status: int = 200,
        content_encoding: str | None = None,
        transfer_encoding: str | None = None,
    ) -> None:
        super().__init__(payload)
        self._url = url
        self.status = status
        self.headers = {
            "Content-Length": str(len(payload)),
            "ETag": f'"{etag}"',
        }
        if content_encoding is not None:
            self.headers["Content-Encoding"] = content_encoding
        if transfer_encoding is not None:
            self.headers["Transfer-Encoding"] = transfer_encoding

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status


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
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _canonical_json_compact(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    ).encode("utf-8")


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _read_locked_json(
    path: Path,
    *,
    expected_sha256: str | None,
    maximum_bytes: int = MAX_LOCKED_JSON_BYTES,
) -> tuple[dict[str, Any], str, int]:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise RoleAuditRefusal(REFUSAL_IDS[0], "locked JSON is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise RoleAuditRefusal(REFUSAL_IDS[0], "locked JSON is not a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RoleAuditRefusal(REFUSAL_IDS[0], "locked JSON no-follow open failed") from exc
    try:
        payload = b""
        while len(payload) <= maximum_bytes:
            chunk = os.read(descriptor, min(64 * 1024, maximum_bytes + 1 - len(payload)))
            if not chunk:
                break
            payload += chunk
    finally:
        os.close(descriptor)
    if len(payload) > maximum_bytes:
        raise RoleAuditRefusal(REFUSAL_IDS[0], "locked JSON exceeds its byte cap")
    observed_hash = _sha256_bytes(payload)
    if expected_sha256 is not None and observed_hash != expected_sha256:
        raise RoleAuditRefusal(REFUSAL_IDS[0], "locked JSON identity mismatch")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise RoleAuditRefusal(REFUSAL_IDS[0], "locked JSON is malformed") from exc
    if not isinstance(value, dict):
        raise RoleAuditRefusal(REFUSAL_IDS[0], "locked JSON root is not an object")
    return value, observed_hash, len(payload)


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green IACKD-H2 registration."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract, _, observed_bytes = _read_locked_json(
        root / CONTRACT_RELATIVE_PATH,
        expected_sha256=CONTRACT_SHA256,
    )
    if observed_bytes != CONTRACT_BYTES:
        raise RoleAuditRefusal(REFUSAL_IDS[0], "registered contract byte count mismatch")
    if (
        contract.get("schema_name")
        != "neurodecodekit.iackd_channel_role_geometry_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("contract_id") != "IACKD-H2-channel-role-geometry-contract-v0"
        or tuple(contract.get("refusal_ids", ())) != REFUSAL_IDS
        or contract.get("ordered_stages", {}).get("stage_R", {}).get(
            "currently_authorized"
        )
        is not False
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[0], "registered contract structure mismatch")
    return contract


def load_registered_inventory(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load only the committed metadata inventory; no payload path is consulted."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    inventory, _, _ = _read_locked_json(
        root / INVENTORY_RELATIVE_PATH,
        expected_sha256=INVENTORY_SHA256,
    )
    if (
        inventory.get("schema_name")
        != "neurodecodekit.iackd_openneuro_metadata_inventory"
        or inventory.get("dataset", {}).get("accession") != "ds006840"
        or inventory.get("dataset", {}).get("version") != "1.0.0"
        or inventory.get("access_boundary", {}).get("payload_url_gets") != 0
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "registered inventory structure mismatch")
    return inventory


def _safe_relative_object_path(value: str) -> str:
    path = Path(value)
    if (
        not value
        or path.is_absolute()
        or "\\" in value
        or any(part in {"", ".", ".."} for part in path.parts)
        or str(path) != value
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[4], "object path is unsafe")
    return value


def _path_identity(path: str, role: str) -> tuple[str, str]:
    matcher = RUN_PATH_RE if role in {"channels", "eeg_sidecar"} else GEOMETRY_PATH_RE
    match = matcher.fullmatch(path)
    if match is None:
        raise RoleAuditRefusal(REFUSAL_IDS[3], "object path does not match its role")
    expected_suffix = {
        "channels": "channels.tsv",
        "eeg_sidecar": "eeg.json",
        "electrodes": "electrodes.tsv",
        "coordsystem": "coordsystem.json",
    }[role]
    if match.group("suffix") != expected_suffix:
        raise RoleAuditRefusal(REFUSAL_IDS[3], "object suffix does not match its role")
    geometry_key = f'{match.group("subject")}|{match.group("hand")}'
    if role in {"channels", "eeg_sidecar"}:
        return f'{geometry_key}|{match.group("run")}', geometry_key
    return geometry_key, geometry_key


def registered_metadata_rows(
    contract: Mapping[str, Any], inventory: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Select and validate the exact 316-object committed metadata surface."""

    roles = set(contract["source"]["selected_roles"])
    selected = [
        dict(row)
        for row in inventory.get("selected_objects", ())
        if row.get("role") in roles
    ]
    selected.sort(key=lambda row: str(row.get("path", "")))
    if len(selected) != int(contract["source"]["expected_object_count"]):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "registered object count mismatch")
    if sum(int(row.get("size_bytes", -1)) for row in selected) != int(
        contract["source"]["expected_total_body_bytes"]
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "registered body-byte total mismatch")
    role_counts = Counter(str(row.get("role")) for row in selected)
    for role, summary in contract["source"]["role_summaries"].items():
        if role_counts[role] != int(summary["objects"]):
            raise RoleAuditRefusal(REFUSAL_IDS[3], "registered role count mismatch")
    paths: set[str] = set()
    for row in selected:
        path = _safe_relative_object_path(str(row.get("path", "")))
        role = str(row.get("role", ""))
        run_key, _ = _path_identity(path, role)
        if path in paths or not run_key:
            raise RoleAuditRefusal(REFUSAL_IDS[3], "duplicate registered object path")
        paths.add(path)
        if row.get("subject") != path.split("/", 1)[0]:
            raise RoleAuditRefusal(REFUSAL_IDS[3], "registered subject-path mismatch")
        size = row.get("size_bytes")
        etag = str(row.get("etag", "")).lower()
        if not isinstance(size, int) or size <= 0 or HEX32_RE.fullmatch(etag) is None:
            raise RoleAuditRefusal(REFUSAL_IDS[3], "registered object identity malformed")
        row["etag"] = etag
    identity = [
        {key: row[key] for key in contract["source"]["canonical_identity_fields"]}
        for row in selected
    ]
    encoded = _canonical_json_compact(identity)
    if (
        len(encoded) != int(contract["source"]["canonical_identity_bytes"])
        or _sha256_bytes(encoded) != contract["source"]["canonical_identity_sha256"]
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "canonical source identity mismatch")
    return selected


def _decode_text(payload: bytes, refusal_id: str) -> str:
    try:
        text = payload.decode("utf-8-sig" if payload.startswith(b"\xef\xbb\xbf") else "utf-8")
    except UnicodeDecodeError as exc:
        raise RoleAuditRefusal(refusal_id, "metadata is not strict UTF-8") from exc
    if "\x00" in text or any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        raise RoleAuditRefusal(refusal_id, "metadata contains a forbidden control")
    return unicodedata.normalize("NFC", text)


def _normalized_name(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).strip().casefold()
    return "".join(char for char in normalized if char.isalnum())


def _parse_tsv(
    payload: bytes,
    *,
    required_first: Sequence[str],
    minimum_rows: int,
    maximum_rows: int,
    refusal_id: str,
) -> tuple[list[str], list[list[str]]]:
    text = _decode_text(payload, refusal_id)
    try:
        table = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t", strict=True))
    except csv.Error as exc:
        raise RoleAuditRefusal(refusal_id, "TSV parsing failed") from exc
    while table and (not table[-1] or all(value == "" for value in table[-1])):
        table.pop()
    if not table or any(not row for row in table):
        raise RoleAuditRefusal(refusal_id, "TSV contains a missing or empty row")
    header = table[0]
    rows = table[1:]
    if header[: len(required_first)] != list(required_first):
        raise RoleAuditRefusal(refusal_id, "TSV required leading columns differ")
    if any(not value for value in header) or len(header) != len(set(header)):
        raise RoleAuditRefusal(refusal_id, "TSV columns are empty or duplicated")
    if not minimum_rows <= len(rows) <= maximum_rows:
        raise RoleAuditRefusal(refusal_id, "TSV row count is outside its bound")
    if any(len(row) != len(header) for row in rows):
        raise RoleAuditRefusal(refusal_id, "TSV row width differs from its header")
    return header, rows


def _finite_positive(value: Any, refusal_id: str, field: str) -> float:
    if isinstance(value, bool):
        raise RoleAuditRefusal(refusal_id, f"{field} is not numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise RoleAuditRefusal(refusal_id, f"{field} is not numeric") from exc
    if not math.isfinite(number) or number <= 0:
        raise RoleAuditRefusal(refusal_id, f"{field} is not positive and finite")
    return number


def _canonical_number(value: float) -> int | float:
    return int(value) if value.is_integer() else value


def parse_channels_tsv(payload: bytes, contract: Mapping[str, Any]) -> dict[str, Any]:
    """Parse one strict BIDS channels table without inferring sensor types."""

    spec = contract["channels_TSV_contract"]
    header, raw_rows = _parse_tsv(
        payload,
        required_first=spec["required_first_columns"],
        minimum_rows=int(spec["minimum_rows"]),
        maximum_rows=int(spec["maximum_rows"]),
        refusal_id=REFUSAL_IDS[8],
    )
    indices = {name: index for index, name in enumerate(header)}
    allowed_types = set(spec["registered_BIDS_types"])
    allowed_status = set(spec["allowed_status_values"])
    rows: list[dict[str, Any]] = []
    normalized_seen: set[str] = set()
    for raw in raw_rows:
        name = unicodedata.normalize("NFC", raw[indices["name"]]).strip()
        normalized = _normalized_name(name)
        if not normalized or normalized in normalized_seen:
            raise RoleAuditRefusal(REFUSAL_IDS[8], "channel names are empty or duplicated")
        normalized_seen.add(normalized)
        channel_type = raw[indices["type"]].strip()
        units = unicodedata.normalize("NFC", raw[indices["units"]]).strip()
        if channel_type not in allowed_types or channel_type.upper() != channel_type:
            raise RoleAuditRefusal(REFUSAL_IDS[9], "channel type is not registered uppercase BIDS")
        if not units:
            raise RoleAuditRefusal(REFUSAL_IDS[9], "channel units are empty")
        status = "n/a"
        if "status" in indices:
            status = raw[indices["status"]].strip()
            if status not in allowed_status:
                raise RoleAuditRefusal(REFUSAL_IDS[9], "channel status is not registered")
        sampling: int | float | None = None
        if "sampling_frequency" in indices:
            value = raw[indices["sampling_frequency"]].strip()
            if value != "n/a":
                sampling = _canonical_number(
                    _finite_positive(value, REFUSAL_IDS[9], "channel sampling frequency")
                )
        rows.append(
            {
                "name": name,
                "normalized_name": normalized,
                "type": channel_type,
                "units": units,
                "status": status,
                "sampling_frequency": sampling,
            }
        )
    unknown = [
        name
        for name in header
        if name
        not in {
            "name",
            "type",
            "units",
            "status",
            "status_description",
            "sampling_frequency",
            "description",
        }
    ]
    return {
        "rows": rows,
        "unknown_column_names_sha256": _sha256_bytes(_canonical_json_bytes(unknown)),
    }


def _parse_json_object(payload: bytes, refusal_id: str) -> dict[str, Any]:
    text = _decode_text(payload, refusal_id)
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise RoleAuditRefusal(refusal_id, "JSON parsing failed") from exc
    if not isinstance(value, dict):
        raise RoleAuditRefusal(refusal_id, "JSON root is not an object")
    return value


def _canonical_reference(value: Any) -> str | list[str]:
    if isinstance(value, str):
        result = unicodedata.normalize("NFC", value).strip()
        if not result:
            raise RoleAuditRefusal(REFUSAL_IDS[10], "EEGReference is empty")
        return result
    if isinstance(value, list) and value:
        result = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise RoleAuditRefusal(REFUSAL_IDS[10], "EEGReference list is malformed")
            result.append(unicodedata.normalize("NFC", item).strip())
        return result
    raise RoleAuditRefusal(REFUSAL_IDS[10], "EEGReference is malformed")


def parse_eeg_sidecar(payload: bytes, contract: Mapping[str, Any]) -> dict[str, Any]:
    """Parse one BIDS EEG sidecar and retain only allowlisted aggregate values."""

    spec = contract["eeg_sidecar_contract"]
    value = _parse_json_object(payload, REFUSAL_IDS[10])
    if any(field not in value for field in spec["required_fields"]):
        raise RoleAuditRefusal(REFUSAL_IDS[10], "EEG sidecar required field is missing")
    if not isinstance(value["TaskName"], str) or not value["TaskName"].strip():
        raise RoleAuditRefusal(REFUSAL_IDS[10], "TaskName is malformed")
    sampling = _canonical_number(
        _finite_positive(value["SamplingFrequency"], REFUSAL_IDS[10], "SamplingFrequency")
    )
    reference = _canonical_reference(value["EEGReference"])
    power = value["PowerLineFrequency"]
    if isinstance(power, str):
        if power != "n/a":
            raise RoleAuditRefusal(REFUSAL_IDS[10], "PowerLineFrequency is malformed")
    else:
        power = _canonical_number(
            _finite_positive(power, REFUSAL_IDS[10], "PowerLineFrequency")
        )
    software = value["SoftwareFilters"]
    if not isinstance(software, (dict, str)) or (isinstance(software, str) and software != "n/a"):
        raise RoleAuditRefusal(REFUSAL_IDS[10], "SoftwareFilters is malformed")
    allowed: dict[str, Any] = {
        "SamplingFrequency": sampling,
        "EEGReference": reference,
        "PowerLineFrequency": power,
    }
    if "RecordingType" in value:
        recording_type = value["RecordingType"]
        if recording_type not in {"continuous", "epoched", "discontinuous", "n/a"}:
            raise RoleAuditRefusal(REFUSAL_IDS[10], "RecordingType is malformed")
        allowed["RecordingType"] = recording_type
    for field in COUNT_FIELDS:
        if field not in value:
            allowed[field] = None
            continue
        count = value[field]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise RoleAuditRefusal(REFUSAL_IDS[10], f"{field} is not a nonnegative integer")
        allowed[field] = count
    allowed["SoftwareFiltersSHA256"] = _sha256_bytes(_canonical_json_bytes(software))
    return allowed


def parse_electrodes_tsv(payload: bytes, contract: Mapping[str, Any]) -> dict[str, Any]:
    """Parse electrode coordinates while retaining no public coordinate value."""

    spec = contract["electrodes_TSV_contract"]
    header, raw_rows = _parse_tsv(
        payload,
        required_first=spec["required_first_columns"],
        minimum_rows=1,
        maximum_rows=256,
        refusal_id=REFUSAL_IDS[11],
    )
    indices = {name: index for index, name in enumerate(header)}
    rows: list[dict[str, Any]] = []
    names_seen: set[str] = set()
    coordinate_hash_rows: list[list[str]] = []
    for raw in raw_rows:
        name = unicodedata.normalize("NFC", raw[indices["name"]]).strip()
        normalized = _normalized_name(name)
        if not normalized or normalized in names_seen:
            raise RoleAuditRefusal(REFUSAL_IDS[11], "electrode names are empty or duplicated")
        names_seen.add(normalized)
        coordinates: list[float | None] = []
        coordinate_text: list[str] = []
        for field in ("x", "y", "z"):
            text = raw[indices[field]].strip()
            coordinate_text.append(text)
            if text == "n/a":
                coordinates.append(None)
                continue
            try:
                number = float(text)
            except ValueError as exc:
                raise RoleAuditRefusal(REFUSAL_IDS[11], "electrode coordinate is malformed") from exc
            if not math.isfinite(number):
                raise RoleAuditRefusal(REFUSAL_IDS[11], "electrode coordinate is non-finite")
            coordinates.append(number)
        rows.append(
            {
                "name": name,
                "normalized_name": normalized,
                "finite": all(item is not None for item in coordinates),
            }
        )
        coordinate_hash_rows.append([name, *coordinate_text])
    return {
        "rows": rows,
        "ordered_name_sha256": _sha256_bytes(
            _canonical_json_bytes([row["name"] for row in rows])
        ),
        "coordinate_bytes_sha256": _sha256_bytes(
            _canonical_json_bytes(coordinate_hash_rows)
        ),
    }


def parse_coordsystem_json(payload: bytes, contract: Mapping[str, Any]) -> dict[str, str]:
    """Parse only the non-coordinate BIDS coordinate-system declarations."""

    spec = contract["coordsystem_JSON_contract"]
    value = _parse_json_object(payload, REFUSAL_IDS[11])
    if any(field not in value for field in spec["required_fields"]):
        raise RoleAuditRefusal(REFUSAL_IDS[11], "coordinate-system field is missing")
    system = value["EEGCoordinateSystem"]
    units = value["EEGCoordinateUnits"]
    if not isinstance(system, str) or not system.strip():
        raise RoleAuditRefusal(REFUSAL_IDS[11], "coordinate system is empty")
    if not isinstance(units, str) or units not in set(spec["allowed_units"]):
        raise RoleAuditRefusal(REFUSAL_IDS[11], "coordinate units are not registered")
    return {
        "coordinate_system": unicodedata.normalize("NFC", system).strip(),
        "coordinate_units": units,
    }


def _channel_semantics(parsed: Mapping[str, Any]) -> dict[str, Any]:
    rows = parsed["rows"]
    by_name = {row["normalized_name"]: row for row in rows}
    predictive = [
        row["name"]
        for row in rows
        if row["type"] == "EEG" and row["normalized_name"] not in {"m1", "m2"}
    ]
    eog_controls = {}
    for display, normalized, allowed in (
        ("HEOG", "heog", {"HEOG", "EOG"}),
        ("VEOG", "veog", {"VEOG", "EOG"}),
    ):
        row = by_name.get(normalized)
        eog_controls[display] = {
            "present": row is not None,
            "source_type": None if row is None else row["type"],
            "compatible": row is not None and row["type"] in allowed,
        }
    trigger = by_name.get("trigger")
    optional = {
        name: (
            None if (row := by_name.get(name.casefold())) is None else row["type"]
        )
        for name in OPTIONAL_REFERENCE_NAMES
    }
    full_schema = [[row["name"], row["type"], row["units"]] for row in rows]
    core_schema = [
        [row["name"], row["type"], row["units"]]
        for row in rows
        if row["normalized_name"] not in {"m1", "m2"}
    ]
    return {
        "row_count": len(rows),
        "ordered_name_type_units": full_schema,
        "ordered_schema_sha256": _sha256_bytes(_canonical_json_bytes(full_schema)),
        "core_ordered_name_type_units": core_schema,
        "core_schema_sha256": _sha256_bytes(_canonical_json_bytes(core_schema)),
        "predictive_EEG_names": predictive,
        "recorded_EOG_controls": eog_controls,
        "trigger": {
            "present": trigger is not None,
            "source_type": None if trigger is None else trigger["type"],
            "compatible": trigger is not None and trigger["type"] in {"TRIG", "MISC"},
            "predictive": False,
        },
        "optional_M1_M2_source_types": optional,
        "required_control_roles_valid": all(
            item["compatible"] for item in eog_controls.values()
        )
        and trigger is not None
        and trigger["type"] in {"TRIG", "MISC"},
        "status_counts": dict(sorted(Counter(row["status"] for row in rows).items())),
        "unknown_column_names_sha256": parsed["unknown_column_names_sha256"],
    }


def _sidecar_channel_counts(parsed: Mapping[str, Any]) -> dict[str, int]:
    rows = parsed["rows"]
    return {
        "EEGChannelCount": sum(row["type"] == "EEG" for row in rows),
        "EOGChannelCount": sum(row["type"] in {"EOG", "HEOG", "VEOG"} for row in rows),
        "ECGChannelCount": sum(row["type"] == "ECG" for row in rows),
        "EMGChannelCount": sum(row["type"] == "EMG" for row in rows),
        "MiscChannelCount": sum(
            row["type"] == "MISC" and row["normalized_name"] != "trigger"
            for row in rows
        ),
        "TriggerChannelCount": sum(
            row["normalized_name"] == "trigger" and row["type"] in {"TRIG", "MISC"}
            for row in rows
        ),
    }


def _counts_reconcile(
    channels: Mapping[str, Any], sidecar: Mapping[str, Any]
) -> bool:
    observed = _sidecar_channel_counts(channels)
    return all(
        sidecar[field] is None or sidecar[field] == observed[field]
        for field in COUNT_FIELDS
    )


def _sampling_reconciles(
    channels: Mapping[str, Any], sidecar: Mapping[str, Any]
) -> bool:
    declared = {
        row["sampling_frequency"]
        for row in channels["rows"]
        if row["sampling_frequency"] is not None
    }
    return not declared or declared == {sidecar["SamplingFrequency"]}


def _group_rows(
    values: Sequence[Mapping[str, Any]], *, id_field: str
) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for value in values:
        canonical = dict(value)
        identifier = _sha256_bytes(_canonical_json_bytes(canonical))
        if identifier not in groups:
            groups[identifier] = {
                id_field: identifier,
                **canonical,
                "occurrence_count": 0,
            }
        groups[identifier]["occurrence_count"] += 1
    return sorted(groups.values(), key=lambda row: row[id_field])


def _role_map_candidate(semantics: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    core_groups = _group_rows(
        [
            {"ordered_name_type_units": value["core_ordered_name_type_units"]}
            for value in semantics
        ],
        id_field="core_schema_id",
    )
    first = semantics[0]
    optional_types = {
        name: sorted(
            {
                value["optional_M1_M2_source_types"][name]
                for value in semantics
                if value["optional_M1_M2_source_types"][name] is not None
            }
        )
        for name in OPTIONAL_REFERENCE_NAMES
    }
    candidate = {
        "core_schema_count": len(core_groups),
        "core_schema_SHA256s": [row["core_schema_id"] for row in core_groups],
        "predictive_EEG_names": list(first["predictive_EEG_names"]),
        "recorded_EOG_control_names": ["HEOG", "VEOG"],
        "trigger_name": "TRIGGER",
        "optional_M1_M2_source_type_groups": optional_types,
        "required_control_roles_valid_across_all_runs": all(
            value["required_control_roles_valid"] for value in semantics
        ),
        "source_order_sha256": first["core_schema_sha256"],
    }
    candidate["role_map_SHA256"] = _sha256_bytes(_canonical_json_bytes(candidate))
    return candidate


def _geometry_signature(
    electrodes: Mapping[str, Any],
    coordsystem: Mapping[str, Any],
    predictive_names: Sequence[str],
    channel_names: Sequence[str],
) -> dict[str, Any]:
    electrode_rows = electrodes["rows"]
    finite_by_name = {
        row["normalized_name"]: bool(row["finite"]) for row in electrode_rows
    }
    channel_set = {_normalized_name(name) for name in channel_names}
    predictive_set = {_normalized_name(name) for name in predictive_names}
    central = {_normalized_name(name) for name in ("C3", "C4", "Cz")}
    occipital = {_normalized_name(name) for name in ("O1", "Oz", "O2")}
    return {
        "electrode_count": len(electrode_rows),
        "finite_coordinate_count": sum(finite_by_name.values()),
        "predictive_EEG_geometry_coverage_count": sum(
            finite_by_name.get(name, False) for name in predictive_set
        ),
        "finite_C3_C4_Cz_presence": all(finite_by_name.get(name, False) for name in central),
        "finite_O1_Oz_O2_presence": all(
            finite_by_name.get(name, False) for name in occipital
        ),
        "channel_electrode_intersection_count": len(channel_set.intersection(finite_by_name)),
        "coordinate_system": coordsystem["coordinate_system"],
        "coordinate_units": coordsystem["coordinate_units"],
        "ordered_name_sha256": electrodes["ordered_name_sha256"],
        "coordinate_bytes_sha256": electrodes["coordinate_bytes_sha256"],
    }


def route_role_audit(
    *,
    reconciliation: Mapping[str, Any],
    role_map_candidate: Mapping[str, Any],
    geometry_groups: Sequence[Mapping[str, Any]],
    reference_values: Sequence[Any],
    failed: bool = False,
) -> str:
    """Apply the frozen IACKD-H2 router in exact order."""

    if failed:
        return "IACKDR-R0"
    contradiction_fields = (
        "channel_row_count_multiset_matches_H1",
        "allowlisted_presence_matches_H1",
        "required_control_BIDS_roles_valid",
        "present_sidecar_type_counts_reconcile",
        "present_channel_sampling_reconciles",
        "all_sidecar_sampling_matches_H1_1024_Hz",
    )
    if not all(bool(reconciliation.get(name)) for name in contradiction_fields):
        return "IACKDR-R1"
    if int(role_map_candidate.get("core_schema_count", 0)) != 1:
        return "IACKDR-R2"
    references = {_canonical_json_bytes(value) for value in reference_values}
    reference_available = bool(reference_values) and all(value != "n/a" for value in reference_values)
    central_complete = sum(
        int(group["occurrence_count"])
        for group in geometry_groups
        if group["finite_C3_C4_Cz_presence"]
    ) == 30
    if len(references) != 1 or not reference_available or not central_complete:
        return "IACKDR-R3"
    return "IACKDR-R4"


def _normalize_etag(value: str) -> str:
    normalized = value.strip().strip('"').lower()
    if HEX32_RE.fullmatch(normalized) is None:
        raise RoleAuditRefusal(REFUSAL_IDS[4], "response ETag is malformed")
    return normalized


def _response_header(stream: BinaryIO, name: str) -> str | None:
    headers = getattr(stream, "headers", None)
    return None if headers is None else headers.get(name)


def _response_url(stream: BinaryIO) -> str | None:
    getter = getattr(stream, "geturl", None)
    return None if getter is None else str(getter())


def _response_status(stream: BinaryIO) -> int | None:
    value = getattr(stream, "status", None)
    if value is None:
        getter = getattr(stream, "getcode", None)
        value = None if getter is None else getter()
    return None if value is None else int(value)


@contextmanager
def _managed_stream(stream: BinaryIO) -> Iterator[BinaryIO]:
    try:
        yield stream
    finally:
        stream.close()


def _validate_response(stream: BinaryIO, *, url: str, row: Mapping[str, Any]) -> None:
    if _response_status(stream) != 200:
        raise RoleAuditRefusal(REFUSAL_IDS[4], "response status is not 200")
    if _response_url(stream) != url:
        raise RoleAuditRefusal(REFUSAL_IDS[5], "response URL differs from request URL")
    length = _response_header(stream, "Content-Length")
    try:
        parsed_length = int(length) if length is not None else -1
    except ValueError as exc:
        raise RoleAuditRefusal(REFUSAL_IDS[4], "Content-Length is malformed") from exc
    if parsed_length != int(row["size_bytes"]):
        raise RoleAuditRefusal(REFUSAL_IDS[4], "Content-Length mismatch")
    etag = _response_header(stream, "ETag")
    if etag is None or _normalize_etag(etag) != row["etag"]:
        raise RoleAuditRefusal(REFUSAL_IDS[4], "response ETag mismatch")
    content_encoding = (_response_header(stream, "Content-Encoding") or "identity").casefold()
    transfer_encoding = (_response_header(stream, "Transfer-Encoding") or "identity").casefold()
    if content_encoding != "identity" or transfer_encoding != "identity":
        raise RoleAuditRefusal(REFUSAL_IDS[4], "response transformation is forbidden")


def _read_exact_body(stream: BinaryIO, expected_bytes: int, maximum_bytes: int) -> bytes:
    if expected_bytes > maximum_bytes:
        raise RoleAuditRefusal(REFUSAL_IDS[6], "registered body exceeds read cap")
    payload = stream.read(expected_bytes + 1)
    if len(payload) != expected_bytes:
        raise RoleAuditRefusal(REFUSAL_IDS[6], "response body length mismatch")
    return payload


def _peak_rss_bytes() -> int:
    import resource

    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise RoleAuditRefusal(REFUSAL_IDS[6], "one-thread environment is required")


def _base_access_counters(*, synthetic: bool) -> dict[str, int]:
    return {
        "synthetic_metadata_requests": 0,
        "real_metadata_requests": 0,
        "real_metadata_body_bytes": 0,
        "real_metadata_parses": 0,
        "VHDR_rereads": 0,
        "local_IACKD_path_stats_or_opens": 0,
        "sibling_resolutions_stats_hashes_or_opens": 0,
        "signal_sample_reads": 0,
        "marker_or_event_reads": 0,
        "trajectory_reads": 0,
        "target_or_label_reads": 0,
        "cache_or_split_operations": 0,
        "feature_extraction_runs": 0,
        "model_or_checkpoint_loads": 0,
        "training_or_parameter_update_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "scoring_runs": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
        "synthetic_mode": int(synthetic),
    }


def _assert_forbidden_counters_zero(counters: Mapping[str, int], *, synthetic: bool) -> None:
    permitted = {"synthetic_mode", "synthetic_metadata_requests"}
    if not synthetic:
        permitted |= {
            "real_metadata_requests",
            "real_metadata_body_bytes",
            "real_metadata_parses",
        }
    for name, value in counters.items():
        if name not in permitted and value != 0:
            raise RoleAuditRefusal(REFUSAL_IDS[15], "forbidden access counter is nonzero")


def _iter_string_values(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from _iter_string_values(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested in value:
            yield from _iter_string_values(nested)


def _ensure_output_preflight(path: Path, *, maximum_output_bytes: int) -> None:
    if maximum_output_bytes < MINIMUM_PLAUSIBLE_LEDGER_BYTES:
        raise RoleAuditRefusal(REFUSAL_IDS[6], "output cap is too small for the schema")
    if path.exists() or path.is_symlink():
        raise RoleAuditRefusal(REFUSAL_IDS[14], "output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    observed = os.lstat(path.parent)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise RoleAuditRefusal(REFUSAL_IDS[14], "output parent is not a regular directory")


def _assert_rooted_output_path(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise RoleAuditRefusal(REFUSAL_IDS[14], "real output escapes repository root") from exc
    current = root
    for part in relative.parts[:-1]:
        current /= part
        try:
            observed = os.lstat(current)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise RoleAuditRefusal(REFUSAL_IDS[14], "real output ancestry is unavailable") from exc
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
            raise RoleAuditRefusal(REFUSAL_IDS[14], "real output ancestry is unsafe")


def _write_atomic_exclusive(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    if temporary.exists() or temporary.is_symlink():
        raise RoleAuditRefusal(REFUSAL_IDS[14], "invocation temporary output exists")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError:
            raise RoleAuditRefusal(REFUSAL_IDS[14], "output appeared during commit") from None
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _build_aggregate_components(
    *,
    contract: Mapping[str, Any],
    channels_by_run: Mapping[str, Mapping[str, Any]],
    sidecars_by_run: Mapping[str, Mapping[str, Any]],
    electrodes_by_group: Mapping[str, Mapping[str, Any]],
    coordsystems_by_group: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    if set(channels_by_run) != set(sidecars_by_run) or len(channels_by_run) != 128:
        raise RoleAuditRefusal(REFUSAL_IDS[12], "channel and sidecar run membership differs")
    if (
        set(electrodes_by_group) != set(coordsystems_by_group)
        or len(electrodes_by_group) != 30
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[12], "geometry pair membership differs")
    run_groups: dict[str, list[str]] = {}
    for run_key in channels_by_run:
        geometry_key = run_key.rsplit("|", 1)[0]
        run_groups.setdefault(geometry_key, []).append(run_key)
    if set(run_groups) != set(electrodes_by_group):
        raise RoleAuditRefusal(REFUSAL_IDS[12], "run and geometry membership differs")

    ordered_run_keys = sorted(channels_by_run)
    semantics = [_channel_semantics(channels_by_run[key]) for key in ordered_run_keys]
    channel_public = [
        {
            "row_count": value["row_count"],
            "ordered_name_type_units": value["ordered_name_type_units"],
            "ordered_schema_sha256": value["ordered_schema_sha256"],
            "core_schema_sha256": value["core_schema_sha256"],
            "predictive_EEG_count": len(value["predictive_EEG_names"]),
            "required_control_roles_valid": value["required_control_roles_valid"],
            "optional_M1_present": value["optional_M1_M2_source_types"]["M1"]
            is not None,
            "optional_M2_present": value["optional_M1_M2_source_types"]["M2"]
            is not None,
            "unknown_column_names_sha256": value["unknown_column_names_sha256"],
        }
        for value in semantics
    ]
    channel_groups = _group_rows(channel_public, id_field="channel_schema_id")
    aggregate_status = Counter()
    for parsed in channels_by_run.values():
        aggregate_status.update(row["status"] for row in parsed["rows"])

    sidecar_values = [dict(sidecars_by_run[key]) for key in ordered_run_keys]
    sidecar_groups = _group_rows(sidecar_values, id_field="sidecar_group_id")
    role_map = _role_map_candidate(semantics)

    geometry_values: list[dict[str, Any]] = []
    for geometry_key in sorted(electrodes_by_group):
        related_keys = sorted(run_groups[geometry_key])
        related_rows = [
            row
            for run_key in related_keys
            for row in channels_by_run[run_key]["rows"]
        ]
        channel_names = list(dict.fromkeys(row["name"] for row in related_rows))
        predictive_names = list(
            dict.fromkeys(
                row["name"]
                for row in related_rows
                if row["type"] == "EEG"
                and row["normalized_name"] not in {"m1", "m2"}
            )
        )
        geometry_values.append(
            _geometry_signature(
                electrodes_by_group[geometry_key],
                coordsystems_by_group[geometry_key],
                predictive_names,
                channel_names,
            )
        )
    geometry_groups = _group_rows(geometry_values, id_field="geometry_group_id")

    presence_counter = Counter()
    for value in semantics:
        presence_counter[
            (
                value["row_count"],
                value["optional_M1_M2_source_types"]["M1"] is not None,
                value["optional_M1_M2_source_types"]["M2"] is not None,
                value["recorded_EOG_controls"]["HEOG"]["present"],
                value["recorded_EOG_controls"]["VEOG"]["present"],
                value["trigger"]["present"],
            )
        ] += 1
    expected_presence = Counter(
        {
            (29, False, False, True, True, True): 96,
            (31, True, True, True, True, True): 32,
        }
    )
    sidecar_counts_ok = all(
        _counts_reconcile(channels_by_run[key], sidecars_by_run[key])
        for key in ordered_run_keys
    )
    channel_sampling_ok = all(
        _sampling_reconciles(channels_by_run[key], sidecars_by_run[key])
        for key in ordered_run_keys
    )
    sidecar_sampling_ok = all(
        sidecars_by_run[key]["SamplingFrequency"]
        == contract["H1_reconciliation_anchor"]["sampling_rate_hz"]
        for key in ordered_run_keys
    )
    reconciliation = {
        "channel_row_count_multiset_matches_H1": Counter(
            value["row_count"] for value in semantics
        )
        == Counter({29: 96, 31: 32}),
        "allowlisted_presence_matches_H1": presence_counter == expected_presence,
        "required_control_BIDS_roles_valid": all(
            value["required_control_roles_valid"] for value in semantics
        ),
        "present_sidecar_type_counts_reconcile": sidecar_counts_ok,
        "present_channel_sampling_reconciles": channel_sampling_ok,
        "all_sidecar_sampling_matches_H1_1024_Hz": sidecar_sampling_ok,
        "core_schema_count_after_removing_only_M1_M2": role_map["core_schema_count"],
    }
    reconciliation["all_source_agreement_checks_pass"] = all(
        value for key, value in reconciliation.items() if key != "core_schema_count_after_removing_only_M1_M2"
    )
    references = [sidecars_by_run[key]["EEGReference"] for key in ordered_run_keys]
    route = route_role_audit(
        reconciliation=reconciliation,
        role_map_candidate=role_map,
        geometry_groups=geometry_groups,
        reference_values=references,
    )
    return {
        "channel_schema_groups": channel_groups,
        "aggregate_status_counts": dict(sorted(aggregate_status.items())),
        "sidecar_groups": sidecar_groups,
        "role_map_candidate": role_map,
        "geometry_groups": geometry_groups,
        "H1_reconciliation": reconciliation,
        "reference_values": references,
        "diagnostic_route": route,
    }


def _group_payload_without_identity(
    row: Mapping[str, Any], *, id_field: str
) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key not in {id_field, "occurrence_count"}
    }


def validate_public_ledger(
    ledger: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    forbidden_private_values: Sequence[str] = (),
) -> None:
    """Validate aggregate identities, router replay, and the leakage firewall."""

    if set(ledger) != PUBLIC_LEDGER_FIELDS:
        raise RoleAuditRefusal(REFUSAL_IDS[13], "public ledger field set mismatch")
    if (
        ledger.get("schema_name") != LEDGER_SCHEMA_NAME
        or ledger.get("schema_version") != SCHEMA_VERSION
        or ledger.get("status") != "completed"
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "public ledger identity mismatch")
    groups_and_totals = (
        ("channel_schema_groups", "channel_schema_id", 128),
        ("sidecar_groups", "sidecar_group_id", 128),
        ("geometry_groups", "geometry_group_id", 30),
    )
    for field, id_field, total in groups_and_totals:
        groups = ledger.get(field)
        if not isinstance(groups, list) or not groups:
            raise RoleAuditRefusal(REFUSAL_IDS[13], f"{field} is missing")
        if groups != sorted(groups, key=lambda row: row[id_field]):
            raise RoleAuditRefusal(REFUSAL_IDS[13], f"{field} is not canonical")
        if sum(int(row["occurrence_count"]) for row in groups) != total:
            raise RoleAuditRefusal(REFUSAL_IDS[13], f"{field} occurrence count mismatch")
        for row in groups:
            expected = _sha256_bytes(
                _canonical_json_bytes(_group_payload_without_identity(row, id_field=id_field))
            )
            if row[id_field] != expected:
                raise RoleAuditRefusal(REFUSAL_IDS[13], f"{field} identifier mismatch")

    role_map = ledger["role_map_candidate"]
    role_without_hash = {
        key: value for key, value in role_map.items() if key != "role_map_SHA256"
    }
    if role_map.get("role_map_SHA256") != _sha256_bytes(
        _canonical_json_bytes(role_without_hash)
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "role-map hash mismatch")
    references = [row["EEGReference"] for row in ledger["sidecar_groups"]]
    expected_route = route_role_audit(
        reconciliation=ledger["H1_reconciliation"],
        role_map_candidate=role_map,
        geometry_groups=ledger["geometry_groups"],
        reference_values=references,
    )
    if ledger.get("diagnostic_route") != expected_route:
        raise RoleAuditRefusal(REFUSAL_IDS[13], "diagnostic route does not replay")
    if ledger.get("warnings") != contract["warnings"]:
        raise RoleAuditRefusal(REFUSAL_IDS[13], "registered warnings changed")
    if ledger.get("unavailable_fields") != contract["unavailable_by_design"]:
        raise RoleAuditRefusal(REFUSAL_IDS[13], "unavailable-field boundary changed")
    if ledger.get("claim_boundary") != contract["claim_boundary"]:
        raise RoleAuditRefusal(REFUSAL_IDS[13], "claim boundary changed")
    if set(ledger.get("acceptance_gate_results", {})) != set(contract["acceptance_gates"]):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "acceptance-gate set changed")
    gate_results = ledger["acceptance_gate_results"]
    real_gate = contract["acceptance_gates"][0]
    synthetic = ledger["proof_posture"] == "generated_fixture_and_mocked_transport_only"
    if gate_results[real_gate] is not (not synthetic):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "real and fixture gates are conflated")
    source_gate = contract["acceptance_gates"][3]
    if gate_results[source_gate] is not bool(
        ledger["H1_reconciliation"]["all_source_agreement_checks_pass"]
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "source-reconciliation gate mismatch")
    if not all(
        value
        for name, value in gate_results.items()
        if name not in {real_gate, source_gate}
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "an invariant acceptance gate is false")
    forbidden_keys = {name.casefold() for name in contract["forbidden_public_fields"]}

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                if str(key).casefold() in forbidden_keys:
                    raise RoleAuditRefusal(REFUSAL_IDS[13], "forbidden public field present")
                visit(nested)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for nested in value:
                visit(nested)

    visit(ledger)
    public_strings = set(_iter_string_values(ledger))
    if any(value and value in public_strings for value in forbidden_private_values):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "private source value escaped into output")
    measurements = ledger["measurements"]
    if (
        measurements["input_objects"] != 316
        or measurements["input_bytes"] != 457_602
        or measurements["body_SHA256_passes"] != 316
        or measurements["semantic_parse_passes"] != 316
        or measurements["producer_is_causal"] is not None
        or measurements["end_to_end_latency_measured"] is not False
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[13], "measurement contract mismatch")
    _assert_forbidden_counters_zero(ledger["access_counters"], synthetic=synthetic)


def _build_ledger(
    *,
    contract: Mapping[str, Any],
    components: Mapping[str, Any],
    body_hash_set_sha256: str,
    role_counts: Mapping[str, int],
    role_bytes: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
    counters: Mapping[str, int],
    synthetic: bool,
    implementation_binding: Mapping[str, Any] | None,
) -> dict[str, Any]:
    gates = {name: True for name in contract["acceptance_gates"]}
    gates[contract["acceptance_gates"][0]] = not synthetic
    gates[contract["acceptance_gates"][3]] = bool(
        components["H1_reconciliation"]["all_source_agreement_checks_pass"]
    )
    return {
        "schema_name": LEDGER_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "completed",
        "proof_posture": (
            "generated_fixture_and_mocked_transport_only"
            if synthetic
            else "authorized_public_BIDS_metadata_compatibility_audit"
        ),
        "provenance": {
            "contract_sha256": CONTRACT_SHA256,
            "inventory_sha256": INVENTORY_SHA256,
            "registration_commit": REGISTRATION_COMMIT,
            "registration_push_CI_run_id": REGISTRATION_CI_RUN_ID,
            "registration_base_python_job_id": REGISTRATION_BASE_JOB_ID,
            "registration_optional_neuro_job_id": REGISTRATION_OPTIONAL_JOB_ID,
            "fixture_bodies": synthetic,
            "implementation": implementation_binding,
        },
        "measurements": {
            "input_objects": sum(role_counts.values()),
            "input_bytes": sum(role_bytes.values()),
            "role_object_counts": dict(sorted(role_counts.items())),
            "role_input_bytes": dict(sorted(role_bytes.items())),
            "network_body_bytes": 0 if synthetic else sum(role_bytes.values()),
            "body_SHA256_passes": sum(role_counts.values()),
            "semantic_parse_passes": sum(role_counts.values()),
            "runtime_seconds_through_output_finalization": round(runtime_seconds, 9),
            "peak_RSS_bytes_through_output_finalization": peak_rss_bytes,
            "generated_output_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "body_hash_set_SHA256": body_hash_set_sha256,
        "channel_schema_groups": components["channel_schema_groups"],
        "aggregate_status_counts": components["aggregate_status_counts"],
        "sidecar_groups": components["sidecar_groups"],
        "role_map_candidate": components["role_map_candidate"],
        "geometry_groups": components["geometry_groups"],
        "H1_reconciliation": components["H1_reconciliation"],
        "access_counters": dict(counters),
        "warnings": list(contract["warnings"]),
        "unavailable_fields": list(contract["unavailable_by_design"]),
        "acceptance_gate_results": gates,
        "diagnostic_route": components["diagnostic_route"],
        "claim_boundary": dict(contract["claim_boundary"]),
    }


def run_role_geometry_audit(
    *,
    contract: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    opener: Callable[[str, int], BinaryIO],
    output_path: str | Path,
    environ: Mapping[str, str],
    synthetic: bool,
    implementation_binding: Mapping[str, Any] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> RoleAuditOutcome:
    """Run the bounded audit over generated or separately authorized bodies."""

    _check_thread_environment(environ)
    caps = contract["resource_caps"]
    destination = Path(output_path)
    _ensure_output_preflight(
        destination,
        maximum_output_bytes=int(caps["public_generated_output_bytes"]),
    )
    if shutil.disk_usage(destination.parent).free < int(caps["minimum_free_disk_bytes"]):
        raise RoleAuditRefusal(REFUSAL_IDS[6], "free disk is below the registered minimum")
    if len(rows) != int(caps["requests"]):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "metadata request count mismatch")
    if sum(int(row["size_bytes"]) for row in rows) != int(caps["expected_body_bytes"]):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "metadata body-byte total mismatch")
    if [str(row["path"]) for row in rows] != sorted(str(row["path"]) for row in rows):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "metadata rows are not canonical")
    base_url = str(contract["source"]["object_base_url"])
    if synthetic and not base_url.startswith("fixture://"):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "synthetic audit requires fixture URLs")
    if not synthetic and not base_url.startswith("https://"):
        raise RoleAuditRefusal(REFUSAL_IDS[3], "real audit requires HTTPS")

    started = clock()
    peak_rss = rss_reader()
    if peak_rss > int(caps["peak_RSS_bytes"]):
        raise RoleAuditRefusal(REFUSAL_IDS[6], "initial peak RSS exceeds cap")
    heavy_before = HEAVY_MODULE_ROOTS.intersection(sys.modules)
    counters = _base_access_counters(synthetic=synthetic)
    channels_by_run: dict[str, dict[str, Any]] = {}
    sidecars_by_run: dict[str, dict[str, Any]] = {}
    electrodes_by_group: dict[str, dict[str, Any]] = {}
    coordsystems_by_group: dict[str, dict[str, Any]] = {}
    stores = {
        "channels": channels_by_run,
        "eeg_sidecar": sidecars_by_run,
        "electrodes": electrodes_by_group,
        "coordsystem": coordsystems_by_group,
    }
    parsers = {
        "channels": parse_channels_tsv,
        "eeg_sidecar": parse_eeg_sidecar,
        "electrodes": parse_electrodes_tsv,
        "coordsystem": parse_coordsystem_json,
    }
    role_counts: Counter[str] = Counter()
    role_bytes: Counter[str] = Counter()
    body_rows: list[dict[str, Any]] = []
    private_values: list[str] = []
    maximum_body = int(caps["maximum_bytes_read_per_object"])
    for row in rows:
        path = _safe_relative_object_path(str(row["path"]))
        role = str(row["role"])
        if role not in stores:
            raise RoleAuditRefusal(REFUSAL_IDS[3], "metadata role is not registered")
        item_key, _ = _path_identity(path, role)
        if item_key in stores[role]:
            raise RoleAuditRefusal(REFUSAL_IDS[12], "metadata semantic member is duplicated")
        size = int(row["size_bytes"])
        etag = str(row["etag"]).lower()
        if size <= 0 or size > maximum_body or HEX32_RE.fullmatch(etag) is None:
            raise RoleAuditRefusal(REFUSAL_IDS[4], "metadata row identity is malformed")
        quoted = urllib.parse.quote(path, safe="/._-")
        url = f"{base_url.rstrip('/')}/{quoted}"
        with _managed_stream(opener(url, maximum_body)) as stream:
            _validate_response(stream, url=url, row=row)
            payload = _read_exact_body(stream, size, maximum_body)
        stores[role][item_key] = parsers[role](payload, contract)
        body_rows.append(
            {
                "path": path,
                "size_bytes": size,
                "etag": etag,
                "body_sha256": _sha256_bytes(payload),
            }
        )
        private_values.extend((path, str(row.get("subject", ""))))
        role_counts[role] += 1
        role_bytes[role] += size
        if synthetic:
            counters["synthetic_metadata_requests"] += 1
        else:
            counters["real_metadata_requests"] += 1
            counters["real_metadata_body_bytes"] += size
            counters["real_metadata_parses"] += 1
        elapsed = clock() - started
        peak_rss = max(peak_rss, rss_reader())
        if elapsed > float(caps["wall_time_seconds"]) or peak_rss > int(caps["peak_RSS_bytes"]):
            raise RoleAuditRefusal(REFUSAL_IDS[6], "runtime or peak RSS cap exceeded")
    if role_counts != Counter(
        {
            role: int(summary["objects"])
            for role, summary in contract["source"]["role_summaries"].items()
        }
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[12], "parsed role membership is incomplete")
    if HEAVY_MODULE_ROOTS.intersection(sys.modules) != heavy_before:
        raise RoleAuditRefusal(REFUSAL_IDS[15], "a heavy dependency was imported")
    _assert_forbidden_counters_zero(counters, synthetic=synthetic)
    components = _build_aggregate_components(
        contract=contract,
        channels_by_run=channels_by_run,
        sidecars_by_run=sidecars_by_run,
        electrodes_by_group=electrodes_by_group,
        coordsystems_by_group=coordsystems_by_group,
    )
    ledger = _build_ledger(
        contract=contract,
        components=components,
        body_hash_set_sha256=_sha256_bytes(_canonical_json_bytes(body_rows)),
        role_counts=role_counts,
        role_bytes=role_bytes,
        runtime_seconds=clock() - started,
        peak_rss_bytes=max(peak_rss, rss_reader()),
        counters=counters,
        synthetic=synthetic,
        implementation_binding=implementation_binding,
    )
    maximum_output = int(caps["public_generated_output_bytes"])
    for _ in range(8):
        payload = _canonical_json_bytes(ledger)
        if ledger["measurements"]["generated_output_bytes"] == len(payload):
            break
        ledger["measurements"]["generated_output_bytes"] = len(payload)
    else:
        raise RoleAuditRefusal(REFUSAL_IDS[6], "output byte accounting did not converge")
    payload = _canonical_json_bytes(ledger)
    if len(payload) > maximum_output:
        raise RoleAuditRefusal(REFUSAL_IDS[6], "public output exceeds cap")
    validate_public_ledger(
        ledger,
        contract=contract,
        forbidden_private_values=private_values,
    )
    _write_atomic_exclusive(destination, payload)
    runtime = clock() - started
    peak_rss = max(
        int(ledger["measurements"]["peak_RSS_bytes_through_output_finalization"]),
        rss_reader(),
    )
    if runtime > float(caps["wall_time_seconds"]) or peak_rss > int(caps["peak_RSS_bytes"]):
        raise RoleAuditRefusal(REFUSAL_IDS[6], "post-write resource cap exceeded")
    return RoleAuditOutcome(ledger, destination, runtime, peak_rss, len(payload))


def _padded_tsv(
    header: Sequence[str], rows: Sequence[Sequence[str]], *, total_bytes: int
) -> bytes:
    padded_header = [*header, "fixture_padding"]
    padded_rows = [[*row, ""] for row in rows]

    def encode() -> bytes:
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(padded_header)
        writer.writerows(padded_rows)
        return stream.getvalue().encode("utf-8")

    payload = encode()
    padding = total_bytes - len(payload)
    if padding < 0 or not padded_rows:
        raise ValueError("requested synthetic TSV byte count is too small")
    padded_rows[0][-1] = "x" * padding
    payload = encode()
    if len(payload) != total_bytes:
        raise AssertionError("synthetic TSV padding is not exact")
    return payload


def _padded_json(value: Mapping[str, Any], *, total_bytes: int) -> bytes:
    prepared = {**value, "_fixture_padding": ""}
    payload = _canonical_json_bytes(prepared)
    padding = total_bytes - len(payload)
    if padding < 0:
        raise ValueError("requested synthetic JSON byte count is too small")
    prepared["_fixture_padding"] = "x" * padding
    payload = _canonical_json_bytes(prepared)
    if len(payload) != total_bytes:
        raise AssertionError("synthetic JSON padding is not exact")
    return payload


def make_synthetic_channels_tsv(*, include_references: bool, total_bytes: int) -> bytes:
    """Create deterministic target-free channel metadata at one registered size."""

    rows = [
        [name, "EEG", "uV", "good", "", "1024", "generated"]
        for name in CORE_EEG_NAMES
    ]
    rows.extend(
        [
            ["HEOG", "HEOG", "uV", "good", "", "1024", "generated"],
            ["VEOG", "VEOG", "uV", "good", "", "1024", "generated"],
            ["TRIGGER", "TRIG", "n/a", "good", "", "1024", "generated"],
        ]
    )
    if include_references:
        rows.extend(
            [
                ["M1", "REF", "uV", "good", "", "1024", "generated"],
                ["M2", "REF", "uV", "good", "", "1024", "generated"],
            ]
        )
    return _padded_tsv(
        (
            "name",
            "type",
            "units",
            "status",
            "status_description",
            "sampling_frequency",
            "description",
        ),
        rows,
        total_bytes=total_bytes,
    )


def make_synthetic_eeg_sidecar(*, total_bytes: int) -> bytes:
    """Create deterministic target-free EEG sidecar metadata."""

    return _padded_json(
        {
            "TaskName": "ihc-generated-fixture",
            "EEGReference": "Cz",
            "SamplingFrequency": 1024,
            "PowerLineFrequency": 50,
            "SoftwareFilters": {"Highpass": "n/a", "Lowpass": "n/a"},
            "RecordingType": "continuous",
            "EEGChannelCount": 26,
            "EOGChannelCount": 2,
            "ECGChannelCount": 0,
            "EMGChannelCount": 0,
            "MiscChannelCount": 0,
            "TriggerChannelCount": 1,
            "TaskDescription": "generated-private-text-must-not-escape",
        },
        total_bytes=total_bytes,
    )


def make_synthetic_electrodes_tsv(*, total_bytes: int) -> bytes:
    """Create deterministic finite geometry without using a real montage."""

    rows = []
    denominator = max(len(CORE_EEG_NAMES) - 1, 1)
    for index, name in enumerate(CORE_EEG_NAMES):
        angle = (2.0 * math.pi * index) / denominator
        rows.append(
            [
                name,
                f"{math.cos(angle):.6f}",
                f"{math.sin(angle):.6f}",
                f"{0.5 + index / 100:.6f}",
            ]
        )
    return _padded_tsv(("name", "x", "y", "z"), rows, total_bytes=total_bytes)


def make_synthetic_coordsystem(*, total_bytes: int) -> bytes:
    """Create deterministic target-free coordinate-system metadata."""

    return _padded_json(
        {
            "EEGCoordinateSystem": "CapTrak",
            "EEGCoordinateUnits": "m",
            "EEGCoordinateSystemDescription": "generated-private-text-must-not-escape",
            "AnatomicalLandmarkCoordinates": {"NAS": [0, 1, 0]},
        },
        total_bytes=total_bytes,
    )


def fixture_opener(
    payloads: Mapping[str, bytes], etags: Mapping[str, str]
) -> Callable[[str, int], BinaryIO]:
    """Return a one-open, no-network transport over generated bytes."""

    calls: list[str] = []

    def open_fixture(url: str, maximum_bytes: int) -> BinaryIO:
        if url not in payloads or url in calls:
            raise RoleAuditRefusal(REFUSAL_IDS[5], "fixture URL is unexpected or repeated")
        if len(payloads[url]) > maximum_bytes:
            raise RoleAuditRefusal(REFUSAL_IDS[6], "fixture body exceeds read cap")
        calls.append(url)
        return FixtureResponse(payloads[url], url=url, etag=etags[url])

    open_fixture.calls = calls  # type: ignore[attr-defined]
    return open_fixture


def _synthetic_contract_and_rows(
    contract: Mapping[str, Any], inventory: Mapping[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, bytes], dict[str, str]]:
    import copy

    registered = registered_metadata_rows(contract, inventory)
    fixture_contract = copy.deepcopy(contract)
    fixture_contract["source"]["object_base_url"] = "fixture://iackd-role-geometry"
    reference_by_run: dict[str, bool] = {}
    for row in registered:
        if row["role"] != "channels":
            continue
        run_key, _ = _path_identity(row["path"], row["role"])
        if row["size_bytes"] not in {1752, 1866}:
            raise RoleAuditRefusal(REFUSAL_IDS[3], "unknown registered channel size")
        reference_by_run[run_key] = row["size_bytes"] == 1866
    rows: list[dict[str, Any]] = []
    payloads: dict[str, bytes] = {}
    etags: dict[str, str] = {}
    for registered_row in registered:
        row = dict(registered_row)
        path = row["path"]
        role = row["role"]
        run_key, _ = _path_identity(path, role)
        size = int(row["size_bytes"])
        if role == "channels":
            payload = make_synthetic_channels_tsv(
                include_references=reference_by_run[run_key],
                total_bytes=size,
            )
        elif role == "eeg_sidecar":
            payload = make_synthetic_eeg_sidecar(total_bytes=size)
        elif role == "electrodes":
            payload = make_synthetic_electrodes_tsv(total_bytes=size)
        else:
            payload = make_synthetic_coordsystem(total_bytes=size)
        etag = _sha256_bytes(payload)[:32]
        row["etag"] = etag
        url = f"fixture://iackd-role-geometry/{urllib.parse.quote(path, safe='/._-')}"
        rows.append(row)
        payloads[url] = payload
        etags[url] = etag
    return fixture_contract, rows, payloads, etags


def run_synthetic_qualification(
    output_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> RoleAuditOutcome:
    """Exercise all 316 registered sizes with generated metadata and mocked transport."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    inventory = load_registered_inventory(root)
    fixture_contract, rows, payloads, etags = _synthetic_contract_and_rows(
        contract, inventory
    )
    return run_role_geometry_audit(
        contract=fixture_contract,
        rows=rows,
        opener=fixture_opener(payloads, etags),
        output_path=output_path,
        environ=os.environ if environ is None else environ,
        synthetic=True,
        clock=clock,
        rss_reader=rss_reader,
    )


def _open_url_once(url: str, maximum_bytes: int) -> BinaryIO:
    request = urllib.request.Request(
        url,
        headers={"Accept-Encoding": "identity", "User-Agent": "NeuroDecodeKit-IACKDR/0.1"},
        method="GET",
    )
    try:
        response = urllib.request.build_opener(_RejectRedirect).open(request, timeout=30)
    except RoleAuditRefusal:
        raise
    except Exception as exc:
        raise RoleAuditRefusal(REFUSAL_IDS[4], "single HTTPS request failed") from exc
    length = response.headers.get("Content-Length")
    try:
        too_large = length is not None and int(length) > maximum_bytes
    except ValueError:
        too_large = True
    if too_large:
        response.close()
        raise RoleAuditRefusal(REFUSAL_IDS[6], "response Content-Length exceeds cap")
    return response


def load_implementation_record(
    repo_root: str | Path | None = None,
) -> tuple[dict[str, Any], str]:
    """Validate the future implementation manifest and its tracked hashes."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    record, record_hash, _ = _read_locked_json(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256=None,
    )
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("status")
        != "fixture_qualified_exact_implementation_requires_remote_green_before_real_access"
        or record.get("contract_sha256") != CONTRACT_SHA256
        or record.get("green_registration", {}).get("commit") != REGISTRATION_COMMIT
        or record.get("fixture_qualification", {}).get("all_gates_passed") is not True
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[0], "implementation record mismatch")
    for binding in record.get("tracked_file_hashes", ()):
        relative = _safe_relative_object_path(str(binding.get("path", "")))
        expected = str(binding.get("sha256", ""))
        if HEX64_RE.fullmatch(expected) is None or _sha256_file(root / relative) != expected:
            raise RoleAuditRefusal(REFUSAL_IDS[0], "implementation source hash mismatch")
    return record, record_hash


def _load_authorization_decision(
    root: Path,
    evidence: RealExecutionEvidence,
    implementation_record_sha256: str,
) -> dict[str, Any]:
    decision, observed_hash, _ = _read_locked_json(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=evidence.authorization_decision_sha256,
    )
    implementation = decision.get("green_implementation", {})
    authorization = decision.get("authorization", {})
    if (
        observed_hash != evidence.authorization_decision_sha256
        or decision.get("schema_name") != DECISION_SCHEMA_NAME
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("contract_sha256") != CONTRACT_SHA256
        or decision.get("effective_only_after_decision_commit_pushed_and_both_CI_jobs_green")
        is not True
        or implementation.get("commit") != evidence.implementation_commit
        or implementation.get("push_CI_run_id") != evidence.implementation_ci_run_id
        or implementation.get("base_python_job_id") != evidence.implementation_base_job_id
        or implementation.get("optional_neuro_job_id")
        != evidence.implementation_optional_job_id
        or implementation.get("implementation_registry_sha256")
        != implementation_record_sha256
        or authorization.get("one_registered_public_metadata_audit") is not True
        or authorization.get("real_metadata_requests") != 316
        or authorization.get("real_metadata_body_bytes") != 457_602
        or authorization.get("retries") != 0
        or authorization.get("reruns") != 0
        or not isinstance(decision.get("maintainer_words"), str)
        or not decision["maintainer_words"].strip()
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[1], "exact real-content decision mismatch")
    return decision


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args), cwd=root, check=False, capture_output=True, text=True
    )


def _verify_real_evidence(root: Path, evidence: RealExecutionEvidence) -> None:
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or HEX40_RE.fullmatch(evidence.authorization_commit) is None
        or HEX64_RE.fullmatch(evidence.authorization_decision_sha256) is None
        or min(
            evidence.implementation_ci_run_id,
            evidence.implementation_base_job_id,
            evidence.implementation_optional_job_id,
            evidence.authorization_ci_run_id,
            evidence.authorization_base_job_id,
            evidence.authorization_optional_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise RoleAuditRefusal(REFUSAL_IDS[0], "green or one-shot evidence is malformed")
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.authorization_commit:
        raise RoleAuditRefusal(REFUSAL_IDS[0], "HEAD differs from authorization evidence")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    if clean.returncode or clean.stdout.strip():
        raise RoleAuditRefusal(REFUSAL_IDS[0], "tracked worktree must be clean")
    for ancestor in (REGISTRATION_COMMIT, evidence.implementation_commit):
        if _git(root, "merge-base", "--is-ancestor", ancestor, "HEAD").returncode:
            raise RoleAuditRefusal(REFUSAL_IDS[0], "required green commit is not an ancestor")


def _write_consumed_marker(path: Path, evidence: RealExecutionEvidence) -> None:
    _ensure_output_preflight(path, maximum_output_bytes=64 * 1024)
    marker = {
        "schema_name": "neurodecodekit.iackd_channel_role_geometry_execution_consumed",
        "schema_version": SCHEMA_VERSION,
        "authorization_commit": evidence.authorization_commit,
        "registered_execution_ordinal": 1,
        "retry_allowed": False,
        "rerun_allowed": False,
    }
    _write_atomic_exclusive(path, _canonical_json_bytes(marker))


def execute_registered_audit(
    repo_root: str | Path,
    *,
    evidence: RealExecutionEvidence,
    environ: Mapping[str, str] | None = None,
    opener: Callable[[str, int], BinaryIO] = _open_url_once,
) -> RoleAuditOutcome:
    """Consume the future one-shot real audit after every exact green gate."""

    root = Path(repo_root)
    contract = load_registered_contract(root)
    inventory = load_registered_inventory(root)
    rows = registered_metadata_rows(contract, inventory)
    _verify_real_evidence(root, evidence)
    implementation, implementation_hash = load_implementation_record(root)
    _load_authorization_decision(root, evidence, implementation_hash)
    if implementation.get("execution_state", {}).get("real_execution_consumed") is not False:
        raise RoleAuditRefusal(REFUSAL_IDS[2], "implementation record is not pre-execution")
    consumed_path = root / REAL_CONSUMED_RELATIVE_PATH
    output_path = root / REAL_OUTPUT_RELATIVE_PATH
    _assert_rooted_output_path(root, consumed_path)
    _assert_rooted_output_path(root, output_path)
    if consumed_path.exists() or consumed_path.is_symlink():
        raise RoleAuditRefusal(REFUSAL_IDS[2], "registered execution is already consumed")
    if output_path.exists() or output_path.is_symlink():
        raise RoleAuditRefusal(REFUSAL_IDS[14], "registered output already exists")
    _write_consumed_marker(consumed_path, evidence)
    binding = {
        "commit": evidence.implementation_commit,
        "push_CI_run_id": evidence.implementation_ci_run_id,
        "base_python_job_id": evidence.implementation_base_job_id,
        "optional_neuro_job_id": evidence.implementation_optional_job_id,
        "implementation_registry_sha256": implementation_hash,
        "authorization_commit": evidence.authorization_commit,
        "authorization_push_CI_run_id": evidence.authorization_ci_run_id,
        "authorization_base_python_job_id": evidence.authorization_base_job_id,
        "authorization_optional_neuro_job_id": evidence.authorization_optional_job_id,
        "authorization_decision_sha256": evidence.authorization_decision_sha256,
    }
    return run_role_geometry_audit(
        contract=contract,
        rows=rows,
        opener=opener,
        output_path=output_path,
        environ=os.environ if environ is None else environ,
        synthetic=False,
        implementation_binding=binding,
    )


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the frozen zero-network plan without inspecting a local bundle."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    inventory = load_registered_inventory(root)
    rows = registered_metadata_rows(contract, inventory)
    role_counts = Counter(row["role"] for row in rows)
    return {
        "schema_name": "neurodecodekit.iackd_channel_role_geometry_plan",
        "schema_version": SCHEMA_VERSION,
        "status": "dry_run_real_metadata_access_unauthorized",
        "lane": "IACKD-H2",
        "registered_objects": len(rows),
        "registered_body_bytes": sum(row["size_bytes"] for row in rows),
        "registered_role_counts": dict(sorted(role_counts.items())),
        "network_requests_made": 0,
        "network_bytes_read": 0,
        "local_IACKD_path_stats_or_opens": 0,
        "VHDR_or_sibling_accesses": 0,
        "signal_target_model_or_score_operations": 0,
        "real_execution_authorized": False,
        "next_gate": "exact_implementation_remote_green_then_separate_Tier_C_packet",
        "claim_ceiling": "metadata_compatibility_only",
    }


def load_public_ledger(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
    maximum_bytes: int = 2 * 1024 * 1024,
) -> dict[str, Any]:
    """Load and validate one bounded aggregate ledger without source access."""

    if maximum_bytes <= 0 or maximum_bytes > 2 * 1024 * 1024:
        raise ValueError("ledger input cap must be in (0, 2 MiB]")
    ledger, _, _ = _read_locked_json(
        Path(path), expected_sha256=None, maximum_bytes=maximum_bytes
    )
    contract = load_registered_contract(repo_root)
    validate_public_ledger(ledger, contract=contract)
    return ledger


def summarize_public_ledger(ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact target-free inspection surface."""

    measurements = ledger["measurements"]
    role_map = ledger["role_map_candidate"]
    geometry_groups = ledger["geometry_groups"]
    central_groups = sum(
        int(row["occurrence_count"])
        for row in geometry_groups
        if row["finite_C3_C4_Cz_presence"]
    )
    occipital_groups = sum(
        int(row["occurrence_count"])
        for row in geometry_groups
        if row["finite_O1_Oz_O2_presence"]
    )
    return {
        "status": ledger["status"],
        "proof_posture": ledger["proof_posture"],
        "diagnostic_route": ledger["diagnostic_route"],
        "input_objects": measurements["input_objects"],
        "input_bytes": measurements["input_bytes"],
        "role_object_counts": measurements["role_object_counts"],
        "channel_schema_groups": len(ledger["channel_schema_groups"]),
        "core_schema_count": role_map["core_schema_count"],
        "predictive_EEG_count": len(role_map["predictive_EEG_names"]),
        "role_map_SHA256": role_map["role_map_SHA256"],
        "central_geometry_groups_complete": central_groups,
        "occipital_geometry_groups_complete": occipital_groups,
        "runtime_seconds": measurements["runtime_seconds_through_output_finalization"],
        "peak_RSS_bytes": measurements["peak_RSS_bytes_through_output_finalization"],
        "generated_output_bytes": measurements["generated_output_bytes"],
        "producer_is_causal": measurements["producer_is_causal"],
        "end_to_end_latency_measured": measurements["end_to_end_latency_measured"],
        "warnings": ledger["warnings"],
        "unavailable_fields": ledger["unavailable_fields"],
        "claim_boundary": ledger["claim_boundary"],
    }


def _thread_environment() -> dict[str, str]:
    environ = dict(os.environ)
    for key in THREAD_ENV_KEYS:
        environ[key] = "1"
    return environ


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.preprocess.iackd_channel_roles",
        description=(
            "Dry-run, fixture-qualify, inspect, or separately authorize the bounded "
            "IACKD-H2 BIDS role and geometry audit. The default makes no network request."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true", help="Run generated fixtures only.")
    mode.add_argument("--inspect", metavar="LEDGER", help="Inspect one aggregate ledger.")
    mode.add_argument("--execute", action="store_true", help="Consume the future authorized run.")
    parser.add_argument("--out", help="New JSON output path for --fixture.")
    parser.add_argument("--implementation-commit")
    parser.add_argument("--implementation-ci-run-id", type=int)
    parser.add_argument("--implementation-base-job-id", type=int)
    parser.add_argument("--implementation-optional-job-id", type=int)
    parser.add_argument("--authorization-commit")
    parser.add_argument("--authorization-ci-run-id", type=int)
    parser.add_argument("--authorization-base-job-id", type=int)
    parser.add_argument("--authorization-optional-job-id", type=int)
    parser.add_argument("--authorization-decision-sha256")
    parser.add_argument("--max-input-mib", type=float, default=2.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.inspect:
            ledger = load_public_ledger(
                args.inspect,
                maximum_bytes=int(args.max_input_mib * 1024 * 1024),
            )
            print(json.dumps(summarize_public_ledger(ledger), indent=2, sort_keys=True))
            return 0
        if args.fixture:
            if not args.out:
                raise ValueError("--fixture requires --out")
            outcome = run_synthetic_qualification(
                args.out,
                environ=_thread_environment(),
                rss_reader=_peak_rss_bytes,
            )
            print(json.dumps(summarize_public_ledger(outcome.ledger), indent=2, sort_keys=True))
            return 0
        if not args.execute:
            print(json.dumps(registered_plan(), indent=2, sort_keys=True))
            print("Safety default: zero network requests and zero local IACKD bundle access.")
            return 0
        names = (
            "implementation_commit",
            "implementation_ci_run_id",
            "implementation_base_job_id",
            "implementation_optional_job_id",
            "authorization_commit",
            "authorization_ci_run_id",
            "authorization_base_job_id",
            "authorization_optional_job_id",
            "authorization_decision_sha256",
        )
        missing = [
            f"--{name.replace('_', '-')}" for name in names if getattr(args, name) is None
        ]
        if missing:
            raise ValueError(f"--execute requires: {', '.join(missing)}")
        evidence = RealExecutionEvidence(**{name: getattr(args, name) for name in names})
        outcome = execute_registered_audit(
            _repo_root(), evidence=evidence, environ=_thread_environment()
        )
        print(json.dumps(summarize_public_ledger(outcome.ledger), indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # noqa: BLE001 - friendly CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
