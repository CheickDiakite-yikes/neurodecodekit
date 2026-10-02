# Next test: temporal information on fresh recordings, not a rescue of session 1

October 2, 2026. The maintainer approved continuing toward a fixed time-resolved
EEG test. This records the source decision and proposed scope; it is not a
completed experiment or a substitute for the additional acquisition decision.

## The discriminating question

Does keeping the order and sign of EEG waveform activity recover useful
imagined-word information that whole-window spectral power missed? A compact
temporal model and the fixed spectral comparator must run on the **same new
trials**, with matched peripheral/timing and null controls. Comparing a new
session's temporal score with session 1's spectral score would confound the
representation with the recording session.

Use one prespecified representation: 32 ordered signed bin means per EEG
channel after EEG-only common-average reference and per-window channel demean.
The two-second action window gives 64 samples per bin; the 384-sample cue
window gives 12. This is a 4,096-feature representation of time-locked waveform
structure, not a claim to test every temporal model. Reuse the small dual-ridge
model and training-only scaling/calibration; no architecture or band search.
Peripheral inputs must receive a matched temporal representation as well, so
EEG cannot win merely because its comparator discarded all temporal detail.

Retain P-only, temporal joint, cue and matched-late views, EEG derangement,
label shuffle, uniform and training-prior controls. Add EEG-only sensitivity
arms and the same-trial spectral joint comparator. Exact arm definitions,
session-specific eligibility and progression thresholds must be fixed and
validated before physiology. Cue success only demonstrates sensitivity to a
recorded response, not cortical attribution or imagined-word content.

## Fresh source, explicitly development-only

The [public metadata selection](../registries/inner_speech_session2_source_selection.v0.json)
pins all ten **ses-02** BDF identities in ds003626 v2.1.2 at source commit
`d96743351ae4e5d0ee7a1384320ea8d52a2ce698`. The ten Git-annex pointers total
**6,870,116,352 bytes (6.3983 GiB)**. Raw BDFs preserve EEG and peripheral
channels; no derivative or participant substitution is proposed.

The [published protocol](https://pmc.ncbi.nlm.nih.gov/articles/PMC8844234/)
describes 200 nominal trials per person in sessions 1 and 2 and variable counts
in session 3. These are consecutive sessions on the **same day**: neither a
new-day nor an unseen-person claim is available. Actual session-2 geometry,
event completeness, exclusions and split eligibility remain unverified.
Session-1 corrections and its seven-exclusion allowance do not transfer by
assumption.

Only the consumed first-session acquisition is currently local. Proposed
acquisition is **session 2 only**, at most 60 minutes and 10 GiB, one worker,
1 GiB RSS, 32 MiB generated metadata and at least 20 GiB free disk. Preserve
all raw files outside OneDrive; no automatic retry or partial-cohort rescue.
Metadata-only object-version checks must precede acquisition. The old exact
acquisition cannot be reused or resumed for this new slice.

After separately approved acquisition and frozen generated validation, one
development experiment would have a 20-minute total numerical/freeze/scoring
cap, 1 GiB RSS, 32 MiB generated output, one worker and one scoring invocation.
It must report every person, condition and control, including failed sensitivity
checks. A successful result only motivates a later untouched confirmation.

**Session 1 remains consumed. Session 3 remains unopened and unacquired.**
No real-data access, fitting or scoring occurred during this source selection.
New-data acquisition and the exact development exposure are awaiting the
explicit 6.40-GiB/60-minute plus one 20-minute run decision presented to the
maintainer. Future session-3 confirmation is not included in that request.

## Prior-result closure

Both remote CI jobs on result commit
`70a9972da636b610a04460b9bccab2ef064091b8` passed
([workflow](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37015448321)).
The [negative result](INNER_SPEECH_OBSERVED_RESULT.md) is unchanged; this source
selection creates no new performance claim and does not reopen its score.
