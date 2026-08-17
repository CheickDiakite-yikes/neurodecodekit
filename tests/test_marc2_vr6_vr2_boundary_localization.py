import ast
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_vr6_vr2_boundary_localization as boundary


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in boundary.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((10.0, 10.125))
    return lambda: next(values)


class Marc2Vr6Vr2BoundaryLocalizationTests(unittest.TestCase):
    def run_audit(self, root=ROOT):
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            return boundary.audit_repository(
                repo_root=root,
                clock=deterministic_clock(),
                rss_reader=lambda: 32 * 1024**2,
            )

    def build_mirror(self, root: Path):
        contract_path = ROOT / boundary.CONTRACT_RELATIVE_PATH
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        paths = [boundary.CONTRACT_RELATIVE_PATH.as_posix()]
        paths.extend(row["path"] for row in contract["fixed_inputs"])
        for relative_text in paths:
            source = ROOT / relative_text
            destination = root / relative_text
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return contract

    def test_plan_is_artifact_only(self):
        plan = boundary.plan(repo_root=ROOT)
        self.assertEqual(plan["lane_id"], "MARC2-VR8A")
        self.assertEqual(plan["fixed_input_count"], 17)
        self.assertEqual(plan["fixed_input_bytes"], 575582)
        self.assertEqual(plan["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(plan["network_bytes"], 0)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["MARC2_FW2_authorized"])

    def test_audit_reaches_registered_two_class_localization(self):
        report = self.run_audit()
        self.assertEqual(report["route"], "MARC2VR8A-R1")
        self.assertEqual(
            [row["route"] for row in report["final_compatible_VR2_classes"]],
            ["MARC2VR2-F03", "MARC2VR2-F04"],
        )
        self.assertTrue(report["route_relay"]["route_relay_loss_proven"])
        self.assertTrue(
            report["producer_envelope"]["VR2_F02_envelope_route_excluded"]
        )
        self.assertFalse(
            report["parser_and_fixture_boundary"][
                "VR2_generated_builder_calls_exact_parser_or_producer"
            ]
        )
        self.assertTrue(all(report["acceptance_gates"].values()))

    def test_audit_measurements_and_access_ledger_are_exact(self):
        report = self.run_audit()
        measurements = report["measurements"]
        self.assertEqual(measurements["input_artifact_count"], 18)
        self.assertEqual(measurements["input_bytes"], 587523)
        self.assertEqual(measurements["Python_AST_parses"], 7)
        self.assertEqual(measurements["strict_JSON_parses"], 11)
        self.assertEqual(measurements["runtime_seconds"], 0.125)
        self.assertEqual(measurements["peak_RSS_bytes"], 32 * 1024**2)
        self.assertEqual(measurements["retained_generated_output_bytes"], 0)
        counters = report["access_counters"]
        self.assertEqual(counters["committed_contract_and_artifact_reads"], 18)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key != "committed_contract_and_artifact_reads"
            )
        )

    def test_deterministic_replay_matches(self):
        first = self.run_audit()
        second = self.run_audit()
        self.assertEqual(
            boundary._canonical_json_bytes(first),
            boundary._canonical_json_bytes(second),
        )

    def test_route_classifier_is_total(self):
        self.assertEqual(
            boundary.classify_result(relay_loss=True, F02_excluded=True),
            "MARC2VR8A-R1",
        )
        self.assertEqual(
            boundary.classify_result(relay_loss=True, F02_excluded=False),
            "MARC2VR8A-R2",
        )
        self.assertEqual(
            boundary.classify_result(relay_loss=False, F02_excluded=True),
            "MARC2VR8A-R3",
        )

    def test_relay_inspection_distinguishes_both_route_attributes(self):
        vr7 = ast.parse(
            (ROOT / "src/neurodecodekit/datasets/marc2_dynamic_private_selection_recovery.py").read_text(
                encoding="utf-8"
            )
        )
        vr6 = ast.parse(
            (ROOT / "src/neurodecodekit/datasets/marc2_dynamic_live_selection.py").read_text(
                encoding="utf-8"
            )
        )
        consumed = json.loads(
            (
                ROOT
                / "registries/marc2_dynamic_private_selection_recovery_failure_result.v0.json"
            ).read_text(encoding="utf-8")
        )
        result = boundary.inspect_route_relay(vr7, vr6, consumed)
        self.assertEqual(result["VR6_outer_route"], "MARC2VR6-F02")
        self.assertEqual(result["VR6_nested_route_attribute"], "upstream_route")
        self.assertEqual(result["VR7P_reads_VR6_outer_route_attribute"], "route")
        self.assertFalse(result["VR7P_reads_VR6_nested_route_attribute"])

    def test_bound_artifact_mutation_refuses_before_AST_conclusion(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            contract = self.build_mirror(root)
            target = root / next(
                row["path"]
                for row in contract["fixed_inputs"]
                if row["role"] == "VR6_adapter_module"
            )
            target.write_bytes(target.read_bytes() + b"\n")
            with self.assertRaises(boundary.Vr6Vr2BoundaryLocalizationRefusal) as caught:
                self.run_audit(root)
        self.assertEqual(caught.exception.route, "MARC2VR8A-F01")

    def test_bound_artifact_symlink_refuses(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            contract = self.build_mirror(root)
            row = next(
                item
                for item in contract["fixed_inputs"]
                if item["role"] == "prior_VR5A_result"
            )
            target = root / row["path"]
            replacement = target.with_name("replacement.json")
            target.rename(replacement)
            target.symlink_to(replacement.name)
            with self.assertRaises(boundary.Vr6Vr2BoundaryLocalizationRefusal) as caught:
                self.run_audit(root)
        self.assertEqual(caught.exception.route, "MARC2VR8A-F01")

    def test_missing_thread_binding_refuses_before_artifact_reads(self):
        environment = copy.deepcopy(os.environ)
        environment.pop("OMP_NUM_THREADS", None)
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(boundary.Vr6Vr2BoundaryLocalizationRefusal) as caught:
                boundary.audit_repository(
                    repo_root=ROOT,
                    clock=deterministic_clock(),
                    rss_reader=lambda: 32 * 1024**2,
                )
        self.assertEqual(caught.exception.route, "MARC2VR8A-F04")

    def test_resource_cap_refuses(self):
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            with self.assertRaises(boundary.Vr6Vr2BoundaryLocalizationRefusal) as caught:
                boundary.audit_repository(
                    repo_root=ROOT,
                    clock=deterministic_clock(),
                    rss_reader=lambda: 128 * 1024**2,
                )
        self.assertEqual(caught.exception.route, "MARC2VR8A-F04")

    def test_public_firewall_rejects_private_and_scientific_keys(self):
        for value in (
            {"member_name": "hidden"},
            {"participant_id": "hidden"},
            {"target": "hidden"},
            {"path": ".codex_work/hidden"},
        ):
            with self.subTest(value=value):
                with self.assertRaises(
                    boundary.Vr6Vr2BoundaryLocalizationRefusal
                ) as caught:
                    boundary._walk_public(value)
                self.assertEqual(caught.exception.route, "MARC2VR8A-F03")

    def test_cli_has_no_execute_or_path_surface(self):
        parser = boundary._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["audit"]).command, "audit")
        with mock.patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                parser.parse_args(["execute"])
        destinations = {action.dest for action in parser._actions}
        self.assertNotIn("path", destinations)
        self.assertNotIn("url", destinations)
        self.assertNotIn("output", destinations)

    def test_module_has_no_network_private_executor_or_heavy_import(self):
        module_path = (
            ROOT
            / "src/neurodecodekit/datasets/marc2_vr6_vr2_boundary_localization.py"
        )
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        self.assertFalse(
            imports
            & {
                "mne",
                "numpy",
                "requests",
                "scipy",
                "torch",
                "urllib.request",
            }
        )
        source = module_path.read_text(encoding="utf-8")
        self.assertNotIn("def execute", source)
        self.assertNotIn(".codex_work/", source)


if __name__ == "__main__":
    unittest.main()
