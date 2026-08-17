import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_proof_record_recovery as proof_recovery
from neurodecodekit.datasets import marc2_two_layer_private_diagnostic as diagnostic


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries"
    / "marc2_two_layer_private_diagnostic_implementation.v0.json"
)
PROOF_PATH = (
    ROOT / "registries/marc2_two_layer_private_diagnostic_proof.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_TWO_LAYER_PRIVATE_DIAGNOSTIC_IMPLEMENTATION.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2TwoLayerPrivateDiagnosticImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.proof_bytes = PROOF_PATH.read_bytes()
        cls.proof = json.loads(cls.proof_bytes)

    def test_identity_and_green_decision_are_exact(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc2_two_layer_private_diagnostic_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC2-VR9P")
        self.assertEqual(
            self.registry["status"],
            "generated_mock_implementation_complete_private_sequence_not_executed",
        )
        green = self.registry["green_authorization_decision"]
        self.assertEqual(green["commit"], diagnostic.DECISION_COMMIT)
        self.assertEqual(green["CI_run_id"], 31_993_388_608)
        self.assertEqual(green["base_python_job_id"], 95_280_728_093)
        self.assertEqual(green["optional_neuro_job_id"], 95_280_728_134)
        self.assertTrue(green["both_required_jobs_green_before_implementation"])

    def test_implementation_artifacts_are_byte_exact(self):
        artifacts = self.registry["implementation_artifacts"]
        self.assertEqual(len(artifacts), 4)
        for artifact in artifacts:
            path = ROOT / artifact["path"]
            with self.subTest(path=artifact["path"]):
                self.assertEqual(path.stat().st_size, artifact["bytes"])
                self.assertEqual(sha256_file(path), artifact["sha256"])

    def test_generated_qualification_is_measured_and_bounded(self):
        generated = self.registry["generated_qualification"]
        self.assertEqual(generated["status"], "completed_generated_mock_only")
        self.assertEqual(generated["route"], "MARC2VR9P-G1")
        self.assertEqual(generated["cases"], ["F03", "F04"])
        self.assertEqual(generated["row_orders"], ["canonical", "reversed"])
        self.assertEqual(generated["exact_replays"], 2)
        self.assertEqual(generated["VR6_calls_total"], 8)
        self.assertEqual(generated["direct_refusals"], 70)
        self.assertEqual(generated["generated_input_bytes"], 3_407_792)
        self.assertEqual(generated["generated_output_bytes"], 53_528)
        self.assertEqual(generated["retained_output_bytes"], 0)
        self.assertEqual(generated["aggregate_output_bytes"], 6_541)
        self.assertLess(generated["runtime_seconds"], 30)
        self.assertLess(generated["peak_RSS_bytes"], 256 * 1024**2)
        self.assertTrue(generated["all_gates_passed"])
        self.assertEqual(
            generated["real_private_neural_target_model_score_or_hardware_operations"],
            0,
        )

    def test_fixed_paths_routes_and_no_cohort_output_are_exact(self):
        paths = self.registry["fixed_paths"]
        identity = self.registry["registered_identities"]
        self.assertEqual(
            paths["fresh_readiness_certificate"],
            ".codex_work/marc2_machine_readiness/vr9p/readiness.v0.json",
        )
        self.assertEqual(
            paths["new_output_root"],
            ".codex_work/marc2_two_layer_private_diagnostic/v0",
        )
        self.assertIsNone(paths["private_manifest"])
        self.assertEqual(identity["private_source"]["bytes"], 418_755)
        self.assertEqual(identity["private_source"]["VR6_adapter_call_limit"], 1)
        self.assertEqual(
            identity["diagnostic_output"]["allowed_nested_routes"],
            ["MARC2VR2-F03", "MARC2VR2-F04"],
        )
        self.assertFalse(identity["diagnostic_output"]["private_manifest_allowed"])

    def test_command_surface_has_no_redirect_or_consumed_reuse(self):
        surface = self.registry["implementation_surface"]
        self.assertEqual(surface["module"], diagnostic.MODULE_NAME)
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertFalse(
            surface["generic_path_URL_threshold_retry_resume_or_fallback_argument"]
        )
        self.assertFalse(surface["consumed_executor_import_call_patch_copy_or_reuse"])
        self.assertFalse(surface["private_manifest_or_cohort_output"])

    def test_private_state_and_all_implementation_counters_are_zero(self):
        state = self.registry["private_execution_state"]
        self.assertEqual(state["registered_private_execution_limit"], 1)
        self.assertFalse(state["registered_private_execution_consumed"])
        self.assertEqual(state["retry_rerun_resume_repair_or_fallback_limit"], 0)
        self.assertFalse(state["fresh_readiness_certificate_created"])
        self.assertFalse(state["private_structural_manifest_opened"])
        self.assertFalse(state["real_two_layer_route_observed"])
        self.assertFalse(state["private_manifest_or_cohort_output_available"])
        self.assertFalse(state["MARC2_FW2_or_CIL1_eligible"])
        self.assertTrue(
            all(
                value == 0
                for value in self.registry["implementation_access_counters"].values()
            )
        )

    def test_shared_proof_record_validates_through_exact_closure(self):
        digest = hashlib.sha256(self.proof_bytes).hexdigest()
        envelope = proof_recovery.ProofEnvelope(
            implementation_commit="a" * 40,
            implementation_CI_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256=digest,
            observed_HEAD="a" * 40,
            tracked_worktree_clean=True,
            green_decision_ancestor=True,
        )
        summary = proof_recovery.validate_implementation_record(
            self.proof_bytes,
            repo_root=ROOT,
            expected_proof=envelope,
            observed_proof=envelope,
        )
        self.assertEqual(summary.record_sha256, digest)
        self.assertGreaterEqual(summary.tracked_binding_count, 12)
        self.assertEqual(summary.validator_module, proof_recovery.MODULE_NAME)

    def test_shared_proof_tracks_new_surface_without_consumed_executor(self):
        bindings = {
            row["path"]: row["sha256"] for row in self.proof["tracked_file_hashes"]
        }
        required = {
            "src/neurodecodekit/datasets/marc2_two_layer_private_diagnostic.py",
            "tests/test_marc2_two_layer_private_diagnostic.py",
            "tests/test_marc2_two_layer_private_diagnostic_implementation.py",
            "docs/MARC_2_TWO_LAYER_PRIVATE_DIAGNOSTIC_IMPLEMENTATION.md",
            "registries/marc2_two_layer_private_diagnostic_implementation.v0.json",
        }
        self.assertTrue(required <= set(bindings))
        for path, digest in bindings.items():
            with self.subTest(path=path):
                self.assertEqual(sha256_file(ROOT / path), digest)
        consumed = "marc2_dynamic_" + "private_selection_recovery"
        self.assertTrue(all(consumed not in path for path in bindings))

    def test_next_gate_and_claim_boundary_fail_closed(self):
        gate = self.registry["next_gate"]
        claim = self.registry["claim_boundary"]
        self.assertTrue(gate["exact_implementation_commit_push_and_both_jobs_green_required"])
        self.assertFalse(gate["private_sequence_may_begin_before_green"])
        self.assertTrue(gate["one_registered_structural_diagnostic_after_green"])
        self.assertFalse(
            gate[
                "FW2_CIL1_archive_payload_neural_training_prediction_target_or_score_authorized"
            ]
        )
        self.assertIn("Generated qualification", claim["scientific_claim_not_established"])

    def test_human_record_preserves_two_green_barriers_and_no_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("private structural command", text)
        self.assertIn("remains closed until this exact implementation", text)
        self.assertIn("70 direct refusals", text)
        self.assertIn("There is no generic source", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
