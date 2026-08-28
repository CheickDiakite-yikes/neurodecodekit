"""Descriptor-only model worker for the generated COMM-P0 qualification.

The worker receives target-free feature rows plus labels for source participants
only. It never receives TrialPlan objects, held-out labels, target-vault state,
filesystem paths, activation state, or scorer capabilities.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import stat
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any, TextIO

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical


SCHEMA_NAME = "neurodecodekit.comm_p0_generated_model_worker"
SCHEMA_VERSION = "0.1.0"
FEATURE_KEYS = frozenset(
    {
        "item_id",
        "cohort_id",
        "participant_id",
        "endpoint",
        "phase",
        "central",
        "posterior",
        "eog",
        "oral_emg",
        "microphone",
        "cue",
        "timing",
        "prechoice",
        "language",
    }
)
FORBIDDEN_CAPABILITY_KEYS = frozenset(
    {
        "trial_index",
        "role",
        "duration_seconds",
        "intention_window_start_seconds",
        "intention_window_stop_seconds",
        "cue_code",
        "commitment",
        "target",
        "label",
        "target_key",
        "target_vault",
        "activation",
        "prediction_freeze_green",
        "score_count",
    }
)


def _validate_descriptor(fd: int, *, access: int) -> None:
    try:
        metadata = os.fstat(fd)
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    except OSError as exc:
        raise core.CommP0GeneratedRefusal("filesystem_object_type_violation") from exc
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or flags & os.O_ACCMODE != access
    ):
        raise core.CommP0GeneratedRefusal("filesystem_object_type_violation")


def _read_json_lines(stream: TextIO, *, byte_cap: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    observed = 0
    for raw_line in stream:
        observed += len(raw_line.encode("utf-8"))
        if observed > byte_cap:
            raise core.CommP0GeneratedRefusal("private_derivative_cap_breach")
        try:
            value = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise core.CommP0GeneratedRefusal(
                "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
            ) from exc
        if not isinstance(value, dict):
            raise core.CommP0GeneratedRefusal(
                "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
            )
        records.append(value)
    return records


def _feature_rows(records: Sequence[Mapping[str, Any]]) -> tuple[numerical.FeatureRow, ...]:
    rows = []
    item_ids: set[str] = set()
    for record in records:
        if set(record) != FEATURE_KEYS or set(record) & FORBIDDEN_CAPABILITY_KEYS:
            raise core.CommP0GeneratedRefusal(
                "target_exposed_to_decoder_operator_freezer_or_language_context"
            )
        core.assert_target_free(record)
        item_id = str(record["item_id"])
        if item_id in item_ids:
            raise core.CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
        item_ids.add(item_id)
        rows.append(
            numerical.FeatureRow(
                item_id=item_id,
                cohort_id=str(record["cohort_id"]),
                participant_id=str(record["participant_id"]),
                endpoint=str(record["endpoint"]),
                phase=str(record["phase"]),
                central=tuple(float(value) for value in record["central"]),
                posterior=tuple(float(value) for value in record["posterior"]),
                eog=tuple(float(value) for value in record["eog"]),
                oral_emg=tuple(float(value) for value in record["oral_emg"]),
                microphone=tuple(float(value) for value in record["microphone"]),
                cue=tuple(float(value) for value in record["cue"]),
                timing=tuple(float(value) for value in record["timing"]),
                prechoice=tuple(float(value) for value in record["prechoice"]),
                language=tuple(float(value) for value in record["language"]),
            )
        )
    return tuple(rows)


def _source_labels(
    records: Sequence[Mapping[str, Any]],
    *,
    feature_rows: Sequence[numerical.FeatureRow],
    held_out_participant: str,
) -> dict[str, int]:
    labels: dict[str, int] = {}
    participants = {row.participant_id for row in feature_rows}
    for record in records:
        if set(record) != {"item_id", "participant_id", "source_command_index"}:
            raise core.CommP0GeneratedRefusal(
                "target_exposed_to_decoder_operator_freezer_or_language_context"
            )
        item_id = str(record["item_id"])
        participant_id = str(record["participant_id"])
        value = record["source_command_index"]
        if (
            participant_id == held_out_participant
            or participant_id not in participants
            or isinstance(value, bool)
            or int(value) not in range(len(core.COMMANDS))
            or item_id in labels
        ):
            raise core.CommP0GeneratedRefusal(
                "held_out_participant_fit_threshold_or_adaptation"
            )
        labels[item_id] = int(value)
    expected = {
        row.item_id for row in feature_rows if row.participant_id != held_out_participant
    }
    if set(labels) != expected:
        raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")
    return labels


def _append_prediction_lines(
    stream: TextIO,
    rows: Sequence[numerical.FeatureRow],
    condition: str,
    probabilities: Any,
) -> int:
    count = 0
    for row, probability in zip(rows, probabilities, strict=True):
        record = {
            "record_type": "prediction",
            "item_id": row.item_id,
            "cohort_id": row.cohort_id,
            "participant_id": row.participant_id,
            "endpoint": row.endpoint,
            "phase": row.phase,
            "condition": condition,
            "probabilities": list(core.validate_probability_vector(probability.tolist())),
        }
        core.assert_target_free(record)
        stream.write(core.canonical_json_bytes(record).decode("utf-8"))
        count += 1
    return count


def run_fold(
    feature_records: Sequence[Mapping[str, Any]],
    label_records: Sequence[Mapping[str, Any]],
    contract: Mapping[str, Any],
    *,
    held_out_participant: str,
    output: TextIO,
) -> dict[str, int]:
    """Fit one source-only fold and stream only held-out predictions."""

    numerical.assert_single_thread_environment()
    if tuple(contract.get("conditions", ())) != (
        "equal_prior",
        "source_class_prior",
        *numerical.NONPRIOR_CONDITIONS,
    ):
        raise core.CommP0GeneratedRefusal(
            "required_control_condition_missing_duplicated_or_substituted"
        )
    rows = _feature_rows(feature_records)
    cohorts = {row.cohort_id for row in rows}
    if len(cohorts) != 1:
        raise core.CommP0GeneratedRefusal("discovery_replication_identity_overlap")
    participants = sorted({row.participant_id for row in rows})
    if held_out_participant not in participants or len(participants) < 3:
        raise core.CommP0GeneratedRefusal("cohort_cardinality_or_replacement_rule_violation")
    labels = _source_labels(
        label_records,
        feature_rows=rows,
        held_out_participant=held_out_participant,
    )
    source_participants = [value for value in participants if value != held_out_participant]
    calibration_ids = numerical._calibration_participants(source_participants)
    fit_rows = [
        row
        for row in rows
        if row.participant_id in source_participants
        and row.participant_id not in calibration_ids
    ]
    calibration_rows = [row for row in rows if row.participant_id in calibration_ids]
    held_rows = [row for row in rows if row.participant_id == held_out_participant]
    if not fit_rows or not calibration_rows or not held_rows:
        raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")

    np = numerical._np()
    fit_y = np.asarray([labels[row.item_id] for row in fit_rows], dtype="int64")
    calibration_y = np.asarray(
        [labels[row.item_id] for row in calibration_rows], dtype="int64"
    )
    counts = Counter(int(value) for value in fit_y.tolist())
    if set(counts) != set(range(len(core.COMMANDS))):
        raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")

    fit_peripheral = numerical._peripheral(fit_rows)
    calibration_peripheral = numerical._peripheral(calibration_rows)
    held_peripheral = numerical._peripheral(held_rows)
    residualizers = numerical._fit_endpoint_residualizers(
        fit_rows, fit_peripheral, numerical._matrix(fit_rows, "central")
    )
    fit_residual = numerical._residualize_by_endpoint(
        fit_rows, residualizers, fit_peripheral, numerical._matrix(fit_rows, "central")
    )
    calibration_residual = numerical._residualize_by_endpoint(
        calibration_rows,
        residualizers,
        calibration_peripheral,
        numerical._matrix(calibration_rows, "central"),
    )
    held_residual = numerical._residualize_by_endpoint(
        held_rows,
        residualizers,
        held_peripheral,
        numerical._matrix(held_rows, "central"),
    )
    fit_deranged = numerical._derange_by_class(fit_rows, fit_residual, fit_y)

    ledger = {
        "prior_fits": 0,
        "residualizer_fits": 2,
        "classifier_fits": 0,
        "temperature_calibration_fits": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "prediction_rows": 0,
        "target_deliveries": 0,
        "scores": 0,
        "post_target_updates": 0,
    }
    header = {
        "record_type": "fold_header",
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "gate_id": core.GATE_ID,
        "cohort_id": next(iter(cohorts)),
        "held_out_participant": held_out_participant,
        "source_participants": len(source_participants),
        "held_out_labels_received": 0,
        "trial_plan_objects_received": 0,
        "target_vault_capabilities_received": 0,
    }
    output.write(core.canonical_json_bytes(header).decode("utf-8"))

    equal = np.full((len(held_rows), len(core.COMMANDS)), 0.25, dtype="float64")
    ledger["prediction_rows"] += _append_prediction_lines(
        output, held_rows, "equal_prior", equal
    )
    ledger["model_inference_runs"] += 1
    ledger["prediction_sets"] += len(core.ENDPOINTS)
    prior = np.asarray([counts[index] for index in range(4)], dtype="float64")
    prior /= prior.sum()
    ledger["prior_fits"] += 1
    ledger["prediction_rows"] += _append_prediction_lines(
        output,
        held_rows,
        "source_class_prior",
        np.tile(prior, (len(held_rows), 1)),
    )
    ledger["model_inference_runs"] += 1
    ledger["prediction_sets"] += len(core.ENDPOINTS)

    for condition in numerical.NONPRIOR_CONDITIONS:
        fit_x = numerical._condition_matrix(condition, fit_rows, fit_residual, fit_deranged)
        calibration_x = numerical._condition_matrix(
            condition,
            calibration_rows,
            calibration_residual,
            calibration_residual,
        )
        held_x = numerical._condition_matrix(
            condition, held_rows, held_residual, held_residual
        )
        scaler, model = numerical._fit_classifier(fit_x, fit_y)
        ledger["classifier_fits"] += 1
        calibration_probabilities = model.predict_proba(scaler.transform(calibration_x))
        temperature = numerical._temperature_fit(
            calibration_probabilities, calibration_y
        )
        ledger["temperature_calibration_fits"] += 1
        held_probabilities = numerical._apply_temperature(
            model.predict_proba(scaler.transform(held_x)), temperature
        )
        ledger["prediction_rows"] += _append_prediction_lines(
            output, held_rows, condition, held_probabilities
        )
        ledger["model_inference_runs"] += 1
        ledger["prediction_sets"] += len(core.ENDPOINTS)

    trailer = {
        "record_type": "fold_ledger",
        "schema_name": SCHEMA_NAME,
        "held_out_participant": held_out_participant,
        **ledger,
    }
    output.write(core.canonical_json_bytes(trailer).decode("utf-8"))
    output.flush()
    return ledger


def _load_contract(stream: TextIO) -> dict[str, Any]:
    try:
        value = json.load(stream)
    except json.JSONDecodeError as exc:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        ) from exc
    if not isinstance(value, dict) or value.get("gate_id") != core.GATE_ID:
        raise core.CommP0GeneratedRefusal(
            "protocol_model_threshold_vocabulary_prior_or_code_hash_drift"
        )
    return value


def descriptor_main(
    *,
    feature_fd: int,
    label_fd: int,
    contract_fd: int,
    output_fd: int,
    held_out_participant: str,
    byte_cap: int,
) -> int:
    _validate_descriptor(feature_fd, access=os.O_RDONLY)
    _validate_descriptor(label_fd, access=os.O_RDONLY)
    _validate_descriptor(contract_fd, access=os.O_RDONLY)
    _validate_descriptor(output_fd, access=os.O_WRONLY)
    with (
        os.fdopen(feature_fd, "r", encoding="utf-8", closefd=True) as feature_stream,
        os.fdopen(label_fd, "r", encoding="utf-8", closefd=True) as label_stream,
        os.fdopen(contract_fd, "r", encoding="utf-8", closefd=True) as contract_stream,
        os.fdopen(output_fd, "w", encoding="utf-8", closefd=True) as output_stream,
    ):
        feature_records = _read_json_lines(feature_stream, byte_cap=byte_cap)
        label_records = _read_json_lines(label_stream, byte_cap=byte_cap)
        contract = _load_contract(contract_stream)
        run_fold(
            feature_records,
            label_records,
            contract,
            held_out_participant=held_out_participant,
            output=output_stream,
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="COMM-P0 descriptor-only model worker")
    parser.add_argument("--feature-fd", type=int, required=True)
    parser.add_argument("--label-fd", type=int, required=True)
    parser.add_argument("--contract-fd", type=int, required=True)
    parser.add_argument("--output-fd", type=int, required=True)
    parser.add_argument("--held-out-participant", required=True)
    parser.add_argument("--byte-cap", type=int, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    return descriptor_main(
        feature_fd=arguments.feature_fd,
        label_fd=arguments.label_fd,
        contract_fd=arguments.contract_fd,
        output_fd=arguments.output_fd,
        held_out_participant=arguments.held_out_participant,
        byte_cap=arguments.byte_cap,
    )


if __name__ == "__main__":
    raise SystemExit(main())
