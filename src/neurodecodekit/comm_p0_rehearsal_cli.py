"""CLI for the generated-only COMM-P0 FS2 resource rehearsal."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_two_child_rehearsal as rehearsal


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.comm_p0_rehearsal_cli",
        description=(
            "Inspect or execute the one-shot generated-only COMM-P0 FS2 resource rehearsal."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the target-free registered rehearsal plan.")

    run = subparsers.add_parser(
        "run",
        help="Run only after the exact implementation proof is remotely green on main.",
    )
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--receipt", type=Path, required=True)

    inspect = subparsers.add_parser("inspect", help="Inspect one aggregate FS2 result.")
    inspect.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "plan":
            value = rehearsal.plan()
        elif arguments.command == "run":
            value = rehearsal.run_registered_rehearsal(
                arguments.output,
                receipt=arguments.receipt,
            )
        else:
            value = rehearsal.inspect_result(arguments.path)
    except core.CommP0GeneratedRefusal as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
