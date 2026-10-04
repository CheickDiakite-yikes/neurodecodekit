# SPEECH-REPRO-1 execution

**Outcome: stopped before evaluation.** After five completed pairs, the final
covert calibration recording failed event/trigger alignment. No scientific
score or decoding conclusion was produced. See the
[failure record and next priority](SPEECH_REPRODUCTION_EXECUTION_FAILURE.md).
The subsequent [label-blind audit](SPEECH_REPRODUCTION_TIMING_AUDIT.md) explains
the format misclassification and assesses checkpoint reuse; it does not resume
the failed run or change the fixed scientific settings below.

September 21, 2026. Continue the scientifically selected experiment in
[the September 6 decision](SPEECH_REPRODUCTION_RESEARCH_DECISION.md), not the
superseded July checkout. Its exact selection commit, `7554fc4`, has both
remote CI checks passing. No historical consumed evaluation is reopened.

The maintainer requested real scientific execution and frequent commits, then
explicitly authorized direct pushes to main. A target-free local CPU probe
showed the original two-hour estimate was not feasible on this computer.
After being shown that limitation, the maintainer explicitly approved:
**"Yes—run the complete experiment, up to six hours".** Only the total runtime
ceiling changes to six hours, including acquisition and scoring. The fifteen-
minute individual-stage ceiling, one numerical thread, four-GiB RSS limit,
1.5-GiB new research-payload budget, people, conditions, models and endpoints
remain unchanged. Raw data, individual labels, predictions and weights stay local.

## Pre-fit implementation clarifications

- The author's continuous trigger marks the end of a buffered trial, not the
  start of the action. Preserve its 2880-sample buffer reconstruction and
  one-sample repetition-centering convention in every action arm. Reject
  incomplete trials and irreconcilable event/trigger alignment.
- Preserve all 128 EEG channels, EEG-only 50/100-Hz notch, common-average EEG
  reference, all-signal 2–118-Hz bandpass, and bipolar auxiliary measurements.
  Reset adaptive filtering per trial. Pre-action filters see only the prefix
  ending before action, never future action samples.
- Ten nonshuffled stratified calibration folds follow the released code.
  Seed 20260906 governs model initialization, training order and jitter.
  Each fold saves its lowest true, sample-weighted validation cross-entropy;
  this corrects the author's validation accumulator bug. Select the four
  checkpoints by their calibration validation accuracy, as the released
  source does, with fold index breaking ties. This source-code choice differs
  from the manuscript's lowest-loss ensemble wording and is fixed before data.
- The source ensemble standardizes each model's five logits per trial and
  averages models. Softmax converts that mean to probabilities without
  changing the predicted class; these are not empirically calibrated probabilities.
- CPU channels-last layout is a computational implementation choice, not a
  changed model. A target-free comparison found maximum evaluation-logit
  difference below 1.9e-8. Measured speed still needs the approved longer run.
- The compact comparator uses exactly the frozen 8,960 EEG features and
  392 auxiliary/timing features. All scaling is learned from calibration.
  Within-recording trial derangement is independent of labels.

## Execution and interpretation

`scripts/run_speech_reproduction.py predict` downloads only the pinned 13 EDFs
and associated sidecars, verifies identities, trains the complete experiment,
and writes a hash-only prediction freeze. Commit and push that freeze before
`score --freeze-commit SHA` opens targets exactly once. A resource or source
failure produces no partial scientific score. The aggregate result must report
both speech conditions and every comparator, regardless of direction.

Published Table 2 participant balanced accuracies are 68.5%, 56.4%, 41.8% for
minimally overt speech and 18.8%, 18.4%, 26.5% for covert speech. These are
descriptive reference points, not matched-data replication targets: our fixed
selection uses each person's earliest session, while the paper includes repeated
sessions. Its displayed minimally-overt average of 52.1% is consistent with
counting participant 3's two sessions separately, not the 55.6% arithmetic mean
of its participant rows. Do not mix these weighting schemes.

Sources: [author code, pinned revision](https://github.com/arayabrain/uhd-gmail-public/tree/0dca00584c528b288392684dcec0d496b6aa4951),
[2024 preprint](https://doi.org/10.1101/2024.05.09.591996),
[primary manuscript Table 2](https://www.researchgate.net/publication/380933941_Delineating_neural_contributions_to_electroencephalogram-based_speech_decoding).
