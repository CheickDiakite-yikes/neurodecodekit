import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_r5_two_route_discriminator_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_r5_two_route_discriminator_result.v0.json"


class Marc2R5TwoRouteDiscriminatorImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_registration_precedes_implementation(self):
        proof = self.implementation["registration_proof"]
        self.assertEqual(
            proof["commit"], "7ce0e16392fed2576031766bead32a5cab44031a"
        )
        self.assertEqual(proof["CI_run_id"], 32_559_365_362)
        self.assertEqual(proof["base_job_id"], 96_998_477_692)
        self.assertEqual(proof["optional_neuro_job_id"], 96_998_477_649)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_implementation_artifacts_are_byte_exact(self):
        total = 0
        for artifact in self.implementation["implementation_artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
            total += len(payload)
        self.assertEqual(total, self.implementation["implementation_artifact_bytes"])

    def test_measured_matrix_is_exact(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 12)
        self.assertEqual(matrix["VR20A_calls"], 12)
        self.assertEqual(matrix["direct_refusals_passed"], 48)
        self.assertEqual(matrix["source_mutations_after_call"], 0)
        self.assertEqual(
            matrix["VR21A_route_counts"],
            {
                "MARC2VR21A-G1": 4,
                "MARC2VR21A-R1": 4,
                "MARC2VR21A-R2": 4,
            },
        )

    def test_resources_and_forbidden_counters_are_bounded(self):
        resources = self.result["resources"]
        self.assertLessEqual(resources["runtime_seconds"], 30)
        self.assertLess(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(resources["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(resources["output_bytes"], 1024**2)
        self.assertEqual(resources["retained_output_bytes"], 0)
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )

    def test_private_route_and_scientific_claim_remain_closed(self):
        interpretation = self.result["result_interpretation"]
        self.assertTrue(interpretation["generated_F06_maps_to_R1"])
        self.assertTrue(interpretation["generated_F07_maps_to_R2"])
        for key, value in interpretation.items():
            if key not in {"generated_F06_maps_to_R1", "generated_F07_maps_to_R2"}:
                self.assertFalse(value, key)
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
