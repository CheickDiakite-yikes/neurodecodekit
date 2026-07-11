"""Cache-only channel-subset study for resource-bounded local MEG experiments."""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from neurodecodekit.cache.sentence_npz import (
    LoadedSentenceCache,
    load_sentence_npz_cache,
    save_sentence_npz_cache,
)


SWEEP_SCHEMA_NAME = "b2q-channel-subset-sweep"
SWEEP_SCHEMA_VERSION = 0
DEFAULT_CHANNEL_COUNTS = (76, 51, 25, 16, 8)
DEFAULT_STRATEGIES = ("spatial-fps", "variance", "random", "first")
OFFICIAL_V2_PAPER_URL = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
OFFICIAL_B2Q_COMMIT = "3bf5a4099ca0d23bbe994b2287905760236e56e0"
OFFICIAL_V2_MODEL_CONFIG_URL = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_B2Q_COMMIT}/brain2qwerty_v2/config/model_config.py#L33-L50"
)
IDENTITY_ARRAY_NAMES = (
    "input_lengths",
    "target_token_ids",
    "target_lengths",
    "target_texts",
    "reference_texts",
    "mat_response_texts",
    "trial_indices",
    "sentence_start_sec",
    "sentence_end_sec",
)


def run_channel_subset_sweep(
    *,
    cache_path: str | Path,
    out_dir: str | Path,
    channel_counts: Iterable[int] = DEFAULT_CHANNEL_COUNTS,
    strategies: Iterable[str] = DEFAULT_STRATEGIES,
    seed: int = 17,
    max_output_mb: float = 128.0,
    report_json_path: str | Path | None = None,
    report_markdown_path: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Materialize deterministic subsets and compare resource and proxy metrics."""

    np = _require_numpy()
    started_at = time.perf_counter()
    source_path = Path(cache_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Sentence cache not found: {source_path}")
    if not math.isfinite(max_output_mb) or max_output_mb <= 0:
        raise ValueError("max_output_mb must be finite and > 0")

    source = load_sentence_npz_cache(source_path)
    counts = normalize_channel_counts(channel_counts, source.summary.n_channels)
    strategy_names = normalize_strategies(strategies)
    geometry = _validated_channel_geometry(source)
    positions = np.asarray([row["position_m"] for row in geometry], dtype="float64")
    channel_names = [str(value) for value in source.channel_names.tolist()]
    variances = channel_variances(source.signals, source.input_lengths)
    orders = build_strategy_orders(
        positions=positions,
        variances=variances,
        channel_names=channel_names,
        strategies=strategy_names,
        seed=seed,
    )

    output_dir = Path(out_dir)
    json_path = Path(report_json_path) if report_json_path else output_dir / "sweep.json"
    markdown_path = (
        Path(report_markdown_path)
        if report_markdown_path
        else output_dir / "sweep.md"
    )
    artifacts = _planned_artifacts(output_dir, strategy_names, counts)
    planned_paths = [json_path, markdown_path]
    for paths in artifacts.values():
        planned_paths.extend(paths.values())
    existing = [str(path) for path in planned_paths if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Channel-subset sweep refuses to overwrite existing artifacts without "
            f"overwrite=True: {existing}"
        )

    max_output_bytes = int(max_output_mb * 1024 * 1024)
    projected_bytes = estimate_uncompressed_output_bytes(
        source,
        channel_counts=counts,
        n_strategies=len(strategy_names),
    )
    if projected_bytes > max_output_bytes:
        raise ValueError(
            "Projected uncompressed subset artifacts exceed the output cap: "
            f"{projected_bytes} > {max_output_bytes} bytes. Reduce counts/strategies or "
            "raise max_output_mb explicitly."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    source_sha256 = _hash_file(source_path)
    identity_hashes = {
        name: _hash_array(getattr(source, name)) for name in IDENTITY_ARRAY_NAMES
    }
    rows: list[dict[str, Any]] = []
    selections: dict[tuple[str, int], set[int]] = {}
    total_artifact_bytes = 0
    all_identity_checks = True
    all_signal_checks = True

    for strategy in strategy_names:
        order = orders[strategy]
        for count in counts:
            ranked_indices = [int(value) for value in order[:count]]
            storage_indices = sorted(ranked_indices)
            selections[(strategy, count)] = set(storage_indices)
            paths = artifacts[(strategy, count)]
            metadata = _subset_metadata(
                source=source,
                source_path=source_path,
                source_sha256=source_sha256,
                geometry=geometry,
                strategy=strategy,
                seed=seed,
                ranked_indices=ranked_indices,
                storage_indices=storage_indices,
                channel_names=channel_names,
            )
            save_sentence_npz_cache(
                paths["cache"],
                signals=source.signals[:, storage_indices, :],
                input_lengths=source.input_lengths,
                target_token_ids=source.target_token_ids,
                target_lengths=source.target_lengths,
                target_texts=source.target_texts,
                reference_texts=source.reference_texts,
                mat_response_texts=source.mat_response_texts,
                trial_indices=source.trial_indices,
                sentence_start_sec=source.sentence_start_sec,
                sentence_end_sec=source.sentence_end_sec,
                channel_names=source.channel_names[storage_indices],
                metadata=metadata,
                metadata_sidecar=paths["metadata"],
            )
            written = load_sentence_npz_cache(paths["cache"])
            identity_ok = all(
                np.array_equal(getattr(source, name), getattr(written, name))
                for name in IDENTITY_ARRAY_NAMES
            )
            signal_ok = np.array_equal(
                source.signals[:, storage_indices, :],
                written.signals,
            )
            all_identity_checks = all_identity_checks and identity_ok
            all_signal_checks = all_signal_checks and signal_ok
            cache_bytes = int(paths["cache"].stat().st_size)
            metadata_bytes = int(paths["metadata"].stat().st_size)
            total_artifact_bytes += cache_bytes + metadata_bytes
            if total_artifact_bytes > max_output_bytes:
                raise RuntimeError(
                    "Written subset artifacts exceeded max_output_mb despite the conservative "
                    "preflight estimate; stop before adding more artifacts."
                )
            row = analyze_selection(
                positions=positions,
                variances=variances,
                selected_indices=storage_indices,
            )
            row.update(
                {
                    "strategy": strategy,
                    "channel_count": count,
                    "keep_fraction": count / source.summary.n_channels,
                    "cache_path": str(paths["cache"]),
                    "metadata_path": str(paths["metadata"]),
                    "cache_bytes": cache_bytes,
                    "metadata_bytes": metadata_bytes,
                    "cache_byte_fraction_of_base": (
                        cache_bytes / int(source.summary.bytes or 1)
                    ),
                    "selection_rank_names": [channel_names[i] for i in ranked_indices],
                    "stored_channel_names": [channel_names[i] for i in storage_indices],
                    "selected_channel_names_sha256": _hash_values(
                        [channel_names[i] for i in storage_indices]
                    ),
                    "identity_arrays_match_base": identity_ok,
                    "signal_values_match_base_subset": signal_ok,
                }
            )
            rows.append(row)

    overlaps = build_pairwise_overlaps(
        selections=selections,
        strategies=strategy_names,
        channel_counts=counts,
    )
    report = build_channel_subset_report(
        source=source,
        source_path=source_path,
        source_sha256=source_sha256,
        channel_counts=counts,
        strategies=strategy_names,
        seed=seed,
        rows=rows,
        overlaps=overlaps,
        identity_hashes=identity_hashes,
        all_identity_checks=all_identity_checks,
        all_signal_checks=all_signal_checks,
        projected_bytes=projected_bytes,
        total_artifact_bytes=total_artifact_bytes,
        max_output_bytes=max_output_bytes,
        runtime_sec=round(time.perf_counter() - started_at, 6),
    )
    report["artifact_paths"] = {
        "report_json": str(json_path),
        "report_markdown": str(markdown_path),
    }
    write_channel_subset_report_json(report, json_path)
    write_channel_subset_report_markdown(report, markdown_path)
    return report


def normalize_channel_counts(values: Iterable[int], n_channels: int) -> list[int]:
    counts = [int(value) for value in values]
    if n_channels < 2:
        raise ValueError("Channel-subset sweeps require at least two base channels.")
    if not counts:
        raise ValueError("At least one channel count is required.")
    if len(set(counts)) != len(counts):
        raise ValueError("Channel counts must be unique.")
    if any(value < 1 or value >= n_channels for value in counts):
        raise ValueError(
            f"Channel counts must be between 1 and {n_channels - 1} for this base cache."
        )
    return sorted(counts, reverse=True)


def normalize_strategies(values: Iterable[str]) -> list[str]:
    strategies = [str(value).strip().lower() for value in values]
    if not strategies:
        raise ValueError("At least one channel selection strategy is required.")
    if len(set(strategies)) != len(strategies):
        raise ValueError("Channel selection strategies must be unique.")
    unknown = sorted(set(strategies) - set(DEFAULT_STRATEGIES))
    if unknown:
        raise ValueError(f"Unknown channel selection strategies: {unknown}")
    return strategies


def spatial_farthest_point_order(positions, channel_names: Iterable[str]) -> list[int]:
    """Build a deterministic nested farthest-point order in device coordinates."""

    np = _require_numpy()
    points = np.asarray(positions, dtype="float64")
    names = [str(value) for value in channel_names]
    if points.ndim != 2 or points.shape[1] != 3 or points.shape[0] != len(names):
        raise ValueError("positions must be [channels, 3] and match channel_names")
    if not np.isfinite(points).all():
        raise ValueError("positions must be finite")
    centroid = points.mean(axis=0)
    centroid_distance = np.linalg.norm(points - centroid, axis=1)
    first = _argmax_with_name_tie(centroid_distance, names, set())
    selected = [first]
    selected_set = {first}
    min_distance = np.linalg.norm(points - points[first], axis=1)
    while len(selected) < len(names):
        next_index = _argmax_with_name_tie(min_distance, names, selected_set)
        selected.append(next_index)
        selected_set.add(next_index)
        distance = np.linalg.norm(points - points[next_index], axis=1)
        min_distance = np.minimum(min_distance, distance)
    return selected


def channel_variances(signals, input_lengths):
    """Compute marginal per-channel variance over valid, non-padding samples."""

    np = _require_numpy()
    data = np.asarray(signals)
    lengths = np.asarray(input_lengths, dtype="int64")
    if data.ndim != 3 or lengths.ndim != 1 or len(lengths) != data.shape[0]:
        raise ValueError("signals and input_lengths do not share the sentence dimension")
    sums = np.zeros(data.shape[1], dtype="float64")
    sums_of_squares = np.zeros(data.shape[1], dtype="float64")
    n_samples = 0
    for row_index, length_value in enumerate(lengths.tolist()):
        length = int(length_value)
        if length < 1 or length > data.shape[2]:
            raise ValueError("input_lengths must stay inside the signal width")
        valid = data[row_index, :, :length].astype("float64", copy=False)
        sums += valid.sum(axis=1)
        sums_of_squares += np.square(valid).sum(axis=1)
        n_samples += length
    means = sums / n_samples
    variances = sums_of_squares / n_samples - np.square(means)
    return np.maximum(variances, 0.0)


def build_strategy_orders(
    *,
    positions,
    variances,
    channel_names: Iterable[str],
    strategies: Iterable[str],
    seed: int,
) -> dict[str, list[int]]:
    np = _require_numpy()
    names = [str(value) for value in channel_names]
    strategy_names = normalize_strategies(strategies)
    variance_values = np.asarray(variances, dtype="float64")
    if variance_values.shape != (len(names),) or not np.isfinite(variance_values).all():
        raise ValueError("variances must be one finite value per channel")
    orders: dict[str, list[int]] = {}
    for strategy in strategy_names:
        if strategy == "spatial-fps":
            order = spatial_farthest_point_order(positions, names)
        elif strategy == "variance":
            order = sorted(range(len(names)), key=lambda i: (-variance_values[i], names[i]))
        elif strategy == "random":
            order = [int(value) for value in np.random.default_rng(seed).permutation(len(names))]
        else:
            order = list(range(len(names)))
        orders[strategy] = order
    return orders


def analyze_selection(*, positions, variances, selected_indices: Iterable[int]) -> dict[str, Any]:
    np = _require_numpy()
    points = np.asarray(positions, dtype="float64")
    variance_values = np.asarray(variances, dtype="float64")
    selected = np.asarray(list(selected_indices), dtype="int64")
    selected_points = points[selected]
    distance_to_selected = np.linalg.norm(
        points[:, None, :] - selected_points[None, :, :],
        axis=2,
    ).min(axis=1)
    pairwise = np.linalg.norm(
        selected_points[:, None, :] - selected_points[None, :, :],
        axis=2,
    )
    off_diagonal = pairwise.copy()
    np.fill_diagonal(off_diagonal, np.inf)
    total_variance = float(variance_values.sum())
    return {
        "marginal_variance_sum": float(variance_values[selected].sum()),
        "marginal_variance_share": (
            float(variance_values[selected].sum()) / total_variance
            if total_variance > 0
            else 0.0
        ),
        "spatial_mean_nearest_distance_m": float(distance_to_selected.mean()),
        "spatial_max_nearest_distance_m": float(distance_to_selected.max()),
        "selected_diameter_m": float(pairwise.max()),
        "selected_min_pairwise_distance_m": (
            float(off_diagonal.min()) if len(selected) > 1 else 0.0
        ),
    }


def build_pairwise_overlaps(
    *,
    selections: dict[tuple[str, int], set[int]],
    strategies: Iterable[str],
    channel_counts: Iterable[int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for count in channel_counts:
        for left, right in itertools.combinations(strategies, 2):
            left_set = selections[(left, count)]
            right_set = selections[(right, count)]
            intersection = len(left_set & right_set)
            union = len(left_set | right_set)
            rows.append(
                {
                    "channel_count": count,
                    "left_strategy": left,
                    "right_strategy": right,
                    "intersection_count": intersection,
                    "jaccard": intersection / union if union else 1.0,
                }
            )
    return rows


def estimate_uncompressed_output_bytes(
    source: LoadedSentenceCache,
    *,
    channel_counts: Iterable[int],
    n_strategies: int,
) -> int:
    shared_bytes = sum(
        int(getattr(source, name).nbytes)
        for name in IDENTITY_ARRAY_NAMES
    )
    signal_itemsize = int(source.signals.dtype.itemsize)
    n_sentences = int(source.signals.shape[0])
    max_timepoints = int(source.signals.shape[2])
    total = 0
    for count in channel_counts:
        signal_bytes = n_sentences * int(count) * max_timepoints * signal_itemsize
        channel_name_bytes = int(source.channel_names.dtype.itemsize) * int(count)
        # Reserve room for embedded JSON metadata and its inspectable sidecar.
        total += n_strategies * (
            signal_bytes + shared_bytes + channel_name_bytes + 192 * 1024
        )
    return total


def build_channel_subset_report(
    *,
    source: LoadedSentenceCache,
    source_path: Path,
    source_sha256: str,
    channel_counts: list[int],
    strategies: list[str],
    seed: int,
    rows: list[dict[str, Any]],
    overlaps: list[dict[str, Any]],
    identity_hashes: dict[str, str],
    all_identity_checks: bool,
    all_signal_checks: bool,
    projected_bytes: int,
    total_artifact_bytes: int,
    max_output_bytes: int,
    runtime_sec: float,
) -> dict[str, Any]:
    best_coverage = {}
    best_variance = {}
    for count in channel_counts:
        count_rows = [row for row in rows if row["channel_count"] == count]
        best_coverage[str(count)] = min(
            count_rows,
            key=lambda row: row["spatial_mean_nearest_distance_m"],
        )["strategy"]
        best_variance[str(count)] = max(
            count_rows,
            key=lambda row: row["marginal_variance_share"],
        )["strategy"]
    return {
        "schema": {"name": SWEEP_SCHEMA_NAME, "version": SWEEP_SCHEMA_VERSION},
        "proof_posture": "single_block_real_data_resource_and_proxy_study",
        "question": (
            "Which deterministic subsets of one 102-magnetometer S21 cache preserve spatial "
            "coverage, marginal variance, and storage efficiency?"
        ),
        "official_v2_anchor": {
            "paper_url": OFFICIAL_V2_PAPER_URL,
            "model_config_url": OFFICIAL_V2_MODEL_CONFIG_URL,
            "full_meg_channels": 306,
            "sensor_types": {"magnetometers": 102, "planar_gradiometers": 204},
            "random_keep_fractions": [0.75, 0.5, 0.25],
            "random_sensor_counts": [230, 153, 76],
            "sensor_selection_seeds": 4,
            "full_array_wer": 0.433,
            "subset_wer": {"230": 0.467, "153": 0.490, "76": 0.547},
            "important_difference": (
                "The official experiment retrained the full multi-subject v2 pipeline. This "
                "local study uses one magnetometer-only v1-era S21 block and no decoder fit."
            ),
        },
        "base_cache": {
            "path": str(source_path),
            "sha256": source_sha256,
            "bytes": source.summary.bytes,
            "signals_shape": list(source.summary.signals_shape),
            "n_sentences": source.summary.n_sentences,
            "n_channels": source.summary.n_channels,
            "sampling_rate_hz": (source.metadata.get("extraction_params") or {}).get("sfreq"),
            "channel_types": _channel_type_counts(source),
            "coordinate_frames": _coordinate_frame_counts(source),
        },
        "design": {
            "channel_counts": channel_counts,
            "strategies": strategies,
            "random_seed": seed,
            "nested_within_strategy": True,
            "stored_channel_order": "original_base_cache_order",
            "proxy_metrics": [
                "marginal_variance_share_after_per_channel_robust_scaling",
                "whole_array_nearest_selected_sensor_distance_in_device_coordinates",
                "selected_sensor_diameter",
                "compressed_cache_bytes",
            ],
        },
        "rows": rows,
        "pairwise_overlaps": overlaps,
        "consistency": {
            "identity_array_sha256": identity_hashes,
            "all_written_identity_arrays_match_base": all_identity_checks,
            "all_written_signal_values_match_base_subsets": all_signal_checks,
        },
        "proxy_leaders": {
            "lowest_mean_spatial_coverage_distance": best_coverage,
            "highest_marginal_variance_share": best_variance,
        },
        "decision": {
            "status": "carry_two_candidates_to_future_accuracy_test",
            "candidates": ["spatial-fps", "variance"],
            "controls": [name for name in ("random", "first") if name in strategies],
            "reason": (
                "Spatial coverage and same-block variance optimize different proxies. Only a "
                "leakage-safe held-out decoder comparison can select an accuracy winner."
            ),
        },
        "resources": {
            "projected_uncompressed_artifact_bytes": projected_bytes,
            "subset_cache_and_sidecar_bytes": total_artifact_bytes,
            "max_output_bytes": max_output_bytes,
            "runtime_sec": runtime_sec,
            "peak_rss_bytes": _peak_rss_bytes(),
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "warnings": [
            "no_decoder_was_trained_or_evaluated",
            "proxy_metrics_do_not_establish_cer_wer_or_generalization",
            "single_subject_single_block_result",
            "magnetometer_only_subsets_are_not_equivalent_to_opm_hardware",
            "device_coordinate_coverage_is_not_an_anatomical_or_motor_cortex_roi",
            "variance_ranking_uses_the_same_block_and_must_not_be_fit_on_future_test_data",
            "first_strategy_depends_on_fif_file_order",
            "random_strategy_is_a_seeded_control_not_an_optimized_sensor_design",
            "real_cache_records_physical_typing_not_arbitrary_thoughts",
            "brain2qwerty_v2_is_whole_sentence_noncausal_not_currently_real_time",
        ],
    }


def write_channel_subset_report_json(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_channel_subset_report_markdown(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Channel-subset sweep",
        "",
        f"**Proof posture:** `{report['proof_posture']}`",
        "",
        report["question"],
        "",
        "## Official v2 anchor",
        "",
        (
            "Brain2Qwerty v2 randomly retained 230, 153, or 76 of 306 MEG channels, "
            "retrained the full pipeline across four sensor seeds, and reported smooth but "
            "nonzero WER degradation. This local study does not reproduce that accuracy test."
        ),
        "",
        f"- Paper: {report['official_v2_anchor']['paper_url']}",
        f"- Pinned model config: {report['official_v2_anchor']['model_config_url']}",
        "",
        "## Resource result",
        "",
        f"- Base cache: `{report['base_cache']['path']}`",
        f"- Base shape: `{report['base_cache']['signals_shape']}`",
        (
            "- Subset caches + sidecars: "
            f"{_format_bytes(report['resources']['subset_cache_and_sidecar_bytes'])}"
        ),
        f"- Runtime: {report['resources']['runtime_sec']:.3f} sec",
        f"- Peak RSS: {_format_optional_bytes(report['resources']['peak_rss_bytes'])}",
        "",
        "## Proxy comparison",
        "",
        (
            "| Channels | Strategy | Cache | Base bytes | Variance share | "
            "Mean coverage | Max coverage | Diameter |"
        ),
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {channel_count} | {strategy} | {cache} | {fraction:.1%} | "
            "{variance:.1%} | {mean_mm:.1f} mm | {max_mm:.1f} mm | {diameter_mm:.1f} mm |".format(
                channel_count=row["channel_count"],
                strategy=row["strategy"],
                cache=_format_bytes(row["cache_bytes"]),
                fraction=row["cache_byte_fraction_of_base"],
                variance=row["marginal_variance_share"],
                mean_mm=1000 * row["spatial_mean_nearest_distance_m"],
                max_mm=1000 * row["spatial_max_nearest_distance_m"],
                diameter_mm=1000 * row["selected_diameter_m"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            report["decision"]["reason"],
            "",
            "Carry `spatial-fps` and `variance` into a future held-out decoder test. Keep "
            "`random` and `first` only as controls.",
            "",
            "## Proof limits",
            "",
        ]
    )
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _planned_artifacts(
    output_dir: Path,
    strategies: Iterable[str],
    counts: Iterable[int],
) -> dict[tuple[str, int], dict[str, Path]]:
    artifacts = {}
    for strategy in strategies:
        for count in counts:
            stem = f"subset_{strategy}_{count}ch"
            artifacts[(strategy, count)] = {
                "cache": output_dir / f"{stem}.npz",
                "metadata": output_dir / f"{stem}.metadata.json",
            }
    return artifacts


def _validated_channel_geometry(source: LoadedSentenceCache) -> list[dict[str, Any]]:
    channels = source.metadata.get("channels") or {}
    geometry = list(channels.get("geometry") or [])
    names = [str(value) for value in source.channel_names.tolist()]
    if len(geometry) != len(names):
        raise ValueError(
            "Base cache needs one channels.geometry row per channel. Re-extract it with "
            "the current extract-sentence-cache command."
        )
    rows = []
    for index, (name, row) in enumerate(zip(names, geometry, strict=True)):
        if not isinstance(row, dict) or str(row.get("name")) != name:
            raise ValueError(f"Channel geometry row {index} does not match {name!r}.")
        position = row.get("position_m")
        if not isinstance(position, list) or len(position) != 3:
            raise ValueError(f"Channel {name!r} lacks a three-value position_m.")
        values = [float(value) for value in position]
        if not all(math.isfinite(value) for value in values):
            raise ValueError(f"Channel {name!r} has non-finite device coordinates.")
        normalized = dict(row)
        normalized["position_m"] = values
        rows.append(normalized)
    return rows


def _subset_metadata(
    *,
    source: LoadedSentenceCache,
    source_path: Path,
    source_sha256: str,
    geometry: list[dict[str, Any]],
    strategy: str,
    seed: int,
    ranked_indices: list[int],
    storage_indices: list[int],
    channel_names: list[str],
) -> dict[str, Any]:
    metadata = copy.deepcopy(source.metadata)
    metadata["kind"] = f"{source.summary.kind}_channel_subset"
    metadata["parent_cache"] = {
        "path": str(source_path),
        "sha256": source_sha256,
        "n_channels": source.summary.n_channels,
    }
    metadata["channel_subset"] = {
        "strategy": strategy,
        "random_seed": seed if strategy == "random" else None,
        "selection_rank_indices": ranked_indices,
        "selection_rank_names": [channel_names[index] for index in ranked_indices],
        "stored_base_indices": storage_indices,
        "stored_channel_order": "original_base_cache_order",
    }
    metadata["channels"] = {
        "n_channels": len(storage_indices),
        "names": [channel_names[index] for index in storage_indices],
        "geometry": [copy.deepcopy(geometry[index]) for index in storage_indices],
        "position_units": "m",
        "position_source": "inherited_from_parent_cache",
    }
    transformations = list(metadata.get("transformations") or [])
    transformations.append(
        {
            "name": "channel_subset",
            "description": "Selected a cache-only channel subset without changing trials or timepoints.",
            "params": {
                "strategy": strategy,
                "random_seed": seed if strategy == "random" else None,
                "n_channels": len(storage_indices),
            },
        }
    )
    metadata["transformations"] = transformations
    warnings = list(metadata.get("warnings") or [])
    warnings.extend(
        [
            "channel_subset_proxy_does_not_establish_decoder_accuracy",
            "magnetometer_only_subset_is_not_equivalent_to_opm_hardware",
        ]
    )
    if strategy == "variance":
        warnings.append("variance_selection_was_fit_on_the_same_source_block")
    metadata["warnings"] = list(dict.fromkeys(warnings))
    return metadata


def _argmax_with_name_tie(values, names: list[str], excluded: set[int]) -> int:
    candidates = [index for index in range(len(names)) if index not in excluded]
    if not candidates:
        raise ValueError("No unselected channel remains.")
    return min(candidates, key=lambda index: (-float(values[index]), names[index]))


def _channel_type_counts(source: LoadedSentenceCache) -> dict[str, int]:
    rows = _validated_channel_geometry(source)
    counts: dict[str, int] = {}
    for row in rows:
        name = str(row.get("type") or "unknown")
        counts[name] = counts.get(name, 0) + 1
    return counts


def _coordinate_frame_counts(source: LoadedSentenceCache) -> dict[str, int]:
    rows = _validated_channel_geometry(source)
    counts: dict[str, int] = {}
    for row in rows:
        name = str(row.get("coord_frame"))
        counts[name] = counts.get(name, 0) + 1
    return counts


def _hash_values(values: Iterable[str]) -> str:
    payload = json.dumps(list(values), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _hash_array(value) -> str:
    array = _require_numpy().ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape)).encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (ImportError, OSError, ValueError):  # pragma: no cover - platform-dependent
        return None
    return value if sys.platform == "darwin" else value * 1024


def _format_bytes(n_bytes: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    size = float(n_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GiB"


def _format_optional_bytes(value: int | None) -> str:
    return _format_bytes(value) if value is not None else "unavailable"


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Channel-subset sweeps require NumPy: `pip install numpy`."
        ) from exc
    return np
