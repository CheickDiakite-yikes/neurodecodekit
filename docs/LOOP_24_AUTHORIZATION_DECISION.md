# Loop 24 Authorization Decision

Date: 2026-07-12

Status: **Authorized after this record is tested, committed, and pushed; no
implementation or runtime exists yet**

Machine decision: `registries/loop24_authorization_decision.v0.json`

Frozen contract: `registries/local_precision_runtime_contract.v0.json`

## User Decision

The user explicitly authorized Loop 24 and also mentioned real data and
training:

> lets conitune, you have autorization for loop 24 real data / training. we'll
> have to use good available dataor try to create some great ones, since we dont
> have eeg yet.

This is an explicit Loop 24 authorization intent, but it is broader than the
frozen Loop 24 contract. The contract was deliberately preregistered as a
target-free synthetic precision/runtime experiment with no training. Adding
real data or parameter updates now would invalidate its fresh partitions,
access counters, resource comparison, and scientific interpretation.

The decision is therefore recorded as a conservative scope amendment:

```text
Loop 24 target-free implementation: authorized
seed-2401 fixture generation:       authorized after this commit is pushed
frozen checkpoint open/validation: authorized after this commit is pushed
candidate conversion/inference:    authorized after this commit is pushed
registered selection:              authorized after this commit is pushed
conditional seed-2402 qualification: authorized after selection freeze
real or consumed data access:      not authorized under Loop 24
target/label/text access:           not authorized under Loop 24
training or parameter updates:     not authorized under Loop 24
new architecture or larger model:  not authorized under Loop 24
energy measurement:                not authorized for this execution
RW3, sockets, devices, hardware:   not authorized
```

The user's real-data and training ambition is preserved rather than discarded:
Loop 25 is the causal-preprocessing gate, Loop 26 is the fixed small real
validation-only encoder gate, and Loop 27 is the metadata-only fresh-holdout
search. Each needs its own frozen inputs, controls, byte/resource caps, and
authorization before execution.

## Existing EEG Boundary

The repository does have one selectively downloaded S7 SpanishBCBL EEG
BrainVision recording. Its trigger/cache mechanics are validated, but its first
nearest-centroid classifier performed worse than a no-signal prior. That
evaluation is consumed. It is not a fresh EEG benchmark, a useful EEG decoder,
an at-home device result, or permission to tune on S7 again.

No additional EEG is downloaded by this decision. Loop 27 can later research a
fresh task-matched cohort using metadata only; any acquisition still requires
an exact revision, file list, byte cap, dry run, license check, split, and user
approval.

## Bound Contract

```text
contract ID:       loop24-local-precision-runtime-v0
schema version:    0.1.0
preregistered at:  186bb6f
authorization parent: 4050b8590507e079eccb961668706eaa0ae6f228
contract SHA-256:  58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d
contract Git blob: 7ac75c8191908b7ab439fd96098027c12ccf5152
```

The preregistration contract remains an immutable snapshot with false
authorization fields. The separate decision file is the current execution
authority. This preserves the pre-result contract hash instead of rewriting
history after authorization.

## Authorized Work

Only the planned Loop 24 surface may be added:

```text
src/neurodecodekit/training/precision_runtime_fixture.py
src/neurodecodekit/models/precision_candidates.py
src/neurodecodekit/experiments/local_precision_runtime_gate.py
tests/test_precision_runtime_fixture.py
tests/test_precision_candidates.py
tests/test_local_precision_runtime_gate.py
docs/LOOP_24_LOCAL_PRECISION_RUNTIME.md
```

Planned commands:

```text
neurodecode make-precision-runtime-fixture
neurodecode inspect-precision-runtime-fixture
neurodecode local-precision-runtime-gate
neurodecode inspect-local-precision-runtime-report
```

The implementation may use only the existing optional NumPy/PyTorch
environment. It may not add a new base or optional dependency.

## Execution Order

1. Test this decision and every existing Loop 24/RW3 invariant.
2. Commit and push authorization-only changes with no implementation.
3. Confirm the pushed commit and CI before creating a fixture or opening the
   checkpoint.
4. Implement and unit-test mechanics with tiny generated fakes.
5. Generate seed 2401 target-free selection data under the frozen caps.
6. Run correctness and the 12 balanced timing rounds, then freeze the candidate
   decision.
7. Open seed 2402 once only if a nonreference replacement candidate qualifies.
8. Close with replacement, storage-only, retain-float32, park, or kill.

## Resource Boundary

```text
numerical threads / workers:        1 / 1
total generated artifacts:          <= 4 MiB
materialized arrays:                <= 32 MiB
internal runtime per worker:        <= 60 sec
peak RSS per worker:                <= 1 GiB
network/data/target/training/RW3:    0
energy measurement:                 unavailable and not authorized
```

Lower limits in the frozen contract continue to win.

## Authorization-Only Measurements

```text
fixture bytes generated:             0
checkpoint reads:                    0
candidate conversions:              0
model inference runs:                0
training runs / parameter updates:   0 / 0
raw / real-cache / consumed reads:   0 / 0 / 0
target / label / text reads:         0 / 0 / 0
network / stream / board operations: 0 / 0 / 0
generated runtime payload bytes:     0
producer causal status:              unchanged from frozen contract
end-to-end latency measured:         false
```

## Claim Boundary

**Engineering capability authorized for testing:** compare correctness,
numerical drift, storage, memory, and one-thread CPU runtime for the three exact
frozen execution candidates around one target-free synthetic causal pipeline.

**Scientific or decoding claim not established:** this authorization is not a
runtime result and does not establish neural information, real-data accuracy,
better CER/WER, unseen-person transfer, end-to-end latency, useful EEG,
portable hardware, at-home thought typing, arbitrary-thought decoding,
assistive efficacy, or clinical utility.
