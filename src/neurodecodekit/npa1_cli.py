"""Standalone generated-only CLI for NPA1 transport admission."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from neurodecodekit.datasets.neural_payload_admission import (
    NeuralPayloadAdmissionRefusal,
    registered_plan,
    run_generated_qualification,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.npa1_cli",
        description="Inspect or qualify the generated-only NPA1 transport boundary.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("plan", "Print the bounded generated-only NPA1 plan."),
        ("qualify-generated", "Run the generated transport qualification."),
    ):
        child = subparsers.add_parser(command, help=help_text)
        child.add_argument(
            "--repo-root",
            type=Path,
            default=Path.cwd(),
            help="Repository root containing the frozen frontier.",
        )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = registered_plan(args.repo_root)
        elif args.command == "qualify-generated":
            result = run_generated_qualification(args.repo_root)
        else:  # pragma: no cover - argparse enforces the command set
            raise AssertionError("unknown command")
    except (OSError, ValueError, NeuralPayloadAdmissionRefusal) as exc:
        raise SystemExit(f"refused: {exc}") from exc
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
