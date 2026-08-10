import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT / "registries" / "iackd_channel_role_geometry_authorization_decision.v0.json"
)
REQUEST_PATH = (
    ROOT / "registries" / "iackd_channel_role_geometry_authorization_request.v0.json"
)
DOC_PATH = ROOT / "docs" / "IACKD_CHANNEL_ROLE_GEOMETRY_AUTHORIZATION_DECISION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


class IACKDChannelRoleGeometryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.document = DOC_PATH.read_text(encoding="utf-8")

    def test_actual_maintainer_words_are_preserved_without_fabricated_recital(self):
        words = "continue :)"
        self.assertEqual(self.decision["maintainer_words"], words)
        self.assertEqual(
            self.decision["maintainer_words_sha256"],
            hashlib.sha256(words.encode()).hexdigest(),
        )
        user = self.decision["user_authorization"]
        self.assertTrue(user["actual_message_preserved_verbatim"])
        self.assertEqual(user["sole_active_Tier_C_packet"], "IACKD-H2")
        self.assertTrue(user["packet_commit_CI_scope_and_gate_identified_before_message"])
        self.assertTrue(user["maintainer_unambiguously_directed_continue"])
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertFalse(user["scope_expansion_by_inference"])

    def test_green_request_commit_and_jobs_are_exact(self):
        green = self.decision["green_request"]
        self.assertEqual(
            green["commit"], "86174bc86123bc010bac2f40a9d72147dc8aef05"
        )
        self.assertEqual(green["push_CI_run_id"], 31_431_064_259)
        self.assertEqual(green["base_python_job_id"], 93_594_327_147)
        self.assertEqual(green["optional_neuro_job_id"], 93_594_327_069)
        self.assertTrue(green["both_required_jobs_green"])

    def test_bound_artifact_hashes_and_git_blobs_are_current(self):
        for binding in self.decision["bound_artifacts"].values():
            path = ROOT / binding["path"]
            self.assertEqual(binding["sha256"], sha256(path))
            self.assertEqual(binding["git_blob_sha1"], git_blob_sha1(path))

    def test_executor_required_decision_shape_is_exact(self):
        required = self.request["required_decision_shape"]
        implementation = self.decision["green_implementation"]
        authorization = self.decision["authorization"]
        self.assertEqual(self.decision["schema_name"], required["schema_name"])
        self.assertEqual(self.decision["schema_version"], required["schema_version"])
        self.assertEqual(self.decision["contract_sha256"], required["contract_sha256"])
        self.assertEqual(implementation["commit"], required["implementation_commit"])
        self.assertEqual(
            implementation["push_CI_run_id"], required["implementation_push_CI_run_id"]
        )
        self.assertEqual(
            implementation["base_python_job_id"],
            required["implementation_base_python_job_id"],
        )
        self.assertEqual(
            implementation["optional_neuro_job_id"],
            required["implementation_optional_neuro_job_id"],
        )
        self.assertEqual(
            implementation["implementation_registry_sha256"],
            required["implementation_registry_sha256"],
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_decision_commit_pushed_and_both_CI_jobs_green"
            ]
        )
        self.assertTrue(authorization["one_registered_public_metadata_audit"])
        self.assertEqual(authorization["real_metadata_requests"], 316)
        self.assertEqual(authorization["real_metadata_body_bytes"], 457_602)
        self.assertEqual(authorization["retries"], 0)
        self.assertEqual(authorization["reruns"], 0)

    def test_authorized_scope_matches_request_without_expansion(self):
        authorization = self.decision["authorization"]
        requested = self.request["requested_scope"]
        self.assertEqual(
            authorization["real_metadata_requests"], requested["metadata_requests"]
        )
        self.assertEqual(
            authorization["real_metadata_body_bytes"], requested["metadata_body_bytes"]
        )
        self.assertEqual(
            authorization["body_SHA256_passes"], requested["body_SHA256_passes"]
        )
        self.assertEqual(
            authorization["semantic_parse_passes"], requested["semantic_parse_passes"]
        )
        self.assertEqual(authorization["role_objects"], requested["role_objects"])
        for name in (
            "raw_bodies_persisted",
            "individual_paths_participants_rows_coordinates_or_free_text_public",
            "existing_local_IACKD_bundle_operations",
            "VHDR_sibling_signal_event_trajectory_target_model_or_score_operations",
            "dependency_installs",
            "retries",
            "reruns",
            "scientific_claim_upgrades",
        ):
            self.assertEqual(authorization[name], 0, name)

    def test_request_remains_an_immutable_all_false_snapshot(self):
        self.assertEqual(
            self.request["status"], "awaiting_new_packet_bound_maintainer_decision"
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_resources_are_exact_request_copies(self):
        self.assertEqual(self.decision["resource_caps"], self.request["resource_caps"])

    def test_order_requires_green_decision_and_consumption_before_network(self):
        order = self.decision["required_execution_order"]
        self.assertLess(
            order.index("test_commit_push_and_obtain_green_CI_for_this_decision"),
            order.index("write_one_private_consumed_marker_before_the_first_request"),
        )
        self.assertLess(
            order.index("write_one_private_consumed_marker_before_the_first_request"),
            order.index("issue_exactly_316_sequential_public_metadata_requests"),
        )
        self.assertFalse(
            self.decision["next_gate"]["real_metadata_execution_may_begin_before_green"]
        )
        self.assertFalse(self.decision["next_gate"]["rerun_available"])

    def test_decision_only_counters_are_zero_except_one_ci_verification(self):
        counters = self.decision["decision_only_access_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
        for name, value in counters.items():
            if name == "GitHub_CI_verification_calls":
                continue
            if name == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, name)

    def test_document_preserves_engineering_and_scientific_boundaries(self):
        compact = " ".join(self.document.split())
        self.assertIn("The decision is ineffective until its own commit", compact)
        self.assertIn("exactly 316 registered public OpenNeuro metadata bodies", compact)
        self.assertIn("Scientific claim not established", compact)
        self.assertIn("brain-specific origin", compact)
        self.assertIn(
            "There is no fallback, redirect, retry, substitution, parser amendment, "
            "or rerun",
            compact,
        )


if __name__ == "__main__":
    unittest.main()
