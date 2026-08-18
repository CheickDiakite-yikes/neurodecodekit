import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_p15_run_index_repair as p15


ROOT = Path(__file__).resolve().parents[1]


class Marc2P15RunIndexRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = p15.load_registered_contract()
        cls.sources = {
            variant: p15.build_generated_variant(variant, "canonical")
            for variant in p15.VARIANTS
        }
        cls.outcomes = {
            variant: p15.adapt_repaired_source(source, contract=cls.contract)
            for variant, source in cls.sources.items()
        }
        before = dict(os.environ)
        os.environ.update(p15.THREAD_ENVIRONMENT)
        try:
            times = iter((100.0, 101.25))
            cls.report = p15.qualify_generated(
                contract=cls.contract,
                clock=lambda: next(times),
                peak_rss=lambda: 64 * 1024**2,
            )
        finally:
            os.environ.clear()
            os.environ.update(before)

    def test_registration_proof_and_contract_are_exact(self):
        self.assertEqual(
            p15.CONTRACT_SHA256,
            "a6cd01e79813f79dfd7b54ee6c2d21ffb82e984b6230434127b936c513cf3f1e",
        )
        self.assertEqual(
            p15.GREEN_REGISTRATION_COMMIT,
            "5107eb3d714f7713a216b9ad4e21c06300cd8c21",
        )
        self.assertEqual(p15.GREEN_REGISTRATION_CI_RUN_ID, 32_168_117_907)
        self.assertEqual(p15.GREEN_REGISTRATION_BASE_JOB_ID, 95_812_470_306)
        self.assertEqual(p15.GREEN_REGISTRATION_OPTIONAL_JOB_ID, 95_812_470_218)

    def test_module_is_additive_dependency_light_and_has_no_execute_surface(self):
        source = Path(p15.__file__).read_text(encoding="utf-8")
        self.assertNotIn("marc2_f03_private_discriminator", source)
        self.assertNotIn("MARC2-VR11P", source)
        self.assertNotIn("def execute", source)
        self.assertNotIn("numpy", source)
        self.assertNotIn("mne", source)
        self.assertEqual(set(p15._parser()._option_string_actions), {"-h", "--help"})

    def test_repaired_parser_accepts_only_registered_run_widths(self):
        padded = p15._first_core(self.sources["padded_control"])["member_name"]
        unpadded = p15._first_core(self.sources["unpadded_single_digit"])[
            "member_name"
        ]
        padded_match = p15._repaired_core_match(padded)
        unpadded_match = p15._repaired_core_match(unpadded)
        self.assertIsNotNone(padded_match)
        self.assertIsNotNone(unpadded_match)
        self.assertEqual(int(padded_match.group("run")), int(unpadded_match.group("run")))
        self.assertIsNone(
            p15._repaired_core_match(
                padded.replace("_run-01_", "_run-001_", 1)
            )
        )
        self.assertIsNone(
            p15._repaired_core_match(padded.replace("_run-01_", "_run-x_", 1))
        )

    def test_all_spelling_variants_preserve_semantic_selection(self):
        self.assertEqual(
            {outcome.semantic_cohort_sha256 for outcome in self.outcomes.values()},
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

    def test_raw_and_source_exact_name_hashes_distinguish_spelling(self):
        self.assertEqual({value.source_sha256 for value in self.outcomes.values()}.__len__(), 3)
        self.assertEqual(
            {
                value.source_exact_selected_names_sha256
                for value in self.outcomes.values()
            }.__len__(),
            3,
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
                        row["reservation_bytes"], p15.selector._reservation_bytes(row)
                    )

    def test_source_objects_are_immutable(self):
        source = p15.build_generated_variant("unpadded_single_digit", "reversed")
        before = p15.vr2._canonical_source_bytes(source)
        p15.adapt_repaired_source(source, contract=self.contract)
        self.assertEqual(p15.vr2._canonical_source_bytes(source), before)

    def test_registered_neighboring_witnesses_refuse_on_exact_routes(self):
        routes = {
            "subject_path_filename_disagreement": p15.REFUSAL_ROUTES[2],
            "session_path_filename_disagreement": p15.REFUSAL_ROUTES[2],
            "nonnumeric_run_token": p15.REFUSAL_ROUTES[2],
            "three_digit_run_token": p15.REFUSAL_ROUTES[2],
            "mixed_lexical_run_tokens_within_bundle": p15.REFUSAL_ROUTES[4],
            "duplicate_normalized_run_companion": p15.REFUSAL_ROUTES[4],
            "wrong_task_token": p15.REFUSAL_ROUTES[3],
            "incomplete_companion_set": p15.REFUSAL_ROUTES[4],
        }
        base = self.sources["padded_control"]
        for witness, expected in routes.items():
            with self.subTest(witness=witness):
                with self.assertRaises(p15.P15RunIndexRepairRefusal) as raised:
                    p15.adapt_repaired_source(
                        p15._mutated_witness(base, witness), contract=self.contract
                    )
                self.assertEqual(raised.exception.route, expected)

    def test_contract_substitution_refuses_before_source_processing(self):
        changed = copy.deepcopy(self.contract)
        changed["frozen_repair"]["accepted_source_digit_widths"] = [1, 2, 3]
        with self.assertRaises(p15.P15RunIndexRepairRefusal) as raised:
            p15.adapt_repaired_source(
                self.sources["padded_control"], contract=changed
            )
        self.assertEqual(raised.exception.route, p15.REFUSAL_ROUTES[0])

    def test_measured_qualification_passes_exact_matrix_and_refusals(self):
        self.assertEqual(self.report["route"], p15.SUCCESS_ROUTE)
        self.assertEqual(self.report["matrix"]["success_paths"], 12)
        self.assertEqual(self.report["matrix"]["distinct_raw_source_hashes"], 3)
        self.assertEqual(
            self.report["matrix"]["distinct_source_exact_selected_name_hashes"], 3
        )
        self.assertEqual(self.report["refusals"]["direct_refusals"], 36)
        self.assertEqual(
            self.report["refusals"]["required_classes_preserved"],
            ["P15", "P16", "P18", "P19"],
        )

    def test_qualification_measurements_and_output_are_bounded(self):
        measured = self.report["measurements"]
        self.assertEqual(measured["runtime_seconds"], 1.25)
        self.assertEqual(measured["peak_RSS_bytes"], 64 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 16 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(
            measured["aggregate_output_bytes"],
            len(p15._canonical_json_bytes(self.report)),
        )

    def test_every_forbidden_operation_counter_is_zero(self):
        self.assertTrue(all(value == 0 for value in self.report["operation_counters"].values()))
        text = json.dumps(self.report, sort_keys=True)
        self.assertNotIn('"member_name":', text)
        self.assertNotIn('"subject_id":', text)
        self.assertNotIn('"target":', text)
        self.assertNotIn('"targets":', text)
        p15._assert_public_report_safe(self.report)

    def test_thread_expansion_and_public_leakage_refuse(self):
        with self.assertRaises(p15.P15RunIndexRepairRefusal) as raised:
            p15._validate_thread_environment(
                {**p15.THREAD_ENVIRONMENT, "OMP_NUM_THREADS": "2"}
            )
        self.assertEqual(raised.exception.route, p15.REFUSAL_ROUTES[8])
        with self.assertRaises(p15.P15RunIndexRepairRefusal) as raised:
            p15._assert_public_report_safe({"safe": {"member_name": "forbidden"}})
        self.assertEqual(raised.exception.route, p15.REFUSAL_ROUTES[7])

    def test_cli_help_and_plan_expose_no_private_execution(self):
        environment = {
            **os.environ,
            **p15.THREAD_ENVIRONMENT,
            "PYTHONPATH": str(ROOT / "src"),
        }
        help_result = subprocess.run(
            [sys.executable, "-m", p15.__name__, "--help"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertNotIn("execute", help_result.stdout)
        plan_result = subprocess.run(
            [sys.executable, "-m", p15.__name__, "plan"],
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
        self.assertFalse(plan["FW2_authorized"])
        self.assertFalse(plan["CIL1_authorized"])


if __name__ == "__main__":
    unittest.main()
