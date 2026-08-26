"""Generated/mock-only command surface for DREYER-C5R-1 Stage H."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from neurodecodekit.datasets.dreyer_c5r_1_stage_h import (
    REGISTERED_RESULT_RELATIVE_PATH,
    REGISTERED_SPEC,
    inspect_generated_result,
    load_contract,
    run_generated_qualification,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.dreyer_c5r_1_stage_h_cli",
        description="Plan or qualify the Stage H preflight with generated fixtures only.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Inspect the frozen one-member plan without access.")
    qualify = subparsers.add_parser(
        "qualify", help="Run the generated/mock streaming and sensor-contract qualification."
    )
    qualify.add_argument(
        "--output",
        type=Path,
        default=REGISTERED_RESULT_RELATIVE_PATH,
        help="No-clobber public generated result path.",
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
            "preflight": {
                "url": REGISTERED_SPEC.url,
                "path": REGISTERED_SPEC.relative_path,
                "bytes": REGISTERED_SPEC.bytes,
                "sha256": REGISTERED_SPEC.sha256,
            },
            "real_authority": False,
            "live_execute_command": False,
        }
    elif args.command == "qualify":
        output = run_generated_qualification(args.output)
    else:
        output = inspect_generated_result(args.path)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
