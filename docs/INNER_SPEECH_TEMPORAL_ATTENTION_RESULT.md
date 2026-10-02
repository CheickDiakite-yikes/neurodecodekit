# Fixed temporal EEG features did not improve imagined word decoding

October 2, 2026. The corrected, fixed experiment completed and scored once in
**252.13 seconds**, retaining **1,994 trials**, all ten people, all three
conditions and all thirteen arms. **The primary test failed, cue sensitivity
failed, and progression failed.** This is a scientific negative result, not an
execution failure.

The [complete aggregate](../registries/inner_speech_temporal_attention_result.v0.json)
retains all calibrated and uncalibrated comparisons, participant results,
confusion matrices, null controls and qualification evidence. No score was
repeated and no model or threshold was changed after seeing results.

## Primary result

Positive log-loss gain means the joint temporal model is better than its
comparator. Values below are equal-participant means of class-macro log-loss
contrasts, in nats, for inner speech.

| Comparator | Joint temporal gain | People with positive gain |
| --- | ---: | ---: |
| Peripheral/timing only | -0.006061 | 2/10 |
| Joint spectral | -0.008322 | 4/10 |
| Joint EEG deranged | -0.003434 | 4/10 |
| Joint labels shuffled | 0.001645 | 4/10 |
| Uniform | -0.012496 | 0/10 |
| Training prior | 0.014259 | 9/10 |

**Zero of ten people** beat every primary control; nine were required. The
mean gain over peripheral/timing alone was **−0.006061 nats**, against a required
+0.020000, and gain over the matched spectral comparator was **−0.008322 nats**,
which had to be positive. Joint inner-speech balanced accuracy was **22.15%**,
versus 25% for uniform. Beating the weaker training-prior baseline does not
override losing to uniform and the other controls.

The separate cue EEG sensitivity endpoint also failed: **4/10** people beat all
three controls, versus nine required. Mean gains were **+0.009220 nats** against
uniform (at least +0.020000 required), **+0.012320** against the cue label-null,
and **+0.035974** against the training prior. The positive mean cue comparisons
do not satisfy the prespecified consistency and effect-size requirements.

## All conditions and controls

These are equal-participant mean balanced accuracies, not pooled trial
accuracies. There were 798 inner-speech, 397 pronounced and 799 visualization
trials. Secondary comparisons cannot rescue the primary.

| Arm | Inner speech | Pronounced | Visualization |
| --- | ---: | ---: | ---: |
| Peripheral/timing only | 21.67% | 68.56% | 28.67% |
| Joint temporal | 22.15% | 65.56% | 26.53% |
| Joint spectral | 22.04% | 67.00% | 27.90% |
| Joint EEG deranged | 20.80% | 60.69% | 23.80% |
| Joint labels shuffled | 26.04% | 20.14% | 23.41% |
| Action EEG only | 23.28% | 35.69% | 21.52% |
| Action EEG labels shuffled | 25.69% | 19.86% | 24.55% |
| Cue EEG only | 27.29% | 20.92% | 28.65% |
| Cue EEG labels shuffled | 21.77% | 19.08% | 23.53% |
| Joint cue window | 24.16% | 65.03% | 31.78% |
| Joint late window | 22.28% | 64.50% | 25.91% |
| Training prior | 17.14% | 10.33% | 17.26% |
| Uniform | 25.00% | 25.00% | 25.00% |

Pronounced peripheral/timing prediction exceeds the joint model (68.56% versus
65.56%). Pronounced action EEG-only accuracy is 35.69%, but EEG-channel
predictability during overt speech is not proof of cortical origin. Inner
action EEG-only accuracy is 23.28%; its log-loss loses to uniform in every
participant. Thus the negative conditional result is not explained merely by
withholding an EEG-only arm. Visualization and cue-window positives remain
secondary observations, not evidence of imagined-content recovery.

## Belief update and next priority

This result weakens the hypothesis that these fixed ordered signed bin means
provide a reliable imagined-word advantage over matched spectral EEG and
peripheral/timing controls. It does not establish an EEG ceiling, eliminate
other representations, or demonstrate an inability to decode thought in
principle. The original spectral session-1 result was also negative, but these
are different sessions and specifications; do not treat their score difference
as a clean causal estimate of improvement.

**Stop advancing the signed-bin model or confirming it on session 3.** The
progression rule failed. Do not tune or rescore consumed sessions 1 or 2.

The next proposed measurement is one preregistered **beta-envelope sensitivity
and attribution experiment** on untouched, separately authorized evidence:
fixed 12–24 Hz amplitude trajectories against whole-window beta power,
independently time-scrambled envelopes per trial, matched peripheral trajectories
and timing, and label-null controls. Use the same time permutation across
channels within each trial, fit preprocessing only on training data, and prevent filters
from borrowing cue, neighboring-trial or held-out samples. Fix separate
measurement-sensitivity and imagined-content endpoints before access. No band,
window, model or participant search is proposed.

Reject useful ordered-envelope information if there is no held-out increment
or if the claimed ordering advantage survives temporal scrambling. A positive
result would support useful time-locked information, not cortical language
origin or cue-independent thought. This is a genuinely different measured
quantity from signed bin averages, not permission to reopen the consumed runs.
Source selection, a bounded protocol and fresh approval are still required;
**no further experiment or acquisition is authorized or launched**.

The longer-term thought-to-text milestone remains recoverable content not
already supplied by an external prompt, followed by untouched word/day transfer.
The present prompted four-word task cannot establish that milestone, arbitrary
text, unseen-person generalization, prospective live use or clinical utility.

## Execution and verification

The sole correction accepted the audited session-2 question/answer pair after
intact observed start/cue/action/relax and before the next observed start;
rest stayed absent. All ten full ordered decoder comparisons and all thirty
split preflights passed before physiology. Six originally indexed core-incomplete
slots were excluded under the unchanged limits; no labels or timestamps were
inferred, and all people and conditions remained.

Implementation `d72d107e7fb61288e1f1dc75a6ff95999578a809` passed 65 focused
generated tests, Ruff and both
[remote CI suites](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37035167107)
before launch. The complete thirty-pair prediction freeze
`e1defd5bb97e0b6d37fd550e7f5f56e0ab6fd710` was pushed and verified on remote
main before the single score. Total elapsed time includes qualification,
prediction, freeze commit/push and scoring; peak RSS was 119,648,256 bytes.
The unchanged experiment performed 5,280 ridge fits and 1,320 temperature
calibrations, with no held-out scoring during prediction.

Both [freeze-commit CI suites](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/37036632228)
also passed before publishing this result.

Local and public aggregate SHA256:
`5a354cb2944a192ee98eee8876e37701a52926e37a5399a6d97c4c06fcb0523b`.
Prior failed attempts and completed audits remain unchanged. Raw recordings,
event rows, targets, per-trial predictions and weights were not uploaded.
Aggregate-only independent validation verified every reported balanced accuracy
against its confusion matrix, the primary contrasts and sign tests, and the
complete condition/control roster. Secondary positives remain separate from
the failed progression decision.
