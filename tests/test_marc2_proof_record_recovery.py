import ast
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_proof_record_recovery as recovery


ROOT = Path(__file__).resolve().parents[1]


class Marc2ProofRecordRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = recovery.load_registered_contract(ROOT)
        cls.record = recovery.build_generated_candidate_record(ROOT)
        cls.record_bytes = recovery._record_json_bytes(cls.record)
        cls.proof = recovery._generated_proof(cls.record_bytes)

    def validate(
        self,
        record: dict | None = None,
        *,
        expected: recovery.ProofEnvelope | None = None,
        observed: recovery.ProofEnvelope | None = None,
    ) -> recovery.ValidationSummary:
        payload = (
            self.record_bytes
            if record is None
            else recovery._record_json_bytes(record)
        )
        proof = recovery._generated_proof(payload)
        return recovery.validate_implementation_record(
            payload,
            repo_root=ROOT,
            expected_proof=expected or proof,
            observed_proof=observed or proof,
        )

    def qualify(self, output: Path) -> recovery.QualificationOutcome:
        return recovery.qualify_generated_proof_record(
            output,
            repo_root=ROOT,
            peak_rss_reader=lambda: 32 * 1024**2,
        )

    def test_green_contract_proof_is_exact(self):
        self.assertEqual(recovery.CONTRACT_SHA256, (
            "0ec54f915289fd66983696bd28c2eb799c59703d1d5ccebece628f83da8b1e4b"
        ))
        self.assertEqual(
            recovery.GREEN_CONTRACT_COMMIT,
            "b86aa940d47a232535ee1e72fb22ad58ea5c2729",
        )
        self.assertEqual(recovery.GREEN_CONTRACT_CI_RUN_ID, 31_767_373_647)
        self.assertEqual(recovery.GREEN_CONTRACT_BASE_JOB_ID, 94_665_902_722)
        self.assertEqual(recovery.GREEN_CONTRACT_OPTIONAL_JOB_ID, 94_665_902_761)
        self.assertEqual(self.contract["lane_id"], recovery.LANE_ID)

    def test_plan_exposes_only_generated_commands_and_zero_private_limit(self):
        plan = recovery.registered_plan(ROOT)
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect"])
        self.assertNotIn("execute", plan["commands"])
        self.assertEqual(plan["registered_private_execution_limit"], 0)
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["private_or_real_input_bytes"], 0)
        self.assertFalse(plan["MARC2_FW2_eligible"])
        self.assertFalse(plan["scientific_claim_upgrade"])

    def test_module_is_standard_library_only_and_has_no_private_path(self):
        source_path = ROOT / recovery.MODULE_RELATIVE_PATH
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertTrue(imports <= set(__import__("sys").stdlib_module_names))
        self.assertNotIn(".codex_work", source)
        self.assertNotIn("member_inventory.private", source)
        self.assertNotIn("marc2_freewill_private_selection as", source)

    def test_candidate_has_exact_ordered_top_level_fields_and_lane_id(self):
        self.assertEqual(tuple(self.record), recovery.EXPECTED_TOP_LEVEL_FIELDS)
        self.assertEqual(len(self.record), 15)
        self.assertEqual(self.record["lane_id"], "MARC2-FW1B")
        self.assertEqual(
            self.record["implementation_id"],
            "MARC-2-FW1B-proof-record-recovery-implementation-v0",
        )

    def test_strict_parser_rejects_encoding_duplicates_nonfinite_and_roots(self):
        cases = (
            b"\xef\xbb\xbf{}",
            b'{"value":"bad\x00value"}',
            b'{"value":1,"value":2}',
            b'{"value":NaN}',
            b"[]",
            b"{} trailing",
            b"\xff",
        )
        for payload in cases:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(
                    recovery.ProofRecordRefusal,
                    "MARC2FWR-F01",
                ):
                    recovery.parse_record_bytes(payload)

    def test_canonical_record_validates_with_complete_summary(self):
        summary = self.validate()
        self.assertEqual(summary.lane_id, recovery.LANE_ID)
        self.assertEqual(summary.top_level_field_count, 15)
        self.assertEqual(summary.tracked_binding_count, 4)
        self.assertEqual(summary.validator_module, recovery.MODULE_NAME)
        self.assertEqual(
            summary.validator_symbol,
            recovery.validate_implementation_record.__name__,
        )
        self.assertEqual(summary.record_sha256, self.proof.implementation_registry_sha256)

    def test_canonical_replay_is_byte_identical(self):
        first = self.validate()
        second = self.validate()
        self.assertEqual(
            recovery._canonical_json_bytes(first.to_mapping()),
            recovery._canonical_json_bytes(second.to_mapping()),
        )

    def test_all_32_ordered_mutations_refuse_on_exact_routes(self):
        routes = recovery.run_generated_mutation_matrix(
            self.record,
            repo_root=ROOT,
        )
        self.assertEqual(tuple(routes), recovery.ORDERED_MUTATIONS)
        self.assertEqual(routes, self.contract["mutation_routes"])
        self.assertEqual(len(routes), 32)

    def test_expected_and_observed_proof_are_separate(self):
        observed = replace(self.proof, observed_HEAD="b" * 40)
        with self.assertRaisesRegex(
            recovery.ProofRecordRefusal,
            "MARC2FWR-F02",
        ):
            recovery.validate_implementation_record(
                self.record_bytes,
                repo_root=ROOT,
                expected_proof=self.proof,
                observed_proof=observed,
            )
        observed = replace(self.proof, implementation_CI_run_id=99)
        with self.assertRaisesRegex(
            recovery.ProofRecordRefusal,
            "MARC2FWR-F02",
        ):
            recovery.validate_implementation_record(
                self.record_bytes,
                repo_root=ROOT,
                expected_proof=self.proof,
                observed_proof=observed,
            )

    def test_record_hash_must_match_observed_proof(self):
        observed = replace(
            self.proof,
            implementation_registry_sha256="b" * 64,
        )
        with self.assertRaisesRegex(
            recovery.ProofRecordRefusal,
            "MARC2FWR-F02",
        ):
            recovery.validate_implementation_record(
                self.record_bytes,
                repo_root=ROOT,
                expected_proof=observed,
                observed_proof=observed,
            )

    def test_generated_closure_must_be_exact_public_validator(self):
        with self.assertRaisesRegex(
            recovery.ProofRecordRefusal,
            "MARC2FWR-F05",
        ):
            recovery.validate_implementation_record(
                self.record_bytes,
                repo_root=ROOT,
                expected_proof=self.proof,
                observed_proof=self.proof,
                generated_closure=lambda: None,
            )

    def test_registry_self_binding_is_forbidden(self):
        record = copy.deepcopy(self.record)
        record["tracked_file_hashes"][0][
            "path"
        ] = recovery.IMPLEMENTATION_REGISTRY_RELATIVE_PATH.as_posix()
        with self.assertRaisesRegex(
            recovery.ProofRecordRefusal,
            "MARC2FWR-F01",
        ):
            self.validate(record)

    def test_all_bound_artifacts_are_regular_and_hash_exact(self):
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertFalse(path.is_symlink())
                self.assertEqual(recovery._sha256_file(path), binding["sha256"])

    def test_execution_authority_and_access_state_is_all_zero(self):
        self.assertEqual(
            self.record["execution_state"],
            recovery.EXPECTED_EXECUTION_STATE,
        )
        self.assertTrue(
            all(value is False for value in self.record["authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))
        self.assertFalse(self.record["next_gate"]["private_access_authorized_now"])
        self.assertFalse(self.record["next_gate"]["MARC2_FW2_eligible_now"])

    def test_full_qualification_passes_replay_mutations_caps_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "qualification"
            outcome = self.qualify(output)
            self.assertFalse(output.exists())
        self.assertEqual(outcome.report["route"], recovery.GENERATED_ROUTE)
        self.assertEqual(len(outcome.mutation_routes), 32)
        self.assertTrue(all(outcome.report["acceptance_gates"].values()))
        self.assertTrue(outcome.output_removed)
        self.assertLess(outcome.generated_input_bytes, 1024**2)
        self.assertLess(outcome.generated_output_bytes, 1024**2)
        self.assertLess(outcome.runtime_seconds, 30)
        self.assertEqual(outcome.peak_rss_bytes, 32 * 1024**2)

    def test_qualification_report_is_public_aggregate_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            outcome = self.qualify(Path(temporary) / "qualification")
        report = outcome.report
        self.assertEqual(set(report), recovery.PUBLIC_REPORT_FIELDS)
        self.assertEqual(report["candidate_summary"]["top_level_fields"], 15)
        self.assertTrue(report["candidate_summary"]["lane_id_present_and_exact"])
        self.assertFalse(report["candidate_summary"]["registry_self_binding"])
        self.assertEqual(report["candidate_summary"]["private_execution_limit"], 0)
        self.assertEqual(report["shared_validator"]["total_calls"], 34)
        self.assertTrue(all(value == 0 for value in report["access_counters"].values()))

    def test_report_roundtrip_inspection_and_filename_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outcome = self.qualify(root / "qualification")
            report_path = root / recovery.REPORT_NAME
            report_path.write_bytes(outcome.report_bytes)
            inspected = recovery.inspect_qualification_report(report_path)
            self.assertEqual(inspected, outcome.report)
            wrong = root / "wrong.json"
            wrong.write_bytes(outcome.report_bytes)
            with self.assertRaisesRegex(
                recovery.ProofRecordRefusal,
                "MARC2FWR-F03",
            ):
                recovery.inspect_qualification_report(wrong)

    def test_existing_output_refuses_without_deleting_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "existing"
            output.mkdir()
            marker = output / "user-file"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(
                recovery.ProofRecordRefusal,
                "MARC2FWR-F03",
            ):
                self.qualify(output)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")

    def test_peak_rss_cap_refuses_before_output_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "qualification"
            with self.assertRaisesRegex(
                recovery.ProofRecordRefusal,
                "MARC2FWR-F03",
            ):
                recovery.qualify_generated_proof_record(
                    output,
                    repo_root=ROOT,
                    peak_rss_reader=lambda: recovery.MAX_PEAK_RSS_BYTES + 1,
                )
            self.assertFalse(output.exists())

    def test_claim_boundary_is_explicitly_non_scientific(self):
        boundary = self.record["claim_boundary"]
        self.assertIn(
            "shared implementation-record validator",
            boundary["engineering_capability_added"],
        )
        self.assertIn("no human neural data", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])

    def test_cli_plan_and_qualify_are_bounded_and_cleanup(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = recovery.main(["plan", "--repo-root", str(ROOT)])
        self.assertEqual(code, 0)
        plan = json.loads(stdout.getvalue())
        self.assertEqual(plan["registered_private_execution_limit"], 0)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "qualification"
            stdout = io.StringIO()
            with mock.patch.object(
                recovery,
                "_peak_rss_bytes",
                return_value=32 * 1024**2,
            ), redirect_stdout(stdout):
                code = recovery.main(
                    [
                        "qualify",
                        "--repo-root",
                        str(ROOT),
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["route"], recovery.GENERATED_ROUTE)
            self.assertEqual(result["mutations_passed"], 32)
            self.assertTrue(result["output_removed"])
            self.assertFalse(output.exists())

    def test_cli_refusal_is_aggregate_and_returns_two(self):
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "existing"
            output.mkdir()
            with redirect_stderr(stderr):
                code = recovery.main(
                    [
                        "qualify",
                        "--repo-root",
                        str(ROOT),
                        "--output",
                        str(output),
                    ]
                )
        self.assertEqual(code, 2)
        self.assertIn("MARC2FWR-F03", stderr.getvalue())
        self.assertNotIn(str(ROOT), stderr.getvalue())

    def test_parser_has_no_execute_subcommand(self):
        parser = recovery._build_parser()
        help_text = parser.format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertIn("inspect", help_text)
        self.assertNotIn("execute", help_text)


if __name__ == "__main__":
    unittest.main()
