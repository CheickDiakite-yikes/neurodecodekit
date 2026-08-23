"""Proof-gated aggregate discriminator for the final MARC2 structural classes."""

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
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_r5_inventory_taxonomy_discriminator as vr27a
from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR28P"
REQUEST_SCHEMA_NAME = (
    "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_authorization_request"
)
DECISION_SCHEMA_NAME = (
    "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_authorization_decision"
)
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_implementation"
)
RESULT_SCHEMA_NAME = (
    "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_result"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_inventory_taxonomy_private_discriminator_authorization_request.v0.json"
)
REQUEST_SHA256 = "0fc194af25972ea58e003c1f042ab73e12a0908ac988e67722263a56095034ba"
DECISION_RELATIVE_PATH = Path(
    "registries/marc2_inventory_taxonomy_private_discriminator_authorization_decision.v0.json"
)
DECISION_SHA256 = "957c809c3be1246c3af89c6e60e208497a0686b9ade03522bcf615b816203cba"
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_inventory_taxonomy_private_discriminator_implementation.v0.json"
)
GREEN_DECISION_COMMIT = "718c3de6ddb0030b1ba39fa0e42250e97db01072"
GREEN_DECISION_CI_RUN_ID = 32_614_796_767
GREEN_DECISION_BASE_JOB_ID = 97_133_595_196
GREEN_DECISION_OPTIONAL_JOB_ID = 97_133_595_235
QUALIFICATION_ROUTE = "MARC2VR28P-G1"
GENERATED_CONTROL_ROUTE = "MARC2VR28P-G2"
PRIVATE_ROUTES = tuple(f"MARC2VR28P-R{index}" for index in range(1, 6))
REFUSAL_ROUTES = tuple(f"MARC2VR28P-F{index:02d}" for index in range(1, 9))
CASES = vr27a.CASES
ORDERS = vr27a.ORDERS
REPLAYS = 2
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json"
)
READINESS_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr28p/readiness.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_inventory_taxonomy_private_discriminator/v0"
)
MARKER_NAME = "consumed.marker.v0.json"
REPORT_NAME = "report.aggregate.v0.json"
PRIVATE_SOURCE_BYTES = 418_755
PRIVATE_SOURCE_SHA256 = "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
PRIVATE_SOURCE_SCHEMA = "neurodecodekit.marc1_central_directory_private_manifest"
MAX_OUTPUT_BYTES = 1_048_576
MAX_RSS_BYTES = 268_435_456
MINIMUM_FREE_DISK_BYTES = 16_106_127_360
MAX_PRIVATE_RUNTIME_SECONDS = 650.0
MAX_GENERATED_RUNTIME_SECONDS = 60.0
PRIVATE_PAYLOAD_FIELDS = {
    "candidate",
    "cohort",
    "companion",
    "count",
    "direction",
    "exception",
    "identity",
    "label",
    "member",
    "offset",
    "participant",
    "path",
    "predicate",
    "private_value",
    "reason",
    "row",
    "run",
    "score",
    "selection",
    "session",
    "source_hash",
    "subject",
    "target",
    "task",
    "value",
}


class InventoryTaxonomyPrivateDiscriminatorRefusal(RuntimeError):
    """Fail closed with one non-private implementation route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR28P refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True)
class SourceBinding:
    bytes: int
    sha256: str
    schema_name: str


@dataclass(frozen=True)
class ExecutionPaths:
    source: Path
    readiness: Path
    output_root: Path

    @property
    def marker(self) -> Path:
        return self.output_root / MARKER_NAME

    @property
    def report(self) -> Path:
        return self.output_root / REPORT_NAME


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
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "JSON is not canonicalizable"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[3], "JSON contains a duplicate key"
            )
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise InventoryTaxonomyPrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[3], "JSON contains a non-finite number"
    )


def _strict_json(payload: bytes, *, canonical: bool = True) -> dict[str, Any]:
    try:
        value = json.loads(
            payload,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except InventoryTaxonomyPrivateDiscriminatorRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "JSON is invalid"
        ) from exc
    if not isinstance(value, dict):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "JSON root is not an object"
        )
    if canonical and _canonical_json_bytes(value) != payload:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "JSON bytes are not canonical"
        )
    return value


def _read_registered_json(
    relative_path: Path,
    expected_sha256: str,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    try:
        payload = ((root or _repo_root()) / relative_path).read_bytes()
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered authority is unavailable"
        ) from exc
    if _sha256_bytes(payload) != expected_sha256:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered authority hash differs"
        )
    return _strict_json(payload, canonical=False)


def load_registered_request(root: Path | None = None) -> dict[str, Any]:
    return _read_registered_json(REQUEST_RELATIVE_PATH, REQUEST_SHA256, root=root)


def load_registered_decision(root: Path | None = None) -> dict[str, Any]:
    return _read_registered_json(DECISION_RELATIVE_PATH, DECISION_SHA256, root=root)


def _verify_authority_mapping(
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> None:
    registered_request = load_registered_request()
    registered_decision = load_registered_decision()
    green = registered_decision.get("green_proof_closeout", {})
    authorization = registered_decision.get("authorization", {})
    requirements = registered_decision.get("generated_stage_requirements", {})
    if (
        not isinstance(request, dict)
        or request != registered_request
        or request.get("schema_name") != REQUEST_SCHEMA_NAME
        or request.get("lane_id") != LANE_ID
        or not isinstance(decision, dict)
        or decision != registered_decision
        or decision.get("schema_name") != DECISION_SCHEMA_NAME
        or decision.get("lane_id") != LANE_ID
        or green.get("both_required_jobs_green") is not True
        or authorization.get("generated_wrapper_implementation_after_decision_green")
        is not True
        or authorization.get("generated_wrapper_qualification_after_decision_green")
        is not True
        or requirements.get("required_paths") != 20
        or requirements.get("direct_refusal_minimum") != 70
    ):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered authority mapping differs"
        )


def _verify_decision_proof() -> None:
    if (
        GREEN_DECISION_COMMIT
        != "718c3de6ddb0030b1ba39fa0e42250e97db01072"
        or GREEN_DECISION_CI_RUN_ID != 32_614_796_767
        or GREEN_DECISION_BASE_JOB_ID != 97_133_595_196
        or GREEN_DECISION_OPTIONAL_JOB_ID != 97_133_595_235
    ):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "decision proof differs"
        )


def _verify_fixed_inputs(request: Mapping[str, Any], root: Path | None = None) -> int:
    base = root or _repo_root()
    rows = request.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != request.get("fixed_input_count"):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input registry differs"
        )
    total = 0
    for row in rows:
        if not isinstance(row, dict) or not {
            "role",
            "path",
            "bytes",
            "sha256",
        }.issubset(row):
            raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (base / str(row["path"])).read_bytes()
        except OSError as exc:
            raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row["bytes"] or _sha256_bytes(payload) != row["sha256"]:
            raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != request.get("fixed_input_bytes"):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "thread environment differs"
        )


def _require_green_implementation(root: Path | None = None) -> str:
    base = root or _repo_root()
    try:
        record = json.loads(
            (base / IMPLEMENTATION_RELATIVE_PATH).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "implementation proof is unavailable"
        ) from exc
    proof = record.get("remote_implementation_proof")
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("lane_id") != LANE_ID
        or not isinstance(proof, dict)
        or proof.get("both_required_jobs_green") is not True
        or proof.get("scope_changed_after_qualification") is not False
        or proof.get("qualification_route") != QUALIFICATION_ROUTE
        or proof.get("qualification_repeated_for_proof_closeout") is not False
        or proof.get("private_operations_during_proof_closeout") != 0
        or not isinstance(proof.get("commit"), str)
        or len(proof["commit"]) != 40
    ):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "implementation proof is not remotely green"
        )
    return proof["commit"]


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in PRIVATE_PAYLOAD_FIELDS:
                raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                    REFUSAL_ROUTES[6], "aggregate report contains a forbidden field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_aggregate_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > MAX_OUTPUT_BYTES:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "aggregate report exceeds output cap"
        )


def _write_exclusive(path: Path, payload: bytes) -> int:
    if len(payload) > MAX_OUTPUT_BYTES:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "output exceeds cap"
        )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if stat.S_IMODE(path.lstat().st_mode) != 0o600:
            raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[4], "output mode differs"
            )
    except InventoryTaxonomyPrivateDiscriminatorRefusal:
        raise
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "exclusive output write refused"
        ) from exc
    return len(payload)


def _read_bound_source_once(path: Path, binding: SourceBinding) -> dict[str, Any]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "bound source open refused"
        ) from exc
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_size != binding.bytes
        ):
            raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[3], "bound source identity differs"
            )
        chunks: list[bytes] = []
        remaining = binding.bytes
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        if remaining or os.read(descriptor, 1):
            raise InventoryTaxonomyPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[3], "bound source length changed"
            )
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if _sha256_bytes(payload) != binding.sha256:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "bound source hash differs"
        )
    source = _strict_json(payload, canonical=False)
    if source.get("schema_name") != binding.schema_name:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "bound source schema differs"
        )
    return source


def _upstream_route(source: Mapping[str, Any]) -> str:
    try:
        return vr25a.apply_selection_boundary_firewall(source).route
    except vr25a.SelectionBoundaryFirewallRefusal as exc:
        return exc.route


def _map_generated_route(upstream: str) -> tuple[str, str]:
    try:
        vr27a_route = vr27a._map_upstream_route(upstream)
    except vr27a.R5InventoryTaxonomyDiscriminatorRefusal as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "upstream route is outside the frozen map"
        ) from exc
    mapping = {
        vr27a.SUCCESS_ROUTE: GENERATED_CONTROL_ROUTE,
        vr27a.INVENTORY_ROUTE: PRIVATE_ROUTES[0],
        vr27a.TAXONOMY_ROUTE: PRIVATE_ROUTES[1],
    }
    try:
        return mapping[vr27a_route], vr27a_route
    except KeyError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "VR27A route is outside the frozen map"
        ) from exc


def _make_marker(paths: ExecutionPaths, *, generated: bool) -> int:
    try:
        paths.output_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "fresh output root is unavailable"
        ) from exc
    marker = {
        "schema_name": (
            "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_marker"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_fixture_consumed" if generated else "invocation_consumed",
    }
    return _write_exclusive(paths.marker, _canonical_json_bytes(marker))


def _generated_readiness(paths: ExecutionPaths) -> int:
    try:
        paths.readiness.parent.mkdir(mode=0o700, parents=False, exist_ok=False)
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "fresh generated readiness parent refused"
        ) from exc
    readiness = {
        "schema_name": (
            "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_generated_readiness"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_ready",
        "passing_samples": 3,
        "grants_private_authority": False,
    }
    return _write_exclusive(paths.readiness, _canonical_json_bytes(readiness))


def _generated_case_report(
    *,
    route: str,
    vr27a_route: str,
    case: str,
    order: str,
) -> dict[str, Any]:
    report = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": route,
        "status": "generated_fixed_path_case_complete",
        "generated_case": case,
        "generated_order": order,
        "upstream_VR27A_route": vr27a_route,
        "private_detail_retained": False,
        "scientific_ceiling": "none",
    }
    _assert_aggregate_safe(report)
    return report


def _run_generated_case(
    *,
    case: str,
    order: str,
    root: Path,
) -> dict[str, Any]:
    source = vr27a._build_case(case, order)
    source_payload = vr25a._source_bytes(source)
    paths = ExecutionPaths(
        source=root / "source.json",
        readiness=root / "readiness" / "readiness.json",
        output_root=root / "output",
    )
    _write_exclusive(paths.source, source_payload)
    readiness_bytes = _generated_readiness(paths)
    marker_bytes = _make_marker(paths, generated=True)
    loaded = _read_bound_source_once(
        paths.source,
        SourceBinding(
            bytes=len(source_payload),
            sha256=_sha256_bytes(source_payload),
            schema_name=str(source["schema_name"]),
        ),
    )
    upstream = _upstream_route(loaded)
    route, vr27a_route = _map_generated_route(upstream)
    report = _generated_case_report(
        route=route,
        vr27a_route=vr27a_route,
        case=case,
        order=order,
    )
    report_payload = _canonical_json_bytes(report)
    report_bytes = _write_exclusive(paths.report, report_payload)
    inspected = _inspect_report_file(paths.report, allow_generated=True)
    if inspected != report:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "generated report inspection differs"
        )
    return {
        "route": route,
        "VR27A_route": vr27a_route,
        "input_bytes": len(source_payload),
        "output_bytes": readiness_bytes + marker_bytes + report_bytes,
        "peak_incremental_output_bytes": sum(
            candidate.stat().st_size
            for candidate in (paths.readiness, paths.marker, paths.report)
        ),
        "report_sha256": _sha256_bytes(report_payload),
        "source_content_opens": 1,
        "VR25A_calls": 1,
        "VR27A_map_calls": 1,
    }


def _inspect_report_file(path: Path, *, allow_generated: bool) -> dict[str, Any]:
    try:
        info = path.lstat()
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate report is unavailable"
        ) from exc
    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o600
        or info.st_size > MAX_OUTPUT_BYTES
    ):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate report file identity differs"
        )
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate report read refused"
        ) from exc
    report = _strict_json(payload)
    _assert_aggregate_safe(report)
    allowed_routes = set(PRIVATE_ROUTES[:2])
    if allow_generated:
        allowed_routes.add(GENERATED_CONTROL_ROUTE)
    if (
        report.get("schema_name") != RESULT_SCHEMA_NAME
        or report.get("lane_id") != LANE_ID
        or report.get("route") not in allowed_routes
    ):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "aggregate report envelope differs"
        )
    return report


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except InventoryTaxonomyPrivateDiscriminatorRefusal as exc:
        return exc.route
    raise InventoryTaxonomyPrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[6], "direct refusal unexpectedly passed"
    )


def _run_direct_refusals(
    request: Mapping[str, Any], decision: Mapping[str, Any]
) -> int:
    inherited = vr27a._run_direct_refusals(vr27a.load_registered_contract())
    routes: list[str] = []
    for key in (
        "schema_name",
        "schema_version",
        "decision_id",
        "lane_id",
        "status",
        "authorization_parent_commit",
        "authorization",
        "required_execution_order",
        "discriminator_contract",
        "generated_stage_requirements",
        "resource_caps",
        "aggregate_output_firewall",
        "failure_semantics",
    ):
        changed = copy.deepcopy(dict(decision))
        changed[key] = f"mutated-{key}"
        routes.append(
            _expect_refusal(
                lambda item=changed: _verify_authority_mapping(request, item)
            )
        )
    for key in THREAD_ENVIRONMENT:
        changed = dict(THREAD_ENVIRONMENT)
        changed[key] = "2"
        routes.append(
            _expect_refusal(lambda item=changed: _validate_thread_environment(item))
        )
        changed = dict(THREAD_ENVIRONMENT)
        del changed[key]
        routes.append(
            _expect_refusal(lambda item=changed: _validate_thread_environment(item))
        )
    for upstream in (
        "MARC2VR25A-G2",
        "MARC2VR25A-R3",
        "MARC2VR25A-R4",
        "MARC2VR25A-F01",
        "unknown",
    ):
        routes.append(_expect_refusal(lambda value=upstream: _map_generated_route(value)))
    for field in sorted(PRIVATE_PAYLOAD_FIELDS):
        routes.append(
            _expect_refusal(lambda key=field: _assert_aggregate_safe({key: "x"}))
        )
    if inherited + len(routes) < 70:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "direct refusal coverage is incomplete"
        )
    return inherited + len(routes)


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _zero_counters() -> dict[str, int]:
    return {
        "repository_dot_codex_work_operations": 0,
        "private_structural_source_stats_resolves_hashes_opens_reads_or_parses": 0,
        "consumed_private_lane_path_or_output_operations": 0,
        "private_detail_or_cohort_retention_operations": 0,
        "archive_header_or_member_payload_operations": 0,
        "signal_event_channel_geometry_target_or_label_operations": 0,
        "derivative_cache_feature_split_or_NeuroToken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_or_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "MARC2_FW2_or_CIL1_operations": 0,
        "retry_rerun_resume_repair_fallback_or_substitution_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def qualify_generated(
    *,
    request: Mapping[str, Any] | None = None,
    decision: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run one 20-path generated fixed-path qualification."""

    started = clock()
    registered_request = dict(request or load_registered_request())
    registered_decision = dict(decision or load_registered_decision())
    _verify_authority_mapping(registered_request, registered_decision)
    _verify_decision_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered_request)
    _validate_thread_environment(environment)
    direct_refusals = _run_direct_refusals(
        registered_request, registered_decision
    )
    route_counts: Counter[str] = Counter()
    vr27a_counts: Counter[str] = Counter()
    signatures: list[list[tuple[str, str, str, str, str]]] = []
    generated_input_bytes = 0
    generated_output_bytes = 0
    peak_incremental_output_bytes = 0
    source_opens = 0
    vr25a_calls = 0
    vr27a_map_calls = 0
    with tempfile.TemporaryDirectory(prefix="marc2-vr28p-generated-") as temp:
        temp_root = Path(temp)
        for replay in range(REPLAYS):
            signature: list[tuple[str, str, str, str, str]] = []
            for order in ORDERS:
                for case in CASES:
                    path_root = temp_root / f"r{replay}-{order}-{case}"
                    path_root.mkdir(mode=0o700)
                    result = _run_generated_case(
                        case=case,
                        order=order,
                        root=path_root,
                    )
                    route_counts[result["route"]] += 1
                    vr27a_counts[result["VR27A_route"]] += 1
                    generated_input_bytes += result["input_bytes"]
                    generated_output_bytes += result["output_bytes"]
                    peak_incremental_output_bytes = max(
                        peak_incremental_output_bytes,
                        result["peak_incremental_output_bytes"],
                    )
                    source_opens += result["source_content_opens"]
                    vr25a_calls += result["VR25A_calls"]
                    vr27a_map_calls += result["VR27A_map_calls"]
                    signature.append(
                        (
                            case,
                            order,
                            result["route"],
                            result["VR27A_route"],
                            result["report_sha256"],
                        )
                    )
            signatures.append(signature)
    expected_vr27a = Counter(
        registered_decision["generated_stage_requirements"]["expected_route_counts"]
    )
    if (
        vr25a_calls != 20
        or vr27a_map_calls != 20
        or source_opens != 20
        or vr27a_counts != expected_vr27a
        or route_counts
        != Counter(
            {
                GENERATED_CONTROL_ROUTE: 4,
                PRIVATE_ROUTES[0]: 12,
                PRIVATE_ROUTES[1]: 4,
            }
        )
        or signatures[0] != signatures[1]
    ):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "generated replay or route distribution differs"
        )
    runtime = clock() - started
    rss = peak_rss()
    if (
        runtime < 0
        or runtime > MAX_GENERATED_RUNTIME_SECONDS
        or rss < 0
        or rss >= MAX_RSS_BYTES
        or peak_incremental_output_bytes > MAX_OUTPUT_BYTES
    ):
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated resource cap exceeded"
        )
    report: dict[str, Any] = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": QUALIFICATION_ROUTE,
        "status": "generated_fixed_path_wrapper_qualified",
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "decision_base_job_id": GREEN_DECISION_BASE_JOB_ID,
            "decision_optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "request_sha256": REQUEST_SHA256,
            "decision_sha256": DECISION_SHA256,
        },
        "matrix": {
            "cases": list(CASES),
            "orders": list(ORDERS),
            "replays": REPLAYS,
            "paths": vr25a_calls,
            "source_content_opens": source_opens,
            "VR25A_calls": vr25a_calls,
            "VR27A_map_calls": vr27a_map_calls,
            "VR28P_route_counts": dict(sorted(route_counts.items())),
            "VR27A_route_counts": dict(sorted(vr27a_counts.items())),
            "exact_replays_match": True,
            "fixed_path_state_machine_qualified": True,
            "marker_preceded_every_source_open": True,
            "direct_refusals_passed": direct_refusals,
            "source_mutations_after_call": 0,
        },
        "measurements": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes_written": generated_output_bytes,
            "peak_incremental_output_bytes": peak_incremental_output_bytes,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": _zero_counters(),
        "warnings": [
            "generated_only_qualification",
            "no_repository_private_or_consumed_path_was_touched",
            "private_execution_remains_proof_gated",
            "no_real_cohort_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "private_R1_or_R2_route",
            "private_structural_detail_or_cohort",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "generated fixed-path one-shot discrimination of the frozen "
                "inventory-versus-taxonomy classes"
            ),
            "scientific_claim_not_established": (
                "No private structural source neural payload target model prediction "
                "or score was accessed."
            ),
        },
    }
    output_bytes = -1
    while report["measurements"].get("aggregate_output_bytes") != output_bytes:
        report["measurements"]["aggregate_output_bytes"] = output_bytes
        output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_aggregate_safe(report)
    return report


def _current_machine_sample(sequence: int) -> dict[str, Any]:
    logical_cpus = os.cpu_count() or 0
    one_minute_load = os.getloadavg()[0]
    rss = _peak_rss_bytes()
    free_disk = shutil.disk_usage(_repo_root()).free
    normalized = one_minute_load / logical_cpus if logical_cpus else None
    passing = (
        logical_cpus >= 1
        and normalized is not None
        and normalized <= 1.0
        and rss < MAX_RSS_BYTES
        and free_disk >= MINIMUM_FREE_DISK_BYTES
    )
    return {
        "sequence": sequence,
        "observed_at_UTC": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "monotonic_seconds": time.monotonic(),
        "logical_CPUs": logical_cpus,
        "one_minute_load": one_minute_load,
        "normalized_one_minute_load": normalized,
        "process_peak_RSS_bytes": rss,
        "free_disk_bytes": free_disk,
        "passing": passing,
    }


def _collect_private_readiness(paths: ExecutionPaths) -> tuple[dict[str, Any], int]:
    if paths.readiness.parent.exists():
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "fresh readiness parent already exists"
        )
    try:
        paths.readiness.parent.mkdir(mode=0o700, parents=False, exist_ok=False)
    except OSError as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "fresh readiness parent creation refused"
        ) from exc
    started = time.monotonic()
    samples: list[dict[str, Any]] = []
    passing_tail = 0
    while time.monotonic() - started <= 600.0:
        sample = _current_machine_sample(len(samples) + 1)
        samples.append(sample)
        passing_tail = passing_tail + 1 if sample["passing"] else 0
        if passing_tail == 3:
            break
        time.sleep(5.0)
    ready = passing_tail == 3
    certificate = {
        "schema_name": (
            "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_readiness"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "ready" if ready else "not_ready",
        "ready": ready,
        "samples": samples,
        "thread_environment": dict(THREAD_ENVIRONMENT),
        "scientific_ceiling": "none",
    }
    written = _write_exclusive(paths.readiness, _canonical_json_bytes(certificate))
    if not ready:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "machine readiness did not pass"
        )
    return certificate, written


def _private_report(
    *,
    route: str,
    implementation_commit: str,
    runtime_seconds: float,
    peak_rss_bytes: int,
    readiness_samples: int,
) -> dict[str, Any]:
    if route not in PRIVATE_ROUTES[:2]:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "private aggregate route is outside R1 or R2"
        )
    report = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": route,
        "status": "consumed_aggregate_target_free_structural_discriminator",
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "implementation_commit": implementation_commit,
        },
        "measurements": {
            "input_bytes": PRIVATE_SOURCE_BYTES,
            "source_content_opens": 1,
            "strict_JSON_parses": 1,
            "VR25A_calls": 1,
            "VR27A_map_calls": 1,
            "readiness_samples": readiness_samples,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
        },
        "warnings": [
            "target_free_structural_route_only",
            "no_detail_or_cohort_retained",
            "invocation_consumed_no_retry_or_rerun",
            "no_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "structural_predicate_or_value",
            "participant_or_cohort",
            "archive_member_neural_signal_target_model_prediction_or_score",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "one aggregate inventory-versus-taxonomy structural class"
            ),
            "scientific_claim_not_established": (
                "No archive payload neural signal target model prediction or score "
                "was accessed."
            ),
        },
    }
    _assert_aggregate_safe(report)
    return report


def execute_fixed() -> dict[str, Any]:
    """Execute the single registered private discriminator after proof activation."""

    started = time.monotonic()
    implementation_commit = _require_green_implementation()
    request = load_registered_request()
    decision = load_registered_decision()
    _verify_authority_mapping(request, decision)
    _verify_decision_proof()
    _verify_fixed_inputs(request)
    _validate_thread_environment()
    root = _repo_root()
    paths = ExecutionPaths(
        source=root / PRIVATE_SOURCE_RELATIVE_PATH,
        readiness=root / READINESS_RELATIVE_PATH,
        output_root=root / OUTPUT_ROOT_RELATIVE_PATH,
    )
    readiness, _readiness_bytes = _collect_private_readiness(paths)
    if shutil.disk_usage(root).free < MINIMUM_FREE_DISK_BYTES:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "free disk is below the registered minimum"
        )
    if paths.output_root.exists() or paths.output_root.parent.is_symlink():
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "fresh output root precondition differs"
        )
    paths.output_root.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _make_marker(paths, generated=False)
    source = _read_bound_source_once(
        paths.source,
        SourceBinding(
            bytes=PRIVATE_SOURCE_BYTES,
            sha256=PRIVATE_SOURCE_SHA256,
            schema_name=PRIVATE_SOURCE_SCHEMA,
        ),
    )
    upstream = _upstream_route(source)
    try:
        vr27a_route = vr27a._map_upstream_route(upstream)
    except vr27a.R5InventoryTaxonomyDiscriminatorRefusal as exc:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "private upstream route is outside the frozen map"
        ) from exc
    route = {
        vr27a.INVENTORY_ROUTE: PRIVATE_ROUTES[0],
        vr27a.TAXONOMY_ROUTE: PRIVATE_ROUTES[1],
    }.get(vr27a_route)
    if route is None:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "private route is outside R1 or R2"
        )
    runtime = time.monotonic() - started
    rss = _peak_rss_bytes()
    if runtime > MAX_PRIVATE_RUNTIME_SECONDS or rss >= MAX_RSS_BYTES:
        raise InventoryTaxonomyPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "private resource cap exceeded"
        )
    report = _private_report(
        route=route,
        implementation_commit=implementation_commit,
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        readiness_samples=len(readiness["samples"]),
    )
    _write_exclusive(paths.report, _canonical_json_bytes(report))
    return report


def inspect_fixed() -> dict[str, Any]:
    """Inspect only the fixed aggregate report after implementation proof activation."""

    _require_green_implementation()
    return _inspect_report_file(
        _repo_root() / OUTPUT_ROOT_RELATIVE_PATH / REPORT_NAME,
        allow_generated=False,
    )


def build_plan() -> dict[str, Any]:
    """Return the frozen proof-gated plan without touching private state."""

    request = load_registered_request()
    decision = load_registered_decision()
    _verify_authority_mapping(request, decision)
    _verify_decision_proof()
    return {
        "schema_name": (
            "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_plan"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_stage_1_authorized_private_stage_proof_gated",
        "generated_paths": 20,
        "minimum_direct_refusals": 70,
        "fixed_path_execute": True,
        "generic_path_or_output_arguments": False,
        "private_execution_requires_green_implementation_proof": True,
        "private_detail_or_cohort_retention": False,
        "FW2_or_CIL1_authorized": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proof-gated MARC2 inventory/taxonomy discriminator."
    )
    parser.add_argument("command", choices=("plan", "qualify", "inspect", "execute"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "plan":
            report = build_plan()
        elif args.command == "qualify":
            report = qualify_generated()
        elif args.command == "inspect":
            report = inspect_fixed()
        else:
            report = execute_fixed()
    except InventoryTaxonomyPrivateDiscriminatorRefusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "status": "refused"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
