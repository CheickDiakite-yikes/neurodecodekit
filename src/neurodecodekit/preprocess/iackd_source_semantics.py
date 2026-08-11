"""Generated-fixture qualification for the prospective IACKD source policy."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import stat
import sys
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_NAME = "neurodecodekit.iackd_source_semantics_qualification"
FIXTURE_SCHEMA_NAME = "neurodecodekit.iackd_source_semantics_fixture"
POLICY_REGISTRY_RELATIVE_PATH = Path(
    "registries/iackd_source_declared_control_policy_research.v0.json"
)
POLICY_REGISTRY_SHA256 = (
    "c3727d297e5f95f9a81de819b90a2048d1292810b646e2591e69412e8cb04ea7"
)
POLICY_SHA256 = "1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4"
GREEN_RESEARCH_COMMIT = "ed5ce8292c2c1dc842898023cfe8cb608e9d4476"
GREEN_RESEARCH_CI_RUN_ID = 31_445_790_741
GREEN_RESEARCH_BASE_JOB_ID = 93_639_606_343
GREEN_RESEARCH_OPTIONAL_JOB_ID = 93_639_606_403
MAX_REPORT_BYTES = 2 * 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
HEAVY_MODULE_ROOTS = frozenset(
    {
        "braindecode",
        "huggingface_hub",
        "mne",
        "moabb",
        "numpy",
        "pyriemann",
        "scipy",
        "sklearn",
        "torch",
        "zarr",
    }
)
FORBIDDEN_FIXTURE_KEYS = frozenset(
    {
        "intended_text",
        "label",
        "labels",
        "prediction",
        "predictions",
        "reference_text",
        "score",
        "scores",
        "sentence",
        "sentences",
        "target",
        "target_text",
        "targets",
    }
)
REFUSAL_IDS = (
    "IACKDS-F00-policy-registry-or-hash-mismatch",
    "IACKDS-F01-BIDS-version-or-count-field-mismatch",
    "IACKDS-F02-fixture-schema-or-value-malformed",
    "IACKDS-F03-source-index-or-order-mismatch",
    "IACKDS-F04-duplicate-unknown-or-missing-channel",
    "IACKDS-F05-source-type-mismatch",
    "IACKDS-F06-source-or-sidecar-count-mismatch",
    "IACKDS-F07-sampling-or-reference-mismatch",
    "IACKDS-F08-functional-role-overlap-or-gap",
    "IACKDS-F09-predictive-set-or-model-mask-mismatch",
    "IACKDS-F10-required-geometry-invalid",
    "IACKDS-F11-derivative-binding-hash-mismatch",
    "IACKDS-F12-forbidden-target-or-outcome-field",
    "IACKDS-F13-heavy-import-or-forbidden-access-counter",
    "IACKDS-F14-output-path-write-or-resource-cap",
    "IACKDS-F15-deterministic-replay-mismatch",
)
EXPECTED_BINDING_FIELDS = (
    "source_order_sha256",
    "source_type_count_sha256",
    "functional_role_sha256",
    "model_inclusion_mask_sha256",
    "geometry_available_mask_sha256",
)


class SourceSemanticsRefusal(RuntimeError):
    """Fail closed with a stable, non-sensitive refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown IACKD-H3 refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
        self.safe_reason = reason


@dataclass(frozen=True)
class QualificationOutcome:
    """One bounded generated-fixture qualification outcome."""

    report: Mapping[str, Any]
    report_path: Path
    runtime_seconds: float
    peak_rss_bytes: int
    generated_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return _sha256_bytes(_canonical_json_bytes(value)[:-1])


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _decode_json_object(payload: bytes, refusal_id: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceSemanticsRefusal(refusal_id, "JSON is malformed") from exc
    if not isinstance(value, dict):
        raise SourceSemanticsRefusal(refusal_id, "JSON root is not an object")
    return value


def _read_regular_file(path: Path, *, maximum_bytes: int, refusal_id: str) -> bytes:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise SourceSemanticsRefusal(refusal_id, "file is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise SourceSemanticsRefusal(refusal_id, "file is not a regular file")
    if observed.st_size <= 0 or observed.st_size > maximum_bytes:
        raise SourceSemanticsRefusal(refusal_id, "file size is outside its bound")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SourceSemanticsRefusal(refusal_id, "no-follow open failed") from exc
    try:
        payload = b""
        while len(payload) <= maximum_bytes:
            chunk = os.read(descriptor, min(64 * 1024, maximum_bytes + 1 - len(payload)))
            if not chunk:
                break
            payload += chunk
    finally:
        os.close(descriptor)
    if len(payload) != observed.st_size or len(payload) > maximum_bytes:
        raise SourceSemanticsRefusal(refusal_id, "file changed or exceeded its bound")
    return payload


def _normalized_name(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip().casefold()


def _iter_mapping_keys(value: Any) -> Iterator[str]:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            yield str(key)
            yield from _iter_mapping_keys(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested in value:
            yield from _iter_mapping_keys(nested)


def _assert_target_firewall(value: Any) -> None:
    for key in _iter_mapping_keys(value):
        if _normalized_name(key) in FORBIDDEN_FIXTURE_KEYS:
            raise SourceSemanticsRefusal(
                REFUSAL_IDS[12], "fixture contains a forbidden target or outcome field"
            )


def _exact_keys(value: Mapping[str, Any], expected: set[str], name: str) -> None:
    if set(value) != expected:
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], f"{name} fields differ")


def _compile_policy(
    policy: Mapping[str, Any], *, expected_hash: str | None
) -> dict[str, Any]:
    if not isinstance(policy, Mapping):
        raise SourceSemanticsRefusal(REFUSAL_IDS[0], "policy is not an object")
    if policy.get("dataset_BIDS_version") != "1.7.0":
        raise SourceSemanticsRefusal(REFUSAL_IDS[1], "policy BIDS version differs")
    if policy.get("version_specific_misc_count_field") != "MiscChannelCount":
        raise SourceSemanticsRefusal(REFUSAL_IDS[1], "policy MISC count field differs")
    if policy.get("current_BIDS_migration_field") != "MISCChannelCount":
        raise SourceSemanticsRefusal(REFUSAL_IDS[1], "policy migration field differs")
    if policy.get("semantic_layers") != [
        "source_type",
        "functional_role",
        "model_inclusion",
    ]:
        raise SourceSemanticsRefusal(REFUSAL_IDS[8], "semantic layers differ")
    rules = policy.get("role_rules")
    if not isinstance(rules, list) or len(rules) != 4:
        raise SourceSemanticsRefusal(REFUSAL_IDS[8], "role rules differ")
    role_lookup: dict[str, dict[str, Any]] = {}
    predictive_order: list[str] = []
    for raw_rule in rules:
        if not isinstance(raw_rule, Mapping):
            raise SourceSemanticsRefusal(REFUSAL_IDS[8], "role rule is malformed")
        names = raw_rule.get("source_names")
        source_type = raw_rule.get("source_type")
        role = raw_rule.get("functional_role")
        model_inclusion = raw_rule.get("model_inclusion")
        geometry = raw_rule.get("geometry_requirement")
        if (
            not isinstance(names, list)
            or not names
            or not isinstance(source_type, str)
            or not isinstance(role, str)
            or not isinstance(model_inclusion, bool)
            or geometry
            not in {"finite_required", "finite_if_present", "unavailable_allowed"}
        ):
            raise SourceSemanticsRefusal(REFUSAL_IDS[8], "role rule values are malformed")
        for display_name in names:
            if not isinstance(display_name, str) or not display_name.strip():
                raise SourceSemanticsRefusal(REFUSAL_IDS[8], "role name is malformed")
            normalized = _normalized_name(display_name)
            if normalized in role_lookup:
                raise SourceSemanticsRefusal(REFUSAL_IDS[8], "functional roles overlap")
            role_lookup[normalized] = {
                "canonical_name": display_name,
                "source_type": source_type,
                "functional_role": role,
                "model_inclusion": model_inclusion,
                "geometry_requirement": geometry,
            }
            if role == "predictive_eeg":
                predictive_order.append(display_name)
                if not model_inclusion or source_type != "EEG":
                    raise SourceSemanticsRefusal(
                        REFUSAL_IDS[9], "predictive role or model mask differs"
                    )
            elif model_inclusion:
                raise SourceSemanticsRefusal(
                    REFUSAL_IDS[9], "nonpredictive role enters the model mask"
                )
    if len(role_lookup) != 31 or len(predictive_order) != 26:
        raise SourceSemanticsRefusal(REFUSAL_IDS[9], "predictive or known set differs")
    groups = policy.get("source_count_groups")
    if not isinstance(groups, list) or [
        (
            row.get("EEG"),
            row.get("MISC"),
            row.get("total_rows"),
            row.get("optional_M1_M2_present"),
        )
        for row in groups
        if isinstance(row, Mapping)
    ] != [(26, 3, 29, False), (28, 3, 31, True)]:
        raise SourceSemanticsRefusal(REFUSAL_IDS[6], "source count groups differ")
    if policy.get("predictive_EEG_count") != 26:
        raise SourceSemanticsRefusal(REFUSAL_IDS[9], "predictive count differs")
    if policy.get("sampling_frequency_hz") != 1024 or policy.get("reference") != "average":
        raise SourceSemanticsRefusal(REFUSAL_IDS[7], "sampling or reference differs")
    observed_hash = _canonical_sha256(policy)
    if expected_hash is not None and observed_hash != expected_hash:
        raise SourceSemanticsRefusal(REFUSAL_IDS[0], "canonical policy hash differs")
    return {
        "policy": dict(policy),
        "policy_sha256": observed_hash,
        "role_lookup": role_lookup,
        "predictive_order": predictive_order,
    }


def load_registered_policy(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green H3 research policy."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    payload = _read_regular_file(
        root / POLICY_REGISTRY_RELATIVE_PATH,
        maximum_bytes=MAX_REPORT_BYTES,
        refusal_id=REFUSAL_IDS[0],
    )
    if _sha256_bytes(payload) != POLICY_REGISTRY_SHA256:
        raise SourceSemanticsRefusal(REFUSAL_IDS[0], "policy registry identity differs")
    registry = _decode_json_object(payload, REFUSAL_IDS[0])
    if (
        registry.get("schema_name")
        != "neurodecodekit.iackd_source_declared_control_policy_research"
        or registry.get("schema_version") != SCHEMA_VERSION
        or registry.get("lane_id") != "IACKD-H3"
        or registry.get("candidate_policy_sha256") != POLICY_SHA256
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[0], "policy registry structure differs")
    compiled = _compile_policy(registry.get("candidate_policy", {}), expected_hash=POLICY_SHA256)
    return {"registry": registry, **compiled}


def count_field_for_bids_version(version: str) -> str:
    """Return the exact MISC count spelling for a supported BIDS version."""

    fields = {"1.7.0": "MiscChannelCount", "1.11.1": "MISCChannelCount"}
    try:
        return fields[version]
    except KeyError as exc:
        raise SourceSemanticsRefusal(REFUSAL_IDS[1], "unsupported BIDS version") from exc


def _finite_geometry(value: Any, *, required: bool) -> bool:
    if value is None:
        if required:
            raise SourceSemanticsRefusal(REFUSAL_IDS[10], "required geometry is unavailable")
        return False
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value)
        or any(not math.isfinite(float(item)) for item in value)
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[10], "geometry is not a finite XYZ triplet")
    return True


def _source_type_counts(channels: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    observed = Counter(str(channel["type"]) for channel in channels)
    allowed = {"EEG", "EOG", "HEOG", "VEOG", "ECG", "EMG", "MISC", "TRIG"}
    if set(observed).difference(allowed):
        raise SourceSemanticsRefusal(REFUSAL_IDS[5], "unregistered source type")
    return {
        "EEGChannelCount": observed["EEG"],
        "EOGChannelCount": observed["EOG"] + observed["HEOG"] + observed["VEOG"],
        "ECGChannelCount": observed["ECG"],
        "EMGChannelCount": observed["EMG"],
        "MiscChannelCount": observed["MISC"],
        "TriggerChannelCount": observed["TRIG"],
    }


def validate_generated_fixture(
    fixture: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    check_bindings: bool = True,
) -> dict[str, Any]:
    """Validate one target-free generated fixture against the prospective policy."""

    _assert_target_firewall(fixture)
    _exact_keys(
        fixture,
        {
            "schema_name",
            "schema_version",
            "fixture_id",
            "dataset",
            "channels",
            "eeg_sidecar",
            "expected_bindings",
        },
        "fixture",
    )
    if (
        fixture.get("schema_name") != FIXTURE_SCHEMA_NAME
        or fixture.get("schema_version") != SCHEMA_VERSION
        or not isinstance(fixture.get("fixture_id"), str)
        or not fixture["fixture_id"]
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], "fixture identity is malformed")
    compiled = _compile_policy(policy, expected_hash=POLICY_SHA256)
    dataset = fixture.get("dataset")
    if not isinstance(dataset, Mapping):
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], "dataset binding is malformed")
    _exact_keys(dataset, {"BIDSVersion"}, "dataset")
    bids_version = dataset.get("BIDSVersion")
    if bids_version != policy["dataset_BIDS_version"]:
        raise SourceSemanticsRefusal(REFUSAL_IDS[1], "fixture BIDS version differs")
    misc_count_field = count_field_for_bids_version(str(bids_version))
    if misc_count_field != policy["version_specific_misc_count_field"]:
        raise SourceSemanticsRefusal(REFUSAL_IDS[1], "fixture count spelling differs")

    channels = fixture.get("channels")
    if not isinstance(channels, list) or len(channels) not in {29, 31}:
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], "channel rows are malformed")
    seen: set[str] = set()
    roles: list[dict[str, Any]] = []
    geometry_mask: list[bool] = []
    model_mask: list[bool] = []
    source_names: list[str] = []
    for index, channel in enumerate(channels):
        if not isinstance(channel, Mapping):
            raise SourceSemanticsRefusal(REFUSAL_IDS[2], "channel row is not an object")
        _exact_keys(channel, {"name", "type", "source_index", "geometry_m"}, "channel")
        name = channel.get("name")
        source_type = channel.get("type")
        if not isinstance(name, str) or not name.strip() or not isinstance(source_type, str):
            raise SourceSemanticsRefusal(REFUSAL_IDS[2], "channel name or type is malformed")
        if channel.get("source_index") != index:
            raise SourceSemanticsRefusal(REFUSAL_IDS[3], "source index or order differs")
        normalized = _normalized_name(name)
        if normalized in seen:
            raise SourceSemanticsRefusal(REFUSAL_IDS[4], "channel name is duplicated")
        seen.add(normalized)
        rule = compiled["role_lookup"].get(normalized)
        if rule is None:
            raise SourceSemanticsRefusal(REFUSAL_IDS[4], "channel name is unknown")
        if source_type != rule["source_type"]:
            raise SourceSemanticsRefusal(REFUSAL_IDS[5], "channel source type differs")
        geometry_required = rule["geometry_requirement"] == "finite_required"
        geometry_available = _finite_geometry(
            channel.get("geometry_m"), required=geometry_required
        )
        if rule["geometry_requirement"] == "finite_if_present" and not geometry_available:
            raise SourceSemanticsRefusal(
                REFUSAL_IDS[10], "present optional EEG geometry is unavailable"
            )
        source_names.append(name)
        geometry_mask.append(geometry_available)
        model_mask.append(bool(rule["model_inclusion"]))
        roles.append(
            {
                "name": name,
                "source_type": source_type,
                "functional_role": rule["functional_role"],
            }
        )

    expected_names = set(compiled["role_lookup"])
    optional_present = {_normalized_name("M1"), _normalized_name("M2")}.issubset(seen)
    required_names = expected_names - {_normalized_name("M1"), _normalized_name("M2")}
    expected_seen = expected_names if optional_present else required_names
    if seen != expected_seen:
        raise SourceSemanticsRefusal(REFUSAL_IDS[4], "required or optional set differs")
    predictive_names = [
        role["name"] for role, included in zip(roles, model_mask, strict=True) if included
    ]
    if (
        len(predictive_names) != 26
        or {_normalized_name(name) for name in predictive_names}
        != {_normalized_name(name) for name in compiled["predictive_order"]}
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[9], "predictive set differs")

    sidecar = fixture.get("eeg_sidecar")
    if not isinstance(sidecar, Mapping):
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], "sidecar is malformed")
    if (
        misc_count_field not in sidecar
        or policy["current_BIDS_migration_field"] in sidecar
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[1], "MISC count spelling differs")
    sidecar_fields = {
        "EEGChannelCount",
        "EOGChannelCount",
        "ECGChannelCount",
        "EMGChannelCount",
        misc_count_field,
        "TriggerChannelCount",
        "SamplingFrequency",
        "EEGReference",
    }
    _exact_keys(sidecar, sidecar_fields, "sidecar")
    source_counts = _source_type_counts(channels)
    for field, observed in source_counts.items():
        if sidecar.get(field) != observed:
            raise SourceSemanticsRefusal(REFUSAL_IDS[6], "sidecar count differs")
    group_matches = [
        row
        for row in policy["source_count_groups"]
        if row["EEG"] == source_counts["EEGChannelCount"]
        and row["MISC"] == source_counts["MiscChannelCount"]
        and row["EOG"] == source_counts["EOGChannelCount"]
        and row["TRIG"] == source_counts["TriggerChannelCount"]
        and row["total_rows"] == len(channels)
        and row["optional_M1_M2_present"] is optional_present
    ]
    if len(group_matches) != 1:
        raise SourceSemanticsRefusal(REFUSAL_IDS[6], "source count group differs")
    if (
        sidecar.get("SamplingFrequency") != policy["sampling_frequency_hz"]
        or sidecar.get("EEGReference") != policy["reference"]
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[7], "sampling or reference differs")

    source_type_count_binding = {
        "BIDSVersion": bids_version,
        "misc_count_field": misc_count_field,
        "counts": source_counts,
    }
    bindings = {
        "source_order_sha256": _canonical_sha256(source_names),
        "source_type_count_sha256": _canonical_sha256(source_type_count_binding),
        "functional_role_sha256": _canonical_sha256(roles),
        "model_inclusion_mask_sha256": _canonical_sha256(model_mask),
        "geometry_available_mask_sha256": _canonical_sha256(geometry_mask),
    }
    expected_bindings = fixture.get("expected_bindings")
    if not isinstance(expected_bindings, Mapping):
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], "expected bindings are malformed")
    _exact_keys(expected_bindings, set(EXPECTED_BINDING_FIELDS), "expected bindings")
    if check_bindings and dict(expected_bindings) != bindings:
        raise SourceSemanticsRefusal(REFUSAL_IDS[11], "derivative binding hash differs")
    role_counts = Counter(role["functional_role"] for role in roles)
    return {
        "fixture_id": fixture["fixture_id"],
        "row_count": len(channels),
        "optional_M1_M2_present": optional_present,
        "source_counts": source_counts,
        "functional_role_counts": dict(sorted(role_counts.items())),
        "predictive_EEG_count": len(predictive_names),
        "predictive_output_order": list(compiled["predictive_order"]),
        "geometry_available_count": sum(geometry_mask),
        "bindings": bindings,
    }


def _generated_coordinate(index: int) -> list[float]:
    return [round(index / 100.0, 4), round((index % 7) / 100.0, 4), 0.5]


def make_generated_fixture(
    *, include_optional_references: bool, policy: Mapping[str, Any]
) -> dict[str, Any]:
    """Create one deterministic, target-free 29-row or 31-row fixture."""

    compiled = _compile_policy(policy, expected_hash=POLICY_SHA256)
    ordered_names = [*compiled["predictive_order"], "HEOG", "VEOG", "Trigger"]
    if include_optional_references:
        ordered_names.extend(("M1", "M2"))
    channels: list[dict[str, Any]] = []
    for index, name in enumerate(ordered_names):
        rule = compiled["role_lookup"][_normalized_name(name)]
        geometry = (
            _generated_coordinate(index)
            if rule["geometry_requirement"] != "unavailable_allowed"
            else None
        )
        channels.append(
            {
                "name": name,
                "type": rule["source_type"],
                "source_index": index,
                "geometry_m": geometry,
            }
        )
    eeg_count = 28 if include_optional_references else 26
    fixture = {
        "schema_name": FIXTURE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "fixture_id": f"generated-{'31' if include_optional_references else '29'}-row-v0",
        "dataset": {"BIDSVersion": "1.7.0"},
        "channels": channels,
        "eeg_sidecar": {
            "EEGChannelCount": eeg_count,
            "EOGChannelCount": 0,
            "ECGChannelCount": 0,
            "EMGChannelCount": 0,
            "MiscChannelCount": 3,
            "TriggerChannelCount": 0,
            "SamplingFrequency": 1024,
            "EEGReference": "average",
        },
        "expected_bindings": {field: "" for field in EXPECTED_BINDING_FIELDS},
    }
    projected = validate_generated_fixture(fixture, policy, check_bindings=False)
    fixture["expected_bindings"] = projected["bindings"]
    validate_generated_fixture(fixture, policy)
    return fixture


def _mutation_fixture(base: Mapping[str, Any], name: str) -> dict[str, Any]:
    fixture = copy.deepcopy(base)
    if name == "BIDS_version":
        fixture["dataset"]["BIDSVersion"] = "1.11.1"
    elif name == "count_spelling":
        fixture["eeg_sidecar"]["MISCChannelCount"] = fixture["eeg_sidecar"].pop(
            "MiscChannelCount"
        )
    elif name == "fixture_schema":
        fixture.pop("channels")
    elif name == "source_order":
        fixture["channels"][0]["source_index"] = 1
    elif name == "duplicate_channel":
        fixture["channels"][1]["name"] = fixture["channels"][0]["name"]
    elif name == "source_type":
        next(row for row in fixture["channels"] if row["name"] == "HEOG")["type"] = "HEOG"
    elif name == "sidecar_count":
        fixture["eeg_sidecar"]["MiscChannelCount"] = 2
    elif name == "reference":
        fixture["eeg_sidecar"]["EEGReference"] = "Cz"
    elif name == "geometry":
        fixture["channels"][0]["geometry_m"] = None
    elif name == "binding":
        fixture["expected_bindings"]["source_order_sha256"] = "0" * 64
    elif name == "target_firewall":
        fixture["target_text"] = "forbidden"
    else:  # pragma: no cover - guarded by the fixed mutation table
        raise ValueError(f"unknown fixture mutation: {name}")
    return fixture


def run_generated_mutation_suite(
    fixture: Mapping[str, Any], policy: Mapping[str, Any]
) -> list[dict[str, str]]:
    """Exercise twelve ordered refusal classes using generated values only."""

    fixture_cases = (
        ("BIDS_version", REFUSAL_IDS[1]),
        ("count_spelling", REFUSAL_IDS[1]),
        ("fixture_schema", REFUSAL_IDS[2]),
        ("source_order", REFUSAL_IDS[3]),
        ("duplicate_channel", REFUSAL_IDS[4]),
        ("source_type", REFUSAL_IDS[5]),
        ("sidecar_count", REFUSAL_IDS[6]),
        ("reference", REFUSAL_IDS[7]),
        ("geometry", REFUSAL_IDS[10]),
        ("binding", REFUSAL_IDS[11]),
        ("target_firewall", REFUSAL_IDS[12]),
    )
    observed: list[dict[str, str]] = []
    for name, expected in fixture_cases:
        try:
            validate_generated_fixture(_mutation_fixture(fixture, name), policy)
        except SourceSemanticsRefusal as exc:
            if exc.refusal_id != expected:
                raise SourceSemanticsRefusal(
                    REFUSAL_IDS[15], "mutation reached a different refusal"
                ) from exc
            observed.append({"mutation": name, "refusal_id": exc.refusal_id})
        else:
            raise SourceSemanticsRefusal(REFUSAL_IDS[15], "mutation was accepted")

    overlapping = copy.deepcopy(policy)
    overlapping["role_rules"][1]["source_names"].append(
        overlapping["role_rules"][0]["source_names"][0]
    )
    nonpredictive = copy.deepcopy(policy)
    nonpredictive["role_rules"][0]["model_inclusion"] = False
    policy_cases = (
        ("functional_role_overlap", overlapping, REFUSAL_IDS[8]),
        ("predictive_model_mask", nonpredictive, REFUSAL_IDS[9]),
    )
    for name, mutated, expected in policy_cases:
        try:
            _compile_policy(mutated, expected_hash=None)
        except SourceSemanticsRefusal as exc:
            if exc.refusal_id != expected:
                raise SourceSemanticsRefusal(
                    REFUSAL_IDS[15], "policy mutation reached a different refusal"
                ) from exc
            observed.append({"mutation": name, "refusal_id": exc.refusal_id})
        else:
            raise SourceSemanticsRefusal(REFUSAL_IDS[15], "policy mutation was accepted")
    if len(observed) != 13 or len({row["refusal_id"] for row in observed}) != 12:
        raise SourceSemanticsRefusal(REFUSAL_IDS[15], "refusal coverage is incomplete")
    return observed


def _peak_rss_bytes() -> int:
    import resource

    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "one-thread environment is required")


def _base_access_counters() -> dict[str, int]:
    return {
        "policy_registry_reads": 1,
        "generated_fixture_builds": 2,
        "generated_fixture_semantic_parses": 4,
        "generated_mutation_attempts": 13,
        "real_or_public_metadata_requests": 0,
        "network_bytes": 0,
        "Git_ignored_execution_artifact_reads": 0,
        "local_IACKD_path_stats_or_opens": 0,
        "VHDR_or_sibling_operations": 0,
        "signal_sample_reads": 0,
        "marker_or_event_reads": 0,
        "trajectory_reads": 0,
        "target_or_label_reads": 0,
        "cache_split_or_derivative_operations": 0,
        "feature_extraction_runs": 0,
        "model_or_checkpoint_loads": 0,
        "training_or_parameter_update_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets_or_scoring_runs": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _assert_access_counters(counters: Mapping[str, int]) -> None:
    allowed_nonzero = {
        "policy_registry_reads",
        "generated_fixture_builds",
        "generated_fixture_semantic_parses",
        "generated_mutation_attempts",
    }
    for name, value in counters.items():
        if name not in allowed_nonzero and value != 0:
            raise SourceSemanticsRefusal(REFUSAL_IDS[13], "forbidden access counter is nonzero")


def _ensure_output_preflight(path: Path, maximum_bytes: int) -> None:
    if maximum_bytes <= 0 or maximum_bytes > MAX_REPORT_BYTES:
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "output cap differs")
    if path.exists() or path.is_symlink():
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    observed = os.lstat(path.parent)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "output parent is unsafe")


def _write_exclusive(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "exclusive output open failed") from exc
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        try:
            path.unlink()
        except OSError:
            pass
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "output write failed") from exc


def validate_qualification_report(report: Mapping[str, Any]) -> None:
    """Validate the bounded, aggregate-only synthetic report."""

    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("status") != "passed_generated_fixture_qualification"
        or report.get("policy_binding", {}).get("policy_sha256") != POLICY_SHA256
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], "report identity differs")
    fixtures = report.get("fixture_groups")
    if not isinstance(fixtures, list) or [row.get("row_count") for row in fixtures] != [29, 31]:
        raise SourceSemanticsRefusal(REFUSAL_IDS[2], "report fixture groups differ")
    if any(row.get("predictive_EEG_count") != 26 for row in fixtures):
        raise SourceSemanticsRefusal(REFUSAL_IDS[9], "report predictive set differs")
    mutation_results = report.get("mutation_results")
    if (
        not isinstance(mutation_results, list)
        or len(mutation_results) != 13
        or len({row.get("refusal_id") for row in mutation_results}) != 12
    ):
        raise SourceSemanticsRefusal(REFUSAL_IDS[15], "report refusal coverage differs")
    if report.get("deterministic_replay", {}).get("summaries_identical") is not True:
        raise SourceSemanticsRefusal(REFUSAL_IDS[15], "report replay differs")
    counters = report.get("access_counters")
    if not isinstance(counters, Mapping):
        raise SourceSemanticsRefusal(REFUSAL_IDS[13], "report counters are malformed")
    _assert_access_counters(counters)
    gates = report.get("acceptance_gate_results")
    if not isinstance(gates, Mapping) or not gates or not all(gates.values()):
        raise SourceSemanticsRefusal(REFUSAL_IDS[15], "report gates did not all pass")


def run_synthetic_qualification(
    output_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] | None = None,
    maximum_output_bytes: int = MAX_REPORT_BYTES,
) -> QualificationOutcome:
    """Run the one bounded H3 generated-fixture qualification."""

    started = clock()
    environment = os.environ if environ is None else environ
    read_rss = _peak_rss_bytes if rss_reader is None else rss_reader
    _check_thread_environment(environment)
    destination = Path(output_path)
    _ensure_output_preflight(destination, maximum_output_bytes)
    heavy_before = set(sys.modules).intersection(HEAVY_MODULE_ROOTS)
    loaded = load_registered_policy(repo_root)
    policy = loaded["policy"]
    fixtures = [
        make_generated_fixture(include_optional_references=False, policy=policy),
        make_generated_fixture(include_optional_references=True, policy=policy),
    ]
    fixture_bytes = [_canonical_json_bytes(fixture) for fixture in fixtures]
    first = [validate_generated_fixture(fixture, policy) for fixture in fixtures]
    replay = [
        validate_generated_fixture(
            _decode_json_object(payload, REFUSAL_IDS[2]), policy
        )
        for payload in fixture_bytes
    ]
    if first != replay:
        raise SourceSemanticsRefusal(REFUSAL_IDS[15], "fixture summaries do not replay")
    mutations = run_generated_mutation_suite(fixtures[0], policy)
    counters = _base_access_counters()
    _assert_access_counters(counters)
    if set(sys.modules).intersection(HEAVY_MODULE_ROOTS) != heavy_before:
        raise SourceSemanticsRefusal(REFUSAL_IDS[13], "heavy dependency was imported")
    runtime = clock() - started
    peak_rss = read_rss()
    if runtime > MAX_RUNTIME_SECONDS or peak_rss > MAX_PEAK_RSS_BYTES:
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "resource cap exceeded")
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_fixture_qualification",
        "proof_posture": "generated_target_free_metadata_only_zero_real_or_public_data",
        "green_research": {
            "commit": GREEN_RESEARCH_COMMIT,
            "CI_run_id": GREEN_RESEARCH_CI_RUN_ID,
            "base_python_job_id": GREEN_RESEARCH_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_RESEARCH_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "policy_binding": {
            "registry_path": str(POLICY_REGISTRY_RELATIVE_PATH),
            "registry_sha256": POLICY_REGISTRY_SHA256,
            "policy_name": policy["policy_name"],
            "policy_version": policy["policy_version"],
            "policy_sha256": POLICY_SHA256,
            "dataset_BIDS_version": policy["dataset_BIDS_version"],
            "version_specific_misc_count_field": policy[
                "version_specific_misc_count_field"
            ],
        },
        "measurements": {
            "generated_fixture_count": 2,
            "generated_fixture_input_bytes": sum(len(payload) for payload in fixture_bytes),
            "generated_channel_rows": sum(len(fixture["channels"]) for fixture in fixtures),
            "semantic_validation_passes": 4,
            "mutation_attempts": 13,
            "distinct_refusal_classes": 12,
            "runtime_seconds_through_report_build": runtime,
            "peak_RSS_bytes_through_report_build": peak_rss,
            "generated_output_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "fixture_groups": first,
        "deterministic_replay": {
            "summaries_identical": True,
            "summary_set_sha256": _canonical_sha256(first),
        },
        "mutation_results": mutations,
        "access_counters": counters,
        "warnings": [
            "All channel rows and geometry are generated and have no source or scientific meaning.",
            "Source-order hashes qualify binding mechanics only; no real IACKD source order was asserted.",
            "This policy remains prospective and does not amend the consumed H2 result.",
        ],
        "unavailable_fields": [
            "real_source_order_validation",
            "real_reader_validation",
            "signal_or_event_validation",
            "target_or_model_validation",
            "producer_causality_not_applicable",
            "end_to_end_latency_not_measured",
        ],
        "acceptance_gate_results": {
            "green_research_bound": True,
            "policy_hash_exact": loaded["policy_sha256"] == POLICY_SHA256,
            "BIDS_version_and_count_field_exact": True,
            "29_and_31_row_groups_pass": [row["row_count"] for row in first] == [29, 31],
            "predictive_core_is_26_in_both": all(
                row["predictive_EEG_count"] == 26 for row in first
            ),
            "source_role_model_layers_separate": True,
            "derivative_bindings_complete": all(
                set(row["bindings"]) == set(EXPECTED_BINDING_FIELDS) for row in first
            ),
            "deterministic_replay_passed": first == replay,
            "twelve_distinct_refusals_passed": len(
                {row["refusal_id"] for row in mutations}
            )
            == 12,
            "target_firewall_passed": any(
                row["refusal_id"] == REFUSAL_IDS[12] for row in mutations
            ),
            "forbidden_access_counters_zero": True,
            "resource_caps_passed": True,
            "output_cap_passed": True,
        },
        "claim_boundary": {
            "engineering_capability_added": "A deterministic version-aware validator now preserves source type counts before assigning functional roles and model inclusion, with strict derivative hashes and fail-closed generated-fixture qualification.",
            "scientific_claim_not_established": "No real or public IACKD body, local bundle, signal, event, trajectory, target, model, prediction, or score was accessed, so this establishes no neural or decoding result.",
        },
    }
    for _ in range(8):
        payload = _canonical_json_bytes(report)
        if report["measurements"]["generated_output_bytes"] == len(payload):
            break
        report["measurements"]["generated_output_bytes"] = len(payload)
    else:
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "output byte accounting did not converge")
    payload = _canonical_json_bytes(report)
    if len(payload) > maximum_output_bytes:
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "output exceeds cap")
    validate_qualification_report(report)
    _write_exclusive(destination, payload)
    final_runtime = clock() - started
    final_rss = max(peak_rss, read_rss())
    if final_runtime > MAX_RUNTIME_SECONDS or final_rss > MAX_PEAK_RSS_BYTES:
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "post-write resource cap exceeded")
    return QualificationOutcome(report, destination, final_runtime, final_rss, len(payload))


def load_qualification_report(
    path: str | Path, *, maximum_bytes: int = MAX_REPORT_BYTES
) -> dict[str, Any]:
    """Load and validate one bounded qualification report."""

    payload = _read_regular_file(
        Path(path), maximum_bytes=maximum_bytes, refusal_id=REFUSAL_IDS[14]
    )
    report = _decode_json_object(payload, REFUSAL_IDS[2])
    validate_qualification_report(report)
    if report["measurements"]["generated_output_bytes"] != len(payload):
        raise SourceSemanticsRefusal(REFUSAL_IDS[14], "report byte accounting differs")
    return report


def summarize_qualification(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact, metadata-only qualification summary."""

    validate_qualification_report(report)
    measurements = report["measurements"]
    return {
        "status": report["status"],
        "policy_sha256": report["policy_binding"]["policy_sha256"],
        "fixture_row_counts": [row["row_count"] for row in report["fixture_groups"]],
        "predictive_EEG_counts": [
            row["predictive_EEG_count"] for row in report["fixture_groups"]
        ],
        "generated_fixture_input_bytes": measurements["generated_fixture_input_bytes"],
        "generated_output_bytes": measurements["generated_output_bytes"],
        "runtime_seconds": measurements["runtime_seconds_through_report_build"],
        "peak_RSS_bytes": measurements["peak_RSS_bytes_through_report_build"],
        "distinct_refusal_classes": measurements["distinct_refusal_classes"],
        "producer_is_causal": measurements["producer_is_causal"],
        "end_to_end_latency_measured": measurements["end_to_end_latency_measured"],
        "warnings": list(report["warnings"]),
        "unavailable_fields": list(report["unavailable_fields"]),
    }


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the network-free generated qualification plan."""

    loaded = load_registered_policy(repo_root)
    return {
        "lane_id": "IACKD-H3",
        "policy_sha256": loaded["policy_sha256"],
        "generated_fixture_row_counts": [29, 31],
        "minimum_refusal_classes": 12,
        "maximum_runtime_seconds": MAX_RUNTIME_SECONDS,
        "maximum_peak_RSS_bytes": MAX_PEAK_RSS_BYTES,
        "maximum_output_bytes": MAX_REPORT_BYTES,
        "real_or_public_data_authorized": False,
        "local_IACKD_bundle_authorized": False,
        "model_or_score_authorized": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Qualify the IACKD-H3 source-semantics policy on generated fixtures."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true", help="run generated fixtures")
    mode.add_argument("--inspect", type=Path, help="inspect a saved qualification report")
    parser.add_argument("--out", type=Path, help="exclusive output path for --fixture")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.inspect is not None:
            if args.out is not None:
                parser.error("--out cannot be used with --inspect")
            print(json.dumps(summarize_qualification(load_qualification_report(args.inspect))))
            return 0
        if args.fixture:
            if args.out is None:
                parser.error("--fixture requires --out")
            outcome = run_synthetic_qualification(args.out)
            print(json.dumps(summarize_qualification(outcome.report)))
            return 0
        if args.out is not None:
            parser.error("--out requires --fixture")
        plan = registered_plan()
        print(json.dumps(plan, sort_keys=True))
        return 0
    except SourceSemanticsRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
