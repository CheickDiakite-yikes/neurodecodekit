# Session 2 temporal experiment stopped before physiological analysis

October 2, 2026. The approved temporal-versus-spectral test produced **no EEG
result**. All ten session-2 recordings were acquired and verified, but the
single numerical attempt stopped after **20.80 seconds** during participant 3's
event qualification. No physiological windows, model fits, predictions or
scores were produced. Primary and sensitivity outcomes remain **not evaluated**,
not failed scientific endpoints.

## What stopped the test

The preserved refusal is `attention_requires_observed_rest`. The frozen parser
permits an attention question/answer only after an observed rest phase in the
current slot. The encountered sequence did not satisfy that rule. The failure
marker alone does **not** establish that a missing rest marker is the sole cause
or the only issue in this cohort. No event rows or word identities were reopened
to diagnose it after failure.

The complete-cohort gate runs before any physiological feature extraction.
Consequently this cannot be repaired by dropping participant 3 or scoring the
first two people. The attempt is consumed and remains immutable. There was no
automatic retry, rule relaxation, partial score or session-3 access.

## What was completed

The [acquisition receipt](../registries/inner_speech_session2_acquisition_result.v0.json)
records ten verified files, **6,870,116,352 bytes**, all original channels and
**883.78 seconds** (14.73 minutes), with zero retries or resumed files. Raw data
remain local outside OneDrive. The numerical attempt's peak recorded RSS was
47,419,392 bytes; it did not hit its time or memory limits.

The [sanitized failure record](../registries/inner_speech_temporal_failure.v0.json)
preserves the exact error, resource observations and hashes of the immutable
start/failure records. The experiment's fixed thirteen arms, all ten people and
three conditions were not changed to obtain a result.

Seventy-five focused generated tests and Ruff passed. Initial remote CI found
one test-only optional-NumPy error; the neuro-enabled suite passed. A two-line
test correction retained the independent pure-Python assertions, and both
remote suites then passed before acquisition at
`f73251e264f6c1e1cecf288c250a94c11ce896b0`
([workflow](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37022035546)).
The numerical attempt used that unchanged scientific code plus the complete
acquisition receipt at `7f96336721a4f0f22091f8152d56f6be550bbb64`.

## Belief update and next priority

**The temporal-information hypothesis is still untested.** Today's observation
changes our belief about event eligibility, not decoding ability: the prospectively
frozen session-2 event grammar does not cover every encountered sequence. The
earlier negative spectral result remains unchanged.

The next useful observation is one **all-ten, Status-only structural audit** of
the already downloaded session-2 files, capped at 120 seconds, 256 MiB RSS and
1 MiB of generated output. It should report event-family ordering and
completeness in aggregate, without word identities, inferred labels/timestamps,
EEG/EXG windows, model fitting or scoring. This can distinguish a narrowly
unsupported parser assumption from data that cannot support the fixed test,
while checking the whole cohort rather than discovering one exception per run.

That audit requires fresh approval and has **not** run. It does not authorize
a corrected numerical successor. No new download, model search or further
exposure of session 1 or session 3 is proposed. Data-quality review is the basis
for this bounded next step; it cannot substitute for a scientific result.
