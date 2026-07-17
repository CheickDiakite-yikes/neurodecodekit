import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "registries" / "loop53_authorization_decision.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop53_authorization_request.v0.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "loop53_fresh_eeg_acquisition_contract.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_53_AUTHORIZATION_DECISION.md"


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


class Loop53AuthorizationDecisionTests(unittest.TestCase):
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
            "neurodecodekit.loop53_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["status"],
            "authorized_after_remote_green_no_implementation_or_execution_yet",
        )
        self.assertEqual(
            decision["authorization_parent_commit"],
            "3dcf70c734a9ba88801c5c5279f957fab938b1a9",
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

    def test_exact_user_sentence_matches_request_and_human_decision(self):
        user = self.decision["user_authorization"]
        sentence = user["exact_sentence_verbatim"]
        self.assertEqual(sentence, self.request["authorization"]["exact_authorization_sentence"])
        self.assertEqual(self.doc.count(sentence), 1)
        self.assertTrue(user["matches_request_exact_sentence"])
        self.assertTrue(user["one_registered_acquisition_only"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])
        self.assertTrue(user["research_autonomy_charter_is_not_substitute_authorization"])

    def test_contract_and_request_remain_immutable_pending_snapshots(self):
        contract_flags = authorization_flags(self.contract)
        self.assertEqual(contract_flags[0], ("research_and_contract_preparation_authorized_now", True))
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
            "pinned_metadata_reverification_authorized_now",
            "one_bounded_acquisition_invocation_authorized_now",
            "four_named_file_download_authorized_now",
            "opaque_size_and_integrity_hashing_authorized_now",
            "isolated_complete_bundle_creation_authorized_now",
            "invocation_created_temporary_cleanup_authorized_now",
            "bounded_manifest_and_receipt_authorized_now",
        }
        flags = dict(authorization_flags(self.decision["authorization"]))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 22)

    def test_registered_identity_files_and_bytes_match_contract(self):
        run = self.decision["registered_execution"]
        contract = self.contract
        self.assertEqual(run["repository"], contract["source_repository"]["repo_id"])
        self.assertEqual(run["revision"], contract["source_repository"]["revision"])
        self.assertEqual(run["license_id"], contract["source_repository"]["license_id"])
        self.assertEqual(run["file_count"], 4)
        self.assertEqual(run["final_payload_bytes"], 96090264)
        self.assertEqual(
            run["selected_files"],
            [
                {"path": row["repository_path"], "size_bytes": row["size_bytes"]}
                for row in contract["selected_files"]
            ],
        )
        self.assertEqual(run["payload_root"], contract["storage_and_output"]["payload_root"])
        self.assertEqual(run["payload_download_invocations"], 1)
        self.assertEqual(run["header_marker_signal_mat_target_reads"], 0)
        self.assertEqual(run["cache_split_model_training_scoring_runs"], 0)
        self.assertEqual(run["reruns"], 0)

    def test_order_requires_two_green_milestones_before_network_or_payload(self):
        order = self.decision["required_execution_order"]
        authorization_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_authorization_record"
        )
        implementation = order.index(
            "implement_and_fixture_test_without_metadata_or_payload_network_access"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_implementation"
        )
        metadata = order.index("reverify_pinned_public_metadata_only")
        download = order.index("execute_one_bounded_four_file_acquisition")
        stop = order.index("mark_consumed_or_parked_and_stop_before_loop54")
        self.assertLess(authorization_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, metadata)
        self.assertLess(metadata, download)
        self.assertLess(download, stop)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(rules["implementation_may_begin_before_authorization_commit_is_green"])
        self.assertFalse(
            rules[
                "metadata_or_payload_network_access_may_occur_during_implementation_or_fixture_tests"
            ]
        )
        self.assertFalse(rules["local_S20_path_may_be_statted_before_implementation_commit_is_green"])
        self.assertFalse(rules["payload_content_may_be_parsed_or_interpreted"])
        self.assertFalse(rules["registered_acquisition_may_run_more_than_once"])

    def test_resource_caps_match_frozen_contract(self):
        resources = self.decision["resource_boundary"]
        storage = self.contract["storage_and_output"]
        caps = self.contract["resource_caps"]
        self.assertEqual(resources["cpu_threads"], caps["cpu_threads"])
        self.assertEqual(resources["workers"], caps["workers"])
        self.assertEqual(resources["wall_time_seconds"], caps["wall_time_seconds"])
        self.assertEqual(resources["peak_rss_bytes"], caps["peak_rss_bytes"])
        self.assertEqual(
            resources["maximum_network_payload_bytes"],
            storage["maximum_network_payload_bytes"],
        )
        self.assertEqual(
            resources["maximum_incremental_disk_bytes"],
            storage["maximum_incremental_disk_bytes_including_temporary_files"],
        )
        self.assertEqual(
            resources["minimum_free_disk_bytes_before_execution"],
            storage["minimum_free_disk_bytes_before_execution"],
        )
        self.assertEqual(resources["expected_final_payload_bytes"], 96090264)

    def test_authorization_only_measurements_are_zero(self):
        for key, value in self.decision["authorization_only_measurements"].items():
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_ceiling_is_acquisition_mechanics_only(self):
        claim = self.decision["claim_boundary"]
        self.assertIn("four-file public S20 bundle", claim["maximum_after_clean_acquisition"])
        unavailable = claim["scientific_claim_not_established"]
        for term in (
            "BrainVision readability",
            "EEG signal quality",
            "neural advantage",
            "decoding accuracy",
            "real-time latency",
            "at-home",
            "clinical",
        ):
            self.assertIn(term, unavailable)
        normalized_doc = " ".join(self.doc.split()).lower()
        self.assertIn("no implementation, download, or payload access", normalized_doc)
        self.assertIn("stop before loop 54", normalized_doc)


if __name__ == "__main__":
    unittest.main()
