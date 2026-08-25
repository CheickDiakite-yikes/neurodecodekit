# BNCI-C3C5-1 Stage Q Result

Date: 2026-08-25

Status: **passed; real MAT semantics validated; target-firewalled derivatives
created; invocation consumed; no retry or rerun**

Machine result: `registries/bnci_2014_001_stage_q_result.v0.json`

The real payload, private manifest, consumed marker, derivatives, aggregate
receipt, target envelopes, and scoring keys remain Git-ignored. No participant
identifier, participant-level outcome, target, private path, derivative hash,
or key is committed or reproduced here.

## Ordered Proof

The one semantic execution began only after every predecessor was remotely
green:

| Gate | Evidence |
|---|---|
| Stage A result | `96d7f0`, CI `32814564120` |
| Runtime implementation | `e5ca6a2`, CI `32822604745` |
| Shallow-checkout compatibility | `52b681e`, CI `32824921855` |
| Final activation | `0e36993`, CI `32825946085` |
| Activation Base / Optional jobs | `97733856845` / `97733856470`, passed |

The first activation proof `e678095` failed before execution because two tests
required ancestor objects unavailable in the shallow Actions checkout. It had
no effect and performed no private operation. The maintainer then explicitly
approved the one-shot semantic analysis after its real MAT access, derivative
creation, and irreversible-consumption risk were restated.

## Result

The registered Stage Q execution completed successfully:

- all 18 acquired MAT files opened and parsed exactly once;
- 108 task runs and 5,184 trials passed the frozen semantic inventory;
- the payload exposed 22 EEG and 3 EOG channels sampled at 250 Hz;
- nine held-out-participant folds were constructed;
- each fold references 4,608 source rows and 288 sealed held-out-E rows;
- no held-out-T row entered any fold capability;
- one-copy target-free signal derivatives were created;
- source labels stayed fold-scoped; and
- held-out targets and scoring keys stayed outside model capabilities.

Payload geometry is unavailable. Artifact flags and availability are sealed and
cannot be used for primary exclusion. The first trial's previous-interval
feature uses the preregistered exact-zero sentinel.

## Measurements

| Measurement | Observed | Registered limit |
|---|---:|---:|
| Real input payload | 779,873,919 bytes | exact acquired bundle |
| MAT content opens / parses | 18 / 18 | 18 / 18 |
| Private derivative output | 72,666,213 bytes | <= 536,870,912 |
| Private aggregate receipt | 2,230 bytes | public cap preserved |
| Runtime | 34.464444 seconds | <= 3,600 seconds |
| Peak process RSS | 910,704,640 bytes | <= 1,073,741,824 |
| Free disk before | 92,395,732,992 bytes | >= 2 GiB plus layout bound |
| Free disk after | 92,320,219,136 bytes | reported |
| CPU threads / workers / jobs | 1 / 1 / 1 | 1 / 1 / 1 |
| Analysis network | 0 bytes | 0 bytes |
| End-to-end decoding latency | not measured | unavailable |

The 72.7 MB derivative is well below both the conservative 227,843,968-byte
layout preflight and the 512 MiB hard cap. Peak RSS remained about 163 MB below
the 1 GiB limit.

## Zero Counters

Every one of these remained zero:

- calibration signal runs read;
- model and training runs;
- prediction sets;
- target deliveries;
- scientific scores; and
- analysis network bytes.

Stage Q isolated 108 target vectors into sealed envelopes but delivered none to
a model or scorer. It produced no accuracy, no no-signal comparison, and no
participant-level scientific outcome.

## Verification

The 52 focused Stage Q tests passed in both numerical and dependency-free
environments, with 10 expected optional skips in the latter. The complete local
discovery run executed 6,166 tests in 343.636 seconds: 6,144 passed, 17 skipped,
and five tests from five legacy modules hit known accumulated-process RSS,
timing, or sandbox-forkserver limits. Those exact five modules then passed all
62 tests in a fresh unsandboxed one-thread process in 22.388 seconds.

Ruff, compileall, Stage Q CLI help, all 488 registry JSON parses, and Git diff
hygiene passed. No verification step reopened a private payload or derivative.

## Next Gate

Stage Q is complete and consumed. Commit, push, and remotely green this exact
aggregate result before Stage P. Stage P remains closed until then, and Stage T
remains closed until a later frozen prediction record is committed, pushed,
and remotely green.

## Claim Boundary

Engineering capability added: NeuroDecodeKit semantically validated the exact
real 18-file BNCI bundle and created bounded target-firewalled nine-fold
derivatives with held-out targets and scoring keys isolated from model
capabilities.

Scientific claim not established: no model training, prediction, target
delivery, or score ran, so Stage Q establishes no neural advantage,
EEG-beyond-EOG effect, unseen-person generalization, decoding accuracy,
language, movement-intention, live, hardware, or clinical result.
