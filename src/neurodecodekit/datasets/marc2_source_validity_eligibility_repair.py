"""Generated-only MARC2 source-validity and eligibility qualification."""

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
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR1"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_source_validity_eligibility_repair_contract"
)
REPORT_SCHEMA_NAME = (
    "neurodecodekit.marc2_source_validity_eligibility_repair_report"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_source_validity_eligibility_repair_contract.v0.json"
)
CONTRACT_SHA256 = "84f44f8bc43a4ee56e256a1546cbc1fae3252f2f320db7064602fe72b44463e9"
GENERATED_PROOF_POSTURE = (
    "generated_structural_metadata_only_no_scientific_value"
)
SUCCESS_ROUTE = "MARC2VR-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR-F{index:02d}" for index in range(1, 9))
PREDICATE_CODES = tuple(f"MARC2VR-P{index:02d}" for index in range(1, 5))
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
SOURCE_TOP_LEVEL_FIELDS = {
    "schema_name",
    "schema_version",
    "proof_posture",
    "source_identity",
    "transport_body_sha256",
    "entries",
}
SOURCE_IDENTITY = {
    "provider": "generated_fixture",
    "record_id": 28_632_599,
    "version": 1,
    "file_id": 0,
    "declared_archive_bytes": 13_591_548_048,
    "registered_MD5": "0" * 32,
    "whole_archive_downloaded": False,
    "member_payload_opened": False,
}
TRANSPORT_KEYS = {"metadata", "tail", "central_directory"}

RunKey = tuple[str, str, int]
RunCompanions = dict[str, dict[str, Any]]
GroupedRuns = dict[RunKey, RunCompanions]


class SourceValidityEligibilityRefusal(RuntimeError):
    """Fail-closed refusal with a registered aggregate route."""

    def __init__(self, route: str, reason: str) -> None:
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.reason = reason


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[6], "public JSON is not canonical"
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


def _fixed_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", "..", ".codex_work"} for part in path.parts)
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input path is unsafe"
        )
    current = root
    for part in path.parts:
        current = current / part
        try:
            info = current.lstat()
        except OSError as exc:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input path contains a symlink"
            )
    if not stat.S_ISREG(current.lstat().st_mode):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input is not a regular file"
        )
    return current


def _read_bound_file(path: Path, *, cap: int) -> bytes:
    size = path.stat(follow_symlinks=False).st_size
    if size > cap:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input exceeds cap"
        )
    try:
        with path.open("rb") as handle:
            payload = handle.read(cap + 1)
    except OSError as exc:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input read failed"
        ) from exc
    if len(payload) != size or len(payload) > cap:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input size changed during read"
        )
    return payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_only_contract_implementation_pending"
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract identity differs"
        )
    domain = contract.get("generated_source_domain", {})
    if (
        domain.get("inventory_rows") != 1_227
        or domain.get("regular_file_rows") != 1_025
        or domain.get("directory_rows") != 202
        or domain.get("complete_source_run_bundles") != 238
        or domain.get("eligible_session_1_2_run_bundles") != 195
        or domain.get("source_valid_but_ineligible_run_bundles") != 43
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract source-domain arithmetic differs"
        )
    eligibility = contract.get("eligibility_policy", {})
    if (
        eligibility.get("eligible_subject_count") != 19
        or eligibility.get("exact_eligible_run_bundles_after_filter") != 195
        or eligibility.get("filter_before_exact_inventory_comparison") is not True
        or eligibility.get("global_195_group_assertion_before_filter_allowed")
        is not False
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract eligibility policy differs"
        )
    routes = contract.get("ordered_routes")
    if not isinstance(routes, list) or [row.get("route") for row in routes] != [
        SUCCESS_ROUTE,
        *REFUSAL_ROUTES,
    ]:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract route order differs"
        )
    mutations = contract.get("qualification", {}).get("required_mutations")
    if (
        not isinstance(mutations, list)
        or len(mutations) != 36
        or len(set(mutations)) != 36
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract mutation inventory differs"
        )
    authorization = contract.get("authorization_state")
    if not isinstance(authorization, dict) or any(authorization.values()):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract authority is not all false"
        )


def load_registered_contract(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or _repo_root()).resolve()
    path = _fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix())
    payload = _read_bound_file(path, cap=2 * 1024**2)
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    return contract


def _verify_fixed_inputs(root: Path, contract: Mapping[str, Any]) -> tuple[int, int]:
    bindings = contract.get("fixed_inputs")
    if not isinstance(bindings, list) or len(bindings) != 6:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    roles: set[str] = set()
    total_bytes = 0
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {
            "role",
            "path",
            "sha256",
        }:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input binding differs"
            )
        role = binding["role"]
        if not isinstance(role, str) or role in roles:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input role differs"
            )
        roles.add(role)
        path = _fixed_path(root, binding["path"])
        payload = _read_bound_file(path, cap=2 * 1024**2)
        if _sha256_bytes(payload) != binding["sha256"]:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input SHA-256 differs"
            )
        total_bytes += len(payload)
    return len(bindings), total_bytes


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _validate_thread_environment() -> None:
    if any(os.environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[7], "one-thread environment is not explicit"
        )


def _adversary_keys_by_predicate(
    contract: Mapping[str, Any],
) -> dict[str, set[RunKey]]:
    by_predicate: dict[str, set[RunKey]] = {}
    matrix = contract["generated_adversary_matrix"]
    for family in matrix["families"]:
        keys: set[RunKey] = set()
        for subject in family["subjects"]:
            for session, run_count in family["sessions"].items():
                keys.update(
                    (subject, session, run) for run in range(1, run_count + 1)
                )
        if len(keys) != family["bundle_count"]:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[0], "adversary recipe arithmetic differs"
            )
        by_predicate[family["predicate"]] = keys
    if (
        set(by_predicate) != set(PREDICATE_CODES[1:])
        or sum(len(keys) for keys in by_predicate.values()) != 43
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "adversary predicate inventory differs"
        )
    all_keys = set().union(*by_predicate.values())
    if len(all_keys) != 43:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "adversary keys overlap"
        )
    return by_predicate


def _core_names_for_key(key: RunKey) -> list[str]:
    subject, session, run = key
    stem = (
        f"Freewill_generated/{subject}/{session}/eeg/"
        f"{subject}_{session}_task-freewill_run-{run:02d}"
    )
    return [f"{stem}{suffix}" for suffix in selector.REQUIRED_SUFFIXES]


def build_generated_full_source(
    *,
    row_order: str = "canonical",
    contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the full 238-bundle generated source without a real path."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    try:
        source = selector.build_generated_manifest(
            profile="main",
            row_order="canonical",
            contract=frozen_selector,
        )
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "frozen selector fixture refused"
        ) from exc
    entries = copy.deepcopy(source["entries"])
    auxiliary_rows = sorted(
        (
            row
            for row in entries
            if row["entry_kind"] == "regular_file"
            and row["member_name"].startswith("Freewill_generated/generated_aux/")
        ),
        key=lambda row: row["member_name"],
    )
    replacement_count = registered["generated_adversary_matrix"][
        "adversary_companion_rows"
    ]
    if len(auxiliary_rows) != 245 or replacement_count != 172:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "base fixture auxiliary inventory differs"
        )
    replacement_ids = {id(row) for row in auxiliary_rows[:replacement_count]}
    retained = [row for row in entries if id(row) not in replacement_ids]
    adversary_keys = _adversary_keys_by_predicate(registered)
    adversary_names = sorted(
        name
        for predicate in PREDICATE_CODES[1:]
        for key in sorted(adversary_keys[predicate])
        for name in _core_names_for_key(key)
    )
    if len(adversary_names) != replacement_count:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "adversary companion arithmetic differs"
        )
    replacements: list[dict[str, Any]] = []
    for template, name in zip(
        auxiliary_rows[:replacement_count], adversary_names, strict=True
    ):
        row = copy.deepcopy(template)
        row["member_name"] = name
        row["CRC32"] = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
        replacements.append(row)
    source["proof_posture"] = GENERATED_PROOF_POSTURE
    source["entries"] = sorted(
        [*retained, *replacements], key=lambda row: row["member_name"]
    )
    if row_order == "reversed":
        source["entries"].reverse()
    elif row_order != "canonical":
        raise ValueError("unknown generated row order")
    return source


def _canonical_source_bytes(source: Mapping[str, Any]) -> bytes:
    canonical = copy.deepcopy(dict(source))
    entries = canonical.get("entries")
    if isinstance(entries, list):
        canonical["entries"] = sorted(
            entries,
            key=lambda row: str(row.get("member_name", ""))
            if isinstance(row, dict)
            else str(row),
        )
    return _canonical_json_bytes(canonical)


def _validate_source_envelope(
    source: Mapping[str, Any], contract: Mapping[str, Any]
) -> list[Any]:
    if not isinstance(source, dict) or set(source) != SOURCE_TOP_LEVEL_FIELDS:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[1], "generated source top-level fields differ"
        )
    if (
        source.get("schema_name")
        != "neurodecodekit.marc1_central_directory_private_manifest"
        or source.get("schema_version") != SCHEMA_VERSION
        or source.get("proof_posture") != GENERATED_PROOF_POSTURE
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[1], "generated source identity differs"
        )
    if source.get("source_identity") != SOURCE_IDENTITY:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[1], "generated source provenance differs"
        )
    transport = source.get("transport_body_sha256")
    if (
        not isinstance(transport, dict)
        or set(transport) != TRANSPORT_KEYS
        or any(
            not isinstance(value, str)
            or len(value) != 64
            or any(char not in "0123456789abcdef" for char in value)
            for value in transport.values()
        )
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[1], "generated transport provenance differs"
        )
    entries = source.get("entries")
    expected_rows = contract["generated_source_domain"]["inventory_rows"]
    if not isinstance(entries, list) or len(entries) != expected_rows:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[1], "generated source row count differs"
        )
    return entries


def _group_source_rows(entries: Sequence[Any]) -> tuple[GroupedRuns, Counter[str]]:
    names: set[str] = set()
    kinds: Counter[str] = Counter()
    grouped: dict[RunKey, RunCompanions] = defaultdict(dict)
    for row in entries:
        try:
            name, match = selector._validate_entry(row)
        except selector.FreewillPrefixSelectionRefusal as exc:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[2], "generated source row is unsafe"
            ) from exc
        if name in names:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[3], "generated member is duplicated"
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
        suffix = match.group("suffix")
        if suffix in grouped[key]:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[3], "run companion is duplicated"
            )
        grouped[key][suffix] = row
    if any(
        set(companions) != set(selector.REQUIRED_SUFFIXES)
        for companions in grouped.values()
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[3], "run companion set is incomplete"
        )
    return dict(grouped), kinds


def _eligible_keys(
    grouped: Mapping[RunKey, RunCompanions],
    selector_contract: Mapping[str, Any],
) -> set[RunKey]:
    eligibility = selector_contract["public_eligibility"]
    subjects = set(eligibility["eligible_subject_ids"])
    sessions = {"ses-01", "ses-02"}
    return {
        key
        for key in grouped
        if key[0] in subjects and key[1] in sessions
    }


def _classify_predicates(
    grouped: Mapping[RunKey, RunCompanions],
    selector_contract: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> tuple[dict[str, int], dict[RunKey, str]]:
    eligible = _eligible_keys(grouped, selector_contract)
    adversaries = _adversary_keys_by_predicate(contract)
    labels: dict[RunKey, str] = {}
    counts = {code: 0 for code in PREDICATE_CODES}
    for key in grouped:
        if key in eligible:
            predicate = PREDICATE_CODES[0]
        else:
            matches = [
                predicate
                for predicate, keys in adversaries.items()
                if key in keys
            ]
            if len(matches) != 1:
                raise SourceValidityEligibilityRefusal(
                    REFUSAL_ROUTES[4], "bundle eligibility is unclassified"
                )
            predicate = matches[0]
        labels[key] = predicate
        counts[predicate] += 1
    _assert_predicate_counts(counts, contract)
    return counts, labels


def _assert_predicate_counts(
    observed: Mapping[str, int], contract: Mapping[str, Any]
) -> None:
    if dict(observed) != contract["expected_predicate_counts"]:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[4], "aggregate predicate counts differ"
        )


def _filter_and_validate_eligible(
    grouped: GroupedRuns,
    labels: Mapping[RunKey, str],
    selector_contract: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> GroupedRuns:
    filtered = {
        key: companions
        for key, companions in grouped.items()
        if labels[key] == PREDICATE_CODES[0]
    }
    expected_total = contract["eligibility_policy"][
        "exact_eligible_run_bundles_after_filter"
    ]
    if len(filtered) != expected_total:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[4], "filtered eligible run total differs"
        )
    eligibility = selector_contract["public_eligibility"]
    expected_counts = eligibility["published_session_1_2_run_counts"]
    observed_counts = {
        subject: [
            sum(
                1
                for row_subject, row_session, _run in filtered
                if row_subject == subject and row_session == session
            )
            for session in ("ses-01", "ses-02")
        ]
        for subject in eligibility["eligible_subject_ids"]
    }
    if observed_counts != expected_counts:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[4], "filtered participant-session counts differ"
        )
    return filtered


def validate_generated_source(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[GroupedRuns, dict[str, int], dict[RunKey, str], str]:
    """Validate the complete source, then filter exact eligibility."""

    _verify_contract_mapping(contract)
    try:
        selector._verify_contract_mapping(selector_contract)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "frozen selector contract differs"
        ) from exc
    entries = _validate_source_envelope(source, contract)
    grouped, kinds = _group_source_rows(entries)
    domain = contract["generated_source_domain"]
    expected_kinds = Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    )
    if kinds != expected_kinds:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[1], "generated source entry-kind counts differ"
        )
    if len(grouped) != domain["complete_source_run_bundles"]:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[1], "generated source run total differs"
        )
    predicate_counts, labels = _classify_predicates(
        grouped, selector_contract, contract
    )
    filtered = _filter_and_validate_eligible(
        grouped, labels, selector_contract, contract
    )
    return (
        filtered,
        predicate_counts,
        labels,
        _sha256_bytes(_canonical_source_bytes(source)),
    )


def _select_from_filtered(
    grouped: GroupedRuns,
    source_sha256: str,
    selector_contract: Mapping[str, Any],
) -> selector.SelectionResult:
    try:
        rank = selector._validate_rank(selector_contract)
        selected_subjects: list[str] = []
        private_rows: list[dict[str, Any]] = []
        selected_bundles: list[list[Any]] = []
        selected_reservation = 0
        examined_subjects = 0
        first_nonfitting_subject: str | None = None
        first_nonfitting_reservation: int | None = None
        for subject in rank:
            rows, bundles, subject_reservation = selector._candidate_rows(
                subject, grouped, source_sha256
            )
            examined_subjects += 1
            if (
                selected_reservation + subject_reservation
                > selector.RESERVATION_CAP_BYTES
            ):
                if len(selected_subjects) < selector.MINIMUM_SUBJECTS:
                    raise selector.FreewillPrefixSelectionRefusal(
                        selector.REFUSAL_IDS[4],
                        "minimum participant prefix exceeds cap",
                    )
                first_nonfitting_subject = subject
                first_nonfitting_reservation = subject_reservation
                break
            selected_subjects.append(subject)
            selected_reservation += subject_reservation
            private_rows.extend(rows)
            selected_bundles.extend(bundles)
        if not (
            selector.MINIMUM_SUBJECTS
            <= len(selected_subjects)
            <= selector.MAXIMUM_SUBJECTS
        ):
            raise selector.FreewillPrefixSelectionRefusal(
                selector.REFUSAL_IDS[4], "selected participant count differs"
            )
        if selected_subjects != rank[: len(selected_subjects)]:
            raise selector.FreewillPrefixSelectionRefusal(
                selector.REFUSAL_IDS[3], "selection is not a rank prefix"
            )
        if (
            first_nonfitting_subject is None
            and len(selected_subjects) != selector.MAXIMUM_SUBJECTS
        ):
            raise selector.FreewillPrefixSelectionRefusal(
                selector.REFUSAL_IDS[4], "prefix ended without cap boundary"
            )
        expected_rows = len(selected_subjects) * 24
        expected_bundles = len(selected_subjects) * 6
        if (
            len(private_rows) != expected_rows
            or len(selected_bundles) != expected_bundles
        ):
            raise selector.FreewillPrefixSelectionRefusal(
                selector.REFUSAL_IDS[3], "selected bundle count differs"
            )
        selection_identity = {
            "selected_subject_ids": selected_subjects,
            "selected_bundles": selected_bundles,
            "fit_session": "ses-01",
            "heldout_session": "ses-02",
            "reservation_cap_bytes": selector.RESERVATION_CAP_BYTES,
            "selected_reservation_bytes": selected_reservation,
        }
        private_manifest = {
            "schema_name": selector.PRIVATE_SCHEMA_NAME,
            "schema_version": selector.SCHEMA_VERSION,
            "proof_posture": (
                "generated_fixture_selection_only_no_scientific_value"
            ),
            "contract_sha256": selector.CONTRACT_SHA256,
            "rows": private_rows,
        }
        return selector.SelectionResult(
            private_manifest=private_manifest,
            cohort_summary={
                "eligible_subjects": selector.EXPECTED_ELIGIBLE_SUBJECTS,
                "selected_subject_ids": selected_subjects,
                "selected_subjects": len(selected_subjects),
                "minimum_subjects": selector.MINIMUM_SUBJECTS,
                "maximum_subjects": selector.MAXIMUM_SUBJECTS,
                "first_nonfitting_subject_id": first_nonfitting_subject,
                "candidate_subjects_examined": examined_subjects,
                "selection_is_maximal_contiguous_rank_prefix": True,
                "selection_was_target_quality_and_outcome_free": True,
            },
            split_summary={
                "fit_session": "ses-01",
                "heldout_session": "ses-02",
                "fit_run_bundles": len(selected_subjects) * 3,
                "heldout_run_bundles": len(selected_subjects) * 3,
                "selected_run_bundles": expected_bundles,
                "selected_core_members": expected_rows,
                "fit_heldout_overlap": 0,
                "row_random_split_used": False,
            },
            byte_summary={
                "selected_reservation_bytes": selected_reservation,
                "reservation_cap_bytes": selector.RESERVATION_CAP_BYTES,
                "remaining_reservation_bytes": (
                    selector.RESERVATION_CAP_BYTES - selected_reservation
                ),
                "first_nonfitting_subject_reservation_bytes": (
                    first_nonfitting_reservation
                ),
                "reservation_formula": (
                    "compressed_size + 30 + UTF8_member_name_bytes + 65535"
                ),
                "fallback_or_budget_increase_used": False,
            },
            selection_hashes={
                "generated_inventory_sha256": source_sha256,
                "selection_identity_sha256": selector._sha256_bytes(
                    selector._canonical_json_bytes(selection_identity)
                ),
                "private_selection_manifest_sha256": selector._sha256_bytes(
                    selector._canonical_json_bytes(private_manifest)
                ),
            },
        )
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[5], "frozen selector mechanics refused"
        ) from exc


def _selected_run_keys(selection: selector.SelectionResult) -> set[RunKey]:
    return {
        (
            row["subject_id"],
            row["session_id"],
            int(row["run_id"].removeprefix("run-")),
        )
        for row in selection.private_manifest["rows"]
    }


def _assert_no_ineligible_candidates(
    selection: selector.SelectionResult,
    eligible_keys: set[RunKey],
) -> None:
    selected = _selected_run_keys(selection)
    if not selected <= eligible_keys:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[4], "ineligible bundle entered selection"
        )


def _assert_selection(
    selection: selector.SelectionResult,
    contract: Mapping[str, Any],
    eligible_keys: set[RunKey],
) -> None:
    expected = contract["expected_selection"]
    observed = {
        "selected_subjects": selection.cohort_summary["selected_subjects"],
        "selected_run_bundles": selection.split_summary[
            "selected_run_bundles"
        ],
        "selected_core_members": selection.split_summary[
            "selected_core_members"
        ],
        "fit_run_bundles": selection.split_summary["fit_run_bundles"],
        "heldout_run_bundles": selection.split_summary[
            "heldout_run_bundles"
        ],
        "fit_heldout_overlap": selection.split_summary["fit_heldout_overlap"],
        "selected_reservation_bytes": selection.byte_summary[
            "selected_reservation_bytes"
        ],
        "reservation_cap_bytes": selection.byte_summary[
            "reservation_cap_bytes"
        ],
        "selection_identity_sha256": selection.selection_hashes[
            "selection_identity_sha256"
        ],
    }
    if any(observed[key] != expected[key] for key in observed):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[5], "frozen selection result differs"
        )
    _assert_no_ineligible_candidates(selection, eligible_keys)


def _first_regular_aux(source: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        row
        for row in source["entries"]
        if row["entry_kind"] == "regular_file"
        and row["member_name"].startswith("Freewill_generated/generated_aux/")
    )


def _first_directory(source: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        row for row in source["entries"] if row["entry_kind"] == "directory"
    )


def _first_core(source: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        row
        for row in source["entries"]
        if selector._core_match(row["member_name"]) is not None
    )


def _rows_for_key(source: Mapping[str, Any], key: RunKey) -> list[dict[str, Any]]:
    rows = []
    for row in source["entries"]:
        match = selector._core_match(row["member_name"])
        if match is None:
            continue
        row_key = (
            match.group("subject"),
            match.group("session"),
            int(match.group("run")),
        )
        if row_key == key:
            rows.append(row)
    return rows


def _rename_key(source: dict[str, Any], old: RunKey, new: RunKey) -> None:
    old_names = _core_names_for_key(old)
    new_names = _core_names_for_key(new)
    mapping = dict(zip(old_names, new_names, strict=True))
    for row in source["entries"]:
        name = row["member_name"]
        if name in mapping:
            row["member_name"] = mapping[name]
            row["CRC32"] = hashlib.sha256(
                mapping[name].encode("utf-8")
            ).hexdigest()[:8]


def _convert_to_aux(row: dict[str, Any], index: int) -> None:
    name = f"Freewill_generated/generated_aux/mutation-{index:04d}.txt"
    row["member_name"] = name
    row["CRC32"] = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]


def _mutated_source(source: Mapping[str, Any], mutation: str) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    entries = changed["entries"]
    aux = _first_regular_aux(changed)
    directory = _first_directory(changed)
    core = _first_core(changed)
    if mutation == "top_level_field_added":
        changed["unexpected"] = 1
    elif mutation == "schema_name_changed":
        changed["schema_name"] += ".changed"
    elif mutation == "proof_posture_changed":
        changed["proof_posture"] += ".changed"
    elif mutation == "source_provider_changed":
        changed["source_identity"]["provider"] = "changed"
    elif mutation == "transport_key_removed":
        changed["transport_body_sha256"].pop("tail")
    elif mutation == "transport_digest_malformed":
        changed["transport_body_sha256"]["tail"] = "bad"
    elif mutation == "entry_count_minus_one":
        entries.remove(aux)
    elif mutation == "regular_file_count_drift":
        aux.update(
            {
                "member_name": "Freewill_generated/generated_aux/mutation-dir/",
                "CRC32": "0" * 8,
                "compressed_size": 0,
                "compression_method": 0,
                "entry_kind": "directory",
                "uncompressed_size": 0,
            }
        )
    elif mutation == "directory_count_drift":
        directory.update(
            {
                "member_name": "Freewill_generated/generated_aux/mutation-file.txt",
                "CRC32": "0" * 8,
                "compressed_size": 1,
                "compression_method": 8,
                "entry_kind": "regular_file",
                "uncompressed_size": 1,
            }
        )
    elif mutation == "duplicate_member_name":
        aux["member_name"] = core["member_name"]
    elif mutation == "overlong_member_path":
        aux["member_name"] = "a" * 1_025
    elif mutation == "non_NFC_member_path":
        aux["member_name"] = "Freewill_generated/e\u0301.txt"
    elif mutation == "absolute_member_path":
        aux["member_name"] = "/absolute.txt"
    elif mutation == "traversal_member_path":
        aux["member_name"] = "Freewill_generated/../escape.txt"
    elif mutation == "backslash_member_path":
        aux["member_name"] = "Freewill_generated\\escape.txt"
    elif mutation == "control_character_member_path":
        aux["member_name"] = "Freewill_generated/control\n.txt"
    elif mutation == "row_field_added":
        aux["unexpected"] = 1
    elif mutation == "integer_field_boolean":
        aux["compressed_size"] = True
    elif mutation == "negative_compressed_size":
        aux["compressed_size"] = -1
    elif mutation == "encrypted_member_flag":
        aux["general_purpose_flags"] = 1
    elif mutation == "unsupported_compression_method":
        aux["compression_method"] = 99
    elif mutation == "malformed_directory_row":
        directory["compressed_size"] = 1
    elif mutation == "malformed_regular_file_row":
        aux["member_name"] += "/"
    elif mutation == "suffix_bearing_non_BIDS_path":
        aux["member_name"] = "Freewill_generated/not-bids_eeg.eeg"
    elif mutation == "wrong_task_entity":
        core["member_name"] = core["member_name"].replace(
            "task-freewill", "task-other"
        )
    elif mutation == "duplicate_run_companion":
        aux.update(copy.deepcopy(core))
        aux["local_header_offset"] += 1
    elif mutation == "incomplete_run_companion_set":
        _convert_to_aux(core, 9_001)
    elif mutation == "source_run_bundle_total_drift":
        adversary_key = ("sub-02", "ses-01", 1)
        for index, row in enumerate(_rows_for_key(changed, adversary_key)):
            _convert_to_aux(row, 9_100 + index)
    elif mutation == "eligible_session_count_drift":
        _rename_key(
            changed,
            ("sub-01", "ses-01", 6),
            ("sub-01", "ses-03", 2),
        )
    elif mutation == "split_or_reservation_drift":
        selected = next(
            row
            for row in entries
            if row["member_name"].startswith(
                "Freewill_generated/sub-08/ses-01/eeg/"
            )
        )
        selected["compressed_size"] += 1
        selected["uncompressed_size"] += 1
    else:
        raise ValueError(f"mutation is not a source mutation: {mutation}")
    return changed


def _walk_public(value: Any) -> None:
    forbidden_keys = {
        "crc32",
        "decoded_text",
        "labels",
        "member_name",
        "participant_id",
        "predictions",
        "private_manifest",
        "private_path",
        "rows",
        "signal",
        "subject_id",
        "target",
        "targets",
    }
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in forbidden_keys:
                raise SourceValidityEligibilityRefusal(
                    REFUSAL_ROUTES[6], "forbidden public field"
                )
            _walk_public(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested)
    elif isinstance(value, str) and ".codex_work" in value:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[6], "private path leaked into public output"
        )


def _assert_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_caps"]
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > caps["runtime_seconds"]
        or isinstance(peak_rss_bytes, bool)
        or not isinstance(peak_rss_bytes, int)
        or peak_rss_bytes < 0
        or peak_rss_bytes > caps["peak_RSS_bytes"]
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[7], "resource cap exceeded"
        )


def _expect_refusal(name: str, action: Callable[[], Any]) -> str:
    try:
        action()
    except SourceValidityEligibilityRefusal as exc:
        return exc.route
    raise SourceValidityEligibilityRefusal(
        REFUSAL_ROUTES[0], f"required mutation did not refuse: {name}"
    )


def run_required_mutations(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> dict[str, str]:
    required = contract["qualification"]["required_mutations"]
    routes: dict[str, str] = {}
    source_mutations = set(required[:28]) | {
        "eligible_session_count_drift",
        "split_or_reservation_drift",
    }
    for name in required:
        if name in source_mutations:
            def source_action(mutation: str = name) -> None:
                changed = _mutated_source(source, mutation)
                filtered, _counts, labels, source_hash = validate_generated_source(
                    changed,
                    contract=contract,
                    selector_contract=selector_contract,
                )
                if mutation == "split_or_reservation_drift":
                    selection = _select_from_filtered(
                        filtered, source_hash, selector_contract
                    )
                    _assert_selection(selection, contract, set(filtered))
                _ = labels

            action = source_action
        elif name == "eligible_subject_set_drift":
            def eligibility_action() -> None:
                changed_contract = copy.deepcopy(dict(contract))
                changed_contract["eligibility_policy"]["eligible_subject_count"] = 18
                _verify_contract_mapping(changed_contract)

            action = eligibility_action
        elif name == "predicate_count_drift":
            def predicate_action() -> None:
                _assert_predicate_counts(
                    {
                        **contract["expected_predicate_counts"],
                        PREDICATE_CODES[0]: 194,
                    },
                    contract,
                )

            action = predicate_action
        elif name == "ineligible_bundle_enters_candidate_set":
            filtered, _counts, _labels, source_hash = validate_generated_source(
                source,
                contract=contract,
                selector_contract=selector_contract,
            )
            selection = _select_from_filtered(
                filtered, source_hash, selector_contract
            )
            def ineligible_action() -> None:
                _assert_no_ineligible_candidates(
                    selection,
                    set(filtered) - {next(iter(_selected_run_keys(selection)))},
                )

            action = ineligible_action
        elif name == "participant_rank_drift":
            filtered, _counts, _labels, source_hash = validate_generated_source(
                source,
                contract=contract,
                selector_contract=selector_contract,
            )

            def rank_action() -> None:
                changed_contract = copy.deepcopy(dict(selector_contract))
                rank = changed_contract["participant_rank"]["full_rank"]
                rank[0], rank[1] = rank[1], rank[0]
                _select_from_filtered(filtered, source_hash, changed_contract)

            action = rank_action
        elif name == "thread_or_resource_cap_drift":
            def resource_action() -> None:
                _assert_resources(
                    contract["resource_caps"]["runtime_seconds"] + 1.0,
                    1,
                    contract,
                )

            action = resource_action
        elif name == "forbidden_public_field_or_retained_output":
            def public_output_action() -> None:
                _walk_public({"member_name": "forbidden"})

            action = public_output_action
        else:
            raise SourceValidityEligibilityRefusal(
                REFUSAL_ROUTES[0], f"required mutation is unimplemented: {name}"
            )
        routes[name] = _expect_refusal(name, action)
    if list(routes) != required or any(route not in REFUSAL_ROUTES for route in routes.values()):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "mutation route inventory differs"
        )
    return routes


def _zero_access_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_marker_output_root_or_old_executor_operations": 0,
        "archive_header_member_or_payload_operations": 0,
        "signal_event_target_label_response_quality_channel_or_geometry_reads": 0,
        "derivative_cache_feature_split_or_neurotoken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_or_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "LA2_patch_retry_rerun_resume_repair_or_reinspection_operations": 0,
        "MARC2_FW2_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
    }


def _selection_summary(selection: selector.SelectionResult) -> dict[str, Any]:
    return {
        "eligible_subjects": selection.cohort_summary["eligible_subjects"],
        "selected_subjects": selection.cohort_summary["selected_subjects"],
        "selected_run_bundles": selection.split_summary[
            "selected_run_bundles"
        ],
        "selected_core_members": selection.split_summary[
            "selected_core_members"
        ],
        "fit_run_bundles": selection.split_summary["fit_run_bundles"],
        "heldout_run_bundles": selection.split_summary[
            "heldout_run_bundles"
        ],
        "fit_heldout_overlap": selection.split_summary["fit_heldout_overlap"],
        "selected_reservation_bytes": selection.byte_summary[
            "selected_reservation_bytes"
        ],
        "reservation_cap_bytes": selection.byte_summary[
            "reservation_cap_bytes"
        ],
        "selection_identity_sha256": selection.selection_hashes[
            "selection_identity_sha256"
        ],
        "ineligible_selected_bundles": 0,
        "ineligible_selected_companions": 0,
        "target_quality_or_outcome_used": False,
    }


def _finalize_output_size(report: dict[str, Any]) -> None:
    measurement = report["measurements"]
    observed = -1
    for _ in range(8):
        measurement["aggregate_output_bytes"] = max(observed, 0)
        current = len(_canonical_json_bytes(report))
        if current == observed:
            return
        observed = current
    measurement["aggregate_output_bytes"] = observed
    if len(_canonical_json_bytes(report)) != observed:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[7], "output-size fixed point failed"
        )


def validate_public_report(report: Mapping[str, Any]) -> None:
    if (
        not isinstance(report, dict)
        or report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[6], "public report identity differs"
        )
    if any(report.get("access_counters", {}).values()):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[6], "forbidden operation counter is nonzero"
        )
    _walk_public(report)
    caps = report.get("resource_caps", {})
    measurements = report.get("measurements", {})
    if (
        measurements.get("aggregate_output_bytes", 0)
        > caps.get("generated_output_bytes", -1)
        or measurements.get("retained_generated_output_bytes") != 0
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[7], "public output cap differs"
        )


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the registered generated-only qualification in memory."""

    _validate_thread_environment()
    started = clock()
    root = Path(repo_root or _repo_root()).resolve()
    contract = load_registered_contract(root)
    fixed_input_count, fixed_input_bytes = _verify_fixed_inputs(root, contract)
    try:
        selector_contract = selector.load_registered_contract(root)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[0], "frozen selector contract load failed"
        ) from exc
    canonical = build_generated_full_source(
        row_order="canonical",
        contract=contract,
        selector_contract=selector_contract,
    )
    reversed_source = build_generated_full_source(
        row_order="reversed",
        contract=contract,
        selector_contract=selector_contract,
    )
    canonical_bytes = _canonical_source_bytes(canonical)
    reversed_bytes = _canonical_source_bytes(reversed_source)
    generated_input_bytes = len(canonical_bytes) + len(reversed_bytes)
    if generated_input_bytes > contract["resource_caps"]["generated_input_bytes"]:
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[7], "generated input cap exceeded"
        )
    filtered_a, counts_a, labels_a, source_hash_a = validate_generated_source(
        canonical,
        contract=contract,
        selector_contract=selector_contract,
    )
    filtered_b, counts_b, labels_b, source_hash_b = validate_generated_source(
        reversed_source,
        contract=contract,
        selector_contract=selector_contract,
    )
    selection_a = _select_from_filtered(
        filtered_a, source_hash_a, selector_contract
    )
    selection_b = _select_from_filtered(
        filtered_b, source_hash_b, selector_contract
    )
    _assert_selection(selection_a, contract, set(filtered_a))
    _assert_selection(selection_b, contract, set(filtered_b))
    if (
        counts_a != counts_b
        or labels_a != labels_b
        or source_hash_a != source_hash_b
        or selection_a.selection_hashes["selection_identity_sha256"]
        != selection_b.selection_hashes["selection_identity_sha256"]
        or selection_a.byte_summary != selection_b.byte_summary
    ):
        raise SourceValidityEligibilityRefusal(
            REFUSAL_ROUTES[5], "canonical and reversed replay differ"
        )
    mutation_routes = run_required_mutations(
        canonical,
        contract=contract,
        selector_contract=selector_contract,
    )
    runtime = clock() - started
    peak_rss = int(rss_reader())
    _assert_resources(runtime, peak_rss, contract)
    predicate_summary = [
        {
            "predicate_code": code,
            "bundle_count": counts_a[code],
            "companion_count": counts_a[code]
            * contract["generated_source_domain"][
                "required_companions_per_bundle"
            ],
        }
        for code in PREDICATE_CODES
    ]
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_only_qualification_passed_consumed_no_rerun",
        "route": SUCCESS_ROUTE,
        "proof_posture": GENERATED_PROOF_POSTURE,
        "registration_proof": {
            "commit": "9dedfe6f649b7f8044598c7047ddeadcd9bfab76",
            "CI_run_id": 31_942_316_544,
            "base_python_job_id": 95_153_164_447,
            "optional_neuro_job_id": 95_153_164_463,
            "both_required_jobs_green_before_implementation": True,
        },
        "source_domain_summary": {
            "inventory_rows": 1_227,
            "regular_file_rows": 1_025,
            "directory_rows": 202,
            "complete_source_run_bundles": 238,
            "complete_source_companion_rows": 952,
            "generic_auxiliary_regular_rows": 73,
            "eligible_run_bundles_after_filter": 195,
            "source_valid_but_ineligible_run_bundles": 43,
            "source_identity_sha256": source_hash_a,
            "full_source_validated_before_eligibility_filter": True,
            "exact_195_assertion_applied_after_filter": True,
        },
        "predicate_summary": predicate_summary,
        "selection_summary": _selection_summary(selection_a),
        "replay_summary": {
            "success_paths": 2,
            "canonical_reversed_source_hash_equal": True,
            "canonical_reversed_predicate_counts_equal": True,
            "canonical_reversed_selection_identity_equal": True,
        },
        "mutation_summary": {
            "required_mutations": len(mutation_routes),
            "refused_mutations": len(mutation_routes),
            "route_counts": dict(sorted(Counter(mutation_routes.values()).items())),
            "all_registered_refusal_routes_exercised": (
                set(mutation_routes.values()) == set(REFUSAL_ROUTES)
            ),
        },
        "measurements": {
            "fixed_input_artifacts": fixed_input_count + 2,
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "resource_caps": copy.deepcopy(contract["resource_caps"]),
        "access_counters": _zero_access_counters(),
        "warnings": [
            "All source rows and run identities are generated structural values.",
            "The 43 adversary assignments do not reproduce unavailable private source assignments.",
            "The frozen selector result validates mechanics only and has no scientific value.",
        ],
        "unavailable_fields": [
            "exact_private_LA1_refusal_predicate",
            "real_source_row_identity",
            "neural_signal",
            "event_or_target_content",
            "decoding_accuracy",
            "end_to_end_latency",
        ],
        "disposition": {
            "generated_closeout_consumed": True,
            "retry_or_rerun_allowed": False,
            "private_read_or_real_executor_allowed": False,
            "LA2_patch_or_reuse_allowed": False,
            "MARC2_FW2_allowed": False,
            "future_private_read_requires_fresh_Tier_C_decision": True,
        },
        "claim_boundary": copy.deepcopy(contract["claim_boundary"]),
    }
    _finalize_output_size(report)
    validate_public_report(report)
    return report


def build_plan_summary() -> dict[str, Any]:
    contract = load_registered_contract()
    return {
        "schema_name": "neurodecodekit.marc2_source_validity_eligibility_repair_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": contract["status"],
        "source_run_bundles": 238,
        "eligible_run_bundles_after_filter": 195,
        "generated_adversary_run_bundles": 43,
        "required_mutations": 36,
        "commands": contract["future_implementation_surface"]["commands"],
        "private_read_or_real_executor_allowed": False,
        "MARC2_FW2_allowed": False,
        "scientific_value": False,
    }


def build_inspection_summary() -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.marc2_source_validity_eligibility_repair_inspection",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "inspectable_aggregate_sections": [
            "source_domain_summary",
            "predicate_summary",
            "selection_summary",
            "replay_summary",
            "mutation_summary",
            "measurements",
            "warnings",
            "unavailable_fields",
        ],
        "private_row_or_path_inspection_available": False,
        "signal_target_model_or_score_inspection_available": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_source_validity_eligibility_repair",
        description=(
            "Qualify the generated MARC2 source-validity and eligibility repair."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the frozen generated-only plan.")
    subparsers.add_parser(
        "qualify", help="Run the bounded generated-only qualification in memory."
    )
    subparsers.add_parser(
        "inspect", help="Print the aggregate-safe inspection surface."
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            output = build_plan_summary()
        elif args.command == "qualify":
            output = qualify_generated()
        else:
            output = build_inspection_summary()
    except SourceValidityEligibilityRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
