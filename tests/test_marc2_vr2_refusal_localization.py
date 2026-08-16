import ast
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_vr2_refusal_localization as audit


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENVIRONMENT = {name: "1" for name in audit.THREAD_ENVIRONMENT}


def _tree(relative: str) -> ast.Module:
    return ast.parse((ROOT / relative).read_text(encoding="utf-8"))


def _json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class Marc2Vr2RefusalLocalizationTests(unittest.TestCase):
    def test_plan_is_fixed_and_has_no_private_authority(self):
        value = audit.plan(repo_root=ROOT)
        self.assertEqual(value["lane_id"], "MARC2-VR5A")
        self.assertEqual(value["fixed_input_count"], 11)
        self.assertEqual(value["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(value["network_bytes"], 0)
        self.assertFalse(value["private_access_authorized"])
        self.assertFalse(value["MARC2_FW2_authorized"])

    def test_exact_wrapper_collapses_eight_routes_to_one(self):
        result = audit.inspect_wrapper_route_collapse(
            _tree(
                "src/neurodecodekit/datasets/"
                "marc2_machine_stable_private_recovery.py"
            )
        )
        self.assertTrue(result["collapse_proven"])
        self.assertFalse(result["nested_route_preserved"])
        self.assertEqual(result["diagnostic_classes_before_catch"], 8)
        self.assertEqual(result["diagnostic_classes_after_catch"], 1)
        self.assertEqual(result["diagnostic_class_reduction"], 7)

    def test_wrapper_that_preserves_route_is_not_classified_as_collapsed(self):
        tree = ast.parse(
            "def _run_structural_sequence():\n"
            "    try:\n"
            "        adapt()\n"
            "    except adapter.LiveDomainEligibilityRefusal as exc:\n"
            "        raise MachineStableRecoveryRefusal(\n"
            "            REFUSAL_ROUTES[7],\n"
            "            'VR2 structural adapter refused' + exc.route,\n"
            "        )\n"
        )
        result = audit.inspect_wrapper_route_collapse(tree)
        self.assertFalse(result["collapse_proven"])
        self.assertTrue(result["nested_route_preserved"])

    def test_exact_call_path_accounts_for_all_eight_nested_routes(self):
        result = audit.inspect_call_path(
            _tree(
                "src/neurodecodekit/datasets/"
                "marc2_live_domain_eligibility_adapter.py"
            ),
            _tree(
                "src/neurodecodekit/datasets/"
                "marc2_machine_stable_private_recovery.py"
            ),
        )
        self.assertTrue(result["contracts_loaded_before_private_sequence"])
        self.assertTrue(result["source_strict_JSON_before_VR2"])
        self.assertEqual(result["nested_routes_accounted_for"], 8)
        self.assertEqual(
            [row["route"] for row in result["route_accounting"]],
            list(audit.NESTED_ROUTES),
        )
        self.assertFalse(result["observed_nested_route_available"])

    def test_exact_selection_contract_is_generated_overconstrained(self):
        result = audit.inspect_selection_contract(
            _tree(
                "src/neurodecodekit/datasets/"
                "marc2_live_domain_eligibility_adapter.py"
            ),
            _tree(
                "src/neurodecodekit/datasets/"
                "marc2_source_validity_eligibility_repair.py"
            ),
            _tree(
                "src/neurodecodekit/datasets/"
                "marc2_freewill_prefix_selection.py"
            ),
            _json("registries/marc2_live_domain_eligibility_adapter_contract.v0.json"),
            _json("registries/marc2_live_domain_eligibility_adapter_result.v0.json"),
        )
        self.assertTrue(result["live_selection_overconstraint_proven"])
        self.assertEqual(result["exact_generated_field_count"], 9)
        self.assertEqual(result["generated_selected_subjects"], 16)
        self.assertEqual(result["generated_selected_reservation_bytes"], 8105207776)
        self.assertFalse(result["dynamic_live_subject_count_accepted"])
        self.assertFalse(result["dynamic_live_reservation_bytes_accepted"])
        self.assertFalse(result["live_source_semantics_preserved"])
        self.assertEqual(result["hardcoded_row_source_id"], "freewill_23_generated")

    def test_exact_producer_lineage_is_consistent_without_excluding_F02(self):
        result = audit.inspect_producer_lineage(
            _tree(
                "src/neurodecodekit/datasets/"
                "marc1_central_directory_live.py"
            ),
            _json("registries/marc1_freewill_central_directory_live_result.v0.json"),
            _json("registries/marc2_live_domain_eligibility_adapter_contract.v0.json"),
            _json(
                "registries/"
                "marc2_machine_stable_private_recovery_failure_result.v0.json"
            ),
        )
        self.assertTrue(result["F02_lineage_consistent"])
        self.assertFalse(
            result["F02_formally_identified_or_excluded_as_observed_route"]
        )
        self.assertFalse(result["private_field_or_row_inspected"])

    def test_frozen_classifier_routes_R1_R2_and_R3(self):
        self.assertEqual(
            audit.classify_result(
                route_collapsed=True, live_selection_overconstrained=True
            ),
            "MARC2VR5-R2",
        )
        self.assertEqual(
            audit.classify_result(
                route_collapsed=True, live_selection_overconstrained=False
            ),
            "MARC2VR5-R3",
        )
        self.assertEqual(
            audit.classify_result(
                route_collapsed=False, live_selection_overconstrained=False
            ),
            "MARC2VR5-R1",
        )

    def test_bound_audit_routes_R2_and_preserves_unknown_predicate(self):
        times = iter((10.0, 10.05))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            report = audit.audit_repository(
                repo_root=ROOT,
                clock=lambda: next(times),
                rss_reader=lambda: 41_943_040,
            )
        self.assertEqual(report["route"], "MARC2VR5-R2")
        self.assertAlmostEqual(report["measurements"]["runtime_seconds"], 0.05)
        self.assertTrue(report["wrapper_diagnostic"]["collapse_proven"])
        self.assertTrue(
            report["selection_contract_diagnostic"][
                "live_selection_overconstraint_proven"
            ]
        )
        self.assertFalse(report["root_cause"]["exact_private_predicate_proven"])
        self.assertFalse(report["root_cause"]["observed_nested_route_inferred"])
        self.assertEqual(
            report["access_counters"]["private_or_Git_ignored_path_operations"],
            0,
        )

    def test_missing_thread_environment_refuses_before_artifact_reads(self):
        environment = dict(THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(audit.Vr2RefusalLocalizationRefusal) as caught:
                audit.audit_repository(repo_root=ROOT)
        self.assertEqual(caught.exception.route, "MARC2VR5-F04")

    def test_resource_overage_refuses(self):
        times = iter((10.0, 10.05))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            with self.assertRaises(audit.Vr2RefusalLocalizationRefusal) as caught:
                audit.audit_repository(
                    repo_root=ROOT,
                    clock=lambda: next(times),
                    rss_reader=lambda: 134_217_728,
                )
        self.assertEqual(caught.exception.route, "MARC2VR5-F04")

    def test_duplicate_JSON_key_refuses(self):
        with self.assertRaises(ValueError):
            audit._strict_json(b'{"a":1,"a":2}')

    def test_symlinked_artifact_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            alias = root / "alias.json"
            alias.symlink_to(target)
            with self.assertRaises(audit.Vr2RefusalLocalizationRefusal) as caught:
                audit._fixed_path(root, "alias.json")
        self.assertEqual(caught.exception.route, "MARC2VR5-F01")

    def test_public_walker_refuses_private_fields_and_paths(self):
        with self.assertRaises(audit.Vr2RefusalLocalizationRefusal):
            audit._walk_public({"target": "x"})
        with self.assertRaises(audit.Vr2RefusalLocalizationRefusal):
            audit._walk_public({"value": ".codex_work/forbidden"})

    def test_subprocess_audit_is_bounded_and_public(self):
        environment = os.environ.copy()
        environment.update(THREAD_ENVIRONMENT)
        environment["PYTHONPATH"] = str(ROOT / "src")
        script = (
            "import json\n"
            "from pathlib import Path\n"
            "from neurodecodekit.datasets."
            "marc2_vr2_refusal_localization import audit_repository\n"
            "report = audit_repository("
            "repo_root=Path.cwd(), rss_reader=lambda: 41943040)\n"
            "print(json.dumps(report, sort_keys=True, separators=(',', ':')))\n"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["route"], "MARC2VR5-R2")
        self.assertLess(report["measurements"]["aggregate_output_bytes"], 1024**2)
        self.assertNotIn(".codex_work", completed.stdout)
        self.assertNotIn('"member_name"', completed.stdout)
        self.assertNotIn('"target"', completed.stdout)

    def test_main_plan_and_help_expose_no_execute_mode(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(audit.main(["plan"]), 0)
        self.assertEqual(json.loads(output.getvalue())["lane_id"], "MARC2-VR5A")
        parser = audit._build_parser()
        help_text = parser.format_help()
        self.assertIn("{plan,audit}", help_text)
        self.assertNotIn("execute", help_text)


if __name__ == "__main__":
    unittest.main()
