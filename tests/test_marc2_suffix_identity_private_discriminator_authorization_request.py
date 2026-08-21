import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT / "registries/marc2_suffix_identity_private_discriminator_authorization_request.v0.json"
)


class Marc2SuffixIdentityPrivateDiscriminatorRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_identity_and_authority_are_exactly_all_false(self):
        self.assertEqual(self.request["lane_id"], "MARC2-VR15P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_prepared_no_decision_no_private_access",
        )
        self.assertTrue(
            all(value is False for value in self.request["authorization_state"].values())
        )
        self.assertTrue(all(value == 0 for value in self.request["operation_counters"].values()))

    def test_every_predecessor_artifact_is_exact(self):
        rows = self.request["fixed_inputs"]
        self.assertEqual(len(rows), 17)
        self.assertEqual(len(rows), self.request["fixed_input_count"])
        self.assertEqual(sum(row["bytes"] for row in rows), 308_187)
        self.assertEqual(sum(row["bytes"] for row in rows), self.request["fixed_input_bytes"])
        self.assertEqual(len({row["path"] for row in rows}), len(rows))
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
            self.assertNotIn(".codex_work", row["path"])

    def test_green_proof_chain_is_exact(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["implementation_commit"],
            "bfb0dcb7752433b4af841d57bbfcbf613a341124",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 32_449_260_503)
        self.assertEqual(proof["implementation_base_job_id"], 96_674_484_190)
        self.assertEqual(proof["implementation_optional_job_id"], 96_674_484_279)
        self.assertEqual(
            proof["proof_closeout_commit"],
            "0bbd8a39f38c27931b09a41b9576585863496dbb",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_449_648_386)
        self.assertEqual(proof["proof_closeout_base_job_id"], 96_675_574_923)
        self.assertEqual(proof["proof_closeout_optional_job_id"], 96_675_574_757)
        self.assertTrue(proof["all_required_jobs_green"])

    def test_private_source_identity_is_copied_but_never_accessed(self):
        source = self.request["future_private_source"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["rows"], 1_227)
        self.assertEqual(source["regular_file_rows"], 1_025)
        self.assertEqual(source["directory_rows"], 202)
        self.assertEqual(source["mode_octal"], "0600")
        self.assertEqual(
            source["sha256"],
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        )
        self.assertFalse(source["path_checked_during_packet_preparation"])
        self.assertFalse(source["content_opened_during_packet_preparation"])

    def test_fixed_paths_are_distinct_and_have_no_override(self):
        paths = self.request["future_fixed_paths"]
        self.assertEqual(len(set(paths.values())), len(paths))
        self.assertTrue(paths["readiness_certificate"].endswith("vr15p/readiness.v0.json"))
        self.assertTrue(
            paths["output_root"].endswith("marc2_suffix_identity_private_discriminator/v0")
        )
        surface = self.request["future_interface"]
        self.assertFalse(surface["generic_path_argument_allowed"])
        self.assertFalse(surface["generic_output_argument_allowed"])
        self.assertFalse(surface["retry_resume_fallback_or_route_override_allowed"])

    def test_two_stage_order_and_route_table_are_frozen(self):
        stages = self.request["requested_sequence"]
        self.assertEqual([row["stage"] for row in stages], [1, 2])
        self.assertTrue(stages[1]["requires_exact_green_stage_1_and_proof_closeout"])
        routes = self.request["private_route_contract"]
        self.assertEqual(
            [row["route"] for row in routes],
            [f"MARC2VR15P-R{index}" for index in range(1, 17)],
        )
        self.assertTrue(all(not row["private_cohort_manifest_allowed"] for row in routes))

    def test_generated_stage_and_one_shot_resources_are_bounded(self):
        generated = self.request["generated_stage_requirements"]
        self.assertEqual(generated["required_paths"], 68)
        self.assertEqual(generated["VR15A_calls_per_path"], 1)
        self.assertEqual(generated["nested_VR12A_calls_per_path"], 1)
        self.assertGreaterEqual(generated["direct_refusal_minimum"], 100)
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["private_source_read_bytes"], 418_755)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["VR15A_classifier_calls"], 1)
        self.assertEqual(caps["nested_VR12A_calls"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["retry_rerun_resume_count"], 0)
        self.assertGreaterEqual(caps["minimum_free_disk_bytes"], 2 * 1024**3)

    def test_registration_artifacts_are_exact(self):
        artifacts = self.request["registration_artifacts"]
        for prefix in ("document", "test"):
            path = ROOT / artifacts[f"{prefix}_path"]
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                artifacts[f"{prefix}_sha256"],
            )

    def test_failure_and_output_boundaries_are_strict(self):
        failure = self.request["failure_semantics"]
        self.assertTrue(failure["failure_before_marker_consumes_invocation"])
        self.assertTrue(failure["failure_after_marker_consumes_diagnostic"])
        self.assertFalse(failure["retry_rerun_resume_or_reinspection_allowed"])
        firewall = self.request["aggregate_output_firewall"]
        self.assertFalse(firewall["per_item_outcomes_allowed"])
        self.assertFalse(firewall["private_identity_in_aggregate_report_allowed"])

    def test_claim_boundary_and_next_gate_remain_closed(self):
        claims = self.request["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_request", "scientific_ceiling"}:
                self.assertFalse(value, key)
        gate = self.request["next_gate"]
        self.assertTrue(gate["request_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["fresh_packet_bound_Tier_C_decision_required"])
        self.assertFalse(gate["implementation_authorized_now"])
        self.assertFalse(gate["private_read_authorized_now"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])


if __name__ == "__main__":
    unittest.main()
