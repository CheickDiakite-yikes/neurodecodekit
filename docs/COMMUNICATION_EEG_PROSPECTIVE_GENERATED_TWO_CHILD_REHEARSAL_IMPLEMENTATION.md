# COMM-P0-G Two-Child Rehearsal Implementation

Recorded: 2026-08-28

Status: additive generated/mock-qualified implementation pending exact commit,
push, remote CI, GitHub `main`, and a separate fixed implementation proof.

Gate: `COMM-P0-G-FS2-v0`

## Added capability

The additive wrapper and CLI implement the control plane for the single future
generated-only full-scale rehearsal without changing the remotely proven
COMM-P0 coordinator.

The wrapper:

- loads and hashes the exact frozen FS2 contract and all four parent records;
- refuses until a future fixed implementation-proof record validates the exact
  five-file implementation allowlist and remote-green evidence;
- requires output and receipt in one no-follow destination directory and
  refuses existing files or links;
- checks the 20.501 GiB pre-reservation free-space threshold;
- writes and fsyncs a separate no-replace FS2 receipt before creating a
  temporary root, reservation, key, nonce, or child;
- physically reserves the complete 537,919,488-byte aggregate disk envelope,
  then releases only the registered per-replay and public-result allowances as
  each stage needs them;
- runs two replay workers sequentially with shared keys, nonce, contract, and
  absolute 180-second deadline;
- validates the exact 21-person-per-cohort schedule, 91,392 rows, 1,428 sets,
  seven shortcut routes, 70 refusal observations, two cohort deliveries and
  scores, 14 shortcut deliveries and scores, and zero post-target updates per
  replay;
- enforces distinct child process IDs, canonical replay equivalence, bounded
  prediction buffering, parent-plus-child RSS, monitor, input, output, and
  temporary-disk caps;
- injects a socket guard into replay, model, and scorer children and makes any
  provider or network attempt fail closed;
- captures descendant process IDs and process groups, terminates the captured
  tree on timeout or cap failure, and refuses surviving descendants;
- removes each private fictional replay tree through descriptor-relative,
  no-follow cleanup that refuses links, hard links, and unknown inode types;
  and
- atomically publishes one exact-key, target-free aggregate `FS2_PASS` or
  `FS2_PARK` result without replacement.

The FS2 receipt uses a new schema. The existing official activation validator
rejects it, and the wrapper exposes no operation that reads, creates, replaces,
renames, or deletes an official consumed marker.

## Qualification performed now

Fifteen focused tests use only generated dictionaries, mocked child
executors, one socket-blocking subprocess, a tiny mock reservation, and
temporary directories. They verify:

- exact parent and future-proof bindings;
- proof absence before any receipt or output;
- two distinct mock children and aggregate pass routing;
- canonical mismatch and resource-cap park routing;
- consumed receipt and no-rerun behavior;
- official activation rejection of the FS2 receipt;
- symlink and existing-output refusal without mutation;
- free-space refusal before child work;
- durable receipt creation before reservation and consumed routing after a
  reservation failure;
- one shared absolute deadline across both child calls;
- structural non-use of the official activation, marker, and qualification
  functions;
- network refusal inside a guarded child;
- descriptor-relative cleanup refusal for symlink and hard-link escape inodes;
- exact-key target-free aggregate inspection; and
- CLI help, plan, and closed run behavior.

Implementation qualification runs zero full-scale replay, model fit, target
delivery, score, network request, real/private read, human or device operation,
official invocation, and scientific-claim operation.

## Delayed execution barrier

The CLI `run` command currently refuses because
`registries/communication_eeg_prospective_generated_two_child_rehearsal_implementation_proof.v0.json`
does not exist. After this exact implementation passes both CI jobs on GitHub
`main`, a separate proof-only record must bind its five exact artifacts and
explicitly preserve every official, real/private, network, device, release, and
claim flag as false. Only that remotely green proof can expose the single
registered Tier B attempt.

Failure, timeout, or refusal after receipt creation consumes
`COMM-P0-G-FS2-R0`. No retry, rerun, resume, or substitution is permitted.

## Boundary

Engineering capability added: NeuroDecodeKit now has a fail-closed wrapper for
measuring whether two complete fictional coordinator replays fit the frozen
resource envelope without spending the official qualification.

Scientific claim not established: no full-scale rehearsal or real EEG was run,
so this establishes no communication decoding, EEG-beyond-peripheral
information, unseen-person generalization, independent replication, causal
live decoding, hardware performance, or clinical value.
