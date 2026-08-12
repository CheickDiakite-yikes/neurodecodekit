# MARC-1 Output-Capability Recovery Preregistration

Date: 2026-08-12

Lane: `MARC1-OP1`

Status: **Generated-only contract frozen; implementation and execution remain
closed until their exact preceding milestones are remotely green**

Machine contract:
`registries/marc1_output_capability_recovery_contract.v0.json`

## Objective

Qualify one additive generated-only wrapper that obtains safe output authority
before any repository read, contract load, deferred pagination import, fixture
construction, selection, or output allocation. Then prove that the unchanged
explicit-page pagination and target-free selector execute through that held
capability without calling or modifying the consumed MARC1-PG1 qualifier.

This is a process recovery on the same scientific path. It does not alter or
reopen MARC1-PG1 and does not contact a source.

## Green Research Anchor

Artifact-only research `d02830b95c76bc428a297c6415db933452af5cbb`
passed Base Python job `94111539407` and Optional Neuro Readers job
`94111539431` in CI `31595996923` before this contract was frozen.

Bound research artifacts:

- document SHA-256
  `04b5886ee164f55b361eb1fb3520cabd013ca7b2ec2a8b5e168055c9909089ac`;
- registry SHA-256
  `1bf34df48992bc0574b6b1bd4d14a4f1292f65b74371101dfcf5c48fc89bfd4c`;
- consumed MARC1-PG1 result SHA-256
  `b99be5d82e1f49f064cf17e4a7b2d6a21e36d89cebc78b133136b181fb4bdcf2`;
- consumed pagination source SHA-256
  `3dc5f4fdf5792040f153797d708cf27cd8ece8e4dc40b3a0eeaba86071724228`;
- candidate capability policy SHA-256
  `6412dd0cdfabf2b96d0c5ebf2d1e2dadb4fc3e8fe5eed6ac762524a5c9881054`.

MARC1-PG1 remains consumed. These hashes permit validation and pure-helper
composition only; they do not authorize its qualifier to run again.

## Exact Future Surface

Only after this contract's exact commit is pushed and both CI jobs are green
may one additive standard-library module be implemented at:

`src/neurodecodekit/datasets/marc1_output_capability_recovery.py`

It may expose only:

- `plan`: print the zero-access contract summary;
- `preflight`: acquire and release one output capability without repository or
  fixture access;
- `qualify`: re-acquire capability first, then run generated qualification;
- `inspect`: inspect one aggregate generated outer report without opening its
  private peer.

There may be no network client, URL, local source input, consumed-root name,
payload, signal, target, model, scorer, retry, fallback, automatic pagination,
or real-data interface.

The module must not import `marc1_versioned_pagination` at module scope. After
capability acquisition it may defer-import the exact hash-bound source and call
only allowlisted pure helpers. It must not call:

```text
qualify_generated_pagination
_assert_new_output_directory
main
```

It must not modify the consumed source file.

## Capability Contract

The future `OutputCapability` is process-local and nonserializable. It binds:

```text
open parent directory descriptor
parent device, inode, and type
normalized output basename
allowlisted public and private output filenames
acquisition sequence number
```

Acquisition is the first callable operation in `preflight` and `qualify`.
Before it succeeds, counters for repository reads, contract loads, deferred
imports, fixtures, rows, selections, and output bytes must all be zero.

The lexical path must be absolute, normalized, non-root, free of `.` and `..`,
and have one nonempty basename. Every ancestor through the parent is checked by
`lstat`; any symlink or non-directory refuses. Required `dir_fd`,
`O_DIRECTORY`, and `O_NOFOLLOW` support must be present.

The parent is opened with `O_RDONLY | O_DIRECTORY | O_NOFOLLOW`; `fstat` must
match the prior parent device/inode/type. The child must be absent under a
parent-relative no-follow stat. The descriptor remains open through work.

Immediately before writing, the implementation must revalidate parent identity
and child absence. It then creates and opens the output directory relative to
the held parent descriptor and writes exactly two files with
`O_CREAT | O_EXCL | O_NOFOLLOW` relative to the held output descriptor:

```text
marc1_output_capability_qualification.v0.json
marc1_output_capability.generated.private.v0.json
```

No absolute-path file write is permitted. Inspection reads only the public
file. Cleanup removes only those two files and the empty directory through the
held descriptors.

## Exact Registered Path And Sequence

The one future local sequence is bound to:

```text
/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812
```

After exact implementation green proof:

1. one registered path-only `preflight` probe runs with one thread;
2. if and only if it reaches `MARC1OP-P0`, one `qualify` invocation immediately
   re-acquires the capability and runs;
3. any preflight refusal parks the lane without path substitution or retry;
4. capability acquisition consumes the one generated qualifier;
5. any later failure parks the lane without retry, rerun, or amendment; and
6. successful output is measured, inspected once, hash-bound, and removed.

The exact path was not statted, created, or reserved while freezing this
contract.

## Accepted Generated Cases

Six cases must pass during implementation qualification:

1. regular absolute parent with absent child;
2. deeper all-regular ancestor chain with absent child;
3. canonical rows with absent `Content-Encoding`;
4. reversed rows with absent `Content-Encoding`;
5. canonical rows with identity `Content-Encoding`; and
6. reversed rows with mixed-case identity `Content-Encoding`.

The four response cases must produce identical semantic and selection hashes.

## Exact Refusal Matrix

All 32 mutations must refuse:

1. relative path;
2. empty path or basename;
3. root destination;
4. `.` or `..` component;
5. non-normalized path;
6. missing parent;
7. non-directory parent;
8. immediate-parent symlink;
9. earlier-ancestor symlink;
10. existing output file;
11. existing output directory;
12. existing output symlink;
13. dangling output symlink;
14. missing required standard-library primitive;
15. `lstat`/open device or inode disagreement;
16. closed, replaced, or retyped parent descriptor;
17. output appears after capability acquisition;
18. parent-relative mkdir or child-open disagreement;
19. repository read, contract load, deferred import, fixture, selection, or
    output operation before capability acquisition;
20. wrong green research proof;
21. wrong consumed-result proof;
22. wrong capability-policy hash;
23. eager or forbidden consumed-pagination import/call;
24. wrong pagination query;
25. ten-row partial inventory;
26. target-like field;
27. split overlap or selection identity drift;
28. output filename allowlist drift;
29. nonexclusive write or overwrite attempt;
30. runtime, RSS, input, output, or disk cap breach;
31. nondeterministic public or private replay; and
32. second registered preflight or qualifier invocation.

The ordered routes are:

```text
MARC1OP-F00  green proof, artifact, source, or policy mismatch
MARC1OP-F01  lexical path identity failure
MARC1OP-F02  ancestor, primitive, or capability-acquisition failure
MARC1OP-F03  held-capability revalidation or race failure
MARC1OP-F04  operation-order, eager-import, or consumed-call failure
MARC1OP-F05  pagination, semantic, target-firewall, or selection failure
MARC1OP-F06  output allowlist, exclusive-write, privacy, or resource failure
MARC1OP-F07  replay, cleanup, second invocation, retry, or rerun failure
MARC1OP-P0   registered path-only preflight passed with zero early operations
MARC1OP-G1   generated capability, pagination, selection, output, and cleanup pass
```

## Unchanged Semantic Identity

The generated full stack must retain:

```text
query:                         page=1&page_size=1000
Wrist rows:                    55
participant archives:         45
supplementary rows:            10
declared Wrist bytes:          3,683,416,050
selected participants/source: 12
Freewill run bundles/members:  72 / 288
private selection rows:        300
fit/held-out overlap:          0
```

Selection remains target-, quality-, size-, checksum-, and outcome-free.

## Acceptance Gates

`MARC1OP-G1` requires all 20 gates:

1. exact green research proof;
2. exact contract, result, consumed-source, and policy hashes;
3. exact registered path identity;
4. no module-scope consumed-pagination import;
5. capability acquisition is first inside preflight and qualify;
6. every ancestor is a real directory and no-follow checked;
7. held parent device/inode/type matches before work and write;
8. output absence passes at acquisition and immediately before creation;
9. all 19 pre-capability mutations refuse with zero early counters;
10. all 13 post-capability mutations refuse under their registered routes;
11. all six accepted cases pass;
12. four transport cases have identical semantic and selection hashes;
13. exact 55-row identity and 54/56/10-row refusals pass;
14. exact target-free 12+12 cohort and split binding passes;
15. consumed qualifier calls and consumed-source modification are zero;
16. exactly two allowlisted files use parent-relative exclusive writes;
17. public/private separation and one public inspection pass;
18. deterministic public and private hashes replay;
19. all resource and zero-access counters pass; and
20. exact generated cleanup passes.

## Resource And Output Caps

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
runtime:                                  30 seconds
peak RSS:                                 256 MiB
generated input:                          2 MiB
combined generated output:                2 MiB
incremental disk:                         4 MiB
network bytes:                            0
real/private input bytes:                 0
```

The future registered preflight emits no file. The generated closeout may
write only the two temporary allowlisted files under the caps above.

## Evidence Order

1. Commit, push, and green this exact contract.
2. Implement only generated/mock capability and wrapper behavior.
3. Commit, push, and green the exact implementation.
4. Run one registered path-only preflight.
5. Only after `MARC1OP-P0`, run one registered generated qualifier.
6. Commit, push, and green the aggregate result.
7. Only then prepare an all-false Tier C request for one future metadata body.

No current message opens step 7. Real/private metadata, dataset requests,
payloads, signals, targets, models, scores, hardware, release, and scientific
claim upgrades remain unauthorized.

## Contract Verification

Before commit, the frozen contract passed:

```text
focused contract tests:                12 / 12
all MARC tests:                        551 / 551
dependency-light suite:                2,690 passed / 204 skipped
dependency-light runtime:              21.616 seconds
dependency-light external peak RSS:    254,148,608 bytes
optional-neuro suite:                   2,761 passed / 35 skipped
optional-neuro runtime:                60.171 seconds
optional-neuro external peak RSS:      771,571,712 bytes
```

The first optional-neuro invocation reached an 813,596,672-byte external peak
RSS and failed two older process-wide peak-RSS rehearsal assertions. Both
tests passed together in a fresh focused process, and the complete clean
second invocation passed at the measurements above. This contract adds twelve
tests and zero skips relative to the preceding green research milestone.

Ruff, source and test compilation, all 190 registry JSON parses, artifact
hash replay, and `git diff --check` are final commit gates. Contract
verification performed zero registered-path, fixture, qualifier, consumed-
source, network, private-input, payload, signal, target, model, prediction,
score, provider, hardware, or other-project operations.

## Claim Boundary

Engineering capability proposed: one capability-first wrapper can preserve the
frozen pagination and cohort mechanics while proving unsafe destinations spend
zero experiment operations and all writes remain bound to one parent identity.

Scientific claim not established: this contract authorizes no dataset body,
neural signal, target, prediction, score, language decoding, or thought-to-text
claim.
