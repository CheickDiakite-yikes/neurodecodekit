import ast
import copy
import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_f03_private_discriminator as private


THREAD_ENV = {name: "1" for name in private.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((100.0, 100.5))
    return lambda: next(values)


class Marc2F03PrivateDiscriminatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = private.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )

    def test_plan_is_fixed_and_private_execution_is_pending(self):
        plan = private.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-VR11P")
        self.assertEqual(plan["generated_cases"], 6)
        self.assertEqual(plan["required_paths"], 24)
        self.assertGreaterEqual(plan["minimum_direct_refusals"], 70)
        self.assertFalse(plan["private_execution_proof_green"])
        self.assertFalse(plan["private_execution_allowed_now"])
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["archive_member_signal_or_target_bytes"], 0)
        self.assertFalse(plan["FW2_or_CIL1_authorized"])

    def test_all_six_routes_are_replayed_four_times(self):
        routes = self.report["route_summary"]
        self.assertEqual(
            routes["ordered_routes"],
            [private.SUCCESS_ROUTE, *private.PRIVATE_ROUTES],
        )
        self.assertEqual(
            routes["route_counts"], private._expected_generated_route_counts()
        )
        self.assertTrue(routes["one_route_per_path"])
        self.assertEqual(routes["failed_values_retained"], 0)
        self.assertEqual(routes["per_item_outcomes_retained"], 0)

    def test_exact_route_mechanics_and_replay_are_frozen(self):
        replay = self.report["replay_summary"]
        self.assertEqual(replay["generated_cases"], 6)
        self.assertEqual(replay["source_orders"], 2)
        self.assertEqual(replay["exact_replays"], 2)
        self.assertEqual(replay["exact_paths"], 24)
        self.assertEqual(replay["exact_parser_entry_visits"], 29_448)
        self.assertEqual(replay["exact_VR6_calls"], 24)
        self.assertEqual(replay["exact_VR10B_calls"], 24)
        self.assertTrue(replay["byte_identical_replay"])
        self.assertEqual(len(replay["replay_digest_sha256"]), 64)

    def test_generated_fixed_path_state_machine_is_bounded_and_removed(self):
        state = self.report["fixed_path_state_machine"]
        self.assertEqual(state["generated_fixture_runs"], 1)
        self.assertEqual(state["generated_fixture_bytes"], 418_755)
        self.assertEqual(state["mock_VR6_calls"], 1)
        self.assertEqual(state["mock_VR10B_calls"], 1)
        self.assertEqual(state["observed_route"], "MARC2VR11P-R3")
        self.assertTrue(state["marker_observed_before_read"])
        self.assertEqual(state["certificate_mode"], "0600")
        self.assertEqual(state["marker_mode"], "0600")
        self.assertEqual(state["report_mode"], "0644")
        self.assertEqual(state["retained_output_bytes"], 0)

    def test_deterministic_replay_with_fixed_resource_probes(self):
        replayed = private.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )
        self.assertEqual(
            private._canonical_json_bytes(replayed),
            private._canonical_json_bytes(self.report),
        )

    def test_direct_refusals_cover_wrapper_and_upstream_boundaries(self):
        refusals = self.report["direct_refusals"]
        self.assertGreaterEqual(len(refusals), 80)
        for name in (
            "implementation_proof_pending",
            "source_hash_drift",
            "output_collision",
            "marker_missing_before_read",
            "symlink_parent",
            "duplicate_JSON",
            "unknown_private_route",
            "runtime_cap",
            "private_counter",
        ):
            self.assertIn(name, refusals)
        self.assertEqual(
            sum(value == "MARC2VR10B-proven" for value in refusals.values()), 60
        )

    def test_generated_access_counters_and_claims_are_all_closed(self):
        self.assertTrue(
            all(value == 0 for value in self.report["access_counters"].values())
        )
        claims = self.report["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["private_cause_identified"])
        self.assertFalse(claims["neural_effect"])
        self.assertFalse(claims["decoding_accuracy"])
        self.assertFalse(claims["language_or_live_decoding"])
        self.assertFalse(self.report["next_gate"]["private_execution_allowed_now"])

    def test_measurements_respect_registered_caps(self):
        measurements = self.report["measurements"]
        self.assertEqual(measurements["runtime_seconds"], 0.5)
        self.assertEqual(measurements["peak_RSS_bytes"], 64 * 1024 * 1024)
        self.assertLessEqual(measurements["generated_input_bytes"], 16 * 1024**2)
        self.assertLessEqual(
            measurements["aggregate_output_bytes"], private.MAX_COMBINED_OUTPUT_BYTES
        )
        self.assertEqual(measurements["retained_generated_output_bytes"], 0)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)
        self.assertEqual(measurements["raw_data_reads"], 0)
        self.assertEqual(measurements["real_cache_reads"], 0)
        self.assertEqual(measurements["model_runs"], 0)
        self.assertEqual(measurements["training_runs"], 0)
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_public_report_refuses_route_counter_and_identity_leakage(self):
        changed = copy.deepcopy(self.report)
        changed["route_summary"]["route_counts"] = {}
        with self.assertRaises(private.F03PrivateDiscriminatorRefusal) as route:
            private._validate_generated_report(changed)
        self.assertEqual(route.exception.route, "MARC2VR11P-F04")

        leaked = copy.deepcopy(self.report)
        leaked["member_name"] = "redacted"
        with self.assertRaises(private.F03PrivateDiscriminatorRefusal) as privacy:
            private._validate_generated_report(leaked)
        self.assertEqual(privacy.exception.route, "MARC2VR11P-F07")

        lowered = private._canonical_json_bytes(self.report).decode("ascii").lower()
        for forbidden in (
            '"member_name":',
            '"row_index":',
            '"participant_id":',
            '"target":',
            '"prediction":',
            ".codex_work",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_execute_refuses_before_private_sequence_while_proof_is_pending(self):
        with mock.patch.object(private, "_run_private_sequence") as run:
            with self.assertRaises(private.F03PrivateDiscriminatorRefusal) as refusal:
                private.execute_registered()
        self.assertEqual(refusal.exception.route, "MARC2VR11P-F01")
        run.assert_not_called()

    def test_cli_has_no_generic_path_or_execution_override(self):
        parser = private._build_parser()
        for command in ("plan", "qualify", "inspect", "execute"):
            self.assertEqual(parser.parse_args([command]).command, command)
        option_strings = {
            option for action in parser._actions for option in action.option_strings
        }
        for forbidden in (
            "--path",
            "--root",
            "--url",
            "--output",
            "--threshold",
            "--retry",
            "--resume",
            "--fallback",
        ):
            self.assertNotIn(forbidden, option_strings)

    def test_module_does_not_import_or_reference_consumed_vr9p_executor(self):
        module_path = Path(private.__file__)
        source = module_path.read_text(encoding="utf-8")
        self.assertNotIn("marc2_two_layer_private_diagnostic", source)
        tree = ast.parse(source)
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        self.assertFalse(
            any("two_layer_private_diagnostic" in name for name in imported)
        )

    def test_no_follow_reader_rejects_wrong_mode_without_opening_content(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "fixture.json"
            path.write_bytes(b"{}")
            path.chmod(0o644)
            identity = {
                "mode": 0o600,
                "bytes": 2,
                "sha256": private._sha256_bytes(b"{}"),
            }
            with self.assertRaises(private.F03PrivateDiscriminatorRefusal) as refusal:
                private._read_private_once(path, identity)
            self.assertEqual(refusal.exception.route, "MARC2VR11P-F05")

    def test_marker_validator_requires_mode_0600_and_exact_schema(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "marker.json"
            marker = {
                "schema_name": private.MARKER_SCHEMA_NAME,
                "schema_version": private.SCHEMA_VERSION,
                "lane_id": private.LANE_ID,
                "status": "consumed_before_private_content_open",
                "implementation_commit": "f" * 40,
                "retry_limit": 0,
            }
            path.write_bytes(private._canonical_json_bytes(marker))
            path.chmod(0o600)
            private._require_consumed_marker(path)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            path.chmod(0o644)
            with self.assertRaises(private.F03PrivateDiscriminatorRefusal):
                private._require_consumed_marker(path)

    def test_private_report_allowlist_rejects_extra_fields(self):
        report = {
            "schema_name": private.REPORT_SCHEMA_NAME,
            "schema_version": private.SCHEMA_VERSION,
            "lane_id": private.LANE_ID,
            "route": "MARC2VR11P-R1",
            "status": "consumed_target_free_structural_discriminator",
            "proof_posture": "aggregate_target_free_structural_diagnosis_only",
            "green_evidence": {"commit": "f" * 40},
            "measurements": {},
            "access_counters": private._base_zero_counters(),
            "warnings": [],
            "unavailable_fields": [],
            "claim_boundary": {},
            "reason": "forbidden",
        }
        with self.assertRaises(private.F03PrivateDiscriminatorRefusal) as refusal:
            private._validate_private_report(report)
        self.assertEqual(refusal.exception.route, "MARC2VR11P-F07")

    def test_registry_proof_state_and_private_gate_move_together(self):
        root = Path(private.__file__).resolve().parents[3]
        record = json.loads((root / private.IMPLEMENTATION_RELATIVE_PATH).read_text())
        proof = record["remote_implementation_proof"]
        allowed = record["next_gate"]["private_execution_allowed_now"]
        if proof is None:
            self.assertFalse(allowed)
            self.assertTrue(record["next_gate"]["implementation_commit_required"])
        else:
            self.assertEqual(
                set(proof),
                {
                    "commit",
                    "CI_run_id",
                    "base_python_job_id",
                    "optional_neuro_job_id",
                    "both_required_jobs_green",
                },
            )
            self.assertEqual(len(proof["commit"]), 40)
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertTrue(allowed)
            self.assertFalse(record["next_gate"]["implementation_commit_required"])


if __name__ == "__main__":
    unittest.main()
