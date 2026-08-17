# MARC2-VR11P F03 Private Discriminator Result

Date: 2026-08-17

Lane: `MARC2-VR11P`

Status: **Consumed once at aggregate route `MARC2VR11P-R2`; no rerun is open**

Machine result:
`registries/marc2_f03_private_discriminator_result.v0.json`

## Green Order

The packet-bound decision was remotely green before implementation. Final exact
implementation `2093ad542d5043c97e2a3b0cabb605009e66600e` then passed Base
Python job `95421634020`, Optional Neuro Readers job `95421633971`, and CI
`32041540553`. Proof-only closeout
`e569bcccfde9bcf5e1116de1b892fed79373c137` passed Base Python job
`95422480212`, Optional Neuro Readers job `95422480363`, and CI
`32041863346` before the sole registered invocation.

## Observation

The one command crossed three passing readiness samples, created the fresh
certificate and consumed marker, opened and strict-parsed exactly 418,755
target-free structural bytes once, required outer `MARC2VR6-F02` plus nested
`MARC2VR2-F03`, called the exact VR10B discriminator once, and retained only
`MARC2VR11P-R2`.

Under the frozen route table, R2 means only that the exact structural manifest
reaches F03 class P15, the suffix-bearing BIDS identity class. The result does
not retain or reveal the failed predicate value, source row, member name, path,
participant identity, candidate selection, or cohort.

## Measurements

| Measure | Observed | Cap |
|---|---:|---:|
| Structural input | 418,755 bytes | exactly 418,755 bytes once |
| VR6 calls | 1 | 1 |
| VR10B calls | 1 | 1 |
| Runtime | 10.041579249984352 seconds | 650 seconds |
| Peak RSS | 34,701,312 bytes | less than 268,435,456 bytes |
| Readiness certificate | 1,228 bytes | 65,536 bytes |
| Consumed marker | 253 bytes | bounded output |
| Aggregate report | 2,101 bytes | bounded output |
| Combined output | 3,582 bytes | 1,048,576 bytes |

The command used one CPU thread, one worker, and one numerical job. Raw-data
reads, real-cache reads, model runs, training runs, archive payload operations,
signal/event/channel/geometry/target/label operations, network/provider calls,
hardware operations, operations on other projects, and claim upgrades were
all zero. End-to-end decoding latency was not measured.

## Consequence

VR11P is consumed with no retry, rerun, resume, repair, fallback,
substitution, or private reinspection. R2 selects the subject of a future
prospective generated-only P15 repair contract; it does not authorize that
repair or another private read. A later repair must preserve the frozen F03
rule until it is independently specified and qualified.

FW2 and CIL1 remain ineligible because this diagnostic produced no candidate
cohort and opened no archive member. The next safe work is artifact-only and
generated-only design for the P15 structural class.

Engineering capability added: the proof-gated one-shot wrapper localized the
remaining target-free F03 blocker to one aggregate structural class without
retaining a private value or identity.

Scientific claim not established: no neural payload, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding accuracy, language decoding, live decoding, or thought-to-text
capability.
