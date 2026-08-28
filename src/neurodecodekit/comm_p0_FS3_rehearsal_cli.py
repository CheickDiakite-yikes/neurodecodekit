"""Sidecar CLI for the generated-only COMM-P0 FS3 full resource rehearsal."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect or run the one-shot generated-only COMM-P0 FS3 rehearsal."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Inspect the frozen fail-closed FS3 plan.")
    run = subparsers.add_parser("run", help="Consume the sole registered FS3 attempt.")
    run.add_argument("--output", required=True)
    run.add_argument("--receipt", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect a public FS3 result.")
    inspect.add_argument("--input", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    from neurodecodekit.experiments import (
        comm_p0_generated_dual_verification_rehearsal as rehearsal,
    )

    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "plan":
            result = rehearsal.plan()
        elif arguments.command == "run":
            result = rehearsal.run_registered_rehearsal(
                arguments.output, receipt=arguments.receipt
            )
        else:
            result = rehearsal.inspect_result(arguments.input)
    except Exception as exc:
        consumed = bool(
            arguments.command == "run"
            and os.path.lexists(arguments.receipt)
        )
        result = {
            "schema_name": "neurodecodekit.comm_p0_generated_FS3_cli_refusal",
            "schema_version": "0.1.0",
            "route": "FS3_PARK" if consumed else None,
            "attempt_consumed": consumed,
            "failure_family": getattr(exc, "family", None),
            "refusal": type(exc).__name__,
            "detail": str(exc),
            "scientific_claim_established": False,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
