import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a


ROOT = Path(__file__).resolve().parents[1]


class Marc2PublishedTaskSelectorRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = vr20a.load_registered_contract()
        cls.sources = {
            variant: vr20a.build_generated_variant(variant, "canonical")
            for variant in vr20a.VARIANTS
        }
        cls.outcomes = {
            variant: vr20a.adapt_published_task_source(source)
            for variant, source in cls.sources.items()
        }
        before = dict(os.environ)
        os.environ.update(vr20a.THREAD_ENVIRONMENT)
        try:
            times = iter((100.0, 101.5))
            cls.report = vr20a.qualify_generated(
                clock=lambda: next(times), peak_rss=lambda: 64 * 1024**2
            )
        finally:
            os.environ.clear()
            os.environ.update(before)

    def test_registration_proof_and_contract_are_exact(self):
        self.assertEqual(
            vr20a.CONTRACT_SHA256,
            "a2719e0e2ab54e28675929e1982a8387406068114c2079dd3864c2c8ec022516",
        )
        self.assertEqual(
            vr20a.GREEN_REGISTRATION_COMMIT,
            "cd71807ac68f449796b6bc97745e9a0b200b2cd3",
        )
        self.assertEqual(vr20a.GREEN_REGISTRATION_CI_RUN_ID, 32_484_725_113)
        self.assertEqual(vr20a.GREEN_REGISTRATION_BASE_JOB_ID, 96_778_573_327)
        self.assertEqual(vr20a.GREEN_REGISTRATION_OPTIONAL_JOB_ID, 96_778_573_092)

    def test_module_is_additive_dependency_light_and_has_no_execute_surface(self):
        source = Path(vr20a.__file__).read_text(encoding="utf-8")
        self.assertNotIn("first_failure_stable_private_discriminator", source)
        self.assertNotIn("def execute", source)
        self.assertNotIn("numpy", source)
        self.assertNotIn("mne", source)
        self.assertEqual(set(vr20a._parser()._option_string_actions), {"-h", "--help"})

    def test_every_generated_core_name_uses_exact_published_task(self):
        for variant, source in self.sources.items():
            with self.subTest(variant=variant):
                matches = [
                    vr20a._core_match(row["member_name"])
                    for row in source["entries"]
                    if isinstance(row, dict)
                    and vr20a._core_match(row.get("member_name", "")) is not None
                ]
                self.assertEqual(len(matches), 952)
                self.assertTrue(
                    all(match.group("task") == "reachingandgrasping" for match in matches)
                )

    def test_published_four_digit_variant_is_source_exact(self):
        source = self.sources["published_four_digit"]
        outcome = self.outcomes["published_four_digit"]
        source_names = {row["member_name"] for row in source["entries"]}
        selected = outcome.selection.private_manifest["rows"]
        self.assertEqual(len(selected), 384)
        for row in selected:
            match = vr20a._core_match(row["member_name"])
            self.assertIsNotNone(match)
            self.assertEqual(len(match.group("run")), 4)
            self.assertIn(row["member_name"], source_names)
            self.assertEqual(
                row["reservation_bytes"], vr20a.selector._reservation_bytes(row)
            )

    def test_all_variants_preserve_one_semantic_selection(self):
        self.assertEqual(
            len({outcome.semantic_sha256 for outcome in self.outcomes.values()}), 1
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

    def test_source_and_selected_name_hashes_distinguish_variants(self):
        self.assertEqual(
            len({outcome.source_sha256 for outcome in self.outcomes.values()}), 5
        )
        self.assertEqual(
            len(
                {
                    outcome.source_exact_selected_names_sha256
                    for outcome in self.outcomes.values()
                }
            ),
            5,
        )

    def test_source_objects_are_immutable(self):
        source = vr20a.build_generated_variant("six_digit", "reversed")
        before = copy.deepcopy(source)
        vr20a.adapt_published_task_source(source)
        self.assertEqual(source, before)

    def test_task_alias_case_and_alternate_values_refuse(self):
        base = self.sources["published_four_digit"]
        for witness in (
            "task_freewill",
            "task_case_variant",
            "task_alternate",
            "task_prefixed",
            "task_suffixed",
            "mixed_task_within_companion_set",
        ):
            with self.subTest(witness=witness), self.assertRaises(
                vr20a.PublishedTaskSelectorRepairRefusal
            ) as caught:
                vr20a.adapt_published_task_source(
                    vr20a._mutated_witness(base, witness)
                )
            self.assertEqual(caught.exception.route, vr20a.REFUSAL_ROUTES[3])

    def test_companion_collision_and_identity_witnesses_refuse(self):
        expected = {
            "mixed_run_spelling_within_companion_set": vr20a.REFUSAL_ROUTES[4],
            "normalized_duplicate_companion": vr20a.REFUSAL_ROUTES[4],
            "incomplete_companion_set": vr20a.REFUSAL_ROUTES[4],
            "subject_repeat_mismatch": vr20a.REFUSAL_ROUTES[2],
            "session_repeat_mismatch": vr20a.REFUSAL_ROUTES[2],
            "semantic_run_zero": vr20a.REFUSAL_ROUTES[6],
            "semantic_run_four": vr20a.REFUSAL_ROUTES[6],
        }
        base = self.sources["published_four_digit"]
        for witness, route in expected.items():
            with self.subTest(witness=witness), self.assertRaises(
                vr20a.PublishedTaskSelectorRepairRefusal
            ) as caught:
                vr20a.adapt_published_task_source(
                    vr20a._mutated_witness(base, witness)
                )
            self.assertEqual(caught.exception.route, route)

    def test_contract_substitution_refuses_before_source_processing(self):
        changed = copy.deepcopy(self.contract)
        changed["frozen_repair"]["required_task_label"] = "freewill"
        with self.assertRaises(vr20a.PublishedTaskSelectorRepairRefusal) as caught:
            vr20a.adapt_published_task_source(
                self.sources["published_four_digit"], contract=changed
            )
        self.assertEqual(caught.exception.route, vr20a.REFUSAL_ROUTES[0])

    def test_qualification_passes_matrix_replay_and_refusals(self):
        self.assertEqual(self.report["route"], vr20a.SUCCESS_ROUTE)
        matrix = self.report["matrix"]
        self.assertEqual(matrix["success_paths"], 20)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(matrix["distinct_raw_source_hashes"], 5)
        self.assertEqual(matrix["distinct_source_exact_selected_name_hashes"], 5)
        self.assertGreaterEqual(self.report["refusals"]["direct_refusals"], 50)

    def test_qualification_measurements_and_output_are_bounded(self):
        measured = self.report["measurements"]
        self.assertEqual(measured["runtime_seconds"], 1.5)
        self.assertEqual(measured["peak_RSS_bytes"], 64 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(measured["temporary_peak_bytes"], 2 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)

    def test_public_report_and_forbidden_counters_are_clean(self):
        self.assertTrue(
            all(value == 0 for value in self.report["operation_counters"].values())
        )
        text = json.dumps(self.report, sort_keys=True)
        for key in ("member_name", "subject_id", "target", "private_manifest"):
            self.assertNotIn(f'"{key}":', text)
        vr20a._assert_public_report_safe(self.report)

    def test_cli_help_and_plan_expose_no_private_execution(self):
        environment = {
            **os.environ,
            **vr20a.THREAD_ENVIRONMENT,
            "PYTHONPATH": str(ROOT / "src"),
        }
        help_result = subprocess.run(
            [sys.executable, "-m", vr20a.__name__, "--help"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertNotIn("execute", help_result.stdout)
        plan_result = subprocess.run(
            [sys.executable, "-m", vr20a.__name__, "plan"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
        plan = json.loads(plan_result.stdout)
        self.assertEqual(plan["required_task_label"], "reachingandgrasping")
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["execute_surface_available"])
        self.assertFalse(plan["cohort_freeze_authorized"])
        self.assertFalse(plan["FW2_authorized"])
        self.assertFalse(plan["CIL1_authorized"])


if __name__ == "__main__":
    unittest.main()
