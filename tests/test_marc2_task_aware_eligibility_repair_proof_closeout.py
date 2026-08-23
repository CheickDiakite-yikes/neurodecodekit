import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = json.loads(
    (
        ROOT
        / "registries/marc2_task_aware_eligibility_repair_implementation.v0.json"
    ).read_text(encoding="utf-8")
)
RESULT = json.loads(
    (
        ROOT / "registries/marc2_task_aware_eligibility_repair_result.v0.json"
    ).read_text(encoding="utf-8")
)
DOC = (
    ROOT / "docs/MARC_2_TASK_AWARE_ELIGIBILITY_REPAIR_PROOF_CLOSEOUT.md"
).read_text(encoding="utf-8")

EXPECTED_PROOF = {
    "commit": "599e22de356df29873eb154f320b89aca125777a",
    "CI_run_id": 32_644_887_730,
    "base_python_job_id": 97_207_526_045,
    "optional_neuro_job_id": 97_207_525_966,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_invocations": 1,
    "preproof_implementation_registry_bytes": 5_197,
    "preproof_implementation_registry_sha256": (
        "408de8b8fe35dbbe94a64cc1fad9ef9282b1adfe7eff28952db20d5a4169e763"
    ),
    "preproof_result_registry_bytes": 4_071,
    "preproof_result_registry_sha256": (
        "f87d2fe0372d57de4b4b73087c19de3188c4fb09fe793faea594c4adf392db28"
    ),
    "implementation_module_Git_blob": "534b1f923bcc5dd762c8e569a2f04affb3257fb1",
    "behavior_test_Git_blob": "ca96f7ecf0a6834a82f5d69ebd4df3249d3b8f64",
    "registration_test_Git_blob": "e2f35cae4d513dad02da85e68496d3e6ddce3124",
    "result_record_test_Git_blob": "4c7890d794510256fe4863d6fb82681f5ac4a83a",
    "implementation_document_Git_blob": "255da23b3efa388c079d3f885a49c8df6ddfdf50",
    "contract_Git_blob": "f77f61620b5736711d61d3f846442c35bb8068b1",
    "preproof_implementation_registry_Git_blob": (
        "20ac45ffd42afeee0a163c4911b08231fa803a97"
    ),
    "preproof_result_registry_Git_blob": "4af790dd87dea32f17baf4d522a2cf85fe559f37",
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2TaskAwareEligibilityRepairProofCloseoutTests(unittest.TestCase):
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
        self.assertFalse(
            EXPECTED_PROOF["generated_qualification_repeated_for_proof_closeout"]
        )
        self.assertEqual(EXPECTED_PROOF["private_operations_during_proof_closeout"], 0)
        self.assertTrue(all(value == 0 for value in RESULT["operation_counters"].values()))

    def test_closeout_has_delayed_effect(self):
        for record in (IMPLEMENTATION, RESULT):
            gate = record["next_gate"]
            self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
            self.assertFalse(gate["generated_lane_remotely_closed_now"])
            self.assertTrue(
                gate["generated_lane_remotely_closed_after_exact_closeout_green"]
            )
            self.assertFalse(gate["qualification_may_be_repeated"])
            self.assertFalse(
                gate["private_execution_or_consumed_lane_reinspection_authorized"]
            )

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("cannot", DOC)
        self.assertIn("fresh", DOC)


if __name__ == "__main__":
    unittest.main()
