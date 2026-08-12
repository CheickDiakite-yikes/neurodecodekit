import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc1_privacy_preserving_pilot_selection_result.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1PilotSelectionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_route_and_consumed_status(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_privacy_preserving_pilot_selection_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["result_id"], "MARC1-P1-generated-result-v0")
        self.assertEqual(self.result["route"], "MARC1PSG-R1")
        self.assertEqual(
            self.result["status"],
            "consumed_passed_generated_selection_no_scientific_value",
        )

    def test_green_implementation_proof_is_exact(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(proof["commit"], "0c0a6982c6b9c65d6c51413d1baa8b577e00a194")
        self.assertEqual(proof["CI_run_id"], 31_571_668_853)
        self.assertEqual(proof["base_job_id"], 94_034_790_262)
        self.assertEqual(proof["optional_neuro_job_id"], 94_034_790_315)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_committed_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_generated_output_hashes_sizes_mode_and_removal_are_exact(self):
        outputs = self.result["generated_output_artifacts"]
        self.assertEqual(outputs["aggregate_report"]["bytes"], 6_946)
        self.assertEqual(
            outputs["aggregate_report"]["sha256"],
            "e76b2ff0c8d74c3d298c0ff83e9ee093e08f3f02e02e1d264543fad749e3890d",
        )
        self.assertEqual(outputs["private_manifest"]["bytes"], 175_618)
        self.assertEqual(outputs["private_manifest"]["mode"], "0600")
        self.assertEqual(
            outputs["private_manifest"]["sha256"],
            "e1b2db1506f94efcc7f85081d9df901349498a8b9a681156d5d37121a887e831",
        )
        self.assertEqual(outputs["combined_bytes"], 182_564)
        self.assertTrue(outputs["temporary_output_directory_removed"])

    def test_selection_and_split_counts_are_exact(self):
        selection = self.result["selection_summary"]
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_selected_run_bundles"], 72)
        self.assertEqual(selection["Freewill_selected_core_members"], 288)
        self.assertEqual(selection["Wrist_selected_archives"], 12)
        self.assertEqual(selection["selected_private_rows"], 300)
        self.assertEqual(selection["Wrist_fit_runs_total"], 72)
        self.assertEqual(selection["Wrist_heldout_runs_total"], 24)
        self.assertEqual(selection["joint_reserved_payload_bytes"], 1_228_139_402)

    def test_runtime_memory_and_output_caps_passed(self):
        measurements = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertEqual(measurements["generated_input_bytes"], 873_348)
        self.assertEqual(measurements["generated_output_bytes"], 182_564)
        self.assertLessEqual(measurements["runtime_seconds"], caps["runtime_seconds"])
        self.assertLessEqual(measurements["peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLessEqual(
            measurements["generated_output_bytes"], caps["combined_output_bytes"]
        )
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)

    def test_all_mutations_and_acceptance_gates_passed(self):
        mutations = self.result["mutation_summary"]
        self.assertEqual(mutations["required_count"], 36)
        self.assertEqual(mutations["passed_count"], 36)
        self.assertEqual(sum(mutations["route_counts"].values()), 36)
        self.assertEqual(len(self.result["acceptance_gates"]), 15)
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_every_real_model_score_and_claim_counter_is_zero(self):
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))
        measurements = self.result["measurements"]
        self.assertEqual(measurements["raw_data_reads"], 0)
        self.assertEqual(measurements["real_cache_reads"], 0)
        self.assertEqual(measurements["model_runs"], 0)
        self.assertEqual(measurements["training_runs"], 0)

    def test_warnings_and_unavailable_fields_preserve_claim_boundary(self):
        self.assertEqual(len(self.result["warnings"]), 5)
        self.assertIn("thought-to-text evidence", self.result["unavailable_fields"])
        self.assertFalse(self.result["claim_boundary"]["scientific_claim_established"])
        self.assertTrue(self.result["research_path"]["same_thought_to_text_path"])
        self.assertFalse(self.result["research_path"]["movement_is_language_evidence"])

    def test_public_result_contains_no_private_identity_or_local_path(self):
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("member_name", serialized)
        self.assertNotIn("archive_name", serialized)
        self.assertNotIn(".codex_work", serialized)
        self.assertNotIn("live_audit_v0", serialized)

    def test_closeout_is_consumed_and_real_selection_remains_closed(self):
        disposition = self.result["disposition"]
        self.assertEqual(disposition["registered_generated_closeout_runs"], 1)
        self.assertTrue(disposition["consumed"])
        self.assertFalse(disposition["retry_or_rerun_authorized"])
        self.assertFalse(disposition["private_Freewill_manifest_read_authorized"])
        self.assertFalse(disposition["public_Wrist_metadata_request_authorized"])
        self.assertTrue(disposition["next_real_operation_requires_Tier_C_decision"])


if __name__ == "__main__":
    unittest.main()
