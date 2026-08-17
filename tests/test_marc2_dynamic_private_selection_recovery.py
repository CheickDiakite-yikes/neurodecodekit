import contextlib
import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_dynamic_live_selection as dynamic
from neurodecodekit.datasets import (
    marc2_dynamic_private_selection_recovery as recovery,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENVIRONMENT = {name: "1" for name in recovery.THREAD_ENVIRONMENT}


class Marc2DynamicPrivateSelectionRecoveryTests(unittest.TestCase):
    def test_plan_is_fixed_and_stops_before_FW2(self):
        plan = recovery.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-VR7P")
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertEqual(
            plan["fixed_paths"]["private_source"],
            recovery.PRIVATE_SOURCE_RELATIVE_PATH.as_posix(),
        )
        self.assertFalse(plan["generic_path_URL_retry_resume_or_fallback_argument"])
        self.assertFalse(plan["FW2_neural_or_live_run_authorized"])
        self.assertEqual(plan["network_or_archive_payload_bytes"], 0)

    def test_green_decision_and_fixed_artifact_hashes_are_exact(self):
        count, total = recovery._verify_green_inputs(ROOT)
        self.assertEqual(count, 12)
        self.assertEqual(total, 250_996)
        self.assertEqual(
            recovery.DECISION_COMMIT,
            "a318521cf9adb057617e839ead0003d89c3cab84",
        )
        self.assertEqual(recovery.DECISION_CI_RUN_ID, 31_979_669_507)

    def test_new_module_does_not_import_or_call_consumed_executor(self):
        source = Path(recovery.__file__).read_text(encoding="utf-8")
        self.assertNotIn("marc2_machine_stable_private_recovery", source)
        self.assertNotIn("marc2_live_domain_private_recovery", source)

    def test_all_generated_profiles_reach_dynamic_counts(self):
        for profile, expected in dynamic.PROFILE_COUNTS.items():
            with self.subTest(profile=profile):
                outcome = recovery._run_generated_fixture(ROOT, profile, "canonical")
                cohort = outcome.aggregate_report["cohort_summary"]
                self.assertEqual(cohort["selected_subjects"], expected)
                self.assertEqual(cohort["selected_bundles"], expected * 6)
                self.assertEqual(cohort["selected_members"], expected * 24)
                recovery.validate_aggregate_report(outcome.aggregate_report)

    def test_row_orders_preserve_normalized_selection_and_raw_provenance(self):
        for profile in dynamic.PROFILE_COUNTS:
            with self.subTest(profile=profile):
                canonical = recovery._run_generated_fixture(
                    ROOT, profile, "canonical"
                )
                reversed_rows = recovery._run_generated_fixture(
                    ROOT, profile, "reversed"
                )
                self.assertEqual(
                    canonical.private_manifest_bytes,
                    reversed_rows.private_manifest_bytes,
                )
                self.assertEqual(
                    canonical.aggregate_report["selection_hashes"][
                        "selection_identity_sha256"
                    ],
                    reversed_rows.aggregate_report["selection_hashes"][
                        "selection_identity_sha256"
                    ],
                )
                self.assertNotEqual(
                    canonical.aggregate_report["source_summary"]["input_sha256"],
                    reversed_rows.aggregate_report["source_summary"]["input_sha256"],
                )

    def test_marker_write_immediately_precedes_source_open(self):
        events = []
        real_write = recovery._write_exclusive
        real_read = recovery._read_exact_nofollow

        def write(path, payload, **kwargs):
            events.append(("write", path.name))
            return real_write(path, payload, **kwargs)

        def read(root, identity, snapshot, route):
            events.append(("read", identity.relative_path.as_posix()))
            return real_read(root, identity, snapshot, route)

        with mock.patch.object(recovery, "_write_exclusive", side_effect=write), mock.patch.object(
            recovery, "_read_exact_nofollow", side_effect=read
        ):
            recovery._run_generated_fixture(ROOT, "lower_middle", "canonical")
        marker = ("write", recovery.MARKER_NAME)
        source = ("read", recovery.PRIVATE_SOURCE_RELATIVE_PATH.as_posix())
        self.assertEqual(events.index(source), events.index(marker) + 1)

    def test_VR6_adapter_is_called_once_per_sequence(self):
        with mock.patch.object(
            dynamic,
            "adapt_dynamic_live_source",
            wraps=dynamic.adapt_dynamic_live_source,
        ) as wrapped:
            recovery._run_generated_fixture(ROOT, "reference_middle", "canonical")
        self.assertEqual(wrapped.call_count, 1)

    def test_generated_sequence_outputs_have_exact_modes_and_inventory(self):
        vr2_contract = recovery.vr2.load_registered_contract(ROOT)
        selector_contract = recovery.selector.load_registered_contract(ROOT)
        source = dynamic.build_generated_profile(
            "minimum_exact_cap",
            "canonical",
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
        payload = recovery._canonical_json_bytes(source)
        samples = iter(
            recovery._generated_raw_samples(
                datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
            )
        )
        times = iter(
            (
                datetime(2026, 8, 16, 12, 1, tzinfo=timezone.utc),
                datetime(2026, 8, 16, 12, 1, 1, tzinfo=timezone.utc),
            )
        )
        clocks = iter((1.0, 1.25))
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            recovery._write_generated_fixture(
                root, recovery.PRIVATE_SOURCE_RELATIVE_PATH, payload, 0o600
            )
            outcome = recovery._run_structural_sequence(
                root=root,
                proof=recovery._generated_proof(ROOT),
                source_identity=recovery.RegisteredFileIdentity(
                    recovery.PRIVATE_SOURCE_RELATIVE_PATH,
                    0o600,
                    len(payload),
                    recovery._sha256_bytes(payload),
                ),
                vr2_contract=vr2_contract,
                selector_contract=selector_contract,
                sampler=lambda _root, _sequence: next(samples),
                sleeper=lambda _seconds: None,
                environ=THREAD_ENVIRONMENT,
                now_UTC=lambda: next(times),
                clock=lambda: next(clocks),
                rss_reader=lambda: 40 * 1024**2,
                disk_reader=lambda _path: 20 * 1024**3,
                real=False,
            )
            output = root / recovery.OUTPUT_ROOT_RELATIVE_PATH
            self.assertEqual(
                outcome.output_files,
                tuple(
                    sorted(
                        (
                            recovery.MARKER_NAME,
                            recovery.PRIVATE_MANIFEST_NAME,
                            recovery.AGGREGATE_REPORT_NAME,
                        )
                    )
                ),
            )
            self.assertEqual(
                os.stat(output / recovery.MARKER_NAME).st_mode & 0o777, 0o600
            )
            self.assertEqual(
                os.stat(output / recovery.PRIVATE_MANIFEST_NAME).st_mode & 0o777,
                0o600,
            )
            self.assertEqual(
                os.stat(output / recovery.AGGREGATE_REPORT_NAME).st_mode & 0o777,
                0o644,
            )

    def test_aggregate_contains_no_private_identity(self):
        report = recovery._run_generated_fixture(
            ROOT, "upper_middle", "canonical"
        ).aggregate_report
        encoded = json.dumps(report, sort_keys=True)
        self.assertNotIn("sub-", encoded)
        self.assertNotIn(".codex_work", encoded)
        self.assertNotIn("member_name", encoded)
        self.assertNotIn("selected_subject_ids", encoded)
        self.assertIn("selected_subjects", report["cohort_summary"])

    def test_unknown_VR6_route_is_never_retained(self):
        with self.assertRaises(ValueError):
            recovery.DynamicPrivateSelectionRecoveryRefusal(
                recovery.REFUSAL_ROUTES[6],
                "refused",
                upstream_route="PRIVATE-ROUTE",
            )

    def test_wrapper_mutations_cover_required_boundaries(self):
        fixture = recovery._run_generated_fixture(
            ROOT, "minimum_exact_cap", "canonical"
        )
        groups = (
            recovery._certificate_mutations(),
            recovery._aggregate_mutations(fixture.aggregate_report),
            recovery._json_mutations(),
            recovery._file_mutations(),
            recovery._state_mutations(),
        )
        routes = {name: route for group in groups for name, route in group.items()}
        self.assertEqual(len(routes), 51)
        self.assertIn("registered_file_owner", routes)
        self.assertIn("registered_file_race", routes)
        self.assertIn("certificate_expired", routes)
        self.assertIn("aggregate_selected_ids_leak", routes)

    def test_generated_qualification_passes_85_refusals_and_zero_real_counters(self):
        times = iter((10.0, 15.0))
        upstream_times = iter((20.0, 21.0))
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False):
            report = recovery.qualify_generated(
                repo_root=ROOT,
                clock=lambda: next(times),
                rss_reader=lambda: 48 * 1024**2,
                upstream_clock=lambda: next(upstream_times),
                upstream_rss_reader=lambda: 40 * 1024**2,
            )
        self.assertEqual(report["replay"]["success_paths"], 10)
        self.assertEqual(report["replay"]["runs"], 20)
        self.assertEqual(report["mutation_summary"]["VR6_direct_mutations"], 34)
        self.assertEqual(report["mutation_summary"]["wrapper_direct_mutations"], 51)
        self.assertEqual(report["mutation_summary"]["total_direct_mutations"], 85)
        self.assertTrue(all(report["acceptance_gates"].values()))
        self.assertTrue(all(value == 0 for value in report["real_access_counters"].values()))
        self.assertEqual(report["measurements"]["retained_generated_output_bytes"], 0)

    def test_generated_qualification_is_deterministic_with_fixed_monitors(self):
        def run_once():
            times = iter((100.0, 105.0))
            upstream_times = iter((200.0, 201.0))
            with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=False):
                return recovery.qualify_generated(
                    repo_root=ROOT,
                    clock=lambda: next(times),
                    rss_reader=lambda: 48 * 1024**2,
                    upstream_clock=lambda: next(upstream_times),
                    upstream_rss_reader=lambda: 40 * 1024**2,
                )

        self.assertEqual(run_once(), run_once())

    def test_cli_refusal_emits_only_safe_route_fields(self):
        with mock.patch.object(
            recovery,
            "qualify_generated",
            side_effect=recovery.DynamicPrivateSelectionRecoveryRefusal(
                recovery.REFUSAL_ROUTES[6],
                "dynamic live selection refused",
                upstream_route=dynamic.REFUSAL_ROUTES[0],
            ),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = recovery.main(["qualify"])
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 2)
        self.assertEqual(payload["upstream_VR6_route"], dynamic.REFUSAL_ROUTES[0])
        self.assertNotIn("subject", output.getvalue().lower())
        self.assertNotIn("path", output.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
