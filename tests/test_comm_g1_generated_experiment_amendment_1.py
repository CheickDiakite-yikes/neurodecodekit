from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "COMM_G1_GENERATED_EXPERIMENT_AMENDMENT_1.md"
REGISTRY = ROOT / "registries" / "comm_g1_generated_experiment_amendment_1.v0.json"
CONTRACT = ROOT / "registries" / "comm_g1_generated_experiment_contract.v0.json"


class CommG1GeneratedExperimentAmendment1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_parent_contract_is_exact_and_remotely_green(self) -> None:
        parent = self.value["parent_registration"]
        payload = CONTRACT.read_bytes()
        self.assertEqual(parent["contract_bytes"], len(payload))
        self.assertEqual(parent["contract_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertTrue(parent["both_required_jobs_green"])
        self.assertEqual(parent["commit"], "286d42883a12a426c7ec9a2a13e4b859fa188e3b")

    def test_derangement_breaks_class_pairing_without_fixed_points(self) -> None:
        rule = self.value["corrected_derangement"]
        self.assertEqual(rule["data_scope"], "source_rows_only")
        self.assertEqual(rule["required_classes_per_group"], [0, 1, 2, 3])
        self.assertEqual(rule["fixed_points"], 0)
        self.assertEqual(
            sorted(rule["mapping"].values()),
            [0, 1, 2, 3],
        )
        for source_class in range(4):
            self.assertNotEqual(
                rule["mapping"][f"class_{source_class}_receives"], source_class
            )
        self.assertFalse(rule["held_out_rows_permuted"])
        self.assertFalse(rule["held_out_targets_read"])

    def test_schedule_and_claim_boundary_remain_unchanged(self) -> None:
        unchanged = self.value["unchanged"]
        self.assertEqual(unchanged["total_parameter_update_fits"], 60)
        self.assertEqual(unchanged["prediction_rows"], 1440)
        self.assertEqual(unchanged["reruns"], 0)
        self.assertEqual(unchanged["scientific_value"], "none_generated_engineering_only")
        self.assertTrue(all(value is False for value in self.value["authorization_state"].values()))
        self.assertTrue(all(value is False for value in self.value["claim_boundary"].values()))

    def test_active_tier_c_gate_is_unchanged(self) -> None:
        gate = self.value["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertTrue(gate["all_authority_flags_false"])
        self.assertFalse(gate["changed_by_this_amendment"])

    def test_document_explains_prospective_control_correction(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for phrase in (
            "class-preserving permutation",
            "No COMM-G1 implementation",
            "one-class cyclic rotation",
            "no fixed point",
            "held-out target",
            "scientific-claim authority remains false",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
