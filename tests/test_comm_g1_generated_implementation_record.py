from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / "comm_g1_generated_implementation.v0.json"
DOC = ROOT / "docs" / "COMM_G1_GENERATED_IMPLEMENTATION.md"


class CommG1GeneratedImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_every_bound_artifact_is_exact(self) -> None:
        for artifact in self.value["artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(artifact["bytes"], len(payload), artifact["path"])
            self.assertEqual(
                artifact["sha256"], hashlib.sha256(payload).hexdigest(), artifact["path"]
            )

    def test_registration_and_amendment_were_green_first(self) -> None:
        for key in ("registration_green_proof", "amendment_green_proof"):
            proof = self.value[key]
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertEqual(len(proof["commit"]), 40)
            self.assertGreater(proof["CI_run_id"], 0)

    def test_development_measurement_is_bounded_and_exactly_scheduled(self) -> None:
        measurement = self.value["development_generated_measurement"]
        self.assertFalse(measurement["official_qualification"])
        self.assertEqual(measurement["total_parameter_update_fits"], 60)
        self.assertEqual(measurement["prediction_sets"], 60)
        self.assertEqual(measurement["prediction_rows"], 1440)
        self.assertEqual(measurement["post_target_updates"], 0)
        self.assertGreaterEqual(measurement["adversarial_refusals"], 30)
        self.assertLessEqual(measurement["runtime_seconds"], 180)
        self.assertLessEqual(measurement["peak_process_tree_RSS_bytes"], 512 << 20)
        self.assertLessEqual(measurement["generated_input_bytes"], 32 << 20)
        self.assertLessEqual(measurement["public_output_bytes"], 1 << 20)
        self.assertTrue(measurement["producer_causal"])
        self.assertFalse(measurement["end_to_end_latency_measured"])
        self.assertEqual(measurement["scientific_value"], "none_generated_engineering_only")

    def test_official_qualification_remains_unconsumed(self) -> None:
        qualification = self.value["official_generated_qualification"]
        self.assertFalse(qualification["executed"])
        self.assertEqual(qualification["invocations_remaining"], 1)
        self.assertFalse(qualification["rerun_allowed"])

    def test_all_real_and_claim_counters_are_zero(self) -> None:
        self.assertTrue(all(value == 0 for value in self.value["access_counters"].values()))
        gate = self.value["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertTrue(gate["all_authority_flags_false"])
        self.assertFalse(gate["changed_by_this_implementation"])

    def test_document_states_engineering_and_scientific_boundaries(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for phrase in (
            "generated-only control plane",
            "NumPy and scikit-learn remain optional",
            "60-update model schedule",
            "35",
            "not the official",
            "does not establish communication decoding",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
