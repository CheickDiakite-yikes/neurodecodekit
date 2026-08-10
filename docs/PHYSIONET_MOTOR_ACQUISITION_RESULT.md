# PhysioNet Motor Acquisition Result

Date: 2026-08-09

Status: **Passed; one registered invocation consumed; no retry or rerun**

Sanitized result registry:
`registries/physionet_motor_acquisition_result.v0.json`

Private generated receipts: retained locally, Git-ignored, not committed, not
uploaded, and not reproduced in this document.

## Ordered Proof

The one real-data action occurred only after all earlier gates were green:

| Gate | Exact evidence |
|---|---|
| Registration | `2a7b4188553e221133d788a081b838dbbb9f41bb`, CI `31301730612` |
| Exact request | `f6eb577fdd8c168a4af229248dc56960e3ba75d8`, CI `31302161647` |
| Authorization decision | `00b91edd213112fd186711d06369ae4f836b2243`, CI `31344104565` |
| Fixture-qualified implementation | `92760ce7e3123058f15127b9afd8d5e4bae75321`, CI `31345401581` |
| Base Python implementation job | `93326279510`, passed |
| Optional Neuro Readers implementation job | `93326279396`, passed |

The execution began from the exact implementation commit with no tracked
changes, one CPU thread, one worker, one numerical job, and more than 2 GiB
free. The unrelated tracker inspection NDJSON remained untouched.

## Result

All 12 registered acquisition gates passed together:

- PhysioNet EEGMMIDB version `1.0.0`, DOI `10.13026/C28G6P`, public
  availability, and the ODC Attribution 1.0 license remained exact.
- The three registered metadata documents and all nine EDF HEAD records matched
  the frozen paths, sizes, task mapping, and official SHA-256 identities.
- Exactly nine EDF body requests transferred exactly `23,248,224` bytes.
- Every local file received exactly one opaque sequential size/SHA-256 pass.
- All nine observed hashes equaled their frozen official hashes.
- The complete nine-file directory was atomically promoted; no partial bundle
  qualified.
- Every metadata, payload, runtime, RSS, disk, thread, worker, and receipt cap
  passed.
- Every forbidden access and operation counter stayed zero.

This proves acquisition identity and mechanics only. No EDF content was decoded
or interpreted.

## Measurements

| Measurement | Observed | Registered cap or expectation |
|---|---:|---:|
| Input expected bytes | 23,248,224 | exactly 23,248,224 |
| Final output payload bytes | 23,248,224 | exactly 23,248,224 |
| Final files | 9 | exactly 9 |
| Metadata requests | 12 | 3 documents + 9 HEADs |
| Metadata response-body bytes | 442,178 | <= 1,048,576 |
| EDF payload requests | 9 | exactly 9 |
| EDF payload network bytes | 23,248,224 | <= 33,554,432 |
| Total measured response-body bytes | 23,690,402 | bounded by the two network caps |
| Opaque local hash passes | 9 | exactly 1 per EDF |
| Runtime | 50.682373 seconds | <= 300 seconds |
| Peak RSS | 55,181,312 bytes | <= 268,435,456 |
| Incremental disk peak | 28,327,635 bytes | <= 67,108,864 |
| Free disk before | 65,470,033,920 bytes | >= 2,147,483,648 |
| Free disk after | 65,443,667,968 bytes | reported, no minimum-after gate |
| Private receipt bytes | 16,083 | <= 1,048,576 combined |
| CPU threads / workers / numerical jobs | 1 / 1 / 1 | 1 / 1 / 1 |
| Payload retries / reruns | 0 / 0 | exactly 0 / 0 |
| End-to-end latency measured | no | unavailable |

Metadata bytes count response bodies, not transport headers, exactly as warned
in the private receipt.

## Zero Counters

Every one of these remained zero:

- EDF header reads;
- EDF annotation, event-channel, or `.event` sidecar reads;
- signal-sample reads;
- task, target, label, epoch, or trial reads;
- channel, montage, reference, geometry, sampling, or signal-quality reads;
- epoch, window, feature, cache, or split operations;
- model or checkpoint access;
- inference, training, parameter update, scoring, or selection runs;
- S20, SpanishBCBL, S7, S21, S24, S25, or other real-dataset operations;
- additional file, participant, run, companion, or substitution requests;
- language-model or provider operations;
- RW3, stream, device, or hardware operations;
- upload, publication, or release of payloads or private receipts; and
- work-order-9 operations.

## Receipt Binding

The two private generated files total 16,083 bytes:

| Private artifact | Bytes | SHA-256 |
|---|---:|---|
| Machine manifest | 10,141 | `5ebe954a07ced8c2d0c549af0e22c5246ff563613d56cd5e0d0b91fb305d3902` |
| Human receipt | 5,942 | `587d52cd69fa66e6c2dd195f396f91012205404e3a98139bc5f25e79e101e913` |

These hashes bind the local evidence without publishing the receipts or their
local paths. The acquired EDF bundle and both receipts remain Git-ignored.

## Post-Result Verification

Thirty-seven focused executor, implementation, and closeout tests pass. The
complete one-thread repository suite passes 1,455 tests with 3 expected skips
and 493 subtests in 50.76 seconds internal and 52.07 seconds external wall
time. Its 665,387,008-byte peak RSS includes the repository's optional ML
stack and is verification overhead, not the acquisition's measured
55,181,312-byte peak RSS.

Repository-wide Ruff, compileall, every registry JSON parse, and Git diff
hygiene pass before the sanitized closeout commit.

## Next Gate

Work order 8 is complete and consumed. It has no retry or rerun. Work order 9
remains separately gated and unauthorized; this result grants no EDF parsing,
annotation extraction, split, model, training, inference, scoring, or claim
permission by implication.

The maintainer's separate 10 GB allowance remains future headroom. This
invocation used only its immutable 23,248,224-byte payload scope and did not
expand into additional files.

## Claim Boundary

Engineering capability added: NeuroDecodeKit acquired and opaque-verified one
exact, isolated nine-file public EEGMMIDB bundle under the registered identity,
access-order, network, runtime, memory, storage, and no-retry controls.

Scientific claim not established: no EDF content was parsed and no event,
signal, target, model, or score was produced, so this result establishes no
motor-EEG effect, neural advantage, decoding accuracy, unseen-person
generalization, real-time latency, portable hardware, home use, assistive
value, or clinical utility.
