"""Generated qualification and machine-only readiness for MARC2-VR4."""

from __future__ import annotations

import argparse
import copy
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
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR4"
MODULE_NAME = "neurodecodekit.datasets.marc2_machine_readiness"
CERTIFICATE_SCHEMA_NAME = "neurodecodekit.marc2_machine_readiness_certificate"
QUALIFICATION_SCHEMA_NAME = "neurodecodekit.marc2_machine_readiness_qualification"
PLAN_SCHEMA_NAME = "neurodecodekit.marc2_machine_readiness_plan"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_machine_stable_structural_recovery_contract.v0.json"
)
CONTRACT_SHA256 = "93d63b273809f05608aaa18f9a52611d6073110e74b3c62ae5cf08d756b6b191"
GREEN_REGISTRATION_COMMIT = "3af2e3d654b91c13aefce76e74b38ae19b2a3d6f"
GREEN_REGISTRATION_CI_RUN_ID = 31_965_823_863
GREEN_REGISTRATION_BASE_JOB_ID = 95_210_732_393
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_210_732_329
CERTIFICATE_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr4/readiness.v0.json"
)

THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
MAX_NORMALIZED_LOAD = 1.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
CONSECUTIVE_PASSING_SAMPLES = 3
MINIMUM_SAMPLE_INTERVAL_SECONDS = 5.0
MAXIMUM_WAIT_SECONDS = 600.0
MAXIMUM_SAMPLES = 121
CERTIFICATE_VALIDITY_SECONDS = 300
MAX_CERTIFICATE_BYTES = 64 * 1024
MAX_QUALIFICATION_RUNTIME_SECONDS = 30.0
MAX_INCREMENTAL_DISK_BYTES = 1024**2
SUCCESS_ROUTE = "MARC2RDY-G1"
REFUSAL_ROUTES = tuple(f"MARC2RDY-F{index:02d}" for index in range(6))

MUTATION_ROUTES = {
    "schema_name_wrong": REFUSAL_ROUTES[0],
    "schema_version_wrong": REFUSAL_ROUTES[0],
    "lane_id_wrong": REFUSAL_ROUTES[0],
    "green_research_proof_wrong": REFUSAL_ROUTES[0],
    "green_result_proof_wrong": REFUSAL_ROUTES[0],
    "command_surface_wrong": REFUSAL_ROUTES[0],
    "execute_command_enabled": REFUSAL_ROUTES[0],
    "private_path_constant_added": REFUSAL_ROUTES[0],
    "generic_override_added": REFUSAL_ROUTES[0],
    "consumed_executor_import_added": REFUSAL_ROUTES[0],
    "thread_environment_drift": REFUSAL_ROUTES[1],
    "logical_CPU_zero": REFUSAL_ROUTES[1],
    "normalized_load_nonfinite": REFUSAL_ROUTES[1],
    "normalized_load_above_threshold": REFUSAL_ROUTES[1],
    "RSS_negative": REFUSAL_ROUTES[1],
    "RSS_at_exclusive_threshold": REFUSAL_ROUTES[1],
    "disk_below_threshold": REFUSAL_ROUTES[1],
    "timestamp_regression": REFUSAL_ROUTES[2],
    "interval_below_five_seconds": REFUSAL_ROUTES[2],
    "fewer_than_three_consecutive_passes": REFUSAL_ROUTES[2],
    "sample_count_above_121": REFUSAL_ROUTES[2],
    "wait_above_600_seconds": REFUSAL_ROUTES[2],
    "certificate_schema_wrong": REFUSAL_ROUTES[3],
    "certificate_commit_wrong": REFUSAL_ROUTES[3],
    "certificate_contract_hash_wrong": REFUSAL_ROUTES[3],
    "certificate_expired": REFUSAL_ROUTES[3],
    "certificate_path_wrong": REFUSAL_ROUTES[4],
    "certificate_symlink": REFUSAL_ROUTES[4],
    "certificate_mode_wrong": REFUSAL_ROUTES[4],
    "certificate_output_cap_exceeded": REFUSAL_ROUTES[4],
    "private_counter_nonzero": REFUSAL_ROUTES[5],
    "network_counter_nonzero": REFUSAL_ROUTES[5],
    "archive_or_neural_counter_nonzero": REFUSAL_ROUTES[5],
    "model_target_or_score_counter_nonzero": REFUSAL_ROUTES[5],
    "generated_certificate_claims_authority": REFUSAL_ROUTES[5],
    "scientific_claim_upgrade": REFUSAL_ROUTES[5],
}
ORDERED_MUTATIONS = tuple(MUTATION_ROUTES)

SAMPLE_FIELDS = frozenset(
    {
        "sequence",
        "observed_at_UTC",
        "monotonic_seconds",
        "logical_CPUs",
        "one_minute_load",
        "normalized_one_minute_load",
        "process_peak_RSS_bytes",
        "free_disk_bytes",
        "thresholds",
        "checks",
        "passing",
        "refusal_reasons",
    }
)
THRESHOLDS = {
    "normalized_one_minute_load_maximum": MAX_NORMALIZED_LOAD,
    "process_peak_RSS_bytes_maximum_exclusive": MAX_PEAK_RSS_BYTES,
    "free_disk_bytes_minimum": MINIMUM_FREE_DISK_BYTES,
    "consecutive_passing_samples": CONSECUTIVE_PASSING_SAMPLES,
    "minimum_sample_interval_seconds": int(MINIMUM_SAMPLE_INTERVAL_SECONDS),
    "maximum_wait_seconds": int(MAXIMUM_WAIT_SECONDS),
    "maximum_samples": MAXIMUM_SAMPLES,
    "certificate_validity_seconds": CERTIFICATE_VALIDITY_SECONDS,
}
ZERO_SCIENTIFIC_COUNTERS = {
    "private_path_operations": 0,
    "private_content_opens": 0,
    "private_input_bytes": 0,
    "private_output_root_operations": 0,
    "network_requests": 0,
    "network_bytes": 0,
    "archive_member_reads": 0,
    "signal_sample_reads": 0,
    "event_target_label_onset_channel_or_geometry_reads": 0,
    "real_derivative_rows": 0,
    "training_or_parameter_update_fits": 0,
    "model_inference_or_prediction_sets": 0,
    "prediction_freezes_target_deliveries_or_scores": 0,
    "provider_or_language_model_calls": 0,
    "hardware_operations": 0,
    "scientific_claim_upgrades": 0,
    "operations_on_other_projects": 0,
}
CLAIM_BOUNDARY = {
    "engineering_capability_added": (
        "A deterministic machine-readiness certificate can be qualified without "
        "consuming a later private content open."
    ),
    "scientific_claim_not_established": (
        "No neural payload target prediction or score is accessed, so this result "
        "establishes no neural effect or decoding result."
    ),
}


class MachineReadinessRefusal(RuntimeError):
    """Fail closed with one stable, aggregate-safe VR4 refusal route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR4 refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MachineReadinessRefusal(
                REFUSAL_ROUTES[4], "certificate contains a duplicate JSON key"
            )
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise MachineReadinessRefusal(
        REFUSAL_ROUTES[4], "certificate contains a non-finite JSON number"
    )


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except MachineReadinessRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate JSON is invalid"
        ) from exc
    if not isinstance(value, dict):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate JSON root is not an object"
        )
    return value


def _parse_utc(value: Any, *, route: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MachineReadinessRefusal(route, "UTC timestamp is malformed")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise MachineReadinessRefusal(route, "UTC timestamp is malformed") from exc
    if parsed.tzinfo != timezone.utc:
        raise MachineReadinessRefusal(route, "UTC timestamp offset differs")
    return parsed


def _format_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _require_number(value: Any, name: str, *, route: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MachineReadinessRefusal(route, f"{name} is not numeric")
    result = float(value)
    if not math.isfinite(result):
        raise MachineReadinessRefusal(route, f"{name} is non-finite")
    return result


def _validate_registered_contract(contract: Mapping[str, Any]) -> None:
    try:
        surface = contract["implementation_surface"]
        readiness = contract["readiness_contract"]
        certificate = contract["certificate_schema"]
        predecessors = contract["green_predecessor_proof"]
        qualification = contract["generated_qualification"]
    except KeyError as exc:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract field is missing"
        ) from exc
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc2_machine_stable_structural_recovery_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract identity differs"
        )
    if (
        predecessors.get("machine_stable_research", {}).get("commit")
        != "4c0b0dc5acf56cff5089992a8bcd9954aa532fe5"
        or predecessors.get("machine_stable_research", {}).get("CI_run_id")
        != 31_965_424_149
        or predecessors.get("VR3_result", {}).get("commit")
        != "a186486fcb3dfb2b6d3a743f180b7ac2fa0b4dd3"
        or predecessors.get("VR3_result", {}).get("CI_run_id") != 31_964_995_980
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "green predecessor proof differs"
        )
    if (
        surface.get("module") != MODULE_NAME
        or surface.get("commands") != ["plan", "qualify", "inspect", "readiness"]
        or surface.get("execute_command") is not False
        or surface.get("private_source_or_private_output_root_constant") is not False
        or surface.get("generic_path_root_threshold_interval_count_wait_or_cap_override")
        is not False
        or surface.get("old_consumed_executor_import_call_copy_edit_or_alias") is not False
        or surface.get("network_archive_neural_target_model_prediction_or_score_interface")
        is not False
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered command or authority surface differs"
        )
    if (
        readiness.get("thread_environment") != {key: "1" for key in THREAD_ENVIRONMENT}
        or readiness.get("logical_CPUs_minimum") != 1
        or readiness.get("normalized_one_minute_load_maximum") != MAX_NORMALIZED_LOAD
        or readiness.get("process_peak_RSS_bytes_maximum_exclusive")
        != MAX_PEAK_RSS_BYTES
        or readiness.get("free_disk_bytes_minimum") != MINIMUM_FREE_DISK_BYTES
        or readiness.get("consecutive_passing_samples")
        != CONSECUTIVE_PASSING_SAMPLES
        or readiness.get("minimum_sample_interval_seconds")
        != MINIMUM_SAMPLE_INTERVAL_SECONDS
        or readiness.get("maximum_wait_seconds") != MAXIMUM_WAIT_SECONDS
        or readiness.get("maximum_samples") != MAXIMUM_SAMPLES
        or readiness.get("certificate_validity_seconds")
        != CERTIFICATE_VALIDITY_SECONDS
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered readiness threshold differs"
        )
    if (
        certificate.get("schema_name") != CERTIFICATE_SCHEMA_NAME
        or certificate.get("schema_version") != SCHEMA_VERSION
        or certificate.get("mode") != "0600"
        or certificate.get("maximum_bytes") != MAX_CERTIFICATE_BYTES
        or surface.get("fixed_certificate_path") != CERTIFICATE_RELATIVE_PATH.as_posix()
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered certificate surface differs"
        )
    if (
        qualification.get("ordered_mutations") != list(ORDERED_MUTATIONS)
        or qualification.get("mutation_count") != len(ORDERED_MUTATIONS)
        or qualification.get("success_route") != SUCCESS_ROUTE
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered qualification matrix differs"
        )
    if any(contract.get("authorization_state", {}).values()):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered authority is nonzero"
        )


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR4 generated-only contract."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    try:
        info = path.lstat()
    except OSError as exc:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract path shape differs"
        )
    if _sha256_file(path) != CONTRACT_SHA256:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    contract = _strict_json(path.read_bytes())
    _validate_registered_contract(contract)
    return contract


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _thread_environment(environ: Mapping[str, str]) -> dict[str, str | None]:
    return {key: environ.get(key) for key in THREAD_ENVIRONMENT}


def _thread_environment_passes(values: Mapping[str, Any]) -> bool:
    return values == {key: "1" for key in THREAD_ENVIRONMENT}


def _raw_machine_sample(
    *,
    sequence: int,
    observed_at: datetime,
    monotonic_seconds: float,
    logical_cpus: int | None,
    one_minute_load: float,
    peak_rss_bytes: int,
    free_disk_bytes: int,
) -> dict[str, Any]:
    if logical_cpus is None:
        normalized = None
    elif logical_cpus > 0:
        normalized = one_minute_load / logical_cpus
    else:
        normalized = 0.0
    return {
        "sequence": sequence,
        "observed_at_UTC": _format_utc(observed_at),
        "monotonic_seconds": monotonic_seconds,
        "logical_CPUs": logical_cpus,
        "one_minute_load": one_minute_load,
        "normalized_one_minute_load": normalized,
        "process_peak_RSS_bytes": peak_rss_bytes,
        "free_disk_bytes": free_disk_bytes,
    }


def _assess_raw_sample(raw: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "sequence",
        "observed_at_UTC",
        "monotonic_seconds",
        "logical_CPUs",
        "one_minute_load",
        "normalized_one_minute_load",
        "process_peak_RSS_bytes",
        "free_disk_bytes",
    }
    if set(raw) != required:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "machine sample fields differ"
        )
    sequence = raw["sequence"]
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "sample sequence is invalid"
        )
    _parse_utc(raw["observed_at_UTC"], route=REFUSAL_ROUTES[2])
    monotonic = _require_number(
        raw["monotonic_seconds"], "monotonic seconds", route=REFUSAL_ROUTES[2]
    )
    if monotonic < 0:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "monotonic seconds is negative"
        )
    logical_cpus = raw["logical_CPUs"]
    if (
        isinstance(logical_cpus, bool)
        or not isinstance(logical_cpus, int)
        or logical_cpus < 1
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "logical CPU count is unavailable"
        )
    load = _require_number(
        raw["one_minute_load"], "one-minute load", route=REFUSAL_ROUTES[1]
    )
    normalized = _require_number(
        raw["normalized_one_minute_load"],
        "normalized one-minute load",
        route=REFUSAL_ROUTES[1],
    )
    rss = _require_number(
        raw["process_peak_RSS_bytes"], "process peak RSS", route=REFUSAL_ROUTES[1]
    )
    disk = _require_number(
        raw["free_disk_bytes"], "free disk bytes", route=REFUSAL_ROUTES[1]
    )
    if load < 0 or normalized < 0 or rss < 0 or disk < 0:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "machine measurement is negative"
        )
    if not math.isclose(normalized, load / logical_cpus, rel_tol=0.0, abs_tol=1e-12):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "normalized load arithmetic differs"
        )
    checks = {
        "logical_CPUs_at_least_one": logical_cpus >= 1,
        "normalized_load_at_or_below_maximum": normalized <= MAX_NORMALIZED_LOAD,
        "peak_RSS_below_exclusive_maximum": rss < MAX_PEAK_RSS_BYTES,
        "free_disk_at_or_above_minimum": disk >= MINIMUM_FREE_DISK_BYTES,
    }
    reasons: list[str] = []
    if not checks["normalized_load_at_or_below_maximum"]:
        reasons.append(
            f"normalized_one_minute_load={normalized!r} exceeds maximum={MAX_NORMALIZED_LOAD!r}"
        )
    if not checks["peak_RSS_below_exclusive_maximum"]:
        reasons.append(
            f"process_peak_RSS_bytes={int(rss)} is not below maximum_exclusive={MAX_PEAK_RSS_BYTES}"
        )
    if not checks["free_disk_at_or_above_minimum"]:
        reasons.append(
            f"free_disk_bytes={int(disk)} is below minimum={MINIMUM_FREE_DISK_BYTES}"
        )
    return {
        **raw,
        "thresholds": {
            "logical_CPUs_minimum": 1,
            "normalized_one_minute_load_maximum": MAX_NORMALIZED_LOAD,
            "process_peak_RSS_bytes_maximum_exclusive": MAX_PEAK_RSS_BYTES,
            "free_disk_bytes_minimum": MINIMUM_FREE_DISK_BYTES,
        },
        "checks": checks,
        "passing": all(checks.values()),
        "refusal_reasons": reasons,
    }


def _validate_sample_sequence(samples: Sequence[Mapping[str, Any]]) -> None:
    if not samples or len(samples) > MAXIMUM_SAMPLES:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "sample count is outside the registered range"
        )
    previous_utc: datetime | None = None
    previous_monotonic: float | None = None
    for index, sample in enumerate(samples, start=1):
        if sample.get("sequence") != index:
            raise MachineReadinessRefusal(
                REFUSAL_ROUTES[2], "sample sequence is not contiguous"
            )
        observed = _parse_utc(sample.get("observed_at_UTC"), route=REFUSAL_ROUTES[2])
        monotonic = _require_number(
            sample.get("monotonic_seconds"),
            "monotonic seconds",
            route=REFUSAL_ROUTES[2],
        )
        if previous_utc is not None:
            if observed <= previous_utc or monotonic <= previous_monotonic:  # type: ignore[operator]
                raise MachineReadinessRefusal(
                    REFUSAL_ROUTES[2], "sample timestamp regressed"
                )
            if (
                (observed - previous_utc).total_seconds()
                < MINIMUM_SAMPLE_INTERVAL_SECONDS
                or monotonic - previous_monotonic  # type: ignore[operator]
                < MINIMUM_SAMPLE_INTERVAL_SECONDS
            ):
                raise MachineReadinessRefusal(
                    REFUSAL_ROUTES[2], "sample interval is below five seconds"
                )
        previous_utc = observed
        previous_monotonic = monotonic


def _passing_tail(samples: Sequence[Mapping[str, Any]]) -> int:
    count = 0
    for sample in reversed(samples):
        if sample.get("passing") is not True:
            break
        count += 1
    return count


def _certificate_access_counters(sample_count: int) -> dict[str, int]:
    return {
        "machine_readiness_checks": sample_count,
        "readiness_certificates": 1,
        **ZERO_SCIENTIFIC_COUNTERS,
    }


def build_certificate(
    raw_samples: Sequence[Mapping[str, Any]],
    *,
    implementation_commit: str,
    thread_environment: Mapping[str, str | None],
    proof_posture: str,
    certificate_path: str,
) -> dict[str, Any]:
    """Build one canonical certificate from generated or current-machine samples."""

    samples = [_assess_raw_sample(sample) for sample in raw_samples]
    _validate_sample_sequence(samples)
    started = _parse_utc(samples[0]["observed_at_UTC"], route=REFUSAL_ROUTES[2])
    finished = _parse_utc(samples[-1]["observed_at_UTC"], route=REFUSAL_ROUTES[2])
    wait_seconds = samples[-1]["monotonic_seconds"] - samples[0]["monotonic_seconds"]
    if wait_seconds > MAXIMUM_WAIT_SECONDS:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "readiness wait exceeds 600 seconds"
        )
    threads_pass = _thread_environment_passes(thread_environment)
    tail = _passing_tail(samples)
    ready = threads_pass and tail >= CONSECUTIVE_PASSING_SAMPLES
    route = SUCCESS_ROUTE if ready else (
        REFUSAL_ROUTES[1] if not threads_pass else REFUSAL_ROUTES[2]
    )
    refusal_reasons: list[str] = []
    if not threads_pass:
        refusal_reasons.append(
            "thread_environment="
            + json.dumps(dict(thread_environment), sort_keys=True, separators=(",", ":"))
            + " differs from required all-one environment"
        )
    if tail < CONSECUTIVE_PASSING_SAMPLES:
        refusal_reasons.append(
            f"consecutive_passing_samples={tail} is below required={CONSECUTIVE_PASSING_SAMPLES}"
        )
        refusal_reasons.extend(samples[-1]["refusal_reasons"])
    expires = finished + timedelta(seconds=CERTIFICATE_VALIDITY_SECONDS)
    certificate = {
        "schema_name": CERTIFICATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "ready" if ready else "not_ready",
        "ready": ready,
        "route": route,
        "proof_posture": proof_posture,
        "certificate_path": certificate_path,
        "implementation_commit": implementation_commit,
        "contract_sha256": CONTRACT_SHA256,
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "started_at_UTC": _format_utc(started),
        "finished_at_UTC": _format_utc(finished),
        "expires_at_UTC": _format_utc(expires),
        "thresholds": copy.deepcopy(THRESHOLDS),
        "samples": samples,
        "measurements": {
            "sample_count": len(samples),
            "consecutive_passing_tail": tail,
            "wait_seconds": wait_seconds,
            "thread_environment": dict(thread_environment),
            "refusal_reasons": refusal_reasons,
        },
        "access_counters": _certificate_access_counters(len(samples)),
        "warnings": [
            "This certificate describes machine state only.",
            "A generated ready certificate grants no private-data authority.",
            "A later private executor requires a separate Tier C decision.",
        ],
        "unavailable_fields": [
            "private_source_path",
            "cohort_identity",
            "archive_member_identity",
            "neural_payload",
            "event_or_target",
            "model_or_prediction",
            "scientific_score",
        ],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    validate_certificate(certificate, allow_not_ready=True)
    if len(_canonical_json_bytes(certificate)) > MAX_CERTIFICATE_BYTES:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate exceeds 64 KiB"
        )
    return certificate


def validate_certificate(
    certificate: Mapping[str, Any],
    *,
    allow_not_ready: bool = False,
    now_UTC: datetime | None = None,
) -> None:
    """Validate certificate identity, samples, counters, expiry, and claim boundary."""

    required = {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "ready",
        "route",
        "proof_posture",
        "certificate_path",
        "implementation_commit",
        "contract_sha256",
        "green_registration",
        "started_at_UTC",
        "finished_at_UTC",
        "expires_at_UTC",
        "thresholds",
        "samples",
        "measurements",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    if set(certificate) != required:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate fields differ"
        )
    if (
        certificate.get("schema_name") != CERTIFICATE_SCHEMA_NAME
        or certificate.get("schema_version") != SCHEMA_VERSION
        or certificate.get("lane_id") != LANE_ID
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate schema identity differs"
        )
    commit = certificate.get("implementation_commit")
    if (
        not isinstance(commit, str)
        or len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate implementation commit differs"
        )
    if certificate.get("contract_sha256") != CONTRACT_SHA256:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate contract hash differs"
        )
    if certificate.get("thresholds") != THRESHOLDS:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate thresholds differ"
        )
    proof = certificate.get("green_registration")
    if proof != {
        "commit": GREEN_REGISTRATION_COMMIT,
        "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
        "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
        "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
    }:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate green registration proof differs"
        )
    samples = certificate.get("samples")
    if not isinstance(samples, list):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "certificate samples are not a list"
        )
    reassessed: list[dict[str, Any]] = []
    for sample in samples:
        if not isinstance(sample, Mapping) or set(sample) != SAMPLE_FIELDS:
            raise MachineReadinessRefusal(
                REFUSAL_ROUTES[1], "assessed sample fields differ"
            )
        raw = {key: sample[key] for key in SAMPLE_FIELDS if key not in {
            "thresholds", "checks", "passing", "refusal_reasons"
        }}
        expected = _assess_raw_sample(raw)
        if dict(sample) != expected:
            raise MachineReadinessRefusal(
                REFUSAL_ROUTES[1], "assessed sample values differ"
            )
        reassessed.append(expected)
    _validate_sample_sequence(reassessed)
    started = _parse_utc(certificate.get("started_at_UTC"), route=REFUSAL_ROUTES[2])
    finished = _parse_utc(certificate.get("finished_at_UTC"), route=REFUSAL_ROUTES[2])
    expires = _parse_utc(certificate.get("expires_at_UTC"), route=REFUSAL_ROUTES[3])
    sample_started = _parse_utc(reassessed[0]["observed_at_UTC"], route=REFUSAL_ROUTES[2])
    sample_finished = _parse_utc(reassessed[-1]["observed_at_UTC"], route=REFUSAL_ROUTES[2])
    if started != sample_started or finished != sample_finished:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "certificate sample time binding differs"
        )
    if expires != finished + timedelta(seconds=CERTIFICATE_VALIDITY_SECONDS):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate expiry interval differs"
        )
    measurements = certificate.get("measurements")
    if not isinstance(measurements, Mapping):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "certificate measurements differ"
        )
    thread_values = measurements.get("thread_environment")
    if not isinstance(thread_values, Mapping):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "thread environment is unavailable"
        )
    thread_pass = _thread_environment_passes(thread_values)
    if not thread_pass and certificate.get("ready") is True:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "thread environment differs from the all-one requirement"
        )
    tail = _passing_tail(reassessed)
    wait_seconds = reassessed[-1]["monotonic_seconds"] - reassessed[0]["monotonic_seconds"]
    if wait_seconds > MAXIMUM_WAIT_SECONDS:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "readiness wait exceeds 600 seconds"
        )
    if (
        measurements.get("sample_count") != len(reassessed)
        or measurements.get("consecutive_passing_tail") != tail
        or measurements.get("wait_seconds") != wait_seconds
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "certificate sequence measurements differ"
        )
    expected_ready = thread_pass and tail >= CONSECUTIVE_PASSING_SAMPLES
    if (
        certificate.get("ready") is not expected_ready
        or certificate.get("status") != ("ready" if expected_ready else "not_ready")
        or certificate.get("route")
        != (SUCCESS_ROUTE if expected_ready else (
            REFUSAL_ROUTES[1] if not thread_pass else REFUSAL_ROUTES[2]
        ))
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "certificate readiness outcome differs"
        )
    if not expected_ready and not allow_not_ready:
        raise MachineReadinessRefusal(
            certificate["route"], "certificate is not ready"
        )
    if now_UTC is not None and now_UTC.astimezone(timezone.utc) > expires:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "certificate is expired"
        )
    if certificate.get("proof_posture") not in {
        "generated_only_non_authoritative",
        "machine_only_non_scientific",
    }:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "certificate claims unregistered authority"
        )
    expected_path = (
        "<generated-fixture>"
        if certificate.get("proof_posture") == "generated_only_non_authoritative"
        else CERTIFICATE_RELATIVE_PATH.as_posix()
    )
    if certificate.get("certificate_path") != expected_path:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate path binding differs"
        )
    counters = certificate.get("access_counters")
    if counters != _certificate_access_counters(len(reassessed)):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "certificate access counter differs"
        )
    if certificate.get("claim_boundary") != CLAIM_BOUNDARY:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "certificate scientific claim boundary differs"
        )


def inspect_certificate_file(
    path: str | Path,
    *,
    now_UTC: datetime | None = None,
) -> dict[str, Any]:
    """Inspect one generated certificate file under strict file controls."""

    certificate_path = Path(path)
    try:
        info = certificate_path.lstat()
    except OSError as exc:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate file is unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate file is a symlink or nonregular"
        )
    if stat.S_IMODE(info.st_mode) != 0o600:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate mode differs from 0600"
        )
    if info.st_size > MAX_CERTIFICATE_BYTES:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate exceeds 64 KiB"
        )
    payload = certificate_path.read_bytes()
    if len(payload) != info.st_size:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate size changed during read"
        )
    certificate = _strict_json(payload)
    if _canonical_json_bytes(certificate) != payload:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate bytes are not canonical"
        )
    if certificate.get("proof_posture") != "generated_only_non_authoritative":
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "inspect accepts generated certificates only"
        )
    validate_certificate(certificate, now_UTC=now_UTC)
    return certificate


def _write_fixed_certificate(repo_root: Path, certificate: Mapping[str, Any]) -> int:
    if certificate.get("proof_posture") != "machine_only_non_scientific":
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "fixed writer accepts machine-only certificates"
        )
    payload = _canonical_json_bytes(certificate)
    if len(payload) > MAX_CERTIFICATE_BYTES:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate exceeds 64 KiB"
        )
    destination = repo_root / CERTIFICATE_RELATIVE_PATH
    current = repo_root
    for component in CERTIFICATE_RELATIVE_PATH.parts[:-1]:
        current = current / component
        if current.exists() or current.is_symlink():
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise MachineReadinessRefusal(
                    REFUSAL_ROUTES[4], "certificate parent path shape differs"
                )
        else:
            current.mkdir(mode=0o700)
    if destination.exists() or destination.is_symlink():
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate overwrite is refused"
        )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(destination, flags, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "certificate write refused"
        ) from exc
    info = destination.lstat()
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o600
        or info.st_size != len(payload)
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "written certificate shape differs"
        )
    return len(payload)


def _resolve_head_commit(repo_root: Path) -> str:
    git_entry = repo_root / ".git"
    if git_entry.is_dir():
        git_dir = git_entry
    elif git_entry.is_file() and not git_entry.is_symlink():
        line = git_entry.read_text(encoding="ascii").strip()
        if not line.startswith("gitdir: "):
            raise MachineReadinessRefusal(
                REFUSAL_ROUTES[3], "Git directory pointer differs"
            )
        git_dir = (repo_root / line[8:]).resolve()
    else:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "Git directory is unavailable"
        )
    head = (git_dir / "HEAD").read_text(encoding="ascii").strip()
    if head.startswith("ref: "):
        ref = head[5:]
        ref_path = git_dir / ref
        if ref_path.is_file() and not ref_path.is_symlink():
            commit = ref_path.read_text(encoding="ascii").strip()
        else:
            commit = ""
            packed = git_dir / "packed-refs"
            if packed.is_file() and not packed.is_symlink():
                for line in packed.read_text(encoding="ascii").splitlines():
                    if line.startswith(("#", "^")):
                        continue
                    parts = line.split(" ", 1)
                    if len(parts) == 2 and parts[1] == ref:
                        commit = parts[0]
                        break
    else:
        commit = head
    if (
        len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[3], "Git HEAD commit is unavailable"
        )
    return commit


def _observe_machine(repo_root: Path, sequence: int) -> dict[str, Any]:
    try:
        one_minute_load = os.getloadavg()[0]
    except (AttributeError, OSError) as exc:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[1], "one-minute load is unavailable"
        ) from exc
    return _raw_machine_sample(
        sequence=sequence,
        observed_at=datetime.now(timezone.utc),
        monotonic_seconds=time.monotonic(),
        logical_cpus=os.cpu_count(),
        one_minute_load=one_minute_load,
        peak_rss_bytes=_peak_rss_bytes(),
        free_disk_bytes=shutil.disk_usage(repo_root).free,
    )


def run_readiness(
    *,
    repo_root: str | Path | None = None,
    sampler: Callable[[Path, int], Mapping[str, Any]] = _observe_machine,
    sleeper: Callable[[float], None] = time.sleep,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Measure the current machine and write one fixed, non-scientific certificate."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_registered_contract(root)
    implementation_commit = _resolve_head_commit(root)
    thread_values = _thread_environment(os.environ if environ is None else environ)
    raw_samples: list[Mapping[str, Any]] = []
    first_monotonic: float | None = None
    while len(raw_samples) < MAXIMUM_SAMPLES:
        sample = dict(sampler(root, len(raw_samples) + 1))
        _assess_raw_sample(sample)
        raw_samples.append(sample)
        if first_monotonic is None:
            first_monotonic = float(sample["monotonic_seconds"])
        if _thread_environment_passes(thread_values):
            assessed_samples = [_assess_raw_sample(item) for item in raw_samples]
            if _passing_tail(assessed_samples) >= CONSECUTIVE_PASSING_SAMPLES:
                break
        elapsed = float(sample["monotonic_seconds"]) - first_monotonic
        if elapsed >= MAXIMUM_WAIT_SECONDS:
            break
        if not _thread_environment_passes(thread_values):
            break
        sleeper(MINIMUM_SAMPLE_INTERVAL_SECONDS)
    certificate = build_certificate(
        raw_samples,
        implementation_commit=implementation_commit,
        thread_environment=thread_values,
        proof_posture="machine_only_non_scientific",
        certificate_path=CERTIFICATE_RELATIVE_PATH.as_posix(),
    )
    _write_fixed_certificate(root, certificate)
    return certificate


def _generated_samples(kind: str) -> list[dict[str, Any]]:
    base = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
    load_values = {
        "three_pass": [0.5, 0.5, 0.5],
        "recover": [8.0, 0.5, 0.5, 0.5],
        "boundary": [4.0, 4.0, 4.0],
        "timeout": [8.0, 0.5, 8.0],
    }[kind]
    records: list[dict[str, Any]] = []
    for index, load in enumerate(load_values):
        boundary = kind == "boundary"
        records.append(
            _raw_machine_sample(
                sequence=index + 1,
                observed_at=base + timedelta(seconds=5 * index),
                monotonic_seconds=100.0 + 5 * index,
                logical_cpus=4,
                one_minute_load=load,
                peak_rss_bytes=(MAX_PEAK_RSS_BYTES - 1) if boundary else 32 * 1024**2,
                free_disk_bytes=MINIMUM_FREE_DISK_BYTES if boundary else 20 * 1024**3,
            )
        )
    return records


def _generated_certificate(kind: str = "three_pass") -> dict[str, Any]:
    return build_certificate(
        _generated_samples(kind),
        implementation_commit="a" * 40,
        thread_environment={key: "1" for key in THREAD_ENVIRONMENT},
        proof_posture="generated_only_non_authoritative",
        certificate_path="<generated-fixture>",
    )


def _expect_refusal(
    mutation: str,
    callback: Callable[[], Any],
) -> str:
    expected = MUTATION_ROUTES[mutation]
    try:
        callback()
    except MachineReadinessRefusal as exc:
        if exc.route != expected:
            raise MachineReadinessRefusal(
                REFUSAL_ROUTES[5],
                f"mutation {mutation} routed {exc.route} instead of {expected}",
            ) from exc
        return exc.route
    raise MachineReadinessRefusal(
        REFUSAL_ROUTES[5], f"mutation {mutation} was accepted"
    )


def _contract_mutation(contract: Mapping[str, Any], mutation: str) -> dict[str, Any]:
    value = copy.deepcopy(contract)
    if mutation == "schema_name_wrong":
        value["schema_name"] = "wrong"
    elif mutation == "schema_version_wrong":
        value["schema_version"] = "9.9.9"
    elif mutation == "lane_id_wrong":
        value["lane_id"] = "wrong"
    elif mutation == "green_research_proof_wrong":
        value["green_predecessor_proof"]["machine_stable_research"]["commit"] = "0" * 40
    elif mutation == "green_result_proof_wrong":
        value["green_predecessor_proof"]["VR3_result"]["commit"] = "0" * 40
    elif mutation == "command_surface_wrong":
        value["implementation_surface"]["commands"] = ["plan"]
    elif mutation == "execute_command_enabled":
        value["implementation_surface"]["execute_command"] = True
    elif mutation == "private_path_constant_added":
        value["implementation_surface"]["private_source_or_private_output_root_constant"] = True
    elif mutation == "generic_override_added":
        value["implementation_surface"][
            "generic_path_root_threshold_interval_count_wait_or_cap_override"
        ] = True
    elif mutation == "consumed_executor_import_added":
        value["implementation_surface"]["old_consumed_executor_import_call_copy_edit_or_alias"] = True
    else:
        raise ValueError("not a contract mutation")
    return value


def _certificate_mutation(certificate: Mapping[str, Any], mutation: str) -> dict[str, Any]:
    value = copy.deepcopy(certificate)
    if mutation == "thread_environment_drift":
        value["measurements"]["thread_environment"][THREAD_ENVIRONMENT[0]] = "2"
    elif mutation == "logical_CPU_zero":
        value["samples"][0]["logical_CPUs"] = 0
    elif mutation == "normalized_load_nonfinite":
        value["samples"][0]["normalized_one_minute_load"] = float("nan")
    elif mutation == "normalized_load_above_threshold":
        value["samples"][0]["one_minute_load"] = 8.0
        value["samples"][0]["normalized_one_minute_load"] = 2.0
    elif mutation == "RSS_negative":
        value["samples"][0]["process_peak_RSS_bytes"] = -1
    elif mutation == "RSS_at_exclusive_threshold":
        value["samples"][0]["process_peak_RSS_bytes"] = MAX_PEAK_RSS_BYTES
    elif mutation == "disk_below_threshold":
        value["samples"][0]["free_disk_bytes"] = MINIMUM_FREE_DISK_BYTES - 1
    elif mutation == "timestamp_regression":
        value["samples"][1]["observed_at_UTC"] = value["samples"][0]["observed_at_UTC"]
    elif mutation == "interval_below_five_seconds":
        first = _parse_utc(value["samples"][0]["observed_at_UTC"], route=REFUSAL_ROUTES[2])
        value["samples"][1]["observed_at_UTC"] = _format_utc(first + timedelta(seconds=4))
        value["samples"][1]["monotonic_seconds"] = value["samples"][0]["monotonic_seconds"] + 4
    elif mutation == "fewer_than_three_consecutive_passes":
        value["samples"] = value["samples"][:2]
    elif mutation == "sample_count_above_121":
        template = value["samples"][-1]
        value["samples"] = []
        base = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
        for index in range(MAXIMUM_SAMPLES + 1):
            sample = copy.deepcopy(template)
            sample["sequence"] = index + 1
            sample["observed_at_UTC"] = _format_utc(base + timedelta(seconds=5 * index))
            sample["monotonic_seconds"] = 100.0 + 5 * index
            value["samples"].append(sample)
    elif mutation == "wait_above_600_seconds":
        last = value["samples"][-1]
        first = _parse_utc(value["samples"][0]["observed_at_UTC"], route=REFUSAL_ROUTES[2])
        last["observed_at_UTC"] = _format_utc(first + timedelta(seconds=605))
        last["monotonic_seconds"] = value["samples"][0]["monotonic_seconds"] + 605
    elif mutation == "certificate_schema_wrong":
        value["schema_name"] = "wrong"
    elif mutation == "certificate_commit_wrong":
        value["implementation_commit"] = "not-a-commit"
    elif mutation == "certificate_contract_hash_wrong":
        value["contract_sha256"] = "0" * 64
    elif mutation == "certificate_path_wrong":
        value["certificate_path"] = "elsewhere.json"
    elif mutation == "private_counter_nonzero":
        value["access_counters"]["private_content_opens"] = 1
    elif mutation == "network_counter_nonzero":
        value["access_counters"]["network_requests"] = 1
    elif mutation == "archive_or_neural_counter_nonzero":
        value["access_counters"]["signal_sample_reads"] = 1
    elif mutation == "model_target_or_score_counter_nonzero":
        value["access_counters"]["training_or_parameter_update_fits"] = 1
    elif mutation == "generated_certificate_claims_authority":
        value["proof_posture"] = "private_authority"
    elif mutation == "scientific_claim_upgrade":
        value["claim_boundary"]["scientific_claim_not_established"] = "neural effect proven"
    else:
        raise ValueError("not an in-memory certificate mutation")
    return value


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run deterministic generated replay and all 36 frozen mutations."""

    started = clock()
    contract = load_registered_contract(repo_root)
    successes = {
        name: _generated_certificate(name)
        for name in ("three_pass", "recover", "boundary")
    }
    timeout_certificate = _generated_certificate("timeout")
    if timeout_certificate["ready"] is not False:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[2], "generated timeout unexpectedly became ready"
        )
    replay_a = _canonical_json_bytes(successes["three_pass"])
    replay_b = _canonical_json_bytes(_generated_certificate("three_pass"))
    if replay_a != replay_b:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "generated certificate replay differs"
        )
    mutation_routes: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="ndk-marc2-vr4-") as temp_dir:
        temp_root = Path(temp_dir)
        generated_path = temp_root / "readiness.v0.json"
        generated_path.write_bytes(replay_a)
        generated_path.chmod(0o600)
        inspected = inspect_certificate_file(
            generated_path,
            now_UTC=datetime(2026, 8, 16, 12, 1, tzinfo=timezone.utc),
        )
        if _canonical_json_bytes(inspected) != replay_a:
            raise MachineReadinessRefusal(
                REFUSAL_ROUTES[5], "generated certificate inspection replay differs"
            )
        for mutation in ORDERED_MUTATIONS:
            if mutation in {
                "schema_name_wrong",
                "schema_version_wrong",
                "lane_id_wrong",
                "green_research_proof_wrong",
                "green_result_proof_wrong",
                "command_surface_wrong",
                "execute_command_enabled",
                "private_path_constant_added",
                "generic_override_added",
                "consumed_executor_import_added",
            }:
                mutated_contract = _contract_mutation(contract, mutation)
                callback = partial(_validate_registered_contract, mutated_contract)
            elif mutation == "certificate_expired":
                callback = partial(
                    validate_certificate,
                    successes["three_pass"],
                    now_UTC=datetime(2026, 8, 16, 13, 0, tzinfo=timezone.utc),
                )
            elif mutation in {"certificate_symlink", "certificate_mode_wrong", "certificate_output_cap_exceeded"}:
                candidate = temp_root / f"{mutation}.json"
                if mutation == "certificate_symlink":
                    candidate.symlink_to(generated_path)
                elif mutation == "certificate_mode_wrong":
                    candidate.write_bytes(replay_a)
                    candidate.chmod(0o644)
                else:
                    candidate.write_bytes(b"x" * (MAX_CERTIFICATE_BYTES + 1))
                    candidate.chmod(0o600)
                callback = partial(inspect_certificate_file, candidate)
            else:
                mutated_certificate = _certificate_mutation(
                    successes["three_pass"], mutation
                )
                callback = partial(validate_certificate, mutated_certificate)
            mutation_routes[mutation] = _expect_refusal(mutation, callback)
        generated_input_bytes = sum(
            len(_canonical_json_bytes(value)) for value in successes.values()
        ) + len(_canonical_json_bytes(timeout_certificate))
    runtime_seconds = clock() - started
    peak_rss_bytes = int(rss_reader())
    if runtime_seconds > MAX_QUALIFICATION_RUNTIME_SECONDS:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "generated qualification runtime exceeds cap"
        )
    if peak_rss_bytes >= MAX_PEAK_RSS_BYTES:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[5], "generated qualification peak RSS reaches cap"
        )
    report = {
        "schema_name": QUALIFICATION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "passed",
        "route": SUCCESS_ROUTE,
        "proof_posture": "generated_and_machine_only_no_private_authority",
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "success_scenarios": {
            "count": 3,
            "names": ["three_immediate_passing_samples", "failure_then_recovery", "exact_boundaries"],
            "deterministic_replay": True,
            "timeout_ready": timeout_certificate["ready"],
        },
        "mutation_summary": {
            "count": len(mutation_routes),
            "ordered_names": list(mutation_routes),
            "routes": mutation_routes,
        },
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "generated_input_bytes": generated_input_bytes,
            "retained_generated_output_bytes": 0,
            "temporary_generated_output_removed": True,
        },
        "resource_caps": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds": MAX_QUALIFICATION_RUNTIME_SECONDS,
            "peak_RSS_bytes_exclusive": MAX_PEAK_RSS_BYTES,
            "certificate_bytes": MAX_CERTIFICATE_BYTES,
            "incremental_disk_bytes": MAX_INCREMENTAL_DISK_BYTES,
            "network_bytes": 0,
            "private_bytes": 0,
        },
        "access_counters": {
            "generated_machine_samples": sum(len(value["samples"]) for value in successes.values())
            + len(timeout_certificate["samples"]),
            "generated_certificates": len(successes) + 1,
            **ZERO_SCIENTIFIC_COUNTERS,
        },
        "acceptance_gates": {
            "three_success_scenarios_passed": True,
            "timeout_remained_not_ready": True,
            "deterministic_replay_passed": True,
            "all_36_mutations_refused_on_registered_routes": len(mutation_routes) == 36,
            "generated_outputs_removed": True,
            "resource_caps_passed": True,
            "private_and_scientific_counters_zero": all(
                value == 0 for value in ZERO_SCIENTIFIC_COUNTERS.values()
            ),
        },
        "warnings": [
            "Generated readiness does not authorize a private structural pass.",
            "Machine readiness is transient and expires after 300 seconds.",
            "FW2 and neural training remain ineligible until a real cohort is frozen under a later Tier C gate.",
        ],
        "unavailable_fields": [
            "real_machine_readiness",
            "private_cohort_identity",
            "neural_payload",
            "target_or_prediction",
            "scientific_score",
        ],
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    report["measurements"]["report_bytes"] = 0
    for _attempt in range(8):
        report_bytes = _canonical_json_bytes(report)
        if len(report_bytes) == report["measurements"]["report_bytes"]:
            break
        report["measurements"]["report_bytes"] = len(report_bytes)
    else:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "qualification report byte count did not settle"
        )
    if len(report_bytes) > MAX_CERTIFICATE_BYTES:
        raise MachineReadinessRefusal(
            REFUSAL_ROUTES[4], "qualification report exceeds 64 KiB"
        )
    return report


def build_plan_summary() -> dict[str, Any]:
    return {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "commands": ["plan", "qualify", "inspect", "readiness"],
        "fixed_certificate_path": CERTIFICATE_RELATIVE_PATH.as_posix(),
        "ordered_mutations": len(ORDERED_MUTATIONS),
        "machine_samples_required": CONSECUTIVE_PASSING_SAMPLES,
        "maximum_wait_seconds": int(MAXIMUM_WAIT_SECONDS),
        "private_content_opens": 0,
        "FW2_authorized": False,
        "scientific_value_of_plan": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_machine_readiness",
        description="Qualify and emit the fixed machine-only MARC2-VR4 readiness certificate.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the fixed generated-only plan.")
    subparsers.add_parser("qualify", help="Run generated replay and 36 refusal mutations.")
    inspect = subparsers.add_parser(
        "inspect", help="Inspect one generated, mode-0600 readiness certificate."
    )
    inspect.add_argument("--certificate", required=True, type=Path)
    subparsers.add_parser(
        "readiness", help="Write one fixed machine-only readiness certificate."
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            output: Mapping[str, Any] = build_plan_summary()
        elif args.command == "qualify":
            output = qualify_generated()
        elif args.command == "inspect":
            output = inspect_certificate_file(args.certificate)
        else:
            output = run_readiness()
    except MachineReadinessRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
