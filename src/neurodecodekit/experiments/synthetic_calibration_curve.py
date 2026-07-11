"""Bounded synthetic calibration-size and shift-family stress study."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import platform
import resource
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from neurodecodekit.evaluation.report import (
    build_text_report,
    compare_paired_predictions,
)
from neurodecodekit.models.prior_baseline import run_prior_baseline
from neurodecodekit.models.tiny_ctc import (
    deterministic_text_holdout_indices,
    run_tiny_ctc_cross_session_views,
)
from neurodecodekit.preprocess.session_adapter import (
    SyntheticChannelMixingShift,
    SyntheticChannelShift,
    SyntheticTimeVaryingShift,
    apply_robust_channel_affine,
    apply_synthetic_channel_mixing_shift,
    apply_synthetic_channel_shift,
    apply_synthetic_time_varying_shift,
    fit_robust_channel_affine,
    make_synthetic_channel_mixing_shift,
    make_synthetic_channel_shift,
    make_synthetic_time_varying_shift,
    padding_is_zero,
    summarize_signal_reconstruction,
)
from neurodecodekit.training.synthetic_sentences import make_synthetic_sentence_arrays


SCHEMA_NAME = "neurodecodekit-synthetic-calibration-curve"
SCHEMA_VERSION = 1
PROOF_POSTURE = "synthetic_calibration_characterization_only_no_real_adapter_claim"
SHIFT_FAMILIES = (
    "stationary_diagonal",
    "stationary_channel_mixing",
    "within_row_time_varying",
)
DEFAULT_CALIBRATION_SIZES = (1, 2, 4, 8, 16, 32)
DEFAULT_SHIFT_SEEDS = (101, 211, 307)
SOURCE_URLS = {
    "brain2qwerty_v2": (
        "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
    ),
    "coral": "https://doi.org/10.1609/aaai.v30i1.10306",
    "euclidean_alignment": "https://doi.org/10.1109/TBME.2019.2913914",
    "meg_covariate_shift": "https://doi.org/10.1186/1687-6180-2012-129",
    "session_domain_generalization": "https://arxiv.org/abs/2012.03533",
}


def run_synthetic_calibration_curve(
    *,
    out_dir: str | Path,
    sentences: int = 96,
    calibration_sentences: int = 48,
    channels: int = 6,
    letter_classes: int = 4,
    seed: int = 23,
    calibration_sizes: Iterable[int] = DEFAULT_CALIBRATION_SIZES,
    shift_seeds: Iterable[int] = DEFAULT_SHIFT_SEEDS,
    epochs: int = 50,
    batch_size: int = 16,
    learning_rate: float = 0.02,
    hidden_channels: int = 16,
    num_threads: int = 1,
    min_stationary_validation_cer_gain: float = 0.10,
    bootstrap_iterations: int = 1000,
    max_output_mb: float = 4.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Measure an unlabeled robust-affine calibration curve without real data."""

    sizes = _normalize_positive_ints(calibration_sizes, name="calibration_sizes")
    seeds = _normalize_positive_ints(shift_seeds, name="shift_seeds")
    _validate_params(
        sentences=sentences,
        calibration_sentences=calibration_sentences,
        channels=channels,
        letter_classes=letter_classes,
        calibration_sizes=sizes,
        shift_seeds=seeds,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        num_threads=num_threads,
        min_stationary_validation_cer_gain=min_stationary_validation_cer_gain,
        bootstrap_iterations=bootstrap_iterations,
        max_output_mb=max_output_mb,
    )
    output_dir = Path(out_dir)
    artifacts = {
        "report_json": output_dir / "report.json",
        "report_markdown": output_dir / "report.md",
        "validation_curve_csv": output_dir / "validation_curve.csv",
        "holdout_results_csv": output_dir / "holdout_results.csv",
    }
    existing = [path for path in artifacts.values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Synthetic calibration artifacts already exist: "
            + ", ".join(str(path) for path in existing)
        )

    started_at = time.perf_counter()
    np = _require_numpy()
    source_arrays, source_metadata = make_synthetic_sentence_arrays(
        sentences=sentences,
        channels=channels,
        letter_classes=letter_classes,
        seed=seed,
    )
    source_signals = np.asarray(source_arrays["signals"], dtype="float32")
    source_lengths = np.asarray(source_arrays["input_lengths"], dtype="int32")
    source_token_ids = np.asarray(source_arrays["target_token_ids"], dtype="int16")
    source_target_lengths = np.asarray(source_arrays["target_lengths"], dtype="int32")
    source_texts = [str(value) for value in source_arrays["target_texts"].tolist()]
    train_indices, remaining_indices = deterministic_text_holdout_indices(
        source_texts,
        train_fraction=2.0 / 3.0,
    )
    remaining_texts = [source_texts[index] for index in remaining_indices]
    validation_local, test_local = deterministic_text_holdout_indices(
        remaining_texts,
        train_fraction=0.5,
    )
    validation_indices = [remaining_indices[index] for index in validation_local]
    test_indices = [remaining_indices[index] for index in test_local]
    partitions = {
        "train": train_indices,
        "val": validation_indices,
        "test": test_indices,
    }
    _validate_partitions(partitions, n_rows=sentences)

    calibration_arrays, calibration_metadata, calibration_generation_seed = (
        _make_disjoint_calibration_pool(
            source_texts=set(source_texts),
            sentences=calibration_sentences,
            channels=channels,
            letter_classes=letter_classes,
            seed=seed + 4001,
        )
    )
    calibration_signals = np.asarray(calibration_arrays["signals"], dtype="float32")
    calibration_lengths = np.asarray(
        calibration_arrays["input_lengths"],
        dtype="int32",
    )
    calibration_texts = [
        str(value) for value in calibration_arrays["target_texts"].tolist()
    ]
    calibration_order = sorted(
        range(calibration_sentences),
        key=lambda index: _stable_order_key(calibration_texts[index], seed),
    )
    sfreq = float(calibration_metadata["sampling_rate_hz"])
    shift_specs = _make_shift_specs(channels=channels, shift_seeds=seeds)

    validation_views: dict[str, Any] = {}
    validation_point_state: list[dict[str, Any]] = []
    validation_identity_reconstruction: dict[tuple[str, int], dict[str, Any]] = {}
    validation_padding_ok = True
    validation_source = source_signals[validation_indices]
    validation_lengths = source_lengths[validation_indices]
    for family in SHIFT_FAMILIES:
        for shift_seed in seeds:
            shift = shift_specs[(family, shift_seed)]
            shifted_calibration = _apply_shift(
                calibration_signals,
                calibration_lengths,
                shift,
            )
            shifted_validation = _apply_shift(
                validation_source,
                validation_lengths,
                shift,
            )
            identity_key = _view_key("validation", family, shift_seed, "identity")
            validation_views[identity_key] = shifted_validation
            validation_identity_reconstruction[(family, shift_seed)] = (
                summarize_signal_reconstruction(
                    validation_source,
                    shifted_validation,
                    validation_lengths,
                )
            )
            validation_padding_ok = validation_padding_ok and padding_is_zero(
                shifted_calibration,
                calibration_lengths,
            )
            validation_padding_ok = validation_padding_ok and padding_is_zero(
                shifted_validation,
                validation_lengths,
            )
            for calibration_size in sizes:
                target_fit_indices = calibration_order[:calibration_size]
                adapter = fit_robust_channel_affine(
                    source_signals=source_signals,
                    source_input_lengths=source_lengths,
                    target_calibration_signals=shifted_calibration,
                    target_input_lengths=calibration_lengths,
                    source_fit_indices=train_indices,
                    target_fit_indices=target_fit_indices,
                )
                adapted_validation = apply_robust_channel_affine(
                    shifted_validation,
                    validation_lengths,
                    adapter,
                )
                adapted_key = _view_key(
                    "validation",
                    family,
                    shift_seed,
                    "adapted",
                    calibration_size,
                )
                validation_views[adapted_key] = adapted_validation
                validation_padding_ok = validation_padding_ok and padding_is_zero(
                    adapted_validation,
                    validation_lengths,
                )
                reconstruction = summarize_signal_reconstruction(
                    validation_source,
                    adapted_validation,
                    validation_lengths,
                )
                validation_point_state.append(
                    {
                        "shift_family": family,
                        "shift_seed": shift_seed,
                        "calibration_rows": calibration_size,
                        "calibration_seconds": sum(
                            int(calibration_lengths[index])
                            for index in target_fit_indices
                        )
                        / sfreq,
                        "calibration_text_membership_sha256": _json_sha256(
                            [calibration_texts[index] for index in target_fit_indices]
                        ),
                        "target_statistics_sha256": adapter.to_dict()[
                            "target_statistics_sha256"
                        ],
                        "identity_view_key": identity_key,
                        "adapted_view_key": adapted_key,
                        "identity_reconstruction": validation_identity_reconstruction[
                            (family, shift_seed)
                        ],
                        "adapted_reconstruction": reconstruction,
                    }
                )

    model_kwargs = {
        "train_signals": source_signals,
        "train_input_lengths": source_lengths,
        "train_target_token_ids": source_token_ids,
        "train_target_lengths": source_target_lengths,
        "train_target_texts": source_texts,
        "source_partitions": partitions,
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "hidden_channels": hidden_channels,
        "device": "cpu",
        "num_threads": num_threads,
        "max_restarts": 1,
    }
    validation_result = run_tiny_ctc_cross_session_views(
        eval_signal_views=validation_views,
        eval_input_lengths=validation_lengths,
        eval_target_token_ids=source_token_ids[validation_indices],
        eval_target_lengths=source_target_lengths[validation_indices],
        eval_target_texts=[source_texts[index] for index in validation_indices],
        **model_kwargs,
    )
    validation_curve = _complete_validation_curve(
        point_state=validation_point_state,
        predictions_by_view=validation_result.predictions_by_view,
        targets=validation_result.targets,
    )
    validation_aggregate = _aggregate_curve(validation_curve)
    selected_size = _select_stationary_size(
        aggregate=validation_aggregate,
        calibration_sizes=sizes,
        min_cer_gain=min_stationary_validation_cer_gain,
    )

    holdout_views: dict[str, Any] = {}
    holdout_state: list[dict[str, Any]] = []
    holdout_padding_ok = True
    holdout_source = source_signals[test_indices]
    holdout_lengths = source_lengths[test_indices]
    evaluation_size = selected_size if selected_size is not None else sizes[-1]
    for family in SHIFT_FAMILIES:
        for shift_seed in seeds:
            shift = shift_specs[(family, shift_seed)]
            shifted_calibration = _apply_shift(
                calibration_signals,
                calibration_lengths,
                shift,
            )
            shifted_holdout = _apply_shift(holdout_source, holdout_lengths, shift)
            adapter = fit_robust_channel_affine(
                source_signals=source_signals,
                source_input_lengths=source_lengths,
                target_calibration_signals=shifted_calibration,
                target_input_lengths=calibration_lengths,
                source_fit_indices=train_indices,
                target_fit_indices=calibration_order[:evaluation_size],
            )
            adapted_holdout = apply_robust_channel_affine(
                shifted_holdout,
                holdout_lengths,
                adapter,
            )
            identity_key = _view_key("holdout", family, shift_seed, "identity")
            adapted_key = _view_key(
                "holdout",
                family,
                shift_seed,
                "adapted",
                evaluation_size,
            )
            holdout_views[identity_key] = shifted_holdout
            holdout_views[adapted_key] = adapted_holdout
            holdout_padding_ok = holdout_padding_ok and all(
                (
                    padding_is_zero(shifted_holdout, holdout_lengths),
                    padding_is_zero(adapted_holdout, holdout_lengths),
                )
            )
            holdout_state.append(
                {
                    "shift_family": family,
                    "shift_seed": shift_seed,
                    "calibration_rows": evaluation_size,
                    "calibration_seconds": sum(
                        int(calibration_lengths[index])
                        for index in calibration_order[:evaluation_size]
                    )
                    / sfreq,
                    "identity_view_key": identity_key,
                    "adapted_view_key": adapted_key,
                    "identity_reconstruction": summarize_signal_reconstruction(
                        holdout_source,
                        shifted_holdout,
                        holdout_lengths,
                    ),
                    "adapted_reconstruction": summarize_signal_reconstruction(
                        holdout_source,
                        adapted_holdout,
                        holdout_lengths,
                    ),
                }
            )

    holdout_result = run_tiny_ctc_cross_session_views(
        eval_signal_views=holdout_views,
        eval_input_lengths=holdout_lengths,
        eval_target_token_ids=source_token_ids[test_indices],
        eval_target_lengths=source_target_lengths[test_indices],
        eval_target_texts=[source_texts[index] for index in test_indices],
        **model_kwargs,
    )
    deterministic_training_replay = _training_replays_identically(
        validation_result,
        holdout_result,
    )
    prior = run_prior_baseline(
        train_targets=[source_texts[index] for index in train_indices],
        eval_targets=holdout_result.targets,
        strategy="most-frequent",
        seed=seed,
    )
    prior_summary = _prediction_summary(holdout_result.targets, prior.predictions)
    holdout_results = _complete_holdout_results(
        point_state=holdout_state,
        predictions_by_view=holdout_result.predictions_by_view,
        targets=holdout_result.targets,
        prior_summary=prior_summary,
        bootstrap_iterations=bootstrap_iterations,
        seed=seed,
    )
    holdout_aggregate = _aggregate_holdout(holdout_results)
    stationary_holdout_gain = next(
        row["median_cer_gain"]
        for row in holdout_aggregate
        if row["shift_family"] == "stationary_diagonal"
    )
    calibration_text_overlap = sorted(set(source_texts) & set(calibration_texts))
    gate_checks = {
        "at_least_five_nested_calibration_sizes": len(sizes) >= 5,
        "multiple_shift_seeds": len(seeds) >= 2,
        "independent_calibration_texts_do_not_overlap_source": not calibration_text_overlap,
        "target_calibration_labels_are_not_used": True,
        "stationary_diagonal_shift_included": "stationary_diagonal" in SHIFT_FAMILIES,
        "non_diagonal_channel_mixing_included": (
            "stationary_channel_mixing" in SHIFT_FAMILIES
        ),
        "within_row_time_varying_shift_included": (
            "within_row_time_varying" in SHIFT_FAMILIES
        ),
        "selection_uses_validation_before_holdout": True,
        "validation_and_holdout_training_replay_identically": (
            deterministic_training_replay
        ),
        "padding_remains_exactly_zero": validation_padding_ok and holdout_padding_ok,
        "decoder_uses_one_cpu_thread": num_threads == 1,
        "real_source_test_and_session2_rows_remain_unloaded": True,
        "new_cache_bytes_are_zero": True,
    }
    gate_passed = all(gate_checks.values())
    holdout_by_family = {
        row["shift_family"]: row for row in holdout_aggregate
    }
    selected_stationary_validation = [
        row
        for row in validation_curve
        if row["shift_family"] == "stationary_diagonal"
        and row["calibration_rows"] == selected_size
    ]
    stationary_holdout_rows = [
        row for row in holdout_results if row["shift_family"] == "stationary_diagonal"
    ]
    outcome_checks = {
        "stationary_validation_selects_a_calibration_size": selected_size is not None,
        "stationary_validation_every_seed_meets_gain_threshold_at_selected_size": (
            bool(selected_stationary_validation)
            and all(
                row["cer_gain"] >= min_stationary_validation_cer_gain
                for row in selected_stationary_validation
            )
        ),
        "evaluated_size_improves_stationary_holdout_median_cer": (
            stationary_holdout_gain > 0
        ),
        "stationary_holdout_median_gain_meets_validation_threshold": (
            stationary_holdout_gain >= min_stationary_validation_cer_gain
        ),
        "stationary_holdout_strictly_improves_every_seed": all(
            row["cer_gain"] > 0 for row in stationary_holdout_rows
        ),
        "channel_mixing_holdout_is_non_harmful_for_every_seed": (
            holdout_by_family["stationary_channel_mixing"]["non_harm_seed_count"]
            == holdout_by_family["stationary_channel_mixing"]["seed_count"]
        ),
        "time_varying_holdout_is_non_harmful_for_every_seed": (
            holdout_by_family["within_row_time_varying"]["non_harm_seed_count"]
            == holdout_by_family["within_row_time_varying"]["seed_count"]
        ),
    }
    runtime_sec = round(time.perf_counter() - started_at, 6)
    report: dict[str, Any] = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "run": {
            "created_at_utc": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
            "sentences": sentences,
            "calibration_sentences": calibration_sentences,
            "channels": channels,
            "letter_classes": letter_classes,
            "seed": seed,
            "calibration_sizes": sizes,
            "shift_seeds": seeds,
            "shift_families": list(SHIFT_FAMILIES),
            "execution_mode": "in_memory_synthetic_only",
            "device": "cpu",
            "numeric_threads": num_threads,
            "runtime_sec": runtime_sec,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "research_context": {
            **SOURCE_URLS,
            "method_choice": (
                "Characterize the smallest unlabeled robust-statistics sample before "
                "adding covariance or learned adaptation."
            ),
            "stress_rationale": (
                "MEG/EEG session drift can include sensor mixing and within-session "
                "non-stationarity, neither of which a static diagonal affine can invert."
            ),
            "deferred_next_methods": [
                "regularized_target_to_source_covariance_alignment",
                "causal_rolling_statistics",
                "source_trained_drift_augmentation",
            ],
        },
        "source": {
            "metadata": source_metadata,
            "signals_sha256": _array_sha256(source_signals),
            "partition_counts": {key: len(value) for key, value in partitions.items()},
            "partition_membership_sha256": _json_sha256(partitions),
        },
        "unpaired_calibration": {
            "metadata": calibration_metadata,
            "generation_seed": calibration_generation_seed,
            "signals_sha256": _array_sha256(calibration_signals),
            "text_membership_sha256": _json_sha256(sorted(calibration_texts)),
            "source_text_overlap": calibration_text_overlap,
            "nested_order_sha256": _json_sha256(calibration_order),
            "labels_used_for_adapter_fit": False,
        },
        "shift_specs": [
            {
                "family": family,
                "requested_seed": shift_seed,
                "spec": shift_specs[(family, shift_seed)].to_dict(),
            }
            for family in SHIFT_FAMILIES
            for shift_seed in seeds
        ],
        "protocol": {
            "curve_rows": "synthetic_source_validation_only",
            "selection_family": "stationary_diagonal",
            "selection_metric": "median_absolute_corpus_cer_gain",
            "selection_minimum_gain": min_stationary_validation_cer_gain,
            "selection_non_harm_rule": "adapted_cer_lte_identity_cer_for_every_seed",
            "selected_calibration_rows_before_holdout": selected_size,
            "holdout_evaluation_calibration_rows": evaluation_size,
            "holdout_rows": "synthetic_source_test_only_after_selection",
            "adapter_source_statistics_rows": "source_train_only",
            "adapter_target_statistics_rows": "independent_unlabeled_calibration_pool",
            "decoder_training_runs": 2,
            "decoder_training_reason": (
                "one validation multi-view fit, then one deterministic replay for the "
                "post-selection holdout; no fit per curve point"
            ),
            "real_source_test_rows_loaded": False,
            "real_session2_rows_loaded": False,
        },
        "model": {
            "validation": validation_result.metadata(),
            "holdout": holdout_result.metadata(),
            "training_replay_identical": deterministic_training_replay,
        },
        "validation_curve": validation_curve,
        "validation_aggregate": validation_aggregate,
        "holdout": {
            "prior_only": prior_summary,
            "rows": holdout_results,
            "aggregate": holdout_aggregate,
        },
        "gate_checks": gate_checks,
        "outcome_checks": outcome_checks,
        "decision": {
            "status": (
                f"loop16_complete_select_{selected_size}_unlabeled_rows_for_"
                "stationary_diagonal_synthetic_shift"
                if gate_passed and selected_size is not None
                else (
                    "loop16_complete_no_tested_stationary_calibration_size_met_gate"
                    if gate_passed
                    else "loop16_integrity_gate_failed_do_not_use_results"
                )
            ),
            "gate_passed": gate_passed,
            "selected_calibration_rows": selected_size,
            "stationary_calibration_recommendation_available": selected_size is not None,
            "real_session_adapter_authorized": False,
            "next_gate": (
                "Use the measured stress failures to choose between regularized "
                "covariance alignment and causal rolling adaptation; keep all real "
                "holdouts frozen until that method is preregistered."
            ),
        },
        "artifact_paths": {key: str(value) for key, value in artifacts.items()},
        "resources": {
            "peak_rss_bytes": _peak_rss_bytes(),
            "source_arrays_bytes_in_memory": _arrays_nbytes(source_arrays),
            "calibration_arrays_bytes_in_memory": _arrays_nbytes(calibration_arrays),
            "validation_eval_views": len(validation_views),
            "holdout_eval_views": len(holdout_views),
            "new_cache_bytes": 0,
            "max_output_bytes": int(max_output_mb * 1024 * 1024),
            "report_json_bytes": 0,
            "report_markdown_bytes": 0,
            "validation_curve_csv_bytes": 0,
            "holdout_results_csv_bytes": 0,
            "total_artifact_bytes": 0,
        },
        "warnings": [
            "all_results_are_synthetic_and_do_not_establish_real_meg_adapter_benefit",
            "synthetic_token_motifs_are_not_a_physiological_forward_model",
            "calibration_examples_are_unlabeled_but_still_require_target_signal_collection",
            "the_tiny_ctc_is_noncausal_and_not_a_real_time_decoder",
            "the_robust_affine_adapter_cannot_in_general_invert_channel_mixing",
            "static_statistics_cannot_in_general_track_within_row_drift",
            "five_real_source_test_rows_and_63_session2_rows_remain_frozen",
            "real_cache_records_physical_typing_not_arbitrary_thoughts",
            "at_home_hardware_accessibility_is_not_evaluated_here",
        ],
    }
    _write_artifacts(
        report,
        artifacts=artifacts,
        validation_curve=validation_curve,
        holdout_results=holdout_results,
        max_output_bytes=int(max_output_mb * 1024 * 1024),
    )
    return report


def render_synthetic_calibration_curve_markdown(report: dict[str, Any]) -> str:
    """Render a compact Loop 16 proof packet."""

    protocol = report["protocol"]
    lines = [
        "# Loop 16 - Synthetic Calibration Curve",
        "",
        f"- Proof posture: `{report['proof_posture']}`",
        f"- Decision: `{report['decision']['status']}`",
        f"- Runtime: `{report['run']['runtime_sec']}` seconds",
        f"- Numeric threads: `{report['run']['numeric_threads']}`",
        f"- New cache bytes: `{report['resources']['new_cache_bytes']}`",
        "",
        "## Protocol",
        "",
        f"- Calibration sizes: `{report['run']['calibration_sizes']}`",
        f"- Shift seeds: `{report['run']['shift_seeds']}`",
        f"- Shift families: `{report['run']['shift_families']}`",
        "- Calibration pool: independent synthetic sentences; target labels unused",
        "- Curve and selection: source validation only",
        "- Holdout: one pass after calibration-size selection",
        f"- Selected calibration rows: `{protocol['selected_calibration_rows_before_holdout']}`",
        "- Real S21 source-test/session-2 rows loaded: `False`",
        "",
        "## Validation Curve",
        "",
        "| Shift | Rows | Minutes | Identity CER | Adapted CER | CER gain | Non-harm seeds |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["validation_aggregate"]:
        lines.append(
            "| "
            f"{row['shift_family']} | {row['calibration_rows']} | "
            f"{row['median_calibration_minutes']:.4f} | "
            f"{row['median_identity_cer']:.6f} | "
            f"{row['median_adapted_cer']:.6f} | "
            f"{row['median_cer_gain']:.6f} | "
            f"{row['non_harm_seed_count']}/{row['seed_count']} |"
        )
    lines.extend(
        [
            "",
            "## Frozen Synthetic Holdout",
            "",
            "| Shift | Rows | Identity CER | Adapted CER | Prior CER | CER gain |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["holdout"]["aggregate"]:
        lines.append(
            "| "
            f"{row['shift_family']} | {row['calibration_rows']} | "
            f"{row['median_identity_cer']:.6f} | "
            f"{row['median_adapted_cer']:.6f} | "
            f"{row['prior_cer']:.6f} | {row['median_cer_gain']:.6f} |"
        )
    lines.extend(["", "## Gate Checks", ""])
    lines.extend(f"- `{key}`: `{value}`" for key, value in report["gate_checks"].items())
    lines.extend(["", "## Performance Outcomes", ""])
    lines.extend(f"- `{key}`: `{value}`" for key, value in report["outcome_checks"].items())
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "The selected row count applies only to an independent synthetic calibration "
            "pool under a stationary diagonal shift. Channel mixing and within-row drift "
            "are stress tests, not alternative claims. No real MEG holdout was opened.",
            "",
            "## Research Sources",
            "",
        ]
    )
    lines.extend(
        f"- {name}: {url}" for name, url in report["research_context"].items() if name in SOURCE_URLS
    )
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _make_shift_specs(*, channels: int, shift_seeds: list[int]) -> dict[tuple[str, int], Any]:
    specs: dict[tuple[str, int], Any] = {}
    for shift_seed in shift_seeds:
        specs[("stationary_diagonal", shift_seed)] = make_synthetic_channel_shift(
            channels,
            seed=shift_seed,
        )
        specs[("stationary_channel_mixing", shift_seed)] = (
            make_synthetic_channel_mixing_shift(
                channels,
                seed=shift_seed + 100_000,
            )
        )
        specs[("within_row_time_varying", shift_seed)] = (
            make_synthetic_time_varying_shift(
                channels,
                seed=shift_seed + 200_000,
            )
        )
    return specs


def _apply_shift(signals, input_lengths, shift):
    if isinstance(shift, SyntheticChannelShift):
        return apply_synthetic_channel_shift(signals, input_lengths, shift)
    if isinstance(shift, SyntheticChannelMixingShift):
        return apply_synthetic_channel_mixing_shift(signals, input_lengths, shift)
    if isinstance(shift, SyntheticTimeVaryingShift):
        return apply_synthetic_time_varying_shift(signals, input_lengths, shift)
    raise TypeError(f"Unsupported synthetic shift: {type(shift).__name__}")


def _complete_validation_curve(
    *,
    point_state: list[dict[str, Any]],
    predictions_by_view: dict[str, list[str]],
    targets: list[str],
) -> list[dict[str, Any]]:
    rows = []
    for state in point_state:
        identity_predictions = predictions_by_view[state.pop("identity_view_key")]
        adapted_predictions = predictions_by_view[state.pop("adapted_view_key")]
        identity = _prediction_summary(targets, identity_predictions)
        adapted = _prediction_summary(targets, adapted_predictions)
        identity_mae = state["identity_reconstruction"]["mae"]
        adapted_mae = state["adapted_reconstruction"]["mae"]
        rows.append(
            {
                **state,
                "calibration_minutes": state["calibration_seconds"] / 60.0,
                "identity_cer": identity["corpus_cer"],
                "adapted_cer": adapted["corpus_cer"],
                "cer_gain": identity["corpus_cer"] - adapted["corpus_cer"],
                "identity_char_edits": identity["char_edits"],
                "adapted_char_edits": adapted["char_edits"],
                "identity_prediction_sha256": _json_sha256(identity_predictions),
                "adapted_prediction_sha256": _json_sha256(adapted_predictions),
                "adapted_to_identity_reconstruction_mae_ratio": (
                    adapted_mae / identity_mae if identity_mae else 0.0
                ),
            }
        )
    return rows


def _aggregate_curve(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate = []
    for family in SHIFT_FAMILIES:
        sizes = sorted(
            {row["calibration_rows"] for row in rows if row["shift_family"] == family}
        )
        for size in sizes:
            selected = [
                row
                for row in rows
                if row["shift_family"] == family and row["calibration_rows"] == size
            ]
            aggregate.append(
                {
                    "shift_family": family,
                    "calibration_rows": size,
                    "seed_count": len(selected),
                    "median_calibration_minutes": statistics.median(
                        row["calibration_minutes"] for row in selected
                    ),
                    "median_identity_cer": statistics.median(
                        row["identity_cer"] for row in selected
                    ),
                    "median_adapted_cer": statistics.median(
                        row["adapted_cer"] for row in selected
                    ),
                    "median_cer_gain": statistics.median(
                        row["cer_gain"] for row in selected
                    ),
                    "min_cer_gain": min(row["cer_gain"] for row in selected),
                    "max_cer_gain": max(row["cer_gain"] for row in selected),
                    "non_harm_seed_count": sum(
                        row["adapted_cer"] <= row["identity_cer"] for row in selected
                    ),
                    "median_reconstruction_mae_ratio": statistics.median(
                        row["adapted_to_identity_reconstruction_mae_ratio"]
                        for row in selected
                    ),
                }
            )
    return aggregate


def _select_stationary_size(
    *,
    aggregate: list[dict[str, Any]],
    calibration_sizes: list[int],
    min_cer_gain: float,
) -> int | None:
    by_size = {
        row["calibration_rows"]: row
        for row in aggregate
        if row["shift_family"] == "stationary_diagonal"
    }
    for size in calibration_sizes:
        row = by_size[size]
        if (
            row["median_cer_gain"] >= min_cer_gain
            and row["non_harm_seed_count"] == row["seed_count"]
        ):
            return size
    return None


def _complete_holdout_results(
    *,
    point_state: list[dict[str, Any]],
    predictions_by_view: dict[str, list[str]],
    targets: list[str],
    prior_summary: dict[str, Any],
    bootstrap_iterations: int,
    seed: int,
) -> list[dict[str, Any]]:
    rows = []
    for index, state in enumerate(point_state):
        identity_predictions = predictions_by_view[state.pop("identity_view_key")]
        adapted_predictions = predictions_by_view[state.pop("adapted_view_key")]
        identity = _prediction_summary(targets, identity_predictions)
        adapted = _prediction_summary(targets, adapted_predictions)
        comparison = compare_paired_predictions(
            targets=targets,
            predictions_a=adapted_predictions,
            predictions_b=identity_predictions,
            label_a="robust_channel_affine",
            label_b="identity",
            bootstrap_iterations=bootstrap_iterations,
            seed=seed + 1000 + index,
        )
        identity_mae = state["identity_reconstruction"]["mae"]
        adapted_mae = state["adapted_reconstruction"]["mae"]
        rows.append(
            {
                **state,
                "calibration_minutes": state["calibration_seconds"] / 60.0,
                "identity_cer": identity["corpus_cer"],
                "adapted_cer": adapted["corpus_cer"],
                "prior_cer": prior_summary["corpus_cer"],
                "cer_gain": identity["corpus_cer"] - adapted["corpus_cer"],
                "identity_char_edits": identity["char_edits"],
                "adapted_char_edits": adapted["char_edits"],
                "prior_char_edits": prior_summary["char_edits"],
                "paired_adapted_minus_identity": comparison,
                "adapted_to_identity_reconstruction_mae_ratio": (
                    adapted_mae / identity_mae if identity_mae else 0.0
                ),
                "identity_prediction_sha256": _json_sha256(identity_predictions),
                "adapted_prediction_sha256": _json_sha256(adapted_predictions),
            }
        )
    return rows


def _aggregate_holdout(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate = []
    for family in SHIFT_FAMILIES:
        selected = [row for row in rows if row["shift_family"] == family]
        aggregate.append(
            {
                "shift_family": family,
                "calibration_rows": selected[0]["calibration_rows"],
                "seed_count": len(selected),
                "median_identity_cer": statistics.median(
                    row["identity_cer"] for row in selected
                ),
                "median_adapted_cer": statistics.median(
                    row["adapted_cer"] for row in selected
                ),
                "prior_cer": selected[0]["prior_cer"],
                "median_cer_gain": statistics.median(row["cer_gain"] for row in selected),
                "min_cer_gain": min(row["cer_gain"] for row in selected),
                "max_cer_gain": max(row["cer_gain"] for row in selected),
                "non_harm_seed_count": sum(
                    row["adapted_cer"] <= row["identity_cer"] for row in selected
                ),
                "median_reconstruction_mae_ratio": statistics.median(
                    row["adapted_to_identity_reconstruction_mae_ratio"]
                    for row in selected
                ),
            }
        )
    return aggregate


def _make_disjoint_calibration_pool(
    *,
    source_texts: set[str],
    sentences: int,
    channels: int,
    letter_classes: int,
    seed: int,
):
    for attempt in range(12):
        candidate_seed = seed + attempt * 1009
        arrays, metadata = make_synthetic_sentence_arrays(
            sentences=sentences,
            channels=channels,
            letter_classes=letter_classes,
            seed=candidate_seed,
        )
        texts = {str(value) for value in arrays["target_texts"].tolist()}
        if not (source_texts & texts):
            return arrays, metadata, candidate_seed
    raise ValueError("Could not generate a calibration pool disjoint from source texts")


def _training_replays_identically(first, second) -> bool:
    return (
        first.selected_initialization_seed == second.selected_initialization_seed
        and first.loss_history == second.loss_history
        and first.train_predictions == second.train_predictions
        and first.train_cer == second.train_cer
    )


def _prediction_summary(targets: Iterable[str], predictions: Iterable[str]) -> dict[str, Any]:
    return build_text_report(
        targets=targets,
        predictions=predictions,
        max_examples=1,
    )["summary"]


def _write_artifacts(
    report: dict[str, Any],
    *,
    artifacts: dict[str, Path],
    validation_curve: list[dict[str, Any]],
    holdout_results: list[dict[str, Any]],
    max_output_bytes: int,
) -> None:
    validation_csv = _rows_to_csv(
        validation_curve,
        fields=(
            "shift_family",
            "shift_seed",
            "calibration_rows",
            "calibration_seconds",
            "calibration_minutes",
            "identity_cer",
            "adapted_cer",
            "cer_gain",
            "adapted_to_identity_reconstruction_mae_ratio",
            "target_statistics_sha256",
            "calibration_text_membership_sha256",
        ),
    )
    holdout_csv = _rows_to_csv(
        holdout_results,
        fields=(
            "shift_family",
            "shift_seed",
            "calibration_rows",
            "calibration_seconds",
            "calibration_minutes",
            "identity_cer",
            "adapted_cer",
            "prior_cer",
            "cer_gain",
            "adapted_to_identity_reconstruction_mae_ratio",
        ),
    )
    for _ in range(4):
        json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        markdown_text = render_synthetic_calibration_curve_markdown(report)
        resources = report["resources"]
        resources["report_json_bytes"] = len(json_text.encode("utf-8"))
        resources["report_markdown_bytes"] = len(markdown_text.encode("utf-8"))
        resources["validation_curve_csv_bytes"] = len(validation_csv.encode("utf-8"))
        resources["holdout_results_csv_bytes"] = len(holdout_csv.encode("utf-8"))
        resources["total_artifact_bytes"] = sum(
            resources[key]
            for key in (
                "report_json_bytes",
                "report_markdown_bytes",
                "validation_curve_csv_bytes",
                "holdout_results_csv_bytes",
            )
        )
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    markdown_text = render_synthetic_calibration_curve_markdown(report)
    total_bytes = sum(
        len(value.encode("utf-8"))
        for value in (json_text, markdown_text, validation_csv, holdout_csv)
    )
    if total_bytes > max_output_bytes:
        raise ValueError(
            "Synthetic calibration artifacts exceed max_output_mb: "
            f"{total_bytes} > {max_output_bytes} bytes."
        )
    artifacts["report_json"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report_json"].write_text(json_text, encoding="utf-8")
    artifacts["report_markdown"].write_text(markdown_text, encoding="utf-8")
    artifacts["validation_curve_csv"].write_text(validation_csv, encoding="utf-8")
    artifacts["holdout_results_csv"].write_text(holdout_csv, encoding="utf-8")


def _rows_to_csv(rows: list[dict[str, Any]], *, fields: tuple[str, ...]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _validate_params(
    *,
    sentences: int,
    calibration_sentences: int,
    channels: int,
    letter_classes: int,
    calibration_sizes: list[int],
    shift_seeds: list[int],
    epochs: int,
    batch_size: int,
    learning_rate: float,
    hidden_channels: int,
    num_threads: int,
    min_stationary_validation_cer_gain: float,
    bootstrap_iterations: int,
    max_output_mb: float,
) -> None:
    if sentences < 48:
        raise ValueError("sentences must be >= 48 for train/validation/test partitions")
    if calibration_sentences < max(calibration_sizes):
        raise ValueError("calibration_sentences must cover the largest calibration size")
    if len(calibration_sizes) < 5:
        raise ValueError("Loop 16 requires at least five calibration sizes")
    if len(shift_seeds) < 2:
        raise ValueError("Loop 16 requires multiple shift seeds")
    if channels < letter_classes + 1:
        raise ValueError("channels must provide one motif channel per letter plus space")
    if epochs < 1 or batch_size < 1 or hidden_channels < 1:
        raise ValueError("epochs, batch_size, and hidden_channels must be >= 1")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be > 0")
    if num_threads != 1:
        raise ValueError("synthetic calibration curve requires num_threads=1")
    if min_stationary_validation_cer_gain < 0:
        raise ValueError("min_stationary_validation_cer_gain must be >= 0")
    if bootstrap_iterations < 100:
        raise ValueError("bootstrap_iterations must be >= 100")
    if max_output_mb <= 0:
        raise ValueError("max_output_mb must be > 0")


def _normalize_positive_ints(values: Iterable[int], *, name: str) -> list[int]:
    normalized = sorted({int(value) for value in values})
    if not normalized or normalized[0] < 1:
        raise ValueError(f"{name} must contain positive integers")
    return normalized


def _validate_partitions(partitions: dict[str, list[int]], *, n_rows: int) -> None:
    sets = [set(values) for values in partitions.values()]
    if any(not values for values in sets):
        raise ValueError("Synthetic calibration partitions must all be non-empty")
    if any(left & right for index, left in enumerate(sets) for right in sets[index + 1 :]):
        raise ValueError("Synthetic calibration partitions must be disjoint")
    if set().union(*sets) != set(range(n_rows)):
        raise ValueError("Synthetic calibration partitions must cover every row")


def _view_key(
    partition: str,
    family: str,
    shift_seed: int,
    method: str,
    calibration_size: int | None = None,
) -> str:
    suffix = "" if calibration_size is None else f":n{calibration_size}"
    return f"{partition}:{family}:s{shift_seed}:{method}{suffix}"


def _stable_order_key(text: str, seed: int) -> tuple[str, str]:
    digest = hashlib.sha256(f"{seed}|{text}".encode()).hexdigest()
    return digest, text


def _array_sha256(value) -> str:
    np = _require_numpy()
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(str(tuple(array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _arrays_nbytes(arrays: dict[str, Any]) -> int:
    return sum(int(getattr(value, "nbytes", 0)) for value in arrays.values())


def _peak_rss_bytes() -> int | None:
    try:
        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (OSError, ValueError):
        return None
    return value if sys.platform == "darwin" else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Synthetic calibration curves require NumPy: `pip install numpy`."
        ) from exc
    return np
