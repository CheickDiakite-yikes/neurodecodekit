import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries" / (
    "communication_eeg_prospective_generated_single_execution_"
    "dual_verification_contract.v0.json"
)
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_FS3_binds_exact_green_amendment_and_consumed_FS2() -> None:
    contract = _contract()
    parents = contract["bound_parents"]
    summary = contract["bound_parent_summary"]

    assert contract["gate_id"] == "COMM-P0-G-FS3-v0"
    assert contract["run_id"] == "COMM-P0-G-FS3-R0"
    assert len(parents) == summary["count"] == 10
    assert sum(row["bytes"] for row in parents) == summary["bytes"] == 67164
    for row in parents:
        path = ROOT / row["path"]
        assert path.stat().st_size == row["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    assert summary["amendment_3_green_commit"] == (
        "b15d3cf86fc4d6234d64c3a19cca394e72f43fc6"
    )
    assert summary["amendment_3_green_CI_run_id"] == 33174711145
    assert summary["amendment_3_on_GitHub_main"] is True
    assert summary["FS2_status"] == "consumed_FS2_PARK_no_rerun"


def test_FS3_preserves_one_exact_full_producer_schedule() -> None:
    producer = _contract()["full_producer_schedule"]

    assert producer["full_scale_producer_children"] == 1
    assert producer["complete_fictional_participants"] == 42
    assert producer["cohorts"] == 2
    assert producer["held_out_participant_folds"] == 42
    assert producer["conditions"] == 17
    assert producer["prior_fits"] == 42
    assert producer["residualizer_fits"] == 84
    assert producer["classifier_fits"] == 630
    assert producer["temperature_calibration_fits"] == 630
    assert producer["model_inference_runs"] == 714
    assert producer["prediction_sets"] == 1428
    assert producer["prediction_rows"] == 91392
    assert producer["refusal_observations"] == 70
    assert producer["cohort_target_deliveries"] == 2
    assert producer["cohort_scores"] == 2
    assert producer["post_target_updates"] == 0
    assert producer["maximum_prediction_rows_buffered"] == 256
    assert producer["complete_prediction_records_materialized"] is False
    assert producer["freeze_durable_and_verified_before_target_delivery"] is True


def test_FS3_verifier_is_independent_and_has_no_model_capability() -> None:
    verifier = _contract()["independent_verifier_scorer_schedule"]
    checks = _contract()["verifier_required_checks"]

    zero_operations = {
        "model_fits",
        "transform_fits",
        "model_inference_runs",
        "threshold_or_calibration_selection_operations",
        "prediction_sets_created",
        "prediction_rows_created",
        "parameter_updates",
        "language_model_operations",
    }
    assert all(verifier[key] == 0 for key in zero_operations)
    assert verifier["distinct_PID_and_isolated_workdir"] is True
    assert verifier["runs_after_producer"] is True
    assert verifier["prediction_stream_validation_passes"] == 1
    assert verifier["independent_generated_cohort_target_deliveries"] == 2
    assert verifier["independent_cohort_scores"] == 2
    assert verifier["aggregate_scores_must_exactly_match_producer"] is True
    assert checks["complete_participants"] == 42
    assert checks["prediction_sets"] == 1428
    assert checks["prediction_rows"] == 91392
    assert checks["target_delivery_only_after_freeze"] is True


def test_FS3_qualification_and_one_shot_barriers_are_strict() -> None:
    contract = _contract()
    scope = contract["implementation_scope"]
    authority = contract["execution_authority"]
    receipt = contract["FS3_receipt"]

    assert scope["implementation_qualification_replays"] == 2
    assert scope["implementation_qualification_participants_per_cohort_maximum"] == 3
    assert scope["implementation_qualification_refusal_observations"] == 140
    assert scope["implementation_qualification_full_scale_runs"] == 0
    assert authority["registration_authorizes_execution_now"] is False
    assert authority["registered_executions_maximum"] == 1
    assert authority["failure_timeout_refusal_or_cap_breach_consumes_attempt"] is True
    assert authority["retry_rerun_resume_repair_or_substitution_allowed"] is False
    assert authority["official_qualification_activation_from_FS3"] is False
    assert receipt["durable_no_replace_before_full_producer"] is True
    assert receipt["official_activation_loader_must_refuse_it"] is True
    assert receipt["official_marker_read_create_replace_rename_or_delete_operations"] == 0


def test_FS3_caps_operations_and_claims_remain_closed() -> None:
    contract = _contract()
    caps = contract["resource_caps"]
    counters = contract["operation_counters_before_implementation_or_execution"]

    assert caps["CPU_threads"] == caps["workers"] == caps["numerical_jobs"] == 1
    assert caps["wall_time_seconds"] == 180
    assert caps["peak_process_tree_RSS_bytes"] == 512 * 1024 * 1024
    assert caps["aggregate_incremental_disk_bytes"] == 537919488
    assert caps["free_bytes_required_before_reservation"] == (
        caps["free_bytes_required_after_reservation"]
        + caps["aggregate_incremental_disk_bytes"]
    )
    assert caps["free_bytes_required_after_reservation"] == 20 * 1024**3
    assert caps["network_requests"] == caps["network_bytes"] == 0
    assert caps["retained_generated_payload_bytes"] == 0
    assert all(value == 0 for value in counters.values())
    assert not any(contract["claim_boundary"].values())
    assert contract["active_gate"] == {
        "gate_id": "DREYER-C5R-1-HL",
        "changed": False,
        "all_authority_flags_false": True,
    }


def test_public_frontier_routes_to_green_amendment_3_and_pending_FS3() -> None:
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    registration = frontier["parallel_tier_A_communication_program"][
        "source_identity_preregistration"
    ]["prospective_synchronized_cohort_preregistration"][
        "generated_qualification_registration"
    ]

    amendment = registration["amendment_3_nonredundant_proof"]
    FS3 = registration["single_execution_dual_verification_rehearsal"]
    assert amendment["green_commit"] == "b15d3cf86fc4d6234d64c3a19cca394e72f43fc6"
    assert amendment["green_CI_run_id"] == 33174711145
    assert amendment["full_scale_producers"] == 1
    assert amendment["independent_model_free_verifiers"] == 1
    assert FS3["gate_id"] == "COMM-P0-G-FS3-v0"
    assert FS3["implementation_authorized_now"] is False
    assert FS3["execution_authorized_now"] is False
    assert FS3["official_qualification_execution_authorized_now"] is False
