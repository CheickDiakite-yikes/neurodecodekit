import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries" / "marc2_live_domain_eligibility_adapter_contract.v0.json"
)
DOC_PATH = (
    ROOT / "docs" / "MARC_2_LIVE_DOMAIN_ELIGIBILITY_ADAPTER_PREREGISTRATION.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveDomainEligibilityAdapterPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_only_and_implementation_pending(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_live_domain_eligibility_adapter_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR2")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_contract_implementation_pending",
        )

    def test_green_VR1_closeout_proof_is_exact(self):
        proof = self.contract["green_VR1_closeout_proof"]
        self.assertEqual(
            proof["proof_addendum_commit"],
            "f70d54923c5a0443ee179d6d580aafde94250589",
        )
        self.assertEqual(proof["CI_run_id"], 31_944_164_607)
        self.assertEqual(proof["base_python_job_id"], 95_157_571_747)
        self.assertEqual(proof["optional_neuro_job_id"], 95_157_571_692)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["VR1_route"], "MARC2VR-G1")

    def test_all_fixed_inputs_and_registration_artifacts_are_hash_bound(self):
        roles = set()
        for binding in self.contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(binding["role"], roles)
                roles.add(binding["role"])
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )
        self.assertEqual(len(roles), 9)
        registration = self.contract["registration_artifacts"]
        self.assertEqual(sha256_file(DOC_PATH), registration["document_sha256"])
        self.assertEqual(
            sha256_file(Path(__file__)), registration["invariant_test_sha256"]
        )

    def test_live_shape_and_source_totals_are_exact(self):
        source = self.contract["generated_live_source_domain"]
        self.assertEqual(source["inventory_rows"], 1_227)
        self.assertEqual(source["regular_file_rows"], 1_025)
        self.assertEqual(source["directory_rows"], 202)
        self.assertEqual(source["complete_source_run_bundles"], 238)
        self.assertEqual(source["eligible_run_bundles_after_filter"], 195)
        self.assertEqual(source["valid_ineligible_run_bundles"], 43)
        self.assertEqual(
            set(source["transport_keys"]), {"metadata", "tail", "directory"}
        )
        self.assertFalse(source["contains_real_or_private_bytes"])

    def test_participant_taxonomy_is_disjoint_and_complete(self):
        taxonomy = self.contract["participant_taxonomy"]
        eligible = set(taxonomy["eligible_subject_ids"])
        single = set(taxonomy["single_session_exclusions"])
        sampling = set(taxonomy["sampling_tier_exclusions"])
        self.assertEqual(len(eligible), 19)
        self.assertEqual(single, {"sub-02", "sub-17"})
        self.assertEqual(sampling, {"sub-13", "sub-15"})
        self.assertFalse(eligible & single)
        self.assertFalse(eligible & sampling)
        self.assertFalse(single & sampling)
        self.assertEqual(len(eligible | single | sampling), 23)

    def test_ineligible_breakdown_varies_across_four_success_profiles(self):
        profiles = self.contract["generated_success_profiles"]
        self.assertEqual(set(profiles), {"A", "B", "C", "D"})
        observed = []
        for name, counts in profiles.items():
            with self.subTest(profile=name):
                triple = [counts[code] for code in ("MARC2VR2-P02", "MARC2VR2-P03", "MARC2VR2-P04")]
                self.assertEqual(sum(triple), 43)
                observed.append(tuple(triple))
        self.assertEqual(len(set(observed)), 4)
        self.assertFalse(self.contract["live_acceptance"]["exact_ineligible_breakdown_frozen"])

    def test_validation_filters_before_exact_eligible_assertion(self):
        order = self.contract["ordered_validation"]
        self.assertLess(
            order.index("classify_all_complete_bundles_by_public_taxonomy"),
            order.index("filter_to_eligible_participants_and_sessions"),
        )
        self.assertLess(
            order.index("filter_to_eligible_participants_and_sessions"),
            order.index("assert_exact_195_eligible_bundles_and_public_counts"),
        )
        self.assertFalse(
            self.contract["live_acceptance"]["global_195_assertion_before_filter_allowed"]
        )

    def test_selection_refusals_and_mutation_floor_are_frozen(self):
        expected = self.contract["expected_selection"]
        self.assertEqual(expected["selected_subjects"], 16)
        self.assertEqual(expected["selected_run_bundles"], 96)
        self.assertEqual(expected["selected_core_members"], 384)
        self.assertEqual(expected["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(expected["ineligible_selected_bundles"], 0)
        routes = self.contract["ordered_routes"]
        self.assertEqual(routes[0]["route"], "MARC2VR2-G1")
        self.assertEqual(
            [row["route"] for row in routes[1:]],
            [f"MARC2VR2-F{index:02d}" for index in range(1, 9)],
        )
        mutations = self.contract["qualification"]["required_mutations"]
        self.assertGreaterEqual(len(mutations), 44)
        self.assertEqual(len(mutations), len(set(mutations)))

    def test_surface_resources_and_authority_are_bounded(self):
        surface = self.contract["future_implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command_allowed"])
        self.assertFalse(surface["generic_path_or_URL_argument_allowed"])
        self.assertTrue(surface["standard_library_only"])
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertTrue(
            all(not value for value in self.contract["authorization_state"].values())
        )

    def test_next_gate_and_document_preserve_claim_boundary(self):
        gate = self.contract["next_gate"]
        self.assertTrue(gate["generated_implementation_allowed_after_registration_green"])
        self.assertFalse(gate["private_read_or_real_executor_allowed"])
        self.assertTrue(gate["future_private_read_requires_fresh_Tier_C_decision"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Variable Breakdown", text)
        self.assertIn("No global 195-bundle assertion", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
