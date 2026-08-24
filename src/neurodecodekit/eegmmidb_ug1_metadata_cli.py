"""Generated-only sidecar CLI for EEGMMIDB-UG1 Stage M1."""

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
        prog="python -m neurodecodekit.eegmmidb_ug1_metadata_cli",
        description=(
            "Plan or generated-qualify EEGMMIDB-UG1 Stage M1. "
            "No command exposes live metadata, payload, target, or scoring stages."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "plan",
        help="Print the exact body-blind Stage M plan without network access.",
    )
    qualify = subparsers.add_parser(
        "qualify",
        help="Run the sole generated/mock Stage M1 metadata qualification.",
    )
    qualify.add_argument(
        "--workspace",
        required=True,
        type=Path,
        help="Existing temporary workspace for generated fixture outputs.",
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
        from neurodecodekit.datasets.eegmmidb_unseen_participant_metadata import (
            registered_metadata_plan,
        )

        print(json.dumps(registered_metadata_plan(Path.cwd()), indent=2, sort_keys=True))
        print(
            "Safety default: no network, real URL, local data path, EDF content, target, or model was opened."
        )
        return 0
    if command == "qualify":
        from neurodecodekit.datasets.eegmmidb_unseen_participant_metadata import (
            run_generated_qualification,
            write_generated_summary,
        )

        summary = run_generated_qualification(
            repo_root=Path.cwd(),
            workspace_root=args.workspace,
            environ=os.environ,
        )
        output_bytes, output_sha256 = write_generated_summary(args.output, summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        print(f"output_bytes={output_bytes} output_sha256={output_sha256}")
        return 0
    parser.error(f"unsupported command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
