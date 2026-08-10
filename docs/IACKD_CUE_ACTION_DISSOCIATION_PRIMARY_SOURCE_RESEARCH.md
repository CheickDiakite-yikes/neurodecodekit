# IACKD Cue-to-Action Reversal Primary-Source Research

Date: 2026-08-10

Status: **Tier A research complete; public candidate and metadata inventory
selected; no EEG, EOG, marker, event, kinematic, target, or label content
opened; no experiment preregistered, authorized, implemented, or run**

Machine records:

- `registries/iackd_cue_action_dissociation_research.v0.json`
- `registries/iackd_openneuro_metadata_inventory.v0.json`

Research lane: **IACKD-1 Cue-to-Action Reversal**

## Decision In One Sentence

Train one fixed low-frequency EEG family only where visual target direction and
actual hand direction agree, freeze it on held-out runs where they disagree,
and score the same predictions against both directions to find out which one
the representation follows.

## Why This Is The Needle-Moving Next Experiment

WO9R established the project's strongest real EEG result so far. The frozen
low-frequency model confirmed on twelve untouched people during execution and
imagery, and both task-transfer directions were positive. But the result
stopped at `WO9R-R3`: the early cue window and frontal proxy were stronger than
the central motor view, and the physiology conjunction failed.

That leaves a precise uncertainty. The model may carry action information, or
it may mostly follow the lateralized visual cue, eye behavior, or another
task-correlated signal. Training a larger model on the same task would not
answer that question.

IACKD changes the task rather than merely changing the classifier. On red
congruent trials, the controlled ball and hand move in the same direction. On
yellow incongruent trials, the hand must move opposite the ball. A predictor
trained only on congruent trials therefore faces a genuine reversal on the
held-out incongruent condition:

```text
congruent fit:      visual right  = hand right
incongruent final: visual right != hand left
```

One frozen prediction cannot agree with both labels. That makes the main
scientific alternative directly measurable rather than inferred from a weak
proxy.

## Primary-Source Basis

### The dataset contains the needed dissociation

The 2026 IACKD data descriptor reports 15 participants, 7,040 recorded trials
and 6,671 retained valid trials. Each trial contains a one-second pre-movement
period followed by movement execution. EEG was recorded from a 32-channel cap
at 1,024 Hz, while hand trajectories were recorded with Leap Motion at about
170 Hz.

Red marks a congruent mapping: hand and ball move in the same direction.
Yellow marks an incongruent mapping: hand and ball move in opposite directions.
The authors report readiness potentials around C3, C4, and Cz, mu/beta
dynamics, and cross-modal residuals within 30 ms for more than 99.375 percent
of trials.

Source: [IACKD data descriptor](https://doi.org/10.1038/s41597-026-07146-x)

### The public release is small enough for the approved machine envelope

OpenNeuro release `ds006840` version `1.0.0` is CC0 and BIDS 1.7.0. A
metadata-only S3 inventory observed 1,679 objects totaling 7,966,799,433
bytes. The selected raw-source subset contains exactly 1,340 objects and
7,249,113,684 bytes:

| Component | Objects | Bytes |
|---|---:|---:|
| BrainVision EEG signals | 128 | 6,432,882,432 |
| BrainVision headers and markers | 256 | 1,110,382 |
| EEG sidecars, events, channels, and geometry | 444 | 1,711,503 |
| Ball streams and sidecars | 256 | 118,637,996 |
| Leap Motion streams and sidecars | 256 | 694,771,371 |
| **Selected total** | **1,340** | **7,249,113,684** |

The selection excludes 717,671,039 bytes of published MATLAB derivatives,
participant demographics, subject scan tables, and root/source-code files.
The derivatives are smaller, but they use published zero-phase preprocessing,
remove EOG, and package labels with features. They are therefore the wrong
source for a new causal and target-firewalled test.

Source: [OpenNeuro ds006840 v1.0.0](https://openneuro.org/datasets/ds006840/versions/1.0.0)

The canonical metadata identity hash for the selected object paths, sizes,
ETags, and modification times is:

```text
c30b518f9dafe3d46128849725e1f2f8fdce33239fbf6ade8603d66a64f0ffa5
```

An S3 ETag is not a SHA-256 guarantee. A later authorized acquisition must
compute local SHA-256 values while keeping the upstream version, path, size,
and ETag bindings intact.

### Visual cues are a known movement-decoding confound

Primary research on executed movement shows that visual cue design can alter
movement-related potential timing, topography, and classification behavior.
This is exactly the ambiguity exposed by WO9R's strong early-cue and frontal
results. IACKD's reversal lets us test it instead of merely acknowledging it.

Source: [EEG analyses of visual cue effects on executed movements](https://doi.org/10.1016/j.jneumeth.2024.110241)

## Prospective Unit And Split

The inference unit is a participant, with moving hand retained as a nested
stratum. There are 30 participant-hand units.

For each participant and hand:

1. Use every run except the highest numbered run as the fit partition.
2. Use only red congruent trials for fitting.
3. Hold the highest numbered run as the sealed final partition.
4. Use only yellow incongruent trials for the final reversal test.
5. Fit a separate fixed model for each participant-hand unit.
6. Never mix rows across people, hands, or final runs.

Participants 04 and 05 have six runs per hand; the other participants have
four. Before quality control, the article's trial geometry implies at most
2,680 congruent fit trials and 840 incongruent final trials. The future exact
contract should require every participant and both hands, at least 24 fit
trials per direction per unit, and at least eight final trials per direction
per unit. Any failure parks the one-shot study rather than silently changing
the cohort.

## Exact Scientific Question

The fixed predictor sees congruent fit targets, where action and visual
direction are identical. On the held-out incongruent run, predictive code gets
only target-free EEG features and group/timing identities. It does not receive
the hand-direction sign, visual-direction sign, ball trajectory, or Leap
trajectory.

All final predictions freeze first. The isolated scorer then opens two sealed
target views together:

1. actual hand direction, confirmed by Leap displacement; and
2. visual ball or target direction.

The scorer applies both views to the exact same predictions. If predictions
follow the hand, action balanced accuracy rises above 0.5 and visual-direction
accuracy falls below 0.5. If predictions follow the cue, the pattern reverses.

## Frozen Model Recommendation

Use the same compact representation family that produced the WO9R lead,
adapted only to IACKD's registered one-second pre-movement interval:

```text
reference:          instantaneous common average over verified EEG channels
filter:             fourth-order Butterworth 0.5-4 Hz, SOS form
application:        causal continuous-run filtering before windowing
window:             [-1.0, 0.0) seconds relative to the registered stop
features/channel:   four 250 ms means plus one whole-window slope
feature dimension:  5C, expected 160 at 32 EEG channels
classifier:         participant-hand-specific shrinkage LDA
solver/shrinkage:   lsqr / 0.1
class priors:       equal
model candidates:   1
hyperparameter runs: 0
right context:      0 seconds
```

The registered stop is the earlier of event 14 and measured kinematic onset
minus 30 ms. Leap speed may define onset, but its direction sign must remain
sealed from predictive code. This is an offline, oracle-aligned pre-movement
assay, not a real-time decoder. End-to-end latency is not measured.

## Mandatory Parallel Controls

The later preregistration should freeze all conditions together:

- whole-head EEG scored against hand direction;
- the same predictions scored against visual direction;
- C3/C4/Cz-only EEG;
- HEOG/VEOG-only prediction;
- whole-head EEG after a fit-only frozen EOG nuisance projection;
- early and late halves of the pre-movement window;
- a pre-window baseline;
- timing-only and train-only no-signal baselines;
- all-zero final signal;
- fixed train-label, run-displacement, channel, and hand-entity controls;
- the target-blind kinematic-onset guard; and
- nonselecting readiness-potential and mu/beta summaries.

The raw source is valuable here because the article explicitly reports HEOG
and VEOG channels before its published preprocessing removed them. EOG can
therefore be a recorded comparator rather than a frontal-channel guess. There
is no synchronized EMG, so even clean EOG and kinematic controls cannot prove
absolute cortical origin.

## Recommended Gates

### H1: action-over-cue reversal

- pooled and macro-participant hand-direction balanced accuracy at least 0.60;
- at least 12 of 15 participants above 0.50;
- exact participant-level sign-flip `p <= 0.01`;
- macro hand-minus-visual balanced-accuracy margin at least 0.20;
- visual-direction balanced accuracy at most 0.40; and
- at least 0.10 macro margin over the train-only no-signal prior.

Participant-level inference is mandatory. Hundreds of trials cannot be
pretended to be hundreds of independent people.

### H2: recorded peripheral and timing controls

- primary macro action accuracy exceeds EOG-only by at least 0.05;
- fit-only EOG-orthogonalized EEG remains at least 0.58 macro action accuracy;
- its action-minus-visual margin remains at least 0.16;
- timing-only and pre-window controls stay at or below 0.55; and
- no fixed derangement or displacement condition rescues the result.

### H3: motor-compatible support

- C3/C4/Cz action balanced accuracy reaches at least 0.55;
- central predictions follow action rather than visual direction;
- early and late halves are reported separately; and
- readiness-potential and mu/beta summaries are nonselecting and cannot rescue
  failed predictive or confound gates.

### H4: integrity and causality

- all 30 participant-hand units pass the target-blind motion guard;
- no final hand or visual direction reaches predictive code before freeze;
- every prediction and control set freezes together;
- both final target views open in one combined delivery only after the public
  hash-only freeze is committed, pushed, and remotely green; and
- post-target updates and reruns remain zero.

## Outcome Router

| Verdict | Meaning |
|---|---|
| `IACKD-R0` | The fixed representation does not generalize cleanly to the conflict test. |
| `IACKD-R1` | Predictions follow the visual target more than the hand; the lead is cue-bound under reversal. |
| `IACKD-R2` | Predictions follow the hand, but EOG or timing controls leave source unresolved. |
| `IACKD-R3` | Action alignment survives recorded EOG, timing, and integrity controls, but motor localization is incomplete. |
| `IACKD-R4` | Action alignment, recorded controls, central support, and integrity all pass within IACKD. |

Even `IACKD-R4` means a within-dataset pre-movement motor-compatible EEG
action-direction effect. It does not prove brain-specific origin, independent
replication, unseen-person generalization, typing, language or thought
decoding, real-time operation, portable hardware, home use, assistive benefit,
or clinical utility.

## Machine And Storage Boundary

The future lane should stay inside:

```text
CPU threads/workers/jobs:     1 / 1 / 1
exact selected payload:       7,249,113,684 bytes
provider payload ceiling:     10 GiB
incremental disk ceiling:     9 GiB
minimum free disk:            20 GiB
peak RSS ceiling:             2 GiB
private derivative ceiling:   512 MiB
public aggregate ceiling:     2 MiB
published derivatives:        0 bytes
retries/reruns:               0 / 0
```

The current machine reported 44 GiB free during this research pass. That is
capacity evidence only. It does not authorize acquisition.

## Ordered Next Work

1. Freeze the exact preregistration and bind the metadata inventory.
2. Prepare a separate all-false Tier C request.
3. After that request is committed, pushed, and remotely green, accept one
   unambiguous packet-bound maintainer decision.
4. Qualify acquisition, parsing, target firewall, controls, freezer, and
   scorer only on generated fixtures and mocked transport.
5. Require the exact implementation commit to be remotely green before any
   payload request.
6. Acquire only the 1,340 registered objects, sequentially and without retry.
7. Freeze all final predictions before one combined target delivery and one
   score.

## Claim Boundary

Engineering capability added: a metadata-bound prospective design now turns
the cue-versus-action ambiguity into a direct reversal test with synchronized
EOG and kinematic controls.

Scientific claim not established: no IACKD payload content was opened and no
prediction was made, so this record establishes no new EEG effect, action
decoding, brain-specific origin, unseen-person generalization, typing,
language or thought decoding, real-time operation, portable hardware, home
use, assistive benefit, or clinical utility.
