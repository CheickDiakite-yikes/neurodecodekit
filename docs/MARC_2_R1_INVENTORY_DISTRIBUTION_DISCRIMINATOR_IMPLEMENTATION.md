# MARC2-VR29A R1 Inventory/Distribution Discriminator Implementation

Date: 2026-08-23

Lane: `MARC2-VR29A`

Status: generated qualification passed; remote implementation proof pending

Machine records:

- `registries/marc2_r1_inventory_distribution_discriminator_implementation.v0.json`
- `registries/marc2_r1_inventory_distribution_discriminator_result.v0.json`

## Proof Before Implementation

Exact registration `fcd088cc2eef6556f36ed596c6d9bb6c7ee9d7c3` passed
Base Python job `97143828645`, Optional Neuro Readers job `97143828576`, and
CI `32618866986` before implementation began.

The implementation binds the unchanged 166,935-byte registered input set and
the exact contract SHA-256
`09fc1baa9e84d65bf8d9e8780d77a2d6707c27a8c30b6b49387c027ac020c607`.

## Implemented Surface

The dependency-free module
`src/neurodecodekit/datasets/marc2_r1_inventory_distribution_discriminator.py`
exposes only:

- `plan`: inspect the frozen generated-only execution plan;
- `qualify`: run the exact 32-path generated matrix.

There is no private executor and no path, URL, route, reason, count,
threshold, output, retry, resource, or source override.

Each generated path calls unchanged VR25A once. Only the 16 paths returning
`MARC2VR25A-R1` re-run unchanged VR2 eligible filtering. The wrapper maps the
two exact internal reasons to aggregate routes and discards the reasons:

| Frozen VR2 check | VR29A route |
|---|---|
| filtered eligible total differs | `MARC2VR29A-R1` |
| eligible participant-session counts differ | `MARC2VR29A-R2` |

Exact and compatibility-only successes remain G1 and G2. Unknown-taxonomy and
incomplete-companion controls collapse to aggregate R3. Every other upstream
route fails closed.

## Measured Qualification

One fresh-process qualification under one CPU thread, one worker, and one
numerical job passed:

- 8 cases x 2 orders x 2 replays = 32 paths;
- 32 unchanged VR25A calls;
- 16 additional R1 filter-discriminator calls;
- 2 statically bound VR2 refusal sites;
- VR29A G1/G2/R1/R2/R3 counts = 4/4/8/8/8;
- VR25A G1/G2/R1/R2/R3 counts = 4/4/16/4/4;
- 77 direct refusals;
- exact replay and order-invariant route distribution;
- zero source mutations and zero retained output.

The pass processed 14,137,216 generated input bytes in
2.2789369999663904 seconds at 37,371,904-byte peak RSS. The canonical
aggregate report was 2,880 bytes. Raw-data reads, real-cache reads, model
runs, training runs, network bytes, and new-payload bytes were zero.

## Boundary

No `.codex_work` path, readiness state, consumed marker, private source,
consumed output, archive member, neural signal, target, label, model,
prediction, score, FW2/CIL1 surface, provider, device, hardware, or other
project was touched.

This generated result does not identify whether the consumed VR28P R1 result
was eligible-total arithmetic or participant-session distribution arithmetic.
The next gate is exact implementation commit, push, and both green CI jobs,
followed by a separately green proof-only closeout. Any private discriminator
afterward remains a new all-false Tier C packet and fresh decision.

Engineering capability added: generated witnesses can now distinguish the two
exact arithmetic checks collapsed into VR28P R1 while retaining only an
aggregate route.

Scientific claim not established: no neural signal, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
