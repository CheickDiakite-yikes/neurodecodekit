# MARC2-VR31A R1 Eligible-Total Direction Discriminator Implementation

Date: 2026-08-23

Lane: `MARC2-VR31A`

Status: generated qualification passed; remote implementation proof pending

Machine records:

- `registries/marc2_r1_eligible_total_direction_discriminator_implementation.v0.json`
- `registries/marc2_r1_eligible_total_direction_discriminator_result.v0.json`

## Proof Before Implementation

Exact registration `eeab6785b8eadc6d65199fa1ac519173f9c160c7` passed Base
Python job `97163443088`, Optional Neuro Readers job `97163443152`, and CI
`32626878097` before implementation began.

The implementation binds the unchanged 122,263-byte registered input set and
the exact contract SHA-256
`d02b95029e3c3b2b61388d0d838d81108ca11675b752a1530c6135c17f1cdf00`.

## Implemented Surface

The dependency-free module
`src/neurodecodekit/datasets/marc2_r1_eligible_total_direction_discriminator.py`
exposes only:

- `plan`: inspect the frozen generated-only execution plan;
- `qualify`: run the exact 32-path generated matrix.

There is no private executor and no path, URL, route, count, threshold,
output, retry, resource, or source override.

Each generated path calls unchanged VR29A once. Only the eight paths returning
`MARC2VR29A-R1` compare the internally reconstructed generated eligible total
with the immutable public threshold of 195. The count exists only long enough
to choose one route:

| Frozen direction | VR31A route |
|---|---|
| below 195 | `MARC2VR31A-R1` |
| above 195 | `MARC2VR31A-R2` |

Exact and compatibility-only successes remain G1 and G2. Every non-R1
upstream refusal collapses to aggregate R3. The observed count and difference
are never returned, logged, hashed, serialized, or retained.

## Measured Qualification

One fresh-process qualification under one CPU thread, one worker, and one
numerical job passed:

- 8 cases x 2 orders x 2 replays = 32 paths;
- 32 unchanged VR29A calls;
- 8 R1 direction comparisons;
- 1 statically bound immutable threshold predicate;
- VR31A G1/G2/R1/R2/R3 counts = 4/4/4/4/16;
- VR29A G1/G2/R1/R2/R3 counts = 4/4/8/8/8;
- 78 direct refusals;
- exact replay and order-invariant route distribution;
- zero source mutations, zero count retention, and zero retained output.

The pass processed 14,137,216 generated input bytes in
2.8035786249674857 seconds at 39,174,144-byte peak RSS. The canonical
aggregate report was 2,957 bytes. Raw-data reads, real-cache reads, model
runs, training runs, network bytes, and new-payload bytes were zero.

## Boundary

No `.codex_work` path, readiness state, consumed marker, private source,
consumed output, archive member, neural signal, target, label, model,
prediction, score, FW2/CIL1 surface, provider, device, hardware, or other
project was touched.

This generated result does not identify whether the consumed VR30P R1 result
is below or above 195. The next gate is exact implementation commit, push, and
both green CI jobs, followed by a separately green proof-only closeout. Any
private direction discriminator afterward remains a new all-false Tier C
packet and fresh decision.

Engineering capability added: generated witnesses can now distinguish below-
expected from above-expected eligible totals while retaining only an aggregate
route and no observed count.

Scientific claim not established: no neural signal, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
