"""CLI for the execution-locked FMSR1 live source witness."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from neurodecodekit.datasets import fresh_motor_source_identity_witness as core
from neurodecodekit.datasets.fresh_motor_source_identity_witness_live import (
    LiveWitnessPark,
    LiveWitnessRefusal,
    execute_registered_witness,
    registered_live_plan,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the decision-locked FMSR1 source-identity witness. "
            "Execution is one-shot and fails before network unless the exact decision "
            "is tracked on clean, remotely green GitHub main."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "plan", help="Print the bounded live witness plan without network access."
    )
    subparsers.add_parser(
        "qualify-generated",
        help="Report the consumed generated qualification as closed.",
    )
    subparsers.add_parser(
        "execute",
        help="Consume and run the single registered CI-gated live source witness.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "plan":
        result = registered_live_plan()
    elif args.command == "qualify-generated":
        from neurodecodekit.datasets.fresh_motor_source_identity_witness_live_qualification import (
            run_generated_live_qualification,
        )

        try:
            result = run_generated_live_qualification()
        except (LiveWitnessRefusal, LiveWitnessPark, core.WitnessRefusal) as exc:
            refusal_code = (
                exc.code if isinstance(exc, LiveWitnessRefusal) else "LIVE_TRANSPORT_REFUSE"
            )
            print(
                json.dumps(
                    {
                        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_live_refusal",
                        "schema_version": "0.1.0",
                        "route": "NAMED_FAIL_CLOSED_REFUSAL",
                        "refusal_code": refusal_code,
                        "scientific_claim_established": False,
                    },
                    sort_keys=True,
                )
            )
            return 2
    else:
        try:
            result = execute_registered_witness()
        except LiveWitnessRefusal as exc:
            print(
                json.dumps(
                    {
                        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_live_refusal",
                        "schema_version": "0.1.0",
                        "route": "NAMED_FAIL_CLOSED_REFUSAL",
                        "refusal_code": exc.code,
                        "scientific_claim_established": False,
                    },
                    sort_keys=True,
                )
            )
            return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result.get("route") == "NAMED_FAIL_CLOSED_REFUSAL" else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
