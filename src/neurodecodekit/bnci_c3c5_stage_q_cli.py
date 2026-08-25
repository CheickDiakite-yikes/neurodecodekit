"""Sidecar CLI for BNCI-C3C5-1 Stage Q."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from neurodecodekit.datasets.bnci_2014_001_stage_q import (
    registered_plan,
    run_generated_qualification,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.bnci_c3c5_stage_q_cli",
        description="Proof-bound target-firewalled BNCI-C3C5-1 Stage Q tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="Print the public Stage Q plan only.")
    plan.add_argument("--repo-root", default=".")
    qualify = subparsers.add_parser(
        "qualify", help="Run the one generated-fixture Stage Q implementation qualification."
    )
    qualify.add_argument("--output", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "plan":
        result = registered_plan(Path(args.repo_root))
    elif args.command == "qualify":
        result = run_generated_qualification(Path(args.output), environ=os.environ)
    else:  # pragma: no cover - argparse enforces the command set
        raise AssertionError("unreachable Stage Q command")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
