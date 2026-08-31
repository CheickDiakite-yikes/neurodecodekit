"""CLI for the generated-only FMSR1 R1-G admission qualification."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.fmsr1_admission_cli",
        description=(
            "Inspect or run the generated-only FMSR1 R1-G admission "
            "qualification. No live network surface exists."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the registered generated-only plan.")
    subparsers.add_parser(
        "qualify-generated",
        help="Run the externally gated generated-only qualification once.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    from neurodecodekit.datasets.fresh_motor_source_admission import (
        registered_plan,
        run_generated_qualification,
    )

    if args.command == "plan":
        result = registered_plan()
    else:
        result = run_generated_qualification()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
