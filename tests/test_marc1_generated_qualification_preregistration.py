import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries" / "marc1_generated_qualification_contract.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1GeneratedQualificationPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_identity_and_status(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc1_generated_qualification_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["contract_id"], "MARC-1-generated-qualification-contract-v0"
        )
        self.assertEqual(
            self.contract["status"],
            "generated_fixture_only_contract_frozen_implementation_not_started",
        )

    def test_artifact_bindings_are_current(self):
        for binding in self.contract["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_research_anchor_is_exact_and_green(self):
        proof = self.contract["green_research_proof"]
        self.assertEqual(
            proof["commit"], "2abea3e2bfa3abb4bc0624579e4a9588c28d96e6"
        )
        self.assertEqual(proof["CI_run_id"], 31_500_649_830)
        self.assertEqual(proof["base_job_id"], 93_809_446_989)
        self.assertEqual(proof["optional_neuro_job_id"], 93_809_446_709)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_cli_has_no_live_execution_surface(self):
        interface = self.contract["interface"]
        self.assertEqual(interface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(interface["execute_command_available"])
        self.assertFalse(interface["URL_argument_available"])
        self.assertFalse(interface["real_archive_path_argument_available"])

    def test_archive_qualification_uses_standard_parser_and_no_members(self):
        archive = self.contract["generated_archive_contract"]
        self.assertEqual(archive["parser"], "python_standard_library_zipfile")
        self.assertEqual(archive["member_count"], 14)
        self.assertEqual(archive["subject_count"], 2)
        self.assertTrue(archive["forced_ZIP64_member_required"])
        self.assertTrue(archive["instrumented_random_access_reader_required"])
        self.assertEqual(archive["member_content_reads"], 0)
        self.assertEqual(archive["member_extractions"], 0)

    def test_archive_caps_are_small(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["generated_archive_bytes"], 8 * 1024 * 1024)
        self.assertEqual(caps["range_bytes_returned"], 8 * 1024 * 1024)
        self.assertEqual(caps["range_read_calls"], 256)
        self.assertEqual(caps["combined_output_bytes"], 1024 * 1024)
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)

    def test_modality_type_role_and_inclusion_are_separate(self):
        roles = self.contract["generated_multimodal_contract"]
        self.assertEqual(
            roles["channel_identity_layers"],
            ["source_type", "functional_role", "model_inclusion"],
        )
        self.assertEqual(
            set(roles["candidate_allowed_source_types"]), {"EEG"}
        )
        self.assertEqual(
            set(roles["always_nonpredictive_source_types"]),
            {"EOG", "EMG", "ACCEL", "ENCODER", "AUDIO", "TRIGGER"},
        )
        self.assertEqual(set(roles["source_profiles"]), {"freewill_like", "wrist_like"})

    def test_causal_window_is_exact(self):
        causal = self.contract["generated_causal_window"]
        self.assertEqual(causal["window_seconds"], [-1.5, -0.2])
        self.assertTrue(causal["right_endpoint_exclusive"])
        self.assertTrue(causal["causal_preprocessing"])
        self.assertEqual(causal["future_context_samples"], 0)
        self.assertEqual(causal["onset_guard_seconds"], 0.2)
        self.assertEqual(causal["normalization"], "fit_rows_only")

    def test_target_firewall_is_physical_and_strict(self):
        firewall = self.contract["generated_target_firewall"]
        self.assertEqual(
            firewall["physical_roles"],
            ["fit_rows", "target_blind_prediction_rows", "isolated_scorer_rows"],
        )
        self.assertTrue(firewall["fit_and_heldout_identities_disjoint"])
        self.assertTrue(firewall["prediction_and_scorer_identities_exact"])
        self.assertFalse(firewall["heldout_targets_in_prediction_rows"])
        self.assertFalse(firewall["window_random_split_allowed"])

    def test_all_twelve_comparator_roles_are_frozen(self):
        comparators = self.contract["comparator_roles"]
        self.assertEqual(len(comparators), 12)
        self.assertEqual(len(set(comparators)), 12)
        self.assertIn("EOG_only_where_available", comparators)
        self.assertIn("pre_onset_EMG_only_where_available", comparators)
        self.assertIn("future_context_sentinel", comparators)

    def test_mutation_inventory_is_exact(self):
        mutations = self.contract["required_mutations"]
        self.assertEqual(len(mutations), 24)
        self.assertEqual(len(set(mutations)), 24)
        self.assertEqual(mutations[0], "truncated_EOCD")
        self.assertEqual(mutations[-1], "output_symlink_overwrite_or_cap")

    def test_router_has_one_generated_success(self):
        router = self.contract["router"]
        self.assertEqual(router["success_route"], "MARC1G-R1")
        self.assertEqual(len(router["ordered_refusal_routes"]), 8)
        self.assertFalse(router["success_route_is_scientific_result"])
        self.assertFalse(router["success_route_authorizes_public_access"])

    def test_all_current_authority_and_counters_are_zero(self):
        for value in self.contract["authorization_flags"].values():
            self.assertFalse(value)
        for value in self.contract["access_counters"].values():
            self.assertEqual(value, 0)

    def test_next_gate_requires_green_contract(self):
        gate = self.contract["next_gate"]
        self.assertTrue(gate["generated_implementation_requires_this_contract_green"])
        self.assertTrue(gate["public_metadata_requires_later_exact_Tier_C_decision"])
        self.assertFalse(gate["real_payload_eligible_after_generated_success"])


if __name__ == "__main__":
    unittest.main()
