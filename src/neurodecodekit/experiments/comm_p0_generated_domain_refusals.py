"""Domain-specific adversarial qualification for generated COMM-P0-G fixtures.

Every refusal is induced by changing one concrete field in an otherwise valid,
fictional protocol fixture.  The module performs no I/O beyond loading the frozen
contract through :mod:`comm_p0_generated`.
"""

from __future__ import annotations

import copy
import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core

INVENTORY_REFUSAL = "required_control_condition_missing_duplicated_or_substituted"
REPLAY_REFUSAL = "nondeterministic_fixture_prediction_or_freeze_replay"

Validator = Callable[[Mapping[str, Any], Mapping[str, Any]], None]
Mutator = Callable[[dict[str, Any], str, Mapping[str, Any]], str]


def _transaction() -> dict[str, Any]:
    return {
        "fit_count": 0,
        "prediction_count": 0,
        "target_delivery_count": 0,
        "score_count": 0,
        "published": False,
    }


def _refuse(family: str) -> None:
    raise core.CommP0GeneratedRefusal(family)


def family_inventory(contract: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Return the exact ordered category/family inventory or fail closed."""

    adversarial = contract.get("adversarial_qualification")
    if not isinstance(adversarial, Mapping):
        _refuse(INVENTORY_REFUSAL)
    categories = adversarial.get("categories")
    families_by_category = adversarial.get("refusal_families")
    if not isinstance(categories, Mapping) or not isinstance(families_by_category, Mapping):
        _refuse(INVENTORY_REFUSAL)
    if tuple(categories) != tuple(families_by_category):
        _refuse(INVENTORY_REFUSAL)

    rows: list[tuple[str, str]] = []
    for category, expected_count in categories.items():
        families = families_by_category.get(category)
        if (
            not isinstance(families, Sequence)
            or isinstance(families, (str, bytes))
            or len(families) != expected_count
            or any(not isinstance(family, str) or not family for family in families)
        ):
            _refuse(INVENTORY_REFUSAL)
        rows.extend((str(category), family) for family in families)

    expected_total = adversarial.get("registered_refusal_families")
    names = [family for _, family in rows]
    if len(rows) != expected_total or len(set(names)) != expected_total:
        _refuse(INVENTORY_REFUSAL)
    if adversarial.get("exact_wrapper_prefix") != "COMM-P0-G:":
        _refuse(REPLAY_REFUSAL)
    return tuple(rows)


def _target_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "public_decoder_payload": {"item_id": "generated-item-001", "features": [0.0]},
        "free_choice_target_precommitted": True,
        "target_vault_key_scope": "vault_only",
        "decoder_target_capability": "none",
        "prediction_emitted_after_precommit": True,
        "target_delivery_after_exact_green_freeze": True,
        "post_target_model_operations": 0,
        "transaction": _transaction(),
    }


def _mutate_target(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "recursive_target_label_reference_key_leakage":
        state["public_decoder_payload"] = {"item_id": "generated-item-001", "label": "yes"}
        return "public_decoder_payload"
    if family == "free_choice_target_before_precommit":
        state["free_choice_target_precommitted"] = False
        return "free_choice_target_precommitted"
    if family == "target_vault_key_capability_escape":
        state["target_vault_key_scope"] = "decoder_process"
        return "target_vault_key_scope"
    if family == "target_exposed_to_decoder_operator_freezer_or_language_context":
        state["decoder_target_capability"] = "language_context"
        return "decoder_target_capability"
    if family == "prediction_visible_before_target_precommit":
        state["prediction_emitted_after_precommit"] = False
        return "prediction_emitted_after_precommit"
    if family == "pre_freeze_target_delivery":
        state["target_delivery_after_exact_green_freeze"] = False
        return "target_delivery_after_exact_green_freeze"
    if family == "post_target_update_rerun_or_model_substitution":
        state["post_target_model_operations"] = 1
        return "post_target_model_operations"
    _refuse(INVENTORY_REFUSAL)


def _validate_target(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    try:
        core.assert_target_free(state["public_decoder_payload"])
    except core.CommP0GeneratedRefusal as exc:
        if exc.family != "recursive_target_label_reference_key_leakage":
            raise
        _refuse(exc.family)
    if state["free_choice_target_precommitted"] is not True:
        _refuse("free_choice_target_before_precommit")
    if state["target_vault_key_scope"] != "vault_only":
        _refuse("target_vault_key_capability_escape")
    if state["decoder_target_capability"] != "none":
        _refuse("target_exposed_to_decoder_operator_freezer_or_language_context")
    if state["prediction_emitted_after_precommit"] is not True:
        _refuse("prediction_visible_before_target_precommit")
    if state["target_delivery_after_exact_green_freeze"] is not True:
        _refuse("pre_freeze_target_delivery")
    if state["post_target_model_operations"] != 0:
        _refuse("post_target_update_rerun_or_model_substitution")


def _causal_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    partition = core.sha256_json({"windows": [[0, 512], [512, 1024]]})
    return {
        "right_context_samples": 0,
        "temporal_filter": "causal_left_aligned",
        "boundary_information_source": "stream_observed_only",
        "source_endpointer_enabled": True,
        "state_reset_scope": "gap_reconnect_session_participant",
        "offline_partition_sha256": partition,
        "incremental_partition_sha256": partition,
        "post_washout_context_seconds": 0.0,
        "transaction": _transaction(),
    }


def _mutate_causal(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "future_sample_or_right_context_use":
        state["right_context_samples"] = 1
        return "right_context_samples"
    if family == "noncausal_filter_or_centered_window":
        state["temporal_filter"] = "zero_phase_centered"
        return "temporal_filter"
    if family == "trial_or_block_boundary_oracle_use":
        state["boundary_information_source"] = "trial_manifest_oracle"
        return "boundary_information_source"
    if family == "source_endpointer_bypass":
        state["source_endpointer_enabled"] = False
        return "source_endpointer_enabled"
    if family == "state_bridge_across_gap_reconnect_session_or_participant":
        state["state_reset_scope"] = "never"
        return "state_reset_scope"
    if family == "offline_incremental_partition_mismatch":
        state["incremental_partition_sha256"] = "0" * 64
        return "incremental_partition_sha256"
    if family == "post_washout_context_limit_breach":
        state["post_washout_context_seconds"] = 0.001
        return "post_washout_context_seconds"
    _refuse(INVENTORY_REFUSAL)


def _validate_causal(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    if state["right_context_samples"] != 0:
        _refuse("future_sample_or_right_context_use")
    if state["temporal_filter"] != "causal_left_aligned":
        _refuse("noncausal_filter_or_centered_window")
    if state["boundary_information_source"] != "stream_observed_only":
        _refuse("trial_or_block_boundary_oracle_use")
    if state["source_endpointer_enabled"] is not True:
        _refuse("source_endpointer_bypass")
    if state["state_reset_scope"] != "gap_reconnect_session_participant":
        _refuse("state_bridge_across_gap_reconnect_session_or_participant")
    if state["offline_partition_sha256"] != state["incremental_partition_sha256"]:
        _refuse("offline_incremental_partition_mismatch")
    if state["post_washout_context_seconds"] != 0.0:
        _refuse("post_washout_context_limit_breach")


def _sensor_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    adapter = contract["synchronized_sensor_adapter"]
    eeg = [f"EEG_{index:02d}" for index in range(1, 65)]
    controls = list(contract["conditions"])
    return {
        "source_identity": ["synthetic_eeg", "generated_synchronized_fixture"],
        "channel_names": eeg
        + [
            "EOG_L",
            "EOG_R",
            "EOG_U",
            "EOG_D",
            "EMG_LL",
            "EMG_LR",
            "EMG_RL",
            "EMG_RR",
            "PHOTODIODE",
        ],
        "EEG_geometry_sha256": core.sha256_json(adapter["central_EEG_roles"]),
        "EOG_roles": ["EOG_L", "EOG_R", "EOG_U", "EOG_D"],
        "oral_EMG_roles": ["EMG_LL", "EMG_LR", "EMG_RL", "EMG_RR"],
        "synchronization_bindings": ["microphone", "hardware_trigger", "photodiode"],
        "control_conditions": controls,
        "transaction": _transaction(),
    }


def _mutate_sensor(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "modality_or_device_identity_drift":
        state["source_identity"] = ["synthetic_meg", "different_device"]
        return "source_identity"
    if family == "channel_count_name_or_order_drift":
        state["channel_names"] = list(reversed(state["channel_names"]))
        return "channel_names"
    if family == "EEG_geometry_missing_or_changed":
        state["EEG_geometry_sha256"] = "0" * 64
        return "EEG_geometry_sha256"
    if family == "EOG_role_inventory_mismatch":
        state["EOG_roles"] = ["EOG_L", "EOG_R"]
        return "EOG_roles"
    if family == "oral_EMG_role_or_laterality_mismatch":
        state["oral_EMG_roles"] = ["EMG_LL", "EMG_LR", "EMG_RL", "EMG_RL"]
        return "oral_EMG_roles"
    if family == "microphone_trigger_or_photodiode_binding_missing":
        state["synchronization_bindings"] = ["microphone", "photodiode"]
        return "synchronization_bindings"
    if family == "required_control_condition_missing_duplicated_or_substituted":
        state["control_conditions"] = list(state["control_conditions"][:-1])
        return "control_conditions"
    _refuse(INVENTORY_REFUSAL)


def _validate_sensor(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    expected = _sensor_fixture(contract)
    if state["source_identity"] != expected["source_identity"]:
        _refuse("modality_or_device_identity_drift")
    if state["channel_names"] != expected["channel_names"]:
        _refuse("channel_count_name_or_order_drift")
    if state["EEG_geometry_sha256"] != expected["EEG_geometry_sha256"]:
        _refuse("EEG_geometry_missing_or_changed")
    if state["EOG_roles"] != expected["EOG_roles"]:
        _refuse("EOG_role_inventory_mismatch")
    if state["oral_EMG_roles"] != expected["oral_EMG_roles"]:
        _refuse("oral_EMG_role_or_laterality_mismatch")
    if state["synchronization_bindings"] != expected["synchronization_bindings"]:
        _refuse("microphone_trigger_or_photodiode_binding_missing")
    if state["control_conditions"] != expected["control_conditions"]:
        _refuse("required_control_condition_missing_duplicated_or_substituted")


def _split_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    count = int(contract["fictional_cohorts"]["complete_participants_per_cohort"])
    return {
        "discovery_participants": [f"D-{index:02d}" for index in range(1, count + 1)],
        "replication_participants": [f"R-{index:02d}" for index in range(1, count + 1)],
        "held_out_fit_or_adaptation_rows": 0,
        "exclusion_policy": "protocol_predeclared_only",
        "complete_counts": {"discovery": count, "independent_replication": count},
        "cross_cohort_or_pooled_rescue": False,
        "calibration_scope": "source_participants_only",
        "transaction": _transaction(),
    }


def _mutate_split(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "participant_identity_collision":
        rows = list(state["discovery_participants"])
        rows[-1] = rows[0]
        state["discovery_participants"] = rows
        return "discovery_participants"
    if family == "discovery_replication_identity_overlap":
        rows = list(state["replication_participants"])
        rows[0] = state["discovery_participants"][0]
        state["replication_participants"] = rows
        return "replication_participants"
    if family == "held_out_participant_fit_threshold_or_adaptation":
        state["held_out_fit_or_adaptation_rows"] = 1
        return "held_out_fit_or_adaptation_rows"
    if family == "performance_based_exclusion_reassignment_or_substitution":
        state["exclusion_policy"] = "performance_based"
        return "exclusion_policy"
    if family == "cohort_cardinality_or_replacement_rule_violation":
        counts = dict(state["complete_counts"])
        counts["discovery"] -= 1
        state["complete_counts"] = counts
        return "complete_counts"
    if family == "pooled_result_or_other_cohort_rescues_failed_cohort":
        state["cross_cohort_or_pooled_rescue"] = True
        return "cross_cohort_or_pooled_rescue"
    if family == "calibration_source_method_or_row_violation":
        state["calibration_scope"] = "held_out_participant"
        return "calibration_scope"
    _refuse(INVENTORY_REFUSAL)


def _validate_split(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    discovery = list(state["discovery_participants"])
    replication = list(state["replication_participants"])
    if len(discovery) != len(set(discovery)) or len(replication) != len(set(replication)):
        _refuse("participant_identity_collision")
    if set(discovery) & set(replication):
        _refuse("discovery_replication_identity_overlap")
    if state["held_out_fit_or_adaptation_rows"] != 0:
        _refuse("held_out_participant_fit_threshold_or_adaptation")
    if state["exclusion_policy"] != "protocol_predeclared_only":
        _refuse("performance_based_exclusion_reassignment_or_substitution")
    expected = int(contract["fictional_cohorts"]["complete_participants_per_cohort"])
    if state["complete_counts"] != {"discovery": expected, "independent_replication": expected}:
        _refuse("cohort_cardinality_or_replacement_rule_violation")
    if state["cross_cohort_or_pooled_rescue"] is not False:
        _refuse("pooled_result_or_other_cohort_rescues_failed_cohort")
    if state["calibration_scope"] != "source_participants_only":
        _refuse("calibration_source_method_or_row_violation")


def _clock_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    ledger = core.sha256_json({"corrections": []})
    return {
        "source_sample_ranges": [[0, 512], [512, 1024]],
        "source_timestamps_seconds": [0.0, 1.0],
        "correction_ledger_pair": [ledger, ledger],
        "cross_clock_map_verified": True,
        "LSL_uncertainty_p99_seconds": 0.0005,
        "hardware_residual_p99_samples": 1,
        "event_order_seconds": [0.0, 0.1, 0.2, 0.3, 0.4],
        "transaction": _transaction(),
    }


def _mutate_clock(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "source_sample_overlap_reorder_or_hidden_gap":
        state["source_sample_ranges"] = [[0, 512], [511, 1024]]
        return "source_sample_ranges"
    if family == "source_timestamp_nonfinite_regression_or_clock_reset":
        state["source_timestamps_seconds"] = [0.0, -1.0]
        return "source_timestamps_seconds"
    if family == "correction_ledger_tamper":
        state["correction_ledger_pair"] = [state["correction_ledger_pair"][0], "0" * 64]
        return "correction_ledger_pair"
    if family == "cross_clock_mapping_missing_or_unverified":
        state["cross_clock_map_verified"] = False
        return "cross_clock_map_verified"
    if family == "LSL_clock_uncertainty_cap_breach":
        maximum = contract["synchronized_sensor_adapter"]["atomic_bundle"][
            "LSL_clock_uncertainty_p99_seconds_maximum"
        ]
        state["LSL_uncertainty_p99_seconds"] = float(maximum) + 0.001
        return "LSL_uncertainty_p99_seconds"
    if family == "hardware_residual_cap_breach":
        maximum = contract["synchronized_sensor_adapter"]["atomic_bundle"][
            "hardware_residual_p99_samples_maximum"
        ]
        state["hardware_residual_p99_samples"] = int(maximum) + 1
        return "hardware_residual_p99_samples"
    if family == "capture_arrival_processing_commit_presentation_order_violation":
        state["event_order_seconds"] = [0.0, 0.1, 0.3, 0.2, 0.4]
        return "event_order_seconds"
    _refuse(INVENTORY_REFUSAL)


def _validate_clock(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    ranges = state["source_sample_ranges"]
    if any(left[1] != right[0] for left, right in zip(ranges, ranges[1:])):
        _refuse("source_sample_overlap_reorder_or_hidden_gap")
    timestamps = state["source_timestamps_seconds"]
    if any(not math.isfinite(value) for value in timestamps) or any(
        left >= right for left, right in zip(timestamps, timestamps[1:])
    ):
        _refuse("source_timestamp_nonfinite_regression_or_clock_reset")
    if state["correction_ledger_pair"][0] != state["correction_ledger_pair"][1]:
        _refuse("correction_ledger_tamper")
    if state["cross_clock_map_verified"] is not True:
        _refuse("cross_clock_mapping_missing_or_unverified")
    atomic = contract["synchronized_sensor_adapter"]["atomic_bundle"]
    if state["LSL_uncertainty_p99_seconds"] > atomic["LSL_clock_uncertainty_p99_seconds_maximum"]:
        _refuse("LSL_clock_uncertainty_cap_breach")
    if state["hardware_residual_p99_samples"] > atomic["hardware_residual_p99_samples_maximum"]:
        _refuse("hardware_residual_cap_breach")
    order = state["event_order_seconds"]
    if any(left > right for left, right in zip(order, order[1:])):
        _refuse("capture_arrival_processing_commit_presentation_order_violation")


def _storage_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    caps = contract["resource_caps"]
    return {
        "raw_payload_bytes": caps["generated_input_bytes"],
        "private_derivative_bytes": caps["private_generated_output_bytes"],
        "temporary_output_bytes": caps["temporary_disk_bytes"],
        "public_output_bytes": caps["public_aggregate_output_bytes"],
        "permission_and_free_space": [True, 2 * 1024**3],
        "raw_materialization_mode": "streamed_no_backup",
        "publication_path_policy": "invocation_root_no_follow_no_replace",
        "transaction": _transaction(),
    }


def _mutate_storage(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    caps = contract["resource_caps"]
    if family == "raw_payload_cap_breach":
        state["raw_payload_bytes"] = caps["generated_input_bytes"] + 1
        return "raw_payload_bytes"
    if family == "private_derivative_cap_breach":
        state["private_derivative_bytes"] = caps["private_generated_output_bytes"] + 1
        return "private_derivative_bytes"
    if family == "temporary_output_cap_breach":
        state["temporary_output_bytes"] = caps["temporary_disk_bytes"] + 1
        return "temporary_output_bytes"
    if family == "public_output_cap_breach":
        state["public_output_bytes"] = caps["public_aggregate_output_bytes"] + 1
        return "public_output_bytes"
    if family == "total_permission_or_free_space_floor_breach":
        state["permission_and_free_space"] = [False, 0]
        return "permission_and_free_space"
    if family == "forbidden_raw_backup_or_full_float32_copy":
        state["raw_materialization_mode"] = "full_float32_backup"
        return "raw_materialization_mode"
    if family == "filesystem_capability_publication_or_cleanup_escape":
        state["publication_path_policy"] = "follow_symlink_outside_invocation_root"
        return "publication_path_policy"
    _refuse(INVENTORY_REFUSAL)


def _validate_storage(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    caps = contract["resource_caps"]
    if state["raw_payload_bytes"] > caps["generated_input_bytes"]:
        _refuse("raw_payload_cap_breach")
    if state["private_derivative_bytes"] > caps["private_generated_output_bytes"]:
        _refuse("private_derivative_cap_breach")
    if state["temporary_output_bytes"] > caps["temporary_disk_bytes"]:
        _refuse("temporary_output_cap_breach")
    if state["public_output_bytes"] > caps["public_aggregate_output_bytes"]:
        _refuse("public_output_cap_breach")
    permission, free_bytes = state["permission_and_free_space"]
    if permission is not True or free_bytes < 2 * 1024**3:
        _refuse("total_permission_or_free_space_floor_breach")
    if state["raw_materialization_mode"] != "streamed_no_backup":
        _refuse("forbidden_raw_backup_or_full_float32_copy")
    if state["publication_path_policy"] != "invocation_root_no_follow_no_replace":
        _refuse("filesystem_capability_publication_or_cleanup_escape")


def _privacy_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "voice_storage_root": "encrypted_protected_nonshareable",
        "shareable_BIDS_identity_fields": [],
        "public_individual_payloads": [],
        "public_artifact_sensitive_fields": [],
        "protected_audio_policy": "encrypted_and_separate",
        "release_request": {"requested": False, "all_bindings_green": False},
        "vault_side_channel_fields": [],
        "transaction": _transaction(),
    }


def _mutate_privacy(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "full_band_voice_in_shareable_BIDS_root":
        state["voice_storage_root"] = "shareable_BIDS_root"
        return "voice_storage_root"
    if family == "identity_consent_or_date_mapping_in_BIDS_root":
        state["shareable_BIDS_identity_fields"] = ["consent_name_date_map"]
        return "shareable_BIDS_identity_fields"
    if family == "individual_neural_audio_or_target_hash_publication":
        state["public_individual_payloads"] = ["participant_neural_row"]
        return "public_individual_payloads"
    if family == "private_path_or_secret_in_public_artifact":
        state["public_artifact_sensitive_fields"] = ["private_path"]
        return "public_artifact_sensitive_fields"
    if family == "protected_audio_root_not_encrypted_or_separated":
        state["protected_audio_policy"] = "plaintext_shared"
        return "protected_audio_policy"
    if family == "release_without_consent_privacy_or_Tier_C_binding":
        state["release_request"] = {"requested": True, "all_bindings_green": False}
        return "release_request"
    if family == "target_vault_ciphertext_timing_path_or_metadata_side_channel":
        state["vault_side_channel_fields"] = ["ciphertext_length"]
        return "vault_side_channel_fields"
    _refuse(INVENTORY_REFUSAL)


def _validate_privacy(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    if state["voice_storage_root"] != "encrypted_protected_nonshareable":
        _refuse("full_band_voice_in_shareable_BIDS_root")
    if state["shareable_BIDS_identity_fields"]:
        _refuse("identity_consent_or_date_mapping_in_BIDS_root")
    if state["public_individual_payloads"]:
        _refuse("individual_neural_audio_or_target_hash_publication")
    if state["public_artifact_sensitive_fields"]:
        _refuse("private_path_or_secret_in_public_artifact")
    if state["protected_audio_policy"] != "encrypted_and_separate":
        _refuse("protected_audio_root_not_encrypted_or_separated")
    release = state["release_request"]
    if release["requested"] and not release["all_bindings_green"]:
        _refuse("release_without_consent_privacy_or_Tier_C_binding")
    if state["vault_side_channel_fields"]:
        _refuse("target_vault_ciphertext_timing_path_or_metadata_side_channel")


def _prediction_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    prediction_rows = ["generated-item-001:P_plus_residual_central_EEG:free_choice_intend"]
    frozen = core.sha256_json(prediction_rows)
    replay = core.sha256_json({"replay": "generated"})
    return {
        "protocol_hash_pair": [core.CONTRACT_SHA256, core.CONTRACT_SHA256],
        "prediction_inventory": prediction_rows,
        "probability_vector": [0.25, 0.25, 0.25, 0.25],
        "prediction_freeze_hash_pair": [frozen, frozen],
        "replication_frozen_before_discovery_delivery": True,
        "replication_freeze_green_before_target_delivery": True,
        "replay_digest_pair": [replay, replay],
        "transaction": _transaction(),
    }


def _mutate_prediction(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "protocol_model_threshold_vocabulary_prior_or_code_hash_drift":
        state["protocol_hash_pair"] = [core.CONTRACT_SHA256, "0" * 64]
        return "protocol_hash_pair"
    if family == "prediction_inventory_missing_or_duplicate":
        state["prediction_inventory"] = list(state["prediction_inventory"]) * 2
        return "prediction_inventory"
    if family == "prediction_probability_nonfinite_or_sum_mismatch":
        state["probability_vector"] = [0.2, 0.2, 0.2, 0.2]
        return "probability_vector"
    if family == "prediction_row_or_probability_tamper_after_freeze":
        state["prediction_freeze_hash_pair"] = [state["prediction_freeze_hash_pair"][0], "0" * 64]
        return "prediction_freeze_hash_pair"
    if family == "replication_freeze_before_discovery_delivery_missing":
        state["replication_frozen_before_discovery_delivery"] = False
        return "replication_frozen_before_discovery_delivery"
    if family == "replication_prediction_freeze_not_green_before_delivery":
        state["replication_freeze_green_before_target_delivery"] = False
        return "replication_freeze_green_before_target_delivery"
    if family == "nondeterministic_fixture_prediction_or_freeze_replay":
        state["replay_digest_pair"] = [state["replay_digest_pair"][0], "0" * 64]
        return "replay_digest_pair"
    _refuse(INVENTORY_REFUSAL)


def _validate_prediction(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    if state["protocol_hash_pair"] != [core.CONTRACT_SHA256, core.CONTRACT_SHA256]:
        _refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    inventory = state["prediction_inventory"]
    if len(inventory) != 1 or len(set(inventory)) != 1:
        _refuse("prediction_inventory_missing_or_duplicate")
    core.validate_probability_vector(state["probability_vector"])
    if state["prediction_freeze_hash_pair"][0] != state["prediction_freeze_hash_pair"][1]:
        _refuse("prediction_row_or_probability_tamper_after_freeze")
    if state["replication_frozen_before_discovery_delivery"] is not True:
        _refuse("replication_freeze_before_discovery_delivery_missing")
    if state["replication_freeze_green_before_target_delivery"] is not True:
        _refuse("replication_prediction_freeze_not_green_before_delivery")
    if state["replay_digest_pair"][0] != state["replay_digest_pair"][1]:
        _refuse("nondeterministic_fixture_prediction_or_freeze_replay")


def _scorer_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "prediction_target_item_sets": [["generated-item-001"], ["generated-item-001"]],
        "scorer_capabilities": ["aggregate_score"],
        "exact_green_freeze": True,
        "delivery_and_prior_score_counts": [1, 0],
        "aggregate_contains_individual_protected_output": False,
        "invalid_prediction_policy": "maximum_frozen_loss_zero_accuracy_uncovered",
        "post_score_operations": [0, 0],
        "transaction": _transaction(),
    }


def _mutate_scorer(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    if family == "scorer_prediction_target_row_mismatch":
        state["prediction_target_item_sets"] = [["generated-item-001"], []]
        return "prediction_target_item_sets"
    if family == "scorer_fit_update_transform_or_model_capability":
        state["scorer_capabilities"] = ["aggregate_score", "model_fit"]
        return "scorer_capabilities"
    if family == "score_before_exact_green_freeze":
        state["exact_green_freeze"] = False
        return "exact_green_freeze"
    if family == "repeated_score_or_target_delivery":
        state["delivery_and_prior_score_counts"] = [2, 1]
        return "delivery_and_prior_score_counts"
    if family == "individual_protected_output_in_aggregate_score":
        state["aggregate_contains_individual_protected_output"] = True
        return "aggregate_contains_individual_protected_output"
    if family == "missing_invalid_or_nonfinite_prediction_dropped":
        state["invalid_prediction_policy"] = "drop_row"
        return "invalid_prediction_policy"
    if family == "post_score_mutation_repeat_or_output_replacement":
        state["post_score_operations"] = [1, 0]
        return "post_score_operations"
    _refuse(INVENTORY_REFUSAL)


def _validate_scorer(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    prediction_rows, target_rows = state["prediction_target_item_sets"]
    if prediction_rows != target_rows:
        _refuse("scorer_prediction_target_row_mismatch")
    if state["scorer_capabilities"] != ["aggregate_score"]:
        _refuse("scorer_fit_update_transform_or_model_capability")
    if state["exact_green_freeze"] is not True:
        _refuse("score_before_exact_green_freeze")
    if state["delivery_and_prior_score_counts"] != [1, 0]:
        _refuse("repeated_score_or_target_delivery")
    if state["aggregate_contains_individual_protected_output"] is not False:
        _refuse("individual_protected_output_in_aggregate_score")
    if state["invalid_prediction_policy"] != "maximum_frozen_loss_zero_accuracy_uncovered":
        _refuse("missing_invalid_or_nonfinite_prediction_dropped")
    if state["post_score_operations"] != [0, 0]:
        _refuse("post_score_mutation_repeat_or_output_replacement")


def _live_fixture(contract: Mapping[str, Any]) -> dict[str, Any]:
    live = contract["live_metrics"]
    required = sorted(
        key for key, value in live.items() if key.endswith("_report_required") and value
    )
    return {
        "reported_metrics": required,
        "coverage": [
            live["stable_commit_coverage_fraction_minimum"],
            live["per_command_coverage_fraction_minimum"],
        ],
        "false_commits_per_inactive_minute": 0.0,
        "drop_and_deadline_fractions": [0.0, 1.0],
        "stable_commit_latency_seconds": [1.0, 2.0],
        "capture_overhead_and_clock_map": [0.1, True],
        "post_freeze_updates_and_claim_basis": [0, "full_registered_protocol"],
        "transaction": _transaction(),
    }


def _mutate_live(state: dict[str, Any], family: str, contract: Mapping[str, Any]) -> str:
    live = contract["live_metrics"]
    if family == "live_required_metric_missing":
        state["reported_metrics"] = list(state["reported_metrics"][1:])
        return "reported_metrics"
    if family == "stable_commit_or_per_command_coverage_below_minimum":
        state["coverage"] = [
            live["stable_commit_coverage_fraction_minimum"] - 0.01,
            live["per_command_coverage_fraction_minimum"],
        ]
        return "coverage"
    if family == "false_commit_or_chatter_rate_above_maximum":
        state["false_commits_per_inactive_minute"] = (
            live["false_commits_per_inactive_minute_maximum"] + 0.01
        )
        return "false_commits_per_inactive_minute"
    if family == "dropped_invalid_or_deadline_gate_failure":
        state["drop_and_deadline_fractions"] = [
            live["dropped_or_invalid_chunk_fraction_maximum"] + 0.01,
            1.0,
        ]
        return "drop_and_deadline_fractions"
    if family == "stable_commit_latency_median_or_p95_above_maximum":
        state["stable_commit_latency_seconds"] = [
            live["stable_commit_latency_median_seconds_maximum"] + 0.01,
            live["stable_commit_latency_p95_seconds_maximum"] + 0.01,
        ]
        return "stable_commit_latency_seconds"
    if family == "capture_to_presentation_overhead_or_clock_map_failure":
        state["capture_overhead_and_clock_map"] = [0.1, False]
        return "capture_overhead_and_clock_map"
    if family == "live_update_or_accuracy_only_claim_upgrade":
        state["post_freeze_updates_and_claim_basis"] = [1, "accuracy_only"]
        return "post_freeze_updates_and_claim_basis"
    _refuse(INVENTORY_REFUSAL)


def _validate_live(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    live = contract["live_metrics"]
    expected = sorted(
        key for key, value in live.items() if key.endswith("_report_required") and value
    )
    if state["reported_metrics"] != expected:
        _refuse("live_required_metric_missing")
    macro, per_command = state["coverage"]
    if (
        macro < live["stable_commit_coverage_fraction_minimum"]
        or per_command < live["per_command_coverage_fraction_minimum"]
    ):
        _refuse("stable_commit_or_per_command_coverage_below_minimum")
    if (
        state["false_commits_per_inactive_minute"]
        > live["false_commits_per_inactive_minute_maximum"]
    ):
        _refuse("false_commit_or_chatter_rate_above_maximum")
    dropped, before_deadline = state["drop_and_deadline_fractions"]
    if (
        dropped > live["dropped_or_invalid_chunk_fraction_maximum"]
        or before_deadline < live["frames_processed_before_next_deadline_fraction_minimum"]
    ):
        _refuse("dropped_invalid_or_deadline_gate_failure")
    latency_median, latency_p95 = state["stable_commit_latency_seconds"]
    if (
        latency_median > live["stable_commit_latency_median_seconds_maximum"]
        or latency_p95 > live["stable_commit_latency_p95_seconds_maximum"]
    ):
        _refuse("stable_commit_latency_median_or_p95_above_maximum")
    overhead, clock_map = state["capture_overhead_and_clock_map"]
    if (
        overhead > live["capture_to_presentation_processing_overhead_p95_seconds_maximum"]
        or clock_map is not True
    ):
        _refuse("capture_to_presentation_overhead_or_clock_map_failure")
    updates, basis = state["post_freeze_updates_and_claim_basis"]
    if updates != 0 or basis == "accuracy_only":
        _refuse("live_update_or_accuracy_only_claim_upgrade")


_DOMAINS: dict[str, tuple[Callable[[Mapping[str, Any]], dict[str, Any]], Mutator, Validator]] = {
    "target_leakage_and_side_channels": (_target_fixture, _mutate_target, _validate_target),
    "causality_context_partition_and_state": (_causal_fixture, _mutate_causal, _validate_causal),
    "sensor_roles_geometry_and_synchronization": (
        _sensor_fixture,
        _mutate_sensor,
        _validate_sensor,
    ),
    "participant_split_calibration_and_aggregation": (
        _split_fixture,
        _mutate_split,
        _validate_split,
    ),
    "clock_sample_deadline_and_latency": (_clock_fixture, _mutate_clock, _validate_clock),
    "storage_filesystem_and_cleanup": (_storage_fixture, _mutate_storage, _validate_storage),
    "privacy_voice_identity_path_and_release": (
        _privacy_fixture,
        _mutate_privacy,
        _validate_privacy,
    ),
    "prediction_freeze_inventory_probability_and_replay": (
        _prediction_fixture,
        _mutate_prediction,
        _validate_prediction,
    ),
    "scorer_capability_delivery_and_one_shot": (_scorer_fixture, _mutate_scorer, _validate_scorer),
    "live_coverage_false_commit_drop_latency_and_overclaim": (
        _live_fixture,
        _mutate_live,
        _validate_live,
    ),
}


def qualify_refusal_case(
    category: str,
    family: str,
    contract: Mapping[str, Any],
    *,
    validator_override: Validator | None = None,
) -> dict[str, Any]:
    """Execute one concrete malformed fixture and verify its exact refusal."""

    inventory = family_inventory(contract)
    if (category, family) not in inventory or category not in _DOMAINS:
        _refuse(INVENTORY_REFUSAL)
    builder, mutator, validator = _DOMAINS[category]
    valid = builder(contract)
    validator(valid, contract)
    before_transaction_sha256 = core.sha256_json(valid["transaction"])
    malformed = copy.deepcopy(valid)
    mutated_field = mutator(malformed, family, contract)
    changed_fields = sorted(
        key for key in set(valid) | set(malformed) if valid.get(key) != malformed.get(key)
    )
    if changed_fields != [mutated_field] or mutated_field == "transaction":
        _refuse(REPLAY_REFUSAL)

    selected_validator = validator_override or validator
    try:
        selected_validator(malformed, contract)
    except core.CommP0GeneratedRefusal as exc:
        expected_wrapper = f"COMM-P0-G:{family}"
        if exc.family != family or str(exc) != expected_wrapper:
            _refuse(REPLAY_REFUSAL)
        wrapper = str(exc)
    else:
        _refuse(INVENTORY_REFUSAL)

    after_transaction_sha256 = core.sha256_json(malformed["transaction"])
    if after_transaction_sha256 != before_transaction_sha256:
        _refuse("post_score_mutation_repeat_or_output_replacement")
    return {
        "category": category,
        "family": family,
        "mutated_field": mutated_field,
        "valid_fixture_sha256": core.sha256_json(valid),
        "malformed_fixture_sha256": core.sha256_json(malformed),
        "wrapper": wrapper,
        "pre_state_sha256": before_transaction_sha256,
        "post_state_sha256": after_transaction_sha256,
        "state_unchanged": True,
    }


def validate_observations(
    observations: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> None:
    """Reject incomplete, extra, duplicate, or wrongly wrapped ledgers."""

    expected = family_inventory(contract)
    observed = tuple((row.get("category"), row.get("family")) for row in observations)
    if observed != expected or len(set(observed)) != len(observed):
        _refuse(INVENTORY_REFUSAL)
    for row in observations:
        family = row["family"]
        if (
            row.get("wrapper") != f"COMM-P0-G:{family}"
            or row.get("pre_state_sha256") != row.get("post_state_sha256")
            or row.get("state_unchanged") is not True
        ):
            _refuse(REPLAY_REFUSAL)


def exercise_domain_refusals(
    contract: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Exercise all 70 frozen families with concrete generated fixtures."""

    frozen = core.load_contract() if contract is None else contract
    observations = tuple(
        qualify_refusal_case(category, family, frozen)
        for category, family in family_inventory(frozen)
    )
    validate_observations(observations, frozen)
    return observations
