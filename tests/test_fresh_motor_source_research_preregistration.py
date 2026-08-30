from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries/fresh_motor_source_research_contract.v0.json"
DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_RESEARCH_PREREGISTRATION.md"
FRONTIER_V8 = ROOT / "registries/current_research_frontier.v8.json"
NPA1_PROOF = (
    ROOT / "registries/neural_payload_admission_generated_qualification_proof.v0.json"
)
LEDGER = ROOT / "registries/scientific_knowledge_ledger.v0.json"


class FreshMotorSourceResearchPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_protocol_is_all_false_and_selects_no_candidate(self) -> None:
        self.assertEqual(self.contract["protocol_id"], "FMSR1-v0")
        self.assertIn("all_authorities_false", self.contract["status"])
        self.assertIsNone(self.contract["scientific_lane"]["candidate_selected"])
        self.assertIsNone(self.contract["scientific_lane"]["active_Tier_C_lane"])
        for key, value in self.contract["operation_authority"].items():
            self.assertFalse(value, key)
        for key, value in self.contract["operation_counters"].items():
            self.assertEqual(value, 0, key)

    def test_proof_anchors_are_exact(self) -> None:
        anchors = self.contract["proof_anchors"]
        self.assertEqual(
            anchors["current_frontier"]["sha256"],
            hashlib.sha256(FRONTIER_V8.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            anchors["NPA1_G_proof"]["sha256"],
            hashlib.sha256(NPA1_PROOF.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            anchors["scientific_knowledge_ledger"]["sha256"],
            "4aa0fbb664cd9a0f6e51a59f7ea31af1b3a34eaef0679cc2c4ec92acc4cfd8cd",
        )
        proof = anchors["NPA1_G_proof"]
        self.assertEqual(
            proof["closeout_commit"],
            "2ec3d4b2b7b8c51f246e948ce9cbc9d667cecfb5",
        )
        self.assertEqual(proof["CI_run_id"], 33_285_776_358)
        self.assertEqual(proof["base_python_job_id"], 99_188_620_896)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 99_188_621_003)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_lane_and_hard_gates_cannot_be_rescued(self) -> None:
        lane = self.contract["scientific_lane"]
        self.assertEqual(lane["domain"], "motor_task_EEG")
        self.assertFalse(lane["communication_or_language_source_can_satisfy_lane"])
        gates = self.contract["noncompensatory_hard_gates"]
        self.assertEqual(gates["minimum_complete_participants"], 10)
        self.assertTrue(gates["recorded_EOG_required_for_every_selected_participant"])
        self.assertTrue(
            gates["task_relevant_EMG_required_for_every_selected_participant"]
        )
        self.assertFalse(gates["kinematics_can_replace_EMG_for_full_confirmation"])
        self.assertTrue(gates["named_EEG_channels_and_geometry_required"])
        self.assertFalse(gates["participant_dropping_for_storage_allowed"])
        self.assertFalse(gates["weighted_score_may_rescue_failed_gate"])
        self.assertFalse(gates["unknown_counts_as_pass"])

    def test_storage_has_headroom_inside_maintainer_ceiling(self) -> None:
        gates = self.contract["noncompensatory_hard_gates"]
        self.assertEqual(gates["selected_source_payload_cap_bytes"], 16 * 2**30)
        self.assertEqual(gates["total_incremental_disk_cap_bytes"], 20 * 2**30)
        self.assertLess(
            gates["selected_source_payload_cap_bytes"],
            gates["total_incremental_disk_cap_bytes"],
        )

    def test_partial_routes_cannot_be_promoted(self) -> None:
        routes = self.contract["deterministic_routes"]
        self.assertTrue(
            routes["FULL_CONFIRMATION"][
                "eligible_for_later_source_specific_metadata_packet"
            ]
        )
        for route in ("PARTIAL_CONTROL", "MECHANISTIC_BRIDGE", "ENGINEERING_ONLY", "PARK"):
            self.assertFalse(routes[route]["eligible_for_flagship_promotion"], route)
        self.assertEqual(
            routes["no_full_confirmation_candidate_outcome"],
            "NO_QUALIFYING_SOURCE",
        )
        self.assertFalse(routes["criteria_may_be_weakened_after_no_candidate"])

    def test_consumed_surfaces_are_excluded(self) -> None:
        excluded = self.contract["freshness"]["excluded_consumed_source_ids"]
        for source in (
            "BNCI-2014-001__NEMAR-nm000139",
            "DREYER-DATASET-A__NEMAR-nm000250",
            "OFNER-2017__NEMAR-nm000173",
            "IACKD__OPENNEURO-ds006840",
            "PHYSIONET-EEGMMIDB",
        ):
            self.assertIn(source, excluded)
        self.assertFalse(
            self.contract["freshness"][
                "consumed_payload_target_prediction_score_or_marker_reuse_allowed"
            ]
        )

    def test_claim_boundary_and_document_are_explicit(self) -> None:
        for key, value in self.contract["claim_boundary"].items():
            self.assertFalse(value, key)
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("NO_QUALIFYING_SOURCE", text)
        self.assertIn("no source selected", text.lower())

    def test_knowledge_ledger_records_registration_without_claim(self) -> None:
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        evidence = {row["id"]: row for row in ledger["evidence"]}
        self.assertIn("EVID-FMSR1-REGISTRATION", evidence)
        self.assertIn(
            "selects no source",
            evidence["EVID-FMSR1-REGISTRATION"]["limitations"],
        )
        self.assertEqual(ledger["operation_boundary"]["FMSR1_source_candidates_selected"], 0)
        self.assertEqual(ledger["operation_boundary"]["FMSR1_metadata_network_requests"], 0)


if __name__ == "__main__":
    unittest.main()
