from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc1_versioned_pagination_recovery_research.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/MARC_1_VERSIONED_PAGINATION_RECOVERY_RESEARCH.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1VersionedPaginationRecoveryResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_status_and_zero_access_posture_are_exact(self) -> None:
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc1_versioned_pagination_recovery_research",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC1-PG1")
        self.assertEqual(
            self.registry["status"],
            "tier_A_pagination_recovery_research_complete_zero_dataset_specific_requests",
        )
        self.assertFalse(self.registry["authorized_now"])

    def test_every_local_artifact_binding_matches(self) -> None:
        for binding in self.registry["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_green_consumed_result_is_bound_without_private_access(self) -> None:
        result = self.registry["green_consumed_result"]
        self.assertEqual(result["commit"], "1337a91ca2dd1f988ddcfc36631b7a1a8d832b0f")
        self.assertEqual(result["push_CI_run_id"], 31589739739)
        self.assertEqual(result["base_python_job_id"], 94091696454)
        self.assertEqual(result["optional_neuro_job_id"], 94091696340)
        self.assertEqual(result["route"], "MARC1HTL-F04")
        self.assertTrue(result["consumed_no_retry_or_rerun"])
        self.assertEqual(result["private_or_consumed_root_operations_in_research"], 0)

    def test_official_source_commit_and_pagination_facts_are_exact(self) -> None:
        source = self.registry["official_Figshare_OpenAPI"]
        self.assertEqual(source["commit"], "751101d87c8fcea45556492bc627499ff49b0f2b")
        self.assertEqual(source["version_files_operation_id"], "article_version_files")
        self.assertEqual(source["page_minimum"], 1)
        self.assertEqual(source["page_maximum"], 5000)
        self.assertEqual(source["page_size_minimum"], 1)
        self.assertEqual(source["page_size_default"], 10)
        self.assertEqual(source["page_size_maximum"], 1000)
        self.assertEqual(source["ArticleComplete_embedded_files_maximum"], 10)
        self.assertEqual(source["dataset_specific_requests"], 0)

    def test_diagnosis_preserves_hypothesis_uncertainty(self) -> None:
        hypotheses = self.registry["failure_hypotheses"]
        self.assertEqual(tuple(hypotheses), ("H1", "H2", "H3"))
        self.assertEqual(hypotheses["H1"]["name"], "omitted_pagination")
        self.assertTrue(hypotheses["H1"]["leading_engineering_hypothesis"])
        self.assertFalse(hypotheses["H1"]["proven_by_consumed_result"])
        self.assertFalse(self.registry["inference_firewall"]["actual_live_row_count_known"])
        self.assertFalse(self.registry["inference_firewall"]["actual_live_row_count_is_10"])

    def test_prospective_request_identity_is_one_explicit_page(self) -> None:
        request = self.registry["prospective_request_identity"]
        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["article_id"], 29666735)
        self.assertEqual(request["version_id"], 3)
        self.assertEqual(request["query"], "page=1&page_size=1000")
        self.assertEqual(request["page"], 1)
        self.assertEqual(request["page_size"], 1000)
        self.assertEqual(request["response_body_count"], 1)
        self.assertEqual(request["second_page_requests"], 0)
        self.assertEqual(request["fallback_requests"], 0)
        self.assertEqual(request["payload_requests"], 0)

    def test_semantic_identity_preserves_the_frozen_55_row_contract(self) -> None:
        identity = self.registry["semantic_identity"]
        self.assertEqual(identity["exact_file_rows"], 55)
        self.assertEqual(identity["participant_archives"], 45)
        self.assertEqual(identity["supplementary_rows"], 10)
        self.assertEqual(identity["declared_record_bytes"], 3683416050)
        self.assertEqual(identity["sub_01_file_id"], 62570743)
        self.assertEqual(identity["sub_01_bytes"], 33690749)
        self.assertTrue(identity["target_like_extra_fields_refused"])
        self.assertFalse(identity["partial_page_or_partial_cohort_accepted"])

    def test_next_sequence_is_generated_first_and_live_closed(self) -> None:
        sequence = self.registry["smallest_next_evidence_sequence"]
        self.assertEqual(sequence[0], "green_this_research_record")
        self.assertEqual(sequence[1], "freeze_generated_only_pagination_contract")
        self.assertIn("green_generated_implementation", sequence)
        self.assertIn("green_registered_generated_closeout", sequence)
        self.assertEqual(sequence[-1], "fresh_Tier_C_decision_before_any_new_live_body")
        flags = self.registry["authorization_flags"]
        self.assertTrue(flags)
        self.assertTrue(all(value is False for value in flags.values()))

    def test_all_dataset_private_neural_and_claim_counters_are_zero(self) -> None:
        counters = self.registry["access_counters"]
        forbidden = (
            "dataset_specific_Figshare_requests",
            "dataset_specific_response_bytes",
            "private_Freewill_manifest_operations",
            "consumed_private_root_operations",
            "payload_requests",
            "payload_bytes",
            "signal_sample_reads",
            "target_or_label_reads",
            "model_runs",
            "training_runs",
            "scoring_events",
            "scientific_claim_upgrades",
            "operations_on_other_projects",
        )
        for key in forbidden:
            with self.subTest(key=key):
                self.assertEqual(counters[key], 0)

    def test_router_resources_and_claim_boundary_are_bounded(self) -> None:
        router = self.registry["prospective_router"]
        self.assertEqual(len(router["ordered_failure_routes"]), 8)
        self.assertEqual(router["generated_success_route"], "MARC1PG-G1")
        self.assertFalse(router["success_is_scientific_result"])
        caps = self.registry["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 268435456)
        self.assertEqual(caps["generated_input_bytes"], 2097152)
        self.assertEqual(caps["generated_output_bytes"], 2097152)
        boundary = self.registry["claim_boundary"]
        self.assertTrue(boundary["same_thought_to_text_path"])
        self.assertFalse(boundary["is_pivot"])
        self.assertIn("no neural effect", boundary["scientific_claim_not_established"])

    def test_human_record_is_explicit_about_pagination_and_nonclaim(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for value in (
            "page=1&page_size=1000",
            "default page size of\n10",
            "actual row count",
            "not yet proven",
            "This is not a pivot",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(value, document)


if __name__ == "__main__":
    unittest.main()
