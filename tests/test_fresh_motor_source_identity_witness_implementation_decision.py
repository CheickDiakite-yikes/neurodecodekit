from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT
    / "registries/fresh_motor_source_identity_witness_implementation_decision.v0.json"
)
HUMAN = ROOT / "docs/FRESH_MOTOR_SOURCE_IDENTITY_WITNESS_IMPLEMENTATION_DECISION.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


class FreshMotorSourceIdentityWitnessImplementationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_actual_maintainer_words_are_exact(self) -> None:
        words = "need real results, real scientific results, focus on that and only that and keep going"
        self.assertEqual(self.decision["maintainer_words"], words)
        self.assertEqual(self.decision["maintainer_words_utf8_bytes"], len(words.encode()))
        self.assertEqual(
            self.decision["maintainer_words_sha256"],
            hashlib.sha256(words.encode()).hexdigest(),
        )
        self.assertIn(f"> {words}", HUMAN.read_text(encoding="utf-8"))

    def test_green_packet_proof_is_exact(self) -> None:
        proof = self.decision["green_packet_proof"]
        self.assertEqual(proof["commit"], "d4ae388d883b8fb04fc75546e6a30aec2fbfa6f2")
        self.assertEqual(proof["CI_run_id"], 33357313608)
        self.assertEqual(proof["base_python_job_id"], 99381828165)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 99381828024)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertTrue(proof["on_GitHub_main"])
        self.assertEqual(proof["fresh_verification_calls"], 1)

    def test_every_bound_artifact_identity_is_exact(self) -> None:
        rows = self.decision["bound_artifacts"]
        self.assertEqual(len(rows), self.decision["bound_artifact_summary"]["count"])
        self.assertEqual(
            sum(row["bytes"] for row in rows),
            self.decision["bound_artifact_summary"]["bytes"],
        )
        for row in rows:
            path = ROOT / row["path"]
            self.assertEqual(row["bytes"], path.stat().st_size, row["path"])
            self.assertEqual(row["sha256"], _sha256(path), row["path"])
            self.assertEqual(row["git_blob"], _git_blob(path), row["path"])

    def test_first_decision_authorizes_generated_work_only(self) -> None:
        authority = self.decision["authorization_after_decision_green"]
        self.assertTrue(authority["additive_standard_library_witness_implementation"])
        self.assertTrue(authority["generated_fixture_only_qualification"])
        self.assertTrue(
            authority["implementation_commit_push_and_both_remote_CI_jobs_green_required"]
        )
        self.assertFalse(authority["generated_surface_may_expose_live_network_command"])
        forbidden = (
            "GitHub_API_or_official_index_network",
            "live_source_identity_witness",
            "candidate_parsing_ranking_or_selection",
            "publication_or_source_specific_metadata",
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
        )
        self.assertTrue(all(authority[name] is False for name in forbidden))

    def test_decision_performs_no_scientific_operation(self) -> None:
        counters = self.decision["decision_only_operations"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key.endswith("operations"))
        )
        self.assertEqual(counters["network_requests"], 0)
        self.assertEqual(counters["network_bytes"], 0)
        self.assertEqual(counters["candidate_or_source_selections"], 0)
        self.assertEqual(counters["payload_header_neural_target_or_label_reads"], 0)
        self.assertFalse(counters["end_to_end_latency_measured"])
        self.assertTrue(all(value is False for value in self.decision["claim_boundary"].values()))

    def test_second_fresh_decision_still_precedes_live_witness(self) -> None:
        barriers = self.decision["next_barriers"]
        self.assertTrue(barriers["fresh_second_execution_bound_maintainer_words_required"])
        self.assertTrue(barriers["separate_authority_bearing_execution_decision_required"])
        self.assertTrue(
            barriers["execution_decision_commit_and_both_remote_CI_jobs_green_before_live_witness"]
        )
        self.assertFalse(barriers["live_network_authority_before_all_barriers"])


if __name__ == "__main__":
    unittest.main()
