import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCIDENT_PATH = (
    ROOT / "registries/marc2_r4_private_discriminator_incident.v0.json"
)
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_r4_private_discriminator_implementation.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/MARC_2_R4_PRIVATE_DISCRIMINATOR_INCIDENT.md"


class Marc2R4PrivateDiscriminatorIncidentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.incident = json.loads(INCIDENT_PATH.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_incident_is_consumed_invalid_and_proof_null(self):
        self.assertEqual(
            self.incident["status"], "consumed_invalid_parked_no_retry_no_result"
        )
        self.assertIsNone(self.implementation["remote_implementation_proof"])
        self.assertFalse(self.implementation["private_execution_authorized_now"])
        self.assertTrue(self.incident["disposition"]["VR13P_consumed"])
        self.assertFalse(self.incident["disposition"]["result_valid"])

    def test_known_structural_operations_are_exact(self):
        operations = self.incident["known_operations"]
        self.assertEqual(operations["focused_test_invocations"], 1)
        self.assertEqual(operations["actual_readiness_samples"], 0)
        self.assertEqual(operations["private_preflight_operations"], 0)
        self.assertEqual(operations["private_source_content_opens"], 1)
        self.assertEqual(operations["private_source_bytes_read"], 418_755)
        self.assertEqual(operations["strict_JSON_parses"], 1)
        self.assertEqual(operations["VR12A_calls"], 1)

    def test_forbidden_scientific_operations_remain_zero(self):
        operations = self.incident["known_operations"]
        for key in (
            "network_operations",
            "archive_header_or_member_payload_operations",
            "signal_event_channel_geometry_target_or_label_operations",
            "training_inference_prediction_freeze_delivery_or_score_operations",
            "FW2_or_CIL1_operations",
            "operations_on_other_projects",
            "retry_rerun_resume_operations",
            "scientific_claim_upgrades",
        ):
            self.assertEqual(operations[key], 0)

    def test_unknown_result_fields_remain_unavailable(self):
        self.assertTrue(all(self.incident["not_retained_or_inspected"].values()))
        disposition = self.incident["disposition"]
        self.assertFalse(disposition["ignored_output_cleanup_or_inspection_authorized"])
        self.assertTrue(
            disposition["future_recovery_requires_new_frozen_Tier_C_packet_and_decision"]
        )
        self.assertFalse(disposition["FW2_or_CIL1_eligible"])

    def test_document_is_explicit_about_failure_and_claim_boundary(self):
        for phrase in (
            "sequencing and proof-verification failure",
            "read exactly 418,755 bytes",
            "ignored output was not inspected",
            "VR13P is consumed and parked",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.document)


if __name__ == "__main__":
    unittest.main()
