import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_exact_count_private_confirmation as wrapper

ROOT = Path(__file__).resolve().parents[1]


class Marc2ExactCountPrivateConfirmationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = wrapper.load_registered_request(ROOT)
        self.decision = wrapper.load_registered_decision(ROOT)

    def test_authority_and_fixed_inputs_are_exact(self):
        wrapper._verify_authority_mapping(self.request, self.decision)
        wrapper._verify_decision_proof()
        self.assertEqual(wrapper._verify_fixed_inputs(self.request, ROOT), 137_581)

    def test_plan_is_non_private_and_fixed_path_only(self):
        plan = wrapper.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR34P")
        self.assertEqual(plan["generated_paths"], 60)
        self.assertEqual(plan["exact_readiness_samples_per_path"], 3)
        self.assertEqual(plan["exact_readiness_sleeps_per_path"], 2)
        self.assertTrue(plan["fixed_path_execute"])
        self.assertFalse(plan["generic_path_or_output_arguments"])
        self.assertFalse(plan["private_detail_or_cohort_retention"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])

    def test_execute_refuses_before_authority_readiness_or_private_path_operation(self):
        refusal = wrapper.ExactCountPrivateConfirmationRefusal(
            wrapper.REFUSAL_ROUTES[1], "proof unavailable"
        )
        with (
            mock.patch.object(
                wrapper, "_require_green_implementation", side_effect=refusal
            ),
            mock.patch.object(wrapper, "load_registered_request") as request,
            mock.patch.object(wrapper, "_collect_private_readiness") as readiness,
            mock.patch.object(wrapper, "_read_bound_source_once") as source_read,
            self.assertRaises(wrapper.ExactCountPrivateConfirmationRefusal) as caught,
        ):
            wrapper.execute_fixed()
        self.assertEqual(caught.exception.route, "MARC2VR34P-F02")
        request.assert_not_called()
        readiness.assert_not_called()
        source_read.assert_not_called()

    def test_public_execute_is_proof_gated_in_current_stage(self):
        registry = ROOT / wrapper.IMPLEMENTATION_RELATIVE_PATH
        if not registry.exists():
            with self.assertRaises(
                wrapper.ExactCountPrivateConfirmationRefusal
            ) as caught:
                wrapper._require_green_implementation(ROOT)
            self.assertEqual(caught.exception.route, "MARC2VR34P-F02")
            return
        record = json.loads(registry.read_text(encoding="utf-8"))
        proof = record["remote_implementation_proof"]
        if proof is None:
            with self.assertRaises(
                wrapper.ExactCountPrivateConfirmationRefusal
            ) as caught:
                wrapper._require_green_implementation(ROOT)
            self.assertEqual(caught.exception.route, "MARC2VR34P-F02")
        else:
            self.assertEqual(wrapper._require_green_implementation(ROOT), proof["commit"])

    def test_every_nonpassing_pattern_consumes_without_source_construction(self):
        def forbidden_source():
            self.fail("nonpassing readiness constructed a source")

        for pattern in wrapper.READINESS_PATTERNS[1:]:
            with self.subTest(pattern=pattern), tempfile.TemporaryDirectory() as temp:
                result = wrapper._run_generated_case(
                    pattern=pattern,
                    source_case=None,
                    order="canonical",
                    root=Path(temp),
                    source_factory=forbidden_source,
                )
                self.assertEqual(result["route"], "MARC2VR34P-R3")
                self.assertFalse(result["readiness_ready"])
                self.assertEqual(result["readiness_provider_calls"], 3)
                self.assertEqual(result["readiness_sleeper_calls"], 2)
                self.assertEqual(result["source_constructions"], 0)
                self.assertEqual(result["source_content_opens"], 0)
                self.assertEqual(result["VR31A_calls"], 0)

    def test_all_passing_source_routes_are_exact(self):
        cases = {
            "exact_public_control": ("MARC2VR34P-G1", "MARC2VR31A-G1", 0),
            "single_session_exclusion_removed": (
                "MARC2VR34P-G2",
                "MARC2VR31A-G2",
                0,
            ),
            "eligible_bundle_removed": ("MARC2VR34P-R1", "MARC2VR31A-R1", 1),
            "eligible_bundle_added": ("MARC2VR34P-R2", "MARC2VR31A-R2", 1),
            "eligible_distribution_shift": (
                "MARC2VR34P-R3",
                "MARC2VR31A-R3",
                0,
            ),
            "eligible_distribution_shift_second": (
                "MARC2VR34P-R3",
                "MARC2VR31A-R3",
                0,
            ),
            "unknown_participant_bundle": (
                "MARC2VR34P-R3",
                "MARC2VR31A-R3",
                0,
            ),
            "incomplete_companion_set": (
                "MARC2VR34P-R3",
                "MARC2VR31A-R3",
                0,
            ),
        }
        for source_case, expected in cases.items():
            with self.subTest(source_case=source_case), tempfile.TemporaryDirectory() as temp:
                result = wrapper._run_generated_case(
                    pattern="PPP",
                    source_case=source_case,
                    order="reversed",
                    root=Path(temp),
                )
                self.assertEqual(
                    (
                        result["route"],
                        result["VR31A_route"],
                        result["R1_direction_comparisons"],
                    ),
                    expected,
                )
                self.assertTrue(result["readiness_ready"])
                self.assertEqual(result["source_constructions"], 1)
                self.assertEqual(result["source_content_opens"], 1)
                self.assertEqual(result["VR31A_calls"], 1)

    def test_marker_precedes_source_construction_and_open(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            def source_factory():
                self.assertTrue((root / "output" / wrapper.MARKER_NAME).is_file())
                return wrapper.vr31a._build_case(
                    "exact_public_control", "canonical"
                )

            real_reader = wrapper._read_bound_source_once

            def guarded_reader(path, binding):
                self.assertTrue((root / "output" / wrapper.MARKER_NAME).is_file())
                return real_reader(path, binding)

            with mock.patch.object(
                wrapper, "_read_bound_source_once", side_effect=guarded_reader
            ):
                result = wrapper._run_generated_case(
                    pattern="PPP",
                    source_case="exact_public_control",
                    order="canonical",
                    root=root,
                    source_factory=source_factory,
                )
        self.assertEqual(result["VR31A_calls"], 1)

    def test_generated_replay_is_byte_deterministic(self):
        hashes = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as temp:
                result = wrapper._run_generated_case(
                    pattern="PPP",
                    source_case="eligible_distribution_shift",
                    order="canonical",
                    root=Path(temp),
                )
                hashes.append(result["report_sha256"])
        self.assertEqual(len(set(hashes)), 1)

    def test_readiness_to_source_binding_is_strict(self):
        for pattern, source_case in (
            ("PPP", None),
            ("PPF", "exact_public_control"),
            ("unknown", None),
        ):
            with self.subTest(pattern=pattern, source_case=source_case), tempfile.TemporaryDirectory() as temp, self.assertRaises(
                wrapper.ExactCountPrivateConfirmationRefusal
            ):
                wrapper._run_generated_case(
                    pattern=pattern,
                    source_case=source_case,
                    order="canonical",
                    root=Path(temp),
                )

    def test_bound_source_rejects_symlink_mode_size_hash_schema_and_duplicate_key(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            valid = wrapper._canonical_json_bytes({"schema_name": "fixture", "x": 1})
            path = root / "source.json"
            path.write_bytes(valid)
            os.chmod(path, 0o600)
            binding = wrapper.SourceBinding(
                bytes=len(valid),
                sha256=wrapper._sha256_bytes(valid),
                schema_name="fixture",
            )
            self.assertEqual(wrapper._read_bound_source_once(path, binding)["x"], 1)

            os.chmod(path, 0o644)
            with self.assertRaises(wrapper.ExactCountPrivateConfirmationRefusal):
                wrapper._read_bound_source_once(path, binding)
            os.chmod(path, 0o600)

            for changed in (
                wrapper.SourceBinding(len(valid) + 1, binding.sha256, "fixture"),
                wrapper.SourceBinding(len(valid), "0" * 64, "fixture"),
                wrapper.SourceBinding(len(valid), binding.sha256, "other"),
            ):
                with self.assertRaises(wrapper.ExactCountPrivateConfirmationRefusal):
                    wrapper._read_bound_source_once(path, changed)

            duplicate = b'{"schema_name":"fixture","x":1,"x":2}\n'
            path.write_bytes(duplicate)
            duplicate_binding = wrapper.SourceBinding(
                len(duplicate), wrapper._sha256_bytes(duplicate), "fixture"
            )
            with self.assertRaises(wrapper.ExactCountPrivateConfirmationRefusal):
                wrapper._read_bound_source_once(path, duplicate_binding)

            target = root / "target.json"
            target.write_bytes(valid)
            os.chmod(target, 0o600)
            path.unlink()
            path.symlink_to(target)
            with self.assertRaises(wrapper.ExactCountPrivateConfirmationRefusal):
                wrapper._read_bound_source_once(path, binding)

    def test_output_is_exclusive_with_requested_mode_and_canonical(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "output.json"
            payload = wrapper._canonical_json_bytes({"a": 1})
            self.assertEqual(
                wrapper._write_exclusive(path, payload, mode=0o644), len(payload)
            )
            self.assertEqual(path.read_bytes(), payload)
            self.assertEqual(path.stat().st_mode & 0o777, 0o644)
            with self.assertRaises(wrapper.ExactCountPrivateConfirmationRefusal):
                wrapper._write_exclusive(path, payload, mode=0o644)

    def test_aggregate_firewall_rejects_every_private_field(self):
        for field in wrapper.PRIVATE_PAYLOAD_FIELDS:
            with self.subTest(field=field), self.assertRaises(
                wrapper.ExactCountPrivateConfirmationRefusal
            ):
                wrapper._assert_aggregate_safe({field: "hidden"})

    def test_unknown_upstream_routes_fail_closed(self):
        for route in ("MARC2VR31A-R4", "MARC2VR31A-F01", "unknown"):
            with self.subTest(route=route), self.assertRaises(
                wrapper.ExactCountPrivateConfirmationRefusal
            ):
                wrapper._map_vr31a_route(route)

    def test_direct_refusal_floor_exceeds_registration(self):
        count = wrapper._run_direct_refusals(self.request, self.decision)
        self.assertGreaterEqual(count, 110)

    def test_thread_environment_is_exactly_one(self):
        wrapper._validate_thread_environment(wrapper.THREAD_ENVIRONMENT)
        for key in wrapper.THREAD_ENVIRONMENT:
            changed = dict(wrapper.THREAD_ENVIRONMENT)
            changed[key] = "2"
            with self.subTest(key=key), self.assertRaises(
                wrapper.ExactCountPrivateConfirmationRefusal
            ):
                wrapper._validate_thread_environment(changed)

    def test_private_report_contains_only_aggregate_route(self):
        report = wrapper._private_report(
            route="MARC2VR34P-R1",
            implementation_commit="a" * 40,
            runtime_seconds=1.0,
            peak_rss_bytes=1,
            source_content_opens=1,
            vr31a_calls=1,
            direction_comparisons=1,
        )
        encoded = json.dumps(report, sort_keys=True)
        self.assertEqual(report["route"], "MARC2VR34P-R1")
        for forbidden in wrapper.PRIVATE_PAYLOAD_FIELDS:
            self.assertNotIn(f'"{forbidden}"', encoded)

    def test_cli_has_no_path_or_policy_override(self):
        with self.assertRaises(SystemExit):
            wrapper._parser().parse_args(["execute", "--source", "elsewhere"])


if __name__ == "__main__":
    unittest.main()
