import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_r4_decomposition_implementation.v0.json"
)
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_r4_decomposition_result.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2FirstFailureStableR4DecompositionRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_records_bind_same_lane_route_and_registration(self):
        self.assertEqual(self.implementation["lane_id"], "MARC2-VR17C")
        self.assertEqual(self.result["lane_id"], "MARC2-VR17C")
        self.assertEqual(self.result["route"], "MARC2VR17C-G1")
        self.assertEqual(
            self.implementation["green_registration_proof"],
            self.result["green_registration_proof"],
        )
        self.assertIsNone(self.implementation["remote_implementation_proof"])
        self.assertIsNone(self.result["remote_implementation_proof"])

    def test_owned_artifact_sizes_and_hashes_are_exact(self):
        for artifact in self.implementation["tracked_implementation_artifacts"]:
            path = ROOT / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["bytes"])
            self.assertEqual(_sha256(path), artifact["sha256"])

    def test_equivalence_and_residual_matrices_are_exact(self):
        equivalence = self.result["equivalence_matrix"]
        self.assertEqual(equivalence["paths"], 24)
        self.assertEqual(equivalence["VR15A_calls"], 24)
        self.assertEqual(equivalence["VR16A_calls"], 24)
        self.assertEqual(len(set(equivalence["replay_digests"])), 1)
        residual = self.result["residual_matrix"]
        self.assertEqual(residual["paths"], 20)
        self.assertEqual(residual["VR16A_calls"], 20)
        self.assertEqual(
            residual["route_counts"],
            {route: 4 for route in ("MARC2VR17C-G1", *vr17c_result_routes())},
        )

    def test_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 19_213_944)
        self.assertEqual(measured["aggregate_output_bytes"], 2_719)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(self.result["refusals"]["direct_refusals"], 50)

    def test_every_hypothesis_passes_and_every_forbidden_counter_is_zero(self):
        self.assertTrue(all(self.result["hypotheses"].values()))
        for record in (self.implementation, self.result):
            self.assertTrue(all(value == 0 for value in record["access_counters"].values()))
            boundary = record["claim_boundary"]
            self.assertEqual(boundary["scientific_ceiling"], "none")
            for key, value in boundary.items():
                if key not in {"engineering_ceiling", "scientific_ceiling"}:
                    self.assertFalse(value, key)

    def test_surface_and_documents_preserve_generated_only_boundary(self):
        surface = self.implementation["implementation_surface"]
        self.assertEqual(surface["CLI_commands"], ["plan", "qualify"])
        self.assertFalse(surface["execute_mode_present"])
        self.assertFalse(surface["private_executor_present"])
        for name in (
            "MARC_2_FIRST_FAILURE_STABLE_R4_DECOMPOSITION_IMPLEMENTATION.md",
            "MARC_2_FIRST_FAILURE_STABLE_R4_DECOMPOSITION_RESULT.md",
        ):
            text = (ROOT / "docs" / name).read_text(encoding="utf-8").lower()
            self.assertIn("generated", text)
            self.assertIn("neural payload", text)
            self.assertIn("scientific", text)


def vr17c_result_routes() -> tuple[str, ...]:
    return tuple(f"MARC2VR17C-R{index}" for index in range(1, 5))


if __name__ == "__main__":
    unittest.main()
