import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_qualification_request_proof.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_QUALIFICATION_REQUEST_PROOF_CLOSEOUT.md"
)


def _proof() -> dict:
    return json.loads(PROOF.read_text(encoding="utf-8"))


def test_proof_binds_exact_green_all_false_request() -> None:
    proof = _proof()
    green = proof["green_request"]
    rows = proof["bound_request_artifacts"]
    commit = green["commit"]

    assert green == {
        "commit": "0213e7050dd845de16b5f1abac4573f30b534452",
        "CI_run_id": 33250382778,
        "base_python_job_id": 99094941511,
        "optional_neuro_readers_job_id": 99094941619,
        "both_required_jobs_green": True,
        "on_GitHub_main": True,
    }
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
    assert proof["artifact_summary"] == {
        "count": 3,
        "bytes": sum(row["bytes"] for row in rows),
        "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def test_proof_repeats_no_qualification_or_real_operation() -> None:
    operations = _proof()["proof_operations"]

    assert operations["committed_public_artifact_reads"] == 3
    assert operations["committed_public_artifact_hashes"] == 3
    assert operations["Git_blob_proof_reads"] == 3
    assert all(
        value == 0
        for key, value in operations.items()
        if key
        not in {
            "committed_public_artifact_reads",
            "committed_public_artifact_hashes",
            "Git_blob_proof_reads",
        }
    )


def test_fresh_decision_and_real_data_boundaries_remain_closed() -> None:
    boundary = _proof()["decision_boundary"]

    assert boundary["proof_closeout_remotely_green_now"] is False
    assert boundary["fresh_packet_bound_maintainer_words_required_after_green"] is True
    assert boundary["predating_short_form_may_activate"] is False
    assert boundary["qualification_coordinator_authorized_by_proof"] is False
    assert boundary["registered_qualification_authorized_by_proof"] is False
    assert boundary["HL2_authority"] is False
    assert boundary["real_EDF_authority"] is False
    assert all(value is False for value in _proof()["claim_boundary"].values())
    text = DOCUMENT.read_text(encoding="utf-8")
    assert "Scientific claim not established" in text
    assert "no real EEG" in text
