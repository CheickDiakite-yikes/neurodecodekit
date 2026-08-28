# COMM-P0-G FS3 Amendment 1: Strict Verifier Semantics

Date: 2026-08-28

Amendment: `COMM-P0-G-FS3-A1`

Parent: `COMM-P0-G-FS3-v0`

Status: prospective generated-only contract correction; no execution authorized

## Why this amendment exists

Independent read-only review after the FS3 implementation proof found several
ambiguities that must be resolved before the one-shot full rehearsal:

1. the contract says one prediction-stream validation pass, while the frozen
   score worker deliberately traverses the stream once to verify the target-
   blind freeze and once to score after target delivery;
2. the reduced verifier accepts any positive row count divisible by 64 rather
   than the exact full 91,392-row / 1,428-set inventory;
3. the contract names separate discovery and independent-replication target
   envelopes, while the frozen generated transport uses one canonical file
   containing two disjoint logical cohort partitions;
4. the reduced verifier checks data surfaces but does not independently hash
   every registered implementation identity;
5. verifier path preflight follows symlinks before no-follow descriptor opens,
   and its child environment lacks the producer's active socket guard; and
6. the stored runtime cannot include the final atomic publication syscall that
   writes the scalar itself.

These are proof-architecture defects, not scientific results.
**No full FS3 run may begin under the ambiguous contract.**

## Frozen corrections

### One verifier, two traversals

FS3 keeps exactly one independent verifier/scorer child. That one invocation
must perform exactly two strictly sequential prediction-stream traversals:

1. a target-blind freeze, order, cardinality, probability, inventory, and file-
   identity verification; and
2. a score traversal only after the verified freeze and authorized target
   delivery.

This is one verifier invocation, not two verifier runs and not two model runs.
The verifier still has zero model, fit, transform, inference, threshold,
calibration, prediction-creation, language-model, or update capability.

### Exact full inventory

The full verifier must require exactly:

- 42 complete fictional participants across two 21-person cohorts;
- 17 conditions and two endpoints;
- 1,428 prediction sets;
- 91,392 prediction rows;
- 64 rows per set;
- two logical cohort target deliveries and two cohort scores; and
- zero post-target updates.

Any smaller divisible inventory, duplicate, omission, order drift, invalid
probability, penalty bypass, or aggregate mismatch parks the consumed attempt.

### Two logical cohort envelopes in one transport

The single `sealed-targets.json` descriptor is an outer transport only. Its
canonical mapping must contain exactly `discovery` and
`independent_replication`, with disjoint complete item-id mappings. The frozen
transaction-level delivery nonce authenticates that one post-freeze transport;
the scorer must still validate and count two logical cohort deliveries and two
separate cohort scores. This does not permit a combined cohort score or one
logical delivery.

### Independent identity and capability checks

The future full wrapper must pass preopened no-follow descriptors for an exact
identity allowlist. The verifier must independently hash and match the FS3
contract, this amendment, wrapper proof, verifier worker, score worker,
score-only module, streaming scorer, and producer transcript identities before
target access. It may receive no repository path.

All producer inputs must be opened by basename relative to one no-follow
producer-directory descriptor. `Path.is_file()`, symlink-following preflight,
hard-linked inputs, inode substitution, and path re-resolution are forbidden.
The verifier must run from its isolated work directory with the active socket
guard installed and must retain the existing static zero-network capability
audit.

### Resource and publication boundary

One 180-second absolute deadline remains shared by setup, reservation,
producer, verifier, cleanup, staged result serialization, and staged-result
fsync. Child phases require continuous parent-plus-child process-tree polling;
bounded parent-only phases require RSS checks before and after each phase and
must use the existing fixed 8 MiB reservation buffer. The stored runtime ends
after staged-result fsync and immediately before the final no-replace atomic
promotion, because a file cannot contain a timestamp sampled after its own
publication. Final promotion must still occur before the same absolute
deadline or the CLI must report a consumed park; promotion latency is not
scientific or end-to-end device latency.

## Ordered barriers

1. This amendment and its exact test must be committed, pushed, pass Base
   Python and Optional Neuro Readers, and reach GitHub `main`.
2. The fail-closed full wrapper may then be revised only to implement these
   corrections using generated/mock fixtures.
3. That exact wrapper and its mock qualification must become remotely green.
4. A separate immutable proof must bind the exact wrapper commit, both jobs,
   all identity artifacts, and zero prior FS3 attempts, then itself become
   remotely green.
5. Only then may the sole generated-only `COMM-P0-G-FS3-R0` attempt be
   considered. Receipt creation consumes the attempt; no retry, rerun, resume,
   repair, or substitution is allowed.

No barrier authorizes an official qualification, real/private access, human or
device operation, network operation, release, Tier C action, or claim upgrade.

Engineering capability added: the prospective verifier contract now has exact
inventory, traversal, identity, envelope, filesystem, network, and runtime
semantics suitable for a one-shot generated resource test.

Scientific claim not established: this amendment performs no numerical run and
accesses no EEG or human target, so it establishes no communication decoding,
EEG-beyond-peripheral advantage, unseen-person generalization, independent
replication, causal live operation, hardware result, or clinical value.
