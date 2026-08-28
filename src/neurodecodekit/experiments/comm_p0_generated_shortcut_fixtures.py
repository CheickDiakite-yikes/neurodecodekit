"""Deterministic numerical shortcut fixtures for generated-only COMM-P0-G.

Each route places the fictional command in exactly one generated surface, then
runs the existing participant-held-out model worker and aggregate scorer.  The
model receives target-free feature records and source-participant labels only.
Nothing in this module can read a path, contact a network, or operate a device.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from io import StringIO
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_model_worker as model_worker
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical
from neurodecodekit.experiments import comm_p0_generated_scorer as scorer

SCHEMA_NAME = "neurodecodekit.comm_p0_generated_shortcut_fixtures"
SCHEMA_VERSION = "0.1.0"
PARTICIPANTS_PER_COHORT = 3
PUBLIC_OUTPUT_CAP_BYTES = 1_048_576
ROUTE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "route_id": "EEG_only_positive_mechanical",
        "injected_surface": "central",
        "diagnostic_condition": "central_EEG_only",
        "expected_neural_evidence_gate_pass": True,
    },
    {
        "route_id": "EOG_only_negative",
        "injected_surface": "eog",
        "diagnostic_condition": "EOG_only",
        "expected_neural_evidence_gate_pass": False,
    },
    {
        "route_id": "oral_EMG_only_negative",
        "injected_surface": "oral_emg",
        "diagnostic_condition": "oral_EMG_only",
        "expected_neural_evidence_gate_pass": False,
    },
    {
        "route_id": "microphone_only_negative",
        "injected_surface": "microphone",
        "diagnostic_condition": "microphone_only",
        "expected_neural_evidence_gate_pass": False,
    },
    {
        "route_id": "cue_only_negative",
        "injected_surface": "cue",
        "diagnostic_condition": "cue_only",
        "expected_neural_evidence_gate_pass": False,
    },
    {
        "route_id": "timing_only_negative",
        "injected_surface": "timing",
        "diagnostic_condition": "timing_only",
        "expected_neural_evidence_gate_pass": False,
    },
    {
        "route_id": "language_only_negative",
        "injected_surface": "language",
        "diagnostic_condition": "language_only",
        "expected_neural_evidence_gate_pass": False,
    },
)
_ROUTE_BY_ID = {str(spec["route_id"]): spec for spec in ROUTE_SPECS}
_COUNTER_KEYS = (
    "prior_fits",
    "residualizer_fits",
    "classifier_fits",
    "temperature_calibration_fits",
    "model_inference_runs",
    "prediction_sets",
    "prediction_rows",
    "target_deliveries",
    "scores",
    "post_target_updates",
)
_SURFACE_DIMENSIONS = {
    "central": 8,
    "posterior": 4,
    "eog": 4,
    "oral_emg": 4,
    "microphone": 4,
    "cue": 4,
    "timing": 4,
    "prechoice": 4,
    "language": 4,
}


@dataclass(frozen=True, slots=True)
class ShortcutRouteResult:
    route_id: str
    injected_surface: str
    diagnostic_condition: str
    expected_neural_evidence_gate_pass: bool
    neural_evidence_gate_pass: bool
    shortcut_control_identified: bool
    cohort_diagnostics: tuple[Mapping[str, Any], ...]
    counters: Mapping[str, int]
    prediction_stream_sha256: str
    aggregate_score_sha256: str
    source_label_rows_delivered: int
    held_out_label_rows_delivered: int
    model_received_trial_plan_objects: int
    model_received_target_vault_capabilities: int

    def public_record(self) -> dict[str, Any]:
        value = asdict(self)
        core.assert_target_free(value)
        return value


@dataclass(frozen=True, slots=True)
class ShortcutMatrixResult:
    routes: tuple[ShortcutRouteResult, ...]
    counters: Mapping[str, int]
    deterministic_payload_sha256: str
    runtime_seconds: float
    peak_process_rss_bytes: int
    public_output_bytes: int
    CPU_threads: int
    workers: int
    numerical_jobs: int
    network_bytes: int
    real_data_reads: int
    device_operations: int
    retained_generated_payload_bytes: int

    def deterministic_record(self) -> dict[str, Any]:
        return {
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "gate_id": core.GATE_ID,
            "routes": [route.public_record() for route in self.routes],
            "counters": dict(self.counters),
            "CPU_threads": self.CPU_threads,
            "workers": self.workers,
            "numerical_jobs": self.numerical_jobs,
            "network_bytes": self.network_bytes,
            "real_data_reads": self.real_data_reads,
            "device_operations": self.device_operations,
            "retained_generated_payload_bytes": self.retained_generated_payload_bytes,
            "scientific_value": False,
        }

    def public_record(self) -> dict[str, Any]:
        value = self.deterministic_record()
        value.update(
            {
                "deterministic_payload_sha256": self.deterministic_payload_sha256,
                "runtime_seconds": self.runtime_seconds,
                "peak_process_rss_bytes": self.peak_process_rss_bytes,
                "public_output_bytes": self.public_output_bytes,
            }
        )
        core.assert_target_free(value)
        return value


def _peak_rss_bytes() -> int:
    observed = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return observed if sys.platform == "darwin" else observed * 1024


def validate_route_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Require one exact registered route; reject malformed or substituted routes."""

    if not isinstance(spec, Mapping) or set(spec) != {
        "route_id",
        "injected_surface",
        "diagnostic_condition",
        "expected_neural_evidence_gate_pass",
    }:
        raise core.CommP0GeneratedRefusal(
            "required_control_condition_missing_duplicated_or_substituted"
        )
    route_id = str(spec.get("route_id", ""))
    expected = _ROUTE_BY_ID.get(route_id)
    if expected is None or dict(spec) != expected:
        raise core.CommP0GeneratedRefusal(
            "required_control_condition_missing_duplicated_or_substituted", route_id
        )
    return dict(expected)


def _noise(route_id: str, item_id: str, surface: str, length: int) -> tuple[float, ...]:
    values = []
    for index in range(length):
        digest = hashlib.sha256(
            f"COMM-P0-G-shortcut:{route_id}:{item_id}:{surface}:{index}".encode()
        ).digest()
        unit = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
        values.append((2.0 * unit - 1.0) * 0.025)
    return tuple(values)


def _surface_vector(
    route_id: str,
    item_id: str,
    surface: str,
    command_index: int,
) -> tuple[float, ...]:
    length = _SURFACE_DIMENSIONS[surface]
    noise = _noise(route_id, item_id, surface, length)
    if _ROUTE_BY_ID[route_id]["injected_surface"] != surface:
        return noise
    signal = [0.0] * length
    signal[command_index] = 2.0
    return tuple(signal[index] + noise[index] for index in range(length))


def _opaque_trial_rows(route_id: str, contract: Mapping[str, Any]) -> tuple[core.TrialPlan, ...]:
    vault = core.GeneratedTargetVault(hashlib.sha256(f"{route_id}:target-vault".encode()).digest())
    plans = core.generate_trial_plan(contract, vault)
    selected: dict[str, set[str]] = {}
    for cohort_id in core.COHORTS:
        selected[cohort_id] = set(
            sorted(
                {
                    row.participant_id
                    for row in plans
                    if row.cohort_id == cohort_id and row.endpoint in core.ENDPOINTS
                }
            )[:PARTICIPANTS_PER_COHORT]
        )
    rows = []
    for row in plans:
        if row.participant_id not in selected[row.cohort_id]:
            continue
        opaque_id = hashlib.sha256(f"{route_id}\0{row.item_id}".encode()).hexdigest()
        rows.append(replace(row, item_id=opaque_id))
    return tuple(rows)


def build_feature_records(
    spec: Mapping[str, Any], trial_rows: Sequence[core.TrialPlan]
) -> tuple[dict[str, Any], ...]:
    """Build target-free model features from one isolated procedural source."""

    exact = validate_route_spec(spec)
    route_id = str(exact["route_id"])
    records = []
    for row in trial_rows:
        if row.endpoint not in core.ENDPOINTS:
            continue
        # The latent command remains inside this generated fixture-producer boundary.
        command = numerical._fixture_command(row)
        feature = numerical.FeatureRow(
            item_id=row.item_id,
            cohort_id=row.cohort_id,
            participant_id=row.participant_id,
            endpoint=row.endpoint,
            phase=row.phase,
            central=_surface_vector(route_id, row.item_id, "central", command),
            posterior=_surface_vector(route_id, row.item_id, "posterior", command),
            eog=_surface_vector(route_id, row.item_id, "eog", command),
            oral_emg=_surface_vector(route_id, row.item_id, "oral_emg", command),
            microphone=_surface_vector(route_id, row.item_id, "microphone", command),
            cue=_surface_vector(route_id, row.item_id, "cue", command),
            timing=_surface_vector(route_id, row.item_id, "timing", command),
            prechoice=_surface_vector(route_id, row.item_id, "prechoice", command),
            language=_surface_vector(route_id, row.item_id, "language", command),
        )
        record = asdict(feature)
        core.assert_target_free(record)
        records.append(record)
    validate_feature_records(records)
    return tuple(records)


def validate_feature_records(records: Sequence[Mapping[str, Any]]) -> None:
    """Reject malformed, nonfinite, duplicate, or capability-bearing features."""

    rows = model_worker._feature_rows(records)
    if not rows:
        raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")
    for row in rows:
        for surface, length in _SURFACE_DIMENSIONS.items():
            values = getattr(row, surface)
            if len(values) != length or any(not math.isfinite(value) for value in values):
                raise core.CommP0GeneratedRefusal(
                    "prediction_probability_nonfinite_or_sum_mismatch", surface
                )


def _prediction_from_record(record: Mapping[str, Any]) -> numerical.CompactPrediction:
    return numerical.CompactPrediction(
        item_id=str(record["item_id"]),
        cohort_id=str(record["cohort_id"]),
        participant_id=str(record["participant_id"]),
        endpoint=str(record["endpoint"]),
        phase=str(record["phase"]),
        condition=str(record["condition"]),
        probabilities=core.validate_probability_vector(record["probabilities"]),
    )


def _run_models(
    feature_records: Sequence[Mapping[str, Any]],
    trial_rows: Sequence[core.TrialPlan],
    contract: Mapping[str, Any],
) -> tuple[tuple[numerical.CompactPrediction, ...], dict[str, int], int]:
    features_by_cohort: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    trial_by_item = {row.item_id: row for row in trial_rows if row.endpoint in core.ENDPOINTS}
    for record in feature_records:
        features_by_cohort[str(record["cohort_id"])].append(record)
    predictions: list[numerical.CompactPrediction] = []
    counters: Counter[str] = Counter()
    source_label_rows = 0
    for cohort_id in core.COHORTS:
        cohort_features = features_by_cohort[cohort_id]
        participants = sorted({str(row["participant_id"]) for row in cohort_features})
        if len(participants) != PARTICIPANTS_PER_COHORT:
            raise core.CommP0GeneratedRefusal("cohort_cardinality_or_replacement_rule_violation")
        for held_out in participants:
            labels = [
                {
                    "item_id": item_id,
                    "participant_id": trial.participant_id,
                    "source_command_index": numerical._fixture_command(trial),
                }
                for item_id, trial in trial_by_item.items()
                if trial.cohort_id == cohort_id and trial.participant_id != held_out
            ]
            source_label_rows += len(labels)
            output = StringIO()
            ledger = model_worker.run_fold(
                cohort_features,
                labels,
                contract,
                held_out_participant=held_out,
                output=output,
            )
            counters.update(ledger)
            records = [json.loads(line) for line in output.getvalue().splitlines()]
            header = records[0]
            if (
                header.get("held_out_labels_received") != 0
                or header.get("trial_plan_objects_received") != 0
                or header.get("target_vault_capabilities_received") != 0
            ):
                raise core.CommP0GeneratedRefusal(
                    "target_exposed_to_decoder_operator_freezer_or_language_context"
                )
            predictions.extend(
                _prediction_from_record(record)
                for record in records
                if record.get("record_type") == "prediction"
            )
    return tuple(predictions), {key: int(counters[key]) for key in _COUNTER_KEYS}, source_label_rows


def _condition_metrics(
    rows: Sequence[core.TrialPlan],
    predictions: Sequence[numerical.CompactPrediction],
    condition: str,
) -> tuple[float, float]:
    index = {(row.item_id, row.condition): row for row in predictions}
    by_participant: dict[str, list[core.TrialPlan]] = defaultdict(list)
    for row in rows:
        if row.endpoint == "free_choice_intend" and row.phase == "shadow":
            by_participant[row.participant_id].append(row)
    accuracies = []
    losses = []
    for participant_rows in by_participant.values():
        commands = [scorer._target_for_trial(row) for row in participant_rows]
        probabilities = [index[(row.item_id, condition)].probabilities for row in participant_rows]
        accuracies.append(scorer._balanced_accuracy(commands, probabilities))
        losses.append(scorer._log_loss(commands, probabilities))
    return sum(accuracies) / len(accuracies), sum(losses) / len(losses)


def _cohort_diagnostics(
    trial_rows: Sequence[core.TrialPlan],
    predictions: Sequence[numerical.CompactPrediction],
    contract: Mapping[str, Any],
    diagnostic_condition: str,
) -> tuple[dict[str, Any], ...]:
    index = scorer._prediction_index(predictions)
    spec = contract["participant_first_scoring"]
    diagnostics = []
    for cohort_id in core.COHORTS:
        rows = [
            row
            for row in trial_rows
            if row.cohort_id == cohort_id
            and row.endpoint == "free_choice_intend"
            and row.phase == "shadow"
        ]
        by_participant: dict[str, list[core.TrialPlan]] = defaultdict(list)
        for row in rows:
            by_participant[row.participant_id].append(row)
        metrics = {
            participant: scorer._participant_metrics(participant_rows, index, contract)
            for participant, participant_rows in by_participant.items()
        }
        summary = scorer._general_participant_summary(metrics, contract)
        positive_required = math.ceil(
            len(metrics)
            * int(spec["positive_participants_minimum"])
            / int(spec["complete_participants_denominator"])
        )
        engineering_pass = bool(
            summary["mean_margin_nats_per_item"] >= float(spec["mean_margin_nats_per_item_minimum"])
            and summary["positive_participants"] >= positive_required
            and summary["mean_balanced_accuracy_margin"]
            >= float(spec["balanced_accuracy_margin_minimum"])
        )
        diagnostic_ba, diagnostic_ll = _condition_metrics(rows, predictions, diagnostic_condition)
        equal_ba, _ = _condition_metrics(rows, predictions, "equal_prior")
        diagnostics.append(
            {
                "cohort_id": cohort_id,
                "participant_count": len(metrics),
                "mean_primary_margin_nats_per_item": summary["mean_margin_nats_per_item"],
                "positive_participants": summary["positive_participants"],
                "positive_participants_required": positive_required,
                "mean_primary_balanced_accuracy_margin": summary["mean_balanced_accuracy_margin"],
                "diagnostic_balanced_accuracy": diagnostic_ba,
                "diagnostic_log_loss": diagnostic_ll,
                "diagnostic_margin_over_equal_prior": diagnostic_ba - equal_ba,
                "neural_evidence_engineering_gate_pass": engineering_pass,
                "inferential_gate_evaluated": False,
            }
        )
    return tuple(diagnostics)


def run_shortcut_route(spec: Mapping[str, Any], contract: Mapping[str, Any]) -> ShortcutRouteResult:
    """Execute one fixed numerical route and return aggregate routing evidence."""

    numerical.assert_single_thread_environment()
    exact = validate_route_spec(spec)
    route_id = str(exact["route_id"])
    trial_rows = _opaque_trial_rows(route_id, contract)
    feature_records = build_feature_records(exact, trial_rows)
    predictions, counters, source_label_rows = _run_models(feature_records, trial_rows, contract)
    expected_rows = PARTICIPANTS_PER_COHORT * len(core.COHORTS) * 128 * 17
    expected_sets = PARTICIPANTS_PER_COHORT * len(core.COHORTS) * 17 * len(core.ENDPOINTS)
    freeze = core.build_prediction_freeze(
        (prediction.public_record() for prediction in predictions),
        expected_rows=expected_rows,
        expected_sets=expected_sets,
    )
    diagnostics = _cohort_diagnostics(
        trial_rows,
        predictions,
        contract,
        str(exact["diagnostic_condition"]),
    )
    # The six negative fixtures are expected to fail neural/live acceptance. Score
    # their frozen shadow probabilities with the production participant-first
    # primitives instead of asking the live acceptance router to accept them.
    counters["target_deliveries"] = len(core.COHORTS)
    counters["scores"] = len(core.COHORTS)
    counters["post_target_updates"] = 0
    neural_pass = all(bool(row["neural_evidence_engineering_gate_pass"]) for row in diagnostics)
    control_identified = all(
        float(row["diagnostic_balanced_accuracy"]) >= 0.80
        and float(row["diagnostic_margin_over_equal_prior"]) >= 0.50
        for row in diagnostics
    )
    expected_pass = bool(exact["expected_neural_evidence_gate_pass"])
    if neural_pass != expected_pass or not control_identified:
        raise core.CommP0GeneratedRefusal("shortcut_fixture_or_control_routing_failure", route_id)
    return ShortcutRouteResult(
        route_id=route_id,
        injected_surface=str(exact["injected_surface"]),
        diagnostic_condition=str(exact["diagnostic_condition"]),
        expected_neural_evidence_gate_pass=expected_pass,
        neural_evidence_gate_pass=neural_pass,
        shortcut_control_identified=control_identified,
        cohort_diagnostics=diagnostics,
        counters=counters,
        prediction_stream_sha256=numerical.prediction_stream_sha256(predictions),
        aggregate_score_sha256=core.sha256_json(
            {
                "prediction_freeze_sha256": core.sha256_json(freeze),
                "cohort_diagnostics": list(diagnostics),
                "target_deliveries": len(core.COHORTS),
                "scores": len(core.COHORTS),
                "post_target_updates": 0,
            }
        ),
        source_label_rows_delivered=source_label_rows,
        held_out_label_rows_delivered=0,
        model_received_trial_plan_objects=0,
        model_received_target_vault_capabilities=0,
    )


def run_shortcut_fixture_matrix(contract: Mapping[str, Any]) -> ShortcutMatrixResult:
    """Execute all seven routes once under the registered generated resource caps."""

    numerical.assert_single_thread_environment()
    started = time.perf_counter()
    routes = tuple(run_shortcut_route(spec, contract) for spec in ROUTE_SPECS)
    runtime = time.perf_counter() - started
    totals: Counter[str] = Counter()
    for route in routes:
        totals.update(route.counters)
    counters = {key: int(totals[key]) for key in _COUNTER_KEYS}
    deterministic = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "gate_id": core.GATE_ID,
        "routes": [route.public_record() for route in routes],
        "counters": counters,
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
        "network_bytes": 0,
        "real_data_reads": 0,
        "device_operations": 0,
        "retained_generated_payload_bytes": 0,
        "scientific_value": False,
    }
    deterministic_sha256 = core.sha256_json(deterministic)
    peak_rss = _peak_rss_bytes()
    preview = {
        **deterministic,
        "deterministic_payload_sha256": deterministic_sha256,
        "runtime_seconds": runtime,
        "peak_process_rss_bytes": peak_rss,
        "public_output_bytes": 0,
    }
    output_bytes = 0
    while True:
        preview["public_output_bytes"] = output_bytes
        measured = len(core.canonical_json_bytes(preview))
        if measured == output_bytes:
            break
        output_bytes = measured
    resource_caps = contract["resource_caps"]
    if runtime > float(resource_caps["wall_time_seconds"]) or output_bytes > min(
        PUBLIC_OUTPUT_CAP_BYTES, int(resource_caps["public_aggregate_output_bytes"])
    ):
        raise core.CommP0GeneratedRefusal("total_permission_or_free_space_floor_breach")
    return ShortcutMatrixResult(
        routes=routes,
        counters=counters,
        deterministic_payload_sha256=deterministic_sha256,
        runtime_seconds=runtime,
        peak_process_rss_bytes=peak_rss,
        public_output_bytes=output_bytes,
        CPU_threads=1,
        workers=1,
        numerical_jobs=1,
        network_bytes=0,
        real_data_reads=0,
        device_operations=0,
        retained_generated_payload_bytes=0,
    )


def thread_environment() -> dict[str, str]:
    """Return the exact environment required for a one-thread invocation."""

    return {name: "1" for name in numerical.THREAD_ENVIRONMENT}


def main() -> int:
    for name, value in thread_environment().items():
        os.environ[name] = value
    contract = core.load_contract()
    result = run_shortcut_fixture_matrix(contract)
    print(json.dumps(result.public_record(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
