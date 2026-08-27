"""Generated-only COMM-L0 OpenNeuro source identity qualification."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import resource
import sys
import time
import unicodedata
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path(
    "registries/communication_eeg_source_identity_contract.v0.json"
)
CONTRACT_SHA256 = "1c2dc0eaf9321fed7e115c5021002a1c93ba4a631a1e952b6f31b28249de88b3"
GREEN_REGISTRATION_COMMIT = "f4a30e4323834dbd53f5c3cc4abee52829ec016a"
GREEN_REGISTRATION_CI_RUN_ID = 33_035_992_877
GREEN_REGISTRATION_BASE_JOB_ID = 98_398_680_307
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 98_398_680_155
REPORT_SCHEMA_NAME = "neurodecodekit.communication_eeg_source_identity_qualification"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_SELECTED_BYTES = 10 * 1024**3
MAX_TREE_ROWS = 100_000
EXPECTED_PARTICIPANTS = tuple(f"sub-{index:02d}" for index in range(1, 11))
HEX_ID_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
VERSION_ID_RE = re.compile(r"[A-Za-z0-9._~+/=:-]{1,256}\Z")
PARTICIPANT_RE = re.compile(r"sub-[0-9]{2}\Z")
SESSION_RE = re.compile(r"ses-[A-Za-z0-9]+\Z")
RAW_DIRECT_CHILD_RE = re.compile(
    r"(?P<participant>sub-[0-9]{2})/(?P<session>ses-[A-Za-z0-9]+)/eeg/(?P<name>[^/]+)\Z"
)
PROCESSED_SUFFIXES = (".fif", ".npy", ".npz", ".pkl", ".pickle")
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
REFUSAL_IDS = (
    "COMM-L0-F00-registration-or-green-proof",
    "COMM-L0-F01-transport",
    "COMM-L0-F02-strict-JSON-or-GraphQL",
    "COMM-L0-F03-snapshot-anchor",
    "COMM-L0-F04-recursive-tree",
    "COMM-L0-F05-participant-or-session-grid",
    "COMM-L0-F06-raw-unit-or-sidecar-completeness",
    "COMM-L0-F07-selection-cap-or-policy",
    "COMM-L0-F08-resource-output-or-privacy",
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
        "rows",
    }
)


class CommunicationSourceIdentityRefusal(RuntimeError):
    """Fail closed with one stable, aggregate-safe refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown COMM-L0 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class CanonicalSourceIdentity:
    """Aggregate report plus private in-memory canonical rows."""

    report: Mapping[str, Any]
    canonical_rows: tuple[Mapping[str, Any], ...]
    selected_rows: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class QualificationOutcome:
    """One generated qualification result."""

    report: Mapping[str, Any]
    output_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


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
            raise CommunicationSourceIdentityRefusal(
                REFUSAL_IDS[2], "duplicate JSON key"
            )
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "non-finite number")


def _strict_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "non-finite number")
    return parsed


def _strict_json(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "UTF-8 BOM")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "invalid UTF-8") from exc
    if "\x00" in text or any(
        ord(character) < 32 and character not in "\t\n\r" for character in text
    ):
        raise CommunicationSourceIdentityRefusal(
            REFUSAL_IDS[2], "disallowed control character"
        )
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
            parse_float=_strict_float,
        )
    except CommunicationSourceIdentityRefusal:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "invalid JSON") from exc
    if not isinstance(value, dict):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "root is not object")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise CommunicationSourceIdentityRefusal(
            REFUSAL_IDS[2], f"{label} fields differ"
        )


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green COMM-L0 registration."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    if _sha256_file(path) != CONTRACT_SHA256:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[0], "contract hash differs")
    contract = _strict_json(path.read_bytes())
    if contract.get("contract_id") != "COMM-L0-source-identity-contract-v0":
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[0], "contract ID differs")
    if contract.get("authorization_state", {}).get("dataset_specific_GraphQL_request"):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[0], "real authority changed")
    return contract


def _normalize_size(value: Any) -> int:
    if isinstance(value, bool):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "boolean size")
    if isinstance(value, int):
        if value < 0:
            raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "negative size")
        return value
    if isinstance(value, str):
        if not re.fullmatch(r"0|[1-9][0-9]*", value):
            raise CommunicationSourceIdentityRefusal(
                REFUSAL_IDS[4], "noncanonical decimal size"
            )
        return int(value)
    raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "size type differs")


def _normalize_path(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 1024:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "path type or length")
    if unicodedata.normalize("NFC", value) != value:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "path is not NFC")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "path control")
    if value.startswith("/") or "\\" in value or "//" in value:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "unsafe POSIX path")
    if any(character in value for character in ("?", "#", "%")):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "URL-ambiguous path")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "unsafe path component")
    return value


def _decode_version_id(raw_value: str) -> str:
    if not raw_value:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "missing versionId")
    for match in re.finditer("%", raw_value):
        if not re.fullmatch(
            r"[0-9A-Fa-f]{2}", raw_value[match.start() + 1 : match.start() + 3]
        ):
            raise CommunicationSourceIdentityRefusal(
                REFUSAL_IDS[4], "invalid versionId escape"
            )
    try:
        decoded = urllib.parse.unquote(raw_value, errors="strict")
    except UnicodeDecodeError as exc:
        raise CommunicationSourceIdentityRefusal(
            REFUSAL_IDS[4], "versionId decode"
        ) from exc
    if not VERSION_ID_RE.fullmatch(decoded):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "versionId shape")
    return decoded


def _parse_versioned_url(value: Any, filename: str) -> tuple[str, str]:
    if not isinstance(value, str) or len(value) > 4096:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "URL type or length")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "URL parse") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname != "s3.amazonaws.com"
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.fragment
    ):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "URL authority")
    expected_path = f"/openneuro.org/ds003626/{filename}"
    if parsed.path != expected_path:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "URL key mismatch")
    if not parsed.query.startswith("versionId=") or any(
        separator in parsed.query for separator in ("&", ";")
    ):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "URL query")
    version_id = _decode_version_id(parsed.query[len("versionId=") :])
    return expected_path.removeprefix("/openneuro.org/"), version_id


def _canonical_file(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "file is not object")
    _exact_keys(
        value,
        {"id", "filename", "size", "directory", "annexed", "urls"},
        "file",
    )
    object_id = value["id"]
    if not isinstance(object_id, str) or not HEX_ID_RE.fullmatch(object_id):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "file ID")
    filename = _normalize_path(value["filename"])
    if filename == "derivatives" or filename.startswith("derivatives/"):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[7], "derivative path")
    size_bytes = _normalize_size(value["size"])
    if value["directory"] is not False or not isinstance(value["annexed"], bool):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "directory or annexed")
    urls = value["urls"]
    if not isinstance(urls, list) or len(urls) != 1:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "URL list")
    s3_key, version_id = _parse_versioned_url(urls[0], filename)
    return {
        "filename": filename,
        "git_object_id": object_id,
        "size_bytes": size_bytes,
        "annexed": value["annexed"],
        "s3_key": s3_key,
        "s3_version_id": version_id,
    }


def _session_rows(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[tuple[str, str], list[Mapping[str, Any]]], set[str]]:
    sessions: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    participants: set[str] = set()
    for row in rows:
        filename = str(row["filename"])
        first = filename.split("/", 1)[0]
        if PARTICIPANT_RE.fullmatch(first):
            participants.add(first)
        match = RAW_DIRECT_CHILD_RE.fullmatch(filename)
        if match:
            participant = match.group("participant")
            session = match.group("session")
            if not SESSION_RE.fullmatch(session):
                raise CommunicationSourceIdentityRefusal(
                    REFUSAL_IDS[5], "session label"
                )
            sessions.setdefault((participant, session), []).append(row)
    return sessions, participants


def _select_raw_sessions(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], dict[str, Any]]:
    sessions, participants = _session_rows(rows)
    if tuple(sorted(participants)) != EXPECTED_PARTICIPANTS:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[5], "participant set")

    complete: dict[str, set[str]] = {participant: set() for participant in EXPECTED_PARTICIPANTS}
    for (participant, session), values in sessions.items():
        names = [str(row["filename"]) for row in values]
        bdfs = [name for name in names if name.lower().endswith(".bdf")]
        if len(bdfs) != 1:
            raise CommunicationSourceIdentityRefusal(
                REFUSAL_IDS[6], "raw session BDF count"
            )
        companions = [name for name in names if name not in bdfs]
        if not companions:
            raise CommunicationSourceIdentityRefusal(
                REFUSAL_IDS[6], "raw session has no companion"
            )
        if any(name.lower().endswith(PROCESSED_SUFFIXES) for name in companions):
            raise CommunicationSourceIdentityRefusal(
                REFUSAL_IDS[7], "processed array in raw session"
            )
        complete[participant].add(session)

    for participant, session_set in complete.items():
        if len(session_set) != 3:
            raise CommunicationSourceIdentityRefusal(
                REFUSAL_IDS[5], f"three-session grid differs for {participant}"
            )
    reference = complete[EXPECTED_PARTICIPANTS[0]]
    if any(complete[participant] != reference for participant in EXPECTED_PARTICIPANTS):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[5], "common sessions differ")
    selected_session = sorted(reference)[0]
    selected: list[Mapping[str, Any]] = []
    for participant in EXPECTED_PARTICIPANTS:
        selected.extend(sessions[(participant, selected_session)])
    selected.sort(key=lambda row: str(row["filename"]))
    selected_bytes = sum(int(row["size_bytes"]) for row in selected)
    bdf_count = sum(
        str(row["filename"]).lower().endswith(".bdf") for row in selected
    )
    if bdf_count != 10:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[6], "selected BDF count")
    if selected_bytes > MAX_SELECTED_BYTES:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[7], "selected byte cap")
    summary = {
        "participant_count": len(EXPECTED_PARTICIPANTS),
        "sessions_per_participant_selected": 1,
        "common_session_count_observed": len(reference),
        "selected_raw_BDF_count": bdf_count,
        "selected_companion_count": len(selected) - bdf_count,
        "selected_object_count": len(selected),
        "selected_payload_bytes": selected_bytes,
        "selected_payload_cap_bytes": MAX_SELECTED_BYTES,
        "selection_rule": "lexicographically_first_common_complete_raw_session",
    }
    return selected, summary


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key).lower())
            keys.update(_walk_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(_walk_keys(nested))
    return keys


def canonicalize_generated_response(
    payload: bytes,
    *,
    contract: Mapping[str, Any] | None = None,
) -> CanonicalSourceIdentity:
    """Canonicalize one generated OpenNeuro response without network access."""

    if not isinstance(payload, bytes):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "response is not bytes")
    if len(payload) > MAX_RESPONSE_BYTES:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[1], "body cap")
    active_contract = dict(contract) if contract is not None else load_registered_contract()
    root = _strict_json(payload)
    if "errors" in root:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "GraphQL errors")
    _exact_keys(root, {"data"}, "response")
    data = root["data"]
    if not isinstance(data, dict):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "data is not object")
    _exact_keys(data, {"snapshot"}, "data")
    snapshot = data["snapshot"]
    if not isinstance(snapshot, dict):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "snapshot is not object")
    _exact_keys(snapshot, {"id", "tag", "hexsha", "description", "files"}, "snapshot")
    expected_anchor = active_contract["snapshot_anchor_contract"]
    if snapshot["id"] != expected_anchor["id"] or snapshot["tag"] != expected_anchor["tag"]:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[3], "snapshot ID or tag")
    hexsha = snapshot["hexsha"]
    if not isinstance(hexsha, str) or not HEX_ID_RE.fullmatch(hexsha):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[3], "snapshot hexsha")
    description = snapshot["description"]
    if not isinstance(description, dict):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[2], "description is not object")
    _exact_keys(
        description,
        {"id", "Name", "BIDSVersion", "License", "DatasetDOI"},
        "description",
    )
    if description["id"] != hexsha:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[3], "description revision")
    for key in ("Name", "BIDSVersion", "License", "DatasetDOI"):
        if not isinstance(description[key], str) or not description[key]:
            raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[3], f"empty {key}")
    if description["DatasetDOI"] != expected_anchor["DatasetDOI_expected"]:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[3], "dataset DOI")
    files = snapshot["files"]
    if not isinstance(files, list) or not files or len(files) > MAX_TREE_ROWS:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "file list size")
    if any(item is None for item in files):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "null file row")
    rows = [_canonical_file(item) for item in files]
    filenames = [str(row["filename"]) for row in rows]
    if len(set(filenames)) != len(filenames):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[4], "duplicate path")
    rows.sort(key=lambda row: str(row["filename"]))
    if not any(row["filename"] == "dataset_description.json" for row in rows):
        raise CommunicationSourceIdentityRefusal(
            REFUSAL_IDS[4], "dataset_description row missing"
        )
    selected, selected_summary = _select_raw_sessions(rows)

    anchor = {
        "dataset_accession": "ds003626",
        "snapshot_id": snapshot["id"],
        "snapshot_tag": snapshot["tag"],
        "snapshot_hexsha": hexsha,
    }
    critical = {
        key: description[key] for key in ("Name", "BIDSVersion", "License", "DatasetDOI")
    }
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "generated_source_identity_qualified",
        "proof_posture": "generated_only_zero_network_zero_real_or_private_operations",
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_readers_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "contract_sha256": CONTRACT_SHA256,
        },
        "snapshot_anchor": {
            "sha256": _sha256_bytes(_canonical_json_bytes(anchor)),
            "dataset_accession": "ds003626",
            "snapshot_tag": "2.1.2",
        },
        "tree_summary": {
            "sha256": _sha256_bytes(_canonical_json_bytes(rows)),
            "object_count": len(rows),
            "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        },
        "selected_summary": {
            **selected_summary,
            "sha256": _sha256_bytes(_canonical_json_bytes(selected)),
        },
        "critical_metadata": critical,
        "route": "COMM-L0-R1",
        "access_counters": {
            "generated_response_bytes": len(payload),
            "dataset_specific_GraphQL_requests": 0,
            "real_metadata_response_bytes": 0,
            "payload_requests": 0,
            "payload_network_bytes": 0,
            "real_or_private_path_reads": 0,
            "BDF_header_reads": 0,
            "signal_samples": 0,
            "event_target_or_label_rows": 0,
            "model_runs": 0,
            "prediction_sets": 0,
            "scores": 0,
            "claim_upgrades": 0,
        },
        "warnings": [
            "Generated fixture only; no OpenNeuro response or payload was accessed.",
            "Paper-reported channel roles and event grammar remain semantically unverified.",
        ],
        "claim_boundary": {
            "engineering_capability_added": "Strict generated source canonicalization and all-person bounded raw-session selection.",
            "scientific_claim_not_established": "No real EEG, event, target, model, prediction, score, decoding result, or live result was accessed or established.",
        },
    }
    if _walk_keys(report) & FORBIDDEN_PUBLIC_KEYS:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "row identity leaked")
    return CanonicalSourceIdentity(
        report=report,
        canonical_rows=tuple(rows),
        selected_rows=tuple(selected),
    )


def _generated_file(path: str, size: int) -> dict[str, Any]:
    object_id = hashlib.sha1(path.encode("utf-8"), usedforsecurity=False).hexdigest()
    version = hashlib.sha256(path.encode("utf-8")).hexdigest()[:24]
    return {
        "id": object_id,
        "filename": path,
        "size": size,
        "directory": False,
        "annexed": path.lower().endswith(".bdf"),
        "urls": [
            f"https://s3.amazonaws.com/openneuro.org/ds003626/{path}?versionId={version}"
        ],
    }


def build_generated_fixture() -> dict[str, Any]:
    """Construct a small deterministic metadata-only success fixture."""

    files = [_generated_file("dataset_description.json", 512)]
    for participant_index, participant in enumerate(EXPECTED_PARTICIPANTS, start=1):
        for session_index in range(1, 4):
            session = f"ses-{session_index:02d}"
            prefix = f"{participant}/{session}/eeg/{participant}_{session}_task-innerspeech"
            files.extend(
                [
                    _generated_file(
                        f"{prefix}_eeg.bdf",
                        100_000 + participant_index * 100 + session_index,
                    ),
                    _generated_file(f"{prefix}_eeg.json", 400),
                    _generated_file(f"{prefix}_channels.tsv", 800),
                    _generated_file(f"{prefix}_events.tsv", 1200),
                ]
            )
    hexsha = hashlib.sha1(
        b"generated-communication-source-identity-v0", usedforsecurity=False
    ).hexdigest()
    return {
        "data": {
            "snapshot": {
                "id": "ds003626:2.1.2",
                "tag": "2.1.2",
                "hexsha": hexsha,
                "description": {
                    "id": hexsha,
                    "Name": "Generated Thinking Out Loud fixture",
                    "BIDSVersion": "1.7.0",
                    "License": "generated-test-only",
                    "DatasetDOI": "10.18112/openneuro.ds003626.v2.1.2",
                },
                "files": files,
            }
        }
    }


def generated_fixture_bytes(value: Mapping[str, Any] | None = None) -> bytes:
    """Serialize the deterministic generated fixture."""

    return _canonical_json_bytes(dict(value) if value is not None else build_generated_fixture())


def _mutate_path(row: dict[str, Any], old: str, new: str) -> None:
    path = str(row["filename"])
    if old not in path:
        raise AssertionError("generated mutation source is absent")
    new_path = path.replace(old, new)
    replacement = _generated_file(new_path, int(row["size"]))
    row.update(replacement)


def _expect_refusal(name: str, fixture: dict[str, Any], expected: str) -> dict[str, str]:
    try:
        canonicalize_generated_response(generated_fixture_bytes(fixture))
    except CommunicationSourceIdentityRefusal as exc:
        if exc.refusal_id != expected:
            raise AssertionError(f"{name} returned {exc.refusal_id}, expected {expected}") from exc
        return {"case": name, "refusal_id": exc.refusal_id}
    raise AssertionError(f"{name} unexpectedly passed")


def _qualification_cases(base: dict[str, Any]) -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["id"] = "ds003626:2.1.1"
    cases.append(_expect_refusal("wrong_snapshot", fixture, REFUSAL_IDS[3]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["description"]["DatasetDOI"] = "wrong"
    cases.append(_expect_refusal("wrong_DOI", fixture, REFUSAL_IDS[3]))

    fixture = copy.deepcopy(base)
    fixture["errors"] = [{"message": "generated"}]
    cases.append(_expect_refusal("graphql_errors", fixture, REFUSAL_IDS[2]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["unknown"] = 1
    cases.append(_expect_refusal("unknown_field", fixture, REFUSAL_IDS[2]))

    fixture = copy.deepcopy(base)
    files = fixture["data"]["snapshot"]["files"]
    files.append(copy.deepcopy(files[1]))
    cases.append(_expect_refusal("duplicate_path", fixture, REFUSAL_IDS[4]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"][1]["filename"] = "../unsafe.bdf"
    cases.append(_expect_refusal("unsafe_path", fixture, REFUSAL_IDS[4]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"][1]["urls"][0] = "https://example.com/x"
    cases.append(_expect_refusal("wrong_URL", fixture, REFUSAL_IDS[4]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"][1]["size"] = "01"
    cases.append(_expect_refusal("noncanonical_size", fixture, REFUSAL_IDS[4]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"][1]["directory"] = True
    cases.append(_expect_refusal("directory_row", fixture, REFUSAL_IDS[4]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"] = [
        row
        for row in fixture["data"]["snapshot"]["files"]
        if not str(row["filename"]).startswith("sub-10/")
    ]
    cases.append(_expect_refusal("missing_participant", fixture, REFUSAL_IDS[5]))

    fixture = copy.deepcopy(base)
    template = [
        copy.deepcopy(row)
        for row in fixture["data"]["snapshot"]["files"]
        if str(row["filename"]).startswith("sub-10/")
    ]
    for row in template:
        _mutate_path(row, "sub-10", "sub-11")
    fixture["data"]["snapshot"]["files"].extend(template)
    cases.append(_expect_refusal("extra_participant", fixture, REFUSAL_IDS[5]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"] = [
        row
        for row in fixture["data"]["snapshot"]["files"]
        if not (
            str(row["filename"]).startswith("sub-01/ses-03/")
            and str(row["filename"]).endswith(".bdf")
        )
    ]
    cases.append(_expect_refusal("missing_session_BDF", fixture, REFUSAL_IDS[6]))

    fixture = copy.deepcopy(base)
    duplicate = copy.deepcopy(fixture["data"]["snapshot"]["files"][1])
    _mutate_path(duplicate, "_eeg.bdf", "_copy.bdf")
    fixture["data"]["snapshot"]["files"].append(duplicate)
    cases.append(_expect_refusal("multiple_session_BDF", fixture, REFUSAL_IDS[6]))

    fixture = copy.deepcopy(base)
    for row in fixture["data"]["snapshot"]["files"]:
        if str(row["filename"]).startswith("sub-10/ses-03/"):
            _mutate_path(row, "ses-03", "ses-04")
    cases.append(_expect_refusal("different_session_set", fixture, REFUSAL_IDS[5]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"] = [
        row
        for row in fixture["data"]["snapshot"]["files"]
        if not (
            str(row["filename"]).startswith("sub-01/ses-01/")
            and not str(row["filename"]).endswith(".bdf")
        )
    ]
    cases.append(_expect_refusal("missing_companions", fixture, REFUSAL_IDS[6]))

    fixture = copy.deepcopy(base)
    processed = _generated_file(
        "sub-01/ses-01/eeg/sub-01_ses-01_task-innerspeech_eeg.fif", 500
    )
    fixture["data"]["snapshot"]["files"].append(processed)
    cases.append(_expect_refusal("processed_in_raw_dir", fixture, REFUSAL_IDS[7]))

    fixture = copy.deepcopy(base)
    fixture["data"]["snapshot"]["files"].append(
        _generated_file("derivatives/summary.json", 20)
    )
    cases.append(_expect_refusal("derivative_path", fixture, REFUSAL_IDS[7]))

    fixture = copy.deepcopy(base)
    for row in fixture["data"]["snapshot"]["files"]:
        if str(row["filename"]).startswith("sub-01/ses-01/") and str(
            row["filename"]
        ).endswith(".bdf"):
            row["size"] = MAX_SELECTED_BYTES + 1
            break
    cases.append(_expect_refusal("selected_cap", fixture, REFUSAL_IDS[7]))
    return cases


def _assert_output_path(path: Path) -> None:
    if path.exists() or path.is_symlink():
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "output exists")
    parent = path.parent
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "output parent")


def qualify_generated_source_identity(output: str | Path) -> QualificationOutcome:
    """Run the sole bounded generated COMM-L0 qualification."""

    started = time.monotonic()
    output_path = Path(output)
    _assert_output_path(output_path)
    contract = load_registered_contract()
    for key in THREAD_ENV_KEYS:
        if os.environ.get(key) not in {None, "1"}:
            raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "thread setting")
    base = build_generated_fixture()
    payload = generated_fixture_bytes(base)
    first = canonicalize_generated_response(payload, contract=contract)
    replay = copy.deepcopy(base)
    replay["data"]["snapshot"]["files"].reverse()
    second = canonicalize_generated_response(generated_fixture_bytes(replay), contract=contract)
    if first.report != second.report:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "replay mismatch")
    refused = _qualification_cases(base)

    duplicate_key_refused = False
    try:
        canonicalize_generated_response(b'{"data":{},"data":{}}', contract=contract)
    except CommunicationSourceIdentityRefusal as exc:
        duplicate_key_refused = exc.refusal_id == REFUSAL_IDS[2]
    invalid_utf8_refused = False
    try:
        canonicalize_generated_response(b"\xff", contract=contract)
    except CommunicationSourceIdentityRefusal as exc:
        invalid_utf8_refused = exc.refusal_id == REFUSAL_IDS[2]
    if not duplicate_key_refused or not invalid_utf8_refused:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "raw JSON refusal")

    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    result = {
        **first.report,
        "status": "generated_qualification_passed_consumed",
        "qualification": {
            "success_replays": 2,
            "adversarial_refusals": len(refused) + 2,
            "case_names": sorted(row["case"] for row in refused)
            + ["duplicate_JSON_key", "invalid_UTF8"],
            "all_expected_refusals_passed": True,
            "consumed": True,
            "rerun_allowed": False,
        },
        "measurements": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "generated_input_bytes": len(payload),
            "generated_output_bytes": 0,
            "network_bytes": 0,
            "real_payload_bytes": 0,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
    }
    result_bytes = _canonical_json_bytes(result)
    for _attempt in range(3):
        result["measurements"]["generated_output_bytes"] = len(result_bytes)
        updated = _canonical_json_bytes(result)
        if len(updated) == len(result_bytes):
            result_bytes = updated
            break
        result_bytes = updated
    if result["measurements"]["generated_output_bytes"] != len(result_bytes):
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "output measurement")
    if runtime > MAX_RUNTIME_SECONDS or peak_rss > MAX_PEAK_RSS_BYTES:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "runtime or RSS")
    if len(payload) > MAX_RESPONSE_BYTES or len(result_bytes) > MAX_OUTPUT_BYTES:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "input or output cap")
    temporary = output_path.with_name(f".{output_path.name}.tmp-{os.getpid()}")
    if temporary.exists() or temporary.is_symlink():
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "temporary exists")
    try:
        temporary.write_bytes(result_bytes)
        if output_path.exists() or output_path.is_symlink():
            raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "output race")
        os.link(temporary, output_path)
    finally:
        temporary.unlink(missing_ok=True)
    return QualificationOutcome(
        report=result,
        output_path=output_path,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        generated_input_bytes=len(payload),
        generated_output_bytes=len(result_bytes),
    )


def inspect_report(path: str | Path) -> dict[str, Any]:
    """Inspect one aggregate generated report without exposing row identities."""

    source = Path(path)
    if not source.is_file() or source.is_symlink():
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "report path")
    payload = source.read_bytes()
    if len(payload) > MAX_OUTPUT_BYTES:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "report cap")
    report = _strict_json(payload)
    if report.get("schema_name") != REPORT_SCHEMA_NAME:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "report schema")
    if _walk_keys(report) & FORBIDDEN_PUBLIC_KEYS:
        raise CommunicationSourceIdentityRefusal(REFUSAL_IDS[8], "report privacy")
    return {
        "schema_name": report["schema_name"],
        "schema_version": report["schema_version"],
        "status": report["status"],
        "route": report["route"],
        "snapshot_anchor": report["snapshot_anchor"],
        "tree_summary": report["tree_summary"],
        "selected_summary": report["selected_summary"],
        "qualification": report.get("qualification"),
        "measurements": report.get("measurements"),
        "warnings": report["warnings"],
        "claim_boundary": report["claim_boundary"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.communication_eeg_source_identity"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Show the generated-only COMM-L0 plan.")
    qualify = commands.add_parser("qualify", help="Run one generated qualification.")
    qualify.add_argument("--output", required=True)
    inspect = commands.add_parser("inspect", help="Inspect one aggregate result.")
    inspect.add_argument("--input", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            value = {
                "schema_name": "neurodecodekit.communication_eeg_source_identity_plan",
                "schema_version": SCHEMA_VERSION,
                "status": "generated_only_no_network_or_real_path_mode",
                "commands": ["plan", "qualify", "inspect"],
                "dataset_specific_GraphQL_authorized": False,
                "payload_authorized": False,
                "maximum_selected_payload_bytes": MAX_SELECTED_BYTES,
            }
        elif args.command == "qualify":
            value = qualify_generated_source_identity(args.output).report
        else:
            value = inspect_report(args.input)
    except CommunicationSourceIdentityRefusal as exc:
        print(_canonical_json_bytes({"status": "refused", "route": exc.refusal_id}).decode(), end="")
        return 2
    print(_canonical_json_bytes(value).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
