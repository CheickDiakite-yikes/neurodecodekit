from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc1_source_aware_inventory_attestation_contract.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1SourceAwareInventoryAttestationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_bytes())

    def test_identity_status_and_lane_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_source_aware_inventory_attestation_contract",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-SA1")
        self.assertEqual(
            self.record["status"],
            "frozen_generated_only_requires_green_before_implementation",
        )

    def test_artifact_bindings_are_current(self) -> None:
        for binding in self.record["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_green_research_precedes_registration(self) -> None:
        proof = self.record["green_research_proof"]
        self.assertEqual(
            proof["commit"], "aa805038cc28c64ad75ddcb0e14768fdcb3cd96e"
        )
        self.assertEqual(proof["CI_run_id"], 31614330447)
        self.assertEqual(proof["base_python_job_id"], 94173234952)
        self.assertEqual(proof["optional_neuro_job_id"], 94173234944)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_command_and_dependency_surface_is_generated_only(self) -> None:
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertFalse(surface["network_client_or_URL_opener"])
        self.assertFalse(surface["execute_command"])
        self.assertFalse(surface["payload_signal_target_model_or_score_interface"])

    def test_six_fixture_families_and_routes_are_exact(self) -> None:
        families = self.record["generated_semantic_families"]
        self.assertEqual(len(families), 6)
        self.assertEqual(families["documented_public_core_exact"]["route"], "MARC1SA-R2")
        self.assertEqual(families["observed_extension_exact"]["route"], "MARC1SA-R1")
        self.assertEqual(families["partial_optional_extension_exact"]["route"], "MARC1SA-R2")
        self.assertEqual(families["single_historical_drift"]["route"], "MARC1SA-R3")
        self.assertEqual(families["multiple_historical_drifts"]["route"], "MARC1SA-R3")
        self.assertEqual(families["unknown_non_target_extension"]["route"], "MARC1SA-R4")

    def test_partial_MD5_availability_pattern_is_exact(self) -> None:
        partial = self.record["generated_semantic_families"]["partial_optional_extension_exact"]
        self.assertEqual(partial["both_MD5_fields"], 18)
        self.assertEqual(partial["supplied_only"], 18)
        self.assertEqual(partial["computed_only"], 9)
        self.assertEqual(partial["neither"], 10)
        self.assertEqual(partial["supplied_present_total"], 36)
        self.assertEqual(partial["computed_present_total"], 27)
        self.assertEqual(partial["agreeing_pairs"], 18)

    def test_predicate_and_hash_contracts_are_exact(self) -> None:
        self.assertEqual(len(self.record["predicate_vector_fields"]), 21)
        domains = self.record["identity_domains"]
        self.assertEqual(len(domains), 7)
        self.assertEqual(len(set(domains.values())), 7)
        self.assertTrue(self.record["predicate_policy"]["ordinary_mismatches_do_not_short_circuit"])
        self.assertTrue(self.record["predicate_policy"]["unsafe_structure_or_target_leakage_refuses"])

    def test_refusal_matrix_has_52_unique_names(self) -> None:
        matrix = self.record["refusal_matrix"]
        names = [name for values in matrix.values() for name in values]
        self.assertEqual(len(names), 52)
        self.assertEqual(len(set(names)), 52)
        self.assertEqual(set(self.record["refusal_routes"]), {f"MARC1SA-F0{i}" for i in range(5)})

    def test_private_public_and_cleanup_policy_is_strict(self) -> None:
        output = self.record["output_policy"]
        self.assertEqual(output["maximum_files"], 2)
        self.assertTrue(output["exclusive_no_follow_parent_relative_writes"])
        self.assertEqual(output["public_inspections"], 1)
        self.assertTrue(output["exact_cleanup_required"])
        self.assertFalse(output["raw_response_persisted"])
        self.assertFalse(output["protected_row_values_allowed_in_public"])

    def test_all_25_acceptance_gates_are_frozen(self) -> None:
        gates = self.record["acceptance_gates"]
        self.assertEqual(len(gates), 25)
        self.assertEqual(len(set(gates)), 25)

    def test_resources_are_small_and_single_threaded(self) -> None:
        caps = self.record["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["generated_input_bytes"], 2 * 1024**2)
        self.assertEqual(caps["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)

    def test_every_authorization_and_operation_is_zero(self) -> None:
        self.assertTrue(all(value is False for value in self.record["authorization_flags"].values()))
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_claim_and_next_gate_are_explicit(self) -> None:
        claim = self.record["claim_boundary"]
        gate = self.record["next_gate"]
        self.assertFalse(claim["scientific_claim_established"])
        self.assertFalse(claim["language_or_thought_to_text_established"])
        self.assertTrue(gate["green_contract_before_generated_implementation"])
        self.assertFalse(gate["live_request_authorized"])
        self.assertFalse(gate["payload_authorized"])


if __name__ == "__main__":
    unittest.main()
