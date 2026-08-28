import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_generated_two_child_rehearsal_preflight_boundary_decision.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_preflight_boundary_decision_binds_unchanged_green_artifacts() -> None:
    record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert record["gate_id"] == "COMM-P0-G-FS2-v0"
    assert record["run_id"] == "COMM-P0-G-FS2-R0"
    assert record["bound_green_head"] == "c9fb2a657e890debb39351f805d435ffaf00a3e6"
    assert record["bound_green_CI"] == {
        "run_id": 33169226797,
        "base_job_id": 98841994134,
        "optional_neuro_readers_job_id": 98841994387,
        "conclusion": "success",
        "present_on_GitHub_main": True,
    }
    for artifact in record["bound_artifacts"]:
        path = ROOT / artifact["path"]
        assert path.stat().st_size == artifact["bytes"]
        assert _sha256(path) == artifact["sha256"]


def test_preflight_event_is_exact_and_has_no_execution_surface() -> None:
    record = json.loads(REGISTRY.read_text(encoding="utf-8"))
    event = record["observed_preflight_event"]
    zero = record["observed_zero_surfaces"]

    assert event == {
        "command_entered_registered_executor": True,
        "result_path": "outputs/comm-p0-fs2/result.json",
        "receipt_path": "outputs/comm-p0-fs2/receipt.json",
        "shared_parent_directory_existed": False,
        "refusal_id": "COMM-P0-G:FS2-publication_collision_partial_write_or_cleanup_escape",
        "refusal_phase": "before_measured_start_and_durable_receipt",
        "CLI_launch_preflight_invocations": 1,
        "launch_preflight_refusals": 1,
    }
    assert all(value == 0 for value in zero.values())


def test_boundary_preserves_one_shot_and_claim_limits() -> None:
    record = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ruling = record["boundary_ruling"]
    preconditions = record["corrected_launch_preconditions"]
    claims = record["claim_boundary"]

    assert ruling == {
        "durable_receipt_is_consumption_boundary": True,
        "observed_preflight_refusal_consumed_registered_attempt": False,
        "observed_preflight_refusal_is_FS2_PASS_or_FS2_PARK": False,
        "corrected_launch_preflight_invocations_remaining_after_green": 1,
        "failure_timeout_refusal_or_park_after_receipt_consumes": True,
        "rerun_after_receipt_allowed": False,
        "second_corrected_pre_receipt_launch_allowed": False,
        "implementation_change_authorized": False,
    }
    assert preconditions == {
        "this_decision_commit_push_both_CI_jobs_green_and_on_main": True,
        "create_only_empty_Git_ignored_destination_directory": True,
        "exact_result_and_receipt_paths_absent": True,
        "implementation_proof_schedule_caps_and_output_names_unchanged": True,
        "network_real_private_official_device_release_and_claim_authority": False,
    }
    assert record["active_Tier_C_gate"] == {
        "gate_id": "DREYER-C5R-1-HL",
        "changed": False,
        "all_authority_flags_false": True,
    }
    assert not any(claims.values())
