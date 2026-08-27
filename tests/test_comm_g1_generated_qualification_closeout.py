from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries" / "comm_g1_generated_qualification_result.v0.json"
CLOSEOUT = ROOT / "registries" / "comm_g1_generated_qualification_closeout.v0.json"
DOC = ROOT / "docs" / "COMM_G1_GENERATED_QUALIFICATION_CLOSEOUT.md"
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"
README = ROOT / "README.md"
START_HERE = ROOT / "START_HERE.md"


class CommG1GeneratedQualificationCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.closeout = json.loads(CLOSEOUT.read_text(encoding="utf-8"))

    def test_immutable_executor_result_is_exact(self) -> None:
        binding = self.closeout["immutable_executor_result"]
        payload = RESULT.read_bytes()
        self.assertEqual(binding["bytes"], len(payload))
        self.assertEqual(binding["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(self.result["cases"]["residual_EEG_increment"]["route"], "COMM-G1-R1")
        self.assertFalse(binding["accepted_at_closeout"])

    def test_binding_route_is_R0_and_run_is_consumed(self) -> None:
        router = self.closeout["binding_router"]
        self.assertEqual(router["route"], "COMM-G1-R0")
        self.assertEqual(router["executor_internal_route_preserved_but_not_accepted"], "COMM-G1-R1")
        consumption = self.closeout["consumption"]
        self.assertEqual(consumption["official_invocations"], 1)
        self.assertTrue(consumption["consumed"])
        self.assertFalse(consumption["rerun_allowed"])
        self.assertFalse(consumption["repair_in_place_allowed"])

    def test_all_three_proof_failures_are_explicit_and_observable(self) -> None:
        failures = {failure["id"] for failure in self.closeout["acceptance_failures"]}
        self.assertEqual(
            failures,
            {
                "COMM-G1-CF01-incomplete-replay-fingerprint",
                "COMM-G1-CF02-replays-not-isolated",
                "COMM-G1-CF03-adversarial-family-incomplete",
            },
        )
        cases = self.result["cases"]
        self.assertEqual(
            cases["cue_only"]["fixture_sha256"], cases["timing_only"]["fixture_sha256"]
        )
        self.assertEqual(
            cases["timing_only"]["fixture_sha256"], cases["no_signal"]["fixture_sha256"]
        )
        refusal_ids = set(self.result["adversarial_qualification"]["refusal_ids"])
        self.assertFalse(any("symlink" in value for value in refusal_ids))
        self.assertFalse(any("resource" in value for value in refusal_ids))

    def test_measurements_are_under_caps_but_do_not_override_proof_failure(self) -> None:
        measurement = self.closeout["measured_execution"]
        self.assertLessEqual(measurement["runtime_seconds"], 180)
        self.assertLessEqual(measurement["peak_process_tree_RSS_bytes"], 512 << 20)
        self.assertLessEqual(measurement["generated_input_bytes"], 32 << 20)
        self.assertLessEqual(measurement["public_output_bytes"], 1 << 20)
        self.assertEqual(measurement["total_parameter_update_fits"], 60)
        self.assertEqual(measurement["prediction_rows"], 1440)
        self.assertEqual(measurement["post_target_updates"], 0)

    def test_real_counters_and_claims_remain_zero_or_false(self) -> None:
        self.assertTrue(all(value == 0 for value in self.closeout["access_counters"].values()))
        self.assertTrue(all(value is False for value in self.closeout["claim_boundary"].values()))
        gate = self.closeout["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(gate["all_authority_flags_false"])

    def test_document_is_plain_about_raw_output_and_rejection(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for phrase in (
            "Why the score is not accepted",
            "Identical hashes",
            "not the two separate clean workdirs",
            "does not explicitly exercise",
            "rejected at closeout",
            "may not be rerun",
            "No real EEG was accessed",
        ):
            self.assertIn(phrase, text)

    def test_public_status_surfaces_bind_the_R0_closeout(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        experiment = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["generated_experiment_preregistration"]
        closeout = experiment["generated_qualification_closeout"]
        self.assertEqual(closeout["binding_closeout_route"], "COMM-G1-R0")
        self.assertFalse(closeout["accepted_synthetic_score"])
        self.assertFalse(closeout["rerun_allowed"])
        self.assertEqual(closeout["acceptance_failure_count"], 3)
        self.assertEqual(frontier["active_lane_id"], "DREYER-C5R-1-HL")
        for path in (README, START_HERE):
            text = path.read_text(encoding="utf-8")
            self.assertIn("COMM-G1-R0", text)
            self.assertIn("consumed", text)


if __name__ == "__main__":
    unittest.main()
