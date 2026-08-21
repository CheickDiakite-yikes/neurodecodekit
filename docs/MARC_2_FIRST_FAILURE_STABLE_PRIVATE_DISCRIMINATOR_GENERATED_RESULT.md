# MARC2-VR18P Generated Stage 1 Result

Date: 2026-08-21

Lane: `MARC2-VR18P`

Route: `MARC2VR18P-G1`

Status: **Generated qualification passed; private Stage 2 remains proof-gated**

Machine record:
`registries/marc2_first_failure_stable_private_discriminator_result.v0.json`

## Result

The frozen five-case matrix passed in canonical and reversed source order
across two exact replays. Generated success plus each of the four registered
first-failure classes appeared exactly four times:

```text
MARC2VR18P-G1: 4
MARC2VR18P-R4: 4
MARC2VR18P-R5: 4
MARC2VR18P-R6: 4
MARC2VR18P-R7: 4
```

The matrix made exactly 20 unchanged VR16A calls and 16 frozen VR17C map
lookups. The temporary fixed-path success rehearsal added one VR16A call and
zero map lookups. All 82 direct refusal checks passed.

## Measurements

| Measure | Value |
|---|---:|
| Generated input | 9,037,650 bytes |
| Aggregate report | 2,020 bytes |
| Peak temporary output | 217,041 bytes |
| Retained output | 0 bytes |
| Runtime | 1.4131330830277875 seconds |
| Peak RSS | 37,879,808 bytes |
| CPU threads / workers / jobs | 1 / 1 / 1 |
| Network / new payload | 0 / 0 bytes |

Replay SHA-256:
`5c214a1e9e5b3aa53b30931ff2d4573b675cb9bf18b41753b0da2eaae9c8bd35`.

## Zero Counters

Repository-private or Git-ignored operations, readiness operations, real
VR16A calls, real VR17C lookups, archive reads, signal/event/channel/geometry
reads, target or label reads, derivatives, model training, inference,
prediction, scoring, provider calls, FW2/CIL1 operations, hardware operations,
other-project operations, retries, and claim upgrades were all zero.

## Meaning

This result proves that the registered wrapper mechanics can preserve the
success path and distinguish all four generated failure classes using one
VR16A call per source. It does not reveal which route a private source will
take.

Engineering capability added: one fixed-path generated composition now keeps
success distinct from four exact first-failure classes under replay and order
changes.

Scientific claim not established: no private or neural payload was accessed,
no real cohort was frozen, and no neural effect or decoding result was tested.
