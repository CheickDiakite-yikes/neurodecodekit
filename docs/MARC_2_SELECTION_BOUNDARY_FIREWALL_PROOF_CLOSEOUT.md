# MARC2-VR25A Selection-Boundary Firewall Proof Closeout

Date: 2026-08-22

Lane: `MARC2-VR25A`

Status: **Proof-only closeout pending its own remote-green barrier**

## Exact Remote Proof

Exact implementation and generated result commit
`891245d73d8e11304d4a98e841ead6f57ad68ff8` passed:

```text
CI run:                 32604761988
Base Python job:        97108121455
Optional Neuro job:     97108121321
both required jobs:     green
qualification route:    MARC2VR25A-G1
scope changed:           false
```

The preproof implementation registry contained 5,474 bytes with SHA-256
`33fef70bed08a229d846fd8da49c1a7e7bc808d554ed9a6c3b4d98ce63bb03d3`.
The preproof result registry contained 4,704 bytes with SHA-256
`71d19f0bc22778ef1e3208821ccadad1c30df0078f54691e43c79e0064922c27`.

The exact implementation commit contains these Git blobs:

| Artifact | Git blob |
|---|---|
| implementation module | `d5394abea69547c321eaad2647e9bff0b0691ad5` |
| behavior test | `4bb6ecee067ad0827a4a4a84e864cb9736adacc3` |
| implementation-boundary test | `df31491fcca83ed2175183749f71ab9fe2c8552a` |
| result-record test | `569b8dbd647308db83e317a2f3a3b31c0a463500` |
| implementation document | `a7ba43d9fdc6b87dc50ad2b70d21039047a1ed53` |
| preproof implementation registry | `f87786d0e9698bafb68893b4ff7c370be7832190` |
| preproof result registry | `027bd428dee9bdb3606734bfceefc66fc14ce475` |

## Proof-Safe Transition

This closeout changes no firewall implementation, generated fixture, route,
measurement, warning, resource cap, or claim boundary. It updates only the two
machine records with exact remote proof, adds assertions for that proof, and
updates public handoff documentation.

The generated qualification was not repeated. No private or Git-ignored path,
VR24P source or consumed state, archive payload, neural data, event, target,
model, prediction, score, network, hardware, other project, FW2/CIL1
operation, release, or scientific claim was accessed or changed.

Thirty focused VR25A tests and all 4,973 dependency-light tests passed with
204 expected skips and zero failures, five tests above the 4,968-test
precloseout baseline. Ruff, compilation, both registry JSON documents, CLI
`help`, `plan`, and `inspect`, and `git diff --check` passed. No command invoked
`qualify`.

## Delayed Effect

This closeout is ineffective until its own exact commit is pushed and both
required CI jobs are green. After that proof, VR25A is closed as remotely
proven generated engineering and Tier A may prepare one separately frozen,
all-false private confirmation packet. That packet will not authorize a
private read; a fresh packet-bound Tier C decision will still be required.

Engineering capability added: exact remotely green code now preserves the
same eligible target-free selection while quarantining generated drift that
affects only known non-selected complete bundles.

Scientific claim not established: no real cohort, archive member, neural
payload, target, model, prediction, or score was accessed, so no neural effect,
decoding accuracy, unseen-person generalization, thought decoding, or live
decoding was established.
