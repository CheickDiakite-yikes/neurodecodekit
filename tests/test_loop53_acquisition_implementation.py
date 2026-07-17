import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries/loop53_acquisition_implementation.v0.json"
DOC_PATH = REPO_ROOT / "docs/LOOP_53_ACQUISITION_IMPLEMENTATION.md"
HISTORICAL_MUTABLE_BINDINGS = {
    "cli": "6aee3a3166863428abe5d26c24736ad5549e7aa2c2f77dfa286e29eb459ec342",
}


def sha256(relative_path):
    return hashlib.sha256((REPO_ROOT / relative_path).read_bytes()).hexdigest()


class Loop53AcquisitionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_authorization_bindings(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.loop53_acquisition_implementation",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(
            registry["status"],
            "implemented_locally_fixture_qualified_remote_green_pending_no_execution",
        )
        binding = registry["authorization_binding"]
        self.assertEqual(
            binding["authorization_commit"],
            "2a47bbc75eac0118c3f9de87363d7da02584d2fc",
        )
        self.assertEqual(binding["authorization_push_ci_run_id"], 29589212626)
        self.assertEqual(binding["authorization_pull_request_ci_run_id"], 29589225113)
        self.assertTrue(binding["both_authorization_workflows_green_before_implementation"])

    def test_source_hashes_preserve_historical_cli_and_current_owned_files(self):
        for name, binding in self.registry["source_bindings"].items():
            if name in HISTORICAL_MUTABLE_BINDINGS:
                self.assertEqual(binding["sha256"], HISTORICAL_MUTABLE_BINDINGS[name])
                current_source = (REPO_ROOT / binding["path"]).read_text(encoding="utf-8")
                self.assertIn("_cmd_loop53_acquire_s20", current_source)
                self.assertIn('"loop53-acquire-s20"', current_source)
            else:
                self.assertEqual(binding["sha256"], sha256(binding["path"]), binding["path"])

    def test_interface_is_dependency_light_dry_run_by_default_and_parser_free(self):
        interface = self.registry["frozen_interface"]
        self.assertEqual(interface["cli_command"], "loop53-acquire-s20")
        self.assertEqual(interface["default_mode"], "dry_run_no_registered_path_stat_no_network")
        self.assertTrue(interface["execution_requires_explicit_flag"])
        self.assertTrue(interface["execution_requires_current_full_implementation_commit"])
        self.assertEqual(interface["base_dependencies_added"], [])
        self.assertFalse(interface["payload_parser_exposed"])
        self.assertEqual(interface["receipt_files"], [
            "acquisition_manifest.json",
            "acquisition_receipt.md",
        ])

    def test_identity_and_resources_match_registered_contract(self):
        identity = self.registry["enforced_identity"]
        resources = self.registry["enforced_resources"]
        self.assertEqual(identity["repository"], "bcbl190626/SpanishBCBL")
        self.assertEqual(identity["file_count"], 4)
        self.assertEqual(identity["expected_payload_bytes"], 96090264)
        self.assertFalse(identity["substitution_allowed"])
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["wall_time_seconds"], 600)
        self.assertEqual(resources["peak_rss_bytes"], 512 * 1024 * 1024)
        self.assertEqual(resources["maximum_network_payload_bytes"], 128 * 1024 * 1024)
        self.assertEqual(resources["maximum_incremental_disk_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["minimum_free_disk_bytes"], 2 * 1024 * 1024 * 1024)
        self.assertEqual(resources["maximum_manifest_and_receipt_bytes"], 1024 * 1024)

    def test_implementation_has_zero_real_or_protected_operations(self):
        fixture = self.registry["fixture_qualification"]
        execution = self.registry["execution_state"]
        self.assertEqual(fixture["metadata_or_payload_network_calls"], 0)
        self.assertEqual(fixture["registered_s20_path_stats_or_hash_reads"], 0)
        self.assertEqual(fixture["real_payload_bytes"], 0)
        self.assertEqual(fixture["header_marker_signal_mat_target_reads"], 0)
        self.assertEqual(fixture["cache_split_model_inference_training_scoring_runs"], 0)
        self.assertTrue(fixture["implementation_remote_green_pending"])
        for key, value in execution.items():
            if key.endswith("_commit") or key.endswith("_run_id"):
                self.assertIsNone(value, key)
            elif isinstance(value, bool):
                self.assertFalse(value, key)
            else:
                self.assertEqual(value, 0, key)

    def test_docs_state_order_failure_behavior_and_claim_boundary(self):
        normalized = " ".join(self.doc.split()).lower()
        for phrase in (
            "remote-green implementation gate pending",
            "does not stat a registered s20 root or contact the network",
            "atomically rename the complete bundle",
            "cleanup iterates only over invocation-created temporary files",
            "there is no retry path",
            "scientific claim not established",
            "stop before loop 54",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
