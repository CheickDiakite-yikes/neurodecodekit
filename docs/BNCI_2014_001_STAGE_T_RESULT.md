# BNCI-C3C5-1 Stage T Frozen-Score Result

Date: 2026-08-25

Status: **Scored once and consumed. Registered route `BNCIC3C5-R2`; neither C3
nor C5-partial passed. The exact aggregate result is pending commit, push, and
both required CI jobs.**

## Plain-Language Result

The real held-out EEG candidate did better than chance and the no-signal/timing
controls in aggregate, but it did not survive the full preregistered control
suite or participant-consistency requirements. Adding EEG to recorded EOG also
moved performance in the desired direction, but the improvement was too small,
too inconsistent across people, and not statistically significant.

This is a real, target-firewalled, completely held-out-person score. It is also
a negative gate result. The data support continued investigation of a weak
candidate effect; they do not support an EEG-specific decoding or unseen-person
generalization claim.

## C3: EEG-Only Held-Out Prediction

The selected EEG candidate achieved participant-macro balanced accuracy of
`0.38349`:

| Comparison | Balanced accuracy | Selected-EEG margin |
|---|---:|---:|
| Uniform / empirical no-signal | 0.25000 | +0.13349 |
| Timing-only | 0.29668 | +0.08681 |
| Selected EEG | 0.38349 | - |
| Posterior EEG control | 0.39236 | -0.00887 |
| Central EEG control | 0.35802 | +0.02546 |
| Frontal EEG control | 0.29244 | +0.09105 |

Two of the five C3 components passed:

- balanced accuracy was above the frozen `0.35` threshold;
- the no-signal/timing margin was above `0.08`;
- the strongest control margin failed because posterior EEG was 0.887 points
  better than selected EEG;
- only 5 of 9 held-out participants had positive primary margins, below the
  required 8; and
- the exact one-sided sign-flip value was `p=0.06641`, above `0.05`.

Selected EEG log loss was `1.61026`, worse than uniform no-signal log loss
`1.38629`. Thus the model's above-chance class ranking included overconfident
errors. Accuracy alone would have overstated this result.

## C5-Partial: EEG Beyond Recorded EOG

Recorded EOG was already highly predictive of the four protocol conditions:

| Condition | Balanced accuracy | Log loss |
|---|---:|---:|
| Recorded EOG (`P`) | 0.60031 | 1.04340 |
| EOG + selected EEG (`P+E`) | 0.61574 | 1.01787 |
| EOG + deranged EEG (`P+D(E)`) | 0.60262 | 1.03630 |

The two preregistered log-loss deltas were directionally positive:

- `P - P+E = 0.02552`, below the required `0.03`; and
- `P+D(E) - P+E = 0.01843`, below the required `0.03`.

Both deltas were positive in 6 of 9 participants rather than the required 8.
Exact sign-flip values were `p=0.29102` and `p=0.32227`. All six C5-partial
components therefore failed.

## What We Learned

1. The real pipeline can recover nontrivial held-out protocol information; the
   EEG candidate exceeded chance and timing-only controls by meaningful
   aggregate margins.
2. The evidence is not spatially specific enough: posterior EEG slightly
   outperformed the selected candidate, weakening a neural-source
   interpretation and pointing toward visual/protocol structure.
3. Recorded EOG alone carried strong condition information. Any future claim
   must continue to treat eye-driven shortcuts as a first-class baseline.
4. EEG added a small, correctly directed improvement to EOG, but it was below
   the frozen effect-size and participant-consistency gates.
5. Larger or more flexible models are not the immediate answer. The next
   independent experiment should sharpen cue/visual/peripheral controls,
   calibration, and probability reliability on a fresh cohort without tuning
   on these consumed targets.

## Integrity And Resources

The scorer verified 41,472 frozen prediction rows against exactly 2,592 target
rows from nine sealed held-out-E sets. It opened the scoring-key vault once,
delivered targets once, scored once, and performed zero parameter updates,
held-out-T reads, retries, reruns, or network access.

Scoring took 2.368218 seconds at 175,243,264-byte peak process-tree RSS and
emitted one 4,951-byte aggregate result with SHA-256
`e836cefb9daf9df090f6f74a12ad90ae6448156d73850414fcca3367e81da9b2`.
No individual prediction, probability, target, or participant outcome is
public.

## Claim Boundary

Engineering capability established: NeuroDecodeKit completed a preregistered,
target-firewalled, nine-person real EEG/EOG experiment from semantic parsing
through frozen predictions and one aggregate score.

Scientific claim not established: neither registered gate passed, so this
result does not establish participant-independent decoding, incremental EEG
information beyond recorded EOG, thought or language decoding, movement
intention, motor-cortex origin, live decoding, portable hardware, home use, or
clinical utility.
