import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop53_fresh_eeg_acquisition_contract.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop53_authorization_request.v0.json"
PACKET_PATH = REPO_ROOT / "docs" / "LOOP_53_AUTHORIZATION_PACKET.md"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_53_PRIMARY_SOURCE_RESEARCH.md"
PREREG_PATH = REPO_ROOT / "docs" / "LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md"
INVARIANT_TEST_PATH = REPO_ROOT / "tests" / "test_loop53_fresh_eeg_acquisition_contract.py"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop53AuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_all_execution_authorization_is_false(self):
        request = self.request
        self.assertEqual(request["schema_name"], "neurodecodekit.loop53_authorization_request")
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["loop_id"], 53)
        self.assertEqual(request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        flags = authorization_flags(request)
        self.assertEqual(len(flags), 16)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_green_registration_commit_and_both_ci_runs_are_bound(self):
        registration = self.request["registration"]
        self.assertEqual(registration["commit"], "bccd36790317b5f58ca62083c6b3019d1983176c")
        self.assertEqual(registration["push_ci_run_id"], 29469813041)
        self.assertEqual(registration["pr_ci_run_id"], 29469829357)
        self.assertEqual(registration["push_ci_conclusion"], "success")
        self.assertEqual(registration["pr_ci_conclusion"], "success")
        self.assertEqual(registration["base_python_tests"], 929)
        self.assertEqual(registration["base_python_expected_skips"], 156)
        self.assertEqual(registration["optional_neuro_tests"], 961)
        self.assertEqual(registration["optional_neuro_expected_skips"], 29)
        self.assertEqual(registration["local_complete_tests"], 976)
        self.assertEqual(registration["local_complete_expected_skips"], 3)

    def test_registration_artifact_hashes_are_exact(self):
        target = self.request["target"]
        for prefix, path in (
            ("contract", CONTRACT_PATH),
            ("research", RESEARCH_PATH),
            ("preregistration", PREREG_PATH),
            ("invariant_test", INVARIANT_TEST_PATH),
        ):
            with self.subTest(path=path.name):
                self.assertEqual(target[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(target[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))
        self.assertEqual(target["contract_schema_version"], "0.1.0")
        self.assertTrue(target["registration_snapshot_must_remain_immutable"])

    def test_exact_sentence_appears_once_and_is_not_received(self):
        authorization = self.request["authorization"]
        sentence = authorization["exact_authorization_sentence"]
        self.assertEqual(self.packet.count(sentence), 1)
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertFalse(authorization["storage_allowance_is_execution_authorization"])
        self.assertFalse(authorization["general_tier_a_b_autonomy_is_tier_c_authorization"])
        self.assertFalse(authorization["historical_S20_packet_is_current_authorization"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])

    def test_requested_files_and_caps_match_contract_exactly(self):
        request = self.request
        files = request["requested_scope"]["selected_files"]
        contract_files = self.contract["selected_files"]
        self.assertEqual(files, contract_files)
        self.assertEqual(sum(row["size_bytes"] for row in files), 96090264)
        caps = request["resource_caps"]
        contract_caps = self.contract["resource_caps"]
        storage = self.contract["storage_and_output"]
        self.assertEqual(caps["cpu_threads"], contract_caps["cpu_threads"])
        self.assertEqual(caps["workers"], contract_caps["workers"])
        self.assertEqual(caps["wall_time_seconds"], contract_caps["wall_time_seconds"])
        self.assertEqual(caps["peak_rss_bytes"], contract_caps["peak_rss_bytes"])
        self.assertEqual(
            caps["maximum_network_payload_bytes"], storage["maximum_network_payload_bytes"]
        )
        self.assertEqual(
            caps["maximum_incremental_disk_bytes"],
            storage["maximum_incremental_disk_bytes_including_temporary_files"],
        )
        self.assertEqual(caps["maximum_receipt_bytes"], 1024 * 1024)

    def test_requested_operations_do_not_expand_acquisition_only_contract(self):
        scope = self.request["requested_scope"]
        self.assertEqual(scope["payload_download_invocations"], 1)
        self.assertEqual(scope["final_payload_bytes"], 96090264)
        for key in (
            "header_or_marker_parse_runs",
            "signal_reads",
            "mat_or_target_reads",
            "cache_or_split_runs",
            "model_or_checkpoint_loads",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "scoring_runs",
            "device_or_hardware_operations",
        ):
            self.assertEqual(scope[key], 0, key)

    def test_sequence_requires_two_green_milestones_before_one_execution(self):
        sequence = self.request["required_sequence_after_authorization"]
        authorization_green = sequence.index("commit_push_and_obtain_green_ci_for_decision")
        implementation = sequence.index("implement_and_fixture_test_without_payload_access")
        implementation_green = sequence.index(
            "commit_push_and_obtain_green_ci_for_implementation"
        )
        execution = sequence.index("execute_registered_acquisition_once")
        stop = sequence.index("stop_before_loop54")
        self.assertLess(authorization_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, execution)
        self.assertLess(execution, stop)

    def test_current_protected_and_experiment_counters_are_zero(self):
        counters = self.request["current_access_counters"]
        self.assertEqual(counters["public_metadata_api_operations"], 4)
        for key, value in counters.items():
            if key != "public_metadata_api_operations":
                self.assertEqual(value, 0, key)

    def test_packet_discloses_scope_resources_and_nonclaims(self):
        for phrase in (
            "96,090,264",
            "512 MiB",
            "128 MiB",
            "256 MiB",
            "at least 2 GiB",
            "may not inspect",
            "no EEG signal quality",
            "Every execution authorization remains false",
        ):
            self.assertIn(phrase, self.packet)


if __name__ == "__main__":
    unittest.main()
