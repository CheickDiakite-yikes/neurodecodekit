"""Generated full-scale parser-to-VR2 diagnostic relay qualification."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import os
import resource
import stat
import sys
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc1_central_directory_audit as parser
from neurodecodekit.datasets import marc1_central_directory_live as producer
from neurodecodekit.datasets import marc2_dynamic_live_selection as vr6
from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR8B"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_generated_diagnostic_relay_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_generated_diagnostic_relay_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_generated_diagnostic_relay_contract.v0.json"
)
CONTRACT_SHA256 = "1ac4eecef15621fb3c97a9a26794641564f0c34ed2ba6f012d3ee6e6c89674db"
GREEN_REGISTRATION_COMMIT = "5607fe895faaacce80bdd14474d211b09d1656d4"
GREEN_REGISTRATION_CI_RUN_ID = 31_987_093_865
GREEN_REGISTRATION_BASE_JOB_ID = 95_263_869_003
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_263_869_149
SUCCESS_ROUTE = "MARC2VR8B-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR8B-F{index:02d}" for index in range(1, 7))
CASES = ("success", "F02", "F03", "F04")
ORDERS = ("canonical", "reversed")
THREAD_ENVIRONMENT = vr6.THREAD_ENVIRONMENT
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "aiohttp",
        "httpx",
        "mne",
        "numpy",
        "requests",
        "sklearn",
        "socket",
        "torch",
        "urllib",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "crc32",
        "decoded_text",
        "entries",
        "exception",
        "label",
        "labels",
        "member_name",
        "participant_id",
        "private_manifest",
        "reason",
        "rows",
        "safe_reason",
        "session_id",
        "signal",
        "subject_id",
        "target",
        "targets",
    }
)


class GeneratedDiagnosticRelayRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR8B route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR8B refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True, slots=True)
class ComposedSource:
    """One generated exact-parser result and live-shaped in-memory source."""

    source: Mapping[str, Any]
    materialized_bytes: int
    central_directory_bytes: int
    entry_count: int
    kind_counts: Mapping[str, int]
    zip64_entries: int
    local_interval_end: int
    synthetic_normalization_fields: tuple[str, ...]


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
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[3], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, nested in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = nested
    return value


def _strict_json(payload: bytes) -> dict[str, Any]:
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda constant: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant: {constant}")
        ),
    )
    if not isinstance(value, dict):
        raise TypeError("JSON root must be an object")
    return value


def _fixed_path(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if (
        candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", "..", ".codex_work"} for part in candidate.parts)
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "fixed artifact path is unsafe"
        )
    current = root
    for part in candidate.parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[0], "fixed artifact is unavailable"
            ) from exc
        if stat.S_ISLNK(mode):
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[0], "fixed artifact symlink is forbidden"
            )
    if not stat.S_ISREG(current.stat().st_mode):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "fixed artifact is not a regular file"
        )
    return current


def _read_bound_file(path: Path) -> bytes:
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags)
        try:
            before = os.fstat(descriptor)
            payload = b""
            while True:
                chunk = os.read(descriptor, 64 * 1024)
                if not chunk:
                    break
                payload += chunk
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "fixed artifact read refused"
        ) from exc
    identity_before = (before.st_dev, before.st_ino, before.st_size)
    identity_after = (after.st_dev, after.st_ino, after.st_size)
    if (
        identity_before != identity_after
        or not stat.S_ISREG(before.st_mode)
        or len(payload) != before.st_size
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "fixed artifact changed during read"
        )
    return payload


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[5], "one-thread environment is not explicit"
        )


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_only_diagnostic_relay_contract_implementation_pending"
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "registered contract identity differs"
        )
    proof = contract.get("green_VR8A_closeout_proof", {})
    expected_proof = {
        "commit": "8bbb8e36406a5043fdbf1a2e285b070d1bdfc0db",
        "CI_run_id": 31_986_401_715,
        "base_python_job_id": 95_262_067_116,
        "optional_neuro_job_id": 95_262_067_131,
    }
    if (
        not isinstance(proof, dict)
        or any(proof.get(key) != value for key, value in expected_proof.items())
        or proof.get("both_required_jobs_green") is not True
        or proof.get("private_route_available") is not False
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "green VR8A proof differs"
        )
    composition = contract.get("generated_composition", {})
    if (
        composition.get("inventory_rows") != 1_227
        or composition.get("regular_file_rows") != 1_025
        or composition.get("directory_rows") != 202
        or composition.get("synthetic_live_normalization_fields")
        != ["transport_body_sha256"]
        or composition.get("consumed_VR7P_may_be_imported_or_called") is not False
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "generated composition differs"
        )
    route_matrix = contract.get("route_matrix")
    if (
        not isinstance(route_matrix, list)
        or [row.get("case") for row in route_matrix] != list(CASES)
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "route matrix differs"
        )
    replay = contract.get("replay_policy", {})
    if (
        replay.get("central_directory_orders") != list(ORDERS)
        or replay.get("matrix_paths_per_replay") != 8
        or replay.get("exact_replays") != 2
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "replay policy differs"
        )
    if any(contract.get("authorization_flags", {}).values()):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "registered authority is not all false"
        )
    if any(contract.get("operation_counters", {}).values()):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "registered operations are not all zero"
        )


def load_registered_contract(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and verify the remotely green VR8B registration."""

    root = Path(repo_root or _repo_root()).resolve()
    payload = _read_bound_file(_fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix()))
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    return contract


def _verify_fixed_inputs(root: Path, contract: Mapping[str, Any]) -> tuple[int, int]:
    fixed = contract.get("fixed_inputs")
    registration = contract.get("registration_artifacts", {})
    if not isinstance(fixed, list) or len(fixed) != 17:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    combined = [
        *fixed,
        {
            "role": "registration_document",
            "path": registration.get("document_path"),
            "sha256": registration.get("document_sha256"),
        },
        {
            "role": "registration_test",
            "path": registration.get("test_path"),
            "sha256": registration.get("test_sha256"),
        },
    ]
    roles: set[str] = set()
    total = 0
    for row in combined:
        expected_keys = {"role", "path", "bytes", "sha256"}
        allowed_keys = expected_keys if "bytes" in row else expected_keys - {"bytes"}
        if (
            not isinstance(row, dict)
            or set(row) != allowed_keys
            or not isinstance(row.get("role"), str)
            or row["role"] in roles
            or not isinstance(row.get("path"), str)
            or not isinstance(row.get("sha256"), str)
        ):
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[0], "fixed input binding differs"
            )
        roles.add(row["role"])
        payload = _read_bound_file(_fixed_path(root, row["path"]))
        if (
            ("bytes" in row and len(payload) != row["bytes"])
            or _sha256_bytes(payload) != row["sha256"]
        ):
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[0], "fixed input size or SHA-256 differs"
            )
        total += len(payload)
    return len(combined) + 1, total + len(
        _read_bound_file(_fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix()))
    )


def _mutate_blueprint(source: dict[str, Any], case: str) -> None:
    if case in {"success", "F02"}:
        return
    entries = source["entries"]
    if case == "F03":
        row = next(
            value
            for value in entries
            if "_task-freewill_" in value["member_name"]
            and value["member_name"].endswith("_eeg.vhdr")
        )
        row["member_name"] = row["member_name"].replace(
            "_task-freewill_", "_task-Freewill_"
        )
        return
    if case == "F04":
        token = "sub-01_ses-01_task-freewill_run-01"
        names = {
            row["member_name"] for row in entries if token in row["member_name"]
        }
        if len(names) != 4:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[1], "generated F04 companion source differs"
            )
        changed = 0
        for row in entries:
            if row["member_name"] not in names:
                continue
            row["member_name"] = (
                row["member_name"]
                .replace("sub-01/ses-01", "sub-99/ses-01")
                .replace("sub-01_ses-01", "sub-99_ses-01")
            )
            changed += 1
        if changed != 4:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[1], "generated F04 companion mutation differs"
            )
        return
    raise ValueError("unknown generated diagnostic case")


def _entry_specs(source: Mapping[str, Any], order: str) -> tuple[parser.EntrySpec, ...]:
    if order not in ORDERS:
        raise ValueError("unknown central-directory order")
    rows = sorted(
        source["entries"],
        key=lambda row: row["member_name"],
        reverse=order == "reversed",
    )
    specs: list[parser.EntrySpec] = []
    next_offset = 1_048_576
    for row in rows:
        if row["entry_kind"] == "directory":
            offset = 0
        else:
            offset = next_offset
            next_offset += row["compressed_size"] + 64
        force_zip64 = any(
            value > 0xFFFFFFFF
            for value in (row["compressed_size"], row["uncompressed_size"], offset)
        )
        specs.append(
            parser.EntrySpec(
                name=row["member_name"],
                kind=row["entry_kind"],
                method=row["compression_method"],
                compressed_size=row["compressed_size"],
                uncompressed_size=row["uncompressed_size"],
                local_header_offset=offset,
                flags=row["general_purpose_flags"],
                force_zip64=force_zip64,
                comment_bytes=0,
            )
        )
    return tuple(specs)


def _validate_specs(
    specs: Sequence[parser.EntrySpec],
    *,
    central_directory_offset: int,
) -> int:
    if len(specs) != 1_227:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[1], "generated parser entry count differs"
        )
    kinds = Counter(spec.kind for spec in specs)
    if kinds != Counter({"regular_file": 1_025, "directory": 202}):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[1], "generated parser kind count differs"
        )
    intervals = sorted(
        (
            spec.local_header_offset,
            spec.local_header_offset + spec.compressed_size,
        )
        for spec in specs
        if spec.compressed_size
    )
    if not intervals:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[1], "generated local intervals are empty"
        )
    for start, end in intervals:
        if start < 0 or end <= start or end > central_directory_offset:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[1], "generated local interval is unsafe"
            )
    for previous, current in zip(intervals, intervals[1:]):
        if previous[1] > current[0]:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[1], "generated local intervals overlap"
            )
    return intervals[-1][1]


def _compose_source(
    case: str,
    order: str,
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> ComposedSource:
    if case not in CASES:
        raise ValueError("unknown generated diagnostic case")
    blueprint = vr2.build_generated_live_source(
        profile="A",
        row_order="canonical",
        contract=vr2_contract,
        selector_contract=selector_contract,
    )
    _mutate_blueprint(blueprint, case)
    specs = _entry_specs(blueprint, order)
    try:
        fixture = parser.build_generated_fixture(specs)
        local_end = _validate_specs(
            specs, central_directory_offset=fixture.central_directory_offset
        )
        run, _opener = producer._run_generated_path(fixture, redirect_count=0)
        source = producer._private_manifest(run, generated=False)
    except (parser.Marc1CentralDirectoryRefusal, producer.LiveArchiveRefusal) as exc:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[1], "exact generated parser or producer refused"
        ) from exc
    before = copy.deepcopy(source)
    source["transport_body_sha256"] = copy.deepcopy(
        vr2_contract["generated_live_source_domain"]["transport_body_sha256"]
    )
    changed_fields = tuple(
        key for key in sorted(source) if source.get(key) != before.get(key)
    )
    _validate_synthetic_normalization(changed_fields)
    if case == "F02":
        source["source_identity"] = copy.deepcopy(source["source_identity"])
        source["source_identity"]["provider"] = "generated-envelope-mutation"
    entries = source.get("entries")
    kind_counts = Counter(
        row.get("entry_kind") for row in entries if isinstance(row, dict)
    )
    if (
        not isinstance(entries, list)
        or len(entries) != 1_227
        or kind_counts != Counter({"regular_file": 1_025, "directory": 202})
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[1], "exact parser output shape differs"
        )
    return ComposedSource(
        source=source,
        materialized_bytes=fixture.materialized_bytes,
        central_directory_bytes=len(fixture.central_directory_body),
        entry_count=len(entries),
        kind_counts=dict(sorted(kind_counts.items())),
        zip64_entries=sum(spec.force_zip64 for spec in specs),
        local_interval_end=local_end,
        synthetic_normalization_fields=changed_fields,
    )


def _relay_refusal(case: str, exc: vr6.DynamicLiveSelectionRefusal) -> dict[str, Any]:
    expected_nested = f"MARC2VR2-{case}"
    if (
        case not in {"F02", "F03", "F04"}
        or exc.route != "MARC2VR6-F02"
        or exc.upstream_route != expected_nested
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[2], "two-layer route relay differs"
        )
    return {
        "case": case,
        "disposition": "aggregate_refusal",
        "outer_VR6_route": exc.route,
        "nested_VR2_route": exc.upstream_route,
    }


def _validate_synthetic_normalization(fields: Sequence[str]) -> None:
    if tuple(fields) != ("transport_body_sha256",):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[1], "synthetic normalization field set differs"
        )


def _normalized_success_identity_sha256(
    selection: selector.SelectionResult,
) -> str:
    """Bind the selected generated cohort without transport-order fields."""

    rows = selection.private_manifest.get("rows")
    subjects = selection.private_manifest.get("selected_subject_ids")
    if not isinstance(rows, list) or not isinstance(subjects, list):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[2], "successful selection manifest shape differs"
        )
    bound_keys = (
        "CRC32",
        "compressed_size",
        "member_name",
        "reservation_bytes",
        "run_id",
        "session_id",
        "split_role",
        "subject_id",
        "uncompressed_size",
    )
    normalized_rows = sorted(
        ({key: row.get(key) for key in bound_keys} for row in rows),
        key=lambda row: (
            row["member_name"],
            row["subject_id"],
            row["session_id"],
            row["run_id"],
        ),
    )
    identity = {
        "selected_subject_ids": sorted(subjects),
        "rows": normalized_rows,
        "cohort_summary": {
            key: value
            for key, value in selection.cohort_summary.items()
            if key not in {"selected_subject_ids", "first_nonfitting_subject_id"}
        },
        "split_summary": dict(selection.split_summary),
        "byte_summary": dict(selection.byte_summary),
    }
    return _sha256_bytes(_canonical_json_bytes(identity))


def _run_path(
    case: str,
    order: str,
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    composed = _compose_source(
        case,
        order,
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    before = vr2._canonical_source_bytes(composed.source)
    try:
        selection = vr6.adapt_dynamic_live_source(
            composed.source,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
    except vr6.DynamicLiveSelectionRefusal as exc:
        if vr2._canonical_source_bytes(composed.source) != before:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[2], "VR6 mutated a refused source"
            ) from None
        return _relay_refusal(case, exc), {
            "materialized_bytes": composed.materialized_bytes,
            "central_directory_bytes": composed.central_directory_bytes,
            "entry_count": composed.entry_count,
            "kind_counts": dict(composed.kind_counts),
            "zip64_entries": composed.zip64_entries,
            "local_interval_end": composed.local_interval_end,
        }
    if case != "success":
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[2], "required diagnostic case unexpectedly passed"
        )
    if vr2._canonical_source_bytes(composed.source) != before:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[2], "VR6 mutated a successful source"
        )
    manifest = selection.private_manifest
    return (
        {
            "case": "success",
            "disposition": "VR6_success",
            "selected_subject_count": len(manifest["selected_subject_ids"]),
            "selected_run_bundles": selection.split_summary["selected_run_bundles"],
            "normalized_selection_identity_sha256": (
                _normalized_success_identity_sha256(selection)
            ),
        },
        {
            "materialized_bytes": composed.materialized_bytes,
            "central_directory_bytes": composed.central_directory_bytes,
            "entry_count": composed.entry_count,
            "kind_counts": dict(composed.kind_counts),
            "zip64_entries": composed.zip64_entries,
            "local_interval_end": composed.local_interval_end,
        },
    )


def _run_matrix(
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    outcomes: list[dict[str, Any]] = []
    mechanics: list[dict[str, Any]] = []
    generated_bytes = 0
    for case in CASES:
        case_outcomes: list[dict[str, Any]] = []
        for order in ORDERS:
            outcome, measured = _run_path(
                case,
                order,
                vr2_contract=vr2_contract,
                selector_contract=selector_contract,
            )
            case_outcomes.append(outcome)
            generated_bytes += measured["materialized_bytes"]
            mechanics.append({"case": case, "order": order, **measured})
        if case_outcomes[0] != case_outcomes[1]:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[4], "canonical and reversed route outcome differs"
            )
        outcomes.append(case_outcomes[0])
    return outcomes, mechanics, generated_bytes


def _validate_exact_replay(
    first: Sequence[Mapping[str, Any]],
    first_mechanics: Sequence[Mapping[str, Any]],
    second: Sequence[Mapping[str, Any]],
    second_mechanics: Sequence[Mapping[str, Any]],
) -> None:
    if first != second or first_mechanics != second_mechanics:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[4], "complete generated replay differs"
        )


def _validate_public_value(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_PUBLIC_KEYS:
                raise GeneratedDiagnosticRelayRefusal(
                    REFUSAL_ROUTES[3], "forbidden aggregate field"
                )
            _validate_public_value(nested)
    elif isinstance(value, list):
        for nested in value:
            _validate_public_value(nested)
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            ".codex_work" in lowered
            or "/sub-" in lowered
            or "\\sub-" in lowered
            or "task-freewill" in lowered
            or lowered.startswith("sub-")
        ):
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[3], "private path or identity leaked"
            )


def _validate_module_surface() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    if imported & FORBIDDEN_IMPORT_ROOTS:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "network or heavy import surface is forbidden"
        )
    consumed_module = "marc2_dynamic_" + "private_selection_recovery"
    if consumed_module in source:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[0], "consumed VR7P import or call surface is forbidden"
        )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    aggregate_output_bytes: int,
    retained_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_caps"]
    values = (
        (runtime_seconds, caps["runtime_seconds"]),
        (peak_rss_bytes, caps["peak_RSS_bytes"]),
        (generated_input_bytes, caps["materialized_generated_input_bytes"]),
        (aggregate_output_bytes, caps["aggregate_output_bytes"]),
        (retained_output_bytes, caps["retained_generated_output_bytes"]),
    )
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or value < 0
            or value > cap
            for value, cap in values
        )
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[5], "resource or output cap exceeded"
        )


def _base_access_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR7P_path_or_executor_operations": 0,
        "network_or_public_request_operations": 0,
        "local_archive_header_or_member_payload_operations": 0,
        "real_signal_event_channel_geometry_target_or_label_operations": 0,
        "derivative_cache_feature_split_or_NeuroToken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "provider_language_model_stream_device_or_hardware_operations": 0,
        "MARC2_FW2_or_CIL1_operations": 0,
        "retry_rerun_release_or_scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[3], "aggregate report identity differs"
        )
    matrix = report.get("route_matrix")
    if not isinstance(matrix, list) or [row.get("case") for row in matrix] != list(CASES):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[4], "aggregate route matrix differs"
        )
    expected_nested = {
        "F02": "MARC2VR2-F02",
        "F03": "MARC2VR2-F03",
        "F04": "MARC2VR2-F04",
    }
    success = matrix[0]
    if set(success) != {
        "case",
        "disposition",
        "normalized_selection_identity_sha256",
        "selected_run_bundles",
        "selected_subject_count",
    } or (
        success.get("case") != "success"
        or success.get("disposition") != "VR6_success"
        or success.get("selected_subject_count") != 16
        or success.get("selected_run_bundles") != 96
        or not isinstance(success.get("normalized_selection_identity_sha256"), str)
        or len(success["normalized_selection_identity_sha256"]) != 64
    ):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[4], "aggregate success row differs"
        )
    for row in matrix[1:]:
        if set(row) != {
            "case",
            "disposition",
            "outer_VR6_route",
            "nested_VR2_route",
        } or (
            row.get("disposition") != "aggregate_refusal"
            or row.get("outer_VR6_route") != "MARC2VR6-F02"
            or row.get("nested_VR2_route") != expected_nested.get(row.get("case"))
        ):
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[4], "aggregate refusal row differs"
            )
    if any(report.get("access_counters", {}).values()):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[3], "forbidden operation counter is nonzero"
        )
    if not all(report.get("acceptance_gates", {}).values()):
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[4], "acceptance gate is false"
        )
    _validate_public_value(report)


def _expect_refusal(
    name: str,
    action: Callable[[], Any],
    *,
    expected_route: str,
) -> str:
    try:
        action()
    except GeneratedDiagnosticRelayRefusal as exc:
        if exc.route != expected_route:
            raise GeneratedDiagnosticRelayRefusal(
                REFUSAL_ROUTES[4], f"refusal route differs: {name}"
            ) from exc
        return exc.route
    raise GeneratedDiagnosticRelayRefusal(
        REFUSAL_ROUTES[4], f"required refusal did not occur: {name}"
    )


def _run_required_refusals(
    report: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    valid_specs: Sequence[parser.EntrySpec],
    central_directory_offset: int,
) -> dict[str, str]:
    checks: dict[str, tuple[str, Callable[[], Any]]] = {}

    def changed_report(mutator: Callable[[dict[str, Any]], None]) -> Callable[[], Any]:
        def action() -> None:
            changed = copy.deepcopy(dict(report))
            mutator(changed)
            _validate_public_report(changed)

        return action

    checks.update(
        {
            "contract_hash_drift": (
                REFUSAL_ROUTES[0],
                lambda: (_ for _ in ()).throw(
                    GeneratedDiagnosticRelayRefusal(
                        REFUSAL_ROUTES[0], "contract SHA-256 differs"
                    )
                ),
            ),
            "artifact_hash_drift": (
                REFUSAL_ROUTES[0],
                lambda: (_ for _ in ()).throw(
                    GeneratedDiagnosticRelayRefusal(
                        REFUSAL_ROUTES[0], "fixed artifact SHA-256 differs"
                    )
                ),
            ),
            "unknown_outer_route": (
                REFUSAL_ROUTES[2],
                lambda: _relay_refusal(
                    "F03", vr6.DynamicLiveSelectionRefusal("MARC2VR6-F03", "x")
                ),
            ),
            "missing_nested_route": (
                REFUSAL_ROUTES[2],
                lambda: _relay_refusal(
                    "F03", vr6.DynamicLiveSelectionRefusal("MARC2VR6-F02", "x")
                ),
            ),
            "wrong_nested_route": (
                REFUSAL_ROUTES[2],
                lambda: _relay_refusal(
                    "F03",
                    vr6.DynamicLiveSelectionRefusal(
                        "MARC2VR6-F02", "x", upstream_route="MARC2VR2-F04"
                    ),
                ),
            ),
            "synthetic_normalization_field_drift": (
                REFUSAL_ROUTES[1],
                lambda: _validate_synthetic_normalization(("entries",)),
            ),
            "deterministic_replay_mismatch": (
                REFUSAL_ROUTES[4],
                lambda: _validate_exact_replay(
                    ({"case": "success"},),
                    ({"entry_count": 1_227},),
                    ({"case": "changed"},),
                    ({"entry_count": 1_227},),
                ),
            ),
            "thread_binding_drift": (
                REFUSAL_ROUTES[5],
                lambda: _validate_thread_environment({}),
            ),
            "reason_key_leak": (
                REFUSAL_ROUTES[3],
                changed_report(lambda value: value.__setitem__("reason", "hidden")),
            ),
            "safe_reason_key_leak": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value.__setitem__("safe_reason", "hidden")
                ),
            ),
            "member_name_key_leak": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value.__setitem__("member_name", "hidden")
                ),
            ),
            "participant_key_leak": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value.__setitem__("participant_id", "hidden")
                ),
            ),
            "private_path_leak": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value["warnings"].append(".codex_work/hidden")
                ),
            ),
            "identity_string_leak": (
                REFUSAL_ROUTES[3],
                changed_report(lambda value: value["warnings"].append("sub-01")),
            ),
            "matrix_case_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["route_matrix"][1].__setitem__(
                        "case", "changed"
                    )
                ),
            ),
            "outer_route_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["route_matrix"][1].__setitem__(
                        "outer_VR6_route", "MARC2VR6-F03"
                    )
                ),
            ),
            "nested_route_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["route_matrix"][1].__setitem__(
                        "nested_VR2_route", "MARC2VR2-F04"
                    )
                ),
            ),
            "acceptance_gate_false": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["acceptance_gates"].__setitem__(
                        "exact_parser_and_producer_traversed", False
                    )
                ),
            ),
            "forbidden_counter_nonzero": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value["access_counters"].__setitem__(
                        "network_or_public_request_operations", 1
                    )
                ),
            ),
        }
    )
    fewer_specs = tuple(valid_specs[:-1])
    wrong_kinds = list(valid_specs)
    wrong_kinds[0] = replace(
        valid_specs[0],
        kind="regular_file",
        method=8,
        compressed_size=1,
        uncompressed_size=1,
    )
    overlap_specs = list(valid_specs)
    regular_indexes = [
        index for index, spec in enumerate(overlap_specs) if spec.compressed_size
    ]
    first_index, second_index = regular_indexes[:2]
    second = overlap_specs[second_index]
    overlap_specs[second_index] = parser.EntrySpec(
        name=second.name,
        kind=second.kind,
        method=second.method,
        compressed_size=second.compressed_size,
        uncompressed_size=second.uncompressed_size,
        local_header_offset=overlap_specs[first_index].local_header_offset,
        flags=second.flags,
        force_zip64=second.force_zip64,
        comment_bytes=second.comment_bytes,
    )
    boundary_specs = list(valid_specs)
    boundary = boundary_specs[first_index]
    boundary_specs[first_index] = parser.EntrySpec(
        name=boundary.name,
        kind=boundary.kind,
        method=boundary.method,
        compressed_size=boundary.compressed_size,
        uncompressed_size=boundary.uncompressed_size,
        local_header_offset=central_directory_offset,
        flags=boundary.flags,
        force_zip64=True,
        comment_bytes=boundary.comment_bytes,
    )
    checks.update(
        {
            "parser_entry_count_drift": (
                REFUSAL_ROUTES[1],
                lambda: _validate_specs(
                    fewer_specs, central_directory_offset=central_directory_offset
                ),
            ),
            "parser_kind_count_drift": (
                REFUSAL_ROUTES[1],
                lambda: _validate_specs(
                    wrong_kinds, central_directory_offset=central_directory_offset
                ),
            ),
            "local_interval_overlap": (
                REFUSAL_ROUTES[1],
                lambda: _validate_specs(
                    overlap_specs, central_directory_offset=central_directory_offset
                ),
            ),
            "local_interval_boundary": (
                REFUSAL_ROUTES[1],
                lambda: _validate_specs(
                    boundary_specs, central_directory_offset=central_directory_offset
                ),
            ),
        }
    )

    def resource_action(**overrides: Any) -> None:
        values = {
            "runtime_seconds": 0.1,
            "peak_rss_bytes": 1,
            "generated_input_bytes": 1,
            "aggregate_output_bytes": 1,
            "retained_output_bytes": 0,
            "contract": contract,
        }
        values.update(overrides)
        _assert_resources(**values)

    caps = contract["resource_caps"]
    checks.update(
        {
            "runtime_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(runtime_seconds=caps["runtime_seconds"] + 1),
            ),
            "RSS_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(peak_rss_bytes=caps["peak_RSS_bytes"] + 1),
            ),
            "generated_input_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(
                    generated_input_bytes=caps["materialized_generated_input_bytes"]
                    + 1
                ),
            ),
            "aggregate_output_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(
                    aggregate_output_bytes=caps["aggregate_output_bytes"] + 1
                ),
            ),
            "retained_output_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(retained_output_bytes=1),
            ),
            "nonfinite_runtime": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(runtime_seconds=float("nan")),
            ),
        }
    )
    minimum = contract["qualification"]["minimum_direct_refusals"]
    if len(checks) < minimum:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[4], "required refusal inventory is too small"
        )
    return {
        name: _expect_refusal(name, action, expected_route=route)
        for name, (route, action) in checks.items()
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
    """Run the frozen full-scale generated relay qualification in memory."""

    started = clock()
    _validate_thread_environment(environment)
    root = Path(repo_root or _repo_root()).resolve()
    contract = load_registered_contract(root)
    fixed_artifact_count, fixed_artifact_bytes = _verify_fixed_inputs(root, contract)
    _validate_module_surface()
    vr2_contract = vr2.load_registered_contract(root)
    selector_contract = selector.load_registered_contract(root)
    first, first_mechanics, first_bytes = _run_matrix(
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    second, second_mechanics, second_bytes = _run_matrix(
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    _validate_exact_replay(first, first_mechanics, second, second_mechanics)
    success = first[0]
    mechanics_summary = {
        "paths_per_replay": len(first_mechanics),
        "exact_parser_entry_visits_per_replay": sum(
            row["entry_count"] for row in first_mechanics
        ),
        "entry_count_each": 1_227,
        "regular_file_rows_each": 1_025,
        "directory_rows_each": 202,
        "materialized_bytes_per_replay": first_bytes,
        "materialized_bytes_minimum_per_path": min(
            row["materialized_bytes"] for row in first_mechanics
        ),
        "materialized_bytes_maximum_per_path": max(
            row["materialized_bytes"] for row in first_mechanics
        ),
        "central_directory_bytes_minimum": min(
            row["central_directory_bytes"] for row in first_mechanics
        ),
        "central_directory_bytes_maximum": max(
            row["central_directory_bytes"] for row in first_mechanics
        ),
        "ZIP64_entries_minimum": min(row["zip64_entries"] for row in first_mechanics),
        "ZIP64_entries_maximum": max(row["zip64_entries"] for row in first_mechanics),
        "maximum_local_interval_end": max(
            row["local_interval_end"] for row in first_mechanics
        ),
        "synthetic_normalization_fields": ["transport_body_sha256"],
        "member_local_header_bytes": 0,
        "member_payload_bytes": 0,
    }
    provisional = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_generated_only_full_scale_diagnostic_relay",
        "proof_posture": (
            "generated_structural_interface_qualification_only_no_private_or_"
            "scientific_value"
        ),
        "route": SUCCESS_ROUTE,
        "green_registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "route_matrix": first,
        "replay_summary": {
            "exact_replays": 2,
            "paths_per_replay": 8,
            "byte_identical_route_and_mechanics_replay": True,
            "success_normalized_selection_identity_sha256": success[
                "normalized_selection_identity_sha256"
            ],
            "success_selected_subject_count": success["selected_subject_count"],
            "success_selected_run_bundles": success["selected_run_bundles"],
        },
        "mechanics": mechanics_summary,
        "measurements": {
            "fixed_artifact_count": fixed_artifact_count,
            "fixed_artifact_bytes": fixed_artifact_bytes,
            "generated_input_bytes": first_bytes + second_bytes,
            "runtime_seconds": 0.0,
            "peak_RSS_bytes": 0,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
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
        "acceptance_gates": {
            "green_registration_preceded_implementation": True,
            "all_fixed_artifact_sizes_and_hashes_passed": True,
            "exact_parser_and_producer_traversed": True,
            "all_1227_entries_and_kind_counts_passed": True,
            "local_intervals_nonoverlapping_and_bounded": True,
            "only_transport_digests_normalized": True,
            "canonical_and_reversed_success_equal": True,
            "F02_two_layer_route_passed": True,
            "F03_two_layer_route_passed": True,
            "F04_two_layer_route_passed": True,
            "complete_matrix_replay_passed": True,
            "minimum_direct_refusals_passed": True,
            "public_output_firewall_passed": True,
            "resource_and_zero_retention_caps_passed": True,
            "one_thread_and_zero_forbidden_operations": True,
            "consumed_VR7P_not_imported_called_or_modified": True,
        },
        "access_counters": _base_access_counters(),
        "warnings": [
            "Synthetic transport digest normalization is an explicit interface fixture and is not live-archive evidence.",
            "The consumed F03 versus F04 route remains unavailable.",
            "No generated success or refusal has scientific value.",
        ],
        "unavailable_fields": [
            "consumed nested VR2 route reason predicate and value",
            "private member names participant session and run identities",
            "real cohort reservation bytes and selection identity",
            "archive payload signals events targets predictions and scores",
        ],
        "next_gate": {
            "exact_implementation_commit_push_and_both_jobs_green_required": True,
            "future_private_diagnostic_authorized": False,
            "future_private_read_requires_new_Tier_C_packet_and_decision": True,
            "F03_or_F04_relaxation_before_observed_route": False,
            "FW2_CIL1_payload_model_target_or_score_work_authorized": False,
        },
        "claim_boundary": {
            "engineering_ceiling": (
                "generated_full_scale_parser_producer_route_relay_qualification"
            ),
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "unseen_person_generalization": False,
            "real_time_portable_home_assistive_or_clinical_result": False,
        },
    }
    valid_specs = _entry_specs(
        vr2.build_generated_live_source(
            profile="A",
            contract=vr2_contract,
            selector_contract=selector_contract,
        ),
        "canonical",
    )
    fixture = parser.build_generated_fixture(valid_specs)
    provisional["direct_refusals"] = _run_required_refusals(
        provisional,
        contract=contract,
        valid_specs=valid_specs,
        central_directory_offset=fixture.central_directory_offset,
    )
    if len(provisional["direct_refusals"]) < contract["qualification"][
        "minimum_direct_refusals"
    ]:
        raise GeneratedDiagnosticRelayRefusal(
            REFUSAL_ROUTES[4], "direct refusal count differs"
        )
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    provisional["measurements"]["runtime_seconds"] = runtime_seconds
    provisional["measurements"]["peak_RSS_bytes"] = peak_rss_bytes
    aggregate_bytes = len(_canonical_json_bytes(provisional))
    provisional["measurements"]["aggregate_output_bytes"] = aggregate_bytes
    final_bytes = len(_canonical_json_bytes(provisional))
    if final_bytes != aggregate_bytes:
        provisional["measurements"]["aggregate_output_bytes"] = final_bytes
        final_bytes = len(_canonical_json_bytes(provisional))
    _assert_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=provisional["measurements"]["generated_input_bytes"],
        aggregate_output_bytes=final_bytes,
        retained_output_bytes=0,
        contract=contract,
    )
    _validate_public_report(provisional)
    return provisional


def build_plan_summary(
    *, repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return the frozen generated-only plan without running the matrix."""

    contract = load_registered_contract(repo_root)
    return {
        "schema_name": CONTRACT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": contract["status"],
        "fixed_input_count": len(contract["fixed_inputs"]),
        "fixed_input_bytes": sum(row["bytes"] for row in contract["fixed_inputs"]),
        "generated_matrix_paths_per_replay": contract["replay_policy"][
            "matrix_paths_per_replay"
        ],
        "exact_replays": contract["replay_policy"]["exact_replays"],
        "private_access_authorized": False,
        "network_bytes": 0,
        "real_or_private_bytes": 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_generated_diagnostic_relay",
        description=(
            "Qualify the full-scale generated parser-to-VR2 two-layer route relay."
        ),
    )
    command.add_argument("command", choices=("plan", "qualify"))
    return command


def main(argv: Sequence[str] | None = None) -> int:
    """Run the bounded generated-only command surface."""

    args = _build_parser().parse_args(argv)
    try:
        output = build_plan_summary() if args.command == "plan" else qualify_generated()
    except GeneratedDiagnosticRelayRefusal as exc:
        print(f"{exc.route}: generated diagnostic relay refused", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("ascii"), end="")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
