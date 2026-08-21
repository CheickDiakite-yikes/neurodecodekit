import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT / "registries/marc2_r4_private_discriminator_implementation.v0.json"
)


class Marc2R4PrivateDiscriminatorImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_decision_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_r4_private_discriminator_implementation",
        )
        self.assertEqual(self.record["lane_id"], "MARC2-VR13P")
        proof = self.record["green_decision_proof"]
        self.assertEqual(proof["commit"], "fe16400fd0ccb5fa2ff40fffd413fee34eb620d6")
        self.assertEqual(proof["CI_run_id"], 32_439_821_302)
        self.assertEqual(proof["base_python_job_id"], 96_648_078_587)
        self.assertEqual(proof["optional_neuro_job_id"], 96_648_078_452)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_owned_artifacts_are_byte_exact(self):
        for row in self.record["owned_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_generated_measurements_are_exact(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["route"], "MARC2VR13P-G1")
        self.assertEqual(result["matrix_paths"], 32)
        self.assertEqual(result["route_count_each"], 4)
        self.assertEqual(result["generated_VR12A_calls"], 33)
        self.assertEqual(result["generated_VR13A_residual_map_calls"], 28)
        self.assertEqual(result["direct_refusals"], 81)
        self.assertEqual(result["generated_input_bytes"], 14_171_146)
        self.assertEqual(result["retained_output_bytes"], 0)
        self.assertLess(result["runtime_seconds"], 60)
        self.assertLess(result["peak_RSS_bytes"], 256 * 1024**2)

    def test_interface_and_execution_proof_fail_closed(self):
        interface = self.record["interface"]
        self.assertEqual(interface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertFalse(interface["generic_path_or_output_override_allowed"])
        self.assertFalse(interface["consumed_executor_reuse_allowed"])
        proof = self.record["remote_implementation_proof"]
        if proof is None:
            self.assertFalse(self.record["private_execution_authorized_now"])
        else:
            self.assertEqual(proof["qualification_route"], "MARC2VR13P-G1")
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(proof["scope_changed_after_qualification"])
            self.assertFalse(proof["qualification_repeated_for_proof_closeout"])
            self.assertEqual(proof["private_operations_during_proof_closeout"], 0)
        self.assertFalse(self.record["private_execution_authorized_now"])

    def test_counters_and_claims_remain_zero(self):
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        claims = self.record["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
