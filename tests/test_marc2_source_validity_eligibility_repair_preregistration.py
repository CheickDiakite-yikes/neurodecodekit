import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "registries"
    / "marc2_source_validity_eligibility_repair_contract.v0.json"
)
DOC_PATH = (
    ROOT
    / "docs"
    / "MARC_2_SOURCE_VALIDITY_ELIGIBILITY_REPAIR_PREREGISTRATION.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2SourceValidityEligibilityRepairPreregistrationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_only_and_pending(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_source_validity_eligibility_repair_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR1")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_contract_implementation_pending",
        )

    def test_green_localization_proof_is_exact(self):
        proof = self.contract["green_localization_proof"]
        self.assertEqual(
            proof["commit"],
            "953692f368fbabae71601a7572804a68c755f44a",
        )
        self.assertEqual(proof["CI_run_id"], 31_941_668_496)
        self.assertEqual(proof["base_python_job_id"], 95_151_661_005)
        self.assertEqual(proof["optional_neuro_job_id"], 95_151_660_910)
        self.assertTrue(proof["both_required_jobs_green_before_registration"])

    def test_every_fixed_input_and_registration_artifact_is_hash_bound(self):
        roles = set()
        for binding in self.contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(binding["role"], roles)
                roles.add(binding["role"])
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )
        self.assertEqual(len(roles), 6)
        artifacts = self.contract["registration_artifacts"]
        self.assertEqual(sha256_file(DOC_PATH), artifacts["document_sha256"])
        self.assertEqual(
            sha256_file(Path(__file__)), artifacts["invariant_test_sha256"]
        )

    def test_generated_domain_arithmetic_is_exact(self):
        source = self.contract["generated_source_domain"]
        self.assertEqual(source["inventory_rows"], 1_227)
        self.assertEqual(source["regular_file_rows"], 1_025)
        self.assertEqual(source["directory_rows"], 202)
        self.assertEqual(source["complete_source_run_bundles"], 238)
        self.assertEqual(source["complete_source_companion_rows"], 952)
        self.assertEqual(source["generic_auxiliary_regular_rows"], 73)
        self.assertEqual(
            source["complete_source_companion_rows"]
            + source["generic_auxiliary_regular_rows"],
            source["regular_file_rows"],
        )

    def test_all_43_adversaries_are_source_shaped_and_classified(self):
        matrix = self.contract["generated_adversary_matrix"]
        families = matrix["families"]
        self.assertEqual([row["bundle_count"] for row in families], [12, 24, 7])
        self.assertEqual(sum(row["bundle_count"] for row in families), 43)
        self.assertEqual(matrix["required_companions_per_bundle"], 4)
        self.assertEqual(matrix["adversary_companion_rows"], 172)
        self.assertTrue(matrix["every_adversary_is_Freewill_shaped"])
        self.assertFalse(matrix["claims_exact_private_or_published_assignment"])

    def test_validation_filters_before_exact_eligible_count(self):
        order = self.contract["ordered_validation"]
        self.assertLess(
            order.index("classify_source_valid_bundle_eligibility"),
            order.index("filter_to_frozen_participants_and_sessions"),
        )
        self.assertLess(
            order.index("filter_to_frozen_participants_and_sessions"),
            order.index("assert_exact_195_eligible_run_bundles"),
        )
        self.assertFalse(
            self.contract["eligibility_policy"][
                "global_195_group_assertion_before_filter_allowed"
            ]
        )

    def test_predicate_counts_and_selector_result_are_exact(self):
        self.assertEqual(
            self.contract["expected_predicate_counts"],
            {
                "MARC2VR-P01": 195,
                "MARC2VR-P02": 12,
                "MARC2VR-P03": 24,
                "MARC2VR-P04": 7,
            },
        )
        expected = self.contract["expected_selection"]
        self.assertEqual(expected["selected_subjects"], 16)
        self.assertEqual(expected["selected_run_bundles"], 96)
        self.assertEqual(expected["selected_core_members"], 384)
        self.assertEqual(expected["fit_run_bundles"], 48)
        self.assertEqual(expected["heldout_run_bundles"], 48)
        self.assertEqual(expected["selected_reservation_bytes"], 8_105_207_776)

    def test_refusals_mutations_and_output_firewall_are_complete(self):
        routes = self.contract["ordered_routes"]
        self.assertEqual(len(routes), 9)
        self.assertEqual(routes[0]["route"], "MARC2VR-G1")
        self.assertEqual(
            [row["route"] for row in routes[1:]],
            [f"MARC2VR-F{index:02d}" for index in range(1, 9)],
        )
        mutations = self.contract["qualification"]["required_mutations"]
        self.assertEqual(len(mutations), 36)
        self.assertEqual(len(mutations), len(set(mutations)))
        self.assertTrue(
            self.contract["predicate_output_firewall"][
                "aggregate_counts_only"
            ]
        )

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
        self.assertEqual(caps["private_or_Git_ignored_bytes"], 0)
        self.assertTrue(
            all(not value for value in self.contract["authorization_state"].values())
        )

    def test_next_gate_and_document_preserve_claim_boundary(self):
        gate = self.contract["next_gate"]
        self.assertTrue(
            gate[
                "generated_implementation_allowed_after_registration_remote_green"
            ]
        )
        self.assertFalse(gate["private_read_or_real_executor_allowed"])
        self.assertTrue(gate["future_private_read_requires_fresh_Tier_C_decision"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Frozen generated-only contract", text)
        self.assertIn("No global 195-bundle assertion", text)
        self.assertIn("Scientific claim not established", text)
        self.assertNotIn("proves neural", text.lower())


if __name__ == "__main__":
    unittest.main()
