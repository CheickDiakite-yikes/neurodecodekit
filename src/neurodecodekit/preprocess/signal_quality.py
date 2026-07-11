"""Bounded, synthetic-only signal readability and quality reports for RW2."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
import sys
import time
import warnings as python_warnings
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from neurodecodekit.datasets.local_intake import validate_intake_report


SCHEMA_NAME = "neurodecodekit-signal-quality"
SCHEMA_VERSION = "0.1.0"
AUDIT_SCHEMA_NAME = "neurodecodekit-signal-quality-audit"
FIXTURE_SCHEMA_NAME = "neurodecodekit-signal-quality-fixtures"
CONTRACT_SCHEMA_NAME = "neurodecodekit.signal_quality_contract"
ARTIFACT_JSON = "signal_quality.json"
ARTIFACT_MARKDOWN = "signal_quality.md"
ARTIFACT_AUDIT = "signal_quality.audit.json"

_MIB = 1024 * 1024
_EXPECTED_MNE_MINOR = (1, 12)
_DATA_CHANNEL_TYPES = {
    "eeg",
    "mag",
    "grad",
    "eog",
    "ecg",
    "emg",
    "seeg",
    "ecog",
    "dbs",
    "bio",
}
_NON_BRAIN_CHANNEL_TYPES = {"stim", "misc", "syst", "eyegaze", "pupil", "ref_meg"}
_SI_UNITS = {
    "eeg": "V",
    "eog": "V",
    "ecg": "V",
    "emg": "V",
    "seeg": "V",
    "ecog": "V",
    "dbs": "V",
    "bio": "V",
    "mag": "T",
    "grad": "T/m",
}
_TIME_METRICS = (
    "sample_count",
    "finite_fraction",
    "exact_zero_fraction",
    "adjacent_equal_fraction",
    "minimum",
    "percentile_01",
    "median",
    "percentile_99",
    "maximum",
    "median_absolute_deviation",
    "centered_rms",
    "peak_to_peak",
    "maximum_absolute_first_difference",
)
_BANDS = {
    "delta": (0.5, 4.0, False),
    "theta": (4.0, 8.0, False),
    "alpha": (8.0, 13.0, False),
    "beta": (13.0, 30.0, False),
    "low_gamma": (30.0, 45.0, True),
}
_FORBIDDEN_KEYS = {
    "target",
    "target_text",
    "targets",
    "label",
    "labels",
    "prediction",
    "predictions",
    "decoded_text",
    "waveform",
    "waveforms",
    "signal_values",
    "geometry_coordinates",
    "annotation_descriptions",
    "event_descriptions",
    "participant_rows",
    "subject_info",
    "device_serial_number",
}


@dataclass(frozen=True)
class SignalQualityLimits:
    """Frozen hard limits for one RW2 bounded synthetic inspection."""

    max_source_files: int = 256
    max_directory_depth: int = 8
    max_declared_source_bytes: int = 4 * 1024 * _MIB
    max_channels: int = 512
    max_windows: int = 3
    max_channel_sample_values: int = 4_194_304
    max_materialized_signal_array_bytes: int = 32 * _MIB
    min_samples_per_window: int = 128
    target_window_seconds: float = 4.0
    max_runtime_seconds: float = 30.0
    max_peak_rss_bytes: int = 1024 * _MIB
    max_output_bytes: int = 4 * _MIB

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive number.")
        integer_fields = {
            "max_source_files",
            "max_directory_depth",
            "max_declared_source_bytes",
            "max_channels",
            "max_windows",
            "max_channel_sample_values",
            "max_materialized_signal_array_bytes",
            "min_samples_per_window",
            "max_peak_rss_bytes",
            "max_output_bytes",
        }
        for name in integer_fields:
            if not isinstance(getattr(self, name), int):
                raise ValueError(f"{name} must be an integer.")


@dataclass(frozen=True)
class SignalQualityResult:
    """Deterministic RW2 report plus measurements kept out of its core hash."""

    report: dict[str, Any]
    runtime_sec: float
    peak_rss_bytes: int | None


def select_window_ranges(
    n_times: int,
    sfreq: float,
    n_channels: int,
    *,
    limits: SignalQualityLimits | None = None,
) -> list[tuple[int, int]]:
    """Select, clip, merge, and cap the three frozen RW2 windows."""

    limits = limits or SignalQualityLimits()
    if not isinstance(n_times, int) or n_times <= 0:
        raise ValueError("n_times must be a positive integer.")
    if not math.isfinite(sfreq) or sfreq <= 0:
        raise ValueError("sfreq must be positive and finite.")
    if not isinstance(n_channels, int) or n_channels <= 0:
        raise ValueError("n_channels must be a positive integer.")
    if n_channels > limits.max_channels:
        raise ValueError("channel_count_exceeds_registered_cap")

    half_width = max(1, int(round(limits.target_window_seconds * sfreq / 2.0)))
    proposed: list[tuple[int, int]] = []
    for fraction in (0.05, 0.5, 0.95)[: limits.max_windows]:
        center = int(round(fraction * n_times))
        start = max(0, center - half_width)
        stop = min(n_times, center + half_width)
        if stop > start:
            proposed.append((start, stop))

    deduplicated: list[tuple[int, int]] = []
    for start, stop in sorted(set(proposed)):
        if deduplicated and start < deduplicated[-1][1]:
            previous_start, previous_stop = deduplicated[-1]
            deduplicated[-1] = (previous_start, max(previous_stop, stop))
        else:
            deduplicated.append((start, stop))
    if not deduplicated:
        raise ValueError("no_valid_bounded_window")

    max_total_samples = limits.max_channel_sample_values // n_channels
    original_lengths = [stop - start for start, stop in deduplicated]
    if sum(original_lengths) > max_total_samples:
        low = limits.min_samples_per_window
        high = max(original_lengths)
        if max_total_samples < low * len(deduplicated):
            raise ValueError("bounded_windows_below_registered_minimum_samples")
        while low < high:
            candidate = (low + high + 1) // 2
            if sum(min(length, candidate) for length in original_lengths) <= max_total_samples:
                low = candidate
            else:
                high = candidate - 1
        target_length = low
        shortened: list[tuple[int, int]] = []
        for (start, stop), original_length in zip(deduplicated, original_lengths):
            length = min(original_length, target_length)
            center = (start + stop) // 2
            new_start = max(start, center - length // 2)
            new_stop = new_start + length
            if new_stop > stop:
                new_stop = stop
                new_start = stop - length
            shortened.append((new_start, new_stop))
        deduplicated = shortened

    if any(stop - start < limits.min_samples_per_window for start, stop in deduplicated):
        raise ValueError("bounded_windows_below_registered_minimum_samples")
    returned_values = n_channels * sum(stop - start for start, stop in deduplicated)
    if returned_values > limits.max_channel_sample_values:
        raise ValueError("channel_sample_value_cap_exceeded")
    return deduplicated


def canonical_payload_sha256(
    channel_names: list[str],
    windows: list[tuple[int, int]],
    values_by_window: list[Any],
    times_by_window: list[Any],
) -> str:
    """Hash canonical channel order, window bounds, float64 values, and times."""

    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - exercised through missing-extra path
        raise RuntimeError("RW2 signal inspection requires: pip install -e '.[neuro]'") from exc
    if len(windows) != len(values_by_window) or len(windows) != len(times_by_window):
        raise ValueError("Canonical payload window/value/time counts do not match.")
    digest = hashlib.sha256()
    digest.update(_json_bytes({"channel_names": channel_names, "windows": windows}))
    for (start, stop), values, times in zip(windows, values_by_window, times_by_window):
        array = np.asarray(values, dtype="<f8", order="C")
        time_array = np.asarray(times, dtype="<f8", order="C")
        if array.shape != (len(channel_names), stop - start):
            raise ValueError("Canonical payload array shape mismatch.")
        if time_array.shape != (stop - start,):
            raise ValueError("Canonical payload timestamp shape mismatch.")
        digest.update(struct.pack("<qq", start, stop))
        digest.update(array.tobytes(order="C"))
        digest.update(time_array.tobytes(order="C"))
    return digest.hexdigest()


def inspect_signal_quality(
    source_path: str | Path,
    *,
    intake_report_path: str | Path,
    fixture_manifest_path: str | Path,
    contract_path: str | Path,
    root_path: str | Path | None = None,
    limits: SignalQualityLimits | None = None,
) -> SignalQualityResult:
    """Run the frozen RW2 bounded reader and descriptive-quality gate."""

    started_at = time.perf_counter()
    limits = limits or SignalQualityLimits()
    _enforce_single_thread_environment()
    contract, contract_bytes = _load_contract(contract_path, limits=limits)
    fixture_manifest, fixture_bytes = _load_fixture_manifest(
        fixture_manifest_path,
        max_bytes=4 * _MIB,
    )
    contract_sha256 = _sha256_bytes(contract_bytes)
    if fixture_manifest["contract_sha256"] != contract_sha256:
        raise ValueError("fixture_manifest_contract_hash_mismatch")

    intake, intake_bytes = _load_intake_payload(
        intake_report_path,
        max_bytes=4 * _MIB,
    )
    intake_sha256 = _sha256_bytes(intake_bytes)
    fixture = _match_fixture_record(
        fixture_manifest,
        intake_sha256=intake_sha256,
        source_manifest_sha256=intake["source"]["source_manifest_sha256"],
        source_path=Path(source_path).expanduser(),
        manifest_root=Path(fixture_manifest_path).expanduser().resolve(strict=True).parent,
    )
    source, root, _bound_files = _bind_source_files(
        source_path,
        root_path=root_path,
        intake=intake,
        limits=limits,
    )
    _validate_fixture_source_binding(fixture, source=source, root=root, intake=intake)
    refusal = fixture.get("expected_refusal")
    if refusal is not None:
        raise ValueError(str(refusal))
    if fixture.get("status") != "readable":
        raise ValueError("fixture_is_not_authorized_for_signal_read")

    mne, np, scipy = _require_neuro_dependencies()
    raw_path, direct_family = _resolve_direct_raw_path(source, root=root, intake=intake)
    _preflight_format_contract(
        direct_family,
        raw_path=raw_path,
        fixture=fixture,
        intake=intake,
        root=root,
    )
    adapter = _adapter_for_family(contract, direct_family)

    captured_warnings: list[python_warnings.WarningMessage]
    with python_warnings.catch_warnings(record=True) as caught:
        python_warnings.simplefilter("always")
        raw = _open_raw(mne, direct_family, raw_path)
        captured_warnings = list(caught)
    try:
        if bool(raw.preload):
            raise ValueError("reader_unexpectedly_preloaded")
        channel_names = list(raw.ch_names)
        channel_types = list(raw.get_channel_types())
        if len(channel_names) != len(channel_types):
            raise ValueError("channel_name_type_length_mismatch")
        duplicate_names = len(set(channel_names)) != len(channel_names)
        selected_indices = [
            index for index, channel_type in enumerate(channel_types)
            if channel_type in _DATA_CHANNEL_TYPES
        ]
        excluded_type_counts = _type_counts(
            channel_type
            for channel_type in channel_types
            if channel_type not in _DATA_CHANNEL_TYPES
        )
        if not selected_indices:
            raise ValueError("no_supported_physiology_channels")
        if len(selected_indices) > limits.max_channels:
            raise ValueError("channel_count_exceeds_registered_cap")
        selected_names = [channel_names[index] for index in selected_indices]
        selected_types = [channel_types[index] for index in selected_indices]
        windows = select_window_ranges(
            int(raw.n_times),
            float(raw.info["sfreq"]),
            len(selected_indices),
            limits=limits,
        )
        if direct_family in {"edf_or_edf_plus", "bdf"}:
            _validate_single_source_rate(raw)

        state_before = _source_state(raw, channel_types=channel_types, np=np)
        state_before_sha256 = _sha256_json(state_before)
        values_by_window, times_by_window, read_calls = _read_grouped_windows(
            raw,
            selected_indices=selected_indices,
            selected_types=selected_types,
            windows=windows,
            np=np,
        )
        payload_before_sha256 = canonical_payload_sha256(
            selected_names,
            windows,
            values_by_window,
            times_by_window,
        )
        if payload_before_sha256 != fixture["expected_payload_sha256"]:
            raise ValueError("synthetic_fixture_payload_hash_mismatch")

        time_rows, structural_warnings = _time_domain_rows(
            selected_names,
            selected_types,
            windows,
            values_by_window,
            np=np,
        )
        psd_rows = _psd_rows(
            mne,
            selected_names,
            selected_types,
            windows,
            values_by_window,
            sfreq=float(raw.info["sfreq"]),
            np=np,
        )
        geometry = _geometry_summary(raw, selected_indices=selected_indices, np=np)
        reference = _reference_summary(raw, selected_types=selected_types)
        filters = _filter_projector_summary(raw)
        events = _annotation_summary(raw, np=np)
        units = _unit_rows(raw, selected_names, selected_types)

        if duplicate_names:
            structural_warnings.add("duplicate_channel_names")
        if any(row["mne_si_unit"] is None for row in units):
            structural_warnings.add("unsupported_or_unknown_units")
        if reference["status"] == "unknown":
            structural_warnings.add("reference_unknown")
        if geometry["status"] != "available_all_selected_channels":
            structural_warnings.add("geometry_unavailable_or_partially_finite")
        if raw.info.get("bads"):
            structural_warnings.add("source_bad_channel_declarations_present")
        if filters["source_filters_or_projectors_present"]:
            structural_warnings.add("source_filters_or_projectors_present")
        for times, (start, stop) in zip(times_by_window, windows):
            expected_times = np.arange(start, stop, dtype=np.float64) / float(
                raw.info["sfreq"]
            )
            if times.shape != expected_times.shape or not np.allclose(
                times,
                expected_times,
                rtol=0.0,
                atol=1e-12,
            ):
                structural_warnings.add("nonmonotonic_or_wrong_length_timestamps")

        advisories = _relative_rms_advisories(time_rows, np=np)
        actual_advisory_channels = sorted(
            row["channel_name"] for row in advisories
        )
        if actual_advisory_channels != sorted(fixture["expected_advisory_channels"]):
            raise ValueError("synthetic_fixture_advisory_mismatch")
        _validate_expected_psd_peaks(
            psd_rows,
            fixture["expected_peak_hz_by_channel"],
        )
        payload_after_sha256 = canonical_payload_sha256(
            selected_names,
            windows,
            values_by_window,
            times_by_window,
        )
        state_after = _source_state(raw, channel_types=channel_types, np=np)
        state_after_sha256 = _sha256_json(state_after)
        no_mutation_passed = (
            payload_before_sha256 == payload_after_sha256
            and state_before_sha256 == state_after_sha256
        )
        if not no_mutation_passed:
            structural_warnings.add("before_after_mutation_mismatch")
            raise ValueError("before_after_mutation_mismatch")

        expected_warnings = sorted(fixture["expected_structural_warnings"])
        actual_warnings = sorted(structural_warnings)
        if actual_warnings != expected_warnings:
            raise ValueError(
                "synthetic_fixture_warning_mismatch: "
                f"expected={expected_warnings} actual={actual_warnings}"
            )
        if events["status"] != fixture["expected_event_status"]:
            raise ValueError("synthetic_fixture_event_status_mismatch")
        if selected_types != fixture["expected_channel_types"]:
            raise ValueError("synthetic_fixture_channel_type_mismatch")
        if geometry["status"] != fixture["expected_geometry_status"]:
            raise ValueError("synthetic_fixture_geometry_status_mismatch")
        if reference["status"] != fixture["expected_reference_status"]:
            raise ValueError("synthetic_fixture_reference_status_mismatch")

        requested_values = len(selected_indices) * sum(stop - start for start, stop in windows)
        returned_values = sum(int(values.size) for values in values_by_window)
        materialized_bytes = sum(int(values.nbytes) for values in values_by_window)
        if returned_values != requested_values:
            raise ValueError("requested_returned_sample_value_mismatch")
        if materialized_bytes > limits.max_materialized_signal_array_bytes:
            raise ValueError("materialized_signal_array_cap_exceeded")

        selected_window_rows = []
        for window_id, ((start, stop), times) in enumerate(zip(windows, times_by_window)):
            selected_window_rows.append(
                {
                    "window_id": window_id,
                    "start_sample": start,
                    "stop_sample_exclusive": stop,
                    "sample_count": stop - start,
                    "first_time_sec": _number(times[0]),
                    "last_time_sec": _number(times[-1]),
                }
            )

        report: dict[str, Any] = {
            "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
            "proof_posture": "synthetic_bounded_reader_and_descriptive_quality_only",
            "status": "passed",
            "item": dict(intake["item"]),
            "source": {
                "selected_path": intake["source"]["selected_path"],
                "format_family": intake["source"]["format_family"],
                "direct_raw_family": direct_family,
                "file_count": intake["source"]["file_count"],
                "declared_source_bytes": intake["resources"]["declared_input_bytes"],
                "relative_paths_only": True,
                "synthetic_fixture_id": fixture["fixture_id"],
                "synthetic_variant_id": fixture["variant_id"],
            },
            "reader": {
                "name": adapter["reader"],
                "arguments": adapter["arguments"],
                "preload_requested": False,
                "preloaded_after_open": bool(raw.preload),
                "warning_count": len(captured_warnings),
                "warning_categories": sorted(
                    {warning.category.__name__ for warning in captured_warnings}
                ),
                "warning_messages_redacted": True,
                "mne_bids_used": False,
            },
            "dependencies": {
                "mne": str(mne.__version__),
                "numpy": str(np.__version__),
                "scipy": str(scipy.__version__),
                "mne_bids": None,
            },
            "recording": {
                "modality": intake["recording"]["modality"],
                "device_type": intake["recording"]["device_type"],
                "channel_count_total": len(channel_names),
                "selected_channel_count": len(selected_indices),
                "selected_channel_names": selected_names,
                "selected_channel_types": selected_types,
                "excluded_channel_type_counts": excluded_type_counts,
                "source_bads": list(raw.info.get("bads", [])),
                "sampling_rate_hz": _number(raw.info["sfreq"]),
                "sample_count": int(raw.n_times),
                "duration_sec": _number(int(raw.n_times) / float(raw.info["sfreq"])),
                "sample_span_sec": _number(
                    max(0, int(raw.n_times) - 1) / float(raw.info["sfreq"])
                ),
                "first_sample": int(raw.first_samp),
                "units": units,
                "reference": reference,
                "source_filters_projectors": filters,
                "geometry": geometry,
                "events": events,
            },
            "selected_windows": selected_window_rows,
            "quality": {
                "time_domain": {
                    "per_channel_window": time_rows,
                    "aggregate_by_channel_type": _aggregate_time_metrics(time_rows, np=np),
                },
                "welch_psd": {
                    "method": _welch_method_payload(),
                    "per_channel_window": psd_rows,
                },
                "structural_warnings": actual_warnings,
                "advisory_candidates": advisories,
                "generic_profile_unavailable": [
                    "amplitude_threshold",
                    "clipping_threshold",
                    "flat_difference_threshold",
                    "line_noise_ratio_threshold",
                ],
                "automatic_cleaning_performed": False,
                "annotate_amplitude_used": False,
            },
            "no_mutation": {
                "selected_payload_before_sha256": payload_before_sha256,
                "selected_payload_after_sha256": payload_after_sha256,
                "source_state_before_sha256": state_before_sha256,
                "source_state_after_sha256": state_after_sha256,
                "passed": True,
                "forbidden_operations_performed": [],
            },
            "compatibility": {
                "current_level": 2,
                "levels": [
                    {"level": 0, "status": "passed_rw1_bound"},
                    {"level": 1, "status": "passed_bounded_signal_readable"},
                    {
                        "level": 2,
                        "status": "passed_channels_timing_events_geometry_status_validated",
                    },
                ]
                + [
                    {"level": level, "status": "unavailable_out_of_rw2_scope"}
                    for level in range(3, 7)
                ],
            },
            "causality": {
                "producer_causal": False,
                "status": "offline_noncausal_descriptive_audit",
                "required_left_context_samples": None,
                "required_right_context_samples": None,
                "end_to_end_latency_measured": False,
            },
            "provenance": {
                "contract_id": contract["contract_id"],
                "contract_sha256": contract_sha256,
                "fixture_manifest_sha256": _sha256_bytes(fixture_bytes),
                "fixture_manifest_payload_sha256": fixture_manifest["hashes"][
                    "manifest_payload_sha256"
                ],
                "intake_report_sha256": intake_sha256,
                "intake_report_payload_sha256": intake["hashes"][
                    "report_payload_sha256"
                ],
                "rw1_item_id_sha256": intake["item"]["item_id_sha256"],
                "source_manifest_sha256": intake["source"]["source_manifest_sha256"],
                "expected_payload_sha256": fixture["expected_payload_sha256"],
                "observed_payload_sha256": payload_before_sha256,
            },
            "access_counts": {
                "metadata_header_files_read": 1,
                "annotation_metadata_files_read": 1 if direct_family == "brainvision" else 0,
                "raw_reader_opens": 1,
                "bounded_signal_read_calls": read_calls,
                "requested_sample_values": requested_values,
                "returned_sample_values": returned_values,
                "materialized_signal_array_bytes": materialized_bytes,
                "physical_storage_bytes_read": None,
                "physical_storage_bytes_status": "unavailable_without_validated_io_instrumentation",
                "real_data_reads": 0,
                "consumed_cache_reads": 0,
                "target_label_values_emitted_or_used": 0,
                "model_runs": 0,
                "training_runs": 0,
                "network_calls": 0,
                "output_bytes": None,
            },
            "resources": {
                "declared_source_bytes": intake["resources"]["declared_input_bytes"],
                "selected_window_count": len(windows),
                "selected_channel_count": len(selected_indices),
                "requested_sample_values": requested_values,
                "returned_sample_values": returned_values,
                "materialized_signal_array_bytes": materialized_bytes,
                "new_signal_cache_bytes": 0,
                "runtime_sec": None,
                "peak_rss_bytes": None,
                "output_bytes": None,
                "caps": asdict(limits),
            },
            "privacy": {
                "local_only": True,
                "absolute_paths_emitted": False,
                "participant_rows_emitted": False,
                "measurement_timestamps_emitted": False,
                "device_serials_emitted": False,
                "event_or_annotation_descriptions_emitted": False,
                "exact_geometry_emitted": False,
                "waveform_values_emitted": False,
            },
            "warnings": sorted(
                [
                    "neural_recordings_and_derived_features_are_sensitive",
                    "synthetic_fixture_only_no_real_recording_authorized",
                    "quality_metrics_are_descriptive_not_diagnostic",
                    "no_prediction_or_decoding_result",
                ]
            ),
            "unavailable_fields": sorted(
                {
                    "end_to_end_latency",
                    "physical_storage_bytes_read",
                    "real_recording_quality",
                    "task_compatibility",
                    "benchmark_authorization",
                    "model_compatibility",
                    "live_source_qualification",
                }
                | {
                    f"generic_warning_profile.{name}"
                    for name in (
                        "amplitude_threshold",
                        "clipping_threshold",
                        "flat_difference_threshold",
                        "line_noise_ratio_threshold",
                    )
                }
            ),
            "claim_boundary": {
                "allowed": [
                    "bounded_reader_mechanics_on_generated_files",
                    "synthetic_channel_timing_unit_geometry_and_event_status_identity",
                    "descriptive_quality_metric_calculation",
                    "privacy_redaction_and_no_mutation_behavior",
                    "measured_local_resource_behavior",
                ],
                "prohibited": [
                    "real_recording_quality",
                    "artifact_warning_validity_on_people_or_devices",
                    "preprocessing_benefit",
                    "prediction_or_decoding",
                    "neural_advantage",
                    "unseen_person_generalization",
                    "end_to_end_real_time_operation",
                    "portable_or_at_home_hardware_performance",
                    "arbitrary_thought_or_clinical_use",
                ],
            },
            "hashes": {"report_payload_sha256": None},
        }
        report["hashes"]["report_payload_sha256"] = _report_payload_sha256(report)
        validate_signal_quality_report(report)
    finally:
        raw.close()

    runtime_sec = round(time.perf_counter() - started_at, 6)
    peak_rss_bytes = _peak_rss_bytes()
    if runtime_sec > limits.max_runtime_seconds:
        raise ValueError("runtime_cap_exceeded")
    if peak_rss_bytes is not None and peak_rss_bytes > limits.max_peak_rss_bytes:
        raise ValueError("peak_rss_cap_exceeded")
    return SignalQualityResult(
        report=report,
        runtime_sec=runtime_sec,
        peak_rss_bytes=peak_rss_bytes,
    )


def write_signal_quality_artifacts(
    result: SignalQualityResult,
    out_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write deterministic JSON/Markdown plus a measured RW2 audit sidecar."""

    validate_signal_quality_report(result.report)
    output_dir = Path(out_dir).expanduser()
    _validate_output_directory(output_dir, overwrite=overwrite)
    report_bytes = _json_bytes(result.report)
    markdown_bytes = render_signal_quality_markdown(result.report).encode("utf-8")
    max_output_bytes = int(result.report["resources"]["caps"]["max_output_bytes"])
    audit = {
        "schema": {"name": AUDIT_SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": "measured_synthetic_signal_quality_audit",
        "measurements": {
            "runtime_sec": result.runtime_sec,
            "runtime_scope": "open_bounded_read_metrics_report_build",
            "peak_rss_bytes": result.peak_rss_bytes,
            "peak_rss_scope": "process_high_water_mark",
            "producer_causal": False,
            "end_to_end_latency_measured": False,
        },
        "access_counts": dict(result.report["access_counts"]),
        "resources": {
            "declared_source_bytes": result.report["resources"]["declared_source_bytes"],
            "materialized_signal_array_bytes": result.report["resources"][
                "materialized_signal_array_bytes"
            ],
            "deterministic_json_bytes": len(report_bytes),
            "deterministic_markdown_bytes": len(markdown_bytes),
            "audit_json_bytes": 0,
            "total_output_bytes": 0,
            "max_output_bytes": max_output_bytes,
            "output_cap_passed": True,
            "max_runtime_seconds": result.report["resources"]["caps"][
                "max_runtime_seconds"
            ],
            "runtime_cap_passed": (
                result.runtime_sec
                <= result.report["resources"]["caps"]["max_runtime_seconds"]
            ),
            "max_peak_rss_bytes": result.report["resources"]["caps"][
                "max_peak_rss_bytes"
            ],
            "peak_rss_cap_passed": (
                result.peak_rss_bytes is None
                or result.peak_rss_bytes
                <= result.report["resources"]["caps"]["max_peak_rss_bytes"]
            ),
            "new_signal_cache_bytes": 0,
        },
        "artifacts": {
            ARTIFACT_JSON: {
                "bytes": len(report_bytes),
                "sha256": _sha256_bytes(report_bytes),
            },
            ARTIFACT_MARKDOWN: {
                "bytes": len(markdown_bytes),
                "sha256": _sha256_bytes(markdown_bytes),
            },
            ARTIFACT_AUDIT: {"bytes": 0, "sha256": None},
        },
        "warnings": [
            "runtime_peak_rss_and_output_bytes_are_outside_deterministic_core",
            "audit_sidecar_does_not_self_hash",
        ],
    }
    for _ in range(12):
        audit_bytes = _json_bytes(audit)
        audit_size = len(audit_bytes)
        total_size = len(report_bytes) + len(markdown_bytes) + audit_size
        if (
            audit["resources"]["audit_json_bytes"] == audit_size
            and audit["resources"]["total_output_bytes"] == total_size
            and audit["artifacts"][ARTIFACT_AUDIT]["bytes"] == audit_size
            and audit["access_counts"]["output_bytes"] == total_size
        ):
            break
        audit["resources"]["audit_json_bytes"] = audit_size
        audit["resources"]["total_output_bytes"] = total_size
        audit["artifacts"][ARTIFACT_AUDIT]["bytes"] = audit_size
        audit["access_counts"]["output_bytes"] = total_size
    else:  # pragma: no cover
        raise RuntimeError("Signal-quality audit byte accounting did not converge.")
    audit_bytes = _json_bytes(audit)
    total_output_bytes = len(report_bytes) + len(markdown_bytes) + len(audit_bytes)
    if total_output_bytes > max_output_bytes:
        raise ValueError(
            "Planned signal-quality artifacts exceed output cap: "
            f"{total_output_bytes} > {max_output_bytes} bytes."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_artifact(output_dir / ARTIFACT_JSON, report_bytes, overwrite=overwrite)
    _write_artifact(output_dir / ARTIFACT_MARKDOWN, markdown_bytes, overwrite=overwrite)
    _write_artifact(output_dir / ARTIFACT_AUDIT, audit_bytes, overwrite=overwrite)
    return {
        "status": result.report["status"],
        "fixture_id": result.report["source"]["synthetic_fixture_id"],
        "format_family": result.report["source"]["format_family"],
        "compatibility_level": result.report["compatibility"]["current_level"],
        "selected_channel_count": result.report["resources"]["selected_channel_count"],
        "selected_window_count": result.report["resources"]["selected_window_count"],
        "requested_sample_values": result.report["resources"][
            "requested_sample_values"
        ],
        "materialized_signal_array_bytes": result.report["resources"][
            "materialized_signal_array_bytes"
        ],
        "runtime_sec": result.runtime_sec,
        "peak_rss_bytes": result.peak_rss_bytes,
        "total_output_bytes": total_output_bytes,
        "max_output_bytes": max_output_bytes,
        "output_cap_passed": True,
        "raw_reader_opens": result.report["access_counts"]["raw_reader_opens"],
        "real_data_reads": 0,
        "consumed_cache_reads": 0,
        "target_label_values_emitted_or_used": 0,
        "model_runs": 0,
        "training_runs": 0,
        "network_calls": 0,
        "producer_causal": False,
        "end_to_end_latency_measured": False,
        "structural_warnings": result.report["quality"]["structural_warnings"],
        "unavailable_fields": result.report["unavailable_fields"],
        "artifacts": [ARTIFACT_JSON, ARTIFACT_MARKDOWN, ARTIFACT_AUDIT],
    }


def load_signal_quality_report(
    report_path: str | Path,
    *,
    audit_path: str | Path | None = None,
    max_report_bytes: int = 4 * _MIB,
) -> dict[str, Any]:
    """Load and strictly validate an RW2 report and optional audit sidecar."""

    report_file = _safe_json_file(report_path, max_bytes=max_report_bytes)
    report_bytes = report_file.read_bytes()
    try:
        report = json.loads(report_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid signal-quality report JSON.") from exc
    validate_signal_quality_report(report)

    if audit_path is None:
        candidate = report_file.with_name(ARTIFACT_AUDIT)
        audit_file = candidate if candidate.is_file() and not candidate.is_symlink() else None
    else:
        audit_file = _safe_json_file(audit_path, max_bytes=max_report_bytes)
    audit = None
    if audit_file is not None:
        audit_bytes = audit_file.read_bytes()
        try:
            audit = json.loads(audit_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid signal-quality audit JSON.") from exc
        _validate_signal_quality_audit(
            audit,
            report_file=report_file,
            report_bytes=report_bytes,
            audit_file=audit_file,
            audit_bytes=audit_bytes,
        )
    return {
        "schema": dict(report["schema"]),
        "status": report["status"],
        "fixture_id": report["source"]["synthetic_fixture_id"],
        "format_family": report["source"]["format_family"],
        "compatibility_level": report["compatibility"]["current_level"],
        "selected_channel_count": report["resources"]["selected_channel_count"],
        "selected_window_count": report["resources"]["selected_window_count"],
        "requested_sample_values": report["resources"]["requested_sample_values"],
        "materialized_signal_array_bytes": report["resources"][
            "materialized_signal_array_bytes"
        ],
        "contract_sha256": report["provenance"]["contract_sha256"],
        "source_manifest_sha256": report["provenance"]["source_manifest_sha256"],
        "payload_sha256": report["provenance"]["observed_payload_sha256"],
        "report_payload_sha256": report["hashes"]["report_payload_sha256"],
        "access_counts": dict(report["access_counts"]),
        "structural_warnings": list(report["quality"]["structural_warnings"]),
        "advisory_candidates": list(report["quality"]["advisory_candidates"]),
        "unavailable_fields": list(report["unavailable_fields"]),
        "measurements": audit["measurements"] if audit else None,
        "output": audit["resources"] if audit else None,
        "audit_validated": audit is not None,
    }


def validate_signal_quality_report(report: dict[str, Any]) -> None:
    """Strictly validate one deterministic RW2 signal-quality report."""

    if not isinstance(report, dict):
        raise ValueError("Signal-quality report must be a JSON object.")
    required = {
        "schema",
        "proof_posture",
        "status",
        "item",
        "source",
        "reader",
        "dependencies",
        "recording",
        "selected_windows",
        "quality",
        "no_mutation",
        "compatibility",
        "causality",
        "provenance",
        "access_counts",
        "resources",
        "privacy",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
        "hashes",
    }
    missing = sorted(required - set(report))
    if missing:
        raise ValueError(f"Signal-quality report is missing required fields: {missing}")
    if report["schema"] != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("Unsupported signal-quality report schema.")
    if report["status"] != "passed":
        raise ValueError("Signal-quality report status must be passed.")
    forbidden = _FORBIDDEN_KEYS & set(_all_mapping_keys(report))
    if forbidden:
        raise ValueError(f"Signal-quality report contains forbidden fields: {sorted(forbidden)}")
    _reject_absolute_paths(report)

    if report["compatibility"].get("current_level") != 2:
        raise ValueError("RW2 report must stop at compatibility level 2.")
    levels = report["compatibility"].get("levels")
    if not isinstance(levels, list) or [row.get("level") for row in levels] != list(range(7)):
        raise ValueError("Compatibility levels must cover exactly 0 through 6.")
    if report["causality"] != {
        "producer_causal": False,
        "status": "offline_noncausal_descriptive_audit",
        "required_left_context_samples": None,
        "required_right_context_samples": None,
        "end_to_end_latency_measured": False,
    }:
        raise ValueError("Causality boundary does not match the frozen RW2 contract.")
    if report["reader"].get("preload_requested") is not False:
        raise ValueError("Reader must request preload=False.")
    if report["reader"].get("preloaded_after_open") is not False:
        raise ValueError("Reader unexpectedly preloaded the source.")
    if report["reader"].get("mne_bids_used") is not False:
        raise ValueError("MNE-BIDS is forbidden in RW2.")

    privacy = report["privacy"]
    if privacy != {
        "local_only": True,
        "absolute_paths_emitted": False,
        "participant_rows_emitted": False,
        "measurement_timestamps_emitted": False,
        "device_serials_emitted": False,
        "event_or_annotation_descriptions_emitted": False,
        "exact_geometry_emitted": False,
        "waveform_values_emitted": False,
    }:
        raise ValueError("Privacy boundary does not match the frozen RW2 contract.")
    events = report["recording"].get("events")
    if not isinstance(events, dict) or any(
        key in events for key in ("descriptions", "onsets", "timestamps", "extras")
    ):
        raise ValueError("Event descriptions or timestamps cannot appear in RW2 artifacts.")
    geometry = report["recording"].get("geometry")
    if not isinstance(geometry, dict) or any(
        key in geometry for key in ("coordinates", "positions", "locs")
    ):
        raise ValueError("Exact geometry cannot appear in RW2 artifacts.")

    if report["quality"].get("automatic_cleaning_performed") is not False:
        raise ValueError("RW2 cannot perform automatic cleaning.")
    if report["quality"].get("annotate_amplitude_used") is not False:
        raise ValueError("RW2 cannot call annotate_amplitude.")
    if report["no_mutation"].get("passed") is not True:
        raise ValueError("RW2 no-mutation gate did not pass.")
    if report["no_mutation"].get("forbidden_operations_performed") != []:
        raise ValueError("RW2 report lists a forbidden operation.")
    if (
        report["no_mutation"].get("selected_payload_before_sha256")
        != report["no_mutation"].get("selected_payload_after_sha256")
    ):
        raise ValueError("Selected payload changed during inspection.")
    if (
        report["no_mutation"].get("source_state_before_sha256")
        != report["no_mutation"].get("source_state_after_sha256")
    ):
        raise ValueError("Source state changed during inspection.")

    access = report["access_counts"]
    for key in (
        "real_data_reads",
        "consumed_cache_reads",
        "target_label_values_emitted_or_used",
        "model_runs",
        "training_runs",
        "network_calls",
    ):
        if access.get(key) != 0:
            raise ValueError(f"Signal-quality report has forbidden access count: {key}")
    if access.get("raw_reader_opens") != 1:
        raise ValueError("Signal-quality report must record exactly one raw reader open.")
    if access.get("requested_sample_values") != access.get("returned_sample_values"):
        raise ValueError("Requested and returned sample values differ.")
    if access.get("output_bytes") is not None:
        raise ValueError("Output bytes belong in the measured audit sidecar.")

    try:
        limits = SignalQualityLimits(**report["resources"]["caps"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Signal-quality report contains invalid caps.") from exc
    if report["resources"].get("selected_channel_count") > limits.max_channels:
        raise ValueError("Signal-quality report exceeds channel cap.")
    if report["resources"].get("selected_window_count") > limits.max_windows:
        raise ValueError("Signal-quality report exceeds window cap.")
    if report["resources"].get("requested_sample_values") > limits.max_channel_sample_values:
        raise ValueError("Signal-quality report exceeds sample-value cap.")
    if (
        report["resources"].get("materialized_signal_array_bytes")
        > limits.max_materialized_signal_array_bytes
    ):
        raise ValueError("Signal-quality report exceeds materialized-array cap.")
    if report["resources"].get("new_signal_cache_bytes") != 0:
        raise ValueError("RW2 cannot create a signal cache.")
    if report["resources"].get("runtime_sec") is not None:
        raise ValueError("Runtime belongs in the measured audit sidecar.")
    if report["resources"].get("peak_rss_bytes") is not None:
        raise ValueError("Peak RSS belongs in the measured audit sidecar.")
    if report["resources"].get("output_bytes") is not None:
        raise ValueError("Output bytes belong in the measured audit sidecar.")

    windows = report["selected_windows"]
    if len(windows) != report["resources"]["selected_window_count"]:
        raise ValueError("Selected-window count mismatch.")
    if any(row.get("sample_count", 0) < limits.min_samples_per_window for row in windows):
        raise ValueError("Selected window is below the minimum sample count.")
    if windows != sorted(windows, key=lambda row: row["start_sample"]):
        raise ValueError("Selected windows are not chronological.")
    if report["quality"].get("structural_warnings") != sorted(
        set(report["quality"].get("structural_warnings", []))
    ):
        raise ValueError("Structural warnings must be sorted and unique.")
    if report["warnings"] != sorted(set(report["warnings"])):
        raise ValueError("Warnings must be sorted and unique.")
    if report["unavailable_fields"] != sorted(set(report["unavailable_fields"])):
        raise ValueError("Unavailable fields must be sorted and unique.")

    expected_payload = report["provenance"].get("expected_payload_sha256")
    observed_payload = report["provenance"].get("observed_payload_sha256")
    if expected_payload != observed_payload:
        raise ValueError("Expected and observed payload hashes differ.")
    for field in (
        "contract_sha256",
        "fixture_manifest_sha256",
        "fixture_manifest_payload_sha256",
        "intake_report_sha256",
        "intake_report_payload_sha256",
        "rw1_item_id_sha256",
        "source_manifest_sha256",
        "expected_payload_sha256",
        "observed_payload_sha256",
    ):
        if not _is_sha256(report["provenance"].get(field)):
            raise ValueError(f"Invalid provenance SHA-256: {field}")
    if report["hashes"].get("report_payload_sha256") != _report_payload_sha256(report):
        raise ValueError("Signal-quality report payload hash mismatch.")
    _json_bytes(report)


def render_signal_quality_markdown(report: dict[str, Any]) -> str:
    """Render a compact deterministic human-readable RW2 report."""

    validate_signal_quality_report(report)
    resources = report["resources"]
    access = report["access_counts"]
    recording = report["recording"]
    lines = [
        "# RW2 Synthetic Signal Quality Report",
        "",
        f"- Status: **{report['status']}**",
        f"- Compatibility level: `{report['compatibility']['current_level']}`",
        f"- Fixture: `{report['source']['synthetic_fixture_id']}`",
        f"- Format: `{report['source']['format_family']}`",
        f"- Direct reader: `{report['reader']['name']}`",
        f"- Modality: `{recording['modality']}`",
        f"- Channels selected: `{resources['selected_channel_count']}`",
        f"- Windows selected: `{resources['selected_window_count']}`",
        f"- Sampling rate: `{recording['sampling_rate_hz']}` Hz",
        f"- Duration: `{recording['duration_sec']}` seconds",
        f"- Geometry: `{recording['geometry']['status']}`",
        f"- Reference: `{recording['reference']['status']}`",
        f"- Events: `{recording['events']['status']}`",
        "",
        "## Bounded Access",
        "",
        f"- Raw reader opens: `{access['raw_reader_opens']}`",
        f"- Bounded signal reads: `{access['bounded_signal_read_calls']}`",
        f"- Requested/returned values: `{access['requested_sample_values']}` / "
        f"`{access['returned_sample_values']}`",
        f"- Materialized arrays: `{access['materialized_signal_array_bytes']}` bytes",
        "- Physical storage bytes read: `unavailable`",
        "- Real-data reads: `0`",
        "- Consumed-cache reads: `0`",
        "- Target/label values used or emitted: `0`",
        "- Model runs: `0`",
        "- Training runs: `0`",
        "- Network calls: `0`",
        "- Runtime, peak RSS, and output bytes: measured in `signal_quality.audit.json`",
        "- Producer causal: `false`",
        "- End-to-end latency measured: `false`",
        "",
        "## Structural Warnings",
        "",
    ]
    structural = report["quality"]["structural_warnings"]
    lines.extend(f"- `{warning}`" for warning in structural)
    if not structural:
        lines.append("- None on this generated fixture.")
    lines.extend(["", "## Advisory Candidates", ""])
    advisories = report["quality"]["advisory_candidates"]
    for row in advisories:
        lines.append(
            f"- `{row['code']}`: `{row['channel_name']}` ({row['channel_type']})"
        )
    if not advisories:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            f"- Contract SHA-256: `{report['provenance']['contract_sha256']}`",
            f"- RW1 source manifest SHA-256: "
            f"`{report['provenance']['source_manifest_sha256']}`",
            f"- Selected payload SHA-256: "
            f"`{report['provenance']['observed_payload_sha256']}`",
            f"- Report payload SHA-256: `{report['hashes']['report_payload_sha256']}`",
            "",
            "## Claim Boundary",
            "",
            "This generated-file gate proves bounded reader/report mechanics, descriptive",
            "metric calculation, privacy redaction, and source no-mutation behavior only.",
            "It does not prove real recording quality, decoding, neural advantage,",
            "real-time text output, or portable at-home hardware performance.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_contract(
    path: str | Path,
    *,
    limits: SignalQualityLimits,
) -> tuple[dict[str, Any], bytes]:
    contract_file = _safe_json_file(path, max_bytes=4 * _MIB)
    raw = contract_file.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Signal-quality contract JSON is invalid.") from exc
    if payload.get("schema_name") != CONTRACT_SCHEMA_NAME:
        raise ValueError("Unsupported signal-quality contract schema.")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported signal-quality contract version.")
    if payload.get("status") != "preregistered_no_reader_implementation":
        raise ValueError("Signal-quality contract is not the frozen preregistration.")
    authorization = payload.get("authorization", {})
    if authorization.get("synthetic_files_only") is not True:
        raise ValueError("RW2 contract must remain synthetic-only.")
    for key in (
        "real_signal_read_authorized",
        "consumed_s7_or_s21_access_authorized",
        "s20_access_authorized",
        "download_authorized",
        "mne_bids_install_or_use_authorized",
        "model_or_training_authorized",
        "target_label_or_prediction_output_authorized",
        "signal_cache_authorized",
    ):
        if authorization.get(key) is not False:
            raise ValueError(f"RW2 contract authorization drift: {key}")
    caps = payload.get("resource_caps", {})
    if caps.get("workers") != 1 or caps.get("numerical_threads") != 1:
        raise ValueError("RW2 contract must freeze one worker and one numerical thread.")
    configured_by_contract_key = {
        "max_source_files": limits.max_source_files,
        "max_directory_depth": limits.max_directory_depth,
        "max_declared_source_bytes": limits.max_declared_source_bytes,
        "max_channels": limits.max_channels,
        "max_windows": limits.max_windows,
        "max_channel_sample_values": limits.max_channel_sample_values,
        "max_materialized_signal_array_bytes": limits.max_materialized_signal_array_bytes,
        "max_runtime_seconds": limits.max_runtime_seconds,
        "max_peak_rss_bytes": limits.max_peak_rss_bytes,
        "max_generated_artifact_bytes_per_run": limits.max_output_bytes,
    }
    for key, configured in configured_by_contract_key.items():
        frozen = caps.get(key)
        if not isinstance(frozen, (int, float)) or configured > frozen:
            raise ValueError(f"RW2 configured limit exceeds frozen contract: {key}")
    if limits.min_samples_per_window < 128:
        raise ValueError("RW2 minimum samples cannot be lower than 128.")
    if limits.target_window_seconds != 4.0:
        raise ValueError("RW2 target window duration must remain 4 seconds.")
    return payload, raw


def _load_fixture_manifest(
    path: str | Path,
    *,
    max_bytes: int,
) -> tuple[dict[str, Any], bytes]:
    manifest_file = _safe_json_file(path, max_bytes=max_bytes)
    raw = manifest_file.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Signal-quality fixture manifest JSON is invalid.") from exc
    if payload.get("schema") != {"name": FIXTURE_SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("Unsupported signal-quality fixture manifest schema.")
    if payload.get("proof_posture") != "deterministic_synthetic_target_free_fixtures":
        raise ValueError("Fixture manifest proof posture is invalid.")
    if not isinstance(payload.get("fixtures"), list) or not payload["fixtures"]:
        raise ValueError("Fixture manifest must contain fixtures.")
    if payload.get("hashes", {}).get("manifest_payload_sha256") != _manifest_payload_sha256(
        payload
    ):
        raise ValueError("Fixture manifest payload hash mismatch.")
    forbidden = _FORBIDDEN_KEYS & set(_all_mapping_keys(payload))
    if forbidden:
        raise ValueError(f"Fixture manifest contains forbidden fields: {sorted(forbidden)}")
    _reject_absolute_paths(payload)
    return payload, raw


def _load_intake_payload(path: str | Path, *, max_bytes: int) -> tuple[dict[str, Any], bytes]:
    report_file = _safe_json_file(path, max_bytes=max_bytes)
    raw = report_file.read_bytes()
    try:
        report = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("RW1 intake report JSON is invalid.") from exc
    validate_intake_report(report)
    if report.get("status") != "recognized" or report["compatibility"].get(
        "current_level"
    ) != 0:
        raise ValueError("RW1 intake report did not pass compatibility level 0.")
    return report, raw


def _match_fixture_record(
    manifest: dict[str, Any],
    *,
    intake_sha256: str,
    source_manifest_sha256: str,
    source_path: Path,
    manifest_root: Path,
) -> dict[str, Any]:
    selected_source = source_path.resolve(strict=True)
    matches = [
        row
        for row in manifest["fixtures"]
        if row.get("intake_report_sha256") == intake_sha256
        and row.get("source_manifest_sha256") == source_manifest_sha256
        and manifest_root.joinpath(
            *_safe_relative_path(row.get("source_path")).parts
        ).resolve(strict=True)
        == selected_source
    ]
    if len(matches) != 1:
        raise ValueError("strict_synthetic_fixture_binding_failed")
    fixture = matches[0]
    required = {
        "fixture_id",
        "variant_id",
        "format_family",
        "status",
        "source_path",
        "selected_path",
        "intake_report_sha256",
        "source_manifest_sha256",
        "expected_payload_sha256",
        "expected_channel_types",
        "expected_geometry_status",
        "expected_reference_status",
        "expected_event_status",
        "expected_structural_warnings",
        "expected_advisory_channels",
        "expected_peak_hz_by_channel",
        "expected_refusal",
    }
    missing = sorted(required - set(fixture))
    if missing:
        raise ValueError(f"Fixture record is missing required fields: {missing}")
    return fixture


def _bind_source_files(
    source_path: str | Path,
    *,
    root_path: str | Path | None,
    intake: dict[str, Any],
    limits: SignalQualityLimits,
) -> tuple[Path, Path, list[Path]]:
    source = Path(source_path).expanduser()
    if source.is_symlink():
        raise ValueError("selected_source_cannot_be_a_symlink")
    if not source.exists():
        raise FileNotFoundError(f"Selected source does not exist: {source.name}")
    source = source.resolve(strict=True)
    if root_path is None:
        root = source if source.is_dir() else source.parent
    else:
        root_candidate = Path(root_path).expanduser()
        if root_candidate.is_symlink():
            raise ValueError("declared_root_cannot_be_a_symlink")
        root = root_candidate.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Declared root must be a directory.")
    try:
        selected_relative = source.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("Selected source escapes the declared root.") from exc
    expected_selected = intake["source"]["selected_path"]
    if source.is_dir():
        selected_relative = "."
    if selected_relative != expected_selected:
        raise ValueError("Selected source does not match the RW1 report.")

    rows = intake["source"]["files"]
    if len(rows) > limits.max_source_files:
        raise ValueError("source_file_count_exceeds_registered_cap")
    declared_bytes = sum(int(row["size_bytes"]) for row in rows)
    if declared_bytes > limits.max_declared_source_bytes:
        raise ValueError("declared_source_bytes_exceed_registered_cap")
    bound: list[Path] = []
    for row in rows:
        relative = _safe_relative_path(row["path"])
        if len(relative.parts) > limits.max_directory_depth + 1:
            raise ValueError("source_directory_depth_exceeds_registered_cap")
        candidate = root.joinpath(*relative.parts)
        if candidate.is_symlink():
            raise ValueError("source_manifest_member_cannot_be_a_symlink")
        if not candidate.is_file():
            raise ValueError("source_manifest_member_is_missing_or_not_regular")
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError("source_manifest_member_escapes_declared_root") from exc
        if resolved.stat().st_size != row["size_bytes"]:
            raise ValueError("source_manifest_file_size_changed")
        bound.append(resolved)
    return source, root, bound


def _validate_fixture_source_binding(
    fixture: dict[str, Any],
    *,
    source: Path,
    root: Path,
    intake: dict[str, Any],
) -> None:
    selected = "." if source.is_dir() else source.relative_to(root).as_posix()
    if fixture["selected_path"] != selected:
        raise ValueError("fixture_selected_path_mismatch")
    if fixture["format_family"] != intake["source"]["format_family"]:
        raise ValueError("fixture_format_family_mismatch")
    if fixture["source_manifest_sha256"] != intake["source"]["source_manifest_sha256"]:
        raise ValueError("fixture_source_manifest_hash_mismatch")


def _resolve_direct_raw_path(
    source: Path,
    *,
    root: Path,
    intake: dict[str, Any],
) -> tuple[Path, str]:
    family = intake["source"]["format_family"]
    if family != "bids":
        return source, family
    candidates = []
    for row in intake["source"]["files"]:
        suffix = PurePosixPath(row["path"]).suffix.lower()
        if suffix in {".vhdr", ".edf", ".bdf", ".set", ".fif"}:
            candidates.append(root.joinpath(*_safe_relative_path(row["path"]).parts))
    if len(candidates) != 1:
        raise ValueError("bids_ambiguous_raw_item")
    direct_family = intake["recording"].get("raw_family")
    if direct_family not in {"brainvision", "edf_or_edf_plus", "bdf", "eeglab", "fif"}:
        raise ValueError("bids_direct_reader_family_unavailable")
    return candidates[0], direct_family


def _preflight_format_contract(
    family: str,
    *,
    raw_path: Path,
    fixture: dict[str, Any],
    intake: dict[str, Any],
    root: Path,
) -> None:
    if family == "eeglab":
        if fixture.get("source_layout") != "continuous_external_fdt":
            raise ValueError("eeglab_embedded_or_epoched_source_refused")
        fdt = raw_path.with_suffix(".fdt")
        if fdt.is_symlink() or not fdt.is_file():
            raise ValueError("eeglab_missing_external_fdt")
    if intake["source"]["format_family"] == "bids":
        paths = [row["path"] for row in intake["source"]["files"]]
        if any(path.endswith("_events.tsv") for path in paths):
            raise ValueError("bids_event_sidecar_requires_content_access")
        if any(PurePosixPath(path).name in {"participants.tsv", "channels.tsv"} for path in paths):
            raise ValueError("bids_sensitive_or_status_sidecar_not_authorized")
        if raw_path.resolve(strict=True).parent == root:
            raise ValueError("bids_raw_item_must_use_bids_modality_directory")


def _require_neuro_dependencies() -> tuple[Any, Any, Any]:
    try:
        import mne
        import numpy as np
        import scipy
    except ImportError as exc:
        raise RuntimeError("RW2 signal inspection requires: pip install -e '.[neuro]'") from exc
    version_parts = re.match(r"^(\d+)\.(\d+)", str(mne.__version__))
    if not version_parts or tuple(map(int, version_parts.groups())) != _EXPECTED_MNE_MINOR:
        raise RuntimeError(
            "RW2 is validated only for MNE 1.12.x; install the pinned [neuro] extra."
        )
    return mne, np, scipy


def _adapter_for_family(contract: dict[str, Any], family: str) -> dict[str, Any]:
    matches = [row for row in contract["format_adapters"] if row["family"] == family]
    if len(matches) != 1:
        raise ValueError(f"No frozen reader adapter for family: {family}")
    return matches[0]


def _open_raw(mne: Any, family: str, path: Path) -> Any:
    if family == "brainvision":
        return mne.io.read_raw_brainvision(
            path,
            eog=(),
            misc=(),
            scale=1.0,
            ignore_marker_types=False,
            preload=False,
            verbose="ERROR",
        )
    if family == "edf_or_edf_plus":
        return mne.io.read_raw_edf(
            path,
            eog=None,
            misc=None,
            stim_channel=None,
            exclude=(),
            infer_types=False,
            include=None,
            preload=False,
            units=None,
            encoding="utf8",
            exclude_after_unique=False,
            verbose="ERROR",
        )
    if family == "bdf":
        return mne.io.read_raw_bdf(
            path,
            eog=None,
            misc=None,
            stim_channel=None,
            exclude=(),
            infer_types=False,
            include=None,
            preload=False,
            units=None,
            encoding="utf8",
            exclude_after_unique=False,
            verbose="ERROR",
        )
    if family == "eeglab":
        return mne.io.read_raw_eeglab(
            path,
            eog=(),
            preload=False,
            uint16_codec=None,
            montage_units="auto",
            verbose="ERROR",
        )
    if family == "fif":
        return mne.io.read_raw_fif(
            path,
            allow_maxshield=False,
            preload=False,
            on_split_missing="raise",
            verbose="ERROR",
        )
    raise ValueError(f"Unsupported direct reader family: {family}")


def _validate_single_source_rate(raw: Any) -> None:
    extras = getattr(raw, "_raw_extras", None)
    if not isinstance(extras, list) or not extras:
        raise ValueError("mixed_or_unknown_source_rates_for_level_2")
    n_samps = extras[0].get("n_samps")
    if n_samps is None:
        raise ValueError("mixed_or_unknown_source_rates_for_level_2")
    rates = {int(value) for value in n_samps if int(value) > 0}
    if len(rates) != 1:
        raise ValueError("mixed_or_unknown_source_rates_for_level_2")


def _read_grouped_windows(
    raw: Any,
    *,
    selected_indices: list[int],
    selected_types: list[str],
    windows: list[tuple[int, int]],
    np: Any,
) -> tuple[list[Any], list[Any], int]:
    groups: dict[str, list[tuple[int, int]]] = {}
    for selected_position, (raw_index, channel_type) in enumerate(
        zip(selected_indices, selected_types)
    ):
        groups.setdefault(channel_type, []).append((selected_position, raw_index))
    values_by_window: list[Any] = []
    times_by_window: list[Any] = []
    read_calls = 0
    for start, stop in windows:
        combined = np.empty((len(selected_indices), stop - start), dtype=np.float64)
        canonical_times = None
        for channel_type in sorted(groups):
            mappings = groups[channel_type]
            positions = [row[0] for row in mappings]
            picks = [row[1] for row in mappings]
            values, times = raw.get_data(
                picks=picks,
                start=start,
                stop=stop,
                return_times=True,
                units=None,
                reject_by_annotation=None,
            )
            read_calls += 1
            values = np.asarray(values, dtype=np.float64)
            times = np.asarray(times, dtype=np.float64)
            if values.shape != (len(picks), stop - start):
                raise ValueError("bounded_reader_returned_unexpected_shape")
            if times.shape != (stop - start,):
                raise ValueError("bounded_reader_returned_unexpected_timestamps")
            if canonical_times is None:
                canonical_times = times
            elif not np.array_equal(canonical_times, times):
                raise ValueError("channel_type_groups_returned_different_timestamps")
            combined[positions, :] = values
        values_by_window.append(combined)
        times_by_window.append(canonical_times)
    return values_by_window, times_by_window, read_calls


def _time_domain_rows(
    channel_names: list[str],
    channel_types: list[str],
    windows: list[tuple[int, int]],
    values_by_window: list[Any],
    *,
    np: Any,
) -> tuple[list[dict[str, Any]], set[str]]:
    rows: list[dict[str, Any]] = []
    structural: set[str] = set()
    for window_id, ((start, stop), values) in enumerate(zip(windows, values_by_window)):
        for channel_index, (name, channel_type) in enumerate(
            zip(channel_names, channel_types)
        ):
            vector = np.asarray(values[channel_index], dtype=np.float64)
            finite = np.isfinite(vector)
            metrics: dict[str, Any] = {
                "sample_count": int(vector.size),
                "finite_fraction": _number(float(np.mean(finite))),
            }
            if not bool(np.all(finite)):
                structural.add("nonfinite_samples_present")
                metrics.update({name: None for name in _TIME_METRICS[2:]})
            else:
                median = float(np.median(vector))
                centered = vector - median
                metrics.update(
                    {
                        "exact_zero_fraction": _number(float(np.mean(vector == 0.0))),
                        "adjacent_equal_fraction": _number(
                            float(np.mean(vector[1:] == vector[:-1]))
                            if vector.size > 1
                            else 0.0
                        ),
                        "minimum": _number(np.min(vector)),
                        "percentile_01": _number(np.percentile(vector, 1)),
                        "median": _number(median),
                        "percentile_99": _number(np.percentile(vector, 99)),
                        "maximum": _number(np.max(vector)),
                        "median_absolute_deviation": _number(
                            np.median(np.abs(centered))
                        ),
                        "centered_rms": _number(np.sqrt(np.mean(centered * centered))),
                        "peak_to_peak": _number(np.ptp(vector)),
                        "maximum_absolute_first_difference": _number(
                            np.max(np.abs(np.diff(vector))) if vector.size > 1 else 0.0
                        ),
                    }
                )
                if vector.size and bool(np.all(vector == vector[0])):
                    structural.add("exact_constant_channel_window")
            rows.append(
                {
                    "window_id": window_id,
                    "start_sample": start,
                    "stop_sample_exclusive": stop,
                    "channel_index": channel_index,
                    "channel_name": name,
                    "channel_type": channel_type,
                    "metrics": metrics,
                }
            )
    return rows, structural


def _aggregate_time_metrics(rows: list[dict[str, Any]], *, np: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    channel_types = sorted({row["channel_type"] for row in rows})
    for channel_type in channel_types:
        selected = [row for row in rows if row["channel_type"] == channel_type]
        metric_rows: dict[str, Any] = {}
        for metric in _TIME_METRICS:
            values = [row["metrics"].get(metric) for row in selected]
            available = [float(value) for value in values if value is not None]
            metric_rows[metric] = {
                "count": len(values),
                "minimum": _number(np.min(available)) if available else None,
                "median": _number(np.median(available)) if available else None,
                "maximum": _number(np.max(available)) if available else None,
                "unavailable_count": len(values) - len(available),
            }
        result[channel_type] = metric_rows
    return result


def _psd_rows(
    mne: Any,
    channel_names: list[str],
    channel_types: list[str],
    windows: list[tuple[int, int]],
    values_by_window: list[Any],
    *,
    sfreq: float,
    np: Any,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for window_id, ((start, stop), values) in enumerate(zip(windows, values_by_window)):
        n_samples = stop - start
        n_per_seg = min(int(round(2.0 * sfreq)), n_samples)
        n_overlap = n_per_seg // 2
        for channel_index, (name, channel_type) in enumerate(
            zip(channel_names, channel_types)
        ):
            vector = np.asarray(values[channel_index], dtype=np.float64)
            if n_samples < 128 or not bool(np.all(np.isfinite(vector))):
                rows.append(
                    {
                        "window_id": window_id,
                        "channel_index": channel_index,
                        "channel_name": name,
                        "channel_type": channel_type,
                        "status": "unavailable_nonfinite_or_too_short",
                        "frequency_resolution_hz": None,
                        "peak_frequency_hz": None,
                        "total_power": None,
                        "bands": _empty_band_payload(),
                        "line_to_sideband_ratio": {"50_hz": None, "60_hz": None},
                    }
                )
                continue
            psd, frequencies = mne.time_frequency.psd_array_welch(
                vector,
                sfreq=sfreq,
                fmin=0.5,
                fmax=min(100.0, sfreq / 2.0),
                n_fft=n_per_seg,
                n_overlap=n_overlap,
                n_per_seg=n_per_seg,
                n_jobs=1,
                average="median",
                window="hann",
                remove_dc=True,
                output="power",
                verbose="ERROR",
            )
            psd = np.asarray(psd, dtype=np.float64)
            frequencies = np.asarray(frequencies, dtype=np.float64)
            total_power = _integrated_power(psd, frequencies, np=np)
            bands: dict[str, Any] = {}
            for band_name, (low, high, inclusive_high) in _BANDS.items():
                mask = (frequencies >= low) & (
                    frequencies <= high if inclusive_high else frequencies < high
                )
                absolute = _integrated_power(psd[mask], frequencies[mask], np=np)
                relative = (
                    absolute / total_power
                    if absolute is not None and total_power not in (None, 0.0)
                    else None
                )
                bands[band_name] = {
                    "absolute_power": _number(absolute),
                    "relative_power": _number(relative),
                }
            peak_frequency = frequencies[int(np.argmax(psd))] if psd.size else None
            resolution = (
                float(np.median(np.diff(frequencies))) if frequencies.size > 1 else None
            )
            rows.append(
                {
                    "window_id": window_id,
                    "channel_index": channel_index,
                    "channel_name": name,
                    "channel_type": channel_type,
                    "status": "available",
                    "frequency_resolution_hz": _number(resolution),
                    "peak_frequency_hz": _number(peak_frequency),
                    "total_power": _number(total_power),
                    "bands": bands,
                    "line_to_sideband_ratio": {
                        "50_hz": _number(_line_ratio(psd, frequencies, 50.0, np=np)),
                        "60_hz": _number(_line_ratio(psd, frequencies, 60.0, np=np)),
                    },
                }
            )
    return rows


def _integrated_power(psd: Any, frequencies: Any, *, np: Any) -> float | None:
    if len(psd) < 2 or len(frequencies) < 2:
        return None
    return float(np.trapezoid(psd, frequencies))


def _validate_expected_psd_peaks(
    rows: list[dict[str, Any]],
    expected_by_channel: dict[str, Any],
) -> None:
    if not isinstance(expected_by_channel, dict):
        raise ValueError("Fixture PSD peak expectations must be a mapping.")
    for channel_name, expected_value in expected_by_channel.items():
        expected = float(expected_value)
        selected = [
            row
            for row in rows
            if row["channel_name"] == channel_name and row["status"] == "available"
        ]
        if not selected:
            raise ValueError("synthetic_fixture_psd_peak_unavailable")
        for row in selected:
            peak = row["peak_frequency_hz"]
            resolution = row["frequency_resolution_hz"]
            if peak is None or resolution is None or abs(float(peak) - expected) > float(
                resolution
            ) + 1e-12:
                raise ValueError("synthetic_fixture_psd_peak_mismatch")


def _line_ratio(psd: Any, frequencies: Any, center: float, *, np: Any) -> float | None:
    center_mask = (frequencies >= center - 1.0) & (frequencies <= center + 1.0)
    side_mask = ((frequencies >= center - 5.0) & (frequencies <= center - 2.0)) | (
        (frequencies >= center + 2.0) & (frequencies <= center + 5.0)
    )
    if int(np.sum(center_mask)) < 1 or int(np.sum(side_mask)) < 2:
        return None
    denominator = float(np.mean(psd[side_mask]))
    if not math.isfinite(denominator) or denominator <= 0:
        return None
    return float(np.mean(psd[center_mask]) / denominator)


def _empty_band_payload() -> dict[str, Any]:
    return {
        name: {"absolute_power": None, "relative_power": None} for name in _BANDS
    }


def _welch_method_payload() -> dict[str, Any]:
    return {
        "function": "mne.time_frequency.psd_array_welch",
        "fmin_hz": 0.5,
        "fmax_hz": "min(100.0,sfreq/2.0)",
        "segment_seconds": 2.0,
        "n_fft": "n_per_seg",
        "n_overlap": "floor(n_per_seg/2)",
        "window": "hann",
        "average": "median",
        "remove_dc": True,
        "n_jobs": 1,
        "output": "power",
        "band_integration": "trapezoid_over_resolved_bins",
        "line_ratio": "mean_center_power_over_mean_combined_sideband_power",
        "generic_pass_fail_threshold": None,
    }


def _relative_rms_advisories(rows: list[dict[str, Any]], *, np: Any) -> list[dict[str, Any]]:
    by_type_channel: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        value = row["metrics"].get("centered_rms")
        if value is not None and value > 0:
            by_type_channel.setdefault(row["channel_type"], {}).setdefault(
                row["channel_name"], []
            ).append(float(value))
    advisories: list[dict[str, Any]] = []
    for channel_type in sorted(by_type_channel):
        channels = by_type_channel[channel_type]
        if len(channels) < 8:
            continue
        names = sorted(channels)
        log_rms = np.asarray(
            [math.log(float(np.median(channels[name]))) for name in names],
            dtype=np.float64,
        )
        center = float(np.median(log_rms))
        mad = float(np.median(np.abs(log_rms - center)))
        if mad <= 0:
            continue
        robust_z = 0.6744897501960817 * (log_rms - center) / mad
        for name, score in zip(names, robust_z):
            if abs(float(score)) > 6.0:
                advisories.append(
                    {
                        "code": "relative_rms_outlier_candidate",
                        "channel_name": name,
                        "channel_type": channel_type,
                        "absolute_robust_z": _number(abs(float(score))),
                        "declares_bad_channel": False,
                    }
                )
    return advisories


def _geometry_summary(raw: Any, *, selected_indices: list[int], np: Any) -> dict[str, Any]:
    payload = []
    finite_count = 0
    coordinate_frames: set[str] = set()
    for index in selected_indices:
        channel = raw.info["chs"][index]
        loc = np.asarray(channel["loc"], dtype=np.float64)
        position = loc[:3]
        available = bool(np.all(np.isfinite(position)) and np.linalg.norm(position) > 0)
        if available:
            finite_count += 1
        frame = _coordinate_frame_name(int(channel.get("coord_frame", 0)))
        coordinate_frames.add(frame)
        payload.append(
            {
                "channel_index": index,
                "coord_frame": frame,
                "loc": [_hash_float(value) for value in loc.tolist()],
            }
        )
    if finite_count == len(selected_indices):
        status = "available_all_selected_channels"
    elif finite_count == 0:
        status = "unavailable"
    else:
        status = "partially_available"
    return {
        "status": status,
        "selected_channel_count": len(selected_indices),
        "finite_location_count": finite_count,
        "coordinate_frames": sorted(coordinate_frames),
        "payload_sha256": _sha256_json(payload),
        "exact_coordinates_emitted": False,
    }


def _coordinate_frame_name(value: int) -> str:
    return {
        0: "unknown",
        1: "device",
        2: "isotrak",
        4: "head",
        5: "mri",
        6: "mri_slice",
        7: "mri_display",
        8: "ctf_device",
        9: "ctf_head",
        10: "unknown",
    }.get(value, f"frame_{value}")


def _reference_summary(raw: Any, *, selected_types: list[str]) -> dict[str, Any]:
    eeg_like = any(
        channel_type in {"eeg", "eog", "ecg", "emg", "seeg", "ecog", "dbs"}
        for channel_type in selected_types
    )
    custom = int(raw.info.get("custom_ref_applied", 0))
    if not eeg_like:
        status = "not_applicable_no_electrical_channels"
    elif custom:
        status = "custom_reference_applied_in_source"
    else:
        status = "unknown"
    return {"status": status, "custom_ref_applied": bool(custom)}


def _filter_projector_summary(raw: Any) -> dict[str, Any]:
    sfreq = float(raw.info["sfreq"])
    highpass = float(raw.info.get("highpass", 0.0) or 0.0)
    lowpass = float(raw.info.get("lowpass", sfreq / 2.0) or sfreq / 2.0)
    line_freq = raw.info.get("line_freq")
    projectors = list(raw.info.get("projs", []))
    active_count = sum(bool(projector.get("active", False)) for projector in projectors)
    present = bool(highpass > 0 or lowpass < sfreq / 2.0 - 1e-12 or projectors)
    compensation_grade = getattr(raw, "compensation_grade", None)
    return {
        "highpass_hz": _number(highpass),
        "lowpass_hz": _number(lowpass),
        "line_frequency_hz": _number(line_freq),
        "projector_count": len(projectors),
        "active_projector_count": active_count,
        "compensation_grade": compensation_grade,
        "source_filters_or_projectors_present": present,
    }


def _annotation_summary(raw: Any, *, np: Any) -> dict[str, Any]:
    annotations = raw.annotations
    count = len(annotations)
    durations = np.asarray(annotations.duration, dtype=np.float64)
    onsets = np.asarray(annotations.onset, dtype=np.float64)
    channel_specific_count = sum(bool(names) for names in annotations.ch_names)
    if count:
        span = float(np.max(onsets + durations) - np.min(onsets))
        duration_total = float(np.sum(durations))
        duration_min = float(np.min(durations))
        duration_max = float(np.max(durations))
        status = "present_aggregate_only"
    else:
        span = None
        duration_total = 0.0
        duration_min = None
        duration_max = None
        status = "absent_by_fixture_contract"
    return {
        "status": status,
        "count": count,
        "unique_description_count": len(set(annotations.description.tolist())),
        "duration_total_sec": _number(duration_total),
        "duration_min_sec": _number(duration_min),
        "duration_max_sec": _number(duration_max),
        "onset_span_sec": _number(span),
        "channel_specific_count": channel_specific_count,
        "original_time_present": annotations.orig_time is not None,
        "descriptions_redacted": True,
        "individual_timestamps_emitted": False,
    }


def _unit_rows(
    raw: Any,
    selected_names: list[str],
    selected_types: list[str],
) -> list[dict[str, Any]]:
    original = getattr(raw, "_orig_units", None)
    original = original if isinstance(original, dict) else {}
    rows = []
    for name, channel_type in zip(selected_names, selected_types):
        source_unit = original.get(name)
        if source_unit is not None:
            source_unit = str(source_unit).replace("µ", "u").replace("μ", "u")
        rows.append(
            {
                "channel_name": name,
                "channel_type": channel_type,
                "mne_si_unit": _SI_UNITS.get(channel_type),
                "source_unit": source_unit,
                "source_unit_available": source_unit is not None,
            }
        )
    return rows


def _source_state(raw: Any, *, channel_types: list[str], np: Any) -> dict[str, Any]:
    annotations = raw.annotations
    projectors = [
        {
            "active": bool(projector.get("active", False)),
            "description": str(projector.get("desc", "")),
            "kind": int(projector.get("kind", 0)),
        }
        for projector in raw.info.get("projs", [])
    ]
    geometry = [
        {
            "coord_frame": int(channel.get("coord_frame", 0)),
            "loc": [_hash_float(value) for value in np.asarray(channel["loc"]).tolist()],
        }
        for channel in raw.info["chs"]
    ]
    return {
        "channel_names": list(raw.ch_names),
        "channel_types": list(channel_types),
        "bads": list(raw.info.get("bads", [])),
        "annotations": {
            "onsets": [_hash_float(value) for value in annotations.onset.tolist()],
            "durations": [_hash_float(value) for value in annotations.duration.tolist()],
            "descriptions": annotations.description.tolist(),
            "orig_time": str(annotations.orig_time) if annotations.orig_time is not None else None,
            "ch_names": [list(names) for names in annotations.ch_names],
        },
        "projectors": projectors,
        "custom_ref_applied": int(raw.info.get("custom_ref_applied", 0)),
        "compensation_grade": getattr(raw, "compensation_grade", None),
        "sampling_rate_hz": _hash_float(raw.info["sfreq"]),
        "sample_count": int(raw.n_times),
        "first_sample": int(raw.first_samp),
        "geometry": geometry,
    }


def _validate_signal_quality_audit(
    audit: dict[str, Any],
    *,
    report_file: Path,
    report_bytes: bytes,
    audit_file: Path,
    audit_bytes: bytes,
) -> None:
    if audit.get("schema") != {"name": AUDIT_SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("Unsupported signal-quality audit schema.")
    resources = audit.get("resources", {})
    if resources.get("audit_json_bytes") != len(audit_bytes):
        raise ValueError("Signal-quality audit byte count mismatch.")
    if resources.get("total_output_bytes", 0) > resources.get("max_output_bytes", -1):
        raise ValueError("Signal-quality audit exceeds output cap.")
    if resources.get("output_cap_passed") is not True:
        raise ValueError("Signal-quality audit output cap did not pass.")
    if resources.get("runtime_cap_passed") is not True:
        raise ValueError("Signal-quality audit runtime cap did not pass.")
    if resources.get("peak_rss_cap_passed") is not True:
        raise ValueError("Signal-quality audit peak-RSS cap did not pass.")
    artifacts = audit.get("artifacts", {})
    report_artifact = artifacts.get(ARTIFACT_JSON, {})
    if report_artifact.get("bytes") != len(report_bytes):
        raise ValueError("Signal-quality report artifact byte mismatch.")
    if report_artifact.get("sha256") != _sha256_bytes(report_bytes):
        raise ValueError("Signal-quality report artifact hash mismatch.")
    markdown_file = report_file.with_name(ARTIFACT_MARKDOWN)
    if not markdown_file.is_file() or markdown_file.is_symlink():
        raise ValueError("Signal-quality Markdown artifact is missing or unsafe.")
    markdown_bytes = markdown_file.read_bytes()
    markdown_artifact = artifacts.get(ARTIFACT_MARKDOWN, {})
    if markdown_artifact.get("bytes") != len(markdown_bytes):
        raise ValueError("Signal-quality Markdown artifact byte mismatch.")
    if markdown_artifact.get("sha256") != _sha256_bytes(markdown_bytes):
        raise ValueError("Signal-quality Markdown artifact hash mismatch.")
    if artifacts.get(ARTIFACT_AUDIT, {}).get("bytes") != len(audit_bytes):
        raise ValueError("Signal-quality audit artifact byte mismatch.")
    expected_total = len(report_bytes) + len(markdown_bytes) + len(audit_bytes)
    if resources.get("total_output_bytes") != expected_total:
        raise ValueError("Signal-quality total output byte mismatch.")
    if audit_file.name != ARTIFACT_AUDIT:
        raise ValueError("Signal-quality audit filename is not registered.")
    access = audit.get("access_counts", {})
    if access.get("output_bytes") != expected_total:
        raise ValueError("Signal-quality audit output access count mismatch.")
    for key in (
        "real_data_reads",
        "consumed_cache_reads",
        "target_label_values_emitted_or_used",
        "model_runs",
        "training_runs",
        "network_calls",
    ):
        if access.get(key) != 0:
            raise ValueError(f"Signal-quality audit has forbidden access count: {key}")


def _validate_output_directory(path: Path, *, overwrite: bool) -> None:
    registered = {ARTIFACT_JSON, ARTIFACT_MARKDOWN, ARTIFACT_AUDIT}
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise ValueError("Output path must be a real directory.")
        existing = list(path.iterdir())
        if existing and not overwrite:
            raise FileExistsError("Refusing to write into a nonempty output directory.")
        for candidate in existing:
            if candidate.name in registered and candidate.is_symlink():
                raise ValueError("Registered output artifact cannot be a symlink.")


def _write_artifact(path: Path, payload: bytes, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite artifact: {path.name}")
    if path.is_symlink():
        raise ValueError(f"Refusing to write through symlink: {path.name}")
    path.write_bytes(payload)


def _safe_json_file(path: str | Path, *, max_bytes: int) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise ValueError("JSON input cannot be a symlink.")
    if not candidate.is_file():
        raise FileNotFoundError(f"JSON input is not a regular file: {candidate.name}")
    if candidate.stat().st_size > max_bytes:
        raise ValueError("JSON input exceeds the configured size cap.")
    return candidate.resolve(strict=True)


def _safe_relative_path(value: Any) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError("Unsafe relative path in source manifest.")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("~"):
        raise ValueError("Unsafe relative path in source manifest.")
    return path


def _enforce_single_thread_environment() -> None:
    for name in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        value = os.environ.get(name)
        if value not in (None, "1"):
            raise ValueError(f"RW2 requires {name}=1 when the variable is set.")


def _type_counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = value if value in _NON_BRAIN_CHANNEL_TYPES else f"unsupported:{value}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _report_payload_sha256(report: dict[str, Any]) -> str:
    payload = json.loads(json.dumps(report))
    payload["hashes"]["report_payload_sha256"] = None
    return _sha256_json(payload)


def _manifest_payload_sha256(manifest: dict[str, Any]) -> str:
    payload = json.loads(json.dumps(manifest))
    payload["hashes"]["manifest_payload_sha256"] = None
    return _sha256_json(payload)


def _json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_json(payload: Any) -> str:
    compact = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return _sha256_bytes(compact)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _number(value: Any) -> float | int | None:
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    if number == 0:
        return 0.0
    return float(f"{number:.15g}")


def _hash_float(value: Any) -> float | str:
    number = float(value)
    if math.isnan(number):
        return "nan"
    if math.isinf(number):
        return "inf" if number > 0 else "-inf"
    return number


def _all_mapping_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.append(str(key))
            keys.extend(_all_mapping_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.extend(_all_mapping_keys(nested))
    return keys


def _reject_absolute_paths(value: Any) -> None:
    if isinstance(value, dict):
        for nested in value.values():
            _reject_absolute_paths(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_absolute_paths(nested)
    elif isinstance(value, str):
        if value.startswith(("/", "file://", "~")) or re.match(r"^[A-Za-z]:[\\/]", value):
            raise ValueError("Artifact contains an absolute path.")


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _peak_rss_bytes() -> int | None:
    try:
        import resource
    except ImportError:  # pragma: no cover
        return None
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return peak if sys.platform == "darwin" else peak * 1024
