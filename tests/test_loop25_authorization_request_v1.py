import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v1.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop25_authorization_request.v1.json"
PACKET_PATH = REPO_ROOT / "docs" / "LOOP_25_AUTHORIZATION_PACKET_V1.md"
AMENDMENT_PATH = (
    REPO_ROOT / "docs" / "LOOP_25_CAUSAL_PREPROCESSING_AMENDMENT_1.md"
)
AUDIT_PATH = REPO_ROOT / "docs" / "LOOP_25_ANTI_ALIAS_AUDIT.md"
AMENDMENT_TEST_PATH = REPO_ROOT / "tests" / "test_causal_preprocessing_amendment.py"
V0_CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v0.json"
V0_REQUEST_PATH = REPO_ROOT / "registries" / "loop25_authorization_request.v0.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()


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


class Loop25AuthorizationRequestV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")
        cls.amendment = AMENDMENT_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_all_authorization_flags_are_false(self):
        request = self.request
        self.assertEqual(
            request["schema_name"], "neurodecodekit.loop25_authorization_request"
        )
        self.assertEqual(request["schema_version"], "0.2.0")
        self.assertTrue(request["request_id"].endswith("-v1"))
        self.assertEqual(request["status"], "awaiting_explicit_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        self.assertIsNone(request["authorization_record_commit"])
        flags = authorization_flags(request)
        self.assertEqual(len(flags), 16)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_green_amendment_commit_and_ci_are_bound(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "b6b92d8ea1cdeadfd6b7cd9f4704aee018516197",
        )
        self.assertEqual(registration["commit_short"], "b6b92d8")
        self.assertEqual(registration["ci_run_id"], 29195938038)
        self.assertEqual(registration["ci_conclusion"], "success")
        self.assertEqual(registration["base_python_job_conclusion"], "success")
        self.assertEqual(
            registration["optional_neuro_readers_job_conclusion"], "success"
        )
        self.assertEqual(registration["complete_local_suite_tests"], 342)
        self.assertEqual(registration["complete_local_suite_skips"], 3)
        self.assertEqual(registration["new_amendment_tests"], 11)

    def test_contract_amendment_audit_and_test_hashes_are_exact(self):
        target = self.request["target"]
        bindings = (
            ("contract", CONTRACT_PATH),
            ("amendment", AMENDMENT_PATH),
            ("anti_alias_audit", AUDIT_PATH),
            ("invariant_test", AMENDMENT_TEST_PATH),
        )
        for prefix, path in bindings:
            with self.subTest(path=path.name):
                self.assertEqual(target[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(target[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))
        self.assertEqual(target["contract_id"], self.contract["contract_id"])
        self.assertEqual(target["contract_schema_version"], "0.2.0")
        self.assertTrue(target["amendment_snapshot_remains_immutable"])

    def test_original_v0_scope_is_immutable_withdrawn_and_unopened(self):
        supersession = self.request["supersession"]
        self.assertEqual(supersession["original_contract_sha256"], sha256(V0_CONTRACT_PATH))
        self.assertEqual(supersession["original_request_sha256"], sha256(V0_REQUEST_PATH))
        self.assertFalse(supersession["original_request_was_authorized"])
        self.assertFalse(supersession["original_authorization_sentence_is_actionable_now"])
        self.assertFalse(supersession["original_development_seed_was_opened"])
        self.assertFalse(supersession["original_qualification_seed_was_opened"])
        self.assertIn("50-to-500 Hz folding band", supersession["reason"])

    def test_exact_decision_language_matches_contract_amendment_and_packet(self):
        decision = self.request["decision"]
        sentence = decision["authorization_sentence_exact"]
        self.assertEqual(sentence, self.contract["authorization"]["authorization_sentence_exact"])
        normalized_packet = (
            self.packet.replace("\n> ", " ").replace("\n", " ").replace("`", "")
        )
        normalized_amendment = (
            self.amendment.replace("\n> ", " ").replace("\n", " ").replace("`", "")
        )
        self.assertIn(sentence, normalized_packet)
        self.assertIn(sentence, normalized_amendment)
        self.assertFalse(decision["silence_or_general_continuation_is_authorization"])
        self.assertFalse(decision["roadmap_approval_is_authorization"])
        self.assertFalse(decision["loop24_or_rw3_decision_is_authorization"])
        self.assertFalse(decision["authorization_is_transitive_to_loop26_or_later"])
        self.assertEqual(len(decision["required_sequence_after_authorization"]), 9)

    def test_amended_scope_matches_filter_fixture_schedule_and_state_contracts(self):
        scope = self.request["registered_scope"]
        fixture = self.contract["fixture_contract"]
        frequency = self.contract["acceptance_gates"]["frequency_response"]
        state = self.contract["state_contract"]
        self.assertEqual(scope["pipeline_id"], self.contract["planned_pipeline"]["pipeline_id"])
        self.assertEqual(scope["development_seed"], fixture["development"]["seed"])
        self.assertEqual(scope["qualification_seed"], fixture["qualification"]["seed"])
        self.assertEqual(scope["total_fixture_items"], 24)
        self.assertEqual(scope["signal_family_count"], 6)
        self.assertEqual(scope["registered_chunk_schedule_count"], 7)
        self.assertEqual(scope["registered_resume_cut_count"], 10)
        self.assertEqual(scope["registered_future_mutation_cut_count"], 3)
        self.assertEqual(
            scope["dense_frequency_response_point_count"],
            frequency["dense_grid_points_inclusive"],
        )
        self.assertEqual(
            scope["registered_alias_source_probe_count"],
            len(frequency["registered_alias_source_probe_frequencies_hz"]),
        )
        self.assertEqual(scope["registered_refusal_count"], 45)
        self.assertEqual(scope["required_access_counter_count"], 23)
        self.assertEqual(scope["maximum_total_sos_sections"], state["maximum_total_sos_sections"])
        self.assertEqual(
            scope["maximum_filter_state_array_bytes"],
            state["maximum_filter_state_array_bytes"],
        )

    def test_static_filter_gate_precedes_all_fixture_array_access(self):
        sequence = self.contract["partition_access_sequence"]
        static = sequence.index(
            "run_static_pole_dense_frequency_alias_fold_map_impulse_and_step_design_gates"
        )
        development = sequence.index("open_development_target_free_partition_once")
        self.assertLess(static, development)
        self.assertTrue(
            self.request["registered_scope"][
                "static_filter_gate_runs_before_development_partition_open"
            ]
        )
        self.assertTrue(
            self.request["registered_scope"][
                "static_filter_failure_keeps_both_partitions_unopened"
            ]
        )
        required = self.request["decision"]["required_sequence_after_authorization"]
        self.assertLess(
            required.index(
                "design_hash_and_pass_the_static_filter_gate_before_any_fixture_array_open"
            ),
            required.index("open_seed_2501_development_once_and_freeze_its_report"),
        )

    def test_resources_do_not_expand_and_forbidden_counters_are_zero(self):
        requested = self.request["resource_caps"]
        contract = self.contract["resource_caps"]
        for name, value in requested.items():
            with self.subTest(resource=name):
                self.assertLessEqual(value, contract[name])
        zero_names = [
            name
            for name in requested
            if any(
                term in name
                for term in (
                    "network",
                    "real_",
                    "consumed",
                    "target_",
                    "checkpoint",
                    "model_",
                    "training",
                    "parameter",
                    "rw3",
                    "stream_",
                )
            )
        ]
        self.assertEqual(len(zero_names), 11)
        self.assertTrue(all(requested[name] == 0 for name in zero_names))

    def test_protected_evidence_and_unopened_seeds_remain_explicit(self):
        protected = self.request["protected_evidence"]
        self.assertEqual(protected["consumed_synthetic_seeds"], [2203, 2303, 2353, 2401])
        self.assertEqual(protected["unopened_synthetic_seeds"], [2402, 2501, 2502])
        real = " ".join(protected["real_cohorts"])
        self.assertIn("S21 session-1", real)
        self.assertIn("S21 session-2", real)
        self.assertIn("S7 EEG", real)
        self.assertTrue(any("folding-band gate" in rule for rule in protected["rules"]))

    def test_packet_discloses_scope_caps_sequence_and_claim_boundary(self):
        for phrase in (
            "65,537 points",
            "23 exact alias source probes",
            "45 exact refusal IDs",
            "23 access counters",
            "8 MiB",
            "Every `authorized_now` field",
            "Scientific Or Decoding Claim Not Established",
        ):
            self.assertIn(phrase, self.packet)
        claims = " ".join(self.request["claim_boundary"])
        self.assertIn("filter phase or ringing", claims)
        self.assertIn("neural information", claims)
        self.assertIn("end-to-end latency", claims)
        self.assertIn("clinical utility", claims)

    def test_no_runtime_fixture_cli_or_model_surface_exists(self):
        for relative in self.request["registered_scope"]["planned_files"]:
            self.assertFalse((REPO_ROOT / relative).exists(), relative)
        cli_text = (REPO_ROOT / "src" / "neurodecodekit" / "cli.py").read_text(
            encoding="utf-8"
        )
        for command in self.request["registered_scope"]["planned_cli_commands"]:
            self.assertNotIn(command, cli_text)


if __name__ == "__main__":
    unittest.main()
