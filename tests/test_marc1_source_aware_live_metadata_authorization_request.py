import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc1_source_aware_live_metadata_authorization_request.v0.json"
)


def load_request() -> dict:
    return json.loads(REQUEST_PATH.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_request_is_all_false_and_waits_for_a_fresh_decision() -> None:
    request = load_request()
    assert request["schema_name"] == (
        "neurodecodekit.marc1_source_aware_live_metadata_authorization_request"
    )
    assert request["schema_version"] == "0.1.0"
    assert request["lane_id"] == "MARC1-SA1A"
    assert request["status"] == "awaiting_new_packet_bound_maintainer_decision"
    assert request["authorized_now"] is False
    assert request["user_decision"] is None
    assert request["authorization_record_commit"] is None


def test_green_source_aware_result_is_the_exact_eligibility_proof() -> None:
    proof = load_request()["green_source_aware_result"]
    assert proof["commit"] == "094b6cb7358c5d44b6d8c2ce7a087e16ec4e17c3"
    assert proof["CI_run_id"] == 31_620_515_340
    assert proof["base_python_job_id"] == 94_193_898_391
    assert proof["optional_neuro_job_id"] == 94_193_898_482
    assert proof["both_required_jobs_green"] is True
    assert proof["route"] == "MARC1SA-G1"
    assert proof["registered_closeout_consumed"] is True
    assert proof["retry_or_rerun_available"] is False


def test_consumed_prior_live_lane_cannot_be_reopened_or_inferred() -> None:
    consumed = load_request()["consumed_prior_live_result"]
    assert consumed["route"] == "MARC1LM-F04"
    assert consumed["accepted_body_bytes"] == 15_652
    assert consumed["actual_inventory_predicate_retained"] is False
    assert consumed["actual_rows_retained"] is False
    assert consumed["retry_or_rerun_available"] is False
    assert consumed["old_private_root_or_wrapper_may_be_opened"] is False


def test_every_bound_green_artifact_matches_size_and_hash() -> None:
    for binding in load_request()["target_artifacts"].values():
        path = ROOT / binding["path"]
        assert path.stat().st_size == binding["bytes"]
        assert sha256_file(path) == binding["sha256"]


def test_exact_single_metadata_body_scope_is_payload_free() -> None:
    scope = load_request()["requested_scope"]
    source = scope["public_metadata"]
    assert (source["record_id"], source["version"]) == (29_666_735, 3)
    assert source["query"] == "page=1&page_size=1000"
    assert source["request_attempts"] == 1
    assert source["redirects"] == 0
    assert source["accepted_body_count"] == 1
    assert source["accepted_body_cap_bytes"] == 2 * 1024**2
    assert (source["payload_requests"], source["payload_bytes"]) == (0, 0)
    assert scope["local_private_input_paths"] == 0
    assert scope["model_runs"] == scope["training_runs"] == 0


def test_historical_identity_is_comparison_not_coercion() -> None:
    historical = load_request()["requested_scope"]["historical_comparison"]
    assert historical["file_rows"] == 55
    assert historical["participant_archives"] == 45
    assert historical["supplementary_rows"] == 10
    assert historical["declared_record_bytes"] == 3_683_416_050
    assert historical["selected_subjects_if_all_historical_predicates_match"] == 12
    assert historical["fit_runs_if_eligible"] == [1, 2, 3, 4, 5, 6]
    assert historical["held_out_runs_if_eligible"] == [7, 8]
    assert historical["historical_difference_may_be_coerced_or_ignored"] is False


def test_source_schema_keeps_md5_optional_and_targets_forbidden() -> None:
    schema = load_request()["source_schema_contract"]
    assert schema["required_public_core_fields"] == [
        "id",
        "name",
        "size",
        "is_link_only",
        "download_url",
    ]
    assert schema["known_optional_MD5_fields"] == ["supplied_md5", "computed_md5"]
    assert schema["optional_MD5_may_be_required_for_source_core_acceptance"] is False
    assert schema["present_MD5_must_be_lowercase_hex_and_agree_when_paired"] is True
    assert schema["unknown_non_target_extension_blocks_selection"] is True
    assert schema["target_like_field_anywhere_refused"] is True
    assert schema["provider_MD5_substitutes_for_payload_SHA256"] is False


def test_route_policy_blocks_selection_on_drift_or_unknown_extensions() -> None:
    routes = load_request()["route_contract"]
    for route in ("MARC1SA-R1", "MARC1SA-R2"):
        assert routes[route]["wrapper_route"] == "MARC1SAL-R1"
        assert routes[route]["selection_available"] is True
        assert routes[route]["payload_available"] is False
    for route in ("MARC1SA-R3", "MARC1SA-R4"):
        assert routes[route]["wrapper_route"] == "MARC1SAL-R2"
        assert routes[route]["selection_available"] is False
        assert routes[route]["payload_available"] is False
    assert len(routes["failure_routes"]) == 5
    assert routes["every_result_or_failure_consumes_lane"] is True


def test_wrapper_is_additive_ordered_and_cannot_import_consumed_live_code() -> None:
    request = load_request()
    order = request["requested_access_order"]
    assert order.index("authorization_decision_commit_pushed_and_both_CI_jobs_green") < (
        order.index("additive_generated_fixture_and_mock_wrapper_implementation")
    )
    assert order.index("exact_wrapper_commit_pushed_and_both_CI_jobs_green") < (
        order.index("one_exact_no_retry_source_metadata_GET")
    )
    wrapper = request["future_live_wrapper_contract"]
    assert wrapper["may_import_green_source_aware_attestor"] is True
    assert wrapper["may_import_call_modify_or_expose_consumed_live_executor"] is False
    assert wrapper["generated_and_mocked_only_before_green_commit"] is True
    assert wrapper["real_endpoint_available_before_green_commit"] is False
    assert wrapper["payload_interface_exists"] is False
    assert wrapper["old_private_invocation_root_forbidden"] is True


def test_transport_is_one_attempt_bounded_uncoded_and_no_retry() -> None:
    transport = load_request()["transport_contract"]
    assert transport["HTTP_request_attempt_cap"] == 1
    assert transport["redirects"] == 0
    assert transport["response_cap_bytes"] == 2 * 1024**2
    assert transport["absent_Content_Encoding_accepted"] is True
    assert transport["one_case_insensitive_identity_Content_Encoding_accepted"] is True
    assert transport["other_present_Content_Encoding_refused"] is True
    assert transport["duplicate_or_list_Content_Encoding_refused"] is True
    assert transport["decoding_or_decompression_operations"] == 0
    assert (transport["retries"], transport["reruns"]) == (0, 0)
    assert transport["raw_response_SHA256_is_semantic_or_payload_identity"] is False


def test_output_privacy_and_computer_caps_are_strict() -> None:
    request = load_request()
    output = request["output_contract"]
    assert output["new_root_must_be_absent"] is True
    assert output["output_capability_acquired_before_repository_or_network_work"] is True
    assert output["private_manifest_mode"] == "0600"
    assert output["public_report_individual_rows_IDs_names_URLs_MD5_or_subjects"] is False
    assert output["unknown_extension_values_persisted_private_or_public"] is False
    assert output["preexisting_path_modified_moved_renamed_or_deleted"] is False
    assert output["every_route_stops_before_archive_or_payload"] is True
    caps = request["resource_caps"]
    assert caps["minimum_free_disk_bytes"] == 10 * 1024**3
    assert (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]) == (1, 1, 1)
    assert caps["real_invocation_wall_time_seconds"] == 30
    assert caps["peak_RSS_bytes"] == 256 * 1024**2
    assert caps["incremental_disk_cap_bytes"] == 4 * 1024**2
    assert caps["base_dependency_delta"] == 0


def test_every_current_authorization_and_operation_is_false_or_zero() -> None:
    request = load_request()
    authorization = request["authorization"]
    assert authorization["separate_authorization_decision_required"] is True
    assert authorization["short_form_may_bind_after_request_is_remotely_green"] is True
    for key, value in authorization.items():
        if key.endswith("_authorized_now") or key in {
            "packet_bound_decision_received",
            "current_or_prior_message_is_retroactive_authorization",
            "general_research_autonomy_is_exact_Tier_C_authorization",
        }:
            assert value is False, key
    assert all(value == 0 for value in request["current_access_counters"].values())


def test_next_gate_requires_green_request_and_fresh_packet_bound_words() -> None:
    request = load_request()
    short = request["packet_bound_short_form"]
    assert short["eligible_only_after_request_commit_is_pushed_and_both_CI_jobs_are_green"]
    assert short["eligible_only_if_sole_active_Tier_C_packet"]
    assert short["assistant_identifies_commit_CI_scope_and_boundary_first"]
    assert short["fresh_message_required_after_identification"]
    assert short["long_scope_may_be_fabricated_as_user_words"] is False
    gate = request["next_gate"]
    assert gate["request_commit_push_and_both_remote_CI_jobs_green_required"] is True
    assert gate["fresh_packet_bound_user_decision_received"] is False
    assert gate["generated_or_mocked_live_wrapper_implementation_may_begin"] is False
    assert gate["real_metadata_request_may_begin"] is False
    assert gate["archive_or_payload_acquisition_may_begin"] is False


def test_human_packet_and_claim_boundary_preserve_the_same_path() -> None:
    packet = (
        ROOT / "docs" / "MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_PACKET.md"
    ).read_text(encoding="utf-8")
    assert "This packet authorizes nothing by itself." in packet
    assert "Same Path, Not A Pivot" in packet
    assert "Fresh Decision Rule" in packet
    assert "Engineering capability requested:" in packet
    assert "Scientific claim not established by this request:" in packet
    claim = load_request()["claim_boundary"]
    assert claim["same_thought_to_text_path"] is True
    assert claim["is_pivot"] is False
    assert claim["movement_metadata_is_language_evidence"] is False
    assert claim["scientific_claim_established_by_request"] is False
    assert "no neural effect" in claim["scientific_claim_not_established_by_request"]
