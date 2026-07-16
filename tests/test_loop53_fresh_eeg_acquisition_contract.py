import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop53_fresh_eeg_acquisition_contract.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_53_PRIMARY_SOURCE_RESEARCH.md"
PREREG_PATH = REPO_ROOT / "docs" / "LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md"


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


class Loop53FreshEEGAcquisitionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.prereg = PREREG_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_claim_ceiling(self):
        contract = self.contract
        self.assertEqual(
            contract["schema_name"],
            "neurodecodekit.loop53_fresh_eeg_acquisition_contract",
        )
        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["loop_id"], 53)
        self.assertEqual(contract["status"], "preregistered_authorization_pending")
        self.assertEqual(contract["claim_target"], "fresh_eeg_acquisition_mechanics_only")
        self.assertIn("only", contract["scientific_claim_ceiling"])

    def test_only_research_preparation_is_currently_authorized(self):
        flags = authorization_flags(self.contract)
        self.assertEqual(len(flags), 15)
        self.assertEqual(flags[0], ("research_and_contract_preparation_authorized_now", True))
        self.assertTrue(all(value is False for _, value in flags[1:]), flags)
        self.assertTrue(
            self.contract["authorization"]["separate_exact_tier_c_authorization_required"]
        )

    def test_source_revision_license_and_cohort_are_exact(self):
        source = self.contract["source_repository"]
        cohort = self.contract["cohort_identity"]
        self.assertEqual(source["repo_id"], "bcbl190626/SpanishBCBL")
        self.assertEqual(source["revision"], "88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684")
        self.assertEqual(source["license_id"], "cc-by-nc-4.0")
        self.assertTrue(source["public_at_registration"])
        self.assertFalse(source["gated_at_registration"])
        self.assertFalse(source["disabled_at_registration"])
        self.assertEqual(
            (cohort["modality"], cohort["subject_id"], cohort["session_id"], cohort["block_id"]),
            ("EEG", "S20", "2", "2"),
        )
        self.assertEqual(cohort["substitution_subjects_allowed"], [])
        self.assertTrue(cohort["S7_is_consumed_and_forbidden"])

    def test_four_exact_files_have_frozen_source_identities(self):
        files = self.contract["selected_files"]
        self.assertEqual(len(files), 4)
        self.assertEqual(sum(row["size_bytes"] for row in files), 96090264)
        self.assertEqual(
            [row["repository_path"] for row in files],
            [
                "EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr",
                "EEG/EEG/020_DECOMEG_S2_11966_task2.eeg",
                "EEG/EEG/020_DECOMEG_S2_11966_task2.vmrk",
                "EEG/logs/S20_session2_block2_list1.mat",
            ],
        )
        self.assertEqual(
            [row["size_bytes"] for row in files],
            [11705, 95782400, 91219, 204940],
        )
        self.assertEqual(
            [row["repository_oid"] for row in files],
            [
                "9ab325a0f8523b675ecab1c97e16169143f1f341",
                "d0513ea226a0b3735794ca9b41844dc22e4a4e52",
                "a06044503e415872a3c8a9a344e6d9a51d5d2a34",
                "c3f11dd336611db2e42a1f01c277079c226f29d1",
            ],
        )
        self.assertEqual(
            [row["lfs_sha256"] for row in files if row["lfs_sha256"]],
            [
                "57664457ca2f2f47e6eed5d942beda68536812e607e735a7118ce4f91a623d65",
                "bdc6b8fa123b041b45f277f9cffb33d64bb3fd557d0facf0e969db5a222c0414",
            ],
        )
        self.assertTrue(all(row["content_parse_allowed"] is False for row in files))

    def test_storage_and_runtime_caps_are_bounded(self):
        storage = self.contract["storage_and_output"]
        caps = self.contract["resource_caps"]
        self.assertEqual(storage["payload_root"], "data/loop53_s20_eeg/SpanishBCBL")
        self.assertTrue(storage["destination_must_not_exist_before_execution"])
        self.assertFalse(storage["overwrite_existing_path"])
        self.assertFalse(storage["delete_preexisting_path"])
        self.assertFalse(storage["follow_symlinks"])
        self.assertEqual(storage["expected_final_payload_bytes"], 96090264)
        self.assertLessEqual(storage["maximum_network_payload_bytes"], 128 * 1024 * 1024)
        self.assertLessEqual(
            storage["maximum_incremental_disk_bytes_including_temporary_files"],
            256 * 1024 * 1024,
        )
        self.assertEqual(storage["maximum_generated_receipt_bytes"], 1024 * 1024)
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["download_invocations"], 1)
        self.assertLessEqual(caps["wall_time_seconds"], 600)
        self.assertLessEqual(caps["peak_rss_bytes"], 512 * 1024 * 1024)

    def test_access_order_verifies_metadata_before_payload_and_stops_after_receipt(self):
        sequence = self.contract["registered_access_order"]
        metadata = sequence.index(
            "reverify_pinned_revision_license_availability_file_paths_sizes_and_source_oids_via_metadata_only_calls"
        )
        download = sequence.index("download_exactly_four_named_files_into_the_isolated_temporary_root")
        hash_check = sequence.index(
            "verify_exact_sizes_and_opaque_source_identity_hashes_without_parsing_payloads"
        )
        receipt = sequence.index("emit_bounded_manifest_receipt_and_access_counters")
        stop = sequence.index("perform_no_other_payload_or_model_operation")
        self.assertLess(metadata, download)
        self.assertLess(download, hash_check)
        self.assertLess(hash_check, receipt)
        self.assertLess(receipt, stop)

    def test_target_signal_model_and_other_people_are_forbidden(self):
        forbidden = set(self.contract["forbidden_operations"])
        expected = {
            "read_eeg_samples_as_signal",
            "decode_or_parse_mat",
            "read_targets_labels_sentences_or_key_events",
            "read_S7_S21_S24_S25_or_any_other_participant",
            "create_event_or_sentence_cache",
            "create_or_select_train_validation_test_splits",
            "model_inference",
            "training_or_parameter_update",
            "scoring_or_threshold_selection",
            "download_additional_files",
            "rerun_after_receipt",
        }
        self.assertTrue(expected.issubset(forbidden), expected - forbidden)

    def test_receipt_requires_resources_access_counters_warnings_and_unavailable_fields(self):
        receipt = self.contract["receipt_contract"]
        required = set(receipt["required_fields"])
        self.assertTrue(
            {
                "runtime_seconds",
                "peak_rss_bytes",
                "network_payload_bytes",
                "incremental_disk_peak_bytes",
                "header_marker_signal_mat_target_reads",
                "cache_split_model_training_scoring_runs",
                "warnings",
                "unavailable_fields",
                "claim_boundary",
            }.issubset(required)
        )
        unavailable = set(receipt["required_unavailable_fields"])
        self.assertTrue(
            {
                "channel_count",
                "sampling_rate_hz",
                "target_text",
                "neural_advantage",
                "decoding_accuracy",
                "end_to_end_latency",
            }.issubset(unavailable)
        )

    def test_current_payload_and_experiment_counters_are_zero(self):
        counters = self.contract["current_access_counters"]
        self.assertEqual(counters["public_metadata_api_operations"], 4)
        for key, value in counters.items():
            if key != "public_metadata_api_operations":
                self.assertEqual(value, 0, key)

    def test_docs_disclose_exact_bytes_caps_and_nonclaims(self):
        combined = self.research + self.prereg
        for phrase in (
            "96,090,264",
            "268,435,456",
            "2,147,483,648",
            "authorization pending",
            "acquisition mechanics only",
            "does not prove",
        ):
            self.assertIn(phrase.lower(), combined.lower())
        self.assertIn("S20 path was listed, stated, hashed, or opened", self.research)
        self.assertIn("General research autonomy", self.prereg)


if __name__ == "__main__":
    unittest.main()
