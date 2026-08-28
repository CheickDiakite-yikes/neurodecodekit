from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_QUALIFICATION_HARDENING_PROOF_CLOSEOUT.md"
)
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_qualification_hardening_proof_closeout.v0.json"
)


class CommunicationEEGProspectiveGeneratedQualificationHardeningProofTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_implementation_is_bound(self) -> None:
        green = self.record["green_implementation"]
        self.assertEqual(green["commit"], "55e627d6504f32d51ea4d6e93e04901f7233411c")
        self.assertEqual(green["CI_run_id"], 33153174019)
        self.assertEqual(green["base_python_job_id"], 98789718192)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98789718367)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_bound_artifacts_are_exact(self) -> None:
        total = 0
        for artifact in self.record["bound_artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            total += len(payload)
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
        self.assertEqual(total, self.record["bound_artifact_bytes"])

    def test_rehearsal_measurement_is_bounded_and_nonofficial(self) -> None:
        measured = self.record["rehearsal_measurement"]
        self.assertFalse(measured["official_qualification"])
        self.assertEqual(measured["fictional_participants"], 42)
        self.assertEqual(measured["prediction_rows"], 91392)
        self.assertEqual(measured["prediction_sets"], 1428)
        self.assertEqual(measured["maximum_prediction_rows_buffered"], 1)
        self.assertFalse(measured["complete_prediction_records_materialized"])
        self.assertEqual(measured["numerical_shortcut_fixture_executions"], 7)
        self.assertEqual(measured["network_bytes"], 0)
        self.assertEqual(measured["real_or_private_reads"], 0)
        self.assertEqual(measured["retained_generated_payload_bytes"], 0)

    def test_closeout_performs_no_operation_and_keeps_claims_closed(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        official = self.record["official_qualification"]
        self.assertFalse(official["activated"])
        self.assertFalse(official["executed"])
        self.assertFalse(official["consumed"])
        claims = self.record["claim_boundary"]
        self.assertTrue(claims["generated_engineering_hardening_established"])
        for key, value in claims.items():
            if key != "generated_engineering_hardening_established":
                self.assertFalse(value, key)

    def test_document_separates_engineering_from_science(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("official qualification remains inactive", document)


if __name__ == "__main__":
    unittest.main()
