# MARC2-VR18P First-Failure-Stable Private Discriminator Proof Closeout

Date: 2026-08-21

Lane: `MARC2-VR18P`

Status: **Proof-only closeout pending its own remote-green barrier**

## Exact Stage 1 Proof

Exact generated Stage 1 implementation commit
`668812367acd8ca3ae9d0603dcde9b4b5aa02d58` passed:

```text
CI run:                 32477528982
Base Python job:        96756873128
Optional Neuro job:     96756873357
both required jobs:     green
qualification route:    MARC2VR18P-G1
scope changed:           false
```

The preproof implementation registry contained 8,361 bytes with SHA-256
`fe57de79cd7891f6d60b975bbe4373d5810b57c540c255335337414b08d5af50`.
The preproof result registry contained 3,654 bytes with SHA-256
`478d23e4f52646bb237e4ef6a38e65401c6315f84febc4c9c20a366f585db403`.

The exact Stage 1 commit contains these Git blobs:

| Artifact | Git blob |
|---|---|
| implementation module | `c3d52b78c280a3ec5dafc70857eadb41b76602c4` |
| behavior test before proof hardening | `17725cdf19b514e7a76722139316747f90bac466` |
| implementation document | `2734e025b8e07c8b3036119e0aa3ea695bdc3ffb` |
| generated result document | `d4477735a21256e366b21b303978404453b223ee` |
| preproof implementation registry | `d3df4b78d3ab4b9b11af5645e32808bcef2c7c28` |
| preproof result registry | `23824ee5c47dba67a53b6b45dd9454c1f47a558b` |
| preproof record test | `1dc288a355ead98a0ea27eef87f4448e82a7fbf4` |

## Proof-Safe Test Transition

This closeout does not change the implementation module, generated fixture,
route table, fixed paths, source identity, measured qualification, resource
caps, or claim boundary. It updates the behavior test so the F01 proof-null
refusal remains explicitly injected after the tracked registry gains its
remote proof, and updates the record test to assert that exact proof. These
test-only changes cannot collect readiness or inspect a private path.

The registered generated qualification was not repeated. Readiness,
`.codex_work`, private-source, cohort, archive, neural, event, target, model,
prediction, score, network, hardware, other-project, FW2/CIL1, release, retry,
and scientific-claim operations are all zero.

## Delayed Effect

This closeout is ineffective until its own exact commit is pushed and both
Base Python and Optional Neuro Readers jobs are green. Before that proof, do
not run `execute`, collect readiness, inspect the registered private source,
or create the real output root.

After this exact closeout is remotely green, the existing packet and decision
permit exactly one Stage 2 invocation. It may read and strict-parse exactly
418,755 target-free structural bytes once, call VR16A once, consult the frozen
VR17C route map at most once, and retain only the registered aggregate output.
It has no retry, rerun, resume, repair, fallback, substitution, or private
reinspection.

Engineering capability added: exact remotely green generated wrapper bytes
are bound before one bounded target-free structural discriminator may run.

Scientific claim not established: this closeout accesses no neural signal,
target, model, prediction, or score and establishes no decoding performance,
language decoding, live decoding, or thought-to-text capability.
