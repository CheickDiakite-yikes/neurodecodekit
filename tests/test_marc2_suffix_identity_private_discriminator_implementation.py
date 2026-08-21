import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT
    / "registries/marc2_suffix_identity_private_discriminator_implementation.v0.json"
)
IMPLEMENTATION_DOC = (
    ROOT / "docs/MARC_2_SUFFIX_IDENTITY_PRIVATE_DISCRIMINATOR_IMPLEMENTATION.md"
)
RESULT_DOC = (
    ROOT / "docs/MARC_2_SUFFIX_IDENTITY_PRIVATE_DISCRIMINATOR_GENERATED_RESULT.md"
)


class Marc2SuffixIdentityPrivateDiscriminatorImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_decision_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_suffix_identity_private_discriminator_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-VR15P")
        proof = self.record["green_decision_proof"]
        self.assertEqual(proof["commit"], "fc694a69489913198f0a630bbb0edb04c29310f6")
        self.assertEqual(proof["CI_run_id"], 32_451_448_725)
        self.assertEqual(proof["base_python_job_id"], 96_680_587_357)
        self.assertEqual(proof["optional_neuro_job_id"], 96_680_587_199)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_fixed_and_owned_artifacts_are_exact(self):
        fixed = self.record["fixed_inputs"]
        owned = self.record["owned_artifacts"]
        self.assertEqual(len(fixed), 6)
        self.assertEqual(sum(row["bytes"] for row in fixed), 88_174)
        self.assertEqual(len(owned), 5)
        for row in [*fixed, *owned]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_generated_measurements_are_exact(self):
        measured = self.record["generated_qualification"]
        self.assertEqual(measured["route"], "MARC2VR15P-G1")
        self.assertEqual(measured["matrix_paths"], 68)
        self.assertEqual(measured["generated_VR15A_calls"], 68)
        self.assertEqual(measured["generated_nested_VR12A_calls"], 68)
        self.assertEqual(measured["route_count_each"], 4)
        self.assertEqual(measured["direct_refusals"], 111)
        self.assertEqual(measured["generated_input_bytes"], 29_199_868)
        self.assertEqual(measured["temporary_peak_bytes"], 429_857)
        self.assertEqual(measured["aggregate_output_bytes"], 2_681)
        self.assertEqual(measured["retained_output_bytes"], 0)
        self.assertLessEqual(measured["runtime_seconds"], 90)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)

    def test_interface_and_private_route_contract_are_frozen(self):
        interface = self.record["interface"]
        self.assertEqual(interface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(interface["fixed_path_execute"])
        self.assertFalse(interface["generic_path_or_output_override_allowed"])
        self.assertTrue(interface["standard_library_only"])
        contract = self.record["private_stage_contract"]
        self.assertEqual(contract["private_source_bytes"], 418_755)
        self.assertEqual(contract["private_content_open_limit"], 1)
        self.assertEqual(contract["VR15A_calls"], 1)
        self.assertEqual(contract["nested_VR12A_calls"], 1)
        self.assertEqual(contract["allowed_routes"], [f"MARC2VR15P-R{i}" for i in range(1, 17)])
        self.assertFalse(contract["cohort_manifest_allowed"])

    def test_remote_implementation_is_green_and_closeout_is_null(self):
        proof = self.record["remote_implementation_proof"]
        self.assertEqual(
            proof["commit"], "28a734df3fb0cb83c3cddb4994b76d8c9453830b"
        )
        self.assertEqual(proof["CI_run_id"], 32_454_196_219)
        self.assertEqual(proof["base_python_job_id"], 96_688_236_516)
        self.assertEqual(proof["optional_neuro_job_id"], 96_688_236_752)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertIsNone(self.record["remote_proof_closeout"])
        self.assertEqual(self.record["private_stage_operations"], 0)
        self.assertTrue(all(value == 0 for value in self.record["forbidden_counters"].values()))
        gate = self.record["next_gate"]
        self.assertFalse(gate["implementation_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["separate_proof_closeout_green_required"])
        self.assertFalse(gate["private_execution_authorized_now"])

    def test_documents_preserve_engineering_and_scientific_boundaries(self):
        implementation = IMPLEMENTATION_DOC.read_text(encoding="utf-8")
        result = RESULT_DOC.read_text(encoding="utf-8")
        self.assertIn("private stage proof-gated", implementation)
        self.assertIn("output is zero", implementation)
        self.assertIn("Scientific claim not established", implementation)
        self.assertIn("111", result)
        self.assertIn("Scientific claim not established", result)


if __name__ == "__main__":
    unittest.main()
