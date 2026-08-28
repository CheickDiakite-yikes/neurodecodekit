"""CLI for the additive COMM-P0-G generated proof runner."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_runner as runner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.comm_p0_runner_cli",
        description="Inspect or development-test the activation-locked COMM-P0-G runner.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("plan", help="Print the target-free registered execution plan.")

    development = subparsers.add_parser(
        "develop",
        help="Run a reduced two-replay generated engineering check; this is not official.",
    )
    development.add_argument("--participants-per-cohort", type=int, default=4)
    development.add_argument("--timeout-seconds", type=float, default=60.0)
    development.add_argument("--output", type=Path)

    qualify = subparsers.add_parser(
        "qualify", help="Run only after a future exact green activation exists."
    )
    qualify.add_argument("--output", type=Path, required=True)

    inspect = subparsers.add_parser("inspect", help="Inspect a target-free public result.")
    inspect.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "plan":
            value = core.plan()
        elif arguments.command == "develop":
            value = runner.run_development_replay_pair(
                participants_per_cohort=arguments.participants_per_cohort,
                timeout_seconds=arguments.timeout_seconds,
            )
            if arguments.output is not None:
                runner.publish_no_replace(arguments.output, value)
        elif arguments.command == "qualify":
            value = runner.run_official_qualification(arguments.output)
        else:
            value = core.inspect_result(arguments.path)
    except core.CommP0GeneratedRefusal as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
