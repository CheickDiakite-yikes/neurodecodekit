import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_inventory_taxonomy_private_discriminator_authorization_request.v0.json"
)


class InventoryTaxonomyPrivateDiscriminatorAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_and_all_false_status_are_exact(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_inventory_taxonomy_private_discriminator_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC2-VR28P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_prepared_no_decision_no_private_access",
        )

    def test_green_VR27A_proof_is_bound(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["registration_commit"],
            "47ceba3ed89df9610540fe3ed2ee8071ac1b84df",
        )
        self.assertEqual(
            proof["implementation_commit"],
            "3f74be383a672748b0781d6571d28181056865b7",
        )
        self.assertEqual(
            proof["proof_closeout_commit"],
            "f6b5dbf697d113c330f3fbf542fd97ad1c65d46d",
        )
        self.assertTrue(proof["all_required_jobs_green"])
        self.assertFalse(proof["private_operation_performed_for_proof_closeout"])

    def test_fixed_inputs_are_exact_and_hash_bound(self):
        inputs = self.request["fixed_inputs"]
        self.assertEqual(len(inputs), self.request["fixed_input_count"])
        self.assertEqual(
            sum(item["bytes"] for item in inputs), self.request["fixed_input_bytes"]
        )
        for item in inputs:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(payload), item["bytes"], item["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), item["sha256"])

    def test_registration_artifact_hashes_match(self):
        artifacts = self.request["registration_artifacts"]
        for prefix in ("document", "test"):
            payload = (ROOT / artifacts[f"{prefix}_path"]).read_bytes()
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), artifacts[f"{prefix}_sha256"]
            )

    def test_requested_sequence_has_two_delayed_stages(self):
        sequence = self.request["requested_sequence"]
        self.assertEqual([item["stage"] for item in sequence], [1, 2])
        self.assertEqual(sequence[0]["real_or_private_operations"], 0)
        self.assertTrue(
            sequence[1]["requires_exact_green_stage_1_and_proof_closeout"]
        )
        self.assertEqual(sequence[1]["registered_invocations"], 1)
        self.assertEqual(sequence[1]["retry_or_rerun"], 0)

    def test_future_paths_are_new_fixed_and_not_accessed(self):
        paths = self.request["future_fixed_paths"]
        self.assertIn("vr28p", paths["readiness_certificate"])
        self.assertIn("inventory_taxonomy_private_discriminator", paths["output_root"])
        self.assertTrue(paths["fresh_readiness_parent_must_be_absent"])
        self.assertFalse(paths["operation_on_named_consumed_path_allowed"])
        self.assertNotIn(paths["output_root"], paths["named_consumed_paths"])
        self.assertEqual(
            self.request["operation_counters"]["private_or_Git_ignored_path_operations"],
            0,
        )

    def test_private_source_is_inert_and_single_open_is_only_future_scope(self):
        source = self.request["future_private_source"]
        self.assertEqual(source["bytes"], 418755)
        self.assertEqual(
            source["sha256"],
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        )
        self.assertTrue(source["identity_copied_from_committed_records_only"])
        self.assertFalse(source["path_checked_during_packet_preparation"])
        self.assertFalse(source["content_opened_during_packet_preparation"])
        self.assertEqual(source["bytes_read_during_packet_preparation"], 0)
        self.assertEqual(source["future_content_open_limit"], 1)

    def test_generated_stage_binds_VR27A_matrix(self):
        stage = self.request["generated_stage_requirements"]
        self.assertEqual(stage["cases"], 5)
        self.assertEqual(stage["orders"], 2)
        self.assertEqual(stage["replays"], 2)
        self.assertEqual(stage["required_paths"], 20)
        self.assertEqual(stage["VR25A_calls_per_path"], 1)
        self.assertEqual(stage["VR27A_map_calls_per_path"], 1)
        self.assertGreaterEqual(stage["direct_refusal_minimum"], 70)
        self.assertEqual(stage["private_or_Git_ignored_path_operation_limit"], 0)

    def test_private_route_ceiling_is_binary_and_aggregate_only(self):
        routes = self.request["private_route_contract"]
        self.assertEqual([item["route"] for item in routes[:2]], ["MARC2VR28P-R1", "MARC2VR28P-R2"])
        self.assertEqual(routes[0]["meaning"], "eligible inventory or participant-session distribution drift")
        self.assertEqual(routes[1]["meaning"], "unknown participant taxonomy")
        self.assertTrue(all(not item["private_detail_allowed"] for item in routes))
        self.assertFalse(self.request["aggregate_output_firewall"]["per_item_outcomes_allowed"])

    def test_resource_caps_are_small_and_single_use(self):
        caps = self.request["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertLessEqual(caps["peak_RSS_bytes"], 268435456)
        self.assertEqual(caps["private_source_read_bytes"], 418755)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertLessEqual(caps["combined_incremental_output_bytes"], 1048576)
        self.assertEqual(caps["retry_rerun_resume_count"], 0)

    def test_every_authorization_flag_is_false(self):
        state = self.request["authorization_state"]
        self.assertTrue(state)
        self.assertTrue(all(value is False for value in state.values()))

    def test_every_current_operation_counter_is_zero(self):
        counters = self.request["operation_counters"]
        self.assertTrue(counters)
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_next_gate_requires_fresh_packet_bound_decision(self):
        gate = self.request["next_gate"]
        self.assertTrue(gate["request_commit_push_and_both_jobs_green_required"])
        self.assertTrue(
            gate["request_proof_closeout_commit_push_and_both_jobs_green_required"]
        )
        self.assertTrue(gate["sole_active_Tier_C_packet_identification_required"])
        self.assertTrue(gate["fresh_packet_bound_Tier_C_decision_required"])
        self.assertFalse(gate["implementation_authorized_now"])
        self.assertFalse(gate["private_read_authorized_now"])

    def test_scientific_claims_remain_false(self):
        boundary = self.request["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        for key, value in boundary.items():
            if key not in {"engineering_request", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
