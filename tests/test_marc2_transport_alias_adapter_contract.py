import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_transport_alias_adapter_contract.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_TRANSPORT_ALIAS_ADAPTER_PREREGISTRATION.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2TransportAliasAdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_only_and_pending(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_transport_alias_adapter_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-TA1")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_adapter_contract_implementation_pending",
        )

    def test_green_lineage_proof_is_exact(self):
        proof = self.contract["green_lineage_proof"]
        self.assertEqual(
            proof["commit"],
            "8c7494812fcfbfa6ea6fd79c1fa119b865df3cb7",
        )
        self.assertEqual(proof["CI_run_id"], 31_932_081_970)
        self.assertEqual(proof["base_python_job_id"], 95_128_350_133)
        self.assertEqual(proof["optional_neuro_job_id"], 95_128_350_179)
        self.assertTrue(proof["both_required_jobs_green_before_registration"])
        self.assertEqual(proof["lineage_route"], "MARC2SL-R2")

    def test_all_fixed_inputs_are_current(self):
        roles = set()
        for binding in self.contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(binding["role"], roles)
                roles.add(binding["role"])
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )
        self.assertEqual(
            roles,
            {"lineage_contract", "lineage_result", "selector_contract", "selector_module"},
        )

    def test_single_alias_and_validation_order_are_exact(self):
        adapter = self.contract["adapter_contract"]
        self.assertEqual(
            adapter["source_transport_keys"], ["directory", "metadata", "tail"]
        )
        self.assertEqual(
            adapter["selector_transport_keys"],
            ["central_directory", "metadata", "tail"],
        )
        self.assertEqual(
            adapter["single_alias"],
            {"source_key": "directory", "selector_key": "central_directory"},
        )
        self.assertTrue(adapter["source_manifest_validated_before_copy_or_mapping"])
        self.assertFalse(adapter["source_object_mutation_allowed"])

    def test_hash_values_and_object_independence_must_be_preserved(self):
        adapter = self.contract["adapter_contract"]
        for field in (
            "source_and_adapted_objects_must_not_alias",
            "metadata_hash_preserved",
            "tail_hash_preserved",
            "directory_hash_preserved_as_central_directory",
            "transport_hash_multiset_preserved",
            "deterministic_replay_required",
        ):
            self.assertTrue(adapter[field], field)

    def test_generated_fixture_contains_no_human_or_scientific_content(self):
        fixture = self.contract["generated_source_manifest"]
        self.assertEqual(fixture["entries"], 1_227)
        self.assertEqual(fixture["regular_file_entries"], 1_025)
        self.assertEqual(fixture["directory_entries"], 202)
        self.assertFalse(fixture["contains_human_content"])
        self.assertFalse(fixture["contains_private_path"])
        self.assertFalse(
            fixture["contains_signal_event_target_label_quality_or_channel"]
        )

    def test_selector_result_is_bound_but_has_no_scientific_value(self):
        result = self.contract["expected_selector_result"]
        self.assertEqual(result["route"], "MARC2FWG-R1")
        self.assertEqual(result["selected_subjects"], 16)
        self.assertEqual(result["selected_run_bundles"], 96)
        self.assertEqual(result["selected_core_members"], 384)
        self.assertEqual(result["selected_reservation_bytes"], 8_105_207_776)
        self.assertFalse(result["scientific_value"])

    def test_mutation_matrix_is_unique_and_complete(self):
        qualification = self.contract["qualification"]
        mutations = qualification["required_mutations"]
        self.assertEqual(len(mutations), qualification["required_mutation_count"])
        self.assertEqual(len(mutations), len(set(mutations)))
        self.assertEqual(
            qualification["required_success_paths"],
            ["canonical_source_order", "reversed_source_entry_order"],
        )
        self.assertFalse(qualification["generated_output_retained"])

    def test_surface_and_resources_remain_small(self):
        surface = self.contract["future_implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command_allowed"])
        self.assertFalse(surface["generic_source_path_or_URL_argument_allowed"])
        self.assertFalse(surface["private_root_or_consumed_executor_import_allowed"])
        self.assertTrue(surface["standard_library_only"])
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["private_or_Git_ignored_bytes"], 0)
        self.assertLessEqual(caps["generated_output_bytes"], 2 * 1024**2)

    def test_every_live_authorization_stays_false(self):
        self.assertTrue(
            all(not value for value in self.contract["authorization_state"].values())
        )
        gate = self.contract["next_gate"]
        self.assertTrue(
            gate["generated_only_implementation_allowed_after_this_registration_is_remotely_green"]
        )
        self.assertFalse(gate["future_live_adapter_or_private_read_allowed"])

    def test_document_preserves_registration_and_claim_boundary(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Frozen generated-only contract", text)
        self.assertIn("does not authorize a live adapter", text)
        self.assertIn("Scientific claim not established", text)
        self.assertNotIn("proves neural", text.lower())


if __name__ == "__main__":
    unittest.main()
