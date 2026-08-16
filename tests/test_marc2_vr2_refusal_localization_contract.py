import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_vr2_refusal_localization_contract.v0.json"
)


class Marc2Vr2RefusalLocalizationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_upstream_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR5A")
        self.assertEqual(
            self.contract["status"],
            "frozen_artifact_only_contract_implementation_pending",
        )
        proof = self.contract["upstream_closeout_green_proof"]
        self.assertEqual(
            proof["commit"], "0618fc3c62d5dfa308547862209a55c6ba85ed90"
        )
        self.assertEqual(proof["CI_run_id"], 31971716473)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["underlying_VR2_route_available"])

    def test_every_fixed_input_is_committed_scoped_and_hash_bound(self):
        bindings = self.contract["fixed_inputs"]
        self.assertEqual(len(bindings), 11)
        self.assertEqual(len({row["role"] for row in bindings}), 11)
        for binding in bindings:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(".codex_work", binding["path"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    binding["sha256"],
                )

    def test_registered_facts_preserve_the_unknown_predicate_boundary(self):
        facts = self.contract["registered_facts"]
        self.assertEqual(facts["private_source_bytes"], 418755)
        self.assertEqual(facts["published_run_bundles"], 238)
        self.assertEqual(facts["eligible_run_bundles"], 195)
        self.assertEqual(facts["valid_ineligible_run_bundles"], 43)
        self.assertEqual(facts["generated_selected_subjects"], 16)
        self.assertEqual(facts["generated_selected_reservation_bytes"], 8105207776)
        self.assertEqual(
            facts["VR2_nested_routes"],
            [f"MARC2VR2-F{index:02d}" for index in range(1, 9)],
        )
        self.assertTrue(
            self.contract["required_findings"][
                "exact_private_predicate_must_remain_unavailable"
            ]
        )
        self.assertTrue(
            self.contract["required_findings"][
                "observed_nested_route_must_not_be_inferred"
            ]
        )

    def test_prospective_repair_is_dynamic_and_diagnostic_only(self):
        repair = self.contract["prospective_repair"]
        self.assertTrue(repair["preserve_nested_VR2_route_in_aggregate_failure"])
        self.assertFalse(repair["preserve_nested_reason_or_private_value"])
        self.assertTrue(
            repair["real_selection_subject_count_may_vary_within_frozen_12_to_19_bounds"]
        )
        self.assertFalse(
            repair[
                "generated_selected_subject_count_reservation_or_hash_may_be_required_of_real_source"
            ]
        )
        self.assertTrue(repair["real_source_id_and_proof_posture_required"])
        self.assertTrue(
            repair["future_private_read_requires_new_Tier_C_packet_and_decision"]
        )

    def test_authority_and_resources_remain_artifact_only(self):
        authority = self.contract["authorization_state"]
        self.assertTrue(authority["generated_or_artifact_only_implementation"])
        self.assertTrue(authority["committed_artifact_reads"])
        self.assertFalse(any(
            value
            for key, value in authority.items()
            if key not in {
                "generated_or_artifact_only_implementation",
                "committed_artifact_reads",
            }
        ))
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)

    def test_claim_boundary_is_zero(self):
        claim = self.contract["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])
        self.assertFalse(claim["language_or_thought_decoding"])


if __name__ == "__main__":
    unittest.main()
