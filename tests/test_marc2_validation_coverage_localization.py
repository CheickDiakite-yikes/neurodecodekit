import ast
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_validation_coverage_localization as audit


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / audit.CONTRACT_RELATIVE_PATH
THREAD_ENVIRONMENT = {name: "1" for name in audit.THREAD_ENVIRONMENT}


class Marc2ValidationCoverageLocalizationTests(unittest.TestCase):
    def test_contract_hash_identity_and_scope_are_exact(self):
        payload = CONTRACT_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), audit.CONTRACT_SHA256)
        contract = json.loads(payload)
        self.assertEqual(contract["lane_id"], "MARC2-VL1")
        self.assertEqual(len(contract["fixed_inputs"]), 9)
        self.assertTrue(all(contract["forbidden_operations"].values()))
        self.assertEqual(contract["resource_caps"]["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(contract["resource_caps"]["network_bytes"], 0)

    def test_every_fixed_artifact_hash_is_current_and_public(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        for binding in contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(".codex_work", binding["path"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(), binding["sha256"]
                )

    def test_plan_has_no_private_or_FW2_authority(self):
        value = audit.plan(repo_root=ROOT)
        self.assertEqual(value["fixed_input_count"], 9)
        self.assertEqual(value["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(value["network_bytes"], 0)
        self.assertFalse(value["private_access_authorized"])
        self.assertFalse(value["MARC2_FW2_authorized"])

    def test_exact_published_to_eligible_gap_routes_R2(self):
        result = audit.classify_coverage(
            published_participants=23,
            published_runs=238,
            eligible_participants=19,
            eligible_runs=195,
            required_companions=4,
            expected_regular_rows=1025,
            expected_source_run_bundles=195,
            fixture_uses_eligible_counts=True,
            fixture_fills_auxiliary_rows=True,
            validator_global_equality_before_filter=True,
            observed_outer_route="MARC2LAR-F02",
        )
        self.assertEqual(result["route"], "MARC2VL-R2")
        self.assertEqual(result["published_minus_eligible_runs"], 43)
        self.assertEqual(result["generated_coverage_gap_companion_slots"], 172)
        self.assertEqual(result["generated_auxiliary_regular_rows"], 245)
        self.assertTrue(result["source_domain_coverage_blind_spot"])

    def test_complete_filtered_domain_routes_R1(self):
        result = audit.classify_coverage(
            published_participants=19,
            published_runs=195,
            eligible_participants=19,
            eligible_runs=195,
            required_companions=4,
            expected_regular_rows=1025,
            expected_source_run_bundles=195,
            fixture_uses_eligible_counts=True,
            fixture_fills_auxiliary_rows=True,
            validator_global_equality_before_filter=False,
            observed_outer_route="MARC2LAR-F02",
        )
        self.assertEqual(result["route"], "MARC2VL-R1")

    def test_changed_validator_or_route_routes_R3(self):
        result = audit.classify_coverage(
            published_participants=23,
            published_runs=238,
            eligible_participants=19,
            eligible_runs=195,
            required_companions=4,
            expected_regular_rows=1025,
            expected_source_run_bundles=195,
            fixture_uses_eligible_counts=True,
            fixture_fills_auxiliary_rows=True,
            validator_global_equality_before_filter=False,
            observed_outer_route="MARC2LAR-F02",
        )
        self.assertEqual(result["route"], "MARC2VL-R3")

    def test_malformed_coverage_count_refuses(self):
        with self.assertRaises(audit.ValidationCoverageRefusal) as caught:
            audit.classify_coverage(
                published_participants=True,
                published_runs=238,
                eligible_participants=19,
                eligible_runs=195,
                required_companions=4,
                expected_regular_rows=1025,
                expected_source_run_bundles=195,
                fixture_uses_eligible_counts=True,
                fixture_fills_auxiliary_rows=True,
                validator_global_equality_before_filter=True,
                observed_outer_route="MARC2LAR-F02",
            )
        self.assertEqual(caught.exception.route, "MARC2VL-F03")

    def test_route_mapping_AST_anchor_extracts_F02_index(self):
        tree = ast.parse(
            "def adapt_and_select():\n"
            "    if exc.route.startswith('MARC2LA-F02'):\n"
            "        route = FAILURE_ROUTES[2]\n"
        )
        self.assertEqual(
            audit._route_index_for_prefix(
                tree,
                function_name="adapt_and_select",
                prefix="MARC2LA-F02",
            ),
            2,
        )

    def test_ambiguous_route_mapping_AST_anchor_refuses(self):
        tree = ast.parse("def adapt_and_select():\n    return None\n")
        with self.assertRaises(audit.ValidationCoverageRefusal) as caught:
            audit._route_index_for_prefix(
                tree,
                function_name="adapt_and_select",
                prefix="MARC2LA-F02",
            )
        self.assertEqual(caught.exception.route, "MARC2VL-F02")

    def test_exact_selector_fixture_uses_eligible_counts_and_auxiliary_fill(self):
        tree = ast.parse(
            (ROOT / "src/neurodecodekit/datasets/marc2_freewill_prefix_selection.py")
            .read_text(encoding="utf-8")
        )
        result = audit._selector_fixture_coverage(tree)
        self.assertTrue(result["uses_only_eligible_session_1_2_count_map"])
        self.assertTrue(
            result["fills_remaining_regular_rows_with_generic_auxiliary_names"]
        )

    def test_exact_live_validator_checks_global_total_before_eligibility(self):
        tree = ast.parse(
            (ROOT / "src/neurodecodekit/datasets/marc2_live_schema_adapter.py")
            .read_text(encoding="utf-8")
        )
        result = audit._live_validator_order(tree)
        self.assertLess(
            result["global_group_total_line"], result["eligibility_lookup_line"]
        )
        self.assertTrue(
            result["global_exact_group_total_precedes_eligibility_counting"]
        )

    def test_exact_producer_guarantees_are_anchored(self):
        parser_tree = ast.parse(
            (ROOT / "src/neurodecodekit/datasets/marc1_central_directory_audit.py")
            .read_text(encoding="utf-8")
        )
        live_tree = ast.parse(
            (ROOT / "src/neurodecodekit/datasets/marc1_central_directory_live.py")
            .read_text(encoding="utf-8")
        )
        self.assertTrue(all(audit._producer_guarantees(parser_tree, live_tree).values()))

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
            with self.assertRaises(audit.ValidationCoverageRefusal) as caught:
                audit._fixed_path(root, "alias.json")
        self.assertEqual(caught.exception.route, "MARC2VL-F01")

    def test_bound_audit_passes_with_deterministic_resource_measurement(self):
        times = iter((10.0, 10.05))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            report = audit.audit_repository(
                repo_root=ROOT,
                clock=lambda: next(times),
                rss_reader=lambda: 40_386_560,
            )
        self.assertEqual(report["route"], "MARC2VL-R2")
        self.assertAlmostEqual(report["measurements"]["runtime_seconds"], 0.05)
        self.assertTrue(
            report["generated_fixture_coverage"]["source_domain_coverage_blind_spot"]
        )
        self.assertFalse(
            report["route_class_localization"]["exact_private_predicate_identified"]
        )
        self.assertEqual(
            report["access_counters"]["private_or_Git_ignored_path_operations"], 0
        )

    def test_missing_thread_environment_refuses_before_audit(self):
        environment = dict(THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(audit.ValidationCoverageRefusal) as caught:
                audit.audit_repository(repo_root=ROOT)
        self.assertEqual(caught.exception.route, "MARC2VL-F03")

    def test_resource_overage_refuses(self):
        times = iter((10.0, 10.05))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            with self.assertRaises(audit.ValidationCoverageRefusal) as caught:
                audit.audit_repository(
                    repo_root=ROOT,
                    clock=lambda: next(times),
                    rss_reader=lambda: 134_217_729,
                )
        self.assertEqual(caught.exception.route, "MARC2VL-F03")

    def test_subprocess_audit_is_bounded_and_public(self):
        environment = os.environ.copy()
        environment.update(THREAD_ENVIRONMENT)
        environment["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc2_validation_coverage_localization",
                "audit",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["route"], "MARC2VL-R2")
        self.assertLess(report["measurements"]["aggregate_output_bytes"], 1024**2)
        self.assertNotIn(".codex_work", completed.stdout)
        self.assertNotIn('"member_name"', completed.stdout)

    def test_main_plan_emits_strict_JSON(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(audit.main(["plan"]), 0)
        self.assertEqual(json.loads(output.getvalue())["lane_id"], "MARC2-VL1")

    def test_public_walker_refuses_private_path_or_target_key(self):
        with self.assertRaises(audit.ValidationCoverageRefusal):
            audit._walk_public({"target": "x"})
        with self.assertRaises(audit.ValidationCoverageRefusal):
            audit._walk_public({"value": ".codex_work/forbidden"})


if __name__ == "__main__":
    unittest.main()
