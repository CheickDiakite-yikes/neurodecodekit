"""Generated-only acquisition qualification surface for EEGMMIDB-UG1.

This module intentionally has no network client and no EDF reader.  It plans the
registered 36-file inventory and can exercise acquisition mechanics only through
sentinel-marked bytes supplied by an in-memory mock transport.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
import io
import json
import os
import re
import resource
import shutil
import stat
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_generalization_contract.v0.json"
)
AMENDMENT_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_generalization_amendment_1.v0.json"
)
CONTRACT_SHA256 = "1df7f4f139809d94a6135d979e8cd37e1ece9b87d001b12bcefd037c63b8ac37"
AMENDMENT_SHA256 = "2d6576e2f31383efdcc1ea9f309e70c4beabdf440149567f7eabcbf1a2b177dd"
DATASET_NAME = "EEG Motor Movement/Imagery Dataset"
DATASET_VERSION = "1.0.0"
DATASET_DOI = "10.13026/C28G6P"
FILE_ROOT_URL = "https://physionet.org/files/eegmmidb/1.0.0/"
SOURCE_PARTICIPANTS = tuple(f"S{index:03d}" for index in range(1, 4))
FRESH_PARTICIPANTS = tuple(f"S{index:03d}" for index in range(16, 31))
SOURCE_RUNS = ("04", "08")
FRESH_RUNS = ("11", "12")
GENERATED_SENTINEL = b"NEURODECODEKIT-UG1-GENERATED-NOT-EDF\x00"
CHUNK_BYTES = 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
FORBIDDEN_OUTPUT_COMPONENTS = frozenset({".codex_work", "data"})
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
GENERATED_VALIDATOR_PATTERN = re.compile(r"generated-sha256:[0-9a-f]{16}")


class UG1AcquisitionRefusal(RuntimeError):
    """A generated qualification request failed before writing output."""


class UG1AcquisitionFailure(RuntimeError):
    """A generated qualification failed after its temporary output began."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


@dataclass(frozen=True)
class PlannedFile:
    """One immutable, target-free UG1 file identity."""

    repository_path: str
    partition: str
    participant: str
    run: str

    @property
    def url(self) -> str:
        return f"{FILE_ROOT_URL}{self.repository_path}"


@dataclass(frozen=True)
class InventoryRecord:
    """Metadata needed to qualify opaque acquisition without parsing content."""

    repository_path: str
    partition: str
    participant: str
    run: str
    size_bytes: int
    sha256: str
    validator: str


@dataclass(frozen=True)
class GeneratedResponse:
    """In-memory response returned by the generated mock transport."""

    requested_url: str
    final_url: str
    body: bytes
    status_code: int = 200
    declared_size: int | None = None

    def open(self) -> BinaryIO:
        return io.BytesIO(self.body)


class GeneratedMockTransport:
    """Deterministic mapping-backed transport with no network capability."""

    def __init__(self, responses: Mapping[str, GeneratedResponse | bytes]) -> None:
        self._responses = dict(responses)
        self.calls: list[tuple[str, int]] = []

    def __call__(self, url: str, maximum_bytes: int) -> GeneratedResponse:
        self.calls.append((url, maximum_bytes))
        try:
            value = self._responses[url]
        except KeyError as exc:
            raise UG1AcquisitionFailure("transport", f"unexpected fixture URL: {url}") from exc
        if isinstance(value, bytes):
            return GeneratedResponse(
                requested_url=url,
                final_url=url,
                body=value,
                declared_size=len(value),
            )
        return value

    def fixture_sha256s(self) -> dict[str, str]:
        """Return target-free source fingerprints without changing call state."""

        return {
            url: _sha256(value if isinstance(value, bytes) else value.body)
            for url, value in sorted(self._responses.items())
        }


@dataclass(frozen=True)
class GeneratedAcquisitionCaps:
    """Frozen Stage G maxima inherited from the amended contract."""

    input_bytes: int = 268_435_456
    cumulative_output_bytes: int = 536_870_912
    manifest_bytes: int = 2_097_152
    wall_time_seconds: float = 900.0
    peak_process_tree_rss_bytes: int = 1_073_741_824
    minimum_free_disk_bytes: int = 2_147_483_648


@dataclass(frozen=True)
class GeneratedAcquisitionOutcome:
    """Dry or executed generated-only acquisition result."""

    status: str
    manifest: dict[str, Any]
    manifest_bytes: bytes
    manifest_sha256: str
    payload_root: Path | None
    manifest_path: Path | None
    measurements: dict[str, Any]


Transport = Callable[[str, int], GeneratedResponse]
FaultInjector = Callable[[str], None]


def _expected_files() -> tuple[PlannedFile, ...]:
    rows = [
        PlannedFile(
            repository_path=f"{participant}/{participant}R{run}.edf",
            partition="source_fit_missing",
            participant=participant,
            run=run,
        )
        for participant in SOURCE_PARTICIPANTS
        for run in SOURCE_RUNS
    ]
    rows.extend(
        PlannedFile(
            repository_path=f"{participant}/{participant}R{run}.edf",
            partition="fresh_final",
            participant=participant,
            run=run,
        )
        for participant in FRESH_PARTICIPANTS
        for run in FRESH_RUNS
    )
    return tuple(rows)


EXPECTED_FILES = _expected_files()
EXPECTED_PATHS = tuple(row.repository_path for row in EXPECTED_FILES)


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _peak_process_tree_rss_bytes() -> int:
    own = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    children = int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    multiplier = 1 if sys.platform == "darwin" else 1024
    return (own + children) * multiplier


def _safe_relative_path(value: str, *, output: bool = False) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise UG1AcquisitionRefusal(f"unsafe relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise UG1AcquisitionRefusal(f"unsafe relative path: {value!r}")
    if output and any(part in FORBIDDEN_OUTPUT_COMPONENTS for part in path.parts):
        raise UG1AcquisitionRefusal("generated output may not use a real or ignored data root")
    return path


def _open_regular_nofollow(path: Path) -> bytes:
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise UG1AcquisitionRefusal(f"locked input is not a single-link regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        observed = os.fstat(handle.fileno())
        if (
            not stat.S_ISREG(observed.st_mode)
            or observed.st_nlink != 1
            or (observed.st_dev, observed.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise UG1AcquisitionRefusal(f"locked input is not a single-link regular file: {path}")
        return handle.read()


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    try:
        payload = _open_regular_nofollow(path)
    except OSError as exc:
        raise UG1AcquisitionRefusal(f"cannot read locked registry: {path}") from exc
    observed = _sha256(payload)
    if observed != expected_sha256:
        raise UG1AcquisitionRefusal(
            f"locked registry hash mismatch: expected {expected_sha256}, got {observed}"
        )
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UG1AcquisitionRefusal(f"locked registry is malformed: {path}") from exc
    if not isinstance(value, dict):
        raise UG1AcquisitionRefusal(f"locked registry must be an object: {path}")
    return value


def _load_registration(repo_root: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(os.path.abspath(os.fspath(repo_root)))
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    amendment = _load_locked_json(root / AMENDMENT_RELATIVE_PATH, AMENDMENT_SHA256)
    if contract.get("schema_name") != (
        "neurodecodekit.eegmmidb_unseen_participant_generalization_contract"
    ):
        raise UG1AcquisitionRefusal("UG1 contract schema mismatch")
    if amendment.get("schema_name") != (
        "neurodecodekit.eegmmidb_unseen_participant_generalization_amendment"
    ):
        raise UG1AcquisitionRefusal("UG1 amendment schema mismatch")
    if amendment.get("lane_id") != "EEGMMIDB-UG1":
        raise UG1AcquisitionRefusal("UG1 amendment lane mismatch")
    return contract, amendment


def registered_plan(repo_root: str | Path) -> dict[str, Any]:
    """Return the exact dry plan without output-path or network access."""

    contract, amendment = _load_registration(repo_root)
    inventory = contract["new_file_inventory"]
    resources = amendment["resource_enforcement"]
    if inventory.get("total_files") != len(EXPECTED_FILES):
        raise UG1AcquisitionRefusal("registered file count is not 36")
    if inventory.get("source_files") != 6 or inventory.get("fresh_files") != 30:
        raise UG1AcquisitionRefusal("registered source/fresh file counts drifted")
    if inventory.get("event_sidecars_allowed") is not False:
        raise UG1AcquisitionRefusal("event sidecars must remain forbidden")
    return {
        "schema_name": "neurodecodekit.eegmmidb_ug1_acquisition_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run_no_output_path_stat_no_transport_call",
        "dataset": {
            "name": DATASET_NAME,
            "version": DATASET_VERSION,
            "doi": DATASET_DOI,
        },
        "files": [
            {
                "repository_path": row.repository_path,
                "partition": row.partition,
                "participant": row.participant,
                "run": row.run,
            }
            for row in EXPECTED_FILES
        ],
        "file_count": len(EXPECTED_FILES),
        "source_file_count": 6,
        "fresh_file_count": 30,
        "sizes_known": False,
        "caps": {
            "metadata_requests": 36,
            "metadata_bytes": resources["metadata_network_bytes_maximum"],
            "payload_requests": 36,
            "payload_bytes": resources["payload_network_bytes_maximum"],
            "incremental_disk_bytes": resources["incremental_disk_bytes_maximum"],
            "manifest_bytes": resources["public_artifact_bytes_maximum"],
            "stage_g_wall_time_seconds": resources["stage_wall_time_seconds_maximum"]["G"],
            "peak_process_tree_rss_bytes": resources["process_tree_peak_RSS_bytes_maximum"],
        },
        "operation_counters": {
            "transport_calls": 0,
            "network_bytes": 0,
            "real_path_reads": 0,
            "edf_content_parses": 0,
            "parameter_update_fits": 0,
            "prediction_sets": 0,
            "model_runs": 0,
            "target_deliveries": 0,
            "scoring_events": 0,
        },
        "warnings": [
            "dry_plan_only",
            "sizes_and_hashes_unavailable_until_metadata_stage",
            "event_sidecars_forbidden",
            "generated_qualification_is_not_a_neural_or_decoding_result",
        ],
    }


def _record_dict(record: InventoryRecord) -> dict[str, Any]:
    return {
        "repository_path": record.repository_path,
        "partition": record.partition,
        "participant": record.participant,
        "run": record.run,
        "size_bytes": record.size_bytes,
        "sha256": record.sha256,
        "validator": record.validator,
    }


def validate_inventory(
    records: Sequence[InventoryRecord],
    *,
    maximum_payload_bytes: int = 268_435_456,
) -> tuple[InventoryRecord, ...]:
    """Validate and canonically order an exact target-free 36-file inventory."""

    if len(records) != len(EXPECTED_FILES):
        raise UG1AcquisitionRefusal("inventory must contain exactly 36 files")
    by_path: dict[str, InventoryRecord] = {}
    for record in records:
        if not isinstance(record, InventoryRecord):
            raise UG1AcquisitionRefusal("inventory rows must be InventoryRecord values")
        path = str(_safe_relative_path(record.repository_path))
        if not path.endswith(".edf") or ".event" in path.lower():
            raise UG1AcquisitionRefusal("only the exact EDF inventory is allowed")
        if path in by_path:
            raise UG1AcquisitionRefusal(f"duplicate inventory path: {path}")
        if not isinstance(record.size_bytes, int) or isinstance(record.size_bytes, bool):
            raise UG1AcquisitionRefusal("inventory size must be an integer")
        if record.size_bytes <= len(GENERATED_SENTINEL):
            raise UG1AcquisitionRefusal("generated fixture size is too small")
        if SHA256_PATTERN.fullmatch(record.sha256) is None:
            raise UG1AcquisitionRefusal("inventory SHA-256 must be lowercase hexadecimal")
        if GENERATED_VALIDATOR_PATTERN.fullmatch(record.validator) is None:
            raise UG1AcquisitionRefusal("inventory validator is not a generated SHA-256 token")
        by_path[path] = record
    if set(by_path) != set(EXPECTED_PATHS):
        raise UG1AcquisitionRefusal("inventory paths differ from the frozen 36-file plan")
    ordered = tuple(by_path[path] for path in EXPECTED_PATHS)
    for expected, observed in zip(EXPECTED_FILES, ordered, strict=True):
        if (
            observed.partition != expected.partition
            or observed.participant != expected.participant
            or observed.run != expected.run
        ):
            raise UG1AcquisitionRefusal(f"inventory identity mismatch: {observed.repository_path}")
    total = sum(record.size_bytes for record in ordered)
    if total > maximum_payload_bytes:
        raise UG1AcquisitionRefusal("inventory payload bytes exceed the frozen cap")
    return ordered


def build_generated_fixture(
    *,
    bytes_per_file: int = 256,
) -> tuple[tuple[InventoryRecord, ...], GeneratedMockTransport]:
    """Build deterministic sentinel-marked bytes and their exact mock inventory."""

    if bytes_per_file <= len(GENERATED_SENTINEL) + 40:
        raise UG1AcquisitionRefusal("bytes_per_file is too small for the generated sentinel")
    records: list[InventoryRecord] = []
    responses: dict[str, bytes] = {}
    for index, planned in enumerate(EXPECTED_FILES):
        prefix = GENERATED_SENTINEL + f"{index:02d}|{planned.repository_path}|".encode("ascii")
        filler = hashlib.sha256(prefix).digest()
        repeats = (bytes_per_file - len(prefix) + len(filler) - 1) // len(filler)
        payload = (prefix + filler * repeats)[:bytes_per_file]
        digest = _sha256(payload)
        records.append(
            InventoryRecord(
                repository_path=planned.repository_path,
                partition=planned.partition,
                participant=planned.participant,
                run=planned.run,
                size_bytes=len(payload),
                sha256=digest,
                validator=f"generated-sha256:{digest[:16]}",
            )
        )
        responses[planned.url] = payload
    return tuple(records), GeneratedMockTransport(responses)


def _assert_thread_environment(environ: Mapping[str, str]) -> None:
    mismatches = {key: environ.get(key) for key in THREAD_ENV_KEYS if environ.get(key) != "1"}
    if mismatches:
        raise UG1AcquisitionRefusal(f"one-thread environment is not exact: {mismatches}")


def _lexical_root(path: str | Path) -> Path:
    root = Path(os.path.abspath(os.fspath(path)))
    try:
        observed = os.lstat(root)
    except OSError as exc:
        raise UG1AcquisitionRefusal("generated workspace root must already exist") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise UG1AcquisitionRefusal("generated workspace root must be a non-symlink directory")
    return root


def _assert_existing_chain_nofollow(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise UG1AcquisitionRefusal("generated output escapes its workspace") from exc
    current = root
    for part in relative.parts:
        current /= part
        try:
            observed = os.lstat(current)
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(observed.st_mode):
            raise UG1AcquisitionRefusal(f"generated output crosses a symlink: {current}")


def _mkdir_relative(root: Path, relative: PurePosixPath) -> Path:
    current = root
    for part in relative.parts:
        current /= part
        try:
            os.mkdir(current, 0o700)
        except FileExistsError:
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
                raise UG1AcquisitionFailure("path", f"unsafe generated directory: {current}")
    return current


def _rename_noreplace(source: Path, destination: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        rename = getattr(libc, "renamex_np", None)
        if rename is None:
            raise UG1AcquisitionFailure("output", "atomic no-replace rename is unavailable")
        rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
        rename.restype = ctypes.c_int
        result = rename(os.fsencode(source), os.fsencode(destination), 0x00000004)
    elif sys.platform.startswith("linux"):
        rename = getattr(libc, "renameat2", None)
        if rename is None:
            raise UG1AcquisitionFailure("output", "atomic no-replace rename is unavailable")
        rename.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        rename.restype = ctypes.c_int
        result = rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    else:
        raise UG1AcquisitionFailure("output", "atomic no-replace rename is unsupported")
    if result == 0:
        return
    error = ctypes.get_errno()
    if error == errno.EEXIST:
        raise UG1AcquisitionFailure("output", "destination appeared before atomic publish")
    raise OSError(error, os.strerror(error), destination)


def _write_atomic(
    path: Path,
    payload: bytes,
    *,
    _before_publish: Callable[[], None] | None = None,
) -> None:
    temporary = path.with_name(f".{path.name}.part")
    if path.exists() or path.is_symlink() or temporary.exists() or temporary.is_symlink():
        raise UG1AcquisitionFailure("output", f"exclusive output already exists: {path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            written = handle.write(payload)
            if written != len(payload):
                raise UG1AcquisitionFailure("output", "short generated output write")
            handle.flush()
            os.fsync(handle.fileno())
        observed_size, observed_sha256 = _hash_regular_nofollow(temporary)
        if observed_size != len(payload) or observed_sha256 != _sha256(payload):
            raise UG1AcquisitionFailure("output", "generated output verification failed")
        if _before_publish is not None:
            _before_publish()
        _rename_noreplace(temporary, path)
    except Exception:
        try:
            observed = os.lstat(temporary)
        except FileNotFoundError:
            pass
        else:
            if stat.S_ISREG(observed.st_mode) and observed.st_nlink == 1:
                temporary.unlink()
        raise


def _hash_regular_nofollow(path: Path) -> tuple[int, str]:
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise UG1AcquisitionFailure("integrity", f"not a single-link regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    digest = hashlib.sha256()
    total = 0
    with os.fdopen(descriptor, "rb") as handle:
        observed = os.fstat(handle.fileno())
        if (
            not stat.S_ISREG(observed.st_mode)
            or observed.st_nlink != 1
            or (observed.st_dev, observed.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise UG1AcquisitionFailure("integrity", f"not a single-link regular file: {path}")
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            total += len(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def _read_generated_response(
    response: GeneratedResponse,
    *,
    expected_url: str,
    expected_size: int,
) -> bytes:
    if not isinstance(response, GeneratedResponse):
        raise UG1AcquisitionFailure("transport", "mock transport returned an invalid response")
    if response.requested_url != expected_url or response.final_url != expected_url:
        raise UG1AcquisitionFailure("transport", "redirect or URL substitution is forbidden")
    if response.status_code != 200:
        raise UG1AcquisitionFailure("transport", "mock response status is not 200")
    if response.declared_size is not None and response.declared_size != expected_size:
        raise UG1AcquisitionFailure("transport", "mock declared size differs from inventory")
    with response.open() as stream:
        payload = stream.read(expected_size + 1)
        if stream.read(1):
            raise UG1AcquisitionFailure("transport", "mock response exceeds the bounded read")
    if len(payload) != expected_size:
        raise UG1AcquisitionFailure("transport", "mock response is partial or oversized")
    if not payload.startswith(GENERATED_SENTINEL):
        raise UG1AcquisitionFailure("firewall", "fixture lacks the generated-only sentinel")
    return payload


def _manifest_for(records: Sequence[InventoryRecord]) -> dict[str, Any]:
    record_rows = [_record_dict(record) for record in records]
    inventory_sha256 = _sha256(_canonical_json({"files": record_rows}))
    return {
        "schema_name": "neurodecodekit.eegmmidb_ug1_generated_acquisition_manifest",
        "schema_version": SCHEMA_VERSION,
        "mode": "generated_fixture_no_network_no_edf_parse",
        "dataset": {
            "name": DATASET_NAME,
            "version": DATASET_VERSION,
            "doi": DATASET_DOI,
        },
        "files": record_rows,
        "file_count": len(record_rows),
        "source_file_count": sum(row.partition == "source_fit_missing" for row in records),
        "fresh_file_count": sum(row.partition == "fresh_final" for row in records),
        "payload_bytes": sum(row.size_bytes for row in records),
        "inventory_sha256": inventory_sha256,
        "operation_counters": {
            "transport_calls": len(record_rows),
            "network_bytes": 0,
            "real_path_reads": 0,
            "edf_content_parses": 0,
            "parameter_update_fits": 0,
            "prediction_sets": 0,
            "model_runs": 0,
            "target_deliveries": 0,
            "scoring_events": 0,
        },
        "warnings": [
            "generated_sentinel_bytes_only",
            "metadata_and_payload_network_not_used",
            "edf_headers_annotations_and_signals_not_parsed",
            "manifest_is_interface_evidence_not_scientific_evidence",
        ],
    }


def _assert_no_protected_values(value: Any, path: tuple[str, ...] = ()) -> None:
    allowed_counter = ("operation_counters", "target_deliveries")
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise UG1AcquisitionRefusal("manifest keys must be strings")
            lowered = key.lower()
            child_path = (*path, key)
            if any(
                token in lowered for token in ("label", "annotation", "sentence", "class_id")
            ) or ("target" in lowered and child_path != allowed_counter):
                raise UG1AcquisitionRefusal(f"protected field is forbidden in manifest: {key}")
            _assert_no_protected_values(child, child_path)
    elif isinstance(value, list):
        for child in value:
            _assert_no_protected_values(child, path)


def validate_generated_manifest(
    manifest: Mapping[str, Any],
    inventory: Sequence[InventoryRecord],
) -> bytes:
    """Validate a canonical generated manifest and return its exact bytes."""

    ordered = validate_inventory(inventory)
    _assert_no_protected_values(manifest)
    expected = _manifest_for(ordered)
    if dict(manifest) != expected:
        raise UG1AcquisitionRefusal("generated manifest differs from canonical inventory")
    payload = _canonical_json(expected)
    if len(payload) > GeneratedAcquisitionCaps().manifest_bytes:
        raise UG1AcquisitionRefusal("generated manifest exceeds the public artifact cap")
    return payload


def _check_resources(
    *,
    started: float,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    caps: GeneratedAcquisitionCaps,
) -> tuple[float, int]:
    runtime = clock() - started
    rss = rss_reader()
    if runtime < 0 or runtime > caps.wall_time_seconds:
        raise UG1AcquisitionFailure("resource", "generated wall-time cap exceeded")
    if rss < 0 or rss > caps.peak_process_tree_rss_bytes:
        raise UG1AcquisitionFailure("resource", "generated process-tree RSS cap exceeded")
    return runtime, rss


def _cleanup_owned_staging(path: Path) -> None:
    try:
        observed = os.lstat(path)
    except FileNotFoundError:
        return
    if stat.S_ISDIR(observed.st_mode) and not stat.S_ISLNK(observed.st_mode):
        shutil.rmtree(path)


def run_generated_fixture_acquisition(
    *,
    inventory: Sequence[InventoryRecord],
    transport: Transport | None = None,
    workspace_root: str | Path | None = None,
    output_relative: str = "ug1-stage-g-generated",
    execute: bool = False,
    environ: Mapping[str, str] | None = None,
    caps: GeneratedAcquisitionCaps = GeneratedAcquisitionCaps(),
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_process_tree_rss_bytes,
    fault_injector: FaultInjector | None = None,
) -> GeneratedAcquisitionOutcome:
    """Dry-plan or execute one generated-only, no-network acquisition pass."""

    ordered = validate_inventory(inventory, maximum_payload_bytes=caps.input_bytes)
    manifest = _manifest_for(ordered)
    manifest_bytes = validate_generated_manifest(manifest, ordered)
    manifest_sha256 = _sha256(manifest_bytes)
    dry_measurements = {
        "input_bytes": 0,
        "output_bytes": 0,
        "cumulative_output_bytes": 0,
        "runtime_seconds": 0.0,
        "peak_process_tree_rss_bytes": 0,
        "transport_calls": 0,
        "network_bytes": 0,
        "real_path_reads": 0,
        "warnings": list(manifest["warnings"]),
    }
    if not execute:
        return GeneratedAcquisitionOutcome(
            status="dry_run",
            manifest=manifest,
            manifest_bytes=manifest_bytes,
            manifest_sha256=manifest_sha256,
            payload_root=None,
            manifest_path=None,
            measurements=dry_measurements,
        )
    if workspace_root is None:
        raise UG1AcquisitionRefusal("generated execution requires an explicit workspace root")
    if transport is None:
        raise UG1AcquisitionRefusal("generated execution requires an in-memory mock transport")
    _assert_thread_environment(os.environ if environ is None else environ)
    output_path = _safe_relative_path(output_relative, output=True)
    root = _lexical_root(workspace_root)
    destination = root.joinpath(*output_path.parts)
    staging = destination.with_name(f".{destination.name}.tmp")
    _assert_existing_chain_nofollow(root, destination)
    if destination.exists() or destination.is_symlink():
        raise UG1AcquisitionRefusal("generated destination already exists")
    if staging.exists() or staging.is_symlink():
        raise UG1AcquisitionRefusal("generated staging destination already exists")
    payload_bytes = sum(record.size_bytes for record in ordered)
    cumulative_upper_bound = 2 * (payload_bytes + len(manifest_bytes))
    if cumulative_upper_bound > caps.cumulative_output_bytes:
        raise UG1AcquisitionRefusal("generated temporary plus final output exceeds cap")
    if len(manifest_bytes) > caps.manifest_bytes:
        raise UG1AcquisitionRefusal("generated manifest exceeds cap")
    if shutil.disk_usage(root).free < max(
        caps.minimum_free_disk_bytes,
        payload_bytes + len(manifest_bytes),
    ):
        raise UG1AcquisitionRefusal("insufficient free disk for generated fixture")
    started = clock()
    peak_rss = rss_reader()
    _, observed_rss = _check_resources(
        started=started,
        clock=clock,
        rss_reader=lambda: peak_rss,
        caps=caps,
    )
    peak_rss = max(peak_rss, observed_rss)
    input_bytes = 0
    os.mkdir(staging, 0o700)
    try:
        payload_root = _mkdir_relative(staging, PurePosixPath("payloads"))
        for index, record in enumerate(ordered):
            expected = EXPECTED_FILES[index]
            response = transport(expected.url, record.size_bytes)
            payload = _read_generated_response(
                response,
                expected_url=expected.url,
                expected_size=record.size_bytes,
            )
            if _sha256(payload) != record.sha256:
                raise UG1AcquisitionFailure(
                    "integrity", f"generated payload hash mismatch: {record.repository_path}"
                )
            relative = _safe_relative_path(record.repository_path)
            parent = _mkdir_relative(payload_root, PurePosixPath(*relative.parts[:-1]))
            destination_file = parent / relative.name
            _write_atomic(destination_file, payload)
            input_bytes += len(payload)
            if fault_injector is not None:
                fault_injector(f"after_payload_{index + 1}")
            _, observed_rss = _check_resources(
                started=started,
                clock=clock,
                rss_reader=rss_reader,
                caps=caps,
            )
            peak_rss = max(peak_rss, observed_rss)
        manifest_path = staging / "manifest.v0.json"
        _write_atomic(manifest_path, manifest_bytes)
        if fault_injector is not None:
            fault_injector("before_promotion")
        for record in ordered:
            relative = _safe_relative_path(record.repository_path)
            size, digest = _hash_regular_nofollow(payload_root.joinpath(*relative.parts))
            if size != record.size_bytes or digest != record.sha256:
                raise UG1AcquisitionFailure("integrity", "generated bundle validation failed")
        manifest_size, observed_manifest_sha256 = _hash_regular_nofollow(manifest_path)
        if manifest_size != len(manifest_bytes) or observed_manifest_sha256 != manifest_sha256:
            raise UG1AcquisitionFailure("integrity", "generated manifest validation failed")
        runtime, observed_rss = _check_resources(
            started=started,
            clock=clock,
            rss_reader=rss_reader,
            caps=caps,
        )
        peak_rss = max(peak_rss, observed_rss)
        _rename_noreplace(staging, destination)
        runtime, observed_rss = _check_resources(
            started=started,
            clock=clock,
            rss_reader=rss_reader,
            caps=caps,
        )
        peak_rss = max(peak_rss, observed_rss)
        final_payload_root = destination / "payloads"
        final_manifest_path = destination / "manifest.v0.json"
        output_bytes = payload_bytes + len(manifest_bytes)
        measurements = {
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "cumulative_output_bytes": 2 * output_bytes,
            "runtime_seconds": runtime,
            "peak_process_tree_rss_bytes": peak_rss,
            "transport_calls": len(ordered),
            "network_bytes": 0,
            "real_path_reads": 0,
            "parameter_update_fits": 0,
            "prediction_sets": 0,
            "model_runs": 0,
            "target_deliveries": 0,
            "scoring_events": 0,
            "warnings": list(manifest["warnings"]),
        }
        return GeneratedAcquisitionOutcome(
            status="passed",
            manifest=manifest,
            manifest_bytes=manifest_bytes,
            manifest_sha256=manifest_sha256,
            payload_root=final_payload_root,
            manifest_path=final_manifest_path,
            measurements=measurements,
        )
    except Exception:
        _cleanup_owned_staging(staging)
        raise


def run_generated_qualification_cases() -> dict[str, Any]:
    """Exercise the Stage G acquisition case classes once with generated bytes."""

    inventory, transport = build_generated_fixture(bytes_per_file=256)
    source_hashes = transport.fixture_sha256s()
    dry = run_generated_fixture_acquisition(inventory=inventory, transport=transport)
    if dry.status != "dry_run" or transport.calls:
        raise UG1AcquisitionFailure("dry_run", "dry plan called transport")
    with tempfile.TemporaryDirectory(prefix="neurodecodekit-ug1-acquisition-") as directory:
        root = Path(directory)
        first = run_generated_fixture_acquisition(
            inventory=inventory,
            transport=transport,
            workspace_root=root,
            output_relative="first",
            execute=True,
        )
        if first.status != "passed" or transport.fixture_sha256s() != source_hashes:
            raise UG1AcquisitionFailure("replay", "generated source changed")
        replay_inventory, replay_transport = build_generated_fixture(bytes_per_file=256)
        replay = run_generated_fixture_acquisition(
            inventory=replay_inventory,
            transport=replay_transport,
            workspace_root=root,
            output_relative="replay",
            execute=True,
        )
        if replay.manifest_sha256 != first.manifest_sha256:
            raise UG1AcquisitionFailure("replay", "generated manifests differ")
        refusals = 0
        for mutated in (
            (*inventory[:-1], inventory[0]),
            (
                InventoryRecord(
                    repository_path="S001/S001R11.edf",
                    partition="source_fit_missing",
                    participant="S001",
                    run="11",
                    size_bytes=inventory[0].size_bytes,
                    sha256=inventory[0].sha256,
                    validator=inventory[0].validator,
                ),
                *inventory[1:],
            ),
        ):
            try:
                validate_inventory(mutated)
            except UG1AcquisitionRefusal:
                refusals += 1
        try:
            run_generated_fixture_acquisition(
                inventory=inventory,
                transport=transport,
                workspace_root=root,
                output_relative="first",
                execute=True,
            )
        except UG1AcquisitionRefusal:
            refusals += 1
        redirect_responses = {}
        for index, expected in enumerate(EXPECTED_FILES):
            body = transport._responses[expected.url]
            redirect_responses[expected.url] = GeneratedResponse(
                requested_url=expected.url,
                final_url=("https://example.invalid/redirect" if index == 0 else expected.url),
                body=body if isinstance(body, bytes) else body.body,
                declared_size=inventory[index].size_bytes,
            )
        try:
            run_generated_fixture_acquisition(
                inventory=inventory,
                transport=GeneratedMockTransport(redirect_responses),
                workspace_root=root,
                output_relative="redirect",
                execute=True,
            )
        except UG1AcquisitionFailure:
            refusals += 1
        try:
            run_generated_fixture_acquisition(
                inventory=inventory,
                transport=transport,
                workspace_root=root,
                output_relative="../escape",
                execute=True,
            )
        except UG1AcquisitionRefusal:
            refusals += 1
        symlink = root / "symlink"
        symlink.symlink_to(root / "first", target_is_directory=True)
        try:
            run_generated_fixture_acquisition(
                inventory=inventory,
                transport=transport,
                workspace_root=root,
                output_relative="symlink/child",
                execute=True,
            )
        except UG1AcquisitionRefusal:
            refusals += 1
        original = root / "regular"
        alias = root / "alias"
        original.write_bytes(b"generated")
        os.link(original, alias)
        try:
            _open_regular_nofollow(alias)
        except UG1AcquisitionRefusal:
            refusals += 1
        file_race = root / "file-race.json"

        def create_file_race() -> None:
            file_race.write_bytes(b"race-owned\n")

        try:
            _write_atomic(file_race, b"{}\n", _before_publish=create_file_race)
        except UG1AcquisitionFailure:
            refusals += 1
        if file_race.read_bytes() != b"race-owned\n" or (root / ".file-race.json.part").exists():
            raise UG1AcquisitionFailure("output", "file publication race handling changed")

        def promotion_race(stage: str) -> None:
            if stage == "before_promotion":
                raced = root / "promotion-race"
                raced.mkdir()
                (raced / "owned.txt").write_bytes(b"race-owned\n")

        try:
            run_generated_fixture_acquisition(
                inventory=inventory,
                transport=transport,
                workspace_root=root,
                output_relative="promotion-race",
                execute=True,
                fault_injector=promotion_race,
            )
        except UG1AcquisitionFailure:
            refusals += 1
        if (root / "promotion-race" / "owned.txt").read_bytes() != b"race-owned\n":
            raise UG1AcquisitionFailure("output", "bundle publication race was overwritten")
        if (root / ".promotion-race.tmp").exists():
            raise UG1AcquisitionFailure("cleanup", "bundle race left generated staging")

        def crash(stage: str) -> None:
            if stage == "before_promotion":
                raise UG1AcquisitionFailure("crash", "injected generated crash")

        try:
            run_generated_fixture_acquisition(
                inventory=inventory,
                transport=transport,
                workspace_root=root,
                output_relative="crash",
                execute=True,
                fault_injector=crash,
            )
        except UG1AcquisitionFailure:
            refusals += 1
        if (root / "crash").exists() or (root / ".crash.tmp").exists():
            raise UG1AcquisitionFailure("cleanup", "crash left generated staging")
        try:
            run_generated_fixture_acquisition(
                inventory=inventory,
                transport=transport,
                workspace_root=root,
                output_relative="cap",
                execute=True,
                caps=GeneratedAcquisitionCaps(cumulative_output_bytes=1),
            )
        except UG1AcquisitionRefusal:
            refusals += 1
        if refusals != 11:
            raise UG1AcquisitionFailure("matrix", "generated refusal count differs")
        return {
            "input_bytes": first.measurements["input_bytes"] + replay.measurements["input_bytes"],
            "output_bytes": first.measurements["output_bytes"]
            + replay.measurements["output_bytes"],
            "refusal_cases": refusals,
            "case_classes": [
                "valid_replay_source_immutability",
                "split_overlap_alias_symlink_hardlink_duplicate_forbidden_run_refusal",
                "atomic_crash_destination_traversal_redirect_output_RSS_wall_and_second_invocation_refusal",
            ],
        }
