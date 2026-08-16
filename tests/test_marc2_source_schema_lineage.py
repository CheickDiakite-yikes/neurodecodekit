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

from neurodecodekit.datasets import marc2_source_schema_lineage as lineage


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / lineage.CONTRACT_RELATIVE_PATH
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


class Marc2SourceSchemaLineageTests(unittest.TestCase):
    def test_contract_hash_and_identity_are_exact(self):
        payload = CONTRACT_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), lineage.CONTRACT_SHA256)
        contract = json.loads(payload)
        self.assertEqual(contract["lane_id"], "MARC2-SL1")
        self.assertEqual(len(contract["fixed_inputs"]), 9)
        self.assertTrue(all(contract["forbidden_operations"].values()))

    def test_every_fixed_artifact_hash_is_current(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        for binding in contract["fixed_inputs"]:
            with self.subTest(role=binding["role"]):
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(), binding["sha256"]
                )

    def test_plan_has_no_private_or_live_authority(self):
        value = lineage.plan(repo_root=ROOT)
        self.assertEqual(value["fixed_input_count"], 9)
        self.assertEqual(value["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(value["network_bytes"], 0)
        self.assertFalse(value["future_live_access_authorized"])

    def test_exact_alias_mismatch_routes_R2(self):
        result = lineage.classify_transport_lineage(
            producer_keys=["directory", "metadata", "tail"],
            selector_fixture_keys=["central_directory", "metadata", "tail"],
            selector_validator_keys=["central_directory", "metadata", "tail"],
            recovery_validator_keys=["central_directory", "metadata", "tail"],
        )
        self.assertEqual(result["route"], "MARC2SL-R2")
        self.assertEqual(result["producer_only_keys"], ["directory"])
        self.assertEqual(result["consumer_only_keys"], ["central_directory"])
        self.assertTrue(result["exact_single_alias_mismatch"])

    def test_exact_compatibility_routes_R1(self):
        keys = ["directory", "metadata", "tail"]
        result = lineage.classify_transport_lineage(
            producer_keys=keys,
            selector_fixture_keys=keys,
            selector_validator_keys=keys,
            recovery_validator_keys=keys,
        )
        self.assertEqual(result["route"], "MARC2SL-R1")

    def test_internal_consumer_drift_routes_R3(self):
        result = lineage.classify_transport_lineage(
            producer_keys=["directory", "metadata", "tail"],
            selector_fixture_keys=["central_directory", "metadata", "tail"],
            selector_validator_keys=["directory", "metadata", "tail"],
            recovery_validator_keys=["central_directory", "metadata", "tail"],
        )
        self.assertEqual(result["route"], "MARC2SL-R3")
        self.assertFalse(result["consumer_internal_consistent"])

    def test_duplicate_transport_key_refuses(self):
        with self.assertRaises(lineage.SourceSchemaLineageRefusal) as caught:
            lineage.classify_transport_lineage(
                producer_keys=["directory", "directory", "tail"],
                selector_fixture_keys=["central_directory", "metadata", "tail"],
                selector_validator_keys=["central_directory", "metadata", "tail"],
                recovery_validator_keys=["central_directory", "metadata", "tail"],
            )
        self.assertEqual(caught.exception.route, "MARC2SL-F02")

    def test_validator_AST_anchor_extracts_literal_transport_set(self):
        tree = ast.parse(
            "def check():\n"
            "    transport = {}\n"
            "    if set(transport) != {'metadata', 'tail', 'directory'}:\n"
            "        raise ValueError\n"
        )
        self.assertEqual(
            lineage._validator_transport_keys(tree, "check"),
            ["directory", "metadata", "tail"],
        )

    def test_missing_validator_AST_anchor_refuses(self):
        tree = ast.parse("def check():\n    return None\n")
        with self.assertRaises(lineage.SourceSchemaLineageRefusal) as caught:
            lineage._validator_transport_keys(tree, "check")
        self.assertEqual(caught.exception.route, "MARC2SL-F02")

    def test_generated_mapping_AST_anchor_extracts_literal_keys(self):
        tree = ast.parse(
            "def build():\n"
            "    return {'transport_body_sha256': "
            "{'metadata': 'a', 'tail': 'b', 'central_directory': 'c'}}\n"
        )
        self.assertEqual(
            lineage._generated_transport_keys(tree, "build"),
            ["central_directory", "metadata", "tail"],
        )

    def test_producer_forwarding_AST_anchor_is_required(self):
        valid = ast.parse(
            "def make(run):\n"
            "    manifest = {}\n"
            "    manifest['transport_body_sha256'] = "
            "dict(run.transport.get('response_body_sha256', {}))\n"
        )
        self.assertTrue(
            lineage._producer_forwards_transport(
                valid,
                function_name="make",
                destination_field="transport_body_sha256",
                source_field="response_body_sha256",
            )
        )
        invalid = ast.parse("def make(run):\n    return {}\n")
        with self.assertRaises(lineage.SourceSchemaLineageRefusal):
            lineage._producer_forwards_transport(
                invalid,
                function_name="make",
                destination_field="transport_body_sha256",
                source_field="response_body_sha256",
            )

    def test_duplicate_JSON_key_refuses(self):
        with self.assertRaises(ValueError):
            lineage._strict_json(b'{"a":1,"a":2}')

    def test_symlinked_artifact_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real = root / "real.json"
            real.write_text("{}", encoding="utf-8")
            alias = root / "alias.json"
            alias.symlink_to(real)
            with self.assertRaises(lineage.SourceSchemaLineageRefusal) as caught:
                lineage._fixed_path(root, "alias.json")
        self.assertEqual(caught.exception.route, "MARC2SL-F01")

    def test_bound_audit_mechanics_pass_with_isolated_low_RSS_baseline(self):
        with mock.patch.object(lineage, "_peak_rss_bytes", return_value=35_717_120):
            report = lineage.audit_repository(repo_root=ROOT)
        self.assertEqual(report["route"], "MARC2SL-R2")
        self.assertTrue(report["lineage"]["exact_single_alias_mismatch"])
        self.assertEqual(report["access_counters"]["private_or_Git_ignored_path_operations"], 0)

    def test_subprocess_audit_passes_or_refuses_only_inherited_RSS(self):
        environment = os.environ.copy()
        environment.update(THREAD_ENVIRONMENT)
        environment["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc2_source_schema_lineage",
                "audit",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
        if completed.returncode:
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(
                completed.stderr.strip(),
                "MARC2SL-F01: resource cap exceeded",
            )
            self.assertEqual(completed.stdout, "")
            return
        report = json.loads(completed.stdout)
        self.assertEqual(report["route"], "MARC2SL-R2")
        self.assertTrue(report["lineage"]["exact_single_alias_mismatch"])
        self.assertTrue(
            report["lineage"]["sufficient_to_explain_observed_structural_refusal"]
        )
        self.assertFalse(report["lineage"]["actual_private_field_or_value_observed"])
        self.assertEqual(report["access_counters"]["private_or_Git_ignored_path_operations"], 0)
        self.assertEqual(report["access_counters"]["MARC2_FW2_operations"], 0)
        self.assertLess(report["measurements"]["generated_output_bytes"], 1024**2)
        self.assertNotIn(".codex_work", completed.stdout)
        self.assertNotIn('"member_name"', completed.stdout)

    def test_main_plan_emits_strict_JSON(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(lineage.main(["plan"]), 0)
        self.assertEqual(json.loads(output.getvalue())["lane_id"], "MARC2-SL1")

    def test_missing_thread_environment_refuses_before_artifact_audit(self):
        environment = {name: "1" for name in lineage.THREAD_ENVIRONMENT}
        environment["OMP_NUM_THREADS"] = "2"
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(lineage.SourceSchemaLineageRefusal) as caught:
                lineage.audit_repository(repo_root=ROOT)
        self.assertEqual(caught.exception.route, "MARC2SL-F01")


if __name__ == "__main__":
    unittest.main()
