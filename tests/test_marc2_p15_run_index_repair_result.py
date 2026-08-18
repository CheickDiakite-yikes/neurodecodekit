import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_p15_run_index_repair_result.v0.json"


class Marc2P15RunIndexRepairResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_and_proof_posture_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_p15_run_index_repair_result",
        )
        self.assertEqual(self.result["lane_id"], "MARC2-VR12A")
        self.assertEqual(self.result["route"], "MARC2VR12A-G1")
        self.assertEqual(
            self.result["status"],
            "generated_only_result_remote_implementation_green_proof_closeout_pending",
        )
        proof = self.result["remote_implementation_proof"]
        self.assertEqual(
            proof["commit"], "873484aaf270bc5b1499e4b0449c9e8ef138c623"
        )
        self.assertEqual(proof["CI_run_id"], 32_170_217_284)
        self.assertEqual(proof["base_python_job_id"], 95_819_297_085)
        self.assertEqual(proof["optional_neuro_job_id"], 95_819_297_010)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["generated_qualification_repeated_for_closeout"])
        self.assertFalse(proof["private_operation_performed_for_closeout"])

    def test_contract_and_registration_proof_are_bound(self):
        contract = self.result["contract"]
        self.assertEqual(contract["bytes"], 9681)
        self.assertEqual(
            contract["sha256"],
            "a6cd01e79813f79dfd7b54ee6c2d21ffb82e984b6230434127b936c513cf3f1e",
        )
        proof = self.result["green_registration_proof"]
        self.assertEqual(
            proof["commit"], "5107eb3d714f7713a216b9ad4e21c06300cd8c21"
        )
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_every_implementation_artifact_binding_matches(self):
        for binding in self.result["artifact_bindings"].values():
            path = ROOT / binding["path"]
            payload = path.read_bytes()
            with self.subTest(path=binding["path"]):
                self.assertEqual(len(payload), binding["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])

    def test_generated_matrix_and_semantic_selection_are_exact(self):
        generated = self.result["generated_qualification"]
        self.assertEqual(generated["success_paths"], 12)
        self.assertEqual(generated["replays"], 2)
        self.assertEqual(generated["selected_subjects"], 16)
        self.assertEqual(generated["selected_run_bundles"], 96)
        self.assertEqual(generated["selected_core_members"], 384)
        self.assertEqual(
            generated["semantic_cohort_sha256"],
            "254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba",
        )
        self.assertEqual(generated["distinct_raw_source_hashes"], 3)
        self.assertEqual(generated["distinct_source_exact_selected_name_hashes"], 3)

    def test_refusal_summary_is_complete(self):
        generated = self.result["generated_qualification"]
        self.assertEqual(generated["direct_refusals"], 36)
        self.assertEqual(
            generated["required_classes_preserved"],
            ["P15", "P16", "P18", "P19"],
        )
        self.assertEqual(sum(generated["refusal_route_counts"].values()), 36)

    def test_measurements_are_bounded_and_complete(self):
        measured = self.result["measurements"]
        self.assertLessEqual(measured["generated_input_bytes"], 16 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertLessEqual(measured["runtime_seconds"], 30)
        self.assertLessEqual(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(
            (measured["CPU_threads"], measured["workers"], measured["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_forbidden_operation_counters_are_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )

    def test_result_contains_no_private_identity_or_payload(self):
        text = RESULT_PATH.read_text(encoding="utf-8")
        for forbidden in (
            '"member_name"',
            '"subject_id"',
            '"participant_id"',
            '"target"',
            '"targets"',
            '"prediction"',
            '"predictions"',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_private_confirmation_and_scientific_work_remain_closed(self):
        gate = self.result["next_gate"]
        self.assertFalse(gate["Tier_C_confirmation_packet_eligible_now"])
        self.assertFalse(gate["private_confirmation_authorized"])
        self.assertFalse(gate["FW2_or_CIL1_authorized"])

    def test_claim_boundary_has_two_distinct_sentences(self):
        boundary = self.result["claim_boundary"]
        self.assertTrue(boundary["engineering_capability_added"].endswith("."))
        self.assertTrue(boundary["scientific_claim_not_established"].endswith("."))
        self.assertNotEqual(
            boundary["engineering_capability_added"],
            boundary["scientific_claim_not_established"],
        )


if __name__ == "__main__":
    unittest.main()
