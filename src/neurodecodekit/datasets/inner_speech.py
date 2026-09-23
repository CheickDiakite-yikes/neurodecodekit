"""Bounded ds003626 BDF reads and strict, prospective four-word event grammar.

Public source: N-Nieto/Inner_Speech_Dataset at
65bd162a32f38546b6596cb25d46f4a862fa87fb, lib/data_extractions.py and
lib/AdHoc_modification.py; paper doi:10.1038/s41597-022-01147-2, Table 3.
The current MATLAB demonstration disagrees with the published timing/grammar;
fixed windows use observed events, with broad prospective interval bounds.
Deviation from nominal published durations is diagnostic, never a tuning input.
No missing direction, action marker, or timestamp is ever inferred.
"""

from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
import math
import os
from pathlib import Path
import re


SFREQ = 1024
MAX_WINDOW_SAMPLES = 4096
EEG_CHANNELS = tuple(f"{bank}{index}" for bank in "ABCD" for index in range(1, 33))
EXG_CHANNELS = tuple(f"EXG{index}" for index in range(1, 9))
INTERVAL_NAMES = ("concentration", "cue", "action", "relax")
NOMINAL_INTERVALS = (.5, .5, 2.5, 1.0)


class InnerSpeechRefusal(ValueError):
    """Fixed technical code only: never include private values in errors."""


def _require(condition, code):
    if not condition:
        raise InnerSpeechRefusal(code)


def _numpy():
    try:
        import numpy as np
    except ImportError:
        raise ImportError("Install neurodecodekit[array] for bounded BDF reads") from None
    return np


def _integer(field):
    _require(re.fullmatch(rb" *-?[0-9]+ *", field) is not None, "header_integer")
    return int(field)


def _number(field):
    try:
        value = float(field)
    except ValueError:
        raise InnerSpeechRefusal("header_number") from None
    _require(math.isfinite(value), "header_nonfinite")
    return value


def _decode24(data, *, signed):
    np = _numpy()
    _require(len(data) % 3 == 0, "truncated_sample")
    octets = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
    values = octets[:, 0] | (octets[:, 1] << 8) | (octets[:, 2] << 16)
    return (values ^ 0x800000) - 0x800000 if signed else values


class BDFReader:
    """Header-only construction; no MNE, preload, mmap, or persistent handle.

    Windows are half-open and returned in microvolts. Status cannot be picked as
    a physiological feature. Only required EEG/EXG channels may be window-read.
    """

    def __init__(self, path):
        self.path = Path(path)
        with self.path.open("rb") as stream:
            stat = os.fstat(stream.fileno())
            self._identity = (stat.st_size, stat.st_mtime_ns, stat.st_ino)
            fixed = stream.read(256)
            _require(len(fixed) == 256 and fixed[:8] == b"\xffBIOSEMI", "bdf_magic")
            count = _integer(fixed[252:256])
            _require(137 <= count <= 512, "channel_count")
            self.header_bytes = _integer(fixed[184:192])
            _require(self.header_bytes == 256 * (count + 1), "header_length")
            header = stream.read(256 * count)
        _require(len(header) == 256 * count, "header_truncated")
        _require(fixed[192:236].strip() == b"24BIT", "bdf_24bit_marker")
        self.n_records = _integer(fixed[236:244])
        _require(self.n_records > 0, "record_count")
        try:
            duration = Decimal(fixed[244:252].decode("ascii").strip())
        except (InvalidOperation, UnicodeDecodeError):
            raise InnerSpeechRefusal("record_duration") from None
        _require(duration.is_finite() and duration > 0, "record_duration")

        def fields(offset, width):
            return [header[offset * count + i * width:offset * count + (i + 1) * width]
                    for i in range(count)]

        labels = fields(0, 16)
        _require(all(all(32 <= byte < 127 for byte in item) for item in labels), "channel_label")
        self.channel_names = tuple(item.decode("ascii").strip() for item in labels)
        _require(all(self.channel_names) and len(set(self.channel_names)) == count, "channel_label")
        _require(set(EEG_CHANNELS + EXG_CHANNELS).issubset(self.channel_names), "required_channels")
        _require(self.channel_names[-1] == "Status", "status_channel")
        samples = [_integer(item) for item in fields(216, 8)]
        _require(all(0 < item <= 65536 and Decimal(item) == SFREQ * duration for item in samples),
                 "sampling_geometry")
        self.samples_per_record = samples[0]
        self.n_samples = self.n_records * self.samples_per_record
        self.sfreq = SFREQ
        self.record_bytes = 3 * sum(samples)
        _require(stat.st_size == self.header_bytes + self.n_records * self.record_bytes,
                 "file_geometry")
        units, pmin, pmax = fields(96, 8), fields(104, 8), fields(112, 8)
        dmin, dmax = fields(120, 8), fields(128, 8)
        self._scales, self._offsets = {}, {}
        for name in EEG_CHANNELS + EXG_CHANNELS:
            index = self.channel_names.index(name)
            unit = units[index].strip()
            _require(unit in (b"uV", b"\xb5V"), "physical_unit_not_microvolts")
            lo, hi = _integer(dmin[index]), _integer(dmax[index])
            plo, phi = _number(pmin[index]), _number(pmax[index])
            _require(-8388608 <= lo < hi <= 8388607 and plo < phi, "calibration_range")
            self._scales[index] = (phi - plo) / (hi - lo)
            self._offsets[index] = plo - lo * self._scales[index]
        self.status_summary = {}

    def _open(self):
        stream = self.path.open("rb")
        stat = os.fstat(stream.fileno())
        if (stat.st_size, stat.st_mtime_ns, stat.st_ino) != self._identity:
            stream.close()
            raise InnerSpeechRefusal("file_changed")
        return stream

    def _read_channel(self, stream, record, channel, start, stop):
        offset = self.header_bytes + record * self.record_bytes
        offset += 3 * (channel * self.samples_per_record + start)
        stream.seek(offset)
        data = stream.read(3 * (stop - start))
        _require(len(data) == 3 * (stop - start), "body_truncated")
        return data

    def iter_status_events(self, check=None, *, participant, session="ses-01"):
        """Return (sample, code) for initial/changed nonzero low-16-bit words.

        High acquisition bits, including 65536, are masked, not trial codes.
        Pulse state spans records. Only sub-10/ses-01 discards pulses shorter
        than ceil(.002*1024)=3 samples, prospectively matching the source's
        duration exception; other participants retain every nonzero pulse.
        Counts are technical aggregates; raw status words never enter reports.
        """
        np = _numpy()
        _require(participant in {f"sub-{i:02d}" for i in range(1, 11)} and session == "ses-01",
                 "participant_session")
        minimum = 3 if participant == "sub-10" else 1
        events, previous, onset = [], 0, 0
        summary = {"short_pulses_below_three": 0, "ignored_short_pulses": 0,
                   "nonzero_highbit_samples": 0, "minimum_pulse_samples": minimum}

        def finish(stop):
            if previous:
                width = stop - onset
                summary["short_pulses_below_three"] += int(width < 3)
                if width >= minimum:
                    events.append((onset, previous))
                    _require(len(events) <= 10000, "event_count")
                else:
                    summary["ignored_short_pulses"] += 1

        with self._open() as stream:
            for record in range(self.n_records):
                if check is not None:
                    check()
                words = _decode24(self._read_channel(stream, record, len(self.channel_names) - 1,
                                                     0, self.samples_per_record), signed=False)
                summary["nonzero_highbit_samples"] += int(np.count_nonzero(words & 0xFF0000))
                codes = words & 0xFFFF
                changes = np.flatnonzero(codes[1:] != codes[:-1]) + 1
                if int(codes[0]) != previous:
                    changes = np.concatenate(([0], changes))
                for index in changes:
                    sample = record * self.samples_per_record + int(index)
                    finish(sample)
                    previous, onset = int(codes[index]), sample
            finish(self.n_samples)
        summary["events_retained"] = len(events)
        self.status_summary = summary
        return events

    def read_window(self, start, stop, picks):
        np = _numpy()
        _require(type(start) is int and type(stop) is int and
                 0 <= start < stop <= self.n_samples and stop - start <= MAX_WINDOW_SAMPLES,
                 "window_bounds")
        indices = []
        for pick in picks:
            if isinstance(pick, str):
                _require(pick in self.channel_names, "window_channel")
                pick = self.channel_names.index(pick)
            _require(type(pick) is int and pick in self._scales, "window_channel")
            indices.append(pick)
        _require(indices and len(set(indices)) == len(indices), "window_channels")
        result = np.empty((len(indices), stop - start), dtype=np.float64)
        with self._open() as stream:
            for record in range(start // self.samples_per_record,
                                (stop - 1) // self.samples_per_record + 1):
                origin = record * self.samples_per_record
                lo, hi = max(start, origin), min(stop, origin + self.samples_per_record)
                for row, channel in enumerate(indices):
                    values = _decode24(self._read_channel(stream, record, channel,
                                                         lo - origin, hi - origin), signed=True)
                    result[row, lo - start:hi - start] = (
                        values * self._scales[channel] + self._offsets[channel])
        return result


@dataclass(frozen=True)
class Trial:
    label: int
    condition: int
    start: int
    cue: int
    action: int
    relax: int
    rest: int
    run_ordinal: int


def parse_trials(events, *, participant, session="ses-01", summary=None):
    """Validate all 200 trials, then apply only the registered sub-03 correction.

    Admitted intervals (seconds): concentration(0,5], cue[.375,3],
    action[2,4], relax(0,3]. Nominal-timing deviations >.1s are diagnostic.
    Rest durations and attention-response latency are not used for selection.
    Missing baseline-end14 is permitted only for sub-10 and never synthesized.
    Unpaired attention events are ignored only after a complete rest46 and
    before the next trial/run end. Inter-run rest51 is optional between intact
    run-end16/start15 markers. Neither exception changes or drops any trial.
    The optional summary dictionary receives aggregate qualification facts.
    """
    _require(participant in {f"sub-{i:02d}" for i in range(1, 11)} and session == "ses-01",
             "participant_session")
    _require(isinstance(events, (list, tuple)) and 0 < len(events) <= 10000, "event_count")
    _require(all(isinstance(item, (list, tuple)) and len(item) == 2 and
                 all(type(value) is int for value in item) and item[0] >= 0 for item in events),
             "event_format")
    _require(all(left[0] < right[0] for left, right in zip(events, events[1:])), "event_order")
    position = 0

    def take(allowed):
        nonlocal position
        _require(position < len(events) and events[position][1] in allowed, "event_grammar")
        item = events[position]
        position += 1
        return item

    def peek():
        return events[position][1] if position < len(events) else None

    take((11,))
    take((13,))
    missing_baseline_end = peek() != 14
    _require(not missing_baseline_end or participant == "sub-10", "baseline_end_missing")
    if not missing_baseline_end:
        take((14,))
    trials, conditions, observed_intervals = [], [], []
    ancillary = {"attention_question_events": 0, "attention_answer_events": 0,
                 "unpaired_attention_questions": 0, "unpaired_attention_answers": 0,
                 "missing_inter_run_rest_tags": 0}
    for run in range(1, 6):
        take((15,))
        condition = take((21, 22, 23))[1]
        conditions.append(condition)
        for _ in range(40):
            start = take((42,))[0]
            cue, code = take((31, 32, 33, 34))
            action, relax, rest = (take((mark,))[0] for mark in (44, 45, 46))
            intervals = (cue - start, action - cue, relax - action, rest - relax)
            _require(0 < intervals[0] <= 5 * SFREQ and
                     384 <= intervals[1] <= 3 * SFREQ and
                     2 * SFREQ <= intervals[2] <= 4 * SFREQ and
                     0 < intervals[3] <= 3 * SFREQ, "trial_timing")
            observed_intervals.append(intervals)
            trials.append(Trial(code - 31, condition, start, cue, action, relax, rest, run))
            pending_question = False
            while peek() in (17, 61, 62, 63, 64):
                attention_code = take((17, 61, 62, 63, 64))[1]
                if attention_code == 17:
                    ancillary["attention_question_events"] += 1
                    ancillary["unpaired_attention_questions"] += int(pending_question)
                    pending_question = True
                else:
                    ancillary["attention_answer_events"] += 1
                    ancillary["unpaired_attention_answers"] += int(not pending_question)
                    pending_question = False
            ancillary["unpaired_attention_questions"] += int(pending_question)
        take((16,))
        if run < 5:
            if peek() == 51:
                take((51,))
            else:
                ancillary["missing_inter_run_rest_tags"] += 1
    take((12,))
    _require(position == len(events), "trailing_events")
    expected = [21, 22, 22, 23, 23]
    _require(conditions == expected or
             (participant == "sub-03" and conditions == [21, 22, 23, 23, 23]), "condition_layout")
    corrected = participant == "sub-03" and conditions == expected
    if corrected:
        trials = [replace(trial, condition=23) if trial.run_ordinal == 3 else trial
                  for trial in trials]
    if summary is not None:
        summary.update(trials=200, runs=5, baseline_end_missing=missing_baseline_end,
                       **ancillary,
                       condition_correction_applied=corrected,
                       condition_correction_already_present=participant == "sub-03" and not corrected,
                       inferred_target_count=0, synthesized_event_count=0,
                       interval_timing={name: {
                           "minimum_seconds": min(row[index] for row in observed_intervals) / SFREQ,
                           "maximum_seconds": max(row[index] for row in observed_intervals) / SFREQ,
                           "nominal_seconds": NOMINAL_INTERVALS[index],
                           "deviation_over_0_1s_count": sum(
                               abs(row[index] / SFREQ - NOMINAL_INTERVALS[index]) > .1
                               for row in observed_intervals)}
                           for index, name in enumerate(INTERVAL_NAMES)})
    return trials
