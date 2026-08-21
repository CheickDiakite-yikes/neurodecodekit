import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_suffix_identity_private_discriminator_result.v0.json"
)


class Marc2SuffixIdentityPrivateDiscriminatorResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_failed_attempt_and_exact_green_activation_are_recorded(self):
        failed = self.result["failed_activation_attempt"]
        self.assertEqual(failed["commit"], "64fa1144d9412b983796b3da2bdfd5904a1562a1")
        self.assertEqual(failed["CI_run_id"], 32_455_530_795)
        self.assertFalse(failed["both_required_jobs_green"])
        self.assertEqual(failed["private_operations_after_failure"], 0)

        proof = self.result["activation_remote_proof"]
        self.assertEqual(proof["commit"], "a9ebef4fb7cafdd281cfa1c4034a63ddcd08f0a1")
        self.assertEqual(proof["CI_run_id"], 32_456_531_938)
        self.assertEqual(proof["base_python_job_id"], 96_694_803_139)
        self.assertEqual(proof["optional_neuro_job_id"], 96_694_803_152)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_consumed_route_and_measured_resources_are_exact(self):
        self.assertEqual(self.result["status"], "consumed")
        self.assertEqual(self.result["route"], "MARC2VR15P-R15")
        resources = self.result["resources"]
        self.assertEqual(resources["input_bytes"], 418_755)
        self.assertEqual(resources["output_bytes"], 2_288)
        self.assertEqual(resources["runtime_seconds"], 10.096426583011635)
        self.assertEqual(resources["peak_RSS_bytes"], 29_016_064)
        self.assertLessEqual(resources["runtime_seconds"], 30)
        self.assertLess(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(resources["output_bytes"], 1024**2)
        for key in ("CPU_threads", "workers", "numerical_jobs"):
            self.assertEqual(resources[key], 1)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["new_payload_bytes"], 0)

    def test_one_shot_operation_counts_are_exact(self):
        expected = {
            "fresh_readiness_samples": 3,
            "readiness_certificate_writes": 1,
            "consumed_marker_writes": 1,
            "private_structural_content_opens": 1,
            "strict_JSON_parses": 1,
            "VR15A_calls": 1,
            "nested_VR12A_calls": 1,
            "aggregate_report_writes": 1,
        }
        self.assertEqual(self.result["authorized_operations"], expected)
        self.assertTrue(
            all(value == 0 for value in self.result["returned_forbidden_counters"].values())
        )

    def test_route_ceiling_localizes_only_the_width_class(self):
        route = self.result["route_interpretation"]
        self.assertEqual(
            route["frozen_class"],
            "run_token_width_outside_one_or_two_ASCII_digits",
        )
        self.assertTrue(route["narrow_width_assumption_falsified"])
        for key, value in route.items():
            if key not in {"frozen_class", "narrow_width_assumption_falsified"}:
                self.assertFalse(value, key)

    def test_no_reinspection_or_scientific_claim(self):
        handling = self.result["post_execution_handling"]
        for key, value in handling.items():
            if key != "result_source":
                self.assertIn(value, (0, False), key)
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
