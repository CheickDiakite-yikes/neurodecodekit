from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries/ofner_2017_motor_imagery_fixed_header_contract.v0.json"
DOCUMENT = ROOT / "docs/OFNER_2017_MOTOR_IMAGERY_FIXED_HEADER_PREREGISTRATION.md"
FRONTIER = ROOT / "registries/current_research_frontier.v3.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v2.json"


class OfnerFixedHeaderPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_green_basis_is_exact(self) -> None:
        basis = self.contract["green_basis"]
        self.assertEqual(
            basis["implementation_commit"],
            "527dffd0cc18a5259eeaba796f38774bbf1f472c",
        )
        self.assertEqual(
            basis["proof_closeout_commit"],
            "786b1249b6f9352136328bf9f289120a300472ad",
        )
        self.assertEqual(basis["proof_closeout_CI_run_id"], 33_267_877_803)
        self.assertTrue(basis["both_proof_closeout_jobs_green"])
        self.assertTrue(basis["proof_closeout_on_GitHub_main"])

    def test_metadata_reverification_and_member_are_exact(self) -> None:
        metadata = self.contract["metadata_reverification"]
        self.assertEqual(metadata["HTTP_GET_requests"], 1)
        self.assertEqual(metadata["raw_body_bytes"], 1_352_270)
        self.assertEqual(metadata["canonical_body_bytes"], 748_162)
        self.assertEqual(
            metadata["canonical_body_sha256"],
            "5e889976bf5f5c91970d35c968f5a7ee4b1075aeca0ede984414d4666845aa34",
        )
        self.assertTrue(metadata["canonical_identity_matched_frozen_source"])
        self.assertEqual(metadata["temporary_manifest_retained_bytes"], 0)
        self.assertEqual(metadata["GDF_requests"], 0)
        self.assertEqual(metadata["GDF_bytes"], 0)
        member = self.contract["exact_member"]
        self.assertEqual(member["participant"], 1)
        self.assertEqual(member["run"], 1)
        self.assertEqual(member["declared_payload_bytes"], 105_365_484)
        self.assertEqual(
            member["declared_payload_sha256"],
            "ec334466272a936986a50c120c52c57634801f028acb0fee30705f8a2dee3087",
        )
        self.assertFalse(member["signed_transport_URL_published"])

    def test_measurement_roster_is_complete_unique_and_partitioned(self) -> None:
        expected = self.contract["expected_measurement_contract"]
        groups = [
            expected["EEG_labels"],
            expected["EOG_labels"],
            expected["glove_labels"],
            expected["arm_labels"],
        ]
        self.assertEqual([len(group) for group in groups], [61, 3, 19, 13])
        labels = [label for group in groups for label in group]
        self.assertEqual(len(labels), 96)
        self.assertEqual(len(set(labels)), 96)
        self.assertEqual(expected["unique_normalized_labels_required"], 96)
        self.assertEqual(expected["sampling_rate_hz"], 512)

    def test_header_and_range_firewalls_exclude_signal_and_events(self) -> None:
        header = self.contract["header_format"]
        self.assertEqual(header["fixed_header_bytes"], 256)
        self.assertEqual(header["number_of_signals_offset"], 252)
        self.assertNotIn("patient_identification", header["decoded_fields_allowlist"])
        self.assertIn("signal_samples", header["forbidden_decoded_fields"])
        proposal = self.contract["future_real_range_proposal_not_authorized"]
        self.assertEqual(proposal["GDF_range_requests_exact"], 2)
        self.assertEqual(proposal["combined_GDF_body_bytes_maximum"], 65_536)
        self.assertTrue(proposal["ranges_nonoverlapping_and_gapless"])
        self.assertFalse(proposal["whole_file_request"])
        self.assertFalse(proposal["event_annotation_or_signal_bytes_requested"])
        self.assertEqual(proposal["redirects"], 0)
        self.assertEqual(proposal["retries"], 0)

    def test_generated_plan_is_bounded_and_real_authority_is_false(self) -> None:
        generated = self.contract["generated_qualification_plan"]
        self.assertTrue(generated["standard_library_only"])
        self.assertFalse(generated["network_client_present"])
        self.assertFalse(generated["real_execution_command_present"])
        self.assertEqual(generated["generated_replays"], 2)
        self.assertGreaterEqual(generated["minimum_named_refusal_cases"], 30)
        envelope = self.contract["resource_envelope"]
        self.assertEqual(envelope["CPU_threads"], 1)
        self.assertEqual(envelope["workers"], 1)
        self.assertEqual(envelope["network_bytes"], 0)
        authority = self.contract["authority"]
        self.assertTrue(authority["all_Tier_C_authority_flags_false"])
        self.assertIsNone(authority["active_Tier_C_packet"])
        for key, value in authority.items():
            if key not in {
                "tier",
                "all_Tier_C_authority_flags_false",
                "active_Tier_C_packet",
            }:
                self.assertFalse(value, key)

    def test_no_real_or_scientific_operation_occurred(self) -> None:
        counters = self.contract["operation_counters_at_registration"]
        self.assertEqual(counters["public_metadata_requests"], 1)
        self.assertEqual(counters["public_metadata_body_bytes"], 1_352_270)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"public_metadata_requests", "public_metadata_body_bytes"}
            )
        )
        boundary = self.contract["claim_boundary"]
        self.assertTrue(boundary["metadata_identity_reverified"])
        for key, value in boundary.items():
            if key != "metadata_identity_reverified":
                self.assertFalse(value, key)

    def test_frontier_is_compact_additive_successor(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.4.0")
        self.assertEqual(self.frontier["active_lane_id"], "NO_ACTIVE_TIER_C_GATE")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )
        header = self.frontier["header_preregistration"]
        self.assertEqual(header["protocol_id"], "OFNER-C6R-1-HG0")
        self.assertFalse(header["real_header_authorized"])
        self.assertIsNone(self.frontier["operation_boundary"]["active_tier_c_packet"])

    def test_document_states_capability_nonclaim_and_separate_gate(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no real-header authority", document)
        self.assertIn("fresh packet-bound maintainer decision", document)


if __name__ == "__main__":
    unittest.main()
