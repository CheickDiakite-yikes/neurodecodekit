# MARC2-VR14P Incident Aggregate Recovery Result

Date: 2026-08-21

Lane: `MARC2-VR14P`

Status: consumed at `MARC2VR13P-R2`; no retry, rerun, resume, repair,
fallback, substitution, cleanup, or reinspection

Machine result:
`registries/marc2_incident_aggregate_recovery_result.v0.json`

## Proof Before Execution

Activation commit `6bfff69048d4c3cffc971882be3b60c9fcaa5eae` passed Base Python
job `96667351062`, Optional Neuro Readers job `96667350910`, and CI
`32446635433`. The tracked activation record was clean, the explicit one-shot
arm was present, and the command used one CPU thread, worker, and numerical
job.

## One-Shot Result

The registered command opened and strict-parsed only the 1,543-byte aggregate
report once and wrote one 1,945-byte aggregate recovery receipt. Runtime was
0.0008393750176765025 seconds and peak RSS was 25,853,952 bytes. Network and
new payload bytes were zero.

The recovered route was `MARC2VR13P-R2`. Under the frozen route ceiling this
localizes the consumed structural failure to the suffix-bearing BIDS identity
class. It does not reveal the failed value, predicate, row, path, identity,
participant, run, task, candidate, or cohort. Aggregate cohort, bundle, and
core-member counts are all zero, and no private cohort was written.

## Operation Boundary

Exactly one aggregate lstat, content open, strict JSON parse, and receipt write
occurred. Readiness-certificate, consumed-marker, structural-source,
private-manifest, archive, neural, signal, event, channel, geometry, target,
label, training, inference, prediction, score, network, provider, stream,
device, hardware, FW2/CIL1, other-project, retry, and claim-upgrade operations
were all zero.

The ignored output was not listed, reopened, hashed, or otherwise inspected
after execution. This result is transcribed only from the command's returned
aggregate JSON.

## What Comes Next

The next safe work is a separately frozen artifact-only and generated-only
decomposition of the suffix-bearing identity class against the committed
producer and validator code. Any new private read, manifest recovery, source
inspection, archive or neural payload access, target/model/score work, FW2, or
CIL1 remains a new Tier C packet and decision.

Engineering capability added: the proof-separated one-shot recovered the
existing aggregate structural route without reopening the structural source or
private manifest.

Scientific claim not established: no neural data, target, model, prediction,
or score was accessed, so this establishes no neural effect, decoding
performance, language decoding, live decoding, or thought-to-text capability.
