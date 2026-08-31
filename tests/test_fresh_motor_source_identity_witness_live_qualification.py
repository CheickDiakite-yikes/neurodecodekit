from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import fresh_motor_source_identity_witness as core
from neurodecodekit.datasets import fresh_motor_source_identity_witness_live as live
from neurodecodekit.datasets import (
    fresh_motor_source_identity_witness_live_qualification as qualification,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = (
    ROOT / "src/neurodecodekit/datasets/fresh_motor_source_identity_witness_live_qualification.py"
)


class FreshMotorSourceIdentityWitnessLiveQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.network_patches = (
            mock.patch("socket.getaddrinfo", side_effect=AssertionError("network closed")),
            mock.patch("socket.socket", side_effect=AssertionError("network closed")),
            mock.patch.object(live, "_peak_rss_bytes", return_value=1),
        )
        for patcher in self.network_patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_generated_decision_qualifies_future_schema_without_authority(self) -> None:
        decision = qualification.build_generated_execution_decision()
        live.validate_execution_decision(decision)
        self.assertEqual(decision["packet_id"], live.PACKET_ID)
        self.assertEqual(decision["packet_artifacts"], [dict(row) for row in live.PACKET_ARTIFACTS])
        authority = decision["authorization_after_decision_green"]
        self.assertFalse(authority["payload_header_signal_event_annotation_target_or_label"])
        self.assertFalse(authority["model_checkpoint_training_inference_prediction_or_score"])
        self.assertFalse(authority["release_or_scientific_claim_upgrade"])

    def test_green_live_implementation_decision_is_exact(self) -> None:
        with mock.patch.object(
            live,
            "_git",
            side_effect=AssertionError("shallow CI history must stay unopened"),
        ) as historical_git:
            decision = qualification.load_green_live_implementation_decision(ROOT)
        self.assertEqual(decision["decision_id"], live.LIVE_IMPLEMENTATION_DECISION_ID)
        self.assertFalse(
            decision["authorization_after_decision_green"]["GitHub_API_or_official_index_contact"]
        )
        historical_git.assert_not_called()

    def test_generated_contact_replays_all_roots_without_socket_access(self) -> None:
        replay = qualification._run_replay(ROOT)
        self.assertEqual(replay.receipt["Base_Python_check_run_id"], 101)
        self.assertEqual(replay.receipt["Optional_Neuro_Readers_check_run_id"], 102)
        self.assertEqual(replay.ledger["total_root_count"], 17)
        self.assertEqual(replay.ledger["total_page_count"], 34)
        self.assertEqual(replay.contact_count, 38)
        self.assertEqual(replay.marker_guard_observations, 38)
        self.assertEqual(replay.request_serialization_assertions, 38)
        self.assertEqual(replay.TLS_context_assertions, 38)
        self.assertEqual(replay.chunked_responses, 1)
        self.assertEqual(replay.redirect_hops, 1)
        self.assertGreater(
            replay.ledger["total_wire_bytes"],
            replay.ledger["total_entity_body_bytes"],
        )
        self.assertEqual(replay.state_transcript, live.STATE_MACHINE)
        self.assertEqual(replay.audit.candidate_semantic_accesses, 0)
        self.assertGreater(replay.audit.control_fields_accessed, 0)
        self.assertGreater(replay.audit.opaque_members_skipped, 0)
        public = core.canonical_json_bytes(replay.ledger, newline=True)
        self.assertNotIn(qualification.POISON_PREFIX, public)

    def test_report_byte_accounting_converges(self) -> None:
        report = {
            "schema_name": "generated-test",
            "route": "GENERATED_ONLY",
            "scientific_claim_established": False,
        }
        rendered, payload = qualification._render_report(report)
        self.assertEqual(rendered["report_bytes"], len(payload))
        self.assertEqual(payload, core.canonical_json_bytes(rendered, newline=True))
        self.assertLessEqual(len(payload), qualification.MAX_QUALIFICATION_REPORT_BYTES)

    def test_direct_transport_refusal_matrix_and_connection_close(self) -> None:
        observations, connection_close = qualification._run_direct_transport_matrix(ROOT)
        self.assertEqual(len(observations), 6)
        self.assertEqual(connection_close, 1)
        self.assertTrue(
            all(
                row.startswith(("WITNESS_TRANSPORT_PARK:", "WITNESS_CAP_PARK:"))
                for row in observations
            )
        )
        self.assertTrue(any(row.endswith(":PAGE_BYTE_CAP") for row in observations))
        self.assertTrue(any(row.endswith(":WIRE_BYTE_CAP") for row in observations))

    def test_qualification_uses_direct_transport_but_not_official_execute(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "import socket",
            "from socket",
            "execute_registered_witness(",
            "urllib.request",
            "requests.",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("live.direct_TLS_contact(", source)

    def test_consumed_public_qualification_entry_point_cannot_replay(self) -> None:
        with mock.patch.object(
            qualification,
            "_run_replay",
            side_effect=AssertionError("consumed qualification replayed"),
        ) as replay:
            with self.assertRaises(live.LiveWitnessRefusal) as raised:
                qualification.run_generated_live_qualification()
        self.assertEqual(raised.exception.code, "LIVE_AUTHORITY_REFUSE")
        replay.assert_not_called()


if __name__ == "__main__":
    unittest.main()
