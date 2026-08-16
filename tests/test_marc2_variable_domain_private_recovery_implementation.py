import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_proof_record_recovery as shared_proof
from neurodecodekit.datasets import (
    marc2_variable_domain_private_recovery as recovery,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / recovery.NATIVE_REGISTRY_RELATIVE_PATH
DOC_PATH = ROOT / "docs/MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_IMPLEMENTATION.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2VariableDomainPrivateRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_wrapper_remote_proof_pending(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_variable_domain_private_recovery_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-VR3")
        self.assertEqual(
            self.record["status"],
            "generated_mock_wrapper_qualified_remote_green_required_before_private_pass",
        )
        self.assertIsNone(self.record["implementation_remote_proof"])

    def test_green_decision_proof_is_exact(self):
        proof = self.record["green_decision_proof"]
        self.assertEqual(proof["commit"], recovery.DECISION_COMMIT)
        self.assertEqual(proof["CI_run_id"], recovery.DECISION_CI_RUN_ID)
        self.assertEqual(proof["base_python_job_id"], recovery.DECISION_BASE_JOB_ID)
        self.assertEqual(
            proof["optional_neuro_job_id"], recovery.DECISION_OPTIONAL_JOB_ID
        )
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_every_tracked_implementation_hash_matches(self):
        seen = set()
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(binding["path"], seen)
                seen.add(binding["path"])
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )
        self.assertGreaterEqual(len(seen), 14)
        self.assertNotIn(recovery.NATIVE_REGISTRY_RELATIVE_PATH.as_posix(), seen)
        self.assertNotIn(recovery.PROOF_CERTIFICATE_RELATIVE_PATH.as_posix(), seen)

    def test_certificate_is_distinct_and_passes_exact_shared_validator(self):
        certificate = recovery._load_certificate_bytes(ROOT)
        certificate_record = shared_proof.parse_record_bytes(certificate)
        self.assertEqual(certificate_record["lane_id"], "MARC2-FW1B")
        self.assertNotEqual(certificate_record["lane_id"], self.record["lane_id"])
        recovery._validate_certificate_generated(ROOT, certificate)
        binding_paths = {
            binding["path"] for binding in certificate_record["tracked_file_hashes"]
        }
        self.assertIn(recovery.NATIVE_REGISTRY_RELATIVE_PATH.as_posix(), binding_paths)
        self.assertNotIn(recovery.PROOF_CERTIFICATE_RELATIVE_PATH.as_posix(), binding_paths)

    def test_surface_is_fixed_standard_library_and_target_free(self):
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["module"], recovery.MODULE_NAME)
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(surface["exact_shared_validator_import_and_call"])
        self.assertTrue(surface["exact_VR2_adapter_import_and_call"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertFalse(surface["generic_source_or_output_override"])
        self.assertFalse(surface["network_or_download_client"])
        self.assertFalse(surface["archive_member_or_neural_reader"])
        self.assertFalse(surface["model_training_prediction_or_score_interface"])

    def test_generated_qualification_covers_all_paths_and_mutations(self):
        qualification = self.record["generated_qualification"]
        self.assertEqual(qualification["route"], "MARC2VDR-G1")
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(qualification["success_profiles"], 4)
        self.assertEqual(qualification["row_orders_per_profile"], 2)
        self.assertEqual(qualification["success_paths"], 8)
        self.assertEqual(qualification["proof_certificate_mutations_passed"], 32)
        self.assertEqual(qualification["wrapper_mutations_passed"], 32)
        self.assertEqual(qualification["total_direct_mutations_passed"], 64)
        self.assertEqual(
            qualification["wrapper_mutation_order"], list(recovery.WRAPPER_MUTATIONS)
        )
        self.assertEqual(
            set(qualification["wrapper_route_counts"]), set(recovery.REFUSAL_ROUTES)
        )
        self.assertEqual(qualification["selected_subjects"], 16)
        self.assertEqual(qualification["selected_run_bundles"], 96)
        self.assertEqual(qualification["selected_core_members"], 384)

    def test_generated_measurements_and_resources_are_bounded(self):
        qualification = self.record["generated_qualification"]
        self.assertLess(qualification["runtime_seconds"], recovery.MAX_RUNTIME_SECONDS)
        self.assertLess(qualification["peak_RSS_bytes"], recovery.MAX_PEAK_RSS_BYTES)
        self.assertLess(
            qualification["aggregate_output_bytes"],
            recovery.MAX_COMBINED_OUTPUT_BYTES,
        )
        self.assertEqual(qualification["CPU_threads"], 1)
        self.assertEqual(qualification["workers"], 1)
        self.assertEqual(qualification["numerical_jobs"], 1)
        self.assertFalse(qualification["end_to_end_latency_measured"])
        self.assertEqual(
            qualification["producer_is_causal"],
            "not_applicable_structural_metadata_only",
        )
        self.assertTrue(qualification["temporary_output_removed"])

    def test_all_authority_and_real_access_remain_zero(self):
        self.assertTrue(
            all(not value for value in self.record["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.record["access_counters"].values())
        )
        gate = self.record["next_gate"]
        self.assertTrue(gate["exact_commit_push_and_both_remote_jobs_green_required"])
        self.assertFalse(gate["private_manifest_access_authorized_before_green"])
        self.assertTrue(gate["one_private_structural_pass_after_green"])
        self.assertFalse(gate["archive_member_or_payload_access_after_success"])
        self.assertFalse(gate["MARC2_FW2_execution_authorized"])

    def test_local_verification_and_known_monolithic_context_are_explicit(self):
        verification = self.record["local_verification"]
        self.assertGreaterEqual(verification["focused_tests"], 40)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compile_passed"])
        self.assertTrue(verification["all_registry_JSON_passed"])
        self.assertTrue(verification["complete_repository_split_passed"])
        self.assertTrue(verification["remote_CI_pending"])

    def test_document_separates_engineering_and_scientific_boundaries(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("This is not the private structural pass", text)
        self.assertIn("No archive member", text)


if __name__ == "__main__":
    unittest.main()
