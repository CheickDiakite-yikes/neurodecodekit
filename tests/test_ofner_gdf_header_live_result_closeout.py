from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/ofner_gdf_header_live_result.v0.json"
CLOSEOUT = ROOT / "registries/ofner_gdf_header_live_result_closeout.v0.json"
FRONTIER = ROOT / "registries/current_research_frontier.v6.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v5.json"
ACTIVATION = ROOT / "registries/ofner_gdf_header_live_activation.v0.json"
LEDGER = ROOT / "registries/scientific_knowledge_ledger.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


class OfnerGDFHeaderLiveResultCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.closeout = json.loads(CLOSEOUT.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_public_result_binding_is_exact(self) -> None:
        binding = self.closeout["bound_public_result"]
        self.assertEqual(binding["bytes"], RESULT.stat().st_size)
        self.assertEqual(binding["sha256"], _sha256(RESULT))
        self.assertEqual(binding["git_blob"], _git_blob(RESULT))
        self.assertEqual(self.result["route"], "OFNER-H0-TRANSPORT")
        self.assertEqual(self.result["refusal_code"], "OHL-TRANSPORT")
        self.assertEqual(self.result["status"], "parked")

    def test_activation_and_frontier_bindings_are_exact(self) -> None:
        activation = self.closeout["green_activation"]
        self.assertEqual(activation["activation_registry_sha256"], _sha256(ACTIVATION))
        self.assertEqual(activation["activation_registry_bytes"], ACTIVATION.stat().st_size)
        self.assertEqual(activation["activation_registry_git_blob"], _git_blob(ACTIVATION))
        frontier = self.closeout["current_frontier"]
        self.assertEqual(frontier["bytes"], FRONTIER.stat().st_size)
        self.assertEqual(frontier["sha256"], _sha256(FRONTIER))
        self.assertEqual(frontier["git_blob"], _git_blob(FRONTIER))
        self.assertEqual(frontier["superseded_registry_sha256"], _sha256(PREDECESSOR))

    def test_consumed_failure_is_localized_without_invention(self) -> None:
        counters = self.closeout["operation_counters"]
        self.assertEqual(counters["manifest_GET_requests"], 1)
        self.assertEqual(counters["manifest_body_bytes"], 1_352_270)
        self.assertEqual(counters["GDF_range_GET_requests"], 1)
        self.assertEqual(counters["GDF_body_bytes"], 0)
        self.assertEqual(counters["fixed_header_reads"], 0)
        self.assertEqual(counters["fixed_header_semantic_parses"], 0)
        self.assertFalse(self.closeout["failure_localization"]["more_specific_cause_may_be_claimed"])
        self.assertFalse(self.closeout["failure_localization"]["biological_null"])

    def test_no_rerun_authority_or_scientific_claim_exists(self) -> None:
        result = self.closeout["result"]
        self.assertTrue(result["invocation_consumed"])
        self.assertFalse(result["retry_allowed"])
        self.assertFalse(result["rerun_allowed"])
        self.assertFalse(result["repair_resume_substitute_or_reinterpret_allowed"])
        self.assertIsNone(self.frontier["active_lane_id"])
        self.assertTrue(
            all(value is False for value in self.frontier["operation_authority"].values())
        )
        self.assertFalse(self.closeout["claim_boundary"]["scientific_claim_established"])
        self.assertIsNone(self.ledger["operation_boundary"]["active_tier_c_packet"])

    def test_current_control_plane_names_v6_and_consumed_H0(self) -> None:
        expected = ("AGENTS.md", "README.md", "START_HERE.md", "docs/CODEX_HANDOFF.md")
        for relative in expected:
            text = (ROOT / relative).read_text(encoding="utf-8")[:14_000]
            self.assertIn("registries/current_research_frontier.v6.json", text, relative)
            self.assertIn("OFNER-H0-TRANSPORT", text, relative)


if __name__ == "__main__":
    unittest.main()
