from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v7.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v6.json"
POSTMORTEM = ROOT / "registries/neural_payload_transport_admission_postmortem.v0.json"


class CurrentResearchFrontierV7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_frontier_is_exact_additive_successor(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.8.0")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )
        self.assertTrue(POSTMORTEM.is_file())
        self.assertIsNone(self.frontier["active_lane_id"])

    def test_consumed_result_proof_is_green_and_closed(self) -> None:
        proof = self.frontier["green_consumed_result_proof"]
        self.assertEqual(
            proof["proof_closeout_commit"],
            "750adc39e27ae578fa38381319648a13706b6af1",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 33_280_371_097)
        self.assertEqual(proof["proof_closeout_base_python_job_id"], 99_174_411_928)
        self.assertEqual(
            proof["proof_closeout_optional_neuro_readers_job_id"],
            99_174_412_006,
        )
        self.assertTrue(proof["both_proof_jobs_green"])
        self.assertTrue(proof["registered_invocation_consumed"])
        self.assertFalse(
            proof["retry_rerun_repair_resume_substitute_or_reinterpret_allowed"]
        )

    def test_postmortem_is_artifact_only_and_not_biology(self) -> None:
        result = self.frontier["artifact_only_postmortem"]
        self.assertEqual(result["network_requests"], 0)
        self.assertEqual(result["real_or_private_path_operations"], 0)
        self.assertEqual(result["payload_header_signal_event_target_or_label_reads"], 0)
        self.assertEqual(result["model_training_prediction_or_score_operations"], 0)
        self.assertFalse(result["shared_endpoint_or_server_cause_established"])
        self.assertFalse(result["biological_result"])

    def test_only_generated_NPA1_is_the_next_active_capability(self) -> None:
        architecture = self.frontier["selected_architecture"]
        self.assertEqual(architecture["protocol_id"], "NPA1-v0")
        self.assertTrue(architecture["generated_only"])
        self.assertEqual(architecture["network_requests"], 0)
        self.assertEqual(architecture["CPU_threads"], 1)
        authority = self.frontier["operation_authority"]
        self.assertTrue(
            authority["generated_fixture_only_NPA1_G_implementation_after_frontier_green"]
        )
        for key, value in authority.items():
            if key != "generated_fixture_only_NPA1_G_implementation_after_frontier_green":
                self.assertFalse(value, key)

    def test_no_source_canary_or_claim_is_promoted(self) -> None:
        self.assertIsNone(self.frontier["source_routing"]["fresh_source_selected"])
        self.assertFalse(self.frontier["future_transport_canary"]["authorized_now"])
        boundary = self.frontier["claim_boundary"]
        self.assertTrue(boundary["transport_admission_architecture_frozen"])
        for key, value in boundary.items():
            if key != "transport_admission_architecture_frozen":
                self.assertFalse(value, key)

    def test_current_control_plane_names_v7_and_generated_next_step(self) -> None:
        for relative in (
            "AGENTS.md",
            "README.md",
            "START_HERE.md",
            "docs/CODEX_HANDOFF.md",
            "docs/SCIENTIFIC_CONVERGENCE_AND_INVENTION_PLAN.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")[:16_000]
            self.assertIn("current_research_frontier.v7.json", text, relative)
            self.assertIn("NPA1", text, relative)


if __name__ == "__main__":
    unittest.main()
