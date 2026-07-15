# Loop 26/31/33 Shared S21 Validation Authorization Decision

Date: 2026-07-15

Status: **Authorized after this record is tested, committed, pushed, and
remotely green; no implementation or protected execution exists yet**

Machine decision: `registries/loop26_authorization_decision.v0.json`

Frozen request: `registries/loop26_authorization_request.v0.json`

Frozen contract: `registries/loop26_shared_validation_contract.v0.json`

## Exact User Decision

The user supplied the registered sentence verbatim:

> Authorize the Loop 26/31/33 shared S21 validation implementation and one registered execution exactly as scoped in docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md and registries/loop26_shared_validation_contract.v0.json. I authorize one hash pass over the named monolithic S21 session-1 cache; opaque streaming traversal of its deflated row members; delivery of exactly 55 train signal/target rows and six validation signal rows into isolated derivatives; 21 bounded training runs, 24 target-blind model-inference runs, six train-only no-signal prior fits, 31 frozen prediction sets, and one conditional scoring delivery of the same six validation targets only after the prediction-freeze hash record is committed, pushed, and remotely green. I do not authorize delivery or scoring of the five source-test rows or session 2, raw FIF/MAT reads, S7/S20/S25, downloads, larger models, restarts, language models, RW3, streams, devices, hardware, post-target tuning, or any rerun after validation scoring.

This is one execution decision for the already frozen shared Loop 26/31/33
event. It is not a general data, model, hardware, or later-loop authorization.

## Bound Evidence

```text
authorization parent: 8572c14af005363cca08d4215a11a4d64455cac7
registration commit:  881145d865b1e25e3982b758c5fd2e519d16933b
contract SHA-256:      c4f94b214993973ec4b4ea7e7b27174023dfef227c8dd4d9b912ac48bb98ccce
request SHA-256:       ea975c148ba5e2da5d6c0bde8b310ec17ca2434f308ce9cbabf63139d9d1802b
```

The contract and request remain immutable snapshots. Their existing
`authorized_now` fields stay false. This separate decision becomes execution
authority only after its own pushed commit and both remote CI jobs are green.

## Authorized Scope

```text
bounded reader and synthetic isolation tests: authorized after green CI
source-cache hash passes:                    exactly 1
opaque deflated-member traversal:            authorized and measured
train derivative:                            55 signals plus targets
validation-input derivative:                 6 signals and no targets
candidate / linear parameters:               2,908 / 2,884
parameter-update runs / steps:               21 / 5,040
target-blind inference runs:                 24
train-only prior fits:                       6
prediction sets frozen:                      31
validation targets delivered:               6, once, after green freeze
validation scoring deliveries:              1
source-test or session-2 rows:               0
restarts / post-target reruns:               0 / 0
downloads:                                   0 bytes
```

Validation targets may not enter the prediction process. The six target rows
may reach only one isolated scorer after the hash-only prediction-freeze
record is committed, pushed, and remotely green.

## Required Order

1. Test this decision against the immutable request and contract.
2. Commit and push these authorization-only files.
3. Confirm both remote CI jobs are green.
4. Implement and synthetically test the bounded reader, causal model,
   controls, prediction freezer, and isolated scorer without real-cache access.
5. Commit, push, and remotely qualify that implementation.
6. Pass every static identity, archive, split, scaler, channel, environment,
   and resource gate.
7. Hash the source cache once and create only the 55-row train and six-row
   target-free validation-input derivatives.
8. Run all registered target-blind fits, priors, controls, inferences, and
   prediction sets.
9. Commit, push, and remotely qualify a hash-only prediction-freeze record.
10. Deliver the same six validation targets to one isolated scorer once.
11. Score every condition together and close or park without a rerun.

## Computer And Storage Boundary

```text
CPU threads / workers:                  1 / 1
candidate parameters:                  <= 2,908
parameter-update runtime:              <= 1,200 sec
end-to-end runtime:                    <= 1,500 sec
peak RSS:                              <= 1 GiB
working arrays:                        <= 128 MiB
checkpoints:                           <= 4 MiB total
prediction payloads:                   <= 2 MiB total
all generated experiment artifacts:   <= 32 MiB
downloads / external model weights:   0 / 0 bytes
```

Generated derivatives, checkpoints, and predictions must stay under
`.codex_work/loop26/`, which is Git-ignored. No operation may touch another
project.

## Authorization-Only Measurements

```text
source-cache stat / hash / member reads: 0 / 0 / 0
signal / target value reads:             0 / 0
train / validation rows delivered:       0 / 0
model / checkpoint / training runs:      0 / 0 / 0
parameter updates:                       0
prediction sets / scoring runs:          0 / 0
raw FIF/MAT / network / downloads:       0 / 0 / 0
generated experiment payload bytes:      0
end-to-end latency measured:              false
```

## Claim Boundary

**Engineering capability authorized for testing:** one hash-bound, bounded,
single-thread implementation and one registered same-person, same-session
validation event may proceed through its staged gates after this decision is
remotely green.

**Scientific or decoding claim not established:** this decision is not a
runtime result and establishes no neural advantage, sensor-signal dependence,
decoding accuracy, real-time operation, unseen-person transfer, EEG or
portable-device performance, assistive efficacy, or clinical capability.
