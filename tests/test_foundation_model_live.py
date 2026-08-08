import io
import copy
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from neurodecodekit.cli import main
from neurodecodekit.evaluation.foundation_model_bridge import write_bounded_json
from neurodecodekit.evaluation.foundation_model_live import (
    EXPECTED_ENDPOINT,
    EXPECTED_MODEL_ID,
    ExecutionEvidence,
    FoundationModelLiveFailure,
    build_live_context,
    dry_run_summary,
    execute_context_with_transport,
    inspect_live_result,
    validate_live_result,
)


def provider_response(
    *,
    decoded_text="SYNTHETIC",
    abstained=False,
    evidence_used="ctc",
    input_tokens=100,
    output_tokens=20,
    cached_tokens=0,
    cache_write_tokens=0,
    reasoning_tokens=4,
):
    output = {
        "decoded_text": decoded_text,
        "abstained": abstained,
        "evidence_used": evidence_used,
        "unsupported_content_warning": False,
    }
    payload = {
        "id": "must-not-be-retained",
        "status": "completed",
        "model": EXPECTED_MODEL_ID,
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(output, sort_keys=True),
                    }
                ],
            }
        ],
        "usage": {
            "input_tokens": input_tokens,
            "input_tokens_details": {
                "cached_tokens": cached_tokens,
                "cache_write_tokens": cache_write_tokens,
            },
            "output_tokens": output_tokens,
            "output_tokens_details": {"reasoning_tokens": reasoning_tokens},
        },
    }
    return json.dumps(payload, sort_keys=True).encode("utf-8")


class FoundationModelLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = build_live_context()
        cls.evidence = ExecutionEvidence(
            implementation_commit="a" * 40,
            implementation_push_ci_run_id=123,
        )

    def setUp(self):
        rss_patcher = patch(
            "neurodecodekit.evaluation.foundation_model_live._peak_rss_bytes",
            return_value=32 * 1024 * 1024,
        )
        rss_patcher.start()
        self.addCleanup(rss_patcher.stop)

    def test_context_rebuilds_exact_plan_and_twelve_blinded_wire_requests(self):
        self.assertEqual(self.context.plan["plan_core_sha256"], self.context.contract[
            "source_bindings"
        ]["FM0_plan_core_sha256"])
        self.assertEqual(len(self.context.wire_requests), 12)
        self.assertEqual(
            [row.condition_id for row in self.context.wire_requests[:4]],
            ["FM-A00", "FM-A01", "FM-A02", "FM-A03"],
        )
        for row in self.context.wire_requests:
            body = json.loads(row.body)
            rendered = row.body.decode("ascii")
            self.assertEqual(body["model"], EXPECTED_MODEL_ID)
            self.assertEqual(body["reasoning"], {"effort": "low"})
            self.assertEqual(body["service_tier"], "default")
            self.assertFalse(body["store"])
            self.assertFalse(body["stream"])
            self.assertEqual(body["tools"], [])
            self.assertNotIn(row.condition_id, rendered)
            self.assertNotIn(row.item_id, rendered)
            self.assertLessEqual(
                len(row.body),
                self.context.contract["resource_caps"][
                    "maximum_wire_request_bytes_per_call"
                ],
            )

    def test_dry_run_never_reads_key_or_calls_transport(self):
        with (
            patch(
                "neurodecodekit.evaluation.foundation_model_live._read_api_key_once",
                side_effect=AssertionError("dry-run read the key"),
            ),
            patch(
                "neurodecodekit.evaluation.foundation_model_live._openai_transport",
                side_effect=AssertionError("dry-run called the provider"),
            ),
        ):
            summary = dry_run_summary()
        self.assertEqual(summary["mode"], "dry_run_no_credential_read_no_network")
        self.assertEqual(summary["request_count"], 12)
        self.assertTrue(all(value == 0 for value in summary["access_counters"].values()))

    def test_successful_fake_execution_is_bounded_sanitized_and_valid(self):
        calls = []

        def fake_transport(body, api_key, timeout, maximum_bytes):
            calls.append((body, api_key, timeout, maximum_bytes))
            index = len(calls) - 1
            evidence_used = ("none", "ctc", "ctc_and_neural", "ctc_and_neural")[
                index % 4
            ]
            return provider_response(
                decoded_text=f"TEXT {index % 4}",
                abstained=index % 4 == 0,
                evidence_used=evidence_used,
            )

        result = execute_context_with_transport(
            self.context,
            api_key="test-secret-never-serialize",
            transport=fake_transport,
            implementation_evidence=self.evidence,
        )
        validate_live_result(
            result,
            self.context.contract,
            self.context.wire_requests,
        )
        self.assertEqual(result["status"], "passed")
        self.assertEqual(len(calls), 12)
        self.assertEqual(result["request_count"], 12)
        self.assertEqual(result["completed_response_count"], 12)
        self.assertEqual(result["schema_valid_response_count"], 12)
        self.assertEqual(result["usage"]["input_tokens"], 1200)
        self.assertEqual(result["usage"]["output_tokens"], 240)
        self.assertEqual(result["access_counters"]["API_credential_reads"], 1)
        self.assertEqual(result["access_counters"]["external_network_calls"], 12)
        rendered = json.dumps(result, sort_keys=True)
        self.assertNotIn("test-secret-never-serialize", rendered)
        self.assertNotIn("must-not-be-retained", rendered)
        self.assertNotIn("Authorization", rendered)

    def test_transport_failure_consumes_without_retry_and_sanitizes_detail(self):
        calls = 0

        def fake_transport(body, api_key, timeout, maximum_bytes):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise FoundationModelLiveFailure(
                    "provider_http_429_rate_limit_exceeded_unknown",
                    "sensitive provider body must not survive",
                )
            return provider_response()

        result = execute_context_with_transport(
            self.context,
            api_key="test-secret",
            transport=fake_transport,
            implementation_evidence=self.evidence,
        )
        validate_live_result(
            result,
            self.context.contract,
            self.context.wire_requests,
        )
        self.assertEqual(result["status"], "parked")
        self.assertTrue(result["consumed"])
        self.assertFalse(result["rerun_authorized"])
        self.assertEqual(calls, 3)
        self.assertEqual(result["request_count"], 3)
        self.assertEqual(result["completed_response_count"], 2)
        self.assertEqual(
            result["terminal_failure"]["category"],
            "provider_http_429_rate_limit_exceeded_unknown",
        )
        self.assertNotIn("sensitive provider body", json.dumps(result))

    def test_oversized_response_consumes_first_call_and_parks(self):
        calls = 0

        def fake_transport(body, api_key, timeout, maximum_bytes):
            nonlocal calls
            calls += 1
            return b"x" * (maximum_bytes + 1)

        result = execute_context_with_transport(
            self.context,
            api_key="test-secret",
            transport=fake_transport,
            implementation_evidence=self.evidence,
        )
        self.assertEqual(result["status"], "parked")
        self.assertEqual(calls, 1)
        self.assertEqual(result["request_count"], 1)
        self.assertEqual(result["completed_response_count"], 0)
        self.assertEqual(
            result["terminal_failure"]["category"], "response_byte_cap_exceeded"
        )

    def test_provider_model_and_structured_schema_mismatches_park(self):
        wrong_model = json.loads(provider_response())
        wrong_model["model"] = "gpt-5.6-sol"
        malformed = json.loads(provider_response())
        output = json.loads(malformed["output"][0]["content"][0]["text"])
        output["extra"] = True
        malformed["output"][0]["content"][0]["text"] = json.dumps(output)
        for payload, category in (
            (wrong_model, "provider_model_mismatch"),
            (malformed, "structured_output_schema_mismatch"),
        ):
            with self.subTest(category=category):
                result = execute_context_with_transport(
                    self.context,
                    api_key="test-secret",
                    transport=lambda *args: json.dumps(payload).encode("utf-8"),
                    implementation_evidence=self.evidence,
                )
                self.assertEqual(result["status"], "parked")
                self.assertEqual(result["request_count"], 1)
                self.assertEqual(result["terminal_failure"]["category"], category)

    def test_malformed_usage_consumes_one_call_and_parks(self):
        payload = json.loads(provider_response())
        payload["usage"]["input_tokens"] = "not-an-integer"
        result = execute_context_with_transport(
            self.context,
            api_key="test-secret",
            transport=lambda *args: json.dumps(payload).encode("utf-8"),
            implementation_evidence=self.evidence,
        )
        self.assertEqual(result["status"], "parked")
        self.assertEqual(result["request_count"], 1)
        self.assertEqual(result["completed_response_count"], 0)
        self.assertEqual(result["terminal_failure"]["category"], "invalid_usage")

    def test_output_token_cap_consumes_call_and_preserves_receipt(self):
        cap = self.context.contract["resource_caps"]["maximum_total_output_tokens"]
        result = execute_context_with_transport(
            self.context,
            api_key="test-secret",
            transport=lambda *args: provider_response(output_tokens=cap + 1),
            implementation_evidence=self.evidence,
        )
        self.assertEqual(result["status"], "parked")
        self.assertEqual(result["request_count"], 1)
        self.assertEqual(result["completed_response_count"], 1)
        self.assertEqual(
            result["terminal_failure"]["category"],
            "output_token_cap_exceeded",
        )
        validate_live_result(
            result,
            self.context.contract,
            self.context.wire_requests,
        )

    def test_result_validation_rejects_binding_and_summary_tampering(self):
        result = execute_context_with_transport(
            self.context,
            api_key="test-secret",
            transport=lambda *args: provider_response(),
            implementation_evidence=self.evidence,
        )
        mutations = (
            ("wire binding", lambda row: row["responses"][0].__setitem__("item_id", "SYNTH-ITEM-99")),
            ("summary", lambda row: row["condition_summaries"]["FM-A00"].__setitem__("response_count", 99)),
            ("claim", lambda row: row["claim_boundary"].__setitem__("scientific_claim_not_established", "claim upgraded")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                tampered = copy.deepcopy(result)
                mutate(tampered)
                with self.assertRaisesRegex(RuntimeError, "mismatch|frozen request"):
                    validate_live_result(
                        tampered,
                        self.context.contract,
                        self.context.wire_requests,
                    )

    def test_sanitized_result_roundtrip_inspection_has_no_network(self):
        result = execute_context_with_transport(
            self.context,
            api_key="test-secret",
            transport=lambda *args: provider_response(),
            implementation_evidence=self.evidence,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            write_bounded_json(path, result, maximum_bytes=2 * 1024 * 1024)
            with patch(
                "neurodecodekit.evaluation.foundation_model_live._openai_transport",
                side_effect=AssertionError("inspection called provider"),
            ):
                summary = inspect_live_result(path)
        self.assertEqual(summary["status"], "passed")
        self.assertEqual(summary["request_count"], 12)
        self.assertEqual(summary["schema_valid_response_count"], 12)

    def test_cli_defaults_to_dry_run_and_execute_requires_green_evidence(self):
        stdout = io.StringIO()
        with (
            patch(
                "neurodecodekit.evaluation.foundation_model_live._read_api_key_once",
                side_effect=AssertionError("CLI dry-run read key"),
            ),
            patch("urllib.request.urlopen", side_effect=AssertionError("CLI dry-run network")),
            redirect_stdout(stdout),
        ):
            self.assertEqual(main(["foundation-model-live-smoke"]), 0)
        summary = json.loads(stdout.getvalue())
        self.assertEqual(summary["request_count"], 12)
        self.assertEqual(summary["model_id"], EXPECTED_MODEL_ID)

        stderr = io.StringIO()
        with (
            patch(
                "neurodecodekit.evaluation.foundation_model_live._read_api_key_once",
                side_effect=AssertionError("invalid execute read key"),
            ),
            redirect_stderr(stderr),
        ):
            self.assertEqual(main(["foundation-model-live-smoke", "--execute"]), 2)
        self.assertIn("--out", stderr.getvalue())
        self.assertIn("--implementation-commit", stderr.getvalue())
        self.assertIn("--implementation-push-ci-run-id", stderr.getvalue())

    def test_cli_help_names_one_shot_terra_boundary(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as caught:
            main(["foundation-model-live-smoke", "--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("12-call synthetic GPT-5.6 Terra", stdout.getvalue())

    def test_source_has_no_heavy_dependency_and_uses_fixed_endpoint(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src/neurodecodekit/evaluation/foundation_model_live.py"
        ).read_text(encoding="utf-8")
        for forbidden in ("import mne", "import numpy", "import scipy", "import torch"):
            self.assertNotIn(forbidden, source)
        self.assertIn(EXPECTED_ENDPOINT, source)
        self.assertNotIn("OPENAI_BASE_URL", source)


if __name__ == "__main__":
    unittest.main()
