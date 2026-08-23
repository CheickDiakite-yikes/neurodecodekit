"""Generated-only MARC2 selection-sufficiency repair qualification."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import resource
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_exact_task_surplus_decomposition as vr37a
from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a
from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a
from neurodecodekit.datasets import marc2_source_validity_eligibility_repair as repair
from neurodecodekit.datasets import marc2_task_aware_eligibility_repair as vr35a


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR38A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_selection_sufficiency_repair_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_selection_sufficiency_repair_result"
CONTRACT_RELATIVE_PATH = Path("registries/marc2_selection_sufficiency_repair_contract.v0.json")
CONTRACT_SHA256 = "0ab620ca0e424247899b5ba4e58c3cbd5f670f7c4ee27a241c52d58d075080d5"
GREEN_REGISTRATION_COMMIT = "25205b1d2a1033cf3cefcab022c885025ac76928"
GREEN_REGISTRATION_CI_RUN_ID = 32_670_514_251
GREEN_REGISTRATION_BASE_JOB_ID = 97_270_563_617
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_270_563_773
SUCCESS_ROUTES = ("MARC2VR38A-G1", "MARC2VR38A-G2")
DIAGNOSTIC_ROUTES = (
    "MARC2VR38A-R1",
    "MARC2VR38A-R2",
    "MARC2VR38A-R3",
)
REFUSAL_ROUTES = tuple(f"MARC2VR38A-F{index:02d}" for index in range(1, 7))
CASES = (
    "public_map_exact_control",
    "single_cell_contiguous_optional_surplus",
    "single_cell_noncontiguous_optional_surplus",
    "multi_cell_optional_surplus",
    "mixed_optional_surplus_and_deficit",
    "required_fit_run_missing",
    "required_heldout_run_missing",
    "unknown_participant",
    "incomplete_companion_set",
    "minimum_prefix_exceeds_cap",
)
ORDERS = ("canonical", "reversed")
REPLAYS = 2
EXPECTED_CASE_ROUTES = {
    "public_map_exact_control": SUCCESS_ROUTES[0],
    "single_cell_contiguous_optional_surplus": SUCCESS_ROUTES[1],
    "single_cell_noncontiguous_optional_surplus": SUCCESS_ROUTES[1],
    "multi_cell_optional_surplus": SUCCESS_ROUTES[1],
    "mixed_optional_surplus_and_deficit": SUCCESS_ROUTES[1],
    "required_fit_run_missing": DIAGNOSTIC_ROUTES[0],
    "required_heldout_run_missing": DIAGNOSTIC_ROUTES[0],
    "unknown_participant": DIAGNOSTIC_ROUTES[1],
    "incomplete_companion_set": DIAGNOSTIC_ROUTES[1],
    "minimum_prefix_exceeds_cap": DIAGNOSTIC_ROUTES[2],
}
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
FORBIDDEN_PUBLIC_KEYS = {
    "actual_count",
    "cohort",
    "difference",
    "eligible_count",
    "filtered_count",
    "member_name",
    "observed_count",
    "participant_id",
    "private_manifest",
    "private_value",
    "reservation",
    "run_index",
    "selected_rows",
    "selection_identity",
    "source_exact_name",
    "source_path",
    "subject_id",
    "target_text",
    "target_value",
    "task_distribution",
}


class SelectionSufficiencyRepairRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR38A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in (*DIAGNOSTIC_ROUTES, *REFUSAL_ROUTES):
            raise ValueError("unknown MARC2-VR38A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class SelectionSufficiencyOutcome:
    """In-memory generated selection and comparison-only hashes."""

    selection: selector.SelectionResult
    route: str
    source_sha256: str
    semantic_sha256: str
    source_exact_selected_names_sha256: str


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
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR38A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract schema differs"
        )
    return payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    registered = load_registered_contract()
    matrix = contract.get("generated_matrix", {})
    implementation = contract.get("implementation_contract", {})
    resources = contract.get("resource_limits", {})
    forbidden = contract.get("forbidden_operations", {})
    selection_contract = contract.get("selection_contract", {})
    if (
        not isinstance(contract, dict)
        or contract != registered
        or contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or matrix.get("cases") != list(CASES)
        or matrix.get("orders") != list(ORDERS)
        or matrix.get("replays") != REPLAYS
        or matrix.get("required_paths") != 40
        or matrix.get("accepted_paths") != 20
        or matrix.get("minimum_direct_refusals", 0) < 80
        or matrix.get("expected_route_counts")
        != {
            SUCCESS_ROUTES[0]: 4,
            SUCCESS_ROUTES[1]: 16,
            DIAGNOSTIC_ROUTES[0]: 8,
            DIAGNOSTIC_ROUTES[1]: 8,
            DIAGNOSTIC_ROUTES[2]: 4,
        }
        or selection_contract.get("required_runs_per_session") != [1, 2, 3]
        or selection_contract.get("minimum_selected_subjects") != 12
        or selection_contract.get("maximum_selected_subjects") != 19
        or selection_contract.get("reservation_cap_bytes") != selector.RESERVATION_CAP_BYTES
        or selection_contract.get("global_eligible_total_equality_required_for_selection")
        is not False
        or implementation.get("commands") != ["plan", "qualify"]
        or implementation.get("dependency_policy") != "standard_library_only"
        or implementation.get("private_executor_allowed") is not False
        or resources.get("CPU_threads") != 1
        or resources.get("workers") != 1
        or resources.get("numerical_jobs") != 1
        or resources.get("network_bytes") != 0
        or resources.get("new_payload_bytes") != 0
        or not forbidden
        or any(value != 0 for value in forbidden.values())
    ):
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT != "25205b1d2a1033cf3cefcab022c885025ac76928"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_670_514_251
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_270_563_617
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_270_563_773
    ):
        raise SelectionSufficiencyRepairRefusal(REFUSAL_ROUTES[0], "registration proof differs")


def _verify_fixed_inputs(contract: Mapping[str, Any], root: Path | None = None) -> int:
    fixed_root = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 11:
        raise SelectionSufficiencyRepairRefusal(REFUSAL_ROUTES[0], "fixed input registry differs")
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise SelectionSufficiencyRepairRefusal(REFUSAL_ROUTES[0], "fixed input row differs")
        try:
            payload = (fixed_root / str(row["path"])).read_bytes()
        except (KeyError, OSError) as exc:
            raise SelectionSufficiencyRepairRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row.get("bytes") or _sha256_bytes(payload) != row.get("sha256"):
            raise SelectionSufficiencyRepairRefusal(REFUSAL_ROUTES[0], "fixed input differs")
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise SelectionSufficiencyRepairRefusal(REFUSAL_ROUTES[0], "fixed input byte total differs")
    return total


def _source_bytes(source: Mapping[str, Any]) -> bytes:
    try:
        return vr35a._source_bytes(source)
    except vr35a.TaskAwareEligibilityRepairRefusal as exc:
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[1], "generated source is not canonical"
        ) from exc


def _selection_exception_route(exc: BaseException) -> str:
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, selector.FreewillPrefixSelectionRefusal):
            if current.refusal_id == selector.REFUSAL_IDS[4]:
                return DIAGNOSTIC_ROUTES[2]
            return DIAGNOSTIC_ROUTES[0]
        current = current.__cause__
    return DIAGNOSTIC_ROUTES[0]


def _semantic_identity(selection: selector.SelectionResult) -> dict[str, Any]:
    """Preserve every selected fact except the whole-source hash binding."""

    identity = asdict(selection)
    manifest = identity["private_manifest"]
    for row in manifest["rows"]:
        row["source_hashes"].pop("generated_inventory_sha256", None)
    hashes = identity["selection_hashes"]
    hashes.pop("generated_inventory_sha256", None)
    hashes["private_selection_manifest_sha256"] = _sha256_bytes(_canonical_json_bytes(manifest))
    return identity


def _validate_selection(
    selection: selector.SelectionResult,
    *,
    filtered_keys: set[tuple[str, str, int]],
    source_names: set[str],
    source_rows: Mapping[str, Mapping[str, Any]],
    source_sha256: str,
    selector_contract: Mapping[str, Any],
) -> tuple[str, str]:
    try:
        rank = selector._validate_rank(selector_contract)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise SelectionSufficiencyRepairRefusal(REFUSAL_ROUTES[2], "selector rank differs") from exc
    cohort = selection.cohort_summary
    split = selection.split_summary
    byte_summary = selection.byte_summary
    subjects = cohort.get("selected_subject_ids")
    if not isinstance(subjects, list):
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[0], "selected subject prefix differs"
        )
    count = len(subjects)
    if (
        subjects != rank[:count]
        or not selector.MINIMUM_SUBJECTS <= count <= selector.MAXIMUM_SUBJECTS
        or cohort.get("selected_subjects") != count
        or cohort.get("selection_is_maximal_contiguous_rank_prefix") is not True
        or cohort.get("selection_was_target_quality_and_outcome_free") is not True
        or split.get("fit_session") != "ses-01"
        or split.get("heldout_session") != "ses-02"
        or split.get("fit_run_bundles") != count * 3
        or split.get("heldout_run_bundles") != count * 3
        or split.get("selected_run_bundles") != count * 6
        or split.get("selected_core_members") != count * 24
        or split.get("fit_heldout_overlap") != 0
        or split.get("row_random_split_used") is not False
    ):
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[0], "cohort or split arithmetic differs"
        )
    rows = selection.private_manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != count * 24:
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[0], "selected structural rows differ"
        )
    names: set[str] = set()
    suffixes: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    measured_reservation = 0
    expected_keys = {
        (subject, session, run)
        for subject in subjects
        for session in ("ses-01", "ses-02")
        for run in (1, 2, 3)
    }
    for row in rows:
        name = row.get("member_name")
        match = vr20a._core_match(name) if isinstance(name, str) else None
        if match is None or match.group("task") != vr35a.PUBLISHED_TASK:
            raise SelectionSufficiencyRepairRefusal(
                DIAGNOSTIC_ROUTES[0], "selected task identity differs"
            )
        key = (
            match.group("subject"),
            match.group("session"),
            vr20a._semantic_run(match.group("run")),
        )
        expected_reservation = selector._reservation_bytes(row)
        source_hashes = row.get("source_hashes")
        source_row = source_rows.get(name)
        if (
            name not in source_names
            or name in names
            or key not in filtered_keys
            or key not in expected_keys
            or row.get("subject_id") != key[0]
            or row.get("session_id") != key[1]
            or row.get("run_id") != f"run-{key[2]:02d}"
            or row.get("split_role") != ("fit" if key[1] == "ses-01" else "heldout")
            or row.get("reservation_bytes") != expected_reservation
            or not isinstance(source_hashes, dict)
            or source_hashes.get("generated_inventory_sha256") != source_sha256
            or not isinstance(source_row, Mapping)
            or any(
                row.get(field) != source_row.get(field)
                for field in (
                    "local_header_offset",
                    "CRC32",
                    "compressed_size",
                    "uncompressed_size",
                )
            )
        ):
            raise SelectionSufficiencyRepairRefusal(
                DIAGNOSTIC_ROUTES[0], "selected row identity or binding differs"
            )
        names.add(name)
        suffixes[key].add(match.group("suffix"))
        measured_reservation += expected_reservation
    if (
        set(suffixes) != expected_keys
        or any(values != set(selector.REQUIRED_SUFFIXES) for values in suffixes.values())
        or measured_reservation != byte_summary.get("selected_reservation_bytes")
        or byte_summary.get("reservation_cap_bytes") != selector.RESERVATION_CAP_BYTES
        or byte_summary.get("remaining_reservation_bytes")
        != selector.RESERVATION_CAP_BYTES - measured_reservation
        or measured_reservation > selector.RESERVATION_CAP_BYTES
        or selection.selection_hashes.get("generated_inventory_sha256") != source_sha256
    ):
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[0], "selected companion or storage arithmetic differs"
        )
    next_subject = cohort.get("first_nonfitting_subject_id")
    examined = cohort.get("candidate_subjects_examined")
    next_reservation = byte_summary.get("first_nonfitting_subject_reservation_bytes")
    if count < selector.MAXIMUM_SUBJECTS:
        if (
            next_subject != rank[count]
            or examined != count + 1
            or isinstance(next_reservation, bool)
            or not isinstance(next_reservation, int)
            or next_reservation <= byte_summary["remaining_reservation_bytes"]
        ):
            raise SelectionSufficiencyRepairRefusal(
                DIAGNOSTIC_ROUTES[0], "maximal prefix boundary differs"
            )
    elif next_subject is not None or next_reservation is not None or examined != count:
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[0], "full prefix boundary differs"
        )
    semantic = _sha256_bytes(_canonical_json_bytes(_semantic_identity(selection)))
    names_hash = _sha256_bytes(_canonical_json_bytes(sorted(names)))
    return semantic, names_hash


def _public_map_is_exact(
    filtered: Mapping[tuple[str, str, int], Mapping[str, Mapping[str, Any]]],
    vr2_contract: Mapping[str, Any],
) -> bool:
    counts = vr2_contract["published_eligible_session_counts"]
    subjects = vr2_contract["participant_taxonomy"]["eligible_subject_ids"]
    expected = {
        (subject, session): set(range(1, int(counts[subject][index]) + 1))
        for subject in subjects
        for index, session in enumerate(("ses-01", "ses-02"))
    }
    observed: dict[tuple[str, str], set[int]] = defaultdict(set)
    for subject, session, run in filtered:
        if run < 1:
            raise SelectionSufficiencyRepairRefusal(
                DIAGNOSTIC_ROUTES[1], "semantic run index is below one"
            )
        observed[(subject, session)].add(run)
    return dict(observed) == expected


def select_generated_source(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    vr2_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> SelectionSufficiencyOutcome:
    """Select the invariant required core without exact-total equality."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    _verify_fixed_inputs(registered)
    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    frozen_selector = dict(selector_contract or selector.load_registered_contract(_repo_root()))
    before = _source_bytes(source)
    try:
        vr2._verify_contract_mapping(registered_vr2)
        entries = vr2._validate_live_envelope(source, registered_vr2)
        grouped, kinds = vr35a._group_task_rows(entries)
        vr35a._classify(grouped, registered_vr2)
        projected = vr35a._project_published_task(grouped)
        labels = vr35a._classify(projected, registered_vr2)
    except (
        vr2.LiveDomainEligibilityRefusal,
        vr35a.TaskAwareEligibilityRepairRefusal,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[1], "source task taxonomy or companions differ"
        ) from exc
    domain = registered_vr2["generated_live_source_domain"]
    if kinds != Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    ):
        raise SelectionSufficiencyRepairRefusal(
            DIAGNOSTIC_ROUTES[1], "source entry-kind arithmetic differs"
        )
    filtered = {
        key: companions
        for key, companions in projected.items()
        if labels[key] == vr2.PREDICATE_CODES[0]
    }
    public_map_exact = _public_map_is_exact(filtered, registered_vr2)
    if _source_bytes(source) != before:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[3], "source changed during validation"
        )
    source_sha256 = _sha256_bytes(before)
    try:
        selection = repair._select_from_filtered(filtered, source_sha256, frozen_selector)
    except (
        repair.SourceValidityEligibilityRefusal,
        selector.FreewillPrefixSelectionRefusal,
    ) as exc:
        route = _selection_exception_route(exc)
        raise SelectionSufficiencyRepairRefusal(route, "required-core selection refused") from exc
    if _source_bytes(source) != before:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[3], "source changed during selection"
        )
    source_names = {
        row["member_name"]
        for row in source["entries"]
        if isinstance(row, dict) and isinstance(row.get("member_name"), str)
    }
    source_rows = {
        row["member_name"]: row
        for row in source["entries"]
        if isinstance(row, dict) and isinstance(row.get("member_name"), str)
    }
    semantic, names_hash = _validate_selection(
        selection,
        filtered_keys=set(filtered),
        source_names=source_names,
        source_rows=source_rows,
        source_sha256=source_sha256,
        selector_contract=frozen_selector,
    )
    return SelectionSufficiencyOutcome(
        selection=selection,
        route=SUCCESS_ROUTES[0] if public_map_exact else SUCCESS_ROUTES[1],
        source_sha256=source_sha256,
        semantic_sha256=semantic,
        source_exact_selected_names_sha256=names_hash,
    )


def _remove_required_bundle(
    source: Mapping[str, Any], key: tuple[str, str, int], label: str
) -> None:
    vr25a._replace_bundle_with_auxiliary(source, key, label)


def _adjust_required_prefix_reservation(
    source: Mapping[str, Any], subjects: Sequence[str], target_bytes: int
) -> None:
    subject_set = set(subjects)
    rows: list[dict[str, Any]] = []
    for row in source["entries"]:
        name = row.get("member_name") if isinstance(row, dict) else None
        match = vr20a._core_match(name) if isinstance(name, str) else None
        if (
            match is not None
            and match.group("task") == vr35a.PUBLISHED_TASK
            and match.group("subject") in subject_set
            and match.group("session") in {"ses-01", "ses-02"}
            and vr20a._semantic_run(match.group("run")) in {1, 2, 3}
        ):
            rows.append(row)
    if len(rows) != len(subjects) * 24:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[2], "generated reservation prefix differs"
        )
    overhead = sum(30 + len(row["member_name"].encode("utf-8")) + 65_535 for row in rows)
    compressed_total = target_bytes - overhead
    if compressed_total < len(rows):
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[2], "generated reservation adjustment is negative"
        )
    quotient, remainder = divmod(compressed_total, len(rows))
    for index, row in enumerate(sorted(rows, key=lambda item: item["member_name"])):
        compressed = quotient + (1 if index < remainder else 0)
        row["compressed_size"] = compressed
        row["uncompressed_size"] = compressed + 128


def build_generated_case(case: str, order: str) -> dict[str, Any]:
    """Build one exact generated VR38A selection-sufficiency witness."""

    if case not in CASES:
        raise ValueError("unknown generated case")
    if order not in ORDERS:
        raise ValueError("unknown generated row order")
    if case == "public_map_exact_control":
        source = vr37a.build_generated_case("public_map_exact_control", "canonical")
    elif case == "single_cell_contiguous_optional_surplus":
        source = vr37a.build_generated_case("single_cell_contiguous_extension", "canonical")
    elif case == "single_cell_noncontiguous_optional_surplus":
        source = vr37a.build_generated_case("single_cell_noncontiguous_extension", "canonical")
    elif case == "multi_cell_optional_surplus":
        source = vr37a.build_generated_case("multi_cell_pure_surplus", "canonical")
    elif case == "mixed_optional_surplus_and_deficit":
        source = vr37a.build_generated_case("mixed_surplus_and_deficit_net_positive", "canonical")
    elif case in {"required_fit_run_missing", "required_heldout_run_missing"}:
        source = vr37a.build_generated_case("public_map_exact_control", "canonical")
        session = "ses-01" if case == "required_fit_run_missing" else "ses-02"
        _remove_required_bundle(source, ("sub-08", session, 1), case)
    elif case == "unknown_participant":
        source = vr25a.build_generated_case("unknown_participant_bundle", "canonical")
    elif case == "incomplete_companion_set":
        source = vr25a.build_generated_case("incomplete_companion_set", "canonical")
    else:
        source = vr37a.build_generated_case("public_map_exact_control", "canonical")
        frozen_selector = selector.load_registered_contract(_repo_root())
        rank = selector._validate_rank(frozen_selector)
        _adjust_required_prefix_reservation(
            source,
            rank[: selector.MINIMUM_SUBJECTS],
            selector.RESERVATION_CAP_BYTES + 1,
        )
    source["entries"] = sorted(source["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        source["entries"].reverse()
    return source


def _route_case(
    source: Mapping[str, Any], *, contract: Mapping[str, Any] | None = None
) -> tuple[str, SelectionSufficiencyOutcome | None]:
    try:
        outcome = select_generated_source(source, contract=contract)
    except SelectionSufficiencyRepairRefusal as exc:
        if exc.route not in DIAGNOSTIC_ROUTES:
            raise
        return exc.route, None
    return outcome.route, outcome


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise SelectionSufficiencyRepairRefusal(REFUSAL_ROUTES[5], "thread environment differs")


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise SelectionSufficiencyRepairRefusal(
                    REFUSAL_ROUTES[4], "aggregate report contains forbidden field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1_048_576:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[4], "aggregate report exceeds output cap"
        )


def _assert_source_surface_safe(source_text: str) -> None:
    forbidden = (
        ".codex" + "_work",
        "/" + "Users" + "/",
        "file:" + "//",
        "private" + "_executor",
    )
    if any(token in source_text for token in forbidden):
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[4], "module contains a forbidden path or executor surface"
        )


def _assert_zero_operations(counters: Mapping[str, int]) -> None:
    if not counters or any(value != 0 for value in counters.values()):
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[4], "forbidden operation counter is nonzero"
        )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    aggregate_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    limits = contract["resource_limits"]
    if (
        runtime_seconds < 0
        or runtime_seconds > limits["runtime_seconds_maximum"]
        or peak_rss_bytes < 0
        or peak_rss_bytes >= limits["peak_RSS_bytes_maximum_exclusive"]
        or aggregate_output_bytes > limits["generated_output_bytes_maximum"]
    ):
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(expected_route: str, action: Callable[[], Any]) -> str:
    try:
        action()
    except SelectionSufficiencyRepairRefusal as exc:
        if exc.route != expected_route:
            raise SelectionSufficiencyRepairRefusal(
                REFUSAL_ROUTES[2], "direct refusal route differs"
            ) from exc
        return exc.route
    raise SelectionSufficiencyRepairRefusal(
        REFUSAL_ROUTES[2], "direct mutation unexpectedly passed"
    )


def _leaf_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    paths: list[tuple[Any, ...]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            paths.extend(_leaf_paths(child, (*prefix, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_leaf_paths(child, (*prefix, index)))
    else:
        paths.append(prefix)
    return paths


def _mutate_leaf(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if value is None:
        return "changed"
    return "changed" if value != "changed" else "changed-again"


def _contract_mutations(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []
    for path in _leaf_paths(contract)[:64]:
        changed = copy.deepcopy(dict(contract))
        cursor: Any = changed
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = _mutate_leaf(cursor[path[-1]])
        mutations.append(changed)
    return mutations


def _mutated_selection(
    outcome: SelectionSufficiencyOutcome, mutation: str
) -> selector.SelectionResult:
    changed = copy.deepcopy(outcome.selection)
    if mutation == "selected_run":
        changed.private_manifest["rows"][0]["run_id"] = "run-04"
    elif mutation == "split_overlap":
        changed.split_summary["fit_heldout_overlap"] = 1
    elif mutation == "storage_cap":
        changed.byte_summary["reservation_cap_bytes"] += 1
    else:
        raise ValueError("unknown selection mutation")
    return changed


def _run_direct_refusals(contract: Mapping[str, Any]) -> Counter[str]:
    routes: Counter[str] = Counter()
    for changed in _contract_mutations(contract):
        route = _expect_refusal(
            REFUSAL_ROUTES[0], lambda item=changed: _verify_contract_mapping(item)
        )
        routes[route] += 1
    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        route = _expect_refusal(
            REFUSAL_ROUTES[4],
            lambda value=key: _assert_public_report_safe({value: "forbidden"}),
        )
        routes[route] += 1
    limits = contract["resource_limits"]
    for runtime_seconds, rss, output_bytes in (
        (limits["runtime_seconds_maximum"] + 1.0, 1, 1),
        (1.0, limits["peak_RSS_bytes_maximum_exclusive"], 1),
        (1.0, 1, limits["generated_output_bytes_maximum"] + 1),
    ):
        route = _expect_refusal(
            REFUSAL_ROUTES[5],
            lambda a=runtime_seconds, b=rss, c=output_bytes: _assert_resources(
                runtime_seconds=a,
                peak_rss_bytes=b,
                aggregate_output_bytes=c,
                contract=contract,
            ),
        )
        routes[route] += 1
    baseline = build_generated_case("public_map_exact_control", "canonical")
    outcome = select_generated_source(baseline, contract=contract)
    source_names = {row["member_name"] for row in baseline["entries"]}
    source_rows = {row["member_name"]: row for row in baseline["entries"]}
    filtered_keys = {
        (
            row["subject_id"],
            row["session_id"],
            int(row["run_id"].removeprefix("run-")),
        )
        for row in outcome.selection.private_manifest["rows"]
    }
    frozen_selector = selector.load_registered_contract(_repo_root())
    for mutation in ("selected_run", "split_overlap", "storage_cap"):
        changed_selection = _mutated_selection(outcome, mutation)
        route = _expect_refusal(
            DIAGNOSTIC_ROUTES[0],
            lambda value=changed_selection: _validate_selection(
                value,
                filtered_keys=filtered_keys,
                source_names=source_names,
                source_rows=source_rows,
                source_sha256=outcome.source_sha256,
                selector_contract=frozen_selector,
            ),
        )
        routes[route] += 1
    malformed = copy.deepcopy(baseline)
    malformed.pop("proof_posture")
    duplicate = copy.deepcopy(baseline)
    duplicate["entries"][0]["member_name"] = duplicate["entries"][1]["member_name"]
    for source in (
        malformed,
        duplicate,
        build_generated_case("unknown_participant", "canonical"),
        build_generated_case("incomplete_companion_set", "canonical"),
    ):
        route = _expect_refusal(
            DIAGNOSTIC_ROUTES[1], lambda value=source: select_generated_source(value)
        )
        routes[route] += 1
    for case, expected in (
        ("required_fit_run_missing", DIAGNOSTIC_ROUTES[0]),
        ("minimum_prefix_exceeds_cap", DIAGNOSTIC_ROUTES[2]),
    ):
        source = build_generated_case(case, "canonical")
        route = _expect_refusal(expected, lambda value=source: select_generated_source(value))
        routes[route] += 1
    changed_rank = copy.deepcopy(frozen_selector)
    changed_rank["participant_rank"]["full_rank"][0:2] = reversed(
        changed_rank["participant_rank"]["full_rank"][0:2]
    )
    route = _expect_refusal(
        REFUSAL_ROUTES[2],
        lambda: _validate_selection(
            outcome.selection,
            filtered_keys=filtered_keys,
            source_names=source_names,
            source_rows=source_rows,
            source_sha256=outcome.source_sha256,
            selector_contract=changed_rank,
        ),
    )
    routes[route] += 1
    for source_text in (
        "path = '" + ".codex" + "_work'",
        "path = '/" + "Users/example/private'",
        "def private" + "_executor(): pass",
    ):
        route = _expect_refusal(
            REFUSAL_ROUTES[4],
            lambda value=source_text: _assert_source_surface_safe(value),
        )
        routes[route] += 1
    changed_operations = dict(contract["forbidden_operations"])
    changed_operations[next(iter(changed_operations))] = 1
    route = _expect_refusal(REFUSAL_ROUTES[4], lambda: _assert_zero_operations(changed_operations))
    routes[route] += 1
    if sum(routes.values()) < contract["generated_matrix"]["minimum_direct_refusals"]:
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[2], "direct refusal coverage is incomplete"
        )
    return routes


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the sole registered 40-path generated-only VR38A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment(environment)
    refusal_counts = _run_direct_refusals(registered)
    route_counts: Counter[str] = Counter()
    replay_hashes: dict[str, list[str]] = {
        f"{case}:{order}": [] for case in CASES for order in ORDERS
    }
    replay_signatures: list[list[tuple[str, str, str, str | None]]] = []
    semantic_hashes: set[str] = set()
    names_hashes: set[str] = set()
    selected_counts: set[int] = set()
    generated_input_bytes = 0
    selector_calls = 0
    for _replay in range(REPLAYS):
        signature: list[tuple[str, str, str, str | None]] = []
        for order in ORDERS:
            for case in CASES:
                source = build_generated_case(case, order)
                before = _source_bytes(source)
                generated_input_bytes += len(before)
                replay_hashes[f"{case}:{order}"].append(_sha256_bytes(before))
                route, outcome = _route_case(source, contract=registered)
                selector_calls += 1
                if route != EXPECTED_CASE_ROUTES[case] or _source_bytes(source) != before:
                    raise SelectionSufficiencyRepairRefusal(
                        REFUSAL_ROUTES[3], "generated route or immutability differs"
                    )
                semantic = outcome.semantic_sha256 if outcome is not None else None
                if outcome is not None:
                    semantic_hashes.add(outcome.semantic_sha256)
                    names_hashes.add(outcome.source_exact_selected_names_sha256)
                    selected_counts.add(outcome.selection.cohort_summary["selected_subjects"])
                route_counts[route] += 1
                signature.append((case, order, route, semantic))
        replay_signatures.append(signature)
    matrix = registered["generated_matrix"]
    if (
        route_counts != Counter(matrix["expected_route_counts"])
        or selector_calls != matrix["required_paths"]
        or replay_signatures[0] != replay_signatures[1]
        or any(len(set(values)) != 1 for values in replay_hashes.values())
        or len(semantic_hashes) != matrix["accepted_semantic_selection_identities"]
        or len(names_hashes) != 1
        or selected_counts != {16}
    ):
        raise SelectionSufficiencyRepairRefusal(
            REFUSAL_ROUTES[3], "generated matrix acceptance gate differs"
        )
    runtime = clock() - started
    rss = peak_rss()
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_selection_sufficiency_repair_qualified",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
        },
        "matrix": {
            "paths": sum(route_counts.values()),
            "cases": len(CASES),
            "orders": len(ORDERS),
            "replays": REPLAYS,
            "route_counts": dict(sorted(route_counts.items())),
            "selector_calls": selector_calls,
            "source_immutability_checks": sum(route_counts.values()),
            "exact_replays_match": True,
        },
        "selection_proof": {
            "accepted_paths": sum(route_counts[route] for route in SUCCESS_ROUTES),
            "accepted_semantic_identities": len(semantic_hashes),
            "accepted_source_exact_name_identities": len(names_hashes),
            "generated_selected_subjects": next(iter(selected_counts)),
            "generated_selected_run_bundles": next(iter(selected_counts)) * 6,
            "generated_selected_core_members": next(iter(selected_counts)) * 24,
            "required_runs_per_session": [1, 2, 3],
            "selected_optional_runs": 0,
            "selected_non_target_rows": 0,
            "selected_ineligible_rows": 0,
            "global_exact_195_gate_used": False,
        },
        "refusals": {
            "direct_refusals": sum(refusal_counts.values()),
            "route_counts": dict(sorted(refusal_counts.items())),
        },
        "measurements": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "aggregate_output_bytes": 0,
            "retained_output_bytes": 0,
            "runtime_seconds": runtime,
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
        "operation_counters": dict(registered["forbidden_operations"]),
        "warnings": [
            "generated_fixture_only_no_private_or_real_source_access",
            "selection_sufficiency_is_not_a_real_cohort_freeze",
            "no_archive_member_neural_payload_or_scientific_result",
        ],
        "unavailable_fields": [
            "private_exact_task_total_difference_or_topology",
            "real_target_free_selected_subjects_or_members",
            "archive_member_integrity_or_payload",
            "neural_signal_event_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "terminal_next_gate": registered["terminal_next_gate"],
        "claim_boundary": registered["claim_boundary"],
    }
    output_bytes = -1
    while report["measurements"]["aggregate_output_bytes"] != output_bytes:
        report["measurements"]["aggregate_output_bytes"] = output_bytes
        output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_zero_operations(report["operation_counters"])
    _assert_public_report_safe(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        aggregate_output_bytes=output_bytes,
        contract=registered,
    )
    return report


def build_plan() -> dict[str, Any]:
    """Return the fixed generated-only plan with no private executor."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "lane_id": LANE_ID,
        "status": "registered_generated_implementation_eligible",
        "fixed_input_bytes": _verify_fixed_inputs(contract),
        "cases": len(CASES),
        "orders": len(ORDERS),
        "replays": REPLAYS,
        "paths": len(CASES) * len(ORDERS) * REPLAYS,
        "direct_refusal_minimum": contract["generated_matrix"]["minimum_direct_refusals"],
        "private_access_authorized": False,
        "real_cohort_freeze_authorized": False,
        "FW2_or_CIL1_authorized": False,
        "execute_surface_available": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 selection-sufficiency repair."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = build_plan() if args.command == "plan" else qualify_generated()
    except SelectionSufficiencyRepairRefusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "status": "refused"},
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 2
    print(_canonical_json_bytes(payload).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
