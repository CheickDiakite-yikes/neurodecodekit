"""Simple keyboard-distance utilities.

This is not meant to be a perfect motor model. It is a cheap diagnostic: if
mistakes cluster near the target key, the model may be capturing motor/keyboard
structure rather than only language-level information.
"""

from __future__ import annotations

from math import sqrt

# Approximate QWERTY layout. SpanishBCBL used a QWERTY keyboard and uppercase
# Spanish text without accents for the task. We keep the map simple for v0.
_ROWS = [
    "1234567890",
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM",
]

KEY_COORDS: dict[str, tuple[float, float]] = {}
for y, row in enumerate(_ROWS):
    x_offset = 0.0 if y == 0 else (0.5 if y == 1 else (0.75 if y == 2 else 1.25))
    for x, char in enumerate(row):
        KEY_COORDS[char] = (x + x_offset, float(y))
KEY_COORDS[" "] = (4.5, 4.0)


def key_distance(target_char: str, pred_char: str, *, unknown_penalty: float = 5.0) -> float:
    """Return Euclidean distance between two approximate keyboard positions."""

    t = target_char.upper()
    p = pred_char.upper()
    if t == p:
        return 0.0
    if t not in KEY_COORDS or p not in KEY_COORDS:
        return unknown_penalty
    x1, y1 = KEY_COORDS[t]
    x2, y2 = KEY_COORDS[p]
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def aligned_keyboard_distance(target: str, prediction: str, *, gap_penalty: float = 5.0) -> float:
    """Average keyboard distance under a simple position-wise alignment.

    This intentionally avoids complicated edit-path alignment in v0. It is a
    diagnostic, not a publication metric.
    """

    if not target and not prediction:
        return 0.0
    max_len = max(len(target), len(prediction))
    total = 0.0
    for i in range(max_len):
        if i >= len(target) or i >= len(prediction):
            total += gap_penalty
        else:
            total += key_distance(target[i], prediction[i], unknown_penalty=gap_penalty)
    return total / max_len
