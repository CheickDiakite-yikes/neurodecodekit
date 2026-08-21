import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_variable_width_private_confirmation_result.v0.json"
)


class Marc2VariableWidthPrivateConfirmationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_proof_chain_precedes_execution(self):
        proof = self.result["execution_proof_chain"]
        self.assertEqual(
            proof["implementation_commit"],
            "55f23d60621949ea008cca1e3ade80a3127cfc70",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 32_464_397_821)
        self.assertEqual(
            proof["proof_closeout_commit"],
            "865d76aff51842e3b57600a7dab399d2bbe91d2e",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_465_104_587)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_consumed_route_and_measured_resources_are_exact(self):
        self.assertEqual(self.result["status"], "consumed_without_cohort_freeze")
        self.assertEqual(self.result["route"], "MARC2VR16P-R4")
        resources = self.result["resources"]
        self.assertEqual(resources["input_bytes"], 418_755)
        self.assertEqual(resources["output_bytes"], 2_702)
        self.assertEqual(resources["runtime_seconds"], 0.02044062502682209)
        self.assertEqual(resources["peak_RSS_bytes"], 30_474_240)
        self.assertLessEqual(resources["runtime_seconds"], 650)
        self.assertLess(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(resources["output_bytes"], 2 * 1024**2)
        for key in ("CPU_threads", "workers", "numerical_jobs"):
            self.assertEqual(resources[key], 1)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["new_payload_bytes"], 0)
        self.assertFalse(resources["end_to_end_latency_measured"])

    def test_one_shot_operation_counts_and_forbidden_counters_are_exact(self):
        operations = self.result["authorized_operations"]
        self.assertEqual(operations["fresh_readiness_samples"], 3)
        self.assertEqual(operations["private_structural_content_opens"], 1)
        self.assertEqual(operations["private_structural_source_bytes"], 418_755)
        self.assertEqual(operations["strict_JSON_parses"], 1)
        self.assertEqual(operations["VR16A_calls"], 1)
        self.assertEqual(operations["private_cohort_freezes"], 0)
        self.assertTrue(
            all(value == 0 for value in self.result["returned_forbidden_counters"].values())
        )

    def test_route_ceiling_preserves_three_way_uncertainty(self):
        route = self.result["route_interpretation"]
        self.assertEqual(
            route["frozen_class"],
            "numeric_identity_exact_task_or_companion_validation_refused",
        )
        self.assertTrue(route["VR16A_called_once"])
        for key, value in route.items():
            if key not in {"frozen_class", "VR16A_called_once"}:
                self.assertFalse(value, key)

    def test_no_private_reinspection_or_scientific_claim(self):
        handling = self.result["post_execution_handling"]
        self.assertEqual(handling["aggregate_report_inspections_after_execution"], 1)
        for key, value in handling.items():
            if key not in {"result_source", "aggregate_report_inspections_after_execution"}:
                self.assertIn(value, (0, False), key)
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
