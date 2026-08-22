import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc2_f06_five_route_decomposition_implementation.v0.json"
)


class Marc2F06FiveRouteDecompositionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registration_proof_is_exact_and_green(self):
        proof = self.registry["registration_proof"]
        self.assertEqual(
            proof["commit"],
            "cee91b0473cd97a91feab22d7fd420e0b550b99f",
        )
        self.assertEqual(proof["CI_run_id"], 32_596_045_581)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_implementation_artifacts_are_exact(self):
        for row in self.registry["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["role"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                row["sha256"],
                row["role"],
            )

    def test_static_and_generated_proofs_are_exact(self):
        static = self.registry["static_proof"]
        self.assertEqual(static["independently_reachable_F06_classes"], 5)
        self.assertEqual(static["non_independent_defensive_reasons"], 2)
        measured = self.registry["generated_qualification"]
        self.assertEqual(measured["route"], "MARC2VR23A-G1")
        self.assertEqual(measured["paths"], 24)
        self.assertEqual(measured["VR20A_calls"], 24)
        self.assertEqual(measured["direct_refusals_passed"], 62)
        self.assertEqual(measured["source_mutations_after_call"], 0)

    def test_resources_and_zero_counters_pass(self):
        measured = self.registry["generated_qualification"]
        self.assertLessEqual(measured["runtime_seconds"], 45)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 24 * 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertTrue(
            all(value == 0 for value in self.registry["operation_counters"].values())
        )

    def test_remote_proof_and_private_execution_remain_closed(self):
        proof = self.registry["remote_implementation_proof"]
        self.assertEqual(
            proof["commit"],
            "9e1b12139ad9cd9bcd2245a1eb74b85d7a3cbeeb",
        )
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(
            proof["generated_qualification_repeated_for_proof_closeout"]
        )
        self.assertEqual(proof["private_operations_during_proof_closeout"], 0)
        gate = self.registry["next_gate"]
        self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
        self.assertFalse(gate["private_discriminator_packet_eligible_now"])
        self.assertFalse(gate["private_packet_allowed_before_closeout"])
        self.assertFalse(gate["private_or_neural_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
