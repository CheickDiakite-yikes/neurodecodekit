import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_selection_boundary_firewall_contract.v0.json"


class Marc2SelectionBoundaryFirewallPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_fixed_inputs_are_exact(self):
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), 12)
        total = 0
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["role"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                row["sha256"],
                row["role"],
            )
            total += len(payload)
        self.assertEqual(total, 256_934)
        self.assertEqual(total, self.contract["fixed_input_bytes"])

    def test_green_result_anchor_is_exact(self):
        proof = self.contract["result_proof_anchor"]
        self.assertEqual(
            proof["commit"],
            "a873f1a2ac796d5616339c7827b11af2a02bc63c",
        )
        self.assertEqual(proof["CI_run_id"], 32_602_610_854)
        self.assertEqual(proof["base_job_id"], 97_103_071_419)
        self.assertEqual(proof["optional_neuro_job_id"], 97_103_071_353)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["observed_route"], "MARC2VR24P-R2")
        self.assertFalse(proof["private_source_reopened_by_registration"])

    def test_layered_invariants_are_frozen(self):
        layers = self.contract["selection_boundary_layers"]
        self.assertEqual(layers["source_inventory_rows"], 1_227)
        self.assertEqual(layers["regular_file_rows"], 1_025)
        self.assertEqual(layers["directory_rows"], 202)
        self.assertEqual(layers["eligible_bundle_total"], 195)
        self.assertEqual(layers["selected_subjects"], 16)
        self.assertEqual(layers["selected_run_bundles"], 96)
        self.assertEqual(layers["selected_core_members"], 384)
        self.assertTrue(layers["validate_all_rows_before_filter"])
        self.assertTrue(layers["exact_eligible_distribution_is_hard_gate"])
        self.assertTrue(layers["public_238_total_is_warning_after_eligibility"])
        self.assertFalse(layers["unknown_bundle_count_is_globally_accepted"])

    def test_generated_matrix_is_exact(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(matrix["case_count"], 10)
        self.assertEqual(matrix["paths"], 40)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(
            matrix["expected_route_counts"],
            {
                "MARC2VR25A-G1": 4,
                "MARC2VR25A-G2": 16,
                "MARC2VR25A-R1": 12,
                "MARC2VR25A-R2": 4,
                "MARC2VR25A-R3": 4,
            },
        )
        accepted = [
            row for row in matrix["cases"] if row["expected_route"].endswith(("G1", "G2"))
        ]
        self.assertEqual(len(accepted), 5)
        self.assertTrue(matrix["accepted_selection_identity_must_match"])
        self.assertTrue(matrix["source_objects_must_remain_byte_identical"])

    def test_warning_does_not_expose_count(self):
        firewall = self.contract["aggregate_output_firewall"]
        self.assertEqual(
            firewall["count_compatibility_field"],
            "full_source_bundle_count_matches_public",
        )
        self.assertFalse(firewall["observed_bundle_count_allowed"])
        self.assertFalse(firewall["difference_direction_or_magnitude_allowed"])
        self.assertFalse(firewall["participant_or_selection_identity_allowed"])

    def test_caps_and_authority_are_strict(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertLessEqual(caps["generated_input_bytes"], 40 * 1024**2)
        self.assertLess(caps["peak_RSS_bytes"], 257 * 1024**2)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        self.assertTrue(
            all(
                value is False
                for value in self.contract["authorization_state"].values()
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )

    def test_scientific_ceiling_remains_none(self):
        claim = self.contract["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        for key, value in claim.items():
            if key not in {"engineering_capability_sought", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
