from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit import fmsr1_witness_live_cli as cli
from neurodecodekit.datasets import fresh_motor_source_identity_witness_live as live


ROOT = Path(__file__).resolve().parents[1]
CLI_SOURCE = ROOT / "src/neurodecodekit/fmsr1_witness_live_cli.py"


class FMSR1WitnessLiveCLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.network_patches = (
            mock.patch("socket.getaddrinfo", side_effect=AssertionError("network closed")),
            mock.patch("socket.socket", side_effect=AssertionError("network closed")),
        )
        for patcher in self.network_patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def invoke(self, *arguments: str) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main(list(arguments))
        return code, json.loads(output.getvalue())

    def test_help_names_only_bounded_commands(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            cli.main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        help_text = output.getvalue()
        self.assertIn("{plan,qualify-generated,execute}", help_text)
        self.assertIn("one-shot", help_text)
        self.assertNotIn("--repo-root", help_text)
        self.assertNotIn("--url", help_text)
        self.assertNotIn("--output", help_text)

    def test_plan_is_inspectable_and_does_not_dispatch_execution(self) -> None:
        with mock.patch.object(
            cli,
            "execute_registered_witness",
            side_effect=AssertionError("execute must stay closed"),
        ) as execute:
            code, result = self.invoke("plan")
        self.assertEqual(code, 0)
        self.assertEqual(result["packet_id"], live.PACKET_ID)
        self.assertEqual(result["root_request_count"], 17)
        self.assertEqual(result["CI_request_count"], 3)
        self.assertTrue(result["execution_decision_required"])
        self.assertFalse(result["scientific_claim_established"])
        execute.assert_not_called()

    def test_execute_refusal_is_sanitized_and_omits_exception_text(self) -> None:
        sensitive = "/private/tmp/secret-decision-path"
        with mock.patch.object(
            cli,
            "execute_registered_witness",
            side_effect=live.LiveWitnessRefusal("LIVE_PATH_REFUSE", f"sensitive path: {sensitive}"),
        ) as execute:
            code, result = self.invoke("execute")
        self.assertEqual(code, 2)
        self.assertEqual(result["route"], "NAMED_FAIL_CLOSED_REFUSAL")
        self.assertEqual(result["refusal_code"], "LIVE_PATH_REFUSE")
        self.assertFalse(result["scientific_claim_established"])
        self.assertNotIn(sensitive, json.dumps(result))
        self.assertNotIn("sensitive path", json.dumps(result))
        execute.assert_called_once_with()

    def test_returned_post_marker_refusal_keeps_nonzero_exit(self) -> None:
        with mock.patch.object(
            cli,
            "execute_registered_witness",
            return_value={
                "route": "NAMED_FAIL_CLOSED_REFUSAL",
                "scientific_claim_established": False,
            },
        ):
            code, result = self.invoke("execute")
        self.assertEqual(code, 2)
        self.assertEqual(result["route"], "NAMED_FAIL_CLOSED_REFUSAL")

    def test_consumed_generated_qualification_is_a_sanitized_refusal(self) -> None:
        code, result = self.invoke("qualify-generated")
        self.assertEqual(code, 2)
        self.assertEqual(result["route"], "NAMED_FAIL_CLOSED_REFUSAL")
        self.assertEqual(result["refusal_code"], "LIVE_AUTHORITY_REFUSE")
        self.assertFalse(result["scientific_claim_established"])

    def test_parser_and_source_expose_no_generic_override_flags(self) -> None:
        source = CLI_SOURCE.read_text(encoding="utf-8")
        forbidden = (
            "--repo-root",
            "--url",
            "--host",
            "--contact",
            "--decision",
            "--output",
            "--retry",
            "--rerun",
            "--resume",
            "--substitute",
        )
        for option in forbidden:
            self.assertNotIn(option, source)
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
                cli.build_parser().parse_args(["execute", option, "value"])
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
