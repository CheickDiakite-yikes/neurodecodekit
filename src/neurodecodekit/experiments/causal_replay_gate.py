"""Synthetic causal chunk/replay audit for the NeuroToken frame producer."""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from neurodecodekit.cache.neurotoken import project_mock_temporal_embeddings
from neurodecodekit.cache.neurotoken_stream import CausalMockNeuroTokenProducer
from neurodecodekit.cache.sentence_npz import validate_sentence_cache_metadata


CAUSAL_REPLAY_SCHEMA_NAME = "b2q-causal-replay-gate"
CAUSAL_REPLAY_SCHEMA_VERSION = 0
PROOF_POSTURE = "synthetic_causal_frame_replay_only_no_decoder"
REGISTERED_SCHEDULES = (
    "single-sample",
    "stride-aligned",
    "kernel-then-stride",
    "jittered",
    "whole-item",
)
THREAD_ENV_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
OFFICIAL_V2_COMMIT = "3bf5a4099ca0d23bbe994b2287905760236e56e0"
OFFICIAL_V2_SOURCE = (
    "https://github.com/facebookresearch/brain2qwerty/tree/"
    f"{OFFICIAL_V2_COMMIT}/brain2qwerty_v2"
)
OFFICIAL_V2_PAPER = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
EMFORMER_SOURCE = (
    "https://ai.meta.com/research/publications/"
    "emformer-efficient-memory-transformer-based-acoustic-model-for-low-latency-"
    "streaming-speech-recognition/"
)
FASTEMIT_SOURCE = (
    "https://research.google/pubs/fastemit-low-latency-streaming-asr-with-"
    "sequence-level-emission-regularization/"
)
SOURCE_MEMBERS_OPENED = (
    "metadata",
    "signals",
    "input_lengths",
    "sentence_start_sec",
)
TARGET_MEMBERS_NOT_OPENED = (
    "target_token_ids",
    "target_lengths",
    "target_texts",
    "reference_texts",
    "mat_response_texts",
)


def run_causal_replay_gate(
    *,
    source_cache_path: str | Path,
    out_json_path: str | Path,
    out_markdown_path: str | Path | None = None,
    source_sampling_rate_hz: float | None = None,
    embedding_dim: int = 32,
    kernel_size: int = 16,
    stride: int = 4,
    seed: int = 23,
    token_dtype: str = "float32",
    compatibility_atol: float = 1e-6,
    max_items: int = 64,
    max_source_mb: float = 4.0,
    max_samples_per_item: int = 128,
    max_chunk_samples: int = 128,
    max_tokens_per_item: int = 128,
    max_total_pushes: int = 100_000,
    max_working_mb: float = 16.0,
    max_state_kib: float = 8.0,
    max_runtime_sec: float = 10.0,
    max_peak_rss_mb: float = 256.0,
    max_report_mb: float = 1.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Run registered chunk schedules against one synthetic signal cache."""

    started_at = time.perf_counter()
    source_path = Path(source_cache_path)
    json_path = Path(out_json_path)
    markdown_path = Path(out_markdown_path) if out_markdown_path else None
    _prepare_outputs([json_path, markdown_path], overwrite=overwrite)
    caps = {
        "max_items": _positive_int(max_items, "max_items"),
        "max_source_bytes": _mb_to_bytes(max_source_mb, "max_source_mb"),
        "max_samples_per_item": _positive_int(
            max_samples_per_item, "max_samples_per_item"
        ),
        "max_chunk_samples": _positive_int(max_chunk_samples, "max_chunk_samples"),
        "max_tokens_per_item": _positive_int(
            max_tokens_per_item, "max_tokens_per_item"
        ),
        "max_total_pushes": _positive_int(max_total_pushes, "max_total_pushes"),
        "max_working_bytes": _mb_to_bytes(max_working_mb, "max_working_mb"),
        "max_state_bytes": _kib_to_bytes(max_state_kib, "max_state_kib"),
        "max_runtime_sec": _positive_finite(max_runtime_sec, "max_runtime_sec"),
        "max_peak_rss_bytes": _mb_to_bytes(max_peak_rss_mb, "max_peak_rss_mb"),
        "max_report_bytes": _mb_to_bytes(max_report_mb, "max_report_mb"),
    }
    tolerance = _positive_finite(compatibility_atol, "compatibility_atol")
    source_bytes = int(source_path.stat().st_size)
    if source_bytes > caps["max_source_bytes"]:
        raise ValueError(
            f"source cache has {source_bytes} bytes, exceeding cap "
            f"{caps['max_source_bytes']}"
        )
    source = _load_synthetic_signal_view(source_path)
    signals = source["signals"]
    input_lengths = source["input_lengths"]
    source_starts = source["sentence_start_sec"]
    metadata = source["metadata"]
    n_items, n_channels, max_timepoints = signals.shape
    if n_items > caps["max_items"]:
        raise ValueError(f"source has {n_items} items, exceeding cap {caps['max_items']}")
    if max_timepoints > caps["max_samples_per_item"]:
        raise ValueError(
            f"source has {max_timepoints} padded samples per item, exceeding cap "
            f"{caps['max_samples_per_item']}"
        )
    if int(input_lengths.max()) > caps["max_chunk_samples"]:
        raise ValueError(
            "whole-item registered schedule would exceed max_chunk_samples; "
            "raise the explicit cap or use a smaller fixture"
        )
    sfreq = _resolve_sampling_rate(metadata, source_sampling_rate_hz)
    producer = CausalMockNeuroTokenProducer(
        n_channels=n_channels,
        source_sampling_rate_hz=sfreq,
        embedding_dim=embedding_dim,
        kernel_size=kernel_size,
        stride=stride,
        seed=seed,
        token_dtype=token_dtype,
    )
    if int(input_lengths.min()) < producer.kernel_size:
        raise ValueError("every source item must contain at least one complete kernel")
    if producer.mutable_state_bound_bytes > caps["max_state_bytes"]:
        raise ValueError(
            f"declared mutable state needs {producer.mutable_state_bound_bytes} bytes, "
            f"exceeding cap {caps['max_state_bytes']}"
        )
    fixed_input_bytes = int(signals.nbytes + producer.fixed_parameter_bytes)
    if fixed_input_bytes > caps["max_working_bytes"]:
        raise ValueError(
            f"signal plus fixed projection arrays need {fixed_input_bytes} bytes, "
            f"exceeding cap {caps['max_working_bytes']}"
        )
    offline = project_mock_temporal_embeddings(
        signals=signals,
        input_lengths=input_lengths,
        source_start_sec=source_starts,
        source_sampling_rate_hz=sfreq,
        embedding_dim=embedding_dim,
        kernel_size=kernel_size,
        stride=stride,
        seed=seed,
        token_dtype=token_dtype,
        max_tokens_per_item=caps["max_tokens_per_item"],
        max_output_mb=max_working_mb,
    )
    working_core_bytes = int(fixed_input_bytes + offline["projected_core_bytes"])
    if working_core_bytes > caps["max_working_bytes"]:
        raise ValueError(
            f"signal, fixed weights, and projected core arrays need "
            f"{working_core_bytes} bytes, exceeding cap {caps['max_working_bytes']}"
        )
    if offline["weights_sha256"] != producer.weights_sha256:
        raise RuntimeError("offline and streaming producers did not share fixed weights")

    schedule_reports = []
    remaining_push_budget = caps["max_total_pushes"]
    for schedule_name in REGISTERED_SCHEDULES:
        schedule = _run_schedule(
            name=schedule_name,
            signals=signals,
            input_lengths=input_lengths,
            source_starts=source_starts,
            offline=offline,
            producer=producer,
            compatibility_atol=tolerance,
            max_chunk_samples=caps["max_chunk_samples"],
            max_samples_per_item=caps["max_samples_per_item"],
            max_tokens_per_item=caps["max_tokens_per_item"],
            push_budget=remaining_push_budget,
        )
        remaining_push_budget -= int(schedule["push_count"])
        schedule_reports.append(schedule)
    canonical_hashes = {
        str(schedule["canonical_stream_payload_sha256"])
        for schedule in schedule_reports
    }
    schedule_invariant_bits = len(canonical_hashes) == 1
    max_state_bytes = max(
        int(schedule["max_mutable_state_bytes"]) for schedule in schedule_reports
    )
    runtime_sec = time.perf_counter() - started_at
    peak_rss_bytes = _peak_rss_bytes()
    resource_gate = (
        runtime_sec <= caps["max_runtime_sec"]
        and (peak_rss_bytes is None or peak_rss_bytes <= caps["max_peak_rss_bytes"])
        and max_state_bytes <= caps["max_state_bytes"]
    )
    replay_gate = all(
        bool(schedule["offline_value_compatibility_passed"])
        and bool(schedule["timestamps_bitwise_equal"])
        and bool(schedule["frame_grid_exact"])
        and bool(schedule["causal_availability_passed"])
        for schedule in schedule_reports
    )
    gate_passed = bool(
        replay_gate
        and schedule_invariant_bits
        and resource_gate
        and producer.producer_right_context_samples == 0
    )
    thread_env = {name: os.environ.get(name) for name in THREAD_ENV_VARS}
    warnings = [
        "synthetic_signal_fixture_only",
        "mock_projection_is_target_free_and_not_learned",
        "canonical_stream_arithmetic_is_bitwise_schedule_invariant",
        "loop20_batched_offline_values_use_declared_float_tolerance",
        "producer_causality_does_not_establish_decoder_causality",
        "no_end_to_end_or_user_perceived_latency_was_measured",
        "whole_item_schedule_is_an_equivalence_stress_not_a_low_latency_mode",
        "not_arbitrary_thought_decoding",
    ]
    if any(value != "1" for value in thread_env.values()):
        warnings.append("one_thread_numeric_environment_not_fully_declared")
    report = {
        "schema": {
            "name": CAUSAL_REPLAY_SCHEMA_NAME,
            "version": CAUSAL_REPLAY_SCHEMA_VERSION,
        },
        "proof_posture": PROOF_POSTURE,
        "gate_passed": gate_passed,
        "decision": (
            "causal_frame_replay_passed_ready_for_learned_encoder_gate"
            if gate_passed
            else "causal_frame_replay_failed_do_not_build_decoder"
        ),
        "source": {
            "path": str(source_path),
            "sha256": _file_sha256(source_path),
            "bytes": source_bytes,
            "kind": str(metadata.get("kind") or ""),
            "shape": [int(value) for value in signals.shape],
            "dtype": str(signals.dtype),
            "items": int(n_items),
            "channels": int(n_channels),
            "total_valid_samples": int(input_lengths.sum()),
            "sampling_rate_hz": sfreq,
            "npz_members_opened": list(SOURCE_MEMBERS_OPENED),
            "target_members_present_but_not_opened": list(TARGET_MEMBERS_NOT_OPENED),
        },
        "protocol": {
            "producer": "mock_temporal_gaussian_projection_stream_v2",
            "source_layout": "items,channels,timepoints",
            "token_layout": "items,time,embedding",
            "embedding_dim": int(embedding_dim),
            "kernel_size_samples": producer.kernel_size,
            "stride_samples": producer.stride,
            "token_dtype": producer.token_dtype,
            "seed": producer.seed,
            "weights_sha256": producer.weights_sha256,
            "asynchronous_input": True,
            "producer_causal": True,
            "producer_right_context_samples": 0,
            "token_timestamp_reference": "frame_end",
            "flush_policy": "drop-incomplete",
            "minimum_frame_availability_sec": producer.minimum_frame_availability_sec,
            "decoder_causality": "unavailable_no_decoder_run",
            "end_to_end_latency_measured": False,
            "offline_v1_compatibility_atol": tolerance,
            "stream_schedule_bitwise_equivalence_required": True,
            "registered_schedules": list(REGISTERED_SCHEDULES),
        },
        "summary": {
            "registered_schedules": len(schedule_reports),
            "schedules_passed": sum(
                bool(schedule["schedule_passed"]) for schedule in schedule_reports
            ),
            "stream_schedule_bits_invariant": schedule_invariant_bits,
            "canonical_stream_payload_sha256": (
                next(iter(canonical_hashes)) if schedule_invariant_bits else None
            ),
            "max_offline_absolute_error": max(
                float(schedule["max_offline_absolute_error"])
                for schedule in schedule_reports
            ),
            "timestamps_bitwise_equal": all(
                bool(schedule["timestamps_bitwise_equal"])
                for schedule in schedule_reports
            ),
            "frame_grid_exact": all(
                bool(schedule["frame_grid_exact"]) for schedule in schedule_reports
            ),
            "producer_right_context_samples": 0,
            "max_mutable_state_bytes": max_state_bytes,
            "mutable_state_bound_bytes": producer.mutable_state_bound_bytes,
            "fixed_parameter_bytes": producer.fixed_parameter_bytes,
            "decoder_runs": 0,
            "model_runs": 0,
            "training_runs": 0,
            "real_data_reads": 0,
            "raw_data_reads": 0,
            "target_array_reads": 0,
            "network_fetches": 0,
            "end_to_end_latency_measured": False,
        },
        "schedules": schedule_reports,
        "resources": {
            "runtime_sec": round(runtime_sec, 6),
            "peak_rss_bytes": peak_rss_bytes,
            "source_signal_bytes": int(signals.nbytes),
            "fixed_parameter_bytes": producer.fixed_parameter_bytes,
            "working_core_bytes_before_temporaries": working_core_bytes,
            "max_mutable_state_bytes": max_state_bytes,
            "total_pushes": caps["max_total_pushes"] - remaining_push_budget,
            "thread_environment": thread_env,
            "caps": caps,
        },
        "research_sources": {
            "official_v2_code": OFFICIAL_V2_SOURCE,
            "official_v2_paper": OFFICIAL_V2_PAPER,
            "bounded_memory_streaming_reference": EMFORMER_SOURCE,
            "emission_latency_reference": FASTEMIT_SOURCE,
        },
        "claim_boundaries": [
            "This proves only a target-free synthetic frame producer contract.",
            "No neural representation was learned or evaluated.",
            "No CTC, language model, beam search, or other decoder ran.",
            "Producer frame availability is not text emission latency.",
            "Compute real-time factor is not user-perceived end-to-end latency.",
            "No real MEG/EEG cache or observed holdout was opened.",
            "No portable sensor, unseen-person, clinical, or arbitrary-thought claim follows.",
        ],
        "warnings": warnings,
        "artifacts": {
            "json_path": str(json_path),
            "markdown_path": str(markdown_path) if markdown_path else None,
            "json_bytes": 0,
        },
    }
    json_text = _stable_report_json(report)
    if len(json_text.encode("utf-8")) > caps["max_report_bytes"]:
        raise ValueError("causal replay JSON report exceeds max_report_mb")
    markdown_text = _report_markdown(report) if markdown_path else None
    if markdown_text and len(markdown_text.encode("utf-8")) > caps["max_report_bytes"]:
        raise ValueError("causal replay Markdown report exceeds max_report_mb")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json_text, encoding="utf-8")
    if markdown_path and markdown_text is not None:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown_text, encoding="utf-8")
    return report


def _run_schedule(
    *,
    name: str,
    signals,
    input_lengths,
    source_starts,
    offline: dict[str, Any],
    producer: CausalMockNeuroTokenProducer,
    compatibility_atol: float,
    max_chunk_samples: int,
    max_samples_per_item: int,
    max_tokens_per_item: int,
    push_budget: int,
) -> dict[str, Any]:
    np = _require_numpy()
    started_at = time.perf_counter()
    item_payloads = []
    compute_ms = []
    delay_samples = []
    chunk_sizes_seen = []
    first_availability_samples = []
    max_abs_error = 0.0
    equal_elements = 0
    total_elements = 0
    timestamp_equal = True
    frame_grid_exact = True
    causal_availability = True
    max_state_bytes = 0
    max_buffered_samples = 0
    unframed_tail_samples = []
    push_count = 0
    total_tokens = 0
    for item_index, length_value in enumerate(input_lengths.tolist()):
        length = int(length_value)
        sizes = _chunk_sizes(
            length,
            name=name,
            kernel_size=producer.kernel_size,
            stride=producer.stride,
        )
        if max(sizes) > max_chunk_samples or length > max_samples_per_item:
            raise ValueError(f"registered schedule {name} exceeded a declared source cap")
        push_count += len(sizes)
        if push_count > push_budget:
            raise ValueError(f"registered schedule {name} exceeded remaining push budget")
        stream = producer.new_stream(
            source_start_sec=float(source_starts[item_index]),
            max_chunk_samples=max_chunk_samples,
            max_total_samples=max_samples_per_item,
            max_total_tokens=max_tokens_per_item,
        )
        batches = []
        offset = 0
        for size in sizes:
            push_started = time.perf_counter()
            batch = stream.push(signals[item_index, :, offset : offset + size])
            compute_ms.append((time.perf_counter() - push_started) * 1000)
            batches.append(batch)
            delay_samples.extend(batch.schedule_delay_samples.tolist())
            chunk_sizes_seen.append(size)
            offset += size
            max_state_bytes = max(max_state_bytes, stream.max_mutable_state_bytes)
            max_buffered_samples = max(
                max_buffered_samples, stream.max_buffered_samples
            )
        flush = stream.flush()
        unframed_tail_samples.append(flush.unframed_tail_samples)
        tokens = np.concatenate([batch.tokens for batch in batches], axis=0)
        starts = np.concatenate(
            [batch.token_start_sec for batch in batches], axis=0
        )
        ends = np.concatenate([batch.token_end_sec for batch in batches], axis=0)
        frame_starts = np.concatenate(
            [batch.frame_start_samples for batch in batches], axis=0
        )
        frame_ends = np.concatenate(
            [batch.frame_end_samples for batch in batches], axis=0
        )
        availability = np.concatenate(
            [batch.availability_samples for batch in batches], axis=0
        )
        count = int(offline["token_lengths"][item_index])
        expected = offline["tokens"][item_index, :count]
        difference = np.abs(tokens.astype("float32") - expected.astype("float32"))
        max_abs_error = max(
            max_abs_error, float(difference.max()) if difference.size else 0.0
        )
        equal_elements += int(np.count_nonzero(tokens == expected))
        total_elements += int(tokens.size)
        timestamp_equal &= bool(
            np.array_equal(starts, offline["token_start_sec"][item_index, :count])
            and np.array_equal(ends, offline["token_end_sec"][item_index, :count])
        )
        expected_frame_starts = np.arange(count, dtype="int64") * producer.stride
        frame_grid_exact &= bool(
            np.array_equal(frame_starts, expected_frame_starts)
            and np.array_equal(
                frame_ends, expected_frame_starts + producer.kernel_size
            )
        )
        causal_availability &= bool((availability >= frame_ends).all())
        if len(availability):
            first_availability_samples.append(int(availability[0]))
        total_tokens += len(tokens)
        item_payloads.append(tokens)
    payload_hash = _canonical_stream_payload_sha256(item_payloads)
    source_duration_sec = float(input_lengths.sum() / producer.source_sampling_rate_hz)
    compute_total_sec = sum(compute_ms) / 1000
    offline_compatible = max_abs_error <= compatibility_atol
    schedule_passed = bool(
        offline_compatible
        and timestamp_equal
        and frame_grid_exact
        and causal_availability
        and max_state_bytes <= producer.mutable_state_bound_bytes
    )
    return {
        "name": name,
        "schedule_passed": schedule_passed,
        "items": int(len(input_lengths)),
        "push_count": push_count,
        "emitted_tokens": total_tokens,
        "canonical_stream_payload_sha256": payload_hash,
        "offline_value_compatibility_passed": offline_compatible,
        "offline_compatibility_atol": compatibility_atol,
        "max_offline_absolute_error": max_abs_error,
        "offline_bitwise_equal_fraction": (
            equal_elements / total_elements if total_elements else 1.0
        ),
        "timestamps_bitwise_equal": timestamp_equal,
        "frame_grid_exact": frame_grid_exact,
        "causal_availability_passed": causal_availability,
        "right_context_samples": 0,
        "chunk_samples": {
            "min": min(chunk_sizes_seen),
            "median": statistics.median(chunk_sizes_seen),
            "max": max(chunk_sizes_seen),
        },
        "schedule_delay_sec": _distribution(
            [value / producer.source_sampling_rate_hz for value in delay_samples]
        ),
        "first_token_availability_from_item_start_sec": _distribution(
            [
                value / producer.source_sampling_rate_hz
                for value in first_availability_samples
            ]
        ),
        "push_compute_ms": _distribution(compute_ms),
        "producer_compute_real_time_factor": (
            compute_total_sec / source_duration_sec if source_duration_sec else None
        ),
        "source_duration_sec": source_duration_sec,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "max_buffered_samples": max_buffered_samples,
        "max_mutable_state_bytes": max_state_bytes,
        "unframed_tail_samples": _distribution(unframed_tail_samples),
    }


def _chunk_sizes(
    total_samples: int,
    *,
    name: str,
    kernel_size: int,
    stride: int,
) -> list[int]:
    if name == "single-sample":
        pattern = [1]
    elif name == "stride-aligned":
        pattern = [stride]
    elif name == "kernel-then-stride":
        first = min(kernel_size, total_samples)
        return [first] + _repeat_pattern(total_samples - first, [stride])
    elif name == "jittered":
        pattern = [1, max(1, kernel_size - 1), stride + 1, max(1, kernel_size // 2), 2 * stride + 1]
    elif name == "whole-item":
        return [total_samples]
    else:
        raise ValueError(f"unknown registered schedule: {name}")
    return _repeat_pattern(total_samples, pattern)


def _repeat_pattern(total_samples: int, pattern: list[int]) -> list[int]:
    sizes = []
    remaining = int(total_samples)
    index = 0
    while remaining:
        size = min(remaining, int(pattern[index % len(pattern)]))
        sizes.append(size)
        remaining -= size
        index += 1
    return sizes


def _load_synthetic_signal_view(path: Path) -> dict[str, Any]:
    np = _require_numpy()
    with np.load(path, allow_pickle=False) as data:
        present = set(data.files)
        missing = sorted(set(SOURCE_MEMBERS_OPENED) - present)
        if missing:
            raise ValueError(f"source cache is missing signal-view members: {missing}")
        missing_targets = sorted(set(TARGET_MEMBERS_NOT_OPENED) - present)
        if missing_targets:
            raise ValueError(
                "source cache is missing expected unopened target members: "
                f"{missing_targets}"
            )
        metadata = _decode_metadata(data["metadata"])
        signals = data["signals"].copy()
        input_lengths = data["input_lengths"].copy()
        sentence_start_sec = data["sentence_start_sec"].copy()
    validate_sentence_cache_metadata(metadata)
    if not str(metadata.get("kind") or "").startswith("synthetic_"):
        raise ValueError("causal replay gate accepts synthetic sentence caches only")
    if (
        signals.ndim != 3
        or min(signals.shape) < 1
        or not np.issubdtype(signals.dtype, np.floating)
    ):
        raise ValueError("signals must be nonempty floating [items,channels,timepoints]")
    if not np.isfinite(signals).all():
        raise ValueError("signals contain non-finite values")
    if input_lengths.shape != (signals.shape[0],):
        raise ValueError("input_lengths must contain one value per source item")
    if not np.issubdtype(input_lengths.dtype, np.integer):
        raise ValueError("input_lengths must use an integer dtype")
    if sentence_start_sec.shape != (signals.shape[0],):
        raise ValueError("sentence_start_sec must contain one value per source item")
    if (input_lengths < 1).any() or (input_lengths > signals.shape[2]).any():
        raise ValueError("input_lengths fall outside the padded signal array")
    if not np.isfinite(sentence_start_sec).all():
        raise ValueError("sentence_start_sec contains non-finite values")
    return {
        "signals": signals,
        "input_lengths": input_lengths.astype("int32", copy=False),
        "sentence_start_sec": sentence_start_sec.astype("float64", copy=False),
        "metadata": metadata,
    }


def _resolve_sampling_rate(metadata: dict[str, Any], explicit: float | None) -> float:
    if explicit is not None:
        return _positive_finite(explicit, "source_sampling_rate_hz")
    if metadata.get("sampling_rate_hz") is not None:
        return _positive_finite(metadata["sampling_rate_hz"], "sampling_rate_hz")
    params = metadata.get("extraction_params") or {}
    return _positive_finite(params.get("sfreq"), "metadata extraction sampling rate")


def _canonical_stream_payload_sha256(item_payloads: list[Any]) -> str:
    digest = hashlib.sha256()
    for index, value in enumerate(item_payloads):
        array = _require_numpy().ascontiguousarray(value)
        digest.update(index.to_bytes(8, "little"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(json.dumps(list(array.shape)).encode("ascii"))
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _distribution(values: list[float | int]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "median": 0.0, "p95": 0.0, "max": 0.0}
    np = _require_numpy()
    array = np.asarray(values, dtype="float64")
    return {
        "min": float(array.min()),
        "median": float(np.median(array)),
        "p95": float(np.percentile(array, 95)),
        "max": float(array.max()),
    }


def _stable_report_json(report: dict[str, Any]) -> str:
    for _ in range(8):
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        size = len(text.encode("utf-8"))
        if report["artifacts"]["json_bytes"] == size:
            return text
        report["artifacts"]["json_bytes"] = size
    raise RuntimeError("causal replay report byte count did not converge")


def _report_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    resources = report["resources"]
    lines = [
        "# Causal NeuroToken Replay Gate",
        "",
        f"- Proof posture: `{report['proof_posture']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        f"- Decision: `{report['decision']}`",
        f"- Source: `{report['source']['path']}`",
        f"- Schedules: {summary['schedules_passed']}/{summary['registered_schedules']} passed",
        f"- Bitwise schedule invariant: `{str(summary['stream_schedule_bits_invariant']).lower()}`",
        f"- Max offline v1 absolute error: {summary['max_offline_absolute_error']:.9g}",
        f"- Right context: {summary['producer_right_context_samples']} samples",
        f"- Mutable state: {summary['max_mutable_state_bytes']} / {summary['mutable_state_bound_bytes']} bytes",
        f"- Runtime: {resources['runtime_sec']:.6f} sec",
        f"- Peak RSS: {resources['peak_rss_bytes']} bytes",
        "",
        "## Schedule Results",
        "",
        "| Schedule | Pushes | Max chunk | Max delay (s) | RTF | Passed |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for schedule in report["schedules"]:
        lines.append(
            "| {name} | {pushes} | {chunk} | {delay:.6f} | {rtf:.6f} | {passed} |".format(
                name=schedule["name"],
                pushes=schedule["push_count"],
                chunk=schedule["chunk_samples"]["max"],
                delay=schedule["schedule_delay_sec"]["max"],
                rtf=schedule["producer_compute_real_time_factor"],
                passed=str(schedule["schedule_passed"]).lower(),
            )
        )
    lines.extend(["", "## Claim Boundaries", ""])
    lines.extend(f"- {value}" for value in report["claim_boundaries"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- `{value}`" for value in report["warnings"])
    return "\n".join(lines) + "\n"


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        raw = value.item() if getattr(value, "shape", None) == () else value.tolist()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        metadata = json.loads(str(raw))
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("source cache metadata is not valid JSON") from exc
    if not isinstance(metadata, dict):
        raise ValueError("source cache metadata must decode to an object")
    return metadata


def _prepare_outputs(paths: list[Path | None], *, overwrite: bool) -> None:
    planned = [path for path in paths if path is not None]
    normalized = [path.expanduser().resolve(strict=False) for path in planned]
    if len(set(normalized)) != len(normalized):
        raise ValueError("causal replay report paths must be distinct")
    for path in planned:
        if path is not None and path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to replace existing report: {path}")


def _positive_int(value: int, name: str) -> int:
    normalized = int(value)
    if normalized < 1:
        raise ValueError(f"{name} must be positive")
    return normalized


def _positive_finite(value: float | None, name: str) -> float:
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be finite and positive") from exc
    if not math.isfinite(normalized) or normalized <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return normalized


def _mb_to_bytes(value: float, name: str) -> int:
    return int(_positive_finite(value, name) * 1024 * 1024)


def _kib_to_bytes(value: float, name: str) -> int:
    return int(_positive_finite(value, name) * 1024)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (AttributeError, ImportError, OSError, ValueError):
        return None
    return value if sys.platform == "darwin" else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Causal replay gate requires NumPy: `pip install numpy`.") from exc
    return np
