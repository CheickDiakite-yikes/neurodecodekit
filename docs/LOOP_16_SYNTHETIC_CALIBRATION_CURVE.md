# Loop 16 - Synthetic Calibration Curve and Drift Stress

Status: `Done` on 2026-07-10.

Proof posture: `synthetic calibration characterization only; no real-session,
subject, population, causal, real-time, arbitrary-thought, or at-home hardware
claim`.

## Decision summary

Loop 16 measures how the zero-parameter robust channel-affine adapter behaves
as unlabeled target calibration grows. The experiment uses six nested sizes,
three independently seeded shifts, and three shift families:

```text
calibration rows: 1, 2, 4, 8, 16, 32
shift seeds:      101, 211, 307
shift families:   stationary diagonal
                  stationary channel mixing
                  within-row time-varying gain/offset
```

The calibration pool contains 48 synthetic sentences generated independently
from the 96 source sentences. Its text-membership intersection with source is
empty. Adapter fitting sees calibration signals and valid lengths, never
target text or token labels.

The preregistered stationary-diagonal rule selects the smallest size whose
median validation CER gain is at least `0.10` and which harms none of the three
seeds. It selects one sentence, representing `1.26` seconds of this synthetic
signal. That is a median-rule result: two holdout seeds improve and one ties.
It must not be translated into a claim that a person needs 1.26 seconds of MEG
calibration.

## Why this study

Brain2Qwerty v2 estimates per-channel median/IQR statistics per recording,
clamps extreme robust amplitudes, augments training data with channel offsets,
and includes a learned per-subject affine layer. Those choices acknowledge
recording and person variation, but they do not establish the amount of target
data needed for a new session.

CORAL and Euclidean Alignment motivate covariance-aware unlabeled alignment.
MEG BCI research also reports non-stationarity from factors such as head motion,
fatigue, and session transfer, including adaptation with rolling windows. A
session-domain-generalization study found that explicit generalization methods
did not reliably outperform empirical risk minimization and that target
fine-tuning could even hurt unseen sessions. The correct first question is
therefore not "which complex adapter should we add?" but "where does the
smallest adapter stop working?"

## Protocol

1. Generate 96 source sentences and split by text hash into 64 train, 16
   validation, and 16 frozen holdout rows.
2. Generate a disjoint 48-sentence calibration pool with a separate seed.
3. Fit one tiny CTC on source train rows and reuse it unchanged across all 63
   validation signal views.
4. Fit source median/IQR statistics on the 64 source-train rows.
5. Fit target statistics on nested prefixes of an independently hashed
   calibration order. Target labels are not passed to the adapter.
6. Measure the full calibration curve on validation only.
7. Select the stationary-diagonal row count before holdout.
8. Replay the same source-model training deterministically once and evaluate
   only the selected row count on the frozen synthetic holdout.

The five real session-1 test rows and all 63 consumed session-2 rows are never
loaded. The command accepts no real-cache path.

## Validation curve

Median results across three shift seeds:

| Shift family | Rows | Synthetic minutes | Identity CER | Adapted CER | CER gain | Non-harm seeds |
|---|---:|---:|---:|---:|---:|---:|
| Stationary diagonal | 1 | 0.0210 | 0.4455 | 0.2000 | +0.2455 | 3/3 |
| Stationary diagonal | 2 | 0.0387 | 0.4455 | 0.0000 | +0.4455 | 3/3 |
| Stationary diagonal | 4 | 0.0773 | 0.4455 | 0.0000 | +0.4455 | 3/3 |
| Stationary diagonal | 8 | 0.1577 | 0.4455 | 0.0000 | +0.4455 | 3/3 |
| Stationary diagonal | 16 | 0.3337 | 0.4455 | 0.0000 | +0.4455 | 3/3 |
| Stationary diagonal | 32 | 0.6293 | 0.4455 | 0.0091 | +0.4364 | 3/3 |
| Channel mixing | 1 | 0.0210 | 0.6545 | 0.7909 | -0.0455 | 0/3 |
| Channel mixing | 32 | 0.6293 | 0.6545 | 0.7091 | -0.0545 | 1/3 |
| Time varying | 1 | 0.0210 | 0.4455 | 0.6000 | -0.1545 | 0/3 |
| Time varying | 32 | 0.6293 | 0.4455 | 0.6000 | -0.1636 | 0/3 |

The diagonal curve saturates quickly because every valid time sample in one
sentence contributes to six independent per-channel statistics, and the source
and calibration generators share the same deliberately easy motif process.
The non-monotonic 32-row point is another reminder that finite synthetic noise
and a tiny 16-row validation partition remain material.

Sensitivity analysis, not the registered decision: if every shift seed had to
meet the full `0.10` gain threshold rather than merely avoid harm, the first
qualifying size would be two sentences, or about `2.32` synthetic seconds.

## Frozen synthetic holdout

The registered one-row size is evaluated once after selection:

| Shift family | Identity CER | Adapted CER | Prior CER | Median CER gain | Non-harm seeds |
|---|---:|---:|---:|---:|---:|
| Stationary diagonal | 0.4224 | 0.2328 | 0.5776 | +0.1897 | 3/3 |
| Channel mixing | 0.5690 | 0.8621 | 0.5776 | -0.2586 | 0/3 |
| Time varying | 0.4397 | 0.6034 | 0.5776 | -0.1638 | 0/3 |

Stationary-diagonal holdout seed gains are `+0.1897`, `0.0000`, and `+0.2759`.
All three channel-mixing seeds and all three time-varying seeds are harmed.
Their paired intervals consistently favor identity over adaptation. The
failure is expected: independent per-channel scaling cannot undo cross-channel
rotation, and one static statistic cannot track drift within a sentence.

## Engineering result

The tiny CTC now has a multi-view evaluation path. One source-trained model can
score many immutable target views without retraining for every calibration
point. Loop 16 uses two fits total: one for validation selection and one exact
replay for post-selection holdout. Loss history, initialization, train
predictions, and train CER match exactly.

## Command

```bash
neurodecode synthetic-calibration-curve \
  --out-dir cache/loop16_synthetic_calibration_curve \
  --sentences 96 --calibration-sentences 48 \
  --channels 6 --letter-classes 4 --seed 23 \
  --calibration-sizes 1,2,4,8,16,32 \
  --shift-seeds 101,211,307 \
  --epochs 50 --batch-size 16 --learning-rate 0.02 \
  --hidden-channels 16 --num-threads 1 \
  --min-stationary-validation-cer-gain 0.10 \
  --bootstrap-iterations 1000 --max-output-mb 4
```

## Resources

```text
execution: in-memory synthetic only
runner runtime: 1.897 sec
wall time: 2.25 sec
external maximum RSS: 318,963,712 bytes
validation views scored from one fit: 63
holdout views scored from one replay: 18
new cache bytes: 0
JSON/Markdown/CSV artifacts: 158,256 bytes
output cap: 4 MiB
numeric/Torch threads: 1
free disk after run: about 17 GiB
```

## Artifacts

```text
cache/loop16_synthetic_calibration_curve/report.json
cache/loop16_synthetic_calibration_curve/report.md
cache/loop16_synthetic_calibration_curve/validation_curve.csv
cache/loop16_synthetic_calibration_curve/holdout_results.csv
```

## Research sources

- Brain2Qwerty v2:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Sun, Feng, and Saenko, CORAL:
  https://doi.org/10.1609/aaai.v30i1.10306
- He and Wu, Euclidean Alignment:
  https://doi.org/10.1109/TBME.2019.2913914
- Spüler, Rosenstiel, and Bogdan, MEG covariate-shift adaptation:
  https://doi.org/10.1186/1687-6180-2012-129
- Han and Jeong, session-independent BCI domain generalization:
  https://arxiv.org/abs/2012.03533

## Decision and next gate

Loop 16 is complete as a synthetic characterization. Robust channel-affine
normalization remains a narrow stationary-diagonal option, not a general
session adapter. It is not authorized for a new real-session claim.

The next adapter research gate should compare a regularized covariance-aware
map for stationary channel mixing with a causal rolling-statistics method for
time drift, still on synthetic validation first. The roadmap can proceed to
Loop 17's honest demo in parallel, but the demo must expose calibration status,
proof posture, and the fact that the current tiny CTC is noncausal.
