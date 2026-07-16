# Loop 48 Stage B Train-Only Failure-Discrimination Authorization Decision

Date: 2026-07-15

Status: **Authorized after this record is tested, committed, pushed, and
remotely green; no implementation or protected execution exists yet**

Machine decision: `registries/loop48_stage_b_authorization_decision.v0.json`

Frozen request: `registries/loop48_stage_b_authorization_request.v0.json`

Frozen contract: `registries/loop48_train_only_discrimination_contract.v0.json`

## Exact User Decision

The maintainer supplied the registered sentence verbatim:

> Authorize the Loop 48 Stage B train-only failure-discrimination implementation and one registered execution exactly as scoped in docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md and registries/loop48_train_only_discrimination_contract.v0.json. I authorize one SHA-256 pass over the named 10,632,576-byte S21 session-1 sentence cache; target-free reading of the bound split metadata; opaque sequential traversal of its deflated members; delivery of exactly 44 source-train signal/target rows and 11 source-train check signal rows into isolated derivatives; 20 bounded parameter-update runs, 35 target-blind model-inference runs, five train-only no-signal prior fits, 41 frozen prediction sets, and one conditional delivery and scoring of the same 11 source-train check targets only after the hash-only prediction-freeze record is committed, pushed, and remotely green. I authorize no validation or source-test row delivery or scoring, session 2, S7/S20/S25, raw FIF/MAT reads, new downloads, larger or additional models, restarts, language models, NeuroTokens, RW3, streams, devices, hardware, post-check tuning, claim upgrade beyond the registered E2 diagnostic ceiling, or rerun after check scoring.

This is one exact Tier C decision for the already frozen Stage B protocol. It
does not authorize another run, a wider cohort, a larger model, or any later
loop.

## Bound Evidence

```text
authorization parent: 54bbbdf6d052b4f273db13819e6dac77c29c4ba3
registration commit:  0ee0ab7cd3abae4ce654af9954854a6e236c8a0e
request commit:       1de3fa351f77e8784cf88da1da0217142d10781d
contract SHA-256:     009e320ea4df17e9f6fa58f74053b2ab70cce73eb0a9eea3cefc5b7b14112a9a
request SHA-256:      c23030f655fd662128dbc70f879a7a7a7d062f861ec279779b53852521d08c38
charter push CI:      29458883131
charter PR CI:        29458896919
```

The preregistration, contract, packet, request, and their historical invariant
tests remain immutable snapshots. Their `authorized_now` fields remain false
because this separate record captures the later decision.

## Exact Authorized Inventory

```text
source-cache SHA-256 passes:                     1
target-free split metadata reads:                registered only
fit signal / target rows:                        44 / 44
pre-freeze check signal / target rows:            11 / 0
parameter-update runs / optimizer steps:          20 / 4,800
target-blind model-inference runs:                 35
train-only no-signal prior fits:                    5
frozen prediction sets:                            41
post-green-freeze check targets:                   11 once
check scoring events:                               1
validation / source-test / session-2 rows:          0 / 0 / 0
new downloads:                                      0 bytes
post-check tuning / reruns:                         0 / 0
```

Only the 2,908-parameter causal candidate and 2,884-parameter linear comparator
are allowed. Seeds remain `4801`, `4802`, and `4803`, with no best-seed
selection, restart, early stopping, or architecture change.

## Required Order

1. Test this decision against the immutable request and contract.
2. Commit, push, and obtain green CI for this authorization-only record.
3. Implement the bounded reader, isolation, training, controls, freezer, and
   scorer using synthetic-only tests without protected access.
4. Commit, push, and obtain green CI for the implementation.
5. Bind target-free identities and resources, then perform the single cache
   SHA-256 pass and create the exact 44-row fit and 11-row check-input
   derivatives.
6. Run the static audit, 20 fits, 35 target-blind inferences, five priors, and
   freeze 41 prediction sets.
7. Commit and push the plaintext-free prediction-freeze record and obtain green
   CI.
8. Deliver the same 11 check targets once to the isolated scorer, emit all six
   hypothesis outcomes together, mark the protocol consumed, and stop.

No protected path stat, hash, archive traversal, signal, target, model, or
derivative operation may happen before its registered green gate.

## Computer And Storage Boundary

```text
CPU threads / workers / numerical jobs: 1 / 1 / 1
parameter-update runtime:              <= 600 seconds
end-to-end runtime:                    <= 900 seconds
peak RSS:                              <= 1 GiB
working arrays:                        <= 128 MiB
checkpoints / private predictions:     <= 4 MiB / 4 MiB
all generated artifacts:              <= 32 MiB
minimum free disk:                     >= 20 GiB
network / downloads:                   0 / 0 bytes
```

## Authorization-Only Measurements

```text
source-cache stat/hash/member reads:                    0 / 0 / 0
split metadata / signal / target reads:                 0 / 0 / 0
fit/check/validation/test/session-2 row deliveries:     0 / 0 / 0 / 0 / 0
model inference / training / parameter updates:         0 / 0 / 0
prediction sets / check scoring:                        0 / 0
downloads / stream / device / hardware operations:     0 / 0 / 0 / 0
generated experiment artifacts:                        0
end-to-end latency measured:                            false
```

## Claim Boundary

**Engineering capability authorized for testing:** one hash-bound,
resource-bounded Stage B implementation and one registered train-only
failure-discrimination execution may proceed through the ordered green gates.

**Scientific claim not established:** this decision is not a runtime result.
Even a later clean Stage B result is capped at E2 pipeline-discriminative
evidence and cannot establish independent validation, neural advantage,
brain-specific origin, useful decoding, unseen-person generalization, causal
preprocessing, real-time behavior, EEG or portable-device performance,
assistive value, diagnostic value, or clinical utility.
