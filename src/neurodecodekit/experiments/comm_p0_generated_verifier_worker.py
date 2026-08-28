"""Independent descriptor-only verifier/scorer for generated COMM-P0 FS3."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Mapping, Sequence
from typing import Any

from neurodecodekit.experiments import comm_p0_generated_score_only as score_only
from neurodecodekit.experiments import comm_p0_generated_score_worker as score_worker


SCHEMA_VERSION = "0.1.0"
GATE_ID = "COMM-P0-G-FS3-v0"
OUTPUT_SCHEMA = "neurodecodekit.comm_p0_generated_FS3_independent_verification"
PREDICTION_ROWS_PER_SET = 64


def _refuse(family: str, detail: str | None = None) -> None:
    raise score_only.ScoreOnlyRefusal(f"FS3-{family}", detail)


def _decode_aggregate(fd: int, *, surface: str, byte_cap: int) -> dict[str, Any]:
    _, payload = score_worker._read_bounded(fd, surface=surface, byte_cap=byte_cap)
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise score_only.ScoreOnlyRefusal("FS3-noncanonical_aggregate", surface) from exc
    if not isinstance(value, Mapping) or score_only.canonical_json_bytes(value) != payload:
        _refuse("noncanonical_aggregate", surface)
    score_only._assert_aggregate_private(value)
    return dict(value)


def _assert_model_free_capability() -> dict[str, Any]:
    audit = score_worker.capability_audit()
    required_true = {
        "standard_library_only_except_pure_score_module",
        "preopened_descriptor_only",
    }
    required_false = {
        "accepts_paths",
        "fit_or_model_capability",
        "subprocess_capability",
        "network_capability",
        "row_level_output_capability",
        "official_qualification_executed",
    }
    if any(audit.get(key) is not True for key in required_true) or any(
        audit.get(key) is not False for key in required_false
    ):
        _refuse("model_or_forbidden_capability")
    forbidden_loaded = sorted(
        name
        for name in sys.modules
        if name == "numpy"
        or name.startswith("numpy.")
        or name == "sklearn"
        or name.startswith("sklearn.")
        or name.endswith("comm_p0_generated_numerical")
        or name.endswith("comm_p0_generated_model_worker")
    )
    if forbidden_loaded:
        _refuse("model_or_forbidden_capability", forbidden_loaded[0])
    return dict(audit)


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
    input_byte_cap: int,
    output_byte_cap: int,
    record_cap: int,
) -> dict[str, Any]:
    """Independently stream-verify, rescore, and match one producer transcript."""

    capability = _assert_model_free_capability()
    producer = _decode_aggregate(
        producer_aggregate_fd,
        surface="producer_aggregate",
        byte_cap=output_byte_cap,
    )
    verifier = score_worker.descriptor_fd_main(
        contract_fd=contract_fd,
        trial_manifest_fd=trial_manifest_fd,
        prediction_stream_fd=prediction_stream_fd,
        freeze_attestation_fd=freeze_attestation_fd,
        target_envelope_fd=target_envelope_fd,
        live_observations_fd=live_observations_fd,
        aggregate_output_fd=verifier_score_output_fd,
        hmac_key_fd=hmac_key_fd,
        input_byte_cap=input_byte_cap,
        output_byte_cap=output_byte_cap,
        record_cap=record_cap,
    )
    producer_payload = score_only.canonical_json_bytes(producer)
    verifier_payload = score_only.canonical_json_bytes(verifier)
    if producer_payload != verifier_payload:
        _refuse("aggregate_score_mismatch")
    prediction_quality = verifier["score"]["prediction_quality"]
    prediction_rows = int(prediction_quality["present_prediction_rows"])
    if prediction_rows <= 0 or prediction_rows % PREDICTION_ROWS_PER_SET:
        _refuse("prediction_inventory_mismatch")
    result = {
        "schema_name": OUTPUT_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "verifier_worker_pid": os.getpid(),
        "producer_aggregate_sha256": hashlib.sha256(producer_payload).hexdigest(),
        "verifier_aggregate_sha256": hashlib.sha256(verifier_payload).hexdigest(),
        "aggregate_scores_exactly_match": True,
        "prediction_stream_validation_passes": int(
            verifier["prediction_streaming"]["passes"]
        ),
        "prediction_rows": prediction_rows,
        "prediction_sets": prediction_rows // PREDICTION_ROWS_PER_SET,
        "target_deliveries": int(verifier["target_delivery_count"]),
        "scores": int(verifier["score_count"]),
        "model_fits": 0,
        "transform_fits": 0,
        "model_inference_runs": 0,
        "threshold_or_calibration_selection_operations": 0,
        "prediction_sets_created": 0,
        "prediction_rows_created": 0,
        "parameter_updates": 0,
        "language_model_operations": 0,
        "post_target_updates": 0,
        "contains_row_level_output": False,
        "generated_only": True,
        "official_qualification": False,
        "scientific_claim_established": False,
        "capability_audit": capability,
    }
    score_only._assert_aggregate_private(result)
    score_worker._write_canonical(
        verification_output_fd,
        result,
        byte_cap=output_byte_cap,
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Internal generated-only COMM-P0 FS3 verifier worker"
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
        input_byte_cap=arguments.input_byte_cap,
        output_byte_cap=arguments.output_byte_cap,
        record_cap=arguments.record_cap,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
