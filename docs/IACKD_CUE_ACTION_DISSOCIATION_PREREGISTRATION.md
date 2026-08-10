# IACKD Cue-to-Action Reversal Preregistration

Date: 2026-08-10

Status: **Frozen prospective contract; exact packet-bound Tier C decision
pending; no IACKD payload acquired, opened, parsed, trained on, inferred from,
or scored**

Contract:
`registries/iackd_cue_action_dissociation_contract.v0.json`

Research basis:
`docs/IACKD_CUE_ACTION_DISSOCIATION_PRIMARY_SOURCE_RESEARCH.md`

Lane: **IACKD-1 Cue-to-Action Reversal**

## Objective

Test whether the fixed low-frequency representation that survived WO9R follows
actual hand direction or visual target direction when those variables are
forced to disagree.

The experiment trains only on congruent trials, where hand and target point in
the same direction. It freezes predictions on held-out incongruent trials,
where hand and target point in opposite directions. The isolated scorer then
applies both target views to the exact same predictions.

This is not a model search, a WO9R rerun, or permission to acquire or inspect
IACKD. It freezes one future operation so its outcome cannot change the
question after the data are seen.

## Green Research Anchor

Research commit
`d6f955e59e210a045d54e1fdb013e4bc7a9235d7` passed CI
`31399402403`:

- Base Python job `93490301532` passed;
- Optional Neuro Readers job `93490301603` passed;
- the metadata inventory remained under 1 MiB; and
- no payload URL, EEG/EOG content, event, marker, trajectory, target, model,
  prediction, or score was accessed.

The frozen public metadata inventory is
`registries/iackd_openneuro_metadata_inventory.v0.json`, SHA-256
`aeaa4928192cca9086fcb0abf4711147c68a68ef5c5aacda2ebc67d162a1ef19`.

## Exact Dataset Boundary

```text
provider:                     OpenNeuro
accession/version:            ds006840 / 1.0.0
DOI:                          10.18112/openneuro.ds006840.v1.0.0
license:                      CC0
participants:                 sub-01 through sub-15
moving-hand strata:           left and right
participant-hand units:       30
BIDS run files:               128
selected objects:             1,340
exact selected bytes:         7,249,113,684
published derivatives:        excluded
participant demographics:     excluded
subject scan tables:           excluded
```

The contract incorporates the inventory by exact SHA-256. Every selected
object path, byte size, S3 ETag, and modification time is therefore frozen
without duplicating 1,340 records into a second file. The expanded canonical
identity SHA-256 is:

```text
c30b518f9dafe3d46128849725e1f2f8fdce33239fbf6ade8603d66a64f0ffa5
```

The future acquisition must compare a new metadata listing to that identity
before requesting an object body. ETags are upstream metadata, not SHA-256.
The acquisition must compute one local SHA-256 per object while streaming it.

## Ordered Evidence Sequence

The preregistration authorizes nothing. A future operation is valid only in
this order:

1. commit and push this registration and pass both CI jobs;
2. commit and push one all-false authorization packet and pass both CI jobs;
3. record the maintainer's actual packet-bound decision in a separate commit;
4. pass both CI jobs on that decision commit;
5. implement and qualify acquisition, parsing, firewall, models, controls,
   freezer, and scorer using generated fixtures and mocked transport only;
6. commit and push that exact implementation and pass both CI jobs;
7. reverify metadata and acquire the exact 1,340 objects once;
8. perform one target-blind analysis and freeze every prediction set;
9. commit and push the aggregate hash-only freeze and pass both CI jobs; and
10. deliver both target views together once, score once, route, and stop.

No earlier `continue`, general autonomy statement, 10 GB allowance, WO9/WO9R
decision, or public-data approval substitutes for the later packet-bound
decision.

## One Exact Acquisition

After a green decision and green implementation, one sequential acquisition
may:

1. re-read only the registered OpenNeuro dataset description, CHANGES file,
   and two-page S3 object listing;
2. reconstruct and compare the exact canonical inventory hash;
3. refuse before payload transfer on any version, DOI, license, path, size,
   ETag, modification-time, object-count, or total-byte mismatch;
4. request the 1,340 allowlisted object bodies once each, sequentially and
   without retry or redirect;
5. verify response path, content length, and ETag;
6. compute SHA-256 while writing each object, without parsing its content;
7. promote only a complete bundle into a new isolated final root; and
8. emit one private machine manifest and one bounded human receipt.

The acquisition may not import MNE, parse a header or TSV, read a marker,
sample, trajectory, event, target, or channel, create a split, or run a model.
An interrupted or failed payload invocation is consumed and parks the lane.

## Exact Participant-Hand Split

Each participant and moving hand is a separate model and final inference unit.

| Unit type | Fit runs | Sealed-final run |
|---|---|---|
| `sub-04` and `sub-05`, each hand | runs 01-05 | run 06 |
| every other participant, each hand | runs 01-03 | run 04 |

Only red congruent trials enter fitting. Only yellow incongruent trials from
the sealed-final run enter prediction. No row-random split, cross-participant
fit, cross-hand fit, real-data model selection, or final-run adaptation exists.

The article geometry gives maximum pre-QC counts of 2,680 congruent fit trials
and 840 incongruent final trials. Counts after target-blind quality checks are
not invented in advance. Every one of the 30 units must retain at least 24 fit
trials per direction and eight final trials per direction. Otherwise the one
execution parks before prediction.

## Reader And Trial Reconciliation

The future reader is restricted to the exact raw-source bundle and must:

- no-follow verify every regular path against the private manifest;
- make one new sequential size/SHA-256 pass over all 1,340 objects;
- parse one BrainVision recording at a time with MNE `1.12.1`;
- require exactly 32 EEG channels plus `M1`, `M2`, `HEOG`, and `VEOG`;
- retain all 32 EEG channels, both EOG channels, and available geometry;
- require 1,024 Hz EEG sampling;
- reconcile only event 55, event 14, and boundary-hit event 66 or its
  registered exported equivalent;
- parse source ball and Leap streams with the standard library;
- join each trial by participant, hand, run, trial identity, and synchronized
  timestamps;
- apply no ICA, interpolation, bad-channel deletion, amplitude rejection,
  zero-phase filtering, or target-derived exclusion; and
- stream compact features without persisting raw EEG or EOG windows.

The contract accepts target-blind validity checks only: finite samples,
complete time coverage, successful boundary hit, exact marker order, exact
cross-stream identity, sufficient pre-movement history, and the frozen motion
guard. Every exclusion reason and count is aggregated before prediction. A
minimum-count failure parks the complete experiment rather than changing the
cohort.

## Target-Blind Motion Guard

The Leap trajectory serves two different roles separated by process and
artifact boundaries.

Predictive preprocessing may receive only absolute three-dimensional speed and
a derived onset timestamp. It never receives signed displacement, final x
position, visual direction, or action direction.

The onset detector is frozen as:

```text
native timestamps:       strictly increasing Leap timestamps
speed:                   Euclidean first-difference displacement / delta time
baseline:                samples during the available pre-movement interval
threshold:               max(20 mm/s, baseline median + 10 * baseline MAD)
persistence:             3 consecutive native Leap samples
registered stop:         min(event-14 time, detected onset - 30 ms)
EEG window:              [registered stop - 1.0 s, registered stop)
```

No EEG sample at or after the registered stop is used. An onset more than 30
ms before event 14, missing persistence, nonfinite kinematics, or inadequate
history fails the trial's target-blind guard. The use of offline measured onset
makes this an oracle-aligned causal-in-samples assay, not a real-time system.

The isolated target builder separately computes signed x displacement. For
each stream, direction is the sign of the median x position over the final 20
percent of execution minus the median over the first 20 percent. Hand
displacement must have magnitude at least 5 mm; ball displacement must have
magnitude at least 5 pixels. Congruent fit trials require equal signs, while
incongruent final trials require opposite signs. The ball stream's categorical
`move_direct` value must agree, but it is not the sole target source. All
signed values remain sealed from predictive code.

## Target Firewall

Fit rows may expose actual direction because congruent action and visual
direction are identical. Final rows expose only:

- EEG features;
- participant and moving-hand group identities;
- run and opaque trial identities;
- target-blind timing and quality fields;
- condition ID `incongruent`; and
- source/feature/configuration hashes.

The final firewall writes one isolated sealed scorer input containing both:

1. actual hand direction from signed Leap displacement; and
2. visual target direction from signed ball displacement.

It verifies that the two final labels are opposites, then hides both. No final
direction, trajectory sign, ball x position, label, probability, prediction,
or participant outcome appears in the public freeze.

## Frozen Preprocessing And Primary Model

```text
EEG reference:        instantaneous common average across all 32 EEG channels
filter:               fourth-order Butterworth 0.5-4 Hz in SOS form
application:          causal scipy.signal.sosfilt over each continuous run
window:               [-1.0, 0.0) seconds from the registered stop
features/channel:     four 250 ms means plus one whole-window slope
feature dimension:    160
classifier:           participant-hand-specific LDA
solver:               lsqr
shrinkage:            0.1
class priors:         equal
fit source:           congruent fit runs only
selection choices:    1
hyperparameter runs:  0
right context:        0 seconds
```

No normalization may see a final row. Every scale, nuisance projection, LDA
coefficient, class prior, and threshold is fitted from the unit's congruent fit
rows only. There is no deep network, CML-v0, foundation model, LLM, pretrained
checkpoint, test-time adaptation, or post-target update.

## EOG Nuisance Projection

The EOG-orthogonalized condition uses the same 160 EEG features and ten EOG
features. Within each participant-hand fit partition only, a fixed ridge
projection predicts each EEG feature from an intercept plus EOG features with
`lambda = 0.001`. The frozen projection is applied to final EEG features, and
the same fixed LDA recipe is fitted to residual fit features.

No final EOG row updates the projection. The HEOG/VEOG-only condition is a
separate ten-feature LDA. Failure of either EOG control cannot prove absolute
cortical origin because synchronized EMG is unavailable.

## Exact Prediction Matrix

Each of 30 participant-hand units has ten fit operations:

1. whole-head primary;
2. C3/C4/Cz central EEG;
3. HEOG/VEOG only;
4. fit-only EOG-orthogonalized whole-head EEG;
5. early half `[-1.0, -0.5)`;
6. late half `[-0.5, 0.0)`;
7. pre-window baseline `[-2.0, -1.0)`;
8. event-index and timing only;
9. fixed train-label derangement; and
10. train-only no-signal prior.

That is exactly 300 maximum parameter-update fits.

Each unit freezes 14 prediction sets:

1. whole-head primary;
2. central EEG;
3. EOG only;
4. EOG-orthogonalized EEG;
5. early half;
6. late half;
7. pre-window baseline;
8. timing only;
9. train-only no-signal prior;
10. all-zero final EEG through the primary model;
11. train-label derangement;
12. one-row cyclic final-feature displacement;
13. fixed final-only EEG-channel permutation; and
14. opposite-hand primary model applied without adaptation.

A valid freeze therefore requires exactly 420 participant-condition prediction
sets and at most 420 target-blind inference calls. The primary predictions are
stored once and later scored against both sealed target views. Scoring twice
does not create a second prediction set.

The label derangement uses seed `6841`; the EEG-channel permutation uses seed
`6842`. Both operate independently within the registered unit and are expanded
canonically before real content access. Final displacement is a one-row cyclic
shift within unit order. No seed or permutation may be replaced.

## Nonselecting Physiology

The freeze also binds, without scoring them:

- mean C3, C4, and Cz readiness-potential traces over the registered window;
- central mu-band `8-13 Hz` and beta-band `13-30 Hz` causal power summaries;
- early-versus-late central negativity; and
- aggregate motion-guard timing distributions.

These summaries are descriptive. They cannot select a model, channel, window,
threshold, participant, or trial, and they cannot rescue failed predictive or
confound gates.

## Frozen Gates

### H1: action-over-cue reversal

All conditions must hold:

- pooled and macro-participant hand-direction balanced accuracy `>= 0.60`;
- at least 12 of 15 participant action accuracies above `0.50`;
- exact participant sign-flip `p <= 0.01` on action-minus-visual margins;
- macro hand-minus-visual balanced-accuracy margin `>= 0.20`;
- macro visual-direction balanced accuracy `<= 0.40`; and
- macro action margin over the train-only no-signal prior `>= 0.10`.

### H2: recorded peripheral and timing controls

All conditions must hold:

- primary minus EOG-only macro action accuracy `>= 0.05`;
- EOG-orthogonalized macro action accuracy `>= 0.58`;
- EOG-orthogonalized macro action-minus-visual margin `>= 0.16`;
- timing-only and pre-window macro action accuracy each `<= 0.55`;
- all-zero, label-deranged, displaced, channel-permuted, and hand-swapped
  controls each stay below `0.55` macro action accuracy; and
- no control has an action-minus-visual margin above `0.10`.

### H3: motor-compatible support

All conditions must hold:

- C3/C4/Cz macro action accuracy `>= 0.55`;
- central action-minus-visual margin `>= 0.10`;
- at least 10 of 15 participants have central action accuracy above `0.50`;
- late-half action accuracy is reported beside early-half accuracy; and
- the readiness-potential and mu/beta records are complete and nonselecting.

No directional sign is preregistered for readiness-potential or mu/beta
differences because the decoded class is trajectory direction within a moving
hand, not left-hand versus right-hand movement.

### H4: integrity and causality

All conditions must hold:

- all 15 participants and 30 participant-hand units meet minimum counts;
- all included windows pass the 30 ms motion guard;
- final target values reaching predictive code before freeze equal zero;
- all 300 fits and all 420 prediction sets complete within caps;
- one combined hash-only freeze binds every source, split, feature,
  dependency, configuration, code, prediction, physiology, and firewall hash;
- that freeze is committed, pushed, and green in both CI jobs before targets;
- the two target views open together once; and
- reruns, retries, and post-target updates equal zero.

## Exact Participant-Level Test

For each participant, combine its left- and right-hand final confusion counts
before computing balanced accuracy. Define the primary participant value as:

```text
balanced_accuracy(actual_hand) - balanced_accuracy(visual_target)
```

Enumerate all `2^15 = 32,768` sign assignments. The one-sided p-value is the
fraction whose mean signed margin is at least the observed mean margin,
including the observed assignment. No pooled-trial binomial test may substitute
for this participant-level test.

## Ordered Router

| Verdict | Frozen condition | Maximum claim |
|---|---|---|
| `IACKD-R1` | Predictions align more with visual target than hand | Representation is cue-bound under the registered reversal |
| `IACKD-R0` | Integrity or H1 fails without stronger visual alignment | Fixed low-frequency representation did not generalize cleanly to conflict |
| `IACKD-R2` | H1 passes but H2 or H4 fails | Action-aligned task information with source unresolved |
| `IACKD-R3` | H1, H2, H4 pass; H3 fails | Pre-movement action alignment survives recorded EOG/timing controls without motor localization |
| `IACKD-R4` | H1-H4 all pass | Within-IACKD pre-movement motor-compatible EEG action-direction effect under synchronized controls, not brain-specific |

`IACKD-R1` is tested before `IACKD-R0` when visual alignment is reliable, so a
clean cue-bound failure is localized rather than collapsed into generic null.

## Resource Caps

### Acquisition

```text
invocations/retries/reruns:  1 / 0 / 0
threads/workers/jobs:        1 / 1 / 1
wall time:                   7,200 seconds
peak RSS:                    512 MiB
metadata response bodies:    8 MiB
payload requests:            1,340
payload bytes:               7,249,113,684
incremental disk:            9 GiB
minimum free disk:           20 GiB
private receipts:            4 MiB
```

### Analysis And Score

```text
registered executions:       1
threads/workers/jobs:        1 / 1 / 1
wall time through freeze:     3,600 seconds
peak RSS:                    2 GiB
private generated output:    512 MiB
public freeze/result:        2 MiB
parameter-update fits:       300 maximum
prediction sets/inferences:  420 exact / 420 maximum
target deliveries/scores:    1 / 1
network/new payload:         0 / 0 bytes
retries/reruns/updates:       0 / 0 / 0
```

Raw files are streamed one run at a time. Raw windows may not be persisted or
duplicated. The isolated existing classical environment may be reused only if
it reports NumPy `2.5.2`, SciPy `1.18.0`, MNE `1.12.1`, and scikit-learn
`1.9.0` exactly. No dependency installation or tooling network is part of this
contract.

## Publication Boundary

Only these public artifacts may be committed:

- the metadata inventory and preregistration;
- an aggregate acquisition receipt with no local path;
- a hash-only prediction freeze with no individual output; and
- one aggregate result with no target, prediction, probability, trajectory,
  channel trace, or participant outcome.

The 7.25 GB bundle, local SHA-256 manifest, parsed arrays, trial table, signed
kinematics, fit labels, final labels, features, model coefficients, individual
predictions, and participant outcomes remain private and Git-ignored.

## Refusal Boundary

The future executor must stop on any unregistered object, redirect, retry,
version drift, inventory drift, path link, overwrite, insufficient free disk,
cap breach, channel/sampling mismatch, marker mismatch, stream mismatch,
motion-guard failure, minimum-count failure, target leak, missing condition,
missing prediction set, pre-freeze target request, dependency drift, second
delivery, rerun, or post-target update.

No failure permits substitution, cohort reduction, threshold revision, seed
change, model change, new download, or restart.

## Claim Boundary

Engineering capability added: a strict target-firewalled preregistration now
defines one cue-to-action reversal experiment with synchronized EOG and
kinematic controls, exact resources, and an outcome router.

Scientific claim not established: this preregistration opened no IACKD payload
and made no prediction, so it establishes no EEG effect, action decoding,
brain-specific origin, unseen-person generalization, typing, language or
thought decoding, real-time operation, portable hardware, home use, assistive
benefit, or clinical utility.
