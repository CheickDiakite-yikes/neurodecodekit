import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_r1_inventory_distribution_discriminator_implementation.v0.json"
)


class Marc2R1InventoryDistributionDiscriminatorImplementationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registration_proof_is_exact_and_green(self):
        proof = self.record["registration_proof"]
        self.assertEqual(
            proof["commit"], "fcd088cc2eef6556f36ed596c6d9bb6c7ee9d7c3"
        )
        self.assertEqual(proof["CI_run_id"], 32_618_866_986)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_implementation_artifacts_match_exact_bytes_and_hashes(self):
        total = 0
        rows = self.record["implementation_artifacts"]
        self.assertEqual(len(rows), self.record["implementation_artifact_count"])
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            total += len(payload)
        self.assertEqual(total, self.record["implementation_artifact_bytes"])

    def test_measured_qualification_matches_frozen_matrix(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["paths"], 32)
        self.assertEqual(result["VR25A_calls"], 32)
        self.assertEqual(result["R1_filter_discriminator_calls"], 16)
        self.assertEqual(result["VR2_filter_refusal_sites"], 2)
        self.assertEqual(
            result["VR29A_route_counts"],
            {
                "MARC2VR29A-G1": 4,
                "MARC2VR29A-G2": 4,
                "MARC2VR29A-R1": 8,
                "MARC2VR29A-R2": 8,
                "MARC2VR29A-R3": 8,
            },
        )
        self.assertGreaterEqual(result["direct_refusals_passed"], 70)

    def test_resources_and_operation_counters_are_bounded(self):
        measured = self.record["measurements"]
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["generated_input_bytes"], 32 * 1024**2)
        self.assertEqual(measured["retained_output_bytes"], 0)
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )

    def test_remote_proof_transition_is_fail_closed(self):
        proof = self.record["remote_implementation_proof"]
        if proof is not None:
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(proof["scope_changed_after_qualification"])
        self.assertFalse(self.record["next_gate"]["private_executor_available"])
        self.assertFalse(
            self.record["next_gate"]["private_discriminator_or_source_read_authorized"]
        )


if __name__ == "__main__":
    unittest.main()
