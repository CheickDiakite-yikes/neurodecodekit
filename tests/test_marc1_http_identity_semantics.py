from __future__ import annotations

import copy
import json
import os
import stat
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from neurodecodekit.datasets import marc1_http_identity_semantics as semantics
from neurodecodekit.datasets import marc1_pilot_selection as selector


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


class MARC1HTTPIdentitySemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wrist = selector.build_generated_wrist_metadata()
        cls.body = semantics._canonical_json_bytes(cls.wrist)

    def qualify(self, output: Path):
        ticks = iter((100.0, 100.125))
        return semantics.qualify_generated_identity_semantics(
            output,
            repo_root=ROOT,
            clock=lambda: next(ticks),
            rss_reader=lambda: 24 * 1024**2,
        )

    def test_contract_loads_only_after_exact_green_proof(self) -> None:
        contract = semantics.load_registered_contract(ROOT)
        self.assertEqual(contract["acceptance_route"], "MARC1HT-G1")
        self.assertTrue(contract["green_research_anchor"]["both_required_jobs_green"])

    def test_all_four_uncoded_forms_are_accepted(self) -> None:
        hashes = set()
        states = set()
        for name in semantics.ACCEPTED_CASES:
            with self.subTest(name=name):
                rows, transport = semantics.validate_mock_terminal_response(
                    semantics._response_for_case(self.body, name)
                )
                self.assertEqual(len(rows), 55)
                hashes.add(transport["body_sha256"])
                states.add(transport["content_encoding_state"])
                self.assertEqual(transport["decompression_or_decoding_operations"], 0)
        self.assertEqual(len(hashes), 1)
        self.assertEqual(states, {"absent", "identity"})

    def test_content_encoding_value_refusals_route_to_f02(self) -> None:
        for value in ("", "   ", "gzip", "br", "deflate", "compress", "x", "identity,gzip"):
            with self.subTest(value=value):
                response = semantics._replace_header(
                    semantics._response_for_case(
                        self.body,
                        "Content_Encoding_absent",
                    ),
                    "Content-Encoding",
                    value,
                )
                with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F02"):
                    semantics.validate_mock_terminal_response(response)

    def test_duplicate_content_encoding_refuses(self) -> None:
        response = semantics._response_for_case(
            self.body,
            "Content_Encoding_identity_lowercase",
            row_headers=(("Content-Encoding", "identity"),),
        )
        with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F02"):
            semantics.validate_mock_terminal_response(response)

    def test_unchanged_envelope_refusals_remain_strict(self) -> None:
        base = semantics._response_for_case(self.body, "Content_Encoding_absent")
        mutations = (
            semantics._replace_header(base, "Transfer-Encoding", "chunked"),
            semantics._replace_header(base, "Content-Type", "text/plain"),
            semantics._replace_header(base, "Content-Length", "bad"),
            semantics.MockResponse(200, "https://changed.invalid", base.headers, base.body),
        )
        for response in mutations:
            with self.subTest(response=response):
                with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F03"):
                    semantics.validate_mock_terminal_response(response)

    def test_content_length_requires_ASCII_digits(self) -> None:
        response = semantics._replace_header(
            semantics._response_for_case(self.body, "Content_Encoding_absent"),
            "Content-Length",
            "\N{ARABIC-INDIC DIGIT ONE}\N{ARABIC-INDIC DIGIT TWO}"
            "\N{ARABIC-INDIC DIGIT THREE}",
        )
        with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F03"):
            semantics.validate_mock_terminal_response(response)

    def test_private_redirect_address_refuses_without_DNS(self) -> None:
        with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F03"):
            semantics.validate_mock_redirect_target(
                "https://private.generated.invalid/files",
                ("127.0.0.1",),
            )

    def test_target_like_field_refuses_before_selection(self) -> None:
        rows = copy.deepcopy(self.wrist)
        rows[0]["target"] = "forbidden"
        body = semantics._canonical_json_bytes(rows)
        with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F03"):
            semantics.validate_mock_terminal_response(
                semantics._response_for_case(body, "Content_Encoding_absent")
            )

    def test_exact_twenty_mutations_refuse_under_frozen_routes(self) -> None:
        base = semantics._response_for_case(self.body, "Content_Encoding_absent")
        with tempfile.TemporaryDirectory() as temporary:
            existing = Path(temporary) / "existing"
            existing.mkdir()
            routes = semantics.run_refusal_matrix(base, existing)
        self.assertEqual(tuple(routes), semantics.REFUSAL_CASES)
        self.assertEqual(len(routes), 20)
        self.assertEqual(set(routes.values()), set(semantics.FAILURE_ROUTES) - {"MARC1HT-F01"})

    def test_source_surface_has_no_network_decoder_or_execute(self) -> None:
        surface = semantics.inspect_source_surface()
        self.assertEqual(surface["network_client_imports"], 0)
        self.assertEqual(surface["DNS_resolver_imports"], 0)
        self.assertEqual(surface["decompressor_or_decoder_imports"], 0)
        self.assertEqual(surface["execute_functions"], 0)
        self.assertEqual(surface["allowed_commands"], ["plan", "qualify", "inspect"])

    def test_source_surface_refuses_network_or_new_command(self) -> None:
        source = """\
import urllib.request

def execute():
    return urllib.request.urlopen('https://generated.invalid')
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "forbidden.py"
            path.write_text(source, encoding="utf-8")
            with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F05"):
                semantics.inspect_source_surface(path)

    def test_generated_qualification_roundtrip_is_bounded_and_private(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
                outcome = self.qualify(output)
            report = semantics.inspect_generated_report(outcome.report_path)
            self.assertEqual(report["route"], "MARC1HT-G1")
            self.assertTrue(all(report["acceptance_gates"].values()))
            self.assertEqual(report["accepted_response_summary"]["passed_count"], 4)
            self.assertEqual(report["refusal_summary"]["passed_count"], 20)
            self.assertEqual(report["cohort_summary"]["selected_subjects_per_axis"], 12)
            self.assertEqual(report["split_summary"]["freewill_selected_core_members"], 288)
            self.assertLess(outcome.generated_input_bytes, 2 * 1024**2)
            self.assertLess(outcome.generated_output_bytes, 2 * 1024**2)
            self.assertEqual(
                report["measurements"]["public_output_bytes"],
                outcome.report_path.stat().st_size,
            )
            self.assertEqual(
                report["measurements"]["private_output_bytes"],
                outcome.private_manifest_path.stat().st_size,
            )
            self.assertEqual(
                report["measurements"]["combined_output_bytes"],
                outcome.generated_output_bytes,
            )
            self.assertEqual(
                report["measurements"]["incremental_disk_bytes"],
                outcome.generated_output_bytes,
            )
            self.assertEqual(stat.S_IMODE(outcome.private_manifest_path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(outcome.report_path.stat().st_mode), 0o644)
            with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F05"):
                semantics.qualify_generated_identity_semantics(output, repo_root=ROOT)

    def test_generated_selection_is_deterministic_across_two_development_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = self.qualify(Path(temporary) / "first")
            second = self.qualify(Path(temporary) / "second")
            self.assertEqual(first.report["selection_hashes"], second.report["selection_hashes"])
            self.assertEqual(
                first.private_manifest_path.read_bytes(),
                second.private_manifest_path.read_bytes(),
            )

    def test_fixed_measurements_replay_both_outputs_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, THREAD_ENV, clear=True):
                first = self.qualify(Path(temporary) / "first")
                second = self.qualify(Path(temporary) / "second")
            self.assertEqual(first.report_path.read_bytes(), second.report_path.read_bytes())
            self.assertEqual(
                first.private_manifest_path.read_bytes(),
                second.private_manifest_path.read_bytes(),
            )

    def test_thread_cap_and_tampered_report_refuse(self) -> None:
        with mock.patch.dict(
            os.environ,
            {**THREAD_ENV, "OPENBLAS_NUM_THREADS": "2"},
            clear=True,
        ):
            with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F04"):
                semantics._assert_resources(0.1, 1024, 1024)
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, THREAD_ENV, clear=True):
                outcome = self.qualify(Path(temporary) / "out")
            report = json.loads(outcome.report_path.read_text(encoding="utf-8"))
            report["unregistered_field"] = True
            outcome.report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F04"):
                semantics.inspect_generated_report(outcome.report_path)

    def test_private_report_cannot_be_inspected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "private.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(semantics.HTTPIdentityRefusal, "MARC1HT-F04"):
                semantics.inspect_generated_report(path)

    def test_plan_and_parser_have_no_execute_command(self) -> None:
        plan = semantics.registered_plan(ROOT)
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect"])
        parser = semantics._build_parser()
        help_text = parser.format_help()
        self.assertNotIn("execute", help_text)
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["real_or_private_input_bytes"], 0)

    def test_public_claim_boundary_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outcome = self.qualify(Path(temporary) / "out")
            claim = outcome.report["claim_boundary"]
            self.assertIn("generated harness", claim["engineering_capability_added"])
            self.assertIn("thought-to-text", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
