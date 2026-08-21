"""Generated-only MARC2 variable-width run-index repair."""

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

from neurodecodekit.datasets import marc2_dynamic_live_selection as vr6
from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import marc2_p15_run_index_repair as vr12a
from neurodecodekit.datasets import marc2_source_validity_eligibility_repair as repair


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR16A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_variable_width_run_index_repair_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_variable_width_run_index_repair_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_variable_width_run_index_repair_contract.v0.json"
)
CONTRACT_SHA256 = "308b80864553fd12a7bda7e4691aea35c63eebfbd651c7ed86ebc15e2fd41dec"
GREEN_REGISTRATION_COMMIT = "7dba59355ca45c8ab5eafb9d8b7757edfc9755c5"
GREEN_REGISTRATION_CI_RUN_ID = 32_458_280_634
GREEN_REGISTRATION_BASE_JOB_ID = 96_699_811_237
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 96_699_811_051
SUCCESS_ROUTE = "MARC2VR16A-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR16A-F{index:02d}" for index in range(1, 10))
VARIANTS = (
    "unpadded",
    "two_digit_control",
    "three_digit",
    "six_digit",
    "sixty_four_digit",
    "bundle_consistent_mixed_width",
)
ORDERS = ("canonical", "reversed")
REPLAYS = 2
WIDTHS = {
    "unpadded": 1,
    "two_digit_control": 2,
    "three_digit": 3,
    "six_digit": 6,
    "sixty_four_digit": 64,
}
MIXED_WIDTHS = (1, 2, 3, 6, 64)
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
VARIABLE_CORE_MEMBER_RE = re.compile(
    r"(?:[A-Za-z0-9._-]+/)*"
    r"(?P<subject>sub-[0-9]{2})/(?P<session>ses-[0-9]{2})/eeg/"
    r"(?P=subject)_(?P=session)_task-(?P<task>[A-Za-z0-9]+)"
    r"(?:_[A-Za-z0-9]+-[A-Za-z0-9]+)*_run-(?P<run>[0-9]+)"
    r"(?P<suffix>_eeg\.eeg|_eeg\.vhdr|_eeg\.vmrk|_events\.tsv)\Z"
)


class VariableWidthRunIndexRepairRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR16A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR16A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class VariableWidthSelection:
    """Generated selection plus aggregate-safe deterministic hashes."""

    selection: selector.SelectionResult
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
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        data = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(data) != CONTRACT_SHA256:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return data


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR16A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract schema differs"
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
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "7dba59355ca45c8ab5eafb9d8b7757edfc9755c5"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_458_280_634
        or GREEN_REGISTRATION_BASE_JOB_ID != 96_699_811_237
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 96_699_811_051
    ):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _verify_fixed_inputs(contract: Mapping[str, Any], root: Path | None = None) -> int:
    fixed_root = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 8:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "fixed input registry differs"
        )
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (fixed_root / str(row["path"])).read_bytes()
        except (KeyError, OSError) as exc:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row.get("bytes") or _sha256_bytes(payload) != row.get(
            "sha256"
        ):
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _variable_core_match(name: str) -> re.Match[str] | None:
    return VARIABLE_CORE_MEMBER_RE.fullmatch(name)


def _canonical_run_token(token: str) -> str:
    if not token or re.fullmatch(r"[0-9]+", token) is None:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "run token is not ASCII numeric"
        )
    return token.lstrip("0") or "0"


def _semantic_run(token: str) -> int:
    canonical = _canonical_run_token(token)
    return int(canonical)


def _replace_match_run(name: str, match: re.Match[str], token: str) -> str:
    start, end = match.span("run")
    return f"{name[:start]}{token}{name[end:]}"


def _validate_variable_entry(row: Any) -> tuple[str, re.Match[str] | None]:
    if not isinstance(row, dict) or set(row) != selector.ENTRY_FIELDS:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source row fields differ"
        )
    try:
        name = selector._normalize_member_name(row["member_name"])
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source member path differs"
        ) from exc
    match = _variable_core_match(name)
    if match is None:
        try:
            validated_name, _ = vr12a._validate_repaired_entry(row)
        except vr12a.P15RunIndexRepairRefusal as exc:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[2], "suffix-bearing identity differs"
            ) from exc
        return validated_name, None
    canonical = _canonical_run_token(match.group("run"))
    normalized = copy.deepcopy(row)
    normalized["member_name"] = _replace_match_run(
        name, match, f"{int(canonical):02d}" if canonical in {"1", "2", "3"} else "04"
    )
    try:
        vr12a._validate_repaired_entry(normalized)
    except vr12a.P15RunIndexRepairRefusal as exc:
        route = REFUSAL_ROUTES[3] if match.group("task") != "freewill" else REFUSAL_ROUTES[2]
        raise VariableWidthRunIndexRepairRefusal(route, "core identity differs") from exc
    if match.group("task") != "freewill":
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[3], "Freewill task differs"
        )
    return name, match


def _group_variable_rows(
    entries: Sequence[Any],
) -> tuple[dict[tuple[str, str, int], dict[str, Mapping[str, Any]]], Counter[str]]:
    names: set[str] = set()
    kinds: Counter[str] = Counter()
    grouped: dict[tuple[str, str, int], dict[str, Mapping[str, Any]]] = defaultdict(
        dict
    )
    run_tokens: dict[tuple[str, str, int], str] = {}
    for row in entries:
        name, match = _validate_variable_entry(row)
        if name in names:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[2], "source full member name is duplicated"
            )
        names.add(name)
        kinds[row["entry_kind"]] += 1
        if match is None:
            continue
        key = (
            match.group("subject"),
            match.group("session"),
            _semantic_run(match.group("run")),
        )
        token = match.group("run")
        previous = run_tokens.setdefault(key, token)
        if previous != token:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[4], "companion run spelling differs"
            )
        suffix = match.group("suffix")
        if suffix in grouped[key]:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[4], "normalized run companion is duplicated"
            )
        grouped[key][suffix] = row
    if any(
        set(companions) != set(selector.REQUIRED_SUFFIXES)
        for companions in grouped.values()
    ):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[4], "run companion set is incomplete"
        )
    return dict(grouped), kinds


def _validate_and_filter(
    source: Mapping[str, Any],
    *,
    vr2_contract: Mapping[str, Any],
) -> tuple[dict[tuple[str, str, int], dict[str, Mapping[str, Any]]], str]:
    try:
        vr2._verify_contract_mapping(vr2_contract)
        entries = vr2._validate_live_envelope(source, vr2_contract)
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[1], "live source envelope differs"
        ) from exc
    grouped, kinds = _group_variable_rows(entries)
    domain = vr2_contract["generated_live_source_domain"]
    if kinds != Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    ) or len(grouped) != domain["complete_source_run_bundles"]:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[5], "source kind or run-bundle total differs"
        )
    labels: dict[tuple[str, str, int], str] = {}
    counts: Counter[str] = Counter()
    try:
        for key in grouped:
            label = vr2._classify_key(key, vr2_contract)
            labels[key] = label
            counts[label] += 1
        vr2._assert_classification_arithmetic(counts, vr2_contract)
        filtered = vr2._filter_and_validate_eligible(grouped, labels, vr2_contract)
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[5], "source taxonomy or eligibility differs"
        ) from exc
    return filtered, _sha256_bytes(vr2._canonical_source_bytes(source))


def _semantic_identity(selection: selector.SelectionResult) -> dict[str, Any]:
    bundles: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    for row in selection.private_manifest["rows"]:
        match = _variable_core_match(row["member_name"])
        if match is None:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[6], "selected row identity differs"
            )
        bundles[
            (
                match.group("subject"),
                match.group("session"),
                _semantic_run(match.group("run")),
            )
        ].add(match.group("suffix"))
    return {
        "selected_subject_ids": list(selection.cohort_summary["selected_subject_ids"]),
        "selected_subject_count": selection.cohort_summary["selected_subjects"],
        "fit_session": selection.split_summary["fit_session"],
        "heldout_session": selection.split_summary["heldout_session"],
        "logical_bundles": [
            [subject, session, run, sorted(suffixes)]
            for (subject, session, run), suffixes in sorted(bundles.items())
        ],
        "selected_core_members": selection.split_summary["selected_core_members"],
    }


def _validate_variable_selection(
    selection: selector.SelectionResult,
    *,
    filtered_keys: set[tuple[str, str, int]],
    source_names: set[str],
    selector_contract: Mapping[str, Any],
) -> tuple[str, str, int]:
    try:
        rank = selector._validate_rank(selector_contract)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "selector rank differs"
        ) from exc
    cohort = selection.cohort_summary
    split = selection.split_summary
    byte_summary = selection.byte_summary
    subjects = cohort.get("selected_subject_ids")
    if not isinstance(subjects, list):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "selected subject prefix differs"
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
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "cohort or split arithmetic differs"
        )
    rows = selection.private_manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != count * 24:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "selected structural rows differ"
        )
    try:
        vr6._walk_scientific_firewall(selection.private_manifest)
    except vr6.DynamicLiveSelectionRefusal as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "scientific firewall refused"
        ) from exc
    names: set[str] = set()
    tokens: dict[tuple[str, str, int], str] = {}
    suffixes: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    measured_reservation = 0
    for row in rows:
        name = row.get("member_name")
        match = _variable_core_match(name) if isinstance(name, str) else None
        if match is None:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[6], "selected source-exact name differs"
            )
        key = (
            match.group("subject"),
            match.group("session"),
            _semantic_run(match.group("run")),
        )
        token = match.group("run")
        previous = tokens.setdefault(key, token)
        expected_reservation = selector._reservation_bytes(row)
        if (
            name not in source_names
            or name in names
            or key not in filtered_keys
            or previous != token
            or row.get("subject_id") != key[0]
            or row.get("session_id") != key[1]
            or row.get("run_id") != f"run-{key[2]:02d}"
            or row.get("split_role")
            != ("fit" if key[1] == "ses-01" else "heldout")
            or key[2] not in {1, 2, 3}
            or row.get("reservation_bytes") != expected_reservation
        ):
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[6], "selected row identity or reservation differs"
            )
        names.add(name)
        suffixes[key].add(match.group("suffix"))
        measured_reservation += expected_reservation
    if (
        len(suffixes) != count * 6
        or any(values != set(selector.REQUIRED_SUFFIXES) for values in suffixes.values())
        or measured_reservation != byte_summary.get("selected_reservation_bytes")
        or byte_summary.get("reservation_cap_bytes") != selector.RESERVATION_CAP_BYTES
        or measured_reservation > selector.RESERVATION_CAP_BYTES
    ):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "selected companion or storage arithmetic differs"
        )
    semantic = _sha256_bytes(_canonical_json_bytes(_semantic_identity(selection)))
    names_hash = _sha256_bytes(_canonical_json_bytes(sorted(names)))
    return semantic, names_hash, measured_reservation


def adapt_variable_width_source(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    vr2_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> VariableWidthSelection:
    """Select one generated source through the variable-width adapter."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    _verify_fixed_inputs(registered)
    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    before = vr2._canonical_source_bytes(source)
    filtered, source_sha256 = _validate_and_filter(
        source, vr2_contract=registered_vr2
    )
    if vr2._canonical_source_bytes(source) != before:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "source changed during variable-width validation"
        )
    try:
        selection = repair._select_from_filtered(
            filtered, source_sha256, frozen_selector
        )
    except (repair.SourceValidityEligibilityRefusal, selector.FreewillPrefixSelectionRefusal) as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "dynamic selection refused"
        ) from exc
    if vr2._canonical_source_bytes(source) != before:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "source changed during variable-width selection"
        )
    source_names = {
        row["member_name"]
        for row in source["entries"]
        if isinstance(row, dict) and isinstance(row.get("member_name"), str)
    }
    semantic, names_hash, _ = _validate_variable_selection(
        selection,
        filtered_keys=set(filtered),
        source_names=source_names,
        selector_contract=frozen_selector,
    )
    return VariableWidthSelection(
        selection=selection,
        source_sha256=source_sha256,
        semantic_sha256=semantic,
        source_exact_selected_names_sha256=names_hash,
    )


def _variant_width(variant: str, match: re.Match[str]) -> int:
    if variant in WIDTHS:
        return WIDTHS[variant]
    if variant == "bundle_consistent_mixed_width":
        seed = (
            int(match.group("subject")[4:])
            + int(match.group("session")[4:])
            + int(match.group("run"))
        )
        return MIXED_WIDTHS[seed % len(MIXED_WIDTHS)]
    raise ValueError("unknown generated spelling variant")


def _rewrite_variant(source: dict[str, Any], variant: str) -> None:
    if variant not in VARIANTS:
        raise ValueError("unknown generated spelling variant")
    for row in source["entries"]:
        if not isinstance(row, dict):
            continue
        name = row.get("member_name")
        match = selector._core_match(name) if isinstance(name, str) else None
        if match is None:
            continue
        width = _variant_width(variant, match)
        token = str(int(match.group("run"))).zfill(width)
        row["member_name"] = _replace_match_run(name, match, token)


def build_generated_variant(
    variant: str,
    order: str,
    *,
    vr2_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one generated 1,227-row variable-width source."""

    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    try:
        source = vr2.build_generated_live_source(
            profile="A", row_order="canonical", contract=registered_vr2
        )
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[1], "generated live source build refused"
        ) from exc
    _rewrite_variant(source, variant)
    source["entries"] = sorted(source["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        source["entries"].reverse()
    elif order != "canonical":
        raise ValueError("unknown generated row order")
    return source


def _first_core(source: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        row
        for row in source["entries"]
        if isinstance(row, dict)
        and isinstance(row.get("member_name"), str)
        and _variable_core_match(row["member_name"]) is not None
    )


def _rows_for_first_bundle(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    first = _first_core(source)
    first_match = _variable_core_match(first["member_name"])
    assert first_match is not None
    key = (
        first_match.group("subject"),
        first_match.group("session"),
        _semantic_run(first_match.group("run")),
    )
    rows = []
    for row in source["entries"]:
        if not isinstance(row, dict) or not isinstance(row.get("member_name"), str):
            continue
        match = _variable_core_match(row["member_name"])
        if match is not None and (
            match.group("subject"),
            match.group("session"),
            _semantic_run(match.group("run")),
        ) == key:
            rows.append(row)
    return rows


def _replace_run_token(name: str, token: str) -> str:
    match = _variable_core_match(name)
    if match is None:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "generated witness source differs"
        )
    return _replace_match_run(name, match, token)


def _mutated_witness(source: Mapping[str, Any], witness: str) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    rows = _rows_for_first_bundle(changed)
    target = rows[0]
    name = target["member_name"]
    if witness == "empty_run_token":
        target["member_name"] = _replace_run_token(name, "")
    elif witness == "signed_run_token":
        target["member_name"] = _replace_run_token(name, "-1")
    elif witness == "decimal_run_token":
        target["member_name"] = _replace_run_token(name, "1.0")
    elif witness == "unicode_digit_run_token":
        target["member_name"] = _replace_run_token(name, "\u0661")
    elif witness == "alphabetic_run_token":
        target["member_name"] = _replace_run_token(name, "one")
    elif witness == "semantic_zero":
        for row in rows:
            row["member_name"] = _replace_run_token(row["member_name"], "000")
    elif witness == "semantic_run_four":
        for row in rows:
            row["member_name"] = _replace_run_token(row["member_name"], "004")
    elif witness == "mixed_lexical_tokens_within_bundle":
        candidate = next(
            row for row in rows if row["member_name"].endswith("_eeg.vhdr")
        )
        candidate["member_name"] = _replace_run_token(candidate["member_name"], "1")
    elif witness == "duplicate_normalized_run_companion":
        auxiliary = next(
            row
            for row in changed["entries"]
            if row["entry_kind"] == "regular_file"
            and _variable_core_match(row["member_name"]) is None
            and not any(
                row["member_name"].endswith(suffix)
                for suffix in selector.REQUIRED_SUFFIXES
            )
        )
        auxiliary.update(copy.deepcopy(target))
        auxiliary["member_name"] = _replace_run_token(name, "1")
        auxiliary["local_header_offset"] += 1
    elif witness == "wrong_task_token":
        target["member_name"] = name.replace("task-freewill", "task-other", 1)
    elif witness == "incomplete_companion_set":
        target["member_name"] = "Freewill_generated/generated_aux/removed-core.bin"
    elif witness == "overlong_member_name":
        target["member_name"] = f"{'a' * 1024}/{name}"
    elif witness == "mutated_row_schema":
        target["unexpected"] = True
    else:
        raise ValueError("unknown generated refusal witness")
    return changed


def _expect_refusal(expected_route: str, action: Callable[[], Any]) -> str:
    try:
        action()
    except VariableWidthRunIndexRepairRefusal as exc:
        if exc.route != expected_route:
            raise VariableWidthRunIndexRepairRefusal(
                REFUSAL_ROUTES[7], "generated refusal route differs"
            ) from exc
        return exc.route
    raise VariableWidthRunIndexRepairRefusal(
        REFUSAL_ROUTES[7], "generated mutation unexpectedly passed"
    )


def _measure(value: Any) -> int:
    return len(_canonical_json_bytes(value))


def _run_direct_refusals(
    base: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> tuple[Counter[str], int, int]:
    counts: Counter[str] = Counter()
    input_bytes = 0
    temporary_peak = _measure(base)
    witness_routes = {
        "empty_run_token": REFUSAL_ROUTES[2],
        "signed_run_token": REFUSAL_ROUTES[2],
        "decimal_run_token": REFUSAL_ROUTES[2],
        "unicode_digit_run_token": REFUSAL_ROUTES[2],
        "alphabetic_run_token": REFUSAL_ROUTES[2],
        "semantic_zero": REFUSAL_ROUTES[6],
        "semantic_run_four": REFUSAL_ROUTES[4],
        "mixed_lexical_tokens_within_bundle": REFUSAL_ROUTES[4],
        "duplicate_normalized_run_companion": REFUSAL_ROUTES[4],
        "wrong_task_token": REFUSAL_ROUTES[3],
        "incomplete_companion_set": REFUSAL_ROUTES[4],
        "overlong_member_name": REFUSAL_ROUTES[2],
        "mutated_row_schema": REFUSAL_ROUTES[2],
    }
    for witness, route in witness_routes.items():
        changed = _mutated_witness(base, witness)
        size = _measure(changed)
        input_bytes += size
        temporary_peak = max(temporary_peak, _measure(base) + size)
        counts[
            _expect_refusal(
                route,
                lambda item=changed: adapt_variable_width_source(
                    item, contract=contract
                ),
            )
        ] += 1

    row = copy.deepcopy(_first_core(base))
    row_mutations: list[tuple[str, Any]] = [
        ("unknown", 1),
        ("CRC32", "X" * 8),
        ("compressed_size", True),
        ("compressed_size", -1),
        ("uncompressed_size", -1),
        ("ZIP64_extra_used", 1),
        ("compression_method", 99),
        ("general_purpose_flags", 1),
        ("entry_kind", "socket"),
        ("member_name", "/absolute_eeg.vhdr"),
        ("member_name", "Freewill_generated/../escape_eeg.vhdr"),
        ("member_name", "Freewill_generated\\escape_eeg.vhdr"),
    ]
    for key, value in row_mutations:
        changed = copy.deepcopy(row)
        changed[key] = value
        input_bytes += _measure(changed)
        counts[
            _expect_refusal(
                REFUSAL_ROUTES[2],
                lambda item=changed: _validate_variable_entry(item),
            )
        ] += 1

    directory = next(
        item for item in base["entries"] if item["entry_kind"] == "directory"
    )
    for key, value in (
        ("compressed_size", 1),
        ("uncompressed_size", 1),
        ("compression_method", 8),
        ("member_name", directory["member_name"].rstrip("/")),
    ):
        changed = copy.deepcopy(directory)
        changed[key] = value
        input_bytes += _measure(changed)
        counts[
            _expect_refusal(
                REFUSAL_ROUTES[2],
                lambda item=changed: _validate_variable_entry(item),
            )
        ] += 1

    contract_mutations = (
        {**contract, "schema_version": "9.9.9"},
        {**contract, "lane_id": "MARC2-VR16X"},
        {**contract, "status": "implemented"},
        {**contract, "unexpected": True},
        {**contract, "fixed_input_bytes": 1},
        {**contract, "direct_refusal_minimum": 47},
    )
    for changed in contract_mutations:
        input_bytes += _measure(changed)
        counts[
            _expect_refusal(
                REFUSAL_ROUTES[0],
                lambda item=changed: _verify_contract_mapping(item),
            )
        ] += 1

    for field, value in (
        ("schema_name", "wrong"),
        ("schema_version", "9.9.9"),
        ("proof_posture", "wrong"),
        ("entries", []),
    ):
        changed = copy.deepcopy(dict(base))
        changed[field] = value
        size = _measure(changed)
        input_bytes += size
        temporary_peak = max(temporary_peak, _measure(base) + size)
        counts[
            _expect_refusal(
                REFUSAL_ROUTES[1],
                lambda item=changed: adapt_variable_width_source(
                    item, contract=contract
                ),
            )
        ] += 1

    for environment in (
        {**THREAD_ENVIRONMENT, "OMP_NUM_THREADS": "2"},
        {**THREAD_ENVIRONMENT, "OPENBLAS_NUM_THREADS": "0"},
        {**THREAD_ENVIRONMENT, "MKL_NUM_THREADS": "2"},
        {**THREAD_ENVIRONMENT, "NUMEXPR_NUM_THREADS": ""},
        {**THREAD_ENVIRONMENT, "VECLIB_MAXIMUM_THREADS": "8"},
    ):
        input_bytes += _measure(environment)
        counts[
            _expect_refusal(
                REFUSAL_ROUTES[8],
                lambda item=environment: _validate_thread_environment(item),
            )
        ] += 1

    for report in (
        {"member_name": "forbidden"},
        {"safe": [{"target": "forbidden"}]},
        {"safe": {"private_manifest": []}},
    ):
        input_bytes += _measure(report)
        counts[
            _expect_refusal(
                REFUSAL_ROUTES[7],
                lambda item=report: _assert_public_report_safe(item),
            )
        ] += 1

    for values in (
        (31.0, 1, 1),
        (1.0, 268_435_456, 1),
        (1.0, 1, 2_097_153),
    ):
        counts[
            _expect_refusal(
                REFUSAL_ROUTES[8],
                lambda item=values: _assert_resources(
                    runtime_seconds=item[0],
                    peak_rss_bytes=item[1],
                    temporary_output_bytes=item[2],
                    aggregate_output_bytes=1,
                    generated_input_bytes=1,
                    contract=contract,
                ),
            )
        ] += 1

    if sum(counts.values()) < contract["direct_refusal_minimum"]:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "direct refusal coverage is incomplete"
        )
    return counts, input_bytes, temporary_peak


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[8], "thread environment differs"
        )


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in vr12a.FORBIDDEN_PUBLIC_KEYS:
                raise VariableWidthRunIndexRepairRefusal(
                    REFUSAL_ROUTES[7], "aggregate report contains forbidden field"
                )
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1024**2:
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "aggregate report exceeds output cap"
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
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[8], "generated resource cap exceeded"
        )


def _zero_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR15P_path_or_output_operations": 0,
        "real_structural_source_operations": 0,
        "cohort_freezes": 0,
        "archive_header_or_member_payload_operations": 0,
        "neural_signal_event_channel_geometry_target_or_label_operations": 0,
        "cache_feature_split_or_NeuroToken_operations": 0,
        "model_training_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scoring_runs": 0,
        "FW2_operations": 0,
        "CIL1_operations": 0,
        "network_requests": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "other_project_operations": 0,
        "retry_rerun_resume_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
    }


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the frozen generated matrix and return one aggregate report."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment()
    outcomes_by_replay: list[list[dict[str, Any]]] = []
    generated_input_bytes = 0
    temporary_peak = 0
    baseline_semantic: str | None = None
    raw_hashes: set[str] = set()
    name_hashes: set[str] = set()
    base = build_generated_variant("two_digit_control", "canonical")
    for replay in range(REPLAYS):
        replay_outcomes: list[dict[str, Any]] = []
        for variant in VARIANTS:
            for order in ORDERS:
                source = build_generated_variant(variant, order)
                source_bytes = vr2._canonical_source_bytes(source)
                generated_input_bytes += len(source_bytes)
                temporary_peak = max(temporary_peak, len(source_bytes) + _measure(base))
                outcome = adapt_variable_width_source(source, contract=registered)
                if vr2._canonical_source_bytes(source) != source_bytes:
                    raise VariableWidthRunIndexRepairRefusal(
                        REFUSAL_ROUTES[7], "qualification mutated generated source"
                    )
                if baseline_semantic is None:
                    baseline_semantic = outcome.semantic_sha256
                elif outcome.semantic_sha256 != baseline_semantic:
                    raise VariableWidthRunIndexRepairRefusal(
                        REFUSAL_ROUTES[7], "semantic replay differs"
                    )
                raw_hashes.add(outcome.source_sha256)
                name_hashes.add(outcome.source_exact_selected_names_sha256)
                replay_outcomes.append(
                    {
                        "variant": variant,
                        "order": order,
                        "subjects": outcome.selection.cohort_summary[
                            "selected_subjects"
                        ],
                        "run_bundles": outcome.selection.split_summary[
                            "selected_run_bundles"
                        ],
                        "core_members": outcome.selection.split_summary[
                            "selected_core_members"
                        ],
                        "semantic_sha256": outcome.semantic_sha256,
                        "raw_sha256": outcome.source_sha256,
                        "names_sha256": outcome.source_exact_selected_names_sha256,
                    }
                )
        outcomes_by_replay.append(replay_outcomes)
    if (
        len(outcomes_by_replay) != 2
        or outcomes_by_replay[0] != outcomes_by_replay[1]
        or len(outcomes_by_replay[0]) != 12
        or len(raw_hashes) != 6
        or len(name_hashes) != 6
    ):
        raise VariableWidthRunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "generated matrix replay or identity differs"
        )
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
        "route": SUCCESS_ROUTE,
        "status": "generated_only_qualified_no_private_access",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
        },
        "matrix": {
            "success_paths": len(outcomes_by_replay) * len(outcomes_by_replay[0]),
            "variants": list(VARIANTS),
            "orders": list(ORDERS),
            "replays": REPLAYS,
            "exact_replays_match": True,
            "semantic_sha256": baseline_semantic,
            "distinct_raw_source_hashes": len(raw_hashes),
            "distinct_source_exact_selected_name_hashes": len(name_hashes),
            "source_objects_immutable": True,
            "source_exact_names_preserved": True,
            "reservation_replayed_from_source_exact_names": True,
        },
        "refusals": {
            "direct_refusals": sum(refusals.values()),
            "route_counts": dict(sorted(refusals.items())),
            "syntax_semantic_companion_collision_schema_resource_output_guards": True,
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
        "operation_counters": _zero_counters(),
        "warnings": [
            "generated_fixture_only_no_private_or_real_source_access",
            "VR15P_R15_scopes_the_repair_but_hidden_token_is_unavailable",
            "no_real_cohort_or_FW2_CIL1_eligibility",
            "no_neural_decoding_or_scientific_claim",
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
    """Return the fixed generated-only plan with no execution authority."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(contract)
    return {
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "fixed_input_bytes": fixed_input_bytes,
        "variants": list(VARIANTS),
        "orders": list(ORDERS),
        "replays": REPLAYS,
        "required_success_paths": 24,
        "direct_refusal_minimum": contract["direct_refusal_minimum"],
        "private_access_authorized": False,
        "real_structural_confirmation_authorized": False,
        "cohort_freeze_authorized": False,
        "FW2_authorized": False,
        "CIL1_authorized": False,
        "execute_surface_available": False,
        "claim_boundary": contract["claim_boundary"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 variable-width run-index repair."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = build_plan() if args.command == "plan" else qualify_generated()
    except VariableWidthRunIndexRepairRefusal as exc:
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
