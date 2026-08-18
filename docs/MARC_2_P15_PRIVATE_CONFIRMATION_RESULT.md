# MARC2-VR12P Target-Free Private Confirmation Result

Date: 2026-08-18

Lane: `MARC2-VR12P`

Status: **Consumed once at aggregate route `MARC2VR12P-R4`; no rerun is open**

Machine result:
`registries/marc2_p15_private_confirmation_result.v0.json`

## Green Order

Packet-bound decision `b0f251a7fb1b69a0ed79f525ab100499e130390a`
passed Base Python job `95894058802`, Optional Neuro Readers job
`95894058625`, and CI `32193964660` before implementation. Final exact
implementation `d98a0115d2fd113929d512dfc7fb372a38b8f5c8` passed Base
Python job `95903371693`, Optional Neuro Readers job `95903371721`, and CI
`32197145780`. Proof-only closeout
`4280aa603da58de4eac220496e09aa97bcce65cb` then passed Base Python job
`95905146777`, Optional Neuro Readers job `95905146692`, and CI
`32197772060` before the sole registered invocation.

## Observation

The one command crossed the frozen readiness boundary, opened and strict-
parsed exactly 418,755 target-free structural bytes once, and called the exact
VR12A adapter once. It consumed at `MARC2VR12P-R4` without creating a private
cohort manifest.

Under the frozen route table, R4 means only that the repaired source still
refused within the identity, task, or companion-validation layer. The result
does not retain or reveal the failed predicate, value, row, member path,
participant identity, task spelling, companion state, selection, or cohort.
Accepting one- or two-digit run indices was therefore insufficient for this
exact source; it does not establish which remaining check failed.

## Measurements

| Measure | Observed | Cap |
|---|---:|---:|
| Structural input | 418,755 bytes | exactly 418,755 bytes once |
| VR12A calls | 1 | 1 |
| Runtime | 0.02449654199881479 seconds | 650 seconds |
| Peak RSS | 30,162,944 bytes | less than 268,435,456 bytes |
| Combined output | 2,669 bytes | 2,097,152 bytes |
| Private cohort freezes | 0 | at most 1, R1 only |

The command used one CPU thread, one worker, and one numerical job. Raw-data
reads, real-cache reads, archive-member reads, signal/event/channel/geometry,
target/label, checkpoint, model, training, inference, prediction, scoring,
network, provider, hardware, other-project, FW2/CIL1, and claim-upgrade
operations were all zero. End-to-end decoding latency was not measured.

## Verification

All 63 focused VR12P tests and all 4,223 dependency-light tests pass with 204
expected skips and zero failures. Ruff 0.15.20, compileall, all 294 registry
JSON files, module CLI help, and `git diff --check` pass.

## Consequence

VR12P is consumed with no retry, rerun, resume, repair, fallback,
substitution, or private reinspection. R4 does not freeze a real cohort, so
FW2 and CIL1 remain ineligible. The next safe lane is separately frozen,
artifact-only and generated-only decomposition of the residual identity/task/
companion predicates. Another private read would require a new Tier C packet
and fresh packet-bound decision.

Engineering capability added: the proof-gated one-shot wrapper tested the
generated run-index repair against the registered target-free structural
source and safely retained one aggregate refusal class.

Scientific claim not established: no archive neural payload, signal sample,
target, model, prediction, or score was accessed, so this establishes no neural
effect, decoding accuracy, language decoding, live decoding, or thought-to-
text capability.
