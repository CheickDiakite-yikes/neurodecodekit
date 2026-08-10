# PhysioNet Motor Positive-Control Acquisition Authorization Decision

Date: 2026-08-09

Status: **Authorized only after this record is tested, committed, pushed, and
remotely green; no implementation, source metadata recheck, download, local
PhysioNet access, or EDF payload access exists yet**

Machine decision:
`registries/physionet_motor_acquisition_authorization_decision.v0.json`

Frozen request:
`registries/physionet_motor_acquisition_authorization_request.v0.json`

Frozen contract: `registries/physionet_motor_acquisition_contract.v0.json`

## Exact User Decision

The maintainer supplied the registered sentence verbatim:

> Authorize the work order 8 PhysioNet motor positive-control acquisition implementation and one registered acquisition exactly as scoped in docs/PHYSIONET_MOTOR_ACQUISITION_PREREGISTRATION.md and registries/physionet_motor_acquisition_contract.v0.json. I bind registration commit 2a7b4188553e221133d788a081b838dbbb9f41bb and green CI run 31301730612. I authorize, only after a separate authorization-only decision is committed, pushed, and remotely green, a dependency-light acquisition implementation qualified only with generated local fixtures and mocked network responses; and only after that exact implementation is committed, pushed, and remotely green, metadata-only reverification of the three registered official source surfaces and one no-retry acquisition invocation for only the nine named PhysioNet EEGMMIDB v1.0.0 EDF files totaling exactly 23,248,224 bytes; one opaque local size and SHA-256 pass per EDF; creation of one new isolated complete bundle; cleanup only of temporary files created by that invocation; and one machine manifest and one human receipt under 1 MiB combined using one CPU thread, one worker, one numerical job, 300 seconds, 256 MiB peak RSS, 1 MiB metadata network, 32 MiB EDF payload network, 64 MiB incremental disk, and at least 2 GiB free disk. I do not authorize opening, decoding, or parsing any EDF header, annotation, event channel, or signal; downloading or reading any .event sidecar; reading task, target, label, event, epoch, trial, channel, montage, reference, geometry, sampling, or signal-quality values from a payload; creating epochs, windows, features, caches, splits, or derivative arrays; importing MNE or another EDF reader in the acquisition executor; model or checkpoint access; inference; training; scoring; S20, SpanishBCBL, S7, S21, S24, S25, or another real dataset; additional files, participants, runs, companions, substitutions, retries, or reruns; language models or providers; RW3; streams; devices; hardware; upload; publication; release; work order 9; or any scientific, decoding, neural, real-time, portable, home-use, assistive, or clinical claim upgrade.

This is one exact Tier C decision for the already frozen acquisition-only
protocol. It does not authorize EDF interpretation, an `.event` sidecar,
another person, another run, another file, a retry, or the positive-control
experiment itself.

## Bound Evidence

```text
authorization parent: f6eb577fdd8c168a4af229248dc56960e3ba75d8
registration commit:  2a7b4188553e221133d788a081b838dbbb9f41bb
contract SHA-256:     6c81dac6a818f13c49f5df25c540e9d3ef65f21b56ecb1a5b5d15d4a3dc819d3
request SHA-256:      77d2d1e7bd3560f2b60feb977c2826190b4ee7fd12144c7698beafb441626a76
parent push CI:       31302161647
Base Python job:      93216583586
Optional Neuro job:  93216583625
```

The preregistration, contract, packet, request, and invariant tests remain
immutable snapshots. Their pending or false authorization fields stay
unchanged because this separate record captures the later decision.

## Exact Authorized Inventory

```text
provider / dataset / version:  PhysioNet / eegmmidb / 1.0.0
DOI / license:                 10.13026/C28G6P / ODC-By-1.0
subjects / runs:               S001-S003 / 03, 07, 11
named files:                   9 EDF files
expected final bytes:          23,248,224
acquisition invocations:       1
payload retries:               0
payload verification:          one opaque size and SHA-256 pass per EDF
final bundle root:             data/physionet_motor/eegmmidb-1.0.0
manifest / receipt:            one each, combined under 1 MiB
EDF parse operations:          0
event-sidecar operations:      0
cache / split operations:      0 / 0
model / training / scoring:    0 / 0 / 0
additional files / reruns:     0 / 0
```

## Required Order

1. Test this decision against the immutable request and contract.
2. Commit, push, and obtain green Base Python and Optional Neuro Readers CI for
   this authorization record.
3. Implement the dependency-light acquisition tool using generated local
   fixture bytes and mocked network responses only, with no source request or
   local PhysioNet path operation.
4. Commit, push, and obtain green Base Python and Optional Neuro Readers CI for
   the exact implementation.
5. Verify one-thread settings, at least 2 GiB free disk, and collision-free,
   non-symlinked registered roots.
6. Reverify only the three registered official source surfaces and abort before
   EDF transfer on any mismatch.
7. Run one no-retry acquisition of the nine exact EDFs, hash each opaque local
   file once, promote only a complete verified bundle, and emit bounded
   receipts.
8. Mark the protocol consumed or parked and stop before EDF parsing or work
   order 9.

No implementation may begin before this decision commit is remotely green. No
source metadata request, local PhysioNet path stat, EDF transfer, local hash
pass, or receipt may occur before the implementation commit is remotely green.

## Computer And Storage Boundary

```text
CPU threads / workers / jobs:  1 / 1 / 1
wall time:                     <= 300 seconds
peak RSS:                      <= 256 MiB
metadata network:              <= 1 MiB
EDF payload network:           <= 32 MiB
incremental disk peak:         <= 64 MiB
minimum free disk:             >= 2 GiB
generated manifest/receipt:    <= 1 MiB combined
final payload:                 exactly 23,248,224 bytes
```

## Authorization-Only Measurements

```text
source metadata calls / EDF downloads:              0 / 0
local PhysioNet stat / open / hash passes:           0 / 0 / 0
header / annotation / signal / target reads:         0 / 0 / 0 / 0
cache / split / model / training / scoring runs:     0 / 0 / 0 / 0 / 0
provider / stream / device / hardware operations:    0 / 0 / 0 / 0
generated experiment artifacts:                     0
end-to-end latency measured:                         false
```

One GitHub Actions API read verified the parent CI. It was not a source-dataset
metadata request and transferred no EEG payload.

## Claim Boundary

**Engineering capability authorized for testing:** one hash-bound,
resource-bounded implementation and one registered acquisition of the exact
nine-file public EEGMMIDB bundle may proceed through the ordered green gates.

**Scientific claim not established:** this decision is not an acquisition or
EEG result. Even a clean acquisition can establish only byte-level acquisition
mechanics. It cannot establish EDF readability, event correctness, signal
quality, a motor effect, neural advantage, model accuracy, generalization,
real-time latency, portable hardware, home use, assistive value, or clinical
utility.
