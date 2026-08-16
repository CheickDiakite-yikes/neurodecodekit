"""Generated-only qualification of dynamic MARC2 live-selection invariants."""

from __future__ import annotations

import argparse
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
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import (
    marc2_source_validity_eligibility_repair as repair,
)


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR6"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_dynamic_live_selection_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_dynamic_live_selection_result"
PRIVATE_SCHEMA_NAME = (
    "neurodecodekit.marc2_dynamic_live_selection_private_manifest"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_dynamic_live_selection_contract.v0.json"
)
CONTRACT_SHA256 = "cadb9b512c0d072ced2bb4219f6c7f2ac962c230ecff7ff56841f00b824c0d58"
GREEN_REGISTRATION_COMMIT = "71d7cec63ff3c57122aec1ffa02fbec02de5f9dd"
GREEN_REGISTRATION_CI_RUN_ID = 31_974_405_202
GREEN_REGISTRATION_BASE_JOB_ID = 95_231_605_521
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_231_605_469
SUCCESS_ROUTE = "MARC2VR6-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR6-F{index:02d}" for index in range(1, 9))
UPSTREAM_ROUTES = tuple(f"MARC2VR2-F{index:02d}" for index in range(1, 9))
THREAD_ENVIRONMENT = repair.THREAD_ENVIRONMENT
LIVE_ROW_SOURCE_ID = "freewill_23_live_central_directory"
LIVE_PROOF_POSTURE = (
    "target_free_live_structural_selection_no_payload_or_scientific_value"
)
PROFILE_COUNTS = {
    "minimum_exact_cap": 12,
    "lower_middle": 14,
    "reference_middle": 16,
    "upper_middle": 18,
    "all_eligible_exact_cap": 19,
}
PROFILE_SELECTED_TOTALS = {
    "minimum_exact_cap": selector.RESERVATION_CAP_BYTES,
    "lower_middle": selector.RESERVATION_CAP_BYTES - 100_000_000,
    "reference_middle": selector.RESERVATION_CAP_BYTES - 50_000_000,
    "upper_middle": selector.RESERVATION_CAP_BYTES - 10_000_000,
    "all_eligible_exact_cap": selector.RESERVATION_CAP_BYTES,
}
FORBIDDEN_SCIENTIFIC_KEYS = frozenset(
    {
        "decoded_text",
        "label",
        "labels",
        "neural",
        "outcome",
        "prediction",
        "predictions",
        "quality",
        "score",
        "scores",
        "signal",
        "target",
        "targets",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "crc32",
        "local_header_offset",
        "member_name",
        "participant_id",
        "private_manifest",
        "private_path",
        "rows",
        "selected_subject_ids",
        "subject_id",
    }
)


class DynamicLiveSelectionRefusal(RuntimeError):
    """Fail closed while retaining at most one allowlisted upstream code."""

    def __init__(
        self,
        route: str,
        safe_reason: str,
        *,
        upstream_route: str | None = None,
    ) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR6 refusal route")
        if upstream_route is not None and upstream_route not in UPSTREAM_ROUTES:
            raise ValueError("unknown upstream VR2 route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason
        self.upstream_route = upstream_route


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
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[6], "JSON is not canonical"
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


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _strict_json(payload: bytes) -> dict[str, Any]:
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _fixed_file(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if (
        candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", "..", ".codex_work"} for part in candidate.parts)
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "fixed artifact path differs"
        )
    current = root
    for part in candidate.parts:
        current = current / part
        try:
            info = current.lstat()
        except OSError as exc:
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[0], "fixed artifact is unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[0], "fixed artifact path contains a symlink"
            )
    if not stat.S_ISREG(current.lstat().st_mode):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "fixed artifact is not a regular file"
        )
    return current


def _read_once(path: Path, *, cap: int) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "fixed artifact open failed"
        ) from exc
    chunks: list[bytes] = []
    total = 0
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[0], "fixed artifact type or size differs"
            )
        while True:
            chunk = os.read(descriptor, min(65_536, cap + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > cap:
                raise DynamicLiveSelectionRefusal(
                    REFUSAL_ROUTES[0], "fixed artifact exceeds cap"
                )
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if (
        before.st_dev != after.st_dev
        or before.st_ino != after.st_ino
        or before.st_size != after.st_size
        or total != before.st_size
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "fixed artifact identity changed"
        )
    return b"".join(chunks)


def _load_contract(root: Path) -> tuple[dict[str, Any], bytes]:
    payload = _read_once(
        _fixed_file(root, CONTRACT_RELATIVE_PATH.as_posix()), cap=1024**2
    )
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    return contract, payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    proof = contract.get("upstream_green_proof", {})
    policy = contract.get("dynamic_selection_policy", {})
    replay = contract.get("generated_replay_policy", {})
    gate = contract.get("implementation_gate", {})
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_only_dynamic_selection_repair_implementation_pending"
        or proof.get("closeout_commit")
        != "0c347adea910e42ef479e4f95e22603e3366683c"
        or proof.get("closeout_CI_run_id") != 31_973_927_757
        or proof.get("both_closeout_jobs_green") is not True
        or proof.get("observed_private_nested_route_available") is not False
        or policy.get("minimum_selected_subjects") != selector.MINIMUM_SUBJECTS
        or policy.get("maximum_selected_subjects") != selector.MAXIMUM_SUBJECTS
        or policy.get("reservation_cap_bytes") != selector.RESERVATION_CAP_BYTES
        or policy.get("generated_expected_selection_object_allowed") is not False
        or replay.get("success_paths") != 10
        or replay.get("minimum_direct_mutations", 0) < 24
        or gate.get("execute_command_allowed") is not False
        or gate.get("future_private_read_requires_new_Tier_C_packet_and_decision")
        is not True
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "contract identity or policy differs"
        )
    profiles = contract.get("generated_success_profiles", [])
    if (
        not isinstance(profiles, list)
        or [row.get("profile") for row in profiles] != list(PROFILE_COUNTS)
        or [row.get("expected_selected_subjects") for row in profiles]
        != list(PROFILE_COUNTS.values())
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "generated profile matrix differs"
        )


def _verify_fixed_inputs(
    root: Path, contract: Mapping[str, Any]
) -> tuple[int, int]:
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 7:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    roles: set[str] = set()
    total = 0
    for row in rows:
        if (
            not isinstance(row, dict)
            or set(row) != {"role", "path", "sha256"}
            or not isinstance(row["role"], str)
            or row["role"] in roles
        ):
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[0], "fixed input binding differs"
            )
        roles.add(row["role"])
        payload = _read_once(_fixed_file(root, row["path"]), cap=2 * 1024**2)
        if _sha256_bytes(payload) != row["sha256"]:
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[0], "fixed input SHA-256 differs"
            )
        total += len(payload)
    return len(rows), total


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[7], "one-thread environment is not explicit"
        )


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _mutable_ids(value: Any) -> set[int]:
    seen: set[int] = set()

    def walk(nested: Any) -> None:
        if isinstance(nested, dict):
            seen.add(id(nested))
            for item in nested.values():
                walk(item)
        elif isinstance(nested, list):
            seen.add(id(nested))
            for item in nested:
                walk(item)

    walk(value)
    return seen


def _assert_no_alias(source: Any, result: Any) -> None:
    if _mutable_ids(source) & _mutable_ids(result):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[6], "selection aliases the source"
        )


def _walk_scientific_firewall(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_SCIENTIFIC_KEYS):
                raise DynamicLiveSelectionRefusal(
                    REFUSAL_ROUTES[5], "forbidden scientific field"
                )
            _walk_scientific_firewall(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_scientific_firewall(nested)


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in FORBIDDEN_PUBLIC_KEYS:
                raise DynamicLiveSelectionRefusal(
                    REFUSAL_ROUTES[6], "private field leaked into aggregate"
                )
            _walk_public(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested)
    elif isinstance(value, str) and (
        ".codex_work" in value or value.startswith("sub-") or "_eeg." in value
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[6], "private value leaked into aggregate"
        )


def _subject_rows(source: Mapping[str, Any], subject: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in source["entries"]:
        match = selector._core_match(row["member_name"])
        if (
            match is not None
            and match.group("subject") == subject
            and match.group("session") in {"ses-01", "ses-02"}
            and int(match.group("run")) <= 3
        ):
            rows.append(row)
    rows.sort(key=lambda row: row["member_name"])
    if len(rows) != selector.EXPECTED_CANDIDATE_CORE_MEMBERS // 19:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[2], "generated subject companion count differs"
        )
    return rows


def _set_subject_reservation(
    source: dict[str, Any], subject: str, target_bytes: int
) -> None:
    rows = _subject_rows(source, subject)
    overhead = sum(
        30 + len(row["member_name"].encode("utf-8")) + 65_535 for row in rows
    )
    compressed_total = target_bytes - overhead
    if compressed_total < len(rows):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[4], "generated reservation target is too small"
        )
    quotient, remainder = divmod(compressed_total, len(rows))
    for index, row in enumerate(rows):
        compressed = quotient + (1 if index < remainder else 0)
        row["compressed_size"] = compressed
        row["uncompressed_size"] = compressed + 128


def build_generated_profile(
    profile: str,
    row_order: str,
    *,
    vr2_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one deterministic live-shaped reservation boundary."""

    if profile not in PROFILE_COUNTS:
        raise ValueError("unknown MARC2-VR6 generated profile")
    if row_order not in {"canonical", "reversed"}:
        raise ValueError("unknown generated row order")
    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    source = vr2.build_generated_live_source(
        profile="A",
        row_order="canonical",
        contract=registered_vr2,
        selector_contract=frozen_selector,
    )
    rank = selector._validate_rank(frozen_selector)
    count = PROFILE_COUNTS[profile]
    selected_total = PROFILE_SELECTED_TOTALS[profile]
    quotient, remainder = divmod(selected_total, count)
    selected_targets = [
        quotient + (1 if index < remainder else 0) for index in range(count)
    ]
    for subject, target in zip(rank[:count], selected_targets, strict=True):
        _set_subject_reservation(source, subject, target)
    if count < len(rank):
        remaining = selector.RESERVATION_CAP_BYTES - selected_total
        nonfit_target = max(2_000_000, remaining + 1)
        for subject in rank[count:]:
            _set_subject_reservation(source, subject, nonfit_target)
    source["entries"].sort(key=lambda row: row["member_name"])
    if row_order == "reversed":
        source["entries"].reverse()
    return source


def _preserve_upstream_route(route: str) -> DynamicLiveSelectionRefusal:
    if route not in UPSTREAM_ROUTES:
        return DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[1], "unknown upstream route refused"
        )
    return DynamicLiveSelectionRefusal(
        REFUSAL_ROUTES[1],
        "upstream VR2 validation refused",
        upstream_route=route,
    )


def _validate_dynamic_selection(
    selection: selector.SelectionResult,
    *,
    eligible_keys: set[repair.RunKey],
    selector_contract: Mapping[str, Any],
) -> None:
    policy_rank = selector._validate_rank(selector_contract)
    cohort = selection.cohort_summary
    split = selection.split_summary
    byte = selection.byte_summary
    subjects = cohort.get("selected_subject_ids")
    if not isinstance(subjects, list):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[2], "selected rank prefix is unavailable"
        )
    count = len(subjects)
    if (
        count < selector.MINIMUM_SUBJECTS
        or count > selector.MAXIMUM_SUBJECTS
        or subjects != policy_rank[:count]
        or cohort.get("selected_subjects") != count
        or cohort.get("eligible_subjects") != selector.EXPECTED_ELIGIBLE_SUBJECTS
        or cohort.get("minimum_subjects") != selector.MINIMUM_SUBJECTS
        or cohort.get("maximum_subjects") != selector.MAXIMUM_SUBJECTS
        or cohort.get("selection_is_maximal_contiguous_rank_prefix") is not True
        or cohort.get("selection_was_target_quality_and_outcome_free") is not True
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[2], "rank prefix or participant bounds differ"
        )
    next_subject = cohort.get("first_nonfitting_subject_id")
    examined = cohort.get("candidate_subjects_examined")
    next_reservation = byte.get("first_nonfitting_subject_reservation_bytes")
    if count == selector.MAXIMUM_SUBJECTS:
        if next_subject is not None or next_reservation is not None or examined != count:
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[2], "all-subject completion boundary differs"
            )
    elif (
        next_subject != policy_rank[count]
        or examined != count + 1
        or isinstance(next_reservation, bool)
        or not isinstance(next_reservation, int)
        or next_reservation <= byte.get("remaining_reservation_bytes", -1)
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[2], "next-subject maximality boundary differs"
        )
    if (
        split.get("fit_session") != "ses-01"
        or split.get("heldout_session") != "ses-02"
        or split.get("fit_run_bundles") != count * 3
        or split.get("heldout_run_bundles") != count * 3
        or split.get("selected_run_bundles") != count * 6
        or split.get("selected_core_members") != count * 24
        or split.get("fit_heldout_overlap") != 0
        or split.get("row_random_split_used") is not False
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[3], "split bundle or member arithmetic differs"
        )
    selected_bytes = byte.get("selected_reservation_bytes")
    remaining = byte.get("remaining_reservation_bytes")
    if (
        isinstance(selected_bytes, bool)
        or not isinstance(selected_bytes, int)
        or selected_bytes < 0
        or selected_bytes > selector.RESERVATION_CAP_BYTES
        or byte.get("reservation_cap_bytes") != selector.RESERVATION_CAP_BYTES
        or remaining != selector.RESERVATION_CAP_BYTES - selected_bytes
        or byte.get("fallback_or_budget_increase_used") is not False
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[4], "reservation cap or remaining bytes differ"
        )
    rows = selection.private_manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != count * 24:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[3], "private structural row count differs"
        )
    _walk_scientific_firewall(rows)
    row_subjects: Counter[str] = Counter()
    split_rows: Counter[tuple[str, str]] = Counter()
    bundle_suffixes: dict[tuple[str, str, int], set[str]] = {}
    names: set[str] = set()
    measured_reservation = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(selector.PRIVATE_ROW_FIELDS):
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[3], "private structural row fields differ"
            )
        subject = row.get("subject_id")
        split_role = row.get("split_role")
        session = row.get("session_id")
        run_id = row.get("run_id")
        name = row.get("member_name")
        match = selector._core_match(name) if isinstance(name, str) else None
        expected_reservation = (
            int(row.get("compressed_size", -1))
            + 30
            + len(name.encode("utf-8"))
            + 65_535
            if isinstance(name, str)
            else -1
        )
        if (
            subject not in subjects
            or split_role not in {"fit", "heldout"}
            or (split_role == "fit" and session != "ses-01")
            or (split_role == "heldout" and session != "ses-02")
            or not isinstance(name, str)
            or name in names
            or match is None
            or match.group("subject") != subject
            or match.group("session") != session
            or run_id != f"run-{int(match.group('run')):02d}"
            or int(match.group("run")) not in {1, 2, 3}
            or row.get("reservation_bytes") != expected_reservation
        ):
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[3], "private row identity or split differs"
            )
        names.add(name)
        row_subjects[subject] += 1
        split_rows[(subject, split_role)] += 1
        bundle = (subject, session, int(match.group("run")))
        bundle_suffixes.setdefault(bundle, set()).add(match.group("suffix"))
        measured_reservation += expected_reservation
    if any(row_subjects[subject] != 24 for subject in subjects) or any(
        split_rows[(subject, role)] != 12
        for subject in subjects
        for role in ("fit", "heldout")
    ) or any(
        suffixes != set(selector.REQUIRED_SUFFIXES)
        for suffixes in bundle_suffixes.values()
    ) or len(bundle_suffixes) != count * 6:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[3], "per-subject split row arithmetic differs"
        )
    if measured_reservation != selected_bytes:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[4], "row reservation sum differs"
        )
    try:
        repair._assert_no_ineligible_candidates(selection, eligible_keys)
    except repair.SourceValidityEligibilityRefusal as exc:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[2], "ineligible run entered selection"
        ) from exc


def _selection_identity(
    selection: selector.SelectionResult,
    *,
    source_sha256: str,
    selected_subject_ids: Sequence[str],
) -> dict[str, Any]:
    return {
        "selected_subject_ids": list(selected_subject_ids),
        "selected_subjects": len(selected_subject_ids),
        "fit_session": "ses-01",
        "heldout_session": "ses-02",
        "selected_run_bundles": selection.split_summary["selected_run_bundles"],
        "selected_core_members": selection.split_summary["selected_core_members"],
        "selected_reservation_bytes": selection.byte_summary[
            "selected_reservation_bytes"
        ],
        "reservation_cap_bytes": selector.RESERVATION_CAP_BYTES,
        "live_source_canonical_sha256": source_sha256,
    }


def _normalize_live_selection(
    selection: selector.SelectionResult,
    *,
    source: Mapping[str, Any],
    source_sha256: str,
) -> selector.SelectionResult:
    rows: list[dict[str, Any]] = []
    for original in selection.private_manifest["rows"]:
        row = copy.deepcopy(dict(original))
        row["source_id"] = LIVE_ROW_SOURCE_ID
        row["source_hashes"] = {
            "live_source_canonical_sha256": source_sha256,
            "selector_contract_sha256": selector.CONTRACT_SHA256,
            "dynamic_selection_contract_sha256": CONTRACT_SHA256,
        }
        rows.append(row)
    subjects = list(selection.cohort_summary["selected_subject_ids"])
    identity = _selection_identity(
        selection,
        source_sha256=source_sha256,
        selected_subject_ids=subjects,
    )
    identity_sha256 = _sha256_bytes(_canonical_json_bytes(identity))
    private_manifest = {
        "schema_name": PRIVATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "proof_posture": LIVE_PROOF_POSTURE,
        "source_identity": copy.deepcopy(source["source_identity"]),
        "source_proof_posture": source["proof_posture"],
        "live_source_canonical_sha256": source_sha256,
        "selector_contract_sha256": selector.CONTRACT_SHA256,
        "dynamic_selection_contract_sha256": CONTRACT_SHA256,
        "selection_identity_sha256": identity_sha256,
        "selected_subject_ids": subjects,
        "rows": rows,
    }
    hashes = {
        "live_source_canonical_sha256": source_sha256,
        "selector_contract_sha256": selector.CONTRACT_SHA256,
        "dynamic_selection_contract_sha256": CONTRACT_SHA256,
        "selection_identity_sha256": identity_sha256,
        "private_selection_manifest_sha256": _sha256_bytes(
            _canonical_json_bytes(private_manifest)
        ),
    }
    normalized = selector.SelectionResult(
        private_manifest=private_manifest,
        cohort_summary=copy.deepcopy(dict(selection.cohort_summary)),
        split_summary=copy.deepcopy(dict(selection.split_summary)),
        byte_summary=copy.deepcopy(dict(selection.byte_summary)),
        selection_hashes=hashes,
    )
    _assert_no_alias(source, normalized.private_manifest)
    _validate_live_semantics(normalized, source_sha256=source_sha256)
    return normalized


def _validate_live_semantics(
    selection: selector.SelectionResult, *, source_sha256: str
) -> None:
    manifest = selection.private_manifest
    expected_top = {
        "schema_name",
        "schema_version",
        "proof_posture",
        "source_identity",
        "source_proof_posture",
        "live_source_canonical_sha256",
        "selector_contract_sha256",
        "dynamic_selection_contract_sha256",
        "selection_identity_sha256",
        "selected_subject_ids",
        "rows",
    }
    if (
        set(manifest) != expected_top
        or manifest.get("schema_name") != PRIVATE_SCHEMA_NAME
        or manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("proof_posture") != LIVE_PROOF_POSTURE
        or manifest.get("live_source_canonical_sha256") != source_sha256
        or manifest.get("selector_contract_sha256") != selector.CONTRACT_SHA256
        or manifest.get("dynamic_selection_contract_sha256") != CONTRACT_SHA256
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[5], "live private manifest semantics differ"
        )
    expected_hash_keys = {
        "live_source_canonical_sha256",
        "selector_contract_sha256",
        "dynamic_selection_contract_sha256",
    }
    for row in manifest["rows"]:
        if (
            row.get("source_id") != LIVE_ROW_SOURCE_ID
            or set(row.get("source_hashes", {})) != expected_hash_keys
            or row["source_hashes"].get("live_source_canonical_sha256")
            != source_sha256
        ):
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[5], "live row source semantics differ"
            )
    _walk_scientific_firewall(manifest)
    expected_identity_hash = manifest.get("selection_identity_sha256")
    recomputed_identity_hash = _sha256_bytes(
        _canonical_json_bytes(
            _selection_identity(
                selection,
                source_sha256=source_sha256,
                selected_subject_ids=manifest.get("selected_subject_ids", []),
            )
        )
    )
    recomputed_manifest_hash = _sha256_bytes(_canonical_json_bytes(manifest))
    if (
        expected_identity_hash != recomputed_identity_hash
        or
        selection.selection_hashes.get("selection_identity_sha256")
        != expected_identity_hash
        or selection.selection_hashes.get("live_source_canonical_sha256")
        != source_sha256
        or selection.selection_hashes.get("private_selection_manifest_sha256")
        != recomputed_manifest_hash
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[4], "measured selection identity differs"
        )


def adapt_dynamic_live_source(
    source: Mapping[str, Any],
    *,
    vr2_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> selector.SelectionResult:
    """Validate the complete source, then select by dynamic invariants."""

    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    source_before = vr2._canonical_source_bytes(source)
    try:
        filtered, _counts, _labels, source_sha256 = vr2.validate_live_domain_source(
            source, contract=registered_vr2
        )
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise _preserve_upstream_route(exc.route) from None
    if vr2._canonical_source_bytes(source) != source_before:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[6], "source changed during validation"
        )
    try:
        selection = repair._select_from_filtered(
            filtered, source_sha256, frozen_selector
        )
    except repair.SourceValidityEligibilityRefusal as exc:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[2], "dynamic prefix selector refused"
        ) from exc
    if vr2._canonical_source_bytes(source) != source_before:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[6], "source changed during selection"
        )
    _validate_dynamic_selection(
        selection,
        eligible_keys=set(filtered),
        selector_contract=frozen_selector,
    )
    normalized = _normalize_live_selection(
        selection, source=source, source_sha256=source_sha256
    )
    _assert_no_alias(source, normalized.private_manifest)
    return normalized


def _expect_refusal(
    name: str,
    expected_route: str,
    action: Callable[[], Any],
) -> str:
    try:
        action()
    except DynamicLiveSelectionRefusal as exc:
        if exc.route != expected_route:
            raise DynamicLiveSelectionRefusal(
                REFUSAL_ROUTES[6], f"mutation route differs: {name}"
            ) from exc
        return exc.route
    raise DynamicLiveSelectionRefusal(
        REFUSAL_ROUTES[6], f"mutation was accepted: {name}"
    )


def _mutate_selection(
    selection: selector.SelectionResult,
    mutation: Callable[[selector.SelectionResult], None],
) -> selector.SelectionResult:
    changed = copy.deepcopy(selection)
    mutation(changed)
    return changed


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
        (generated_input_bytes, caps["generated_input_bytes"]),
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
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[7], "resource or output cap exceeded"
        )


def _run_mutation_matrix(
    *,
    contract: Mapping[str, Any],
    source: Mapping[str, Any],
    raw: selector.SelectionResult,
    normalized: selector.SelectionResult,
    eligible_keys: set[repair.RunKey],
    selector_contract: Mapping[str, Any],
) -> dict[str, Any]:
    refusals: list[tuple[str, str]] = []

    def record(name: str, route: str, action: Callable[[], Any]) -> None:
        refusals.append((name, _expect_refusal(name, route, action)))

    changed_contract = copy.deepcopy(dict(contract))
    changed_contract["status"] = "changed"
    record(
        "contract_identity_changed",
        REFUSAL_ROUTES[0],
        lambda: _verify_contract_mapping(changed_contract),
    )
    changed_contract = copy.deepcopy(dict(contract))
    changed_contract["fixed_inputs"][0]["sha256"] = "0" * 64
    record(
        "fixed_input_binding_changed",
        REFUSAL_ROUTES[0],
        lambda: _verify_fixed_inputs(_repo_root(), changed_contract),
    )
    changed_source = copy.deepcopy(dict(source))
    changed_source["unknown"] = True
    record(
        "source_unknown_field",
        REFUSAL_ROUTES[1],
        lambda: adapt_dynamic_live_source(changed_source),
    )
    changed_source = copy.deepcopy(dict(source))
    changed_source["source_identity"]["file_id"] += 1
    record(
        "source_identity_changed",
        REFUSAL_ROUTES[1],
        lambda: adapt_dynamic_live_source(changed_source),
    )
    record(
        "unknown_upstream_route",
        REFUSAL_ROUTES[1],
        lambda: (_ for _ in ()).throw(_preserve_upstream_route("UNKNOWN")),
    )
    record(
        "source_alias",
        REFUSAL_ROUTES[6],
        lambda: _assert_no_alias(source, source),
    )

    def validate(changed: selector.SelectionResult) -> None:
        _validate_dynamic_selection(
            changed,
            eligible_keys=eligible_keys,
            selector_contract=selector_contract,
        )

    record(
        "selected_below_minimum",
        REFUSAL_ROUTES[2],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.cohort_summary.__setitem__(
                    "selected_subject_ids",
                    value.cohort_summary["selected_subject_ids"][:11],
                ),
            )
        ),
    )
    record(
        "selected_above_maximum",
        REFUSAL_ROUTES[2],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.cohort_summary["selected_subject_ids"].append(
                    "sub-99"
                ),
            )
        ),
    )
    record(
        "rank_prefix_reordered",
        REFUSAL_ROUTES[2],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.cohort_summary["selected_subject_ids"].reverse(),
            )
        ),
    )
    record(
        "selected_count_changed",
        REFUSAL_ROUTES[2],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.cohort_summary.__setitem__(
                    "selected_subjects", 13
                ),
            )
        ),
    )
    record(
        "next_subject_changed",
        REFUSAL_ROUTES[2],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.cohort_summary.__setitem__(
                    "first_nonfitting_subject_id", "sub-99"
                ),
            )
        ),
    )
    record(
        "examined_count_changed",
        REFUSAL_ROUTES[2],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.cohort_summary.__setitem__(
                    "candidate_subjects_examined", 99
                ),
            )
        ),
    )
    record(
        "next_reservation_not_overflowing",
        REFUSAL_ROUTES[2],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.byte_summary.__setitem__(
                    "first_nonfitting_subject_reservation_bytes",
                    value.byte_summary["remaining_reservation_bytes"],
                ),
            )
        ),
    )
    for name, key in (
        ("fit_bundle_count_changed", "fit_run_bundles"),
        ("heldout_bundle_count_changed", "heldout_run_bundles"),
        ("total_bundle_count_changed", "selected_run_bundles"),
        ("core_member_count_changed", "selected_core_members"),
        ("fit_heldout_overlap_changed", "fit_heldout_overlap"),
    ):
        record(
            name,
            REFUSAL_ROUTES[3],
            lambda key=key: validate(
                _mutate_selection(
                    raw,
                    lambda value: value.split_summary.__setitem__(
                        key, value.split_summary[key] + 1
                    ),
                )
            ),
        )
    record(
        "row_random_split_enabled",
        REFUSAL_ROUTES[3],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.split_summary.__setitem__(
                    "row_random_split_used", True
                ),
            )
        ),
    )
    record(
        "reservation_over_cap",
        REFUSAL_ROUTES[4],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.byte_summary.__setitem__(
                    "selected_reservation_bytes",
                    selector.RESERVATION_CAP_BYTES + 1,
                ),
            )
        ),
    )
    record(
        "remaining_bytes_changed",
        REFUSAL_ROUTES[4],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.byte_summary.__setitem__(
                    "remaining_reservation_bytes",
                    value.byte_summary["remaining_reservation_bytes"] + 1,
                ),
            )
        ),
    )
    record(
        "reservation_cap_changed",
        REFUSAL_ROUTES[4],
        lambda: validate(
            _mutate_selection(
                raw,
                lambda value: value.byte_summary.__setitem__(
                    "reservation_cap_bytes", selector.RESERVATION_CAP_BYTES + 1
                ),
            )
        ),
    )

    def live(changed: selector.SelectionResult) -> None:
        _validate_live_semantics(
            changed,
            source_sha256=normalized.selection_hashes[
                "live_source_canonical_sha256"
            ],
        )

    record(
        "live_row_source_id_changed",
        REFUSAL_ROUTES[5],
        lambda: live(
            _mutate_selection(
                normalized,
                lambda value: value.private_manifest["rows"][0].__setitem__(
                    "source_id", "freewill_23_generated"
                ),
            )
        ),
    )
    record(
        "live_proof_posture_changed",
        REFUSAL_ROUTES[5],
        lambda: live(
            _mutate_selection(
                normalized,
                lambda value: value.private_manifest.__setitem__(
                    "proof_posture", "generated_fixture_selection_only"
                ),
            )
        ),
    )
    record(
        "live_source_hash_key_changed",
        REFUSAL_ROUTES[5],
        lambda: live(
            _mutate_selection(
                normalized,
                lambda value: value.private_manifest["rows"][0][
                    "source_hashes"
                ].__setitem__("generated_inventory_sha256", "0" * 64),
            )
        ),
    )
    record(
        "target_field_added",
        REFUSAL_ROUTES[5],
        lambda: live(
            _mutate_selection(
                normalized,
                lambda value: value.private_manifest["rows"][0].__setitem__(
                    "target", "forbidden"
                ),
            )
        ),
    )
    record(
        "selection_identity_changed",
        REFUSAL_ROUTES[4],
        lambda: live(
            _mutate_selection(
                normalized,
                lambda value: value.selection_hashes.__setitem__(
                    "selection_identity_sha256", "0" * 64
                ),
            )
        ),
    )
    record(
        "private_aggregate_field",
        REFUSAL_ROUTES[6],
        lambda: _walk_public({"rows": []}),
    )
    record(
        "thread_environment_changed",
        REFUSAL_ROUTES[7],
        lambda: _validate_thread_environment({}),
    )
    caps = contract["resource_caps"]
    for name, kwargs in (
        ("runtime_cap", {"runtime_seconds": caps["runtime_seconds"] + 1}),
        ("RSS_cap", {"peak_rss_bytes": caps["peak_RSS_bytes"] + 1}),
        (
            "generated_input_cap",
            {"generated_input_bytes": caps["generated_input_bytes"] + 1},
        ),
        (
            "aggregate_output_cap",
            {"aggregate_output_bytes": caps["aggregate_output_bytes"] + 1},
        ),
        ("retained_output_cap", {"retained_output_bytes": 1}),
    ):
        baseline = {
            "runtime_seconds": 0.0,
            "peak_rss_bytes": 0,
            "generated_input_bytes": 0,
            "aggregate_output_bytes": 0,
            "retained_output_bytes": 0,
            "contract": contract,
        }
        baseline.update(kwargs)
        record(
            name,
            REFUSAL_ROUTES[7],
            lambda baseline=baseline: _assert_resources(**baseline),
        )
    return {
        "direct_mutations_passed": len(refusals),
        "route_counts": dict(sorted(Counter(route for _name, route in refusals).items())),
        "mutation_names": [name for name, _route in refusals],
    }


def _raw_selection_for_mutations(
    source: Mapping[str, Any],
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[selector.SelectionResult, set[repair.RunKey], str]:
    filtered, _counts, _labels, source_sha256 = vr2.validate_live_domain_source(
        source, contract=vr2_contract
    )
    raw = repair._select_from_filtered(filtered, source_sha256, selector_contract)
    _validate_dynamic_selection(
        raw,
        eligible_keys=set(filtered),
        selector_contract=selector_contract,
    )
    return raw, set(filtered), source_sha256


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the frozen ten-path generated dynamic-selection qualification."""

    _validate_thread_environment()
    started = clock()
    root = Path(repo_root or _repo_root()).resolve()
    contract, contract_payload = _load_contract(root)
    fixed_count, fixed_bytes = _verify_fixed_inputs(root, contract)
    registered_vr2 = vr2.load_registered_contract(root)
    frozen_selector = selector.load_registered_contract(root)
    profile_rows: list[dict[str, Any]] = []
    generated_input_bytes = 0
    profile_hashes: dict[str, set[str]] = {name: set() for name in PROFILE_COUNTS}
    profile_source_hashes: dict[str, set[str]] = {
        name: set() for name in PROFILE_COUNTS
    }
    first_source: dict[str, Any] | None = None
    first_normalized: selector.SelectionResult | None = None
    for profile, expected_count in PROFILE_COUNTS.items():
        for row_order in ("canonical", "reversed"):
            source = build_generated_profile(
                profile,
                row_order,
                vr2_contract=registered_vr2,
                selector_contract=frozen_selector,
            )
            generated_input_bytes += len(vr2._canonical_source_bytes(source))
            normalized = adapt_dynamic_live_source(
                source,
                vr2_contract=registered_vr2,
                selector_contract=frozen_selector,
            )
            if normalized.cohort_summary["selected_subjects"] != expected_count:
                raise DynamicLiveSelectionRefusal(
                    REFUSAL_ROUTES[6], "generated profile selected count differs"
                )
            selection_hash = normalized.selection_hashes[
                "selection_identity_sha256"
            ]
            source_hash = normalized.selection_hashes[
                "live_source_canonical_sha256"
            ]
            profile_hashes[profile].add(selection_hash)
            profile_source_hashes[profile].add(source_hash)
            profile_rows.append(
                {
                    "profile": profile,
                    "row_order": row_order,
                    "selected_subjects": expected_count,
                    "selected_run_bundles": normalized.split_summary[
                        "selected_run_bundles"
                    ],
                    "selected_core_members": normalized.split_summary[
                        "selected_core_members"
                    ],
                    "selected_reservation_bytes": normalized.byte_summary[
                        "selected_reservation_bytes"
                    ],
                    "remaining_reservation_bytes": normalized.byte_summary[
                        "remaining_reservation_bytes"
                    ],
                    "next_ranked_subject_does_not_fit": (
                        expected_count < selector.MAXIMUM_SUBJECTS
                    ),
                    "all_eligible_subjects_fit": (
                        expected_count == selector.MAXIMUM_SUBJECTS
                    ),
                    "selection_identity_sha256": selection_hash,
                    "source_canonical_sha256": source_hash,
                }
            )
            if first_source is None:
                first_source = source
                first_normalized = normalized
    if (
        any(len(values) != 1 for values in profile_hashes.values())
        or any(len(values) != 1 for values in profile_source_hashes.values())
        or len({next(iter(values)) for values in profile_hashes.values()})
        != len(PROFILE_COUNTS)
    ):
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[6], "generated replay or profile identity differs"
        )
    if first_source is None or first_normalized is None:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[6], "generated success matrix is empty"
        )
    raw, eligible_keys, _source_sha256 = _raw_selection_for_mutations(
        first_source,
        vr2_contract=registered_vr2,
        selector_contract=frozen_selector,
    )
    mutations = _run_mutation_matrix(
        contract=contract,
        source=first_source,
        raw=raw,
        normalized=first_normalized,
        eligible_keys=eligible_keys,
        selector_contract=frozen_selector,
    )
    runtime = clock() - started
    peak_rss = int(rss_reader())
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_generated_only_dynamic_selection_qualification",
        "proof_posture": (
            "generated_live_shaped_structural_selection_only_no_private_or_scientific_value"
        ),
        "green_registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "dynamic_policy": {
            "minimum_selected_subjects": selector.MINIMUM_SUBJECTS,
            "maximum_selected_subjects": selector.MAXIMUM_SUBJECTS,
            "reservation_cap_bytes": selector.RESERVATION_CAP_BYTES,
            "source_validation_precedes_selection": True,
            "exact_generated_selection_assertion_called": False,
            "selected_count_reservation_and_hash_are_measured_outputs": True,
            "live_row_source_id": LIVE_ROW_SOURCE_ID,
            "live_private_proof_posture": LIVE_PROOF_POSTURE,
            "upstream_route_code_only": True,
            "upstream_reason_or_private_value_retained": False,
        },
        "generated_profiles": profile_rows,
        "replay_summary": {
            "profiles": len(PROFILE_COUNTS),
            "row_orders": 2,
            "success_paths": len(profile_rows),
            "same_profile_replay_exact": True,
            "different_subject_counts_have_distinct_selection_hashes": True,
        },
        "mutation_summary": mutations,
        "measurements": {
            "fixed_committed_artifact_reads": fixed_count + 1,
            "fixed_committed_input_bytes": fixed_bytes + len(contract_payload),
            "generated_input_bytes": generated_input_bytes,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
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
        "access_counters": {
            "private_or_Git_ignored_path_operations": 0,
            "consumed_root_marker_certificate_or_source_operations": 0,
            "network_download_provider_or_language_model_operations": 0,
            "archive_local_header_or_member_payload_reads": 0,
            "signal_event_target_label_quality_channel_or_geometry_reads": 0,
            "real_participant_or_cohort_selections": 0,
            "derivative_cache_split_feature_or_neurotoken_operations": 0,
            "training_inference_prediction_freeze_delivery_or_score_operations": 0,
            "stream_device_or_hardware_operations": 0,
            "consumed_executor_patch_retry_rerun_resume_or_reuse_operations": 0,
            "MARC2_FW2_or_CIL1_operations": 0,
            "scientific_claim_upgrades": 0,
            "operations_on_other_projects": 0,
        },
        "acceptance_gates": {
            "green_registration_preceded_implementation": True,
            "all_fixed_artifact_hashes_passed": True,
            "five_dynamic_subject_boundaries_passed": True,
            "both_row_orders_replayed": True,
            "full_source_validation_preceded_selection": True,
            "fixture_exact_result_assertion_was_not_called": True,
            "rank_split_cap_and_maximality_invariants_passed": True,
            "live_source_semantics_replaced_generated_labels": True,
            "upstream_route_code_only_boundary_passed": True,
            "target_firewall_and_aggregate_privacy_passed": True,
            "minimum_mutation_count_passed": (
                mutations["direct_mutations_passed"]
                >= contract["generated_replay_policy"]["minimum_direct_mutations"]
            ),
            "one_thread_runtime_RSS_input_output_and_retention_caps_passed": True,
            "all_forbidden_real_neural_target_model_score_counters_zero": True,
        },
        "route": SUCCESS_ROUTE,
        "warnings": [
            "All sources and selections in this qualification are generated fixtures.",
            "Live source semantics were validated as an interface contract, not observed on a new private source.",
            "No real cohort is frozen and the consumed private VR2 route remains unavailable.",
            "A future private structural pass requires a new Tier C packet and decision.",
        ],
        "unavailable_fields": [
            "real selected participant count reservation bytes and selection identity",
            "consumed private nested VR2 route reason predicate and value",
            "archive member integrity neural signals events targets channels and geometry",
            "model predictions scores and end-to-end neural decoding latency",
        ],
        "claim_boundary": contract["claim_boundary"],
    }
    for _ in range(6):
        payload = _canonical_json_bytes(report)
        size = len(payload)
        if report["measurements"]["aggregate_output_bytes"] == size:
            break
        report["measurements"]["aggregate_output_bytes"] = size
    payload = _canonical_json_bytes(report)
    if len(payload) != report["measurements"]["aggregate_output_bytes"]:
        raise DynamicLiveSelectionRefusal(
            REFUSAL_ROUTES[7], "aggregate output size did not converge"
        )
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        generated_input_bytes=generated_input_bytes,
        aggregate_output_bytes=len(payload),
        retained_output_bytes=0,
        contract=contract,
    )
    _walk_public(report)
    return report


def build_plan_summary(*, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or _repo_root()).resolve()
    contract, _payload = _load_contract(root)
    return {
        "schema_name": CONTRACT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": contract["status"],
        "generated_profiles": list(PROFILE_COUNTS),
        "generated_success_paths": contract["generated_replay_policy"][
            "success_paths"
        ],
        "minimum_direct_mutations": contract["generated_replay_policy"][
            "minimum_direct_mutations"
        ],
        "private_or_Git_ignored_bytes": 0,
        "network_bytes": 0,
        "execute_command": False,
        "real_cohort_freeze_authorized": False,
        "MARC2_FW2_or_CIL1_authorized": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=(
            "python -m neurodecodekit.datasets."
            "marc2_dynamic_live_selection"
        ),
        description=(
            "Qualify dynamic target-free live-selection invariants on generated "
            "structural manifests only."
        ),
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        value = (
            build_plan_summary()
            if args.command == "plan"
            else qualify_generated()
        )
    except DynamicLiveSelectionRefusal as exc:
        suffix = (
            f" upstream={exc.upstream_route}"
            if exc.upstream_route is not None
            else ""
        )
        print(f"{exc.route}: {exc.safe_reason}{suffix}", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(value).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
