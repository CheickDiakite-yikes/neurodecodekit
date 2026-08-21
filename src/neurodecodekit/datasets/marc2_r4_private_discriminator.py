"""Proof-gated MARC2-VR13P target-free structural discriminator."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import resource
import shutil
import stat
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_p15_run_index_repair as vr12a
from neurodecodekit.datasets import marc2_r4_residual_decomposition as vr13a

LANE_ID = "MARC2-VR13P"
SCHEMA_VERSION = "0.1.0"
PLAN_SCHEMA_NAME = "neurodecodekit.marc2_r4_private_discriminator_plan"
QUALIFICATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_r4_private_discriminator_qualification"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_r4_private_discriminator_report"
PRIVATE_SCHEMA_NAME = "neurodecodekit.marc2_r4_private_structural_cohort"
CERTIFICATE_SCHEMA_NAME = "neurodecodekit.marc2_r4_readiness_certificate"
MARKER_SCHEMA_NAME = "neurodecodekit.marc2_r4_private_discriminator_consumed"

DECISION_RELATIVE_PATH = Path(
    "registries/marc2_r4_private_discriminator_authorization_decision.v0.json"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_r4_private_discriminator_authorization_request.v0.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_r4_private_discriminator_implementation.v0.json"
)
VR12A_MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_p15_run_index_repair.py"
)
VR12A_IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_p15_run_index_repair_implementation.v0.json"
)
VR12A_RESULT_RELATIVE_PATH = Path(
    "registries/marc2_p15_run_index_repair_result.v0.json"
)
VR13A_MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_r4_residual_decomposition.py"
)
VR13A_IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_r4_residual_decomposition_implementation.v0.json"
)
VR13A_RESULT_RELATIVE_PATH = Path(
    "registries/marc2_r4_residual_decomposition_result.v0.json"
)

DECISION_SHA256 = "2b2352c2e92183e0b3c6e7f4b470572772339836701b52ff6da0a9a8a34f54eb"
REQUEST_SHA256 = "e7684ed66df2689df2ac4eb5b19a9e71f09925313c2d49e3884f19560d8c11cd"
GREEN_DECISION_COMMIT = "fe16400fd0ccb5fa2ff40fffd413fee34eb620d6"
GREEN_DECISION_CI_RUN_ID = 32_439_821_302
GREEN_DECISION_BASE_JOB_ID = 96_648_078_587
GREEN_DECISION_OPTIONAL_JOB_ID = 96_648_078_452
VR12A_ARTIFACT_SHA256 = {
    VR12A_MODULE_RELATIVE_PATH:
        "e7321d2a2b347ae2a4d0294c59d06d8eeeb3c6f08bf279b2658d1d56a25aa2f6",
    VR12A_IMPLEMENTATION_RELATIVE_PATH:
        "ab9ecf59d466ff63cad572747945f5dd6942a7d69de0d70c37578c41447140f7",
    VR12A_RESULT_RELATIVE_PATH:
        "a439f1242ba469f389dc970fa9062eca1ba159b17ea262a6b22484009e5b9953",
}
VR13A_ARTIFACT_SHA256 = {
    VR13A_MODULE_RELATIVE_PATH:
        "a4ebd7890e60e37f181169b7d90ea03edeace6b364b1774b98921788416f0513",
    VR13A_IMPLEMENTATION_RELATIVE_PATH:
        "e117097047193108042e0aa9203dc7102fadb8f333789bb25fcd2ef49b25c9d7",
    VR13A_RESULT_RELATIVE_PATH:
        "1a23ed7b14166050070fe052193bdb8b05c22ebd055b1d0ba2a0eb65ae39d913",
}

PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
READINESS_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr13p/readiness.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_r4_private_discriminator/v0"
)
MARKER_RELATIVE_NAME = "consumed.marker.v0.json"
PRIVATE_MANIFEST_RELATIVE_NAME = "cohort.private.v0.json"
REPORT_RELATIVE_NAME = "report.aggregate.v0.json"
PRIVATE_SOURCE_IDENTITY = {
    "bytes": 418_755,
    "sha256": "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
    "mode": 0o600,
}

THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
GENERATED_SUCCESS_ROUTE = "MARC2VR13P-G1"
PRIVATE_SUCCESS_ROUTE = "MARC2VR13P-R1"
PRIVATE_RESIDUAL_ROUTES = tuple(f"MARC2VR13P-R{i}" for i in range(2, 9))
REFUSAL_ROUTES = tuple(f"MARC2VR13P-F{i:02d}" for i in range(1, 13))
VR13A_TO_PRIVATE_ROUTE = {
    f"MARC2VR13A-R{i}": f"MARC2VR13P-R{i + 1}" for i in range(1, 8)
}

MAX_GENERATED_RUNTIME_SECONDS = 60.0
MAX_PRIVATE_RUNTIME_SECONDS = 650.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_TRACKED_FILE_BYTES = 2 * 1024**2
MAX_CERTIFICATE_BYTES = 64 * 1024
REQUIRED_PASSING_SAMPLES = 3
MINIMUM_SAMPLE_INTERVAL_SECONDS = 5.0

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


class R4PrivateDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR13P refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR13P refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


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
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "canonical JSON refused"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "strict JSON refused"
        ) from exc
    if not isinstance(value, dict):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "top-level JSON object required"
        )
    return value


def _read_tracked(root: Path, relative: Path) -> bytes:
    if relative.is_absolute() or ".." in relative.parts:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked path differs"
        )
    path = root / relative
    try:
        info = path.lstat()
    except OSError as exc:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact type differs"
        )
    if info.st_size <= 0 or info.st_size > MAX_TRACKED_FILE_BYTES:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact size differs"
        )
    return path.read_bytes()


def _validate_decision(decision: Mapping[str, Any]) -> None:
    proof = decision.get("green_proof_closeout")
    request = decision.get("green_request")
    user = decision.get("user_authorization")
    authority = decision.get("authorization")
    caps = decision.get("resource_caps")
    routes = decision.get("private_route_contract")
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc2_r4_private_discriminator_authorization_decision"
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "bff3d3fc344291f57c5ef90c6affb8077e57d7c0"
        or not isinstance(proof, dict)
        or proof.get("commit") != "bff3d3fc344291f57c5ef90c6affb8077e57d7c0"
        or proof.get("CI_run_id") != 32_429_569_470
        or proof.get("base_python_job_id") != 96_618_310_916
        or proof.get("optional_neuro_job_id") != 96_618_311_046
        or proof.get("both_required_jobs_green") is not True
        or not isinstance(request, dict)
        or request.get("commit") != "d55371e8d95c562dc0e4eff7f3ea27820e2af7d0"
        or request.get("CI_run_id") != 32_428_583_270
        or request.get("both_required_jobs_green") is not True
        or not isinstance(user, dict)
        or user.get("actual_message_verbatim") != "continue"
        or user.get("actual_message_UTF8_bytes") != 8
        or user.get("actual_message_SHA256")
        != "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad"
        or user.get("sole_active_Tier_C_packet") != LANE_ID
        or user.get("one_registered_two_stage_sequence_only") is not True
        or user.get("scope_may_not_expand_by_inference") is not True
        or not isinstance(authority, dict)
        or authority.get("generated_wrapper_implementation_after_decision_green")
        is not True
        or authority.get("generated_wrapper_qualification_after_decision_green")
        is not True
        or authority.get("stage_1_proof_closeout_after_implementation_green")
        is not True
        or authority.get("one_private_structural_read_after_stage_1_green")
        is not True
        or authority.get("one_VR12A_call_after_stage_1_green") is not True
        or authority.get("one_VR13A_residual_map_call_maximum") is not True
        or authority.get("one_private_structural_cohort_freeze_on_R1") is not True
        or authority.get("implementation_or_private_access_authorized_now")
        is not False
        or authority.get("private_source_or_output_path_operation_authorized_now")
        is not False
        or authority.get("archive_member_or_payload_access_authorized_now")
        is not False
        or authority.get("neural_derivative_creation_authorized_now") is not False
        or authority.get(
            "training_prediction_freeze_target_delivery_or_scoring_authorized_now"
        )
        is not False
        or authority.get("FW2_or_CIL1_execution_authorized_now") is not False
        or authority.get(
            "retry_rerun_resume_substitution_fallback_or_amendment_authorized_now"
        )
        is not False
        or authority.get("release_publication_or_scientific_claim_upgrade_authorized_now")
        is not False
        or not isinstance(caps, dict)
        or caps.get("CPU_threads") != 1
        or caps.get("workers") != 1
        or caps.get("numerical_jobs") != 1
        or caps.get("private_source_read_bytes") != 418_755
        or caps.get("private_source_content_opens") != 1
        or caps.get("VR12A_calls") != 1
        or caps.get("VR13A_residual_map_calls_maximum") != 1
        or caps.get("network_bytes") != 0
        or caps.get("signal_bytes") != 0
        or caps.get("target_bytes") != 0
        or caps.get("combined_incremental_output_bytes") != 2 * 1024**2
        or caps.get("retry_rerun_resume_count") != 0
        or not isinstance(routes, list)
        or [row.get("route") for row in routes if isinstance(row, dict)]
        != [f"MARC2VR13P-R{i}" for i in range(1, 9)]
    ):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "authorization decision differs"
        )


def load_decision(root: Path | None = None) -> dict[str, Any]:
    fixed_root = root or _repo_root()
    payload = _read_tracked(fixed_root, DECISION_RELATIVE_PATH)
    if _sha256_bytes(payload) != DECISION_SHA256:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "authorization decision hash differs"
        )
    decision = _strict_json(payload)
    _validate_decision(decision)
    return decision


def _validate_green_dependencies(root: Path | None = None) -> None:
    fixed_root = root or _repo_root()
    request = _read_tracked(fixed_root, REQUEST_RELATIVE_PATH)
    if _sha256_bytes(request) != REQUEST_SHA256:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "request artifact differs"
        )
    for relative, expected in {
        **VR12A_ARTIFACT_SHA256,
        **VR13A_ARTIFACT_SHA256,
    }.items():
        if _sha256_bytes(_read_tracked(fixed_root, relative)) != expected:
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[1], "green dependency differs"
            )


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    current = environment or os.environ
    if any(current.get(key) != value for key, value in THREAD_ENVIRONMENT.items()):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "one-thread environment required"
        )


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower()
            if normalized in FORBIDDEN_PUBLIC_KEYS:
                raise R4PrivateDiscriminatorRefusal(
                    REFUSAL_ROUTES[8], "public output key refused"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_resources(
    *, runtime_seconds: float, peak_rss_bytes: int, output_bytes: int, private: bool
) -> None:
    limit = MAX_PRIVATE_RUNTIME_SECONDS if private else MAX_GENERATED_RUNTIME_SECONDS
    if (
        runtime_seconds < 0
        or runtime_seconds > limit
        or peak_rss_bytes < 0
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or output_bytes < 0
        or output_bytes > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "resource boundary refused"
        )


def _discriminate_source(
    source: Mapping[str, Any],
) -> tuple[str, vr12a.RepairedSelection | None, int]:
    before = vr12a.vr2._canonical_source_bytes(source)
    repaired: vr12a.RepairedSelection | None = None
    residual_calls = 0
    try:
        repaired = vr12a.adapt_repaired_source(source)
    except vr12a.P15RunIndexRepairRefusal as exc:
        residual_calls = 1
        generated_route = vr13a._route_for_refusal(exc)
        route = VR13A_TO_PRIVATE_ROUTE.get(generated_route)
        if route is None:
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[6], "residual route differs"
            ) from exc
    else:
        route = GENERATED_SUCCESS_ROUTE
    if vr12a.vr2._canonical_source_bytes(source) != before:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "source changed during discrimination"
        )
    return route, repaired, residual_calls


def _expected_generated_counts() -> dict[str, int]:
    return {
        GENERATED_SUCCESS_ROUTE: 4,
        **{route: 4 for route in PRIVATE_RESIDUAL_ROUTES},
    }


def _run_generated_matrix() -> dict[str, Any]:
    counts: Counter[str] = Counter()
    replay_rows: list[list[list[str]]] = []
    generated_input_bytes = 0
    vr12a_calls = 0
    residual_calls = 0
    for _replay in range(2):
        replay_result: list[list[str]] = []
        for order in vr13a.ORDERS:
            order_result: list[str] = []
            for case in vr13a.CASES:
                source = vr13a._build_case(case, order)
                generated_input_bytes += len(vr12a.vr2._canonical_source_bytes(source))
                route, _repaired, route_calls = _discriminate_source(source)
                vr12a_calls += 1
                residual_calls += route_calls
                counts[route] += 1
                order_result.append(route)
            replay_result.append(order_result)
        replay_rows.append(replay_result)
    if (
        replay_rows[0] != replay_rows[1]
        or dict(sorted(counts.items())) != _expected_generated_counts()
        or vr12a_calls != 32
        or residual_calls != 28
    ):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "generated matrix differs"
        )
    return {
        "route_counts": dict(sorted(counts.items())),
        "replay_sha256": _sha256_bytes(_canonical_json_bytes(replay_rows)),
        "generated_input_bytes": generated_input_bytes,
        "VR12A_calls": vr12a_calls,
        "VR13A_residual_map_calls": residual_calls,
    }


def _safe_parent_chain(root: Path, relative: Path) -> None:
    if relative.is_absolute() or ".." in relative.parts:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "fixed path differs"
        )
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[5], "fixed parent symlink refused"
            )


def _create_fresh_directory(root: Path, relative: Path) -> Path:
    _safe_parent_chain(root, relative)
    path = root / relative
    if path.exists() or path.is_symlink():
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "fixed output already exists"
        )
    try:
        path.mkdir(parents=True, mode=0o700)
        os.chmod(path, 0o700)
    except OSError as exc:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "fixed output creation refused"
        ) from exc
    return path


def _write_exclusive(path: Path, payload: bytes, mode: int) -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
    except OSError as exc:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "exclusive output creation refused"
        ) from exc
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    os.chmod(path, mode)
    return len(payload)


def _private_manifest(repaired: vr12a.RepairedSelection) -> dict[str, Any]:
    source_manifest = repaired.selection.private_manifest
    rows = source_manifest.get("rows") if isinstance(source_manifest, dict) else None
    if not isinstance(rows, list):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "private cohort envelope differs"
        )
    return {
        "schema_name": PRIVATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "source_exact_rows": rows,
        "cohort_summary": repaired.selection.cohort_summary,
        "split_summary": repaired.selection.split_summary,
        "byte_summary": repaired.selection.byte_summary,
        "semantic_cohort_sha256": repaired.semantic_cohort_sha256,
        "source_exact_selected_names_sha256": (
            repaired.source_exact_selected_names_sha256
        ),
    }


def _zero_counters() -> dict[str, int]:
    return {
        "raw_archive_header_or_member_payload_reads": 0,
        "signal_event_channel_geometry_target_or_label_reads": 0,
        "derivative_cache_feature_split_or_NeuroToken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "FW2_or_CIL1_operations": 0,
        "operations_on_other_projects": 0,
        "retry_rerun_resume_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _aggregate_report(
    *,
    route: str,
    repaired: vr12a.RepairedSelection | None,
    runtime_seconds: float,
    peak_rss_bytes: int,
    input_bytes: int,
    output_bytes: int,
    private: bool,
) -> dict[str, Any]:
    if route == GENERATED_SUCCESS_ROUTE:
        reported_route = PRIVATE_SUCCESS_ROUTE if private else route
    else:
        reported_route = route
    cohort = repaired.selection.cohort_summary if repaired is not None else {}
    split = repaired.selection.split_summary if repaired is not None else {}
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed" if private else "generated_qualification",
        "route": reported_route,
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI": GREEN_DECISION_CI_RUN_ID,
        },
        "aggregate": {
            "cohort_size": cohort.get("selected_subjects", 0),
            "bundle_count": split.get("selected_run_bundles", 0),
            "core_member_count": split.get("selected_core_members", 0),
            "fit_heldout_overlap": 0,
            "private_cohort_written": private and repaired is not None,
        },
        "resources": {
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
        },
        "counters": _zero_counters(),
        "warnings": [
            "This is a target-free structural result, not a neural result.",
            "FW2 remains a separate prospective packet even after R1.",
        ],
        "unavailable_fields": [
            "neural_payload",
            "decoding_metric",
            "live_latency",
            "FW2_result",
            "CIL1_result",
        ],
        "claim_boundary": {
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "live_decoding": False,
        },
    }
    _walk_public(report)
    return report


def _run_generated_state_machine(
    *, rss_reader: Callable[[], int] = _peak_rss_bytes
) -> dict[str, int]:
    source = vr13a._build_case("control_success", "canonical")
    payload = vr12a.vr2._canonical_source_bytes(source)
    with tempfile.TemporaryDirectory(prefix="marc2-vr13p-generated-") as name:
        root = Path(name)
        readiness = root / READINESS_RELATIVE_PATH
        output_root = _create_fresh_directory(root, OUTPUT_ROOT_RELATIVE_PATH)
        readiness.parent.mkdir(parents=True, mode=0o700)
        certificate = {
            "schema_name": CERTIFICATE_SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "generated": True,
            "passing_samples": 3,
        }
        certificate_bytes = _canonical_json_bytes(certificate)
        certificate_size = _write_exclusive(readiness, certificate_bytes, 0o600)
        marker = {
            "schema_name": MARKER_SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "generated": True,
        }
        marker_size = _write_exclusive(
            output_root / MARKER_RELATIVE_NAME,
            _canonical_json_bytes(marker),
            0o600,
        )
        parsed = _strict_json(payload)
        route, repaired, residual_calls = _discriminate_source(parsed)
        if route != GENERATED_SUCCESS_ROUTE or repaired is None or residual_calls != 0:
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[7], "generated fixed-path state differs"
            )
        private_size = _write_exclusive(
            output_root / PRIVATE_MANIFEST_RELATIVE_NAME,
            _canonical_json_bytes(_private_manifest(repaired)),
            0o600,
        )
        report = _aggregate_report(
            route=route,
            repaired=repaired,
            runtime_seconds=0.0,
            peak_rss_bytes=rss_reader(),
            input_bytes=len(payload),
            output_bytes=0,
            private=False,
        )
        report_size = _write_exclusive(
            output_root / REPORT_RELATIVE_NAME,
            _canonical_json_bytes(report),
            0o644,
        )
        total = certificate_size + marker_size + private_size + report_size
        if total > MAX_COMBINED_OUTPUT_BYTES:
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[9], "generated output cap refused"
            )
        return {
            "generated_state_input_bytes": len(payload),
            "generated_state_peak_output_bytes": total,
            "generated_state_VR12A_calls": 1,
            "generated_state_residual_map_calls": 0,
        }


def _expect_refusal(call: Callable[[], Any]) -> int:
    try:
        call()
    except R4PrivateDiscriminatorRefusal:
        return 1
    raise AssertionError("expected MARC2-VR13P refusal")


def _run_direct_refusals(decision: Mapping[str, Any]) -> dict[str, int]:
    local_total = 0
    malformed = (
        b"[]\n",
        b'{"a":1,"a":2}\n',
        b'{"a":NaN}\n',
        b"\xff",
    )
    for payload in malformed:
        local_total += _expect_refusal(lambda payload=payload: _strict_json(payload))
    for key in THREAD_ENVIRONMENT:
        missing = dict(THREAD_ENVIRONMENT)
        missing.pop(key)
        wrong = dict(THREAD_ENVIRONMENT)
        wrong[key] = "2"
        local_total += _expect_refusal(
            lambda missing=missing: _validate_thread_environment(missing)
        )
        local_total += _expect_refusal(
            lambda wrong=wrong: _validate_thread_environment(wrong)
        )
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("lane_id", "MARC2-VR13X"),
        lambda value: value.__setitem__("authorization_parent_commit", "0" * 40),
        lambda value: value["green_proof_closeout"].__setitem__("CI_run_id", 0),
        lambda value: value["green_proof_closeout"].__setitem__(
            "both_required_jobs_green", False
        ),
        lambda value: value["green_request"].__setitem__("commit", "0" * 40),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_verbatim", "approve"
        ),
        lambda value: value["authorization"].__setitem__(
            "archive_member_or_payload_access_authorized_now", True
        ),
        lambda value: value["authorization"].__setitem__(
            "FW2_or_CIL1_execution_authorized_now", True
        ),
        lambda value: value["resource_caps"].__setitem__("CPU_threads", 2),
        lambda value: value["private_route_contract"].pop(),
        lambda value: value["green_proof_closeout"].__setitem__(
            "base_python_job_id", 0
        ),
        lambda value: value["green_proof_closeout"].__setitem__(
            "optional_neuro_job_id", 0
        ),
        lambda value: value["green_request"].__setitem__("CI_run_id", 0),
        lambda value: value["green_request"].__setitem__(
            "both_required_jobs_green", False
        ),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_UTF8_bytes", 9
        ),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_SHA256", "0" * 64
        ),
        lambda value: value["user_authorization"].__setitem__(
            "one_registered_two_stage_sequence_only", False
        ),
        lambda value: value["user_authorization"].__setitem__(
            "scope_may_not_expand_by_inference", False
        ),
        lambda value: value["authorization"].__setitem__(
            "generated_wrapper_qualification_after_decision_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "stage_1_proof_closeout_after_implementation_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "one_private_structural_read_after_stage_1_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "one_VR12A_call_after_stage_1_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "one_VR13A_residual_map_call_maximum", False
        ),
        lambda value: value["authorization"].__setitem__(
            "one_private_structural_cohort_freeze_on_R1", False
        ),
        lambda value: value["authorization"].__setitem__(
            "implementation_or_private_access_authorized_now", True
        ),
        lambda value: value["authorization"].__setitem__(
            "private_source_or_output_path_operation_authorized_now", True
        ),
        lambda value: value["authorization"].__setitem__(
            "neural_derivative_creation_authorized_now", True
        ),
        lambda value: value["authorization"].__setitem__(
            "training_prediction_freeze_target_delivery_or_scoring_authorized_now",
            True,
        ),
        lambda value: value["authorization"].__setitem__(
            "retry_rerun_resume_substitution_fallback_or_amendment_authorized_now",
            True,
        ),
        lambda value: value["authorization"].__setitem__(
            "release_publication_or_scientific_claim_upgrade_authorized_now", True
        ),
    ]
    for mutate in mutations:
        changed = copy.deepcopy(dict(decision))
        mutate(changed)
        local_total += _expect_refusal(
            lambda changed=changed: _validate_decision(changed)
        )
    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        local_total += _expect_refusal(
            lambda key=key: _walk_public({key: "redacted"})
        )
    resource_cases = (
        (-1.0, 1, 1),
        (MAX_GENERATED_RUNTIME_SECONDS + 1, 1, 1),
        (1.0, -1, 1),
        (1.0, MAX_PEAK_RSS_BYTES + 1, 1),
        (1.0, 1, -1),
        (1.0, 1, MAX_COMBINED_OUTPUT_BYTES + 1),
    )
    for runtime_seconds, peak_rss_bytes, output_bytes in resource_cases:
        local_total += _expect_refusal(
            lambda runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            output_bytes=output_bytes: _assert_resources(
                runtime_seconds=runtime_seconds,
                peak_rss_bytes=peak_rss_bytes,
                output_bytes=output_bytes,
                private=False,
            )
        )
    with tempfile.TemporaryDirectory(prefix="marc2-vr13p-refusal-") as name:
        root = Path(name)
        local_total += _expect_refusal(
            lambda: _safe_parent_chain(root, Path("/absolute"))
        )
        local_total += _expect_refusal(
            lambda: _safe_parent_chain(root, Path("parent/../escape"))
        )
        (root / "linked").symlink_to(root / "missing", target_is_directory=True)
        local_total += _expect_refusal(
            lambda: _create_fresh_directory(root, Path("linked/output"))
        )
        output = _create_fresh_directory(root, Path("fixed/output"))
        local_total += _expect_refusal(
            lambda: _create_fresh_directory(root, Path("fixed/output"))
        )
        existing = output / "existing.json"
        _write_exclusive(existing, b"{}\n", 0o600)
        local_total += _expect_refusal(
            lambda: _write_exclusive(existing, b"{}\n", 0o600)
        )
        linked_output = output / "linked.json"
        linked_output.symlink_to(existing)
        local_total += _expect_refusal(
            lambda: _write_exclusive(linked_output, b"{}\n", 0o600)
        )
    total = local_total
    if total < 80:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "direct refusal minimum differs"
        )
    return {
        "wrapper_refusals": local_total,
        "total": total,
    }


def qualify_generated(
    *,
    environment: Mapping[str, str] | None = None,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the one bounded generated-only Stage 1 qualification."""

    started = time.monotonic()
    decision = load_decision()
    _validate_green_dependencies()
    _validate_thread_environment(environment)
    matrix = _run_generated_matrix()
    fixed_state = _run_generated_state_machine(rss_reader=rss_reader)
    refusals = _run_direct_refusals(decision)
    runtime = time.monotonic() - started
    peak_rss = rss_reader()
    report = {
        "schema_name": QUALIFICATION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "stage_1_generated_qualified_private_stage_closed",
        "route": GENERATED_SUCCESS_ROUTE,
        "matrix": matrix,
        "fixed_path_state_machine": fixed_state,
        "direct_refusals": refusals,
        "resources": {
            "generated_input_bytes": (
                matrix["generated_input_bytes"]
                + fixed_state["generated_state_input_bytes"]
            ),
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
            **_zero_counters(),
            "private_or_Git_ignored_path_operations": 0,
            "readiness_or_private_source_operations": 0,
            "real_VR12A_calls": 0,
            "real_VR13A_residual_map_calls": 0,
            "generated_VR12A_calls": matrix["VR12A_calls"] + 1,
            "generated_VR13A_residual_map_calls": matrix[
                "VR13A_residual_map_calls"
            ],
        },
        "warnings": [
            "Synthetic qualification demonstrates interface mechanics only.",
            "No private path, cohort, archive member, or neural payload was accessed.",
        ],
        "unavailable_fields": [
            "private_route",
            "real_cohort",
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
    output_size = len(_canonical_json_bytes(report))
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=output_size,
        private=False,
    )
    report["resources"]["aggregate_output_bytes"] = len(
        _canonical_json_bytes(report)
    )
    _walk_public(report)
    return report


def _load_implementation(root: Path) -> dict[str, Any]:
    return _strict_json(_read_tracked(root, IMPLEMENTATION_RELATIVE_PATH))


def _require_green_implementation(
    record: Mapping[str, Any], root: Path | None = None
) -> str:
    fixed_root = root or _repo_root()
    proof = record.get("remote_implementation_proof")
    artifacts = record.get("owned_artifacts")
    if not isinstance(proof, dict) or proof.get("both_required_jobs_green") is not True:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "remote implementation proof required"
        )
    commit = proof.get("commit")
    if not isinstance(commit, str) or len(commit) != 40:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation commit differs"
        )
    if not isinstance(artifacts, list) or not artifacts:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation artifacts unavailable"
        )
    for row in artifacts:
        if not isinstance(row, dict):
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "implementation artifact row differs"
            )
        relative = Path(str(row.get("path", "")))
        payload = _read_tracked(fixed_root, relative)
        if (
            len(payload) != row.get("bytes")
            or _sha256_bytes(payload) != row.get("sha256")
        ):
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "implementation artifact differs"
            )
    return commit


def _observe_machine(root: Path, sequence: int) -> dict[str, Any]:
    load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
    cpus = max(os.cpu_count() or 1, 1)
    return {
        "sequence": sequence,
        "captured_monotonic": time.monotonic(),
        "normalized_one_minute_load": load / cpus,
        "free_disk_bytes": shutil.disk_usage(root).free,
        "peak_RSS_bytes": _peak_rss_bytes(),
    }


def _sample_passes(sample: Mapping[str, Any]) -> bool:
    return (
        isinstance(sample.get("normalized_one_minute_load"), (int, float))
        and sample["normalized_one_minute_load"] <= 1.0
        and isinstance(sample.get("free_disk_bytes"), int)
        and sample["free_disk_bytes"] >= MINIMUM_FREE_DISK_BYTES
        and isinstance(sample.get("peak_RSS_bytes"), int)
        and sample["peak_RSS_bytes"] <= MAX_PEAK_RSS_BYTES
    )


def _collect_readiness(root: Path) -> list[dict[str, Any]]:
    started = time.monotonic()
    passing: list[dict[str, Any]] = []
    sequence = 0
    while time.monotonic() - started <= 600:
        sample = _observe_machine(root, sequence)
        sequence += 1
        if _sample_passes(sample):
            passing.append(sample)
            if len(passing) == REQUIRED_PASSING_SAMPLES:
                return passing
        else:
            passing.clear()
        time.sleep(MINIMUM_SAMPLE_INTERVAL_SECONDS)
    raise R4PrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[2], "fresh readiness did not pass"
    )


def _preflight_private_source(path: Path) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "registered private source unavailable"
        ) from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != PRIVATE_SOURCE_IDENTITY["mode"]
        or info.st_size != PRIVATE_SOURCE_IDENTITY["bytes"]
    ):
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "registered private source identity differs"
        )


def _read_private_once(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or stat.S_IMODE(info.st_mode) != PRIVATE_SOURCE_IDENTITY["mode"]
            or info.st_size != PRIVATE_SOURCE_IDENTITY["bytes"]
        ):
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[5], "private source changed before open"
            )
        chunks: list[bytes] = []
        remaining = PRIVATE_SOURCE_IDENTITY["bytes"]
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                raise R4PrivateDiscriminatorRefusal(
                    REFUSAL_ROUTES[5], "private source ended early"
                )
            chunks.append(chunk)
            remaining -= len(chunk)
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if _sha256_bytes(payload) != PRIVATE_SOURCE_IDENTITY["sha256"]:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "private source hash differs"
        )
    return payload


def execute_registered() -> dict[str, Any]:
    """Consume the one fixed private structural invocation after proof green."""

    root = _repo_root()
    started = time.monotonic()
    load_decision(root)
    _validate_green_dependencies(root)
    _validate_thread_environment()
    implementation = _load_implementation(root)
    implementation_commit = _require_green_implementation(implementation, root)
    samples = _collect_readiness(root)
    readiness_parent = READINESS_RELATIVE_PATH.parent
    readiness_directory = _create_fresh_directory(root, readiness_parent)
    certificate = {
        "schema_name": CERTIFICATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "implementation_commit": implementation_commit,
        "passing_samples": len(samples),
        "created_unix_seconds": time.time(),
    }
    certificate_payload = _canonical_json_bytes(certificate)
    if len(certificate_payload) > MAX_CERTIFICATE_BYTES:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "readiness certificate cap refused"
        )
    certificate_size = _write_exclusive(
        readiness_directory / READINESS_RELATIVE_PATH.name,
        certificate_payload,
        0o600,
    )
    _safe_parent_chain(root, OUTPUT_ROOT_RELATIVE_PATH)
    private_path = root / PRIVATE_SOURCE_RELATIVE_PATH
    _preflight_private_source(private_path)
    output_root = _create_fresh_directory(root, OUTPUT_ROOT_RELATIVE_PATH)
    marker = {
        "schema_name": MARKER_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "implementation_commit": implementation_commit,
        "content_open_limit": 1,
        "retry_rerun_resume": 0,
    }
    marker_size = _write_exclusive(
        output_root / MARKER_RELATIVE_NAME,
        _canonical_json_bytes(marker),
        0o600,
    )
    payload = _read_private_once(private_path)
    source = _strict_json(payload)
    route, repaired, residual_calls = _discriminate_source(source)
    if route == GENERATED_SUCCESS_ROUTE:
        route = PRIVATE_SUCCESS_ROUTE
    private_size = 0
    if route == PRIVATE_SUCCESS_ROUTE:
        if repaired is None:
            raise R4PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[7], "R1 cohort unavailable"
            )
        private_size = _write_exclusive(
            output_root / PRIVATE_MANIFEST_RELATIVE_NAME,
            _canonical_json_bytes(_private_manifest(repaired)),
            0o600,
        )
    elif route not in PRIVATE_RESIDUAL_ROUTES or repaired is not None:
        raise R4PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "private route envelope differs"
        )
    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    report = _aggregate_report(
        route=route,
        repaired=repaired,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        input_bytes=len(payload),
        output_bytes=0,
        private=True,
    )
    report["resources"]["private_content_opens"] = 1
    report["resources"]["strict_JSON_parses"] = 1
    report["resources"]["VR12A_calls"] = 1
    report["resources"]["VR13A_residual_map_calls"] = residual_calls
    report_payload = _canonical_json_bytes(report)
    total_without_report = certificate_size + marker_size + private_size
    total_output = total_without_report + len(report_payload)
    report["resources"]["output_bytes"] = total_output
    report_payload = _canonical_json_bytes(report)
    total_output = total_without_report + len(report_payload)
    report["resources"]["output_bytes"] = total_output
    report_payload = _canonical_json_bytes(report)
    total_output = total_without_report + len(report_payload)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=total_output,
        private=True,
    )
    _write_exclusive(output_root / REPORT_RELATIVE_NAME, report_payload, 0o644)
    return report


def inspect_registered_report() -> dict[str, Any]:
    root = _repo_root()
    path = root / OUTPUT_ROOT_RELATIVE_PATH / REPORT_RELATIVE_NAME
    payload = path.read_bytes()
    report = _strict_json(payload)
    _walk_public(report)
    return report


def build_plan() -> dict[str, Any]:
    decision = load_decision()
    _validate_green_dependencies()
    return {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "decision_green_stage_1_available_private_stage_proof_gated",
        "fixed_interface": decision["future_interface"]["CLI_commands"],
        "generated_paths": 32,
        "private_content_open_limit": 1,
        "private_input_bytes": 418_755,
        "CPU_threads": 1,
        "workers": 1,
        "network_bytes": 0,
        "archive_member_bytes": 0,
        "signal_bytes": 0,
        "target_bytes": 0,
        "warnings": [
            "Execute refuses until exact Stage 1 proof is remotely green.",
            "R1 only enables a separate prospective FW2 preregistration.",
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
            result = inspect_registered_report()
        else:
            result = execute_registered()
    except R4PrivateDiscriminatorRefusal as exc:
        print(json.dumps({"status": "refused", "route": exc.route}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
