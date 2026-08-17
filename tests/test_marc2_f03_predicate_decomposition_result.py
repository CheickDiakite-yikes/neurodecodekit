import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_f03_predicate_decomposition as f03

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_f03_predicate_decomposition_result.v0.json"
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_f03_predicate_decomposition_implementation.v0.json"
)
RESULT_DOCUMENT_PATH = ROOT / "docs/MARC_2_F03_PREDICATE_DECOMPOSITION_RESULT.md"
IMPLEMENTATION_DOCUMENT_PATH = (
    ROOT / "docs/MARC_2_F03_PREDICATE_DECOMPOSITION_IMPLEMENTATION.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2F03PredicateDecompositionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )

    def test_result_identity_and_remote_pending_status_are_honest(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_f03_predicate_decomposition_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR10A")
        self.assertEqual(self.result["route"], "MARC2VR10A-G1")
        self.assertEqual(
            self.result["status"],
            "completed_artifact_only_generated_F03_decomposition_remote_proof_pending",
        )
        self.assertTrue(self.result["verification"]["remote_CI_pending"])
        self.assertFalse(
            self.implementation["remote_implementation_proof"][
                "both_required_jobs_green"
            ]
        )

    def test_green_registration_precedes_implementation(self):
        proof = self.result["green_registration_proof"]
        self.assertEqual(
            proof["commit"], "80175a7e6483a6d156b23a24f9503a9ae32e7201"
        )
        self.assertEqual(proof["CI_run_id"], 31_997_129_703)
        self.assertEqual(proof["base_python_job_id"], 95_290_665_076)
        self.assertEqual(proof["optional_neuro_job_id"], 95_290_665_173)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])
        self.assertEqual(proof, self.implementation["green_registration_proof"])

    def test_tracked_implementation_artifacts_match_exact_files(self):
        artifacts = {
            row["role"]: row
            for row in self.implementation["tracked_implementation_artifacts"]
        }
        expected = {
            "implementation_module": ROOT
            / "src/neurodecodekit/datasets/marc2_f03_predicate_decomposition.py",
            "behavior_test": ROOT / "tests/test_marc2_f03_predicate_decomposition.py",
            "implementation_document": IMPLEMENTATION_DOCUMENT_PATH,
            "result_document": RESULT_DOCUMENT_PATH,
        }
        self.assertEqual(set(artifacts), set(expected))
        for role, path in expected.items():
            self.assertEqual(artifacts[role]["path"], path.relative_to(ROOT).as_posix())
            self.assertEqual(artifacts[role]["bytes"], path.stat().st_size)
            self.assertEqual(artifacts[role]["sha256"], sha256(path))

    def test_machine_result_passes_the_exact_public_validator(self):
        f03._validate_public_report(self.result)
        self.assertEqual(len(self.result["predicate_inventory"]), 20)
        self.assertEqual(len(self.result["witness_matrix"]), 6)
        self.assertEqual(len(self.result["direct_refusals"]), 47)
        self.assertTrue(all(self.result["acceptance_gates"].values()))
        self.assertTrue(
            all(value == 0 for value in self.result["access_counters"].values())
        )

    def test_partition_and_all_five_generated_witnesses_are_exact(self):
        self.assertEqual(
            self.result["partition_summary"],
            {
                "leaf_predicates": 20,
                "excluded_by_committed_evidence": 15,
                "unresolved_source_dependent": 5,
                "private_observations": 0,
                "causal_claims": 0,
            },
        )
        matrix = self.result["witness_matrix"]
        self.assertEqual([row["case"] for row in matrix], list(f03.CASES))
        self.assertEqual(matrix[0]["disposition"], "VR6_success")
        for row in matrix[1:]:
            self.assertEqual(row["outer_VR6_route"], "MARC2VR6-F02")
            self.assertEqual(row["nested_VR2_route"], "MARC2VR2-F03")
            self.assertEqual(row["predicate_id"], f03.CASE_PREDICATES[row["case"]])

    def test_replay_and_resources_match_the_measured_closeout(self):
        replay = self.result["replay_summary"]
        self.assertEqual(replay["total_paths"], 24)
        self.assertEqual(replay["exact_parser_entry_visits"], 29_448)
        self.assertEqual(replay["exact_VR6_calls"], 24)
        self.assertEqual(replay["control_success_paths"], 4)
        self.assertEqual(replay["nested_F03_paths"], 20)
        self.assertTrue(replay["route_and_mechanics_replay_byte_identical"])
        measured = self.result["measurements"]
        self.assertEqual(measured["fixed_artifact_count"], 17)
        self.assertEqual(measured["fixed_artifact_bytes"], 480_963)
        self.assertEqual(measured["generated_input_bytes"], 6_979_708)
        self.assertEqual(measured["aggregate_output_bytes"], 10_751)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["runtime_seconds"], 1.8363693330029491)
        self.assertEqual(measured["peak_RSS_bytes"], 45_072_384)
        self.assertLessEqual(measured["runtime_seconds"], 30)
        self.assertLessEqual(measured["peak_RSS_bytes"], 256 * 1024 * 1024)

    def test_implementation_record_matches_machine_result(self):
        qualification = self.implementation["generated_witness_qualification"]
        measured = self.implementation["measured_qualification"]
        self.assertEqual(qualification["route"], self.result["route"])
        self.assertEqual(qualification["exact_paths"], 24)
        self.assertEqual(qualification["exact_parser_entry_visits"], 29_448)
        self.assertEqual(qualification["exact_VR6_calls"], 24)
        self.assertEqual(qualification["direct_refusals_passed"], 47)
        self.assertEqual(measured, self.result["measurements"])

    def test_documents_state_result_and_claim_boundary_plainly(self):
        result_text = RESULT_DOCUMENT_PATH.read_text(encoding="utf-8")
        implementation_text = IMPLEMENTATION_DOCUMENT_PATH.read_text(
            encoding="utf-8"
        )
        self.assertIn("Five remain source-dependent", result_text)
        self.assertIn("does not identify which of the five", result_text)
        self.assertIn("Scientific claim not established", result_text)
        self.assertIn("remote implementation proof pending", implementation_text)
        self.assertIn("No private path", implementation_text)
        self.assertIn("Scientific claim not established", implementation_text)

    def test_next_gate_does_not_authorize_private_or_scientific_work(self):
        gate = self.result["next_gate"]
        self.assertTrue(
            gate[
                "future_aggregate_safe_five_route_discriminator_design_allowed_after_green"
            ]
        )
        self.assertFalse(gate["future_private_discriminator_authorized"])
        self.assertTrue(
            gate["future_private_read_requires_new_Tier_C_packet_and_fresh_decision"]
        )
        self.assertFalse(gate["consumed_VR9P_reuse_allowed"])
        self.assertFalse(gate["F03_rule_relaxation_allowed"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["neural_effect"])
        self.assertFalse(claims["decoding_accuracy"])
        self.assertFalse(claims["language_or_thought_decoding"])


if __name__ == "__main__":
    unittest.main()
