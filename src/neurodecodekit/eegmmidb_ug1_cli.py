"""Sidecar CLI for the hash-isolated EEGMMIDB-UG1 lane."""

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
        prog="python -m neurodecodekit.eegmmidb_ug1_cli",
        description=(
            "Plan or generated-qualify the frozen EEGMMIDB-UG1 unseen-person lane. "
            "No command exposes real metadata, payload, target, or scoring stages."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "plan",
        help="Print the exact no-stat, no-network acquisition plan.",
    )
    qualify = subparsers.add_parser(
        "qualify",
        help="Consume the sole generated/mock Stage G qualification.",
    )
    qualify.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Exclusive aggregate JSON destination outside protected data roots.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "plan"
    _freeze_threads()
    if command == "plan":
        from neurodecodekit.datasets.eegmmidb_unseen_participant_acquisition import (
            registered_plan,
        )

        print(json.dumps(registered_plan(Path.cwd()), indent=2, sort_keys=True))
        print(
            "Safety default: no output path, network, EDF, retained payload, target, or model was opened."
        )
        return 0
    if command == "qualify":
        from neurodecodekit.experiments.eegmmidb_unseen_participant_generalization import (
            run_generated_qualification,
        )

        summary = run_generated_qualification(args.output)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    parser.error(f"unsupported command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
