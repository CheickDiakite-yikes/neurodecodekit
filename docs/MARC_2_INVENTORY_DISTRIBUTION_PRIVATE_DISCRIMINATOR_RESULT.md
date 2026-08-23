# MARC2-VR30P Inventory/Distribution Private Discriminator Result

Date: 2026-08-23

Lane: `MARC2-VR30P`

Status: consumed at `MARC2VR30P-R1`; no retry, rerun, resume, repair,
fallback, substitution, cleanup, amendment, output inspection, or private
reinspection

Machine result:
`registries/marc2_inventory_distribution_private_discriminator_private_result.v0.json`

## Proof Before Execution

Packet-bound decision `2bd811e30991997b8b7616e4c9451899f579dc94`
passed Base Python job `97154390311`, Optional Neuro Readers job
`97154390379`, and CI `32623171395` before Stage 1.

Exact implementation `b20d632c184382716509197c2fe1617058a8e230`
passed Base Python job `97157732938`, Optional Neuro Readers job
`97157733105`, and CI `32624543064`.

Proof-only closeout `7ce2c5e7f7dde15dfe1dfafa35058613ae09b016`
then passed Base Python job `97159363190`, Optional Neuro Readers job
`97159363046`, and CI `32625197776`. No qualification or private operation
was repeated during closeout.

## One-Shot Result

The registered command collected three fresh readiness samples, opened and
strict-parsed exactly 418,755 target-free structural bytes once, called VR29A
once, called its unchanged VR25A boundary once, and called the unchanged VR2
eligible filter once. It returned `MARC2VR30P-R1` and is now consumed.

Runtime was 10.091467417078093 seconds and peak RSS was 30,752,768 bytes
under one CPU thread, one worker, and one numerical job. Network and
new-payload bytes were zero. A post-execution filesystem check found
113,453,273,088 bytes available; the run created no new payload data.

Under the frozen route table, R1 means the filtered eligible total differs
from the registered public total of 195. This localizes the structural cohort
blocker more tightly than VR28P. Because the discriminator is ordered, R1
does not establish whether the later participant-session distribution check
would pass or fail.

This result does not identify the observed total, whether it is above or below
195, the difference magnitude, the failed private value, row, path, identity,
participant, selection, reservation, or cohort. No cohort was frozen.

## Output Measurement Boundary

The returned aggregate JSON is reproduced in the machine record and can be
canonicalized without reading the consumed output. The executor did not
return the readiness-certificate or consumed-marker byte counts, so exact
combined incremental output bytes are unavailable. They were not recovered by
listing, statting, opening, or inspecting the consumed output root.

The implementation enforces a 1 MiB cap on each write and the execution
returned successfully, but this lane did not directly report the exact
combined readiness, marker, and report byte total. That telemetry gap is
recorded rather than upgraded into a measured cap result.

## Operation Boundary

This tracked result was created only from the aggregate JSON returned by
`execute` and already public proof records. The private report, readiness
certificate, consumed marker, output root, and source were not inspected after
execution. Consumed VR20P, VR22P, VR24P, VR26P, and VR28P state was untouched.

Archive members, neural payloads, signals, events, channels, geometry,
targets, labels, caches, features, splits, models, training, inference,
predictions, scoring, FW2/CIL1, network, providers, streams, devices,
hardware, releases, and other projects were untouched.

## What Comes Next

The next safe task is an artifact-only and generated-only R1 decomposition
that distinguishes below-expected from above-expected eligible totals without
retaining an observed count or difference. Any later private discriminator,
cohort freeze, archive or neural payload access, target/model/score work, FW2,
or CIL1 remains a new Tier C packet and decision.

Engineering capability added: one proof-separated target-free structural
invocation localized the real blocker to filtered eligible-total arithmetic
without exposing an observed count, participant, or cohort.

Scientific claim not established: no neural signal, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
