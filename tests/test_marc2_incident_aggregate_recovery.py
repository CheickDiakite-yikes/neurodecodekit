import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_incident_aggregate_recovery as vr14p


class Marc2IncidentAggregateRecoveryTests(unittest.TestCase):
    def test_decision_dependencies_and_plan_are_exact(self):
        decision = vr14p.load_decision()
        vr14p._validate_green_dependencies()
        plan = vr14p.build_plan()
        self.assertEqual(decision["lane_id"], "MARC2-VR14P")
        self.assertEqual(plan["lane_id"], "MARC2-VR14P")
        self.assertEqual(plan["generated_paths"], 32)
        self.assertEqual(plan["aggregate_report_content_open_limit"], 1)
        self.assertEqual(plan["aggregate_report_bytes_maximum"], 65_536)
        self.assertEqual(plan["structural_source_operations"], 0)
        self.assertEqual(plan["private_manifest_operations"], 0)

    def test_all_eight_generated_routes_are_strict_and_canonical(self):
        for route in vr14p.ALLOWED_ROUTES:
            with self.subTest(route=route):
                report = vr14p._generated_report(route)
                payload = vr14p._canonical_json_bytes(report)
                parsed = vr14p._strict_json(payload)
                vr14p._validate_source_report(parsed, payload=payload)

    def test_generated_matrix_is_deterministic_and_balanced(self):
        first = vr14p._run_generated_matrix()
        second = vr14p._run_generated_matrix()
        self.assertEqual(first, second)
        self.assertEqual(first["paths"], 32)
        self.assertEqual(first["route_counts"], {route: 4 for route in vr14p.ALLOWED_ROUTES})
        self.assertEqual(len(first["replay_sha256"]), 64)

    def test_generated_fixed_path_is_bounded_and_temporary(self):
        result = vr14p._run_generated_fixed_path(
            rss_reader=lambda: 32 * 1024**2
        )
        self.assertEqual(result["route"], "MARC2VR13P-R4")
        self.assertLess(result["source_bytes"], vr14p.MAX_SOURCE_REPORT_BYTES)
        self.assertLess(result["receipt_bytes"], vr14p.MAX_OUTPUT_BYTES)
        self.assertTrue(result["temporary_root_only"])
        self.assertEqual(result["retained_output_bytes"], 0)

    def test_direct_refusal_inventory_exceeds_minimum(self):
        result = vr14p._run_direct_refusals(vr14p.load_decision())
        self.assertGreaterEqual(result["total"], 80)

    def test_qualification_is_target_free_bounded_and_retains_nothing(self):
        result = vr14p.qualify_generated(
            environment=vr14p.THREAD_ENVIRONMENT,
            rss_reader=lambda: 32 * 1024**2,
        )
        self.assertEqual(result["route"], "MARC2VR14P-G1")
        self.assertEqual(result["matrix"]["paths"], 32)
        self.assertGreaterEqual(result["direct_refusals"]["total"], 80)
        self.assertEqual(result["resources"]["retained_output_bytes"], 0)
        self.assertEqual(result["resources"]["network_bytes"], 0)
        self.assertEqual(result["counters"]["aggregate_report_operations"], 0)
        self.assertEqual(result["counters"]["structural_source_operations"], 0)
        self.assertEqual(result["counters"]["FW2_or_CIL1_operations"], 0)
        self.assertEqual(result["claim_boundary"]["scientific_ceiling"], "none")

    def test_execute_requires_arming_before_proof_or_ignored_path_access(self):
        with (
            mock.patch.object(vr14p, "_load_implementation_proof") as proof,
            mock.patch.object(vr14p, "_preflight_source_report") as preflight,
            self.assertRaises(vr14p.AggregateRecoveryRefusal) as caught,
        ):
            vr14p.execute_registered()
        self.assertEqual(caught.exception.route, "MARC2VR14P-F01")
        proof.assert_not_called()
        preflight.assert_not_called()

    def test_report_mutations_and_public_leakage_fail_closed(self):
        report = vr14p._generated_report("MARC2VR13P-R4")
        changed = copy.deepcopy(report)
        changed["resources"]["private_content_opens"] = 2
        with self.assertRaises(vr14p.AggregateRecoveryRefusal):
            vr14p._validate_source_report(changed)
        changed = copy.deepcopy(report)
        changed["claim_boundary"]["neural_effect"] = True
        with self.assertRaises(vr14p.AggregateRecoveryRefusal):
            vr14p._validate_source_report(changed)
        for key in vr14p.FORBIDDEN_PUBLIC_KEYS:
            changed = {**report, key: "redacted"}
            with (
                self.subTest(key=key),
                self.assertRaises(vr14p.AggregateRecoveryRefusal),
            ):
                vr14p._validate_source_report(changed)

    def test_strict_json_and_noncanonical_encoding_fail_closed(self):
        for payload in (b"[]\n", b'{"a":1,"a":2}\n', b'{"a":NaN}\n', b"\xff"):
            with (
                self.subTest(payload=payload),
                self.assertRaises(vr14p.AggregateRecoveryRefusal),
            ):
                vr14p._strict_json(payload)
        report = vr14p._generated_report("MARC2VR13P-R4")
        noncanonical = json.dumps(report, indent=2).encode()
        with self.assertRaises(vr14p.AggregateRecoveryRefusal):
            vr14p._validate_source_report(report, payload=noncanonical)

    def test_no_follow_size_collision_and_path_controls_fail_closed(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source.json"
            source.write_bytes(b"{}\n")
            linked = root / "linked.json"
            linked.symlink_to(source)
            with self.assertRaises(vr14p.AggregateRecoveryRefusal):
                vr14p._preflight_source_report(linked)
            oversized = root / "oversized.json"
            oversized.write_bytes(b"x" * (vr14p.MAX_SOURCE_REPORT_BYTES + 1))
            with self.assertRaises(vr14p.AggregateRecoveryRefusal):
                vr14p._preflight_source_report(oversized)
            output = vr14p._create_fresh_directory(root, Path("fresh/output"))
            self.assertTrue(output.is_dir())
            with self.assertRaises(vr14p.AggregateRecoveryRefusal):
                vr14p._create_fresh_directory(root, Path("fresh/output"))

    def test_parser_has_only_fixed_commands(self):
        parser = vr14p._build_parser()
        for command in ("plan", "qualify", "inspect", "execute"):
            self.assertEqual(parser.parse_args([command]).command, command)
        with self.assertRaises(SystemExit):
            parser.parse_args(["execute", "--source", "/tmp/other"])


if __name__ == "__main__":
    unittest.main()
