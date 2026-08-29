import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_implementation.v0.json"
)
DOCUMENT = ROOT / "docs" / "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_IMPLEMENTATION.md"


def _record() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_implementation_binds_exact_green_decision() -> None:
    green = _record()["green_decision"]

    assert green == {
        "commit": "eaff077fc14b10886a6c26f45318ae649765e76d",
        "CI_run_id": 33247816266,
        "base_python_job_id": 99088241281,
        "optional_neuro_readers_job_id": 99088241372,
        "both_required_jobs_green": True,
        "on_GitHub_main": True,
    }


def test_tracked_implementation_artifacts_match_bytes_hashes_and_blobs() -> None:
    for row in _record()["tracked_implementation_artifacts"]:
        path = ROOT / row["path"]
        payload = path.read_bytes()
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]
        blob = subprocess.check_output(
            ["git", "hash-object", str(path)], cwd=ROOT, text=True
        ).strip()
        assert blob == row["git_blob"]


def test_consumed_predecessor_is_byte_identical() -> None:
    for row in _record()["frozen_consumed_predecessor_artifacts"]:
        assert hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row[
            "sha256"
        ]


def test_development_matrix_is_complete_but_not_official_qualification() -> None:
    verification = _record()["development_verification"]

    assert verification["deterministic_valid_H1_replays"] == 2
    assert verification["ordered_successor_failure_identities"] == 43
    assert verification["ordered_successor_failure_identities_passed"] == 43
    assert verification["focused_tests"] == 9
    assert verification["focused_subtests"] == 43
    assert verification["registered_qualification_runs"] == 0
    assert verification["official_qualification_marker_writes"] == 0
    assert verification["valid_case_input_marker_output_bytes"] < 8 * 1024**2
    assert verification["valid_case_private_allocated_bytes"] < 16 * 1024**2
    assert verification["focused_suite_peak_child_RSS_bytes"] < 256 * 1024**2


def test_authority_and_scientific_claims_remain_closed() -> None:
    record = _record()
    contract = record["implementation_contract"]
    barriers = record["next_barriers"]

    assert contract["usable_real_command_exposed"] is False
    assert contract["qualification_command_exposed"] is False
    assert barriers["registered_qualification_runs_authorized_now"] == 0
    assert barriers["separate_all_false_qualification_activation_required"] is True
    assert barriers["HL2_authority"] is False
    assert barriers["real_EDF_authority"] is False
    assert all(value == 0 for value in record["implementation_access_counters"].values())
    assert all(value is False for value in record["claim_boundary"].values())
    document = DOCUMENT.read_text(encoding="utf-8")
    assert "Scientific claim not established" in document
    assert "no real EEG" in document
