import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "registries/marc2_vr6_vr2_boundary_localization_contract.v0.json"
)


class Marc2Vr6Vr2BoundaryLocalizationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_upstream_green_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR8A")
        self.assertEqual(
            self.contract["status"],
            "frozen_artifact_only_contract_implementation_pending",
        )
        proof = self.contract["upstream_closeout_green_proof"]
        self.assertEqual(
            proof["commit"], "5fc1226b3b0a0246b17609d74d741ed20c24ab61"
        )
        self.assertEqual(proof["CI_run_id"], 31983540816)
        self.assertEqual(proof["consumed_wrapper_route"], "MARC2VR7P-F07")
        self.assertEqual(proof["preserved_VR6_route"], "MARC2VR6-F02")
        self.assertFalse(proof["nested_VR2_route_available"])
        self.assertFalse(proof["private_source_reinspection_or_rerun_allowed"])

    def test_every_fixed_input_is_scoped_size_and_hash_bound(self):
        bindings = self.contract["fixed_inputs"]
        self.assertEqual(len(bindings), 17)
        self.assertEqual(len({row["role"] for row in bindings}), 17)
        self.assertEqual(
            sum(row["bytes"] for row in bindings),
            self.contract["registered_facts"]["fixed_input_bytes"],
        )
        for binding in bindings:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(".codex_work", binding["path"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                payload = path.read_bytes()
                self.assertEqual(len(payload), binding["bytes"])
                self.assertEqual(
                    hashlib.sha256(payload).hexdigest(), binding["sha256"]
                )

    def test_registered_schema_facts_preserve_the_unknown_private_boundary(self):
        facts = self.contract["registered_facts"]
        self.assertEqual(facts["private_source_bytes"], 418755)
        self.assertEqual(facts["published_run_bundles"], 238)
        self.assertEqual(facts["eligible_run_bundles"], 195)
        self.assertEqual(facts["valid_ineligible_run_bundles"], 43)
        self.assertEqual(
            facts["producer_manifest_top_level_fields"],
            facts["VR2_source_top_level_fields"],
        )
        self.assertEqual(facts["producer_row_fields"], facts["selector_row_fields"])
        self.assertEqual(facts["producer_transport_keys"], facts["VR2_transport_keys"])
        self.assertEqual(
            facts["VR2_routes"],
            [f"MARC2VR2-F{index:02d}" for index in range(1, 9)],
        )
        required = self.contract["required_findings"]
        self.assertTrue(
            required[
                "exact_private_member_path_participant_run_predicate_and_nested_route_must_remain_unavailable"
            ]
        )
        self.assertTrue(
            required[
                "no_private_value_may_be_reconstructed_from_bytes_hash_runtime_or_failure_class"
            ]
        )

    def test_ordered_routes_distinguish_two_and_three_class_localization(self):
        routes = self.contract["ordered_routes"]
        self.assertEqual(
            [row["route"] for row in routes],
            [
                "MARC2VR8A-R1",
                "MARC2VR8A-R2",
                "MARC2VR8A-R3",
                "MARC2VR8A-F01",
                "MARC2VR8A-F02",
                "MARC2VR8A-F03",
                "MARC2VR8A-F04",
            ],
        )
        self.assertIn("leaving only F03", routes[0]["meaning"])
        self.assertIn("and F04", routes[0]["meaning"])
        self.assertIn("F02 F03 and F04", routes[1]["meaning"])

    def test_prospective_relay_does_not_relax_source_rules(self):
        repair = self.contract["prospective_repair"]
        self.assertTrue(repair["preserve_outer_VR6_route_code"])
        self.assertTrue(repair["preserve_nested_VR2_route_code_when_allowlisted"])
        self.assertFalse(
            repair[
                "preserve_exception_reason_private_value_member_path_participant_or_run"
            ]
        )
        self.assertFalse(
            repair["relax_F03_path_or_companion_rules_before_observed_route"]
        )
        self.assertFalse(
            repair["relax_F04_bundle_taxonomy_or_arithmetic_rules_before_observed_route"]
        )
        self.assertTrue(
            repair[
                "private_read_or_real_cohort_freeze_requires_new_Tier_C_packet_and_decision"
            ]
        )

    def test_authority_resources_and_claims_remain_artifact_only(self):
        authority = self.contract["authorization_state"]
        allowed = {"artifact_only_implementation", "fixed_committed_artifact_reads"}
        self.assertTrue(all(authority[key] for key in allowed))
        self.assertFalse(
            any(value for key, value in authority.items() if key not in allowed)
        )
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["total_input_bytes"], 1024 * 1024)
        self.assertEqual(caps["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        claim = self.contract["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])
        self.assertFalse(claim["language_or_thought_decoding"])


if __name__ == "__main__":
    unittest.main()
