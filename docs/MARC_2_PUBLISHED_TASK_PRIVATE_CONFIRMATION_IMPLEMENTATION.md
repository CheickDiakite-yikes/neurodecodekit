# MARC2-VR20P Published-Task Private Confirmation Implementation

Date: 2026-08-22

Lane: `MARC2-VR20P`

Status: **Generated Stage 1 implemented and qualified; private Stage 2 remains
proof-gated**

Machine record:
`registries/marc2_published_task_private_confirmation_implementation.v0.json`

## Green Authority

Authorization decision `49b0f4b9b8ec13f885b0010947326fbd3b9641ac`
passed Base Python job `96991921763`, Optional Neuro Readers job
`96991921631`, and CI `32556695686` before implementation began. The wrapper
also verifies the unchanged VR20A module and its exact implementation and
result records.

This record completes Stage 1 only. `execute` refuses before readiness or any
private-path operation while `remote_implementation_proof` is null. Stage 2
does not become available until this exact implementation is committed,
pushed, green in both jobs, and a separate proof-only closeout is also
committed, pushed, and green.

## Added Interface

`src/neurodecodekit/datasets/marc2_published_task_private_confirmation.py`
adds four fixed commands without a new dependency:

- `plan` reports the immutable packet, route matrix, and proof state;
- `qualify` uses only generated fixtures in invocation-created temporary roots;
- `inspect` reads only the future lane's aggregate-safe report; and
- `execute` has no path, URL, output, task, run, threshold, retry, route, or
  substitution override and refuses until exact remote proof exists.

The wrapper validates duplicate-free finite JSON, one-thread settings,
three-sample readiness, no-follow source identity, fresh output roots,
marker-before-open order, exact mode/size/hash, one VR20A call, R1-only private
manifest creation, deterministic serialization, aggregate privacy, and every
resource cap. It does not import or call the consumed VR18P executor.

## Generated Qualification

The frozen matrix has one accepted VR20A source plus five aggregate refusal
groups. Each case ran in canonical and reversed source order across two exact
replays. Every path used a fresh temporary fixed-path tree and called unchanged
VR20A exactly once.

```text
route:                              MARC2VR20P-G1
generated paths:                    24 / 24
success / refusal paths:            4 / 20
G1 and R2-R6 route counts:          4 each
VR20A calls:                        24
generated source content opens:     24
direct refusal mutations:           91
selected generated subjects:        16
selected generated run bundles:     96
selected generated core members:    384
semantic cohort SHA-256:             254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba
generated input bytes:               10,602,864
generated output bytes written:      946,517
peak incremental output bytes:       222,998
aggregate report bytes:              2,610
retained generated output bytes:     0
runtime seconds:                     1.1980904169613495
peak RSS bytes:                      35,504,128
CPU threads / workers / jobs:        1 / 1 / 1
network / new payload bytes:         0 / 0
repository `.codex_work` operations: 0
archive / signal / target bytes:     0 / 0 / 0
model / training / prediction runs:  0 / 0 / 0
FW2 / CIL1 operations:               0 / 0
```

Cumulative generated writes include short-lived readiness, marker, private
fixture, and aggregate files across 24 temporary roots. Peak incremental
output remained 222,998 bytes, below the 2 MiB cap, and all generated output
was deleted by temporary-directory teardown.

## Failure Safety

The six-path matrix proves the exact aggregate map: adapter precondition to
R2, source envelope to R3, task/identity/companion to R4,
taxonomy/selection/split to R5, and privacy/resource/unknown to R6. It retains
no upstream reason or private value.

The 91 direct mutations cover decision and implementation proof, all thread
settings, readiness, fixed paths, source identity, strict parsing, marker
order, exact published task, numeric run semantics, source-exact names and
reservation, companion completeness and collision refusal, split/cohort
arithmetic, public/private output separation, resources, and every forbidden
operation class. Generated tests also cover symlink and mode drift, missing
remote proof, output caps, leakage, replay, and aggregate-only failure output.

No test stats, resolves, hashes, opens, reads, parses, or writes the registered
`.codex_work` source or consumed VR18P state.

## Remaining Gate

`remote_implementation_proof` is deliberately null. Commit and push this
implementation, require both jobs green, then create a proof-only closeout
binding the exact implementation bytes without repeating qualification or
performing a private operation. Only after that closeout is remotely green may
the registered 418,755-byte target-free structural confirmation run once.

Engineering capability added: a generated-qualified, proof-gated fixed-path
wrapper can freeze a target-free published-task structural cohort or emit one
aggregate blocker route without exposing private identity.

Scientific claim not established: Stage 1 accessed no real cohort, archive
member, neural signal, target, model, prediction, or score and establishes no
neural effect, decoding performance, language decoding, unseen-person
generalization, live decoding, or thought-to-text capability.
