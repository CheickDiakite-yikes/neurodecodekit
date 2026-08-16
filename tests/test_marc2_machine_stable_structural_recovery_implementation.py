import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc2_machine_stable_structural_recovery_implementation.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_MACHINE_STABLE_STRUCTURAL_RECOVERY_IMPLEMENTATION.md"


class Marc2MachineStableStructuralRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_bounded(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc2_machine_stable_structural_recovery_implementation",
        )
        self.assertEqual(self.registry["lane_id"], "MARC2-VR4")
        self.assertEqual(
            self.registry["status"],
            "generated_and_machine_only_implementation_complete_remote_green_pending",
        )

    def test_registration_proof_is_exact_and_green(self):
        proof = self.registry["green_registration"]
        self.assertEqual(proof["commit"], "3af2e3d654b91c13aefce76e74b38ae19b2a3d6f")
        self.assertEqual(proof["CI_run_id"], 31965823863)
        self.assertEqual(proof["base_python_job_id"], 95210732393)
        self.assertEqual(proof["optional_neuro_job_id"], 95210732329)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_implementation_file_hashes_are_exact(self):
        for record in self.registry["implementation_files"].values():
            payload = (ROOT / record["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), record["sha256"])

    def test_surface_stops_before_private_or_model_work(self):
        surface = self.registry["implemented_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "readiness"])
        self.assertFalse(surface["execute_command"])
        self.assertFalse(surface["private_source_or_output_root_constant"])
        self.assertFalse(
            surface["network_archive_neural_target_model_prediction_or_score_interface"]
        )
        self.assertTrue(surface["standard_library_only"])

    def test_generated_qualification_passed_all_registered_cases(self):
        result = self.registry["generated_qualification"]
        self.assertEqual(result["route"], "MARC2RDY-G1")
        self.assertEqual(result["success_scenarios_passed"], 3)
        self.assertEqual(result["ordered_mutations_refused"], 36)
        self.assertTrue(result["deterministic_replay"])
        self.assertFalse(result["timeout_ready"])
        self.assertEqual(result["retained_generated_output_bytes"], 0)

    def test_measurements_are_within_caps(self):
        result = self.registry["generated_qualification"]
        caps = self.registry["resource_caps"]
        self.assertLess(result["runtime_seconds"], caps["generated_runtime_seconds"])
        self.assertLess(result["peak_RSS_bytes"], caps["peak_RSS_bytes_exclusive"])
        self.assertLessEqual(result["report_bytes"], caps["certificate_bytes"])
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["private_bytes"], 0)

    def test_every_real_or_scientific_counter_is_zero(self):
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))

    def test_next_gate_requires_remote_green_before_machine_closeout(self):
        gate = self.registry["next_gate"]
        self.assertTrue(gate["exact_implementation_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["one_measured_machine_only_readiness_closeout_after_green"])
        self.assertFalse(gate["private_executor_implemented_or_authorized"])
        self.assertFalse(gate["real_cohort_identity_available"])
        self.assertFalse(gate["FW2_or_neural_experiment_eligible"])

    def test_document_separates_engineering_from_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("The current or any earlier `continue` is not", text)


if __name__ == "__main__":
    unittest.main()
