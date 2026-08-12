from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc1_output_capability_recovery_research.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_RESEARCH.md"
SOURCE_PATH = ROOT / "src/neurodecodekit/datasets/marc1_versioned_pagination.py"
REGISTRY_SHA256 = "1bf34df48992bc0574b6b1bd4d14a4f1292f65b74371101dfcf5c48fc89bfd4c"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1OutputCapabilityRecoveryResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_bytes = REGISTRY_PATH.read_bytes()
        cls.record = json.loads(cls.registry_bytes)

    def test_identity_hash_and_artifact_only_status_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.registry_bytes).hexdigest(), REGISTRY_SHA256)
        self.assertEqual(len(self.registry_bytes), 9782)
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_output_capability_recovery_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-OP1")
        self.assertEqual(
            self.record["status"],
            "artifact_only_recovery_design_no_implementation_or_execution",
        )

    def test_all_bound_artifacts_match(self) -> None:
        for binding in self.record["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_green_consumed_result_precedes_research(self) -> None:
        proof = self.record["green_failure_result_proof"]
        self.assertEqual(
            proof["commit"],
            "a4dcaea784f4c3a62547fd4f73bb3e2a5528100a",
        )
        self.assertEqual(proof["CI_run_id"], 31594881048)
        self.assertEqual(proof["base_python_job_id"], 94107907276)
        self.assertEqual(proof["optional_neuro_job_id"], 94107907246)
        self.assertTrue(proof["both_required_jobs_green_before_research"])

    def test_consumed_lane_is_not_reopened(self) -> None:
        boundary = self.record["consumed_boundary"]
        self.assertEqual(boundary["consumed_lane"], "MARC1-PG1")
        self.assertEqual(boundary["consumed_route"], "MARC1PG-F07")
        self.assertEqual(boundary["registered_invocations"], 1)
        self.assertTrue(boundary["generated_operations_preceded_failed_preflight"])
        for key in (
            "retry_or_rerun_available",
            "corrected_path_invocation_available",
            "post_result_implementation_amendment_available",
            "live_metadata_packet_eligible",
        ):
            with self.subTest(key=key):
                self.assertFalse(boundary[key])

    def test_root_cause_matches_the_committed_source_order(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        start = source.index("def qualify_generated_pagination(")
        end = source.index("def inspect_generated_report(", start)
        body = source[start:end]
        self.assertLess(body.index("load_registered_contract(root)"), body.index("_assert_new_output_directory(output)"))
        self.assertLess(body.index("build_generated_wrist_rows()"), body.index("_assert_new_output_directory(output)"))
        self.assertTrue(self.record["root_cause"]["failed_guard_was_too_late"])
        self.assertFalse(self.record["root_cause"]["failed_guard_was_missing"])

    def test_candidate_policy_hash_replays_exactly(self) -> None:
        policy = self.record["candidate_policy"]
        canonical = {
            "before_any": policy["before_any"],
            "network_bytes": policy["network_bytes"],
            "preflight_order": policy["preflight_order"],
            "real_private_input_bytes": policy["real_private_input_bytes"],
            "registered_output_path": policy["registered_output_path"],
            "retries": policy["retries"],
            "schema": policy["schema"],
            "version": policy["version"],
            "write_order": policy["write_order"],
        }
        payload = (json.dumps(canonical, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        self.assertEqual(len(payload), 672)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), policy["sha256"])

    def test_capability_is_held_private_and_parent_relative(self) -> None:
        capability = self.record["output_capability"]
        self.assertTrue(capability["process_local_only"])
        self.assertFalse(capability["serialized"])
        self.assertTrue(capability["all_ancestors_lstat_checked"])
        self.assertTrue(capability["all_symlink_ancestors_refused"])
        self.assertTrue(capability["parent_identity_rechecked_before_write"])
        self.assertTrue(capability["directory_creation_uses_dir_fd"])
        self.assertTrue(capability["file_creation_uses_dir_fd_and_O_EXCL"])
        self.assertFalse(capability["silent_string_only_fallback_allowed"])

    def test_local_capability_observation_is_not_a_portability_claim(self) -> None:
        observation = self.record["local_standard_library_observation"]
        self.assertEqual(observation["python_version"], "3.14.6")
        self.assertEqual(
            set(observation["dir_fd_supported_functions"]),
            {"open", "mkdir", "stat", "unlink", "rmdir"},
        )
        self.assertFalse(observation["observation_is_portability_guarantee"])
        self.assertEqual(
            observation["future_missing_primitive_policy"],
            "refuse_before_repository_or_fixture_access",
        )

    def test_required_refusals_cover_ordering_identity_and_races(self) -> None:
        refusals = self.record["required_future_pre_capability_refusals"]
        self.assertEqual(len(refusals), 19)
        self.assertEqual(len(refusals), len(set(refusals)))
        for required in (
            "immediate_parent_symlink",
            "earlier_ancestor_symlink",
            "lstat_open_device_or_inode_disagreement",
            "output_appears_after_capability_acquisition",
            "repository_contract_import_fixture_selection_or_output_operation_before_capability",
        ):
            with self.subTest(required=required):
                self.assertIn(required, refusals)

    def test_semantics_resources_and_access_remain_bounded(self) -> None:
        identity = self.record["unchanged_pagination_and_selection_identity"]
        self.assertEqual(identity["request_query"], "page=1&page_size=1000")
        self.assertEqual(identity["Wrist_rows"], 55)
        self.assertEqual(identity["selected_subjects_per_axis"], 12)
        self.assertEqual(identity["fit_heldout_overlap"], 0)
        caps = self.record["prospective_resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["real_or_private_input_bytes"], 0)
        counters = self.record["research_access_counters"]
        self.assertEqual(counters["local_standard_library_introspections"], 1)
        for key, value in counters.items():
            if key != "local_standard_library_introspections":
                with self.subTest(key=key):
                    self.assertEqual(value, 0)

    def test_authorization_next_gate_and_claim_boundary_are_explicit(self) -> None:
        self.assertTrue(all(value is False for value in self.record["authorization_flags"].values()))
        self.assertTrue(all(self.record["next_gate"].values()))
        verification = self.record["verification"]
        self.assertEqual(verification["focused_research_tests"], 11)
        self.assertEqual(verification["final_MARC1_tests"], 539)
        self.assertEqual(verification["dependency_light_tests"], 2678)
        self.assertEqual(verification["optional_neuro_tests"], 2749)
        self.assertEqual(verification["additional_skips"], 0)
        self.assertFalse(verification["qualify_or_fixture_operation_during_verification"])
        claim = self.record["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "safe output authority a prerequisite capability",
            "This is not a pivot",
            "Engineering capability proposed:",
            "Scientific claim not established:",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
