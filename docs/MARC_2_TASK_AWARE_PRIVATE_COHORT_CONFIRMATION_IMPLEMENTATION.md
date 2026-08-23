# MARC2-VR36P Task-Aware Private Cohort Confirmation Implementation

Date: 2026-08-23

Lane: `MARC2-VR36P`

Status: **Generated Stage 1 qualified once; exact implementation remote proof
pending**

Machine records:

- `registries/marc2_task_aware_private_cohort_confirmation_implementation.v0.json`
- `registries/marc2_task_aware_private_cohort_confirmation_result.v0.json`

## Decision Proof

Packet-bound authorization decision
`fd08dd6ee40b16d3b4f4312601fed3370b7e2ca5` passed:

```text
CI run:                 32648347577
Base Python job:        97215989173
Optional Neuro job:     97215989332
both required jobs:     green
```

Only then did Stage 1 implementation and generated qualification begin.

## Independent Fixed-Path Wrapper

The new standard-library module is
`neurodecodekit.datasets.marc2_task_aware_private_cohort_confirmation`. It
does not import, call, patch, or inspect a consumed private executor. It calls
only unchanged generated/readiness interface VR33A and generated task-aware
selection interface VR35A.

The CLI exposes only:

```text
plan
qualify
inspect
execute
```

There is no generic path, output, URL, task, count, threshold, rank, cap,
route, interval, retry, or resource override. `execute` and `inspect` check the
remote implementation proof before consulting a fixed private path.

The wrapper adds strict duplicate-key and non-finite JSON refusal, no-follow
source open, inode/device/size/mode/content binding, exclusive mode-preserving
output writes, output caps, public-field firewalling, fixed one-thread checks,
and one-use marker semantics. Generated cohort files are temporary and contain
the exact selector-produced 16-subject, 96-bundle, 384-row structure only on
VR35A G1/G2.

## Sole Generated Qualification

One qualification invocation covered five VR35A cases, two readiness states,
two row orders, and two exact replays:

```text
paths:                         40
VR33A calls:                   40
readiness provider calls:     120
readiness sleeper calls:       80
ready source constructions:    20
generated source opens:        20
VR35A calls:                   20
generated cohort writes:        8
direct refusals:              111
source mutations:               0
retained output bytes:           0
```

Every mapped R1-R5 route appeared four times and R6 appeared twenty times.
Every upstream VR35A G1/G2/R1/R2/R3 route appeared four times. Not-ready paths
constructed no source and called VR35A zero times. The two replay signatures
matched exactly.

Measured resources:

```text
fixed tracked input:        211,512 bytes
generated input:          8,847,228 bytes
generated output written: 1,801,084 bytes (temporary, cumulative)
peak incremental output:    221,058 bytes
aggregate report:             3,521 bytes
runtime:                1.785233375034295 seconds
peak RSS:                  35,340,288 bytes
CPU / workers / jobs:       1 / 1 / 1
network / new payload:      0 / 0 bytes
raw/private/model/training: 0 / 0 / 0 / 0 runs or reads
```

The qualification may not be repeated.

## Proof Gate

The implementation registry deliberately has `remote_implementation_proof`
set to `null`. The fixed `execute` and `inspect` commands therefore refuse at
`MARC2VR36P-F02` before readiness, `.codex_work`, source, output-root, or
consumed-state access.

Commit, push, and green the exact implementation and generated result. Then
add a proof-only closeout that binds the exact green commit without repeating
qualification or touching private state. Only after that closeout is itself
remotely green may the one registered target-free private invocation run.

Engineering capability added: a deterministic task-aware fixed-path state
machine now proves readiness gating, source isolation, route mapping, and
conditional cohort serialization entirely on generated fixtures.

Scientific claim not established: Stage 1 opened no private structural source,
archive member, neural signal, target, model, prediction, or score and proves
no neural effect, decoding performance, language decoding, unseen-person
generalization, or live decoding.
