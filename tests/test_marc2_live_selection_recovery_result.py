import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc2_live_selection_recovery_failure_result.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key, nested
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


class Marc2LiveSelectionRecoveryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_route_and_consumed_status_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_live_selection_recovery_failure_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-FW1C")
        self.assertEqual(self.result["route"], "MARC2FWC-F02")
        self.assertEqual(
            self.result["status"],
            "consumed_strict_live_source_identity_failure_no_selection_or_rerun",
        )

    def test_green_implementation_proof_is_exact(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"],
            "7b924bee1f10217bccf911ccb4e380485226d50c",
        )
        self.assertEqual(proof["CI_run_id"], 31_930_051_249)
        self.assertEqual(proof["base_python_job_id"], 95_123_374_369)
        self.assertEqual(proof["optional_neuro_job_id"], 95_123_374_211)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])
        self.assertEqual(
            proof["native_registry_sha256"],
            "dcd95616ad65b1b44b13f3116e6a63ea77d958705f4e9bcfad12d8b74a841edc",
        )
        self.assertEqual(
            proof["proof_certificate_sha256"],
            "06668731cdb507373053bce5fe652366591f7fb83a7a0bd48f4fcd82f2610e82",
        )

    def test_aggregate_report_identity_is_bound_without_committing_output(self):
        report = self.result["aggregate_report_identity"]
        self.assertEqual(report["bytes"], 6_540)
        self.assertEqual(
            report["sha256"],
            "f3c9d1d8a10de32975824422a809f8d408e0924f65916bf3b92ed513e29af8fc",
        )
        self.assertFalse(report["report_committed"])
        self.assertFalse(report["private_output_committed"])

    def test_tracked_bindings_are_current_and_non_self(self):
        seen = set()
        for binding in self.result["tracked_file_hashes"]:
            relative = binding["path"]
            with self.subTest(path=relative):
                self.assertNotIn(relative, seen)
                seen.add(relative)
                self.assertNotEqual(relative, RESULT_PATH.relative_to(ROOT).as_posix())
                self.assertEqual(sha256_file(ROOT / relative), binding["sha256"])

    def test_failure_occurs_after_one_exact_read_and_before_selection(self):
        stage = self.result["failure_boundary"]
        self.assertEqual(stage["stage"], "target_free_prefix_selection")
        self.assertEqual(stage["safe_reason"], "live source identity differs")
        self.assertTrue(stage["size_hash_and_strict_JSON_passed_by_stage_order"])
        self.assertFalse(stage["differing_private_field_or_value_retained"])
        self.assertEqual(stage["selected_participants"], 0)
        self.assertEqual(stage["selected_members"], 0)

    def test_exact_private_access_counters_are_bounded(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["private_manifest_content_opens"], 1)
        self.assertEqual(counters["private_manifest_body_reads"], 1)
        self.assertEqual(counters["private_manifest_bytes"], 418_755)
        self.assertEqual(counters["private_manifest_hashes"], 1)
        self.assertEqual(counters["private_manifest_parses"], 1)
        self.assertEqual(counters["consumed_markers"], 1)
        self.assertEqual(counters["aggregate_reports"], 1)
        self.assertEqual(counters["private_selection_manifests"], 0)
        self.assertEqual(counters["real_participant_selections"], 0)
        self.assertEqual(counters["real_member_selections"], 0)

    def test_every_forbidden_operation_counter_is_zero(self):
        counters = self.result["access_counters"]
        forbidden = (
            "network_requests",
            "network_bytes",
            "archive_local_header_or_member_payload_reads",
            "signal_sample_reads",
            "event_target_label_quality_onset_or_channel_reads",
            "real_derivative_rows",
            "training_or_parameter_update_fits",
            "model_inference_or_prediction_sets",
            "prediction_freezes_target_deliveries_or_scores",
            "provider_or_language_model_calls",
            "hardware_operations",
            "old_consumed_root_operations",
            "retries_reruns_or_resumes",
            "scientific_claim_upgrades",
        )
        self.assertTrue(all(counters[key] == 0 for key in forbidden))

    def test_resource_measurements_are_exact_and_within_caps(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_bytes"], 418_755)
        self.assertEqual(measured["combined_output_bytes"], 6_944)
        self.assertEqual(measured["peak_RSS_bytes"], 25_280_512)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["combined_output_bytes"], 2 * 1024**2)
        self.assertGreaterEqual(measured["free_disk_bytes"], 15 * 1024**3)
        self.assertLessEqual(measured["load_per_logical_CPU"], 1.0)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_all_ninety_generated_refusals_remain_bound(self):
        mutations = self.result["generated_qualification_proof"]
        self.assertEqual(mutations["proof_record_passed"], 32)
        self.assertEqual(mutations["selector_passed"], 40)
        self.assertEqual(mutations["wrapper_passed"], 18)
        self.assertEqual(mutations["total_passed"], 90)

    def test_result_publishes_no_private_row_or_member_detail(self):
        forbidden_keys = {
            "crc32",
            "local_header_offset",
            "member_name",
            "private_path",
            "private_rows",
            "raw_body",
            "source_body",
            "source_path",
        }
        for key, value in walk(self.result):
            self.assertNotIn(key.lower(), forbidden_keys)
            if isinstance(value, str):
                self.assertNotIn(".codex_work", value)
                self.assertNotIn("_eeg.", value)
                self.assertNotIn("_events.tsv", value)

    def test_authority_is_closed_and_no_retry_is_available(self):
        self.assertTrue(all(not value for value in self.result["authorization_state"].values()))
        state = self.result["execution_state"]
        self.assertTrue(state["registered_execution_consumed"])
        self.assertEqual(state["retry_rerun_resume_limit"], 0)
        self.assertFalse(state["selection_result_available"])
        self.assertFalse(state["MARC2_FW2_eligible"])

    def test_claim_boundary_stays_engineering_only(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("failed closed", boundary["engineering_capability_added"])
        scientific = boundary["scientific_claim_not_established"].lower()
        self.assertIn("no neural payload", scientific)
        self.assertIn("thought-to-text", scientific)


if __name__ == "__main__":
    unittest.main()
