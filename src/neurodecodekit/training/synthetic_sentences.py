"""Deterministic variable-length sentence signals for CTC plumbing tests."""

from __future__ import annotations

from pathlib import Path

from neurodecodekit.preprocess.ctc_text import encode_ctc_text


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Synthetic sentence generation requires NumPy: `pip install numpy`.") from exc
    return np


def make_synthetic_sentence_arrays(
    *,
    sentences: int = 96,
    channels: int = 6,
    letter_classes: int = 4,
    min_word_length: int = 2,
    max_word_length: int = 4,
    token_width: int = 5,
    gap_width: int = 3,
    sfreq: float = 50.0,
    seed: int = 7,
):
    """Create easy but variable synthetic CTC sequences.

    Each target token has a channel-local pulse and tokens are separated by a
    noise-only gap. This proves sequence batching and CTC loss behavior; it is
    deliberately not a physiological simulation.
    """

    if sentences < 4:
        raise ValueError("sentences must be >= 4")
    if not 2 <= letter_classes <= 10:
        raise ValueError("letter_classes must be between 2 and 10")
    if channels < letter_classes + 1:
        raise ValueError("channels must provide one motif channel per letter plus space")
    if min_word_length < 1 or max_word_length < min_word_length:
        raise ValueError("word length bounds are invalid")
    if token_width < 2 or gap_width < 1:
        raise ValueError("token_width must be >= 2 and gap_width must be >= 1")
    if sfreq <= 0:
        raise ValueError("sfreq must be > 0")

    np = _require_numpy()
    rng = np.random.default_rng(seed)
    letters = [chr(ord("A") + index) for index in range(letter_classes)]
    target_texts: list[str] = []
    seen: set[str] = set()
    max_attempts = sentences * 100
    attempts = 0
    while len(target_texts) < sentences and attempts < max_attempts:
        attempts += 1
        words = []
        for _ in range(2):
            length = int(rng.integers(min_word_length, max_word_length + 1))
            words.append("".join(str(rng.choice(letters)) for _ in range(length)))
        text = " ".join(words)
        if text not in seen:
            seen.add(text)
            target_texts.append(text)
    if len(target_texts) != sentences:
        raise ValueError(
            "Could not generate enough unique sentences; increase letter classes or word lengths."
        )

    encoded = [encode_ctc_text(text) for text in target_texts]
    lead_widths = rng.integers(2, 6, size=sentences)
    tail_widths = rng.integers(2, 6, size=sentences)
    input_lengths = np.asarray(
        [
            int(lead_widths[index] + tail_widths[index])
            + len(tokens) * token_width
            + (len(tokens) - 1) * gap_width
            for index, tokens in enumerate(encoded)
        ],
        dtype="int32",
    )
    max_timepoints = int(input_lengths.max())
    signals = np.zeros((sentences, channels, max_timepoints), dtype="float32")
    motif_tokens = [*letters, " "]
    motif_channel = {token: index for index, token in enumerate(motif_tokens)}
    for row_index, (text, length) in enumerate(zip(target_texts, input_lengths.tolist())):
        row = rng.normal(0.0, 0.035, size=(channels, length)).astype("float32")
        cursor = int(lead_widths[row_index])
        for char_index, character in enumerate(text):
            channel = motif_channel[character]
            row[channel, cursor : cursor + token_width] += 3.0
            row[(channel + 1) % channels, cursor : cursor + token_width] += 0.35
            cursor += token_width
            if char_index < len(text) - 1:
                cursor += gap_width
        signals[row_index, :, :length] = row

    target_lengths = np.asarray([len(tokens) for tokens in encoded], dtype="int32")
    target_token_ids = np.zeros((sentences, int(target_lengths.max())), dtype="int16")
    for row_index, tokens in enumerate(encoded):
        target_token_ids[row_index, : len(tokens)] = tokens
    start_sec = np.zeros(sentences, dtype="float64")
    end_sec = input_lengths.astype("float64") / sfreq
    arrays = {
        "signals": signals,
        "input_lengths": input_lengths,
        "target_token_ids": target_token_ids,
        "target_lengths": target_lengths,
        "target_texts": np.asarray(target_texts, dtype="U"),
        "reference_texts": np.asarray(target_texts, dtype="U"),
        "mat_response_texts": np.asarray(target_texts, dtype="U"),
        "trial_indices": np.arange(sentences, dtype="int32"),
        "sentence_start_sec": start_sec,
        "sentence_end_sec": end_sec,
        "channel_names": np.asarray(
            [f"synthetic_sentence_ch_{index}" for index in range(channels)], dtype="U"
        ),
    }
    metadata = {
        "kind": "synthetic_continuous_sentences",
        "source_files": {},
        "transformations": [
            {
                "name": "synthetic_ctc_sentence_generation",
                "description": (
                    "Generated variable-length noise signals with token-specific channel pulses "
                    "and explicit blank gaps."
                ),
                "params": {
                    "sentences": sentences,
                    "channels": channels,
                    "letter_classes": letter_classes,
                    "min_word_length": min_word_length,
                    "max_word_length": max_word_length,
                    "token_width": token_width,
                    "gap_width": gap_width,
                    "sfreq": sfreq,
                    "seed": seed,
                },
            }
        ],
        "sampling_rate_hz": sfreq,
        "warnings": [
            "synthetic_sentence_cache_not_real_neural_data",
            "token_pulses_are_intentionally_easy_for_ctc_plumbing_validation",
        ],
    }
    return arrays, metadata


def save_synthetic_sentence_npz(
    out: str | Path,
    **kwargs,
) -> dict[str, object]:
    """Generate, validate, and save one synthetic sentence cache."""

    from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache

    arrays, metadata = make_synthetic_sentence_arrays(**kwargs)
    save_sentence_npz_cache(out, **arrays, metadata=metadata)
    path = Path(out)
    return {
        "path": str(path),
        "bytes": int(path.stat().st_size),
        "shape": tuple(int(value) for value in arrays["signals"].shape),
        "n_sentences": int(arrays["signals"].shape[0]),
        "min_input_length": int(arrays["input_lengths"].min()),
        "max_input_length": int(arrays["input_lengths"].max()),
        "min_target_length": int(arrays["target_lengths"].min()),
        "max_target_length": int(arrays["target_lengths"].max()),
    }
