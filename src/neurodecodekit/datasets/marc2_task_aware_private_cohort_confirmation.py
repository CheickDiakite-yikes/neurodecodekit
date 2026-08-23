"""Proof-gated task-aware MARC2 cohort confirmation."""

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
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_exact_count_readiness as vr33a
from neurodecodekit.datasets import marc2_task_aware_eligibility_repair as vr35a


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR36P"
REQUEST_SCHEMA_NAME = (
    "neurodecodekit.marc2_task_aware_private_cohort_confirmation_authorization_request"
)
DECISION_SCHEMA_NAME = (
    "neurodecodekit.marc2_task_aware_private_cohort_confirmation_authorization_decision"
)
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_task_aware_private_cohort_confirmation_implementation"
)
RESULT_SCHEMA_NAME = (
    "neurodecodekit.marc2_task_aware_private_cohort_confirmation_result"
)
PRIVATE_MANIFEST_SCHEMA_NAME = (
    "neurodecodekit.marc2_task_aware_private_cohort_manifest"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/"
    "marc2_task_aware_private_cohort_confirmation_authorization_request.v0.json"
)
REQUEST_SHA256 = "b226d58b8eb1f707619d251bd633ebf0053f62e23f7adce31dec943067db74ca"
DECISION_RELATIVE_PATH = Path(
    "registries/"
    "marc2_task_aware_private_cohort_confirmation_authorization_decision.v0.json"
)
DECISION_SHA256 = "2837aee3155cfac4558054a6ba90c0cfb128aac18627ce6781a4dab818a76018"
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_task_aware_private_cohort_confirmation_implementation.v0.json"
)
GREEN_DECISION_COMMIT = "fd08dd6ee40b16d3b4f4312601fed3370b7e2ca5"
GREEN_DECISION_CI_RUN_ID = 32_648_347_577
GREEN_DECISION_BASE_JOB_ID = 97_215_989_173
GREEN_DECISION_OPTIONAL_JOB_ID = 97_215_989_332
QUALIFICATION_ROUTE = "MARC2VR36P-G1"
PRIVATE_ROUTES = tuple(f"MARC2VR36P-R{index}" for index in range(1, 7))
REFUSAL_ROUTES = tuple(f"MARC2VR36P-F{index:02d}" for index in range(1, 11))
CASES = vr35a.CASES
ORDERS = vr35a.ORDERS
READINESS_PATTERNS = ("PPP", "FFF")
REPLAYS = 2
THREAD_ENVIRONMENT = dict(vr33a.THREAD_ENVIRONMENT)
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
READINESS_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr36p/readiness.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_task_aware_private_cohort_confirmation/v0"
)
MARKER_NAME = "consumed.marker.v0.json"
PRIVATE_MANIFEST_NAME = "cohort.private.v0.json"
REPORT_NAME = "report.aggregate.v0.json"
PRIVATE_SOURCE_BYTES = 418_755
PRIVATE_SOURCE_SHA256 = "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
PRIVATE_SOURCE_SCHEMA = "neurodecodekit.marc1_central_directory_private_manifest"
MAX_OUTPUT_BYTES = 2_097_152
MAX_RSS_BYTES = 268_435_456
MINIMUM_FREE_DISK_BYTES = 16_106_127_360
MAX_PRIVATE_RUNTIME_SECONDS = 120.0
MAX_GENERATED_RUNTIME_SECONDS = 90.0
FORBIDDEN_PUBLIC_KEYS = {
    "actual_count",
    "cohort",
    "difference",
    "eligible_count",
    "eligible_total",
    "exception",
    "label",
    "member_name",
    "observed_count",
    "participant",
    "participant_id",
    "path",
    "predicate",
    "private_hash",
    "private_manifest",
    "private_value",
    "probability",
    "reservation",
    "row",
    "selected_rows",
    "selection_identity",
    "session",
    "source_exact_name",
    "source_path",
    "subject",
    "subject_id",
    "target",
    "target_text",
    "target_value",
    "task_distribution",
    "value",
}


class TaskAwarePrivateCohortConfirmationRefusal(RuntimeError):
    """Fail closed with an aggregate-safe VR36P refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR36P refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class SourceBinding:
    bytes: int
    sha256: str
    schema_name: str
    rows: int
    mode: int


@dataclass(frozen=True, slots=True)
class ExecutionPaths:
    source: Path
    readiness: Path
    output_root: Path

    @property
    def marker(self) -> Path:
        return self.output_root / MARKER_NAME

    @property
    def private_manifest(self) -> Path:
        return self.output_root / PRIVATE_MANIFEST_NAME

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
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[3], "JSON value is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[3], "duplicate JSON key"
            )
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise TaskAwarePrivateCohortConfirmationRefusal(
        REFUSAL_ROUTES[3], "non-finite JSON value"
    )


def _strict_json(payload: bytes, *, canonical: bool = False) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[3], "UTF-8 BOM is forbidden"
        )
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[3], "invalid UTF-8"
        ) from exc
    if "\x00" in text or any(
        ord(char) < 32 and char not in "\t\n\r" for char in text
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[3], "disallowed control character"
        )
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except TaskAwarePrivateCohortConfirmationRefusal:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[3], "invalid JSON"
        ) from exc
    if not isinstance(value, dict):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[3], "JSON root is not an object"
        )
    if canonical and _canonical_json_bytes(value) != payload:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[3], "JSON bytes are not canonical"
        )
    return value


def _read_registered_json(
    relative_path: Path, expected_sha256: str, *, root: Path | None = None
) -> dict[str, Any]:
    base = root or _repo_root()
    try:
        payload = (base / relative_path).read_bytes()
    except OSError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[0], "registered authority is unavailable"
        ) from exc
    if _sha256_bytes(payload) != expected_sha256:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[0], "registered authority hash differs"
        )
    return _strict_json(payload)


def load_registered_request(root: Path | None = None) -> dict[str, Any]:
    return _read_registered_json(REQUEST_RELATIVE_PATH, REQUEST_SHA256, root=root)


def load_registered_decision(root: Path | None = None) -> dict[str, Any]:
    return _read_registered_json(DECISION_RELATIVE_PATH, DECISION_SHA256, root=root)


def _verify_authority_mapping(
    request: Mapping[str, Any], decision: Mapping[str, Any]
) -> None:
    registered_request = load_registered_request()
    registered_decision = load_registered_decision()
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
        or decision.get("user_authorization", {}).get("actual_message_verbatim")
        != "coninue"
        or authorization.get("generated_wrapper_implementation_after_decision_green")
        is not True
        or authorization.get("generated_wrapper_qualification_after_decision_green")
        is not True
        or requirements.get("required_paths") != 40
        or requirements.get("VR33A_calls") != 40
        or requirements.get("readiness_provider_calls") != 120
        or requirements.get("readiness_sleeper_calls") != 80
        or requirements.get("VR35A_calls") != 20
        or requirements.get("direct_refusal_minimum") != 100
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[0], "registered authority mapping differs"
        )


def _verify_decision_proof() -> None:
    if (
        GREEN_DECISION_COMMIT
        != "fd08dd6ee40b16d3b4f4312601fed3370b7e2ca5"
        or GREEN_DECISION_CI_RUN_ID != 32_648_347_577
        or GREEN_DECISION_BASE_JOB_ID != 97_215_989_173
        or GREEN_DECISION_OPTIONAL_JOB_ID != 97_215_989_332
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[0], "decision proof differs"
        )


def _verify_fixed_inputs(
    request: Mapping[str, Any], decision: Mapping[str, Any], root: Path | None = None
) -> int:
    base = root or _repo_root()
    rows: list[Mapping[str, Any]] = []
    for group in (
        request.get("fixed_committed_artifacts"),
        decision.get("bound_packet_artifacts"),
        decision.get("decision_artifacts"),
    ):
        if not isinstance(group, list):
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[0], "fixed input registry differs"
            )
        rows.extend(group)
    seen: set[str] = set()
    total = 0
    for row in rows:
        if not isinstance(row, Mapping) or not {
            "path",
            "bytes",
            "sha256",
        }.issubset(row):
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        relative = str(row["path"])
        if relative in seen:
            continue
        seen.add(relative)
        try:
            payload = (base / relative).read_bytes()
        except OSError as exc:
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row["bytes"] or _sha256_bytes(payload) != row["sha256"]:
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if len(seen) != 23 or total != 211_512:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[9], "thread environment differs"
        )


def _require_green_implementation(root: Path | None = None) -> str:
    base = root or _repo_root()
    try:
        record = json.loads(
            (base / IMPLEMENTATION_RELATIVE_PATH).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
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
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[1], "implementation proof is not remotely green"
        )
    return proof["commit"]


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise TaskAwarePrivateCohortConfirmationRefusal(
                    REFUSAL_ROUTES[7], "aggregate report contains forbidden field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_aggregate_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    payload = _canonical_json_bytes(report)
    if len(payload) > MAX_OUTPUT_BYTES:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[7], "aggregate report exceeds output cap"
        )


def _write_exclusive(path: Path, payload: bytes, *, mode: int = 0o600) -> int:
    if path.is_symlink() or path.parent.is_symlink():
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[4], "output path is a symlink"
        )
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
    except OSError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[4], "exclusive output creation refused"
        ) from exc
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short output write")
            view = view[written:]
        os.fsync(descriptor)
    except OSError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[4], "output write refused"
        ) from exc
    finally:
        os.close(descriptor)
    if stat.S_IMODE(path.stat().st_mode) != mode or path.stat().st_size != len(payload):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[4], "output identity differs"
        )
    return len(payload)


def _preflight_bound_source(path: Path, binding: SourceBinding) -> os.stat_result:
    try:
        facts = os.lstat(path)
    except OSError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[5], "source preflight refused"
        ) from exc
    if (
        not stat.S_ISREG(facts.st_mode)
        or stat.S_ISLNK(facts.st_mode)
        or facts.st_size != binding.bytes
        or stat.S_IMODE(facts.st_mode) != binding.mode
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[5], "source facts differ"
        )
    return facts


def _read_bound_source_once(
    path: Path, binding: SourceBinding, *, preflight: os.stat_result | None = None
) -> dict[str, Any]:
    facts = preflight or _preflight_bound_source(path, binding)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[5], "source open refused"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_dev != facts.st_dev
            or opened.st_ino != facts.st_ino
            or opened.st_size != binding.bytes
            or stat.S_IMODE(opened.st_mode) != binding.mode
        ):
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[5], "opened source identity differs"
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65_536, binding.bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > binding.bytes:
                raise TaskAwarePrivateCohortConfirmationRefusal(
                    REFUSAL_ROUTES[5], "source exceeds byte binding"
                )
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if len(payload) != binding.bytes or _sha256_bytes(payload) != binding.sha256:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[5], "source content binding differs"
        )
    source = _strict_json(payload)
    entries = source.get("entries")
    if (
        source.get("schema_name") != binding.schema_name
        or not isinstance(entries, list)
        or len(entries) != binding.rows
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[5], "source structural envelope differs"
        )
    return source


def _sample_payload(sequence: int, passing: bool) -> dict[str, Any]:
    return {
        "sequence": sequence,
        "passing": passing,
        "observed_at_seconds": float(sequence * 5),
        "available_bytes": MINIMUM_FREE_DISK_BYTES + sequence,
    }


def _collect_generated_readiness(
    pattern: str,
) -> tuple[vr33a.ReadinessResult, int, int, int]:
    if pattern not in READINESS_PATTERNS:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[2], "generated readiness pattern differs"
        )
    samples = [
        _sample_payload(sequence, marker == "P")
        for sequence, marker in enumerate(pattern, start=1)
    ]
    provider_calls = 0
    sleeper_calls = 0
    input_bytes = 0

    def provider(sequence: int) -> Mapping[str, Any]:
        nonlocal provider_calls, input_bytes
        provider_calls += 1
        sample = samples[sequence - 1]
        input_bytes += len(_canonical_json_bytes(sample))
        return sample

    def sleeper(interval: float) -> None:
        nonlocal sleeper_calls
        if interval != vr33a.INTERVAL_SECONDS:
            raise ValueError("generated sleeper interval differs")
        sleeper_calls += 1

    result = vr33a.collect_exact_readiness(provider, sleeper)
    return result, provider_calls, sleeper_calls, input_bytes


def _write_readiness_certificate(
    paths: ExecutionPaths,
    readiness: vr33a.ReadinessResult,
    *,
    generated: bool,
) -> int:
    payload = {
        "schema_name": "neurodecodekit.marc2_task_aware_readiness_certificate",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "generated": generated,
        "ready": readiness.ready,
        "sample_count": len(readiness.samples),
        "samples": [
            {
                "sequence": sample.sequence,
                "passing": sample.passing,
                "observed_at_seconds": sample.observed_at_seconds,
                "available_bytes": sample.available_bytes,
            }
            for sample in readiness.samples
        ],
    }
    return _write_exclusive(paths.readiness, _canonical_json_bytes(payload))


def _make_marker(paths: ExecutionPaths, *, generated: bool) -> int:
    if paths.output_root.exists() or paths.output_root.is_symlink():
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[4], "fresh output root precondition differs"
        )
    paths.output_root.mkdir(mode=0o700, parents=True)
    marker = {
        "schema_name": "neurodecodekit.marc2_task_aware_consumed_marker",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "generated": generated,
        "state": "consumed_no_retry_or_rerun",
    }
    return _write_exclusive(paths.marker, _canonical_json_bytes(marker))


def _map_vr35a_route(route: str) -> str:
    mapping = {
        "MARC2VR35A-G1": PRIVATE_ROUTES[0],
        "MARC2VR35A-G2": PRIVATE_ROUTES[1],
        "MARC2VR35A-R1": PRIVATE_ROUTES[2],
        "MARC2VR35A-R2": PRIVATE_ROUTES[3],
        "MARC2VR35A-R3": PRIVATE_ROUTES[4],
    }
    try:
        return mapping[route]
    except KeyError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[6], "VR35A route is not allowlisted"
        ) from exc


def _apply_vr35a(
    source: Mapping[str, Any],
) -> tuple[str, vr35a.TaskAwareSelection | None]:
    before = vr35a._source_bytes(source)
    outcome: vr35a.TaskAwareSelection | None = None
    try:
        outcome = vr35a.adapt_task_aware_source(source)
        upstream = outcome.route
    except vr35a.TaskAwareEligibilityRepairRefusal as exc:
        if exc.route not in vr35a.DIAGNOSTIC_ROUTES:
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[6], "VR35A refused outside the diagnostic map"
            ) from exc
        upstream = exc.route
    if vr35a._source_bytes(source) != before:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[6], "source changed during VR35A call"
        )
    return _map_vr35a_route(upstream), outcome


def _build_private_manifest(
    outcome: vr35a.TaskAwareSelection,
) -> dict[str, Any]:
    selection = outcome.selection
    rows = selection.private_manifest.get("rows")
    cohort = selection.cohort_summary
    split = selection.split_summary
    if (
        outcome.route not in vr35a.SUCCESS_ROUTES
        or not isinstance(rows, list)
        or len(rows) != 384
        or cohort.get("selected_subjects") != 16
        or split.get("selected_run_bundles") != 96
        or split.get("fit_run_bundles") != 48
        or split.get("heldout_run_bundles") != 48
        or split.get("selected_core_members") != 384
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[6], "cohort cardinality differs"
        )
    return {
        "schema_name": PRIVATE_MANIFEST_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "proof_posture": "target_free_structural_selection_no_neural_payload",
        "task": vr35a.PUBLISHED_TASK,
        "source_binding": {
            "source_sha256": outcome.source_sha256,
            "source_semantic_sha256": outcome.semantic_sha256,
            "source_exact_selected_names_sha256": (
                outcome.source_exact_selected_names_sha256
            ),
        },
        "selection_hashes": dict(selection.selection_hashes),
        "cohort_summary": dict(cohort),
        "split_summary": dict(split),
        "byte_summary": dict(selection.byte_summary),
        "rows": rows,
    }


def _case_report(
    *, route: str, pattern: str, case: str, order: str, cohort_written: bool
) -> dict[str, Any]:
    report = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": route,
        "status": "generated_fixed_path_case",
        "generated_condition": {
            "readiness_pattern": pattern,
            "fixture_case": case,
            "fixture_order": order,
        },
        "cohort_file_written": cohort_written,
        "warnings": ["generated_only", "no_repository_private_path_touched"],
    }
    _assert_aggregate_safe(report)
    return report


def _inspect_report_file(path: Path, *, allow_generated: bool) -> dict[str, Any]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[8], "aggregate report is unavailable"
        ) from exc
    report = _strict_json(payload, canonical=True)
    _assert_aggregate_safe(report)
    if report.get("schema_name") != RESULT_SCHEMA_NAME or report.get("lane_id") != LANE_ID:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[8], "aggregate report identity differs"
        )
    if allow_generated:
        if report.get("status") != "generated_fixed_path_case":
            raise TaskAwarePrivateCohortConfirmationRefusal(
                REFUSAL_ROUTES[8], "generated report status differs"
            )
    elif report.get("status") != "consumed_target_free_structural_confirmation":
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[8], "private aggregate report status differs"
        )
    return report


def _run_generated_case(
    *, pattern: str, case: str, order: str, root: Path
) -> dict[str, Any]:
    if pattern not in READINESS_PATTERNS or case not in CASES or order not in ORDERS:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[2], "generated condition differs"
        )
    paths = ExecutionPaths(
        source=root / "source.json",
        readiness=root / "readiness" / "readiness.json",
        output_root=root / "output",
    )
    readiness, provider_calls, sleeper_calls, readiness_input_bytes = (
        _collect_generated_readiness(pattern)
    )
    readiness_bytes = _write_readiness_certificate(
        paths, readiness, generated=True
    )
    marker_bytes = _make_marker(paths, generated=True)
    source_constructions = 0
    source_opens = 0
    vr35a_calls = 0
    source_bytes = 0
    cohort_bytes = 0
    cohort_written = False
    source_unchanged = True
    upstream_route: str | None = None
    if readiness.ready:
        source = vr35a.build_generated_case(case, order)
        source_constructions = 1
        payload = vr35a._source_bytes(source)
        source_before = payload
        source_bytes = len(payload)
        _write_exclusive(paths.source, payload)
        loaded = _read_bound_source_once(
            paths.source,
            SourceBinding(
                bytes=len(payload),
                sha256=_sha256_bytes(payload),
                schema_name=str(source["schema_name"]),
                rows=len(source["entries"]),
                mode=0o600,
            ),
        )
        source_opens = 1
        route, outcome = _apply_vr35a(loaded)
        vr35a_calls = 1
        if outcome is not None:
            upstream_route = outcome.route
            private_manifest = _build_private_manifest(outcome)
            cohort_bytes = _write_exclusive(
                paths.private_manifest,
                _canonical_json_bytes(private_manifest),
            )
            cohort_written = True
        else:
            upstream_route = {
                PRIVATE_ROUTES[2]: "MARC2VR35A-R1",
                PRIVATE_ROUTES[3]: "MARC2VR35A-R2",
                PRIVATE_ROUTES[4]: "MARC2VR35A-R3",
            }[route]
        source_unchanged = vr35a._source_bytes(loaded) == source_before
    else:
        route = PRIVATE_ROUTES[5]
    report = _case_report(
        route=route,
        pattern=pattern,
        case=case,
        order=order,
        cohort_written=cohort_written,
    )
    report_payload = _canonical_json_bytes(report)
    report_bytes = _write_exclusive(paths.report, report_payload, mode=0o644)
    if _inspect_report_file(paths.report, allow_generated=True) != report:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[8], "generated report replay differs"
        )
    output_candidates = [paths.readiness, paths.marker, paths.report]
    if cohort_written:
        output_candidates.append(paths.private_manifest)
    return {
        "route": route,
        "VR35A_route": upstream_route,
        "readiness_ready": readiness.ready,
        "readiness_provider_calls": provider_calls,
        "readiness_sleeper_calls": sleeper_calls,
        "source_constructions": source_constructions,
        "source_content_opens": source_opens,
        "VR35A_calls": vr35a_calls,
        "cohort_file_writes": int(cohort_written),
        "source_unchanged": source_unchanged,
        "input_bytes": readiness_input_bytes + source_bytes,
        "output_bytes": readiness_bytes + marker_bytes + cohort_bytes + report_bytes,
        "peak_incremental_output_bytes": sum(
            candidate.stat().st_size for candidate in output_candidates
        ),
        "report_sha256": _sha256_bytes(report_payload),
    }


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except TaskAwarePrivateCohortConfirmationRefusal as exc:
        return exc.route
    raise TaskAwarePrivateCohortConfirmationRefusal(
        REFUSAL_ROUTES[8], "direct refusal unexpectedly passed"
    )


def _run_direct_refusals(
    request: Mapping[str, Any], decision: Mapping[str, Any]
) -> Counter[str]:
    routes: list[str] = []
    request_mutations = [
        ("schema_name", "wrong"),
        ("lane_id", "wrong"),
        ("status", "wrong"),
    ]
    for key, value in request_mutations:
        mutated = copy.deepcopy(request)
        mutated[key] = value
        routes.append(_expect_refusal(lambda m=mutated: _verify_authority_mapping(m, decision)))
    decision_mutations = [
        ("schema_name", "wrong"),
        ("lane_id", "wrong"),
        ("status", "wrong"),
    ]
    for key, value in decision_mutations:
        mutated = copy.deepcopy(decision)
        mutated[key] = value
        routes.append(_expect_refusal(lambda m=mutated: _verify_authority_mapping(request, m)))
    for key in THREAD_ENVIRONMENT:
        missing = dict(THREAD_ENVIRONMENT)
        del missing[key]
        routes.append(_expect_refusal(lambda m=missing: _validate_thread_environment(m)))
        wrong = dict(THREAD_ENVIRONMENT)
        wrong[key] = "2"
        routes.append(_expect_refusal(lambda m=wrong: _validate_thread_environment(m)))
    for index in range(25):
        routes.append(
            _expect_refusal(
                lambda i=index: _strict_json(
                    f'{{"duplicate":{i},"duplicate":{i + 1}}}\n'.encode("ascii")
                )
            )
        )
    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        routes.append(_expect_refusal(lambda k=key: _assert_aggregate_safe({k: "x"})))
    for index in range(12):
        routes.append(
            _expect_refusal(
                lambda i=index: _run_generated_case(
                    pattern="PPP",
                    case=f"unknown-{i}",
                    order="canonical",
                    root=Path("unused"),
                )
            )
        )
    for index in range(12):
        routes.append(
            _expect_refusal(
                lambda i=index: _run_generated_case(
                    pattern="PPP",
                    case=CASES[0],
                    order=f"unknown-{i}",
                    root=Path("unused"),
                )
            )
        )
    for index in range(12):
        routes.append(
            _expect_refusal(
                lambda i=index: _run_generated_case(
                    pattern=f"X{i}",
                    case=CASES[0],
                    order="canonical",
                    root=Path("unused"),
                )
            )
        )
    for route in ("unknown", "MARC2VR35A-F01", "MARC2VR35A-R9"):
        routes.append(_expect_refusal(lambda r=route: _map_vr35a_route(r)))
    counts = Counter(routes)
    if len(routes) < 100 or any(route not in REFUSAL_ROUTES for route in routes):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[8], "direct refusal coverage differs"
        )
    return counts


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _zero_counters() -> dict[str, int]:
    return {
        "repository_dot_codex_work_operations": 0,
        "private_structural_source_stats_resolves_hashes_opens_reads_or_parses": 0,
        "consumed_private_lane_path_or_output_operations": 0,
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


def _assert_generated_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    peak_incremental_output_bytes: int,
) -> None:
    if (
        runtime_seconds < 0
        or runtime_seconds > MAX_GENERATED_RUNTIME_SECONDS
        or peak_rss_bytes < 0
        or peak_rss_bytes >= MAX_RSS_BYTES
        or peak_incremental_output_bytes > MAX_OUTPUT_BYTES
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[9], "generated resource cap exceeded"
        )


def qualify_generated(
    *,
    request: Mapping[str, Any] | None = None,
    decision: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the sole registered 40-path generated qualification."""

    started = clock()
    registered_request = dict(request or load_registered_request())
    registered_decision = dict(decision or load_registered_decision())
    _verify_authority_mapping(registered_request, registered_decision)
    _verify_decision_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered_request, registered_decision)
    _validate_thread_environment(environment)
    refusal_counts = _run_direct_refusals(registered_request, registered_decision)
    route_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    replay_signatures: list[list[tuple[Any, ...]]] = []
    provider_calls = 0
    sleeper_calls = 0
    source_constructions = 0
    source_opens = 0
    vr35a_calls = 0
    cohort_writes = 0
    source_mutations = 0
    generated_input_bytes = 0
    generated_output_bytes = 0
    peak_incremental_output_bytes = 0
    with tempfile.TemporaryDirectory(prefix="marc2-vr36p-generated-") as temp:
        temp_root = Path(temp)
        for replay in range(REPLAYS):
            signature: list[tuple[Any, ...]] = []
            for order in ORDERS:
                for case in CASES:
                    for pattern in READINESS_PATTERNS:
                        case_root = temp_root / f"r{replay}-{order}-{case}-{pattern}"
                        case_root.mkdir(mode=0o700)
                        result = _run_generated_case(
                            pattern=pattern,
                            case=case,
                            order=order,
                            root=case_root,
                        )
                        route_counts[result["route"]] += 1
                        if result["VR35A_route"] is not None:
                            upstream_counts[result["VR35A_route"]] += 1
                        provider_calls += result["readiness_provider_calls"]
                        sleeper_calls += result["readiness_sleeper_calls"]
                        source_constructions += result["source_constructions"]
                        source_opens += result["source_content_opens"]
                        vr35a_calls += result["VR35A_calls"]
                        cohort_writes += result["cohort_file_writes"]
                        source_mutations += int(not result["source_unchanged"])
                        generated_input_bytes += result["input_bytes"]
                        generated_output_bytes += result["output_bytes"]
                        peak_incremental_output_bytes = max(
                            peak_incremental_output_bytes,
                            result["peak_incremental_output_bytes"],
                        )
                        signature.append(
                            (
                                order,
                                case,
                                pattern,
                                result["route"],
                                result["VR35A_route"],
                                result["cohort_file_writes"],
                                result["report_sha256"],
                            )
                        )
            replay_signatures.append(signature)
    expected_routes = Counter(
        {
            PRIVATE_ROUTES[0]: 4,
            PRIVATE_ROUTES[1]: 4,
            PRIVATE_ROUTES[2]: 4,
            PRIVATE_ROUTES[3]: 4,
            PRIVATE_ROUTES[4]: 4,
            PRIVATE_ROUTES[5]: 20,
        }
    )
    expected_upstream = Counter(
        {
            "MARC2VR35A-G1": 4,
            "MARC2VR35A-G2": 4,
            "MARC2VR35A-R1": 4,
            "MARC2VR35A-R2": 4,
            "MARC2VR35A-R3": 4,
        }
    )
    if (
        provider_calls != 120
        or sleeper_calls != 80
        or source_constructions != 20
        or source_opens != 20
        or vr35a_calls != 20
        or cohort_writes != 8
        or source_mutations != 0
        or route_counts != expected_routes
        or upstream_counts != expected_upstream
        or replay_signatures[0] != replay_signatures[1]
    ):
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[8], "generated replay or call distribution differs"
        )
    runtime = clock() - started
    rss = peak_rss()
    _assert_generated_resources(runtime, rss, peak_incremental_output_bytes)
    report: dict[str, Any] = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": QUALIFICATION_ROUTE,
        "status": "generated_task_aware_fixed_path_wrapper_qualified",
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "decision_base_job_id": GREEN_DECISION_BASE_JOB_ID,
            "decision_optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "request_sha256": REQUEST_SHA256,
            "decision_sha256": DECISION_SHA256,
        },
        "matrix": {
            "fixture_cases": list(CASES),
            "readiness_patterns": list(READINESS_PATTERNS),
            "orders": list(ORDERS),
            "replays": REPLAYS,
            "paths": 40,
            "VR33A_calls": 40,
            "readiness_provider_calls": provider_calls,
            "readiness_sleeper_calls": sleeper_calls,
            "source_constructions": source_constructions,
            "source_content_opens": source_opens,
            "VR35A_calls": vr35a_calls,
            "cohort_file_writes": cohort_writes,
            "VR36P_route_counts": dict(sorted(route_counts.items())),
            "VR35A_route_counts": dict(sorted(upstream_counts.items())),
            "nonpassing_readiness_source_constructions": 0,
            "nonpassing_readiness_VR35A_calls": 0,
            "exact_replays_match": True,
            "source_mutations_after_call": source_mutations,
            "fixed_path_state_machine_qualified": True,
            "marker_preceded_every_source_construction_and_open": True,
            "direct_refusals_passed": sum(refusal_counts.values()),
            "direct_refusal_route_counts": dict(sorted(refusal_counts.items())),
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
            "real_task_aware_route_or_cohort",
            "private_count_difference_task_distribution_identity_or_row",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "generated exact-readiness and task-aware fixed-path cohort-freeze "
                "state machine"
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
        "passing": passing,
        "observed_at_seconds": time.monotonic(),
        "available_bytes": free_disk,
    }


def _private_report(
    *,
    route: str,
    implementation_commit: str,
    runtime_seconds: float,
    peak_rss_bytes: int,
    source_content_opens: int,
    vr35a_calls: int,
    cohort_written: bool,
    input_bytes: int,
) -> dict[str, Any]:
    if route not in PRIVATE_ROUTES:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[6], "private aggregate route differs"
        )
    report = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": route,
        "status": "consumed_target_free_structural_confirmation",
        "proof": {
            "decision_commit": GREEN_DECISION_COMMIT,
            "implementation_commit": implementation_commit,
        },
        "measurements": {
            "input_bytes": input_bytes,
            "source_content_opens": source_content_opens,
            "strict_JSON_parses": source_content_opens,
            "VR33A_calls": 1,
            "readiness_samples": 3,
            "readiness_sleeps": 2,
            "VR35A_calls": vr35a_calls,
            "cohort_file_written": cohort_written,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "archive_member_bytes": 0,
            "signal_bytes": 0,
            "target_bytes": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "warnings": [
            "target_free_structural_route_only",
            "invocation_consumed_no_retry_or_rerun",
            "no_private_count_distribution_identity_or_row_in_public_output",
            "no_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "private_count_difference_task_distribution_identity_or_row",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "one exact-readiness-gated target-free task-aware structural "
                "confirmation with conditional source-bound cohort freeze"
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
    """Execute the one fixed private confirmation after proof activation."""

    started = time.monotonic()
    implementation_commit = _require_green_implementation()
    request = load_registered_request()
    decision = load_registered_decision()
    _verify_authority_mapping(request, decision)
    _verify_decision_proof()
    _verify_fixed_inputs(request, decision)
    _validate_thread_environment()
    root = _repo_root()
    paths = ExecutionPaths(
        source=root / PRIVATE_SOURCE_RELATIVE_PATH,
        readiness=root / READINESS_RELATIVE_PATH,
        output_root=root / OUTPUT_ROOT_RELATIVE_PATH,
    )
    if paths.readiness.parent.exists() or paths.readiness.parent.is_symlink():
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[4], "fresh readiness path precondition differs"
        )
    if paths.output_root.exists() or paths.output_root.is_symlink():
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[4], "fresh output root precondition differs"
        )
    readiness = vr33a.collect_exact_readiness(_current_machine_sample, time.sleep)
    readiness_bytes = _write_readiness_certificate(paths, readiness, generated=False)
    route = PRIVATE_ROUTES[5]
    source_opens = 0
    vr35a_calls = 0
    cohort_written = False
    cohort_bytes = 0
    input_bytes = 0
    preflight: os.stat_result | None = None
    if readiness.ready:
        try:
            preflight = _preflight_bound_source(
                paths.source,
                SourceBinding(
                    bytes=PRIVATE_SOURCE_BYTES,
                    sha256=PRIVATE_SOURCE_SHA256,
                    schema_name=PRIVATE_SOURCE_SCHEMA,
                    rows=1227,
                    mode=0o600,
                ),
            )
        except TaskAwarePrivateCohortConfirmationRefusal:
            route = PRIVATE_ROUTES[4]
    marker_bytes = _make_marker(paths, generated=False)
    if readiness.ready and preflight is not None:
        try:
            source = _read_bound_source_once(
                paths.source,
                SourceBinding(
                    bytes=PRIVATE_SOURCE_BYTES,
                    sha256=PRIVATE_SOURCE_SHA256,
                    schema_name=PRIVATE_SOURCE_SCHEMA,
                    rows=1227,
                    mode=0o600,
                ),
                preflight=preflight,
            )
            source_opens = 1
            input_bytes = PRIVATE_SOURCE_BYTES
            route, outcome = _apply_vr35a(source)
            vr35a_calls = 1
            if outcome is not None:
                manifest = _build_private_manifest(outcome)
                cohort_bytes = _write_exclusive(
                    paths.private_manifest,
                    _canonical_json_bytes(manifest),
                )
                cohort_written = True
        except TaskAwarePrivateCohortConfirmationRefusal:
            route = PRIVATE_ROUTES[4]
        except vr35a.TaskAwareEligibilityRepairRefusal:
            route = PRIVATE_ROUTES[4]
    runtime = time.monotonic() - started
    rss = _peak_rss_bytes()
    if runtime > MAX_PRIVATE_RUNTIME_SECONDS or rss >= MAX_RSS_BYTES:
        route = PRIVATE_ROUTES[5]
    report = _private_report(
        route=route,
        implementation_commit=implementation_commit,
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        source_content_opens=source_opens,
        vr35a_calls=vr35a_calls,
        cohort_written=cohort_written,
        input_bytes=input_bytes,
    )
    report_payload = _canonical_json_bytes(report)
    report_bytes = _write_exclusive(paths.report, report_payload, mode=0o644)
    if readiness_bytes + marker_bytes + cohort_bytes + report_bytes > MAX_OUTPUT_BYTES:
        raise TaskAwarePrivateCohortConfirmationRefusal(
            REFUSAL_ROUTES[9], "combined output cap exceeded"
        )
    return report


def inspect_fixed() -> dict[str, Any]:
    """Inspect only the fixed aggregate report after proof activation."""

    _require_green_implementation()
    return _inspect_report_file(
        _repo_root() / OUTPUT_ROOT_RELATIVE_PATH / REPORT_NAME,
        allow_generated=False,
    )


def build_plan() -> dict[str, Any]:
    request = load_registered_request()
    decision = load_registered_decision()
    _verify_authority_mapping(request, decision)
    _verify_decision_proof()
    return {
        "schema_name": "neurodecodekit.marc2_task_aware_private_cohort_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "decision_green_generated_stage_open_private_stage_proof_gated",
        "generated_paths": 40,
        "VR33A_calls": 40,
        "VR35A_calls": 20,
        "private_invocation_limit_after_proof": 1,
        "private_source_bytes_after_proof_if_ready": PRIVATE_SOURCE_BYTES,
        "neural_payload_bytes": 0,
        "target_bytes": 0,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proof-gated MARC2 task-aware cohort confirmation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "qualify", "inspect", "execute"):
        subparsers.add_parser(command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        result = build_plan()
    elif args.command == "qualify":
        result = qualify_generated()
    elif args.command == "inspect":
        result = inspect_fixed()
    else:
        result = execute_fixed()
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
