from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_dual_verification as FS3
from neurodecodekit.experiments import comm_p0_generated_score_only as score_only
from neurodecodekit.experiments import comm_p0_generated_verifier_worker as verifier


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_RECORD = ROOT / "registries" / (
    "communication_eeg_prospective_generated_single_execution_"
    "dual_verification_implementation.v0.json"
)
IMPLEMENTATION_DOCUMENT = ROOT / "docs" / (
    "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_SINGLE_EXECUTION_"
    "DUAL_VERIFICATION_IMPLEMENTATION.md"
)


def test_exact_FS3_contract_and_plan_remain_closed() -> None:
    contract = FS3.load_contract(ROOT)
    plan = FS3.plan(ROOT)

    assert contract["gate_id"] == FS3.GATE_ID
    assert contract["run_id"] == FS3.RUN_ID
    assert plan["registration_remotely_green_on_GitHub_main"] is True
    assert plan["implementation_proof_present"] is False
    assert plan["registration_authorizes_execution_now"] is False
    assert plan["official_qualification_activated"] is False
    assert plan["real_or_private_operations_authorized"] is False
    assert plan["scientific_claim_established"] is False


def test_contract_hash_or_parent_drift_refuses(tmp_path: Path) -> None:
    copied = tmp_path / FS3.CONTRACT_PATH
    copied.parent.mkdir(parents=True)
    copied.write_bytes((ROOT / FS3.CONTRACT_PATH).read_bytes() + b"\n")

    with pytest.raises(core.CommP0GeneratedRefusal, match="parent_hash"):
        FS3.load_contract(tmp_path)


def test_reduced_producer_validation_enforces_schedule() -> None:
    participants = 3
    ledger = {
        **FS3.qualification._expected_model_ledger(participants),
    }
    producer = {
        "ledger": ledger,
        "prediction_inventory": {"rows": 3 * 2 * 128 * 17, "sets": 3 * 2 * 2 * 17},
        "refusal_observations": 70,
        "target_deliveries": 2,
        "scores": 2,
        "post_target_updates": 0,
        "complete_prediction_records_materialized": False,
        "maximum_prediction_rows_buffered": 1,
    }

    FS3._validate_reduced_producer(producer, participants_per_cohort=participants)
    producer["prediction_inventory"]["rows"] -= 1
    with pytest.raises(core.CommP0GeneratedRefusal, match="schedule_or_counter"):
        FS3._validate_reduced_producer(producer, participants_per_cohort=participants)


def test_verifier_capability_surface_is_model_free() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json; "
                "from neurodecodekit.experiments import "
                "comm_p0_generated_verifier_worker as worker; "
                "print(json.dumps(worker._assert_model_free_capability()))"
            ),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    audit = json.loads(result.stdout)

    assert audit["accepts_paths"] is False
    assert audit["fit_or_model_capability"] is False
    assert audit["subprocess_capability"] is False
    assert audit["network_capability"] is False
    assert audit["row_level_output_capability"] is False
    assert audit["preopened_descriptor_only"] is True


def test_implementation_identity_is_target_free_and_bounded() -> None:
    identity = FS3.implementation_identity()

    assert identity["gate_id"] == FS3.GATE_ID
    assert identity["contract_sha256"] == FS3.CONTRACT_SHA256
    assert len(identity["artifacts"]) == 4
    assert identity["full_scale_runs"] == 0
    assert identity["real_or_private_operations"] == 0
    assert identity["scientific_claim_established"] is False
    core.assert_target_free(identity)


def _aggregate() -> dict:
    return {
        "score": {"prediction_quality": {"present_prediction_rows": 64}},
        "prediction_streaming": {"passes": 2},
        "target_delivery_count": 2,
        "score_count": 2,
    }


def _run_mock_verifier(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, mismatch: bool):
    producer = _aggregate()
    producer_path = tmp_path / "producer.json"
    output_path = tmp_path / "verification.json"
    score_path = tmp_path / "score.json"
    producer_path.write_bytes(score_only.canonical_json_bytes(producer))
    output_path.write_bytes(b"")
    score_path.write_bytes(b"")
    monkeypatch.setattr(
        verifier,
        "_assert_model_free_capability",
        lambda: {
            "standard_library_only_except_pure_score_module": True,
            "accepts_paths": False,
            "preopened_descriptor_only": True,
            "fit_or_model_capability": False,
            "subprocess_capability": False,
            "network_capability": False,
            "row_level_output_capability": False,
            "official_qualification_executed": False,
        },
    )
    returned = _aggregate()
    if mismatch:
        returned["score_count"] = 1
    monkeypatch.setattr(verifier.score_worker, "descriptor_fd_main", lambda **_: returned)
    producer_fd = os.open(producer_path, os.O_RDONLY)
    output_fd = os.open(output_path, os.O_WRONLY)
    score_fd = os.open(score_path, os.O_WRONLY)
    try:
        return verifier.descriptor_main(
            contract_fd=-1,
            trial_manifest_fd=-1,
            prediction_stream_fd=-1,
            freeze_attestation_fd=-1,
            target_envelope_fd=-1,
            live_observations_fd=-1,
            hmac_key_fd=-1,
            producer_aggregate_fd=producer_fd,
            verifier_score_output_fd=score_fd,
            verification_output_fd=output_fd,
            input_byte_cap=1024,
            output_byte_cap=4096,
            record_cap=100,
        )
    finally:
        os.close(producer_fd)
        os.close(output_fd)
        os.close(score_fd)


def test_verifier_accepts_exact_aggregate_and_refuses_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = _run_mock_verifier(tmp_path, monkeypatch, mismatch=False)
    assert result["aggregate_scores_exactly_match"] is True
    assert result["prediction_rows"] == 64
    assert result["prediction_sets"] == 1
    assert result["model_fits"] == result["model_inference_runs"] == 0

    second = tmp_path / "mismatch"
    second.mkdir()
    with pytest.raises(score_only.ScoreOnlyRefusal, match="aggregate_score_mismatch"):
        _run_mock_verifier(second, monkeypatch, mismatch=True)


def test_cli_help_and_plan_are_dependency_light() -> None:
    help_result = subprocess.run(
        [sys.executable, "-m", "neurodecodekit.comm_p0_FS3_cli", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "qualify-reduced" in help_result.stdout

    plan_result = subprocess.run(
        [sys.executable, "-m", "neurodecodekit.comm_p0_FS3_cli", "plan"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    value = json.loads(plan_result.stdout)
    assert value["gate_id"] == FS3.GATE_ID
    assert value["registration_authorizes_execution_now"] is False


def test_implementation_record_binds_artifacts_and_measured_qualification() -> None:
    record = json.loads(IMPLEMENTATION_RECORD.read_text(encoding="utf-8"))
    observed_bytes = 0
    for row in record["implementation_artifacts"]:
        payload = (ROOT / row["path"]).read_bytes()
        observed_bytes += len(payload)
        assert row["bytes"] == len(payload)
        assert row["sha256"] == hashlib.sha256(payload).hexdigest()
    assert record["artifact_summary"] == {
        "count": len(record["implementation_artifacts"]),
        "bytes": observed_bytes,
    }
    result = record["reduced_generated_qualification"]
    assert result["isolated_model_replays"] == 2
    assert result["isolated_verifier_replays"] == 2
    assert result["refusal_observations"] == 140
    assert result["prediction_rows_per_replay"] == 13056
    assert result["prediction_sets_per_replay"] == 204
    assert result["retained_generated_payload_bytes"] == 0
    assert record["authority"]["full_scale_FS3_execution_authorized_now"] is False
    assert not any(record["claim_boundary"].values())


def test_implementation_document_separates_engineering_from_science() -> None:
    text = IMPLEMENTATION_DOCUMENT.read_text(encoding="utf-8")

    assert "Engineering capability added:" in text
    assert "Scientific claim not established:" in text
    assert "No full 21-person-per-cohort producer ran here." in text
