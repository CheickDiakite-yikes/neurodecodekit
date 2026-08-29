"""CLI for the activation-locked DREYER-C5R-1 H-L2 adapter."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from neurodecodekit.datasets import dreyer_c5r_1_stage_h_l2 as hl2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.dreyer_c5r_1_stage_h_l2_cli",
        description="Inspect or execute the one-file activation-locked H-L2 adapter.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Inspect the activation-locked H-L2 plan")
    commands.add_parser(
        "qualify-generated",
        help="Run the complete generated-only adapter qualification",
    )
    inspect = commands.add_parser("inspect", help="Inspect an aggregate H-L2 result")
    inspect.add_argument("path")
    execute = commands.add_parser(
        "execute",
        help="Execute only after the exact activation is remotely green",
    )
    execute.add_argument("--activation-sha256", required=True)
    execute.add_argument("--activation-commit", required=True)
    execute.add_argument("--activation-ci-run-id", required=True, type=int)
    execute.add_argument("--activation-base-job-id", required=True, type=int)
    execute.add_argument("--activation-optional-job-id", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = hl2.registered_plan()
        elif args.command == "qualify-generated":
            result = hl2.run_generated_qualification()
        elif args.command == "inspect":
            result = hl2.inspect_public_result(args.path)
        else:
            evidence = hl2.ActivationEvidence(
                activation_sha256=args.activation_sha256,
                activation_commit=args.activation_commit,
                activation_ci_run_id=args.activation_ci_run_id,
                activation_base_job_id=args.activation_base_job_id,
                activation_optional_job_id=args.activation_optional_job_id,
            )
            result = hl2.execute_registered_preflight(evidence)
    except hl2.HL2Refusal as exc:
        print(json.dumps({"status": "refused", "refusal_code": exc.code}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
