"""Live-only sidecar CLI for the proof-bound BNCI-C3C5-1 Stage Q run."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from neurodecodekit.datasets.bnci_2014_001_stage_q_live import (
    collect_remote_green_proof,
    execute_registered_stage_q_live,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.bnci_c3c5_stage_q_live_cli",
        description="Execute the exact green-activated BNCI-C3C5-1 Stage Q once.",
    )
    parser.add_argument("--repo-root", default=".")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.repo_root)
    remote_proof = collect_remote_green_proof(root)
    result = execute_registered_stage_q_live(
        root,
        environ=os.environ,
        remote_green_proof=remote_proof,
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
