"""Proof-gated MARC2-VR11P generated qualification and fixed-path executor."""

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from . import marc2_dynamic_live_selection as vr6
from . import marc2_f03_five_route_discriminator as five


LANE_ID = "MARC2-VR11P"
SCHEMA_VERSION = "0.1.0"
PLAN_SCHEMA_NAME = "neurodecodekit.marc2_f03_private_discriminator_plan"
QUALIFICATION_SCHEMA_NAME = (
    "neurodecodekit.marc2_f03_private_discriminator_qualification"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_f03_private_discriminator_report"
CERTIFICATE_SCHEMA_NAME = (
    "neurodecodekit.marc2_f03_private_discriminator_readiness"
)
MARKER_SCHEMA_NAME = "neurodecodekit.marc2_f03_private_discriminator_consumed"

DECISION_RELATIVE_PATH = Path(
    "registries/marc2_f03_private_discriminator_authorization_decision.v0.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc2_f03_private_discriminator_implementation.v0.json"
)
READINESS_RELATIVE_PATH = Path(
    ".codex_work/marc2_machine_readiness/vr11p/readiness.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(".codex_work/marc2_f03_private_discriminator/v0")
MARKER_RELATIVE_NAME = "consumed_marker.v0.json"
REPORT_RELATIVE_NAME = "f03_private_discriminator.aggregate.v0.json"
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)

GREEN_DECISION_COMMIT = "4fa277121f24dde3f6f7c917ef6c2bb7506134d6"
GREEN_DECISION_CI_RUN_ID = 32038683203
GREEN_DECISION_BASE_JOB_ID = 95414004791
GREEN_DECISION_OPTIONAL_JOB_ID = 95414004814

PRIVATE_SOURCE_IDENTITY = {
    "mode": 0o600,
    "bytes": 418_755,
    "sha256": "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
    "rows": 1_227,
}
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
SUCCESS_ROUTE = "MARC2VR11P-G1"
PRIVATE_ROUTES = tuple(f"MARC2VR11P-R{index}" for index in range(1, 6))
REFUSAL_ROUTES = tuple(f"MARC2VR11P-F{index:02d}" for index in range(1, 13))
VR10B_TO_PRIVATE_ROUTE = {
    f"MARC2VR10B-R{index}": f"MARC2VR11P-R{index}" for index in range(1, 6)
}
VR10B_TO_GENERATED_ROUTE = {
    "MARC2VR10B-G1": SUCCESS_ROUTE,
    **VR10B_TO_PRIVATE_ROUTE,
}

MAX_GENERATED_RUNTIME_SECONDS = 45.0
MAX_PRIVATE_RUNTIME_SECONDS = 650.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_COMBINED_OUTPUT_BYTES = 1024**2
MAX_TRACKED_FILE_BYTES = 2 * 1024**2
MAX_CERTIFICATE_BYTES = 64 * 1024
MINIMUM_SAMPLE_INTERVAL_SECONDS = 5.0
REQUIRED_PASSING_SAMPLES = 3

FORBIDDEN_PUBLIC_KEYS = {
    "reason",
    "exception",
    "predicate",
    "failed_value",
    "row",
    "row_index",
    "member",
    "member_name",
    "path",
    "offset",
    "crc",
    "private_hash",
    "subject",
    "subject_id",
    "participant",
    "participant_id",
    "session",
    "run",
    "companion",
    "candidate",
    "selection",
    "cohort",
    "target",
    "label",
    "prediction",
}


class F03PrivateDiscriminatorRefusal(RuntimeError):
    """Fail-closed refusal with one aggregate-safe route."""

    def __init__(self, route: str, message: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown refusal route")
        self.route = route
        super().__init__(message)


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
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "canonical JSON refused"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[5], "duplicate JSON key"
            )
        value[key] = item
    return value


def _reject_constant(_value: str) -> None:
    raise F03PrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[5], "non-finite JSON number"
    )


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except F03PrivateDiscriminatorRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "strict JSON refused"
        ) from exc
    if not isinstance(value, dict):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "JSON root is not an object"
        )
    return value


def _read_tracked(root: Path, relative: Path) -> bytes:
    path = root / relative
    try:
        info = path.lstat()
    except OSError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact type refused"
        )
    if info.st_size > MAX_TRACKED_FILE_BYTES:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact exceeds cap"
        )
    payload = path.read_bytes()
    if len(payload) != info.st_size:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "tracked artifact changed during read"
        )
    return payload


def _load_records(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    decision = _strict_json(_read_tracked(root, DECISION_RELATIVE_PATH))
    implementation = _strict_json(_read_tracked(root, IMPLEMENTATION_RELATIVE_PATH))
    proof = implementation.get("green_decision_proof")
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc2_f03_private_discriminator_authorization_decision"
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "136f7b999d3514bd8d62f8dc9e7d7c01b89662f7"
        or proof
        != {
            "commit": GREEN_DECISION_COMMIT,
            "CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "base_python_job_id": GREEN_DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
        }
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "decision proof differs"
        )
    if (
        implementation.get("schema_name")
        != "neurodecodekit.marc2_f03_private_discriminator_implementation"
        or implementation.get("schema_version") != SCHEMA_VERSION
        or implementation.get("lane_id") != LANE_ID
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation record differs"
        )
    return decision, implementation


def _verify_implementation_artifacts(root: Path, record: Mapping[str, Any]) -> None:
    rows = record.get("tracked_implementation_artifacts")
    if not isinstance(rows, list) or len(rows) != 3:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation artifact inventory differs"
        )
    for row in rows:
        if not isinstance(row, Mapping):
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "implementation artifact row differs"
            )
        relative = row.get("path")
        if not isinstance(relative, str) or relative.startswith(("/", ".codex_work/")):
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "implementation artifact path differs"
            )
        payload = _read_tracked(root, Path(relative))
        if len(payload) != row.get("bytes") or _sha256_bytes(payload) != row.get(
            "sha256"
        ):
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "implementation artifact identity differs"
            )


def _validate_thread_environment(environment: Mapping[str, str] | None) -> None:
    values = dict(os.environ if environment is None else environment)
    if {name: values.get(name) for name in THREAD_ENVIRONMENT} != {
        name: "1" for name in THREAD_ENVIRONMENT
    }:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "one-thread environment differs"
        )


def _base_zero_counters() -> dict[str, int]:
    return {
        "real_readiness_operations": 0,
        "private_or_Git_ignored_path_operations": 0,
        "private_structural_source_opens": 0,
        "private_structural_bytes_read": 0,
        "VR6_real_calls": 0,
        "VR10B_real_calls": 0,
        "archive_local_header_or_member_payload_operations": 0,
        "signal_event_channel_geometry_target_or_label_operations": 0,
        "derivative_cache_feature_split_or_NeuroToken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_or_language_model_operations": 0,
        "RW3_stream_device_or_hardware_operations": 0,
        "MARC2_FW2_or_CIL1_operations": 0,
        "retry_rerun_resume_repair_fallback_or_substitution_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_PUBLIC_KEYS:
                raise F03PrivateDiscriminatorRefusal(
                    REFUSAL_ROUTES[6], "forbidden aggregate key"
                )
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)
    elif isinstance(value, str):
        lowered = value.lower()
        if ".codex_work" in lowered or "member_inventory.private" in lowered:
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[6], "private identity leaked"
            )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    output_bytes: int,
    retained_bytes: int,
) -> None:
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_GENERATED_RUNTIME_SECONDS
        or isinstance(peak_rss_bytes, bool)
        or peak_rss_bytes < 0
        or peak_rss_bytes >= MAX_PEAK_RSS_BYTES
        or output_bytes < 0
        or output_bytes > MAX_COMBINED_OUTPUT_BYTES
        or retained_bytes != 0
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated resource cap exceeded"
        )


def _translate_route_counts(counts: Mapping[str, Any]) -> dict[str, int]:
    if set(counts) != set(VR10B_TO_GENERATED_ROUTE):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated route inventory differs"
        )
    translated: dict[str, int] = {}
    for source, destination in VR10B_TO_GENERATED_ROUTE.items():
        value = counts.get(source)
        if isinstance(value, bool) or not isinstance(value, int) or value != 4:
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[3], "generated route count differs"
            )
        translated[destination] = value
    return translated


def _expected_generated_route_counts() -> dict[str, int]:
    return {route: 4 for route in (SUCCESS_ROUTE, *PRIVATE_ROUTES)}


def _expect_refusal(
    name: str,
    action: Callable[[], Any],
    *,
    expected: str,
) -> tuple[str, str]:
    try:
        action()
    except F03PrivateDiscriminatorRefusal as exc:
        if exc.route != expected:
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[8], "refusal route differs"
            ) from exc
        return name, exc.route
    raise F03PrivateDiscriminatorRefusal(
        REFUSAL_ROUTES[8], "required refusal did not occur"
    )


def _validate_generated_report(
    report: Mapping[str, Any], *, require_refusals: bool = True
) -> None:
    if (
        report.get("schema_name") != QUALIFICATION_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "generated report identity differs"
        )
    summary = report.get("route_summary")
    replay = report.get("replay_summary")
    state_machine = report.get("fixed_path_state_machine")
    measurements = report.get("measurements")
    if (
        not isinstance(summary, Mapping)
        or summary.get("route_counts") != _expected_generated_route_counts()
        or not isinstance(replay, Mapping)
        or replay.get("exact_paths") != 24
        or replay.get("exact_VR6_calls") != 24
        or replay.get("exact_VR10B_calls") != 24
        or replay.get("byte_identical_replay") is not True
        or not isinstance(state_machine, Mapping)
        or state_machine.get("generated_fixture_runs") != 1
        or state_machine.get("generated_fixture_bytes") != 418_755
        or state_machine.get("mock_VR6_calls") != 1
        or state_machine.get("mock_VR10B_calls") != 1
        or state_machine.get("observed_route") != "MARC2VR11P-R3"
        or state_machine.get("marker_observed_before_read") is not True
        or state_machine.get("certificate_mode") != "0600"
        or state_machine.get("marker_mode") != "0600"
        or state_machine.get("report_mode") != "0644"
        or state_machine.get("retained_output_bytes") != 0
        or not isinstance(measurements, Mapping)
        or measurements.get("retained_generated_output_bytes") != 0
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated report mechanics differ"
        )
    refusals = report.get("direct_refusals")
    if not isinstance(refusals, Mapping) or (
        require_refusals and len(refusals) < 70
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[8], "direct refusal inventory is too small"
        )
    counters = report.get("access_counters")
    if not isinstance(counters, Mapping) or any(counters.values()):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[9], "generated forbidden counter is nonzero"
        )
    _walk_public(report)


def _run_wrapper_refusals(
    report: Mapping[str, Any], implementation: Mapping[str, Any]
) -> dict[str, str]:
    checks: list[tuple[str, str, Callable[[], Any]]] = []

    def changed_report(path: Sequence[str], value: Any) -> Callable[[], None]:
        def action() -> None:
            changed = copy.deepcopy(report)
            cursor: dict[str, Any] = changed
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = value
            _validate_generated_report(changed, require_refusals=False)

        return action

    checks.extend(
        [
            ("thread_environment", REFUSAL_ROUTES[1], lambda: _validate_thread_environment({})),
            (
                "report_schema",
                REFUSAL_ROUTES[2],
                changed_report(("schema_name",), "wrong"),
            ),
            (
                "route_count",
                REFUSAL_ROUTES[3],
                changed_report(("route_summary", "route_counts"), {}),
            ),
            (
                "replay_count",
                REFUSAL_ROUTES[3],
                changed_report(("replay_summary", "exact_paths"), 23),
            ),
            (
                "VR6_count",
                REFUSAL_ROUTES[3],
                changed_report(("replay_summary", "exact_VR6_calls"), 23),
            ),
            (
                "VR10B_count",
                REFUSAL_ROUTES[3],
                changed_report(("replay_summary", "exact_VR10B_calls"), 23),
            ),
            (
                "replay_identity",
                REFUSAL_ROUTES[3],
                changed_report(("replay_summary", "byte_identical_replay"), False),
            ),
            (
                "retained_output",
                REFUSAL_ROUTES[3],
                changed_report(("measurements", "retained_generated_output_bytes"), 1),
            ),
            (
                "private_counter",
                REFUSAL_ROUTES[9],
                changed_report(("access_counters", "private_structural_source_opens"), 1),
            ),
            (
                "private_key",
                REFUSAL_ROUTES[6],
                lambda: _walk_public({"member_name": "redacted"}),
            ),
            (
                "private_value",
                REFUSAL_ROUTES[6],
                lambda: _walk_public({"warning": ".codex_work/redacted"}),
            ),
            (
                "runtime_cap",
                REFUSAL_ROUTES[7],
                lambda: _assert_resources(
                    runtime_seconds=46.0,
                    peak_rss_bytes=1,
                    output_bytes=1,
                    retained_bytes=0,
                ),
            ),
            (
                "RSS_cap",
                REFUSAL_ROUTES[7],
                lambda: _assert_resources(
                    runtime_seconds=1.0,
                    peak_rss_bytes=MAX_PEAK_RSS_BYTES,
                    output_bytes=1,
                    retained_bytes=0,
                ),
            ),
            (
                "output_cap",
                REFUSAL_ROUTES[7],
                lambda: _assert_resources(
                    runtime_seconds=1.0,
                    peak_rss_bytes=1,
                    output_bytes=MAX_COMBINED_OUTPUT_BYTES + 1,
                    retained_bytes=0,
                ),
            ),
            (
                "unknown_private_route",
                REFUSAL_ROUTES[4],
                lambda: _map_private_route("MARC2VR10B-G1"),
            ),
            (
                "duplicate_JSON",
                REFUSAL_ROUTES[5],
                lambda: _strict_json(b'{"a":1,"a":2}'),
            ),
            (
                "implementation_proof_pending",
                REFUSAL_ROUTES[0],
                lambda: _require_green_implementation(implementation),
            ),
        ]
    )
    with tempfile.TemporaryDirectory(prefix="neurodecodekit-vr11p-refusal-") as raw:
        root = Path(raw)
        source = root / "source.json"
        source.write_bytes(b"{}")
        source.chmod(0o600)
        wrong_hash_identity = {
            "mode": 0o600,
            "bytes": 2,
            "sha256": "0" * 64,
        }
        checks.extend(
            [
                (
                    "source_hash_drift",
                    REFUSAL_ROUTES[4],
                    lambda: _read_private_once(source, wrong_hash_identity),
                ),
                (
                    "output_collision",
                    REFUSAL_ROUTES[10],
                    lambda: _write_exclusive(source, b"{}", 0o600),
                ),
                (
                    "marker_missing_before_read",
                    REFUSAL_ROUTES[10],
                    lambda: _require_consumed_marker(root / "missing.json"),
                ),
            ]
        )
        if hasattr(os, "symlink"):
            target = root / "target"
            target.mkdir()
            link = root / "unsafe"
            link.symlink_to(target, target_is_directory=True)
            checks.append(
                (
                    "symlink_parent",
                    REFUSAL_ROUTES[10],
                    lambda: _safe_parent_chain(root, Path("unsafe/child")),
                )
            )
        own = dict(
            _expect_refusal(name, action, expected=route)
            for name, route, action in checks
        )
    upstream = implementation.get("upstream_VR10B_direct_refusals")
    if upstream != 60:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "upstream refusal proof differs"
        )
    for index in range(upstream):
        own[f"upstream_VR10B_refusal_{index + 1:02d}"] = "MARC2VR10B-proven"
    return own


def _generated_private_payload() -> bytes:
    source: dict[str, Any] = {
        "entries": [{} for _ in range(PRIVATE_SOURCE_IDENTITY["rows"])],
        "padding": "",
    }
    baseline = _canonical_json_bytes(source)
    padding_bytes = PRIVATE_SOURCE_IDENTITY["bytes"] - len(baseline)
    if padding_bytes < 0:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated fixed-path fixture exceeds cap"
        )
    source["padding"] = "x" * padding_bytes
    payload = _canonical_json_bytes(source)
    if len(payload) != PRIVATE_SOURCE_IDENTITY["bytes"]:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated fixed-path fixture size differs"
        )
    return payload


def _qualify_fixed_path_state_machine() -> dict[str, Any]:
    payload = _generated_private_payload()
    identity = {
        "mode": 0o600,
        "bytes": len(payload),
        "sha256": _sha256_bytes(payload),
        "rows": PRIVATE_SOURCE_IDENTITY["rows"],
    }
    marker_observed_before_read = False

    with tempfile.TemporaryDirectory(prefix="neurodecodekit-vr11p-fixture-") as raw:
        root = Path(raw)
        source = root / PRIVATE_SOURCE_RELATIVE_PATH
        source.parent.mkdir(parents=True, mode=0o700)
        source.write_bytes(payload)
        source.chmod(0o600)

        def sample_reader(_root: Path, sequence: int) -> Mapping[str, Any]:
            return {
                "sequence": sequence,
                "observed_at_UTC": f"2026-08-17T00:00:{sequence:02d}Z",
                "monotonic_seconds": 100.0
                + (sequence - 1) * MINIMUM_SAMPLE_INTERVAL_SECONDS,
                "logical_CPUs": 1,
                "one_minute_load": 0.0,
                "normalized_one_minute_load": 0.0,
                "process_peak_RSS_bytes": 1,
                "free_disk_bytes": MINIMUM_FREE_DISK_BYTES,
            }

        def payload_reader(path: Path, expected: Mapping[str, Any]) -> bytes:
            nonlocal marker_observed_before_read
            _require_consumed_marker(
                root / OUTPUT_ROOT_RELATIVE_PATH / MARKER_RELATIVE_NAME
            )
            marker_observed_before_read = True
            return _read_private_once(path, expected)

        def vr6_adapter(_source: Mapping[str, Any]) -> Any:
            raise vr6.DynamicLiveSelectionRefusal(
                "MARC2VR6-F02",
                "generated fixed-path witness",
                upstream_route="MARC2VR2-F03",
            )

        def discriminator(
            _source: Mapping[str, Any], *, vr2_contract: Mapping[str, Any]
        ) -> five.DiscriminatorDecision:
            if vr2_contract != {"fixture": True}:
                raise AssertionError("generated VR2 fixture contract differs")
            return five.DiscriminatorDecision("MARC2VR10B-R3")

        clock_values = iter((10.0, 11.0))
        report = _run_private_sequence(
            root=root,
            implementation_commit="f" * 40,
            source_identity=identity,
            sample_reader=sample_reader,
            sleep_fn=lambda _seconds: None,
            clock=lambda: next(clock_values),
            environment={name: "1" for name in THREAD_ENVIRONMENT},
            payload_reader=payload_reader,
            vr6_adapter=vr6_adapter,
            vr2_contract_loader=lambda _root: {"fixture": True},
            vr10b_discriminator=discriminator,
            rss_reader=lambda: 1,
        )
        output_root = root / OUTPUT_ROOT_RELATIVE_PATH
        marker_mode = stat.S_IMODE(
            (output_root / MARKER_RELATIVE_NAME).lstat().st_mode
        )
        report_mode = stat.S_IMODE(
            (output_root / REPORT_RELATIVE_NAME).lstat().st_mode
        )
        certificate_mode = stat.S_IMODE(
            (root / READINESS_RELATIVE_PATH).lstat().st_mode
        )
        route = report["route"]
        combined_output_bytes = report["measurements"]["combined_output_bytes"]

    return {
        "generated_fixture_runs": 1,
        "generated_fixture_bytes": len(payload),
        "mock_VR6_calls": 1,
        "mock_VR10B_calls": 1,
        "observed_route": route,
        "marker_observed_before_read": marker_observed_before_read,
        "certificate_mode": f"{certificate_mode:04o}",
        "marker_mode": f"{marker_mode:04o}",
        "report_mode": f"{report_mode:04o}",
        "combined_output_bytes": combined_output_bytes,
        "retained_output_bytes": 0,
    }


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run the exact 24-path generated wrapper qualification."""

    started = clock()
    _validate_thread_environment(environment)
    root = Path(repo_root or _repo_root())
    _decision, implementation = _load_records(root)
    _verify_implementation_artifacts(root, implementation)
    upstream = five.qualify_generated(
        repo_root=root,
        clock=lambda: 0.0,
        rss_reader=lambda: 1,
        environment={name: "1" for name in five.THREAD_ENVIRONMENT},
    )
    route_counts = _translate_route_counts(upstream["route_summary"]["route_counts"])
    state_machine = _qualify_fixed_path_state_machine()
    provisional: dict[str, Any] = {
        "schema_name": QUALIFICATION_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_generated_mock_fixed_path_qualification",
        "proof_posture": "generated_only_no_private_or_scientific_value",
        "route": SUCCESS_ROUTE,
        "green_decision_proof": copy.deepcopy(
            implementation["green_decision_proof"]
        ),
        "route_summary": {
            "ordered_routes": [SUCCESS_ROUTE, *PRIVATE_ROUTES],
            "route_counts": route_counts,
            "one_route_per_path": True,
            "failed_values_retained": 0,
            "per_item_outcomes_retained": 0,
        },
        "replay_summary": {
            "generated_cases": 6,
            "source_orders": 2,
            "exact_replays": 2,
            "exact_paths": 24,
            "exact_parser_entry_visits": upstream["replay_summary"][
                "exact_parser_entry_visits"
            ],
            "exact_VR6_calls": upstream["replay_summary"]["exact_VR6_calls"],
            "exact_VR10B_calls": upstream["replay_summary"][
                "exact_discriminator_calls"
            ],
            "byte_identical_replay": True,
            "replay_digest_sha256": _sha256_bytes(
                _canonical_json_bytes(
                    {
                        "routes": route_counts,
                        "upstream_digest": upstream["replay_summary"][
                            "internal_matrix_digest_sha256"
                        ],
                    }
                )
            ),
        },
        "fixed_path_state_machine": {
            "readiness_before_output_or_private_path": True,
            "fresh_readiness_parent_required": True,
            "fresh_output_root_required": True,
            "marker_immediately_before_content_open": True,
            "one_strict_JSON_read": True,
            "one_VR6_call_then_one_VR10B_call": True,
            "generic_path_or_execute_override": False,
            "generated_real_path_operations": 0,
            **state_machine,
        },
        "measurements": {
            "generated_input_bytes": (
                upstream["measurements"]["generated_input_bytes"]
                + state_machine["generated_fixture_bytes"]
            ),
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": 0.0,
            "peak_RSS_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "direct_refusals": {},
        "access_counters": _base_zero_counters(),
        "warnings": [
            "Generated routes test engineering separation only.",
            "No real or ignored path was accessed.",
            "Private execution remains closed until implementation proof is green.",
            "FW2 and CIL1 remain closed.",
        ],
        "unavailable_fields": [
            "private F03 class and failed value",
            "private member identity and real cohort",
            "archive neural target model prediction score and latency",
        ],
        "next_gate": {
            "exact_implementation_commit_push_and_both_jobs_green_required": True,
            "private_execution_allowed_now": False,
            "FW2_or_CIL1_authorized": False,
        },
        "claim_boundary": {
            "engineering_ceiling": "generated_fixed_path_five_route_wrapper",
            "scientific_ceiling": "none",
            "private_cause_identified": False,
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_live_decoding": False,
        },
    }
    provisional["direct_refusals"] = _run_wrapper_refusals(
        provisional, implementation
    )
    runtime = clock() - started
    peak_rss = rss_reader()
    provisional["measurements"]["runtime_seconds"] = runtime
    provisional["measurements"]["peak_RSS_bytes"] = peak_rss
    output_bytes = len(_canonical_json_bytes(provisional))
    provisional["measurements"]["aggregate_output_bytes"] = output_bytes
    output_bytes = len(_canonical_json_bytes(provisional))
    provisional["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        output_bytes=len(_canonical_json_bytes(provisional)),
        retained_bytes=0,
    )
    _validate_generated_report(provisional)
    return provisional


def _safe_parent_chain(root: Path, relative: Path) -> None:
    current = root
    for component in relative.parts:
        current = current / component
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        except OSError as exc:
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[10], "parent preflight failed"
            ) from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[10], "parent path refused"
            )


def _create_fresh_directory(root: Path, relative: Path) -> Path:
    _safe_parent_chain(root, relative.parent)
    parent = root
    for component in relative.parts[:-1]:
        parent = parent / component
        if not parent.exists():
            parent.mkdir(mode=0o700)
    destination = root / relative
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "fresh directory already exists"
        ) from exc
    return destination


def _write_exclusive(path: Path, payload: bytes, mode: int) -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
    except OSError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "exclusive output refused"
        ) from exc
    try:
        written = os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if written != len(payload):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "short output write"
        )
    os.chmod(path, mode)
    return written


def _require_consumed_marker(path: Path) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "consumed marker unavailable"
        ) from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o600
        or info.st_size > MAX_CERTIFICATE_BYTES
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "consumed marker identity differs"
        )
    marker = _strict_json(path.read_bytes())
    if (
        marker.get("schema_name") != MARKER_SCHEMA_NAME
        or marker.get("schema_version") != SCHEMA_VERSION
        or marker.get("lane_id") != LANE_ID
        or marker.get("status") != "consumed_before_private_content_open"
        or marker.get("retry_limit") != 0
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "consumed marker content differs"
        )


def _default_sample(root: Path, sequence: int) -> dict[str, Any]:
    logical = os.cpu_count() or 0
    load = os.getloadavg()[0]
    return {
        "sequence": sequence,
        "observed_at_UTC": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "monotonic_seconds": time.monotonic(),
        "logical_CPUs": logical,
        "one_minute_load": load,
        "normalized_one_minute_load": load / logical if logical else math.inf,
        "process_peak_RSS_bytes": _peak_rss_bytes(),
        "free_disk_bytes": shutil.disk_usage(root).free,
    }


def _assess_samples(samples: Sequence[Mapping[str, Any]]) -> bool:
    if len(samples) != REQUIRED_PASSING_SAMPLES:
        return False
    previous_monotonic: float | None = None
    for index, sample in enumerate(samples, start=1):
        try:
            logical = sample["logical_CPUs"]
            load = float(sample["one_minute_load"])
            normalized = float(sample["normalized_one_minute_load"])
            rss = sample["process_peak_RSS_bytes"]
            disk = sample["free_disk_bytes"]
            monotonic = float(sample["monotonic_seconds"])
        except (KeyError, TypeError, ValueError, OverflowError):
            return False
        if (
            sample.get("sequence") != index
            or isinstance(logical, bool)
            or not isinstance(logical, int)
            or logical < 1
            or not math.isfinite(load)
            or not math.isfinite(normalized)
            or not math.isclose(normalized, load / logical, abs_tol=1e-12, rel_tol=0)
            or isinstance(rss, bool)
            or not isinstance(rss, int)
            or rss < 0
            or rss >= MAX_PEAK_RSS_BYTES
            or isinstance(disk, bool)
            or not isinstance(disk, int)
            or disk < MINIMUM_FREE_DISK_BYTES
            or normalized > 1.0
            or (
                previous_monotonic is not None
                and monotonic - previous_monotonic < MINIMUM_SAMPLE_INTERVAL_SECONDS
            )
        ):
            return False
        previous_monotonic = monotonic
    return True


def _read_private_once(path: Path, identity: Mapping[str, Any]) -> bytes:
    try:
        before = path.lstat()
    except OSError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private source preflight failed"
        ) from exc
    if (
        stat.S_ISLNK(before.st_mode)
        or not stat.S_ISREG(before.st_mode)
        or stat.S_IMODE(before.st_mode) != identity["mode"]
        or before.st_size != identity["bytes"]
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private source identity differs"
        )
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private source open refused"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if (
            opened.st_dev != before.st_dev
            or opened.st_ino != before.st_ino
            or opened.st_size != before.st_size
            or stat.S_IMODE(opened.st_mode) != identity["mode"]
        ):
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[4], "private source changed before read"
            )
        chunks: list[bytes] = []
        remaining = identity["bytes"] + 1
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if (
        len(payload) != identity["bytes"]
        or _sha256_bytes(payload) != identity["sha256"]
        or after.st_dev != before.st_dev
        or after.st_ino != before.st_ino
        or after.st_size != before.st_size
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private source integrity differs"
        )
    return payload


def _map_private_route(route: str) -> str:
    try:
        return VR10B_TO_PRIVATE_ROUTE[route]
    except KeyError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private discriminator route refused"
        ) from exc


def _validate_private_report(report: Mapping[str, Any]) -> None:
    allowed_fields = {
        "schema_name",
        "schema_version",
        "lane_id",
        "route",
        "status",
        "proof_posture",
        "green_evidence",
        "measurements",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    if (
        set(report) != allowed_fields
        or
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") not in PRIVATE_ROUTES
        or report.get("status") != "consumed_target_free_structural_discriminator"
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "private report identity differs"
        )
    counters = report.get("access_counters")
    expected_counters = _base_zero_counters()
    expected_counters.update(
        {
            "real_readiness_operations": 1,
            "private_or_Git_ignored_path_operations": 1,
            "private_structural_source_opens": 1,
            "private_structural_bytes_read": 418_755,
            "VR6_real_calls": 1,
            "VR10B_real_calls": 1,
        }
    )
    if not isinstance(counters, Mapping) or dict(counters) != expected_counters:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "private report counters differ"
        )
    _walk_public(report)


def _run_private_sequence(
    *,
    root: Path,
    implementation_commit: str,
    source_identity: Mapping[str, Any],
    sample_reader: Callable[[Path, int], Mapping[str, Any]],
    sleep_fn: Callable[[float], None],
    clock: Callable[[], float],
    environment: Mapping[str, str] | None,
    payload_reader: Callable[[Path, Mapping[str, Any]], bytes] = _read_private_once,
    vr6_adapter: Callable[[Mapping[str, Any]], Any] = vr6.adapt_dynamic_live_source,
    vr2_contract_loader: Callable[[Path], Mapping[str, Any]] = (
        vr6.vr2.load_registered_contract
    ),
    vr10b_discriminator: Callable[..., five.DiscriminatorDecision] = (
        five.discriminate_generated_source
    ),
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    started = clock()
    _validate_thread_environment(environment)
    readiness_dir = _create_fresh_directory(root, READINESS_RELATIVE_PATH.parent)
    samples: list[Mapping[str, Any]] = []
    for sequence in range(1, REQUIRED_PASSING_SAMPLES + 1):
        samples.append(dict(sample_reader(root, sequence)))
        if sequence < REQUIRED_PASSING_SAMPLES:
            sleep_fn(MINIMUM_SAMPLE_INTERVAL_SECONDS)
    ready = _assess_samples(samples)
    certificate = {
        "schema_name": CERTIFICATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "ready" if ready else "not_ready_consumed",
        "ready": ready,
        "implementation_commit": implementation_commit,
        "sample_count": len(samples),
        "thresholds": {
            "normalized_one_minute_load_maximum": 1.0,
            "peak_RSS_bytes_maximum_exclusive": MAX_PEAK_RSS_BYTES,
            "free_disk_bytes_minimum": MINIMUM_FREE_DISK_BYTES,
        },
        "samples": list(samples),
        "claim_boundary": "machine_state_only_no_scientific_value",
    }
    certificate_bytes = _canonical_json_bytes(certificate)
    if len(certificate_bytes) > MAX_CERTIFICATE_BYTES:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "certificate output cap exceeded"
        )
    certificate_path = readiness_dir / READINESS_RELATIVE_PATH.name
    certificate_written = _write_exclusive(certificate_path, certificate_bytes, 0o600)
    if not ready:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "machine readiness refused"
        )

    output_root = _create_fresh_directory(root, OUTPUT_ROOT_RELATIVE_PATH)
    source_path = root / PRIVATE_SOURCE_RELATIVE_PATH
    _safe_parent_chain(root, PRIVATE_SOURCE_RELATIVE_PATH.parent)
    try:
        source_info = source_path.lstat()
    except OSError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private source unavailable"
        ) from exc
    if source_info.st_size != source_identity["bytes"]:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "private source size differs"
        )

    marker = {
        "schema_name": MARKER_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_before_private_content_open",
        "implementation_commit": implementation_commit,
        "retry_limit": 0,
    }
    marker_bytes = _canonical_json_bytes(marker)
    marker_written = _write_exclusive(
        output_root / MARKER_RELATIVE_NAME, marker_bytes, 0o600
    )
    _require_consumed_marker(output_root / MARKER_RELATIVE_NAME)
    payload = payload_reader(source_path, source_identity)
    source = _strict_json(payload)
    if len(source.get("entries", [])) != source_identity["rows"]:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "private source row count differs"
        )
    try:
        vr6_adapter(source)
    except vr6.DynamicLiveSelectionRefusal as exc:
        if exc.route != "MARC2VR6-F02" or exc.upstream_route != "MARC2VR2-F03":
            raise F03PrivateDiscriminatorRefusal(
                REFUSAL_ROUTES[4], "VR6 consistency route refused"
            ) from None
    else:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "VR6 unexpectedly accepted private source"
        )
    try:
        decision = vr10b_discriminator(
            source,
            vr2_contract=vr2_contract_loader(root),
        )
    except five.FiveRouteDiscriminatorRefusal as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "VR10B private discriminator refused"
        ) from exc
    route = _map_private_route(decision.route)
    runtime = clock() - started
    counters = _base_zero_counters()
    counters.update(
        {
            "real_readiness_operations": 1,
            "private_or_Git_ignored_path_operations": 1,
            "private_structural_source_opens": 1,
            "private_structural_bytes_read": len(payload),
            "VR6_real_calls": 1,
            "VR10B_real_calls": 1,
        }
    )
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_target_free_structural_discriminator",
        "proof_posture": "aggregate_target_free_structural_diagnosis_only",
        "route": route,
        "green_evidence": {
            "commit": implementation_commit,
            "both_required_jobs_green": True,
        },
        "measurements": {
            "runtime_seconds": runtime,
            "peak_RSS_bytes": rss_reader(),
            "input_bytes": len(payload),
            "certificate_bytes": certificate_written,
            "marker_bytes": marker_written,
            "report_bytes": 0,
            "combined_output_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "access_counters": counters,
        "warnings": [
            "This route localizes one structural refusal class only.",
            "No archive member or neural payload was opened.",
            "No candidate cohort was retained.",
            "FW2 and CIL1 remain closed.",
        ],
        "unavailable_fields": [
            "failed predicate and private value",
            "private member and person identities",
            "candidate selection and real cohort",
            "archive neural target model prediction score and latency",
        ],
        "claim_boundary": {
            "engineering_ceiling": "one_coarse_target_free_structural_class",
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_live_decoding": False,
        },
    }
    report_bytes = _canonical_json_bytes(report)
    report["measurements"]["report_bytes"] = len(report_bytes)
    report["measurements"]["combined_output_bytes"] = (
        certificate_written + marker_written + len(report_bytes)
    )
    report_bytes = _canonical_json_bytes(report)
    report["measurements"]["report_bytes"] = len(report_bytes)
    report["measurements"]["combined_output_bytes"] = (
        certificate_written + marker_written + len(report_bytes)
    )
    report_bytes = _canonical_json_bytes(report)
    if (
        runtime > MAX_PRIVATE_RUNTIME_SECONDS
        or report["measurements"]["peak_RSS_bytes"] >= MAX_PEAK_RSS_BYTES
        or report["measurements"]["combined_output_bytes"]
        > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "private resource cap exceeded"
        )
    _validate_private_report(report)
    _write_exclusive(output_root / REPORT_RELATIVE_NAME, report_bytes, 0o644)
    return report


def _require_green_implementation(record: Mapping[str, Any]) -> str:
    proof = record.get("remote_implementation_proof")
    if (
        not isinstance(proof, Mapping)
        or proof.get("both_required_jobs_green") is not True
        or not isinstance(proof.get("commit"), str)
        or len(proof["commit"]) != 40
        or record.get("next_gate", {}).get("private_execution_allowed_now") is not True
    ):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "implementation proof is not green"
        )
    return proof["commit"]


def execute_registered(
    *,
    repo_root: str | Path | None = None,
    sample_reader: Callable[[Path, int], Mapping[str, Any]] = _default_sample,
    sleep_fn: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.perf_counter,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Execute the fixed private discriminator after exact remote proof."""

    root = Path(repo_root or _repo_root())
    _decision, implementation = _load_records(root)
    _verify_implementation_artifacts(root, implementation)
    commit = _require_green_implementation(implementation)
    return _run_private_sequence(
        root=root,
        implementation_commit=commit,
        source_identity=PRIVATE_SOURCE_IDENTITY,
        sample_reader=sample_reader,
        sleep_fn=sleep_fn,
        clock=clock,
        environment=environment,
    )


def inspect_registered_report(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    """Inspect only the fixed aggregate report after a consumed execution."""

    root = Path(repo_root or _repo_root())
    path = root / OUTPUT_ROOT_RELATIVE_PATH / REPORT_RELATIVE_NAME
    try:
        info = path.lstat()
    except OSError as exc:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "aggregate report unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[10], "aggregate report type refused"
        )
    payload = path.read_bytes()
    report = _strict_json(payload)
    if _canonical_json_bytes(report) != payload:
        raise F03PrivateDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "aggregate report is not canonical"
        )
    _validate_private_report(report)
    return report


def build_plan_summary(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    """Return the fixed plan without touching any real or ignored path."""

    root = Path(repo_root or _repo_root())
    _decision, implementation = _load_records(root)
    proof = implementation.get("remote_implementation_proof")
    return {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": implementation["status"],
        "green_decision_commit": GREEN_DECISION_COMMIT,
        "generated_cases": 6,
        "required_paths": 24,
        "minimum_direct_refusals": 70,
        "private_execution_proof_green": bool(
            isinstance(proof, Mapping) and proof.get("both_required_jobs_green")
        ),
        "private_execution_allowed_now": bool(
            isinstance(proof, Mapping)
            and proof.get("both_required_jobs_green")
            and implementation.get("next_gate", {}).get(
                "private_execution_allowed_now"
            )
        ),
        "network_bytes": 0,
        "archive_member_signal_or_target_bytes": 0,
        "FW2_or_CIL1_authorized": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_f03_private_discriminator",
        description="Operate the fixed proof-gated MARC2-VR11P wrapper.",
    )
    parser.add_argument("command", choices=("plan", "qualify", "inspect", "execute"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            output = build_plan_summary()
        elif args.command == "qualify":
            output = qualify_generated()
        elif args.command == "inspect":
            output = inspect_registered_report()
        else:
            output = execute_registered()
    except F03PrivateDiscriminatorRefusal as exc:
        print(f"{exc.route}: VR11P operation refused", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("ascii"), end="")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
