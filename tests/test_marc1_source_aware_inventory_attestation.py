from __future__ import annotations

import io
import json
import os
import pickle
import stat
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc1_source_aware_inventory_attestation as attestor


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


class MARC1SourceAwareInventoryAttestationTests(unittest.TestCase):
    def temporary_directory(self):
        return tempfile.TemporaryDirectory(dir=attestor._canonical_temp_parent())

    def qualify(self, output: Path):
        ticks = iter((100.0, 100.125))
        return attestor.qualify_generated_attestation(
            output,
            repo_root=ROOT,
            clock=lambda: next(ticks),
            rss_reader=lambda: 24 * 1024**2,
            environ=THREAD_ENV,
        )

    def test_green_contract_and_provenance_chain_are_exact(self) -> None:
        contract = attestor.load_registered_contract(ROOT)
        self.assertEqual(attestor.GREEN_CONTRACT_COMMIT, "8f64ccb6dd33df8c81382a9dafd2e84590f50061")
        self.assertEqual(attestor.GREEN_CONTRACT_CI_RUN_ID, 31616551270)
        self.assertEqual(attestor.GREEN_CONTRACT_BASE_JOB_ID, 94180673330)
        self.assertEqual(attestor.GREEN_CONTRACT_OPTIONAL_JOB_ID, 94180673125)
        self.assertEqual(contract["predicate_vector_fields"], list(attestor.PREDICATE_FIELDS))
        self.assertEqual(contract["identity_domains"], attestor.IDENTITY_DOMAINS)

    def test_source_surface_is_standard_library_generated_only(self) -> None:
        surface = attestor.inspect_source_surface()
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertEqual(surface["network_client_imports"], 0)
        self.assertEqual(surface["heavy_optional_imports"], 0)
        self.assertEqual(surface["consumed_executor_imports"], 0)
        self.assertEqual(surface["URL_opener_calls"], 0)
        self.assertEqual(surface["execute_functions"], 0)

    def test_source_surface_refuses_consumed_or_network_code(self) -> None:
        snippets = (
            "from neurodecodekit.datasets import marc1_paginated_live_metadata\n",
            "import urllib.request\n",
            "def execute():\n    return None\n",
            "import numpy\n",
        )
        for source in snippets:
            with self.subTest(source=source):
                with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F00"):
                    attestor._source_surface_from_text(source)

    def test_six_semantic_families_reach_exact_routes(self) -> None:
        observed = {}
        for name, expected in attestor.FAMILY_ROUTES.items():
            with self.subTest(name=name):
                body = attestor._fixture_json_bytes(attestor.build_generated_family(name))
                result = attestor.attest_inventory(body)
                observed[name] = result.route
                self.assertEqual(result.route, expected)
                self.assertEqual(tuple(result.predicate_vector), attestor.PREDICATE_FIELDS)
                self.assertEqual(tuple(result.hashes), tuple(attestor.IDENTITY_DOMAINS))
        self.assertEqual(observed, attestor.FAMILY_ROUTES)

    def test_optional_MD5_availability_and_unknown_extension_are_exact(self) -> None:
        partial = attestor.attest_inventory(
            attestor._fixture_json_bytes(
                attestor.build_generated_family("partial_optional_extension_exact")
            )
        )
        self.assertEqual(partial.predicate_vector["supplied_MD5_present_count"], 36)
        self.assertEqual(partial.predicate_vector["computed_MD5_present_count"], 27)
        self.assertEqual(partial.predicate_vector["MD5_pair_agreement_count"], 18)
        unknown = attestor.attest_inventory(
            attestor._fixture_json_bytes(
                attestor.build_generated_family("unknown_non_target_extension")
            )
        )
        self.assertEqual(unknown.route, "MARC1SA-R4")
        self.assertFalse(unknown.selection_available)
        self.assertIsNone(unknown.hashes["selection_sha256"])
        self.assertEqual(
            unknown.selection_unavailable_reason,
            "unknown_non_target_schema_extension",
        )
        self.assertNotIn("storage_location", json.dumps(unknown.private_record))
        self.assertNotIn("generated-value-never-retained", json.dumps(unknown.private_record))

    def test_historical_differences_are_complete_and_ordered(self) -> None:
        single = attestor.attest_inventory(
            attestor._fixture_json_bytes(
                attestor.build_generated_family("single_historical_drift")
            )
        )
        multiple = attestor.attest_inventory(
            attestor._fixture_json_bytes(
                attestor.build_generated_family("multiple_historical_drifts")
            )
        )
        self.assertEqual(single.historical_differences, attestor.EXPECTED_SINGLE_DIFFERENCES)
        self.assertEqual(
            multiple.historical_differences,
            attestor.EXPECTED_MULTIPLE_DIFFERENCES,
        )
        self.assertFalse(single.selection_available)
        self.assertFalse(multiple.selection_available)

    def test_row_and_key_reorder_preserve_every_semantic_layer(self) -> None:
        for family in attestor.FAMILY_ROUTES:
            canonical_body = attestor._fixture_json_bytes(attestor.build_generated_family(family))
            canonical = attestor.attest_inventory(canonical_body)
            canonical_projection = attestor._semantic_projection(canonical)
            transport_hashes = {canonical.hashes["transport_body_sha256"]}
            for reverse_rows, reverse_keys in ((True, False), (False, True), (True, True)):
                replay_body = attestor._fixture_json_bytes(
                    attestor.build_generated_family(
                        family,
                        reverse_rows=reverse_rows,
                        reverse_keys=reverse_keys,
                    )
                )
                replay = attestor.attest_inventory(replay_body)
                transport_hashes.add(replay.hashes["transport_body_sha256"])
                self.assertEqual(attestor._semantic_projection(replay), canonical_projection)
            self.assertGreater(len(transport_hashes), 1)

    def test_nested_target_firewall_and_strict_JSON_refuse(self) -> None:
        cases = (
            b"\xff",
            b"[",
            b'[{"id":1,"id":2}]',
            b'[{"id":NaN}]',
            b"{}",
            b"[1]",
        )
        for body in cases:
            with self.subTest(body=body):
                with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F02"):
                    attestor.attest_inventory(body)
        for key, value in (
            ("target", "x"),
            ("metadata", {"label": "x"}),
            ("metadata", [{"sentence": "x"}]),
            ("Ground-Truth", "x"),
        ):
            rows = attestor.build_generated_family("observed_extension_exact")
            rows[0][key] = value
            with self.subTest(key=key, value=value):
                with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F03"):
                    attestor.attest_inventory(attestor._fixture_json_bytes(rows))

    def test_all_52_refusals_have_exact_routes_and_no_output(self) -> None:
        ledger = attestor.AccessLedger()
        routes = attestor.run_refusal_matrix(repo_root=ROOT, ledger=ledger)
        self.assertEqual(tuple(routes), attestor.REFUSAL_CASES)
        self.assertEqual(len(routes), 52)
        self.assertEqual(list(routes.values()).count("MARC1SA-F00"), 6)
        self.assertEqual(list(routes.values()).count("MARC1SA-F02"), 6)
        self.assertEqual(list(routes.values()).count("MARC1SA-F03"), 34)
        self.assertEqual(list(routes.values()).count("MARC1SA-F04"), 6)
        self.assertLess(ledger.values["generated_input_bytes"], 2 * 1024**2)
        self.assertEqual(ledger.values["output_files_created"], 0)

    def test_output_capability_is_first_process_local_and_exactly_cleaned(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            ledger = attestor.AccessLedger()
            capability = attestor.acquire_output_capability(output, ledger)
            try:
                with self.assertRaisesRegex(TypeError, "process-local"):
                    pickle.dumps(capability)
                attestor._create_output(capability)
                attestor._write_relative(capability, attestor.PRIVATE_NAME, b"private\n")
                attestor._write_relative(capability, attestor.REPORT_NAME, b"public\n")
                for name in attestor.OUTPUT_NAMES:
                    info = os.stat(name, dir_fd=capability.output_fd, follow_symlinks=False)
                    self.assertEqual(stat.S_IMODE(info.st_mode), 0o600)
                attestor._cleanup_output(capability)
                self.assertFalse(output.exists())
            finally:
                attestor._cleanup_output(capability, suppress=True)
                capability.close()

    def test_output_preflight_refuses_symlink_existing_and_non_temp_paths(self) -> None:
        with self.temporary_directory() as temporary:
            root = Path(temporary)
            real = root / "real"
            real.mkdir()
            linked = root / "linked"
            linked.symlink_to(real, target_is_directory=True)
            existing = root / "existing"
            existing.mkdir()
            for path in (linked / "out", existing, ROOT / "forbidden-output"):
                with self.subTest(path=path):
                    with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F04"):
                        attestor.acquire_output_capability(path, attestor.AccessLedger())

    def test_full_generated_qualification_passes_and_removes_both_outputs(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "qualification"
            outcome = self.qualify(output)
            self.assertFalse(output.exists())
        report = outcome.report
        self.assertEqual(report["route"], "MARC1SA-G1")
        self.assertEqual([row["route"] for row in report["family_summary"]], list(attestor.FAMILY_ROUTES.values()))
        self.assertEqual(report["refusal_summary"]["passed"], 52)
        self.assertEqual(len(report["acceptance_gates"]), 25)
        self.assertTrue(all(report["acceptance_gates"].values()))
        self.assertTrue(outcome.output_removed)
        self.assertLess(outcome.generated_input_bytes, 2 * 1024**2)
        self.assertLess(outcome.generated_output_bytes, 2 * 1024**2)

    def test_final_counters_are_exact_and_forbidden_operations_stay_zero(self) -> None:
        with self.temporary_directory() as temporary:
            outcome = self.qualify(Path(temporary) / "qualification")
        counters = outcome.report["access_counters"]
        self.assertEqual(counters["capability_acquisitions"], 1)
        self.assertEqual(counters["capability_revalidations"], 1)
        self.assertEqual(counters["output_directories_created"], 1)
        self.assertEqual(counters["output_files_created"], 2)
        self.assertEqual(counters["public_report_inspections"], 1)
        self.assertEqual(counters["cleanup_file_unlinks"], 2)
        self.assertEqual(counters["cleanup_directory_removals"], 1)
        self.assertEqual(counters["output_bytes"], outcome.generated_output_bytes)
        self.assertTrue(attestor._forbidden_counters_zero(counters))

    def test_fixed_measurements_replay_private_and_public_outputs_exactly(self) -> None:
        with self.temporary_directory() as temporary:
            root = Path(temporary)
            first = self.qualify(root / "first")
            second = self.qualify(root / "second")
        self.assertEqual(first.private_bytes, second.private_bytes)
        self.assertEqual(first.report_bytes, second.report_bytes)
        self.assertEqual(first.private_sha256, second.private_sha256)
        self.assertEqual(first.public_sha256, second.public_sha256)

    def test_public_output_has_no_protected_values_and_private_is_allowlisted(self) -> None:
        with self.temporary_directory() as temporary:
            outcome = self.qualify(Path(temporary) / "qualification")
        public_text = outcome.report_bytes.decode("ascii")
        private_text = outcome.private_bytes.decode("ascii")
        for protected in (
            "sub-01.zip",
            "62570743",
            "https://ndownloader.figshare.com",
            attestor.SUB01_MD5,
            "generated-value-never-retained",
        ):
            self.assertNotIn(protected, public_text)
        self.assertIn("sub-01.zip", private_text)
        self.assertNotIn("storage_location", private_text)
        self.assertNotIn("generated-value-never-retained", private_text)

    def test_inspector_accepts_only_untampered_public_basename(self) -> None:
        with self.temporary_directory() as temporary:
            root = Path(temporary)
            outcome = self.qualify(root / "qualification")
            public = root / attestor.REPORT_NAME
            public.write_bytes(outcome.report_bytes)
            public.chmod(0o600)
            inspected = attestor.inspect_generated_report(public)
            self.assertEqual(inspected, outcome.report)
            private = root / attestor.PRIVATE_NAME
            private.write_bytes(outcome.private_bytes)
            with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F04"):
                attestor.inspect_generated_report(private)
            tampered = json.loads(outcome.report_bytes)
            tampered["unregistered"] = True
            public.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F04"):
                attestor.inspect_generated_report(public)

    def test_failure_after_output_creation_cleans_invocation_files(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "qualification"
            with mock.patch.object(
                attestor,
                "_read_public_relative",
                side_effect=attestor.SourceAwareRefusal("MARC1SA-F04", "injected"),
            ):
                with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F04"):
                    self.qualify(output)
            self.assertFalse(output.exists())

    def test_resource_caps_and_thread_environment_refuse(self) -> None:
        cases = (
            (31.0, 1, 1, 1, THREAD_ENV),
            (0.1, 257 * 1024**2, 1, 1, THREAD_ENV),
            (0.1, 1, 2 * 1024**2 + 1, 1, THREAD_ENV),
            (0.1, 1, 1, 2 * 1024**2 + 1, THREAD_ENV),
            (0.1, 1, 1, 1, {**THREAD_ENV, "OMP_NUM_THREADS": "2"}),
        )
        for values in cases:
            with self.subTest(values=values[:4]):
                with self.assertRaisesRegex(attestor.SourceAwareRefusal, "MARC1SA-F04"):
                    attestor._enforce_resources(*values)

    def test_plan_parser_and_cli_have_exactly_three_commands(self) -> None:
        plan = attestor.registered_plan(ROOT)
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect"])
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["payload_signal_target_model_or_score_operations"], 0)
        parser = attestor._build_parser()
        help_text = parser.format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertIn("inspect", help_text)
        self.assertNotIn("execute", help_text)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = attestor.main(["plan"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["commands"], list(attestor.COMMANDS))

    def test_cli_qualify_and_inspect_are_bounded(self) -> None:
        with self.temporary_directory() as temporary, mock.patch.dict(
            os.environ, THREAD_ENV, clear=False
        ):
            root = Path(temporary)
            stdout = io.StringIO()
            real_qualifier = attestor.qualify_generated_attestation

            def bounded_qualifier(output_dir):
                return real_qualifier(
                    output_dir,
                    repo_root=ROOT,
                    rss_reader=lambda: 24 * 1024**2,
                    environ=THREAD_ENV,
                )

            with mock.patch.object(
                attestor,
                "qualify_generated_attestation",
                side_effect=bounded_qualifier,
            ), redirect_stdout(stdout):
                code = attestor.main(["qualify", "--output-dir", str(root / "out")])
            summary = json.loads(stdout.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(summary["route"], "MARC1SA-G1")
            self.assertTrue(summary["output_removed"])
            outcome = self.qualify(root / "fixture")
            report = root / attestor.REPORT_NAME
            report.write_bytes(outcome.report_bytes)
            inspect_stdout = io.StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_code = attestor.main(["inspect", str(report)])
            self.assertEqual(inspect_code, 0)
            self.assertEqual(json.loads(inspect_stdout.getvalue())["route"], "MARC1SA-G1")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                refused = attestor.main(["inspect", str(root / attestor.PRIVATE_NAME)])
            self.assertEqual(refused, 2)
            self.assertEqual(json.loads(stderr.getvalue())["route"], "MARC1SA-F04")

    def test_claim_boundary_stays_engineering_only(self) -> None:
        with self.temporary_directory() as temporary:
            outcome = self.qualify(Path(temporary) / "qualification")
        claim = outcome.report["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["scientific_claim_established"])
        self.assertIn("thought-to-text", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
