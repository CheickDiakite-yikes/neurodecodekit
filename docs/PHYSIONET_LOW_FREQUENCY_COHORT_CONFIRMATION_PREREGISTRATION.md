# PhysioNet Low-Frequency Cohort Confirmation Preregistration

Date: 2026-08-09

Status: **Frozen prospective contract; exact Tier C authorization pending; no
EDF payload acquired, opened, parsed, trained on, inferred from, or scored**

Contract:
`registries/physionet_low_frequency_cohort_confirmation_contract.v0.json`

Research basis:
`docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PRIMARY_SOURCE_RESEARCH.md`

Lane: **WO9R**, additive to the numbered work orders

## Objective

Test whether the prespecified Work Order 9 `0.5-4 Hz` whole-head comparator
confirms on twelve untouched EEGMMIDB participants, then route task
information, execution/imagery robustness, and motor-compatible localization
as separate questions.

This is a prospective confirmation of one previously observed model template.
It is not permission to acquire data or execute the experiment, and it is not
a search over filters, windows, channels, classifiers, thresholds, or cohorts.

## Why This Is Frozen Now

Work Order 9's selected `8-30 Hz` model failed, but its prespecified
low-frequency comparator reached `36/45` correct, pooled balanced accuracy
`0.800395`, macro-participant balanced accuracy `0.800595`, and one-sided
`p=0.000183` on held-out run 11 for S001-S003. The result also failed the
registered motor-physiology route: a frontal/occipital proxy outperformed the
central sensorimotor model.

WO9R therefore asks two falsifiable questions before any larger architecture:

1. Does the exact low-frequency template confirm in new people?
2. If it confirms, does its spatial, temporal, execution/imagery, and
   lateralization pattern look more motor-compatible than cue/confound-like?

S001-S003, their targets, and their private outputs remain consumed. They are
not part of the new inventory, fitting data, thresholds, or scoring.

## Metadata-Only Registration Pass

The exact inventory was assembled without requesting an EDF URL. The pass read
only:

- twelve public `ListObjectsV2` XML responses from PhysioNet's official
  `physionet-open` AWS bucket, one prefix for each of S004-S015; and
- the official EEGMMIDB v1.0.0 `SHA256SUMS.txt` metadata document.

The twelve listing bodies total `80,784` bytes. The checksum-manifest body is
`259,919` bytes. The retained registration metadata bodies therefore total
exactly `340,703` bytes across 13 successful metadata GETs. HTTP headers and
earlier public research-tool transfer bytes were not retained, so total
network transfer including those fields is explicitly unavailable.

The listing responses supplied exact object paths and sizes; the official
manifest supplied one SHA-256 per selected EDF. No HTTP HEAD or GET was sent to
an EDF URL, and no EDF byte, header, annotation, event, sample, target, channel,
or geometry value was transferred or opened. The canonical expanded 72-file
inventory SHA-256 is:

```text
41906e8c74cafdcaa99354baab8acd4927127a73e7454939429dbca2a8c03dad
```

Canonicalization is UTF-8 JSON with keys sorted, no insignificant whitespace,
and records ordered by subject then run. Each record contains exactly `path`,
`subject`, `run`, `task`, `role`, `size_bytes`, and `sha256`.

## Exact Dataset Identity

```text
provider:                    PhysioNet
dataset:                     eegmmidb
version:                     1.0.0
DOI:                         10.13026/C28G6P
license:                     ODC-By-1.0
participants:                S004-S015 inclusive
execution fit runs:          03 and 07
execution sealed-final run:  11
imagery fit runs:            04 and 08
imagery sealed-final run:    12
EDF files:                   72
fit EDF files:               48
sealed-final EDF files:      24
event sidecars:              0
exact payload bytes:         184,252,032
fit-file bytes:              122,834,688
sealed-final-file bytes:     61,417,344
```

The machine contract stores one exact size and official SHA-256 for every
subject/run pair. Paths expand only as `{subject}/{subject}R{run}.edf`. No
wildcard, participant, run, companion, or substitute is allowed.

## Prospective Acquisition Boundary

After, and only after, a separate exact authorization-only decision and a
fixture-qualified implementation are each committed, pushed, and remotely
green, a future acquisition stage may:

1. Reverify the dataset page, task mapping, official checksum manifest, and
   twelve exact S3 metadata prefixes.
2. Refuse before payload transfer if any selected path, size, checksum,
   version, DOI, license, or public-access field differs.
3. Download only the 72 registered EDF files into a new isolated temporary
   root, sequentially, with no retry.
4. Opaquely stream each completed local EDF through SHA-256 exactly once,
   without parsing it.
5. Promote only a complete 72-file verified bundle into the absent frozen
   final root.
6. Emit one bounded machine manifest and human receipt.

The acquisition stage may not import MNE, parse EDF content, read an annotation
or sample, create a split, or run a model. It is one invocation, not a general
downloader.

## Target Firewall And Split

Every participant receives a separate model. There is no row-random split and
no cross-participant fit.

| Task | Fit runs | Sealed-final run | Expected fit trials | Expected final trials |
|---|---|---|---:|---:|
| Execution | 03, 07 | 11 | 360 | 180 |
| Imagery | 04, 08 | 12 | 360 | 180 |
| Total | 4 runs/person | 2 runs/person | 720 | 360 |

Each selected EDF must contain exactly 15 usable `T1`/`T2` task events after
strict parsing. A mismatch parks the one-shot execution without exclusion or
replacement.

An EDF reader necessarily materializes annotation values. The registered
target firewall must immediately separate run-11 and run-12 targets into one
isolated sealed scorer input and expose only target-free final features,
timestamps, group identities, and row hashes to predictive code. This is not a
claim that target bytes remain physically unopened. It is a claim that final
targets are unavailable to fitting, model-family choice, threshold choice,
channel choice, normalization, prediction generation, and the public
prediction-freeze ledger.

All run-11 and run-12 predictions must freeze together. Both final target sets
are delivered together exactly once to the isolated scorer only after the
hash-only freeze commit is pushed and both required CI jobs are remotely green.
Opening either target set to revise the other is forbidden.

## Exact Signal Contract

The real reader is restricted to MNE `>=1.12,<1.13` and must:

- verify the private acquisition manifest and all 72 regular no-follow paths;
- make one new sequential size/SHA-256 pass and one semantic parse per EDF;
- standardize the exact 64 EEGBCI channel names and require their exact order;
- retain all 64 EEG channels and available standard-1005 geometry;
- require 160 Hz sampling and only `T0`, `T1`, and `T2` annotations;
- retain `T1` and `T2` as left/right only for the six unilateral runs;
- apply no resampling, ICA, interpolation, target-derived rejection, or
  evaluation-time normalization; and
- stream compact features without persisting raw signal windows.

Any header, channel, geometry, sampling, annotation, event-count, finite-value,
duration, hash, or path mismatch parks the execution. No participant, channel,
epoch, or trial may be silently dropped.

## Frozen Primary Model

The only primary template is the exact Work Order 9 low-frequency comparator:

```text
reference:          instantaneous common average across all 64 channels
filter:             fourth-order Butterworth 0.5-4 Hz in SOS form
application:        causal scipy.signal.sosfilt on each continuous run
decision window:    +1.0 through +3.0 seconds from cue onset
features/channel:   four consecutive 500 ms means plus one window slope
feature dimension:  320
classifier:         participant-specific LDA, lsqr, shrinkage 0.1
class priors:        equal, fit rows only
right context:      0 seconds relative to the +3.0 second decision
selection choices:  1
hyperparameter runs: 0
```

This is cue-causal and has a three-second decision latency. It is not
pre-movement, asynchronous, continuous, or end-to-end real-time decoding.
Actual movement onset is unavailable.

## Fixed Channel And Temporal Views

All views use the all-64 common-average reference before a channel subset is
selected.

- Left sensorimotor: `FC5, FC3, FC1, C5, C3, C1, CP5, CP3, CP1`
- Right sensorimotor: `FC6, FC4, FC2, C6, C4, C2, CP6, CP4, CP2`
- Frontal/ocular-sensitive: `Fp1, Fpz, Fp2, AF7, AF3, AFz, AF4, AF8`
- Occipital/visual-sensitive: `PO7, PO3, POz, PO4, PO8, O1, Oz, O2`
- Frontal-asymmetry left: `Fp1, AF7, AF3`
- Frontal-asymmetry right: `Fp2, AF8, AF4`
- Early cue window: `0.0` through `1.0` seconds, four 250 ms means plus slope
- Pre-cue window: `-2.0` through `0.0` seconds, four 500 ms means plus slope

The frontal-asymmetry model receives one value per trial: left-group minus
right-group mean filtered potential over `+1.0` through `+3.0` seconds. It is
an ocular-sensitive proxy, not measured EOG.

## Exact Predictive Work

There are twelve parameter-update fits per participant, exactly 144 total:

1. execution whole-head primary;
2. imagery whole-head primary;
3. execution central sensorimotor;
4. execution frontal proxy;
5. execution occipital proxy;
6. execution frontal asymmetry;
7. execution early cue;
8. execution pre-cue;
9. execution timing-only;
10. execution no-signal prior;
11. imagery no-signal prior; and
12. execution fixed train-label derangement.

The two whole-head models are reused unchanged for bidirectional task transfer.
The execution primary is reused for all-zero, one-trial displacement, and
channel-derangement predictions. The central model is reused for the hemisphere
swap. Reuse does not create an additional fit.

There are exactly 18 prediction-condition families and 216 participant-
condition prediction sets. At the expected 15 rows per final run, the private
freeze binds 3,240 individual predictions. No probability, target, individual
prediction, or participant outcome is committed.

The target-blind timing-only features are normalized event ordinal, seconds
since run start, and previous inter-event interval. The first previous interval
is fixed to zero. No future event time is used.

The train-label permutation is the literal 15-index mapping in the machine
contract, applied separately within each fit run. Final-signal displacement is
a within-participant circular shift by one event. The channel derangement is a
literal 64-index permutation. Hemisphere swap exchanges the nine registered
left/right sensorimotor pairs. None is generated from a final target.

## Low-Frequency Physiology Assay

The scorer computes one independent descriptive assay from frozen final
features after target delivery:

- baseline: `-1.0` through `0.0` seconds;
- active: `+1.0` through `+3.0` seconds;
- signal: mean `0.5-4 Hz` filtered potential;
- contralateral side: right channels for left-fist targets and left channels
  for right-fist targets;
- registered statistic: ipsilateral active-minus-baseline minus contralateral
  active-minus-baseline; and
- registered direction: greater than zero, consistent with stronger
  contralateral negativity.

The assay cannot select, rescue, or update a model. Mu/beta ERD is not part of
the primary or router.

## Frozen Gates

### H1: execution-native cohort confirmation

All conditions must hold over the expected 180 run-11 trials:

- at least `117/180` correct;
- pooled balanced accuracy at least `0.65`;
- macro-participant balanced accuracy at least `0.625`;
- at least `9/12` participants strictly above `0.50` balanced accuracy;
- exact one-sided participant sign-flip `p <= 0.01`; and
- pooled and macro balanced-accuracy margins over the execution no-signal
  prior of at least `0.10`.

The sign-flip unit is the participant, not the trial.

### H2: imagery-native task-mode robustness

All conditions must hold over the expected 180 run-12 trials:

- pooled and macro-participant balanced accuracy at least `0.60`;
- at least `8/12` participants strictly above `0.50`; and
- exact one-sided participant sign-flip `p <= 0.05`.

Execution-to-imagery and imagery-to-execution transfer are reported in both
directions but cannot rescue H1 or H2.

### H3: motor-compatible localization

All conditions must hold on execution-final data:

- central pooled and macro balanced accuracy at least `0.60`;
- central pooled and macro accuracy exceed the strongest frontal, occipital,
  or frontal-asymmetry proxy by at least `0.05`;
- the central-minus-strongest-proxy participant differences pass an exact
  paired one-sided sign-flip test at `p <= 0.05`;
- at least `8/12` participants have the registered low-frequency
  lateralization direction; and
- the participant-level lateralization values pass an exact one-sided
  sign-flip test at `p <= 0.05`.

For the strongest route, frontal, occipital, frontal-asymmetry, early-cue,
pre-cue, timing-only, all-zero, train-label-deranged, one-trial-displaced, and
channel-deranged execution predictions must each remain below `0.60` pooled
and macro balanced accuracy. The central hemisphere-swap control must remain
below `0.60` and at least `0.05` below the unswapped central model. Execution
and imagery no-signal balanced accuracy must equal `0.50` when both final
classes are present.

These controls make the result more failure-addressable. They do not prove a
cortical source or complete removal of ocular, visual, muscle, timing, or
movement confounds.

## Ordered Verdict Router

| Verdict | Condition | Maximum interpretation |
|---|---|---|
| `WO9R-R0` | Integrity, event, target-firewall, freeze, access-order, or resource gate fails | Invalid or incomplete registered execution |
| `WO9R-R1` | H1 fails | The three-person low-frequency effect did not confirm under the frozen cohort test |
| `WO9R-R2` | H1 passes but H2 fails | Execution-task information confirmed in a new cohort, without imagery robustness |
| `WO9R-R3` | H1 and H2 pass but H3 or any mandatory confound control fails | Low-frequency task information is robust across execution and imagery, but motor-compatible localization is unsupported |
| `WO9R-R4` | H1, H2, H3, and every mandatory control pass | Multi-person held-out motor-compatible low-frequency EEG task effect within EEGMMIDB |

Even `WO9R-R4` is not brain-specific proof. It is within-dataset confirmation
by this team under proxy controls, not an unseen-person decoder or independent
replication.

## Resource Caps

### Acquisition stage

| Resource | Limit |
|---|---:|
| Invocation | exactly 1 |
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Metadata body bytes | 2,097,152 |
| EDF payload requests | exactly 72 |
| EDF payload bytes | exactly 184,252,032 |
| Wall time | 900 seconds |
| Peak RSS | 268,435,456 bytes |
| Peak incremental disk | 402,653,184 bytes |
| Minimum free disk before start | 21,474,836,480 bytes |
| Receipt bytes | 1,048,576 |
| Retries / reruns | 0 / 0 |

### Analysis and scoring stages

| Resource | Limit |
|---|---:|
| Registered analysis executions | exactly 1 |
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time through prediction freeze | 1,800 seconds |
| Peak RSS | 1,073,741,824 bytes |
| Private generated bytes | 67,108,864 |
| Public freeze/result bytes | 2,097,152 |
| Parameter-update fits | exactly 144 |
| Target-blind inference runs | exactly 216 |
| Participant-condition prediction sets | exactly 216 |
| Final-target deliveries / scoring events | 1 / 1 |
| Network bytes / new payload bytes | 0 / 0 |
| Retries / reruns / post-target updates | 0 / 0 / 0 |

The existing Git-ignored classical environment may be reused only if its exact
qualified versions are present: NumPy `2.5.2`, SciPy `1.18.0`, MNE `1.12.1`,
scikit-learn `1.9.0`, and pyRiemann `0.12`. Missing or different dependencies
park the run; this contract does not authorize installation or network access.

## Required Evidence Order

1. Commit and push this preregistration, contract, and invariant tests.
2. Require both repository CI jobs green at the exact registration commit.
3. Commit and push an all-false request binding that exact proof.
4. Require both CI jobs green at the exact request commit.
5. Obtain the maintainer's exact Tier C decision in a separate commit.
6. Require both CI jobs green at the exact decision commit.
7. Implement and qualify acquisition, firewall, analysis, freeze, and scorer
   behavior using generated fixtures and mocked transport only.
8. Commit and push that exact implementation and require both CI jobs green.
9. Reverify public metadata and acquire the exact 72-file bundle once.
10. Execute one target-blind analysis and freeze all run-11/run-12 predictions.
11. Commit and push the aggregate hash-only freeze and require both CI jobs
    green.
12. Deliver both final target sets once, score once, apply the frozen router,
    and stop without update or rerun.

No later green commit can retroactively repair an out-of-order real operation.

## Current Access Ledger

This registration used 13 retained public metadata GETs and 340,703 retained
metadata body bytes. All EDF URL requests, EDF body bytes, local PhysioNet path
operations, hashes, parses, headers, annotations, events, samples, targets,
channels, geometry, derivatives, models, fits, inferences, predictions,
scoring events, providers, streams, devices, and hardware operations are zero.

## Explicitly Unavailable

No new participant content has been inspected. Actual selected-file headers,
channel order, geometry, sampling values, annotations, event counts, target
balance, signal quality, finite-sample status, usable-trial count, fit success,
prediction values, accuracy, latency, or memory use are currently unavailable.
The 15-event-per-file count is a fail-closed expectation, not an observation.

## Claim Boundary

Engineering capability added by this preregistration: NeuroDecodeKit now has
an exact, metadata-bound, one-shot protocol for testing its strongest real EEG
lead in twelve untouched people with matched execution/imagery, sealed final
targets, and explicit localization and confound routes.

Scientific claim not established: no selected EDF payload or target was opened
and no model was run, so this contract establishes no cohort confirmation,
brain-specific neural effect, unseen-person generalization, typing, language or
thought decoding, real-time behavior, portable hardware, home use, assistive
benefit, or clinical utility.
