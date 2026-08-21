import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import (
    marc2_suffix_identity_private_discriminator as vr15p,
)


class Marc2SuffixIdentityPrivateDiscriminatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = vr15p.qualify_generated(
            environment=vr15p.THREAD_ENVIRONMENT,
            rss_reader=lambda: 50_135_040,
        )

    def test_plan_is_fixed_and_private_stage_is_proof_gated(self):
        plan = vr15p.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR15P")
        self.assertEqual(plan["fixed_interface"], ["plan", "qualify", "inspect", "execute"])
        self.assertEqual(plan["fixed_input_bytes"], 308_187)
        self.assertEqual(plan["generated_paths"], 68)
        self.assertEqual(plan["private_content_open_limit"], 1)
        self.assertEqual(plan["private_input_bytes"], 418_755)
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["signal_bytes"], 0)
        self.assertEqual(plan["target_bytes"], 0)

    def test_generated_matrix_is_exact_and_deterministic(self):
        matrix = self.report["matrix"]
        expected_routes = [vr15p.GENERATED_SUCCESS_ROUTE, *vr15p.PRIVATE_ROUTES]
        self.assertEqual(matrix["route_counts"], {route: 4 for route in expected_routes})
        self.assertEqual(matrix["path_count"], 68)
        self.assertEqual(matrix["VR15A_calls"], 68)
        self.assertEqual(matrix["nested_VR12A_calls"], 68)
        self.assertEqual(matrix["generated_input_bytes"], 29_199_868)
        self.assertEqual(
            matrix["matrix_digest_sha256"],
            "5e16552822e94724d242758212feead71abd9d66246d71251889c51117ad953c",
        )
        self.assertEqual(matrix["retained_output_bytes"], 0)

    def test_generated_resources_and_refusals_pass(self):
        resources = self.report["resources"]
        self.assertLessEqual(resources["runtime_seconds"], 90)
        self.assertLess(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(resources["temporary_peak_bytes"], 1024**2)
        self.assertLessEqual(resources["aggregate_output_bytes"], 1024**2)
        self.assertEqual(resources["retained_output_bytes"], 0)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(self.report["direct_refusals"]["count"], 111)
        self.assertTrue(self.report["direct_refusals"]["minimum_passed"])

    def test_generated_public_report_has_no_forbidden_keys_or_operations(self):
        vr15p._walk_public(self.report)
        counters = self.report["counters"]
        for key, value in counters.items():
            if key.startswith("generated_"):
                self.assertEqual(value, 68)
            else:
                self.assertEqual(value, 0, key)
        self.assertEqual(self.report["claim_boundary"]["scientific_ceiling"], "none")
        self.assertFalse(self.report["claim_boundary"]["neural_effect"])
        self.assertFalse(self.report["claim_boundary"]["decoding_accuracy"])

    def test_execute_refuses_before_readiness_or_private_path_access(self):
        with (
            mock.patch.dict("os.environ", vr15p.THREAD_ENVIRONMENT, clear=False),
            mock.patch.object(vr15p, "_collect_readiness") as readiness,
            mock.patch.object(vr15p, "_preflight_private_source") as preflight,
            mock.patch.object(vr15p, "_read_private_once") as private_read,
        ):
            with self.assertRaises(vr15p.SuffixIdentityPrivateDiscriminatorRefusal) as ctx:
                vr15p.execute_registered()
        self.assertEqual(ctx.exception.route, "MARC2VR15P-F10")
        readiness.assert_not_called()
        preflight.assert_not_called()
        private_read.assert_not_called()

    def test_execution_proof_requires_both_remote_green_records(self):
        records = (
            {},
            {"remote_implementation_proof": None, "remote_proof_closeout": None},
            {
                "remote_implementation_proof": {"both_required_jobs_green": True},
                "remote_proof_closeout": None,
            },
            {
                "remote_implementation_proof": {"both_required_jobs_green": True},
                "remote_proof_closeout": {"both_required_jobs_green": False},
            },
        )
        for record in records:
            with self.subTest(record=record):
                with self.assertRaises(
                    vr15p.SuffixIdentityPrivateDiscriminatorRefusal
                ) as ctx:
                    vr15p._require_execution_proof(record)
                self.assertEqual(ctx.exception.route, "MARC2VR15P-F10")

    def test_decision_and_fixed_inputs_fail_closed_on_mutation(self):
        decision = vr15p.load_decision()
        changed = copy.deepcopy(decision)
        changed["private_route_contract"][0]["private_cohort_manifest_allowed"] = True
        with self.assertRaises(vr15p.SuffixIdentityPrivateDiscriminatorRefusal) as ctx:
            vr15p._validate_decision(changed)
        self.assertEqual(ctx.exception.route, "MARC2VR15P-F02")

        root = vr15p._repo_root()
        request, _proof = vr15p._load_request_and_proof(root)
        payloads = vr15p._fixed_payloads(request, root)
        first = next(iter(payloads))
        changed_payloads = dict(payloads)
        changed_payloads[first] += b"x"
        with self.assertRaises(vr15p.SuffixIdentityPrivateDiscriminatorRefusal):
            vr15p._verify_fixed_payloads(request, changed_payloads)

    def test_strict_json_and_output_firewall_reject_malformed_values(self):
        for payload in (b"[]", b'{"x":NaN}', b'{"x":1,"x":2}', b"\xff"):
            with self.subTest(payload=payload):
                with self.assertRaises(vr15p.SuffixIdentityPrivateDiscriminatorRefusal):
                    vr15p._strict_json(payload)
        for key in vr15p.FORBIDDEN_PUBLIC_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(vr15p.SuffixIdentityPrivateDiscriminatorRefusal):
                    vr15p._walk_public({key: "redacted"})

    def test_generated_writes_are_exclusive_and_no_follow(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / "value.json"
            self.assertEqual(vr15p._write_exclusive(target, b"{}\n", 0o600), 3)
            with self.assertRaises(vr15p.SuffixIdentityPrivateDiscriminatorRefusal):
                vr15p._write_exclusive(target, b"{}\n", 0o600)

    def test_cli_surface_has_no_generic_override(self):
        parser = vr15p._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["execute", "--path", "/tmp/value"])

    def test_inspection_reads_only_tracked_proof_state(self):
        inspection = vr15p.inspect_proof_state()
        self.assertEqual(inspection["lane_id"], "MARC2-VR15P")
        self.assertTrue(inspection["implementation_proof_green"])
        self.assertFalse(inspection["proof_closeout_green"])
        self.assertFalse(inspection["private_access_performed"])
        self.assertEqual(inspection["scientific_ceiling"], "none")

    def test_qualification_serializes_as_canonical_json(self):
        payload = vr15p._canonical_json_bytes(self.report)
        parsed = json.loads(payload)
        self.assertEqual(parsed, self.report)
        self.assertEqual(len(payload), self.report["resources"]["aggregate_output_bytes"])


if __name__ == "__main__":
    unittest.main()
