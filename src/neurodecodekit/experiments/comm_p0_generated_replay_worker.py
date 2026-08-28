"""Isolated child-process entry point for one COMM-P0-G generated replay."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_qualification as qualification


CONTROL_KEYS = frozenset(
    {
        "repository",
        "temporary_root",
        "participants_per_cohort",
        "absolute_deadline",
        "vault_key_hex",
        "opaque_key_hex",
        "freeze_key_hex",
        "invocation_nonce",
    }
)


def _read_fd(fd: int, *, byte_cap: int) -> bytes:
    payload = bytearray()
    while block := os.read(fd, min(1_048_576, byte_cap - len(payload) + 1)):
        payload.extend(block)
        if len(payload) > byte_cap:
            qualification._refuse("private_derivative_cap_breach")
    return bytes(payload)


def _write_fd(fd: int, payload: bytes, *, byte_cap: int) -> None:
    if len(payload) > byte_cap:
        qualification._refuse("private_derivative_cap_breach")
    qualification._write_all(fd, payload)
    os.fsync(fd)


def descriptor_main(*, control_fd: int, output_fd: int) -> dict[str, Any]:
    payload = _read_fd(control_fd, byte_cap=16_384)
    try:
        control = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        ) from exc
    if not isinstance(control, Mapping) or set(control) != CONTROL_KEYS:
        qualification._refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    if core.canonical_json_bytes(dict(control)) != payload:
        qualification._refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    try:
        keys = {
            name: bytes.fromhex(str(control[f"{name}_hex"]))
            for name in ("vault_key", "opaque_key", "freeze_key")
        }
    except ValueError as exc:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        ) from exc
    if any(len(value) != 32 for value in keys.values()):
        qualification._refuse("protocol_model_threshold_vocabulary_prior_or_code_hash_drift")
    result = qualification._run_replay(
        Path(str(control["repository"])),
        Path(str(control["temporary_root"])),
        participants_per_cohort=int(control["participants_per_cohort"]),
        absolute_deadline=float(control["absolute_deadline"]),
        vault_key=keys["vault_key"],
        opaque_key=keys["opaque_key"],
        freeze_key=keys["freeze_key"],
        invocation_nonce=str(control["invocation_nonce"]),
    )
    result["isolated_replay_worker_pid"] = os.getpid()
    core.assert_target_free(result)
    _write_fd(output_fd, core.canonical_json_bytes(result), byte_cap=1_048_576)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Internal COMM-P0-G replay worker")
    parser.add_argument("--control-fd", type=int, required=True)
    parser.add_argument("--output-fd", type=int, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    descriptor_main(control_fd=args.control_fd, output_fd=args.output_fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
