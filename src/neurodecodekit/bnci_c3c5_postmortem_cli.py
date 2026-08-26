"""Sidecar CLI for the BNCI C3/C5 artifact-only postmortem."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.bnci_c3c5_postmortem_cli",
        description="Plan, run, or inspect the aggregate-only BNCI C3/C5 postmortem.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Show the bounded artifact-only envelope.")
    run = commands.add_parser("run", help="Create the one no-clobber aggregate report.")
    run.add_argument("--implementation-commit", required=True)
    run.add_argument("--ci-run-id", required=True, type=int)
    run.add_argument("--base-job-id", required=True, type=int)
    run.add_argument("--optional-job-id", required=True, type=int)
    commands.add_parser("inspect", help="Validate and summarize the report.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    from neurodecodekit.experiments import bnci_2014_001_artifact_postmortem as postmortem

    root = Path(__file__).resolve().parents[2]
    if args.command == "plan":
        result = postmortem.plan_postmortem()
    elif args.command == "inspect":
        result = postmortem.inspect_postmortem(root)
    else:
        result = postmortem.run_registered_postmortem(
            root,
            implementation_commit=args.implementation_commit,
            ci_run_id=args.ci_run_id,
            base_job_id=args.base_job_id,
            optional_job_id=args.optional_job_id,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
