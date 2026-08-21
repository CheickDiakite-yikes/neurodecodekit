import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_incident_aggregate_recovery_result.v0.json"
)


class Marc2IncidentAggregateRecoveryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_activation_and_route_are_recorded(self):
        proof = self.result["activation_remote_proof"]
        self.assertEqual(proof["commit"], "6bfff69048d4c3cffc971882be3b60c9fcaa5eae")
        self.assertEqual(proof["CI_run_id"], 32_446_635_433)
        self.assertEqual(proof["base_python_job_id"], 96_667_351_062)
        self.assertEqual(proof["optional_neuro_job_id"], 96_667_350_910)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(self.result["status"], "consumed")
        self.assertEqual(self.result["route"], "MARC2VR13P-R2")

    def test_measured_resources_are_inside_the_frozen_caps(self):
        resources = self.result["resources"]
        self.assertEqual(resources["input_bytes"], 1_543)
        self.assertEqual(resources["receipt_bytes"], 1_945)
        self.assertLessEqual(resources["runtime_seconds"], 30)
        self.assertLessEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(resources["receipt_bytes"], 1024**2)
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["new_payload_bytes"], 0)

    def test_one_shot_operation_counts_are_exact(self):
        operations = self.result["operations"]
        for key in (
            "aggregate_report_lstats",
            "aggregate_report_content_opens",
            "aggregate_report_strict_JSON_parses",
            "aggregate_recovery_receipt_writes",
        ):
            self.assertEqual(operations[key], 1)
        for key, value in operations.items():
            if key not in {
                "aggregate_report_lstats",
                "aggregate_report_content_opens",
                "aggregate_report_strict_JSON_parses",
                "aggregate_recovery_receipt_writes",
            }:
                self.assertEqual(value, 0, key)

    def test_route_ceiling_reveals_no_private_detail(self):
        route = self.result["route_interpretation"]
        self.assertEqual(
            route["frozen_class"],
            "suffix_bearing_BIDS_identity_structural_class_only",
        )
        for key, value in route.items():
            if key != "frozen_class":
                self.assertFalse(value)
        self.assertTrue(
            all(value == 0 for value in self.result["aggregate"].values())
        )

    def test_no_reinspection_or_scientific_claim(self):
        handling = self.result["post_execution_handling"]
        for key, value in handling.items():
            if key == "result_source":
                continue
            self.assertIn(value, (0, False))
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
