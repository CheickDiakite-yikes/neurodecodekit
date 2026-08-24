# EEGMMIDB-UG1 Unseen-Participant Generalization Preregistration

Date: 2026-08-24

Status: **Frozen locally; all real-operation authority remains false**

Contract:

- `registries/eegmmidb_unseen_participant_generalization_contract.v0.json`

## Primary Hypothesis

A single source-pooled low-frequency model fitted only on S001-S015 runs 03/07
will predict left versus right execution in S016-S030 run 11 with zero
held-out-person calibration, and will beat the stronger of no-signal and
timing-only controls at the participant level.

Imagery transfer from S001-S015 runs 04/08 to S016-S030 run 12 is a
prespecified upgrade. It cannot rescue failed execution.

## Immutable Identities

Dataset: PhysioNet EEG Motor Movement/Imagery Dataset `1.0.0`, DOI
`10.13026/C28G6P`.

Source participants are exactly S001-S015. Fresh participants are exactly
S016-S030. Source run-11/run-12 rows and all other participants are forbidden.
Only EDF+ annotations T1 and T2 define left/right targets; `.event` sidecars
are forbidden.

Thirty-six not-yet-frozen remote files are named by rule:

- S001-S003 runs 04 and 08: six source-fit EDFs; and
- S016-S030 runs 11 and 12: thirty fresh-final EDFs.

A metadata stage must observe exactly those 36 paths, successful identity
responses, and a combined size at or below 268,435,456 bytes. It may not open
an EDF body. The exact path/size/validator inventory must be committed, pushed,
and remotely green before any payload request.

## Ordered Stages

### G: generated qualification

Implement and qualify, using generated EDF fixtures and mocked transport only:

- exact path and cohort validators;
- sequential bounded acquisition;
- source/fresh payload isolation;
- EDF reader and target firewall;
- causal preprocessing and fixed model family;
- LOSO source gate;
- all frozen controls;
- model/checkpoint freezer;
- fresh target-blind predictor;
- hash-only prediction freezer;
- isolated participant-level scorer; and
- resource, overwrite, and no-retry guards.

The exact implementation must be committed, pushed, and remotely green.

### M: metadata identity

Make at most 36 sequential metadata requests for only the named EDFs. Record
path, exact byte size, stable validator fields if available, and immutable
version/DOI identity. Transfer at most 2 MiB and write at most 1 MiB. Open zero
EDF bodies. Commit and remotely green the exact inventory.

### S: source-only qualification and checkpoint freeze

Acquire only the six missing S001-S003 source-fit EDFs. Reuse only the exact
54 already acquired S001-S015 source-fit EDFs under a fresh decision. Never
open source run 11/12.

Extract exactly T1/T2 rows from runs 03/07 for execution and 04/08 for imagery.
Run the 15-fold source LOSO gate. If execution fails, emit R1 and stop before
fresh acquisition. If it passes, refit the two exact models on all eligible
source rows and freeze model coefficients, scaler values, channel order,
preprocessing, source split, controls, configuration, and code hashes. Commit,
push, and require both CI jobs green.

### F: fresh target-blind prediction freeze

Only after Stage S is remotely green, acquire the 30 S016-S030 run-11/run-12
EDFs. A target-isolation process may parse annotations and create timing-only
target-free rows plus one sealed 450-target scorer input. Predictive code gets
signal, cue timing, task family, and fixed model artifacts. It gets no T1/T2
identity, participant calibration statistic, target-derived exclusion, or
selection signal.

Produce every primary and control prediction with no adaptation. Freeze only
aggregate hashes and completeness counts publicly; publish no individual
prediction, probability, target, or participant outcome. Commit and remotely
green the prediction freeze.

### T: one target delivery and score

Deliver the same sealed 450 targets once. Score execution first, then imagery,
using the frozen participant-level tests and router. Emit aggregate metrics
only. No post-target update or rerun is allowed.

## Fixed Representation

The model is exactly the one described in the research record: 64-channel
instantaneous common-average reference, causal fourth-order 0.5-4 Hz SOS
filter on continuous runs, `[+1,+3)` window, four 500 ms means plus one slope
per channel, source-fitted standardization, and pooled shrinkage LDA with
`lsqr`, shrinkage `0.1`, equal priors.

Separate execution and imagery models are frozen. There is one candidate and
no selection.

## Primary Controls And Statistics

All eleven conditions in the contract freeze together. Participant-macro
balanced accuracy is primary. Pooled accuracy is descriptive. Exact sign-flip
tests enumerate participant-level sign assignments; trial-level p-values are
forbidden.

Execution passes only when every frozen fresh gate passes. Imagery upgrades R3
to R4 only if execution already passed and every imagery gate passes.

## Router

- `EEGMMIDBUG1-R0`: integrity, identity, payload, firewall, freeze, or resource
  refusal.
- `EEGMMIDBUG1-R1`: source LOSO execution gate failed; fresh acquisition zero.
- `EEGMMIDBUG1-R2`: fresh execution failed one or more primary/control gates.
- `EEGMMIDBUG1-R3`: execution passed strict zero-calibration unseen-person
  protocol-condition generalization.
- `EEGMMIDBUG1-R4`: execution and imagery both passed.

Every route consumes its reached stage. R2-R4 consume the final target event.
There is no retry, rerun, alternative seed, additional model, threshold
change, participant exclusion, or post-target amendment.

## Claims

The highest possible claim is participant-independent left/right EEGMMIDB
protocol-condition prediction across 15 unseen participants with zero
calibration. Cue and ocular compatibility remain explicit because EEGMMIDB has
no recorded EOG comparator and the prior early/frontal controls were strong.

This preregistration authorizes nothing. It establishes no unseen-person
result, motor-intention decoding, motor-cortex origin, eye-independent neural
signal, language or thought decoding, live operation, or hardware result.
