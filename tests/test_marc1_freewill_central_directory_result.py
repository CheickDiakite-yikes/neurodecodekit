import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries" / "marc1_freewill_central_directory_result.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1FreewillCentralDirectoryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_route_and_consumed_status(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_freewill_central_directory_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(
            self.result["result_id"],
            "MARC1-CD1-generated-central-directory-result-v0",
        )
        self.assertEqual(self.result["route"], "MARC1CDG-R1")
        self.assertEqual(
            self.result["status"],
            "consumed_passed_generated_mock_qualification_no_scientific_value",
        )

    def test_green_implementation_proof_is_exact(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"], "211fd78fba82a660c4730a586541819b2eb264fd"
        )
        self.assertEqual(proof["CI_run_id"], 31_511_626_051)
        self.assertEqual(proof["base_job_id"], 93_846_584_402)
        self.assertEqual(proof["optional_neuro_job_id"], 93_846_584_527)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_committed_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_generated_output_hashes_sizes_and_cleanup_are_exact(self):
        outputs = self.result["generated_output_artifacts"]
        self.assertEqual(outputs["aggregate_report"]["bytes"], 5_898)
        self.assertEqual(
            outputs["aggregate_report"]["sha256"],
            "a8bfc657ca77464292c7ab047e46a7a8cec1c66bb9876845a2ef30c7e4c355ab",
        )
        self.assertEqual(outputs["private_manifest"]["bytes"], 5_676)
        self.assertEqual(
            outputs["private_manifest"]["sha256"],
            "c38c0be784f19401b08da26bdd2d0dd6a43339c34202f6845c7ca7cb6b5c4bf0",
        )
        self.assertEqual(outputs["combined_bytes"], 11_574)
        self.assertTrue(outputs["temporary_output_directory_removed"])
        self.assertFalse(outputs["generated_outputs_committed"])

    def test_virtual_archive_inventory_is_exact_and_payload_free(self):
        archive = self.result["archive_summary"]
        self.assertEqual(archive["virtual_archive_bytes"], 13_591_548_048)
        self.assertEqual(archive["materialized_generated_bytes"], 280_249)
        self.assertEqual(archive["tail_bytes"], 131_072)
        self.assertEqual(archive["central_directory_bytes"], 148_910)
        self.assertEqual(archive["entry_count"], 18)
        self.assertEqual(archive["directory_count"], 4)
        self.assertEqual(archive["regular_file_count"], 14)
        self.assertEqual(archive["ZIP64_extended_member_count"], 1)
        self.assertEqual(archive["local_header_bytes"], 0)
        self.assertEqual(archive["member_payload_bytes"], 0)

    def test_transport_paths_are_exact_and_mock_only(self):
        transport = self.result["transport_summary"]
        self.assertEqual(transport["direct_path_requests"], 3)
        self.assertEqual(transport["redirect_path_requests"], 5)
        self.assertEqual(transport["bodyless_redirects"], 2)
        self.assertEqual(transport["body_bytes_per_path"], 280_249)
        self.assertEqual(transport["response_bodies_per_path"], 3)
        self.assertEqual(transport["terminal_status"], 206)
        self.assertTrue(transport["mock_only"])

    def test_runtime_memory_and_output_caps_passed(self):
        measurements = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertEqual(measurements["generated_input_bytes"], 280_249)
        self.assertEqual(measurements["generated_output_bytes"], 11_574)
        self.assertLessEqual(measurements["runtime_seconds"], caps["runtime_seconds"])
        self.assertLessEqual(measurements["peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLessEqual(
            measurements["generated_output_bytes"], caps["combined_output_bytes"]
        )
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)
        self.assertEqual(measurements["producer_is_causal"], "not_applicable_metadata_only")
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_all_mutations_and_acceptance_gates_passed(self):
        mutations = self.result["mutation_summary"]
        self.assertEqual(mutations["required_count"], 32)
        self.assertEqual(mutations["passed_count"], 32)
        self.assertEqual(sum(mutations["route_counts"].values()), 32)
        self.assertEqual(len(self.result["acceptance_gates"]), 14)
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_every_live_real_model_score_and_claim_counter_is_zero(self):
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))
        measurements = self.result["measurements"]
        self.assertEqual(measurements["raw_data_reads"], 0)
        self.assertEqual(measurements["real_cache_reads"], 0)
        self.assertEqual(measurements["model_runs"], 0)
        self.assertEqual(measurements["training_runs"], 0)

    def test_warnings_and_unavailable_fields_preserve_claim_boundary(self):
        self.assertEqual(len(self.result["warnings"]), 6)
        self.assertIn("end-to-end latency", self.result["unavailable_fields"])
        self.assertIn("real member inventory", self.result["unavailable_fields"])
        self.assertFalse(self.result["claim_boundary"]["scientific_claim_established"])

    def test_public_result_contains_no_private_inventory_or_local_path(self):
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("member_name", serialized)
        self.assertNotIn("local_header_offset", serialized)
        self.assertNotIn("/private/tmp", serialized)
        self.assertNotIn("dataset/", serialized)

    def test_closeout_is_consumed_and_live_gate_remains_closed(self):
        disposition = self.result["disposition"]
        self.assertEqual(disposition["registered_generated_closeout_runs"], 1)
        self.assertTrue(disposition["consumed"])
        self.assertFalse(disposition["retry_or_rerun_authorized"])
        self.assertFalse(disposition["public_metadata_access_authorized"])
        self.assertFalse(disposition["public_archive_range_access_authorized"])
        self.assertFalse(disposition["real_payload_access_authorized"])
        self.assertTrue(disposition["next_gate_is_all_false_Tier_C_request"])


if __name__ == "__main__":
    unittest.main()
