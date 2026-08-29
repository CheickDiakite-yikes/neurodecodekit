import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_live_recovery_qualification_result.v0.json"
)
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_live_recovery_qualification_implementation.v0.json"
)
DOCUMENT_PATH = (
    ROOT / "docs/DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_QUALIFICATION_CLOSEOUT.md"
)


def _git_blob(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class DreyerRecoveryQualificationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_coordinator_is_bound(self):
        green = self.result["green_coordinator"]
        self.assertEqual(
            green["commit"], "0ef634e4852d9f8a18d4b8a1f50e6a1331bd020a"
        )
        self.assertEqual(green["CI_run_id"], 33_253_657_120)
        self.assertEqual(green["base_python_job_id"], 99_103_540_731)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_103_540_620)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_implementation_registry_identity_is_exact(self):
        binding = self.result["green_coordinator"]["implementation_registry"]
        payload = IMPLEMENTATION_PATH.read_bytes()
        self.assertEqual(len(payload), binding["bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])
        self.assertEqual(_git_blob(payload), binding["git_blob"])

    def test_one_shot_result_passed_and_is_consumed(self):
        self.assertEqual(
            self.result["status"],
            "passed_generated_only_consumed_closeout_pending_remote_green",
        )
        consumption = self.result["consumption"]
        self.assertEqual(consumption["registered_attempts_authorized"], 1)
        self.assertEqual(consumption["registered_attempts_consumed"], 1)
        self.assertFalse(
            consumption[
                "rerun_retry_resume_repair_substitution_or_amendment_allowed"
            ]
        )

    def test_matrix_and_resources_are_exact_and_bounded(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["total_cases"], 65)
        self.assertEqual(matrix["valid_H1_replays"], 2)
        self.assertEqual(matrix["inherited_stage_H_valid_cases"], 2)
        self.assertEqual(matrix["inherited_stage_H_refusals"], 18)
        self.assertEqual(matrix["ordered_successor_refusals"], 43)
        for key in (
            "valid_H1_byte_deterministic",
            "marker_before_capability",
            "exactly_one_opener_and_request_on_H1",
            "response_closure",
            "manifest_contained_cleanup",
            "no_staging_or_unaccepted_payload_debris",
            "aggregate_H0_behavior",
            "no_replace_publication",
            "consumed_rerun_refusal",
        ):
            self.assertTrue(matrix[key], key)
        measured = self.result["measurements"]
        self.assertLessEqual(
            measured["runtime_seconds"], measured["runtime_seconds_maximum"]
        )
        self.assertLessEqual(
            measured["peak_process_tree_RSS_bytes"],
            measured["peak_process_tree_RSS_bytes_maximum"],
        )
        self.assertLessEqual(
            measured["generated_input_plus_output_bytes"],
            measured["generated_input_plus_output_bytes_maximum"],
        )
        self.assertLessEqual(
            measured["incremental_temporary_allocated_bytes"],
            measured["incremental_temporary_disk_bytes_maximum"],
        )

    def test_every_forbidden_operation_and_claim_remains_zero(self):
        counters = self.result["operation_counters"]
        self.assertEqual(counters["registered_qualification_attempts"], 1)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key != "registered_qualification_attempts"
            )
        )
        claims = self.result["claim_boundary"]
        for key, value in claims.items():
            if key != "engineering_capability":
                self.assertFalse(value, key)

    def test_ignored_evidence_is_hash_only_and_not_committed(self):
        evidence = self.result["ignored_local_evidence"]
        self.assertEqual([item["kind"] for item in evidence], ["consumed_marker", "aggregate_result"])
        self.assertEqual([item["bytes"] for item in evidence], [251, 9046])
        self.assertTrue(all(not item["committed"] for item in evidence))
        self.assertTrue(all(len(item["sha256"]) == 64 for item in evidence))

    def test_document_and_router_preserve_the_scientific_boundary(self):
        text = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertFalse(self.result["routing"]["HL2_activation_allowed"])
        self.assertFalse(self.result["routing"]["HL2_real_invocation_consumed"])


if __name__ == "__main__":
    unittest.main()
