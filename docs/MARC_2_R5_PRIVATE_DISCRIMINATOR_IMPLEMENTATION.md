# MARC2-VR22P R5 Private Discriminator Implementation

Date: 2026-08-22

Lane: `MARC2-VR22P`

Status: **Generated Stage 1 qualified; exact remote implementation proof and a
separately green proof-only closeout are still required before Stage 2**

Machine record:
`registries/marc2_r5_private_discriminator_implementation.v0.json`

## Authority And Boundary

Packet-bound decision `197f253e9e0411085f6ecdccf466f9f7059bd479`
passed Base Python job `97080176920`, Optional Neuro Readers job
`97080176717`, and CI `32593234295` before implementation began.

This implementation performs only the packet's generated Stage 1. It does not
stat, resolve, hash, open, parse, copy, or modify the registered private source,
readiness path, output root, consumed VR20P state, archive members, neural
payloads, targets, models, predictions, or scores.

## Fixed Interface

The additive dependency-free module
`src/neurodecodekit/datasets/marc2_r5_private_discriminator.py` exposes only:

```text
plan
qualify
inspect
execute
```

There is no source, output, URL, task, run, reason, threshold, cap, route,
retry, resume, fallback, or substitution argument. `execute` verifies the
exact decision and upstream artifacts, then refuses before readiness or any
private path operation while the implementation proof is null.

The wrapper does not import or call the consumed VR20P executor. It calls the
unchanged VR20A adapter once per path and calls the exact VR21A route map only
after an F06 or F07 refusal. Success bypasses VR21A mapping.

## Generated Qualification

One measured qualification used three generated cases, two source orders, and
two exact replays:

| Case | VR22P route | Paths | VR20A calls | VR21A map calls |
|---|---:|---:|---:|---:|
| accepted control | `MARC2VR22P-G1` | 4 | 4 | 0 |
| F06 taxonomy/eligibility witness | `MARC2VR22P-R4` | 4 | 4 | 4 |
| F07 selection/split/rank/reservation witness | `MARC2VR22P-R5` | 4 | 4 | 4 |

All 12 paths passed. Each case/order source hash replayed exactly. The accepted
control preserved the generated 16-subject, 96-bundle, 384-core-member cohort
with semantic hash
`254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba`.
The execution envelope and aggregate firewall passed 121 direct refusal
mutations, above the frozen minimum of 60.

## Measurements

```text
generated input bytes:          5,301,432
generated output bytes written:   915,445
peak temporary output bytes:       223,195
retained generated output bytes:         0
aggregate report bytes:              3,559
runtime seconds:                   0.867054
peak RSS bytes:                  35,946,496
CPU threads / workers / jobs:       1 / 1 / 1
VR20A calls:                               12
VR21A map calls:                            8
raw-data / real-cache reads:            0 / 0
model / training runs:                  0 / 0
network / new payload bytes:            0 / 0
end-to-end latency measured:              no
```

All generated files lived under invocation-created temporary directories and
were removed on context exit. No repository `.codex_work` operation occurred.

## Fail-Closed State Machine

The wrapper freezes fresh readiness, no-follow source identity, one content
open, one strict parse, one VR20A call, at most one VR21A map call, marker
before content open, a private manifest on R1 only, aggregate-only R1-R6
reporting, and the existing resource caps. Public output rejects member, path,
identity, session, run, task, companion, predicate, reason, exception, target,
prediction, score, and outcome fields.

Every future route consumes the registered invocation. No retry, rerun,
resume, repair, fallback, substitution, cleanup, private reinspection, or
post-result amendment is implemented.

## Next Gate

Commit, push, and green this exact implementation. Then add a proof-only
closeout that changes no qualified artifact and repeats no qualification or
private operation. Only after that closeout is separately committed, pushed,
and green may `execute` perform the one registered target-free structural read.

Engineering capability added: a fixed-path wrapper now distinguishes the
remaining generated-qualified F06 and F07 structural classes while preserving
one-shot source, privacy, provenance, and resource controls.

Scientific claim not established: no real/private source, archive member,
neural signal, target, model, prediction, or score was accessed, so this Stage
1 result establishes no neural effect, decoding accuracy, language decoding,
unseen-person generalization, live decoding, or thought-to-text capability.
