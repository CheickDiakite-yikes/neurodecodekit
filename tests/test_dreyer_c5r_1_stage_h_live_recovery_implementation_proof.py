import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_implementation_proof.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_IMPLEMENTATION_PROOF_CLOSEOUT.md"
)


def _proof() -> dict:
    return json.loads(PROOF.read_text(encoding="utf-8"))


def test_proof_binds_exact_green_implementation_and_artifacts() -> None:
    proof = _proof()
    green = proof["green_implementation"]
    rows = proof["bound_implementation_artifacts"]
    commit = green["commit"]

    assert green == {
        "commit": "6a0bc7749dd6c36b4d8db019cc6e78acf653c83d",
        "CI_run_id": 33249178006,
        "base_python_job_id": 99091760720,
        "optional_neuro_readers_job_id": 99091760774,
        "both_required_jobs_green": True,
        "on_GitHub_main": True,
        "working_branch_matches_main": True,
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
        "count": 6,
        "bytes": sum(row["bytes"] for row in rows),
        "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def test_proof_repeats_no_development_qualification_or_real_operation() -> None:
    operations = _proof()["proof_operations"]

    assert operations["committed_public_artifact_reads"] == 6
    assert operations["committed_public_artifact_hashes"] == 6
    assert operations["Git_blob_proof_reads"] == 6
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


def test_qualification_and_real_data_boundaries_remain_closed() -> None:
    boundary = _proof()["activation_boundary"]

    assert boundary["proof_closeout_remotely_green_now"] is False
    assert boundary["all_false_qualification_activation_request_may_follow_after_green"] is True
    assert boundary["registered_qualification_authorized_by_proof"] is False
    assert boundary["fresh_packet_bound_qualification_decision_required"] is True
    assert boundary["HL2_authority"] is False
    assert boundary["real_EDF_authority"] is False
    assert all(value is False for value in _proof()["claim_boundary"].values())
    text = DOCUMENT.read_text(encoding="utf-8")
    assert "Scientific claim not established" in text
    assert "no real EEG" in text
