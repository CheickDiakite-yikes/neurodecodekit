import hashlib
import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    REPO_ROOT
    / "registries"
    / "physionet_motor_acquisition_authorization_request.v0.json"
)
CONTRACT_PATH = REPO_ROOT / "registries" / "physionet_motor_acquisition_contract.v0.json"
PREREG_PATH = REPO_ROOT / "docs" / "PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md"
CONTRACT_TEST_PATH = REPO_ROOT / "tests" / "test_physionet_motor_acquisition_contract.py"
PACKET_PATH = REPO_ROOT / "docs" / "PHYSIONET_MOTOR_ACQUISITION_AUTHORIZATION_PACKET.md"
REQUEST_TEST_PATH = Path(__file__).resolve()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path):
    return subprocess.run(
        ["git", "hash-object", str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "authorized_now" or key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class PhysioNetMotorAcquisitionAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_request_identity_and_decision_are_pending(self):
        request = self.request
        self.assertEqual(
            request["schema_name"],
            "neurodecodekit.physionet_motor_acquisition_authorization_request",
        )
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["work_order"], 8)
        self.assertEqual(request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        self.assertIsNone(request["authorization_record_commit"])

    def test_registration_commit_and_both_ci_jobs_are_exact_and_green(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "2a7b4188553e221133d788a081b838dbbb9f41bb",
        )
        self.assertEqual(registration["push_ci_run_id"], 31301730612)
        self.assertEqual(registration["push_ci_conclusion"], "success")
        self.assertEqual(registration["base_python_job_id"], 93215490492)
        self.assertEqual(registration["base_python_job_conclusion"], "success")
        self.assertEqual(registration["optional_neuro_job_id"], 93215490501)
        self.assertEqual(registration["optional_neuro_job_conclusion"], "success")
        self.assertTrue(registration["remote_registration_is_green"])

    def test_registration_and_request_surface_hashes_are_byte_exact(self):
        target = self.request["target"]
        bindings = (
            ("preregistration", PREREG_PATH),
            ("contract", CONTRACT_PATH),
            ("invariant_test", CONTRACT_TEST_PATH),
            ("authorization_packet", PACKET_PATH),
            ("authorization_request_test", REQUEST_TEST_PATH),
        )
        for name, path in bindings:
            self.assertEqual(target[f"{name}_path"], str(path.relative_to(REPO_ROOT)))
            self.assertEqual(target[f"{name}_sha256"], sha256(path), name)
            self.assertEqual(target[f"{name}_git_blob_sha1"], git_blob(path), name)
        self.assertTrue(target["registration_snapshot_must_remain_immutable"])

    def test_exact_sentence_matches_packet_and_preserves_staged_green_order(self):
        sentence = self.request["authorization"]["exact_authorization_sentence"]
        packet_sentences = [line[2:] for line in self.packet.splitlines() if line.startswith("> ")]
        self.assertEqual(packet_sentences, [sentence])
        for phrase in (
            "registration commit 2a7b4188553e221133d788a081b838dbbb9f41bb",
            "green CI run 31301730612",
            "only after a separate authorization-only decision is committed, pushed, and remotely green",
            "only after that exact implementation is committed, pushed, and remotely green",
            "one no-retry acquisition invocation",
            "exactly 23,248,224 bytes",
            "one opaque local size and SHA-256 pass per EDF",
            "one CPU thread",
            "256 MiB peak RSS",
            "32 MiB EDF payload network",
            "work order 9",
        ):
            self.assertIn(phrase, sentence)

    def test_every_current_execution_authorization_is_false(self):
        flags = authorization_flags(self.request)
        self.assertGreaterEqual(len(flags), 18)
        self.assertTrue(all(value is False for _, value in flags), flags)
        authorization = self.request["authorization"]
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertFalse(authorization["general_tier_a_b_autonomy_is_tier_c_authorization"])
        self.assertFalse(authorization["prior_storage_allowance_is_execution_authorization"])
        self.assertFalse(authorization["prior_real_data_permission_is_transitive"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])

    def test_requested_files_are_exactly_the_registered_nine(self):
        requested = self.request["requested_scope"]
        contract_rows = self.contract["selected_files"]
        expected = [
            {
                "repository_relative_path": row["repository_relative_path"],
                "destination_relative_path": row["destination_relative_path"],
                "subject_id": row["subject_id"],
                "run_id": row["run_id"],
                "prospective_future_role": row["prospective_future_role"],
                "size_bytes": row["size_bytes"],
                "official_sha256": row["official_sha256"],
                "content_parse_allowed": False,
            }
            for row in contract_rows
        ]
        self.assertEqual(requested["selected_files"], expected)
        self.assertEqual(requested["file_count"], 9)
        self.assertEqual(requested["final_payload_bytes"], 23248224)
        self.assertEqual(requested["acquisition_invocations"], 1)
        self.assertEqual(requested["payload_retries"], 0)
        self.assertEqual(requested["opaque_hash_passes_per_file"], 1)
        self.assertEqual(requested["edf_parse_runs"], 0)
        self.assertEqual(requested["split_runs"], 0)
        self.assertEqual(requested["model_training_inference_scoring_runs"], 0)

    def test_resource_caps_match_the_frozen_contract(self):
        requested = self.request["resource_caps"]
        contract_caps = self.contract["resource_caps"]
        storage = self.contract["storage_and_output"]
        self.assertEqual(requested["cpu_threads"], contract_caps["cpu_threads"])
        self.assertEqual(requested["workers"], contract_caps["workers"])
        self.assertEqual(
            requested["concurrent_numerical_jobs"],
            contract_caps["concurrent_numerical_jobs"],
        )
        self.assertEqual(requested["wall_time_seconds"], contract_caps["wall_time_seconds"])
        self.assertEqual(requested["peak_rss_bytes"], contract_caps["peak_rss_bytes"])
        self.assertEqual(
            requested["maximum_metadata_network_bytes"],
            storage["maximum_metadata_network_bytes"],
        )
        self.assertEqual(
            requested["maximum_edf_payload_network_bytes"],
            storage["maximum_edf_payload_network_bytes"],
        )
        self.assertEqual(
            requested["maximum_incremental_disk_bytes"],
            storage["maximum_incremental_disk_bytes_including_temporary_files"],
        )
        self.assertEqual(
            requested["minimum_free_disk_bytes"],
            storage["minimum_free_disk_bytes_before_execution"],
        )
        self.assertEqual(
            requested["maximum_receipt_bytes"],
            storage["maximum_generated_receipt_bytes_combined"],
        )
        self.assertEqual(requested["acquisition_invocations"], 1)
        self.assertEqual(requested["payload_retries"], 0)

    def test_required_sequence_stops_before_payload_until_both_green_gates(self):
        sequence = self.request["required_sequence_after_authorization"]
        decision = sequence.index(
            "create_separate_authorization_only_decision_bound_to_registration_hashes"
        )
        green_decision = sequence.index("commit_push_and_obtain_green_ci_for_decision")
        fixture_implementation = sequence.index(
            "implement_and_fixture_test_without_edf_payload_access"
        )
        green_implementation = sequence.index(
            "commit_push_and_obtain_green_ci_for_implementation"
        )
        execution = sequence.index("execute_registered_acquisition_once_without_retry")
        stop = sequence.index("stop_before_edf_parsing_or_work_order_9")
        self.assertLess(decision, green_decision)
        self.assertLess(green_decision, fixture_implementation)
        self.assertLess(fixture_implementation, green_implementation)
        self.assertLess(green_implementation, execution)
        self.assertLess(execution, stop)

    def test_current_counters_match_registration_and_have_zero_edf_body_access(self):
        counters = self.request["current_access_counters"]
        self.assertEqual(counters, self.contract["current_access_counters"])
        for key, value in counters.items():
            if key in {
                "official_dataset_page_reads",
                "official_checksum_manifest_reads",
                "official_task_mapping_document_reads",
                "http_head_requests",
            }:
                continue
            self.assertEqual(value, 0, key)
        self.assertEqual(counters["http_head_requests"], 10)
        self.assertEqual(counters["http_head_body_bytes"], 0)
        self.assertEqual(counters["edf_payload_get_requests"], 0)
        self.assertEqual(counters["edf_payload_network_bytes"], 0)

    def test_claim_ceiling_remains_acquisition_only(self):
        boundary = self.request["claim_boundary"]
        self.assertIn("No implementation", boundary["current"])
        self.assertIn("acquisition mechanics", boundary["maximum_after_clean_acquisition"])
        unavailable = set(boundary["still_unavailable_after_clean_acquisition"])
        self.assertTrue(
            {
                "EDF readability or parser compatibility",
                "motor effect or EEG signal quality",
                "model accuracy or no-signal improvement",
                "neural or brain-specific advantage",
                "typing thought or language decoding",
                "cross-person or unseen-person generalization",
                "real-time or end-to-end latency",
                "portable hardware at-home assistive or clinical performance",
            }.issubset(unavailable)
        )


if __name__ == "__main__":
    unittest.main()
