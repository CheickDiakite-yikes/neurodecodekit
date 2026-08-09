import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / "registries/loop54_stage_a_recovery_authorization_request.v1.json"
PACKET_PATH = ROOT / "docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_PACKET.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
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


class Loop54StageARecoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_request_is_recovery_bound_and_not_authorized(self):
        request = self.request
        self.assertEqual(
            request["schema_name"],
            "neurodecodekit.loop54_stage_a_recovery_authorization_request",
        )
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(
            request["status"],
            "prepared_recovery_bound_exact_decision_pending_user_not_authorized",
        )
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        self.assertTrue(
            all(value is False for _, value in authorization_flags(request)),
            authorization_flags(request),
        )

    def test_immutable_registration_hashes_and_blobs_are_current(self):
        registration = self.request["immutable_registration"]
        self.assertEqual(
            registration["commit"],
            "c1146233a6178ca5e1153b92565915abad029719",
        )
        self.assertEqual(len(registration["artifacts"]), 3)
        for artifact in registration["artifacts"]:
            path = ROOT / artifact["path"]
            self.assertEqual(artifact["sha256"], sha256(path), artifact["path"])
            self.assertEqual(artifact["git_blob_sha1"], git_blob_sha1(path), artifact["path"])
        self.assertTrue(registration["snapshot_must_remain_byte_identical"])

    def test_green_anchor_recovery_and_preceding_work_order_are_bound(self):
        evidence = self.request["remote_evidence"]
        historical = evidence["historical_exact_registration_run"]
        self.assertFalse(historical["may_be_called_green"])
        anchor = evidence["pinned_toolchain_proof_anchor"]
        self.assertEqual(anchor["push_CI_run_id"], 31132586790)
        self.assertEqual(anchor["push_CI_conclusion"], "success")
        recovery = evidence["additive_recovery_record"]
        self.assertEqual(
            recovery["commit"],
            "5915bdf28d96385b190f27c7743dd3df00396ced",
        )
        self.assertEqual(recovery["push_CI_run_id"], 31277277711)
        self.assertEqual(recovery["push_CI_conclusion"], "success")
        for name in ("document", "registry"):
            binding = recovery[name]
            path = ROOT / binding["path"]
            self.assertEqual(binding["sha256"], sha256(path))
            self.assertEqual(binding["git_blob_sha1"], git_blob_sha1(path))
        preceding = evidence["completed_preceding_work_order"]
        self.assertEqual(preceding["work_order"], 5)
        self.assertEqual(preceding["push_CI_run_id"], 31282657626)
        self.assertEqual(preceding["push_CI_conclusion"], "success")
        self.assertFalse(preceding["authorizes_L54_A"])

    def test_historical_request_is_hash_bound_and_nonactionable(self):
        supersession = self.request["supersession"]
        for prefix in ("historical_packet", "historical_request"):
            path = ROOT / supersession[f"{prefix}_path"]
            self.assertEqual(supersession[f"{prefix}_sha256"], sha256(path))
            self.assertEqual(supersession[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))
        self.assertFalse(supersession["historical_request_was_authorized"])
        self.assertFalse(supersession["historical_sentence_actionable_now"])

    def test_exact_sentence_matches_packet_and_preserves_order(self):
        sentence = self.request["decision"]["exact_authorization_sentence"]
        packet_sentence = next(
            line.removeprefix("> ")
            for line in self.packet.splitlines()
            if line.startswith("> Authorize the Loop 54 Stage A recovery-bound")
        )
        self.assertEqual(sentence, packet_sentence)
        for phrase in (
            "only after this decision is committed, pushed, and remotely green",
            "only after that exact implementation is committed, pushed, and remotely green",
            "one VHDR content open",
            "zero network bytes",
            "do not authorize opening, statting, resolving, hashing, or parsing the VMRK",
            "or any scientific, decoding, neural, real-time, portable, home-use, or clinical claim upgrade",
        ):
            self.assertIn(phrase, sentence)
        self.assertFalse(self.request["decision"]["exact_sentence_received_from_user"])

    def test_scope_resources_and_current_counters_are_exact(self):
        scope = self.request["requested_scope_after_green_decision"]
        self.assertEqual(scope["registered_VHDR_expected_size_bytes"], 11705)
        self.assertEqual(scope["registered_real_executions"], 1)
        self.assertEqual(scope["registered_VHDR_content_opens"], 1)
        self.assertFalse(scope["resolve_stat_hash_or_open_referenced_siblings"])
        resources = self.request["resource_caps"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["maximum_combined_generated_output_bytes"], 1024**2)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["new_payload_bytes"], 0)
        self.assertTrue(all(value == 0 for value in self.request["current_access_counters"].values()))

    def test_packet_and_public_route_stop_before_parser_or_S20(self):
        for phrase in (
            "not an authorization decision",
            "This packet did not stat, resolve, hash, or open that local path",
            "Scientific claim not established",
        ):
            self.assertIn(phrase, self.packet)
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        work_order_six = next(line for line in queue.splitlines() if line.startswith("| 6 |"))
        work_order_seven = next(line for line in queue.splitlines() if line.startswith("| 7 |"))
        self.assertIn("Decision Recorded; CI Gate", work_order_six)
        self.assertIn("| Gated |", work_order_seven)

    def test_local_verification_advances_the_complete_baseline(self):
        verification = self.request["request_local_verification"]
        self.assertEqual(verification["focused_recovery_route_tests_passed"], 50)
        self.assertEqual(verification["complete_tests_passed"], 1317)
        self.assertEqual(verification["complete_tests_skipped"], 3)
        self.assertEqual(verification["pre_change_complete_tests_passed"], 1309)
        self.assertEqual(verification["test_count_delta"], 8)
        self.assertEqual(verification["ruff_version"], "0.15.20")
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertEqual(verification["tracked_registry_JSON_files_validated"], 90)
        self.assertEqual(verification["local_markdown_links_broken"], 0)
        self.assertTrue(verification["root_CLI_help_passed"])
        self.assertTrue(verification["staged_gitleaks_passed"])
        self.assertTrue(verification["diff_check_passed"])


if __name__ == "__main__":
    unittest.main()
