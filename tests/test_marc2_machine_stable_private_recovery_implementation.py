import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    marc2_machine_stable_private_recovery as recovery,
)
from neurodecodekit.datasets import marc2_proof_record_recovery as proof_recovery


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / recovery.IMPLEMENTATION_REGISTRY_RELATIVE_PATH
PROOF_PATH = ROOT / recovery.PROOF_CERTIFICATE_RELATIVE_PATH
DOC_PATH = ROOT / "docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_IMPLEMENTATION.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2MachineStablePrivateRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.proof_bytes = PROOF_PATH.read_bytes()
        cls.proof_record = json.loads(cls.proof_bytes.decode("ascii"))

    def test_native_registry_identity_and_green_decision_are_exact(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc2_machine_stable_private_recovery_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC2-VR4P")
        decision = self.registry["green_authorization_decision"]
        self.assertEqual(
            decision["commit"], "eac37262dcf7cd4167475b7cc9145e3698d6dd9b"
        )
        self.assertEqual(decision["CI_run_id"], 31_969_063_955)
        self.assertTrue(decision["both_required_jobs_green"])

    def test_generated_qualification_is_measured_and_real_counters_are_zero(self):
        qualification = self.registry["generated_qualification"]
        self.assertEqual(qualification["status"], "completed_generated_mock_only")
        self.assertEqual(qualification["route"], recovery.SUCCESS_ROUTE)
        self.assertEqual(qualification["replay_runs"], 2)
        self.assertEqual(qualification["direct_mutations_refused"], 27)
        self.assertGreater(qualification["generated_input_bytes"], 0)
        self.assertGreater(qualification["generated_output_bytes"], 0)
        self.assertEqual(qualification["retained_output_bytes"], 0)
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(
            qualification["real_private_archive_neural_target_model_score_operations"],
            0,
        )
        self.assertTrue(
            all(
                value == 0
                for value in self.registry["implementation_access_counters"].values()
            )
        )

    def test_distinct_shared_proof_record_validates_through_exact_symbol(self):
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
        self.assertEqual(
            summary.validator_symbol,
            proof_recovery.validate_implementation_record.__name__,
        )

    def test_proof_record_binds_all_implementation_ownership_files(self):
        tracked = {
            item["path"]: item["sha256"]
            for item in self.proof_record["tracked_file_hashes"]
        }
        required = {
            "src/neurodecodekit/datasets/marc2_machine_stable_private_recovery.py",
            "tests/test_marc2_machine_stable_private_recovery.py",
            "tests/test_marc2_machine_stable_private_recovery_implementation.py",
            "docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_IMPLEMENTATION.md",
            recovery.IMPLEMENTATION_REGISTRY_RELATIVE_PATH.as_posix(),
            recovery.DECISION_DOCUMENT_RELATIVE_PATH.as_posix(),
            recovery.DECISION_REGISTRY_RELATIVE_PATH.as_posix(),
            recovery.REQUEST_REGISTRY_RELATIVE_PATH.as_posix(),
            "src/neurodecodekit/datasets/marc2_machine_readiness.py",
            "src/neurodecodekit/datasets/marc2_live_domain_eligibility_adapter.py",
            "src/neurodecodekit/datasets/marc2_freewill_prefix_selection.py",
            "src/neurodecodekit/datasets/marc2_proof_record_recovery.py",
        }
        self.assertTrue(required.issubset(tracked))
        self.assertNotIn(recovery.PROOF_CERTIFICATE_RELATIVE_PATH.as_posix(), tracked)
        for path, digest in tracked.items():
            with self.subTest(path=path):
                self.assertEqual(sha256_file(ROOT / path), digest)

    def test_fixed_state_machine_and_caps_match_authorized_scope(self):
        identities = self.registry["registered_identities"]
        self.assertEqual(identities["expired_certificate"]["bytes"], 4_551)
        self.assertEqual(identities["expired_certificate"]["unlink_limit"], 1)
        self.assertEqual(identities["private_source"]["bytes"], 418_755)
        self.assertEqual(identities["private_source"]["content_open_limit"], 1)
        self.assertEqual(identities["private_source"]["VR2_adapter_call_limit"], 1)
        self.assertEqual(identities["cohort"]["selected_subjects"], 16)
        self.assertEqual(identities["cohort"]["selected_bundles"], 96)
        self.assertEqual(identities["cohort"]["selected_members"], 384)
        caps = self.registry["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2)
        self.assertEqual(caps["combined_output_bytes"], 4 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)

    def test_real_execution_remains_unconsumed_and_payload_closed(self):
        state = self.registry["real_execution_state"]
        self.assertEqual(state["registered_real_execution_limit"], 1)
        self.assertFalse(state["registered_real_execution_consumed"])
        self.assertEqual(state["retry_rerun_resume_repair_or_fallback_limit"], 0)
        self.assertFalse(state["expired_certificate_operated_on"])
        self.assertFalse(state["private_structural_manifest_opened"])
        self.assertFalse(state["real_cohort_frozen"])
        gate = self.registry["next_gate"]
        self.assertTrue(
            gate["exact_implementation_commit_push_and_both_jobs_green_required"]
        )
        self.assertFalse(gate["real_sequence_may_begin_before_green"])
        self.assertFalse(
            gate[
                "archive_payload_neural_training_prediction_target_or_score_authorized_now"
            ]
        )

    def test_document_states_engineering_and_scientific_boundaries(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("preceding state-machine event", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("qualified on generated/mock inputs", text)


if __name__ == "__main__":
    unittest.main()
