import json
import re
import unittest
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "physionet_motor_acquisition_contract.v0.json"
PREREG_PATH = REPO_ROOT / "docs" / "PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md"
STRATEGY_PATH = REPO_ROOT / "docs" / "OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md"


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


class PhysioNetMotorAcquisitionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.prereg = PREREG_PATH.read_text(encoding="utf-8")
        cls.strategy = STRATEGY_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_claim_ceiling(self):
        contract = self.contract
        self.assertEqual(
            contract["schema_name"],
            "neurodecodekit.physionet_motor_acquisition_contract",
        )
        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["work_order"], 8)
        self.assertEqual(contract["status"], "preregistered_authorization_pending")
        self.assertEqual(contract["claim_target"], "public_eeg_acquisition_mechanics_only")
        self.assertIn("only", contract["scientific_claim_ceiling"].lower())
        self.assertIn("nine exact public EDF bytestrings", contract["scientific_claim_ceiling"])

    def test_only_research_preparation_is_currently_authorized(self):
        flags = authorization_flags(self.contract)
        self.assertEqual(len(flags), 16)
        self.assertEqual(
            flags[0],
            ("research_and_contract_preparation_authorized_now", True),
        )
        self.assertTrue(all(value is False for _, value in flags[1:]), flags)
        self.assertTrue(
            self.contract["authorization"]["separate_exact_tier_c_authorization_required"]
        )

    def test_source_version_doi_license_and_identity_rules_are_exact(self):
        source = self.contract["source_dataset"]
        self.assertEqual(source["provider"], "PhysioNet")
        self.assertEqual(source["dataset_id"], "eegmmidb")
        self.assertEqual(source["version"], "1.0.0")
        self.assertEqual(source["doi"], "10.13026/C28G6P")
        self.assertEqual(source["license_id"], "ODC-By-1.0")
        self.assertEqual(source["license_label"], "Open Data Commons Attribution License v1.0")
        self.assertTrue(source["public_at_registration"])
        self.assertEqual(
            source["hard_identity_fields"],
            [
                "dataset_version",
                "repository_relative_path",
                "size_bytes",
                "official_sha256",
            ],
        )
        self.assertEqual(
            source["informational_http_fields"],
            ["etag", "last_modified", "content_type"],
        )
        self.assertFalse(source["metadata_response_bytes_measured"])
        self.assertTrue(source["metadata_response_bytes_unavailable_reason"])

    def test_exact_nine_files_have_frozen_sizes_and_official_hashes(self):
        files = self.contract["selected_files"]
        self.assertEqual(len(files), 9)
        self.assertEqual(sum(row["size_bytes"] for row in files), 23248224)
        self.assertEqual(
            [row["repository_relative_path"] for row in files],
            [
                "S001/S001R03.edf",
                "S001/S001R07.edf",
                "S001/S001R11.edf",
                "S002/S002R03.edf",
                "S002/S002R07.edf",
                "S002/S002R11.edf",
                "S003/S003R03.edf",
                "S003/S003R07.edf",
                "S003/S003R11.edf",
            ],
        )
        self.assertEqual(
            [row["size_bytes"] for row in files],
            [
                2596896,
                2596896,
                2596896,
                2555616,
                2555616,
                2555616,
                2596896,
                2596896,
                2596896,
            ],
        )
        self.assertEqual(
            [row["official_sha256"] for row in files],
            [
                "3427c8d01bff1380bc9ab9f27a35ece2af5dfadf3e291bbc05eb66e4dadbfe2e",
                "6320a941815eb7a0bc632e32c07c88b6e2281a0e2f177e8f49e2d0a16231145c",
                "d5296b9232b0ad88b7022155cbcde618df44d4b0db046ce3bec54f8f8644207a",
                "cbabe29620b19978454bc429f59976f6ee8f32f6392e4fcdf7e463981248072c",
                "cdba64ad60574903248aed651d393c148df3c611eebdc9694717a04e2e2deef3",
                "694bd9fbee1305dbc212ea4eecb8930750f5e08f8cc8ea45e2b94c92ac5f5a7d",
                "ebf184ea51d9aa3178190583f428db02f184e22412ff300a5f224776d1e8dbb4",
                "d8a610bf60a19c1d653a11633f7df40bd7b3eca976bebf2b525eb65017fdf044",
                "0563c2a26f759d849d6b99b3efb6047d1e1d288f80c0c16f5f07403bd0029271",
            ],
        )
        for row in files:
            self.assertRegex(row["official_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                row["download_url"],
                self.contract["source_dataset"]["file_root_url"]
                + row["repository_relative_path"],
            )
            self.assertEqual(row["destination_relative_path"], row["repository_relative_path"])
            self.assertFalse(row["content_parse_allowed"])

    def test_subject_run_roles_are_complete_but_do_not_activate_a_split(self):
        cohort = self.contract["prospective_cohort"]
        files = self.contract["selected_files"]
        self.assertEqual(cohort["subjects"], ["S001", "S002", "S003"])
        self.assertEqual(cohort["runs"], ["03", "07", "11"])
        self.assertEqual(cohort["prospective_fit_runs"], ["03", "07"])
        self.assertEqual(cohort["prospective_check_runs"], ["11"])
        self.assertFalse(cohort["split_created_or_activated_by_this_contract"])
        self.assertEqual(
            {(row["subject_id"], row["run_id"]) for row in files},
            {(subject, run) for subject in cohort["subjects"] for run in cohort["runs"]},
        )
        self.assertTrue(
            all(
                row["prospective_future_role"]
                == ("check_candidate" if row["run_id"] == "11" else "fit_candidate")
                for row in files
            )
        )

    def test_selection_refuses_sidecars_wildcards_traversal_and_substitution(self):
        selection = self.contract["selection_constraints"]
        files = self.contract["selected_files"]
        self.assertEqual(selection["file_count"], 9)
        self.assertEqual(selection["allowed_suffixes"], [".edf"])
        self.assertFalse(selection["event_sidecar_files_allowed"])
        self.assertFalse(selection["wildcard_expansion_allowed"])
        self.assertFalse(selection["redirect_to_unregistered_host_allowed"])
        self.assertFalse(selection["additional_manifest_or_document_download_allowed"])
        self.assertFalse(selection["partial_bundle_qualifies"])
        self.assertFalse(selection["substitution_allowed"])
        for row in files:
            path = PurePosixPath(row["repository_relative_path"])
            self.assertEqual(path.suffix, ".edf")
            self.assertNotIn("..", path.parts)
            self.assertFalse(any(token in str(path) for token in "*?[]"))
            self.assertFalse(str(path).endswith(".event"))

    def test_storage_network_and_runtime_caps_are_tiny_and_exact(self):
        storage = self.contract["storage_and_output"]
        caps = self.contract["resource_caps"]
        self.assertEqual(storage["expected_final_payload_bytes"], 23248224)
        self.assertEqual(storage["maximum_metadata_network_bytes"], 1024 * 1024)
        self.assertEqual(storage["maximum_edf_payload_network_bytes"], 32 * 1024 * 1024)
        self.assertEqual(
            storage["maximum_incremental_disk_bytes_including_temporary_files"],
            64 * 1024 * 1024,
        )
        self.assertEqual(storage["minimum_free_disk_bytes_before_execution"], 2 * 1024**3)
        self.assertEqual(storage["maximum_generated_receipt_bytes_combined"], 1024 * 1024)
        self.assertTrue(storage["destination_must_not_exist_before_execution"])
        self.assertTrue(storage["temporary_root_must_not_exist_before_execution"])
        self.assertTrue(storage["receipt_root_must_not_exist_before_execution"])
        self.assertFalse(storage["overwrite_existing_path"])
        self.assertFalse(storage["delete_preexisting_path"])
        self.assertFalse(storage["rename_preexisting_path"])
        self.assertFalse(storage["follow_symlinks"])
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["concurrent_numerical_jobs"], 1)
        self.assertEqual(caps["wall_time_seconds"], 300)
        self.assertEqual(caps["peak_rss_bytes"], 256 * 1024 * 1024)
        self.assertEqual(caps["acquisition_invocations"], 1)
        self.assertEqual(caps["http_payload_retries"], 0)
        self.assertEqual(caps["opaque_local_sha256_passes_per_edf"], 1)

    def test_access_order_verifies_metadata_before_payload_and_stops_before_parse(self):
        sequence = self.contract["registered_access_order"]
        metadata = sequence.index(
            "reverify_version_doi_license_public_availability_nine_paths_sizes_and_official_sha256_entries_via_metadata_only_requests"
        )
        abort_gate = sequence.index("abort_before_any_edf_body_request_on_any_metadata_mismatch")
        download = sequence.index(
            "perform_one_bounded_acquisition_invocation_for_exactly_nine_registered_edf_paths_into_the_isolated_temporary_root"
        )
        hash_check = sequence.index(
            "opaquely_stream_each_local_edf_exactly_once_for_size_and_sha256_without_decode_or_parse"
        )
        receipt = sequence.index("emit_one_bounded_machine_manifest_and_one_human_receipt")
        stop = sequence.index(
            "stop_before_edf_parse_event_extraction_split_creation_model_work_or_work_order_9"
        )
        self.assertLess(metadata, abort_gate)
        self.assertLess(abort_gate, download)
        self.assertLess(download, hash_check)
        self.assertLess(hash_check, receipt)
        self.assertLess(receipt, stop)

    def test_payload_interpretation_models_other_data_and_reruns_are_forbidden(self):
        forbidden = set(self.contract["forbidden_operations"])
        expected = {
            "open_decode_or_parse_any_edf_header",
            "open_decode_or_parse_any_edf_annotation_or_event_channel",
            "download_or_read_any_event_sidecar",
            "read_signal_samples_as_signal",
            "create_epochs_windows_features_caches_splits_or_derivative_arrays",
            "import_mne_or_another_edf_reader_in_the_acquisition_executor",
            "load_or_access_any_model_checkpoint_or_baseline",
            "model_inference",
            "training_or_parameter_update",
            "scoring_selection_or_threshold_update",
            "read_S20_SpanishBCBL_S7_S21_S24_S25_or_another_real_dataset",
            "download_additional_participants_runs_files_companions_or_substitutes",
            "retry_or_second_invocation_after_any_acquisition_receipt_exists",
            "scientific_or_decoding_claim_promotion",
        }
        self.assertTrue(expected.issubset(forbidden), expected - forbidden)

    def test_receipt_requires_resources_counters_warnings_and_unavailable_fields(self):
        receipt = self.contract["receipt_contract"]
        required = set(receipt["required_fields"])
        self.assertTrue(
            {
                "runtime_seconds",
                "peak_rss_bytes",
                "metadata_network_bytes",
                "edf_payload_network_bytes",
                "incremental_disk_peak_bytes",
                "forbidden_access_and_operation_counters",
                "warnings",
                "unavailable_fields",
                "claim_boundary",
            }.issubset(required)
        )
        unavailable = set(receipt["required_unavailable_fields"])
        self.assertTrue(
            {
                "observed_channel_count",
                "observed_sampling_rate_hz",
                "observed_event_count",
                "observed_trial_count",
                "observed_signal_quality",
                "model_accuracy",
                "no_signal_comparison",
                "neural_advantage",
                "cross_person_generalization",
                "end_to_end_latency",
            }.issubset(unavailable)
        )

    def test_registration_counters_show_metadata_only_and_zero_edf_body_access(self):
        counters = self.contract["current_access_counters"]
        expected_nonzero = {
            "official_dataset_page_reads": 1,
            "official_checksum_manifest_reads": 1,
            "official_task_mapping_document_reads": 1,
            "http_head_requests": 10,
        }
        for key, value in counters.items():
            if key in expected_nonzero:
                self.assertEqual(value, expected_nonzero[key], key)
            else:
                self.assertEqual(value, 0, key)
        self.assertEqual(self.contract["source_dataset"]["registration_http_head_body_bytes"], 0)
        self.assertEqual(self.contract["source_dataset"]["registration_edf_payload_bytes"], 0)

    def test_docs_disclose_exact_scope_pending_decision_and_nonclaims(self):
        combined = self.prereg + self.strategy
        for phrase in (
            "23,248,224",
            "33,554,432",
            "67,108,864",
            "2,147,483,648",
            "exact Tier C authorization pending",
            "No EDF payload byte",
            "cannot prove EDF readability",
        ):
            self.assertIn(phrase.lower(), combined.lower())
        self.assertIn("No PhysioNet file was downloaded or opened", self.strategy)
        self.assertNotRegex(self.prereg, re.compile(r"scientific result (?:was|is) established", re.I))


if __name__ == "__main__":
    unittest.main()
