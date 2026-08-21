import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_suffix_identity_grammar_decomposition_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_suffix_identity_grammar_decomposition_result.v0.json"


class Marc2SuffixIdentityGrammarDecompositionRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_records_bind_lane_route_and_green_proof(self):
        self.assertEqual(self.implementation["lane_id"], "MARC2-VR15A")
        self.assertEqual(self.result["lane_id"], "MARC2-VR15A")
        self.assertEqual(self.result["route"], "MARC2VR15A-G1")
        self.assertFalse(self.implementation["local_verification"]["remote_CI_pending"])
        for record in (self.implementation, self.result):
            proof = record["remote_implementation_proof"]
            self.assertEqual(proof["commit"], "bfb0dcb7752433b4af841d57bbfcbf613a341124")
            self.assertEqual(proof["CI_run_id"], 32_449_260_503)
            self.assertEqual(proof["base_python_job_id"], 96_674_484_190)
            self.assertEqual(proof["optional_neuro_job_id"], 96_674_484_279)
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(proof["generated_qualification_repeated_for_proof_closeout"])
            self.assertFalse(proof["private_operation_repeated_for_proof_closeout"])

    def test_owned_artifact_hashes_match(self):
        rows = self.implementation["tracked_implementation_artifacts"]
        self.assertEqual(len(rows), 5)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])

    def test_green_registration_is_exact(self):
        for record in (self.implementation, self.result):
            proof = record["green_registration_proof"]
            self.assertEqual(proof["commit"], "185fbc54366fd0eaf0ed4e994511e4485514b53e")
            self.assertEqual(proof["CI_run_id"], 32_447_836_662)
            self.assertEqual(proof["base_python_job_id"], 96_670_618_009)
            self.assertEqual(proof["optional_neuro_job_id"], 96_670_617_843)
            self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_matrix_and_measurements_match(self):
        generated = self.implementation["generated_qualification"]
        replay = self.result["replay_summary"]
        self.assertEqual(generated["exact_paths"], 68)
        self.assertEqual(generated["exact_VR12A_calls"], 68)
        self.assertEqual(generated["route_count_each"], 4)
        self.assertEqual(generated["direct_refusals_passed"], 70)
        self.assertEqual(replay["total_paths"], 68)
        self.assertEqual(replay["exact_VR12A_calls"], 68)
        self.assertEqual(
            generated["internal_matrix_digest_sha256"],
            replay["internal_matrix_digest_sha256"],
        )
        self.assertEqual(
            self.implementation["measured_qualification"],
            self.result["measurements"],
        )

    def test_verification_delta_is_additive(self):
        verification = self.implementation["local_verification"]
        self.assertEqual(verification["focused_tests"], 26)
        self.assertEqual(verification["prechange_complete_base_tests"], 4_359)
        self.assertEqual(verification["complete_base_tests"], 4_380)
        self.assertEqual(verification["complete_expected_skips"], 204)
        self.assertEqual(verification["complete_failures"], 0)
        self.assertTrue(verification["complete_base_suite_passed"])

    def test_authority_and_scientific_boundaries_remain_closed(self):
        for record in (self.implementation, self.result):
            self.assertTrue(all(value == 0 for value in record["access_counters"].values()))
            self.assertFalse(record["next_gate"]["future_private_discriminator_authorized"])
            self.assertFalse(record["next_gate"]["MARC2_FW2_or_CIL1_authorized"])
            self.assertTrue(
                record["next_gate"][
                    "exact_implementation_and_result_commit_push_and_both_jobs_green_satisfied"
                ]
            )
            claims = record["claim_boundary"]
            self.assertEqual(claims["scientific_ceiling"], "none")
            for key, value in claims.items():
                if key not in {"engineering_ceiling", "scientific_ceiling"}:
                    self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
