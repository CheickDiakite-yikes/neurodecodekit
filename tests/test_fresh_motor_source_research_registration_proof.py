from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries/fresh_motor_source_research_registration_proof.v0.json"
DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_RESEARCH_REGISTRATION_PROOF_CLOSEOUT.md"
EXPECTED_PATHS = {
    "docs/FRESH_MOTOR_SOURCE_RESEARCH_PREREGISTRATION_AMENDMENT_1.md",
    "registries/current_research_frontier.v10.json",
    "registries/fresh_motor_source_research_contract.v1.json",
    "tests/test_current_research_frontier_v10.py",
    "tests/test_fresh_motor_source_research_v1.py",
}


class FreshMotorSourceResearchRegistrationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_registration_commit_is_remotely_green(self) -> None:
        green = self.proof["green_registration_commit"]
        self.assertEqual(green["commit"], "e09f6cc014744485940713c148dacad9dbbe59e3")
        self.assertEqual(green["CI_run_id"], 33_289_147_031)
        self.assertEqual(green["base_python_job_id"], 99_197_577_034)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_197_577_007)
        self.assertTrue(green["both_required_jobs_green"])

    def assert_exact_commit_artifact_binding(self, proof: dict) -> None:
        rows = proof["bound_artifacts"]
        summary = proof["bound_artifact_summary"]
        commit = proof["green_registration_commit"]["commit"]
        self.assertEqual(len(rows), summary["count"])
        self.assertEqual({row["path"] for row in rows}, EXPECTED_PATHS)
        self.assertEqual(sum(row["bytes"] for row in rows), summary["bytes"])
        canonical_lines = []
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            commit_payload = subprocess.check_output(
                ["git", "show", f'{commit}:{row["path"]}'], cwd=ROOT
            )
            self.assertEqual(payload, commit_payload, row["path"])
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(len(commit_payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(commit_payload).hexdigest(), row["sha256"], row["path"]
            )
            blob = subprocess.check_output(
                ["git", "rev-parse", f'{commit}:{row["path"]}'], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"], row["path"])
            canonical_lines.append(
                f'{row["path"]}|{row["bytes"]}|{row["sha256"]}|{row["git_blob"]}\n'
            )
        canonical = "".join(sorted(canonical_lines)).encode()
        self.assertEqual(summary["count"], 5)
        self.assertEqual(summary["bytes"], 47_128)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_five_artifacts_are_hash_size_and_git_bound(self) -> None:
        self.assert_exact_commit_artifact_binding(self.proof)

    def test_sha_size_and_blob_substitutions_fail(self) -> None:
        cases = (
            ("sha256", "0" * 64),
            ("bytes", self.proof["bound_artifacts"][0]["bytes"] + 1),
            ("git_blob", "0" * 40),
        )
        for field, value in cases:
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.proof)
                mutated["bound_artifacts"][0][field] = value
                with self.assertRaises(AssertionError):
                    self.assert_exact_commit_artifact_binding(mutated)

    def test_closeout_performs_only_proof_reads(self) -> None:
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 5)
        self.assertEqual(counters["Git_proof_reads"], 5)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )
        self.assertIsNone(self.proof["transition"]["active_Tier_C_packet_after_closeout"])

    def test_capability_and_nonclaim_are_separate(self) -> None:
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability pending remote proof:", text)
        self.assertIn("Scientific claim not established:", text)
        boundary = self.proof["claim_boundary"]
        for key, value in boundary.items():
            if key != "engineering_proof_added":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
