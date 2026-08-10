"""Bounded, opaque acquisition for the registered PhysioNet motor EEG slice.

The executor deliberately has no EDF parser. It verifies public metadata,
streams nine registered bytestrings, hashes each local file once, and promotes
only the complete verified bundle.
"""

from __future__ import annotations

import hashlib
import html.parser
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Sequence


CONTRACT_RELATIVE_PATH = Path("registries/physionet_motor_acquisition_contract.v0.json")
DECISION_RELATIVE_PATH = Path(
    "registries/physionet_motor_acquisition_authorization_decision.v0.json"
)
CONTRACT_SHA256 = "6c81dac6a818f13c49f5df25c540e9d3ef65f21b56ecb1a5b5d15d4a3dc819d3"
DECISION_SHA256 = "5f232f174c67fae2f70f2cc26a779a82caee9176dc406ceccb182ad77d1bc304"
AUTHORIZATION_COMMIT = "00b91edd213112fd186711d06369ae4f836b2243"
AUTHORIZATION_CI_RUN_ID = 31344104565
AUTHORIZATION_BASE_JOB_ID = 93322699209
AUTHORIZATION_OPTIONAL_JOB_ID = 93322699259
EXPECTED_DATASET_ID = "eegmmidb"
EXPECTED_VERSION = "1.0.0"
EXPECTED_DOI = "10.13026/C28G6P"
EXPECTED_LICENSE_ID = "ODC-By-1.0"
EXPECTED_LICENSE_LABEL = "Open Data Commons Attribution License v1.0"
EXPECTED_PAYLOAD_BYTES = 23_248_224
EXPECTED_SUBJECTS = ("S001", "S002", "S003")
EXPECTED_RUNS = ("03", "07", "11")
EXPECTED_PATHS = tuple(
    f"{subject}/{subject}R{run}.edf"
    for subject in EXPECTED_SUBJECTS
    for run in EXPECTED_RUNS
)
CHUNK_BYTES = 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
REQUIRED_UNAVAILABLE_FIELDS = (
    "device_model",
    "observed_channel_count",
    "observed_channel_names",
    "observed_units",
    "observed_sampling_rate_hz",
    "observed_montage",
    "observed_reference",
    "observed_sensor_geometry",
    "observed_annotations",
    "observed_event_count",
    "observed_trial_count",
    "observed_target_balance",
    "observed_signal_quality",
    "usable_epoch_count",
    "model_accuracy",
    "no_signal_comparison",
    "neural_advantage",
    "cross_person_generalization",
    "end_to_end_latency",
)


class AcquisitionRefusal(RuntimeError):
    """Preflight failed before the one registered invocation began."""


class AcquisitionFailure(RuntimeError):
    """The registered invocation was consumed and must be parked."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


@dataclass(frozen=True)
class ExecutionEvidence:
    """Remote-green implementation evidence supplied at execution time."""

    implementation_commit: str
    implementation_ci_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


@dataclass(frozen=True)
class MetadataEvidence:
    """Target-free evidence from the three source surfaces and nine HEADs."""

    dataset_version: str
    doi: str
    license_label: str
    public_available: bool
    task_mapping_confirmed: bool
    source_surfaces: tuple[str, ...]
    file_records: tuple[Mapping[str, Any], ...]
    request_count: int
    network_bytes: int


@dataclass(frozen=True)
class AcquisitionOutcome:
    """One pass-or-park result and its private receipt paths."""

    status: str
    manifest: dict[str, Any]
    manifest_path: Path
    receipt_path: Path

    @property
    def passed(self) -> bool:
        return self.status == "passed"


MetadataFetcher = Callable[
    [Mapping[str, Any], Sequence[Mapping[str, Any]], int], MetadataEvidence
]
PayloadOpener = Callable[[str, int], BinaryIO]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    payload = path.read_bytes()
    observed = _sha256_bytes(payload)
    if observed != expected_sha256:
        raise AcquisitionRefusal(
            f"locked file hash mismatch for {path}: expected {expected_sha256}, got {observed}"
        )
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise AcquisitionRefusal(f"locked JSON must contain an object: {path}")
    return value


def registered_plan(repo_root: str | Path) -> dict[str, Any]:
    """Return the frozen plan without path stats or network access."""

    root = Path(repo_root)
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    if decision["authorized_contract"]["sha256"] != CONTRACT_SHA256:
        raise AcquisitionRefusal("authorization decision does not bind the frozen contract")
    storage = contract["storage_and_output"]
    caps = contract["resource_caps"]
    return {
        "mode": "dry_run_no_registered_path_stat_no_network",
        "provider": contract["source_dataset"]["provider"],
        "dataset_id": contract["source_dataset"]["dataset_id"],
        "version": contract["source_dataset"]["version"],
        "doi": contract["source_dataset"]["doi"],
        "license_id": contract["source_dataset"]["license_id"],
        "subjects": contract["prospective_cohort"]["subjects"],
        "runs": contract["prospective_cohort"]["runs"],
        "file_count": len(contract["selected_files"]),
        "file_paths": [row["repository_relative_path"] for row in contract["selected_files"]],
        "expected_payload_bytes": storage["expected_final_payload_bytes"],
        "payload_root": storage["payload_root"],
        "temporary_root": storage["temporary_root"],
        "receipt_root": storage["receipt_root"],
        "caps": {
            "cpu_threads": caps["cpu_threads"],
            "workers": caps["workers"],
            "concurrent_numerical_jobs": caps["concurrent_numerical_jobs"],
            "wall_time_seconds": caps["wall_time_seconds"],
            "peak_rss_bytes": caps["peak_rss_bytes"],
            "metadata_network_bytes": storage["maximum_metadata_network_bytes"],
            "edf_payload_network_bytes": storage["maximum_edf_payload_network_bytes"],
            "incremental_disk_bytes": storage["maximum_incremental_disk_bytes_including_temporary_files"],
            "minimum_free_disk_bytes": storage["minimum_free_disk_bytes_before_execution"],
            "receipt_bytes": storage["maximum_generated_receipt_bytes_combined"],
        },
        "warnings": [
            "dry_run_only_no_registered_path_stat_or_network_access",
            "execute_consumes_the_single_registered_invocation_even_if_it_parks",
            "edf_payloads_remain_opaque_and_event_sidecars_are_forbidden",
            "acquisition_does_not_establish_an_eeg_or_decoding_result",
        ],
    }


def _verify_execution_evidence(repo_root: Path, evidence: ExecutionEvidence) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", evidence.implementation_commit):
        raise AcquisitionRefusal("implementation commit must be a full lowercase Git SHA")
    if evidence.implementation_commit == AUTHORIZATION_COMMIT:
        raise AcquisitionRefusal("implementation commit must follow the authorization commit")
    if min(
        evidence.implementation_ci_run_id,
        evidence.base_python_job_id,
        evidence.optional_neuro_job_id,
    ) <= 0:
        raise AcquisitionRefusal("implementation CI run and both required job IDs must be positive")

    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ("git", *args),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )

    head = git("rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.implementation_commit:
        raise AcquisitionRefusal("current HEAD does not match the supplied implementation commit")
    tracked = git("status", "--porcelain", "--untracked-files=no")
    if tracked.returncode or tracked.stdout.strip():
        raise AcquisitionRefusal("tracked worktree changes are forbidden during registered execution")
    ancestor = git("merge-base", "--is-ancestor", AUTHORIZATION_COMMIT, "HEAD")
    if ancestor.returncode:
        raise AcquisitionRefusal("authorization commit is not an ancestor of the implementation")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _peak_rss_bytes() -> int:
    import resource

    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise AcquisitionRefusal(f"unsafe registered relative path: {value!r}")
    return path


def _workspace_path(workspace_root: Path, value: str) -> Path:
    return workspace_root / _safe_relative_path(value)


def _lstat_optional(path: Path) -> os.stat_result | None:
    try:
        return os.lstat(path)
    except FileNotFoundError:
        return None


def _assert_existing_components_not_symlinks(workspace_root: Path, path: Path) -> None:
    relative = path.relative_to(workspace_root)
    current = workspace_root
    for part in relative.parts:
        current = current / part
        stat_result = _lstat_optional(current)
        if stat_result is None:
            return
        if os.path.islink(current):
            raise AcquisitionRefusal(f"registered path component is a symlink: {current}")


def _mkdir_tracked(path: Path, *, workspace_root: Path, created_dirs: list[Path]) -> None:
    relative = path.relative_to(workspace_root)
    current = workspace_root
    for part in relative.parts:
        current = current / part
        stat_result = _lstat_optional(current)
        if stat_result is None:
            os.mkdir(current)
            created_dirs.append(current)
            continue
        if os.path.islink(current) or not os.path.isdir(current):
            raise AcquisitionFailure("filesystem", f"unsafe directory component: {current}")


def _cleanup_created_temp(created_files: Sequence[Path], created_dirs: Sequence[Path]) -> None:
    for path in reversed(created_files):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    for path in reversed(created_dirs):
        try:
            path.rmdir()
        except (FileNotFoundError, OSError):
            pass


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    wrong = {key: environ.get(key) for key in THREAD_ENV_KEYS if environ.get(key) != "1"}
    if wrong:
        details = ", ".join(f"{key}={value!r}" for key, value in wrong.items())
        raise AcquisitionRefusal(f"one-thread environment required; set each to '1': {details}")


def _validate_contract_shape(contract: Mapping[str, Any]) -> None:
    source = contract["source_dataset"]
    if source["provider"] != "PhysioNet" or source["dataset_id"] != EXPECTED_DATASET_ID:
        raise AcquisitionRefusal("source identity is not the frozen PhysioNet dataset")
    if source["version"] != EXPECTED_VERSION or source["doi"] != EXPECTED_DOI:
        raise AcquisitionRefusal("dataset version or DOI drifted from the frozen identity")
    if source["license_id"] != EXPECTED_LICENSE_ID:
        raise AcquisitionRefusal("license identity drifted from the frozen contract")
    selected = contract["selected_files"]
    paths = tuple(row["repository_relative_path"] for row in selected)
    if paths != EXPECTED_PATHS or len(selected) != 9:
        raise AcquisitionRefusal("contract must bind the exact nine ordered EDF paths")
    if len(set(paths)) != 9:
        raise AcquisitionRefusal("registered EDF paths must be unique")
    for row in selected:
        path = row["repository_relative_path"]
        if Path(path).suffix.casefold() != ".edf" or ".event" in path.casefold():
            raise AcquisitionRefusal("only the nine registered EDF paths are allowed")
        if row["destination_relative_path"] != path:
            raise AcquisitionRefusal("destination path must exactly preserve repository identity")
        expected_url = urllib.parse.urljoin(source["file_root_url"], path)
        if row["download_url"] != expected_url:
            raise AcquisitionRefusal("registered EDF URL drifted")
        if row.get("content_parse_allowed") is not False:
            raise AcquisitionRefusal("EDF content parsing must remain forbidden")


class _VisibleTextParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _document_text(payload: bytes) -> str:
    try:
        decoded = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AcquisitionFailure("metadata", "metadata document is not strict UTF-8") from exc
    parser = _VisibleTextParser()
    parser.feed(decoded)
    parser.close()
    text = " ".join(parser.parts) if parser.parts else decoded
    return re.sub(r"\s+", " ", text).strip()


def _validate_dataset_document(text: str, source: Mapping[str, Any]) -> None:
    folded = text.casefold()
    required = (
        source["dataset_name"].casefold(),
        source["version"].casefold(),
        source["doi"].casefold(),
        source["license_label"].casefold(),
    )
    if any(value not in folded for value in required):
        raise AcquisitionFailure("metadata", "dataset page identity or license metadata mismatch")


def _validate_task_mapping_document(text: str) -> None:
    folded = re.sub(r"\s+", " ", text.casefold())
    run_sequence = re.search(r"\b3\s*,\s*7\s*,\s*11\b", folded)
    execution = "motor execution" in folded or "real, left vs right hand" in folded
    left_right = re.search(r"left\s+(?:vs\.?|versus)\s+right\s+hand", folded)
    if run_sequence is None or not execution or left_right is None:
        raise AcquisitionFailure("metadata", "MNE run mapping no longer confirms 3/7/11 execution")


def _parse_checksum_manifest(payload: bytes) -> dict[str, str]:
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise AcquisitionFailure("metadata", "checksum manifest is not ASCII") from exc
    checksums: dict[str, str] = {}
    pattern = re.compile(r"^([0-9a-fA-F]{64})[ \t]+[*]?(.+?)\s*$")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = pattern.fullmatch(line)
        if match is None:
            raise AcquisitionFailure("metadata", "checksum manifest contains a malformed line")
        path = match.group(2).removeprefix("./")
        if path in checksums:
            raise AcquisitionFailure("metadata", f"duplicate checksum path: {path}")
        checksums[path] = match.group(1).lower()
    return checksums


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, stage: str) -> None:
        self.stage = stage

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: BinaryIO,
        code: int,
        msg: str,
        headers: Mapping[str, str],
        newurl: str,
    ) -> None:
        del req, fp, code, msg, headers, newurl
        raise AcquisitionFailure(self.stage, "HTTP redirect refused; no unregistered host contacted")


def _open_request_once(request: urllib.request.Request, *, stage: str) -> BinaryIO:
    opener = urllib.request.build_opener(_RejectRedirect(stage))
    try:
        return opener.open(request, timeout=30)
    except AcquisitionFailure:
        raise
    except urllib.error.HTTPError as exc:
        raise AcquisitionFailure(stage, f"HTTP request failed with status {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AcquisitionFailure(stage, f"HTTP request failed: {exc.reason}") from exc


def _response_status(response: BinaryIO) -> int:
    status = getattr(response, "status", None)
    if status is None:
        status = response.getcode()
    return int(status)


def _assert_exact_response_url(response: BinaryIO, expected_url: str, *, stage: str) -> None:
    observed = response.geturl()
    if observed != expected_url:
        raise AcquisitionFailure(stage, "response URL differs from the registered source URL")


def _read_metadata_body(response: BinaryIO, remaining_bytes: int) -> bytes:
    if remaining_bytes <= 0:
        raise AcquisitionFailure("resource", "metadata network byte cap exhausted")
    content_length = response.headers.get("Content-Length")
    if content_length is not None:
        try:
            declared = int(content_length)
        except ValueError as exc:
            raise AcquisitionFailure("metadata", "invalid metadata Content-Length") from exc
        if declared > remaining_bytes:
            raise AcquisitionFailure("resource", "metadata response exceeds remaining byte cap")
    payload = response.read(remaining_bytes + 1)
    if len(payload) > remaining_bytes:
        raise AcquisitionFailure("resource", "metadata network byte cap exceeded")
    return payload


def _fetch_metadata_document(url: str, remaining_bytes: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"Accept-Encoding": "identity", "User-Agent": "NeuroDecodeKit/0.1"},
        method="GET",
    )
    with _managed_binary_stream(_open_request_once(request, stage="metadata")) as response:
        if _response_status(response) != 200:
            raise AcquisitionFailure("metadata", "metadata request did not return HTTP 200")
        _assert_exact_response_url(response, url, stage="metadata")
        encoding = response.headers.get("Content-Encoding")
        if encoding not in (None, "identity"):
            raise AcquisitionFailure("metadata", "compressed metadata responses are forbidden")
        return _read_metadata_body(response, remaining_bytes)


def _fetch_edf_head(url: str, expected_size: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept-Encoding": "identity", "User-Agent": "NeuroDecodeKit/0.1"},
        method="HEAD",
    )
    with _managed_binary_stream(_open_request_once(request, stage="metadata")) as response:
        if _response_status(response) != 200:
            raise AcquisitionFailure("metadata", "EDF HEAD did not return HTTP 200")
        _assert_exact_response_url(response, url, stage="metadata")
        content_length = response.headers.get("Content-Length")
        try:
            observed_size = int(content_length) if content_length is not None else -1
        except ValueError as exc:
            raise AcquisitionFailure("metadata", "invalid EDF HEAD Content-Length") from exc
        if observed_size != expected_size:
            raise AcquisitionFailure("metadata", "EDF HEAD size differs from frozen size")
        return {
            "size_bytes": observed_size,
            "content_type": response.headers.get("Content-Type"),
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
        }


def _fetch_registered_metadata(
    source: Mapping[str, Any],
    selected_files: Sequence[Mapping[str, Any]],
    maximum_network_bytes: int,
) -> MetadataEvidence:
    dataset_payload = _fetch_metadata_document(source["dataset_url"], maximum_network_bytes)
    consumed = len(dataset_payload)
    checksum_payload = _fetch_metadata_document(
        source["official_checksum_manifest_url"], maximum_network_bytes - consumed
    )
    consumed += len(checksum_payload)
    mapping_payload = _fetch_metadata_document(
        source["task_mapping_source_url"], maximum_network_bytes - consumed
    )
    consumed += len(mapping_payload)

    _validate_dataset_document(_document_text(dataset_payload), source)
    _validate_task_mapping_document(_document_text(mapping_payload))
    checksums = _parse_checksum_manifest(checksum_payload)
    file_records: list[dict[str, Any]] = []
    for frozen in selected_files:
        path = frozen["repository_relative_path"]
        if checksums.get(path) != frozen["official_sha256"]:
            raise AcquisitionFailure("metadata", f"official SHA-256 mismatch for {path}")
        head = _fetch_edf_head(frozen["download_url"], int(frozen["size_bytes"]))
        file_records.append(
            {
                "path": path,
                "size_bytes": head["size_bytes"],
                "official_sha256": checksums[path],
                "content_type": head["content_type"],
                "etag": head["etag"],
                "last_modified": head["last_modified"],
            }
        )
    return MetadataEvidence(
        dataset_version=source["version"],
        doi=source["doi"],
        license_label=source["license_label"],
        public_available=True,
        task_mapping_confirmed=True,
        source_surfaces=(
            source["dataset_url"],
            source["official_checksum_manifest_url"],
            source["task_mapping_source_url"],
        ),
        file_records=tuple(file_records),
        request_count=3 + len(selected_files),
        network_bytes=consumed,
    )


def _validate_metadata_evidence(
    evidence: MetadataEvidence,
    source: Mapping[str, Any],
    selected_files: Sequence[Mapping[str, Any]],
    cap_bytes: int,
) -> None:
    if (
        evidence.dataset_version != source["version"]
        or evidence.doi != source["doi"]
        or evidence.license_label != source["license_label"]
        or evidence.public_available is not True
        or evidence.task_mapping_confirmed is not True
    ):
        raise AcquisitionFailure("metadata", "source identity, availability, or task mapping drifted")
    expected_surfaces = (
        source["dataset_url"],
        source["official_checksum_manifest_url"],
        source["task_mapping_source_url"],
    )
    if evidence.source_surfaces != expected_surfaces:
        raise AcquisitionFailure("metadata", "metadata source surfaces differ from registration")
    if evidence.request_count != 3 + len(selected_files):
        raise AcquisitionFailure("metadata", "metadata request count differs from the frozen pass")
    if evidence.network_bytes < 0 or evidence.network_bytes > cap_bytes:
        raise AcquisitionFailure("resource", "metadata network byte cap exceeded")
    expected = {row["repository_relative_path"]: row for row in selected_files}
    observed: dict[str, Mapping[str, Any]] = {}
    for row in evidence.file_records:
        path = row.get("path")
        if not isinstance(path, str) or path in observed:
            raise AcquisitionFailure("metadata", "metadata returned an invalid or duplicate path")
        observed[path] = row
    if set(observed) != set(expected):
        raise AcquisitionFailure("metadata", "metadata membership differs from nine frozen paths")
    for path, frozen in expected.items():
        row = observed[path]
        if row.get("size_bytes") != frozen["size_bytes"]:
            raise AcquisitionFailure("metadata", f"metadata size mismatch for {path}")
        if row.get("official_sha256") != frozen["official_sha256"]:
            raise AcquisitionFailure("metadata", f"metadata SHA-256 mismatch for {path}")


def _open_payload(url: str, expected_size: int) -> BinaryIO:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "physionet.org":
        raise AcquisitionFailure("transfer", "payload URL host is not the registered PhysioNet host")
    if Path(parsed.path).suffix.casefold() != ".edf" or ".event" in parsed.path.casefold():
        raise AcquisitionFailure("transfer", "only registered EDF payload URLs are permitted")
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/octet-stream",
            "Accept-Encoding": "identity",
            "User-Agent": "NeuroDecodeKit/0.1",
        },
        method="GET",
    )
    response = _open_request_once(request, stage="transfer")
    if _response_status(response) != 200:
        response.close()
        raise AcquisitionFailure("transfer", "payload request did not return HTTP 200")
    try:
        _assert_exact_response_url(response, url, stage="transfer")
    except AcquisitionFailure:
        response.close()
        raise
    encoding = response.headers.get("Content-Encoding")
    if encoding not in (None, "identity"):
        response.close()
        raise AcquisitionFailure("transfer", "compressed payload responses are forbidden")
    content_length = response.headers.get("Content-Length")
    try:
        observed = int(content_length) if content_length is not None else -1
    except ValueError as exc:
        response.close()
        raise AcquisitionFailure("transfer", "invalid payload Content-Length") from exc
    if observed != expected_size:
        response.close()
        raise AcquisitionFailure("transfer", "payload Content-Length differs from frozen size")
    return response


@contextmanager
def _managed_binary_stream(stream: BinaryIO) -> Iterator[BinaryIO]:
    try:
        yield stream
    finally:
        stream.close()


def _assert_live_caps(
    *,
    start_monotonic: float,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    wall_cap: float,
    rss_cap: int,
) -> tuple[float, int]:
    runtime = clock() - start_monotonic
    rss = rss_reader()
    if runtime > wall_cap:
        raise AcquisitionFailure("resource", "wall-time cap exceeded")
    if rss > rss_cap:
        raise AcquisitionFailure("resource", "peak RSS cap exceeded")
    return runtime, rss


def _open_exclusive_binary(path: Path) -> BinaryIO:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    return os.fdopen(descriptor, "wb", buffering=0)


def _opaque_hash_file(path: Path) -> tuple[int, str]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    digest = hashlib.sha256()
    observed_size = 0
    with os.fdopen(descriptor, "rb", buffering=0) as stream:
        while True:
            chunk = stream.read(CHUNK_BYTES)
            if not chunk:
                break
            observed_size += len(chunk)
            digest.update(chunk)
    return observed_size, digest.hexdigest()


def _enumerate_regular_files(root: Path) -> list[Path]:
    files: list[Path] = []
    stack = [root]
    while stack:
        current = stack.pop()
        with os.scandir(current) as entries:
            for entry in entries:
                if entry.is_symlink():
                    raise AcquisitionFailure("integrity", "symlink appeared in staging bundle")
                if entry.is_dir(follow_symlinks=False):
                    stack.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    files.append(Path(entry.path))
                else:
                    raise AcquisitionFailure("integrity", "non-regular staging entry appeared")
    return sorted(files)


def _base_access_counters() -> dict[str, int]:
    return {
        "acquisition_invocation_count": 1,
        "metadata_request_count": 0,
        "metadata_network_bytes": 0,
        "edf_payload_download_invocations": 0,
        "edf_payload_request_count": 0,
        "edf_payload_network_bytes": 0,
        "opaque_local_hash_pass_count": 0,
        "local_edf_payload_opens_for_opaque_hash": 0,
        "edf_header_reads": 0,
        "edf_annotation_or_event_reads": 0,
        "event_sidecar_requests_or_reads": 0,
        "signal_sample_reads": 0,
        "task_target_label_epoch_trial_reads": 0,
        "channel_montage_reference_geometry_sampling_quality_reads": 0,
        "epoch_window_feature_cache_operations": 0,
        "split_operations": 0,
        "model_or_checkpoint_accesses": 0,
        "model_inference_runs": 0,
        "training_or_parameter_update_runs": 0,
        "scoring_or_selection_runs": 0,
        "other_real_dataset_operations": 0,
        "additional_file_participant_run_or_substitution_requests": 0,
        "payload_retries": 0,
        "language_model_or_provider_operations": 0,
        "rw3_stream_device_or_hardware_operations": 0,
        "upload_publication_or_release_operations": 0,
        "work_order_9_operations": 0,
        "reruns": 0,
    }


def _warnings(status: str, failure_stage: str | None) -> list[str]:
    values = [
        "odc_by_1_0_attribution_boundary",
        "edf_bytes_hashed_opaquely_without_header_annotation_signal_or_event_parsing",
        "event_sidecars_were_not_requested_or_read",
        "prospective_fit_and_check_roles_did_not_create_a_split",
        "single_registered_invocation_consumed_no_retry_or_rerun_authorized",
        "metadata_network_bytes_count_response_bodies_not_transport_headers",
        "bundle_identity_does_not_establish_edf_readability_signal_quality_or_motor_physiology",
        "no_scientific_decoding_neural_realtime_portable_home_assistive_or_clinical_claim_upgrade",
    ]
    if status == "parked":
        values.append(f"registered_invocation_parked_at_{failure_stage or 'unknown'}")
    return values


def _unavailable_fields() -> dict[str, str]:
    reason = "unavailable because work order 8 forbids EDF interpretation and downstream analysis"
    return {field: reason for field in REQUIRED_UNAVAILABLE_FIELDS}


def _claim_boundary(status: str) -> dict[str, str]:
    if status == "passed":
        engineering = (
            "The exact nine-file public EEGMMIDB v1.0.0 bundle was acquired once and matched "
            "its frozen paths, sizes, and official SHA-256 identities within the registered limits."
        )
    else:
        engineering = (
            "The one registered acquisition was consumed and parked; no complete qualifying "
            "PhysioNet bundle is claimed."
        )
    return {
        "engineering_result": engineering,
        "scientific_claim_not_established": (
            "This acquisition establishes no EDF readability, event correctness, signal quality, "
            "motor effect, neural advantage, model accuracy, unseen-person generalization, "
            "end-to-end latency, typing or language decoding, portable hardware, home use, "
            "assistive value, or clinical utility."
        ),
    }


def _gate_results(
    *,
    status: str,
    metadata_matched: bool,
    transfer_complete: bool,
    integrity_matched: bool,
    bundle_promoted: bool,
    resource_caps_passed: bool,
    forbidden_counters_zero: bool,
) -> dict[str, bool]:
    passed = status == "passed"
    return {
        "registration_authorization_and_implementation_remote_green": True,
        "version_doi_public_availability_and_license_exact": metadata_matched,
        "nine_metadata_paths_and_sizes_exact": metadata_matched,
        "nine_official_sha256_entries_exact": metadata_matched,
        "output_roots_absent_isolated_and_non_symlinked": True,
        "complete_nine_file_23248224_byte_bundle": transfer_complete and bundle_promoted,
        "one_opaque_size_and_sha256_pass_per_edf": integrity_matched,
        "metadata_payload_runtime_rss_disk_thread_worker_and_receipt_caps": resource_caps_passed
        and passed,
        "all_forbidden_access_and_operation_counters_zero": forbidden_counters_zero,
        "no_preexisting_path_followed_overwritten_deleted_or_renamed": True,
        "warnings_and_unavailable_fields_explicit_in_both_receipts": True,
        "acquisition_only_claim_ceiling_and_stop_before_work_order_9": True,
    }


def _human_receipt(manifest: Mapping[str, Any]) -> str:
    metrics = manifest["measurements"]
    lines = [
        "# PhysioNet Motor Acquisition Receipt",
        "",
        f"Status: **{manifest['status'].upper()}**",
        f"Dataset: `{manifest['source_dataset']['dataset_id']}` v`{manifest['source_dataset']['version']}`",
        f"DOI: `{manifest['source_dataset']['doi']}`",
        f"License: `{manifest['source_dataset']['license_id']}`",
        f"Files: {metrics['final_file_count']}",
        f"Final payload bytes: {metrics['final_payload_bytes']}",
        f"Metadata network bytes: {metrics['metadata_network_bytes']}",
        f"EDF payload network bytes: {metrics['edf_payload_network_bytes']}",
        f"Runtime seconds: {metrics['runtime_seconds']}",
        f"Peak RSS bytes: {metrics['peak_rss_bytes']}",
        f"Incremental disk peak bytes: {metrics['incremental_disk_peak_bytes']}",
        f"Failure stage: {manifest.get('failure_stage') or 'none'}",
        "",
        "## Files",
        "",
    ]
    lines.extend(
        (
            f"- `{row['path']}`: {row['size_bytes']} bytes, official "
            f"`{row['official_sha256']}`, observed `{row['observed_local_sha256']}`"
        )
        for row in manifest["file_paths_sizes_official_and_observed_sha256"]
    )
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- `{warning}`" for warning in manifest["warnings"])
    lines.extend(["", "## Unavailable Fields", ""])
    lines.extend(
        f"- `{field}`: {reason}" for field, reason in manifest["unavailable_fields"].items()
    )
    lines.extend(["", "## Acceptance Gates", ""])
    lines.extend(
        f"- `{gate}`: {'pass' if passed else 'fail'}"
        for gate, passed in manifest["acceptance_gate_results"].items()
    )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            manifest["claim_boundary"]["engineering_result"],
            "",
            manifest["claim_boundary"]["scientific_claim_not_established"],
            "",
        ]
    )
    return "\n".join(lines)


def _render_receipts(manifest: dict[str, Any], cap_bytes: int) -> tuple[bytes, bytes]:
    generated = int(manifest["measurements"].get("generated_receipt_bytes", 0))
    for _ in range(12):
        manifest["measurements"]["generated_receipt_bytes"] = generated
        machine = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
        human = _human_receipt(manifest).encode("utf-8")
        observed = len(machine) + len(human)
        if observed == generated:
            break
        generated = observed
    manifest["measurements"]["generated_receipt_bytes"] = generated
    machine = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    human = _human_receipt(manifest).encode("utf-8")
    if len(machine) + len(human) > cap_bytes:
        raise AcquisitionFailure("receipt", "manifest and receipt exceed the frozen output cap")
    return machine, human


def _write_receipts(
    *,
    manifest: dict[str, Any],
    receipt_root: Path,
    machine_name: str,
    human_name: str,
    cap_bytes: int,
    workspace_root: Path,
    baseline_allocated_bytes: int,
    incremental_disk_cap_bytes: int,
) -> tuple[Path, Path]:
    machine_path = receipt_root / machine_name
    human_path = receipt_root / human_name
    machine, human = _render_receipts(manifest, cap_bytes)
    projected_incremental = max(
        manifest["measurements"]["incremental_disk_peak_bytes"],
        baseline_allocated_bytes + len(machine) + len(human),
    )
    if projected_incremental > incremental_disk_cap_bytes:
        raise AcquisitionFailure("resource", "receipt would exceed incremental disk cap")
    manifest["measurements"]["incremental_disk_peak_bytes"] = projected_incremental
    machine, human = _render_receipts(manifest, cap_bytes)
    with machine_path.open("xb") as stream:
        stream.write(machine)
    with human_path.open("xb") as stream:
        stream.write(human)
    for _ in range(2):
        manifest["measurements"]["free_disk_after_bytes"] = shutil.disk_usage(workspace_root).free
        machine, human = _render_receipts(manifest, cap_bytes)
        with machine_path.open("wb") as stream:
            stream.write(machine)
        with human_path.open("wb") as stream:
            stream.write(human)
    return machine_path, human_path


def _build_manifest(
    *,
    status: str,
    contract: Mapping[str, Any],
    evidence: ExecutionEvidence,
    started_at: str,
    finished_at: str,
    runtime_seconds: float,
    peak_rss_bytes: int,
    free_disk_before_bytes: int,
    free_disk_after_bytes: int,
    incremental_disk_peak_bytes: int,
    counters: Mapping[str, int],
    file_records: Sequence[Mapping[str, Any]],
    hash_passes_by_path: Mapping[str, int],
    final_payload_bytes: int,
    final_file_count: int,
    failure_stage: str | None,
    failure_reason: str | None,
    gates: Mapping[str, bool],
) -> dict[str, Any]:
    source = contract["source_dataset"]
    return {
        "schema_name": "neurodecodekit.physionet_motor_acquisition_manifest",
        "schema_version": "0.1.0",
        "work_order": 8,
        "status": status,
        "proof_posture": "acquisition_mechanics_only_opaque_edf_no_interpretation",
        "contract_sha256": CONTRACT_SHA256,
        "authorization_decision_sha256": DECISION_SHA256,
        "authorization_commit": AUTHORIZATION_COMMIT,
        "authorization_ci_run_id": AUTHORIZATION_CI_RUN_ID,
        "authorization_base_python_job_id": AUTHORIZATION_BASE_JOB_ID,
        "authorization_optional_neuro_job_id": AUTHORIZATION_OPTIONAL_JOB_ID,
        "implementation_commit": evidence.implementation_commit,
        "implementation_ci_run_id": evidence.implementation_ci_run_id,
        "implementation_base_python_job_id": evidence.base_python_job_id,
        "implementation_optional_neuro_job_id": evidence.optional_neuro_job_id,
        "source_dataset": {
            "provider": source["provider"],
            "dataset_id": source["dataset_id"],
            "version": source["version"],
            "doi": source["doi"],
            "license_id": source["license_id"],
            "license_label": source["license_label"],
        },
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "failure_stage": failure_stage,
        "failure_reason": failure_reason,
        "measurements": {
            "input_expected_bytes": contract["storage_and_output"]["expected_final_payload_bytes"],
            "output_bytes": final_payload_bytes,
            "metadata_network_bytes": counters["metadata_network_bytes"],
            "edf_payload_network_bytes": counters["edf_payload_network_bytes"],
            "final_payload_bytes": final_payload_bytes,
            "final_file_count": final_file_count,
            "runtime_seconds": round(runtime_seconds, 6),
            "peak_rss_bytes": peak_rss_bytes,
            "free_disk_before_bytes": free_disk_before_bytes,
            "free_disk_after_bytes": free_disk_after_bytes,
            "incremental_disk_peak_bytes": incremental_disk_peak_bytes,
            "generated_receipt_bytes": 0,
            "cpu_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "end_to_end_latency_measured": False,
        },
        "file_paths_sizes_official_and_observed_sha256": list(file_records),
        "opaque_local_hash_pass_count_by_edf": dict(hash_passes_by_path),
        "access_and_operation_counters": dict(counters),
        "warnings": _warnings(status, failure_stage),
        "unavailable_fields": _unavailable_fields(),
        "acceptance_gate_results": dict(gates),
        "claim_boundary": _claim_boundary(status),
    }


def run_acquisition(
    *,
    contract: Mapping[str, Any],
    evidence: ExecutionEvidence,
    workspace_root: str | Path,
    metadata_fetcher: MetadataFetcher,
    payload_opener: PayloadOpener,
    environ: Mapping[str, str],
    clock: Callable[[], float] = time.monotonic,
    utc_now: Callable[[], str] = _utc_now,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> AcquisitionOutcome:
    """Execute one pass-or-park acquisition with injectable fixture transports."""

    _check_thread_environment(environ)
    _validate_contract_shape(contract)
    source = contract["source_dataset"]
    storage = contract["storage_and_output"]
    caps = contract["resource_caps"]
    selected_files = contract["selected_files"]
    expected_total = sum(int(row["size_bytes"]) for row in selected_files)
    if expected_total != storage["expected_final_payload_bytes"]:
        raise AcquisitionRefusal("selected file sizes do not match the registered total")

    root = Path(workspace_root)
    payload_root = _workspace_path(root, storage["payload_root"])
    temporary_root = _workspace_path(root, storage["temporary_root"])
    receipt_root = _workspace_path(root, storage["receipt_root"])
    final_container = payload_root.parent
    for path in (payload_root, final_container, temporary_root, receipt_root):
        _assert_existing_components_not_symlinks(root, path)
        if _lstat_optional(path) is not None:
            raise AcquisitionRefusal(f"registered root must not already exist: {path}")
    data_parent = final_container.parent
    data_parent_stat = _lstat_optional(data_parent)
    if data_parent_stat is None or os.path.islink(data_parent) or not os.path.isdir(data_parent):
        raise AcquisitionRefusal("registered data parent must be an existing non-symlink directory")

    free_before = shutil.disk_usage(root).free
    if free_before < storage["minimum_free_disk_bytes_before_execution"]:
        raise AcquisitionRefusal("free disk is below the frozen 2 GiB minimum")
    initial_rss = rss_reader()
    if initial_rss > caps["peak_rss_bytes"]:
        raise AcquisitionRefusal("process RSS already exceeds the frozen cap")

    started_at = utc_now()
    started = clock()
    counters = _base_access_counters()
    created_temp_files: list[Path] = []
    created_temp_dirs: list[Path] = []
    created_receipt_dirs: list[Path] = []
    file_records: list[dict[str, Any]] = []
    hash_passes_by_path = {row["repository_relative_path"]: 0 for row in selected_files}
    incremental_peak = 0
    completed_allocated = 0
    metadata_matched = False
    transfer_complete = False
    integrity_matched = False
    bundle_promoted = False
    resource_caps_passed = False
    failure_stage: str | None = None
    failure_reason: str | None = None
    peak_rss = initial_rss
    final_payload_bytes = 0
    final_file_count = 0

    _mkdir_tracked(receipt_root, workspace_root=root, created_dirs=created_receipt_dirs)
    _mkdir_tracked(temporary_root, workspace_root=root, created_dirs=created_temp_dirs)
    staging_bundle = temporary_root / payload_root.name

    try:
        if os.stat(temporary_root).st_dev != os.stat(data_parent).st_dev:
            raise AcquisitionFailure("filesystem", "temporary and final roots are not on one filesystem")
        _mkdir_tracked(staging_bundle, workspace_root=root, created_dirs=created_temp_dirs)

        metadata = metadata_fetcher(
            source,
            selected_files,
            int(storage["maximum_metadata_network_bytes"]),
        )
        counters["metadata_request_count"] = metadata.request_count
        counters["metadata_network_bytes"] = metadata.network_bytes
        _validate_metadata_evidence(
            metadata,
            source,
            selected_files,
            int(storage["maximum_metadata_network_bytes"]),
        )
        _, current_rss = _assert_live_caps(
            start_monotonic=started,
            clock=clock,
            rss_reader=rss_reader,
            wall_cap=caps["wall_time_seconds"],
            rss_cap=caps["peak_rss_bytes"],
        )
        peak_rss = max(peak_rss, current_rss)
        metadata_matched = True

        counters["edf_payload_download_invocations"] = 1
        for frozen in selected_files:
            relative = _safe_relative_path(frozen["destination_relative_path"])
            destination = staging_bundle / relative
            _mkdir_tracked(destination.parent, workspace_root=root, created_dirs=created_temp_dirs)
            expected_size = int(frozen["size_bytes"])
            observed_size = 0
            counters["edf_payload_request_count"] += 1
            stream = payload_opener(frozen["download_url"], expected_size)
            with _managed_binary_stream(stream), _open_exclusive_binary(destination) as output:
                created_temp_files.append(destination)
                while True:
                    chunk = stream.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    if not isinstance(chunk, bytes):
                        raise AcquisitionFailure("transfer", "payload stream returned non-byte data")
                    observed_size += len(chunk)
                    if observed_size > expected_size:
                        raise AcquisitionFailure("transfer", "payload exceeded its frozen file size")
                    counters["edf_payload_network_bytes"] += len(chunk)
                    if counters["edf_payload_network_bytes"] > storage[
                        "maximum_edf_payload_network_bytes"
                    ]:
                        raise AcquisitionFailure("resource", "EDF payload network cap exceeded")
                    written = output.write(chunk)
                    if written != len(chunk):
                        raise AcquisitionFailure("transfer", "short write to isolated staging file")
                    current_allocated = int(os.fstat(output.fileno()).st_blocks) * 512
                    incremental_peak = max(incremental_peak, completed_allocated + current_allocated)
                    if incremental_peak > storage[
                        "maximum_incremental_disk_bytes_including_temporary_files"
                    ]:
                        raise AcquisitionFailure("resource", "incremental disk cap exceeded")
                    _, current_rss = _assert_live_caps(
                        start_monotonic=started,
                        clock=clock,
                        rss_reader=rss_reader,
                        wall_cap=caps["wall_time_seconds"],
                        rss_cap=caps["peak_rss_bytes"],
                    )
                    peak_rss = max(peak_rss, current_rss)
            if observed_size != expected_size:
                raise AcquisitionFailure("transfer", "payload ended before its frozen file size")
            completed_allocated += int(os.lstat(destination).st_blocks) * 512

        if counters["edf_payload_network_bytes"] != expected_total:
            raise AcquisitionFailure("transfer", "batch payload byte total mismatch")
        transfer_complete = True

        for frozen in selected_files:
            path_key = frozen["repository_relative_path"]
            path = staging_bundle / _safe_relative_path(frozen["destination_relative_path"])
            if hash_passes_by_path[path_key] != 0:
                raise AcquisitionFailure("integrity", "more than one local hash pass requested")
            counters["opaque_local_hash_pass_count"] += 1
            counters["local_edf_payload_opens_for_opaque_hash"] += 1
            hash_passes_by_path[path_key] = 1
            observed_size, observed_sha256 = _opaque_hash_file(path)
            if observed_size != frozen["size_bytes"]:
                raise AcquisitionFailure("integrity", f"opaque size mismatch for {path_key}")
            if observed_sha256 != frozen["official_sha256"]:
                raise AcquisitionFailure("integrity", f"opaque SHA-256 mismatch for {path_key}")
            file_records.append(
                {
                    "path": path_key,
                    "size_bytes": observed_size,
                    "official_sha256": frozen["official_sha256"],
                    "observed_local_sha256": observed_sha256,
                    "hash_pass_count": 1,
                }
            )
            _, current_rss = _assert_live_caps(
                start_monotonic=started,
                clock=clock,
                rss_reader=rss_reader,
                wall_cap=caps["wall_time_seconds"],
                rss_cap=caps["peak_rss_bytes"],
            )
            peak_rss = max(peak_rss, current_rss)

        staged_files = _enumerate_regular_files(staging_bundle)
        registered_destinations = {
            staging_bundle / _safe_relative_path(row["destination_relative_path"])
            for row in selected_files
        }
        if set(staged_files) != registered_destinations:
            raise AcquisitionFailure("integrity", "staging bundle membership mismatch")
        final_payload_bytes = sum(os.lstat(path).st_size for path in staged_files)
        final_file_count = len(staged_files)
        if final_file_count != 9 or final_payload_bytes != expected_total:
            raise AcquisitionFailure("integrity", "staging bundle count or byte total mismatch")
        if any(value != 1 for value in hash_passes_by_path.values()):
            raise AcquisitionFailure("integrity", "each EDF must receive exactly one hash pass")
        integrity_matched = True

        _assert_live_caps(
            start_monotonic=started,
            clock=clock,
            rss_reader=rss_reader,
            wall_cap=caps["wall_time_seconds"],
            rss_cap=caps["peak_rss_bytes"],
        )
        os.mkdir(final_container)
        os.rename(staging_bundle, payload_root)
        bundle_promoted = True
        created_temp_files.clear()
        _cleanup_created_temp(created_temp_files, created_temp_dirs)
        resource_caps_passed = True
    except AcquisitionFailure as exc:
        failure_stage = exc.stage
        failure_reason = str(exc)
        _cleanup_created_temp(created_temp_files, created_temp_dirs)
    except Exception as exc:  # noqa: BLE001 - preserve a receipt for a consumed invocation
        failure_stage = "unexpected"
        failure_reason = f"{type(exc).__name__}: {exc}"
        _cleanup_created_temp(created_temp_files, created_temp_dirs)

    finished_at = utc_now()
    runtime_seconds = clock() - started
    peak_rss = max(peak_rss, rss_reader())
    if runtime_seconds > caps["wall_time_seconds"] or peak_rss > caps["peak_rss_bytes"]:
        resource_caps_passed = False
        if failure_stage is None:
            failure_stage = "resource"
            failure_reason = "final runtime or RSS cap exceeded"
    status = "passed" if bundle_promoted and failure_stage is None else "parked"
    forbidden_keys = (
        "edf_header_reads",
        "edf_annotation_or_event_reads",
        "event_sidecar_requests_or_reads",
        "signal_sample_reads",
        "task_target_label_epoch_trial_reads",
        "channel_montage_reference_geometry_sampling_quality_reads",
        "epoch_window_feature_cache_operations",
        "split_operations",
        "model_or_checkpoint_accesses",
        "model_inference_runs",
        "training_or_parameter_update_runs",
        "scoring_or_selection_runs",
        "other_real_dataset_operations",
        "additional_file_participant_run_or_substitution_requests",
        "payload_retries",
        "language_model_or_provider_operations",
        "rw3_stream_device_or_hardware_operations",
        "upload_publication_or_release_operations",
        "work_order_9_operations",
        "reruns",
    )
    forbidden_zero = all(counters[key] == 0 for key in forbidden_keys)
    gates = _gate_results(
        status=status,
        metadata_matched=metadata_matched,
        transfer_complete=transfer_complete,
        integrity_matched=integrity_matched,
        bundle_promoted=bundle_promoted,
        resource_caps_passed=resource_caps_passed,
        forbidden_counters_zero=forbidden_zero,
    )
    manifest = _build_manifest(
        status=status,
        contract=contract,
        evidence=evidence,
        started_at=started_at,
        finished_at=finished_at,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss,
        free_disk_before_bytes=free_before,
        free_disk_after_bytes=shutil.disk_usage(root).free,
        incremental_disk_peak_bytes=incremental_peak,
        counters=counters,
        file_records=file_records,
        hash_passes_by_path=hash_passes_by_path,
        final_payload_bytes=final_payload_bytes,
        final_file_count=final_file_count,
        failure_stage=failure_stage,
        failure_reason=failure_reason,
        gates=gates,
    )
    machine_path, human_path = _write_receipts(
        manifest=manifest,
        receipt_root=receipt_root,
        machine_name=contract["receipt_contract"]["machine_manifest"],
        human_name=contract["receipt_contract"]["human_receipt"],
        cap_bytes=storage["maximum_generated_receipt_bytes_combined"],
        workspace_root=root,
        baseline_allocated_bytes=completed_allocated,
        incremental_disk_cap_bytes=storage[
            "maximum_incremental_disk_bytes_including_temporary_files"
        ],
    )
    return AcquisitionOutcome(
        status=status,
        manifest=manifest,
        manifest_path=machine_path,
        receipt_path=human_path,
    )


def execute_registered_acquisition(
    repo_root: str | Path,
    *,
    evidence: ExecutionEvidence,
) -> AcquisitionOutcome:
    """Run the one frozen PhysioNet acquisition after all remote-green gates."""

    root = Path(repo_root)
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    if decision["authorized_contract"]["sha256"] != CONTRACT_SHA256:
        raise AcquisitionRefusal("authorization decision does not bind the frozen contract")
    authorization = decision["authorization"]
    required_true = (
        "acquisition_implementation_authorized_now",
        "registered_source_metadata_reverification_authorized_now",
        "one_bounded_acquisition_invocation_authorized_now",
        "nine_named_edf_download_authorized_now",
        "opaque_size_and_sha256_hashing_authorized_now",
    )
    if not all(authorization.get(key) is True for key in required_true):
        raise AcquisitionRefusal("authorization decision does not enable the registered execution")
    required_false = (
        "edf_header_or_annotation_parse_authorized_now",
        "event_sidecar_access_authorized_now",
        "signal_sample_read_authorized_now",
        "event_or_target_read_authorized_now",
        "cache_or_split_authorized_now",
        "model_or_checkpoint_access_authorized_now",
        "model_inference_authorized_now",
        "training_or_parameter_update_authorized_now",
        "scoring_authorized_now",
        "additional_file_participant_run_or_substitution_authorized_now",
        "rerun_authorized_now",
        "language_model_or_provider_authorized_now",
        "rw3_stream_device_or_hardware_authorized_now",
        "upload_publication_or_release_authorized_now",
        "work_order_9_authorized_now",
        "scientific_claim_upgrade_authorized_now",
    )
    if not all(authorization.get(key) is False for key in required_false):
        raise AcquisitionRefusal("authorization decision contains a forbidden scope expansion")
    if contract["storage_and_output"]["expected_final_payload_bytes"] != EXPECTED_PAYLOAD_BYTES:
        raise AcquisitionRefusal("registered payload byte total drifted")
    _verify_execution_evidence(root, evidence)
    return run_acquisition(
        contract=contract,
        evidence=evidence,
        workspace_root=root,
        metadata_fetcher=_fetch_registered_metadata,
        payload_opener=_open_payload,
        environ=os.environ,
    )
