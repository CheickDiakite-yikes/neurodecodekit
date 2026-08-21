# MARC2-VR13P R4 Private Discriminator Implementation

Date: 2026-08-20

Lane: `MARC2-VR13P`

Status: **Stage 1 implemented and generated-qualified; private execution remains
closed until this exact implementation and a separate proof closeout are both
remotely green**

Machine implementation:
`registries/marc2_r4_private_discriminator_implementation.v0.json`

Measured generated result:
`docs/MARC_2_R4_PRIVATE_DISCRIMINATOR_GENERATED_RESULT.md`

## Implemented Interface

`src/neurodecodekit/datasets/marc2_r4_private_discriminator.py` adds four fixed
surfaces:

- `plan`: reads only tracked proof artifacts and describes the frozen bounds;
- `qualify`: runs the generated 32-path matrix, temporary fixed-path state
  machine, and direct refusal inventory;
- `inspect`: reads only the future aggregate-safe registered report; and
- `execute`: refuses before readiness or private-path access until the exact
  implementation proof is present and remotely green.

No surface accepts a source path, output root, URL, threshold, route, retry,
resume, fallback, or arbitrary execution override.

## One-Call Discrimination

For each source, the wrapper:

1. snapshots the canonical structural source bytes;
2. calls the exact green VR12A adapter once;
3. on refusal only, calls VR13A's exact green residual mapper once;
4. maps VR13A R1-R7 to private VR13P R2-R8;
5. maps VR12A success to generated G1 or private R1; and
6. verifies that the source was not mutated.

The wrapper neither imports nor calls a consumed VR11P/VR12P executor. It
binds the green VR12A and VR13A modules plus their implementation/result
records by exact SHA-256.

## Fixed-Path State Machine

Generated qualification creates only a temporary root and exercises the same
certificate, exclusive marker, strict JSON, private-manifest, aggregate-report,
mode, collision, symlink, and output-cap helpers intended for the registered
execution. The temporary root is deleted by its context manager and retained
generated output is zero.

The future public `execute` path is fixed to the registered readiness,
structural source, output root, marker, private cohort manifest, and aggregate
report paths. It remains blocked by `remote_implementation_proof: null`.

## Refusal And Privacy Coverage

Eighty-one direct mutations cover:

- malformed, duplicate-key, non-finite, and non-UTF-8 JSON;
- missing or non-one thread variables;
- decision, proof, user-message, authority, cap, and route drift;
- every forbidden public-output key;
- runtime, memory, and output cap violations; and
- absolute/traversing paths, symlink parents, output collisions, and exclusive
  write collisions.

Aggregate output contains no predicate, failed value, row, member, path,
participant, session, run, companion, source hash, signal, event, target,
label, prediction, or score. A private source-exact cohort manifest is possible
only on future R1 and is mode `0600`.

## Resource Boundary

- CPU threads / workers / numerical jobs: `1 / 1 / 1`;
- generated runtime cap: 60 seconds;
- private runtime cap: 650 seconds;
- peak RSS cap: 256 MiB;
- free-disk floor before private execution: 15 GiB;
- private source: exactly 418,755 bytes and one content open;
- combined output cap: 2 MiB;
- network, new payload, archive-member, signal, and target bytes: zero; and
- retry, rerun, and resume: zero.

## Next Gate

Commit, push, and green this exact implementation. Then bind its exact owned
artifacts and CI identifiers in a separate proof-only closeout, commit and push
that closeout, and require both jobs to pass. Only afterward may the one
registered private structural execution begin.

Engineering capability added: a fixed, one-call structural discriminator can
separate all seven residual blocker classes or freeze an R1 cohort without
opening neural payloads.

Scientific claim not established: generated qualification is not neural data
and establishes no neural effect, decoding accuracy, language decoding, live
decoding, or thought-to-text capability.
