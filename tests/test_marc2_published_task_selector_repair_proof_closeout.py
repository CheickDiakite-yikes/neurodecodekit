import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_published_task_selector_repair_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_published_task_selector_repair_result.v0.json"
PROOF_DOC_PATH = (
    ROOT / "docs/MARC_2_PUBLISHED_TASK_SELECTOR_REPAIR_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "bf4d2b729ac948d32aa1c7b239d3c65a30f18017",
    "CI_run_id": 32_486_620_566,
    "base_python_job_id": 96_784_482_381,
    "optional_neuro_job_id": 96_784_482_602,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR20A-G1",
    "preproof_implementation_registry_bytes": 4_804,
    "preproof_implementation_registry_sha256": (
        "ad1c908d50f0232ed91921857e5d27212bb80b13fa22f9962ae94c2fdab4d0f2"
    ),
    "preproof_result_registry_bytes": 4_710,
    "preproof_result_registry_sha256": (
        "363aaf14bab5b8c964ff88be8d44e3551fdb17ddc2ec354d30358c030210906c"
    ),
    "implementation_module_Git_blob": "33cd5e52d186a768ce8dc706e163c8d5c3a2fc92",
    "behavior_test_Git_blob": "339d6d32da8cae2be2dd8672996d0bb6973701b6",
    "implementation_document_Git_blob": (
        "55583492ff4edba48c9c719cd83817d9d6f314c2"
    ),
    "result_document_Git_blob": "da0474cbfefca3d3f93d2d655d56a7ab8afafda6",
    "preproof_implementation_registry_Git_blob": (
        "dbdc7f039f42cd67f905002fb2a31d07933e367d"
    ),
    "preproof_result_registry_Git_blob": (
        "5de8fd23b827a5a574937224218182af827a88f0"
    ),
    "preproof_record_test_Git_blob": "599857a7f1ce3db3b98626102a49f25c6534fc57",
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2PublishedTaskSelectorRepairProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.document = PROOF_DOC_PATH.read_text(encoding="utf-8")

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.implementation["remote_implementation_proof"], EXPECTED_PROOF
        )
        self.assertEqual(self.result["remote_implementation_proof"], EXPECTED_PROOF)

    def test_closeout_binds_all_preproof_git_blobs(self):
        for key, value in EXPECTED_PROOF.items():
            if key.endswith("Git_blob"):
                with self.subTest(key=key):
                    self.assertIn(value, self.document)

    def test_closeout_repeats_no_qualification_or_private_operation(self):
        self.assertFalse(
            EXPECTED_PROOF["generated_qualification_repeated_for_proof_closeout"]
        )
        self.assertEqual(EXPECTED_PROOF["private_operations_during_proof_closeout"], 0)
        self.assertTrue(
            all(
                value == 0
                for value in self.implementation["operation_counters"].values()
            )
        )

    def test_private_packet_eligibility_has_delayed_effect(self):
        for record in (self.implementation, self.result):
            gate = record["next_gate"]
            self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
            self.assertFalse(gate["private_confirmation_packet_eligible_now"])
            self.assertTrue(
                gate["private_confirmation_packet_eligible_after_exact_closeout_green"]
            )
            self.assertFalse(gate["private_or_neural_execution_authorized"])

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", self.document)
        self.assertIn("Scientific claim not established", self.document)
        self.assertIn("no real cohort or neural payload", self.document.lower())


if __name__ == "__main__":
    unittest.main()
