"""Generated-only sidecar CLI for COMM-P0-G."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as experiment


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="COMM-P0-G fictional prospective-study engineering only"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="show the frozen bounded generated schedule")
    qualify = commands.add_parser(
        "qualify", help="run the activation-gated official generated qualification"
    )
    qualify.add_argument("--output", type=Path, required=True)
    inspect = commands.add_parser("inspect", help="inspect an aggregate generated result")
    inspect.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        value = experiment.plan()
    elif args.command == "qualify":
        value = experiment.run_generated_qualification(args.output)
    else:
        value = experiment.inspect_result(args.path)
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
