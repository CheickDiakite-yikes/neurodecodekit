"""Optional CPU-safe CTC baseline over continuous sentence signals."""

from __future__ import annotations

import hashlib
import math
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from neurodecodekit.evaluation.metrics import character_error_rate
from neurodecodekit.preprocess.ctc_text import CTC_VOCAB, greedy_decode_ctc_ids


ML_INSTALL_HINT = "pip install -e '.[ml]'"


@dataclass(frozen=True)
class TinyCTCResult:
    """Predictions, split evidence, and resource metrics for the tiny CTC run."""

    predictions: list[str]
    targets: list[str]
    train_predictions: list[str]
    train_targets: list[str]
    strategy: str
    model_name: str
    split_mode: str
    seed: int
    train_fraction: float
    train_indices: list[int]
    eval_indices: list[int]
    validation_indices: list[int]
    test_indices: list[int]
    eval_partition: str
    split_protocol_config_sha256: str | None
    group_assignment_sha256: str | None
    semantic_membership_sha256: str | None
    n_train_rows: int
    n_eval_rows: int
    n_channels: int
    n_classes: int
    parameter_count: int
    parameter_bytes_float32: int
    epochs: int
    batch_size: int
    learning_rate: float
    hidden_channels: int
    device: str
    num_threads: int
    max_restarts: int
    restart_count: int
    selected_initialization_seed: int
    restart_summaries: list[dict[str, object]]
    output_stride: int
    causal: bool
    loss_history: list[float]
    train_cer: float
    eval_cer: float
    eval_blank_fraction: float
    runtime_sec: float
    peak_rss_bytes: int | None
    warnings: list[str]

    def metadata(self) -> dict[str, object]:
        payload = asdict(self)
        for key in ("predictions", "targets", "train_predictions", "train_targets"):
            payload.pop(key)
        payload.update(
            {
                "kind": "tiny-ctc-sentence",
                "description": (
                    "Optional tiny temporal ConvNet trained with PyTorch CTCLoss over padded "
                    "continuous sentence signals."
                ),
                "uses_neural_windows": True,
                "uses_continuous_sentence_signals": True,
                "uses_deep_learning": True,
                "optional_dependency_extra": "ml",
            }
        )
        return payload


@dataclass(frozen=True)
class CrossSessionTinyCTCResult:
    """Tiny CTC result trained and evaluated on separate session arrays."""

    predictions: list[str]
    targets: list[str]
    train_predictions: list[str]
    train_targets: list[str]
    strategy: str
    model_name: str
    split_mode: str
    seed: int
    train_indices: list[int]
    reserved_validation_indices: list[int]
    reserved_test_indices: list[int]
    eval_indices: list[int]
    split_protocol_config_sha256: str | None
    group_assignment_sha256: str | None
    semantic_membership_sha256: str | None
    n_source_rows: int
    n_train_rows: int
    n_reserved_validation_rows: int
    n_reserved_test_rows: int
    n_eval_rows: int
    n_channels: int
    n_classes: int
    parameter_count: int
    parameter_bytes_float32: int
    epochs: int
    batch_size: int
    learning_rate: float
    hidden_channels: int
    device: str
    num_threads: int
    max_restarts: int
    restart_count: int
    selected_initialization_seed: int
    restart_summaries: list[dict[str, object]]
    output_stride: int
    causal: bool
    loss_history: list[float]
    train_cer: float
    eval_cer: float
    eval_blank_fraction: float
    runtime_sec: float
    peak_rss_bytes: int | None
    warnings: list[str]

    def metadata(self) -> dict[str, object]:
        payload = asdict(self)
        for key in ("predictions", "targets", "train_predictions", "train_targets"):
            payload.pop(key)
        payload.update(
            {
                "kind": "tiny-ctc-cross-session",
                "description": (
                    "Tiny temporal ConvNet trained on one session's strict train rows and "
                    "evaluated on a separate session cache."
                ),
                "uses_neural_windows": True,
                "uses_continuous_sentence_signals": True,
                "uses_deep_learning": True,
                "optional_dependency_extra": "ml",
            }
        )
        return payload


@dataclass(frozen=True)
class CrossSessionTinyCTCMultiViewResult:
    """One source-trained tiny CTC evaluated on multiple target signal views."""

    predictions_by_view: dict[str, list[str]]
    targets: list[str]
    train_predictions: list[str]
    train_targets: list[str]
    strategy: str
    model_name: str
    split_mode: str
    seed: int
    train_indices: list[int]
    reserved_validation_indices: list[int]
    reserved_test_indices: list[int]
    eval_indices: list[int]
    split_protocol_config_sha256: str | None
    group_assignment_sha256: str | None
    semantic_membership_sha256: str | None
    n_source_rows: int
    n_train_rows: int
    n_reserved_validation_rows: int
    n_reserved_test_rows: int
    n_eval_rows: int
    n_eval_views: int
    n_channels: int
    n_classes: int
    parameter_count: int
    parameter_bytes_float32: int
    epochs: int
    batch_size: int
    learning_rate: float
    hidden_channels: int
    device: str
    num_threads: int
    max_restarts: int
    restart_count: int
    selected_initialization_seed: int
    restart_summaries: list[dict[str, object]]
    output_stride: int
    causal: bool
    loss_history: list[float]
    train_cer: float
    eval_cer_by_view: dict[str, float]
    eval_blank_fraction_by_view: dict[str, float]
    runtime_sec: float
    peak_rss_bytes: int | None
    warnings: list[str]

    def metadata(self) -> dict[str, object]:
        payload = asdict(self)
        for key in (
            "predictions_by_view",
            "targets",
            "train_predictions",
            "train_targets",
        ):
            payload.pop(key)
        payload.update(
            {
                "kind": "tiny-ctc-cross-session-multi-view",
                "description": (
                    "One tiny temporal ConvNet fitted on source train rows and reused "
                    "without mutation across multiple target-domain signal views."
                ),
                "uses_neural_windows": True,
                "uses_continuous_sentence_signals": True,
                "uses_deep_learning": True,
                "optional_dependency_extra": "ml",
            }
        )
        return payload


def deterministic_text_holdout_indices(
    texts: Iterable[str],
    *,
    train_fraction: float = 0.8,
) -> tuple[list[int], list[int]]:
    """Split by unique text hash so the same sentence cannot leak across sets."""

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    rows = [str(text) for text in texts]
    unique = sorted(set(rows), key=lambda text: (_stable_text_hash(text), text))
    if len(unique) < 2:
        raise ValueError("CTC text-hash holdout requires at least two unique sentence texts.")
    n_train_texts = int(round(len(unique) * train_fraction))
    n_train_texts = min(max(1, n_train_texts), len(unique) - 1)
    train_texts = set(unique[:n_train_texts])
    train = [index for index, text in enumerate(rows) if text in train_texts]
    eval_ = [index for index, text in enumerate(rows) if text not in train_texts]
    if not train or not eval_:
        raise ValueError("CTC text-hash holdout produced an empty train or eval split.")
    return train, eval_


def greedy_decode_token_rows(token_rows, input_lengths: Iterable[int]) -> list[str]:
    """Decode already-argmaxed token rows with each row's valid length."""

    lengths = [int(value) for value in input_lengths]
    if len(token_rows) != len(lengths):
        raise ValueError("token rows and input lengths must have the same row count")
    return [greedy_decode_ctc_ids(row[:length]) for row, length in zip(token_rows, lengths)]


def run_tiny_ctc_baseline_from_cache(
    cache,
    *,
    train_fraction: float = 0.8,
    seed: int = 7,
    epochs: int = 60,
    batch_size: int = 16,
    learning_rate: float = 0.02,
    hidden_channels: int = 16,
    device: str = "cpu",
    num_threads: int = 1,
    max_restarts: int = 3,
    partition_indices: Mapping[str, Iterable[int]] | None = None,
    eval_partition: str = "test",
    split_metadata: Mapping[str, Any] | None = None,
) -> TinyCTCResult:
    """Train and evaluate from a validated LoadedSentenceCache."""

    return run_tiny_ctc_baseline(
        signals=cache.signals,
        input_lengths=cache.input_lengths,
        target_token_ids=cache.target_token_ids,
        target_lengths=cache.target_lengths,
        target_texts=cache.target_texts.tolist(),
        train_fraction=train_fraction,
        seed=seed,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        device=device,
        num_threads=num_threads,
        max_restarts=max_restarts,
        partition_indices=partition_indices,
        eval_partition=eval_partition,
        split_metadata=split_metadata,
    )


def run_tiny_ctc_cross_session_views(
    *,
    train_signals,
    train_input_lengths,
    train_target_token_ids,
    train_target_lengths,
    train_target_texts: Iterable[str],
    eval_signal_views: Mapping[str, Any],
    eval_input_lengths,
    eval_target_token_ids,
    eval_target_lengths,
    eval_target_texts: Iterable[str],
    source_partitions: Mapping[str, Iterable[int]],
    split_metadata: Mapping[str, Any] | None = None,
    seed: int = 7,
    epochs: int = 60,
    batch_size: int = 16,
    learning_rate: float = 0.02,
    hidden_channels: int = 16,
    device: str = "cpu",
    num_threads: int = 1,
    max_restarts: int = 1,
) -> CrossSessionTinyCTCMultiViewResult:
    """Fit once on source train rows and evaluate immutable target signal views."""

    _validate_training_params(
        train_fraction=None,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        num_threads=num_threads,
        max_restarts=max_restarts,
    )
    np, torch = _require_ml_dependencies()
    train_x = np.asarray(train_signals, dtype="float32")
    train_x_lengths = np.asarray(train_input_lengths, dtype="int64")
    train_y = np.asarray(train_target_token_ids, dtype="int64")
    train_y_lengths = np.asarray(train_target_lengths, dtype="int64")
    train_texts = [str(value) for value in train_target_texts]
    if not eval_signal_views:
        raise ValueError("eval_signal_views must contain at least one named view")
    eval_views = {
        str(name): np.asarray(values, dtype="float32")
        for name, values in eval_signal_views.items()
    }
    if any(not name for name in eval_views):
        raise ValueError("eval signal view names must be non-empty")
    eval_x_lengths = np.asarray(eval_input_lengths, dtype="int64")
    eval_y = np.asarray(eval_target_token_ids, dtype="int64")
    eval_y_lengths = np.asarray(eval_target_lengths, dtype="int64")
    eval_texts = [str(value) for value in eval_target_texts]
    _validate_arrays(
        train_x,
        train_x_lengths,
        train_y,
        train_y_lengths,
        train_texts,
    )
    for name, eval_x in eval_views.items():
        _validate_arrays(eval_x, eval_x_lengths, eval_y, eval_y_lengths, eval_texts)
        if train_x.shape[1] != eval_x.shape[1]:
            raise ValueError(
                "Cross-session train and evaluation caches must have equal channels; "
                f"view {name!r} has {eval_x.shape[1]} vs {train_x.shape[1]}."
            )

    normalized = _normalize_partition_indices(
        source_partitions,
        n_rows=len(train_texts),
        eval_partition="test",
    )
    train_indices = normalized["train"]
    validation_indices = normalized.get("val", [])
    test_indices = normalized["test"]
    eval_indices = list(range(len(eval_texts)))

    started_at = time.perf_counter()
    torch.set_num_threads(num_threads)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
    torch_device = _resolve_device(torch, device)
    train_targets = [train_texts[index] for index in train_indices]
    candidates = []
    restart_summaries: list[dict[str, object]] = []
    for restart_index in range(max_restarts):
        initialization_seed = seed + restart_index * 1009
        torch.manual_seed(initialization_seed)
        np.random.seed(initialization_seed)
        model = _build_model(
            torch,
            in_channels=int(train_x.shape[1]),
            hidden_channels=hidden_channels,
            n_classes=len(CTC_VOCAB),
        ).to(torch_device)
        loss_history = _train_model(
            np,
            torch,
            model,
            signals=train_x,
            input_lengths=train_x_lengths,
            target_token_ids=train_y,
            target_lengths=train_y_lengths,
            train_indices=train_indices,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            device=torch_device,
            seed=initialization_seed,
        )
        train_predictions, train_blank_fraction = _predict(
            torch,
            model,
            train_x,
            train_x_lengths,
            train_indices,
            batch_size=batch_size,
            device=torch_device,
        )
        train_cer = _mean_cer(train_targets, train_predictions)
        restart_summaries.append(
            {
                "restart_index": restart_index,
                "initialization_seed": initialization_seed,
                "train_cer": train_cer,
                "train_blank_fraction": train_blank_fraction,
                "final_loss": loss_history[-1],
            }
        )
        candidates.append(
            (
                train_cer,
                loss_history[-1],
                initialization_seed,
                model,
                loss_history,
                train_predictions,
            )
        )
        if train_cer <= 0.05:
            break

    (
        selected_train_cer,
        _selected_final_loss,
        selected_initialization_seed,
        model,
        loss_history,
        train_predictions,
    ) = min(candidates, key=lambda item: (item[0], item[1], item[2]))
    predictions_by_view: dict[str, list[str]] = {}
    blank_fraction_by_view: dict[str, float] = {}
    for name, eval_x in eval_views.items():
        predictions, blank_fraction = _predict(
            torch,
            model,
            eval_x,
            eval_x_lengths,
            eval_indices,
            batch_size=batch_size,
            device=torch_device,
        )
        predictions_by_view[name] = predictions
        blank_fraction_by_view[name] = blank_fraction
    parameter_count = sum(int(parameter.numel()) for parameter in model.parameters())
    split_values = dict(split_metadata or {})
    return CrossSessionTinyCTCMultiViewResult(
        predictions_by_view=predictions_by_view,
        targets=eval_texts,
        train_predictions=train_predictions,
        train_targets=train_targets,
        strategy="character-ctc",
        model_name="TinySentenceCTC",
        split_mode="strict-source-train-to-independent-session-eval",
        seed=seed,
        train_indices=train_indices,
        reserved_validation_indices=validation_indices,
        reserved_test_indices=test_indices,
        eval_indices=eval_indices,
        split_protocol_config_sha256=split_values.get("protocol_config_sha256"),
        group_assignment_sha256=split_values.get("group_assignment_sha256"),
        semantic_membership_sha256=split_values.get("semantic_membership_sha256"),
        n_source_rows=len(train_texts),
        n_train_rows=len(train_indices),
        n_reserved_validation_rows=len(validation_indices),
        n_reserved_test_rows=len(test_indices),
        n_eval_rows=len(eval_indices),
        n_eval_views=len(eval_views),
        n_channels=int(train_x.shape[1]),
        n_classes=len(CTC_VOCAB),
        parameter_count=parameter_count,
        parameter_bytes_float32=parameter_count * 4,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        device=str(torch_device),
        num_threads=num_threads,
        max_restarts=max_restarts,
        restart_count=len(restart_summaries),
        selected_initialization_seed=selected_initialization_seed,
        restart_summaries=restart_summaries,
        output_stride=1,
        causal=False,
        loss_history=[round(value, 8) for value in loss_history],
        train_cer=selected_train_cer,
        eval_cer_by_view={
            name: _mean_cer(eval_texts, predictions)
            for name, predictions in predictions_by_view.items()
        },
        eval_blank_fraction_by_view=blank_fraction_by_view,
        runtime_sec=round(time.perf_counter() - started_at, 6),
        peak_rss_bytes=_peak_rss_bytes(),
        warnings=[
            "tiny_ctc_trained_on_source_session_train_rows_only",
            "source_validation_rows_reserved_and_unused",
            "source_test_rows_reserved_and_unused",
            "independent_session_rows_used_only_for_final_evaluation",
            "tiny_ctc_model_is_noncausal",
            "tiny_ctc_no_checkpoint_saved",
            "same_subject_cross_session_is_not_subject_generalization",
            "multiple_target_views_share_one_frozen_source_trained_model",
            *(
                ["tiny_ctc_restarted_after_degenerate_training_fit"]
                if len(restart_summaries) > 1
                else []
            ),
        ],
    )


def run_tiny_ctc_cross_session(
    *,
    train_signals,
    train_input_lengths,
    train_target_token_ids,
    train_target_lengths,
    train_target_texts: Iterable[str],
    eval_signals,
    eval_input_lengths,
    eval_target_token_ids,
    eval_target_lengths,
    eval_target_texts: Iterable[str],
    source_partitions: Mapping[str, Iterable[int]],
    split_metadata: Mapping[str, Any] | None = None,
    seed: int = 7,
    epochs: int = 60,
    batch_size: int = 16,
    learning_rate: float = 0.02,
    hidden_channels: int = 16,
    device: str = "cpu",
    num_threads: int = 1,
    max_restarts: int = 1,
) -> CrossSessionTinyCTCResult:
    """Train on strict source rows and evaluate one separate session."""

    result = run_tiny_ctc_cross_session_views(
        train_signals=train_signals,
        train_input_lengths=train_input_lengths,
        train_target_token_ids=train_target_token_ids,
        train_target_lengths=train_target_lengths,
        train_target_texts=train_target_texts,
        eval_signal_views={"eval": eval_signals},
        eval_input_lengths=eval_input_lengths,
        eval_target_token_ids=eval_target_token_ids,
        eval_target_lengths=eval_target_lengths,
        eval_target_texts=eval_target_texts,
        source_partitions=source_partitions,
        split_metadata=split_metadata,
        seed=seed,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        device=device,
        num_threads=num_threads,
        max_restarts=max_restarts,
    )
    multi_view_warning = "multiple_target_views_share_one_frozen_source_trained_model"
    return CrossSessionTinyCTCResult(
        predictions=result.predictions_by_view["eval"],
        targets=result.targets,
        train_predictions=result.train_predictions,
        train_targets=result.train_targets,
        strategy=result.strategy,
        model_name=result.model_name,
        split_mode=result.split_mode,
        seed=result.seed,
        train_indices=result.train_indices,
        reserved_validation_indices=result.reserved_validation_indices,
        reserved_test_indices=result.reserved_test_indices,
        eval_indices=result.eval_indices,
        split_protocol_config_sha256=result.split_protocol_config_sha256,
        group_assignment_sha256=result.group_assignment_sha256,
        semantic_membership_sha256=result.semantic_membership_sha256,
        n_source_rows=result.n_source_rows,
        n_train_rows=result.n_train_rows,
        n_reserved_validation_rows=result.n_reserved_validation_rows,
        n_reserved_test_rows=result.n_reserved_test_rows,
        n_eval_rows=result.n_eval_rows,
        n_channels=result.n_channels,
        n_classes=result.n_classes,
        parameter_count=result.parameter_count,
        parameter_bytes_float32=result.parameter_bytes_float32,
        epochs=result.epochs,
        batch_size=result.batch_size,
        learning_rate=result.learning_rate,
        hidden_channels=result.hidden_channels,
        device=result.device,
        num_threads=result.num_threads,
        max_restarts=result.max_restarts,
        restart_count=result.restart_count,
        selected_initialization_seed=result.selected_initialization_seed,
        restart_summaries=result.restart_summaries,
        output_stride=result.output_stride,
        causal=result.causal,
        loss_history=result.loss_history,
        train_cer=result.train_cer,
        eval_cer=result.eval_cer_by_view["eval"],
        eval_blank_fraction=result.eval_blank_fraction_by_view["eval"],
        runtime_sec=result.runtime_sec,
        peak_rss_bytes=result.peak_rss_bytes,
        warnings=[warning for warning in result.warnings if warning != multi_view_warning],
    )


def run_tiny_ctc_baseline(
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    target_texts: Iterable[str],
    train_fraction: float = 0.8,
    seed: int = 7,
    epochs: int = 60,
    batch_size: int = 16,
    learning_rate: float = 0.02,
    hidden_channels: int = 16,
    device: str = "cpu",
    num_threads: int = 1,
    max_restarts: int = 3,
    partition_indices: Mapping[str, Iterable[int]] | None = None,
    eval_partition: str = "test",
    split_metadata: Mapping[str, Any] | None = None,
) -> TinyCTCResult:
    """Run a tiny stride-one temporal CTC model with explicit resource caps."""

    _validate_training_params(
        train_fraction=train_fraction,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        num_threads=num_threads,
        max_restarts=max_restarts,
    )
    np, torch = _require_ml_dependencies()
    x = np.asarray(signals, dtype="float32")
    x_lengths = np.asarray(input_lengths, dtype="int64")
    y = np.asarray(target_token_ids, dtype="int64")
    y_lengths = np.asarray(target_lengths, dtype="int64")
    texts = [str(value) for value in target_texts]
    _validate_arrays(x, x_lengths, y, y_lengths, texts)
    if partition_indices is None:
        train_indices, eval_indices = deterministic_text_holdout_indices(
            texts,
            train_fraction=train_fraction,
        )
        validation_indices: list[int] = []
        test_indices = list(eval_indices)
        effective_eval_partition = "eval"
        split_mode = "single-cache-deterministic-text-hash-holdout"
        split_values: dict[str, Any] = {}
    else:
        normalized_partitions = _normalize_partition_indices(
            partition_indices,
            n_rows=len(texts),
            eval_partition=eval_partition,
        )
        train_indices = normalized_partitions["train"]
        eval_indices = normalized_partitions[eval_partition]
        validation_indices = normalized_partitions.get("val", [])
        test_indices = normalized_partitions.get("test", [])
        effective_eval_partition = eval_partition
        split_mode = "split-protocol-v1-explicit-membership"
        split_values = dict(split_metadata or {})

    started_at = time.perf_counter()
    torch.set_num_threads(num_threads)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
    torch_device = _resolve_device(torch, device)
    train_targets = [texts[index] for index in train_indices]
    candidates = []
    restart_summaries: list[dict[str, object]] = []
    for restart_index in range(max_restarts):
        initialization_seed = seed + restart_index * 1009
        torch.manual_seed(initialization_seed)
        np.random.seed(initialization_seed)
        model = _build_model(
            torch,
            in_channels=int(x.shape[1]),
            hidden_channels=hidden_channels,
            n_classes=len(CTC_VOCAB),
        ).to(torch_device)
        loss_history = _train_model(
            np,
            torch,
            model,
            signals=x,
            input_lengths=x_lengths,
            target_token_ids=y,
            target_lengths=y_lengths,
            train_indices=train_indices,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            device=torch_device,
            seed=initialization_seed,
        )
        train_predictions, train_blank_fraction = _predict(
            torch,
            model,
            x,
            x_lengths,
            train_indices,
            batch_size=batch_size,
            device=torch_device,
        )
        train_cer = _mean_cer(train_targets, train_predictions)
        restart_summaries.append(
            {
                "restart_index": restart_index,
                "initialization_seed": initialization_seed,
                "train_cer": train_cer,
                "train_blank_fraction": train_blank_fraction,
                "final_loss": loss_history[-1],
            }
        )
        candidates.append(
            (
                train_cer,
                loss_history[-1],
                initialization_seed,
                model,
                loss_history,
                train_predictions,
            )
        )
        if train_cer <= 0.05:
            break

    (
        selected_train_cer,
        _selected_final_loss,
        selected_initialization_seed,
        model,
        loss_history,
        train_predictions,
    ) = min(candidates, key=lambda item: (item[0], item[1], item[2]))
    predictions, eval_blank_fraction = _predict(
        torch,
        model,
        x,
        x_lengths,
        eval_indices,
        batch_size=batch_size,
        device=torch_device,
    )
    eval_targets = [texts[index] for index in eval_indices]
    parameter_count = sum(int(parameter.numel()) for parameter in model.parameters())
    runtime_sec = round(time.perf_counter() - started_at, 6)
    return TinyCTCResult(
        predictions=predictions,
        targets=eval_targets,
        train_predictions=train_predictions,
        train_targets=train_targets,
        strategy="character-ctc",
        model_name="TinySentenceCTC",
        split_mode=split_mode,
        seed=seed,
        train_fraction=len(train_indices) / len(texts),
        train_indices=train_indices,
        eval_indices=eval_indices,
        validation_indices=validation_indices,
        test_indices=test_indices,
        eval_partition=effective_eval_partition,
        split_protocol_config_sha256=split_values.get("protocol_config_sha256"),
        group_assignment_sha256=split_values.get("group_assignment_sha256"),
        semantic_membership_sha256=split_values.get("semantic_membership_sha256"),
        n_train_rows=len(train_indices),
        n_eval_rows=len(eval_indices),
        n_channels=int(x.shape[1]),
        n_classes=len(CTC_VOCAB),
        parameter_count=parameter_count,
        parameter_bytes_float32=parameter_count * 4,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        device=str(torch_device),
        num_threads=num_threads,
        max_restarts=max_restarts,
        restart_count=len(restart_summaries),
        selected_initialization_seed=selected_initialization_seed,
        restart_summaries=restart_summaries,
        output_stride=1,
        causal=False,
        loss_history=[round(value, 8) for value in loss_history],
        train_cer=selected_train_cer,
        eval_cer=_mean_cer(eval_targets, predictions),
        eval_blank_fraction=eval_blank_fraction,
        runtime_sec=runtime_sec,
        peak_rss_bytes=_peak_rss_bytes(),
        warnings=[
            "tiny_ctc_uses_continuous_sentence_signals",
            (
                "tiny_ctc_split_protocol_v1_explicit_membership"
                if partition_indices is not None
                else "tiny_ctc_single_cache_text_hash_holdout"
            ),
            "tiny_ctc_model_is_noncausal",
            "tiny_ctc_no_checkpoint_saved",
            "tiny_ctc_result_requires_dataset_specific_claim_boundary",
            *(
                ["validation_partition_reserved_not_used_for_model_selection"]
                if partition_indices is not None and validation_indices
                else []
            ),
            *(
                ["tiny_ctc_restarted_after_degenerate_training_fit"]
                if len(restart_summaries) > 1
                else []
            ),
        ],
    )


def _train_model(
    np,
    torch,
    model,
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    train_indices,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device,
    seed: int,
) -> list[float]:
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=True)
    rng = np.random.default_rng(seed)
    loss_history: list[float] = []
    model.train()
    for _epoch in range(epochs):
        order = np.asarray(train_indices, dtype="int64")
        rng.shuffle(order)
        epoch_loss = 0.0
        seen = 0
        for start in range(0, len(order), batch_size):
            batch_indices = order[start : start + batch_size]
            xb = torch.from_numpy(signals[batch_indices]).to(device)
            input_len = torch.from_numpy(input_lengths[batch_indices]).to(device)
            targets = torch.from_numpy(target_token_ids[batch_indices]).to(device)
            target_len = torch.from_numpy(target_lengths[batch_indices]).to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(xb)
            log_probs = logits.log_softmax(dim=2).permute(1, 0, 2)
            loss = criterion(log_probs, targets, input_len, target_len)
            if not torch.isfinite(loss):
                raise RuntimeError("Tiny CTC training produced a non-finite loss.")
            loss.backward()
            optimizer.step()
            count = int(len(batch_indices))
            epoch_loss += float(loss.detach().cpu()) * count
            seen += count
        loss_history.append(epoch_loss / max(1, seen))
    return loss_history


def _build_model(torch, *, in_channels: int, hidden_channels: int, n_classes: int):
    class TinySentenceCTC(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.network = torch.nn.Sequential(
                torch.nn.Conv1d(in_channels, hidden_channels, kernel_size=1),
                torch.nn.GELU(),
                torch.nn.Conv1d(
                    hidden_channels,
                    hidden_channels,
                    kernel_size=3,
                    padding=1,
                ),
                torch.nn.GELU(),
                torch.nn.Conv1d(hidden_channels, n_classes, kernel_size=1),
            )

        def forward(self, value):
            return self.network(value).transpose(1, 2)

    return TinySentenceCTC()


def _predict(torch, model, signals, input_lengths, indices, *, batch_size: int, device):
    model.eval()
    predictions: list[str] = []
    blank_count = 0
    valid_count = 0
    with torch.no_grad():
        for start in range(0, len(indices), batch_size):
            batch_indices = indices[start : start + batch_size]
            xb = torch.from_numpy(signals[batch_indices]).to(device)
            token_rows = model(xb).argmax(dim=2).cpu().numpy()
            lengths = input_lengths[batch_indices].tolist()
            predictions.extend(greedy_decode_token_rows(token_rows, lengths))
            for row, length in zip(token_rows, lengths):
                blank_count += int((row[: int(length)] == 0).sum())
                valid_count += int(length)
    return predictions, blank_count / valid_count if valid_count else 0.0


def _validate_training_params(
    *,
    train_fraction: float | None,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    hidden_channels: int,
    num_threads: int,
    max_restarts: int,
) -> None:
    if train_fraction is not None and not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    if epochs < 1:
        raise ValueError("epochs must be >= 1")
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be > 0")
    if hidden_channels < 1:
        raise ValueError("hidden_channels must be >= 1")
    if num_threads < 1:
        raise ValueError("num_threads must be >= 1")
    if max_restarts < 1 or max_restarts > 10:
        raise ValueError("max_restarts must be between 1 and 10")


def _normalize_partition_indices(
    partition_indices: Mapping[str, Iterable[int]],
    *,
    n_rows: int,
    eval_partition: str,
) -> dict[str, list[int]]:
    normalized = {
        str(name): sorted(int(value) for value in values)
        for name, values in partition_indices.items()
    }
    if "train" not in normalized:
        raise ValueError("explicit CTC partitions require a train partition")
    if eval_partition == "train" or eval_partition not in normalized:
        raise ValueError("eval_partition must name a non-train explicit partition")
    if not normalized["train"] or not normalized[eval_partition]:
        raise ValueError("explicit train and evaluation partitions must be non-empty")
    seen: set[int] = set()
    for name, indices in normalized.items():
        if len(indices) != len(set(indices)):
            raise ValueError(f"explicit partition {name!r} repeats a row index")
        if any(index < 0 or index >= n_rows for index in indices):
            raise ValueError(f"explicit partition {name!r} contains an invalid row index")
        overlap = seen & set(indices)
        if overlap:
            raise ValueError(f"explicit CTC partitions overlap at rows {sorted(overlap)}")
        seen.update(indices)
    if seen != set(range(n_rows)):
        raise ValueError("explicit CTC partitions must cover every sentence row exactly once")
    return normalized


def _validate_arrays(signals, input_lengths, target_ids, target_lengths, texts) -> None:
    if signals.ndim != 3:
        raise ValueError(f"signals must be [sentences, channels, timepoints], got {signals.shape}")
    n_rows = signals.shape[0]
    if any(len(value) != n_rows for value in (input_lengths, target_ids, target_lengths, texts)):
        raise ValueError("sentence CTC arrays must have matching row counts")
    if target_ids.ndim != 2:
        raise ValueError("target_token_ids must be rank 2")
    if (input_lengths > signals.shape[2]).any() or (input_lengths < 1).any():
        raise ValueError("input_lengths are outside the signal width")
    if (target_lengths > target_ids.shape[1]).any() or (target_lengths < 1).any():
        raise ValueError("target_lengths are outside the target width")


def _require_ml_dependencies():
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            f"Tiny CTC training requires optional ML dependencies. Install with: {ML_INSTALL_HINT}"
        ) from exc
    return np, torch


def _resolve_device(torch, device: str):
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA was requested but is not available.")
    if device == "mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS was requested but is not available.")
    if device not in {"cpu", "cuda", "mps"}:
        raise ValueError("device must be one of: cpu, cuda, mps")
    return torch.device(device)


def _stable_text_hash(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


def _mean_cer(targets: list[str], predictions: list[str]) -> float:
    values = [
        character_error_rate(target, prediction) for target, prediction in zip(targets, predictions)
    ]
    finite = [value for value in values if math.isfinite(value)]
    return sum(finite) / len(finite) if finite else math.inf


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (ImportError, OSError, ValueError):  # pragma: no cover - platform-dependent
        return None
    return value if sys.platform == "darwin" else value * 1024
