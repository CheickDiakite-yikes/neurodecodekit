# DREYER-C5R-1 Independent EEG Replication Preregistration

Date: 2026-08-25

Status: **Prospectively frozen design. No source EDF payload, header,
annotation, signal sample, target, label, model outcome, or score has been
read. This document grants no real-data authority.**

## Question

In completely unseen participants performing visually cued left-versus-right
hand motor imagery, do predeclared central EEG features add held-out predictive
information beyond recorded EOG, wrist EMG, posterior EEG, and trial timing?

This is designed around the exact BNCI postmortem failures. It tests
incremental sensor information under strong nuisance controls; it does not
assume a motor-cortex source or call the target spontaneous intention.
In shorthand, the primary comparison is nuisance + residual central EEG
against both nuisance alone and nuisance + deranged residual central EEG.

## Evidence Sequence

The one-way sequence is `G -> H -> A -> Q -> P -> T`:

1. `G`: generated-only qualification of the parser contract, firewall, model
   schedule, prediction freezer, scorer, and failure cases;
2. `H`: one exact source-EDF header preflight;
3. `A`: opaque acquisition and SHA-256 verification of the other 119 files;
4. `Q`: one semantic parse and target-firewalled feature derivation;
5. `P`: 60 held-out-person folds, source-only fitting, target-blind held-out
   predictions, and one aggregate hash-only freeze; and
6. `T`: one delivery of the same sealed targets and one frozen aggregate score,
   only after the prediction-freeze commit is remotely green.

Each real stage is separately consumed. Failure parks the lane. No stage may
retry, substitute data, tune a setting, or infer authority for the next stage.

## Cohort And Split

- Dataset: Dreyer et al. 2023 Dataset A, NEMAR `nm000250` `v1.0.4`.
- Participants: exactly `sub-01` through `sub-60`.
- Runs: exactly R1 and R2, 40 trials per run, 20 left and 20 right.
- Expected rows: 4,800.
- Outer protocol: 60 leave-one-participant-out folds.
- Each fold: 59 source participants and one completely unseen participant.
- Held-out-person calibration, adaptation, exclusion, and target access: zero.
- R3-R6: untouched by every stage.

The class target is the instructed left/right protocol condition. `left=0` and
`right=1`. It is created only inside the target-sealing capability after all
target-free features and identities are complete.

## Fixed Sensor Sets

The exact EOG and EMG labels must be narrowed to the Stage H observed roster
without changing their counts or roles. EEG labels are fixed now.

Central homologous pairs:

`C1/C2`, `C3/C4`, `C5/C6`, `FC1/FC2`, `FC3/FC4`, `FC5/FC6`,
`CP1/CP2`, `CP3/CP4`, `CP5/CP6`.

Posterior nuisance set: `P3`, `Pz`, `P4`.

Frontal audit set: `F3`, `Fz`, `F4`.

No common-average rereference, participant-specific channel selection,
channel deletion, interpolation, ICA, CSP, source localization, or
target-derived artifact rejection is permitted. The recorded left-ear
reference is preserved.

## Causal Features

All signals are converted to volts and sampled at exactly 512 Hz. Every
one-second segment is mean-centered, multiplied by a periodic Hann window, and
transformed with `numpy.fft.rfft`. Power is squared magnitude divided by the
squared-window sum. For each channel and band, the feature is
`log10(band_power + 1e-18) - log10(5_to_35_Hz_power + 1e-18)`.

Frozen half-open bands are `8-12 Hz`, `12-20 Hz`, and `20-30 Hz`. Boundary
bins belong to the higher band except 30 Hz, which is included in the last
band. No sample outside the registered interval may enter a feature.

Windows relative to trial start:

| Name | Samples | Purpose |
|---|---:|---|
| pre | `[1.0, 2.0)` | pre-cue negative control |
| cue | `[3.0, 4.0)` | lateralized visual-cue control |
| late | `[5.0, 8.0)` as three 1-second bins | primary motor-imagery/feedback interval |

Late per-channel features are the arithmetic mean of the three bin features.
Central EEG features are left-minus-right log-relative power for the nine
fixed homologous pairs and three bands: 27 values. EOG, EMG, posterior, and
frontal features retain one value per channel and band.

Timing features are target-free and fixed: R2 indicator, trial index divided
by 39, and sine/cosine of `2*pi*trial_index/40`.

The producer is causal with one second of spectral context and a decision time
of 8 seconds after trial start. This experiment does not measure acquisition,
transport, or end-to-end live latency.

## Residualization And Derangement

For each outer fold and window, a source-only multi-output ridge model predicts
the 27 central-pair features from EOG, EMG, posterior EEG, and timing. Frozen
settings are `alpha=10`, fitted intercept, and source-only standardization.
Held-out central residuals are observed minus the source-fitted nuisance
prediction. Labels never enter residualization.

The matched derangement swaps adjacent residual rows within each participant
and run: `0<->1`, `2<->3`, ..., `38<->39`. It never wraps across a run,
participant, or split. The same target-blind transform is applied independently
to source and held-out residuals.

## Compact Model And Calibration

Every fitted classifier is the same scikit-learn L2 logistic family:

- `C=0.1`;
- `solver="lbfgs"`;
- `max_iter=1000`;
- `tol=1e-6`;
- no class weights;
- one CPU thread; and
- source-only mean/standard-deviation scaling with zero variance mapped to 1.

Nonconvergence, a warning, NaN, infinite coefficient, missing class, or
dimension drift parks the real stage. There is no fallback solver or larger
model.

The nine log-loss conditions use five participant-grouped inner source folds.
Inner fold is `(participant_number - 1) mod 5`; the outer participant is never
present. Out-of-fold source logits select one temperature from the fixed grid
`2**(k/16)` for integer `k=-32..32`. Selection minimizes source log loss, with
ties resolved by distance to 1 and then lower temperature. Final held-out
logits are divided by that source-only temperature and clipped to
`[1e-6, 1-1e-6]`.

The exact real schedule is 4,740 parameter-update fits and 1,020 held-out
prediction sets: 17 conditions across 60 folds. No search, restart, checkpoint,
deep network, pretrained model, foundation model, or language model is used.

## Frozen Conditions

1. equal prior;
2. timing only;
3. EOG only;
4. EMG only;
5. posterior EEG only;
6. late nuisance (`N`);
7. late central EEG (`E`);
8. late residual central EEG (`R`);
9. late `N+R`;
10. late `N+D(R)`;
11. late nuisance without posterior (`N-P`);
12. late `N-P+R`;
13. pre-cue nuisance;
14. pre-cue `N+R`;
15. cue nuisance;
16. cue `N+R`; and
17. late `N+R` trained with a one-step within-run source-label rotation.

Only conditions 6, 9, 10, 11, 12, 13, 14, 15, and 16 use source-only
temperature calibration. All other classifier conditions use temperature 1.

## Primary Gate

Scores are computed per held-out participant, then macro-averaged across the
60 participants. Let `LL(X)` be participant-macro binary log loss.

The lane passes only if every component passes:

1. `LL(N) - LL(N+R) >= 0.020` nats/trial;
2. `LL(N+D(R)) - LL(N+R) >= 0.020`;
3. each of those two deltas is positive in at least 39 of 60 participants and
   its exact one-sided binomial sign-test value is `p <= 0.025`;
4. `LL(N-P) - LL(N-P+R) >= 0.015`;
5. the late nuisance increment exceeds the pre-cue nuisance increment by at
   least `0.010`;
6. `LL(N+R) < ln(2)` and its ten-bin equal-width expected calibration error is
   at most `0.10`;
7. `N+R` balanced accuracy is at least `0.60` and at least `0.05` above the
   stronger of equal-prior and timing-only accuracy; and
8. all structural, target-firewall, completeness, prediction-freeze, resource,
   and no-update assertions pass exactly.

Components 1 and 2 are the two co-primary comparisons. Their `0.025` sign-test
thresholds form a fixed Bonferroni family. Cue, EOG-only, EMG-only, posterior,
central-only, residual-only, and source-label rotation remain mandatory audit
outputs but cannot rescue a failed primary gate.

## Frozen Routes

- `DREYERC5R-R1`: every primary component passed.
- `DREYERC5R-R2`: aggregate candidate information exists, but one or more
  specificity, consistency, calibration, or effect-size components failed.
- `DREYERC5R-R3`: no registered candidate advantage.
- `DREYERC5R-R0`: structural, proof, firewall, resource, or completeness
  failure; no scientific score is accepted.

Only R1 supports the claim ceiling. R2 and R3 are negative gate results.

## Target Firewall And Publication

Stage Q creates fold-isolated source arrays, source targets, held-out feature
arrays, and sealed held-out target envelopes. A fold capability cannot name or
traverse another fold, its own held-out target envelope, or scoring keys.

Stage P writes private predictions and a public aggregate freeze containing
only identities, counts, dimensions, condition names, and hashes. It contains
no prediction, probability, target, participant outcome, or score. Stage T may
open the same 60 target envelopes exactly once only after that freeze commit
and both required CI jobs are remotely green.

Public scoring is aggregate only. Individual targets, predictions,
probabilities, participant metrics, source headers, raw signals, private paths,
and derivative arrays are never committed or released.

## Resource Envelope

- one CPU thread, one worker, one numerical job;
- at least 10 GiB free disk before Stage H/A/Q/P;
- 2 GiB maximum payload network and 3 GiB incremental disk;
- 1.5 GiB maximum process-tree RSS;
- 7,200 seconds maximum for any one real stage;
- 256 MiB maximum private generated derivatives/predictions;
- 4 MiB maximum combined public output per stage;
- zero analysis network after acquisition; and
- zero retries, reruns, post-target updates, substitutions, or partial success.

## Claim Boundary

An R1 result could establish participant-independent visually cued left/right
motor-imagery protocol-condition information with an incremental contribution
from predeclared central EEG sensors beyond the recorded EOG, wrist EMG,
posterior EEG, timing, and derangement controls in this cohort.

It would not establish spontaneous intention, exclusive motor-cortex origin,
eye-independent causation, thought or language decoding, live decoding,
portable hardware, home use, or clinical utility.
