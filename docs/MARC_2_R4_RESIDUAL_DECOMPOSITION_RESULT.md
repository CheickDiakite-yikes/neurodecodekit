# MARC2-VR13A R4 Residual Decomposition Result

Date: 2026-08-20

Route: `MARC2VR13A-G1`

Status: **Generated qualification passed; remote implementation proof pending**

Machine result:
`registries/marc2_r4_residual_decomposition_result.v0.json`

## Result

The registered generated matrix passed all acceptance gates. The unchanged
VR12A adapter was called exactly 32 times: eight cases, canonical and reversed,
across two exact replays. Every aggregate route appeared exactly four times:

| Route | Generated structural class | Count |
|---|---|---:|
| `MARC2VR13A-G1` | clean generated control | 4 |
| `MARC2VR13A-R1` | residual suffix-bearing BIDS identity | 4 |
| `MARC2VR13A-R2` | exact Freewill task token | 4 |
| `MARC2VR13A-R3` | companion run-token inconsistency | 4 |
| `MARC2VR13A-R4` | normalized companion collision | 4 |
| `MARC2VR13A-R5` | incomplete companion set | 4 |
| `MARC2VR13A-R6` | repaired bundle-total mismatch | 4 |
| `MARC2VR13A-R7` | taxonomy or eligibility mismatch | 4 |

Both replays were byte-identical at the aggregate matrix boundary, all routes
were invariant to row order, and the internal matrix digest was
`56430e51b8f97f8c34a2c2fc95706316f2bbf058d7c25b8b8fc2b6a74bf1ae05`.
No generated source changed during validation.

## Measurements

- fixed artifacts verified: 18 files, 342,211 bytes;
- generated input processed: 13,741,736 bytes;
- aggregate output: 5,514 bytes;
- retained generated output: 0 bytes;
- runtime: 2.401633999950718 seconds;
- peak RSS: 36,978,688 bytes;
- threads, workers, and numerical jobs: one each;
- AST-bound VR12A refusal call sites: 23;
- direct refusal mutations passed: 54; and
- raw-data reads, real-cache reads, model runs, and training runs: zero.

End-to-end latency was not measured because this is an in-memory structural
qualification, not a neural or live pipeline.

## What Changed In Our Knowledge

Before VR13A, VR12P R4 compressed seven still-plausible structural classes
into one aggregate route. VR13A now proves that all seven classes are
independently reachable and distinguishable through the unchanged adapter.
That makes a future one-shot private question precise enough to return one
class rather than another broad identity/task/companion bucket.

It does not reveal which class caused the consumed private result. Generated
reachability cannot substitute for a private observation.

## Warnings And Unavailable Fields

- The private failure class and failed value are unavailable.
- A real cohort is unavailable.
- No private row, identity, path, task spelling, companion state, or per-item
  outcome was retained.
- No archive member or neural payload was accessed.
- No target, label, model, prediction, or score exists in this lane.
- Generated routes have no scientific or decoding claim value.

## Next Gate

Commit, push, and require both CI jobs green for the exact implementation and
result. Only then may an all-false private-discriminator authorization packet
be prepared. The packet would still require a fresh Tier C decision before one
new target-free structural read.

FW2 and CIL1 remain ineligible. This result establishes no neural effect,
decoding accuracy, language decoding, live decoding, thought-to-text result,
unseen-person generalization, or portable/clinical capability.
