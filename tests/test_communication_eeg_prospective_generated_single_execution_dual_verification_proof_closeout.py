import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / (
    "communication_eeg_prospective_generated_single_execution_"
    "dual_verification_proof_closeout.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_SINGLE_EXECUTION_"
    "DUAL_VERIFICATION_PROOF_CLOSEOUT.md"
)


def _record() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_closeout_binds_exact_green_implementation_and_artifacts() -> None:
    record = _record()
    green = record["green_implementation"]
    rows = record["bound_implementation_artifacts"]

    assert green["commit"] == "a3b561b118d606ee009c413d2f2419e976d4bc3d"
    assert green["CI_run_id"] == 33179247000
    assert green["base_python_job_id"] == 98875866699
    assert green["optional_neuro_readers_job_id"] == 98875866417
    assert green["both_required_jobs_green"] is True
    assert green["on_GitHub_main"] is True
    for row in rows:
        payload = (ROOT / row["path"]).read_bytes()
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]
    assert record["artifact_summary"] == {
        "count": 6,
        "bytes": 43587,
        "canonical_artifact_set_sha256": (
            "90515e3be142e99fc92a3b2bf57d28aaee0141f8f956ee06c381048ae7079cbc"
        ),
    }


def test_closeout_repeats_no_execution_and_preserves_authority() -> None:
    record = _record()
    operations = record["proof_operations"]

    assert operations["committed_public_artifact_reads"] == 6
    assert operations["committed_public_artifact_hashes"] == 6
    assert all(
        value == 0
        for key, value in operations.items()
        if key not in {"committed_public_artifact_reads", "committed_public_artifact_hashes"}
    )
    assert record["delayed_effect"]["closeout_commit_remotely_green_now"] is False
    assert record["delayed_effect"]["registered_FS3_attempts_maximum"] == 1
    assert record["delayed_effect"]["retry_rerun_resume_repair_or_substitution_allowed"] is False
    assert not any(record["claim_boundary"].values())
    assert record["active_Tier_C_gate"] == {
        "gate_id": "DREYER-C5R-1-HL",
        "changed": False,
        "all_authority_flags_false": True,
    }


def test_closeout_document_separates_engineering_from_science() -> None:
    text = DOCUMENT.read_text(encoding="utf-8")

    assert "Engineering capability added:" in text
    assert "Scientific claim not established:" in text
    assert "did not rerun" in text
