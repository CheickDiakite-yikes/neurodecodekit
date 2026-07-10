"""Bounded causal streaming for the target-free NeuroToken mock producer."""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from neurodecodekit.cache.neurotoken import (
    SUPPORTED_TOKEN_DTYPES,
    make_mock_projection_weights,
)


DROP_INCOMPLETE_FLUSH = "drop-incomplete"


class CausalFrameProducer(Protocol):
    """Minimal producer interface consumed by the shared causal window stream."""

    n_channels: int
    source_sampling_rate_hz: float
    embedding_dim: int
    kernel_size: int
    stride: int
    token_dtype: str
    mutable_state_bound_bytes: int

    def project_frame(self, frame) -> Any:
        """Project one flattened complete frame to shape `[1, embedding]`."""


@dataclass(frozen=True)
class StreamingTokenBatch:
    """Tokens emitted by one push and their causal availability metadata."""

    tokens: Any
    frame_start_samples: Any
    frame_end_samples: Any
    availability_samples: Any
    token_start_sec: Any
    token_end_sec: Any
    schedule_delay_samples: Any

    @property
    def n_tokens(self) -> int:
        return int(self.tokens.shape[0])


@dataclass(frozen=True)
class StreamFlushSummary:
    """Final state accounting for the registered drop-incomplete policy."""

    policy: str
    received_samples: int
    emitted_tokens: int
    buffered_samples_before_flush: int
    unframed_tail_samples: int
    mutable_state_bytes_after_flush: int
    stream_closed: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class CausalMockNeuroTokenProducer:
    """Fixed zero-lookahead frame projector shared across independent streams."""

    def __init__(
        self,
        *,
        n_channels: int,
        source_sampling_rate_hz: float,
        embedding_dim: int = 32,
        kernel_size: int = 16,
        stride: int = 4,
        seed: int = 23,
        token_dtype: str = "float32",
    ) -> None:
        if not math.isfinite(source_sampling_rate_hz) or source_sampling_rate_hz <= 0:
            raise ValueError("source_sampling_rate_hz must be finite and positive")
        if kernel_size < 1 or stride < 1 or stride > kernel_size:
            raise ValueError("kernel_size and stride must satisfy 1 <= stride <= kernel_size")
        normalized_dtype = str(token_dtype).strip().lower()
        if normalized_dtype not in SUPPORTED_TOKEN_DTYPES:
            raise ValueError(
                f"token_dtype must be one of: {', '.join(SUPPORTED_TOKEN_DTYPES)}"
            )
        self.n_channels = int(n_channels)
        self.source_sampling_rate_hz = float(source_sampling_rate_hz)
        self.embedding_dim = int(embedding_dim)
        self.kernel_size = int(kernel_size)
        self.stride = int(stride)
        self.seed = int(seed)
        self.token_dtype = normalized_dtype
        self.weights = make_mock_projection_weights(
            n_channels=self.n_channels,
            kernel_size=self.kernel_size,
            embedding_dim=self.embedding_dim,
            seed=self.seed,
        )

    @property
    def weights_sha256(self) -> str:
        return hashlib.sha256(self.weights.tobytes(order="C")).hexdigest()

    @property
    def fixed_parameter_bytes(self) -> int:
        return int(self.weights.nbytes)

    @property
    def mutable_state_bound_bytes(self) -> int:
        return int(self.n_channels * max(0, self.kernel_size - 1) * 4)

    @property
    def producer_right_context_samples(self) -> int:
        return 0

    @property
    def minimum_frame_availability_sec(self) -> float:
        return self.kernel_size / self.source_sampling_rate_hz

    def new_stream(
        self,
        *,
        source_start_sec: float = 0.0,
        max_chunk_samples: int = 4096,
        max_total_samples: int = 65536,
        max_total_tokens: int = 4096,
    ) -> CausalMockNeuroTokenStream:
        return CausalMockNeuroTokenStream(
            self,
            source_start_sec=source_start_sec,
            max_chunk_samples=max_chunk_samples,
            max_total_samples=max_total_samples,
            max_total_tokens=max_total_tokens,
        )

    def project_frame(self, frame):
        """Project one complete frame with canonical one-row arithmetic."""

        np = _require_numpy()
        value = np.asarray(frame, dtype="float32")
        expected = self.n_channels * self.kernel_size
        if value.shape != (expected,):
            raise ValueError(f"frame must be flattened with {expected} values")
        return (value[None, :] @ self.weights).astype(self.token_dtype)


class CausalMockNeuroTokenStream:
    """Producer-neutral incremental stream with sub-kernel overlap state."""

    def __init__(
        self,
        producer: CausalFrameProducer,
        *,
        source_start_sec: float,
        max_chunk_samples: int,
        max_total_samples: int,
        max_total_tokens: int,
    ) -> None:
        if not math.isfinite(source_start_sec):
            raise ValueError("source_start_sec must be finite")
        if min(max_chunk_samples, max_total_samples, max_total_tokens) < 1:
            raise ValueError("stream caps must be positive")
        self.producer = producer
        self.source_start_sec = float(source_start_sec)
        self.max_chunk_samples = int(max_chunk_samples)
        self.max_total_samples = int(max_total_samples)
        self.max_total_tokens = int(max_total_tokens)
        np = _require_numpy()
        self._buffer = np.zeros((producer.n_channels, 0), dtype="float32")
        self._received_samples = 0
        self._emitted_tokens = 0
        self._closed = False
        self._max_buffered_samples = 0
        self._max_mutable_state_bytes = 0

    @property
    def received_samples(self) -> int:
        return self._received_samples

    @property
    def emitted_tokens(self) -> int:
        return self._emitted_tokens

    @property
    def buffered_samples(self) -> int:
        return int(self._buffer.shape[1])

    @property
    def mutable_state_bytes(self) -> int:
        return int(self._buffer.nbytes)

    @property
    def max_buffered_samples(self) -> int:
        return self._max_buffered_samples

    @property
    def max_mutable_state_bytes(self) -> int:
        return self._max_mutable_state_bytes

    @property
    def closed(self) -> bool:
        return self._closed

    def push(self, chunk) -> StreamingTokenBatch:
        """Consume one nonempty `[channels,time]` chunk and emit ready frames."""

        if self._closed:
            raise RuntimeError("stream is already closed")
        np = _require_numpy()
        value = np.asarray(chunk)
        if value.ndim != 2 or value.shape[0] != self.producer.n_channels:
            raise ValueError(
                "chunk must be [channels,time] with exactly "
                f"{self.producer.n_channels} channels"
            )
        if value.shape[1] < 1:
            raise ValueError("chunk must contain at least one sample")
        if value.shape[1] > self.max_chunk_samples:
            raise ValueError(
                f"chunk has {value.shape[1]} samples, exceeding cap "
                f"{self.max_chunk_samples}"
            )
        if not np.issubdtype(value.dtype, np.floating) or not np.isfinite(value).all():
            raise ValueError("chunk must contain finite floating values")
        next_received = self._received_samples + int(value.shape[1])
        if next_received > self.max_total_samples:
            raise ValueError(
                f"stream would reach {next_received} samples, exceeding cap "
                f"{self.max_total_samples}"
            )

        buffer_start_sample = self._received_samples - self.buffered_samples
        expected_start_sample = self._emitted_tokens * self.producer.stride
        if buffer_start_sample != expected_start_sample:
            raise RuntimeError("stream overlap state lost its frame-grid position")
        combined = np.concatenate(
            [self._buffer, value.astype("float32", copy=False)], axis=1
        )
        available = int(combined.shape[1])
        count = (
            1 + (available - self.producer.kernel_size) // self.producer.stride
            if available >= self.producer.kernel_size
            else 0
        )
        if self._emitted_tokens + count > self.max_total_tokens:
            raise ValueError(
                f"stream would emit {self._emitted_tokens + count} tokens, "
                f"exceeding cap {self.max_total_tokens}"
            )

        local_starts = np.arange(count, dtype="int64") * self.producer.stride
        global_starts = local_starts + buffer_start_sample
        global_ends = global_starts + self.producer.kernel_size
        if count:
            frames = np.stack(
                [
                    combined[:, int(start) : int(start) + self.producer.kernel_size]
                    .reshape(-1)
                    for start in local_starts.tolist()
                ]
            ).astype("float32", copy=False)
            # Canonical per-frame arithmetic keeps output bits independent of
            # how many ready frames happen to share a transport chunk.
            projected = [
                np.asarray(self.producer.project_frame(frame)) for frame in frames
            ]
            for value in projected:
                if value.shape != (1, self.producer.embedding_dim):
                    raise RuntimeError(
                        "producer project_frame must return [1, embedding_dim]"
                    )
                if not np.issubdtype(value.dtype, np.floating) or not np.isfinite(
                    value
                ).all():
                    raise RuntimeError("producer project_frame returned invalid values")
            tokens = np.concatenate(projected, axis=0)
            if str(tokens.dtype) != self.producer.token_dtype:
                raise RuntimeError("producer project_frame returned the wrong dtype")
        else:
            tokens = np.zeros(
                (0, self.producer.embedding_dim), dtype=self.producer.token_dtype
            )
        availability_samples = np.full(count, next_received, dtype="int64")
        delay_samples = availability_samples - global_ends
        if count and (delay_samples < 0).any():
            raise RuntimeError("producer emitted a frame before its final sample arrived")
        token_start_sec = self.source_start_sec + (
            global_starts.astype("float64") / self.producer.source_sampling_rate_hz
        )
        token_end_sec = self.source_start_sec + (
            global_ends.astype("float64") / self.producer.source_sampling_rate_hz
        )

        consumed = count * self.producer.stride
        self._buffer = combined[:, consumed:].copy()
        self._received_samples = next_received
        self._emitted_tokens += count
        if self.buffered_samples >= self.producer.kernel_size:
            raise RuntimeError("mutable overlap state reached a complete kernel")
        if self.mutable_state_bytes > self.producer.mutable_state_bound_bytes:
            raise RuntimeError("mutable overlap state exceeded its declared bound")
        self._max_buffered_samples = max(
            self._max_buffered_samples, self.buffered_samples
        )
        self._max_mutable_state_bytes = max(
            self._max_mutable_state_bytes, self.mutable_state_bytes
        )
        return StreamingTokenBatch(
            tokens=tokens,
            frame_start_samples=global_starts,
            frame_end_samples=global_ends,
            availability_samples=availability_samples,
            token_start_sec=token_start_sec,
            token_end_sec=token_end_sec,
            schedule_delay_samples=delay_samples,
        )

    def flush(self, *, policy: str = DROP_INCOMPLETE_FLUSH) -> StreamFlushSummary:
        """Close the stream without inventing a padded final frame."""

        if self._closed:
            raise RuntimeError("stream is already closed")
        if policy != DROP_INCOMPLETE_FLUSH:
            raise ValueError(f"unsupported flush policy: {policy}")
        if self._emitted_tokens:
            last_frame_end = (
                (self._emitted_tokens - 1) * self.producer.stride
                + self.producer.kernel_size
            )
            unframed_tail = max(0, self._received_samples - last_frame_end)
        else:
            unframed_tail = self._received_samples
        buffered_before = self.buffered_samples
        np = _require_numpy()
        self._buffer = np.zeros((self.producer.n_channels, 0), dtype="float32")
        self._closed = True
        return StreamFlushSummary(
            policy=policy,
            received_samples=self._received_samples,
            emitted_tokens=self._emitted_tokens,
            buffered_samples_before_flush=buffered_before,
            unframed_tail_samples=unframed_tail,
            mutable_state_bytes_after_flush=self.mutable_state_bytes,
            stream_closed=self._closed,
        )

    def state_summary(self) -> dict[str, object]:
        return {
            "received_samples": self._received_samples,
            "emitted_tokens": self._emitted_tokens,
            "buffered_samples": self.buffered_samples,
            "mutable_state_bytes": self.mutable_state_bytes,
            "max_buffered_samples": self._max_buffered_samples,
            "max_mutable_state_bytes": self._max_mutable_state_bytes,
            "next_frame_start_sample": self._emitted_tokens
            * self.producer.stride,
            "closed": self._closed,
        }


CausalWindowTokenStream = CausalMockNeuroTokenStream


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Streaming NeuroTokens require NumPy: `pip install numpy`.") from exc
    return np
