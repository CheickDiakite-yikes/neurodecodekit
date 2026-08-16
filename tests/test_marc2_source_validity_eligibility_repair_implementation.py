import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc2_source_validity_eligibility_repair_implementation.v0.json"
)
DOC_PATH = (
    ROOT
    / "docs"
    / "MARC_2_SOURCE_VALIDITY_ELIGIBILITY_REPAIR_IMPLEMENTATION.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2SourceValidityEligibilityRepairImplementationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_only_and_remote_proof_is_pending(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc2_source_validity_eligibility_repair_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC2-VR1")
        self.assertEqual(
            self.registry["status"],
            "generated_implementation_ready_remote_proof_pending",
        )
        remote = self.registry["implementation_remote_proof"]
        self.assertTrue(remote["pending"])
        self.assertFalse(remote["both_required_jobs_green"])
        self.assertIsNone(remote["commit"])

    def test_green_registration_proof_is_exact(self):
        proof = self.registry["green_registration_proof"]
        self.assertEqual(
            proof["commit"],
            "9dedfe6f649b7f8044598c7047ddeadcd9bfab76",
        )
        self.assertEqual(proof["CI_run_id"], 31_942_316_544)
        self.assertEqual(proof["base_python_job_id"], 95_153_164_447)
        self.assertEqual(proof["optional_neuro_job_id"], 95_153_164_463)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_every_tracked_file_hash_is_current(self):
        for binding in self.registry["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )

    def test_surface_is_generated_only_and_dependency_free(self):
        surface = self.registry["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command_available"])
        self.assertFalse(surface["generic_source_path_or_URL_available"])
        self.assertFalse(surface["private_root_output_root_or_consumed_executor_available"])
        self.assertFalse(surface["network_or_archive_reader_available"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)

    def test_full_source_domain_and_adversaries_are_exact(self):
        domain = self.registry["generated_source_domain"]
        self.assertEqual(domain["inventory_rows"], 1_227)
        self.assertEqual(domain["complete_source_run_bundles"], 238)
        self.assertEqual(domain["complete_source_companion_rows"], 952)
        self.assertEqual(domain["eligible_run_bundles_after_filter"], 195)
        self.assertEqual(domain["source_valid_but_ineligible_run_bundles"], 43)
        self.assertEqual(domain["source_valid_but_ineligible_companion_rows"], 172)
        self.assertFalse(domain["contains_real_or_private_bytes"])

    def test_filter_order_and_frozen_selection_are_exact(self):
        selection = self.registry["validation_and_selection"]
        self.assertTrue(selection["full_source_validated_before_eligibility_classification"])
        self.assertTrue(selection["all_238_companion_groups_validated_before_filter"])
        self.assertFalse(selection["global_195_bundle_assertion_before_filter"])
        self.assertTrue(selection["exact_195_bundle_assertion_after_filter"])
        self.assertEqual(selection["selected_subjects"], 16)
        self.assertEqual(selection["selected_run_bundles"], 96)
        self.assertEqual(selection["selected_core_members"], 384)
        self.assertEqual(selection["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(selection["ineligible_selected_bundles"], 0)

    def test_all_registered_mutations_refuse_across_all_routes(self):
        preflight = self.registry["generated_adversarial_preflight"]
        self.assertEqual(preflight["registered_mutations"], 36)
        self.assertEqual(preflight["refused_mutations"], 36)
        self.assertTrue(preflight["all_eight_refusal_routes_exercised"])
        self.assertEqual(
            set(preflight["route_counts"]),
            {f"MARC2VR-F{index:02d}" for index in range(1, 9)},
        )
        self.assertFalse(preflight["registered_measured_closeout_executed"])

    def test_authority_and_access_remain_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.registry["access_counters"].values())
        )
        self.assertTrue(
            all(not value for value in self.registry["authorization_state"].values())
        )
        gate = self.registry["next_gate"]
        self.assertTrue(gate["commit_push_and_both_remote_jobs_green_required"])
        self.assertFalse(
            gate["registered_measured_generated_closeout_allowed_before_remote_green"]
        )
        self.assertFalse(gate["private_read_or_real_executor_allowed"])
        self.assertTrue(gate["future_private_read_requires_fresh_Tier_C_decision"])

    def test_document_and_claim_boundary_are_explicit(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("No global 195-bundle assertion", text)
        self.assertIn("single measured generated qualification", text)
        self.assertIn("Scientific claim not established", text)
        boundary = self.registry["claim_boundary"]
        self.assertIn("validates all 238", boundary["engineering"])
        self.assertIn("No private archive", boundary["scientific_not_established"])


if __name__ == "__main__":
    unittest.main()
