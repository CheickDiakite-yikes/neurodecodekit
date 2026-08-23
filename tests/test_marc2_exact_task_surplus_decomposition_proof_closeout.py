import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = json.loads(
    (ROOT / "registries/marc2_exact_task_surplus_decomposition_implementation.v0.json").read_text(
        encoding="utf-8"
    )
)
RESULT = json.loads(
    (ROOT / "registries/marc2_exact_task_surplus_decomposition_result.v0.json").read_text(
        encoding="utf-8"
    )
)
DOC = (ROOT / "docs/MARC_2_EXACT_TASK_SURPLUS_DECOMPOSITION_PROOF_CLOSEOUT.md").read_text(
    encoding="utf-8"
)

EXPECTED_PROOF = {
    "commit": "f698a10d2649bd65f7b819531cbf3d89cd3f0c0a",
    "CI_run_id": 32_654_295_221,
    "base_python_job_id": 97_230_546_153,
    "optional_neuro_job_id": 97_230_546_048,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_invocations": 1,
    "preproof_implementation_registry_bytes": 5_521,
    "preproof_implementation_registry_sha256": (
        "a616975b3df521b800fbb2a32ac2ffa7c8ad9f2b03496cf9b4503809d7d2005a"
    ),
    "preproof_result_registry_bytes": 3_996,
    "preproof_result_registry_sha256": (
        "23c575f3662e5a51cd4f549f4bdbcbf482b8929a7c31c090dfddc3ee512632f5"
    ),
    "implementation_module_Git_blob": "792da996a5d5116079d166811fc7735be3275729",
    "behavior_test_Git_blob": "603d5c167e1918cd1f4aff6460760bdf8cab3db4",
    "registration_test_Git_blob": "2fa8edb8808adeea023675deac977c317f5fa40f",
    "result_record_test_Git_blob": "a7d7b85f719238b3556387793a99fcd7d08f15b2",
    "implementation_document_Git_blob": "0d7d32c4455563938181314905bf15d41e667c6c",
    "contract_Git_blob": "c5d0aeb60eea71e140aa8c4115c6d8033fd79335",
    "preproof_implementation_registry_Git_blob": ("ee25696b98987a87f8f2aa8103af1b9ed5bc83f3"),
    "preproof_result_registry_Git_blob": ("4286c92f91a28e4ea4283ed34a74dd43f4ce3bfa"),
    "result_test_transition_hardening_only": True,
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class ExactTaskSurplusDecompositionProofCloseoutTests(unittest.TestCase):
    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(IMPLEMENTATION["remote_implementation_proof"], EXPECTED_PROOF)
        self.assertEqual(RESULT["remote_implementation_proof"], EXPECTED_PROOF)

    def test_closeout_binds_all_preproof_git_blobs(self):
        for key, value in EXPECTED_PROOF.items():
            if key.endswith("Git_blob"):
                with self.subTest(key=key):
                    self.assertIn(value, DOC)

    def test_qualification_and_private_operation_are_not_repeated(self):
        self.assertEqual(RESULT["qualification_invocations"], 1)
        self.assertFalse(RESULT["qualification_may_be_repeated"])
        self.assertFalse(EXPECTED_PROOF["generated_qualification_repeated_for_proof_closeout"])
        self.assertEqual(EXPECTED_PROOF["private_operations_during_proof_closeout"], 0)
        self.assertTrue(all(value == 0 for value in RESULT["operation_counters"].values()))

    def test_closeout_has_delayed_effect(self):
        for record in (IMPLEMENTATION, RESULT):
            gate = record["next_gate"]
            self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
            self.assertFalse(gate["generated_lane_remotely_closed_now"])
            self.assertTrue(gate["generated_lane_remotely_closed_after_exact_closeout_green"])
            self.assertFalse(gate["qualification_may_be_repeated"])
            if record is IMPLEMENTATION:
                self.assertFalse(gate["private_execution_or_consumed_lane_reinspection_authorized"])
            else:
                self.assertFalse(gate["private_discriminator_or_read_authorized"])

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("fresh", DOC)


if __name__ == "__main__":
    unittest.main()
