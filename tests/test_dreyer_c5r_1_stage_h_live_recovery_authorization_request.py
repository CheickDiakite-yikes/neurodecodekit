import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_authorization_request.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_AUTHORIZATION_PACKET.md"
)


def _request() -> dict:
    return json.loads(REQUEST.read_text(encoding="utf-8"))


def test_request_binds_exact_green_failure_proof() -> None:
    request = _request()

    assert request["packet_id"] == "DREYER-C5R-1-HL1R1"
    assert request["status"] == "request_only_all_authority_false"
    assert request["green_failure_proof"] == {
        "commit": "a70fda0a808751c6057ed07117b7d22ee715a273",
        "CI_run_id": 33233017769,
        "base_python_job_id": 99049010377,
        "optional_neuro_readers_job_id": 99049010221,
        "both_required_jobs_green": True,
        "on_GitHub_main": True,
    }
    predecessor = request["consumed_predecessor"]
    assert predecessor["attempt_id"] == "DREYER-C5R-1-HL1-R0"
    assert predecessor["rerun_repair_resume_or_reinterpretation_allowed"] is False
    assert predecessor["source_must_remain_byte_identical"] is True


def test_request_hash_size_and_git_binds_all_public_inputs() -> None:
    request = _request()
    artifact_set = request["bound_artifact_set"]
    rows = artifact_set["artifacts"]
    commit = request["green_failure_proof"]["commit"]

    assert len(rows) == artifact_set["count"] == 14
    assert sum(row["bytes"] for row in rows) == artifact_set["bytes"] == 204302
    for row in rows:
        payload = subprocess.check_output(
            ["git", "show", f"{commit}:{row['path']}"], cwd=ROOT
        )
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]
        blob = subprocess.check_output(
            ["git", "rev-parse", f"{commit}:{row['path']}"], cwd=ROOT, text=True
        ).strip()
        assert blob == row["git_blob"]
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    assert (
        hashlib.sha256(canonical).hexdigest()
        == artifact_set["canonical_artifact_set_sha256"]
    )


def test_transaction_boundary_and_exact_case_matrix_are_frozen() -> None:
    request = _request()
    successor = request["requested_successor"]
    qualification = request["mandatory_generated_qualification"]

    assert successor["failed_source_mutations_allowed"] is False
    assert successor["usable_real_command_allowed"] is False
    assert successor["transaction_boundary_begins_immediately_after_marker"] is True
    assert successor["transaction_boundary_precedes_staging_opener_and_request"] is True
    assert successor["aggregate_H0_required_when_public_destination_available"] is True
    assert qualification["registered_attempts_maximum"] == 1
    assert qualification["ordered_successor_refusal_count"] == 43
    assert len(qualification["ordered_successor_refusal_cases"]) == 43
    assert "opener_factory_refusal" in qualification["ordered_successor_refusal_cases"]
    assert qualification["post_marker_opener_failure_H0_required"] is True
    assert qualification["no_staging_debris_after_applicable_post_marker_cases"] is True


def test_resources_authority_and_claims_remain_closed() -> None:
    request = _request()
    resources = request["resource_envelope"]

    assert resources["CPU_threads"] == 1
    assert resources["runtime_seconds_maximum"] == 30
    assert resources["peak_process_tree_RSS_bytes_maximum"] == 256 << 20
    assert resources["generated_input_plus_output_bytes_maximum"] == 8 << 20
    assert resources["incremental_temporary_disk_bytes_maximum"] == 16 << 20
    assert resources["HTTP_requests"] == 0
    assert resources["network_bytes"] == 0
    assert all(value is False for value in request["authority"].values())
    assert all(value == 0 for value in request["operation_counters_at_request"].values())
    assert not any(request["claim_boundary"].values())


def test_document_explains_request_only_short_form_boundary() -> None:
    text = DOCUMENT.read_text(encoding="utf-8")

    assert "every authority flag remains false" in text
    assert "No short-form instruction predating this packet may activate" in text
    assert "Engineering capability requested:" in text
    assert "Scientific claim not established:" in text
