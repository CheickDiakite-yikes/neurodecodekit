import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "registries" / "loop44_claim_release_matrix.v0.json"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"


class Loop44ClaimReleaseMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))

    def test_schema_identity_and_closed_review_status(self):
        self.assertEqual(
            self.matrix["schema_name"],
            "neurodecodekit.loop44_claim_release_matrix",
        )
        self.assertEqual(self.matrix["schema_version"], "0.1.0")
        self.assertEqual(self.matrix["loop_id"], 44)
        self.assertEqual(
            self.matrix["status"],
            "artifact_only_claim_review_complete_release_held",
        )

    def test_review_does_not_authorize_release_or_experiment(self):
        authorization = dict(self.matrix["authorization"])
        self.assertTrue(authorization.pop("artifact_only_review_authorized"))
        self.assertTrue(all(value is False for value in authorization.values()))
        self.assertEqual(len(authorization), 19)

    def test_evidence_ladder_is_contiguous_and_replication_is_highest(self):
        levels = self.matrix["evidence_levels"]
        self.assertEqual(len(levels), 7)
        self.assertEqual(
            [row["level_id"].split("_", 1)[0] for row in levels],
            [f"E{index}" for index in range(7)],
        )
        self.assertIn("independent scientific", levels[-1]["meaning"])

    def test_claim_inventory_preserves_real_negative_results(self):
        claims = {row["claim_id"]: row for row in self.matrix["claim_cards"]}
        self.assertEqual(len(claims), 16)
        session1 = claims["L44-C05_s21_session1_predictive_result"]
        session2 = claims["L44-C06_s21_cross_session_result"]
        eeg = claims["L44-C07_s7_eeg_result"]
        self.assertEqual(session1["status"], "retained_negative_scientific")
        self.assertAlmostEqual(session1["metrics"]["tiny_minus_prior_cer"], -0.005814)
        self.assertAlmostEqual(session2["metrics"]["tiny_minus_prior_cer"], 0.142491)
        self.assertAlmostEqual(eeg["metrics"]["model_minus_prior_accuracy"], -0.113636)
        self.assertTrue(
            all(
                row["evidence_level"] == "E4_real_data_predictive_result"
                for row in (session1, session2, eeg)
            )
        )

    def test_supported_claims_have_complete_evidence_bindings(self):
        required = {
            "cohort",
            "task",
            "split",
            "comparator",
            "uncertainty",
            "resource_record",
            "access_record",
            "privacy",
            "license",
            "evidence_paths",
        }
        supported_statuses = {
            "promoted_engineering",
            "retained_negative_scientific",
            "fixture_backed_only",
            "parked_measured",
        }
        supported = [
            row for row in self.matrix["claim_cards"] if row["status"] in supported_statuses
        ]
        self.assertEqual(len(supported), 10)
        for claim in supported:
            self.assertTrue(required.issubset(claim), claim["claim_id"])
            self.assertTrue(claim["evidence_paths"], claim["claim_id"])
            for relative_path in claim["evidence_paths"]:
                self.assertTrue((REPO_ROOT / relative_path).exists(), relative_path)

    def test_unavailable_and_prohibited_claims_are_not_smuggled_as_results(self):
        blocked = self.matrix["claim_cards"][10:]
        self.assertEqual(len(blocked), 6)
        self.assertTrue(
            all(
                row["status"] in {"unavailable", "prohibited_overclaim"}
                for row in blocked
            )
        )
        self.assertTrue(all(row["evidence_level"] == "E0_unavailable" for row in blocked))
        self.assertTrue(all(row["blocking_evidence"] for row in blocked))

    def test_models_and_datasets_have_no_released_payload(self):
        self.assertEqual(len(self.matrix["model_cards"]), 5)
        self.assertTrue(
            all(not row["release_payload_exists"] for row in self.matrix["model_cards"])
        )
        self.assertEqual(len(self.matrix["dataset_cards"]), 4)
        self.assertTrue(
            all(not row["release_allowed_here"] for row in self.matrix["dataset_cards"])
        )

    def test_release_checklist_fails_closed(self):
        gates = self.matrix["release_checklist"]
        self.assertEqual(len(gates), 14)
        self.assertEqual(
            [row["gate_id"].split("_", 1)[0] for row in gates],
            [f"L44-G{index:02d}" for index in range(1, 15)],
        )
        statuses = {row["status"] for row in gates}
        self.assertEqual(statuses, {"pass", "fail", "unavailable", "pending_verification"})
        self.assertEqual(sum(row["status"] == "pass" for row in gates), 3)
        self.assertGreaterEqual(sum(row["status"] == "fail" for row in gates), 8)

    def test_decision_separates_engineering_and_scientific_release(self):
        decision = self.matrix["decision"]
        self.assertEqual(decision["loop44_planning_and_artifact_review"], "proceed_complete")
        self.assertEqual(decision["engineering_source_release"], "hold")
        self.assertEqual(decision["scientific_performance_release"], "park")
        self.assertEqual(decision["clinical_or_arbitrary_thought_claim"], "prohibit")
        for key, value in decision.items():
            if key.endswith("_established"):
                self.assertFalse(value, key)

    def test_current_operations_are_zero_except_disclosed_sidecar_read(self):
        operations = self.matrix["current_operations"]
        exceptions = {
            "user_owned_tracker_sidecar_text_reads",
            "user_owned_tracker_sidecar_overwrite_incidents",
            "user_owned_tracker_sidecar_restored_byte_exact",
            "user_owned_tracker_sidecar_final_sha256",
            "user_owned_tracker_sidecar_modified_at_closeout",
            "user_owned_tracker_sidecar_staged",
        }
        for key, value in operations.items():
            if key not in exceptions:
                self.assertEqual(value, 0, key)
        self.assertEqual(operations["user_owned_tracker_sidecar_text_reads"], 1)
        self.assertEqual(operations["user_owned_tracker_sidecar_overwrite_incidents"], 1)
        self.assertTrue(operations["user_owned_tracker_sidecar_restored_byte_exact"])
        self.assertEqual(
            operations["user_owned_tracker_sidecar_final_sha256"],
            "b96bbea77ec93e59c0db7c4bcaeb4a9182f1f7cc7039d13fb223b65e0005beb6",
        )
        self.assertFalse(operations["user_owned_tracker_sidecar_modified_at_closeout"])
        self.assertFalse(operations["user_owned_tracker_sidecar_staged"])

    def test_sources_risks_and_warnings_are_complete(self):
        self.assertEqual(len(self.matrix["source_bindings"]), 8)
        self.assertEqual(len(self.matrix["risk_register"]), 8)
        self.assertEqual(len(self.matrix["warnings"]), 5)
        source_ids = {row["source_id"] for row in self.matrix["source_bindings"]}
        self.assertEqual(
            source_ids,
            {
                "model_cards",
                "datasheets",
                "nist_ai_rmf",
                "cobidas_meeg",
                "acm_artifact_badging",
                "fair4rs",
                "github_citation",
                "zenodo_versioning",
            },
        )

    def test_roadmap_loop44_is_closed_without_execution_authorization(self):
        loop44 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 44)
        self.assertEqual(loop44["status"], "Planning Research Complete")
        self.assertFalse(loop44["execution_authorized"])
        self.assertEqual(loop44["proof_posture"], "artifact_only_claim_review_release_held")
        self.assertEqual(loop44["claim_card_count"], 16)
        self.assertEqual(loop44["release_gate_count"], 14)
        self.assertEqual(loop44["risk_count"], 8)

    def test_public_docs_use_the_loop44_boundary(self):
        required_paths = [
            "README.md",
            "START_HERE.md",
            "AGENTS.md",
            "docs/CODEX_HANDOFF.md",
            "docs/NEXT_20_LOOPS_TRACKER.md",
            "docs/OPEN_SOURCE_READINESS.md",
        ]
        for relative_path in required_paths:
            text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("Loop 44", text, relative_path)
            self.assertIn("release", text.lower(), relative_path)


if __name__ == "__main__":
    unittest.main()
