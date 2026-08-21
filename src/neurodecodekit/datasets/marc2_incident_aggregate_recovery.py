"""Proof-gated MARC2-VR14P aggregate-only incident recovery."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import resource
import stat
import subprocess
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

LANE_ID = "MARC2-VR14P"
SCHEMA_VERSION = "0.1.0"
PLAN_SCHEMA_NAME = "neurodecodekit.marc2_incident_aggregate_recovery_plan"
QUALIFICATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_incident_aggregate_recovery_qualification"
)
SOURCE_SCHEMA_NAME = "neurodecodekit.marc2_r4_private_discriminator_report"
RESULT_SCHEMA_NAME = "neurodecodekit.marc2_incident_aggregate_recovery_result"

DECISION_RELATIVE_PATH = Path(
    "registries/marc2_incident_aggregate_recovery_authorization_decision.v0.json"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_incident_aggregate_recovery_authorization_request.v0.json"
)
REQUEST_PROOF_RELATIVE_PATH = Path(
    "registries/marc2_incident_aggregate_recovery_request_proof.v0.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_incident_aggregate_recovery_implementation.v0.json"
)
IMPLEMENTATION_PROOF_RELATIVE_PATH = Path(
    "registries/marc2_incident_aggregate_recovery_implementation_proof.v0.json"
)

DECISION_SHA256 = "ecd7ad1bfc78740546c1849d4cdf924f2a89a2125860bec3f841b4da3657ab90"
REQUEST_SHA256 = "6ea606b35910bdc044b8750ce865845d25794da57488db54a564d31ab9f056c4"
REQUEST_PROOF_SHA256 = "d98f34a9b556d8eaca39e5018f298b6a0755e8dd50d7940c8f8835c4bf0077fa"
GREEN_DECISION_COMMIT = "60b97ea6c9715b651c17bb6d797c1f02c10ba9e2"
GREEN_DECISION_CI_RUN_ID = 32_444_425_790
GREEN_DECISION_BASE_JOB_ID = 96_661_242_381
GREEN_DECISION_OPTIONAL_JOB_ID = 96_661_242_496

SOURCE_REPORT_RELATIVE_PATH = Path(
    ".codex_work/marc2_r4_private_discriminator/v0/report.aggregate.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_incident_aggregate_recovery/v0"
)
RECEIPT_RELATIVE_NAME = "recovery.aggregate.v0.json"

THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
ARM_ENVIRONMENT_VARIABLE = "NEURODECODEKIT_VR14P_ONE_SHOT"
ARM_VALUE = "MARC2VR14P-ONE-SHOT-AGGREGATE-RECOVERY-V0"

ALLOWED_ROUTES = tuple(f"MARC2VR13P-R{i}" for i in range(1, 9))
GENERATED_ROUTE = "MARC2VR14P-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR14P-F{i:02d}" for i in range(1, 13))

MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_SOURCE_REPORT_BYTES = 65_536
MAX_OUTPUT_BYTES = 1024**2
MAX_TRACKED_BYTES = 1024**2

SOURCE_TOP_LEVEL_KEYS = {
    "schema_name",
    "schema_version",
    "lane_id",
    "status",
    "route",
    "proof",
    "aggregate",
    "resources",
    "counters",
    "warnings",
    "unavailable_fields",
    "claim_boundary",
}
SOURCE_PROOF_KEYS = {"decision_commit", "decision_CI"}
SOURCE_AGGREGATE_KEYS = {
    "cohort_size",
    "bundle_count",
    "core_member_count",
    "fit_heldout_overlap",
    "private_cohort_written",
}
SOURCE_RESOURCE_KEYS = {
    "input_bytes",
    "output_bytes",
    "runtime_seconds",
    "peak_RSS_bytes",
    "CPU_threads",
    "workers",
    "numerical_jobs",
    "network_bytes",
    "new_payload_bytes",
    "private_content_opens",
    "strict_JSON_parses",
    "VR12A_calls",
    "VR13A_residual_map_calls",
}
SOURCE_COUNTER_KEYS = {
    "raw_archive_header_or_member_payload_reads",
    "signal_event_channel_geometry_target_or_label_reads",
    "derivative_cache_feature_split_or_NeuroToken_operations",
    "training_inference_prediction_freeze_delivery_or_score_operations",
    "network_download_provider_language_model_operations",
    "stream_device_or_hardware_operations",
    "FW2_or_CIL1_operations",
    "operations_on_other_projects",
    "retry_rerun_resume_operations",
    "scientific_claim_upgrades",
}
SOURCE_CLAIM_KEYS = {
    "scientific_ceiling",
    "neural_effect",
    "decoding_accuracy",
    "language_or_thought_decoding",
    "live_decoding",
}
EXPECTED_SOURCE_WARNINGS = [
    "This is a target-free structural result, not a neural result.",
    "FW2 remains a separate prospective packet even after R1.",
]
EXPECTED_SOURCE_UNAVAILABLE = [
    "neural_payload",
    "decoding_metric",
    "live_latency",
    "FW2_result",
    "CIL1_result",
]
FORBIDDEN_PUBLIC_KEYS = {
    "candidate",
    "companion",
    "crc",
    "event",
    "exception",
    "failed_value",
    "label",
    "member",
    "model",
    "offset",
    "participant",
    "path",
    "predicate",
    "prediction",
    "reason",
    "row",
    "run",
    "score",
    "selection",
    "session",
    "signal",
    "source_hash",
    "subject",
    "target",
    "task",
}


class AggregateRecoveryRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR14P route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR14P refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    try:
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
    except (TypeError, ValueError) as exc:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[5], "canonical JSON refused"
        ) from exc


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[5], "strict JSON refused"
        ) from exc
    if not isinstance(value, dict):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[5], "top-level JSON object required"
        )
    return value


def _read_tracked(root: Path, relative: Path) -> bytes:
    if relative.is_absolute() or ".." in relative.parts:
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[0], "tracked path differs")
    path = root / relative
    try:
        info = path.lstat()
    except OSError as exc:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact type differs"
        )
    if info.st_size <= 0 or info.st_size > MAX_TRACKED_BYTES:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact size differs"
        )
    return path.read_bytes()


def _validate_decision(decision: Mapping[str, Any]) -> None:
    proof = decision.get("green_proof_closeout")
    request = decision.get("green_request")
    user = decision.get("user_authorization")
    authority = decision.get("authorization")
    caps = decision.get("resource_caps")
    routes = decision.get("route_contract")
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc2_incident_aggregate_recovery_authorization_decision"
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "3274a728ccf25a2e7bb5a7c208d2e8d53f2db6fb"
        or not isinstance(proof, dict)
        or proof.get("commit") != "3274a728ccf25a2e7bb5a7c208d2e8d53f2db6fb"
        or proof.get("CI_run_id") != 32_443_804_353
        or proof.get("base_python_job_id") != 96_659_529_617
        or proof.get("optional_neuro_job_id") != 96_659_529_824
        or proof.get("both_required_jobs_green") is not True
        or not isinstance(request, dict)
        or request.get("commit") != "d920e8eeaf7a7e9c980232c5de59f0e390c374be"
        or request.get("CI_run_id") != 32_443_248_466
        or request.get("both_required_jobs_green") is not True
        or not isinstance(user, dict)
        or user.get("actual_message_UTF8_bytes") != 96
        or user.get("actual_message_SHA256")
        != "607078d59f4150642583e70e780f00a9770bf405dc2a48ea4828ceb9a4bfbbe8"
        or user.get("sole_active_Tier_C_packet") != LANE_ID
        or user.get("one_registered_two_stage_sequence_only") is not True
        or user.get("continuous_or_future_packet_authority_inferred") is not False
        or not isinstance(authority, dict)
        or authority.get("generated_wrapper_implementation_after_decision_green")
        is not True
        or authority.get("generated_wrapper_qualification_after_decision_green")
        is not True
        or authority.get("stage_1_proof_closeout_after_implementation_green")
        is not True
        or authority.get("one_aggregate_report_read_after_stage_1_green") is not True
        or authority.get("one_aggregate_recovery_receipt") is not True
        or authority.get("implementation_or_ignored_access_authorized_now")
        is not False
        or authority.get("structural_source_or_private_manifest_access") is not False
        or authority.get("archive_neural_target_model_or_score_access") is not False
        or authority.get("FW2_or_CIL1_execution") is not False
        or not isinstance(caps, dict)
        or caps.get("CPU_threads") != 1
        or caps.get("workers") != 1
        or caps.get("numerical_jobs") != 1
        or caps.get("runtime_seconds_maximum") != 30
        or caps.get("peak_RSS_bytes_maximum") != MAX_PEAK_RSS_BYTES
        or caps.get("aggregate_report_content_opens") != 1
        or caps.get("aggregate_report_bytes_maximum") != MAX_SOURCE_REPORT_BYTES
        or caps.get("combined_output_bytes_maximum") != MAX_OUTPUT_BYTES
        or caps.get("network_bytes") != 0
        or caps.get("structural_source_operations") != 0
        or caps.get("private_manifest_operations") != 0
        or caps.get("retry_rerun_resume_count") != 0
        or not isinstance(routes, list)
        or [row.get("route") for row in routes if isinstance(row, dict)]
        != list(ALLOWED_ROUTES)
    ):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "authorization decision differs"
        )


def load_decision(root: Path | None = None) -> dict[str, Any]:
    fixed_root = root or _repo_root()
    payload = _read_tracked(fixed_root, DECISION_RELATIVE_PATH)
    if _sha256_bytes(payload) != DECISION_SHA256:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "authorization decision hash differs"
        )
    decision = _strict_json(payload)
    _validate_decision(decision)
    return decision


def _validate_green_dependencies(root: Path | None = None) -> None:
    fixed_root = root or _repo_root()
    for relative, expected in {
        REQUEST_RELATIVE_PATH: REQUEST_SHA256,
        REQUEST_PROOF_RELATIVE_PATH: REQUEST_PROOF_SHA256,
    }.items():
        if _sha256_bytes(_read_tracked(fixed_root, relative)) != expected:
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[0], "green dependency differs"
            )


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    current = environment or os.environ
    if any(current.get(key) != value for key, value in THREAD_ENVIRONMENT.items()):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[1], "one-thread environment required"
        )


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_PUBLIC_KEYS:
                raise AggregateRecoveryRefusal(
                    REFUSAL_ROUTES[7], "public output key refused"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _is_int(value: Any) -> bool:
    return type(value) is int


def _is_number(value: Any) -> bool:
    return type(value) in {int, float}


def _require_keys(value: Any, expected: set[str], route: str) -> Mapping[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise AggregateRecoveryRefusal(route, "aggregate schema differs")
    return value


def _validate_source_report(
    report: Mapping[str, Any], *, payload: bytes | None = None
) -> None:
    if set(report) != SOURCE_TOP_LEVEL_KEYS:
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "top-level schema differs")
    if (
        report.get("schema_name") != SOURCE_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != "MARC2-VR13P"
        or report.get("status") != "consumed"
        or report.get("route") not in ALLOWED_ROUTES
    ):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "source identity differs")
    _walk_public(report)
    proof = _require_keys(report["proof"], SOURCE_PROOF_KEYS, REFUSAL_ROUTES[6])
    if (
        proof.get("decision_commit")
        != "fe16400fd0ccb5fa2ff40fffd413fee34eb620d6"
        or proof.get("decision_CI") != 32_439_821_302
    ):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "source proof differs")
    aggregate = _require_keys(
        report["aggregate"], SOURCE_AGGREGATE_KEYS, REFUSAL_ROUTES[6]
    )
    integer_keys = (
        "cohort_size",
        "bundle_count",
        "core_member_count",
        "fit_heldout_overlap",
    )
    if any(not _is_int(aggregate.get(key)) for key in integer_keys):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "aggregate type differs")
    if aggregate["fit_heldout_overlap"] != 0 or not isinstance(
        aggregate["private_cohort_written"], bool
    ):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "aggregate value differs")
    route = str(report["route"])
    if route == ALLOWED_ROUTES[0]:
        if (
            not 12 <= aggregate["cohort_size"] <= 19
            or not 72 <= aggregate["bundle_count"] <= 114
            or not 288 <= aggregate["core_member_count"] <= 456
            or aggregate["private_cohort_written"] is not True
        ):
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[6], "R1 aggregate envelope differs"
            )
    elif any(aggregate[key] != 0 for key in integer_keys[:3]) or aggregate[
        "private_cohort_written"
    ] is not False:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[6], "residual aggregate envelope differs"
        )
    resources = _require_keys(
        report["resources"], SOURCE_RESOURCE_KEYS, REFUSAL_ROUTES[6]
    )
    integer_resources = SOURCE_RESOURCE_KEYS - {"runtime_seconds"}
    if any(not _is_int(resources.get(key)) for key in integer_resources):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "resource type differs")
    if not _is_number(resources.get("runtime_seconds")):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "runtime type differs")
    if (
        resources["input_bytes"] != 418_755
        or not 0 < resources["output_bytes"] <= 2 * 1024**2
        or not 0 <= resources["runtime_seconds"] <= 650
        or not 0 <= resources["peak_RSS_bytes"] <= MAX_PEAK_RSS_BYTES
        or resources["CPU_threads"] != 1
        or resources["workers"] != 1
        or resources["numerical_jobs"] != 1
        or resources["network_bytes"] != 0
        or resources["new_payload_bytes"] != 0
        or resources["private_content_opens"] != 1
        or resources["strict_JSON_parses"] != 1
        or resources["VR12A_calls"] != 1
        or resources["VR13A_residual_map_calls"] != (0 if route == ALLOWED_ROUTES[0] else 1)
    ):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "resource value differs")
    counters = _require_keys(
        report["counters"], SOURCE_COUNTER_KEYS, REFUSAL_ROUTES[6]
    )
    if any(not _is_int(value) or value != 0 for value in counters.values()):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "counter differs")
    claims = _require_keys(
        report["claim_boundary"], SOURCE_CLAIM_KEYS, REFUSAL_ROUTES[6]
    )
    if claims.get("scientific_ceiling") != "none" or any(
        claims.get(key) is not False for key in SOURCE_CLAIM_KEYS - {"scientific_ceiling"}
    ):
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "claim boundary differs")
    if report["warnings"] != EXPECTED_SOURCE_WARNINGS:
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[6], "warning set differs")
    if report["unavailable_fields"] != EXPECTED_SOURCE_UNAVAILABLE:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[6], "unavailable-field set differs"
        )
    if payload is not None and _canonical_json_bytes(report) != payload:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[6], "canonical source encoding required"
        )


def _generated_report(route: str) -> dict[str, Any]:
    success = route == ALLOWED_ROUTES[0]
    return {
        "schema_name": SOURCE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": "MARC2-VR13P",
        "status": "consumed",
        "route": route,
        "proof": {
            "decision_commit": "fe16400fd0ccb5fa2ff40fffd413fee34eb620d6",
            "decision_CI": 32_439_821_302,
        },
        "aggregate": {
            "cohort_size": 12 if success else 0,
            "bundle_count": 72 if success else 0,
            "core_member_count": 288 if success else 0,
            "fit_heldout_overlap": 0,
            "private_cohort_written": success,
        },
        "resources": {
            "input_bytes": 418_755,
            "output_bytes": 2048,
            "runtime_seconds": 1.0,
            "peak_RSS_bytes": 32 * 1024**2,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "private_content_opens": 1,
            "strict_JSON_parses": 1,
            "VR12A_calls": 1,
            "VR13A_residual_map_calls": 0 if success else 1,
        },
        "counters": {key: 0 for key in sorted(SOURCE_COUNTER_KEYS)},
        "warnings": list(EXPECTED_SOURCE_WARNINGS),
        "unavailable_fields": list(EXPECTED_SOURCE_UNAVAILABLE),
        "claim_boundary": {
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "live_decoding": False,
        },
    }


def _safe_parent_chain(root: Path, relative: Path) -> None:
    if relative.is_absolute() or ".." in relative.parts:
        raise AggregateRecoveryRefusal(REFUSAL_ROUTES[2], "fixed path differs")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[2], "symlinked parent refused"
            )


def _create_fresh_directory(root: Path, relative: Path) -> Path:
    _safe_parent_chain(root, relative)
    path = root / relative
    try:
        path.mkdir(parents=True, mode=0o700, exist_ok=False)
    except OSError as exc:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[9], "fresh output root required"
        ) from exc
    return path


def _write_exclusive(path: Path, payload: bytes, mode: int = 0o644) -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
        try:
            written = 0
            while written < len(payload):
                written += os.write(descriptor, payload[written:])
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[9], "exclusive output write refused"
        ) from exc
    return len(payload)


def _preflight_source_report(path: Path) -> int:
    try:
        info = path.lstat()
    except OSError as exc:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[3], "aggregate report unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[3], "aggregate report type refused"
        )
    if info.st_size <= 0 or info.st_size > MAX_SOURCE_REPORT_BYTES:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[3], "aggregate report size refused"
        )
    return info.st_size


def _read_source_report_once(path: Path, expected_size: int) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[4], "aggregate report open refused"
        ) from exc
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_size != expected_size
            or info.st_size <= 0
            or info.st_size > MAX_SOURCE_REPORT_BYTES
        ):
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[4], "aggregate report changed before open"
            )
        chunks: list[bytes] = []
        remaining = expected_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 16_384))
            if not chunk:
                raise AggregateRecoveryRefusal(
                    REFUSAL_ROUTES[4], "aggregate report ended early"
                )
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[4], "aggregate report grew during read"
            )
    finally:
        os.close(descriptor)
    return b"".join(chunks)


def _zero_counters() -> dict[str, int]:
    return {
        "readiness_certificate_or_consumed_marker_operations": 0,
        "structural_source_operations": 0,
        "private_manifest_operations": 0,
        "archive_header_or_member_payload_operations": 0,
        "signal_event_channel_geometry_target_or_label_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "FW2_or_CIL1_operations": 0,
        "operations_on_other_projects": 0,
        "retry_rerun_resume_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _build_receipt(
    *,
    source_report: Mapping[str, Any],
    input_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
    implementation_proof: Mapping[str, Any],
) -> dict[str, Any]:
    report_aggregate = source_report["aggregate"]
    receipt = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed",
        "route": source_report["route"],
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI": GREEN_DECISION_CI_RUN_ID,
            "implementation_commit": implementation_proof["implementation_commit"],
            "implementation_CI": implementation_proof["implementation_CI_run_id"],
            "proof_closeout_commit": implementation_proof["proof_closeout_commit"],
            "proof_closeout_CI": implementation_proof["proof_closeout_CI_run_id"],
        },
        "aggregate": {
            "cohort_size": report_aggregate["cohort_size"],
            "bundle_count": report_aggregate["bundle_count"],
            "core_member_count": report_aggregate["core_member_count"],
            "fit_heldout_overlap": report_aggregate["fit_heldout_overlap"],
            "upstream_private_cohort_written": report_aggregate[
                "private_cohort_written"
            ],
        },
        "resources": {
            "input_bytes": input_bytes,
            "receipt_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
        },
        "operations": {
            "aggregate_report_lstats": 1,
            "aggregate_report_content_opens": 1,
            "aggregate_report_strict_JSON_parses": 1,
            "aggregate_recovery_receipt_writes": 1,
            **_zero_counters(),
        },
        "warnings": [
            "This recovers one aggregate structural route, not neural evidence.",
            "No source, private manifest, archive, signal, target, model, or score was accessed.",
        ],
        "unavailable_fields": [
            "failed_private_value",
            "private_row_or_identity",
            "real_neural_cohort",
            "neural_effect",
            "decoding_accuracy",
            "live_latency",
        ],
        "claim_boundary": {
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "live_decoding": False,
        },
    }
    _walk_public(receipt)
    for _ in range(4):
        payload = _canonical_json_bytes(receipt)
        if receipt["resources"]["receipt_bytes"] == len(payload):
            break
        receipt["resources"]["receipt_bytes"] = len(payload)
    if receipt["resources"]["receipt_bytes"] != len(_canonical_json_bytes(receipt)):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[9], "receipt size did not stabilize"
        )
    return receipt


def _assert_resources(
    *, runtime_seconds: float, peak_rss_bytes: int, output_bytes: int
) -> None:
    if (
        not 0 <= runtime_seconds <= MAX_RUNTIME_SECONDS
        or not 0 <= peak_rss_bytes <= MAX_PEAK_RSS_BYTES
        or not 0 < output_bytes <= MAX_OUTPUT_BYTES
    ):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[10], "resource boundary refused"
        )


def _load_implementation(root: Path) -> dict[str, Any]:
    return _strict_json(_read_tracked(root, IMPLEMENTATION_RELATIVE_PATH))


def _tracked_and_clean(root: Path, relative: Path) -> bool:
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(relative)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    clean = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", str(relative)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return tracked.returncode == 0 and clean.returncode == 0


def _load_implementation_proof(root: Path) -> dict[str, Any]:
    if not _tracked_and_clean(root, IMPLEMENTATION_PROOF_RELATIVE_PATH):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked clean implementation proof required"
        )
    record = _strict_json(_read_tracked(root, IMPLEMENTATION_PROOF_RELATIVE_PATH))
    if (
        record.get("schema_name")
        != "neurodecodekit.marc2_incident_aggregate_recovery_implementation_proof"
        or record.get("lane_id") != LANE_ID
        or record.get("both_required_jobs_green") is not True
        or record.get("proof_closeout_both_required_jobs_green") is not True
        or not isinstance(record.get("implementation_commit"), str)
        or len(record["implementation_commit"]) != 40
        or not _is_int(record.get("implementation_CI_run_id"))
        or not isinstance(record.get("proof_closeout_commit"), str)
        or len(record["proof_closeout_commit"]) != 40
        or not _is_int(record.get("proof_closeout_CI_run_id"))
        or record.get("aggregate_report_content_opens_authorized") is not True
        or record.get("retry_rerun_resume_allowed") is not False
    ):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "implementation proof differs"
        )
    implementation = _load_implementation(root)
    artifacts = implementation.get("owned_artifacts")
    if (
        implementation.get("schema_name")
        != "neurodecodekit.marc2_incident_aggregate_recovery_implementation"
        or implementation.get("lane_id") != LANE_ID
        or not isinstance(artifacts, list)
        or not artifacts
    ):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "implementation record differs"
        )
    for row in artifacts:
        if not isinstance(row, dict):
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[0], "implementation artifact row differs"
            )
        relative = Path(str(row.get("path", "")))
        payload = _read_tracked(root, relative)
        if (
            len(payload) != row.get("bytes")
            or _sha256_bytes(payload) != row.get("sha256")
            or not _tracked_and_clean(root, relative)
        ):
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[0], "implementation artifact differs"
            )
    return record


def _recover_from_root(
    root: Path,
    *,
    implementation_proof: Mapping[str, Any],
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    started = time.monotonic()
    _safe_parent_chain(root, SOURCE_REPORT_RELATIVE_PATH)
    source_path = root / SOURCE_REPORT_RELATIVE_PATH
    expected_size = _preflight_source_report(source_path)
    output_root = _create_fresh_directory(root, OUTPUT_ROOT_RELATIVE_PATH)
    payload = _read_source_report_once(source_path, expected_size)
    report = _strict_json(payload)
    _validate_source_report(report, payload=payload)
    runtime = time.monotonic() - started
    peak_rss = rss_reader()
    receipt = _build_receipt(
        source_report=report,
        input_bytes=len(payload),
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        implementation_proof=implementation_proof,
    )
    receipt_payload = _canonical_json_bytes(receipt)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=len(receipt_payload),
    )
    _write_exclusive(output_root / RECEIPT_RELATIVE_NAME, receipt_payload)
    return receipt


def _generated_proof() -> dict[str, Any]:
    return {
        "implementation_commit": "1" * 40,
        "implementation_CI_run_id": 1,
        "proof_closeout_commit": "2" * 40,
        "proof_closeout_CI_run_id": 2,
    }


def _run_generated_matrix() -> dict[str, Any]:
    counts: Counter[str] = Counter()
    replay_rows: list[list[list[str]]] = []
    input_bytes = 0
    orders = (ALLOWED_ROUTES, tuple(reversed(ALLOWED_ROUTES)))
    for _replay in range(2):
        replay: list[list[str]] = []
        for order in orders:
            rows: list[str] = []
            for route in order:
                report = _generated_report(route)
                payload = _canonical_json_bytes(report)
                input_bytes += len(payload)
                parsed = _strict_json(payload)
                _validate_source_report(parsed, payload=payload)
                counts[route] += 1
                rows.append(route)
            replay.append(rows)
        replay_rows.append(replay)
    if (
        replay_rows[0] != replay_rows[1]
        or dict(sorted(counts.items())) != {route: 4 for route in ALLOWED_ROUTES}
    ):
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[8], "generated route matrix differs"
        )
    return {
        "cases": 8,
        "orders": 2,
        "replays": 2,
        "paths": 32,
        "route_counts": dict(sorted(counts.items())),
        "generated_input_bytes": input_bytes,
        "replay_sha256": _sha256_bytes(_canonical_json_bytes(replay_rows)),
    }


def _run_generated_fixed_path(
    *, rss_reader: Callable[[], int] = _peak_rss_bytes
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="marc2-vr14p-generated-") as name:
        root = Path(name)
        source_path = root / SOURCE_REPORT_RELATIVE_PATH
        source_path.parent.mkdir(parents=True, mode=0o700)
        payload = _canonical_json_bytes(_generated_report(ALLOWED_ROUTES[3]))
        _write_exclusive(source_path, payload)
        receipt = _recover_from_root(
            root,
            implementation_proof=_generated_proof(),
            rss_reader=rss_reader,
        )
        output_path = root / OUTPUT_ROOT_RELATIVE_PATH / RECEIPT_RELATIVE_NAME
        output_payload = output_path.read_bytes()
        if (
            receipt["route"] != ALLOWED_ROUTES[3]
            or _strict_json(output_payload) != receipt
            or len(output_payload) > MAX_OUTPUT_BYTES
        ):
            raise AggregateRecoveryRefusal(
                REFUSAL_ROUTES[8], "generated fixed path differs"
            )
        return {
            "source_bytes": len(payload),
            "receipt_bytes": len(output_payload),
            "route": receipt["route"],
            "temporary_root_only": True,
            "retained_output_bytes": 0,
        }


def _expect_refusal(call: Callable[[], Any]) -> int:
    try:
        call()
    except AggregateRecoveryRefusal:
        return 1
    raise AssertionError("expected MARC2-VR14P refusal")


def _run_direct_refusals(decision: Mapping[str, Any]) -> dict[str, int]:
    total = 0
    for payload in (b"[]\n", b'{"a":1,"a":2}\n', b'{"a":NaN}\n', b"\xff"):
        total += _expect_refusal(lambda payload=payload: _strict_json(payload))
    for key in THREAD_ENVIRONMENT:
        missing = dict(THREAD_ENVIRONMENT)
        missing.pop(key)
        wrong = dict(THREAD_ENVIRONMENT)
        wrong[key] = "2"
        total += _expect_refusal(
            lambda missing=missing: _validate_thread_environment(missing)
        )
        total += _expect_refusal(
            lambda wrong=wrong: _validate_thread_environment(wrong)
        )
    decision_mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("lane_id", "MARC2-VR14X"),
        lambda value: value.__setitem__("authorization_parent_commit", "0" * 40),
        lambda value: value["green_proof_closeout"].__setitem__("CI_run_id", 0),
        lambda value: value["green_proof_closeout"].__setitem__(
            "both_required_jobs_green", False
        ),
        lambda value: value["green_request"].__setitem__("commit", "0" * 40),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_UTF8_bytes", 95
        ),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_SHA256", "0" * 64
        ),
        lambda value: value["user_authorization"].__setitem__(
            "continuous_or_future_packet_authority_inferred", True
        ),
        lambda value: value["authorization"].__setitem__(
            "generated_wrapper_implementation_after_decision_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "one_aggregate_report_read_after_stage_1_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "implementation_or_ignored_access_authorized_now", True
        ),
        lambda value: value["authorization"].__setitem__(
            "structural_source_or_private_manifest_access", True
        ),
        lambda value: value["authorization"].__setitem__(
            "archive_neural_target_model_or_score_access", True
        ),
        lambda value: value["authorization"].__setitem__("FW2_or_CIL1_execution", True),
        lambda value: value["resource_caps"].__setitem__("CPU_threads", 2),
        lambda value: value["resource_caps"].__setitem__(
            "aggregate_report_bytes_maximum", 65_535
        ),
        lambda value: value["route_contract"].pop(),
    ]
    for mutate in decision_mutations:
        changed = copy.deepcopy(dict(decision))
        mutate(changed)
        total += _expect_refusal(lambda changed=changed: _validate_decision(changed))
    report_mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("schema_name", "other"),
        lambda value: value.__setitem__("lane_id", LANE_ID),
        lambda value: value.__setitem__("status", "generated"),
        lambda value: value.__setitem__("route", "MARC2VR13P-R9"),
        lambda value: value.__setitem__("extra", 1),
        lambda value: value["proof"].__setitem__("decision_commit", "0" * 40),
        lambda value: value["aggregate"].__setitem__("fit_heldout_overlap", 1),
        lambda value: value["aggregate"].__setitem__("cohort_size", True),
        lambda value: value["resources"].__setitem__("input_bytes", 0),
        lambda value: value["resources"].__setitem__("output_bytes", 0),
        lambda value: value["resources"].__setitem__("runtime_seconds", 651),
        lambda value: value["resources"].__setitem__(
            "peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1
        ),
        lambda value: value["resources"].__setitem__("CPU_threads", 2),
        lambda value: value["resources"].__setitem__("private_content_opens", 2),
        lambda value: value["resources"].__setitem__("strict_JSON_parses", 2),
        lambda value: value["resources"].__setitem__("VR12A_calls", 2),
        lambda value: value["resources"].__setitem__(
            "VR13A_residual_map_calls", 0
        ),
        lambda value: value["counters"].__setitem__(
            "scientific_claim_upgrades", 1
        ),
        lambda value: value["claim_boundary"].__setitem__("neural_effect", True),
        lambda value: value.__setitem__("warnings", []),
        lambda value: value.__setitem__("unavailable_fields", []),
    ]
    for mutate in report_mutations:
        changed = _generated_report(ALLOWED_ROUTES[3])
        mutate(changed)
        total += _expect_refusal(lambda changed=changed: _validate_source_report(changed))
    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        total += _expect_refusal(
            lambda key=key: _validate_source_report(
                {**_generated_report(ALLOWED_ROUTES[3]), key: "redacted"}
            )
        )
    for runtime_seconds, peak_rss_bytes, output_bytes in (
        (-1.0, 1, 1),
        (MAX_RUNTIME_SECONDS + 1, 1, 1),
        (1.0, -1, 1),
        (1.0, MAX_PEAK_RSS_BYTES + 1, 1),
        (1.0, 1, 0),
        (1.0, 1, MAX_OUTPUT_BYTES + 1),
    ):
        total += _expect_refusal(
            lambda runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            output_bytes=output_bytes: _assert_resources(
                runtime_seconds=runtime_seconds,
                peak_rss_bytes=peak_rss_bytes,
                output_bytes=output_bytes,
            )
        )
    with tempfile.TemporaryDirectory(prefix="marc2-vr14p-refusal-") as name:
        root = Path(name)
        total += _expect_refusal(lambda: _safe_parent_chain(root, Path("/absolute")))
        total += _expect_refusal(
            lambda: _safe_parent_chain(root, Path("parent/../escape"))
        )
        (root / "linked").symlink_to(root / "missing", target_is_directory=True)
        total += _expect_refusal(
            lambda: _create_fresh_directory(root, Path("linked/output"))
        )
        output = _create_fresh_directory(root, Path("fixed/output"))
        total += _expect_refusal(
            lambda: _create_fresh_directory(root, Path("fixed/output"))
        )
        existing = output / "existing.json"
        _write_exclusive(existing, b"{}\n")
        total += _expect_refusal(lambda: _write_exclusive(existing, b"{}\n"))
        oversized = root / "oversized.json"
        oversized.write_bytes(b"x" * (MAX_SOURCE_REPORT_BYTES + 1))
        total += _expect_refusal(lambda: _preflight_source_report(oversized))
    if total < 80:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[11], "direct refusal minimum differs"
        )
    return {"total": total}


def qualify_generated(
    *,
    environment: Mapping[str, str] | None = None,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run bounded generated-only Stage 1 qualification."""

    started = time.monotonic()
    decision = load_decision()
    _validate_green_dependencies()
    _validate_thread_environment(environment)
    matrix = _run_generated_matrix()
    fixed_path = _run_generated_fixed_path(rss_reader=rss_reader)
    refusals = _run_direct_refusals(decision)
    runtime = time.monotonic() - started
    peak_rss = rss_reader()
    result = {
        "schema_name": QUALIFICATION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "stage_1_generated_qualified_aggregate_read_closed",
        "route": GENERATED_ROUTE,
        "matrix": matrix,
        "fixed_path": fixed_path,
        "direct_refusals": refusals,
        "resources": {
            "generated_input_bytes": (
                matrix["generated_input_bytes"] + fixed_path["source_bytes"]
            ),
            "aggregate_output_bytes": 0,
            "retained_output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
        },
        "counters": {
            "generated_report_validations": 33,
            "private_or_Git_ignored_path_operations": 0,
            "aggregate_report_operations": 0,
            "recovery_output_operations": 0,
            **_zero_counters(),
        },
        "warnings": [
            "Generated qualification demonstrates aggregate interface mechanics only.",
            "The real aggregate report remains closed until separate remote proof.",
        ],
        "unavailable_fields": [
            "recovered_route",
            "real_neural_cohort",
            "neural_effect",
            "decoding_accuracy",
            "live_latency",
        ],
        "claim_boundary": {
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "live_decoding": False,
        },
    }
    result["resources"]["aggregate_output_bytes"] = len(
        _canonical_json_bytes(result)
    )
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=len(_canonical_json_bytes(result)),
    )
    _walk_public(result)
    return result


def execute_registered(*, armed: bool = False) -> dict[str, Any]:
    """Consume the one fixed aggregate-only recovery after all proof gates."""

    if not armed:
        raise AggregateRecoveryRefusal(
            REFUSAL_ROUTES[0], "explicit one-shot arming required"
        )
    root = _repo_root()
    load_decision(root)
    _validate_green_dependencies(root)
    _validate_thread_environment()
    proof = _load_implementation_proof(root)
    return _recover_from_root(root, implementation_proof=proof)


def inspect_stage() -> dict[str, Any]:
    """Inspect only tracked Stage 1 metadata; never inspect ignored output."""

    root = _repo_root()
    load_decision(root)
    _validate_green_dependencies(root)
    implementation = _load_implementation(root)
    return {
        "schema_name": "neurodecodekit.marc2_incident_aggregate_recovery_inspection",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": implementation.get("status"),
        "remote_implementation_proof": implementation.get(
            "remote_implementation_proof"
        ),
        "ignored_path_operations": 0,
        "aggregate_report_operations": 0,
        "claim_boundary": {
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "live_decoding": False,
        },
    }


def build_plan() -> dict[str, Any]:
    decision = load_decision()
    _validate_green_dependencies()
    return {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "decision_green_stage_1_available_aggregate_read_proof_gated",
        "fixed_interface": decision["future_interface"]["CLI_commands"],
        "generated_paths": 32,
        "aggregate_report_content_open_limit": 1,
        "aggregate_report_bytes_maximum": MAX_SOURCE_REPORT_BYTES,
        "combined_output_bytes_maximum": MAX_OUTPUT_BYTES,
        "CPU_threads": 1,
        "workers": 1,
        "network_bytes": 0,
        "structural_source_operations": 0,
        "private_manifest_operations": 0,
        "warnings": [
            "Execute requires explicit one-shot arming and a tracked clean green proof.",
            "R1 enables only a separate private-manifest recovery packet.",
        ],
        "claim_boundary": {
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "live_decoding": False,
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "qualify", "inspect", "execute"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = build_plan()
        elif args.command == "qualify":
            result = qualify_generated()
        elif args.command == "inspect":
            result = inspect_stage()
        else:
            result = execute_registered(
                armed=os.environ.get(ARM_ENVIRONMENT_VARIABLE) == ARM_VALUE
            )
    except AggregateRecoveryRefusal as exc:
        print(json.dumps({"status": "refused", "route": exc.route}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
