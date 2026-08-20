import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_r4_residual_decomposition_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_r4_residual_decomposition_result.v0.json"


class Marc2R4ResidualDecompositionRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_record_identities_and_remote_proof_are_explicit(self):
        self.assertEqual(self.implementation["lane_id"], "MARC2-VR13A")
        self.assertEqual(self.result["lane_id"], "MARC2-VR13A")
        self.assertEqual(self.result["route"], "MARC2VR13A-G1")
        proof = {
            "commit": "63a0b8ea4cc72b942a6b7dbdcd96680859f5f059",
            "CI_run_id": 32_426_975_815,
            "base_python_job_id": 96_610_793_887,
            "optional_neuro_job_id": 96_610_793_714,
            "both_required_jobs_green": True,
            "implementation_module_Git_blob": (
                "4c4a929917cbda3409f8476363e192edac668dfe"
            ),
            "behavior_test_Git_blob": "eeca2af700b4ad1d89e53c8da7fcbe22c8f2e661",
            "implementation_document_Git_blob": (
                "a2f32c50c32ef74bc95f64f061a7deedb66b60e7"
            ),
            "result_document_Git_blob": (
                "07b1c2d225791b4a185793d23b01e880e7eed35f"
            ),
            "preproof_implementation_registry_Git_blob": (
                "50c3ba032d60d66ce45457609d113ed4b2165ec7"
            ),
            "preproof_result_registry_Git_blob": (
                "6aa114f908c796b8ed45ad3b2b7d1ca7170e15df"
            ),
            "generated_qualification_repeated_for_proof_closeout": False,
            "private_operation_repeated_for_proof_closeout": False,
        }
        self.assertEqual(self.implementation["remote_implementation_proof"], proof)
        self.assertEqual(self.result["remote_implementation_proof"], proof)
        self.assertNotIn("pending", self.implementation["status"])
        self.assertNotIn("pending", self.result["status"])

    def test_registration_proof_matches_both_records(self):
        expected = {
            "commit": "1177174c1d466cf357ef3a81a4d96b39321af063",
            "CI_run_id": 32_424_688_012,
            "base_python_job_id": 96_604_083_183,
            "optional_neuro_job_id": 96_604_083_100,
            "both_required_jobs_green_before_implementation": True,
            "contract_sha256": (
                "b51472e609d5355bac9902b3c70f37ea7ba3bd39231910e1507926be953e4b55"
            ),
        }
        self.assertEqual(self.implementation["green_registration_proof"], expected)
        self.assertEqual(self.result["green_registration_proof"], expected)

    def test_every_tracked_implementation_artifact_matches(self):
        rows = self.implementation["tracked_implementation_artifacts"]
        self.assertEqual(len(rows), 4)
        self.assertEqual(len({row["path"] for row in rows}), len(rows))
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertNotIn(".codex_work", row["path"])

    def test_route_counts_and_replay_measurements_are_exact(self):
        expected = {"MARC2VR13A-G1": 4}
        expected.update({f"MARC2VR13A-R{index}": 4 for index in range(1, 8)})
        self.assertEqual(self.result["route_summary"]["route_counts"], expected)
        replay = self.result["replay_summary"]
        self.assertEqual(replay["total_paths"], 32)
        self.assertEqual(replay["exact_VR12A_calls"], 32)
        self.assertTrue(replay["order_invariant_routes"])
        self.assertTrue(replay["byte_identical_replay"])
        self.assertEqual(
            replay["internal_matrix_digest_sha256"],
            "56430e51b8f97f8c34a2c2fc95706316f2bbf058d7c25b8b8fc2b6a74bf1ae05",
        )

    def test_resource_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 13_741_736)
        self.assertEqual(measured["aggregate_output_bytes"], 5_514)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["runtime_seconds"], 2.401633999950718)
        self.assertEqual(measured["peak_RSS_bytes"], 36_978_688)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertLessEqual(measured["generated_input_bytes"], 24 * 1024 * 1024)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024 * 1024)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_all_gates_pass_and_every_forbidden_counter_is_zero(self):
        self.assertTrue(all(self.result["acceptance_gates"].values()))
        self.assertTrue(
            all(value == 0 for value in self.result["access_counters"].values())
        )
        self.assertTrue(
            all(
                value == 0
                for value in self.implementation["access_counters"].values()
            )
        )
        self.assertEqual(self.result["direct_refusals"]["total_passed"], 54)

    def test_no_private_executor_or_scientific_surface_was_added(self):
        surface = self.implementation["implementation_surface"]
        self.assertFalse(surface["private_executor_present"])
        self.assertFalse(surface["network_client_present"])
        self.assertFalse(surface["archive_payload_reader_present"])
        self.assertFalse(surface["model_or_scorer_present"])
        next_gate = self.result["next_gate"]
        self.assertFalse(next_gate["future_private_discriminator_authorized"])
        self.assertFalse(next_gate["consumed_VR11P_or_VR12P_reuse_allowed"])
        self.assertFalse(next_gate["MARC2_FW2_or_CIL1_authorized"])
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_ceiling", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
