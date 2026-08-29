# DREYER-C5R-1 H-L1R1 Generated Recovery Implementation

Date: 2026-08-29

Status: **implementation complete; remote-green proof and separate
qualification activation still required**

Machine record:

- `registries/dreyer_c5r_1_stage_h_live_recovery_implementation.v0.json`

## What Was Built

This milestone adds a separate standard-library recovery module and CLI. It
does not modify the consumed H-L1 source, CLI, or tests. The new module binds
the remotely green H-L1R1 decision, verifies the three frozen predecessor
artifacts, and provides a generated-only transaction implementation with these
properties:

1. the protected transaction begins immediately after marker durability and
   before staging, opener, request, or response capability;
2. an invocation manifest records only paths actually created by that case;
3. cleanup refuses any path outside that manifest and never follows symlinks;
4. expected and unexpected standard exceptions become allowlisted codes and
   case identities without exception text;
5. response closure and path cleanup are independently accounted;
6. response-close or cleanup failure downgrades the outcome to H0;
7. every eligible post-marker refusal emits one aggregate H0;
8. publication failure occurs only after teardown and leaves no generated
   staging or final payload; and
9. public output is strict, bounded, target-free, path-free, and explicit about
   unavailable science and latency fields.

The CLI exposes only `plan` and `inspect`. It has no `qualify`, `execute`, URL,
network, real-path, or EDF argument. A future qualification command may not be
added until a separate all-false activation and fresh decision are remotely
green.

## Development Verification

The bounded unit-level suite exercised both deterministic valid replay and all
43 ordered successor failure identities. These are development checks, not the
registered one-shot qualification.

```text
focused tests / subtests:                  9 / 43
focused suite runtime:                     0.709127917 seconds
focused suite peak child RSS:              56,655,872 bytes
valid-case generated input:                42,496 bytes
valid-case public output:                  2,073 bytes
valid-case input + marker + output:        44,813 bytes
valid-case private allocated bytes:        49,152 bytes
retained output after temporary cleanup:   0 bytes
registered qualification runs:             0
real/private path operations:              0
HTTP requests / network bytes:             0 / 0
real EDF/header/signal/target reads:        0 / 0 / 0 / 0
model runs / training / inference / scores: 0 / 0 / 0 / 0
provider / stream / device / hardware:      0 / 0 / 0 / 0
producer causal:                            unavailable
end-to-end latency measured:                false
```

The three original H-L1 artifacts retain their exact frozen SHA-256 values.
The focused suite, CLI help, Ruff, JSON parsing, and `git diff --check` passed
locally under one-thread environment variables.

## Next Barrier

This exact implementation must be committed, pushed, and pass Base Python and
Optional Neuro Readers on GitHub `main`. A proof-only closeout may then bind
its exact code and test hashes. Only after a separate all-false qualification
activation packet and fresh packet-bound decision are remotely green may the
single registered 43-case qualification run. H-L2 remains closed regardless
of this implementation result.

Engineering capability added: a transactionally complete generated recovery
wrapper now contains every registered failure surface without exposing real or
qualification execution capability.

Scientific claim not established: this implementation accesses no real EEG
and establishes no neural, decoding, unseen-person, peripheral-adjusted, live,
hardware, or clinical result.
