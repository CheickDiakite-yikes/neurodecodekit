# MARC2-VR3 Variable-Domain Private Recovery Result

Date: 2026-08-16

Lane: `MARC2-VR3`

Status: **Consumed at machine preflight; no private-path or output-root
operation occurred; no retry or rerun is open**

Machine result:
`registries/marc2_variable_domain_private_recovery_failure_result.v0.json`

## Green Execution Proof

Exact implementation commit
`24678760106b6a5a9ea035c14f628ec909755e61` passed Base Python job
`95207398015`, Optional Neuro Readers job `95207398092`, and CI
`31964473405`. The tracked HEAD remained exact and clean before invocation.

The command was invoked once with all five numerical-thread variables fixed to
one and only the four registered proof arguments. There was no source, output,
participant, split, cap, or fallback override.

## Final Route

The one invocation returned:

```text
MARC2VDR-F01: machine resource preflight refused
```

This route occurs after exact implementation proof validation and before
output-root preparation or retained-path preflight. The executor therefore did
not check a component of the registered private path, create or inspect the new
output root, write a consumed marker, open or hash the manifest, parse JSON, or
call the VR2 adapter.

The frozen preflight combines normalized one-minute load, free disk, and
process RSS in one aggregate refusal. The exact failing predicate and its value
were intentionally not emitted and are unavailable. A later machine snapshot
would not reconstruct the invocation and is not treated as evidence.

## Measured Boundary

The command returned in 1.166707792 external wall seconds. Internal runtime,
peak RSS, normalized load, free disk, and logical CPU measurements were not
emitted. Generated output files and incremental disk bytes were zero. Network,
archive-member, signal, event, target, channel, derivative, model, prediction,
freeze, scoring, provider, hardware, and claim operations were all zero.

The private input count is exactly zero bytes and zero content opens. No real
participant, bundle, or member selection exists. The generated 16-subject,
96-bundle, 384-member prefix remains interface evidence only and was not
promoted to a real cohort.

## Disposition

The registered invocation is consumed. There is no retry, rerun, resume,
repair, fallback, alternate path, or post-result threshold change. Do not stat,
open, hash, parse, rename, delete, or reuse a VR3 output root or the registered
private manifest under this lane.

`MARC2-FW2` remains ineligible because there is no frozen real cohort identity.
The next safe work is a separately named prospective machine-stable structural
recovery that can wait or fail diagnostically before consumption while
preserving the same source, selector, storage, privacy, and no-payload
boundaries. FW2 architecture research may continue, but real payload access,
training, prediction freezing, target delivery, and scoring require a new
immutable packet and fresh Tier C decision after cohort freeze.

Engineering capability added: the exact remotely green wrapper failed closed
before any private-path or output-root operation when its machine safety gate
was not satisfied.

Scientific claim not established: no human neural payload, target, prediction,
or score was accessed, so this result establishes no neural effect, decoding
accuracy, language decoding, or thought-to-text capability.
