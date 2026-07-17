"""Bounded, opaque acquisition for the registered Loop 53 S20 EEG bundle.

The payload path intentionally exposes no parser. Bytes are transferred and
hashed sequentially, then the complete verified directory is promoted once.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Sequence


CONTRACT_RELATIVE_PATH = Path("registries/loop53_fresh_eeg_acquisition_contract.v0.json")
DECISION_RELATIVE_PATH = Path("registries/loop53_authorization_decision.v0.json")
CONTRACT_SHA256 = "bc7d86a1ce6ef3dc71dacca0af97cb5813df87620ac35d4f34ecd343f97e65ac"
DECISION_SHA256 = "f5e75bb9f9315ced6f45812f3841973abedbef3c8a0890fa78737a7b5b478107"
AUTHORIZATION_COMMIT = "2a47bbc75eac0118c3f9de87363d7da02584d2fc"
AUTHORIZATION_PUSH_CI_RUN_ID = 29589212626
AUTHORIZATION_PR_CI_RUN_ID = 29589225113
EXPECTED_REPO_ID = "bcbl190626/SpanishBCBL"
EXPECTED_REVISION = "88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684"
EXPECTED_LICENSE = "cc-by-nc-4.0"
EXPECTED_PAYLOAD_BYTES = 96_090_264
CHUNK_BYTES = 1024 * 1024
MAX_METADATA_RESPONSE_BYTES = 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
REQUIRED_UNAVAILABLE_FIELDS = (
    "channel_count",
    "channel_names",
    "sampling_rate_hz",
    "reference_scheme",
    "sensor_geometry",
    "event_count",
    "trial_count",
    "target_text",
    "signal_quality",
    "neural_advantage",
    "decoding_accuracy",
    "end_to_end_latency",
)


class AcquisitionRefusal(RuntimeError):
    """Preflight failed before the registered invocation could safely start."""


class AcquisitionFailure(RuntimeError):
    """A consumed registered invocation failed and must be parked."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


@dataclass(frozen=True)
class ExecutionEvidence:
    """Remote-green implementation evidence supplied to the frozen runner."""

    implementation_commit: str
    implementation_push_ci_run_id: int
    implementation_pr_ci_run_id: int


@dataclass(frozen=True)
class AcquisitionOutcome:
    """One pass-or-park result and its two private receipt paths."""

    status: str
    manifest: dict[str, Any]
    manifest_path: Path
    receipt_path: Path

    @property
    def passed(self) -> bool:
        return self.status == "passed"


RevisionFetcher = Callable[[str, str], tuple[dict[str, Any], int]]
PathsFetcher = Callable[[str, str, Sequence[str]], tuple[list[dict[str, Any]], int]]
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
    """Return the immutable plan without touching S20 paths or the network."""

    root = Path(repo_root)
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    storage = contract["storage_and_output"]
    caps = contract["resource_caps"]
    return {
        "mode": "dry_run_no_path_stat_no_network",
        "repo_id": contract["source_repository"]["repo_id"],
        "revision": contract["source_repository"]["revision"],
        "license_id": contract["source_repository"]["license_id"],
        "subject_id": contract["cohort_identity"]["subject_id"],
        "session_id": contract["cohort_identity"]["session_id"],
        "block_id": contract["cohort_identity"]["block_id"],
        "file_count": len(contract["selected_files"]),
        "file_paths": [row["repository_path"] for row in contract["selected_files"]],
        "expected_payload_bytes": storage["expected_final_payload_bytes"],
        "payload_root": storage["payload_root"],
        "temporary_root": storage["temporary_root"],
        "receipt_root": storage["receipt_root"],
        "caps": {
            "cpu_threads": caps["cpu_threads"],
            "workers": caps["workers"],
            "wall_time_seconds": caps["wall_time_seconds"],
            "peak_rss_bytes": caps["peak_rss_bytes"],
            "network_payload_bytes": storage["maximum_network_payload_bytes"],
            "incremental_disk_bytes": storage[
                "maximum_incremental_disk_bytes_including_temporary_files"
            ],
            "minimum_free_disk_bytes": storage["minimum_free_disk_bytes_before_execution"],
            "receipt_bytes": storage["maximum_generated_receipt_bytes"],
        },
        "warnings": [
            "dry_run_only_no_registered_path_stat_or_network_access",
            "cc_by_nc_4_0_noncommercial_research_boundary",
            "execute_consumes_the_single_registered_invocation_even_if_it_parks",
            "payload_content_must_never_be_parsed_or_interpreted_in_loop53",
        ],
    }


def _verify_execution_evidence(repo_root: Path, evidence: ExecutionEvidence) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", evidence.implementation_commit):
        raise AcquisitionRefusal("implementation commit must be a full lowercase Git SHA")
    if evidence.implementation_commit == AUTHORIZATION_COMMIT:
        raise AcquisitionRefusal("implementation commit must follow the authorization commit")
    if evidence.implementation_push_ci_run_id <= 0 or evidence.implementation_pr_ci_run_id <= 0:
        raise AcquisitionRefusal("both implementation CI run IDs must be positive")

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


def _license_values(metadata: Mapping[str, Any]) -> set[str]:
    values: set[str] = set()
    card_data = metadata.get("cardData")
    if isinstance(card_data, Mapping):
        license_value = card_data.get("license")
        if isinstance(license_value, str):
            values.add(license_value)
        elif isinstance(license_value, list):
            values.update(item for item in license_value if isinstance(item, str))
    tags = metadata.get("tags")
    if isinstance(tags, list):
        values.update(
            item.split(":", 1)[1]
            for item in tags
            if isinstance(item, str) and item.startswith("license:")
        )
    return values


def _validate_revision_metadata(metadata: Mapping[str, Any], source: Mapping[str, Any]) -> None:
    expected_revision = source["revision"]
    if metadata.get("sha") != expected_revision:
        raise AcquisitionFailure("metadata", "pinned revision SHA mismatch")
    if metadata.get("private") is not False:
        raise AcquisitionFailure("metadata", "dataset is no longer explicitly public")
    if metadata.get("gated") is not False:
        raise AcquisitionFailure("metadata", "dataset is gated or availability is ambiguous")
    if metadata.get("disabled") is not False:
        raise AcquisitionFailure("metadata", "dataset is disabled or availability is ambiguous")
    if source["license_id"] not in _license_values(metadata):
        raise AcquisitionFailure("metadata", "registered cc-by-nc-4.0 license metadata mismatch")


def _validate_path_metadata(
    rows: Sequence[Mapping[str, Any]], selected_files: Sequence[Mapping[str, Any]]
) -> None:
    expected = {row["repository_path"]: row for row in selected_files}
    observed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        path = row.get("path")
        if not isinstance(path, str) or path in observed:
            raise AcquisitionFailure("metadata", "paths-info returned an invalid or duplicate path")
        observed[path] = row
    if set(observed) != set(expected):
        raise AcquisitionFailure("metadata", "paths-info membership differs from four frozen paths")

    for path, frozen in expected.items():
        row = observed[path]
        if row.get("type") != "file":
            raise AcquisitionFailure("metadata", f"paths-info type mismatch for {path}")
        if row.get("size") != frozen["size_bytes"]:
            raise AcquisitionFailure("metadata", f"paths-info size mismatch for {path}")
        if row.get("oid") != frozen["repository_oid"]:
            raise AcquisitionFailure("metadata", f"paths-info source oid mismatch for {path}")
        expected_lfs = frozen.get("lfs_sha256")
        lfs = row.get("lfs")
        if expected_lfs is None:
            if lfs not in (None, {}):
                raise AcquisitionFailure("metadata", f"unexpected LFS metadata for {path}")
        else:
            if not isinstance(lfs, Mapping):
                raise AcquisitionFailure("metadata", f"missing LFS metadata for {path}")
            if lfs.get("oid") != expected_lfs or lfs.get("size") != frozen["size_bytes"]:
                raise AcquisitionFailure("metadata", f"LFS identity mismatch for {path}")
            if row.get("xetHash") != frozen.get("xet_hash"):
                raise AcquisitionFailure("metadata", f"Xet identity mismatch for {path}")


def _read_bounded_json(response: BinaryIO) -> tuple[Any, int]:
    payload = response.read(MAX_METADATA_RESPONSE_BYTES + 1)
    if len(payload) > MAX_METADATA_RESPONSE_BYTES:
        raise AcquisitionFailure("metadata", "metadata response exceeded the 1 MiB safety bound")
    try:
        return json.loads(payload), len(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AcquisitionFailure("metadata", "metadata response was not valid JSON") from exc


def _fetch_revision_metadata(repo_id: str, revision: str) -> tuple[dict[str, Any], int]:
    url = f"https://huggingface.co/api/datasets/{repo_id}/revision/{revision}"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Accept-Encoding": "identity"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        value, size = _read_bounded_json(response)
    if not isinstance(value, dict):
        raise AcquisitionFailure("metadata", "revision metadata must be a JSON object")
    return value, size


def _fetch_paths_metadata(
    repo_id: str, revision: str, paths: Sequence[str]
) -> tuple[list[dict[str, Any]], int]:
    url = f"https://huggingface.co/api/datasets/{repo_id}/paths-info/{revision}"
    fields = [("paths", path) for path in paths]
    fields.append(("expand", "false"))
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(fields).encode("ascii"),
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        value, size = _read_bounded_json(response)
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise AcquisitionFailure("metadata", "paths-info metadata must be a JSON object list")
    return value, size


def _open_payload(url: str, expected_size: int) -> BinaryIO:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/octet-stream", "Accept-Encoding": "identity"},
        method="GET",
    )
    response = urllib.request.urlopen(request, timeout=30)
    encoding = response.headers.get("Content-Encoding")
    if encoding not in (None, "identity"):
        response.close()
        raise AcquisitionFailure("transfer", f"unexpected payload content encoding: {encoding}")
    content_length = response.headers.get("Content-Length")
    if content_length is not None:
        try:
            observed = int(content_length)
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


def _payload_url(repo_id: str, revision: str, path: str) -> str:
    quoted = urllib.parse.quote(path, safe="/")
    return f"https://huggingface.co/datasets/{repo_id}/resolve/{revision}/{quoted}?download=true"


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


def _opaque_hash_file(path: Path, frozen: Mapping[str, Any]) -> tuple[int, str, str | None]:
    expected_size = int(frozen["size_bytes"])
    content_sha256 = hashlib.sha256()
    git_sha1 = hashlib.sha1() if frozen["repository_oid_algorithm"] == "git_blob_sha1" else None
    if git_sha1 is not None:
        git_sha1.update(f"blob {expected_size}\0".encode("ascii"))
    observed_size = 0
    with path.open("rb", buffering=0) as stream:
        while True:
            chunk = stream.read(CHUNK_BYTES)
            if not chunk:
                break
            observed_size += len(chunk)
            content_sha256.update(chunk)
            if git_sha1 is not None:
                git_sha1.update(chunk)
    return observed_size, content_sha256.hexdigest(), git_sha1.hexdigest() if git_sha1 else None


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
        "registered_acquisition_invocations": 1,
        "metadata_calls": 0,
        "metadata_response_bytes": 0,
        "payload_download_invocations": 0,
        "payload_file_requests": 0,
        "network_payload_bytes": 0,
        "opaque_hash_reads": 0,
        "local_S20_payload_hash_reads": 0,
        "header_reads": 0,
        "marker_reads": 0,
        "signal_reads": 0,
        "mat_reads": 0,
        "target_or_label_reads": 0,
        "cache_reads_or_writes": 0,
        "split_operations": 0,
        "model_or_checkpoint_loads": 0,
        "model_inference_runs": 0,
        "training_or_parameter_update_runs": 0,
        "scoring_runs": 0,
        "language_model_runs": 0,
        "rw3_stream_device_or_hardware_operations": 0,
        "additional_file_requests": 0,
        "additional_participant_operations": 0,
        "reruns": 0,
    }


def _warnings(status: str, failure_stage: str | None) -> list[str]:
    values = [
        "cc_by_nc_4_0_noncommercial_research_boundary",
        "payload_bytes_hashed_opaquely_without_decode_parse_or_interpretation",
        "single_registered_invocation_consumed_no_rerun_authorized",
        "bundle_identity_does_not_establish_brainvision_readability_or_signal_quality",
        "no_scientific_decoding_realtime_portable_home_or_clinical_claim_upgrade",
    ]
    if status == "parked":
        values.append(f"registered_invocation_parked_at_{failure_stage or 'unknown'}")
    return values


def _unavailable_fields() -> dict[str, str]:
    reason = "unavailable because Loop 53 forbids payload interpretation and downstream analysis"
    return {field: reason for field in REQUIRED_UNAVAILABLE_FIELDS}


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
        "authorization_and_implementation_commits_remote_green_before_execution": True,
        "pinned_revision_license_and_availability_exact": metadata_matched,
        "four_metadata_records_match_frozen_identity": metadata_matched,
        "one_complete_four_file_96090264_byte_bundle": transfer_complete and bundle_promoted,
        "all_opaque_size_and_integrity_checks_pass": integrity_matched,
        "all_resource_and_output_caps_pass": resource_caps_passed and passed,
        "all_forbidden_access_and_operation_counters_zero": forbidden_counters_zero,
        "all_warnings_and_unavailable_fields_explicit": True,
        "no_preexisting_path_followed_overwritten_deleted_or_renamed": True,
        "no_scientific_or_decoding_claim_promoted": True,
    }


def _claim_boundary(status: str) -> dict[str, str]:
    if status == "passed":
        engineering = (
            "The exact four-file public S20 bundle was acquired once and matched its frozen "
            "source identities within the registered resource, storage, license, and access-order limits."
        )
    else:
        engineering = (
            "The one registered acquisition was consumed and parked; no complete qualifying bundle "
            "is claimed."
        )
    return {
        "engineering_result": engineering,
        "scientific_claim_not_established": (
            "Loop 53 establishes no BrainVision readability, EEG signal quality, trial or target "
            "validity, neural advantage, decoding accuracy, generalization, end-to-end latency, "
            "portable hardware, at-home use, or clinical utility."
        ),
    }


def _human_receipt(manifest: Mapping[str, Any]) -> str:
    metrics = manifest["measurements"]
    return "\n".join(
        [
            "# Loop 53 S20 EEG Acquisition Receipt",
            "",
            f"Status: **{manifest['status'].upper()}**",
            f"Source revision: `{manifest['source_revision']}`",
            f"License: `{manifest['license_id']}` (noncommercial research boundary)",
            f"Files: {metrics['final_file_count']}",
            f"Final payload bytes: {metrics['final_payload_bytes']}",
            f"Network payload bytes: {metrics['network_payload_bytes']}",
            f"Runtime seconds: {metrics['runtime_seconds']}",
            f"Peak RSS bytes: {metrics['peak_rss_bytes']}",
            f"Incremental disk peak bytes: {metrics['incremental_disk_peak_bytes']}",
            f"Failure stage: {manifest.get('failure_stage') or 'none'}",
            "",
            "## Warnings",
            "",
            *[f"- `{warning}`" for warning in manifest["warnings"]],
            "",
            "## Claim Boundary",
            "",
            manifest["claim_boundary"]["engineering_result"],
            "",
            manifest["claim_boundary"]["scientific_claim_not_established"],
            "",
        ]
    )


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
        free_after = shutil.disk_usage(workspace_root).free
        manifest["measurements"]["free_disk_after_bytes"] = free_after
        machine, human = _render_receipts(manifest, cap_bytes)
        with machine_path.open("wb") as stream:
            stream.write(machine)
        with human_path.open("wb") as stream:
            stream.write(human)
    return machine_path, human_path


def _build_manifest(
    *,
    status: str,
    contract_sha256: str,
    decision_sha256: str,
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
    final_payload_bytes: int,
    final_file_count: int,
    failure_stage: str | None,
    failure_reason: str | None,
    gates: Mapping[str, bool],
) -> dict[str, Any]:
    source = contract["source_repository"]
    return {
        "schema_name": "neurodecodekit.loop53_acquisition_manifest",
        "schema_version": "0.1.0",
        "loop_id": 53,
        "status": status,
        "proof_posture": "acquisition_mechanics_only_opaque_payload_no_interpretation",
        "contract_sha256": contract_sha256,
        "authorization_decision_sha256": decision_sha256,
        "authorization_commit": AUTHORIZATION_COMMIT,
        "authorization_push_ci_run_id": AUTHORIZATION_PUSH_CI_RUN_ID,
        "authorization_pr_ci_run_id": AUTHORIZATION_PR_CI_RUN_ID,
        "implementation_commit": evidence.implementation_commit,
        "implementation_push_ci_run_id": evidence.implementation_push_ci_run_id,
        "implementation_pr_ci_run_id": evidence.implementation_pr_ci_run_id,
        "source_repository": source["repo_id"],
        "source_revision": source["revision"],
        "license_id": source["license_id"],
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "failure_stage": failure_stage,
        "failure_reason": failure_reason,
        "measurements": {
            "input_expected_bytes": contract["storage_and_output"]["expected_final_payload_bytes"],
            "network_payload_bytes": counters["network_payload_bytes"],
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
            "end_to_end_latency_measured": False,
        },
        "file_paths_sizes_source_oids_and_content_sha256": list(file_records),
        "access_counters": dict(counters),
        "header_marker_signal_mat_target_reads": 0,
        "cache_split_model_training_scoring_runs": 0,
        "warnings": _warnings(status, failure_stage),
        "unavailable_fields": _unavailable_fields(),
        "acceptance_gate_results": dict(gates),
        "claim_boundary": _claim_boundary(status),
    }


def run_acquisition(
    *,
    contract: Mapping[str, Any],
    contract_sha256: str,
    decision_sha256: str,
    evidence: ExecutionEvidence,
    workspace_root: str | Path,
    revision_fetcher: RevisionFetcher,
    paths_fetcher: PathsFetcher,
    payload_opener: PayloadOpener,
    environ: Mapping[str, str],
    clock: Callable[[], float] = time.monotonic,
    utc_now: Callable[[], str] = _utc_now,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> AcquisitionOutcome:
    """Execute one pass-or-park acquisition using a validated contract.

    Tests supply tiny opaque streams and fake metadata transports. The
    registered wrapper below supplies only the frozen public contract.
    """

    _check_thread_environment(environ)
    source = contract["source_repository"]
    storage = contract["storage_and_output"]
    caps = contract["resource_caps"]
    selected_files = contract["selected_files"]
    if source["repo_id"] != EXPECTED_REPO_ID or source["revision"] != EXPECTED_REVISION:
        raise AcquisitionRefusal("source identity is not the frozen Loop 53 repository revision")
    if source["license_id"] != EXPECTED_LICENSE:
        raise AcquisitionRefusal("license identity is not the frozen Loop 53 license")
    expected_total = sum(int(row["size_bytes"]) for row in selected_files)
    if len(selected_files) != 4 or expected_total != storage["expected_final_payload_bytes"]:
        raise AcquisitionRefusal("contract must bind exactly four files and its exact byte total")

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

        revision_metadata, revision_bytes = revision_fetcher(source["repo_id"], source["revision"])
        counters["metadata_calls"] += 1
        counters["metadata_response_bytes"] += revision_bytes
        _assert_live_caps(
            start_monotonic=started,
            clock=clock,
            rss_reader=rss_reader,
            wall_cap=caps["wall_time_seconds"],
            rss_cap=caps["peak_rss_bytes"],
        )
        _validate_revision_metadata(revision_metadata, source)

        registered_paths = [row["repository_path"] for row in selected_files]
        path_metadata, path_bytes = paths_fetcher(
            source["repo_id"], source["revision"], registered_paths
        )
        counters["metadata_calls"] += 1
        counters["metadata_response_bytes"] += path_bytes
        _validate_path_metadata(path_metadata, selected_files)
        metadata_matched = True

        counters["payload_download_invocations"] = 1
        for frozen in selected_files:
            relative = _safe_relative_path(frozen["destination_relative_path"])
            destination = staging_bundle / relative
            _mkdir_tracked(destination.parent, workspace_root=root, created_dirs=created_temp_dirs)
            url = _payload_url(source["repo_id"], source["revision"], frozen["repository_path"])
            expected_size = int(frozen["size_bytes"])
            observed_size = 0
            counters["payload_file_requests"] += 1
            stream = payload_opener(url, expected_size)
            with _managed_binary_stream(stream), destination.open("xb", buffering=0) as output:
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
                    counters["network_payload_bytes"] += len(chunk)
                    if counters["network_payload_bytes"] > storage["maximum_network_payload_bytes"]:
                        raise AcquisitionFailure("resource", "network payload cap exceeded")
                    output.write(chunk)
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

        if counters["network_payload_bytes"] != expected_total:
            raise AcquisitionFailure("transfer", "batch payload byte total mismatch")
        transfer_complete = True

        for frozen in selected_files:
            relative = _safe_relative_path(frozen["destination_relative_path"])
            path = staging_bundle / relative
            counters["opaque_hash_reads"] += 1
            counters["local_S20_payload_hash_reads"] += 1
            observed_size, content_sha256, git_blob_sha1 = _opaque_hash_file(path, frozen)
            if observed_size != frozen["size_bytes"]:
                raise AcquisitionFailure("integrity", "opaque verification size mismatch")
            if frozen["repository_oid_algorithm"] == "git_blob_sha1":
                if git_blob_sha1 != frozen["repository_oid"]:
                    raise AcquisitionFailure("integrity", "opaque Git blob SHA-1 mismatch")
            elif frozen["repository_oid_algorithm"] == "git_lfs_pointer_sha1":
                if content_sha256 != frozen["lfs_sha256"]:
                    raise AcquisitionFailure("integrity", "opaque LFS SHA-256 mismatch")
            else:
                raise AcquisitionFailure("integrity", "unsupported registered oid algorithm")
            file_records.append(
                {
                    "role": frozen["role"],
                    "path": frozen["repository_path"],
                    "size_bytes": observed_size,
                    "repository_oid_algorithm": frozen["repository_oid_algorithm"],
                    "repository_oid": frozen["repository_oid"],
                    "lfs_sha256": frozen.get("lfs_sha256"),
                    "xet_hash": frozen.get("xet_hash"),
                    "content_sha256": content_sha256,
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
        if final_file_count != 4 or final_payload_bytes != expected_total:
            raise AcquisitionFailure("integrity", "staging bundle count or byte total mismatch")
        integrity_matched = True

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
    except Exception as exc:  # noqa: BLE001 - convert a consumed invocation to a park receipt
        failure_stage = "unexpected"
        failure_reason = f"{type(exc).__name__}: {exc}"
        _cleanup_created_temp(created_temp_files, created_temp_dirs)

    finished_at = utc_now()
    runtime_seconds = clock() - started
    peak_rss = max(peak_rss, rss_reader())
    status = "passed" if bundle_promoted and failure_stage is None else "parked"
    forbidden_zero = all(
        counters[key] == 0
        for key in (
            "header_reads",
            "marker_reads",
            "signal_reads",
            "mat_reads",
            "target_or_label_reads",
            "cache_reads_or_writes",
            "split_operations",
            "model_or_checkpoint_loads",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "scoring_runs",
            "language_model_runs",
            "rw3_stream_device_or_hardware_operations",
            "additional_file_requests",
            "additional_participant_operations",
            "reruns",
        )
    )
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
        contract_sha256=contract_sha256,
        decision_sha256=decision_sha256,
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
        cap_bytes=storage["maximum_generated_receipt_bytes"],
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
    """Run the one frozen Loop 53 acquisition after all green gates."""

    root = Path(repo_root)
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    if decision["authorized_contract"]["sha256"] != CONTRACT_SHA256:
        raise AcquisitionRefusal("authorization decision does not bind the frozen contract")
    if contract["storage_and_output"]["expected_final_payload_bytes"] != EXPECTED_PAYLOAD_BYTES:
        raise AcquisitionRefusal("registered payload byte total drifted")
    _verify_execution_evidence(root, evidence)
    return run_acquisition(
        contract=contract,
        contract_sha256=CONTRACT_SHA256,
        decision_sha256=DECISION_SHA256,
        evidence=evidence,
        workspace_root=root,
        revision_fetcher=_fetch_revision_metadata,
        paths_fetcher=_fetch_paths_metadata,
        payload_opener=_open_payload,
        environ=os.environ,
    )
