import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = (
    ROOT
    / "registries/eegmmidb_unseen_participant_generalization_implementation.v0.json"
)
RESULT = (
    ROOT
    / "registries/eegmmidb_unseen_participant_generalization_stage_g_result.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_GENERALIZATION_IMPLEMENTATION.md"


class EEGMMIDBUnseenParticipantStageGResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.implementation = json.loads(IMPLEMENTATION.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_exact_implementation_commit_was_remotely_green_before_execution(self):
        proof = self.implementation["implementation_proof"]
        self.assertEqual(
            proof["commit"], "da2be31a3ea4b7a438f86039c1d80b182e628ccf"
        )
        self.assertEqual(proof["CI_run_id"], 32704970582)
        self.assertEqual(proof["base_python_job_id"], 97363993816)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 97363993465)
        self.assertTrue(proof["both_required_jobs_green_before_stage_G"])
        self.assertTrue(
            self.result["execution_binding"]["all_required_jobs_green_before_execution"]
        )

    def test_exact_implementation_files_and_git_blobs_are_bound(self):
        for row in self.implementation["implementation_artifacts"]:
            path = ROOT / row["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

    def test_central_cli_remains_at_its_historical_proof_identity(self):
        payload = (ROOT / "src/neurodecodekit/cli.py").read_bytes()
        proof = self.implementation["implementation_proof"]
        self.assertEqual(hashlib.sha256(payload).hexdigest(), proof["central_CLI_sha256"])
        blob = subprocess.check_output(
            ["git", "hash-object", "src/neurodecodekit/cli.py"], cwd=ROOT, text=True
        ).strip()
        self.assertEqual(blob, proof["central_CLI_git_blob"])
        self.assertFalse(self.implementation["implemented_surfaces"]["central_CLI_modified"])

    def test_stage_g_is_consumed_once_and_aggregate_result_is_hash_bound(self):
        execution = self.result["execution_binding"]
        self.assertEqual(execution["qualification_invocations"], 1)
        self.assertFalse(execution["qualification_may_be_repeated"])
        self.assertEqual(execution["canonical_source_output_bytes"], 3911)
        self.assertEqual(
            execution["canonical_source_output_sha256"],
            "08bd7568c596c423825b799b2d4e1e67cf4066e2fd7ebd329eeb1a76ccc23359",
        )
        self.assertFalse(execution["canonical_source_output_committed"])

    def test_every_registered_generated_case_class_passed(self):
        self.assertEqual(self.result["case_classes_passed"], 17)
        self.assertEqual(len(self.result["case_classes"]), 17)
        self.assertEqual(set(self.result["case_classes"]), set(self.result["case_evidence"]))
        evidence = self.result["case_evidence"]
        self.assertEqual(evidence["execution_and_imagery_exact_counts"]["source_rows"], 900)
        self.assertEqual(evidence["execution_and_imagery_exact_counts"]["fresh_rows"], 450)
        self.assertEqual(evidence["valid_replay_source_immutability"]["source_mutations"], 0)
        self.assertEqual(evidence["target_swap_and_canary_invariance"]["checkpoint_mutations"], 0)

    def test_exact_schedule_and_resource_measurements_are_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["parameter_update_fits"], 61)
        self.assertEqual(measured["prediction_sets"], 420)
        self.assertEqual(measured["model_inference_runs"], 111)
        self.assertEqual(measured["model_runs"], 172)
        self.assertEqual(measured["input_bytes"], 25975920)
        self.assertEqual(measured["output_bytes"], 3911)
        self.assertLessEqual(measured["peak_incremental_output_bytes"], 536870912)
        self.assertLessEqual(measured["peak_process_tree_RSS_bytes"], 1073741824)
        self.assertLessEqual(measured["runtime_seconds"], 900)
        self.assertTrue(measured["producer_is_causal"])
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_real_data_network_and_real_target_counters_remain_zero(self):
        measured = self.result["measurements"]
        for key in (
            "raw_data_reads",
            "real_cache_reads",
            "real_path_reads",
            "real_EDF_semantic_parses",
            "real_target_deliveries",
            "network_bytes",
            "new_payload_bytes",
        ):
            self.assertEqual(measured[key], 0)
        self.assertEqual(measured["synthetic_target_deliveries"], 1)
        self.assertEqual(measured["scoring_events"], 1)

    def test_synthetic_route_has_no_scientific_claim_value(self):
        self.assertEqual(self.result["synthetic_router_route"], "EEGMMIDBUG1-R4")
        self.assertIn(
            "synthetic_router_route_has_no_claim_value", self.result["warnings"]
        )
        boundary = self.result["claim_boundary"]
        self.assertTrue(all(value is False for key, value in boundary.items() if key not in {"maximum_route_unchanged", "maximum_claim_unchanged"}))
        next_gate = self.implementation["next_gate"]
        self.assertFalse(next_gate["stage_M_metadata_authorized_now"])
        self.assertFalse(next_gate["real_path_or_EDF_access_authorized_now"])

        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no real EEG was opened or scored", document)


if __name__ == "__main__":
    unittest.main()
