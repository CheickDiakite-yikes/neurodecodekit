import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/marc2_selection_sufficiency_repair_implementation.v0.json"


class Marc2SelectionSufficiencyRepairImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registration_proof_is_exact_and_green(self):
        proof = self.registry["registration_proof"]
        self.assertEqual(proof["commit"], "25205b1d2a1033cf3cefcab022c885025ac76928")
        self.assertEqual(proof["CI_run_id"], 32_670_514_251)
        self.assertEqual(proof["base_job_id"], 97_270_563_617)
        self.assertEqual(proof["optional_neuro_job_id"], 97_270_563_773)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_every_implementation_artifact_is_byte_exact(self):
        total = 0
        for row in self.registry["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            total += len(payload)
        self.assertEqual(total, self.registry["implementation_artifact_bytes"])
        self.assertEqual(
            len(self.registry["implementation_artifacts"]),
            self.registry["implementation_artifact_count"],
        )
        for row in self.registry["transitive_helper_bindings"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_qualification_and_surface_are_closed(self):
        qualification = self.registry["qualification"]
        self.assertEqual(qualification["qualification_invocations"], 1)
        self.assertFalse(qualification["qualification_may_be_repeated"])
        self.assertEqual(qualification["paths"], 40)
        self.assertEqual(qualification["accepted_paths"], 20)
        self.assertEqual(qualification["direct_refusals_passed"], 101)
        surface = self.registry["surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify"])
        self.assertFalse(surface["private_executor_available"])
        self.assertEqual(surface["private_or_Git_ignored_path_constants"], 0)
        self.assertTrue(surface["standard_library_only"])

    def test_claim_and_next_gate_do_not_overreach(self):
        boundary = self.registry["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        self.assertFalse(boundary["real_cohort_established"])
        self.assertFalse(boundary["neural_payload_accessed"])
        self.assertFalse(boundary["decoding_performance_established"])
        gate = self.registry["next_gate"]
        self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
        self.assertFalse(gate["generated_lane_remotely_closed_now"])
        self.assertFalse(gate["terminal_private_read_authorized"])


if __name__ == "__main__":
    unittest.main()
