import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/current_research_frontier.v0.json"


class CurrentResearchFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_active_lane_are_exact(self):
        self.assertEqual(
            self.frontier["schema_name"],
            "neurodecodekit.current_research_frontier",
        )
        self.assertEqual(self.frontier["schema_version"], "0.1.0")
        self.assertEqual(self.frontier["active_lane_id"], "BNCI-C3C5-1-Q")
        self.assertEqual(
            self.frontier["status"],
            "Stage_Q_implementation_and_generated_core_prepared_pending_remote_green",
        )

    def test_proof_chain_records_green_recovery_activation(self):
        proof = self.frontier["completed_proof"]
        self.assertEqual(
            proof["G1_proof_closeout_commit"],
            "cf476982d70cbd6c710b7d0a67352765155c6bc1",
        )
        self.assertEqual(
            proof["redirect_recovery_implementation_commit"],
            "09a19d1c1c498bdd6e0ece2fbecb6d15917bdefa",
        )
        self.assertEqual(
            proof["redirect_recovery_activation_commit"],
            "492a36a818bb00ca6bb86de6592c6cd0d5134f90",
        )
        self.assertEqual(proof["redirect_recovery_activation_CI_run_id"], 32_807_676_008)
        self.assertTrue(proof["both_activation_jobs_green"])
        self.assertEqual(
            proof["Stage_A_result_commit"],
            "96d7f0569a54b05f8031d2e3943658ef598e38a5",
        )
        self.assertTrue(proof["both_Stage_A_result_jobs_green"])

    def test_prelaunch_rejection_did_not_consume_recovery(self):
        rejection = self.frontier["prelaunch_rejection"]
        self.assertFalse(rejection["process_created"])
        self.assertFalse(rejection["replacement_recovery_invocation_consumed"])
        for key in (
            "manifest_requests",
            "payload_requests",
            "network_body_bytes",
            "accepted_payload_bytes",
            "recovery_marker_writes",
            "ignored_path_operations",
            "MAT_semantic_opens",
            "model_runs",
            "target_deliveries",
            "scores",
        ):
            self.assertEqual(rejection[key], 0, key)

    def test_recovery_resources_and_stage_order_are_frozen(self):
        envelope = self.frontier["active_Stage_Q_envelope"]
        self.assertEqual(envelope["registered_invocations_remaining_after_activation"], 1)
        self.assertEqual(envelope["MAT_content_opens_maximum"], 18)
        self.assertEqual(envelope["CPU_threads"], 1)
        self.assertEqual(envelope["workers"], 1)
        self.assertEqual(envelope["reruns"], 0)
        self.assertEqual(
            self.frontier["evidence_sequence"],
            [
                "G1_generated_proof",
                "A_opaque_acquisition",
                "Q_target_blind_validation",
                "P_target_firewalled_prediction_freeze",
                "T_one_frozen_score",
            ],
        )
        result = self.frontier["Stage_A_recovery_result"]
        self.assertEqual(result["payload_files"], 18)
        self.assertEqual(result["accepted_payload_bytes"], 779_873_919)
        self.assertEqual(result["MAT_semantic_opens"], 0)
        self.assertEqual(result["model_runs"], 0)
        self.assertEqual(result["scores"], 0)
        generated = self.frontier["Stage_Q_generated_qualification_result"]
        self.assertEqual(generated["generated_trials"], 288)
        self.assertEqual(generated["real_or_private_path_opens"], 0)
        self.assertEqual(generated["model_runs"], 0)

    def test_all_five_scientific_goals_and_claims_remain_unestablished(self):
        self.assertEqual(
            set(self.frontier["five_scientific_goals"].values()),
            {"not_established"},
        )
        claims = self.frontier["claim_boundary"]
        for key, value in claims.items():
            if key not in {
                "engineering_capability_established",
                "verified_recovery_bundle_acquired",
            }:
                self.assertFalse(value, key)
        self.assertTrue(claims["verified_recovery_bundle_acquired"])

    def test_control_plane_entrypoints_name_the_current_gate(self):
        expected = {
            "AGENTS.md": "Stage Q generated semantic core",
            "START_HERE.md": "Current Gate: BNCI-C3C5-1 Stage Q Implementation",
            "README.md": "Stage Q implementation",
            "docs/CODEX_HANDOFF.md": "Current gate, 2026-08-25",
            "docs/NEXT_20_LOOPS_TRACKER.md": "Stage Q implementation gate (2026-08-25)",
        }
        for path, phrase in expected.items():
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(phrase, text, path)
        start = (ROOT / "START_HERE.md").read_text(encoding="utf-8")[:8_000]
        self.assertNotIn("Current Gate: BNCI-C3C5-1 G1 Proof Closeout", start)


if __name__ == "__main__":
    unittest.main()
