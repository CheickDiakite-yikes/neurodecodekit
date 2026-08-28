"""Strict descriptor-only verifier for the full generated COMM-P0 FS3 rehearsal."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from neurodecodekit.experiments import comm_p0_generated_score_only as score_only
from neurodecodekit.experiments import comm_p0_generated_score_worker as score_worker
from neurodecodekit.experiments import comm_p0_generated_streaming_score as streaming_score
from neurodecodekit.experiments import comm_p0_generated_verifier_worker as legacy


SCHEMA_VERSION = "0.1.0"
GATE_ID = "COMM-P0-G-FS3-v0"
OUTPUT_SCHEMA = "neurodecodekit.comm_p0_generated_FS3_strict_verification"
EXPECTED_PREDICTION_PASSES = 2
EXPECTED_PREDICTION_ROWS = 91_392
EXPECTED_PREDICTION_SETS = 1_428
EXPECTED_ROWS_PER_SET = 64
EXPECTED_TARGET_DELIVERIES = 2
EXPECTED_SCORES = 2
STATIC_IDENTITY_SHA256 = (
    "99022366ce5aa59266d855ef9d4fd84c9cc7a1bf4f960c9398022b8e582a3771",
    "e9c5827495dd684fb95b2eed87b6ad61ef86994ee2845a92dda9be566ee7c3e5",
    "89e5ba2d10d9fa2af312e885922fb7bf7cdd54db7dc6f466bfe03d8a3d6a3531",
    "5b08692b79e0e1387f6045d93db407e4f96842335cddc4937bd2db9609c988ac",
    "c7e96abd52d86e988f0edbaaf2b6806977a9850b5be42e49d3714438306e35ab",
    "12bd07cf249c9730061aea22eef1675bbd89e721b0d833c6111f37907992e96a",
    "88d521251af07b454f99544236ed45583ffd804f7dabf8db7c7764b0f527cf12",
)
IDENTITY_BYTE_CAP = 1_048_576
STRICT_WORKER_ARTIFACT = (
    "src/neurodecodekit/experiments/comm_p0_generated_strict_verifier_worker.py"
)


def _refuse(family: str, detail: str | None = None) -> None:
    raise score_only.ScoreOnlyRefusal(f"FS3-{family}", detail)


def _read_identity(fd: int, *, expected_sha256: str, surface: str) -> bytes:
    before = os.fstat(fd)
    if before.st_nlink != 1:
        _refuse("identity_artifact_invalid", surface)
    _, payload = score_worker._read_bounded(
        fd, surface=surface, byte_cap=IDENTITY_BYTE_CAP
    )
    after = os.fstat(fd)
    if (
        after.st_dev != before.st_dev
        or after.st_ino != before.st_ino
        or after.st_size != before.st_size
        or after.st_nlink != 1
        or hashlib.sha256(payload).hexdigest() != expected_sha256
    ):
        _refuse("identity_artifact_invalid", surface)
    return payload


def _read_unbound_identity(fd: int, *, surface: str) -> bytes:
    before = os.fstat(fd)
    if before.st_nlink != 1:
        _refuse("identity_artifact_invalid", surface)
    _, payload = score_worker._read_bounded(
        fd, surface=surface, byte_cap=IDENTITY_BYTE_CAP
    )
    after = os.fstat(fd)
    if (
        after.st_dev != before.st_dev
        or after.st_ino != before.st_ino
        or after.st_size != before.st_size
        or after.st_nlink != 1
    ):
        _refuse("identity_artifact_invalid", surface)
    return payload


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(score_only.canonical_json_bytes(value)).hexdigest()


def _assert_loaded_capsule_identities(
    *, strict_worker_sha256: str
) -> None:
    capsule = os.environ.get("NDK_FS3_CAPSULE_DIR")
    if not capsule:
        _refuse("identity_artifact_invalid", "capsule_absent")
    capsule = os.path.realpath(capsule)
    modules = (
        (__import__(__name__, fromlist=["*"]), strict_worker_sha256),
        (legacy, STATIC_IDENTITY_SHA256[3]),
        (score_worker, STATIC_IDENTITY_SHA256[4]),
        (score_only, STATIC_IDENTITY_SHA256[5]),
        (streaming_score, STATIC_IDENTITY_SHA256[6]),
    )
    for module, expected in modules:
        module_path = os.path.realpath(str(module.__file__))
        if os.path.commonpath((capsule, module_path)) != capsule:
            _refuse("identity_artifact_invalid", "loaded_module_outside_capsule")
        descriptor = os.open(
            module_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            _read_identity(
                descriptor,
                expected_sha256=expected,
                surface="loaded_capsule_module",
            )
        finally:
            os.close(descriptor)


def _verify_identities(
    identity_fds: Sequence[int], *, expected_proof_sha256: str
) -> dict[str, Any]:
    if len(identity_fds) != len(STATIC_IDENTITY_SHA256) + 2:
        _refuse("identity_artifact_invalid", "allowlist_cardinality")
    observed = []
    for index, expected in enumerate(STATIC_IDENTITY_SHA256):
        payload = _read_identity(
            identity_fds[index],
            expected_sha256=expected,
            surface=f"static_identity_{index}",
        )
        observed.append(hashlib.sha256(payload).hexdigest())
    proof_payload = _read_unbound_identity(identity_fds[-1], surface="wrapper_proof")
    try:
        proof = json.loads(proof_payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise score_only.ScoreOnlyRefusal("FS3-identity_artifact_invalid") from exc
    if not isinstance(proof, Mapping):
        _refuse("identity_artifact_invalid", "wrapper_proof")
    canonical = dict(proof)
    supplied = canonical.pop("proof_sha256", None)
    if (
        supplied != expected_proof_sha256
        or _sha256_json(canonical) != expected_proof_sha256
    ):
        _refuse("identity_artifact_invalid", "wrapper_proof")
    artifacts = proof.get("implementation_artifacts")
    if not isinstance(artifacts, list):
        _refuse("identity_artifact_invalid", "wrapper_proof_artifacts")
    strict_rows = [
        row
        for row in artifacts
        if isinstance(row, Mapping) and row.get("path") == STRICT_WORKER_ARTIFACT
    ]
    if len(strict_rows) != 1 or not isinstance(strict_rows[0].get("sha256"), str):
        _refuse("identity_artifact_invalid", "strict_worker_proof_identity")
    strict_sha256 = str(strict_rows[0]["sha256"])
    strict_payload = _read_identity(
        identity_fds[-2],
        expected_sha256=strict_sha256,
        surface="strict_worker_identity",
    )
    _assert_loaded_capsule_identities(strict_worker_sha256=strict_sha256)
    observed.append(hashlib.sha256(strict_payload).hexdigest())
    observed.append(hashlib.sha256(proof_payload).hexdigest())
    return {
        "exact_identity_artifacts_verified": len(observed),
        "identity_set_sha256": _sha256_json(observed),
    }


def _assert_active_socket_guard() -> None:
    if "NDK_FS3_GUARD_DIR" not in os.environ:
        _refuse("model_or_forbidden_capability", "socket_guard_absent")
    try:
        socket.getaddrinfo("example.invalid", 443)
    except RuntimeError as exc:
        if "forbidden_operation_nonzero" not in str(exc):
            raise
    else:
        _refuse("model_or_forbidden_capability", "socket_guard_inactive")


def _audit_prediction_records(
    records: Iterable[Mapping[str, Any]],
    completed_passes: list[dict[str, int]],
) -> Iterable[Mapping[str, Any]]:
    """Count observed participant-condition-endpoint sets without retaining rows."""

    counts: dict[tuple[str, str, str], int] = {}
    total = 0
    for record in records:
        if not isinstance(record, Mapping):
            _refuse("exact_full_inventory_mismatch", "nonmapping_prediction")
        key = (
            str(record.get("participant_id", "")),
            str(record.get("condition", "")),
            str(record.get("endpoint", "")),
        )
        if not all(key):
            _refuse("exact_full_inventory_mismatch", "empty_set_key")
        counts[key] = counts.get(key, 0) + 1
        total += 1
        yield record
    if (
        total != EXPECTED_PREDICTION_ROWS
        or len(counts) != EXPECTED_PREDICTION_SETS
        or any(count != EXPECTED_ROWS_PER_SET for count in counts.values())
    ):
        _refuse("exact_full_inventory_mismatch", "observed_rows_per_set")
    completed_passes.append(
        {
            "rows": total,
            "sets": len(counts),
            "minimum_rows_per_set": min(counts.values(), default=0),
            "maximum_rows_per_set": max(counts.values(), default=0),
        }
    )


def descriptor_main(
    *,
    contract_fd: int,
    trial_manifest_fd: int,
    prediction_stream_fd: int,
    freeze_attestation_fd: int,
    target_envelope_fd: int,
    live_observations_fd: int,
    hmac_key_fd: int,
    producer_aggregate_fd: int,
    verifier_score_output_fd: int,
    verification_output_fd: int,
    identity_fds: Sequence[int],
    expected_proof_sha256: str,
    input_byte_cap: int,
    output_byte_cap: int,
    record_cap: int,
) -> dict[str, Any]:
    """Verify exact identities before invoking the frozen zero-model scorer."""

    _assert_active_socket_guard()
    identity = _verify_identities(
        identity_fds, expected_proof_sha256=expected_proof_sha256
    )
    completed_passes: list[dict[str, int]] = []
    original_iterator = score_worker._iter_ndjson_descriptor

    def audited_iterator(*args: Any, **kwargs: Any) -> Iterable[Mapping[str, Any]]:
        return _audit_prediction_records(
            original_iterator(*args, **kwargs), completed_passes
        )

    score_worker._iter_ndjson_descriptor = audited_iterator
    try:
        value = legacy.descriptor_main(
            contract_fd=contract_fd,
            trial_manifest_fd=trial_manifest_fd,
            prediction_stream_fd=prediction_stream_fd,
            freeze_attestation_fd=freeze_attestation_fd,
            target_envelope_fd=target_envelope_fd,
            live_observations_fd=live_observations_fd,
            hmac_key_fd=hmac_key_fd,
            producer_aggregate_fd=producer_aggregate_fd,
            verifier_score_output_fd=verifier_score_output_fd,
            verification_output_fd=verification_output_fd,
            input_byte_cap=input_byte_cap,
            output_byte_cap=output_byte_cap,
            record_cap=record_cap,
        )
    finally:
        score_worker._iter_ndjson_descriptor = original_iterator
    if (
        value.get("prediction_stream_validation_passes")
        != EXPECTED_PREDICTION_PASSES
        or value.get("prediction_rows") != EXPECTED_PREDICTION_ROWS
        or value.get("prediction_sets") != EXPECTED_PREDICTION_SETS
        or len(completed_passes) != EXPECTED_PREDICTION_PASSES
        or any(
            row
            != {
                "rows": EXPECTED_PREDICTION_ROWS,
                "sets": EXPECTED_PREDICTION_SETS,
                "minimum_rows_per_set": EXPECTED_ROWS_PER_SET,
                "maximum_rows_per_set": EXPECTED_ROWS_PER_SET,
            }
            for row in completed_passes
        )
        or value.get("target_deliveries") != EXPECTED_TARGET_DELIVERIES
        or value.get("scores") != EXPECTED_SCORES
        or value.get("post_target_updates") != 0
        or value.get("model_fits") != 0
        or value.get("transform_fits") != 0
        or value.get("model_inference_runs") != 0
        or value.get("prediction_sets_created") != 0
        or value.get("prediction_rows_created") != 0
        or value.get("parameter_updates") != 0
        or value.get("language_model_operations") != 0
    ):
        _refuse("exact_full_inventory_mismatch")
    quality = value.get("score", {}).get("prediction_quality", {})
    if (
        quality.get("assigned_prediction_rows") != EXPECTED_PREDICTION_ROWS
        or quality.get("present_prediction_rows") != EXPECTED_PREDICTION_ROWS
        or quality.get("valid_prediction_rows") != EXPECTED_PREDICTION_ROWS
        or quality.get("missing_prediction_rows_retained") != 0
        or quality.get("invalid_prediction_rows_retained") != 0
        or quality.get("rows_dropped") != 0
    ):
        _refuse("exact_full_inventory_mismatch")
    result = dict(value)
    result["schema_name"] = OUTPUT_SCHEMA
    result["identity_verification"] = identity
    result["physical_target_envelope_descriptors"] = 1
    result["observed_rows_per_prediction_set"] = EXPECTED_ROWS_PER_SET
    result["logical_target_partitions"] = [
        "discovery",
        "independent_replication",
    ]
    score_only._assert_aggregate_private(result)
    os.lseek(verification_output_fd, 0, os.SEEK_SET)
    os.ftruncate(verification_output_fd, 0)
    score_worker._write_canonical(
        verification_output_fd, result, byte_cap=output_byte_cap
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Internal strict generated-only COMM-P0 FS3 verifier"
    )
    for name in (
        "contract-fd",
        "trial-manifest-fd",
        "prediction-stream-fd",
        "freeze-attestation-fd",
        "target-envelope-fd",
        "live-observations-fd",
        "hmac-key-fd",
        "producer-aggregate-fd",
        "verifier-score-output-fd",
        "verification-output-fd",
    ):
        parser.add_argument(f"--{name}", type=int, required=True)
    parser.add_argument("--identity-fd", type=int, action="append", required=True)
    parser.add_argument("--expected-proof-sha256", required=True)
    parser.add_argument("--input-byte-cap", type=int, required=True)
    parser.add_argument("--output-byte-cap", type=int, required=True)
    parser.add_argument("--record-cap", type=int, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    descriptor_main(
        contract_fd=arguments.contract_fd,
        trial_manifest_fd=arguments.trial_manifest_fd,
        prediction_stream_fd=arguments.prediction_stream_fd,
        freeze_attestation_fd=arguments.freeze_attestation_fd,
        target_envelope_fd=arguments.target_envelope_fd,
        live_observations_fd=arguments.live_observations_fd,
        hmac_key_fd=arguments.hmac_key_fd,
        producer_aggregate_fd=arguments.producer_aggregate_fd,
        verifier_score_output_fd=arguments.verifier_score_output_fd,
        verification_output_fd=arguments.verification_output_fd,
        identity_fds=arguments.identity_fd,
        expected_proof_sha256=arguments.expected_proof_sha256,
        input_byte_cap=arguments.input_byte_cap,
        output_byte_cap=arguments.output_byte_cap,
        record_cap=arguments.record_cap,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
