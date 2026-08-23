# MARC2-VR34P Exact-Count Private Confirmation Result

Date: 2026-08-23

Lane: `MARC2-VR34P`

Status: consumed at `MARC2VR34P-R2` under the exact registered readiness
protocol; no retry, rerun, resume, repair, fallback, substitution, cleanup,
amendment, output inspection, or private reinspection

Machine result:
`registries/marc2_exact_count_private_confirmation_private_result.v0.json`

## Proof Before Execution

Packet-bound decision `5d6a56ecfad01f49d9e7987cc1072c4aab15bd11`
passed Base Python job `97193199080`, Optional Neuro Readers job
`97193198951`, and CI `32639054941` before Stage 1.

Exact implementation `a0e36afd08bc9d6ae9429e9471d4650f6093e406`
passed Base Python job `97196742388`, Optional Neuro Readers job
`97196742556`, and CI `32640499738`.

Proof-only closeout `c863fd4b5bb9c866d6bc5683cb74c9fbeab6d8d8`
then passed Base Python job `97198447774`, Optional Neuro Readers job
`97198447418`, and CI `32641201220`. No qualification or private operation was
repeated during closeout.

## One-Shot Result

The registered command collected exactly three readiness samples with two
fixed five-second sleeps, opened and strict-parsed exactly 418,755 target-free
structural bytes once, called VR33A once, called VR31A once, and made one
nested VR29A call, one nested VR25A call, and one direction comparison. It
returned `MARC2VR34P-R2` and is now consumed.

Under the frozen route table, R2 means the filtered eligible total is above
the registered public total of 195. The exact total, difference magnitude,
failed private value, row, path, identity, participant, selection,
reservation, and cohort remain unavailable. No cohort was frozen.

Runtime was 10.147974541061558 seconds and peak RSS was 26,935,296 bytes
under one CPU thread, one worker, and one numerical job. Network and
new-payload bytes were zero. A post-execution filesystem-capacity check found
110,084,317,184 bytes available; it did not inspect the private source or
consumed output.

## Protocol Fidelity

The returned aggregate report records exactly three readiness samples and two
sleeps, matching the frozen packet. The source-open, strict-parse, VR33A,
VR31A, runtime, peak-RSS, network, and new-payload limits also conform. This
repairs the specific readiness-sampling deviation that bounded VR32P.

Protocol conformance does not reveal the exact count, validate a cohort, or
upgrade a scientific claim. It establishes only that the registered aggregate
structural direction was recovered through the exact finite readiness gate.

## Output Measurement Boundary

The returned aggregate JSON is reproduced in the machine record and can be
canonicalized without reading the consumed output. The executor did not
return the readiness-certificate, consumed-marker, or report byte counts, so
exact combined incremental output bytes are unavailable. They were not
recovered by listing, statting, opening, or inspecting the consumed output
root.

The implementation enforces a 1 MiB combined cap before returning, but this
lane did not directly report the exact combined byte total. That telemetry gap
is recorded rather than upgraded into a measured byte result.

## Verification

Seven focused result tests pass. The complete dependency-light suite passes
5,415 tests with 204 expected skips, exactly seven more than the 5,408-test
proof-closeout baseline. Repository-pinned Ruff 0.15.20, compilation, all 412
registry JSON files, and `git diff --check` pass. Verification performed zero
private or consumed-output operation.

## Operation Boundary

This tracked result was created only from the aggregate JSON returned by
`execute`, an ordinary filesystem-capacity summary, and already public proof
records. The private report, readiness certificate, consumed marker, output
root, and source were not inspected after execution. Consumed VR20P, VR22P,
VR24P, VR26P, VR28P, VR30P, and VR32P state was untouched.

Archive members, neural payloads, signals, events, channels, geometry,
targets, labels, caches, features, splits, models, training, inference,
predictions, scoring, FW2/CIL1, network, providers, streams, devices,
hardware, releases, and other projects were untouched.

## What Comes Next

VR34P cannot be rerun or reinspected. The next safe task is an artifact-only
review of the protocol-conforming R2 boundary and preparation of a separately
frozen packet for any cohort, archive, or neural step. Any later private read,
cohort freeze, archive or neural payload access, target/model/score work, FW2,
or CIL1 remains a new Tier C packet and decision.

Engineering capability added: one proof-separated, exact-readiness-gated
target-free structural invocation established the aggregate above-195
direction without exposing a count, participant, or cohort.

Scientific claim not established: no neural signal, target, model,
prediction, or score was accessed, so this establishes no neural effect,
decoding performance, language decoding, unseen-person generalization, live
decoding, or thought-to-text capability.
