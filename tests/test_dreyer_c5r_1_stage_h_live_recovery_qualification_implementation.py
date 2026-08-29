import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / (
    "dreyer_c5r_1_stage_h_live_recovery_qualification_implementation.v0.json"
)
DOCUMENT = ROOT / "docs" / (
    "DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_QUALIFICATION_IMPLEMENTATION.md"
)


def _record() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


class DreyerRecoveryQualificationImplementationTests(unittest.TestCase):
    def test_coordinator_binds_exact_green_decision(self) -> None:
        green = _record()["green_qualification_decision"]

        self.assertEqual(
            green["commit"], "749fd5695441350d8cc949af19b6ad4bb5863dba"
        )
        self.assertEqual(green["CI_run_id"], 33_251_731_156)
        self.assertEqual(green["base_python_job_id"], 99_098_454_755)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_098_454_800)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_exact_implementation_artifacts_match(self) -> None:
        record = _record()
        rows = record["tracked_implementation_artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(
            record["tracked_implementation_artifact_summary"],
            {
                "count": 3,
                "bytes": sum(row["bytes"] for row in rows),
                "canonical_artifact_set_sha256": hashlib.sha256(canonical).hexdigest(),
            },
        )

    def test_matrix_and_resource_measurements_are_bounded(self) -> None:
        record = _record()
        contract = record["qualification_contract"]
        measured = record["development_qualification"]
        caps = record["resource_envelope"]

        self.assertEqual(contract["total_cases"], 65)
        self.assertEqual(contract["valid_H1_replays"], 2)
        self.assertEqual(contract["inherited_stage_H_valid_cases"], 2)
        self.assertEqual(contract["inherited_stage_H_refusals"], 18)
        self.assertEqual(contract["ordered_successor_refusals"], 43)
        self.assertEqual(measured["full_matrix_cases_passed"], 65)
        self.assertEqual(measured["registered_qualification_attempts"], 0)
        self.assertLess(measured["runtime_seconds"], caps["runtime_seconds_maximum"])
        self.assertLess(
            measured["peak_process_RSS_bytes"],
            caps["peak_process_tree_RSS_bytes_maximum"],
        )
        self.assertLess(
            measured["generated_fixture_plus_temporary_logical_bytes"],
            caps["generated_input_plus_output_bytes_maximum"],
        )
        self.assertLess(
            measured["temporary_allocated_bytes"],
            caps["incremental_temporary_disk_bytes_maximum"],
        )

    def test_authority_and_claim_boundaries_are_closed_until_green(self) -> None:
        record = _record()
        barriers = record["next_barriers"]

        self.assertTrue(
            barriers["exact_coordinator_commit_push_and_both_jobs_green_required"]
        )
        self.assertEqual(
            barriers["registered_qualification_attempts_authorized_after_green"], 1
        )
        self.assertEqual(barriers["registered_qualification_attempts_consumed_now"], 0)
        self.assertFalse(
            barriers["rerun_retry_resume_repair_substitution_or_amendment_allowed"]
        )
        self.assertFalse(barriers["HL2_authority"])
        self.assertFalse(barriers["real_EDF_authority"])
        self.assertTrue(
            all(value == 0 for value in record["implementation_access_counters"].values())
        )
        self.assertTrue(all(value is False for value in record["claim_boundary"].values()))
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
