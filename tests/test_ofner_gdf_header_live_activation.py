import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import ofner_gdf_header_live as live

ROOT = Path(__file__).resolve().parents[1]
ACTIVATION = ROOT / "registries/ofner_gdf_header_live_activation.v0.json"


class OfnerGDFHeaderLiveActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))

    def test_activation_binds_exact_green_implementation(self):
        implementation = self.activation["green_implementation"]
        self.assertEqual(
            implementation["commit"],
            "b6c55dfed93d803a14df906f9c0b57c04e44cd58",
        )
        self.assertEqual(implementation["CI_run_id"], 33277551227)
        self.assertEqual(implementation["base_python_job_id"], 99166826652)
        self.assertEqual(implementation["optional_neuro_readers_job_id"], 99166826697)
        payload = (ROOT / implementation["registry_path"]).read_bytes()
        self.assertEqual(len(payload), implementation["registry_bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), implementation["registry_sha256"])
        record = live.load_implementation_record(
            ROOT,
            expected_sha256=implementation["registry_sha256"],
        )
        self.assertTrue(record["generated_qualification"]["all_gates_passed"])

    def test_activation_is_one_shot_and_range_only(self):
        authority = self.activation["authority"]
        self.assertEqual(authority["registered_invocations"], 1)
        self.assertEqual(authority["success_manifest_GET_requests"], 1)
        self.assertEqual(authority["success_GDF_range_GET_requests"], 2)
        self.assertEqual(authority["first_range"], "bytes=0-255")
        self.assertEqual(
            authority["second_range"],
            "bytes=256-(declared_header_length-1)",
        )
        for key in (
            "whole_GDF_file_requests",
            "full_payload_SHA256_passes",
            "event_or_annotation_reads",
            "signal_sample_reads",
            "target_or_label_reads",
            "model_or_checkpoint_opens",
            "training_runs",
            "model_inference_runs",
            "scores",
            "redirects",
            "retries",
            "reruns",
            "fallbacks_or_substitutions",
            "scientific_claim_upgrades",
        ):
            self.assertEqual(authority[key], 0, key)

    def test_activation_created_no_real_operation(self):
        counters = self.activation["activation_record_operation_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key != "GitHub_CI_verification_calls")
        )
        state = self.activation["execution_state"]
        self.assertFalse(state["consumed_marker_present"])
        self.assertFalse(state["real_invocation_consumed"])
        self.assertIsNone(state["terminal_route"])

    def test_human_activation_preserves_claim_boundary(self):
        text = (
            ROOT / "docs/OFNER_2017_MOTOR_IMAGERY_RANGE_HEADER_ACTIVATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability activated:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("Every post-marker outcome", text)


if __name__ == "__main__":
    unittest.main()
