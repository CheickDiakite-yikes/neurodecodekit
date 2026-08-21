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
EXPECTED_REMOTE_PROOF = {
    "commit": "fcff5140a9e8f106a42cf8c5a2a944ca1d52f42d",
    "CI_run_id": 32_472_572_881,
    "base_python_job_id": 96_742_255_383,
    "optional_neuro_job_id": 96_742_255_145,
    "both_required_jobs_green": True,
    "implementation_module_Git_blob": "c38967813b231c74625693bb9b121bb29382e136",
    "behavior_test_Git_blob": "0bee38ec776ad7c1ee37a160fb837501c3ecdde6",
    "implementation_document_Git_blob": "84fab15bf36f1d8ab0587e6f7b03880816f1d82d",
    "result_document_Git_blob": "2f0073d64a707bb63c1b856355cc4300b1bf2bc0",
    "preproof_implementation_registry_Git_blob": (
        "5e052c3d498a716cc50a6e3f5ff01d051e08c8d1"
    ),
    "preproof_result_registry_Git_blob": "6138d24dfa7a6ab628dea5d4851b640f4c8a5e87",
    "preproof_record_test_Git_blob": "f2188d3e59bc11259c8b8c94d0a916d1dce4df61",
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operation_repeated_for_proof_closeout": False,
}


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
        self.assertEqual(
            self.implementation["remote_implementation_proof"],
            EXPECTED_REMOTE_PROOF,
        )
        self.assertEqual(self.result["remote_implementation_proof"], EXPECTED_REMOTE_PROOF)
        self.assertFalse(self.implementation["local_verification"]["remote_CI_pending"])

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
