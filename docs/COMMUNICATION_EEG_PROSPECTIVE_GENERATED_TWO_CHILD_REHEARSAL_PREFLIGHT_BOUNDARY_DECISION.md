# COMM-P0 generated FS2 preflight-boundary decision

Date: 2026-08-28
Gate: `COMM-P0-G-FS2-v0`
Run: `COMM-P0-G-FS2-R0`
Scope: generated-only Tier B control-plane clarification

## Why this record exists

After the exact implementation proof was green and present on GitHub `main`,
the CLI was invoked with `outputs/comm-p0-fs2/result.json` and
`outputs/comm-p0-fs2/receipt.json`. The shared parent directory did not exist.
The registered destination normalizer therefore refused with
`COMM-P0-G:FS2-publication_collision_partial_write_or_cleanup_escape`.

The refusal occurred before the measured attempt start and before creation of
the durable no-replace rehearsal receipt. No result, receipt, temporary root,
disk reservation, child process, generated payload, model operation, target
delivery, score, network operation, real/private operation, or official-marker
operation occurred. The destination directory was also absent afterward.

## Boundary ruling

The exact implementation and its tests already distinguish two phases:

1. launch preflight validates the proof, destination, and free space; and
2. the registered one-shot attempt begins when its durable receipt is created.

Destination collision and insufficient-free-space tests refuse before a
receipt and before execution. Reservation failure is the first tested failure
that occurs after the receipt and is routed to `FS2_PARK` with
`attempt_consumed=true`.

This record therefore classifies the observed missing-parent event as one
non-consuming launch-preflight refusal. It does not reinterpret an FS2 result,
because no FS2 result or generated scientific/model observation existed. It
does not relax the rule after receipt creation: any failure, timeout, refusal,
or park after the durable receipt consumes `COMM-P0-G-FS2-R0`, and no retry,
rerun, resume, or substitution is permitted.

The broader preregistration wording that any refusal consumes is narrowed only
to resolve this phase ambiguity in accordance with the already-green executable
ordering and tests. This decision must itself be committed, pushed, pass both
CI jobs, and be present on GitHub `main` before one corrected launch-preflight
invocation may be made.

## Corrected launch rule

The existing Git-ignored destination directory may be created empty before the
corrected invocation. Both exact result and receipt paths must remain absent.
The implementation, proof, run ID, schedule, resource caps, output names, and
all authority and claim boundaries remain byte-for-byte unchanged.

No implementation change is authorized by this decision. The corrected
invocation allowance is one. If it reaches durable receipt creation, the run is
consumed regardless of outcome. Another pre-receipt refusal also exhausts this
narrow corrected-launch allowance and parks the lane without another launch.

## Counters at this decision

- CLI launch-preflight invocations: 1
- launch-preflight refusals: 1
- registered FS2 attempts consumed: 0
- durable rehearsal receipts: 0
- public FS2 results: 0
- temporary roots or reservations: 0
- child replay processes: 0
- full-scale generated replays: 0
- model fits, inference runs, predictions, target deliveries, and scores: 0
- network, real/private, human, device, stream, and official operations: 0
- scientific claim upgrades: 0
- corrected launch-preflight invocations remaining after this decision is green: 1

## Claim boundary

Engineering capability added: an explicit durable boundary now separates
non-consuming FS2 launch validation from the single consumed generated
rehearsal attempt.

Scientific claim not established: no generated replay or real EEG was run, so
this decision establishes no decoding, EEG-specific, unseen-person,
replication, causal-live, device, or clinical result.
