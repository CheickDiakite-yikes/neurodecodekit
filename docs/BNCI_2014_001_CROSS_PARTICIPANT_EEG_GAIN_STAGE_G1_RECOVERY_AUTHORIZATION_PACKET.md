# BNCI-C3C5-1 Stage G1 Recovery Authorization Packet

Date: 2026-08-24

Status: **recovery request prepared; all authority false; decision pending**

Machine request:
`registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_recovery_authorization_request.v0.json`

## Why Recovery Is Needed

The original packet authorized one generated G1 qualification. Its CLI
launcher was invoked after the decision was remotely green, but refused before
the first generated case because the coordinator passed an existing temporary
root to a helper requiring a new child directory.

The failure is frozen as `BNCIC3C5-R1`. It created no fixture file, made no
mock or real network call, fit no model, froze no prediction, delivered no
target, scored nothing, and published no output. Only the two tracked bound
registries were read. The invocation-owned empty root was removed.

The one-line wiring defect is repaired and 12 component tests are green, but
the old one-shot authority is not reused.

## Requested Recovery

After this request and its proof-only closeout are committed, pushed, and both
CI jobs are green, a fresh packet-bound maintainer decision may authorize
exactly one replacement generated/mock G1 pass using the already-frozen
implementation.

The replacement may:

- write only generated MAT fixtures under one invocation-owned temporary root;
- use only mocked transport and generated feature/target rows;
- run nine spawned folds sequentially with one active worker;
- perform exactly 468 synthetic parameter-update fits and 495 synthetic
  prediction sets;
- freeze generated predictions, deliver generated targets once, and apply the
  synthetic scorer once; and
- emit one aggregate result under 4 MiB, then remove only invocation-created
  generated payload and derivative files.

The original caps remain unchanged: one CPU thread, one worker, one numerical
job, 3,600 seconds, 1 GiB peak process-tree RSS, 512 MiB private generated
bytes, 4 MiB public output, zero network bytes, and zero real-data operations.

## Still Forbidden

This recovery does not authorize Stage A, any payload download, any existing
or ignored path, real MAT open or parse, signal/event/artifact/target/label
read, real feature or derivative creation, real model fit or inference,
scientific scoring, retry after the replacement pass, provider or language
model use, hardware, release, or claim upgrade.

If the replacement refuses, G1 remains R1 and the lane parks. If it passes,
its implementation and aggregate result must be committed, pushed, and both
CI jobs green before any later packet is considered.

## Decision Surface

After the remotely green request proof identifies this as the sole active Tier
C packet, the maintainer may use an unambiguous short-form `continue` under the
approved charter rule. A message sent before that identification does not
authorize the recovery.

Engineering capability proposed: one clean, bounded replacement run can prove
that the generated target-firewalled BNCI pipeline works end to end.

Scientific claim not established: this request performs no replacement run
and accesses no real neural data, so it establishes no decoding,
generalization, or EEG-beyond-EOG result.
