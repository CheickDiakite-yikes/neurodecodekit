"""Pure collapsed-family diagnostics, not a parser or a trial qualification.

Rank-reset segments describe the observed stream only. Neither a missing marker
nor any scientific trial identity is established by a segment signature.
"""

from collections import Counter
import importlib.util
import json
from numbers import Integral
from pathlib import Path


_SPEC = importlib.util.spec_from_file_location(
    "session2_structure_family", Path(__file__).with_name("audit_inner_speech_events.py"))
_AUDIT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_AUDIT)
family = _AUDIT.family

PHASES = ("trial_start", "direction_cue", "action", "relax", "rest")
RANK = {name: i for i, name in enumerate(PHASES)}
ATTENTION = {"attention_question", "attention_answer"}
INTERVALS = {
    "start_to_cue": (0, 1, 1, 5120),
    "cue_to_action": (1, 2, 384, 3072),
    "action_to_relax": (2, 3, 2048, 4096),
    "relax_to_rest": (3, 4, 1, 3072),
}
WINDOWS = {"cue_384_before_action": (1, 2, 384),
           "action_2048_before_relax": (2, 3, 2048)}


def _multiplicity(count):
    return "zero" if count == 0 else "one" if count == 1 else "multiple"


def _key(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _rows(counter, name):
    return [dict(json.loads(key), **{name: count}) for key, count in sorted(counter.items())]


def _run_spans(names):
    spans, depth, start, nested = [], 0, None, False
    unmatched_end, nested_start = 0, 0
    for index, name in enumerate(names):
        if name == "run_start":
            if depth == 0:
                start, nested = index, False
            else:
                nested, nested_start = True, nested_start + 1
            depth += 1
        elif name == "run_end":
            if not depth:
                unmatched_end += 1
                continue
            depth -= 1
            if depth == 0 and not nested:
                spans.append((start, index))
    return spans, {"unmatched_run_ends": unmatched_end, "nested_run_starts": nested_start,
                   "unclosed_run_starts": depth}


def _segments(names, start, stop):
    """Partition only at observed rank decreases to start/cue; retain anomalies."""
    result, begin, previous, ambiguous = [], None, None, False
    for index in range(start + 1, stop):
        name = names[index]
        if name not in RANK:
            continue
        rank = RANK[name]
        if begin is None:
            begin, ambiguous = index, rank > 1
        elif rank < previous and rank <= 1:
            # A reset before relax/rest is not evidence of an intact slot boundary.
            bad_boundary = previous < 3
            result.append((begin, index, ambiguous or bad_boundary, name))
            begin, ambiguous = index, bad_boundary
        previous = rank
    if begin is not None:
        result.append((begin, stop, ambiguous or previous < 3, "run_end"))
    return result


def _signature(samples, names, begin, end, boundary_ambiguous, ending):
    block = names[begin:end]
    positions = {p: [i for i in range(begin, end) if names[i] == p] for p in PHASES}
    ranks = [RANK[p] for p in block if p in RANK]
    ordered = all(a < b for a, b in zip(ranks, ranks[1:]))
    duplicate = any(len(indices) > 1 for indices in positions.values())
    foreign = any(p not in RANK and p not in ATTENTION for p in block)
    # Include both adjacent boundary gaps; a reset never repairs sample ordering.
    bad_sample_order = any(samples[i] >= samples[i + 1]
                           for i in range(max(0, begin - 1), min(end, len(samples) - 1)))
    ambiguous = boundary_ambiguous or not ordered or duplicate or foreign or bad_sample_order
    phase_indices = [i for indices in positions.values() for i in indices]
    interleaved = any(names[i] in ATTENTION
                      for i in range(min(phase_indices), max(phase_indices)))
    signature = {
        "phase_counts": {p: _multiplicity(len(positions[p])) for p in PHASES},
        "strictly_ordered_observed_phases": ordered,
        "duplicate_phase": duplicate, "ambiguous_structure": ambiguous,
        "nonincreasing_sample_gap": bad_sample_order,
        "noncore_nonattention_marker": foreign,
        "contiguous_cue_action_relax": any(
            block[i:i + 3] == ["direction_cue", "action", "relax"]
            for i in range(len(block) - 2)),
        "attention_present": any(p in ATTENTION for p in block),
        "attention_between_observed_phases": interleaved,
        "ending_boundary_family": ending,
    }

    def interval(a, b, lower, upper=None):
        left, right = positions[PHASES[a]], positions[PHASES[b]]
        if len(left) != 1 or len(right) != 1:
            return "unavailable_missing_or_duplicate"
        if ambiguous:
            return "unavailable_ambiguous_structure"
        delta = samples[right[0]] - samples[left[0]]
        return "within_range" if delta >= lower and (upper is None or delta <= upper) else "outside_range"

    signature["observed_phase_interval_checks"] = {
        name: interval(*bounds) for name, bounds in INTERVALS.items()}
    signature["observed_core_window_checks"] = {
        name: interval(*bounds) for name, bounds in WINDOWS.items()}
    return signature


def analyze_structure(events, *, check=None):
    """Return aggregate patterns only; no repair, parser, file or numerical calls.

    Samples are retained internally solely for range comparisons. All codes are
    immediately collapsed using the existing audit allowlist. Run-boundary pairs
    must be nonnested; structural rank-reset segments must never be called trials.
    The resource callback can refuse at any point without producing a partial result.
    """
    check = check or (lambda: None)
    check()
    samples, names = [], []
    for index, event in enumerate(events):
        if index % 256 == 0:
            check()
        if len(event) != 2 or any(isinstance(v, bool) or not isinstance(v, Integral) for v in event):
            raise ValueError("event_format")
        sample, code = event
        names.append(family(int(code)))
        samples.append(int(sample))
    spans, malformed = _run_spans(names)
    owners, segment_at, previous_phase = [-1] * len(names), [None] * len(names), [None] * len(names)
    patterns, attention_patterns = Counter(), Counter()
    run_segment_counts, run_condition_counts = Counter(), Counter()
    segment_count, inside_events = 0, 0
    for owner, (start, stop) in enumerate(spans):
        check()
        last = "none_observed"
        for index in range(start, stop + 1):
            owners[index], previous_phase[index] = owner, last
            if names[index] in RANK:
                last = names[index]
        inside_events += stop - start + 1
        segments = _segments(names, start, stop)
        run_segment_counts[len(segments)] += 1
        run_condition_counts[_multiplicity(names[start:stop + 1].count("condition_marker"))] += 1
        for begin, end, ambiguous, ending in segments:
            check()
            signature = _signature(samples, names, begin, end, ambiguous, ending)
            patterns[_key(signature)] += 1
            segment_count += 1
            for index in range(begin, end):
                segment_at[index] = signature
    groups, attention_events, outside_groups, index = 0, 0, 0, 0
    while index < len(names):
        if index % 256 == 0:
            check()
        if names[index] not in ATTENTION:
            index += 1
            continue
        end = index + 1
        while end < len(names) and names[end] in ATTENTION:
            end += 1
        counts = Counter(names[index:end])
        inside = owners[index] >= 0 and owners[index] == owners[end - 1]
        signature = segment_at[index] if inside else None
        context = {
            "run_context": "inside_intact_boundary_pair" if inside else "outside_or_ambiguous_run",
            "preceding_family": names[index - 1] if index else "beginning_of_events",
            "next_family": names[end] if end < len(names) else "end_of_events",
            "previous_observed_core_phase": previous_phase[index] if inside else "unavailable",
            "question_count": _multiplicity(counts["attention_question"]),
            "answer_count": _multiplicity(counts["attention_answer"]),
            "single_question_then_answers": names[index] == "attention_question" and
            counts["attention_question"] == 1 and counts["attention_answer"] >= 1,
            "segment_signature": signature,
        }
        attention_patterns[_key(context)] += 1
        groups, attention_events = groups + 1, attention_events + end - index
        outside_groups += int(not inside)
        index = end
    check()
    return {
        "schema_version": 1, "events": len(names),
        "event_family_counts": dict(sorted(Counter(names).items())),
        "nonincreasing_sample_pairs": sum(a >= b for a, b in zip(samples, samples[1:])),
        "intact_run_boundary_pairs": len(spans),
        "per_run_segment_count_histogram": [
            {"structural_segments": count, "runs": runs} for count, runs in sorted(run_segment_counts.items())],
        "per_run_condition_marker_multiplicity_histogram": {
            name: run_condition_counts[name] for name in ("zero", "one", "multiple")},
        "events_inside_intact_run_boundaries": inside_events,
        "events_outside_or_ambiguous_run_boundaries": len(names) - inside_events,
        "unassigned_run_boundary_markers": sum(p in {"run_start", "run_end"} for p in names) - 2 * len(spans),
        "malformed_run_boundary_counts": malformed,
        "structural_segments": segment_count,
        "structural_segment_patterns": _rows(patterns, "segments"),
        "attention_groups": groups, "attention_events": attention_events,
        "attention_groups_outside_or_ambiguous_runs": outside_groups,
        "attention_context_patterns": _rows(attention_patterns, "groups"),
        "parser_calls": 0, "events_changed": 0, "labels_inferred": 0,
        "alignment_or_scientific_qualification_established": False,
    }
