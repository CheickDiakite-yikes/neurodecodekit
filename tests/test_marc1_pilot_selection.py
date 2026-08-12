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

from neurodecodekit.datasets import marc1_pilot_selection as pilot


ROOT = Path(__file__).resolve().parents[1]


def one_thread_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    env["PYTHONHASHSEED"] = "0"
    for key in pilot.THREAD_ENV_KEYS:
        env[key] = "1"
    return env


class MARC1PilotSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = pilot.load_registered_contract(ROOT)
        cls.freewill = pilot.build_generated_freewill_manifest(contract=cls.contract)
        cls.wrist = pilot.build_generated_wrist_metadata()

    def select(self):
        return pilot.select_generated_pilot(
            self.freewill,
            self.wrist,
            contract=self.contract,
        )

    def qualify(self, output: Path):
        ticks = iter((10.0, 10.5))
        return pilot.qualify_generated_pilot_selection(
            output,
            clock=lambda: next(ticks),
            rss_probe=lambda: 32 * 1024 * 1024,
        )

    def test_contract_hash_and_remote_green_proof_are_exact(self):
        path = ROOT / pilot.CONTRACT_RELATIVE_PATH
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pilot.CONTRACT_SHA256)
        self.assertEqual(
            pilot.GREEN_CONTRACT_COMMIT,
            "d1218066e64dea502d263acf0c096ed7eab55a11",
        )
        self.assertEqual(pilot.GREEN_CONTRACT_CI_RUN_ID, 31_569_417_204)
        self.assertEqual(pilot.GREEN_CONTRACT_BASE_JOB_ID, 94_028_013_357)
        self.assertEqual(pilot.GREEN_CONTRACT_OPTIONAL_JOB_ID, 94_028_013_230)

    def test_generated_freewill_fixture_matches_full_inventory_scale(self):
        entries = self.freewill["entries"]
        kinds = {kind: 0 for kind in ("regular_file", "directory")}
        for row in entries:
            kinds[row["entry_kind"]] += 1
            self.assertEqual(set(row), pilot.FREEWILL_ENTRY_FIELDS)
        self.assertEqual(len(entries), 1_227)
        self.assertEqual(kinds, {"regular_file": 1_025, "directory": 202})
        self.assertEqual(self.freewill["proof_posture"], "generated_fixture_private_metadata_only")
        self.assertFalse(self.freewill["source_identity"]["whole_archive_downloaded"])
        self.assertFalse(self.freewill["source_identity"]["member_payload_opened"])

    def test_generated_wrist_fixture_has_45_archives_and_10_support_rows(self):
        self.assertEqual(len(self.wrist), 55)
        self.assertTrue(all(set(row) == pilot.WRIST_ROW_FIELDS for row in self.wrist))
        self.assertEqual(
            sum(row["role"] == "participant_archive" for row in self.wrist),
            45,
        )
        self.assertEqual(sum(row["role"] == "supplementary" for row in self.wrist), 10)

    def test_both_DOI_bound_rankings_replay_exactly(self):
        for axis_name in ("freewill_axis", "wrist_axis"):
            axis = self.contract[axis_name]
            eligible = (
                axis["eligibility"]["eligible_subject_ids"]
                if axis_name == "freewill_axis"
                else axis["eligible_subject_ids"]
            )
            ranked = pilot._rank_subjects(axis["selection_seed"], eligible)
            self.assertEqual(ranked[:12], axis["selected_subject_ids_in_rank_order"])

    def test_selection_counts_splits_and_private_row_schema_are_exact(self):
        selected = self.select()
        rows = selected.private_manifest["rows"]
        self.assertEqual(len(rows), 300)
        self.assertTrue(all(tuple(row) == pilot.PRIVATE_ROW_FIELDS for row in rows))
        self.assertEqual(selected.split_summary["freewill_selected_run_bundles"], 72)
        self.assertEqual(selected.split_summary["freewill_selected_core_members"], 288)
        self.assertEqual(selected.split_summary["wrist_fit_runs"], 72)
        self.assertEqual(selected.split_summary["wrist_heldout_runs"], 24)
        self.assertEqual(selected.split_summary["fit_heldout_overlap"], 0)

    def test_freewill_cross_day_split_uses_three_runs_each(self):
        selected = self.select()
        rows = [
            row
            for row in selected.private_manifest["rows"]
            if row["source_id"] == "freewill_23_generated"
        ]
        self.assertEqual(len(rows), 288)
        fit = {row["run_id"] for row in rows if row["session_id"] == "ses-01"}
        heldout = {row["run_id"] for row in rows if row["session_id"] == "ses-02"}
        self.assertEqual(fit, {"run-01", "run-02", "run-03"})
        self.assertEqual(heldout, fit)
        self.assertTrue(
            all(
                row["split_role"] == ("fit" if row["session_id"] == "ses-01" else "heldout")
                for row in rows
            )
        )

    def test_selection_stays_inside_each_source_and_joint_cap(self):
        byte_summary = self.select().byte_summary
        self.assertLess(
            byte_summary["freewill_reserved_payload_bytes"],
            byte_summary["freewill_payload_cap_bytes"],
        )
        self.assertLess(
            byte_summary["wrist_reserved_payload_bytes"],
            byte_summary["wrist_payload_cap_bytes"],
        )
        self.assertLess(
            byte_summary["joint_reserved_payload_bytes"],
            byte_summary["joint_payload_cap_bytes"],
        )
        self.assertFalse(byte_summary["fallback_used"])

    def test_irrelevant_row_order_replays_byte_identically(self):
        first = self.select()
        replay = pilot.select_generated_pilot(
            pilot.build_generated_freewill_manifest(
                row_order="reversed", contract=self.contract
            ),
            pilot.build_generated_wrist_metadata(row_order="reversed"),
            contract=self.contract,
        )
        self.assertEqual(
            pilot._canonical_json_bytes(first.private_manifest),
            pilot._canonical_json_bytes(replay.private_manifest),
        )
        self.assertEqual(first.selection_hashes, replay.selection_hashes)

    def test_size_and_CRC_changes_do_not_change_cohort_or_split(self):
        baseline = self.select()
        changed_freewill = copy.deepcopy(self.freewill)
        row = next(
            item
            for item in changed_freewill["entries"]
            if "/sub-08/" in item["member_name"] and item["member_name"].endswith("_eeg.eeg")
        )
        row["compressed_size"] += 1
        row["uncompressed_size"] += 1
        row["CRC32"] = "1234abcd"
        changed_wrist = copy.deepcopy(self.wrist)
        selected_ids = set(self.contract["wrist_axis"]["selected_subject_ids_in_rank_order"])
        archive = next(item for item in changed_wrist if item["subject_id"] in selected_ids)
        archive["size"] += 1
        changed = pilot.select_generated_pilot(
            changed_freewill,
            changed_wrist,
            contract=self.contract,
        )
        self.assertEqual(baseline.cohort_summary, changed.cohort_summary)
        self.assertEqual(baseline.split_summary, changed.split_summary)
        self.assertEqual(
            baseline.selection_hashes["joint_selection_identity_sha256"],
            changed.selection_hashes["joint_selection_identity_sha256"],
        )
        self.assertNotEqual(
            baseline.selection_hashes["private_selection_manifest_sha256"],
            changed.selection_hashes["private_selection_manifest_sha256"],
        )

    def test_target_or_quality_field_refuses_as_unknown_inventory_content(self):
        leaked = copy.deepcopy(self.freewill)
        leaked["entries"][0]["target"] = "generated-left"
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F01"):
            pilot.select_generated_pilot(leaked, self.wrist, contract=self.contract)

    def test_nested_source_provenance_is_strict(self):
        changed = copy.deepcopy(self.freewill)
        changed["source_identity"]["unexpected"] = True
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F01"):
            pilot.select_generated_pilot(changed, self.wrist, contract=self.contract)

    def test_non_object_inventory_row_refuses_instead_of_crashing(self):
        changed = copy.deepcopy(self.freewill)
        changed["entries"][0] = "not-an-object"
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F01"):
            pilot.select_generated_pilot(changed, self.wrist, contract=self.contract)
        changed = copy.deepcopy(self.freewill)
        changed["transport_body_sha256"]["tail"] = "not-a-digest"
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F01"):
            pilot.select_generated_pilot(changed, self.wrist, contract=self.contract)

    def test_incomplete_bundle_refuses(self):
        changed = copy.deepcopy(self.freewill)
        pilot._replace_core_name(
            changed,
            lambda name: "/sub-08/ses-01/" in name and "_run-01_eeg.eeg" in name,
            lambda name: name.replace("_eeg.eeg", "_notes.txt"),
        )
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F02"):
            pilot.select_generated_pilot(changed, self.wrist, contract=self.contract)

    def test_source_caps_refuse_without_fallback(self):
        changed = copy.deepcopy(self.wrist)
        selected_ids = set(self.contract["wrist_axis"]["selected_subject_ids_in_rank_order"])
        for row in changed:
            if row["subject_id"] in selected_ids:
                row["size"] = 256 * 1024**2
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F04"):
            pilot.select_generated_pilot(self.freewill, changed, contract=self.contract)

    def test_all_36_mutations_refuse_in_frozen_classes(self):
        outcomes = pilot.run_required_mutations(
            self.freewill,
            self.wrist,
            contract=self.contract,
        )
        self.assertEqual(tuple(outcomes), pilot.REQUIRED_MUTATIONS)
        self.assertEqual(len(outcomes), 36)
        self.assertTrue(all(route in pilot.REFUSAL_IDS for route in outcomes.values()))
        self.assertEqual(
            Counter(outcomes.values()),
            Counter(
                {
                    pilot.REFUSAL_IDS[0]: 1,
                    pilot.REFUSAL_IDS[1]: 5,
                    pilot.REFUSAL_IDS[2]: 9,
                    pilot.REFUSAL_IDS[3]: 13,
                    pilot.REFUSAL_IDS[4]: 2,
                    pilot.REFUSAL_IDS[5]: 2,
                    pilot.REFUSAL_IDS[6]: 4,
                }
            ),
        )

    def test_generated_qualification_is_bounded_private_and_inspectable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            outcome = self.qualify(output)
            self.assertEqual(outcome.report["route"], pilot.EXPECTED_ROUTE)
            self.assertLess(outcome.generated_input_bytes, 2 * 1024 * 1024)
            self.assertLess(outcome.generated_output_bytes, 2 * 1024 * 1024)
            self.assertEqual(
                stat.S_IMODE(outcome.private_manifest_path.stat().st_mode),
                0o600,
            )
            self.assertEqual(sum(outcome.report["access_counters"].values()), 0)
            self.assertTrue(all(outcome.report["acceptance_gates"].values()))
            inspected = pilot.inspect_generated_report(outcome.report_path)
            self.assertEqual(inspected["route"], pilot.EXPECTED_ROUTE)
            self.assertEqual(inspected["mutation_refusals_passed"], 36)

    def test_two_qualifications_replay_exact_output_with_fixed_measurements(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.qualify(Path(directory) / "first")
            second = self.qualify(Path(directory) / "second")
            self.assertEqual(first.report_path.read_bytes(), second.report_path.read_bytes())
            self.assertEqual(
                first.private_manifest_path.read_bytes(),
                second.private_manifest_path.read_bytes(),
            )

    def test_public_report_contains_no_private_selection_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.qualify(Path(directory) / "qualification")
            public_text = outcome.report_path.read_text(encoding="utf-8")
            self.assertNotIn("member_or_archive_name", public_text)
            self.assertNotIn("local_header_offset", public_text)
            self.assertNotIn("download_url", public_text)
            self.assertNotIn("_eeg.eeg", public_text)
            self.assertNotIn(".zip", public_text)
            private = json.loads(outcome.private_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(len(private["rows"]), 300)

    def test_public_report_refuses_private_Freewill_or_Wrist_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.qualify(Path(directory) / "qualification")
            freewill_leak = copy.deepcopy(outcome.report)
            freewill_leak["cohort_summary"]["member_name"] = "private"
            with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F06"):
                pilot.validate_public_report(freewill_leak)
            wrist_leak = copy.deepcopy(outcome.report)
            wrist_leak["warnings"].append("https://generated.invalid/private.zip")
            with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F06"):
                pilot.validate_public_report(wrist_leak)
            alias_leak = copy.deepcopy(outcome.report)
            alias_leak["cohort_summary"]["selected_archive_names"] = ["private"]
            with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F06"):
                pilot.validate_public_report(alias_leak)

    def test_inspect_refuses_private_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            outcome = self.qualify(Path(directory) / "qualification")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                return_code = pilot.main(["inspect", str(outcome.private_manifest_path)])
            self.assertEqual(return_code, 2)
            self.assertEqual(json.loads(stderr.getvalue())["refusal_id"], pilot.REFUSAL_IDS[6])

    def test_existing_destination_and_symlink_parent_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F06"):
                pilot._assert_output_destination(existing)
            real_parent = root / "real"
            real_parent.mkdir()
            linked_parent = root / "linked"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F06"):
                pilot._assert_output_destination(linked_parent / "out")

    def test_output_and_resource_caps_refuse(self):
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F06"):
            pilot._bounded_output_bytes(b"x" * (pilot.MAX_PUBLIC_OUTPUT_BYTES + 1), b"")
        with self.assertRaisesRegex(pilot.PilotSelectionRefusal, "MARC1PSG-F06"):
            pilot._assert_resources(0.0, pilot.MAX_PEAK_RSS_BYTES + 1)

    def test_plan_reports_zero_real_and_model_authority(self):
        plan = pilot.build_plan_summary()
        self.assertEqual(plan["generated_commands"], ["plan", "qualify", "inspect"])
        self.assertEqual(plan["required_mutations"], 36)
        self.assertEqual(plan["real_or_network_operations_authorized"], 0)
        self.assertEqual(plan["signal_target_model_or_score_operations_authorized"], 0)

    def test_module_has_standard_library_imports_and_no_network_constructor(self):
        source_path = ROOT / "src/neurodecodekit/datasets/marc1_pilot_selection.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            node.names[0].name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertFalse(imported & {"mne", "numpy", "requests", "scipy", "sklearn", "torch"})
        self.assertNotIn("urllib", imported)
        self.assertNotIn("urlopen", source)
        self.assertNotIn(".codex_work", source)

    def test_cli_help_has_no_real_selection_or_override_surface(self):
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-m",
                "neurodecodekit.datasets.marc1_pilot_selection",
                "--help",
            ],
            cwd=ROOT,
            env=one_thread_env(),
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = result.stdout.lower()
        for forbidden in ("execute", "--url", "--host", "--participant", "--seed", "--size"):
            self.assertNotIn(forbidden, help_text)
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertIn("inspect", help_text)

    def test_isolated_python_S_CLI_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            qualify = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    "-m",
                    "neurodecodekit.datasets.marc1_pilot_selection",
                    "qualify",
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                env=one_thread_env(),
                check=False,
                capture_output=True,
                text=True,
            )
            if qualify.returncode != 0:
                refusal = json.loads(qualify.stderr)
                inherited_high_water = pilot._peak_rss_bytes() > pilot.MAX_PEAK_RSS_BYTES
                if refusal.get("refusal_id") == pilot.REFUSAL_IDS[6] and inherited_high_water:
                    self.skipTest("forked child inherited an over-cap parent RSS high-water mark")
                self.fail(f"qualification CLI refused unexpectedly: {refusal}")
            result = json.loads(qualify.stdout)
            self.assertEqual(result["route"], pilot.EXPECTED_ROUTE)
            inspect = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    "-m",
                    "neurodecodekit.datasets.marc1_pilot_selection",
                    "inspect",
                    result["report"],
                ],
                cwd=ROOT,
                env=one_thread_env(),
                check=True,
                capture_output=True,
                text=True,
            )
            inspected = json.loads(inspect.stdout)
            self.assertEqual(inspected["freewill_selected_run_bundles"], 72)
            self.assertEqual(inspected["wrist_selected_archives"], 12)


if __name__ == "__main__":
    unittest.main()
