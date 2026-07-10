# Loop 15 Stage B - Synthetic Session Adapter Gate

Status: `Done` on 2026-07-10.

Proof posture: `synthetic domain-shift mechanism proof only; no real-session,
subject, population, causal, real-time, or at-home hardware claim`.

## Decision summary

A zero-learned-parameter robust channel-affine adapter passed the predeclared
synthetic gate. It estimates per-channel median/IQR statistics from source
train signals and unlabeled target calibration signals, then maps target
samples back to the source robust-statistics domain. It never reads text labels
while fitting.

The fixed synthetic protocol contains 96 unique variable-length sentences and
six channels. Text-hash partitions are 64 source train, 16 validation, and 16
frozen holdout rows. A deterministic positive-gain plus offset shift is applied
to valid samples only. The tiny CTC is trained on source train rows with one CPU
thread. Identity and adapted views replay the exact same initialization, loss
history, train predictions, and train CER.

Validation selected the adapter before holdout evaluation:

```text
minimum required validation CER gain: 0.10
identity validation CER:              0.327273
adapted validation CER:               0.000000
observed validation CER gain:          0.327273
selected:                              robust_channel_affine
```

On the frozen synthetic holdout:

| Method | Character edits | Corpus CER | Exact rows |
|---|---:|---:|---:|
| Identity shifted signal | 40 | 0.344828 | 0 / 16 |
| Robust channel affine | 0 | 0.000000 | 16 / 16 |
| Signal-free prior | 67 | 0.577586 | 0 / 16 |

The adapted-minus-identity paired CER delta is `-0.344828`; the 2,000-sample
sentence-bootstrap interval is `[-0.408696, -0.286957]`. All 16 sentences favor
the adapted view.

This closes Loop 15's stated synthetic acceptance gate. It does not authorize
retuning or re-evaluating on consumed S21 session 2.

## Why this adapter

Brain2Qwerty v2 normalizes each recording with per-channel median/IQR
statistics and includes a learned per-subject affine layer after spatial
channel merging. Adaptive Batch Normalization provides a broader precedent for
parameter-free target-domain statistic replacement. Euclidean Alignment is an
important BCI-specific full-covariance alternative, and latent cross-session
alignment is a more expressive research direction, but both add assumptions
that this first diagonal gate did not yet justify.

The selected adapter is deliberately smaller:

```text
target_aligned =
    ((target - target_median) / target_iqr) * source_iqr + source_median
```

It stores four scalars per channel and learns no gradient-trained parameters.
The target statistics use signal samples but no labels.

## Protocol and leakage boundary

The experiment is in-memory and synthetic-only:

1. Generate 96 unique token-motif sentences.
2. Split by deterministic text hash into 64/16/16 rows.
3. Train the tiny CTC only on the 64 source-train rows.
4. Create a shifted calibration view of source-train signals.
5. Fit source and target median/IQR statistics without target labels.
6. Select identity or adaptation only on the 16 shifted validation rows.
7. Evaluate the already selected adapter and the predeclared identity/prior
   comparators on the 16 shifted holdout rows.

The five real session-1 test rows and all 63 consumed session-2 rows are never
loaded. No real cache path is accepted by the command.

## Signal reconstruction

Because the synthetic shift is diagonal and invertible, the gate can compare
adapted samples with their known unshifted truth:

| View | Valid-sample MAE | RMSE | Maximum error |
|---|---:|---:|---:|
| Shifted identity | 0.7230882 | 0.9520396 | 2.5514081 |
| Robust channel affine | 1.3525e-7 | 4.3233e-7 | 2.6226e-6 |

The adapted-to-identity MAE ratio is `1.87e-7`. Padding remains exactly zero.

This near-exact inversion is expected: the calibration distribution is a
shifted copy of source train by construction. It is a best-case mechanism test,
not evidence that real MEG drift is diagonal, stationary, or invertible.

## Command

```bash
neurodecode synthetic-adapter-gate \
  --out-dir cache/loop15_synthetic_adapter_gate \
  --sentences 96 --channels 6 --letter-classes 4 \
  --seed 23 --epochs 50 --batch-size 16 \
  --learning-rate 0.02 --hidden-channels 16 \
  --num-threads 1 --min-validation-cer-gain 0.10 \
  --bootstrap-iterations 2000 --max-output-mb 2
```

## Resources

```text
execution: in-memory synthetic only
runtime reported by runner: 2.498 sec
wall time: 2.86 sec
peak RSS reported by runner: 306,790,400 bytes
external maximum resident set size: 316,342,272 bytes
source arrays in memory: 195,048 bytes
new cache bytes: 0
report/prediction artifacts: 21,354 bytes
output cap: 2 MiB
numeric/Torch threads: 1
free disk after run: about 17 GiB
```

## Gate checks

All ten checks pass:

- partitions are disjoint and complete
- adapter fitting uses no target labels
- real caches and consumed evaluation remain unloaded
- validation gain exceeds the predeclared threshold
- validation selects robust channel affine
- selected adaptation improves the frozen synthetic holdout
- reconstruction MAE ratio is below 0.001
- padding remains exactly zero
- decoder training replays identically across comparisons
- decoder uses one CPU thread

## Artifacts

```text
cache/loop15_synthetic_adapter_gate/report.json
cache/loop15_synthetic_adapter_gate/report.md
cache/loop15_synthetic_adapter_gate/identity_holdout_predictions.txt
cache/loop15_synthetic_adapter_gate/adapted_holdout_predictions.txt
cache/loop15_synthetic_adapter_gate/prior_holdout_predictions.txt
```

## Research sources

- Brain2Qwerty v2 paper:
  https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf
- Li et al., Adaptive Batch Normalization:
  https://arxiv.org/abs/1603.04779
- He and Wu, Euclidean Alignment for BCI:
  https://doi.org/10.1109/TBME.2019.2913914
- Jude et al., cross-session latent alignment:
  https://proceedings.mlr.press/v162/jude22a.html

## Closeout and next gate

Loop 15 is closed because its tracker acceptance criterion was synthetic
domain-shift recovery plus a documented real-data path. The real Stage A result
remains negative and frozen; Stage B proves only that the plumbing can detect
and reverse the simple shift it was designed for.

Loop 16 should measure a calibration curve across at least five unlabeled
target-calibration sizes and multiple shift seeds. It must include an unpaired
calibration distribution and at least one non-diagonal or time-varying shift so
the adapter can fail honestly. No real holdout may be reopened for that study.
