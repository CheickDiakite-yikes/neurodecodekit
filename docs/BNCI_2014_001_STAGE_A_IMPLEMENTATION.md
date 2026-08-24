# BNCI-C3C5-1 Stage A Acquisition Implementation

Date: 2026-08-24

Status: **implementation qualified; live invocation not run**

Machine record:

- `registries/bnci_2014_001_stage_a_implementation.v0.json`

## Added Capability

Stage A now has an isolated sidecar implementation for the one authorized
opaque acquisition of the 18 frozen NEMAR MAT payloads. It is additive: the
proof-bound G1 module, CLI, scorer, and generated result remain byte-identical.

Before a live transport can be constructed, the executor verifies the exact
G1 proof registry and requires the five numerical thread variables to equal
one. It then writes one exclusive consumed marker. Existing destinations,
markers, receipts, symlinks, redirects, response compression, malformed
lengths, wrong ranges, wrong sizes, and wrong SHA-256 digests fail closed.

The transport uses standard-library HTTPS with certificate verification, no
proxy, no redirect following, identity encoding, bounded one-MiB reads, and
only the registered URL order. The existing G1-qualified downloader owns
partial-file cleanup and accepts a final file only after an opaque size and
SHA-256 pass. No MAT structure or content is interpreted in Stage A.

## Qualification

Focused tests verify the exact green G1 proof, preservation of every original
G1 implementation artifact, request and range semantics, redirect and short-
body refusal, foreign-root refusal before network construction, and CLI help.
The plan command reports only aggregate registered facts and performs no
ignored-path or network operation.

## Resource Boundary

- 18 files and exactly 779,873,919 accepted payload bytes;
- at most 54 requests and three attempts per file;
- at most 2.5 GiB network transfer and 2 GiB incremental disk;
- at least 5 GiB free disk before execution;
- one CPU thread, worker, and numerical job;
- at most 1 GiB peak RSS and 1,800 seconds; and
- at most 4 MiB aggregate public output.

The private bundle, member manifest, consumed marker, and detailed receipt are
written only below `.codex_work/bnci_c3c5/`, which is Git-ignored. No existing
file or unrelated project is touched.

## Next Gate

Commit and push this exact implementation and require both remote CI jobs to
pass. Only then may the one registered Stage A invocation run. Its aggregate
result must be committed, pushed, and remotely green before Stage Q can parse
any MAT content.

Engineering capability added: NeuroDecodeKit can perform one proof-gated,
bounded, opaque acquisition of the exact frozen BNCI payload.

Scientific claim not established: no real payload has been acquired or
opened, no model has run, and no EEG, EOG, target, or decoding result has been
measured in this milestone.
