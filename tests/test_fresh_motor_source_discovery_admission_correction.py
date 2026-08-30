from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/fresh_motor_source_discovery_admission_correction.v0.json"
)
DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_DISCOVERY_ADMISSION_CORRECTION.md"


class FreshMotorSourceDiscoveryAdmissionCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_proof_closeout_is_bound(self) -> None:
        proof = self.record["predecessor_proof"]
        self.assertEqual(
            proof["commit"], "fac60bfafaa6414da82b075fa677e2aa31c80e22"
        )
        self.assertEqual(proof["CI_run_id"], 33_338_847_448)
        self.assertEqual(proof["base_python_job_id"], 99_330_615_390)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 99_330_615_564)
        self.assertTrue(proof["both_required_jobs_green"])
        for path_key, digest_key in (
            ("implementation_proof_path", "implementation_proof_sha256"),
            ("frontier_v14_path", "frontier_v14_sha256"),
        ):
            payload = (ROOT / proof[path_key]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), proof[digest_key])

    def test_old_packet_is_not_rearmed(self) -> None:
        resolution = self.record["defect_resolution"]
        self.assertFalse(resolution["current_M0_packet_rearmed"])
        self.assertFalse(resolution["current_M0_decision_scope_expanded"])
        self.assertFalse(resolution["missing_revision_values_imputed"])
        self.assertFalse(resolution["tracked_JSON_accepted_as_external_CI_proof"])
        self.assertFalse(resolution["real_transport_added"])
        self.assertFalse(resolution["live_execution_armable"])
        self.assertTrue(resolution["fresh_successor_packet_required"])

    def test_all_five_revision_profiles_remain_null_and_unadmitted(self) -> None:
        revision = self.record["revision_admission_contract"]
        self.assertEqual(
            revision["accepted_modes"],
            ["SOURCE_GLOBAL_REVISION", "OPAQUE_COMPLETE_SNAPSHOT_REPLAY"],
        )
        self.assertFalse(revision["all_profiles_bound"])
        self.assertFalse(revision["witness_execution_authorized"])
        self.assertEqual(len(revision["profiles"]), 5)
        for profile in revision["profiles"]:
            self.assertIsNone(profile["mode"])
            self.assertIsNone(profile["authoritative_issuer"])
            self.assertIsNone(profile["revision_or_snapshot_scope"])
            self.assertIsNone(profile["exact_request_profile_sha256"])
            self.assertIsNone(profile["exact_witness_value_or_ledger_sha256"])
            self.assertIsNone(profile["source_global_revision_evidence"])
            self.assertIsNone(profile["opaque_complete_snapshot_ledger"])
            self.assertFalse(profile["mode_contract_satisfied"])
            self.assertFalse(profile["admitted"])

        mode_contracts = revision["mode_specific_contracts"]
        self.assertTrue(
            mode_contracts["SOURCE_GLOBAL_REVISION"][
                "complete_registered_traversal_covered_must_be_true"
            ]
        )
        snapshot = mode_contracts["OPAQUE_COMPLETE_SNAPSHOT_REPLAY"]
        self.assertTrue(snapshot["complete_must_be_true"])
        self.assertFalse(snapshot["source_semantic_revision_claimed"])
        self.assertIn(
            "ordered_raw_response_body_sha256_values",
            snapshot["required_ledger_fields"],
        )

    def test_external_CI_requires_a_live_check_not_a_saved_receipt(self) -> None:
        witness = self.record["external_CI_witness_contract"]
        self.assertTrue(witness["live_check_must_complete_before_first_source_contact"])
        self.assertFalse(witness["tracked_receipt_is_authority_bearing"])
        self.assertEqual(witness["exact_API_host"], "api.github.com")
        self.assertIsNone(witness["numeric_repository_id"])
        self.assertIsNone(witness["numeric_owner_id"])
        self.assertIsNone(witness["head_repository_id"])
        self.assertIsNone(witness["head_repository_owner_id"])
        self.assertIsNone(witness["workflow_numeric_id"])
        self.assertIsNone(witness["workflow_path"])
        self.assertIsNone(witness["CI_run_id"])
        self.assertIsNone(witness["expected_head_sha"])
        self.assertIsNone(witness["expected_event"])
        self.assertTrue(witness["CI_W0_and_CI_W1_are_distinct_and_non_reusable"])
        self.assertTrue(witness["direct_GET_by_exact_run_id_required"])
        self.assertFalse(witness["search_for_matching_run_allowed"])
        self.assertEqual(
            witness["required_jobs"],
            [
                {"name": "Base Python", "job_id": None},
                {"name": "Optional Neuro Readers", "job_id": None},
            ],
        )
        consumption = witness["attempt_consumption_contract"]
        self.assertTrue(
            consumption[
                "durable_no_follow_marker_before_first_GitHub_DNS_or_socket_operation"
            ]
        )
        self.assertTrue(consumption["CI_and_index_contact_same_process"])
        self.assertFalse(consumption["process_exit_after_CI_can_resume_from_receipt"])
        trust = witness["trust_and_transport_contract"]
        self.assertTrue(trust["proxy_auto_discovery_disabled"])
        self.assertFalse(trust["profile_complete"])
        self.assertEqual(trust["maximum_cache_Age_seconds"], 0)
        self.assertFalse(witness["Sigstore_OIDC_required_for_same_process_gate"])
        self.assertFalse(witness["implemented"])
        self.assertFalse(witness["network_request_authorized"])

    def test_stage_order_separates_observation_freeze_and_discovery(self) -> None:
        self.assertEqual(
            self.record["ordered_successor_route"],
            [
                "R1_G_generated_admission_qualification",
                "R1_W_fresh_all_false_witness_packet_and_exact_green_decision",
                "R1_W_durable_consumed_marker_before_first_GitHub_operation",
                "CI_W0_live_external_CI_verification_before_R1_W_source_contact",
                "R1_W_separately_authorized_index_witness",
                "R1_W_commit_push_and_remote_proof",
                "D1_fresh_all_false_witness_bound_discovery_packet",
                "D1_fresh_packet_bound_decision_and_remote_proof",
                "D1_durable_consumed_marker_before_first_GitHub_operation",
                "CI_W1_live_external_CI_verification_before_D1_source_contact",
                "D1_one_complete_or_park_discovery",
            ],
        )
        self.assertTrue(
            self.record["revision_admission_contract"][
                "observation_and_admission_are_separate_irreversible_events"
            ]
        )
        self.assertFalse(
            self.record["revision_admission_contract"][
                "runtime_learned_revision_can_be_admitted_in_same_discovery"
            ]
        )

    def test_only_strategy_commit_and_CI_are_open(self) -> None:
        authority = self.record["operation_authority_now"]
        self.assertTrue(authority["strategy_document_commit_push_and_CI"])
        for key, value in authority.items():
            if key != "strategy_document_commit_push_and_CI":
                self.assertFalse(value, key)

    def test_scientific_coordinates_and_language_boundary_do_not_move(self) -> None:
        coordinate = self.record["scientific_evidence_coordinate"]
        for dimension in range(1, 7):
            value = coordinate[f"dimension_{dimension}_" + {
                1: "spatial",
                2: "temporal",
                3: "physiological",
                4: "task_autonomy",
                5: "population_generalization",
                6: "translation",
            }[dimension]]
            self.assertTrue(value.startswith("unchanged_"), value)
        self.assertFalse(coordinate["live_motor_success_validates_language"])
        self.assertTrue(coordinate["communication_requires_separate_preregistration"])
        self.assertTrue(
            coordinate["communication_requires_independently_scored_LM_only_baseline"]
        )

    def test_document_states_capability_nonclaim_and_no_authority(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability specified:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("3D attribution cube", document)
        self.assertIn("This correction authorizes no generated execution", document)


if __name__ == "__main__":
    unittest.main()
