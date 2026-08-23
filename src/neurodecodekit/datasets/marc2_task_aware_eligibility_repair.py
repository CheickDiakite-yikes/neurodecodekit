"""Generated-only task-aware MARC2 eligibility and selection repair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import resource
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a
from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a
from neurodecodekit.datasets import marc2_source_validity_eligibility_repair as repair


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR35A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_task_aware_eligibility_repair_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_task_aware_eligibility_repair_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_task_aware_eligibility_repair_contract.v0.json"
)
CONTRACT_SHA256 = "b801d9f1db51d7b6053f22bebd2d8dcda9e4987cbb242cf4f19b69f72fc46823"
GREEN_REGISTRATION_COMMIT = "aa4c39a5ce8ca04627c9252600971ee878f20e3e"
GREEN_REGISTRATION_CI_RUN_ID = 32_643_351_246
GREEN_REGISTRATION_BASE_JOB_ID = 97_203_738_713
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_203_738_637
PUBLISHED_TASK = "reachingandgrasping"
EXPECTED_ELIGIBLE_TOTAL = 195
SUCCESS_ROUTES = ("MARC2VR35A-G1", "MARC2VR35A-G2")
DIAGNOSTIC_ROUTES = (
    "MARC2VR35A-R1",
    "MARC2VR35A-R2",
    "MARC2VR35A-R3",
)
REFUSAL_ROUTES = tuple(f"MARC2VR35A-F{index:02d}" for index in range(1, 7))
CASES = (
    "baseline_exact_task_exact_total",
    "mixed_task_surplus",
    "target_task_surplus",
    "target_task_deficit",
    "selection_or_task_firewall_refusal",
)
ORDERS = ("canonical", "reversed")
REPLAYS = 2
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
    "selected_rows",
    "selection_identity",
    "source_exact_name",
    "source_path",
    "subject_id",
    "target_text",
    "target_value",
    "task_distribution",
}


class TaskAwareEligibilityRepairRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR35A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in (*DIAGNOSTIC_ROUTES, *REFUSAL_ROUTES):
            raise ValueError("unknown MARC2-VR35A route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class TaskAwareSelection:
    """Generated selection plus comparison-only aggregate hashes."""

    selection: selector.SelectionResult
    route: str
    source_sha256: str
    semantic_sha256: str
    source_exact_selected_names_sha256: str
    task_blind_surplus_removed: bool


TaskRunKey = tuple[str, str, str, int]
RunKey = tuple[str, str, int]
TaskGroupedRuns = dict[TaskRunKey, dict[str, Mapping[str, Any]]]
GroupedRuns = dict[RunKey, dict[str, Mapping[str, Any]]]


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
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR35A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract schema differs"
        )
    return payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    registered = load_registered_contract()
    repair_contract = contract.get("repair_contract", {})
    implementation = contract.get("implementation_contract", {})
    resources = contract.get("resource_limits", {})
    matrix = contract.get("generated_matrix", {})
    if (
        not isinstance(contract, dict)
        or contract != registered
        or contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "preregistered_artifact_only_generated_only_no_private_access"
        or repair_contract.get("published_task_label") != PUBLISHED_TASK
        or repair_contract.get("exact_projected_eligible_run_bundles")
        != EXPECTED_ELIGIBLE_TOTAL
        or repair_contract.get("non_target_task_bundle_may_enter_selection")
        is not False
        or repair_contract.get("source_mutation_allowed") is not False
        or implementation.get("commands") != ["plan", "qualify"]
        or implementation.get("private_executor_allowed") is not False
        or resources.get("CPU_threads") != 1
        or resources.get("workers") != 1
        or resources.get("numerical_jobs") != 1
        or resources.get("retained_output_bytes") != 0
        or resources.get("network_bytes") != 0
        or resources.get("new_payload_bytes") != 0
        or matrix.get("required_paths") != 20
        or matrix.get("minimum_direct_refusals", 0) < 80
    ):
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "aa4c39a5ce8ca04627c9252600971ee878f20e3e"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_643_351_246
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_203_738_713
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_203_738_637
    ):
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _verify_fixed_inputs(contract: Mapping[str, Any], root: Path | None = None) -> int:
    fixed_root = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 11:
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "fixed input registry differs"
        )
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise TaskAwareEligibilityRepairRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (fixed_root / str(row["path"])).read_bytes()
        except (KeyError, OSError) as exc:
            raise TaskAwareEligibilityRepairRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row.get("bytes") or _sha256_bytes(payload) != row.get(
            "sha256"
        ):
            raise TaskAwareEligibilityRepairRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _source_bytes(source: Mapping[str, Any]) -> bytes:
    try:
        return vr2._canonical_source_bytes(source)
    except (TypeError, ValueError) as exc:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "source is not canonical"
        ) from exc


def _validate_task_aware_entry(
    row: Any,
) -> tuple[str, re.Match[str] | None]:
    if not isinstance(row, dict) or set(row) != selector.ENTRY_FIELDS:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "source row fields differ"
        )
    try:
        name = selector._normalize_member_name(row["member_name"])
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "source member path differs"
        ) from exc
    match = vr20a._core_match(name)
    if match is None:
        try:
            validated_name, _ = vr20a.vr12a._validate_repaired_entry(row)
        except vr20a.vr12a.P15RunIndexRepairRefusal as exc:
            raise TaskAwareEligibilityRepairRefusal(
                DIAGNOSTIC_ROUTES[2], "suffix-bearing identity differs"
            ) from exc
        return validated_name, None
    task = match.group("task")
    if not task.isascii() or re.fullmatch(r"[a-z0-9]+", task) is None:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "task token is not exact lowercase ASCII"
        )
    projected = copy.deepcopy(row)
    projected["member_name"] = vr20a._schema_projection(name, match)
    try:
        vr20a.vr12a._validate_repaired_entry(projected)
    except vr20a.vr12a.P15RunIndexRepairRefusal as exc:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "core row schema or identity differs"
        ) from exc
    return name, match


def _group_task_rows(
    entries: Sequence[Any],
) -> tuple[TaskGroupedRuns, Counter[str]]:
    names: set[str] = set()
    kinds: Counter[str] = Counter()
    grouped: dict[TaskRunKey, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    run_tokens: dict[TaskRunKey, str] = {}
    for row in entries:
        name, match = _validate_task_aware_entry(row)
        if name in names:
            raise TaskAwareEligibilityRepairRefusal(
                DIAGNOSTIC_ROUTES[2], "source full member name is duplicated"
            )
        names.add(name)
        kinds[row["entry_kind"]] += 1
        if match is None:
            continue
        key = (
            match.group("subject"),
            match.group("session"),
            match.group("task"),
            vr20a._semantic_run(match.group("run")),
        )
        run = match.group("run")
        if run_tokens.setdefault(key, run) != run:
            raise TaskAwareEligibilityRepairRefusal(
                DIAGNOSTIC_ROUTES[2], "companion run spelling differs"
            )
        suffix = match.group("suffix")
        if suffix in grouped[key]:
            raise TaskAwareEligibilityRepairRefusal(
                DIAGNOSTIC_ROUTES[2], "normalized companion is duplicated"
            )
        grouped[key][suffix] = row
    if any(
        set(companions) != set(selector.REQUIRED_SUFFIXES)
        for companions in grouped.values()
    ):
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "task-aware companion set is incomplete"
        )
    return dict(grouped), kinds


def _project_published_task(grouped: TaskGroupedRuns) -> GroupedRuns:
    projected: GroupedRuns = {}
    for (subject, session, task, run), companions in grouped.items():
        if task != PUBLISHED_TASK:
            continue
        key = (subject, session, run)
        if key in projected:
            raise TaskAwareEligibilityRepairRefusal(
                DIAGNOSTIC_ROUTES[2], "projected task identity is duplicated"
            )
        projected[key] = companions
    return projected


def _classify(
    grouped: Mapping[tuple[str, ...], Mapping[str, Mapping[str, Any]]],
    vr2_contract: Mapping[str, Any],
) -> dict[tuple[str, ...], str]:
    labels: dict[tuple[str, ...], str] = {}
    try:
        for key in grouped:
            subject, session, run = key[0], key[1], key[-1]
            labels[key] = vr2._classify_key(
                (str(subject), str(session), int(run)), vr2_contract
            )
    except (TypeError, ValueError, vr2.LiveDomainEligibilityRefusal) as exc:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "participant or session taxonomy differs"
        ) from exc
    return labels


def adapt_task_aware_source(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    vr2_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> TaskAwareSelection:
    """Project the exact task before eligibility arithmetic and selection."""

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
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "live source envelope differs"
        ) from exc
    grouped, kinds = _group_task_rows(entries)
    domain = registered_vr2["generated_live_source_domain"]
    if kinds != Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    ):
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "source entry-kind arithmetic differs"
        )
    projected = _project_published_task(grouped)
    labels = _classify(projected, registered_vr2)
    eligible_total = sum(
        label == vr2.PREDICATE_CODES[0] for label in labels.values()
    )
    if eligible_total > EXPECTED_ELIGIBLE_TOTAL:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[0], "projected eligible total is above threshold"
        )
    if eligible_total < EXPECTED_ELIGIBLE_TOTAL:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[1], "projected eligible total is below threshold"
        )
    counts = Counter(labels.values())
    try:
        vr2._assert_classification_arithmetic(counts, registered_vr2)
        filtered = vr2._filter_and_validate_eligible(
            projected, labels, registered_vr2
        )
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "projected eligibility distribution differs"
        ) from exc
    task_blind_labels = _classify(grouped, registered_vr2)
    task_blind_surplus = (
        sum(label == vr2.PREDICATE_CODES[0] for label in task_blind_labels.values())
        > EXPECTED_ELIGIBLE_TOTAL
    )
    if _source_bytes(source) != before:
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[3], "source changed during task-aware projection"
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
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "target-free selection refused"
        ) from exc
    if _source_bytes(source) != before:
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[3], "source changed during selection"
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
        raise TaskAwareEligibilityRepairRefusal(
            DIAGNOSTIC_ROUTES[2], "selection firewall differs"
        ) from exc
    return TaskAwareSelection(
        selection=selection,
        route=SUCCESS_ROUTES[1] if task_blind_surplus else SUCCESS_ROUTES[0],
        source_sha256=source_sha256,
        semantic_sha256=semantic,
        source_exact_selected_names_sha256=names_hash,
        task_blind_surplus_removed=task_blind_surplus,
    )


def _replace_bundle_task(
    source: Mapping[str, Any], key: RunKey, task: str
) -> None:
    for row in vr25a._bundle_rows(source, key):
        name = row["member_name"]
        match = vr20a._core_match(name)
        if match is None:
            raise TaskAwareEligibilityRepairRefusal(
                REFUSAL_ROUTES[1], "generated task witness differs"
            )
        row["member_name"] = vr20a._replace_group(name, match, "task", task)


def build_generated_case(case: str, order: str) -> dict[str, Any]:
    """Build one exact generated VR35A witness without private input."""

    if case not in CASES:
        raise ValueError("unknown generated case")
    if order not in ORDERS:
        raise ValueError("unknown generated row order")
    if case == "baseline_exact_task_exact_total":
        source = vr25a.build_generated_case("exact_public_control", "canonical")
    elif case == "mixed_task_surplus":
        source = vr25a.build_generated_case("eligible_bundle_added", "canonical")
        _replace_bundle_task(source, ("sub-07", "ses-01", 4), "motorimagery")
    elif case == "target_task_surplus":
        source = vr25a.build_generated_case("eligible_bundle_added", "canonical")
    elif case == "target_task_deficit":
        source = vr25a.build_generated_case("eligible_bundle_removed", "canonical")
    else:
        source = vr25a.build_generated_case("exact_public_control", "canonical")
        row = vr25a._bundle_rows(source, ("sub-01", "ses-01", 1))[0]
        name = row["member_name"]
        match = vr20a._core_match(name)
        assert match is not None
        row["member_name"] = vr20a._replace_group(
            name, match, "task", "motorimagery"
        )
    source["entries"] = sorted(source["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        source["entries"].reverse()
    return source


def _route_case(
    source: Mapping[str, Any], *, contract: Mapping[str, Any] | None = None
) -> tuple[str, TaskAwareSelection | None]:
    try:
        outcome = adapt_task_aware_source(source, contract=contract)
    except TaskAwareEligibilityRepairRefusal as exc:
        if exc.route not in DIAGNOSTIC_ROUTES:
            raise
        return exc.route, None
    return outcome.route, outcome


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise TaskAwareEligibilityRepairRefusal(
                    REFUSAL_ROUTES[4], "aggregate report contains forbidden field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1_048_576:
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[4], "aggregate report exceeds output cap"
        )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    aggregate_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    limits = contract["resource_limits"]
    if (
        runtime_seconds < 0
        or runtime_seconds > limits["runtime_seconds"]
        or peak_rss_bytes < 0
        or peak_rss_bytes >= limits["peak_RSS_bytes_exclusive"]
        or generated_input_bytes > limits["generated_input_bytes"]
        or aggregate_output_bytes > limits["aggregate_output_bytes"]
    ):
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(expected_route: str, action: Callable[[], Any]) -> str:
    try:
        action()
    except TaskAwareEligibilityRepairRefusal as exc:
        if exc.route != expected_route:
            raise TaskAwareEligibilityRepairRefusal(
                REFUSAL_ROUTES[2], "direct refusal route differs"
            ) from exc
        return exc.route
    raise TaskAwareEligibilityRepairRefusal(
        REFUSAL_ROUTES[2], "direct mutation unexpectedly passed"
    )


def _contract_mutations(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []
    paths: list[tuple[str, ...]] = [
        ("schema_name",),
        ("schema_version",),
        ("lane_id",),
        ("status",),
        ("objective",),
        ("fixed_input_count",),
        ("fixed_input_bytes",),
    ]
    paths.extend(("authorization", key) for key in contract["authorization"])
    paths.extend(
        ("registration_operation_counters", key)
        for key in contract["registration_operation_counters"]
    )
    paths.extend(("repair_contract", key) for key in contract["repair_contract"])
    paths.extend(("resource_limits", key) for key in contract["resource_limits"])
    paths.extend(("implementation_contract", key) for key in contract["implementation_contract"])
    for path in paths:
        changed = copy.deepcopy(dict(contract))
        cursor: dict[str, Any] = changed
        for key in path[:-1]:
            cursor = cursor[key]
        value = cursor[path[-1]]
        if isinstance(value, bool):
            cursor[path[-1]] = not value
        elif isinstance(value, int):
            cursor[path[-1]] = value + 1
        elif isinstance(value, list):
            cursor[path[-1]] = [*value, "changed"]
        elif isinstance(value, dict):
            cursor[path[-1]] = {**value, "unexpected": True}
        else:
            cursor[path[-1]] = "changed"
        mutations.append(changed)
    return mutations


def _run_direct_refusals(contract: Mapping[str, Any]) -> Counter[str]:
    routes: Counter[str] = Counter()
    for changed in _contract_mutations(contract):
        routes[_expect_refusal(REFUSAL_ROUTES[0], lambda item=changed: _verify_contract_mapping(item))] += 1

    base = build_generated_case(CASES[0], "canonical")
    source_mutations: list[dict[str, Any]] = []
    for field in ("schema_name", "schema_version", "proof_posture", "source_identity"):
        changed = copy.deepcopy(base)
        changed[field] = "changed"
        source_mutations.append(changed)
    changed = copy.deepcopy(base)
    changed["entries"][0]["unexpected"] = True
    source_mutations.append(changed)
    changed = copy.deepcopy(base)
    first = next(
        row
        for row in changed["entries"]
        if vr20a._core_match(row.get("member_name", "")) is not None
    )
    match = vr20a._core_match(first["member_name"])
    assert match is not None
    first["member_name"] = vr20a._replace_group(
        first["member_name"], match, "task", "MotorImagery"
    )
    source_mutations.append(changed)
    for changed in source_mutations:
        route, _ = _route_case(changed, contract=contract)
        if route != DIAGNOSTIC_ROUTES[2]:
            raise TaskAwareEligibilityRepairRefusal(
                REFUSAL_ROUTES[2], "source mutation route differs"
            )
        routes[route] += 1

    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        routes[
            _expect_refusal(
                REFUSAL_ROUTES[4],
                lambda value=key: _assert_public_report_safe({value: "forbidden"}),
            )
        ] += 1

    limits = contract["resource_limits"]
    resource_mutations = (
        (limits["runtime_seconds"] + 1.0, 1, 1, 1),
        (1.0, limits["peak_RSS_bytes_exclusive"], 1, 1),
        (1.0, 1, limits["generated_input_bytes"] + 1, 1),
        (1.0, 1, 1, limits["aggregate_output_bytes"] + 1),
    )
    for runtime_seconds, rss, input_bytes, output_bytes in resource_mutations:
        routes[
            _expect_refusal(
                REFUSAL_ROUTES[5],
                lambda a=runtime_seconds, b=rss, c=input_bytes, d=output_bytes: _assert_resources(
                    runtime_seconds=a,
                    peak_rss_bytes=b,
                    generated_input_bytes=c,
                    aggregate_output_bytes=d,
                    contract=contract,
                ),
            )
        ] += 1
    if sum(routes.values()) < contract["generated_matrix"]["minimum_direct_refusals"]:
        raise TaskAwareEligibilityRepairRefusal(
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
    """Run the sole registered 20-path generated-only VR35A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment(environment)
    refusal_counts = _run_direct_refusals(registered)

    expected_routes = {
        "baseline_exact_task_exact_total": SUCCESS_ROUTES[0],
        "mixed_task_surplus": SUCCESS_ROUTES[1],
        "target_task_surplus": DIAGNOSTIC_ROUTES[0],
        "target_task_deficit": DIAGNOSTIC_ROUTES[1],
        "selection_or_task_firewall_refusal": DIAGNOSTIC_ROUTES[2],
    }
    route_counts: Counter[str] = Counter()
    replay_hashes: dict[str, list[str]] = {
        f"{case}:{order}": [] for case in CASES for order in ORDERS
    }
    semantic_hashes: dict[str, set[str]] = {
        SUCCESS_ROUTES[0]: set(),
        SUCCESS_ROUTES[1]: set(),
    }
    replay_signatures: list[list[tuple[str, str, str]]] = []
    generated_input_bytes = 0
    selection_calls = 0
    selection_validation_calls = 0
    non_target_selected_rows = 0
    for _replay in range(REPLAYS):
        signature: list[tuple[str, str, str]] = []
        for order in ORDERS:
            for case in CASES:
                source = build_generated_case(case, order)
                source_before = _source_bytes(source)
                generated_input_bytes += len(source_before)
                replay_hashes[f"{case}:{order}"].append(
                    _sha256_bytes(source_before)
                )
                route, outcome = _route_case(source, contract=registered)
                if route != expected_routes[case] or _source_bytes(source) != source_before:
                    raise TaskAwareEligibilityRepairRefusal(
                        REFUSAL_ROUTES[3], "generated route or immutability differs"
                    )
                if outcome is not None:
                    selection_calls += 1
                    selection_validation_calls += 1
                    semantic_hashes[route].add(outcome.semantic_sha256)
                    for row in outcome.selection.private_manifest["rows"]:
                        match = vr20a._core_match(row["member_name"])
                        if match is None or match.group("task") != PUBLISHED_TASK:
                            non_target_selected_rows += 1
                route_counts[route] += 1
                signature.append((case, order, route))
        replay_signatures.append(signature)

    matrix = registered["generated_matrix"]
    semantic_identity_matches = (
        len(semantic_hashes[SUCCESS_ROUTES[0]]) == 1
        and semantic_hashes[SUCCESS_ROUTES[0]]
        == semantic_hashes[SUCCESS_ROUTES[1]]
    )
    if (
        route_counts != Counter(matrix["expected_route_counts"])
        or selection_calls != matrix["successful_selection_calls"]
        or selection_validation_calls
        != matrix["successful_selection_validation_calls"]
        or non_target_selected_rows != matrix["non_target_selected_rows"]
        or replay_signatures[0] != replay_signatures[1]
        or any(len(set(values)) != 1 for values in replay_hashes.values())
        or not semantic_identity_matches
    ):
        raise TaskAwareEligibilityRepairRefusal(
            REFUSAL_ROUTES[3], "generated matrix acceptance gate differs"
        )

    runtime = clock() - started
    rss = peak_rss()
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_task_aware_repair_qualified_no_private_access",
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
            "selection_calls": selection_calls,
            "selection_validation_calls": selection_validation_calls,
            "mixed_task_semantic_cohort_matches_baseline": semantic_identity_matches,
            "non_target_selected_rows": non_target_selected_rows,
            "exact_replays_match": True,
            "source_immutability_checks": sum(route_counts.values()),
        },
        "repair": {
            "published_task": PUBLISHED_TASK,
            "task_projection_precedes_eligibility_arithmetic": True,
            "mixed_task_surplus_removed": True,
            "genuine_target_task_surplus_distinguished": True,
            "genuine_target_task_deficit_distinguished": True,
            "unchanged_rank_prefix_split_and_storage_selector": True,
            "source_exact_selected_names_required": True,
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
        "operation_counters": dict(registered["registration_operation_counters"]),
        "warnings": [
            "generated_fixture_only_no_private_or_real_source_access",
            "mixed_task_surplus_is_compatible_with_VR34P_R2_but_not_proven_as_its_private_cause",
            "no_real_cohort_archive_member_neural_payload_or_scientific_result",
        ],
        "unavailable_fields": [
            "private_total_or_difference",
            "private_task_distribution",
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
        generated_input_bytes=generated_input_bytes,
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
        "direct_refusal_minimum": contract["generated_matrix"][
            "minimum_direct_refusals"
        ],
        "published_task": PUBLISHED_TASK,
        "private_access_authorized": False,
        "real_cohort_freeze_authorized": False,
        "FW2_or_CIL1_authorized": False,
        "execute_surface_available": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 task-aware eligibility repair."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = build_plan() if args.command == "plan" else qualify_generated()
    except TaskAwareEligibilityRepairRefusal as exc:
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
