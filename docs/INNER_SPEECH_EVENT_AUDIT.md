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

## Observed result

The single approved audit completed in **4.25 seconds**, with **42,467,328
bytes (40.50 MiB)** peak RSS, using `bd2c830f21b267ea3575a99e6c526777a1e8d624`
after both remote CI jobs passed (workflow `36582699440`). The source SHA-256
matched. The failed scientific attempt and frozen code stayed unchanged;
there was no audit-failure marker. The
[complete sanitized aggregate](../registries/inner_speech_event_audit_result.v0.json)
contains the observations, including all collapsed event-family totals.

**Exact refusal:** after three fully parsed trials in the first run, the
unchanged parser expected a **rest** marker and instead encountered the next
**trial start**. The fourth trial therefore failed its mandatory trailing-rest
check. This is not a recording-initial event or protocol-start mismatch.

Across the decoded stream there are **200 trial starts, 200 direction cues,
200 action markers and 200 relax markers, but 199 rest markers**. There are
1,112 retained events and zero ignored short pulses. The absence is in the
frozen reader's decoded stream; this audit did not independently validate the
raw Status interpretation against the author's reader. Aggregate counts alone
do not prove that every later trial is intact or that the source is corrupt.

No physiological windows were decoded, no model was fit, and no prediction or
score was produced. Opaque bytes from the full recording were hashed, and
Status codes (including target-bearing codes) were read inside the diagnostic;
only collapsed categories were exported. Do not call labels unopened.

## Belief update and next boundary

The obstacle is now a specific mandatory-marker mismatch, not an unidentified
event failure. There is no observed shortage of direction-cue markers in the
aggregate. **This does not change our belief about EEG decoding accuracy or
thought-to-text feasibility.** The data-quality finding blocks the registered
scientific test; it is not its primary-endpoint result.

Do not drop the fourth trial, invent a rest timestamp, disable initial events,
or silently make rest optional. The current model uses rest-relative timing
features and the parser checks a rest-bounded interval, so accepting missing
rest would require an explicit protocol amendment, not just an unchanged
implementation retry. The next decision must preserve all participants and
targets, account for any removed or replaced timing feature in every arm, and
qualify complete event sequences before fitting. This audit is consumed; no
further data access or scientific run follows automatically.

## Recommended successor, not yet authorized

The pinned author's [event correction](https://github.com/N-Nieto/Inner_Speech_Dataset/blob/65bd162a32f38546b6596cb25d46f4a862fa87fb/Python_Processing/lib/events_analysis.py)
explicitly handles a relax marker not followed by rest, inserting an estimated
rest marker. Thus the public pipeline anticipates this omission pattern; our
strict no-synthesis parser does not. This is supporting implementation evidence,
not independent verification of this recording's raw Status decoding.

Recommended amendment: admit only an otherwise intact trial's `relax -> next
trial_start` omission, keeping all direction/action/relax anchors observed and
all EEG windows unchanged. Preserve observed rest-dependent timing values;
encode an unavailable feature as fixed zero plus its availability flag. Apply
this to both the affected trial's rest-minus-relax value and the next trial's
start-minus-previous-rest value, identically across all relevant arms. This is
explicit feature-level missing-value encoding, not a synthesized event,
timestamp or target. P changes from **85 to 87 features**, including changed
block normalization; train-only scaling remains mandatory. A missingness
pattern absent from training cannot acquire a learned correction.

Retain every other event/timing check and report the unavailable rest-bounded
checks as unavailable, not passed. Qualify all ten people before any fitting;
refuse other missing or ambiguous required markers. Freeze this as a new
protocol and attempt, preserving both old failures and this consumed audit.
Keep all participants, trials, conditions, model settings, eight arms, decision
rules and the 20-minute/1-GiB cap. No new run is authorized here. This option
preserves observed nuisance information better than deleting the two timing
features, but is not equivalent to the original frozen comparison.
