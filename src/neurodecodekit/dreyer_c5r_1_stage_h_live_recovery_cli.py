"""CLI for the generated-only DREYER-C5R-1 H-L1R1 implementation."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from neurodecodekit.datasets import dreyer_c5r_1_stage_h_live_recovery as recovery


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_cli",
        description="Inspect the activation-locked H-L1R1 generated implementation.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Inspect the locked generated plan")
    inspect = commands.add_parser("inspect", help="Inspect an aggregate generated report")
    inspect.add_argument("path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        result = recovery.registered_plan()
    else:
        result = recovery.inspect_generated_report(args.path)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
