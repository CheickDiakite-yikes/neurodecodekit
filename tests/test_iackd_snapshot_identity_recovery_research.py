import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "iackd_snapshot_identity_recovery_research.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IackdSnapshotIdentityRecoveryResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_schema_identity_and_tier_a_status(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_snapshot_identity_recovery_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["research_id"],
            "IACKD-M1-snapshot-scoped-identity-research-v0",
        )
        self.assertEqual(
            self.record["status"],
            "tier_A_architecture_research_complete_no_dataset_specific_response",
        )

    def test_artifact_bindings_are_current(self):
        for binding in self.record["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_consumed_lanes_remain_closed(self):
        for lane in self.record["consumed_boundaries"].values():
            self.assertTrue(lane["consumed"])
            self.assertFalse(lane["retry_or_rerun_allowed"])
        self.assertFalse(
            self.record["proof_posture"]["consumed_lane_reopened_or_amended"]
        )

    def test_official_source_commit_and_platform_fields_are_bound(self):
        source = self.record["official_openneuro_source"]
        self.assertRegex(source["commit"], r"^[0-9a-f]{40}$")
        self.assertTrue(source["snapshot_hexsha_exposed"])
        self.assertTrue(source["recursive_files_rooted_at_snapshot_hexsha"])
        self.assertTrue(source["recursive_results_have_full_relative_paths"])
        self.assertTrue(source["public_S3_URLs_carry_versionId"])
        self.assertTrue(source["description_values_may_be_repaired_by_resolver"])
        self.assertGreaterEqual(len(source["source_files"]), 5)

    def test_four_identity_layers_are_independent(self):
        layers = self.record["identity_layers"]
        self.assertEqual(
            list(layers),
            [
                "snapshot_anchor",
                "recursive_snapshot_tree",
                "selected_acquisition_inventory",
                "critical_scientific_metadata",
            ],
        )
        self.assertFalse(layers["snapshot_anchor"]["raw_response_SHA_is_identity"])
        self.assertTrue(
            layers["recursive_snapshot_tree"]["content_addressed_file_IDs_required"]
        )
        self.assertTrue(
            layers["selected_acquisition_inventory"][
                "snapshot_versioned_public_S3_URL_required"
            ]
        )
        self.assertTrue(
            layers["critical_scientific_metadata"][
                "cannot_override_snapshot_or_tree_drift"
            ]
        )

    def test_legacy_compatibility_counts_are_exact(self):
        expected = self.record["legacy_compatibility_gate"]
        self.assertEqual(expected["participant_count"], 15)
        self.assertEqual(expected["bids_run_count"], 128)
        self.assertEqual(expected["selected_object_count"], 1340)
        self.assertEqual(expected["selected_payload_bytes"], 7_249_113_684)
        self.assertEqual(expected["dataset_accession"], "ds006840")
        self.assertEqual(expected["snapshot_tag"], "1.0.0")

    def test_critical_metadata_projection_is_narrow_and_exact(self):
        projection = self.record["critical_metadata_projection"]
        self.assertEqual(
            set(projection), {"Name", "BIDSVersion", "License", "DatasetDOI"}
        )
        self.assertEqual(projection["BIDSVersion"], "1.7.0")
        self.assertEqual(projection["License"], "CC0")
        self.assertEqual(
            projection["DatasetDOI"], "10.18112/openneuro.ds006840.v1.0.0"
        )

    def test_transport_provenance_cannot_rescue_semantic_drift(self):
        policy = self.record["drift_policy"]
        self.assertFalse(policy["raw_response_SHA_is_acceptance_identity"])
        self.assertFalse(policy["HTTP_Content_Length_is_scientific_identity"])
        self.assertFalse(policy["ETag_or_last_modified_can_replace_snapshot_ID"])
        self.assertTrue(policy["snapshot_or_tree_drift_always_parks"])
        self.assertTrue(policy["critical_metadata_drift_always_parks"])

    def test_router_has_one_success_and_ordered_failures(self):
        router = self.record["prospective_router"]
        self.assertEqual(router["success_route"], "IACKDM-R1")
        self.assertEqual(len(router["ordered_failure_routes"]), 8)
        self.assertEqual(
            router["ordered_failure_routes"][0],
            "IACKDM-F00-registration-source-query-or-green-proof-mismatch",
        )
        self.assertEqual(
            router["ordered_failure_routes"][-1],
            "IACKDM-F07-output-runtime-RSS-thread-retry-or-overwrite-failure",
        )
        self.assertFalse(router["success_route_is_scientific_result"])

    def test_next_execution_is_small_and_still_tier_c(self):
        scope = self.record["prospective_metadata_audit"]
        self.assertEqual(scope["public_GraphQL_responses"], 1)
        self.assertEqual(scope["response_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(scope["generated_output_cap_bytes"], 1024 * 1024)
        self.assertEqual(scope["cpu_threads"], 1)
        self.assertEqual(scope["workers"], 1)
        self.assertEqual(scope["retries_or_reruns"], 0)
        self.assertTrue(scope["requires_separate_exact_Tier_C_decision"])

    def test_every_access_and_claim_counter_is_zero(self):
        for value in self.record["access_counters"].values():
            self.assertEqual(value, 0)
        for value in self.record["authorization_flags"].values():
            self.assertFalse(value)

    def test_claim_boundary_is_explicit(self):
        boundary = self.record["claim_boundary"]
        self.assertIn("snapshot-scoped", boundary["engineering_capability_added"])
        self.assertIn("no neural effect", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
