from __future__ import annotations

import copy
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc1_versioned_pagination as pagination


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


class MARC1VersionedPaginationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = pagination.canonical_request()
        cls.rows = pagination.build_generated_wrist_rows()
        cls.response = pagination._response_for_case(
            cls.rows,
            pagination.ACCEPTED_CASES[0],
        )

    def qualify(self, output: Path):
        ticks = iter((100.0, 100.25))
        return pagination.qualify_generated_pagination(
            output,
            repo_root=ROOT,
            clock=lambda: next(ticks),
            rss_reader=lambda: 24 * 1024**2,
        )

    def test_contract_loads_only_after_exact_green_proof(self) -> None:
        contract = pagination.load_registered_contract(ROOT)
        self.assertEqual(contract["acceptance_route"], "MARC1PG-G1")
        self.assertTrue(contract["green_research_anchor"]["both_required_jobs_green"])

    def test_request_serialization_is_exact_and_target_free(self) -> None:
        summary = pagination.validate_mock_request(self.request)
        self.assertEqual(summary["query"], "page=1&page_size=1000")
        self.assertEqual((summary["page"], summary["page_size"]), (1, 1000))
        self.assertEqual(summary["response_body_count"], 1)
        self.assertEqual(summary["second_page_requests"], 0)
        self.assertEqual(summary["fallback_requests"], 0)
        self.assertEqual(len(summary["request_sha256"]), 64)

    def test_query_mutations_refuse_before_any_response(self) -> None:
        for query in (
            "",
            "page_size=1000",
            "page=1",
            "page=0&page_size=1000",
            "page=one&page_size=1000",
            "page=1&page_size=10",
            "page=1&page_size=1001",
            "page_size=1000&page=1",
            "page=1&page=1&page_size=1000",
            "page=1&page_size=1000&limit=55&offset=0",
        ):
            with self.subTest(query=query):
                changed = pagination._replace_request(self.request, query=query)
                with self.assertRaisesRegex(
                    pagination.PaginationRefusal,
                    "MARC1PG-F01",
                ):
                    pagination.validate_mock_request(changed)

    def test_all_accepted_cases_have_one_semantic_identity(self) -> None:
        hashes = set()
        states = set()
        for name in pagination.ACCEPTED_CASES:
            with self.subTest(name=name):
                rows, transport = pagination.parse_mock_response(
                    pagination._response_for_case(self.rows, name)
                )
                identity = pagination.validate_wrist_rows(rows)
                hashes.add(identity["canonical_source_sha256"])
                states.add(transport["content_encoding_state"])
                self.assertEqual(transport["decompression_or_decoding_operations"], 0)
        self.assertEqual(len(hashes), 1)
        self.assertEqual(states, {"absent", "identity"})

    def test_transport_envelope_refusals_route_to_f02(self) -> None:
        mutations = (
            pagination._replace_response(self.response, status=206),
            pagination._replace_response(self.response, redirect_count=1),
            pagination._replace_header(self.response, "Content-Encoding", "gzip"),
            pagination._replace_header(self.response, "Transfer-Encoding", "chunked"),
            pagination._replace_header(self.response, "Content-Type", "text/plain"),
            pagination._replace_header(self.response, "Content-Length", "bad"),
            pagination._replace_header(self.response, "Content-Length", "1"),
        )
        for response in mutations:
            with self.subTest(response=response):
                with self.assertRaisesRegex(
                    pagination.PaginationRefusal,
                    "MARC1PG-F02",
                ):
                    pagination.parse_mock_response(response)

    def test_strict_json_root_and_row_refusals_route_to_f03(self) -> None:
        payloads = (b"[", b'{"x":1}', b'[{"id":1,"id":2}]', b"[1]")
        for payload in payloads:
            response = pagination._replace_response(
                self.response,
                headers=(("Content-Type", "application/json"),),
                body=payload,
            )
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(
                    pagination.PaginationRefusal,
                    "MARC1PG-F03",
                ):
                    pagination.parse_mock_response(response)

    def test_target_like_extra_field_refuses_at_f06(self) -> None:
        rows = copy.deepcopy(self.rows)
        rows[0]["target"] = "forbidden"
        response = pagination._response_for_case(rows, pagination.ACCEPTED_CASES[0])
        with self.assertRaisesRegex(pagination.PaginationRefusal, "MARC1PG-F06"):
            pagination.parse_mock_response(response)

    def test_partial_default_and_off_by_one_pages_refuse_at_f04(self) -> None:
        for count in (10, 54, 56):
            rows = copy.deepcopy(self.rows[:count])
            if count == 56:
                rows = copy.deepcopy(self.rows)
                extra = copy.deepcopy(rows[-1])
                extra["id"] = 80_000_000
                extra["name"] = "extra.txt"
                extra["download_url"] = (
                    "https://ndownloader.figshare.com/files/80000000"
                )
                rows.append(extra)
            with self.subTest(count=count):
                with self.assertRaisesRegex(
                    pagination.PaginationRefusal,
                    "MARC1PG-F04",
                ):
                    pagination.validate_wrist_rows(rows)

    def test_semantic_anchor_url_md5_and_total_refuse_at_f05(self) -> None:
        mutations = []
        wrong_url = copy.deepcopy(self.rows)
        wrong_url[0]["download_url"] = "https://generated.invalid/wrong"
        mutations.append(wrong_url)
        wrong_md5 = copy.deepcopy(self.rows)
        wrong_md5[0]["supplied_md5"] = "0" * 32
        mutations.append(wrong_md5)
        wrong_anchor = copy.deepcopy(self.rows)
        wrong_anchor[0]["size"] += 1
        wrong_anchor[-1]["size"] -= 1
        mutations.append(wrong_anchor)
        wrong_total = copy.deepcopy(self.rows)
        wrong_total[-1]["size"] += 1
        mutations.append(wrong_total)
        for rows in mutations:
            with self.subTest(rows=rows[0]):
                with self.assertRaisesRegex(
                    pagination.PaginationRefusal,
                    "MARC1PG-F05",
                ):
                    pagination.validate_wrist_rows(rows)

    def test_all_41_mutations_refuse_and_cover_all_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            existing = Path(temporary) / "existing"
            existing.mkdir()
            routes = pagination.run_refusal_matrix(
                self.request,
                self.response,
                self.rows,
                existing,
            )
        self.assertEqual(tuple(routes), pagination.REFUSAL_CASES)
        self.assertEqual(len(routes), 41)
        self.assertEqual(set(routes.values()), set(pagination.FAILURE_ROUTES))

    def test_source_surface_has_no_live_or_execute_capability(self) -> None:
        surface = pagination.inspect_source_surface()
        self.assertEqual(surface["network_client_imports"], 0)
        self.assertEqual(surface["DNS_or_transport_calls"], 0)
        self.assertEqual(surface["execute_functions"], 0)
        self.assertEqual(surface["execute_commands"], 0)
        self.assertEqual(surface["allowed_commands"], ["inspect", "plan", "qualify"])

    def test_source_surface_refuses_a_network_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "forbidden.py"
            path.write_text("import socket\n", encoding="utf-8")
            with self.assertRaisesRegex(
                pagination.PaginationRefusal,
                "MARC1PG-F06",
            ):
                pagination.inspect_source_surface(path)

    def test_generated_roundtrip_is_bounded_private_and_inspectable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            with mock.patch.dict(os.environ, THREAD_ENV, clear=True):
                outcome = self.qualify(output)
            report = pagination.inspect_generated_report(outcome.report_path)
            self.assertEqual(report["route"], "MARC1PG-G1")
            self.assertTrue(all(report["acceptance_gates"].values()))
            self.assertEqual(report["response_summary"]["accepted_cases_passed"], 4)
            self.assertEqual(report["refusal_summary"]["passed_count"], 41)
            self.assertEqual(report["inventory_summary"]["file_rows"], 55)
            self.assertEqual(report["cohort_summary"]["selected_subjects_per_axis"], 12)
            self.assertLess(outcome.generated_input_bytes, 2 * 1024**2)
            self.assertLess(outcome.generated_output_bytes, 2 * 1024**2)
            self.assertEqual(
                stat.S_IMODE(outcome.private_manifest_path.stat().st_mode),
                0o600,
            )
            self.assertEqual(stat.S_IMODE(outcome.report_path.stat().st_mode), 0o644)

    def test_selection_and_private_output_replay_across_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, THREAD_ENV, clear=True):
                first = self.qualify(Path(temporary) / "first")
                second = self.qualify(Path(temporary) / "second")
            self.assertEqual(first.report["selection_hashes"], second.report["selection_hashes"])
            self.assertEqual(
                first.private_manifest_path.read_bytes(),
                second.private_manifest_path.read_bytes(),
            )

    def test_fixed_measurements_replay_public_output_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, THREAD_ENV, clear=True):
                first = self.qualify(Path(temporary) / "first")
                second = self.qualify(Path(temporary) / "second")
            self.assertEqual(first.report_path.read_bytes(), second.report_path.read_bytes())

    def test_thread_cap_existing_output_and_tampered_report_refuse(self) -> None:
        with mock.patch.dict(
            os.environ,
            {**THREAD_ENV, "OPENBLAS_NUM_THREADS": "2"},
            clear=True,
        ):
            with self.assertRaisesRegex(
                pagination.PaginationRefusal,
                "MARC1PG-F07",
            ):
                pagination._assert_resources(0.1, 1024, 1024, 1024)
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, THREAD_ENV, clear=True):
                outcome = self.qualify(Path(temporary) / "out")
            with self.assertRaisesRegex(
                pagination.PaginationRefusal,
                "MARC1PG-F07",
            ):
                self.qualify(Path(temporary) / "out")
            report = json.loads(outcome.report_path.read_text(encoding="utf-8"))
            report["unregistered_field"] = True
            outcome.report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                pagination.PaginationRefusal,
                "MARC1PG-F07",
            ):
                pagination.inspect_generated_report(outcome.report_path)

    def test_private_output_cannot_be_used_as_public_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / pagination.PRIVATE_NAME
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(
                pagination.PaginationRefusal,
                "MARC1PG-F07",
            ):
                pagination.inspect_generated_report(path)

    def test_plan_cli_and_claim_boundary_remain_closed(self) -> None:
        plan = pagination.registered_plan(ROOT)
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect"])
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["real_or_private_input_bytes"], 0)
        self.assertNotIn("execute", pagination._build_parser().format_help())
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, THREAD_ENV, clear=True):
                outcome = self.qualify(Path(temporary) / "out")
            claim = outcome.report["claim_boundary"]
            self.assertIn("generated harness", claim["engineering_capability_added"])
            self.assertIn("thought-to-text", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
