# PhysioNet Motor Acquisition Implementation

Date: 2026-08-09

Status: **Implemented locally; fixture qualified; remote-green implementation gate pending**

Implementation registry:
`registries/physionet_motor_acquisition_implementation.v0.json`

Frozen contract:
`registries/physionet_motor_acquisition_contract.v0.json`

Authorization decision:
`registries/physionet_motor_acquisition_authorization_decision.v0.json`

## Green Authorization Parent

Authorization-only commit `00b91edd213112fd186711d06369ae4f836b2243`
passed Base Python job `93322699209` and Optional Neuro Readers job
`93322699259` in CI `31344104565` before implementation began.

No PhysioNet source metadata, registered local path, or EDF payload was touched
during this implementation milestone. All qualification used generated local
bytes and mocked request/response objects.

## Added Capability

NeuroDecodeKit now has one dependency-free, fail-closed executor for the exact
nine-file EEGMMIDB acquisition and one CLI surface:

```bash
neurodecode physionet-motor-acquire
neurodecode physionet-motor-acquire --help
```

The default command verifies the immutable contract and decision hashes and
prints only the nine paths, identities, and resource caps. It does not stat the
registered payload, temporary, or receipt roots and does not contact a source.

`--execute` additionally requires the full current implementation commit, its
successful CI run ID, and the successful Base Python and Optional Neuro Readers
job IDs. The runner verifies that HEAD is exact, the authorization commit is an
ancestor, tracked files are clean, and every registered thread environment
variable equals `1`.

This implementation commit does not execute the real mode. The one invocation
remains blocked until this exact tree is committed, pushed, and remotely green.

## Ordered Executor

The standard-library executor follows the frozen sequence:

1. Verify the contract and authorization-decision SHA-256 values.
2. Verify current Git identity, green-evidence fields, and all authorization
   allow and deny flags.
3. Refuse output collisions, traversal, symlinks, non-regular parents, low
   free space, high initial RSS, or a non-one-thread environment before source
   access.
4. Fetch only the registered dataset page, official checksum manifest, and MNE
   run-mapping page, then issue HEAD only for the nine exact EDF URLs.
5. Require exact version, DOI, public availability, license label, run mapping,
   paths, sizes, and official SHA-256 values before an EDF GET.
6. Reject every redirect and issue one no-retry GET for each exact EDF URL.
7. Stream bytes directly into an isolated temporary tree while enforcing
   metadata, payload, runtime, RSS, and allocated-disk caps.
8. Reopen each local EDF exactly once for opaque sequential size and SHA-256
   verification with no-follow file descriptors.
9. Reject missing, extra, symlink, non-regular, partial, size-drifted, or
   hash-drifted members without substitution or retry.
10. Create a new absent final parent and atomically rename only the complete
    verified nine-file directory.
11. Emit one machine manifest and one human receipt under 1 MiB combined.
12. Stop before EDF parsing, event extraction, split creation, model work, or
    work order 9.

The module imports no MNE, NumPy, SciPy, Torch, pyEDFlib, or EDF reader. Its
payload interface is binary streaming only.

## Failure Behavior

Metadata drift parks before the first EDF body request. A transfer, byte, hash,
membership, redirect, or resource failure parks without final promotion.
Cleanup walks only the exact list of temporary files and directories created by
that invocation; it never recursively removes or mutates a preexisting tree.

The receipt root is created before metadata access. Its existence, the final
root, or the temporary root refuses any second invocation. There is no retry,
resume, wildcard, sidecar, substitute, or alternate-host path.

## Offline Qualification

The fixture uses the same nine subject/run paths with tiny invalid-UTF-8 binary
payloads and generated SHA-256 identities. All transport responses are local
objects. Coverage includes:

- deterministic nine-file transfer, exact one-pass hashes, and atomic promote;
- dataset, DOI, license, task mapping, surface, path, size, checksum, and
  request-count drift before payload access;
- strict checksum-manifest and run-mapping parsers;
- redirect, unregistered-host, `.event`, substitution, and URL refusals;
- short transfer, payload cap, metadata cap, runtime cap, initial RSS, and free
  disk controls;
- hash mismatch and extra-member cleanup without partial promotion;
- preexisting-path and symlink refusal without mutation;
- exact zero counters for every forbidden operation;
- complete warnings, unavailable fields, metrics, hashes, and claim boundary
  in both receipts; and
- second-invocation refusal.

Twenty-three dedicated executor tests and 55 combined work-order-8 contract,
request, decision, and executor tests pass. Seven implementation-registry tests
bind the owned source, test, and documentation artifacts while treating the
shared CLI hash as historical implementation evidence. The same additive
historical-hash treatment repairs the consumed CML-v0 test without changing its
registry or result.

The complete one-thread suite passes 1,448 tests with 3 expected skips and 493
subtests in 44.21 seconds of pytest runtime and 45.73 seconds external wall
time. That is 30 additional passing tests over the 1,418-test green decision
baseline. The suite reached 598,622,208 bytes peak RSS because it loads the
repository's optional ML stack; this is verification overhead, not an
acquisition-execution measurement. The standard-library executor independently
enforces its frozen 268,435,456-byte process cap.

One earlier complete attempt correctly exposed the historical CML shared-CLI
assertion and also saw the existing isolated timing worker exceed its five-
second test timeout. The CML assertion received the evidence-preserving repair;
the exact timing test passed unchanged on focused replay and the final full
suite. Ruff, compile, JSON, CLI, and diff-hygiene results are recorded in the
implementation registry before this milestone is committed.

## Measured Implementation Boundary

```text
real source metadata requests / bytes:       0 / 0
real EDF payload requests / bytes:           0 / 0
registered PhysioNet path stats / opens:     0 / 0
EDF header / annotation / signal reads:      0 / 0 / 0
event-sidecar requests or reads:              0
task / target / label / trial reads:          0
cache / split operations:                     0 / 0
model / inference / training / scoring:       0 / 0 / 0 / 0
provider / stream / device / hardware:        0 / 0 / 0 / 0
work-order-9 runs / reruns:                   0 / 0
retained generated experiment bytes:          0
```

Source, test, registry, and documentation files are implementation artifacts,
not generated experiment output. Temporary fixture trees are removed by their
test contexts.

The maintainer's 10 GB data allowance is unused future headroom. It does not
amend this immutable nine-file, 23,248,224-byte execution.

## Claim Boundary

Engineering capability added: one strict standard-library path can reverify,
acquire, opaque-hash, atomically promote, and privately receipt the exact
registered nine-EDF bundle after the ordered remote-green gates.

Scientific claim not established: no real PhysioNet metadata or EDF operation
occurred during implementation, so EDF readability, event correctness, signal
quality, motor physiology, neural advantage, model accuracy, unseen-person
generalization, end-to-end latency, typing or language decoding, portable
hardware, home use, assistive value, and clinical utility remain unestablished.
