from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = (
    ROOT
    / "registries/fresh_motor_source_admission_generated_implementation.v0.json"
)
REGISTRY = (
    ROOT
    / "registries/fresh_motor_source_admission_generated_implementation.v1.json"
)
FRONTIER = ROOT / "registries/current_research_frontier.v18.json"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class FreshMotorSourceAdmissionGeneratedImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_implementation_identity_and_green_registration_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.fresh_motor_source_admission_generated_implementation",
        )
        self.assertEqual(self.record["protocol_id"], "FMSR1-R1-G-v0")
        self.assertEqual(self.record["implementation_id"], "FMSR1-R1-G-I1")
        self.assertEqual(
            self.record["green_registration"]["commit"],
            "d53f3e8870b1f3ae6f014411c9932f20474b8092",
        )
        self.assertTrue(
            self.record["green_registration"]["both_required_jobs_green"]
        )

    def test_bound_artifacts_match_exact_local_bytes(self) -> None:
        rows = self.record["bound_artifacts"]
        self.assertEqual(len(rows), 7)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(_sha256(payload), row["sha256"], row["path"])
        canonical = (
            json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("ascii")
        summary = self.record["bound_artifact_summary"]
        self.assertEqual(sum(row["bytes"] for row in rows), summary["bytes"])
        self.assertEqual(len(canonical), summary["canonical_manifest_bytes"])
        self.assertEqual(_sha256(canonical), summary["canonical_manifest_sha256"])

    def test_rejected_green_predecessor_is_preserved_exactly(self) -> None:
        binding = self.record["supersedes"]
        payload = PREDECESSOR.read_bytes()
        self.assertEqual(binding["implementation_id"], "FMSR1-R1-G-I0")
        self.assertEqual(binding["registry_bytes"], len(payload))
        self.assertEqual(binding["registry_sha256"], _sha256(payload))
        self.assertEqual(
            binding["commit"], "c3f536d3e527117d9347ed0d6c4fdbc39d7d44ac"
        )
        self.assertTrue(binding["both_required_jobs_green"])
        self.assertEqual(binding["post_green_review_disposition"], "REJECT_before_activation")
        self.assertEqual(self.predecessor["implementation_id"], "FMSR1-R1-G-I0")

    def test_official_qualification_is_explicitly_not_run(self) -> None:
        qualification = self.record["official_qualification"]
        self.assertFalse(qualification["activation_record_present"])
        self.assertFalse(qualification["implementation_exact_green"])
        self.assertEqual(qualification["official_runs"], 0)
        self.assertFalse(qualification["durable_consumed_marker_created"])
        self.assertFalse(qualification["report_emitted"])

    def test_frontier_preserves_scientific_and_live_boundaries(self) -> None:
        self.assertEqual(
            self.frontier["supersedes"],
            "registries/current_research_frontier.v17.json",
        )
        implementation = self.frontier["R1_G_corrected_generated_only_implementation"]
        self.assertEqual(implementation["focused_test_count"], 37)
        self.assertEqual(implementation["component_refusals_passed"], 82)
        self.assertEqual(
            implementation["pending_reservation_event"],
            "official_attempt_directory_created",
        )
        self.assertEqual(
            implementation["arming_event"],
            "work_root_fsync_succeeded_after_official_attempt_reservation_created",
        )
        self.assertFalse(
            implementation[
                "pending_reservation_is_crash_durable_before_work_root_fsync"
            ]
        )
        self.assertEqual(
            self.frontier["independent_review"]["I1_re_review_disposition"],
            "ACCEPT_for_prior_durability_and_consumption_blockers_fresh_remote_CI_still_required",
        )
        self.assertEqual(
            self.frontier["independent_review"]["I1_second_review_disposition"],
            "REJECT_pending_reservation_boundary_and_capacity_matched_comparator_blockers",
        )
        self.assertEqual(
            self.frontier["independent_review"]["I1_final_re_review_disposition"],
            "ACCEPT_no_P0_or_P1_implementation_commit_and_fresh_CI_only",
        )
        self.assertTrue(
            self.frontier["rejected_green_R1_G_implementation_predecessor"][
                "both_required_main_jobs_green"
            ]
        )
        self.assertIsNone(self.frontier["active_Tier_C_packet"])
        self.assertFalse(self.frontier["claim_boundary"]["real_EEG_accessed"])
        self.assertFalse(
            self.frontier["claim_boundary"]["neural_advantage_established"]
        )
        self.assertFalse(
            self.frontier["claim_boundary"]["causal_live_decoding_established"]
        )


if __name__ == "__main__":
    unittest.main()
