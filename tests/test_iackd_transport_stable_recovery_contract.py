import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries" / "iackd_transport_stable_recovery_contract.v0.json"
INVENTORY_PATH = ROOT / "registries" / "iackd_openneuro_metadata_inventory.v0.json"
PARENT_PATH = ROOT / "registries" / "iackd_role_aware_dual_reversal_contract.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDTransportStableRecoveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        cls.parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))

    def test_schema_and_status_are_prospective(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.iackd_transport_stable_recovery_contract",
        )
        self.assertEqual(
            self.contract["contract_id"],
            "IACKD-T1-transport-stable-recovery-contract-v0",
        )
        self.assertIn("public_requests_unauthorized", self.contract["status"])
        self.assertFalse(self.contract["authorization_state"]["real_executor_integration"])
        self.assertFalse(self.contract["authorization_state"]["public_metadata_request"])
        self.assertFalse(self.contract["authorization_state"]["public_payload_request"])

    def test_every_bound_artifact_hash_matches(self) -> None:
        for binding in self.contract["bindings"].values():
            if "path" in binding and "sha256" in binding:
                with self.subTest(path=binding["path"]):
                    self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_metadata_bodies_replay_exactly_from_inventory(self) -> None:
        docs = self.contract["metadata_contract"]["documents"]
        source = self.inventory["source_documents"]
        pages = self.inventory["listing_snapshot"]["pages"]
        expected = [
            (source["dataset_description"]["bytes"], source["dataset_description"]["sha256"]),
            (source["changes"]["bytes"], source["changes"]["sha256"]),
            (pages[0]["body_bytes"], pages[0]["body_sha256"]),
            (pages[1]["body_bytes"], pages[1]["body_sha256"]),
        ]
        self.assertEqual(
            [(row["registered_bytes"], row["registered_sha256"]) for row in docs],
            expected,
        )
        self.assertEqual(sum(row["registered_bytes"] for row in docs), 595400)
        self.assertEqual(sum(row["read_limit_bytes"] for row in docs), 595404)

    def test_metadata_transport_is_bounded_and_content_addressed(self) -> None:
        metadata = self.contract["metadata_contract"]
        self.assertEqual(
            metadata["accepted_framing_profiles"],
            ["fixed_length", "chunked", "close_delimited"],
        )
        self.assertFalse(metadata["Content_Length_required"])
        self.assertEqual(metadata["Content_Length_role"], "advisory_transport_evidence")
        self.assertEqual(metadata["content_identity_fields"], ["observed_body_bytes", "body_SHA256"])
        self.assertEqual(metadata["read_algorithm"], "one_read_registered_bytes_plus_one")
        self.assertTrue(metadata["ambiguous_Content_Length_and_Transfer_Encoding_refused"])
        self.assertEqual(metadata["allowed_Transfer_Encoding"], [None, "chunked"])
        self.assertEqual(metadata["allowed_Content_Encoding"], [None, "", "identity"])
        self.assertEqual(metadata["semantic_parse_after_identity_passes"], 1)
        self.assertEqual(metadata["retries"], 0)

    def test_large_payload_transport_remains_strict(self) -> None:
        payload = self.contract["payload_contract"]
        self.assertEqual(payload["object_count"], 1340)
        self.assertEqual(payload["payload_bytes"], 7249113684)
        self.assertTrue(payload["exact_Content_Length_required"])
        self.assertTrue(payload["exact_registered_ETag_required"])
        self.assertTrue(payload["exact_observed_bytes_required"])
        self.assertEqual(payload["full_stream_SHA256_passes_per_object"], 1)
        self.assertEqual(payload["retries"], 0)
        self.assertEqual(payload["reruns"], 0)

    def test_parent_scientific_design_is_frozen(self) -> None:
        frozen = self.contract["frozen_scientific_parent"]
        self.assertEqual(frozen["parent_contract_id"], self.parent["contract_id"])
        self.assertEqual(frozen["participant_hand_units"], 30)
        self.assertEqual(frozen["arms"], ["C2I", "I2C"])
        self.assertEqual(frozen["predictive_EEG_channels"], 26)
        self.assertEqual(frozen["window_seconds"], [-1.0, 0.0])
        self.assertEqual(frozen["primary_passband_hz"], [0.5, 4.0])
        self.assertEqual(frozen["parameter_update_fits"], 660)
        self.assertEqual(frozen["prediction_sets"], 900)
        self.assertTrue(frozen["all_other_scientific_fields_inherited_unchanged"])
        self.assertEqual(self.contract["allowed_semantic_delta"], ["small_metadata_response_framing_policy"])

    def test_fixture_stage_is_zero_network_and_bounded(self) -> None:
        caps = self.contract["resource_caps"]["generated_qualification"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["wall_time_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(caps["generated_output_bytes"], 1024 * 1024)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["real_or_public_body_reads"], 0)

    def test_stage_order_requires_two_green_milestones_and_fresh_decision(self) -> None:
        stages = self.contract["ordered_stages"]
        self.assertTrue(stages["generated_implementation"]["requires_green_registration"])
        self.assertTrue(stages["tier_C_request"]["requires_green_exact_implementation"])
        self.assertTrue(stages["tier_C_decision"]["fresh_packet_bound_maintainer_message_required"])
        self.assertTrue(stages["real_executor_integration"]["requires_green_decision"])
        self.assertFalse(stages["public_execution"]["authorized_now"])
        self.assertFalse(stages["public_execution"]["current_continue_is_retroactive"])

    def test_claim_boundary_and_document_are_explicit(self) -> None:
        claim = self.contract["claim_boundary"]
        self.assertIn("framing", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])
        document = (
            ROOT / "docs" / "IACKD_TRANSPORT_STABLE_RECOVERY_PREREGISTRATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("The current instruction is not step 7 authorization", document)


if __name__ == "__main__":
    unittest.main()
