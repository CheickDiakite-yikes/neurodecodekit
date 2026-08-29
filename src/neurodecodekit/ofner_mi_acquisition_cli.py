"""Standalone generated-only CLI for the Ofner motor-imagery acquisition core."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from neurodecodekit.datasets.ofner_2017_motor_imagery_acquisition import (
    registered_plan,
    write_generated_qualification_result,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or generated-qualify the Ofner acquisition core. "
            "No real-payload execution mode exists."
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("plan", help="Print the no-network frozen plan.")
    plan.add_argument("--repo-root", default=".")

    qualify = commands.add_parser(
        "qualify-generated",
        help="Run two generated fixture replays and the refusal matrix.",
    )
    qualify.add_argument("--repo-root", default=".")
    qualify.add_argument("--out", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if args.command == "plan":
        print(json.dumps(registered_plan(repo_root), indent=2, sort_keys=True))
        print("Safety default: no network, real payload, header, event, target, or signal access.")
        return 0
    result = write_generated_qualification_result(repo_root, args.out)
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"Wrote generated-only qualification result to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
