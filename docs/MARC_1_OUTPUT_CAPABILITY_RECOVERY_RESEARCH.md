# MARC-1 Output-Capability-First Recovery Research

Date: 2026-08-12

Lane: `MARC1-OP1`

Status: **Artifact-only recovery design; no implementation, fixture, source
request, or closeout authorized by this record**

Machine record:
`registries/marc1_output_capability_recovery_research.v0.json`

## Research Question

How can a generated closeout prove that its output destination is safe before
it spends any contract read, fixture construction, selection, or other
experiment operation?

This is a narrow process-recovery question. It does not change the exact
`page=1&page_size=1000` request, 55-row semantic identity, target firewall,
12+12 cohort selection, resource caps, or scientific claim boundary.

## Evidence Boundary

Consumed result `a4dcaea784f4c3a62547fd4f73bb3e2a5528100a` passed Base
Python job `94107907276` and Optional Neuro Readers job `94107907246` in CI
`31594881048` before this research began.

That result establishes:

- the one `MARC1-PG1` closeout is consumed at `MARC1PG-F07`;
- `/tmp` was presented as a symlink to `private/tmp`;
- both generated inventories, four accepted selections, and a generated
  private manifest had already been constructed in memory before preflight;
- zero output, network, real/private, payload, signal, target, model, or score
  bytes or operations occurred; and
- no corrected-path invocation, retry, rerun, or live packet is open.

This research reads only committed source and aggregate records plus local
standard-library capability metadata. It does not reopen the failed output
path, invoke `qualify`, build a fixture, or access a dataset endpoint.

## Root Cause

The failed implementation asks the right safety question at the wrong time.
Its orchestration order is:

```text
contract -> generated inventories -> four selections -> private bytes
         -> output-path preflight -> refusal matrix -> write
```

The path guard prevented unsafe output, but it could not preserve the
registered experiment budget because generated work had already begun. The
recovery must make safe output authority a prerequisite capability:

```text
output capability -> contract -> generated work -> capability recheck -> write
```

## Candidate Capability Architecture

`MARC1-OP1` should use a small standard-library `OutputCapability` object. It
contains only an open parent-directory descriptor, parent device/inode
identity, normalized output basename, and permitted filenames. The descriptor
is process-local and never serialized.

Acquisition must be the first operation inside the future qualification entry
point:

1. require one absolute normalized path with no `.` or `..` components;
2. require a nonempty final basename and forbid root as the destination;
3. `lstat` every existing ancestor from root through the immediate parent;
4. reject any symbolic link, non-directory ancestor, or unavailable parent;
5. open the immediate parent with `O_DIRECTORY | O_NOFOLLOW`;
6. compare `fstat` device/inode/type with the prior `lstat` identity;
7. require the output basename to be absent using parent-relative `stat` with
   `follow_symlinks=False`; and
8. retain the parent descriptor as the capability.

Only after step 8 may the implementation read a repository artifact, load a
contract, import the consumed pagination helper module, construct generated
rows, run selection, or allocate output bytes.

Before output creation it must:

1. re-`fstat` the held parent descriptor and match device/inode/type;
2. require the output basename to remain absent;
3. create the output directory parent-relatively with `mkdir(..., dir_fd=fd)`;
4. open the new directory using `O_DIRECTORY | O_NOFOLLOW`;
5. create allowlisted files with `O_CREAT | O_EXCL | O_NOFOLLOW` relative to
   that directory descriptor;
6. measure, inspect, and hash the generated outputs; and
7. remove only those allowlisted files and the empty generated directory via
   their held descriptors.

This is capability-oriented rather than path-oriented: later work acts through
the already verified directory identity instead of trusting the same string a
second time.

## Local Feasibility Observation

Dependency-light Python `3.14.6` on the current macOS host reports:

```text
O_DIRECTORY = 1048576
O_NOFOLLOW  = 256
dir_fd support: open, mkdir, stat, unlink, rmdir
```

This is a local engineering observation, not a portability guarantee. A future
implementation must feature-detect each required primitive and refuse before
repository or fixture access when one is unavailable. It may not silently
downgrade to string-only path checks.

## Frozen Candidate Policy

The canonical candidate policy is 672 ASCII bytes with SHA-256:

```text
6412dd0cdfabf2b96d0c5ebf2d1e2dadb4fc3e8fe5eed6ac762524a5c9881054
```

It binds:

- preflight before repository read, contract load, deferred pagination import,
  fixture construction, selection, and output write;
- exact local closeout destination
  `/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812`;
- one held parent capability and parent-relative create/write/cleanup;
- zero retry, network bytes, or real/private input bytes; and
- no change to the frozen pagination and selector semantics.

The exact destination is prospective. This research does not stat, create, or
reserve it.

## Required Generated Qualification

A later contract should require at least these accepted cases:

1. one regular absolute parent with an absent output child;
2. one deeper all-regular ancestor chain;
3. deterministic replay under the same lexical path shape; and
4. the unchanged pagination and selection stack after capability acquisition.

It should refuse at least these classes before generated work:

- relative, empty, root, dot-segment, or non-normalized paths;
- missing or non-directory parents;
- symlink at the immediate parent or any earlier ancestor;
- existing output file, directory, symlink, or dangling symlink;
- unavailable `dir_fd`, `O_DIRECTORY`, or `O_NOFOLLOW` support;
- `lstat`/open device or inode disagreement;
- parent descriptor closure, replacement, or type drift;
- output appearance between acquisition and creation;
- parent-relative `mkdir` or child-open disagreement; and
- any contract read, deferred pagination import, fixture row, selection, or
  output allocation observed before capability acquisition.

Post-capability mutations should separately refuse altered pagination proof,
request identity, semantic inventory, target firewall, selection, output
allowlist, exclusive write, resource cap, replay, and second invocation.

## Recommended Sequencing

1. Commit, push, and green this artifact-only research.
2. Freeze a generated-only `MARC1-OP1` contract with exact operation order,
   capability schema, paths, cases, refusals, routes, gates, and caps.
3. Commit, push, and green that contract.
4. Implement an additive wrapper without changing the consumed
   `marc1_versioned_pagination.py` file.
5. Prove generated preflight refusals spend zero contract/fixture operations.
6. Commit, push, and green the exact wrapper.
7. Run one registered generated closeout at the exact `/private/tmp` path.
8. Commit, push, and green its aggregate result.
9. Only then consider an all-false Tier C packet for one new metadata response.

No current or previous message opens step 9. Any live dataset response, private
manifest operation, payload acquisition, signal, target, model, or score
remains closed.

## Verification

Eleven focused research tests and all 539 MARC tests pass. The dependency-light
suite passes 2,678 tests with 204 expected skips in 21.491 seconds at
235,159,552-byte external peak RSS. The optional-neuro suite passes 2,749 tests
with 35 expected skips in 59.776 seconds at 765,181,952-byte external peak RSS.
Both complete suites add exactly eleven tests and zero skips over the green
consumed-result baseline.

Repository-wide Ruff, compilation, all 189 registry JSON parses, policy-hash
replay, artifact-hash checks, and `git diff --check` pass. Verification did not
invoke a qualifier, construct a fixture, or stat/create the prospective output
path.

## Same Research Path

This is not a pivot. MARC1-OP1 repairs the experiment-control layer needed to
select a trustworthy multimodal cohort. That cohort supports a cue-resistant
neural positive control, which supports held-out language decoding and the
long-term non-invasive thought-to-text objective.

Engineering capability proposed: a held directory capability can make safe
output authority the first prerequisite and keep all later writes bound to the
same verified parent identity.

Scientific claim not established: this artifact-only research accessed no
dataset response, neural signal, target, prediction, score, language decoding,
or thought-to-text evidence.
