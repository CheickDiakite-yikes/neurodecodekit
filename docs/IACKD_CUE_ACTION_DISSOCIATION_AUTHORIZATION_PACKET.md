# IACKD Cue-to-Action Reversal Authorization Packet

Date: 2026-08-10

Status: **Exact packet-bound Tier C decision requested; not granted**

Registration commit:
`e42b79961d1fafe5cf406beaf868388ecbcbfb09`

Green registration CI:
`31400450392`

Machine request:
`registries/iackd_cue_action_dissociation_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission to build and run one carefully bounded public-EEG
experiment that can tell whether NeuroDecodeKit's strongest low-frequency lead
follows the intended hand action or merely follows the visual cue.

The future experiment would use OpenNeuro IACKD `ds006840` version `1.0.0`:

- 15 participants and 30 participant-hand model units;
- congruent earlier runs for fitting;
- one held-out incongruent run per participant and hand;
- the same frozen predictions scored against actual hand direction and the
  opposite visual target direction;
- direct HEOG/VEOG and Leap Motion controls;
- one fixed 0.5-4 Hz shrinkage-LDA family;
- no larger model, model search, LLM, or post-target tuning; and
- one outcome from `IACKD-R0` through `IACKD-R4`.

This packet authorizes nothing by itself.

## Why A New Decision Is Required

The approved Research Autonomy Charter permits Tier A research and Tier B
bounded development, but real payload acquisition, content parsing, target
delivery, scoring, and scientific claim changes remain Tier C.

The user's prior 10 GB data allowance is a resource ceiling, not a dataset or
experiment decision. Earlier `continue`, `approve`, or general autonomy
messages occurred before this immutable packet existed and cannot be applied
retroactively.

After this packet is committed, pushed, and remotely green, the assistant may
identify its exact commit, CI run, and scope. If this is still the sole active
Tier C packet, a new unambiguous `continue`, `approve`, or `proceed` may bind
this packet by reference. The separate decision artifact must quote the user's
actual words. It must not fabricate the long scope as a user utterance.

## Immutable Registration Proof

Registration `e42b79961d1fafe5cf406beaf868388ecbcbfb09` freezes:

- the 1,340-object, 7,249,113,684-byte raw-source inventory;
- OpenNeuro `ds006840` version `1.0.0`, DOI, CC0 license, paths, sizes, ETags,
  and modification times;
- exclusion of MATLAB derivatives, demographics, and subject scan tables;
- 15 participants, both moving hands, and 30 participant-hand units;
- earlier congruent fit runs and one final incongruent run per unit;
- the target-blind 30 ms Leap Motion guard;
- 32 EEG channels, HEOG/VEOG controls, and no ICA or zero-phase filtering;
- the fixed causal 0.5-4 Hz feature and shrinkage-LDA recipe;
- 300 maximum fit operations and exactly 420 prediction sets;
- one combined target delivery and one aggregate score after a green freeze;
- `IACKD-R1` cue-bound routing before generic null routing; and
- one-thread CPU, 2 GiB RSS, 10 GiB network, 9 GiB incremental disk, 512 MiB
  private derivative, no-retry, and no-rerun caps.

CI `31400450392` passed Base Python job `93493810963` and Optional Neuro
Readers job `93493811025` at that exact commit. Local registration verification
passed 1,638 tests with eight expected skips, Ruff 0.15.20, compileall, 117
registry JSON files, and `git diff --check`.

## Ordered Authorization

Permission is conditional. A packet-bound `continue` would not start an
immediate download.

### Stage 1: authorization-only record

The user's actual short-form or long-form decision is recorded in separate
human and machine artifacts that bind this packet, registration commit, every
scope hash, CI run, and resource cap. That decision-only commit must be pushed
and both CI jobs must pass.

This stage performs no metadata request, dependency operation, fixture run,
payload stat, content read, model run, or score.

### Stage 2: generated-fixture implementation

Only after the decision commit is remotely green may Codex implement and test:

- a dry-run-first 1,340-object allowlisted downloader using mocked transport;
- strict no-follow paths, atomic promotion, one-shot markers, and receipts;
- sequential BrainVision, event, ball, and Leap readers;
- exact channel, sampling, marker, stream, and geometry validation;
- the target-blind kinematic onset guard;
- signed-displacement target creation inside an isolated firewall;
- causal 0.5-4 Hz features, central and EOG views, and EOG projection;
- all 300 fit and 420 prediction-set interfaces;
- the target-free freeze and isolated aggregate scorer;
- resource monitors, deterministic refusal mutations, and CLI commands; and
- generated fixtures with no IACKD or other real data.

The implementation may not stat or open a local IACKD path or request a real
object URL. It may reuse the existing Git-ignored classical environment only
if it reports exactly NumPy 2.5.2, SciPy 1.18.0, MNE 1.12.1, and scikit-learn
1.9.0. Missing or changed versions park the sequence. No package installation,
dependency resolution, or tooling network is requested.

The exact implementation must be committed, pushed, and green in both CI jobs
before acquisition.

### Stage 3: one metadata recheck and acquisition

Only after green implementation may one no-retry invocation:

1. re-read the registered dataset description, CHANGES, and two-page object
   listing;
2. require the same version, DOI, license, 1,679 listed objects, and canonical
   selected inventory hash;
3. request only the 1,340 selected object bodies, in sorted order, once each;
4. transfer exactly 7,249,113,684 payload bytes;
5. verify response path, length, and ETag and compute SHA-256 while streaming;
6. write only to a new isolated temporary root;
7. promote only a complete exact bundle; and
8. write one private manifest and aggregate receipt.

The acquisition is capped at one thread, one worker, 7,200 seconds, 512 MiB
RSS, 8 MiB metadata bodies, 10 GiB network payload, 9 GiB incremental disk,
at least 20 GiB free disk, 4 MiB private receipts, and zero retry or rerun.

Acquisition parses no header, marker, event, sample, channel, trajectory,
target, or label and imports no MNE.

### Stage 4: one target-blind analysis and freeze

After acquisition succeeds and no earlier gate fails, one no-network analysis
may:

- no-follow verify and rehash all 1,340 objects;
- parse each of 128 BrainVision runs sequentially;
- read all 32 EEG channels, M1/M2, HEOG/VEOG, 1,024 Hz samples, available
  geometry, registered markers, ball streams, and Leap streams;
- apply only target-blind validity and 30 ms motion-guard checks;
- create congruent labeled fit rows, target-free final EEG rows, and one
  isolated sealed dual-target input;
- complete at most 300 parameter-update fits and all 420 target-blind
  participant-condition prediction sets;
- freeze nonselecting readiness-potential, mu/beta, EOG, timing, corruption,
  and resource records; and
- emit one public aggregate hash ledger with no individual output.

Predictive code receives no final action direction, visual direction, signed
trajectory, ball position, target, probability, or participant outcome.

The analysis is capped at one thread, one worker, 3,600 seconds through
freeze, 2 GiB RSS, 512 MiB private generated output, 2 MiB public freeze and
result output, zero network, zero new payload, zero retry, and zero rerun.

The hash-only freeze must be committed, pushed, and green in both CI jobs
before either target view opens.

### Stage 5: one combined target delivery and score

Only after the exact freeze is remotely green may the isolated scorer receive
both final views together once:

1. actual hand direction from signed Leap displacement; and
2. visual target direction from signed ball displacement.

It verifies that each final pair is opposite, scores the same frozen
predictions against both, computes participant-level exact tests, applies H1
through H4 and the ordered router, emits aggregate output, and stops.

No refit, normalization update, threshold change, channel change, exclusion,
seed change, second delivery, second score, retry, rerun, or post-target update
is permitted.

## What Is Not Authorized

The packet excludes:

- every object outside the 1,340-object inventory;
- OpenNeuro derivatives, demographics, or scan tables;
- S20, S21, S24, S25, SpanishBCBL, PhysioNet, raw FIF, or MAT access;
- redirects, retries, resumes, restarts, substitutions, or partial promotion;
- package installation or dependency fallback;
- row-random, cross-participant, or cross-hand fitting;
- final-target use for quality, selection, normalization, or adaptation;
- ICA, interpolation, bad-channel deletion, amplitude rejection, or
  zero-phase filtering;
- any filter, window, channel, threshold, seed, cohort, or model search;
- a larger model, deep network, CML-v0, checkpoint, foundation model, LLM, or
  provider call;
- RW3, stream, device, hardware, release, or publication operation;
- public individual targets, predictions, probabilities, trajectories,
  traces, or participant outcomes; and
- any claim beyond the registered `IACKD-R4` ceiling.

## Outcome Meaning

- `IACKD-R1`: the representation follows the visual target under reversal and
  is localized as cue-bound.
- `IACKD-R0`: it does not generalize cleanly and is not reliably cue-bound.
- `IACKD-R2`: it follows action, but recorded peripheral or integrity controls
  leave source unresolved.
- `IACKD-R3`: action alignment survives EOG, timing, and integrity controls,
  but motor-compatible central support is incomplete.
- `IACKD-R4`: action alignment, recorded controls, central support, and
  integrity all pass within IACKD.

Even `IACKD-R4` would establish only a within-dataset, pre-movement,
motor-compatible EEG action-direction effect under synchronized EOG and
kinematic controls. It would not establish absolute brain-specific origin,
independent replication, unseen-person generalization, typing, language or
thought decoding, real-time operation, portable hardware, home use, assistive
benefit, or clinical utility.

## Current State

Every authorization flag in the machine request is false. No new metadata
request was made while preparing this packet. IACKD payload requests, bytes,
local path operations, content reads, dependencies, derivatives, fits,
predictions, freezes, target deliveries, scores, retries, and reruns remain
zero.

Engineering capability requested: one exact cue-to-action reversal pipeline
with synchronized EOG and kinematic controls can be implemented and, only
after successive green gates, executed once.

Scientific claim not established by this request: an authorization packet is
not data or a result, so it adds no EEG effect, action decoding, source
localization, generalization, real-time, hardware, assistive, or clinical
evidence.
