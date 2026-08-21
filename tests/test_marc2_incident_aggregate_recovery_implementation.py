import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT / "registries/marc2_incident_aggregate_recovery_implementation.v0.json"
)


class Marc2IncidentAggregateRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    def test_green_decision_and_interface_are_exact(self):
        proof = self.record["green_decision_proof"]
        self.assertEqual(proof["commit"], "60b97ea6c9715b651c17bb6d797c1f02c10ba9e2")
        self.assertEqual(proof["CI_run_id"], 32_444_425_790)
        self.assertEqual(proof["base_python_job_id"], 96_661_242_381)
        self.assertEqual(proof["optional_neuro_job_id"], 96_661_242_496)
        self.assertTrue(proof["both_required_jobs_green"])
        interface = self.record["interface"]
        self.assertEqual(interface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(interface["fixed_path_execute"])
        self.assertTrue(interface["explicit_one_shot_arming_required"])
        self.assertFalse(interface["generic_path_or_output_override_allowed"])

    def test_owned_artifacts_match_exact_bytes_and_hashes(self):
        rows = self.record["owned_artifacts"]
        self.assertEqual(len(rows), 5)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_generated_qualification_is_exact_and_bounded(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["route"], "MARC2VR14P-G1")
        self.assertEqual((result["cases"], result["orders"], result["replays"]), (8, 2, 2))
        self.assertEqual(result["paths"], 32)
        self.assertEqual(result["route_count_each"], 4)
        self.assertEqual(result["generated_report_validations"], 33)
        self.assertEqual(result["direct_refusals"], 89)
        self.assertEqual(result["generated_input_bytes"], 50_370)
        self.assertEqual(result["retained_output_bytes"], 0)
        self.assertLess(result["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(result["runtime_seconds"], 30)

    def test_real_and_forbidden_operations_are_zero(self):
        counters = self.record["operation_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()))
        self.assertFalse(self.record["aggregate_execution_authorized_now"])
        self.assertIsNone(self.record["remote_implementation_proof"])

    def test_proof_gate_and_claim_boundary_remain_closed(self):
        gate = self.record["next_gate"]
        claims = self.record["claim_boundary"]
        self.assertTrue(gate["implementation_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["separate_proof_closeout_green_required"])
        self.assertFalse(gate["aggregate_report_read_authorized_now"])
        self.assertFalse(gate["FW2_or_CIL1_execution_authorized"])
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["neural_effect"])
        self.assertFalse(claims["decoding_accuracy"])


if __name__ == "__main__":
    unittest.main()
