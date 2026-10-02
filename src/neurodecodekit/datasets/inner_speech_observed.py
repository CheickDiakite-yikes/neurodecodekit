"""Pure observed-phase slot assignment; never repair events, targets or time.

The returned slots are local/private records, including excluded observations.
Only the aggregate summary is suitable for publication. A valid slot has four
or five strictly increasing phase ranks: its first rank is 0/1, its last 3/4.
Thus every valid boundary necessarily decreases rank; equal-rank duplicates
cannot be resolved by inventing a slot and are refused.
"""

from dataclasses import dataclass, replace

from neurodecodekit.datasets.inner_speech import SFREQ, _require


PHASE_NAMES = ("start", "cue", "action", "relax", "rest")
PHASE_RANK = {42: 0, 31: 1, 32: 1, 33: 1, 34: 1, 44: 2, 45: 3, 46: 4}
ATTENTION = (17, 61, 62, 63, 64)


@dataclass(frozen=True)
class ObservedSlot:
    label: int | None
    condition: int
    start: int | None
    cue: int | None
    action: int | None
    relax: int | None
    rest: int | None
    run_ordinal: int
    original_index: int

    @property
    def eligible(self):
        return self.cue is not None and self.action is not None and self.relax is not None


def _make_slot(phases, condition, run, original_index):
    _require(len(phases) in (4, 5), "slot_phase_count")
    values = {name: phases[rank][0] if rank in phases else None
              for rank, name in enumerate(PHASE_NAMES)}
    slot = ObservedSlot(label=phases[1][1] - 31 if 1 in phases else None,
                        condition=condition, run_ordinal=run, original_index=original_index, **values)
    bounds = ((1, 5 * SFREQ), (384, 3 * SFREQ), (2 * SFREQ, 4 * SFREQ), (1, 3 * SFREQ))
    for left, right, (lower, upper) in zip(PHASE_NAMES, PHASE_NAMES[1:], bounds):
        start, stop = values[left], values[right]
        if start is not None and stop is not None:
            _require(lower <= stop - start <= upper, "trial_timing")
    if slot.eligible:
        _require(slot.cue + 384 <= slot.action and slot.relax - 2048 >= slot.action,
                 "observed_window_bounds")
    return slot


def parse_observed_slots(events, *, participant, session="ses-01", summary=None):
    """Assign exactly 5x40 observed slots for explicitly admitted sessions.

    At most one of start/cue/action/relax/rest may be absent in any slot.
    Missing start/rest alone retain eligibility. Missing cue/action/relax
    excludes a slot without relabeling or compressing original chronology.
    Session 1 permits at most seven missing-core exclusions per person;
    opt-in session 2 permits two. The caller enforces the respective study-wide
    caps of seven and twenty, along with condition coverage and split preflight.
    Session-1 participant corrections never apply to session 2.
    Only observed adjacent logical intervals are validated; missing timestamps
    stay None, never an inferred boundary or substituted neighbouring event.
    """
    _require(participant in {f"sub-{i:02d}" for i in range(1, 11)} and session in ("ses-01", "ses-02"),
             "participant_session")
    _require(isinstance(events, (list, tuple)) and 0 < len(events) <= 10000, "event_count")
    _require(all(isinstance(item, (list, tuple)) and len(item) == 2 and
                 all(type(value) is int for value in item) and item[0] >= 0 for item in events),
             "event_format")
    _require(all(left[0] < right[0] for left, right in zip(events, events[1:])), "event_order")
    position = 0

    def peek():
        return events[position][1] if position < len(events) else None

    def take(allowed):
        nonlocal position
        _require(position < len(events) and events[position][1] in allowed, "event_grammar")
        item = events[position]
        position += 1
        return item

    take((11,))
    take((13,))
    missing_baseline_end = peek() != 14
    _require(not missing_baseline_end or (participant == "sub-10" and session == "ses-01"),
             "baseline_end_missing")
    if not missing_baseline_end:
        take((14,))
    ancillary = {"attention_question_events": 0, "attention_answer_events": 0,
                 "unpaired_attention_questions": 0, "unpaired_attention_answers": 0,
                 "missing_inter_run_rest_tags": 0}
    slots, conditions = [], []
    for run in range(1, 6):
        take((15,))
        condition = take((21, 22, 23))[1]
        conditions.append(condition)
        phases, last_rank, run_start = {}, -1, len(slots)
        while peek() != 16:
            code = peek()
            if code in ATTENTION:
                _require(last_rank == 4 and 4 in phases, "attention_requires_observed_rest")
                pending_question = False
                while peek() in ATTENTION:
                    attention = take(ATTENTION)[1]
                    if attention == 17:
                        ancillary["attention_question_events"] += 1
                        ancillary["unpaired_attention_questions"] += int(pending_question)
                        pending_question = True
                    else:
                        ancillary["attention_answer_events"] += 1
                        ancillary["unpaired_attention_answers"] += int(not pending_question)
                        pending_question = False
                ancillary["unpaired_attention_questions"] += int(pending_question)
                _require(peek() == 16 or PHASE_RANK.get(peek()) in (0, 1), "attention_boundary")
                continue
            _require(code in PHASE_RANK, "event_grammar")
            rank = PHASE_RANK[code]
            _require(rank != last_rank, "duplicate_phase_rank")
            if rank < last_rank:
                slots.append(_make_slot(phases, condition, run, len(slots)))
                phases = {}
            if not phases:
                _require(rank in (0, 1), "slot_start_rank")
            phases[rank] = take(PHASE_RANK)
            last_rank = rank
            _require(len(slots) - run_start < 40, "run_slot_count")
        _require(bool(phases), "run_slot_count")
        slots.append(_make_slot(phases, condition, run, len(slots)))
        _require(len(slots) - run_start == 40, "run_slot_count")
        take((16,))
        if run < 5:
            if peek() == 51:
                take((51,))
            else:
                ancillary["missing_inter_run_rest_tags"] += 1
    take((12,))
    _require(position == len(events), "trailing_events")
    expected = [21, 22, 22, 23, 23]
    correction_allowed = participant == "sub-03" and session == "ses-01"
    _require(conditions == expected or
             (correction_allowed and conditions == [21, 22, 23, 23, 23]), "condition_layout")
    corrected = correction_allowed and conditions == expected
    if corrected:
        slots = [replace(slot, condition=23) if slot.run_ordinal == 3 else slot for slot in slots]
    excluded = sum(not slot.eligible for slot in slots)
    _require(len(slots) == 200 and excluded <= (7 if session == "ses-01" else 2),
             "exclusion_cap_or_slot_count")
    if summary is not None:
        summary.update(
            slots=200, eligible=200 - excluded, excluded=excluded, runs=5,
            exclusion_reasons={"missing_" + name: sum(getattr(slot, name) is None for slot in slots)
                               for name in ("cue", "action", "relax")},
            missing_start_events=sum(slot.start is None for slot in slots),
            missing_rest_events=sum(slot.rest is None for slot in slots),
            condition_counts_nominal={str(code): sum(slot.condition == code for slot in slots)
                                      for code in (21, 22, 23)},
            condition_counts_eligible={str(code): sum(slot.condition == code and slot.eligible for slot in slots)
                                       for code in (21, 22, 23)},
            baseline_end_missing=missing_baseline_end, **ancillary,
            condition_correction_applied=corrected,
            condition_correction_already_present=correction_allowed and not corrected,
            inferred_target_count=0, synthesized_event_count=0)
    return slots
