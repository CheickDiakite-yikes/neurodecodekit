# IACKD-2R Transport-Stable Dual-Reversal Recovery Authorization Packet

Date: 2026-08-11

Status: **Exact packet-bound Tier C decision requested; not granted**

Lane: **IACKD-2R Transport-Stable Dual-Reversal Recovery**

Green transport registration:
`ee0f62adf74afd390052694142090ccc0395c539`

Green generated transport implementation:
`93a067c4dcdb89ea5e5d17db6e5adaca454a64d1`

Green implementation CI: `31474412246` (Base Python `93724709807`;
Optional Neuro Readers `93724709840`)

Machine request:
`registries/iackd_transport_stable_recovery_authorization_request.v0.json`

## Decision In Plain Language

This packet asks permission to build and qualify one additive real executor,
then make one fresh, no-retry attempt at the scientific experiment that
IACKD-2 never reached. The only protocol correction is transport-level: the
four small metadata bodies may be fixed-length, chunked, or cleanly close-
delimited, but their observed bytes and registered SHA-256 must still match
exactly before parsing.

The 1,340 selected payload objects remain strict fixed-length responses with
exact registered ETags, exact observed byte counts, and one full-stream
SHA-256 pass. Every participant, hand, arm, channel role, causal window,
control, model, target-firewall, freeze, scorer, and router field remains
identical to the frozen IACKD-2 scientific design.

The consumed IACKD-2 invocation is not reopened or rerun. IACKD-2R would use a
new module, new invocation identity, new private consumed marker, and new
Git-ignored root. The old invocation root, old retained bundle, and consumed
executor remain forbidden.

This packet authorizes nothing by itself.

## Why A Fresh Decision Is Required

The Research Autonomy Charter permits the completed generated-only transport
work. Integrating a public-data executor, requesting any `ds006840` body,
reading EEG or target content, fitting a model, freezing predictions, and
opening final targets are Tier C actions.

The maintainer's current `continue` arrived before this immutable packet and
cannot authorize it retroactively. After this packet is committed, pushed,
and both CI jobs are green, Codex may identify its exact commit, CI run, sole
scope, and decision boundary. If it remains the only active Tier C packet, a
fresh unambiguous `continue`, `approve`, or `proceed` may bind it by reference.
A separate decision artifact must quote the maintainer's actual words and bind
this request by hash. Codex must not fabricate a long authorization sentence
as a user utterance.

## Immutable Proof

Transport registration
`ee0f62adf74afd390052694142090ccc0395c539` passed Base Python job
`93717995481` and Optional Neuro Readers job `93717995427` in CI
`31472269070`.

Exact generated transport implementation
`93a067c4dcdb89ea5e5d17db6e5adaca454a64d1` passed Base Python job
`93724709807` and Optional Neuro Readers job `93724709840` in CI
`31474412246`. Its implementation registry SHA-256 is
`f9c1f87e846b4b8e2394c47a0d996e31833398241eca1ff4686ddc39ad10e318`.

The implementation passed 41 focused tests and both complete remote suites.
Its one measured fresh-process generated qualification accepted ten responses
across two deterministic replays, refused all 22 registered mutations, ran in
0.001049624988809228 seconds at 20,332,544-byte peak RSS, emitted 5,540
bytes, and made zero network, public-data, local-IACKD, model, target, or score
operations.

Two earlier implementation candidates remain preserved as failed CI evidence.
`6b89b7d` and `8d7be6a` each passed Base Python but failed the optional suite
because the CLI resource test inherited the dependency-loaded suite's RSS
history. Neither candidate is accepted as green implementation proof.

The consumed parent executor
`dab5dd47ee47f285430311e4fe0f38f457d1118a` passed both jobs in CI
`31461818620`. Its sole invocation opened one metadata response and failed
closed before body read at `IACKD2-F08`. Result
`36aeccb76c7e277b9dd69792e9bfcffb018f1188` passed both jobs in CI
`31467335648`. It produced no scientific observation and has no retry.

## Requested Ordered Sequence

Only after a separate decision commit is pushed and both CI jobs pass may the
following sequence begin:

1. Implement a new additive IACKD-2R executor using only generated fixtures
   and mocked transport. It must integrate the green transport validator,
   preserve the parent science contract, refuse every old root, and expose no
   public operation before proof validation.
2. Commit and push that exact executor, then require Base Python and Optional
   Neuro Readers CI to pass. A failed implementation remains ineligible; no
   public request may follow it.
3. Run one pre-consumption safety check. Refuse before writing the consumed
   marker unless at least 10 GiB is free, all numerical thread settings equal
   one, and one-minute system load does not exceed one runnable process per
   logical CPU.
4. Create one new isolated Git-ignored invocation root and consumed marker,
   then perform one canonical four-body metadata reverification using the
   transport-stable framing contract.
5. Stream exactly 1,340 registered objects totaling 7,249,113,684 bytes in
   canonical order. Keep at most one raw run group at a time, verify each
   object, create the registered isolated derivatives, and remove only that
   invocation-created temporary raw group after promotion.
6. Validate complete target-free model derivatives, sealed scorer targets,
   physiology derivatives, source roles, geometry availability, target
   firewall, and all resource/output counters.
7. Execute exactly 660 fixed parameter-update fits and 900 target-blind
   prediction sets. Final target values and signed trajectories remain
   physically unavailable to predictive code.
8. Emit one aggregate hash-only prediction freeze containing no individual
   prediction, probability, target, trajectory, or participant outcome.
9. Commit and push the freeze, then require both remote CI jobs to pass.
10. Deliver the two sealed final target views together exactly once, score the
    same frozen predictions once, apply `IACKD2-R0` through `IACKD2-R5`, emit
    one aggregate result, and stop.

There is no retry, resume, restart, substitution, second target delivery,
second score, post-target update, or post-result tuning. Any failure after the
new consumed marker is written consumes IACKD-2R.

## Transport Boundary

For the four small metadata bodies only:

- accepted framing is exact fixed length, valid chunked transfer, or clean
  connection close;
- one read is bounded to registered bytes plus one;
- exact observed bytes and registered SHA-256 are mandatory;
- `Content-Length`, when valid and present, is recorded as exact or different
  advisory evidence;
- ambiguous length plus transfer coding, malformed or over-cap length,
  compression, redirect, status/URL drift, underflow, overflow, read error, or
  hash drift refuses; and
- raw bodies are not persisted and are discarded before the next request.

For all 1,340 selected payload objects, exact `Content-Length`, exact ETag,
exact observed bytes, identity encoding, and one full-stream SHA-256 remain
mandatory. The metadata repair cannot weaken payload integrity.

## Scientific Boundary

The frozen design remains a 15-participant, 30 participant-hand-unit,
two-direction reversal:

- `C2I`: fit red congruent, test yellow incongruent;
- `I2C`: fit yellow incongruent, test red congruent;
- 26 source-declared EEG predictors, with M1/M2 optional and HEOG, VEOG, and
  Trigger excluded from predictors;
- 1024 Hz source sampling and a causal `[-1.0, 0.0]` second pre-action window;
- fixed 0.5-4 Hz role-aware shrinkage LDA, no candidate search, and no
  hyperparameter search;
- recorded-EOG, visual timing, corruption, displacement, central-support, and
  action-versus-cue controls inherited unchanged; and
- the weaker participant-level action-over-cue margin remains primary, with
  both reversal arms required.

The maximum possible route is `IACKD2-R5`. Even that route would not prove
absolute brain-specific origin, independent replication, unseen-person
generalization, typing, language or thought decoding, real-time operation,
portable hardware, home use, assistive benefit, or clinical utility.

## Resource Caps

| Stage | Wall time | Peak RSS | Network/body bytes | Incremental/private output |
|---|---:|---:|---:|---:|
| Generated executor qualification | 120 s | 536,870,912 | 0 | 8,388,608 |
| Fresh stream and derivatives | 7,200 s | 2,147,483,648 | 7,257,502,292 | 1,073,741,824 peak disk |
| Fit, freeze, and score | 10,800 s | 2,147,483,648 | 0 | 536,870,912 private |

Every stage uses one CPU thread, one worker, and one numerical job. The stream
requires at least 10,737,418,240 free bytes before consumption, keeps at most
one 82,064,564-byte raw run group, and may emit at most 4,194,304 public bytes.
Retries and reruns are zero. End-to-end latency is not measured.

## Explicitly Not Authorized

- any action before a separate packet-bound decision is remotely green;
- any public request before the exact additive executor is remotely green;
- statting, resolving, hashing, opening, moving, deleting, or reusing the old
  invocation root, old retained bundle, private consumed marker, or another
  project;
- modifying or rerunning the consumed IACKD-2 executor;
- any object outside the exact 1,340-object inventory or four registered
  metadata bodies;
- another dataset, participant, hand, run, file, URL, metadata refresh,
  redirect, retry, resume, restart, substitution, or rerun;
- row-random, cross-participant, cross-hand, or cross-arm fitting;
- target-derived filtering, exclusion, selection, normalization, adaptation,
  or evaluation-time fitting;
- final target, signed trajectory, prediction, probability, or participant
  outcome visibility before the remotely green aggregate freeze;
- ICA, interpolation, bad-channel deletion, amplitude rejection, zero-phase
  filtering, or any filter/window/channel/model/threshold/seed/cohort search;
- a larger, additional, deep, CML, pretrained, foundation, or language model;
- dependency installation, tooling network, provider, RW3, stream, device,
  hardware, upload, publication, or release operation;
- individual protected output or a second target delivery or score; and
- any scientific claim beyond the registered IACKD-2 ceiling or any claim of
  brain-specific origin, typing, thought decoding, real-time operation,
  hardware capability, assistive benefit, home use, or clinical use.

## Current State

Every implementation, public-data, local-data, model, target, scoring, and
claim authorization flag in the machine request is false. Preparing this
packet made zero network requests, public or local body reads, signal/event/
trajectory/target reads, model fits, predictions, freezes, scores, retries,
reruns, releases, or claim changes.

Engineering capability requested: one new storage-safe, transport-stable,
target-firewalled executor can attempt the already frozen dual-reversal EEG
experiment without mistaking an optional HTTP framing header for content
identity.

Scientific claim not established by this request: this all-false packet is
not EEG data or a result and establishes no neural effect, action decoding,
brain-specific origin, generalization, real-time operation, hardware
capability, assistive benefit, home use, or clinical use.
