# One decisive fresh-cohort imagined-word test

September 22, 2026. Protocol prepared before event labels or outcomes are opened.
Execution needs explicit approval of this complete study; acquisition approval
alone does not grant scoring. No real-data execution has occurred under this plan.

## Question and decision

Does recorded EEG improve held-out probabilities for four instructed inner-speech
words beyond a strong fixed eye/lip/reference-channel and timing model?

The [machine protocol](../registries/inner_speech_test_plan.v0.json) retains all
ten first-session participants and all three conditions. Expected source scope
is 2,000 trials: 760 inner speech, 400 pronounced and 840 visualization, accounting
for the published participant-03 condition correction. These are prospective
expectations, not observed event counts.

Primary success requires mean participant class-macro log-loss improvement of
at least **0.02 nats** over the peripheral/timing model, with the **same nine or
more of ten people** improving against *every* primary comparison: peripheral
only, misaligned EEG, shuffled labels, uniform and training prior. Report exact
one-sided sign tests separately; nine positives gives 11/1024. This conjunction
tests consistency, not a confidence bound on the mean effect or clinical utility.
Balanced accuracy and every negative or null result remain visible. Neither
pronounced nor visualization results can rescue a failed inner-speech primary.

## Minimal comparison

Use the final two seconds before the actual relaxation event, wholly inside the
tagged action interval. EEG uses EEG-only common-average reference and fixed
FFT band powers. Peripherals use all eight EXG channels referenced only within
their own branch, plus three eye/lip bipolar differences, fixed wider-band
powers, variance and non-identifying timing. No peripheral-driven EEG cleaning,
directional cue identity, language-model generation or model/band search.

Eight arms: P, P+EEG, P+cue EEG, P+matched late EEG, P+misaligned EEG, joint
shuffled labels, uniform and training prior. Cue and matched late windows are
384 samples each (0.375 seconds); they are explanatory comparisons, not proof
of cue independence. Their frequency resolution is 2.667 Hz, not 1 Hz.

Four contiguous whole-trial outer folds within each participant/condition;
one-original-trial embargo at outer and inner boundaries; three remaining
outer blocks supply inner calibration folds. This is retrospective same-session
validation, not forward prediction or unseen-person model transfer. Fixed
ridge alpha 1, training-only scaling, and identical nested positive-temperature
calibration opportunities for all six learned arms. No alternate folds if a
training class is absent: retain four output columns, learn from available
training labels and report class support. All four words must exist globally
in each participant/condition for the four-word endpoint.

The machine protocol specifies Hann-energy normalization and the float64 floor
for spectral/variance logarithms. Positive calibration retains every top-choice
word; exact ties caused solely by floating-point rounding may restore the
original winner by one ULP under a fixed four-ULP lost-gap bound. Count each
correction and refuse any strict order reversal. Generated tests exercise this
case; it is not an outcome-driven calibration change.

## Source handling and stopping

Qualify every participant's event sequence before any fitting. No missing-word
imputation, dropped trials/participants, condition substitution or partial score.
Apply the published participant-03 third-run correction prospectively. Apply
the author's 2 ms short-trigger rule only to participant 10; count the ignored
pulses and any missing unused baseline-end tag, without inventing events.
Unused attention-question/answer tags can be unpaired only between complete
trials; an inter-run rest tag may be missing only between intact run boundaries.
Count these ancillary omissions without inferring attention correctness or
repairing any trial, direction, condition or action boundary.

The paper and newer author MATLAB disagree on nominal interval durations.
Use actual event anchors with the fixed broad admission bounds in the protocol;
report deviations from published nominal timing rather than treating those
unverified timer assumptions as labels or changing windows after observation.
Ambiguous sequence, target, condition, identity or unsafe window geometry stops
the entire attempt. This is a new attribution test, not an exact timing reproduction.

One prediction pass, then commit/push its hash freeze before **one** score.
No tuning or automatic recovery after any failure. Cap the complete prediction,
freeze publication and scoring at **20 minutes, 1 GiB RSS and 32 MiB generated
output**, with one numerical worker and at least 20 GiB disk free. No new data
downloads. Raw data, event rows, targets and per-trial predictions remain in
local AppData outside OneDrive; only hashes and aggregate results enter Git.

Implementation checks before participant access: 26 generated-only tests passed
in 2.514 seconds, including all 30 scoring pairs, temporal leakage guards,
source-event refusals, and one-shot consumption before target loading. Ruff is
clean; the default dry run opens zero participant files. These checks validate
implementation, not a scientific outcome or the runtime on real recordings.

## What either result would mean

A positive primary supports incremental recorded-EEG prediction under this
specific four-word, same-day, personalized laboratory task. It motivates a
changed-cue/new-day test. A negative primary redirects the method or measurement
question; secondary winners do not reverse it. Neither establishes cortical
origin, inner-speech specificity, cue-independent thoughts, arbitrary text,
new-day robustness, prospective live operation or clinical utility.

Sources: [dataset paper](https://www.nature.com/articles/s41597-022-01147-2),
[pinned author code](https://github.com/N-Nieto/Inner_Speech_Dataset/tree/65bd162a32f38546b6596cb25d46f4a862fa87fb),
[verified local acquisition](INNER_SPEECH_ACQUISITION.md).
