import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop54_stage_a_vhdr_contract.v0.json"
PREREG_PATH = REPO_ROOT / "docs" / "LOOP_54_STAGE_A_VHDR_PREREGISTRATION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop54StageAVHDRContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.prereg = PREREG_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_authorization_boundary(self):
        contract = self.contract
        self.assertEqual(
            contract["schema_name"], "neurodecodekit.loop54_stage_a_vhdr_contract"
        )
        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["loop_id"], 54)
        self.assertEqual(contract["stage_id"], "L54-A")
        self.assertEqual(contract["status"], "preregistered_authorization_pending")
        flags = authorization_flags(contract)
        self.assertEqual(flags[0], ("contract_preparation_authorized_now", True))
        self.assertTrue(all(value is False for _, value in flags[1:]), flags)
        self.assertTrue(
            contract["authorization"]["separate_exact_tier_c_authorization_required"]
        )

    def test_dependencies_are_exact_hash_bound_committed_artifacts(self):
        dependencies = self.contract["dependencies"]
        bindings = (
            ("loop53_result", REPO_ROOT / "registries" / "loop53_acquisition_result.v0.json"),
            (
                "loop53_contract",
                REPO_ROOT / "registries" / "loop53_fresh_eeg_acquisition_contract.v0.json",
            ),
            ("loop54_research", REPO_ROOT / "docs" / "LOOP_54_PRIMARY_SOURCE_RESEARCH.md"),
            (
                "loop54_research_registry",
                REPO_ROOT / "registries" / "loop54_eeg_trial_geometry_research.v0.json",
            ),
        )
        for prefix, path in bindings:
            with self.subTest(path=path.name):
                self.assertEqual(dependencies[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(dependencies[f"{prefix}_git_blob"], git_blob_sha1(path))
        self.assertEqual(
            dependencies["loop53_required_status"],
            "consumed_passed_no_rerun_stop_before_loop54",
        )
        self.assertTrue(dependencies["loop53_status_satisfied_from_committed_result"])
        self.assertTrue(dependencies["loop55_preregistration_blocked_until_loop54_closeout"])

    def test_registered_input_is_exactly_one_small_vhdr(self):
        registered = self.contract["registered_input"]
        self.assertEqual(
            registered["vhdr_relative_path"],
            "EEG/EEG/020_DECOMEG_S2_11966_task2.vhdr",
        )
        self.assertEqual(registered["expected_size_bytes"], 11705)
        self.assertEqual(registered["maximum_read_bytes"], 16384)
        self.assertEqual(
            registered["source_identity"], "9ab325a0f8523b675ecab1c97e16169143f1f341"
        )
        self.assertTrue(registered["regular_file_required"])
        self.assertTrue(registered["nofollow_open_required"])
        self.assertTrue(registered["all_path_components_must_be_non_symlink"])
        self.assertFalse(registered["wildcards_allowed"])
        self.assertFalse(registered["substitutions_allowed"])

    def test_parser_is_dependency_light_sibling_blind_and_fail_closed(self):
        parser = self.contract["parser_contract"]
        self.assertTrue(parser["base_python_standard_library_only"])
        self.assertFalse(parser["mne_allowed"])
        self.assertFalse(parser["sibling_resolution_allowed"])
        self.assertFalse(parser["replacement_character_decoding_allowed"])
        self.assertEqual(
            parser["required_sections"],
            ["Common Infos", "Binary Infos", "Channel Infos"],
        )
        self.assertEqual(
            parser["required_binary_info_keys"],
            ["BinaryFormat"],
        )
        self.assertTrue(parser["data_and_marker_references_must_be_exact_basenames"])
        self.assertTrue(
            parser[
                "referenced_siblings_may_be_recorded_as_strings_but_not_resolved_statted_or_opened"
            ]
        )
        for action in (
            "duplicate_section_or_key_action",
            "duplicate_or_missing_channel_action",
            "noncontiguous_channel_index_action",
            "channel_count_mismatch_action",
            "nonpositive_or_nonfinite_sampling_interval_action",
        ):
            self.assertEqual(parser[action], "park", action)

    def test_output_allowlist_excludes_raw_or_protected_content(self):
        output = self.contract["output_contract"]
        self.assertEqual(output["maximum_combined_generated_output_bytes"], 1024**2)
        self.assertFalse(output["raw_vhdr_text_allowed"])
        self.assertFalse(output["comment_content_allowed"])
        self.assertFalse(output["absolute_local_paths_allowed"])
        self.assertFalse(output["marker_signal_mat_target_values_allowed"])
        unavailable = set(self.contract["forced_unavailable_fields"])
        for field in (
            "channel type",
            "measured electrode position",
            "EOG identity",
            "event count",
            "trial count",
            "target text",
            "signal quality",
            "neural advantage",
        ):
            self.assertIn(field, unavailable)

    def test_resources_and_execution_order_are_bounded(self):
        resources = self.contract["resource_caps"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["registered_real_executions"], 1)
        self.assertEqual(resources["vhdr_content_opens"], 1)
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_rss_bytes"], 256 * 1024**2)
        self.assertEqual(resources["maximum_generated_output_bytes"], 1024**2)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["download_bytes"], 0)
        sequence = self.contract["registered_access_order"]
        remote_green = sequence.index(
            "verify_authorization_and_implementation_commits_were_remote_green_before_execution"
        )
        open_vhdr = sequence.index("open_exactly_one_registered_vhdr_once_with_nofollow_semantics")
        emit = sequence.index("atomically_emit_bounded_ledger_and_summary")
        stop = sequence.index("stop_before_loop54_stage_b")
        self.assertLess(remote_green, open_vhdr)
        self.assertLess(open_vhdr, emit)
        self.assertLess(emit, stop)

    def test_gates_refusals_and_current_counters_are_complete(self):
        self.assertEqual(len(self.contract["acceptance_gates"]), 18)
        refusals = self.contract["refusal_ids"]
        self.assertEqual(len(refusals), 22)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L54A-F{index:02d}" for index in range(1, 23)],
        )
        counters = self.contract["current_access_counters"]
        self.assertEqual(counters["committed_dependency_artifacts_read"], 5)
        for key, value in counters.items():
            if key != "committed_dependency_artifacts_read":
                self.assertEqual(value, 0, key)

    def test_preregistration_discloses_scope_order_and_nonclaims(self):
        for phrase in (
            "exactly 11,705",
            "no-follow semantics",
            "No sibling path is resolved, statted, or opened",
            "268,435,456 bytes",
            "There is no second real execution",
            "exact Tier C authorization pending",
            "Engineering capability proposed:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase.lower(), self.prereg.lower())


if __name__ == "__main__":
    unittest.main()
