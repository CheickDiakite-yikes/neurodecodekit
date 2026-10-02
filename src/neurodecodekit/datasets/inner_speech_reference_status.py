"""Independent, bounded pre-repair author/MNE Status semantics.

Only header geometry and the identity-checked file opener are shared with the
frozen BDFReader. Byte decoding, transitions and duration handling are separate.
Returned sample/code pairs are private: callers may export agreement facts only.
No physiological channel, author correction, or missing-event inference is used.
"""

from neurodecodekit.datasets.inner_speech import InnerSpeechRefusal


AUTHOR_COMMIT = "65bd162a32f38546b6596cb25d46f4a862fa87fb"
MNE_VERSION = "0.22.0"
SOURCE_URLS = (
    f"https://github.com/N-Nieto/Inner_Speech_Dataset/blob/{AUTHOR_COMMIT}/Python_Processing/lib/data_extractions.py#L282-L295",
    f"https://github.com/N-Nieto/Inner_Speech_Dataset/blob/{AUTHOR_COMMIT}/Python_Processing/lib/events_analysis.py#L112-L134",
    "https://github.com/mne-tools/mne-python/blob/v0.22.0/mne/event.py#L316-L480",
    "https://github.com/mne-tools/mne-python/blob/v0.22.0/mne/event.py#L640-L678",
    "https://github.com/mne-tools/mne-python/blob/v0.22.0/mne/io/edf/edf.py#L288-L290",
)
STATUS_MASK = (1 << 17) - 1
OVERFLOW_ONLY = 1 << 16
SFREQ = 1024
MAX_STEPS = 100000
CORE_CODES = frozenset((31, 32, 33, 34, 44, 45))
CONTEXT_CODES = frozenset((15, 16, 21, 22, 23))


def _require(condition, code):
    if not condition:
        raise InnerSpeechRefusal(code)


def _status_steps(records, samples_per_record, check):
    """Decode one Status record at a time, retaining only bounded transitions."""
    steps, initial, previous, sample = [], None, None, 0
    for payload in records:
        if check is not None:
            check()
        _require(len(payload) == 3 * samples_per_record, "reference_status_truncated")
        octets = memoryview(payload)
        for offset in range(0, len(octets), 3):
            # Signed-24 decode followed by &0x1ffff has these same low bits.
            # BDF stim channels bypass physical calibration in MNE 0.22.
            value = (octets[offset] | (octets[offset + 1] << 8) |
                     ((octets[offset + 2] & 1) << 16))
            if initial is None:
                initial = value
            elif value != previous:
                steps.append((sample, previous, value))
                _require(len(steps) <= MAX_STEPS, "reference_transition_limit")
            previous, sample = value, sample + 1
    _require(initial is not None, "reference_empty_status")
    return steps, initial, sample


def _onsets(steps, initial, n_samples, *, minimum_duration):
    """Reproduce MNE 0.22 step merging, then onset and shortest-event handling."""
    steps = list(steps)
    # Source _find_stim_steps returns immediately when no transition exists;
    # therefore a wholly constant nonzero recording has no paired event.
    if steps and steps[-1][2] != 0:
        steps.append((n_samples, steps[-1][2], 0))
    if minimum_duration and steps:
        # .002 * 1024 = 2.048 => merge=2. This is a simultaneous assignment
        # using ORIGINAL preceding values, not iterative pulse deletion.
        close = [right[0] - left[0] <= 2 for left, right in zip(steps, steps[1:])]
        merged = []
        for index, (sample, before, after) in enumerate(steps):
            if index and close[index - 1]:
                before = steps[index - 1][1]
            if (index == len(steps) - 1 or not close[index]) and before != after:
                merged.append((sample, before, after))
        steps = merged
    if initial:
        steps.insert(0, (0, 0, initial))
    steps = [step for step in steps if step[1] != step[2]]
    onsets = [i for i, step in enumerate(steps) if step[2] > 0]
    offsets = [i for i, step in enumerate(steps) if step[1] > 0]
    if not onsets or not offsets:
        return []
    if onsets[0] > offsets[0]:
        offsets.pop(0)
    _require(bool(offsets), "reference_orphan_offsets")
    if onsets[-1] > offsets[-1]:
        onsets.pop()
    events = [(steps[i][0], steps[i][2]) for i in onsets]
    # Author leaves shortest_event at the MNE default2. It tests onset gaps,
    # not every nonzero pulse width, and runs BEFORE dropping overflow-only.
    _require(all(b[0] - a[0] >= 2 for a, b in zip(events, events[1:])),
             "reference_shortest_event")
    return [(sample, code) for sample, code in events if code != OVERFLOW_ONLY]


def reference_status_events(reader, *, participant, check=None):
    """Private ordered (sample, code) pairs for the fixed ses-01 source route.

    Equivalent extraction settings: initial_event=True, consecutive=True,
    shortest_event=2, min_duration=.002 only for sub-10 (otherwise0). Retain
    17 bits before transitions, then remove exact65536 AFTER event extraction.
    Caller must keep this list private and refuse an anchor disagreement.
    """
    _require(participant in {f"sub-{i:02d}" for i in range(1, 11)},
             "reference_participant")
    _require(reader.sfreq == SFREQ and reader.channel_names[-1] == "Status" and
             reader.n_samples == reader.n_records * reader.samples_per_record,
             "reference_geometry")

    def records():
        # Do not call iter_status_events, _decode24, _read_channel or read_window.
        channel_offset = 3 * (len(reader.channel_names) - 1) * reader.samples_per_record
        with reader._open() as stream:
            for record in range(reader.n_records):
                stream.seek(reader.header_bytes + record * reader.record_bytes + channel_offset)
                yield stream.read(3 * reader.samples_per_record)

    steps, initial, n_samples = _status_steps(records(), reader.samples_per_record, check)
    _require(n_samples == reader.n_samples, "reference_incomplete_status")
    result = _onsets(steps, initial, n_samples, minimum_duration=participant == "sub-10")
    if check is not None:
        check()
    return result


def status_agreement(frozen_events, reference_events):
    """Compare identities/order/timestamps privately; return only two booleans."""
    def same(codes):
        return ([event for event in frozen_events if event[1] in codes] ==
                [event for event in reference_events if event[1] in codes])
    return {"core_events_match": same(CORE_CODES), "context_events_match": same(CONTEXT_CODES)}
