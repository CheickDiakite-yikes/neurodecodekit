import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_qualification_decision.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_QUALIFICATION_DECISION.md"
)


def _decision() -> dict:
    return json.loads(DECISION.read_text(encoding="utf-8"))


def test_actual_short_form_is_preserved_without_scope_expansion() -> None:
    decision = _decision()
    words = "continue"

    assert decision["maintainer_words"] == words
    assert decision["maintainer_words_utf8_bytes"] == len(words.encode())
    assert decision["maintainer_words_sha256"] == hashlib.sha256(words.encode()).hexdigest()
    user = decision["user_authorization"]
    assert user["actual_message_preserved_verbatim"] is True
    assert user["single_named_packet_before_message"] == "DREYER-C5R-1-HL1R1-QA0"
    assert user["long_form_sentence_claimed_as_user_utterance"] is False
    assert user["substantive_registered_scope_unchanged"] is True
    assert user["scope_expansion_by_inference"] is False
    assert DOCUMENT.read_text(encoding="utf-8").count("> continue") == 1


def test_exact_green_request_proof_is_bound() -> None:
    proof = _decision()["green_request_proof"]

    assert proof["commit"] == "d1c003f303083d23685da858bca069397b1f9c58"
    assert proof["CI_run_id"] == 33_250_971_717
    assert proof["base_python_job_id"] == 99_096_464_718
    assert proof["optional_neuro_readers_job_id"] == 99_096_464_770
    assert proof["both_required_jobs_green"] is True
    assert proof["on_GitHub_main"] is True
    assert proof["fresh_verification_calls"] == 1


def test_bound_artifacts_match_green_proof_commit() -> None:
    decision = _decision()
    rows = decision["bound_artifacts"]
    commit = decision["green_request_proof"]["commit"]

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
    assert decision["bound_artifact_summary"] == {
        "count": 6,
        "bytes": sum(row["bytes"] for row in rows),
        "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def test_authority_is_generated_only_and_ordered() -> None:
    authorization = _decision()["authorization_after_decision_green"]

    assert authorization["implement_additive_generated_qualification_coordinator"] is True
    assert authorization["run_generated_coordinator_unit_qualification"] is True
    assert (
        authorization[
            "run_one_registered_generated_qualification_after_coordinator_remote_green"
        ]
        is True
    )
    assert authorization["registered_qualification_attempts_maximum"] == 1
    assert authorization["expose_real_path_URL_network_or_HL2_command"] is False
    assert authorization["create_HL2_activation"] is False
    for key in (
        "make_real_HTTP_request",
        "open_real_or_private_path",
        "write_or_read_real_EDF",
        "read_header_annotation_signal_target_or_label",
        "access_model_or_checkpoint",
        "train_or_infer",
        "create_prediction_deliver_target_or_score",
        "use_language_model_or_provider",
        "use_stream_device_or_hardware",
        "touch_other_project",
        "release_or_publish",
        "upgrade_scientific_claim",
    ):
        assert authorization[key] is False, key


def test_decision_records_zero_qualification_or_irreversible_operations() -> None:
    operations = _decision()["decision_only_operations"]

    assert operations["GitHub_CI_verification_calls"] == 1
    assert operations["end_to_end_latency_measured"] is False
    assert all(
        value == 0
        for key, value in operations.items()
        if key not in {"GitHub_CI_verification_calls", "end_to_end_latency_measured"}
    )


def test_next_barriers_and_claim_boundary_remain_closed() -> None:
    decision = _decision()
    barriers = decision["next_barriers"]

    assert barriers["this_decision_commit_push_and_remote_green_required_before_coordinator"]
    assert barriers["exact_coordinator_commit_push_and_remote_green_required_before_execution"]
    assert barriers["registered_qualification_attempts_maximum_after_coordinator_green"] == 1
    assert barriers["HL2_authority"] is False
    assert barriers["real_EDF_authority"] is False
    assert all(value is False for value in decision["claim_boundary"].values())
