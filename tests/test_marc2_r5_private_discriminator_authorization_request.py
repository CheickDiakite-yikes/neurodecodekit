import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_r5_private_discriminator_authorization_request.v0.json"
)


class Marc2R5PrivateDiscriminatorRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_identity_and_authority_are_all_false(self):
        self.assertEqual(self.request["lane_id"], "MARC2-VR22P")
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

    def test_every_predecessor_artifact_is_exact(self):
        rows = self.request["fixed_inputs"]
        self.assertEqual(len(rows), self.request["fixed_input_count"])
        self.assertEqual(sum(row["bytes"] for row in rows), self.request["fixed_input_bytes"])
        self.assertEqual(len({row["path"] for row in rows}), len(rows))
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertNotIn(".codex_work", row["path"])

    def test_green_vr21a_proof_chain_is_exact(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["implementation_commit"],
            "661b18d896eef93cd1135c780b4cdca2e7917d04",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 32_560_284_291)
        self.assertEqual(proof["implementation_base_job_id"], 97_000_708_150)
        self.assertEqual(proof["implementation_optional_job_id"], 97_000_708_047)
        self.assertEqual(
            proof["proof_closeout_commit"],
            "3aa166a5ce7a68ed60ee70786ab0892194fbd6d4",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_560_933_310)
        self.assertEqual(proof["proof_closeout_base_job_id"], 97_002_244_081)
        self.assertEqual(proof["proof_closeout_optional_job_id"], 97_002_244_114)
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
        self.assertTrue(paths["readiness_certificate"].endswith("vr22p/readiness.v0.json"))
        self.assertTrue(paths["output_root"].endswith("marc2_r5_private_discriminator/v0"))
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
            [f"MARC2VR22P-R{index}" for index in range(1, 7)],
        )
        self.assertTrue(routes[0]["private_cohort_manifest_allowed"])
        self.assertTrue(
            all(not row["private_cohort_manifest_allowed"] for row in routes[1:])
        )

    def test_generated_stage_uses_exact_two_class_map(self):
        stage = self.request["generated_stage_requirements"]
        self.assertEqual(stage["cases"], 3)
        self.assertEqual(stage["orders"], 2)
        self.assertEqual(stage["replays"], 2)
        self.assertEqual(stage["required_paths"], 12)
        self.assertEqual(stage["VR20A_calls_per_path"], 1)
        self.assertEqual(stage["direct_refusal_minimum"], 60)
        adapter = self.request["future_adapter_contract"]
        self.assertEqual(len(adapter["frozen_failure_map"]), 2)
        self.assertEqual(adapter["exact_real_VR20A_calls"], 1)
        self.assertEqual(adapter["exact_real_VR21A_map_calls_maximum"], 1)

    def test_success_cohort_bounds_are_exact_but_fw2_stays_closed(self):
        success = self.request["conditional_R1_cohort"]
        self.assertEqual(success["selected_subjects_minimum"], 12)
        self.assertEqual(success["selected_subjects_maximum"], 19)
        self.assertEqual(success["selected_run_bundles_minimum"], 72)
        self.assertEqual(success["selected_run_bundles_maximum"], 114)
        self.assertEqual(success["reservation_cap_bytes"], 8 * 1024**3)
        self.assertTrue(success["R1_makes_separate_FW2_preregistration_eligible"])
        self.assertFalse(success["FW2_implementation_or_execution_authorized"])

    def test_resources_and_one_shot_semantics_are_bounded(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["private_source_read_bytes"], 418_755)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["VR20A_calls"], 1)
        self.assertEqual(caps["VR21A_map_calls_maximum"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["retry_rerun_resume_count"], 0)
        self.assertLess(caps["peak_RSS_bytes"], 257 * 1024**2)
        self.assertGreaterEqual(caps["minimum_free_disk_bytes"], 15 * 1024**3)

    def test_registration_artifacts_are_exact(self):
        artifacts = self.request["registration_artifacts"]
        for prefix in ("document", "test"):
            path = ROOT / artifacts[f"{prefix}_path"]
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                artifacts[f"{prefix}_sha256"],
            )

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
