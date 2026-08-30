from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from neurodecodekit.datasets import fresh_motor_source_discovery as discovery

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/fresh_motor_source_discovery_implementation.v0.json"
HUMAN = ROOT / "docs/FRESH_MOTOR_SOURCE_DISCOVERY_IMPLEMENTATION.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FreshMotorSourceDiscoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_green_decision_binding(self) -> None:
        self.assertEqual(self.registry["implementation_id"], discovery.PROTOCOL_ID)
        self.assertEqual(
            self.registry["green_decision_commit"], discovery.GREEN_DECISION_COMMIT
        )
        self.assertEqual(
            self.registry["implementation_commit_binding"],
            "this_exact_commit_after_push_and_both_required_CI_jobs_green",
        )
        self.assertFalse(
            self.registry["live_execution_status"]["armable_under_current_packet"]
        )
        self.assertTrue(
            self.registry["live_execution_status"][
                "fresh_additive_packet_and_decision_required"
            ]
        )

    def test_registered_plan_digest_and_endpoint_profiles(self) -> None:
        payload = discovery._canonical_json_bytes(discovery.registered_plan())
        registered = self.registry["registered_plan"]
        self.assertEqual(len(payload), registered["canonical_bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), registered["canonical_sha256"])
        profiles = self.registry["endpoint_profiles"]
        self.assertEqual([row["index_id"] for row in profiles], [row.index_id for row in discovery.INDEX_SPECS])
        self.assertEqual([row["endpoint"] for row in profiles], [row.endpoint for row in discovery.INDEX_SPECS])
        self.assertEqual([row["method"] for row in profiles], [row.method for row in discovery.INDEX_SPECS])

    def test_every_bound_artifact_matches_bytes_sha_and_git_blob(self) -> None:
        total = 0
        for row in self.registry["bound_artifacts"]:
            path = ROOT / row["path"]
            self.assertTrue(path.is_file(), row["path"])
            self.assertFalse(path.is_symlink(), row["path"])
            self.assertEqual(path.stat().st_size, row["bytes"], row["path"])
            self.assertEqual(sha256(path), row["sha256"], row["path"])
            observed_blob = subprocess.run(
                ["git", "hash-object", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                timeout=20,
            ).stdout.strip()
            self.assertEqual(observed_blob, row["git_blob"], row["path"])
            total += row["bytes"]
        summary = self.registry["bound_artifact_summary"]
        self.assertEqual(len(self.registry["bound_artifacts"]), summary["count"])
        self.assertEqual(total, summary["bytes"])

    def test_generated_measurements_and_all_zero_protected_operations(self) -> None:
        qualification = self.registry["generated_qualification"]
        self.assertEqual(
            qualification["status"],
            "passed_generated_only_two_replay_qualification",
        )
        self.assertEqual(qualification["replay_count"], 2)
        self.assertEqual(qualification["mock_HTTP_calls"], 34)
        self.assertGreaterEqual(qualification["refusal_case_count"], 21)
        self.assertTrue(qualification["all_refusal_cases_passed"])
        for key in (
            "real_network_requests",
            "real_network_bytes",
            "payload_or_header_reads",
            "signal_event_annotation_target_or_label_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "scores",
            "provider_calls",
            "stream_device_or_hardware_runs",
            "operations_on_other_projects",
            "cleanup_or_deletion_operations",
            "scientific_claim_upgrades",
        ):
            self.assertEqual(qualification[key], 0, key)

    def test_live_authority_and_claims_remain_closed_now(self) -> None:
        authority = self.registry["operation_authority_now"]
        self.assertFalse(authority["public_metadata_network_execution"])
        self.assertFalse(authority["payload_or_header_access"])
        self.assertFalse(authority["model_training_inference_prediction_or_score"])
        self.assertFalse(
            self.registry["live_execution_status"]["real_transport_capability_implemented"]
        )
        self.assertFalse(any(self.registry["claim_boundary"].values()))
        text = HUMAN.read_text(encoding="utf-8")
        self.assertIn("3D attribution cube", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
