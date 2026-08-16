import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_live_schema_adapter_contract.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_LIVE_SCHEMA_ADAPTER_PREREGISTRATION.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveSchemaAdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_mock_only_and_pending(self):
        self.assertEqual(self.contract["schema_name"], "neurodecodekit.marc2_live_schema_adapter_contract")
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-LA1")
        self.assertEqual(self.contract["status"], "frozen_generated_mock_live_schema_adapter_contract_implementation_pending")

    def test_green_adapter_proof_is_exact(self):
        proof = self.contract["green_adapter_proof"]
        self.assertEqual(proof["commit"], "108b869a6199b6d3aa2d87f8a59b6d8bee0c847b")
        self.assertEqual(proof["CI_run_id"], 31_933_692_066)
        self.assertEqual(proof["base_python_job_id"], 95_132_260_089)
        self.assertEqual(proof["optional_neuro_job_id"], 95_132_260_076)
        self.assertTrue(proof["both_required_jobs_green_before_registration"])

    def test_all_fixed_inputs_are_current_and_unique(self):
        roles = set()
        for binding in self.contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(binding["role"], roles)
                roles.add(binding["role"])
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])
        self.assertEqual(len(roles), 8)

    def test_generated_source_has_exact_live_envelope_without_real_bytes(self):
        source = self.contract["generated_live_shaped_source"]
        self.assertEqual(source["proof_posture"], "live_archive_private_central_directory_metadata_only")
        self.assertEqual(source["source_identity"]["provider"], "Figshare")
        self.assertEqual(source["source_identity"]["file_id"], 57_518_986)
        self.assertEqual(source["transport_keys"], ["directory", "metadata", "tail"])
        self.assertEqual(source["entries"], 1_227)
        self.assertFalse(source["contains_human_content"])
        self.assertFalse(source["contains_private_path"])
        self.assertFalse(source["contains_real_or_private_bytes"])

    def test_bridge_changes_only_four_identity_values(self):
        bridge = self.contract["identity_bridge"]
        self.assertTrue(bridge["live_envelope_validated_before_copy_or_bridge"])
        self.assertEqual(bridge["changed_values"], ["proof_posture", "source_identity.provider", "source_identity.file_id", "source_identity.registered_MD5"])
        self.assertEqual(bridge["green_public_adapter_function"], "adapt_generated_source")
        self.assertEqual(bridge["green_public_adapter_calls_per_success_path"], 1)
        self.assertTrue(bridge["transport_alias_mapping_inside_green_adapter_only"])
        self.assertFalse(bridge["source_object_mutation_allowed"])

    def test_expected_selector_result_is_exact_and_non_scientific(self):
        result = self.contract["expected_selector_result"]
        self.assertEqual(result["selected_subjects"], 16)
        self.assertEqual(result["selected_run_bundles"], 96)
        self.assertEqual(result["selected_core_members"], 384)
        self.assertEqual(result["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(result["selection_identity_sha256"], "dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641")
        self.assertFalse(result["scientific_value"])

    def test_mutation_matrix_is_unique_and_complete(self):
        qualification = self.contract["qualification"]
        mutations = qualification["required_mutations"]
        self.assertEqual(len(mutations), 30)
        self.assertEqual(len(mutations), qualification["required_mutation_count"])
        self.assertEqual(len(mutations), len(set(mutations)))
        self.assertEqual(qualification["required_success_paths"], ["canonical_source_order", "reversed_source_entry_order"])
        self.assertFalse(qualification["generated_output_retained"])

    def test_surface_has_no_live_or_private_interface(self):
        surface = self.contract["future_implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command_allowed"])
        self.assertFalse(surface["generic_source_path_or_URL_argument_allowed"])
        self.assertFalse(surface["private_root_output_root_or_consumed_executor_interface_allowed"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)

    def test_resources_are_small_and_every_authority_flag_is_false(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["private_or_Git_ignored_bytes"], 0)
        self.assertLessEqual(caps["generated_output_bytes"], 2 * 1024**2)
        self.assertTrue(all(not value for value in self.contract["authorization_state"].values()))

    def test_next_gate_requires_green_generated_proof_then_fresh_authority(self):
        gate = self.contract["next_gate"]
        self.assertTrue(gate["generated_mock_implementation_allowed_after_this_registration_is_remotely_green"])
        self.assertFalse(gate["private_read_or_live_executor_allowed"])
        self.assertTrue(gate["all_false_Tier_C_packet_allowed_only_after_green_generated_implementation"])
        self.assertTrue(gate["fresh_packet_bound_maintainer_authority_required_before_live_executor_work"])

    def test_document_preserves_gate_and_claim_boundary(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Frozen generated/mock contract", text)
        self.assertIn("Stop for fresh packet-bound maintainer authority", text)
        self.assertIn("Scientific claim not established", text)
        self.assertNotIn("proves neural", text.lower())


if __name__ == "__main__":
    unittest.main()
