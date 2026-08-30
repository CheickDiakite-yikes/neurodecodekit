from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries/fresh_motor_source_discovery_authorization_request.v0.json"
DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_DISCOVERY_AUTHORIZATION_PACKET.md"
CONTRACT = ROOT / "registries/fresh_motor_source_research_contract.v1.json"


class FreshMotorSourceDiscoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def assert_complete_packet_surface(self, request: dict) -> None:
        green = request["green_predecessor"]
        self.assertEqual(
            green,
            {
                "protocol_id": "FMSR1-v1",
                "commit": "e09f6cc014744485940713c148dacad9dbbe59e3",
                "CI_run_id": 33_289_147_031,
                "base_python_job_id": 99_197_577_034,
                "optional_neuro_readers_job_id": 99_197_577_007,
                "both_required_jobs_green": True,
                "on_GitHub_main": True,
                "contract_path": "registries/fresh_motor_source_research_contract.v1.json",
                "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            },
        )
        proof = request["proof_closeout"]
        self.assertEqual(
            proof["path"],
            "registries/fresh_motor_source_research_registration_proof.v0.json",
        )
        self.assertTrue(proof["pending_this_exact_commit_remote_green"])
        self.assertEqual(proof["bound_artifact_count"], 5)
        self.assertEqual(proof["bound_artifact_bytes"], 47_128)
        self.assertEqual(
            proof["canonical_artifact_set_sha256"],
            "f7afef74e7cf4b44e0fe39d8819d949903b05589c504bb6b3293ead7392d5aa4",
        )

        surface = request["frozen_discovery_surface"]
        contract_surface = self.contract["frozen_discovery_universe"]
        self.assertEqual(
            surface,
            {
                "official_index_ids_in_order": [
                    row["id"] for row in contract_surface["official_indexes"]
                ],
                "exact_text_queries_in_order": contract_surface["exact_text_queries"],
                "catalogue_without_text_search_rule": (
                    "traverse_complete_motor_EEG_category_or_DISCOVERY_CAP_PARK"
                ),
                "all_endpoint_URL_revision_method_and_scheme_host_port_method_allowlists_bound_by_implementation_record_before_execution": True,
                "general_search_engine_provider_or_ad_hoc_candidate_allowed": False,
                "query_change_after_result_allowed": False,
            },
        )

        self.assertEqual(
            request["requested_ordered_authority_after_separate_exact_green_decision"],
            {
                "generated_fixture_only_implementation": True,
                "generated_mock_network_qualification": True,
                "implementation_commit_push_and_both_remote_CI_jobs_green_before_execution": True,
                "one_metadata_only_public_discovery_execution": True,
                "execution_consumed_on_success_park_or_refusal": True,
                "retry_or_rerun": False,
            },
        )

        caps = request["network_and_resource_caps"]
        contract_caps = self.contract["future_discovery_packet_requirements"]
        shared_caps = {
            "maximum_network_requests": "maximum_network_requests",
            "maximum_response_body_bytes_total": "maximum_response_body_bytes_total",
            "maximum_retained_public_artifact_bytes": (
                "maximum_retained_public_artifact_bytes"
            ),
            "maximum_runtime_seconds": "maximum_runtime_seconds",
            "maximum_peak_RSS_bytes": "maximum_peak_RSS_bytes",
            "CPU_threads": "CPU_threads",
            "workers": "workers",
            "retry_count": "retry_count",
        }
        for request_key, contract_key in shared_caps.items():
            self.assertEqual(caps[request_key], contract_caps[contract_key], request_key)
        self.assertEqual(caps["maximum_per_request_timeout_seconds"], 30)
        self.assertEqual(caps["maximum_redirects_per_request"], 3)
        self.assertTrue(caps["request_counter_incremented_before_contact"])
        self.assertTrue(
            caps[
                "initial_requests_redirect_hops_pagination_requests_error_responses_and_failed_opens_count_toward_maximum"
            ]
        )
        self.assertEqual(
            caps["maximum_wire_response_body_bytes_total"],
            caps["maximum_response_body_bytes_total"],
        )
        self.assertEqual(
            caps["maximum_decoded_response_body_bytes_total"],
            caps["maximum_response_body_bytes_total"],
        )
        for key in (
            "all_HTTP_status_body_bytes_count_toward_both_applicable_totals",
            "cap_plus_one_streaming_allowed_only_to_detect_and_refuse_boundary_breach",
            "unsupported_content_encoding_refused_before_body_consumption",
            "every_redirect_hop_scheme_host_port_and_resolved_method_allowlisted_before_contact",
            "ordered_redirect_transcript_retained",
            "complete_pagination_required",
            "every_cursor_or_page_identity_recorded",
        ):
            self.assertTrue(caps[key], key)
        self.assertFalse(caps["redirect_method_rewrite_allowed"])
        self.assertFalse(caps["partial_or_truncated_results_may_be_ranked_or_selected"])
        self.assertEqual(caps["incremental_disk_bytes_for_payloads"], 0)

        boundary = request["candidate_boundary"]
        self.assertEqual(
            boundary,
            {
                "canonicalization_equal_to_green_v1_contract": True,
                "eligibility_predicate_equal_to_green_v1_contract": True,
                "consumed_source_exclusions_equal_to_green_v1_contract": True,
                "deterministic_total_sort_order_equal_to_green_v1_contract": True,
                "joint_control_and_storage_requirements_equal_to_green_v1_contract": True,
                "retained_field_allowlist": contract_caps["retained_field_allowlist"],
                "unknown_missing_ambiguous_or_conflicting_is_false": True,
                "maximum_selected_candidates": 1,
                "allowed_selected_route": "ELIGIBLE_FOR_METADATA_RESEARCH",
                "FULL_CONFIRMATION_SOURCE_emission_allowed": False,
                "zero_candidate_complete_surface_outcome": "NO_QUALIFYING_SOURCE",
                "incomplete_surface_outcome": "DISCOVERY_CAP_PARK",
            },
        )

        self.assertEqual(
            request["failure_routes"],
            [
                "DISCOVERY_CAP_PARK",
                "UNREGISTERED_ENDPOINT_REFUSE",
                "UNREGISTERED_METHOD_REFUSE",
                "OFF_ALLOWLIST_REDIRECT_REFUSE",
                "REDIRECT_METHOD_REWRITE_REFUSE",
                "PAGINATION_CYCLE_REFUSE",
                "DUPLICATE_PAGE_REFUSE",
                "TRUNCATED_RESPONSE_REFUSE",
                "UNSUPPORTED_CONTENT_ENCODING_REFUSE",
                "RESPONSE_CAP_REFUSE",
                "RETAINED_FIELD_REFUSE",
                "MALFORMED_RESPONSE_REFUSE",
                "RESOURCE_CAP_REFUSE",
            ],
        )
        authority = request["operation_authority_now"]
        self.assertEqual(
            set(authority),
            {
                "generated_implementation",
                "generated_qualification",
                "public_source_discovery_network_research",
                "source_specific_metadata_or_publication_research",
                "general_search_engine_or_provider",
                "payload_URL_retention",
                "payload_range_archive_member_or_header_request",
                "signal_event_annotation_target_or_label_access",
                "candidate_selection",
                "acquisition_cache_split_or_derivative_creation",
                "model_checkpoint_training_inference_prediction_or_score",
                "language_model_or_provider",
                "stream_device_or_hardware",
                "touch_other_project",
                "cleanup_delete_overwrite_rename_or_move",
                "release_or_publish",
                "scientific_claim_upgrade",
            },
        )
        for key, value in authority.items():
            self.assertFalse(value, key)
        for key, value in request["operation_counters_now"].items():
            self.assertEqual(value, 0, key)
        for key, value in request["claim_boundary"].items():
            self.assertFalse(value, key)
        decision = request["decision_requirement"]
        self.assertEqual(
            decision,
            {
                "this_request_grants_authority": False,
                "packet_and_proof_must_be_remotely_green_first": True,
                "fresh_packet_bound_maintainer_words_required": True,
                "separate_decision_commit_and_both_remote_CI_jobs_green_required": True,
                "general_continuation_or_prior_authorization_sufficient": False,
            },
        )

    def test_request_binds_exact_green_v1(self) -> None:
        green = self.request["green_predecessor"]
        self.assertEqual(green["commit"], "e09f6cc014744485940713c148dacad9dbbe59e3")
        self.assertEqual(green["CI_run_id"], 33_289_147_031)
        self.assertEqual(green["contract_sha256"], hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
        self.assertTrue(green["both_required_jobs_green"])

    def test_surface_and_caps_equal_green_contract(self) -> None:
        self.assert_complete_packet_surface(self.request)

    def test_safety_family_mutations_fail_complete_binding(self) -> None:
        cases = (
            (("proof_closeout", "canonical_artifact_set_sha256"), "0" * 64),
            (("network_and_resource_caps", "maximum_network_requests"), 129),
            (("network_and_resource_caps", "maximum_retained_public_artifact_bytes"), 1),
            (("network_and_resource_caps", "maximum_runtime_seconds"), 301),
            (("network_and_resource_caps", "maximum_peak_RSS_bytes"), 268_435_457),
            (("network_and_resource_caps", "maximum_per_request_timeout_seconds"), 31),
            (("network_and_resource_caps", "maximum_redirects_per_request"), 4),
            (("network_and_resource_caps", "request_counter_incremented_before_contact"), False),
            (("network_and_resource_caps", "maximum_wire_response_body_bytes_total"), 33_554_433),
            (("network_and_resource_caps", "maximum_decoded_response_body_bytes_total"), 33_554_433),
            (
                (
                    "network_and_resource_caps",
                    "unsupported_content_encoding_refused_before_body_consumption",
                ),
                False,
            ),
            (
                (
                    "network_and_resource_caps",
                    "every_redirect_hop_scheme_host_port_and_resolved_method_allowlisted_before_contact",
                ),
                False,
            ),
            (("network_and_resource_caps", "complete_pagination_required"), False),
            (("network_and_resource_caps", "every_cursor_or_page_identity_recorded"), False),
            (
                (
                    "network_and_resource_caps",
                    "partial_or_truncated_results_may_be_ranked_or_selected",
                ),
                True,
            ),
            (("candidate_boundary", "retained_field_allowlist"), []),
            (("failure_routes",), self.request["failure_routes"][:-1]),
            (("operation_authority_now", "payload_URL_retention"), True),
            (("decision_requirement", "this_request_grants_authority"), True),
        )
        for path, replacement in cases:
            with self.subTest(path=path):
                mutated = copy.deepcopy(self.request)
                target = mutated
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = replacement
                with self.assertRaises(AssertionError):
                    self.assert_complete_packet_surface(mutated)

    def test_every_authority_and_discovery_surface_mutation_fails(self) -> None:
        sections = (
            "requested_ordered_authority_after_separate_exact_green_decision",
            "frozen_discovery_surface",
            "operation_authority_now",
            "decision_requirement",
        )
        for section in sections:
            for key, value in self.request[section].items():
                with self.subTest(section=section, key=key):
                    mutated = copy.deepcopy(self.request)
                    if isinstance(value, bool):
                        replacement = not value
                    elif isinstance(value, list):
                        replacement = list(reversed(value)) if len(value) > 1 else []
                    elif isinstance(value, int):
                        replacement = value + 1
                    else:
                        replacement = f"{value}-MUTATED"
                    mutated[section][key] = replacement
                    with self.assertRaises(AssertionError):
                        self.assert_complete_packet_surface(mutated)

    def test_current_authority_and_counters_are_all_false_or_zero(self) -> None:
        for key, value in self.request["operation_authority_now"].items():
            self.assertFalse(value, key)
        for key, value in self.request["operation_counters_now"].items():
            self.assertEqual(value, 0, key)
        decision = self.request["decision_requirement"]
        self.assertFalse(decision["this_request_grants_authority"])
        self.assertTrue(decision["fresh_packet_bound_maintainer_words_required"])
        self.assertFalse(decision["general_continuation_or_prior_authorization_sufficient"])

    def test_candidate_route_cannot_skip_metadata_verification(self) -> None:
        boundary = self.request["candidate_boundary"]
        self.assertEqual(boundary["maximum_selected_candidates"], 1)
        self.assertEqual(boundary["allowed_selected_route"], "ELIGIBLE_FOR_METADATA_RESEARCH")
        self.assertFalse(boundary["FULL_CONFIRMATION_SOURCE_emission_allowed"])
        self.assertEqual(boundary["incomplete_surface_outcome"], "DISCOVERY_CAP_PARK")

    def test_document_is_explicitly_a_request_and_nonclaim(self) -> None:
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("This packet selects no source and authorizes nothing by itself", text)
        self.assertIn("Engineering capability requested:", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
