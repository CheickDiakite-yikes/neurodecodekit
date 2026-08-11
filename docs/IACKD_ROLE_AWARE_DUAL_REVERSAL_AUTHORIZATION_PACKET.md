# IACKD-2 Role-Aware Dual-Reversal Authorization Packet

Date: 2026-08-10

Status: **Exact packet-bound Tier C decision requested; not granted**

Lane: **IACKD-2 Real EEG Dual Reversal**

Green generated closeout commit:
`7bc45c94f6479564385e3e4d341145343c92b037`

Green generated closeout CI: `31452614232`

Machine request:
`registries/iackd_role_aware_dual_reversal_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission for one prospectively frozen public-EEG experiment
that tests whether pre-movement information follows the participant's actual
hand direction rather than the visual direction implied by a learned mapping.

The future experiment would use OpenNeuro IACKD `ds006840` version `1.0.0`:

- 15 participants, both moving hands, and 30 participant-hand units;
- two disjoint transfer arms, congruent-to-incongruent (`C2I`) and
  incongruent-to-congruent (`I2C`);
- the highest-numbered run sealed for each participant-hand unit and all
  eligible earlier runs reserved for fitting;
- one fixed causal 0.5-4 Hz shrinkage-LDA family;
- direct HEOG/VEOG, occipital, central, timing, pre-window, displacement,
  permutation, derangement, opposite-hand, and all-zero controls;
- exactly 660 parameter-update fits and 900 target-blind prediction sets;
- one remotely green aggregate prediction freeze before either final target
  view opens;
- one combined delivery and score of actual action and the exact opposite cue
  surrogate; and
- one outcome from `IACKD2-R0` through `IACKD2-R5`.

This packet authorizes nothing by itself.

## Why A Fresh Decision Is Required

The approved Research Autonomy Charter permits Tier A research and Tier B
bounded development. Public payload acquisition, EEG and trajectory parsing,
fit-label delivery, model execution, final-target delivery, scoring, and any
scientific claim change remain Tier C.

The maintainer's instruction to do the next three stages allowed preparation
of this request, but it preceded this packet's immutable commit and remote CI
proof. It cannot authorize later content access retroactively.

After this packet is committed, pushed, and both CI jobs are green, Codex may
identify its exact commit, CI run, sole scope, and boundary. If it remains the
only active Tier C packet, a fresh unambiguous `continue`, `approve`, or
`proceed` may bind it by reference. The separate decision artifacts must quote
the maintainer's actual words and bind this request by hash. Codex must not
fabricate a long authorization sentence as a user utterance.

## Immutable Proof

Registration `5bdab3055a8a1c5200b5ec6c0037e401d8c817ce` passed Base
Python job `93648969685` and Optional Neuro Readers job `93648969711` in CI
`31448911258`.

The first implementation push `25a569216db805db068265744b12e84df9fd7b64`
failed CI only because one generated-fixture test hardcoded a macOS temporary
path. No registered closeout followed. Portability correction
`af7488ab1e8f49854733425a96bbdc9c222ef02b` passed Base Python job
`93655939217` and Optional Neuro Readers job `93655939167` in CI
`31451262840`.

Generated closeout `7bc45c94f6479564385e3e4d341145343c92b037` passed Base
Python job `93659819850` and Optional Neuro Readers job `93659819910` in CI
`31452614232`. Before that closeout was recorded, one generated qualification
passed all 15 gates in 5.024801375111565 seconds at 257,130,496-byte peak RSS
with 30,170 output bytes. It exercised the exact 660-fit/900-prediction matrix
and replay, but accessed no real or public IACKD content and has no scientific
value.

## Ordered Authorization

Permission is conditional. A packet-bound `continue` would not immediately
download EEG or open a target.

### Stage 1: authorization-only decision

The maintainer's fresh words are recorded in separate human and machine
artifacts that bind this packet, registration, implementation, generated
result, every artifact hash, access order, and resource cap. That decision-only
commit must be pushed and both CI jobs must pass.

This stage performs no metadata request, dependency operation, local-path
operation, fixture run, payload read, model run, target delivery, or score.

### Stage 2: generated qualification of the real executor

Only after the decision commit is remotely green may Codex implement a
separate real-execution module and qualify it using generated BrainVision,
events, ball, and Leap fixtures plus mocked network responses. It must preserve
the already-hashed generated-only implementation rather than modifying it.

The qualification must cover:

- dry-run-first commands, strict evidence and execution-ordinal checks, and a
  private consumed marker written before the first real request;
- sequential allowlisted transport with path, status, redirect, length, ETag,
  SHA-256, response-encoding, and one-pass guards;
- 29-row and 31-row source-declared channel-role reconciliation;
- one-run-at-a-time BrainVision, events, ball, and Leap parsing;
- causal preprocessing, all registered views, exact dimensions, and the 30 ms
  target-blind kinematic guard;
- isolated fit-label and sealed-final-target construction;
- the exact 660-fit/900-prediction matrix, target firewall, aggregate freeze,
  isolated scorer, router, resource monitors, and bounded receipts; and
- refusal of every registered failure class, retry, rerun, overwrite,
  preexisting-path cleanup, or individual protected public output.

The implementation may use only generated fixtures and mocked transport. It
may reuse the existing Git-ignored numerical environment only if it reports
exactly NumPy `2.5.2`, SciPy `1.18.0`, MNE `1.12.1`, and scikit-learn `1.9.0`.
No installation, dependency resolution, tooling network, public URL request,
or local IACKD path operation is requested.

The exact real-executor implementation must be committed, pushed, and green in
both CI jobs before any public-content operation.

### Stage 3: one fresh streaming acquisition and derivative build

Only after the exact implementation is remotely green may one no-retry
invocation:

1. reverify the registered dataset description, CHANGES, and two object-list
   pages without accepting identity drift;
2. require the same version, DOI, license, 1,679-object listing,
   1,340-object selection, 7,249,113,684 selected bytes, and canonical identity
   hash;
3. create one new isolated invocation root and a private consumed marker;
4. request and verify the 60 registered geometry objects, retaining only the
   bounded role and geometry ledger needed by the reader;
5. process exactly 128 ten-object run groups in canonical order, with only one
   raw group present at a time;
6. issue each of the 1,340 payload requests once, require the registered final
   URL, length, ETag, and SHA-256, and reject redirects, compression, retry,
   substitution, or partial promotion;
7. semantically parse each run once, apply source-declared roles and the fixed
   target-blind quality and motion guards, and promote only complete private
   derivatives;
8. place fit labels and final action/cue views in structurally separate private
   containers, with final targets sealed from predictive code;
9. remove only the invocation-created temporary raw run group after derivative
   promotion; and
10. emit one aggregate public receipt and private manifest, then stop before
    model fitting.

The old retained IACKD bundle is forbidden even if it remains on disk. A full
second raw bundle may never exist. No preexisting file or other project may be
renamed, moved, overwritten, or deleted.

### Stage 4: one target-blind fit, prediction, and freeze

After Stage 3 passes, one no-network execution may:

- verify the private derivative identities without opening sealed final target
  values;
- deliver only arm-specific fit labels and target-free final features to the
  model stage;
- complete exactly 660 registered parameter-update fits and 900 target-blind
  prediction sets;
- compute every registered primary, regional, EOG, timing, null, corruption,
  opposite-hand, and physiology record without selecting from outcomes;
- emit one aggregate hash-only prediction-freeze ledger containing no
  individual prediction, probability, target, trajectory, coefficient, or
  participant outcome; and
- stop with final targets still sealed.

The freeze commit must be pushed and both CI jobs must pass before scoring.

### Stage 5: one combined target delivery and frozen score

Only after the exact freeze is remotely green may the isolated scorer receive
the final target views once:

1. actual hand direction from signed Leap displacement; and
2. the arm-specific cue surrogate derived from visual direction and the frozen
   fit mapping.

The scorer must verify that the two views are exact opposites for every final
row, recompute all prediction and split hashes, score the same frozen
predictions against both views, calculate participant-level exact tests, apply
H0 through H3 and the ordered router, emit one aggregate result, and stop.

No refit, normalization update, threshold change, channel change, exclusion,
seed change, second target delivery, second score, retry, rerun, or post-target
update is permitted.

## Resource Caps

### Generated executor qualification

| Resource | Maximum |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time | 120 seconds |
| Peak RSS | 536,870,912 bytes |
| Generated output | 8,388,608 bytes |
| Real/public/local payload reads | 0 |
| Network bytes | 0 |

### Streaming acquisition and derivative build

| Resource | Maximum |
|---|---:|
| Invocations | 1 |
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time | 7,200 seconds |
| Peak RSS | 2,147,483,648 bytes |
| Metadata bodies | 8,388,608 bytes |
| Payload requests / exact bytes | 1,340 / 7,249,113,684 |
| Largest raw run group | 82,064,564 bytes |
| Peak incremental disk | 1,073,741,824 bytes |
| Minimum free disk | 10,737,418,240 bytes |
| Private derivatives | 536,870,912 bytes |
| Public / private receipts | 4,194,304 / 4,194,304 bytes |
| Retries / reruns | 0 / 0 |

### Fit, freeze, and score

| Resource | Maximum |
|---|---:|
| Registered executions | 1 |
| CPU threads / workers / numerical jobs | 1 / 1 / 1 |
| Wall time through freeze | 10,800 seconds |
| Peak RSS | 2,147,483,648 bytes |
| Private generated output | 536,870,912 bytes |
| Public freeze and result | 4,194,304 bytes |
| Parameter-update fits / prediction sets | 660 / 900 |
| Target deliveries / scores | 1 / 1 |
| Network / new payload bytes | 0 / 0 |
| Retries / reruns / post-target updates | 0 / 0 / 0 |

## Explicitly Not Authorized

- any operation before the separate decision and implementation commits are
  remotely green;
- statting, resolving, hashing, opening, moving, deleting, or otherwise using
  the old retained IACKD bundle;
- any object outside the frozen 1,340-object inventory, published derivative,
  participant demographic, or scan table;
- any other dataset, including S20, S21, S24, S25, SpanishBCBL, PhysioNet,
  raw FIF, or MAT;
- a row-random, cross-participant, cross-hand, or cross-arm fit;
- target-derived quality filtering, exclusion, model selection, normalization,
  adaptation, or early stopping;
- target, signed trajectory, prediction, probability, or participant-outcome
  visibility to predictive code before the green freeze;
- ICA, interpolation, bad-channel deletion, amplitude rejection, zero-phase
  filtering, or an unregistered transform;
- any channel, window, filter, model, threshold, seed, cohort, or
  hyperparameter search;
- a larger or additional model, deep network, CML-v0, pretrained checkpoint,
  foundation model, language model, or provider call;
- dependency installation, version fallback, redirect, retry, resume,
  restart, substitution, or rerun;
- preexisting-path cleanup or any operation on another project;
- individual protected output, upload, publication, release, stream, device,
  or hardware operation; and
- any claim beyond the registered `IACKD2-R5` ceiling.

## Outcome Meaning

- `IACKD2-R1`: the fixed representation is symmetrically cue-bound.
- `IACKD2-R2`: exactly one transfer direction passes, so the symmetric
  hypothesis fails.
- `IACKD2-R3`: both arms favor action, but the registered controls leave the
  source unresolved.
- `IACKD2-R4`: action alignment survives the controls without
  motor-compatible central support.
- `IACKD2-R5`: within-IACKD pre-movement action-direction information survives
  symmetric cue reversals and registered controls, with motor-compatible
  central support.
- `IACKD2-R0`: the fixed design does not establish coherent symmetric
  action-over-cue transfer.

Even `IACKD2-R5` is not proof of brain-specific origin because synchronized
EMG and stronger independent instrumentation are unavailable. It does not
establish external replication, unseen-person generalization, typing,
language or thought decoding, end-to-end real-time operation, portable
hardware, home use, assistive benefit, or clinical utility.

## Current State

Every authorization flag in the machine request is false. Preparing this
packet made zero metadata or payload requests, network transfers, local IACKD
path operations, signal/event/trajectory/target reads, derivative builds,
fits, predictions, freezes, target deliveries, scores, cleanups, retries,
reruns, releases, or scientific claim changes.

Engineering capability requested: one storage-safe, role-aware,
target-firewalled public IACKD dual-reversal can be implemented and, only
after successive remotely green gates, executed once.

Scientific claim not established by this request: an all-false authorization
packet is not EEG data or a result, so it adds no neural effect, action
decoding, brain-specific origin, generalization, real-time, hardware,
assistive, or clinical evidence.
