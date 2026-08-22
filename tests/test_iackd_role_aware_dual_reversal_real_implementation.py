import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT
    / "registries"
    / "iackd_role_aware_dual_reversal_real_implementation.v0.json"
)
HISTORICAL_MUTABLE_BINDINGS = {
    "tests/test_iackd_role_aware_dual_reversal_real_implementation.py": (
        "8e9d58aa775276a0a6f6ab0e625a8b24e128b2df55ec4952bcf350869fed63b8"
    ),
    ".github/workflows/ci.yml": (
        "b2dfcf8214b3b5d975e7a432e7c8ff0b6da9b0f1108fcef681cc22310ba50bba"
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKD2RealImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    def test_schema_and_status_are_generated_only(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_role_aware_dual_reversal_real_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["status"],
            "generated_fixture_qualified_exact_real_executor_requires_remote_green_before_public_access",
        )
        self.assertIn("zero_real_or_public", self.record["proof_posture"])

    def test_green_authorization_decision_is_exact(self):
        green = self.record["green_authorization_decision"]
        self.assertEqual(
            green["commit"],
            "2ce87fadcbb1ce3fd90d8fab4a48824b19b9fb59",
        )
        self.assertEqual(green["push_CI_run_id"], 31456317734)
        self.assertEqual(green["base_python_job_id"], 93670726013)
        self.assertEqual(green["optional_neuro_job_id"], 93670725945)
        self.assertTrue(green["both_required_jobs_green"])

    def test_every_tracked_implementation_file_hash_matches(self):
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                if binding["path"] in HISTORICAL_MUTABLE_BINDINGS:
                    self.assertEqual(
                        binding["sha256"], HISTORICAL_MUTABLE_BINDINGS[binding["path"]]
                    )
                else:
                    self.assertEqual(sha256(ROOT / binding["path"]), binding["sha256"])

    def test_exact_optional_environment_and_matrix_are_bound(self):
        self.assertEqual(
            self.record["optional_environment"]["qualified_versions"],
            {
                "mne": "1.12.1",
                "numpy": "2.5.2",
                "scikit_learn": "1.9.0",
                "scipy": "1.18.0",
            },
        )
        matrix = self.record["implemented_interface"]["model_matrix"]
        self.assertEqual(matrix["parameter_update_fits"], 660)
        self.assertEqual(matrix["target_blind_inference_calls"], 900)
        self.assertEqual(matrix["prediction_sets"], 900)
        self.assertEqual(matrix["arms"], ["C2I", "I2C"])
        self.assertFalse(matrix["one_arm_may_rescue_other"])

    def test_stream_and_firewall_match_the_frozen_contract(self):
        stream = self.record["implemented_interface"]["fresh_stream"]
        self.assertEqual(stream["object_count"], 1340)
        self.assertEqual(stream["payload_bytes"], 7249113684)
        self.assertEqual(stream["run_groups"], 128)
        self.assertEqual(stream["largest_run_group_bytes"], 82064564)
        self.assertEqual(stream["maximum_concurrent_raw_run_groups"], 1)
        self.assertTrue(stream["old_retained_bundle_forbidden"])
        firewall = self.record["implemented_interface"]["target_firewall"]
        self.assertEqual(firewall["final_target_rows_visible_to_model"], 0)
        self.assertTrue(firewall["model_and_scorer_directories_separate"])
        self.assertTrue(firewall["green_freeze_required_before_score"])
        self.assertEqual(firewall["post_target_updates"], 0)

    def test_fixture_measurements_and_access_boundary_are_exact(self):
        fixture = self.record["fixture_qualification"]
        self.assertTrue(fixture["all_gates_passed"])
        self.assertEqual(fixture["acceptance_gate_count"], 15)
        self.assertEqual(fixture["generated_input_bytes"], 3257217)
        self.assertEqual(fixture["parameter_update_fits"], 660)
        self.assertEqual(fixture["prediction_sets"], 900)
        self.assertTrue(fixture["deterministic_replay"])
        self.assertEqual(fixture["synthetic_route"], "IACKD2-R5")
        self.assertFalse(fixture["scientific_claim"])
        self.assertEqual(fixture["network_bytes"], 0)
        self.assertEqual(fixture["real_or_public_payload_requests"], 0)
        self.assertEqual(fixture["old_retained_bundle_operations"], 0)
        self.assertLessEqual(fixture["peak_RSS_bytes"], 512 * 1024 * 1024)
        self.assertLessEqual(fixture["output_bytes"], 8 * 1024 * 1024)

    def test_real_resource_caps_and_execution_state_are_closed(self):
        caps = self.record["real_execution_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["concurrent_numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["minimum_free_disk_bytes"], 10 * 1024 * 1024 * 1024)
        self.assertEqual(caps["peak_incremental_disk_bytes"], 1024 * 1024 * 1024)
        self.assertEqual((caps["retries"], caps["reruns"]), (0, 0))
        state = self.record["execution_state"]
        self.assertFalse(state["implementation_commit_remote_green"])
        self.assertFalse(state["public_stream_consumed"])
        self.assertFalse(state["target_blind_analysis_consumed"])
        self.assertFalse(state["prediction_freeze_remote_green"])
        self.assertFalse(state["target_delivery_consumed"])
        self.assertFalse(state["rerun_available"])

    def test_every_implementation_real_access_counter_is_zero(self):
        self.assertTrue(
            all(
                value == 0
                for value in self.record["implementation_real_access_counters"].values()
            )
        )

    def test_document_separates_engineering_and_scientific_claims(self):
        document = (
            ROOT
            / "docs"
            / "IACKD_ROLE_AWARE_DUAL_REVERSAL_REAL_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No mode accepts a path to the old retained bundle", document)
        claim = self.record["claim_boundary"]
        self.assertIn("fresh-stream executor", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
