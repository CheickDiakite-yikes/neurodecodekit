# IACKD Role-Aware Dual-Reversal Preregistration

Date: 2026-08-10

Status: **Frozen prospective contract; no public payload, retained private
bundle, signal, event, trajectory, target, training, inference, prediction, or
score is authorized**

Contract:
`registries/iackd_role_aware_dual_reversal_contract.v0.json`

Research basis:
`docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_RESEARCH.md`

Lane: **IACKD-2 Role-Aware Dual Reversal**

## Objective

Test whether a fixed causal pre-movement EEG representation follows measured
hand direction rather than the visual cue under two opposing transfer
directions:

1. `C2I`: fit congruent trials and predict held-out incongruent trials; and
2. `I2C`: fit incongruent trials and predict held-out congruent trials.

For each arm, the cue-derived alternative is the exact opposite of action on
the sealed-final trials. Both arms must independently favor action. One arm
cannot rescue the other.

This is deliberately harder than repeating the consumed IACKD-1 design. It
binds the corrected 26-channel source-declared EEG core, uses a symmetric
mapping reversal, adds an occipital visual proxy, makes the weaker of the two
participant-level arm margins primary, and forbids the old retained bundle.

This document freezes a possible future experiment. It does not authorize an
implementation against real data, a download, local-path access, training,
prediction, target delivery, scoring, or a scientific claim.

## Evidence Anchors

The design binds four immutable public records:

- the green dual-reversal research commit
  `41ea1fcc6c31ebe67437ae4d381b4a57cf6cef54`;
- the consumed H2 role/geometry result commit
  `580f11fc60d2882a11bf4e765bb33b60ffc0bd04`, which measured one fixed
  26-channel EEG core, optional M1/M2, source-typed MISC controls, 1024 Hz,
  average reference, and complete central and occipital geometry;
- the generated-only H3 source-semantics result commit
  `cff8d79208a8afa11b3da036f69626236c9664e2`, whose policy hash is
  `1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4`;
  and
- the committed OpenNeuro inventory whose expanded identity hash is
  `c30b518f9dafe3d46128849725e1f2f8fdce33239fbf6ade8603d66a64f0ffa5`.

H2 remains consumed at `IACKDR-R1`; H3 did not amend that outcome or validate a
real reader. IACKD-1 remains consumed at `IACKD-F10`. These records inform the
new prospective contract but cannot be reopened, rerouted, or scored again.

## Exact Dataset Identity

```text
provider:                       OpenNeuro
accession/version:              ds006840 / 1.0.0
DOI:                            10.18112/openneuro.ds006840.v1.0.0
license/BIDS:                   CC0 / 1.7.0
participants:                   sub-01 through sub-15
participant-hand units:         30
BIDS run groups:                128
objects per run group:          10
separate geometry objects:      60
selected objects:               1,340
selected payload bytes:         7,249,113,684
largest run group:              82,064,564 bytes
largest individual object:      73,200,640 bytes
geometry bytes:                 56,386
published derivatives:          excluded
participant demographics:       excluded
subject scan tables:             excluded
```

The exact selected-object paths, sizes, ETags, and modification times live in
`registries/iackd_openneuro_metadata_inventory.v0.json`. ETags remain provider
metadata, not content hashes. A later authorized executor must compute one
SHA-256 per body while streaming it.

Before the first payload request, that executor must re-read only the registered
OpenNeuro `dataset_description.json`, `CHANGES`, and two-page S3 listing. The
listing must still contain 1,679 objects and 7,966,799,433 bytes overall, and
the selected identity must still match all 1,340 paths and bytes exactly. No
payload request is allowed before that match.

## Fresh, Storage-Safe Access Design

The existing Git-ignored IACKD bundle is forbidden. A future Tier C sequence
must use a new invocation-created root and process one run group at a time:

1. reverify the exact public inventory before any payload request;
2. fetch and validate the 60 geometry objects once;
3. fetch one canonical 10-object run group into an isolated temporary root;
4. verify every path, size, ETag, response, and streaming SHA-256;
5. reconcile that run and emit bounded target-blind and sealed derivatives;
6. delete only that invocation's temporary raw run group after derivative
   promotion; and
7. continue to the next group without retaining a second raw bundle.

At most 82,064,564 registered raw payload bytes may coexist as one complete run
group. Peak incremental disk is capped at 1 GiB, including temporary raw files,
private derivatives, manifests, and receipts. At least 10 GiB free disk is
required before the first payload request. The future sequence transfers the
exact 7,249,113,684 selected bytes once, with no redirect, retry, substitution,
or rerun.

No cleanup may target a pre-existing path. Failure consumes the future
one-shot execution and leaves only bounded diagnostics and already promoted
private derivatives for explicit later disposition.

## Ordered Evidence Sequence

The valid order is:

1. commit and push this preregistration and pass both CI jobs;
2. implement and qualify the reader, target firewall, models, controls,
   freezer, scorer, and storage guards on generated fixtures and mocked
   transport only under Tier B;
3. commit and push that exact implementation and pass both CI jobs;
4. prepare an all-false Tier C request that binds the green registration and
   implementation;
5. record a fresh packet-bound maintainer decision in a separate commit and
   pass both CI jobs;
6. perform one fresh sequential public acquisition and derivative build;
7. perform one target-blind fit/prediction execution;
8. commit and push one aggregate hash-only prediction freeze and pass both CI
   jobs;
9. deliver both arms' sealed-final target views together once;
10. score once, apply the frozen router, and stop.

No earlier public-data allowance, autonomy statement, `continue`, IACKD-1
decision, H2 decision, or old local bundle substitutes for step 5.

## Source Semantics

The H3 policy is mandatory and precedes model construction:

```text
source layer:         preserve BIDS type and source counts
functional layer:     assign predictive, ocular, trigger, or optional role
model layer:          assign an explicit inclusion mask
predictive EEG:       fixed 26-channel core only
optional EEG:         M1 and M2, nonpredictive
ocular controls:      HEOG and VEOG, source type MISC, nonpredictive
trigger control:      Trigger, source type MISC, nonpredictive
sampling rate:        1024 Hz
source reference:     average
central view:         C3, C4, Cz
occipital view:       O1, Oz, O2
```

The fixed predictive order is:

```text
Fp1 Fp2 F7 F3 Fz F4 F8 FC3 FCz FC4 T7 C3 Cz C4 T8 CP3 CPz CP4
P7 P3 Pz P4 P8 O1 Oz O2
```

Every derivative, feature set, model, prediction set, freeze record, and receipt
must bind the source-order, source-count, functional-role, model-mask,
geometry-mask, and H3 policy hashes. MNE inference may not replace these source
declarations.

## Split And Dual Reversal

Each participant and moving hand is a separate model unit. `sub-04` and
`sub-05` use runs 01-05 for fitting and run 06 as sealed final. Every other
participant uses runs 01-03 for fitting and run 04 as sealed final.

The two arms use disjoint condition rows inside the same run partition:

| Arm | Fit rows | Final rows | Frozen fit relation | Final cue surrogate |
|---|---|---|---|---|
| `C2I` | red congruent | yellow incongruent | `action = visual` | `+visual = -action` |
| `I2C` | yellow incongruent | red congruent | `action = -visual` | `-visual = -action` |

The published 7,040-trial geometry yields exact pre-quality-control maxima:

```text
per arm fit rows:          2,680
per arm final rows:          840
both arms fit rows:         5,360
both arms final rows:       1,680
all assigned rows:          7,040
```

After target-blind quality checks, every arm and participant-hand unit must
retain at least 24 fit rows per action direction and eight final rows per
action direction. All 15 participants and 30 units are required. No row-random
split, cross-participant fit, cross-hand fit, arm pooling, participant
replacement, target-derived exclusion, final-run model selection, or
evaluation-time adaptation exists.

## Trial Reconciliation And Motion Guard

A future reader must process one BrainVision run and its registered event,
ball, and Leap companions at a time. It must:

- require exact source-order agreement between VHDR and `channels.tsv`;
- apply the H3 role policy instead of a total-channel-count rule;
- accept only the measured 29-row and 31-row source signatures;
- retain the 26 predictive EEG channels and HEOG/VEOG controls;
- require complete registered central and occipital geometry;
- require 1024 Hz and source-declared average reference;
- reconcile only the frozen marker and stream identities;
- perform no ICA, interpolation, bad-channel deletion, amplitude rejection,
  zero-phase filtering, or target-derived exclusion; and
- persist no raw EEG, EOG, ball, or Leap window.

Predictive preprocessing may receive only absolute three-dimensional hand
speed and the derived onset timestamp. Signed displacement, final position,
visual direction, action direction, and color-derived direction remain behind
the target firewall.

```text
speed:               Euclidean first-difference displacement / delta time
threshold:           max(20 mm/s, baseline median + 10 * baseline MAD)
persistence:         3 consecutive native Leap samples
registered stop:     min(event-14, detected onset - 30 ms)
primary EEG window:  [registered stop - 1.0 s, registered stop)
```

The window is half-open and uses zero right context. This is an offline,
oracle-aligned causal-in-samples assay. End-to-end latency is not measured.

## Target Firewall

Fit-label delivery is arm-specific and limited to the fit partition. The
isolated builder verifies the expected action/visual relation before exposing
only the actual hand-direction fit target to that arm's fitting process.

Final predictive derivatives contain only EEG/control features, participant,
hand, run, opaque trial identity, arm identity, target-blind timing and quality
fields, and provenance hashes. Condition, color, action sign, visual sign,
signed ball or Leap values, target, probability, score, and participant outcome
are forbidden from predictive arrays and public artifacts.

The isolated scorer receives one sealed row per final trial containing:

1. actual hand direction from signed Leap displacement; and
2. the arm-specific cue surrogate, defined as the visual direction multiplied
   by the frozen fit action-to-visual sign.

It verifies that those two labels are exact opposites. All 900 prediction sets
freeze before either final target view is delivered.

Direction is not taken from a single categorical field. For both Leap and ball
streams, it is the sign of median x position over the final 20 percent of the
execution segment minus median x position over the first 20 percent. Absolute
Leap displacement must be at least 5 mm and absolute ball displacement at least
5 pixels. The ball `move_direct` field must agree, but cannot serve as the sole
target source.

## Fixed Causal Model

```text
predictive EEG:       26 channels in frozen order
re-reference:         instantaneous common average across those 26 channels
filter:               fourth-order Butterworth 0.5-4 Hz SOS
application:          causal scipy.signal.sosfilt over each continuous run
window:               [-1.0, 0.0) from registered stop
features/channel:     four 250 ms means plus one whole-window slope
primary dimension:    130
classifier:           participant-hand-and-arm-specific LDA
solver/shrinkage:     lsqr / 0.1
class priors:         equal
selection choices:    1
hyperparameter runs:  0
right context:        0 seconds
```

Central and occipital models use 15 features each. HEOG/VEOG use ten features.
Early and late half-window models use 78 features each. The pre-window model
uses the same 130-feature recipe over `[-2.0, -1.0)`. Timing-only features are
the frozen run ordinal, within-run trial ordinal, event-55-to-event-14
interval, and event-55-to-registered-stop interval.

Every scale, nuisance projection, coefficient, prior, and threshold is fit from
one arm's fit rows only. There is no deep network, CML-v0, foundation model,
LLM, pretrained checkpoint, language feature, model search, test-time
adaptation, or post-target update.

The future implementation may reuse an existing isolated environment only if
it reports NumPy `2.5.2`, SciPy `1.18.0`, MNE `1.12.1`, and scikit-learn
`1.9.0` exactly. A missing or drifted environment parks the lane. Dependency
installation or network resolution is outside this contract.

## Exact Fit And Prediction Inventory

Each of 30 participant-hand units has 11 fits per arm:

1. whole-head primary;
2. central C3/C4/Cz;
3. occipital O1/Oz/O2;
4. HEOG/VEOG only;
5. fit-only EOG-orthogonalized primary;
6. early half;
7. late half;
8. pre-window baseline;
9. timing only;
10. fixed train-label derangement, seed `6841`; and
11. train-only no-signal prior.

That is exactly `30 * 2 * 11 = 660` parameter-update fits.

Each unit freezes 15 prediction sets per arm: the 11 fitted conditions plus
all-zero final EEG through the primary model, one-row cyclic final-feature
displacement, fixed final-only EEG-channel permutation seed `6842`, and the
opposite-hand primary model without adaptation. That is exactly
`30 * 2 * 15 = 900` prediction sets and at most 900 target-blind inference
calls.

The same primary prediction is scored once against action and once against the
exact-opposite cue surrogate. The second target view does not create another
prediction set.

## Participant-Level Primary Statistic

For each participant, hands are combined before computing balanced accuracy.
For each arm:

```text
arm margin = BA(actual action) - BA(arm-specific cue surrogate)
```

The primary participant value is:

```text
minimum(C2I arm margin, I2C arm margin)
```

This makes the weaker transfer direction decisive. Enumerate all `2^15 =
32,768` sign assignments over the 15 participant minimum margins. The one-sided
p-value is the fraction whose mean signed value is at least the observed mean,
including the observed assignment. The same exact test is reported separately
for each arm. Pooled trials are descriptive and cannot substitute for
participant-level inference.

## Frozen Gates

### H0: integrity, causality, and freeze

- all 15 participants, 30 participant-hand units, and both arms meet counts;
- all source-semantics and geometry hashes match H3;
- every included window passes the 30 ms motion guard;
- no final action or cue target reaches predictive code before freeze;
- exactly 660 fits and 900 prediction sets complete within caps;
- one aggregate hash-only freeze binds every source, split, role, feature,
  dependency, configuration, code, prediction, physiology, and firewall hash;
- the freeze commit is pushed and both CI jobs are green before target
  delivery; and
- target deliveries, scores, retries, reruns, and post-target updates equal
  `1 / 1 / 0 / 0 / 0`.

### H1: symmetric action-over-cue reversal

For each arm independently:

- pooled and macro-participant action balanced accuracy are at least `0.60`;
- at least 12 of 15 participant action accuracies exceed `0.50`;
- the exact one-sided arm-margin sign-flip p-value is at most `0.01`;
- macro action-minus-cue margin is at least `0.20`;
- macro cue-surrogate balanced accuracy is at most `0.40`; and
- macro action accuracy exceeds the train-only no-signal prior by at least
  `0.10`.

Across arms, the mean participant minimum-arm margin must be at least `0.15`
and its exact sign-flip p-value at most `0.01`.

### H2: recorded peripheral, visual, and timing controls

For each arm:

- primary action accuracy exceeds EOG-only by at least `0.05`;
- primary action accuracy exceeds occipital-only by at least `0.03`;
- EOG-orthogonalized action accuracy is at least `0.58` and its action-minus-
  cue margin at least `0.16`;
- EOG-only and occipital-only action-minus-cue margins are each at most `0.10`;
- timing-only and pre-window action accuracy are each at most `0.55`;
- all-zero, deranged-label, displaced-row, channel-permuted, and opposite-hand
  controls each remain at or below `0.55` action accuracy; and
- each fixed control action-minus-cue margin remains at or below `0.10`.

These controls reduce specific alternatives. They cannot prove brain-specific
origin because synchronized EMG is unavailable and unmeasured peripheral
sources may remain.

### H3: motor-compatible central support

For each arm:

- central macro action accuracy is at least `0.55`;
- central action-minus-cue margin is at least `0.10`;
- at least 10 of 15 participants exceed `0.50` central action accuracy; and
- early and late halves are reported separately.

The participant mean of the weaker central arm margin must be at least `0.08`.
Readiness-potential, central mu `8-13 Hz`, central beta `13-30 Hz`, and
motion-guard timing summaries must be complete and nonselecting. They cannot
rescue H1 or H2.

## Ordered Router

| Route | Frozen condition | Maximum interpretation |
|---|---|---|
| `IACKD2-R1` | H0 passes and both arms reliably favor cue surrogate | Fixed representation is symmetrically cue-bound |
| `IACKD2-R2` | H0 passes and exactly one arm passes H1 | Transfer is direction-asymmetric and cannot support the dual-reversal hypothesis |
| `IACKD2-R3` | H0 and both H1 arms pass, but H2 fails | Action alignment is present with source unresolved by registered controls |
| `IACKD2-R4` | H0, H1, and H2 pass, but H3 fails | Action alignment survives controls without motor-compatible central support |
| `IACKD2-R5` | H0 through H3 all pass | Within-IACKD pre-movement action-direction information survives symmetric cue reversals and registered controls, with motor-compatible central support |
| `IACKD2-R0` | Any remaining integrity, null, mixed, or incomplete outcome | The fixed design did not establish coherent symmetric action-over-cue transfer |

Routes are evaluated in the listed order; `R0` is the final catch-all. Even
`R5` is not proof of brain-specific origin, external generalization, thought
decoding, real-time operation, hardware capability, assistive benefit, or
clinical utility.

## Resource Caps

### Future generated-fixture implementation

```text
threads/workers/jobs:             1 / 1 / 1
wall time:                        120 seconds
peak RSS:                         512 MiB
generated output:                 8 MiB
real/public/local payload reads:  0
network bytes:                    0
```

### Future fresh acquisition and derivative build

```text
invocations/retries/reruns:       1 / 0 / 0
threads/workers/jobs:             1 / 1 / 1
wall time:                        7,200 seconds
peak RSS:                         2 GiB
metadata response bodies:         8 MiB
payload requests/bytes:           1,340 / 7,249,113,684
largest raw run group:            82,064,564 bytes
peak incremental disk:            1 GiB
minimum free disk:                10 GiB
private derivatives:              512 MiB
public/private receipts:          4 MiB / 4 MiB
```

### Future fit, freeze, and score

```text
registered executions:            1
threads/workers/jobs:              1 / 1 / 1
wall time through freeze:          10,800 seconds
peak RSS:                          2 GiB
private generated output:          512 MiB
public freeze/result:              4 MiB
parameter-update fits:             660 exact
prediction sets/inferences:        900 exact / 900 maximum
target deliveries/scores:          1 / 1
network/new payload bytes:         0 / 0
retries/reruns/post-target update: 0 / 0 / 0
```

## Publication Boundary

Public commits may contain only aggregate receipts, the hash-only prediction
freeze, and one aggregate result. They may not contain local paths, raw source
bodies, channel traces, trial rows, signed kinematics, targets, predictions,
probabilities, coefficients, participant outcomes, or private hashes that
permit individual reconstruction.

All raw temporary files and private derivatives remain Git-ignored. The
future executor may remove only invocation-created temporary raw run files;
it may not delete a pre-existing bundle, cache, derivative, project file, or
another project's content.

## Refusal Boundary

The future implementation must fail closed on evidence-hash drift, an ungreen
stage, dependency drift, insufficient disk, old-bundle access, metadata or
object drift, redirect, retry, path link, overwrite, raw-group cap breach,
source-semantics mismatch, geometry mismatch, trial join failure, motion-guard
failure, count failure, target leakage, inventory mismatch, incomplete freeze,
public privacy failure, second delivery, rerun, post-target update, or claim
boundary breach.

No substitution, threshold change, seed change, parser relaxation, cohort
reduction, model addition, restart, or post-result amendment is allowed.

## Claim Boundary

Engineering capability proposed: a storage-safe, role-aware, target-firewalled
dual-reversal experiment can test action alignment against the exact
cue-derived alternative in both mapping directions with participant-level
inference and registered confound controls.

Scientific claim not established: this preregistration accessed no IACKD
payload, retained bundle, signal, event, trajectory, target, model prediction,
or score, so it establishes no neural effect, action decoding, brain-specific
origin, unseen-person generalization, typing, language or thought decoding,
real-time operation, hardware capability, assistive benefit, or clinical use.
