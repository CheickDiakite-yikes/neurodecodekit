"""Sidecar CLI for the BNCI-C3C5-1 Stage A signed-object recovery."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence


THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


def _freeze_threads() -> None:
    for name in THREAD_ENVIRONMENT:
        os.environ[name] = "1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.bnci_c3c5_stage_a_redirect_recovery_cli",
        description="Plan, qualify, or execute the proof-gated BNCI signed-object recovery.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "plan",
        help="Print the green-decision-bound plan without network or ignored-path access.",
    )
    subparsers.add_parser(
        "qualify",
        help="Run the single generated qualification; a recorded result refuses repeats.",
    )
    subparsers.add_parser(
        "execute",
        help="Consume and run the single registered signed-object recovery.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _freeze_threads()
    if args.command == "plan":
        from neurodecodekit.datasets.bnci_2014_001_stage_a_redirect_recovery import (
            registered_recovery_plan,
        )

        result = registered_recovery_plan(Path.cwd())
    elif args.command == "qualify":
        from neurodecodekit.datasets.bnci_2014_001_stage_a_redirect_recovery import (
            run_generated_recovery_qualification,
        )

        result = run_generated_recovery_qualification()
    elif args.command == "execute":
        from neurodecodekit.datasets.bnci_2014_001_stage_a_redirect_recovery import (
            execute_registered_recovery,
        )

        result = execute_registered_recovery(Path.cwd(), environ=os.environ)
    else:  # pragma: no cover
        raise RuntimeError(f"unsupported command: {args.command}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
