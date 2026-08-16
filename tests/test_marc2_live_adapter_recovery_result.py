import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_live_schema_adapter_recovery as live


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_live_adapter_recovery_result.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveAdapterRecoveryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_consumed_and_remote_pending(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_live_adapter_recovery_closeout",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-LA2")
        self.assertEqual(self.result["route"], "MARC2LAR-G1")
        self.assertEqual(
            self.result["status"],
            "generated_qualification_complete_consumed_remote_green_pending",
        )
        self.assertFalse(self.result["proof_posture"]["scientific_value"])
        summary = live.inspect_public_result(RESULT_PATH)
        self.assertEqual(summary["route"], "MARC2LAR-G1")
        self.assertEqual(summary["selected_subjects"], 16)

    def test_all_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]),
                    binding["sha256"],
                )

    def test_exact_public_composition_and_replay_passed(self):
        composition = self.result["composition_result"]
        self.assertTrue(composition["shared_proof_validator_exact"])
        self.assertTrue(composition["LA1_adapter_exact"])
        self.assertTrue(composition["selector_exact"])
        self.assertEqual(composition["LA1_calls_per_success"], 1)
        self.assertEqual(composition["selector_calls_per_success"], 1)
        self.assertTrue(composition["canonical_and_reversed_replay"])

    def test_generated_prefix_is_exact_and_target_free(self):
        selection = self.result["generated_selection"]
        self.assertEqual(selection["selected_subjects"], 16)
        self.assertEqual(selection["selected_run_bundles"], 96)
        self.assertEqual(selection["selected_core_members"], 384)
        self.assertEqual(selection["selected_reservation_bytes"], 8_105_207_776)
        self.assertTrue(selection["target_quality_and_outcome_free"])

    def test_all_mutations_and_acceptance_gates_passed(self):
        mutations = self.result["mutation_result"]
        self.assertEqual(mutations["proof_certificate_passed"], 32)
        self.assertEqual(mutations["executor_passed"], 24)
        self.assertEqual(mutations["total_direct_passed"], 56)
        self.assertEqual(sum(mutations["executor_route_counts"].values()), 24)
        self.assertEqual(self.result["acceptance_gates_passed"], 10)
        self.assertEqual(self.result["acceptance_gates_required"], 10)

    def test_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 846_696)
        self.assertEqual(measured["combined_output_bytes"], 221_863)
        self.assertEqual(measured["runtime_seconds"], 0.27368504100013524)
        self.assertEqual(measured["peak_RSS_bytes"], 37_978_112)
        self.assertLess(measured["combined_output_bytes"], 2 * 1024**2)
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertFalse(measured["temporary_output_retained"])

    def test_no_private_neural_model_or_network_operation_occurred(self):
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))
        measured = self.result["measurements"]
        self.assertEqual(measured["raw_data_reads"], 0)
        self.assertEqual(measured["real_cache_reads"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)

    def test_private_stage_remains_closed_until_exact_remote_green(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["generated_qualification_consumed"])
        self.assertTrue(disposition["temporary_output_removed"])
        self.assertTrue(disposition["implementation_remote_green_pending"])
        self.assertFalse(disposition["private_selection_executed"])
        self.assertFalse(disposition["archive_member_or_payload_allowed"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])

    def test_claim_boundary_is_explicit(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("proof-gated additive executor", boundary["engineering_capability_added"])
        scientific = boundary["scientific_claim_not_established"].lower()
        self.assertIn("no human neural signal", scientific)
        self.assertIn("thought-to-text", scientific)


if __name__ == "__main__":
    unittest.main()
