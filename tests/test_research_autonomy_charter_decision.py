import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHARTER_PATH = REPO_ROOT / "docs" / "RESEARCH_AUTONOMY_CHARTER_DRAFT.md"
DECISION_DOC_PATH = REPO_ROOT / "docs" / "RESEARCH_AUTONOMY_CHARTER_DECISION.md"
DECISION_PATH = REPO_ROOT / "registries" / "research_autonomy_charter_decision.v0.json"
PUBLIC_PATHS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class ResearchAutonomyCharterDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.charter = CHARTER_PATH.read_text(encoding="utf-8")
        cls.doc = DECISION_DOC_PATH.read_text(encoding="utf-8")
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_decision_identity_and_effective_green_gate(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.research_autonomy_charter_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["status"],
            "tier_a_tier_b_authorized_effective_after_remote_green",
        )
        self.assertEqual(
            decision["authorization_parent_commit"],
            "d49f026fc3eee5f78bca9cf0640cbe73fe8684d8",
        )
        self.assertTrue(
            decision["effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"]
        )

    def test_approved_charter_snapshot_remains_byte_identical(self):
        snapshot = self.decision["charter_snapshot"]
        self.assertEqual(snapshot["sha256"], sha256(CHARTER_PATH))
        self.assertEqual(snapshot["git_blob_sha1"], git_blob_sha1(CHARTER_PATH))
        self.assertEqual(snapshot["commit"][:7], "df9035a")
        self.assertTrue(snapshot["remains_byte_identical_historical_proposal"])
        self.assertIn("Draft for maintainer approval", self.charter)
        self.assertTrue(snapshot["separate_decision_is_activation_record"])

    def test_exact_user_sentence_matches_charter_and_decision_doc(self):
        user = self.decision["user_authorization"]
        sentence = user["exact_sentence_verbatim"]
        self.assertIn(sentence, " ".join(self.charter.replace(">", "").split()))
        self.assertEqual(self.doc.count(sentence), 1)
        self.assertTrue(user["matches_charter_standing_approval_sentence"])
        self.assertTrue(user["prospective_only"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_only_tier_a_b_and_git_ci_autonomy_are_standing_authorizations(self):
        flags = dict(authorization_flags(self.decision["authorization"]))
        expected_true = {
            "tier_a_routine_work_authorized_now",
            "tier_b_bounded_development_experiments_authorized_now",
            "autonomous_commits_pushes_and_ci_checks_authorized_now",
        }
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 15)

    def test_tier_b_never_consumes_a_scientific_test(self):
        tier_b = self.decision["tier_b_requirements"]
        self.assertEqual(
            tier_b[
                "held_out_final_source_test_cross_person_final_or_consumed_validation_target_reads"
            ],
            0,
        )
        self.assertTrue(tier_b["future_scientific_test_may_not_be_consumed"])
        self.assertTrue(tier_b["failed_results_must_be_retained_without_silent_rerun"])

    def test_default_resource_envelope_is_exact(self):
        resources = self.decision["default_operating_envelope"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["concurrent_numerical_jobs"], 1)
        self.assertEqual(resources["ordinary_peak_rss_bytes"], 1024**3)
        self.assertEqual(resources["generated_artifacts_per_loop_bytes"], 32 * 1024**2)
        self.assertEqual(resources["minimum_free_disk_bytes"], 20 * 1024**3)
        self.assertEqual(resources["new_real_data_download_bytes"], 0)
        self.assertFalse(resources["loop_specific_contract_may_silently_loosen_envelope"])

    def test_loop48_rw3_and_s25_remain_independently_gated(self):
        boundary = self.decision["nonretroactive_boundary"]
        self.assertFalse(boundary["consumed_loop_may_reopen"])
        self.assertFalse(boundary["existing_narrower_contract_may_be_loosened"])
        self.assertTrue(boundary["loop48_stage_b_requires_separate_exact_decision"])
        self.assertTrue(boundary["rw3_requires_separate_exact_decision"])
        self.assertTrue(boundary["s25_requires_separate_exact_decision"])
        self.assertTrue(
            boundary["same_session_loop48_stage_b_sentence_must_be_recorded_independently"]
        )

    def test_authorization_only_measurements_are_zero(self):
        for key, value in self.decision["authorization_only_measurements"].items():
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_public_status_points_to_active_decision_and_tier_c_stop(self):
        for path in PUBLIC_PATHS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn("RESEARCH_AUTONOMY_CHARTER_DECISION.md", content)
                self.assertIn("Tier C", content)
                self.assertNotIn("The draft is not active yet", content)


if __name__ == "__main__":
    unittest.main()
