import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/physionet_motor_acquisition_implementation.v0.json"
DOC_PATH = ROOT / "docs/PHYSIONET_MOTOR_ACQUISITION_IMPLEMENTATION.md"
TRACKER_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"
HISTORICAL_SHARED_BINDINGS = {
    "cli_snapshot": "efba51ab2674ed6a1111f15095d328dadc3f20bf7b5804cc6a8d9c0169e55fa2",
    "historical_cml_compatibility_test_snapshot": (
        "680aabfd393658ff520c25ecac3429fab426e2ce2106498085e8a23261ef33c3"
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetMotorAcquisitionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_status_is_fixture_qualified_but_real_execution_is_zero(self):
        self.assertEqual(
            self.registry["status"],
            "implemented_locally_fixture_qualified_remote_green_pending_no_execution",
        )
        execution = self.registry["execution_state"]
        self.assertFalse(execution["registered_execution_consumed"])
        self.assertFalse(execution["bundle_created"])
        for key in (
            "remote_metadata_calls",
            "metadata_network_bytes",
            "edf_payload_requests",
            "edf_payload_network_bytes",
            "local_edf_hash_passes",
        ):
            self.assertEqual(execution[key], 0, key)

    def test_green_authorization_parent_and_locked_hashes_are_exact(self):
        binding = self.registry["authorization_binding"]
        self.assertEqual(binding["authorization_commit"], "00b91edd213112fd186711d06369ae4f836b2243")
        self.assertEqual(binding["authorization_ci_run_id"], 31344104565)
        self.assertEqual(binding["authorization_base_python_job_id"], 93322699209)
        self.assertEqual(binding["authorization_optional_neuro_job_id"], 93322699259)
        self.assertEqual(
            binding["contract_sha256"],
            sha256(ROOT / binding["contract_path"]),
        )
        self.assertEqual(
            binding["authorization_decision_sha256"],
            sha256(ROOT / binding["authorization_decision_path"]),
        )

    def test_owned_sources_are_current_and_shared_snapshots_are_historical(self):
        for name, binding in self.registry["source_bindings"].items():
            if name in HISTORICAL_SHARED_BINDINGS:
                self.assertEqual(binding["sha256"], HISTORICAL_SHARED_BINDINGS[name])
            else:
                self.assertTrue(binding["owned_by_this_implementation"])
                self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]), name)
        cli = (ROOT / self.registry["source_bindings"]["cli_snapshot"]["path"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("_cmd_physionet_motor_acquire", cli)
        self.assertIn('"physionet-motor-acquire"', cli)

    def test_interface_identity_and_resources_are_frozen(self):
        interface = self.registry["frozen_interface"]
        self.assertEqual(interface["default_mode"], "dry_run_no_registered_path_stat_no_network")
        self.assertEqual(interface["base_dependencies_added"], [])
        self.assertFalse(interface["edf_parser_exposed"])
        self.assertFalse(interface["event_sidecar_interface_exposed"])
        identity = self.registry["enforced_identity"]
        self.assertEqual(identity["file_count"], 9)
        self.assertEqual(identity["expected_payload_bytes"], 23_248_224)
        self.assertFalse(identity["substitution_allowed"])
        resources = self.registry["enforced_resources"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["wall_time_seconds"], 300)
        self.assertEqual(resources["peak_rss_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["payload_retries"], 0)
        self.assertEqual(resources["opaque_local_hash_passes_per_edf"], 1)

    def test_fixture_qualification_and_zero_access_boundary_are_explicit(self):
        qualification = self.registry["fixture_qualification"]
        self.assertEqual(qualification["dedicated_executor_tests"], 23)
        self.assertEqual(qualification["combined_work_order_8_tests_before_registry_tests"], 55)
        self.assertEqual(qualification["implementation_registry_tests"], 7)
        self.assertEqual(qualification["complete_suite_prechange_passed_tests"], 1418)
        self.assertEqual(qualification["complete_suite_expected_passed_tests"], 1448)
        for key in (
            "source_metadata_calls",
            "source_metadata_network_bytes",
            "edf_payload_requests",
            "edf_payload_network_bytes",
            "registered_physionet_path_stats_or_opens",
            "edf_header_annotation_signal_or_event_reads",
            "target_label_epoch_or_trial_reads",
            "cache_split_model_inference_training_or_scoring_runs",
            "persistent_generated_experiment_bytes",
        ):
            self.assertEqual(qualification[key], 0, key)

    def test_consumed_cml_evidence_is_preserved_while_current_command_is_checked(self):
        repair = self.registry["compatibility_repair"]
        self.assertFalse(repair["consumed_cml_registry_modified"])
        self.assertFalse(repair["consumed_cml_result_modified"])
        self.assertEqual(
            repair["historical_cml_cli_sha256_preserved"],
            "808fbc930db504e80cc7ecb0117e11115dc039b28505090abe545737b74bfc9e",
        )
        self.assertTrue(repair["current_cml_command_presence_still_tested"])

    def test_document_claim_boundary_and_tracker_preserve_execution_gate(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("10 GB data allowance is unused future headroom", document)
        self.assertIn("23,248,224-byte execution", document)
        tracker = TRACKER_PATH.read_text(encoding="utf-8")
        row = next(line for line in tracker.splitlines() if line.startswith("| 8 |"))
        self.assertTrue(
            "Implementation Qualified Locally" in row or "Complete" in row,
            row,
        )
        if "Complete" in row:
            self.assertIn("Consumed", row)
            self.assertIn("No Rerun", row)
        else:
            self.assertIn("Execution Pending Remote Green", row)


if __name__ == "__main__":
    unittest.main()
