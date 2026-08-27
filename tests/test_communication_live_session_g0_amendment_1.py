from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMENDMENT = (
    ROOT / "registries" / "communication_live_session_g0_amendment_1.v0.json"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommunicationLiveSessionG0Amendment1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))

    def test_parent_registration_and_proof_are_exact(self) -> None:
        for key in ("document", "contract"):
            artifact = self.amendment["parent_registration"][key]
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
        for key in ("document", "registry"):
            artifact = self.amendment["parent_proof"][key]
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
        self.assertEqual(self.amendment["parent_proof"]["CI_run_id"], 33104990326)

    def test_sample_cadence_is_partition_invariant(self) -> None:
        cadence = self.amendment["sample_cadence"]
        self.assertEqual(cadence["processor_frame_valid_samples"], 16)
        self.assertEqual(cadence["warmup_valid_samples_per_generation"], 32)
        self.assertEqual(cadence["first_output_eligible_frame_index"], 2)
        self.assertEqual(cadence["frame_index_origin"], 0)
        self.assertFalse(cadence["transport_chunks_define_processor_updates"])
        self.assertTrue(cadence["gap_or_reconnect_discards_incomplete_tail"])
        self.assertEqual(len(cadence["partition_schedules_required"]), 4)
        self.assertEqual(
            self.amendment["superseded_fields"][
                "commit_policy.warmup_chunks_per_generation"
            ],
            2,
        )

    def test_clock_domains_fail_closed_when_not_comparable(self) -> None:
        clocks = self.amendment["clock_domains"]
        self.assertTrue(clocks["order_checks_are_domain_local"])
        self.assertFalse(clocks["numeric_values_from_different_domains_may_be_subtracted"])
        self.assertTrue(clocks["cross_domain_latency_requires_verified_mapping"])
        self.assertIsNone(clocks["unavailable_value"])
        self.assertTrue(clocks["unavailable_flag_required"])
        self.assertFalse(clocks["chunk_local_arrival_boundaries_in_replay_equivalence_payload"])

    def test_hash_preimages_are_exact_and_nonrecursive(self) -> None:
        encoding = self.amendment["canonical_encoding"]
        self.assertTrue(encoding["sort_keys"])
        self.assertFalse(encoding["allow_nan"])
        self.assertFalse(encoding["unknown_fields_allowed"])
        hashes = self.amendment["hash_preimages"]
        payload = hashes["valid_payload_sha256"]
        self.assertEqual(payload["domain_ascii"], "NDK-SOURCE-VALID-PAYLOAD-v0")
        self.assertEqual(payload["domain_terminator_hex"], "00")
        self.assertEqual(payload["order"], "sample_major_channel_order_frozen")
        self.assertEqual(payload["byte_order"], "little_endian")
        self.assertFalse(payload["padding_included"])
        semantic = hashes["semantic_prefix_sha256"]
        self.assertEqual(semantic["domain_ascii"], "NDK-SOURCE-SEMANTIC-v0")
        self.assertEqual(semantic["domain_terminator_hex"], "00")
        self.assertTrue(semantic["snapshot_persists_digest_bytes_and_element_count"])
        self.assertFalse(semantic["implementation_specific_hash_object_serialized"])
        envelope = hashes["chunk_envelope_sha256"]
        self.assertEqual(
            envelope["canonical_envelope_field_omitted"],
            "hashes.chunk_envelope_sha256",
        )
        self.assertFalse(envelope["self_reference_allowed"])

    def test_push_is_transactional_and_target_free(self) -> None:
        push = self.amendment["transactional_push"]
        self.assertTrue(all(push.values()))
        self.assertEqual(len(self.amendment["forbidden_key_scan_surfaces"]), 5)
        self.assertIn("snapshot_sha256", self.amendment["snapshot_binding_fields"])

    def test_authority_and_claims_remain_closed(self) -> None:
        allowed = {
            "generated_implementation_after_amendment_green",
            "generated_qualification_after_amended_implementation_green",
        }
        for key, value in self.amendment["authority"].items():
            self.assertEqual(value, key in allowed, key)
        self.assertTrue(
            all(value == 0 for value in self.amendment["operation_counters"].values())
        )
        self.assertTrue(
            all(value is False for value in self.amendment["claim_boundary"].values())
        )
        self.assertTrue(self.amendment["active_gate"]["all_authority_flags_false"])

    def test_frontier_pauses_implementation_until_amendment_green(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        live = frontier["parallel_tier_A_communication_program"][
            "generated_live_session_preregistration"
        ]
        amendment = live["amendment_1"]
        self.assertEqual(amendment["amendment_id"], "COMM-LIVE-G0-A1")
        self.assertEqual(amendment["status"], "pending_own_remote_green")
        self.assertFalse(live["generated_implementation_authorized_now"])
        self.assertFalse(live["generated_qualification_authorized_now"])


if __name__ == "__main__":
    unittest.main()
