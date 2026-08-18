import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/marc2_p15_private_confirmation_implementation.v0.json"


class Marc2P15PrivateConfirmationImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_record_is_stage_1_only_and_proof_gated(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_p15_private_confirmation_implementation",
        )
        self.assertEqual(self.record["lane_id"], "MARC2-VR12P")
        self.assertIsNone(self.record["remote_implementation_proof"])
        self.assertFalse(self.record["stage_2_status"]["private_execution_available_now"])

    def test_every_implementation_artifact_is_exact(self):
        for artifact in self.record["implementation_artifacts"]:
            with self.subTest(path=artifact["path"]):
                payload = (ROOT / artifact["path"]).read_bytes()
                self.assertEqual(len(payload), artifact["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_generated_measurements_pass_all_caps(self):
        measured = self.record["generated_qualification"]
        caps = self.record["resource_caps"]
        self.assertEqual(measured["route"], "MARC2VR12P-G1")
        self.assertEqual(measured["success_paths"], 12)
        self.assertEqual(measured["VR12A_calls"], 12)
        self.assertGreaterEqual(measured["direct_refusals"], 50)
        self.assertLessEqual(measured["runtime_seconds"], caps["generated_runtime_seconds_maximum"])
        self.assertLess(measured["peak_RSS_bytes"], caps["peak_RSS_bytes_maximum_exclusive"])
        self.assertLessEqual(
            measured["peak_incremental_output_bytes"],
            caps["peak_incremental_output_bytes_maximum"],
        )
        self.assertEqual(measured["retained_generated_output_bytes"], 0)

    def test_every_forbidden_operation_counter_is_zero(self):
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_wrapper_does_not_reference_consumed_private_executors(self):
        source = (ROOT / "src/neurodecodekit/datasets/marc2_p15_private_confirmation.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "marc2_f03_private_discriminator",
            "marc2_two_layer_private_diagnostic",
            "MARC2VR11P",
            "MARC2VR9P",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
