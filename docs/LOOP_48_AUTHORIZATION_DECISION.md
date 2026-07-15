# Loop 48 Artifact-Only Failure Localization Authorization Decision

Date: 2026-07-15

Status: **Authorized after this record is tested, committed, pushed, and
remotely green; no implementation or Stage A execution exists yet**

Machine decision: `registries/loop48_authorization_decision.v0.json`

Frozen request: `registries/loop48_authorization_request.v0.json`

Frozen contract: `registries/loop48_failure_localization_contract.v0.json`

## Exact User Decision

The user supplied the registered sentence verbatim:

> Authorize the Loop 48 artifact-only failure-localization implementation and one Stage A execution exactly as scoped in docs/LOOP_48_PRIMARY_SOURCE_RESEARCH.md and registries/loop48_failure_localization_contract.v0.json. I authorize reading and SHA-256 verification of only the four committed JSON artifacts named by that contract; recomputation of the frozen aggregate blank/CER summaries and six fixed-prefix seed-dispersion checks; application of the ordered eight-class decision tree; and emission of one aggregate target-free JSON report under one CPU thread, one worker, 30 seconds, 256 MiB peak RSS, and 1 MiB generated output. I do not authorize any Git-ignored Loop 26 output, cache/member, train/validation array, target, checkpoint, private prediction, source-test/session-2, S7/S20/S25, raw FIF/MAT, model inference, training, parameter update, threshold/seed/architecture selection, download, language model, RW3, stream, device, hardware, scientific claim upgrade, or rerun.

This is one execution decision for the already frozen artifact-only Stage A.
It is not general data, model, hardware, rerun, or later-loop authorization.

## Bound Evidence

```text
authorization parent: 8c96c7f009d9f3b5b5d93178f3f7e43771bdce61
request commit:       0ffdf47384a35a09e61158921711b033fd62707d
registration commit:  83309bfc29300c542c7a7a6dc0f193baba28d42e
contract SHA-256:      ecd226f8ae8892e40ecd65c25d59e000384289e9c434886db71dabcfde9e31b1
request SHA-256:       799e5c09c6b5dddf555c19a06f8bf1ce3734246218e4323dffb816b47af813f8
```

The contract, request, and research note remain immutable snapshots. The
request's historical invariant-test blob also remains hash-bound in Git
history; the live test transitions only so the repository can represent the
subsequent decision without rewriting those frozen artifacts.

## Authorized Scope

```text
dependency-light analyzer:                  authorized after green CI
committed JSON inputs:                      exactly 4 / 155,545 bytes
input path, byte, and SHA-256 verification: required
aggregate blank/CER summaries:              recompute once
fixed-prefix seed-dispersion groups:         exactly 6
ordered failure classes:                    exactly 8
aggregate target-free reports:              exactly 1
model inference / training / updates:        0 / 0 / 0
target or protected-cache reads:             0
downloads / network calls:                  0 / 0
reruns:                                      0
```

The implementation and its synthetic isolation tests may not read any of the
four registered inputs. Those inputs may open once only after the separate
implementation commit is pushed and both remote CI jobs are green.

## Required Order

1. Test this decision against the immutable request and contract.
2. Commit and push these authorization-only files.
3. Confirm the pushed authorization commit and both CI jobs are green.
4. Implement and synthetically test the dependency-light analyzer without
   reading any registered input.
5. Commit, push, and remotely qualify that implementation.
6. Execute Stage A once over only the four exact committed JSON inputs.
7. Validate one aggregate report, record access and resources, then close or
   park without rerunning or tuning.

## Computer And Storage Boundary

```text
CPU threads / workers:       1 / 1
runtime:                     <= 30 seconds
peak RSS:                    <= 256 MiB
generated output:            <= 1 MiB
network / downloads:         0 / 0 bytes
other project operations:    0
```

## Authorization-Only Measurements

```text
registered artifact reads:                 0
generated diagnostic reports:              0
cache/member/array/target reads:            0
checkpoint/private-prediction reads:        0
model inference / training / updates:       0 / 0 / 0
network calls / downloaded bytes:           0 / 0
RW3/stream/device/hardware operations:      0
generated experiment payload bytes:         0
end-to-end latency measured:                 false
```

## Claim Boundary

**Engineering capability authorized for testing:** one hash-bound,
dependency-light analyzer and one aggregate-only Stage A execution may proceed
through the staged green gates.

**Scientific or decoding claim not established:** this decision is not a
runtime result and establishes no causal root cause, independent evidence,
neural advantage, sensor-signal dependence, brain-specific origin, decoding
improvement, unseen-person generalization, real-time behavior, EEG or portable
device performance, assistive efficacy, diagnostic value, or clinical
capability.
