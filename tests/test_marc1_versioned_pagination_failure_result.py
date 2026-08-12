from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc1_versioned_pagination_failure_result.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/MARC_1_VERSIONED_PAGINATION_GENERATED_RESULT.md"
SOURCE_PATH = ROOT / "src/neurodecodekit/datasets/marc1_versioned_pagination.py"
RESULT_SHA256 = "b99be5d82e1f49f064cf17e4a7b2d6a21e36d89cebc78b133136b181fb4bdcf2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1VersionedPaginationFailureResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result_bytes = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.result_bytes)

    def test_result_identity_hash_and_consumed_status_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.result_bytes).hexdigest(), RESULT_SHA256)
        self.assertEqual(len(self.result_bytes), 8122)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_versioned_pagination_failure_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC1-PG1")
        self.assertEqual(
            self.result["status"],
            "consumed_at_MARC1PG_F07_output_parent_symlink_no_retry_or_rerun",
        )

    def test_bound_artifacts_are_current(self) -> None:
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_remote_green_implementation_preceded_invocation(self) -> None:
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"],
            "2c98a2ad4b3972de5c2a398b85c0cf8735db89d4",
        )
        self.assertEqual(proof["CI_run_id"], 31593790492)
        self.assertEqual(proof["base_python_job_id"], 94104455930)
        self.assertEqual(proof["optional_neuro_job_id"], 94104455857)
        self.assertTrue(proof["both_required_jobs_green_before_invocation"])

    def test_one_invocation_refused_at_the_exact_path_gate(self) -> None:
        run = self.result["registered_invocation"]
        self.assertEqual(run["registered_runs"], 1)
        self.assertEqual(run["invocations_attempted"], 1)
        self.assertEqual(run["successful_closeouts"], 0)
        self.assertEqual((run["retries_after_refusal"], run["reruns_after_refusal"]), (0, 0))
        self.assertEqual(run["route"], "MARC1PG-F07")
        self.assertEqual(run["safe_reason"], "output parent is a symlink")
        self.assertEqual(run["requested_output_parent"], "/tmp")
        self.assertEqual(run["observed_parent_link_text"], "private/tmp")
        self.assertFalse(run["requested_output_path_created"])
        self.assertTrue(run["contract_consumed"])

    def test_source_order_proves_fixture_work_preceded_preflight(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        start = source.index("def qualify_generated_pagination(")
        end = source.index("def inspect_generated_report(", start)
        body = source[start:end]
        self.assertLess(body.index("load_registered_contract(root)"), body.index("_assert_new_output_directory(output)"))
        self.assertLess(body.index("build_generated_freewill_manifest("), body.index("_assert_new_output_directory(output)"))
        self.assertLess(body.index("build_generated_wrist_rows()"), body.index("_assert_new_output_directory(output)"))
        self.assertLess(body.index("private_bytes ="), body.index("_assert_new_output_directory(output)"))
        self.assertLess(body.index("_assert_new_output_directory(output)"), body.index("run_refusal_matrix("))

    def test_pre_refusal_operation_ledger_is_exact_and_partial(self) -> None:
        operations = self.result["pre_refusal_generated_operations"]
        self.assertEqual(operations["Freewill_inventory_rows_constructed"], 1227)
        self.assertEqual(operations["Wrist_inventory_rows_constructed"], 55)
        self.assertEqual(operations["accepted_mock_cases_constructed_and_validated"], 4)
        self.assertEqual(operations["accepted_case_target_free_selections"], 4)
        self.assertTrue(operations["accepted_case_selection_hash_equality_checked"])
        self.assertEqual(
            operations["generated_private_manifest_rows_constructed_in_memory"],
            300,
        )
        self.assertFalse(operations["generated_private_manifest_written"])
        self.assertEqual(operations["refusal_matrix_cases_run"], 0)
        self.assertFalse(operations["public_report_assembled"])

    def test_resources_record_zero_output_and_unavailable_internal_metrics(self) -> None:
        resources = self.result["resources"]
        self.assertEqual(resources["external_wall_seconds"], 0.17)
        self.assertEqual(resources["external_maximum_RSS_bytes"], 30064640)
        self.assertLess(resources["external_maximum_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["generated_output_bytes"], 0)
        self.assertEqual(resources["incremental_disk_bytes"], 0)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["real_or_private_input_bytes"], 0)
        self.assertIsNone(resources["internal_runtime_seconds"])
        self.assertIsNone(resources["generated_input_bytes"])
        verification = self.result["closeout_verification"]
        self.assertEqual(verification["focused_pagination_tests"], 39)
        self.assertEqual(verification["final_MARC1_tests"], 528)
        self.assertEqual(verification["dependency_light_tests"], 2667)
        self.assertEqual(verification["optional_neuro_tests"], 2738)
        self.assertEqual(verification["tests_added_over_green_implementation"], 10)
        self.assertEqual(verification["additional_skips"], 0)
        self.assertFalse(verification["qualify_command_rerun_during_verification"])

    def test_every_real_protected_model_and_claim_counter_is_zero(self) -> None:
        counters = self.result["access_counters"]
        self.assertTrue(counters)
        for key, value in counters.items():
            with self.subTest(key=key):
                self.assertEqual(value, 0)

    def test_no_retry_live_escalation_or_claim_is_open(self) -> None:
        boundary = self.result["consumption_and_authorization"]
        self.assertTrue(boundary["MARC1_PG1_consumed"])
        for key, value in boundary.items():
            if key != "MARC1_PG1_consumed":
                with self.subTest(key=key):
                    self.assertFalse(value)
        recovery = self.result["prospective_recovery_requirements"]
        self.assertTrue(all(recovery.values()))

    def test_human_record_preserves_same_path_and_claim_boundary(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        normalized = " ".join(document.split())
        for phrase in (
            "Consumed at `MARC1PG-F07`",
            "one registered closeout was therefore consumed",
            "No corrected invocation is allowed",
            "not a pivot",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)
        disposition = self.result["disposition"]
        self.assertTrue(disposition["same_thought_to_text_path"])
        self.assertFalse(disposition["is_pivot"])


if __name__ == "__main__":
    unittest.main()
