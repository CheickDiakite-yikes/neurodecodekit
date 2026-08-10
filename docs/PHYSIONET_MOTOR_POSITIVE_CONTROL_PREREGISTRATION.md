# PhysioNet Motor Positive-Control Preregistration

Status: **Frozen prospective Tier C registration; not authorized, implemented,
or executed**

Date: 2026-08-09

Machine contract:
`registries/physionet_motor_positive_control_contract.v0.json`

## Primary Question

On public EEGMMIDB participants S001-S003, can one train-only-selected classical
family recover left-versus-right motor-task information from held-out run 11
while the fixed physiology assay has the expected sensorimotor direction and
all mandatory leakage/confound controls remain below their frozen ceilings?

The primary unit is an annotated `T1` or `T2` task event. The fit unit is a
participant-run group. The result is a three-part conjunction:

1. held-out-run prediction;
2. motor-compatible mu/beta physiology; and
3. confound and leakage controls.

Accuracy by itself cannot pass.

## Immutable Input Boundary

The only eligible payload is the completed work-order-8 bundle:

```text
dataset:          PhysioNet EEGMMIDB 1.0.0
subjects:         S001, S002, S003
runs:             03, 07, 11
files:            exactly 9 EDF files
payload bytes:    exactly 23,248,224
event sidecars:   0
```

The experiment must verify the committed acquisition-result identity and the
private acquisition-manifest hash before any semantic parse. It may perform one
new sequential SHA-256 pass per EDF and one semantic MNE parse per EDF. It may
not request or read `.event` sidecars, another file, another participant, or a
network resource.

## Access Order

### Gate A: authorization and implementation

1. This preregistration, machine contract, and invariant tests are committed,
   pushed, and remotely green.
2. A separate exact Tier C request binds that immutable registration.
3. The maintainer's exact decision is committed, pushed, and remotely green.
4. The parser, target firewall, models, controls, freezer, and scorer are
   implemented and qualified only with generated synthetic fixtures.
5. That exact implementation is committed, pushed, and remotely green.

No local PhysioNet path operation is allowed before all five conditions hold.

### Gate B: one extraction

One isolated extractor may then:

1. verify exact file membership, sizes, hashes, regular-file/no-symlink status,
   and free disk;
2. parse each EDF sequentially with MNE 1.12.x;
3. standardize channel names and bind the standard 10-05 montage;
4. retain all 64 EEG channels and record every channel and geometry field;
5. read only EDF+ annotations `T0`, `T1`, and `T2`;
6. validate 160 Hz sampling, finite samples, monotone event times, and event
   windows that remain within run bounds;
7. map `T1 -> left_fist` and `T2 -> right_fist` only because all files are runs
   03/07/11;
8. write runs 03/07 signals and targets to a fit derivative;
9. write run-11 signals without targets to a prediction derivative; and
10. write run-11 targets to a separate sealed scorer input without printing or
    returning individual target values.

If any observed header, channel, sampling, annotation, trial-count, timing, or
quality invariant differs from the frozen contract, stop at `WO9-V0`. Do not
repair, exclude, reinterpret, or continue conditionally from the same final
set.

### Gate C: train-only family selection

The only selection candidates are:

- `fixed_8_to_30_hz_csp_lda`; and
- `regularized_riemannian_mdm`.

For every participant, each candidate runs both `03 -> 07` and `07 -> 03`.
Selection uses macro participant balanced accuracy across those six directional
check sets. Exact ties select CSP-LDA because it is first in the registered
order. The low-frequency shrinkage-LDA path is a fixed comparator and cannot
select the winner.

All preprocessing, reference, covariance, spatial transform, standardization,
classifier, centroid, and class-prior state is fit on the current fit run only.
There is no row-random cross-validation, pooled evaluation normalization,
target-derived channel selection, evaluation-time adaptation, or silent model
fallback.

### Gate D: target-blind final prediction

The selected family refits once per participant on runs 03+07. It and every
mandatory control then predict run-11 rows without receiving the sealed target
file. The following prediction sets are required:

1. selected full-head primary;
2. low-frequency shrinkage-LDA comparator;
3. train-only no-signal prior;
4. all-zero final signal;
5. pre-cue model;
6. event-index/timing-only model;
7. fixed train-label derangement;
8. fixed one-trial final signal displacement;
9. fixed validation-channel derangement;
10. fixed left/right hemisphere swap;
11. frontal-plus-occipital proxy-channel model; and
12. central sensorimotor-channel model.

The process emits private predictions and a public hash-only freeze ledger. No
individual prediction, probability, target, or participant outcome enters Git.

### Gate E: remote-green prediction freeze

The hash-only prediction ledger must be committed and pushed. Both required CI
jobs must be green at that exact commit. Only then may the isolated scorer open
the same run-11 target file once.

### Gate F: one score

The scorer verifies all prediction and target hashes, computes the registered
aggregate metrics and fixed-seed permutation tests once, applies the ordered
verdict router, emits aggregate target-free receipts, and consumes the final
set. There is no rerun, retry, threshold change, family change, exclusion,
post-result fit, or larger-model escalation.

## Frozen Signal Views

### Primary causal motor-band view

- source sampling: exactly 160 Hz;
- reference: instantaneous common average over all 64 retained EEG channels;
- filter: fourth-order Butterworth bandpass, 8-30 Hz, SOS form;
- application: `scipy.signal.sosfilt` over each continuous run in time order;
- resampling: none;
- event window: `[+1.0, +3.0)` seconds from `T1`/`T2` onset;
- right context relative to decision time: zero;
- decision latency relative to cue: 3.0 seconds;
- ICA, interpolation, channel deletion, clipping, and target-derived rejection:
  forbidden.

This is cue-causal, not pre-movement evidence. Actual movement onset is not
available.

### Pre-cue control

The pre-cue model uses `[-2.0, 0.0)` seconds with the same causal filter and
channel treatment. It is a leakage/schedule control, not a competing model.

### Physiology view

The physiology assay uses fixed C3/C4-centered sensorimotor channels, separate
mu `8-13 Hz` and beta `13-30 Hz` causal views, baseline `[-1.0, 0.0)`, and
active `[+1.0, +3.0)`. It records log-power active-minus-baseline and the
registered contralateral-minus-ipsilateral sign per event and participant.

## Frozen Models

### CSP-LDA

- four CSP components;
- concatenated train covariance;
- covariance regularization `0.1`;
- log average-power transform;
- no trace normalization;
- shrinkage LDA with fixed `0.1` shrinkage; and
- train-only equal class priors.

### Riemannian MDM

- per-event covariance;
- fixed `0.1` trace regularization;
- Riemannian metric;
- train-only class centroids; and
- minimum-distance prediction.

### Low-frequency comparator

The already registered `fixed_low_frequency_shrinkage_lda` family remains a
comparator under its fixed `5C` feature and `0.1` shrinkage contract. It cannot
select or replace the primary family.

No deep network, CML-v0, foundation model, language model, pretrained
checkpoint, fine-tuning, augmentation, or hyperparameter search is allowed.

## Frozen Primary Gate

All conditions are required:

1. exactly the expected three participants, nine runs/files, and 45 held-out
   run-11 task events are scored;
2. pooled primary correct count is at least `30/45`;
3. pooled primary balanced accuracy is at least `0.65`;
4. macro participant balanced accuracy is at least `0.60`;
5. at least two of three participant balanced accuracies exceed `0.50`, and no
   participant is below `0.40`;
6. the fixed-seed within-participant label-permutation p-value is at most
   `0.05`;
7. the primary beats the train-only no-signal prior in pooled and macro
   participant balanced accuracy; and
8. all prediction identities, hashes, ordering, and freeze gates pass.

The exact correct-count requirement is stricter than the one-sided fair-coin
threshold of 29/45 and remains descriptive because trial independence is not
assumed to prove population generalization.

## Frozen Physiology Gate

All conditions are required:

1. at least two of three participants show the registered movement-compatible
   post-cue mu/beta direction;
2. the pooled contralateral-minus-ipsilateral effect has the registered sign;
3. the fixed-seed paired sign-flip p-value is at most `0.05`;
4. no nonfinite, missing-channel, or window-bound violation exists; and
5. physiology is computed independently of model selection and predictions.

## Frozen Confound Gate

All conditions are required:

1. pre-cue, timing-only, train-label-deranged, and one-trial-displaced pooled
   balanced accuracy are each below `0.60`;
2. zero-signal and no-signal controls equal their registered deterministic
   expectations;
3. validation-channel derangement does not meet the primary gate;
4. the central sensorimotor model exceeds the frontal/occipital proxy model by
   at least `0.05` pooled balanced-accuracy points;
5. the frontal/occipital proxy does not meet the primary gate; and
6. the hemisphere-swap response matches the registered directional control or
   the verdict cannot exceed `WO9-V2`.

Failure to detect a proxy confound never proves ocular or muscle artifacts are
absent.

## Verdict Router

Apply in order:

1. any integrity, split, resource, access-order, or freeze failure -> `WO9-V0`;
2. primary gate fails -> `WO9-V1`;
3. physiology or confound gate fails -> `WO9-V2`;
4. all three conjunctions pass -> `WO9-V3`.

The router is deterministic and cannot be amended after any real content is
opened.

## Bounded Execution

```text
registered executions:             1
CPU threads / workers / jobs:       1 / 1 / 1
wall time:                          <= 1,800 seconds
peak RSS:                           <= 805,306,368 bytes
generated private output:           <= 67,108,864 bytes
minimum free disk before:           >= 2,147,483,648 bytes
network bytes:                      0
new payload bytes:                  0
EDF SHA-256 passes:                 9
EDF semantic parses:                9
event-sidecar operations:           0
classical parameter-update fits:    <= 40
prediction sets:                    <= 64
final target deliveries / scores:   1 / 1
retries / reruns:                   0 / 0
```

## Explicitly Not Authorized By Registration

This registration alone authorizes nothing. It does not authorize a local
PhysioNet path stat or open, EDF hash or parse, header/annotation/signal/target
read, dependency install or import, derivative, split, fit, inference, freeze,
score, additional download, another dataset, S20, S21, S24, S25, raw FIF/MAT,
language model, provider, RW3, stream, device, hardware, publication, release,
or claim upgrade.

A separate exact Tier C decision remains mandatory after this registration is
committed, pushed, and remotely green.

Engineering capability if a future execution passes every gate: NeuroDecodeKit
can run one leakage-resistant, resource-bounded, held-out-run public EEG motor
positive control with a remotely green prediction freeze and physiology plus
confound triangulation.

Scientific claim not established even by `WO9-V3`: the maximum result is a
three-person motor-task EEG pilot. It cannot establish brain-specific origin,
unseen-person generalization, typing or language decoding, thought reading,
real-time performance, portable hardware, home use, assistive benefit, or
clinical utility.
