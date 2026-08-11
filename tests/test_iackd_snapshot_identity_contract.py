import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries" / "iackd_snapshot_identity_contract.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IackdSnapshotIdentityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_schema_identity_and_status(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.iackd_snapshot_identity_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["contract_id"],
            "IACKD-M1-snapshot-identity-contract-v0",
        )
        self.assertIn("public_GraphQL_unauthorized", self.contract["status"])

    def test_every_local_binding_is_current(self):
        for binding in self.contract["bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_research_proof_is_exact(self):
        proof = self.contract["green_research_proof"]
        self.assertEqual(
            proof["commit"], "723c8e244ff5f414cb4859bd122d42cccfaa795f"
        )
        self.assertEqual(proof["CI_run_id"], 31_480_538_821)
        self.assertEqual(proof["base_python_job_id"], 93_744_221_145)
        self.assertEqual(proof["optional_neuro_job_id"], 93_744_221_059)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_exact_query_and_request_body_are_hash_bound(self):
        query = self.contract["GraphQL_contract"]
        query_bytes = query["query_text"].encode("utf-8")
        self.assertEqual(hashlib.sha256(query_bytes).hexdigest(), query["query_sha256"])
        request_body = (
            json.dumps(
                {"query": query["query_text"]},
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(request_body).hexdigest(), query["request_body_sha256"]
        )
        self.assertEqual(query["requests_if_future_authorized"], 1)
        self.assertFalse(query["variables_or_fallbacks_allowed"])

    def test_snapshot_and_description_shapes_are_strict(self):
        snapshot = self.contract["snapshot_anchor_contract"]
        self.assertEqual(snapshot["id"], "ds006840:1.0.0")
        self.assertEqual(snapshot["tag"], "1.0.0")
        self.assertEqual(snapshot["hexsha"], "lowercase_hex_40_or_64")
        self.assertTrue(snapshot["description_id_must_equal_hexsha"])
        self.assertEqual(
            set(snapshot["critical_description"]),
            {"Name", "BIDSVersion", "License", "DatasetDOI"},
        )

    def test_tree_and_selected_inventory_are_exact(self):
        tree = self.contract["recursive_tree_contract"]
        selected = self.contract["selected_inventory_contract"]
        self.assertEqual(tree["file_count"], 1679)
        self.assertEqual(tree["total_bytes"], 7_966_799_433)
        self.assertTrue(tree["full_relative_paths_unique_and_safe"])
        self.assertTrue(tree["public_S3_versionId_required"])
        self.assertEqual(selected["participant_count"], 15)
        self.assertEqual(selected["bids_run_count"], 128)
        self.assertEqual(selected["object_count"], 1340)
        self.assertEqual(selected["payload_bytes"], 7_249_113_684)
        self.assertEqual(len(selected["role_summaries"]), 12)

    def test_raw_transport_is_provenance_not_identity(self):
        transport = self.contract["transport_contract"]
        self.assertFalse(transport["raw_response_SHA_is_acceptance_identity"])
        self.assertFalse(transport["Content_Length_is_scientific_identity"])
        self.assertTrue(transport["raw_response_SHA_recorded"])
        self.assertEqual(transport["response_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["retries"], 0)

    def test_generated_qualification_is_closed_to_real_access(self):
        fixture = self.contract["generated_qualification_contract"]
        self.assertEqual(fixture["constructed_file_rows"], 1679)
        self.assertEqual(fixture["deterministic_replays"], 2)
        self.assertGreaterEqual(len(fixture["required_refusals"]), 30)
        self.assertFalse(fixture["URL_opener_socket_or_HTTP_client_allowed"])
        self.assertFalse(fixture["real_endpoint_or_local_IACKD_path_allowed"])
        self.assertFalse(fixture["scientific_claim_value"])

    def test_resources_are_small_and_single_threaded(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["wall_time_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(caps["combined_generated_output_bytes"], 1024 * 1024)
        self.assertEqual(caps["network_bytes"], 0)

    def test_ordered_gates_keep_public_request_tier_c(self):
        stages = self.contract["ordered_stages"]
        self.assertTrue(stages["generated_implementation"]["requires_green_contract"])
        self.assertTrue(stages["tier_C_request"]["requires_green_implementation"])
        self.assertFalse(stages["tier_C_request"]["authorizes_public_access"])
        self.assertTrue(
            stages["tier_C_decision"]["fresh_packet_bound_message_required"]
        )
        self.assertFalse(stages["tier_C_decision"]["current_continue_is_retroactive"])

    def test_all_current_authorizations_and_access_counters_are_zero(self):
        for value in self.contract["authorization_state"].values():
            if isinstance(value, bool):
                self.assertFalse(value)
        for value in self.contract["access_counters"].values():
            self.assertEqual(value, 0)

    def test_router_and_claim_ceiling(self):
        router = self.contract["router"]
        self.assertEqual(router["success_route"], "IACKDM-R1")
        self.assertEqual(len(router["ordered_failure_routes"]), 8)
        self.assertFalse(router["success_is_scientific_result"])
        boundary = self.contract["claim_boundary"]
        self.assertIn("snapshot", boundary["engineering_capability_proposed"])
        self.assertIn("no neural effect", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
