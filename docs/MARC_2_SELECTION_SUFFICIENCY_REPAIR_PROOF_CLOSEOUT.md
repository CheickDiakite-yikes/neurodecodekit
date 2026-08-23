# MARC2-VR38A Selection-Sufficiency Repair Proof Closeout

Date: 2026-08-23

Lane: `MARC2-VR38A`

Status: **Proof-only closeout pending its own remote-green barrier**

## Exact Remote Proof

Exact implementation and generated result commit
`7ef4a8dface0c2a00e27b38f1f91b4043c12535f` passed:

```text
CI run:                 32672478625
Base Python job:        97275279259
Optional Neuro job:     97275279380
both required jobs:     green
qualification calls:    1
scope changed:          false
```

The preproof implementation registry contained 7,182 bytes with SHA-256
`81192cb39c126cf5e464d530b2a1724df0232421e9f6f8fede6777c1a5029645`.
The preproof result registry contained 4,742 bytes with SHA-256
`298676b47daa0ea62144cb98f46924bf3552b8847e4c76041d75a6f468fd385e`.

The exact implementation commit contains these Git blobs:

| Artifact | Git blob |
|---|---|
| implementation module | `984e303a63255d909ae9eb4dd09c5f89f573570d` |
| behavior test | `f0f9f4eeab2abf019f0370026ebea0b4d01bcd27` |
| registration test | `7b2ea2c95ce8c3bf346041dff0d421164041f238` |
| surface test | `ce34baac1af41964c1a5ca41cd0864962ce0ec2a` |
| result-record test | `c76338bec65e33faa658b204b446b25c3d790b05` |
| implementation-record test | `fd74d9141c8ac19bb0d25839b77aa6e6457cb3ce` |
| implementation document | `f6b9b24b5a273583a20f23c5b2c807dde3601c01` |
| contract | `7490d781d4d640a82663bbd8c3cbbe5940e61aba` |
| preproof implementation registry | `109ad2ff80c5037e394e88c198c2ce40863bf657` |
| preproof result registry | `cec776feca9c22ffcb08e564e415e89ffffae68b` |
| live-domain helper | `52f49b58345b1c6fad344306c9978eca70dc9d03` |
| published-task helper | `33cd5e52d186a768ce8dc706e163c8d5c3a2fc92` |
| selection-firewall helper | `d5394abea69547c321eaad2647e9bff0b0691ad5` |

## Proof-Safe Transition

This closeout changes no implementation module, generated case, route,
selection rule, measurement, resource cap, warning, or claim boundary. It
updates only the two machine remote-proof objects, implementation status and
current-result metadata, additive proof assertions, and frontier documentation.
Every preproof code, test, and human implementation artifact remains
byte-identical; the current implementation registry records the post-transition
size and hash of the machine result while separately retaining its exact
preproof size, SHA-256, and Git blob.

The generated qualification was not repeated. Its invocation count remains
exactly one. No private or Git-ignored path, readiness state, consumed lane,
archive member, neural signal, event, target, label, model, prediction, score,
network, provider, stream, device, hardware, other project, FW2/CIL1 operation,
release, or scientific claim was accessed or changed.

## Verification

- The focused VR38A and proof-closeout suite passed 37/37 tests.
- The complete dependency-light suite passed 5,597 tests with 204 expected
  skips, a five-test increase over the 5,592-test implementation baseline.
- Ruff 0.15.20 checks, targeted formatting, compilation, all 429 registry JSON
  parses, module immutability, and `git diff --check` passed.
- A separate optional-neuro local run reached 5,668 tests with 35 skips but was
  not itself green: one forkserver socket was denied by the sandbox and two
  load-sensitive mechanics checks failed after the long run. Both mechanics
  checks passed in isolation, and the forkserver check passed once outside the
  sandbox. Remote Base and Optional Neuro CI remain the closeout authority.

## Delayed Effect

This closeout is ineffective until its own exact commit is pushed and both
required CI jobs are green. After that proof, VR38A is closed as remotely
proven generated engineering. It does not freeze a real cohort.

The next structural step may only be a newly frozen all-false terminal Tier C
packet for one target-free 418,755-byte read and one deterministic selection
attempt. A success must freeze at least 12 participants; any failure parks the
Freewill/CIL1 lane. Another topology-only private discriminator is forbidden.
The packet still needs a fresh packet-bound maintainer decision before private
access. Archive members, neural payloads, targets, models, scores, devices,
release, and claims remain closed.

Engineering capability added: exact remotely green generated code can select
the same scientific core despite harmless optional-run inventory drift.

Scientific claim not established: no real cohort, archive member, neural
payload, target, model, prediction, or score was accessed, so no neural effect,
decoding performance, advantage over a no-signal or peripheral baseline,
language decoding, unseen-person generalization, or live decoding claim was
tested.
