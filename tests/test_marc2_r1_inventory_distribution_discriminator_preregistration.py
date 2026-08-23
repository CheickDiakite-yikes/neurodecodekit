import ast
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc2_r1_inventory_distribution_discriminator_contract.v0.json"
)
DOC_PATH = (
    ROOT / "docs/MARC_2_R1_INVENTORY_DISTRIBUTION_DISCRIMINATOR_PREREGISTRATION.md"
)
VR2_PATH = (
    ROOT / "src/neurodecodekit/datasets/marc2_live_domain_eligibility_adapter.py"
)


class Marc2R1InventoryDistributionDiscriminatorPreregistrationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_schema_and_green_result_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR29A")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )
        proof = self.contract["result_proof"]
        self.assertEqual(
            proof["VR28P_result_commit"],
            "f2b396ed99196d2a5632251390097c6990a7d8d4",
        )
        self.assertEqual(proof["VR28P_result_CI_run_id"], 32_618_219_730)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["observed_route"], "MARC2VR28P-R1")
        self.assertFalse(
            proof["private_source_or_consumed_output_reinspected_by_registration"]
        )

    def test_all_fixed_inputs_match_exact_bytes_and_hashes(self):
        total = 0
        rows = self.contract["fixed_inputs"]
        self.assertEqual(len(rows), self.contract["fixed_input_count"])
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            total += len(payload)
        self.assertEqual(total, self.contract["fixed_input_bytes"])

    def test_exact_two_vr2_filter_refusal_sites_are_frozen(self):
        tree = ast.parse(VR2_PATH.read_text(encoding="utf-8"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_filter_and_validate_eligible"
        )
        reasons = []
        for node in ast.walk(function):
            if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
                continue
            if not isinstance(node.exc.func, ast.Name):
                continue
            if node.exc.func.id != "LiveDomainEligibilityRefusal":
                continue
            reason = node.exc.args[1]
            self.assertIsInstance(reason, ast.Constant)
            reasons.append(reason.value)
        self.assertEqual(
            reasons,
            [
                "filtered eligible total differs",
                "eligible participant-session counts differ",
            ],
        )
        self.assertEqual(self.contract["exact_R1_call_site_total"], 2)

    def test_generated_matrix_and_route_counts_are_frozen(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(len(matrix["cases"]), 8)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 32)
        self.assertEqual(matrix["required_VR25A_calls"], 32)
        self.assertEqual(matrix["required_R1_filter_discriminator_calls"], 16)
        self.assertEqual(
            matrix["expected_VR29A_route_counts"],
            {
                "MARC2VR29A-G1": 4,
                "MARC2VR29A-G2": 4,
                "MARC2VR29A-R1": 8,
                "MARC2VR29A-R2": 8,
                "MARC2VR29A-R3": 8,
            },
        )
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 70)

    def test_resources_and_authority_remain_generated_only(self):
        resources = self.contract["resource_limits"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertLessEqual(resources["generated_input_bytes"], 32 * 1024**2)
        self.assertEqual(resources["retained_output_bytes"], 0)
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["artifact_only_reads"])
        self.assertTrue(authorization["generated_fixture_creation"])
        self.assertTrue(
            all(
                value is False or value == 0
                for key, value in authorization.items()
                if key not in {"artifact_only_reads", "generated_fixture_creation"}
            )
        )
        self.assertTrue(
            all(
                value == 0
                for value in self.contract["registration_operation_counters"].values()
            )
        )

    def test_human_preregistration_preserves_claim_boundary(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("filtered eligible total differs", text)
        self.assertIn("eligible participant-session counts differ", text)
        self.assertIn("private executor", text)
        self.assertIn("Engineering capability proposed", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
