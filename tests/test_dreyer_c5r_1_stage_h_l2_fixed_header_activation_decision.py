import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_l2_fixed_header_activation_decision.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_L2_FIXED_HEADER_ACTIVATION_DECISION.md"
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
    assert user["single_named_packet_before_message"] == "DREYER-C5R-1-HL2-A0"
    assert user["long_form_sentence_claimed_as_user_utterance"] is False
    assert user["substantive_registered_scope_unchanged"] is True
    assert user["scope_expansion_by_inference"] is False
    assert DOCUMENT.read_text(encoding="utf-8").count("> continue") == 1


def test_exact_green_request_and_proof_are_bound() -> None:
    decision = _decision()
    request = decision["green_request"]
    proof = decision["green_request_proof"]

    assert request["commit"] == "a97fc191106e5fe42859d871d78e59930bef79ac"
    assert request["CI_run_id"] == 33_255_920_346
    assert request["both_required_jobs_green"] is True
    assert proof["commit"] == "036a9ec7e78b460d464c3349151ddb0e35914d87"
    assert proof["CI_run_id"] == 33_257_159_816
    assert proof["base_python_job_id"] == 99_112_795_545
    assert proof["optional_neuro_readers_job_id"] == 99_112_795_525
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
        "bytes": 27_477,
        "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def test_authority_is_exact_ordered_and_narrow() -> None:
    authorization = _decision()["authorization_after_decision_green"]

    assert authorization["implement_additive_standard_library_HL2_execution_adapter"]
    assert authorization["run_generated_adapter_wiring_and_refusal_tests"]
    assert authorization["implementation_commit_push_and_both_jobs_green_required"]
    assert authorization[
        "create_one_no_authority_activation_record_after_implementation_green"
    ]
    assert authorization["activation_commit_push_and_both_jobs_green_required"]
    assert authorization["run_one_registered_HL2_invocation_after_activation_green"]
    assert authorization["write_durable_consumed_marker_before_opener_or_request"]
    assert authorization["registered_HL2_invocations_maximum"] == 1
    assert authorization["real_HTTP_GET_requests_exact"] == 1
    assert authorization["successful_payload_body_bytes_exact"] == 14_805_604
    assert authorization["fixed_EDF_header_semantic_parses_maximum"] == 1
    assert authorization["modify_frozen_predecessor_artifacts"] is False
    for key in (
        "open_or_parse_annotations",
        "read_signal_samples_targets_labels_trials_events_or_individual_outcomes",
        "request_remaining_119_EDFs",
        "create_split_epoch_feature_cache_or_derivative",
        "access_model_or_checkpoint",
        "train_infer_predict_deliver_target_or_score",
        "use_language_model_or_provider",
        "use_stream_device_or_hardware",
        "touch_other_project",
        "release_or_publish",
        "upgrade_scientific_claim",
        "retry_rerun_resume_repair_substitute_or_post_result_amend",
    ):
        assert authorization[key] is False, key


def test_exact_member_transport_and_resource_caps_are_frozen() -> None:
    decision = _decision()
    member = decision["exact_member"]
    transport = decision["transport_contract"]
    caps = decision["resource_envelope"]

    assert member["path"] == (
        "sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf"
    )
    assert member["bytes"] == 14_805_604
    assert member["sha256"] == (
        "a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185"
    )
    assert transport["standard_library_only"] is True
    assert transport["Accept_Encoding"] == "identity"
    for key in ("proxies", "redirects", "retries", "ranges", "resume"):
        assert transport[key] == 0, key
    assert caps["CPU_threads"] == 1
    assert caps["workers"] == 1
    assert caps["runtime_seconds_maximum"] == 300
    assert caps["peak_process_tree_RSS_bytes_maximum"] == 256 * 1024 * 1024
    assert caps["incremental_disk_bytes_maximum"] == 32 * 1024 * 1024
    assert caps["free_disk_bytes_minimum"] == 10 * 1024 * 1024 * 1024


def test_decision_performed_no_authority_bearing_operation_or_claim() -> None:
    decision = _decision()
    operations = decision["decision_only_operations"]

    assert operations["GitHub_CI_verification_calls"] == 1
    assert operations["end_to_end_latency_measured"] is False
    assert all(
        value == 0
        for key, value in operations.items()
        if key not in {"GitHub_CI_verification_calls", "end_to_end_latency_measured"}
    )
    barriers = decision["next_barriers"]
    assert barriers["this_decision_commit_push_and_remote_green_required_before_adapter"]
    assert barriers["exact_adapter_commit_push_and_remote_green_required_before_activation"]
    assert barriers["activation_commit_push_and_remote_green_required_before_live_invocation"]
    assert barriers["HL2_authority_before_all_barriers"] is False
    assert barriers["real_EDF_authority_before_all_barriers"] is False
    assert all(value is False for value in decision["claim_boundary"].values())
