"""One-shot opaque acquisition for the registered WO9R PhysioNet cohort."""

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
import urllib.request
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path(
    "registries/physionet_low_frequency_cohort_confirmation_contract.v0.json"
)
DECISION_RELATIVE_PATH = Path(
    "registries/physionet_low_frequency_cohort_confirmation_authorization_decision.v0.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/physionet_low_frequency_cohort_confirmation_implementation.v0.json"
)
CONTRACT_SHA256 = "ce0dcf5e5ddd598fb69b5baa73f827bbc3f51c4aeab8578d2d2eebda87cd0935"
DECISION_SHA256 = "8d87b57a825840c4b749dc628fa95871ba1832f5ffd0b4e8138a3de533756c9c"
DECISION_COMMIT = "1efeac7f0b7b316bb94effb1a2eeeb1bbf99f50a"
DECISION_CI_RUN_ID = 31355944651
DECISION_BASE_JOB_ID = 93355535398
DECISION_OPTIONAL_JOB_ID = 93355535361
CHUNK_BYTES = 1024 * 1024
MAX_LOCKED_JSON_BYTES = 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


class WO9RAcquisitionRefusal(RuntimeError):
    """A preflight failed before the registered acquisition was consumed."""


class WO9RAcquisitionFailure(RuntimeError):
    """The registered one-shot acquisition was consumed and parked."""

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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    payload = path.read_bytes()
    if len(payload) > MAX_LOCKED_JSON_BYTES:
        raise WO9RAcquisitionRefusal(f"locked JSON exceeds 1 MiB: {path}")
    observed = _sha256_bytes(payload)
    if observed != expected_sha256:
        raise WO9RAcquisitionRefusal(
            f"locked JSON hash mismatch for {path}: expected {expected_sha256}, got {observed}"
        )
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise WO9RAcquisitionRefusal(f"locked JSON must be an object: {path}")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    if contract.get("schema_name") != (
        "neurodecodekit.physionet_low_frequency_cohort_confirmation_contract"
    ):
        raise WO9RAcquisitionRefusal("WO9R contract schema mismatch")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise WO9RAcquisitionRefusal("WO9R contract version mismatch")
    if len(contract.get("selected_files", [])) != 72:
        raise WO9RAcquisitionRefusal("WO9R contract does not contain 72 files")
    return contract


def load_registered_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    if decision.get("schema_name") != (
        "neurodecodekit.physionet_low_frequency_cohort_confirmation_"
        "authorization_decision"
    ):
        raise WO9RAcquisitionRefusal("WO9R decision schema mismatch")
    if decision.get("authorized_contract", {}).get("sha256") != CONTRACT_SHA256:
        raise WO9RAcquisitionRefusal("WO9R decision does not bind the contract")
    return decision


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact plan without path stats, environment imports, or network."""

    contract = load_registered_contract(repo_root)
    load_registered_decision(repo_root)
    binding = contract["dataset_binding"]
    caps = contract["resource_caps"]["acquisition"]
    acquisition = contract["acquisition_contract"]
    return {
        "schema_name": "neurodecodekit.physionet_low_frequency_acquisition_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run_no_registered_path_stat_no_network",
        "subjects": binding["participants"],
        "runs": ["03", "04", "07", "08", "11", "12"],
        "file_count": binding["file_count"],
        "payload_bytes": binding["exact_payload_bytes"],
        "payload_root": acquisition["payload_root"],
        "temporary_root": acquisition["temporary_root"],
        "receipt_root": acquisition["receipt_root"],
        "metadata_documents": acquisition["metadata_reverification_documents"],
        "payload_requests": acquisition["edf_payload_requests"],
        "caps": caps,
        "next_gate": "exact_implementation_commit_and_both_ci_jobs_must_be_green",
        "warnings": [
            "dry_run_only_no_registered_path_stat_or_network_access",
            "execute_consumes_the_single_no_retry_acquisition",
            "edf_content_remains_opaque_during_acquisition",
            "acquisition_is_not_an_eeg_or_decoding_result",
        ],
    }


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise WO9RAcquisitionFailure("path", f"unsafe relative path: {value!r}")
    return path


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    mismatches = {key: environ.get(key) for key in THREAD_ENV_KEYS if environ.get(key) != "1"}
    if mismatches:
        raise WO9RAcquisitionRefusal(f"one-thread environment is not exact: {mismatches}")


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
        raise WO9RAcquisitionRefusal("current HEAD differs from implementation evidence")
    if _git(repo_root, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise WO9RAcquisitionRefusal("tracked worktree changes are forbidden")
    if _git(repo_root, "merge-base", "--is-ancestor", DECISION_COMMIT, "HEAD").returncode:
        raise WO9RAcquisitionRefusal("green decision is not an implementation ancestor")
    if min(
        evidence.implementation_ci_run_id,
        evidence.base_python_job_id,
        evidence.optional_neuro_job_id,
    ) <= 0:
        raise WO9RAcquisitionRefusal("positive implementation CI identifiers are required")
    registry_path = repo_root / IMPLEMENTATION_RELATIVE_PATH
    if _git(repo_root, "cat-file", "-e", f"HEAD:{IMPLEMENTATION_RELATIVE_PATH}").returncode:
        raise WO9RAcquisitionRefusal("implementation registry is not tracked at HEAD")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema_name") != (
        "neurodecodekit.physionet_low_frequency_cohort_confirmation_implementation"
    ):
        raise WO9RAcquisitionRefusal("implementation registry schema mismatch")
    expected_parent = {
        "commit": DECISION_COMMIT,
        "push_ci_run_id": DECISION_CI_RUN_ID,
        "base_python_job_id": DECISION_BASE_JOB_ID,
        "optional_neuro_job_id": DECISION_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
    }
    if registry.get("green_authorization_decision") != expected_parent:
        raise WO9RAcquisitionRefusal("implementation registry decision proof mismatch")
    for row in registry.get("tracked_file_hashes", []):
        path = repo_root / _safe_relative_path(str(row["path"]))
        if _file_sha256(path) != row["sha256"]:
            raise WO9RAcquisitionRefusal(f"implementation hash mismatch: {row['path']}")
    if registry.get("fixture_qualification", {}).get("all_gates_passed") is not True:
        raise WO9RAcquisitionRefusal("generated-fixture qualification is not passed")
    if any(registry.get("implementation_access_counters", {}).values()):
        raise WO9RAcquisitionRefusal("implementation registry reports a real operation")
    return registry


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise WO9RAcquisitionFailure("network", f"redirect forbidden: {newurl}")


def _open_url_once(url: str, maximum_bytes: int) -> BinaryIO:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NeuroDecodeKit-WO9R/0.1"},
        method="GET",
    )
    response = urllib.request.build_opener(_RejectRedirect).open(request, timeout=60)
    status_code = getattr(response, "status", response.getcode())
    if status_code != 200:
        response.close()
        raise WO9RAcquisitionFailure("network", f"unexpected HTTP status {status_code}")
    content_length = response.headers.get("Content-Length")
    if content_length is not None and int(content_length) > maximum_bytes:
        response.close()
        raise WO9RAcquisitionFailure("network", "response Content-Length exceeds cap")
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
        raise WO9RAcquisitionFailure("metadata", "metadata response exceeds cap")
    return payload


def _manifest_checksums(payload: bytes) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw_line in payload.decode("utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        pieces = line.split()
        if len(pieces) != 2 or len(pieces[0]) != 64:
            raise WO9RAcquisitionFailure("metadata", "checksum manifest line is malformed")
        path = pieces[1].lstrip("*")
        if path in rows:
            raise WO9RAcquisitionFailure("metadata", "duplicate checksum path")
        rows[path] = pieces[0].lower()
    return rows


def _s3_objects(payload: bytes) -> dict[str, int]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise WO9RAcquisitionFailure("metadata", "S3 listing XML is malformed") from exc
    rows: dict[str, int] = {}
    for contents in root.iter():
        if contents.tag.rsplit("}", 1)[-1] != "Contents":
            continue
        key = None
        size = None
        for child in contents:
            local = child.tag.rsplit("}", 1)[-1]
            if local == "Key":
                key = child.text
            elif local == "Size":
                size = child.text
        if key is None or size is None or key in rows:
            raise WO9RAcquisitionFailure("metadata", "S3 listing object is malformed")
        rows[key] = int(size)
    return rows


def validate_metadata_documents(
    contract: Mapping[str, Any],
    documents: Mapping[str, bytes],
) -> dict[str, Any]:
    """Validate the 15 registered metadata documents without opening an EDF URL."""

    metadata = contract["metadata_registration"]
    required_urls = [
        metadata["official_dataset_url"],
        metadata["task_mapping_url"],
        metadata["official_checksum_manifest_url"],
        *[row["url"] for row in metadata["retained_documents"] if "s3_listing" in row["source_id"]],
    ]
    if len(required_urls) != 15 or set(documents) != set(required_urls):
        raise WO9RAcquisitionFailure("metadata", "metadata URL inventory is not exact")
    dataset_text = documents[metadata["official_dataset_url"]].decode("utf-8", "replace").lower()
    for token in ("eeg motor movement/imagery", "1.0.0", "10.13026/c28g6p"):
        if token not in dataset_text:
            raise WO9RAcquisitionFailure("metadata", f"dataset page is missing {token!r}")
    task_text = documents[metadata["task_mapping_url"]].decode("utf-8", "replace").lower()
    for token in ("eegbci", "3, 7, 11", "4, 8, 12"):
        if token not in task_text:
            raise WO9RAcquisitionFailure("metadata", f"task mapping is missing {token!r}")
    checksums = _manifest_checksums(documents[metadata["official_checksum_manifest_url"]])
    listing_rows: dict[str, int] = {}
    for row in metadata["retained_documents"]:
        if "s3_listing" in row["source_id"]:
            listing_rows.update(_s3_objects(documents[row["url"]]))
    prefix = metadata["official_s3_prefix"]
    for row in contract["selected_files"]:
        path = str(row["path"])
        object_key = f"{prefix}{path}"
        if listing_rows.get(object_key) != int(row["size_bytes"]):
            raise WO9RAcquisitionFailure("metadata", f"S3 path/size mismatch: {path}")
        manifest_candidates = (path, object_key, f"./{path}")
        observed = next((checksums[key] for key in manifest_candidates if key in checksums), None)
        if observed != row["sha256"]:
            raise WO9RAcquisitionFailure("metadata", f"checksum mismatch: {path}")
    return {
        "document_count": 15,
        "validated_files": len(contract["selected_files"]),
        "metadata_body_bytes": sum(len(value) for value in documents.values()),
    }


def fetch_registered_metadata(
    contract: Mapping[str, Any],
    opener: URLopener,
) -> tuple[dict[str, bytes], int]:
    metadata = contract["metadata_registration"]
    urls = [
        metadata["official_dataset_url"],
        metadata["task_mapping_url"],
        metadata["official_checksum_manifest_url"],
        *[row["url"] for row in metadata["retained_documents"] if "s3_listing" in row["source_id"]],
    ]
    cap = int(contract["resource_caps"]["acquisition"]["metadata_body_bytes"])
    documents: dict[str, bytes] = {}
    total = 0
    for url in urls:
        with _managed_stream(opener(url, cap - total)) as stream:
            payload = _read_bounded(stream, cap - total)
        total += len(payload)
        documents[url] = payload
    validate_metadata_documents(contract, documents)
    return documents, total


def _write_json_exclusive(path: Path, value: Mapping[str, Any], cap: int) -> int:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > cap:
        raise WO9RAcquisitionFailure("output", "JSON receipt exceeds cap")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError:
        raise WO9RAcquisitionRefusal(f"refusing to replace output: {path}") from None
    return len(payload)


def _assert_safe_path_chain(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise WO9RAcquisitionRefusal("registered path escapes the workspace root") from exc
    current = root
    for part in relative.parts:
        current /= part
        if not current.exists() and not current.is_symlink():
            continue
        observed = os.lstat(current)
        if stat.S_ISLNK(observed.st_mode):
            raise WO9RAcquisitionRefusal(f"registered path crosses a symlink: {current}")


def _tree_bytes_regular(path: Path) -> int:
    total = 0
    for current_root, directories, filenames in os.walk(path, followlinks=False):
        current = Path(current_root)
        if any((current / name).is_symlink() for name in directories):
            raise WO9RAcquisitionFailure("output", "output tree contains a symlink directory")
        for filename in filenames:
            candidate = current / filename
            if candidate.is_symlink():
                raise WO9RAcquisitionFailure("output", "output tree contains a symlink file")
            total += candidate.stat().st_size
    return total


def _hash_regular_nofollow(path: Path) -> tuple[int, str]:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise WO9RAcquisitionFailure("integrity", f"payload is not a regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    digest = hashlib.sha256()
    total = 0
    with os.fdopen(descriptor, "rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            total += len(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def _human_receipt(manifest: Mapping[str, Any]) -> bytes:
    measurements = manifest["measurements"]
    text = (
        "# WO9R PhysioNet Acquisition Receipt\n\n"
        f"Status: **{manifest['status']}**\n\n"
        f"Files: {measurements['edf_payload_requests']}\n\n"
        f"Payload bytes: {measurements['edf_payload_bytes']}\n\n"
        f"Metadata body bytes: {measurements['metadata_body_bytes']}\n\n"
        f"Runtime seconds: {measurements['runtime_seconds']}\n\n"
        f"Peak RSS bytes: {measurements['peak_rss_bytes']}\n\n"
        "EDF content was not parsed. This receipt establishes acquisition integrity only.\n"
    )
    return text.encode("utf-8")


def run_acquisition(
    *,
    workspace_root: str | Path,
    contract: Mapping[str, Any],
    opener: URLopener,
    environ: Mapping[str, str],
    enforce_registered_roots: bool,
    minimum_free_disk_bytes: int | None = None,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> AcquisitionOutcome:
    """Run the shared one-shot acquisition core with real or mocked transport."""

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
        expected = load_registered_contract(root)
        if contract != expected:
            raise WO9RAcquisitionRefusal("real acquisition contract differs from registration")
    selected_files = contract.get("selected_files", [])
    selected_paths = [str(row.get("path", "")) for row in selected_files]
    if len(selected_files) != int(caps["edf_payload_requests"]):
        raise WO9RAcquisitionRefusal("selected-file count differs from the resource contract")
    if len(set(selected_paths)) != len(selected_paths):
        raise WO9RAcquisitionRefusal("selected-file paths are not unique")
    if sum(int(row.get("size_bytes", -1)) for row in selected_files) != int(
        caps["edf_payload_bytes"]
    ):
        raise WO9RAcquisitionRefusal("selected-file bytes differ from the resource contract")
    for path in selected_paths:
        _safe_relative_path(path)
    if int(caps["edf_payload_bytes"]) + int(caps["receipt_bytes"]) > int(
        caps["peak_incremental_disk_bytes"]
    ):
        raise WO9RAcquisitionRefusal("registered payload and receipt caps exceed disk cap")
    for path in (payload_root, temporary_root, receipt_root):
        if path.exists() or path.is_symlink():
            raise WO9RAcquisitionRefusal(f"exclusive acquisition path already exists: {path}")
    required_free = (
        int(caps["minimum_free_disk_bytes_before"])
        if minimum_free_disk_bytes is None
        else int(minimum_free_disk_bytes)
    )
    if shutil.disk_usage(root).free < required_free:
        raise WO9RAcquisitionRefusal("free disk is below the registered minimum")
    started = time.monotonic()
    start_rss = rss_reader()
    free_disk_before = shutil.disk_usage(root).free
    receipt_root.mkdir(parents=True, exist_ok=False)
    consumed_path = receipt_root / "acquisition_consumed.v0.json"
    _write_json_exclusive(
        consumed_path,
        {
            "schema_name": "neurodecodekit.physionet_low_frequency_acquisition_consumed",
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
        _, metadata_bytes = fetch_registered_metadata(contract, opener)
        if time.monotonic() - started > float(caps["wall_time_seconds"]):
            raise WO9RAcquisitionFailure("resource", "metadata wall cap exceeded")
        if rss_reader() > int(caps["peak_rss_bytes"]):
            raise WO9RAcquisitionFailure("resource", "metadata RSS cap exceeded")
        rows = []
        payload_bytes = 0
        file_root = contract["metadata_registration"]["official_file_root_url"].rstrip("/")
        for row in selected_files:
            relative = _safe_relative_path(str(row["path"]))
            destination = temporary_bundle / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            expected_size = int(row["size_bytes"])
            with _managed_stream(opener(f"{file_root}/{row['path']}", expected_size)) as stream:
                try:
                    handle = destination.open("xb")
                except FileExistsError:
                    raise WO9RAcquisitionFailure("payload", "duplicate payload path") from None
                network_count = 0
                with handle:
                    while True:
                        chunk = stream.read(min(CHUNK_BYTES, expected_size - network_count + 1))
                        if not chunk:
                            break
                        network_count += len(chunk)
                        if network_count > expected_size:
                            raise WO9RAcquisitionFailure("payload", "payload exceeds expected size")
                        handle.write(chunk)
            if network_count != expected_size:
                raise WO9RAcquisitionFailure("payload", "payload ended before expected size")
            local_size, local_sha256 = _hash_regular_nofollow(destination)
            if local_size != expected_size or local_sha256 != row["sha256"]:
                raise WO9RAcquisitionFailure("integrity", f"payload hash mismatch: {row['path']}")
            payload_bytes += local_size
            rows.append(
                {
                    "path": row["path"],
                    "size_bytes": local_size,
                    "official_sha256": row["sha256"],
                    "observed_local_sha256": local_sha256,
                    "local_hash_passes": 1,
                }
            )
            if time.monotonic() - started > float(caps["wall_time_seconds"]):
                raise WO9RAcquisitionFailure("resource", "acquisition wall cap exceeded")
            if rss_reader() > int(caps["peak_rss_bytes"]):
                raise WO9RAcquisitionFailure("resource", "acquisition RSS cap exceeded")
        if len(rows) != int(caps["edf_payload_requests"]):
            raise WO9RAcquisitionFailure("inventory", "payload request count mismatch")
        if payload_bytes != int(caps["edf_payload_bytes"]):
            raise WO9RAcquisitionFailure("inventory", "payload byte total mismatch")
        payload_root.parent.mkdir(parents=True, exist_ok=True)
        os.replace(temporary_bundle, payload_root)
        temporary_root.rmdir()
        runtime = time.monotonic() - started
        manifest = {
            "schema_name": "neurodecodekit.physionet_low_frequency_acquisition_manifest",
            "schema_version": SCHEMA_VERSION,
            "status": "passed",
            "contract_sha256": CONTRACT_SHA256 if enforce_registered_roots else None,
            "file_records": rows,
            "measurements": {
                "metadata_requests": 15,
                "metadata_body_bytes": metadata_bytes,
                "edf_payload_requests": len(rows),
                "edf_payload_bytes": payload_bytes,
                "opaque_local_hash_passes": len(rows),
                "edf_content_parses": 0,
                "runtime_seconds": round(runtime, 6),
                "peak_rss_bytes": rss_reader(),
                "starting_peak_rss_bytes": start_rss,
                "free_disk_bytes_before": free_disk_before,
                "free_disk_bytes_after_payload_promotion": 0,
                "retained_output_bytes": 0,
                "peak_incremental_disk_upper_bound_bytes": 0,
                "cpu_threads": 1,
                "workers": 1,
                "concurrent_numerical_jobs": 1,
                "retries": 0,
                "reruns": 0,
            },
            "warnings": [
                "edf_content_headers_annotations_signals_and_targets_unread",
                "acquisition_receipt_is_not_scientific_evidence",
            ],
            "created_at_utc": _utc_now(),
        }
        receipt_cap = int(caps["receipt_bytes"])
        manifest_path = receipt_root / acquisition["receipt_files"][0]
        receipt_path = receipt_root / acquisition["receipt_files"][1]
        free_disk_after_payload = shutil.disk_usage(root).free
        manifest["measurements"][
            "free_disk_bytes_after_payload_promotion"
        ] = free_disk_after_payload
        for _ in range(8):
            manifest_payload = (
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
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
            raise WO9RAcquisitionFailure("output", "disk byte measurement did not converge")
        if retained > int(caps["peak_incremental_disk_bytes"]):
            raise WO9RAcquisitionFailure("resource", "incremental disk cap exceeded")
        manifest_bytes = _write_json_exclusive(manifest_path, manifest, receipt_cap)
        if manifest_bytes + len(receipt_payload) > receipt_cap:
            raise WO9RAcquisitionFailure("output", "combined receipts exceed cap")
        with receipt_path.open("xb") as handle:
            handle.write(receipt_payload)
        observed_retained = _tree_bytes_regular(payload_root) + _tree_bytes_regular(receipt_root)
        if observed_retained != retained:
            raise WO9RAcquisitionFailure("output", "retained byte measurement differs")
        if time.monotonic() - started > float(caps["wall_time_seconds"]):
            raise WO9RAcquisitionFailure("resource", "acquisition wall cap exceeded")
        if rss_reader() > int(caps["peak_rss_bytes"]):
            raise WO9RAcquisitionFailure("resource", "acquisition RSS cap exceeded")
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
    """Consume the one registered real acquisition after remote-green implementation."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    _validate_implementation_registry(root, evidence)
    return run_acquisition(
        workspace_root=root,
        contract=contract,
        opener=_open_url_once,
        environ=environ,
        enforce_registered_roots=True,
    )


def synthetic_metadata_documents(
    contract: Mapping[str, Any],
    selected_files: Sequence[Mapping[str, Any]],
) -> dict[str, bytes]:
    """Create deterministic generated metadata fixtures for the shared validator."""

    metadata = contract["metadata_registration"]
    documents = {
        metadata["official_dataset_url"]: (
            b"EEG Motor Movement/Imagery Dataset 1.0.0 DOI 10.13026/C28G6P"
        ),
        metadata["task_mapping_url"]: b"eegbci runs 3, 7, 11 and runs 4, 8, 12",
    }
    manifest_lines = []
    by_subject: dict[str, list[Mapping[str, Any]]] = {}
    for row in selected_files:
        by_subject.setdefault(str(row["subject"]), []).append(row)
        manifest_lines.append(f"{row['sha256']}  {row['path']}")
    documents[metadata["official_checksum_manifest_url"]] = (
        "\n".join(manifest_lines) + "\n"
    ).encode("utf-8")
    prefix = metadata["official_s3_prefix"]
    for registered in metadata["retained_documents"]:
        if "s3_listing" not in registered["source_id"]:
            continue
        subject = registered["source_id"].rsplit("_", 1)[-1]
        contents = "".join(
            f"<Contents><Key>{prefix}{row['path']}</Key>"
            f"<Size>{row['size_bytes']}</Size></Contents>"
            for row in by_subject.get(subject, [])
        )
        documents[registered["url"]] = (
            f"<ListBucketResult xmlns=\"http://s3.amazonaws.com/doc/2006-03-01/\">"
            f"{contents}</ListBucketResult>"
        ).encode("utf-8")
    return documents


def bytes_opener(payloads: Mapping[str, bytes]) -> URLopener:
    """Return a no-network one-open-per-call transport for generated qualification."""

    def open_payload(url: str, maximum_bytes: int) -> BinaryIO:
        if url not in payloads:
            raise WO9RAcquisitionFailure("fixture", f"unexpected fixture URL: {url}")
        payload = payloads[url]
        if len(payload) > maximum_bytes:
            raise WO9RAcquisitionFailure("fixture", "fixture payload exceeds requested cap")
        return io.BytesIO(payload)

    return open_payload
