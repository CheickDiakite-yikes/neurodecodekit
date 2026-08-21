import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc2_published_task_private_confirmation_authorization_request.v0.json"
)
DOC_PATH = (
    ROOT
    / "docs"
    / "MARC_2_PUBLISHED_TASK_PRIVATE_CONFIRMATION_AUTHORIZATION_PACKET.md"
)


class Marc2PublishedTaskPrivateConfirmationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_identity_and_authority_are_exactly_all_false(self):
        self.assertEqual(self.request["lane_id"], "MARC2-VR20P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_prepared_no_decision_no_private_access",
        )
        self.assertTrue(
            all(value is False for value in self.request["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["operation_counters"].values())
        )

    def test_every_fixed_input_is_exact_and_tracked(self):
        rows = self.request["fixed_inputs"]
        self.assertEqual(len(rows), 20)
        self.assertEqual(len(rows), self.request["fixed_input_count"])
        self.assertEqual(sum(row["bytes"] for row in rows), 297_031)
        self.assertEqual(sum(row["bytes"] for row in rows), self.request["fixed_input_bytes"])
        self.assertEqual(len({row["path"] for row in rows}), len(rows))
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertNotIn(".codex_work", row["path"])

    def test_green_vr20a_proof_chain_is_exact(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["implementation_commit"],
            "bf4d2b729ac948d32aa1c7b239d3c65a30f18017",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 32_486_620_566)
        self.assertEqual(proof["implementation_base_job_id"], 96_784_482_381)
        self.assertEqual(proof["implementation_optional_job_id"], 96_784_482_602)
        self.assertEqual(
            proof["proof_closeout_commit"],
            "9b5bea4b4aed21234cf3e79ae682ce1606ad2f44",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_487_854_026)
        self.assertEqual(proof["proof_closeout_base_job_id"], 96_788_350_279)
        self.assertEqual(proof["proof_closeout_optional_job_id"], 96_788_350_655)
        self.assertTrue(proof["all_required_jobs_green"])
        self.assertFalse(proof["qualification_repeated_for_proof_closeout"])
        self.assertEqual(proof["private_operations_for_proof_closeout"], 0)

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
        self.assertEqual(source["bytes_read_during_packet_preparation"], 0)

    def test_interface_and_fixed_paths_have_no_override(self):
        paths = self.request["future_fixed_paths"]
        self.assertEqual(len(set(paths.values())), len(paths))
        self.assertTrue(paths["readiness_certificate"].endswith("vr20p/readiness.v0.json"))
        self.assertTrue(
            paths["output_root"].endswith(
                "marc2_published_task_private_confirmation/v0"
            )
        )
        surface = self.request["future_interface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertFalse(surface["generic_path_argument_allowed"])
        self.assertFalse(surface["generic_output_argument_allowed"])
        self.assertFalse(surface["task_run_reason_or_route_override_allowed"])
        self.assertFalse(surface["retry_resume_fallback_or_substitution_allowed"])

    def test_adapter_mapping_is_complete_and_coarse(self):
        adapter = self.request["future_adapter_contract"]
        self.assertEqual(
            adapter["exact_function"],
            "neurodecodekit.datasets.marc2_published_task_selector_repair.adapt_published_task_source",
        )
        self.assertEqual(adapter["required_task_label"], "reachingandgrasping")
        self.assertEqual(adapter["exact_real_calls"], 1)
        mapping = adapter["frozen_route_map"]
        self.assertEqual(
            sorted(route for row in mapping for route in row["VR20A_routes"]),
            [f"MARC2VR20A-F{index:02d}" for index in range(1, 10)],
        )
        self.assertTrue(adapter["private_failure_reason_retention_allowed"] is False)
        self.assertTrue(adapter["private_value_path_row_or_identity_retention_allowed"] is False)

    def test_two_stage_order_and_route_table_are_frozen(self):
        stages = self.request["requested_sequence"]
        self.assertEqual([row["stage"] for row in stages], [1, 2])
        self.assertTrue(stages[1]["requires_exact_green_stage_1_and_proof_closeout"])
        routes = self.request["private_route_contract"]
        self.assertEqual(
            [row["route"] for row in routes],
            [f"MARC2VR20P-R{index}" for index in range(1, 7)],
        )
        self.assertTrue(routes[0]["private_cohort_manifest_allowed"])
        self.assertTrue(
            all(not row["private_cohort_manifest_allowed"] for row in routes[1:])
        )

    def test_generated_stage_and_one_shot_resources_are_bounded(self):
        generated = self.request["generated_stage_requirements"]
        self.assertEqual(generated["required_paths"], 24)
        self.assertEqual(generated["VR20A_calls_per_path"], 1)
        self.assertGreaterEqual(generated["direct_refusal_minimum"], 90)
        self.assertEqual(generated["private_or_Git_ignored_path_operation_limit"], 0)
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["private_source_read_bytes"], 418_755)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["VR20A_adapter_calls"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["retry_rerun_resume_count"], 0)
        self.assertGreaterEqual(caps["minimum_free_disk_bytes"], 2 * 1024**3)

    def test_registration_document_and_test_hashes_are_exact(self):
        artifacts = self.request["registration_artifacts"]
        for prefix in ("document", "test"):
            path = ROOT / artifacts[f"{prefix}_path"]
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                artifacts[f"{prefix}_sha256"],
            )

    def test_failure_claim_and_next_gate_boundaries_are_closed(self):
        failure = self.request["failure_semantics"]
        self.assertTrue(failure["failure_before_marker_consumes_invocation"])
        self.assertTrue(failure["failure_after_marker_consumes_diagnostic"])
        self.assertFalse(failure["retry_rerun_resume_cleanup_or_reinspection_allowed"])
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

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("not retroactive Tier C", text)
        self.assertIn("It would not authorize FW2", text)


if __name__ == "__main__":
    unittest.main()
