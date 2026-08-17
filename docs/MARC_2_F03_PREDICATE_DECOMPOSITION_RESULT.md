# MARC2-VR10A F03 Predicate Decomposition Result

Date: 2026-08-17

Route: `MARC2VR10A-G1`

Status: **Artifact-only and generated-only qualification remotely green**

Machine result:
`registries/marc2_f03_predicate_decomposition_result.v0.json`

## Result

The exact validator path contains 20 frozen F03 leaf predicate classes.
Tracked producer guarantees and the committed live aggregate exclude 15
without another private read. Five remain source-dependent:

1. UTF-8 member-name length at or below 1,024 bytes;
2. suffix-bearing BIDS identity and filename/path agreement;
3. the exact lowercase Freewill task token;
4. logical companion uniqueness after parent prefixes collapse; and
5. completeness of each four-companion run group.

Each unresolved class received one full-scale generated witness. Every witness
passed the exact central-directory parser and live producer, then returned
outer `MARC2VR6-F02` plus nested `MARC2VR2-F03`. The unmodified control passed
VR6. Both outcomes were unchanged by canonical versus reversed source order
and by a complete second replay.

## Measurements

| Measure | Observed | Cap |
|---|---:|---:|
| Fixed tracked artifacts | 17 / 480,963 bytes | exact hashes required |
| Generated cases | 6 | 6 |
| Exact paths | 24 | 24 |
| Parser-entry visits | 29,448 | 29,448 |
| VR6 calls | 24 | 24 |
| Control successes | 4 | 4 |
| Nested F03 witnesses | 20 | 20 |
| Generated input | 6,979,708 bytes | 16,777,216 bytes |
| Aggregate output | 10,751 bytes | 1,048,576 bytes |
| Retained output | 0 bytes | 0 bytes |
| Runtime | 1.8363693330029491 seconds | 30 seconds |
| Peak RSS | 45,072,384 bytes | 268,435,456 bytes |
| Direct refusals | 47 | at least 40 |

The pass used one CPU thread, one worker, and one numerical job. Raw-data
reads, real-cache reads, model runs, training runs, private operations, archive
payload operations, network operations, and operations on other projects were
all zero. End-to-end latency was not measured because this is structural
metadata qualification, not a decoder.

## What This Resolves

VR9P's broad F03 route is no longer an unstructured bucket for development.
We now have a complete frozen five-mechanism possibility set and a known-good
generated witness for each mechanism. A prospective discriminator can be
tested against all five before any further private authorization is considered.

## What Remains Unknown

The result does not identify which of the five mechanisms, if any, caused the
consumed private F03 outcome. It contains no failed value, row, path,
participant, session, run, selection, or cohort. Generated witnesses cannot be
used to infer private content.

No archive member, signal sample, event, channel, geometry, target, label,
derivative, model, prediction, or score was accessed. FW2 and CIL1 remain
closed because no real cohort identity exists.

## Disposition

Exact implementation `84103a5fab86b7c7c8d3cf3af00c9efe3457470c` passed Base
Python job `95295212461`, Optional Neuro Readers job `95295212440`, and CI
`31998811585`. The next safe engineering lane is a separately frozen
aggregate-safe discriminator that emits one of the five predicate-class routes
without values or identities. Any later private invocation still requires a
new immutable Tier C packet and fresh decision; this result grants no such
authority.

Engineering capability added: every still-plausible F03 mechanism now has an
exact full-scale generated witness and deterministic two-layer route proof.

Scientific claim not established: no private or neural data, target, model,
prediction, or score was used, so this establishes no neural effect or decoding
performance.
