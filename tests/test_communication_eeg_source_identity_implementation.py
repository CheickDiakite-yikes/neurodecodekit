import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_source_identity_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CommunicationEEGSourceIdentityImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_schema_status_and_green_registration(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.communication_eeg_source_identity_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertIn("qualification_not_yet_consumed", self.record["status"])
        proof = self.record["green_registration"]
        self.assertEqual(
            proof["commit"], "f4a30e4323834dbd53f5c3cc4abee52829ec016a"
        )
        self.assertEqual(proof["CI_run_id"], 33_035_992_877)
        self.assertEqual(proof["base_python_job_id"], 98_398_680_307)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 98_398_680_155)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_every_binding_is_exact(self):
        for binding in self.record["bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_module_has_generated_only_commands(self):
        surface = self.record["surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command"])
        self.assertFalse(surface["network_constructor"])
        self.assertFalse(surface["real_dataset_path_mode"])
        self.assertFalse(surface["payload_mode"])

    def test_module_contains_no_request_or_socket_constructor(self):
        source = (
            ROOT
            / "src"
            / "neurodecodekit"
            / "datasets"
            / "communication_eeg_source_identity.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "urllib.request",
            "import socket",
            "http.client",
            "requests.",
            "openneuro.org/crn/graphql",
        ):
            self.assertNotIn(forbidden, source)

    def test_selection_is_exact_and_target_free(self):
        selection = self.record["selection_implementation"]
        self.assertEqual(selection["participant_count"], 10)
        self.assertEqual(selection["complete_sessions_per_participant"], 3)
        self.assertEqual(selection["selected_sessions_per_participant"], 1)
        self.assertEqual(selection["selected_raw_BDF_count"], 10)
        self.assertEqual(selection["maximum_selected_bytes"], 10 << 30)
        self.assertFalse(selection["participant_dropping"])
        self.assertFalse(selection["target_or_result_based_selection"])

    def test_generated_schedule_is_frozen_but_unconsumed(self):
        generated = self.record["generated_qualification_schedule"]
        self.assertEqual(generated["deterministic_success_replays"], 2)
        self.assertEqual(generated["adversarial_refusals"], 20)
        self.assertEqual(generated["official_invocations_completed"], 0)
        self.assertFalse(generated["consumed"])
        self.assertFalse(generated["scientific_claim_value"])

    def test_resources_and_authority_stay_closed(self):
        resources = self.record["resource_caps"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 << 20)
        self.assertEqual(resources["response_bytes"], 2 << 20)
        self.assertEqual(resources["output_bytes"], 1 << 20)
        self.assertTrue(all(not value for value in self.record["authorization_state"].values()))
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_claim_boundary_is_non_scientific(self):
        boundary = self.record["claim_boundary"]
        self.assertIn("generated-only", boundary["engineering_capability_added"])
        self.assertIn("no real metadata", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
