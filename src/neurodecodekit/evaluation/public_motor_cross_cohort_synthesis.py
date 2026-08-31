"""Synthesize tracked public aggregate motor-EEG results without reopening data."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


SOURCE_IDENTITIES = {
    "wo9_result": (
        "registries/physionet_motor_positive_control_result.v0.json",
        "017c62162774b5cd32a635f58bb4c503f903a8e901cb2b696efa0890a1040579",
    ),
    "wo9_contract": (
        "registries/physionet_motor_positive_control_contract.v0.json",
        "4f00f8e2cb257e912a947b49268c1476554f3e671eb9322926592df4908b144e",
    ),
    "wo9r_result": (
        "registries/physionet_low_frequency_cohort_confirmation_result.v0.json",
        "d6cda8b4ce5f6da7add4a78ac8b1e74587cd8ab8eacf0dce8b806c076e85699a",
    ),
    "wo9r_contract": (
        "registries/physionet_low_frequency_cohort_confirmation_contract.v0.json",
        "ce0dcf5e5ddd598fb69b5baa73f827bbc3f51c4aeab8578d2d2eebda87cd0935",
    ),
    "bnci_result": (
        "registries/bnci_2014_001_stage_t_result.v0.json",
        "e836cefb9daf9df090f6f74a12ad90ae6448156d73850414fcca3367e81da9b2",
    ),
    "bnci_research": (
        "registries/bnci_2014_001_cross_participant_eeg_gain_research.v0.json",
        "5a333709dbbf8c2e30f33c9f47240d8830d34b78ac9eda5ae22ede68a751ded2",
    ),
}


def _identity(path: Path, root: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _load_bound_json(root: Path, key: str) -> tuple[dict[str, Any], dict[str, Any]]:
    relative, expected_sha256 = SOURCE_IDENTITIES[key]
    path = root / relative
    payload = path.read_bytes()
    identity = {
        "path": relative,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    if identity["sha256"] != expected_sha256:
        raise ValueError(f"source identity drift: {key}")
    return json.loads(payload), identity


def _fisher_two_p_values(first: float, second: float) -> tuple[float, float]:
    """Return Fisher's statistic and the exact chi-square(4) survival value."""

    product = first * second
    statistic = -2.0 * math.log(product)
    combined_p = product * (1.0 - math.log(product))
    return statistic, combined_p


def build_result(root: Path) -> dict[str, Any]:
    wo9, wo9_identity = _load_bound_json(root, "wo9_result")
    wo9_contract, wo9_contract_identity = _load_bound_json(root, "wo9_contract")
    wo9r, wo9r_identity = _load_bound_json(root, "wo9r_result")
    wo9r_contract, wo9r_contract_identity = _load_bound_json(root, "wo9r_contract")
    bnci, bnci_identity = _load_bound_json(root, "bnci_result")
    bnci_research, bnci_research_identity = _load_bound_json(root, "bnci_research")

    pilot_people = tuple(wo9_contract["dataset_binding"]["subjects"])
    confirmation_people = tuple(wo9r_contract["dataset_binding"]["participants"])
    overlap = sorted(set(pilot_people) & set(confirmation_people))
    if overlap:
        raise ValueError("EEGMMIDB cohorts are not participant-disjoint")
    eegmmidb_dataset_id = wo9_contract["dataset_binding"]["dataset_id"]
    eegmmidb_version = wo9_contract["dataset_binding"]["version"]
    if (
        wo9r_contract["dataset_binding"]["dataset_id"] != eegmmidb_dataset_id
        or wo9r_contract["dataset_binding"]["version"] != eegmmidb_version
    ):
        raise ValueError("EEGMMIDB phase source identity drift")
    bnci_source = bnci_research["source_snapshot"]
    distinct_dataset = bnci_source["official_dataset_id"] != eegmmidb_dataset_id
    if not distinct_dataset:
        raise ValueError("BNCI and EEGMMIDB source identities unexpectedly match")

    pilot = wo9["condition_metrics"]["low_frequency_shrinkage_lda_comparator"]
    confirmation = wo9r["condition_metrics"]["execution_native_primary"]
    fisher_statistic, fisher_p = _fisher_two_p_values(
        pilot["one_sided_within_participant_permutation_p"],
        confirmation["exact_one_sided_participant_sign_flip_p"],
    )

    pilot_n = len(pilot_people)
    confirmation_n = len(confirmation_people)
    replicated_people = pilot_n + confirmation_n
    correct = pilot["correct_count"] + confirmation["correct_count"]
    events = 45 + confirmation["event_count"]
    weighted_macro_ba = (
        pilot_n * pilot["macro_participant_balanced_accuracy"]
        + confirmation_n * confirmation["macro_participant_balanced_accuracy"]
    ) / replicated_people

    wo9_central = wo9["condition_metrics"]["central_sensorimotor_channel_model"]
    wo9_proxy = wo9["condition_metrics"]["frontal_occipital_proxy_channel_model"]
    wo9r_central = wo9r["condition_metrics"]["execution_central_sensorimotor"]
    wo9r_proxy = wo9r["condition_metrics"]["execution_frontal_proxy"]
    bnci_ba = bnci["aggregate_metrics"]["participant_macro_balanced_accuracy"]

    spatial_cohorts = [
        {
            "cohort": "EEGMMIDB_S001_S003_WO9",
            "participants": pilot_n,
            "candidate_id": "central_sensorimotor_channel_model",
            "candidate_macro_balanced_accuracy": wo9_central[
                "macro_participant_balanced_accuracy"
            ],
            "strongest_spatial_control": "frontal_occipital_proxy",
            "control_macro_balanced_accuracy": wo9_proxy[
                "macro_participant_balanced_accuracy"
            ],
        },
        {
            "cohort": "EEGMMIDB_S004_S015_WO9R",
            "participants": confirmation_n,
            "candidate_id": "execution_central_sensorimotor",
            "candidate_macro_balanced_accuracy": wo9r_central[
                "macro_participant_balanced_accuracy"
            ],
            "strongest_spatial_control": "frontal_proxy",
            "control_macro_balanced_accuracy": wo9r_proxy[
                "macro_participant_balanced_accuracy"
            ],
        },
        {
            "cohort": "BNCI_2014_001_STAGE_T",
            "participants": bnci["inventory"]["participants"],
            "candidate_id": "selected_E",
            "candidate_macro_balanced_accuracy": bnci_ba["selected_E"],
            "strongest_spatial_control": "posterior_EEG",
            "control_macro_balanced_accuracy": bnci_ba["posterior_EEG"],
            "registered_contrast": "C3_macro_control_margin",
        },
    ]
    for cohort in spatial_cohorts:
        cohort["candidate_minus_control_macro_balanced_accuracy"] = (
            cohort["candidate_macro_balanced_accuracy"]
            - cohort["control_macro_balanced_accuracy"]
        )

    spatial_people = sum(item["participants"] for item in spatial_cohorts)
    participant_weighted_spatial_margin = sum(
        item["participants"] * item["candidate_minus_control_macro_balanced_accuracy"]
        for item in spatial_cohorts
    ) / spatial_people
    equal_cohort_spatial_margin = sum(
        item["candidate_minus_control_macro_balanced_accuracy"] for item in spatial_cohorts
    ) / len(spatial_cohorts)
    negative_spatial_cohorts = sum(
        item["candidate_minus_control_macro_balanced_accuracy"] < 0.0
        for item in spatial_cohorts
    )

    source_identities = {
        "wo9_result": wo9_identity,
        "wo9_contract": wo9_contract_identity,
        "wo9r_result": wo9r_identity,
        "wo9r_contract": wo9r_contract_identity,
        "bnci_result": bnci_identity,
        "bnci_research": bnci_research_identity,
    }
    code_identity = _identity(Path(__file__).resolve(), root)
    public_bytes_read = sum(item["bytes"] for item in source_identities.values())

    return {
        "schema_name": "neurodecodekit.public_motor_cross_cohort_synthesis_result",
        "schema_version": "0.1.0",
        "result_id": "PUBLIC-MOTOR-SYNTHESIS-v0",
        "recorded_at": "2026-08-31",
        "status": "completed_retrospective_public_aggregate_scientific_synthesis",
        "analysis_class": "retrospective_evidence_synthesis_not_preregistered_confirmation",
        "source_identities": source_identities,
        "analysis_code": code_identity,
        "cohort_independence": {
            "EEGMMIDB_pilot_participants": list(pilot_people),
            "EEGMMIDB_confirmation_participants": list(confirmation_people),
            "EEGMMIDB_participant_overlap": overlap,
            "EEGMMIDB_dataset_id": eegmmidb_dataset_id,
            "EEGMMIDB_version": eegmmidb_version,
            "BNCI_official_dataset_id": bnci_source["official_dataset_id"],
            "BNCI_NEMAR_dataset_id": bnci_source["nemar_dataset_id"],
            "BNCI_NEMAR_version": bnci_source["nemar_version"],
            "BNCI_is_distinct_dataset": distinct_dataset,
            "EEGMMIDB_participant_disjoint_recordings": True,
            "BNCI_biological_person_overlap_with_EEGMMIDB_known": False,
            "independent_team_replication": False,
            "method_selection_independent_of_pilot_outcome": False,
        },
        "replicated_low_frequency_task_information": {
            "cohorts": 2,
            "participants": replicated_people,
            "held_out_execution_events": events,
            "correct_events": correct,
            "descriptive_event_accuracy": correct / events,
            "participant_count_weighted_mean_macro_balanced_accuracy": weighted_macro_ba,
            "pilot_within_participant_label_permutation_p": pilot[
                "one_sided_within_participant_permutation_p"
            ],
            "confirmation_participant_sign_flip_p": confirmation[
                "exact_one_sided_participant_sign_flip_p"
            ],
            "retrospective_Fisher_statistic": fisher_statistic,
            "retrospective_Fisher_nominal_p": fisher_p,
            "confirmatory_p_value": confirmation[
                "exact_one_sided_participant_sign_flip_p"
            ],
            "Fisher_value_is_confirmatory": False,
            "reason": (
                "the low-frequency family was promoted after the pilot outcome; "
                "the two p-values also use different null randomizations; only the "
                "disjoint S004-S015 result is prospective confirmation"
            ),
        },
        "cross_cohort_spatial_control_convergence": {
            "cohorts": spatial_cohorts,
            "cohort_participant_records": spatial_people,
            "cohorts_with_negative_candidate_minus_control_margin": (
                negative_spatial_cohorts
            ),
            "participant_count_weighted_descriptive_margin": (
                participant_weighted_spatial_margin
            ),
            "equal_cohort_weight_descriptive_margin": equal_cohort_spatial_margin,
            "nominal_all_negative_probability_under_independent_fair_signs": (
                0.5 ** len(spatial_cohorts)
            ),
            "sign_test_valid": False,
            "formal_pooled_effect_valid": False,
            "reason": (
                "tasks, feature definitions, and spatial controls differ across cohorts, "
                "the strongest-control operation favors negative margins, and "
                "participant-level paired margins are not public"
            ),
        },
        "peripheral_attribution": {
            "cohorts_with_recorded_EOG": 1,
            "cohorts_with_recorded_task_relevant_EMG": 0,
            "BNCI_EOG_plus_EEG_log_loss_gain": bnci["aggregate_metrics"][
                "C5_macro_EOG_delta"
            ],
            "BNCI_EOG_plus_deranged_EEG_log_loss_gain": bnci["aggregate_metrics"][
                "C5_macro_deranged_delta"
            ],
            "BNCI_EOG_delta_sign_flip_p": bnci["aggregate_metrics"][
                "C5_exact_EOG_delta_sign_flip_p"
            ],
            "BNCI_deranged_delta_sign_flip_p": bnci["aggregate_metrics"][
                "C5_exact_deranged_delta_sign_flip_p"
            ],
            "joint_EOG_EMG_attribution_tested": False,
        },
        "operation_counters": {
            "tracked_public_JSON_files_read": len(source_identities),
            "tracked_public_JSON_content_open_events": len(source_identities),
            "tracked_public_JSON_bytes_read": public_bytes_read,
            "tracked_public_result_JSON_files_read": 3,
            "tracked_public_result_JSON_bytes_read": sum(
                source_identities[key]["bytes"]
                for key in ("wo9_result", "wo9r_result", "bnci_result")
            ),
            "tracked_public_contract_or_identity_JSON_files_read": 3,
            "tracked_public_contract_or_identity_JSON_bytes_read": sum(
                source_identities[key]["bytes"]
                for key in ("wo9_contract", "wo9r_contract", "bnci_research")
            ),
            "raw_neural_payload_reads": 0,
            "private_or_ignored_reads": 0,
            "target_deliveries": 0,
            "model_fits": 0,
            "prediction_sets": 0,
            "scores": 0,
            "network_requests": 0,
        },
        "scientific_conclusion": {
            "supported": (
                "A fixed low-frequency EEG representation prospectively replicated "
                "held-out-run left-right task information in 12 fresh participants "
                "after a three-participant discovery cohort."
            ),
            "convergent_negative_result": (
                "No examined registered candidate contrast outperformed its strongest "
                "available spatial control across the three cohort phases."
            ),
            "active_FMSR1_conjunction_established": False,
            "why_not": (
                "No cohort jointly measured and tested EOG plus all relevant-effector "
                "EMG with the complete frozen spatial, timing, shift, and derangement arms."
            ),
            "brain_specific_motor_signal_established": False,
            "language_or_thought_decoding_established": False,
            "clinical_claim_established": False,
        },
        "warnings": [
            "aggregate_only_synthesis_does_not_reopen_or_rescore_consumed_experiments",
            "retrospective_Fisher_combination_is_descriptive_not_confirmatory",
            "three_cohort_sign_probability_is_nominal_not_a_valid_inferential_p_value",
            "cross_cohort_spatial_effect_pooling_is_not_valid_without_harmonized_methods",
            "task_information_is_not_neural_source_attribution",
        ],
    }


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    print(json.dumps(build_result(root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
