import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from neurodecodekit.datasets import eegmmidb_unseen_participant_acquisition as acquisition
from neurodecodekit.datasets import eegmmidb_unseen_participant_metadata as metadata


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "registries/eegmmidb_unseen_participant_metadata_stage_m2_result.v0.json"
)
INVENTORY = (
    ROOT / "registries/eegmmidb_unseen_participant_metadata_inventory.v0.json"
)
RECEIPT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_RECEIPT.md"
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_STAGE_M2_RESULT.md"


class EEGMMIDBUnseenParticipantMetadataStageM2ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.inventory_bytes = INVENTORY.read_bytes()
        cls.inventory = json.loads(cls.inventory_bytes)

    def test_exact_m1_proof_was_green_before_the_one_real_invocation(self):
        execution = self.result["execution_binding"]
        self.assertEqual(
            execution["proof_closeout_commit"],
            "fd88d9d7ca9ffd3951eda295daa74a05ee4201a9",
        )
        self.assertEqual(execution["proof_closeout_CI_run_id"], 32717768039)
        self.assertEqual(execution["base_python_job_id"], 97402552811)
        self.assertEqual(execution["optional_neuro_readers_job_id"], 97402552736)
        self.assertTrue(execution["both_required_jobs_green_before_execution"])
        self.assertEqual(execution["real_metadata_invocations"], 1)
        self.assertFalse(execution["real_metadata_invocation_may_be_repeated"])

    def test_inventory_and_receipt_are_exact_and_canonical(self):
        artifacts = self.result["artifacts"]
        inventory = artifacts["inventory"]
        receipt = artifacts["receipt"]
        self.assertEqual(len(self.inventory_bytes), inventory["bytes"])
        self.assertEqual(
            hashlib.sha256(self.inventory_bytes).hexdigest(), inventory["sha256"]
        )
        self.assertEqual(metadata._canonical_json(self.inventory), self.inventory_bytes)
        receipt_bytes = RECEIPT.read_bytes()
        self.assertEqual(len(receipt_bytes), receipt["bytes"])
        self.assertEqual(hashlib.sha256(receipt_bytes).hexdigest(), receipt["sha256"])
        self.assertEqual(len(self.inventory_bytes) + len(receipt_bytes), 11979)

    def test_exact_frozen_paths_and_partitions_are_complete(self):
        files = self.inventory["files"]
        self.assertEqual(len(files), 36)
        self.assertEqual(
            [row["repository_path"] for row in files],
            [row.repository_path for row in acquisition.EXPECTED_FILES],
        )
        self.assertEqual(len({row["repository_path"] for row in files}), 36)
        self.assertEqual(
            Counter(row["partition"] for row in files),
            {"source_fit_missing": 6, "fresh_final": 30},
        )
        self.assertEqual(sum(row["size_bytes"] for row in files), 92414976)
        metadata._assert_target_free(self.inventory)

    def test_validators_and_transport_are_complete_and_body_blind(self):
        remote = self.result["remote_inventory"]
        self.assertEqual(remote["validator_availability"], {
            "etag": 36,
            "last_modified": 36,
            "accept_ranges": 36,
        })
        self.assertEqual(remote["unavailable_optional_validator_fields"], [])
        transport = self.inventory["transport"]
        self.assertEqual(transport["method"], "HEAD")
        self.assertEqual(transport["requests"], 36)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["retries"], 0)
        self.assertEqual(transport["response_body_reads"], 0)
        self.assertEqual(transport["response_body_bytes"], 0)

    def test_resources_pass_and_every_nonmetadata_operation_is_zero(self):
        measured = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertEqual(measured["real_HEAD_requests"], 36)
        self.assertLessEqual(measured["runtime_seconds"], caps["wall_time_seconds"])
        self.assertLessEqual(
            measured["peak_process_tree_RSS_bytes"],
            caps["peak_process_tree_RSS_bytes"],
        )
        self.assertLessEqual(measured["output_bytes"], caps["generated_output_bytes"])
        self.assertGreaterEqual(
            measured["initial_free_disk_bytes"], caps["minimum_free_disk_bytes"]
        )
        for key in (
            "mock_HEAD_requests",
            "redirects",
            "retries",
            "response_body_reads",
            "response_body_bytes",
            "local_real_data_path_operations",
            "EDF_body_header_annotation_event_or_signal_reads",
            "payload_download_bytes",
            "target_or_label_reads",
            "parameter_update_fits",
            "model_inference_runs",
            "model_runs",
            "training_runs",
            "scoring_events",
            "new_payload_bytes",
        ):
            self.assertEqual(measured[key], 0)

    def test_payload_and_scientific_claims_remain_closed(self):
        gate = self.result["next_gate"]
        self.assertFalse(gate["payload_acquisition_authorized_by_result"])
        self.assertFalse(gate["EDF_content_access_authorized_by_result"])
        self.assertFalse(gate["fresh_final_acquisition_authorized_now"])
        boundary = self.result["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        self.assertFalse(boundary["unseen_participant_generalization_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
