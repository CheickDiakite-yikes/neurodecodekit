"""Sidecar CLI for generated-only COMM-P0 FS3 development qualification."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect or qualify the generated-only COMM-P0 FS3 interface."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Inspect the frozen FS3 contract.")
    qualify = subparsers.add_parser(
        "qualify-reduced",
        help="Run two reduced fictional producer/verifier pairs.",
    )
    qualify.add_argument("--participants-per-cohort", type=int, default=3)
    qualify.add_argument("--timeout-seconds", type=float, default=180.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    from neurodecodekit.experiments import comm_p0_generated_dual_verification as FS3

    arguments = build_parser().parse_args(argv)
    if arguments.command == "plan":
        result = FS3.plan()
    else:
        result = FS3.run_reduced_qualification(
            participants_per_cohort=arguments.participants_per_cohort,
            timeout_seconds=arguments.timeout_seconds,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
