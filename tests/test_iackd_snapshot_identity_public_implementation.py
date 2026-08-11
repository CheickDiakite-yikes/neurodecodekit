import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "iackd_snapshot_identity_public_implementation.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDSnapshotIdentityPublicImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_record_is_generated_only_and_remote_green_pending(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_snapshot_identity_public_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "IACKD-M1A")
        self.assertEqual(
            self.record["status"],
            "generated_mock_wrapper_qualified_requires_remote_green_before_public_access",
        )
        self.assertFalse(self.record["execution_state"]["wrapper_commit_remote_green"])
        self.assertFalse(self.record["execution_state"]["public_execution_consumed"])

    def test_green_decision_proof_is_exact(self) -> None:
        proof = self.record["green_decision"]
        self.assertEqual(
            proof["commit"],
            "4165c24cdad9768c7e36b5e4893602d02434be50",
        )
        self.assertEqual(proof["push_CI_run_id"], 31485359989)
        self.assertEqual(proof["base_python_job_id"], 93759373384)
        self.assertEqual(proof["optional_neuro_job_id"], 93759373333)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["decision_SHA256"],
            "73cb45db87f1d73957fdb06c588e88718a7f0855ca4c09de9a2352f41f7597e1",
        )

    def test_every_tracked_file_hash_matches(self) -> None:
        bindings = self.record["tracked_file_hashes"]
        self.assertEqual(len(bindings), 4)
        for binding in bindings:
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_transport_and_machine_contracts_are_strict(self) -> None:
        transport = self.record["implemented_transport"]
        self.assertEqual(transport["endpoint_count"], 1)
        self.assertEqual(transport["query_bytes"], 316)
        self.assertEqual(transport["request_body_bytes"], 355)
        self.assertEqual(transport["response_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(transport["response_read_calls"], 1)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["retries"], 0)
        self.assertEqual(transport["reruns"], 0)
        self.assertFalse(transport["credentials_or_API_key_interface"])
        machine = self.record["machine_gate"]
        self.assertEqual(machine["minimum_free_disk_bytes"], 2 * 1024 * 1024 * 1024)
        self.assertEqual(machine["maximum_load_per_logical_CPU"], 1.0)
        self.assertEqual(
            (machine["CPU_threads"], machine["workers"], machine["numerical_jobs"]),
            (1, 1, 1),
        )

    def test_generated_qualification_measurements_are_exact(self) -> None:
        result = self.record["generated_qualification"]
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["route"], "IACKDMP-R0")
        self.assertEqual(result["generated_response_bytes"], 531067)
        self.assertEqual(result["deterministic_replays"], 2)
        self.assertEqual(result["wrapper_refusal_mutations"], 20)
        self.assertEqual(result["tree_rows"], 1679)
        self.assertEqual(result["selected_rows"], 1340)
        self.assertEqual(result["aggregate_report_bytes"], 6151)
        self.assertEqual(result["private_manifest_bytes"], 423279)
        self.assertEqual(result["combined_output_bytes"], 429430)
        self.assertLess(result["runtime_seconds"], 30)
        self.assertLess(result["peak_RSS_bytes"], 256 * 1024 * 1024)

    def test_real_and_protected_access_counters_are_zero(self) -> None:
        counters = self.record["implementation_access_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()))
        self.assertEqual(self.record["generated_qualification"]["public_GraphQL_requests"], 0)
        self.assertEqual(self.record["generated_qualification"]["S3_payload_requests"], 0)

    def test_failure_is_consumed_and_success_cannot_cascade(self) -> None:
        behavior = self.record["one_shot_behavior"]
        self.assertTrue(behavior["private_marker_before_first_request"])
        self.assertTrue(behavior["post_marker_failure_emits_aggregate_result"])
        self.assertTrue(behavior["post_marker_failure_consumes_execution"])
        self.assertFalse(behavior["retry_available"])
        self.assertFalse(behavior["rerun_available"])
        self.assertFalse(behavior["success_authorizes_payload_access"])

    def test_verification_and_next_gate_are_explicit(self) -> None:
        verification = self.record["verification"]
        self.assertTrue(verification["focused_tests_passed"])
        self.assertTrue(verification["complete_base_suite_passed"])
        self.assertTrue(verification["complete_optional_suite_passed"])
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertTrue(verification["all_registry_JSON_valid"])
        gate = self.record["execution_state"]
        self.assertTrue(gate["wrapper_commit_required"])
        self.assertTrue(gate["wrapper_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["public_execution_eligible_before_remote_green"])
        self.assertFalse(gate["EEG_payload_access_eligible"])

    def test_human_record_separates_engineering_and_scientific_claims(self) -> None:
        document = (
            ROOT / "docs" / "IACKD_SNAPSHOT_IDENTITY_PUBLIC_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No EEG payload", document)
        claim = self.record["claim_boundary"]
        self.assertIn("wrapper", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
