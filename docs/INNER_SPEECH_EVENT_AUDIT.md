# Locate the event mismatch, without changing the experiment

September 29, 2026. The maintainer approved a bounded event-structure-only
audit and publication of the sanitized qualification-failure summary to the
existing project repository. This does not authorize a new decoding run.

The diagnostic is `scripts/audit_inner_speech_events.py`; its default is a
no-data dry run. It reuses the frozen reader and parser, without modifying
`INNER-SPEECH-TEST-1` or its failed local attempt.

- Scope: first participant, first session, pinned ds003626 v2.1.2 recording.
- Verify the acquired SHA-256 by hashing opaque file bytes; validate the BDF
  header; decode only the Status channel, never EEG/EXG windows.
- Call the unchanged parser exactly once on the original event list. No
  filtering, alternative parse, label inference, trial repair or retry.
- Export only collapsed event-family totals, the first failing structural
  state, completed-trial/run counts and technical resource/identity metadata.
  Direction, condition and attention-answer identities stay collapsed; unknown
  numeric words, sample positions, timestamps and source rows are not exported.
- Maximum 120 seconds, 256 MiB RSS, 64 KiB aggregate output, one numerical
  thread; separate exclusive local output outside OneDrive. A watchdog enforces
  time/memory limits, with mutually exclusive completion/failure publication.
- No physiological feature computation, fitting, predictions or scoring. The
  failed attempt's start/failure marker and frozen code fingerprints must remain
  unchanged. Any initialized audit is consumed; no automatic retry.

Generated tests check refusal-position projection, target-category collapsing,
absence of unknown numeric words, unchanged inputs, one parser call, explicit
EOF/non-grammar failures and intact-event success. This establishes diagnostic
behavior, not source compatibility or neural information.

The public author pipeline explicitly uses `initial_event=True`; omitting an
initial event is not automatically source-faithful. It uses MNE's 17-bit BDF
mask followed by removal of exact acquisition-only events, while our reader
masks to 16 bits before transition detection. These semantic differences are
hypotheses to interpret only after the audit; they are not proof of its cause.
Sources: [pinned author extraction code](https://github.com/N-Nieto/Inner_Speech_Dataset/blob/65bd162a32f38546b6596cb25d46f4a862fa87fb/Python_Processing/lib/data_extractions.py#L282-L295),
[author event validation](https://github.com/N-Nieto/Inner_Speech_Dataset/blob/65bd162a32f38546b6596cb25d46f4a862fa87fb/Python_Processing/lib/events_analysis.py#L17-L31),
[pinned MNE BDF implementation](https://github.com/mne-tools/mne-python/blob/v0.22.0/mne/io/edf/edf.py#L288-L290).

Next decision: use the observed structural mismatch to propose the smallest
source-supported correction, if justified. No data repair or scientific run
is authorized by this diagnostic, and no diagnostic result is a biological null.
