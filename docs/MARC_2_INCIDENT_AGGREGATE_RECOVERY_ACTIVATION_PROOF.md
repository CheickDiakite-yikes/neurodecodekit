# MARC2-VR14P Aggregate Recovery Activation Proof

Date: 2026-08-21

Lane: `MARC2-VR14P`

Status: activation transition recorded; ineffective until this exact commit is
pushed and both required CI jobs are green

Machine record:
`registries/marc2_incident_aggregate_recovery_implementation_proof.v0.json`

## Green Barriers

Exact Stage 1 implementation `046013a4a8089f5a9f3a91fc246420cac21a1d20`
passed Base Python job `96664169190`, Optional Neuro Readers job
`96664169147`, and CI `32445483857`.

Exact proof-only closeout `f352c1b50d15ab81f641dca21732e1ffffa7a6b8`
passed Base Python job `96665759734`, Optional Neuro Readers job
`96665759548`, and CI `32446071998`. The activation record binds the three
closeout artifacts totaling 8,959 bytes by path, byte count, SHA-256, and Git
blob.

## Delayed Effect

This record performs no generated qualification and no ignored-path operation.
It does not become effective because it exists locally or is committed. The
single fixed execution remains closed until this exact activation commit is
pushed and both required remote jobs are green.

After that proof, one explicitly armed command may open only the registered
aggregate report once, strict-parse at most 65,536 bytes, and write one new
aggregate receipt. Missing, malformed, leaking, unknown-route, or over-budget
input consumes and parks the lane. There is no retry, rerun, resume, fallback,
substitution, cleanup, or reinspection.

## Boundary

This activation does not permit access to the VR13P readiness certificate,
consumed marker, private cohort manifest, structural source, sibling, archive
member, neural payload, signal, event, target, label, model, prediction, or
score. It does not authorize FW2 or CIL1. `MARC2VR13P-R1` could only make a
separate private-manifest recovery packet eligible.

Engineering capability activated after remote green: one proof-separated,
fixed-path, aggregate-only incident recovery command.

Scientific claim not established: this activation record contains no neural
data or result and establishes no neural effect, decoding performance,
language decoding, live decoding, or thought-to-text capability.
