import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries/marc2_selection_boundary_private_confirmation_authorization_decision.v0.json"
)


class Marc2SelectionBoundaryPrivateConfirmationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_and_exact_user_message_are_bound(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_selection_boundary_private_confirmation_authorization_decision",
        )
        self.assertEqual(self.decision["lane_id"], "MARC2-VR26P")
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"],
            "e256ee8e7aff6957a781d8328f0f68e26996564c81fa458da59fbca2305138ad",
        )
        self.assertEqual(user["sole_active_Tier_C_packet"], "MARC2-VR26P")
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])

    def test_request_and_proof_green_are_exact(self):
        request = self.decision["green_request"]
        self.assertEqual(
            request["commit"], "00db8254f67dd349bddb8a906b57d7e28c2f7101"
        )
        self.assertEqual(request["CI_run_id"], 32_606_451_461)
        self.assertEqual(request["base_python_job_id"], 97_112_059_257)
        self.assertEqual(request["optional_neuro_job_id"], 97_112_059_152)
        self.assertTrue(request["both_required_jobs_green"])
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(
            proof["commit"], "efd779a2d8bafbd4efbf5618fadf2355f4f89ee4"
        )
        self.assertEqual(proof["CI_run_id"], 32_607_272_954)
        self.assertEqual(proof["base_python_job_id"], 97_114_173_204)
        self.assertEqual(proof["optional_neuro_job_id"], 97_114_173_360)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])
        self.assertEqual(proof["private_real_or_scientific_operations"], 0)

    def test_six_bound_packet_artifacts_are_exact(self):
        rows = self.decision["bound_packet_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 51_785)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.run(
                ["git", "hash-object", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_decision_artifacts_are_exact_without_private_operations(self):
        for row in self.decision["decision_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
        counters = self.decision["decision_only_counters"]
        for key, value in counters.items():
            if key == "GitHub_CI_verification_calls":
                self.assertEqual(value, 1)
            else:
                self.assertEqual(value, 0, key)

    def test_authorization_is_strictly_staged(self):
        authorization = self.decision["authorization"]
        self.assertTrue(authorization["generated_wrapper_implementation_after_decision_green"])
        self.assertTrue(authorization["generated_wrapper_qualification_after_decision_green"])
        self.assertTrue(authorization["stage_1_proof_closeout_after_implementation_green"])
        self.assertTrue(
            authorization["one_private_structural_read_after_stage_1_proof_green"]
        )
        self.assertTrue(authorization["private_cohort_freeze_on_R1_or_R2"])
        for key, value in authorization.items():
            if key.endswith("authorized_now"):
                with self.subTest(key=key):
                    self.assertFalse(value)

    def test_routes_and_cohort_identity_are_frozen(self):
        routes = self.decision["private_route_contract"]
        self.assertEqual([row["route"] for row in routes], [
            "MARC2VR26P-R1",
            "MARC2VR26P-R2",
            "MARC2VR26P-R3",
            "MARC2VR26P-R4",
            "MARC2VR26P-R5",
            "MARC2VR26P-R6",
            "MARC2VR26P-R7",
        ])
        self.assertTrue(routes[0]["private_cohort_manifest_allowed"])
        self.assertTrue(routes[1]["private_cohort_manifest_allowed"])
        self.assertTrue(
            all(not row["private_cohort_manifest_allowed"] for row in routes[2:])
        )
        cohort = self.decision["cohort_contract"]
        self.assertEqual(cohort["selected_subjects"], 16)
        self.assertEqual(cohort["selected_run_bundles"], 96)
        self.assertEqual(cohort["selected_core_members"], 384)
        self.assertFalse(cohort["observed_complete_bundle_count_allowed_publicly"])

    def test_resources_and_scientific_boundary_remain_closed(self):
        caps = self.decision["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["private_source_read_bytes"], 418_755)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_member_bytes"], 0)
        self.assertEqual(caps["signal_bytes"], 0)
        self.assertEqual(caps["target_bytes"], 0)
        claims = self.decision["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {
                "engineering_capability_authorized_after_green",
                "scientific_ceiling",
            }:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
