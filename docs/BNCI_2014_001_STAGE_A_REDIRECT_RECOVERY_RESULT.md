# BNCI-C3C5-1 Stage A Redirect-Recovery Result

Date: 2026-08-25

Status: **passed; exact opaque bundle acquired; invocation consumed; no retry
or rerun**

Machine result:
`registries/bnci_2014_001_stage_a_redirect_recovery_result.v0.json`

The private bundle, private manifest, consumed marker, and aggregate receipt
remain Git-ignored. They are not committed, uploaded, or reproduced here.

## Ordered Proof

The one live action began only after every predecessor was remotely green:

| Gate | Evidence |
|---|---|
| Recovery decision | `588dd70`, CI `32803138246` |
| Generated-qualified implementation | `09a19d1`, CI `32806186972` |
| Corrected activation | `492a36a`, CI `32807676008` |
| Current control plane | `21cedd5`, CI `32811586786` |
| Base / Optional jobs | `97691784130` / `97691784315`, passed |

The maintainer then explicitly approved the exact one-shot 18-file recovery
after its 779,873,919-byte transfer and irreversible-consumption risk were
restated. Earlier rejected launch requests did not create a process or consume
the invocation.

## Result

The registered recovery completed successfully:

- exactly 18 signed NEMAR objects were requested once each;
- exactly 779,873,919 payload bytes were accepted;
- every payload passed its registered byte-count and SHA-256 identity check;
- one complete isolated private bundle was created;
- the original 297-byte consumed marker remained byte-identical; and
- the recovery marker makes this invocation permanently consumed.

This proves source identity and bounded acquisition mechanics only. The MAT
files were not semantically opened or parsed.

## Measurements

| Measurement | Observed | Registered limit |
|---|---:|---:|
| Manifest input | 401,826 bytes | <= 1,048,576 |
| Payload files | 18 | exactly 18 |
| Payload requests | 18 | <= 54 |
| Accepted payload bytes | 779,873,919 | exactly 779,873,919 |
| Total network bytes | 780,275,745 | <= 2,685,403,136 |
| Output excluding marker/receipt | 779,876,862 bytes | <= 2,147,483,648 |
| Runtime | 113.066114 seconds | <= 1,800 seconds |
| Peak process RSS | 42,893,312 bytes | <= 1,073,741,824 |
| Free disk before | 92,905,000,960 bytes | >= 5,368,709,120 |
| Free disk after | 92,111,536,128 bytes | reported |
| CPU threads / workers / jobs | 1 / 1 / 1 | 1 / 1 / 1 |
| Aggregate receipt | 2,347 bytes | public-output cap preserved |
| End-to-end decoding latency | not measured | unavailable |

The private aggregate receipt is bound by SHA-256
`ac8c18238905112db5a80ddfb8cf37e4c4fcca1be5098f34dd034630ff347b22`
without publishing the receipt or its path.

## Zero Counters

Every one of these remained zero:

- MAT semantic opens and parses;
- signal, event, target, and label reads;
- model and training runs;
- prediction sets;
- target deliveries; and
- scientific scores.

No signed URL credential was retained. No payload, private manifest, or
private receipt was committed, uploaded, or released.

## Post-Result Verification

All 140 focused BNCI tests passed with five expected optional skips. The full
one-thread dependency-free suite passed all 6,066 tests with 217 expected skips
in 223.003 seconds. Ruff, compileall, all 484 registry JSON parses, and Git diff
hygiene also passed without reopening the private bundle.

## Next Gate

Stage A is complete and consumed. Commit, push, and remotely green this exact
aggregate result before Stage Q. Stage Q may then perform only the frozen
target-blind semantic validation. Stage P and Stage T remain closed behind
their ordered proof barriers.

## Claim Boundary

Engineering capability added: NeuroDecodeKit acquired and opaque-verified the
exact isolated 18-file BNCI-C3C5-1 bundle through validated signed objects
under the registered proof, identity, resource, and no-rerun controls.

Scientific claim not established: no MAT semantics, signal, event, target, or
label was read and no model, prediction, or score ran, so this acquisition
establishes no neural advantage, unseen-person generalization, decoding,
language, movement-intention, live, hardware, or clinical result.
