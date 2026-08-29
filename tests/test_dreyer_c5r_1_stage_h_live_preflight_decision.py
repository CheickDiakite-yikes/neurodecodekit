import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT / "registries" / "dreyer_c5r_1_stage_h_live_preflight_decision.v0.json"
)
REQUEST_PATH = (
    ROOT
    / "registries"
    / "dreyer_c5r_1_stage_h_live_preflight_authorization_request.v0.json"
)
DOC_PATH = ROOT / "docs" / "DREYER_C5R_1_STAGE_H_LIVE_PREFLIGHT_DECISION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


class DreyerStageHLivePreflightDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.document = DOC_PATH.read_text(encoding="utf-8")

    def test_actual_maintainer_words_are_preserved(self):
        words = "continue, make a deep push"
        self.assertEqual(self.decision["maintainer_words"], words)
        self.assertEqual(
            self.decision["maintainer_words_sha256"],
            hashlib.sha256(words.encode()).hexdigest(),
        )
        user = self.decision["user_authorization"]
        self.assertTrue(user["actual_message_preserved_verbatim"])
        self.assertEqual(user["sole_active_Tier_C_packet"], "DREYER-C5R-1-HL")
        self.assertTrue(
            user[
                "packet_commit_CI_scope_exact_member_ordered_barriers_and_exclusions_identified_before_message"
            ]
        )
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertFalse(user["scope_expansion_by_inference"])

    def test_request_and_proof_are_exact_green_anchors(self):
        request = self.decision["green_request"]
        self.assertEqual(
            request["commit"], "5191e79e2ccfa50b5042a24357c0c22d68d8f088"
        )
        self.assertEqual(request["CI_run_id"], 32_934_958_878)
        proof = self.decision["green_request_proof"]
        self.assertEqual(
            proof["commit"], "821fad17e06914375c50a7d0dd7017458b2df838"
        )
        self.assertEqual(proof["CI_run_id"], 32_936_247_679)
        self.assertEqual(proof["base_python_job_id"], 98_077_895_278)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 98_077_895_460)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["fresh_verification_calls"], 1)

    def test_all_bound_artifacts_match_current_bytes(self):
        for binding in self.decision["bound_artifacts"].values():
            path = ROOT / binding["path"]
            self.assertEqual(binding["bytes"], path.stat().st_size)
            self.assertEqual(binding["sha256"], sha256(path))
            if "git_blob_sha1" in binding:
                self.assertEqual(binding["git_blob_sha1"], git_blob_sha1(path))

    def test_exact_member_copies_the_immutable_request(self):
        self.assertEqual(self.decision["exact_member"], {
            key: self.request["exact_member"][key]
            for key in ("dataset", "NEMAR_dataset", "revision", "path", "url", "bytes", "sha256")
        })
        summary = self.decision["bound_request_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 23_950)
        self.assertEqual(
            summary["canonical_artifact_set_sha256"],
            "e41870d4d1623861f02f52adc390c2e4b9f9e38247867e6a40acb9d4dcda07d4",
        )

    def test_authority_is_ordered_and_does_not_expand_scope(self):
        auth = self.decision["authorization"]
        self.assertTrue(auth["implement_HL1_additive_standard_library_wrapper_after_decision_green"])
        self.assertEqual(auth["run_HL1_registered_generated_mock_qualification_maximum"], 1)
        self.assertTrue(auth["run_HL2_after_exact_decision_implementation_and_activation_remote_green"])
        self.assertEqual(auth["HL2_registered_invocations_maximum"], 1)
        self.assertEqual(auth["HL2_real_HTTP_GET_requests_exact"], 1)
        self.assertEqual(auth["HL2_successful_payload_body_bytes_exact"], 14_805_604)
        for name in (
            "remaining_119_payload_requests",
            "annotation_record_reads",
            "signal_sample_semantic_reads",
            "target_or_label_reads",
            "model_or_checkpoint_opens",
            "training_runs",
            "model_inference_runs",
            "prediction_sets",
            "target_deliveries",
            "scores",
            "retries",
            "reruns",
            "release_operations",
            "scientific_claim_upgrades",
        ):
            self.assertEqual(auth[name], 0, name)

    def test_all_nine_safety_controls_are_bound(self):
        self.assertEqual(len(self.decision["required_wrapper_controls"]), 9)
        self.assertEqual(
            self.decision["required_wrapper_controls"],
            json.loads(
                (
                    ROOT
                    / "registries"
                    / "dreyer_c5r_1_stage_h_live_implementation_safety_review.v0.json"
                ).read_text(encoding="utf-8")
            )["required_wrapper_controls"],
        )

    def test_order_requires_two_remote_green_barriers_and_marker_before_opener(self):
        order = self.decision["required_execution_order"]
        self.assertLess(
            order.index("test_commit_push_and_obtain_green_CI_for_this_decision"),
            order.index("implement_and_generated_qualify_HL1_without_real_or_network_operations"),
        )
        self.assertLess(
            order.index("commit_push_and_obtain_green_CI_for_exact_HL1_implementation"),
            order.index("create_commit_push_and_obtain_green_CI_for_exact_HL2_activation"),
        )
        self.assertLess(
            order.index("durably_write_the_unique_consumed_marker"),
            order.index("construct_the_proxy_free_verified_TLS_opener"),
        )
        gate = self.decision["next_gate"]
        self.assertFalse(gate["HL1_may_begin_before_decision_green"])
        self.assertFalse(gate["HL2_may_begin_before_HL1_implementation_and_activation_green"])
        self.assertFalse(gate["rerun_available"])

    def test_decision_only_counters_are_zero_except_one_ci_verification(self):
        counters = self.decision["decision_only_access_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
        for name, value in counters.items():
            if name == "GitHub_CI_verification_calls":
                continue
            if name == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, name)

    def test_document_preserves_the_claim_boundary(self):
        compact = " ".join(self.document.split())
        self.assertIn("The decision is ineffective until its own exact commit", compact)
        self.assertIn("Any outcome after the H-L2 consumed marker is final", compact)
        self.assertIn("Scientific claim not established", compact)
        self.assertIn("thought or language decoding", compact)


if __name__ == "__main__":
    unittest.main()
