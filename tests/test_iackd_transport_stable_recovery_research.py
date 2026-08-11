import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries" / "iackd_transport_stable_recovery_research.v0.json"
FAILURE_PATH = (
    ROOT / "registries" / "iackd_role_aware_dual_reversal_stream_failure_result.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDTransportStableRecoveryResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.failure = json.loads(FAILURE_PATH.read_text(encoding="utf-8"))

    def test_record_is_tier_a_and_target_free(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_transport_stable_recovery_research",
        )
        self.assertEqual(self.record["research_id"], "IACKD-T1-transport-stable-recovery-v0")
        self.assertIn("no_public_dataset_request", self.record["status"])
        self.assertFalse(self.record["proof_posture"]["scientific_result"])

    def test_consumed_failure_binding_is_exact_and_closed(self) -> None:
        parent = self.record["consumed_parent"]
        self.assertEqual(parent["commit"], "36aeccb76c7e277b9dd69792e9bfcffb018f1188")
        self.assertEqual(parent["route"], self.failure["route"])
        self.assertTrue(parent["consumed"])
        self.assertFalse(parent["retry_or_rerun_allowed"])
        self.assertFalse(parent["body_read"])
        self.assertEqual(_sha256(ROOT / parent["result_path"]), parent["result_sha256"])

    def test_primary_sources_are_official_and_transport_specific(self) -> None:
        sources = self.record["primary_sources"]
        self.assertEqual(set(sources), {"RFC9110", "RFC9112", "python_http", "python_redirect", "openneuro", "amazon_s3"})
        self.assertTrue(sources["RFC9110"]["url"].startswith("https://www.rfc-editor.org/"))
        self.assertTrue(sources["RFC9112"]["url"].startswith("https://www.rfc-editor.org/"))
        self.assertTrue(sources["python_http"]["url"].startswith("https://docs.python.org/"))
        self.assertTrue(sources["openneuro"]["url"].startswith("https://docs.openneuro.org/"))
        self.assertTrue(sources["amazon_s3"]["url"].startswith("https://docs.aws.amazon.com/"))

    def test_correction_separates_framing_from_identity(self) -> None:
        correction = self.record["architectural_correction"]
        self.assertEqual(
            correction["accepted_metadata_framing_profiles"],
            ["fixed_length", "chunked", "close_delimited"],
        )
        self.assertFalse(correction["metadata_Content_Length_is_content_identity"])
        self.assertEqual(
            correction["metadata_content_identity"],
            ["exact_observed_bytes", "registered_SHA256"],
        )
        self.assertTrue(correction["payload_exact_Content_Length_retained"])
        self.assertTrue(correction["payload_exact_ETag_retained"])
        self.assertTrue(correction["payload_full_stream_SHA256_retained"])

    def test_scientific_protocol_is_unchanged(self) -> None:
        frozen = self.record["scientific_protocol"]
        self.assertTrue(frozen["all_parent_scientific_fields_unchanged"])
        self.assertEqual(frozen["parameter_update_fits"], 660)
        self.assertEqual(frozen["prediction_sets"], 900)
        self.assertEqual(frozen["final_target_deliveries"], 1)
        self.assertEqual(frozen["scoring_events"], 1)
        self.assertEqual(frozen["router"], "IACKD2-R0_through_IACKD2-R5")

    def test_every_research_access_counter_is_zero(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_claim_boundary_is_explicit(self) -> None:
        claim = self.record["claim_boundary"]
        self.assertIn("transport", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])
        document = (
            ROOT / "docs" / "IACKD_TRANSPORT_STABLE_RECOVERY_RESEARCH.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
