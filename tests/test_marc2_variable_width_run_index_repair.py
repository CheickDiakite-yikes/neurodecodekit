import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_variable_width_run_index_repair as vr16a


ROOT = Path(__file__).resolve().parents[1]


class Marc2VariableWidthRunIndexRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = vr16a.load_registered_contract()
        cls.sources = {
            variant: vr16a.build_generated_variant(variant, "canonical")
            for variant in vr16a.VARIANTS
        }
        cls.outcomes = {
            variant: vr16a.adapt_variable_width_source(
                source, contract=cls.contract
            )
            for variant, source in cls.sources.items()
        }
        before = dict(os.environ)
        os.environ.update(vr16a.THREAD_ENVIRONMENT)
        try:
            times = iter((100.0, 101.5))
            cls.report = vr16a.qualify_generated(
                contract=cls.contract,
                clock=lambda: next(times),
                peak_rss=lambda: 64 * 1024**2,
            )
        finally:
            os.environ.clear()
            os.environ.update(before)

    def test_registration_proof_and_contract_are_exact(self):
        self.assertEqual(
            vr16a.CONTRACT_SHA256,
            "308b80864553fd12a7bda7e4691aea35c63eebfbd651c7ed86ebc15e2fd41dec",
        )
        self.assertEqual(
            vr16a.GREEN_REGISTRATION_COMMIT,
            "7dba59355ca45c8ab5eafb9d8b7757edfc9755c5",
        )
        self.assertEqual(vr16a.GREEN_REGISTRATION_CI_RUN_ID, 32_458_280_634)
        self.assertEqual(vr16a.GREEN_REGISTRATION_BASE_JOB_ID, 96_699_811_237)
        self.assertEqual(vr16a.GREEN_REGISTRATION_OPTIONAL_JOB_ID, 96_699_811_051)

    def test_module_is_additive_dependency_light_and_has_no_execute_surface(self):
        source = Path(vr16a.__file__).read_text(encoding="utf-8")
        self.assertNotIn("suffix_identity_private_discriminator", source)
        self.assertNotIn("def execute", source)
        self.assertNotIn("numpy", source)
        self.assertNotIn("mne", source)
        self.assertEqual(set(vr16a._parser()._option_string_actions), {"-h", "--help"})

    def test_parser_accepts_all_frozen_widths_with_one_semantic_identity(self):
        tokens = set()
        for source in self.sources.values():
            name = vr16a._first_core(source)["member_name"]
            match = vr16a._variable_core_match(name)
            self.assertIsNotNone(match)
            tokens.add(match.group("run"))
            self.assertIn(vr16a._semantic_run(match.group("run")), {1, 2, 3})
        self.assertGreaterEqual(len(tokens), 5)
        self.assertEqual(vr16a._semantic_run("0" * 63 + "1"), 1)
        self.assertEqual(vr16a._semantic_run("0004"), 4)

    def test_all_width_variants_preserve_semantic_selection(self):
        self.assertEqual(
            {outcome.semantic_sha256 for outcome in self.outcomes.values()},
            {"254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba"},
        )
        self.assertEqual(
            {
                outcome.selection.cohort_summary["selected_subjects"]
                for outcome in self.outcomes.values()
            },
            {16},
        )
        self.assertEqual(
            {
                outcome.selection.split_summary["selected_run_bundles"]
                for outcome in self.outcomes.values()
            },
            {96},
        )
        self.assertEqual(
            {
                outcome.selection.split_summary["selected_core_members"]
                for outcome in self.outcomes.values()
            },
            {384},
        )

    def test_source_and_selected_name_hashes_distinguish_every_variant(self):
        self.assertEqual(
            len({outcome.source_sha256 for outcome in self.outcomes.values()}), 6
        )
        self.assertEqual(
            len(
                {
                    outcome.source_exact_selected_names_sha256
                    for outcome in self.outcomes.values()
                }
            ),
            6,
        )

    def test_selected_names_and_reservations_are_source_exact(self):
        for variant, outcome in self.outcomes.items():
            with self.subTest(variant=variant):
                source_names = {
                    row["member_name"] for row in self.sources[variant]["entries"]
                }
                for row in outcome.selection.private_manifest["rows"]:
                    self.assertIn(row["member_name"], source_names)
                    self.assertEqual(
                        row["reservation_bytes"],
                        vr16a.selector._reservation_bytes(row),
                    )

    def test_source_objects_are_immutable(self):
        source = vr16a.build_generated_variant("sixty_four_digit", "reversed")
        before = vr16a.vr2._canonical_source_bytes(source)
        vr16a.adapt_variable_width_source(source, contract=self.contract)
        self.assertEqual(vr16a.vr2._canonical_source_bytes(source), before)

    def test_registered_witnesses_refuse_on_exact_routes(self):
        routes = {
            "empty_run_token": vr16a.REFUSAL_ROUTES[2],
            "signed_run_token": vr16a.REFUSAL_ROUTES[2],
            "decimal_run_token": vr16a.REFUSAL_ROUTES[2],
            "unicode_digit_run_token": vr16a.REFUSAL_ROUTES[2],
            "alphabetic_run_token": vr16a.REFUSAL_ROUTES[2],
            "semantic_zero": vr16a.REFUSAL_ROUTES[6],
            "semantic_run_four": vr16a.REFUSAL_ROUTES[4],
            "mixed_lexical_tokens_within_bundle": vr16a.REFUSAL_ROUTES[4],
            "duplicate_normalized_run_companion": vr16a.REFUSAL_ROUTES[4],
            "wrong_task_token": vr16a.REFUSAL_ROUTES[3],
            "incomplete_companion_set": vr16a.REFUSAL_ROUTES[4],
            "overlong_member_name": vr16a.REFUSAL_ROUTES[2],
            "mutated_row_schema": vr16a.REFUSAL_ROUTES[2],
        }
        base = self.sources["two_digit_control"]
        for witness, expected in routes.items():
            with self.subTest(witness=witness):
                with self.assertRaises(
                    vr16a.VariableWidthRunIndexRepairRefusal
                ) as raised:
                    vr16a.adapt_variable_width_source(
                        vr16a._mutated_witness(base, witness),
                        contract=self.contract,
                    )
                self.assertEqual(raised.exception.route, expected)

    def test_contract_substitution_refuses_before_source_processing(self):
        changed = copy.deepcopy(self.contract)
        changed["frozen_repair"]["accepted_run_token_regex"] = "[0-9]{1,64}"
        with self.assertRaises(vr16a.VariableWidthRunIndexRepairRefusal) as raised:
            vr16a.adapt_variable_width_source(
                self.sources["two_digit_control"], contract=changed
            )
        self.assertEqual(raised.exception.route, vr16a.REFUSAL_ROUTES[0])

    def test_qualification_passes_exact_matrix_and_refusals(self):
        self.assertEqual(self.report["route"], vr16a.SUCCESS_ROUTE)
        matrix = self.report["matrix"]
        self.assertEqual(matrix["success_paths"], 24)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(matrix["distinct_raw_source_hashes"], 6)
        self.assertEqual(matrix["distinct_source_exact_selected_name_hashes"], 6)
        self.assertGreaterEqual(self.report["refusals"]["direct_refusals"], 48)

    def test_qualification_measurements_and_output_are_bounded(self):
        measured = self.report["measurements"]
        self.assertEqual(measured["runtime_seconds"], 1.5)
        self.assertEqual(measured["peak_RSS_bytes"], 64 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(measured["temporary_peak_bytes"], 2 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(
            measured["aggregate_output_bytes"],
            len(vr16a._canonical_json_bytes(self.report)),
        )

    def test_forbidden_counters_and_public_output_are_clean(self):
        self.assertTrue(
            all(value == 0 for value in self.report["operation_counters"].values())
        )
        text = json.dumps(self.report, sort_keys=True)
        for key in ("member_name", "subject_id", "target", "private_manifest"):
            self.assertNotIn(f'"{key}":', text)
        vr16a._assert_public_report_safe(self.report)

    def test_cli_help_and_plan_expose_no_private_execution(self):
        environment = {
            **os.environ,
            **vr16a.THREAD_ENVIRONMENT,
            "PYTHONPATH": str(ROOT / "src"),
        }
        help_result = subprocess.run(
            [sys.executable, "-m", vr16a.__name__, "--help"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertNotIn("execute", help_result.stdout)
        plan_result = subprocess.run(
            [sys.executable, "-m", vr16a.__name__, "plan"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
        plan = json.loads(plan_result.stdout)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["execute_surface_available"])
        self.assertFalse(plan["cohort_freeze_authorized"])
        self.assertFalse(plan["FW2_authorized"])
        self.assertFalse(plan["CIL1_authorized"])


if __name__ == "__main__":
    unittest.main()
