import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import (
    marc2_task_aware_private_cohort_confirmation as vr36p,
)


class TaskAwarePrivateCohortConfirmationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment = dict(vr36p.THREAD_ENVIRONMENT)

    def test_registered_authority_and_green_decision_are_exact(self):
        request = vr36p.load_registered_request()
        decision = vr36p.load_registered_decision()
        vr36p._verify_authority_mapping(request, decision)
        vr36p._verify_decision_proof()
        self.assertEqual(request["lane_id"], "MARC2-VR36P")
        self.assertEqual(
            decision["user_authorization"]["actual_message_verbatim"], "coninue"
        )
        self.assertEqual(vr36p._verify_fixed_inputs(request, decision), 211_512)

    def test_plan_is_generated_open_and_private_proof_gated(self):
        plan = vr36p.build_plan()
        self.assertEqual(plan["generated_paths"], 40)
        self.assertEqual(plan["VR33A_calls"], 40)
        self.assertEqual(plan["VR35A_calls"], 20)
        self.assertEqual(plan["private_invocation_limit_after_proof"], 1)
        self.assertEqual(plan["neural_payload_bytes"], 0)
        self.assertEqual(plan["target_bytes"], 0)
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_cli_has_only_fixed_commands_and_no_overrides(self):
        parser = vr36p._parser()
        for command in ("plan", "qualify", "inspect", "execute"):
            self.assertEqual(parser.parse_args([command]).command, command)
        with self.assertRaises(SystemExit):
            parser.parse_args(["execute", "--source", "/tmp/other"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["qualify", "--output", "/tmp/other"])

    def test_generated_readiness_calls_are_exact(self):
        ready, providers, sleepers, input_bytes = vr36p._collect_generated_readiness(
            "PPP"
        )
        self.assertTrue(ready.ready)
        self.assertEqual((providers, sleepers), (3, 2))
        self.assertGreater(input_bytes, 0)
        not_ready, providers, sleepers, _ = vr36p._collect_generated_readiness(
            "FFF"
        )
        self.assertFalse(not_ready.ready)
        self.assertEqual((providers, sleepers), (3, 2))

    def test_ready_case_matrix_maps_all_five_vr35a_routes(self):
        expected = {
            vr36p.CASES[0]: (vr36p.PRIVATE_ROUTES[0], "MARC2VR35A-G1", 1),
            vr36p.CASES[1]: (vr36p.PRIVATE_ROUTES[1], "MARC2VR35A-G2", 1),
            vr36p.CASES[2]: (vr36p.PRIVATE_ROUTES[2], "MARC2VR35A-R1", 0),
            vr36p.CASES[3]: (vr36p.PRIVATE_ROUTES[3], "MARC2VR35A-R2", 0),
            vr36p.CASES[4]: (vr36p.PRIVATE_ROUTES[4], "MARC2VR35A-R3", 0),
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index, case in enumerate(vr36p.CASES):
                case_root = root / str(index)
                case_root.mkdir()
                result = vr36p._run_generated_case(
                    pattern="PPP",
                    case=case,
                    order="canonical",
                    root=case_root,
                )
                route, upstream, cohort_writes = expected[case]
                self.assertEqual(result["route"], route)
                self.assertEqual(result["VR35A_route"], upstream)
                self.assertEqual(result["cohort_file_writes"], cohort_writes)
                self.assertEqual(result["VR35A_calls"], 1)
                self.assertTrue(result["source_unchanged"])

    def test_not_ready_constructs_no_source_and_calls_no_vr35a(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with mock.patch.object(
                vr36p.vr35a,
                "build_generated_case",
                side_effect=AssertionError("source factory must not run"),
            ):
                result = vr36p._run_generated_case(
                    pattern="FFF",
                    case=vr36p.CASES[0],
                    order="canonical",
                    root=root,
                )
        self.assertEqual(result["route"], vr36p.PRIVATE_ROUTES[5])
        self.assertEqual(result["source_constructions"], 0)
        self.assertEqual(result["source_content_opens"], 0)
        self.assertEqual(result["VR35A_calls"], 0)
        self.assertEqual(result["cohort_file_writes"], 0)

    def test_private_manifest_has_frozen_cardinalities_and_mode(self):
        source = vr36p.vr35a.build_generated_case(vr36p.CASES[0], "canonical")
        outcome = vr36p.vr35a.adapt_task_aware_source(source)
        manifest = vr36p._build_private_manifest(outcome)
        self.assertEqual(manifest["schema_name"], vr36p.PRIVATE_MANIFEST_SCHEMA_NAME)
        self.assertEqual(len(manifest["rows"]), 384)
        self.assertEqual(manifest["cohort_summary"]["selected_subjects"], 16)
        self.assertEqual(manifest["split_summary"]["selected_run_bundles"], 96)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cohort.private.json"
            payload = vr36p._canonical_json_bytes(manifest)
            self.assertEqual(vr36p._write_exclusive(path, payload), len(payload))
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_strict_json_rejects_duplicate_nonfinite_bom_and_noncanonical(self):
        invalid = [
            b'{"a":1,"a":2}\n',
            b'{"a":NaN}\n',
            b"\xef\xbb\xbf{}\n",
            b'{"a":"\x00"}\n',
            b"[]\n",
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                    vr36p._strict_json(payload)
        with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
            vr36p._strict_json(b'{ "a": 1 }\n', canonical=True)

    def test_bound_source_rejects_symlink_wrong_mode_size_and_hash(self):
        payload = vr36p._canonical_json_bytes(
            {"schema_name": "fixture", "entries": [{"x": 1}]}
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.json"
            source.write_bytes(payload)
            os.chmod(source, 0o600)
            binding = vr36p.SourceBinding(
                bytes=len(payload),
                sha256=vr36p._sha256_bytes(payload),
                schema_name="fixture",
                rows=1,
                mode=0o600,
            )
            self.assertEqual(vr36p._read_bound_source_once(source, binding)["entries"], [{"x": 1}])
            link = root / "link.json"
            link.symlink_to(source)
            with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                vr36p._read_bound_source_once(link, binding)
            os.chmod(source, 0o644)
            with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                vr36p._read_bound_source_once(source, binding)
            os.chmod(source, 0o600)
            bad = vr36p.SourceBinding(
                bytes=len(payload),
                sha256="0" * 64,
                schema_name="fixture",
                rows=1,
                mode=0o600,
            )
            with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                vr36p._read_bound_source_once(source, bad)

    def test_exclusive_writer_refuses_overwrite_and_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "out.json"
            vr36p._write_exclusive(path, b"{}\n")
            with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                vr36p._write_exclusive(path, b"{}\n")
            target = root / "target.json"
            target.write_bytes(b"{}\n")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                vr36p._write_exclusive(link, b"{}\n")

    def test_public_firewall_rejects_every_forbidden_key(self):
        for key in vr36p.FORBIDDEN_PUBLIC_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                    vr36p._assert_aggregate_safe({"nested": [{key: "x"}]})
        vr36p._assert_aggregate_safe(
            {
                "route": vr36p.PRIVATE_ROUTES[0],
                "counts": {"selected_subjects_fixed": 16},
                "warnings": ["target_free"],
            }
        )

    def test_direct_refusal_matrix_exceeds_registered_minimum(self):
        counts = vr36p._run_direct_refusals(
            vr36p.load_registered_request(), vr36p.load_registered_decision()
        )
        self.assertGreaterEqual(sum(counts.values()), 100)
        self.assertTrue(set(counts).issubset(vr36p.REFUSAL_ROUTES))

    def test_execute_and_inspect_refuse_before_green_implementation_proof(self):
        refusal = vr36p.TaskAwarePrivateCohortConfirmationRefusal(
            vr36p.REFUSAL_ROUTES[1], "proof blocked"
        )
        with (
            mock.patch.object(
                vr36p, "_require_green_implementation", side_effect=refusal
            ),
            mock.patch.object(vr36p, "load_registered_request") as load_request,
            mock.patch.object(vr36p, "_repo_root") as repo_root,
        ):
            with self.assertRaises(
                vr36p.TaskAwarePrivateCohortConfirmationRefusal
            ) as ctx:
                vr36p.execute_fixed()
            self.assertEqual(ctx.exception.route, vr36p.REFUSAL_ROUTES[1])
            load_request.assert_not_called()
            repo_root.assert_not_called()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
                vr36p._require_green_implementation(Path(temp))

    def test_resource_checks_fail_closed_without_running_matrix(self):
        with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal) as ctx:
            vr36p._assert_generated_resources(91.0, 1, 1)
        self.assertEqual(ctx.exception.route, vr36p.REFUSAL_ROUTES[9])
        with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
            vr36p._assert_generated_resources(1.0, vr36p.MAX_RSS_BYTES, 1)
        with self.assertRaises(vr36p.TaskAwarePrivateCohortConfirmationRefusal):
            vr36p._assert_generated_resources(1.0, 1, vr36p.MAX_OUTPUT_BYTES + 1)


if __name__ == "__main__":
    unittest.main()
