import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_private_discriminator_implementation.v0.json"
)
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_private_discriminator_result.v0.json"
)


class Marc2FirstFailureStablePrivateDiscriminatorImplementationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_decision_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_first_failure_stable_private_discriminator_implementation",
        )
        self.assertEqual(self.record["lane_id"], "MARC2-VR18P")
        proof = self.record["green_decision_proof"]
        self.assertEqual(proof["commit"], "5113be7fee63d769276a781c0ed3af5ac2bbf567")
        self.assertEqual(proof["CI_run_id"], 32_475_765_286)
        self.assertEqual(proof["base_python_job_id"], 96_751_646_673)
        self.assertEqual(proof["optional_neuro_job_id"], 96_751_646_346)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_owned_artifacts_are_byte_exact(self):
        for row in self.record["owned_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_generated_measurements_are_exact(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["route"], "MARC2VR18P-G1")
        self.assertEqual(result["matrix_paths"], 20)
        self.assertEqual(result["route_count_each"], 4)
        self.assertEqual(result["generated_VR16A_calls"], 21)
        self.assertEqual(result["generated_VR17C_map_calls"], 16)
        self.assertEqual(result["direct_refusals"], 82)
        self.assertEqual(result["generated_input_bytes"], 9_037_650)
        self.assertEqual(result["retained_output_bytes"], 0)
        self.assertLess(result["runtime_seconds"], 60)
        self.assertLess(result["peak_RSS_bytes"], 256 * 1024**2)

    def test_result_record_matches_and_remote_proof_is_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR18P")
        self.assertEqual(self.result["route"], "MARC2VR18P-G1")
        self.assertEqual(
            self.result["matrix"]["replay_sha256"],
            "5c214a1e9e5b3aa53b30931ff2d4573b675cb9bf18b41753b0da2eaae9c8bd35",
        )
        proof = self.record["remote_implementation_proof"]
        self.assertEqual(proof["commit"], "668812367acd8ca3ae9d0603dcde9b4b5aa02d58")
        self.assertEqual(proof["CI_run_id"], 32_477_528_982)
        self.assertEqual(proof["base_python_job_id"], 96_756_873_128)
        self.assertEqual(proof["optional_neuro_job_id"], 96_756_873_357)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_after_qualification"])
        self.assertFalse(proof["qualification_repeated_for_proof_closeout"])
        self.assertEqual(proof["private_operations_during_proof_closeout"], 0)
        self.assertEqual(self.result["remote_implementation_proof"], proof)
        self.assertFalse(self.record["private_execution_authorized_now"])
        self.assertFalse(self.result["private_execution_authorized_now"])

    def test_counters_and_claims_remain_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )
        claims = self.record["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
