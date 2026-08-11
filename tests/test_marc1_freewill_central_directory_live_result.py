import hashlib
import json
import re
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc1_central_directory_live as live


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries" / "marc1_freewill_central_directory_live_result.v0.json"
)
RESULT_SHA256 = "fee969818b4e3e2ef7aee86096ad676c9bd70f80d19f2fd6dbe0e8069175257b"
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")


class MARC1CentralDirectoryLiveResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_committed_result_hash_and_identity_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(RESULT_PATH.read_bytes()).hexdigest(), RESULT_SHA256)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc1_central_directory_live_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC1-CD1A")
        self.assertEqual(self.result["status"], "passed_live_archive_central_directory_inventory")
        self.assertEqual(self.result["route"], "MARC1CD-R1")

    def test_exact_green_wrapper_proof_preceded_execution(self) -> None:
        proof = self.result["green_evidence"]
        self.assertEqual(
            proof["wrapper_commit"],
            "5dfa3c4c8cd7f0e990b7b1db7b35c4df8694171f",
        )
        self.assertEqual(proof["wrapper_CI_run_id"], 31521510374)
        self.assertEqual(proof["wrapper_base_job_id"], 93879378282)
        self.assertEqual(proof["wrapper_optional_neuro_job_id"], 93879378362)
        self.assertEqual(
            proof["implementation_registry_sha256"],
            "b0e2c0fe20a20b142fa53c387ffd4fe467aff9898ecd1ab1eadc3a441f8405b0",
        )
        self.assertTrue(proof["both_decision_jobs_green"])
        self.assertTrue(proof["both_wrapper_jobs_green"])

    def test_source_identity_did_not_become_a_whole_download(self) -> None:
        source = self.result["source"]
        self.assertEqual(source["provider"], "Figshare")
        self.assertEqual((source["record_id"], source["version"]), (28_632_599, 1))
        self.assertEqual(source["file_id"], 57_518_986)
        self.assertEqual(source["declared_archive_bytes"], 13_591_548_048)
        self.assertEqual(source["registered_MD5"], "3b7c3039c5c9fb6abf1429a830301711")
        self.assertFalse(source["whole_archive_downloaded"])
        self.assertFalse(source["member_payload_opened"])

    def test_transport_used_only_three_bounded_bodies(self) -> None:
        transport = self.result["transport_summary"]
        counters = self.result["access_counters"]
        self.assertEqual(transport["HTTP_request_attempts"], 4)
        self.assertEqual(transport["accepted_response_bodies"], 3)
        self.assertEqual(transport["accepted_response_body_bytes"], 306_758)
        self.assertLessEqual(transport["accepted_response_body_bytes"], 17_039_360)
        self.assertEqual(transport["network_redirects"], 1)
        self.assertEqual(counters["public_metadata_body_bytes"], 304)
        self.assertEqual(counters["public_archive_tail_body_bytes"], 131_072)
        self.assertEqual(counters["public_central_directory_body_bytes"], 175_382)
        self.assertEqual(
            counters["public_metadata_body_bytes"]
            + counters["public_archive_tail_body_bytes"]
            + counters["public_central_directory_body_bytes"],
            transport["accepted_response_body_bytes"],
        )
        self.assertEqual(counters["DNS_queries"], 1)
        self.assertFalse(transport["raw_headers_published"])
        self.assertFalse(transport["raw_bodies_persisted"])
        self.assertFalse(transport["terminal_URL_published"])

    def test_archive_inventory_aggregate_is_exact(self) -> None:
        archive = self.result["archive_summary"]
        self.assertEqual(archive["virtual_archive_bytes"], 13_591_548_048)
        self.assertEqual(archive["central_directory_bytes"], 175_382)
        self.assertEqual(archive["archive_comment_bytes"], 0)
        self.assertEqual(archive["entry_count"], 1_227)
        self.assertEqual(archive["regular_file_entries"], 1_025)
        self.assertEqual(archive["directory_entries"], 202)
        self.assertEqual(archive["method_counts"], {"0": 202, "8": 1025})
        self.assertEqual(archive["ZIP64_member_entries"], 796)
        self.assertEqual(archive["total_compressed_member_bytes"], 13_591_200_154)
        self.assertEqual(archive["total_uncompressed_member_bytes"], 17_362_624_734)
        self.assertEqual(archive["whole_archive_materialized_bytes"], 0)
        self.assertFalse(archive["whole_archive_MD5_verified"])
        self.assertFalse(archive["member_CRC_verified"])
        self.assertFalse(archive["local_headers_verified"])
        self.assertFalse(archive["member_payload_integrity_verified"])

    def test_inventory_and_response_hashes_are_aggregate_and_well_formed(self) -> None:
        archive = self.result["archive_summary"]
        self.assertIsNotNone(HEX64_RE.fullmatch(archive["inventory_sha256"]))
        self.assertEqual(
            archive["private_manifest_sha256"],
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        )
        hashes = self.result["transport_summary"]["response_body_sha256"]
        self.assertEqual(set(hashes), {"metadata", "tail", "directory"})
        self.assertTrue(all(HEX64_RE.fullmatch(value) for value in hashes.values()))

    def test_resources_and_output_are_below_caps(self) -> None:
        measurements = self.result["measurements"]
        self.assertLess(measurements["runtime_seconds"], 120)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(measurements["combined_output_bytes"], 424_873)
        self.assertEqual(measurements["incremental_disk_bytes"], 425_323)
        self.assertLess(measurements["incremental_disk_bytes"], 32 * 1024 * 1024)
        self.assertEqual(
            (
                measurements["CPU_threads"],
                measurements["workers"],
                measurements["numerical_jobs"],
            ),
            (1, 1, 1),
        )
        machine = measurements["machine_gate"]
        self.assertTrue(machine["passed_before_consumed_marker"])
        self.assertGreaterEqual(machine["free_disk_bytes"], 12 * 1024**3)
        self.assertLessEqual(machine["one_minute_load_per_logical_CPU"], 1.0)

    def test_every_acceptance_gate_passed(self) -> None:
        self.assertEqual(len(self.result["acceptance_gates"]), 14)
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_all_forbidden_access_counters_remained_zero(self) -> None:
        counters = self.result["access_counters"]
        forbidden = (
            "whole_archive_downloads",
            "member_local_header_requests",
            "member_payload_requests",
            "member_payload_bytes",
            "local_archive_path_operations",
            "participant_or_cohort_selections",
            "participant_acquisitions",
            "signal_sample_reads",
            "channel_geometry_event_or_onset_reads",
            "target_label_response_sentence_key_or_trial_reads",
            "derivative_cache_split_or_feature_operations",
            "training_or_parameter_update_runs",
            "model_inference_runs",
            "prediction_sets",
            "prediction_freezes",
            "target_deliveries",
            "scoring_events",
            "dependency_installs",
            "provider_or_language_model_calls",
            "stream_device_or_hardware_operations",
            "temporary_cleanup_operations",
            "retries_or_reruns",
            "post_result_updates",
            "release_operations",
            "scientific_claim_upgrades",
        )
        for key in forbidden:
            with self.subTest(key=key):
                self.assertEqual(counters[key], 0)

    def test_public_result_contains_no_private_member_or_URL_field(self) -> None:
        live.validate_public_result(self.result)
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("member_name", serialized)
        self.assertNotIn("local_header_offset", serialized)
        self.assertNotIn("https://", serialized)
        self.assertNotIn("/files/", serialized)

    def test_result_document_binds_outputs_and_two_claim_sentences(self) -> None:
        document = (
            ROOT / "docs" / "MARC_1_FREEWILL_CENTRAL_DIRECTORY_LIVE_RESULT.md"
        ).read_text(encoding="utf-8")
        for value in (
            RESULT_SHA256,
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
            "421cec0380b23d87d78aadf97adea20625af39e874b15d39cadd844b672087c1",
        ):
            self.assertIn(value, document)
        self.assertIn("consumed with no", document)
        self.assertIn("retry or rerun", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
