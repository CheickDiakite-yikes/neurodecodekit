"""Resource and CTC-feasibility comparison across sentence-cache sampling rates."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import os
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from neurodecodekit.cache.sentence_npz import (
    load_sentence_npz_cache,
    write_sentence_cache_metadata_sidecar,
)
from neurodecodekit.preprocess.ctc_text import minimum_ctc_input_steps


SWEEP_SCHEMA_NAME = "b2q-sampling-rate-sweep"
SWEEP_SCHEMA_VERSION = 0
OFFICIAL_V2_RATE_HZ = 100.0
OFFICIAL_V2_LOWPASS_HZ = 45.0
OFFICIAL_B2Q_COMMIT = "3bf5a4099ca0d23bbe994b2287905760236e56e0"
OFFICIAL_V2_TEMPORAL_KERNEL_SIZE = 16
OFFICIAL_V2_TEMPORAL_STRIDE = 4
OFFICIAL_V2_CONFIG_URL = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_B2Q_COMMIT}/brain2qwerty_v2/config/xp_config.py#L45-L59"
)
OFFICIAL_V2_MODEL_CONFIG_URL = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_B2Q_COMMIT}/brain2qwerty_v2/config/model_config.py#L33-L50"
)
OFFICIAL_V2_LENGTH_CODE_URL = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_B2Q_COMMIT}/brain2qwerty_v2/utils.py#L72-L78"
)
OFFICIAL_V2_PAPER_URL = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
MNE_RESAMPLING_URL = "https://mne.tools/stable/help/faq.html#resampling-and-decimating-data"
THREAD_ENV_VARS = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)

ExtractionWorker = Callable[..., dict[str, Any]]


def run_sampling_rate_sweep(
    *,
    raw_path: str | Path,
    events_path: str | Path,
    out_dir: str | Path,
    rates_hz: Iterable[float] = (100.0, 50.0, 25.0),
    pre_context_sec: float = 0.4,
    post_context_sec: float = 0.45,
    picks: str | None = "meg",
    max_channels: int | None = 16,
    stim_channel: str = "STI101",
    l_freq: float | None = 0.5,
    h_freq: float | None = 45.0,
    notch_freq: float | None = 50.0,
    robust_scale: bool = True,
    clamp: float | None = 5.0,
    max_sentences: int | None = None,
    report_json_path: str | Path | None = None,
    report_markdown_path: str | Path | None = None,
    overwrite: bool = False,
    extraction_worker: ExtractionWorker | None = None,
) -> dict[str, Any]:
    """Extract each rate in isolation, compare caches, and write one audit report."""

    raw_file = Path(raw_path)
    events_file = Path(events_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw FIF file not found: {raw_file}")
    if not events_file.exists():
        raise FileNotFoundError(f"MAT event/log file not found: {events_file}")
    if max_channels is None:
        raise ValueError("isolated sampling-rate sweeps require an explicit max_channels cap")
    required_numeric_options = {
        "l_freq": l_freq,
        "h_freq": h_freq,
        "notch_freq": notch_freq,
        "clamp": clamp,
    }
    missing_options = [name for name, value in required_numeric_options.items() if value is None]
    if missing_options:
        raise ValueError(
            "isolated sampling-rate sweeps require explicit numeric preprocessing options: "
            f"{missing_options}"
        )
    rates = normalize_sampling_rates(rates_hz)
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = Path(report_json_path) if report_json_path else output_dir / "sweep.json"
    markdown_path = (
        Path(report_markdown_path)
        if report_markdown_path
        else output_dir / "sweep.md"
    )

    artifacts: dict[float, dict[str, Path]] = {}
    planned_paths = [json_path, markdown_path]
    for rate in rates:
        slug = sampling_rate_slug(rate)
        cache_path = output_dir / f"sentence_{slug}hz.npz"
        summary_path = output_dir / f"sentence_{slug}hz.extraction.json"
        metadata_path = output_dir / f"sentence_{slug}hz.metadata.json"
        log_path = output_dir / f"sentence_{slug}hz.worker.log"
        artifacts[rate] = {
            "cache": cache_path,
            "summary": summary_path,
            "metadata": metadata_path,
            "log": log_path,
        }
        planned_paths.extend((cache_path, summary_path, metadata_path, log_path))
    existing = [str(path) for path in planned_paths if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Sampling-rate sweep refuses to overwrite existing artifacts without "
            f"overwrite=True: {existing}"
        )

    options = {
        "raw_path": raw_file,
        "events_path": events_file,
        "pre_context_sec": pre_context_sec,
        "post_context_sec": post_context_sec,
        "picks": picks,
        "max_channels": max_channels,
        "stim_channel": stim_channel,
        "l_freq": l_freq,
        "h_freq": h_freq,
        "notch_freq": notch_freq,
        "robust_scale": robust_scale,
        "clamp": clamp,
        "max_sentences": max_sentences,
    }
    worker = extraction_worker or _run_isolated_extraction
    extraction_summaries: dict[float, dict[str, Any]] = {}
    started_at = time.perf_counter()
    for rate in rates:
        paths = artifacts[rate]
        extraction_summaries[rate] = worker(
            rate_hz=rate,
            cache_path=paths["cache"],
            summary_path=paths["summary"],
            log_path=paths["log"],
            options=options,
        )
        write_sentence_cache_metadata_sidecar(paths["cache"], paths["metadata"])
    total_runtime_sec = round(time.perf_counter() - started_at, 6)

    report = build_sampling_rate_report(
        raw_path=raw_file,
        events_path=events_file,
        rates_hz=rates,
        artifacts=artifacts,
        extraction_summaries=extraction_summaries,
        total_runtime_sec=total_runtime_sec,
        configured_h_freq=h_freq,
    )
    report["artifact_paths"]["report_json"] = str(json_path)
    report["artifact_paths"]["report_markdown"] = str(markdown_path)
    write_sampling_rate_report_json(report, json_path)
    write_sampling_rate_report_markdown(report, markdown_path)
    return report


def normalize_sampling_rates(rates_hz: Iterable[float]) -> list[float]:
    rates = [float(value) for value in rates_hz]
    if len(rates) < 2:
        raise ValueError("sampling-rate sweep requires at least two rates")
    if any(not math.isfinite(value) or value <= 0 for value in rates):
        raise ValueError("sampling rates must be finite and > 0")
    if len(set(rates)) != len(rates):
        raise ValueError("sampling rates must be unique")
    return sorted(rates, reverse=True)


def sampling_rate_slug(rate_hz: float) -> str:
    return f"{float(rate_hz):g}".replace(".", "p")


def build_sampling_rate_report(
    *,
    raw_path: str | Path,
    events_path: str | Path,
    rates_hz: Iterable[float],
    artifacts: dict[float, dict[str, Path]],
    extraction_summaries: dict[float, dict[str, Any]],
    total_runtime_sec: float,
    configured_h_freq: float | None,
) -> dict[str, Any]:
    """Load all rate caches and build a strict comparison report."""

    rates = normalize_sampling_rates(rates_hz)
    reference_rate = rates[0]
    loaded = {rate: load_sentence_npz_cache(artifacts[rate]["cache"]) for rate in rates}
    reference = loaded[reference_rate]
    reference_cache_bytes = int(reference.summary.bytes or 0)
    if reference_cache_bytes <= 0:
        raise ValueError(f"Reference cache size is unavailable for {reference.path}.")
    rows = []
    for rate in rates:
        row = _analyze_rate_cache(
            expected_rate_hz=rate,
            loaded=loaded[rate],
            extraction_summary=extraction_summaries[rate],
            configured_h_freq=configured_h_freq,
        )
        row["cache_byte_retention_vs_reference"] = round(
            row["cache_bytes"] / reference_cache_bytes,
            8,
        )
        row["valid_timepoint_retention_vs_reference"] = round(
            row["total_valid_timepoints"] / reference.summary.total_valid_timepoints,
            8,
        )
        row["max_start_boundary_shift_ms_vs_reference"] = _max_abs_delta_ms(
            reference.sentence_start_sec,
            loaded[rate].sentence_start_sec,
        )
        row["max_end_boundary_shift_ms_vs_reference"] = _max_abs_delta_ms(
            reference.sentence_end_sec,
            loaded[rate].sentence_end_sec,
        )
        rows.append(row)

    identity_fields = {
        "trial_indices": "trial_indices_sha256",
        "typed_targets": "target_texts_sha256",
        "reference_texts": "reference_texts_sha256",
        "mat_responses": "mat_response_texts_sha256",
        "channel_names": "channel_names_sha256",
    }
    exact_identity = {
        name: len({row[hash_field] for row in rows}) == 1
        for name, hash_field in identity_fields.items()
    }
    duration_values = [row["total_valid_duration_sec"] for row in rows]
    duration_delta_sec = max(duration_values) - min(duration_values)
    reference_sentence_count = reference.summary.n_sentences
    consistency = {
        "reference_rate_hz": reference_rate,
        "sentence_counts_match": len({row["n_sentences"] for row in rows}) == 1,
        "channel_counts_match": len({row["n_channels"] for row in rows}) == 1,
        "exact_identity": exact_identity,
        "all_identity_fields_match": all(exact_identity.values()),
        "max_total_valid_duration_delta_sec": round(duration_delta_sec, 8),
        "mean_duration_delta_per_sentence_ms": round(
            duration_delta_sec * 1000.0 / reference_sentence_count,
            8,
        ),
    }
    warnings = [
        "resource_and_ctc_feasibility_sweep_only_no_neural_accuracy",
        "same_single_block_is_not_a_generalization_evaluation",
        "rates_run_sequentially_in_isolated_one_thread_workers",
        "lower_rates_reduce_bandwidth_and_boundary_precision_not_only_storage",
        "real_cache_records_physical_typing_not_arbitrary_thoughts",
    ]
    if OFFICIAL_V2_RATE_HZ not in rates:
        warnings.append("official_v2_100hz_reference_rate_missing")
    if not consistency["all_identity_fields_match"]:
        warnings.append("rate_caches_do_not_share_exact_trial_text_channel_identity")
    if not consistency["sentence_counts_match"] or not consistency["channel_counts_match"]:
        warnings.append("rate_cache_shape_identity_failed")
    for row in rows:
        if row["ctc_infeasible_rows_stride_1"]:
            warnings.append(f"ctc_stride_1_infeasible_at_{sampling_rate_slug(row['rate_hz'])}hz")
        if row["official_v2_ctc_infeasible_rows"]:
            warnings.append(
                "official_v2_kernel16_stride4_ctc_infeasible_at_"
                f"{sampling_rate_slug(row['rate_hz'])}hz:"
                f"{row['official_v2_ctc_infeasible_rows']}"
            )

    extraction_runtime = sum(row["extraction_runtime_sec"] for row in rows)
    cache_bytes = sum(row["cache_bytes"] for row in rows)
    peak_rss_values = [row["worker_peak_rss_bytes"] for row in rows]
    official_v2_incompatible_rates = [
        row["rate_hz"] for row in rows if row["official_v2_ctc_infeasible_rows"]
    ]
    report = {
        "schema": {"name": SWEEP_SCHEMA_NAME, "version": SWEEP_SCHEMA_VERSION},
        "proof_posture": (
            "real-cache resource and CTC-length feasibility; no model training, decoding "
            "accuracy, causal latency, or generalization claim"
        ),
        "run": {
            "raw_path": str(Path(raw_path)),
            "events_path": str(Path(events_path)),
            "rates_hz": rates,
            "reference_rate_hz": reference_rate,
            "execution_mode": "sequential-isolated-worker-processes",
            "worker_thread_cap": 1,
            "thread_environment_variables": list(THREAD_ENV_VARS),
            "total_runtime_sec": total_runtime_sec,
            "summed_extraction_runtime_sec": round(extraction_runtime, 6),
            "peak_worker_rss_bytes": max(
                (value for value in peak_rss_values if value is not None),
                default=None,
            ),
            "total_cache_bytes": cache_bytes,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "dependency_versions": {
                name: _dependency_version(name) for name in ("mne", "numpy", "scipy")
            },
        },
        "research_context": {
            "official_v2_reference_rate_hz": OFFICIAL_V2_RATE_HZ,
            "official_v2_configured_lowpass_hz": OFFICIAL_V2_LOWPASS_HZ,
            "official_brain2qwerty_commit": OFFICIAL_B2Q_COMMIT,
            "official_v2_config_source": OFFICIAL_V2_CONFIG_URL,
            "official_v2_model_config_source": OFFICIAL_V2_MODEL_CONFIG_URL,
            "official_v2_output_length_source": OFFICIAL_V2_LENGTH_CODE_URL,
            "official_v2_paper": OFFICIAL_V2_PAPER_URL,
            "official_v2_temporal_downsampling": {
                "kernel_size": OFFICIAL_V2_TEMPORAL_KERNEL_SIZE,
                "stride": OFFICIAL_V2_TEMPORAL_STRIDE,
                "output_length_formula": "(input_steps - 16) // 4 + 1",
            },
            "mne_resampling_source": MNE_RESAMPLING_URL,
            "resampling_note": (
                "MNE Raw.resample applies an anti-alias low-pass filter. Effective upper "
                "bandwidth is therefore bounded by the lower of the configured low-pass and "
                "the target-rate Nyquist frequency."
            ),
        },
        "consistency": consistency,
        "rates": rows,
        "decision": {
            "status": "resource_characterized_no_rate_selected",
            "reason": (
                "A rate cannot be selected from bytes and CTC length feasibility alone. "
                "Accuracy comparison requires a leakage-resistant second block or session."
            ),
            "official_v2_temporal_contract_incompatible_rates_hz": (
                official_v2_incompatible_rates
            ),
            "architecture_constraint": (
                "Rates listed as incompatible cannot reuse the official no-padding "
                "kernel-16, stride-4 temporal downsampling while satisfying every local "
                "CTC target length. This is a structural constraint, not an accuracy score."
            ),
        },
        "artifact_paths": {
            "rate_artifacts": {
                sampling_rate_slug(rate): {
                    name: str(path) for name, path in artifacts[rate].items()
                }
                for rate in rates
            }
        },
        "warnings": list(dict.fromkeys(warnings)),
    }
    return report


def write_sampling_rate_report_json(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sampling_rate_report_markdown(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_sampling_rate_report_markdown(report), encoding="utf-8")


def render_sampling_rate_report_markdown(report: dict[str, Any]) -> str:
    run = report["run"]
    consistency = report["consistency"]
    incompatible_rates = ", ".join(
        f"{rate:g} Hz"
        for rate in report["decision"][
            "official_v2_temporal_contract_incompatible_rates_hz"
        ]
    ) or "none"
    lines = [
        "# Sampling-Rate Sweep",
        "",
        f"**Proof posture:** {report['proof_posture']}.",
        "",
        f"- Raw: `{run['raw_path']}`",
        f"- Events: `{run['events_path']}`",
        f"- Execution: {run['execution_mode']}, {run['worker_thread_cap']} thread per worker",
        f"- Total wall time: {run['total_runtime_sec']:.3f} sec",
        f"- Total cache bytes: {_format_bytes(run['total_cache_bytes'])}",
        f"- Peak worker RSS: {_format_optional_bytes(run['peak_worker_rss_bytes'])}",
        "",
        "## Rate Comparison",
        "",
        (
            "| Rate | Effective bandwidth | Cache | Cache vs ref | Runtime | Peak RSS | "
            "Shape | Boundary grid | CTC s1 | v2 k16/s4 | s1 margin | v2 margin | "
            "Min ratio | RMS | Clamp |"
        ),
        (
            "|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|"
            "---:|---:|---:|"
        ),
    ]
    for row in report["rates"]:
        shape = "x".join(str(value) for value in row["signals_shape"])
        clamp_fraction = row["clamp_saturation_fraction"]
        clamp_text = "n/a" if clamp_fraction is None else f"{100 * clamp_fraction:.3f}%"
        lines.append(
            "| "
            f"{row['rate_hz']:g} Hz | {row['effective_upper_bandwidth_hz']:g} Hz | "
            f"{_format_bytes(row['cache_bytes'])} | "
            f"{100 * row['cache_byte_retention_vs_reference']:.1f}% | "
            f"{row['extraction_runtime_sec']:.3f}s | "
            f"{_format_optional_bytes(row['worker_peak_rss_bytes'])} | `{shape}` | "
            f"{row['sample_period_ms']:.1f}ms | "
            f"{row['ctc_feasible_rows_stride_1']}/{row['n_sentences']} | "
            f"{row['official_v2_ctc_feasible_rows']}/{row['n_sentences']} | "
            f"{row['minimum_ctc_margin_steps']} | "
            f"{row['official_v2_minimum_ctc_margin_steps']} | "
            f"{row['minimum_input_to_required_ctc_ratio']:.2f}x | "
            f"{row['valid_signal_rms']:.4f} | {clamp_text} |"
        )
    lines.extend(
        [
            "",
            "## Identity And Timing",
            "",
            f"- Sentence counts match: `{consistency['sentence_counts_match']}`",
            f"- Channel counts match: `{consistency['channel_counts_match']}`",
            f"- Exact trial/text/channel identity: `{consistency['all_identity_fields_match']}`",
            (
                "- Maximum total-valid-duration delta: "
                f"`{consistency['max_total_valid_duration_delta_sec']:.6f} sec`"
            ),
            (
                "- Mean duration delta per sentence: "
                f"`{consistency['mean_duration_delta_per_sentence_ms']:.3f} ms`"
            ),
        ]
    )
    for row in report["rates"]:
        lines.append(
            f"- {row['rate_hz']:g} Hz boundary shift vs reference: "
            "start "
            f"`{_format_optional_float(row['max_start_boundary_shift_ms_vs_reference'])} ms`, "
            "end "
            f"`{_format_optional_float(row['max_end_boundary_shift_ms_vs_reference'])} ms`"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"**{report['decision']['status']}**: {report['decision']['reason']}",
            "",
            (
                "- Official v2 temporal-contract incompatible rates: `"
                + incompatible_rates
                + "`"
            ),
            f"- {report['decision']['architecture_constraint']}",
            "",
            "## Research Sources",
            "",
            (
                "- Official Brain2Qwerty v2 preprocessing config: "
                f"{report['research_context']['official_v2_config_source']}"
            ),
            (
                "- Official v2 temporal downsampling config: "
                f"{report['research_context']['official_v2_model_config_source']}"
            ),
            (
                "- Official v2 output-length implementation: "
                f"{report['research_context']['official_v2_output_length_source']}"
            ),
            (
                "- MNE resampling and anti-alias behavior: "
                f"{report['research_context']['mne_resampling_source']}"
            ),
            "",
            "## Warnings",
            "",
        ]
    )
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _analyze_rate_cache(
    *,
    expected_rate_hz: float,
    loaded,
    extraction_summary: dict[str, Any],
    configured_h_freq: float | None,
) -> dict[str, Any]:
    np = _require_numpy()
    extraction_params = loaded.metadata.get("extraction_params") or {}
    metadata_rate = float(extraction_params.get("sfreq"))
    if not math.isclose(metadata_rate, expected_rate_hz, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(
            f"Cache sampling rate mismatch: expected {expected_rate_hz}, got {metadata_rate}."
        )
    summary_rate = float(extraction_summary.get("sfreq", expected_rate_hz))
    if not math.isclose(summary_rate, expected_rate_hz, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(
            f"Extraction summary rate mismatch: expected {expected_rate_hz}, got {summary_rate}."
        )

    metadata_h_freq = extraction_params.get("h_freq")
    if configured_h_freq is None:
        if metadata_h_freq is not None:
            raise ValueError(
                f"Cache low-pass mismatch: expected disabled, got {metadata_h_freq}."
            )
    elif metadata_h_freq is None or not math.isclose(
        float(metadata_h_freq),
        float(configured_h_freq),
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError(
            f"Cache low-pass mismatch: expected {configured_h_freq}, got {metadata_h_freq}."
        )
    robust_scale_enabled = bool(extraction_params.get("robust_scale", True))
    clamp = extraction_params.get("clamp") if robust_scale_enabled else None
    valid_value_count = 0
    absolute_sum = 0.0
    square_sum = 0.0
    max_abs = 0.0
    clamp_count = 0
    required_steps = []
    for row_index, input_length_value in enumerate(loaded.input_lengths.tolist()):
        input_length = int(input_length_value)
        valid = loaded.signals[row_index, :, :input_length].astype("float64", copy=False)
        absolute = np.abs(valid)
        valid_value_count += int(valid.size)
        absolute_sum += float(absolute.sum(dtype="float64"))
        square_sum += float(np.square(valid).sum(dtype="float64"))
        max_abs = max(max_abs, float(absolute.max()))
        if clamp is not None:
            clamp_count += int(np.count_nonzero(absolute >= float(clamp) - 1e-6))
        target_length = int(loaded.target_lengths[row_index])
        ids = loaded.target_token_ids[row_index, :target_length].tolist()
        required_steps.append(minimum_ctc_input_steps(ids))

    input_lengths = loaded.input_lengths.astype("int64", copy=False)
    required = np.asarray(required_steps, dtype="int64")
    margins = input_lengths - required
    ratios = input_lengths / required
    target_ratios = input_lengths / loaded.target_lengths.astype("int64", copy=False)
    official_v2_output_lengths = np.asarray(
        [
            temporal_conv_output_length(
                int(value),
                kernel_size=OFFICIAL_V2_TEMPORAL_KERNEL_SIZE,
                stride=OFFICIAL_V2_TEMPORAL_STRIDE,
            )
            for value in input_lengths.tolist()
        ],
        dtype="int64",
    )
    official_v2_margins = official_v2_output_lengths - required
    cache_bytes = int(loaded.summary.bytes or 0)
    if cache_bytes <= 0:
        raise ValueError(f"Cache size is unavailable for {loaded.path}.")
    nyquist_hz = expected_rate_hz / 2.0
    effective_bandwidth = (
        nyquist_hz if configured_h_freq is None else min(float(configured_h_freq), nyquist_hz)
    )
    return {
        "rate_hz": expected_rate_hz,
        "nyquist_hz": nyquist_hz,
        "effective_upper_bandwidth_hz": effective_bandwidth,
        "configured_lowpass_hz": metadata_h_freq,
        "robust_scale_enabled": robust_scale_enabled,
        "effective_bandwidth_retention_vs_official_v2": round(
            effective_bandwidth / OFFICIAL_V2_LOWPASS_HZ,
            8,
        ),
        "sample_period_ms": 1000.0 / expected_rate_hz,
        "cache_path": loaded.path,
        "cache_bytes": cache_bytes,
        "cache_bytes_per_valid_signal_value": round(cache_bytes / valid_value_count, 8),
        "signals_shape": list(loaded.summary.signals_shape),
        "signals_dtype": loaded.summary.signals_dtype,
        "padded_signal_array_bytes": int(loaded.signals.nbytes),
        "n_sentences": loaded.summary.n_sentences,
        "n_channels": loaded.summary.n_channels,
        "max_timepoints": loaded.summary.max_timepoints,
        "total_valid_timepoints": loaded.summary.total_valid_timepoints,
        "total_valid_duration_sec": round(
            loaded.summary.total_valid_timepoints / expected_rate_hz,
            8,
        ),
        "padding_fraction": loaded.summary.padding_fraction,
        "min_input_length": loaded.summary.min_input_length,
        "max_input_length": loaded.summary.max_input_length,
        "min_target_length": loaded.summary.min_target_length,
        "max_target_length": loaded.summary.max_target_length,
        "valid_signal_value_count": valid_value_count,
        "valid_signal_mean_abs": round(absolute_sum / valid_value_count, 8),
        "valid_signal_rms": round(math.sqrt(square_sum / valid_value_count), 8),
        "valid_signal_max_abs": round(max_abs, 8),
        "clamp_value": clamp,
        "clamp_saturation_fraction": (
            round(clamp_count / valid_value_count, 10) if clamp is not None else None
        ),
        "ctc_output_stride": 1,
        "ctc_feasible_rows_stride_1": int((margins >= 0).sum()),
        "ctc_infeasible_rows_stride_1": int((margins < 0).sum()),
        "minimum_required_ctc_steps": int(required.min()),
        "maximum_required_ctc_steps": int(required.max()),
        "minimum_ctc_margin_steps": int(margins.min()),
        "maximum_ctc_margin_steps": int(margins.max()),
        "minimum_input_to_required_ctc_ratio": round(float(ratios.min()), 8),
        "minimum_input_steps_per_target_token": round(float(target_ratios.min()), 8),
        "max_uniform_floor_output_stride": int((input_lengths // required).min()),
        "official_v2_temporal_kernel_size": OFFICIAL_V2_TEMPORAL_KERNEL_SIZE,
        "official_v2_temporal_stride": OFFICIAL_V2_TEMPORAL_STRIDE,
        "official_v2_output_length_min": int(official_v2_output_lengths.min()),
        "official_v2_output_length_max": int(official_v2_output_lengths.max()),
        "official_v2_ctc_feasible_rows": int((official_v2_margins >= 0).sum()),
        "official_v2_ctc_infeasible_rows": int((official_v2_margins < 0).sum()),
        "official_v2_minimum_ctc_margin_steps": int(official_v2_margins.min()),
        "extraction_runtime_sec": float(extraction_summary.get("runtime_sec", 0.0)),
        "worker_peak_rss_bytes": extraction_summary.get("peak_rss_bytes"),
        "trial_indices_sha256": _hash_values(loaded.trial_indices.tolist()),
        "target_texts_sha256": _hash_values(loaded.target_texts.tolist()),
        "reference_texts_sha256": _hash_values(loaded.reference_texts.tolist()),
        "mat_response_texts_sha256": _hash_values(loaded.mat_response_texts.tolist()),
        "channel_names_sha256": _hash_values(loaded.channel_names.tolist()),
    }


def _run_isolated_extraction(
    *,
    rate_hz: float,
    cache_path: Path,
    summary_path: Path,
    log_path: Path,
    options: dict[str, Any],
) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "neurodecodekit.cli",
        "extract-sentence-cache",
        "--raw",
        str(options["raw_path"]),
        "--events",
        str(options["events_path"]),
        "--out",
        str(cache_path),
        "--sfreq",
        f"{rate_hz:g}",
        "--pre-context",
        f"{options['pre_context_sec']:g}",
        "--post-context",
        f"{options['post_context_sec']:g}",
        "--stim-channel",
        str(options["stim_channel"]),
        "--summary-json",
        str(summary_path),
    ]
    _append_optional_argument(command, "--picks", options["picks"])
    _append_optional_argument(command, "--max-channels", options["max_channels"])
    _append_optional_argument(command, "--l-freq", options["l_freq"])
    _append_optional_argument(command, "--h-freq", options["h_freq"])
    _append_optional_argument(command, "--notch-freq", options["notch_freq"])
    _append_optional_argument(command, "--clamp", options["clamp"])
    _append_optional_argument(command, "--max-sentences", options["max_sentences"])
    if not options["robust_scale"]:
        command.append("--no-robust-scale")

    environment = os.environ.copy()
    for name in THREAD_ENV_VARS:
        environment[name] = "1"
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    log_path.write_text(
        f"$ {shlex.join(command)}\n\nSTDOUT\n{completed.stdout}\nSTDERR\n{completed.stderr}",
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Isolated {rate_hz:g} Hz extraction failed with code "
            f"{completed.returncode}; see {log_path}."
        )
    if not summary_path.exists():
        raise RuntimeError(f"Extraction worker did not write summary: {summary_path}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["worker"] = {
        "process_isolated": True,
        "thread_cap": 1,
        "command": shlex.join(command),
        "log_path": str(log_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _append_optional_argument(command: list[str], flag: str, value: object | None) -> None:
    if value is not None:
        command.extend((flag, str(value)))


def temporal_conv_output_length(
    input_length: int,
    *,
    kernel_size: int,
    stride: int,
) -> int:
    """Return the no-padding Conv1d output length used by the official v2 code."""

    if input_length < 1:
        raise ValueError("input_length must be >= 1")
    if kernel_size < 1 or stride < 1:
        raise ValueError("kernel_size and stride must be >= 1")
    if input_length < kernel_size:
        return 0
    return (input_length - kernel_size) // stride + 1


def _hash_values(values: list[object]) -> str:
    encoded = json.dumps(values, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _max_abs_delta_ms(reference, candidate) -> float | None:
    np = _require_numpy()
    if reference.shape != candidate.shape:
        return None
    return round(float(np.max(np.abs(reference - candidate))) * 1000.0, 8)


def _format_bytes(n_bytes: int) -> str:
    size = float(n_bytes)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    raise AssertionError("unreachable")


def _format_optional_bytes(n_bytes: int | None) -> str:
    return "n/a" if n_bytes is None else _format_bytes(n_bytes)


def _format_optional_float(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def _dependency_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Sampling-rate sweeps require NumPy: `pip install numpy`.") from exc
    return np
