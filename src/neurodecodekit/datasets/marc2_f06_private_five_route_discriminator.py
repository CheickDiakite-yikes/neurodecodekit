"""Proof-gated MARC2 private five-route F06 discriminator.

Generated qualification uses only invocation-created temporary fixtures. The
public executor has fixed paths and refuses before readiness or private-path
access until the implementation registry contains exact remote-green proof.
"""

from __future__ import annotations

import argparse
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
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.datasets import marc2_published_task_selector_repair as repair
from neurodecodekit.datasets import marc2_f06_five_route_decomposition as discriminator


LANE_ID = "MARC2-VR24P"
SCHEMA_VERSION = "0.1.0"
PLAN_SCHEMA_NAME = "neurodecodekit.marc2_f06_private_five_route_discriminator_plan"
QUALIFICATION_SCHEMA_NAME = "neurodecodekit.marc2_f06_private_five_route_discriminator_qualification"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_f06_private_five_route_discriminator_report"
CERTIFICATE_SCHEMA_NAME = "neurodecodekit.marc2_f06_private_five_route_discriminator_readiness_certificate"
MARKER_SCHEMA_NAME = "neurodecodekit.marc2_f06_private_five_route_discriminator_consumed"

DECISION_RELATIVE_PATH = Path(
    "registries/marc2_f06_private_five_route_discriminator_authorization_decision.v0.json"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_f06_private_five_route_discriminator_authorization_request.v0.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_f06_private_five_route_discriminator_implementation.v0.json"
)
VR20A_MODULE_RELATIVE_PATH = Path("src/neurodecodekit/datasets/marc2_published_task_selector_repair.py")
VR20A_CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_published_task_selector_repair_contract.v0.json"
)
VR23A_MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_f06_five_route_decomposition.py"
)
VR23A_IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_f06_five_route_decomposition_implementation.v0.json"
)
VR23A_RESULT_RELATIVE_PATH = Path(
    "registries/marc2_f06_five_route_decomposition_result.v0.json"
)
READINESS_RELATIVE_PATH = Path(".codex_work/marc2_machine_readiness/vr24p/readiness.v0.json")
OUTPUT_ROOT_RELATIVE_PATH = Path(".codex_work/marc2_f06_private_five_route/v0")
MARKER_RELATIVE_NAME = "consumed.marker.v0.json"
REPORT_RELATIVE_NAME = "report.aggregate.v0.json"
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json"
)

DECISION_SHA256 = "3dc22c42c8ea7da95d36745e3fec024b0cf374b7d1e4c96d854aa811ea57f102"
REQUEST_SHA256 = "5389e2364634e4ae02bdffa69076132478456cb4bd152e9148f374cb3efb95a6"
GREEN_DECISION_COMMIT = "53bc114db9a51a256cbf86d470f24397a50f12b2"
GREEN_DECISION_CI_RUN_ID = 32_599_996_090
GREEN_DECISION_BASE_JOB_ID = 97_096_723_985
GREEN_DECISION_OPTIONAL_JOB_ID = 97_096_724_073
VR20A_MODULE_SHA256 = "9f6ebe63dbeb1cd778a71ff395d698159acc672b187e5121d5d5e734d9e05fba"
VR20A_CONTRACT_SHA256 = "a2719e0e2ab54e28675929e1982a8387406068114c2079dd3864c2c8ec022516"
VR23A_MODULE_SHA256 = "199f31aee5b0131a9061589625cdc607d6cc61ad43c4797b39941e57c1d49143"
VR23A_IMPLEMENTATION_SHA256 = "4eef300494ae2fc9fd72d2338ccf156bd7efb807d3c2d60c3a06c9f21b57f028"
VR23A_RESULT_SHA256 = "c3166203b32805ddfec9a7f33937f33c3781a366850d3f57a275b4b8903f0f9d"

PRIVATE_SOURCE_IDENTITY = {
    "mode": 0o600,
    "bytes": 418_755,
    "sha256": "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
}
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
SUCCESS_ROUTE = "MARC2VR24P-G1"
PRIVATE_CLASS_ROUTES = tuple(f"MARC2VR24P-R{index}" for index in range(1, 6))
PRIVATE_FAILURE_ROUTES = tuple(f"MARC2VR24P-R{index}" for index in range(6, 10))
PRIVATE_ROUTES = PRIVATE_CLASS_ROUTES + PRIVATE_FAILURE_ROUTES
REFUSAL_ROUTES = tuple(f"MARC2VR24P-F{index:02d}" for index in range(1, 13))
MAX_GENERATED_RUNTIME_SECONDS = 60.0
MAX_PRIVATE_RUNTIME_SECONDS = 650.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_COMBINED_OUTPUT_BYTES = 1 * 1024**2
MAX_TRACKED_FILE_BYTES = 2 * 1024**2
MAX_CERTIFICATE_BYTES = 64 * 1024
MINIMUM_SAMPLE_INTERVAL_SECONDS = 5.0
REQUIRED_PASSING_SAMPLES = 3
GENERATED_CASES = discriminator.CASES
GENERATED_CASE_ROUTES = {
    "control_success": SUCCESS_ROUTE,
    "entry_kind_count_drift": PRIVATE_CLASS_ROUTES[0],
    "extra_complete_bundle": PRIVATE_CLASS_ROUTES[1],
    "unknown_participant_taxonomy": PRIVATE_CLASS_ROUTES[2],
    "classification_arithmetic_drift": PRIVATE_CLASS_ROUTES[3],
    "eligible_session_distribution_drift": PRIVATE_CLASS_ROUTES[4],
}

FORBIDDEN_PUBLIC_KEYS = {
    "member_name",
    "source_path",
    "subject_id",
    "participant_id",
    "session_id",
    "run_id",
    "task",
    "offset",
    "crc",
    "predicate",
    "failed_value",
    "reason",
    "safe_reason",
    "failure_detail",
    "upstream_route",
    "exception",
    "label",
    "target",
    "prediction",
    "score",
    "selected_subject_ids",
    "source_sha256",
    "rows",
}


class F06PrivateFiveRouteDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe route."""

    def __init__(self, route: str, reason: str):
        if route not in REFUSAL_ROUTES and route not in PRIVATE_ROUTES:
            raise ValueError("unknown MARC2-VR24P refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "value is not canonical JSON"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[6], "duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[6], "non-finite JSON number")


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except F06PrivateFiveRouteDiscriminatorRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[6], "strict JSON parse failed") from exc
    if not isinstance(value, dict):
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[6], "JSON root is not an object")
    return value


def _read_tracked(root: Path, relative: Path) -> bytes:
    if relative.is_absolute() or ".." in relative.parts:
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[0], "tracked path is unsafe")
    path = root / relative
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_TRACKED_FILE_BYTES:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact is not a bounded regular file"
        )
    return path.read_bytes()


def load_decision(root: Path | None = None) -> dict[str, Any]:
    repo = root or _repo_root()
    request_payload = _read_tracked(repo, REQUEST_RELATIVE_PATH)
    if _sha256_bytes(request_payload) != REQUEST_SHA256:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "authorization request identity differs"
        )
    payload = _read_tracked(repo, DECISION_RELATIVE_PATH)
    if _sha256_bytes(payload) != DECISION_SHA256:
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[0], "decision identity differs")
    decision = _strict_json(payload)
    _validate_decision(decision)
    return decision


def _validate_upstream_artifacts(root: Path | None = None) -> None:
    repo = root or _repo_root()
    expected = (
        (VR20A_MODULE_RELATIVE_PATH, VR20A_MODULE_SHA256),
        (VR20A_CONTRACT_RELATIVE_PATH, VR20A_CONTRACT_SHA256),
        (VR23A_MODULE_RELATIVE_PATH, VR23A_MODULE_SHA256),
        (VR23A_IMPLEMENTATION_RELATIVE_PATH, VR23A_IMPLEMENTATION_SHA256),
        (VR23A_RESULT_RELATIVE_PATH, VR23A_RESULT_SHA256),
    )
    for relative, digest in expected:
        if _sha256_bytes(_read_tracked(repo, relative)) != digest:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "upstream artifact identity differs"
            )


def _validate_decision(decision: Mapping[str, Any]) -> None:
    request = decision.get("green_request")
    proof = decision.get("green_proof_closeout")
    user = decision.get("user_authorization")
    authority = decision.get("authorization")
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc2_f06_private_five_route_discriminator_authorization_decision"
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "c53d4cf18f3ef976e993438470b012cd5115399e"
        or not isinstance(request, dict)
        or request.get("commit") != "b7fca404a85c9597f61b1016c388b544ee901595"
        or request.get("both_required_jobs_green") is not True
        or not isinstance(proof, dict)
        or proof.get("commit") != "c53d4cf18f3ef976e993438470b012cd5115399e"
        or proof.get("both_required_jobs_green") is not True
        or not isinstance(user, dict)
        or user.get("actual_message_verbatim") != "continue"
        or user.get("actual_message_SHA256")
        != "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad"
        or user.get("sole_active_Tier_C_packet") != LANE_ID
        or not isinstance(authority, dict)
        or authority.get("one_private_structural_read_after_stage_1_proof_green") is not True
        or authority.get("one_VR23A_call_after_stage_1_proof_green") is not True
        or authority.get("one_nested_VR20A_call_after_stage_1_proof_green") is not True
        or authority.get("private_cohort_freeze_authorized") is not False
        or authority.get("MARC2_FW2_or_CIL1_real_execution_authorized_now") is not False
    ):
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[0], "decision contract differs")


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment if environment is not None else os.environ
    if any(values.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[1], "thread environment is not one")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _base_zero_counters() -> dict[str, int]:
    return {
        "raw_data_reads": 0,
        "real_cache_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "network_requests": 0,
        "new_payload_bytes": 0,
        "archive_local_header_reads": 0,
        "archive_member_payload_reads": 0,
        "signal_sample_reads": 0,
        "event_channel_or_geometry_reads": 0,
        "target_or_label_reads": 0,
        "checkpoint_reads": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scoring_runs": 0,
        "FW2_operations": 0,
        "CIL1_operations": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "other_project_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _walk_public(value: Any, *, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_PUBLIC_KEYS:
                raise F06PrivateFiveRouteDiscriminatorRefusal(
                    REFUSAL_ROUTES[9], "aggregate report contains a private field"
                )
            _walk_public(child, path=(*path, str(key)))
    elif isinstance(value, list):
        for child in value:
            _walk_public(child, path=path)
    elif isinstance(value, float) and not math.isfinite(value):
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "aggregate report contains a non-finite number"
        )


def _assert_resources(
    runtime: float, peak_rss: int, output_bytes: int, *, generated: bool = True
) -> None:
    runtime_cap = MAX_GENERATED_RUNTIME_SECONDS if generated else MAX_PRIVATE_RUNTIME_SECONDS
    if (
        runtime < 0
        or runtime > runtime_cap
        or peak_rss < 0
        or peak_rss >= MAX_PEAK_RSS_BYTES
        or output_bytes < 0
        or output_bytes > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[10], "resource or output cap exceeded")


def _safe_parent_chain(root: Path, relative: Path) -> None:
    if relative.is_absolute() or ".." in relative.parts:
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[2], "unsafe fixed path")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[2], "fixed parent is a symlink")


def _create_fresh_directory(root: Path, relative: Path) -> Path:
    _safe_parent_chain(root, relative)
    path = root / relative
    if path.exists() or path.is_symlink():
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[2], "fixed output already exists")
    path.mkdir(parents=True, mode=0o700)
    return path


def _write_exclusive(path: Path, payload: bytes, mode: int) -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, mode)
    try:
        written = os.write(descriptor, payload)
        if written != len(payload):
            raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[9], "short fixed-path write")
    finally:
        os.close(descriptor)
    os.chmod(path, mode)
    return len(payload)


def _sample_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[4], "readiness timestamp is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "readiness timestamp is malformed"
        ) from exc
    if parsed.tzinfo is None:
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[4], "readiness timestamp lacks timezone")
    return parsed.astimezone(UTC)


def _validate_samples(samples: Sequence[Mapping[str, Any]]) -> None:
    if len(samples) != REQUIRED_PASSING_SAMPLES:
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[4], "readiness sample count differs")
    times = [_sample_time(sample.get("observed_at_UTC")) for sample in samples]
    for index, sample in enumerate(samples):
        if (
            sample.get("sequence") != index + 1
            or sample.get("logical_CPUs", 0) < 1
            or sample.get("normalized_one_minute_load", 2.0) > 1.0
            or sample.get("process_peak_RSS_bytes", MAX_PEAK_RSS_BYTES) >= MAX_PEAK_RSS_BYTES
            or sample.get("free_disk_bytes", 0) < MINIMUM_FREE_DISK_BYTES
            or sample.get("thread_environment_all_one") is not True
        ):
            raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[4], "readiness sample failed")
        if index and (times[index] - times[index - 1]).total_seconds() < 5:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[4], "readiness samples are too close"
            )


def _generated_samples() -> list[dict[str, Any]]:
    started = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
    return [
        {
            "sequence": index + 1,
            "observed_at_UTC": (started + timedelta(seconds=index * 5)).isoformat(),
            "logical_CPUs": 4,
            "normalized_one_minute_load": 0.25,
            "process_peak_RSS_bytes": 32 * 1024**2,
            "free_disk_bytes": 20 * 1024**3,
            "thread_environment_all_one": True,
        }
        for index in range(3)
    ]


def _certificate(
    samples: Sequence[Mapping[str, Any]], *, implementation_commit: str, generated: bool
) -> dict[str, Any]:
    _validate_samples(samples)
    return {
        "schema_name": CERTIFICATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_fixture_ready" if generated else "real_machine_ready",
        "implementation_commit": implementation_commit,
        "sample_count": len(samples),
        "samples_sha256": _sha256_bytes(_canonical_json_bytes(list(samples))),
        "validity_seconds": 300,
        "generated": generated,
    }


def _preflight_source(path: Path, identity: Mapping[str, Any]) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            PRIVATE_FAILURE_ROUTES[0], "fixed source is unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            PRIVATE_FAILURE_ROUTES[0], "fixed source precondition failed"
        )
    if stat.S_IMODE(info.st_mode) != identity["mode"] or info.st_size != identity["bytes"]:
        raise F06PrivateFiveRouteDiscriminatorRefusal(PRIVATE_FAILURE_ROUTES[1], "source identity differs")


def _read_source_once(
    path: Path,
    identity: Mapping[str, Any],
    *,
    preflighted: bool = False,
    accounting: dict[str, int] | None = None,
) -> bytes:
    if not preflighted:
        _preflight_source(path, identity)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            PRIVATE_FAILURE_ROUTES[1], "source no-follow open failed"
        ) from exc
    if accounting is not None:
        accounting["source_content_opens"] = 1
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or stat.S_IMODE(opened.st_mode) != identity["mode"]
            or opened.st_size != identity["bytes"]
        ):
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                PRIVATE_FAILURE_ROUTES[1], "opened source identity differs"
            )
        payload = os.read(descriptor, identity["bytes"] + 1)
        if accounting is not None:
            accounting["source_bytes"] = len(payload)
    finally:
        os.close(descriptor)
    if len(payload) != identity["bytes"] or _sha256_bytes(payload) != identity["sha256"]:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            PRIVATE_FAILURE_ROUTES[1], "source content identity differs"
        )
    return payload


def _aggregate_report(
    *,
    route: str,
    generated: bool,
    source_bytes: int,
    output_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
    implementation_commit: str,
) -> dict[str, Any]:
    if generated:
        if route not in (SUCCESS_ROUTE, *PRIVATE_CLASS_ROUTES):
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[9], "generated aggregate route differs"
            )
    elif route not in PRIVATE_ROUTES:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "private aggregate route differs"
        )
    counters = _base_zero_counters()
    counters["private_structural_source_reads"] = 0 if generated else 1
    counters["private_structural_source_bytes"] = 0 if generated else source_bytes
    counters["VR23A_calls"] = 1
    counters["nested_VR20A_calls"] = 1
    counters["private_cohort_freezes"] = 0
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": route,
        "status": (
            "generated_fixture_qualified"
            if generated
            else "consumed_aggregate_class_only"
        ),
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "implementation_commit": implementation_commit,
            "VR20A_module_sha256": VR20A_MODULE_SHA256,
            "VR23A_module_sha256": VR23A_MODULE_SHA256,
        },
        "source_summary": {
            "structural_bytes": source_bytes,
            "registered_rows": 1227,
            "registered_regular_files": 1025,
            "registered_directories": 202,
            "registered_complete_bundles": 238,
            "registered_eligible_bundles": 195,
            "registered_valid_ineligible_bundles": 43,
        },
        "measurements": {
            "input_bytes": source_bytes,
            "combined_output_bytes": output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": counters,
        "warnings": [
            (
                "generated_fixture_only_no_real_or_private_source_access"
                if generated
                else "target_free_structural_class_only_no_neural_payload_access"
            ),
            "failed_predicate_value_row_path_and_identity_not_retained",
            "no_private_cohort_manifest_created",
            "FW2_execution_not_authorized",
            "CIL1_not_authorized",
            "no_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "structural_failure_detail",
            "source_exact_cohort",
            "archive_member_payload",
            "neural_signal",
            "target_or_label",
            "model_prediction_or_score",
            "decoding_accuracy",
            "live_latency",
        ],
        "claim_boundary": {
            "engineering_capability": "bounded target-free five-route F06 structural discrimination",
            "scientific_claim_not_established": (
                "No neural effect decoding performance language decoding live decoding "
                "or thought-to-text capability was tested."
            ),
        },
    }
    _walk_public(report)
    return report


def _private_route_for_refusal(exc: F06PrivateFiveRouteDiscriminatorRefusal) -> str:
    if exc.route in PRIVATE_FAILURE_ROUTES:
        return exc.route
    if exc.route == REFUSAL_ROUTES[6]:
        return PRIVATE_FAILURE_ROUTES[1]
    if exc.route == REFUSAL_ROUTES[7]:
        return PRIVATE_FAILURE_ROUTES[2]
    if exc.route in REFUSAL_ROUTES[8:]:
        return PRIVATE_FAILURE_ROUTES[3]
    return PRIVATE_FAILURE_ROUTES[0]


def _failure_report(
    route: str,
    *,
    accounting: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
    implementation_commit: str,
    generated: bool,
) -> dict[str, Any]:
    counters = _base_zero_counters()
    counters.update(
        {
            "private_structural_source_reads": (
                0 if generated else accounting["source_content_opens"]
            ),
            "private_structural_source_bytes": (
                0 if generated else accounting["source_bytes"]
            ),
            "generated_source_content_opens": (
                accounting["source_content_opens"] if generated else 0
            ),
            "generated_source_bytes": accounting["source_bytes"] if generated else 0,
            "strict_structural_parses": accounting["strict_parses"],
            "VR23A_calls": accounting["VR23A_calls"],
            "nested_VR20A_calls": accounting["nested_VR20A_calls"],
            "private_cohort_freezes": 0,
        }
    )
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": route,
        "status": (
            "generated_refusal_group_qualified"
            if generated
            else "consumed_without_cohort_freeze"
        ),
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "implementation_commit": implementation_commit,
            "VR20A_module_sha256": VR20A_MODULE_SHA256,
            "VR23A_module_sha256": VR23A_MODULE_SHA256,
        },
        "measurements": {
            "input_bytes": accounting["source_bytes"],
            "combined_output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": counters,
        "warnings": [
            (
                "generated_temporary_fixture_only"
                if generated
                else "one_registered_invocation_consumed_no_retry_or_rerun"
            ),
            "failure_detail_withheld_by_aggregate_privacy_contract",
            "no_private_cohort_manifest_was_created",
            "FW2_execution_not_authorized",
            "CIL1_not_authorized",
            "no_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "structural_failure_detail",
            "source_exact_cohort",
            "archive_member_payload",
            "neural_signal",
            "target_or_label",
            "model_prediction_or_score",
            "decoding_accuracy",
            "live_latency",
        ],
        "claim_boundary": {
            "engineering_capability": "bounded target-free five-route F06 structural discrimination",
            "scientific_claim_not_established": (
                "No neural effect decoding performance language decoding live decoding "
                "or thought-to-text capability was tested."
            ),
        },
    }
    _walk_public(report)
    return report


def _build_generated_case(generated_case: str, order: str) -> dict[str, Any]:
    if generated_case not in GENERATED_CASES:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated case is not registered"
        )
    if order not in discriminator.ORDERS:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated order is not registered"
        )
    return discriminator._build_case(generated_case, order)


def _adapt_and_discriminate(
    source: Mapping[str, Any], accounting: dict[str, int], *, generated: bool
) -> str:
    before = repair.vr2._canonical_source_bytes(source)
    accounting["VR23A_calls"] += 1
    accounting["nested_VR20A_calls"] += 1
    try:
        route, upstream_route = discriminator.discriminate_generated_source(source)
    except discriminator.F06FiveRouteDecompositionRefusal as exc:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            PRIVATE_FAILURE_ROUTES[3], "VR23A refused aggregate discrimination"
        ) from exc
    after = repair.vr2._canonical_source_bytes(source)
    if after != before:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            PRIVATE_FAILURE_ROUTES[3], "VR23A changed source"
        )
    if route == discriminator.SUCCESS_ROUTE:
        if upstream_route != repair.SUCCESS_ROUTE:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                PRIVATE_FAILURE_ROUTES[3], "VR23A success route disagrees"
            )
        return SUCCESS_ROUTE if generated else PRIVATE_FAILURE_ROUTES[2]
    if route in discriminator.RESULT_ROUTES:
        if upstream_route != repair.REFUSAL_ROUTES[5]:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                PRIVATE_FAILURE_ROUTES[3], "VR23A F06 route disagrees"
            )
        return PRIVATE_CLASS_ROUTES[discriminator.RESULT_ROUTES.index(route)]
    raise F06PrivateFiveRouteDiscriminatorRefusal(
        PRIVATE_FAILURE_ROUTES[3], "VR23A route is unknown"
    )


def _stable_report_bytes(report: dict[str, Any], *, other_output_bytes: int) -> tuple[bytes, int]:
    total = -1
    while report["measurements"]["combined_output_bytes"] != total:
        report["measurements"]["combined_output_bytes"] = total
        payload = _canonical_json_bytes(report)
        total = other_output_bytes + len(payload)
    report["measurements"]["combined_output_bytes"] = total
    payload = _canonical_json_bytes(report)
    final_total = other_output_bytes + len(payload)
    if final_total != total:
        report["measurements"]["combined_output_bytes"] = final_total
        payload = _canonical_json_bytes(report)
        final_total = other_output_bytes + len(payload)
    return payload, final_total


def _run_fixed_sequence(
    root: Path,
    *,
    samples: Sequence[Mapping[str, Any]],
    source_identity: Mapping[str, Any],
    implementation_commit: str,
    generated: bool,
    generated_case: str = "control_success",
    peak_rss: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    started = clock()
    accounting = {
        "source_content_opens": 0,
        "source_bytes": 0,
        "strict_parses": 0,
        "VR23A_calls": 0,
        "nested_VR20A_calls": 0,
    }
    certificate = _certificate(
        samples, implementation_commit=implementation_commit, generated=generated
    )
    certificate_bytes = _canonical_json_bytes(certificate)
    if len(certificate_bytes) > MAX_CERTIFICATE_BYTES:
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[10], "readiness certificate exceeds cap")
    readiness_parent = READINESS_RELATIVE_PATH.parent
    _create_fresh_directory(root, readiness_parent)
    readiness_path = root / READINESS_RELATIVE_PATH
    _write_exclusive(readiness_path, certificate_bytes, 0o600)

    source_path = root / PRIVATE_SOURCE_RELATIVE_PATH
    _safe_parent_chain(root, PRIVATE_SOURCE_RELATIVE_PATH)
    output_root = _create_fresh_directory(root, OUTPUT_ROOT_RELATIVE_PATH)
    marker = {
        "schema_name": MARKER_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_before_content_open",
        "implementation_commit": implementation_commit,
        "generated": generated,
    }
    marker_bytes = _canonical_json_bytes(marker)
    marker_path = output_root / MARKER_RELATIVE_NAME

    def finish_failure(exc: F06PrivateFiveRouteDiscriminatorRefusal) -> dict[str, Any]:
        if not marker_path.exists():
            _write_exclusive(marker_path, marker_bytes, 0o600)
        elapsed = clock() - started
        rss = peak_rss()
        route = _private_route_for_refusal(exc)
        report = _failure_report(
            route,
            accounting=accounting,
            runtime_seconds=elapsed,
            peak_rss_bytes=rss,
            implementation_commit=implementation_commit,
            generated=generated,
        )
        report_bytes, total = _stable_report_bytes(
            report,
            other_output_bytes=len(certificate_bytes) + len(marker_bytes),
        )
        if total > MAX_COMBINED_OUTPUT_BYTES:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                PRIVATE_FAILURE_ROUTES[4], "aggregate failure report exceeds cap"
            ) from exc
        _write_exclusive(output_root / REPORT_RELATIVE_NAME, report_bytes, 0o644)
        return {
            "report": report,
            "certificate_bytes": len(certificate_bytes),
            "marker_bytes": len(marker_bytes),
            "report_bytes": len(report_bytes),
            "combined_output_bytes": total,
            "VR23A_calls": accounting["VR23A_calls"],
            "nested_VR20A_calls": accounting["nested_VR20A_calls"],
            "source_content_opens": accounting["source_content_opens"],
        }

    try:
        _preflight_source(source_path, source_identity)
    except F06PrivateFiveRouteDiscriminatorRefusal as exc:
        return finish_failure(exc)

    _write_exclusive(marker_path, marker_bytes, 0o600)
    try:
        payload = _read_source_once(
            source_path,
            source_identity,
            preflighted=True,
            accounting=accounting,
        )
        source = _strict_json(payload)
        accounting["strict_parses"] = 1
        if generated and generated_case not in GENERATED_CASES:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                PRIVATE_FAILURE_ROUTES[4], "generated case differs"
            )
        route = _adapt_and_discriminate(source, accounting, generated=generated)
    except F06PrivateFiveRouteDiscriminatorRefusal as exc:
        return finish_failure(exc)

    try:
        elapsed = clock() - started
        rss = peak_rss()
        report = _aggregate_report(
            route=route,
            generated=generated,
            source_bytes=len(payload),
            output_bytes=0,
            runtime_seconds=elapsed,
            peak_rss_bytes=rss,
            implementation_commit=implementation_commit,
        )
        report_bytes, total = _stable_report_bytes(
            report,
            other_output_bytes=len(certificate_bytes) + len(marker_bytes),
        )
        _assert_resources(elapsed, rss, total, generated=generated)
        report_path = output_root / REPORT_RELATIVE_NAME
        _write_exclusive(report_path, report_bytes, 0o644)
    except F06PrivateFiveRouteDiscriminatorRefusal as exc:
        return finish_failure(exc)
    return {
        "report": report,
        "certificate_bytes": len(certificate_bytes),
        "marker_bytes": len(marker_bytes),
        "report_bytes": len(report_bytes),
        "combined_output_bytes": total,
        "VR23A_calls": 1,
        "nested_VR20A_calls": 1,
        "source_content_opens": 1,
    }


_ENVELOPE_EXPECTED: dict[str, Any] = {
    "decision_green": True,
    "decision_scope_unchanged": True,
    "decision_short_form_exact": True,
    "implementation_green": True,
    "implementation_exact": True,
    "implementation_proof_closeout_green": True,
    "thread_OMP": "1",
    "thread_OPENBLAS": "1",
    "thread_MKL": "1",
    "thread_NUMEXPR": "1",
    "thread_VECLIB": "1",
    "readiness_samples": 3,
    "readiness_interval_seconds": 5,
    "readiness_all_pass": True,
    "readiness_certificate_fresh": True,
    "readiness_certificate_mode": 0o600,
    "source_path_fixed": True,
    "source_parent_safe": True,
    "source_regular": True,
    "source_symlink": False,
    "source_mode": 0o600,
    "source_content_opens": 1,
    "source_strict_parses": 1,
    "source_mutations": 0,
    "source_bytes": 418_755,
    "source_rows": 1_227,
    "source_regular_files": 1_025,
    "source_directories": 202,
    "output_root_fresh": True,
    "output_root_symlink": False,
    "marker_mode": 0o600,
    "marker_before_open": True,
    "marker_writes": 1,
    "VR23A_calls": 1,
    "VR23A_calls_per_path": 1,
    "VR23A_source_exact": True,
    "VR23A_source_immutable": True,
    "VR23A_route_agreement": True,
    "VR23A_success_route": "MARC2VR23A-G1",
    "VR23A_class_route_1": "MARC2VR23A-R1",
    "VR23A_class_route_2": "MARC2VR23A-R2",
    "VR23A_class_route_3": "MARC2VR23A-R3",
    "VR23A_class_route_4": "MARC2VR23A-R4",
    "VR23A_class_route_5": "MARC2VR23A-R5",
    "VR23A_private_class_count": 5,
    "VR23A_non_F06_parks": True,
    "VR23A_unknown_parks": True,
    "nested_VR20A_calls": 1,
    "nested_VR20A_calls_per_path": 1,
    "nested_VR20A_source_exact": True,
    "nested_VR20A_required_task": "reachingandgrasping",
    "nested_VR20A_task_aliases_allowed": False,
    "nested_VR20A_task_casefolding_allowed": False,
    "nested_VR20A_run_token_regex": "[0-9]+",
    "nested_VR20A_width_ceiling_absent": True,
    "nested_VR20A_numeric_identity_canonical": True,
    "nested_VR20A_selected_semantic_runs": "1,2,3",
    "nested_VR20A_source_exact_names": True,
    "nested_VR20A_source_exact_reservation": True,
    "nested_VR20A_companion_spelling_exact": True,
    "nested_VR20A_normalized_collision_refused": True,
    "nested_VR20A_source_immutable": True,
    "VR24P_class_route_1": "MARC2VR24P-R1",
    "VR24P_class_route_2": "MARC2VR24P-R2",
    "VR24P_class_route_3": "MARC2VR24P-R3",
    "VR24P_class_route_4": "MARC2VR24P-R4",
    "VR24P_class_route_5": "MARC2VR24P-R5",
    "VR24P_readiness_route": "MARC2VR24P-R6",
    "VR24P_source_route": "MARC2VR24P-R7",
    "VR24P_non_F06_route": "MARC2VR24P-R8",
    "VR24P_unknown_route": "MARC2VR24P-R9",
    "private_manifest_allowed": False,
    "private_cohort_freeze_allowed": False,
    "private_failure_detail_allowed": False,
    "private_predicate_allowed": False,
    "private_value_allowed": False,
    "private_row_allowed": False,
    "private_identity_allowed": False,
    "aggregate_report_mode": 0o644,
    "aggregate_private_fields": 0,
    "aggregate_failure_reason_fields": 0,
    "aggregate_per_item_rows": 0,
    "aggregate_exception_fields": 0,
    "network_bytes": 0,
    "new_payload_bytes": 0,
    "archive_bytes": 0,
    "signal_bytes": 0,
    "target_bytes": 0,
    "model_runs": 0,
    "training_runs": 0,
    "prediction_sets": 0,
    "scoring_runs": 0,
    "FW2_operations": 0,
    "CIL1_operations": 0,
    "hardware_operations": 0,
    "other_project_operations": 0,
    "retries": 0,
    "reruns": 0,
    "resumes": 0,
    "fallbacks": 0,
    "substitutions": 0,
    "private_reinspections": 0,
    "post_result_amendments": 0,
    "consumed_VR22P_operations": 0,
    "claim_upgrades": 0,
}


def _envelope_route(key: str) -> str:
    if key.startswith("decision") or key.startswith("implementation"):
        return REFUSAL_ROUTES[0]
    if key.startswith("thread"):
        return REFUSAL_ROUTES[1]
    if key.startswith("readiness"):
        return REFUSAL_ROUTES[4]
    if key.startswith("source"):
        return REFUSAL_ROUTES[3]
    if key.startswith("output") or key.startswith("marker"):
        return REFUSAL_ROUTES[5]
    if key.startswith("VR23A") or key.startswith("nested_VR20A"):
        return REFUSAL_ROUTES[7]
    if key.startswith("VR24P") or key.startswith("private"):
        return REFUSAL_ROUTES[8]
    if key.startswith("aggregate"):
        return REFUSAL_ROUTES[9]
    return REFUSAL_ROUTES[11]


def _validate_envelope(envelope: Mapping[str, Any]) -> None:
    if set(envelope) != set(_ENVELOPE_EXPECTED):
        raise F06PrivateFiveRouteDiscriminatorRefusal(REFUSAL_ROUTES[11], "execution envelope fields differ")
    for key, expected in _ENVELOPE_EXPECTED.items():
        if type(envelope[key]) is not type(expected) or envelope[key] != expected:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                _envelope_route(key), "execution envelope value differs"
            )


def _different(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return value + "x"
    raise TypeError("unsupported envelope value")


def _run_direct_refusals() -> dict[str, int]:
    counts = {route: 0 for route in REFUSAL_ROUTES}
    for key, value in _ENVELOPE_EXPECTED.items():
        mutated = dict(_ENVELOPE_EXPECTED)
        mutated[key] = _different(value)
        try:
            _validate_envelope(mutated)
        except F06PrivateFiveRouteDiscriminatorRefusal as exc:
            counts[exc.route] += 1
        else:  # pragma: no cover
            raise AssertionError(f"mutation unexpectedly passed: {key}")
    for mutation in ("missing", "extra"):
        mutated = dict(_ENVELOPE_EXPECTED)
        if mutation == "missing":
            mutated.pop("decision_green")
        else:
            mutated["unexpected"] = 0
        try:
            _validate_envelope(mutated)
        except F06PrivateFiveRouteDiscriminatorRefusal as exc:
            counts[exc.route] += 1
        else:  # pragma: no cover
            raise AssertionError(f"field mutation unexpectedly passed: {mutation}")
    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        try:
            _walk_public({key: "forbidden"})
        except F06PrivateFiveRouteDiscriminatorRefusal as exc:
            counts[exc.route] += 1
        else:  # pragma: no cover
            raise AssertionError(f"public firewall mutation unexpectedly passed: {key}")
    return counts


def qualify_generated(
    *,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run one generated-only fixed-path qualification with zero retention."""

    started = clock()
    decision = load_decision()
    _validate_decision(decision)
    _validate_upstream_artifacts()
    _validate_thread_environment()
    outcomes: list[dict[str, Any]] = []
    generated_input_bytes = 0
    generated_output_bytes_written = 0
    peak_generated_output_bytes = 0
    replay_hashes = {
        f"{generated_case}:{order}": []
        for generated_case in GENERATED_CASES
        for order in discriminator.ORDERS
    }
    for replay in range(2):
        for generated_case in GENERATED_CASES:
            for order in discriminator.ORDERS:
                source = _build_generated_case(generated_case, order)
                payload = _canonical_json_bytes(source)
                replay_hashes[f"{generated_case}:{order}"].append(
                    _sha256_bytes(payload)
                )
                identity = {
                    "mode": 0o600,
                    "bytes": len(payload),
                    "sha256": _sha256_bytes(payload),
                }
                generated_input_bytes += len(payload)
                with tempfile.TemporaryDirectory(prefix="ndk-vr24p-") as temporary:
                    root = Path(temporary)
                    source_path = root / PRIVATE_SOURCE_RELATIVE_PATH
                    source_path.parent.mkdir(parents=True, mode=0o700)
                    source_path.write_bytes(payload)
                    os.chmod(source_path, 0o600)
                    result = _run_fixed_sequence(
                        root,
                        samples=_generated_samples(),
                        source_identity=identity,
                        implementation_commit="generated-implementation-pending",
                        generated=True,
                        generated_case=generated_case,
                        peak_rss=lambda: 32 * 1024**2,
                    )
                    generated_output_bytes_written += result["combined_output_bytes"]
                    peak_generated_output_bytes = max(
                        peak_generated_output_bytes, result["combined_output_bytes"]
                    )
                    outcome = {
                        "case": generated_case,
                        "order": order,
                        "replay": replay + 1,
                        "route": result["report"]["route"],
                        "VR23A_calls": result["VR23A_calls"],
                        "nested_VR20A_calls": result["nested_VR20A_calls"],
                        "source_content_opens": result["source_content_opens"],
                    }
                    outcomes.append(outcome)
                if root.exists():  # pragma: no cover
                    raise F06PrivateFiveRouteDiscriminatorRefusal(
                        REFUSAL_ROUTES[9], "temporary generated root was retained"
                    )
    route_counts = {
        route: sum(item["route"] == route for item in outcomes)
        for route in GENERATED_CASE_ROUTES.values()
    }
    success_outcomes = [item for item in outcomes if item["route"] == SUCCESS_ROUTE]
    if (
        len(outcomes) != 24
        or route_counts != {route: 4 for route in GENERATED_CASE_ROUTES.values()}
        or sum(item["VR23A_calls"] for item in outcomes) != 24
        or sum(item["nested_VR20A_calls"] for item in outcomes) != 24
        or sum(item["source_content_opens"] for item in outcomes) != 24
        or any(len(set(values)) != 1 for values in replay_hashes.values())
        or peak_generated_output_bytes > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated route matrix differs"
        )
    refusals = _run_direct_refusals()
    direct_refusals = sum(refusals.values())
    if direct_refusals < 80:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[11], "direct refusal floor not met"
        )
    elapsed = clock() - started
    rss = peak_rss()
    report = {
        "schema_name": QUALIFICATION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_only_qualified_no_private_or_real_path_access",
        "decision_proof": {
            "commit": GREEN_DECISION_COMMIT,
            "CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "base_job_id": GREEN_DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
        },
        "matrix": {
            "generated_cases": 6,
            "orders": 2,
            "replays": 2,
            "paths": len(outcomes),
            "success_paths": len(success_outcomes),
            "refusal_paths": len(outcomes) - len(success_outcomes),
            "route_counts": route_counts,
            "VR23A_calls": sum(item["VR23A_calls"] for item in outcomes),
            "nested_VR20A_calls": sum(
                item["nested_VR20A_calls"] for item in outcomes
            ),
            "generated_source_content_opens": sum(
                item["source_content_opens"] for item in outcomes
            ),
            "replay_source_hashes": replay_hashes,
            "deterministic_replay": True,
        },
        "refusals": {
            "direct_refusals": direct_refusals,
            "route_counts": dict(sorted(refusals.items())),
        },
        "measurements": {
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes_written": generated_output_bytes_written,
            "peak_incremental_output_bytes": peak_generated_output_bytes,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": elapsed,
            "peak_RSS_bytes": rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": _base_zero_counters(),
        "warnings": [
            "generated_temporary_root_only_no_repository_dot_codex_work_operation",
            "private_structural_source_not_statted_hashed_opened_or_read",
            "FW2_and_CIL1_not_authorized",
            "no_neural_decoding_or_scientific_claim",
        ],
        "claim_boundary": {
            "engineering_capability": "generated fixed-path five-route F06 discriminator qualification",
            "scientific_claim_not_established": (
                "No real cohort neural effect decoding performance language decoding "
                "live decoding or thought-to-text capability was tested."
            ),
        },
    }
    output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _walk_public(report)
    _assert_resources(elapsed, rss, output_bytes)
    return report


def _require_green_implementation(record: Mapping[str, Any], root: Path | None = None) -> str:
    proof = record.get("remote_implementation_proof")
    artifacts = record.get("implementation_artifacts")
    if (
        not isinstance(proof, dict)
        or proof.get("both_required_jobs_green") is not True
        or proof.get("scope_changed_after_qualification") is not False
        or not isinstance(proof.get("commit"), str)
        or len(proof["commit"]) != 40
        or any(character not in "0123456789abcdef" for character in proof["commit"])
        or type(proof.get("CI_run_id")) is not int
        or proof["CI_run_id"] <= 0
        or type(proof.get("base_job_id")) is not int
        or proof["base_job_id"] <= 0
        or type(proof.get("optional_neuro_job_id")) is not int
        or proof["optional_neuro_job_id"] <= 0
        or proof.get("qualification_route") != SUCCESS_ROUTE
        or proof.get("qualification_repeated_for_proof_closeout") is not False
        or proof.get("private_operations_during_proof_closeout") != 0
        or type(proof.get("implementation_registry_preproof_bytes")) is not int
        or proof["implementation_registry_preproof_bytes"] <= 0
        or not isinstance(proof.get("implementation_registry_preproof_sha256"), str)
        or len(proof["implementation_registry_preproof_sha256"]) != 64
        or not isinstance(proof.get("implementation_artifact_set_sha256"), str)
        or len(proof["implementation_artifact_set_sha256"]) != 64
        or not isinstance(artifacts, list)
        or not artifacts
    ):
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation is not remotely green"
        )
    repo = root or _repo_root()
    for artifact in artifacts:
        if (
            not isinstance(artifact, dict)
            or not isinstance(artifact.get("path"), str)
            or type(artifact.get("bytes")) is not int
            or artifact["bytes"] < 1
            or not isinstance(artifact.get("sha256"), str)
            or len(artifact["sha256"]) != 64
        ):
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "implementation artifact proof differs"
            )
        payload = _read_tracked(repo, Path(artifact["path"]))
        if len(payload) != artifact["bytes"] or _sha256_bytes(payload) != artifact["sha256"]:
            raise F06PrivateFiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "implementation artifact identity differs"
            )
    artifact_set_sha256 = _sha256_bytes(_canonical_json_bytes(artifacts))
    if proof["implementation_artifact_set_sha256"] != artifact_set_sha256:
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation artifact set differs"
        )
    return proof["commit"]


def _load_implementation(root: Path) -> dict[str, Any]:
    payload = _read_tracked(root, IMPLEMENTATION_RELATIVE_PATH)
    record = _strict_json(payload)
    if (
        record.get("schema_name")
        != "neurodecodekit.marc2_f06_private_five_route_discriminator_implementation"
        or record.get("lane_id") != LANE_ID
    ):
        raise F06PrivateFiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation record differs"
        )
    return record


def _observe_machine(root: Path, sequence: int) -> dict[str, Any]:
    load = os.getloadavg()[0]
    cpus = os.cpu_count() or 1
    return {
        "sequence": sequence,
        "observed_at_UTC": datetime.now(UTC).isoformat(),
        "logical_CPUs": cpus,
        "normalized_one_minute_load": load / cpus,
        "process_peak_RSS_bytes": _peak_rss_bytes(),
        "free_disk_bytes": shutil.disk_usage(root).free,
        "thread_environment_all_one": all(
            os.environ.get(name) == "1" for name in THREAD_ENVIRONMENT
        ),
    }


def _collect_readiness(root: Path) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    deadline = time.monotonic() + 600
    while time.monotonic() <= deadline:
        sample = _observe_machine(root, len(samples) + 1)
        if (
            sample["normalized_one_minute_load"] <= 1.0
            and sample["process_peak_RSS_bytes"] < MAX_PEAK_RSS_BYTES
            and sample["free_disk_bytes"] >= MINIMUM_FREE_DISK_BYTES
            and sample["thread_environment_all_one"] is True
        ):
            samples.append(sample)
            if len(samples) == REQUIRED_PASSING_SAMPLES:
                return samples
        else:
            samples.clear()
        time.sleep(MINIMUM_SAMPLE_INTERVAL_SECONDS)
    raise F06PrivateFiveRouteDiscriminatorRefusal(
        PRIVATE_FAILURE_ROUTES[0], "machine readiness did not pass"
    )


def execute_registered() -> dict[str, Any]:
    """Run the one fixed real confirmation only after exact green proof."""

    root = _repo_root()
    decision = load_decision(root)
    _validate_decision(decision)
    _validate_upstream_artifacts(root)
    implementation = _load_implementation(root)
    implementation_commit = _require_green_implementation(implementation, root)
    _validate_thread_environment()
    samples = _collect_readiness(root)
    return _run_fixed_sequence(
        root,
        samples=samples,
        source_identity=PRIVATE_SOURCE_IDENTITY,
        implementation_commit=implementation_commit,
        generated=False,
    )["report"]


def inspect_registered_report() -> dict[str, Any]:
    root = _repo_root()
    path = root / OUTPUT_ROOT_RELATIVE_PATH / REPORT_RELATIVE_NAME
    payload = path.read_bytes()
    report = _strict_json(payload)
    _walk_public(report)
    return report


def build_plan() -> dict[str, Any]:
    decision = load_decision()
    _validate_decision(decision)
    _validate_upstream_artifacts()
    implementation_proof_available = False
    implementation_path = _repo_root() / IMPLEMENTATION_RELATIVE_PATH
    if implementation_path.exists() and not implementation_path.is_symlink():
        try:
            record = _load_implementation(_repo_root())
            _require_green_implementation(record, _repo_root())
        except F06PrivateFiveRouteDiscriminatorRefusal:
            pass
        else:
            implementation_proof_available = True
    return {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_wrapper_implementation",
        "decision_green": True,
        "generated_paths": 24,
        "generated_success_paths": 4,
        "generated_refusal_paths": 20,
        "VR23A_calls": 24,
        "nested_VR20A_calls": 24,
        "direct_refusal_minimum": 80,
        "fixed_private_source_bytes": 418_755,
        "fixed_output_cap_bytes": MAX_COMBINED_OUTPUT_BYTES,
        "implementation_proof_available": implementation_proof_available,
        "private_execution_available": implementation_proof_available,
        "FW2_authorized": False,
        "CIL1_authorized": False,
        "claim_boundary": "structural engineering only; no neural claim",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proof-gated MARC2 target-free five-route F06 discriminator."
    )
    parser.add_argument("command", choices=("plan", "qualify", "inspect", "execute"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "plan":
        value = build_plan()
    elif args.command == "qualify":
        value = qualify_generated()
    elif args.command == "inspect":
        value = inspect_registered_report()
    else:
        value = execute_registered()
    print(json.dumps(value, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
