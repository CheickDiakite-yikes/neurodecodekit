# NPA1-G Generated Qualification Proof Closeout

Date: 2026-08-29

Status: **implementation remotely green; proof-only closeout effective after
this exact closeout commit is pushed and both required CI jobs are green**

Machine proof:

- `registries/neural_payload_admission_generated_qualification_proof.v0.json`

## Remotely Green Implementation

Exact successor commit
`2e164fffb00e5db79a6c6d810eabbcc2d447c5a1` passed on GitHub `main`:

- Base Python job `99184746988`;
- Optional Neuro Readers job `99184747065`; and
- CI `33284320443`.

The predecessor implementation commit `be9110b4c91842610cda4774eaabd41a15ef284c`
was not accepted because its late full-suite CLI subprocess inherited the
Linux runner's lifetime RSS high-water mark. The successor keeps the real RSS
gate unchanged and limits that nested subprocess test to CLI help and plan;
the generated roundtrip remains directly tested, and the measured standalone
qualification was not repeated.

## Bound Evidence

This proof binds six exact implementation and qualification artifacts totaling
89,732 bytes. Their canonical artifact-set SHA-256 is:

```text
93e293f9718119019d88d328338ae328d00bcabef2308f135610d33a17efadc5
```

The accepted generated result remains two deterministic seven-profile
replays, one refreshed capability identity, and 37 exact adversarial
refusals. It completed in 0.003375791013240814 seconds at 22,577,152-byte
peak RSS, read 4,162 generated input bytes, emitted a 4,947-byte aggregate
report in memory, and retained zero payload bytes.

## Proof Boundary

This closeout reads only six committed artifacts and their Git identities. It
does not rerun qualification, open a network client, contact a source, inspect
a real or private path, read a payload or sensor header, parse a signal, event,
annotation, target, or label, run a model, train, predict, score, stream,
operate hardware, publish a release, or upgrade a scientific claim.

No Tier C packet is active. The consumed Dreyer and Ofner invocations remain
closed, and the unrelated tracker inspection file remains untouched.

## Next Gate

After this closeout is remotely green, NPA1-G generated transport engineering
is closed. The next reversible step is an all-false fresh-source research
preregistration that defines candidate, license, nuisance-control, participant,
geometry, storage, and metadata boundaries before any source-specific network
request. A real 256-byte canary remains a separate Tier C operation.

Engineering capability added: the dependency-free transport-admission validator is now hash-bound and remotely proven across exact request, redirect, framing, range, bounded-read, capability-expiry, and sanitized-report behavior.

Scientific claim not established: no neural measurement was accessed or analyzed, so no neural advantage, unseen-person generalization, movement-intention decoding, language decoding, live operation, hardware result, or clinical value was established.
