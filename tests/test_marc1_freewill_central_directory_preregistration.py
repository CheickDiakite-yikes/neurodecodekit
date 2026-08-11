import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries" / "marc1_freewill_central_directory_contract.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1FreewillCentralDirectoryPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc1_freewill_central_directory_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["contract_id"],
            "MARC-1-freewill-central-directory-generated-contract-v0",
        )
        self.assertEqual(
            self.contract["status"],
            "generated_mock_only_contract_frozen_implementation_not_started",
        )

    def test_artifact_bindings_are_current(self):
        for binding in self.contract["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_research_anchor_is_exact_and_green(self):
        proof = self.contract["green_research_proof"]
        self.assertEqual(
            proof["commit"], "93faf368ed01dda418b836e794ba354d8f180794"
        )
        self.assertEqual(proof["CI_run_id"], 31_507_965_329)
        self.assertEqual(proof["base_job_id"], 93_834_276_391)
        self.assertEqual(proof["optional_neuro_job_id"], 93_834_276_150)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_interface_has_no_live_surface(self):
        interface = self.contract["interface"]
        self.assertEqual(interface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(interface["execute_command_available"])
        self.assertFalse(interface["URL_or_host_argument_available"])
        self.assertFalse(interface["real_archive_path_argument_available"])
        self.assertFalse(interface["network_opener_available"])

    def test_virtual_archive_does_not_allocate_monolith(self):
        fixture = self.contract["generated_virtual_archive"]
        self.assertEqual(fixture["virtual_archive_bytes"], 13_591_548_048)
        self.assertEqual(fixture["materialized_whole_archive_bytes"], 0)
        self.assertEqual(fixture["tail_bytes"], 128 * 1024)
        self.assertEqual(fixture["entry_count"], 18)
        self.assertEqual(fixture["directory_count"], 4)
        self.assertEqual(fixture["regular_file_count"], 14)
        self.assertTrue(fixture["decoy_EOCD_signature_in_comment"])

    def test_mock_transport_is_exact_and_bounded(self):
        transport = self.contract["mock_transport"]
        self.assertEqual(transport["response_body_count"], 3)
        self.assertEqual(transport["maximum_redirect_count"], 2)
        self.assertEqual(transport["redirect_body_bytes"], 0)
        self.assertEqual(transport["archive_terminal_status"], 206)
        self.assertTrue(transport["exact_Content_Range_required"])
        self.assertTrue(transport["cap_plus_one_read_required"])
        self.assertFalse(transport["real_network_surface_available"])

    def test_structural_parsers_are_dependency_free(self):
        trailer = self.contract["trailer_parser"]
        directory = self.contract["central_directory_parser"]
        self.assertEqual(trailer["parser"], "stdlib_struct_and_bounded_slices")
        self.assertEqual(directory["parser"], "stdlib_struct_and_bounded_slices")
        self.assertTrue(trailer["complete_ZIP64_record_inside_tail_required"])
        self.assertFalse(trailer["additional_ZIP64_probe_available"])
        self.assertEqual(directory["maximum_bytes"], 16 * 1024 * 1024)
        self.assertEqual(directory["maximum_entries"], 250_000)

    def test_member_rules_preserve_private_inventory(self):
        members = self.contract["member_policy"]
        self.assertEqual(set(members["allowed_kinds"]), {"regular_file", "directory"})
        self.assertEqual(set(members["allowed_compression_methods"]), {0, 8})
        self.assertFalse(members["encrypted_or_special_entries_allowed"])
        self.assertTrue(members["safe_POSIX_relative_NFC_names_required"])
        self.assertFalse(members["public_names_offsets_or_checksums_allowed"])

    def test_exact_mutation_inventory_is_frozen(self):
        mutations = self.contract["required_mutations"]
        self.assertEqual(len(mutations), 32)
        self.assertEqual(len(set(mutations)), 32)
        self.assertEqual(mutations[0], "contract_or_artifact_hash_mismatch")
        self.assertEqual(
            mutations[-1], "output_symlink_overwrite_cap_or_replay_mismatch"
        )

    def test_router_has_one_generated_success(self):
        router = self.contract["router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 7)
        self.assertEqual(router["success_route"], "MARC1CDG-R1")
        self.assertFalse(router["success_is_scientific_result"])
        self.assertFalse(router["success_authorizes_live_audit"])

    def test_resources_are_small_and_one_threaded(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(caps["generated_fixture_bytes"], 2 * 1024 * 1024)
        self.assertEqual(caps["combined_output_bytes"], 1024 * 1024)
        self.assertEqual(caps["network_requests"], 0)

    def test_acceptance_requires_no_member_or_real_operations(self):
        gates = self.contract["acceptance_gates"]
        self.assertIn("zero_local_header_and_member_content_reads", gates)
        self.assertIn("all_32_mutations_refused", gates)
        self.assertIn("all_live_real_model_score_and_claim_counters_zero", gates)

    def test_all_current_authority_and_counters_are_zero(self):
        for value in self.contract["authorization_flags"].values():
            self.assertFalse(value)
        for value in self.contract["access_counters"].values():
            self.assertEqual(value, 0)

    def test_next_gate_requires_green_contract_and_implementation(self):
        gate = self.contract["next_gate"]
        self.assertTrue(gate["generated_implementation_requires_contract_green"])
        self.assertTrue(gate["generated_closeout_requires_implementation_green"])
        self.assertTrue(gate["live_audit_requires_later_exact_Tier_C_decision"])
        self.assertFalse(gate["real_member_acquisition_eligible_after_generated_success"])


if __name__ == "__main__":
    unittest.main()
