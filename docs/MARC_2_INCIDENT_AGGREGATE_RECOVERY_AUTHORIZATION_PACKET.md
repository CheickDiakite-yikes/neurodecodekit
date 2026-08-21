# MARC2-VR14P Incident Aggregate Recovery Authorization Packet

Date: 2026-08-20

Lane: `MARC2-VR14P`

Status: all-false request; no implementation or ignored-output access authorized

## Purpose

VR13P is consumed invalid because an uncommitted local proof object let a
focused test pass F01 before the proof closeout was committed and remotely
green. The test did not retain the returned aggregate route, and the ignored
output was deliberately not inspected afterward.

VR14P requests the smallest possible recovery surface: one future read of only
the already-written aggregate public report. It does not request another
structural-source read or access to the private cohort manifest.

## Bound Incident Proof

Incident commit `1563cae48a9424b38f13a42b25e17e8587a18c92` passed:

```text
CI run:                 32442807612
Base Python job:        96656682033
Optional Neuro job:     96656682232
both required jobs:     green
```

The request binds six tracked incident, implementation, and authorization
artifacts by path, byte count, SHA-256, and Git blob. Packet preparation does
not stat, resolve, hash, open, or list `.codex_work`.

## Requested Sequence

Only a fresh packet-bound Tier C decision may activate this sequence:

1. Build a standard-library wrapper and qualify it only with generated
   aggregate reports and temporary fixed-path fixtures.
2. Commit, push, and remotely green that exact implementation.
3. Commit, push, and remotely green a separate proof-only closeout that repeats
   no qualification and performs no ignored-path operation.
4. Perform one no-follow size-and-content open of only
   `.codex_work/marc2_r4_private_discriminator/v0/report.aggregate.v0.json`.
5. Strict-parse at most 65,536 bytes, enforce the frozen aggregate schema and
   R1-R8 route allowlist, and write one new aggregate recovery receipt under a
   separate fixed output root.

Any missing, symlinked, oversized, malformed, leaking, unknown-route, or
resource-exceeding report consumes and parks VR14P. There is no retry, rerun,
resume, fallback, substitution, cleanup, or source reinspection.

## Explicitly Closed

The future sequence must not open, stat, resolve, hash, list, or parse the
VR13P readiness certificate, consumed marker, private cohort manifest,
structural source, sibling, or any other ignored path. It must not access an
archive header/member, signal, event, channel, geometry, target, label, cache,
feature, split, NeuroToken, model, prediction, score, network, provider,
language model, stream, device, hardware, or another project.

R1 would only make a separate private-manifest recovery packet eligible. It
would not make FW2 or CIL1 executable. R2-R8 would recover one aggregate
structural class only.

## Bounds

```text
CPU threads:                         1
workers / numerical jobs:            1 / 1
future runtime cap:                  30 seconds
future peak RSS cap:                 256 MiB
aggregate report content opens:      1
aggregate report bytes:              <= 65,536
combined generated output cap:       1 MiB
network / new payload bytes:         0 / 0
structural-source opens:              0
private-manifest operations:          0
retry / rerun / resume:               0 / 0 / 0
```

Every authorization in the machine request is currently false and every
operation counter is zero.

Engineering capability requested: a proof-separated, aggregate-only recovery
reader that cannot reopen the consumed structural source or private manifest.

Scientific claim not established: this all-false packet accesses no ignored
output, cohort, neural signal, target, model, prediction, or score and
establishes no neural effect, decoding performance, language decoding, live
decoding, or thought-to-text capability.
