from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/neural_payload_admission_generated_implementation.v0.json"
DOCUMENT = ROOT / "docs/NEURAL_PAYLOAD_ADMISSION_GENERATED_IMPLEMENTATION.md"


class NeuralPayloadAdmissionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_frontier_proof_is_exact(self) -> None:
        green = self.record["green_frontier"]
        self.assertEqual(
            green["commit"], "d07eea0bc0ae2d6a218c06e08ef9ffa7e1592c35"
        )
        self.assertEqual(green["CI_run_id"], 33_281_704_903)
        self.assertEqual(green["base_python_job_id"], 99_177_847_778)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_177_847_631)
        self.assertTrue(green["both_required_jobs_green"])

    def test_implementation_artifacts_are_byte_exact(self) -> None:
        for artifact in self.record["implementation_artifacts"]:
            path = ROOT / artifact["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), artifact["bytes"], artifact["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                artifact["sha256"],
                artifact["path"],
            )

    def test_generated_qualification_is_complete_and_deterministic(self) -> None:
        result = self.record["qualification"]
        self.assertEqual(result["deterministic_replays"], 2)
        self.assertEqual(result["accepted_profiles_per_replay"], 7)
        self.assertEqual(result["named_adversarial_families"], 37)
        self.assertTrue(result["stable_transcript_digests_equal"])
        self.assertTrue(result["signed_capability_refresh_accepted"])
        self.assertTrue(result["all_gates_passed"])

    def test_measurements_are_bounded_and_operations_are_zero(self) -> None:
        measured = self.record["measurements"]
        self.assertLessEqual(measured["runtime_seconds"], 30)
        self.assertLessEqual(measured["peak_RSS_bytes"], 268_435_456)
        self.assertLessEqual(
            measured["generated_input_bytes"] + measured["generated_output_bytes"],
            8_388_608,
        )
        self.assertEqual(measured["response_opens"], measured["response_closes"])
        self.assertEqual(measured["retained_generated_payload_bytes"], 0)
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_capability_and_authority_boundaries_are_closed(self) -> None:
        capabilities = self.record["capabilities"]
        self.assertFalse(capabilities["live_network_client_present"])
        self.assertFalse(capabilities["real_execution_command_present"])
        authority = self.record["authority"]
        self.assertTrue(authority["proof_only_closeout_after_exact_remote_green"])
        for key, value in authority.items():
            if key != "proof_only_closeout_after_exact_remote_green":
                self.assertFalse(value, key)

    def test_document_separates_engineering_from_science(self) -> None:
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("no live network opener", text)
        self.assertIn("canary is still Tier C", text)


if __name__ == "__main__":
    unittest.main()
