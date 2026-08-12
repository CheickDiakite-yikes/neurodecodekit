from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc1_source_aware_inventory_attestation_research.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1SourceAwareInventoryAttestationResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_bytes())

    def test_identity_status_and_same_path_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_source_aware_inventory_attestation_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-SA1")
        self.assertEqual(
            self.record["status"],
            "tier_A_source_aware_attestation_research_complete_no_live_access",
        )
        self.assertTrue(self.record["same_research_path"]["same_thought_to_text_path"])
        self.assertFalse(self.record["same_research_path"]["is_pivot"])

    def test_artifact_and_evidence_bindings_are_current(self) -> None:
        for binding in self.record["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_consumed_result_is_the_green_anchor(self) -> None:
        proof = self.record["green_consumed_result_proof"]
        self.assertEqual(
            proof["commit"], "d8595098a1a31243e0b147779ed35656a313fd8b"
        )
        self.assertEqual(proof["CI_run_id"], 31612923903)
        self.assertEqual(proof["base_python_job_id"], 94168528552)
        self.assertEqual(proof["optional_neuro_job_id"], 94168528522)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertTrue(proof["lane_consumed"])
        self.assertFalse(proof["retry_or_rerun_allowed"])

    def test_public_core_and_optional_extensions_are_separate(self) -> None:
        policy = self.record["source_schema_policy"]
        self.assertEqual(
            policy["required_public_core_fields"],
            ["id", "name", "size", "is_link_only", "download_url"],
        )
        self.assertEqual(
            policy["known_optional_extension_fields"],
            ["supplied_md5", "computed_md5"],
        )
        self.assertEqual(policy["absent_MD5_state"], "unavailable_not_schema_failure")
        self.assertTrue(policy["target_like_keys_recursively_forbidden"])

    def test_provenance_ladder_keeps_payload_integrity_separate(self) -> None:
        ladder = self.record["provenance_ladder"]
        self.assertEqual(list(ladder), ["public_source_identity", "cohort_identity", "payload_integrity"])
        self.assertTrue(ladder["payload_integrity"]["observed_SHA256_required"])
        self.assertFalse(ladder["payload_integrity"]["provider_MD5_substitutes_for_SHA256"])
        self.assertFalse(ladder["public_source_identity"]["authorizes_payload"])
        self.assertFalse(ladder["cohort_identity"]["authorizes_payload"])

    def test_predicate_vector_is_non_short_circuit_and_aggregate_only(self) -> None:
        vector = self.record["predicate_vector"]
        self.assertTrue(vector["evaluate_all_safe_predicates_after_structural_gate"])
        self.assertGreaterEqual(len(vector["fields"]), 20)
        self.assertTrue(vector["aggregate_counts_and_booleans_public"])
        self.assertFalse(vector["filenames_file_IDs_URLs_or_checksums_public"])
        self.assertFalse(vector["participant_level_results_public"])

    def test_hash_layers_are_domain_separated(self) -> None:
        layers = self.record["identity_layers"]
        self.assertEqual(len(layers), 7)
        self.assertEqual(len(set(layers.values())), 7)
        self.assertIn("public_core_sha256", layers)
        self.assertIn("predicate_vector_sha256", layers)

    def test_router_localizes_without_opening_payload(self) -> None:
        router = self.record["prospective_router"]
        self.assertEqual(len(router["refusal_routes"]), 5)
        self.assertEqual(len(router["aggregate_result_routes"]), 4)
        self.assertEqual(router["generated_success_route"], "MARC1SA-G1")
        self.assertFalse(router["any_route_is_scientific_result"])
        self.assertFalse(router["any_route_authorizes_payload"])

    def test_generated_qualification_covers_both_documented_shapes(self) -> None:
        qualification = self.record["next_generated_qualification"]
        self.assertTrue(qualification["five_field_public_presenter_fixture"])
        self.assertTrue(qualification["seven_field_observed_extension_fixture"])
        self.assertTrue(qualification["multi_predicate_drift_fixture"])
        self.assertTrue(qualification["unknown_extension_fixture"])
        self.assertTrue(qualification["nested_target_firewall_fixtures"])
        self.assertFalse(qualification["URL_opener_available"])
        self.assertFalse(qualification["execute_command_available"])

    def test_resource_caps_are_small_and_single_threaded(self) -> None:
        caps = self.record["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["generated_input_bytes"], 2 * 1024**2)
        self.assertEqual(caps["generated_output_bytes"], 2 * 1024**2)
        verification = self.record["verification"]
        self.assertEqual(verification["MARC_tests"], 680)
        self.assertEqual(verification["dependency_light_tests"], 2819)
        self.assertEqual(verification["optional_neuro_tests"], 2875)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compile_passed"])

    def test_every_current_authority_and_operation_is_zero(self) -> None:
        self.assertTrue(all(value is False for value in self.record["authorization_flags"].values()))
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_claim_boundary_is_explicit(self) -> None:
        claim = self.record["claim_boundary"]
        self.assertFalse(claim["scientific_claim_established"])
        self.assertFalse(claim["language_or_thought_to_text_established"])
        self.assertIn("no dataset-specific body", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
