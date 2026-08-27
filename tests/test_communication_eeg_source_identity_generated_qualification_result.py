from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import communication_eeg_source_identity as source_identity

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries/communication_eeg_source_identity_generated_qualification_result.v0.json"
)
DOC_PATH = (
    ROOT / "docs/COMMUNICATION_EEG_SOURCE_IDENTITY_GENERATED_QUALIFICATION_RESULT.md"
)
RESULT_BYTES = 3_001
RESULT_SHA256 = "39b0833ac821246a7159fda7575f6cfa3c1f621fd3acb64af6f3fa07fe3fb48d"


class CommunicationEEGSourceIdentityGeneratedResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)

    def test_exact_result_identity_and_consumed_route(self) -> None:
        self.assertEqual(len(self.payload), RESULT_BYTES)
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), RESULT_SHA256)
        self.assertEqual(self.result["route"], "COMM-L0-R1")
        self.assertEqual(
            self.result["status"], "generated_qualification_passed_consumed"
        )
        self.assertTrue(self.result["qualification"]["consumed"])
        self.assertFalse(self.result["qualification"]["rerun_allowed"])

    def test_registered_replay_and_refusal_schedule_passed(self) -> None:
        qualification = self.result["qualification"]
        self.assertEqual(qualification["success_replays"], 2)
        self.assertEqual(qualification["adversarial_refusals"], 20)
        self.assertTrue(qualification["all_expected_refusals_passed"])
        self.assertEqual(len(qualification["case_names"]), 20)

    def test_generated_selection_and_measurements_are_exact(self) -> None:
        selected = self.result["selected_summary"]
        self.assertEqual(selected["participant_count"], 10)
        self.assertEqual(selected["selected_raw_BDF_count"], 10)
        self.assertEqual(selected["selected_companion_count"], 30)
        self.assertEqual(selected["selected_object_count"], 40)
        self.assertEqual(selected["selected_payload_bytes"], 1_029_510)
        self.assertLessEqual(
            selected["selected_payload_bytes"], source_identity.MAX_SELECTED_BYTES
        )
        measurements = self.result["measurements"]
        self.assertEqual(measurements["generated_input_bytes"], 39_137)
        self.assertEqual(measurements["generated_output_bytes"], RESULT_BYTES)
        self.assertEqual(measurements["peak_RSS_bytes"], 22_069_248)
        self.assertLessEqual(
            measurements["runtime_seconds"], source_identity.MAX_RUNTIME_SECONDS
        )
        self.assertIsNone(measurements["producer_is_causal"])
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_every_real_model_score_and_claim_counter_is_zero(self) -> None:
        counters = self.result["access_counters"]
        self.assertEqual(counters["generated_response_bytes"], 39_137)
        for key, value in counters.items():
            if key != "generated_response_bytes":
                self.assertEqual(value, 0, key)
        self.assertEqual(self.result["measurements"]["network_bytes"], 0)
        self.assertEqual(self.result["measurements"]["real_payload_bytes"], 0)

    def test_committed_result_refuses_rerun_before_fixture_work(self) -> None:
        with self.assertRaises(source_identity.CommunicationSourceIdentityRefusal) as ctx:
            source_identity.qualify_generated_source_identity(RESULT_PATH)
        self.assertEqual(ctx.exception.refusal_id, source_identity.REFUSAL_IDS[8])

    def test_closeout_states_capability_nonclaim_and_next_gate(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("qualification is consumed and must not be rerun", text)
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("all-false Tier C request", text)
        self.assertIn("DREYER-C5R-1-HL", text)


if __name__ == "__main__":
    unittest.main()
