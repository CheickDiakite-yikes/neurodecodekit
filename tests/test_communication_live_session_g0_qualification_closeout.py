from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/communication_live_session_g0_generated_result.v0.json"
)
CLOSEOUT_PATH = (
    ROOT
    / "registries/communication_live_session_g0_qualification_closeout.v0.json"
)
DOC_PATH = ROOT / "docs/COMMUNICATION_LIVE_SESSION_G0_QUALIFICATION_CLOSEOUT.md"


class CommunicationLiveSessionG0QualificationCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result_bytes = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.result_bytes)
        cls.closeout = json.loads(CLOSEOUT_PATH.read_text(encoding="utf-8"))

    def test_exact_result_is_bound_and_consumed_once(self) -> None:
        bound = self.closeout["official_result"]
        self.assertEqual(len(self.result_bytes), bound["bytes"])
        self.assertEqual(hashlib.sha256(self.result_bytes).hexdigest(), bound["sha256"])
        self.assertEqual(self.result["route"], "COMM-LIVE-G0-R1")
        self.assertTrue(self.result["official_invocation_consumed"])
        self.assertTrue(self.closeout["next_gate"]["COMM_LIVE_G0_closed_and_consumed"])
        self.assertFalse(self.closeout["next_gate"]["rerun_allowed"])

    def test_replay_refusal_and_measurement_summary_matches_result(self) -> None:
        qualification = self.closeout["qualification"]
        replay = self.result["replay_equivalence"]
        self.assertEqual(replay["deterministic_replays"], 2)
        self.assertTrue(replay["byte_equivalent"])
        self.assertEqual(qualification["registered_refusal_count"], 33)
        self.assertEqual(self.result["adversarial_qualification"]["refusal_count"], 33)
        self.assertTrue(
            self.result["adversarial_qualification"]["every_named_family_executed"]
        )
        for key in (
            "runtime_seconds",
            "peak_RSS_bytes",
            "public_output_bytes",
            "temporary_generated_bytes",
            "cpu_threads",
            "workers",
        ):
            self.assertEqual(self.closeout["measurements"][key], self.result["measurements"][key])

    def test_all_forbidden_operations_and_claims_remain_zero_or_false(self) -> None:
        counters = self.closeout["operation_counters"]
        self.assertEqual(counters["official_generated_qualification_runs"], 1)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key != "official_generated_qualification_runs"
            )
        )
        claims = self.closeout["claim_boundary"]
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_value"}:
                self.assertFalse(value, key)

    def test_warning_schema_caveat_is_preserved_without_result_rewrite(self) -> None:
        self.assertEqual(self.closeout["warnings"], self.result["warnings"])
        interpretation = self.closeout["warning_interpretation"]
        self.assertTrue(
            interpretation["development_path_wording_inherited_from_inner_repeatable_harness"]
        )
        self.assertTrue(
            interpretation[
                "official_status_and_consumed_marker_take_precedence_for_invocation_state"
            ]
        )
        self.assertFalse(interpretation["result_modified_or_rerun_to_change_warning"])

    def test_human_closeout_states_engineering_and_scientific_boundaries(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("closed and consumed", text)


if __name__ == "__main__":
    unittest.main()
