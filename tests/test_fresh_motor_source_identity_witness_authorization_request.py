import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets.fresh_motor_source_discovery import registered_plan

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries/fresh_motor_source_identity_witness_authorization_request.v0.json"
PACKET = ROOT / "docs/FRESH_MOTOR_SOURCE_IDENTITY_WITNESS_AUTHORIZATION_PACKET.md"
PROOF = ROOT / "registries/fresh_motor_source_admission_generated_qualification_proof.v0.json"


class FreshMotorSourceIdentityWitnessAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_green_predecessor_is_exact(self) -> None:
        predecessor = self.request["green_predecessor"]
        self.assertEqual(predecessor["commit"], "dbfaf682595c33d3c6de10e88503fb84a2a6254c")
        self.assertEqual(predecessor["CI_run_id"], 33352882661)
        self.assertEqual(predecessor["base_python_job_id"], 99369471021)
        self.assertEqual(predecessor["optional_neuro_readers_job_id"], 99369470875)
        proof_bytes = PROOF.read_bytes()
        self.assertEqual(len(proof_bytes), predecessor["proof_bytes"])
        self.assertEqual(hashlib.sha256(proof_bytes).hexdigest(), predecessor["proof_sha256"])

    def test_all_five_profiles_use_conservative_opaque_mode(self) -> None:
        profiles = self.request["index_profiles"]
        self.assertEqual(
            [row["index_id"] for row in profiles],
            ["OPENNEURO_CRN", "NEMAR", "PHYSIONET", "GIGADB", "BNCI_HORIZON_2020"],
        )
        self.assertEqual(sum(row["root_request_count"] for row in profiles), 17)
        self.assertTrue(all(row["mode"] == "OPAQUE_COMPLETE_SNAPSHOT_REPLAY" for row in profiles))
        self.assertTrue(
            all(
                row["candidate_semantic_decode_extract_iterate_or_retain_allowed"] is False
                for row in profiles
            )
        )
        self.assertFalse(self.request["revision_admission"]["SOURCE_GLOBAL_REVISION_selected"])

    def test_all_17_root_identities_and_profile_hashes_replay_exactly(self) -> None:
        plan = registered_plan()
        canonical = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        frozen = self.request["frozen_discovery_plan"]
        self.assertEqual(len(canonical), frozen["canonical_JSON_object_bytes"])
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(), frozen["canonical_JSON_object_sha256"]
        )
        emitted = canonical + b"\n"
        self.assertEqual(len(emitted), frozen["canonical_plan_bytes"])
        self.assertEqual(hashlib.sha256(emitted).hexdigest(), frozen["canonical_plan_sha256"])
        self.assertEqual(plan["request_identities"], frozen["root_request_identities"])
        specs = {row["index_id"]: row for row in plan["index_specs"]}
        for profile in self.request["index_profiles"]:
            plan_index_id = profile["discovery_plan_index_id"]
            subset = {
                "index_spec": specs[plan_index_id],
                "request_identities": [
                    row for row in plan["request_identities"] if row["index_id"] == plan_index_id
                ],
            }
            payload = json.dumps(
                subset, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
            self.assertEqual(len(payload), profile["canonical_plan_profile_bytes"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), profile["canonical_plan_profile_sha256"]
            )

    def test_snapshot_is_complete_or_park_and_target_free(self) -> None:
        ledger = self.request["opaque_snapshot_ledger_contract"]
        self.assertEqual(ledger["exact_root_count"], 17)
        self.assertEqual(ledger["outer_field"], "profiles")
        self.assertTrue(ledger["root_order_must_equal_frozen_discovery_plan"])
        self.assertTrue(ledger["all_17_roots_complete_required"])
        self.assertFalse(ledger["candidate_semantic_decode_extract_iterate_retain_rank_or_select_allowed"])
        self.assertTrue(ledger["identical_response_body_hash_for_distinct_request_identities_allowed"])
        self.assertFalse(self.request["result_router"]["partial_ledger_can_authorize_D1"])
        counters = self.request["operation_counters_now"]
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_snapshot_hash_tree_reconciles_profiles_roots_and_pages(self) -> None:
        ledger = self.request["opaque_snapshot_ledger_contract"]
        membership = ledger["profile_root_membership"]
        self.assertEqual(list(membership), ledger["profile_order"])
        flattened = [ordinal for index_id in ledger["profile_order"] for ordinal in membership[index_id]]
        self.assertEqual(flattened, list(range(17)))
        self.assertTrue(ledger["all_root_ordinals_appear_in_exactly_one_profile"])
        self.assertTrue(ledger["profile_and_global_counts_and_bytes_must_equal_nested_sums"])
        self.assertIn("profile_sha256_values", ledger["required_outer_fields"])

        reconciliation = ledger["child_digest_reconciliation"]
        self.assertTrue(
            all(
                value is True
                for key, value in reconciliation.items()
                if key != "digest_array_substitution_omission_duplication_or_reordering_allowed"
            )
        )
        self.assertFalse(
            reconciliation["digest_array_substitution_omission_duplication_or_reordering_allowed"]
        )

        synthetic_profiles = []
        for profile_ordinal, index_id in enumerate(ledger["profile_order"]):
            roots = [
                {
                    "root_ordinal": root_ordinal,
                    "canonical_root_ledger_sha256": f"{root_ordinal:064x}",
                }
                for root_ordinal in membership[index_id]
            ]
            synthetic_profiles.append(
                {
                    "profile_ordinal": profile_ordinal,
                    "canonical_profile_ledger_sha256": f"{profile_ordinal + 100:064x}",
                    "roots": roots,
                    "root_sha256_values": [
                        root["canonical_root_ledger_sha256"] for root in roots
                    ],
                }
            )
        profile_sha256_values = [
            profile["canonical_profile_ledger_sha256"] for profile in synthetic_profiles
        ]
        global_root_sha256_values = [
            root["canonical_root_ledger_sha256"]
            for profile in synthetic_profiles
            for root in profile["roots"]
        ]
        self.assertEqual(len(profile_sha256_values), 5)
        self.assertEqual(len(global_root_sha256_values), 17)
        self.assertEqual(
            global_root_sha256_values,
            [f"{root_ordinal:064x}" for root_ordinal in range(17)],
        )

        hashes = ledger["canonical_hash_contract"]
        self.assertEqual(hashes["hash"], "SHA_256_lowercase_hex")
        self.assertIn("page_sha256_values", hashes["root_preimage_fields"])
        self.assertIn("root_sha256_values", hashes["profile_preimage_fields"])
        self.assertIn("profile_sha256_values", hashes["global_preimage_fields"])
        self.assertIn("global_root_sha256_values", hashes["global_preimage_fields"])
        self.assertNotIn("canonical_page_ledger_sha256", hashes["page_preimage_fields"])
        self.assertNotIn("canonical_root_ledger_sha256", hashes["root_preimage_fields"])
        self.assertNotIn("canonical_profile_ledger_sha256", hashes["profile_preimage_fields"])
        self.assertNotIn("canonical_global_ledger_sha256", hashes["global_preimage_fields"])

    def test_HTTP_request_identity_includes_required_protocol_headers(self) -> None:
        profile = self.request["exact_source_HTTP_profile"]
        self.assertEqual(profile["HTTP_version"], "HTTP/1.1")
        managed = profile["protocol_managed_headers_in_order_after_application_headers"]
        self.assertEqual([row["name"] for row in managed], ["Host", "Content-Length"])
        self.assertEqual(managed[0]["required_for_methods"], ["GET", "POST"])
        self.assertEqual(managed[1]["required_for_methods"], ["POST"])
        self.assertFalse(profile["Transfer_Encoding_request_header_allowed"])
        self.assertIn("protocol_managed_headers_in_order", profile["request_identity_covers"])
        self.assertFalse(
            profile["implicit_or_automatically_added_header_outside_the_two_protocol_managed_headers_allowed"]
        )

    def test_pagination_grammars_are_typed_and_source_bound(self) -> None:
        URL = self.request["continuation_URL_canonicalization"]
        self.assertEqual(URL["algorithm_id"], "FMSR1_URL_FORM_V0")
        self.assertFalse(URL["query_form_decoder"]["duplicate_keys_allowed"])
        self.assertFalse(URL["mixed_continuation_keys_allowed"])

        shared = self.request["shared_pagination_control_schemas"]
        JSON_control = shared["GENERIC_JSON_CONTROL_V0"]
        self.assertEqual(
            [row["variant_id"] for row in JSON_control["control_variants"]],
            ["TOP_LEVEL_NEXT", "PAGINATION_NEXT", "PAGINATION_HAS_NEXT_FALSE"],
        )
        self.assertTrue(JSON_control["exactly_one_control_variant_required"])
        HTML_control = shared["GENERIC_HTML_CONTROL_V0"]
        self.assertEqual(HTML_control["distinct_matching_container_count"], 1)
        self.assertEqual(
            HTML_control["next_control"]["one_match_means_continuation_URL_processed_only_by"],
            "FMSR1_URL_FORM_V0",
        )

        grammars = {row["index_id"]: row for row in self.request["pagination_grammars"]}
        self.assertEqual(set(grammars), {row["index_id"] for row in self.request["index_profiles"]})
        openneuro = grammars["OPENNEURO_CRN"]
        self.assertEqual(
            openneuro["continuation_case"]["only_mutable_JSON_pointer"], "/variables/after"
        )
        self.assertIsNone(openneuro["terminal_case"]["endCursor_required_exact_value"])
        for index_id in ("NEMAR", "PHYSIONET", "GIGADB", "BNCI_HORIZON_2020"):
            grammar = grammars[index_id]
            self.assertEqual(grammar["URL_algorithm_id"], "FMSR1_URL_FORM_V0")
            self.assertEqual(
                set(grammar["media_type_branches"].values()),
                {"GENERIC_JSON_CONTROL_V0", "GENERIC_HTML_CONTROL_V0"},
            )
            self.assertEqual(
                set(grammar["continuation_key_value_types"]),
                set(grammar["allowed_continuation_keys"]),
            )
            self.assertFalse(grammar["terminal_without_exact_schema_evidence_allowed"])

    def test_redirect_transcript_is_fully_typed_and_chained(self) -> None:
        redirect = self.request["redirect_hop_contract"]
        required = set(redirect["required_fields_in_canonical_order"])
        self.assertEqual(required, set(redirect["field_types"]))
        self.assertLessEqual(redirect["maximum_items"], 3)
        self.assertEqual(redirect["Location_header_count"], 1)
        self.assertTrue(redirect["DNS_TLS_and_peer_evidence_required_for_every_hop"])
        self.assertTrue(redirect["redirect_response_headers_and_entity_body_are_counted_and_hashed"])
        self.assertTrue(
            redirect["next_hop_request_identity_must_equal_previous_normalized_next_request_identity"]
        )

    def test_CI_and_marker_order_is_fail_closed(self) -> None:
        ci = self.request["CI_W0_contract"]
        firewall = self.request["attempt_and_transport_firewall"]
        self.assertEqual(ci["request_count"], 3)
        self.assertIn("git/ref/heads/main", ci["current_main_ref_request"])
        self.assertIn("{local_HEAD_sha}", ci["exact_HEAD_check_runs_request_template"])
        self.assertIn("git/blobs/", ci["exact_workflow_blob_request"])
        self.assertTrue(ci["current_main_ref_object_SHA_must_equal_local_HEAD"])
        self.assertTrue(ci["decision_does_not_claim_its_future_commit_or_future_check_run_ids"])
        self.assertEqual(ci["check_runs_response_total_count"], 2)
        self.assertEqual(ci["required_job_multiplicity_each"], 1)
        self.assertFalse(ci["additional_check_runs_allowed"])
        self.assertNotIn(
            "authorized_execution_decision_commit",
            ci["second_authority_bearing_execution_decision_must_bind"],
        )
        self.assertFalse(ci["implementation_specific_values_bound_now"])
        self.assertFalse(ci["source_contact_before_second_decision_exact_green_and_live_CI_success"])
        self.assertTrue(firewall["durable_no_follow_consumed_marker_before_first_GitHub_DNS_or_socket"])
        self.assertTrue(firewall["CI_and_source_contact_same_process"])
        self.assertFalse(firewall["pause_user_input_reexec_resume_or_mutable_handoff_allowed"])
        self.assertEqual(
            firewall["state_machine"],
            [
                "CLOSED",
                "LOCAL_PREFLIGHT",
                "RESERVED_PENDING",
                "ARMED_CONSUMED",
                "CI_W0",
                "SEVENTEEN_ROOT_WITNESS",
                "FINALIZE",
                "COMPLETE_OR_PARK",
            ],
        )

    def test_caps_and_authority_are_strict(self) -> None:
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], caps["workers"])
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertLessEqual(caps["maximum_peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertLessEqual(caps["maximum_retained_witness_artifact_bytes"], 1024 * 1024)
        self.assertEqual(caps["retry_count"], 0)
        self.assertEqual(caps["rerun_count"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["CI_requests"] + caps["maximum_official_index_requests"], 128)
        self.assertEqual(caps["maximum_total_network_requests"], 128)
        self.assertTrue(all(value is False for value in self.request["operation_authority_now"].values()))
        self.assertFalse(self.request["decision_requirement"]["this_request_grants_authority"])
        self.assertFalse(
            self.request["decision_requirement"]["general_continuation_or_prior_authorization_sufficient"]
        )

    def test_human_packet_preserves_engineering_science_split(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("This packet grants nothing.", text)

    def test_governing_contract_hashes_are_exact(self) -> None:
        for artifact in self.request["governing_contracts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])


if __name__ == "__main__":
    unittest.main()
