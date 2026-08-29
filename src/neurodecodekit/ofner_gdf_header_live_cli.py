"""CLI for the activation-locked Ofner GDF range-header wrapper."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from neurodecodekit.datasets import ofner_gdf_header_live as live


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.ofner_gdf_header_live_cli",
        description="Plan, generated-qualify, or separately activate one Ofner header check.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="Inspect the activation-locked range plan")
    plan.add_argument("--repo-root")
    qualify = commands.add_parser("qualify", help="Run the sole generated/mock qualification")
    qualify.add_argument("--output", required=True)
    qualify.add_argument("--repo-root")
    execute = commands.add_parser("execute", help="Run only after exact activation is green")
    execute.add_argument("--activation-sha256", required=True)
    execute.add_argument("--activation-commit", required=True)
    execute.add_argument("--activation-ci-run-id", required=True, type=int)
    execute.add_argument("--activation-base-job-id", required=True, type=int)
    execute.add_argument("--activation-optional-job-id", required=True, type=int)
    execute.add_argument("--repo-root")
    inspect = commands.add_parser("inspect", help="Inspect one aggregate H1/H0 result")
    inspect.add_argument("path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        result = live.registered_plan(args.repo_root)
    elif args.command == "qualify":
        result = live.run_generated_qualification(args.output, repo_root=args.repo_root)
    elif args.command == "execute":
        evidence = live.LiveEvidence(
            activation_sha256=args.activation_sha256,
            activation_commit=args.activation_commit,
            activation_ci_run_id=args.activation_ci_run_id,
            activation_base_job_id=args.activation_base_job_id,
            activation_optional_job_id=args.activation_optional_job_id,
        )
        result = live.execute_registered_checkpoint(evidence, repo_root=args.repo_root)
    else:
        result = live.inspect_public_result(args.path)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
