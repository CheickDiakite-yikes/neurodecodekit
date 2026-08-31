from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "registries/fresh_motor_source_identity_witness_live_implementation.v0.json"
)
RESULT = (
    ROOT
    / "registries/fresh_motor_source_identity_witness_live_qualification_result.v0.json"
)

EXPECTED_ARTIFACTS = {
    "docs/FRESH_MOTOR_SOURCE_IDENTITY_WITNESS_LIVE_IMPLEMENTATION.md",
    "registries/current_research_frontier.v25.json",
    "registries/fresh_motor_source_identity_witness_live_implementation_decision.v0.json",
    "registries/fresh_motor_source_identity_witness_live_qualification_result.v0.json",
    "src/neurodecodekit/__init__.py",
    "src/neurodecodekit/datasets/__init__.py",
    "src/neurodecodekit/datasets/fresh_motor_source_identity_witness.py",
    "src/neurodecodekit/datasets/fresh_motor_source_identity_witness_live.py",
    "src/neurodecodekit/datasets/fresh_motor_source_identity_witness_live_qualification.py",
    "src/neurodecodekit/fmsr1_witness_live_cli.py",
    "tests/test_current_research_frontier_v25.py",
    "tests/test_fmsr1_witness_live_cli.py",
    "tests/test_fresh_motor_source_identity_witness_live.py",
    "tests/test_fresh_motor_source_identity_witness_live_implementation_record.py",
    "tests/test_fresh_motor_source_identity_witness_live_qualification.py",
}


def git_blob(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324 - Git identity


class FreshMotorSourceIdentityWitnessLiveImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_identity_and_decision_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.fresh_motor_source_identity_witness_live_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["packet_id"], "FMSR1-R1-W-v0")
        self.assertEqual(self.record["implementation_id"], "FMSR1-R1-W-I1")
        self.assertEqual(self.record["qualification_id"], "FMSR1-R1-W-I1-Q0")
        decision = self.record["green_live_implementation_decision"]
        self.assertEqual(
            decision["commit"], "0c50299dc5223ba0f2b1f337beded51038bffd4d"
        )
        self.assertEqual(decision["CI_run_id"], 33364407489)
        self.assertTrue(decision["both_required_jobs_green"])

    def test_artifact_set_matches_exact_local_bytes(self) -> None:
        rows = self.record["implementation_artifacts"]
        self.assertEqual({row["path"] for row in rows}, EXPECTED_ARTIFACTS)
        self.assertEqual(self.record["implementation_artifact_summary"]["count"], len(rows))
        self.assertEqual(
            self.record["implementation_artifact_summary"]["bytes"],
            sum(row["bytes"] for row in rows),
        )
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
            self.assertEqual(git_blob(payload), row["git_blob"], row["path"])

    def test_result_is_exact_and_zero_network(self) -> None:
        identity = self.record["generated_qualification"]["result_artifact"]
        payload = RESULT.read_bytes()
        self.assertEqual(identity["path"], RESULT.relative_to(ROOT).as_posix())
        self.assertEqual(identity["bytes"], len(payload))
        self.assertEqual(identity["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(identity["git_blob"], git_blob(payload))
        self.assertEqual(self.result["route"], "GENERATED_LIVE_ADAPTER_QUALIFIED")
        self.assertEqual(self.result["candidate_semantic_accesses"], 0)
        self.assertEqual(self.result["operation_counters"]["network_requests"], 0)
        self.assertEqual(self.result["operation_counters"]["payload_or_neural_reads"], 0)
        self.assertTrue(all(value is False for value in self.result["claim_boundary"].values()))

    def test_caps_and_authority_remain_closed(self) -> None:
        qualification = self.record["generated_qualification"]
        self.assertTrue(qualification["consumed"])
        self.assertFalse(qualification["rerun_allowed"])
        self.assertTrue(all(self.record["qualification_caps"].values()))
        authority = self.record["authority_now"]
        self.assertFalse(authority["repeat_generated_qualification"])
        self.assertFalse(authority["GitHub_API_or_official_index_network"])
        self.assertFalse(authority["candidate_parsing_ranking_or_selection"])
        self.assertFalse(authority["model_training_inference_prediction_or_score"])
        self.assertTrue(all(value is False for value in self.record["claim_boundary"].values()))

    def test_record_is_valid_json_under_base_python(self) -> None:
        completed = subprocess.run(
            ["python", "-m", "json.tool", str(RECORD)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
