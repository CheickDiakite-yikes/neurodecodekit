# MARC2-VR16P Variable-Width Private Confirmation Implementation

Date: 2026-08-21

Lane: `MARC2-VR16P`

Status: **Generated Stage 1 implemented and qualified; private Stage 2 remains
proof-gated**

Machine record:
`registries/marc2_variable_width_private_confirmation_implementation.v0.json`

## Green Authority

The implementation binds authorization decision
`79d9b49c94063e68663d3774d6e6296961a544a6`, CI `32463248736`, Base
Python job `96714374482`, and Optional Neuro Readers job `96714374314`.
It also verifies the unchanged VR16A module and its remotely proven
implementation/result records before qualification or execution.

This record completes only Stage 1. `execute` refuses before readiness or any
private-path operation while `remote_implementation_proof` is null. Stage 2
does not become available until this exact implementation is committed,
pushed, green in both jobs, and a separate proof-only closeout is also
committed, pushed, and green.

## Added Interface

`src/neurodecodekit/datasets/marc2_variable_width_private_confirmation.py`
adds four fixed commands without a new dependency:

- `plan` reports the immutable gate and proof state;
- `qualify` uses only generated fixtures in invocation-created temporary
  roots;
- `inspect` reads only the future lane's aggregate report; and
- `execute` has no path, URL, output, width, threshold, retry, or substitution
  override and refuses until exact remote proof exists.

The wrapper validates duplicate-free finite JSON, one-thread settings,
three-sample readiness, no-follow source identity, fresh output roots,
marker-before-open order, exact source mode/size/hash, one VR16A call, R1-only
private manifest creation, deterministic serialization, aggregate privacy,
and all resource caps. It does not import or reference the consumed VR15P
executor.

## Generated Qualification

The registered qualification ran all six width variants in two source orders
and two exact replays. Each path used a fresh temporary fixed-path tree and
exactly one VR16A call.

```text
route:                              MARC2VR16P-G1
success paths:                      24 / 24
VR16A calls:                        24
generated source content opens:     24
direct refusal mutations:           71
selected generated subjects:        16
selected generated run bundles:     96
selected generated core members:    384
semantic cohort SHA-256:             254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba
generated input bytes:               10,606,656
generated output bytes written:      5,353,661
peak incremental output bytes:       241,813
aggregate report bytes:              2,456
retained generated output bytes:     0
runtime seconds:                     1.8574632920208387
peak RSS bytes:                      34,783,232
CPU threads / workers / jobs:        1 / 1 / 1
network / new payload bytes:         0 / 0
repository-private path operations:  0
archive / signal / target bytes:     0 / 0 / 0
model / training / prediction runs:  0 / 0 / 0
FW2 / CIL1 operations:               0 / 0
```

Cumulative generated writes exceed one artifact because each path creates and
deletes its own temporary state machine. Peak incremental output remained
241,813 bytes, below the 2 MiB cap, and retained output was zero.

## Failure Safety

The 71 direct mutations cover decision and implementation proof, all thread
settings, readiness, fixed paths, source identity, strict parse, marker order,
the variable-width grammar and canonical numeric identity, source-exact names
and reservation, companion completeness and collision refusal, selection,
cohort, aggregate privacy, resources, and every forbidden operation class.

Generated tests also exercise duplicate and non-finite JSON, source mode drift,
an absent remote proof, output caps, public-field leakage, deterministic
replay, and an aggregate-only mock R3 route. No generated test stats, resolves,
hashes, opens, reads, parses, or writes the registered `.codex_work` source.

## Remaining Gate

`remote_implementation_proof` is deliberately null. Commit and push this
implementation, require both jobs green, then create a proof-only closeout
binding the exact implementation bytes without repeating qualification or
performing a private operation. Only after that closeout is remotely green may
the registered 418,755-byte target-free structural confirmation run once.

Engineering capability added: a generated-qualified, proof-gated fixed-path
wrapper can safely freeze a target-free structural cohort or emit one
aggregate failure route without exposing private identities.

Scientific claim not established: Stage 1 accessed no real cohort, archive
member, neural signal, target, model, prediction, or score and establishes no
neural effect, decoding performance, language decoding, live decoding, or
thought-to-text capability.
