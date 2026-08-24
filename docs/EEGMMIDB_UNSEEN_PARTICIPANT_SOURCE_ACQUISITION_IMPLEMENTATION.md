# EEGMMIDB-UG1 Stage S-A1 Source Acquisition Implementation

Date: 2026-08-24

Lane: `EEGMMIDB-UG1-SA1`

Status: **Implementation ready; registered generated qualification not
executed; exact implementation commit must be remotely green first**

Machine implementation record:

- `registries/eegmmidb_unseen_participant_source_acquisition_implementation.v0.json`

## Green Authority

Authorization decision `1b5c9195f384e5867f18131aa7d669f7c9cd0e2b`
passed Base Python job `97426157639`, Optional Neuro Readers job
`97426157381`, and CI `32725633524` before this implementation began.

The decision binds only the unchanged green request and proof artifacts. This
implementation activates Stage S-A1 generated/mock work only. It does not
activate Stage S-A2 or perform a network, real-payload, target, model, or score
operation.

## Added Capability

The isolated
`src/neurodecodekit/datasets/eegmmidb_unseen_participant_source_acquisition.py`
module provides:

- a hash-locked six-file source-only allowlist cross-checked against the green
  authorization decision, request, and Stage M inventory;
- strict direct HTTPS `GET` construction with no proxy, redirect, retry,
  fallback, range, mirror, query, credential, or host-substitution route;
- a bounded ASCII `SHA256SUMS.txt` parser that freezes exactly six lowercase
  checksums before the first payload request and refuses missing, duplicate,
  malformed, uppercase, traversal, and alias entries;
- exact request order and exact conditional headers using identity encoding,
  strong `If-Match`, and `If-Unmodified-Since`;
- duplicate-sensitive direct status, final URL, `Content-Length`, `ETag`,
  `Last-Modified`, and `Accept-Ranges` validation before a body read;
- refusal of `Content-Encoding`, `Content-Range`, `Transfer-Encoding`, short,
  oversized, non-byte, partial, or unexpected response bodies;
- opaque sequential streaming in reads no larger than 1 MiB, transfer SHA-256,
  and exactly one no-follow local size/SHA-256 pass per completed EDF;
- a durable exclusive consumed marker synced before the first opener call;
- exclusive single-link files, exact temporary membership, a private canonical
  manifest, and atomic no-replace complete-bundle promotion;
- inode-checked cleanup of invocation-created temporary objects only;
- aggregate public receipt validation that excludes identities, paths, URLs,
  validators, checksums, targets, and participant-level outcomes; and
- one-thread, free-disk, network-body, header, metadata, incremental-disk,
  wall-time, and peak-RSS enforcement.

The generated fixture streams exact registered payload sizes without retaining
fixture files. The module contains no EDF parser, MNE import, target transform,
feature extractor, model, inference, training, prediction, or scoring surface.

## CLI Boundary

The isolated sidecar
`src/neurodecodekit/eegmmidb_ug1_source_acquisition_cli.py` exposes only:

- `plan`: aggregate dry-run information with zero network or payload access;
- `qualify`: the one generated/mock Stage S-A1 adversarial qualification.

There is deliberately no `execute`, URL, source-root, destination-root,
participant, run, retry, or override argument. The central CLI and all
proof-bound Stage G and Stage M modules remain unchanged.

The internal Stage S-A2 entry point refuses before constructing the standard-
library live opener unless a future exact Stage S-A1 implementation/result and
proof-closeout registry is supplied and verified. Its presence is a gate under
test, not present authority to contact PhysioNet.

## Qualification Design

The registered Stage S-A1 pass has 27 ordered cases:

1. complete six-file bundle;
2. deterministic replay;
3. missing checksum;
4. duplicate checksum;
5. uppercase checksum;
6. aliased checksum path;
7. malformed checksum line;
8. request-order drift;
9. missing response;
10. redirect;
11. non-200 status;
12. content-length drift;
13. ETag drift;
14. last-modified drift;
15. accept-ranges drift;
16. content encoding;
17. content range;
18. short body;
19. oversized body;
20. non-byte stream;
21. output collision;
22. second invocation;
23. thread-environment drift;
24. free-disk failure;
25. peak-RSS breach;
26. wall-time breach; and
27. fresh-final path refusal.

Focused unit tests exercise the component contracts, including exact-sized
generated streams. The sole registered aggregate qualification has not run. It
may run only after this exact implementation commit is pushed and both required
CI jobs pass.

## Current Operation Ledger

```text
registered generated qualifications: 0
real network requests:                 0
real URL or local payload operations:  0
real payload / new disk bytes:         0 / 0
EDF semantic reads:                    0
targets / model / training / score:    0 / 0 / 0 / 0
fresh-final / retained-source reads:   0 / 0
release / claim upgrades:              0 / 0
```

## Next Gate

Commit and push this exact implementation and require both CI jobs green. Then
run the one registered generated/mock qualification and record its measured
aggregate result. Stage S-A2 remains closed until that result commit and a
separate proof-only closeout are each pushed and remotely green.

Engineering capability added: a dependency-light, checksum-bound, streaming,
complete-bundle-only source acquisition gate is ready for one generated/mock
qualification.

Scientific claim not established: no real URL, EEG payload, target, model, or
score was accessed, so this implementation establishes no neural effect,
decoding advantage, movement intention, motor-cortex origin, eye independence,
language decoding, live performance, or unseen-person generalization.
