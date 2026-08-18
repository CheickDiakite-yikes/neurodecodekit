# MARC2-VR12P P15 Private Confirmation Implementation

Date: 2026-08-18

Lane: `MARC2-VR12P`

Status: generated Stage 1 implemented and qualified; private Stage 2 remains
proof-gated

## Green Authority

The implementation binds the exact authorization decision at commit
`b0f251a7fb1b69a0ed79f525ab100499e130390a`, CI run `32193964660`, Base
Python job `95894058802`, and Optional Neuro Readers job `95894058625`. It
also verifies the frozen request and the exact VR12A module, implementation
record, and result record before qualification or execution.

The decision authorizes two ordered stages. This record completes only Stage
1. The fixed private executor continues to refuse before readiness or any
private-path operation while `remote_implementation_proof` is null. Stage 2
does not become available until this exact implementation and a separate
proof-only closeout are committed, pushed, and green in both required jobs.

## Added Interface

`src/neurodecodekit/datasets/marc2_p15_private_confirmation.py` adds a
dependency-free wrapper with four fixed commands:

- `plan` reports the immutable lane and whether remote implementation proof is
  present;
- `qualify` runs only generated fixtures in invocation-created temporary
  roots;
- `inspect` reads only the future lane's aggregate report; and
- `execute` has no path or threshold override and refuses until exact remote
  proof is present.

The wrapper validates strict duplicate-free and finite JSON, one-thread
environment variables, three-sample readiness, no-follow source handling,
fresh output roots, marker-before-open ordering, exact source mode/size/hash,
one VR12A call, R1-only private manifest creation, aggregate-field privacy,
deterministic serialization, and resource caps. A consumed R2-R6 path writes
no private manifest and exposes only its aggregate route, operation counts,
resource measurements, warnings, unavailable fields, and claim boundary.

## Generated Qualification

The final recorded qualification ran three generated run-index spellings in
two source orders and two exact replays. Each path used a fresh temporary
fixed-path tree and exactly one VR12A adapter call.

```text
route:                              MARC2VR12P-G1
success paths:                      12 / 12
VR12A calls:                        12
generated source content opens:     12
direct refusal mutations:           61
selected generated subjects:        16
selected generated run bundles:     96
selected generated core members:    384
generated input bytes:               5,147,208
generated output bytes written:      2,613,227
peak incremental output bytes:       217,962
retained generated output bytes:     0
aggregate output bytes:              2,443
runtime seconds:                     0.6937790419906378
peak RSS bytes:                      37,142,528
CPU threads / workers / jobs:        1 / 1 / 1
network / new payload bytes:         0 / 0
real/private source operations:      0
archive / neural / target bytes:     0 / 0 / 0
model / training / prediction runs:  0 / 0 / 0
FW2 / CIL1 operations:               0 / 0
```

The cumulative generated write throughput is larger than one temporary
artifact, but cleanup occurs after every path. Peak incremental output was
217,962 bytes, below the frozen 2 MiB cap, and retained output was zero.

The generated semantic cohort digest was
`254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba`
in every order and replay.

## Failure Safety

The direct matrix covers 61 execution-envelope mutations across decision,
thread, readiness, fixed-path, source, marker, adapter, cohort, aggregate,
resource, and forbidden-operation boundaries. Additional tests cover strict
JSON failures, source mode drift, absent remote proof, output caps, public
field leakage, and a generated mock R3 sequence. The mock R3 sequence writes
only a mode-`0644` aggregate report after its consumed marker and creates no
private cohort manifest.

Twenty focused tests pass. The complete clean dependency-light suite passes
4,208 tests with 204 expected skips and zero failures, exactly 20 tests above
the 4,188-test pre-change decision baseline.

No generated qualification or unit test stats, resolves, hashes, opens, reads,
parses, or writes the registered repository-private source. Temporary fixtures
use isolated roots and are removed after each path.

## Remaining Gate

`remote_implementation_proof` is deliberately null. The next step is to commit
and push this implementation, obtain both green remote jobs, and commit a
proof-only closeout binding the immutable implementation bytes. Only after
that closeout is also remotely green may the one registered 418,755-byte
target-free structural confirmation run once. No retry or rerun is available.

Engineering capability added: a generated-qualified, proof-gated fixed-path
wrapper can safely freeze a target-free structural cohort or emit one
aggregate failure route without exposing private identities.

Scientific claim not established: Stage 1 accessed no real cohort, archive
member, neural signal, target, model, prediction, or score and establishes no
neural effect, decoding performance, language decoding, live decoding, or
thought-to-text capability.
