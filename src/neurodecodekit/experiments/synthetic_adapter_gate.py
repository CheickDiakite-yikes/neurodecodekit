"""Synthetic-only gate for the first resource-bounded session adapter."""

from __future__ import annotations

import hashlib
import json
import platform
import resource
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
    run_tiny_ctc_cross_session,
)
from neurodecodekit.preprocess.session_adapter import (
    apply_robust_channel_affine,
    apply_synthetic_channel_shift,
    fit_robust_channel_affine,
    make_synthetic_channel_shift,
    padding_is_zero,
    summarize_signal_reconstruction,
)
from neurodecodekit.training.synthetic_sentences import make_synthetic_sentence_arrays


GATE_SCHEMA_NAME = "neurodecodekit-synthetic-session-adapter-gate"
GATE_SCHEMA_VERSION = 1
PROOF_POSTURE = "synthetic_domain_shift_only_no_real_adapter_benefit_claim"
BRAIN2QWERTY_V2_SOURCE = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
ADABN_SOURCE = "https://arxiv.org/abs/1603.04779"
EUCLIDEAN_ALIGNMENT_SOURCE = (
    "https://doi.org/10.1109/TBME.2019.2913914"
)
CROSS_SESSION_LATENT_ALIGNMENT_SOURCE = (
    "https://proceedings.mlr.press/v162/jude22a.html"
)


def run_synthetic_adapter_gate(
    *,
    out_dir: str | Path,
    sentences: int = 96,
    channels: int = 6,
    letter_classes: int = 4,
    seed: int = 23,
    epochs: int = 50,
    batch_size: int = 16,
    learning_rate: float = 0.02,
    hidden_channels: int = 16,
    num_threads: int = 1,
    min_validation_cer_gain: float = 0.10,
    bootstrap_iterations: int = 2000,
    max_output_mb: float = 2.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Run a deterministic identity-versus-robust-affine synthetic comparison."""

    _validate_gate_params(
        sentences=sentences,
        channels=channels,
        letter_classes=letter_classes,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        num_threads=num_threads,
        min_validation_cer_gain=min_validation_cer_gain,
        bootstrap_iterations=bootstrap_iterations,
        max_output_mb=max_output_mb,
    )
    output_dir = Path(out_dir)
    artifacts = {
        "report_json": output_dir / "report.json",
        "report_markdown": output_dir / "report.md",
        "identity_holdout_predictions": output_dir / "identity_holdout_predictions.txt",
        "adapted_holdout_predictions": output_dir / "adapted_holdout_predictions.txt",
        "prior_holdout_predictions": output_dir / "prior_holdout_predictions.txt",
    }
    existing = [path for path in artifacts.values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Synthetic adapter artifacts already exist: "
            + ", ".join(str(path) for path in existing)
        )

    started_at = time.perf_counter()
    np = _require_numpy()
    arrays, synthetic_metadata = make_synthetic_sentence_arrays(
        sentences=sentences,
        channels=channels,
        letter_classes=letter_classes,
        seed=seed,
    )
    signals = np.asarray(arrays["signals"], dtype="float32")
    input_lengths = np.asarray(arrays["input_lengths"], dtype="int32")
    target_token_ids = np.asarray(arrays["target_token_ids"], dtype="int16")
    target_lengths = np.asarray(arrays["target_lengths"], dtype="int32")
    target_texts = [str(value) for value in arrays["target_texts"].tolist()]
    train_indices, remaining_indices = deterministic_text_holdout_indices(
        target_texts,
        train_fraction=2.0 / 3.0,
    )
    remaining_texts = [target_texts[index] for index in remaining_indices]
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

    shift = make_synthetic_channel_shift(channels, seed=seed + 2004)
    calibration_signals = apply_synthetic_channel_shift(
        signals[train_indices],
        input_lengths[train_indices],
        shift,
    )
    shifted_validation = apply_synthetic_channel_shift(
        signals[validation_indices],
        input_lengths[validation_indices],
        shift,
    )
    shifted_test = apply_synthetic_channel_shift(
        signals[test_indices],
        input_lengths[test_indices],
        shift,
    )
    adapter = fit_robust_channel_affine(
        source_signals=signals,
        source_input_lengths=input_lengths,
        target_calibration_signals=calibration_signals,
        target_input_lengths=input_lengths[train_indices],
        source_fit_indices=train_indices,
    )
    adapted_validation = apply_robust_channel_affine(
        shifted_validation,
        input_lengths[validation_indices],
        adapter,
    )
    adapted_test = apply_robust_channel_affine(
        shifted_test,
        input_lengths[test_indices],
        adapter,
    )

    model_kwargs = {
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
    identity_validation = _run_eval(
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
        target_texts=target_texts,
        eval_indices=validation_indices,
        eval_signals=shifted_validation,
        model_kwargs=model_kwargs,
    )
    adapted_validation_result = _run_eval(
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
        target_texts=target_texts,
        eval_indices=validation_indices,
        eval_signals=adapted_validation,
        model_kwargs=model_kwargs,
    )
    validation_reports = {
        "identity": _prediction_summary(identity_validation.targets, identity_validation.predictions),
        "robust_channel_affine": _prediction_summary(
            adapted_validation_result.targets,
            adapted_validation_result.predictions,
        ),
    }
    validation_gain = (
        validation_reports["identity"]["corpus_cer"]
        - validation_reports["robust_channel_affine"]["corpus_cer"]
    )
    selected_adapter = (
        "robust_channel_affine"
        if validation_gain >= min_validation_cer_gain
        else "identity"
    )

    identity_test = _run_eval(
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
        target_texts=target_texts,
        eval_indices=test_indices,
        eval_signals=shifted_test,
        model_kwargs=model_kwargs,
    )
    adapted_test_result = _run_eval(
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
        target_texts=target_texts,
        eval_indices=test_indices,
        eval_signals=adapted_test,
        model_kwargs=model_kwargs,
    )
    deterministic_model_replay = _model_runs_match(
        [
            identity_validation,
            adapted_validation_result,
            identity_test,
            adapted_test_result,
        ]
    )
    test_reports = {
        "identity": _prediction_summary(identity_test.targets, identity_test.predictions),
        "robust_channel_affine": _prediction_summary(
            adapted_test_result.targets,
            adapted_test_result.predictions,
        ),
    }
    train_targets = [target_texts[index] for index in train_indices]
    prior = run_prior_baseline(
        train_targets=train_targets,
        eval_targets=adapted_test_result.targets,
        strategy="most-frequent",
        seed=seed,
    )
    prior_summary = _prediction_summary(adapted_test_result.targets, prior.predictions)

    identity_reconstruction = summarize_signal_reconstruction(
        signals[test_indices],
        shifted_test,
        input_lengths[test_indices],
    )
    adapted_reconstruction = summarize_signal_reconstruction(
        signals[test_indices],
        adapted_test,
        input_lengths[test_indices],
    )
    reconstruction_mae_ratio = (
        adapted_reconstruction["mae"] / identity_reconstruction["mae"]
    )
    all_padding_zero = all(
        (
            padding_is_zero(value, lengths)
            for value, lengths in (
                (calibration_signals, input_lengths[train_indices]),
                (shifted_validation, input_lengths[validation_indices]),
                (shifted_test, input_lengths[test_indices]),
                (adapted_validation, input_lengths[validation_indices]),
                (adapted_test, input_lengths[test_indices]),
            )
        )
    )
    gate_checks = {
        "partitions_are_disjoint_and_complete": True,
        "adapter_fit_uses_no_target_labels": True,
        "real_cache_and_consumed_evaluation_remain_unloaded": True,
        "validation_gain_meets_threshold": validation_gain >= min_validation_cer_gain,
        "validation_selected_robust_channel_affine": (
            selected_adapter == "robust_channel_affine"
        ),
        "selected_adapter_improves_frozen_holdout": (
            test_reports["robust_channel_affine"]["corpus_cer"]
            < test_reports["identity"]["corpus_cer"]
        ),
        "adapted_reconstruction_mae_ratio_below_0_001": (
            reconstruction_mae_ratio < 0.001
        ),
        "padding_remains_exactly_zero": all_padding_zero,
        "decoder_training_replays_identically": deterministic_model_replay,
        "decoder_uses_one_cpu_thread": num_threads == 1,
    }
    gate_passed = all(gate_checks.values())
    run_runtime = round(time.perf_counter() - started_at, 6)
    report: dict[str, Any] = {
        "schema": {"name": GATE_SCHEMA_NAME, "version": GATE_SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "run": {
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "sentences": sentences,
            "channels": channels,
            "letter_classes": letter_classes,
            "seed": seed,
            "shift_seed": shift.seed,
            "execution_mode": "in_memory_synthetic_only",
            "device": "cpu",
            "numeric_threads": num_threads,
            "runtime_sec": run_runtime,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "research_context": {
            "brain2qwerty_v2": BRAIN2QWERTY_V2_SOURCE,
            "adaptive_batch_normalization": ADABN_SOURCE,
            "euclidean_alignment": EUCLIDEAN_ALIGNMENT_SOURCE,
            "cross_session_latent_alignment": CROSS_SESSION_LATENT_ALIGNMENT_SOURCE,
            "method_choice": (
                "Start with unlabeled per-channel median/IQR matching because it is diagonal, "
                "parameter-free, CPU-cheap, and directly tests the affine-shift hypothesis."
            ),
            "deferred_methods": [
                "full_covariance_euclidean_alignment",
                "learned_linear_channel_mixing",
                "latent_sequential_domain_adapter",
            ],
        },
        "synthetic_source": {
            "metadata": synthetic_metadata,
            "signals_sha256": _array_sha256(signals),
            "signal_bytes_in_memory": int(signals.nbytes),
        },
        "domain_shift": shift.to_dict(),
        "adapter": adapter.to_dict(),
        "protocol": {
            "partitions": {key: list(value) for key, value in partitions.items()},
            "partition_counts": {key: len(value) for key, value in partitions.items()},
            "partition_membership_sha256": _json_sha256(partitions),
            "decoder_fit_rows": "source_train_only",
            "adapter_source_statistics_rows": "source_train_only",
            "adapter_target_statistics_rows": "synthetic_shifted_source_train_only",
            "adapter_target_labels_used": False,
            "selection_rows": "synthetic_shifted_source_validation_only",
            "holdout_rows": "synthetic_shifted_source_test_only_after_selection",
            "real_source_test_rows_loaded": False,
            "real_session2_rows_loaded": False,
            "selection_rule": {
                "candidate_order": ["identity", "robust_channel_affine"],
                "metric": "validation_corpus_cer",
                "minimum_absolute_cer_gain": min_validation_cer_gain,
                "tie_break": "identity",
            },
            "selected_adapter_before_holdout": selected_adapter,
        },
        "model": {
            **identity_test.metadata(),
            "identical_training_replay_across_four_comparisons": deterministic_model_replay,
        },
        "validation": {
            "identity": validation_reports["identity"],
            "robust_channel_affine": validation_reports["robust_channel_affine"],
            "absolute_corpus_cer_gain": validation_gain,
            "selected_adapter": selected_adapter,
        },
        "holdout": {
            "identity": test_reports["identity"],
            "robust_channel_affine": test_reports["robust_channel_affine"],
            "prior_only": prior_summary,
            "adapted_vs_identity": compare_paired_predictions(
                targets=adapted_test_result.targets,
                predictions_a=adapted_test_result.predictions,
                predictions_b=identity_test.predictions,
                label_a="robust_channel_affine",
                label_b="identity",
                bootstrap_iterations=bootstrap_iterations,
                seed=seed + 17,
            ),
            "adapted_vs_prior_only": compare_paired_predictions(
                targets=adapted_test_result.targets,
                predictions_a=adapted_test_result.predictions,
                predictions_b=prior.predictions,
                label_a="robust_channel_affine",
                label_b="prior_only",
                bootstrap_iterations=bootstrap_iterations,
                seed=seed + 31,
            ),
        },
        "signal_reconstruction": {
            "identity_shifted": identity_reconstruction,
            "robust_channel_affine": adapted_reconstruction,
            "adapted_to_identity_mae_ratio": reconstruction_mae_ratio,
        },
        "gate_checks": gate_checks,
        "decision": {
            "status": (
                "synthetic_gate_passed_select_robust_channel_affine"
                if gate_passed
                else "synthetic_gate_failed_do_not_advance_adapter"
            ),
            "gate_passed": gate_passed,
            "real_session_adapter_authorized": False,
            "next_gate": (
                "Loop 16 calibration-size curve on synthetic shifts; preserve all consumed "
                "real evaluation rows and pre-register any future real holdout."
            ),
        },
        "artifact_paths": {key: str(value) for key, value in artifacts.items()},
        "resources": {
            "peak_rss_bytes": _peak_rss_bytes(),
            "source_arrays_bytes_in_memory": _arrays_nbytes(arrays),
            "new_cache_bytes": 0,
            "max_output_bytes": int(max_output_mb * 1024 * 1024),
            "report_json_bytes": 0,
            "report_markdown_bytes": 0,
            "prediction_bytes": 0,
            "total_artifact_bytes": 0,
        },
        "warnings": [
            "synthetic_affine_shift_is_a_best_case_not_a_physiological_session_model",
            "synthetic_gate_does_not_establish_real_session_adapter_benefit",
            "consumed_s21_session2_evaluation_was_not_loaded_or_retuned",
            "five_real_source_test_rows_remain_frozen",
            "target_calibration_statistics_are_unlabeled_but_use_target_signal_samples",
            "tiny_ctc_is_noncausal_and_not_a_real_time_decoder",
            "full_covariance_and_learned_adapters_remain_unjustified_by_this_gate",
            "real_cache_records_physical_typing_not_arbitrary_thoughts",
        ],
    }
    prediction_texts = {
        "identity_holdout_predictions": _text_rows(identity_test.predictions),
        "adapted_holdout_predictions": _text_rows(adapted_test_result.predictions),
        "prior_holdout_predictions": _text_rows(prior.predictions),
    }
    _write_artifacts(
        report,
        artifacts=artifacts,
        prediction_texts=prediction_texts,
        max_output_bytes=int(max_output_mb * 1024 * 1024),
    )
    return report


def render_synthetic_adapter_gate_markdown(report: dict[str, Any]) -> str:
    """Render the compact proof packet for the synthetic adapter gate."""

    validation = report["validation"]
    holdout = report["holdout"]
    reconstruction = report["signal_reconstruction"]
    resources = report["resources"]
    lines = [
        "# Loop 15 Stage B - Synthetic Session Adapter Gate",
        "",
        f"- Proof posture: `{report['proof_posture']}`",
        f"- Decision: `{report['decision']['status']}`",
        f"- Runtime: `{report['run']['runtime_sec']}` seconds",
        f"- Numeric threads: `{report['run']['numeric_threads']}`",
        f"- New cache bytes: `{resources['new_cache_bytes']}`",
        "",
        "## Protocol",
        "",
        f"- Partition rows: `{report['protocol']['partition_counts']}`",
        "- Decoder fit: source train only",
        "- Adapter fit: source-train and unlabeled shifted-calibration statistics only",
        "- Selection: shifted source validation only",
        "- Holdout: shifted source test after selection",
        "- Real S21 source-test/session-2 rows loaded: `False`",
        "",
        "## Results",
        "",
        "| Partition | Identity CER | Adapted CER | Prior CER |",
        "|---|---:|---:|---:|",
        (
            "| Validation | "
            f"{validation['identity']['corpus_cer']:.6f} | "
            f"{validation['robust_channel_affine']['corpus_cer']:.6f} | n/a |"
        ),
        (
            "| Frozen synthetic holdout | "
            f"{holdout['identity']['corpus_cer']:.6f} | "
            f"{holdout['robust_channel_affine']['corpus_cer']:.6f} | "
            f"{holdout['prior_only']['corpus_cer']:.6f} |"
        ),
        "",
        f"Validation CER gain: `{validation['absolute_corpus_cer_gain']:.6f}`",
        "",
        "## Reconstruction",
        "",
        "| View | MAE | RMSE | Max abs. error |",
        "|---|---:|---:|---:|",
        (
            "| Shifted identity | "
            f"{reconstruction['identity_shifted']['mae']:.9g} | "
            f"{reconstruction['identity_shifted']['rmse']:.9g} | "
            f"{reconstruction['identity_shifted']['max_abs_error']:.9g} |"
        ),
        (
            "| Robust affine | "
            f"{reconstruction['robust_channel_affine']['mae']:.9g} | "
            f"{reconstruction['robust_channel_affine']['rmse']:.9g} | "
            f"{reconstruction['robust_channel_affine']['max_abs_error']:.9g} |"
        ),
        "",
        "## Gate Checks",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in report["gate_checks"].items())
    lines.extend(
        [
            "",
            "## Research Boundary",
            "",
            f"- Brain2Qwerty v2: {report['research_context']['brain2qwerty_v2']}",
            f"- Adaptive Batch Normalization: {report['research_context']['adaptive_batch_normalization']}",
            f"- Euclidean Alignment: {report['research_context']['euclidean_alignment']}",
            "",
            "This proves recovery from a known diagonal synthetic affine shift. It does not "
            "show benefit on real MEG, non-affine drift, unseen people, causal decoding, or "
            "at-home hardware.",
            "",
            "## Warnings",
            "",
        ]
    )
    lines.extend(f"- `{warning}`" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _run_eval(
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    target_texts: list[str],
    eval_indices: list[int],
    eval_signals,
    model_kwargs: dict[str, Any],
):
    return run_tiny_ctc_cross_session(
        train_signals=signals,
        train_input_lengths=input_lengths,
        train_target_token_ids=target_token_ids,
        train_target_lengths=target_lengths,
        train_target_texts=target_texts,
        eval_signals=eval_signals,
        eval_input_lengths=input_lengths[eval_indices],
        eval_target_token_ids=target_token_ids[eval_indices],
        eval_target_lengths=target_lengths[eval_indices],
        eval_target_texts=[target_texts[index] for index in eval_indices],
        **model_kwargs,
    )


def _prediction_summary(targets: Iterable[str], predictions: Iterable[str]) -> dict[str, Any]:
    return build_text_report(
        targets=targets,
        predictions=predictions,
        max_examples=1,
    )["summary"]


def _model_runs_match(results: list[Any]) -> bool:
    first = results[0]
    return all(
        result.selected_initialization_seed == first.selected_initialization_seed
        and result.loss_history == first.loss_history
        and result.train_predictions == first.train_predictions
        and result.train_cer == first.train_cer
        for result in results[1:]
    )


def _validate_partitions(partitions: dict[str, list[int]], *, n_rows: int) -> None:
    sets = [set(values) for values in partitions.values()]
    if any(not values for values in sets):
        raise ValueError("Synthetic adapter partitions must all be non-empty.")
    if any(left & right for index, left in enumerate(sets) for right in sets[index + 1 :]):
        raise ValueError("Synthetic adapter partitions must be disjoint.")
    if set().union(*sets) != set(range(n_rows)):
        raise ValueError("Synthetic adapter partitions must cover every row exactly once.")


def _validate_gate_params(
    *,
    sentences: int,
    channels: int,
    letter_classes: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    hidden_channels: int,
    num_threads: int,
    min_validation_cer_gain: float,
    bootstrap_iterations: int,
    max_output_mb: float,
) -> None:
    if sentences < 24:
        raise ValueError("sentences must be >= 24 for train/validation/test partitions")
    if channels < letter_classes + 1:
        raise ValueError("channels must provide one motif channel per letter plus space")
    if epochs < 1 or batch_size < 1 or hidden_channels < 1:
        raise ValueError("epochs, batch_size, and hidden_channels must be >= 1")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be > 0")
    if num_threads != 1:
        raise ValueError("synthetic adapter gate requires num_threads=1")
    if min_validation_cer_gain < 0:
        raise ValueError("min_validation_cer_gain must be >= 0")
    if bootstrap_iterations < 100:
        raise ValueError("bootstrap_iterations must be >= 100")
    if max_output_mb <= 0:
        raise ValueError("max_output_mb must be > 0")


def _write_artifacts(
    report: dict[str, Any],
    *,
    artifacts: dict[str, Path],
    prediction_texts: dict[str, str],
    max_output_bytes: int,
) -> None:
    prediction_bytes = sum(len(value.encode("utf-8")) for value in prediction_texts.values())
    for _ in range(4):
        json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        markdown_text = render_synthetic_adapter_gate_markdown(report)
        resources = report["resources"]
        resources["report_json_bytes"] = len(json_text.encode("utf-8"))
        resources["report_markdown_bytes"] = len(markdown_text.encode("utf-8"))
        resources["prediction_bytes"] = prediction_bytes
        resources["total_artifact_bytes"] = (
            resources["report_json_bytes"]
            + resources["report_markdown_bytes"]
            + prediction_bytes
        )
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    markdown_text = render_synthetic_adapter_gate_markdown(report)
    total_bytes = len(json_text.encode("utf-8")) + len(markdown_text.encode("utf-8")) + prediction_bytes
    if total_bytes > max_output_bytes:
        raise ValueError(
            "Synthetic adapter artifacts exceed max_output_mb: "
            f"{total_bytes} > {max_output_bytes} bytes."
        )
    artifacts["report_json"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report_json"].write_text(json_text, encoding="utf-8")
    artifacts["report_markdown"].write_text(markdown_text, encoding="utf-8")
    for key, text in prediction_texts.items():
        artifacts[key].write_text(text, encoding="utf-8")


def _text_rows(values: Iterable[str]) -> str:
    return "".join(f"{value}\n" for value in values)


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
        raise RuntimeError("Synthetic adapter gate requires NumPy: `pip install numpy`.") from exc
    return np
