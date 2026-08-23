import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_eligible_total_direction_private_discriminator_authorization_request.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_ELIGIBLE_TOTAL_DIRECTION_PRIVATE_DISCRIMINATOR_AUTHORIZATION_PACKET.md"
)


class Marc2EligibleTotalDirectionPrivateDiscriminatorAuthorizationRequestTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_predecessor_proof_are_exact(self):
        self.assertEqual(self.request["lane_id"], "MARC2-VR32P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_prepared_no_decision_no_private_access",
        )
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["proof_closeout_commit"],
            "18d8fb9c9d376b680c3f0a31e513a2f37122283c",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_628_483_371)
        self.assertTrue(proof["all_required_jobs_green"])
        self.assertFalse(proof["qualification_repeated_for_proof_closeout"])
        self.assertFalse(proof["private_operation_performed_for_proof_closeout"])

    def test_all_fixed_inputs_match(self):
        total = 0
        for item in self.request["fixed_inputs"]:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(payload), item["bytes"], item["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                item["sha256"],
                item["path"],
            )
            total += len(payload)
        self.assertEqual(len(self.request["fixed_inputs"]), 13)
        self.assertEqual(total, self.request["fixed_input_bytes"])

    def test_registration_artifact_hashes_match(self):
        artifacts = self.request["registration_artifacts"]
        for prefix in ("document", "test"):
            payload = (ROOT / artifacts[f"{prefix}_path"]).read_bytes()
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                artifacts[f"{prefix}_sha256"],
            )

    def test_two_stage_sequence_is_delayed_and_single_use(self):
        stages = self.request["requested_sequence"]
        self.assertEqual([row["stage"] for row in stages], [1, 2])
        self.assertTrue(stages[0]["requires_request_proof_and_decision_green"])
        self.assertEqual(stages[0]["real_or_private_operations"], 0)
        self.assertTrue(stages[1]["requires_exact_green_stage_1_and_closeout"])
        self.assertEqual(stages[1]["registered_invocations"], 1)
        self.assertEqual(stages[1]["retry_or_rerun"], 0)

    def test_future_interface_is_fixed_path_only(self):
        interface = self.request["future_interface"]
        self.assertEqual(interface["CLI_commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(interface["execute_is_fixed_path_only"])
        for key, value in interface.items():
            if key.endswith("_allowed"):
                self.assertFalse(value, key)

    def test_private_source_is_copied_but_untouched(self):
        source = self.request["future_private_source"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["rows"], 1_227)
        self.assertFalse(source["path_checked_during_packet_preparation"])
        self.assertFalse(source["content_opened_during_packet_preparation"])
        self.assertEqual(source["bytes_read_during_packet_preparation"], 0)
        self.assertEqual(source["future_content_open_limit"], 1)

    def test_direction_map_is_aggregate_only(self):
        discriminator = self.request["future_discriminator_contract"]
        self.assertEqual(discriminator["exact_real_VR31A_calls"], 1)
        self.assertEqual(
            discriminator["frozen_map"],
            [
                {
                    "VR31A_route": "MARC2VR31A-R1",
                    "VR32P_route": "MARC2VR32P-R1",
                },
                {
                    "VR31A_route": "MARC2VR31A-R2",
                    "VR32P_route": "MARC2VR32P-R2",
                },
            ],
        )
        self.assertFalse(discriminator["observed_total_or_difference_allowed"])
        self.assertFalse(discriminator["cohort_freeze_allowed"])

    def test_generated_stage_and_resources_are_bounded(self):
        generated = self.request["generated_stage_requirements"]
        self.assertEqual(generated["required_paths"], 32)
        self.assertEqual(generated["VR31A_calls_per_path"], 1)
        self.assertEqual(
            generated["expected_route_counts"],
            {
                "MARC2VR32P-G1": 4,
                "MARC2VR32P-G2": 4,
                "MARC2VR32P-R1": 4,
                "MARC2VR32P-R2": 4,
                "MARC2VR32P-R3": 16,
            },
        )
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertLessEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["retry_rerun_resume_count"], 0)

    def test_all_authority_flags_and_operation_counters_are_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["operation_counters"].values())
        )

    def test_next_gate_requires_fresh_packet_bound_decision(self):
        gate = self.request["next_gate"]
        self.assertTrue(gate["request_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["request_proof_closeout_green_required"])
        self.assertTrue(gate["fresh_packet_bound_Tier_C_decision_required"])
        self.assertFalse(gate["implementation_authorized_now"])
        self.assertFalse(gate["private_read_authorized_now"])

    def test_human_packet_preserves_both_boundaries(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("current `continue` predates this packet", text)
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
