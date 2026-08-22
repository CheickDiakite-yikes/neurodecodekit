import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_selection_boundary_firewall_result.v0.json"
)
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_selection_boundary_firewall_implementation.v0.json"
)


class Marc2SelectionBoundaryFirewallResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )

    def test_result_route_and_matrix_are_exact(self):
        self.assertEqual(self.result["route"], "MARC2VR25A-G1")
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 40)
        self.assertEqual(matrix["accepted_paths"], 20)
        self.assertEqual(
            matrix["route_counts"],
            {
                "MARC2VR25A-G1": 4,
                "MARC2VR25A-G2": 16,
                "MARC2VR25A-R1": 12,
                "MARC2VR25A-R2": 4,
                "MARC2VR25A-R3": 4,
            },
        )
        self.assertTrue(matrix["accepted_semantic_identity_matches"])
        self.assertTrue(matrix["accepted_split_reservation_identity_matches"])
        self.assertEqual(matrix["eligible_drift_successes"], 0)
        self.assertEqual(matrix["unknown_participant_successes"], 0)
        self.assertEqual(matrix["incomplete_companion_successes"], 0)

    def test_firewall_preserves_exact_selection_boundary(self):
        firewall = self.result["firewall"]
        self.assertTrue(firewall["all_rows_validated_before_filter"])
        self.assertTrue(firewall["all_recognized_bundles_complete_before_filter"])
        self.assertEqual(firewall["exact_eligible_bundle_total"], 195)
        self.assertTrue(firewall["exact_eligible_distribution_required"])
        self.assertTrue(
            firewall["known_ineligible_quarantined_before_candidate_construction"]
        )
        self.assertEqual(firewall["selected_subjects"], 16)
        self.assertEqual(firewall["selected_run_bundles"], 96)
        self.assertEqual(firewall["selected_core_members"], 384)
        self.assertFalse(firewall["observed_full_total_exposed"])

    def test_measurements_and_counters_are_bounded(self):
        measured = self.result["measurements"]
        self.assertLessEqual(measured["generated_input_bytes"], 40 * 1024**2)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["temporary_peak_bytes"], 2 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )

    def test_implementation_artifacts_are_exact(self):
        for row in self.implementation["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["role"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                row["sha256"],
                row["role"],
            )
        self.assertIsNone(self.implementation["remote_implementation_proof"])
        self.assertFalse(self.implementation["proof_transition_ready"])

    def test_scientific_ceiling_remains_none(self):
        claim = self.result["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        for key, value in claim.items():
            if key not in {"engineering_capability_added", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
