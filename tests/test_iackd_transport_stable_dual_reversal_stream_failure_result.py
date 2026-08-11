import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries"
    / "iackd_transport_stable_dual_reversal_stream_failure_result.v0.json"
)


class IACKD2RStreamFailureResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_schema_route_and_consumption_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.iackd_transport_stable_dual_reversal_stream_failure_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["route"], "IACKD2R-F05")
        self.assertTrue(self.result["invocation"]["consumed"])
        self.assertFalse(self.result["invocation"]["retry_allowed"])
        self.assertFalse(self.result["invocation"]["rerun_allowed"])
        self.assertEqual(
            self.result["invocation"]["consumed_marker_SHA256"],
            "48523eebdbb9cb73d71341fb3691a5e2cde93a7a8300fc7f562a491749783d94",
        )

    def test_green_implementation_proof_and_registry_hash_are_exact(self):
        implementation = self.result["immutable_evidence"][
            "exact_additive_implementation"
        ]
        self.assertEqual(
            implementation["commit"],
            "b32dc25e94efc15bcb4288db9bb5a4c0d4172ed5",
        )
        self.assertEqual(implementation["push_CI_run_id"], 31478167292)
        self.assertEqual(implementation["base_python_job_id"], 93736708777)
        self.assertEqual(implementation["optional_neuro_job_id"], 93736708868)
        self.assertTrue(implementation["both_required_jobs_green"])
        registry = (
            ROOT
            / "registries"
            / "iackd_transport_stable_dual_reversal_real_implementation.v0.json"
        )
        self.assertEqual(
            hashlib.sha256(registry.read_bytes()).hexdigest(),
            implementation["implementation_registry_sha256"],
        )

    def test_failure_is_after_byte_identity_and_before_semantic_parse(self):
        failure = self.result["failure_localization"]
        self.assertEqual(
            failure["nested_transport_refusal_id"],
            "IACKDT-F07-body-SHA256-mismatch",
        )
        self.assertTrue(failure["exact_registered_observed_body_bytes_passed"])
        self.assertEqual(failure["registered_body_bytes"], 1178)
        self.assertEqual(failure["observed_body_bytes"], 1178)
        self.assertEqual(failure["SHA256_computations"], 1)
        self.assertEqual(failure["SHA256_matches"], 0)
        self.assertEqual(failure["semantic_parse_calls"], 0)
        self.assertFalse(failure["raw_body_persisted"])
        self.assertFalse(failure["observed_SHA256_retained"])

    def test_no_payload_model_target_or_score_was_reached(self):
        counters = self.result["access_counters"]
        expected_zero = {
            "public_payload_response_opens",
            "old_executor_calls",
            "old_invocation_root_operations",
            "old_retained_bundle_operations",
            "local_IACKD_payload_operations",
            "VHDR_or_VMRK_reads",
            "EEG_or_EOG_header_reads",
            "channel_or_geometry_reads",
            "marker_or_event_reads",
            "signal_sample_reads",
            "ball_or_Leap_trajectory_reads",
            "target_or_label_reads",
            "derivative_writes",
            "training_or_parameter_update_fits",
            "model_inference_calls",
            "prediction_sets",
            "prediction_freezes",
            "final_target_deliveries",
            "scoring_events",
            "post_target_updates",
            "retries",
            "reruns",
            "scientific_claim_upgrades",
        }
        self.assertTrue(all(counters[name] == 0 for name in expected_zero))
        self.assertEqual(counters["preconsumption_machine_safety_checks"], 1)
        self.assertEqual(counters["public_metadata_response_opens"], 1)
        self.assertEqual(counters["public_metadata_body_reads"], 1)

    def test_downstream_sequence_is_unreachable(self):
        state = self.result["execution_state"]
        self.assertTrue(state["public_stream_consumed"])
        self.assertFalse(state["complete_derivatives_exist"])
        self.assertFalse(state["target_blind_analysis_reachable"])
        self.assertFalse(state["prediction_freeze_reachable"])
        self.assertFalse(state["final_target_delivery_reachable"])
        self.assertFalse(state["score_reachable"])
        self.assertFalse(state["retry_or_rerun_available"])

    def test_public_record_is_aggregate_and_claim_bounded(self):
        rendered = json.dumps(self.result, sort_keys=True)
        self.assertNotIn("/Users/", rendered)
        self.assertNotIn("/private/", rendered)
        self.assertNotIn("observed_body_payload", rendered)
        self.assertIn(
            "no neural effect",
            self.result["claim_boundary"]["scientific_claim_not_established"],
        )


if __name__ == "__main__":
    unittest.main()
