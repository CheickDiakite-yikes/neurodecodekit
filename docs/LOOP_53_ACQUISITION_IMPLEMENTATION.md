# Loop 53 Acquisition Implementation

Date: 2026-07-17

Status: **Implemented locally; fixture qualified; remote-green implementation gate pending**

Implementation registry:
`registries/loop53_acquisition_implementation.v0.json`

Frozen contract:
`registries/loop53_fresh_eeg_acquisition_contract.v0.json`

Authorization decision:
`registries/loop53_authorization_decision.v0.json`

## Added Capability

NeuroDecodeKit now has one dependency-free, fail-closed executor for the exact
Loop 53 bundle and one CLI surface:

```bash
neurodecode loop53-acquire-s20
neurodecode loop53-acquire-s20 --help
```

The default command is a plan only. It verifies the public contract and
authorization hashes, prints the four frozen paths and resource caps, and does
not stat a registered S20 root or contact the network.

`--execute` is available only with a full current implementation commit and its
successful push and pull-request CI run IDs. The runner also requires the
authorization commit to be an ancestor, no tracked worktree changes, and these
thread controls to equal `1`:

```text
OMP_NUM_THREADS
OPENBLAS_NUM_THREADS
MKL_NUM_THREADS
VECLIB_MAXIMUM_THREADS
NUMEXPR_NUM_THREADS
```

This implementation milestone does not execute that mode. The real invocation
remains blocked until this implementation is committed, pushed, and green in
both workflows.

## Ordered Executor

The implementation follows the preregistered sequence:

1. Verify the immutable contract and authorization decision SHA-256 values.
2. Verify the implementation Git identity and one-thread environment.
3. Refuse any collision or symlink before creating the registered roots.
4. Verify free disk and one-filesystem atomic-promotion support.
5. Reverify the pinned revision, public/gated/disabled state, license, and four
   exact paths, sizes, Git OIDs, LFS SHA-256 values, and Xet identities.
6. Start one four-file payload invocation only after every metadata check passes.
7. Stream each payload in 1 MiB binary chunks while enforcing bytes, disk,
   runtime, and RSS caps.
8. Reopen each temporary file only for an opaque sequential size/hash pass.
9. Reject extra, missing, symlink, or non-regular staging entries.
10. Create a new isolated final parent and atomically rename the complete bundle.
11. Write exactly one machine manifest and one human receipt under the 1 MiB cap.
12. Stop before Loop 54.

The module contains no MNE, NumPy, SciPy, Torch, MAT, BrainVision, signal, event,
target, cache, split, model, training, inference, or scoring interface.

## Failure Behavior

Metadata drift parks before the first payload request. Transfer, byte, hash,
resource, or membership failure parks without promoting a partial bundle.
Cleanup iterates only over invocation-created temporary files and directories;
it never recursively deletes an unregistered tree. Existing paths are refused,
not opened, overwritten, renamed, or deleted.

Once the private receipt root exists, another invocation is refused. A pass or
park consumes the single registered execution; there is no retry path.

## Offline Qualification

The test fixture substitutes four tiny opaque binary streams containing invalid
UTF-8. It uses the same four roles and path topology but no real S20 bytes,
metadata call, or registered local path.

Covered cases include:

- deterministic four-file transfer, local SHA-256, Git blob SHA-1, and LFS
  SHA-256 verification;
- invalid UTF-8 payloads succeeding without decode or parse;
- revision, license, path membership, size, OID, LFS, and Xet mismatches;
- abort-before-payload behavior on metadata mismatch;
- transfer byte cap and receipt output cap enforcement;
- hash mismatch cleanup without promotion;
- symlink and destination collision refusal;
- mandatory one-thread controls;
- explicit zero counters for every forbidden operation;
- explicit warnings, unavailable fields, metrics, and claim ceiling; and
- refusal of a second invocation.

Local qualification passed 17 executor tests, 6 implementation-registry tests,
and 51 focused Loop 53 tests. The complete suite passed 1,056 tests with 3
expected skips in 30.623 seconds, compared with the 1,033-test pre-change
baseline. Ruff, compile, every registry JSON parse, CLI help, the no-stat/no-
network dry run, and `git diff --check` also passed.

The complete test process reached 568,688,640 bytes peak RSS because it loads
the repository's optional ML stack. That is not a Loop 53 execution metric and
does not qualify the 512 MiB acquisition cap; the registered executor measures
and enforces its own process RSS during the future invocation.

## Measured Implementation Boundary

```text
real metadata calls:                         0
real payload requests:                       0
real network payload bytes:                  0
registered S20 path stats or hash reads:     0
header / marker / signal / MAT reads:        0 / 0 / 0 / 0
target or label reads:                       0
cache / split operations:                    0 / 0
model / inference / training / scoring:      0 / 0 / 0 / 0
generated persistent experiment bytes:       0
```

The source and tests are implementation artifacts, not generated experiment
output. Temporary synthetic test trees are removed by their test contexts.

## Claim Boundary

Engineering capability added: one strict standard-library path can acquire,
opaque-hash, atomically promote, and privately receipt the exact registered
four-file bundle after the two remote-green gates.

Scientific claim not established: this implementation has not contacted or
opened S20 and establishes no BrainVision readability, EEG signal quality,
trial or target validity, neural advantage, decoding accuracy, generalization,
end-to-end latency, portable hardware, at-home use, or clinical utility.
