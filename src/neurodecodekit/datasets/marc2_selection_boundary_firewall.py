"""Generated-only MARC2 selection-boundary firewall."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import resource
import sys
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import marc2_p15_run_index_repair as vr12a
from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a
from neurodecodekit.datasets import marc2_source_validity_eligibility_repair as repair


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR25A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_selection_boundary_firewall_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_selection_boundary_firewall_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_selection_boundary_firewall_contract.v0.json"
)
CONTRACT_SHA256 = "c0af130d51e68151757e85d14674e327673cb2586dab866bc4437320952d6ea1"
GREEN_REGISTRATION_COMMIT = "ad8be2197e58d4d3e0e1fe4f344de1c608930f73"
GREEN_REGISTRATION_CI_RUN_ID = 32_603_540_967
GREEN_REGISTRATION_BASE_JOB_ID = 97_105_227_375
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_105_227_440
SUCCESS_ROUTES = ("MARC2VR25A-G1", "MARC2VR25A-G2")
REFUSAL_ROUTES = tuple(f"MARC2VR25A-R{index}" for index in range(1, 5)) + tuple(
    f"MARC2VR25A-F{index:02d}" for index in range(1, 5)
)
CASES = (
    "exact_public_control",
    "single_session_exclusion_removed",
    "single_session_exclusion_added",
    "sampling_exclusion_removed",
    "outside_pair_bundle_added",
    "eligible_bundle_removed",
    "eligible_bundle_added",
    "eligible_distribution_shift",
    "unknown_participant_bundle",
    "incomplete_companion_set",
)
EXPECTED_CASE_ROUTES = {
    "exact_public_control": "MARC2VR25A-G1",
    "single_session_exclusion_removed": "MARC2VR25A-G2",
    "single_session_exclusion_added": "MARC2VR25A-G2",
    "sampling_exclusion_removed": "MARC2VR25A-G2",
    "outside_pair_bundle_added": "MARC2VR25A-G2",
    "eligible_bundle_removed": "MARC2VR25A-R1",
    "eligible_bundle_added": "MARC2VR25A-R1",
    "eligible_distribution_shift": "MARC2VR25A-R1",
    "unknown_participant_bundle": "MARC2VR25A-R2",
    "incomplete_companion_set": "MARC2VR25A-R3",
}
ORDERS = ("canonical", "reversed")
REPLAYS = 2
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


class SelectionBoundaryFirewallRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR25A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR25A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class FirewallSelection:
    """Generated selection plus private-in-memory comparison hashes."""

    selection: selector.SelectionResult
    route: str
    full_source_bundle_count_matches_public: bool
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
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F03", "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR25A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "registered contract schema differs"
        )
    return payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    registered = load_registered_contract()
    if (
        not isinstance(contract, dict)
        or contract != registered
        or contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "preregistered_artifact_only_generated_only_no_private_access"
    ):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "ad8be2197e58d4d3e0e1fe4f344de1c608930f73"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_603_540_967
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_105_227_375
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_105_227_440
    ):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "registration proof differs"
        )


def _verify_fixed_inputs(
    contract: Mapping[str, Any], root: Path | None = None
) -> int:
    fixed_root = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 12:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "fixed input registry differs"
        )
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise SelectionBoundaryFirewallRefusal(
                "MARC2VR25A-F01", "fixed input row differs"
            )
        try:
            payload = (fixed_root / str(row["path"])).read_bytes()
        except (KeyError, OSError) as exc:
            raise SelectionBoundaryFirewallRefusal(
                "MARC2VR25A-F01", "fixed input is unavailable"
            ) from exc
        if len(payload) != row.get("bytes") or _sha256_bytes(payload) != row.get(
            "sha256"
        ):
            raise SelectionBoundaryFirewallRefusal(
                "MARC2VR25A-F01", "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F01", "fixed input byte total differs"
        )
    return total


def _source_bytes(source: Mapping[str, Any]) -> bytes:
    try:
        return vr2._canonical_source_bytes(source)
    except (TypeError, ValueError) as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-R3", "source is not canonical"
        ) from exc


def apply_selection_boundary_firewall(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    vr2_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> FirewallSelection:
    """Validate one generated source and isolate the exact eligible inventory."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    _verify_fixed_inputs(registered)
    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    before = _source_bytes(source)
    try:
        vr2._verify_contract_mapping(registered_vr2)
        entries = vr2._validate_live_envelope(source, registered_vr2)
        grouped, kinds = vr20a._group_rows(entries)
    except (vr2.LiveDomainEligibilityRefusal, vr20a.PublishedTaskSelectorRepairRefusal) as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-R3", "source row or companion integrity differs"
        ) from exc
    domain = registered_vr2["generated_live_source_domain"]
    if kinds != Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    ):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-R3", "source entry-kind arithmetic differs"
        )
    labels: dict[tuple[str, str, int], str] = {}
    try:
        for key in grouped:
            labels[key] = vr2._classify_key(key, registered_vr2)
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-R2", "recognized participant taxonomy differs"
        ) from exc
    try:
        filtered = vr2._filter_and_validate_eligible(
            grouped, labels, registered_vr2
        )
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-R1", "eligible inventory or distribution differs"
        ) from exc
    compatibility = len(grouped) == domain["complete_source_run_bundles"]
    if _source_bytes(source) != before:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F02", "source changed during validation"
        )
    source_sha256 = _sha256_bytes(before)
    try:
        selection = repair._select_from_filtered(
            filtered, source_sha256, frozen_selector
        )
    except (
        repair.SourceValidityEligibilityRefusal,
        selector.FreewillPrefixSelectionRefusal,
    ) as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-R4", "target-free selection refused"
        ) from exc
    if _source_bytes(source) != before:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F02", "source changed during selection"
        )
    source_names = {
        row["member_name"]
        for row in source["entries"]
        if isinstance(row, dict) and isinstance(row.get("member_name"), str)
    }
    try:
        semantic, names_hash = vr20a._validate_selection(
            selection,
            filtered_keys=set(filtered),
            source_names=source_names,
            selector_contract=frozen_selector,
        )
    except vr20a.PublishedTaskSelectorRepairRefusal as exc:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-R4", "selection firewall differs"
        ) from exc
    return FirewallSelection(
        selection=selection,
        route=SUCCESS_ROUTES[0] if compatibility else SUCCESS_ROUTES[1],
        full_source_bundle_count_matches_public=compatibility,
        source_sha256=source_sha256,
        semantic_sha256=semantic,
        source_exact_selected_names_sha256=names_hash,
    )


def _bundle_rows(
    source: Mapping[str, Any], key: tuple[str, str, int]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in source["entries"]:
        if not isinstance(row, dict) or not isinstance(row.get("member_name"), str):
            continue
        match = vr20a._core_match(row["member_name"])
        if match is not None and (
            match.group("subject"),
            match.group("session"),
            vr20a._semantic_run(match.group("run")),
        ) == key:
            rows.append(row)
    if len(rows) != 4:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F02", "generated witness bundle differs"
        )
    return sorted(rows, key=lambda row: row["member_name"])


def _auxiliary_rows(source: Mapping[str, Any], count: int) -> list[dict[str, Any]]:
    rows = [
        row
        for row in source["entries"]
        if isinstance(row, dict)
        and row.get("entry_kind") == "regular_file"
        and isinstance(row.get("member_name"), str)
        and vr20a._core_match(row["member_name"]) is None
        and not any(
            row["member_name"].endswith(suffix)
            for suffix in selector.REQUIRED_SUFFIXES
        )
    ]
    if len(rows) < count:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F02", "generated auxiliary rows differ"
        )
    return sorted(rows, key=lambda row: row["member_name"])[:count]


def _replace_bundle_with_auxiliary(
    source: Mapping[str, Any], key: tuple[str, str, int], case: str
) -> None:
    for index, row in enumerate(_bundle_rows(source, key), start=1):
        row["member_name"] = (
            f"Freewill_generated/generated_aux/{case}-removed-{index:02d}.bin"
        )


def _bundle_name(
    key: tuple[str, str, int], suffix: str, *, root: str = "Freewill_generated"
) -> str:
    subject, session, run = key
    return (
        f"{root}/{subject}/{session}/eeg/{subject}_{session}_"
        f"task-{vr20a.PUBLISHED_TASK}_run-{run:04d}{suffix}"
    )


def _replace_auxiliary_with_bundle(
    source: Mapping[str, Any], key: tuple[str, str, int]
) -> None:
    for row, suffix in zip(
        _auxiliary_rows(source, 4), sorted(selector.REQUIRED_SUFFIXES), strict=True
    ):
        row["member_name"] = _bundle_name(key, suffix)


def _move_bundle(
    source: Mapping[str, Any],
    old_key: tuple[str, str, int],
    new_key: tuple[str, str, int],
) -> None:
    for row in _bundle_rows(source, old_key):
        match = vr20a._core_match(row["member_name"])
        assert match is not None
        row["member_name"] = _bundle_name(new_key, match.group("suffix"))


def build_generated_case(case: str, order: str) -> dict[str, Any]:
    """Build one exact generated VR25A witness."""

    if case not in CASES:
        raise ValueError("unknown generated case")
    if order not in ORDERS:
        raise ValueError("unknown generated row order")
    source = vr20a.build_generated_variant("published_four_digit", "canonical")
    if case == "single_session_exclusion_removed":
        _replace_bundle_with_auxiliary(source, ("sub-02", "ses-01", 1), case)
    elif case == "single_session_exclusion_added":
        _replace_auxiliary_with_bundle(source, ("sub-02", "ses-01", 3))
    elif case == "sampling_exclusion_removed":
        _replace_bundle_with_auxiliary(source, ("sub-13", "ses-01", 1), case)
    elif case == "outside_pair_bundle_added":
        _replace_auxiliary_with_bundle(source, ("sub-03", "ses-03", 2))
    elif case == "eligible_bundle_removed":
        _replace_bundle_with_auxiliary(source, ("sub-07", "ses-01", 1), case)
    elif case == "eligible_bundle_added":
        _replace_auxiliary_with_bundle(source, ("sub-07", "ses-01", 4))
    elif case == "eligible_distribution_shift":
        _move_bundle(
            source,
            ("sub-01", "ses-02", 7),
            ("sub-07", "ses-01", 4),
        )
    elif case == "unknown_participant_bundle":
        _move_bundle(
            source,
            ("sub-02", "ses-01", 1),
            ("sub-24", "ses-01", 1),
        )
    elif case == "incomplete_companion_set":
        row = _bundle_rows(source, ("sub-01", "ses-01", 1))[0]
        row["member_name"] = (
            "Freewill_generated/generated_aux/incomplete-companion.bin"
        )
    source["entries"] = sorted(source["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        source["entries"].reverse()
    return source


def _route_case(
    source: Mapping[str, Any], *, contract: Mapping[str, Any]
) -> tuple[str, FirewallSelection | None]:
    try:
        outcome = apply_selection_boundary_firewall(source, contract=contract)
    except SelectionBoundaryFirewallRefusal as exc:
        return exc.route, None
    return outcome.route, outcome


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F04", "thread environment differs"
        )


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in vr12a.FORBIDDEN_PUBLIC_KEYS:
                raise SelectionBoundaryFirewallRefusal(
                    "MARC2VR25A-F03", "aggregate report contains forbidden field"
                )
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1024**2:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F03", "aggregate report exceeds output cap"
        )


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    temporary_output_bytes: int,
    aggregate_output_bytes: int,
    generated_input_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_caps"]
    if (
        runtime_seconds < 0
        or runtime_seconds > caps["runtime_seconds"]
        or peak_rss_bytes < 0
        or peak_rss_bytes >= caps["peak_RSS_bytes"]
        or temporary_output_bytes > caps["temporary_output_bytes"]
        or aggregate_output_bytes > caps["aggregate_output_bytes"]
        or generated_input_bytes > caps["generated_input_bytes"]
    ):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F04", "generated resource cap exceeded"
        )


def _expect_refusal(expected_route: str, action: Callable[[], Any]) -> str:
    try:
        action()
    except SelectionBoundaryFirewallRefusal as exc:
        if exc.route != expected_route:
            raise SelectionBoundaryFirewallRefusal(
                "MARC2VR25A-F02", "direct refusal route differs"
            ) from exc
        return exc.route
    raise SelectionBoundaryFirewallRefusal(
        "MARC2VR25A-F02", "direct mutation unexpectedly passed"
    )


def _mutated_source(base: Mapping[str, Any], mutation: str) -> dict[str, Any]:
    changed = copy.deepcopy(dict(base))
    if mutation in CASES:
        return build_generated_case(mutation, "canonical")
    if mutation in {
        "schema_name",
        "schema_version",
        "proof_posture",
        "source_identity",
        "transport_body_sha256",
    }:
        changed[mutation] = "wrong"
    elif mutation == "empty_entries":
        changed["entries"] = []
    else:
        core_rows = _bundle_rows(changed, ("sub-01", "ses-01", 1))
        row = core_rows[0]
        if mutation == "row_field_added":
            row["unexpected"] = True
        elif mutation == "encrypted_row":
            row["general_purpose_flags"] = 1
        elif mutation == "traversal_path":
            row["member_name"] = f"../{row['member_name']}"
        elif mutation == "wrong_task":
            row["member_name"] = row["member_name"].replace(
                "task-reachingandgrasping", "task-freewill", 1
            )
        elif mutation == "duplicate_name":
            core_rows[1]["member_name"] = row["member_name"]
        else:
            raise ValueError("unknown direct source mutation")
    return changed


def _run_direct_refusals(
    base: Mapping[str, Any], *, contract: Mapping[str, Any]
) -> tuple[Counter[str], int, int]:
    counts: Counter[str] = Counter()
    input_bytes = 0
    base_bytes = _source_bytes(base)
    temporary_peak = len(base_bytes)

    contract_mutations: list[dict[str, Any]] = []
    for key, value in (
        ("schema_version", "9.9.9"),
        ("lane_id", "MARC2-VR25X"),
        ("status", "implemented"),
        ("unexpected", True),
        ("fixed_input_bytes", 1),
        ("objective", "changed"),
        ("ordered_validation", []),
        ("fixed_inputs", []),
    ):
        changed = copy.deepcopy(dict(contract))
        changed[key] = value
        contract_mutations.append(changed)
    for key in contract["authorization_state"]:
        changed = copy.deepcopy(dict(contract))
        changed["authorization_state"][key] = True
        contract_mutations.append(changed)
    for key in list(contract["operation_counters"])[:2]:
        changed = copy.deepcopy(dict(contract))
        changed["operation_counters"][key] = 1
        contract_mutations.append(changed)
    for changed in contract_mutations:
        input_bytes += len(_canonical_json_bytes(changed))
        counts[
            _expect_refusal(
                "MARC2VR25A-F01",
                lambda item=changed: _verify_contract_mapping(item),
            )
        ] += 1

    for key in sorted(vr12a.FORBIDDEN_PUBLIC_KEYS):
        report = {key: "forbidden"}
        input_bytes += len(_canonical_json_bytes(report))
        counts[
            _expect_refusal(
                "MARC2VR25A-F03",
                lambda item=report: _assert_public_report_safe(item),
            )
        ] += 1

    for environment_key in THREAD_ENVIRONMENT:
        environment = dict(THREAD_ENVIRONMENT)
        environment[environment_key] = "2"
        input_bytes += len(_canonical_json_bytes(environment))
        counts[
            _expect_refusal(
                "MARC2VR25A-F04",
                lambda item=environment: _validate_thread_environment(item),
            )
        ] += 1

    caps = contract["resource_caps"]
    resource_mutations = (
        (caps["runtime_seconds"] + 1.0, 1, 1, 1, 1),
        (1.0, caps["peak_RSS_bytes"], 1, 1, 1),
        (1.0, 1, caps["temporary_output_bytes"] + 1, 1, 1),
        (1.0, 1, 1, caps["aggregate_output_bytes"] + 1, 1),
        (1.0, 1, 1, 1, caps["generated_input_bytes"] + 1),
    )
    for values in resource_mutations:
        counts[
            _expect_refusal(
                "MARC2VR25A-F04",
                lambda item=values: _assert_resources(
                    runtime_seconds=item[0],
                    peak_rss_bytes=item[1],
                    temporary_output_bytes=item[2],
                    aggregate_output_bytes=item[3],
                    generated_input_bytes=item[4],
                    contract=contract,
                ),
            )
        ] += 1

    source_routes = {
        "schema_name": "MARC2VR25A-R3",
        "schema_version": "MARC2VR25A-R3",
        "proof_posture": "MARC2VR25A-R3",
        "source_identity": "MARC2VR25A-R3",
        "transport_body_sha256": "MARC2VR25A-R3",
        "empty_entries": "MARC2VR25A-R3",
        "row_field_added": "MARC2VR25A-R3",
        "encrypted_row": "MARC2VR25A-R3",
        "traversal_path": "MARC2VR25A-R3",
        "wrong_task": "MARC2VR25A-R3",
        "duplicate_name": "MARC2VR25A-R3",
        "eligible_bundle_removed": "MARC2VR25A-R1",
        "eligible_bundle_added": "MARC2VR25A-R1",
        "eligible_distribution_shift": "MARC2VR25A-R1",
        "unknown_participant_bundle": "MARC2VR25A-R2",
        "incomplete_companion_set": "MARC2VR25A-R3",
    }
    for mutation, route in source_routes.items():
        changed = _mutated_source(base, mutation)
        changed_bytes = _source_bytes(changed)
        input_bytes += len(changed_bytes)
        temporary_peak = max(temporary_peak, len(base_bytes) + len(changed_bytes))
        counts[
            _expect_refusal(
                route,
                lambda item=changed: apply_selection_boundary_firewall(
                    item, contract=contract
                ),
            )
        ] += 1
    if sum(counts.values()) != 72:
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F02", "direct refusal count differs"
        )
    return counts, input_bytes, temporary_peak


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the registered generated matrix once and return an aggregate report."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment()
    expected_counts = Counter(
        registered["generated_witness_matrix"]["expected_route_counts"]
    )
    route_counts: Counter[str] = Counter()
    generated_input_bytes = 0
    temporary_peak = 0
    replay_signatures: list[list[tuple[str, str, str, bool]]] = []
    accepted_identity: tuple[str, str, int, int, int, int] | None = None
    source_immutability_checks = 0
    for _replay in range(REPLAYS):
        replay_signature: list[tuple[str, str, str, bool]] = []
        for case in CASES:
            for order in ORDERS:
                source = build_generated_case(case, order)
                before = _source_bytes(source)
                generated_input_bytes += len(before)
                temporary_peak = max(temporary_peak, len(before) * 2)
                route, outcome = _route_case(source, contract=registered)
                if route != EXPECTED_CASE_ROUTES[case]:
                    raise SelectionBoundaryFirewallRefusal(
                        "MARC2VR25A-F02", "generated witness route differs"
                    )
                if _source_bytes(source) != before:
                    raise SelectionBoundaryFirewallRefusal(
                        "MARC2VR25A-F02", "generated witness source changed"
                    )
                source_immutability_checks += 1
                compatibility = bool(
                    outcome
                    and outcome.full_source_bundle_count_matches_public
                )
                replay_signature.append((case, order, route, compatibility))
                route_counts[route] += 1
                if outcome is not None:
                    current_identity = (
                        outcome.semantic_sha256,
                        outcome.source_exact_selected_names_sha256,
                        outcome.selection.cohort_summary["selected_subjects"],
                        outcome.selection.split_summary["selected_run_bundles"],
                        outcome.selection.split_summary["selected_core_members"],
                        outcome.selection.byte_summary[
                            "selected_reservation_bytes"
                        ],
                    )
                    if accepted_identity is None:
                        accepted_identity = current_identity
                    elif accepted_identity != current_identity:
                        raise SelectionBoundaryFirewallRefusal(
                            "MARC2VR25A-R4", "accepted selection identity differs"
                        )
        replay_signatures.append(replay_signature)
    if (
        replay_signatures[0] != replay_signatures[1]
        or route_counts != expected_counts
        or accepted_identity is None
        or source_immutability_checks != 40
    ):
        raise SelectionBoundaryFirewallRefusal(
            "MARC2VR25A-F02", "matrix replay or route distribution differs"
        )
    base = build_generated_case("exact_public_control", "canonical")
    refusals, refusal_input, refusal_peak = _run_direct_refusals(
        base, contract=registered
    )
    generated_input_bytes += refusal_input
    temporary_peak = max(temporary_peak, refusal_peak)
    runtime = clock() - started
    rss = peak_rss()
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": "MARC2VR25A-G1",
        "status": "generated_only_qualified_no_private_access",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
        },
        "matrix": {
            "paths": 40,
            "cases": 10,
            "orders": 2,
            "replays": 2,
            "route_counts": dict(sorted(route_counts.items())),
            "accepted_paths": 20,
            "accepted_semantic_identity_matches": True,
            "accepted_source_exact_name_identity_matches": True,
            "accepted_split_reservation_identity_matches": True,
            "source_immutability_checks": source_immutability_checks,
            "eligible_drift_successes": 0,
            "unknown_participant_successes": 0,
            "incomplete_companion_successes": 0,
            "exact_replays_match": True,
        },
        "firewall": {
            "all_rows_validated_before_filter": True,
            "all_recognized_bundles_complete_before_filter": True,
            "exact_eligible_bundle_total": 195,
            "exact_eligible_distribution_required": True,
            "known_ineligible_quarantined_before_candidate_construction": True,
            "public_full_total_exposed_as_boolean_only": True,
            "observed_full_total_exposed": False,
            "difference_direction_or_magnitude_exposed": False,
            "selected_subjects": 16,
            "selected_run_bundles": 96,
            "selected_core_members": 384,
        },
        "refusals": {
            "direct_refusals": sum(refusals.values()),
            "route_counts": dict(sorted(refusals.items())),
        },
        "measurements": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "temporary_peak_bytes": temporary_peak,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
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
        "operation_counters": dict(registered["operation_counters"]),
        "warnings": [
            "generated_fixture_only_no_private_or_real_source_access",
            "full_source_238_compatibility_is_warning_only_after_exact_eligibility",
            "observed_private_bundle_count_and_difference_are_unavailable",
            "no_real_cohort_archive_member_neural_payload_or_scientific_result",
        ],
        "unavailable_fields": [
            "observed_real_complete_bundle_count",
            "real_bundle_count_difference_direction_or_magnitude",
            "real_target_free_cohort",
            "archive_member_integrity",
            "neural_signal_event_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": registered["claim_boundary"],
    }
    output_bytes = -1
    while report["measurements"]["aggregate_output_bytes"] != output_bytes:
        report["measurements"]["aggregate_output_bytes"] = output_bytes
        output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_public_report_safe(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        temporary_output_bytes=temporary_peak,
        aggregate_output_bytes=output_bytes,
        generated_input_bytes=generated_input_bytes,
        contract=registered,
    )
    return report


def build_plan() -> dict[str, Any]:
    """Return the fixed generated-only plan with no private authority."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "fixed_input_bytes": _verify_fixed_inputs(contract),
        "cases": 10,
        "orders": 2,
        "replays": 2,
        "paths": 40,
        "direct_refusal_minimum": 72,
        "private_access_authorized": False,
        "real_cohort_freeze_authorized": False,
        "FW2_or_CIL1_authorized": False,
        "execute_surface_available": False,
        "claim_boundary": contract["claim_boundary"],
    }


def build_inspection() -> dict[str, Any]:
    """Return the aggregate contract boundary without running qualification."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    layers = contract["selection_boundary_layers"]
    return {
        "lane_id": LANE_ID,
        "status": "registered_generated_only",
        "source_inventory_rows": layers["source_inventory_rows"],
        "regular_file_rows": layers["regular_file_rows"],
        "directory_rows": layers["directory_rows"],
        "eligible_bundle_total": layers["eligible_bundle_total"],
        "selected_subjects": layers["selected_subjects"],
        "selected_run_bundles": layers["selected_run_bundles"],
        "selected_core_members": layers["selected_core_members"],
        "full_source_bundle_count_matches_public_field": (
            contract["aggregate_output_firewall"]["count_compatibility_field"]
        ),
        "observed_bundle_count_available": False,
        "private_access_authorized": False,
        "execute_surface_available": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 selection-boundary firewall."
    )
    parser.add_argument("command", choices=("plan", "qualify", "inspect"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "plan":
            payload = build_plan()
        elif args.command == "inspect":
            payload = build_inspection()
        else:
            payload = qualify_generated()
    except SelectionBoundaryFirewallRefusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "status": "refused"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
