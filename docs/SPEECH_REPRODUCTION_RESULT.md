# Minimally overt task-label prediction reproduces; EEG's added value does not pass the controls

September 21, 2026. **SPEECH-REPRO-1 completed and scored once.** The minimally
overt EEGNet reference reached **52.49% equal-person balanced accuracy**, above
the five-class 20% baseline in every participant. But the auxiliary-only model
reached **84.83%**, and adding filtered EEG **failed the registered conditional
test**. Covert reference performance was **18.13%**; its joint EEG-plus-auxiliary
comparator also failed the full conditional test. This is a result about
release-label prediction and attribution, not a demonstration of thought decoding.

## Complete result, including the negative endpoints

All three people, both conditions, all nine arms and all 341 evaluation trials
were retained: 191 minimally overt and 150 covert, after 600 calibration trials.
All six person/condition endpoints contain all five classes; none is incomplete.
Numbers below weight people equally after pooling their associated online runs.
Balanced accuracy (BA) averages recall across the five classes; class-macro log
loss (LL, natural-log units) measures probability predictions, with lower better.
`N` is the joint display, microphone, eye, upper/lower-lip and timing bundle.

| Frozen arm | Minimally overt BA | Minimally overt LL | Covert BA | Covert LL |
|---|---:|---:|---:|---:|
| N only | 84.83% | 1.240702 | 24.16% | 1.588576 |
| N + raw EEG | 85.95% | 1.247039 | 27.61% | 1.595622 |
| **N + filtered EEG (primary)** | **87.47%** | **1.263215** | **31.23%** | **1.586054** |
| N + pre-action EEG | 81.67% | 1.285283 | 26.69% | 1.582747 |
| N + deranged EEG | 84.10% | 1.282731 | 23.13% | 1.589826 |
| Shuffled-calibration-label joint model | 22.53% | 1.613697 | 18.45% | 1.628926 |
| Uniform | 20.00% | 1.609438 | 20.00% | 1.609438 |
| Training-word prior | 20.00% | 1.653511 | 20.00% | 1.688099 |
| EEGNet reference (filtered EEG only) | 52.49% | 1.206894 | 18.13% | 1.870178 |

The [unaltered aggregate result](../registries/speech_reproduction_result.v0.json)
contains every participant metric, ordinary accuracy, class count and comparator
edge at full precision. No arm, null result or unfavorable comparison is omitted.

### The primary conditional claim fails; higher accuracy cannot replace it

The preselected endpoint is comparator LL minus primary LL, not accuracy.
For minimally overt speech, adding filtered EEG to N gives **-0.022513** mean
gain: LL worsens. Gains for people 1/2/3 are **-0.042133, -0.034950, +0.009543**.
Only one person improves. The mean BA gain of **+2.64 percentage points** is real
descriptively, but cannot rescue this endpoint or the all-person rule. BA changes
are -1.74, -1.11 and +10.76 percentage points: the average gain comes from person 3.

| Log-loss improvement: comparator LL - primary LL | Minimally overt mean | Positive people | Covert mean | Positive people |
|---|---:|---:|---:|---:|
| N only | -0.022513 | 1/3 | +0.002522 | 3/3 |
| N + raw EEG (interpretation comparison) | -0.016176 | 1/3 | +0.009569 | 3/3 |
| N + pre-action EEG (interpretation comparison) | +0.022068 | 3/3 | -0.003307 | 1/3 |
| N + deranged EEG | +0.019516 | 3/3 | +0.003772 | 2/3 |
| Shuffled-calibration-label joint model | +0.350483 | 3/3 | +0.042872 | 3/3 |
| Uniform | +0.346223 | 3/3 | +0.023384 | 1/3 |
| Training-word prior | +0.390296 | 3/3 | +0.102045 | 3/3 |

The minimally overt primary beats derangement, shuffled labels, uniform and
training prior in every person, but not N alone. Covert gains over N are small
and positive in all three people (**+0.000274, +0.001729, +0.005564**), but person
2 loses to derangement and people 2/3 lose to uniform in LL. Thus **neither
condition meets the registered conjunction**. Pre-action is better than the
covert primary on mean LL; its shorter, preparation/cue-containing window is
not a signal-free null. Raw and pre-action comparisons are outside the success
conjunction, as fixed before scoring.

### The reference succeeds only for minimally overt speech

| Condition / person | Reference accuracy | Reference BA | Published participant BA | Difference |
|---|---:|---:|---:|---:|
| Minimally overt / 1 | 63.74% | 60.01% | 68.5% | -8.49 pp |
| Minimally overt / 2 | 50.00% | 44.55% | 56.4% | -11.85 pp |
| Minimally overt / 3 | 54.00% | 52.90% | 41.8% | +11.10 pp |
| Covert / 1 | 28.00% | 22.32% | 18.8% | +3.52 pp |
| Covert / 2 | 16.00% | 12.62% | 18.4% | -5.78 pp |
| Covert / 3 | 26.00% | 19.45% | 26.5% | -7.05 pp |

Equal-person reference ordinary accuracy is 55.91% minimally overt and 23.33%
covert. The minimally overt all-person BA-above-20% criterion passes; covert
does not. These are descriptive, not significance tests. The published rows
are context, not matched-session targets: our earliest-session selection and
documented implementation deviations differ from the paper's repeated-session
coverage. Do not equate our 52.49% with its differently weighted 52.1% average.
Published values and the weighting caveat are recorded in the
[pre-score execution document](SPEECH_REPRODUCTION_EXECUTION.md).

## What changes in our belief, and what we do next

**We now have a positive reference for minimally overt task-label prediction,
but no demonstrated EEG increment under the fixed conditional test.** Strong
accuracy is plainly available from the measured auxiliary bundle without EEG
features. This makes attribution and cue identifiability more urgent than
another model architecture. It does not prove that the EEG reference itself
uses the same information, that all EEG information is peripheral, or that
non-invasive neural communication is impossible.

The specific carrier of the auxiliary result is unresolved: display/cue
identity, timing, eye/lip activity, microphone or a mixture could contribute.
Joint-bundle results cannot identify individual modalities. Probability
calibration or model limitations might contribute to the BA/LL disagreement,
but this score does not diagnose either. EEGNet and the compact primary do not
have matched inputs; their comparison cannot establish an architecture ceiling.

**Next priority: identify which recorded modality carries the strong minimally
overt signal.** Propose a bounded, calibration-only discovery ablation separating
display/timing from microphone/lip/EOG and their combinations, with all tried
variants recorded. This is a proposed next experiment, not executed or newly
authorized by this closeout. Do not tune on or rescore these consumed online
trials. Any confirmatory follow-up needs a separately frozen, untouched
evaluation; a thought-content claim additionally needs cue-remapped or
counterbalanced targets, independently recorded intention and matched controls.
If display/timing carries the prediction, prioritize task redesign. If measured
speech-related physiology carries it, investigate explicitly multimodal utility
without relabeling it cortical decoding.

Three known participants, sparse class counts, fixed cues, partial peripheral
coverage and offline historical recordings sharply limit inference. The smallest
one-sided person-level sign-flip p is 0.125; no population significance is
claimed. Neither reference success nor a future conditional gain alone proves
cortical origin, cue-independent thoughts, unseen-person transfer, arbitrary
text, clinical utility or prospective live operation.

## Execution integrity

Implementation `29d1f10f04aebb9e2ec972a7cb8fa7e626f82832` passed both remote CI
jobs before invocation. All six pairs and ten 100-epoch folds per pair completed:
50 preserved fits were reused and ten newly trained. Predictions finished in
1,277.61 seconds; total wall time through the sole scorer was **3,896.94 seconds
(64.95 minutes)**, including waiting for the hourly monitor and freeze push,
within the approved 7,200 seconds.

The [complete prediction freeze](../registries/speech_reproduction_prediction_freeze.v0.json)
was committed and remotely verified at
`dd3b3dccb637ec26ecf8f32ab134388923b3c561` before targets were released. Scoring
exited successfully; the one-use marker exists and no execution-failure marker
exists in the corrected root. Both earlier failed roots remain untouched.
No scientific code changed between prediction generation and scoring, no
partial evaluation or second score occurred, and no raw data, individual labels,
probabilities or weights were uploaded.

Aggregate-only independent review checked 228 identities, counts, means,
differences and decision-conjunction conditions with zero discrepancies; this
did not reopen predictions or targets. Result SHA-256:
`5ca61ce244d9d7ed65ba6a3cebd65b0af49a4782979a8b834008553329087d8c`.
