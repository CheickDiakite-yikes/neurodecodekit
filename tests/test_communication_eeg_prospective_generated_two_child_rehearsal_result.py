import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_generated_two_child_rehearsal_result.v0.json"
)
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"


def _record() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_fs2_result_is_consumed_park_with_exact_evidence() -> None:
    record = _record()

    assert record["gate_id"] == "COMM-P0-G-FS2-v0"
    assert record["run_id"] == "COMM-P0-G-FS2-R0"
    assert record["route"] == "FS2_PARK"
    assert record["failure_family"] == "FS2-resource_or_monitor_failure"
    assert record["attempt_consumed"] is True
    assert record["retry_rerun_resume_repair_or_substitution_allowed"] is False
    assert record["evidence_identities"] == {
        "contract_sha256": "ce533db97ace7b1d8c1423f48227119699f66e454252b78b9acd80b65a8f0a7a",
        "implementation_proof_sha256": "3ca7ad91893716b751abc60a2e828132d2c8682a4f5491e4bca2e46172ef8919",
        "public_result_bytes": 2286,
        "public_result_sha256": "17dcb54837eff1932bec474051ee1981f8e139146f35f4c5f6a0e0ef2f8de881",
        "rehearsal_receipt_bytes": 531,
        "rehearsal_receipt_sha256": "0e76a4ce898e93b85bdf2602876b6539909acc354c0ac5296d654751f823792e",
        "result_bound_receipt_matches": True,
        "started_at_unix_ns": 1787920282746778000,
    }


def test_fs2_result_records_runtime_failure_and_passed_resource_gates() -> None:
    record = _record()
    completion = record["completion"]
    resources = record["resource_measurement"]
    gates = record["gate_results"]

    assert completion == {
        "expected_replay_children": 2,
        "completed_replay_children": 1,
        "canonical_replay_equivalent": None,
        "canonical_replay_sha256": None,
        "distinct_replay_worker_PIDs": None,
        "observed_generated_counters": None,
    }
    assert resources["runtime_seconds"] == 180.05074683297426
    assert resources["runtime_cap_seconds"] == 180
    assert resources["runtime_overage_seconds"] == 0.05074683297426
    assert resources["peak_process_tree_RSS_bytes"] == 305119232
    assert resources["peak_process_tree_RSS_bytes"] < resources[
        "peak_process_tree_RSS_cap_bytes"
    ]
    assert resources["mandatory_process_monitor_samples"] == 1510
    assert resources["reservation_delta_bytes"] == 537919488
    assert resources["retained_generated_payload_bytes"] == 0
    assert gates == {
        "runtime_at_or_below_cap": False,
        "two_children_completed": False,
        "canonical_equivalence_available": False,
        "RSS_within_cap": True,
        "monitor_samples_nonzero": True,
        "free_space_preflight_passed": True,
        "free_space_after_reservation_passed": True,
        "reservation_delta_exact": True,
        "temporary_cleanup_passed": True,
        "public_output_within_cap": True,
    }


def test_fs2_result_preserves_zero_operations_and_claim_boundary() -> None:
    record = _record()

    assert all(value == 0 for value in record["measured_zero_counters"].values())
    assert record["unavailable_or_unmeasured"] == [
        "canonical_replay_equivalence",
        "canonical_replay_sha256",
        "distinct_replay_worker_PIDs",
        "observed_generated_counters",
        "end_to_end_device_latency",
    ]
    assert record["active_Tier_C_gate"] == {
        "gate_id": "DREYER-C5R-1-HL",
        "changed": False,
        "all_authority_flags_false": True,
    }
    assert not any(record["claim_boundary"].values())


def test_current_frontier_routes_to_consumed_fs2_runtime_result() -> None:
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    communication = frontier["parallel_tier_A_communication_program"][
        "source_identity_preregistration"
    ]["prospective_synchronized_cohort_preregistration"]
    result = communication["generated_qualification_registration"][
        "full_scale_two_child_rehearsal"
    ]

    assert result["status"] == "consumed_FS2_PARK_resource_or_monitor_failure_no_rerun"
    assert result["route"] == "FS2_PARK"
    assert result["completed_replay_children"] == 1
    assert result["expected_replay_children"] == 2
    assert result["closeout_commit"] == "a654541621f2824906d288313d457636844074da"
    assert result["closeout_CI_run_id"] == 33171818869
    assert result["closeout_on_GitHub_main"] is True
    assert result["retry_rerun_resume_repair_or_substitution_allowed"] is False
    assert communication["generated_qualification_next"] is False
    assert communication["generated_runtime_successor_design_next"] is True
