import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "iackd_transport_stable_recovery_authorization_request.v0.json"
)
PACKET_PATH = (
    ROOT / "docs" / "IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_PACKET.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDTransportStableRecoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_request_is_all_false_and_requires_fresh_user_words(self) -> None:
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        authorization = self.request["authorization"]
        procedural = {
            "separate_authorization_only_record_required",
            "short_form_may_bind_after_request_is_remotely_green",
            "actual_user_words_must_be_quoted",
        }
        self.assertTrue(all(authorization[name] for name in procedural))
        self.assertTrue(
            all(
                value is False
                for name, value in authorization.items()
                if name not in procedural and isinstance(value, bool)
            )
        )
        self.assertFalse(authorization["current_continue_is_retroactive_authorization"])

    def test_green_registration_and_exact_implementation_are_bound(self) -> None:
        registration = self.request["green_transport_registration"]
        self.assertEqual(
            registration["commit"],
            "ee0f62adf74afd390052694142090ccc0395c539",
        )
        self.assertEqual(registration["push_CI_run_id"], 31472269070)
        self.assertTrue(registration["both_required_jobs_green"])
        implementation = self.request["green_transport_implementation"]
        self.assertEqual(
            implementation["commit"],
            "93a067c4dcdb89ea5e5d17db6e5adaca454a64d1",
        )
        self.assertEqual(implementation["push_CI_run_id"], 31474412246)
        self.assertEqual(implementation["base_python_job_id"], 93724709807)
        self.assertEqual(implementation["optional_neuro_job_id"], 93724709840)
        self.assertTrue(implementation["both_required_jobs_green"])

    def test_consumed_parent_is_bound_and_cannot_be_reopened(self) -> None:
        parent = self.request["consumed_parent_evidence"]
        self.assertEqual(parent["consumed_route"], "IACKD2-F08")
        self.assertEqual(parent["metadata_response_opens"], 1)
        self.assertEqual(parent["response_body_reads"], 0)
        self.assertEqual(parent["scientific_observations"], 0)
        self.assertTrue(parent["IACKD2_consumed"])
        self.assertFalse(parent["IACKD2_retry_or_rerun_allowed"])
        self.assertTrue(parent["old_invocation_root_forbidden"])
        self.assertTrue(parent["old_retained_bundle_forbidden"])

    def test_every_bound_artifact_hash_is_current(self) -> None:
        for binding in self.request["target_artifacts"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))

    def test_only_metadata_framing_changes(self) -> None:
        delta = self.request["allowed_protocol_delta"]
        self.assertEqual(delta["changed_fields"], ["small_metadata_response_framing_policy"])
        self.assertTrue(delta["scientific_parent_inherited_unchanged"])
        self.assertTrue(delta["resource_safety_may_only_strengthen"])
        self.assertFalse(delta["post_result_tuning_or_update_allowed"])

    def test_transport_distinguishes_metadata_and_payload_integrity(self) -> None:
        metadata = self.request["metadata_response_contract"]
        self.assertEqual(metadata["requests"], 4)
        self.assertEqual(metadata["registered_body_bytes"], 595400)
        self.assertEqual(
            metadata["accepted_framing_profiles"],
            ["fixed_length", "chunked", "close_delimited"],
        )
        self.assertFalse(metadata["Content_Length_required"])
        self.assertTrue(metadata["exact_observed_body_bytes_required"])
        self.assertTrue(metadata["exact_registered_SHA256_required"])
        payload = self.request["payload_response_contract"]
        self.assertEqual(payload["objects"], 1340)
        self.assertEqual(payload["payload_bytes"], 7249113684)
        self.assertTrue(payload["exact_Content_Length_required"])
        self.assertTrue(payload["exact_registered_ETag_required"])
        self.assertTrue(payload["full_stream_SHA256_required"])

    def test_scientific_design_and_target_firewall_are_unchanged(self) -> None:
        science = self.request["frozen_scientific_scope"]
        self.assertEqual(science["participant_count"], 15)
        self.assertEqual(science["participant_hand_units"], 30)
        self.assertEqual(science["arms"], ["C2I", "I2C"])
        self.assertEqual(science["predictive_EEG_channels"], 26)
        self.assertEqual(science["parameter_update_fits"], 660)
        self.assertEqual(science["prediction_sets"], 900)
        self.assertEqual(science["maximum_verdict"], "IACKD2-R5")
        firewall = self.request["target_firewall"]
        self.assertEqual(firewall["final_target_visibility_before_green_freeze"], 0)
        self.assertEqual(firewall["final_target_deliveries"], 1)
        self.assertEqual(firewall["scoring_events"], 1)
        self.assertTrue(firewall["remote_green_hash_only_freeze_required"])

    def test_order_requires_green_executor_and_freeze(self) -> None:
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_fixture_and_mock_transport_executor_integration"),
        )
        self.assertLess(
            order.index("exact_additive_executor_commit_pushed_and_both_CI_jobs_green"),
            order.index("write_new_private_consumed_marker"),
        )
        self.assertLess(
            order.index("one_target_blind_660_fit_900_prediction_execution"),
            order.index("aggregate_hash_only_prediction_freeze"),
        )
        self.assertLess(
            order.index("prediction_freeze_commit_pushed_and_both_CI_jobs_green"),
            order.index("one_combined_final_target_delivery_and_score"),
        )

    def test_machine_safety_and_storage_caps_are_strict(self) -> None:
        caps = self.request["resource_caps"]
        safety = caps["pre_consumption_machine_safety"]
        self.assertEqual(safety["CPU_threads"], 1)
        self.assertEqual(safety["workers"], 1)
        self.assertEqual(safety["numerical_jobs"], 1)
        self.assertEqual(safety["minimum_free_disk_bytes"], 10 * 1024 * 1024 * 1024)
        self.assertEqual(safety["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertTrue(safety["failure_occurs_before_consumed_marker"])
        stream = caps["fresh_stream_and_derivatives"]
        self.assertEqual(stream["payload_bytes"], 7249113684)
        self.assertLessEqual(stream["peak_incremental_disk_bytes"], 1024**3)
        self.assertEqual((stream["retries"], stream["reruns"]), (0, 0))

    def test_all_current_access_counters_are_zero(self) -> None:
        for name, value in self.request["current_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_forbidden_scope_and_claim_boundary_are_explicit(self) -> None:
        forbidden = set(self.request["forbidden_operations"])
        required = {
            "old_invocation_root_or_retained_bundle_operation",
            "consumed_IACKD2_executor_amendment_or_rerun",
            "operation_on_another_project",
            "target_visibility_before_green_freeze",
            "retry_resume_restart_substitution_or_rerun",
            "scientific_claim_beyond_IACKD2_R5_or_brain_specific_origin",
        }
        self.assertTrue(required.issubset(forbidden))
        packet = " ".join(self.packet.split())
        self.assertIn("This packet authorizes nothing by itself", packet)
        self.assertIn("cannot authorize it retroactively", packet)
        self.assertIn("a fresh unambiguous `continue`", packet)
        self.assertIn("Scientific claim not established by this request", packet)


if __name__ == "__main__":
    unittest.main()
