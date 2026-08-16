"""Generated-only MARC2 producer-to-selector transport adapter."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import resource
import stat
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector


SCHEMA_VERSION = "0.1.0"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_transport_alias_adapter_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_transport_alias_adapter_qualification"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_transport_alias_adapter_contract.v0.json"
)
CONTRACT_SHA256 = "020b6f60234869cee446f732ed070ded4f98c4bd3ea495e4734e77f6a31405aa"
GREEN_REGISTRATION_COMMIT = "0c0e1c8a08ff7e68d0e4432a64dde8a85fb0274f"
GREEN_REGISTRATION_CI_RUN_ID = 31_932_701_989
GREEN_REGISTRATION_BASE_JOB_ID = 95_129_832_134
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_129_832_169
SOURCE_PROOF_POSTURE = "generated_producer_native_private_metadata_only"
SOURCE_PROVIDER = "generated_producer_fixture"
SELECTOR_PROOF_POSTURE = "generated_fixture_private_metadata_only"
SELECTOR_PROVIDER = "generated_fixture"
SUCCESS_ROUTE = "MARC2TA-G1-generated_producer_adapter_selector_integration_passed"
REFUSAL_ROUTES = (
    "MARC2TA-F01-contract_or_artifact_identity",
    "MARC2TA-F02-source_manifest_schema",
    "MARC2TA-F03-transport_alias_or_digest",
    "MARC2TA-F04-copy_value_or_replay_integrity",
    "MARC2TA-F05-selector_integration_or_result",
    "MARC2TA-F06-private_target_model_network_or_claim_boundary",
    "MARC2TA-F07-resource_or_output_cap",
)
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
SOURCE_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "proof_posture",
        "source_identity",
        "transport_body_sha256",
        "entries",
    }
)
SOURCE_IDENTITY_FIELDS = frozenset(
    {
        "provider",
        "record_id",
        "version",
        "file_id",
        "declared_archive_bytes",
        "registered_MD5",
        "whole_archive_downloaded",
        "member_payload_opened",
    }
)
SOURCE_TRANSPORT_KEYS = frozenset({"directory", "metadata", "tail"})
SELECTOR_TRANSPORT_KEYS = frozenset(
    {"central_directory", "metadata", "tail"}
)
SHA256_HEX = frozenset("0123456789abcdef")
ACCESS_COUNTER_KEYS = (
    "private_or_Git_ignored_path_operations",
    "consumed_marker_or_output_root_operations",
    "archive_local_header_or_member_payload_reads",
    "signal_event_target_label_quality_channel_or_geometry_reads",
    "derivative_cache_feature_split_or_neurotoken_operations",
    "training_inference_prediction_freeze_delivery_or_score_operations",
    "network_download_provider_or_language_model_operations",
    "stream_device_or_hardware_operations",
    "consumed_executor_patch_retry_rerun_resume_or_repair_operations",
    "MARC2_FW2_operations",
    "scientific_claim_upgrades",
)
REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "proof_posture",
        "green_registration",
        "contract",
        "adapter_summary",
        "fixture_summary",
        "selector_summary",
        "replay_summary",
        "mutation_summary",
        "measurements",
        "access_counters",
        "acceptance_gates",
        "route",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)


class TransportAliasAdapterRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC2-TA1 route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-TA1 refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class SourceValidation:
    """Validated generated source identity before adaptation."""

    canonical_sha256: str
    entry_count: int
    regular_file_count: int
    directory_count: int
    source_run_bundles: int
    transport_hashes: Mapping[str, str]


@dataclass(frozen=True)
class QualificationOutcome:
    """One bounded generated-only qualification result."""

    report: Mapping[str, Any]
    report_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _canonical_manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
    canonical = copy.deepcopy(dict(manifest))
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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _strict_json(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError("UTF-8 BOM is forbidden")
    value = json.loads(
        payload.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda _value: (_ for _ in ()).throw(
            ValueError("non-finite JSON value")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root is not an object")
    return value


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("contract_id")
        != "MARC-2-generated-source-native-transport-alias-adapter-v0"
        or contract.get("lane_id") != "MARC2-TA1"
        or contract.get("status")
        != "frozen_generated_only_adapter_contract_implementation_pending"
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "contract identity differs"
        )
    adapter = contract.get("adapter_contract")
    if not isinstance(adapter, dict) or adapter.get("single_alias") != {
        "source_key": "directory",
        "selector_key": "central_directory",
    }:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "registered alias differs"
        )
    qualification = contract.get("qualification")
    if (
        not isinstance(qualification, dict)
        or qualification.get("required_mutation_count") != 26
        or len(qualification.get("required_mutations", ())) != 26
        or len(set(qualification.get("required_mutations", ()))) != 26
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "mutation inventory differs"
        )
    if any(contract.get("authorization_state", {}).values()):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "live authority differs"
        )


def load_registered_contract(
    repo_root: str | Path | None = None,
    *,
    verify_fixed_inputs: bool = True,
) -> dict[str, Any]:
    """Load the exact registration that passed both remote jobs."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    if verify_fixed_inputs:
        for binding in contract["fixed_inputs"]:
            fixed = root / binding["path"]
            try:
                observed = _sha256_file(fixed)
            except OSError as exc:
                raise TransportAliasAdapterRefusal(
                    REFUSAL_ROUTES[0], "fixed artifact is unavailable"
                ) from exc
            if observed != binding["sha256"]:
                raise TransportAliasAdapterRefusal(
                    REFUSAL_ROUTES[0], "fixed artifact SHA-256 differs"
                )
    return contract


def build_generated_source_manifest(
    *,
    row_order: str = "canonical",
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a generated producer-native source without human content."""

    registered = dict(selector_contract or selector.load_registered_contract())
    source = copy.deepcopy(
        selector.build_generated_manifest(
            row_order=row_order,
            contract=registered,
        )
    )
    source["proof_posture"] = SOURCE_PROOF_POSTURE
    source["source_identity"]["provider"] = SOURCE_PROVIDER
    transport = source["transport_body_sha256"]
    transport["directory"] = transport.pop("central_directory")
    return source


def _validate_digest(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in SHA256_HEX for character in value)
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[2], "transport digest differs"
        )
    return value


def _validate_source_identity(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != SOURCE_IDENTITY_FIELDS:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source identity fields differ"
        )
    expected = {
        "provider": SOURCE_PROVIDER,
        "record_id": 28_632_599,
        "version": 1,
        "file_id": 0,
        "declared_archive_bytes": 13_591_548_048,
        "registered_MD5": "0" * 32,
        "whole_archive_downloaded": False,
        "member_payload_opened": False,
    }
    if value != expected:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source identity differs"
        )


def _validate_source_manifest(
    manifest: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> SourceValidation:
    """Validate every source field before copying or mapping the alias."""

    if not isinstance(manifest, dict) or set(manifest) != SOURCE_TOP_LEVEL_FIELDS:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source top-level fields differ"
        )
    if (
        manifest["schema_name"]
        != "neurodecodekit.marc1_central_directory_private_manifest"
        or manifest["schema_version"] != SCHEMA_VERSION
        or manifest["proof_posture"] != SOURCE_PROOF_POSTURE
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source schema identity differs"
        )
    _validate_source_identity(manifest["source_identity"])
    transport = manifest["transport_body_sha256"]
    if not isinstance(transport, dict) or set(transport) != SOURCE_TRANSPORT_KEYS:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[2], "source transport aliases differ"
        )
    hashes = {key: _validate_digest(transport[key]) for key in sorted(transport)}

    entries = manifest["entries"]
    if not isinstance(entries, list) or len(entries) != selector.EXPECTED_ROWS:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source entry count differs"
        )
    names: set[str] = set()
    kinds: Counter[str] = Counter()
    grouped: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    try:
        for row in entries:
            name, match = selector._validate_entry(row)
            if name in names:
                raise TransportAliasAdapterRefusal(
                    REFUSAL_ROUTES[1], "source member identity is duplicated"
                )
            names.add(name)
            kinds[row["entry_kind"]] += 1
            if match is not None:
                key = (
                    match.group("subject"),
                    match.group("session"),
                    int(match.group("run")),
                )
                suffix = match.group("suffix")
                if suffix in grouped[key]:
                    raise TransportAliasAdapterRefusal(
                        REFUSAL_ROUTES[1], "source run companion is duplicated"
                    )
                grouped[key].add(suffix)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source entry schema differs"
        ) from exc
    if kinds != Counter(
        {
            "regular_file": selector.EXPECTED_FILES,
            "directory": selector.EXPECTED_DIRECTORIES,
        }
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source entry-kind counts differ"
        )
    if len(grouped) != selector.EXPECTED_SOURCE_RUN_BUNDLES or any(
        suffixes != set(selector.REQUIRED_SUFFIXES) for suffixes in grouped.values()
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source run inventory differs"
        )
    eligibility = selector_contract["public_eligibility"]
    expected_counts = eligibility["published_session_1_2_run_counts"]
    observed_counts = {
        subject: [
            sum(
                1
                for row_subject, row_session, _run in grouped
                if row_subject == subject and row_session == session
            )
            for session in ("ses-01", "ses-02")
        ]
        for subject in eligibility["eligible_subject_ids"]
    }
    if observed_counts != expected_counts:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[1], "source public run counts differ"
        )
    return SourceValidation(
        canonical_sha256=_sha256_bytes(_canonical_manifest_bytes(manifest)),
        entry_count=len(entries),
        regular_file_count=kinds["regular_file"],
        directory_count=kinds["directory"],
        source_run_bundles=len(grouped),
        transport_hashes=hashes,
    )


def _mutable_ids(value: Any) -> set[int]:
    found: set[int] = set()
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            if id(current) in found:
                continue
            found.add(id(current))
            pending.extend(current.values())
        elif isinstance(current, list):
            if id(current) in found:
                continue
            found.add(id(current))
            pending.extend(current)
    return found


def _assert_no_mutable_alias(source: Mapping[str, Any], adapted: Mapping[str, Any]) -> None:
    if _mutable_ids(source) & _mutable_ids(adapted):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "source and adapted mutable objects alias"
        )


def _assert_adaptation_integrity(
    source: Mapping[str, Any],
    source_before: bytes,
    adapted: Mapping[str, Any],
    validated: SourceValidation,
) -> None:
    if _canonical_manifest_bytes(source) != source_before:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "source object mutated during adaptation"
        )
    _assert_no_mutable_alias(source, adapted)
    observed = adapted.get("transport_body_sha256")
    if not isinstance(observed, dict) or set(observed) != SELECTOR_TRANSPORT_KEYS:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "adapted transport fields differ"
        )
    expected = {
        "central_directory": validated.transport_hashes["directory"],
        "metadata": validated.transport_hashes["metadata"],
        "tail": validated.transport_hashes["tail"],
    }
    if observed != expected or Counter(observed.values()) != Counter(
        validated.transport_hashes.values()
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "transport values changed during adaptation"
        )


def _adapt_validated_source(
    source: Mapping[str, Any],
    validated: SourceValidation,
    *,
    copy_fn: Callable[[Any], Any] = copy.deepcopy,
) -> dict[str, Any]:
    source_before = _canonical_manifest_bytes(source)
    adapted = copy_fn(source)
    if not isinstance(adapted, dict):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "adapted object is not a mapping"
        )
    adapted["proof_posture"] = SELECTOR_PROOF_POSTURE
    adapted["source_identity"]["provider"] = SELECTOR_PROVIDER
    transport = adapted["transport_body_sha256"]
    transport["central_directory"] = transport.pop("directory")
    _assert_adaptation_integrity(source, source_before, adapted, validated)
    return adapted


def adapt_generated_source(
    source: Mapping[str, Any],
    *,
    adapter_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a generated source first, then map its single transport alias."""

    registered_adapter = dict(adapter_contract or load_registered_contract())
    _verify_contract_mapping(registered_adapter)
    registered_selector = dict(
        selector_contract or selector.load_registered_contract()
    )
    validated = _validate_source_manifest(source, registered_selector)
    adapted = _adapt_validated_source(source, validated)
    try:
        selector._validate_manifest(adapted, registered_selector)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[4], "adapted selector manifest refused"
        ) from exc
    return adapted


def _selection_summary(result: selector.SelectionResult) -> dict[str, Any]:
    return {
        "selector_route": selector.EXPECTED_ROUTE,
        "selected_subjects": result.cohort_summary["selected_subjects"],
        "selected_run_bundles": result.split_summary["selected_run_bundles"],
        "selected_core_members": result.split_summary["selected_core_members"],
        "selected_reservation_bytes": result.byte_summary[
            "selected_reservation_bytes"
        ],
        "selection_identity_sha256": result.selection_hashes[
            "selection_identity_sha256"
        ],
        "private_selection_manifest_sha256": result.selection_hashes[
            "private_selection_manifest_sha256"
        ],
    }


def _assert_selector_result(
    result: selector.SelectionResult,
    adapter_contract: Mapping[str, Any],
) -> None:
    expected = adapter_contract["expected_selector_result"]
    summary = _selection_summary(result)
    if (
        summary["selector_route"] != expected["route"]
        or summary["selected_subjects"] != expected["selected_subjects"]
        or summary["selected_run_bundles"] != expected["selected_run_bundles"]
        or summary["selected_core_members"] != expected["selected_core_members"]
        or summary["selected_reservation_bytes"]
        != expected["selected_reservation_bytes"]
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[4], "selector result differs"
        )


def _assert_selection_identity(
    observed: selector.SelectionResult,
    expected: selector.SelectionResult,
) -> None:
    if (
        observed.selection_hashes != expected.selection_hashes
        or observed.cohort_summary != expected.cohort_summary
        or observed.split_summary != expected.split_summary
        or observed.byte_summary != expected.byte_summary
        or _canonical_json_bytes(observed.private_manifest)
        != _canonical_json_bytes(expected.private_manifest)
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[4], "selector identity differs"
        )


def _assert_replay(first: Any, second: Any) -> None:
    first_bytes = (
        _canonical_manifest_bytes(first)
        if isinstance(first, dict) and "entries" in first
        else _canonical_json_bytes(first)
    )
    second_bytes = (
        _canonical_manifest_bytes(second)
        if isinstance(second, dict) and "entries" in second
        else _canonical_json_bytes(second)
    )
    if first_bytes != second_bytes:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "generated replay differs"
        )


def _assert_direct_source_refuses(
    source: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> None:
    try:
        selector.select_generated_prefix(source, contract=selector_contract)
    except selector.FreewillPrefixSelectionRefusal:
        return
    raise TransportAliasAdapterRefusal(
        REFUSAL_ROUTES[4], "direct producer-native selector call did not refuse"
    )


def _zero_access_counters() -> dict[str, int]:
    return {key: 0 for key in ACCESS_COUNTER_KEYS}


def _validate_zero_access_counters(counters: Mapping[str, Any]) -> None:
    if set(counters) != set(ACCESS_COUNTER_KEYS) or any(
        isinstance(value, bool) or not isinstance(value, int) or value != 0
        for value in counters.values()
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[5], "forbidden operation counter differs"
        )


def _mutated_source(
    source: Mapping[str, Any],
    mutation: Callable[[dict[str, Any]], None],
    adapter_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> None:
    changed = copy.deepcopy(dict(source))
    mutation(changed)
    adapt_generated_source(
        changed,
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
    )


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], Any],
) -> str:
    try:
        operation()
    except TransportAliasAdapterRefusal as exc:
        if exc.route != expected_route:
            raise TransportAliasAdapterRefusal(
                REFUSAL_ROUTES[3], f"mutation route differs: {name}"
            ) from exc
        return exc.route
    raise TransportAliasAdapterRefusal(
        REFUSAL_ROUTES[3], f"mutation did not refuse: {name}"
    )


def run_required_mutations(
    source: Mapping[str, Any],
    *,
    adapter_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Exercise all 26 frozen generated refusal mutations."""

    registered_adapter = dict(adapter_contract or load_registered_contract())
    registered_selector = dict(
        selector_contract or selector.load_registered_contract()
    )
    validated = _validate_source_manifest(source, registered_selector)
    adapted = _adapt_validated_source(source, validated)
    selected = selector.select_generated_prefix(adapted, contract=registered_selector)

    def mutate_transport_value() -> None:
        changed = copy.deepcopy(adapted)
        changed["transport_body_sha256"]["central_directory"] = "0" * 64
        _assert_adaptation_integrity(
            source,
            _canonical_manifest_bytes(source),
            changed,
            validated,
        )

    def mutate_source_object() -> None:
        changed_source = copy.deepcopy(dict(source))
        changed_source["entries"][0]["CRC32"] = "1234abcd"
        _assert_adaptation_integrity(
            changed_source,
            _canonical_manifest_bytes(source),
            adapted,
            validated,
        )

    def alias_mutable_object() -> None:
        changed = copy.deepcopy(adapted)
        changed["entries"] = source["entries"]
        _assert_no_mutable_alias(source, changed)

    def selector_result_drift() -> None:
        changed_contract = copy.deepcopy(registered_adapter)
        changed_contract["expected_selector_result"]["selected_subjects"] += 1
        _assert_selector_result(selected, changed_contract)

    def replay_drift() -> None:
        _assert_replay(
            {"selection_identity_sha256": "0" * 64},
            {"selection_identity_sha256": "1" * 64},
        )

    def forbidden_counter() -> None:
        counters = _zero_access_counters()
        counters["network_download_provider_or_language_model_operations"] = 1
        _validate_zero_access_counters(counters)

    mutations: dict[str, tuple[str, Callable[[], Any]]] = {
        "source_top_level_missing_field": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value.pop("entries"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "source_top_level_extra_field": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value.__setitem__("extra", False),
                registered_adapter,
                registered_selector,
            ),
        ),
        "source_schema_name_drift": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value.__setitem__("schema_name", "changed"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "source_schema_version_drift": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value.__setitem__("schema_version", "9.9.9"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "source_proof_posture_drift": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value.__setitem__("proof_posture", "changed"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "source_provider_drift": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value["source_identity"].__setitem__(
                    "provider", "changed"
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "source_identity_missing_field": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value["source_identity"].pop("record_id"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "source_identity_extra_field": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value["source_identity"].__setitem__(
                    "extra", False
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_missing_directory": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].pop("directory"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_missing_metadata": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].pop("metadata"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_missing_tail": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].pop("tail"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_extra_key": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].__setitem__(
                    "extra", "0" * 64
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_central_directory_without_directory": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].__setitem__(
                    "central_directory",
                    value["transport_body_sha256"].pop("directory"),
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_directory_and_central_directory_both_present": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].__setitem__(
                    "central_directory",
                    value["transport_body_sha256"]["directory"],
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_nonstring_digest": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].__setitem__(
                    "directory", 1
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_short_digest": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].__setitem__(
                    "directory", "0" * 63
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_uppercase_digest": (
            REFUSAL_ROUTES[2],
            lambda: _mutated_source(
                source,
                lambda value: value["transport_body_sha256"].__setitem__(
                    "directory", "A" * 64
                ),
                registered_adapter,
                registered_selector,
            ),
        ),
        "transport_value_mutated_during_mapping": (
            REFUSAL_ROUTES[3],
            mutate_transport_value,
        ),
        "source_object_mutated_during_mapping": (
            REFUSAL_ROUTES[3],
            mutate_source_object,
        ),
        "source_and_adapted_object_alias": (
            REFUSAL_ROUTES[3],
            alias_mutable_object,
        ),
        "entry_count_drift": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value["entries"].pop(),
                registered_adapter,
                registered_selector,
            ),
        ),
        "entry_schema_drift": (
            REFUSAL_ROUTES[1],
            lambda: _mutated_source(
                source,
                lambda value: value["entries"][0].__setitem__("target", "forbidden"),
                registered_adapter,
                registered_selector,
            ),
        ),
        "direct_unadapted_selector_call": (
            REFUSAL_ROUTES[4],
            lambda: (
                _assert_direct_source_refuses(source, registered_selector),
                (_ for _ in ()).throw(
                    TransportAliasAdapterRefusal(
                        REFUSAL_ROUTES[4], "direct source refusal observed"
                    )
                ),
            ),
        ),
        "adapted_selector_result_drift": (
            REFUSAL_ROUTES[4],
            selector_result_drift,
        ),
        "nondeterministic_replay": (
            REFUSAL_ROUTES[3],
            replay_drift,
        ),
        "forbidden_private_target_model_or_network_counter": (
            REFUSAL_ROUTES[5],
            forbidden_counter,
        ),
    }
    required = registered_adapter["qualification"]["required_mutations"]
    if tuple(mutations) != tuple(required):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[0], "implemented mutation order differs"
        )
    return {
        name: _expect_refusal(name, expected, operation)
        for name, (expected, operation) in mutations.items()
    }


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _validate_thread_environment() -> None:
    if any(os.environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "one-thread environment is not explicit"
        )


def _assert_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_caps"]
    if (
        not isinstance(runtime_seconds, (int, float))
        or runtime_seconds < 0
        or runtime_seconds > caps["runtime_seconds"]
        or isinstance(peak_rss_bytes, bool)
        or not isinstance(peak_rss_bytes, int)
        or peak_rss_bytes < 0
        or peak_rss_bytes > caps["peak_RSS_bytes"]
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "resource cap exceeded"
        )


def _walk_public(value: Any) -> None:
    forbidden_keys = {
        "entries",
        "local_header_offset",
        "member_name",
        "private_manifest",
        "selected_subject_ids",
    }
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden_keys:
                raise TransportAliasAdapterRefusal(
                    REFUSAL_ROUTES[5], "aggregate report leaks a private key"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)
    elif isinstance(value, str) and (
        value.startswith("/")
        or "Freewill_generated/" in value
        or "_eeg." in value
        or "_events.tsv" in value
        or "https://" in value
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[5], "aggregate report leaks a private value"
        )


def validate_report(
    report: Mapping[str, Any],
    *,
    allow_unstable_output_measurement: bool = False,
) -> None:
    if not isinstance(report, dict) or set(report) != REPORT_FIELDS:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[5], "report fields differ"
        )
    if (
        report["schema_name"] != REPORT_SCHEMA_NAME
        or report["schema_version"] != SCHEMA_VERSION
        or report["lane_id"] != "MARC2-TA1"
        or report["route"] != SUCCESS_ROUTE
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[5], "report identity differs"
        )
    _validate_zero_access_counters(report["access_counters"])
    gates = report["acceptance_gates"]
    if not isinstance(gates, dict) or len(gates) != 15 or not all(gates.values()):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[5], "acceptance gates differ"
        )
    if report["mutation_summary"]["passed"] != 26:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[5], "mutation summary differs"
        )
    if (
        not allow_unstable_output_measurement
        and report["measurements"]["generated_output_bytes"]
        != len(_canonical_json_bytes(report))
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "output measurement differs"
        )
    _walk_public(report)


def _build_report(
    *,
    adapter_contract: Mapping[str, Any],
    validation: SourceValidation,
    selection: selector.SelectionResult,
    mutation_results: Mapping[str, str],
    generated_input_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    route_counts = Counter(mutation_results.values())
    summary = _selection_summary(selection)
    access_counters = _zero_access_counters()
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": "MARC2-TA1",
        "status": "generated_only_transport_adapter_qualified",
        "proof_posture": (
            "generated_producer_to_selector_integration_only_no_scientific_value"
        ),
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
        },
        "contract": {
            "sha256": CONTRACT_SHA256,
            "fixed_inputs_verified": len(adapter_contract["fixed_inputs"]),
        },
        "adapter_summary": {
            "source_transport_keys": sorted(SOURCE_TRANSPORT_KEYS),
            "selector_transport_keys": sorted(SELECTOR_TRANSPORT_KEYS),
            "source_key": "directory",
            "selector_key": "central_directory",
            "source_validated_before_copy_or_mapping": True,
            "source_object_mutated": False,
            "source_and_adapted_mutable_objects_alias": False,
            "transport_hashes_preserved_byte_for_byte": True,
            "transport_hash_multiset_preserved": True,
            "direct_unadapted_selector_call_refused": True,
        },
        "fixture_summary": {
            "source_schema_name": (
                "neurodecodekit.marc1_central_directory_private_manifest"
            ),
            "source_provider": SOURCE_PROVIDER,
            "entry_count": validation.entry_count,
            "regular_file_entries": validation.regular_file_count,
            "directory_entries": validation.directory_count,
            "source_run_bundles": validation.source_run_bundles,
            "canonical_source_sha256": validation.canonical_sha256,
            "contains_human_content": False,
            "contains_private_path": False,
            "contains_signal_event_target_label_quality_or_channel": False,
        },
        "selector_summary": summary,
        "replay_summary": {
            "success_paths": [
                "canonical_source_order",
                "reversed_source_entry_order",
            ],
            "adapted_manifest_replayed": True,
            "selection_identity_replayed": True,
            "existing_generated_selector_identity_matched": True,
        },
        "mutation_summary": {
            "required": 26,
            "passed": len(mutation_results),
            "route_counts": dict(sorted(route_counts.items())),
        },
        "measurements": {
            "generated_input_bytes": generated_input_bytes,
            "generated_output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "registered_success_source_orders_validated": 2,
            "generated_selector_success_runs": 4,
            "generated_direct_selector_refusals": 2,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_adapter",
            "end_to_end_latency_measured": False,
        },
        "access_counters": access_counters,
        "acceptance_gates": {
            "registration_and_fixed_inputs_exact": True,
            "source_schema_validated_before_adaptation": True,
            "single_alias_only": True,
            "deep_copy_without_mutable_alias": True,
            "source_unchanged": True,
            "transport_values_preserved": True,
            "transport_hash_multiset_preserved": True,
            "direct_unadapted_selector_refused": True,
            "canonical_source_order_passed": True,
            "reversed_source_order_passed": True,
            "existing_selector_identity_matched": True,
            "deterministic_replay_passed": True,
            "all_26_mutations_refused": True,
            "resource_and_output_caps_passed": True,
            "all_forbidden_counters_zero": True,
        },
        "route": SUCCESS_ROUTE,
        "warnings": [
            "The producer-native manifest and selection are generated fixtures.",
            "The adapter is not connected to a private path or live executor.",
            "The selected identities and transport hashes have no scientific value.",
        ],
        "unavailable_fields": [
            "real archive members headers or payloads",
            "signals events targets labels channels or geometry",
            "neural features predictions scores or end-to-end latency",
        ],
        "claim_boundary": adapter_contract["claim_boundary"],
    }
    validate_report(report, allow_unstable_output_measurement=True)
    for _ in range(4):
        payload = _canonical_json_bytes(report)
        measured = len(payload)
        if report["measurements"]["generated_output_bytes"] == measured:
            break
        report["measurements"]["generated_output_bytes"] = measured
    else:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "output measurement did not stabilize"
        )
    validate_report(report)
    return report


def _assert_output_path(path: Path) -> None:
    parent = path.parent
    try:
        parent_mode = os.lstat(parent).st_mode
    except OSError as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "output parent is unavailable"
        ) from exc
    if stat.S_ISLNK(parent_mode) or not stat.S_ISDIR(parent_mode):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "output parent is not a real directory"
        )
    try:
        os.lstat(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "output destination check failed"
        ) from exc
    raise TransportAliasAdapterRefusal(
        REFUSAL_ROUTES[6], "output destination already exists"
    )


def _write_exclusive(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(path, flags, 0o600)
        created = True
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short output write")
            view = view[written:]
        os.fsync(descriptor)
    except OSError as exc:
        if created:
            try:
                path.unlink()
            except OSError:
                pass
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "output write failed"
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def qualify_generated_adapter(
    output_path: str | Path,
    *,
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run one bounded producer-adapter-selector generated qualification."""

    _validate_thread_environment()
    output = Path(output_path)
    _assert_output_path(output)
    started = clock()
    adapter_contract = load_registered_contract()
    selector_contract = selector.load_registered_contract()
    canonical_source = build_generated_source_manifest(
        selector_contract=selector_contract
    )
    reversed_source = build_generated_source_manifest(
        row_order="reversed",
        selector_contract=selector_contract,
    )
    canonical_before = _canonical_manifest_bytes(canonical_source)
    reversed_before = _canonical_manifest_bytes(reversed_source)
    validation = _validate_source_manifest(canonical_source, selector_contract)
    reversed_validation = _validate_source_manifest(reversed_source, selector_contract)
    if validation.canonical_sha256 != reversed_validation.canonical_sha256:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "source entry-order identity differs"
        )
    _assert_direct_source_refuses(canonical_source, selector_contract)
    canonical_adapted = adapt_generated_source(
        canonical_source,
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
    )
    reversed_adapted = adapt_generated_source(
        reversed_source,
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
    )
    if (
        _canonical_manifest_bytes(canonical_source) != canonical_before
        or _canonical_manifest_bytes(reversed_source) != reversed_before
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[3], "source changed after adaptation"
        )
    _assert_replay(canonical_adapted, reversed_adapted)
    canonical_selection = selector.select_generated_prefix(
        canonical_adapted,
        contract=selector_contract,
    )
    reversed_selection = selector.select_generated_prefix(
        reversed_adapted,
        contract=selector_contract,
    )
    baseline_selection = selector.select_generated_prefix(
        selector.build_generated_manifest(contract=selector_contract),
        contract=selector_contract,
    )
    _assert_selector_result(canonical_selection, adapter_contract)
    _assert_selector_result(reversed_selection, adapter_contract)
    _assert_selection_identity(canonical_selection, reversed_selection)
    _assert_selection_identity(canonical_selection, baseline_selection)
    mutation_results = run_required_mutations(
        canonical_source,
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
    )
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_probe()
    _assert_resources(runtime_seconds, peak_rss_bytes, adapter_contract)
    generated_input_bytes = len(canonical_before) + len(reversed_before)
    report = _build_report(
        adapter_contract=adapter_contract,
        validation=validation,
        selection=canonical_selection,
        mutation_results=mutation_results,
        generated_input_bytes=generated_input_bytes,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
    )
    report_bytes = _canonical_json_bytes(report)
    caps = adapter_contract["resource_caps"]
    if (
        len(report_bytes) > caps["generated_output_bytes"]
        or len(report_bytes) > caps["incremental_disk_bytes"]
    ):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "generated output cap exceeded"
        )
    _write_exclusive(output, report_bytes)
    if output.stat().st_size != len(report_bytes):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "written output size differs"
        )
    return QualificationOutcome(
        report=report,
        report_path=output,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=len(report_bytes),
    )


def inspect_report(path: str | Path) -> dict[str, Any]:
    """Inspect only an aggregate generated qualification report."""

    report_path = Path(path)
    try:
        mode = os.lstat(report_path).st_mode
    except OSError as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "report is unavailable"
        ) from exc
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "report is not a regular no-follow file"
        )
    if report_path.stat().st_size > 2 * 1024 * 1024:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "report exceeds cap"
        )
    try:
        report = _strict_json(report_path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise TransportAliasAdapterRefusal(
            REFUSAL_ROUTES[6], "report parse failed"
        ) from exc
    validate_report(report)
    return {
        "route": report["route"],
        "source_transport_keys": report["adapter_summary"][
            "source_transport_keys"
        ],
        "selector_transport_keys": report["adapter_summary"][
            "selector_transport_keys"
        ],
        "selected_subjects": report["selector_summary"]["selected_subjects"],
        "selected_run_bundles": report["selector_summary"][
            "selected_run_bundles"
        ],
        "selected_core_members": report["selector_summary"][
            "selected_core_members"
        ],
        "selected_reservation_bytes": report["selector_summary"][
            "selected_reservation_bytes"
        ],
        "mutations_passed": report["mutation_summary"]["passed"],
        "runtime_seconds": report["measurements"]["runtime_seconds"],
        "peak_RSS_bytes": report["measurements"]["peak_RSS_bytes"],
        "generated_input_bytes": report["measurements"]["generated_input_bytes"],
        "generated_output_bytes": report["measurements"][
            "generated_output_bytes"
        ],
        "warnings": list(report["warnings"]),
        "unavailable_fields": list(report["unavailable_fields"]),
    }


def build_plan_summary() -> dict[str, Any]:
    """Return the registered generated-only plan without building a fixture."""

    contract = load_registered_contract()
    return {
        "lane_id": contract["lane_id"],
        "contract_sha256": CONTRACT_SHA256,
        "green_registration_commit": GREEN_REGISTRATION_COMMIT,
        "green_registration_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
        "commands": list(contract["future_implementation_surface"]["commands"]),
        "source_transport_keys": sorted(SOURCE_TRANSPORT_KEYS),
        "selector_transport_keys": sorted(SELECTOR_TRANSPORT_KEYS),
        "required_mutations": contract["qualification"]["required_mutation_count"],
        "expected_selected_subjects": contract["expected_selector_result"][
            "selected_subjects"
        ],
        "private_or_Git_ignored_bytes_authorized": 0,
        "network_bytes_authorized": 0,
        "live_adapter_or_MARC2_FW2_authorized": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_transport_alias_adapter",
        description="Qualify the generated-only MARC2 transport alias adapter.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the frozen generated-only plan.")
    qualify = subparsers.add_parser(
        "qualify", help="Run one generated adapter qualification."
    )
    qualify.add_argument("--output", required=True)
    inspect = subparsers.add_parser(
        "inspect", help="Inspect an aggregate generated report."
    )
    inspect.add_argument("report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            payload = build_plan_summary()
        elif args.command == "qualify":
            outcome = qualify_generated_adapter(args.output)
            payload = {
                "route": outcome.report["route"],
                "report": str(outcome.report_path),
                "runtime_seconds": outcome.runtime_seconds,
                "peak_RSS_bytes": outcome.peak_rss_bytes,
                "generated_input_bytes": outcome.generated_input_bytes,
                "generated_output_bytes": outcome.generated_output_bytes,
            }
        else:
            payload = inspect_report(args.report)
    except TransportAliasAdapterRefusal as exc:
        print(
            json.dumps(
                {"refusal_id": exc.route, "reason": exc.safe_reason},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
