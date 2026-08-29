"""CLI for the generated-only DREYER-C5R-1 H-L1R1 qualification."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from neurodecodekit.datasets import (
    dreyer_c5r_1_stage_h_live_recovery_qualification as qualification,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_qualification_cli"
        ),
        description="Run or inspect the generated-only H-L1R1 qualification.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Inspect the exact generated-only matrix")
    commands.add_parser(
        "qualify",
        help="Consume the sole generated-only qualification after exact green CI",
    )
    inspect = commands.add_parser("inspect", help="Inspect the aggregate result")
    inspect.add_argument("path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = qualification.registered_plan()
        elif args.command == "qualify":
            result = qualification.run_official_qualification()
        else:
            result = qualification.inspect_result(args.path)
    except qualification.QualificationRefusal as exc:
        print(json.dumps({"status": "refused", "code": exc.code}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") != "failed_consumed_generated_only" else 1


if __name__ == "__main__":
    raise SystemExit(main())
