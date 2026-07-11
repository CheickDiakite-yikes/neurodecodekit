"""Character vocabulary and decoding helpers for the local CTC path."""

from __future__ import annotations

import re
from typing import Iterable


CTC_BLANK_ID = 0
CTC_BLANK_TOKEN = "<blank>"
CTC_ALPHABET = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")
CTC_VOCAB = (CTC_BLANK_TOKEN, *CTC_ALPHABET)
CTC_TOKEN_TO_ID = {token: index for index, token in enumerate(CTC_VOCAB)}


def normalize_ctc_text(text: str) -> str:
    """Normalize text without silently discarding unsupported characters."""

    normalized = re.sub(r"\s+", " ", str(text).upper()).strip()
    unsupported = sorted(set(normalized) - set(CTC_ALPHABET))
    if unsupported:
        raise ValueError(
            "CTC text contains unsupported characters "
            f"{unsupported}; supported targets are A-Z and space."
        )
    return normalized


def encode_ctc_text(text: str) -> list[int]:
    """Encode one target string; blank zero is never used in a target."""

    normalized = normalize_ctc_text(text)
    if not normalized:
        raise ValueError("CTC target text must not be empty.")
    return [CTC_TOKEN_TO_ID[character] for character in normalized]


def decode_ctc_target(token_ids: Iterable[int]) -> str:
    """Decode target IDs without repeat collapsing."""

    characters: list[str] = []
    for value in token_ids:
        token_id = int(value)
        if token_id <= CTC_BLANK_ID or token_id >= len(CTC_VOCAB):
            if token_id == CTC_BLANK_ID:
                continue
            raise ValueError(f"CTC token ID is outside vocabulary: {token_id}")
        characters.append(CTC_VOCAB[token_id])
    return "".join(characters)


def greedy_decode_ctc_ids(token_ids: Iterable[int]) -> str:
    """Collapse repeats and remove blanks using standard greedy CTC semantics."""

    characters: list[str] = []
    previous = CTC_BLANK_ID
    for value in token_ids:
        token_id = int(value)
        if token_id < 0 or token_id >= len(CTC_VOCAB):
            raise ValueError(f"CTC token ID is outside vocabulary: {token_id}")
        if token_id != previous and token_id != CTC_BLANK_ID:
            characters.append(CTC_VOCAB[token_id])
        previous = token_id
    return "".join(characters)


def minimum_ctc_input_steps(token_ids: Iterable[int]) -> int:
    """Return the minimum output steps needed to align a CTC target."""

    values = [int(value) for value in token_ids]
    adjacent_repeats = sum(current == previous for previous, current in zip(values, values[1:]))
    return len(values) + adjacent_repeats
