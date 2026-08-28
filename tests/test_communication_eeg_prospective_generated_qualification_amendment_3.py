import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_generated_qualification_amendment_3.v0.json"
)


def _record() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_amendment_3_binds_exact_unchanged_parent_artifacts() -> None:
    record = _record()

    assert record["amendment_id"] == "COMM-P0-G-A3"
    assert record["parent_registration_id"] == "COMM-P0-G-v0"
    for artifact in record["bound_parent_artifacts"]:
        path = ROOT / artifact["path"]
        assert path.stat().st_size == artifact["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]


def test_amendment_3_replaces_only_redundant_full_model_replay() -> None:
    record = _record()
    architecture = record["replacement_proof_architecture"]
    producer = record["full_scale_producer_schedule"]
    verifier = record["independent_verifier_schedule"]

    assert architecture["full_scale_producer_children"] == 1
    assert architecture["independent_model_free_verifier_scorer_children"] == 1
    assert architecture["full_scale_model_schedules"] == 1
    assert architecture["reduced_isolated_model_replays_before_activation"] == 2
    assert architecture["producer_and_verifier_aggregate_scores_must_match"] is True
    assert architecture["verifier_model_fit_transform_threshold_or_update_capability"] is False
    assert producer == {
        "complete_participants": 42,
        "cohorts": 2,
        "held_out_participant_folds": 42,
        "conditions": 17,
        "endpoints": 2,
        "prior_fits": 42,
        "residualizer_fits": 84,
        "classifier_fits": 630,
        "temperature_calibration_fits": 630,
        "model_inference_runs": 714,
        "prediction_sets": 1428,
        "prediction_rows": 91392,
        "shortcut_fixture_executions": 7,
        "cohort_target_deliveries": 2,
        "cohort_scores": 2,
        "post_target_updates": 0,
        "maximum_prediction_rows_buffered": 256,
    }
    assert verifier["model_fits"] == 0
    assert verifier["model_inference_runs"] == 0
    assert verifier["independent_generated_cohort_target_deliveries"] == 2
    assert verifier["independent_cohort_scores"] == 2
    assert verifier["post_target_updates"] == 0


def test_amendment_3_keeps_caps_authority_and_claims_closed() -> None:
    record = _record()
    unchanged = record["unchanged_fields"]
    authority = record["authority"]
    claims = record["claim_boundary"]

    assert unchanged["wall_time_seconds"] == 180
    assert unchanged["peak_process_tree_RSS_bytes"] == 536870912
    assert unchanged["aggregate_incremental_disk_bytes"] == 537919488
    assert unchanged["network_bytes"] == 0
    assert unchanged["retained_generated_payload_bytes"] == 0
    assert not any(authority.values())
    assert claims["generated_proof_architecture_corrected"] is True
    assert not any(
        value for key, value in claims.items() if key != "generated_proof_architecture_corrected"
    )
    assert record["active_Tier_C_gate"] == {
        "gate_id": "DREYER-C5R-1-HL",
        "changed": False,
        "all_authority_flags_false": True,
    }
