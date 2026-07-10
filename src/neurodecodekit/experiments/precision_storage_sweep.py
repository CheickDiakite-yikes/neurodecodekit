"""Resource-bounded precision and storage sweep for sentence signal caches."""

from __future__ import annotations

import json
import math
import platform
import re
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
from neurodecodekit.cache.signal_representation import (
    NON_SIGNAL_ARRAY_NAMES,
    SUPPORTED_SIGNAL_ENCODINGS,
    array_sha256,
    decode_signal_payload,
    encode_signal_payload,
    file_sha256,
    load_signal_representation_cache,
    normalize_signal_encoding,
    write_signal_representation_cache,
    write_signal_representation_metadata_sidecar,
)


SWEEP_SCHEMA_NAME = "b2q-precision-storage-sweep"
SWEEP_SCHEMA_VERSION = 0
DEFAULT_VARIANTS = list(SUPPORTED_SIGNAL_ENCODINGS)
DEFAULT_BANDS_HZ = (
    ("delta_0_5_4", 0.5, 4.0),
    ("theta_4_8", 4.0, 8.0),
    ("alpha_8_13", 8.0, 13.0),
    ("beta_13_30", 13.0, 30.0),
    ("low_gamma_30_45", 30.0, 45.0),
)
ENCODING_BYTES_PER_VALUE = {
    "float32": 4,
    "float16": 2,
    "bfloat16": 2,
    "qint16": 2,
    "qint8": 1,
}

OFFICIAL_V2_PAPER_URL = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
OFFICIAL_V2_COMMIT = "3bf5a4099ca0d23bbe994b2287905760236e56e0"
OFFICIAL_V2_MODEL_CONFIG_URL = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_V2_COMMIT}/brain2qwerty_v2/config/model_config.py"
)
BFLOAT16_PAPER_URL = "https://arxiv.org/abs/1905.12322"
INTEGER_QUANTIZATION_PAPER_URL = (
    "https://openaccess.thecvf.com/content_cvpr_2018/html/"
    "Jacob_Quantization_and_Training_CVPR_2018_paper.html"
)
NUMPY_SAVEZ_URL = (
    "https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html"
)
NUMPY_LOAD_URL = "https://numpy.org/doc/stable/reference/generated/numpy.load.html"


def run_precision_storage_sweep(
    *,
    cache_paths: Iterable[str | Path],
    out_dir: str | Path,
    variants: Iterable[str] = DEFAULT_VARIANTS,
    clip_abs: float = 5.0,
    repetitions: int = 3,
    max_output_mb: float = 96.0,
    allow_clipping: bool = False,
    report_json_path: str | Path | None = None,
    report_markdown_path: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write packed variants sequentially and report fidelity without training a decoder."""

    started_at = time.perf_counter()
    normalized_variants = normalize_variants(variants)
    sources = _load_sources(cache_paths)
    if not np_is_finite_positive(clip_abs):
        raise ValueError("clip_abs must be finite and positive")
    if repetitions < 1 or repetitions > 20:
        raise ValueError("repetitions must be within 1..20")
    if not np_is_finite_positive(max_output_mb):
        raise ValueError("max_output_mb must be finite and positive")

    output_dir = Path(out_dir)
    report_json = Path(report_json_path) if report_json_path else output_dir / "sweep.json"
    report_markdown = (
        Path(report_markdown_path) if report_markdown_path else output_dir / "sweep.md"
    )
    artifact_plan = _artifact_plan(output_dir, sources, normalized_variants)
    planned_paths = [report_json, report_markdown]
    for per_source in artifact_plan.values():
        for artifact in per_source.values():
            planned_paths.extend([artifact["cache"], artifact["metadata"]])

    projected_bytes = _projected_uncompressed_bytes(sources, normalized_variants)
    cap_bytes = int(max_output_mb * 1024 * 1024)
    if projected_bytes > cap_bytes:
        raise ValueError(
            "Projected uncompressed representation artifacts exceed cap: "
            f"{projected_bytes} > {cap_bytes} bytes"
        )
    _prepare_planned_paths(planned_paths, overwrite=overwrite)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    created_paths: list[Path] = []
    try:
        for source in sources:
            source_cache = source["cache"]
            source_sha256 = source["sha256"]
            sfreq = _sampling_rate_hz(source_cache)
            source_identity = {
                name: array_sha256(getattr(source_cache, name))
                for name in NON_SIGNAL_ARRAY_NAMES
            }
            for encoding in normalized_variants:
                artifact = artifact_plan[source["label"]][encoding]
                encode_started = time.perf_counter()
                payload, encoding_metadata = encode_signal_payload(
                    source_cache.signals,
                    encoding,
                    clip_abs=clip_abs,
                    allow_clipping=allow_clipping,
                )
                encode_time_sec = time.perf_counter() - encode_started

                write_started = time.perf_counter()
                write_signal_representation_cache(
                    artifact["cache"],
                    source_cache=source_cache,
                    signal_payload=payload,
                    encoding_metadata=encoding_metadata,
                    source_sha256=source_sha256,
                )
                write_validate_time_sec = time.perf_counter() - write_started
                created_paths.append(artifact["cache"])

                decode_times = []
                for _ in range(repetitions):
                    decode_started = time.perf_counter()
                    decode_signal_payload(payload, encoding_metadata)
                    decode_times.append(time.perf_counter() - decode_started)

                loaded = None
                load_times = []
                for _ in range(repetitions):
                    load_started = time.perf_counter()
                    loaded = load_signal_representation_cache(artifact["cache"])
                    load_times.append(time.perf_counter() - load_started)
                assert loaded is not None

                identity_hashes = {
                    name: array_sha256(getattr(loaded, name))
                    for name in NON_SIGNAL_ARRAY_NAMES
                }
                identity_checks = {
                    name: identity_hashes[name] == source_identity[name]
                    for name in NON_SIGNAL_ARRAY_NAMES
                }
                reconstruction = analyze_signal_reconstruction(
                    source_cache.signals,
                    loaded.signals,
                    source_cache.input_lengths,
                    channel_names=source_cache.channel_names.tolist(),
                    sfreq=sfreq,
                )
                write_signal_representation_metadata_sidecar(
                    artifact["cache"], artifact["metadata"]
                )
                created_paths.append(artifact["metadata"])
                cache_bytes = int(artifact["cache"].stat().st_size)
                sidecar_bytes = int(artifact["metadata"].stat().st_size)
                row = {
                    "source_label": source["label"],
                    "source_cache_path": str(source["path"]),
                    "source_cache_sha256": source_sha256,
                    "source_cache_bytes": int(source_cache.summary.bytes or 0),
                    "signals_shape": [int(value) for value in source_cache.signals.shape],
                    "sampling_rate_hz": sfreq,
                    "encoding": encoding,
                    "payload_dtype": str(payload.dtype),
                    "decoded_dtype": str(loaded.signals.dtype),
                    "bits_per_value": int(encoding_metadata["bits_per_value"]),
                    "payload_bytes": int(payload.nbytes),
                    "cache_bytes": cache_bytes,
                    "sidecar_bytes": sidecar_bytes,
                    "cache_and_sidecar_bytes": cache_bytes + sidecar_bytes,
                    "cache_byte_ratio_vs_source": _safe_ratio(
                        cache_bytes, int(source_cache.summary.bytes or 0)
                    ),
                    "encoding_metadata": encoding_metadata,
                    "timing": {
                        "encode_sec": round(encode_time_sec, 9),
                        "write_and_validate_sec": round(write_validate_time_sec, 9),
                        "decode_in_memory": _timing_summary(decode_times),
                        "load_decode_validate": _timing_summary(load_times),
                    },
                    "reconstruction": reconstruction,
                    "identity": {
                        "source_array_sha256": source_identity,
                        "written_array_sha256": identity_hashes,
                        "array_checks": identity_checks,
                        "all_non_signal_arrays_exact": all(identity_checks.values()),
                        "semantic_metadata_exact": (
                            loaded.metadata == source_cache.metadata
                        ),
                    },
                    "artifact_paths": {
                        "cache": str(artifact["cache"]),
                        "metadata": str(artifact["metadata"]),
                    },
                }
                rows.append(row)
                del loaded, payload

        _add_float32_relative_sizes(rows)
        aggregates = _aggregate_encodings(rows, normalized_variants)
        pareto = {
            source["label"]: _pareto_encodings(
                [row for row in rows if row["source_label"] == source["label"]]
            )
            for source in sources
        }
        consistency = {
            "all_non_signal_arrays_exact": all(
                row["identity"]["all_non_signal_arrays_exact"] for row in rows
            ),
            "all_semantic_metadata_exact": all(
                row["identity"]["semantic_metadata_exact"] for row in rows
            ),
            "all_padding_exact_zero": all(
                row["reconstruction"]["padding"]["decoded_nonzero_count"] == 0
                for row in rows
            ),
            "all_decoded_shapes_match": all(
                row["signals_shape"] == row["reconstruction"]["decoded_shape"]
                for row in rows
            ),
            "integer_source_values_outside_clip_count": sum(
                int(row["encoding_metadata"]["source_values_outside_clip_count"])
                for row in rows
                if row["encoding"].startswith("qint")
            ),
        }
        decision = _build_decision(aggregates)
        warnings = [
            "no_decoder_was_trained_or_evaluated",
            "reconstruction_fidelity_is_not_retained_cer_wer_or_generalization",
            "single_subject_single_block_inputs_do_not_establish_generalization",
            "quantized_input_storage_is_not_integer_only_model_inference",
            "official_v2_bf16_training_does_not_define_an_input_cache_format",
            "timings_are_machine_local_and_include_warm_filesystem_cache_effects",
            "real_cache_records_physical_typing_not_arbitrary_thoughts",
            "official_v2_sentence_decoding_may_have_delay_and_is_not_proven_low_latency_here",
        ]
        if consistency["integer_source_values_outside_clip_count"]:
            warnings.append("integer_variants_clipped_source_values")

        representation_bytes = sum(
            int(row["cache_and_sidecar_bytes"]) for row in rows
        )
        report = {
            "schema": {"name": SWEEP_SCHEMA_NAME, "version": SWEEP_SCHEMA_VERSION},
            "proof_posture": "single_block_multi_cache_representation_fidelity_study",
            "run": {
                "execution_mode": "sequential_single_process",
                "source_cache_count": len(sources),
                "variant_count": len(normalized_variants),
                "artifact_count": len(rows),
                "variants": normalized_variants,
                "clip_abs": float(clip_abs),
                "allow_clipping": bool(allow_clipping),
                "timing_repetitions": repetitions,
                "max_output_mb": float(max_output_mb),
                "projected_uncompressed_bytes": projected_bytes,
                "total_runtime_sec": round(time.perf_counter() - started_at, 6),
                "peak_rss_bytes": _peak_rss_bytes(),
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "numpy_version": _numpy_version(),
            },
            "research_context": {
                "official_v2_paper": OFFICIAL_V2_PAPER_URL,
                "official_v2_model_config": OFFICIAL_V2_MODEL_CONFIG_URL,
                "official_v2_commit": OFFICIAL_V2_COMMIT,
                "official_v2_precision_note": (
                    "The paper reports BF16 mixed-precision training on 8 A100 GPUs. "
                    "That is compute context, not evidence that BF16 is the best MEG cache."
                ),
                "bfloat16_primary_source": BFLOAT16_PAPER_URL,
                "integer_quantization_primary_source": INTEGER_QUANTIZATION_PAPER_URL,
                "numpy_compressed_npz_source": NUMPY_SAVEZ_URL,
                "numpy_safe_load_source": NUMPY_LOAD_URL,
                "serialization_note": (
                    "Each artifact uses numpy.savez_compressed (ZIP_DEFLATED) and loads "
                    "with allow_pickle=False."
                ),
            },
            "source_caches": [_source_report(source) for source in sources],
            "rows": rows,
            "encoding_aggregates": aggregates,
            "pareto_frontiers": pareto,
            "consistency": consistency,
            "resources": {
                "representation_cache_and_sidecar_bytes": representation_bytes,
                "actual_bytes_within_cap": representation_bytes <= cap_bytes,
                "cap_bytes": cap_bytes,
            },
            "decision": decision,
            "artifact_paths": {
                "report_json": str(report_json),
                "report_markdown": str(report_markdown),
                "representations": {
                    label: {
                        encoding: {name: str(path) for name, path in artifact.items()}
                        for encoding, artifact in per_source.items()
                    }
                    for label, per_source in artifact_plan.items()
                },
            },
            "warnings": warnings,
        }
        write_precision_storage_report_json(report, report_json)
        created_paths.append(report_json)
        write_precision_storage_report_markdown(report, report_markdown)
        created_paths.append(report_markdown)
        total_artifact_bytes = sum(
            int(path.stat().st_size) for path in dict.fromkeys(created_paths) if path.exists()
        )
        report["resources"]["total_artifact_bytes"] = total_artifact_bytes
        report["resources"]["total_artifacts_within_cap"] = total_artifact_bytes <= cap_bytes
        if total_artifact_bytes > cap_bytes:
            raise ValueError(
                f"Actual sweep artifacts exceed cap: {total_artifact_bytes} > {cap_bytes} bytes"
            )
        write_precision_storage_report_json(report, report_json)
        write_precision_storage_report_markdown(report, report_markdown)
        return report
    except Exception:
        for path in reversed(list(dict.fromkeys(created_paths))):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def analyze_signal_reconstruction(
    source,
    decoded,
    input_lengths,
    *,
    channel_names: list[str],
    sfreq: float,
) -> dict[str, Any]:
    """Measure valid-region numeric and spectral distortion with bounded memory."""

    np = _require_numpy()
    source_array = np.asarray(source, dtype="float32")
    decoded_array = np.asarray(decoded, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if source_array.shape != decoded_array.shape:
        raise ValueError("source and decoded signal shapes differ")
    if source_array.ndim != 3 or len(lengths) != source_array.shape[0]:
        raise ValueError("signals and input_lengths do not share the sentence dimension")
    if len(channel_names) != source_array.shape[1]:
        raise ValueError("channel_names do not match the signal channel dimension")
    if not np_is_finite_positive(sfreq):
        raise ValueError("sfreq must be finite and positive")

    count = 0
    exact_count = 0
    absolute_sum = 0.0
    squared_error_sum = 0.0
    source_squared_sum = 0.0
    max_abs_error = 0.0
    sum_x = 0.0
    sum_y = 0.0
    sum_x2 = 0.0
    sum_y2 = 0.0
    sum_xy = 0.0
    first_diff_count = 0
    first_diff_squared_error_sum = 0.0
    channel_sse = np.zeros(source_array.shape[1], dtype="float64")
    channel_count = np.zeros(source_array.shape[1], dtype="int64")
    abs_error_chunks = []
    padding_values = 0
    source_padding_nonzero = 0
    decoded_padding_nonzero = 0
    band_source = {name: 0.0 for name, _, _ in DEFAULT_BANDS_HZ}
    band_decoded = {name: 0.0 for name, _, _ in DEFAULT_BANDS_HZ}
    band_bins = {name: 0 for name, _, _ in DEFAULT_BANDS_HZ}

    for row_index, length_value in enumerate(lengths.tolist()):
        length = int(length_value)
        x = source_array[row_index, :, :length].astype("float64", copy=False)
        y = decoded_array[row_index, :, :length].astype("float64", copy=False)
        error = y - x
        absolute = np.abs(error)
        abs_error_chunks.append(absolute.astype("float32", copy=False).ravel())
        count += int(error.size)
        exact_count += int(np.count_nonzero(error == 0))
        absolute_sum += float(absolute.sum(dtype="float64"))
        squared_error_sum += float(np.square(error).sum(dtype="float64"))
        source_squared_sum += float(np.square(x).sum(dtype="float64"))
        max_abs_error = max(max_abs_error, float(absolute.max(initial=0.0)))
        sum_x += float(x.sum(dtype="float64"))
        sum_y += float(y.sum(dtype="float64"))
        sum_x2 += float(np.square(x).sum(dtype="float64"))
        sum_y2 += float(np.square(y).sum(dtype="float64"))
        sum_xy += float((x * y).sum(dtype="float64"))
        channel_sse += np.square(error).sum(axis=1, dtype="float64")
        channel_count += length
        if length > 1:
            difference_error = np.diff(y, axis=1) - np.diff(x, axis=1)
            first_diff_squared_error_sum += float(
                np.square(difference_error).sum(dtype="float64")
            )
            first_diff_count += int(difference_error.size)
        if length < source_array.shape[2]:
            source_padding = source_array[row_index, :, length:]
            decoded_padding = decoded_array[row_index, :, length:]
            padding_values += int(source_padding.size)
            source_padding_nonzero += int(np.count_nonzero(source_padding))
            decoded_padding_nonzero += int(np.count_nonzero(decoded_padding))
        _accumulate_bandpower(
            x,
            y,
            sfreq=float(sfreq),
            source_totals=band_source,
            decoded_totals=band_decoded,
            bin_counts=band_bins,
        )

    rmse = math.sqrt(squared_error_sum / count) if count else 0.0
    source_rms = math.sqrt(source_squared_sum / count) if count else 0.0
    absolute_errors = (
        np.concatenate(abs_error_chunks) if abs_error_chunks else np.asarray([], dtype="float32")
    )
    p99 = float(np.percentile(absolute_errors, 99.0)) if absolute_errors.size else 0.0
    covariance = sum_xy - (sum_x * sum_y / count) if count else 0.0
    x_variance = sum_x2 - (sum_x * sum_x / count) if count else 0.0
    y_variance = sum_y2 - (sum_y * sum_y / count) if count else 0.0
    denominator = math.sqrt(max(0.0, x_variance) * max(0.0, y_variance))
    correlation = covariance / denominator if denominator else (1.0 if squared_error_sum == 0 else None)
    channel_rmse = np.sqrt(
        np.divide(
            channel_sse,
            channel_count,
            out=np.zeros_like(channel_sse),
            where=channel_count > 0,
        )
    )
    worst_channel_index = int(np.argmax(channel_rmse))
    spectral = {}
    for name, low, high in DEFAULT_BANDS_HZ:
        source_power = band_source[name]
        decoded_power = band_decoded[name]
        spectral[name] = {
            "low_hz": low,
            "high_hz": high,
            "source_power_sum": source_power,
            "decoded_power_sum": decoded_power,
            "signed_relative_error": (
                (decoded_power - source_power) / source_power if source_power else None
            ),
            "absolute_relative_error": (
                abs(decoded_power - source_power) / source_power if source_power else None
            ),
            "frequency_bin_observations": band_bins[name],
        }
    if squared_error_sum == 0:
        snr_db = None
        snr_is_infinite = True
    else:
        snr_db = 10.0 * math.log10(source_squared_sum / squared_error_sum)
        snr_is_infinite = False
    return {
        "decoded_shape": [int(value) for value in decoded_array.shape],
        "valid_value_count": count,
        "exact_value_count": exact_count,
        "exact_value_fraction": exact_count / count if count else 1.0,
        "mae": absolute_sum / count if count else 0.0,
        "rmse": rmse,
        "relative_rmse_vs_source_rms": _safe_ratio(rmse, source_rms),
        "max_abs_error": max_abs_error,
        "p99_abs_error": p99,
        "snr_db": snr_db,
        "snr_is_infinite": snr_is_infinite,
        "pearson_correlation": correlation,
        "first_difference_rmse": (
            math.sqrt(first_diff_squared_error_sum / first_diff_count)
            if first_diff_count
            else 0.0
        ),
        "worst_channel_rmse": float(channel_rmse[worst_channel_index]),
        "worst_channel_name": str(channel_names[worst_channel_index]),
        "source_rms": source_rms,
        "source_min": float(source_array.min()),
        "source_max": float(source_array.max()),
        "decoded_min": float(decoded_array.min()),
        "decoded_max": float(decoded_array.max()),
        "padding": {
            "value_count": padding_values,
            "source_nonzero_count": source_padding_nonzero,
            "decoded_nonzero_count": decoded_padding_nonzero,
        },
        "spectral_bandpower": spectral,
        "spectral_note": (
            "Aggregate Hann-windowed FFT bandpower over each valid sentence and channel; "
            "this is a signal-fidelity proxy, not a decoding metric."
        ),
    }


def normalize_variants(variants: Iterable[str]) -> list[str]:
    normalized = [normalize_signal_encoding(value) for value in variants]
    if not normalized:
        raise ValueError("at least one representation variant is required")
    if len(set(normalized)) != len(normalized):
        raise ValueError("representation variants must be unique")
    if "float32" not in normalized:
        raise ValueError("float32 is required as the lossless sweep reference")
    if len(normalized) < 2:
        raise ValueError("at least one packed variant is required beside float32")
    return normalized


def write_precision_storage_report_json(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_precision_storage_report_markdown(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Precision and Storage Sweep",
        "",
        f"**Proof posture:** `{report['proof_posture']}`",
        "",
        "This run compares storage representations of fixed real sentence caches. It does not "
        "train or evaluate a decoder, so numeric fidelity cannot be read as retained CER/WER.",
        "",
        "## Inputs",
        "",
        "| Cache | Shape | Source bytes | Sampling rate |",
        "|---|---:|---:|---:|",
    ]
    for source in report["source_caches"]:
        shape = " x ".join(str(value) for value in source["signals_shape"])
        lines.append(
            f"| `{source['label']}` | {shape} | {source['bytes']:,} | "
            f"{source['sampling_rate_hz']:g} Hz |"
        )
    lines.extend(
        [
            "",
            "## Aggregate Tradeoffs",
            "",
            "| Encoding | Total cache bytes | Reduction vs float32 | Mean relative RMSE | "
            "Max relative RMSE | Median load + decode |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["encoding_aggregates"]:
        lines.append(
            f"| `{row['encoding']}` | {row['total_cache_bytes']:,} | "
            f"{row['storage_reduction_vs_float32']:.2%} | "
            f"{row['mean_relative_rmse']:.6g} | {row['max_relative_rmse']:.6g} | "
            f"{row['mean_median_load_decode_validate_sec']:.6f} s |"
        )
    lines.extend(
        [
            "",
            "## Per-cache Results",
            "",
            "| Cache | Encoding | Cache bytes | Ratio vs source | RMSE | Relative RMSE | "
            "Max error | Max bandpower error | Exact metadata arrays |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["rows"]:
        band_errors = [
            value["absolute_relative_error"]
            for value in row["reconstruction"]["spectral_bandpower"].values()
            if value["absolute_relative_error"] is not None
        ]
        max_band = max(band_errors, default=0.0)
        lines.append(
            f"| `{row['source_label']}` | `{row['encoding']}` | {row['cache_bytes']:,} | "
            f"{row['cache_byte_ratio_vs_source']:.3f} | "
            f"{row['reconstruction']['rmse']:.6g} | "
            f"{row['reconstruction']['relative_rmse_vs_source_rms']:.6g} | "
            f"{row['reconstruction']['max_abs_error']:.6g} | {max_band:.6g} | "
            f"`{row['identity']['all_non_signal_arrays_exact']}` |"
        )
    decision = report["decision"]
    resources = report["resources"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Status: `{decision['status']}`",
            f"- Default: `{decision['default_encoding']}`",
            f"- Fidelity candidate for a later held-out decoder test: "
            f"`{decision['fidelity_candidate']}`",
            f"- Aggressive storage candidate for a later held-out decoder test: "
            f"`{decision['aggressive_storage_candidate']}`",
            f"- Reason: {decision['reason']}",
            "",
            "## Resources",
            "",
            f"- Runtime: {report['run']['total_runtime_sec']:.3f} sec",
            f"- Peak RSS: {_format_optional_bytes(report['run']['peak_rss_bytes'])}",
            f"- Representation caches + sidecars: "
            f"{_format_bytes(resources['representation_cache_and_sidecar_bytes'])}",
            f"- Hard cap: {_format_bytes(resources['cap_bytes'])}",
            f"- Projected uncompressed bytes: "
            f"{_format_bytes(report['run']['projected_uncompressed_bytes'])}",
            "",
            "## Research Boundary",
            "",
            "The official v2 paper reports BF16 mixed-precision *training* on eight A100 GPUs. "
            "This sweep tests BF16 as one input-storage representation; it does not assume the "
            "official model used BF16 MEG cache files. Integer variants use a fixed symmetric "
            "range inherited from the existing robust-scale clamp, not a fitted calibration set.",
            "",
            "## Pareto Frontiers",
            "",
        ]
    )
    for label, encodings in report["pareto_frontiers"].items():
        lines.append(f"- `{label}`: {', '.join(f'`{value}`' for value in encodings)}")
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_sources(cache_paths: Iterable[str | Path]) -> list[dict[str, Any]]:
    paths = [Path(value) for value in cache_paths]
    if not paths:
        raise ValueError("at least one source cache is required")
    if len({str(path.resolve()) for path in paths}) != len(paths):
        raise ValueError("source cache paths must be unique")
    sources = []
    labels = set()
    for path in paths:
        loaded = load_sentence_npz_cache(path)
        label = _slug(path.stem)
        if label in labels:
            raise ValueError(f"source cache labels collide after normalization: {label!r}")
        labels.add(label)
        sources.append(
            {
                "label": label,
                "path": path,
                "sha256": file_sha256(path),
                "cache": loaded,
            }
        )
    return sources


def _source_report(source: dict[str, Any]) -> dict[str, Any]:
    cache = source["cache"]
    return {
        "label": source["label"],
        "path": str(source["path"]),
        "sha256": source["sha256"],
        "bytes": int(cache.summary.bytes or 0),
        "signals_shape": [int(value) for value in cache.signals.shape],
        "signals_dtype": str(cache.signals.dtype),
        "sampling_rate_hz": _sampling_rate_hz(cache),
        "n_sentences": cache.summary.n_sentences,
        "n_channels": cache.summary.n_channels,
        "total_valid_timepoints": cache.summary.total_valid_timepoints,
    }


def _artifact_plan(
    out_dir: Path,
    sources: list[dict[str, Any]],
    variants: list[str],
) -> dict[str, dict[str, dict[str, Path]]]:
    return {
        source["label"]: {
            encoding: {
                "cache": out_dir / f"{source['label']}__{encoding}.npz",
                "metadata": out_dir / f"{source['label']}__{encoding}.metadata.json",
            }
            for encoding in variants
        }
        for source in sources
    }


def _projected_uncompressed_bytes(
    sources: list[dict[str, Any]], variants: list[str]
) -> int:
    total = 1024 * 1024
    for source in sources:
        cache = source["cache"]
        non_signal_bytes = sum(
            int(getattr(cache, name).nbytes) for name in NON_SIGNAL_ARRAY_NAMES
        )
        semantic_metadata_bytes = len(
            json.dumps(cache.metadata, sort_keys=True).encode("utf-8")
        )
        for encoding in variants:
            payload_bytes = int(cache.signals.size) * ENCODING_BYTES_PER_VALUE[encoding]
            total += payload_bytes + non_signal_bytes + 3 * semantic_metadata_bytes + 65536
    return total


def _prepare_planned_paths(paths: list[Path], *, overwrite: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        joined = ", ".join(str(path) for path in existing[:5])
        suffix = " ..." if len(existing) > 5 else ""
        raise FileExistsError(f"Planned sweep artifacts already exist: {joined}{suffix}")
    if overwrite:
        for path in existing:
            if path.is_dir():
                raise IsADirectoryError(f"Planned artifact path is a directory: {path}")
            path.unlink()


def _add_float32_relative_sizes(rows: list[dict[str, Any]]) -> None:
    references = {
        row["source_label"]: row["cache_bytes"]
        for row in rows
        if row["encoding"] == "float32"
    }
    for row in rows:
        reference = references.get(row["source_label"])
        row["cache_byte_ratio_vs_float32_representation"] = (
            _safe_ratio(row["cache_bytes"], reference) if reference else None
        )


def _aggregate_encodings(
    rows: list[dict[str, Any]], variants: list[str]
) -> list[dict[str, Any]]:
    totals = {
        encoding: sum(row["cache_bytes"] for row in rows if row["encoding"] == encoding)
        for encoding in variants
    }
    float32_total = totals.get("float32")
    aggregates = []
    for encoding in variants:
        selected = [row for row in rows if row["encoding"] == encoding]
        relative_rmse = [
            row["reconstruction"]["relative_rmse_vs_source_rms"] for row in selected
        ]
        aggregates.append(
            {
                "encoding": encoding,
                "source_count": len(selected),
                "total_cache_bytes": totals[encoding],
                "total_cache_and_sidecar_bytes": sum(
                    row["cache_and_sidecar_bytes"] for row in selected
                ),
                "storage_reduction_vs_float32": (
                    1.0 - totals[encoding] / float32_total if float32_total else 0.0
                ),
                "mean_rmse": statistics.fmean(
                    row["reconstruction"]["rmse"] for row in selected
                ),
                "mean_relative_rmse": statistics.fmean(relative_rmse),
                "max_relative_rmse": max(relative_rmse),
                "max_abs_error": max(
                    row["reconstruction"]["max_abs_error"] for row in selected
                ),
                "mean_median_load_decode_validate_sec": statistics.fmean(
                    row["timing"]["load_decode_validate"]["median_sec"]
                    for row in selected
                ),
                "all_non_signal_arrays_exact": all(
                    row["identity"]["all_non_signal_arrays_exact"] for row in selected
                ),
                "source_values_outside_clip_count": sum(
                    int(row["encoding_metadata"]["source_values_outside_clip_count"])
                    for row in selected
                ),
            }
        )
    return aggregates


def _build_decision(aggregates: list[dict[str, Any]]) -> dict[str, Any]:
    packed = [row for row in aggregates if row["encoding"] != "float32"]
    fidelity = min(
        packed,
        key=lambda row: (
            row["max_relative_rmse"],
            row["total_cache_bytes"],
            row["encoding"],
        ),
    )
    aggressive = min(
        packed,
        key=lambda row: (
            row["total_cache_bytes"],
            row["max_relative_rmse"],
            row["encoding"],
        ),
    )
    return {
        "status": "retain_float32_default_carry_two_packed_candidates",
        "default_encoding": "float32",
        "fidelity_candidate": fidelity["encoding"],
        "aggressive_storage_candidate": aggressive["encoding"],
        "reason": (
            "Float32 remains the default because no decoder accuracy or held-out "
            "generalization was measured. The lowest-distortion packed encoding and the "
            "smallest packed encoding are retained only as candidates for a future fixed-split test."
        ),
        "selection_metrics": {
            "fidelity": "minimum maximum relative RMSE across source caches",
            "aggressive_storage": "minimum total compressed cache bytes",
        },
    }


def _pareto_encodings(rows: list[dict[str, Any]]) -> list[str]:
    frontier = []
    for candidate in rows:
        dominated = any(
            other["cache_bytes"] <= candidate["cache_bytes"]
            and other["reconstruction"]["rmse"] <= candidate["reconstruction"]["rmse"]
            and (
                other["cache_bytes"] < candidate["cache_bytes"]
                or other["reconstruction"]["rmse"] < candidate["reconstruction"]["rmse"]
            )
            for other in rows
            if other is not candidate
        )
        if not dominated:
            frontier.append(candidate["encoding"])
    return frontier


def _accumulate_bandpower(
    source,
    decoded,
    *,
    sfreq: float,
    source_totals: dict[str, float],
    decoded_totals: dict[str, float],
    bin_counts: dict[str, int],
) -> None:
    np = _require_numpy()
    n_times = source.shape[1]
    if n_times < 4:
        return
    window = np.hanning(n_times)
    window_energy = float(np.square(window).sum())
    if window_energy == 0:
        return
    source_fft = np.fft.rfft(source * window, axis=1)
    decoded_fft = np.fft.rfft(decoded * window, axis=1)
    source_power = np.square(np.abs(source_fft)) / window_energy
    decoded_power = np.square(np.abs(decoded_fft)) / window_energy
    frequencies = np.fft.rfftfreq(n_times, d=1.0 / sfreq)
    for name, low, high in DEFAULT_BANDS_HZ:
        mask = (frequencies >= low) & (frequencies < high)
        if not mask.any():
            continue
        source_totals[name] += float(source_power[:, mask].sum(dtype="float64"))
        decoded_totals[name] += float(decoded_power[:, mask].sum(dtype="float64"))
        bin_counts[name] += int(mask.sum()) * int(source.shape[0])


def _sampling_rate_hz(cache) -> float:
    metadata = cache.metadata
    extraction = metadata.get("extraction_params") or {}
    candidates = [
        extraction.get("sfreq"),
        metadata.get("sampling_rate_hz"),
        metadata.get("sfreq"),
    ]
    for value in candidates:
        if value is not None and np_is_finite_positive(value):
            return float(value)
    raise ValueError(f"Sentence cache {cache.path} does not declare a sampling rate.")


def _timing_summary(values: list[float]) -> dict[str, Any]:
    return {
        "repetitions": len(values),
        "median_sec": round(statistics.median(values), 9),
        "min_sec": round(min(values), 9),
        "max_sec": round(max(values), 9),
    }


def _safe_ratio(numerator: float, denominator: float | None) -> float:
    if denominator is None or denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def np_is_finite_positive(value: Any) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(numeric) and numeric > 0


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value).strip()).strip("-._")
    if not normalized:
        raise ValueError(f"Cannot derive an artifact label from {value!r}")
    return normalized


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        return value if sys.platform == "darwin" else value * 1024
    except (ImportError, OSError, ValueError):
        return None


def _numpy_version() -> str | None:
    try:
        np = _require_numpy()
        return str(np.__version__)
    except RuntimeError:
        return None


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Precision/storage sweeps require NumPy: `pip install numpy`."
        ) from exc
    return np


def _format_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024 or unit == "GiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} GiB"


def _format_optional_bytes(value: int | None) -> str:
    return "unavailable" if value is None else _format_bytes(value)
