from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries"
    / "communication_eeg_source_identity_metadata_authorization_request.v0.json"
)
DOCUMENT = (
    ROOT / "docs" / "COMMUNICATION_EEG_SOURCE_IDENTITY_METADATA_AUTHORIZATION_PACKET.md"
)


class CommunicationEEGSourceIdentityMetadataAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_green_generated_proof_closeout_is_exact(self) -> None:
        green = self.request["green_generated_proof_closeout"]
        self.assertEqual(green["commit"], "4acd82bcc460f3e7a7668ec3c1c6a49c8d964aca")
        self.assertEqual(green["CI_run_id"], 33039371687)
        self.assertEqual(green["base_python_job_id"], 98409242950)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98409242802)
        self.assertTrue(green["both_required_jobs_green"])

    def test_bound_artifacts_are_exact_and_canonical(self) -> None:
        rows = self.request["bound_pre_request_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(row["bytes"], len(payload))
            self.assertEqual(row["sha256"], hashlib.sha256(payload).hexdigest())
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(row["git_blob"], blob)
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.request["bound_pre_request_artifact_summary"]
        self.assertEqual(summary["count"], 20)
        self.assertEqual(summary["bytes"], 156361)
        self.assertEqual(
            summary["canonical_artifact_set_sha256"],
            hashlib.sha256(canonical).hexdigest(),
        )

    def test_exact_query_is_one_metadata_request_only(self) -> None:
        request = self.request["exact_request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["endpoint"], "https://openneuro.org/crn/graphql")
        self.assertEqual(request["dataset_accession"], "ds003626")
        self.assertEqual(request["snapshot_tag"], "2.1.2")
        self.assertEqual(request["canonical_request_body_bytes"], 361)
        self.assertEqual(
            request["canonical_request_body_sha256"],
            "db465645cdea29b3fdca3fd70e742b15a1dc3732d8f8900775b595871ab68a20",
        )
        self.assertEqual(request["requests_exact"], 1)
        self.assertEqual(request["redirects"], 0)
        self.assertEqual(request["retries"], 0)
        self.assertEqual(request["reruns"], 0)

    def test_ordered_stages_require_green_barriers(self) -> None:
        stages = self.request["requested_ordered_stages"]
        self.assertEqual([stage["stage"] for stage in stages], [
            "M1_generated_live_wrapper_implementation_and_qualification",
            "M2_activation",
            "M3_one_metadata_invocation",
        ])
        self.assertEqual(stages[0]["real_requests"], 0)
        self.assertTrue(stages[0]["requires_green_packet_bound_decision"])
        self.assertTrue(stages[0]["decision_artifact_hash_bound"])
        self.assertEqual(stages[1]["real_requests"], 0)
        self.assertTrue(stages[1]["requires_same_green_decision_artifact"])
        self.assertTrue(stages[1]["decision_artifact_hash_bound"])
        self.assertEqual(stages[2]["metadata_requests"], 1)
        self.assertTrue(stages[2]["requires_same_green_decision_artifact"])
        self.assertTrue(stages[2]["decision_artifact_hash_bound"])
        self.assertEqual(stages[2]["payload_requests"], 0)
        self.assertTrue(stages[2]["consumes_on_success_or_failure"])

    def test_active_dreyer_gate_is_not_displaced(self) -> None:
        sequence = self.request["active_gate_sequencing"]
        self.assertEqual(sequence["current_sole_active_Tier_C_packet"], "DREYER-C5R-1-HL")
        self.assertFalse(sequence["this_packet_active_now"])
        self.assertFalse(sequence["may_displace_current_active_packet"])
        self.assertFalse(sequence["may_receive_a_decision_while_another_packet_is_active"])
        self.assertTrue(sequence["requires_current_gate_closed_or_parked_before_activation"])
        self.assertTrue(sequence["decision_required_before_M1"])
        self.assertTrue(sequence["same_green_decision_must_be_hash_bound_by_M1_M2_and_M3"])

    def test_resource_caps_are_metadata_only_and_small(self) -> None:
        caps = self.request["resource_caps"]
        self.assertEqual(
            [caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]],
            [1, 1, 0],
        )
        self.assertEqual(caps["metadata_response_body_bytes_maximum"], 16 << 20)
        self.assertEqual(caps["payload_requests"], 0)
        self.assertEqual(caps["payload_network_bytes"], 0)
        self.assertEqual(caps["incremental_disk_bytes_maximum"], 8 << 20)
        self.assertEqual(caps["minimum_free_disk_bytes"], 10 << 30)
        self.assertEqual(caps["reruns"], 0)

    def test_paths_and_router_are_frozen_before_implementation(self) -> None:
        publication = self.request["transport_and_publication_contract"]
        self.assertEqual(
            publication["invocation_root"],
            "data/communication_eeg/ds003626-v2.1.2/comm-l0-meta",
        )
        self.assertEqual(
            publication["consumed_marker_name"],
            "comm-l0-meta-consumed.v0.json",
        )
        self.assertEqual(
            publication["private_manifest_name"],
            "selected-source-manifest.v0.json",
        )
        self.assertEqual(
            publication["public_result_path"],
            "registries/communication_eeg_source_identity_metadata_result.v0.json",
        )
        self.assertEqual(publication["private_temporary_name_prefix"], ".tmp-")
        self.assertEqual(
            publication["public_result_temporary_path_pattern"],
            "registries/.communication_eeg_source_identity_metadata_result.v0.json.tmp-<invocation_nonce>",
        )
        self.assertIn("O_EXCL", publication["public_result_temporary_create"])
        self.assertIn("O_NOFOLLOW", publication["public_result_temporary_create"])
        self.assertEqual(publication["public_result_temporary_mode"], "0600")
        self.assertTrue(
            publication["public_result_temporary_source_descriptor_inode_verified_before_link"]
        )
        self.assertTrue(
            publication[
                "private_paths_must_remain_beneath_invocation_root_without_symlink_or_replacement"
            ]
        )
        router = self.request["router"]
        self.assertEqual(router["success"], "COMM-L0-META-R1")
        self.assertEqual(len(router["ordered_failures"]), 7)
        self.assertTrue(router["every_route_consumes_invocation"])
        self.assertFalse(router["partial_response_manifest_or_result_is_success"])

        self.assertEqual(publication["consumed_marker_mode"], "0600")
        self.assertIn("O_EXCL", publication["consumed_marker_create"])
        self.assertTrue(publication["consumed_marker_file_and_parent_directories_fsynced"])
        self.assertTrue(publication["preexisting_consumed_marker_refuses_before_opener_construction"])
        self.assertTrue(publication["consumed_marker_permanently_retained_on_every_outcome"])
        self.assertFalse(publication["cleanup_may_modify_or_remove_consumed_marker"])
        self.assertEqual(publication["socket_timeout_seconds"], 60)
        self.assertEqual(publication["monotonic_real_operation_deadline_seconds"], 240)
        self.assertEqual(publication["termination_cleanup_and_receipt_headroom_seconds"], 60)
        self.assertEqual(publication["monotonic_total_process_tree_watchdog_seconds"], 300)
        self.assertEqual(publication["read_limit_bytes"], (16 << 20) + 1)
        self.assertEqual(
            publication["combined_retained_manifest_and_public_result_bytes_maximum"],
            2 << 20,
        )
        self.assertEqual(publication["atomic_staging_bytes_maximum"], 4 << 20)
        self.assertTrue(publication["public_result_required_after_every_post_marker_route"])
        self.assertTrue(publication["public_result_preexisting_path_refuses_before_marker"])
        self.assertTrue(publication["public_result_parent_verified_beneath_repository_without_symlink"])
        self.assertEqual(
            publication["public_result_publish"],
            "descriptor_relative_os_link_same_parent_temp_to_final_fails_on_EEXIST_then_unlink_temp_and_fsync_parent",
        )
        self.assertTrue(publication["public_result_file_and_parent_directory_fsynced"])
        self.assertTrue(
            publication[
                "public_result_failure_receipt_includes_route_warning_unavailable_fields_and_counters"
            ]
        )
        self.assertFalse(publication["public_result_cleanup_may_modify_or_remove"])
        self.assertEqual(
            publication["cleanup_scope"],
            "invocation_owned_private_temporary_files_and_exact_public_result_temporary_inode_only",
        )
        race = publication["public_result_destination_race_qualification"]
        self.assertTrue(all(race.values()))

    def test_request_authorizes_and_executes_nothing(self) -> None:
        self.assertTrue(all(value is False for value in self.request["authority_now"].values()))
        counters = self.request["request_operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 20)
        self.assertEqual(counters["Git_proof_reads"], 20)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_claim_boundary_and_document_are_plain(self) -> None:
        boundary = self.request["claim_boundary"]
        self.assertTrue(
            all(value is False for key, value in boundary.items() if key != "maximum_future_result")
        )
        text = DOCUMENT.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in (
            "Status: **All authority false; queued request only**",
            "no EEG payload",
            "may not displace `DREYER-C5R-1-HL`",
            "Engineering capability proposed:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
