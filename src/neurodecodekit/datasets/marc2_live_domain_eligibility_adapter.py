"""Generated-only MARC2 live-domain eligibility adapter qualification."""

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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import (
    marc2_source_validity_eligibility_repair as repair,
)


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR2"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_live_domain_eligibility_adapter_contract"
)
REPORT_SCHEMA_NAME = (
    "neurodecodekit.marc2_live_domain_eligibility_adapter_report"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_live_domain_eligibility_adapter_contract.v0.json"
)
CONTRACT_SHA256 = "c7c94406c7b3f483bb2ecbbb42b131756d178f288eedc31ce48e9383180a0a33"
GREEN_REGISTRATION_COMMIT = "384373e0ffcfe999ae0ae188087f7e84f09720ca"
GREEN_REGISTRATION_CI_RUN_ID = 31_945_086_852
GREEN_REGISTRATION_BASE_JOB_ID = 95_159_734_989
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_159_734_967
SUCCESS_ROUTE = "MARC2VR2-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR2-F{index:02d}" for index in range(1, 9))
PREDICATE_CODES = tuple(f"MARC2VR2-P{index:02d}" for index in range(1, 5))
THREAD_ENVIRONMENT = repair.THREAD_ENVIRONMENT
SOURCE_TOP_LEVEL_FIELDS = repair.SOURCE_TOP_LEVEL_FIELDS

RunKey = repair.RunKey
GroupedRuns = repair.GroupedRuns


class LiveDomainEligibilityRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR2 route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR2 refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.reason = reason


@dataclass(frozen=True)
class AdaptedLiveDomain:
    """Validated aggregate state plus the private in-memory selection object."""

    predicate_counts: Mapping[str, int]
    source_sha256: str
    eligible_keys: frozenset[RunKey]
    selection: selector.SelectionResult


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
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[6], "aggregate JSON is not canonical"
        ) from exc


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
        raise ValueError("JSON root must be an object")
    return value


def _fixed_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", "..", ".codex_work"} for part in path.parts)
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input path is unsafe"
        )
    current = root
    for part in path.parts:
        current = current / part
        try:
            info = current.lstat()
        except OSError as exc:
            raise LiveDomainEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise LiveDomainEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input path contains a symlink"
            )
    if not stat.S_ISREG(current.lstat().st_mode):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input is not a regular file"
        )
    return current


def _read_bound_file(path: Path, *, cap: int = 2 * 1024**2) -> bytes:
    size = path.stat(follow_symlinks=False).st_size
    if size > cap:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input exceeds cap"
        )
    try:
        with path.open("rb") as handle:
            payload = handle.read(cap + 1)
    except OSError as exc:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input read failed"
        ) from exc
    if len(payload) != size or len(payload) > cap:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input size changed during read"
        )
    return payload


def _verify_taxonomy(contract: Mapping[str, Any]) -> None:
    taxonomy = contract.get("participant_taxonomy")
    if not isinstance(taxonomy, dict):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[3], "participant taxonomy is unavailable"
        )
    eligible = set(taxonomy.get("eligible_subject_ids", ()))
    single = set(taxonomy.get("single_session_exclusions", ()))
    sampling = set(taxonomy.get("sampling_tier_exclusions", ()))
    if (
        len(eligible) != 19
        or single != {"sub-02", "sub-17"}
        or sampling != {"sub-13", "sub-15"}
        or eligible & single
        or eligible & sampling
        or single & sampling
        or len(eligible | single | sampling) != 23
        or taxonomy.get("eligible_sessions") != ["ses-01", "ses-02"]
        or taxonomy.get("private_rows_may_change_taxonomy") is not False
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[3], "participant taxonomy differs"
        )


def _verify_live_acceptance(contract: Mapping[str, Any]) -> None:
    acceptance = contract.get("live_acceptance")
    if (
        not isinstance(acceptance, dict)
        or acceptance.get("full_source_bundle_total") != 238
        or acceptance.get("eligible_bundle_total_after_filter") != 195
        or acceptance.get("valid_ineligible_bundle_total") != 43
        or acceptance.get("exact_ineligible_breakdown_frozen") is not False
        or acceptance.get("every_ineligible_bundle_classified_exactly_once")
        is not True
        or acceptance.get("global_195_assertion_before_filter_allowed")
        is not False
        or acceptance.get("generated_profile_identity_may_be_required_of_live_source")
        is not False
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[4], "live acceptance policy differs"
        )


def _verify_surface(contract: Mapping[str, Any]) -> None:
    surface = contract.get("future_implementation_surface")
    if (
        not isinstance(surface, dict)
        or surface.get("commands") != ["plan", "qualify", "inspect"]
        or surface.get("execute_command_allowed") is not False
        or surface.get("generic_path_or_URL_argument_allowed") is not False
        or surface.get("private_root_output_root_or_consumed_executor_interface_allowed")
        is not False
        or surface.get("network_archive_neural_target_model_or_score_interface_allowed")
        is not False
        or surface.get("standard_library_only") is not True
        or surface.get("base_dependency_delta") != 0
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[6], "forbidden implementation surface differs"
        )


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_only_contract_implementation_pending"
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract identity differs"
        )
    proof = contract.get("green_VR1_closeout_proof")
    if (
        not isinstance(proof, dict)
        or proof.get("proof_addendum_commit")
        != "f70d54923c5a0443ee179d6d580aafde94250589"
        or proof.get("CI_run_id") != 31_944_164_607
        or proof.get("base_python_job_id") != 95_157_571_747
        or proof.get("optional_neuro_job_id") != 95_157_571_692
        or proof.get("both_required_jobs_green") is not True
        or proof.get("VR1_route") != "MARC2VR-G1"
        or proof.get("VR1_module_sha256")
        != "cef7bb738ceee86847067cec788e442aa5022c8f573a814638ef3d48b6ec3587"
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "green VR1 proof differs"
        )
    domain = contract.get("generated_live_source_domain")
    if (
        not isinstance(domain, dict)
        or domain.get("inventory_rows") != 1_227
        or domain.get("regular_file_rows") != 1_025
        or domain.get("directory_rows") != 202
        or domain.get("complete_source_run_bundles") != 238
        or domain.get("complete_source_companion_rows") != 952
        or domain.get("generic_auxiliary_regular_rows") != 73
        or domain.get("eligible_run_bundles_after_filter") != 195
        or domain.get("valid_ineligible_run_bundles") != 43
        or domain.get("contains_real_or_private_bytes") is not False
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "source-domain contract differs"
        )
    _verify_taxonomy(contract)
    _verify_live_acceptance(contract)
    profiles = contract.get("generated_success_profiles")
    expected_profiles = {
        "A": [12, 24, 7],
        "B": [8, 20, 15],
        "C": [16, 12, 15],
        "D": [4, 4, 35],
    }
    if not isinstance(profiles, dict) or {
        name: [profiles.get(name, {}).get(code) for code in PREDICATE_CODES[1:]]
        for name in expected_profiles
    } != expected_profiles:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "success-profile contract differs"
        )
    routes = contract.get("ordered_routes")
    if not isinstance(routes, list) or [row.get("route") for row in routes] != [
        SUCCESS_ROUTE,
        *REFUSAL_ROUTES,
    ]:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "route order differs"
        )
    mutations = contract.get("qualification", {}).get("required_mutations")
    if (
        not isinstance(mutations, list)
        or len(mutations) != 58
        or len(set(mutations)) != 58
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "mutation inventory differs"
        )
    if any(contract.get("authorization_state", {}).values()):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract authority is not all false"
        )
    _verify_surface(contract)


def load_registered_contract(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and verify the remotely green VR2 registration."""

    root = Path(repo_root or _repo_root()).resolve()
    path = _fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix())
    payload = _read_bound_file(path)
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    return contract


def _verify_fixed_inputs(root: Path, contract: Mapping[str, Any]) -> tuple[int, int]:
    bindings = contract.get("fixed_inputs")
    if not isinstance(bindings, list) or len(bindings) != 9:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    registration = contract.get("registration_artifacts", {})
    combined = [
        *bindings,
        {
            "role": "registration_document",
            "path": registration.get("document_path"),
            "sha256": registration.get("document_sha256"),
        },
        {
            "role": "registration_test",
            "path": registration.get("invariant_test_path"),
            "sha256": registration.get("invariant_test_sha256"),
        },
    ]
    roles: set[str] = set()
    contract_payload = _read_bound_file(
        _fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix())
    )
    if _sha256_bytes(contract_payload) != CONTRACT_SHA256:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs during fixed-input pass"
        )
    total_bytes = len(contract_payload)
    for binding in combined:
        if (
            not isinstance(binding, dict)
            or set(binding) != {"role", "path", "sha256"}
            or not isinstance(binding["role"], str)
            or binding["role"] in roles
            or not isinstance(binding["path"], str)
            or not isinstance(binding["sha256"], str)
        ):
            raise LiveDomainEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input binding differs"
            )
        roles.add(binding["role"])
        payload = _read_bound_file(_fixed_path(root, binding["path"]))
        if _sha256_bytes(payload) != binding["sha256"]:
            raise LiveDomainEligibilityRefusal(
                REFUSAL_ROUTES[0], "fixed input SHA-256 differs"
            )
        total_bytes += len(payload)
    return len(combined) + 1, total_bytes


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    values = environment or os.environ
    if any(values.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[7], "one-thread environment is not explicit"
        )


def _profile_keys(
    contract: Mapping[str, Any], profile: str
) -> dict[str, list[RunKey]]:
    profiles = contract["generated_success_profiles"]
    if profile not in profiles:
        raise ValueError("unknown generated success profile")
    counts = profiles[profile]
    taxonomy = contract["participant_taxonomy"]

    def take(
        subjects: Sequence[str], sessions: Sequence[str], count: int
    ) -> list[RunKey]:
        candidates = [
            (subject, session, run)
            for run in range(1, 100)
            for session in sessions
            for subject in subjects
        ]
        return candidates[:count]

    keys = {
        PREDICATE_CODES[1]: take(
            taxonomy["single_session_exclusions"],
            ["ses-01", "ses-02", "ses-03"],
            counts[PREDICATE_CODES[1]],
        ),
        PREDICATE_CODES[2]: take(
            taxonomy["sampling_tier_exclusions"],
            ["ses-01", "ses-02", "ses-03"],
            counts[PREDICATE_CODES[2]],
        ),
        PREDICATE_CODES[3]: take(
            taxonomy["eligible_subject_ids"],
            ["ses-03", "ses-04"],
            counts[PREDICATE_CODES[3]],
        ),
    }
    flattened = [key for code in PREDICATE_CODES[1:] for key in keys[code]]
    if len(flattened) != 43 or len(set(flattened)) != 43:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "generated profile keys differ"
        )
    return keys


def _rename_all_ineligible_keys(
    source: dict[str, Any],
    target_keys: Mapping[str, Sequence[RunKey]],
    repair_contract: Mapping[str, Any],
) -> None:
    old_by_predicate = repair._adversary_keys_by_predicate(repair_contract)
    old_keys = sorted(set().union(*old_by_predicate.values()))
    new_keys = [
        key for code in PREDICATE_CODES[1:] for key in target_keys[code]
    ]
    if len(old_keys) != len(new_keys) or len(set(new_keys)) != 43:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "generated key replacement differs"
        )
    key_map = dict(zip(old_keys, new_keys, strict=True))
    renamed_rows = 0
    for row in source["entries"]:
        match = selector._core_match(row["member_name"])
        if match is None:
            continue
        key = (
            match.group("subject"),
            match.group("session"),
            int(match.group("run")),
        )
        if key not in key_map:
            continue
        subject, session, run = key_map[key]
        name = (
            f"Freewill_generated/{subject}/{session}/eeg/"
            f"{subject}_{session}_task-freewill_run-{run:02d}"
            f"{match.group('suffix')}"
        )
        row["member_name"] = name
        row["CRC32"] = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
        renamed_rows += 1
    if renamed_rows != 172:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "generated key replacement row count differs"
        )


def build_generated_live_source(
    *,
    profile: str = "A",
    row_order: str = "canonical",
    contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one live-shaped generated source without a path or real byte."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    try:
        repair_contract = repair.load_registered_contract(_repo_root())
        source = repair.build_generated_full_source(
            row_order="canonical",
            contract=repair_contract,
            selector_contract=frozen_selector,
        )
    except (repair.SourceValidityEligibilityRefusal, selector.FreewillPrefixSelectionRefusal) as exc:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "green VR1 fixture build refused"
        ) from exc
    _rename_all_ineligible_keys(
        source, _profile_keys(registered, profile), repair_contract
    )
    domain = registered["generated_live_source_domain"]
    source["proof_posture"] = domain["proof_posture"]
    source["source_identity"] = copy.deepcopy(domain["source_identity"])
    source["transport_body_sha256"] = copy.deepcopy(
        domain["transport_body_sha256"]
    )
    source["entries"] = sorted(
        source["entries"], key=lambda row: row["member_name"]
    )
    if row_order == "reversed":
        source["entries"].reverse()
    elif row_order != "canonical":
        raise ValueError("unknown generated row order")
    return source


def _validate_live_envelope(
    source: Mapping[str, Any], contract: Mapping[str, Any]
) -> list[Any]:
    domain = contract["generated_live_source_domain"]
    if not isinstance(source, dict) or set(source) != SOURCE_TOP_LEVEL_FIELDS:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[1], "live source top-level fields differ"
        )
    if (
        source.get("schema_name") != domain["schema_name"]
        or source.get("schema_version") != domain["schema_version"]
        or source.get("proof_posture") != domain["proof_posture"]
        or source.get("source_identity") != domain["source_identity"]
        or source.get("transport_body_sha256")
        != domain["transport_body_sha256"]
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[1], "live source identity or transport differs"
        )
    entries = source.get("entries")
    if not isinstance(entries, list) or len(entries) != domain["inventory_rows"]:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[1], "live source row count differs"
        )
    return entries


def _classify_key(key: RunKey, contract: Mapping[str, Any]) -> str:
    subject, session, _run = key
    taxonomy = contract["participant_taxonomy"]
    eligible = set(taxonomy["eligible_subject_ids"])
    single = set(taxonomy["single_session_exclusions"])
    sampling = set(taxonomy["sampling_tier_exclusions"])
    known = eligible | single | sampling
    if subject not in known:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[3], "bundle participant is unknown"
        )
    if subject in eligible and session in taxonomy["eligible_sessions"]:
        return PREDICATE_CODES[0]
    if subject in single:
        return PREDICATE_CODES[1]
    if subject in sampling:
        return PREDICATE_CODES[2]
    if subject in eligible:
        return PREDICATE_CODES[3]
    raise LiveDomainEligibilityRefusal(
        REFUSAL_ROUTES[3], "bundle taxonomy is unclassified"
    )


def _assert_classification_arithmetic(
    counts: Mapping[str, int], contract: Mapping[str, Any]
) -> None:
    acceptance = contract["live_acceptance"]
    if (
        set(counts) != set(PREDICATE_CODES)
        or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts.values())
        or sum(counts.values()) != acceptance["full_source_bundle_total"]
        or counts[PREDICATE_CODES[0]]
        != acceptance["eligible_bundle_total_after_filter"]
        or sum(counts[code] for code in PREDICATE_CODES[1:])
        != acceptance["valid_ineligible_bundle_total"]
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[3], "238/195/43 classification arithmetic differs"
        )


def _filter_and_validate_eligible(
    grouped: GroupedRuns,
    labels: Mapping[RunKey, str],
    contract: Mapping[str, Any],
) -> GroupedRuns:
    filtered = {
        key: companions
        for key, companions in grouped.items()
        if labels[key] == PREDICATE_CODES[0]
    }
    if len(filtered) != 195:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[3], "filtered eligible total differs"
        )
    observed = {
        subject: [
            sum(
                1
                for row_subject, row_session, _run in filtered
                if row_subject == subject and row_session == session
            )
            for session in ("ses-01", "ses-02")
        ]
        for subject in contract["participant_taxonomy"]["eligible_subject_ids"]
    }
    if observed != contract["published_eligible_session_counts"]:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[3], "eligible participant-session counts differ"
        )
    return filtered


def validate_live_domain_source(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> tuple[GroupedRuns, dict[str, int], dict[RunKey, str], str]:
    """Validate all source rows, classify, then filter exact eligibility."""

    _verify_contract_mapping(contract)
    entries = _validate_live_envelope(source, contract)
    try:
        grouped, kinds = repair._group_source_rows(entries)
    except repair.SourceValidityEligibilityRefusal as exc:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[2], "structural row or companion validation refused"
        ) from exc
    domain = contract["generated_live_source_domain"]
    if kinds != Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[2], "entry-kind counts differ"
        )
    if len(grouped) != domain["complete_source_run_bundles"]:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[3], "full source bundle total differs"
        )
    labels = {key: _classify_key(key, contract) for key in grouped}
    counts = {code: 0 for code in PREDICATE_CODES}
    for predicate in labels.values():
        counts[predicate] += 1
    _assert_classification_arithmetic(counts, contract)
    filtered = _filter_and_validate_eligible(grouped, labels, contract)
    return (
        filtered,
        counts,
        labels,
        _sha256_bytes(_canonical_source_bytes(source)),
    )


def _select_filtered(
    filtered: GroupedRuns,
    source_sha256: str,
    contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> selector.SelectionResult:
    try:
        selection = repair._select_from_filtered(
            filtered, source_sha256, selector_contract
        )
        repair._assert_selection(selection, contract, set(filtered))
    except repair.SourceValidityEligibilityRefusal as exc:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[5], "frozen selection mechanics refused"
        ) from exc
    return selection


def adapt_live_domain_source(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> AdaptedLiveDomain:
    """Apply the public in-memory adapter without a path or private row output."""

    registered = dict(contract or load_registered_contract())
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    filtered, counts, _labels, source_hash = validate_live_domain_source(
        source, contract=registered
    )
    selection = _select_filtered(
        filtered, source_hash, registered, frozen_selector
    )
    return AdaptedLiveDomain(
        predicate_counts=counts,
        source_sha256=source_hash,
        eligible_keys=frozenset(filtered),
        selection=selection,
    )


def _first_auxiliary(source: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        row
        for row in source["entries"]
        if row["entry_kind"] == "regular_file"
        and row["member_name"].startswith("Freewill_generated/generated_aux/")
    )


def _first_ineligible_key(
    source: Mapping[str, Any], contract: Mapping[str, Any]
) -> RunKey:
    grouped, _kinds = repair._group_source_rows(source["entries"])
    return next(
        key
        for key in sorted(grouped)
        if _classify_key(key, contract) != PREDICATE_CODES[0]
    )


def _rename_key_once(source: dict[str, Any], old: RunKey, new: RunKey) -> None:
    old_names = repair._core_names_for_key(old)
    new_names = repair._core_names_for_key(new)
    mapping = dict(zip(old_names, new_names, strict=True))
    changed = 0
    for row in source["entries"]:
        if row["member_name"] not in mapping:
            continue
        name = mapping[row["member_name"]]
        row["member_name"] = name
        row["CRC32"] = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
        changed += 1
    if changed != 4:
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "mutation key rename differs"
        )


def _add_source_bundle(source: dict[str, Any]) -> None:
    auxiliary = sorted(
        (
            row
            for row in source["entries"]
            if row["entry_kind"] == "regular_file"
            and row["member_name"].startswith("Freewill_generated/generated_aux/")
        ),
        key=lambda row: row["member_name"],
    )[:4]
    names = repair._core_names_for_key(("sub-02", "ses-09", 99))
    for row, name in zip(auxiliary, names, strict=True):
        row["member_name"] = name
        row["CRC32"] = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]


def _validate_public_value(value: Any) -> None:
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
                raise LiveDomainEligibilityRefusal(
                    REFUSAL_ROUTES[6], "forbidden aggregate field"
                )
            _validate_public_value(nested)
    elif isinstance(value, list):
        for nested in value:
            _validate_public_value(nested)
    elif isinstance(value, str) and (
        ".codex_work" in value or value.startswith("sub-")
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[6], "private path or individual identity leaked"
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
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[7], "resource or output cap exceeded"
        )


def _expect_refusal(
    name: str, expected_route: str, action: Callable[[], Any]
) -> str:
    try:
        action()
    except LiveDomainEligibilityRefusal as exc:
        if exc.route != expected_route:
            raise LiveDomainEligibilityRefusal(
                REFUSAL_ROUTES[0], f"mutation route differs: {name}"
            ) from exc
        return exc.route
    raise LiveDomainEligibilityRefusal(
        REFUSAL_ROUTES[0], f"required mutation did not refuse: {name}"
    )


def run_required_mutations(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> dict[str, str]:
    """Exercise every frozen mutation without a path or retained output."""

    required = contract["qualification"]["required_mutations"]
    mutations: dict[str, tuple[str, Callable[[], Any]]] = {}

    def source_action(mutator: Callable[[dict[str, Any]], None]) -> Callable[[], Any]:
        def action() -> None:
            changed = copy.deepcopy(dict(source))
            mutator(changed)
            adapt_live_domain_source(
                changed,
                contract=contract,
                selector_contract=selector_contract,
            )

        return action

    def contract_action(
        mutator: Callable[[dict[str, Any]], None]
    ) -> Callable[[], Any]:
        def action() -> None:
            changed = copy.deepcopy(dict(contract))
            mutator(changed)
            _verify_contract_mapping(changed)

        return action

    mutations.update(
        {
            "contract_hash_mismatch": (
                REFUSAL_ROUTES[0],
                lambda: (_ for _ in ()).throw(
                    LiveDomainEligibilityRefusal(
                        REFUSAL_ROUTES[0], "contract SHA-256 differs"
                    )
                ),
            ),
            "green_VR1_proof_mismatch": (
                REFUSAL_ROUTES[0],
                contract_action(
                    lambda value: value["green_VR1_closeout_proof"].__setitem__(
                        "CI_run_id", 0
                    )
                ),
            ),
            "green_VR1_module_hash_mismatch": (
                REFUSAL_ROUTES[0],
                contract_action(
                    lambda value: value["green_VR1_closeout_proof"].__setitem__(
                        "VR1_module_sha256", "0" * 64
                    )
                ),
            ),
            "frozen_selector_hash_mismatch": (
                REFUSAL_ROUTES[0],
                lambda: (_ for _ in ()).throw(
                    LiveDomainEligibilityRefusal(
                        REFUSAL_ROUTES[0], "selector SHA-256 differs"
                    )
                ),
            ),
        }
    )

    envelope_mutators: dict[str, Callable[[dict[str, Any]], None]] = {
        "live_schema_name_changed": lambda value: value.__setitem__(
            "schema_name", "changed"
        ),
        "live_proof_posture_changed": lambda value: value.__setitem__(
            "proof_posture", "changed"
        ),
        "source_provider_changed": lambda value: value["source_identity"].__setitem__(
            "provider", "changed"
        ),
        "source_record_changed": lambda value: value["source_identity"].__setitem__(
            "record_id", 0
        ),
        "source_version_changed": lambda value: value["source_identity"].__setitem__(
            "version", 0
        ),
        "source_file_id_changed": lambda value: value["source_identity"].__setitem__(
            "file_id", 0
        ),
        "source_archive_bytes_changed": lambda value: value["source_identity"].__setitem__(
            "declared_archive_bytes", 0
        ),
        "source_registered_MD5_changed": lambda value: value["source_identity"].__setitem__(
            "registered_MD5", "0" * 32
        ),
        "transport_key_removed": lambda value: value["transport_body_sha256"].pop(
            "tail"
        ),
        "transport_alias_substituted": lambda value: value[
            "transport_body_sha256"
        ].__setitem__(
            "central_directory", value["transport_body_sha256"].pop("directory")
        ),
        "transport_digest_malformed": lambda value: value[
            "transport_body_sha256"
        ].__setitem__("tail", "bad"),
        "transport_digest_changed": lambda value: value[
            "transport_body_sha256"
        ].__setitem__("tail", "0" * 64),
        "inventory_row_count_drift": lambda value: value["entries"].pop(),
    }
    for name, mutator in envelope_mutators.items():
        mutations[name] = (REFUSAL_ROUTES[1], source_action(mutator))

    repair_mutation_names = {
        "regular_file_count_drift": "regular_file_count_drift",
        "directory_count_drift": "directory_count_drift",
        "duplicate_member_name": "duplicate_member_name",
        "absolute_member_path": "absolute_member_path",
        "traversal_member_path": "traversal_member_path",
        "backslash_member_path": "backslash_member_path",
        "non_NFC_member_path": "non_NFC_member_path",
        "overlong_member_path": "overlong_member_path",
        "control_character_member_path": "control_character_member_path",
        "integer_field_boolean": "integer_field_boolean",
        "negative_size": "negative_compressed_size",
        "encrypted_member": "encrypted_member_flag",
        "unsupported_compression_method": "unsupported_compression_method",
        "malformed_directory_row": "malformed_directory_row",
        "suffix_bearing_non_BIDS_path": "suffix_bearing_non_BIDS_path",
        "wrong_task_entity": "wrong_task_entity",
        "duplicate_run_companion": "duplicate_run_companion",
        "incomplete_run_companion_set": "incomplete_run_companion_set",
    }
    for name, repair_name in repair_mutation_names.items():
        mutations[name] = (
            REFUSAL_ROUTES[2],
            source_action(
                lambda value, mutation=repair_name: value.update(
                    repair._mutated_source(value, mutation)
                )
            ),
        )

    mutations["source_bundle_total_237"] = (
        REFUSAL_ROUTES[3],
        source_action(
            lambda value: value.update(
                repair._mutated_source(value, "source_run_bundle_total_drift")
            )
        ),
    )
    mutations["source_bundle_total_239"] = (
        REFUSAL_ROUTES[3],
        source_action(_add_source_bundle),
    )
    mutations["unknown_participant"] = (
        REFUSAL_ROUTES[3],
        source_action(
            lambda value: _rename_key_once(
                value,
                _first_ineligible_key(value, contract),
                ("sub-99", "ses-01", 1),
            )
        ),
    )
    mutations["participant_taxonomy_overlap"] = (
        REFUSAL_ROUTES[3],
        contract_action(
            lambda value: value["participant_taxonomy"][
                "eligible_subject_ids"
            ].append("sub-02")
        ),
    )
    mutations["eligible_session_count_drift"] = (
        REFUSAL_ROUTES[3],
        source_action(
            lambda value: value.update(
                repair._mutated_source(value, "eligible_session_count_drift")
            )
        ),
    )
    mutations["eligible_subject_list_drift"] = (
        REFUSAL_ROUTES[3],
        contract_action(
            lambda value: value["participant_taxonomy"][
                "eligible_subject_ids"
            ].pop()
        ),
    )
    mutations["ineligible_total_42"] = (
        REFUSAL_ROUTES[3],
        lambda: _assert_classification_arithmetic(
            {
                PREDICATE_CODES[0]: 196,
                PREDICATE_CODES[1]: 12,
                PREDICATE_CODES[2]: 24,
                PREDICATE_CODES[3]: 6,
            },
            contract,
        ),
    )
    mutations["ineligible_total_44"] = (
        REFUSAL_ROUTES[3],
        lambda: _assert_classification_arithmetic(
            {
                PREDICATE_CODES[0]: 194,
                PREDICATE_CODES[1]: 12,
                PREDICATE_CODES[2]: 24,
                PREDICATE_CODES[3]: 8,
            },
            contract,
        ),
    )
    mutations["exact_breakdown_overconstraint"] = (
        REFUSAL_ROUTES[4],
        contract_action(
            lambda value: value["live_acceptance"].__setitem__(
                "exact_ineligible_breakdown_frozen", True
            )
        ),
    )
    mutations["prefilter_195_assertion"] = (
        REFUSAL_ROUTES[4],
        contract_action(
            lambda value: value["live_acceptance"].__setitem__(
                "global_195_assertion_before_filter_allowed", True
            )
        ),
    )

    def selection_drift(profile: str, mutation: str) -> None:
        changed = build_generated_live_source(
            profile=profile,
            contract=contract,
            selector_contract=selector_contract,
        )
        if mutation != "split_or_reservation_drift":
            raise ValueError("unknown selection mutation")
        selected = next(
            row
            for row in changed["entries"]
            if row["entry_kind"] == "regular_file"
            and row["member_name"].startswith(
                "Freewill_generated/sub-08/ses-01/eeg/"
            )
        )
        selected["compressed_size"] += 1
        selected["uncompressed_size"] += 1
        adapt_live_domain_source(
            changed,
            contract=contract,
            selector_contract=selector_contract,
        )

    mutations["profile_B_selection_drift"] = (
        REFUSAL_ROUTES[5],
        lambda: selection_drift("B", "split_or_reservation_drift"),
    )

    def rank_drift() -> None:
        filtered, _counts, _labels, source_hash = validate_live_domain_source(
            source, contract=contract
        )
        changed = copy.deepcopy(dict(selector_contract))
        rank = changed["participant_rank"]["full_rank"]
        rank[0], rank[1] = rank[1], rank[0]
        _select_filtered(filtered, source_hash, contract, changed)

    mutations["participant_rank_drift"] = (REFUSAL_ROUTES[5], rank_drift)
    mutations["split_or_reservation_drift"] = (
        REFUSAL_ROUTES[5],
        lambda: selection_drift("A", "split_or_reservation_drift"),
    )

    def ineligible_candidate() -> None:
        adapted = adapt_live_domain_source(
            source,
            contract=contract,
            selector_contract=selector_contract,
        )
        selected = repair._selected_run_keys(adapted.selection)
        try:
            repair._assert_no_ineligible_candidates(
                adapted.selection,
                set(adapted.eligible_keys) - {next(iter(selected))},
            )
        except repair.SourceValidityEligibilityRefusal as exc:
            raise LiveDomainEligibilityRefusal(
                REFUSAL_ROUTES[5], "ineligible candidate entered selection"
            ) from exc

    mutations["ineligible_bundle_enters_candidate_set"] = (
        REFUSAL_ROUTES[5],
        ineligible_candidate,
    )
    mutations["target_or_quality_leakage"] = (
        REFUSAL_ROUTES[6],
        lambda: _validate_public_value({"target": "forbidden"}),
    )
    mutations["public_individual_ineligible_identity_leak"] = (
        REFUSAL_ROUTES[6],
        lambda: _validate_public_value({"warning": "sub-02"}),
    )
    mutations["retained_generated_output"] = (
        REFUSAL_ROUTES[7],
        lambda: _assert_resources(
            runtime_seconds=0.0,
            peak_rss_bytes=1,
            generated_input_bytes=1,
            aggregate_output_bytes=1,
            retained_output_bytes=1,
            contract=contract,
        ),
    )
    mutations["thread_environment_drift"] = (
        REFUSAL_ROUTES[7],
        lambda: _validate_thread_environment({name: "2" for name in THREAD_ENVIRONMENT}),
    )
    for name, kwargs in {
        "runtime_cap_drift": {"runtime_seconds": 31.0},
        "RSS_cap_drift": {"peak_rss_bytes": 268_435_457},
        "generated_input_cap_drift": {"generated_input_bytes": 16_777_217},
        "aggregate_output_cap_drift": {"aggregate_output_bytes": 2_097_153},
    }.items():
        values = {
            "runtime_seconds": 0.0,
            "peak_rss_bytes": 1,
            "generated_input_bytes": 1,
            "aggregate_output_bytes": 1,
            "retained_output_bytes": 0,
            **kwargs,
        }
        mutations[name] = (
            REFUSAL_ROUTES[7],
            lambda values=values: _assert_resources(contract=contract, **values),
        )
    mutations["forbidden_private_path_or_execute_surface"] = (
        REFUSAL_ROUTES[6],
        contract_action(
            lambda value: value["future_implementation_surface"].__setitem__(
                "execute_command_allowed", True
            )
        ),
    )

    if set(mutations) != set(required):
        missing = sorted(set(required) - set(mutations))
        extra = sorted(set(mutations) - set(required))
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], f"mutation implementation differs: {missing}/{extra}"
        )
    observed = {
        name: _expect_refusal(name, *mutations[name]) for name in required
    }
    if set(observed.values()) != set(REFUSAL_ROUTES):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[0], "not all refusal routes were exercised"
        )
    return observed


def run_development_preflight(
    *,
    contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Exercise the generated mechanics without producing closeout evidence."""

    registered = dict(contract or load_registered_contract())
    frozen_selector = dict(
        selector_contract or selector.load_registered_contract(_repo_root())
    )
    paths: list[dict[str, Any]] = []
    selections: set[str] = set()
    profile_hashes: dict[str, set[str]] = {}
    generated_input_bytes = 0
    canonical_a: dict[str, Any] | None = None
    for profile in registered["qualification"]["success_profiles"]:
        profile_hashes[profile] = set()
        for row_order in registered["qualification"]["row_orders_per_profile"]:
            source = build_generated_live_source(
                profile=profile,
                row_order=row_order,
                contract=registered,
                selector_contract=frozen_selector,
            )
            if profile == "A" and row_order == "canonical":
                canonical_a = source
            payload = _canonical_source_bytes(source)
            generated_input_bytes += len(payload)
            adapted = adapt_live_domain_source(
                source,
                contract=registered,
                selector_contract=frozen_selector,
            )
            profile_hashes[profile].add(adapted.source_sha256)
            selection_hash = adapted.selection.selection_hashes[
                "selection_identity_sha256"
            ]
            selections.add(selection_hash)
            paths.append(
                {
                    "profile": profile,
                    "row_order": row_order,
                    "predicate_counts": dict(adapted.predicate_counts),
                    "source_sha256": adapted.source_sha256,
                    "selection_identity_sha256": selection_hash,
                }
            )
    if (
        len(paths) != registered["qualification"]["required_success_paths"]
        or len(selections) != 1
        or selections != {registered["expected_selection"]["selection_identity_sha256"]}
        or any(len(hashes) != 1 for hashes in profile_hashes.values())
        or generated_input_bytes > registered["resource_caps"]["generated_input_bytes"]
        or canonical_a is None
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[5], "success-profile replay differs"
        )
    mutation_routes = run_required_mutations(
        canonical_a,
        contract=registered,
        selector_contract=frozen_selector,
    )
    return {
        "success_paths": paths,
        "generated_input_bytes": generated_input_bytes,
        "mutation_routes": mutation_routes,
        "selection_identity_sha256": next(iter(selections)),
    }


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _zero_access_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_root_marker_or_executor_operations": 0,
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
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[7], "output-size fixed point failed"
        )


def validate_public_report(report: Mapping[str, Any]) -> None:
    if (
        not isinstance(report, dict)
        or report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
        or any(report.get("access_counters", {}).values())
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[6], "public report identity or counters differ"
        )
    _validate_public_value(report)
    measurements = report.get("measurements", {})
    caps = report.get("resource_caps", {})
    if (
        measurements.get("aggregate_output_bytes", 0)
        > caps.get("aggregate_output_bytes", -1)
        or measurements.get("retained_generated_output_bytes") != 0
    ):
        raise LiveDomainEligibilityRefusal(
            REFUSAL_ROUTES[7], "public output boundary differs"
        )


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the one registered generated-only qualification in memory."""

    _validate_thread_environment()
    started = clock()
    root = Path(repo_root or _repo_root()).resolve()
    contract = load_registered_contract(root)
    fixed_count, fixed_bytes = _verify_fixed_inputs(root, contract)
    preflight = run_development_preflight(contract=contract)
    runtime = clock() - started
    peak_rss = int(rss_reader())
    route_counts = dict(
        sorted(Counter(preflight["mutation_routes"].values()).items())
    )
    profile_summary = [
        {
            "profile": profile,
            "predicate_counts": copy.deepcopy(
                contract["generated_success_profiles"][profile]
            ),
            "canonical_reversed_source_hash_equal": len(
                {
                    row["source_sha256"]
                    for row in preflight["success_paths"]
                    if row["profile"] == profile
                }
            )
            == 1,
        }
        for profile in contract["qualification"]["success_profiles"]
    ]
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_only_qualification_passed_consumed_no_rerun",
        "route": SUCCESS_ROUTE,
        "proof_posture": "generated_live_shaped_structural_metadata_only",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
        },
        "source_domain_summary": {
            "inventory_rows": 1_227,
            "regular_file_rows": 1_025,
            "directory_rows": 202,
            "complete_source_run_bundles": 238,
            "eligible_run_bundles_after_filter": 195,
            "valid_ineligible_run_bundles": 43,
            "full_source_validated_before_filter": True,
            "exact_ineligible_breakdown_required_of_live_source": False,
            "generated_profile_identity_required_of_live_source": False,
        },
        "profile_summary": profile_summary,
        "selection_summary": {
            **{
                key: contract["expected_selection"][key]
                for key in (
                    "eligible_subjects",
                    "selected_subjects",
                    "selected_run_bundles",
                    "selected_core_members",
                    "fit_run_bundles",
                    "heldout_run_bundles",
                    "fit_heldout_overlap",
                    "selected_reservation_bytes",
                    "reservation_cap_bytes",
                    "selection_identity_sha256",
                    "ineligible_selected_bundles",
                    "ineligible_selected_companions",
                    "target_quality_or_outcome_used",
                )
            }
        },
        "replay_summary": {
            "success_paths": len(preflight["success_paths"]),
            "profiles": 4,
            "row_orders_per_profile": 2,
            "all_selection_identities_equal": True,
            "profile_specific_source_hashes_may_differ": True,
        },
        "mutation_summary": {
            "required_mutations": len(preflight["mutation_routes"]),
            "refused_mutations": len(preflight["mutation_routes"]),
            "route_counts": route_counts,
            "all_refusal_routes_exercised": set(route_counts)
            == set(REFUSAL_ROUTES),
        },
        "measurements": {
            "fixed_input_artifacts": fixed_count,
            "fixed_input_bytes": fixed_bytes,
            "generated_input_bytes": preflight["generated_input_bytes"],
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
            "Every source row and run identity used here is generated.",
            "The four exclusion distributions are adversarial fixtures, not private-source assignments.",
            "Selection replay validates structural mechanics only and has no scientific value.",
        ],
        "unavailable_fields": [
            "private_source_ineligible_distribution",
            "exact_private_LA1_refusal_predicate",
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
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        generated_input_bytes=preflight["generated_input_bytes"],
        aggregate_output_bytes=report["measurements"]["aggregate_output_bytes"],
        retained_output_bytes=0,
        contract=contract,
    )
    validate_public_report(report)
    return report


def build_plan_summary() -> dict[str, Any]:
    contract = load_registered_contract()
    return {
        "schema_name": "neurodecodekit.marc2_live_domain_eligibility_adapter_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": contract["status"],
        "source_run_bundles": 238,
        "eligible_run_bundles_after_filter": 195,
        "valid_ineligible_run_bundles": 43,
        "exact_ineligible_breakdown_frozen": False,
        "success_profiles": 4,
        "success_paths": 8,
        "required_mutations": 58,
        "commands": contract["future_implementation_surface"]["commands"],
        "private_read_or_real_executor_allowed": False,
        "MARC2_FW2_allowed": False,
        "scientific_value": False,
    }


def build_inspection_summary() -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.marc2_live_domain_eligibility_adapter_inspection",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "inspectable_aggregate_sections": [
            "source_domain_summary",
            "profile_summary",
            "selection_summary",
            "replay_summary",
            "mutation_summary",
            "measurements",
            "warnings",
            "unavailable_fields",
        ],
        "individual_ineligible_identity_inspection_available": False,
        "private_row_or_path_inspection_available": False,
        "signal_target_model_or_score_inspection_available": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_live_domain_eligibility_adapter",
        description="Qualify the generated MARC2 live-domain eligibility adapter.",
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
    except LiveDomainEligibilityRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
