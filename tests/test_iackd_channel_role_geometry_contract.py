import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries" / "iackd_channel_role_geometry_contract.v0.json"
INVENTORY_PATH = ROOT / "registries" / "iackd_openneuro_metadata_inventory.v0.json"
H1_RESULT_PATH = ROOT / "registries" / "iackd_channel_inventory_result.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDChannelRoleGeometryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        cls.h1 = json.loads(H1_RESULT_PATH.read_text(encoding="utf-8"))

    def test_schema_status_and_objective_are_prospective(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.iackd_channel_role_geometry_contract",
        )
        self.assertEqual(self.contract["contract_id"], "IACKD-H2-channel-role-geometry-contract-v0")
        self.assertIn("unauthorized", self.contract["status"])
        self.assertIn("before any future", self.contract["objective"])

    def test_green_research_and_consumed_H1_bindings_are_exact(self) -> None:
        bindings = self.contract["bindings"]
        research = bindings["green_research"]
        self.assertEqual(research["commit"], "41ea1fcc6c31ebe67437ae4d381b4a57cf6cef54")
        self.assertEqual(research["push_CI_run_id"], 31426772597)
        self.assertEqual(research["base_python_job_id"], 93580219586)
        self.assertEqual(research["optional_neuro_readers_job_id"], 93580219644)
        self.assertTrue(research["both_required_jobs_green"])

        h1 = bindings["consumed_H1_result"]
        self.assertEqual(h1["commit"], "a6704898cfb09f6321bac5f15e27424f02614317")
        self.assertEqual(h1["route"], "IACKDH-R5")
        self.assertTrue(h1["consumed"])
        self.assertFalse(h1["rerun_allowed"])

    def test_all_bound_artifact_hashes_are_current(self) -> None:
        bindings = self.contract["bindings"]
        prereg = bindings["human_preregistration"]
        self.assertEqual(_sha256(ROOT / prereg["path"]), prereg["sha256"])
        invariant = bindings["invariant_test"]
        self.assertEqual(_sha256(ROOT / invariant["path"]), invariant["sha256"])
        inventory = bindings["committed_openneuro_inventory"]
        self.assertEqual(_sha256(ROOT / inventory["path"]), inventory["sha256"])
        h1 = bindings["consumed_H1_result"]
        self.assertEqual(_sha256(ROOT / h1["path"]), h1["sha256"])
        research = bindings["green_research"]
        for path_key, hash_key in (
            ("document_path", "document_sha256"),
            ("registry_path", "registry_sha256"),
            ("invariant_test_path", "invariant_test_sha256"),
        ):
            self.assertEqual(_sha256(ROOT / research[path_key]), research[hash_key])

    def test_exact_316_object_surface_replays_from_inventory(self) -> None:
        roles = set(self.contract["source"]["selected_roles"])
        rows = [row for row in self.inventory["selected_objects"] if row["role"] in roles]
        source = self.contract["source"]
        self.assertEqual(len(rows), source["expected_object_count"])
        self.assertEqual(sum(row["size_bytes"] for row in rows), source["expected_total_body_bytes"])

        identity = sorted(
            (
                {
                    key: row[key]
                    for key in ("path", "size_bytes", "etag", "last_modified")
                }
                for row in rows
            ),
            key=lambda row: row["path"],
        )
        encoded = json.dumps(
            identity,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        self.assertEqual(len(encoded), source["canonical_identity_bytes"])
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), source["canonical_identity_sha256"])

        for role in sorted(roles):
            selected = [row for row in rows if row["role"] == role]
            summary = source["role_summaries"][role]
            self.assertEqual(len(selected), summary["objects"])
            self.assertEqual(sum(row["size_bytes"] for row in selected), summary["bytes"])
            self.assertEqual(min(row["size_bytes"] for row in selected), summary["minimum_object_bytes"])
            self.assertEqual(max(row["size_bytes"] for row in selected), summary["maximum_object_bytes"])

        channel_sizes = Counter(
            row["size_bytes"] for row in rows if row["role"] == "channels"
        )
        self.assertEqual(channel_sizes, Counter({1752: 96, 1866: 32}))
        self.assertFalse(source["VHDR_reread_allowed"])
        self.assertFalse(source["existing_local_bundle_may_be_used"])

    def test_H1_reconciliation_anchor_matches_consumed_result(self) -> None:
        anchor = self.contract["H1_reconciliation_anchor"]
        diagnosis = self.h1["diagnosis"]
        self.assertEqual(anchor["header_count"], self.h1["measurements"]["input_objects"])
        self.assertEqual(anchor["header_bytes"], self.h1["measurements"]["input_bytes"])
        self.assertEqual(anchor["header_rereads"], 0)
        self.assertEqual(
            [
                (row["declared_channel_count"], row["occurrence_count"])
                for row in anchor["declared_channel_count_groups"]
            ],
            [
                (row["declared_channel_count"], row["occurrence_count"])
                for row in diagnosis["signature_groups"]
            ],
        )
        self.assertFalse(anchor["actual_EEG_count_inferred"])

    def test_transport_is_one_pass_sequential_and_body_bounded(self) -> None:
        fetch = self.contract["fetch_contract"]
        self.assertEqual(fetch["transport"], "python_standard_library_https")
        self.assertTrue(fetch["canonical_path_order"])
        self.assertTrue(fetch["sequential_requests_only"])
        self.assertEqual(fetch["maximum_concurrent_requests"], 1)
        self.assertEqual(fetch["requests"], 316)
        self.assertFalse(fetch["redirects_allowed"])
        self.assertFalse(fetch["retries_allowed"])
        self.assertEqual(fetch["body_SHA256_passes_per_object"], 1)
        self.assertEqual(fetch["semantic_parse_passes_per_object"], 1)
        self.assertFalse(fetch["raw_body_persisted"])
        self.assertTrue(fetch["raw_body_discarded_before_next_request"])
        self.assertTrue(fetch["private_consumed_marker_before_first_request"])

    def test_channel_parser_and_role_policy_are_explicit(self) -> None:
        parser = self.contract["channels_TSV_contract"]
        self.assertEqual(parser["required_first_columns"], ["name", "type", "units"])
        self.assertFalse(parser["duplicate_column_names_allowed"])
        self.assertEqual((parser["minimum_rows"], parser["maximum_rows"]), (1, 64))
        self.assertTrue(parser["type_must_be_uppercase"])
        self.assertEqual(parser["allowed_status_values"], ["good", "bad", "n/a"])
        self.assertEqual(len(parser["registered_BIDS_types"]), len(set(parser["registered_BIDS_types"])))
        self.assertIn("EEG", parser["registered_BIDS_types"])
        self.assertIn("TRIG", parser["registered_BIDS_types"])

        policy = self.contract["semantic_role_policy"]
        self.assertEqual(policy["predictive_EEG_candidate"], "type_EEG_excluding_exact_M1_M2_names")
        self.assertFalse(policy["trigger"]["predictive"])
        self.assertEqual(policy["optional_mastoid_or_reference_candidates"], ["M1", "M2"])
        self.assertIsNone(policy["expected_core_EEG_count"])
        self.assertFalse(policy["MNE_inferred_type_authoritative"])

    def test_sidecar_and_geometry_contracts_preserve_unavailable_values(self) -> None:
        sidecar = self.contract["eeg_sidecar_contract"]
        self.assertIn("EEGReference", sidecar["required_fields"])
        self.assertIn("SamplingFrequency", sidecar["public_allowlisted_fields"])
        self.assertTrue(sidecar["recommended_count_fields_may_be_missing"])
        self.assertFalse(sidecar["free_text_public"])

        electrodes = self.contract["electrodes_TSV_contract"]
        self.assertEqual(electrodes["required_first_columns"], ["name", "x", "y", "z"])
        self.assertFalse(electrodes["coordinate_values_public"])
        coordinate = self.contract["coordsystem_JSON_contract"]
        self.assertEqual(coordinate["allowed_units"], ["m", "cm", "mm"])
        self.assertFalse(coordinate["fiducial_anatomical_or_coordinate_values_public"])

        link = self.contract["geometry_link_contract"]
        self.assertEqual(link["geometry_groups"], 30)
        self.assertFalse(link["equal_channel_and_electrode_row_counts_required"])
        self.assertFalse(link["source_paths_public"])
        self.assertFalse(link["participant_identity_public"])

    def test_router_is_ordered_and_occipital_view_cannot_rescue_R4(self) -> None:
        router = self.contract["diagnostic_router_order"]
        self.assertEqual(
            [row["route"] for row in router],
            ["IACKDR-R0", "IACKDR-R1", "IACKDR-R2", "IACKDR-R3", "IACKDR-R4"],
        )
        self.assertIn("C3_C4_Cz", router[3]["condition"])
        occipital = self.contract["occipital_policy"]
        self.assertTrue(occipital["O1_Oz_O2_geometry_reported"])
        self.assertFalse(occipital["gates_IACKDR_R4"])
        self.assertTrue(occipital["complete_availability_required_for_future_IACKD2_occipital_proxy"])

    def test_public_output_is_aggregate_and_forbidden_fields_are_explicit(self) -> None:
        aggregate = self.contract["aggregate_contract"]
        self.assertFalse(aggregate["individual_paths_public"])
        self.assertFalse(aggregate["individual_status_rows_public"])
        self.assertFalse(aggregate["participant_outcomes_public"])
        forbidden = set(self.contract["forbidden_public_fields"])
        self.assertTrue(
            {
                "raw_body",
                "source_path",
                "local_path",
                "electrode_coordinates",
                "signal",
                "event",
                "trajectory",
                "target",
                "model",
                "prediction",
                "participant_outcome",
            }.issubset(forbidden)
        )

    def test_resources_and_acceptance_gates_are_exact(self) -> None:
        caps = self.contract["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["concurrent_numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["wall_time_seconds"], 180)
        self.assertEqual(caps["requests"], 316)
        self.assertEqual(caps["expected_body_bytes"], 457602)
        self.assertEqual(caps["network_body_bytes"], 2 * 1024 * 1024)
        self.assertEqual(caps["incremental_disk_bytes"], 4 * 1024 * 1024)
        self.assertEqual((caps["retries"], caps["reruns"]), (0, 0))
        self.assertIsNone(caps["producer_is_causal"])
        self.assertFalse(caps["end_to_end_latency_measured"])
        self.assertEqual(len(self.contract["acceptance_gates"]), 9)

    def test_stage_order_keeps_real_access_behind_a_fresh_decision(self) -> None:
        stages = self.contract["ordered_stages"]
        synthetic = stages["stage_I"]
        self.assertEqual(synthetic["tier"], "B")
        self.assertTrue(
            synthetic["eligible_only_after_registration_commit_pushed_and_both_CI_jobs_green"]
        )
        self.assertTrue(synthetic["generated_BIDS_metadata_fixtures_only"])
        self.assertFalse(synthetic["real_or_local_IACKD_access"])

        real = stages["stage_R"]
        self.assertEqual(real["tier"], "C")
        self.assertTrue(real["separate_all_false_request_and_packet_bound_maintainer_decision_required"])
        self.assertTrue(real["decision_commit_must_be_pushed_and_both_CI_jobs_green"])
        self.assertFalse(real["currently_authorized"])
        self.assertEqual((real["registered_execution_count"], real["retry_count"], real["rerun_count"]), (1, 0, 0))

    def test_current_counters_are_zero_and_authorization_is_narrow(self) -> None:
        self.assertTrue(all(value == 0 for value in self.contract["current_access_counters"].values()))
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["tier_B_synthetic_implementation_eligible_after_registration_green"])
        self.assertTrue(authorization["generated_fixture_creation"])
        self.assertTrue(authorization["mocked_transport_qualification"])
        for key, value in authorization.items():
            if key in {
                "tier_B_synthetic_implementation_eligible_after_registration_green",
                "generated_fixture_creation",
                "mocked_transport_qualification",
            }:
                continue
            self.assertFalse(value, key)

    def test_document_preserves_engineering_and_scientific_boundaries(self) -> None:
        document_path = ROOT / self.contract["bindings"]["human_preregistration"]["path"]
        document = document_path.read_text(encoding="utf-8")
        self.assertIn("Engineering capability proposed:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No substitution", document)
        self.assertIn("The retained IACKD bundle remains closed", " ".join(self.contract["warnings"]))
        self.assertIn("cannot establish a neural effect", self.contract["claim_boundary"]["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
