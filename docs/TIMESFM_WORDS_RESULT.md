# TimesFM-3 on imagined-word EEG: tested, useful decoding not demonstrated

Three frozen applications of the official TimesFM-3 checkpoint were executed
locally on real ArEEG. The best accuracy was 22.33%, but no TimesFM method
demonstrated useful prediction beyond the no-signal controls. The word prior
had better average probability predictions than every TimesFM method.

This is a fresh **recording-level test**: 300 trials, twelve calibrated people,
25 trials per person and five per class. Training used 1,198 complete events
from sessions 0, 1, 3, 4; the new test used previously unacquired session 6.
Session numbering does not establish chronology or different recording days.
The old session-5 evaluation and session 2 were not reopened. This is one
exploratory cohort result, not independent confirmation or unseen-person transfer.

| Method | Balanced word accuracy | Class-macro log loss, lower is better |
|---|---:|---:|
| **TimesFM, joint electrodes** | **22.33%** | **1.7117** |
| TimesFM, separate electrodes | 17.00% | 1.8065 |
| TimesFM, forecast residuals | 19.33% | 2.5480 |
| Same-run covariance baseline | 20.33% | 4.7640 |
| Same-run raw temporal baseline | 19.67% | 2.6208 |
| **Training-only word prior** | **20.00%** | **1.6095** |
| Trial-position metadata | 18.00% | 1.8610 |
| Joint TimesFM, shuffled labels | 18.33% | 1.7520 |
| Joint TimesFM, Gaussian noise | 23.33% | 1.6454 |
| Separate TimesFM, shuffled labels | 18.00% | 1.7919 |
| Separate TimesFM, Gaussian noise | 17.67% | 1.6658 |
| Forecast residuals, shuffled labels | 19.33% | 2.6822 |
| Forecast residuals, Gaussian noise | 17.33% | 1.6862 |
| Covariance, shuffled labels | 20.00% | 4.5961 |
| Covariance, Gaussian noise | 20.67% | 2.0223 |
| Raw temporal, shuffled labels | 19.33% | 2.7438 |
| Raw temporal, Gaussian noise | 20.67% | 1.6324 |

All values are equal-person means. Accuracy and balanced accuracy coincide
because each person's test classes are balanced. Noise's larger point accuracy
is not evidence that noise is scientifically better.

## What this changes scientifically

Joint TimesFM improved log loss over the matched covariance baseline for all
twelve people: mean gain **3.0523 nats**, descriptive paired-bootstrap 95%
interval **[1.7077, 4.5539]**. Its conditional sign-flip p-value after Holm
correction across eighteen registered comparisons was **0.00439**. The other
two TimesFM applications also improved over this weak covariance baseline.
This is a relative representation-pipeline result, not evidence that pretraining
specifically learned neural language information; no random-weight TimesFM arm
was tested.

The decisive control fails: joint TimesFM's log-loss gain over the word prior
was **−0.1023 nats**, descriptive 95% interval **[−0.1608, −0.0276]**. Only one
of twelve people improved. Its gain over shuffled labels was **0.0403**
**[−0.0253, 0.1393]**, and over matched noise **−0.0664**
**[−0.1425, 0.0095]**. These comparisons do not establish useful word information.
All three TimesFM modes had worse mean log loss than the prior and none won
against its shuffled/noise controls after correction. Joint features also
improved over metadata; that does not overcome the failed prior/noise edges.

Sign-flip tests assume symmetric/exchangeable participant gain signs. Their
enumeration is exhaustive, but they are not assumption-free tests of mean
improvement. Intervals are descriptive, and this experiment is exploratory.
Do not compare 22.33% with the earlier experiment's 16.73% as a model gain:
the recording, participant set, calibration slice and readout changed. The
contemporaneous baselines above are the valid comparison.

## What was actually implemented and measured

The [fixed experiment](TIMESFM_WORDS_EXPERIMENT.md) used the same eight electrodes,
completed 2–4 s windows, 1–30 Hz filtering, 64 Hz resampling, 32-dimensional
training-only PCA and C=0.1 classifier in each feature arm. Each TimesFM method
had its own independently fitted shuffled-label and Gaussian-noise control.
Weights stayed frozen; English output labels identify five prompted Arabic
command-word conditions. No LLM rewrote the output.

The exact checkpoint contained **330,710,976 parameters**. Feature extraction
including all noise controls took **435.22 s**; the classifier process took
**7.11 s** for **192 fits**. Monitored feature-process peak RSS was
**2,328,510,464 bytes (2.17 GiB)**. Fresh acquisition verified **36 files /
45,969,075 bytes** in **12.54 s**. Preparation took **3.05 s**, retaining all
300 new test events and excluding two incomplete training events. New invocation
storage at prediction freeze was **1,662,853,583 bytes (1.55 GiB)**, within the
2 GiB invocation bound and global storage/reserve limits.

Two implementation corrections happened before the real comparison: ordinary
CPU initialization was required for nonpersistent rotary buffers, and the
parent needed permission to monitor its OS-sandboxed worker. The initial broker
parent failed to start monitoring; its child was stopped and retained no prepared data. Independent reviews
also caught scorer arm naming and child-process cleanup before execution.
These are implementation facts, not scientific successes.

**33 focused tests and twelve subtests passed.** Independent aggregate review
found zero discrepancies in arm means, participant counts, eighteen comparisons,
Holm adjustments and the prediction digest. It did not reopen targets or rescore.

All prediction hashes were committed and pushed at
`bdf0c0700f29f8e797e8fd267b5d1fd595b49b86` before the sole scoring transaction.
Prediction SHA256:
`90d4c7f4dd6cc24431f8a2dd653ceb9aeb5c52fd5d4d27e7c8c1b8f4c2e955c2`.
The new evaluation is now closed. Do not tune, refit or rescore it.

The [freeze record](../registries/timesfm_words_prediction_freeze.v0.json) binds
the code, protocol, source, inputs and feature arrays. The
[aggregate result](../registries/timesfm_words_result.v0.json) retains all
seventeen arms and eighteen comparisons. The local HTML report and exportable
figure are in `.codex_work/timesfm-words-r1/scored/`. Raw recordings, row-level
targets/predictions, extracted features and model weights remain local/ignored.
The official TimesFM weights are noncommercial/nonproduction and were not
redistributed.

## Claim boundary and next informative question

The strongest supported claim is that these frozen TimesFM features produced
better probability predictions than this particular covariance pipeline, while
failing to establish useful prompted-word decoding beyond null controls.
The source has visible cues and no dedicated eye or muscle channels. The result
does not establish isolated inner speech, arbitrary thoughts, free sentences,
brain-specific attribution, new-person generalization or real-time use.

The next informative question is whether word conditions are separable within
recordings but fail to transfer across recordings. That requires a separately
declared development analysis or fresh evaluation; this scored recording cannot
be used to select another model. Simply scaling up the model has not earned
priority from this evidence.
