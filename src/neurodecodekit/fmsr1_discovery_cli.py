"""CLI for the packet-bound FMSR1 metadata-only discovery lane."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from neurodecodekit.datasets import fresh_motor_source_discovery as discovery


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.fmsr1_discovery_cli",
        description="Plan or qualify the generated FMSR1 metadata discovery.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Inspect the exact zero-network request plan")
    commands.add_parser(
        "qualify-generated",
        help="Run two deterministic mock-HTTP replays and adversarial refusals",
    )
    execute = commands.add_parser(
        "execute",
        help="Report the fail-closed live barrier; this packet is not armable",
    )
    execute.add_argument("--implementation-commit", required=True)
    execute.add_argument("--implementation-registry-sha256", required=True)
    execute.add_argument("--implementation-proof-commit", required=True)
    execute.add_argument("--implementation-proof-sha256", required=True)
    execute.add_argument("--ci-run-id", required=True, type=int)
    execute.add_argument("--base-python-job-id", required=True, type=int)
    execute.add_argument("--optional-neuro-readers-job-id", required=True, type=int)
    execute.add_argument("--execution-ordinal", type=int, default=1)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = discovery.registered_plan()
        elif args.command == "qualify-generated":
            result = discovery.run_generated_qualification()
        else:
            evidence = discovery.GreenImplementationEvidence(
                implementation_commit=args.implementation_commit,
                implementation_registry_sha256=args.implementation_registry_sha256,
                implementation_proof_commit=args.implementation_proof_commit,
                implementation_proof_sha256=args.implementation_proof_sha256,
                CI_run_id=args.ci_run_id,
                base_python_job_id=args.base_python_job_id,
                optional_neuro_readers_job_id=args.optional_neuro_readers_job_id,
                execution_ordinal=args.execution_ordinal,
            )
            result = discovery.execute_registered_discovery(evidence)
    except discovery.FreshMotorDiscoveryRefusal as exc:
        print(json.dumps({"status": "refused", "route": exc.route}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
