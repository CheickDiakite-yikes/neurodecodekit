import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_request.v0.json"
)
DECISION_PATH = (
    ROOT
    / "registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_decision.v0.json"
)
DOC_PATH = (
    ROOT / "docs/MARC_2_SELECTION_SUFFICIENCY_PRIVATE_COHORT_FREEZE_AUTHORIZATION_DECISION.md"
)


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class SelectionSufficiencyPrivateCohortFreezeDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.document = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_and_exact_user_message_are_bound(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_selection_sufficiency_private_cohort_freeze_authorization_decision",
        )
        self.assertEqual(self.decision["lane_id"], "MARC2-VR39P")
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"],
            "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad",
        )
        self.assertEqual(user["sole_active_Tier_C_packet"], "MARC2-VR39P")
        self.assertFalse(user["message_silently_corrected"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])

    def test_request_and_proof_green_are_exact(self):
        request = self.decision["green_request"]
        self.assertEqual(request["commit"], "6c805a817fa44375b7b0e120abcb2c748c78ca07")
        self.assertEqual(request["CI_run_id"], 32_675_925_646)
        self.assertEqual(request["base_python_job_id"], 97_283_907_786)
        self.assertEqual(request["optional_neuro_job_id"], 97_283_907_932)
        self.assertTrue(request["both_required_jobs_green"])

        proof = self.decision["green_proof_closeout"]
        self.assertEqual(proof["commit"], "e581fe99d97e91e5af07e211dd75caa22a10d098")
        self.assertEqual(proof["CI_run_id"], 32_677_755_105)
        self.assertEqual(proof["base_python_job_id"], 97_288_870_035)
        self.assertEqual(proof["optional_neuro_job_id"], 97_288_870_180)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])
        self.assertTrue(proof["metadata_only_protocol_deviation_recorded"])
        self.assertEqual(proof["private_descendant_or_content_operations"], 0)

    def test_six_bound_packet_artifacts_are_exact(self):
        rows = self.decision["bound_packet_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 61_722)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_decision_artifacts_and_counters_are_exact(self):
        for row in self.decision["decision_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

        counters = self.decision["decision_only_counters"]
        for key, value in counters.items():
            if key == "GitHub_CI_verification_calls":
                self.assertEqual(value, 5)
            else:
                self.assertEqual(value, 0, key)

    def test_authorization_is_strictly_staged(self):
        authorization = self.decision["authorization"]
        self.assertTrue(authorization["generated_wrapper_implementation_after_decision_green"])
        self.assertTrue(authorization["generated_wrapper_qualification_after_decision_green"])
        self.assertTrue(authorization["one_private_structural_read_after_stage_1_proof_green"])
        self.assertTrue(authorization["one_private_cohort_freeze_after_stage_1_proof_green"])
        for key, value in authorization.items():
            if key.endswith("authorized_now"):
                self.assertFalse(value, key)

    def test_generated_matrix_and_readiness_are_exact(self):
        stage = self.decision["generated_stage_requirements"]
        self.assertEqual(stage["case_count"], 21)
        self.assertEqual(stage["successful_cardinalities"], list(range(12, 20)))
        self.assertEqual(stage["required_paths"], 168)
        self.assertEqual(stage["VR33A_calls"], 168)
        self.assertEqual(stage["readiness_provider_calls"], 504)
        self.assertEqual(stage["readiness_sleeper_calls"], 336)
        self.assertEqual(stage["VR38A_calls"], 84)
        self.assertEqual(stage["generated_cohort_writes"], 64)
        self.assertEqual(stage["route_counts"], {"MARC2VR39P-R1": 64, "MARC2VR39P-R2": 104})
        self.assertGreaterEqual(stage["direct_refusal_minimum"], 200)
        readiness = self.decision["readiness_contract"]
        self.assertEqual(readiness["sample_provider_calls"], 3)
        self.assertEqual(readiness["sleeper_calls"], 2)
        self.assertEqual(readiness["passing_pattern"], "PPP")
        self.assertFalse(readiness["dynamic_loop_allowed"])

    def test_routes_cohort_commitment_and_storage_are_frozen(self):
        routes = self.decision["private_route_contract"]
        self.assertEqual([row["route"] for row in routes], ["MARC2VR39P-R1", "MARC2VR39P-R2"])
        self.assertTrue(all(not row["private_detail_allowed"] for row in routes))
        cohort = self.decision["cohort_freeze_contract"]
        self.assertEqual(cohort["minimum_selected_subjects"], 12)
        self.assertEqual(cohort["maximum_selected_subjects"], 19)
        self.assertEqual(cohort["required_runs_per_session"], [1, 2, 3])
        self.assertEqual(cohort["selected_bundles_per_subject"], 6)
        self.assertEqual(cohort["selected_core_members_per_subject"], 24)
        commitment = self.decision["private_commitment_contract"]
        self.assertEqual(commitment["scheme"], "HMAC-SHA256-v0")
        self.assertEqual(commitment["private_nonce_bytes"], 32)
        self.assertFalse(commitment["nonce_allowed_in_public_output"])
        storage = self.decision["storage_feasibility_contract"]
        self.assertEqual(storage["selected_compressed_payload_bytes_maximum"], 8_589_934_592)
        self.assertEqual(storage["peak_incremental_disk_bytes_maximum"], 10_737_418_240)

    def test_output_firewall_and_metadata_accounting_are_preserved(self):
        output = self.decision["aggregate_output_firewall"]
        self.assertEqual(len(output["public_allowlist_fields"]), 11)
        self.assertTrue(output["every_R2_public_report_byte_identical"])
        self.assertTrue(output["public_commitment_only_on_R1"])
        self.assertFalse(output["selected_count_identity_topology_or_failure_detail_allowed"])
        accounting = self.decision["inherited_proof_metadata_accounting"]
        self.assertEqual(accounting["repository_root_directory_listings"], 1)
        self.assertEqual(accounting["Git_ignored_root_entry_metadata_observations"], 1)
        self.assertEqual(accounting["descendant_or_content_operations"], 0)
        self.assertEqual(accounting["private_source_or_consumed_state_content_operations"], 0)
        self.assertFalse(accounting["metadata_values_retained_in_decision"])

    def test_resources_and_claim_boundary_remain_closed(self):
        caps = self.decision["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["private_source_read_bytes_if_ready"], 418_755)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["signal_bytes"], 0)
        self.assertEqual(caps["target_bytes"], 0)
        self.assertEqual(caps["retry_rerun_resume_count"], 0)

        claims = self.decision["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability_authorized_after_green", "scientific_ceiling"}:
                self.assertFalse(value, key)
        self.assertIn("Scientific claim not established", self.document)


if __name__ == "__main__":
    unittest.main()
