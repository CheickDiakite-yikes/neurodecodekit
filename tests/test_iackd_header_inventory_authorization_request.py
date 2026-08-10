import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / "registries/iackd_channel_inventory_authorization_request.v0.json"
PACKET_PATH = ROOT / "docs/IACKD_CHANNEL_INVENTORY_AUTHORIZATION_PACKET.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDHeaderInventoryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_request_is_all_false_and_waits_for_new_user_words(self):
        self.assertEqual(
            self.request["status"], "awaiting_new_packet_bound_maintainer_decision"
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
        self.assertFalse(authorization["earlier_continue_is_retroactive_authorization"])

    def test_green_registration_and_implementation_are_exact(self):
        registration = self.request["green_registration"]
        self.assertEqual(
            registration["commit"], "0e52278aaa1d15e70f4baab7b21ab1c96eb37f67"
        )
        self.assertEqual(registration["push_CI_run_id"], 31_412_667_060)
        self.assertTrue(registration["both_required_jobs_green"])
        implementation = self.request["green_implementation"]
        self.assertEqual(
            implementation["commit"], "16621cc484f4bec4a9474b9ac20d5b7d9314152f"
        )
        self.assertEqual(implementation["push_CI_run_id"], 31_415_213_841)
        self.assertEqual(implementation["base_python_job_id"], 93_542_494_819)
        self.assertEqual(implementation["optional_neuro_job_id"], 93_542_494_839)
        self.assertTrue(implementation["both_required_jobs_green"])

    def test_every_bound_artifact_hash_is_current(self):
        for binding in self.request["target_artifacts"].values():
            self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))

    def test_scope_is_exactly_128_small_public_headers(self):
        scope = self.request["requested_scope"]
        self.assertEqual(scope["provider"], "OpenNeuro")
        self.assertEqual(scope["dataset_id"], "ds006840")
        self.assertEqual(scope["version"], "1.0.0")
        self.assertEqual(scope["object_role"], "eeg_header")
        self.assertEqual(scope["VHDR_requests"], 128)
        self.assertEqual(scope["VHDR_body_bytes"], 161_792)
        self.assertEqual(scope["body_SHA256_passes"], 128)
        self.assertEqual(scope["semantic_parse_passes"], 128)
        self.assertEqual(scope["public_name_allowlist"], 7)
        self.assertEqual(scope["public_aggregate_ledgers"], 1)
        self.assertEqual(scope["maximum_diagnostic_route"], "IACKDH-R5")

    def test_order_requires_green_decision_before_any_request(self):
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("write_private_consumed_marker"),
        )
        self.assertLess(
            order.index("write_private_consumed_marker"),
            order.index("issue_128_sequential_public_VHDR_requests"),
        )
        self.assertLess(
            order.index("issue_128_sequential_public_VHDR_requests"),
            order.index("emit_one_aggregate_public_ledger_and_stop"),
        )

    def test_resources_are_small_one_thread_and_no_rerun(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["concurrent_numerical_jobs"], 1)
        self.assertEqual(caps["wall_time_seconds"], 120)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(caps["VHDR_requests"], 128)
        self.assertEqual(caps["expected_VHDR_body_bytes"], 161_792)
        self.assertLessEqual(caps["network_body_bytes"], 1024 * 1024)
        self.assertLessEqual(caps["incremental_disk_bytes"], 2 * 1024 * 1024)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)

    def test_all_real_and_forbidden_current_counters_are_zero(self):
        for name, value in self.request["current_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_future_decision_shape_matches_executor_gate(self):
        shape = self.request["required_decision_shape"]
        self.assertEqual(
            shape["schema_name"],
            "neurodecodekit.iackd_channel_inventory_authorization_decision",
        )
        self.assertTrue(shape["maintainer_words_must_be_actual_and_nonempty"])
        self.assertTrue(shape["one_registered_real_header_audit"])
        self.assertEqual(shape["real_VHDR_requests"], 128)
        self.assertEqual(shape["real_VHDR_body_bytes"], 161_792)
        self.assertEqual(shape["retries"], 0)
        self.assertEqual(shape["reruns"], 0)

    def test_forbidden_scope_and_claim_language_are_explicit(self):
        forbidden = set(self.request["forbidden_operations"])
        required = {
            "existing_local_IACKD_bundle_stat_resolve_hash_open_move_or_delete",
            "VMRK_EEG_channels_events_geometry_ball_Leap_or_other_sibling_access",
            "signal_event_trajectory_target_label_model_inference_training_or_scoring",
            "additional_object_metadata_refresh_redirect_retry_resume_restart_or_rerun",
            "S20_S21_S24_S25_SpanishBCBL_PhysioNet_raw_FIF_or_MAT_access",
            "scientific_decoding_neural_realtime_hardware_assistive_or_clinical_claim_upgrade",
        }
        self.assertTrue(required.issubset(forbidden))
        packet = " ".join(self.packet.split())
        self.assertIn("Scientific claim not established by this request", packet)
        self.assertIn("cannot authorize it retroactively", packet)
        self.assertIn("a new unambiguous `continue`", packet)


if __name__ == "__main__":
    unittest.main()
