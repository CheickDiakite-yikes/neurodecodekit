# MARC2-VR14P Incident Aggregate Recovery Implementation

Date: 2026-08-20

Lane: `MARC2-VR14P`

Status: Stage 1 generated-qualified; aggregate read remains closed

Machine record:
`registries/marc2_incident_aggregate_recovery_implementation.v0.json`

## Green Decision

Exact authorization decision `60b97ea6c9715b651c17bb6d797c1f02c10ba9e2`
passed Base Python job `96661242381`, Optional Neuro Readers job
`96661242496`, and CI `32444425790` before implementation began.

## Added Interface

The standard-library module
`src/neurodecodekit/datasets/marc2_incident_aggregate_recovery.py` exposes
fixed `plan`, `qualify`, `inspect`, and `execute` commands.

The reader validates the exact public aggregate schema emitted by VR13P. It
accepts only routes `MARC2VR13P-R1` through `MARC2VR13P-R8`, canonical strict
JSON, the frozen upstream proof, bounded aggregate counts, exact zero
forbidden-operation counters, exact warnings and unavailable fields, and a
scientifically empty claim boundary.

It rejects duplicate keys, non-finite values, noncanonical encodings,
symlinks, aliases, oversized content, unknown routes, changed proofs, resource
drift, and public keys that could expose a source, person, row, member,
predicate, target, model, prediction, or score.

## One-Shot Safety

`execute` refuses before proof loading or ignored-path access unless the fixed
one-shot arming value is present. It then requires a separate implementation-
proof registry to be tracked at `HEAD` and clean, and verifies every owned
implementation artifact by exact bytes and SHA-256.

This addresses the VR13P incident directly: merely editing local proof fields
cannot make an ordinary test cross into `.codex_work`. The one aggregate open
remains closed until the exact implementation and a separate proof closeout
are both remotely green.

## Generated Qualification

One standalone one-thread qualification reached `MARC2VR14P-G1`:

```text
generated routes:                 8
orders / replays / paths:         2 / 2 / 32
count per route:                  4
generated report validations:     33
direct refusals:                  89
generated input bytes:            50,370
aggregate output bytes:           2,058
temporary receipt bytes:          1,925
retained output bytes:            0
runtime seconds:                  0.008616000006441027
peak RSS bytes:                   28,901,376
CPU threads / workers / jobs:     1 / 1 / 1
network / new payload bytes:      0 / 0
```

Replay SHA-256:
`94d920bfcf235f3950311ea64553e9742a744038e9f6104dbbf8dc8ab357bcc6`.

The generated fixed-path case created and removed only a temporary root. It
retained no output and performed zero real or Git-ignored path operations.

## Current Boundary

The implementation has not opened, statted, resolved, hashed, listed, or
parsed the real aggregate report, readiness certificate, consumed marker,
private manifest, structural source, sibling, or another ignored path. It has
not accessed an archive, neural signal, event, target, model, prediction, or
score.

Next: commit, push, and green this exact implementation. Then create, commit,
push, and green a separate proof-only closeout. Only afterward may the one
armed aggregate-only execution run.

Engineering capability added: a strict, fixed-path, one-shot aggregate
recovery reader with deterministic generated replay and leakage controls.

Scientific claim not established: generated qualification is not neural data
and establishes no neural effect, decoding performance, language decoding,
live decoding, or thought-to-text capability.
