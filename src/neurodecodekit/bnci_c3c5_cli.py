"""CLI for the proof-gated BNCI-C3C5-1 experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.bnci_c3c5_cli",
        description="Plan or qualify the generated-only BNCI-C3C5-1 pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "plan",
        help="Print the registered 18-file acquisition plan without touching paths or network.",
    )
    qualify = subparsers.add_parser(
        "qualify",
        help="Run the sole generated/mock G1 qualification.",
    )
    qualify.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New path for the aggregate generated result JSON.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "plan":
        from neurodecodekit.datasets.bnci_2014_001_acquisition import registered_plan

        print(json.dumps(registered_plan(), sort_keys=True, indent=2))
        return 0
    if args.command == "qualify":
        from neurodecodekit.experiments.bnci_2014_001_cross_participant_eeg_gain import (
            run_generated_qualification,
        )

        result = run_generated_qualification(args.output)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    raise RuntimeError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
