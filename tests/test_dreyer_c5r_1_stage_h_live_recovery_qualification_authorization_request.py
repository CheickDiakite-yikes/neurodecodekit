import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_qualification_authorization_request.v0.json"
)
ORIGINAL = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_authorization_request.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_QUALIFICATION_AUTHORIZATION_PACKET.md"
)


def _request() -> dict:
    return json.loads(REQUEST.read_text(encoding="utf-8"))


def test_request_binds_exact_green_implementation_proof() -> None:
    request = _request()
    green = request["green_implementation_proof"]
    rows = request["bound_proof_artifacts"]
    commit = green["commit"]

    assert green["CI_run_id"] == 33249903090
    assert green["base_python_job_id"] == 99093675279
    assert green["optional_neuro_readers_job_id"] == 99093675204
    assert green["both_required_jobs_green"] is True
    assert green["on_GitHub_main"] is True
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
    assert request["artifact_summary"] == {
        "count": 3,
        "bytes": sum(row["bytes"] for row in rows),
        "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def test_request_preserves_exact_qualification_matrix_and_caps() -> None:
    request = _request()
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    qualification = request["requested_qualification"]

    assert qualification["ordered_successor_refusal_cases"] == original[
        "mandatory_generated_qualification"
    ]["ordered_successor_refusal_cases"]
    assert qualification["ordered_successor_refusal_count"] == 43
    assert qualification["registered_attempts_maximum"] == 1
    assert qualification["attempt_consumed_on_pass_or_failure"] is True
    assert qualification["green_recovery_implementation_mutation_allowed"] is False
    assert qualification["real_path_URL_network_or_HL2_command_allowed"] is False
    assert request["resource_envelope"] == original["resource_envelope"]


def test_request_grants_no_authority_and_changes_no_claim() -> None:
    request = _request()

    assert all(value is False for value in request["authority"].values())
    assert all(value == 0 for value in request["operation_counters_at_request"].values())
    assert request["decision_boundary"]["predating_short_form_may_activate"] is False
    assert request["decision_boundary"]["HL2_remains_separately_closed"] is True
    assert all(value is False for value in request["claim_boundary"].values())
    text = DOCUMENT.read_text(encoding="utf-8")
    assert "every authority flag remains false" in text
    assert "Scientific claim not established" in text
