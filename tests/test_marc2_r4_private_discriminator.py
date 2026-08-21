import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_r4_private_discriminator as vr13p


class Marc2R4PrivateDiscriminatorTests(unittest.TestCase):
    def test_decision_dependencies_and_plan_are_exact(self):
        decision = vr13p.load_decision()
        vr13p._validate_green_dependencies()
        plan = vr13p.build_plan()
        self.assertEqual(decision["lane_id"], "MARC2-VR13P")
        self.assertEqual(plan["lane_id"], "MARC2-VR13P")
        self.assertEqual(plan["generated_paths"], 32)
        self.assertEqual(plan["private_content_open_limit"], 1)
        self.assertEqual(plan["private_input_bytes"], 418_755)
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["signal_bytes"], 0)
        self.assertEqual(plan["target_bytes"], 0)

    def test_generated_matrix_calls_vr12a_once_per_path(self):
        matrix = vr13p._run_generated_matrix()
        self.assertEqual(matrix["route_counts"], vr13p._expected_generated_counts())
        self.assertEqual(matrix["VR12A_calls"], 32)
        self.assertEqual(matrix["VR13A_residual_map_calls"], 28)
        self.assertGreater(matrix["generated_input_bytes"], 10_000_000)
        self.assertEqual(len(matrix["replay_sha256"]), 64)

    def test_generated_fixed_path_state_machine_is_temporary_and_bounded(self):
        state = vr13p._run_generated_state_machine()
        self.assertEqual(state["generated_state_VR12A_calls"], 1)
        self.assertEqual(state["generated_state_residual_map_calls"], 0)
        self.assertGreater(state["generated_state_input_bytes"], 100_000)
        self.assertLess(
            state["generated_state_peak_output_bytes"],
            vr13p.MAX_COMBINED_OUTPUT_BYTES,
        )

    def test_direct_refusal_inventory_exceeds_registered_minimum(self):
        refusals = vr13p._run_direct_refusals(vr13p.load_decision())
        self.assertGreaterEqual(refusals["wrapper_refusals"], 80)
        self.assertGreaterEqual(refusals["total"], 80)

    def test_qualification_report_is_target_free_and_bounded(self):
        report = vr13p.qualify_generated(
            environment=vr13p.THREAD_ENVIRONMENT,
            rss_reader=lambda: 32 * 1024**2,
        )
        self.assertEqual(report["route"], "MARC2VR13P-G1")
        self.assertEqual(report["matrix"]["VR12A_calls"], 32)
        self.assertGreaterEqual(report["direct_refusals"]["total"], 80)
        self.assertEqual(report["resources"]["retained_output_bytes"], 0)
        self.assertEqual(report["resources"]["network_bytes"], 0)
        self.assertEqual(report["counters"]["private_or_Git_ignored_path_operations"], 0)
        self.assertEqual(report["counters"]["real_VR12A_calls"], 0)
        self.assertEqual(report["counters"]["FW2_or_CIL1_operations"], 0)
        self.assertEqual(report["claim_boundary"]["scientific_ceiling"], "none")

    def test_execute_refuses_before_readiness_or_private_path_access(self):
        with (
            mock.patch.object(vr13p, "_collect_readiness") as readiness,
            mock.patch.object(vr13p, "_preflight_private_source") as preflight,
            self.assertRaises(vr13p.R4PrivateDiscriminatorRefusal) as caught,
        ):
            vr13p.execute_registered()
        self.assertEqual(caught.exception.route, "MARC2VR13P-F01")
        readiness.assert_not_called()
        preflight.assert_not_called()

    def test_decision_mutation_and_public_leakage_fail_closed(self):
        changed = copy.deepcopy(vr13p.load_decision())
        changed["resource_caps"]["private_source_content_opens"] = 2
        with self.assertRaises(vr13p.R4PrivateDiscriminatorRefusal):
            vr13p._validate_decision(changed)
        for key in vr13p.FORBIDDEN_PUBLIC_KEYS:
            with (
                self.subTest(key=key),
                self.assertRaises(vr13p.R4PrivateDiscriminatorRefusal),
            ):
                vr13p._walk_public({key: "redacted"})

    def test_private_manifest_is_generated_source_exact_and_not_public(self):
        source = vr13p.vr13a._build_case("control_success", "canonical")
        route, repaired, residual_calls = vr13p._discriminate_source(source)
        self.assertEqual(route, "MARC2VR13P-G1")
        self.assertEqual(residual_calls, 0)
        self.assertIsNotNone(repaired)
        manifest = vr13p._private_manifest(repaired)
        self.assertGreater(len(manifest["source_exact_rows"]), 250)
        self.assertEqual(len(manifest["semantic_cohort_sha256"]), 64)
        self.assertIn("source_exact_rows", manifest)

    def test_fixed_output_helpers_reject_collision_and_symlink(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            relative = Path("fixed/output")
            output = vr13p._create_fresh_directory(root, relative)
            self.assertTrue(output.is_dir())
            with self.assertRaises(vr13p.R4PrivateDiscriminatorRefusal):
                vr13p._create_fresh_directory(root, relative)
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "fixed").symlink_to(root / "elsewhere", target_is_directory=True)
            with self.assertRaises(vr13p.R4PrivateDiscriminatorRefusal):
                vr13p._create_fresh_directory(root, Path("fixed/output"))

    def test_strict_json_and_canonical_json_reject_malformed_values(self):
        for payload in (b"[]\n", b'{"a":1,"a":2}\n', b'{"a":NaN}\n', b"\xff"):
            with (
                self.subTest(payload=payload),
                self.assertRaises(vr13p.R4PrivateDiscriminatorRefusal),
            ):
                vr13p._strict_json(payload)
        with self.assertRaises(vr13p.R4PrivateDiscriminatorRefusal):
            vr13p._canonical_json_bytes({"value": float("nan")})

    def test_cli_has_only_fixed_commands_and_qualify_serializes(self):
        parser = vr13p._build_parser()
        for command in ("plan", "qualify", "inspect", "execute"):
            self.assertEqual(parser.parse_args([command]).command, command)
        with self.assertRaises(SystemExit):
            parser.parse_args(["execute", "--source", "/tmp/other"])
        payload = json.dumps(vr13p.build_plan(), sort_keys=True)
        self.assertIn("MARC2-VR13P", payload)


if __name__ == "__main__":
    unittest.main()
