# MARC2-VR28P Inventory/Taxonomy Request Proof Closeout

Date: 2026-08-22

Lane: `MARC2-VR28P`

Status: **Proof-only closeout pending its own remote-green barrier**

Machine proof:
`registries/marc2_inventory_taxonomy_private_discriminator_request_proof.v0.json`

## Exact Remote Proof

Exact all-false request commit
`4e5895fc0fc8bc3cf2c91f5211406115a8e2e6d5` passed:

```text
CI run:                 32613575234
Base Python job:        97130420447
Optional Neuro job:     97130420507
both required jobs:     green
```

The unchanged request artifact set is:

| Artifact | Bytes | SHA-256 | Git blob |
|---|---:|---|---|
| authorization packet | 8,318 | `cc070d0a9d7310c9f5cd681a2489fc8065020f1ca51d4738f97a1b9862607e52` | `0f33d1c5eccde6354cc396f6026d4c6bf3ed5b76` |
| machine request | 14,289 | `0fc194af25972ea58e003c1f042ab73e12a0908ac988e67722263a56095034ba` | `e256ca3ef1f96edadd11a4ec171d90bc036cdfac` |
| request test | 7,580 | `4dd12d7639c6a61cd83faf8182dbb257480d7dc230c8efe8ea4b897a6111dd75` | `b2df7af6c7cd4408a1f718bdc195759dd3157e6a` |

The three files total 30,187 bytes. The packet still binds 13 predecessor
inputs totaling 149,233 bytes, and every request authority flag remains false.

## Scope Is Unchanged

This closeout does not add implementation authority or alter either delayed
stage. A future Stage 1 remains one generated fixed-path wrapper around
unchanged VR25A and the frozen VR27A map. A future Stage 2 remains one
418,755-byte target-free structural read, one VR25A call, one VR27A map call,
and aggregate-only R1 inventory/distribution or R2 unknown-taxonomy output.

No predicate, value, count, direction, row, path, identity, participant,
selection, or cohort may be retained. The one-invocation, one-thread,
256 MiB RSS, 1 MiB output, zero-network, zero-new-payload, and no-rerun limits
are unchanged.

## Zero-Operation Closeout

This closeout performs no generated qualification or implementation. It does
not inspect readiness, `.codex_work`, the private source, any consumed lane,
archive content, neural data, events, targets, models, predictions, scores,
network, providers, devices, streams, hardware, other projects, or release
state. It changes no scientific claim.

The request and proof tests pass with the complete dependency-light suite.
Ruff on the new tests, compilation, all registry JSON, and diff hygiene pass.
The repository-wide Ruff baseline still contains pre-existing findings and was
not broadened into this proof-only milestone.

## Delayed Effect

This closeout is ineffective until its own exact commit is pushed and both
required CI jobs are green. Only after that proof may VR28P be identified as
the sole active Tier C gate. A fresh unambiguous maintainer message after that
identification is still required before a decision can authorize Stage 1.

Engineering capability added: the exact all-false VR28P request now has a
remote proof chain binding its immutable bytes and aggregate-only boundary.

Scientific claim not established: no private source or neural payload was
accessed, no cohort was frozen, and no decoding result was produced.
