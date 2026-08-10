import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT / "registries/physionet_motor_positive_control_authorization_request.v0.json"
)
PACKET_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_AUTHORIZATION_PACKET.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetMotorPositiveControlAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_is_awaiting_exact_sentence_and_authorizes_nothing(self):
        self.assertEqual(self.request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        authorization = self.request["authorization"]
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])
        self.assertTrue(
            all(
                value is False
                for key, value in authorization.items()
                if key
                not in {
                    "exact_authorization_sentence",
                    "separate_authorization_only_record_required",
                }
            )
        )

    def test_registration_commit_and_remote_green_jobs_are_exact(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "3c00557ecfb09c80e30843589ae295a09feec97c",
        )
        self.assertEqual(registration["push_ci_run_id"], 31346882592)
        self.assertEqual(registration["base_python_job_id"], 93330354031)
        self.assertEqual(registration["optional_neuro_job_id"], 93330354047)
        self.assertTrue(registration["remote_registration_is_green"])

    def test_registration_artifact_hashes_and_blobs_are_bound(self):
        target = self.request["target"]
        for prefix in ("research", "preregistration", "contract", "invariant_test"):
            path = ROOT / target[f"{prefix}_path"]
            self.assertEqual(target[f"{prefix}_sha256"], sha256(path), str(path))
            self.assertEqual(len(target[f"{prefix}_git_blob_sha1"]), 40)
        self.assertEqual(target["authorization_packet_sha256"], sha256(PACKET_PATH))
        self.assertTrue(target["registration_snapshot_must_remain_immutable"])

    def test_exact_sentence_is_identical_to_packet(self):
        packet = PACKET_PATH.read_text(encoding="utf-8")
        marker = "> Authorize the work order 9 PhysioNet motor positive-control implementation"
        sentence_lines = []
        recording = False
        for line in packet.splitlines():
            if line.startswith(marker):
                recording = True
            if recording:
                if not line.startswith("> "):
                    break
                sentence_lines.append(line[2:])
        self.assertTrue(sentence_lines)
        packet_sentence = " ".join(sentence_lines)
        self.assertEqual(
            self.request["authorization"]["exact_authorization_sentence"],
            packet_sentence,
        )

    def test_requested_scope_does_not_expand_the_acquired_inventory(self):
        scope = self.request["requested_scope"]
        self.assertEqual(scope["subjects"], ["S001", "S002", "S003"])
        self.assertEqual(scope["runs"], ["03", "07", "11"])
        self.assertEqual(scope["file_count"], 9)
        self.assertEqual(scope["payload_bytes"], 23_248_224)
        self.assertEqual(scope["new_payload_bytes"], 0)
        self.assertEqual(scope["network_bytes_during_real_execution"], 0)
        self.assertEqual(scope["event_sidecar_operations"], 0)

    def test_order_requires_green_decision_implementation_and_freeze(self):
        order = self.request["requested_access_order"]
        self.assertEqual(len(order), 12)
        self.assertLess(
            order.index("decision_commit_pushed_and_both_required_CI_jobs_green"),
            order.index("generated_fixture_only_implementation_and_optional_environment"),
        )
        self.assertLess(
            order.index("implementation_commit_pushed_and_both_required_CI_jobs_green"),
            order.index("one_real_nine_EDF_execution"),
        )
        self.assertLess(
            order.index("hash_only_prediction_freeze_commit_pushed_and_remotely_green"),
            order.index("one_delivery_and_one_score_of_same_45_run11_targets"),
        )

    def test_resource_caps_match_frozen_contract_and_install_is_isolated(self):
        resources = self.request["resource_caps"]
        real = resources["real_execution"]
        self.assertEqual(real["cpu_threads"], 1)
        self.assertEqual(real["wall_time_seconds"], 1800)
        self.assertEqual(real["peak_rss_bytes"], 805_306_368)
        self.assertEqual(real["generated_private_output_bytes"], 67_108_864)
        self.assertEqual(real["maximum_classical_fits"], 40)
        self.assertEqual(real["maximum_prediction_sets"], 64)
        self.assertEqual(real["network_bytes"], 0)
        self.assertEqual(real["retries"], 0)
        self.assertEqual(real["reruns"], 0)
        install = resources["optional_environment_installation"]
        self.assertEqual(install["invocations"], 1)
        self.assertEqual(install["maximum_network_bytes"], 256 * 1024 * 1024)
        self.assertEqual(install["maximum_incremental_disk_bytes"], 512 * 1024 * 1024)
        self.assertFalse(install["base_dependency_change"])
        self.assertFalse(install["torch_or_broad_EEG_stack_allowed"])

    def test_counters_and_claim_boundary_remain_zero_and_narrow(self):
        self.assertTrue(
            all(value == 0 for value in self.request["current_access_counters"].values())
        )
        boundary = self.request["claim_boundary"]
        self.assertIn("three-person", boundary["maximum_future_claim"])
        self.assertIn("unseen-person", boundary["not_established_even_if_WO9_V3"])
        self.assertFalse(boundary["current_scientific_claim_upgrade"])


if __name__ == "__main__":
    unittest.main()
