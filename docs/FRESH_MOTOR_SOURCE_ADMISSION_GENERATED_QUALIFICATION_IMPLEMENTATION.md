# Fresh Motor Source Admission Generated Qualification Implementation

Date: 2026-08-30

Protocol: `FMSR1-R1-G-v0`

Implementation: `FMSR1-R1-G-I0`

Status: **additive generated-only implementation complete locally; official
qualification has not run and remains blocked until this exact implementation
is committed, pushed, remotely green, and separately activated**

Machine record:

- `registries/fresh_motor_source_admission_generated_implementation.v0.json`

## Green Registration Boundary

The implementation is downstream of exact registration commit
`d53f3e8870b1f3ae6f014411c9932f20474b8092`. GitHub `main` CI
`33341954248` passed both required jobs:

```text
Base Python:             99339083749
Optional Neuro Readers: 99339083636
```

The implementation reads and verifies the exact registration contract and
frontier v16 bytes before exposing a plan. It does not authenticate GitHub or
contact a source.

## Added Surface

The implementation is isolated in:

```text
src/neurodecodekit/datasets/fresh_motor_source_admission.py
src/neurodecodekit/fmsr1_admission_cli.py
tests/test_fresh_motor_source_admission.py
tests/test_fmsr1_admission_cli.py
```

The CLI exposes only:

```text
python -m neurodecodekit.fmsr1_admission_cli plan
python -m neurodecodekit.fmsr1_admission_cli qualify-generated
```

There is no live, execute, witness, URL, host, credential, source-path, or
output-path option. Neither module imports a network transport or adds a base
dependency. Before a later official generated run, `qualify-generated` must
find a separate exact implementation-activation record. That record is absent
in this milestone, so the runner refuses before creating an attempt root.

## What The Validator Does

The generated validator now binds rather than trusts its own evidence:

- one exact closed-authority profile;
- two exact source-global revision fixtures and three exact ordered opaque
  snapshot fixtures across the five registered source indexes;
- exact generated issuer, host, revision, extraction, request, scope, page,
  response-body, pagination, and ledger identities;
- one exact generated GitHub run-attempt profile and exactly two generated
  response envelopes;
- exact API media/version, request headers, host, port, peer, TLS, repository,
  owner, workflow, run, head, attempt, and required-job identities; and
- one legal `marker_durable -> CI_W0_success -> source_contact_started`
  ordering transcript.

The response type carries explicit generated provenance and rejects captured
or real-response provenance. It also rejects alternate hosts or ports,
credential or conditional request headers, changed peers, nonidentity content
encoding, stale cache evidence, redirects, duplicate singleton headers, and
ambiguous job identity.

## Strict Failure And Report Contracts

All 82 preregistered mutations now exercise validators and land on their exact
13 frozen refusal routes. The implementation rejects duplicate JSON keys at
any depth, floating or nonfinite numbers, BOM/NUL/invalid UTF-8, trailing JSON,
container/depth overflow, Unicode-confusable security tokens, mixed evidence
modes, self-signed revision/snapshot drift, CI drift, proxy/custom-CA state,
resource overruns, and forbidden operation counters.

The public report validator binds every refusal name and route in frozen order,
the replay digest shape, exact nested fields, marker and fsync counts, finite
runtime/RSS, zero forbidden-operation counters, warnings, unavailable fields,
claim boundary, and stabilized byte count. Arbitrary nested material cannot be
hidden under an otherwise harmless key.

## Filesystem And One-Shot Boundary

Generated marker writes are limited to an actively registered
qualification-created root. An arbitrary caller path refuses. The marker uses
`O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW`, mode `0600`, exact canonical bytes,
file `fsync`, parent-directory `fsync`, and inode/device verification across
the no-follow parent open.

A later official generated invocation will first create the fixed Git-ignored
root `.codex_work/fmsr1-r1-g-v0-official` and its durable marker. If the root
already exists, the invocation refuses before any replay. A failed attempt
therefore remains consumed, and no retry can be mistaken for the registered
one-shot. Only tiny generated audit bytes may remain there; no real, captured,
source, payload, or model material can enter this implementation.

## Local Component Evidence

The official `qualify-generated` runner was not invoked. Reversible component
checks passed locally:

```text
focused unit tests:       28 passed
frozen refusal matrix:    82 / 82 passed
distinct refusal routes:  13
Ruff:                     passed
Python compilation:       passed
CLI help and plan:        passed
```

These checks used one numerical thread where applicable and created only
ephemeral generated fixtures. The exact full-suite and remote-CI measurements
belong to the implementation commit closeout, not this local draft record.

## Independent Review

Independent adversarial review initially rejected the draft for five reasons:
an unenforced qualification gate, self-signed evidence, scripted refusal
raises, arbitrary marker paths, and an underconstrained public report. The
implementation was changed to address all five before commit. The final
read-only re-review returned `ACCEPT` with no remaining blocker. It specifically
verified that wrong protocol, stage, execution ordinal, or generated flag
refuses before `consumed.json` is opened or created.

## Next Ordered Gate

1. run the complete local verification matrix;
2. commit and push this exact implementation;
3. require both GitHub `main` jobs to pass;
4. add a separate activation record binding that exact implementation commit,
   CI run, jobs, and code/test hashes;
5. commit, push, and remotely green that activation without running the
   qualification;
6. run `qualify-generated` exactly once under the frozen resource environment;
7. commit its aggregate result, then add a proof-only closeout without rerun;
8. stop before any `R1-W` live witness packet.

No GitHub API call, official-index contact, candidate metadata, header,
payload, signal, target, model, score, provider, stream, device, release, or
scientific claim is opened by this implementation.

Engineering capability added: a dependency-free, activation-gated, generated-only validator now distinguishes exact revision, snapshot, CI, ordering, durability, and resource evidence from 82 malformed or ambiguous counterexamples without exposing live transport.

Scientific claim not established: no real source or human neural data was accessed, so this implementation establishes no source authenticity, neural advantage, motor-cortex attribution, intention decoding, unseen-person generalization, thought or language decoding, or live operation.
