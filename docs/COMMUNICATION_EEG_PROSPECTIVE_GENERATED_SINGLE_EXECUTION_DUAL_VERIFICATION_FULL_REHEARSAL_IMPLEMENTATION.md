# COMM-P0-G FS3 Full Rehearsal Wrapper Implementation

Date: 2026-08-28

Gate: `COMM-P0-G-FS3-v0`

Status: generated/mock-only wrapper implementation pending exact commit, push,
both remote CI jobs, a separate execution-proof artifact, and a final
proof-digest activation commit

## Added interface

The additive wrapper supplies the missing one-shot control plane around the
already-green FS3 producer and model-free verifier. It does not modify the six
artifacts bound by the prior implementation proof.

The wrapper:

- validates a separate future exact-green implementation proof without Git or
  network access and remains fail-closed until a later activation commit binds
  that proof's exact digest;
- refuses before consumption when output paths, proof identity, or the 20 GiB
  post-reservation storage floor are invalid;
- creates a distinct durable no-replace FS3 receipt before any full producer;
- reserves the frozen 537,919,488-byte disk envelope before child work;
- runs one frozen 21-person-per-cohort producer and then one independent
  zero-model verifier under one absolute 180-second deadline;
- continuously inherits the existing process-tree RSS monitor, adds parent-
  phase RSS checkpoints, and preserves one-thread child environments;
- opens all eight producer surfaces by basename relative to one no-follow
  directory descriptor and rejects symlinks, hardlinks, and inode drift;
- gives the verifier preopened descriptors, no repository paths, an isolated
  working directory, and an active socket guard;
- independently verifies the exact FS3 contract, Amendment 1, wrapper proof,
  frozen verifier, score worker, score-only module, and streaming scorer;
- validates exactly two sequential stream traversals, 91,392 rows, 1,428 sets,
  and the observed 64 rows inside every participant-condition-endpoint set,
  plus one physical target transport with two disjoint logical
  cohort partitions, two deliveries, two scores, zero model operations, PID
  isolation, and aggregate score equality;
- cleans only its invocation-owned temporary tree; and
- fsyncs a bounded target-free staged result, records a stable decisecond
  runtime and all mandatory parent RSS samples, atomically promotes it without
  replacing an existing output, and removes invocation-owned publication if a
  final deadline or resource check crosses.

The separate sidecar CLI exposes `plan`, `run`, and `inspect`. `run` is
fail-closed while the future wrapper proof is not digest-bound by activation.

## Generated/mock qualification only

The focused tests inject small generated producer/verifier records. They cover
strict future-proof validation, rejection of wrapped real callbacks, exact
identity binding, rejection of reduced, invalid, and unequal-per-set inventory,
symlink and hardlink refusal, an actual isolated socket-guarded code capsule, a
target-free pass, post-receipt verifier park, pre-receipt path and storage
refusals, post-receipt reservation consumption, one shared deadline, final RSS
and deadline cleanup, absence of official capabilities, CLI fail-closed
behavior, and implementation-record identity.

No reduced or full numerical producer was rerun. No receipt was created outside
pytest temporary directories. Full FS3 attempts remain zero.

## Ordered next barrier

This implementation must be committed, pushed, pass Base Python and Optional
Neuro Readers, and reach GitHub `main`. A separate immutable proof must then
bind the exact green commit, both job IDs, and the implementation artifacts.
Only after that proof is itself remotely green and a final separately green
activation commit binds its exact digest may the single registered
`COMM-P0-G-FS3-R0` attempt be considered. A post-receipt failure consumes it.

Engineering capability added: FS3 now has a fail-closed, resource-bounded,
one-shot producer-plus-independent-verifier control plane that can be qualified
without executing its full numerical schedule.

Scientific claim not established: this generated/mock implementation accessed
no EEG, human target, device, or provider and establishes no communication
decoding, EEG-beyond-peripheral advantage, unseen-person generalization,
independent replication, causal live operation, hardware result, or clinical
value.
