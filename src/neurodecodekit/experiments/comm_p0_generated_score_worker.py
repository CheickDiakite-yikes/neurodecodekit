"""Descriptor-only isolated aggregate scorer for generated COMM-P0-G fixtures.

The worker accepts no paths. It verifies every target-free input and the HMAC
freeze before it inspects the preopened target descriptor, consumes that target
delivery once, and delegates only pure scoring to ``comm_p0_generated_score_only``.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import hmac
import json
import os
import stat
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from neurodecodekit.experiments import comm_p0_generated_score_only as score_only
from neurodecodekit.experiments import comm_p0_generated_streaming_score as streaming_score

SCHEMA_VERSION = "0.1.0"
ATTESTATION_SCHEMA = "neurodecodekit.comm_p0_generated_score_worker_freeze"
OUTPUT_SCHEMA = "neurodecodekit.comm_p0_generated_score_worker_aggregate"
DEFAULT_INPUT_BYTE_CAP = 16 * 1024 * 1024
DEFAULT_OUTPUT_BYTE_CAP = 1 * 1024 * 1024
DEFAULT_RECORD_CAP = 100_000
MAX_LINE_BYTES = 64 * 1024

_BOUND_SURFACES = (
    "contract",
    "trial_manifest",
    "prediction_stream",
    "live_observations",
)
_CONSUMED_TARGET_IDENTITIES: set[tuple[int, int]] = set()


def _refuse(family: str, detail: str | None = None) -> None:
    raise score_only.ScoreOnlyRefusal(family, detail)


def _descriptor_stat(fd: int, *, access: int, surface: str) -> os.stat_result:
    if isinstance(fd, bool) or not isinstance(fd, int) or fd < 0:
        _refuse("descriptor_capability_mismatch", surface)
    try:
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        descriptor_stat = os.fstat(fd)
    except OSError as exc:
        _refuse("descriptor_capability_mismatch", surface)
        raise AssertionError from exc
    if flags & os.O_ACCMODE != access:
        _refuse("descriptor_access_mode_mismatch", surface)
    if not stat.S_ISREG(descriptor_stat.st_mode) or descriptor_stat.st_nlink != 1:
        _refuse("descriptor_type_or_link_mismatch", surface)
    try:
        offset = os.lseek(fd, 0, os.SEEK_CUR)
    except OSError as exc:
        _refuse("descriptor_capability_mismatch", surface)
        raise AssertionError from exc
    if offset != 0:
        _refuse("repeated_score_or_target_delivery", surface)
    return descriptor_stat


def _read_bounded(
    fd: int,
    *,
    surface: str,
    byte_cap: int,
) -> tuple[dict[str, Any], bytes]:
    descriptor_stat = _descriptor_stat(fd, access=os.O_RDONLY, surface=surface)
    if byte_cap <= 0 or descriptor_stat.st_size <= 0 or descriptor_stat.st_size > byte_cap:
        _refuse("bounded_input_violation", surface)
    remaining = descriptor_stat.st_size
    chunks: list[bytes] = []
    digest = hashlib.sha256()
    while remaining:
        chunk = os.read(fd, min(64 * 1024, remaining))
        if not chunk:
            _refuse("descriptor_identity_mismatch", surface)
        chunks.append(chunk)
        digest.update(chunk)
        remaining -= len(chunk)
    if os.read(fd, 1):
        _refuse("descriptor_identity_mismatch", surface)
    after = os.fstat(fd)
    if (
        after.st_dev != descriptor_stat.st_dev
        or after.st_ino != descriptor_stat.st_ino
        or after.st_size != descriptor_stat.st_size
        or after.st_nlink != 1
        or not stat.S_ISREG(after.st_mode)
    ):
        _refuse("descriptor_identity_mismatch", surface)
    payload = b"".join(chunks)
    return (
        {
            "device": int(descriptor_stat.st_dev),
            "inode": int(descriptor_stat.st_ino),
            "size_bytes": int(descriptor_stat.st_size),
            "sha256": digest.hexdigest(),
        },
        payload,
    )


def _reject_duplicate_pairs(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _refuse("noncanonical_input", f"duplicate:{key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    _refuse("noncanonical_input", value)


def _decode_json(payload: bytes, *, surface: str) -> Any:
    try:
        value = json.loads(
            payload,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        _refuse("noncanonical_input", surface)
        raise AssertionError from exc
    if score_only.canonical_json_bytes(value) != payload:
        _refuse("noncanonical_input", surface)
    return value


def _decode_ndjson(
    payload: bytes,
    *,
    surface: str,
    record_cap: int,
) -> tuple[dict[str, Any], ...]:
    if record_cap <= 0 or not payload.endswith(b"\n"):
        _refuse("noncanonical_input", surface)
    lines = payload.splitlines(keepends=True)
    if not lines or len(lines) > record_cap:
        _refuse("bounded_input_violation", surface)
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if len(line) > MAX_LINE_BYTES:
            _refuse("bounded_input_violation", f"{surface}[{index}]")
        value = _decode_json(line, surface=f"{surface}[{index}]")
        if not isinstance(value, Mapping):
            _refuse("noncanonical_input", f"{surface}[{index}]")
        records.append(dict(value))
    return tuple(records)


def _iter_ndjson_descriptor(
    fd: int,
    *,
    surface: str,
    byte_cap: int,
    record_cap: int,
) -> Iterable[dict[str, Any]]:
    """Yield canonical records while retaining at most one decoded row."""

    descriptor_stat = _descriptor_stat(fd, access=os.O_RDONLY, surface=surface)
    if byte_cap <= 0 or descriptor_stat.st_size <= 0 or descriptor_stat.st_size > byte_cap:
        _refuse("bounded_input_violation", surface)
    buffer = bytearray()
    total = 0
    records = 0
    while total < descriptor_stat.st_size:
        chunk = os.read(fd, min(64 * 1024, descriptor_stat.st_size - total))
        if not chunk:
            _refuse("descriptor_identity_mismatch", surface)
        total += len(chunk)
        buffer.extend(chunk)
        while True:
            newline = buffer.find(b"\n")
            if newline < 0:
                if len(buffer) > MAX_LINE_BYTES:
                    _refuse("bounded_input_violation", f"{surface}[{records}]")
                break
            line = bytes(buffer[: newline + 1])
            del buffer[: newline + 1]
            if len(line) > MAX_LINE_BYTES:
                _refuse("bounded_input_violation", f"{surface}[{records}]")
            if records >= record_cap:
                _refuse("bounded_input_violation", surface)
            value = _decode_json(line, surface=f"{surface}[{records}]")
            if not isinstance(value, Mapping):
                _refuse("noncanonical_input", f"{surface}[{records}]")
            records += 1
            yield dict(value)
    if buffer or records == 0 or os.read(fd, 1):
        _refuse("noncanonical_input", surface)
    after = os.fstat(fd)
    if (
        after.st_dev != descriptor_stat.st_dev
        or after.st_ino != descriptor_stat.st_ino
        or after.st_size != descriptor_stat.st_size
        or after.st_nlink != 1
        or not stat.S_ISREG(after.st_mode)
    ):
        _refuse("descriptor_identity_mismatch", surface)


def _hmac_sha256(key: bytes, body: Mapping[str, Any]) -> str:
    return hmac.new(key, score_only.canonical_json_bytes(body), hashlib.sha256).hexdigest()


def _verify_attestation(
    attestation: Mapping[str, Any],
    *,
    hmac_key: bytes,
    identities: Mapping[str, Mapping[str, Any]],
    contract: Mapping[str, Any],
    expected_freeze: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not isinstance(hmac_key, bytes) or len(hmac_key) < 32:
        _refuse("freeze_hmac_key_invalid")
    body = dict(attestation)
    supplied = body.pop("attestation_hmac_sha256", None)
    if not isinstance(supplied, str) or not hmac.compare_digest(
        supplied, _hmac_sha256(hmac_key, body)
    ):
        _refuse("prediction_row_or_probability_tamper_after_freeze")
    if (
        body.get("schema_name") != ATTESTATION_SCHEMA
        or body.get("schema_version") != SCHEMA_VERSION
        or body.get("gate_id") != contract.get("gate_id")
        or body.get("target_descriptor_open_count_at_freeze") != 0
        or body.get("target_delivery_count_at_freeze") != 0
        or body.get("score_count_at_freeze") != 0
    ):
        _refuse("prediction_freeze_attestation_mismatch")
    if body.get("bound_inputs") != identities:
        _refuse("descriptor_identity_mismatch")
    if body.get("score_only_prediction_freeze") != expected_freeze:
        _refuse("prediction_freeze_attestation_mismatch")
    authorization = body.get("authorization")
    if not isinstance(authorization, Mapping):
        _refuse("one_shot_authorization_invalid")
    return authorization


def build_freeze_attestation(
    *,
    contract: Mapping[str, Any],
    predictions: Sequence[Mapping[str, Any]] | None = None,
    prediction_freeze: Mapping[str, Any] | None = None,
    identities: Mapping[str, Mapping[str, Any]],
    authorization: Mapping[str, Any],
    hmac_key: bytes,
) -> dict[str, Any]:
    """Build the exact target-free attestation accepted by the score child."""

    if set(identities) != set(_BOUND_SURFACES):
        _refuse("descriptor_identity_mismatch")
    if (predictions is None) == (prediction_freeze is None):
        _refuse("prediction_freeze_attestation_mismatch")
    exact_freeze = (
        dict(prediction_freeze)
        if prediction_freeze is not None
        else streaming_score.build_prediction_freeze_attestation(iter(predictions or ()), contract)
    )
    body = {
        "schema_name": ATTESTATION_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": str(contract.get("gate_id", "")),
        "target_descriptor_open_count_at_freeze": 0,
        "target_delivery_count_at_freeze": 0,
        "score_count_at_freeze": 0,
        "bound_inputs": {key: dict(identities[key]) for key in _BOUND_SURFACES},
        "score_only_prediction_freeze": exact_freeze,
        "authorization": dict(authorization),
    }
    body["attestation_hmac_sha256"] = _hmac_sha256(hmac_key, body)
    return body


def _write_canonical(fd: int, value: Mapping[str, Any], *, byte_cap: int) -> None:
    descriptor_stat = _descriptor_stat(fd, access=os.O_WRONLY, surface="aggregate_output")
    if descriptor_stat.st_size != 0:
        _refuse("repeated_score_or_target_delivery", "aggregate_output")
    payload = score_only.canonical_json_bytes(value)
    if byte_cap <= 0 or len(payload) > byte_cap:
        _refuse("bounded_output_violation")
    view = memoryview(payload)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            _refuse("aggregate_output_write_failure")
        view = view[written:]
    os.fsync(fd)


def descriptor_main(
    *,
    contract_fd: int,
    trial_manifest_fd: int,
    prediction_stream_fd: int,
    freeze_attestation_fd: int,
    target_envelope_fd: int,
    live_observations_fd: int,
    aggregate_output_fd: int,
    hmac_key: bytes,
    input_byte_cap: int = DEFAULT_INPUT_BYTE_CAP,
    output_byte_cap: int = DEFAULT_OUTPUT_BYTE_CAP,
    record_cap: int = DEFAULT_RECORD_CAP,
) -> dict[str, Any]:
    """Run one target-firewalled generated score over preopened descriptors only."""

    output_stat = _descriptor_stat(
        aggregate_output_fd, access=os.O_WRONLY, surface="aggregate_output"
    )
    if output_stat.st_size != 0:
        _refuse("repeated_score_or_target_delivery", "aggregate_output")

    identities: dict[str, Mapping[str, Any]] = {}
    identities["contract"], contract_payload = _read_bounded(
        contract_fd, surface="contract", byte_cap=input_byte_cap
    )
    identities["trial_manifest"], trial_payload = _read_bounded(
        trial_manifest_fd, surface="trial_manifest", byte_cap=input_byte_cap
    )
    identities["live_observations"], live_payload = _read_bounded(
        live_observations_fd, surface="live_observations", byte_cap=input_byte_cap
    )
    _, attestation_payload = _read_bounded(
        freeze_attestation_fd, surface="freeze_attestation", byte_cap=input_byte_cap
    )

    contract = _decode_json(contract_payload, surface="contract")
    attestation = _decode_json(attestation_payload, surface="freeze_attestation")
    if not isinstance(contract, Mapping) or not isinstance(attestation, Mapping):
        _refuse("noncanonical_input")
    trials = _decode_ndjson(trial_payload, surface="trial_manifest", record_cap=record_cap)
    prediction_stat = _descriptor_stat(
        prediction_stream_fd, access=os.O_RDONLY, surface="prediction_stream"
    )
    if (
        input_byte_cap <= 0
        or prediction_stat.st_size <= 0
        or prediction_stat.st_size > input_byte_cap
    ):
        _refuse("bounded_input_violation", "prediction_stream")
    prediction_freeze = streaming_score.build_prediction_freeze_attestation(
        _iter_ndjson_descriptor(
            prediction_stream_fd,
            surface="prediction_stream",
            byte_cap=input_byte_cap,
            record_cap=record_cap,
        ),
        contract,
    )
    identities["prediction_stream"] = {
        "device": int(prediction_stat.st_dev),
        "inode": int(prediction_stat.st_ino),
        "size_bytes": int(prediction_stat.st_size),
        "sha256": prediction_freeze["private_prediction_stream_sha256"],
    }
    observations = _decode_ndjson(live_payload, surface="live_observations", record_cap=record_cap)
    authorization = _verify_attestation(
        attestation,
        hmac_key=hmac_key,
        identities=identities,
        contract=contract,
        expected_freeze=prediction_freeze,
    )

    # This is the first target-descriptor operation. Identity registration occurs
    # before reading, so a malformed target delivery is consumed and cannot retry.
    target_stat = _descriptor_stat(
        target_envelope_fd, access=os.O_RDONLY, surface="target_envelope"
    )
    target_identity = (int(target_stat.st_dev), int(target_stat.st_ino))
    if target_identity in _CONSUMED_TARGET_IDENTITIES:
        _refuse("repeated_score_or_target_delivery", "target_envelope")
    _CONSUMED_TARGET_IDENTITIES.add(target_identity)
    _, target_payload = _read_bounded(
        target_envelope_fd, surface="target_envelope", byte_cap=input_byte_cap
    )
    targets = _decode_json(target_payload, surface="target_envelope")
    if not isinstance(targets, Mapping):
        _refuse("target_delivery_mismatch")

    os.lseek(prediction_stream_fd, 0, os.SEEK_SET)
    result = streaming_score.score_records_after_verified_freeze(
        contract=contract,
        trial_records=trials,
        prediction_records=_iter_ndjson_descriptor(
            prediction_stream_fd,
            surface="prediction_stream",
            byte_cap=input_byte_cap,
            record_cap=record_cap,
        ),
        live_observation_records=observations,
        verified_freeze=prediction_freeze,
        authorization=authorization,
        delivered_targets=targets,
    )
    score_only._assert_aggregate_private(result)
    aggregate = {
        "schema_name": OUTPUT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": str(contract["gate_id"]),
        "score": result,
        "target_delivery_count": 1,
        "score_count": 1,
        "post_target_updates": 0,
        "contains_row_level_output": False,
        "generated_only": True,
        "scientific_claim_established": False,
        "prediction_streaming": {
            "passes": 2,
            "maximum_prediction_rows_buffered": streaming_score.MAXIMUM_PREDICTION_ROWS_BUFFERED,
            "complete_prediction_records_materialized": False,
        },
    }
    score_only._assert_aggregate_private(aggregate)
    _write_canonical(aggregate_output_fd, aggregate, byte_cap=output_byte_cap)
    return aggregate


def descriptor_fd_main(
    *,
    contract_fd: int,
    trial_manifest_fd: int,
    prediction_stream_fd: int,
    freeze_attestation_fd: int,
    target_envelope_fd: int,
    live_observations_fd: int,
    aggregate_output_fd: int,
    hmac_key_fd: int,
    input_byte_cap: int = DEFAULT_INPUT_BYTE_CAP,
    output_byte_cap: int = DEFAULT_OUTPUT_BYTE_CAP,
    record_cap: int = DEFAULT_RECORD_CAP,
) -> dict[str, Any]:
    """Read the invocation key from one narrow descriptor, then score once."""

    _, hmac_key = _read_bounded(
        hmac_key_fd,
        surface="freeze_hmac_key",
        byte_cap=64,
    )
    if len(hmac_key) != 32:
        _refuse("freeze_hmac_key_invalid")
    return descriptor_main(
        contract_fd=contract_fd,
        trial_manifest_fd=trial_manifest_fd,
        prediction_stream_fd=prediction_stream_fd,
        freeze_attestation_fd=freeze_attestation_fd,
        target_envelope_fd=target_envelope_fd,
        live_observations_fd=live_observations_fd,
        aggregate_output_fd=aggregate_output_fd,
        hmac_key=hmac_key,
        input_byte_cap=input_byte_cap,
        output_byte_cap=output_byte_cap,
        record_cap=record_cap,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="COMM-P0 generated descriptor-only score worker")
    for name in (
        "contract-fd",
        "trial-manifest-fd",
        "prediction-stream-fd",
        "freeze-attestation-fd",
        "target-envelope-fd",
        "live-observations-fd",
        "aggregate-output-fd",
        "hmac-key-fd",
    ):
        parser.add_argument(f"--{name}", type=int, required=True)
    parser.add_argument("--input-byte-cap", type=int, default=DEFAULT_INPUT_BYTE_CAP)
    parser.add_argument("--output-byte-cap", type=int, default=DEFAULT_OUTPUT_BYTE_CAP)
    parser.add_argument("--record-cap", type=int, default=DEFAULT_RECORD_CAP)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    descriptor_fd_main(
        contract_fd=arguments.contract_fd,
        trial_manifest_fd=arguments.trial_manifest_fd,
        prediction_stream_fd=arguments.prediction_stream_fd,
        freeze_attestation_fd=arguments.freeze_attestation_fd,
        target_envelope_fd=arguments.target_envelope_fd,
        live_observations_fd=arguments.live_observations_fd,
        aggregate_output_fd=arguments.aggregate_output_fd,
        hmac_key_fd=arguments.hmac_key_fd,
        input_byte_cap=arguments.input_byte_cap,
        output_byte_cap=arguments.output_byte_cap,
        record_cap=arguments.record_cap,
    )
    return 0


def capability_audit() -> dict[str, Any]:
    """Describe this worker's intentionally narrow capability surface."""

    return {
        "standard_library_only_except_pure_score_module": True,
        "accepts_paths": False,
        "preopened_descriptor_only": True,
        "fit_or_model_capability": False,
        "subprocess_capability": False,
        "network_capability": False,
        "row_level_output_capability": False,
        "official_qualification_executed": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
