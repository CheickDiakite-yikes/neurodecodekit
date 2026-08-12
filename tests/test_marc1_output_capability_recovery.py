from __future__ import annotations

import copy
import json
import os
import pickle
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc1_output_capability_recovery as recovery


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


class MARC1OutputCapabilityRecoveryTests(unittest.TestCase):
    def temporary_directory(self):
        return tempfile.TemporaryDirectory(dir=recovery._canonical_temp_parent())

    def qualify(self, output: Path):
        ticks = iter((100.0, 100.125))
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            return recovery.qualify_generated_output_capability(
                output,
                repo_root=ROOT,
                clock=lambda: next(ticks),
                rss_reader=lambda: 32 * 1024**2,
            )

    def test_policy_contract_and_green_proof_are_exact(self) -> None:
        self.assertEqual(
            recovery._policy_sha256(),
            "6412dd0cdfabf2b96d0c5ebf2d1e2dadb4fc3e8fe5eed6ac762524a5c9881054",
        )
        self.assertEqual(len(recovery._canonical_json_bytes(recovery.CANDIDATE_POLICY)), 672)
        self.assertEqual(
            recovery.CONTRACT_SHA256,
            "2fe17a263a8c923c2a7af76dbba0c6422eacb601b7668de987ef0d53485c5cb6",
        )
        self.assertEqual(
            recovery.GREEN_CONTRACT_COMMIT,
            "baade51146309bd3b3fa6c1750a36482669a0ff2",
        )
        self.assertEqual(recovery.GREEN_CONTRACT_CI_RUN_ID, 31597291352)
        self.assertEqual(recovery.GREEN_CONTRACT_BASE_JOB_ID, 94115807028)
        self.assertEqual(recovery.GREEN_CONTRACT_OPTIONAL_JOB_ID, 94115807008)

    def test_source_surface_has_only_four_commands_and_no_eager_import(self) -> None:
        surface = recovery.inspect_source_surface()
        self.assertEqual(
            surface["commands"], ["inspect", "plan", "preflight", "qualify"]
        )
        self.assertEqual(surface["network_client_imports"], 0)
        self.assertEqual(surface["module_scope_consumed_pagination_imports"], 0)
        self.assertEqual(surface["forbidden_consumed_qualifier_calls"], 0)
        self.assertEqual(surface["absolute_path_write_calls"], 0)

    def test_registered_path_identity_is_bound_without_being_opened(self) -> None:
        self.assertEqual(
            recovery.REGISTERED_OUTPUT_PATH,
            "/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812",
        )
        plan = recovery.registered_plan(ROOT)
        self.assertEqual(plan["registered_output_path"], recovery.REGISTERED_OUTPUT_PATH)
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["real_or_private_input_bytes"], 0)

    def test_output_capability_is_process_local_and_nonserializable(self) -> None:
        with self.temporary_directory() as temporary:
            capability = recovery.acquire_output_capability(Path(temporary) / "out")
            try:
                with self.assertRaisesRegex(TypeError, "process-local"):
                    pickle.dumps(capability)
                self.assertGreaterEqual(capability.parent_fd, 0)
                self.assertEqual(capability.allowlisted_filenames, recovery.OUTPUT_NAMES)
            finally:
                capability.close()

    def test_path_only_preflight_has_zero_early_operations_and_no_output(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            report = recovery.preflight_output_capability(output)
            self.assertEqual(report["route"], "MARC1OP-P0")
            self.assertTrue(all(value == 0 for value in report["early_operation_counters"].values()))
            self.assertFalse(output.exists())
            self.assertEqual(report["output_bytes"], 0)

    def test_lexical_path_refusals_fail_closed(self) -> None:
        cases = (
            ("", "empty"),
            ("relative", "not absolute"),
            ("/", "root"),
            ("/private/tmp/../out", "dot component"),
            ("/private//tmp/out", "not normalized"),
        )
        for path, reason in cases:
            with self.subTest(path=path):
                with self.assertRaisesRegex(
                    recovery.OutputCapabilityRefusal, f"MARC1OP-F01: .*{reason}"
                ) as caught:
                    recovery.acquire_output_capability(path)
                self.assertIsNotNone(caught.exception.early_counters)
                self.assertTrue(
                    all(
                        value == 0
                        for value in caught.exception.early_counters.values()
                    )
                )

    def test_all_19_precapability_refusals_have_exact_routes(self) -> None:
        routes = recovery.run_precapability_refusal_matrix()
        self.assertEqual(tuple(routes), recovery.REFUSAL_CASES[:19])
        self.assertEqual(
            list(routes.values()).count("MARC1OP-F01"),
            5,
        )
        self.assertEqual(list(routes.values()).count("MARC1OP-F02"), 10)
        self.assertEqual(list(routes.values()).count("MARC1OP-F03"), 3)
        self.assertEqual(list(routes.values()).count("MARC1OP-F04"), 1)

    def test_both_path_acceptance_cases_pass(self) -> None:
        self.assertEqual(
            recovery.run_path_acceptance_matrix(),
            {
                "regular_absolute_parent_absent_child": True,
                "deeper_all_regular_ancestor_chain_absent_child": True,
            },
        )

    def test_existing_output_and_second_invocation_refuse(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            output.mkdir()
            with self.assertRaisesRegex(
                recovery.OutputCapabilityRefusal, "MARC1OP-F02"
            ):
                recovery.acquire_output_capability(output)
            second = Path(temporary) / "second"
            with self.assertRaisesRegex(
                recovery.OutputCapabilityRefusal, "MARC1OP-F07"
            ):
                recovery.acquire_output_capability(second, sequence_number=2)

    def test_output_race_is_detected_before_directory_creation(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            capability = recovery.acquire_output_capability(output)
            output.write_bytes(b"race")
            try:
                with self.assertRaisesRegex(
                    recovery.OutputCapabilityRefusal, "MARC1OP-F03"
                ):
                    recovery._create_output_directory(capability)
            finally:
                output.unlink()
                capability.close()

    def test_closed_descriptor_refuses_revalidation(self) -> None:
        with self.temporary_directory() as temporary:
            capability = recovery.acquire_output_capability(Path(temporary) / "out")
            capability.close()
            with self.assertRaisesRegex(
                recovery.OutputCapabilityRefusal, "MARC1OP-F03"
            ):
                recovery._revalidate_capability(capability)

    def test_relative_exclusive_writes_have_exact_modes_and_cleanup(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            capability = recovery.acquire_output_capability(output)
            try:
                recovery._create_output_directory(capability)
                recovery._write_relative_exclusive(
                    capability, recovery.PRIVATE_NAME, b"private\n", 0o600
                )
                recovery._write_relative_exclusive(
                    capability, recovery.REPORT_NAME, b"public\n", 0o644
                )
                private = os.stat(
                    recovery.PRIVATE_NAME,
                    dir_fd=capability.output_fd,
                    follow_symlinks=False,
                )
                public = os.stat(
                    recovery.REPORT_NAME,
                    dir_fd=capability.output_fd,
                    follow_symlinks=False,
                )
                self.assertEqual(stat.S_IMODE(private.st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(public.st_mode), 0o644)
                with self.assertRaisesRegex(
                    recovery.OutputCapabilityRefusal, "MARC1OP-F06"
                ):
                    recovery._write_relative_exclusive(
                        capability, recovery.REPORT_NAME, b"again\n", 0o644
                    )
                recovery._cleanup_capability_output(capability)
                self.assertFalse(output.exists())
            finally:
                recovery._cleanup_capability_output(capability, suppress_errors=True)
                capability.close()

    def test_full_generated_roundtrip_passes_all_gates_and_cleans(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            outcome = self.qualify(output)
        report = outcome.report
        self.assertEqual(report["route"], "MARC1OP-G1")
        self.assertTrue(all(report["acceptance_gates"].values()))
        self.assertEqual(report["refusal_summary"]["passed_count"], 32)
        self.assertEqual(report["refusal_summary"]["precapability_count"], 19)
        self.assertEqual(report["refusal_summary"]["postcapability_count"], 13)
        self.assertEqual(report["inventory_summary"]["Wrist_rows"], 55)
        self.assertEqual(report["cohort_summary"]["selected_subjects_per_axis"], 12)
        self.assertEqual(report["split_summary"]["fit_heldout_overlap"], 0)
        self.assertTrue(outcome.output_removed)
        self.assertFalse(output.exists())
        self.assertLess(outcome.generated_input_bytes, 2 * 1024**2)
        self.assertLess(outcome.generated_output_bytes, 2 * 1024**2)

    def test_final_access_ledger_matches_writes_inspection_and_cleanup(self) -> None:
        with self.temporary_directory() as temporary:
            outcome = self.qualify(Path(temporary) / "out")
        counters = outcome.report["access_counters"]
        self.assertEqual(counters["capability_acquisitions"], 1)
        self.assertEqual(counters["capability_revalidations"], 1)
        self.assertEqual(counters["repository_reads"], 10)
        self.assertEqual(counters["contract_loads"], 2)
        self.assertEqual(counters["deferred_pagination_imports"], 1)
        self.assertEqual(counters["output_files_created"], 2)
        self.assertEqual(counters["public_report_inspections"], 1)
        self.assertEqual(counters["cleanup_file_unlinks"], 2)
        self.assertEqual(counters["cleanup_directory_removals"], 1)
        self.assertEqual(
            counters["output_bytes_allocated"], outcome.generated_output_bytes
        )

    def test_every_forbidden_real_neural_model_and_claim_counter_is_zero(self) -> None:
        with self.temporary_directory() as temporary:
            outcome = self.qualify(Path(temporary) / "out")
        counters = outcome.report["access_counters"]
        allowed = {
            "capability_acquisitions",
            "capability_revalidations",
            "repository_reads",
            "contract_loads",
            "deferred_pagination_imports",
            "fixtures_constructed",
            "rows_constructed",
            "selections_run",
            "output_directories_created",
            "output_files_created",
            "output_bytes_allocated",
            "public_report_inspections",
            "cleanup_file_unlinks",
            "cleanup_directory_removals",
        }
        self.assertTrue(all(value == 0 for key, value in counters.items() if key not in allowed))

    def test_consumed_qualifier_guard_and_cli_are_never_called(self) -> None:
        from neurodecodekit.datasets import marc1_versioned_pagination as consumed

        with self.temporary_directory() as temporary, mock.patch.object(
            consumed,
            "qualify_generated_pagination",
            side_effect=AssertionError("consumed qualifier called"),
        ) as qualifier, mock.patch.object(
            consumed,
            "_assert_new_output_directory",
            side_effect=AssertionError("consumed guard called"),
        ) as guard, mock.patch.object(
            consumed,
            "main",
            side_effect=AssertionError("consumed CLI called"),
        ) as main:
            outcome = self.qualify(Path(temporary) / "out")
        self.assertEqual(outcome.report["route"], "MARC1OP-G1")
        qualifier.assert_not_called()
        guard.assert_not_called()
        main.assert_not_called()

    def test_capability_acquisition_precedes_contract_load_and_import(self) -> None:
        order: list[str] = []
        real_acquire = recovery.acquire_output_capability
        real_load = recovery.load_registered_contract
        real_import = recovery._deferred_pagination_module

        def tracked_acquire(*args, **kwargs):
            if not order:
                order.append("capability")
            return real_acquire(*args, **kwargs)

        def tracked_load(*args, **kwargs):
            self.assertEqual(order[0], "capability")
            order.append("contract")
            return real_load(*args, **kwargs)

        def tracked_import(*args, **kwargs):
            self.assertEqual(order[:2], ["capability", "contract"])
            order.append("import")
            return real_import(*args, **kwargs)

        with self.temporary_directory() as temporary, mock.patch.object(
            recovery, "acquire_output_capability", side_effect=tracked_acquire
        ), mock.patch.object(
            recovery, "load_registered_contract", side_effect=tracked_load
        ), mock.patch.object(
            recovery, "_deferred_pagination_module", side_effect=tracked_import
        ):
            self.qualify(Path(temporary) / "out")
        self.assertEqual(order[:3], ["capability", "contract", "import"])

    def test_source_order_makes_acquisition_the_first_call_in_both_commands(self) -> None:
        source = (
            ROOT
            / "src/neurodecodekit/datasets/marc1_output_capability_recovery.py"
        ).read_text(encoding="utf-8")
        preflight = source[
            source.index("def preflight_output_capability(") : source.index(
                "def qualify_generated_output_capability("
            )
        ]
        qualify = source[
            source.index("def qualify_generated_output_capability(") : source.index(
                "def inspect_generated_report("
            )
        ]
        for body in (preflight, qualify):
            with self.subTest(function=body.splitlines()[0]):
                acquisition = body.index("capability = acquire_output_capability(")
                self.assertNotIn("AccessLedger()", body[:acquisition])
                self.assertNotIn("load_registered_contract", body[:acquisition])
                self.assertNotIn("import_module", body[:acquisition])

    def test_deterministic_replay_is_byte_identical_across_output_paths(self) -> None:
        with self.temporary_directory() as temporary:
            first = self.qualify(Path(temporary) / "first")
            second = self.qualify(Path(temporary) / "second")
        self.assertEqual(first.report_bytes, second.report_bytes)
        self.assertEqual(first.public_report_sha256, second.public_report_sha256)
        self.assertEqual(first.private_manifest_sha256, second.private_manifest_sha256)

    def test_public_inspection_does_not_open_private_peer(self) -> None:
        with self.temporary_directory() as temporary:
            outcome = self.qualify(Path(temporary) / "qualification")
            root = Path(temporary) / "inspection"
            root.mkdir()
            report_path = root / recovery.REPORT_NAME
            private_path = root / recovery.PRIVATE_NAME
            report_path.write_bytes(outcome.report_bytes)
            private_path.write_bytes(b"must-not-open")
            real_open = os.open
            opened: list[str] = []

            def tracked_open(path, *args, **kwargs):
                opened.append(os.fspath(path))
                return real_open(path, *args, **kwargs)

            with mock.patch.object(os, "open", side_effect=tracked_open):
                inspected = recovery.inspect_generated_report(report_path)
        self.assertEqual(inspected["route"], "MARC1OP-G1")
        self.assertIn(os.fspath(report_path), opened)
        self.assertNotIn(os.fspath(private_path), opened)

    def test_tampered_or_wrongly_named_public_report_refuses(self) -> None:
        with self.temporary_directory() as temporary:
            outcome = self.qualify(Path(temporary) / "qualification")
            wrong_name = Path(temporary) / "wrong.json"
            wrong_name.write_bytes(outcome.report_bytes)
            with self.assertRaisesRegex(
                recovery.OutputCapabilityRefusal, "MARC1OP-F06"
            ):
                recovery.inspect_generated_report(wrong_name)
            report = copy.deepcopy(outcome.report)
            report["route"] = "MARC1OP-P0"
            tampered = Path(temporary) / recovery.REPORT_NAME
            tampered.write_bytes(recovery._canonical_json_bytes(report))
            with self.assertRaisesRegex(
                recovery.OutputCapabilityRefusal, "MARC1OP-F06"
            ):
                recovery.inspect_generated_report(tampered)

    def test_resource_and_target_mutations_refuse(self) -> None:
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            with self.assertRaisesRegex(
                recovery.OutputCapabilityRefusal, "MARC1OP-F06"
            ):
                recovery._assert_resources(31.0, 1, 1, 1)
        with mock.patch.dict(
            os.environ, {**THREAD_ENV, "OPENBLAS_NUM_THREADS": "2"}, clear=False
        ):
            with self.assertRaisesRegex(
                recovery.OutputCapabilityRefusal, "MARC1OP-F06"
            ):
                recovery._assert_resources(1.0, 1, 1, 1)

    def test_public_report_has_warnings_unavailable_fields_and_claim_boundary(self) -> None:
        with self.temporary_directory() as temporary:
            report = self.qualify(Path(temporary) / "out").report
        self.assertGreaterEqual(len(report["warnings"]), 4)
        self.assertIn("neural_signal", report["unavailable_fields"])
        self.assertTrue(report["claim_boundary"]["same_thought_to_text_path"])
        self.assertFalse(report["claim_boundary"]["is_pivot"])
        self.assertIn(
            "No dataset body",
            report["claim_boundary"]["scientific_claim_not_established"],
        )

    def test_cli_help_and_plan_are_dependency_light(self) -> None:
        parser = recovery._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(
            parser.parse_args(["preflight", "--output", "/private/tmp/example"]).command,
            "preflight",
        )
        with mock.patch("builtins.print") as printer:
            self.assertEqual(recovery.main(["plan", "--repo-root", str(ROOT)]), 0)
        payload = json.loads(printer.call_args.args[0])
        self.assertEqual(payload["lane_id"], "MARC1-OP1")
        self.assertEqual(payload["payload_signal_target_model_or_score_operations"], 0)


if __name__ == "__main__":
    unittest.main()
