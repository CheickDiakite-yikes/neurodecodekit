import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT / "registries" / "iackd_channel_role_geometry_authorization_request.v0.json"
)
PACKET_PATH = ROOT / "docs" / "IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_PACKET.md"
HISTORICAL_MUTABLE_BINDINGS = {
    "tests/test_iackd_channel_role_geometry_implementation.py": (
        "d5f7c40dd30050d6067adefc5afd6c7f3e19a756d313999a2afbe053e91a2491"
    ),
    "tests/test_iackd_channel_role_geometry_authorization_request.py": (
        "c6d8454f87cb6f180abc8da6aebd616ca27981fad74acfac6343905b3d093cb8"
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDChannelRoleGeometryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_request_is_all_false_and_waits_for_fresh_user_words(self):
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
            registration["commit"], "228ccd03f5e0b5d02ba104e13b77b04f2032df78"
        )
        self.assertEqual(registration["push_CI_run_id"], 31427931578)
        self.assertTrue(registration["both_required_jobs_green"])
        implementation = self.request["green_implementation"]
        self.assertEqual(
            implementation["commit"], "9f6fef9540ae0a1fe52cbf24b17b0af89147beae"
        )
        self.assertEqual(implementation["push_CI_run_id"], 31430151368)
        self.assertEqual(implementation["base_python_job_id"], 93591323731)
        self.assertEqual(implementation["optional_neuro_job_id"], 93591323646)
        self.assertTrue(implementation["both_required_jobs_green"])

    def test_every_bound_artifact_hash_is_current(self):
        for binding in self.request["target_artifacts"].values():
            with self.subTest(path=binding["path"]):
                if binding["path"] in HISTORICAL_MUTABLE_BINDINGS:
                    self.assertEqual(
                        binding["sha256"], HISTORICAL_MUTABLE_BINDINGS[binding["path"]]
                    )
                else:
                    self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))

    def test_scope_is_exactly_316_small_public_metadata_bodies(self):
        scope = self.request["requested_scope"]
        self.assertEqual(scope["provider"], "OpenNeuro")
        self.assertEqual(scope["dataset_id"], "ds006840")
        self.assertEqual(scope["version"], "1.0.0")
        self.assertEqual(
            scope["role_objects"],
            {"channels": 128, "eeg_sidecar": 128, "electrodes": 30, "coordsystem": 30},
        )
        self.assertEqual(scope["metadata_requests"], 316)
        self.assertEqual(scope["metadata_body_bytes"], 457602)
        self.assertEqual(scope["body_SHA256_passes"], 316)
        self.assertEqual(scope["semantic_parse_passes"], 316)
        self.assertEqual(scope["public_aggregate_ledgers"], 1)
        self.assertEqual(scope["maximum_diagnostic_route"], "IACKDR-R4")

    def test_order_requires_green_decision_before_consumption_or_request(self):
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("write_private_consumed_marker"),
        )
        self.assertLess(
            order.index("write_private_consumed_marker"),
            order.index("issue_316_sequential_public_metadata_requests"),
        )
        self.assertLess(
            order.index("issue_316_sequential_public_metadata_requests"),
            order.index("emit_one_aggregate_public_ledger_and_stop"),
        )

    def test_response_contract_is_one_pass_no_redirect_or_retry(self):
        response = self.request["response_contract"]
        self.assertTrue(response["sequential"])
        self.assertEqual(response["maximum_concurrency"], 1)
        self.assertTrue(response["final_URL_must_equal_requested_URL"])
        self.assertTrue(response["Content_Length_must_equal_registered_size"])
        self.assertTrue(response["ETag_must_equal_registered_ETag"])
        self.assertEqual(response["Content_Encoding"], "identity_only")
        self.assertEqual(response["body_SHA256_passes_per_object"], 1)
        self.assertEqual(response["semantic_parse_passes_per_object"], 1)
        self.assertEqual((response["redirects"], response["retries"]), (0, 0))

    def test_resources_are_bounded_one_thread_and_no_rerun(self):
        caps = self.request["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["concurrent_numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["wall_time_seconds"], 180)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(caps["requests"], 316)
        self.assertEqual(caps["expected_body_bytes"], 457602)
        self.assertLessEqual(caps["network_body_bytes"], 2 * 1024 * 1024)
        self.assertLessEqual(caps["incremental_disk_bytes"], 4 * 1024 * 1024)
        self.assertEqual((caps["retries"], caps["reruns"]), (0, 0))

    def test_all_real_and_forbidden_current_counters_are_zero(self):
        for name, value in self.request["current_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_future_decision_shape_matches_executor_gate(self):
        shape = self.request["required_decision_shape"]
        self.assertEqual(
            shape["schema_name"],
            "neurodecodekit.iackd_channel_role_geometry_authorization_decision",
        )
        self.assertTrue(shape["maintainer_words_must_be_actual_and_nonempty"])
        self.assertTrue(shape["one_registered_public_metadata_audit"])
        self.assertEqual(shape["real_metadata_requests"], 316)
        self.assertEqual(shape["real_metadata_body_bytes"], 457602)
        self.assertEqual((shape["retries"], shape["reruns"]), (0, 0))

    def test_forbidden_scope_and_claim_language_are_explicit(self):
        forbidden = set(self.request["forbidden_operations"])
        required = {
            "existing_local_IACKD_bundle_stat_resolve_hash_open_move_or_delete",
            "VHDR_VMRK_EEG_event_ball_Leap_or_unregistered_object_access",
            "signal_event_trajectory_target_label_model_inference_training_or_scoring",
            "additional_object_inventory_refresh_redirect_retry_resume_restart_or_rerun",
            "S20_S21_S24_S25_SpanishBCBL_PhysioNet_raw_FIF_or_MAT_access",
            "IACKD2_or_scientific_decoding_neural_realtime_hardware_assistive_or_clinical_claim_upgrade",
        }
        self.assertTrue(required.issubset(forbidden))
        packet = " ".join(self.packet.split())
        self.assertIn("Scientific claim not established by this request", packet)
        self.assertIn("cannot authorize it retroactively", packet)
        self.assertIn("a fresh unambiguous `continue`", packet)


if __name__ == "__main__":
    unittest.main()
