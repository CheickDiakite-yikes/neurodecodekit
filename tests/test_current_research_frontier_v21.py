import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v21.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v20.json"
REQUEST = ROOT / "registries/fresh_motor_source_identity_witness_authorization_request.v0.json"


class CurrentResearchFrontierV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_predecessor_identity_is_exact(self) -> None:
        payload = PREDECESSOR.read_bytes()
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(), self.frontier["superseded_registry_sha256"]
        )

    def test_packet_pointer_and_closed_authority_match(self) -> None:
        packet = self.frontier["proposed_packet"]
        self.assertEqual(packet["packet_id"], self.request["packet_id"])
        self.assertEqual(packet["official_index_profiles"], len(self.request["index_profiles"]))
        self.assertEqual(
            packet["root_request_identities"],
            len(self.request["frozen_discovery_plan"]["root_request_identities"]),
        )
        self.assertFalse(packet["grants_authority"])
        self.assertIsNone(self.frontier["active_Tier_C_packet"])
        self.assertFalse(self.frontier["next_gate"]["network_request_authorized_now"])
        self.assertTrue(
            all(
                value is False
                for key, value in self.frontier["operation_authority_now"].items()
                if key != "commit_push_and_CI_for_this_all_false_packet"
            )
        )

    def test_route_reaches_discovery_and_frozen_score_without_claim_upgrade(self) -> None:
        route = self.frontier["ordered_route_after_packet_exact_green"]
        self.assertIn("run_one_consumed_same_process_CI_gated_five_index_witness", route)
        self.assertIn("run_one_complete_or_park_discovery", route)
        self.assertIn(
            "stage_one_candidate_source_to_frozen_score_work_order_if_exactly_one_source_qualifies",
            route,
        )
        packet_index = route.index("prepare_all_false_D1_packet_only_after_WITNESS_COMPLETE")
        decision_index = route.index(
            "commit_push_and_green_separate_D1_authority_bearing_decision"
        )
        discovery_index = route.index("run_one_complete_or_park_discovery")
        self.assertLess(packet_index, decision_index)
        self.assertLess(decision_index, discovery_index)
        self.assertIn("obtain_fresh_D1_packet_bound_maintainer_words", route)
        self.assertTrue(all(value is False for value in self.frontier["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
