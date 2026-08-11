import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import iackd_transport_stable as transport
from neurodecodekit.datasets.iackd_transport_stable import (
    AuditedResponse,
    GeneratedResponse,
    REFUSAL_IDS,
    ResponseSpec,
    TransportStableRefusal,
    assert_generated_source,
    load_qualification_report,
    registered_plan,
    response_spec_from_mapping,
    run_acceptance_matrix,
    run_refusal_matrix,
    run_synthetic_qualification,
    summarize_qualification,
    validate_and_parse_response,
    validate_qualification_report,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


def _body(case: str = "unit") -> bytes:
    return transport._fixture_body(case)


def _spec(body: bytes, *, etag: str | None = None) -> ResponseSpec:
    return ResponseSpec(
        "fixture://iackd-t1/unit",
        len(body),
        transport._sha256_bytes(body),
        etag,
    )


def _validate(
    body: bytes,
    *,
    headers=None,
    spec=None,
    mode="metadata",
    parser=transport._fixture_parser,
):
    chosen = _spec(body) if spec is None else spec
    response = GeneratedResponse(body, url=chosen.url, headers=headers)
    return validate_and_parse_response(
        AuditedResponse(response),
        spec=chosen,
        mode=mode,
        parser=parser,
    )


class IACKDTransportStableCoreTests(unittest.TestCase):
    def test_contract_and_default_plan_are_zero_network(self):
        contract = transport.load_registered_contract(ROOT)
        self.assertEqual(
            contract["contract_id"],
            "IACKD-T1-transport-stable-recovery-contract-v0",
        )
        plan = registered_plan(ROOT)
        self.assertEqual(plan["lane"], "IACKD-T1")
        self.assertEqual(plan["accepted_metadata_framing_profiles"], ["fixed_length", "chunked", "close_delimited"])
        self.assertEqual(plan["metadata_documents"], 4)
        self.assertEqual(plan["metadata_registered_body_bytes"], 595400)
        self.assertEqual(plan["network_requests_made"], 0)
        self.assertEqual(plan["local_IACKD_path_operations"], 0)
        self.assertFalse(plan["real_executor_available"])
        self.assertFalse(plan["public_execution_authorized"])

    def test_response_spec_mapping_is_strict_and_fixture_only(self):
        body = _body()
        mapping = {
            "url": "fixture://iackd-t1/unit",
            "expected_bytes": len(body),
            "expected_sha256": transport._sha256_bytes(body),
            "expected_etag": None,
        }
        self.assertEqual(response_spec_from_mapping(mapping), _spec(body))
        for mutation in (
            {**mapping, "unknown": True},
            {key: value for key, value in mapping.items() if key != "expected_etag"},
            {**mapping, "url": "https://example.invalid/body"},
            {**mapping, "expected_bytes": True},
            {**mapping, "expected_sha256": "bad"},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises(TransportStableRefusal):
                    response_spec_from_mapping(mutation)

    def test_acceptance_matrix_covers_three_metadata_profiles_and_payload(self):
        result = run_acceptance_matrix()
        rows = {row["case"]: row for row in result["cases"]}
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows["fixed_length_exact"]["framing_profile"], "fixed_length")
        self.assertEqual(rows["fixed_length_exact"]["content_length_state"], "exact")
        self.assertEqual(rows["fixed_length_valid_different"]["content_length_state"], "different")
        self.assertEqual(rows["chunked"]["framing_profile"], "chunked")
        self.assertEqual(rows["close_delimited"]["framing_profile"], "close_delimited")
        self.assertEqual(rows["payload_fixed_length_exact"]["mode"], "payload")
        self.assertEqual(rows["payload_fixed_length_exact"]["etag_state"], "exact")
        self.assertTrue(transport._is_hex64(result["canonical_sha256"]))
        self.assertTrue(all((row["read_calls"], row["hash_calls"], row["parse_calls"]) == (1, 1, 1) for row in rows.values()))

    def test_valid_different_metadata_length_is_advisory_only(self):
        body = _body()
        validation, parsed = _validate(
            body,
            headers={"Content-Length": str(len(body) + 1)},
        )
        self.assertEqual(validation.content_length_state, "different")
        self.assertEqual(validation.observed_bytes, len(body))
        self.assertEqual(validation.body_sha256, transport._sha256_bytes(body))
        self.assertEqual(
            validation.warnings,
            ("metadata_Content_Length_differs_content_identity_passed",),
        )
        self.assertEqual(parsed["fixture"], "iackd-t1-generated-transport")

    def test_absent_length_accepts_chunked_or_clean_close_only(self):
        body = _body()
        chunked, _ = _validate(body, headers={"transfer-encoding": "chunked"})
        closed, _ = _validate(body)
        identity, _ = _validate(body, headers={"Content-Encoding": "Identity"})
        self.assertEqual(chunked.framing_profile, "chunked")
        self.assertEqual(closed.framing_profile, "close_delimited")
        self.assertEqual(identity.framing_profile, "close_delimited")
        self.assertEqual(chunked.content_length_state, "unavailable")
        self.assertIn("unavailable", closed.warnings[0])

    def test_ambiguous_and_malformed_framing_refuses_before_read(self):
        body = _body()
        cases = (
            {"Content-Length": str(len(body)), "Transfer-Encoding": "chunked"},
            {"Content-Length": " 1"},
            {"Content-Length": "+1"},
            {"Content-Length": "1, 1"},
            {"Transfer-Encoding": "gzip"},
            {"Transfer-Encoding": " chunked"},
        )
        for headers in cases:
            with self.subTest(headers=headers):
                audited = AuditedResponse(GeneratedResponse(body, url=_spec(body).url, headers=headers))
                with self.assertRaises(TransportStableRefusal) as failure:
                    validate_and_parse_response(
                        audited,
                        spec=_spec(body),
                        mode="metadata",
                        parser=transport._fixture_parser,
                    )
                self.assertEqual(failure.exception.refusal_id, REFUSAL_IDS[3])
                self.assertEqual(audited.read_calls, 0)
                self.assertEqual(audited.hash_calls, 0)
                self.assertEqual(audited.parse_calls, 0)

    def test_underflow_overflow_hash_and_parser_fail_closed(self):
        body = _body()
        for candidate in (body[:-1], body + b"x"):
            with self.subTest(length=len(candidate)):
                with self.assertRaises(TransportStableRefusal) as failure:
                    _validate(candidate, spec=_spec(body))
                self.assertEqual(failure.exception.refusal_id, REFUSAL_IDS[6])

        wrong = ResponseSpec(_spec(body).url, len(body), "0" * 64)
        with self.assertRaises(TransportStableRefusal) as hashed:
            _validate(body, spec=wrong)
        self.assertEqual(hashed.exception.refusal_id, REFUSAL_IDS[7])

        with self.assertRaises(TransportStableRefusal) as parsed:
            _validate(body, parser=lambda _: (_ for _ in ()).throw(ValueError("generated")))
        self.assertEqual(parsed.exception.refusal_id, REFUSAL_IDS[10])

    def test_payload_mode_keeps_exact_length_and_etag(self):
        body = _body()
        expected = _spec(body, etag="fixture-etag-001")
        accepted, _ = _validate(
            body,
            spec=expected,
            mode="payload",
            headers={
                "Content-Length": str(len(body)),
                "ETag": '"fixture-etag-001"',
            },
        )
        self.assertEqual(accepted.etag_state, "exact")
        cases = (
            {},
            {"Content-Length": str(len(body) + 1), "ETag": '"fixture-etag-001"'},
            {"Content-Length": str(len(body))},
            {"Content-Length": str(len(body)), "ETag": '"different"'},
            {"Content-Length": str(len(body)), "ETag": 'W/"fixture-etag-001"'},
            {"Transfer-Encoding": "chunked", "ETag": '"fixture-etag-001"'},
        )
        for headers in cases:
            with self.subTest(headers=headers):
                with self.assertRaises(TransportStableRefusal):
                    _validate(body, spec=expected, mode="payload", headers=headers)

    def test_one_use_wrapper_refuses_reuse_and_bad_order(self):
        body = _body()
        audited = AuditedResponse(GeneratedResponse(body, url=_spec(body).url))
        validate_and_parse_response(
            audited,
            spec=_spec(body),
            mode="metadata",
            parser=transport._fixture_parser,
        )
        with self.assertRaises(TransportStableRefusal) as reused:
            validate_and_parse_response(
                audited,
                spec=_spec(body),
                mode="metadata",
                parser=transport._fixture_parser,
            )
        self.assertEqual(reused.exception.refusal_id, REFUSAL_IDS[9])

        fresh = AuditedResponse(GeneratedResponse(body, url=_spec(body).url))
        with self.assertRaises(TransportStableRefusal):
            fresh.hash_once(body)
        with self.assertRaises(TransportStableRefusal):
            fresh.parse_once(transport._fixture_parser, body)

    def test_refusal_matrix_matches_all_twenty_two_registered_mutations(self):
        rows = run_refusal_matrix()
        self.assertEqual(len(rows), 22)
        self.assertEqual(len({row["mutation"] for row in rows}), 22)
        self.assertEqual(
            {row["mutation"] for row in rows},
            set(transport.load_registered_contract(ROOT)["fixture_qualification_contract"]["required_refusals"]),
        )
        self.assertTrue(all(row["refusal_id"] in REFUSAL_IDS for row in rows))

    def test_generated_source_firewall_and_forbidden_fixture_terms(self):
        assert_generated_source("generated")
        for source in ("public_url", "real_path", "retained_bundle"):
            with self.subTest(source=source):
                with self.assertRaises(TransportStableRefusal) as failure:
                    assert_generated_source(source)
                self.assertEqual(failure.exception.refusal_id, REFUSAL_IDS[13])
        for term in transport.FORBIDDEN_GENERATED_TERMS:
            with self.subTest(term=term):
                with self.assertRaises(TransportStableRefusal):
                    transport._fixture_body(term)


class IACKDTransportStableQualificationTests(unittest.TestCase):
    @staticmethod
    def _clock():
        values = iter((0.0, 0.125))
        return lambda: next(values)

    def run_qualification(self, output, **kwargs):
        return run_synthetic_qualification(
            output,
            repo_root=ROOT,
            environ=THREAD_ENV,
            clock=self._clock(),
            rss_reader=lambda: 32 * 1024 * 1024,
            **kwargs,
        )

    def test_bounded_roundtrip_summary_and_zero_access_counters(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            outcome = self.run_qualification(output)
            loaded = load_qualification_report(output)
            summary = summarize_qualification(loaded)
        self.assertEqual(outcome.report, loaded)
        self.assertEqual(summary["metadata_framing_profiles"], ["fixed_length", "chunked", "close_delimited"])
        self.assertEqual(summary["accepted_case_count_total"], 10)
        self.assertEqual(summary["refusal_mutation_count"], 22)
        self.assertEqual(summary["deterministic_replays"], 2)
        self.assertEqual(summary["runtime_seconds"], 0.125)
        self.assertEqual(summary["peak_RSS_bytes"], 32 * 1024 * 1024)
        self.assertLess(summary["generated_output_bytes"], 1024 * 1024)
        self.assertIsNone(summary["producer_is_causal"])
        self.assertFalse(summary["end_to_end_latency_measured"])
        self.assertTrue(all(value == 0 for value in loaded["access_counters"].values()))
        serialized = json.dumps(loaded)
        self.assertNotIn("https://", serialized)
        self.assertNotIn(str(ROOT), serialized)

    def test_fixed_monitors_produce_byte_identical_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            self.run_qualification(first)
            self.run_qualification(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_thread_runtime_rss_cap_collision_and_output_cap_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            wrong_env = dict(THREAD_ENV)
            wrong_env["OMP_NUM_THREADS"] = "2"
            with self.assertRaises(TransportStableRefusal) as thread:
                run_synthetic_qualification(output, repo_root=ROOT, environ=wrong_env)
            self.assertEqual(thread.exception.refusal_id, REFUSAL_IDS[12])

            with self.assertRaises(TransportStableRefusal) as runtime:
                run_synthetic_qualification(
                    output,
                    repo_root=ROOT,
                    environ=THREAD_ENV,
                    clock=(lambda values=iter((0.0, 31.0)): lambda: next(values))(),
                    rss_reader=lambda: 32 * 1024 * 1024,
                )
            self.assertEqual(runtime.exception.refusal_id, REFUSAL_IDS[12])

            with self.assertRaises(TransportStableRefusal) as rss:
                run_synthetic_qualification(
                    output,
                    repo_root=ROOT,
                    environ=THREAD_ENV,
                    clock=self._clock(),
                    rss_reader=lambda: 257 * 1024 * 1024,
                )
            self.assertEqual(rss.exception.refusal_id, REFUSAL_IDS[12])

            self.run_qualification(output)
            with self.assertRaises(TransportStableRefusal) as collision:
                self.run_qualification(output)
            self.assertEqual(collision.exception.refusal_id, REFUSAL_IDS[11])

            too_small = Path(directory) / "small.json"
            with self.assertRaises(TransportStableRefusal) as cap:
                self.run_qualification(too_small, maximum_output_bytes=128)
            self.assertEqual(cap.exception.refusal_id, REFUSAL_IDS[11])

    def test_report_mutations_and_symlink_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            report = dict(self.run_qualification(output).report)
            for mutate in (
                lambda row: row.update({"unknown": True}),
                lambda row: row["access_counters"].update({"network_bytes": 1}),
                lambda row: row["access_counters"].update({"unknown_counter": 0}),
                lambda row: row["fixture_qualification"].update({"refusal_mutation_count": 21}),
                lambda row: row["fixture_qualification"]["refusal_mutations"].reverse(),
                lambda row: row["measurements"].update({"CPU_threads": 2}),
                lambda row: row["measurements"].update({"generated_output_bytes": 1024 * 1024 + 1}),
                lambda row: row["green_registration"].update({"commit": "0" * 40}),
            ):
                with self.subTest(mutate=mutate):
                    candidate = copy.deepcopy(report)
                    mutate(candidate)
                    with self.assertRaises(TransportStableRefusal):
                        validate_qualification_report(candidate)

            link = Path(directory) / "link.json"
            link.symlink_to(output)
            with self.assertRaises(TransportStableRefusal) as symlink:
                load_qualification_report(link)
            self.assertEqual(symlink.exception.refusal_id, REFUSAL_IDS[11])

    def test_cli_help_default_fixture_and_inspect(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(transport.main([]), 0)
        default = stdout.getvalue()
        self.assertIn('"network_requests_made": 0', default)
        self.assertIn("Safety default", default)

        with self.assertRaises(SystemExit) as help_exit:
            with contextlib.redirect_stdout(io.StringIO()):
                transport.main(["--help"])
        self.assertEqual(help_exit.exception.code, 0)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification.json"
            prior = dict(os.environ)
            try:
                os.environ.update(THREAD_ENV)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(
                        transport.main(["--fixture", "--out", str(output)]),
                        0,
                    )
                with contextlib.redirect_stdout(io.StringIO()) as inspected:
                    self.assertEqual(transport.main(["--inspect", str(output)]), 0)
                self.assertIn('"refusal_mutation_count": 22', inspected.getvalue())
            finally:
                os.environ.clear()
                os.environ.update(prior)

    def test_module_has_no_public_executor_or_network_constructor(self):
        source = Path(transport.__file__).read_text(encoding="utf-8")
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn('add_argument("--execute"', source)
        self.assertNotIn("socket.", source)


if __name__ == "__main__":
    unittest.main()
