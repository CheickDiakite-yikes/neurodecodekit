# MARC-1 Source-Aware Inventory Attestation Implementation

Date: 2026-08-12

Lane: `MARC1-SA1`

Status: **Generated-only implementation candidate; no registered closeout,
network, dataset-specific body, private path, archive, payload, signal, target,
model, prediction, or score is authorized before this exact implementation is
remotely green**

Machine record:
`registries/marc1_source_aware_inventory_attestation_implementation.v0.json`

## Eligibility

Implementation began only after contract commit
`8f64ccb6dd33df8c81382a9dafd2e84590f50061` passed Base Python job
`94180673330` and Optional Neuro Readers job `94180673125` in CI
`31616551270`.

The implementation binds contract SHA-256
`7c405520a3c2039d8ff202f8e34f228627b5b2f5b97cd74e2fe9b42b83de8bec`
and verifies the green research and consumed aggregate result chain before
building a fixture.

## Added Interface

The new dependency-free module is:

```text
src/neurodecodekit/datasets/marc1_source_aware_inventory_attestation.py
```

Its command surface is exactly:

```text
plan
qualify --output-dir ABSENT_TEMP_PATH
inspect PUBLIC_REPORT
```

There is no `execute` command, URL opener, network library, dataset endpoint,
registered or consumed path, participant-archive reader, payload reader,
signal or target interface, model, training, prediction, or scorer.

## Source-Aware Semantics

The parser requires the five-field public core:

```text
id
name
size
is_link_only
download_url
```

`supplied_md5` and `computed_md5` are optional provenance. Present values must
be lowercase 32-hex, and a present pair must agree. Their absence does not
invalidate the public core. An unknown non-target extension is hashed only by
row shape, never retained by name or value, and blocks selection.

Structural parsing rejects malformed UTF-8/JSON, duplicate keys, non-finite
constants, non-list roots, and non-object rows. The target firewall recursively
rejects direct, nested-object, nested-list, and normalized target-like keys
before retention.

## Independent Evidence Layers

Each accepted family produces the frozen 21-field aggregate predicate vector
and seven domain-separated hashes:

```text
transport body
public core
optional extensions
row shapes
private classification
private selection
predicate vector
```

The raw-body hash is provenance only. Row order and object-key order preserve
all six semantic hashes, predicates, routes, historical differences, and
selection status.

Selection is available only when the known schema and every frozen historical
predicate match. A safe historical mismatch routes `MARC1SA-R3` and stops
before selection. An unknown non-target extension routes `MARC1SA-R4`, omits
the unknown name and value, and also stops before selection.

## Output Safety

The qualifier acquires a held no-follow parent capability before repository or
fixture work. It permits only a new normalized absolute path inside the real
system temporary tree. It creates exactly two mode-`0600` files through
parent-relative exclusive writes:

```text
marc1_source_aware_inventory.private.v0.json
marc1_source_aware_inventory_result.v0.json
```

The public validator rejects filenames, file IDs, URLs, MD5 values, source
rows, selected-subject lists, and participant-level outcomes. The qualifier
inspects the public file once, removes both files and its directory, and
returns only in-memory aggregate evidence.

## Adversarial Qualification

All six semantic families reached their frozen routes:

| Family | Route |
|---|---|
| documented five-field public core | `MARC1SA-R2` |
| observed seven-field extension | `MARC1SA-R1` |
| partial optional MD5 extension | `MARC1SA-R2` |
| one historical byte-total drift | `MARC1SA-R3` |
| multiple historical inventory drifts | `MARC1SA-R3` |
| unknown non-target extension | `MARC1SA-R4` |

The partial-MD5 family retained the frozen 36 supplied, 27 computed, and 18
agreeing-pair counts. The single-drift family reported only the byte-total
predicate. The multi-drift family reported participant count, supplementary
count, participant-name identity, and byte-total predicates in the frozen
order.

All 52 named refusals passed:

```text
F00 proof/source:        6
F02 JSON/container:      6
F03 target/row/URL/MD5: 34
F04 output/resources:    6
```

`MARC1SA-F01` remains reserved for a future separately authorized transport
wrapper and is intentionally unreachable from this no-network module.

## Final Development Measurement

One final nonregistered generated development qualification produced:

```text
overall route:                  MARC1SA-G1
semantic families passed:      6 / 6
refusals passed:               52 / 52
acceptance gates passed:       25 / 25
generated input bytes:         732,811
private output bytes:           95,392
public output bytes:            14,197
combined output bytes:         109,589
runtime:                      0.052419791 sec
peak RSS:                      27,426,816 bytes
external wall time:                  0.14 sec
external peak RSS:             27,426,816 bytes
network bytes:                          0
payload bytes:                          0
public SHA-256:                97bec694d0cb93e1b295edd2dbb957006
                                29ec388000114d0e19d4422d3bc4866
private SHA-256:               dd267efdce39ae20002d4e251f19cac4
                                39ce316c61c7f9c1bda2bd9e41e2a7c5
output files retained:                  0
```

Every dataset-specific request, response body, private or consumed path,
participant archive, payload, signal, target, model, training, prediction,
score, provider-model, hardware, other-project, retry, rerun, and claim counter
was zero.

The development SHA-256 values describe generated temporary bytes only. They
do not bind a public dataset response or participant payload.

## Tests

The behavior suite has 21 tests and 28 subtests covering:

- green proof and artifact binding;
- exact six-family routing;
- optional MD5 availability;
- historical mismatch localization;
- semantic replay under row/key reorder;
- nested target leakage;
- all 52 refusals;
- capability-first no-follow output;
- exact file modes and cleanup;
- deterministic private/public bytes;
- aggregate-public privacy;
- malformed/tampered reports;
- failure-path cleanup;
- resource and thread caps; and
- exact CLI shape and claim boundary.

## Next Gate

Commit, push, and require both remote CI jobs green for this exact source,
tests, implementation document, and machine registry. Only then may one
registered generated closeout run under the same caps. That closeout remains
generated engineering evidence.

A future public metadata response remains closed behind a new all-false Tier C
packet, a fresh packet-bound maintainer decision, and a separately green live
wrapper. No participant archive or neural payload becomes eligible from a
generated success.

## Claim Boundary

Engineering capability added: a deterministic generated harness can separate
public source schema, optional checksum provenance, target-free cohort
identity, and later payload integrity while localizing safe inventory drift.

Scientific claim not established: no real metadata, neural signal, target,
model, prediction, decoding score, language result, or thought-to-text
capability was accessed or established.
