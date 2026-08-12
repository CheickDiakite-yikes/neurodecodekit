from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries/marc1_versioned_pagination_recovery_contract.v0.json"
)
DOCUMENT_PATH = (
    ROOT / "docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_PREREGISTRATION.md"
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


class MARC1VersionedPaginationRecoveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_identity_status_and_route_are_exact(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc1_versioned_pagination_recovery_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC1-PG1")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_contract_real_inputs_and_execution_unauthorized",
        )
        self.assertEqual(self.contract["acceptance_route"], "MARC1PG-G1")

    def test_green_research_anchor_and_hashes_are_exact(self) -> None:
        anchor = self.contract["green_research_anchor"]
        self.assertEqual(
            anchor["commit"],
            "7a7883abda094eb9f202215b8b138a17cdff022e",
        )
        self.assertEqual(anchor["CI_run_id"], 31591022429)
        self.assertEqual(anchor["base_python_job_id"], 94095736694)
        self.assertEqual(anchor["optional_neuro_job_id"], 94095736770)
        self.assertTrue(anchor["both_required_jobs_green"])
        for name in ("research_document", "research_registry"):
            binding = anchor[name]
            self.assertEqual(_sha256(ROOT / binding["path"]), binding["SHA256"])

    def test_frozen_sources_match_and_consumed_lane_stays_closed(self) -> None:
        bindings = self.contract["frozen_source_bindings"]
        for binding in bindings.values():
            self.assertEqual(_sha256(ROOT / binding["path"]), binding["SHA256"])
        self.assertFalse(bindings["generated_selector"]["modification_authorized"])
        self.assertFalse(
            bindings["generated_HTTP_semantics"]["modification_authorized"]
        )
        consumed = bindings["consumed_aggregate_result"]
        self.assertEqual(consumed["route"], "MARC1HTL-F04")
        self.assertFalse(consumed["retry_or_rerun"])
        self.assertFalse(consumed["private_root_access_authorized"])

    def test_candidate_policy_hash_and_request_are_exact(self) -> None:
        policy = self.contract["candidate_pagination_policy"]
        self.assertEqual(
            _canonical_sha256(policy),
            self.contract["candidate_pagination_policy_SHA256"],
        )
        request = policy["request"]
        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["path"], "/v2/articles/29666735/versions/3/files")
        self.assertEqual(request["query"], "page=1&page_size=1000")
        self.assertEqual(request["query_items"], [["page", "1"], ["page_size", "1000"]])
        self.assertEqual((request["page"], request["page_size"]), (1, 1000))
        response = policy["response"]
        self.assertEqual(response["body_count"], 1)
        self.assertEqual(response["exact_rows_required"], 55)
        self.assertEqual(response["second_page_requests"], 0)
        self.assertEqual(response["fallback_requests"], 0)
        self.assertFalse(response["partial_page_accepted"])

    def test_generated_surface_has_no_live_or_private_executor(self) -> None:
        surface = self.contract["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        forbidden = set(surface) - {
            "module",
            "commands",
            "execute_command",
            "standard_library_only",
            "base_dependency_delta",
        }
        self.assertTrue(all(surface[name] == 0 for name in forbidden))

    def test_generated_inputs_and_matrices_are_exact(self) -> None:
        inputs = self.contract["generated_inputs"]
        self.assertEqual(inputs["Freewill_rows"], 1227)
        self.assertEqual(inputs["Wrist_rows"], 55)
        self.assertEqual(inputs["Wrist_participant_archives"], 45)
        self.assertEqual(inputs["Wrist_supplementary_rows"], 10)
        self.assertEqual(inputs["private_selection_rows"], 300)
        self.assertEqual(inputs["accepted_mock_cases"], 4)
        self.assertEqual(inputs["refused_mock_mutations"], 41)
        self.assertEqual(inputs["network_bytes"], 0)
        self.assertEqual(len(self.contract["accepted_cases"]), 4)
        self.assertEqual(len(set(self.contract["accepted_cases"])), 4)
        self.assertEqual(len(self.contract["refusal_cases"]), 41)
        self.assertEqual(len(set(self.contract["refusal_cases"])), 41)
        self.assertIn("ten_row_partial_page", self.contract["refusal_cases"])
        self.assertIn(
            "second_generated_closeout_invocation",
            self.contract["refusal_cases"],
        )

    def test_semantic_identity_does_not_weaken_the_selector(self) -> None:
        identity = self.contract["semantic_identity"]
        self.assertEqual(identity["record_id"], 29666735)
        self.assertEqual(identity["version_id"], 3)
        self.assertEqual(identity["exact_file_rows"], 55)
        self.assertEqual(identity["participant_archives"], 45)
        self.assertEqual(identity["supplementary_rows"], 10)
        self.assertEqual(identity["declared_record_bytes"], 3683416050)
        self.assertEqual(identity["sub_01_file_id"], 62570743)
        self.assertEqual(identity["sub_01_bytes"], 33690749)
        self.assertTrue(identity["target_like_extra_fields_refused"])
        self.assertFalse(identity["partial_page_or_partial_cohort_accepted"])

    def test_routes_gates_and_resource_caps_are_exact(self) -> None:
        routes = self.contract["failure_routes"]
        self.assertEqual(list(routes), [f"MARC1PG-F0{index}" for index in range(8)])
        gates = self.contract["acceptance_gates"]
        self.assertEqual(len(gates), 18)
        self.assertEqual(len(set(gates)), 18)
        caps = self.contract["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["generated_input_bytes"], 2 * 1024**2)
        self.assertEqual(caps["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)

    def test_evidence_order_keeps_live_access_closed(self) -> None:
        order = self.contract["evidence_order"]
        self.assertEqual(order[0], "contract_commit_push_both_CI_jobs_green")
        self.assertEqual(order[1], "generated_only_implementation")
        self.assertIn("one_registered_generated_closeout", order)
        self.assertEqual(
            order[-1],
            "all_false_Tier_C_request_only_after_generated_result_green",
        )
        flags = self.contract["authorization_flags"]
        self.assertTrue(flags)
        self.assertTrue(all(value is False for value in flags.values()))
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_claim_boundary_is_same_path_and_not_scientific(self) -> None:
        boundary = self.contract["claim_boundary"]
        self.assertTrue(boundary["same_thought_to_text_path"])
        self.assertFalse(boundary["is_pivot"])
        self.assertIn(
            "no dataset body neural signal",
            boundary["scientific_claim_not_established"],
        )

    def test_human_contract_names_pagination_uncertainty_and_nonclaim(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for value in (
            "page=1&page_size=1000",
            "41 named mutations",
            "not infer that the response held 10 rows",
            "same-path",
            "Engineering capability proposed:",
            "Scientific claim not established:",
        ):
            self.assertIn(value, document)


if __name__ == "__main__":
    unittest.main()
