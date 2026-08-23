# MARC2-VR32P Eligible-Total Direction Private Discriminator Result

Date: 2026-08-23

Lane: `MARC2-VR32P`

Status: consumed at `MARC2VR32P-R2` with a readiness-sampling protocol
deviation; no retry, rerun, resume, repair, fallback, substitution, cleanup,
amendment, output inspection, or private reinspection

Machine result:
`registries/marc2_eligible_total_direction_private_discriminator_private_result.v0.json`

## Proof Before Execution

Packet-bound decision `cb80d07b0e83c3d02d0bb3f7afae08b4ee6ba528`
passed Base Python job `97173642868`, Optional Neuro Readers job
`97173642874`, and CI `32630976806` before Stage 1.

Exact implementation `bae648e269e56dde45eb15295224fbafcc3c8706`
passed Base Python job `97175866956`, Optional Neuro Readers job
`97175866782`, and CI `32631907880`.

Proof-only closeout `5aec8a15f5ee6fa3c6ca9cefcfb4fbfead9dd72f`
then passed Base Python job `97177262321`, Optional Neuro Readers job
`97177262387`, and CI `32632497701`. No qualification or private operation was
repeated during closeout.

## One-Shot Result

The registered command opened and strict-parsed exactly 418,755 target-free
structural bytes once, called VR31A once, and made one nested VR29A call, one
nested VR25A call, and one direction comparison. It returned
`MARC2VR32P-R2` and is now consumed.

Under the frozen route table, R2 means the filtered eligible total is above
the registered public total of 195. The exact total, difference magnitude,
failed private value, row, path, identity, participant, selection,
reservation, and cohort remain unavailable. No cohort was frozen.

Runtime was 20.141367041040212 seconds and peak RSS was 30,130,176 bytes
under one CPU thread, one worker, and one numerical job. Network and
new-payload bytes were zero. A post-execution filesystem-capacity check found
113,434,021,888 bytes available; it did not inspect the private source or
consumed output.

## Protocol Deviation

The returned aggregate report records five readiness samples. The frozen
authorization packet specified three fresh readiness samples. The private
invocation therefore exceeded the registered readiness-sample count by two,
even though it stayed within the 650-second runtime ceiling and all private
source, parser, model, network, and output-operation limits reported by the
executor.

This mismatch is material. The R2 route is retained as a bounded engineering
observation, but the invocation is not described as a fully protocol-
conforming registered result and upgrades no evidence or scientific claim.
The lane is consumed, so the deviation cannot be repaired by rerunning it.

## Output Measurement Boundary

The returned aggregate JSON is reproduced in the machine record and can be
canonicalized without reading the consumed output. The executor did not
return the readiness-certificate, consumed-marker, or report byte counts, so
exact combined incremental output bytes are unavailable. They were not
recovered by listing, statting, opening, or inspecting the consumed output
root.

The implementation enforces a 1 MiB combined cap before returning, but this
lane did not directly report the exact combined byte total. That telemetry
gap is recorded rather than upgraded into a measured cap result.

## Operation Boundary

This tracked result was created only from the aggregate JSON returned by
`execute`, the ordinary filesystem-capacity summary, and already public proof
records. The private report, readiness certificate, consumed marker, output
root, and source were not inspected after execution. Consumed VR20P, VR22P,
VR24P, VR26P, VR28P, and VR30P state was untouched.

Archive members, neural payloads, signals, events, channels, geometry,
targets, labels, caches, features, splits, models, training, inference,
predictions, scoring, FW2/CIL1, network, providers, streams, devices,
hardware, releases, and other projects were untouched.

## What Comes Next

The next safe task is an artifact-only and generated-only failure review that
fixes the readiness sampler to an exact registered count and strengthens its
tests before any future packet. VR32P itself cannot be rerun. Any later
private discriminator, cohort freeze, archive or neural payload access,
target/model/score work, FW2, or CIL1 remains a new Tier C packet and
decision.

Engineering capability added: one proof-separated target-free structural
invocation observed the aggregate above-195 direction without exposing a
count, participant, or cohort, while the audit caught and bounded a readiness-
sampling deviation.

Scientific claim not established: no neural signal, target, model,
prediction, or score was accessed, and the execution was not fully protocol-
conforming, so this establishes no neural effect, decoding performance,
language decoding, unseen-person generalization, live decoding, or thought-
to-text capability.
