import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from neurodecodekit.datasets import marc1_generated_qualification as marc1


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_REGISTRY = (
    ROOT / "registries" / "marc1_generated_qualification_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one_thread_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    for key in marc1.THREAD_ENV_KEYS:
        env[key] = "1"
    return env


class Marc1GeneratedQualificationImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(IMPLEMENTATION_REGISTRY.read_text(encoding="utf-8"))

    def test_implementation_registry_identity(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc1_generated_qualification_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(
            self.registry["implementation_id"],
            "MARC-1-generated-qualification-implementation-v0",
        )
        self.assertEqual(
            self.registry["status"],
            "generated_implementation_complete_closeout_not_executed",
        )

    def test_implementation_artifact_bindings_are_current(self):
        for binding in self.registry["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_contract_proof_is_exact(self):
        proof = self.registry["green_contract_proof"]
        self.assertEqual(proof["commit"], marc1.GREEN_CONTRACT_COMMIT)
        self.assertEqual(proof["CI_run_id"], marc1.GREEN_CONTRACT_CI_RUN_ID)
        self.assertEqual(proof["base_job_id"], marc1.GREEN_CONTRACT_BASE_JOB_ID)
        self.assertEqual(
            proof["optional_neuro_job_id"], marc1.GREEN_CONTRACT_OPTIONAL_JOB_ID
        )
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["contract_sha256"], marc1.CONTRACT_SHA256)

    def test_contract_loader_refuses_drift_and_loads_exact_contract(self):
        contract = marc1.load_registered_contract()
        self.assertEqual(
            contract["contract_id"], "MARC-1-generated-qualification-contract-v0"
        )
        self.assertEqual(contract["interface"]["commands"], ["plan", "qualify", "inspect"])
        self.assertTrue(all(value == 0 for value in contract["access_counters"].values()))

    def test_generated_archive_is_small_and_deterministic(self):
        first = marc1.build_generated_archive()
        second = marc1.build_generated_archive()
        self.assertEqual(first.payload, second.payload)
        self.assertEqual(first.payload_intervals, second.payload_intervals)
        self.assertLessEqual(len(first.payload), marc1.MAX_ARCHIVE_BYTES)
        self.assertGreater(len(first.payload), zipfile.ZIP_MAX_COMMENT)

    def test_archive_inventory_uses_only_bounded_metadata_ranges(self):
        fixture = marc1.build_generated_archive()
        inventory = marc1.inventory_generated_archive(fixture)
        summary = inventory.aggregate_summary
        self.assertEqual(summary["member_count"], 14)
        self.assertEqual(summary["forced_ZIP64_member_count"], 1)
        self.assertEqual(summary["member_content_reads"], 0)
        self.assertEqual(summary["payload_interval_read_bytes"], 0)
        self.assertLessEqual(inventory.range_read_calls, marc1.MAX_RANGE_CALLS)
        self.assertLessEqual(inventory.range_bytes_returned, marc1.MAX_RANGE_BYTES)

    def test_private_inventory_has_exact_fields_and_public_summary_has_no_names(self):
        inventory = marc1.inventory_generated_archive(marc1.build_generated_archive())
        members = inventory.private_manifest["members"]
        self.assertEqual(len(members), 14)
        self.assertEqual(
            set(members[0]),
            {
                "member_name",
                "CRC32",
                "compression_method",
                "flag_bits",
                "compressed_size",
                "uncompressed_size",
                "local_header_offset",
            },
        )
        self.assertNotIn("member_name", json.dumps(inventory.aggregate_summary))
        zip64_row = next(
            row for row in members if row["member_name"] == marc1.FORCED_ZIP64_MEMBER
        )
        self.assertEqual(zip64_row["compression_method"], zipfile.ZIP_STORED)

    def test_range_adapter_refuses_before_exceeding_cap(self):
        fixture = marc1.build_generated_archive()
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F01"):
            marc1.inventory_generated_archive(
                fixture,
                budget=marc1._RangeBudget(max_calls=0, max_bytes=0),
            )

    def test_truncated_archive_refuses(self):
        fixture = marc1.build_generated_archive()
        eocd = fixture.payload.rfind(zipfile.stringEndArchive)
        truncated = marc1.GeneratedArchiveFixture(
            payload=fixture.payload[:eocd],
            payload_intervals=fixture.payload_intervals,
            forced_zip64_member=fixture.forced_zip64_member,
        )
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F01"):
            marc1.inventory_generated_archive(truncated)

    def test_generated_plan_is_deterministic_and_strict(self):
        first = marc1.build_generated_multimodal_plan()
        second = marc1.build_generated_multimodal_plan()
        self.assertEqual(first, second)
        first_summary = marc1.validate_generated_multimodal_plan(first)
        second_summary = marc1.validate_generated_multimodal_plan(second)
        self.assertEqual(first_summary, second_summary)
        self.assertEqual(first_summary["source_profile_count"], 2)
        self.assertEqual(first_summary["comparator_role_count"], 12)

    def test_source_type_role_and_model_inclusion_remain_distinct(self):
        plan = marc1.build_generated_multimodal_plan()
        for channel in plan["channels"]:
            self.assertNotEqual(channel["source_type"], channel["functional_role"])
            if channel["source_type"] != "EEG":
                self.assertEqual(channel["model_inclusion"], "nonpredictive")
        changed = copy.deepcopy(plan)
        changed["channels"][4]["model_inclusion"] = "candidate"
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F03"):
            marc1.validate_generated_multimodal_plan(changed)

    def test_geometry_and_clock_are_explicit(self):
        plan = marc1.build_generated_multimodal_plan()
        for channel in plan["channels"]:
            self.assertIn(channel["geometry_state"], {"available", "unavailable"})
            self.assertTrue(channel["clock_id"])
            self.assertEqual(channel["synchronization_state"], "same_amplifier")
        changed = copy.deepcopy(plan)
        changed["channels"][0]["clock_id"] = "different-clock"
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F03"):
            marc1.validate_generated_multimodal_plan(changed)

    def test_causal_window_and_guard_are_exact(self):
        plan = marc1.build_generated_multimodal_plan()
        preprocessing = plan["preprocessing"]
        self.assertEqual(preprocessing["window_seconds"], [-1.5, -0.2])
        self.assertEqual(preprocessing["future_context_samples"], 0)
        self.assertEqual(
            preprocessing["source_sample_offsets"]["wrist_like"]["stop_exclusive"],
            -102,
        )
        changed = copy.deepcopy(plan)
        changed["preprocessing"]["zero_phase_filter"] = True
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F04"):
            marc1.validate_generated_multimodal_plan(changed)

    def test_split_binding_and_target_firewall_are_physical(self):
        plan = marc1.build_generated_multimodal_plan()
        firewall = plan["target_firewall"]
        fit_ids = {marc1._identity_tuple(row) for row in firewall["fit_rows"]}
        prediction_ids = {
            marc1._identity_tuple(row)
            for row in firewall["target_blind_prediction_rows"]
        }
        scorer_ids = {
            marc1._identity_tuple(row) for row in firewall["isolated_scorer_rows"]
        }
        self.assertFalse(fit_ids & prediction_ids)
        self.assertEqual(prediction_ids, scorer_ids)
        self.assertTrue(
            all("target" not in row for row in firewall["target_blind_prediction_rows"])
        )

    def test_target_leakage_and_split_overlap_refuse(self):
        leaked = marc1.build_generated_multimodal_plan()
        leaked["target_firewall"]["target_blind_prediction_rows"][0]["target"] = "left"
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F05"):
            marc1.validate_generated_multimodal_plan(leaked)
        overlap = marc1.build_generated_multimodal_plan()
        prediction = overlap["target_firewall"]["target_blind_prediction_rows"][0]
        fit = overlap["target_firewall"]["fit_rows"][0]
        for field in marc1.IDENTITY_FIELDS:
            fit[field] = prediction[field]
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F05"):
            marc1.validate_generated_multimodal_plan(overlap)

    def test_recorded_modalities_require_their_comparators(self):
        plan = marc1.build_generated_multimodal_plan()
        self.assertEqual(
            plan["comparator_availability"]["freewill_like"][
                "EOG_only_where_available"
            ],
            "available",
        )
        self.assertEqual(
            plan["comparator_availability"]["wrist_like"][
                "pre_onset_EMG_only_where_available"
            ],
            "available",
        )
        changed = copy.deepcopy(plan)
        changed["comparator_availability"]["wrist_like"][
            "pre_onset_EMG_only_where_available"
        ] = "unavailable"
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F05"):
            marc1.validate_generated_multimodal_plan(changed)

    def test_all_twenty_four_mutations_refuse_in_frozen_classes(self):
        fixture = marc1.build_generated_archive()
        plan = marc1.build_generated_multimodal_plan()
        budget = marc1._RangeBudget()
        infos = marc1._read_infos_for_mutations(fixture, budget)
        outcomes = marc1.run_required_mutations(
            fixture,
            plan,
            infos,
            budget=budget,
        )
        self.assertEqual(tuple(outcomes), marc1.REQUIRED_MUTATIONS)
        self.assertEqual(len(outcomes), 24)
        self.assertTrue(all(route in marc1.REFUSAL_IDS for route in outcomes.values()))

    def test_output_cap_and_existing_destination_refuse(self):
        with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F06"):
            marc1._bounded_output_bytes(b"x" * (marc1.MAX_OUTPUT_BYTES + 1), b"")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing"
            output.mkdir()
            with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F06"):
                marc1._assert_output_destination(output)

    def test_symlink_output_parent_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real_parent = root / "real"
            real_parent.mkdir()
            linked_parent = root / "linked"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F06"):
                marc1._assert_output_destination(linked_parent / "out")

    def test_public_report_rejects_private_member_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            result = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    "-m",
                    "neurodecodekit.datasets.marc1_generated_qualification",
                    "qualify",
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                env=one_thread_env(),
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            report = json.loads(Path(payload["report"]).read_text(encoding="utf-8"))
            report["archive_summary"]["member_name"] = "private"
            with self.assertRaisesRegex(marc1.Marc1GeneratedRefusal, "MARC1G-F06"):
                marc1.validate_public_report(report)

    def test_isolated_cli_roundtrip_is_bounded_and_inspectable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            qualify = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    "-m",
                    "neurodecodekit.datasets.marc1_generated_qualification",
                    "qualify",
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                env=one_thread_env(),
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(qualify.stdout)
            self.assertEqual(result["route"], "MARC1G-R1")
            self.assertLessEqual(result["generated_output_bytes"], marc1.MAX_OUTPUT_BYTES)
            self.assertLessEqual(result["peak_RSS_bytes"], marc1.MAX_PEAK_RSS_BYTES)
            inspect = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    "-m",
                    "neurodecodekit.datasets.marc1_generated_qualification",
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
            self.assertEqual(inspected["member_count"], 14)
            self.assertEqual(inspected["mutation_refusals_passed"], 24)

    def test_inspect_refuses_private_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            result = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    "-m",
                    "neurodecodekit.datasets.marc1_generated_qualification",
                    "qualify",
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                env=one_thread_env(),
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            manifest = output / "marc1_generated_manifest.private.v0.json"
            refused = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    "-m",
                    "neurodecodekit.datasets.marc1_generated_qualification",
                    "inspect",
                    str(manifest),
                ],
                cwd=ROOT,
                env=one_thread_env(),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(json.loads(refused.stderr)["refusal_id"], "MARC1G-F06-output-privacy-overwrite-runtime-RSS-or-cap-failure")
            self.assertEqual(payload["route"], "MARC1G-R1")

    def test_cli_help_has_no_live_surface(self):
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-m",
                "neurodecodekit.datasets.marc1_generated_qualification",
                "--help",
            ],
            cwd=ROOT,
            env=one_thread_env(),
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("{plan,qualify,inspect}", result.stdout)
        for forbidden in ("--url", "--host", "--archive", "--participant", "--model"):
            self.assertNotIn(forbidden, result.stdout.lower())

    def test_plan_command_reports_zero_live_authority(self):
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-m",
                "neurodecodekit.datasets.marc1_generated_qualification",
                "plan",
            ],
            cwd=ROOT,
            env=one_thread_env(),
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["network_bytes"], 0)
        self.assertEqual(payload["real_payload_bytes"], 0)
        self.assertFalse(payload["scientific_claim"])
        self.assertEqual(payload["mutation_count"], 24)

    def test_implementation_registry_preserves_zero_authority(self):
        self.assertTrue(all(value is False for value in self.registry["authorization_flags"].values()))
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))
        self.assertFalse(self.registry["next_gate"]["public_access_eligible_now"])
        self.assertTrue(
            self.registry["next_gate"]["measured_generated_closeout_requires_this_implementation_green"]
        )


if __name__ == "__main__":
    unittest.main()
