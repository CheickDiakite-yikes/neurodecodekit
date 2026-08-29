import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/ofner_gdf_header_live_implementation.v0.json"


class OfnerGDFHeaderLiveImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_record_is_generated_qualified_but_not_activated(self):
        self.assertEqual(
            self.record["status"],
            "generated_qualified_remote_green_required_before_activation",
        )
        self.assertTrue(self.record["generated_qualification"]["all_gates_passed"])
        self.assertEqual(self.record["generated_qualification"]["registered_invocations"], 1)
        self.assertFalse(self.record["execution_state"]["activation_record_created"])
        self.assertFalse(self.record["execution_state"]["real_invocation_consumed"])
        self.assertFalse(self.record["next_gate"]["real_checkpoint_available_now"])
        self.assertTrue(all(value == 0 for value in self.record["real_operation_counters"].values()))

    def test_record_binds_every_implementation_artifact(self):
        bindings = self.record["tracked_file_hashes"]
        self.assertEqual(self.record["tracked_file_summary"]["count"], len(bindings))
        self.assertEqual(
            self.record["tracked_file_summary"]["bytes"],
            sum(binding["bytes"] for binding in bindings),
        )
        for binding in bindings:
            payload = (ROOT / binding["path"]).read_bytes()
            self.assertEqual(len(payload), binding["bytes"], binding["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                binding["sha256"],
                binding["path"],
            )

    def test_generated_result_is_bounded_and_zero_network(self):
        result = json.loads(
            (
                ROOT
                / "registries/ofner_gdf_header_live_generated_qualification.v0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(result["status"], "accepted_generated_only")
        self.assertEqual(result["measurements"]["generated_replays"], 2)
        self.assertEqual(result["measurements"]["named_adversarial_refusals"], 35)
        self.assertEqual(result["measurements"]["network_bytes"], 0)
        self.assertEqual(result["measurements"]["retained_generated_payload_bytes"], 0)
        self.assertLess(result["measurements"]["runtime_seconds"], 120)
        self.assertLess(result["measurements"]["peak_process_RSS_bytes"], 256 * 1024**2)
        self.assertTrue(all(value == 0 for value in result["real_operation_counters"].values()))


if __name__ == "__main__":
    unittest.main()
