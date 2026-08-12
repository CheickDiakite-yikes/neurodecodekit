from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries" / "marc1_http_identity_semantics_recovery_contract.v0.json"
)
DOCUMENT_PATH = (
    ROOT / "docs" / "MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_PREREGISTRATION.md"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


class MARC1HTTPIdentitySemanticsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc1_http_identity_semantics_recovery_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_mock_contract_real_inputs_and_execution_unauthorized",
        )
        self.assertEqual(self.contract["acceptance_route"], "MARC1HT-G1")

    def test_green_research_anchor_and_hashes_are_exact(self) -> None:
        anchor = self.contract["green_research_anchor"]
        self.assertEqual(
            anchor["commit"],
            "f515b36cfdd2b297bcbba9885af92e59ead066a7",
        )
        self.assertEqual(anchor["CI_run_id"], 31580575669)
        self.assertEqual(anchor["base_python_job_id"], 94062432262)
        self.assertEqual(anchor["optional_neuro_job_id"], 94062432241)
        self.assertTrue(anchor["both_required_jobs_green"])
        for name in ("research_document", "research_registry"):
            binding = anchor[name]
            self.assertEqual(_sha256(ROOT / binding["path"]), binding["SHA256"])

    def test_consumed_result_and_generated_selector_are_immutable(self) -> None:
        bindings = self.contract["frozen_source_bindings"]
        for name in ("consumed_live_result", "generated_selector"):
            binding = bindings[name]
            self.assertEqual(_sha256(ROOT / binding["path"]), binding["SHA256"])
        self.assertEqual(bindings["consumed_live_result"]["route"], "MARC1PS-F03")
        self.assertFalse(bindings["consumed_live_result"]["retry_or_rerun"])
        self.assertFalse(bindings["generated_selector"]["modification_authorized"])

    def test_candidate_policy_hash_and_semantics_are_exact(self) -> None:
        policy = self.contract["candidate_transport_policy"]
        expected_hash = self.contract["frozen_source_bindings"][
            "candidate_transport_policy_SHA256"
        ]
        self.assertEqual(_canonical_sha256(policy), expected_hash)
        self.assertEqual(policy["request_Accept_Encoding"], "identity")
        self.assertEqual(
            policy["terminal_Content_Encoding"]["header_absent"],
            "accept_as_no_content_coding",
        )
        self.assertEqual(
            policy["terminal_Content_Encoding"][
                "single_identity_token_case_insensitive"
            ],
            "accept_as_narrow_compatibility_tolerance",
        )
        self.assertEqual(policy["decompression_or_decoding_operations"], 0)

    def test_generated_surface_has_no_real_or_network_executor(self) -> None:
        surface = self.contract["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        forbidden_counts = set(surface) - {
            "module",
            "commands",
            "execute_command",
            "standard_library_only",
            "base_dependency_delta",
        }
        self.assertTrue(all(surface[key] == 0 for key in forbidden_counts))

    def test_exact_generated_inputs_are_bounded_and_target_free(self) -> None:
        inputs = self.contract["generated_inputs"]
        self.assertEqual(inputs["Freewill_rows"], 1_227)
        self.assertEqual(inputs["Wrist_rows"], 55)
        self.assertEqual(inputs["selected_participants_per_axis"], 12)
        self.assertEqual(inputs["Freewill_run_bundles"], 72)
        self.assertEqual(inputs["Freewill_core_members"], 288)
        self.assertEqual(inputs["Wrist_archives"], 12)
        self.assertEqual(inputs["private_selection_rows"], 300)
        self.assertEqual(inputs["real_or_private_input_bytes"], 0)
        self.assertEqual(inputs["network_bytes"], 0)

    def test_acceptance_and_refusal_matrices_are_exact(self) -> None:
        accepted = self.contract["accepted_response_cases"]
        refused = self.contract["refusal_cases"]
        self.assertEqual(len(accepted), 4)
        self.assertEqual(len(set(accepted)), 4)
        self.assertEqual(len(refused), 20)
        self.assertEqual(len(set(refused)), 20)
        self.assertIn("Content_Encoding_absent", accepted)
        self.assertIn("Content_Encoding_identity_plus_gzip", refused)
        self.assertIn("second_invocation", refused)

    def test_routes_and_acceptance_gates_are_non_overlapping_and_exact(self) -> None:
        routes = self.contract["failure_routes"]
        self.assertEqual(len(routes), 5)
        self.assertEqual(set(routes), {f"MARC1HT-F0{index}" for index in range(1, 6)})
        gates = self.contract["acceptance_gates"]
        self.assertEqual(len(gates), 16)
        self.assertEqual(len(set(gates)), 16)

    def test_resource_caps_are_small_and_zero_network(self) -> None:
        caps = self.contract["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(caps["incremental_disk_bytes"], 4 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["real_or_private_input_bytes"], 0)

    def test_all_current_authorization_and_access_values_are_closed(self) -> None:
        flags = self.contract["authorization_flags"]
        self.assertEqual(len(flags), 17)
        self.assertTrue(all(value is False for value in flags.values()))
        self.assertTrue(all(value == 0 for value in self.contract["current_access_counters"].values()))

    def test_document_binds_no_pivot_no_inference_and_claim_ceiling(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for value in (
            "MARC1-HT1",
            "MARC1HT-G1",
            "must not be inferred",
            "same-path",
            "Engineering capability proposed:",
            "Scientific claim not established:",
        ):
            self.assertIn(value, document)


if __name__ == "__main__":
    unittest.main()
