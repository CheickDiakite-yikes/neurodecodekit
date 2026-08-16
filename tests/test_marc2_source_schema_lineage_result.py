import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_source_schema_lineage_result.v0.json"


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


class Marc2SourceSchemaLineageResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_route_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_source_schema_lineage_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-SL1")
        self.assertEqual(self.result["route"], "MARC2SL-R2")

    def test_upstream_consumed_result_was_remotely_green(self):
        proof = self.result["upstream_consumed_result_proof"]
        self.assertEqual(
            proof["commit"],
            "512b84b17893762bb60275b29e9d5da875c8a4e0",
        )
        self.assertEqual(proof["CI_run_id"], 31_930_686_034)
        self.assertEqual(proof["base_python_job_id"], 95_124_886_816)
        self.assertEqual(proof["optional_neuro_job_id"], 95_124_886_768)
        self.assertTrue(proof["both_required_jobs_green_before_lineage_closeout"])

    def test_contract_and_tracked_hashes_are_current(self):
        contract = self.result["contract"]
        self.assertEqual(sha256_file(ROOT / contract["path"]), contract["sha256"])
        for binding in self.result["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertNotEqual(binding["path"], RESULT_PATH.relative_to(ROOT).as_posix())
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )

    def test_producer_and_consumer_key_sets_are_exact(self):
        value = self.result["lineage"]
        self.assertEqual(
            value["producer_public_transport_keys"],
            ["directory", "metadata", "tail"],
        )
        expected_consumer = ["central_directory", "metadata", "tail"]
        self.assertEqual(value["selector_fixture_transport_keys"], expected_consumer)
        self.assertEqual(value["selector_validator_transport_keys"], expected_consumer)
        self.assertEqual(value["recovery_validator_transport_keys"], expected_consumer)

    def test_single_alias_mismatch_is_sufficient_for_F02(self):
        value = self.result["lineage"]
        self.assertEqual(value["shared_transport_keys"], ["metadata", "tail"])
        self.assertEqual(value["producer_only_transport_keys"], ["directory"])
        self.assertEqual(
            value["consumer_only_transport_keys"], ["central_directory"]
        )
        self.assertTrue(value["exact_single_alias_mismatch"])
        self.assertTrue(value["sufficient_to_explain_observed_structural_refusal"])
        self.assertFalse(value["actual_private_field_or_value_observed"])

    def test_root_cause_is_engineering_not_data_or_science(self):
        root_cause = self.result["root_cause"]
        self.assertEqual(root_cause["producer_key"], "directory")
        self.assertEqual(root_cause["consumer_key"], "central_directory")
        self.assertFalse(root_cause["data_or_scientific_failure"])
        self.assertFalse(self.result["lineage"]["private_source_malformed_inferred"])

    def test_adapter_design_validates_before_one_way_alias(self):
        design = self.result["prospective_adapter_design"]
        self.assertTrue(design["validation_before_adaptation_required"])
        self.assertEqual(
            design["single_allowed_alias"],
            {"source_key": "directory", "selector_key": "central_directory"},
        )
        self.assertTrue(design["transport_hash_values_must_be_preserved_byte_for_byte"])
        self.assertFalse(design["consumed_executor_patch_or_reuse_allowed"])

    def test_measurements_are_exact_and_within_caps(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_artifact_count"], 10)
        self.assertEqual(measured["input_bytes"], 310_015)
        self.assertEqual(measured["Python_AST_parses"], 3)
        self.assertEqual(measured["strict_JSON_parses"], 7)
        self.assertLess(measured["runtime_seconds"], 10)
        self.assertLess(measured["peak_RSS_bytes"], 128 * 1024**2)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["CPU_threads"], 1)

    def test_every_forbidden_operation_counter_is_zero(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["committed_public_artifact_reads"], 10)
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key != "committed_public_artifact_reads")
        )

    def test_result_contains_no_private_path_or_payload_detail(self):
        forbidden_keys = {
            "crc32",
            "decoded_text",
            "labels",
            "member_name",
            "predictions",
            "private_path",
            "signal",
            "target",
            "targets",
        }
        for key, value in walk(self.result):
            self.assertNotIn(key.lower(), forbidden_keys)
            if isinstance(value, str):
                self.assertNotIn(".codex_work", value)
                self.assertNotIn("_eeg.", value)

    def test_disposition_keeps_live_and_FW2_closed(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["artifact_only_diagnosis_complete"])
        self.assertTrue(disposition["MARC2_FW1C_consumed"])
        self.assertFalse(
            disposition["consumed_executor_may_be_modified_reused_retried_or_resumed"]
        )
        self.assertFalse(disposition["private_source_or_output_reinspection_allowed"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])

    def test_claim_boundary_stays_engineering_only(self):
        claim = self.result["claim_boundary"]
        self.assertIn("transport-key alias mismatch", claim["engineering_capability_added"])
        scientific = claim["scientific_claim_not_established"].lower()
        self.assertIn("no neural payload", scientific)
        self.assertIn("thought-to-text", scientific)


if __name__ == "__main__":
    unittest.main()
