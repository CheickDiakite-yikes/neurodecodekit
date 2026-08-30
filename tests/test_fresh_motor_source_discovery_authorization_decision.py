from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "registries/fresh_motor_source_discovery_authorization_decision.v0.json"
DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_DISCOVERY_AUTHORIZATION_DECISION.md"


class FreshMotorSourceDiscoveryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_actual_words_are_preserved_without_scope_expansion(self) -> None:
        words = (
            "lets do it, attack this with tremendous relentlessness, get real "
            "results, do what it takes, think outside the box"
        )
        self.assertEqual(self.decision["maintainer_words"], words)
        self.assertEqual(self.decision["maintainer_words_utf8_bytes"], len(words.encode()))
        self.assertEqual(
            self.decision["maintainer_words_sha256"],
            hashlib.sha256(words.encode()).hexdigest(),
        )
        user = self.decision["user_authorization"]
        self.assertTrue(user["actual_message_preserved_verbatim"])
        self.assertEqual(user["single_named_packet_before_message"], "FMSR1-DISCOVERY-M0")
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertFalse(user["relentlessness_language_expands_scope"])
        self.assertFalse(user["scope_expansion_by_inference"])
        self.assertEqual(DOCUMENT.read_text(encoding="utf-8").count(f"> {words}"), 1)

    def test_exact_green_request_and_proof_are_bound(self) -> None:
        green = self.decision["green_request_and_proof"]
        self.assertEqual(green["commit"], "5c466efd6086db0acce6a57a9f32172c67e157f6")
        self.assertEqual(green["CI_run_id"], 33_291_744_779)
        self.assertEqual(green["base_python_job_id"], 99_204_462_828)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_204_462_714)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])
        self.assertEqual(green["fresh_verification_calls"], 1)

    def test_bound_artifacts_match_hash_size_blob_and_green_commit(self) -> None:
        rows = self.decision["bound_artifacts"]
        summary = self.decision["bound_artifact_summary"]
        commit = self.decision["green_request_and_proof"]["commit"]
        commit_available = (
            subprocess.run(
                ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
                cwd=ROOT,
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )
        if not commit_available:
            shallow = subprocess.check_output(
                ["git", "rev-parse", "--is-shallow-repository"], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(shallow, "true")
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            git_blob_payload = f"blob {len(payload)}\0".encode() + payload
            self.assertEqual(
                hashlib.sha1(git_blob_payload, usedforsecurity=False).hexdigest(),
                row["git_blob"],
                row["path"],
            )
            if commit_available:
                committed = subprocess.check_output(
                    ["git", "show", f'{commit}:{row["path"]}'], cwd=ROOT
                )
                self.assertEqual(payload, committed, row["path"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(summary["count"], 6)
        self.assertEqual(summary["bytes"], 42_986)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_authority_is_ordered_and_metadata_only(self) -> None:
        authority = self.decision["authorization_after_decision_green"]
        self.assertTrue(authority["implement_additive_standard_library_discovery_system"])
        self.assertTrue(authority["run_generated_fixture_and_mock_network_qualification"])
        self.assertTrue(
            authority["implementation_commit_push_and_both_remote_CI_jobs_green_required"]
        )
        self.assertTrue(
            authority["execute_one_metadata_only_public_discovery_after_implementation_green"]
        )
        self.assertEqual(authority["maximum_registered_executions"], 1)
        self.assertEqual(authority["official_index_count_exact"], 5)
        self.assertEqual(authority["exact_text_query_count"], 4)
        self.assertEqual(authority["maximum_selected_candidates"], 1)
        self.assertFalse(authority["FULL_CONFIRMATION_SOURCE_emission_allowed"])
        for key in (
            "general_search_engine_provider_or_ad_hoc_candidate_allowed",
            "query_endpoint_method_or_allowlist_change_allowed",
            "source_specific_publication_or_payload_research",
            "payload_URL_archive_range_member_or_header_access",
            "signal_event_annotation_target_or_label_access",
            "acquisition_cache_split_or_derivative_creation",
            "model_checkpoint_training_inference_prediction_or_score",
            "language_model_or_provider",
            "stream_device_or_hardware",
            "touch_other_project",
            "cleanup_delete_overwrite_rename_or_move",
            "release_or_publish",
            "scientific_claim_upgrade",
            "retry_rerun_resume_repair_substitute_or_post_result_amend",
        ):
            self.assertFalse(authority[key], key)

    def test_caps_and_decision_only_zero_operations(self) -> None:
        caps = self.decision["network_and_resource_caps"]
        self.assertEqual(caps["maximum_network_requests"], 128)
        self.assertEqual(caps["maximum_wire_response_body_bytes_total"], 32 * 1024 * 1024)
        self.assertEqual(caps["maximum_decoded_response_body_bytes_total"], 32 * 1024 * 1024)
        self.assertEqual(caps["maximum_retained_public_artifact_bytes"], 8 * 1024 * 1024)
        self.assertEqual(caps["maximum_runtime_seconds"], 300)
        self.assertEqual(caps["maximum_peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual((caps["CPU_threads"], caps["workers"]), (1, 1))
        self.assertEqual((caps["retry_count"], caps["rerun_count"]), (0, 0))
        operations = self.decision["decision_only_operations"]
        self.assertEqual(operations["GitHub_CI_verification_calls"], 1)
        self.assertFalse(operations["end_to_end_latency_measured"])
        self.assertTrue(
            all(
                value == 0
                for key, value in operations.items()
                if key not in {"GitHub_CI_verification_calls", "end_to_end_latency_measured"}
            )
        )

    def test_barriers_and_claim_ceiling_remain_closed(self) -> None:
        barriers = self.decision["next_barriers"]
        self.assertTrue(
            barriers["this_decision_commit_push_and_both_remote_CI_jobs_green_before_implementation"]
        )
        self.assertTrue(
            barriers["exact_implementation_commit_push_and_both_remote_CI_jobs_green_before_execution"]
        )
        self.assertFalse(barriers["implementation_authority_before_decision_green"])
        self.assertFalse(barriers["network_authority_before_implementation_green"])
        self.assertFalse(barriers["payload_model_score_or_claim_authority"])
        self.assertTrue(all(value is False for value in self.decision["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
