import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_f03_five_route_discriminator as five

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_f03_five_route_discriminator_result.v0.json"
)
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_f03_five_route_discriminator_implementation.v0.json"
)
RESULT_DOCUMENT_PATH = (
    ROOT / "docs/MARC_2_F03_FIVE_ROUTE_DISCRIMINATOR_RESULT.md"
)
IMPLEMENTATION_DOCUMENT_PATH = (
    ROOT / "docs/MARC_2_F03_FIVE_ROUTE_DISCRIMINATOR_IMPLEMENTATION.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2F03FiveRouteDiscriminatorResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )

    def test_result_identity_and_remote_green_status_are_honest(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_f03_five_route_discriminator_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR10B")
        self.assertEqual(self.result["route"], "MARC2VR10B-G1")
        self.assertEqual(
            self.result["status"],
            "completed_artifact_only_generated_five_route_qualification_remotely_green",
        )
        self.assertFalse(
            self.implementation["local_verification"]["remote_CI_pending"]
        )
        proof = self.implementation["remote_implementation_proof"]
        self.assertEqual(
            proof["commit"], "61bb801689eb2885b1e96aa4b56c86658dc3b333"
        )
        self.assertEqual(proof["CI_run_id"], 32_007_641_751)
        self.assertEqual(proof["base_python_job_id"], 95_320_325_187)
        self.assertEqual(proof["optional_neuro_job_id"], 95_320_325_136)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof, {
            key: value
            for key, value in self.result["remote_implementation_proof"].items()
            if key
            not in {
                "generated_qualification_repeated_for_proof_closeout",
                "private_operation_repeated_for_proof_closeout",
            }
        })
        self.assertFalse(
            self.result["remote_implementation_proof"][
                "generated_qualification_repeated_for_proof_closeout"
            ]
        )
        self.assertFalse(
            self.result["remote_implementation_proof"][
                "private_operation_repeated_for_proof_closeout"
            ]
        )

    def test_green_registration_precedes_implementation(self):
        proof = self.result["green_registration_proof"]
        self.assertEqual(
            proof["commit"], "d642eae988bdf5200429fb992e7ff25d778ce949"
        )
        self.assertEqual(proof["CI_run_id"], 32_003_674_374)
        self.assertEqual(proof["base_python_job_id"], 95_308_775_711)
        self.assertEqual(proof["optional_neuro_job_id"], 95_308_775_577)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])
        self.assertEqual(proof, self.implementation["green_registration_proof"])

    def test_tracked_implementation_artifacts_match_exact_files(self):
        artifacts = {
            row["role"]: row
            for row in self.implementation["tracked_implementation_artifacts"]
        }
        expected = {
            "implementation_module": ROOT
            / "src/neurodecodekit/datasets/marc2_f03_five_route_discriminator.py",
            "behavior_test": ROOT
            / "tests/test_marc2_f03_five_route_discriminator.py",
            "implementation_document": IMPLEMENTATION_DOCUMENT_PATH,
            "result_document": RESULT_DOCUMENT_PATH,
        }
        self.assertEqual(set(artifacts), set(expected))
        for role, path in expected.items():
            self.assertEqual(artifacts[role]["path"], path.relative_to(ROOT).as_posix())
            self.assertEqual(artifacts[role]["bytes"], path.stat().st_size)
            self.assertEqual(artifacts[role]["sha256"], sha256(path))

    def test_machine_result_passes_exact_public_validator(self):
        five._validate_public_report(self.result)
        self.assertEqual(len(self.result["direct_refusals"]), 60)
        self.assertTrue(all(self.result["acceptance_gates"].values()))
        self.assertTrue(
            all(value == 0 for value in self.result["access_counters"].values())
        )

    def test_all_six_routes_and_broad_relay_are_exact(self):
        summary = self.result["route_summary"]
        self.assertEqual(
            summary["ordered_routes"],
            [five.SUCCESS_ROUTE, *five.RESULT_ROUTES],
        )
        self.assertEqual(summary["route_counts"], five._expected_route_counts())
        self.assertEqual(summary["broad_VR6_success_paths"], 4)
        self.assertEqual(summary["broad_outer_F02_nested_F03_paths"], 20)
        self.assertEqual(summary["failed_values_retained"], 0)
        self.assertEqual(summary["per_item_outcomes_retained"], 0)

    def test_replay_and_resources_match_measured_closeout(self):
        replay = self.result["replay_summary"]
        self.assertEqual(replay["total_paths"], 24)
        self.assertEqual(replay["exact_parser_entry_visits"], 29_448)
        self.assertEqual(replay["exact_VR6_calls"], 24)
        self.assertEqual(replay["exact_discriminator_calls"], 24)
        self.assertTrue(replay["order_invariant"])
        self.assertTrue(replay["byte_identical_replay"])
        self.assertEqual(
            replay["internal_matrix_digest_sha256"],
            "e2c184bbe53c6a1d298cfcd4fef86f0910450b2557e906404816c1175b5a21df",
        )
        measured = self.result["measurements"]
        self.assertEqual(measured["fixed_artifact_count"], 13)
        self.assertEqual(measured["fixed_artifact_bytes"], 417_533)
        self.assertEqual(measured["generated_input_bytes"], 6_979_708)
        self.assertEqual(measured["aggregate_output_bytes"], 7_515)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["runtime_seconds"], 2.725759166991338)
        self.assertEqual(measured["peak_RSS_bytes"], 44_564_480)
        self.assertLessEqual(measured["runtime_seconds"], 45)
        self.assertLessEqual(measured["peak_RSS_bytes"], 256 * 1024 * 1024)

    def test_implementation_record_matches_machine_result(self):
        qualification = self.implementation["generated_qualification"]
        measured = self.implementation["measured_qualification"]
        self.assertEqual(qualification["route"], self.result["route"])
        self.assertEqual(qualification["exact_paths"], 24)
        self.assertEqual(qualification["exact_VR6_calls"], 24)
        self.assertEqual(qualification["exact_discriminator_calls"], 24)
        self.assertEqual(qualification["route_counts"], five._expected_route_counts())
        self.assertEqual(qualification["direct_refusals_passed"], 60)
        self.assertEqual(measured, self.result["measurements"])

    def test_documents_state_result_and_claim_boundary_plainly(self):
        result_text = RESULT_DOCUMENT_PATH.read_text(encoding="utf-8")
        implementation_text = IMPLEMENTATION_DOCUMENT_PATH.read_text(
            encoding="utf-8"
        )
        self.assertIn("cleanly separated all five", result_text)
        self.assertIn("does not identify the cause", result_text)
        self.assertIn("Scientific claim not established", result_text)
        self.assertIn("remotely green", implementation_text)
        self.assertIn("No private path", implementation_text)
        self.assertIn("Scientific claim not established", implementation_text)

    def test_next_gate_does_not_authorize_private_or_scientific_work(self):
        gate = self.result["next_gate"]
        self.assertTrue(
            gate[
                "exact_implementation_and_result_commit_push_and_both_jobs_green_satisfied"
            ]
        )
        self.assertFalse(gate["future_private_discriminator_authorized"])
        self.assertTrue(
            gate[
                "future_private_discriminator_requires_new_Tier_C_packet_and_fresh_decision"
            ]
        )
        self.assertFalse(gate["consumed_VR9P_reuse_allowed"])
        self.assertFalse(gate["F03_rule_relaxation_allowed"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["private_cause_identified"])
        self.assertFalse(claims["neural_effect"])
        self.assertFalse(claims["decoding_accuracy"])
        self.assertFalse(claims["language_or_thought_decoding"])


if __name__ == "__main__":
    unittest.main()
