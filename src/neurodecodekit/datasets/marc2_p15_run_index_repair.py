"""Generated-only MARC2 P15 semantic run-index repair."""

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
from neurodecodekit.datasets import marc2_source_validity_eligibility_repair as repair


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR12A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_p15_run_index_repair_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_p15_run_index_repair_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_p15_run_index_repair_contract.v0.json"
)
CONTRACT_SHA256 = "a6cd01e79813f79dfd7b54ee6c2d21ffb82e984b6230434127b936c513cf3f1e"
GREEN_REGISTRATION_COMMIT = "5107eb3d714f7713a216b9ad4e21c06300cd8c21"
GREEN_REGISTRATION_CI_RUN_ID = 32_168_117_907
GREEN_REGISTRATION_BASE_JOB_ID = 95_812_470_306
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_812_470_218
SUCCESS_ROUTE = "MARC2VR12A-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR12A-F{index:02d}" for index in range(1, 10))
VARIANTS = (
    "padded_control",
    "unpadded_single_digit",
    "bundle_consistent_mixed_width",
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
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "candidate",
        "cohort",
        "crc32",
        "entries",
        "event",
        "failed_value",
        "label",
        "labels",
        "member_name",
        "participant_id",
        "path",
        "prediction",
        "predictions",
        "private_manifest",
        "row",
        "row_index",
        "rows",
        "run_id",
        "selection",
        "session_id",
        "signal",
        "source_identity",
        "subject_id",
        "suffix",
        "target",
        "targets",
    }
)
REPAIRED_CORE_MEMBER_RE = re.compile(
    r"(?:[A-Za-z0-9._-]+/)*"
    r"(?P<subject>sub-[0-9]{2})/(?P<session>ses-[0-9]{2})/eeg/"
    r"(?P=subject)_(?P=session)_task-(?P<task>[A-Za-z0-9]+)"
    r"(?:_[A-Za-z0-9]+-[A-Za-z0-9]+)*_run-(?P<run>[0-9]{1,2})"
    r"(?P<suffix>_eeg\.eeg|_eeg\.vhdr|_eeg\.vmrk|_events\.tsv)\Z"
)


class P15RunIndexRepairRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR12A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR12A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class RepairedSelection:
    """Private structural selection plus aggregate-safe deterministic hashes."""

    selection: selector.SelectionResult
    source_sha256: str
    semantic_cohort_sha256: str
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
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    path = (root or _repo_root()) / CONTRACT_RELATIVE_PATH
    data = path.read_bytes()
    if _sha256_bytes(data) != CONTRACT_SHA256:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return data


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR12A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if not isinstance(payload, dict):
        raise P15RunIndexRepairRefusal(
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
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "5107eb3d714f7713a216b9ad4e21c06300cd8c21"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_168_117_907
        or GREEN_REGISTRATION_BASE_JOB_ID != 95_812_470_306
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 95_812_470_218
    ):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _repaired_core_match(name: str) -> re.Match[str] | None:
    return REPAIRED_CORE_MEMBER_RE.fullmatch(name)


def _validate_repaired_entry(row: Any) -> tuple[str, re.Match[str] | None]:
    if not isinstance(row, dict) or set(row) != selector.ENTRY_FIELDS:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source row fields differ"
        )
    try:
        name = selector._normalize_member_name(row["member_name"])
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source member path differs"
        ) from exc
    if (
        not isinstance(row["CRC32"], str)
        or selector.CRC_RE.fullmatch(row["CRC32"]) is None
    ):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source CRC declaration differs"
        )
    integer_fields = (
        "compressed_size",
        "compression_method",
        "external_attributes",
        "general_purpose_flags",
        "local_header_offset",
        "uncompressed_size",
        "version_made_by",
    )
    if any(
        isinstance(row[key], bool) or not isinstance(row[key], int)
        for key in integer_fields
    ):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source integer declaration differs"
        )
    if row["compressed_size"] < 0 or row["uncompressed_size"] < 0:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source size is negative"
        )
    if not isinstance(row["ZIP64_extra_used"], bool):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "source ZIP64 declaration differs"
        )
    if row["compression_method"] not in {0, 8} or row["general_purpose_flags"] & 1:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "encrypted or unsupported member"
        )
    if row["entry_kind"] == "directory":
        if (
            not name.endswith("/")
            or row["compressed_size"]
            or row["uncompressed_size"]
            or row["compression_method"] != 0
        ):
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[2], "directory row is malformed"
            )
        return name, None
    if row["entry_kind"] != "regular_file" or name.endswith("/"):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "regular member type differs"
        )
    match = _repaired_core_match(name)
    if match is None and any(name.endswith(value) for value in selector.REQUIRED_SUFFIXES):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[2], "P15 suffix-bearing BIDS identity differs"
        )
    if match is not None and match.group("task") != "freewill":
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[3], "P16 Freewill task differs"
        )
    return name, match


def _group_repaired_rows(
    entries: Sequence[Any],
) -> tuple[dict[tuple[str, str, int], dict[str, Mapping[str, Any]]], Counter[str]]:
    names: set[str] = set()
    kinds: Counter[str] = Counter()
    grouped: dict[tuple[str, str, int], dict[str, Mapping[str, Any]]] = defaultdict(
        dict
    )
    run_tokens: dict[tuple[str, str, int], str] = {}
    for row in entries:
        name, match = _validate_repaired_entry(row)
        if name in names:
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[2], "source full member name is duplicated"
            )
        names.add(name)
        kinds[row["entry_kind"]] += 1
        if match is None:
            continue
        key = (
            match.group("subject"),
            match.group("session"),
            int(match.group("run")),
        )
        token = match.group("run")
        previous_token = run_tokens.setdefault(key, token)
        if previous_token != token:
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[4], "P18 companion run spelling differs"
            )
        suffix = match.group("suffix")
        if suffix in grouped[key]:
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[4], "P18 normalized run companion is duplicated"
            )
        grouped[key][suffix] = row
    if any(
        set(companions) != set(selector.REQUIRED_SUFFIXES)
        for companions in grouped.values()
    ):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[4], "P19 run companion set is incomplete"
        )
    return dict(grouped), kinds


def _validate_and_filter(
    source: Mapping[str, Any],
    *,
    vr2_contract: Mapping[str, Any],
) -> tuple[
    dict[tuple[str, str, int], dict[str, Mapping[str, Any]]],
    str,
]:
    try:
        vr2._verify_contract_mapping(vr2_contract)
        entries = vr2._validate_live_envelope(source, vr2_contract)
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[1], "live source envelope differs"
        ) from exc
    grouped, kinds = _group_repaired_rows(entries)
    domain = vr2_contract["generated_live_source_domain"]
    if kinds != Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    ) or len(grouped) != domain["complete_source_run_bundles"]:
        raise P15RunIndexRepairRefusal(
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
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[5], "source taxonomy or eligibility differs"
        ) from exc
    return filtered, _sha256_bytes(vr2._canonical_source_bytes(source))


def _semantic_identity(selection: selector.SelectionResult) -> dict[str, Any]:
    bundles: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    for row in selection.private_manifest["rows"]:
        match = _repaired_core_match(row["member_name"])
        if match is None:
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[6], "selected row identity differs"
            )
        bundles[
            (
                match.group("subject"),
                match.group("session"),
                int(match.group("run")),
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


def _validate_repaired_selection(
    selection: selector.SelectionResult,
    *,
    filtered_keys: set[tuple[str, str, int]],
    source_names: set[str],
    selector_contract: Mapping[str, Any],
) -> tuple[str, str]:
    try:
        rank = selector._validate_rank(selector_contract)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "selector rank differs"
        ) from exc
    cohort = selection.cohort_summary
    split = selection.split_summary
    byte_summary = selection.byte_summary
    subjects = cohort.get("selected_subject_ids")
    if not isinstance(subjects, list):
        raise P15RunIndexRepairRefusal(
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
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "cohort or split arithmetic differs"
        )
    rows = selection.private_manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != count * 24:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "selected structural rows differ"
        )
    try:
        vr6._walk_scientific_firewall(selection.private_manifest)
    except vr6.DynamicLiveSelectionRefusal as exc:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "scientific firewall refused"
        ) from exc
    names: set[str] = set()
    bundle_tokens: dict[tuple[str, str, int], str] = {}
    bundle_suffixes: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    measured_reservation = 0
    for row in rows:
        name = row.get("member_name")
        match = _repaired_core_match(name) if isinstance(name, str) else None
        if match is None:
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[6], "selected source-exact name differs"
            )
        key = (
            match.group("subject"),
            match.group("session"),
            int(match.group("run")),
        )
        token = match.group("run")
        previous_token = bundle_tokens.setdefault(key, token)
        expected_reservation = selector._reservation_bytes(row)
        if (
            name not in source_names
            or name in names
            or key not in filtered_keys
            or previous_token != token
            or row.get("subject_id") != key[0]
            or row.get("session_id") != key[1]
            or row.get("run_id") != f"run-{key[2]:02d}"
            or row.get("split_role")
            != ("fit" if key[1] == "ses-01" else "heldout")
            or key[2] not in {1, 2, 3}
            or row.get("reservation_bytes") != expected_reservation
        ):
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[6], "selected row identity or reservation differs"
            )
        names.add(name)
        bundle_suffixes[key].add(match.group("suffix"))
        measured_reservation += expected_reservation
    if (
        len(bundle_suffixes) != count * 6
        or any(
            values != set(selector.REQUIRED_SUFFIXES)
            for values in bundle_suffixes.values()
        )
        or measured_reservation != byte_summary.get("selected_reservation_bytes")
        or byte_summary.get("reservation_cap_bytes") != selector.RESERVATION_CAP_BYTES
        or measured_reservation > selector.RESERVATION_CAP_BYTES
    ):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "selected companion or storage arithmetic differs"
        )
    semantic_sha256 = _sha256_bytes(_canonical_json_bytes(_semantic_identity(selection)))
    names_sha256 = _sha256_bytes(_canonical_json_bytes(sorted(names)))
    return semantic_sha256, names_sha256


def adapt_repaired_source(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    vr2_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> RepairedSelection:
    """Validate and select one generated source through the repaired P15 path."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    before = vr2._canonical_source_bytes(source)
    filtered, source_sha256 = _validate_and_filter(
        source, vr2_contract=registered_vr2
    )
    if vr2._canonical_source_bytes(source) != before:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "source changed during repaired validation"
        )
    try:
        selection = repair._select_from_filtered(
            filtered, source_sha256, frozen_selector
        )
    except (repair.SourceValidityEligibilityRefusal, selector.FreewillPrefixSelectionRefusal) as exc:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[6], "repaired dynamic selection refused"
        ) from exc
    if vr2._canonical_source_bytes(source) != before:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "source changed during repaired selection"
        )
    source_names = {
        row["member_name"]
        for row in source["entries"]
        if isinstance(row, dict) and isinstance(row.get("member_name"), str)
    }
    semantic_sha256, names_sha256 = _validate_repaired_selection(
        selection,
        filtered_keys=set(filtered),
        source_names=source_names,
        selector_contract=frozen_selector,
    )
    return RepairedSelection(
        selection=selection,
        source_sha256=source_sha256,
        semantic_cohort_sha256=semantic_sha256,
        source_exact_selected_names_sha256=names_sha256,
    )


def _rewrite_variant(source: dict[str, Any], variant: str) -> None:
    if variant not in VARIANTS:
        raise ValueError("unknown generated spelling variant")
    if variant == "padded_control":
        return
    for row in source["entries"]:
        if not isinstance(row, dict):
            continue
        name = row.get("member_name")
        match = selector._core_match(name) if isinstance(name, str) else None
        if match is None:
            continue
        run = int(match.group("run"))
        should_unpad = run < 10 and (
            variant == "unpadded_single_digit"
            or (
                variant == "bundle_consistent_mixed_width"
                and (int(match.group("subject")[4:]) + int(match.group("session")[4:]) + run)
                % 2
                == 1
            )
        )
        if should_unpad:
            row["member_name"] = re.sub(
                r"_run-0([0-9])(?=_)", r"_run-\1", name, count=1
            )


def build_generated_variant(
    variant: str,
    order: str,
    *,
    vr2_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one 1,227-row generated source without a real path or byte."""

    registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())
    try:
        source = vr2.build_generated_live_source(
            profile="A", row_order="canonical", contract=registered_vr2
        )
    except vr2.LiveDomainEligibilityRefusal as exc:
        raise P15RunIndexRepairRefusal(
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
        and _repaired_core_match(row["member_name"]) is not None
    )


def _rows_for_first_bundle(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    first = _first_core(source)
    match = _repaired_core_match(first["member_name"])
    assert match is not None
    key = (match.group("subject"), match.group("session"), int(match.group("run")))
    rows = []
    for row in source["entries"]:
        if not isinstance(row, dict) or not isinstance(row.get("member_name"), str):
            continue
        candidate = _repaired_core_match(row["member_name"])
        if candidate is not None and (
            candidate.group("subject"),
            candidate.group("session"),
            int(candidate.group("run")),
        ) == key:
            rows.append(row)
    return rows


def _mutated_witness(source: Mapping[str, Any], witness: str) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    rows = _rows_for_first_bundle(changed)
    target = rows[0]
    name = target["member_name"]
    match = _repaired_core_match(name)
    if match is None:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "generated witness source differs"
        )
    subject = match.group("subject")
    session = match.group("session")
    if witness == "subject_path_filename_disagreement":
        target["member_name"] = name.replace(f"/{subject}_", "/sub-99_", 1)
    elif witness == "session_path_filename_disagreement":
        target["member_name"] = name.replace(f"_{session}_", "_ses-99_", 1)
    elif witness == "nonnumeric_run_token":
        target["member_name"] = re.sub(r"_run-[0-9]{1,2}_", "_run-x_", name, count=1)
    elif witness == "three_digit_run_token":
        target["member_name"] = re.sub(r"_run-[0-9]{1,2}_", "_run-001_", name, count=1)
    elif witness == "mixed_lexical_run_tokens_within_bundle":
        candidate = next(
            row for row in rows if row["member_name"].endswith("_eeg.vhdr")
        )
        candidate["member_name"] = re.sub(
            r"_run-0([0-9])(?=_)", r"_run-\1", candidate["member_name"], count=1
        )
    elif witness == "duplicate_normalized_run_companion":
        auxiliary = next(
            row
            for row in changed["entries"]
            if row["entry_kind"] == "regular_file"
            and _repaired_core_match(row["member_name"]) is None
            and not any(
                row["member_name"].endswith(value)
                for value in selector.REQUIRED_SUFFIXES
            )
        )
        auxiliary.update(copy.deepcopy(target))
        auxiliary["member_name"] = re.sub(
            r"_run-0([0-9])(?=_)", r"_run-\1", target["member_name"], count=1
        )
        auxiliary["local_header_offset"] += 1
    elif witness == "wrong_task_token":
        target["member_name"] = name.replace("task-freewill", "task-other", 1)
    elif witness == "incomplete_companion_set":
        target["member_name"] = "Freewill_generated/generated_aux/removed-core.bin"
    else:
        raise ValueError("unknown generated refusal witness")
    return changed


def _expect_refusal(
    expected_route: str,
    action: Callable[[], Any],
) -> str:
    try:
        action()
    except P15RunIndexRepairRefusal as exc:
        if exc.route != expected_route:
            raise P15RunIndexRepairRefusal(
                REFUSAL_ROUTES[7], "generated refusal route differs"
            ) from exc
        return exc.route
    raise P15RunIndexRepairRefusal(
        REFUSAL_ROUTES[7], "generated mutation unexpectedly passed"
    )


def _run_direct_refusals(
    base: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    witness_routes = {
        "subject_path_filename_disagreement": REFUSAL_ROUTES[2],
        "session_path_filename_disagreement": REFUSAL_ROUTES[2],
        "nonnumeric_run_token": REFUSAL_ROUTES[2],
        "three_digit_run_token": REFUSAL_ROUTES[2],
        "mixed_lexical_run_tokens_within_bundle": REFUSAL_ROUTES[4],
        "duplicate_normalized_run_companion": REFUSAL_ROUTES[4],
        "wrong_task_token": REFUSAL_ROUTES[3],
        "incomplete_companion_set": REFUSAL_ROUTES[4],
    }
    for witness, route in witness_routes.items():
        counts[_expect_refusal(route, lambda w=witness: adapt_repaired_source(
            _mutated_witness(base, w), contract=contract
        ))] += 1

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
        counts[_expect_refusal(
            REFUSAL_ROUTES[2], lambda item=changed: _validate_repaired_entry(item)
        )] += 1

    directory = next(row for row in base["entries"] if row["entry_kind"] == "directory")
    for key, value in (
        ("compressed_size", 1),
        ("uncompressed_size", 1),
        ("compression_method", 8),
        ("member_name", directory["member_name"].rstrip("/")),
    ):
        changed = copy.deepcopy(directory)
        changed[key] = value
        counts[_expect_refusal(
            REFUSAL_ROUTES[2], lambda item=changed: _validate_repaired_entry(item)
        )] += 1

    for mutation in (
        {**contract, "schema_version": "9.9.9"},
        {**contract, "lane_id": "MARC2-VR12X"},
        {**contract, "status": "implemented"},
        {**contract, "unexpected": True},
    ):
        counts[_expect_refusal(
            REFUSAL_ROUTES[0], lambda item=mutation: _verify_contract_mapping(item)
        )] += 1

    for field, value in (
        ("schema_name", "wrong"),
        ("schema_version", "9.9.9"),
        ("proof_posture", "wrong"),
        ("entries", []),
    ):
        changed = copy.deepcopy(dict(base))
        changed[field] = value
        counts[_expect_refusal(
            REFUSAL_ROUTES[1], lambda item=changed: adapt_repaired_source(
                item, contract=contract
            )
        )] += 1

    for environment in (
        {**THREAD_ENVIRONMENT, "OMP_NUM_THREADS": "2"},
        {**THREAD_ENVIRONMENT, "OPENBLAS_NUM_THREADS": "0"},
    ):
        counts[_expect_refusal(
            REFUSAL_ROUTES[8], lambda item=environment: _validate_thread_environment(item)
        )] += 1

    for report in (
        {"member_name": "forbidden"},
        {"safe": [{"target": "forbidden"}]},
    ):
        counts[_expect_refusal(
            REFUSAL_ROUTES[7], lambda item=report: _assert_public_report_safe(item)
        )] += 1
    if sum(counts.values()) < 36:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "direct refusal coverage is incomplete"
        )
    return counts


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[8], "thread environment differs"
        )


def _walk_public(value: Any, *, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).casefold()
            if lowered in FORBIDDEN_PUBLIC_KEYS:
                raise P15RunIndexRepairRefusal(
                    REFUSAL_ROUTES[7], "aggregate report contains forbidden field"
                )
            _walk_public(item, path=(*path, str(key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_public(item, path=(*path, str(index)))


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    payload = _canonical_json_bytes(report)
    if len(payload) > 1024**2:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[8], "aggregate output cap exceeded"
        )


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _zero_counters() -> dict[str, int]:
    return {
        "private_path_operations": 0,
        "consumed_result_or_output_reopens": 0,
        "real_structural_source_opens": 0,
        "real_structural_bytes": 0,
        "archive_member_operations": 0,
        "neural_signal_operations": 0,
        "event_or_target_operations": 0,
        "cohort_freezes": 0,
        "FW2_operations": 0,
        "CIL1_operations": 0,
        "model_training_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scoring_runs": 0,
        "network_requests": 0,
        "provider_or_language_model_calls": 0,
        "device_or_hardware_operations": 0,
        "other_project_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the registered generated matrix and return one aggregate report."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    _validate_thread_environment()
    outcomes: list[dict[str, Any]] = []
    total_generated_input = 0
    baseline_semantic: str | None = None
    variant_raw_hashes: dict[str, set[str]] = defaultdict(set)
    variant_name_hashes: dict[str, set[str]] = defaultdict(set)
    base = build_generated_variant("padded_control", "canonical")
    for replay in range(REPLAYS):
        for variant in VARIANTS:
            for order in ORDERS:
                source = build_generated_variant(variant, order)
                before = vr2._canonical_source_bytes(source)
                total_generated_input += len(before)
                repaired = adapt_repaired_source(source, contract=registered)
                if vr2._canonical_source_bytes(source) != before:
                    raise P15RunIndexRepairRefusal(
                        REFUSAL_ROUTES[7], "qualification mutated generated source"
                    )
                if baseline_semantic is None:
                    baseline_semantic = repaired.semantic_cohort_sha256
                elif repaired.semantic_cohort_sha256 != baseline_semantic:
                    raise P15RunIndexRepairRefusal(
                        REFUSAL_ROUTES[7], "semantic cohort replay differs"
                    )
                variant_raw_hashes[variant].add(repaired.source_sha256)
                variant_name_hashes[variant].add(
                    repaired.source_exact_selected_names_sha256
                )
                outcomes.append(
                    {
                        "variant": variant,
                        "order": order,
                        "replay": replay + 1,
                        "selected_subject_count": repaired.selection.cohort_summary[
                            "selected_subjects"
                        ],
                        "selected_run_bundle_count": repaired.selection.split_summary[
                            "selected_run_bundles"
                        ],
                        "selected_core_member_count": repaired.selection.split_summary[
                            "selected_core_members"
                        ],
                        "semantic_cohort_sha256": repaired.semantic_cohort_sha256,
                        "raw_source_sha256": repaired.source_sha256,
                        "source_exact_selected_names_sha256": repaired.source_exact_selected_names_sha256,
                    }
                )
    if (
        len(outcomes) != 12
        or any(len(values) != 1 for values in variant_raw_hashes.values())
        or any(len(values) != 1 for values in variant_name_hashes.values())
        or len({next(iter(values)) for values in variant_raw_hashes.values()}) != 3
        or len({next(iter(values)) for values in variant_name_hashes.values()}) != 3
    ):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[7], "generated replay or source-exact hash matrix differs"
        )
    refusals = _run_direct_refusals(base, contract=registered)
    elapsed = clock() - started
    rss = peak_rss()
    caps = registered["resource_caps"]
    if (
        elapsed < 0
        or elapsed > caps["runtime_seconds"]
        or rss < 0
        or rss > caps["peak_RSS_bytes"]
        or total_generated_input > caps["generated_input_bytes"]
    ):
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[8], "generated resource cap exceeded"
        )
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
            "success_paths": len(outcomes),
            "variants": list(VARIANTS),
            "orders": list(ORDERS),
            "replays": REPLAYS,
            "semantic_cohort_sha256": baseline_semantic,
            "distinct_raw_source_hashes": 3,
            "distinct_source_exact_selected_name_hashes": 3,
            "source_objects_immutable": True,
            "source_exact_names_preserved": True,
            "reservation_replayed_from_source_exact_names": True,
        },
        "refusals": {
            "direct_refusals": sum(refusals.values()),
            "route_counts": dict(sorted(refusals.items())),
            "required_classes_preserved": ["P15", "P16", "P18", "P19"],
        },
        "measurements": {
            "generated_input_bytes": total_generated_input,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": elapsed,
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
            "unpadded_run_index_not_observed_in_consumed_private_source",
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
    if output_bytes > caps["aggregate_output_bytes"]:
        raise P15RunIndexRepairRefusal(
            REFUSAL_ROUTES[8], "aggregate output cap exceeded"
        )
    return report


def build_plan() -> dict[str, Any]:
    """Return an aggregate generated-only plan with no execution authority."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    return {
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "variants": list(VARIANTS),
        "orders": list(ORDERS),
        "replays": REPLAYS,
        "required_success_paths": 12,
        "direct_refusal_minimum": contract["direct_refusal_minimum"],
        "private_access_authorized": False,
        "real_structural_confirmation_authorized": False,
        "FW2_authorized": False,
        "CIL1_authorized": False,
        "execute_surface_available": False,
        "claim_boundary": contract["claim_boundary"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 P15 semantic run-index repair."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = build_plan() if args.command == "plan" else qualify_generated()
    except P15RunIndexRepairRefusal as exc:
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
