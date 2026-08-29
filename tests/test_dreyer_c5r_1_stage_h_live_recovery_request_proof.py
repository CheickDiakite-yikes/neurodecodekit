import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_request_proof.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_REQUEST_PROOF_CLOSEOUT.md"
)


def _proof() -> dict:
    return json.loads(PROOF.read_text(encoding="utf-8"))


def test_proof_binds_exact_green_request_and_artifacts() -> None:
    proof = _proof()
    green = proof["green_request"]
    rows = proof["bound_request_artifacts"]
    commit = green["commit"]

    assert green == {
        "commit": "0152fa5417f85c54d8c022634e73bee69bc8ef70",
        "CI_run_id": 33233829570,
        "base_python_job_id": 99051201520,
        "optional_neuro_readers_job_id": 99051201612,
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
        "bytes": 109850,
        "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def test_proof_performs_no_implementation_execution_or_private_operation() -> None:
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


def test_proof_preserves_fresh_decision_and_HL2_barriers() -> None:
    boundary = _proof()["activation_boundary"]

    assert boundary["proof_closeout_remotely_green_now"] is False
    assert boundary["fresh_packet_bound_maintainer_words_required"] is True
    assert boundary["predating_short_form_may_activate"] is False
    assert boundary["successor_implementation_authorized_by_closeout"] is False
    assert boundary["successor_qualification_authorized_by_closeout"] is False
    assert boundary["separate_generated_qualification_activation_required"] is True
    assert boundary["HL2_authority"] is False
    assert boundary["real_EDF_authority"] is False


def test_document_separates_engineering_from_science() -> None:
    proof = _proof()
    text = DOCUMENT.read_text(encoding="utf-8")

    assert not any(proof["claim_boundary"].values())
    assert "Engineering capability added:" in text
    assert "Scientific claim not established:" in text
    assert "No earlier instruction may be" in text
