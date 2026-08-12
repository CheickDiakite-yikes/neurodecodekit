from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc1_source_aware_inventory_attestation_implementation.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1SourceAwareInventoryAttestationImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_bytes())

    def test_identity_status_and_lane_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_source_aware_inventory_attestation_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-SA1")
        self.assertEqual(
            self.record["status"],
            "generated_implementation_requires_green_before_registered_closeout",
        )

    def test_all_artifact_bindings_are_current(self) -> None:
        for binding in self.record["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_green_contract_proof_is_exact(self) -> None:
        proof = self.record["green_contract_proof"]
        self.assertEqual(proof["commit"], "8f64ccb6dd33df8c81382a9dafd2e84590f50061")
        self.assertEqual(proof["CI_run_id"], 31616551270)
        self.assertEqual(proof["base_python_job_id"], 94180673330)
        self.assertEqual(proof["optional_neuro_job_id"], 94180673125)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_surface_is_generated_only_and_dependency_free(self) -> None:
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertFalse(surface["network_client_or_URL_opener"])
        self.assertFalse(surface["execute_command"])
        self.assertFalse(surface["registered_or_consumed_path_interface"])
        self.assertFalse(surface["payload_signal_target_model_or_score_interface"])

    def test_exact_families_predicates_hashes_refusals_and_gates_pass(self) -> None:
        result = self.record["development_qualification"]
        self.assertEqual(result["overall_route"], "MARC1SA-G1")
        self.assertEqual(result["semantic_families_passed"], 6)
        self.assertEqual(result["predicate_fields"], 21)
        self.assertEqual(result["identity_hash_domains"], 7)
        self.assertEqual(result["refusals_passed"], 52)
        self.assertEqual(result["acceptance_gates_passed"], 25)
        self.assertEqual(
            result["family_routes"],
            {
                "documented_public_core_exact": "MARC1SA-R2",
                "observed_extension_exact": "MARC1SA-R1",
                "partial_optional_extension_exact": "MARC1SA-R2",
                "single_historical_drift": "MARC1SA-R3",
                "multiple_historical_drifts": "MARC1SA-R3",
                "unknown_non_target_extension": "MARC1SA-R4",
            },
        )

    def test_measurements_are_exact_and_below_caps(self) -> None:
        measured = self.record["development_qualification"]["measurements"]
        caps = self.record["resource_caps"]
        self.assertEqual(measured["generated_input_bytes"], 732811)
        self.assertEqual(measured["private_output_bytes"], 95392)
        self.assertEqual(measured["public_output_bytes"], 14197)
        self.assertEqual(measured["combined_output_bytes"], 109589)
        self.assertEqual(measured["peak_RSS_bytes"], 27426816)
        self.assertLess(measured["runtime_seconds"], caps["runtime_seconds"])
        self.assertLess(measured["peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLess(measured["generated_input_bytes"], caps["generated_input_bytes"])
        self.assertLess(measured["combined_output_bytes"], caps["combined_output_bytes"])
        self.assertTrue(measured["exact_cleanup"])

    def test_every_authorization_and_forbidden_counter_is_zero(self) -> None:
        self.assertTrue(all(value is False for value in self.record["authorization_flags"].values()))
        self.assertTrue(all(value == 0 for value in self.record["forbidden_counters"].values()))

    def test_next_gate_and_claim_boundary_are_explicit(self) -> None:
        gate = self.record["next_gate"]
        claim = self.record["claim_boundary"]
        self.assertTrue(gate["green_implementation_before_registered_generated_closeout"])
        self.assertFalse(gate["registered_generated_closeout_authorized_now"])
        self.assertFalse(gate["live_request_authorized"])
        self.assertFalse(gate["payload_authorized"])
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["scientific_claim_established"])
        self.assertFalse(claim["language_or_thought_to_text_established"])


if __name__ == "__main__":
    unittest.main()
