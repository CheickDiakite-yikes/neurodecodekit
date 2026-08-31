from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit import fmsr1_witness_cli as cli

ROOT = Path(__file__).resolve().parents[1]
CLI_SOURCE = ROOT / "src/neurodecodekit/fmsr1_witness_cli.py"


class FMSR1WitnessCLITests(unittest.TestCase):
    def invoke(self, *arguments: str) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main(list(arguments))
        return code, json.loads(output.getvalue())

    def test_plan_and_inspection_commands_are_generated_only(self) -> None:
        code, plan = self.invoke("plan")
        self.assertEqual(code, 0)
        self.assertEqual(plan["root_request_count"], 17)
        self.assertFalse(plan["network_authorized"])
        code, inspection = self.invoke("inspect-generated")
        self.assertEqual(code, 0)
        self.assertEqual(inspection["route"], "GENERATED_WITNESS_INSPECTED")
        self.assertEqual(inspection["network_requests"], 0)
        self.assertEqual(inspection["payload_or_neural_reads"], 0)

    def test_qualification_command_dispatches_without_an_alternate_path(self) -> None:
        expected = {"route": "SENTINEL"}
        with mock.patch(
            "neurodecodekit.datasets.fresh_motor_source_identity_witness."
            "run_generated_qualification",
            return_value=expected,
        ) as qualification:
            code, result = self.invoke("qualify-generated")
        self.assertEqual(code, 0)
        self.assertEqual(result, expected)
        qualification.assert_called_once_with()

    def test_help_exposes_no_live_or_execute_command(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.fmsr1_witness_cli", "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("inspect-generated", completed.stdout)
        self.assertIn("qualify-generated", completed.stdout)
        self.assertNotIn("{live", completed.stdout)
        self.assertNotIn(",live", completed.stdout)
        self.assertNotIn("{execute", completed.stdout)
        self.assertNotIn(",execute", completed.stdout)

    def test_unknown_live_and_execute_verbs_refuse(self) -> None:
        for command in ("live", "execute", "witness-source"):
            with self.assertRaises(SystemExit) as raised:
                cli._parser().parse_args([command])
            self.assertEqual(raised.exception.code, 2)

    def test_CLI_source_contains_no_network_or_live_adapter(self) -> None:
        source = CLI_SOURCE.read_text(encoding="utf-8")
        for token in (
            "urllib.request",
            "socket",
            "ssl",
            "http.client",
            "subprocess",
            'add_parser("live"',
            'add_parser("execute"',
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
