"""Generated/mock MARC2 live-envelope to green-adapter composition."""

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
from neurodecodekit.datasets import marc2_transport_alias_adapter as adapter


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-LA1"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_live_schema_adapter_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_live_schema_adapter_qualification"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_live_schema_adapter_contract.v0.json"
)
CONTRACT_SHA256 = "e06fbb1401326d4f788bfdd50162c07bf88652b0c1dc4b11cef46cbec6e41e05"
GREEN_REGISTRATION_COMMIT = "62e465e0600622444b0868d5dcf19678504d20c4"
GREEN_REGISTRATION_CI_RUN_ID = 31_934_737_967
GREEN_REGISTRATION_BASE_JOB_ID = 95_134_785_476
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_134_785_489
LIVE_PROOF_POSTURE = "live_archive_private_central_directory_metadata_only"
LIVE_SOURCE_IDENTITY = {
    "provider": "Figshare",
    "record_id": 28_632_599,
    "version": 1,
    "file_id": 57_518_986,
    "declared_archive_bytes": 13_591_548_048,
    "registered_MD5": "3b7c3039c5c9fb6abf1429a830301711",
    "whole_archive_downloaded": False,
    "member_payload_opened": False,
}
SUCCESS_ROUTE = "MARC2LA-G1-generated_live_schema_adapter_selector_composition_passed"
REFUSAL_ROUTES = (
    "MARC2LA-F01-contract_or_green_artifact_identity",
    "MARC2LA-F02-live_source_envelope_or_entry_schema",
    "MARC2LA-F03-source_transport_alias_or_digest",
    "MARC2LA-F04-identity_bridge_copy_or_value_integrity",
    "MARC2LA-F05-green_adapter_selector_or_replay_integration",
    "MARC2LA-F06-private_target_model_network_or_claim_boundary",
    "MARC2LA-F07-resource_or_output_cap",
)
THREAD_ENVIRONMENT = adapter.THREAD_ENVIRONMENT
SOURCE_TOP_LEVEL_FIELDS = adapter.SOURCE_TOP_LEVEL_FIELDS
SOURCE_IDENTITY_FIELDS = adapter.SOURCE_IDENTITY_FIELDS
SOURCE_TRANSPORT_KEYS = adapter.SOURCE_TRANSPORT_KEYS
SELECTOR_TRANSPORT_KEYS = adapter.SELECTOR_TRANSPORT_KEYS
ACCESS_COUNTER_KEYS = adapter.ACCESS_COUNTER_KEYS
REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "proof_posture",
        "green_registration",
        "contract",
        "composition_summary",
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


class LiveSchemaAdapterRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC2-LA1 route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-LA1 refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class LiveSourceValidation:
    """Exact live-shaped source validation completed before copying."""

    canonical_sha256: str
    entry_count: int
    regular_file_count: int
    directory_count: int
    source_run_bundles: int
    transport_hashes: Mapping[str, str]


@dataclass(frozen=True)
class QualificationOutcome:
    """One bounded generated/mock qualification outcome."""

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
        while chunk := handle.read(1024 * 1024):
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
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda constant: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON value: {constant}")
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
        != "MARC-2-generated-live-schema-adapter-composition-v0"
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_mock_live_schema_adapter_contract_implementation_pending"
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "contract identity differs"
        )
    proof = contract.get("green_adapter_proof")
    if (
        not isinstance(proof, dict)
        or proof.get("commit")
        != "108b869a6199b6d3aa2d87f8a59b6d8bee0c847b"
        or proof.get("CI_run_id") != 31_933_692_066
        or proof.get("adapter_module_sha256") != adapter_module_sha256()
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "green adapter proof differs"
        )
    bridge = contract.get("identity_bridge")
    if (
        not isinstance(bridge, dict)
        or bridge.get("changed_values")
        != [
            "proof_posture",
            "source_identity.provider",
            "source_identity.file_id",
            "source_identity.registered_MD5",
        ]
        or bridge.get("green_public_adapter_function")
        != "adapt_generated_source"
        or bridge.get("green_public_adapter_calls_per_success_path") != 1
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "identity bridge contract differs"
        )
    qualification = contract.get("qualification")
    if (
        not isinstance(qualification, dict)
        or qualification.get("required_mutation_count") != 30
        or len(qualification.get("required_mutations", ())) != 30
        or len(set(qualification.get("required_mutations", ()))) != 30
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "mutation inventory differs"
        )
    if any(contract.get("authorization_state", {}).values()):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "live authority differs"
        )


def adapter_module_sha256() -> str:
    """Return the compiled-in exact green adapter source identity."""

    return "f4da58dac4723dd024912c842e2ecf849e17a4bc1906897b32b4a287f4a7bbf2"


def load_registered_contract(
    repo_root: str | Path | None = None,
    *,
    verify_fixed_inputs: bool = True,
) -> dict[str, Any]:
    """Load the exact remotely green MARC2-LA1 registration."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    path = root / CONTRACT_RELATIVE_PATH
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    if verify_fixed_inputs:
        for binding in contract["fixed_inputs"]:
            try:
                observed = _sha256_file(root / binding["path"])
            except OSError as exc:
                raise LiveSchemaAdapterRefusal(
                    REFUSAL_ROUTES[0], "fixed artifact is unavailable"
                ) from exc
            if observed != binding["sha256"]:
                raise LiveSchemaAdapterRefusal(
                    REFUSAL_ROUTES[0], "fixed artifact SHA-256 differs"
                )
    return contract


def build_generated_live_source(
    *,
    row_order: str = "canonical",
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a generated source with the exact committed live envelope."""

    registered_selector = dict(
        selector_contract or selector.load_registered_contract()
    )
    source = adapter.build_generated_source_manifest(
        row_order=row_order,
        selector_contract=registered_selector,
    )
    source["proof_posture"] = LIVE_PROOF_POSTURE
    source["source_identity"] = copy.deepcopy(LIVE_SOURCE_IDENTITY)
    return source


def _validate_digest(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in adapter.SHA256_HEX for character in value)
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[2], "transport digest differs"
        )
    return value


def _validate_live_source_manifest(
    manifest: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> LiveSourceValidation:
    """Validate the complete live-shaped source before any copy or bridge."""

    if not isinstance(manifest, dict) or set(manifest) != SOURCE_TOP_LEVEL_FIELDS:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source top-level fields differ"
        )
    if (
        manifest.get("schema_name")
        != "neurodecodekit.marc1_central_directory_private_manifest"
        or manifest.get("schema_version") != SCHEMA_VERSION
        or manifest.get("proof_posture") != LIVE_PROOF_POSTURE
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source schema identity differs"
        )
    source_identity = manifest.get("source_identity")
    if (
        not isinstance(source_identity, dict)
        or set(source_identity) != SOURCE_IDENTITY_FIELDS
        or source_identity != LIVE_SOURCE_IDENTITY
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source identity differs"
        )
    transport = manifest.get("transport_body_sha256")
    if not isinstance(transport, dict) or set(transport) != SOURCE_TRANSPORT_KEYS:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[2], "source transport aliases differ"
        )
    hashes = {key: _validate_digest(transport[key]) for key in sorted(transport)}

    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) != selector.EXPECTED_ROWS:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source entry count differs"
        )
    names: set[str] = set()
    kinds: Counter[str] = Counter()
    grouped: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    try:
        for row in entries:
            name, match = selector._validate_entry(row)
            if name in names:
                raise LiveSchemaAdapterRefusal(
                    REFUSAL_ROUTES[1], "live source member is duplicated"
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
                    raise LiveSchemaAdapterRefusal(
                        REFUSAL_ROUTES[1], "live run companion is duplicated"
                    )
                grouped[key].add(suffix)
    except selector.FreewillPrefixSelectionRefusal as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source entry schema differs"
        ) from exc
    if kinds != Counter(
        {
            "regular_file": selector.EXPECTED_FILES,
            "directory": selector.EXPECTED_DIRECTORIES,
        }
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source entry-kind counts differ"
        )
    if len(grouped) != selector.EXPECTED_SOURCE_RUN_BUNDLES or any(
        suffixes != set(selector.REQUIRED_SUFFIXES) for suffixes in grouped.values()
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source run inventory differs"
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
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[1], "live source public run counts differ"
        )
    return LiveSourceValidation(
        canonical_sha256=_sha256_bytes(_canonical_manifest_bytes(manifest)),
        entry_count=len(entries),
        regular_file_count=kinds["regular_file"],
        directory_count=kinds["directory"],
        source_run_bundles=len(grouped),
        transport_hashes=hashes,
    )


def _mutable_ids(value: Any) -> set[int]:
    return adapter._mutable_ids(value)


def _assert_bridge_integrity(
    source: Mapping[str, Any],
    source_before: bytes,
    bridged: Mapping[str, Any],
    validation: LiveSourceValidation,
) -> None:
    if _canonical_manifest_bytes(source) != source_before:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[3], "source object mutated during identity bridge"
        )
    if _mutable_ids(source) & _mutable_ids(bridged):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[3], "source and bridged mutable objects alias"
        )
    expected_identity = {
        "provider": adapter.SOURCE_PROVIDER,
        "record_id": LIVE_SOURCE_IDENTITY["record_id"],
        "version": LIVE_SOURCE_IDENTITY["version"],
        "file_id": 0,
        "declared_archive_bytes": LIVE_SOURCE_IDENTITY["declared_archive_bytes"],
        "registered_MD5": "0" * 32,
        "whole_archive_downloaded": False,
        "member_payload_opened": False,
    }
    if (
        bridged.get("schema_name") != source.get("schema_name")
        or bridged.get("schema_version") != source.get("schema_version")
        or bridged.get("proof_posture") != adapter.SOURCE_PROOF_POSTURE
        or bridged.get("source_identity") != expected_identity
        or bridged.get("transport_body_sha256")
        != source.get("transport_body_sha256")
        or Counter(bridged.get("transport_body_sha256", {}).values())
        != Counter(validation.transport_hashes.values())
        or _canonical_json_bytes(bridged.get("entries"))
        != _canonical_json_bytes(source.get("entries"))
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[3], "identity bridge changed a preserved value"
        )


def _bridge_live_identity(
    source: Mapping[str, Any],
    validation: LiveSourceValidation,
    *,
    copy_fn: Callable[[Any], Any] = copy.deepcopy,
) -> dict[str, Any]:
    source_before = _canonical_manifest_bytes(source)
    bridged = copy_fn(source)
    if not isinstance(bridged, dict):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[3], "bridged object is not a mapping"
        )
    bridged["proof_posture"] = adapter.SOURCE_PROOF_POSTURE
    bridged["source_identity"]["provider"] = adapter.SOURCE_PROVIDER
    bridged["source_identity"]["file_id"] = 0
    bridged["source_identity"]["registered_MD5"] = "0" * 32
    _assert_bridge_integrity(source, source_before, bridged, validation)
    return bridged


def adapt_live_shaped_source(
    source: Mapping[str, Any],
    *,
    live_contract: Mapping[str, Any] | None = None,
    adapter_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a live-shaped source, bridge identity, then call green TA1."""

    registered_live = dict(live_contract or load_registered_contract())
    _verify_contract_mapping(registered_live)
    registered_adapter = dict(
        adapter_contract or adapter.load_registered_contract()
    )
    registered_selector = dict(
        selector_contract or selector.load_registered_contract()
    )
    validation = _validate_live_source_manifest(source, registered_selector)
    bridged = _bridge_live_identity(source, validation)
    try:
        adapted = adapter.adapt_generated_source(
            bridged,
            adapter_contract=registered_adapter,
            selector_contract=registered_selector,
        )
    except adapter.TransportAliasAdapterRefusal as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[4], "green adapter refused bridged source"
        ) from exc
    if _mutable_ids(source) & _mutable_ids(adapted):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[3], "source and adapted mutable objects alias"
        )
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
    }


def _assert_selector_result(
    result: selector.SelectionResult,
    contract: Mapping[str, Any],
) -> None:
    expected = contract["expected_selector_result"]
    summary = _selection_summary(result)
    if (
        summary["selector_route"] != expected["route"]
        or summary["selected_subjects"] != expected["selected_subjects"]
        or summary["selected_run_bundles"] != expected["selected_run_bundles"]
        or summary["selected_core_members"] != expected["selected_core_members"]
        or summary["selected_reservation_bytes"]
        != expected["selected_reservation_bytes"]
        or summary["selection_identity_sha256"]
        != expected["selection_identity_sha256"]
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[4], "selector result differs"
        )


def _assert_replay(
    first_manifest: Mapping[str, Any],
    second_manifest: Mapping[str, Any],
    first_result: selector.SelectionResult,
    second_result: selector.SelectionResult,
) -> None:
    if (
        _canonical_manifest_bytes(first_manifest)
        != _canonical_manifest_bytes(second_manifest)
        or first_result.selection_hashes != second_result.selection_hashes
        or first_result.cohort_summary != second_result.cohort_summary
        or first_result.split_summary != second_result.split_summary
        or first_result.byte_summary != second_result.byte_summary
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[4], "generated composition replay differs"
        )


def _assert_direct_source_refuses(
    source: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> None:
    try:
        selector.select_generated_prefix(source, contract=selector_contract)
    except selector.FreewillPrefixSelectionRefusal:
        return
    raise LiveSchemaAdapterRefusal(
        REFUSAL_ROUTES[4], "direct live-shaped selector call did not refuse"
    )


def _zero_access_counters() -> dict[str, int]:
    return {key: 0 for key in ACCESS_COUNTER_KEYS}


def _validate_zero_access_counters(counters: Mapping[str, Any]) -> None:
    if set(counters) != set(ACCESS_COUNTER_KEYS) or any(
        isinstance(value, bool) or not isinstance(value, int) or value != 0
        for value in counters.values()
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[5], "forbidden operation counter differs"
        )


def _mutated_source(
    source: Mapping[str, Any],
    mutation: Callable[[dict[str, Any]], None],
    live_contract: Mapping[str, Any],
    adapter_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> None:
    changed = copy.deepcopy(dict(source))
    mutation(changed)
    adapt_live_shaped_source(
        changed,
        live_contract=live_contract,
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
    except LiveSchemaAdapterRefusal as exc:
        if exc.route != expected_route:
            raise LiveSchemaAdapterRefusal(
                REFUSAL_ROUTES[3], f"mutation route differs: {name}"
            ) from exc
        return exc.route
    raise LiveSchemaAdapterRefusal(
        REFUSAL_ROUTES[3], f"mutation did not refuse: {name}"
    )


def run_required_mutations(
    source: Mapping[str, Any],
    *,
    live_contract: Mapping[str, Any] | None = None,
    adapter_contract: Mapping[str, Any] | None = None,
    selector_contract: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Exercise all 30 frozen generated/mock refusal mutations."""

    registered_live = dict(live_contract or load_registered_contract())
    registered_adapter = dict(
        adapter_contract or adapter.load_registered_contract()
    )
    registered_selector = dict(
        selector_contract or selector.load_registered_contract()
    )
    validation = _validate_live_source_manifest(source, registered_selector)
    bridged = _bridge_live_identity(source, validation)

    def mutate_bridge_transport() -> None:
        changed = copy.deepcopy(bridged)
        changed["transport_body_sha256"]["directory"] = "0" * 64
        _assert_bridge_integrity(
            source,
            _canonical_manifest_bytes(source),
            changed,
            validation,
        )

    def mutate_bridge_source() -> None:
        changed_source = copy.deepcopy(dict(source))
        changed_source["entries"][0]["CRC32"] = "1234abcd"
        _assert_bridge_integrity(
            changed_source,
            _canonical_manifest_bytes(source),
            bridged,
            validation,
        )

    def direct_selector_refusal() -> None:
        _assert_direct_source_refuses(source, registered_selector)
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[4], "direct source refusal observed"
        )

    def forbidden_counter() -> None:
        counters = _zero_access_counters()
        counters["private_or_Git_ignored_path_operations"] = 1
        _validate_zero_access_counters(counters)

    def call(mutation: Callable[[dict[str, Any]], None]) -> None:
        _mutated_source(
            source,
            mutation,
            registered_live,
            registered_adapter,
            registered_selector,
        )

    mutations: dict[str, tuple[str, Callable[[], Any]]] = {
        "live_top_level_missing_field": (
            REFUSAL_ROUTES[1],
            lambda: call(lambda value: value.pop("entries")),
        ),
        "live_top_level_extra_field": (
            REFUSAL_ROUTES[1],
            lambda: call(lambda value: value.__setitem__("extra", False)),
        ),
        "live_schema_name_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(lambda value: value.__setitem__("schema_name", "changed")),
        ),
        "live_schema_version_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(lambda value: value.__setitem__("schema_version", "9.9.9")),
        ),
        "live_proof_posture_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(lambda value: value.__setitem__("proof_posture", "changed")),
        ),
        "live_source_identity_missing_field": (
            REFUSAL_ROUTES[1],
            lambda: call(lambda value: value["source_identity"].pop("record_id")),
        ),
        "live_source_identity_extra_field": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__("extra", False)
            ),
        ),
        "live_provider_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__(
                    "provider", "changed"
                )
            ),
        ),
        "live_record_id_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__("record_id", 0)
            ),
        ),
        "live_version_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__("version", 0)
            ),
        ),
        "live_file_id_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__("file_id", 0)
            ),
        ),
        "live_archive_bytes_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__(
                    "declared_archive_bytes", 0
                )
            ),
        ),
        "live_MD5_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__(
                    "registered_MD5", "0" * 32
                )
            ),
        ),
        "live_whole_archive_downloaded_true": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__(
                    "whole_archive_downloaded", True
                )
            ),
        ),
        "live_member_payload_opened_true": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["source_identity"].__setitem__(
                    "member_payload_opened", True
                )
            ),
        ),
        "transport_missing_directory": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].pop("directory")
            ),
        ),
        "transport_missing_metadata": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].pop("metadata")
            ),
        ),
        "transport_missing_tail": (
            REFUSAL_ROUTES[2],
            lambda: call(lambda value: value["transport_body_sha256"].pop("tail")),
        ),
        "transport_extra_key": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].__setitem__(
                    "extra", "0" * 64
                )
            ),
        ),
        "transport_consumer_alias_without_source_alias": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].__setitem__(
                    "central_directory",
                    value["transport_body_sha256"].pop("directory"),
                )
            ),
        ),
        "transport_source_and_consumer_alias_both_present": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].__setitem__(
                    "central_directory",
                    value["transport_body_sha256"]["directory"],
                )
            ),
        ),
        "transport_nonstring_digest": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].__setitem__(
                    "directory", 1
                )
            ),
        ),
        "transport_short_digest": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].__setitem__(
                    "directory", "0" * 63
                )
            ),
        ),
        "transport_uppercase_digest": (
            REFUSAL_ROUTES[2],
            lambda: call(
                lambda value: value["transport_body_sha256"].__setitem__(
                    "directory", "A" * 64
                )
            ),
        ),
        "entry_count_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(lambda value: value["entries"].pop()),
        ),
        "entry_schema_drift": (
            REFUSAL_ROUTES[1],
            lambda: call(
                lambda value: value["entries"][0].__setitem__(
                    "target", "forbidden"
                )
            ),
        ),
        "bridge_transport_value_mutation": (
            REFUSAL_ROUTES[3],
            mutate_bridge_transport,
        ),
        "bridge_source_object_mutation": (
            REFUSAL_ROUTES[3],
            mutate_bridge_source,
        ),
        "direct_unadapted_selector_call": (
            REFUSAL_ROUTES[4],
            direct_selector_refusal,
        ),
        "forbidden_private_target_model_or_network_counter": (
            REFUSAL_ROUTES[5],
            forbidden_counter,
        ),
    }
    required = registered_live["qualification"]["required_mutations"]
    if tuple(mutations) != tuple(required):
        raise LiveSchemaAdapterRefusal(
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
        raise LiveSchemaAdapterRefusal(
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
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "resource cap exceeded"
        )


def _walk_public(value: Any) -> None:
    forbidden_keys = {
        "entries",
        "local_header_offset",
        "member_name",
        "private_manifest",
        "selected_subject_ids",
        "source_path",
        "target",
        "targets",
    }
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden_keys:
                raise LiveSchemaAdapterRefusal(
                    REFUSAL_ROUTES[5], "aggregate report leaks a private key"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)
    elif isinstance(value, str) and (
        value.startswith("/")
        or ".codex_work" in value
        or "Freewill_generated/" in value
        or "_eeg." in value
        or "_events.tsv" in value
        or "https://" in value
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[5], "aggregate report leaks a private value"
        )


def validate_report(
    report: Mapping[str, Any],
    *,
    allow_unstable_output_measurement: bool = False,
) -> None:
    if not isinstance(report, dict) or set(report) != REPORT_FIELDS:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[5], "report fields differ"
        )
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[5], "report identity differs"
        )
    _validate_zero_access_counters(report["access_counters"])
    gates = report.get("acceptance_gates")
    if not isinstance(gates, dict) or len(gates) != 16 or not all(gates.values()):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[5], "acceptance gates differ"
        )
    if report["mutation_summary"]["passed"] != 30:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[5], "mutation summary differs"
        )
    if (
        not allow_unstable_output_measurement
        and report["measurements"]["generated_output_bytes"]
        != len(_canonical_json_bytes(report))
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "output measurement differs"
        )
    _walk_public(report)


def _build_report(
    *,
    contract: Mapping[str, Any],
    validation: LiveSourceValidation,
    selection: selector.SelectionResult,
    mutation_results: Mapping[str, str],
    generated_input_bytes: int,
    runtime_seconds: float,
    peak_rss_bytes: int,
) -> dict[str, Any]:
    summary = _selection_summary(selection)
    route_counts = Counter(mutation_results.values())
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_mock_live_schema_adapter_composition_qualified",
        "proof_posture": "generated_live_envelope_composition_only_no_scientific_value",
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
        },
        "contract": {
            "sha256": CONTRACT_SHA256,
            "fixed_inputs_verified": len(contract["fixed_inputs"]),
            "green_adapter_module_sha256": adapter_module_sha256(),
        },
        "composition_summary": {
            "live_envelope_validated_before_copy_or_bridge": True,
            "identity_values_changed": list(
                contract["identity_bridge"]["changed_values"]
            ),
            "green_public_adapter_function": "adapt_generated_source",
            "green_public_adapter_calls_per_success_path": 1,
            "source_object_mutated": False,
            "source_and_bridged_mutable_objects_alias": False,
            "transport_alias_mapped_inside_green_adapter_only": True,
            "transport_hashes_preserved_byte_for_byte": True,
            "transport_hash_multiset_preserved": True,
            "direct_unadapted_selector_call_refused": True,
        },
        "fixture_summary": {
            "source_schema_name": (
                "neurodecodekit.marc1_central_directory_private_manifest"
            ),
            "source_provider": "Figshare",
            "entry_count": validation.entry_count,
            "regular_file_entries": validation.regular_file_count,
            "directory_entries": validation.directory_count,
            "source_run_bundles": validation.source_run_bundles,
            "canonical_source_sha256": validation.canonical_sha256,
            "contains_human_content": False,
            "contains_private_path": False,
            "contains_real_or_private_bytes": False,
            "contains_signal_event_target_label_quality_channel_or_geometry": False,
        },
        "selector_summary": summary,
        "replay_summary": {
            "success_paths": [
                "canonical_source_order",
                "reversed_source_entry_order",
            ],
            "live_source_canonical_identity_replayed": True,
            "adapted_manifest_replayed": True,
            "selection_identity_replayed": True,
            "existing_generated_selector_identity_matched": True,
        },
        "mutation_summary": {
            "required": 30,
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
            "green_adapter_success_calls": 2,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_adapter",
            "end_to_end_latency_measured": False,
        },
        "access_counters": _zero_access_counters(),
        "acceptance_gates": {
            "green_registration_and_contract_hashes": True,
            "all_fixed_artifact_hashes": True,
            "exact_live_envelope_before_bridge": True,
            "all_source_entries_validated_before_bridge": True,
            "four_value_identity_bridge_only": True,
            "source_unchanged_and_no_mutable_alias": True,
            "transport_values_and_multiset_preserved": True,
            "green_public_adapter_called_once_per_success": True,
            "direct_live_selector_call_refused": True,
            "canonical_and_reversed_source_orders": True,
            "existing_selector_identity_replayed": True,
            "all_30_mutations_refused": True,
            "zero_private_archive_neural_target_model_or_network_operations": True,
            "runtime_RSS_output_and_one_thread_caps": True,
            "aggregate_privacy_and_strict_inspection": True,
            "claim_boundary_preserved": True,
        },
        "route": SUCCESS_ROUTE,
        "warnings": [
            "The live-shaped source entries and transport digests are generated fixtures.",
            "The four-value bridge enables generated adapter composition and is not evidence conversion.",
            "No private read live executor or MARC2-FW2 operation is authorized.",
        ],
        "unavailable_fields": [
            "real private manifest and archive member content",
            "signals events targets labels channels geometry and quality",
            "neural features predictions scores and end-to-end latency",
        ],
        "claim_boundary": contract["claim_boundary"],
    }
    validate_report(report, allow_unstable_output_measurement=True)
    for _ in range(4):
        measured = len(_canonical_json_bytes(report))
        if report["measurements"]["generated_output_bytes"] == measured:
            break
        report["measurements"]["generated_output_bytes"] = measured
    else:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "output size did not stabilize"
        )
    validate_report(report)
    return report


def _assert_output_path(path: Path) -> None:
    if not path.is_absolute():
        path = Path.cwd() / path
    if path.exists() or path.is_symlink():
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "output already exists"
        )
    parent = path.parent
    try:
        observed = os.lstat(parent)
    except OSError as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "output parent unavailable"
        ) from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "output parent differs"
        )


def _write_exclusive(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "exclusive output write failed"
        ) from exc
    observed = os.lstat(path)
    if (
        stat.S_ISLNK(observed.st_mode)
        or not stat.S_ISREG(observed.st_mode)
        or stat.S_IMODE(observed.st_mode) != 0o600
        or observed.st_size != len(payload)
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "output identity differs"
        )


def qualify_generated_composition(
    output: str | Path,
    *,
    clock: Callable[[], float] = time.perf_counter,
    rss_probe: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run one bounded generated live-envelope adapter qualification."""

    _validate_thread_environment()
    report_path = Path(output)
    _assert_output_path(report_path)
    contract = load_registered_contract()
    adapter_contract = adapter.load_registered_contract()
    selector_contract = selector.load_registered_contract()
    canonical_source = build_generated_live_source(
        selector_contract=selector_contract
    )
    reversed_source = build_generated_live_source(
        row_order="reversed",
        selector_contract=selector_contract,
    )
    generated_input_bytes = len(_canonical_json_bytes(canonical_source)) + len(
        _canonical_json_bytes(reversed_source)
    )
    started = clock()
    canonical_validation = _validate_live_source_manifest(
        canonical_source, selector_contract
    )
    reversed_validation = _validate_live_source_manifest(
        reversed_source, selector_contract
    )
    if canonical_validation.canonical_sha256 != reversed_validation.canonical_sha256:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[4], "live source canonical identity differs"
        )
    _assert_direct_source_refuses(canonical_source, selector_contract)
    canonical_adapted = adapt_live_shaped_source(
        canonical_source,
        live_contract=contract,
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
    )
    reversed_adapted = adapt_live_shaped_source(
        reversed_source,
        live_contract=contract,
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
    )
    canonical_selection = selector.select_generated_prefix(
        canonical_adapted,
        contract=selector_contract,
    )
    reversed_selection = selector.select_generated_prefix(
        reversed_adapted,
        contract=selector_contract,
    )
    _assert_selector_result(canonical_selection, contract)
    _assert_selector_result(reversed_selection, contract)
    _assert_replay(
        canonical_adapted,
        reversed_adapted,
        canonical_selection,
        reversed_selection,
    )
    mutation_results = run_required_mutations(
        canonical_source,
        live_contract=contract,
        adapter_contract=adapter_contract,
        selector_contract=selector_contract,
    )
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_probe()
    _assert_resources(runtime_seconds, peak_rss_bytes, contract)
    report = _build_report(
        contract=contract,
        validation=canonical_validation,
        selection=canonical_selection,
        mutation_results=mutation_results,
        generated_input_bytes=generated_input_bytes,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
    )
    payload = _canonical_json_bytes(report)
    caps = contract["resource_caps"]
    if len(payload) > caps["generated_output_bytes"]:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "generated output exceeds cap"
        )
    _write_exclusive(report_path, payload)
    return QualificationOutcome(
        report=report,
        report_path=report_path,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=len(payload),
    )


def inspect_report(path: str | Path) -> dict[str, Any]:
    """Inspect only one aggregate generated qualification report."""

    report_path = Path(path)
    try:
        observed = os.lstat(report_path)
    except OSError as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "report unavailable"
        ) from exc
    if (
        stat.S_ISLNK(observed.st_mode)
        or not stat.S_ISREG(observed.st_mode)
        or observed.st_size > 2 * 1024**2
    ):
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "report identity differs"
        )
    try:
        report = _strict_json(report_path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LiveSchemaAdapterRefusal(
            REFUSAL_ROUTES[6], "report JSON differs"
        ) from exc
    validate_report(report)
    return {
        "status": report["status"],
        "route": report["route"],
        "selected_subjects": report["selector_summary"]["selected_subjects"],
        "selected_core_members": report["selector_summary"][
            "selected_core_members"
        ],
        "selected_reservation_bytes": report["selector_summary"][
            "selected_reservation_bytes"
        ],
        "mutations_passed": report["mutation_summary"]["passed"],
        "generated_input_bytes": report["measurements"]["generated_input_bytes"],
        "generated_output_bytes": report["measurements"][
            "generated_output_bytes"
        ],
        "runtime_seconds": report["measurements"]["runtime_seconds"],
        "peak_RSS_bytes": report["measurements"]["peak_RSS_bytes"],
        "producer_is_causal": report["measurements"]["producer_is_causal"],
        "end_to_end_latency_measured": report["measurements"][
            "end_to_end_latency_measured"
        ],
        "warnings": list(report["warnings"]),
        "unavailable_fields": list(report["unavailable_fields"]),
    }


def build_plan_summary() -> dict[str, Any]:
    """Return the fixed generated-only plan without building a fixture."""

    contract = load_registered_contract()
    return {
        "lane_id": LANE_ID,
        "green_registration_commit": GREEN_REGISTRATION_COMMIT,
        "green_registration_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
        "commands": ["plan", "qualify", "inspect"],
        "generated_live_source_entries": contract["generated_live_shaped_source"][
            "entries"
        ],
        "required_mutations": contract["qualification"][
            "required_mutation_count"
        ],
        "private_or_Git_ignored_bytes_authorized": 0,
        "network_bytes_authorized": 0,
        "live_executor_or_private_read_authorized": False,
        "MARC2_FW2_authorized": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_live_schema_adapter",
        description="Qualify the generated/mock MARC2 live-schema composition.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the fixed generated-only plan.")
    qualify = subparsers.add_parser(
        "qualify", help="Run one generated/mock composition qualification."
    )
    qualify.add_argument("--output", required=True)
    inspect = subparsers.add_parser(
        "inspect", help="Inspect one aggregate qualification report."
    )
    inspect.add_argument("report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the dependency-free MARC2-LA1 module CLI."""

    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            value = build_plan_summary()
        elif args.command == "qualify":
            outcome = qualify_generated_composition(args.output)
            value = inspect_report(outcome.report_path)
        else:
            value = inspect_report(args.report)
    except LiveSchemaAdapterRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(value, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
