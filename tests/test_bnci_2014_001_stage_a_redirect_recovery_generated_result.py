import json
import os
import unittest
from pathlib import Path

from neurodecodekit.datasets.bnci_2014_001_acquisition import BNCIAcquisitionRefusal
from neurodecodekit.datasets import (
    bnci_2014_001_stage_a_redirect_recovery as recovery,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "registries/bnci_2014_001_stage_a_redirect_recovery_generated_result.v0.json"
)
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_REDIRECT_RECOVERY_GENERATED_RESULT.md"


class BNCIStageARedirectRecoveryGeneratedResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_exact_generated_result_and_resource_measurements(self):
        self.assertEqual(self.result["case_classes_passed"], 18)
        self.assertEqual(self.result["validated_exact_members"], 18)
        self.assertEqual(self.result["validated_exact_member_bytes"], 779_873_919)
        self.assertEqual(self.result["direct_refusals"], 12)
        self.assertEqual(self.result["generated_operations"]["payload_requests"], 4)
        self.assertEqual(self.result["generated_operations"]["resume_requests"], 1)
        self.assertEqual(self.result["measurements"]["retained_generated_payload_bytes"], 0)
        self.assertLess(self.result["measurements"]["runtime_seconds"], 30)
        self.assertLess(self.result["measurements"]["peak_process_RSS_bytes"], 256 * 1024 * 1024)

    def test_every_real_operation_is_zero(self):
        self.assertTrue(all(value == 0 for value in self.result["real_operations"].values()))
        self.assertFalse(self.result["claim_boundary"]["scientific_claim_established"])

    def test_result_registry_closes_qualification_before_any_generated_work(self):
        previous = {name: os.environ.get(name) for name in recovery.THREAD_ENVIRONMENT}
        try:
            for name in recovery.THREAD_ENVIRONMENT:
                os.environ[name] = "1"
            with self.assertRaises(BNCIAcquisitionRefusal):
                recovery.run_generated_recovery_qualification()
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_result_document_is_explicitly_non_scientific(self):
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering result:", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
