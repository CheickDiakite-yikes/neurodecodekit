import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc2_freewill_private_selection_failure_result.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2FreewillPrivateSelectionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_status_and_route_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_freewill_private_selection_failure_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-FW1A")
        self.assertEqual(
            self.result["status"],
            "consumed_failed_before_private_path_at_implementation_record_proof",
        )
        self.assertEqual(self.result["route"], "MARC2FWS-F00")

    def test_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]),
                    binding["sha256"],
                )

    def test_exact_implementation_was_remotely_green(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"],
            "d9a38530974ceab8e7f79b1f7a79b8fff57069e9",
        )
        self.assertEqual(proof["CI_run_id"], 31_765_857_313)
        self.assertEqual(proof["base_job_id"], 94_661_484_721)
        self.assertEqual(proof["optional_neuro_job_id"], 94_661_484_713)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_pre_invocation_snapshot_was_inside_caps_but_not_substituted(self):
        snapshot = self.result["pre_invocation_snapshot"]
        self.assertTrue(snapshot["tracked_worktree_clean"])
        self.assertTrue(snapshot["registered_output_root_absent"])
        self.assertGreaterEqual(snapshot["free_disk_bytes"], 15 * 1024**3)
        self.assertLessEqual(snapshot["one_minute_load_per_logical_CPU"], 1.0)
        self.assertEqual(snapshot["CPU_threads"], 1)
        self.assertTrue(snapshot["snapshot_is_not_in_executor_machine_gate"])

    def test_one_invocation_is_consumed_without_retry(self):
        invocation = self.result["registered_invocation"]
        self.assertEqual(invocation["execution_ordinal"], 1)
        self.assertEqual(invocation["execution_limit"], 1)
        self.assertTrue(invocation["attempted"])
        self.assertTrue(invocation["consumed"])
        self.assertEqual(invocation["CLI_exit_code"], 2)
        self.assertEqual(
            invocation["CLI_output"],
            "MARC2FWS-F00: implementation record differs",
        )
        self.assertFalse(invocation["retry_rerun_resume_repair_or_fallback_available"])

    def test_failure_preceded_machine_source_marker_and_outputs(self):
        invocation = self.result["registered_invocation"]
        for field in (
            "in_executor_machine_gate_reached",
            "registered_source_path_logic_reached",
            "consumed_marker_created",
            "private_selection_created",
            "aggregate_execution_report_created",
            "registered_output_root_exists_after_failure",
        ):
            self.assertFalse(invocation[field], field)
        self.assertIsNone(invocation["in_executor_runtime_seconds"])
        self.assertIsNone(invocation["peak_RSS_bytes"])

    def test_artifact_only_diagnosis_is_exact_and_private_free(self):
        diagnosis = self.result["artifact_only_diagnosis"]
        self.assertTrue(diagnosis["performed_after_invocation"])
        self.assertFalse(diagnosis["retained_private_path_or_content_access"])
        self.assertEqual(diagnosis["required_top_level_field"], "lane_id")
        self.assertEqual(diagnosis["required_value"], "MARC2-FW1A")
        self.assertIsNone(diagnosis["observed_value"])
        self.assertEqual(diagnosis["failure_condition"], "top_level_lane_id_absent")
        self.assertFalse(diagnosis["diagnosis_authorizes_repair_or_rerun"])

    def test_every_private_payload_neural_and_model_counter_is_zero(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["tracked_proof_validation_attempts"], 1)
        for key, value in counters.items():
            if key == "tracked_proof_validation_attempts":
                continue
            self.assertEqual(value, 0, key)

    def test_all_closeout_acceptance_gates_pass(self):
        gates = self.result["acceptance_gates"]
        self.assertEqual(len(gates), 9)
        self.assertTrue(all(gates.values()))
        verification = self.result["verification"]
        self.assertEqual(verification["focused_result_tests"], 12)
        self.assertEqual(verification["complete_base_tests"], 3_083)
        self.assertEqual(verification["complete_optional_tests"], 3_154)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["remote_CI_pending"])

    def test_unavailable_measurements_are_explicit(self):
        unavailable = " ".join(self.result["unavailable_fields"])
        self.assertIn("runtime and peak RSS", unavailable)
        self.assertIn("selected participants", unavailable)
        self.assertIn("EEG signal", unavailable)

    def test_disposition_closes_old_lane_and_marc2_fw2(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["MARC2_FW1A_consumed"])
        self.assertFalse(disposition["old_implementation_may_be_modified_and_reused"])
        self.assertFalse(disposition["old_execution_may_be_retried_or_resumed"])
        self.assertFalse(disposition["private_manifest_access_authorized_now"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])
        self.assertTrue(
            disposition[
                "future_private_access_requires_new_all_false_Tier_C_packet_and_decision"
            ]
        )

    def test_claim_boundary_reports_engineering_not_science(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("failed closed", boundary["engineering_capability_demonstrated"])
        self.assertIn("No human EEG", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
