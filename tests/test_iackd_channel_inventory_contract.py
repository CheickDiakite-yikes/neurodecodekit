import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DOCUMENT = ROOT / "docs/IACKD_CHANNEL_INVENTORY_PRIMARY_SOURCE_RESEARCH.md"
PREREGISTRATION = ROOT / "docs/IACKD_CHANNEL_INVENTORY_PREREGISTRATION.md"
RESEARCH_REGISTRY = ROOT / "registries/iackd_channel_inventory_research.v0.json"
CONTRACT_PATH = ROOT / "registries/iackd_channel_inventory_contract.v0.json"
INVENTORY_PATH = ROOT / "registries/iackd_openneuro_metadata_inventory.v0.json"
RESULT_PATH = ROOT / "registries/iackd_cue_action_dissociation_result.v0.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDChannelInventoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.research = json.loads(RESEARCH_REGISTRY.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_public_artifact_hashes_are_current(self):
        bindings = self.contract["bindings"]
        self.assertEqual(
            bindings["primary_source_research_document"]["sha256"],
            sha256(RESEARCH_DOCUMENT),
        )
        self.assertEqual(
            bindings["primary_source_research_registry"]["sha256"],
            sha256(RESEARCH_REGISTRY),
        )
        self.assertEqual(
            bindings["preregistration_document"]["sha256"],
            sha256(PREREGISTRATION),
        )
        self.assertEqual(
            bindings["committed_openneuro_inventory"]["sha256"],
            sha256(INVENTORY_PATH),
        )
        self.assertEqual(
            bindings["consumed_iackd_result"]["sha256"],
            sha256(RESULT_PATH),
        )

    def test_consumed_failure_and_green_closeout_are_exact(self):
        failure = self.research["consumed_failure"]
        self.assertEqual(
            failure["failure_id"],
            "IACKD-F10-channel_sampling_or_geometry_failure",
        )
        self.assertFalse(failure["observed_count_retained"])
        self.assertFalse(failure["observed_names_retained"])
        self.assertFalse(failure["which_predicate_failed_known"])
        self.assertFalse(failure["rerun_allowed"])
        green = self.contract["bindings"]["consumed_iackd_result"]
        self.assertEqual(
            green["closeout_commit"],
            "3a58fccb0db4f0c17e2521773ded248baff68e76",
        )
        self.assertEqual(green["push_CI_run_id"], 31411229793)
        self.assertTrue(green["both_required_jobs_green"])

    def test_exact_header_surface_replays_from_committed_inventory(self):
        headers = sorted(
            (
                row
                for row in self.inventory["selected_objects"]
                if row["path"].endswith(".vhdr")
            ),
            key=lambda row: row["path"],
        )
        source = self.contract["source"]
        self.assertEqual(len(headers), source["expected_object_count"])
        self.assertEqual(
            sum(row["size_bytes"] for row in headers),
            source["expected_total_body_bytes"],
        )
        self.assertEqual(
            sorted({row["size_bytes"] for row in headers}),
            source["unique_object_sizes"],
        )
        first = source["first_deterministic_object"]
        self.assertEqual(
            {name: headers[0][name] for name in first},
            first,
        )
        self.assertEqual(len({row["subject"] for row in headers}), 15)

    def test_public_code_aliases_are_hypotheses_not_observations(self):
        files = self.research["primary_sources"]["upstream_code"]["files"]
        self.assertEqual(
            files[0]["presence_based_deletion_allowlist"],
            ["M1", "M2", "HEOG", "VEOG", "TRIGGER"],
        )
        self.assertEqual(
            files[1]["presence_based_deletion_allowlist"],
            ["HEO", "VEO", "TRIGGER", "HEOG", "VEOG"],
        )
        self.assertFalse(
            self.research["primary_sources"]["upstream_code"]
            ["same_deletion_vocabulary_across_both_pipelines"]
        )
        for hypothesis in self.research["unresolved_hypotheses"]:
            self.assertFalse(hypothesis["supported_as_observed_result"])

    def test_real_stage_and_every_scientific_operation_remain_closed(self):
        stages = self.contract["ordered_stages"]
        self.assertEqual(stages["stage_I"]["tier"], "B")
        self.assertTrue(stages["stage_I"]["generated_VHDR_fixtures_only"])
        self.assertEqual(stages["stage_I"]["network_calls"], 0)
        self.assertEqual(stages["stage_R"]["tier"], "C")
        self.assertFalse(stages["stage_R"]["currently_authorized"])
        self.assertTrue(
            stages["stage_R"]["separate_packet_bound_maintainer_decision_required"]
        )
        authorization = self.contract["authorization"]
        self.assertTrue(
            authorization[
                "tier_B_synthetic_implementation_eligible_after_registration_green"
            ]
        )
        for name, value in authorization.items():
            if name in {
                "tier_B_synthetic_implementation_eligible_after_registration_green",
                "generated_fixture_creation",
                "mocked_transport_qualification",
            }:
                self.assertTrue(value, name)
            else:
                self.assertFalse(value, name)
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_fetch_parser_signature_and_router_are_fail_closed(self):
        fetch = self.contract["fetch_contract"]
        self.assertEqual(fetch["requests"], 128)
        self.assertTrue(fetch["sequential_requests_only"])
        self.assertFalse(fetch["redirects_allowed"])
        self.assertFalse(fetch["retries_allowed"])
        self.assertFalse(fetch["raw_body_persisted"])
        self.assertEqual(fetch["temporary_payload_files"], 0)
        parser = self.contract["parser_contract"]
        self.assertTrue(parser["base_dependencies_only"])
        self.assertFalse(parser["MNE_or_neural_reader"])
        self.assertFalse(parser["sibling_path_construction_resolution_stat_hash_or_open"])
        self.assertFalse(parser["fuzzy_alias_inference"])
        self.assertEqual(
            self.contract["public_name_allowlist"],
            ["M1", "M2", "HEOG", "VEOG", "HEO", "VEO", "TRIGGER"],
        )
        self.assertEqual(
            [row["route"] for row in self.contract["diagnostic_router_order"]],
            [
                "IACKDH-R0",
                "IACKDH-R5",
                "IACKDH-R1",
                "IACKDH-R4",
                "IACKDH-R2",
                "IACKDH-R3",
            ],
        )
        self.assertEqual(len(self.contract["refusal_ids"]), 16)
        self.assertEqual(len(set(self.contract["refusal_ids"])), 16)

    def test_resources_are_small_and_do_not_reopen_large_bundle(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["concurrent_numerical_jobs"], 1)
        self.assertEqual(caps["expected_VHDR_body_bytes"], 161_792)
        self.assertLessEqual(caps["network_body_bytes"], 1024 * 1024)
        self.assertLessEqual(caps["incremental_disk_bytes"], 2 * 1024 * 1024)
        self.assertLessEqual(caps["public_generated_output_bytes"], 1024 * 1024)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertFalse(self.contract["source"]["existing_local_bundle_may_be_used"])

    def test_docs_preserve_metadata_only_claim_ceiling(self):
        research_text = RESEARCH_DOCUMENT.read_text(encoding="utf-8")
        prereg_text = PREREGISTRATION.read_text(encoding="utf-8")
        for text in (research_text, prereg_text):
            self.assertIn("Engineering capability", text)
            self.assertIn("Scientific claim not established:", text)
            self.assertRegex(text.lower(), r"(?:no|zero) reruns?")
        self.assertIn("integrity-contract failure, not a null neural result", research_text)
        self.assertIn("every real-content operation\nremains unauthorized", prereg_text)


if __name__ == "__main__":
    unittest.main()
