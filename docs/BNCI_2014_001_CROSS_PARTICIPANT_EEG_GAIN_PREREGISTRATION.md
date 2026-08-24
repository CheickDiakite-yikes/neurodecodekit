# BNCI-C3C5-1 Cross-Participant EEG-Gain Preregistration

Date: 2026-08-24

Status: **Frozen locally; every real-data, model, target, score, and claim
authority remains false**

Contract:

- `registries/bnci_2014_001_cross_participant_eeg_gain_contract.v0.json`

## Questions

This experiment asks two linked questions on the original BNCI 2014-001 motor
imagery distribution:

1. **C3:** can a compact scalp-EEG model predict four-class protocol condition
   in a completely held-out participant with zero calibration; and
2. **C5-partial:** does scalp EEG improve held-out-participant probability
   quality beyond the dataset's three recorded EOG channels and a size-matched
   deranged-EEG fusion?

C3 is evaluated with the EEG-only model. C5-partial is evaluated with a
cross-fitted conditional EOG+EEG stack. Neither endpoint may rescue the other.

## Immutable Source

The source is BNCI 2014-001, also known as BCI Competition IV dataset 2a,
mirrored by NEMAR `nm000139` tag `v1.0.2` at peeled commit
`15cf4f87975f4b5ee2ac39f703b9ac85b0ff97dc`.

The payload is exactly the 18 original `sourcedata/A??[TE].mat` files frozen in
the contract and research registry. They total `779,873,919` bytes and have
published SHA-256 digests. BDF conversions, HTML derivatives, duplicate
representations, and every other dataset are forbidden.

The semantic contract is:

- participants `A01` through `A09`;
- sessions `T` and `E`, with six task runs and 48 trials per run;
- 288 trials per session and 5,184 nominal trials overall;
- four labels: left hand, right hand, feet, and tongue;
- 250 Hz sampling;
- 22 EEG channels followed by three EOG channels in the frozen order; and
- source trial indices are one-based and converted once to zero-based sample
  offsets.

The channel order is pinned from the public MOABB loader at commit
`69d80d02d4300147fbd7b0d4b2c2d5d992dcaada`. The reader must validate the
MAT structure itself; the MOABB package is not a required base dependency.

## Trial And Time Contract

Time zero is fixation-cross and warning-tone onset. The directional cue begins
at `2.0` seconds, disappears at `3.25` seconds, and imagery continues until the
trial ends at `6.0` seconds.

The frozen windows are:

| Condition | Trial-relative interval | Samples at 250 Hz | Role |
|---|---:|---:|---|
| primary late EEG | `[3.5, 6.0)` | `[875, 1500)` | sustained-imagery endpoint |
| EOG comparator | `[2.0, 6.0)` | `[500, 1500)` | strongest recorded-eye comparator |
| early cue EEG | `[2.0, 3.0)` | `[500, 750)` | visual/cue control |
| pre-cue EEG | `[0.0, 2.0)` | `[0, 500)` | precondition control |

There is one decision per completed trial at `6.0` seconds. Every filter is
causal and runs sequentially over the continuous run with zero initial state
and state reset only at run boundaries. Forward-backward filtering, centered
windows, future samples, and trial-boundary filter resets are forbidden.

## Participant Firewall

There are exactly nine outer folds. In fold `i`, participant `Ai` is completely
held out:

- neither session from `Ai` may fit a filter parameter, scaler, covariance
  reference, classifier, fusion weight, selector, calibrator, or threshold;
- session `AiE` is the sole final evaluation session;
- session `AiT` is unused for that fold; and
- there is no held-out signal alignment, normalization fit, calibration,
  adaptation, rejection threshold, or abstention threshold.

The other eight participants, both sessions, are the fold's source domain. A
target can train another fold where its participant is a source participant,
but it is forbidden from the capability that predicts its own participant.
Each fold therefore runs in an isolated process with an explicit target
capability manifest. All nine held-out prediction sets must be frozen before
the one aggregate scoring delivery.

## Causal EEG Models

Instantaneous common-average reference is computed across the exact 22 EEG
channels only. Four fourth-order Butterworth SOS bands are applied causally:
`8-12`, `12-16`, `16-24`, and `24-30` Hz.

Two compact candidates are fixed before real data:

- **E1 log-bandpower:** log variance for each channel and band, variance floor
  `1e-12`, 88 features, source-only standardization, multinomial L2 logistic
  regression with `C=1.0`, `lbfgs`, equal class weights, and fixed seed `0`.
- **E2 filter-bank covariance:** trace-normalized regularized covariance per
  band, diagonal regularization `1e-5`, source-only log-Euclidean tangent
  reference, upper triangle including the diagonal, 1,012 features,
  source-only standardization, and the same classifier with `C=0.1`.

Within each outer fold, E1 versus E2 is selected by eight-fold inner
leave-one-source-participant-out participant-macro log loss. A tie within
`1e-12` selects E1. The selected family is then fitted once on all eight source
participants. No global winner may be chosen after held-out scoring.

## Recorded-EOG Comparator And Conditional Fusion

The EOG-only model `P` uses the three recorded EOG channels, causal `0.5-4`
and `4-8` Hz SOS bands, and the `[2.0, 6.0)` interval. For each channel and band
it records the mean and least-squares slope in eight nonoverlapping 500 ms bins
plus whole-window log variance. This yields 102 features. It uses source-only
standardization and multinomial L2 logistic regression with `C=1.0`, `lbfgs`,
equal class weights, and seed `0`.

Within each outer fold, eight source-participant cross-fits produce out-of-
person P and selected-E logits. Each four-class logit vector is class-centered
and represented by its first three components. The six resulting features fit
a multinomial L2 logistic fusion with `C=1.0`. P and E are refit on all eight
source participants before held-out prediction.

`P+D(E)` is a separate, size-matched fusion trained through the same procedure
after replacing each EEG trial with the previous trial's EEG from the same
48-trial run and replacing the first trial with exact zeros. This displacement
never wraps and never uses a label.

## Frozen Controls

Every fold freezes these conditions together:

- equal `0.25` no-signal prior;
- source empirical prior;
- timing and order only: session, run ordinal, trial ordinal, trial-onset time,
  and previous intertrial interval;
- EEG-only selected E;
- EOG-only P;
- fused `P+E`;
- size-matched `P+D(E)`;
- exact-zero EEG through the selected family;
- test-time EEG channel rotation by seven positions after canonical source fit;
- nonwrapping within-run EEG trial displacement;
- source-label rotation by one position within each run;
- pre-cue and early-cue EEG windows; and
- central, frontal, and posterior frozen EEG views.

The central view is `FC3, FC1, FCz, FC2, FC4, C5, C3, C1, Cz, C2, C4, C6,
CP3, CP1, CPz, CP2, CP4`. The frontal view is `Fz, FC3, FC1, FCz, FC2, FC4`.
The posterior view is `CP3, CP1, CPz, CP2, CP4, P1, Pz, P2, POz`.

All structurally complete trials enter the primary endpoint. Source artifact
flags may be retained for post-score description but may not exclude, weight,
select, or tune a primary row. Held-out artifact flags are unavailable to the
predictive process and cannot alter the scored set.

## Frozen Gates

### C3: unseen-participant protocol-condition prediction

The EEG-only selected E passes C3 only if all are true:

- participant-macro four-class balanced accuracy is at least `0.35`;
- its macro margin over the stronger equal-prior and timing-only comparator is
  at least `0.08`;
- its macro margin over the strongest fixed displacement, channel-rotation,
  source-label-derangement, pre-cue, and early-cue control is at least `0.02`;
- at least eight of nine held-out participants have positive balanced-accuracy
  margin over their stronger no-signal/timing comparator; and
- the exact one-sided participant sign-flip p-value for that primary margin is
  at most `0.05`.

### C5-partial: EEG beyond the three recorded EOG channels

Define per-participant mean multiclass log loss and:

```text
delta_EOG       = log_loss(P)      - log_loss(P+E)
delta_deranged  = log_loss(P+D(E)) - log_loss(P+E)
```

P+E passes C5-partial only if both participant-macro deltas are at least
`0.03` nats per trial, at least eight of nine participant deltas are positive
for each comparison, and each exact one-sided paired participant sign-flip
p-value is at most `0.05`.

All integrity, capability, completeness, resource, and freeze gates must also
pass. Pooled trial p-values are forbidden.

## Router

- `BNCIC3C5-R0`: integrity, identity, semantic, capability, payload, resource,
  freeze, or scoring refusal.
- `BNCIC3C5-R1`: generated or target-blind structural qualification failed;
  no scientific score.
- `BNCIC3C5-R2`: neither C3 nor C5-partial passed.
- `BNCIC3C5-R3`: C3 passed and C5-partial failed.
- `BNCIC3C5-R4`: C5-partial passed and C3 failed.
- `BNCIC3C5-R5`: both C3 and C5-partial passed.

R2 through R5 consume the single aggregate target-scoring event. There is no
scientific rerun, alternate seed, post-target exclusion, threshold change,
model change, or route amendment.

## Ordered Evidence Stages

1. `G1`: generated MAT, target-firewall, causal-feature, model, control,
   transport, resource, freeze, and scorer qualification.
2. `A`: one opaque acquisition invocation for the exact 18 original MAT files;
   size and SHA-256 only.
3. `Q`: one target-blind semantic and signal qualification; freeze the exact
   run/trial/channel inventory and target-capability plan.
4. `P`: nine isolated source-only folds, every target-blind held-out prediction,
   and one aggregate hash-only prediction freeze.
5. `T`: only after the freeze is committed, pushed, and both CI jobs are green,
   one delivery of the same nine fold-scoped target sets and one score.

Every stage is one-shot and depends on the preceding exact implementation and
proof barrier. A transport retry may resume only an invocation-created partial
file and does not authorize a second scientific execution.

## Resource And Publication Boundary

- one CPU thread, one worker, and one numerical job;
- at most three transport attempts per file and 54 payload requests total;
- at most 2.5 GiB network transfer and 2 GiB incremental disk;
- at least 5 GiB free disk before acquisition;
- at most 512 MiB private derivatives, 4 MiB public artifacts, and 1 GiB peak
  RSS;
- at most 540 parameter-update fits and 900 prediction sets;
- zero network during semantic analysis, modeling, freezing, and scoring; and
- one scoring delivery, one scoring event, zero scientific reruns, and zero
  post-target updates.

No payload, row-level derivative, checkpoint, individual prediction,
probability, target, or participant outcome may be committed or published.
Only code, exact source identity, aggregate resource measurements, aggregate
metrics, routes, warnings, and claim boundaries may be public.

## Claim Boundary

The maximum R5 claim is participant-independent four-class BNCI
protocol-condition prediction plus incremental scalp-EEG sensor information
beyond the three recorded EOG channels.

It is not arbitrary thought or language decoding, executed movement-intention
decoding, exclusive motor-cortex attribution, evidence beyond every peripheral
or unrecorded artifact, real-time decoding, portable hardware, home use, or a
clinical result. The dataset has no synchronized EMG or motion sensor, so even
C5-partial cannot establish the broader peripheral-independence claim.

This preregistration authorizes nothing and establishes no new scientific
result.
