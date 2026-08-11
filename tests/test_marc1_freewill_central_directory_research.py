import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "marc1_freewill_central_directory_research.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1FreewillCentralDirectoryResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_freewill_central_directory_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["research_id"],
            "MARC-1-freewill-central-directory-range-research-v0",
        )
        self.assertEqual(
            self.record["status"],
            "tier_A_transport_and_archive_research_complete_no_live_access",
        )

    def test_artifact_bindings_are_current(self):
        for binding in self.record["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_generated_anchor_is_exact_and_green(self):
        proof = self.record["green_generated_closeout_proof"]
        self.assertEqual(
            proof["commit"], "a5f3ff51583898bcd0de1ce10bd8967fc3d8da92"
        )
        self.assertEqual(proof["CI_run_id"], 31_506_699_956)
        self.assertEqual(proof["base_job_id"], 93_830_009_939)
        self.assertEqual(proof["optional_neuro_job_id"], 93_830_009_975)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_bound_archive_identity_is_exact(self):
        identity = self.record["bound_source_identity"]
        self.assertEqual(identity["record_id"], 28_632_599)
        self.assertEqual(identity["version"], 1)
        self.assertEqual(identity["file_id"], 57_518_986)
        self.assertEqual(identity["archive_bytes"], 13_591_548_048)
        self.assertEqual(identity["archive_md5"], "3b7c3039c5c9fb6abf1429a830301711")
        self.assertFalse(identity["whole_archive_download_eligible"])

    def test_future_request_sequence_is_three_bounded_bodies(self):
        sequence = self.record["prospective_request_sequence"]
        self.assertEqual(sequence["maximum_response_bodies"], 3)
        self.assertEqual(sequence["metadata_body_cap_bytes"], 128 * 1024)
        self.assertEqual(sequence["tail_range_bytes"], 128 * 1024)
        self.assertEqual(sequence["central_directory_cap_bytes"], 16 * 1024 * 1024)
        self.assertEqual(sequence["total_network_body_cap_bytes"], 17_039_360)
        self.assertEqual(sequence["retries"], 0)
        self.assertEqual(sequence["reruns"], 0)

    def test_tail_range_is_exact(self):
        trailer = self.record["zip_trailer_policy"]
        self.assertEqual(trailer["range_start"], 13_591_416_976)
        self.assertEqual(trailer["range_end"], 13_591_548_047)
        self.assertEqual(trailer["range_length"], 131_072)
        self.assertTrue(trailer["EOCD_must_end_at_archive_end"])
        self.assertTrue(trailer["ZIP64_record_must_be_fully_inside_tail"])
        self.assertFalse(trailer["exploratory_ZIP64_request_allowed"])

    def test_http_response_is_self_describing_and_exact(self):
        transport = self.record["transport_policy"]
        self.assertEqual(transport["archive_success_status"], 206)
        self.assertTrue(transport["exact_Content_Range_required"])
        self.assertTrue(transport["exact_Content_Length_required"])
        self.assertTrue(transport["cap_plus_one_read_required"])
        self.assertFalse(transport["HTTP_200_archive_response_allowed"])
        self.assertFalse(transport["multipart_byteranges_allowed"])

    def test_central_directory_is_bounded_before_request(self):
        directory = self.record["central_directory_policy"]
        self.assertEqual(directory["maximum_bytes"], 16 * 1024 * 1024)
        self.assertEqual(directory["maximum_entries"], 250_000)
        self.assertTrue(directory["bounds_proven_before_request"])
        self.assertTrue(directory["single_exact_range_request"])
        self.assertEqual(directory["member_content_reads"], 0)
        self.assertEqual(directory["local_header_reads"], 0)

    def test_member_policy_keeps_names_private(self):
        members = self.record["member_inventory_policy"]
        self.assertTrue(members["safe_POSIX_relative_NFC_paths_required"])
        self.assertTrue(members["unique_normalized_names_required"])
        self.assertEqual(set(members["allowed_kinds"]), {"regular_file", "directory"})
        self.assertFalse(members["symlinks_or_special_files_allowed"])
        self.assertFalse(members["encrypted_entries_allowed"])
        self.assertFalse(members["public_member_names_or_offsets_allowed"])

    def test_partial_audit_does_not_claim_full_integrity(self):
        integrity = self.record["integrity_boundary"]
        self.assertEqual(integrity["whole_archive_MD5_state"], "unavailable_not_read")
        self.assertEqual(integrity["member_CRC32_verification_state"], "unavailable_not_read")
        self.assertFalse(integrity["partial_ranges_verify_whole_archive"])

    def test_resources_are_machine_safe(self):
        caps = self.record["resource_caps"]
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(caps["incremental_disk_bytes"], 32 * 1024 * 1024)
        self.assertEqual(caps["required_free_disk_bytes"], 12 * 1024 * 1024 * 1024)

    def test_router_has_one_non_scientific_success(self):
        router = self.record["prospective_router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 7)
        self.assertEqual(router["success_route"], "MARC1CD-R1")
        self.assertFalse(router["success_is_scientific_result"])
        self.assertFalse(router["success_authorizes_member_acquisition"])

    def test_all_current_authority_and_counters_are_zero(self):
        for value in self.record["authorization_flags"].values():
            self.assertFalse(value)
        for value in self.record["access_counters"].values():
            self.assertEqual(value, 0)

    def test_next_step_remains_generated_only(self):
        next_scope = self.record["next_tier_B_scope"]
        self.assertTrue(next_scope["generated_and_mocked_only"])
        self.assertTrue(next_scope["standard_library_only"])
        self.assertFalse(next_scope["live_endpoint_available"])
        self.assertFalse(next_scope["execute_command_available"])


if __name__ == "__main__":
    unittest.main()
