from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc1_output_capability_recovery_result.v0.json"
DOCUMENT_PATH = ROOT / "docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESULT.md"
REGISTRY_SHA256 = "162ba18d403007a80875d3fa56c0284f991d433f4f7e5356f1bbc630fcff1725"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1OutputCapabilityRecoveryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_bytes = REGISTRY_PATH.read_bytes()
        cls.result = json.loads(cls.registry_bytes)

    def test_identity_hash_and_consumed_status_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.registry_bytes).hexdigest(), REGISTRY_SHA256)
        self.assertEqual(len(self.registry_bytes), 8795)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_output_capability_recovery_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC1-OP1")
        self.assertEqual(
            self.result["status"],
            "passed_and_consumed_at_MARC1OP_G1_no_retry_or_rerun",
        )

    def test_every_artifact_binding_matches(self) -> None:
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_green_implementation_preceded_registered_path_access(self) -> None:
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"], "fcedcc308c1038c765605571c19ba24eb4f7603f"
        )
        self.assertEqual(proof["CI_run_id"], 31600085119)
        self.assertEqual(proof["base_python_job_id"], 94125013790)
        self.assertEqual(proof["optional_neuro_job_id"], 94125013956)
        self.assertTrue(proof["both_required_jobs_green_before_registered_path_operation"])

    def test_registered_sequence_is_exact_successful_and_consumed(self) -> None:
        sequence = self.result["registered_sequence"]
        self.assertEqual(
            sequence["output_path"],
            "/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812",
        )
        self.assertFalse(sequence["path_substitution"])
        self.assertEqual(sequence["path_only_preflight_invocations"], 1)
        self.assertEqual(sequence["path_only_preflight_route"], "MARC1OP-P0")
        self.assertTrue(sequence["qualifier_opened_only_after_MARC1OP_P0"])
        self.assertEqual(sequence["generated_qualifier_invocations"], 1)
        self.assertEqual(sequence["generated_qualifier_route"], "MARC1OP-G1")
        self.assertTrue(sequence["registered_sequence_consumed"])
        self.assertFalse(sequence["retry_or_rerun_available"])

    def test_preflight_passed_with_zero_experiment_work(self) -> None:
        preflight = self.result["registered_preflight"]
        self.assertEqual(preflight["route"], "MARC1OP-P0")
        self.assertEqual(preflight["capability_acquisitions"], 1)
        self.assertTrue(all(value == 0 for value in preflight["early_operation_counters"].values()))
        self.assertEqual(preflight["output_files_created"], 0)
        self.assertEqual(preflight["output_bytes"], 0)
        self.assertEqual(preflight["network_bytes"], 0)
        self.assertEqual(preflight["real_or_private_input_bytes"], 0)

    def test_qualifier_passed_all_cases_refusals_and_gates(self) -> None:
        qualifier = self.result["registered_qualifier"]
        self.assertEqual(qualifier["route"], "MARC1OP-G1")
        self.assertEqual(qualifier["accepted_cases_passed"], 6)
        self.assertEqual(qualifier["refusal_cases_passed"], 32)
        self.assertEqual(qualifier["precapability_refusals"], 19)
        self.assertEqual(qualifier["postcapability_refusals"], 13)
        self.assertEqual(qualifier["acceptance_gates_passed"], 20)
        self.assertTrue(qualifier["temporary_output_removed_before_return"])

    def test_registered_measurements_are_under_every_cap(self) -> None:
        qualifier = self.result["registered_qualifier"]
        caps = self.result["resource_caps"]
        self.assertLess(qualifier["reported_runtime_seconds"], caps["runtime_seconds"])
        self.assertLess(qualifier["reported_peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLess(qualifier["generated_input_bytes"], caps["generated_input_bytes"])
        self.assertLess(qualifier["combined_output_bytes"], caps["combined_output_bytes"])
        self.assertLess(qualifier["incremental_disk_bytes"], caps["incremental_disk_bytes"])

    def test_capability_output_and_cleanup_result_is_exact(self) -> None:
        capability = self.result["capability_and_output_result"]
        self.assertTrue(capability["capability_first_in_both_registered_operations"])
        self.assertTrue(capability["all_seven_early_counters_zero"])
        self.assertTrue(capability["held_parent_device_inode_and_type_revalidated"])
        self.assertEqual(capability["parent_relative_exclusive_writes"], 2)
        self.assertEqual(capability["absolute_path_file_writes"], 0)
        self.assertEqual(capability["public_report_inspections"], 1)
        self.assertEqual(capability["private_manifest_inspections"], 0)
        self.assertEqual(capability["relative_file_unlinks"], 2)
        self.assertFalse(capability["output_exists_after_return"])

    def test_semantic_identity_is_generated_target_free_and_not_live(self) -> None:
        identity = self.result["semantic_and_selection_result"]
        self.assertEqual(identity["request_query"], "page=1&page_size=1000")
        self.assertEqual(identity["Wrist_rows"], 55)
        self.assertEqual(identity["selected_subjects_per_axis"], 12)
        self.assertEqual(identity["Freewill_run_bundles"], 72)
        self.assertEqual(identity["fit_heldout_overlap"], 0)
        self.assertTrue(identity["selection_target_label_quality_size_checksum_and_outcome_free"])
        self.assertFalse(identity["participant_IDs_public"])
        self.assertFalse(identity["live_inventory_compatibility_established"])

    def test_access_ledger_and_forbidden_counters_are_exact(self) -> None:
        ledger = self.result["registered_public_access_ledger"]
        self.assertEqual(ledger["bound_repository_reads"], 10)
        self.assertEqual(ledger["contract_loads"], 2)
        self.assertEqual(ledger["generated_rows"], 1282)
        self.assertEqual(ledger["selection_runs"], 4)
        self.assertEqual(ledger["output_files_created"], 2)
        self.assertEqual(ledger["output_bytes_allocated"], 184173)
        self.assertTrue(all(value == 0 for value in self.result["forbidden_access_counters"].values()))

    def test_next_gate_requires_green_result_then_fresh_Tier_C_decision(self) -> None:
        self.assertTrue(all(self.result["next_gate"].values()))
        verification = self.result["verification"]
        self.assertEqual(verification["status"], "complete_all_result_gates_passed")
        self.assertEqual(verification["focused_result_tests"], 12)
        self.assertEqual(verification["final_MARC1_tests"], 599)
        self.assertEqual(verification["dependency_light_tests"], 2738)
        self.assertEqual(verification["optional_neuro_tests"], 2809)
        self.assertEqual(verification["result_test_delta"], 12)
        self.assertEqual(verification["additional_skips"], 0)
        self.assertEqual(verification["registered_operation_reruns_during_verification"], 0)

    def test_warnings_claim_boundary_and_same_path_are_explicit(self) -> None:
        self.assertEqual(len(self.result["warnings"]), 5)
        claim = self.result["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "It is not a pivot",
            "Both registered invocations are consumed",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
