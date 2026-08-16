import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc2_machine_stable_private_recovery_authorization_request.v0.json"
)
DOC_PATH = (
    ROOT / "docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_AUTHORIZATION_PACKET.md"
)


class Marc2MachineStablePrivateRecoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_request_identity_is_all_false(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_machine_stable_private_recovery_authorization_request",
        )
        self.assertEqual(self.request["lane_id"], "MARC2-VR4P")
        self.assertTrue(
            all(
                value is False
                for value in self.request["requested_authorization_flags"].values()
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_access_counters"].values())
        )

    def test_green_predecessors_are_exact(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(proof["VR4_registration"]["CI_run_id"], 31965823863)
        self.assertEqual(proof["VR4_implementation"]["CI_run_id"], 31967145837)
        self.assertEqual(proof["VR4_readiness_result"]["commit"],
                         "0a4a7fbe43238465ebd3ebbd97a20801e42f76c8")
        self.assertEqual(proof["VR4_readiness_result"]["CI_run_id"], 31967501519)
        self.assertTrue(
            all(record["both_required_jobs_green"] for record in proof.values())
        )

    def test_expired_cleanup_is_exactly_one_file(self):
        artifact = self.request["expired_certificate_identity"]
        self.assertEqual(
            artifact["path"],
            ".codex_work/marc2_machine_readiness/vr4/readiness.v0.json",
        )
        self.assertEqual(artifact["mode"], "0600")
        self.assertEqual(artifact["bytes"], 4551)
        self.assertEqual(
            artifact["sha256"],
            "5c268ffaefe6e557ace92214c6ec3bab6db29d0a89dee4c83ebd94dbf07b522e",
        )
        self.assertEqual(artifact["unlink_limit"], 1)
        self.assertEqual(artifact["other_path_or_project_deletion_limit"], 0)

    def test_fresh_readiness_precedes_private_operations(self):
        readiness = self.request["fresh_readiness_contract"]
        self.assertEqual(readiness["consecutive_passing_samples"], 3)
        self.assertEqual(readiness["maximum_wait_seconds"], 600)
        self.assertTrue(
            readiness["bind_future_exact_executor_implementation_commit_from_proof_record"]
        )
        self.assertFalse(readiness["ambient_HEAD_binding_allowed"])
        self.assertFalse(readiness["output_or_private_path_operation_before_ready"])

    def test_private_source_and_cohort_are_unchanged(self):
        source = self.request["private_source_identity"]
        self.assertEqual(source["bytes"], 418755)
        self.assertEqual(source["rows"], 1227)
        self.assertEqual(source["source_bundles"], 238)
        self.assertEqual(source["eligible_bundles"], 195)
        self.assertEqual(source["valid_ineligible_bundles"], 43)
        cohort = self.request["frozen_cohort_invariants"]
        self.assertEqual(cohort["selected_subjects"], 16)
        self.assertEqual(cohort["selected_bundles"], 96)
        self.assertEqual(cohort["selected_members"], 384)
        self.assertEqual(cohort["archive_member_or_payload_bytes"], 0)

    def test_marker_is_immediately_before_one_open(self):
        output = self.request["future_output_contract"]
        sequence = self.request["requested_sequence"]
        self.assertTrue(output["root_must_be_absent"])
        self.assertTrue(output["marker_immediately_before_private_content_open"])
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["retry_limit"], 0)
        self.assertEqual(sequence["rerun_limit"], 0)

    def test_resources_are_small_and_payload_free(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2)
        self.assertEqual(caps["private_source_input_bytes"], 418755)
        self.assertEqual(caps["combined_output_bytes"], 4 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)

    def test_fresh_decision_and_green_implementation_are_required(self):
        requirements = self.request["decision_requirements"]
        self.assertTrue(all(requirements.values()))
        gate = self.request["next_gate"]
        self.assertEqual(gate["current_authority"], "none_request_only")
        self.assertFalse(gate["private_structural_pass_authorized"])
        self.assertFalse(gate["FW2_or_CIL1_eligible"])

    def test_packet_disclaims_scientific_result(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("All authorization fields false", text)
        self.assertIn("current and earlier `continue` messages are not retroactive", text)
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
