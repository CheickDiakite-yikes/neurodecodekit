# Loop 53 Fresh S20 EEG Acquisition Authorization Decision

Date: 2026-07-17

Status: **authorized after this record is tested, committed, pushed, and
remotely green; no implementation, download, or payload access exists yet**

Machine decision: `registries/loop53_authorization_decision.v0.json`

Frozen request: `registries/loop53_authorization_request.v0.json`

Frozen contract: `registries/loop53_fresh_eeg_acquisition_contract.v0.json`

## Exact User Decision

The maintainer supplied the registered sentence verbatim:

> Authorize the Loop 53 fresh S20 EEG acquisition implementation and one registered acquisition exactly as scoped in docs/LOOP_53_FRESH_EEG_ACQUISITION_PREREGISTRATION.md and registries/loop53_fresh_eeg_acquisition_contract.v0.json. I authorize metadata reverification for the pinned public revision; one bounded acquisition invocation for only the four named S20 session-2 block-2 files totaling exactly 96,090,264 bytes; opaque sequential size and integrity hashing; creation of one new isolated complete bundle; cleanup only of temporary files created by that invocation; and one manifest and receipt under 1 MiB using one CPU thread, one worker, 600 seconds, 512 MiB peak RSS, 128 MiB network payload, 256 MiB incremental disk, and at least 2 GiB free disk. I do not authorize parsing or interpreting VHDR, VMRK, EEG, or MAT content; reading headers, markers, signal samples, targets, labels, sentences, key events, channels, geometry, sampling, events, or trials; creating caches or splits; model or checkpoint access; inference; training; scoring; S7/S21/S24/S25 or raw FIF access; additional files, participants, substitutions, downloads, or reruns; language models; RW3; streams; devices; hardware; release; or scientific, decoding, real-time, portable, home-use, or clinical claim upgrades.

This is one exact Tier C decision for the already frozen acquisition-only
protocol. It does not authorize payload interpretation, another participant,
another file, another download, or any later Loop 54 content stage.

## Bound Evidence

```text
authorization parent: 3dcf70c734a9ba88801c5c5279f957fab938b1a9
registration commit:  bccd36790317b5f58ca62083c6b3019d1983176c
contract SHA-256:     bc7d86a1ce6ef3dc71dacca0af97cb5813df87620ac35d4f34ecd343f97e65ac
request SHA-256:      a9ef260f6f1ad7bb06899a6de82f6a715ec6f37b0ba264227414d44537604a9b
parent push CI:       29587058356
parent PR CI:         29587061539
```

The preregistration, contract, packet, request, and historical invariant tests
remain immutable snapshots. Their pending or false authorization fields remain
unchanged because this separate record captures the later decision.

## Exact Authorized Inventory

```text
repository / revision:       bcbl190626/SpanishBCBL / 88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684
subject / session / block:   S20 / 2 / 2
named files:                 4
expected final bytes:        96,090,264
acquisition invocations:     1
metadata reverification:     pinned revision and exact records only
payload verification:       opaque size, Git blob SHA-1, LFS SHA-256, content SHA-256
final bundle root:           data/loop53_s20_eeg/SpanishBCBL
manifest / receipt:          one each, combined under 1 MiB
content parse operations:    0
cache / split operations:    0 / 0
model / training / scoring:  0 / 0 / 0
additional files / reruns:   0 / 0
```

## Required Order

1. Test this decision against the immutable request and contract.
2. Commit, push, and obtain green push and PR CI for this authorization record.
3. Implement the dependency-light acquisition tool using synthetic fixture
   bytes only, without metadata or payload network access.
4. Commit, push, and obtain green push and PR CI for the implementation.
5. Verify one-thread settings, at least 2 GiB free disk, and collision-free,
   non-symlinked registered roots.
6. Reverify only the pinned public metadata and abort before payload transfer on
   any mismatch.
7. Run one bounded acquisition of the four exact files, hash their opaque bytes,
   promote only a complete verified bundle, and emit one bounded receipt.
8. Mark the protocol consumed or parked and stop before Loop 54.

No S20 path stat, metadata request, payload transfer, hash pass, content read,
or receipt may occur before the implementation commit is remotely green.

## Computer And Storage Boundary

```text
CPU threads / workers:       1 / 1
wall time:                   <= 600 seconds
peak RSS:                    <= 512 MiB
network payload:             <= 128 MiB
incremental disk peak:       <= 256 MiB
minimum free disk:           >= 2 GiB
generated manifest/receipt:  <= 1 MiB
final payload:               exactly 96,090,264 bytes
```

## Authorization-Only Measurements

```text
metadata calls / network bytes / downloads:          0 / 0 / 0
local S20 stat/hash/content reads:                    0 / 0 / 0
header / marker / signal / MAT / target reads:        0 / 0 / 0 / 0 / 0
cache / split / model / training / scoring runs:      0 / 0 / 0 / 0 / 0
stream / device / hardware operations:               0 / 0 / 0
generated experiment artifacts:                      0
end-to-end latency measured:                          false
```

## Claim Boundary

**Engineering capability authorized for testing:** one hash-bound,
resource-bounded implementation and one registered acquisition of the exact
four-file public S20 bundle may proceed through the ordered green gates.

**Scientific claim not established:** this decision is not an acquisition
result. Even a clean acquisition can establish only byte-level acquisition
mechanics. It cannot establish BrainVision readability, EEG signal quality,
trial or target validity, neural advantage, decoding accuracy, generalization,
real-time latency, portable hardware, at-home use, or clinical utility.
