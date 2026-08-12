# MARC-1 Output-Capability Recovery Implementation

Date: 2026-08-12

Lane: `MARC1-OP1`

Status: **Generated-only implementation qualified; registered path probe and
registered generated closeout remain closed until this exact implementation is
committed, pushed, and both required CI jobs are green**

Machine record:
`registries/marc1_output_capability_recovery_implementation.v0.json`

## Why This Exists

Consumed lane MARC1-PG1 performed generated pagination and cohort work before
discovering that its `/tmp` output parent was a symlink. It therefore consumed
its one registered closeout at `MARC1PG-F07` without producing an artifact.

MARC1-OP1 repairs that operation order without reopening the consumed lane.
Safe output authority is now acquired first. Only then can the wrapper read a
contract, verify source hashes, defer-import pure pagination helpers, build a
fixture, select a cohort, or allocate output bytes.

This is process hardening on the same controlled-neural-effect to held-out-
language-decoding path. It is not a scientific pivot.

## Green Contract Anchor

Frozen contract commit
`baade51146309bd3b3fa6c1750a36482669a0ff2` passed:

```text
CI run:                 31597291352
Base Python job:        94115807028
Optional Neuro job:    94115807008
contract SHA-256:       2fe17a263a8c923c2a7af76dbba0c6422eacb601b7668de987ef0d53485c5cb6
```

Both required jobs were green before implementation began.

## Added Surface

The additive dependency-free module is:

`src/neurodecodekit/datasets/marc1_output_capability_recovery.py`

It exposes four commands:

```text
plan
preflight
qualify
inspect
```

It has no network client, live URL, source-data path, consumed-root name,
payload decoder, signal reader, target interface, model, scorer, retry,
fallback, automatic pagination, or release interface.

The consumed `marc1_versioned_pagination` module is not imported at module
scope. It is hash-verified and defer-imported only after output capability
acquisition. The wrapper never calls:

```text
qualify_generated_pagination
_assert_new_output_directory
main
```

The consumed source remains byte-identical at SHA-256
`3dc5f4fdf5792040f153797d708cf27cd8ece8e4dc40b3a0eeaba86071724228`.

## Capability Mechanics

`OutputCapability` is a process-local, deliberately nonserializable object. It
holds:

```text
parent directory descriptor
parent device, inode, and mode
normalized output basename
two-filename allowlist
acquisition sequence number
operation ledger
```

Acquisition performs the following sequence:

1. Validate an absolute, normalized, non-root lexical path with no `.` or
   `..` component.
2. Require `dir_fd`, `O_DIRECTORY`, `O_NOFOLLOW`, and no-follow stat support.
3. `lstat` every ancestor and reject any symlink or non-directory.
4. Open the parent with `O_RDONLY | O_DIRECTORY | O_NOFOLLOW`.
5. Require the opened device, inode, and type to match the prior `lstat`.
6. Require the output child to be absent through parent-relative no-follow
   stat.

Immediately before writing, the wrapper rechecks the named parent and held
descriptor identities and rechecks child absence. It creates the child with
parent-relative `mkdir`, opens it with `O_DIRECTORY | O_NOFOLLOW`, then writes
exactly two files through the child descriptor using
`O_CREAT | O_EXCL | O_NOFOLLOW`:

```text
marc1_output_capability_qualification.v0.json       mode 0644
marc1_output_capability.generated.private.v0.json  mode 0600
```

The public report is opened and inspected once without opening its private
peer. Both files are unlinked through the held child descriptor, and the empty
directory is removed through the held parent descriptor before qualification
returns. There is no absolute-path file write.

## Generated Semantics

After capability acquisition, the wrapper composes only hash-bound pure
helpers from the consumed pagination module. It retains:

```text
explicit query:                  page=1&page_size=1000
Wrist rows:                      55
participant/supplement rows:     45 / 10
declared Wrist bytes:            3,683,416,050
selected participants/source:    12
Freewill bundles/members:        72 / 288
private selection rows:          300
fit/held-out overlap:            0
```

Selection remains independent of targets, labels, quality, payload size,
checksums, and outcomes. Subject-level rows exist only in the temporary mode-
0600 private manifest and are removed before return.

## Adversarial Qualification

The implementation passes all six accepted cases:

```text
2 path-capability cases
4 generated transport/order cases
```

It also passes all 32 frozen refusal mutations:

```text
pre-capability/path/order refusals:  19
post-capability/semantic refusals:   13
failure routes covered:               8
acceptance gates passed:             20 / 20
```

The matrix covers relative and malformed paths, symlink ancestors, missing or
non-directory parents, existing and dangling children, absent primitives,
device/inode disagreement, closed descriptors, output races, child-open
disagreement, early work, proof and hash drift, forbidden consumed calls,
partial pagination, target-like fields, split overlap, output allowlist drift,
overwrite attempts, resource breaches, replay drift, and second invocation.

## Final Development Measurement

One final nonregistered qualification used
`/private/tmp/neurodecodekit-marc1op1-development-final-v3-20260812`. That
temporary path was not the registered closeout path and was removed by the
wrapper.

```text
route:                              MARC1OP-G1
accepted cases:                     6 / 6
refusals:                           32 / 32
acceptance gates:                   20 / 20
generated input bytes:              1,019,776
public report bytes:                8,499
private manifest bytes:             175,674
combined output / disk bytes:       184,173
runtime:                            0.09579495782963932 seconds
reported peak RSS:                  33,767,424 bytes
external wall time:                 0.16 seconds
external maximum RSS:               33,800,192 bytes
public report SHA-256:               6717044dad76e497d5a1a21f0f32ad02258ece6af973e6dd5085e31a00a7af02
private manifest SHA-256:            e835e41a2494268c7795ca72e2e6ef9f01d0494767c9c70b4e76c382c6e609b4
output remains after return:         no
```

The public report's final ledger records ten bound repository reads, two
contract loads, one deferred import, two generated fixtures, 1,282 generated
rows, four selections, one capability revalidation, exactly two writes, one
public inspection, two unlinks, and one directory removal.

Every real/private dataset, live metadata, payload, signal, target, model,
training, prediction, scoring, provider, hardware, other-project, retry, and
claim counter is zero.

Development and unit-test fixture invocations are not registered evidence and
have no one-shot scientific status. The registered path
`/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812` was not
statted, created, reserved, preflighted, or qualified during implementation.

## Verification

Before the implementation record was frozen:

```text
focused behavior tests:                24 / 24
implementation-record tests:           12 / 12
all MARC tests:                        587 / 587
MARC runtime / external peak RSS:      6.491 sec / 67,076,096 bytes
dependency-light suite:                2,726 passed / 204 skipped
dependency-light runtime / peak RSS:   22.538 sec / 254,607,360 bytes
optional-neuro suite:                  2,797 passed / 35 skipped
optional-neuro runtime / peak RSS:     61.192 sec / 738,394,112 bytes
```

The implementation adds 36 tests and zero skips relative to the green contract
milestone. Repository-wide Ruff, source and test compilation, all 191 registry
JSON parses, CLI help/plan/preflight/qualify/inspect checks, artifact hash
replay, and `git diff --check` pass. CLI checks used only generated,
nonregistered paths and removed every temporary output.

## Next Gate

Commit and push this exact implementation, then require both CI jobs to pass.
Only after that proof may the exact registered path receive one path-only
`preflight` invocation. Only `MARC1OP-P0` opens one immediately following
registered generated qualifier. Any refusal consumes and parks the lane
without retry, rerun, substitution, or amendment.

A live metadata response remains a separate Tier C action after a green
registered generated result. No current authorization opens it.

## Claim Boundary

Engineering capability added: NeuroDecodeKit can acquire safe output authority
before experiment work, preserve frozen pagination and cohort semantics, bind
all writes to one held parent identity, inspect only the public result, and
clean up exactly.

Scientific claim not established: no live dataset body, neural signal, target,
model prediction, score, language decoding, or thought-to-text result was
produced.
