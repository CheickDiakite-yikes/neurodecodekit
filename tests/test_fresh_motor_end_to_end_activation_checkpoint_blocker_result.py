from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "registries/fresh_motor_end_to_end_activation_checkpoint_blocker_result.v0.json"
)
FRONTIER = ROOT / "registries/current_research_frontier.v28.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v27.json"


def _git_blob(payload: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload,
        usedforsecurity=False,
    ).hexdigest()


def _assert_identity(test: unittest.TestCase, identity: dict[str, object]) -> None:
    payload = (ROOT / str(identity["path"])).read_bytes()
    test.assertEqual(len(payload), identity["bytes"])
    test.assertEqual(hashlib.sha256(payload).hexdigest(), identity["sha256"])
    test.assertEqual(_git_blob(payload), identity["git_blob"])


class FreshMotorActivationCheckpointBlockerResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_result_and_bound_authority_identities_are_exact(self) -> None:
        _assert_identity(self, self.result["human_result"])
        for identity in self.result["bound_authority"].values():
            if isinstance(identity, dict):
                _assert_identity(self, identity)

    def test_exact_activation_blocker_is_terminal(self) -> None:
        checkpoint = self.result["activation_checkpoint"]
        self.assertEqual(checkpoint["verifier_invocations"], 1)
        self.assertEqual(checkpoint["GitHub_CI_read_requests"], 3)
        self.assertEqual(checkpoint["network_retries"], 0)
        self.assertEqual(checkpoint["emitted_route"], "WITNESS_TRANSPORT_PARK")
        self.assertEqual(checkpoint["emitted_reason"], "CI_CHECK_IDENTITY")
        self.assertEqual(checkpoint["packet_terminal_class"], "ANY_OTHER_TERMINAL_ROUTE")
        self.assertFalse(checkpoint["checkpoint_passed"])
        self.assertFalse(checkpoint["standing_delegation_effective"])
        self.assertIsNone(checkpoint["GitHub_response_body_bytes"])
        self.assertIsNone(checkpoint["runtime_seconds"])
        self.assertIsNone(checkpoint["peak_RSS_bytes"])
        self.assertFalse(checkpoint["more_specific_check_predicate_or_value_inferred"])

    def test_protocol_integrity_violation_is_not_a_retry_loophole(self) -> None:
        integrity = self.result["protocol_integrity"]
        self.assertFalse(integrity["registered_FMSR1_E2E_entrypoint_used"])
        self.assertTrue(integrity["predecessor_bound_run_CI_W0_helper_called_directly"])
        self.assertFalse(integrity["durable_E2E_attempt_arm_before_first_network_request"])
        self.assertTrue(integrity["required_preflight_and_reservation_sequence_bypassed"])
        self.assertTrue(integrity["protocol_integrity_blocker"])
        self.assertFalse(integrity["retroactive_arm_allowed"])
        self.assertFalse(integrity["missing_arm_makes_requests_non_consuming_or_retryable"])
        consumption = self.result["consumption"]
        self.assertTrue(consumption["attempt_consumed"])
        self.assertTrue(
            all(
                value is False
                for key, value in consumption.items()
                if key
                in {
                    "retry",
                    "rerun",
                    "resume",
                    "repair",
                    "substitute_verifier",
                    "source_substitution",
                    "reuse",
                    "unused_budgets_transfer_to_successor",
                }
            )
        )

    def test_every_scientific_or_protected_counter_is_zero(self) -> None:
        counters = self.result["operation_counters"]
        self.assertEqual(counters["network_requests_total"], 3)
        self.assertEqual(counters["GitHub_control_plane_requests"], 3)
        for key, value in counters.items():
            if key not in {"network_requests_total", "GitHub_control_plane_requests"}:
                with self.subTest(key=key):
                    self.assertEqual(value, 0)
        claim = self.result["claim_boundary"]
        self.assertTrue(claim["control_plane_or_protocol_blocker_only"])
        self.assertTrue(claim["biological_null"] is False)
        self.assertTrue(claim["scientific_evidence_established"] is False)

    def test_frontier_supersedes_v27_and_binds_result(self) -> None:
        predecessor = PREDECESSOR.read_bytes()
        self.assertEqual(self.frontier["supersedes"], PREDECESSOR.relative_to(ROOT).as_posix())
        self.assertEqual(self.frontier["superseded_registry_bytes"], len(predecessor))
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(predecessor).hexdigest(),
        )
        self.assertEqual(self.frontier["superseded_registry_git_blob"], _git_blob(predecessor))
        for identity in self.frontier["bound_result_artifacts"]:
            _assert_identity(self, identity)
        self.assertIsNone(self.frontier["active_Tier_C_packet"])
        self.assertFalse(self.frontier["next_gate"]["FMSR1_E2E_v0_may_continue"])
        self.assertIsNone(self.frontier["next_gate"]["action_under_current_profile"])


if __name__ == "__main__":
    unittest.main()
