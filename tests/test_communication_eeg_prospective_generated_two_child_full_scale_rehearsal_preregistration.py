import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries" / (
    "communication_eeg_prospective_generated_two_child_full_scale_"
    "rehearsal_contract.v0.json"
)


def _load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_parent_artifacts_are_exact_and_green_proof_is_bound() -> None:
    contract = _load_contract()
    rows = contract["bound_parents"]

    assert len(rows) == contract["bound_parent_summary"]["count"] == 4
    assert sum(row["bytes"] for row in rows) == 30797
    for row in rows:
        path = ROOT / row["path"]
        assert path.is_file()
        assert path.stat().st_size == row["bytes"]
        assert _sha256(path) == row["sha256"]
    assert contract["bound_parent_summary"]["green_coordinator_head"] == (
        "669c858d9c35f33bb39d5a71aa886d645a832497"
    )
    assert contract["bound_parent_summary"]["green_proof_closeout_head"] == (
        "f9a8e8f6eb73081bbc0ec14ef9b52c3a8fbfb474"
    )


def test_exact_two_replay_schedule_is_frozen() -> None:
    contract = _load_contract()
    per_replay = contract["schedule_per_replay"]
    total = contract["two_replay_totals"]

    doubled = {
        "prior_fits",
        "residualizer_fits",
        "classifier_fits",
        "temperature_calibration_fits",
        "model_inference_runs",
        "prediction_sets",
        "prediction_rows",
        "numerical_shortcut_fixture_executions",
        "refusal_observations",
        "cohort_target_deliveries",
        "cohort_scores",
        "shortcut_target_deliveries",
        "shortcut_scores",
        "post_target_updates",
    }
    assert per_replay["fictional_participants_per_cohort"] == 21
    assert per_replay["cohorts"] == 2
    assert total["isolated_child_process_replays"] == 2
    assert total["strictly_sequential"] is True
    assert total["concurrent_children_maximum"] == 1
    for key in doubled:
        assert total[key] == 2 * per_replay[key]
    assert per_replay["maximum_prediction_rows_buffered"] == 256
    assert per_replay["complete_prediction_records_materialized"] is False


def test_resources_preserve_storage_and_one_thread_boundary() -> None:
    caps = _load_contract()["resource_caps"]

    assert caps["CPU_threads"] == caps["workers"] == caps["numerical_jobs"] == 1
    assert caps["wall_time_seconds"] == 180
    assert caps["peak_process_tree_RSS_bytes"] == 512 * 1024 * 1024
    assert caps["aggregate_incremental_disk_bytes"] == 537919488
    assert caps["public_target_free_result_bytes"] == 1024 * 1024
    assert caps["free_bytes_required_before_reservation"] == (
        caps["free_bytes_required_after_reservation"]
        + caps["aggregate_incremental_disk_bytes"]
    )
    assert caps["free_bytes_required_after_reservation"] == 20 * 1024**3
    assert caps["network_requests"] == caps["network_bytes"] == 0
    assert caps["retained_generated_payload_bytes"] == 0


def test_execution_is_delayed_one_shot_and_nonofficial() -> None:
    contract = _load_contract()
    authority = contract["execution_authority"]
    implementation = contract["implementation_scope"]
    receipt = contract["rehearsal_receipt"]

    assert authority["registration_authorizes_execution_now"] is False
    assert authority["registered_executions_maximum"] == 1
    assert authority["failure_timeout_or_refusal_consumes_attempt"] is True
    assert authority["retry_rerun_resume_or_substitution_allowed"] is False
    assert implementation["green_coordinator_modified"] is False
    assert implementation["implementation_qualification_full_scale_runs"] == 0
    assert receipt["new_schema_separate_from_official_marker"] is True
    assert receipt["official_activation_loader_must_refuse_it"] is True
    assert receipt["official_marker_read_create_replace_rename_or_delete_operations"] == 0


def test_all_operations_and_claims_are_initially_false() -> None:
    contract = _load_contract()
    counters = contract["operation_counters_before_implementation_or_execution"]
    claims = contract["claim_boundary"]

    assert all(value == 0 for value in counters.values())
    assert all(value is False for value in claims.values())
    assert contract["active_gate"] == {
        "gate_id": "DREYER-C5R-1-HL",
        "changed": False,
        "all_authority_flags_false": True,
    }
