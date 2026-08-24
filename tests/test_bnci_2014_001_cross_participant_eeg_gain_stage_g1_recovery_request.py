import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_recovery_authorization_request.v0.json"


class BNCIStageG1RecoveryRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text())

    def test_request_is_all_false_and_has_zero_current_operations(self):
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertTrue(
            all(value is False for value in self.request["recovery_authority_now"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_operation_counters"].values())
        )

    def test_every_bound_artifact_matches_size_and_sha256(self):
        for binding in self.request["bindings"].values():
            path = ROOT / binding["path"]
            payload = path.read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])
            if "bytes" in binding:
                self.assertEqual(len(payload), binding["bytes"])

    def test_recovery_is_one_generated_pass_and_stops_before_stage_A(self):
        scope = self.request["requested_scope_after_fresh_green_decision"]
        self.assertEqual(scope["replacement_generated_qualification_invocations"], 1)
        self.assertEqual(scope["synthetic_parameter_update_fits_exact"], 468)
        self.assertEqual(scope["synthetic_prediction_sets_exact"], 495)
        self.assertEqual(scope["real_or_existing_payload_operations"], 0)
        self.assertFalse(scope["retry_after_replacement"])
        self.assertFalse(scope["Stage_A_authorized_by_recovery"])
        self.assertEqual(self.request["required_order"][-1], "stop_before_Stage_A")


if __name__ == "__main__":
    unittest.main()
