"""Generated-only sidecar CLI for COMM-LIVE-G0."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path

from neurodecodekit.experiments import comm_live_g0_generated as experiment


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="COMM-LIVE-G0 generated session qualification only"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="show the frozen generated schedule")
    qualify = commands.add_parser(
        "qualify", help="run the proof-gated one-shot generated qualification"
    )
    qualify.add_argument("--output", type=Path, required=True)
    inspect = commands.add_parser("inspect", help="inspect a generated result")
    inspect.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        value = experiment.plan()
    elif args.command == "qualify":
        value = experiment.qualify(args.output)
    else:
        value = experiment.inspect_result(args.path)
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
