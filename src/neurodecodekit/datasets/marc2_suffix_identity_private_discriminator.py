"""Proof-gated MARC2-VR15P target-free structural discriminator."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import resource
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_suffix_identity_grammar_decomposition as vr15a


LANE_ID = "MARC2-VR15P"
SCHEMA_VERSION = "0.1.0"
PLAN_SCHEMA_NAME = "neurodecodekit.marc2_suffix_identity_private_discriminator_plan"
QUALIFICATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_suffix_identity_private_discriminator_qualification"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_suffix_identity_private_discriminator_report"
CERTIFICATE_SCHEMA_NAME = (
    "neurodecodekit.marc2_suffix_identity_private_discriminator_readiness"
)
MARKER_SCHEMA_NAME = (
    "neurodecodekit.marc2_suffix_identity_private_discriminator_consumed"
)

DECISION_RELATIVE_PATH = Path(
    "registries/"
    "marc2_suffix_identity_private_discriminator_authorization_decision.v0.json"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/"
    "marc2_suffix_identity_private_discriminator_authorization_request.v0.json"
)
REQUEST_PROOF_RELATIVE_PATH = Path(
    "registries/marc2_suffix_identity_private_discriminator_request_proof.v0.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_suffix_identity_private_discriminator_implementation.v0.json"
)
VR15A_MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_suffix_identity_grammar_decomposition.py"
)
VR15A_IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_suffix_identity_grammar_decomposition_implementation.v0.json"
)
VR15A_RESULT_RELATIVE_PATH = Path(
    "registries/marc2_suffix_identity_grammar_decomposition_result.v0.json"
)

DECISION_SHA256 = "4d87d78f74001eefc0f229551c23d9b631a7ee06e5259b523ed0d3837013fd26"
REQUEST_SHA256 = "675f2ddf62aa89984aa5042b811a482b52dc194ff00f0666b66f05fcb01ccd05"
REQUEST_PROOF_SHA256 = (
    "246b3326193e6fd69aea2d87b3cdbb68fe551009bb0d5af9912e2012fb345fc1"
)
GREEN_DECISION_COMMIT = "fc694a69489913198f0a630bbb0edb04c29310f6"
GREEN_DECISION_CI_RUN_ID = 32_451_448_725
GREEN_DECISION_BASE_JOB_ID = 96_680_587_357
GREEN_DECISION_OPTIONAL_JOB_ID = 96_680_587_199
VR15A_ARTIFACT_SHA256 = {
    VR15A_MODULE_RELATIVE_PATH:
        "d30ae877c67855fd7df58ba54e600361b013e950e6b6bfd36cf966890fc09ee9",
    VR15A_IMPLEMENTATION_RELATIVE_PATH:
        "80ca0dd4ee014856ca3dbdd470d21a91a6effadee15d1a6d82f868e5bde4ea66",
    VR15A_RESULT_RELATIVE_PATH:
        "ecc7bee1c8d1b0263887e0a4cee2db0846fdf0ffbc81fdcdd1abf1208c1e031f",
}

PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
READINESS_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr15p/readiness.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_suffix_identity_private_discriminator/v0"
)
MARKER_RELATIVE_NAME = "consumed.marker.v0.json"
REPORT_RELATIVE_NAME = "report.aggregate.v0.json"
PRIVATE_SOURCE_IDENTITY = {
    "bytes": 418_755,
    "sha256": "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
    "mode": 0o600,
}

THREAD_ENVIRONMENT = dict(vr15a.THREAD_ENVIRONMENT)
GENERATED_SUCCESS_ROUTE = "MARC2VR15P-G1"
PRIVATE_ROUTES = tuple(f"MARC2VR15P-R{index}" for index in range(1, 17))
REFUSAL_ROUTES = tuple(f"MARC2VR15P-F{index:02d}" for index in range(1, 13))
VR15A_TO_PRIVATE_ROUTE = {
    f"MARC2VR15A-R{index}": f"MARC2VR15P-R{index}" for index in range(1, 17)
}

MAX_GENERATED_RUNTIME_SECONDS = 90.0
MAX_PRIVATE_RUNTIME_SECONDS = 650.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 2 * 1024**3
MAX_COMBINED_OUTPUT_BYTES = 1 * 1024**2
MAX_TRACKED_FILE_BYTES = 2 * 1024**2
MAX_CERTIFICATE_BYTES = 64 * 1024
REQUIRED_PASSING_SAMPLES = 3
MINIMUM_SAMPLE_INTERVAL_SECONDS = 5.0
EXECUTION_ARM_ENV = "NEURODECODEKIT_MARC2_VR15P_ARM"
EXECUTION_ARM_VALUE = "MARC2-VR15P:one-target-free-structural-open"

FORBIDDEN_PUBLIC_KEYS = {
    "candidate",
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


class SuffixIdentityPrivateDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR15P refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR15P refusal route")
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
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "canonical JSON refused"
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
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "strict JSON refused"
        ) from exc
    if not isinstance(value, dict):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "top-level JSON object required"
        )
    return value


def _read_tracked(root: Path, relative: Path) -> bytes:
    if relative.is_absolute() or ".." in relative.parts:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked path differs"
        )
    path = root / relative
    try:
        info = path.lstat()
    except OSError as exc:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact type differs"
        )
    if info.st_size <= 0 or info.st_size > MAX_TRACKED_FILE_BYTES:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
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
        != "neurodecodekit.marc2_suffix_identity_private_discriminator_authorization_decision"
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "8873796f772d7c2352d27aa9c0ad2be5278b67fe"
        or not isinstance(proof, dict)
        or proof.get("commit") != "8873796f772d7c2352d27aa9c0ad2be5278b67fe"
        or proof.get("CI_run_id") != 32_450_773_951
        or proof.get("base_python_job_id") != 96_678_759_155
        or proof.get("optional_neuro_job_id") != 96_678_759_451
        or proof.get("both_required_jobs_green") is not True
        or not isinstance(request, dict)
        or request.get("commit") != "08cef4bfacb126770c1a3a4be2fab58d1f7a276f"
        or request.get("CI_run_id") != 32_450_174_692
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
        or authority.get("one_VR15A_classifier_call_after_stage_1_green")
        is not True
        or authority.get("one_nested_VR12A_call_after_stage_1_green") is not True
        or authority.get("private_cohort_manifest_authorized") is not False
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
        or authority.get("release_publication_or_scientific_claim_upgrade_authorized_now")
        is not False
        or not isinstance(caps, dict)
        or caps.get("CPU_threads") != 1
        or caps.get("workers") != 1
        or caps.get("numerical_jobs") != 1
        or caps.get("generated_runtime_seconds") != 90
        or caps.get("private_runtime_seconds") != 650
        or caps.get("minimum_free_disk_bytes") != MINIMUM_FREE_DISK_BYTES
        or caps.get("private_source_read_bytes") != 418_755
        or caps.get("private_source_content_opens") != 1
        or caps.get("VR15A_classifier_calls") != 1
        or caps.get("nested_VR12A_calls") != 1
        or caps.get("combined_incremental_output_bytes") != MAX_COMBINED_OUTPUT_BYTES
        or caps.get("network_bytes") != 0
        or caps.get("signal_bytes") != 0
        or caps.get("target_bytes") != 0
        or caps.get("retry_rerun_resume_count") != 0
        or not isinstance(routes, list)
        or [row.get("route") for row in routes if isinstance(row, dict)]
        != list(PRIVATE_ROUTES)
        or any(
            row.get("private_cohort_manifest_allowed") is not False
            for row in routes
            if isinstance(row, dict)
        )
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "authorization decision differs"
        )


def load_decision(root: Path | None = None) -> dict[str, Any]:
    fixed_root = root or _repo_root()
    payload = _read_tracked(fixed_root, DECISION_RELATIVE_PATH)
    if _sha256_bytes(payload) != DECISION_SHA256:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "authorization decision hash differs"
        )
    decision = _strict_json(payload)
    _validate_decision(decision)
    return decision


def _load_request_and_proof(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    request_payload = _read_tracked(root, REQUEST_RELATIVE_PATH)
    proof_payload = _read_tracked(root, REQUEST_PROOF_RELATIVE_PATH)
    if (
        _sha256_bytes(request_payload) != REQUEST_SHA256
        or _sha256_bytes(proof_payload) != REQUEST_PROOF_SHA256
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "request proof differs"
        )
    request = _strict_json(request_payload)
    proof = _strict_json(proof_payload)
    if (
        request.get("lane_id") != LANE_ID
        or request.get("fixed_input_count") != 17
        or request.get("fixed_input_bytes") != 308_187
        or proof.get("lane_id") != LANE_ID
        or proof.get("request_remote_proof", {}).get("commit")
        != "08cef4bfacb126770c1a3a4be2fab58d1f7a276f"
        or proof.get("request_remote_proof", {}).get("both_required_jobs_green")
        is not True
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "request identity differs"
        )
    return request, proof


def _fixed_payloads(
    request: Mapping[str, Any], root: Path
) -> dict[str, bytes]:
    rows = request.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 17:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "fixed input inventory differs"
        )
    return {
        str(row["path"]): _read_tracked(root, Path(str(row["path"])))
        for row in rows
        if isinstance(row, dict)
    }


def _verify_fixed_payloads(
    request: Mapping[str, Any], payloads: Mapping[str, bytes]
) -> int:
    rows = request.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 17 or len(payloads) != 17:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "fixed input inventory differs"
        )
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[1], "fixed input row differs"
            )
        payload = payloads.get(str(row.get("path")))
        if (
            payload is None
            or len(payload) != row.get("bytes")
            or _sha256_bytes(payload) != row.get("sha256")
        ):
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[1], "fixed input identity differs"
            )
        total += len(payload)
    if total != 308_187:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "fixed input byte total differs"
        )
    return total


def _validate_green_dependencies(root: Path | None = None) -> int:
    fixed_root = root or _repo_root()
    request, _proof = _load_request_and_proof(fixed_root)
    payloads = _fixed_payloads(request, fixed_root)
    total = _verify_fixed_payloads(request, payloads)
    for relative, expected in VR15A_ARTIFACT_SHA256.items():
        if _sha256_bytes(_read_tracked(fixed_root, relative)) != expected:
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[1], "VR15A artifact differs"
            )
    return total


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    current = os.environ if environment is None else environment
    if any(current.get(key) != value for key, value in THREAD_ENVIRONMENT.items()):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "one-thread environment required"
        )


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise SuffixIdentityPrivateDiscriminatorRefusal(
                    REFUSAL_ROUTES[7], "public output key refused"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)
    elif isinstance(value, str):
        lowered = value.casefold()
        if ".codex_work" in lowered or "/users/" in lowered or "safe_reason" in lowered:
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[7], "public output value refused"
            )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    output_bytes: int,
    private: bool,
) -> None:
    runtime_limit = (
        MAX_PRIVATE_RUNTIME_SECONDS if private else MAX_GENERATED_RUNTIME_SECONDS
    )
    values = (runtime_seconds, peak_rss_bytes, output_bytes)
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0
        for value in values
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[8], "resource measurement differs"
        )
    if (
        runtime_seconds > runtime_limit
        or peak_rss_bytes >= MAX_PEAK_RSS_BYTES
        or output_bytes > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[8], "resource cap exceeded"
        )


def _map_vr15a_route(route: str) -> str:
    if route == vr15a.SUCCESS_ROUTE:
        return GENERATED_SUCCESS_ROUTE
    mapped = VR15A_TO_PRIVATE_ROUTE.get(route)
    if mapped is None:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "VR15A route differs"
        )
    return mapped


def _safe_parent_chain(root: Path, relative: Path) -> None:
    if relative.is_absolute() or ".." in relative.parts:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "fixed path differs"
        )
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[5], "fixed parent symlink refused"
            )


def _create_fresh_directory(root: Path, relative: Path) -> Path:
    _safe_parent_chain(root, relative)
    path = root / relative
    if path.exists() or path.is_symlink():
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "fixed output already exists"
        )
    try:
        path.mkdir(parents=True, mode=0o700)
        os.chmod(path, 0o700)
    except OSError as exc:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
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
        raise SuffixIdentityPrivateDiscriminatorRefusal(
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


def _read_generated_once(path: Path, expected_bytes: int) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size != expected_bytes:
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[5], "generated source identity differs"
            )
        chunks: list[bytes] = []
        remaining = expected_bytes
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                raise SuffixIdentityPrivateDiscriminatorRefusal(
                    REFUSAL_ROUTES[5], "generated source ended early"
                )
            chunks.append(chunk)
            remaining -= len(chunk)
    finally:
        os.close(descriptor)
    return b"".join(chunks)


def _generated_path(
    *, root: Path, index: int, source: Mapping[str, Any]
) -> tuple[str, int, int]:
    relative = Path(f"path-{index:03d}")
    path_root = _create_fresh_directory(root, relative)
    source_payload = vr15a.vr12a.vr2._canonical_source_bytes(source)
    source_path = path_root / "source.generated.v0.json"
    _write_exclusive(source_path, source_payload, 0o600)
    parsed = _strict_json(_read_generated_once(source_path, len(source_payload)))
    decision = vr15a.discriminate_generated_source(parsed)
    route = _map_vr15a_route(decision.route)
    marker_payload = _canonical_json_bytes(
        {
            "schema_name": MARKER_SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "generated",
        }
    )
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated",
        "route": route,
        "measurements": {"input_bytes": len(source_payload), "VR15A_calls": 1},
        "claim_boundary": {"scientific_ceiling": "none"},
    }
    _walk_public(report)
    report_payload = _canonical_json_bytes(report)
    _write_exclusive(path_root / MARKER_RELATIVE_NAME, marker_payload, 0o600)
    _write_exclusive(path_root / REPORT_RELATIVE_NAME, report_payload, 0o644)
    peak_bytes = len(source_payload) + len(marker_payload) + len(report_payload)
    shutil.rmtree(path_root)
    return route, len(source_payload), peak_bytes


def _expected_generated_counts() -> dict[str, int]:
    return {route: 4 for route in (GENERATED_SUCCESS_ROUTE, *PRIVATE_ROUTES)}


def _run_generated_matrix() -> dict[str, Any]:
    counts: Counter[str] = Counter()
    replays: list[list[list[str]]] = []
    generated_input_bytes = 0
    temporary_peak_bytes = 0
    calls = 0
    index = 0
    with tempfile.TemporaryDirectory(prefix="marc2-vr15p-generated-") as name:
        root = Path(name)
        for _replay in range(vr15a.REPLAYS):
            current: list[list[str]] = []
            for order in vr15a.ORDERS:
                for case in vr15a.CASES:
                    source = vr15a._build_case(case, order)
                    route, input_bytes, peak_bytes = _generated_path(
                        root=root, index=index, source=source
                    )
                    index += 1
                    calls += 1
                    generated_input_bytes += input_bytes
                    temporary_peak_bytes = max(temporary_peak_bytes, peak_bytes)
                    if route != _map_vr15a_route(vr15a.CASE_ROUTES[case]):
                        raise SuffixIdentityPrivateDiscriminatorRefusal(
                            REFUSAL_ROUTES[10], "generated route differs"
                        )
                    counts[route] += 1
                    current.append([case, order, route])
            replays.append(current)
    digest_rows = [_sha256_bytes(_canonical_json_bytes(rows)) for rows in replays]
    if (
        len(replays) != 2
        or replays[0] != replays[1]
        or digest_rows[0] != digest_rows[1]
        or dict(sorted(counts.items())) != _expected_generated_counts()
        or calls != 68
        or temporary_peak_bytes > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "generated replay differs"
        )
    return {
        "route_counts": dict(sorted(counts.items())),
        "matrix_digest_sha256": digest_rows[0],
        "generated_input_bytes": generated_input_bytes,
        "temporary_peak_bytes": temporary_peak_bytes,
        "path_count": 68,
        "VR15A_calls": calls,
        "nested_VR12A_calls": calls,
        "retained_output_bytes": 0,
    }


def _expect_refusal(
    name: str,
    expected_route: str,
    action: Callable[[], Any],
    refusals: dict[str, str],
) -> None:
    try:
        action()
    except SuffixIdentityPrivateDiscriminatorRefusal as exc:
        if exc.route != expected_route:
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[11], "direct refusal route differs"
            ) from exc
        refusals[name] = exc.route
        return
    raise SuffixIdentityPrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[11], "direct mutation unexpectedly passed"
    )


def _run_direct_refusals(
    *,
    decision: Mapping[str, Any],
    request: Mapping[str, Any],
    payloads: Mapping[str, bytes],
) -> dict[str, str]:
    refusals: dict[str, str] = {}
    decision_mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("lane_id", "MARC2-VR15X"),
        lambda value: value.__setitem__("authorization_parent_commit", "0" * 40),
        lambda value: value["green_proof_closeout"].__setitem__("commit", "0" * 40),
        lambda value: value["green_proof_closeout"].__setitem__("CI_run_id", 0),
        lambda value: value["green_proof_closeout"].__setitem__(
            "base_python_job_id", 0
        ),
        lambda value: value["green_proof_closeout"].__setitem__(
            "optional_neuro_job_id", 0
        ),
        lambda value: value["green_proof_closeout"].__setitem__(
            "both_required_jobs_green", False
        ),
        lambda value: value["green_request"].__setitem__("commit", "0" * 40),
        lambda value: value["green_request"].__setitem__("CI_run_id", 0),
        lambda value: value["green_request"].__setitem__(
            "both_required_jobs_green", False
        ),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_verbatim", "approve"
        ),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_UTF8_bytes", 9
        ),
        lambda value: value["user_authorization"].__setitem__(
            "actual_message_SHA256", "0" * 64
        ),
        lambda value: value["user_authorization"].__setitem__(
            "sole_active_Tier_C_packet", "MARC2-VR14P"
        ),
        lambda value: value["user_authorization"].__setitem__(
            "scope_may_not_expand_by_inference", False
        ),
        lambda value: value["authorization"].__setitem__(
            "generated_wrapper_implementation_after_decision_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "one_private_structural_read_after_stage_1_green", False
        ),
        lambda value: value["authorization"].__setitem__(
            "private_cohort_manifest_authorized", True
        ),
        lambda value: value["authorization"].__setitem__(
            "archive_member_or_payload_access_authorized_now", True
        ),
        lambda value: value["authorization"].__setitem__(
            "FW2_or_CIL1_execution_authorized_now", True
        ),
        lambda value: value["resource_caps"].__setitem__("CPU_threads", 2),
        lambda value: value["resource_caps"].__setitem__(
            "private_source_content_opens", 2
        ),
        lambda value: value["resource_caps"].__setitem__("VR15A_classifier_calls", 2),
        lambda value: value["resource_caps"].__setitem__("network_bytes", 1),
        lambda value: value["private_route_contract"].pop(),
    ]
    for index, mutate in enumerate(decision_mutations, start=1):
        changed = copy.deepcopy(dict(decision))
        mutate(changed)
        _expect_refusal(
            f"decision_{index:03d}",
            REFUSAL_ROUTES[1],
            lambda value=changed: _validate_decision(value),
            refusals,
        )
    for index, name in enumerate(payloads, start=1):
        changed = dict(payloads)
        changed[name] = changed[name] + b"x"
        _expect_refusal(
            f"fixed_input_{index:03d}",
            REFUSAL_ROUTES[1],
            lambda value=changed: _verify_fixed_payloads(request, value),
            refusals,
        )
    for index, payload in enumerate(
        (b"", b"[]", b"{", b'{"x":NaN}', b'{"x":1,"x":2}', b"\xff"),
        start=1,
    ):
        _expect_refusal(
            f"strict_json_{index:03d}",
            REFUSAL_ROUTES[3],
            lambda value=payload: _strict_json(value),
            refusals,
        )
    for index in range(18):
        _expect_refusal(
            f"route_{index:03d}",
            REFUSAL_ROUTES[4],
            lambda value=f"MARC2VR15A-X{index}": _map_vr15a_route(value),
            refusals,
        )
    for index, key in enumerate(sorted(FORBIDDEN_PUBLIC_KEYS), start=1):
        _expect_refusal(
            f"firewall_{index:03d}",
            REFUSAL_ROUTES[7],
            lambda value={key: "redacted"}: _walk_public(value),
            refusals,
        )
    for index, environment in enumerate(
        (
            {},
            {**THREAD_ENVIRONMENT, "OMP_NUM_THREADS": "2"},
            {**THREAD_ENVIRONMENT, "OPENBLAS_NUM_THREADS": "0"},
            {**THREAD_ENVIRONMENT, "MKL_NUM_THREADS": "2"},
            {**THREAD_ENVIRONMENT, "NUMEXPR_NUM_THREADS": "2"},
            {**THREAD_ENVIRONMENT, "VECLIB_MAXIMUM_THREADS": "2"},
        ),
        start=1,
    ):
        _expect_refusal(
            f"thread_{index:03d}",
            REFUSAL_ROUTES[2],
            lambda value=environment: _validate_thread_environment(value),
            refusals,
        )
    base_resources: dict[str, int | float | bool] = {
        "runtime_seconds": 1.0,
        "peak_rss_bytes": 1,
        "output_bytes": 1,
        "private": False,
    }
    resource_mutations = (
        {"runtime_seconds": -1.0},
        {"runtime_seconds": 91.0},
        {"peak_rss_bytes": -1},
        {"peak_rss_bytes": MAX_PEAK_RSS_BYTES},
        {"output_bytes": -1},
        {"output_bytes": MAX_COMBINED_OUTPUT_BYTES + 1},
        {"runtime_seconds": True},
        {"peak_rss_bytes": True},
        {"output_bytes": True},
    )
    for index, mutation in enumerate(resource_mutations, start=1):
        _expect_refusal(
            f"resource_{index:03d}",
            REFUSAL_ROUTES[8],
            lambda values={**base_resources, **mutation}: _assert_resources(**values),
            refusals,
        )
    for index, record in enumerate(
        (
            {},
            {"remote_implementation_proof": None},
            {"remote_implementation_proof": {}},
            {"remote_implementation_proof": {"both_required_jobs_green": False}},
            {"remote_implementation_proof": {"both_required_jobs_green": True}},
            {
                "remote_implementation_proof": {
                    "both_required_jobs_green": True,
                    "commit": "short",
                }
            },
        ),
        start=1,
    ):
        _expect_refusal(
            f"proof_{index:03d}",
            REFUSAL_ROUTES[9],
            lambda value=record: _require_execution_proof(value),
            refusals,
        )
    if len(refusals) < 100:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[11], "direct refusal minimum differs"
        )
    return dict(sorted(refusals.items()))


def _zero_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR13P_or_VR14P_path_or_output_operations": 0,
        "real_structural_source_operations": 0,
        "archive_local_header_or_member_payload_operations": 0,
        "signal_event_channel_geometry_target_or_label_operations": 0,
        "private_cohort_manifest_operations": 0,
        "derivative_cache_feature_split_or_NeuroToken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "FW2_or_CIL1_operations": 0,
        "retry_rerun_resume_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _stabilize_output_size(report: dict[str, Any], key: str) -> int:
    for _ in range(10):
        size = len(_canonical_json_bytes(report))
        if report["resources"][key] == size:
            return size
        report["resources"][key] = size
    raise SuffixIdentityPrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[8], "aggregate output size did not stabilize"
    )


def qualify_generated(
    *,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the bounded 68-path generated-only Stage 1 qualification."""

    started = clock()
    decision = load_decision()
    _validate_thread_environment(environment)
    fixed_input_bytes = _validate_green_dependencies()
    request, _proof = _load_request_and_proof(_repo_root())
    payloads = _fixed_payloads(request, _repo_root())
    matrix = _run_generated_matrix()
    refusals = _run_direct_refusals(
        decision=decision, request=request, payloads=payloads
    )
    runtime = clock() - started
    peak_rss = rss_reader()
    report: dict[str, Any] = {
        "schema_name": QUALIFICATION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "stage_1_generated_qualified_private_stage_closed",
        "route": GENERATED_SUCCESS_ROUTE,
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI": GREEN_DECISION_CI_RUN_ID,
            "decision_base_job": GREEN_DECISION_BASE_JOB_ID,
            "decision_optional_job": GREEN_DECISION_OPTIONAL_JOB_ID,
        },
        "matrix": matrix,
        "direct_refusals": {
            "count": len(refusals),
            "digest_sha256": _sha256_bytes(_canonical_json_bytes(refusals)),
            "minimum_passed": len(refusals) >= 100,
        },
        "resources": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": matrix["generated_input_bytes"],
            "temporary_peak_bytes": matrix["temporary_peak_bytes"],
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
            **_zero_counters(),
            "generated_VR15A_calls": matrix["VR15A_calls"],
            "generated_nested_VR12A_calls": matrix["nested_VR12A_calls"],
            "real_VR15A_calls": 0,
            "real_nested_VR12A_calls": 0,
        },
        "warnings": [
            "generated_fixture_interface_demonstration_only",
            "private_structural_source_not_accessed",
            "neural_payload_not_accessed",
            "no_route_can_freeze_a_cohort",
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
            "private_cause_identified": False,
            "real_cohort_frozen": False,
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "live_decoding": False,
        },
    }
    output_bytes = _stabilize_output_size(report, "aggregate_output_bytes")
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=max(output_bytes, matrix["temporary_peak_bytes"]),
        private=False,
    )
    _walk_public(report)
    return report


def _load_implementation(root: Path) -> dict[str, Any]:
    return _strict_json(_read_tracked(root, IMPLEMENTATION_RELATIVE_PATH))


def _require_execution_proof(
    record: Mapping[str, Any], root: Path | None = None
) -> str:
    fixed_root = root or _repo_root()
    implementation_proof = record.get("remote_implementation_proof")
    closeout_proof = record.get("remote_proof_closeout")
    artifacts = record.get("owned_artifacts")
    if (
        not isinstance(implementation_proof, dict)
        or implementation_proof.get("both_required_jobs_green") is not True
        or not isinstance(closeout_proof, dict)
        or closeout_proof.get("both_required_jobs_green") is not True
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "remote Stage 1 and closeout proofs required"
        )
    commit = closeout_proof.get("commit")
    if not isinstance(commit, str) or len(commit) != 40:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "proof closeout commit differs"
        )
    if not isinstance(artifacts, list) or not artifacts:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "implementation artifacts unavailable"
        )
    for row in artifacts:
        if not isinstance(row, dict):
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[9], "implementation artifact row differs"
            )
        payload = _read_tracked(fixed_root, Path(str(row.get("path", ""))))
        if (
            len(payload) != row.get("bytes")
            or _sha256_bytes(payload) != row.get("sha256")
        ):
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[9], "implementation artifact differs"
            )
    return commit


def _require_tracked_clean(root: Path) -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or result.stdout.strip():
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "tracked repository must be clean"
        )


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
        and not isinstance(sample.get("normalized_one_minute_load"), bool)
        and sample["normalized_one_minute_load"] <= 1.0
        and isinstance(sample.get("free_disk_bytes"), int)
        and sample["free_disk_bytes"] >= MINIMUM_FREE_DISK_BYTES
        and isinstance(sample.get("peak_RSS_bytes"), int)
        and sample["peak_RSS_bytes"] < MAX_PEAK_RSS_BYTES
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
    raise SuffixIdentityPrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[2], "fresh readiness did not pass"
    )


def _preflight_private_source(path: Path) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "registered private source unavailable"
        ) from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != PRIVATE_SOURCE_IDENTITY["mode"]
        or info.st_size != PRIVATE_SOURCE_IDENTITY["bytes"]
    ):
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "registered private source identity differs"
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
            raise SuffixIdentityPrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[6], "private source changed before open"
            )
        chunks: list[bytes] = []
        remaining = PRIVATE_SOURCE_IDENTITY["bytes"]
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                raise SuffixIdentityPrivateDiscriminatorRefusal(
                    REFUSAL_ROUTES[6], "private source ended early"
                )
            chunks.append(chunk)
            remaining -= len(chunk)
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if _sha256_bytes(payload) != PRIVATE_SOURCE_IDENTITY["sha256"]:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "private source hash differs"
        )
    return payload


def _private_report(
    *,
    route: str,
    proof_commit: str,
    runtime_seconds: float,
    peak_rss_bytes: int,
    output_bytes: int,
) -> dict[str, Any]:
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed",
        "route": route,
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI": GREEN_DECISION_CI_RUN_ID,
            "proof_closeout_commit": proof_commit,
        },
        "resources": {
            "input_bytes": PRIVATE_SOURCE_IDENTITY["bytes"],
            "output_bytes": output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "private_content_opens": 1,
            "strict_JSON_parses": 1,
            "VR15A_calls": 1,
            "nested_VR12A_calls": 1,
        },
        "counters": _zero_counters(),
        "warnings": [
            "target_free_structural_result_not_neural_evidence",
            "private_identity_and_failed_value_not_retained",
            "no_route_freezes_a_cohort_or_opens_FW2",
        ],
        "unavailable_fields": [
            "failed_private_value",
            "private_identity",
            "real_cohort",
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


def execute_registered() -> dict[str, Any]:
    """Consume the one fixed private structural invocation after proof green."""

    root = _repo_root()
    started = time.monotonic()
    load_decision(root)
    _validate_green_dependencies(root)
    _validate_thread_environment()
    implementation = _load_implementation(root)
    proof_commit = _require_execution_proof(implementation, root)
    _require_tracked_clean(root)
    if os.environ.get(EXECUTION_ARM_ENV) != EXECUTION_ARM_VALUE:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "explicit one-shot arm required"
        )
    samples = _collect_readiness(root)
    readiness_directory = _create_fresh_directory(root, READINESS_RELATIVE_PATH.parent)
    certificate = {
        "schema_name": CERTIFICATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "proof_closeout_commit": proof_commit,
        "passing_samples": len(samples),
        "created_unix_seconds": time.time(),
    }
    certificate_payload = _canonical_json_bytes(certificate)
    if len(certificate_payload) > MAX_CERTIFICATE_BYTES:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[8], "readiness certificate cap refused"
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
        "proof_closeout_commit": proof_commit,
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
    decision = vr15a.discriminate_generated_source(source)
    route = _map_vr15a_route(decision.route)
    if route == GENERATED_SUCCESS_ROUTE or route not in PRIVATE_ROUTES:
        raise SuffixIdentityPrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private route envelope differs"
        )
    runtime = time.monotonic() - started
    peak_rss = _peak_rss_bytes()
    report = _private_report(
        route=route,
        proof_commit=proof_commit,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=0,
    )
    report_payload = _canonical_json_bytes(report)
    total_output = certificate_size + marker_size + len(report_payload)
    report["resources"]["output_bytes"] = total_output
    report_payload = _canonical_json_bytes(report)
    total_output = certificate_size + marker_size + len(report_payload)
    report["resources"]["output_bytes"] = total_output
    report_payload = _canonical_json_bytes(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=certificate_size + marker_size + len(report_payload),
        private=True,
    )
    _write_exclusive(output_root / REPORT_RELATIVE_NAME, report_payload, 0o644)
    return report


def inspect_proof_state() -> dict[str, Any]:
    root = _repo_root()
    implementation = _load_implementation(root)
    implementation_proof = implementation.get("remote_implementation_proof")
    closeout_proof = implementation.get("remote_proof_closeout")
    return {
        "schema_name": "neurodecodekit.marc2_suffix_identity_private_discriminator_inspection",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "implementation_proof_green": (
            isinstance(implementation_proof, dict)
            and implementation_proof.get("both_required_jobs_green") is True
        ),
        "proof_closeout_green": (
            isinstance(closeout_proof, dict)
            and closeout_proof.get("both_required_jobs_green") is True
        ),
        "private_access_performed": False,
        "scientific_ceiling": "none",
    }


def build_plan() -> dict[str, Any]:
    decision = load_decision()
    fixed_input_bytes = _validate_green_dependencies()
    return {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "decision_green_stage_1_available_private_stage_proof_gated",
        "fixed_interface": decision["future_interface"]["CLI_commands"],
        "fixed_input_bytes": fixed_input_bytes,
        "generated_paths": 68,
        "private_content_open_limit": 1,
        "private_input_bytes": 418_755,
        "CPU_threads": 1,
        "workers": 1,
        "network_bytes": 0,
        "archive_member_bytes": 0,
        "signal_bytes": 0,
        "target_bytes": 0,
        "warnings": [
            "execute_refuses_until_exact_Stage_1_and_closeout_proofs_are_green",
            "no_route_freezes_a_cohort_or_opens_FW2",
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
            result = inspect_proof_state()
        else:
            result = execute_registered()
    except SuffixIdentityPrivateDiscriminatorRefusal as exc:
        print(json.dumps({"status": "refused", "route": exc.route}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
