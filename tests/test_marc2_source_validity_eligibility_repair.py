import contextlib
import copy
import io
import json
import os
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector
from neurodecodekit.datasets import (
    marc2_source_validity_eligibility_repair as repair,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENVIRONMENT = {name: "1" for name in repair.THREAD_ENVIRONMENT}


class Marc2SourceValidityEligibilityRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = repair.load_registered_contract(ROOT)
        cls.selector_contract = selector.load_registered_contract(ROOT)
        cls.source = repair.build_generated_full_source(
            contract=cls.contract,
            selector_contract=cls.selector_contract,
        )

    def test_contract_hash_and_remote_green_registration_are_exact(self):
        self.assertEqual(
            repair.CONTRACT_SHA256,
            "84f44f8bc43a4ee56e256a1546cbc1fae3252f2f320db7064602fe72b44463e9",
        )
        proof = self.contract["green_localization_proof"]
        self.assertTrue(proof["both_required_jobs_green_before_registration"])
        self.assertEqual(
            self.contract["next_gate"][
                "generated_implementation_allowed_after_registration_remote_green"
            ],
            True,
        )

    def test_full_source_has_exact_rows_kinds_and_generated_posture(self):
        self.assertEqual(set(self.source), repair.SOURCE_TOP_LEVEL_FIELDS)
        self.assertEqual(
            self.source["proof_posture"], repair.GENERATED_PROOF_POSTURE
        )
        self.assertEqual(len(self.source["entries"]), 1_227)
        self.assertEqual(
            Counter(row["entry_kind"] for row in self.source["entries"]),
            Counter({"regular_file": 1_025, "directory": 202}),
        )

    def test_full_source_has_238_complete_bundles_and_73_auxiliary_files(self):
        grouped, kinds = repair._group_source_rows(self.source["entries"])
        self.assertEqual(kinds["regular_file"], 1_025)
        self.assertEqual(len(grouped), 238)
        self.assertTrue(
            all(
                set(companions) == set(selector.REQUIRED_SUFFIXES)
                for companions in grouped.values()
            )
        )
        auxiliary = [
            row
            for row in self.source["entries"]
            if row["entry_kind"] == "regular_file"
            and selector._core_match(row["member_name"]) is None
        ]
        self.assertEqual(len(auxiliary), 73)

    def test_43_adversary_keys_and_172_companions_are_exact(self):
        by_predicate = repair._adversary_keys_by_predicate(self.contract)
        self.assertEqual(
            {code: len(keys) for code, keys in by_predicate.items()},
            {
                "MARC2VR-P02": 12,
                "MARC2VR-P03": 24,
                "MARC2VR-P04": 7,
            },
        )
        self.assertEqual(sum(len(keys) for keys in by_predicate.values()), 43)
        self.assertEqual(
            sum(
                len(repair._rows_for_key(self.source, key))
                for keys in by_predicate.values()
                for key in keys
            ),
            172,
        )

    def test_validation_filters_only_after_classifying_all_source_bundles(self):
        filtered, counts, labels, source_hash = repair.validate_generated_source(
            self.source,
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(counts, self.contract["expected_predicate_counts"])
        self.assertEqual(len(labels), 238)
        self.assertEqual(len(filtered), 195)
        self.assertEqual(len(source_hash), 64)
        self.assertEqual(set(labels.values()), set(repair.PREDICATE_CODES))
        self.assertTrue(
            all(labels[key] == "MARC2VR-P01" for key in filtered)
        )

    def test_filtered_selector_replays_frozen_identity_and_excludes_adversaries(self):
        filtered, _counts, _labels, source_hash = repair.validate_generated_source(
            self.source,
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        selection = repair._select_from_filtered(
            filtered, source_hash, self.selector_contract
        )
        repair._assert_selection(selection, self.contract, set(filtered))
        self.assertEqual(selection.cohort_summary["selected_subjects"], 16)
        self.assertEqual(selection.split_summary["selected_run_bundles"], 96)
        self.assertEqual(selection.split_summary["selected_core_members"], 384)
        self.assertEqual(
            selection.byte_summary["selected_reservation_bytes"],
            8_105_207_776,
        )

    def test_reversed_source_order_replays_exactly(self):
        reversed_source = repair.build_generated_full_source(
            row_order="reversed",
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        first = repair.validate_generated_source(
            self.source,
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        second = repair.validate_generated_source(
            reversed_source,
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(first[1:], second[1:])
        first_selection = repair._select_from_filtered(
            first[0], first[3], self.selector_contract
        )
        second_selection = repair._select_from_filtered(
            second[0], second[3], self.selector_contract
        )
        self.assertEqual(
            first_selection.selection_hashes["selection_identity_sha256"],
            second_selection.selection_hashes["selection_identity_sha256"],
        )
        self.assertEqual(first_selection.byte_summary, second_selection.byte_summary)

    def test_every_registered_mutation_refuses_and_all_routes_are_exercised(self):
        routes = repair.run_required_mutations(
            self.source,
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(
            list(routes), self.contract["qualification"]["required_mutations"]
        )
        self.assertEqual(len(routes), 36)
        self.assertEqual(set(routes.values()), set(repair.REFUSAL_ROUTES))

    def test_source_envelope_and_path_mutations_fail_closed(self):
        for mutation, expected in (
            ("top_level_field_added", "MARC2VR-F02"),
            ("absolute_member_path", "MARC2VR-F03"),
            ("duplicate_member_name", "MARC2VR-F04"),
            ("eligible_session_count_drift", "MARC2VR-F05"),
        ):
            with self.subTest(mutation=mutation):
                changed = repair._mutated_source(self.source, mutation)
                with self.assertRaises(
                    repair.SourceValidityEligibilityRefusal
                ) as caught:
                    repair.validate_generated_source(
                        changed,
                        contract=self.contract,
                        selector_contract=self.selector_contract,
                    )
                self.assertEqual(caught.exception.route, expected)

    def test_source_builder_is_deterministic_and_does_not_mutate_base_fixture(self):
        replay = repair.build_generated_full_source(
            contract=self.contract,
            selector_contract=self.selector_contract,
        )
        self.assertEqual(
            repair._canonical_source_bytes(self.source),
            repair._canonical_source_bytes(replay),
        )
        base = selector.build_generated_manifest(
            contract=self.selector_contract,
            profile="main",
        )
        grouped, _kinds = repair._group_source_rows(base["entries"])
        self.assertEqual(len(grouped), 195)
        self.assertEqual(base["proof_posture"], "generated_fixture_private_metadata_only")

    def test_generated_qualification_is_deterministic_and_public(self):
        def run_once() -> dict:
            times = iter((100.0, 100.25))
            with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
                return repair.qualify_generated(
                    repo_root=ROOT,
                    clock=lambda: next(times),
                    rss_reader=lambda: 50_000_000,
                )

        first = run_once()
        second = run_once()
        self.assertEqual(first, second)
        self.assertEqual(first["route"], "MARC2VR-G1")
        self.assertEqual(
            first["source_domain_summary"]["complete_source_run_bundles"],
            238,
        )
        self.assertEqual(first["mutation_summary"]["refused_mutations"], 36)
        self.assertTrue(
            first["mutation_summary"]["all_registered_refusal_routes_exercised"]
        )
        repair.validate_public_report(first)

    def test_report_measurements_and_zero_counters_are_bounded(self):
        times = iter((5.0, 5.5))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            report = repair.qualify_generated(
                repo_root=ROOT,
                clock=lambda: next(times),
                rss_reader=lambda: 60_000_000,
            )
        measurements = report["measurements"]
        self.assertEqual(measurements["runtime_seconds"], 0.5)
        self.assertEqual(measurements["peak_RSS_bytes"], 60_000_000)
        self.assertEqual(measurements["retained_generated_output_bytes"], 0)
        self.assertLessEqual(
            measurements["aggregate_output_bytes"],
            report["resource_caps"]["generated_output_bytes"],
        )
        self.assertTrue(all(value == 0 for value in report["access_counters"].values()))

    def test_thread_resource_and_public_output_drift_refuse(self):
        environment = dict(THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(
                repair.SourceValidityEligibilityRefusal
            ) as caught:
                repair.qualify_generated(repo_root=ROOT)
        self.assertEqual(caught.exception.route, "MARC2VR-F08")
        with self.assertRaises(repair.SourceValidityEligibilityRefusal):
            repair._assert_resources(31.0, 1, self.contract)
        with self.assertRaises(repair.SourceValidityEligibilityRefusal):
            repair._walk_public({"member_name": "forbidden"})

    def test_report_tampering_refuses(self):
        times = iter((1.0, 1.1))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            report = repair.qualify_generated(
                repo_root=ROOT,
                clock=lambda: next(times),
                rss_reader=lambda: 40_000_000,
            )
        changed = copy.deepcopy(report)
        changed["access_counters"]["model_runs"] = 1
        with self.assertRaises(repair.SourceValidityEligibilityRefusal):
            repair.validate_public_report(changed)

    def test_plan_inspect_and_help_have_no_execute_surface(self):
        parser = repair._build_parser()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as caught:
                parser.parse_args(["--help"])
        self.assertEqual(caught.exception.code, 0)
        help_text = output.getvalue()
        self.assertIn("qualify", help_text)
        self.assertNotIn("execute", help_text)
        self.assertFalse(repair.build_plan_summary()["private_read_or_real_executor_allowed"])
        self.assertFalse(
            repair.build_inspection_summary()["private_row_or_path_inspection_available"]
        )

    def test_main_plan_and_inspect_emit_strict_JSON(self):
        for command in ("plan", "inspect"):
            with self.subTest(command=command):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(repair.main([command]), 0)
                payload = json.loads(output.getvalue())
                self.assertEqual(payload["lane_id"], "MARC2-VR1")

    def test_module_has_no_private_live_network_or_heavy_dependency_surface(self):
        source = Path(repair.__file__).read_text(encoding="utf-8")
        self.assertNotIn("live_alias_recovery_v2", source)
        self.assertNotIn("member_inventory.private.v0.json", source)
        self.assertNotIn("marc2_live_schema_adapter_recovery", source)
        self.assertNotIn('add_parser("execute"', source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)
        self.assertNotIn("import numpy", source)
        self.assertNotIn("import mne", source)
        self.assertNotIn("import torch", source)


if __name__ == "__main__":
    unittest.main()
