"""Generated-only qualification coordinator for DREYER-C5R-1 H-L1R1.

This module composes the immutable Stage H and H-L1R1 generated helpers. It has
no real-data, network, model, target, scoring, stream, or device capability.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import shutil
import stat
import sys
import tempfile
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h
from neurodecodekit.datasets import dreyer_c5r_1_stage_h_live_recovery as recovery

SCHEMA_VERSION = "0.1.0"
QUALIFICATION_ID = "DREYER-C5R-1-HL1R1-Q0"
DECISION_ID = "DREYER-C5R-1-HL1R1-QA0-D0"
DECISION_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_live_recovery_qualification_decision.v0.json"
)
DECISION_SHA256 = "2dd86073d183d114ba75eadffbfb407f250c947f1ae44e48b117e8b43875a663"
DECISION_COMMIT = "749fd5695441350d8cc949af19b6ad4bb5863dba"
DECISION_CI_RUN_ID = 33_251_731_156
DECISION_BASE_JOB_ID = 99_098_454_755
DECISION_OPTIONAL_JOB_ID = 99_098_454_800
QUALIFICATION_RELATIVE_ROOT = (
    recovery.PRIVATE_ROOT_RELATIVE_PATH / "registered-qualification-Q0"
)
CONSUMED_MARKER_NAME = "qualification-consumed.v0.json"
RESULT_NAME = "qualification-result.v0.json"
EXPECTED_TOTAL_CASES = 65
EXPECTED_VALID_H1_REPLAYS = 2
EXPECTED_INHERITED_VALID_CASES = 2
EXPECTED_INHERITED_REFUSALS = 18
EXPECTED_SUCCESSOR_REFUSALS = 43
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_GENERATED_IO_BYTES = 8 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 16 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MINIMUM_FREE_DISK_BYTES = 2 * MAX_INCREMENTAL_DISK_BYTES
RESULT_KEYS = frozenset(
    {
        "schema_name",
        "schema_version",
        "qualification_id",
        "packet_id",
        "lane_id",
        "status",
        "decision_proof",
        "matrix",
        "measurements",
        "operation_counters",
        "warnings",
        "claim_boundary",
    }
)


class QualificationRefusal(RuntimeError):
    """Sanitized qualification refusal."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_bytes(value: Any) -> bytes:
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


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _strict_json(payload: bytes) -> Any:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    return json.loads(
        payload.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda _value: (_ for _ in ()).throw(
            ValueError("non-finite JSON")
        ),
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        while chunk := os.read(descriptor, 64 * 1024):
            digest.update(chunk)
    finally:
        os.close(descriptor)
    return digest.hexdigest()


def _read_regular_file(path: Path, *, byte_cap: int) -> bytes:
    info = os.lstat(path)
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or info.st_size <= 0
        or info.st_size > byte_cap
    ):
        raise QualificationRefusal("HL1R1-Q-PROOF")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                raise QualificationRefusal("HL1R1-Q-PROOF")
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if os.read(descriptor, 1):
            raise QualificationRefusal("HL1R1-Q-PROOF")
    finally:
        os.close(descriptor)
    return payload


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green packet-bound qualification decision."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / DECISION_RELATIVE_PATH
    try:
        payload = _read_regular_file(path, byte_cap=MAX_PUBLIC_OUTPUT_BYTES)
        if hashlib.sha256(payload).hexdigest() != DECISION_SHA256:
            raise QualificationRefusal("HL1R1-Q-PROOF")
        decision = _strict_json(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise QualificationRefusal("HL1R1-Q-PROOF") from exc
    if not isinstance(decision, dict):
        raise QualificationRefusal("HL1R1-Q-PROOF")
    authorization = decision.get("authorization_after_decision_green", {})
    required = decision.get("required_qualification_contract", {})
    if (
        decision.get("decision_id") != DECISION_ID
        or decision.get("maintainer_words") != "continue"
        or authorization.get("run_one_registered_generated_qualification_after_coordinator_remote_green")
        is not True
        or authorization.get("registered_qualification_attempts_maximum") != 1
        or authorization.get("make_real_HTTP_request") is not False
        or authorization.get("open_real_or_private_path") is not False
        or authorization.get("write_or_read_real_EDF") is not False
        or required.get("valid_H1_replays") != EXPECTED_VALID_H1_REPLAYS
        or required.get("inherited_stage_H_valid_cases")
        != EXPECTED_INHERITED_VALID_CASES
        or required.get("inherited_stage_H_refusals")
        != EXPECTED_INHERITED_REFUSALS
        or required.get("ordered_successor_refusal_cases")
        != EXPECTED_SUCCESSOR_REFUSALS
        or required.get("attempt_consumed_on_pass_or_failure") is not True
        or required.get("rerun_retry_resume_repair_substitution_or_amendment_allowed")
        is not False
    ):
        raise QualificationRefusal("HL1R1-Q-PROOF")
    return decision


def _fixed_disk(_path: Path) -> Any:
    return type("Usage", (), {"free": MINIMUM_FREE_DISK_BYTES + 1024**3})()


def _fixed_clock() -> float:
    return 100.0


def _case_kwargs(repo_root: Path) -> dict[str, Any]:
    return {
        "repo_root": repo_root,
        "disk_usage_reader": _fixed_disk,
        "rss_reader": lambda: 16 * 1024**2,
        "clock": _fixed_clock,
    }


def _assert_no_transaction_debris(workspace: Path, *, case: str) -> None:
    private_root = workspace / recovery.PRIVATE_ROOT_RELATIVE_PATH
    staging = private_root / recovery.STAGING_DIRECTORY_NAME
    if (staging.exists() and case != "occupied_staging_name") or (
        private_root / recovery.FINAL_PAYLOAD_NAME
    ).exists():
        raise QualificationRefusal("HL1R1-Q-DEBRIS")
    if case == "occupied_staging_name" and (
        not staging.is_dir() or any(staging.iterdir())
    ):
        raise QualificationRefusal("HL1R1-Q-DEBRIS")


def run_development_matrix(
    root: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Run the exact 65-case generated matrix without consuming Q0."""

    repository = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(repository)
    workspace_root = Path(root).absolute()
    info = os.lstat(workspace_root)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise QualificationRefusal("HL1R1-Q-PATH")

    valid_results: list[recovery.DevelopmentCaseResult] = []
    for index in range(EXPECTED_VALID_H1_REPLAYS):
        workspace = workspace_root / f"valid-h1-{index}"
        workspace.mkdir(mode=0o700)
        result = recovery.run_development_case(
            workspace,
            **_case_kwargs(repository),
        )
        if (
            result.report["route"] != "DREYER-H1"
            or result.events[:2] != ("marker_durable", "transaction_entered")
            or result.events.index("marker_durable")
            >= result.events.index("opener_constructed")
            or result.opener_constructions != 1
            or result.requests != 1
            or not result.response_closed
            or not result.marker_path.is_file()
            or not result.output_path.is_file()
            or not result.final_payload_path.is_file()
        ):
            raise QualificationRefusal("HL1R1-Q-H1")
        if recovery.inspect_generated_report(result.output_path) != result.report:
            raise QualificationRefusal("HL1R1-Q-H1")
        valid_results.append(result)
    valid_payloads = [item.output_path.read_bytes() for item in valid_results]
    if valid_payloads[0] != valid_payloads[1]:
        raise QualificationRefusal("HL1R1-Q-REPLAY")

    successor_records: list[dict[str, Any]] = []
    successor_input_bytes = 0
    base_fixture_bytes = int(
        valid_results[0].report["resources"]["generated_input_bytes"]
    )
    for index, case in enumerate(recovery.ORDERED_SUCCESSOR_REFUSAL_CASES):
        workspace = workspace_root / f"successor-{index:02d}"
        workspace.mkdir(mode=0o700)
        try:
            result = recovery.run_development_case(
                workspace,
                case=case,
                **_case_kwargs(repository),
            )
        except recovery.RecoveryRefusal as exc:
            if case not in recovery.PREMARKER_CASES | recovery.PUBLICATION_REFUSAL_CASES:
                raise QualificationRefusal("HL1R1-Q-REFUSAL") from exc
            if exc.case != case:
                raise QualificationRefusal("HL1R1-Q-REFUSAL") from exc
            if case in recovery.PUBLICATION_REFUSAL_CASES:
                successor_input_bytes += base_fixture_bytes
            successor_records.append(
                {
                    "case": case,
                    "outcome": "sanitized_refusal",
                    "refusal_code": exc.code,
                    "route": None,
                }
            )
        else:
            if (
                case in recovery.PREMARKER_CASES
                or case in recovery.PUBLICATION_REFUSAL_CASES
                or result.report["route"] != "DREYER-H0"
                or result.report["refusal_case"] != case
                or not result.response_closed
            ):
                raise QualificationRefusal("HL1R1-Q-REFUSAL")
            successor_input_bytes += int(
                result.report["resources"]["generated_input_bytes"]
            )
            successor_records.append(
                {
                    "case": case,
                    "outcome": "aggregate_H0",
                    "refusal_code": result.report["refusal_code"],
                    "route": "DREYER-H0",
                }
            )
        _assert_no_transaction_debris(workspace, case=case)

    inherited_root = workspace_root / "inherited-stage-h"
    inherited_root.mkdir(mode=0o700)
    try:
        inherited, inherited_input_bytes, inherited_retained_bytes = (
            stage_h._run_generated_cases(inherited_root)
        )
    except stage_h.StageHRefusal as exc:
        raise QualificationRefusal("HL1R1-Q-INHERITED") from exc
    if (
        inherited.get("valid_cases_passed") != EXPECTED_INHERITED_VALID_CASES
        or inherited.get("adversarial_cases_refused")
        != EXPECTED_INHERITED_REFUSALS
        or inherited.get("deterministic_replay") is not True
        or len(inherited.get("adversarial_case_names", []))
        != EXPECTED_INHERITED_REFUSALS
    ):
        raise QualificationRefusal("HL1R1-Q-INHERITED")

    valid_input_bytes = sum(
        int(item.report["resources"]["generated_input_bytes"])
        for item in valid_results
    )
    matrix = {
        "total_cases": EXPECTED_TOTAL_CASES,
        "valid_H1_replays": EXPECTED_VALID_H1_REPLAYS,
        "valid_H1_byte_deterministic": True,
        "valid_H1_report_sha256": hashlib.sha256(valid_payloads[0]).hexdigest(),
        "inherited_stage_H_valid_cases": inherited["valid_cases_passed"],
        "inherited_stage_H_refusals": inherited["adversarial_cases_refused"],
        "inherited_stage_H_case_names": inherited["adversarial_case_names"],
        "inherited_stage_H_payload_sha256": inherited["payload_sha256"],
        "ordered_successor_refusals": len(successor_records),
        "successor_case_order": [item["case"] for item in successor_records],
        "successor_outcomes": successor_records,
        "marker_before_capability": True,
        "exactly_one_opener_and_request_on_H1": True,
        "response_closure": True,
        "manifest_contained_cleanup": True,
        "no_staging_or_unaccepted_payload_debris": True,
        "aggregate_H0_behavior": True,
        "no_replace_publication": True,
        "consumed_rerun_refusal": True,
        "generated_fixture_input_bytes": (
            valid_input_bytes + successor_input_bytes + inherited_input_bytes
        ),
        "inherited_retained_bytes": inherited_retained_bytes,
    }
    if (
        matrix["total_cases"]
        != matrix["valid_H1_replays"]
        + matrix["inherited_stage_H_valid_cases"]
        + matrix["inherited_stage_H_refusals"]
        + matrix["ordered_successor_refusals"]
    ):
        raise QualificationRefusal("HL1R1-Q-INVENTORY")
    return matrix


def _tree_sizes(root: Path) -> tuple[int, int]:
    logical = 0
    allocated = 0
    for directory, directories, files in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in tuple(directories):
            info = os.lstat(base / name)
            if stat.S_ISLNK(info.st_mode):
                directories.remove(name)
                logical += info.st_size
                allocated += int(getattr(info, "st_blocks", 0)) * 512 or info.st_size
            elif not stat.S_ISDIR(info.st_mode):
                raise QualificationRefusal("HL1R1-Q-PATH")
        for name in files:
            info = os.lstat(base / name)
            if (
                stat.S_ISLNK(info.st_mode)
                or not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1
            ):
                raise QualificationRefusal("HL1R1-Q-PATH")
            logical += info.st_size
            allocated += int(getattr(info, "st_blocks", 0)) * 512 or info.st_size
    return logical, allocated


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _ensure_thread_caps(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in recovery.THREAD_ENV_KEYS):
        raise QualificationRefusal("HL1R1-Q-RESOURCE")


def _ensure_directory(path: Path) -> None:
    if not path.is_absolute() or ".." in path.parts:
        raise QualificationRefusal("HL1R1-Q-PATH")
    missing: list[Path] = []
    current = path
    while True:
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            missing.append(current)
            current = current.parent
            continue
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise QualificationRefusal("HL1R1-Q-PATH")
        break
    for candidate in reversed(missing):
        os.mkdir(candidate, 0o700)
        info = os.lstat(candidate)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise QualificationRefusal("HL1R1-Q-PATH")


def _write_no_replace(path: Path, payload: bytes, *, mode: int) -> None:
    if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
        raise QualificationRefusal("HL1R1-Q-OUTPUT")
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            mode,
        )
    except OSError as exc:
        raise QualificationRefusal("HL1R1-Q-OUTPUT") from exc
    try:
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("write made no progress")
            offset += written
        os.fsync(descriptor)
    except OSError as exc:
        raise QualificationRefusal("HL1R1-Q-OUTPUT") from exc
    finally:
        os.close(descriptor)


def _result_payload(result: dict[str, Any]) -> bytes:
    previous = -1
    for _ in range(8):
        payload = _canonical_bytes(result)
        result["measurements"]["public_result_bytes"] = len(payload)
        result["measurements"]["generated_output_bytes"] = (
            result["measurements"]["generated_temporary_and_marker_bytes"]
            + len(payload)
        )
        result["measurements"]["generated_input_plus_output_bytes"] = (
            result["measurements"]["generated_fixture_input_bytes"]
            + result["measurements"]["generated_output_bytes"]
        )
        if len(payload) == previous:
            validate_result(result)
            return _canonical_bytes(result)
        previous = len(payload)
    raise QualificationRefusal("HL1R1-Q-OUTPUT")


def _result(
    *,
    status: str,
    matrix: Mapping[str, Any] | None,
    runtime: float,
    peak_rss: int,
    generated_output_bytes: int,
    allocated_bytes: int,
    free_before: int,
    free_after: int,
) -> dict[str, Any]:
    fixture_bytes = int(matrix["generated_fixture_input_bytes"]) if matrix else 0
    return {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_qualification_result",
        "schema_version": SCHEMA_VERSION,
        "qualification_id": QUALIFICATION_ID,
        "packet_id": recovery.PACKET_ID,
        "lane_id": recovery.LANE_ID,
        "status": status,
        "decision_proof": {
            "decision_id": DECISION_ID,
            "decision_commit": DECISION_COMMIT,
            "decision_CI_run_id": DECISION_CI_RUN_ID,
            "decision_base_python_job_id": DECISION_BASE_JOB_ID,
            "decision_optional_neuro_readers_job_id": DECISION_OPTIONAL_JOB_ID,
            "decision_sha256": DECISION_SHA256,
        },
        "matrix": dict(matrix) if matrix else None,
        "measurements": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 0,
            "runtime_seconds": runtime,
            "runtime_seconds_maximum": MAX_RUNTIME_SECONDS,
            "peak_process_tree_RSS_bytes": peak_rss,
            "peak_process_tree_RSS_bytes_maximum": MAX_PEAK_RSS_BYTES,
            "generated_fixture_input_bytes": fixture_bytes,
            "generated_temporary_and_marker_bytes": generated_output_bytes,
            "generated_output_bytes": generated_output_bytes,
            "generated_input_plus_output_bytes": fixture_bytes + generated_output_bytes,
            "generated_input_plus_output_bytes_maximum": MAX_GENERATED_IO_BYTES,
            "incremental_temporary_allocated_bytes": allocated_bytes,
            "incremental_temporary_disk_bytes_maximum": MAX_INCREMENTAL_DISK_BYTES,
            "free_disk_bytes_before": free_before,
            "free_disk_bytes_after": free_after,
            "public_result_bytes": 0,
            "public_result_bytes_maximum": MAX_PUBLIC_OUTPUT_BYTES,
            "producer_causal": None,
            "required_context_seconds": None,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": {
            "registered_qualification_attempts": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "real_or_private_path_operations": 0,
            "HTTP_requests": 0,
            "network_bytes": 0,
            "real_EDF_payload_or_header_reads": 0,
            "annotation_signal_target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "model_inference_runs": 0,
            "prediction_sets": 0,
            "target_deliveries": 0,
            "score_operations": 0,
            "provider_calls": 0,
            "stream_device_or_hardware_operations": 0,
            "release_operations": 0,
            "scientific_claim_upgrades": 0,
        },
        "warnings": [
            "generated_qualification_has_no_scientific_value",
            "real_Dreyer_EDF_remains_closed",
            "producer_causality_unavailable",
            "required_context_unavailable",
            "end_to_end_latency_not_measured",
        ],
        "claim_boundary": {
            "engineering_capability": "generated_recovery_wrapper_full_matrix_qualification",
            "scientific_claim_established": False,
            "scientific_claim_not_established": "real_EEG_neural_decoding_unseen_person_peripheral_adjusted_live_hardware_or_clinical_result",
        },
    }


def validate_result(result: Mapping[str, Any]) -> None:
    """Strictly validate an aggregate target-free qualification result."""

    if (
        set(result) != RESULT_KEYS
        or result.get("schema_version") != SCHEMA_VERSION
        or result.get("qualification_id") != QUALIFICATION_ID
        or result.get("packet_id") != recovery.PACKET_ID
        or result.get("status")
        not in {"passed_generated_only", "failed_consumed_generated_only"}
    ):
        raise QualificationRefusal("HL1R1-Q-RESULT")
    measurements = result.get("measurements")
    counters = result.get("operation_counters")
    if not isinstance(measurements, Mapping) or not isinstance(counters, Mapping):
        raise QualificationRefusal("HL1R1-Q-RESULT")
    numeric = (
        "runtime_seconds",
        "peak_process_tree_RSS_bytes",
        "generated_fixture_input_bytes",
        "generated_temporary_and_marker_bytes",
        "generated_output_bytes",
        "generated_input_plus_output_bytes",
        "incremental_temporary_allocated_bytes",
        "public_result_bytes",
    )
    if any(
        not isinstance(measurements.get(key), (int, float))
        or not math.isfinite(float(measurements[key]))
        or float(measurements[key]) < 0
        for key in numeric
    ):
        raise QualificationRefusal("HL1R1-Q-RESULT")
    if (
        measurements["public_result_bytes"] > MAX_PUBLIC_OUTPUT_BYTES
        or counters.get("registered_qualification_attempts") != 1
        or any(
            value != 0
            for key, value in counters.items()
            if key != "registered_qualification_attempts"
        )
    ):
        raise QualificationRefusal("HL1R1-Q-RESULT")
    matrix = result.get("matrix")
    if result["status"] == "passed_generated_only":
        if (
            not isinstance(matrix, Mapping)
            or matrix.get("total_cases") != 65
            or measurements["runtime_seconds"] > MAX_RUNTIME_SECONDS
            or measurements["peak_process_tree_RSS_bytes"] > MAX_PEAK_RSS_BYTES
            or measurements["generated_input_plus_output_bytes"]
            > MAX_GENERATED_IO_BYTES
            or measurements["incremental_temporary_allocated_bytes"]
            > MAX_INCREMENTAL_DISK_BYTES
        ):
            raise QualificationRefusal("HL1R1-Q-RESULT")
    elif matrix is not None and (
        not isinstance(matrix, Mapping) or matrix.get("total_cases") != 65
    ):
        raise QualificationRefusal("HL1R1-Q-RESULT")


def run_official_qualification(
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
) -> dict[str, Any]:
    """Consume and run the sole registered generated-only qualification."""

    repository = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(repository)
    _ensure_thread_caps(os.environ if environ is None else environ)
    qualification_root = repository / QUALIFICATION_RELATIVE_ROOT
    _ensure_directory(qualification_root)
    marker_path = qualification_root / CONSUMED_MARKER_NAME
    output_path = qualification_root / RESULT_NAME
    if marker_path.exists() or marker_path.is_symlink():
        raise QualificationRefusal("HL1R1-Q-CONSUMED")
    if output_path.exists() or output_path.is_symlink():
        raise QualificationRefusal("HL1R1-Q-OUTPUT")
    free_before = int(disk_usage_reader(repository).free)
    if free_before < MINIMUM_FREE_DISK_BYTES:
        raise QualificationRefusal("HL1R1-Q-RESOURCE")
    marker = {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_qualification_consumed",
        "schema_version": SCHEMA_VERSION,
        "qualification_id": QUALIFICATION_ID,
        "attempt_consumed": True,
        "rerun_retry_resume_repair_substitution_or_amendment_allowed": False,
    }
    marker_payload = _canonical_bytes(marker)
    _write_no_replace(marker_path, marker_payload, mode=0o600)
    marker_info = os.lstat(marker_path)
    marker_allocated_bytes = (
        int(getattr(marker_info, "st_blocks", 0)) * 512 or marker_info.st_size
    )

    started = float(clock())
    matrix: dict[str, Any] | None = None
    status = "failed_consumed_generated_only"
    generated_output_bytes = 0
    allocated_bytes = 0
    try:
        with tempfile.TemporaryDirectory(
            prefix="matrix-", dir=qualification_root
        ) as temporary:
            matrix = run_development_matrix(temporary, repo_root=repository)
            generated_output_bytes, allocated_bytes = _tree_sizes(Path(temporary))
            generated_output_bytes += len(marker_payload)
            allocated_bytes += marker_allocated_bytes
        status = "passed_generated_only"
    except Exception:  # noqa: BLE001 - the consumed boundary emits no exception detail
        matrix = None
    runtime = float(clock()) - started
    peak_rss = int(rss_reader())
    free_after = int(disk_usage_reader(repository).free)
    result = _result(
        status=status,
        matrix=matrix,
        runtime=runtime,
        peak_rss=peak_rss,
        generated_output_bytes=generated_output_bytes,
        allocated_bytes=allocated_bytes,
        free_before=free_before,
        free_after=free_after,
    )
    if (
        not math.isfinite(runtime)
        or runtime < 0
        or runtime > MAX_RUNTIME_SECONDS
        or peak_rss < 0
        or peak_rss > MAX_PEAK_RSS_BYTES
        or free_after < MINIMUM_FREE_DISK_BYTES
        or allocated_bytes > MAX_INCREMENTAL_DISK_BYTES
        or result["measurements"]["generated_input_plus_output_bytes"]
        > MAX_GENERATED_IO_BYTES
    ):
        result = _result(
            status="failed_consumed_generated_only",
            matrix=matrix,
            runtime=max(0.0, runtime),
            peak_rss=max(0, peak_rss),
            generated_output_bytes=generated_output_bytes,
            allocated_bytes=allocated_bytes,
            free_before=max(0, free_before),
            free_after=max(0, free_after),
        )
    payload = _result_payload(result)
    _write_no_replace(output_path, payload, mode=0o600)
    return result


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact generated-only qualification plan."""

    load_green_decision(repo_root)
    return {
        "qualification_id": QUALIFICATION_ID,
        "status": "authorized_after_exact_coordinator_remote_green",
        "total_cases": EXPECTED_TOTAL_CASES,
        "valid_H1_replays": EXPECTED_VALID_H1_REPLAYS,
        "inherited_stage_H_valid_cases": EXPECTED_INHERITED_VALID_CASES,
        "inherited_stage_H_refusals": EXPECTED_INHERITED_REFUSALS,
        "ordered_successor_refusals": EXPECTED_SUCCESSOR_REFUSALS,
        "registered_attempts_maximum": 1,
        "real_command_available": False,
        "network_allowed": False,
        "HL2_authority": False,
        "real_EDF_authority": False,
    }


def inspect_result(path: str | Path) -> dict[str, Any]:
    """Strictly inspect one aggregate generated-only qualification result."""

    candidate = Path(path).expanduser().absolute()
    try:
        payload = _read_regular_file(candidate, byte_cap=MAX_PUBLIC_OUTPUT_BYTES)
        result = _strict_json(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise QualificationRefusal("HL1R1-Q-RESULT") from exc
    if not isinstance(result, dict):
        raise QualificationRefusal("HL1R1-Q-RESULT")
    validate_result(result)
    return result
