import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries"
    / "iackd_role_aware_dual_reversal_stream_failure_result.v0.json"
)


def canonical_sha256(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class IACKD2StreamFailureResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_schema_route_and_self_hash_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.iackd_role_aware_dual_reversal_stream_failure_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(
            self.result["status"],
            "consumed_parked_metadata_Content_Length_mismatch_no_retry",
        )
        self.assertEqual(
            self.result["route"],
            "IACKD2-F08-payload_size_ETag_SHA_or_run_group_cap_failure",
        )
        unhashed = dict(self.result)
        observed = unhashed.pop("record_sha256")
        self.assertEqual(observed, canonical_sha256(unhashed))

    def test_green_implementation_is_exact(self):
        green = self.result["green_implementation"]
        self.assertEqual(
            green["commit"],
            "dab5dd47ee47f285430311e4fe0f38f457d1118a",
        )
        self.assertEqual(green["push_CI_run_id"], 31461818620)
        self.assertEqual(green["base_python_job_id"], 93686690177)
        self.assertEqual(green["optional_neuro_job_id"], 93686690138)
        self.assertTrue(green["both_required_jobs_green"])

    def test_failure_is_localized_before_body_read(self):
        failure = self.result["failure_localization"]
        self.assertEqual(failure["registered_body_bytes"], 1178)
        self.assertTrue(failure["HTTP_status_gate_passed"])
        self.assertTrue(failure["final_URL_gate_passed"])
        self.assertFalse(failure["Content_Length_exact_1178_gate_passed"])
        self.assertIsNone(failure["observed_Content_Length"])
        self.assertFalse(failure["response_body_read"])
        self.assertFalse(failure["response_body_SHA256_computed"])
        self.assertFalse(failure["metadata_JSON_parsed"])
        self.assertFalse(failure["second_metadata_request_opened"])

    def test_invocation_is_consumed_with_no_retry(self):
        invocation = self.result["registered_invocation"]
        self.assertEqual(invocation["execution_ordinal"], 1)
        self.assertTrue(invocation["consumed_marker_created_before_first_request"])
        self.assertEqual(invocation["consumed_marker_bytes"], 267)
        self.assertFalse(invocation["retry_allowed"])
        self.assertFalse(invocation["rerun_allowed"])
        state = self.result["downstream_state"]
        self.assertTrue(state["IACKD2_consumed"])
        self.assertFalse(state["IACKD2_rerun_available"])

    def test_artifacts_and_downstream_operations_are_zero(self):
        artifacts = self.result["artifact_inventory"]
        for name in (
            "temporary_payload_files",
            "model_derivative_files",
            "sealed_target_derivative_files",
            "physiology_derivative_files",
            "private_prediction_files",
            "public_acquisition_receipts",
            "public_prediction_freezes",
            "public_scientific_results",
        ):
            self.assertEqual(artifacts[name], 0)
        self.assertFalse(
            ROOT.joinpath(
                "registries",
                "iackd_role_aware_dual_reversal_acquisition_receipt.v0.json",
            ).exists()
        )

    def test_all_protected_model_target_and_claim_counters_are_zero(self):
        counters = self.result["access_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()))
        measurements = self.result["measurements"]
        self.assertEqual(measurements["public_metadata_response_opens"], 1)
        self.assertEqual(measurements["metadata_body_bytes_read"], 0)
        self.assertEqual(measurements["selected_payload_requests"], 0)
        self.assertEqual(measurements["selected_payload_bytes_read"], 0)

    def test_unavailable_values_are_explicit_and_not_guessed(self):
        measurements = self.result["measurements"]
        for name in (
            "runtime_seconds",
            "peak_RSS_bytes",
            "network_wire_bytes",
            "response_header_wire_bytes",
            "producer_is_causal_in_samples",
        ):
            self.assertIsNone(measurements[name])
        self.assertIn(
            "observed_Content_Length",
            self.result["unavailable_fields"],
        )

    def test_public_record_has_no_local_or_individual_material(self):
        rendered = json.dumps(self.result, sort_keys=True)
        for token in (
            "/Users/",
            "/private/",
            "individual_prediction",
            "participant_outcome",
            "actual_action_values",
            "cue_surrogate_values",
        ):
            self.assertNotIn(token, rendered)

    def test_document_states_engineering_and_scientific_boundaries(self):
        document = (
            ROOT
            / "docs"
            / "IACKD_ROLE_AWARE_DUAL_REVERSAL_STREAM_RESULT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no retry", document.lower())
        self.assertIn("HTTP transport header", document)
        claim = self.result["claim_boundary"]
        self.assertIn("real public endpoint", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
