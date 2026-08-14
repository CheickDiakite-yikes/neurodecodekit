"""Proof-gated MARC2-FW1A private-manifest prefix selection."""

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
import subprocess
import sys
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-FW1A"
GENERATED_ROUTE = "MARC2FWS-G1"
SUCCESS_ROUTE = "MARC2FWS-R1"
FAILURE_ROUTES = tuple(f"MARC2FWS-F0{index}" for index in range(7))

DECISION_RELATIVE_PATH = Path(
    "registries/marc2_freewill_private_selection_authorization_decision.v0.json"
)
DECISION_SHA256 = "8b47f1397e5f32f9856e8cdb1e71f6350827067614ed7c651bb221bf6c6142e8"
GREEN_DECISION_COMMIT = "ad1e4064256f963b2d03daeb27e4a4779b32415f"
GREEN_DECISION_CI_RUN_ID = 31_764_052_451
GREEN_DECISION_BASE_JOB_ID = 94_656_172_494
GREEN_DECISION_OPTIONAL_JOB_ID = 94_656_172_528

REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_freewill_private_selection_authorization_request.v0.json"
)
REQUEST_SHA256 = "2795818b0517bdd66a69e4039c98d3359c0115ef78d5f0be7ff8869511e5987d"
PACKET_RELATIVE_PATH = Path(
    "docs/MARC_2_FREEWILL_PRIVATE_SELECTION_AUTHORIZATION_PACKET.md"
)
PACKET_SHA256 = "94437f2dad9d3d9b9b1c84ca68c9a12848e9dba7e1fcd3f0a902c5e657870f98"
SELECTOR_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_freewill_prefix_selection.py"
)
SELECTOR_SHA256 = "86fa30fbd1caed735f0fb2e627144482a2bb8e033567bb3794e3f05508005c97"
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_freewill_private_selection_implementation.v0.json"
)

PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
PRIVATE_SOURCE_BYTES = 418_755
PRIVATE_SOURCE_MODE = 0o600
PRIVATE_SOURCE_SHA256 = "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
PRIVATE_SOURCE_SCHEMA = "neurodecodekit.marc1_central_directory_private_manifest"
PRIVATE_SOURCE_ENTRIES = 1_227
FREEWILL_RECORD_ID = 28_632_599
FREEWILL_VERSION = 1
FREEWILL_FILE_ID = 57_518_986
FREEWILL_ARCHIVE_BYTES = 13_591_548_048
FREEWILL_ARCHIVE_MD5 = "3b7c3039c5c9fb6abf1429a830301711"

OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_freewill_prefix/live_selection_v0"
)
OUTPUT_PARENT_RELATIVE_PATH = OUTPUT_ROOT_RELATIVE_PATH.parent
CONSUMED_MARKER_NAME = "execution_consumed.v0.json"
PRIVATE_SELECTION_NAME = "marc2_freewill_private_selection.private.v0.json"
AGGREGATE_REPORT_NAME = "marc2_freewill_private_selection_result.v0.json"

REPORT_SCHEMA_NAME = "neurodecodekit.marc2_freewill_private_selection_result"
PRIVATE_SELECTION_SCHEMA_NAME = (
    "neurodecodekit.marc2_freewill_private_selection_manifest"
)
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_freewill_private_selection_implementation"
)

MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_LOAD_PER_LOGICAL_CPU = 1.0
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2
THREAD_ENV_KEYS = selector.THREAD_ENV_KEYS

HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
WRAPPER_MUTATIONS = (
    "implementation_proof_commit_mismatch",
    "implementation_proof_CI_or_job_mismatch",
    "dirty_tracked_worktree_or_HEAD_mismatch",
    "output_root_differs",
    "output_root_exists",
    "symlink_output_parent_or_destination",
    "insufficient_free_disk",
    "load_worker_thread_runtime_or_RSS_preflight_failure",
    "retained_path_component_symlink",
    "retained_final_path_symlink_or_non_regular_file",
    "retained_owner_mode_mismatch",
    "retained_size_mismatch",
    "retained_SHA256_mismatch",
    "no_follow_open_fstat_identity_race",
    "strict_JSON_duplicate_encoding_control_or_schema_failure",
    "private_aggregate_field_leak_or_schema_confusion",
    "output_cap_mode_overwrite_atomic_write_or_cleanup_failure",
    "retry_rerun_resume_old_root_network_archive_or_payload_attempt",
)

PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "proof_posture",
        "green_evidence",
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
        "crc32",
        "local_header_offset",
        "member_name",
        "private_path",
        "private_rows",
        "raw_body",
        "raw_header",
        "source_body",
        "source_path",
    }
)
FORBIDDEN_PRIVATE_KEY_FRAGMENTS = (
    "target",
    "label",
    "response",
    "sentence",
    "trial",
    "quality",
    "channel",
    "onset",
)


class PrivateSelectionRefusal(RuntimeError):
    """Fail closed with one stable aggregate-safe route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC2-FW1A route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class GreenImplementationEvidence:
    """Externally observed green proof for the exact implementation commit."""

    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    implementation_registry_sha256: str
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class PrivateSelectionOutcome:
    """One generated qualification or registered private selection outcome."""

    report: Mapping[str, Any]
    report_path: Path
    private_selection_path: Path | None
    consumed_marker_path: Path | None
    runtime_seconds: float
    peak_rss_bytes: int
    input_bytes: int
    output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).parents[3]


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
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_fd_bounded(
    descriptor: int,
    maximum_bytes: int,
    *,
    reader: Callable[[int, int], bytes] = os.read,
) -> bytes:
    payload = bytearray()
    while len(payload) <= maximum_bytes:
        remaining = maximum_bytes + 1 - len(payload)
        chunk = reader(descriptor, min(64 * 1024, remaining))
        if not chunk:
            break
        if not isinstance(chunk, (bytes, bytearray)):
            raise OSError("bounded reader returned non-bytes")
        payload.extend(chunk)
    return bytes(payload)


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("nonfinite JSON value")


def _strict_json(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    text = payload.decode("utf-8", errors="strict")
    value = json.loads(
        text,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root differs")
    return value


def _read_tracked_json(
    path: Path,
    *,
    expected_sha256: str,
    maximum_bytes: int = MAX_COMBINED_OUTPUT_BYTES,
) -> dict[str, Any]:
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "tracked proof unavailable") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "tracked proof type differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            payload = _read_fd_bounded(descriptor, maximum_bytes)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "tracked proof open failed") from exc
    if len(payload) > maximum_bytes or _sha256_bytes(payload) != expected_sha256:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "tracked proof identity differs")
    try:
        return _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "tracked proof JSON differs") from exc


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact authorization decision that passed both remote jobs."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _read_tracked_json(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=DECISION_SHA256,
    )
    request = _read_tracked_json(
        root / REQUEST_RELATIVE_PATH,
        expected_sha256=REQUEST_SHA256,
    )
    authorization = decision.get("authorization", {})
    source = decision.get("registered_private_source", {})
    execution = decision.get("future_private_execution", {})
    proof = decision.get("green_request", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc2_freewill_private_selection_authorization_decision"
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "d0a6eaa391b12f04da35bf277f6409f2750d40df"
        or decision.get("user_authorization", {}).get("actual_message_verbatim")
        != "continue"
        or proof.get("CI_run_id") != 31_679_428_199
        or proof.get("base_python_job_id") != 94_381_244_828
        or proof.get("optional_neuro_job_id") != 94_381_244_902
        or proof.get("both_required_jobs_green") is not True
        or authorization.get("wrapper_implementation_after_decision_green") is not True
        or authorization.get("one_private_manifest_read_after_wrapper_green") is not True
        or authorization.get("payload_acquisition_or_download_authorized_now") is not False
        or source.get("path") != str(PRIVATE_SOURCE_RELATIVE_PATH)
        or source.get("bytes") != PRIVATE_SOURCE_BYTES
        or source.get("mode") != "0600"
        or source.get("sha256") != PRIVATE_SOURCE_SHA256
        or source.get("entries") != PRIVATE_SOURCE_ENTRIES
        or execution.get("output_root") != str(OUTPUT_ROOT_RELATIVE_PATH)
        or execution.get("execution_limit") != 1
        or execution.get("retry_rerun_resume_repair_or_fallback_limit") != 0
        or execution.get("success_authorizes_archive_member_or_payload") is not False
        or request.get("authorized") is not False
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "authorization proof differs")
    if (
        _sha256_file(root / PACKET_RELATIVE_PATH) != PACKET_SHA256
        or _sha256_file(root / SELECTOR_RELATIVE_PATH) != SELECTOR_SHA256
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "frozen upstream differs")
    selector.load_registered_contract(root)
    return decision


def load_implementation_record(
    repo_root: str | Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    """Load the generated-qualified wrapper implementation record."""

    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "implementation hash malformed")
    root = Path(repo_root)
    record = _read_tracked_json(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256=expected_sha256,
    )
    qualification = record.get("generated_qualification", {})
    execution = record.get("execution_state", {})
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("lane_id") != LANE_ID
        or record.get("status")
        != "generated_mock_wrapper_qualified_requires_remote_green_before_private_selection"
        or record.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or record.get("green_decision", {}).get("CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or qualification.get("all_gates_passed") is not True
        or qualification.get("inherited_selector_mutations_passed") != 40
        or qualification.get("wrapper_mutations_passed") != 18
        or tuple(qualification.get("wrapper_mutation_routes", {}))
        != WRAPPER_MUTATIONS
        or any(
            route not in FAILURE_ROUTES
            for route in qualification.get("wrapper_mutation_routes", {}).values()
        )
        or execution.get("registered_private_execution_consumed") is not False
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "implementation record differs")
    for binding in record.get("tracked_file_hashes", ()):
        relative = str(binding.get("path", ""))
        digest = str(binding.get("sha256", ""))
        if (
            not relative
            or relative.startswith(("/", "~"))
            or ".." in Path(relative).parts
            or HEX64_RE.fullmatch(digest) is None
            or _sha256_file(root / relative) != digest
        ):
            raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "implementation file differs")
    return record


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _validate_evidence_shape(evidence: GreenImplementationEvidence) -> None:
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or HEX64_RE.fullmatch(evidence.implementation_registry_sha256) is None
        or min(
            evidence.implementation_ci_run_id,
            evidence.implementation_base_job_id,
            evidence.implementation_optional_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "green proof malformed")


def _verify_mock_git_snapshot(*, head_matches: bool, clean: bool, ancestor: bool) -> None:
    if not head_matches or not clean or not ancestor:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[0], "tracked Git proof differs")


def verify_green_implementation(
    repo_root: str | Path,
    evidence: GreenImplementationEvidence,
) -> dict[str, Any]:
    """Require a clean exact HEAD descending from the green decision."""

    _validate_evidence_shape(evidence)
    root = Path(repo_root)
    head = _git(root, "rev-parse", "HEAD")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    ancestor = _git(root, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, "HEAD")
    _verify_mock_git_snapshot(
        head_matches=not head.returncode
        and head.stdout.strip() == evidence.implementation_commit,
        clean=not clean.returncode and not clean.stdout.strip(),
        ancestor=not ancestor.returncode,
    )
    load_green_decision(root)
    return load_implementation_record(
        root,
        expected_sha256=evidence.implementation_registry_sha256,
    )


def preconsumption_machine_gate(
    root: str | Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Measure computer-protection conditions before consumption."""

    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "thread environment differs")
    try:
        free_bytes = int(disk_usage_reader(Path(root)).free)
        logical_cpus = cpu_count_reader()
        load_values = loadavg_reader()
        peak_rss = int(rss_reader())
    except Exception as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "machine metric unavailable") from exc
    if logical_cpus is None or logical_cpus <= 0 or not load_values:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "CPU or load unavailable")
    one_minute_load = float(load_values[0])
    normalized_load = one_minute_load / logical_cpus
    if (
        free_bytes < MINIMUM_FREE_DISK_BYTES
        or not math.isfinite(one_minute_load)
        or one_minute_load < 0
        or normalized_load > MAX_LOAD_PER_LOGICAL_CPU
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "machine resource cap failed")
    return {
        "passed_before_consumed_marker": True,
        "free_disk_bytes": free_bytes,
        "logical_CPUs": logical_cpus,
        "one_minute_load": one_minute_load,
        "one_minute_load_per_logical_CPU": normalized_load,
        "peak_RSS_bytes_before_consumption": peak_rss,
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
    }


def _assert_registered_output_root(root: Path, output_root: Path) -> None:
    if output_root != root / OUTPUT_ROOT_RELATIVE_PATH:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "output root differs")


def _assert_output_absent(output_root: Path) -> None:
    try:
        observed = os.lstat(output_root)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "output root unavailable") from exc
    if observed:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "output root already exists")


def _assert_non_symlink_parent(path: Path) -> None:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "path parent unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "path parent type differs")


def _assert_source_components(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "private source path differs")
    current = root
    for component in relative.parts[:-1]:
        current = current / component
        _assert_non_symlink_parent(current)
    return current / relative.parts[-1]


def _preflight_private_source(path: Path, *, expected_bytes: int) -> os.stat_result:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "private source unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "private source type differs")
    if observed.st_uid != os.getuid() or stat.S_IMODE(observed.st_mode) != PRIVATE_SOURCE_MODE:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "private source owner or mode differs")
    if observed.st_size != expected_bytes:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source size differs")
    return observed


def _base_access_counters() -> dict[str, int]:
    return {
        "registered_private_path_component_checks": 0,
        "registered_private_final_lstats": 0,
        "private_manifest_content_opens": 0,
        "private_manifest_body_reads": 0,
        "private_manifest_bytes": 0,
        "private_manifest_hashes": 0,
        "private_manifest_parses": 0,
        "real_participant_selections": 0,
        "real_member_selections": 0,
        "consumed_markers": 0,
        "private_selection_manifests": 0,
        "aggregate_reports": 0,
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
    }


def read_locked_private_manifest(
    path: Path,
    *,
    expected_bytes: int,
    expected_sha256: str,
    counters: dict[str, int] | None,
    lstat_reader: Callable[[Path], Any] = os.lstat,
    opener: Callable[[Path, int], int] = os.open,
    fstat_reader: Callable[[int], Any] = os.fstat,
    body_reader: Callable[[int, int], bytes] = os.read,
    closer: Callable[[int], None] = os.close,
) -> tuple[dict[str, Any], bytes]:
    """Perform one no-follow open, sequential read, hash, and strict parse."""

    if expected_bytes <= 0 or HEX64_RE.fullmatch(expected_sha256) is None:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source contract differs")
    try:
        before = lstat_reader(path)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source unavailable") from exc
    if counters is not None:
        counters["registered_private_final_lstats"] += 1
    if (
        stat.S_ISLNK(before.st_mode)
        or not stat.S_ISREG(before.st_mode)
        or before.st_uid != os.getuid()
        or stat.S_IMODE(before.st_mode) != PRIVATE_SOURCE_MODE
        or before.st_size != expected_bytes
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source identity differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = opener(path, flags)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private no-follow open failed") from exc
    if counters is not None:
        counters["private_manifest_content_opens"] += 1
    try:
        after = fstat_reader(descriptor)
        if (
            after.st_dev != before.st_dev
            or after.st_ino != before.st_ino
            or after.st_uid != before.st_uid
            or not stat.S_ISREG(after.st_mode)
            or stat.S_IMODE(after.st_mode) != PRIVATE_SOURCE_MODE
            or after.st_size != expected_bytes
        ):
            raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source changed during open")
        payload = _read_fd_bounded(
            descriptor,
            expected_bytes,
            reader=body_reader,
        )
    finally:
        closer(descriptor)
    if counters is not None:
        counters["private_manifest_body_reads"] += 1
        counters["private_manifest_bytes"] += len(payload)
    if len(payload) != expected_bytes:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source byte count differs")
    digest = _sha256_bytes(payload)
    if counters is not None:
        counters["private_manifest_hashes"] += 1
    if digest != expected_sha256:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source SHA-256 differs")
    try:
        manifest = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "private source JSON differs") from exc
    if counters is not None:
        counters["private_manifest_parses"] += 1
    return manifest, payload


def build_generated_live_manifest(*, row_order: str = "canonical") -> dict[str, Any]:
    """Build a generated body with the exact live source identity."""

    manifest = selector.build_generated_manifest(row_order=row_order)
    manifest["proof_posture"] = "live_archive_private_central_directory_metadata_only"
    manifest["source_identity"] = {
        "provider": "Figshare",
        "record_id": FREEWILL_RECORD_ID,
        "version": FREEWILL_VERSION,
        "file_id": FREEWILL_FILE_ID,
        "declared_archive_bytes": FREEWILL_ARCHIVE_BYTES,
        "registered_MD5": FREEWILL_ARCHIVE_MD5,
        "whole_archive_downloaded": False,
        "member_payload_opened": False,
    }
    return manifest


def _canonical_live_manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
    value = copy.deepcopy(dict(manifest))
    entries = value.get("entries")
    if isinstance(entries, list):
        value["entries"] = sorted(
            entries,
            key=lambda row: str(row.get("member_name", ""))
            if isinstance(row, dict)
            else str(row),
        )
    return _canonical_json_bytes(value)


def _validate_live_source_identity(manifest: Mapping[str, Any]) -> None:
    source = manifest.get("source_identity") if isinstance(manifest, dict) else None
    transport = (
        manifest.get("transport_body_sha256") if isinstance(manifest, dict) else None
    )
    expected_top = {
        "schema_name",
        "schema_version",
        "proof_posture",
        "source_identity",
        "transport_body_sha256",
        "entries",
    }
    if (
        not isinstance(manifest, dict)
        or set(manifest) != expected_top
        or manifest.get("schema_name") != PRIVATE_SOURCE_SCHEMA
        or manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("proof_posture")
        != "live_archive_private_central_directory_metadata_only"
        or source
        != {
            "provider": "Figshare",
            "record_id": FREEWILL_RECORD_ID,
            "version": FREEWILL_VERSION,
            "file_id": FREEWILL_FILE_ID,
            "declared_archive_bytes": FREEWILL_ARCHIVE_BYTES,
            "registered_MD5": FREEWILL_ARCHIVE_MD5,
            "whole_archive_downloaded": False,
            "member_payload_opened": False,
        }
        or not isinstance(transport, dict)
        or set(transport) != {"metadata", "tail", "central_directory"}
        or any(
            not isinstance(value, str) or HEX64_RE.fullmatch(value) is None
            for value in transport.values()
        )
        or not isinstance(manifest.get("entries"), list)
        or len(manifest["entries"]) != PRIVATE_SOURCE_ENTRIES
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[2], "live source identity differs")


def _map_selector_route(route: str) -> str:
    return {
        selector.REFUSAL_IDS[0]: FAILURE_ROUTES[0],
        selector.REFUSAL_IDS[1]: FAILURE_ROUTES[2],
        selector.REFUSAL_IDS[2]: FAILURE_ROUTES[3],
        selector.REFUSAL_IDS[3]: FAILURE_ROUTES[4],
        selector.REFUSAL_IDS[4]: FAILURE_ROUTES[5],
        selector.REFUSAL_IDS[5]: FAILURE_ROUTES[6],
    }[route]


def _walk_private_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = key.lower()
            if any(fragment in lowered for fragment in FORBIDDEN_PRIVATE_KEY_FRAGMENTS):
                raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "forbidden private field")
            _walk_private_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_private_keys(nested)


def select_live_prefix(
    manifest: Mapping[str, Any],
    *,
    source_file_sha256: str,
) -> selector.SelectionResult:
    """Apply the immutable selector to a strictly validated live manifest."""

    _validate_live_source_identity(manifest)
    canonical_source_sha256 = _sha256_bytes(_canonical_live_manifest_bytes(manifest))
    adapted = copy.deepcopy(dict(manifest))
    adapted["proof_posture"] = "generated_fixture_private_metadata_only"
    adapted["source_identity"] = {
        "provider": "generated_fixture",
        "record_id": FREEWILL_RECORD_ID,
        "version": FREEWILL_VERSION,
        "file_id": 0,
        "declared_archive_bytes": FREEWILL_ARCHIVE_BYTES,
        "registered_MD5": "0" * 32,
        "whole_archive_downloaded": False,
        "member_payload_opened": False,
    }
    try:
        selected = selector.select_generated_prefix(adapted)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise PrivateSelectionRefusal(
            _map_selector_route(exc.refusal_id),
            "frozen prefix selector refused",
        ) from exc
    rows: list[dict[str, Any]] = []
    for original in selected.private_manifest["rows"]:
        row = copy.deepcopy(dict(original))
        row["source_id"] = "freewill_23_live_central_directory"
        row["source_hashes"] = {
            "private_source_file_sha256": source_file_sha256,
            "private_source_canonical_sha256": canonical_source_sha256,
            "selector_sha256": SELECTOR_SHA256,
            "contract_sha256": selector.CONTRACT_SHA256,
        }
        rows.append(row)
    selection_identity = {
        "selected_subject_ids": selected.cohort_summary["selected_subject_ids"],
        "selected_subjects": selected.cohort_summary["selected_subjects"],
        "selected_run_bundles": selected.split_summary["selected_run_bundles"],
        "selected_core_members": selected.split_summary["selected_core_members"],
        "selected_reservation_bytes": selected.byte_summary[
            "selected_reservation_bytes"
        ],
        "source_file_sha256": source_file_sha256,
    }
    private_manifest = {
        "schema_name": PRIVATE_SELECTION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "proof_posture": "target_free_private_selection_no_payload_or_scientific_value",
        "decision_sha256": DECISION_SHA256,
        "selector_sha256": SELECTOR_SHA256,
        "contract_sha256": selector.CONTRACT_SHA256,
        "source_file_sha256": source_file_sha256,
        "source_canonical_sha256": canonical_source_sha256,
        "selected_subject_ids": list(selected.cohort_summary["selected_subject_ids"]),
        "rows": rows,
    }
    _walk_private_keys(private_manifest)
    return selector.SelectionResult(
        private_manifest=private_manifest,
        cohort_summary=dict(selected.cohort_summary),
        split_summary=dict(selected.split_summary),
        byte_summary=dict(selected.byte_summary),
        selection_hashes={
            "private_source_file_sha256": source_file_sha256,
            "private_source_canonical_sha256": canonical_source_sha256,
            "selection_identity_sha256": _sha256_bytes(
                _canonical_json_bytes(selection_identity)
            ),
            "private_selection_manifest_sha256": _sha256_bytes(
                _canonical_json_bytes(private_manifest)
            ),
        },
    )


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.lower() in FORBIDDEN_PUBLIC_KEYS:
                raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "private field leaked")
            _walk_public(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested)
    elif isinstance(value, str):
        if ".codex_work" in value or "_eeg." in value or "_events.tsv" in value:
            raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "private value leaked")


def _bounded_output_bytes(*payloads: bytes) -> int:
    total = sum(len(payload) for payload in payloads)
    if total > MAX_COMBINED_OUTPUT_BYTES:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "combined output exceeds cap")
    return total


def _forbidden_operation() -> None:
    raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "forbidden operation attempted")


def _expect_refusal(
    operation: Callable[[], Any],
    *,
    expected_route: str,
) -> str:
    try:
        operation()
    except PrivateSelectionRefusal as exc:
        if exc.route != expected_route:
            raise AssertionError("wrapper mutation routed incorrectly") from exc
        return exc.route
    raise AssertionError("wrapper mutation did not refuse")


def run_wrapper_mutations() -> dict[str, str]:
    """Exercise all 18 wrapper-specific refusals with generated local facts."""

    results: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="marc2fw1a-mutations-") as temporary:
        root = Path(temporary)
        safe = root / "safe"
        safe.mkdir()
        source = safe / "source.json"
        payload = b"{}\n"
        source.write_bytes(payload)
        source.chmod(0o600)
        wrong_output = root / "wrong"
        existing_output = root / "existing"
        existing_output.mkdir()
        symlink_parent = root / "symlink-parent"
        symlink_parent.symlink_to(safe, target_is_directory=True)
        component_root = root / "components"
        component_root.mkdir()
        (component_root / "link").symlink_to(safe, target_is_directory=True)
        final_link = safe / "final-link"
        final_link.symlink_to(source)

        good_evidence = GreenImplementationEvidence(
            implementation_commit="1" * 40,
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="2" * 64,
        )
        results[WRAPPER_MUTATIONS[0]] = _expect_refusal(
            lambda: _validate_evidence_shape(
                GreenImplementationEvidence(
                    implementation_commit="bad",
                    implementation_ci_run_id=1,
                    implementation_base_job_id=2,
                    implementation_optional_job_id=3,
                    implementation_registry_sha256="2" * 64,
                )
            ),
            expected_route=FAILURE_ROUTES[0],
        )
        results[WRAPPER_MUTATIONS[1]] = _expect_refusal(
            lambda: _validate_evidence_shape(
                GreenImplementationEvidence(
                    implementation_commit=good_evidence.implementation_commit,
                    implementation_ci_run_id=0,
                    implementation_base_job_id=2,
                    implementation_optional_job_id=3,
                    implementation_registry_sha256="2" * 64,
                )
            ),
            expected_route=FAILURE_ROUTES[0],
        )
        results[WRAPPER_MUTATIONS[2]] = _expect_refusal(
            lambda: _verify_mock_git_snapshot(
                head_matches=True, clean=False, ancestor=True
            ),
            expected_route=FAILURE_ROUTES[0],
        )
        results[WRAPPER_MUTATIONS[3]] = _expect_refusal(
            lambda: _assert_registered_output_root(root, wrong_output),
            expected_route=FAILURE_ROUTES[1],
        )
        results[WRAPPER_MUTATIONS[4]] = _expect_refusal(
            lambda: _assert_output_absent(existing_output),
            expected_route=FAILURE_ROUTES[1],
        )
        results[WRAPPER_MUTATIONS[5]] = _expect_refusal(
            lambda: _assert_non_symlink_parent(symlink_parent),
            expected_route=FAILURE_ROUTES[1],
        )

        class _Disk:
            free = MINIMUM_FREE_DISK_BYTES - 1

        results[WRAPPER_MUTATIONS[6]] = _expect_refusal(
            lambda: preconsumption_machine_gate(
                root,
                environ={key: "1" for key in THREAD_ENV_KEYS},
                disk_usage_reader=lambda _path: _Disk(),
                cpu_count_reader=lambda: 8,
                loadavg_reader=lambda: (0.0, 0.0, 0.0),
                rss_reader=lambda: 1,
            ),
            expected_route=FAILURE_ROUTES[1],
        )
        results[WRAPPER_MUTATIONS[7]] = _expect_refusal(
            lambda: preconsumption_machine_gate(
                root,
                environ={key: "2" for key in THREAD_ENV_KEYS},
            ),
            expected_route=FAILURE_ROUTES[1],
        )
        results[WRAPPER_MUTATIONS[8]] = _expect_refusal(
            lambda: _assert_source_components(component_root, Path("link/source.json")),
            expected_route=FAILURE_ROUTES[1],
        )
        results[WRAPPER_MUTATIONS[9]] = _expect_refusal(
            lambda: _preflight_private_source(final_link, expected_bytes=len(payload)),
            expected_route=FAILURE_ROUTES[1],
        )
        source.chmod(0o644)
        results[WRAPPER_MUTATIONS[10]] = _expect_refusal(
            lambda: _preflight_private_source(source, expected_bytes=len(payload)),
            expected_route=FAILURE_ROUTES[1],
        )
        source.chmod(0o600)
        results[WRAPPER_MUTATIONS[11]] = _expect_refusal(
            lambda: _preflight_private_source(source, expected_bytes=len(payload) + 1),
            expected_route=FAILURE_ROUTES[2],
        )
        results[WRAPPER_MUTATIONS[12]] = _expect_refusal(
            lambda: read_locked_private_manifest(
                source,
                expected_bytes=len(payload),
                expected_sha256="0" * 64,
                counters=None,
            ),
            expected_route=FAILURE_ROUTES[2],
        )

        before = os.lstat(source)

        class _Changed:
            st_dev = before.st_dev
            st_ino = before.st_ino + 1
            st_uid = before.st_uid
            st_mode = before.st_mode
            st_size = before.st_size

        results[WRAPPER_MUTATIONS[13]] = _expect_refusal(
            lambda: read_locked_private_manifest(
                source,
                expected_bytes=len(payload),
                expected_sha256=_sha256_bytes(payload),
                counters=None,
                fstat_reader=lambda _descriptor: _Changed(),
            ),
            expected_route=FAILURE_ROUTES[2],
        )
        try:
            _strict_json(b'{"x":1,"x":2}\n')
        except ValueError:
            results[WRAPPER_MUTATIONS[14]] = FAILURE_ROUTES[2]
        else:
            raise AssertionError("strict JSON mutation did not refuse")
        results[WRAPPER_MUTATIONS[15]] = _expect_refusal(
            lambda: _walk_public({"member_name": "private"}),
            expected_route=FAILURE_ROUTES[6],
        )
        results[WRAPPER_MUTATIONS[16]] = _expect_refusal(
            lambda: _bounded_output_bytes(b"x" * (MAX_COMBINED_OUTPUT_BYTES + 1)),
            expected_route=FAILURE_ROUTES[6],
        )
        results[WRAPPER_MUTATIONS[17]] = _expect_refusal(
            _forbidden_operation,
            expected_route=FAILURE_ROUTES[6],
        )
    if tuple(results) != WRAPPER_MUTATIONS:
        raise AssertionError("wrapper mutation order differs")
    return results


def _generated_access_counters() -> dict[str, int]:
    return _base_access_counters()


def _green_evidence(
    evidence: GreenImplementationEvidence | None,
    implementation_registry_sha256: str | None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "decision_commit": GREEN_DECISION_COMMIT,
        "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
        "decision_base_job_id": GREEN_DECISION_BASE_JOB_ID,
        "decision_optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
        "decision_registry_sha256": DECISION_SHA256,
        "both_decision_jobs_green": True,
    }
    if evidence is None:
        value.update(
            {
                "implementation_commit": "uncommitted_generated_qualification",
                "implementation_CI_run_id": None,
                "implementation_base_job_id": None,
                "implementation_optional_neuro_job_id": None,
                "implementation_registry_sha256": implementation_registry_sha256,
                "both_implementation_jobs_green": False,
            }
        )
    else:
        value.update(
            {
                "implementation_commit": evidence.implementation_commit,
                "implementation_CI_run_id": evidence.implementation_ci_run_id,
                "implementation_base_job_id": evidence.implementation_base_job_id,
                "implementation_optional_neuro_job_id": (
                    evidence.implementation_optional_job_id
                ),
                "implementation_registry_sha256": (
                    evidence.implementation_registry_sha256
                ),
                "both_implementation_jobs_green": True,
            }
        )
    return value


def _build_report(
    selection: selector.SelectionResult,
    *,
    generated: bool,
    input_bytes: int,
    output_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
    access_counters: Mapping[str, int],
    wrapper_mutations: Mapping[str, str] | None,
    inherited_mutations: Mapping[str, str] | None,
    machine_gate: Mapping[str, Any] | None,
    evidence: GreenImplementationEvidence | None,
    implementation_registry_sha256: str | None,
) -> dict[str, Any]:
    selected_subjects = int(selection.cohort_summary["selected_subjects"])
    selected_members = int(selection.split_summary["selected_core_members"])
    return {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": (
            "passed_generated_mock_private_selection_wrapper_qualification"
            if generated
            else "passed_registered_target_free_private_selection"
        ),
        "proof_posture": (
            "generated_manifest_and_mocked_filesystem_only_no_scientific_value"
            if generated
            else "private_ZIP_directory_metadata_only_no_archive_member_or_scientific_value"
        ),
        "green_evidence": _green_evidence(evidence, implementation_registry_sha256),
        "cohort_summary": dict(selection.cohort_summary),
        "split_summary": dict(selection.split_summary),
        "byte_summary": dict(selection.byte_summary),
        "selection_hashes": dict(selection.selection_hashes),
        "measurements": {
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "selected_participants": selected_subjects,
            "selected_private_rows": selected_members,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "machine_gate": dict(machine_gate) if machine_gate is not None else None,
        },
        "mutation_summary": {
            "inherited_required": 40,
            "inherited_passed": len(inherited_mutations or {}),
            "wrapper_required": 18,
            "wrapper_passed": len(wrapper_mutations or {}),
            "wrapper_names": list(WRAPPER_MUTATIONS),
            "wrapper_route_counts": dict(
                sorted(Counter((wrapper_mutations or {}).values()).items())
            ),
        },
        "access_counters": dict(access_counters),
        "acceptance_gates": {
            "green_decision_and_frozen_artifact_identity": True,
            "generated_or_exact_live_source_schema": True,
            "immutable_19_subject_rank_and_session_split": True,
            "maximal_contiguous_prefix_under_8_GiB": True,
            "target_quality_outcome_and_content_free_selection": True,
            "all_40_inherited_selector_refusals": True,
            "all_18_wrapper_refusals": True,
            "proof_disabled_execute_until_remote_green": True,
            "one_no_follow_private_open_only_when_live": True,
            "private_and_aggregate_output_separation": True,
            "zero_archive_local_header_member_or_payload_access": True,
            "zero_signal_event_target_model_prediction_or_score_access": True,
            "runtime_RSS_output_disk_and_one_thread_caps": True,
            "deterministic_selection_and_hashes": True,
            "claim_boundary_preserved": True,
        },
        "route": GENERATED_ROUTE if generated else SUCCESS_ROUTE,
        "warnings": [
            (
                "All source rows are generated and no registered private path was accessed."
                if generated
                else "Only the exact private central-directory manifest was read once."
            ),
            "Declared ZIP sizes CRCs and offsets do not verify a local header or member payload.",
            "No signal event target quality model prediction or score was accessed.",
            "The selected reservation is an acquisition ceiling, not acquired payload bytes.",
            "End-to-end neural decoding latency was not measured.",
        ],
        "unavailable_fields": [
            "archive local-header and member payload integrity",
            "EEG channels geometry samples events targets quality and movement onsets",
            "neural features predictions scores and conditional information",
            "language decoding thought-to-text performance and latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A proof-gated wrapper converts one exact private ZIP-directory manifest "
                "into a deterministic storage-bounded target-free selection."
            ),
            "scientific_claim_not_established": (
                "Private ZIP-directory metadata contain no neural signal prediction or "
                "score and establish no neural effect decoding or thought-to-text result."
            ),
        },
    }


def _build_failure_report(
    *,
    refusal: PrivateSelectionRefusal,
    stage: str,
    evidence: GreenImplementationEvidence,
    machine_gate: Mapping[str, Any],
    access_counters: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    selected_subjects = int(access_counters.get("real_participant_selections", 0))
    selected_members = int(access_counters.get("real_member_selections", 0))
    resource_gate = (
        runtime_seconds <= MAX_RUNTIME_SECONDS
        and peak_rss_bytes <= MAX_PEAK_RSS_BYTES
    )
    return {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_failed_registered_private_selection",
        "proof_posture": "aggregate_failure_after_consumed_marker_no_retry_or_rerun",
        "green_evidence": _green_evidence(
            evidence,
            evidence.implementation_registry_sha256,
        ),
        "cohort_summary": {
            "selected_subjects": selected_subjects,
            "selected_subject_ids": [],
            "identities_published": False,
        },
        "split_summary": {
            "selected_run_bundles": selected_members // 4,
            "selected_core_members": selected_members,
            "split_available": False,
        },
        "byte_summary": {
            "selected_reservation_bytes": 0,
            "reservation_cap_bytes": selector.RESERVATION_CAP_BYTES,
            "reservation_available": False,
        },
        "selection_hashes": {"available": False},
        "measurements": {
            "input_bytes": int(access_counters.get("private_manifest_bytes", 0)),
            "output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "selected_participants": selected_subjects,
            "selected_private_rows": selected_members,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "failure_stage": stage,
            "failure_reason_published": False,
            "machine_gate": dict(machine_gate),
        },
        "mutation_summary": {
            "inherited_required": 40,
            "inherited_passed": 40,
            "wrapper_required": 18,
            "wrapper_passed": 18,
            "wrapper_names": list(WRAPPER_MUTATIONS),
            "wrapper_route_counts": {},
        },
        "access_counters": dict(access_counters),
        "acceptance_gates": {
            "green_decision_and_frozen_artifact_identity": True,
            "generated_or_exact_live_source_schema": False,
            "immutable_19_subject_rank_and_session_split": True,
            "maximal_contiguous_prefix_under_8_GiB": False,
            "target_quality_outcome_and_content_free_selection": True,
            "all_40_inherited_selector_refusals": True,
            "all_18_wrapper_refusals": True,
            "proof_disabled_execute_until_remote_green": True,
            "one_no_follow_private_open_only_when_live": (
                access_counters.get("private_manifest_content_opens", 0) <= 1
            ),
            "private_and_aggregate_output_separation": True,
            "zero_archive_local_header_member_or_payload_access": True,
            "zero_signal_event_target_model_prediction_or_score_access": True,
            "runtime_RSS_output_disk_and_one_thread_caps": resource_gate,
            "deterministic_selection_and_hashes": False,
            "claim_boundary_preserved": True,
        },
        "route": refusal.route,
        "warnings": [
            "The one registered invocation is consumed and cannot be retried or resumed.",
            "The aggregate route records only a failure class and stage; no private failure detail is published.",
            "No archive member signal event target model prediction or score was accessed.",
        ],
        "unavailable_fields": [
            "completed target-free selection and selected identity hashes",
            "archive local-header and member payload integrity",
            "EEG channels geometry samples events targets quality and movement onsets",
            "neural features predictions scores and conditional information",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "The one-shot wrapper failed closed and retained an aggregate consumed result."
            ),
            "scientific_claim_not_established": (
                "A metadata selection failure establishes no neural effect decoding or thought-to-text result."
            ),
        },
    }


def validate_public_report(
    report: Mapping[str, Any],
    *,
    allow_incomplete_measurements: bool = False,
) -> None:
    """Validate an aggregate report without accepting a private schema."""

    if set(report) != PUBLIC_REPORT_FIELDS:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "public fields differ")
    route = report.get("route")
    generated = route == GENERATED_ROUTE
    consumed_failure = route in FAILURE_ROUTES
    expected_status = (
        "passed_generated_mock_private_selection_wrapper_qualification"
        if generated
        else (
            "consumed_failed_registered_private_selection"
            if consumed_failure
            else "passed_registered_target_free_private_selection"
        )
    )
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or route not in {GENERATED_ROUTE, SUCCESS_ROUTE, *FAILURE_ROUTES}
        or report.get("status") != expected_status
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "public identity differs")
    _walk_public(report)
    gates = report.get("acceptance_gates")
    counters = report.get("access_counters")
    mutations = report.get("mutation_summary")
    measurements = report.get("measurements")
    if not isinstance(gates, dict) or len(gates) != 15:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "acceptance gate differs")
    required_safety_gates = (
        "green_decision_and_frozen_artifact_identity",
        "target_quality_outcome_and_content_free_selection",
        "proof_disabled_execute_until_remote_green",
        "one_no_follow_private_open_only_when_live",
        "private_and_aggregate_output_separation",
        "zero_archive_local_header_member_or_payload_access",
        "zero_signal_event_target_model_prediction_or_score_access",
        "claim_boundary_preserved",
    )
    if consumed_failure:
        if any(gates.get(key) is not True for key in required_safety_gates):
            raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "failure safety gate differs")
    elif not all(gates.values()):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "acceptance gate differs")
    if not isinstance(counters, dict):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "access counters unavailable")
    forbidden_counter_keys = (
        "network_requests",
        "network_bytes",
        "archive_local_header_or_member_payload_reads",
        "signal_sample_reads",
        "event_target_label_quality_onset_or_channel_reads",
        "real_derivative_rows",
        "training_or_parameter_update_fits",
        "model_inference_or_prediction_sets",
        "prediction_freezes_target_deliveries_or_scores",
        "provider_or_language_model_calls",
        "hardware_operations",
        "old_consumed_root_operations",
        "retries_reruns_or_resumes",
        "scientific_claim_upgrades",
    )
    if any(counters.get(key) for key in forbidden_counter_keys):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "forbidden counter is nonzero")
    if not isinstance(mutations, dict):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "mutation summary unavailable")
    if generated and (
        mutations.get("inherited_passed") != 40
        or mutations.get("wrapper_passed") != 18
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "mutation count differs")
    if not isinstance(measurements, dict):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "measurements unavailable")
    if not allow_incomplete_measurements:
        if measurements.get("output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1) > MAX_COMBINED_OUTPUT_BYTES:
            raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "output cap exceeded")
        if measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1) > MAX_RUNTIME_SECONDS:
            raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "runtime cap exceeded")
        if measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1) > MAX_PEAK_RSS_BYTES:
            raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "RSS cap exceeded")


def _assert_generated_destination(destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "generated output exists")
    _assert_non_symlink_parent(destination.parent)


def _write_generated_outputs(
    destination: Path,
    report: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
) -> tuple[Path, Path, int]:
    _assert_generated_destination(destination)
    report_bytes = _canonical_json_bytes(report)
    private_bytes = _canonical_json_bytes(private_manifest)
    total = _bounded_output_bytes(report_bytes, private_bytes)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    try:
        report_path = stage / AGGREGATE_REPORT_NAME
        private_path = stage / PRIVATE_SELECTION_NAME
        report_path.write_bytes(report_bytes)
        private_path.write_bytes(private_bytes)
        private_path.chmod(PRIVATE_SOURCE_MODE)
        os.replace(stage, destination)
    except Exception as exc:
        shutil.rmtree(stage, ignore_errors=True)
        if isinstance(exc, PrivateSelectionRefusal):
            raise
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "generated output failed") from exc
    final_report = destination / AGGREGATE_REPORT_NAME
    final_private = destination / PRIVATE_SELECTION_NAME
    if stat.S_IMODE(os.lstat(final_private).st_mode) != PRIVATE_SOURCE_MODE:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "private output mode differs")
    return final_report, final_private, total


def qualify_generated_mock_wrapper(
    output_dir: str | Path,
    *,
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> PrivateSelectionOutcome:
    """Run one bounded generated/mock wrapper qualification."""

    destination = Path(output_dir)
    _assert_generated_destination(destination)
    start = clock()
    load_green_decision()
    contract = selector.load_registered_contract()
    base = selector.build_generated_manifest(contract=contract)
    inherited = selector.run_required_mutations(base, contract=contract)
    boundaries = selector.exercise_boundary_profiles(contract=contract)
    if len(boundaries) != 4 or not all(item["passed"] for item in boundaries.values()):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[5], "selector boundary differs")
    first_manifest = build_generated_live_manifest()
    replay_manifest = build_generated_live_manifest(row_order="reversed")
    first_bytes = _canonical_json_bytes(first_manifest)
    replay_bytes = _canonical_json_bytes(replay_manifest)
    first = select_live_prefix(
        first_manifest,
        source_file_sha256=_sha256_bytes(
            _canonical_live_manifest_bytes(first_manifest)
        ),
    )
    replay = select_live_prefix(
        replay_manifest,
        source_file_sha256=_sha256_bytes(
            _canonical_live_manifest_bytes(replay_manifest)
        ),
    )
    if first.cohort_summary != replay.cohort_summary:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "cohort replay differs")
    if (
        first.selection_hashes["selection_identity_sha256"]
        != replay.selection_hashes["selection_identity_sha256"]
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "selection replay differs")
    wrapper_mutations = run_wrapper_mutations()
    runtime_seconds = clock() - start
    peak_rss_bytes = rss_probe()
    if runtime_seconds > MAX_RUNTIME_SECONDS or peak_rss_bytes > MAX_PEAK_RSS_BYTES:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "qualification resource cap failed")
    input_bytes = len(first_bytes) + len(replay_bytes)
    counters = _generated_access_counters()
    report = _build_report(
        first,
        generated=True,
        input_bytes=input_bytes,
        output_bytes=0,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        access_counters=counters,
        wrapper_mutations=wrapper_mutations,
        inherited_mutations=inherited,
        machine_gate=None,
        evidence=None,
        implementation_registry_sha256=None,
    )
    validate_public_report(report, allow_incomplete_measurements=True)
    private_bytes = _canonical_json_bytes(first.private_manifest)
    for _ in range(4):
        report_bytes = _canonical_json_bytes(report)
        total = _bounded_output_bytes(report_bytes, private_bytes)
        if report["measurements"]["output_bytes"] == total:
            break
        report["measurements"]["output_bytes"] = total
    else:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "output size did not stabilize")
    validate_public_report(report)
    report_path, private_path, written = _write_generated_outputs(
        destination,
        report,
        first.private_manifest,
    )
    if written != report["measurements"]["output_bytes"]:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "written output differs")
    return PrivateSelectionOutcome(
        report=report,
        report_path=report_path,
        private_selection_path=private_path,
        consumed_marker_path=None,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        input_bytes=input_bytes,
        output_bytes=written,
    )


def _write_exclusive(path: Path, payload: bytes, *, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            written = os.write(descriptor, payload)
            if written != len(payload):
                raise OSError("short write")
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "exclusive output failed") from exc


def _ensure_output_parent(root: Path) -> Path:
    codex_work = root / ".codex_work"
    _assert_non_symlink_parent(codex_work)
    parent = root / OUTPUT_PARENT_RELATIVE_PATH
    try:
        observed = os.lstat(parent)
    except FileNotFoundError:
        try:
            os.mkdir(parent, 0o700)
        except OSError as exc:
            raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "output parent create failed") from exc
        observed = os.lstat(parent)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "output parent unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "output parent differs")
    return parent


def _create_consumed_root(
    root: Path,
    output_root: Path,
    evidence: GreenImplementationEvidence,
) -> Path:
    parent = _ensure_output_parent(root)
    _assert_output_absent(output_root)
    try:
        os.mkdir(output_root, 0o700)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[1], "output root create failed") from exc
    marker = {
        "schema_name": "neurodecodekit.marc2_freewill_private_selection_consumed",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "state": "consumed_before_private_content_open",
        "execution_ordinal": 1,
        "decision_commit": GREEN_DECISION_COMMIT,
        "implementation_commit": evidence.implementation_commit,
        "output_parent_identity": parent.name,
        "retry_rerun_or_resume_allowed": False,
    }
    marker_path = output_root / CONSUMED_MARKER_NAME
    _write_exclusive(marker_path, _canonical_json_bytes(marker), mode=0o600)
    return marker_path


def _write_live_outputs(
    output_root: Path,
    report: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    marker_path: Path,
) -> tuple[Path, Path, int]:
    marker_bytes = os.lstat(marker_path).st_size
    report_bytes = _canonical_json_bytes(report)
    private_bytes = _canonical_json_bytes(private_manifest)
    total = _bounded_output_bytes(b"x" * marker_bytes, report_bytes, private_bytes)
    private_path = output_root / PRIVATE_SELECTION_NAME
    report_path = output_root / AGGREGATE_REPORT_NAME
    _write_exclusive(private_path, private_bytes, mode=0o600)
    _write_exclusive(report_path, report_bytes, mode=0o644)
    if stat.S_IMODE(os.lstat(private_path).st_mode) != 0o600:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "private output mode differs")
    return report_path, private_path, total


def _write_consumed_failure_report(
    output_root: Path,
    *,
    refusal: PrivateSelectionRefusal,
    stage: str,
    evidence: GreenImplementationEvidence,
    machine_gate: Mapping[str, Any],
    access_counters: Mapping[str, int],
    started: float,
    clock: Callable[[], float],
    rss_probe: Callable[[], int],
    marker_path: Path,
) -> None:
    counters = dict(access_counters)
    counters["aggregate_reports"] = 1
    report = _build_failure_report(
        refusal=refusal,
        stage=stage,
        evidence=evidence,
        machine_gate=machine_gate,
        access_counters=counters,
        runtime_seconds=clock() - started,
        peak_rss_bytes=rss_probe(),
    )
    marker_size = os.lstat(marker_path).st_size
    private_size = 0
    private_path = output_root / PRIVATE_SELECTION_NAME
    try:
        observed_private = os.lstat(private_path)
    except FileNotFoundError:
        pass
    except OSError as exc:
        raise PrivateSelectionRefusal(
            FAILURE_ROUTES[6],
            "private output identity unavailable",
        ) from exc
    else:
        if stat.S_ISLNK(observed_private.st_mode) or not stat.S_ISREG(
            observed_private.st_mode
        ):
            raise PrivateSelectionRefusal(
                FAILURE_ROUTES[6],
                "private output identity differs",
            )
        private_size = observed_private.st_size
    for _ in range(4):
        report_bytes = _canonical_json_bytes(report)
        total = _bounded_output_bytes(
            b"x" * marker_size,
            b"x" * private_size,
            report_bytes,
        )
        if report["measurements"]["output_bytes"] == total:
            break
        report["measurements"]["output_bytes"] = total
    else:
        raise PrivateSelectionRefusal(
            FAILURE_ROUTES[6],
            "failure output size did not stabilize",
        )
    validate_public_report(report)
    _write_exclusive(
        output_root / AGGREGATE_REPORT_NAME,
        _canonical_json_bytes(report),
        mode=0o644,
    )


def execute_registered_private_selection(
    repo_root: str | Path,
    *,
    evidence: GreenImplementationEvidence,
    output_root: str | Path,
    environ: Mapping[str, str],
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> PrivateSelectionOutcome:
    """Consume the one registered private selection and stop before payload."""

    started = clock()
    root = Path(repo_root)
    destination = Path(output_root)
    _assert_registered_output_root(root, destination)
    verify_green_implementation(root, evidence)
    machine = preconsumption_machine_gate(root, environ=environ, rss_reader=rss_probe)
    _assert_output_absent(destination)
    source_path = _assert_source_components(root, PRIVATE_SOURCE_RELATIVE_PATH)
    _preflight_private_source(source_path, expected_bytes=PRIVATE_SOURCE_BYTES)
    counters = _base_access_counters()
    counters["registered_private_path_component_checks"] = len(
        PRIVATE_SOURCE_RELATIVE_PATH.parts
    ) - 1
    counters["registered_private_final_lstats"] = 1
    marker_path = _create_consumed_root(root, destination, evidence)
    counters["consumed_markers"] = 1
    stage = "private_manifest_read"
    try:
        manifest, payload = read_locked_private_manifest(
            source_path,
            expected_bytes=PRIVATE_SOURCE_BYTES,
            expected_sha256=PRIVATE_SOURCE_SHA256,
            counters=counters,
        )
        stage = "target_free_prefix_selection"
        selection = select_live_prefix(
            manifest,
            source_file_sha256=_sha256_bytes(payload),
        )
        counters["real_participant_selections"] = selection.cohort_summary[
            "selected_subjects"
        ]
        counters["real_member_selections"] = selection.split_summary[
            "selected_core_members"
        ]
        stage = "resource_and_output_validation"
        runtime_seconds = clock() - started
        peak_rss_bytes = rss_probe()
        if runtime_seconds > MAX_RUNTIME_SECONDS or peak_rss_bytes > MAX_PEAK_RSS_BYTES:
            raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "live resource cap failed")
        counters["private_selection_manifests"] = 1
        counters["aggregate_reports"] = 1
        report = _build_report(
            selection,
            generated=False,
            input_bytes=len(payload),
            output_bytes=0,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            access_counters=counters,
            wrapper_mutations=None,
            inherited_mutations=None,
            machine_gate=machine,
            evidence=evidence,
            implementation_registry_sha256=evidence.implementation_registry_sha256,
        )
        validate_public_report(report, allow_incomplete_measurements=True)
        marker_size = os.lstat(marker_path).st_size
        private_bytes = _canonical_json_bytes(selection.private_manifest)
        for _ in range(4):
            report_bytes = _canonical_json_bytes(report)
            total = _bounded_output_bytes(
                b"x" * marker_size,
                report_bytes,
                private_bytes,
            )
            if report["measurements"]["output_bytes"] == total:
                break
            report["measurements"]["output_bytes"] = total
        else:
            raise PrivateSelectionRefusal(
                FAILURE_ROUTES[6],
                "live output size did not stabilize",
            )
        validate_public_report(report)
        if total > MAX_INCREMENTAL_DISK_BYTES:
            raise PrivateSelectionRefusal(
                FAILURE_ROUTES[6],
                "incremental disk cap exceeded",
            )
        report_path, private_path, written = _write_live_outputs(
            destination,
            report,
            selection.private_manifest,
            marker_path,
        )
        return PrivateSelectionOutcome(
            report=report,
            report_path=report_path,
            private_selection_path=private_path,
            consumed_marker_path=marker_path,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            input_bytes=len(payload),
            output_bytes=written,
        )
    except PrivateSelectionRefusal as refusal:
        report_path = destination / AGGREGATE_REPORT_NAME
        if not report_path.exists() and not report_path.is_symlink():
            _write_consumed_failure_report(
                destination,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                machine_gate=machine,
                access_counters=counters,
                started=started,
                clock=clock,
                rss_probe=rss_probe,
                marker_path=marker_path,
            )
        raise
    except Exception as exc:
        refusal = PrivateSelectionRefusal(
            FAILURE_ROUTES[6],
            "unexpected post-consumption implementation failure",
        )
        report_path = destination / AGGREGATE_REPORT_NAME
        if not report_path.exists() and not report_path.is_symlink():
            _write_consumed_failure_report(
                destination,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                machine_gate=machine,
                access_counters=counters,
                started=started,
                clock=clock,
                rss_probe=rss_probe,
                marker_path=marker_path,
            )
        raise refusal from exc


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    """Inspect only an aggregate generated or live report."""

    report_path = Path(path)
    try:
        observed = os.lstat(report_path)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "report unavailable") from exc
    if (
        stat.S_ISLNK(observed.st_mode)
        or not stat.S_ISREG(observed.st_mode)
        or observed.st_size > MAX_PUBLIC_OUTPUT_BYTES
    ):
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "report identity differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(report_path, flags)
        try:
            payload = _read_fd_bounded(descriptor, MAX_PUBLIC_OUTPUT_BYTES)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "report open failed") from exc
    report = _strict_json(payload)
    if report.get("schema_name") == PRIVATE_SELECTION_SCHEMA_NAME:
        raise PrivateSelectionRefusal(FAILURE_ROUTES[6], "private inspection forbidden")
    validate_public_report(report)
    return {
        "status": report["status"],
        "route": report["route"],
        "selected_subjects": report["cohort_summary"]["selected_subjects"],
        "selected_subject_ids": list(report["cohort_summary"]["selected_subject_ids"]),
        "selected_run_bundles": report["split_summary"]["selected_run_bundles"],
        "selected_core_members": report["split_summary"]["selected_core_members"],
        "selected_reservation_bytes": report["byte_summary"][
            "selected_reservation_bytes"
        ],
        "reservation_cap_bytes": report["byte_summary"]["reservation_cap_bytes"],
        "input_bytes": report["measurements"]["input_bytes"],
        "output_bytes": report["measurements"]["output_bytes"],
        "runtime_seconds": report["measurements"]["runtime_seconds"],
        "peak_RSS_bytes": report["measurements"]["peak_RSS_bytes"],
        "producer_is_causal": report["measurements"]["producer_is_causal"],
        "end_to_end_latency_measured": report["measurements"]
        ["end_to_end_latency_measured"],
        "warnings": list(report["warnings"]),
        "unavailable_fields": list(report["unavailable_fields"]),
    }


def registered_plan() -> dict[str, Any]:
    """Return the fixed plan without touching the registered source or output."""

    load_green_decision()
    return {
        "lane_id": LANE_ID,
        "green_decision_commit": GREEN_DECISION_COMMIT,
        "green_decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
        "commands": ["plan", "qualify", "inspect", "execute"],
        "private_source_bytes": PRIVATE_SOURCE_BYTES,
        "private_source_entries": PRIVATE_SOURCE_ENTRIES,
        "minimum_subjects": selector.MINIMUM_SUBJECTS,
        "maximum_subjects": selector.MAXIMUM_SUBJECTS,
        "reservation_cap_bytes": selector.RESERVATION_CAP_BYTES,
        "inherited_selector_mutations": 40,
        "wrapper_mutations": 18,
        "registered_executions": 1,
        "network_bytes": 0,
        "archive_local_header_or_member_bytes": 0,
        "signal_target_model_or_score_operations": 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_freewill_private_selection",
        description="Proof-gated MARC2-FW1A target-free private selection.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the fixed proof-gated plan.")
    qualify = subparsers.add_parser("qualify", help="Run generated/mock qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate report.")
    inspect.add_argument("report")
    execute = subparsers.add_parser("execute", help="Consume the registered private selection.")
    execute.add_argument("--output-root", required=True)
    execute.add_argument("--implementation-commit", required=True)
    execute.add_argument("--implementation-ci-run-id", required=True, type=int)
    execute.add_argument("--implementation-base-job-id", required=True, type=int)
    execute.add_argument("--implementation-optional-job-id", required=True, type=int)
    execute.add_argument("--implementation-registry-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the dependency-free MARC2-FW1A module CLI."""

    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            payload = registered_plan()
        elif args.command == "qualify":
            outcome = qualify_generated_mock_wrapper(args.output_dir)
            payload = inspect_public_result(outcome.report_path)
        elif args.command == "inspect":
            payload = inspect_public_result(args.report)
        else:
            evidence = GreenImplementationEvidence(
                implementation_commit=args.implementation_commit,
                implementation_ci_run_id=args.implementation_ci_run_id,
                implementation_base_job_id=args.implementation_base_job_id,
                implementation_optional_job_id=args.implementation_optional_job_id,
                implementation_registry_sha256=args.implementation_registry_sha256,
            )
            outcome = execute_registered_private_selection(
                _repo_root(),
                evidence=evidence,
                output_root=args.output_root,
                environ=os.environ,
            )
            payload = inspect_public_result(outcome.report_path)
    except PrivateSelectionRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
