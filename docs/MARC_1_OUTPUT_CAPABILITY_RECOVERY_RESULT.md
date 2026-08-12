# MARC-1 Output-Capability Recovery Result

Date: 2026-08-12

Lane: `MARC1-OP1`

Status: **Passed and consumed at `MARC1OP-G1`; no retry or rerun remains**

Machine result:
`registries/marc1_output_capability_recovery_result.v0.json`

## Result In One Line

The one registered path-only preflight reached `MARC1OP-P0`, then the one
conditional generated qualifier reached `MARC1OP-G1`, proved capability-first
ordering and unchanged pagination/selection mechanics, and removed every
temporary output.

This is a successful engineering gate on the same thought-to-text research
path. It is not a pivot and it is not new neural evidence.

## Green Implementation Anchor

Exact implementation commit
`fcedcc308c1038c765605571c19ba24eb4f7603f` passed:

```text
CI run:                 31600085119
Base Python job:        94125013790
Optional Neuro job:    94125013956
```

Both jobs were green before the registered output path was touched.

Bound implementation artifacts:

```text
implementation registry SHA-256: d2ea78bd173ab290b6f5eb56e67f8ed73d324ecdaae1fdee8fea4852f801506c
implementation source SHA-256:   40a2d8520102b6502fcad82e1f262613a647335bbad92ef1529204bb5a9166b4
behavior test SHA-256:            946ae88d3d8467d125a955022ba517f6725702429a00240e1bf031110eee475f
contract SHA-256:                 2fe17a263a8c923c2a7af76dbba0c6422eacb601b7668de987ef0d53485c5cb6
```

## Registered Sequence

The exact registered destination was:

`/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812`

No substituted path was used.

### 1. Path-Only Preflight

The one preflight acquired and released the output capability and returned:

```text
route:                         MARC1OP-P0
capability acquisitions:       1
repository reads:              0
contract loads:                0
deferred imports:              0
fixtures constructed:          0
rows constructed:              0
selections run:                0
output files / bytes:          0 / 0
network bytes:                 0
real/private input bytes:      0
external wall time:            0.10 seconds
external maximum RSS:          25,280,512 bytes
```

Because and only because it returned `MARC1OP-P0`, the conditional qualifier
was opened.

### 2. Generated Qualifier

The one qualifier returned:

```text
route:                         MARC1OP-G1
accepted cases:                6 / 6
refusal mutations:             32 / 32
acceptance gates:              20 / 20
generated input bytes:         1,019,776
public report bytes:           8,499
private manifest bytes:        175,674
combined output/disk bytes:    184,173
reported runtime:              0.09794287499971688 seconds
external wall time:            0.24 seconds
reported peak RSS:             33,882,112 bytes
external maximum RSS:          33,914,880 bytes
public report SHA-256:          15e822309d89aafdeda06a89ffa8e6430d45abb2388bd17aeee0fac78376c711
private manifest SHA-256:       e835e41a2494268c7795ca72e2e6ef9f01d0494767c9c70b4e76c382c6e609b4
output removed before return:   yes
```

The public hash differs from the fixed-measurement development hash because
runtime and RSS are measured fields. The private manifest hash is identical to
development replay.

## What Passed

The frozen mechanics all held:

1. Capability acquisition was the first call in both registered operations.
2. All seven experiment-work counters were zero at capability acquisition.
3. Every output ancestor was a real no-follow directory.
4. The held parent device, inode, and type matched before work and writing.
5. Output absence passed at acquisition and immediately before creation.
6. All 19 pre-capability and 13 post-capability mutations refused correctly.
7. The four generated response forms shared semantic and selection hashes.
8. Exact 55-row, 45-participant, and ten-supplement identity held.
9. Exact target-free 12+12 selection and zero-overlap split identity held.
10. The consumed qualifier was never called and its source stayed unchanged.
11. Exactly two files were written parent-relatively and exclusively.
12. Only the aggregate public file was inspected.
13. Public and private replay, resource caps, and zero-access gates passed.
14. Both files and the output directory were removed before return.

## Access Ledger

The generated qualifier's aggregate public ledger recorded:

```text
capability acquisitions/revalidations:  1 / 1
bound repository reads:                 10
contract loads:                          2
deferred pagination imports:             1
generated fixtures/rows:                 2 / 1,282
selection runs:                           4
output directories/files:                1 / 2
output bytes allocated:                   184,173
public/private inspections:               1 / 0
cleanup file/directory removals:           2 / 1
```

Dataset-specific requests and response bytes, private real-manifest access,
consumed-root operations, payload requests and bytes, signal reads, target or
label reads, model runs, training runs, prediction sets, scoring events,
provider calls, hardware operations, other-project operations, retries,
reruns, and claim upgrades were all zero.

## Consumption And Next Gate

Both registered invocations are consumed. There is no second preflight,
qualifier, corrected path, retry, rerun, resume, substitution, or amendment.

After this result is committed, pushed, and both CI jobs are green, Tier A may
prepare one all-false Tier C request for a future bounded live metadata
response. The request itself may not contact Figshare. Any live response still
requires a separate packet-bound maintainer decision after the request is
remotely green.

Payload acquisition, private source input, neural data, targets, models,
training, prediction, scoring, language-model use, devices, hardware, release,
and claim upgrades remain closed.

## Warnings And Unavailable Fields

- All pagination, cohort, and split values used here were generated locally.
- Current live Figshare inventory compatibility remains unknown.
- No real Freewill or Wrist participant was selected by this run.
- Neural signal, target, model prediction, scientific score, and end-to-end
  latency are unavailable.
- Passing this result proves process mechanics, not scientific validity.

## Verification

```text
focused result tests:                 12 / 12
all MARC tests:                      599 / 599
MARC runtime / external peak RSS:    6.500 sec / 67,502,080 bytes
dependency-light suite:              2,738 passed / 204 skipped
dependency-light runtime / peak RSS: 22.533 sec / 245,284,864 bytes
optional-neuro suite:                2,809 passed / 35 skipped
optional-neuro runtime / peak RSS:   60.996 sec / 731,545,600 bytes
```

The result adds twelve tests and zero skips. Repository-wide Ruff, source and
test compilation, all 192 registry JSON parses, artifact hash replay, and
`git diff --check` pass. Verification did not rerun either registered
operation or access a live/private source.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has a remotely qualified
capability-first path exercised under registered controls that safely composes
generated pagination and cohort selection, writes only through held
descriptors, exposes only aggregate output, and cleans up exactly.

Scientific claim not established: no live dataset body, neural signal, target,
model prediction, score, language decoding, or thought-to-text result was
produced.
