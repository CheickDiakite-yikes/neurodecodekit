import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop25_authorization_request.v0.json"
PACKET_PATH = REPO_ROOT / "docs" / "LOOP_25_AUTHORIZATION_PACKET.md"
LOOP24_DECISION_PATH = (
    REPO_ROOT / "registries" / "loop24_authorization_decision.v0.json"
)
RW3_REQUEST_PATH = (
    REPO_ROOT / "registries" / "rw3_stage_a_authorization_request.v0.json"
)
INVARIANT_TEST_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "historical_snapshots"
    / "loop25"
    / "test_causal_preprocessing_contract.py.snapshot"
)


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


class Loop25AuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")
        cls.loop24 = json.loads(LOOP24_DECISION_PATH.read_text(encoding="utf-8"))
        cls.rw3 = json.loads(RW3_REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_status_and_every_authorization_flag_remain_false(self):
        request = self.request
        self.assertEqual(
            request["schema_name"],
            "neurodecodekit.loop25_authorization_request",
        )
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["status"], "awaiting_explicit_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        self.assertIsNone(request["authorization_record_commit"])
        flags = authorization_flags(request)
        self.assertEqual(len(flags), 16)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_green_registration_and_all_frozen_file_hashes_are_exact(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "a36d97b8556e95637a21c86c44095b7e8d4c4863",
        )
        self.assertEqual(registration["ci_conclusion"], "success")
        self.assertEqual(registration["complete_local_suite_tests"], 323)
        self.assertEqual(registration["new_contract_tests"], 10)
        target = self.request["target"]
        bindings = (
            ("contract", CONTRACT_PATH),
            (
                "preregistration",
                REPO_ROOT / "docs" / "LOOP_25_CAUSAL_PREPROCESSING_PREREGISTRATION.md",
            ),
            (
                "research",
                REPO_ROOT / "docs" / "LOOP_25_PRIMARY_SOURCE_RESEARCH.md",
            ),
            (
                "invariant_test",
                INVARIANT_TEST_SNAPSHOT_PATH,
            ),
        )
        for prefix, path in bindings:
            with self.subTest(path=path.name):
                self.assertEqual(target[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(target[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))

    def test_exact_decision_language_matches_immutable_contract(self):
        decision = self.request["decision"]
        contract_decision = self.contract["authorization"]
        self.assertEqual(
            decision["authorization_sentence_exact"],
            contract_decision["authorization_sentence_exact"],
        )
        self.assertEqual(
            decision["hold_sentence_exact"],
            contract_decision["hold_sentence_exact"],
        )
        self.assertFalse(decision["silence_or_general_continuation_is_authorization"])
        self.assertFalse(decision["roadmap_approval_is_authorization"])
        self.assertFalse(decision["loop24_or_rw3_decision_is_authorization"])
        self.assertFalse(decision["authorization_is_transitive_to_loop26_or_later"])
        self.assertEqual(len(decision["required_sequence_after_authorization"]), 8)

    def test_registered_scope_matches_fixture_schedules_refusals_and_cli(self):
        scope = self.request["registered_scope"]
        fixture = self.contract["fixture_contract"]
        self.assertEqual(scope["pipeline_id"], self.contract["planned_pipeline"]["pipeline_id"])
        self.assertEqual(scope["development_seed"], fixture["development"]["seed"])
        self.assertEqual(scope["qualification_seed"], fixture["qualification"]["seed"])
        self.assertEqual(scope["items_per_partition"], fixture["development"]["items"])
        self.assertEqual(scope["total_fixture_items"], 24)
        self.assertEqual(scope["signal_family_count"], len(fixture["signal_families"]))
        self.assertEqual(
            scope["registered_chunk_schedule_count"],
            len(self.contract["registered_chunk_schedules"]),
        )
        self.assertEqual(
            scope["registered_resume_cut_count"],
            len(self.contract["registered_resume_cut_source_samples"]),
        )
        self.assertEqual(scope["registered_refusal_count"], 40)
        self.assertEqual(scope["required_access_counter_count"], 21)
        self.assertEqual(scope["planned_files"], self.contract["planned_implementation"]["files"])
        self.assertEqual(
            scope["planned_cli_commands"],
            self.contract["planned_implementation"]["cli_commands"],
        )

    def test_resources_are_no_larger_and_forbidden_operations_remain_zero(self):
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

    def test_protected_evidence_and_fresh_seeds_are_not_repurposed(self):
        protected = self.request["protected_evidence"]
        self.assertEqual(protected["consumed_synthetic_seeds"], [2203, 2303, 2353, 2401])
        self.assertEqual(protected["unopened_synthetic_seeds"], [2402, 2501, 2502])
        real = " ".join(protected["real_cohorts"])
        self.assertIn("S21 session-1", real)
        self.assertIn("S21 session-2", real)
        self.assertIn("S7 EEG", real)
        self.assertFalse(self.request["authorized_now"])
        decision = json.loads(
            (REPO_ROOT / "registries/loop25_authorization_decision.v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            decision["authorization_request"]["request_path"],
            "registries/loop25_authorization_request.v1.json",
        )
        self.assertTrue(
            all(
                (REPO_ROOT / path).exists()
                for path in self.request["registered_scope"]["planned_files"]
            )
        )

    def test_loop24_and_rw3_history_cannot_authorize_loop25(self):
        loop24_flags = self.loop24["authorization"]
        self.assertTrue(loop24_flags["loop24_implementation_authorized_now"])
        self.assertFalse(loop24_flags["loop25_through_44_execution_authorized_now"])
        self.assertFalse(self.rw3["authorized_now"])
        self.assertFalse(self.request["authorized_now"])

    def test_human_packet_exposes_decision_caps_access_and_claim_boundary(self):
        sentence = self.request["decision"]["authorization_sentence_exact"]
        self.assertIn(sentence, self.packet.replace("\n> ", " ").replace("\n", " "))
        for phrase in (
            "24 items",
            "seven frozen chunk schedules",
            "Ten registered resume cuts",
            "Forty exact refusal IDs",
            "21 access counters",
            "8 MiB",
            "authorized_now` is `false",
            "Scientific or decoding claim not established",
        ):
            self.assertIn(phrase, self.packet)


if __name__ == "__main__":
    unittest.main()
