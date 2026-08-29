from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/ofner_2017_motor_imagery_range_header_request_proof.v0.json"
)
DOCUMENT = (
    ROOT / "docs/OFNER_2017_MOTOR_IMAGERY_RANGE_HEADER_REQUEST_PROOF_CLOSEOUT.md"
)


class OfnerRangeHeaderRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_green_request_is_bound(self) -> None:
        anchor = self.proof["green_request_commit"]
        self.assertEqual(
            anchor["commit"], "af9d0247bb816c3432a9eb407fadcd286f84d87c"
        )
        self.assertEqual(anchor["CI_run_id"], 33_273_113_793)
        self.assertEqual(anchor["base_python_job_id"], 99_155_058_261)
        self.assertEqual(anchor["optional_neuro_readers_job_id"], 99_155_058_168)
        self.assertTrue(anchor["both_required_jobs_green"])
        self.assertTrue(anchor["commit_on_GitHub_main"])

    def test_bound_request_artifacts_are_exact(self) -> None:
        rows = self.proof["bound_request_artifacts"]
        summary = self.proof["bound_request_artifact_summary"]
        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["bytes"], 25_008)
        self.assertEqual(sum(row["bytes"] for row in rows), 25_008)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_does_not_expand_scope(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["request_artifacts_unchanged"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["claim_boundary_changed"])
        transition = self.proof["transition"]
        self.assertFalse(transition["effective_before_this_closeout_commit_remote_green"])
        self.assertFalse(transition["implementation_authorized_by_closeout"])
        self.assertFalse(transition["network_or_real_operation_authorized_by_closeout"])
        self.assertTrue(transition["fresh_packet_bound_maintainer_words_required"])

    def test_no_protected_or_scientific_operation_occurred(self) -> None:
        counters = self.proof["operation_counters"]
        exempt = {"tracked_artifact_reads": 4, "Git_proof_reads": 4}
        for key, value in counters.items():
            self.assertEqual(value, exempt.get(key, 0), key)
        claims = self.proof["claim_boundary"]
        for key, value in claims.items():
            if key != "engineering_proof_added":
                self.assertFalse(value, key)

    def test_human_closeout_states_both_boundaries(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("every\noperation authority still false", document)


if __name__ == "__main__":
    unittest.main()
