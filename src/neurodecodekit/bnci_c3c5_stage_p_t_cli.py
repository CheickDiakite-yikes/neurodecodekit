"""Isolated CLI for proof-gated BNCI-C3C5-1 Stages P and T."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.bnci_c3c5_stage_p_t_cli",
        description="Plan or execute the proof-gated BNCI-C3C5-1 P/T stages.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan-p", help="Show the target-blind Stage P envelope.")
    commands.add_parser("plan-t", help="Show the one-score Stage T envelope.")
    commands.add_parser("execute-p", help="Execute the single activated real Stage P run.")
    commands.add_parser("score-t", help="Execute the single activated Stage T score.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    if args.command in {"plan-p", "execute-p"}:
        from neurodecodekit.experiments import bnci_2014_001_stage_p_live as stage_p

        result = (
            stage_p.plan_stage_p()
            if args.command == "plan-p"
            else stage_p.execute_registered_stage_p(root, environ=os.environ)
        )
    else:
        from neurodecodekit.evaluation import bnci_2014_001_stage_t_live as stage_t

        result = (
            stage_t.plan_stage_t()
            if args.command == "plan-t"
            else stage_t.execute_registered_stage_t(root, environ=os.environ)
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
