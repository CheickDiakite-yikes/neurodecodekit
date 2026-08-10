import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    REPO_ROOT
    / "registries"
    / "physionet_motor_acquisition_authorization_decision.v0.json"
)
REQUEST_PATH = (
    REPO_ROOT
    / "registries"
    / "physionet_motor_acquisition_authorization_request.v0.json"
)
CONTRACT_PATH = REPO_ROOT / "registries" / "physionet_motor_acquisition_contract.v0.json"
PACKET_PATH = REPO_ROOT / "docs" / "PHYSIONET_MOTOR_ACQUISITION_AUTHORIZATION_PACKET.md"
DOC_PATH = REPO_ROOT / "docs" / "PHYSIONET_MOTOR_ACQUISITION_AUTHORIZATION_DECISION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


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


class PhysioNetMotorAcquisitionAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_hash_bindings_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.physionet_motor_acquisition_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["status"],
            "authorized_after_remote_green_no_implementation_or_execution_yet",
        )
        self.assertEqual(
            decision["authorization_parent_commit"],
            "f6eb577fdd8c168a4af229248dc56960e3ba75d8",
        )
        self.assertTrue(
            decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"
            ]
        )
        self.assertEqual(decision["authorized_contract"]["sha256"], sha256(CONTRACT_PATH))
        self.assertEqual(
            decision["authorized_contract"]["git_blob_sha1"],
            git_blob_sha1(CONTRACT_PATH),
        )
        self.assertEqual(decision["authorization_request"]["sha256"], sha256(REQUEST_PATH))
        self.assertEqual(
            decision["authorization_request"]["git_blob_sha1"],
            git_blob_sha1(REQUEST_PATH),
        )
        self.assertEqual(decision["authorization_packet"]["sha256"], sha256(PACKET_PATH))

    def test_green_request_commit_and_both_jobs_are_exact(self):
        green = self.decision["green_request"]
        self.assertEqual(green["commit"], "f6eb577fdd8c168a4af229248dc56960e3ba75d8")
        self.assertEqual(green["push_ci_run_id"], 31302161647)
        self.assertEqual(green["push_ci_conclusion"], "success")
        self.assertEqual(green["base_python_job_id"], 93216583586)
        self.assertEqual(green["base_python_job_conclusion"], "success")
        self.assertEqual(green["optional_neuro_job_id"], 93216583625)
        self.assertEqual(green["optional_neuro_job_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])

    def test_exact_user_sentence_matches_request_and_human_decision(self):
        user = self.decision["user_authorization"]
        sentence = user["exact_sentence_verbatim"]
        self.assertEqual(sentence, self.request["authorization"]["exact_authorization_sentence"])
        self.assertEqual(self.doc.count(sentence), 1)
        self.assertTrue(user["matches_request_exact_sentence"])
        self.assertTrue(user["one_registered_acquisition_only"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_contract_and_request_remain_immutable_pending_snapshots(self):
        contract_flags = authorization_flags(self.contract)
        self.assertEqual(
            contract_flags[0],
            ("research_and_contract_preparation_authorized_now", True),
        )
        self.assertTrue(all(value is False for _, value in contract_flags[1:]))
        request_flags = authorization_flags(self.request)
        self.assertTrue(request_flags)
        self.assertTrue(all(value is False for _, value in request_flags))
        self.assertEqual(self.contract["status"], "preregistered_authorization_pending")
        self.assertEqual(self.request["status"], "awaiting_exact_user_authorization")
        self.assertTrue(
            self.decision["authorized_contract"]["remains_immutable_preregistration_snapshot"]
        )
        self.assertTrue(
            self.decision["authorization_request"][
                "remains_immutable_and_unauthorized_snapshot"
            ]
        )

    def test_only_exact_acquisition_surfaces_are_authorized(self):
        expected_true = {
            "acquisition_implementation_authorized_now",
            "generated_fixture_and_mock_qualification_authorized_now",
            "registered_source_metadata_reverification_authorized_now",
            "one_bounded_acquisition_invocation_authorized_now",
            "nine_named_edf_download_authorized_now",
            "opaque_size_and_sha256_hashing_authorized_now",
            "isolated_complete_bundle_creation_authorized_now",
            "invocation_created_temporary_cleanup_authorized_now",
            "bounded_manifest_and_receipt_authorized_now",
        }
        flags = dict(authorization_flags(self.decision["authorization"]))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 25)

    def test_registered_identity_files_and_bytes_match_contract(self):
        run = self.decision["registered_execution"]
        contract = self.contract
        self.assertEqual(run["provider"], contract["source_dataset"]["provider"])
        self.assertEqual(run["dataset_id"], contract["source_dataset"]["dataset_id"])
        self.assertEqual(run["dataset_version"], contract["source_dataset"]["version"])
        self.assertEqual(run["doi"], contract["source_dataset"]["doi"])
        self.assertEqual(run["license_id"], contract["source_dataset"]["license_id"])
        self.assertEqual(run["file_count"], 9)
        self.assertEqual(run["final_payload_bytes"], 23248224)
        self.assertEqual(
            run["selected_files"],
            [
                {
                    "path": row["repository_relative_path"],
                    "size_bytes": row["size_bytes"],
                    "official_sha256": row["official_sha256"],
                }
                for row in contract["selected_files"]
            ],
        )
        self.assertEqual(run["payload_root"], contract["storage_and_output"]["payload_root"])
        self.assertEqual(run["acquisition_invocations"], 1)
        self.assertEqual(run["payload_retries"], 0)
        self.assertEqual(run["edf_parse_event_sidecar_signal_target_reads"], 0)
        self.assertEqual(run["reruns"], 0)

    def test_order_requires_two_green_milestones_before_network_or_payload(self):
        order = self.decision["required_execution_order"]
        authorization_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_authorization_record"
        )
        implementation = order.index(
            "implement_and_fixture_test_without_source_metadata_or_edf_payload_network_access"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_implementation"
        )
        metadata = order.index("reverify_only_registered_official_source_metadata")
        download = order.index("execute_one_no_retry_nine_file_acquisition")
        stop = order.index(
            "mark_consumed_or_parked_and_stop_before_edf_parse_or_work_order_9"
        )
        self.assertLess(authorization_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, metadata)
        self.assertLess(metadata, download)
        self.assertLess(download, stop)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(rules["implementation_may_begin_before_authorization_commit_is_green"])
        self.assertFalse(
            rules[
                "source_metadata_or_edf_payload_network_access_may_occur_during_implementation_or_fixture_tests"
            ]
        )
        self.assertFalse(
            rules["local_physionet_path_may_be_statted_before_implementation_commit_is_green"]
        )
        self.assertFalse(rules["edf_payload_content_may_be_parsed_or_interpreted"])
        self.assertFalse(rules["event_sidecar_may_be_downloaded_or_read"])
        self.assertFalse(rules["registered_acquisition_may_run_more_than_once"])

    def test_resource_caps_match_frozen_contract(self):
        resources = self.decision["resource_boundary"]
        storage = self.contract["storage_and_output"]
        caps = self.contract["resource_caps"]
        self.assertEqual(resources["cpu_threads"], caps["cpu_threads"])
        self.assertEqual(resources["workers"], caps["workers"])
        self.assertEqual(
            resources["concurrent_numerical_jobs"],
            caps["concurrent_numerical_jobs"],
        )
        self.assertEqual(resources["wall_time_seconds"], caps["wall_time_seconds"])
        self.assertEqual(resources["peak_rss_bytes"], caps["peak_rss_bytes"])
        self.assertEqual(
            resources["maximum_metadata_network_bytes"],
            storage["maximum_metadata_network_bytes"],
        )
        self.assertEqual(
            resources["maximum_edf_payload_network_bytes"],
            storage["maximum_edf_payload_network_bytes"],
        )
        self.assertEqual(
            resources["maximum_incremental_disk_bytes"],
            storage["maximum_incremental_disk_bytes_including_temporary_files"],
        )
        self.assertEqual(resources["expected_final_payload_bytes"], 23248224)

    def test_authorization_only_measurements_preserve_zero_source_and_payload_access(self):
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["github_ci_verification_calls"], 1)
        for key, value in measurements.items():
            if key == "github_ci_verification_calls":
                continue
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_ceiling_is_acquisition_mechanics_only(self):
        claim = self.decision["claim_boundary"]
        self.assertIn(
            "nine-file public EEGMMIDB bundle",
            claim["maximum_after_clean_acquisition"],
        )
        unavailable = claim["scientific_claim_not_established"]
        for term in (
            "EDF readability",
            "signal quality",
            "motor effect",
            "neural advantage",
            "model accuracy",
            "real-time latency",
            "clinical",
        ):
            self.assertIn(term, unavailable)
        normalized_doc = " ".join(self.doc.split()).lower()
        self.assertIn("no implementation, source metadata recheck, download", normalized_doc)
        self.assertIn("stop before edf parsing or work order 9", normalized_doc)


if __name__ == "__main__":
    unittest.main()
