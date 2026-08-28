import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "registries" / (
    "communication_eeg_prospective_generated_official_coordinator_"
    "proof_closeout.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_exact_green_remote_proof_is_bound() -> None:
    record = _load_record()
    green = record["green_implementation"]

    assert green["final_green_head"] == (
        "669c858d9c35f33bb39d5a71aa886d645a832497"
    )
    assert green["CI_run_id"] == 33161053075
    assert green["base_python_job_id"] == 98815336723
    assert green["optional_neuro_readers_job_id"] == 98815336577
    assert green["both_required_jobs_green"] is True
    assert green["on_GitHub_main"] is True
    assert green["promotion_was_non_forced_fast_forward"] is True


def test_bound_green_artifacts_are_byte_exact() -> None:
    record = _load_record()
    rows = record["bound_artifacts"]

    assert len(rows) == record["bound_artifact_summary"]["count"] == 3
    assert sum(row["bytes"] for row in rows) == 17813
    for row in rows:
        path = ROOT / row["path"]
        assert path.is_file()
        assert path.stat().st_size == row["bytes"]
        assert _sha256(path) == row["sha256"]
    assert record["transitive_implementation_artifact_summary"] == {
        "count": 16,
        "bytes": 409861,
        "bound_by_implementation_registry": True,
    }


def test_measurement_is_generated_reduced_and_not_official() -> None:
    record = _load_record()
    measurement = record["reduced_generated_measurement"]

    assert record["proof_only"] is True
    assert record["new_execution_performed"] is False
    assert measurement["fictional_participants_per_cohort"] == 3
    assert measurement["isolated_child_process_replays"] == 2
    assert measurement["cohort_target_deliveries_total"] == 4
    assert measurement["cohort_scores_total"] == 4
    assert measurement["post_target_updates"] == 0
    assert measurement["network_bytes"] == 0
    assert measurement["real_or_private_reads"] == 0
    assert measurement["device_operations"] == 0
    assert measurement["retained_generated_payload_bytes"] == 0
    assert measurement["official_qualification_invocations"] == 0


def test_remaining_gates_and_claims_stay_closed() -> None:
    record = _load_record()
    gates = record["remaining_gates"]
    claims = record["claim_boundary"]

    assert (
        gates["two_full_21_person_per_cohort_replays_under_180_seconds_proven"]
        is False
    )
    assert gates["separate_full_scale_rehearsal_registration_required"] is True
    assert gates["activation_record_exists"] is False
    assert gates["activation_remotely_green"] is False
    assert gates["official_generated_qualification_executed"] is False
    assert gates["official_generated_qualification_consumed"] is False
    assert record["active_gate"] == {
        "gate_id": "DREYER-C5R-1-HL",
        "changed": False,
        "all_authority_flags_false": True,
    }
    assert claims["generated_coordinator_engineering_proven"] is True
    assert all(
        value is False
        for key, value in claims.items()
        if key != "generated_coordinator_engineering_proven"
    )
