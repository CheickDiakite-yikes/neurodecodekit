import ast
import copy
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.datasets import marc2_freewill_prefix_selection as prefix


ROOT = Path(__file__).resolve().parents[1]


def one_thread_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    env["PYTHONHASHSEED"] = "0"
    for key in prefix.THREAD_ENV_KEYS:
        env[key] = "1"
    return env


class Marc2FreewillPrefixSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = prefix.load_registered_contract(ROOT)
        cls.manifest = prefix.build_generated_manifest(contract=cls.contract)
        cls.selection = prefix.select_generated_prefix(
            cls.manifest,
            contract=cls.contract,
        )

    def qualify(self, output: Path):
        ticks = iter((10.0, 10.5))
        return prefix.qualify_generated_prefix_selection(
            output,
            clock=lambda: next(ticks),
            rss_probe=lambda: 32 * 1024 * 1024,
        )

    def test_contract_hash_and_green_proof_are_exact(self):
        contract_path = ROOT / prefix.CONTRACT_RELATIVE_PATH
        self.assertEqual(
            hashlib.sha256(contract_path.read_bytes()).hexdigest(),
            prefix.CONTRACT_SHA256,
        )
        self.assertEqual(
            prefix.GREEN_CONTRACT_COMMIT,
            "a12edebdab8b1252be546600d37fdb04503394d6",
        )
        self.assertEqual(prefix.GREEN_CONTRACT_CI_RUN_ID, 31_676_261_134)
        self.assertEqual(prefix.GREEN_CONTRACT_BASE_JOB_ID, 94_371_385_720)
        self.assertEqual(prefix.GREEN_CONTRACT_OPTIONAL_JOB_ID, 94_371_385_628)

    def test_generated_manifest_matches_full_inventory_scale(self):
        entries = self.manifest["entries"]
        self.assertEqual(len(entries), 1_227)
        self.assertTrue(all(set(row) == prefix.ENTRY_FIELDS for row in entries))
        self.assertEqual(
            Counter(row["entry_kind"] for row in entries),
            Counter({"regular_file": 1_025, "directory": 202}),
        )
        self.assertEqual(
            self.manifest["proof_posture"],
            "generated_fixture_private_metadata_only",
        )
        self.assertFalse(self.manifest["source_identity"]["whole_archive_downloaded"])
        self.assertFalse(self.manifest["source_identity"]["member_payload_opened"])

    def test_generated_fixture_has_all_source_and_candidate_bundles(self):
        core_rows = [
            row
            for row in self.manifest["entries"]
            if prefix.CORE_MEMBER_RE.fullmatch(row["member_name"])
        ]
        source_bundles = {
            (
                match.group("subject"),
                match.group("session"),
                match.group("run"),
            )
            for row in core_rows
            if (match := prefix.CORE_MEMBER_RE.fullmatch(row["member_name"]))
        }
        candidate_rows = prefix._prefix_rows(
            self.manifest["entries"],
            self.contract["participant_rank"]["full_rank"],
        )
        self.assertEqual(len(source_bundles), 195)
        self.assertEqual(len(core_rows), 780)
        self.assertEqual(len(candidate_rows), 456)

    def test_full_public_rank_replays_exactly(self):
        rank = self.contract["participant_rank"]
        eligible = self.contract["public_eligibility"]["eligible_subject_ids"]
        self.assertEqual(
            prefix._rank_subjects(rank["selection_seed"], eligible),
            rank["full_rank"],
        )

    def test_main_selection_expands_floor_to_sixteen(self):
        cohort = self.selection.cohort_summary
        self.assertEqual(cohort["selected_subjects"], 16)
        self.assertEqual(
            cohort["selected_subject_ids"],
            self.contract["participant_rank"]["full_rank"][:16],
        )
        self.assertEqual(cohort["first_nonfitting_subject_id"], "sub-18")
        self.assertEqual(cohort["candidate_subjects_examined"], 17)
        self.assertTrue(cohort["selection_is_maximal_contiguous_rank_prefix"])

    def test_main_selection_counts_and_sessions_are_exact(self):
        split = self.selection.split_summary
        self.assertEqual(split["fit_session"], "ses-01")
        self.assertEqual(split["heldout_session"], "ses-02")
        self.assertEqual(split["fit_run_bundles"], 48)
        self.assertEqual(split["heldout_run_bundles"], 48)
        self.assertEqual(split["selected_run_bundles"], 96)
        self.assertEqual(split["selected_core_members"], 384)
        self.assertEqual(split["fit_heldout_overlap"], 0)
        self.assertFalse(split["row_random_split_used"])

    def test_private_rows_have_exact_schema_and_first_three_runs(self):
        rows = self.selection.private_manifest["rows"]
        self.assertEqual(len(rows), 384)
        self.assertTrue(all(tuple(row) == prefix.PRIVATE_ROW_FIELDS for row in rows))
        self.assertEqual({row["run_id"] for row in rows}, {"run-01", "run-02", "run-03"})
        self.assertTrue(
            all(
                row["split_role"]
                == ("fit" if row["session_id"] == "ses-01" else "heldout")
                for row in rows
            )
        )

    def test_reservation_is_bounded_and_formula_replays(self):
        rows = self.selection.private_manifest["rows"]
        expected = sum(
            row["compressed_size"]
            + 30
            + len(row["member_name"].encode("utf-8"))
            + 65_535
            for row in rows
        )
        byte_summary = self.selection.byte_summary
        self.assertEqual(expected, byte_summary["selected_reservation_bytes"])
        self.assertEqual(expected, 8_105_207_776)
        self.assertLess(expected, byte_summary["reservation_cap_bytes"])
        self.assertGreater(
            expected + byte_summary["first_nonfitting_subject_reservation_bytes"],
            byte_summary["reservation_cap_bytes"],
        )

    def test_selection_stops_at_first_nonfit_without_skipping(self):
        rank = self.contract["participant_rank"]["full_rank"]
        selected = self.selection.cohort_summary["selected_subject_ids"]
        self.assertEqual(selected, rank[:16])
        self.assertNotIn(rank[17], selected)
        self.assertNotIn(rank[18], selected)

    def test_irrelevant_row_order_replays_byte_identically(self):
        replay = prefix.select_generated_prefix(
            prefix.build_generated_manifest(
                row_order="reversed",
                contract=self.contract,
            ),
            contract=self.contract,
        )
        self.assertEqual(
            prefix._canonical_json_bytes(self.selection.private_manifest),
            prefix._canonical_json_bytes(replay.private_manifest),
        )
        self.assertEqual(self.selection.selection_hashes, replay.selection_hashes)

    def test_crc_change_cannot_change_rank_split_or_reservation(self):
        changed = copy.deepcopy(self.manifest)
        row = next(
            item
            for item in changed["entries"]
            if "/sub-08/" in item["member_name"] and item["member_name"].endswith("_eeg.eeg")
        )
        row["CRC32"] = "1234abcd"
        observed = prefix.select_generated_prefix(changed, contract=self.contract)
        self.assertEqual(observed.cohort_summary, self.selection.cohort_summary)
        self.assertEqual(observed.split_summary, self.selection.split_summary)
        self.assertEqual(observed.byte_summary, self.selection.byte_summary)
        self.assertEqual(
            observed.selection_hashes["selection_identity_sha256"],
            self.selection.selection_hashes["selection_identity_sha256"],
        )
        self.assertNotEqual(
            observed.selection_hashes["private_selection_manifest_sha256"],
            self.selection.selection_hashes["private_selection_manifest_sha256"],
        )

    def test_unknown_target_or_quality_field_refuses(self):
        changed = copy.deepcopy(self.manifest)
        changed["entries"][0]["target"] = "generated-left"
        with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F01"):
            prefix.select_generated_prefix(changed, contract=self.contract)

    def test_non_object_row_refuses_instead_of_crashing(self):
        changed = copy.deepcopy(self.manifest)
        changed["entries"][0] = "not-an-object"
        with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F01"):
            prefix.select_generated_prefix(changed, contract=self.contract)

    def test_incomplete_bundle_refuses(self):
        changed = copy.deepcopy(self.manifest)
        prefix._replace_core_name(
            changed,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.eeg" in name,
            lambda name: name.replace("_eeg.eeg", "_notes.txt"),
        )
        with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F02"):
            prefix.select_generated_prefix(changed, contract=self.contract)

    def test_floor_profile_selects_exactly_twelve(self):
        observed = prefix.select_generated_prefix(
            prefix.build_generated_manifest(profile="floor", contract=self.contract),
            contract=self.contract,
        )
        self.assertEqual(observed.cohort_summary["selected_subjects"], 12)
        self.assertEqual(observed.split_summary["selected_core_members"], 288)

    def test_all19_profile_selects_every_eligible_subject(self):
        observed = prefix.select_generated_prefix(
            prefix.build_generated_manifest(profile="all19", contract=self.contract),
            contract=self.contract,
        )
        self.assertEqual(observed.cohort_summary["selected_subjects"], 19)
        self.assertIsNone(observed.cohort_summary["first_nonfitting_subject_id"])
        self.assertEqual(observed.split_summary["selected_core_members"], 456)

    def test_exact_cap_profile_is_accepted(self):
        observed = prefix.select_generated_prefix(
            prefix.build_generated_manifest(profile="exact_cap", contract=self.contract),
            contract=self.contract,
        )
        self.assertEqual(observed.cohort_summary["selected_subjects"], 12)
        self.assertEqual(
            observed.byte_summary["selected_reservation_bytes"],
            prefix.RESERVATION_CAP_BYTES,
        )

    def test_cap_plus_one_profile_refuses_below_floor(self):
        with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F04"):
            prefix.select_generated_prefix(
                prefix.build_generated_manifest(
                    profile="cap_plus_one",
                    contract=self.contract,
                ),
                contract=self.contract,
            )

    def test_all_four_boundary_profiles_pass(self):
        boundaries = prefix.exercise_boundary_profiles(contract=self.contract)
        self.assertEqual(set(boundaries), {"floor_12", "all_19", "exact_cap", "cap_plus_one"})
        self.assertTrue(all(item["passed"] for item in boundaries.values()))

    def test_all_40_mutations_refuse_in_frozen_classes(self):
        outcomes = prefix.run_required_mutations(self.manifest, contract=self.contract)
        self.assertEqual(tuple(outcomes), prefix.REQUIRED_MUTATIONS)
        self.assertEqual(len(outcomes), 40)
        self.assertTrue(all(route in prefix.REFUSAL_IDS for route in outcomes.values()))
        self.assertEqual(
            Counter(outcomes.values()),
            Counter(
                {
                    prefix.REFUSAL_IDS[0]: 3,
                    prefix.REFUSAL_IDS[1]: 5,
                    prefix.REFUSAL_IDS[2]: 12,
                    prefix.REFUSAL_IDS[3]: 12,
                    prefix.REFUSAL_IDS[4]: 4,
                    prefix.REFUSAL_IDS[5]: 4,
                }
            ),
        )

    def test_qualification_is_bounded_private_and_inspectable(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.qualify(Path(directory) / "qualification")
            self.assertEqual(outcome.report["route"], prefix.EXPECTED_ROUTE)
            self.assertLess(outcome.generated_input_bytes, 2 * 1024 * 1024)
            self.assertLess(outcome.generated_output_bytes, 2 * 1024 * 1024)
            self.assertEqual(
                stat.S_IMODE(outcome.private_manifest_path.stat().st_mode),
                0o600,
            )
            self.assertEqual(sum(outcome.report["access_counters"].values()), 0)
            self.assertTrue(all(outcome.report["acceptance_gates"].values()))
            inspected = prefix.inspect_generated_report(outcome.report_path)
            self.assertEqual(inspected["selected_subjects"], 16)
            self.assertEqual(inspected["boundary_profiles_passed"], 4)
            self.assertEqual(inspected["mutation_refusals_passed"], 40)

    def test_two_qualifications_replay_with_fixed_measurements(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.qualify(Path(directory) / "first")
            second = self.qualify(Path(directory) / "second")
            self.assertEqual(first.report_path.read_bytes(), second.report_path.read_bytes())
            self.assertEqual(
                first.private_manifest_path.read_bytes(),
                second.private_manifest_path.read_bytes(),
            )

    def test_public_report_contains_no_private_member_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.qualify(Path(directory) / "qualification")
            public_text = outcome.report_path.read_text(encoding="utf-8")
            self.assertNotIn('"member_name":', public_text)
            self.assertNotIn('"local_header_offset":', public_text)
            self.assertNotIn("_eeg.eeg", public_text)
            self.assertNotIn("_events.tsv", public_text)
            private = json.loads(outcome.private_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(len(private["rows"]), 384)

    def test_public_report_rejects_private_key_or_value(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.qualify(Path(directory) / "qualification")
            key_leak = copy.deepcopy(outcome.report)
            key_leak["cohort_summary"]["member_name"] = "private"
            with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F05"):
                prefix.validate_public_report(key_leak)
            value_leak = copy.deepcopy(outcome.report)
            value_leak["warnings"].append("https://generated.invalid/private")
            with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F05"):
                prefix.validate_public_report(value_leak)

    def test_inspect_refuses_private_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.qualify(Path(directory) / "qualification")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                return_code = prefix.main(["inspect", str(outcome.private_manifest_path)])
            self.assertEqual(return_code, 2)
            self.assertEqual(
                json.loads(stderr.getvalue())["refusal_id"],
                prefix.REFUSAL_IDS[5],
            )

    def test_existing_destination_and_symlink_parent_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F05"):
                self.qualify(existing)
            real_parent = root / "real"
            real_parent.mkdir()
            symlink_parent = root / "link"
            symlink_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F05"):
                self.qualify(symlink_parent / "qualification")

    def test_resource_caps_refuse_runtime_rss_and_thread_drift(self):
        with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F05"):
            prefix._assert_resources(prefix.MAX_RUNTIME_SECONDS + 1, 1)
        with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F05"):
            prefix._assert_resources(0, prefix.MAX_PEAK_RSS_BYTES + 1)
        with patch.dict(os.environ, {prefix.THREAD_ENV_KEYS[0]: "2"}):
            with self.assertRaisesRegex(prefix.FreewillPrefixSelectionRefusal, "MARC2FWG-F05"):
                prefix._assert_resources(0, 1)

    def test_plan_exposes_no_real_authority(self):
        plan = prefix.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-FW1")
        self.assertEqual(plan["generated_commands"], ["plan", "qualify", "inspect"])
        self.assertEqual(plan["expected_main_subjects"], 16)
        self.assertEqual(plan["reservation_cap_bytes"], 8 * 1024**3)
        self.assertEqual(plan["real_private_or_network_operations_authorized"], 0)
        self.assertEqual(plan["signal_target_model_or_score_operations_authorized"], 0)

    def test_module_has_no_network_neuro_model_or_execute_surface(self):
        source_path = ROOT / "src" / "neurodecodekit" / "datasets" / "marc2_freewill_prefix_selection.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertTrue(
            imported.isdisjoint(
                {"urllib", "requests", "httpx", "socket", "mne", "numpy", "torch", "sklearn"}
            )
        )
        self.assertNotIn('add_parser("execute"', source)
        self.assertNotIn(".codex_work", source)

    def test_module_cli_help_and_plan(self):
        help_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc2_freewill_prefix_selection",
                "--help",
            ],
            cwd=ROOT,
            env=one_thread_env(),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("{plan,qualify,inspect}", help_result.stdout)
        self.assertNotIn("execute", help_result.stdout)
        plan_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc2_freewill_prefix_selection",
                "plan",
            ],
            cwd=ROOT,
            env=one_thread_env(),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
        self.assertEqual(json.loads(plan_result.stdout)["expected_main_subjects"], 16)


if __name__ == "__main__":
    unittest.main()
