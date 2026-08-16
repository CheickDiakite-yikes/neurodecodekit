import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc2_machine_readiness_result.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_MACHINE_READINESS_RESULT.md"


class Marc2MachineReadinessResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_route_and_proof_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_machine_readiness_result",
        )
        self.assertEqual(self.result["lane_id"], "MARC2-VR4")
        self.assertEqual(self.result["route"], "MARC2RDY-G1")
        proof = self.result["green_implementation_proof"]
        self.assertEqual(proof["commit"], "9fdda316441fef4f245544c90dc0a373993140e0")
        self.assertEqual(proof["CI_run_id"], 31967145837)
        self.assertEqual(proof["base_python_job_id"], 95213934048)
        self.assertEqual(proof["optional_neuro_job_id"], 95213934126)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_three_samples_pass_exact_limits(self):
        self.assertEqual(len(self.result["samples"]), 3)
        self.assertTrue(all(sample["passing"] for sample in self.result["samples"]))
        self.assertLessEqual(
            max(sample["normalized_one_minute_load"] for sample in self.result["samples"]),
            1.0,
        )
        self.assertLess(
            max(sample["process_peak_RSS_bytes"] for sample in self.result["samples"]),
            256 * 1024**2,
        )
        self.assertGreaterEqual(
            min(sample["free_disk_bytes"] for sample in self.result["samples"]),
            15 * 1024**3,
        )

    def test_certificate_is_small_mode_0600_and_transient(self):
        certificate = self.result["certificate"]
        self.assertEqual(certificate["mode"], "0600")
        self.assertEqual(certificate["bytes"], 4551)
        self.assertEqual(
            certificate["sha256"],
            "5c268ffaefe6e557ace92214c6ec3bab6db29d0a89dee4c83ebd94dbf07b522e",
        )
        self.assertTrue(certificate["ready_at_closeout"])
        self.assertTrue(certificate["transient_not_future_private_authority"])

    def test_every_private_or_scientific_counter_is_zero(self):
        counters = self.result["access_counters"]
        allowed_nonzero = {"machine_readiness_checks": 3, "readiness_certificates": 1}
        for key, value in counters.items():
            self.assertEqual(value, allowed_nonzero.get(key, 0), key)

    def test_all_acceptance_gates_passed(self):
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_next_gate_stops_before_private_FW2_and_CIL1(self):
        gate = self.result["next_gate"]
        self.assertTrue(gate["result_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["separate_all_false_Tier_C_structural_packet_after_green"])
        self.assertTrue(gate["fresh_packet_bound_maintainer_decision_required"])
        self.assertFalse(gate["private_structural_pass_authorized"])
        self.assertFalse(gate["real_cohort_identity_available"])
        self.assertFalse(gate["FW2_or_CIL1_eligible"])

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("No private or cohort path was resolved", text)


if __name__ == "__main__":
    unittest.main()
