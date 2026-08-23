# MARC2-VR28P Inventory/Taxonomy Private Discriminator Result

Date: 2026-08-23

Lane: `MARC2-VR28P`

Status: consumed at `MARC2VR28P-R1`; no retry, rerun, resume, repair,
fallback, substitution, cleanup, amendment, output inspection, or private
reinspection

Machine result:
`registries/marc2_inventory_taxonomy_private_discriminator_private_result.v0.json`

## Proof Before Execution

Packet-bound decision `718c3de6ddb0030b1ba39fa0e42250e97db01072`
passed Base Python job `97133595196`, Optional Neuro Readers job
`97133595235`, and CI `32614796767` before Stage 1.

The initial implementation `06174e1456c57c050c48f5b1bce9b276629e2f25`
passed Base Python job `97137205238`, Optional Neuro Readers job
`97137205346`, and CI `32616187929`. A generated-only proof-transition test
was then hardened without changing the module or measured qualification.
Exact hardened implementation `6d3b770d0e67c8b394c6a1a7581c21ae7b202909`
passed Base Python job `97138335047`, Optional Neuro Readers job
`97138335116`, and CI `32616632414`.

Proof-only closeout `96bff687013dcbfb507455b5f8c045977bc84fe8`
then passed Base Python job `97139815087`, Optional Neuro Readers job
`97139815147`, and CI `32617240661`. No qualification or private operation
was repeated during closeout.

## One-Shot Result

The registered command collected three fresh readiness samples, opened and
strict-parsed exactly 418,755 target-free structural bytes once, called VR25A
once, called the frozen VR27A route map once, and returned
`MARC2VR28P-R1`. Runtime was 10.065900957910344 seconds and peak RSS was
30,654,464 bytes under one CPU thread, one worker, and one numerical job.
Network and new-payload bytes were zero.

Under the frozen route table, R1 means the remaining blocker is in the
eligible-inventory or participant-session distribution class. The real source
did not take the unknown-participant taxonomy route in this execution.

This result does not identify the failed predicate, observed count, direction,
magnitude, row, path, identity, participant, selection, reservation, or
cohort. No cohort was frozen.

## Output Measurement Boundary

The returned aggregate JSON is reproduced in the machine record and can be
canonicalized without reading the consumed output. The executor did not
return the readiness-certificate or consumed-marker byte counts, so exact
combined incremental output bytes are unavailable. They were not recovered by
listing, statting, opening, or inspecting the consumed output root.

The implementation enforces a 1 MiB cap on each write and the execution
returned successfully, but this lane did not directly report the exact
combined readiness, marker, and report byte total. That telemetry gap is
recorded rather than silently upgraded into a measured cap result.

## Operation Boundary

This tracked result was created only from the aggregate JSON returned by
`execute` and the already public proof records. The private report, readiness
certificate, consumed marker, output root, and source were not inspected after
execution. Consumed VR20P, VR22P, VR24P, and VR26P state was untouched.

Archive members, neural payloads, signals, events, channels, geometry,
targets, labels, caches, features, splits, models, training, inference,
predictions, scoring, FW2/CIL1, network, providers, streams, devices,
hardware, releases, and other projects were untouched.

## What Comes Next

The next safe task is an artifact-only and generated-only R1 decomposition
that separates eligible-inventory arithmetic from participant-session
distribution arithmetic without touching the consumed source. Any later
private discriminator, cohort freeze, archive or neural payload access,
target/model/score work, FW2, or CIL1 remains a new Tier C packet and decision.

Engineering capability added: one proof-separated target-free structural
invocation excluded unknown-participant taxonomy and localized the remaining
cohort blocker to eligible-inventory or participant-session distribution
validation without exposing private detail.

Scientific claim not established: no neural signal, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
