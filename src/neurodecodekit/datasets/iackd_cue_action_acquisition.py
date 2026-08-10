"""One-shot OpenNeuro acquisition for the registered IACKD reversal study."""

from __future__ import annotations

import hashlib
import io
import json
import os
import resource
import shutil
import stat
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path("registries/iackd_cue_action_dissociation_contract.v0.json")
DECISION_RELATIVE_PATH = Path(
    "registries/iackd_cue_action_dissociation_authorization_decision.v0.json"
)
INVENTORY_RELATIVE_PATH = Path("registries/iackd_openneuro_metadata_inventory.v0.json")
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/iackd_cue_action_dissociation_implementation.v0.json"
)
CONTRACT_SHA256 = "bb2433bb1d2b4a6257a80382764c5392aad0eaa65fa34427f76b52838755f814"
DECISION_SHA256 = "41ef8518110dfbcf442d8f6d5fdddbfbf6d11e84b73f64c848c671815ecccc08"
INVENTORY_SHA256 = "aeaa4928192cca9086fcb0abf4711147c68a68ef5c5aacda2ebc67d162a1ef19"
DECISION_COMMIT = "1f48b3011e19ba8da35a18c3d3395813f159adc2"
DECISION_CI_RUN_ID = 31403012709
DECISION_BASE_JOB_ID = 93502398308
DECISION_OPTIONAL_JOB_ID = 93502398753
CHUNK_BYTES = 1024 * 1024
MAX_LOCKED_JSON_BYTES = 2 * 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


class IACKDAcquisitionRefusal(RuntimeError):
    """A preflight failed before the one-shot acquisition was consumed."""


class IACKDAcquisitionFailure(RuntimeError):
    """The one-shot acquisition was consumed and then failed closed."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


@dataclass(frozen=True)
class ImplementationEvidence:
    implementation_commit: str
    implementation_ci_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


@dataclass(frozen=True)
class AcquisitionOutcome:
    status: str
    manifest: dict[str, Any]
    manifest_path: Path
    receipt_path: Path

    @property
    def passed(self) -> bool:
        return self.status == "passed"


URLopener = Callable[[str, int], BinaryIO]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise IACKDAcquisitionRefusal(f"hash input is not a regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    digest = hashlib.sha256()
    with os.fdopen(descriptor, "rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    observed_path = os.lstat(path)
    if stat.S_ISLNK(observed_path.st_mode) or not stat.S_ISREG(observed_path.st_mode):
        raise IACKDAcquisitionRefusal(f"locked JSON is not a regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        payload = handle.read(MAX_LOCKED_JSON_BYTES + 1)
    if len(payload) > MAX_LOCKED_JSON_BYTES:
        raise IACKDAcquisitionRefusal(f"locked JSON exceeds 2 MiB: {path}")
    observed = _sha256_bytes(payload)
    if expected_sha256 == "TO_BE_LOCKED":
        raise IACKDAcquisitionRefusal("decision hash has not been locked")
    if observed != expected_sha256:
        raise IACKDAcquisitionRefusal(
            f"locked JSON hash mismatch for {path}: expected {expected_sha256}, got {observed}"
        )
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise IACKDAcquisitionRefusal(f"locked JSON must be an object: {path}")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    if contract.get("schema_name") != "neurodecodekit.iackd_cue_action_dissociation_contract":
        raise IACKDAcquisitionRefusal("IACKD contract schema mismatch")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise IACKDAcquisitionRefusal("IACKD contract version mismatch")
    binding = contract.get("dataset_binding", {})
    if binding.get("selected_object_count") != 1340:
        raise IACKDAcquisitionRefusal("IACKD contract does not bind 1,340 objects")
    return contract


def load_registered_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    if decision.get("schema_name") != (
        "neurodecodekit.iackd_cue_action_dissociation_authorization_decision"
    ):
        raise IACKDAcquisitionRefusal("IACKD decision schema mismatch")
    if decision.get("authorized_contract", {}).get("sha256") != CONTRACT_SHA256:
        raise IACKDAcquisitionRefusal("IACKD decision does not bind the contract")
    return decision


def load_registered_inventory(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    inventory = _load_locked_json(root / INVENTORY_RELATIVE_PATH, INVENTORY_SHA256)
    if inventory.get("schema_name") != "neurodecodekit.iackd_openneuro_metadata_inventory":
        raise IACKDAcquisitionRefusal("IACKD inventory schema mismatch")
    if len(inventory.get("selected_objects", [])) != 1340:
        raise IACKDAcquisitionRefusal("IACKD inventory object count mismatch")
    return inventory


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact plan without path stats, imports, or network access."""

    contract = load_registered_contract(repo_root)
    load_registered_decision(repo_root)
    inventory = load_registered_inventory(repo_root)
    binding = contract["dataset_binding"]
    acquisition = contract["acquisition_contract"]
    return {
        "schema_name": "neurodecodekit.iackd_acquisition_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run_no_registered_path_stat_no_network",
        "dataset_id": binding["accession"],
        "dataset_version": binding["version"],
        "participants": binding["participant_ids"],
        "BIDS_runs": binding["bids_run_count"],
        "object_count": binding["selected_object_count"],
        "payload_bytes": binding["exact_selected_payload_bytes"],
        "inventory_sha256": inventory["selection"]["canonical_identity_sha256"],
        "payload_root": acquisition["payload_root"],
        "temporary_root": acquisition["temporary_root"],
        "receipt_root": acquisition["receipt_root"],
        "caps": contract["resource_caps"]["acquisition"],
        "next_gate": "exact_implementation_commit_and_both_ci_jobs_must_be_green",
        "warnings": [
            "dry_run_only_no_registered_path_stat_or_network_access",
            "execute_consumes_the_single_no_retry_acquisition",
            "payload_content_remains_opaque_during_acquisition",
            "acquisition_is_not_an_EEG_or_decoding_result",
        ],
    }


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise IACKDAcquisitionFailure("path", f"unsafe relative path: {value!r}")
    return path


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    mismatches = {key: environ.get(key) for key in THREAD_ENV_KEYS if environ.get(key) != "1"}
    if mismatches:
        raise IACKDAcquisitionRefusal(f"one-thread environment is not exact: {mismatches}")


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def _validate_implementation_registry(
    repo_root: Path,
    evidence: ImplementationEvidence,
) -> dict[str, Any]:
    if _git(repo_root, "rev-parse", "HEAD").stdout.strip() != evidence.implementation_commit:
        raise IACKDAcquisitionRefusal("current HEAD differs from implementation evidence")
    if _git(repo_root, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise IACKDAcquisitionRefusal("tracked worktree changes are forbidden")
    if _git(repo_root, "merge-base", "--is-ancestor", DECISION_COMMIT, "HEAD").returncode:
        raise IACKDAcquisitionRefusal("green decision is not an implementation ancestor")
    if min(
        evidence.implementation_ci_run_id,
        evidence.base_python_job_id,
        evidence.optional_neuro_job_id,
    ) <= 0:
        raise IACKDAcquisitionRefusal("positive implementation CI identifiers are required")
    registry_path = repo_root / IMPLEMENTATION_RELATIVE_PATH
    if _git(repo_root, "cat-file", "-e", f"HEAD:{IMPLEMENTATION_RELATIVE_PATH}").returncode:
        raise IACKDAcquisitionRefusal("implementation registry is not tracked at HEAD")
    observed_registry = os.lstat(registry_path)
    if stat.S_ISLNK(observed_registry.st_mode) or not stat.S_ISREG(observed_registry.st_mode):
        raise IACKDAcquisitionRefusal("implementation registry is not a regular file")
    descriptor = os.open(registry_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        registry_payload = handle.read(MAX_LOCKED_JSON_BYTES + 1)
    if len(registry_payload) > MAX_LOCKED_JSON_BYTES:
        raise IACKDAcquisitionRefusal("implementation registry exceeds 2 MiB")
    try:
        registry = json.loads(registry_payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IACKDAcquisitionRefusal("implementation registry is not valid JSON") from exc
    if not isinstance(registry, dict):
        raise IACKDAcquisitionRefusal("implementation registry root must be an object")
    if registry.get("schema_name") != "neurodecodekit.iackd_cue_action_dissociation_implementation":
        raise IACKDAcquisitionRefusal("implementation registry schema mismatch")
    expected_parent = {
        "commit": DECISION_COMMIT,
        "push_ci_run_id": DECISION_CI_RUN_ID,
        "base_python_job_id": DECISION_BASE_JOB_ID,
        "optional_neuro_job_id": DECISION_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
    }
    if registry.get("green_authorization_decision") != expected_parent:
        raise IACKDAcquisitionRefusal("implementation registry decision proof mismatch")
    for row in registry.get("tracked_file_hashes", []):
        path = repo_root / _safe_relative_path(str(row["path"]))
        if _file_sha256(path) != row["sha256"]:
            raise IACKDAcquisitionRefusal(f"implementation hash mismatch: {row['path']}")
    if registry.get("fixture_qualification", {}).get("all_gates_passed") is not True:
        raise IACKDAcquisitionRefusal("generated-fixture qualification is not passed")
    if any(registry.get("implementation_access_counters", {}).values()):
        raise IACKDAcquisitionRefusal("implementation registry reports a real operation")
    return registry


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise IACKDAcquisitionFailure("network", f"redirect forbidden: {newurl}")


def _open_url_once(url: str, maximum_bytes: int) -> BinaryIO:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NeuroDecodeKit-IACKD/0.1"},
        method="GET",
    )
    response = urllib.request.build_opener(_RejectRedirect).open(request, timeout=120)
    status_code = getattr(response, "status", response.getcode())
    if status_code != 200:
        response.close()
        raise IACKDAcquisitionFailure("network", f"unexpected HTTP status {status_code}")
    content_length = response.headers.get("Content-Length")
    if content_length is not None and int(content_length) > maximum_bytes:
        response.close()
        raise IACKDAcquisitionFailure("network", "response Content-Length exceeds cap")
    return response


@contextmanager
def _managed_stream(stream: BinaryIO) -> Iterator[BinaryIO]:
    try:
        yield stream
    finally:
        stream.close()


def _read_bounded(stream: BinaryIO, maximum_bytes: int) -> bytes:
    payload = stream.read(maximum_bytes + 1)
    if len(payload) > maximum_bytes:
        raise IACKDAcquisitionFailure("metadata", "metadata response exceeds cap")
    return payload


def _header(stream: BinaryIO, name: str) -> str | None:
    headers = getattr(stream, "headers", None)
    if headers is None:
        return None
    return headers.get(name)


def _final_url(stream: BinaryIO) -> str | None:
    getter = getattr(stream, "geturl", None)
    return str(getter()) if callable(getter) else None


def _normalize_etag(value: str) -> str:
    return value.strip().strip('"').lower()


def _listing_objects(payload: bytes) -> tuple[list[dict[str, Any]], bool, str | None]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise IACKDAcquisitionFailure("metadata", "S3 listing XML is malformed") from exc
    rows: list[dict[str, Any]] = []
    truncated = False
    continuation = None
    for node in root:
        local = node.tag.rsplit("}", 1)[-1]
        if local == "IsTruncated":
            truncated = (node.text or "").strip().lower() == "true"
        elif local == "NextContinuationToken":
            continuation = node.text
        elif local == "Contents":
            values = {child.tag.rsplit("}", 1)[-1]: child.text for child in node}
            required = ("Key", "Size", "ETag", "LastModified")
            if any(values.get(key) is None for key in required):
                raise IACKDAcquisitionFailure("metadata", "S3 object identity is incomplete")
            key = str(values["Key"])
            if not key.startswith("ds006840/"):
                raise IACKDAcquisitionFailure("metadata", "S3 object escaped dataset prefix")
            rows.append(
                {
                    "path": key.removeprefix("ds006840/"),
                    "size_bytes": int(str(values["Size"])),
                    "etag": _normalize_etag(str(values["ETag"])),
                    "last_modified": str(values["LastModified"]),
                }
            )
    if truncated and not continuation:
        raise IACKDAcquisitionFailure("metadata", "truncated listing lacks continuation token")
    if not truncated and continuation:
        raise IACKDAcquisitionFailure("metadata", "terminal listing has continuation token")
    return rows, truncated, continuation


def _canonical_identity(rows: Sequence[Mapping[str, Any]]) -> tuple[int, str]:
    identity = [
        {
            "path": str(row["path"]),
            "size_bytes": int(row["size_bytes"]),
            "etag": str(row["etag"]),
            "last_modified": str(row["last_modified"]),
        }
        for row in sorted(rows, key=lambda item: str(item["path"]))
    ]
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(payload), _sha256_bytes(payload)


def validate_metadata_documents(
    contract: Mapping[str, Any],
    inventory: Mapping[str, Any],
    dataset_description: bytes,
    changes: bytes,
    listing_pages: Sequence[bytes],
) -> dict[str, Any]:
    """Validate the registered metadata snapshot before any payload request."""

    source = inventory["source_documents"]
    if _sha256_bytes(dataset_description) != source["dataset_description"]["sha256"]:
        raise IACKDAcquisitionFailure("metadata", "dataset description hash mismatch")
    if _sha256_bytes(changes) != source["changes"]["sha256"]:
        raise IACKDAcquisitionFailure("metadata", "CHANGES hash mismatch")
    try:
        description = json.loads(dataset_description)
    except json.JSONDecodeError as exc:
        raise IACKDAcquisitionFailure("metadata", "dataset description is malformed") from exc
    binding = contract["dataset_binding"]
    doi = str(description.get("DatasetDOI", "")).removeprefix("doi:")
    if description.get("BIDSVersion") != binding["bids_version"]:
        raise IACKDAcquisitionFailure("metadata", "BIDS version mismatch")
    if description.get("License") != binding["license"]:
        raise IACKDAcquisitionFailure("metadata", "license mismatch")
    if doi != binding["dataset_doi"]:
        raise IACKDAcquisitionFailure("metadata", "dataset DOI mismatch")
    if binding["version"] not in changes.decode("utf-8", "strict"):
        raise IACKDAcquisitionFailure("metadata", "CHANGES lacks registered version")
    if len(listing_pages) != 2:
        raise IACKDAcquisitionFailure("metadata", "exactly two listing pages are required")
    listed: list[dict[str, Any]] = []
    first, first_truncated, _ = _listing_objects(listing_pages[0])
    second, second_truncated, _ = _listing_objects(listing_pages[1])
    if not first_truncated or second_truncated:
        raise IACKDAcquisitionFailure("metadata", "listing page truncation pattern mismatch")
    listed.extend(first)
    listed.extend(second)
    metadata = contract["metadata_reverification"]
    if len(listed) != metadata["expected_listed_object_count"]:
        raise IACKDAcquisitionFailure("metadata", "listed object count mismatch")
    if sum(row["size_bytes"] for row in listed) != metadata["expected_listed_total_bytes"]:
        raise IACKDAcquisitionFailure("metadata", "listed byte total mismatch")
    if len({row["path"] for row in listed}) != len(listed):
        raise IACKDAcquisitionFailure("metadata", "duplicate listed object path")
    expected = [
        {
            "path": str(row["path"]),
            "size_bytes": int(row["size_bytes"]),
            "etag": str(row["etag"]),
            "last_modified": str(row["last_modified"]),
        }
        for row in sorted(inventory["selected_objects"], key=lambda row: row["path"])
    ]
    observed_map = {row["path"]: row for row in listed}
    observed = [observed_map.get(row["path"]) for row in expected]
    if any(row is None for row in observed) or observed != expected:
        raise IACKDAcquisitionFailure("metadata", "selected object identity drift")
    identity_bytes, identity_sha256 = _canonical_identity(expected)
    if identity_sha256 != metadata["canonical_identity_sha256"]:
        raise IACKDAcquisitionFailure("metadata", "selected canonical identity mismatch")
    return {
        "metadata_requests": 4,
        "metadata_body_bytes": (
            len(dataset_description) + len(changes) + sum(len(page) for page in listing_pages)
        ),
        "listed_object_count": len(listed),
        "listed_total_bytes": sum(row["size_bytes"] for row in listed),
        "selected_object_count": len(expected),
        "selected_payload_bytes": sum(row["size_bytes"] for row in expected),
        "canonical_identity_bytes": identity_bytes,
        "canonical_identity_sha256": identity_sha256,
    }


def fetch_registered_metadata(
    contract: Mapping[str, Any],
    inventory: Mapping[str, Any],
    opener: URLopener,
) -> tuple[dict[str, Any], int]:
    cap = int(contract["resource_caps"]["acquisition"]["metadata_body_bytes"])
    source = inventory["source_documents"]
    endpoint = contract["metadata_reverification"]["list_objects_endpoint"]
    query = contract["metadata_reverification"]["list_objects_query"]
    urls = [source["dataset_description"]["url"], source["changes"]["url"]]
    bodies = []
    total = 0
    for url in urls:
        with _managed_stream(opener(url, cap - total)) as stream:
            final = _final_url(stream)
            if final is not None and final != url:
                raise IACKDAcquisitionFailure("metadata", "metadata response URL mismatch")
            payload = _read_bounded(stream, cap - total)
        bodies.append(payload)
        total += len(payload)
    first_url = f"{endpoint}?{query}"
    with _managed_stream(opener(first_url, cap - total)) as stream:
        final = _final_url(stream)
        if final is not None and final != first_url:
            raise IACKDAcquisitionFailure("metadata", "listing response URL mismatch")
        first_page = _read_bounded(stream, cap - total)
    total += len(first_page)
    _, truncated, token = _listing_objects(first_page)
    if not truncated or not token:
        raise IACKDAcquisitionFailure("metadata", "first listing page is not continuable")
    second_url = f"{first_url}&continuation-token={urllib.parse.quote(token, safe='')}"
    with _managed_stream(opener(second_url, cap - total)) as stream:
        final = _final_url(stream)
        if final is not None and final != second_url:
            raise IACKDAcquisitionFailure("metadata", "listing response URL mismatch")
        second_page = _read_bounded(stream, cap - total)
    total += len(second_page)
    result = validate_metadata_documents(
        contract,
        inventory,
        bodies[0],
        bodies[1],
        (first_page, second_page),
    )
    if result["metadata_body_bytes"] != total:
        raise IACKDAcquisitionFailure("metadata", "metadata byte accounting mismatch")
    return result, total


def _write_json_exclusive(path: Path, value: Mapping[str, Any], cap: int) -> int:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > cap:
        raise IACKDAcquisitionFailure("output", "JSON output exceeds cap")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError:
        raise IACKDAcquisitionRefusal(f"refusing to replace output: {path}") from None
    return len(payload)


def _assert_safe_path_chain(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise IACKDAcquisitionRefusal("registered path escapes the workspace root") from exc
    current = root
    for part in relative.parts:
        current /= part
        if not current.exists() and not current.is_symlink():
            continue
        observed = os.lstat(current)
        if stat.S_ISLNK(observed.st_mode):
            raise IACKDAcquisitionRefusal(f"registered path crosses a symlink: {current}")


def _tree_bytes_regular(path: Path) -> int:
    total = 0
    for current_root, directories, filenames in os.walk(path, followlinks=False):
        current = Path(current_root)
        if any((current / name).is_symlink() for name in directories):
            raise IACKDAcquisitionFailure("output", "output tree contains a symlink directory")
        for filename in filenames:
            candidate = current / filename
            if candidate.is_symlink():
                raise IACKDAcquisitionFailure("output", "output tree contains a symlink file")
            total += candidate.stat().st_size
    return total


def _human_receipt(manifest: Mapping[str, Any]) -> bytes:
    measurements = manifest["measurements"]
    text = (
        "# IACKD Acquisition Receipt\n\n"
        f"Status: **{manifest['status']}**\n\n"
        f"Objects: {measurements['payload_requests']}\n\n"
        f"Payload bytes: {measurements['payload_bytes']}\n\n"
        f"Metadata body bytes: {measurements['metadata_body_bytes']}\n\n"
        f"Runtime seconds: {measurements['runtime_seconds']}\n\n"
        f"Peak RSS bytes: {measurements['peak_rss_bytes']}\n\n"
        "Payload content was not parsed. This receipt establishes acquisition integrity only.\n"
    )
    return text.encode("utf-8")


def _validate_payload_response(
    stream: BinaryIO,
    requested_url: str,
    row: Mapping[str, Any],
) -> None:
    final = _final_url(stream)
    if final != requested_url:
        raise IACKDAcquisitionFailure("network", "payload response URL mismatch")
    length = _header(stream, "Content-Length")
    if length is None or int(length) != int(row["size_bytes"]):
        raise IACKDAcquisitionFailure("network", "payload Content-Length mismatch")
    etag = _header(stream, "ETag")
    if etag is None or _normalize_etag(etag) != str(row["etag"]).lower():
        raise IACKDAcquisitionFailure("network", "payload ETag mismatch")


def run_acquisition(
    *,
    workspace_root: str | Path,
    contract: Mapping[str, Any],
    inventory: Mapping[str, Any],
    opener: URLopener,
    environ: Mapping[str, str],
    enforce_registered_roots: bool,
    minimum_free_disk_bytes: int | None = None,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> AcquisitionOutcome:
    """Run the one-shot acquisition core with real or mocked transport."""

    _check_thread_environment(environ)
    root = Path(workspace_root).resolve()
    acquisition = contract["acquisition_contract"]
    caps = contract["resource_caps"]["acquisition"]
    payload_root = root / _safe_relative_path(acquisition["payload_root"])
    temporary_root = root / _safe_relative_path(acquisition["temporary_root"])
    receipt_root = root / _safe_relative_path(acquisition["receipt_root"])
    for path in (payload_root, temporary_root, receipt_root):
        _assert_safe_path_chain(root, path)
    if enforce_registered_roots:
        if contract != load_registered_contract(root):
            raise IACKDAcquisitionRefusal("real acquisition contract differs from registration")
        if inventory != load_registered_inventory(root):
            raise IACKDAcquisitionRefusal("real acquisition inventory differs from registration")
    selected = sorted(inventory.get("selected_objects", []), key=lambda row: row["path"])
    selected_paths = [str(row.get("path", "")) for row in selected]
    if len(selected) != int(caps["payload_requests"]):
        raise IACKDAcquisitionRefusal("selected-object count differs from resource contract")
    if len(set(selected_paths)) != len(selected_paths):
        raise IACKDAcquisitionRefusal("selected-object paths are not unique")
    if sum(int(row.get("size_bytes", -1)) for row in selected) != int(caps["payload_bytes"]):
        raise IACKDAcquisitionRefusal("selected-object bytes differ from resource contract")
    for path in selected_paths:
        _safe_relative_path(path)
    if int(caps["payload_bytes"]) + int(caps["private_receipt_bytes"]) > int(
        caps["peak_incremental_disk_bytes"]
    ):
        raise IACKDAcquisitionRefusal("registered payload and receipts exceed disk cap")
    for path in (payload_root, temporary_root, receipt_root):
        if path.exists() or path.is_symlink():
            raise IACKDAcquisitionRefusal(f"exclusive acquisition path already exists: {path}")
    required_free = (
        int(caps["minimum_free_disk_bytes"])
        if minimum_free_disk_bytes is None
        else int(minimum_free_disk_bytes)
    )
    if shutil.disk_usage(root).free < required_free:
        raise IACKDAcquisitionRefusal("free disk is below the registered minimum")
    started = time.monotonic()
    starting_rss = rss_reader()
    free_disk_before = shutil.disk_usage(root).free
    receipt_root.mkdir(parents=True, exist_ok=False)
    consumed_path = receipt_root / "acquisition_consumed.v0.json"
    _write_json_exclusive(
        consumed_path,
        {
            "schema_name": "neurodecodekit.iackd_acquisition_consumed",
            "schema_version": SCHEMA_VERSION,
            "started_at_utc": _utc_now(),
            "retry_allowed": False,
            "rerun_allowed": False,
        },
        64 * 1024,
    )
    temporary_bundle = temporary_root / "bundle"
    temporary_bundle.mkdir(parents=True, exist_ok=False)
    try:
        metadata, metadata_bytes = fetch_registered_metadata(contract, inventory, opener)
        if time.monotonic() - started > float(caps["wall_time_seconds"]):
            raise IACKDAcquisitionFailure("resource", "metadata wall cap exceeded")
        if rss_reader() > int(caps["peak_rss_bytes"]):
            raise IACKDAcquisitionFailure("resource", "metadata RSS cap exceeded")
        rows = []
        payload_bytes = 0
        base_url = contract["acquisition_contract"]["object_base_url"].rstrip("/")
        for row in selected:
            relative = _safe_relative_path(str(row["path"]))
            destination = temporary_bundle / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            expected_size = int(row["size_bytes"])
            quoted = urllib.parse.quote(str(row["path"]), safe="/._-")
            requested_url = f"{base_url}/{quoted}"
            with _managed_stream(opener(requested_url, expected_size)) as stream:
                _validate_payload_response(stream, requested_url, row)
                try:
                    handle = destination.open("xb")
                except FileExistsError:
                    raise IACKDAcquisitionFailure("payload", "duplicate payload path") from None
                digest = hashlib.sha256()
                network_count = 0
                with handle:
                    while True:
                        chunk = stream.read(min(CHUNK_BYTES, expected_size - network_count + 1))
                        if not chunk:
                            break
                        network_count += len(chunk)
                        if network_count > expected_size:
                            raise IACKDAcquisitionFailure("payload", "payload exceeds expected size")
                        digest.update(chunk)
                        handle.write(chunk)
            if network_count != expected_size:
                raise IACKDAcquisitionFailure("payload", "payload ended before expected size")
            payload_bytes += network_count
            rows.append(
                {
                    "path": row["path"],
                    "role": row["role"],
                    "size_bytes": network_count,
                    "registered_etag": row["etag"],
                    "registered_last_modified": row["last_modified"],
                    "observed_local_sha256": digest.hexdigest(),
                    "stream_hash_passes": 1,
                    "post_write_content_opens": 0,
                }
            )
            if time.monotonic() - started > float(caps["wall_time_seconds"]):
                raise IACKDAcquisitionFailure("resource", "acquisition wall cap exceeded")
            if rss_reader() > int(caps["peak_rss_bytes"]):
                raise IACKDAcquisitionFailure("resource", "acquisition RSS cap exceeded")
        if len(rows) != int(caps["payload_requests"]):
            raise IACKDAcquisitionFailure("inventory", "payload request count mismatch")
        if payload_bytes != int(caps["payload_bytes"]):
            raise IACKDAcquisitionFailure("inventory", "payload byte total mismatch")
        payload_root.parent.mkdir(parents=True, exist_ok=True)
        os.replace(temporary_bundle, payload_root)
        temporary_root.rmdir()
        runtime = time.monotonic() - started
        manifest = {
            "schema_name": "neurodecodekit.iackd_acquisition_manifest",
            "schema_version": SCHEMA_VERSION,
            "status": "passed",
            "contract_sha256": CONTRACT_SHA256 if enforce_registered_roots else None,
            "canonical_inventory_sha256": metadata["canonical_identity_sha256"],
            "file_records": rows,
            "measurements": {
                **metadata,
                "payload_requests": len(rows),
                "payload_bytes": payload_bytes,
                "stream_hash_passes": len(rows),
                "post_write_content_opens": 0,
                "payload_content_parses": 0,
                "runtime_seconds": round(runtime, 6),
                "peak_rss_bytes": rss_reader(),
                "starting_peak_rss_bytes": starting_rss,
                "free_disk_bytes_before": free_disk_before,
                "free_disk_bytes_after_payload_promotion": shutil.disk_usage(root).free,
                "retained_output_bytes": 0,
                "peak_incremental_disk_upper_bound_bytes": 0,
                "cpu_threads": 1,
                "workers": 1,
                "concurrent_numerical_jobs": 1,
                "retries": 0,
                "reruns": 0,
            },
            "warnings": [
                "payload_headers_markers_signals_trajectories_and_targets_unread",
                "acquisition_receipt_is_not_scientific_evidence",
            ],
            "created_at_utc": _utc_now(),
        }
        receipt_cap = int(caps["private_receipt_bytes"])
        manifest_path = receipt_root / "acquisition_manifest.v0.json"
        receipt_path = receipt_root / "ACQUISITION_RECEIPT.md"
        for _ in range(8):
            manifest_payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
            receipt_payload = _human_receipt(manifest)
            retained = (
                payload_bytes
                + consumed_path.stat().st_size
                + len(manifest_payload)
                + len(receipt_payload)
            )
            measurements = manifest["measurements"]
            if (
                measurements["retained_output_bytes"] == retained
                and measurements["peak_incremental_disk_upper_bound_bytes"] == retained
            ):
                break
            measurements["retained_output_bytes"] = retained
            measurements["peak_incremental_disk_upper_bound_bytes"] = retained
        else:
            raise IACKDAcquisitionFailure("output", "disk byte measurement did not converge")
        if retained > int(caps["peak_incremental_disk_bytes"]):
            raise IACKDAcquisitionFailure("resource", "incremental disk cap exceeded")
        manifest_bytes = _write_json_exclusive(manifest_path, manifest, receipt_cap)
        if consumed_path.stat().st_size + manifest_bytes + len(receipt_payload) > receipt_cap:
            raise IACKDAcquisitionFailure("output", "combined receipts exceed cap")
        with receipt_path.open("xb") as handle:
            handle.write(receipt_payload)
        observed_retained = _tree_bytes_regular(payload_root) + _tree_bytes_regular(receipt_root)
        if observed_retained != retained:
            raise IACKDAcquisitionFailure("output", "retained byte measurement differs")
        if time.monotonic() - started > float(caps["wall_time_seconds"]):
            raise IACKDAcquisitionFailure("resource", "acquisition wall cap exceeded")
        if rss_reader() > int(caps["peak_rss_bytes"]):
            raise IACKDAcquisitionFailure("resource", "acquisition RSS cap exceeded")
        return AcquisitionOutcome("passed", manifest, manifest_path, receipt_path)
    except Exception:
        if temporary_root.exists() and not temporary_root.is_symlink():
            shutil.rmtree(temporary_root)
        raise


def execute_registered_acquisition(
    repo_root: str | Path,
    *,
    evidence: ImplementationEvidence,
    environ: Mapping[str, str],
) -> AcquisitionOutcome:
    """Consume the one registered acquisition after green implementation."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    inventory = load_registered_inventory(root)
    _validate_implementation_registry(root, evidence)
    return run_acquisition(
        workspace_root=root,
        contract=contract,
        inventory=inventory,
        opener=_open_url_once,
        environ=environ,
        enforce_registered_roots=True,
    )


class FixtureResponse(io.BytesIO):
    """Small response object with urllib-like identity headers for tests."""

    def __init__(self, payload: bytes, url: str, etag: str | None = None) -> None:
        super().__init__(payload)
        self._url = url
        self.headers = {"Content-Length": str(len(payload))}
        if etag is not None:
            self.headers["ETag"] = f'"{etag}"'

    def geturl(self) -> str:
        return self._url


def bytes_opener(
    payloads: Mapping[str, bytes],
    etags: Mapping[str, str] | None = None,
) -> URLopener:
    """Return a no-network one-open-per-call transport for generated fixtures."""

    calls: list[str] = []

    def open_payload(url: str, maximum_bytes: int) -> BinaryIO:
        if url not in payloads:
            raise IACKDAcquisitionFailure("fixture", f"unexpected fixture URL: {url}")
        if url in calls:
            raise IACKDAcquisitionFailure("fixture", f"fixture URL reopened: {url}")
        calls.append(url)
        payload = payloads[url]
        if len(payload) > maximum_bytes:
            raise IACKDAcquisitionFailure("fixture", "fixture payload exceeds requested cap")
        return FixtureResponse(payload, url, None if etags is None else etags.get(url))

    open_payload.calls = calls  # type: ignore[attr-defined]
    return open_payload


def synthetic_listing_pages(
    rows: Sequence[Mapping[str, Any]],
    *,
    split_at: int,
    token: str = "fixture-token",
) -> tuple[bytes, bytes]:
    """Create deterministic two-page ListObjectsV2 fixtures."""

    def page(items: Sequence[Mapping[str, Any]], truncated: bool) -> bytes:
        contents = "".join(
            "<Contents>"
            f"<Key>ds006840/{row['path']}</Key>"
            f"<LastModified>{row['last_modified']}</LastModified>"
            f"<ETag>&quot;{row['etag']}&quot;</ETag>"
            f"<Size>{row['size_bytes']}</Size>"
            "</Contents>"
            for row in items
        )
        continuation = f"<NextContinuationToken>{token}</NextContinuationToken>" if truncated else ""
        return (
            '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
            f"<IsTruncated>{str(truncated).lower()}</IsTruncated>"
            f"{continuation}{contents}</ListBucketResult>"
        ).encode("utf-8")

    return page(rows[:split_at], True), page(rows[split_at:], False)
