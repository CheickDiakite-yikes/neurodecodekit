from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from neurodecodekit import fmsr1_admission_cli as cli

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_COMMANDS = ("execute", "witness", "live")
FORBIDDEN_OPTIONS = {
    "--api-key",
    "--credential",
    "--host",
    "--output",
    "--output-path",
    "--source-path",
    "--token",
    "--url",
}


def _subparser_choices(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    action = next(
        item
        for item in parser._actions
        if isinstance(item, argparse._SubParsersAction)
    )
    return action.choices


def _all_option_strings(parser: argparse.ArgumentParser) -> set[str]:
    options = {
        option
        for action in parser._actions
        for option in action.option_strings
    }
    for child in _subparser_choices(parser).values():
        options.update(
            option
            for action in child._actions
            for option in action.option_strings
        )
    return options


class FMSR1AdmissionCLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.environment = os.environ.copy()
        cls.environment["PYTHONPATH"] = str(ROOT / "src")

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "neurodecodekit.fmsr1_admission_cli", *arguments],
            cwd=ROOT,
            env=self.environment,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_parser_exposes_only_plan_and_qualify_generated(self) -> None:
        parser = cli._parser()
        self.assertEqual(
            tuple(_subparser_choices(parser)),
            ("plan", "qualify-generated"),
        )
        self.assertTrue(_all_option_strings(parser).isdisjoint(FORBIDDEN_OPTIONS))

    def test_help_has_no_execute_witness_live_or_transport_option(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("plan", result.stdout)
        self.assertIn("qualify-generated", result.stdout)
        for command in FORBIDDEN_COMMANDS:
            self.assertNotIn(f"{{plan,qualify-generated,{command}}}", result.stdout)
        for option in FORBIDDEN_OPTIONS:
            self.assertNotIn(option, result.stdout)

    def test_plan_prints_generated_only_closed_authority_JSON(self) -> None:
        result = self.run_cli("plan")
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["protocol_id"], "FMSR1-R1-G-v0")
        self.assertEqual(plan["named_refusal_mutations"], 82)
        self.assertEqual(plan["network_imports"], [])
        self.assertFalse(plan["live_command_present"])
        self.assertFalse(plan["network_or_real_source_authority"])
        self.assertFalse(plan["scientific_claim_authority"])

    def test_forbidden_commands_fail_without_running_qualification(self) -> None:
        for command in FORBIDDEN_COMMANDS:
            with self.subTest(command=command):
                result = self.run_cli(command)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("invalid choice", result.stderr)

    def test_qualify_generated_help_does_not_run_the_one_shot(self) -> None:
        result = self.run_cli("qualify-generated", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("usage:"), 1)
        for option in FORBIDDEN_OPTIONS:
            self.assertNotIn(option, result.stdout)

    def test_CLI_module_has_no_network_import(self) -> None:
        source = (ROOT / "src/neurodecodekit/fmsr1_admission_cli.py").read_text(
            encoding="utf-8"
        )
        imported_roots: set[str] = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertTrue(
            imported_roots.isdisjoint(
                {"aiohttp", "github", "http", "httpx", "requests", "socket", "ssl", "urllib"}
            ),
            imported_roots,
        )


if __name__ == "__main__":
    unittest.main()
