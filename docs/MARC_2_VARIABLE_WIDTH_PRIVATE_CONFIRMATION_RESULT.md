# MARC2-VR16P Variable-Width Private Confirmation Result

Date: 2026-08-21

Lane: `MARC2-VR16P`

Status: consumed at `MARC2VR16P-R4`; no retry, rerun, resume, repair,
fallback, substitution, cleanup, or private reinspection

Machine result:
`registries/marc2_variable_width_private_confirmation_result.v0.json`

## Proof Before Execution

Exact Stage 1 implementation `55f23d60621949ea008cca1e3ade80a3127cfc70`
passed Base Python job `96717830579`, Optional Neuro Readers job
`96717830410`, and CI `32464397821`.

Proof-only closeout `865d76aff51842e3b57600a7dab399d2bbe91d2e`
then passed Base Python job `96719949813`, Optional Neuro Readers job
`96719949597`, and CI `32465104587`. No registered qualification or private
operation was repeated during closeout.

## One-Shot Result

The registered command collected three fresh readiness samples, opened the
fixed 418,755-byte target-free structural source once, strict-parsed it once,
and called VR16A once. It returned `MARC2VR16P-R4` and created no private
cohort manifest. Runtime was 0.02044062502682209 seconds, peak RSS was
30,474,240 bytes, combined output was 2,702 bytes, and network and new payload
bytes were zero.

Under the frozen route table, R4 means only that numeric identity, exact task
token, or companion validation refused. It does not identify which predicate
failed and does not retain a token, filename, path, row, participant, value,
candidate, selection, or cohort. The route therefore cannot support an
unregistered repair or another private read.

## Operation Boundary

The invocation wrote only its authorized readiness certificate, consumed
marker, and aggregate report. The aggregate report was inspected once through
the fixed public `inspect` command to confirm the returned JSON. No private
manifest was created or inspected.

Archive members, neural payloads, signals, events, channels, geometry, targets,
labels, caches, features, splits, models, training, inference, predictions,
scoring, FW2/CIL1, network, providers, streams, devices, hardware, releases,
and other projects were untouched.

Five focused result tests and all 4,529 dependency-light tests pass with 204
expected skips and zero failures. Ruff, strict registry JSON, and diff hygiene
also pass.

## What Comes Next

The next safe task is a separately frozen artifact-only and generated-only R4
predicate decomposition. It may distinguish the exact generated numeric-
identity, task-token, and companion classes without touching this consumed
source. Any later private discriminator, cohort freeze, archive or neural
payload access, target/model/score work, FW2, or CIL1 remains a new Tier C
packet and decision.

Engineering capability added: the proof-separated one-shot confirmed that the
real target-free structure reaches VR16A and localized the remaining refusal
to one frozen three-part aggregate class without exposing private identities.

Scientific claim not established: no neural payload, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, live decoding, or thought-to-text
capability.
