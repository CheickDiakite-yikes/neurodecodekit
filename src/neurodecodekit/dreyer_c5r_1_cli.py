"""Generated-only command surface for DREYER-C5R-1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from neurodecodekit.experiments.dreyer_c5r_1 import (
    REGISTERED_RESULT_RELATIVE_PATH,
    inspect_generated_result,
    load_contract,
    plan_real_schedule,
    run_generated_qualification,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.dreyer_c5r_1_cli",
        description="Plan or qualify DREYER-C5R-1 with generated fixtures only.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Inspect the frozen schedule without touching data.")
    qualify = subparsers.add_parser(
        "qualify", help="Run the generated-only target-firewall and model qualification."
    )
    qualify.add_argument(
        "--output",
        type=Path,
        default=REGISTERED_RESULT_RELATIVE_PATH,
        help="No-clobber public result path.",
    )
    inspect = subparsers.add_parser("inspect", help="Inspect a generated result summary.")
    inspect.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        contract = load_contract()
        output = {
            "lane_id": contract["lane_id"],
            "status": contract["status"],
            "schedule": plan_real_schedule(),
            "real_authority": contract["authority"],
            "next_stage": "generated_qualification_only",
        }
    elif args.command == "qualify":
        output = run_generated_qualification(args.output)
    else:
        output = inspect_generated_result(args.path)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
