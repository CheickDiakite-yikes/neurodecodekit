import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_exact_count_private_confirmation_authorization_request.v0.json"
)
DECISION_PATH = (
    ROOT
    / "registries/marc2_exact_count_private_confirmation_authorization_decision.v0.json"
)


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class ExactCountPrivateConfirmationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_and_exact_user_message_are_bound(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_exact_count_private_confirmation_authorization_decision",
        )
        self.assertEqual(self.decision["lane_id"], "MARC2-VR34P")
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"],
            "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad",
        )
        self.assertEqual(user["sole_active_Tier_C_packet"], "MARC2-VR34P")
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])

    def test_request_and_proof_green_are_exact(self):
        request = self.decision["green_request"]
        self.assertEqual(
            request["commit"], "d4215c5aa5b8e43d91ff7ff26b8ea035648f3706"
        )
        self.assertEqual(request["CI_run_id"], 32_637_387_771)
        self.assertEqual(request["base_python_job_id"], 97_189_079_380)
        self.assertEqual(request["optional_neuro_job_id"], 97_189_079_311)
        self.assertTrue(request["both_required_jobs_green"])
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(
            proof["commit"], "45cc8f18fe8fc7f5c8b9675648a4cd358617808d"
        )
        self.assertEqual(proof["CI_run_id"], 32_638_120_718)
        self.assertEqual(proof["base_python_job_id"], 97_190_816_942)
        self.assertEqual(proof["optional_neuro_job_id"], 97_190_817_104)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_six_bound_packet_artifacts_are_exact(self):
        rows = self.decision["bound_packet_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 41_496)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_decision_artifacts_and_counters_are_exact(self):
        for row in self.decision["decision_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
        counters = self.decision["decision_only_counters"]
        for key, value in counters.items():
            if key == "GitHub_CI_verification_calls":
                self.assertEqual(value, 1)
            else:
                self.assertEqual(value, 0, key)

    def test_authorization_is_strictly_staged(self):
        authorization = self.decision["authorization"]
        self.assertTrue(
            authorization["generated_wrapper_implementation_after_decision_green"]
        )
        self.assertTrue(
            authorization["generated_wrapper_qualification_after_decision_green"]
        )
        self.assertTrue(
            authorization["one_private_structural_read_after_stage_1_proof_green"]
        )
        self.assertFalse(
            authorization["observed_total_difference_or_private_detail_retention"]
        )
        self.assertFalse(authorization["cohort_freeze"])
        for key, value in authorization.items():
            if key.endswith("authorized_now"):
                self.assertFalse(value, key)

    def test_generated_stage_and_readiness_are_exact(self):
        stage = self.decision["generated_stage_requirements"]
        self.assertEqual(stage["required_paths"], 60)
        self.assertEqual(stage["VR33A_calls"], 60)
        self.assertEqual(stage["readiness_provider_calls"], 180)
        self.assertEqual(stage["readiness_sleeper_calls"], 120)
        self.assertEqual(stage["VR31A_calls"], 32)
        self.assertEqual(
            stage["expected_route_counts"],
            self.request["generated_stage_requirements"]["expected_route_counts"],
        )
        readiness = self.decision["readiness_contract"]
        self.assertEqual(readiness["sample_provider_calls"], 3)
        self.assertEqual(readiness["sleeper_calls"], 2)
        self.assertEqual(readiness["passing_pattern"], "PPP")
        self.assertFalse(readiness["dynamic_loop_allowed"])
        self.assertFalse(readiness["extra_sample_allowed"])

    def test_routes_resources_and_request_binding_are_frozen(self):
        routes = self.decision["private_route_contract"]
        self.assertEqual(
            [row["route"] for row in routes],
            [f"MARC2VR34P-R{index}" for index in range(1, 6)],
        )
        self.assertTrue(all(not row["private_detail_allowed"] for row in routes))
        self.assertEqual(
            self.decision["discriminator_contract"]["frozen_map"],
            self.request["future_discriminator_contract"]["frozen_map"],
        )
        caps = self.decision["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["private_source_read_bytes_if_ready"], 418_755)
        self.assertEqual(caps["private_source_content_opens_if_ready"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["signal_bytes"], 0)
        self.assertEqual(caps["target_bytes"], 0)
        self.assertEqual(caps["retry_rerun_resume_count"], 0)

    def test_scientific_boundary_remains_closed(self):
        claims = self.decision["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {
                "engineering_capability_authorized_after_green",
                "scientific_ceiling",
            }:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
