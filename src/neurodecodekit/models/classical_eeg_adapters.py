"""Standard-library contracts for optional classical EEG adapter plans."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


SCHEMA_NAME = "neurodecodekit.classical_eeg_adapter_plan"
SCHEMA_VERSION = "0.1.0"
PROOF_POSTURE = "symbolic_plan_only_no_adapter_import_fit_inference_or_score"
CONTRACT_RELATIVE_PATH = Path("registries/classical_eeg_adapter_contract.v0.json")
REGISTERED_CONTRACT_SHA256 = "ae1dc56d7610cb8a4a0bfb970e02c1466b53f5cff0391040eff51ac00084020d"
REGISTERED_CONTRACT_BYTES = 12_025
MAX_CONTRACT_BYTES = 1024 * 1024
DEFAULT_MAX_PLAN_BYTES = 1024 * 1024
ADAPTER_IDS = (
    "fixed_low_frequency_shrinkage_lda",
    "fixed_8_to_30_hz_csp_lda",
    "regularized_riemannian_mdm",
)
FACTOR_IDS = (
    "potential_shape_signal",
    "mu_energy_signal",
    "beta_energy_signal",
    "mixed_potential_mu_beta_signal",
    "left_right_spatial_reversal",
    "timing_only_labels_without_signal_relation",
    "peripheral_like_common_mode_artifact",
    "pure_noise",
)
PARTITION_BY_PAIR = ("train", "train", "train", "check", "check", "final")
PARTITION_ITEM_COUNTS = {"train": 48, "check": 32, "final": 16}
PARTITION_GROUP_COUNTS = {"train": 24, "check": 16, "final": 8}
FIT_STAGES = (
    "causal_preprocessing_state",
    "channel_quality_or_selection",
    "feature_standardization",
    "spatial_or_covariance_transform",
    "classifier_or_class_centroid",
    "class_prior",
)
REFUSAL_IDS = (
    "group_cross_partition",
    "pair_cross_partition",
    "duplicate_item_identity",
    "missing_group_identity",
    "row_level_random_split",
    "check_or_final_target_access",
    "evaluation_time_fit_or_update",
    "global_or_evaluation_normalization",
    "post_event_or_right_context",
    "forbidden_target_or_identity_field",
    "unknown_or_unregistered_adapter",
    "silent_dependency_fallback_or_substitution",
)
FORBIDDEN_KEY_FRAGMENTS = (
    "target_text",
    "reference_text",
    "intended_text",
    "performed_key",
    "performed_hand",
    "label_value",
    "prediction_value",
    "participant_id",
    "subject_id",
    "protected_path",
)
ACCESS_COUNTERS = {
    "synthetic_plan_builds": 1,
    "adapter_import_attempts": 0,
    "optional_dependency_installs": 0,
    "array_payload_reads": 0,
    "raw_data_reads": 0,
    "real_cache_reads": 0,
    "public_EEG_payload_reads": 0,
    "target_or_label_value_reads": 0,
    "feature_extraction_runs": 0,
    "parameter_update_runs": 0,
    "model_inference_runs": 0,
    "scoring_or_selection_runs": 0,
    "network_calls": 0,
    "provider_calls": 0,
    "stream_device_or_hardware_operations": 0,
    "scientific_claim_upgrades": 0,
}
PLAN_TOP_LEVEL_FIELDS = {
    "schema",
    "proof_posture",
    "contract",
    "plan_seed",
    "source",
    "adapter_specs",
    "selection",
    "items",
    "partition_summary",
    "fit_scope",
    "split_protocol",
    "evaluation_firewall",
    "causality",
    "dependency_routes",
    "access_counters",
    "warnings",
    "claim_boundary",
    "plan_sha256",
}


def load_registered_classical_adapter_contract(
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load the exact registered work-order-4 contract."""

    source = Path(path) if path is not None else _repo_root() / CONTRACT_RELATIVE_PATH
    with source.open("rb") as handle:
        payload = handle.read(MAX_CONTRACT_BYTES + 1)
    if len(payload) > MAX_CONTRACT_BYTES:
        raise ValueError("classical EEG adapter contract exceeds 1 MiB")
    if hashlib.sha256(payload).hexdigest() != REGISTERED_CONTRACT_SHA256:
        raise ValueError("classical EEG adapter contract SHA-256 mismatch")
    if len(payload) != REGISTERED_CONTRACT_BYTES:
        raise ValueError("classical EEG adapter contract byte count mismatch")
    contract = json.loads(payload.decode("utf-8"))
    if contract.get("schema_name") != "neurodecodekit.classical_eeg_adapter_contract":
        raise ValueError("classical EEG adapter contract schema mismatch")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("classical EEG adapter contract version mismatch")
    if contract.get("status") != (
        "preregistered_tier_B_contract_only_not_implemented_not_executed"
    ):
        raise ValueError("classical EEG adapter contract status mismatch")
    _validate_contract_identity(contract)
    return contract


def registered_classical_adapter_specs(
    contract_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Return independent copies of the three registered adapter specs."""

    contract = load_registered_classical_adapter_contract(contract_path)
    return copy.deepcopy(contract["adapter_families"])


def build_synthetic_classical_adapter_plan(
    *,
    contract_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a symbolic plan without reading arrays, labels, or adapter backends."""

    contract_source = (
        Path(contract_path) if contract_path is not None else _repo_root() / CONTRACT_RELATIVE_PATH
    )
    contract = load_registered_classical_adapter_contract(contract_source)
    items: list[dict[str, Any]] = []
    for factor_index, factor_id in enumerate(FACTOR_IDS):
        for pair_index, partition in enumerate(PARTITION_BY_PAIR):
            group_id = f"plan-f{factor_index:02d}-g{pair_index:02d}"
            pair_id = f"plan-f{factor_index:02d}-p{pair_index:02d}"
            for member_index in (0, 1):
                items.append(
                    {
                        "item_id": f"plan-f{factor_index:02d}-p{pair_index:02d}-m{member_index}",
                        "group_id": group_id,
                        "pair_id": pair_id,
                        "factor_id": factor_id,
                        "partition_id": partition,
                    }
                )
    plan: dict[str, Any] = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "bytes": REGISTERED_CONTRACT_BYTES,
            "sha256": REGISTERED_CONTRACT_SHA256,
        },
        "plan_seed": 5504,
        "source": {
            "kind": "synthetic_identity_formula_only",
            "item_count": 96,
            "group_count": 48,
            "factor_family_count": 8,
            "array_payload_reads": 0,
            "protected_class_values_created_or_read": 0,
        },
        "adapter_specs": copy.deepcopy(contract["adapter_families"]),
        "selection": {
            "winner_adapter_id": None,
            "winner_selected_now": False,
            "future_choice_source": contract["selection_contract"][
                "future_CSP_vs_Riemannian_choice_source"
            ],
            "mandatory_future_comparator": "train_only_no_signal_prior",
        },
        "items": items,
        "partition_summary": {
            "item_counts": dict(PARTITION_ITEM_COUNTS),
            "group_counts": dict(PARTITION_GROUP_COUNTS),
            "group_cross_partition_count": 0,
            "pair_cross_partition_count": 0,
            "duplicate_item_count": 0,
        },
        "fit_scope": copy.deepcopy(contract["fit_scope_contract"]),
        "split_protocol": {
            "partitions": ["train", "check", "final"],
            "group_unit": contract["grouped_split_contract"]["group_unit"],
            "synthetic_pair_is_group_surrogate": True,
            "row_level_random_split": False,
            "split_reassignment_after_label_or_outcome": False,
            "normalization_scope": "train_groups_only",
            "check_role": "future_bounded_public_family_selection_only",
            "final_role": "future_once_after_prediction_freeze_only",
        },
        "evaluation_firewall": copy.deepcopy(contract["evaluation_firewall"]),
        "causality": {
            "strictly_pre_event_timestamps_required": True,
            "right_context_samples": 0,
            "post_event_samples": 0,
            "known_event_boundary_required": True,
            "continuous_or_real_time_claim": False,
        },
        "dependency_routes": [
            {
                "adapter_id": row["adapter_id"],
                "audited_local_status": row["audited_local_status"],
                "available_for_execution_now": False,
                "optional_backend_import_attempts": 0,
                "fallback_adapter_id": None,
                "silent_fallback_allowed": False,
                "missing_dependency_behavior": "refuse_with_exact_optional_extra",
            }
            for row in contract["adapter_families"]
        ],
        "access_counters": dict(ACCESS_COUNTERS),
        "warnings": list(contract["warnings"]),
        "claim_boundary": dict(contract["claim_boundary"]),
    }
    plan["plan_sha256"] = canonical_classical_adapter_plan_sha256(plan)
    validate_classical_adapter_plan(plan, contract_path=contract_source)
    return plan


def validate_classical_adapter_plan(
    plan: Mapping[str, Any],
    *,
    contract_path: str | Path | None = None,
) -> dict[str, Any]:
    """Strictly validate identities, grouping, fit scope, and leakage boundaries."""

    contract = load_registered_classical_adapter_contract(contract_path)
    if set(plan) != PLAN_TOP_LEVEL_FIELDS:
        raise ValueError("classical EEG adapter plan fields mismatch")
    for section in ("source", "selection", "items", "causality", "dependency_routes"):
        _validate_forbidden_keys(plan.get(section))
    if plan.get("schema") != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("classical EEG adapter plan schema mismatch")
    if plan.get("proof_posture") != PROOF_POSTURE:
        raise ValueError("classical EEG adapter plan proof posture mismatch")
    expected_contract = {
        "path": CONTRACT_RELATIVE_PATH.as_posix(),
        "bytes": REGISTERED_CONTRACT_BYTES,
        "sha256": REGISTERED_CONTRACT_SHA256,
    }
    if plan.get("contract") != expected_contract:
        raise ValueError("classical EEG adapter plan contract binding mismatch")
    if plan.get("plan_seed") != 5504:
        raise ValueError("classical EEG adapter plan seed mismatch")
    if plan.get("source") != {
        "kind": "synthetic_identity_formula_only",
        "item_count": 96,
        "group_count": 48,
        "factor_family_count": 8,
        "array_payload_reads": 0,
        "protected_class_values_created_or_read": 0,
    }:
        raise ValueError("classical EEG adapter symbolic source mismatch")
    if plan.get("adapter_specs") != contract["adapter_families"]:
        raise ValueError("unknown or modified classical EEG adapter specification")

    selection = plan.get("selection", {})
    if selection != {
        "winner_adapter_id": None,
        "winner_selected_now": False,
        "future_choice_source": contract["selection_contract"][
            "future_CSP_vs_Riemannian_choice_source"
        ],
        "mandatory_future_comparator": "train_only_no_signal_prior",
    }:
        raise ValueError("classical EEG adapter selection must remain unchosen")
    _validate_items(plan)
    if plan.get("fit_scope") != contract["fit_scope_contract"]:
        raise ValueError("classical EEG adapter fit scope is not train-only")
    expected_split = {
        "partitions": ["train", "check", "final"],
        "group_unit": contract["grouped_split_contract"]["group_unit"],
        "synthetic_pair_is_group_surrogate": True,
        "row_level_random_split": False,
        "split_reassignment_after_label_or_outcome": False,
        "normalization_scope": "train_groups_only",
        "check_role": "future_bounded_public_family_selection_only",
        "final_role": "future_once_after_prediction_freeze_only",
    }
    if plan.get("split_protocol") != expected_split:
        raise ValueError("classical EEG adapter split or normalization protocol mismatch")
    if plan.get("evaluation_firewall") != contract["evaluation_firewall"]:
        raise ValueError("classical EEG adapter evaluation firewall mismatch")
    if plan.get("causality") != {
        "strictly_pre_event_timestamps_required": True,
        "right_context_samples": 0,
        "post_event_samples": 0,
        "known_event_boundary_required": True,
        "continuous_or_real_time_claim": False,
    }:
        raise ValueError("classical EEG adapter plan uses future or post-event context")
    if plan.get("dependency_routes") != _expected_dependency_routes(contract):
        raise ValueError("classical EEG adapter dependency route or fallback mismatch")
    if plan.get("access_counters") != ACCESS_COUNTERS:
        raise ValueError("classical EEG adapter plan access counters mismatch")
    if plan.get("warnings") != contract["warnings"]:
        raise ValueError("classical EEG adapter plan warnings mismatch")
    if plan.get("claim_boundary") != contract["claim_boundary"]:
        raise ValueError("classical EEG adapter plan claim boundary mismatch")
    if plan.get("plan_sha256") != canonical_classical_adapter_plan_sha256(plan):
        raise ValueError("classical EEG adapter canonical plan SHA-256 mismatch")
    return summarize_classical_adapter_plan(plan)


def save_classical_adapter_plan(
    path: str | Path,
    plan: Mapping[str, Any],
    *,
    contract_path: str | Path | None = None,
    max_plan_bytes: int = DEFAULT_MAX_PLAN_BYTES,
) -> None:
    """Write one validated plan without replacing an existing file."""

    if max_plan_bytes <= 0 or max_plan_bytes > DEFAULT_MAX_PLAN_BYTES:
        raise ValueError("classical EEG adapter plan cap must be positive and at most 1 MiB")
    validate_classical_adapter_plan(plan, contract_path=contract_path)
    destination = Path(path)
    payload = (json.dumps(plan, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > max_plan_bytes:
        raise ValueError(
            f"classical EEG adapter plan would write {len(payload)} bytes, "
            f"exceeding cap {max_plan_bytes}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb") as handle:
            handle.write(payload)
    except FileExistsError:
        raise FileExistsError(
            f"refusing to replace classical EEG adapter plan: {destination}"
        ) from None


def load_classical_adapter_plan(
    path: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_plan_bytes: int = DEFAULT_MAX_PLAN_BYTES,
) -> dict[str, Any]:
    """Load and validate one bounded symbolic plan."""

    if max_plan_bytes <= 0 or max_plan_bytes > DEFAULT_MAX_PLAN_BYTES:
        raise ValueError("classical EEG adapter plan cap must be positive and at most 1 MiB")
    source = Path(path)
    with source.open("rb") as handle:
        payload = handle.read(max_plan_bytes + 1)
    if len(payload) > max_plan_bytes:
        raise ValueError("classical EEG adapter plan exceeds output cap")
    plan = json.loads(payload.decode("utf-8"))
    validate_classical_adapter_plan(plan, contract_path=contract_path)
    return plan


def summarize_classical_adapter_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact target-free plan summary."""

    return {
        "schema": plan["schema"],
        "proof_posture": plan["proof_posture"],
        "plan_sha256": plan["plan_sha256"],
        "adapter_ids": [row["adapter_id"] for row in plan["adapter_specs"]],
        "winner_adapter_id": plan["selection"]["winner_adapter_id"],
        "item_count": len(plan["items"]),
        "group_count": len({row["group_id"] for row in plan["items"]}),
        "partition_summary": plan["partition_summary"],
        "fit_stages": [row["stage"] for row in plan["fit_scope"]],
        "producer_requires_right_context_samples": plan["causality"]["right_context_samples"],
        "post_event_samples": plan["causality"]["post_event_samples"],
        "dependency_routes": plan["dependency_routes"],
        "access_counters": plan["access_counters"],
        "warnings": plan["warnings"],
        "claim_boundary": plan["claim_boundary"],
    }


def make_classical_adapter_refusal_mutation(
    plan: Mapping[str, Any],
    refusal_id: str,
) -> dict[str, Any]:
    """Create one deterministic malformed plan for a registered refusal test."""

    if refusal_id not in REFUSAL_IDS:
        raise ValueError(f"unknown classical EEG adapter refusal: {refusal_id}")
    mutated = copy.deepcopy(dict(plan))
    train_index = next(
        index for index, row in enumerate(mutated["items"]) if row["partition_id"] == "train"
    )
    check_index = next(
        index for index, row in enumerate(mutated["items"]) if row["partition_id"] == "check"
    )
    if refusal_id == "group_cross_partition":
        mutated["items"][check_index]["group_id"] = mutated["items"][train_index]["group_id"]
    elif refusal_id == "pair_cross_partition":
        mutated["items"][check_index]["pair_id"] = mutated["items"][train_index]["pair_id"]
    elif refusal_id == "duplicate_item_identity":
        mutated["items"][1]["item_id"] = mutated["items"][0]["item_id"]
    elif refusal_id == "missing_group_identity":
        mutated["items"][0]["group_id"] = ""
    elif refusal_id == "row_level_random_split":
        mutated["split_protocol"]["row_level_random_split"] = True
    elif refusal_id == "check_or_final_target_access":
        mutated["evaluation_firewall"]["check_target_values_available_to_fit_or_transform"] = True
    elif refusal_id == "evaluation_time_fit_or_update":
        mutated["fit_scope"][2]["fit_scope"] = "all_partitions"
    elif refusal_id == "global_or_evaluation_normalization":
        mutated["split_protocol"]["normalization_scope"] = "global_all_partitions"
    elif refusal_id == "post_event_or_right_context":
        mutated["causality"]["post_event_samples"] = 1
    elif refusal_id == "forbidden_target_or_identity_field":
        mutated["items"][0]["target_text"] = "forbidden"
    elif refusal_id == "unknown_or_unregistered_adapter":
        mutated["adapter_specs"][0]["adapter_id"] = "unregistered_adapter"
    else:
        mutated["dependency_routes"][1]["fallback_adapter_id"] = ADAPTER_IDS[0]
        mutated["dependency_routes"][1]["silent_fallback_allowed"] = True
    mutated["plan_sha256"] = canonical_classical_adapter_plan_sha256(mutated)
    return mutated


def canonical_classical_adapter_plan_sha256(plan: Mapping[str, Any]) -> str:
    """Hash every plan field except the self-referential hash field."""

    payload = {key: value for key, value in plan.items() if key != "plan_sha256"}
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _validate_contract_identity(contract: Mapping[str, Any]) -> None:
    if tuple(row["adapter_id"] for row in contract["adapter_families"]) != ADAPTER_IDS:
        raise ValueError("classical EEG adapter family contract drifted")
    if tuple(row["stage"] for row in contract["fit_scope_contract"]) != FIT_STAGES:
        raise ValueError("classical EEG adapter fit-stage contract drifted")
    if tuple(contract["required_refusal_matrix"]) != REFUSAL_IDS:
        raise ValueError("classical EEG adapter refusal contract drifted")
    fixture = contract["plan_fixture"]
    if fixture.get("seed") != 5504 or fixture.get("items") != 96:
        raise ValueError("classical EEG adapter plan-fixture contract drifted")
    if fixture.get("groups") != 48 or fixture.get("factor_families") != 8:
        raise ValueError("classical EEG adapter group contract drifted")
    if fixture.get("partition_item_counts") != PARTITION_ITEM_COUNTS:
        raise ValueError("classical EEG adapter item partition contract drifted")
    if fixture.get("partition_group_counts") != PARTITION_GROUP_COUNTS:
        raise ValueError("classical EEG adapter group partition contract drifted")
    if contract["resource_caps"]["maximum_generated_output_bytes"] != DEFAULT_MAX_PLAN_BYTES:
        raise ValueError("classical EEG adapter output cap drifted")


def _validate_items(plan: Mapping[str, Any]) -> None:
    items = plan.get("items")
    if not isinstance(items, list) or len(items) != 96:
        raise ValueError("classical EEG adapter plan must contain exactly 96 items")
    expected_keys = {"item_id", "group_id", "pair_id", "factor_id", "partition_id"}
    item_ids: list[str] = []
    group_partitions: dict[str, set[str]] = defaultdict(set)
    pair_partitions: dict[str, set[str]] = defaultdict(set)
    factor_counts: Counter[str] = Counter()
    partition_counts: Counter[str] = Counter()
    group_counts: dict[str, set[str]] = defaultdict(set)
    for row in items:
        if not isinstance(row, Mapping) or set(row) != expected_keys:
            raise ValueError("classical EEG adapter item fields mismatch")
        if not all(isinstance(row[key], str) and row[key] for key in expected_keys):
            raise ValueError("classical EEG adapter item identities must be non-empty strings")
        if row["factor_id"] not in FACTOR_IDS:
            raise ValueError("classical EEG adapter item factor is unknown")
        if row["partition_id"] not in PARTITION_ITEM_COUNTS:
            raise ValueError("classical EEG adapter item partition is unknown")
        item_ids.append(row["item_id"])
        group_partitions[row["group_id"]].add(row["partition_id"])
        pair_partitions[row["pair_id"]].add(row["partition_id"])
        factor_counts[row["factor_id"]] += 1
        partition_counts[row["partition_id"]] += 1
        group_counts[row["partition_id"]].add(row["group_id"])
    duplicate_count = len(item_ids) - len(set(item_ids))
    group_cross = sum(len(values) > 1 for values in group_partitions.values())
    pair_cross = sum(len(values) > 1 for values in pair_partitions.values())
    if duplicate_count:
        raise ValueError("classical EEG adapter plan contains duplicate item identity")
    if group_cross:
        raise ValueError("classical EEG adapter group crosses partitions")
    if pair_cross:
        raise ValueError("classical EEG adapter pair crosses partitions")
    if factor_counts != Counter({factor: 12 for factor in FACTOR_IDS}):
        raise ValueError("classical EEG adapter factor inventory mismatch")
    if dict(partition_counts) != PARTITION_ITEM_COUNTS:
        raise ValueError("classical EEG adapter item partition counts mismatch")
    actual_group_counts = {name: len(group_counts[name]) for name in PARTITION_GROUP_COUNTS}
    if actual_group_counts != PARTITION_GROUP_COUNTS:
        raise ValueError("classical EEG adapter group partition counts mismatch")
    summary = plan.get("partition_summary")
    expected_summary = {
        "item_counts": dict(PARTITION_ITEM_COUNTS),
        "group_counts": dict(PARTITION_GROUP_COUNTS),
        "group_cross_partition_count": 0,
        "pair_cross_partition_count": 0,
        "duplicate_item_count": 0,
    }
    if summary != expected_summary:
        raise ValueError("classical EEG adapter partition summary mismatch")


def _expected_dependency_routes(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "adapter_id": row["adapter_id"],
            "audited_local_status": row["audited_local_status"],
            "available_for_execution_now": False,
            "optional_backend_import_attempts": 0,
            "fallback_adapter_id": None,
            "silent_fallback_allowed": False,
            "missing_dependency_behavior": "refuse_with_exact_optional_extra",
        }
        for row in contract["adapter_families"]
    ]


def _validate_forbidden_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError(f"classical EEG adapter plan contains forbidden field: {key}")
            _validate_forbidden_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _validate_forbidden_keys(item)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
