import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries" / "marc1_generated_qualification_result.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1GeneratedQualificationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_route_and_consumed_status(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_generated_qualification_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["result_id"], "MARC-1-generated-qualification-result-v0")
        self.assertEqual(self.result["route"], "MARC1G-R1")
        self.assertEqual(
            self.result["status"],
            "consumed_passed_generated_qualification_no_scientific_value",
        )

    def test_green_implementation_proof_is_exact(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(proof["commit"], "e35a58743766ba404ae16f63804481a5f51531c9")
        self.assertEqual(proof["CI_run_id"], 31_505_555_044)
        self.assertEqual(proof["base_job_id"], 93_826_102_571)
        self.assertEqual(proof["optional_neuro_job_id"], 93_826_102_044)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_committed_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_generated_output_hashes_and_sizes_are_exact(self):
        outputs = self.result["generated_output_artifacts"]
        self.assertEqual(outputs["aggregate_report"]["bytes"], 5_018)
        self.assertEqual(
            outputs["aggregate_report"]["sha256"],
            "f7c4de84f7d80bee7461ae38e13c560e54f075a6a6df41faa1aa853a48599c70",
        )
        self.assertEqual(outputs["private_manifest"]["bytes"], 2_795)
        self.assertEqual(
            outputs["private_manifest"]["sha256"],
            "008ae558bd0192bb853ddc0d8dafa873ba6f048dcc62b0ebaeb6104b0f1150cf",
        )
        self.assertEqual(outputs["combined_bytes"], 7_813)
        self.assertTrue(outputs["temporary_output_directory_removed"])

    def test_runtime_memory_range_and_output_caps_passed(self):
        measurements = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertEqual(measurements["generated_input_bytes"], 81_139)
        self.assertEqual(measurements["generated_output_bytes"], 7_813)
        self.assertLessEqual(measurements["runtime_seconds"], caps["runtime_seconds"])
        self.assertLessEqual(measurements["peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLessEqual(measurements["range_read_calls"], caps["range_read_calls"])
        self.assertLessEqual(
            measurements["range_bytes_returned"], caps["range_bytes_returned"]
        )
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)

    def test_archive_inventory_proves_metadata_only_traversal(self):
        archive = self.result["archive_summary"]
        self.assertEqual(archive["archive_bytes"], 67_916)
        self.assertEqual(archive["member_count"], 14)
        self.assertEqual(archive["forced_ZIP64_member_count"], 1)
        self.assertEqual(archive["member_content_reads"], 0)
        self.assertEqual(archive["member_extractions"], 0)
        self.assertEqual(archive["payload_interval_read_bytes"], 0)
        self.assertEqual(archive["compression_method_counts"], {"0": 2, "8": 12})

    def test_multimodal_plan_counts_and_firewall_are_exact(self):
        plan = self.result["multimodal_summary"]
        self.assertEqual(plan["source_profile_count"], 2)
        self.assertEqual(plan["channel_record_count"], 18)
        self.assertEqual(plan["comparator_role_count"], 12)
        self.assertEqual(plan["fit_row_count"], 4)
        self.assertEqual(plan["target_blind_prediction_row_count"], 4)
        self.assertEqual(plan["isolated_scorer_row_count"], 4)
        self.assertTrue(plan["causal"])
        self.assertEqual(plan["future_context_samples"], 0)
        self.assertFalse(plan["end_to_end_latency_measured"])

    def test_all_mutations_and_acceptance_gates_passed(self):
        mutations = self.result["mutation_summary"]
        self.assertEqual(mutations["required_count"], 24)
        self.assertEqual(mutations["passed_count"], 24)
        self.assertEqual(sum(mutations["route_counts"].values()), 24)
        self.assertEqual(len(self.result["acceptance_gates"]), 14)
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_every_real_model_score_and_claim_counter_is_zero(self):
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))
        measurements = self.result["measurements"]
        self.assertEqual(measurements["raw_data_reads"], 0)
        self.assertEqual(measurements["real_cache_reads"], 0)
        self.assertEqual(measurements["model_runs"], 0)
        self.assertEqual(measurements["training_runs"], 0)

    def test_warnings_and_unavailable_fields_preserve_claim_boundary(self):
        warnings = self.result["warnings"]
        unavailable = self.result["unavailable_fields"]
        self.assertEqual(len(warnings), 5)
        self.assertIn("End-to-end latency was not measured.", warnings)
        self.assertIn("decoding accuracy", unavailable)
        self.assertIn("end-to-end latency", unavailable)
        self.assertFalse(self.result["claim_boundary"]["scientific_claim_established"])

    def test_public_result_contains_no_member_name_offset_or_local_path(self):
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("member_name", serialized)
        self.assertNotIn("local_header_offset", serialized)
        self.assertNotIn("/private/tmp", serialized)
        self.assertNotIn("sub-01", serialized)

    def test_closeout_is_consumed_and_next_real_gate_remains_closed(self):
        disposition = self.result["disposition"]
        self.assertEqual(disposition["registered_generated_closeout_runs"], 1)
        self.assertTrue(disposition["consumed"])
        self.assertFalse(disposition["retry_or_rerun_authorized"])
        self.assertFalse(disposition["public_metadata_access_authorized"])
        self.assertFalse(disposition["real_payload_access_authorized"])
        self.assertTrue(disposition["next_Tier_A_design_is_metadata_range_audit"])


if __name__ == "__main__":
    unittest.main()
