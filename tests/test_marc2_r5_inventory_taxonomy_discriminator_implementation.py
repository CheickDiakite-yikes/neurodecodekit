import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_r5_inventory_taxonomy_discriminator_implementation.v0.json"
)
RESULT_PATH = (
    ROOT / "registries/marc2_r5_inventory_taxonomy_discriminator_result.v0.json"
)


class Marc2R5InventoryTaxonomyDiscriminatorImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_registration_proof_is_exact_and_green(self):
        proof = self.implementation["registration_proof"]
        self.assertEqual(
            proof["commit"], "47ceba3ed89df9610540fe3ed2ee8071ac1b84df"
        )
        self.assertEqual(proof["CI_run_id"], 32_611_101_033)
        self.assertEqual(proof["base_job_id"], 97_124_216_923)
        self.assertEqual(proof["optional_neuro_job_id"], 97_124_216_871)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_implementation_artifacts_are_byte_exact(self):
        artifacts = self.implementation["implementation_artifacts"]
        self.assertEqual(len(artifacts), 4)
        self.assertEqual(
            sum(item["bytes"] for item in artifacts),
            self.implementation["implementation_artifact_bytes"],
        )
        for item in artifacts:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(payload), item["bytes"], item["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                item["sha256"],
                item["path"],
            )

    def test_generated_result_matches_frozen_matrix(self):
        generated = self.implementation["generated_qualification"]
        self.assertEqual(generated["route"], "MARC2VR27A-G1")
        self.assertEqual(generated["paths"], 20)
        self.assertEqual(generated["VR25A_calls"], 20)
        self.assertEqual(
            generated["VR27A_route_counts"],
            {
                "MARC2VR27A-G1": 4,
                "MARC2VR27A-R1": 12,
                "MARC2VR27A-R2": 4,
            },
        )
        self.assertEqual(generated["direct_refusals_passed"], 57)
        self.assertTrue(generated["exact_replays_match"])
        self.assertEqual(generated["source_mutations_after_call"], 0)
        self.assertEqual(self.result["matrix"], {
            "cases": [
                "exact_public_control",
                "eligible_bundle_removed",
                "eligible_bundle_added",
                "eligible_distribution_shift",
                "unknown_participant_bundle",
            ],
            "orders": ["canonical", "reversed"],
            "replays": 2,
            "paths": 20,
            "VR25A_calls": 20,
            "VR27A_route_counts": generated["VR27A_route_counts"],
            "VR25A_route_counts": generated["VR25A_route_counts"],
            "direct_refusals_passed": 57,
            "exact_replays_match": True,
            "order_invariant_route_distribution": True,
            "replay_digest": generated["replay_digest"],
            "source_mutations_after_call": 0,
        })

    def test_measurements_obey_caps_and_counters_are_zero(self):
        measured = self.implementation["measurements"]
        self.assertLessEqual(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_output_bytes"], 0)
        self.assertEqual(measured, self.result["measurements"])
        self.assertTrue(
            all(
                value == 0
                for value in self.implementation["operation_counters"].values()
            )
        )
        self.assertEqual(
            self.implementation["operation_counters"],
            self.result["operation_counters"],
        )

    def test_remote_proof_and_scientific_claims_remain_closed(self):
        barrier = self.implementation["proof_barrier"]
        self.assertIsNone(barrier["remote_implementation_proof"])
        self.assertFalse(barrier["private_executor_available"])
        self.assertIsNone(self.result["remote_implementation_proof"])
        for record in (self.implementation, self.result):
            boundary = record["claim_boundary"]
            self.assertFalse(boundary["consumed_private_branch_identified"])
            self.assertFalse(boundary["real_cohort_established"])
            self.assertFalse(boundary["neural_payload_accessed"])
            self.assertFalse(boundary["decoding_performance_established"])


if __name__ == "__main__":
    unittest.main()
