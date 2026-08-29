import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_generated_qualification_proof.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_GENERATED_QUALIFICATION_PROOF_CLOSEOUT.md"
)


def _record() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_proof_binds_exact_green_rejected_result_and_artifacts() -> None:
    record = _record()
    green = record["green_rejected_result"]
    rows = record["bound_public_artifacts"]

    assert green == {
        "commit": "24a5da2973ef65fa05f5ea7b1d1389370534ad23",
        "CI_run_id": 33232453046,
        "base_python_job_id": 99047501588,
        "optional_neuro_readers_job_id": 99047501456,
        "both_required_jobs_green": True,
        "on_GitHub_main": True,
        "working_branch_matches_main": True,
    }
    for row in rows:
        payload = (ROOT / row["path"]).read_bytes()
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]
        blob = subprocess.check_output(
            ["git", "hash-object", row["path"]], cwd=ROOT, text=True
        ).strip()
        assert blob == row["git_blob"]

    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    assert record["artifact_summary"] == {
        "count": 9,
        "bytes": 182883,
        "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def test_proof_repeats_no_execution_or_private_operation() -> None:
    record = _record()
    operations = record["proof_operations"]

    assert operations["committed_public_artifact_reads"] == 9
    assert operations["committed_public_artifact_hashes"] == 9
    assert operations["Git_blob_proof_reads"] == 9
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


def test_proof_preserves_consumed_failure_and_blocks_HL2() -> None:
    routing = _record()["routing"]

    assert routing["HL1_R0_consumed"] is True
    assert routing["HL1_R0_accepted"] is False
    assert routing["HL1_R0_rerun_repair_resume_or_reinterpretation_allowed"] is False
    assert routing["HL2_authority"] is False
    assert routing["HL2_real_invocation_consumed"] is False
    assert routing["successor_packet_active"] is False
    assert routing["fresh_packet_bound_maintainer_decision_required"] is True
    assert routing["proof_closeout_authorizes_successor_implementation_or_execution"] is False


def test_proof_document_separates_engineering_from_science() -> None:
    record = _record()
    text = DOCUMENT.read_text(encoding="utf-8")

    assert not any(record["claim_boundary"].values())
    assert "Engineering capability added:" in text
    assert "Scientific claim not established:" in text
    assert "did not read the ignored raw receipt" in text
    assert "H-L2 remains blocked" in text
