import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT
    / "registries/bnci_2014_001_cross_participant_eeg_gain_authorization_decision.v0.json"
)
DOCUMENT = (
    ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_AUTHORIZATION_DECISION.md"
)


class BNCI2014001CrossParticipantEEGGainAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_exact_short_form_message_and_green_packet_are_bound(self):
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"], hashlib.sha256(b"continue").hexdigest()
        )
        self.assertEqual(user["sole_active_Tier_C_packet"], "BNCI-C3C5-1")
        self.assertFalse(user["message_silently_corrected"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])

        request = self.decision["green_request"]
        self.assertEqual(request["commit"], "3197390d45bfc8d19c9df2f3675166815f56f028")
        self.assertEqual(request["CI_run_id"], 32_749_812_954)
        self.assertTrue(request["both_required_jobs_green"])
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(proof["commit"], "9e7c70dcdecae8264ea988563c05e7b2f1da7fd0")
        self.assertEqual(proof["CI_run_id"], 32_751_503_586)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_every_proof_artifact_identity_is_exact(self):
        rows = self.decision["bound_proof_artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"], row["path"])
        self.assertEqual(len(rows), self.decision["bound_proof_artifact_summary"]["count"])
        self.assertEqual(
            sum(row["bytes"] for row in rows),
            self.decision["bound_proof_artifact_summary"]["bytes"],
        )

    def test_decision_has_delayed_effect_and_strict_stage_order(self):
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )
        order = self.decision["required_order"]
        self.assertEqual(order[0], "decision_commit_push_and_both_CI_jobs_green")
        self.assertEqual(order[-1], "stop_without_rerun_or_post_target_update")
        auth = self.decision["authorization"]
        self.assertTrue(auth["G1_generated_mocked_implementation_after_decision_green"])
        self.assertTrue(auth["A_one_exact_acquisition_after_G1_green"])
        self.assertTrue(auth["Q_one_target_blind_qualification_after_A_manifest_green"])
        self.assertTrue(auth["P_nine_fold_isolated_fits_after_Q_green"])
        self.assertTrue(auth["T_one_target_delivery_after_prediction_freeze_green"])
        self.assertFalse(auth["implementation_or_any_stage_authorized_at_decision_recording"])

    def test_experiment_and_scientific_gates_are_unchanged(self):
        payload = self.decision["registered_payload"]
        self.assertEqual(payload["file_count"], 18)
        self.assertEqual(payload["accepted_payload_bytes_exact"], 779_873_919)
        self.assertFalse(payload["BDF_or_HTML_derivative_allowed"])
        experiment = self.decision["experiment"]
        self.assertEqual(experiment["outer_folds"], 9)
        self.assertEqual(experiment["held_out_session"], "E")
        self.assertEqual(experiment["held_out_T_session_use"], "forbidden")
        self.assertEqual(experiment["held_out_person_calibration_rows"], 0)
        self.assertFalse(experiment["target_or_artifact_derived_exclusion"])
        self.assertEqual(
            self.decision["C3_gate"]["participant_macro_four_class_balanced_accuracy_minimum"],
            0.35,
        )
        self.assertEqual(
            self.decision["C5_partial_gate"]["P_minus_P_plus_E_nats_per_trial_minimum"],
            0.03,
        )

    def test_resources_are_bounded_and_one_shot(self):
        caps = self.decision["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1)
        )
        self.assertEqual(caps["payload_bytes_exact"], 779_873_919)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 2 << 30)
        self.assertGreaterEqual(caps["free_disk_bytes_minimum_before_acquisition"], 5 << 30)
        self.assertLessEqual(caps["peak_RSS_bytes_maximum"], 1 << 30)
        self.assertEqual(caps["target_deliveries"], 1)
        self.assertEqual(caps["scoring_events"], 1)
        self.assertEqual(caps["scientific_reruns"], 0)
        self.assertEqual(caps["post_target_updates"], 0)

    def test_recording_performed_no_protected_operation_or_claim(self):
        self.assertTrue(
            all(value == 0 for value in self.decision["decision_only_counters"].values())
        )
        boundary = self.decision["claim_boundary"]
        self.assertEqual(boundary["maximum_route"], "BNCIC3C5-R5")
        self.assertFalse(boundary["language_or_arbitrary_thought_decoding"])
        self.assertFalse(boundary["live_portable_home_or_clinical_use"])
        self.assertFalse(boundary["scientific_claim_established_by_decision"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Scientific claim not established", document)
        self.assertIn("generated/mock G1 qualification", document)

    def test_immediate_gate_remains_decision_remote_green(self):
        gate = self.decision["next_gate"]
        self.assertTrue(gate["decision_commit_push_and_both_CI_jobs_green_required"])
        self.assertFalse(gate["G1_implementation_or_qualification_allowed_before_decision_green"])
        self.assertFalse(gate["real_network_payload_or_MAT_access_allowed_before_G1_green"])


if __name__ == "__main__":
    unittest.main()
