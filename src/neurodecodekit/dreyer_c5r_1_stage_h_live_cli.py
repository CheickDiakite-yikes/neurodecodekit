"""CLI for the activation-locked DREYER-C5R-1 Stage H live wrapper."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from neurodecodekit.datasets import dreyer_c5r_1_stage_h_live as live


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.dreyer_c5r_1_stage_h_live_cli",
        description="Plan, generated-qualify, or separately activate the one-file Stage H wrapper.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Inspect the locked one-file plan")
    qualify = commands.add_parser(
        "qualify",
        help="Run the sole generated/mock wrapper qualification",
    )
    qualify.add_argument("--output", required=True)
    execute = commands.add_parser(
        "execute",
        help="Run only after the separately green activation exists",
    )
    execute.add_argument("--activation-sha256", required=True)
    execute.add_argument("--activation-commit", required=True)
    execute.add_argument("--activation-ci-run-id", required=True, type=int)
    execute.add_argument("--activation-base-job-id", required=True, type=int)
    execute.add_argument("--activation-optional-job-id", required=True, type=int)
    inspect = commands.add_parser("inspect", help="Inspect an aggregate H1/H0 result")
    inspect.add_argument("path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "plan":
        result = live.registered_plan()
    elif args.command == "qualify":
        result = live.run_generated_qualification(args.output)
    elif args.command == "execute":
        evidence = live.LiveEvidence(
            activation_sha256=args.activation_sha256,
            activation_commit=args.activation_commit,
            activation_ci_run_id=args.activation_ci_run_id,
            activation_base_job_id=args.activation_base_job_id,
            activation_optional_job_id=args.activation_optional_job_id,
        )
        result = live.execute_registered_preflight(evidence)
    else:
        result = live.inspect_public_result(args.path)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
