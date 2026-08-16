import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_transport_alias_adapter_result.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2TransportAliasAdapterResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_is_generated_only_and_consumed(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_transport_alias_adapter_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-TA1")
        self.assertEqual(self.result["route"], "MARC2TA-G1")
        self.assertEqual(
            self.result["status"],
            "generated_qualification_complete_consumed_remote_green",
        )
        self.assertFalse(self.result["proof_posture"]["scientific_value"])
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"], "108b869a6199b6d3aa2d87f8a59b6d8bee0c847b"
        )
        self.assertEqual(proof["CI_run_id"], 31_933_692_066)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_all_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )

    def test_single_alias_passed_without_source_mutation(self):
        result = self.result["adapter_result"]
        self.assertEqual(result["source_key"], "directory")
        self.assertEqual(result["selector_key"], "central_directory")
        self.assertTrue(result["source_validated_before_copy_or_mapping"])
        self.assertFalse(result["source_mutated"])
        self.assertFalse(result["mutable_alias_detected"])
        self.assertTrue(result["all_transport_values_preserved"])

    def test_generated_selector_identity_replayed_exactly(self):
        selection = self.result["selector_result"]
        self.assertEqual(selection["selected_subjects"], 16)
        self.assertEqual(selection["selected_run_bundles"], 96)
        self.assertEqual(selection["selected_core_members"], 384)
        self.assertEqual(selection["selected_reservation_bytes"], 8_105_207_776)
        self.assertTrue(selection["existing_generated_identity_matched"])
        self.assertTrue(selection["canonical_and_reversed_orders_matched"])

    def test_all_mutations_and_acceptance_gates_passed(self):
        mutations = self.result["mutation_result"]
        self.assertEqual(mutations["required"], 26)
        self.assertEqual(mutations["passed"], 26)
        self.assertEqual(sum(mutations["route_counts"].values()), 26)
        self.assertEqual(self.result["acceptance_gates_passed"], 15)
        self.assertEqual(self.result["acceptance_gates_required"], 15)

    def test_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 846_708)
        self.assertEqual(measured["generated_output_bytes"], 4_931)
        self.assertEqual(measured["runtime_seconds"], 0.4533158749982249)
        self.assertEqual(measured["peak_RSS_bytes"], 39_108_608)
        self.assertEqual(
            measured["report_SHA256"],
            "40303300d396415cf6833707330303b8cbf60b1576bbe6c7b9a70825ff0af28a",
        )
        self.assertFalse(measured["temporary_output_retained"])

    def test_no_real_neural_or_model_operation_occurred(self):
        self.assertTrue(
            all(value == 0 for value in self.result["access_counters"].values())
        )
        self.assertEqual(self.result["measurements"]["raw_data_reads"], 0)
        self.assertEqual(self.result["measurements"]["real_cache_reads"], 0)
        self.assertEqual(self.result["measurements"]["model_runs"], 0)
        self.assertEqual(self.result["measurements"]["training_runs"], 0)
        self.assertFalse(
            self.result["measurements"]["end_to_end_latency_measured"]
        )

    def test_live_boundary_remains_closed(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["generated_qualification_consumed"])
        self.assertFalse(disposition["live_adapter_or_private_read_allowed"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])
        self.assertTrue(
            disposition["future_live_attempt_requires_new_Tier_C_packet_and_decision"]
        )

    def test_claim_boundary_is_exact(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("schema adapter", boundary["engineering_capability_added"])
        self.assertIn(
            "no neural payload",
            boundary["scientific_claim_not_established"].lower(),
        )


if __name__ == "__main__":
    unittest.main()
