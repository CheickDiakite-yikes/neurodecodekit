"""Generated-only CLI for the FMSR1 R1-W source-identity witness."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.fmsr1_witness_cli",
        description=(
            "Plan, inspect, or qualify the generated-only FMSR1 R1-W witness. "
            "No live network or source command exists."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the exact generated-only witness plan.")
    subparsers.add_parser(
        "inspect-generated",
        help="Inspect one deterministic generated witness replay.",
    )
    subparsers.add_parser(
        "qualify-generated",
        help="Run the bounded generated-only witness qualification.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    from neurodecodekit.datasets.fresh_motor_source_identity_witness import (
        inspect_generated,
        registered_plan,
        run_generated_qualification,
    )

    if args.command == "plan":
        result = registered_plan()
    elif args.command == "inspect-generated":
        result = inspect_generated()
    else:
        result = run_generated_qualification()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
